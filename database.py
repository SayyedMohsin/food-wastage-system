import pandas as pd
from sqlalchemy import create_engine
import os

# Relative path + auto-create folder
DB_PATH = os.path.join(os.path.dirname(__file__), "db", "food_wastage.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

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
        df.columns = [c.lower() for c in df.columns]
        df.to_sql(table, engine, if_exists='replace', index=False)
    print("✅ All Excel files loaded into SQLite.")

if __name__ == "__main__":
    load_excel_to_sql()
