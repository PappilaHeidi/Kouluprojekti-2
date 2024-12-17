SELECT c.serialized_model
FROM {{ table_name }}
WHERE {{ filter_column }} = '{{ filter_value }}'