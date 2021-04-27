import logging
import tempfile
import subprocess as sp
import os
from pathlib import Path
import json
import calendar
import time

from jinja2 import Environment
from github import Github
from github.GithubException import UnknownObjectException, RateLimitExceededException
import git
from jinja2 import Environment, FileSystemLoader, select_autoescape
import yaml

logging.basicConfig(level=logging.INFO)

env = Environment(
    autoescape=select_autoescape(["html"]), loader=FileSystemLoader("templates")
)

# do not clone LFS files
os.environ["GIT_LFS_SKIP_SMUDGE"] = "1"
g = Github(os.environ["GITHUB_TOKEN"])
core_rate_limit = g.get_rate_limit().core

with open("data.js", "r") as f:
    next(f)
    previous_repos = {repo["full_name"]: repo for repo in json.loads(f.read())}

with open("skips.json", "r") as f:
    previous_skips = {repo["full_name"]: repo for repo in json.load(f)}

blacklist = set(l.strip() for l in open("blacklist.txt", "r"))

repos = []
skips = []


def register_skip(repo):
    skips.append(
        {"full_name": repo.full_name, "updated_at": repo.updated_at.timestamp()}
    )


class Repo:
    data_format = 2

    def __init__(self, github_repo, linting, formatting, config_readme, settings: dict):
        for attr in [
            "full_name",
            "description",
            "stargazers_count",
            "subscribers_count",
        ]:
            setattr(self, attr, getattr(github_repo, attr))

        self.topics = github_repo.get_topics()
        self.updated_at = github_repo.updated_at.timestamp()

        self.linting = linting
        self.formatting = formatting
        
        self.latest_release = github_repo.get_latest_release()
        if self.latest_release:
            self.latest_release = self.latest_release.tag_name

        if settings is not None and config_readme is not None:
            self.mandatory_flags = settings.get("usage", {}).get("mandatory-flags", None)
            self.report = settings.get("report", False)
            self.software_stack_deployment = settings.get("software-stack-deployment", {})
            self.standardized = True
            self.config_readme = g.render_markdown(config_readme)
        else:
            self.snakemake_flags = []
            self.standardized = False

        # increase this if fields above change
        self.data_format = Repo.data_format


def rate_limit_wait():
    reset_timestamp = calendar.timegm(core_rate_limit.reset.timetuple())
    # add 5 seconds to be sure the rate limit has been reset
    sleep_time = reset_timestamp - calendar.timegm(time.gmtime()) + 5
    logging.warning(f"Rate limit exceeded, waiting {sleep_time}")
    time.sleep(sleep_time)


def store_data():
    repos.sort(key=lambda repo: repo["stargazers_count"])

    with open("data.js", "w") as out:
        print(env.get_template("data.js").render(data=repos), file=out)
    with open("skips.json", "w") as out:
        json.dump(skips, out, sort_keys=True, indent=2)


repo_search = g.search_repositories("snakemake workflow in:readme archived:false")

for i, repo in enumerate(repo_search):
    if i % 10 == 0:
        logging.info(f"{i} of {repo_search.totalCount} repos done")

    log_skip = lambda reason: logging.info(
        f"Skipped {repo.full_name} because {reason}."
    )

    logging.info(f"Processing {repo.full_name}.")
    if repo.full_name in blacklist:
        log_skip("it is blacklisted")
        continue

    prev = previous_repos.get(repo.full_name)
    if (
        prev is not None
        and Repo.data_format == prev["data_format"]
        and prev["updated_at"] == repo.updated_at.timestamp()
    ):
        # keep old data, it hasn't changed
        logging.info("Repo hasn't changed, using old data.")
        repos.append(prev)
        continue
    prev = previous_skips.get(repo.full_name)
    if (prev is not None and Repo.data_format == prev["data_format"] and prev["updated_at"] == repo.updated_at.timestamp()):
        # keep old data, it hasn't changed
        logging.info("Repo hasn't changed, skipping again based on old data.")
        skips.append(prev)
        continue

    with tempfile.TemporaryDirectory() as tmp:
        try:
            gitrepo = git.Repo.clone_from(repo.clone_url, tmp, depth=1)
        except git.GitCommandError:
            log_skip("error cloning repository")
            register_skip(repo)
            continue

        glob_path = lambda path: glob.glob(str(Path(tmp) / path))
        get_path = lambda path: "{}{}".format(workflow_base, path)

        release = repo.get_latest_release()
        if release is not None:
            # go to release commit
            gitrepo.head.reference = gitrepo.commit(release.target_commitish)
            gitrepo.head.reset(index=True, working_tree=True)

        workflow = Path(tmp) / "workflow"
        if not workflow.exists():
            workflow = Path(tmp)

        if not (workflow / "Snakefile").exists():
            log_skip("of missing Snakefile")
            register_skip(repo)
            continue

        rules = workflow / "rules"

        rule_modules = (
            [] if not rules.exists() else [rules / f for f in rules.glob("*.smk")]
        )
        if rule_modules and not any(f.suffix == ".smk" for f in rule_modules):
            log_skip("rule modules are not using .smk extension")
            register_skip(repo)
            continue

        # catalog settings
        settings = None
        settings_file = tmp / ".snakemake-workflow-catalog.yml"
        if settings.exists():
            with open(settings) as settings_file:
                settings = yaml.load(settings_file, yaml.Loader)

        linting = None
        formatting = None

        # config readme
        config_readme = None
        config_readme_path = tmp / "config" / "README.md"
        if config_readme_path.exists():
            with open(config_readme_path, "r") as f:
                config_readme = f.read()

        # linting
        try:
            out = sp.run(
                ["snakemake", "--lint"], capture_output=True, cwd=tmp, check=True
            )
        except sp.CalledProcessError as e:
            linting = e.stderr.decode()

        # formatting
        snakefiles = [workflow / "Snakefile"] + list(rules.glob("*.smk"))
        try:
            out = sp.run(
                ["snakefmt", "--check"] + snakefiles,
                capture_output=True,
                cwd=tmp,
                check=True,
            )
        except sp.CalledProcessError as e:
            formatting = e.stderr.decode()

    while True:
        try:
            parsed = Repo(repo, linting, formatting, config_readme, settings)
            repos.append(parsed.__dict__)
            break
        except RateLimitExceededException:
            rate_limit_wait()

    if len(repos) % 20 == 0:
        logging.info("Storing intermediate results.")
        store_data()

    # if len(repos) >= 2:
    #     break

store_data()
