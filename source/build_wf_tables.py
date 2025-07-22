import json
import re
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
from pathlib import Path


# clean repo items, can add more in future
def clean_repo(repo):
    if repo["description"] is not None:
        repo["description"] = repo["description"].replace('"', "")
        if len(repo["description"]) > 100:
            repo["description"] = repo["description"][:100] + "..."
    else:
        repo["description"] = "No description available."
    return repo


def slugify(value):
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value


# function to render markdown tables and cards
def render_markdown(
    type,
    repos,
    jinja_env,
    template,
    output,
    metric="stars",
    top_n=None,
):
    wf_standard = type == "standardized"
    if metric == "stars":
        sort_by = "stargazers_count"
        reverse = True
    elif metric == "update":
        sort_by = "updated_at"
        reverse = True
    elif metric == "watchers":
        sort_by = "subscribers_count"
        reverse = True
    elif metric == "tests":
        sort_by = "updated_at"
        reverse = True
        repos = {
            k: v
            for k, v in repos.items()
            if v["linting"] is None and v["formatting"] is None
        }
    repos = {k: v for k, v in repos.items() if v["standardized"] == wf_standard}
    repos = sorted(repos.values(), key=lambda x: x[sort_by], reverse=reverse)
    if top_n:
        repos = repos[:top_n] if len(repos) > top_n else repos
    repos = [clean_repo(repo) for repo in repos]
    repos[0]["metric"] = metric
    template = jinja_env.get_template(template)
    md_rendered = template.render(input=repos)
    output_path = Path(output)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_rendered)


def build_wf_tables():
    # items to select from json file
    selected_items = [
        "full_name",
        "standardized",
        "description",
        "topics",
        "latest_release",
        "updated_at",
        "linting",
        "formatting",
        "stargazers_count",
        "subscribers_count",
    ]

    # import workflow data
    with open("../data.json", "r") as f:
        repos = {}
        for repo in json.load(f):
            repo = {k: repo[k] for k in selected_items if k in repo}
            repo["user"] = repo["full_name"].split("/")[0]
            repo["name"] = repo["full_name"].split("/")[1]
            last_update = datetime.fromtimestamp(repo["updated_at"])
            repo["last_update"] = datetime.strftime(last_update, "%Y-%m-%d")
            repos[repo["full_name"]] = repo

    # import topics
    with open("../topics.json", "r") as f:
        topics = json.loads(f.read())

    # import jinja templates
    env = Environment(
        loader=FileSystemLoader("_templates"),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["slugify"] = slugify

    # render tables
    for wf_type in ["standardized", "other"]:
        render_markdown(
            type=wf_type,
            repos=repos,
            jinja_env=env,
            template=f"all_{wf_type}_workflows.md",
            output=f"docs/all_{wf_type}_workflows.md",
        )

    # render cards
    for metric in ["stars", "watchers", "update", "tests"]:
        render_markdown(
            type="standardized",
            repos=repos,
            jinja_env=env,
            template="workflows_by.md",
            output=f"docs/workflows_by_{metric}.md",
            metric=metric,
            top_n=15,
        )

    # match repos to topics
    for topic in topics:
        standardized_repos = {k: v for k, v in repos.items() if v["standardized"]}
        matching_repos = {}
        for repo_name, repo_data in standardized_repos.items():
            if any(tag in topics[topic] for tag in repo_data["topics"]):
                matching_repos[repo_name] = repo_data
        topics[topic] = {
            "name": topic,
            "number": len(matching_repos),
            "repos": list(matching_repos.keys()),
            "keywords": topics[topic],
        }

    # render topics landing page
    template = env.get_template("workflows_by_topic.md")
    output = "docs/workflows_by_topic.md"
    topics_list = sorted(topics.values(), key=lambda x: x["number"], reverse=True)
    md_rendered = template.render(input=list(topics_list))
    output_path = Path(output)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_rendered)

    # closing statement
    print("Tables and cards rendered successfully.")
    return None
