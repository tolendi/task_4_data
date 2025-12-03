import pandas as pd
import yaml
import re
from dateutil import parser
import matplotlib.pyplot as plt
import json
import warnings
import datetime as dt

warnings.filterwarnings("ignore")

EUR_TO_USD = 1.2

print("="*60)
print("Processing DATA2")
print("="*60)

# ============================================================
# 1. LOAD USERS
# ============================================================
df_users = pd.read_csv(
    "DATA2/users.csv",
    sep=",",
    quotechar='"',
    skipinitialspace=True
)

df_users.columns = ["id", "name", "address", "phone", "email"]
df_users["id"] = df_users["id"].astype(int)

# ============================================================
# 2. LOAD BOOKS (YAML)
# ============================================================
with open("DATA2/books.yaml", "r", encoding="utf-8") as f:
    books = yaml.safe_load(f)

df_books = pd.DataFrame(books)

# Remove leading ":" in column names
df_books.rename(columns={c: c.lstrip(":") for c in df_books.columns}, inplace=True)

# Clean "year"
if "year" in df_books.columns:
    df_books["year"] = (
        df_books["year"]
        .astype(str)
        .str.strip()
        .replace(["", "None", "NULL", "-", ".", "o", "O", "\t"], pd.NA)
    )
    df_books["year"] = pd.to_numeric(df_books["year"], errors="coerce")

# Normalize authors
df_books["author_tuple"] = df_books["author"].apply(
    lambda x: tuple(sorted(x.split(","))) if isinstance(x, str) else (str(x),)
)

# ============================================================
# 3. LOAD ORDERS
# ============================================================
df_orders = pd.read_parquet("DATA2/orders.parquet")

# --------------------
# Clean unit_price
# --------------------
def clean_price(v):
    if pd.isna(v):
        return None

    v = str(v).strip()

    # € Format: 1.234,56 or 12.000,00
    if re.match(r"^\d{1,3}(\.\d{3})*,\d{2}$", v):
        v = v.replace(".", "").replace(",", ".")
        return float(v)

    # 12.000 → should be 12.0
    if re.match(r"^\d+\.\d{3}$", v):
        v = v.replace(".", "")
        return float(v)

    # 9,99 → convert
    if re.match(r"^\d+,\d+$", v):
        return float(v.replace(",", "."))

    # Normal clean
    v = re.sub(r"[^\d\.]", "", v)
    return float(v) if v else None


df_orders["unit_price"] = df_orders["unit_price"].apply(clean_price)

# --------------------
# Clean timestamp
# --------------------
def clean_timestamp_strict(value):
    # 1. Пустое → повреждённое, сразу None
    if pd.isna(value) or str(value).strip() == "":
        return None

    # 2. Превращаем в строку
    v = str(value)

    # 3. Запоминаем сегодняшнюю дату
    # чтобы обнаруживать случаи auto-fill = today
    today = dt.date.today()

    try:
        # 4. Пробуем распарсить строку
        ts = parser.parse(v, fuzzy=True)

        # 5. Ловим момент когда парсер сам подставил сегодня
        if ts.date() == today:
            # → это повреждённый timestamp
            return None

        # 6. Если дата валидная → возвращаем её
        return ts

    except:
        # 7. Любая ошибка = повреждённая дата → None
        return None


df_orders["timestamp_clean"] = df_orders["timestamp"].apply(clean_timestamp_strict)


# --------------------
# Remove bad timestamps completely (A)
# --------------------
df_orders = df_orders[df_orders["timestamp_clean"].notna()].copy()

# Replace original timestamp
df_orders["timestamp"] = df_orders["timestamp_clean"]
df_orders.drop(columns=["timestamp_clean"], inplace=True)

# Convert types
df_orders["id"] = df_orders["id"].astype(int)
df_orders["user_id"] = df_orders["user_id"].astype(int)
df_orders["book_id"] = df_orders["book_id"].astype(int)
df_orders["quantity"] = df_orders["quantity"].astype(int)
df_orders["unit_price"] = df_orders["unit_price"].astype(float) * EUR_TO_USD

