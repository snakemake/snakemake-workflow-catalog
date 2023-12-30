import logging
import math
import time

from common import store_data, check_repo_exists, g, previous_repos, previous_skips, offset

def cleanup(repos):
    _offset = int(offset / 100 * len(repos))
    n = int(math.ceil(len(repos) / 10))
    logging.info(f"Checking {n} repos for existence.")
    for i, repo_name in enumerate(list(repos.keys())[_offset:min(_offset + n, len(repos))]):
        if i != 0:
            time.sleep(5)
        
        if not check_repo_exists(g, repo_name):
            logging.info(f"Repo {repo_name} has been deleted or moved")
            del repos[repo_name]
            continue
        else:
            logging.info(f"Repo {repo_name} still exists, keeping data.")

logging.info("Remove superfluous repos.")
cleanup(previous_repos)
logging.info("Remove superfluous skips.")
cleanup(previous_skips)

store_data(previous_repos, previous_skips)