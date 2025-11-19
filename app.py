import streamlit as st
import pandas as pd
import plotly.express as px

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
