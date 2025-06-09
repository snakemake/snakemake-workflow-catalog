---
notoc: true
description: "all standardized workflows"
---

# All standardized workflows

<!-- NOTE: the raw strings for commas are required to ensure correct line breaks-->

```{csv-table} All workflows according to 'standardized usage'
:header: Workflow,Description,Topics,Reporting,Stars,Watchers
:class: sphinx-datatable
:width: 100%
:widths: auto

{% for repo in input -%}
    [{{ repo["full_name"] }}](<workflows/{{ repo["full_name"] }}>){% raw %},{% endraw %}
    "{{ repo["description"] }}"{% raw %},{% endraw %}
    {%- for t in repo["topics"] -%}{bdg-secondary}`{{ t }}` {% endfor %}{% raw %},{% endraw %}
    {bdg-muted}`last update {{ repo["last_update"] }}`
    {%- for qc in ["formatting", "linting"] -%}
        {%- if repo[qc] == None -%}
            {bdg-success}`{{qc}}: passed`
        {%- else -%}
            {bdg-ref-danger}`{{qc}}: failed <{{qc}}-{{ repo["full_name"]|slugify }}>`
        {%- endif -%}
    {% endfor %}{% raw %},{% endraw %}
    {{ repo["stargazers_count"] }}{% raw %},{% endraw %}
    {{ repo["subscribers_count"] }}
{% endfor %}
```
