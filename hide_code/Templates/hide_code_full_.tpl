{%- extends 'full.tpl' -%}
{%- block header -%}
{{ super() }}

 <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.12.1/jquery-ui.css">

<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.9.1/jquery-ui.min.js"></script>

<link rel="stylesheet" type="text/css" href="https://min.gitcdn.xyz/cdn/ipython-contrib/jupyter_contrib_nbextensions/master/src/jupyter_contrib_nbextensions/nbextensions/toc2/main.css">

<link rel="stylesheet" type="text/css" href="https://min.gitcdn.xyz/cdn/ipython-contrib/jupyter_contrib_nbextensions/master/src/jupyter_contrib_nbextensions/nbextensions/collapsible_headings/main.css">

<link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">

<script src="https://min.gitcdn.xyz/cdn/ipython-contrib/jupyter_contrib_nbextensions/master/src/jupyter_contrib_nbextensions/nbextensions/toc2/toc2.js"></script>

<script src="https://min.gitcdn.xyz/cdn/ipython-contrib/jupyter_contrib_nbextensions/master/src/jupyter_contrib_nbextensions/nbextensions/collapsible_headings/main.js"></script>

<script>
$( document ).ready(function(){
            var cfg = {{ nb.get('metadata', {}).get('toc', {})|tojson|safe }};
	    var cd2=  {{ nb.get('notebook').get('collapsible_headings', {}) }};
            cfg.navigate_menu=false;
            // fire the main function with these parameters
            require(['nbextensions/toc2/toc2'], function (toc2) {
                toc2.table_of_contents(cfg);
            });
	    
	    require(['nbextensions/collapsible_headings/main'], function (ch) {
		ch.set_collapsible_headings_options(cd2);
		ch.refresh_all_headings();
	    });
    });
</script>
{%- endblock header -%}
{%-block html_head-%}
    <style type="text/css">
        div.output_subarea {
            max-width: 100% !important;
        }
    </style>
    {{ super() }}
    
{%- endblock html_head -%}

{%- block input -%}
    {%- if cell.metadata.hideCode -%}
        <div></div>
    {%- else -%}
        {{ super() }}
    {%- endif -%}
{%- endblock input -%}

{%- block in_prompt -%}
    {%- if cell.metadata.hidePrompt -%}
        <div class="prompt input_prompt"></div>
    {%- else -%}
        {{ super() }}
    {%- endif -%}
{%- endblock in_prompt -%}

{% block output %}
    <div class="output_area">
    {% if resources.global_content_filter.include_output_prompt %}
        {% block output_area_prompt %}
            {%- if output.output_type == 'execute_result' and not cell.metadata.hidePrompt -%}
                <div class="prompt output_prompt">
                {%- if cell.execution_count is defined -%}
                    Out[{{ cell.execution_count|replace(None, "&nbsp;") }}]:
                {%- else -%}
                    Out[&nbsp;]:
                {%- endif -%}
            {%- else -%}
                <div class="prompt">
            {%- endif -%}
        </div>
        {% endblock output_area_prompt %}
    {% endif %}
{%- if cell.metadata.hideOutput -%}
{%- else -%}
    {% if output.data %}
        {% block execute_result -%}	{{ super() }} {% endblock execute_result %}
        {% block stream -%} {{ super() }} {% endblock stream -%}
        {%- if output.output_type == 'error' -%}
            {% block error %} {{ super() }} {% endblock error %}
        {%- endif -%}
    {%- elif output.text -%}
		{% block stream_stdout -%} {{ super() }} {% endblock stream_stdout -%}
    {%- endif -%}
{%- endif -%}
</div>
{% endblock output %}

{% block markdowncell scoped %}
{%- if cell.metadata.heading_collapsed -%}
<div class="cell border-box-sizing text_cell rendered collapsible_headings_collapsed">
{%- else -%}
<div class="cell border-box-sizing text_cell rendered">
{%- endif -%}
{{ self.empty_in_prompt() }}
<div class="inner_cell">
<div class="text_cell_render border-box-sizing rendered_html">
{{ cell.source  | markdown2html | strip_files_prefix }}
</div>
</div>
</div>
{%- endblock markdowncell %}