# ============================================================
# 4. paid_price
# ============================================================
df_orders["paid_price"] = df_orders["quantity"] * df_orders["unit_price"]

# ============================================================
# 5. DATE PARTS
# ============================================================
df_orders["date"] = df_orders["timestamp"].dt.date
df_orders["year"] = df_orders["timestamp"].dt.year
df_orders["month"] = df_orders["timestamp"].dt.month
df_orders["day"] = df_orders["timestamp"].dt.day

# ============================================================
# 6. DAILY REVENUE
# ============================================================
daily_revenue = (
    df_orders.groupby("date")["paid_price"]
    .sum()
    .reset_index()
    .sort_values("paid_price", ascending=False)
)

top5_days = daily_revenue.head(5)
top5_days_formatted = [str(d) for d in top5_days["date"]]

print("\nTop 5 days by revenue:")
for _, row in top5_days.iterrows():
    print(f"  {row['date']}: ${row['paid_price']:,.2f}")

# ============================================================
# 7. USER RECONCILIATION
# ============================================================
def normalize_user(row):
    return {
        "name": str(row["name"]).strip().lower() if pd.notna(row["name"]) else "",
        "address": str(row["address"]).strip().lower() if pd.notna(row["address"]) else "",
        "phone": str(row["phone"]).strip().lower() if pd.notna(row["phone"]) else "",
        "email": str(row["email"]).strip().lower() if pd.notna(row["email"]) else "",
    }

df_users["norm"] = df_users.apply(normalize_user, axis=1)

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

        comp = df_users.loc[j, "norm"]
        matches = sum(base[k] == comp[k] and base[k] != "" for k in base)

        if matches >= 1:
            group.append(int(df_users.loc[j, "id"]))
            used.add(j)

    groups.append(group)

unique_users_count = len(groups)
print(f"\nUnique real users: {unique_users_count}")

# ============================================================
# 8. UNIQUE AUTHOR SETS
# ============================================================
unique_author_sets = df_books["author_tuple"].nunique()
print(f"Unique author sets: {unique_author_sets}")

# ============================================================
# 9. MOST POPULAR AUTHOR
# ============================================================
df_orders_books = df_orders.merge(df_books, left_on="book_id", right_on="id")

sales_by_author = (
    df_orders_books.groupby("author_tuple")["quantity"]
    .sum()
    .sort_values(ascending=False)
)

top_author_tuple = sales_by_author.index[0]
top_author_display = ", ".join(top_author_tuple)

print(f"Most popular author: {top_author_display}")

# ============================================================
# 10. BEST BUYER
# ============================================================
user_spending = df_orders.groupby("user_id")["paid_price"].sum().reset_index()
top_customer_id = int(user_spending.sort_values("paid_price", ascending=False).iloc[0]["user_id"])

top_group = next((g for g in groups if top_customer_id in g), [top_customer_id])
top_group = sorted(top_group)

print(f"Best buyer IDs: {top_group}")

# ============================================================
# 11. PLOT REVENUE
# ============================================================
daily_sorted = daily_revenue.sort_values("date")

plt.figure(figsize=(12, 5))
plt.plot(daily_sorted["date"], daily_sorted["paid_price"], linewidth=2, color="#667eea")
plt.title("Daily Revenue — DATA1", fontsize=14, fontweight="bold")
plt.xlabel("Date")
plt.ylabel("Revenue (USD)")
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("revenue_chart.png", dpi=150)
plt.show()

print("\nChart saved: revenue_chart.png")

# ============================================================
# SAVE RESULTS
# ============================================================
daily_list = [
    {"date": str(row["date"]), "paid_price": float(row["paid_price"])}
    for _, row in daily_sorted.iterrows()
]

results = {
    "top_5_days": top5_days_formatted,
    "unique_users": unique_users_count,
    "unique_author_sets": unique_author_sets,
    "most_popular_author": top_author_display,
    "best_buyer": top_group,
    "daily_revenue": daily_list,
}

with open("results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("Results saved: results.json")
print("="*60)
print("Processing complete!")
print("="*60)
