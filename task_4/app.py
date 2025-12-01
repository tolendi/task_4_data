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
# Попытка из подпапки
path_subfolder = os.path.join(folder, "results.json")
if os.path.exists(path_subfolder):
with open(path_subfolder, "r", encoding="utf-8") as f:
return json.load(f)

```
# Попытка из основного каталога
path_main = f"{folder}_results.json"
if os.path.exists(path_main):
    with open(path_main, "r", encoding="utf-8") as f:
        return json.load(f)

return None
```

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

```
    if not data:
        st.warning(f"No data found for {folder}. Make sure the JSON file exists.")
        continue

    # --- Cards with KPIs ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Unique Users", data.get("unique_users", "N/A"))
    with col2:
        st.metric("Unique Author Sets", data.get("unique_author_sets", "N/A"))
    with col3:
        st.metric("Most Popular Author", data.get("most_popular_author", "N/A"))

    # --- Best Buyer(s) ---
    st.subheader("Best Buyer(s)")
    st.write(data.get("best_buyer", "N/A"))

    # --- Total Revenue ---
    st.subheader("Total Revenue")
    df_rev = pd.DataFrame(data.get("daily_revenue", []))
    total_rev = df_rev["paid_price"].sum() if not df_rev.empty else 0
    st.metric("Total Revenue (USD)", f"${total_rev:,.2f}")

    # --- Top 5 days ---
    st.subheader("Top 5 Days by Revenue")
    top5 = pd.DataFrame({"date": data.get("top_5_days", [])})
    if not top5.empty:
        top5["date"] = pd.to_datetime(top5["date"])
        top5 = top5.sort_values("date", ascending=False)
        st.dataframe(top5.style.format({"date": lambda x: x.strftime("%Y-%m-%d")}))
    else:
        st.info("No top 5 days data available.")

    # --- Daily Revenue Chart ---
    st.subheader("Daily Revenue Chart")
    if not df_rev.empty:
        df_rev["date"] = pd.to_datetime(df_rev["date"])
        df_rev = df_rev.sort_values("date")

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df_rev["date"], df_rev["paid_price"], marker='o', linestyle='-', color='tab:blue')
        ax.set_ylabel("Revenue (USD)")
        ax.set_xlabel("Date")
        ax.set_title("Daily Revenue")
        ax.grid(True)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        fig.autofmt_xdate()
        st.pyplot(fig)
    else:
        st.info("No daily revenue data available for this dataset.")
```
