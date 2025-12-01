import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(
    page_title="Book Store BI Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Попробуем импортировать Plotly
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    import matplotlib.pyplot as plt
    PLOTLY_AVAILABLE = False

# --------------------------
# Load JSON data
# --------------------------
def load_json(folder):
    # Ищем файлы внутри папки task_4
    path_main = os.path.join("task_4", f"{folder}_results.json")
    st.write(f"Trying path: {path_main}")  # для отладки
    if os.path.exists(path_main):
        with open(path_main, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# --------------------------
# Render a single tab
# --------------------------
def render_tab(folder_name):
    st.header(f"📊 Dataset: {folder_name}")
    data = load_json(folder_name)
    if not data:
        st.warning(f"No data found for {folder_name}. Make sure the JSON file exists.")
        return

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

    # --- Daily Revenue Chart ---
    st.subheader("💰 Daily Revenue Chart")
    if not df_rev.empty:
        df_rev["date"] = pd.to_datetime(df_rev["date"])
        df_rev = df_rev.sort_values("date")
        if PLOTLY_AVAILABLE:
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
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(df_rev["date"], df_rev["paid_price"], marker='o', linestyle='-', color='tab:blue')
            ax.set_ylabel("Revenue (USD)")
            ax.set_xlabel("Date")
            ax.set_title("Daily Revenue Over Time")
            ax.grid(True)
            st.pyplot(fig)
    else:
        st.info("No daily revenue data available.")

# --------------------------
# Tabs
# --------------------------
tabs = st.tabs(["DATA1", "DATA2", "DATA3"])
folders = ["DATA1", "DATA2", "DATA3"]

for tab_obj, folder in zip(tabs, folders):
    with tab_obj:
        render_tab(folder)



