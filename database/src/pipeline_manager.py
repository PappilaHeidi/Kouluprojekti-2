# pipeline_manager.py
from datetime import datetime
import pandas as pd
from connection_tool import MojovaDB
from utils import MojovaModels
import logging
from typing import Dict
import json
from dotenv import load_dotenv
import re
import numpy as np
import json

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
            'silver': 'Analytics',
            'gold': 'Analytics'
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
    
    def _gold_transform(self, source, df):
        """
        Gold transformation:

        Transforms the given DataFrame locally. Modifies it in-place and returns it.

        Parameters:
            df (pd.DataFrame): Input DataFrame to transform.

        Returns:
            pd.DataFrame: Transformed DataFrame (same as input, modified in-place).
        """
        if source == "hopp":
            ## kooste ##
            df_kooste_hopp = df.copy()
            df_kyssarit = df.copy()
            df_columns = ['kysely', 'vuosineljannes', 'luokittelukoodi', 'kysymys_pitka', 'kyselyita', 'vastauksia', 'keskiarvo'
            ]
            luokittelusuodatus = ["AIKTEHOHO", "EALAPSAIK", "ENSIHOITO"]
            df_kooste_hopp = df_kooste_hopp[df_columns]
            df_kooste_hopp = df_kooste_hopp[df_kooste_hopp["luokittelukoodi"].isin(luokittelusuodatus)]
            # standardize columns to match with other hopp dataset
            df_kooste_hopp = self._kooste_transform(df_kooste_hopp)
            df_kooste_hopp["quarter"] = df_kooste_hopp["vuosineljannes"].astype(str).apply(lambda x: f"{x[4:]}_{x[:4]}")

            # pivot
            df_kooste_hopp = df_kooste_hopp.pivot_table(
                index="quarter",  # Group by 'vuosineljannes'
                columns="kysymys_pitka",  # Use 'kysymys_pitka' as columns
                values=["keskiarvo"],  # Aggregate these columns
                aggfunc="mean"  # Calculate the mean
            )
            # Flatten the column MultiIndex for better readability
            df_kooste_hopp.columns = [col[1] for col in df_kooste_hopp.columns.values]
            # Reset index for a clean table
            df_kooste_hopp = df_kooste_hopp.reset_index()
            # standardize columns
            df_kooste_hopp.columns = [self._standardize(col) for col in df_kooste_hopp.columns]

            ## kyssarit ##
            df_columns = ['quarter', 'unit_code', '1_hoitajat_ottivat_mielipiteeni_huomioon_kun_hoitoani_suunniteltiin_tai_toteutettiin',
            '2_hoitajat_ja_laakarit_toimivat_hyvin_yhdessa_hoitooni_liittyvissa_asioissa',
            '3_hoitoni_oli_hyvin_suunniteltu_ja_toteutettu_hoitajien_seka_laakareiden_toimesta',
            '4_hoitajat_pyysivat_minulta_anteeksi_jos_hoidossani_tapahtui_virhe',
            '5_hoitajat_puuttuivat_epakohtaan_josta_mainitsin_heille',
            '6_hoitajat_kertoivat_minulle_uuden_laakkeen_antamisen_yhteydessa_miksi_laaketta_annetaan',
            '7_hoitajat_kertoivat_minulle_saamieni_laakkeiden_mahdollisista_sivuvaikutuksista',
            '8_hoitajat_puhuivat_arkaluontoisista_asioista_siten_etteivat_ulkopuoliset_kuulleet_niita',
            '9_hoitajat_huolehtivat_etta_liikkuminen_oli_turvallista_hoidon_aikana',
            '10_hoitajat_kohtelivat_minua_hyvin',
            '11_hoitajat_huolehtivat_etteivat_hoito_ja_tai_tutkimukset_aiheuttaneet_minulle_noloja_tai_kiusallisia_tilanteita',
            '12_hoitajat_huolehtivat_yksityisyyteni_toteutumisesta',
            '13_sain_tarvitsemani_avun_hoitajilta_riittavan_nopeasti',
            '14_sain_hoitajilta_apua_riittavan_nopeasti_halutessani_wc:hen_tai_alusastian',
            '15_hoitajat_selittivat_ymmarrettavasti_hoitooni_ja_tutkimuksiini_liittyvat_asiat',
            '16_hoitajat_ohjasivat_ymmarrettavasti_jatkohoitooni_liittyvat_asiat',
            '17_hoitajat_ohjasivat_ymmarrettavasti_kotona_vointini_tarkkailuun_liittyvat_asiat',
            '18_hoitajat_varmistivat_etta_ymmarsin_saamani_tiedon',
            '19_hoitaja_huolehti_etta_sain_lievitysta_kipuihin_kun_siihen_oli_tarvetta',
            '20_hoitajat_arvioivat_kipujani_riittavan_usein',
            '21_hoitajat_kuuntelivat_minua_huolellisesti',
            '22_hoitajat_olivat_aidosti_lasna']

            df_kyssarit = df_kyssarit[df_columns]
            df_kyssarit = df_kyssarit[df_kyssarit["unit_code"].isin(luokittelusuodatus)]
            df_kyssarit.replace("E", np.nan, inplace=True)
            df_kyssarit.dropna(how="all", inplace=True)
            df_kyssarit = df_kyssarit.groupby("quarter").mean(numeric_only=True).reset_index()
            df_kyssarit["quarter"] = df_kyssarit["quarter"].apply(lambda x: f"{int(x.split('_')[0]):02d}_{x.split('_')[1]}")

            # add column to separate aggergated data
            df_kooste_hopp.insert(1, "datajoukko", None)
            df_kooste_hopp["datajoukko"] = "kooste"
            df_kyssarit["datajoukko"] = "kainuu"

            # combine aggregated datasets in one dataframe
            df_combined =  pd.concat([df_kooste_hopp, df_kyssarit], ignore_index=True)
            df_combined['/medallion'] = 'gold_hopp'
            return df_combined
        
    async def process_data(self, source: str, layer: str) -> Dict:
        """Process data through the pipeline"""
        logger.info(f"Starting {self.target_layer} processing for {source}")
        # Ajaa dataputken 
        try:
            # Extract
            df = self._extract_data(source)
            if df.empty:
                return {"status": "completed", "message": "No data to process"}

            # Silver transform
            if layer.lower() == 'silver':
                df = self._silver_transform(source, df)
                logger.info("Doing transformations")
            
            # Gold transform
            if layer.lower() == 'gold':
                df = self._gold_transform(source, df)
                logger.info("Doing transformations")
 

            if df.empty:
                return {"status": "completed", "message": "No valid records after transformation"}
            
            # Load
            #df.to_json('gold_aggr.json', orient='records', lines=True) ## for testing ##
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
        
    def _standardize(self, col):
        """
        Standardizes columns
        Parameters:
            col (List): Input list of columns
        
        Returns:
            col (List): Standardized list of column names
        """
        col = re.sub(r'\b0(\d+)\b', r'\1', col.strip())
        return col.strip().replace(' ', '_').replace('ä', 'a').replace('\n', '').replace('(', '').replace(')', '').replace('/', '_').replace(',', '').replace('.', '').lower().replace('ö', 'o')
    
    def _kooste_transform(self, df_kooste_hopp):
        """ad-hoc transform  for hopp kooste dataset"""

        df_kooste_hopp = df_kooste_hopp[~df_kooste_hopp['kysymys_pitka'].str.contains(r"(lapseni|Lapseni|lapselleni)", na=False)]


        df_kooste_hopp = df_kooste_hopp[df_kooste_hopp['kysymys_pitka'] !=
            '11 Hoitajat auttoivat minua, jos minuun sattui']

        df_kooste_hopp = df_kooste_hopp[df_kooste_hopp['kysymys_pitka'] !=
            '12 Hoitajilla oli aikaa kuunnella minua']

        df_kooste_hopp = df_kooste_hopp[df_kooste_hopp['kysymys_pitka'] !=
            '13 Hoitajat kuuntelivat meitä huolellisesti']

        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '01 Hoitajat ja minä suunnittelimme hoitoani yhdessä',
            '01 Hoitajat ottivat mielipiteeni huomioon, kun hoitoani suunniteltiin tai toteutettiin'
        )

        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '03 Hoitajat hoitivat asian, josta sanoin, että se pitää korjata',
            '03 Hoitoni oli hyvin suunniteltu ja toteutettu hoitajien ja lääkäreiden toimesta'
        )

        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '05 Hoitajat puhuivat kanssani niin, ettei kukaan minulle tuntematon kuullut asioitani',
            '08 Hoitajat puhuivat arkaluontoisista asioista siten, etteivät ulkopuoliset kuulleet niitä'
        )

        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '04 Hoitajat kertoivat minulle, miksi lääkettä annetaan',
            '06 Hoitajat kertoivat minulle uuden lääkkeen antamisen yhteydessä, miksi lääkettä annetaan'
        )

        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '08 Hoitajat olivat kohteliaita',
            '10 Hoitajat kohtelivat minua hyvin'
        )

        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '06 Hoitajat olivat minulle ystävällisiä',
            '10 hoitajat kohtelivat minua hyvin'
        )

        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '07 Hoitajat huolehtivat, ettei hoito tai tutkimukset aiheuttaneet minulle noloja tilanteita',
            '11 hoitajat huolehtivat etteivat hoito ja tai tutkimukset aiheuttaneet minulle noloja tai kiusallisia tilanteita'
        )

        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '07 Hoitajat puhuivat arkaluontoisista asioista siten, etteivät ulkopuoliset kuulleet niitä',
            '11 hoitajat huolehtivat etteivat hoito ja tai tutkimukset aiheuttaneet minulle noloja tai kiusallisia tilanteita'
        )

        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '08 Hoitajat auttoivat minua aina, kun tarvitsin apua',
            '13 sain tarvitsemani avun hoitajilta riittavan nopeasti'
        )

        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '09 Hoitajat kertoivat minulle, miksi ja miten minua hoidetaan',
            '15 hoitajat selittivat ymmarrettavasti hoitooni ja tutkimuksiini liittyvat asiat'
        )

        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '10 Hoitajat kertoivat minulle asioista niin, että minun oli helppo ymmärtää ne',
            '18 hoitajat varmistivat etta ymmarsin saamani tiedon'
        )

        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '11 Hoitajat auttoivat minua, jos minuun sattui',
            '18 hoitajat varmistivat etta ymmarsin saamani tiedon'
        )

        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '11 Hoitajat huolehtivat, etteivät hoito ja/tai tutkimukset aiheuttaneet minulle noloja tai kiusallisia tilanteita',
            '11 hoitajat huolehtivat etteivat hoito ja tai tutkimukset aiheuttaneet minulle noloja tai kiusallisia tilanteita'
        )

        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '14 Hoitajat olivat aidosti läsnä',
            '22 Hoitajat olivat aidosti läsnä'
        )

        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '15 Hoitajat selittivät ymmärrettävästi hoitooni ja tutkimuksiini liittyvät asiat',
            '15 hoitajat selittivat ymmarrettavasti hoitooni ja tutkimuksiini liittyvat asiat'
        )

        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '18 Hoitajat varmistivat, että ymmärsin saamani tiedon',
            '18 hoitajat varmistivat etta ymmarsin saamani tiedon'
        )
        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '10 Hoitajat kohtelivat minua hyvin',
            '10 hoitajat kohtelivat minua hyvin'
        )
        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '18 Hoitajat varmistivat, että ymmärsin saamani tiedon',
            '18_hoitajat_varmistivat_etta_ymmarsin_saamani_tiedon'
        )

        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '13 sain tarvitsemani avun hoitajilta riittavan nopeasti',
            '13 Sain tarvitsemani avun hoitajilta riittävän nopeasti'
        )
        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '02 Hoitajat pyysivät minulta anteeksi, jos hoidossa tapahtui virhe',
            '04 Hoitajat pyysivät minulta anteeksi, jos hoidossani tapahtui virhe'
        )

        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '02 Hoitajat pyysivät minulta anteeksi, jos hoidossa tapahtui virhe',
            '04 Hoitajat pyysivät minulta anteeksi, jos hoidossani tapahtui virhe'
        )

        df_kooste_hopp['kysymys_pitka'] = df_kooste_hopp['kysymys_pitka'].replace(
            '03 Hoitoni oli hyvin suunniteltu ja toteutettu hoitajien ja lääkäreiden toimesta',
            '03 Hoitoni oli hyvin suunniteltu ja toteutettu hoitajien sekä lääkäreiden toimesta'
        )
        return df_kooste_hopp