from dotenv import load_dotenv
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import azure.cosmos.partition_key as PK
import os
from jinja2 import Environment, FileSystemLoader

class MojovaModels:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader('/app/db_templates/'))
    
    def get_query(self, template):
        match template:
            case 'bronze_hopp':
                template = self.env.get_template('bronze.sql')
                query_template = template.render(
                table_name="c",
                filter_column="c['/medallion']",
                filter_value="bronze_hopp"
                )
                return query_template
            case 'bronze_nes':
                template = self.env.get_template('bronze.sql')
                query_template = template.render(
                table_name="c",
                filter_column="c['/medallion']",
                filter_value="bronze_nes"
                )
                return query_template
            case 'silver_hopp':
                pass
            case 'silver_nes':
                pass
