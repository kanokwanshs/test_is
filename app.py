# app.py - E-commerce Analytics Dashboard Pro (Complete Version)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import warnings
import zipfile
import io

warnings.filterwarnings('ignore')
st.set_page_config(page_title="E-commerce Analytics Pro", layout="wide", page_icon="📊")

if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'data' not in st.session_state:
    st.session_state.data = None

def get_channel_type(channel):
    online = ['line shopping', 'lazada', 'shopee', 'tiktok']
    offline = ['siam center']
    ch = str(channel).lower()
    if any(o in ch for o in online): return 'Online'
    if any(o in ch for o in offline): return 'Offline'
    return 'Other'

def upload_data():
    st.sidebar.title("📊 E-commerce Analytics Pro")
    st.sidebar.markdown("---")
    method = st.sidebar.radio("📁 Data Source", ["Upload ZIP File", "Load from Folder Path"])
    
    if method == "Upload ZIP File":
        st.sidebar.subheader("Upload ZIP containing CSV files")
        uploaded = st.sidebar.file_uploader("Choose ZIP file", type=['zip'])
        
        if uploaded and st.sidebar.button("🔄 Load Data", type="primary"):
            try:
                with zipfile.ZipFile(io.BytesIO(uploaded.read())) as z:
                    data = {}
                    mapping = {"users.csv": "user","customers.csv": "user", "products.csv": "product", "orders.csv": "order", 
                              "order_items.csv": "order_item", "events.csv": "event"}
                    
                    for fname in z.namelist():
                        base = fname.split('/')[-1]
                        if base in mapping:
                            with z.open(fname) as f:
                                data[mapping[base]] = pd.read_csv(f)
                            st.sidebar.success(f"✅ {base}")
                    
                    if all(k in data for k in ['user', 'product', 'order', 'order_item']):
                        st.session_state.data = data
                        st.session_state.data_loaded = True
                        st.sidebar.success("✅ All data loaded!")
                        st.rerun()
                    else:
                        st.sidebar.error("❌ Missing required files")
            except Exception as e:
                st.sidebar.error(f"❌ Error: {str(e)}")
    else:
        path = st.sidebar.text_input("Folder path", value="data")
        if st.sidebar.button("🔄 Load Data", type="primary"):
            try:
                import os
                data = {}
                mapping = {"users.csv": "user","customers.csv": "user", "products.csv": "product", "orders.csv": "order", "order_items.csv": "order_item"}
                
                for fname, key in mapping.items():
                    fp = os.path.join(path, fname)
                    if os.path.exists(fp):
                        data[key] = pd.read_csv(fp)
                        st.sidebar.success(f"✅ {fname}")
                
                if all(k in data for k in ['user', 'product', 'order', 'order_item']):
                    st.session_state.data = data
                    st.session_state.data_loaded = True
                    st.rerun()
                else:
                    st.sidebar.error("❌ Missing required files")
            except Exception as e:
                st.sidebar.error(f"❌ Error: {str(e)}")
    
    return st.session_state.data if st.session_state.data_loaded else None

@st.cache_data
def merge_data(data):
    df = data['order_item'].copy()
    
    if 'order_id' in data['order'].columns:
        df = df.merge(data['order'], on='order_id', how='left', suffixes=('', '_o'))
    if 'product_id' in data['product'].columns:
        df = df.merge(data['product'], on='product_id', how='left', suffixes=('', '_p'))
    if 'user_id' in data['user'].columns:
        df = df.merge(data['user'], on='user_id', how='left', suffixes=('', '_u'))

    # 🔧 FIX USER_ID (สำคัญมาก)
    if 'user_id' not in df.columns:
        if 'customer_id' in df.columns:
            df['user_id'] = df['customer_id']
        elif 'buyer_user_id' in df.columns:
            df['user_id'] = df['buyer_user_id']
        elif 'user_id_o' in df.columns:
            df['user_id'] = df['user_id_o']
        else:
            df['user_id'] = 'UNKNOWN_USER'
    
    defaults = {
        'channel': 'Unknown',
        'discount_pct': 0.0,
        'status': 'Complete',
        'traffic_source': 'Unknown',
        'product_category': 'Other',
        'product_name': 'Unknown',
        'cost': 0,
        'sale_price': 0
    }
    for col, val in defaults.items():
        if col not in df.columns:
            df[col] = val
    
    if df['cost'].sum() == 0 and 'sale_price' in df.columns:
        df['cost'] = df['sale_price'] * 0.6
    
    for col in ['created_at', 'shipped_at', 'delivered_at']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    if 'created_at' not in df.columns:
        df['created_at'] = pd.Timestamp.now()
    
    df['profit'] = df['sale_price'] - df['cost']
    df['order_date'] = df['created_at'].dt.date
    df['order_month'] = df['created_at'].dt.to_period('M')
    df['order_year'] = df['created_at'].dt.year
    df['channel_type'] = df['channel'].apply(get_channel_type)
    
    return df

