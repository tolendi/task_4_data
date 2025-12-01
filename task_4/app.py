import streamlit as st
import json
import os

st.title("Test Dashboard")

folders = ["DATA1", "DATA2", "DATA3"]

for folder in folders:
    st.header(folder)
    path = f"{folder}_results.json"
    st.write("Path exists?", os.path.exists(path))
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        st.write(data)
