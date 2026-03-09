# Top workflows by {{ input[0]["metric"] }}

::::{grid} 3

{% for repo in input -%}

:::{grid-item-card} [{{ repo["name"] }}](workflows/{{ repo["full_name"] }})

{{ repo["user"] }}

^^^

{{ repo["description"] }}

---

{bdg-muted}`Updated: {{ repo["last_update"] }}`
{bdg-muted}`Release: {{ repo["latest_release"] }}`
{%- for qc in ["formatting", "linting"] -%}
{%- if repo[qc] == None -%}
{bdg-success}`{{qc}}: passed`
{%- else -%}
{bdg-danger}`{{qc}}: failed`
{%- endif -%}
{% endfor %}

+++

{octicon}`feed-star;1.0em;sd-text-success`
{bdg-primary-line}`{{ repo["stargazers_count"] }} stars`

{octicon}`eye;1.0em;sd-text-success`
{bdg-primary-line}`{{ repo["subscribers_count"] }} watchers`
:::
{% endfor %}

::::

```{toctree}
:hidden:

{% for repo in input -%}
workflows/{{ repo["full_name"] }}
{% endfor %}
```
