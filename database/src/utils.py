from dotenv import load_dotenv
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import azure.cosmos.partition_key as PK
import os
from jinja2 import Environment, FileSystemLoader

class MojovaModels:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(os.path.dirname(current_dir), 'db_templates')

        try:
            self.env = Environment(loader=FileSystemLoader(template_dir))
            # Test template loading
            print("Available templates: " + str(self.env.list_templates()))
        except Exception as e:
            print(f"Error initializing Jinja environment: {str(e)}")
            raise
    
    def get_query(self, template):
        # TODO: Add templates for gold
        try:
            match template:
                case 'bronze_hopp':
                    sql_template = self.env.get_template('bronze.sql')
                    query_template = sql_template.render(
                        table_name="c",
                        filter_column="c['/medallion']",
                        filter_value="bronze_hopp"
                    )
                    print(f"Generated query: {query_template}")
                    return query_template
                    
                case 'bronze_nes':
                    sql_template = self.env.get_template('bronze.sql')
                    query_template = sql_template.render(
                        table_name="c",
                        filter_column="c['/medallion']",
                        filter_value="bronze_nes"
                    )
                    print(f"Generated query: {query_template}")
                    return query_template
                    
                case 'silver_hopp':
                    sql_template = self.env.get_template('silver.sql')
                    query_template = sql_template.render(
                        table_name="c",
                        filter_column="c['/medallion']",
                        filter_value="silver_hopp"
                    )
                    print(f"Generated query: {query_template}")
                    return query_template
                case 'silver_nes':
                    sql_template = self.env.get_template('silver.sql')
                    query_template = sql_template.render(
                        table_name="c",
                        filter_column="c['/medallion']",
                        filter_value="silver_nes"
                    )
                    print(f"Generated query: {query_template}")
                    return query_template
                case _:
                    print(f"Unknown template: {template}")
                    return None
                    
        except Exception as e:
            print(f"Error generating query for template {template}: {str(e)}")
            return None
