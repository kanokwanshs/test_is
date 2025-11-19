import streamlit as st
import pandas as pd
import plotly.express as px
import os

from etl import merge_data
from features import build_features
from models import build_churn_model

# ---------------------------
# OPTION 1 — Upload CSV Files
# ---------------------------
def load_from_upload():
    st.sidebar.subheader("📁 Upload CSV Files")

    uploaded_files = st.sidebar.file_uploader(
        "Upload all 7 CSV files",
        accept_multiple_files=True,
        type=["csv"]
    )

    if not uploaded_files:
        return None

    required = {
        "distribution_centers.csv": "dc",
        "user.csv": "user",
        "product.csv": "product",
        "inventory_item.csv": "inventory_item",
        "order.csv": "order",
        "order_item.csv": "order_item",
        "event.csv": "event",
    }

    data = {v: None for v in required.values()}

    for f in uploaded_files:
        name = f.name.lower()
        if name in required:
            key = required[name]
            data[key] = pd.read_csv(f)

    missing = [k for k, v in data.items() if v is None]
    if missing:
        st.sidebar.error(f"Missing files: {', '.join(missing)}")
        return None

    return data


# ---------------------------
# OPTION 2 — Load from folder
# ---------------------------
def load_from_folder(path="data"):

    required = {
        "distribution_centers.csv": "dc",
        "user.csv": "user",
        "product.csv": "product",
        "inventory_item.csv": "inventory_item",
        "order.csv": "order",
        "order_item.csv": "order_item",
        "event.csv": "event",
    }

    data = {}

    for file, key in required.items():
        fp = f"{path}/{file}"
        if not os.path.exists(fp):
            st.error(f"❌ File not found: {fp}")
            data[key] = None
        else:
            data[key] = pd.read_csv(fp)

    return data


# ---------------------------
# UI LOAD
# ---------------------------
st.sidebar.title("Data Source")
mode = st.sidebar.radio("Load data from:", ["Upload CSV", "GitHub folder /data"])

data = load_from_upload() if mode == "Upload CSV" else load_from_folder("data")

if data is None or any(v is None for v in data.values()):
    st.warning("Please upload CSV files or check /data folder structure")
    st.stop()

# ---------------------------
# MERGE NORMALIZED DATA
# ---------------------------
df = merge_data(data)

# ---------------------------
# FEATURES
# ---------------------------
df_feat, rfm, demand = build_features(df)

st.set_page_config(page_title="Ecommerce Enterprise Dashboard", layout="wide")

st.title("📊 Ecommerce Enterprise Analytics Dashboard")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📦 Sales & CRM",
    "📈 Inventory Forecast",
    "💰 Accounting & Profit",
    "🎯 Marketing Analytics"
])

# ======================
# CRM & Sales
# ======================
with tab1:
    st.subheader("Customer RFM Segmentation")
    fig1 = px.scatter(rfm, x="frequency", y="monetary", size="recency", color="recency")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Churn Prediction Model")
    model, report = build_churn_model(rfm)
    st.json(report)


# ======================
# Inventory
# ======================
with tab2:
    st.subheader("Monthly Product Demand")
    fig2 = px.line(demand, x="month", y="demand", color="product_id")
    st.plotly_chart(fig2, use_container_width=True)


# ======================
# Accounting
# ======================
with tab3:
    st.subheader("Revenue")
    rev = df_feat.groupby("order_date")["total_revenue"].sum().reset_index()
    fig3 = px.line(rev, x="order_date", y="total_revenue")
    st.plotly_chart(fig3, use_container_width=True)


# ======================
# Marketing
# ======================
with tab4:
    st.subheader("Channel Performance")
    ch = df_feat.groupby("channel")["sale_price"].sum().reset_index()
    fig4 = px.bar(ch, x="channel", y="sale_price")
    st.plotly_chart(fig4, use_container_width=True)
