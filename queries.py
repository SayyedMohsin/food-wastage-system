# queries.py  (copy-paste 100 % ready)
from sqlalchemy import text
from database import engine
import pandas as pd

QUERY_MAP = {
    "1️⃣ Providers per City":
    "SELECT City AS City, COUNT(*) AS Total_Providers FROM providers GROUP BY City ORDER BY Total_Providers DESC;",

    "2️⃣ Top Provider Type":
        "SELECT type AS Provider_Type, COUNT(*) AS Count FROM providers GROUP BY type ORDER BY Count DESC LIMIT 1;",

    "3️⃣ Provider Contacts in Delhi":
        "SELECT name AS Provider_Name, contact AS Phone FROM providers WHERE city = 'Delhi';",

    "4️⃣ Top 5 Receivers by Claims":
        """SELECT r.name AS Receiver_Name, COUNT(c.claim_id) AS Total_Claims
           FROM receivers r JOIN claims c ON r.receiver_id = c.receiver_id
           GROUP BY r.name ORDER BY Total_Claims DESC LIMIT 5;""",

    "5️⃣ Total Food Available":
        "SELECT SUM(quantity) AS Total_Quantity FROM food_listings;",

    "6️⃣ City with Highest Listings":
    "SELECT Location AS City, COUNT(*) AS Total_Listings FROM food_listings GROUP BY Location ORDER BY Total_Listings DESC LIMIT 1;",

    "7️⃣ Most Common Food Types":
        "SELECT food_type AS Food_Type, COUNT(*) AS Count FROM food_listings GROUP BY food_type ORDER BY Count DESC;",

    "8️⃣ Claims per Food Item":
        """SELECT f.food_name AS Food_Name, COUNT(c.claim_id) AS Total_Claims
           FROM food_listings f LEFT JOIN claims c ON f.food_id = c.food_id
           GROUP BY f.food_name ORDER BY Total_Claims DESC;""",

    "9️⃣ Provider with Most Successful Claims":
        """SELECT p.name AS Provider_Name, COUNT(c.claim_id) AS Successful_Claims
           FROM providers p
           JOIN food_listings f ON p.provider_id = f.provider_id
           JOIN claims c ON f.food_id = c.food_id
           WHERE c.status = 'Completed'
           GROUP BY p.name ORDER BY Successful_Claims DESC LIMIT 1;""",

    "🔟 Claims Status %":
        """SELECT status AS Status, ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) AS Percentage
           FROM claims GROUP BY status;""",

    "1️⃣1️⃣ Avg Quantity Claimed per Receiver":
        """SELECT AVG(qty) AS Avg_Quantity FROM
           (SELECT r.receiver_id, SUM(f.quantity) AS qty
            FROM claims c
            JOIN food_listings f ON c.food_id = f.food_id
            JOIN receivers r ON c.receiver_id = r.receiver_id
            GROUP BY r.receiver_id);""",

    "1️⃣2️⃣ Most Claimed Meal Type":
        """SELECT f.meal_type AS Meal_Type, COUNT(*) AS Total_Claims
           FROM food_listings f
           JOIN claims c ON f.food_id = c.food_id
           GROUP BY f.meal_type ORDER BY Total_Claims DESC LIMIT 1;""",

    "1️⃣3️⃣ Total Donated per Provider":
        """SELECT p.name AS Provider_Name, SUM(f.quantity) AS Total_Donated
           FROM providers p
           JOIN food_listings f ON p.provider_id = f.provider_id
           GROUP BY p.name ORDER BY Total_Donated DESC;""",

    "1️⃣4️⃣ Expired vs Claimed Food":
        """SELECT
           SUM(CASE WHEN f.expiry_date < DATE('now') THEN f.quantity ELSE 0 END) AS Expired_Qty,
           SUM(CASE WHEN c.status = 'Completed' THEN f.quantity ELSE 0 END) AS Claimed_Qty
           FROM food_listings f LEFT JOIN claims c ON f.food_id = c.food_id;""",

    "1️⃣5️⃣ Weekly Expiry Trend":
        """SELECT strftime('%Y-%W', expiry_date) AS Week, SUM(quantity) AS Weekly_Qty
           FROM food_listings GROUP BY Week ORDER BY Week;"""
}

def run_all_queries(filters: dict):
    results = {}
    with engine.connect() as conn:
        where_parts = []
        params = {}
        if filters.get('city'):
            where_parts.append("city = :city")
            params['city'] = filters['city']
        if filters.get('provider'):
            where_parts.append("provider_id = :provider")
            params['provider'] = filters['provider']
        if filters.get('food_type'):
            where_parts.append("food_type = :food_type")
            params['food_type'] = filters['food_type']
        if filters.get('meal_type'):
            where_parts.append("meal_type = :meal_type")
            params['meal_type'] = filters['meal_type']
        where_clause = (" WHERE " + " AND ".join(where_parts)) if where_parts else ""

        for title, sql in QUERY_MAP.items():
            safe_sql = sql
            if "food_listings" in sql.lower() and where_clause:
                safe_sql = sql.replace("FROM food_listings", f"FROM food_listings {where_clause}")
            df = pd.read_sql(text(safe_sql), conn, params=params)
            results[title] = df
    return results