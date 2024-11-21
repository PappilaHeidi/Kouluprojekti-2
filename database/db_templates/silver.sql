SELECT *
FROM {{ table_name }}
WHERE {{ filter_column }} = '{{ filter_value }}'