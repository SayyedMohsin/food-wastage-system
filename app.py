import streamlit as st
import pandas as pd
from queries import run_all_queries
from database import load_excel_to_sql
from sqlalchemy import text
from database import engine

st.set_page_config(page_title="Food Wastage Management", layout="wide")
st.title("🍲 Local Food Wastage Management System")

# ── Sidebar Menu ──
menu = ["View Listings", "Add Listing", "Edit Listing", "Delete Listing", "Analytics"]
choice = st.sidebar.selectbox("Menu", menu)

# Always reload database
load_excel_to_sql()

# ── 1. VIEW LISTINGS ──
if choice == "View Listings":
    st.subheader("📋 Available Food Listings")
    df = pd.read_sql("SELECT * FROM food_listings LIMIT 100", "sqlite:///db/food_wastage.db")
    st.dataframe(df, use_container_width=True)

# ── 2. ADD LISTING ──
elif choice == "Add Listing":
    st.subheader("➕ Add New Food Listing")
    with st.form("add_form"):
        name   = st.text_input("Food Name")
        qty    = st.number_input("Quantity", min_value=1)
        exp    = st.date_input("Expiry Date")
        prov   = st.number_input("Provider ID", min_value=1)
        loc    = st.text_input("City")
        ftype  = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
        mtype  = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
        submitted = st.form_submit_button("Add")
        if submitted:
            sql = text(
                "INSERT INTO food_listings(food_name, quantity, expiry_date, provider_id, city, food_type, meal_type) "
                "VALUES(:a,:b,:c,:d,:e,:f,:g)"
            )
            with engine.connect() as conn:
                conn.execute(sql, {"a": name, "b": qty, "c": exp, "d": prov, "e": loc, "f": ftype, "g": mtype})
                conn.commit()
            st.success("✅ Added!")

# ── 3. EDIT LISTING ──
elif choice == "Edit Listing":
    st.subheader("✏️ Edit Food Listing")
    listing_id = st.number_input("Food_ID to edit", min_value=1)
    if st.button("Fetch"):
        df = pd.read_sql(
            text("SELECT * FROM food_listings WHERE food_id = :id"),
            engine,
            params={"id": listing_id},
        )
        if not df.empty:
            name   = st.text_input("Food Name", value=df.iloc[0]["food_name"])
            qty    = st.number_input("Quantity", min_value=1, value=int(df.iloc[0]["quantity"]))
            exp    = st.date_input("Expiry Date", value=pd.to_datetime(df.iloc[0]["expiry_date"]).date())
            prov   = st.number_input("Provider ID", min_value=1, value=int(df.iloc[0]["provider_id"]))
            loc    = st.text_input("City", value=df.iloc[0]["city"])
            ftype  = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"], index=["Vegetarian", "Non-Vegetarian", "Vegan"].index(df.iloc[0]["food_type"]))
            mtype  = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"], index=["Breakfast", "Lunch", "Dinner", "Snacks"].index(df.iloc[0]["meal_type"]))
            if st.button("Update"):
                sql = text(
                    "UPDATE food_listings SET food_name=:a, quantity=:b, expiry_date=:c, provider_id=:d, city=:e, food_type=:f, meal_type=:g WHERE food_id=:id"
                )
                with engine.connect() as conn:
                    conn.execute(
                        sql,
                        {"a": name, "b": qty, "c": exp, "d": prov, "e": loc, "f": ftype, "g": mtype, "id": listing_id},
                    )
                    conn.commit()
                st.success("✅ Updated!")
        else:
            st.error("No listing found with this ID")

# ── 4. DELETE LISTING ──
elif choice == "Delete Listing":
    st.subheader("🗑️ Delete Food Listing")
    listing_id = st.number_input("Food_ID to delete", min_value=1)
    if st.button("Delete"):
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM food_listings WHERE food_id = :id"), {"id": listing_id})
            conn.commit()
        st.success("✅ Deleted!")

# ── 5. ANALYTICS (15 Queries) ──
elif choice == "Analytics":
    st.subheader("📊 Analytics – 15 SQL Queries")
    with st.sidebar:
        st.header("🔍 Filters")
        city_list = ["All"] + pd.read_sql("SELECT DISTINCT city FROM providers", "sqlite:///db/food_wastage.db")["city"].tolist()
        city = st.selectbox("City", city_list)
        prov_list = ["All"] + [str(x) for x in pd.read_sql("SELECT DISTINCT provider_id FROM food_listings", "sqlite:///db/food_wastage.db")["provider_id"].tolist()]
        provider = st.selectbox("Provider ID", prov_list)
        ft_list = ["All"] + pd.read_sql("SELECT DISTINCT food_type FROM food_listings", "sqlite:///db/food_wastage.db")["food_type"].tolist()
        food_type = st.selectbox("Food Type", ft_list)
        mt_list = ["All"] + pd.read_sql("SELECT DISTINCT meal_type FROM food_listings", "sqlite:///db/food_wastage.db")["meal_type"].tolist()
        meal_type = st.selectbox("Meal Type", mt_list)

    # Build filters dict
    filters = {}
    if city != "All":
        filters["city"] = city
    if provider != "All":
        filters["provider"] = int(provider)
    if food_type != "All":
        filters["food_type"] = food_type
    if meal_type != "All":
        filters["meal_type"] = meal_type

    # Run and display 15 queries
    results = run_all_queries(filters)
    for title, df in results.items():
        with st.expander(title):
            if df.empty:
                st.info("No data for selected filters.")
            else:
                st.dataframe(df, use_container_width=True)
                # Safe charts
                if len(df.columns) >= 2 and len(df) <= 30:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.bar_chart(df.set_index(df.columns[0])[df.columns[1]])
                    with col2:
                        fig = df.set_index(df.columns[0]).plot.pie(
                            y=df.columns[1], legend=False, autopct="%1.1f%%"
                        ).figure
                        st.pyplot(fig)
                else:
                    st.write("📊 Chart not shown (single value or too large).")

# ── 6. Provider Contacts ──
st.markdown("---")
st.header("📞 Provider Contact Details")
contacts = pd.read_sql("SELECT name, contact, city FROM providers", "sqlite:///db/food_wastage.db")
st.dataframe(contacts, use_container_width=True)