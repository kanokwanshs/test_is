# app.py - Main Streamlit Dashboard with File Upload
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(page_title="E-commerce Analytics", layout="wide", page_icon="📊")

# Initialize session state for data
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'data' not in st.session_state:
    st.session_state.data = None

# File upload section
def upload_files():
    """Upload CSV files"""
    st.sidebar.title("📊 E-commerce Analytics")
    st.sidebar.markdown("---")
    st.sidebar.subheader("📁 Upload CSV Files")
    
    uploaded_files = {
        "distribution_centers": st.sidebar.file_uploader("Distribution Centers CSV", type=['csv'], key='dc'),
        "user": st.sidebar.file_uploader("User CSV", type=['csv'], key='user'),
        "product": st.sidebar.file_uploader("Product CSV", type=['csv'], key='product'),
        "inventory_item": st.sidebar.file_uploader("Inventory Item CSV", type=['csv'], key='inventory'),
        "order": st.sidebar.file_uploader("Order CSV", type=['csv'], key='order'),
        "order_item": st.sidebar.file_uploader("Order Item CSV", type=['csv'], key='order_item'),
        "event": st.sidebar.file_uploader("Event CSV", type=['csv'], key='event')
    }
    
    if st.sidebar.button("🔄 Load Data", type="primary"):
        # Check if all required files are uploaded
        required_files = ["user", "product", "order", "order_item"]
        missing_files = [f for f in required_files if uploaded_files[f] is None]
        
        if missing_files:
            st.sidebar.error(f"❌ Please upload required files: {', '.join(missing_files)}")
            return None
        
        # Load all uploaded files
        data = {}
        try:
            for key, file in uploaded_files.items():
                if file is not None:
                    data[key] = pd.read_csv(file)
                    st.sidebar.success(f"✅ Loaded {key}")
            
            st.session_state.data = data
            st.session_state.data_loaded = True
            st.sidebar.success("✅ All data loaded successfully!")
            return data
        except Exception as e:
            st.sidebar.error(f"❌ Error loading data: {str(e)}")
            return None
    
    return st.session_state.data if st.session_state.data_loaded else None

@st.cache_data
def merge_and_preprocess(data):
    """Merge all tables and create master dataframe"""
    # Order items + Orders
    df = data['order_item'].merge(
        data['order'][['order_id', 'channel', 'discount_pct', 'status', 'num_of_item']], 
        on='order_id', 
        how='left',
        suffixes=('', '_order')
    )
    
    # Add product info
    df = df.merge(
        data['product'][['product_id', 'product_category', 'product_collection', 'retail_price', 'product_name']], 
        on='product_id', 
        how='left',
        suffixes=('', '_prod')
    )
    
    # Add user info
    df = df.merge(
        data['user'][['user_id', 'city', 'traffic_source', 'age', 'gender']], 
        on='user_id', 
        how='left'
    )
    
    # Date conversions
    for col in ['created_at', 'shipped_at', 'delivered_at', 'returned_at']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Derived fields
    df['profit'] = df['sale_price'] - df['cost']
    df['order_date'] = df['created_at'].dt.date
    df['order_month'] = df['created_at'].dt.to_period('M')
    df['order_hour'] = df['created_at'].dt.hour
    df['order_dayofweek'] = df['created_at'].dt.dayofweek
    
    return df, data

# ==========================================
# SIDEBAR - File Upload
# ==========================================
data = upload_files()

if data is None or not st.session_state.data_loaded:
    st.title("📊 E-commerce Analytics Dashboard")
    st.info("👈 Please upload CSV files in the sidebar to begin analysis")
    
    st.markdown("""
    ### Required Files:
    - ✅ **User CSV** (user_id, city, traffic_source, age, gender)
    - ✅ **Product CSV** (product_id, product_category, product_name, retail_price)
    - ✅ **Order CSV** (order_id, channel, discount_pct, status, num_of_item, created_at)
    - ✅ **Order Item CSV** (order_id, product_id, user_id, sale_price, cost)
    
    ### Optional Files:
    - Distribution Centers CSV
    - Inventory Item CSV
    - Event CSV
    """)
    st.stop()

# Process data
df_master, data_dict = merge_and_preprocess(data)

st.sidebar.markdown("---")
st.sidebar.success(f"✅ Loaded {len(df_master):,} transactions")
st.sidebar.metric("Total Revenue", f"฿{df_master['sale_price'].sum():,.0f}")
st.sidebar.metric("Total Profit", f"฿{df_master['profit'].sum():,.0f}")

# ==========================================
# MAIN TABS
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "👥 CRM & Sales", 
    "📦 Inventory Forecast", 
    "💰 Accounting & Profit",
    "🎯 Marketing Analytics"
])

