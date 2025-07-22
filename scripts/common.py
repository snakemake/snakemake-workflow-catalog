import logging
import subprocess as sp
import os
import json
import calendar
import time
import re
import tarfile
import urllib.request

from ratelimit import limits, sleep_and_retry
from github import Github
from github.GithubException import UnknownObjectException, RateLimitExceededException

logging.basicConfig(level=logging.INFO)

test_repo = os.environ.get("TEST_REPO")
offset = int(os.environ.get("OFFSET", 0))

# do not clone LFS files
os.environ["GIT_LFS_SKIP_SMUDGE"] = "1"
g = Github(os.environ["GITHUB_TOKEN"])
get_rate_limit = lambda api_type: getattr(g.get_rate_limit(), api_type)

with open("data.json", "r") as f:
    previous_repos = {repo["full_name"]: repo for repo in json.load(f)}

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


def register_skip(repo, skips):
    skips[repo.full_name] = {
        "full_name": repo.full_name,
        "updated_at": repo.updated_at.timestamp(),
    }
    return skips


def store_data(input, json_output):
    input = sorted(input.values(), key=lambda repo: repo["full_name"])
    with open(json_output, "w") as out:
        json.dump(input, out, sort_keys=True, indent=2)


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


def get_wrappers(smkfile):
    wrappers = {}
    for match in re.finditer(r"\n\s*wrapper:\s*(.+)\n", smkfile):
        wrapper_line = match.group(1).strip().replace('"', "")
        wrp_clean = wrapper_line.split("/")
        if len(wrp_clean) not in [3, 4]:
            continue
        version, *rest = wrp_clean
        if not re.match(r"v\d+\.\d+\.\d+", version):
            continue
        wrapper_name = "/".join(rest)
        wrapper_url = f"https://snakemake-wrappers.readthedocs.io/en/stable/wrappers/{"/".join(rest)}.html"
        wrappers[wrapper_name] = {
            "wrapper_name": wrapper_name,
            "wrapper_version": version,
            "wrapper_url": wrapper_url,
        }
    return wrappers


def get_tarfile(url):
    return tarfile.open(fileobj=urllib.request.urlopen(url), mode="r|gz")
