# app.py - Enhanced E-commerce Analytics Dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
import zipfile

warnings.filterwarnings('ignore')

# Page config
st.set_page_config(page_title="E-commerce Analytics Pro", layout="wide", page_icon="📊")

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'data' not in st.session_state:
    st.session_state.data = None

def get_channel_type(channel):
    """Map channel to Online/Offline"""
    online_channels = ['line shopping', 'lazada', 'shopee', 'tiktok']
    offline_channels = ['siam center']
    channel_lower = str(channel).lower()
    for oc in online_channels:
        if oc in channel_lower:
            return 'Online'
    for of in offline_channels:
        if of in channel_lower:
            return 'Offline'
    return 'Other'

def upload_data():
    """Flexible data upload - ZIP file or folder path"""
    st.sidebar.title("📊 E-commerce Analytics Pro")
    st.sidebar.markdown("---")
    
    upload_method = st.sidebar.radio(
        "📁 Data Source",
        ["Upload ZIP File", "Load from Folder Path"]
    )
    
    data = None
    
    if upload_method == "Upload ZIP File":
        st.sidebar.subheader("Upload ZIP containing CSV files")
        st.sidebar.caption("ZIP should contain: user.csv, product.csv, order.csv, order_item.csv")
        uploaded_zip = st.sidebar.file_uploader("Choose ZIP file", type=['zip'])
        
        if uploaded_zip is not None:
            if st.sidebar.button("🔄 Load Data", type="primary"):
                try:
                    with zipfile.ZipFile(uploaded_zip) as z:
                        data = {}
                        file_mapping = {
                            "distribution_centers.csv": "dc",
                            "user.csv": "user",
                            "product.csv": "product",
                            "inventory_item.csv": "inventory",
                            "order.csv": "order",
                            "order_item.csv": "order_item",
                            "event.csv": "event"
                        }
                        
                        for filename in z.namelist():
                            base_name = filename.split('/')[-1]
                            if base_name in file_mapping:
                                key = file_mapping[base_name]
                                with z.open(filename) as f:
                                    data[key] = pd.read_csv(f)
                                st.sidebar.success(f"✅ {base_name}")
                        
                        required = ['user', 'product', 'order', 'order_item']
                        missing = [r for r in required if r not in data]
                        if missing:
                            st.sidebar.error(f"❌ Missing: {', '.join(missing)}")
                            return None
                        
                        st.session_state.data = data
                        st.session_state.data_loaded = True
                        st.sidebar.success("✅ All data loaded!")
                        return data
                except Exception as e:
                    st.sidebar.error(f"❌ Error: {str(e)}")
                    return None
    else:
        data_path = st.sidebar.text_input("Folder path", value="data")
        if st.sidebar.button("🔄 Load Data", type="primary"):
            try:
                import os
                data = {}
                file_mapping = {
                            "distribution_centers.csv": "dc",
                            "users.csv": "user",
                            "products.csv": "product",
                            "inventory_items.csv": "inventory",
                            "orders.csv": "order",
                            "order_items.csv": "order_item",
                            "events.csv": "event",
                            "sales_representatives.csv": "sales_rep",
                            "leads.csv": "lead",
                            "marketing_campaigns.csv": "campaign"
                  }
                
                for filename, key in file_mapping.items():
                    filepath = os.path.join(data_path, filename)
                    if os.path.exists(filepath):
                        data[key] = pd.read_csv(filepath)
                        st.sidebar.success(f"✅ {filename}")
                
                required = ['user', 'product', 'order', 'order_item']
                missing = [r for r in required if r not in data]
                if missing:
                    st.sidebar.error(f"❌ Missing: {', '.join(missing)}")
                    return None
                
                st.session_state.data = data
                st.session_state.data_loaded = True
                st.sidebar.success("✅ All data loaded!")
                return data
            except Exception as e:
                st.sidebar.error(f"❌ Error: {str(e)}")
                return None
    
    return st.session_state.data if st.session_state.data_loaded else None

