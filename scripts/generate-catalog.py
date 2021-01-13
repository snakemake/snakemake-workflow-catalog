import logging
import tempfile
import subprocess as sp
import os
from itertools import chain
import glob
from pathlib import Path

from jinja2 import Environment
from github import Github
from github.GithubException import UnknownObjectException
import git
from jinja2 import Environment, FileSystemLoader, select_autoescape

logging.basicConfig(level=logging.INFO)

env = Environment(autoescape=select_autoescape(['html']),
                  loader=FileSystemLoader('templates'))

class Repo:
    def __init__(self, github_repo):
        self.github = github_repo
        self.linting = None
        self.formatting = None

    def __getattr__(self, attr):
        return getattr(self.github, attr)

g = Github(os.environ["GITHUB_TOKEN"])

repos = []

for repo in g.search_repositories("snakemake workflow in:readme archived:false"):
    log_skip = lambda reason: logging.info(f"skipped {repo.full_name} because of {reason}")

    logging.info(f"Processing {repo.name}")

    workflow_base = "workflow/"
    get_path = lambda path: "{}{}".format(workflow_base, path)

    try:
        repo.get_contents("workflow")
    except UnknownObjectException:
        workflow_base = ""
    
    try:
        repo.get_contents(get_path("Snakefile"))
    except UnknownObjectException:
        log_skip("missing Snakefile")
        continue

    try:
        rule_modules = repo.get_contents(get_path("rules"))
    except UnknownObjectException:
        rule_modules = []
    if not all(module.name.endswith(".smk") for module in rule_modules):
        log_skip("rule modules not using .smk extension")
        continue
    
    repo = Repo(repo)

    with tempfile.TemporaryDirectory() as tmp:
        git.Git().clone(repo.clone_url, tmp, depth=1, filter="blob:limit=1m")

        # linting
        try:
            out = sp.run(["snakemake", "--lint"], capture_output=True, cwd=tmp, check=True)
        except sp.CalledProcessError as e:
            repo.linting = e.stderr.decode()
        
        # formatting
        glob_path = lambda path: glob.glob(str(Path(tmp) / path))
        snakefiles = list(chain(glob_path("Snakefile"), glob_path("workflow/Snakefile"), glob_path("rules/*.smk"), glob_path("workflow/rules/*.smk")))
        try:
            out = sp.run(["snakefmt", "--check"] + snakefiles, capture_output=True, cwd=tmp, check=True)
        except sp.CalledProcessError as e:
            repo.formatting = e.stderr.decode()
    
    repos.append(repo)

repos.sort(key=lambda repo: repo.stargazers_count)

with open("index.html", "w") as out:
    print(env.get_template("index.html").render(repos=repos), file=out)