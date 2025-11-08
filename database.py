import pandas as pd
from sqlalchemy import create_engine
import os

# Debug – Cloud में दिखेगा कौन-सी files मौजूद
print("📁 Contents of 'data' folder:")
print(os.listdir("data"))

# Relative path + auto-create folder
DB_PATH = os.path.join(os.path.dirname(__file__), "db", "food_wastage.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

def load_excel_to_sql():
    # Exact names जैसा GitHub पर दिख रहा है (case-sensitive)
    tables = {
    'food_listings': 'data/food_listings_data.xlsx',
    'providers':     'data/providers_data.xlsx',  # ← lower case
    'receivers':     'data/receivers_data.xlsx',
    'claims':        'data/claims_data.xlsx'
    }
    for table, file in tables.items():
        if not os.path.isfile(file):
            raise FileNotFoundError(f"❌ File not found: {file}")
        df = pd.read_excel(file)
        df.columns = [c.lower() for c in df.columns]
        df.to_sql(table, engine, if_exists='replace', index=False)
    print("✅ All Excel files loaded into SQLite.")

if __name__ == "__main__":
    load_excel_to_sql()
