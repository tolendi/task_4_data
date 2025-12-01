import pandas as pd
import yaml
import re
from dateutil import parser
import matplotlib.pyplot as plt
import json
import warnings

warnings.filterwarnings('ignore')

EUR_TO_USD = 1.2

print("="*60)
print("Processing DATA1")
print("="*60)

# === 1. Load USERS ===
df_users = pd.read_csv(
    "users.csv",
    sep=",",
    quotechar='"',
    skipinitialspace=True
)

df_users.columns = ["id", "name", "address", "phone", "email"]
df_users["id"] = df_users["id"].astype(int)

# === 2. Load BOOKS (YAML) ===
with open("books.yaml", "r", encoding="utf-8") as f:
    books = yaml.safe_load(f)

df_books = pd.DataFrame(books)

# Rename columns to remove colons
column_mapping = {}
for col in df_books.columns:
    if col.startswith(':'):
        column_mapping[col] = col[1:]

df_books.rename(columns=column_mapping, inplace=True)

# Clean year column
if 'year' in df_books.columns:
    df_books["year"] = (
        df_books["year"]
        .astype(str)
        .str.strip()
        .replace(["", "None", "NULL", "-", ".", "o", "O", "\t"], pd.NA)
    )
    df_books["year"] = pd.to_numeric(df_books["year"], errors="coerce")

# Convert authors to tuple
df_books["author_tuple"] = df_books["author"].apply(
    lambda x: tuple(sorted(x.split(","))) if isinstance(x, str) else (str(x),)
)

# === 3. Load ORDERS (parquet) ===
df_orders = pd.read_parquet("orders.parquet")

# Clean unit_price
def clean_price(value):
    if pd.isna(value):
        return None
    v = str(value)
    v = re.sub(r"[^\d\.]", "", v)
    if v == "":
        return None
    return float(v)

df_orders["unit_price"] = df_orders["unit_price"].apply(clean_price)

# Clean timestamp
def clean_timestamp(value):
    if pd.isna(value) or value == "":
        return None
    value = str(value)
    if "," in value:
        parts = value.split(",")
        for p in parts:
            try:
                return pd.to_datetime(parser.parse(p.strip(), fuzzy=True))
            except:
                pass
    try:
        return pd.to_datetime(parser.parse(value, fuzzy=True))
    except:
        return None

df_orders["timestamp"] = df_orders["timestamp"].apply(clean_timestamp)

# Convert types
df_orders["id"] = df_orders["id"].astype(int)
df_orders["user_id"] = df_orders["user_id"].astype(int)
df_orders["book_id"] = df_orders["book_id"].astype(int)
df_orders["quantity"] = df_orders["quantity"].astype(int)
df_orders["unit_price"] = df_orders["unit_price"].astype(float) * EUR_TO_USD

# === 4. Add paid_price ===
df_orders["paid_price"] = df_orders["quantity"] * df_orders["unit_price"]

# === 5. Extract date parts ===
df_orders["date"] = df_orders["timestamp"].dt.date
df_orders["year"] = df_orders["timestamp"].dt.year
df_orders["month"] = df_orders["timestamp"].dt.month
df_orders["day"] = df_orders["timestamp"].dt.day

# === 6. Daily revenue ===
daily_revenue = df_orders.groupby("date")["paid_price"].sum().reset_index()
daily_revenue = daily_revenue.sort_values("paid_price", ascending=False)

top5_days = daily_revenue.head(5)
top5_days_formatted = [str(d) for d in top5_days["date"].tolist()]

print("\nTop 5 days by revenue:")
for i, row in top5_days.iterrows():
    print(f"  {row['date']}: ${row['paid_price']:,.2f}")

# === 7. Unique users reconciliation ===
def normalize_user(row):
    return {
        "name": str(row["name"]).strip().lower() if pd.notna(row["name"]) else "",
        "address": str(row["address"]).strip().lower() if pd.notna(row["address"]) else "",
        "phone": str(row["phone"]).strip().lower() if pd.notna(row["phone"]) else "",
        "email": str(row["email"]).strip().lower() if pd.notna(row["email"]) else "",
    }

df_users["norm"] = df_users.apply(normalize_user, axis=1)

# Build user groups
groups = []
used = set()

for i in df_users.index:
    if i in used:
        continue
    base = df_users.loc[i, "norm"]
    group = [int(df_users.loc[i, "id"])]
    used.add(i)
    
    for j in df_users.index:
        if j in used:
            continue
        compare = df_users.loc[j, "norm"]
        
        matches = sum(
            base[k] == compare[k] and base[k] != "" 
            for k in base.keys()
        )
        if matches >= 1:
            group.append(int(df_users.loc[j, "id"]))
            used.add(j)
    
    groups.append(group)

unique_users_count = len(groups)
print(f"\nUnique real users: {unique_users_count}")

# === 8. Unique sets of authors ===
unique_author_sets = df_books["author_tuple"].nunique()
print(f"Unique author sets: {unique_author_sets}")

# === 9. Most popular author (by sold quantity) ===
df_orders_books = df_orders.merge(df_books, left_on="book_id", right_on="id", suffixes=('', '_book'))

sales_by_author = df_orders_books.groupby("author_tuple")["quantity"].sum().sort_values(ascending=False)

top_author_tuple = sales_by_author.index[0]
top_author_display = ", ".join(top_author_tuple)
print(f"Most popular author(s): {top_author_display}")

# === 10. Top customer by total spending ===
user_spending = df_orders.groupby("user_id")["paid_price"].sum().reset_index()
top_customer_id = int(user_spending.sort_values("paid_price", ascending=False).iloc[0]["user_id"])

top_group = next((g for g in groups if top_customer_id in g), [top_customer_id])
top_group = sorted(top_group)
print(f"Best buyer (all IDs): {top_group}")

# === 11. Plot daily revenue ===
plt.figure(figsize=(12, 5))
daily_revenue_sorted = daily_revenue.sort_values("date")
plt.plot(daily_revenue_sorted["date"], daily_revenue_sorted["paid_price"], linewidth=2, color='#667eea')
plt.title("Daily Revenue - DATA1", fontsize=14, fontweight='bold')
plt.xlabel("Date", fontsize=12)
plt.ylabel("Revenue (USD)", fontsize=12)
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("revenue_chart.png", dpi=150, bbox_inches='tight')
print("\nChart saved: revenue_chart.png")
plt.show()

# Prepare results
daily_revenue_list = []
for _, row in daily_revenue_sorted.iterrows():
    daily_revenue_list.append({
        "date": str(row["date"]),
        "paid_price": float(row["paid_price"])
    })

results = {
    "top_5_days": top5_days_formatted,
    "unique_users": unique_users_count,
    "unique_author_sets": unique_author_sets,
    "most_popular_author": top_author_display,
    "best_buyer": top_group,
    "daily_revenue": daily_revenue_list
}

# Save results
with open("results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("Results saved: results.json")
print("="*60)
print("Processing complete!")
print("="*60)