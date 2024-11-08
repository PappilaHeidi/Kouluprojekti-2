import pandas as pd
import json
import os

class IngestionTool():
    def __init__(self):
        pass
        self.ingestion_path = './data/ingestion/'

    def column_clean_up(self, df: pd.DataFrame) -> pd.DataFrame:
        def row_by_row(col):
            return col.strip().replace(' ', '_').replace('ä', 'a').replace('\n', '').replace('(', '').replace(')', '').replace('/', '_').replace(',', '').replace('.', '').lower().replace('ö', 'o')
        
        df.columns = [row_by_row(col) for col in df.columns]
        self.df = df
        return df

    def read_excel(self, fpath):
        try:
            df = pd.read_excel(fpath)
        except Exception as e:
            return {"message": f"Error reading file: {str(e)}"}
        self.df_from_excel = df
        return df
    

    def json_to_file(self, filename):
        fpath = os.path.join(self.ingestion_path, f"{filename}.json")
        self.df.to_json(fpath, orient='records', indent=4)
