# app.py - Main Streamlit Dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
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

# Load data functions
@st.cache_data
def load_from_folder(path="data"):
    """Load all CSV files from data folder"""
    files = {
        "distribution_centers.csv": "dc",
        "user.csv": "user",
        "product.csv": "product",
        "inventory_item.csv": "inventory",
        "order.csv": "order",
        "order_item.csv": "order_item",
        "event.csv": "event"
    }
    
    data = {}
    for file, key in files.items():
        fp = os.path.join(path, file)
        if os.path.exists(fp):
            data[key] = pd.read_csv(fp)
        else:
            st.warning(f"Missing: {file}")
            return None
    return data

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
    
    # Add user info (but we won't use customer_segment column)
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
# SIDEBAR - Data Loading
# ==========================================
st.sidebar.title("📊 E-commerce Analytics")
st.sidebar.markdown("---")

# Load data
data_path = st.sidebar.text_input("Data folder path", value="data")
if st.sidebar.button("🔄 Load Data"):
    st.cache_data.clear()

data = load_from_folder(data_path)
if data is None:
    st.error("❌ Cannot load data. Please check the data folder path.")
    st.stop()

df_master, data_dict = merge_and_preprocess(data)

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
    
    # Behavioral Customer Segmentation (NOT using customer_segment column)
    st.subheader("1️⃣ Behavioral Customer Segmentation")
    st.info("Segmentation based on RFM (Recency, Frequency, Monetary) - NOT using pre-labeled segments")
    
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
    
    # Customer Activity Time Patterns
    st.subheader("4️⃣ Customer Activity Time Patterns")
    
    col1, col2 = st.columns(2)
    with col1:
        hourly = df_master.groupby('order_hour').size().reset_index(name='orders')
        fig = px.line(hourly, x='order_hour', y='orders',
                     title="Orders by Hour of Day",
                     labels={'order_hour': 'Hour', 'orders': 'Number of Orders'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        dow_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
        daily = df_master.groupby('order_dayofweek').size().reset_index(name='orders')
        daily['day'] = daily['order_dayofweek'].map(dow_map)
        fig = px.bar(daily, x='day', y='orders',
                    title="Orders by Day of Week")
        st.plotly_chart(fig, use_container_width=True)
    
    # Customer Cohort Analysis
    st.subheader("5️⃣ Customer Cohort Analysis")
    
    # Get first purchase date for each customer
    cohort_data = df_master.groupby('user_id')['created_at'].min().reset_index()
    cohort_data.columns = ['user_id', 'first_purchase']
    cohort_data['cohort_month'] = cohort_data['first_purchase'].dt.to_period('M')
    
    # Merge back
    df_cohort = df_master.merge(cohort_data[['user_id', 'cohort_month']], on='user_id')
    df_cohort['order_month'] = df_cohort['created_at'].dt.to_period('M')
    
    # Calculate cohort index
    df_cohort['cohort_index'] = (df_cohort['order_month'] - df_cohort['cohort_month']).apply(lambda x: x.n)
    
    # Cohort table
    cohort_counts = df_cohort.groupby(['cohort_month', 'cohort_index'])['user_id'].nunique().reset_index()
    cohort_table = cohort_counts.pivot(index='cohort_month', columns='cohort_index', values='user_id')
    
    # Retention rate
    cohort_size = cohort_table.iloc[:, 0]
    retention = cohort_table.divide(cohort_size, axis=0) * 100
    
    fig = go.Figure(data=go.Heatmap(
        z=retention.values,
        x=[f"Month {i}" for i in retention.columns],
        y=[str(i) for i in retention.index],
        colorscale='Blues',
        text=retention.values.round(1),
        texttemplate='%{text}%',
        textfont={"size": 10}
    ))
    fig.update_layout(title="Cohort Retention Rate (%)",
                     xaxis_title="Months Since First Purchase",
                     yaxis_title="Cohort Month")
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
            
            # Safety stock calculation (using std dev)
            std_dev = prod_demand['quantity'].std()
            safety_stock = 1.65 * std_dev * np.sqrt(7)  # 95% service level, 7-day lead time
            st.metric("Recommended Safety Stock", f"{safety_stock:.0f} units")
    
    # Fast vs Slow Moving Products
    st.subheader("2️⃣ Product Movement Segmentation")
    
    product_velocity = df_master.groupby('product_id').agg({
        'order_id': 'nunique',
        'sale_price': 'sum'
    }).reset_index()
    product_velocity.columns = ['product_id', 'order_count', 'total_revenue']
    
    # Classify
    velocity_threshold = product_velocity['order_count'].quantile(0.7)
    product_velocity['movement'] = product_velocity['order_count'].apply(
        lambda x: 'Fast Moving' if x >= velocity_threshold else 'Slow Moving'
    )
    
    col1, col2 = st.columns(2)
    with col1:
        movement_dist = product_velocity['movement'].value_counts()
        fig = px.pie(values=movement_dist.values, names=movement_dist.index,
                    title="Product Movement Distribution",
                    hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        top_fast = product_velocity[product_velocity['movement'] == 'Fast Moving'].nlargest(10, 'order_count')
        fig = px.bar(top_fast, x='product_id', y='order_count',
                    title="Top 10 Fast Moving Products")
        st.plotly_chart(fig, use_container_width=True)
    
    # Out-of-stock risk
    st.subheader("3️⃣ Out-of-Stock Risk Estimation")
    
    # Calculate current inventory vs demand
    inventory_status = data_dict['inventory'].groupby('product_id').agg({
        'in': 'sum',
        'out': 'sum'
    }).reset_index()
    inventory_status['current_stock'] = inventory_status['in'] - inventory_status['out']
    
    # Merge with demand
    inventory_status = inventory_status.merge(
        product_velocity[['product_id', 'order_count']], 
        on='product_id', 
        how='left'
    )
    
    # Days of inventory remaining
    inventory_status['days_remaining'] = inventory_status['current_stock'] / (inventory_status['order_count'] / 30)
    inventory_status['risk_level'] = inventory_status['days_remaining'].apply(
        lambda x: 'High Risk' if x < 7 else ('Medium Risk' if x < 14 else 'Low Risk')
    )
    
    risk_summary = inventory_status['risk_level'].value_counts()
    fig = px.bar(x=risk_summary.index, y=risk_summary.values,
                title="Out-of-Stock Risk Distribution",
                labels={'x': 'Risk Level', 'y': 'Number of Products'},
                color=risk_summary.index,
                color_discrete_map={'High Risk': 'red', 'Medium Risk': 'orange', 'Low Risk': 'green'})
    st.plotly_chart(fig, use_container_width=True)

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
    
    # CAC vs CLV
    st.subheader("3️⃣ Customer Acquisition Cost (CAC) vs CLV")
    
    # Estimate CAC (simplified: marketing spend / new customers)
    # Using avg discount as proxy for acquisition cost
    avg_discount = df_master[df_master['discount_pct'] > 0]['sale_price'].mean() * df_master['discount_pct'].mean()
    estimated_cac = avg_discount if not pd.isna(avg_discount) else 100
    
    avg_clv = rfm['monetary'].mean()
    ltv_cac_ratio = avg_clv / estimated_cac if estimated_cac > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Estimated CAC", f"฿{estimated_cac:,.0f}")
    with col2:
        st.metric("Avg CLV", f"฿{avg_clv:,.0f}")
    with col3:
        st.metric("LTV:CAC Ratio", f"{ltv_cac_ratio:.1f}x")
        if ltv_cac_ratio >= 3:
            st.success("✅ Healthy ratio (>3x)")
        else:
            st.warning("⚠️ Needs improvement")
    
    # Revenue Forecasting
    st.subheader("4️⃣ Revenue Forecasting")
    
    monthly_revenue = df_master.groupby('order_month')['sale_price'].sum().reset_index()
    monthly_revenue['order_month'] = monthly_revenue['order_month'].dt.to_timestamp()
    
    # Simple linear forecast
    if len(monthly_revenue) >= 3:
        last_3_months = monthly_revenue.tail(3)['sale_price'].mean()
        forecast_next_month = last_3_months
        
        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(monthly_revenue, x='order_month', y='sale_price',
                         title="Monthly Revenue Trend")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Avg Revenue (Last 3 Months)", f"฿{last_3_months:,.0f}")
            st.metric("Forecasted Next Month", f"฿{forecast_next_month:,.0f}")
            
            # Growth rate
            if len(monthly_revenue) >= 2:
                growth = ((monthly_revenue['sale_price'].iloc[-1] / monthly_revenue['sale_price'].iloc[-2] - 1) * 100)
                st.metric("MoM Growth", f"{growth:+.1f}%")

# ==========================================
# TAB 4: MARKETING ANALYTICS
# ==========================================
with tab4:
    st.header("🎯 Marketing Analytics")
    
    # Campaign Effectiveness
    st.subheader("1️⃣ Campaign Effectiveness Scoring")
    
    # Campaigns are discount_pct > 0
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
    
    # Compare campaign vs non-campaign
    comparison = pd.DataFrame({
        'Type': ['With Campaign', 'Without Campaign'],
        'AOV': [campaign_orders['sale_price'].mean(), non_campaign_orders['sale_price'].mean()],
        'Orders': [len(campaign_orders), len(non_campaign_orders)]
    })
    
    fig = px.bar(comparison, x='Type', y='AOV', title="AOV: Campaign vs Non-Campaign")
    st.plotly_chart(fig, use_container_width=True)
    
    # Channel Attribution
    st.subheader("2️⃣ Channel Attribution Analysis")
    
    channel_perf = df_master.groupby('channel').agg({
        'order_id': 'nunique',
        'sale_price': 'sum',
        'profit': 'sum'
    }).reset_index()
    channel_perf.columns = ['channel', 'orders', 'revenue', 'profit']
    channel_perf['aov'] = (channel_perf['revenue'] / channel_perf['orders']).round(2)
    channel_perf['profit_margin_%'] = (channel_perf['profit'] / channel_perf['revenue'] * 100).round(1)
    
    st.dataframe(channel_perf, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(channel_perf, values='revenue', names='channel',
                    title="Revenue Distribution by Channel",
                    hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(channel_perf, x='channel', y='profit_margin_%',
                    title="Profit Margin by Channel (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Customer Clustering (KMeans)
    st.subheader("3️⃣ Customer Segmentation (KMeans Clustering)")
    
    # Prepare features for clustering
    cluster_features = rfm[['recency', 'frequency', 'monetary']].fillna(0)
    
    # Standardize
    scaler = StandardScaler()
    cluster_features_scaled = scaler.fit_transform(cluster_features)
    
    # KMeans
    n_clusters = st.slider("Number of Clusters", 2, 6, 4)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    rfm['cluster'] = kmeans.fit_predict(cluster_features_scaled)
    
    # Visualize clusters
    fig = px.scatter_3d(rfm, x='recency', y='frequency', z='monetary',
                       color='cluster',
                       title="Customer Clusters (3D)",
                       labels={'cluster': 'Cluster'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Cluster statistics
    cluster_stats = rfm.groupby('cluster').agg({
        'recency': 'mean',
        'frequency': 'mean',
        'monetary': 'mean',
        'user_id': 'count'
    }).round(2)
    cluster_stats.columns = ['Avg Recency', 'Avg Frequency', 'Avg Monetary', 'Customer Count']
    st.dataframe(cluster_stats, use_container_width=True)
    
    # Traffic Source Performance
    st.subheader("4️⃣ Traffic Source Performance")
    
    traffic_perf = df_master.groupby('traffic_source').agg({
        'user_id': 'nunique',
        'sale_price': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    traffic_perf.columns = ['traffic_source', 'customers', 'revenue', 'orders']
    traffic_perf['revenue_per_customer'] = (traffic_perf['revenue'] / traffic_perf['customers']).round(2)
    
    fig = px.bar(traffic_perf, x='traffic_source', y='revenue',
                title="Revenue by Traffic Source",
                labels={'revenue': 'Revenue (฿)', 'traffic_source': 'Traffic Source'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(traffic_perf, use_container_width=True)

st.markdown("---")
st.caption("📊 E-commerce Analytics Dashboard | Built with Streamlit")
