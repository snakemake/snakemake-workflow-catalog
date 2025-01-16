# snakemake-workflow-catalog

[![Generate catalog](https://github.com/snakemake/snakemake-workflow-catalog/actions/workflows/generate.yml/badge.svg)](https://github.com/snakemake/snakemake-workflow-catalog/actions/workflows/generate.yml)
[![pages-build-deployment](https://github.com/snakemake/snakemake-workflow-catalog/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/snakemake/snakemake-workflow-catalog/actions/workflows/pages/pages-build-deployment)
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

```bash
usage:
  mandatory-flags: # optional definition of additional flags
    desc: # describe your flags here in a few sentences (they will be inserted below the example commands)
    flags: # put your flags here
  software-stack-deployment: # definition of software deployment method (at least one of conda, singularity, or singularity+conda)
    conda: true # whether pipeline works with --use-conda
    singularity: true # whether pipeline works with --use-singularity
    singularity+conda: true # whether pipeline works with --use-singularity --use-conda
    report: true # add this to confirm that the workflow allows to use 'snakemake --report report.zip' to generate a report containing all results and explanations
```

Once included in the standardized usage area you can link directly to the usage instructions for your repository via the URL `https://snakemake.github.io/snakemake-workflow-catalog?usage=<owner>/<repo>`.

### Release handling

If your workflow provides Github releases, the catalog will always just scrape the latest non-preview release. Hence, in order to update your workflow's records here, you need to release a new version on Github.

## Contributing

Contributions to the Snakemake Workflow Catalog are welcome!
Ideas can be discussed on the [catalog's Issues page](https://github.com/snakemake/snakemake-workflow-catalog/issues) first, and contributions made through Github Pull Requests.

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
