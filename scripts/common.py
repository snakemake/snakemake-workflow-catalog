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

from ratelimit import limits, sleep_and_retry
from jinja2 import Environment
from github import Github
from github.ContentFile import ContentFile
from github.GithubException import UnknownObjectException, RateLimitExceededException
import git
from jinja2 import Environment, FileSystemLoader, select_autoescape
import yaml

logging.basicConfig(level=logging.INFO)

test_repo = os.environ.get("TEST_REPO")
offset = int(os.environ.get("OFFSET", 0))

env = Environment(
    autoescape=select_autoescape(["html"]), loader=FileSystemLoader("templates")
)

# do not clone LFS files
os.environ["GIT_LFS_SKIP_SMUDGE"] = "1"
g = Github(os.environ["GITHUB_TOKEN"])
get_rate_limit = lambda api_type: getattr(g.get_rate_limit(), api_type)

with open("data.js", "r") as f:
    next(f)
    previous_repos = {repo["full_name"]: repo for repo in json.loads(f.read())}

with open("skips.json", "r") as f:
    previous_skips = {repo["full_name"]: repo for repo in json.load(f)}

blacklist = set(l.strip() for l in open("blacklist.txt", "r"))

snakefmt_version = (
    sp.run(["snakefmt", "--version"], capture_output=True, check=True)
    .stdout.decode()
    .strip()
    .split()[-1]
)

def rate_limit_wait(api_type):
    curr_timestamp = calendar.timegm(time.gmtime())
    reset_timestamp = calendar.timegm(get_rate_limit(api_type).reset.timetuple())
    # add 5 seconds to be sure the rate limit has been reset
    sleep_time = max(0, reset_timestamp - curr_timestamp) + 5
    logging.warning(f"Rate limit exceeded, waiting {sleep_time} seconds")
    time.sleep(sleep_time)


@sleep_and_retry
@limits(calls=990, period=3600)
def call_rate_limit_aware(func, api_type="core"):
    while True:
        try:
            return func()
        except RateLimitExceededException:
            rate_limit_wait(api_type)


def store_data(repos, skips):
    repos.sort(key=lambda repo: repo["stargazers_count"])

    with open("data.js", "w") as out:
        print(env.get_template("data.js").render(data=repos), file=out)
    with open("skips.json", "w") as out:
        json.dump(skips, out, sort_keys=True, indent=2)


def check_repo_exists(g, full_name):
    def inner():
        try:
            repo = g.get_repo(full_name)
            # return true if repo has not been moved (i.e. full name did not change)
            # otherwise, we would have retrieved it under the other name in the search
            return repo.full_name == full_name
        except UnknownObjectException:
            logging.info(f"Repo {full_name} has been deleted")
            return False

    return call_rate_limit_aware(inner)
