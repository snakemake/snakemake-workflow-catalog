import logging
import tempfile
import subprocess as sp
import os
from pathlib import Path
import time
from typing import Dict
import re
from datetime import timedelta, datetime
import git
from git import Repo as GitRepo
import yaml
from github.PaginatedList import PaginatedList

from common import (
    register_skip,
    store_data,
    call_rate_limit_aware,
    get_wrappers,
    get_tarfile,
    g,
    previous_repos,
    previous_skips,
    blacklist,
    snakefmt_version,
    offset,
)

logging.basicConfig(level=logging.INFO)

test_repo = os.environ.get("TEST_REPO")
offset = int(offset * 10)
n_repos = int(os.environ.get("N_REPOS", 100))
assert n_repos >= 1

repos = {}
skips = {}


class Repo:
    data_format = 2

    def __init__(
        self,
        github_repo,
        linting,
        formatting,
        config_readme,
        settings: Dict | None,
        release,
        updated_at,
        topics,
        wrappers,
    ):
        self.full_name: str
        for attr in [
            "full_name",
            "description",
            "stargazers_count",
            "subscribers_count",
        ]:
            setattr(self, attr, getattr(github_repo, attr))

        self.topics = topics
        self.wrappers = wrappers
        self.updated_at = updated_at.timestamp()

        self.linting = linting

        self.formatting = formatting
        if formatting is not None:
            self.formatting += f"\nsnakefmt version: {snakefmt_version}"

        if release is not None:
            self.latest_release = release.tag_name
        else:
            self.latest_release = None

        if settings is not None and config_readme is not None:
            self.mandatory_flags = settings.get("usage", {}).get(
                "mandatory-flags", None
            )
            self.report = settings.get("usage", {}).get("report", False)
            self.software_stack_deployment = settings.get("usage", {}).get(
                "software-stack-deployment", {}
            )
            self.config_readme = config_readme
            self.standardized = True
            self.non_standardized_reason = None
        else:
            self.mandatory_flags = []
            self.software_stack_deployment = None
            self.config_readme = None
            self.report = False
            self.standardized = False
            self.non_standardized_reason = []
            if settings is None:
                self.non_standardized_reason.append(
                    "no .snakemake-workflow-catalog.yml found in repo root"
                )
            if config_readme is None:
                self.non_standardized_reason.append(
                    "no config/README.md found in repo root"
                )

        # increase this if fields above change
        self.data_format = Repo.data_format


if test_repo is not None:
    repo_search = [g.get_repo(test_repo)]
    total_count = 1
    offset = 0
else:
    assert "LATEST_COMMIT" in os.environ
    latest_commit = int(os.environ["LATEST_COMMIT"])

    date_threshold = datetime.today() - timedelta(latest_commit)
    date_threshold = datetime.strftime(date_threshold, "%Y-%m-%d")
    repo_search: PaginatedList = g.search_repositories(
        f"snakemake workflow in:readme archived:false pushed:>={date_threshold}",
        sort="updated",
    )
    time.sleep(5)
    total_count = call_rate_limit_aware(
        lambda: repo_search.totalCount, api_type="search"
    )

end = min(offset + n_repos, total_count)
logging.info(f"Checking {total_count} repos, repo {offset}-{end-1}.")

