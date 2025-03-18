
## Adding workflows

Workflows are **automatically added** to the Workflow Catalog. This is done by regularly searching Github repositories for matching workflow structures. The catalog includes workflows based on the following criteria.

### Generic workflows

- The workflow is contained in a public Github repository.
- The repository has a `README.md` file, containing the words "snakemake" and "workflow" (case insensitive).
- The repository contains a workflow definition named either `Snakefile` or `workflow/Snakefile`.
- If the repository contains a folder `rules` or `workflow/rules`, that folder must at least contain one file ending on `.smk`.
- The repository is small enough to be cloned into a [Github Actions](https://docs.github.com/en/actions/about-github-actions/understanding-github-actions) job (very large files should be handled via [Git LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files), so that they can be stripped out during cloning).
- The repository is not blacklisted here.

### *Standardized Usage* workflows

In order to additionally appear in the "standardized usage" area, repositories additionally have to:

- have their main workflow definition named `workflow/Snakefile` (unlike for [plain inclusion](#generic-workflows), which also allows just `Snakefile` in the root of the repository),
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
    singularity: true # whether pipeline works with '--sdm singularity/apptainer'
    singularity+conda: true # whether pipeline works with '--sdm conda singularity/apptainer'
    report: true # whether creation of reports using 'snakemake --report report.zip' is supported
```

:::{note}
Definition of mandatory flags can happen through a list of strings (`['--a', '--b']`), or a single string (`'--a --b'`).
:::

:::{note}
The content of the `.snakemake-workflow-catalog.yml` file is subject to change. Flags might change in the near future, but current versions will always stay compatible with the catalog. 
:::

Once included in the standardized usage area you can link directly to the usage instructions for your repository via the URL `https://snakemake.github.io/snakemake-workflow-catalog?usage=<owner>/<repo>`. Do not forget to replace the `<owner>` and `<repo>` tags at the end of the URL.

### Release handling

If your workflow provides Github releases, the catalog will always just scrape the latest non-preview release. Hence, in order to update your workflow's records here, you need to release a new version on Github.