# ==========================================
# TAB 1: CRM & SALES
# ==========================================
with tab1:
    st.header("👥 CRM & Sales Analytics")
    
    # Behavioral Customer Segmentation
    st.subheader("1️⃣ Behavioral Customer Segmentation")
    st.info("Segmentation based on RFM (Recency, Frequency, Monetary)")
    
    # Calculate RFM
    max_date = df_master['created_at'].max()
    rfm = df_master.groupby('user_id').agg({
        'created_at': lambda x: (max_date - x.max()).days,  # Recency
        'order_id': 'nunique',  # Frequency
        'sale_price': 'sum'  # Monetary
    }).reset_index()
    rfm.columns = ['user_id', 'recency', 'frequency', 'monetary']
    
    # Add user info
    rfm = rfm.merge(data_dict['user'][['user_id', 'city', 'traffic_source']], on='user_id', how='left')
    
    # RFM Scoring (1-5)
    rfm['R_score'] = pd.qcut(rfm['recency'], 5, labels=[5,4,3,2,1], duplicates='drop')
    rfm['F_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5], duplicates='drop')
    rfm['M_score'] = pd.qcut(rfm['monetary'], 5, labels=[1,2,3,4,5], duplicates='drop')
    
    # Behavioral Segments
    def segment_customers(row):
        if row['R_score'] >= 4 and row['F_score'] >= 4:
            return 'Champions'
        elif row['R_score'] >= 3 and row['F_score'] >= 3:
            return 'Loyal Customers'
        elif row['R_score'] >= 4:
            return 'Promising'
        elif row['F_score'] >= 4:
            return 'Need Attention'
        elif row['R_score'] <= 2:
            return 'At Risk'
        else:
            return 'Others'
    
    rfm['behavioral_segment'] = rfm.apply(segment_customers, axis=1)
    
    # Display segments
    col1, col2 = st.columns(2)
    with col1:
        seg_dist = rfm['behavioral_segment'].value_counts()
        fig = px.pie(values=seg_dist.values, names=seg_dist.index, 
                     title="Customer Segments Distribution",
                     hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        seg_value = rfm.groupby('behavioral_segment')['monetary'].sum().sort_values(ascending=False)
        fig = px.bar(x=seg_value.index, y=seg_value.values,
                    title="Revenue by Customer Segment",
                    labels={'x': 'Segment', 'y': 'Revenue (฿)'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Customer Lifetime Value (CLV)
    st.subheader("2️⃣ Customer Lifetime Value (CLV)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_clv = rfm['monetary'].mean()
        st.metric("Avg CLV", f"฿{avg_clv:,.0f}")
    with col2:
        avg_freq = rfm['frequency'].mean()
        st.metric("Avg Purchase Frequency", f"{avg_freq:.1f}")
    with col3:
        avg_recency = rfm['recency'].mean()
        st.metric("Avg Recency (days)", f"{avg_recency:.0f}")
    
    # CLV by segment
    clv_by_seg = rfm.groupby('behavioral_segment').agg({
        'monetary': 'mean',
        'frequency': 'mean',
        'recency': 'mean',
        'user_id': 'count'
    }).round(2)
    clv_by_seg.columns = ['Avg CLV (฿)', 'Avg Frequency', 'Avg Recency (days)', 'Customer Count']
    st.dataframe(clv_by_seg, use_container_width=True)
    
    # Churn Prediction
    st.subheader("3️⃣ Churn Prediction Model")
    
    # Define churn (no purchase in last 60 days)
    rfm['is_churned'] = (rfm['recency'] > 60).astype(int)
    
    # Features for model
    X = rfm[['recency', 'frequency', 'monetary']].fillna(0)
    y = rfm['is_churned']
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    model.fit(X_train, y_train)
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        accuracy = (y_pred == y_test).mean()
        st.metric("Accuracy", f"{accuracy:.1%}")
    with col2:
        churn_rate = y.mean()
        st.metric("Overall Churn Rate", f"{churn_rate:.1%}")
    with col3:
        auc = roc_auc_score(y_test, y_pred_proba)
        st.metric("ROC-AUC", f"{auc:.3f}")
    with col4:
        high_risk = (rfm['recency'] > 60).sum()
        st.metric("High Risk Customers", f"{high_risk:,}")
    
    # Feature importance
    feat_imp = pd.DataFrame({
        'feature': ['Recency', 'Frequency', 'Monetary'],
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    fig = px.bar(feat_imp, x='importance', y='feature', orientation='h',
                title="Churn Prediction - Feature Importance")
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TAB 2: INVENTORY FORECAST
# ==========================================
with tab2:
    st.header("📦 Inventory Forecasting")
    
    # Product demand aggregation
    demand_df = df_master.groupby(['order_date', 'product_id']).size().reset_index(name='quantity')
    demand_df['order_date'] = pd.to_datetime(demand_df['order_date'])
    
    # Select product for forecast
    st.subheader("1️⃣ Product Demand Forecasting")
    top_products = df_master.groupby('product_id').size().nlargest(20).index.tolist()
    selected_product = st.selectbox("Select Product", top_products)
    
    # Filter for selected product
    prod_demand = demand_df[demand_df['product_id'] == selected_product].sort_values('order_date')
    
    if len(prod_demand) > 30:
        # Simple moving average forecast
        prod_demand['MA_7'] = prod_demand['quantity'].rolling(window=7).mean()
        prod_demand['MA_30'] = prod_demand['quantity'].rolling(window=30).mean()
        
        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(prod_demand, x='order_date', y=['quantity', 'MA_7', 'MA_30'],
                         title=f"Demand Forecast: {selected_product}")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Forecast next 30 days
            last_30_avg = prod_demand['quantity'].tail(30).mean()
            forecast_30d = last_30_avg * 30
            
            st.metric("Avg Daily Demand (Last 30d)", f"{last_30_avg:.1f} units")
            st.metric("Forecasted Demand (Next 30d)", f"{forecast_30d:.0f} units")
            
            # Safety stock calculation
            std_dev = prod_demand['quantity'].std()
            safety_stock = 1.65 * std_dev * np.sqrt(7)
            st.metric("Recommended Safety Stock", f"{safety_stock:.0f} units")

# ==========================================
# TAB 3: ACCOUNTING & PROFIT
# ==========================================
with tab3:
    st.header("💰 Accounting & Profitability Analysis")
    
    # Overall metrics
    st.subheader("1️⃣ Key Financial Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_revenue = df_master['sale_price'].sum()
        st.metric("Total Revenue", f"฿{total_revenue:,.0f}")
    with col2:
        total_cost = df_master['cost'].sum()
        st.metric("Total Cost", f"฿{total_cost:,.0f}")
    with col3:
        total_profit = df_master['profit'].sum()
        st.metric("Total Profit", f"฿{total_profit:,.0f}")
    with col4:
        profit_margin = (total_profit / total_revenue * 100)
        st.metric("Profit Margin", f"{profit_margin:.1f}%")
    
    # Profitability by Category
    st.subheader("2️⃣ Profitability Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        cat_profit = df_master.groupby('product_category').agg({
            'sale_price': 'sum',
            'profit': 'sum'
        }).reset_index()
        cat_profit['margin_%'] = (cat_profit['profit'] / cat_profit['sale_price'] * 100).round(1)
        
        fig = px.bar(cat_profit, x='product_category', y='profit',
                    title="Profit by Product Category",
                    labels={'profit': 'Profit (฿)', 'product_category': 'Category'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        channel_profit = df_master.groupby('channel').agg({
            'sale_price': 'sum',
            'profit': 'sum'
        }).reset_index()
        channel_profit['margin_%'] = (channel_profit['profit'] / channel_profit['sale_price'] * 100).round(1)
        
        fig = px.bar(channel_profit, x='channel', y='profit',
                    title="Profit by Sales Channel",
                    labels={'profit': 'Profit (฿)', 'channel': 'Channel'})
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TAB 4: MARKETING ANALYTICS
# ==========================================
with tab4:
    st.header("🎯 Marketing Analytics")
    
    # Campaign Effectiveness
    st.subheader("1️⃣ Campaign Effectiveness")
    
    campaign_orders = df_master[df_master['discount_pct'] > 0].copy()
    non_campaign_orders = df_master[df_master['discount_pct'] == 0].copy()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        campaign_revenue = campaign_orders['sale_price'].sum()
        st.metric("Campaign Revenue", f"฿{campaign_revenue:,.0f}")
    with col2:
        campaign_orders_count = len(campaign_orders)
        st.metric("Campaign Orders", f"{campaign_orders_count:,}")
    with col3:
        avg_discount = campaign_orders['discount_pct'].mean() * 100
        st.metric("Avg Discount", f"{avg_discount:.1f}%")
    with col4:
        campaign_aov = campaign_orders['sale_price'].mean()
        st.metric("Campaign AOV", f"฿{campaign_aov:,.0f}")
    
    # Customer Clustering
    st.subheader("2️⃣ Customer Segmentation (KMeans)")
    
    # Prepare features
    cluster_features = rfm[['recency', 'frequency', 'monetary']].fillna(0)
    scaler = StandardScaler()
    cluster_features_scaled = scaler.fit_transform(cluster_features)
    
    # KMeans
    n_clusters = st.slider("Number of Clusters", 2, 6, 4)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    rfm['cluster'] = kmeans.fit_predict(cluster_features_scaled)
    
    # Visualize
    fig = px.scatter_3d(rfm, x='recency', y='frequency', z='monetary',
                       color='cluster',
                       title="Customer Clusters (3D)")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("📊 E-commerce Analytics Dashboard | Built with Streamlit")