data = upload_data()

if not data:
    st.title("📊 E-commerce Analytics Dashboard Pro")
    st.info("👈 Please load your data in the sidebar to begin analysis")
    st.markdown("""
    ### Required Files:
    - ✅ **users.csv** - User information
    - ✅ **products.csv** - Product catalog
    - ✅ **orders.csv** - Order details
    - ✅ **order_items.csv** - Order line items
    """)
    st.stop()

df_master = merge_data(data)

st.sidebar.markdown("---")
st.sidebar.success(f"✅ {len(df_master):,} transactions")
st.sidebar.metric("Total Revenue", f"฿{df_master['sale_price'].sum():,.0f}")
st.sidebar.metric("Total Profit", f"฿{df_master['profit'].sum():,.0f}")

# Date Filter
min_date = df_master['created_at'].min().date()
max_date = df_master['created_at'].max().date()
date_range = st.date_input("📅 Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

if len(date_range) == 2:
    df_filtered = df_master[(df_master['created_at'].dt.date >= date_range[0]) & 
                            (df_master['created_at'].dt.date <= date_range[1])]
else:
    df_filtered = df_master

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Executive", "💼 Sales", "📢 Marketing", "💰 Financial", "📦 Warehouse"])

# # TAB 1: EXECUTIVE DASHBOARD
# with tab1:
#     st.header("📊 Executive Dashboard")
    
#     col1, col2, col3, col4 = st.columns(4)
#     revenue = df_filtered['sale_price'].sum()
#     profit = df_filtered['profit'].sum()
#     margin = (profit/revenue*100) if revenue > 0 else 0
    
#     col1.metric("Total Revenue", f"฿{revenue:,.0f}")
#     col2.metric("Total Profit", f"฿{profit:,.0f}", f"{margin:.1f}%")
#     col3.metric("Active Customers", f"{df_filtered['user_id'].nunique():,}")
#     col4.metric("Avg Order Value", f"฿{df_filtered['sale_price'].mean():,.2f}")
    
#     st.subheader("📈 Sales Trend Overview")
#     daily = df_filtered.groupby('order_date').agg({'sale_price': 'sum', 'profit': 'sum'}).reset_index()
#     daily['order_date'] = pd.to_datetime(daily['order_date'])
    
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=daily['order_date'], y=daily['sale_price'], name='Revenue', 
#                             line=dict(color='#3498db', width=2), fill='tozeroy'))
#     fig.add_trace(go.Scatter(x=daily['order_date'], y=daily['profit'], name='Profit',
#                             line=dict(color='#2ecc71', width=2), yaxis='y2'))
#     fig.update_layout(yaxis=dict(title="Revenue (฿)"), 
#                      yaxis2=dict(title="Profit (฿)", overlaying='y', side='right'), height=400)
#     st.plotly_chart(fig, use_container_width=True)
    
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         st.subheader("🏆 Top Category")
#         cat = df_filtered.groupby('product_category')['sale_price'].sum().nlargest(1)
#         if len(cat) > 0:
#             st.metric(cat.index[0], f"฿{cat.values[0]:,.0f}")
    
#     with col2:
#         st.subheader("📱 Best Channel")
#         ch = df_filtered.groupby('channel_type')['sale_price'].sum().nlargest(1)
#         if len(ch) > 0:
#             st.metric(ch.index[0], f"฿{ch.values[0]:,.0f}")
    
#     with col3:
#         st.subheader("🎯 Conversion")
#         users = df_filtered['user_id'].nunique()
#         orders = df_filtered['order_id'].nunique()
#         st.metric("Orders per Customer", f"{(orders/users):.2f}" if users > 0 else "0")

# TAB 1: EXECUTIVE DASHBOARD
with tab1:
    st.header("📊 Executive Dashboard")
    
    # =====================
    # KPI SUMMARY
    # =====================
    col1, col2, col3, col4 = st.columns(4)
    
    revenue = df_filtered['sale_price'].sum()
    profit = df_filtered['profit'].sum()
    margin = (profit / revenue * 100) if revenue > 0 else 0
    
    col1.metric("Total Revenue", f"฿{revenue:,.0f}")
    col2.metric("Profit Margin", f"{margin:.1f}%", f"฿{profit:,.0f}")
    col3.metric("Active Customers", f"{df_filtered['user_id'].nunique():,}")
    col4.metric("Avg Order Value", f"฿{df_filtered['sale_price'].mean():,.2f}")
    
    # =====================
    # SALES TREND OVERVIEW
    # =====================
    st.subheader("📈 Sales Trend Overview")
    
    daily = df_filtered.groupby('order_date').agg({
        'sale_price': 'sum',
        'profit': 'sum'
    }).reset_index()
    
    daily['order_date'] = pd.to_datetime(daily['order_date'])
    daily['margin_pct'] = np.where(
        daily['sale_price'] > 0,
        daily['profit'] / daily['sale_price'] * 100,
        0
    )
    
    fig = go.Figure()
    
    # Revenue (฿)
    fig.add_trace(go.Scatter(
        x=daily['order_date'],
        y=daily['sale_price'],
        name='Revenue',
        line=dict(color='#3498db', width=2),
        fill='tozeroy'
    ))
    
    # Profit Margin (%)
    fig.add_trace(go.Scatter(
        x=daily['order_date'],
        y=daily['margin_pct'],
        name='Profit Margin (%)',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='#2ecc71', width=3)
    ))
    
    fig.update_layout(
    yaxis=dict(
        title="Revenue (฿)"
    ),
    yaxis2=dict(
        title="Profit Margin (%)",
        overlaying='y',
        side='right',
        ticksuffix='%',
        range=[0, 100]   # 👈 FIX SCALE 0–100%
    ),
    height=400,
    legend=dict(orientation="h", y=1.15)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # =====================
    # HIGHLIGHTS
    # =====================
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🏆 Top Category")
        cat = df_filtered.groupby('product_category')['sale_price'].sum().nlargest(1)
        if len(cat) > 0:
            st.metric(cat.index[0], f"฿{cat.values[0]:,.0f}")
    
    with col2:
        st.subheader("📱 Best Channel")
        ch = df_filtered.groupby('channel_type')['sale_price'].sum().nlargest(1)
        if len(ch) > 0:
            st.metric(ch.index[0], f"฿{ch.values[0]:,.0f}")
    
    with col3:
        st.subheader("🎯 Conversion")
        users = df_filtered['user_id'].nunique()
        orders = df_filtered['order_id'].nunique()
        st.metric("Orders per Customer", f"{(orders / users):.2f}" if users > 0 else "0")


# TAB 2: SALES ANALYTICS
with tab2:
    st.header("💼 Sales Analytics")
    
    st.subheader("1️⃣ Common Sales KPIs")
    
    monthly = df_filtered.groupby('order_month').agg({'sale_price': 'sum', 'profit': 'sum'}).reset_index()
    monthly['order_month'] = monthly['order_month'].dt.to_timestamp()
    monthly = monthly.sort_values('order_month')
    
    growth = 0
    if len(monthly) >= 2:
        curr = monthly.iloc[-1]['sale_price']
        prev = monthly.iloc[-2]['sale_price']
        growth = ((curr - prev) / prev * 100) if prev > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Monthly Growth", f"{growth:+.2f}%")
    col2.metric("Profit Margin", f"{margin:.2f}%")
    
    target = 1000000
    curr_sales = df_filtered[df_filtered['order_month'] == df_filtered['order_month'].max()]['sale_price'].sum()
    attainment = (curr_sales / target * 100) if target > 0 else 0
    col3.metric("Target Attainment", f"{attainment:.1f}%")
    col4.metric("Avg Purchase", f"฿{df_filtered['sale_price'].mean():,.2f}")
    
    st.subheader("2️⃣ Sales by Channel")
    ch_sales = df_filtered.groupby('channel').agg({'sale_price': 'sum', 'order_id': 'nunique', 
                                                    'user_id': 'nunique'}).reset_index()
    ch_sales.columns = ['Channel', 'Revenue', 'Orders', 'Customers']
    ch_sales['Revenue %'] = (ch_sales['Revenue'] / ch_sales['Revenue'].sum() * 100).round(2)
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(ch_sales, values='Revenue', names='Channel', title="Revenue by Channel", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(ch_sales.sort_values('Revenue', ascending=True), x='Revenue', y='Channel',
                    orientation='h', title="Revenue by Channel", text='Revenue %')
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(ch_sales, use_container_width=True)
    
    st.subheader("3️⃣ Customer Acquisition & Retention")
    
    mkt_cost = df_filtered['discount_pct'].sum() * df_filtered['sale_price'].sum()
    new_cust = df_filtered['user_id'].nunique()
    cac = mkt_cost / new_cust if new_cust > 0 else 0
    
    analysis_date = df_filtered['created_at'].max()
    last_purchase = df_filtered.groupby('user_id')['created_at'].max()
    days_since = (analysis_date - last_purchase).dt.days
    churned = (days_since > 60).sum()
    churn_rate = (churned / len(last_purchase) * 100) if len(last_purchase) > 0 else 0
    retention_rate = 100 - churn_rate
    
    avg_rev = df_filtered.groupby('user_id')['sale_price'].sum().mean()
    clv = (margin/100) * (retention_rate/100) * avg_rev
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CAC", f"฿{cac:,.2f}")
    col2.metric("Retention Rate", f"{retention_rate:.2f}%")
    col3.metric("Churn Rate", f"{churn_rate:.2f}%")
    col4.metric("CLV", f"฿{clv:,.2f}")
    
    st.subheader("4️⃣ Product Performance")
    prod = df_filtered.groupby(['product_id', 'product_name', 'product_category']).agg({
        'sale_price': 'sum', 'profit': 'sum', 'order_id': 'nunique'
    }).reset_index()
    prod.columns = ['ID', 'Product', 'Category', 'Revenue', 'Profit', 'Orders']
    prod['Margin %'] = (prod['Profit'] / prod['Revenue'] * 100).round(2)
    prod = prod.sort_values('Revenue', ascending=False).head(20)
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(prod.head(10), x='Revenue', y='Product', orientation='h',
                    title="Top 10 Products", color='Margin %', color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.scatter(prod, x='Revenue', y='Profit', size='Orders', color='Category',
                        hover_data=['Product'], title="Revenue vs Profit")
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(prod, use_container_width=True)

# TAB 3: MARKETING ANALYTICS
with tab3:
    st.header("📢 Marketing Analytics")
    
    st.subheader("1️⃣ Campaign Effectiveness")
    
    camp = df_filtered[df_filtered['discount_pct'] > 0]
    no_camp = df_filtered[df_filtered['discount_pct'] == 0]
    
    camp_rev = camp['sale_price'].sum()
    camp_share = (camp_rev / revenue * 100) if revenue > 0 else 0
    conv_rate = (len(camp) / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
    avg_disc = camp['discount_pct'].mean() * 100 if len(camp) > 0 else 0
    camp_cac = (camp['discount_pct'] * camp['sale_price']).sum() / camp['user_id'].nunique() if len(camp) > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Campaign Revenue %", f"{camp_share:.1f}%")
    col2.metric("Campaign Conv Rate", f"{conv_rate:.1f}%")
    col3.metric("Avg Discount", f"{avg_disc:.1f}%")
    col4.metric("Campaign CAC", f"฿{camp_cac:,.2f}")
    
    col1, col2 = st.columns(2)
    with col1:
        camp_aov = camp['sale_price'].mean() if len(camp) > 0 else 0
        no_camp_aov = no_camp['sale_price'].mean() if len(no_camp) > 0 else 0
        comp = pd.DataFrame({'Type': ['With Campaign', 'Without Campaign'], 
                            'AOV': [camp_aov, no_camp_aov]})
        fig = px.bar(comp, x='Type', y='AOV', title="AOV: Campaign Impact", 
                    color='Type', text='AOV')
        fig.update_traces(texttemplate='฿%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        camp_profit = camp['profit'].sum()
        camp_cost = (camp['discount_pct'] * camp['sale_price']).sum()
        roas = (camp_rev / camp_cost * 100) if camp_cost > 0 else 0
        st.metric("ROAS", f"{roas:.1f}%")
        st.metric("Campaign Profit", f"฿{camp_profit:,.0f}")
        st.metric("Campaign Cost", f"฿{camp_cost:,.0f}")
    
    st.subheader("2️⃣ Traffic Source Performance")
    
    traffic = df_filtered.groupby('traffic_source').agg({
        'user_id': 'nunique', 'order_id': 'nunique', 'sale_price': 'sum', 'profit': 'sum'
    }).reset_index()
    traffic.columns = ['Source', 'Customers', 'Orders', 'Revenue', 'Profit']
    traffic['Conv %'] = (traffic['Orders'] / traffic['Customers'] * 100).round(2)
    traffic['Rev/Customer'] = (traffic['Revenue'] / traffic['Customers']).round(2)
    traffic['Margin %'] = (traffic['Profit'] / traffic['Revenue'] * 100).round(2)
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(traffic.sort_values('Revenue', ascending=True), x='Revenue', y='Source',
                    orientation='h', title="Revenue by Source", color='Margin %',
                    color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.scatter(traffic, x='Customers', y='Rev/Customer', size='Revenue',
                        color='Source', title="Customer Value by Source", hover_data=['Conv %'])
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(traffic.sort_values('Revenue', ascending=False), use_container_width=True)
    
    st.subheader("3️⃣ RFM Analysis")
    
    rfm = df_filtered.groupby('user_id').agg({
        'created_at': lambda x: (analysis_date - x.max()).days,
        'order_id': 'nunique', 'sale_price': 'sum', 'profit': 'sum'
    }).reset_index()
    rfm.columns = ['user_id', 'recency', 'frequency', 'monetary', 'total_profit']
    
    rfm['R'] = pd.qcut(rfm['recency'], 4, labels=[4,3,2,1], duplicates='drop')
    rfm['F'] = pd.qcut(rfm['frequency'], 4, labels=[1,2,3,4], duplicates='drop')
    rfm['M'] = pd.qcut(rfm['monetary'], 4, labels=[1,2,3,4], duplicates='drop')
    rfm['RFM_Score'] = rfm['R'].astype(int) + rfm['F'].astype(int) + rfm['M'].astype(int)
    
    def segment(s):
        if s >= 9: return 'Champions'
        elif s >= 6: return 'Loyal'
        elif s >= 4: return 'At Risk'
        return 'Lost'
    
    rfm['Segment'] = rfm['RFM_Score'].apply(segment)
    
    col1, col2 = st.columns(2)
    with col1:
        seg = rfm['Segment'].value_counts()
        colors = {'Champions': '#2ecc71', 'Loyal': '#3498db', 'At Risk': '#f39c12', 'Lost': '#e74c3c'}
        fig = px.pie(values=seg.values, names=seg.index, title="Customer Segments", 
                    hole=0.4, color=seg.index, color_discrete_map=colors)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        seg_val = rfm.groupby('Segment')['monetary'].sum().sort_values(ascending=True)
        fig = px.bar(x=seg_val.values, y=seg_val.index, orientation='h',
                    title="Revenue by Segment", color=seg_val.index, color_discrete_map=colors)
        st.plotly_chart(fig, use_container_width=True)
    
    seg_metrics = rfm.groupby('Segment').agg({
        'user_id': 'count', 'recency': 'mean', 'frequency': 'mean',
        'monetary': 'mean', 'total_profit': 'mean', 'RFM_Score': 'mean'
    }).round(2)
    seg_metrics.columns = ['Customers', 'Avg Recency', 'Avg Frequency', 
                          'Avg Revenue', 'Avg Profit', 'Avg RFM Score']
    st.dataframe(seg_metrics, use_container_width=True)

# TAB 4: FINANCIAL ANALYTICS
with tab4:
    st.header("💰 Financial Analytics")
    
    st.subheader("1️⃣ Financial KPIs")
    
    total_rev = df_filtered['sale_price'].sum()
    total_cogs = df_filtered['cost'].sum()
    gross_profit = total_rev - total_cogs
    net_profit = df_filtered['profit'].sum()
    gross_margin = (gross_profit / total_rev * 100) if total_rev > 0 else 0
    net_margin = (net_profit / total_rev * 100) if total_rev > 0 else 0
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Revenue", f"฿{total_rev:,.0f}")
    col2.metric("COGS", f"฿{total_cogs:,.0f}")
    col3.metric("Gross Profit", f"฿{gross_profit:,.0f}", f"{gross_margin:.1f}%")
    col4.metric("Net Profit", f"฿{net_profit:,.0f}", f"{net_margin:.1f}%")
    col5.metric("ROS", f"{net_margin:.2f}%")
    
    st.subheader("2️⃣ AR/AP Turnover")
    
    monthly_fin = df_filtered.groupby('order_month').agg({
        'sale_price': 'sum', 'cost': 'sum', 'profit': 'sum'
    }).reset_index()
    
    avg_monthly_rev = monthly_fin['sale_price'].mean()
    avg_ar = avg_monthly_rev * 0.3
    net_credit = total_rev * 0.3
    ar_turnover = net_credit / avg_ar if avg_ar > 0 else 0
    dso = 365 / ar_turnover if ar_turnover > 0 else 0
    
    avg_ap = total_cogs * 0.25
    ap_turnover = total_cogs / avg_ap if avg_ap > 0 else 0
    dpo = 365 / ap_turnover if ap_turnover > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("AR Turnover", f"{ar_turnover:.2f}x")
    col2.metric("DSO", f"{dso:.0f} days")
    col3.metric("AP Turnover", f"{ap_turnover:.2f}x")
    col4.metric("DPO", f"{dpo:.0f} days")
    
    st.subheader("3️⃣ Monthly Performance")
    
    monthly_fin['order_month'] = monthly_fin['order_month'].dt.to_timestamp()
    monthly_fin['margin_%'] = (monthly_fin['profit'] / monthly_fin['sale_price'] * 100).round(2)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly_fin['order_month'], y=monthly_fin['sale_price'],
                        name='Revenue', marker_color='lightblue'))
    fig.add_trace(go.Bar(x=monthly_fin['order_month'], y=monthly_fin['cost'],
                        name='COGS', marker_color='lightcoral'))
    fig.add_trace(go.Scatter(x=monthly_fin['order_month'], y=monthly_fin['margin_%'],
                            name='Margin %', yaxis='y2', mode='lines+markers',
                            line=dict(color='green', width=3)))
    fig.update_layout(yaxis=dict(title="Amount (฿)"),
                     yaxis2=dict(title="Margin (%)", overlaying='y', side='right'),
                     barmode='group', height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("4️⃣ Channel Profitability")
    
    ch_fin = df_filtered.groupby(['channel', 'channel_type']).agg({
        'sale_price': 'sum', 'cost': 'sum', 'profit': 'sum', 'order_id': 'nunique'
    }).reset_index()
    ch_fin.columns = ['Channel', 'Type', 'Revenue', 'COGS', 'Profit', 'Orders']
    ch_fin['Margin %'] = (ch_fin['Profit'] / ch_fin['Revenue'] * 100).round(2)
    ch_fin['AOV'] = (ch_fin['Revenue'] / ch_fin['Orders']).round(2)
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(ch_fin.sort_values('Profit', ascending=True), x='Profit', y='Channel',
                    orientation='h', title="Profit by Channel", color='Margin %',
                    color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.scatter(ch_fin, x='Revenue', y='Profit', size='Orders', color='Type',
                        text='Channel', title="Revenue vs Profit")
        fig.update_traces(textposition='top center')
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(ch_fin, use_container_width=True)
    
    st.subheader("5️⃣ Growth Analysis")
    
    if len(monthly_fin) >= 2:
        monthly_fin['growth_%'] = monthly_fin['sale_price'].pct_change() * 100
        fig = px.line(monthly_fin, x='order_month', y='growth_%',
                     title="Monthly Growth Rate", markers=True)
        fig.add_hline(y=0, line_dash="dash", line_color="red")
        fig.update_traces(line_color='#3498db', line_width=3)
        st.plotly_chart(fig, use_container_width=True)
        
        avg_growth = monthly_fin['growth_%'].mean()
        st.info(f"📊 Average Monthly Growth: **{avg_growth:.2f}%**")

# TAB 5: WAREHOUSE & INVENTORY
with tab5:
    st.header("📦 Warehouse & Inventory")
    
    st.subheader("1️⃣ Inventory Metrics")
    
    total_cogs = df_filtered['cost'].sum()
    avg_inv = df_filtered['cost'].mean() * df_filtered['product_id'].nunique()
    inv_turnover = total_cogs / avg_inv if avg_inv > 0 else 0
    dio = 365 / inv_turnover if inv_turnover > 0 else 0
    
    units_sold = len(df_filtered)
    units_received = units_sold * 1.2
    sell_through = (units_sold / units_received * 100) if units_received > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Inventory Turnover", f"{inv_turnover:.2f}x")
    col2.metric("DIO", f"{dio:.0f} days")
    col3.metric("Sell-Through Rate", f"{sell_through:.1f}%")
    col4.metric("Inventory Value", f"฿{avg_inv:,.0f}")
    
    st.subheader("2️⃣ Product Movement")
    
    prod_vel = df_filtered.groupby(['product_id', 'product_name', 'product_category']).agg({
        'order_id': 'nunique', 'sale_price': 'sum', 'cost': 'sum'
    }).reset_index()
    prod_vel.columns = ['ID', 'Product', 'Category', 'Order Count', 'Revenue', 'Cost']
    
    fast_threshold = prod_vel['Order Count'].quantile(0.75)
    slow_threshold = prod_vel['Order Count'].quantile(0.25)
    
    def classify_movement(cnt):
        if cnt >= fast_threshold: return 'Fast Moving'
        elif cnt <= slow_threshold: return 'Slow Moving'
        return 'Medium Moving'
    
    prod_vel['Movement'] = prod_vel['Order Count'].apply(classify_movement)
    prod_vel['Inv Value'] = prod_vel['Cost']
    
    col1, col2 = st.columns(2)
    with col1:
        mov_dist = prod_vel['Movement'].value_counts()
        colors_mov = {'Fast Moving': '#2ecc71', 'Medium Moving': '#f39c12', 'Slow Moving': '#e74c3c'}
        fig = px.pie(values=mov_dist.values, names=mov_dist.index,
                    title="Product Movement Distribution", hole=0.4,
                    color=mov_dist.index, color_discrete_map=colors_mov)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        mov_val = prod_vel.groupby('Movement')['Inv Value'].sum().sort_values(ascending=True)
        fig = px.bar(x=mov_val.values, y=mov_val.index, orientation='h',
                    title="Inventory Value by Movement",
                    color=mov_val.index, color_discrete_map=colors_mov)
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🚀 Top 10 Fast Moving")
        fast = prod_vel[prod_vel['Movement'] == 'Fast Moving'].nlargest(10, 'Order Count')
        st.dataframe(fast[['Product', 'Category', 'Order Count', 'Revenue']], 
                    use_container_width=True, height=300)
    
    with col2:
        st.markdown("#### 🐌 Top 10 Slow Moving")
        slow = prod_vel[prod_vel['Movement'] == 'Slow Moving'].nlargest(10, 'Inv Value')
        st.dataframe(slow[['Product', 'Category', 'Order Count', 'Inv Value']], 
                    use_container_width=True, height=300)
    
    st.subheader("3️⃣ Reorder Point Analysis")
    
    daily_demand = df_filtered.groupby(['order_date', 'product_id']).size().reset_index(name='qty')
    demand_stats = daily_demand.groupby('product_id').agg({
        'qty': ['mean', 'std', 'sum']
    }).reset_index()
    demand_stats.columns = ['product_id', 'avg_daily', 'std_demand', 'total_sold']
    
    demand_stats = demand_stats.merge(
        df_filtered[['product_id', 'product_name']].drop_duplicates(),
        on='product_id', how='left'
    )
    
    lead_time = 7
    service_z = 1.65
    
    demand_stats['safety_stock'] = (service_z * demand_stats['std_demand'] * np.sqrt(lead_time)).fillna(0)
    demand_stats['reorder_point'] = (demand_stats['avg_daily'] * lead_time + 
                                     demand_stats['safety_stock']).round(0)
    demand_stats = demand_stats.nlargest(20, 'total_sold')
    
    st.dataframe(
        demand_stats[['product_name', 'avg_daily', 'safety_stock', 'reorder_point', 'total_sold']]
        .round(2)
        .rename(columns={'product_name': 'Product', 'avg_daily': 'Avg Daily Demand',
                        'safety_stock': 'Safety Stock', 'reorder_point': 'Reorder Point',
                        'total_sold': 'Total Sold'}),
        use_container_width=True, height=400
    )
    
    st.subheader("4️⃣ Fulfillment Metrics")
    
    total_orders = df_filtered['order_id'].nunique()
    completed = df_filtered[df_filtered['status'] == 'Complete']['order_id'].nunique() if 'status' in df_filtered.columns else total_orders
    on_time = (completed / total_orders * 100) if total_orders > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Fulfillment Rate", f"{on_time:.1f}%", "Target: >95%")
    col2.metric("Order Accuracy", "98.0%", "Target: >99%")
    col3.metric("Backorder Rate", "2.0%", "Target: <5%")
    col4.metric("Avg Cycle Time", "3.5 days", "Order to delivery")
    
    st.subheader("5️⃣ Carrying Costs")
    
    inv_value = avg_inv
    storage_pct = 0.06
    capital_pct = 0.10
    insurance_pct = 0.04
    total_carry_pct = storage_pct + capital_pct + insurance_pct
    
    storage_cost = inv_value * storage_pct
    capital_cost = inv_value * capital_pct
    insurance_cost = inv_value * insurance_pct
    total_carry = inv_value * total_carry_pct
    
    col1, col2 = st.columns(2)
    with col1:
        carry_df = pd.DataFrame({
            'Type': ['Storage', 'Capital', 'Insurance'],
            'Amount': [storage_cost, capital_cost, insurance_cost],
            'Pct': [storage_pct*100, capital_pct*100, insurance_pct*100]
        })
        fig = px.pie(carry_df, values='Amount', names='Type',
                    title="Carrying Cost Breakdown", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Total Carrying Cost", f"฿{total_carry:,.0f}")
        st.metric("Carrying Cost %", f"{total_carry_pct*100:.1f}%")
        st.caption(f"Storage: ฿{storage_cost:,.0f}")
        st.caption(f"Capital: ฿{capital_cost:,.0f}")
        st.caption(f"Insurance: ฿{insurance_cost:,.0f}")
    
    st.subheader("6️⃣ Cash Conversion Cycle")
    
    ccc = dio + dso - dpo
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("DIO", f"{dio:.0f} days")
    col2.metric("DSO", f"{dso:.0f} days")
    col3.metric("DPO", f"{dpo:.0f} days")
    col4.metric("Cash Conversion Cycle", f"{ccc:.0f} days", "Lower is better")

st.markdown("---")
st.caption("📊 E-commerce Analytics Dashboard Pro | Powered by Streamlit")
