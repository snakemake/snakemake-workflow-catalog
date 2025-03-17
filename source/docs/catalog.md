
# The catalog

```{toctree}
:hidden:

about/purpose
about/using_workflows
about/adding_workflows
about/contributions
```

Here you can find the most important information about the **Snakemake workflow catalog**.

*Estimated reading time: 5 minutes*.

:::
## Use a workflow from the catalog
:::

1. Clone the repository or download the specific workflow directory.

```bash
git clone https://github.com/<user>/<workflow>
```

2. Review the documentation provided with the workflow to understand its requirements and usage.

3. Configure the workflow by editing the `config.yml` files as needed.

4. Create an environment with access to Snakemake. It is recommended to use `mamba`.

```bash
mamba create -n <env-name> -c <channels> snakemake
mamba activate <env-name>
```

5. Execute the workflow using Snakemake.

```bash
cd <workflow-dir>
snakemake --cores 2
```

:::{tip}
Use the `--dry-run` option first to check if all inputs are found.
:::

For more detailed instructions, please refer to the individual documentation for each [workflow](workflows/top_wf_by_stars.mdx).

:::
## Add a workflow to the catalog
:::

Workflows are **automatically added** to the Workflow Catalog. This is done by regularly searching Github repositories for matching workflow structures. The catalog includes workflows based on the following criteria.

The catalog currently discriminates between two types of workflows based on their documentation:

**Generic workflows**

- all snakemake workflows in public Github repositories
- repositories need to have a `README.md` file containing the words "snakemake" and "workflow"
- also need to have a workflow definition named either `Snakefile` or `workflow/Snakefile`, and contain rules in `*.smk` format.

**Standardized Usage workflows**

- workflows that additionally adhere to standards of the workflow catalog
- main workflow definition must be named `workflow/Snakefile`
- provide configuration instructions under `config/README.md`
- contain a `.snakemake-workflow-catalog.yml` file with instructions on deployment options