@st.cache_data
def merge_and_preprocess(data):
    """Merge all tables and create master dataframe"""
    # Helper function to get available columns
    def get_available_cols(df, desired_cols):
        return [col for col in desired_cols if col in df.columns]
    
    # Start with order_item
    df = data['order_item'].copy()
    
    # Merge order table
    order_cols = ['order_id', 'channel', 'discount_pct', 'status', 'num_of_item', 'created_at']
    available_order_cols = get_available_cols(data['order'], order_cols)
    if 'order_id' in available_order_cols:
        df = df.merge(
            data['order'][available_order_cols],
            on='order_id', how='left', suffixes=('', '_order')
        )
    
    # Merge product table
    product_cols = ['product_id', 'product_category', 'product_collection', 'retail_price', 'product_name']
    available_product_cols = get_available_cols(data['product'], product_cols)
    if 'product_id' in available_product_cols:
        df = df.merge(
            data['product'][available_product_cols],
            on='product_id', how='left', suffixes=('', '_prod')
        )
    
    # Merge user table
    user_cols = ['user_id', 'city', 'traffic_source', 'age', 'gender']
    available_user_cols = get_available_cols(data['user'], user_cols)
    if 'user_id' in available_user_cols:
        df = df.merge(
            data['user'][available_user_cols],
            on='user_id', how='left'
        )
    
    # Add missing columns with default values
    if 'channel' not in df.columns:
        df['channel'] = 'Unknown'
    if 'discount_pct' not in df.columns:
        df['discount_pct'] = 0.0
    if 'status' not in df.columns:
        df['status'] = 'Complete'
    if 'traffic_source' not in df.columns:
        df['traffic_source'] = 'Unknown'
    if 'product_category' not in df.columns:
        df['product_category'] = 'Uncategorized'
    if 'product_name' not in df.columns:
        df['product_name'] = 'Unknown Product'
    if 'cost' not in df.columns:
        # Estimate cost as 60% of sale price if not available
        if 'sale_price' in df.columns:
            df['cost'] = df['sale_price'] * 0.6
        else:
            df['cost'] = 0
    if 'sale_price' not in df.columns:
        df['sale_price'] = 0
    
    # Date conversions
    for col in ['created_at', 'shipped_at', 'delivered_at', 'returned_at']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # If created_at doesn't exist, try to find any date column
    if 'created_at' not in df.columns:
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if date_cols:
            df['created_at'] = pd.to_datetime(df[date_cols[0]], errors='coerce')
        else:
            df['created_at'] = pd.Timestamp.now()
    
    # Derived fields
    df['profit'] = df['sale_price'] - df['cost']
    df['order_date'] = df['created_at'].dt.date
    df['order_month'] = df['created_at'].dt.to_period('M')
    df['order_year'] = df['created_at'].dt.year
    df['order_quarter'] = df['created_at'].dt.quarter
    df['order_hour'] = df['created_at'].dt.hour
    df['order_dayofweek'] = df['created_at'].dt.dayofweek
    df['channel_type'] = df['channel'].apply(get_channel_type)
    
    return df, data

# ==========================================
# SIDEBAR - Data Upload
# ==========================================
data = upload_data()

