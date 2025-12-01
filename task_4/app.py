import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os

st.set_page_config(layout="wide")

# --------------------------
# Function to load result JSON
# --------------------------
def load_json(folder):
    path = os.path.join(folder, "result.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# --------------------------
# Dashboard Layout
# --------------------------
st.title("📊 Online Dashboard for Book Store Analysis")

tabs = st.tabs(["DATA1", "DATA2", "DATA3"])

folders = ["DATA1", "DATA2", "DATA3"]

for tab, folder in zip(tabs, folders):
    with tab:
        st.header(f"Dataset: {folder}")

        data = load_json(folder)

        # --- Cards with KPIs ---
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Unique Users", data["unique_users"])

        with col2:
            st.metric("Unique Author Sets", data["unique_author_sets"])

        with col3:
            st.metric("Most Popular Author", data["most_popular_author"])

        st.subheader("Best Buyer(s)")
        st.write(data["best_buyer"])

        # --- Top 5 days ---
        st.subheader("Top 5 Days by Revenue")
        st.write(pd.DataFrame({"date": data["top_5_days"]}))

        # --- Daily Revenue Chart ---
        st.subheader("Daily Revenue Chart")

        df_rev = pd.DataFrame(data["daily_revenue"])

        if not df_rev.empty:
            df_rev["date"] = pd.to_datetime(df_rev["date"])
            df_rev = df_rev.sort_values("date")

            fig, ax = plt.subplots()
            ax.plot(df_rev["date"], df_rev["paid_price"])
            ax.set_ylabel("Revenue (USD)")
            ax.set_xlabel("Date")
            ax.set_title("Daily Revenue")
            st.pyplot(fig)
        else:
            st.info("No daily revenue data available for this dataset.")
