import pandas as pd
import json
import os
import re
import uuid
import numpy as np

class IngestionTool():
    def __init__(self):
        pass
        self.ingestion_path = './data/ingestion/'

    def column_clean_up(self, df: pd.DataFrame) -> pd.DataFrame:
        def row_by_row(col):
            return col.strip().replace(' ', '_').replace('ä', 'a').replace('\n', '').replace('(', '').replace(')', '').replace('/', '_').replace(',', '').replace('.', '').lower().replace('ö', 'o')
        if isinstance(df, dict):
            print("probably ness")
            sheet = self.check_sheets(df)
            df = df[sheet]
            print(df)

        df.columns = [row_by_row(col) for col in df.columns]
        self.df = df
        return df

    def read_excel(self, fpath):
        try:
            if self.test_partition(fpath):
                df = pd.read_excel(fpath)

            if self.test_partition(fpath) is False:
                df = pd.read_excel(fpath, sheet_name=None)

            self.df_from_excel = df 
        except Exception as e:
            return {"message": f"Error reading file: {str(e)}"}
        
        return df
    

    def check_sheets(self, dict_sheets: dict):
        desired_sheets = ["Matriisi", "Data", "Kaikki vastaajat"]
        for sheet in desired_sheets:
            if sheet in dict_sheets:
                return sheet
        return None
    
    def json_to_file(self, filename):
        fpath = os.path.join(self.ingestion_path, f"{filename}.json")
        self.df.to_json(fpath, orient='records', indent=4, lines=False)
        self.df = self.df.replace({np.nan: None})
        self.json_data = self.df.to_dict(orient='records')
        print(type(self.json_data))

    def test_partition(self, filename):
        # Define regex patterns for "hopp" and "nes" separately
        hopp_pattern = r'(?:\b|_)hopp'
        ness_pattern = r'(?:\b|_)nes'
        # Check if "hopp" is in the filename
        if re.search(hopp_pattern, filename, re.IGNORECASE):
            return True
        # Check if "ness" is in the filename
        elif re.search(ness_pattern, filename, re.IGNORECASE):
            return False
        # If neither is found, return None or handle as needed
        else:
            return None

    def set_id(self):
        for item in self.json_data:
            item.setdefault("id", str(uuid.uuid4()))

    def set_partitionkey(self, medallion: str):
        for item in self.json_data:
            item.setdefault("/medallion", medallion)