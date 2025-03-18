
## Using workflows

### Basic usage

To get started with a workflow from the catalog:

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

For more detailed instructions, please refer to the individual documentation for each [workflow](<all_standardized_workflows>).

### Deployment options

The deployment method is controlled using the `--software-deployment-method` (short `--sdm`) argument.

To run the workflow with automatic deployment of all required software via `conda`/`mamba`, use

```bash
snakemake --cores all --sdm conda
```

To run the workflow using `apptainer`/`singularity`, use

```bash
snakemake --cores all --sdm apptainer
```

To run the workflow using a combination of `conda` and `apptainer`/`singularity` for software deployment, use

```bash
snakemake --cores all --sdm conda apptainer
```

Snakemake will automatically detect the main `Snakefile` in the `workflow` subfolder and execute the workflow.

For further options such as cluster and cloud execution, see [the docs](https://snakemake.readthedocs.io/).
