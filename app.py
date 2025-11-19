import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit as st
import pandas as pd
import os

# ---------------------------
#  OPTION 1 — Upload CSV Files
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

    required_files = {
        "distribution_centers.csv": None,
        "user.csv": None,
        "product.csv": None,
        "inventory_item.csv": None,
        "order.csv": None,
        "order_item.csv": None,
        "event.csv": None,
    }

    # map file names
    for f in uploaded_files:
        name = f.name.lower()
        if name in required_files:
            required_files[name] = pd.read_csv(f)

    # check missing
    missing = [k for k,v in required_files.items() if v is None]
    if missing:
        st.sidebar.error(f"Missing files: {', '.join(missing)}")
        return None

    return required_files


# ---------------------------
#  OPTION 2 — Load from data/ folder
# ---------------------------
def load_from_folder(path="data"):

    st.sidebar.write(f"Looking for CSV inside: `{path}`")

    def safe_read(file):
        fp = f"{path}/{file}"
        if not os.path.exists(fp):
            st.error(f"❌ File not found: {fp}")
            return None
        return pd.read_csv(fp)

    return {
        "distribution_centers.csv": safe_read("distribution_centers.csv"),
        "user.csv": safe_read("user.csv"),
        "product.csv": safe_read("product.csv"),
        "inventory_item.csv": safe_read("inventory_item.csv"),
        "order.csv": safe_read("order.csv"),
        "order_item.csv": safe_read("order_item.csv"),
        "event.csv": safe_read("event.csv")
    }


# ---------------------------
#  SIDEBAR — Pick Load Method
# ---------------------------
st.sidebar.title("Data Source")
mode = st.sidebar.radio("Load data from:", ["Upload CSV", "GitHub folder /data"])

if mode == "Upload CSV":
    data = load_from_upload()
else:
    data = load_from_folder("data")

# Stop app if data missing
if data is None or any(v is None for v in data.values()):
    st.warning("Please upload CSV files or check /data folder structure")
    st.stop()

# Assign variables like before
df_dc       = data["distribution_centers.csv"]
df_user     = data["user.csv"]
df_product  = data["product.csv"]
df_inventory= data["inventory_item.csv"]
df_order    = data["order.csv"]
df_order_item = data["order_item.csv"]
df_event    = data["event.csv"]

from etl import load_data, merge_data
from features import build_features
from models import build_churn_model

st.set_page_config(page_title="Ecommerce Enterprise Dashboard", layout="wide")

st.title("📊 Ecommerce Enterprise Analytics Dashboard")

# Load CSV
data = load_data("data")

# Merge
df = merge_data(data)

# Feature engineering
df_feat, rfm, demand = build_features(df)

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