for i in range(offset, end):
    if i != offset:
        # sleep for one minute +x to avoid running into secondary rate limit
        time.sleep(63)

    # We access each repo by index instead of using an iterator
    # in order to be able to retry the access in case we reach the search
    # rate limit.
    repo = call_rate_limit_aware(lambda: repo_search[i], api_type="search")

    if i % 10 == 0:
        logging.info(f"{i} of {total_count} repos done.")

    log_skip = lambda reason: logging.info(
        f"Skipped {repo.full_name} because {reason}."
    )

    logging.info(f"Processing {repo.full_name}.")
    if repo.full_name in blacklist:
        log_skip("it is blacklisted")
        continue

    updated_at = repo.updated_at
    releases = call_rate_limit_aware(repo.get_releases)
    try:
        release = releases[0]
        updated_at = max(updated_at, release.created_at)
    except IndexError:
        # no releases
        release = None

    prev = previous_repos.get(repo.full_name)
    if (
        prev is not None
        and Repo.data_format == prev["data_format"]
        and prev["updated_at"] == updated_at.timestamp()
    ):
        # keep old data, it hasn't changed
        logging.info("Repo hasn't changed, keeping old data.")
        repos[prev["full_name"]] = prev
        continue

    prev_skip = previous_skips.get(repo.full_name)
    if prev_skip is not None and prev_skip["updated_at"] == updated_at.timestamp():
        # keep old data, it hasn't changed
        logging.info("Repo hasn't changed, skipping again based on old data.")
        skips[prev_skip["full_name"]] = prev_skip
        continue

    snakefile = "Snakefile"
    rules = "rules"

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        if release is not None:
            # download release tag (use hardcoded url, because repo.tarball_url can sometimes
            # cause ambiguity errors if a branch is called the same as the release).
            tarball_url = f"https://github.com/{repo.full_name}/tarball/refs/tags/{release.tag_name}"
            root_dir = get_tarfile(tarball_url).getmembers()[0].name
            get_tarfile(tarball_url).extractall(path=tmp, filter="tar")
            tmp /= root_dir
        else:
            # no latest release, clone main branch
            try:
                gitrepo = GitRepo.clone_from(repo.clone_url, str(tmp), depth=1)
            except git.GitCommandError:
                log_skip("error cloning repository")
                skips = register_skip(repo, skips)
                continue

        workflow = tmp / "workflow"
        if not workflow.exists():
            workflow = tmp

        rules = workflow / "rules"
        snakefile = workflow / "Snakefile"

        if not snakefile.exists():
            log_skip("of missing Snakefile")
            skips = register_skip(repo, skips)
            continue

        if rules.exists() and rules.is_dir():
            if not any(
                rule_file.suffix == ".smk"
                for rule_file in rules.iterdir()
                if rule_file.is_file()
            ):
                log_skip("rule modules are not using .smk extension")
                skips = register_skip(repo, skips)
                continue

        # catalog settings
        settings = None
        settings_file = tmp / ".snakemake-workflow-catalog.yml"
        if settings_file.exists():
            with open(settings_file) as settings_file:
                try:
                    settings = yaml.load(settings_file, yaml.SafeLoader)
                    if not isinstance(settings, dict):
                        logging.info(
                            "No standardized usage possible because "
                            ".snakemake-workflow-catalog.yml does not contain a YAML "
                            "mapping."
                        )
                        settings = None
                except yaml.scanner.ScannerError as e:
                    logging.info(
                        "No standardized usage possible because "
                        "there was an error parsing "
                        ".snakemake-workflow-catalog.yml:\n{}".format(e)
                    )

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
            linting = re.sub("gh[pousr]\\_[a-zA-Z0-9_]{36}@?", "", linting)
            if test_repo is not None:
                logging.error(linting)

        # formatting
        snakefiles = [workflow / "Snakefile"] + list(rules.glob("*.smk"))
        fmt_mode = "--check" if test_repo is None else "--diff"
        try:
            sp.run(
                ["snakefmt", fmt_mode, "-v"] + snakefiles,
                cwd=tmp,
                check=True,
                stderr=sp.STDOUT,
                stdout=sp.PIPE,
            )
        except sp.CalledProcessError as e:
            formatting = e.stdout.decode()
            if test_repo is not None:
                logging.error(formatting)

        # wrappers
        wrappers = {}
        for smk in snakefiles:
            try:
                with open(smk, "r") as f:
                    smkfile = f.read()
            except Exception as e:
                logging.warning(f"Could not read {smk}: {e}")
                continue
            smk_wrappers = get_wrappers(smkfile)
            if smk_wrappers:
                wrappers = wrappers | smk_wrappers

    topics = call_rate_limit_aware(repo.get_topics)

    repo_obj = Repo(
        repo,
        linting,
        formatting,
        config_readme,
        settings,
        release,
        updated_at,
        topics,
        wrappers,
    )
    logging.info(
        f"Repo {repo_obj.full_name} processed successfully as "
        f"{'standardized' if repo_obj.standardized else 'non-standardized'} workflow."
    )

    repos[repo_obj.__dict__["full_name"]] = repo_obj.__dict__

if test_repo is None:
    # Now add all old repos that haven't been covered by the current search.
    # This is necessary because Github limits search queries to 1000 items,
    # and we use up to 1000 repos with the most recent changes.
    logging.info("Adding all old repos not covered by the current query.")
    store_data(previous_repos | repos, "data.json")

    logging.info("Adding all old skipped repos not covered by the current query.")
    store_data(previous_skips | skips, "skips.json")

    logging.info(
        f"Processed {len(previous_repos)} existing and {len(repos)} new/updated repos."
    )
