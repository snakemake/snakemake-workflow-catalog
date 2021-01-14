import logging
import tempfile
import subprocess as sp
import os
from pathlib import Path
import json

from jinja2 import Environment
from github import Github
from github.GithubException import UnknownObjectException
import git
from jinja2 import Environment, FileSystemLoader, select_autoescape

logging.basicConfig(level=logging.INFO)

env = Environment(
    autoescape=select_autoescape(["html"]), loader=FileSystemLoader("templates")
)


class Repo:
    data_format = 1
    def __init__(self, github_repo, linting, formatting):
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
        # increase this if fields above change
        self.data_format = Repo.data_format


g = Github(os.environ["GITHUB_TOKEN"])

with open("data.js", "r") as f:
    next(f)
    previous_repos = {repo["full_name"]: repo for repo in json.loads(next(f))}

blacklist = set(l.strip() for l in open("blacklist.txt", "r"))

repos = []

for repo in g.search_repositories("snakemake workflow in:readme archived:false"):
    log_skip = lambda reason: logging.info(
        f"Skipped {repo.full_name} because {reason}."
    )

    logging.info(f"Processing {repo.full_name}.")
    if repo.full_name in blacklist:
        log_skip("it is blacklisted")
        continue

    prev = previous_repos.get(repo.full_name)
    if prev is not None and Repo.data_format == prev["data_format"] and prev["updated_at"] == repo.updated_at.timestamp():
        # keep old data, it hasn't changed
        logging.info("Repo hasn't changed, using old data.")
        repos.append(prev)
        continue

    with tempfile.TemporaryDirectory() as tmp:
        git.Git().clone(repo.clone_url, tmp, depth=1, filter="blob:limit=1m")
        glob_path = lambda path: glob.glob(str(Path(tmp) / path))
        get_path = lambda path: "{}{}".format(workflow_base, path)

        workflow = Path(tmp) / "workflow"
        if not workflow.exists():
            workflow = Path(tmp)

        if not (workflow / "Snakefile").exists():
            log_skip("of missing Snakefile")
            continue

        rules = workflow / "rules"

        rule_modules = (
            [] if not rules.exists() else [rules / f for f in rules.glob("*.smk")]
        )
        if rule_modules and not any(f.suffix == ".smk" for f in rule_modules):
            log_skip("rule modules are not using .smk extension")
            continue

        linting = None
        formatting = None

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

    repos.append(Repo(repo, linting, formatting).__dict__)

    # if len(repos) >= 2:
    #     break

repos.sort(key=lambda repo: repo["stargazers_count"])

with open("data.js", "w") as out:
    print(env.get_template("data.js").render(data=repos), file=out)
