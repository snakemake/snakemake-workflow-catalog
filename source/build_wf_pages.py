import json
import re
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
from pathlib import Path
from modify_svg import modify_svg
import subprocess as sp


def check_readme(readme):
    clean_readme = []
    readme_split = readme.split("\n")
    code_block = False
    for i, j in zip(readme_split, range(0, len(readme_split))):
        if i.startswith("```"):
            code_block = not code_block
        if i.startswith("# ") and not code_block:
            clean_readme += [i.replace("# ", "## ")]
        else:
            clean_readme += [i]
    return "\n".join(clean_readme)


def check_deployment(depl):
    result = {}
    for i in depl.keys():
        if depl[i]:
            result[i.replace("singularity", "apptainer")] = True
    return result


def check_qc_output(qc_item, max_lines=200):
    if qc_item is None:
        return None
    else:
        result = qc_item.split("\n")
        if len(result) > max_lines:
            return "\n".join(result[:max_lines]) + "\n\n... (truncated)"
        else:
            return "\n".join(result)


def slugify(value):
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value


def plot_rulegraph(output: Path, rg_dot: str) -> list[str]:
    dotfile = output.with_suffix(".dot")
    with open(dotfile, "w", encoding="utf-8") as f:
        f.write(rg_dot)
    styles = {
        "light": ["label_arrow_stroke=lightgrey"],
        "dark": ["node_stroke=black", "label_arrow_stroke=darkgrey"],
    }
    snakevision_cmd = [
        "snakevision",
        "-s",
        "all",
        "multiqc",
        "-y",
    ]
    output_files = []
    for style in styles:
        svgfile = output.with_name(f"{output.name}_{style}.svg")
        try:
            sp.run(
                snakevision_cmd + styles[style] + ["-o", str(svgfile)] + [str(dotfile)],
                check=True,
            )
        except sp.CalledProcessError:
            return []
        modify_svg(svgfile, style)
        output_files.append(svgfile.name)
    return output_files


def format_default(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def schema_to_markdown(data):
    rows = []
    data = json.loads(data)

    def parse_props(props, parent="", required_list=None, nesting=0):
        required_list = required_list or []

        for name, details in props.items():
            if not isinstance(details, dict):
                continue

            spacer = " . " * nesting
            full_name = f"{spacer}{name}" if parent else f"**{name}**"
            param_type = details.get("type", "")
            description = details.get("description", "")
            required = "yes" if name in required_list else ""
            default = format_default(details.get("default"))

            rows.append([full_name, param_type, description, required, default])

            if "properties" in details:
                child_props = details.get("properties", {})
                child_required = details.get("required", [])
                parse_props(child_props, full_name, child_required, nesting + 1)

    parse_props(
        data.get("properties", {}), parent="", required_list=data.get("required", [])
    )

    headers = ["Parameter", "Type", "Description", "Required", "Default"]
    rows = [[str(cell) for cell in row] for row in rows]
    col_widths = [
        max(len(headers[i]), *(len(row[i]) for row in rows))
        for i in range(len(headers))
    ]

    md_lines = []
    md_lines.append(
        "| "
        + " | ".join(headers[i].ljust(col_widths[i]) for i in range(len(headers)))
        + " |"
    )
    md_lines.append(
        "| " + " | ".join("-" * col_widths[i] for i in range(len(headers))) + " |"
    )
    for row in rows:
        md_lines.append(
            "| "
            + " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers)))
            + " |"
        )
    markdown = "\n".join(md_lines)
    return markdown


def build_wf_pages():
    # import jinja templates
    env = Environment(
        loader=FileSystemLoader("_templates"),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["slugify"] = slugify
    template = env.get_template("workflow_page.md")

    # import workflow data
    with open("../data.json", "r") as f:
        repos = {}
        for repo in json.load(f):
            if repo["standardized"]:
                repos[repo["full_name"]] = repo

    # render markdown template with jinja2 for each repo
    for current_repo in repos:
        repo = repos[current_repo]
        wf_data = {}
        wf_data["full_name"] = current_repo
        wf_dir, wf_name = current_repo.split("/")
        output_dir = Path("docs/workflows") / wf_dir
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        # plot rulegraph as SVG if available
        rg_dot = repo.get("rulegraph", None)
        if rg_dot is not None:
            plots = plot_rulegraph(output_dir / wf_name, rg_dot)
        else:
            plots = None
        # prepare title, description, reporting, qc stats, etc.
        wf_data["description"] = repo["description"]
        wf_data["topics"] = repo["topics"]
        wf_data["wrappers"] = repo.get("wrappers", {})
        wf_data["linting"] = check_qc_output(repo["linting"])
        wf_data["formatting"] = check_qc_output(repo["formatting"])
        wf_data["release"] = repo["latest_release"]
        wf_data["rulegraph"] = plots
        last_update = datetime.fromtimestamp(repo["updated_at"])
        wf_data["last_update"] = datetime.strftime(last_update, "%Y-%m-%d")
        # add deployment options
        wf_data["deployment"] = check_deployment(repo["software_stack_deployment"])
        # add configuration from readme; adjust header level if necessary
        wf_data["config_from_readme"] = check_readme(repo["config_readme"])
        wf_data["config_from_schema"] = ""
        if repo.get("schemas"):
            wf_data["config_from_schema"] = schema_to_markdown(repo.get("schemas"))
        # render and export
        md_rendered = template.render(wf=wf_data)
        output_path = output_dir / f"{current_repo.split('/')[1]}.md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_rendered)

    # closing statement
    print("Workflow pages rendered successfully.")
    return None
