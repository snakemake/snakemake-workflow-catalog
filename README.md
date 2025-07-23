# snakemake-workflow-catalog

[![Generate catalog](https://github.com/snakemake/snakemake-workflow-catalog/actions/workflows/generate.yml/badge.svg)](https://github.com/snakemake/snakemake-workflow-catalog/actions/workflows/generate.yml)
[![Deploy catalog](https://github.com/snakemake/snakemake-workflow-catalog/actions/workflows/deploy.yml/badge.svg)](https://github.com/snakemake/snakemake-workflow-catalog/actions/workflows/deploy.yml)
![GitHub last commit](https://img.shields.io/github/last-commit/snakemake/snakemake-workflow-catalog?label=latest%20update)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/snakemake/snakemake-workflow-catalog)

A statically generated catalog of available Snakemake workflows

This repository serves as a centralized collection of workflows designed to facilitate reproducible and scalable data analyses using the [**Snakemake**](https://snakemake.github.io/) workflow management system.

## Purpose

The Snakemake Workflow Catalog aims to provide a regularly updated list of high-quality workflows that can be easily reused and adapted for various data analysis tasks. By leveraging the power of [**Snakemake**](https://snakemake.github.io/), these workflows promote:

- Reproducibility: Snakemake workflows produce consistent results, making it easier to share and validate scientific findings.
- Scalability: Snakemake workflows can be executed on various computing environments, from local machines to high-performance computing clusters and cloud services.
- Modularity: Snakemake workflows are structured to allow easy customization and extension, enabling users to adapt them to their specific needs.

## Workflows

Workflows are automatically added to the Workflow Catalog. This is done by regularly searching Github repositories for matching workflow structures. The catalog includes workflows based on the following criteria.

### All workflows

- The workflow is contained in a public Github repository.
- The repository has a `README.md` file, containing the words "snakemake" and "workflow" (case insensitive).
- The repository contains a workflow definition named either `Snakefile` or `workflow/Snakefile`.
- If the repository contains a folder `rules` or `workflow/rules`, that folder must at least contain one file ending on `.smk`.
- The repository is small enough to be cloned into a [Github Actions](https://docs.github.com/en/actions/about-github-actions/understanding-github-actions) job (very large files should be handled via [Git LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files), so that they can be stripped out during cloning).
- The repository is not blacklisted here.

### Standardized usage workflows

In order to additionally appear in the "standardized usage" area, repositories additionally have to:

- have their main workflow definition named `workflow/Snakefile` (unlike for plain inclusion (see above), which also allows just `Snakefile` in the root of the repository),
- provide configuration instructions under `config/README.md`
- contain a `YAML` file `.snakemake-workflow-catalog.yml` in their root directory, which configures the usage instructions displayed by this workflow catalog.

Typical content of the `.snakemake-workflow-catalog.yml` file:

```yaml
usage:
  mandatory-flags:
    desc: # describe your flags here in a few sentences
    flags: # put your flags here
  software-stack-deployment:
    conda: true # whether pipeline works with '--sdm conda'
    apptainer: true # whether pipeline works with '--sdm apptainer/singularity'
    apptainer+conda: true # whether pipeline works with '--sdm conda apptainer/singularity'
    report: true # whether creation of reports using 'snakemake --report report.zip' is supported
```

Once included in the standardized usage area you can link directly to the workflow page using the URL `https://snakemake.github.io/snakemake-workflow-catalog/docs/workflows/<owner>/<repo>`. Do not forget to replace the `<owner>` and `<repo>` tags at the end of the URL.

### Release handling

If your workflow provides Github releases, the catalog will always just scrape the latest non-preview release. Hence, in order to update your workflow's records here, you need to release a new version on Github.

## Contributing

Contributions to the Snakemake Workflow Catalog are welcome!
Ideas can be discussed on the [catalog's Issues page](https://github.com/snakemake/snakemake-workflow-catalog/issues) first, and contributions made through Github Pull Requests, see the [next section](#working-with-a-local-copy) for details.

[Topics](https://snakemake.github.io/snakemake-workflow-catalog/docs/workflows_by_topic.html) are currently predefined in the `topics.json` file.
Users are encouraged to add topics for their workflows by a pull request to this file, if they feel a topic is not represented.

## Working with a local copy

In order to make contributions, you can set up a local copy of the catalog and test your changes.

First, fork the repository on Github:

1. Go to the [Snakemake Workflow Catalog repository](https://github.com/snakemake/snakemake-workflow-catalog) on Github.
2. Click on the "Fork" button in the top right corner ([Github documentation: Forking a repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo)).

Then, clone the forked repository:

1. Open a terminal on your local machine.
2. Run `git clone https://github.com/{your-username}/snakemake-workflow-catalog.git` to clone the repository ([Github documentation: Cloning a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)).

Make your changes to the catalog:

1. Create a conda/mamba environment in order to work with the catalog locally.

```bash
cd <path-to>/snakemake-workflow-catalog
conda env create -n snakemake-workflow-catalog -f environment.yml
conda activate snakemake-workflow-catalog
```

2. Set required environment variables.
The variable `N_REPOS` can be used to fetch data from a limited number of repos.
The variable `TEST_REPO` can be used to fetch only data from a single workflow.
**Note:** Building the entire catalog from scratch will take several hours due to searching and testing thousands of Github repos.

```bash
export GITHUB_TOKEN="<your-github-token>"
export OFFSET=0
export LATEST_COMMIT=1000
export N_REPOS=3
export TEST_REPO="snakemake-workflows/rna-seq-star-deseq2"
```

3. Build the catalog data sources using the test repository.

```bash
python scripts/generate-catalog.py
python scripts/cleanup-catalog.py
```

4. Build the catalog web page using sphinx autobuild (live reload).

```bash
sphinx-autobuild source/ build/
```

... or using the make file (static build).

```bash
make html
```

5. Run `git add .` to stage your changes.
6. Run `git commit -m "fix: your commit message"` to commit your changes.
7. Run `git push` to push your changes to your fork on Github.

Finally, create a pull request:

1. Go to your fork on Github.
2. Follow the instructions on the [Github documentation: Creating a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request).

## Using workflows from the catalog

To get started with a workflow from the catalog:

1. Clone the repository or download the specific workflow directory.
2. Review the documentation provided with the workflow to understand its requirements and usage.
3. Configure the workflow by editing the `config.yml` files as needed.
4. Execute the workflow using Snakemake.

For more detailed instructions, please refer to the documentation within each workflow directory.

## License

The Snakemake Workflow Catalog is open-source and available under the MIT License.
For more information and to explore the available workflows, visit https://snakemake.github.io/snakemake-workflow-catalog/.

Note: All workflows collected and presented on the Catalog are licensed under their own terms!
