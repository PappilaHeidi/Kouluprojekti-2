# pipeline_manager.py
from datetime import datetime
import pandas as pd
from .connection_tool import MojovaDB
from .utils import MojovaModels
import logging
from typing import Dict
import json
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PipelineManager:
    def __init__(self, source_layer: str, target_layer: str, api_url: str = None):
        self.source_layer = source_layer.lower()
        self.target_layer = target_layer.lower()
        self.models = MojovaModels()
        
        # Container mapping
        self.containers = {
            'bronze': 'Analytics',
            'silver': 'Silver',
            'gold': 'Gold'
        }
            
        logger.info(f"Initialized pipeline manager with source: {source_layer}, target: {target_layer}")
        
    
    
    def _extract_data(self, source: str) -> pd.DataFrame:
        """Extract data from source container"""
        try:
            source = source.lower()
            logger.info(f"Extracting {source} data from {self.source_layer} layer")
            
            # Init Database connection
            db = MojovaDB(self.containers[self.source_layer])
            db.connect()
            
            # Get Database models
            model = MojovaModels()
            query = model.get_query(f'{self.source_layer}_{source}')
            logger.info(f"Executing query: {query}")
            
            # Make Database query
            data = db.query(query)
            logger.info(f"Retrieved {len(data)} records")
            
            return pd.DataFrame(data) if data else pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Data extraction failed: {str(e)}")
            raise

    def _load_data(self, df: pd.DataFrame):
        """Load data to target container in the database"""
        try:
            logger.info(f"Starting data load to {self.target_layer} layer")
            
            # Prepare records for target layer
            json_str = df.to_json(orient='records', date_format='iso')
            records = json.loads(json_str)
            
            # Connect to target container
            db = MojovaDB(self.containers[self.target_layer])
            db.connect()

            # Load data into database
            db.upsert_data(records)
            logger.info(f"Successfully loaded {len(records)} records to {self.target_layer} layer")
            
        except Exception as e:
            logger.error(f"Data storing failed: {str(e)}")
            raise

    def _silver_transform(self, source: str, df: pd.DataFrame) -> pd.DataFrame:
        """Transform Bronze data to Silver format"""
        try:
            logger.info(f"Starting silver transformation for {source} data")
            if source == "hopp":
                # Create a copy for transformation
                silver_df = df.copy()
                
                # Remove extra columns
                extra_columns = ['/medallion','_rid', '_self', '_etag', '_attachments', '_ts']
                silver_df.drop(columns=extra_columns, inplace=True)
                
                # Renamecolumns
                column_mapping = {
                    'organisaatiokoodi_kolme_numeroa': 'org_code',
                    'yksikkokoodiks_luokitteluohje_yksikkokoodit-valilehdelta': 'unit_code',
                    'kvartaali_ja_vuosiesim_1_2020': 'quarter'
                }
                # TODO: Tähän voisi lisätä esim "E" arvojen käsittelyn?
                # Ns. pohja valmiina, tähän pitää tehdä jotain muuta vielä esim AIKTEHOHO EALAPSAIK ja ENSIHOITO vastaukset sort
                silver_df.rename(columns=column_mapping, inplace=True)

                logger.info(f"Completed silver transformation. Records: {len(silver_df)}")

                silver_df['/medallion'] = "silver_hopp"

                return silver_df
            elif source == "nes":
                # Copy data for transformation
                silver_df = df.copy()

                # Categorize Employment info
                # TODO: Onkohan tää hyvä?
                silver_df['employment_category'] = 'permanent'
                silver_df.loc[silver_df['tyosuhde'] == 2, 'employment_category'] = 'temporary'

                # First calculate all the average satisfactions
                silver_df['avg_org_satisfaction'] = silver_df[[
                    'uskon_org_paamaariin',
                    'tiedan_oman_toim_org_paamaariin',
                    'org_johto_arvojen_muk'
                ]].mean(axis=1)
                
                # Average leadership satisfaction
                silver_df['avg_leadership_satisfaction'] = silver_df[[
                    'lahiesimies_avoin_ehdotuksille',
                    'lahiesimies_hlokunnan_puolestapuhuja',
                    'lahiesimies_korostaa_hoidon_laatua',
                    'lahiesimies_hoitaa_velvoll'
                ]].mean(axis=1)
                
                # Average work conditions
                silver_df['avg_work_conditions'] = silver_df[[
                    'kaytettavissa_tarv_laitteet',
                    'sopivasti_potilaita',
                    'riittavasti_aikaa_pot'
                ]].mean(axis=1)
                
                # Average professional development
                silver_df['avg_professional_development'] = silver_df[[
                    'mahdoll_keskusteluun_ammuralla_eten',
                    'amm_kasvu_merkittavaa',
                    'opiskelua_tuetaan',
                    'org_tarjoaa_urallakehitt_mahd'
                ]].mean(axis=1)

                # Calculate overall satisfaction using the averages
                silver_df['overall_satisfaction'] = silver_df[[
                    'avg_org_satisfaction',
                    'avg_leadership_satisfaction',
                    'avg_work_conditions',
                    'avg_professional_development'
                ]].mean(axis=1)

                # Retention / Outlook indicators
                silver_df['retention_indicator'] = (
                    silver_df['tyoskentelen_3v_todnak'] +
                    silver_df['valmis_panostamaan'] +
                    silver_df['suosittelen_org']
                ) / 3

                # Remove extra columns
                columns_to_drop = ['_rid', '_self', '_etag', '_attachments', '_ts']
                silver_df = silver_df.drop(columns=columns_to_drop, errors='ignore')

                logger.info(f"Completed silver transformation. Records: {len(silver_df)}")

                silver_df['/medallion'] = "silver_nes"

                return silver_df
                
        except Exception as e:
            logger.error(f"Error in silver transformation: {str(e)}")
            raise
    
    async def process_data(self, source: str, layer: str) -> Dict:
        """Process data through the pipeline"""
        logger.info(f"Starting {self.target_layer} processing for {source}")
        # Ajaa dataputken 
        try:
            # Extract
            df = self._extract_data(source)
            if df.empty:
                return {"status": "completed", "message": "No data to process"}

            # Transform
            if layer.lower() == 'silver':
                df = self._silver_transform(source, df)
                logger.info("Doing transformations")
                
            if df.empty:
                return {"status": "completed", "message": "No valid records after transformation"}
            
            # Load
            self._load_data(df)
            logger.info("Start Loading data to database")
            
            return {
                "status": "completed",
                "message": f"Successfully processed {len(df)} records",
                "records_processed": len(df)
            }
            
        except Exception as e:
            error_msg = f"Pipeline failed: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "failed", 
                "message": error_msg
            }