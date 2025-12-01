import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import json
import os

st.set_page_config(layout="wide")

# --------------------------

# Function to load result JSON

# --------------------------

def load_json(folder):
    base_path = os.path.dirname(__file__)  # папка, где лежит app.py
    path_main = os.path.join(base_path, f"{folder}_results.json")
    if os.path.exists(path_main):
        with open(path_main, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# --------------------------

# Dashboard Layout

# --------------------------

st.title("📊 Online Dashboard for Book Store Analysis")

tabs = st.tabs(["DATA1", "DATA2", "DATA3"])
folders = ["DATA1", "DATA2", "DATA3"]

for tab, folder in zip(tabs, folders):
with tab:
st.header(f"📊 Dataset: {folder}")
data = load_json(folder)
if not data:
st.warning(f"No data found for {folder}. Make sure the JSON file exists.")
continue

    # --- KPI CARDS ---
    df_rev = pd.DataFrame(data.get("daily_revenue", []))
    total_rev = df_rev["paid_price"].sum() if not df_rev.empty else 0

    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Unique Users", data.get("unique_users", "N/A"))
    kpi_cols[1].metric("Unique Author Sets", data.get("unique_author_sets", "N/A"))
    kpi_cols[2].metric("Most Popular Author", data.get("most_popular_author", "N/A"))
    kpi_cols[3].metric("Total Revenue (USD)", f"${total_rev:,.2f}")

    # --- Best Buyer(s) ---
    st.subheader("🏆 Best Buyer(s)")
    st.write(data.get("best_buyer", "N/A"))

    # --- Top 5 Days ---
    st.subheader("📅 Top 5 Days by Revenue")
    top5 = pd.DataFrame({"date": data.get("top_5_days", [])})
    if not top5.empty:
        top5["date"] = pd.to_datetime(top5["date"])
        st.dataframe(top5.sort_values("date", ascending=False))
    else:
        st.info("No top 5 days data available.")

    # --- Daily Revenue Chart (Interactive) ---
    st.subheader("💰 Daily Revenue Chart")
    if not df_rev.empty:
        df_rev["date"] = pd.to_datetime(df_rev["date"])
        df_rev = df_rev.sort_values("date")
        fig = px.line(
            df_rev,
            x="date",
            y="paid_price",
            title="Daily Revenue Over Time",
            markers=True,
            labels={"paid_price": "Revenue (USD)", "date": "Date"}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No daily revenue data available.")









