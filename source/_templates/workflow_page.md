
# {{ wf["full_name"] }}

::::{grid} 4
{% for badge in ["license", "issues", "stars", "watchers"] %}
:::{grid-item}
:columns: auto
:margin: 0
:padding: 1
![](https://img.shields.io/github/{{ badge }}/{{ wf["full_name"] }}?style=flat&label={{ badge }})
:::
{% endfor %}
:::{grid-item}
:columns: auto
:margin: 0
:padding: 1
[![](https://img.shields.io/badge/GitHub%20page-blue?style=flat)](https://github.com/{{ wf["full_name"] }})
:::
::::

{{ wf["description"] }}

## Overview


**Latest release:** {bdg-primary}`{{ wf["release"] }}`, **Last update:** {bdg-primary}`{{ wf["last_update"] }}`


**Linting:**
{% if wf["linting"] == None -%}
    {bdg-success}`linting: passed`
{%- else -%}
    {bdg-ref-danger}`linting: failed <linting-{{ wf["full_name"]|slugify }}>`
{%- endif -%},
**Formatting:**
{% if wf["formatting"] == None -%}
    {bdg-success}`formatting: passed`
{%- else -%}
    {bdg-ref-danger}`formatting: failed <formatting-{{ wf["full_name"]|slugify }}>`
{%- endif %}


{% if wf["topics"] -%}
    **Topics:**
    {% for t in wf["topics"] %}
        {bdg-secondary}`{{ t }}`
    {% endfor %}
{%- endif %}


{% if wf["wrappers"] -%}
    **Wrappers:**
    {% for w in wf["wrappers"] %}
        {bdg-link-secondary}`{{ wf["wrappers"][w]["wrapper_name"] }} <{{ wf["wrappers"][w]["wrapper_url"] }}>`
    {% endfor %}
{%- endif %}


## Deployment

### Step 1: Install Snakemake and Snakedeploy

Snakemake and Snakedeploy are best installed via the [Conda](https://conda.io). It is recommended to install conda via [Miniforge](https://github.com/conda-forge/miniforge). Run

```bash
conda create -c conda-forge -c bioconda -c nodefaults --name snakemake snakemake snakedeploy
```

to install both Snakemake and Snakedeploy in an isolated environment. For all following commands ensure that this environment is activated _via_

```bash
conda activate snakemake
```

For other installation methods, refer to the [Snakemake](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html) and [Snakedeploy](https://snakedeploy.readthedocs.io/en/stable/getting_started/installation.html) documentation.

### Step 2: Deploy workflow

With Snakemake and Snakedeploy installed, the workflow can be deployed as follows.
First, create an appropriate project working directory on your system and enter it:

```bash
mkdir -p path/to/project-workdir
cd path/to/project-workdir
```

In all following steps, we will assume that you are inside of that directory. Then run

```bash
snakedeploy deploy-workflow https://github.com/{{ wf["full_name"] }} . --tag {{ wf["release"] }}
```

Snakedeploy will create two folders, `workflow` and `config`. The former contains the deployment of the chosen workflow as a [Snakemake module](https://snakemake.readthedocs.io/en/stable/snakefiles/deployment.html#using-and-combining-pre-exising-workflows), the latter contains configuration files which will be modified in the next step in order to configure the workflow to your needs.

### Step 3: Configure workflow

To configure the workflow, adapt `config/config.yml` to your needs following the [instructions below](#configuration).

### Step 4: Run workflow

The deployment method is controlled using the `--software-deployment-method` (short `--sdm`) argument.

{% for depl in wf.deployment %}
{%- if depl == 'conda' %}

To run the workflow with automatic deployment of all required software via `conda`/`mamba`, use

```bash
snakemake --cores all --sdm conda
```

{%- endif -%}
{%- if depl == 'apptainer' %}

To run the workflow using `apptainer`/`singularity`, use

```bash
snakemake --cores all --sdm apptainer
```

{%- endif -%}
{%- if depl == 'apptainer+conda' %}

To run the workflow using a combination of `conda` and `apptainer`/`singularity` for software deployment, use

```bash
snakemake --cores all --sdm conda apptainer
```

{%- endif -%}
{% endfor %}

Snakemake will automatically detect the main `Snakefile` in the `workflow` subfolder and execute the workflow module that has been defined by the deployment in [step 2](#step-2-deploy-workflow).

For further options such as cluster and cloud execution, see [the docs](https://snakemake.readthedocs.io/).

### Step 5: Generate report

After finalizing your data analysis, you can automatically generate an interactive visual HTML report for inspection of results together with parameters and code inside of the browser using

```bash
snakemake --report report.zip
```

## Configuration

_The following section is imported from the workflow's `config/README.md`_.

{{ wf["config_from_readme"] }}

## Linting and formatting

(linting-{{ wf["full_name"]|slugify }})=
### Linting results

{% if wf["linting"] == None %}
```
All tests passed!
```
{%- else -%}

<div style="height: 400px; overflow-y: scroll; padding: 0px;">

```{code-block}
:linenos:

{{ wf["linting"] }}
```
</div >

{% endif %}

(formatting-{{ wf["full_name"]|slugify }})=
### Formatting results

{% if wf["formatting"] == None %}
```
All tests passed!
```
{%- else -%}

<div style="height: 400px; overflow-y: scroll; padding: 0px;">

```{code-block}
:linenos:

{{ wf["formatting"] }}
```
</div >

{% endif %}
