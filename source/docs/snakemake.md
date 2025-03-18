
# Snakemake

```{toctree}
:hidden:
```

## What is Snakemake?

The Snakemake workflow management system is a tool to create reproducible and scalable data analyses. Workflows are described *via* a human readable, Python based language. They can be seamlessly scaled to server, cluster, grid and cloud environments, without the need to modify the workflow definition.

- To learn more about Snakemake, visit the [Snakemake homepage!](https://snakemake.github.io/)

- To get an impression of the Snakemake architecture, [read the Snakemake paper](https://doi.org/10.12688/f1000research.29032.2)

- To learn how to use Snakemake workflows, [read the documentation](https://snakemake.readthedocs.io/en/stable/).

## Create your own workflows

The best starting point to create your own workflows is the [Snakemake workflow template](https://github.com/snakemake-workflows/snakemake-workflow-template).

The template comes with a pre-configured structure that is compatible with the Snakemake catalog ['standardized usage'](<about/adding_workflows>). Just fork or clone the template, start addiong rules and push your workflow to Github. The structure of 'standardized' workflows is like this:

```
├── config/
│   └── config.yaml
│   └── README.md
├── workflow/
│   ├── Snakefile
│   ├── rules/
│   ├── scripts/
│   └── envs/
├── .snakemake-workflow-catalog.yml
└── README.md
```

:::{note}
The template is currently not fully functional as it contains no actual `Snakefile` and test cases. This will be changed in the near future.
:::

