import logging
import tempfile
import subprocess as sp
import os
from pathlib import Path
import json
import calendar
import time
import urllib
import tarfile

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

        try:
            self.latest_release = github_repo.get_latest_release().tag_name
        except UnknownObjectException:
            # no release
            self.latest_release = None

        if settings is not None and config_readme is not None:
            self.mandatory_flags = settings.get("usage", {}).get(
                "mandatory-flags", None
            )
            self.report = settings.get("usage", {}).get("report", False)
            self.software_stack_deployment = settings.get("usage", {}).get(
                "software-stack-deployment", {}
            )
            self.config_readme = g.render_markdown(config_readme)
            self.standardized = True
        else:
            self.mandatory_flags = []
            self.software_stack_deployment = None
            self.config_readme = None
            self.report = False
            self.standardized = False

        # increase this if fields above change
        self.data_format = Repo.data_format


def rate_limit_wait():
    curr_timestamp = calendar.timegm(time.gmtime())
    reset_timestamp = calendar.timegm(core_rate_limit.reset.timetuple())
    # add 5 seconds to be sure the rate limit has been reset
    sleep_time = max(0, reset_timestamp - curr_timestamp) + 5
    logging.warning(f"Rate limit exceeded, waiting {sleep_time}")
    time.sleep(sleep_time)


def call_rate_limit_aware(func):
    while True:
        try:
            return func()
        except RateLimitExceededException:
            rate_limit_wait()


def store_data():
    repos.sort(key=lambda repo: repo["stargazers_count"])

    with open("data.js", "w") as out:
        print(env.get_template("data.js").render(data=repos), file=out)
    with open("skips.json", "w") as out:
        json.dump(skips, out, sort_keys=True, indent=2)


repo_search = g.search_repositories("snakemake workflow in:readme archived:false",
        sort="updated")

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

    updated_at = repo.updated_at
    try:
        release = call_rate_limit_aware(repo.get_latest_release)
        updated_at = max(updated_at, release.created_at)
    except UnknownObjectException:
        release = None

    prev = previous_repos.get(repo.full_name)
    if (
        prev is not None
        and Repo.data_format == prev["data_format"]
        and prev["updated_at"] == updated_at.timestamp()
    ):
        # keep old data, it hasn't changed
        logging.info("Remaining repos haven't changed, using old data.")
        older_repos = [repo for repo in previous_repos.values() if repo["updated_at"] =< updated_at.timestamp()]
        repos += older_repos
        break
    prev_skip = previous_skips.get(repo.full_name)
    if prev_skip is not None and prev_skip["updated_at"] == updated_at.timestamp():
        # keep old data, it hasn't changed
        logging.info("Repo hasn't changed, skipping again based on old data.")
        skips.append(prev_skip)
        continue

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        if release is not None:
            # download release tag
            get_tarfile = lambda: tarfile.open(
                fileobj=urllib.request.urlopen(release.tarball_url), mode="r|gz"
            )
            root_dir = get_tarfile().getmembers()[0].name
            get_tarfile().extractall(path=tmp)
            tmp /= root_dir
        else:
            # no latest release, clone main branch
            try:
                gitrepo = git.Repo.clone_from(repo.clone_url, str(tmp), depth=1)
            except git.GitCommandError:
                log_skip("error cloning repository")
                register_skip(repo)
                continue

        workflow = tmp / "workflow"
        if not workflow.exists():
            workflow = tmp

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
        if settings_file.exists():
            with open(settings_file) as settings_file:
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

    call_rate_limit_aware(
        lambda: repos.append(
            Repo(repo, linting, formatting, config_readme, settings).__dict__
        )
    )

    if len(repos) % 20 == 0:
        logging.info("Storing intermediate results.")
        store_data()

    # if len(repos) >= 2:
    #     break

store_data()
