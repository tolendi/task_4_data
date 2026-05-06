# 📊 Task 4 — Data Cleaning & Analytics Dashboard

## 📌 Overview

This project processes transactional and book-related datasets (`DATA1`, `DATA2`, `DATA3`) using pandas, performs data cleaning, feature engineering, and analytical aggregation. The results are visualized in a simple BI-style dashboard.

---

## ⚙️ Tech Stack

* Python (pandas, matplotlib)
* Data cleaning & transformation
* Basic data visualization

---

## 🧹 Data Processing

For each dataset folder:

* Load raw data into pandas
* Clean missing, duplicated, and malformed values
* Ensure correct data types (dates, numeric fields)
* Normalize inconsistent user records (name, phone, address, aliases)

---

## 💰 Feature Engineering

* `paid_price = quantity * unit_price`
* Currency conversion applied: **€1 = $1.2**
* Extracted from timestamp:

  * year
  * month
  * day

---

## 📈 Analytics Tasks

### 1. Revenue Analysis

* Compute daily revenue (group by date)
* Identify top 5 revenue days

### 2. Unique Users

* Reconcile user identities across:

  * name
  * phone
  * email
  * address
  * aliases
* Estimate true number of unique users

### 3. Author Analysis

* Identify unique author sets
* Count number of distinct author combinations
* Find most popular author (by books sold)

### 4. Customer Analysis

* Identify top customer by total spending
* Return all associated user IDs (aliases included)

---

## 📊 Visualization

* Daily revenue line chart created using matplotlib
* Displayed in dashboard view

---

## 📊 Dashboard

A simple BI-style dashboard includes:

* Top 5 revenue days (formatted YYYY-MM-DD)
* Number of unique users
* Number of author sets
* Most popular author(s)
* Best buyer (list of user IDs)
* Daily revenue chart

Built as a lightweight web-based/static dashboard with multiple views.

---

## 📁 Dataset Scope

The same pipeline is applied independently to:

* `DATA1`
* `DATA2`
* `DATA3`

---

## 📬 Submission

* GitHub repository with full code
* Online dashboard (browser-accessible)
* Sent to: [p.lebedev@itransition.com](mailto:p.lebedev@itransition.com)

---
