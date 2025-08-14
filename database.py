import pandas as pd
from sqlalchemy import create_engine

DB_PATH = "db/food_wastage.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

def load_excel_to_sql():
    tables = {
        'food_listings': 'data/food_listings_data.xlsx',
        'providers':     'data/Providers_data.xlsx',
        'receivers':     'data/receivers_data.xlsx',
        'claims':        'data/claims_data.xlsx'
    }
    for table, file in tables.items():
        df = pd.read_excel(file)
        # सारे column names को lower-case करें ताकि case-sensitive error न हो
        df.columns = [c.lower() for c in df.columns]
        df.to_sql(table, engine, if_exists='replace', index=False)
    print("✅ All Excel files loaded into SQLite.")

if __name__ == "__main__":
    load_excel_to_sql()