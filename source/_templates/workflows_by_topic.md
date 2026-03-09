# Top workflows by topic

- topics were clustered by similarity using a language model
- topics can be added by users by [opening a pull request](contributions) with updates to `topics.json`
- only [standardized workflows](all_standardized_workflows) are included
- follow the links to the individual workflow pages to get more information

{% for topic in input -%}

## {{ topic["name"] }} ({{ topic["number"] }})

**Keywords**

{% for kw in topic["keywords"] -%}
{bdg-info-line}`{{ kw }}`
{% endfor %}

**Matching workflows**

{% for repo in topic["repos"] -%}
{bdg-ref-secondary}`{{ repo }} <workflows/{{ repo }}>`
{% endfor %}

{% endfor %}

```{toctree}
:hidden:

```
