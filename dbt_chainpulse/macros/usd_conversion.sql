{% macro usd_conversion(amount_column, price_column) %}
  coalesce({{ amount_column }} * nullif({{ price_column }}, 0), 0)
{% endmacro %}