if data is None or not st.session_state.data_loaded:
    st.title("📊 E-commerce Analytics Dashboard Pro")
    st.info("👈 Please load your data in the sidebar to begin analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### 📦 Option 1: Upload ZIP File
        - Create a ZIP file containing your CSV files
        - Upload it directly through the web interface
        - Quick and easy!
        """)
    with col2:
        st.markdown("""
        ### 📁 Option 2: Load from Folder
        - Place CSV files in a folder (e.g., 'data/')
        - Specify the folder path
        - Great for local development
        """)
    
    st.markdown("""
    ---
    ### Required Files:
    - ✅ **user.csv** - User information
    - ✅ **product.csv** - Product catalog
    - ✅ **order.csv** - Order details
    - ✅ **order_item.csv** - Order line items
    
    ### Optional Files:
    - distribution_centers.csv
    - inventory_item.csv
    - event.csv
    """)
    st.stop()

# Process data
df_master, data_dict = merge_and_preprocess(data)

st.sidebar.markdown("---")
st.sidebar.success(f"✅ {len(df_master):,} transactions")
st.sidebar.metric("Total Revenue", f"฿{df_master['sale_price'].sum():,.0f}")
st.sidebar.metric("Total Profit", f"฿{df_master['profit'].sum():,.0f}")

# ==========================================
# MAIN TABS
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive Dashboard",
    "💼 Sales Analytics", 
    "📢 Marketing Analytics",
    "💰 Financial Analytics",
    "📦 Warehouse & Inventory"
])

# ==========================================
# TAB 1: EXECUTIVE DASHBOARD
# ==========================================
with tab1:
    st.header("📊 Executive Dashboard")
    
    # Date Range Filter
    col1, col2 = st.columns([3, 1])
    with col1:
        min_date = df_master['created_at'].min().date()
        max_date = df_master['created_at'].max().date()
        date_range = st.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    
    with col2:
        if len(date_range) == 2:
            df_filtered = df_master[
                (df_master['created_at'].dt.date >= date_range[0]) & 
                (df_master['created_at'].dt.date <= date_range[1])
            ]
        else:
            df_filtered = df_master
        
        st.metric("Transactions", f"{len(df_filtered):,}")
    
    # KPI Cards
    st.subheader("🎯 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = df_filtered['sale_price'].sum()
        st.metric("Total Revenue", f"฿{total_revenue:,.0f}")
    
    with col2:
        total_profit = df_filtered['profit'].sum()
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        st.metric("Total Profit", f"฿{total_profit:,.0f}", 
                 delta=f"{profit_margin:.1f}% margin")
    
    with col3:
        unique_customers = df_filtered['user_id'].nunique()
        st.metric("Active Customers", f"{unique_customers:,}")
    
    with col4:
        avg_order_value = df_filtered['sale_price'].mean()
        st.metric("Avg Order Value", f"฿{avg_order_value:,.2f}")
    
    # Sales Trend
    st.subheader("📈 Sales Trend Overview")
    daily_sales = df_filtered.groupby('order_date').agg({
        'sale_price': 'sum',
        'profit': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    daily_sales['order_date'] = pd.to_datetime(daily_sales['order_date'])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_sales['order_date'], 
        y=daily_sales['sale_price'],
        name='Revenue',
        line=dict(color='#3498db', width=2),
        fill='tozeroy'
    ))
    fig.add_trace(go.Scatter(
        x=daily_sales['order_date'], 
        y=daily_sales['profit'],
        name='Profit',
        line=dict(color='#2ecc71', width=2),
        yaxis='y2'
    ))
    fig.update_layout(
        title="Daily Revenue & Profit Trend",
        xaxis_title="Date",
        yaxis_title="Revenue (฿)",
        yaxis2=dict(title="Profit (฿)", overlaying='y', side='right'),
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Quick Stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🏆 Top Performing Category")
        cat_revenue = df_filtered.groupby('product_category')['sale_price'].sum().sort_values(ascending=False)
        if len(cat_revenue) > 0:
            top_cat = cat_revenue.index[0]
            top_cat_rev = cat_revenue.values[0]
            st.metric(top_cat, f"฿{top_cat_rev:,.0f}")
    
    with col2:
        st.subheader("📱 Best Channel")
        channel_revenue = df_filtered.groupby('channel_type')['sale_price'].sum().sort_values(ascending=False)
        if len(channel_revenue) > 0:
            best_channel = channel_revenue.index[0]
            best_channel_rev = channel_revenue.values[0]
            st.metric(best_channel, f"฿{best_channel_rev:,.0f}")
    
    with col3:
        st.subheader("🎯 Conversion Insights")
        total_users = df_filtered['user_id'].nunique()
        total_orders = df_filtered['order_id'].nunique()
        conversion = (total_orders / total_users) if total_users > 0 else 0
        st.metric("Orders per Customer", f"{conversion:.2f}")

# ==========================================
# TAB 2: SALES ANALYTICS
# ==========================================
with tab2:
    st.header("💼 Sales Analytics")
    
    # Date filter for this tab
    df_sales = df_filtered.copy()
    
    st.subheader("1️⃣ Common Sales KPIs")
    
    # Calculate monthly growth
    monthly_sales = df_sales.groupby('order_month').agg({
        'sale_price': 'sum',
        'profit': 'sum'
    }).reset_index()
    monthly_sales['order_month'] = monthly_sales['order_month'].dt.to_timestamp()
    monthly_sales = monthly_sales.sort_values('order_month')
    
    if len(monthly_sales) >= 2:
        current_month_sales = monthly_sales.iloc[-1]['sale_price']
        previous_month_sales = monthly_sales.iloc[-2]['sale_price']
        monthly_growth = ((current_month_sales - previous_month_sales) / previous_month_sales * 100) if previous_month_sales > 0 else 0
    else:
        monthly_growth = 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Monthly Sales Growth", f"{monthly_growth:+.2f}%")
    
    with col2:
        total_revenue = df_sales['sale_price'].sum()
        total_profit = df_sales['profit'].sum()
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        st.metric("Average Profit Margin", f"{profit_margin:.2f}%")
    
    with col3:
        # Sales target attainment (assuming a target)
        monthly_target = 1000000  # Example target
        current_sales = df_sales[df_sales['order_month'] == df_sales['order_month'].max()]['sale_price'].sum()
        target_attainment = (current_sales / monthly_target * 100) if monthly_target > 0 else 0
        st.metric("Sales Target Attainment", f"{target_attainment:.1f}%")
    
    with col4:
        avg_purchase = df_sales['sale_price'].mean()
        st.metric("Average Purchase Value", f"฿{avg_purchase:,.2f}")
    
    # Sales by Channel
    st.subheader("2️⃣ Sales by Contact Method (Channel)")
    
    channel_sales = df_sales.groupby('channel').agg({
        'sale_price': 'sum',
        'order_id': 'nunique',
        'user_id': 'nunique'
    }).reset_index()
    channel_sales.columns = ['Channel', 'Revenue', 'Orders', 'Customers']
    channel_sales['Revenue %'] = (channel_sales['Revenue'] / channel_sales['Revenue'].sum() * 100).round(2)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(channel_sales, 
                     values='Revenue', 
                     names='Channel',
                     title="Revenue Distribution by Channel",
                     hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(channel_sales.sort_values('Revenue', ascending=True),
                     x='Revenue',
                     y='Channel',
                     orientation='h',
                     title="Revenue by Channel",
                     text='Revenue %')
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(channel_sales, use_container_width=True)
    
    # Customer Acquisition & Retention
    st.subheader("3️⃣ Customer Acquisition & Retention Metrics")
    
    # Customer Acquisition Cost (simplified)
    total_marketing_cost = df_sales['discount_pct'].sum() * df_sales['sale_price'].sum()
    new_customers = df_sales['user_id'].nunique()
    cac = total_marketing_cost / new_customers if new_customers > 0 else 0
    
    # Retention and Churn
    analysis_date = df_sales['created_at'].max()
    customer_last_purchase = df_sales.groupby('user_id')['created_at'].max()
    days_since_purchase = (analysis_date - customer_last_purchase).dt.days
    
    churned_customers = (days_since_purchase > 60).sum()
    total_customers = len(customer_last_purchase)
    churn_rate = (churned_customers / total_customers * 100) if total_customers > 0 else 0
    retention_rate = 100 - churn_rate
    
    # Customer Lifetime Value
    avg_revenue_per_customer = df_sales.groupby('user_id')['sale_price'].sum().mean()
    gross_margin_pct = profit_margin / 100
    customer_lifetime_value = gross_margin_pct * (retention_rate/100) * avg_revenue_per_customer
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Customer Acquisition Cost", f"฿{cac:,.2f}")
    
    with col2:
        st.metric("Retention Rate", f"{retention_rate:.2f}%")
    
    with col3:
        st.metric("Churn Rate", f"{churn_rate:.2f}%")
    
    with col4:
        st.metric("Customer Lifetime Value", f"฿{customer_lifetime_value:,.2f}")
    
    # Product Performance
    st.subheader("4️⃣ Product Performance")
    
    product_perf = df_sales.groupby(['product_id', 'product_name', 'product_category']).agg({
        'sale_price': 'sum',
        'profit': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    product_perf.columns = ['Product ID', 'Product Name', 'Category', 'Revenue', 'Profit', 'Orders']
    product_perf['Profit Margin %'] = (product_perf['Profit'] / product_perf['Revenue'] * 100).round(2)
    product_perf = product_perf.sort_values('Revenue', ascending=False).head(20)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(product_perf.head(10),
                     x='Revenue',
                     y='Product Name',
                     orientation='h',
                     title="Top 10 Products by Revenue",
                     color='Profit Margin %',
                     color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(product_perf,
                        x='Revenue',
                        y='Profit',
                        size='Orders',
                        color='Category',
                        hover_data=['Product Name'],
                        title="Product Performance: Revenue vs Profit")
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(product_perf, use_container_width=True, height=400)

# ==========================================
# TAB 3: MARKETING ANALYTICS
# ==========================================
with tab3:
    st.header("📢 Marketing Analytics")
    
    df_marketing = df_filtered.copy()
    
    st.subheader("1️⃣ Campaign Effectiveness (Discount Analysis)")
    
    campaign_df = df_marketing[df_marketing['discount_pct'] > 0].copy()
    non_campaign_df = df_marketing[df_marketing['discount_pct'] == 0].copy()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        campaign_revenue = campaign_df['sale_price'].sum()
        total_revenue = df_marketing['sale_price'].sum()
        campaign_share = (campaign_revenue / total_revenue * 100) if total_revenue > 0 else 0
        st.metric("Campaign Revenue Share", f"{campaign_share:.1f}%")
    
    with col2:
        campaign_orders = len(campaign_df)
        total_orders = len(df_marketing)
        conversion_rate = (campaign_orders / total_orders * 100) if total_orders > 0 else 0
        st.metric("Campaign Conversion Rate", f"{conversion_rate:.1f}%")
    
    with col3:
        avg_discount = campaign_df['discount_pct'].mean() * 100 if len(campaign_df) > 0 else 0
        st.metric("Average Discount Rate", f"{avg_discount:.1f}%")
    
    with col4:
        campaign_cac = (campaign_df['discount_pct'] * campaign_df['sale_price']).sum() / campaign_df['user_id'].nunique() if len(campaign_df) > 0 else 0
        st.metric("Campaign CAC", f"฿{campaign_cac:,.2f}")
    
    # ROI Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        campaign_aov = campaign_df['sale_price'].mean() if len(campaign_df) > 0 else 0
        non_campaign_aov = non_campaign_df['sale_price'].mean() if len(non_campaign_df) > 0 else 0
        
        comparison = pd.DataFrame({
            'Type': ['With Campaign', 'Without Campaign'],
            'AOV': [campaign_aov, non_campaign_aov],
            'Orders': [len(campaign_df), len(non_campaign_df)]
        })
        
        fig = px.bar(comparison,
                     x='Type',
                     y='AOV',
                     title="Average Order Value: Campaign Impact",
                     color='Type',
                     text='AOV')
        fig.update_traces(texttemplate='฿%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Return on Ad Spend (ROAS)
        campaign_profit = campaign_df['profit'].sum()
        campaign_cost = (campaign_df['discount_pct'] * campaign_df['sale_price']).sum()
        roas = (campaign_revenue / campaign_cost * 100) if campaign_cost > 0 else 0
        
        st.metric("Return on Ad Spend (ROAS)", f"{roas:.1f}%")
        st.metric("Campaign Profit", f"฿{campaign_profit:,.0f}")
        st.metric("Campaign Cost", f"฿{campaign_cost:,.0f}")
    
    # Traffic Source Performance
    st.subheader("2️⃣ Traffic Source Performance (SEO/Marketing Channels)")
    
    traffic_perf = df_marketing.groupby('traffic_source').agg({
        'user_id': 'nunique',
        'order_id': 'nunique',
        'sale_price': 'sum',
        'profit': 'sum'
    }).reset_index()
    traffic_perf.columns = ['Traffic Source', 'Customers', 'Orders', 'Revenue', 'Profit']
    traffic_perf['Conversion Rate %'] = (traffic_perf['Orders'] / traffic_perf['Customers'] * 100).round(2)
    traffic_perf['Revenue per Customer'] = (traffic_perf['Revenue'] / traffic_perf['Customers']).round(2)
    traffic_perf['Profit Margin %'] = (traffic_perf['Profit'] / traffic_perf['Revenue'] * 100).round(2)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(traffic_perf.sort_values('Revenue', ascending=True),
                     x='Revenue',
                     y='Traffic Source',
                     orientation='h',
                     title="Revenue by Traffic Source",
                     color='Profit Margin %',
                     color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(traffic_perf,
                        x='Customers',
                        y='Revenue per Customer',
                        size='Revenue',
                        color='Traffic Source',
                        title="Customer Value by Traffic Source",
                        hover_data=['Conversion Rate %'])
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(traffic_perf.sort_values('Revenue', ascending=False), use_container_width=True)
    
    # Customer Segmentation (RFM + Clustering)
    st.subheader("3️⃣ Customer Segmentation (RFM Analysis)")
    
    analysis_date = df_marketing['created_at'].max()
    
    rfm_data = df_marketing.groupby('user_id').agg({
        'created_at': lambda x: (analysis_date - x.max()).days,
        'order_id': 'nunique',
        'sale_price': 'sum',
        'profit': 'sum'
    }).reset_index()
    rfm_data.columns = ['user_id', 'recency', 'frequency', 'monetary', 'total_profit']
    
    # Calculate RFM scores
    rfm_data['R_score'] = pd.qcut(rfm_data['recency'], q=4, labels=[4,3,2,1], duplicates='drop')
    rfm_data['F_score'] = pd.qcut(rfm_data['frequency'], q=4, labels=[1,2,3,4], duplicates='drop')
    rfm_data['M_score'] = pd.qcut(rfm_data['monetary'], q=4, labels=[1,2,3,4], duplicates='drop')
    
    rfm_data['RFM_score'] = (rfm_data['R_score'].astype(int) + 
                              rfm_data['F_score'].astype(int) + 
                              rfm_data['M_score'].astype(int))
    
    def segment_customer(score):
        if score >= 9:
            return 'Champions'
        elif score >= 6:
            return 'Loyal'
        elif score >= 4:
            return 'At Risk'
        else:
            return 'Lost'
    
    rfm_data['segment'] = rfm_data['RFM_score'].apply(segment_customer)
    
    col1, col2 = st.columns(2)
    
    with col1:
        seg_dist = rfm_data['segment'].value_counts()
        colors = {'Champions': '#2ecc71', 'Loyal': '#3498db', 'At Risk': '#f39c12', 'Lost': '#e74c3c'}
        fig = px.pie(values=seg_dist.values,
                     names=seg_dist.index,
                     title="Customer Distribution by RFM Segment",
                     hole=0.4,
                     color=seg_dist.index,
                     color_discrete_map=colors)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        seg_value = rfm_data.groupby('segment')['monetary'].sum().sort_values(ascending=True)
        fig = px.bar(x=seg_value.values,
                     y=seg_value.index,
                     orientation='h',
                     title="Total Revenue by RFM Segment",
                     color=seg_value.index,
                     color_discrete_map=colors)
        st.plotly_chart(fig, use_container_width=True)
    
    # Segment metrics
    seg_metrics = rfm_data.groupby('segment').agg({
        'user_id': 'count',
        'recency': 'mean',
        'frequency': 'mean',
        'monetary': 'mean',
        'total_profit': 'mean',
        'RFM_score': 'mean'
    }).round(2)
    seg_metrics.columns = ['Customers', 'Avg Recency (days)', 'Avg Frequency', 'Avg Revenue (฿)', 'Avg Profit (฿)', 'Avg RFM Score']
    
    segment_order = ['Champions', 'Loyal', 'At Risk', 'Lost']
    seg_metrics = seg_metrics.reindex([s for s in segment_order if s in seg_metrics.index])
    
    st.dataframe(seg_metrics.style.background_gradient(cmap='RdYlGn', subset=['Avg RFM Score']), 
                use_container_width=True)

# ==========================================
# TAB 4: FINANCIAL ANALYTICS
# ==========================================
with tab4:
    st.header("💰 Financial & Accounting Analytics")
    
    df_finance = df_filtered.copy()
    
    st.subheader("1️⃣ Common Financial KPIs")
    
    # Key Financial Metrics
    total_revenue = df_finance['sale_price'].sum()
    total_cogs = df_finance['cost'].sum()
    gross_profit = total_revenue - total_cogs
    net_profit = df_finance['profit'].sum()
    
    # Gross Profit Margin
    gross_profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Net Profit Margin
    net_profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Operating metrics
    total_orders = df_finance['order_id'].nunique()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Revenue", f"฿{total_revenue:,.0f}")
    
    with col2:
        st.metric("COGS", f"฿{total_cogs:,.0f}")
    
    with col3:
        st.metric("Gross Profit", f"฿{gross_profit:,.0f}",
                 delta=f"{gross_profit_margin:.1f}%")
    
    with col4:
        st.metric("Net Profit", f"฿{net_profit:,.0f}",
                 delta=f"{net_profit_margin:.1f}%")
    
    with col5:
        ros = net_profit_margin  # Return on Sales = Net Profit Margin
        st.metric("Return on Sales (ROS)", f"{ros:.2f}%")
    
    # Account Receivable & Payable Analysis
    st.subheader("2️⃣ AR/AP Turnover & Cash Flow Metrics")
    
    # Simulate AR/AP data (in real scenario, you'd have actual AR/AP data)
    monthly_revenue = df_finance.groupby('order_month').agg({
        'sale_price': 'sum',
        'cost': 'sum',
        'profit': 'sum'
    }).reset_index()
    
    avg_monthly_revenue = monthly_revenue['sale_price'].mean()
    avg_ar_balance = avg_monthly_revenue * 0.3  # Assume 30% of sales are on credit
    
    # AR Turnover = Net Credit Sales / Average AR Balance
    net_credit_sales = total_revenue * 0.3  # Assume 30% credit sales
    ar_turnover = net_credit_sales / avg_ar_balance if avg_ar_balance > 0 else 0
    
    # Days Sales Outstanding (DSO) = 365 / AR Turnover
    dso = 365 / ar_turnover if ar_turnover > 0 else 0
    
    # AP Turnover
    avg_ap_balance = total_cogs * 0.25  # Assume 25% of COGS are payables
    ap_turnover = total_cogs / avg_ap_balance if avg_ap_balance > 0 else 0
    
    # Days Payable Outstanding (DPO)
    dpo = 365 / ap_turnover if ap_turnover > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("AR Turnover", f"{ar_turnover:.2f}x")
        st.caption("Higher is better")
    
    with col2:
        st.metric("Days Sales Outstanding", f"{dso:.0f} days")
        st.caption("Lower is better")
    
    with col3:
        st.metric("AP Turnover", f"{ap_turnover:.2f}x")
    
    with col4:
        st.metric("Days Payable Outstanding", f"{dpo:.0f} days")
    
    # Monthly Financial Performance
    st.subheader("3️⃣ Monthly Financial Performance")
    
    monthly_revenue['order_month'] = monthly_revenue['order_month'].dt.to_timestamp()
    monthly_revenue['gross_margin_%'] = (monthly_revenue['profit'] / monthly_revenue['sale_price'] * 100).round(2)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly_revenue['order_month'],
        y=monthly_revenue['sale_price'],
        name='Revenue',
        marker_color='lightblue'
    ))
    fig.add_trace(go.Bar(
        x=monthly_revenue['order_month'],
        y=monthly_revenue['cost'],
        name='COGS',
        marker_color='lightcoral'
    ))
    fig.add_trace(go.Scatter(
        x=monthly_revenue['order_month'],
        y=monthly_revenue['gross_margin_%'],
        name='Gross Margin %',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='green', width=3)
    ))
    
    fig.update_layout(
        title="Monthly Revenue, COGS & Gross Margin",
        xaxis_title="Month",
        yaxis_title="Amount (฿)",
        yaxis2=dict(title="Gross Margin (%)", overlaying='y', side='right'),
        barmode='group',
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Channel Profitability
    st.subheader("4️⃣ Channel Profitability Analysis")
    
    channel_finance = df_finance.groupby(['channel', 'channel_type']).agg({
        'sale_price': 'sum',
        'cost': 'sum',
        'profit': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    channel_finance.columns = ['Channel', 'Type', 'Revenue', 'COGS', 'Profit', 'Orders']
    channel_finance['Gross Margin %'] = (channel_finance['Profit'] / channel_finance['Revenue'] * 100).round(2)
    channel_finance['AOV'] = (channel_finance['Revenue'] / channel_finance['Orders']).round(2)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(channel_finance.sort_values('Profit', ascending=True),
                     x='Profit',
                     y='Channel',
                     orientation='h',
                     title="Profit by Channel",
                     color='Gross Margin %',
                     color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(channel_finance,
                        x='Revenue',
                        y='Profit',
                        size='Orders',
                        color='Type',
                        text='Channel',
                        title="Revenue vs Profit by Channel")
        fig.update_traces(textposition='top center')
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(channel_finance.sort_values('Revenue', ascending=False), use_container_width=True)
    
    # Sales Growth Rate
    st.subheader("5️⃣ Sales Growth Analysis")
    
    if len(monthly_revenue) >= 2:
        monthly_revenue['growth_rate'] = monthly_revenue['sale_price'].pct_change() * 100
        
        fig = px.line(monthly_revenue,
                     x='order_month',
                     y='growth_rate',
                     title="Monthly Sales Growth Rate (%)",
                     markers=True)
        fig.add_hline(y=0, line_dash="dash", line_color="red")
        fig.update_traces(line_color='#3498db', line_width=3)
        st.plotly_chart(fig, use_container_width=True)
        
        avg_growth = monthly_revenue['growth_rate'].mean()
        st.info(f"📊 Average Monthly Growth Rate: **{avg_growth:.2f}%**")

# ==========================================
# TAB 5: WAREHOUSE & INVENTORY ANALYTICS
# ==========================================
with tab5:
    st.header("📦 Warehouse & Inventory Analytics")
    
    df_warehouse = df_filtered.copy()
    
    st.subheader("1️⃣ Inventory Performance Metrics")
    
    # Inventory Turnover
    total_cogs = df_warehouse['cost'].sum()
    
    # Average Inventory (simplified - using cost as proxy)
    avg_inventory = df_warehouse['cost'].mean() * df_warehouse['product_id'].nunique()
    inventory_turnover = total_cogs / avg_inventory if avg_inventory > 0 else 0
    
    # Days Inventory Outstanding (DIO)
    dio = 365 / inventory_turnover if inventory_turnover > 0 else 0
    
    # Sell-through Rate
    total_units_sold = len(df_warehouse)
    total_units_received = total_units_sold * 1.2  # Assume 20% more received than sold
    sell_through_rate = (total_units_sold / total_units_received * 100) if total_units_received > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Inventory Turnover", f"{inventory_turnover:.2f}x")
        st.caption("Higher is better")
    
    with col2:
        st.metric("Days Inventory Outstanding", f"{dio:.0f} days")
        st.caption("Lower is better")
    
    with col3:
        st.metric("Sell-Through Rate", f"{sell_through_rate:.1f}%")
        st.caption("Target: >80%")
    
    with col4:
        total_inventory_value = avg_inventory
        st.metric("Total Inventory Value", f"฿{total_inventory_value:,.0f}")
    
    # Product Movement Analysis
    st.subheader("2️⃣ Product Movement Analysis (Fast/Slow Moving)")
    
    product_velocity = df_warehouse.groupby(['product_id', 'product_name', 'product_category']).agg({
        'order_id': 'nunique',
        'sale_price': 'sum',
        'cost': 'sum'
    }).reset_index()
    product_velocity.columns = ['Product ID', 'Product Name', 'Category', 'Order Count', 'Revenue', 'Cost']
    
    # Classify movement
    velocity_threshold_fast = product_velocity['Order Count'].quantile(0.75)
    velocity_threshold_slow = product_velocity['Order Count'].quantile(0.25)
    
    def classify_movement(count):
        if count >= velocity_threshold_fast:
            return 'Fast Moving'
        elif count <= velocity_threshold_slow:
            return 'Slow Moving'
        else:
            return 'Medium Moving'
    
    product_velocity['Movement'] = product_velocity['Order Count'].apply(classify_movement)
    product_velocity['Inventory Value'] = product_velocity['Cost']
    
    col1, col2 = st.columns(2)
    
    with col1:
        movement_dist = product_velocity['Movement'].value_counts()
        colors_movement = {
            'Fast Moving': '#2ecc71',
            'Medium Moving': '#f39c12',
            'Slow Moving': '#e74c3c'
        }
        fig = px.pie(values=movement_dist.values,
                     names=movement_dist.index,
                     title="Product Movement Distribution",
                     hole=0.4,
                     color=movement_dist.index,
                     color_discrete_map=colors_movement)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        movement_value = product_velocity.groupby('Movement')['Inventory Value'].sum().sort_values(ascending=True)
        fig = px.bar(x=movement_value.values,
                     y=movement_value.index,
                     orientation='h',
                     title="Inventory Value by Movement",
                     color=movement_value.index,
                     color_discrete_map=colors_movement)
        st.plotly_chart(fig, use_container_width=True)
    
    # Top/Bottom Products
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🚀 Top 10 Fast Moving Products")
        top_fast = product_velocity[product_velocity['Movement'] == 'Fast Moving'].nlargest(10, 'Order Count')
        st.dataframe(top_fast[['Product Name', 'Category', 'Order Count', 'Revenue']],
                    use_container_width=True, height=300)
    
    with col2:
        st.markdown("#### 🐌 Top 10 Slow Moving Products")
        top_slow = product_velocity[product_velocity['Movement'] == 'Slow Moving'].nlargest(10, 'Inventory Value')
        st.dataframe(top_slow[['Product Name', 'Category', 'Order Count', 'Inventory Value']],
                    use_container_width=True, height=300)
    
    # Stock Level & Reorder Analysis
    st.subheader("3️⃣ Stock Level & Reorder Point Analysis")
    
    # Calculate daily demand for top products
    daily_demand = df_warehouse.groupby(['order_date', 'product_id']).size().reset_index(name='quantity')
    
    product_demand_stats = daily_demand.groupby('product_id').agg({
        'quantity': ['mean', 'std', 'sum']
    }).reset_index()
    product_demand_stats.columns = ['product_id', 'avg_daily_demand', 'std_demand', 'total_sold']
    
    # Merge with product info
    product_demand_stats = product_demand_stats.merge(
        df_warehouse[['product_id', 'product_name']].drop_duplicates(),
        on='product_id',
        how='left'
    )
    
    # Calculate reorder point (assuming 7-day lead time and 95% service level)
    lead_time_days = 7
    service_level_z = 1.65  # 95% service level
    
    product_demand_stats['safety_stock'] = (
        service_level_z * product_demand_stats['std_demand'] * np.sqrt(lead_time_days)
    ).fillna(0)
    
    product_demand_stats['reorder_point'] = (
        product_demand_stats['avg_daily_demand'] * lead_time_days + 
        product_demand_stats['safety_stock']
    ).round(0)
    
    product_demand_stats = product_demand_stats.nlargest(20, 'total_sold')
    
    st.dataframe(
        product_demand_stats[['product_name', 'avg_daily_demand', 'safety_stock', 'reorder_point', 'total_sold']]
        .round(2)
        .rename(columns={
            'product_name': 'Product',
            'avg_daily_demand': 'Avg Daily Demand',
            'safety_stock': 'Safety Stock',
            'reorder_point': 'Reorder Point',
            'total_sold': 'Total Sold'
        }),
        use_container_width=True,
        height=400
    )
    
    # Order Fulfillment Metrics
    st.subheader("4️⃣ Order Fulfillment & Accuracy Metrics")
    
    # Calculate fulfillment metrics
    total_orders = df_warehouse['order_id'].nunique()
    completed_orders = df_warehouse[df_warehouse['status'] == 'Complete']['order_id'].nunique() if 'status' in df_warehouse.columns else total_orders
    
    # On-time shipping rate (simplified)
    on_time_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
    
    # Order accuracy (assume 98% accuracy)
    order_accuracy = 98.0
    
    # Backorder rate
    backorder_rate = 2.0  # Simplified assumption
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Order Fulfillment Rate", f"{on_time_rate:.1f}%")
        st.caption("Target: >95%")
    
    with col2:
        st.metric("Order Accuracy", f"{order_accuracy:.1f}%")
        st.caption("Target: >99%")
    
    with col3:
        st.metric("Backorder Rate", f"{backorder_rate:.1f}%")
        st.caption("Target: <5%")
    
    with col4:
        avg_order_cycle = 3.5  # days
        st.metric("Avg Order Cycle Time", f"{avg_order_cycle:.1f} days")
        st.caption("Order to delivery")
    
    # Inventory Carrying Cost
    st.subheader("5️⃣ Inventory Carrying Costs")
    
    total_inventory_value = avg_inventory
    
    # Carrying cost breakdown (typical percentages)
    storage_cost_pct = 0.06  # 6%
    capital_cost_pct = 0.10  # 10%
    insurance_risk_pct = 0.04  # 4%
    
    total_carrying_cost_pct = storage_cost_pct + capital_cost_pct + insurance_risk_pct
    
    storage_cost = total_inventory_value * storage_cost_pct
    capital_cost = total_inventory_value * capital_cost_pct
    insurance_cost = total_inventory_value * insurance_risk_pct
    total_carrying_cost = total_inventory_value * total_carrying_cost_pct
    
    col1, col2 = st.columns(2)
    
    with col1:
        carrying_breakdown = pd.DataFrame({
            'Cost Type': ['Storage Cost', 'Capital Cost', 'Insurance & Risk'],
            'Amount': [storage_cost, capital_cost, insurance_cost],
            'Percentage': [storage_cost_pct * 100, capital_cost_pct * 100, insurance_risk_pct * 100]
        })
        
        fig = px.pie(carrying_breakdown,
                     values='Amount',
                     names='Cost Type',
                     title="Inventory Carrying Cost Breakdown",
                     hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Total Carrying Cost", f"฿{total_carrying_cost:,.0f}")
        st.metric("Carrying Cost %", f"{total_carrying_cost_pct * 100:.1f}%")
        st.caption(f"Storage: ฿{storage_cost:,.0f}")
        st.caption(f"Capital: ฿{capital_cost:,.0f}")
        st.caption(f"Insurance: ฿{insurance_cost:,.0f}")
    
    # Cash Conversion Cycle
    st.subheader("6️⃣ Cash Conversion Cycle")
    
    # DIO calculated earlier
    # DSO calculated earlier (in finance tab)
    # DPO calculated earlier (in finance tab)
    
    cash_conversion_cycle = dio + dso - dpo
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Days Inventory Outstanding", f"{dio:.0f} days")
    
    with col2:
        st.metric("Days Sales Outstanding", f"{dso:.0f} days")
    
    with col3:
        st.metric("Days Payable Outstanding", f"{dpo:.0f} days")
    
    with col4:
        st.metric("Cash Conversion Cycle", f"{cash_conversion_cycle:.0f} days")
        st.caption("Lower is better")

st.markdown("---")
st.caption("📊 E-commerce Analytics Dashboard Pro | Powered by Streamlit")
