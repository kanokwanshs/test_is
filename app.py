# # app.py - E-commerce Analytics Dashboard Pro (Complete Version)
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# import numpy as np
# import warnings
# import zipfile
# import io

# warnings.filterwarnings('ignore')
# st.set_page_config(page_title="E-commerce Analytics Pro", layout="wide", page_icon="📊")

# if 'data_loaded' not in st.session_state:
#     st.session_state.data_loaded = False
# if 'data' not in st.session_state:
#     st.session_state.data = None

# def get_channel_type(channel):
#     online = ['line shopping', 'lazada', 'shopee', 'tiktok']
#     offline = ['siam center']
#     ch = str(channel).lower()
#     if any(o in ch for o in online): return 'Online'
#     if any(o in ch for o in offline): return 'Offline'
#     return 'Other'

# def upload_data():
#     st.sidebar.title("📊 E-commerce Analytics Pro")
#     st.sidebar.markdown("---")
#     method = st.sidebar.radio("📁 Data Source", ["Upload ZIP File", "Load from Folder Path"])
    
#     if method == "Upload ZIP File":
#         st.sidebar.subheader("Upload ZIP containing CSV files")
#         uploaded = st.sidebar.file_uploader("Choose ZIP file", type=['zip'])
        
#         if uploaded and st.sidebar.button("🔄 Load Data", type="primary"):
#             try:
#                 with zipfile.ZipFile(io.BytesIO(uploaded.read())) as z:
#                     data = {}
#                     mapping = {"users.csv": "user","customers.csv": "user", "products.csv": "product", "orders.csv": "order", 
#                               "order_items.csv": "order_item", "events.csv": "event"}
                    
#                     for fname in z.namelist():
#                         base = fname.split('/')[-1]
#                         if base in mapping:
#                             with z.open(fname) as f:
#                                 data[mapping[base]] = pd.read_csv(f)
#                             st.sidebar.success(f"✅ {base}")
                    
#                     if all(k in data for k in ['user', 'product', 'order', 'order_item']):
#                         st.session_state.data = data
#                         st.session_state.data_loaded = True
#                         st.sidebar.success("✅ All data loaded!")
#                         st.rerun()
#                     else:
#                         st.sidebar.error("❌ Missing required files")
#             except Exception as e:
#                 st.sidebar.error(f"❌ Error: {str(e)}")
#     else:
#         path = st.sidebar.text_input("Folder path", value="data")
#         if st.sidebar.button("🔄 Load Data", type="primary"):
#             try:
#                 import os
#                 data = {}
#                 mapping = {"users.csv": "user","customers.csv": "user", "products.csv": "product", "orders.csv": "order", "order_items.csv": "order_item"}
                
#                 for fname, key in mapping.items():
#                     fp = os.path.join(path, fname)
#                     if os.path.exists(fp):
#                         data[key] = pd.read_csv(fp)
#                         st.sidebar.success(f"✅ {fname}")
                
#                 if all(k in data for k in ['user', 'product', 'order', 'order_item']):
#                     st.session_state.data = data
#                     st.session_state.data_loaded = True
#                     st.rerun()
#                 else:
#                     st.sidebar.error("❌ Missing required files")
#             except Exception as e:
#                 st.sidebar.error(f"❌ Error: {str(e)}")
    
#     return st.session_state.data if st.session_state.data_loaded else None

# @st.cache_data
# def merge_data(data):
#     df = data['order_item'].copy()
    
#     if 'order_id' in data['order'].columns:
#         df = df.merge(data['order'], on='order_id', how='left', suffixes=('', '_o'))
#     if 'product_id' in data['product'].columns:
#         df = df.merge(data['product'], on='product_id', how='left', suffixes=('', '_p'))
#     if 'user_id' in data['user'].columns:
#         df = df.merge(data['user'], on='user_id', how='left', suffixes=('', '_u'))

#     # 🔧 FIX USER_ID (สำคัญมาก)
#     if 'user_id' not in df.columns:
#         if 'customer_id' in df.columns:
#             df['user_id'] = df['customer_id']
#         elif 'buyer_user_id' in df.columns:
#             df['user_id'] = df['buyer_user_id']
#         elif 'user_id_o' in df.columns:
#             df['user_id'] = df['user_id_o']
#         else:
#             df['user_id'] = 'UNKNOWN_USER'
    
#     defaults = {
#         'channel': 'Unknown',
#         'discount_pct': 0.0,
#         'status': 'Complete',
#         'traffic_source': 'Unknown',
#         'product_category': 'Other',
#         'product_name': 'Unknown',
#         'cost': 0,
#         'sale_price': 0
#     }
#     for col, val in defaults.items():
#         if col not in df.columns:
#             df[col] = val
    
#     if df['cost'].sum() == 0 and 'sale_price' in df.columns:
#         df['cost'] = df['sale_price'] * 0.6
    
#     for col in ['created_at', 'shipped_at', 'delivered_at']:
#         if col in df.columns:
#             df[col] = pd.to_datetime(df[col], errors='coerce')
    
#     if 'created_at' not in df.columns:
#         df['created_at'] = pd.Timestamp.now()
    
#     df['profit'] = df['sale_price'] - df['cost']
#     df['order_date'] = df['created_at'].dt.date
#     df['order_month'] = df['created_at'].dt.to_period('M')
#     df['order_year'] = df['created_at'].dt.year
#     df['channel_type'] = df['channel'].apply(get_channel_type)
    
#     return df

# data = upload_data()

# if not data:
#     st.title("📊 E-commerce Analytics Dashboard Pro")
#     st.info("👈 Please load your data in the sidebar to begin analysis")
#     st.markdown("""
#     ### Required Files:
#     - ✅ **users.csv** - User information
#     - ✅ **products.csv** - Product catalog
#     - ✅ **orders.csv** - Order details
#     - ✅ **order_items.csv** - Order line items
#     """)
#     st.stop()

# df_master = merge_data(data)

# st.sidebar.markdown("---")
# st.sidebar.success(f"✅ {len(df_master):,} transactions")
# st.sidebar.metric("Total Revenue", f"฿{df_master['sale_price'].sum():,.0f}")
# st.sidebar.metric("Total Profit", f"฿{df_master['profit'].sum():,.0f}")

# # Date Filter
# min_date = df_master['created_at'].min().date()
# max_date = df_master['created_at'].max().date()
# date_range = st.date_input("📅 Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# if len(date_range) == 2:
#     df_filtered = df_master[(df_master['created_at'].dt.date >= date_range[0]) & 
#                             (df_master['created_at'].dt.date <= date_range[1])]
# else:
#     df_filtered = df_master

# # Tabs
# tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Executive", "💼 Sales", "📢 Marketing", "💰 Financial", "📦 Warehouse"])

# # # TAB 1: EXECUTIVE DASHBOARD
# # with tab1:
# #     st.header("📊 Executive Dashboard")
    
# #     col1, col2, col3, col4 = st.columns(4)
# #     revenue = df_filtered['sale_price'].sum()
# #     profit = df_filtered['profit'].sum()
# #     margin = (profit/revenue*100) if revenue > 0 else 0
    
# #     col1.metric("Total Revenue", f"฿{revenue:,.0f}")
# #     col2.metric("Total Profit", f"฿{profit:,.0f}", f"{margin:.1f}%")
# #     col3.metric("Active Customers", f"{df_filtered['user_id'].nunique():,}")
# #     col4.metric("Avg Order Value", f"฿{df_filtered['sale_price'].mean():,.2f}")
    
# #     st.subheader("📈 Sales Trend Overview")
# #     daily = df_filtered.groupby('order_date').agg({'sale_price': 'sum', 'profit': 'sum'}).reset_index()
# #     daily['order_date'] = pd.to_datetime(daily['order_date'])
    
# #     fig = go.Figure()
# #     fig.add_trace(go.Scatter(x=daily['order_date'], y=daily['sale_price'], name='Revenue', 
# #                             line=dict(color='#3498db', width=2), fill='tozeroy'))
# #     fig.add_trace(go.Scatter(x=daily['order_date'], y=daily['profit'], name='Profit',
# #                             line=dict(color='#2ecc71', width=2), yaxis='y2'))
# #     fig.update_layout(yaxis=dict(title="Revenue (฿)"), 
# #                      yaxis2=dict(title="Profit (฿)", overlaying='y', side='right'), height=400)
# #     st.plotly_chart(fig, use_container_width=True)
    
# #     col1, col2, col3 = st.columns(3)
# #     with col1:
# #         st.subheader("🏆 Top Category")
# #         cat = df_filtered.groupby('product_category')['sale_price'].sum().nlargest(1)
# #         if len(cat) > 0:
# #             st.metric(cat.index[0], f"฿{cat.values[0]:,.0f}")
    
# #     with col2:
# #         st.subheader("📱 Best Channel")
# #         ch = df_filtered.groupby('channel_type')['sale_price'].sum().nlargest(1)
# #         if len(ch) > 0:
# #             st.metric(ch.index[0], f"฿{ch.values[0]:,.0f}")
    
# #     with col3:
# #         st.subheader("🎯 Conversion")
# #         users = df_filtered['user_id'].nunique()
# #         orders = df_filtered['order_id'].nunique()
# #         st.metric("Orders per Customer", f"{(orders/users):.2f}" if users > 0 else "0")

# # TAB 1: EXECUTIVE DASHBOARD
# with tab1:
#     st.header("📊 Executive Dashboard")
    
#     # =====================
#     # KPI SUMMARY
#     # =====================
#     col1, col2, col3, col4 = st.columns(4)
    
#     revenue = df_filtered['sale_price'].sum()
#     profit = df_filtered['profit'].sum()
#     margin = (profit / revenue * 100) if revenue > 0 else 0
    
#     col1.metric("Total Revenue", f"฿{revenue:,.0f}")
#     col2.metric("Profit Margin", f"{margin:.1f}%", f"฿{profit:,.0f}")
#     col3.metric("Active Customers", f"{df_filtered['user_id'].nunique():,}")
#     col4.metric("Avg Order Value", f"฿{df_filtered['sale_price'].mean():,.2f}")
    
#     # =====================
#     # SALES TREND OVERVIEW
#     # =====================
#     st.subheader("📈 Sales Trend Overview")
    
#     daily = df_filtered.groupby('order_date').agg({
#         'sale_price': 'sum',
#         'profit': 'sum'
#     }).reset_index()
    
#     daily['order_date'] = pd.to_datetime(daily['order_date'])
#     daily['margin_pct'] = np.where(
#         daily['sale_price'] > 0,
#         daily['profit'] / daily['sale_price'] * 100,
#         0
#     )
    
#     fig = go.Figure()
    
#     # Revenue (฿)
#     fig.add_trace(go.Scatter(
#         x=daily['order_date'],
#         y=daily['sale_price'],
#         name='Revenue',
#         line=dict(color='#3498db', width=2),
#         fill='tozeroy'
#     ))
    
#     # Profit Margin (%)
#     fig.add_trace(go.Scatter(
#         x=daily['order_date'],
#         y=daily['margin_pct'],
#         name='Profit Margin (%)',
#         yaxis='y2',
#         mode='lines+markers',
#         line=dict(color='#2ecc71', width=3)
#     ))
    
#     fig.update_layout(
#     yaxis=dict(
#         title="Revenue (฿)"
#     ),
#     yaxis2=dict(
#         title="Profit Margin (%)",
#         overlaying='y',
#         side='right',
#         ticksuffix='%',
#         range=[0, 100]   # 👈 FIX SCALE 0–100%
#     ),
#     height=400,
#     legend=dict(orientation="h", y=1.15)
#     )
    
#     st.plotly_chart(fig, use_container_width=True)
    
#     # =====================
#     # HIGHLIGHTS
#     # =====================
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
#         st.metric("Orders per Customer", f"{(orders / users):.2f}" if users > 0 else "0")


# # TAB 2: SALES ANALYTICS
# with tab2:
#     st.header("💼 Sales Analytics")
    
#     st.subheader("1️⃣ Common Sales KPIs")
    
#     monthly = df_filtered.groupby('order_month').agg({'sale_price': 'sum', 'profit': 'sum'}).reset_index()
#     monthly['order_month'] = monthly['order_month'].dt.to_timestamp()
#     monthly = monthly.sort_values('order_month')
    
#     growth = 0
#     if len(monthly) >= 2:
#         curr = monthly.iloc[-1]['sale_price']
#         prev = monthly.iloc[-2]['sale_price']
#         growth = ((curr - prev) / prev * 100) if prev > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("Monthly Growth", f"{growth:+.2f}%")
#     col2.metric("Profit Margin", f"{margin:.2f}%")
    
#     target = 1000000
#     curr_sales = df_filtered[df_filtered['order_month'] == df_filtered['order_month'].max()]['sale_price'].sum()
#     attainment = (curr_sales / target * 100) if target > 0 else 0
#     col3.metric("Target Attainment", f"{attainment:.1f}%")
#     col4.metric("Avg Purchase", f"฿{df_filtered['sale_price'].mean():,.2f}")
    
#     st.subheader("2️⃣ Sales by Channel")
#     ch_sales = df_filtered.groupby('channel').agg({'sale_price': 'sum', 'order_id': 'nunique', 
#                                                     'user_id': 'nunique'}).reset_index()
#     ch_sales.columns = ['Channel', 'Revenue', 'Orders', 'Customers']
#     ch_sales['Revenue %'] = (ch_sales['Revenue'] / ch_sales['Revenue'].sum() * 100).round(2)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         fig = px.pie(ch_sales, values='Revenue', names='Channel', title="Revenue by Channel", hole=0.4)
#         st.plotly_chart(fig, use_container_width=True)
#     with col2:
#         fig = px.bar(ch_sales.sort_values('Revenue', ascending=True), x='Revenue', y='Channel',
#                     orientation='h', title="Revenue by Channel", text='Revenue %')
#         fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
#         st.plotly_chart(fig, use_container_width=True)
    
#     st.dataframe(ch_sales, use_container_width=True)
    
#     st.subheader("3️⃣ Customer Acquisition & Retention")
    
#     mkt_cost = df_filtered['discount_pct'].sum() * df_filtered['sale_price'].sum()
#     new_cust = df_filtered['user_id'].nunique()
#     cac = mkt_cost / new_cust if new_cust > 0 else 0
    
#     analysis_date = df_filtered['created_at'].max()
#     last_purchase = df_filtered.groupby('user_id')['created_at'].max()
#     days_since = (analysis_date - last_purchase).dt.days
#     churned = (days_since > 60).sum()
#     churn_rate = (churned / len(last_purchase) * 100) if len(last_purchase) > 0 else 0
#     retention_rate = 100 - churn_rate
    
#     avg_rev = df_filtered.groupby('user_id')['sale_price'].sum().mean()
#     clv = (margin/100) * (retention_rate/100) * avg_rev
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("CAC", f"฿{cac:,.2f}")
#     col2.metric("Retention Rate", f"{retention_rate:.2f}%")
#     col3.metric("Churn Rate", f"{churn_rate:.2f}%")
#     col4.metric("CLV", f"฿{clv:,.2f}")
    
#     st.subheader("4️⃣ Product Performance")
#     prod = df_filtered.groupby(['product_id', 'product_name', 'product_category']).agg({
#         'sale_price': 'sum', 'profit': 'sum', 'order_id': 'nunique'
#     }).reset_index()
#     prod.columns = ['ID', 'Product', 'Category', 'Revenue', 'Profit', 'Orders']
#     prod['Margin %'] = (prod['Profit'] / prod['Revenue'] * 100).round(2)
#     prod = prod.sort_values('Revenue', ascending=False).head(20)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         fig = px.bar(prod.head(10), x='Revenue', y='Product', orientation='h',
#                     title="Top 10 Products", color='Margin %', color_continuous_scale='RdYlGn')
#         st.plotly_chart(fig, use_container_width=True)
#     with col2:
#         fig = px.scatter(prod, x='Revenue', y='Profit', size='Orders', color='Category',
#                         hover_data=['Product'], title="Revenue vs Profit")
#         st.plotly_chart(fig, use_container_width=True)
    
#     st.dataframe(prod, use_container_width=True)

# # TAB 3: MARKETING ANALYTICS
# with tab3:
#     st.header("📢 Marketing Analytics")
    
#     st.subheader("1️⃣ Campaign Effectiveness")
    
#     camp = df_filtered[df_filtered['discount_pct'] > 0]
#     no_camp = df_filtered[df_filtered['discount_pct'] == 0]
    
#     camp_rev = camp['sale_price'].sum()
#     camp_share = (camp_rev / revenue * 100) if revenue > 0 else 0
#     conv_rate = (len(camp) / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
#     avg_disc = camp['discount_pct'].mean() * 100 if len(camp) > 0 else 0
#     camp_cac = (camp['discount_pct'] * camp['sale_price']).sum() / camp['user_id'].nunique() if len(camp) > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("Campaign Revenue %", f"{camp_share:.1f}%")
#     col2.metric("Campaign Conv Rate", f"{conv_rate:.1f}%")
#     col3.metric("Avg Discount", f"{avg_disc:.1f}%")
#     col4.metric("Campaign CAC", f"฿{camp_cac:,.2f}")
    
#     col1, col2 = st.columns(2)
#     with col1:
#         camp_aov = camp['sale_price'].mean() if len(camp) > 0 else 0
#         no_camp_aov = no_camp['sale_price'].mean() if len(no_camp) > 0 else 0
#         comp = pd.DataFrame({'Type': ['With Campaign', 'Without Campaign'], 
#                             'AOV': [camp_aov, no_camp_aov]})
#         fig = px.bar(comp, x='Type', y='AOV', title="AOV: Campaign Impact", 
#                     color='Type', text='AOV')
#         fig.update_traces(texttemplate='฿%{text:,.0f}', textposition='outside')
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         camp_profit = camp['profit'].sum()
#         camp_cost = (camp['discount_pct'] * camp['sale_price']).sum()
#         roas = (camp_rev / camp_cost * 100) if camp_cost > 0 else 0
#         st.metric("ROAS", f"{roas:.1f}%")
#         st.metric("Campaign Profit", f"฿{camp_profit:,.0f}")
#         st.metric("Campaign Cost", f"฿{camp_cost:,.0f}")
    
#     st.subheader("2️⃣ Traffic Source Performance")
    
#     traffic = df_filtered.groupby('traffic_source').agg({
#         'user_id': 'nunique', 'order_id': 'nunique', 'sale_price': 'sum', 'profit': 'sum'
#     }).reset_index()
#     traffic.columns = ['Source', 'Customers', 'Orders', 'Revenue', 'Profit']
#     traffic['Conv %'] = (traffic['Orders'] / traffic['Customers'] * 100).round(2)
#     traffic['Rev/Customer'] = (traffic['Revenue'] / traffic['Customers']).round(2)
#     traffic['Margin %'] = (traffic['Profit'] / traffic['Revenue'] * 100).round(2)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         fig = px.bar(traffic.sort_values('Revenue', ascending=True), x='Revenue', y='Source',
#                     orientation='h', title="Revenue by Source", color='Margin %',
#                     color_continuous_scale='Viridis')
#         st.plotly_chart(fig, use_container_width=True)
#     with col2:
#         fig = px.scatter(traffic, x='Customers', y='Rev/Customer', size='Revenue',
#                         color='Source', title="Customer Value by Source", hover_data=['Conv %'])
#         st.plotly_chart(fig, use_container_width=True)
    
#     st.dataframe(traffic.sort_values('Revenue', ascending=False), use_container_width=True)
    
#     st.subheader("3️⃣ RFM Analysis")
    
#     # rfm = df_filtered.groupby('user_id').agg({
#     #     'created_at': lambda x: (analysis_date - x.max()).days,
#     #     'order_id': 'nunique', 'sale_price': 'sum', 'profit': 'sum'
#     # }).reset_index()
#     # rfm.columns = ['user_id', 'recency', 'frequency', 'monetary', 'total_profit']
    
#     # rfm['R'] = pd.qcut(rfm['recency'], 4, labels=[4,3,2,1], duplicates='drop')
#     # rfm['F'] = pd.qcut(rfm['frequency'], 4, labels=[1,2,3,4], duplicates='drop')
#     # rfm['M'] = pd.qcut(rfm['monetary'], 4, labels=[1,2,3,4], duplicates='drop')
#     # rfm['RFM_Score'] = rfm['R'].astype(int) + rfm['F'].astype(int) + rfm['M'].astype(int)
    
#     # def segment(s):
#     #     if s >= 9: return 'Champions'
#     #     elif s >= 6: return 'Loyal'
#     #     elif s >= 4: return 'At Risk'
#     #     return 'Lost'
    
#     # rfm['Segment'] = rfm['RFM_Score'].apply(segment)
    
#     # col1, col2 = st.columns(2)
#     # with col1:
#     #     seg = rfm['Segment'].value_counts()
#     #     colors = {'Champions': '#2ecc71', 'Loyal': '#3498db', 'At Risk': '#f39c12', 'Lost': '#e74c3c'}
#     #     fig = px.pie(values=seg.values, names=seg.index, title="Customer Segments", 
#     #                 hole=0.4, color=seg.index, color_discrete_map=colors)
#     #     st.plotly_chart(fig, use_container_width=True)
    
#     # with col2:
#     #     seg_val = rfm.groupby('Segment')['monetary'].sum().sort_values(ascending=True)
#     #     fig = px.bar(x=seg_val.values, y=seg_val.index, orientation='h',
#     #                 title="Revenue by Segment", color=seg_val.index, color_discrete_map=colors)
#     #     st.plotly_chart(fig, use_container_width=True)
    
#     # seg_metrics = rfm.groupby('Segment').agg({
#     #     'user_id': 'count', 'recency': 'mean', 'frequency': 'mean',
#     #     'monetary': 'mean', 'total_profit': 'mean', 'RFM_Score': 'mean'
#     # }).round(2)
#     # seg_metrics.columns = ['Customers', 'Avg Recency', 'Avg Frequency', 
#     #                       'Avg Revenue', 'Avg Profit', 'Avg RFM Score']
#     # st.dataframe(seg_metrics, use_container_width=True)
# st.subheader("3️⃣ RFM Analysis")

# rfm = df_filtered.groupby('user_id').agg({
#     'created_at': lambda x: (analysis_date - x.max()).days,
#     'order_id': 'nunique',
#     'sale_price': 'sum',
#     'profit': 'sum'
# }).reset_index()

# rfm.columns = ['user_id', 'recency', 'frequency', 'monetary', 'total_profit']

# # =========================
# # SAFE QCUT FUNCTION
# # =========================
# def safe_qcut(series, q, labels):
#     try:
#         bins = pd.qcut(series.rank(method='first'), q=q, duplicates='drop')
#         n_bins = bins.cat.categories.size
#         return pd.qcut(
#             series.rank(method='first'),
#             q=n_bins,
#             labels=labels[:n_bins]
#         )
#     except Exception:
#         return pd.Series([labels[0]] * len(series), index=series.index)

# # Apply RFM scoring safely
# rfm['R'] = safe_qcut(rfm['recency'], 4, [4,3,2,1])
# rfm['F'] = safe_qcut(rfm['frequency'], 4, [1,2,3,4])
# rfm['M'] = safe_qcut(rfm['monetary'], 4, [1,2,3,4])

# rfm['RFM_Score'] = rfm[['R','F','M']].astype(int).sum(axis=1)

# def segment(score):
#     if score >= 9:
#         return 'Champions'
#     elif score >= 6:
#         return 'Loyal'
#     elif score >= 4:
#         return 'At Risk'
#     return 'Lost'

# rfm['Segment'] = rfm['RFM_Score'].apply(segment)

# # TAB 4: FINANCIAL ANALYTICS
# with tab4:
#     st.header("💰 Financial Analytics")
    
#     st.subheader("1️⃣ Financial KPIs")
    
#     total_rev = df_filtered['sale_price'].sum()
#     total_cogs = df_filtered['cost'].sum()
#     gross_profit = total_rev - total_cogs
#     net_profit = df_filtered['profit'].sum()
#     gross_margin = (gross_profit / total_rev * 100) if total_rev > 0 else 0
#     net_margin = (net_profit / total_rev * 100) if total_rev > 0 else 0
    
#     col1, col2, col3, col4, col5 = st.columns(5)
#     col1.metric("Revenue", f"฿{total_rev:,.0f}")
#     col2.metric("COGS", f"฿{total_cogs:,.0f}")
#     col3.metric("Gross Profit", f"฿{gross_profit:,.0f}", f"{gross_margin:.1f}%")
#     col4.metric("Net Profit", f"฿{net_profit:,.0f}", f"{net_margin:.1f}%")
#     col5.metric("ROS", f"{net_margin:.2f}%")
    
#     st.subheader("2️⃣ AR/AP Turnover")
    
#     monthly_fin = df_filtered.groupby('order_month').agg({
#         'sale_price': 'sum', 'cost': 'sum', 'profit': 'sum'
#     }).reset_index()
    
#     avg_monthly_rev = monthly_fin['sale_price'].mean()
#     avg_ar = avg_monthly_rev * 0.3
#     net_credit = total_rev * 0.3
#     ar_turnover = net_credit / avg_ar if avg_ar > 0 else 0
#     dso = 365 / ar_turnover if ar_turnover > 0 else 0
    
#     avg_ap = total_cogs * 0.25
#     ap_turnover = total_cogs / avg_ap if avg_ap > 0 else 0
#     dpo = 365 / ap_turnover if ap_turnover > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("AR Turnover", f"{ar_turnover:.2f}x")
#     col2.metric("DSO", f"{dso:.0f} days")
#     col3.metric("AP Turnover", f"{ap_turnover:.2f}x")
#     col4.metric("DPO", f"{dpo:.0f} days")
    
#     st.subheader("3️⃣ Monthly Performance")
    
#     monthly_fin['order_month'] = monthly_fin['order_month'].dt.to_timestamp()
#     monthly_fin['margin_%'] = (monthly_fin['profit'] / monthly_fin['sale_price'] * 100).round(2)
    
#     fig = go.Figure()
#     fig.add_trace(go.Bar(x=monthly_fin['order_month'], y=monthly_fin['sale_price'],
#                         name='Revenue', marker_color='lightblue'))
#     fig.add_trace(go.Bar(x=monthly_fin['order_month'], y=monthly_fin['cost'],
#                         name='COGS', marker_color='lightcoral'))
#     fig.add_trace(go.Scatter(x=monthly_fin['order_month'], y=monthly_fin['margin_%'],
#                             name='Margin %', yaxis='y2', mode='lines+markers',
#                             line=dict(color='green', width=3)))
#     fig.update_layout(yaxis=dict(title="Amount (฿)"),
#                      yaxis2=dict(title="Margin (%)", overlaying='y', side='right'),
#                      barmode='group', height=400)
#     st.plotly_chart(fig, use_container_width=True)
    
#     st.subheader("4️⃣ Channel Profitability")
    
#     ch_fin = df_filtered.groupby(['channel', 'channel_type']).agg({
#         'sale_price': 'sum', 'cost': 'sum', 'profit': 'sum', 'order_id': 'nunique'
#     }).reset_index()
#     ch_fin.columns = ['Channel', 'Type', 'Revenue', 'COGS', 'Profit', 'Orders']
#     ch_fin['Margin %'] = (ch_fin['Profit'] / ch_fin['Revenue'] * 100).round(2)
#     ch_fin['AOV'] = (ch_fin['Revenue'] / ch_fin['Orders']).round(2)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         fig = px.bar(ch_fin.sort_values('Profit', ascending=True), x='Profit', y='Channel',
#                     orientation='h', title="Profit by Channel", color='Margin %',
#                     color_continuous_scale='RdYlGn')
#         st.plotly_chart(fig, use_container_width=True)
#     with col2:
#         fig = px.scatter(ch_fin, x='Revenue', y='Profit', size='Orders', color='Type',
#                         text='Channel', title="Revenue vs Profit")
#         fig.update_traces(textposition='top center')
#         st.plotly_chart(fig, use_container_width=True)
    
#     st.dataframe(ch_fin, use_container_width=True)
    
#     st.subheader("5️⃣ Growth Analysis")
    
#     if len(monthly_fin) >= 2:
#         monthly_fin['growth_%'] = monthly_fin['sale_price'].pct_change() * 100
#         fig = px.line(monthly_fin, x='order_month', y='growth_%',
#                      title="Monthly Growth Rate", markers=True)
#         fig.add_hline(y=0, line_dash="dash", line_color="red")
#         fig.update_traces(line_color='#3498db', line_width=3)
#         st.plotly_chart(fig, use_container_width=True)
        
#         avg_growth = monthly_fin['growth_%'].mean()
#         st.info(f"📊 Average Monthly Growth: **{avg_growth:.2f}%**")

# # TAB 5: WAREHOUSE & INVENTORY
# with tab5:
#     st.header("📦 Warehouse & Inventory")
    
#     st.subheader("1️⃣ Inventory Metrics")
    
#     total_cogs = df_filtered['cost'].sum()
#     avg_inv = df_filtered['cost'].mean() * df_filtered['product_id'].nunique()
#     inv_turnover = total_cogs / avg_inv if avg_inv > 0 else 0
#     dio = 365 / inv_turnover if inv_turnover > 0 else 0
    
#     units_sold = len(df_filtered)
#     units_received = units_sold * 1.2
#     sell_through = (units_sold / units_received * 100) if units_received > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("Inventory Turnover", f"{inv_turnover:.2f}x")
#     col2.metric("DIO", f"{dio:.0f} days")
#     col3.metric("Sell-Through Rate", f"{sell_through:.1f}%")
#     col4.metric("Inventory Value", f"฿{avg_inv:,.0f}")
    
#     st.subheader("2️⃣ Product Movement")
    
#     prod_vel = df_filtered.groupby(['product_id', 'product_name', 'product_category']).agg({
#         'order_id': 'nunique', 'sale_price': 'sum', 'cost': 'sum'
#     }).reset_index()
#     prod_vel.columns = ['ID', 'Product', 'Category', 'Order Count', 'Revenue', 'Cost']
    
#     fast_threshold = prod_vel['Order Count'].quantile(0.75)
#     slow_threshold = prod_vel['Order Count'].quantile(0.25)
    
#     def classify_movement(cnt):
#         if cnt >= fast_threshold: return 'Fast Moving'
#         elif cnt <= slow_threshold: return 'Slow Moving'
#         return 'Medium Moving'
    
#     prod_vel['Movement'] = prod_vel['Order Count'].apply(classify_movement)
#     prod_vel['Inv Value'] = prod_vel['Cost']
    
#     col1, col2 = st.columns(2)
#     with col1:
#         mov_dist = prod_vel['Movement'].value_counts()
#         colors_mov = {'Fast Moving': '#2ecc71', 'Medium Moving': '#f39c12', 'Slow Moving': '#e74c3c'}
#         fig = px.pie(values=mov_dist.values, names=mov_dist.index,
#                     title="Product Movement Distribution", hole=0.4,
#                     color=mov_dist.index, color_discrete_map=colors_mov)
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         mov_val = prod_vel.groupby('Movement')['Inv Value'].sum().sort_values(ascending=True)
#         fig = px.bar(x=mov_val.values, y=mov_val.index, orientation='h',
#                     title="Inventory Value by Movement",
#                     color=mov_val.index, color_discrete_map=colors_mov)
#         st.plotly_chart(fig, use_container_width=True)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         st.markdown("#### 🚀 Top 10 Fast Moving")
#         fast = prod_vel[prod_vel['Movement'] == 'Fast Moving'].nlargest(10, 'Order Count')
#         st.dataframe(fast[['Product', 'Category', 'Order Count', 'Revenue']], 
#                     use_container_width=True, height=300)
    
#     with col2:
#         st.markdown("#### 🐌 Top 10 Slow Moving")
#         slow = prod_vel[prod_vel['Movement'] == 'Slow Moving'].nlargest(10, 'Inv Value')
#         st.dataframe(slow[['Product', 'Category', 'Order Count', 'Inv Value']], 
#                     use_container_width=True, height=300)
    
#     st.subheader("3️⃣ Reorder Point Analysis")
    
#     daily_demand = df_filtered.groupby(['order_date', 'product_id']).size().reset_index(name='qty')
#     demand_stats = daily_demand.groupby('product_id').agg({
#         'qty': ['mean', 'std', 'sum']
#     }).reset_index()
#     demand_stats.columns = ['product_id', 'avg_daily', 'std_demand', 'total_sold']
    
#     demand_stats = demand_stats.merge(
#         df_filtered[['product_id', 'product_name']].drop_duplicates(),
#         on='product_id', how='left'
#     )
    
#     lead_time = 7
#     service_z = 1.65
    
#     demand_stats['safety_stock'] = (service_z * demand_stats['std_demand'] * np.sqrt(lead_time)).fillna(0)
#     demand_stats['reorder_point'] = (demand_stats['avg_daily'] * lead_time + 
#                                      demand_stats['safety_stock']).round(0)
#     demand_stats = demand_stats.nlargest(20, 'total_sold')
    
#     st.dataframe(
#         demand_stats[['product_name', 'avg_daily', 'safety_stock', 'reorder_point', 'total_sold']]
#         .round(2)
#         .rename(columns={'product_name': 'Product', 'avg_daily': 'Avg Daily Demand',
#                         'safety_stock': 'Safety Stock', 'reorder_point': 'Reorder Point',
#                         'total_sold': 'Total Sold'}),
#         use_container_width=True, height=400
#     )
    
#     st.subheader("4️⃣ Fulfillment Metrics")
    
#     total_orders = df_filtered['order_id'].nunique()
#     completed = df_filtered[df_filtered['status'] == 'Complete']['order_id'].nunique() if 'status' in df_filtered.columns else total_orders
#     on_time = (completed / total_orders * 100) if total_orders > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("Fulfillment Rate", f"{on_time:.1f}%", "Target: >95%")
#     col2.metric("Order Accuracy", "98.0%", "Target: >99%")
#     col3.metric("Backorder Rate", "2.0%", "Target: <5%")
#     col4.metric("Avg Cycle Time", "3.5 days", "Order to delivery")
    
#     st.subheader("5️⃣ Carrying Costs")
    
#     inv_value = avg_inv
#     storage_pct = 0.06
#     capital_pct = 0.10
#     insurance_pct = 0.04
#     total_carry_pct = storage_pct + capital_pct + insurance_pct
    
#     storage_cost = inv_value * storage_pct
#     capital_cost = inv_value * capital_pct
#     insurance_cost = inv_value * insurance_pct
#     total_carry = inv_value * total_carry_pct
    
#     col1, col2 = st.columns(2)
#     with col1:
#         carry_df = pd.DataFrame({
#             'Type': ['Storage', 'Capital', 'Insurance'],
#             'Amount': [storage_cost, capital_cost, insurance_cost],
#             'Pct': [storage_pct*100, capital_pct*100, insurance_pct*100]
#         })
#         fig = px.pie(carry_df, values='Amount', names='Type',
#                     title="Carrying Cost Breakdown", hole=0.4)
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         st.metric("Total Carrying Cost", f"฿{total_carry:,.0f}")
#         st.metric("Carrying Cost %", f"{total_carry_pct*100:.1f}%")
#         st.caption(f"Storage: ฿{storage_cost:,.0f}")
#         st.caption(f"Capital: ฿{capital_cost:,.0f}")
#         st.caption(f"Insurance: ฿{insurance_cost:,.0f}")
    
#     st.subheader("6️⃣ Cash Conversion Cycle")
    
#     ccc = dio + dso - dpo
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("DIO", f"{dio:.0f} days")
#     col2.metric("DSO", f"{dso:.0f} days")
#     col3.metric("DPO", f"{dpo:.0f} days")
#     col4.metric("Cash Conversion Cycle", f"{ccc:.0f} days", "Lower is better")

# st.markdown("---")
# st.caption("📊 E-commerce Analytics Dashboard Pro | Powered by Streamlit")








































































































































































































# # Fashion E-commerce Analytics Dashboard
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# import numpy as np
# import warnings

# warnings.filterwarnings('ignore')
# st.set_page_config(page_title="Fashion Analytics Pro", layout="wide", page_icon="👕")

# if 'data_loaded' not in st.session_state:
#     st.session_state.data_loaded = False
# if 'data' not in st.session_state:
#     st.session_state.data = {}

# REQUIRED_COLUMNS = {
#     'users': ['user_id', 'customer_type', 'created_at'],
#     'products': ['product_id', 'category', 'sale_price', 'cost'],
#     'orders': ['order_id', 'user_id', 'order_date', 'channel', 'status'],
#     'order_items': ['order_id', 'product_id', 'quantity', 'net_revenue', 'cost', 'profit']
# }

# def load_data():
#     st.sidebar.title("👕 Fashion Analytics Pro")
#     st.sidebar.markdown("---")
    
#     uploaded = st.sidebar.file_uploader("📁 Upload CSV Files", type=['csv'], accept_multiple_files=True)
    
#     if uploaded and st.sidebar.button("🔄 Load Data", type="primary"):
#         data = {}
#         mapping = {"users.csv": "users", "products.csv": "products", "orders.csv": "orders", 
#                    "order_items.csv": "order_items", "inventory_movements.csv": "inventory"}
        
#         for file in uploaded:
#             if file.name in mapping:
#                 try:
#                     df = pd.read_csv(file)
#                     table = mapping[file.name]
#                     if table in REQUIRED_COLUMNS:
#                         missing = [c for c in REQUIRED_COLUMNS[table] if c not in df.columns]
#                         if not missing:
#                             data[table] = df
#                             st.sidebar.success(f"✅ {file.name}")
#                         else:
#                             st.sidebar.error(f"❌ {file.name} - Missing: {', '.join(missing)}")
#                     else:
#                         data[table] = df
#                         st.sidebar.success(f"✅ {file.name}")
#                 except Exception as e:
#                     st.sidebar.error(f"❌ {file.name}: {str(e)}")
        
#         if all(t in data for t in ['users', 'products', 'orders', 'order_items']):
#             st.session_state.data = data
#             st.session_state.data_loaded = True
#             st.sidebar.success("✅ All data loaded!")
#             st.rerun()
#         else:
#             st.sidebar.error("❌ Missing required tables")
    
#     return st.session_state.data if st.session_state.data_loaded else None

# @st.cache_data
# def merge_data(data):
#     df = data['order_items'].copy()
#     df = df.merge(data['orders'], on='order_id', how='left', suffixes=('', '_o'))
#     df = df.merge(data['products'], on='product_id', how='left', suffixes=('', '_p'))
#     df = df.merge(data['users'], on='user_id', how='left', suffixes=('', '_u'))
    
#     for col in ['order_date', 'created_at']:
#         if col in df.columns:
#             df[col] = pd.to_datetime(df[col], errors='coerce')
    
#     if 'order_date' in df.columns:
#         df['order_month'] = df['order_date'].dt.to_period('M')
#         df['order_year'] = df['order_date'].dt.year
    
#     online = ['Shopee', 'Lazada', 'TikTok', 'LINE Shopping']
#     df['channel_type'] = df['channel'].apply(lambda x: 'Online' if x in online else 'Offline')
    
#     return df

# data = load_data()

# if not data:
#     st.title("👕 Fashion E-commerce Analytics Dashboard")
#     st.info("👈 Please upload CSV files to begin")
    
#     st.markdown("### 📋 Required Columns")
#     col1, col2 = st.columns(2)
#     with col1:
#         st.code("users.csv:\n- user_id\n- customer_type\n- created_at")
#         st.code("orders.csv:\n- order_id\n- user_id\n- order_date\n- channel\n- status")
#     with col2:
#         st.code("products.csv:\n- product_id\n- category\n- sale_price\n- cost")
#         st.code("order_items.csv:\n- order_id\n- product_id\n- quantity\n- net_revenue\n- cost\n- profit")
#     st.stop()

# df_master = merge_data(data)

# st.sidebar.markdown("---")
# st.sidebar.success(f"✅ {len(df_master):,} transactions")

# min_date = df_master['order_date'].min().date()
# max_date = df_master['order_date'].max().date()
# date_range = st.sidebar.date_input("📅 Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# if len(date_range) == 2:
#     df_filtered = df_master[(df_master['order_date'].dt.date >= date_range[0]) & 
#                             (df_master['order_date'].dt.date <= date_range[1])]
# else:
#     df_filtered = df_master

# channels = st.sidebar.multiselect("Channel", df_filtered['channel'].unique(), df_filtered['channel'].unique())
# df_filtered = df_filtered[df_filtered['channel'].isin(channels)]

# statuses = st.sidebar.multiselect("Status", df_filtered['status'].unique(), ['Completed'])
# df_filtered = df_filtered[df_filtered['status'].isin(statuses)]

# st.sidebar.markdown("---")
# st.sidebar.metric("Revenue", f"฿{df_filtered['net_revenue'].sum():,.0f}")
# st.sidebar.metric("Profit", f"฿{df_filtered['profit'].sum():,.0f}")

# tab1, tab2, tab3, tab4 = st.tabs(["💼 Sales", "📢 Marketing", "💰 Financial", "📦 Warehouse"])

# with tab1:
#     st.header("💼 Sales Analytics")
    
#     st.subheader("1️⃣ KPIs")
    
#     revenue = df_filtered['net_revenue'].sum()
#     profit = df_filtered['profit'].sum()
#     margin = (profit / revenue * 100) if revenue > 0 else 0
    
#     monthly = df_filtered.groupby('order_month')['net_revenue'].sum().sort_index()
#     growth = ((monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2] * 100) if len(monthly) >= 2 else 0
    
#     aov = df_filtered.groupby('order_id')['net_revenue'].sum().mean()
#     target = 5000000
#     curr_sales = df_filtered[df_filtered['order_month'] == df_filtered['order_month'].max()]['net_revenue'].sum()
#     attainment = (curr_sales / target * 100) if target > 0 else 0
    
#     col1, col2, col3, col4, col5 = st.columns(5)
#     col1.metric("Monthly Growth", f"{growth:+.1f}%")
#     col2.metric("Profit Margin", f"{margin:.1f}%")
#     col3.metric("Target", f"{attainment:.1f}%")
#     col4.metric("AOV", f"฿{aov:,.0f}")
#     col5.metric("Customers", f"{df_filtered['user_id'].nunique():,}")
    
#     st.subheader("2️⃣ Sales Trend")
    
#     daily = df_filtered.groupby('order_date').agg({'net_revenue': 'sum', 'profit': 'sum'}).reset_index()
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=daily['order_date'], y=daily['net_revenue'], name='Revenue', fill='tozeroy'))
#     fig.add_trace(go.Scatter(x=daily['order_date'], y=daily['profit'], name='Profit', yaxis='y2'))
#     fig.update_layout(yaxis=dict(title="Revenue"), yaxis2=dict(title="Profit", overlaying='y', side='right'), height=400)
#     st.plotly_chart(fig, use_container_width=True)
    
#     st.subheader("3️⃣ Channel Performance")
    
#     ch = df_filtered.groupby('channel').agg({'net_revenue': 'sum', 'profit': 'sum', 'order_id': 'nunique', 'user_id': 'nunique'}).reset_index()
#     ch.columns = ['Channel', 'Revenue', 'Profit', 'Orders', 'Customers']
#     ch['Margin %'] = (ch['Profit'] / ch['Revenue'] * 100).round(1)
#     ch = ch.sort_values('Revenue', ascending=False)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         fig = px.pie(ch, values='Revenue', names='Channel', title="Revenue by Channel", hole=0.4)
#         st.plotly_chart(fig, use_container_width=True)
#     with col2:
#         fig = px.bar(ch.sort_values('Revenue', ascending=True), x='Revenue', y='Channel', orientation='h', 
#                     color='Margin %', color_continuous_scale='RdYlGn')
#         st.plotly_chart(fig, use_container_width=True)
    
#     st.dataframe(ch.style.format({'Revenue': '฿{:,.0f}', 'Profit': '฿{:,.0f}', 'Orders': '{:,}', 
#                                   'Customers': '{:,}', 'Margin %': '{:.1f}%'}), use_container_width=True)
    
#     st.subheader("4️⃣ Product Performance")
    
#     prod = df_filtered.groupby(['product_id', 'product_name', 'category']).agg({
#         'net_revenue': 'sum', 'profit': 'sum', 'quantity': 'sum'}).reset_index()
#     prod.columns = ['ID', 'Product', 'Category', 'Revenue', 'Profit', 'Units']
#     prod['Margin %'] = (prod['Profit'] / prod['Revenue'] * 100).round(1)
#     prod = prod.sort_values('Revenue', ascending=False).head(20)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         fig = px.bar(prod.head(10), x='Revenue', y='Product', orientation='h', color='Margin %', 
#                     color_continuous_scale='RdYlGn', title="Top 10 Products")
#         st.plotly_chart(fig, use_container_width=True)
#     with col2:
#         fig = px.scatter(prod, x='Revenue', y='Profit', size='Units', color='Category', 
#                         hover_data=['Product'], title="Revenue vs Profit")
#         st.plotly_chart(fig, use_container_width=True)
    
#     st.dataframe(prod.style.format({'Revenue': '฿{:,.0f}', 'Profit': '฿{:,.0f}', 
#                                     'Units': '{:,}', 'Margin %': '{:.1f}%'}), use_container_width=True)
    
#     st.subheader("5️⃣ Customer Metrics")
    
#     marketing_cost = df_filtered['discount_amount'].sum() if 'discount_amount' in df_filtered.columns else 0
#     new_cust = df_filtered['user_id'].nunique()
#     cac = marketing_cost / new_cust if new_cust > 0 else 0
    
#     analysis_date = df_filtered['order_date'].max()
#     last_purchase = df_filtered.groupby('user_id')['order_date'].max()
#     churned = ((analysis_date - last_purchase).dt.days > 90).sum()
#     churn = (churned / len(last_purchase) * 100) if len(last_purchase) > 0 else 0
#     retention = 100 - churn
    
#     avg_rev = df_filtered.groupby('user_id')['net_revenue'].sum().mean()
#     clv = (margin / 100) * (retention / 100) * avg_rev
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("CAC", f"฿{cac:,.2f}")
#     col2.metric("Retention", f"{retention:.1f}%")
#     col3.metric("Churn", f"{churn:.1f}%")
#     col4.metric("CLV", f"฿{clv:,.0f}")

# with tab2:
#     st.header("📢 Marketing Analytics")
    
#     st.subheader("1️⃣ Campaign Effectiveness")
    
#     if 'campaign_type' in df_filtered.columns:
#         camp = df_filtered[df_filtered['campaign_type'].notna()]
#         no_camp = df_filtered[df_filtered['campaign_type'].isna()]
        
#         if len(camp) > 0:
#             camp_rev = camp['net_revenue'].sum()
#             camp_share = (camp_rev / revenue * 100) if revenue > 0 else 0
#             conv = (len(camp) / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
#             camp_aov = camp.groupby('order_id')['net_revenue'].sum().mean()
#             no_camp_aov = no_camp.groupby('order_id')['net_revenue'].sum().mean() if len(no_camp) > 0 else 0
            
#             camp_cost = camp['discount_amount'].sum() if 'discount_amount' in camp.columns else 0
#             roas = (camp_rev / camp_cost * 100) if camp_cost > 0 else 0
            
#             col1, col2, col3, col4 = st.columns(4)
#             col1.metric("Campaign Revenue %", f"{camp_share:.1f}%")
#             col2.metric("Conv Rate", f"{conv:.1f}%")
#             col3.metric("ROAS", f"{roas:.0f}%")
#             col4.metric("Campaign AOV", f"฿{camp_aov:,.0f}")
            
#             col1, col2 = st.columns(2)
#             with col1:
#                 comp = pd.DataFrame({'Type': ['With Campaign', 'Without'], 'AOV': [camp_aov, no_camp_aov]})
#                 fig = px.bar(comp, x='Type', y='AOV', title="AOV Impact", color='Type', text='AOV')
#                 fig.update_traces(texttemplate='฿%{text:,.0f}', textposition='outside')
#                 st.plotly_chart(fig, use_container_width=True)
#             with col2:
#                 camp_break = camp.groupby('campaign_type')['net_revenue'].sum().sort_values(ascending=False)
#                 fig = px.bar(x=camp_break.values, y=camp_break.index, orientation='h', title="Revenue by Campaign")
#                 st.plotly_chart(fig, use_container_width=True)
    
#     st.subheader("2️⃣ Acquisition Channel")
    
#     if 'acquisition_channel' in df_filtered.columns:
#         acq = df_filtered.groupby('acquisition_channel').agg({'user_id': 'nunique', 'order_id': 'nunique', 
#                                                                'net_revenue': 'sum', 'profit': 'sum'}).reset_index()
#         acq.columns = ['Channel', 'Customers', 'Orders', 'Revenue', 'Profit']
#         acq['Conv %'] = (acq['Orders'] / acq['Customers'] * 100).round(1)
#         acq['Rev/Cust'] = (acq['Revenue'] / acq['Customers']).round(0)
#         acq = acq.sort_values('Revenue', ascending=False)
        
#         col1, col2 = st.columns(2)
#         with col1:
#             fig = px.bar(acq.sort_values('Revenue', ascending=True), x='Revenue', y='Channel', orientation='h')
#             st.plotly_chart(fig, use_container_width=True)
#         with col2:
#             fig = px.scatter(acq, x='Customers', y='Rev/Cust', size='Revenue', color='Channel')
#             st.plotly_chart(fig, use_container_width=True)
        
#         st.dataframe(acq.style.format({'Revenue': '฿{:,.0f}', 'Profit': '฿{:,.0f}', 
#                                        'Rev/Cust': '฿{:,.0f}', 'Conv %': '{:.1f}%'}), use_container_width=True)
    
#     st.subheader("3️⃣ RFM Analysis")
    
#     rfm = df_filtered.groupby('user_id').agg({'order_date': lambda x: (analysis_date - x.max()).days, 
#                                                'order_id': 'nunique', 'net_revenue': 'sum', 'profit': 'sum'}).reset_index()
#     rfm.columns = ['user_id', 'recency', 'frequency', 'monetary', 'profit']
    
#     def safe_qcut(s, q, labels):
#         try:
#             return pd.qcut(s.rank(method='first'), q=q, labels=labels, duplicates='drop')
#         except:
#             return pd.Series([labels[0]] * len(s), index=s.index)
    
#     rfm['R'] = safe_qcut(rfm['recency'], 4, [4,3,2,1])
#     rfm['F'] = safe_qcut(rfm['frequency'], 4, [1,2,3,4])
#     rfm['M'] = safe_qcut(rfm['monetary'], 4, [1,2,3,4])
#     rfm['RFM_Score'] = rfm[['R','F','M']].astype(int).sum(axis=1)
    
#     def segment(s):
#         if s >= 9: return 'Champions'
#         elif s >= 6: return 'Loyal'
#         elif s >= 4: return 'At Risk'
#         return 'Lost'
    
#     rfm['Segment'] = rfm['RFM_Score'].apply(segment)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         seg = rfm['Segment'].value_counts()
#         colors = {'Champions': '#2ecc71', 'Loyal': '#3498db', 'At Risk': '#f39c12', 'Lost': '#e74c3c'}
#         fig = px.pie(values=seg.values, names=seg.index, hole=0.4, color=seg.index, color_discrete_map=colors)
#         st.plotly_chart(fig, use_container_width=True)
#     with col2:
#         seg_val = rfm.groupby('Segment')['monetary'].sum().sort_values(ascending=True)
#         fig = px.bar(x=seg_val.values, y=seg_val.index, orientation='h', color=seg_val.index, color_discrete_map=colors)
#         st.plotly_chart(fig, use_container_width=True)

# with tab3:
#     st.header("💰 Financial Analytics")
    
#     st.subheader("1️⃣ Financial KPIs")
    
#     cogs = df_filtered['cost'].sum()
#     gross_profit = revenue - cogs
#     gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
#     net_margin = (profit / revenue * 100) if revenue > 0 else 0
    
#     col1, col2, col3, col4, col5 = st.columns(5)
#     col1.metric("Revenue", f"฿{revenue:,.0f}")
#     col2.metric("COGS", f"฿{cogs:,.0f}")
#     col3.metric("Gross Profit", f"฿{gross_profit:,.0f}", f"{gross_margin:.1f}%")
#     col4.metric("Net Profit", f"฿{profit:,.0f}", f"{net_margin:.1f}%")
#     col5.metric("ROS", f"{net_margin:.1f}%")
    
#     st.subheader("2️⃣ Monthly Performance")
    
#     mon_fin = df_filtered.groupby('order_month').agg({'net_revenue': 'sum', 'cost': 'sum', 'profit': 'sum'}).reset_index()
#     mon_fin['order_month'] = mon_fin['order_month'].dt.to_timestamp()
#     mon_fin['margin_%'] = (mon_fin['profit'] / mon_fin['net_revenue'] * 100).round(2)
    
#     fig = go.Figure()
#     fig.add_trace(go.Bar(x=mon_fin['order_month'], y=mon_fin['net_revenue'], name='Revenue', marker_color='lightblue'))
#     fig.add_trace(go.Bar(x=mon_fin['order_month'], y=mon_fin['cost'], name='COGS', marker_color='lightcoral'))
#     fig.add_trace(go.Scatter(x=mon_fin['order_month'], y=mon_fin['margin_%'], name='Margin %', yaxis='y2', 
#                             mode='lines+markers', line=dict(color='green', width=3)))
#     fig.update_layout(yaxis=dict(title="Amount"), yaxis2=dict(title="Margin %", overlaying='y', side='right'), 
#                      barmode='group', height=400)
#     st.plotly_chart(fig, use_container_width=True)
    
#     st.subheader("3️⃣ AR/AP Turnover")
    
#     avg_monthly_rev = mon_fin['net_revenue'].mean()
#     avg_ar = avg_monthly_rev * 0.3
#     ar_turnover = revenue * 0.3 / avg_ar if avg_ar > 0 else 0
#     dso = 365 / ar_turnover if ar_turnover > 0 else 0
    
#     avg_ap = cogs * 0.25
#     ap_turnover = cogs / avg_ap if avg_ap > 0 else 0
#     dpo = 365 / ap_turnover if ap_turnover > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("AR Turnover", f"{ar_turnover:.2f}x")
#     col2.metric("DSO", f"{dso:.0f} days")
#     col3.metric("AP Turnover", f"{ap_turnover:.2f}x")
#     col4.metric("DPO", f"{dpo:.0f} days")

# with tab4:
#     st.header("📦 Warehouse & Inventory")
    
#     st.subheader("1️⃣ Inventory Metrics")
    
#     avg_inv = df_filtered['cost'].mean() * df_filtered['product_id'].nunique()
#     inv_turnover = cogs / avg_inv if avg_inv > 0 else 0
#     dio = 365 / inv_turnover if inv_turnover > 0 else 0
    
#     units_sold = df_filtered['quantity'].sum()
#     units_received = units_sold * 1.2
#     sell_through = (units_sold / units_received * 100) if units_received > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("Inventory Turnover", f"{inv_turnover:.2f}x")
#     col2.metric("DIO", f"{dio:.0f} days")
#     col3.metric("Sell-Through Rate", f"{sell_through:.1f}%")
#     col4.metric("Inventory Value", f"฿{avg_inv:,.0f}")
    
#     st.subheader("2️⃣ Product Movement")
    
#     prod_vel = df_filtered.groupby(['product_id', 'product_name', 'category']).agg({
#         'order_id': 'nunique', 'net_revenue': 'sum', 'cost': 'sum'}).reset_index()
#     prod_vel.columns = ['ID', 'Product', 'Category', 'Orders', 'Revenue', 'Cost']
    
#     fast_th = prod_vel['Orders'].quantile(0.75)
#     slow_th = prod_vel['Orders'].quantile(0.25)
    
#     def classify(cnt):
#         if cnt >= fast_th: return 'Fast Moving'
#         elif cnt <= slow_th: return 'Slow Moving'
#         return 'Medium Moving'
    
#     prod_vel['Movement'] = prod_vel['Orders'].apply(classify)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         mov = prod_vel['Movement'].value_counts()
#         colors = {'Fast Moving': '#2ecc71', 'Medium Moving': '#f39c12', 'Slow Moving': '#e74c3c'}
#         fig = px.pie(values=mov.values, names=mov.index, hole=0.4, color=mov.index, color_discrete_map=colors)
#         st.plotly_chart(fig, use_container_width=True)
#     with col2:
#         mov_val = prod_vel.groupby('Movement')['Cost'].sum().sort_values(ascending=True)
#         fig = px.bar(x=mov_val.values, y=mov_val.index, orientation='h', color=mov_val.index, color_discrete_map=colors)
#         st.plotly_chart(fig, use_container_width=True)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         st.markdown("#### 🚀 Top 10 Fast Moving")
#         fast = prod_vel[prod_vel['Movement'] == 'Fast Moving'].nlargest(10, 'Orders')
#         st.dataframe(fast[['Product', 'Category', 'Orders', 'Revenue']].style.format({'Revenue': '฿{:,.0f}'}), height=300)
#     with col2:
#         st.markdown("#### 🐌 Top 10 Slow Moving")
#         slow = prod_vel[prod_vel['Movement'] == 'Slow Moving'].nlargest(10, 'Cost')
#         st.dataframe(slow[['Product', 'Category', 'Orders', 'Cost']].style.format({'Cost': '฿{:,.0f}'}), height=300)
    
#     st.subheader("3️⃣ Cash Conversion Cycle")
    
#     ccc = dio + dso - dpo
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("DIO", f"{dio:.0f} days")
#     col2.metric("DSO", f"{dso:.0f} days")
#     col3.metric("DPO", f"{dpo:.0f} days")
#     col4.metric("CCC", f"{ccc:.0f} days")

# st.markdown("---")
# st.caption("📊 Fashion E-commerce Analytics | Powered by Streamlit")







































































# # Fashion E-commerce Analytics Dashboard - Improved Version
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# import numpy as np
# import warnings
# from datetime import datetime, timedelta

# warnings.filterwarnings('ignore')
# st.set_page_config(page_title="Fashion Analytics Pro", layout="wide", page_icon="👕")

# if 'data_loaded' not in st.session_state:
#     st.session_state.data_loaded = False
# if 'data' not in st.session_state:
#     st.session_state.data = {}

# REQUIRED_COLUMNS = {
#     'users': ['user_id', 'customer_type', 'created_at'],
#     'products': ['product_id', 'category', 'sale_price', 'cost'],
#     'orders': ['order_id', 'user_id', 'order_date', 'channel', 'status'],
#     'order_items': ['order_id', 'product_id', 'quantity', 'net_revenue', 'cost', 'profit']
# }

# def load_data():
#     st.sidebar.title("👕 Fashion Analytics Pro")
#     st.sidebar.markdown("---")
    
#     uploaded = st.sidebar.file_uploader("📁 Upload CSV Files", type=['csv'], accept_multiple_files=True)
    
#     if uploaded and st.sidebar.button("🔄 Load Data", type="primary"):
#         data = {}
#         mapping = {"users.csv": "users", "products.csv": "products", "orders.csv": "orders", 
#                    "order_items.csv": "order_items", "inventory_movements.csv": "inventory"}
        
#         for file in uploaded:
#             if file.name in mapping:
#                 try:
#                     df = pd.read_csv(file)
#                     table = mapping[file.name]
#                     if table in REQUIRED_COLUMNS:
#                         missing = [c for c in REQUIRED_COLUMNS[table] if c not in df.columns]
#                         if not missing:
#                             data[table] = df
#                             st.sidebar.success(f"✅ {file.name}")
#                         else:
#                             st.sidebar.error(f"❌ {file.name} - Missing: {', '.join(missing)}")
#                     else:
#                         data[table] = df
#                         st.sidebar.success(f"✅ {file.name}")
#                 except Exception as e:
#                     st.sidebar.error(f"❌ {file.name}: {str(e)}")
        
#         if all(t in data for t in ['users', 'products', 'orders', 'order_items']):
#             st.session_state.data = data
#             st.session_state.data_loaded = True
#             st.sidebar.success("✅ All data loaded!")
#             st.rerun()
#         else:
#             st.sidebar.error("❌ Missing required tables")
    
#     return st.session_state.data if st.session_state.data_loaded else None

# @st.cache_data
# def merge_data(data):
#     df = data['order_items'].copy()
#     df = df.merge(data['orders'], on='order_id', how='left', suffixes=('', '_o'))
#     df = df.merge(data['products'], on='product_id', how='left', suffixes=('', '_p'))
#     df = df.merge(data['users'], on='user_id', how='left', suffixes=('', '_u'))
    
#     for col in ['order_date', 'created_at']:
#         if col in df.columns:
#             df[col] = pd.to_datetime(df[col], errors='coerce')
    
#     if 'order_date' in df.columns:
#         df['order_month'] = df['order_date'].dt.to_period('M')
#         df['order_year'] = df['order_date'].dt.year
#         df['order_day'] = df['order_date'].dt.day
    
#     online = ['Shopee', 'Lazada', 'TikTok', 'LINE Shopping']
#     df['channel_type'] = df['channel'].apply(lambda x: 'Online' if x in online else 'Offline')
    
#     return df

# data = load_data()

# if not data:
#     st.title("👕 Fashion E-commerce Analytics Dashboard")
#     st.info("👈 Please upload CSV files to begin")
    
#     st.markdown("### 📋 Required Columns")
#     col1, col2 = st.columns(2)
#     with col1:
#         st.code("users.csv:\n- user_id\n- customer_type\n- created_at")
#         st.code("orders.csv:\n- order_id\n- user_id\n- order_date\n- channel\n- status")
#     with col2:
#         st.code("products.csv:\n- product_id\n- category\n- sale_price\n- cost")
#         st.code("order_items.csv:\n- order_id\n- product_id\n- quantity\n- net_revenue\n- cost\n- profit")
#     st.stop()

# df_master = merge_data(data)

# # ==================== IMPROVED FILTERS ====================
# st.sidebar.markdown("---")
# st.sidebar.markdown("### 🔍 Filters")

# # Date Range Filter with Quick Selections
# min_date = df_master['order_date'].min().date()
# max_date = df_master['order_date'].max().date()

# st.sidebar.markdown("**📅 Select Time Period:**")
# period_options = ["Custom Range", "Last 7 Days", "Last 30 Days", "Last 90 Days", "This Month", "Last Month", "This Quarter", "This Year", "All Time"]
# selected_period = st.sidebar.selectbox("Quick Select", period_options, index=0)

# # Calculate date range based on selection
# if selected_period == "Last 7 Days":
#     start_date = max_date - timedelta(days=7)
#     end_date = max_date
# elif selected_period == "Last 30 Days":
#     start_date = max_date - timedelta(days=30)
#     end_date = max_date
# elif selected_period == "Last 90 Days":
#     start_date = max_date - timedelta(days=90)
#     end_date = max_date
# elif selected_period == "This Month":
#     start_date = max_date.replace(day=1)
#     end_date = max_date
# elif selected_period == "Last Month":
#     first_day_this_month = max_date.replace(day=1)
#     end_date = first_day_this_month - timedelta(days=1)
#     start_date = end_date.replace(day=1)
# elif selected_period == "This Quarter":
#     quarter = (max_date.month - 1) // 3
#     start_date = datetime(max_date.year, quarter * 3 + 1, 1).date()
#     end_date = max_date
# elif selected_period == "This Year":
#     start_date = datetime(max_date.year, 1, 1).date()
#     end_date = max_date
# elif selected_period == "All Time":
#     start_date = min_date
#     end_date = max_date
# else:  # Custom Range
#     date_range = st.sidebar.date_input("Select Custom Range", [min_date, max_date], 
#                                        min_value=min_date, max_value=max_date)
#     if len(date_range) == 2:
#         start_date, end_date = date_range
#     else:
#         start_date, end_date = min_date, max_date

# # Display selected date range
# st.sidebar.info(f"📆 From: {start_date.strftime('%d %b %Y')}\n\n📆 To: {end_date.strftime('%d %b %Y')}")

# df_filtered = df_master[(df_master['order_date'].dt.date >= start_date) & 
#                         (df_master['order_date'].dt.date <= end_date)]

# st.sidebar.markdown("---")

# # Other Filters
# channels = st.sidebar.multiselect("🏪 Channel", df_filtered['channel'].unique(), df_filtered['channel'].unique())
# df_filtered = df_filtered[df_filtered['channel'].isin(channels)]

# statuses = st.sidebar.multiselect("📦 Status", df_filtered['status'].unique(), ['Completed'])
# df_filtered = df_filtered[df_filtered['status'].isin(statuses)]

# # Display metrics in sidebar
# st.sidebar.markdown("---")
# st.sidebar.markdown("### 📊 Quick Stats")
# st.sidebar.metric("💰 Total Revenue", f"฿{df_filtered['net_revenue'].sum():,.0f}")
# st.sidebar.metric("💵 Total Profit", f"฿{df_filtered['profit'].sum():,.0f}")
# st.sidebar.metric("📝 Total Orders", f"{df_filtered['order_id'].nunique():,}")
# st.sidebar.metric("👥 Total Customers", f"{df_filtered['user_id'].nunique():,}")

# tab1, tab2, tab3, tab4 = st.tabs(["💼 Sales", "📢 Marketing", "💰 Financial", "📦 Warehouse"])

# with tab1:
#     st.header("💼 Sales Analytics")
    
#     st.subheader("1️⃣ Key Performance Indicators")
    
#     revenue = df_filtered['net_revenue'].sum()
#     profit = df_filtered['profit'].sum()
#     margin = (profit / revenue * 100) if revenue > 0 else 0
    
#     monthly = df_filtered.groupby('order_month')['net_revenue'].sum().sort_index()
#     growth = ((monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2] * 100) if len(monthly) >= 2 else 0
    
#     aov = df_filtered.groupby('order_id')['net_revenue'].sum().mean()
#     target = 5000000
#     curr_sales = df_filtered[df_filtered['order_month'] == df_filtered['order_month'].max()]['net_revenue'].sum()
#     attainment = (curr_sales / target * 100) if target > 0 else 0
    
#     col1, col2, col3, col4, col5 = st.columns(5)
#     col1.metric("📈 Monthly Growth", f"{growth:+.1f}%", help="เปรียบเทียบเดือนปัจจุบันกับเดือนที่แล้ว")
#     col2.metric("💹 Profit Margin", f"{margin:.1f}%", help="กำไรหารด้วยยอดขาย")
#     col3.metric("🎯 Target Achievement", f"{attainment:.1f}%", help="เทียบกับเป้า 5M/เดือน")
#     col4.metric("🛒 Avg Order Value", f"฿{aov:,.0f}", help="ยอดขายเฉลี่ยต่อออเดอร์")
#     col5.metric("👥 Total Customers", f"{df_filtered['user_id'].nunique():,}", help="จำนวนลูกค้าทั้งหมด")
    
#     # ==================== IMPROVED SALES TREND ====================
#     st.subheader("2️⃣ Sales Trend Analysis")
    
#     # Monthly Bar Chart with Profit Margin %
#     monthly_data = df_filtered.groupby('order_month').agg({
#         'net_revenue': 'sum', 
#         'cost': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     monthly_data['order_month'] = monthly_data['order_month'].dt.to_timestamp()
#     monthly_data['margin_%'] = (monthly_data['profit'] / monthly_data['net_revenue'] * 100).clip(0, 100)
#     monthly_data['month_label'] = monthly_data['order_month'].dt.strftime('%b %Y')
    
#     col1, col2 = st.columns([2, 1])
    
#     with col1:
#         st.markdown("**📊 Monthly Revenue & Profit Margin**")
#         fig = go.Figure()
        
#         # Revenue bars
#         fig.add_trace(go.Bar(
#             x=monthly_data['month_label'],
#             y=monthly_data['net_revenue'],
#             name='Revenue',
#             marker_color='#3498db',
#             text=monthly_data['net_revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         # Profit margin line
#         fig.add_trace(go.Scatter(
#             x=monthly_data['month_label'],
#             y=monthly_data['margin_%'],
#             name='Profit Margin %',
#             yaxis='y2',
#             mode='lines+markers+text',
#             line=dict(color='#27ae60', width=3),
#             marker=dict(size=10),
#             text=monthly_data['margin_%'],
#             texttemplate='%{text:.1f}%',
#             textposition='top center',
#             hovertemplate='<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>'
#         ))
        
#         fig.update_layout(
#             yaxis=dict(title="Revenue (฿)", showgrid=True, gridcolor='lightgray'),
#             yaxis2=dict(
#                 title="Profit Margin (%)", 
#                 overlaying='y', 
#                 side='right',
#                 range=[0, 100],
#                 showgrid=False
#             ),
#             height=450,
#             hovermode='x unified',
#             showlegend=True,
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         st.markdown("**📈 Margin Gauge**")
#         current_margin = monthly_data['margin_%'].iloc[-1] if len(monthly_data) > 0 else 0
        
#         fig_gauge = go.Figure(go.Indicator(
#             mode="gauge+number+delta",
#             value=current_margin,
#             domain={'x': [0, 1], 'y': [0, 1]},
#             title={'text': "Current Month<br>Profit Margin"},
#             delta={'reference': monthly_data['margin_%'].iloc[-2] if len(monthly_data) >= 2 else current_margin},
#             gauge={
#                 'axis': {'range': [None, 100], 'ticksuffix': '%'},
#                 'bar': {'color': "#27ae60"},
#                 'steps': [
#                     {'range': [0, 30], 'color': "#e74c3c"},
#                     {'range': [30, 50], 'color': "#f39c12"},
#                     {'range': [50, 100], 'color': "#d5f4e6"}
#                 ],
#                 'threshold': {
#                     'line': {'color': "red", 'width': 4},
#                     'thickness': 0.75,
#                     'value': 40
#                 }
#             }
#         ))
        
#         fig_gauge.update_layout(height=450)
#         st.plotly_chart(fig_gauge, use_container_width=True)
    
#     # Daily Trend for Selected Month
#     st.markdown("**📅 Daily Sales Breakdown**")
    
#     # Month selector
#     available_months = sorted(df_filtered['order_month'].unique(), reverse=True)
#     month_labels = [m.strftime('%B %Y') for m in available_months]
    
#     col1, col2 = st.columns([1, 3])
#     with col1:
#         selected_month_label = st.selectbox("Select Month", month_labels, index=0)
#         selected_month = available_months[month_labels.index(selected_month_label)]
    
#     # Filter data for selected month
#     month_filtered = df_filtered[df_filtered['order_month'] == selected_month]
    
#     if len(month_filtered) > 0:
#         daily_data = month_filtered.groupby(month_filtered['order_date'].dt.date).agg({
#             'net_revenue': 'sum',
#             'profit': 'sum',
#             'order_id': 'nunique'
#         }).reset_index()
#         daily_data.columns = ['date', 'revenue', 'profit', 'orders']
#         daily_data['margin_%'] = (daily_data['profit'] / daily_data['revenue'] * 100).fillna(0)
        
#         fig_daily = go.Figure()
        
#         # Revenue line
#         fig_daily.add_trace(go.Scatter(
#             x=daily_data['date'],
#             y=daily_data['revenue'],
#             name='Daily Revenue',
#             mode='lines+markers',
#             line=dict(color='#3498db', width=2),
#             marker=dict(size=6),
#             fill='tozeroy',
#             fillcolor='rgba(52, 152, 219, 0.1)',
#             hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         # Orders line
#         fig_daily.add_trace(go.Scatter(
#             x=daily_data['date'],
#             y=daily_data['orders'],
#             name='Number of Orders',
#             mode='lines+markers',
#             line=dict(color='#9b59b6', width=2, dash='dash'),
#             marker=dict(size=6),
#             yaxis='y2',
#             hovertemplate='<b>%{x}</b><br>Orders: %{y}<extra></extra>'
#         ))
        
#         fig_daily.update_layout(
#             yaxis=dict(title="Revenue (฿)", showgrid=True, gridcolor='lightgray'),
#             yaxis2=dict(title="Number of Orders", overlaying='y', side='right', showgrid=False),
#             height=400,
#             hovermode='x unified',
#             showlegend=True,
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#         )
        
#         st.plotly_chart(fig_daily, use_container_width=True)
        
#         # Summary stats for selected month
#         col1, col2, col3, col4 = st.columns(4)
#         col1.metric("📊 Total Revenue", f"฿{daily_data['revenue'].sum():,.0f}")
#         col2.metric("📝 Total Orders", f"{daily_data['orders'].sum():,}")
#         col3.metric("📈 Avg Daily Revenue", f"฿{daily_data['revenue'].mean():,.0f}")
#         col4.metric("🎯 Best Day", f"฿{daily_data['revenue'].max():,.0f}")
#     else:
#         st.info("No data available for the selected month")
    
#     st.markdown("---")
    
#     # ==================== IMPROVED CHANNEL PERFORMANCE ====================
#     st.subheader("3️⃣ Channel Performance")
    
#     ch = df_filtered.groupby('channel').agg({
#         'net_revenue': 'sum', 
#         'profit': 'sum', 
#         'order_id': 'nunique', 
#         'user_id': 'nunique'
#     }).reset_index()
#     ch.columns = ['Channel', 'Revenue', 'Profit', 'Orders', 'Customers']
#     ch['Margin %'] = (ch['Profit'] / ch['Revenue'] * 100).round(1)
#     ch['AOV'] = (ch['Revenue'] / ch['Orders']).round(0)
#     ch = ch.sort_values('Revenue', ascending=False)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         fig = px.pie(
#             ch, 
#             values='Revenue', 
#             names='Channel', 
#             title="Revenue Distribution by Channel", 
#             hole=0.4,
#             color_discrete_sequence=px.colors.qualitative.Set3
#         )
#         fig.update_traces(
#             textposition='inside',
#             textinfo='percent+label',
#             hovertemplate='<b>%{label}</b><br>Revenue: ฿%{value:,.0f}<br>Share: %{percent}<extra></extra>'
#         )
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         fig = px.bar(
#             ch.sort_values('Revenue', ascending=True), 
#             x='Revenue', 
#             y='Channel', 
#             orientation='h',
#             title="Revenue by Channel (with Profit Margin)",
#             color='Margin %', 
#             color_continuous_scale='RdYlGn',
#             text='Revenue'
#         )
#         fig.update_traces(
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<br>Margin: %{marker.color:.1f}%<extra></extra>'
#         )
#         st.plotly_chart(fig, use_container_width=True)
    
#     st.markdown("**📋 Detailed Channel Metrics**")
#     st.dataframe(
#         ch.style.format({
#             'Revenue': '฿{:,.0f}', 
#             'Profit': '฿{:,.0f}', 
#             'Orders': '{:,}',
#             'Customers': '{:,}', 
#             'Margin %': '{:.1f}%',
#             'AOV': '฿{:,.0f}'
#         }).background_gradient(subset=['Margin %'], cmap='RdYlGn', vmin=0, vmax=100),
#         use_container_width=True
#     )
    
#     st.markdown("---")
    
#     # ==================== IMPROVED PRODUCT PERFORMANCE ====================
#     st.subheader("4️⃣ Top Product Performance")
    
#     prod = df_filtered.groupby(['product_id', 'product_name', 'category']).agg({
#         'net_revenue': 'sum', 
#         'profit': 'sum', 
#         'quantity': 'sum'
#     }).reset_index()
#     prod.columns = ['ID', 'Product', 'Category', 'Revenue', 'Profit', 'Units']
#     prod['Margin %'] = (prod['Profit'] / prod['Revenue'] * 100).round(1)
#     prod = prod.sort_values('Revenue', ascending=False).head(20)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         top10 = prod.head(10).sort_values('Revenue', ascending=True)
#         fig = px.bar(
#             top10, 
#             x='Revenue', 
#             y='Product', 
#             orientation='h',
#             title="Top 10 Products by Revenue",
#             color='Margin %',
#             color_continuous_scale='RdYlGn',
#             text='Revenue'
#         )
#         fig.update_traces(
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<br>Margin: %{marker.color:.1f}%<extra></extra>'
#         )
#         fig.update_layout(yaxis={'categoryorder': 'total ascending'})
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         fig = px.scatter(
#             prod, 
#             x='Revenue', 
#             y='Profit', 
#             size='Units',
#             color='Category',
#             hover_data=['Product'],
#             title="Revenue vs Profit (size = units sold)",
#             color_discrete_sequence=px.colors.qualitative.Set2
#         )
#         fig.update_traces(
#             hovertemplate='<b>%{customdata[0]}</b><br>Revenue: ฿%{x:,.0f}<br>Profit: ฿%{y:,.0f}<br>Units: %{marker.size}<extra></extra>'
#         )
#         st.plotly_chart(fig, use_container_width=True)
    
#     st.markdown("**📋 Top 20 Products Detail**")
#     st.dataframe(
#         prod.style.format({
#             'Revenue': '฿{:,.0f}', 
#             'Profit': '฿{:,.0f}',
#             'Units': '{:,}', 
#             'Margin %': '{:.1f}%'
#         }).background_gradient(subset=['Margin %'], cmap='RdYlGn', vmin=0, vmax=100),
#         use_container_width=True
#     )
    
#     st.markdown("---")
    
#     # ==================== IMPROVED CUSTOMER METRICS ====================
#     st.subheader("5️⃣ Customer Lifetime Value Metrics")
    
#     marketing_cost = df_filtered['discount_amount'].sum() if 'discount_amount' in df_filtered.columns else 0
#     new_cust = df_filtered['user_id'].nunique()
#     cac = marketing_cost / new_cust if new_cust > 0 else 0
    
#     analysis_date = df_filtered['order_date'].max()
#     last_purchase = df_filtered.groupby('user_id')['order_date'].max()
#     churned = ((analysis_date - last_purchase).dt.days > 90).sum()
#     churn = (churned / len(last_purchase) * 100) if len(last_purchase) > 0 else 0
#     retention = 100 - churn
    
#     avg_rev = df_filtered.groupby('user_id')['net_revenue'].sum().mean()
#     clv = (margin / 100) * (retention / 100) * avg_rev
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("💳 CAC", f"฿{cac:,.2f}", help="Customer Acquisition Cost (ค่าใช้จ่ายในการหาลูกค้าใหม่)")
#     col2.metric("🔄 Retention Rate", f"{retention:.1f}%", help="ลูกค้าที่ซื้อซ้ำภายใน 90 วัน")
#     col3.metric("❌ Churn Rate", f"{churn:.1f}%", help="ลูกค้าที่หายไป (ไม่ซื้อเกิน 90 วัน)")
#     col4.metric("💎 CLV", f"฿{clv:,.0f}", help="Customer Lifetime Value (มูลค่าของลูกค้าตลอดชีพ)")
    
#     # Customer cohort visualization
#     st.markdown("**👥 Customer Segmentation by Purchase Frequency**")
    
#     cust_orders = df_filtered.groupby('user_id')['order_id'].nunique().reset_index()
#     cust_orders.columns = ['user_id', 'order_count']
    
#     def segment_customer(count):
#         if count == 1:
#             return 'One-time'
#         elif count <= 3:
#             return 'Occasional'
#         elif count <= 5:
#             return 'Regular'
#         else:
#             return 'Loyal'
    
#     cust_orders['segment'] = cust_orders['order_count'].apply(segment_customer)
#     segment_dist = cust_orders['segment'].value_counts()
    
#     colors = {'One-time': '#e74c3c', 'Occasional': '#f39c12', 'Regular': '#3498db', 'Loyal': '#27ae60'}
#     fig = px.pie(
#         values=segment_dist.values,
#         names=segment_dist.index,
#         title="Customer Distribution by Purchase Frequency",
#         hole=0.4,
#         color=segment_dist.index,
#         color_discrete_map=colors
#     )
#     fig.update_traces(
#         textposition='inside',
#         textinfo='percent+label',
#         hovertemplate='<b>%{label}</b><br>Customers: %{value}<br>Share: %{percent}<extra></extra>'
#     )
#     st.plotly_chart(fig, use_container_width=True)

# with tab2:
#     st.header("📢 Marketing Analytics")
    
#     st.subheader("1️⃣ Campaign Effectiveness")
    
#     if 'campaign_type' in df_filtered.columns:
#         camp = df_filtered[df_filtered['campaign_type'].notna()]
#         no_camp = df_filtered[df_filtered['campaign_type'].isna()]
        
#         if len(camp) > 0:
#             camp_rev = camp['net_revenue'].sum()
#             camp_share = (camp_rev / revenue * 100) if revenue > 0 else 0
#             conv = (len(camp) / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
#             camp_aov = camp.groupby('order_id')['net_revenue'].sum().mean()
#             no_camp_aov = no_camp.groupby('order_id')['net_revenue'].sum().mean() if len(no_camp) > 0 else 0
            
#             camp_cost = camp['discount_amount'].sum() if 'discount_amount' in camp.columns else 0
#             roas = (camp_rev / camp_cost * 100) if camp_cost > 0 else 0
            
#             col1, col2, col3, col4 = st.columns(4)
#             col1.metric("📊 Campaign Revenue Share", f"{camp_share:.1f}%", help="สัดส่วนยอดขายจากแคมเปญ")
#             col2.metric("🎯 Conversion Rate", f"{conv:.1f}%", help="อัตราการซื้อจากแคมเปญ")
#             col3.metric("💰 ROAS", f"{roas:.0f}%", help="Return on Ad Spend (ผลตอบแทนจากการโฆษณา)")
#             col4.metric("🛒 Campaign AOV", f"฿{camp_aov:,.0f}", help="ค่าเฉลี่ยต่อออเดอร์จากแคมเปญ")
            
#             col1, col2 = st.columns(2)
#             with col1:
#                 comp = pd.DataFrame({
#                     'Type': ['With Campaign', 'Without Campaign'],
#                     'AOV': [camp_aov, no_camp_aov]
#                 })
#                 fig = px.bar(
#                     comp, 
#                     x='Type', 
#                     y='AOV',
#                     title="AOV Comparison: Campaign vs Non-Campaign",
#                     color='Type',
#                     text='AOV',
#                     color_discrete_map={'With Campaign': '#27ae60', 'Without Campaign': '#95a5a6'}
#                 )
#                 fig.update_traces(
#                     texttemplate='฿%{text:,.0f}',
#                     textposition='outside'
#                 )
#                 st.plotly_chart(fig, use_container_width=True)
            
#             with col2:
#                 camp_break = camp.groupby('campaign_type')['net_revenue'].sum().sort_values(ascending=False)
#                 fig = px.bar(
#                     x=camp_break.values,
#                     y=camp_break.index,
#                     orientation='h',
#                     title="Revenue by Campaign Type",
#                     labels={'x': 'Revenue', 'y': 'Campaign Type'},
#                     text=camp_break.values
#                 )
#                 fig.update_traces(
#                     texttemplate='฿%{text:,.0f}',
#                     textposition='outside',
#                     marker_color='#9b59b6'
#                 )
#                 st.plotly_chart(fig, use_container_width=True)
#     else:
#         st.info("Campaign data not available in the dataset")
    
#     st.markdown("---")
    
#     st.subheader("2️⃣ Acquisition Channel Analysis")
    
#     if 'acquisition_channel' in df_filtered.columns:
#         acq = df_filtered.groupby('acquisition_channel').agg({
#             'user_id': 'nunique',
#             'order_id': 'nunique',
#             'net_revenue': 'sum',
#             'profit': 'sum'
#         }).reset_index()
#         acq.columns = ['Channel', 'Customers', 'Orders', 'Revenue', 'Profit']
#         acq['Conv %'] = (acq['Orders'] / acq['Customers'] * 100).round(1)
#         acq['Rev/Cust'] = (acq['Revenue'] / acq['Customers']).round(0)
#         acq = acq.sort_values('Revenue', ascending=False)
        
#         col1, col2 = st.columns(2)
#         with col1:
#             fig = px.bar(
#                 acq.sort_values('Revenue', ascending=True),
#                 x='Revenue',
#                 y='Channel',
#                 orientation='h',
#                 title="Revenue by Acquisition Channel",
#                 text='Revenue',
#                 color='Conv %',
#                 color_continuous_scale='Blues'
#             )
#             fig.update_traces(
#                 texttemplate='฿%{text:,.0f}',
#                 textposition='outside'
#             )
#             st.plotly_chart(fig, use_container_width=True)
        
#         with col2:
#             fig = px.scatter(
#                 acq,
#                 x='Customers',
#                 y='Rev/Cust',
#                 size='Revenue',
#                 color='Channel',
#                 title="Customer Efficiency by Channel",
#                 labels={'Rev/Cust': 'Revenue per Customer'},
#                 color_discrete_sequence=px.colors.qualitative.Set2
#             )
#             fig.update_traces(
#                 hovertemplate='<b>%{fullData.name}</b><br>Customers: %{x}<br>Rev/Cust: ฿%{y:,.0f}<extra></extra>'
#             )
#             st.plotly_chart(fig, use_container_width=True)
        
#         st.markdown("**📋 Acquisition Channel Details**")
#         st.dataframe(
#             acq.style.format({
#                 'Revenue': '฿{:,.0f}',
#                 'Profit': '฿{:,.0f}',
#                 'Rev/Cust': '฿{:,.0f}',
#                 'Conv %': '{:.1f}%'
#             }).background_gradient(subset=['Conv %'], cmap='Blues'),
#             use_container_width=True
#         )
#     else:
#         st.info("Acquisition channel data not available in the dataset")
    
#     st.markdown("---")
    
#     st.subheader("3️⃣ RFM Customer Segmentation")
    
#     analysis_date = df_filtered['order_date'].max()
#     rfm = df_filtered.groupby('user_id').agg({
#         'order_date': lambda x: (analysis_date - x.max()).days,
#         'order_id': 'nunique',
#         'net_revenue': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     rfm.columns = ['user_id', 'recency', 'frequency', 'monetary', 'profit']
    
#     def safe_qcut(s, q, labels):
#         try:
#             return pd.qcut(s.rank(method='first'), q=q, labels=labels, duplicates='drop')
#         except:
#             return pd.Series([labels[0]] * len(s), index=s.index)
    
#     rfm['R'] = safe_qcut(rfm['recency'], 4, [4, 3, 2, 1])
#     rfm['F'] = safe_qcut(rfm['frequency'], 4, [1, 2, 3, 4])
#     rfm['M'] = safe_qcut(rfm['monetary'], 4, [1, 2, 3, 4])
#     rfm['RFM_Score'] = rfm[['R', 'F', 'M']].astype(int).sum(axis=1)
    
#     def segment(s):
#         if s >= 9:
#             return 'Champions'
#         elif s >= 6:
#             return 'Loyal Customers'
#         elif s >= 4:
#             return 'At Risk'
#         return 'Lost'
    
#     rfm['Segment'] = rfm['RFM_Score'].apply(segment)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         seg = rfm['Segment'].value_counts()
#         colors = {
#             'Champions': '#27ae60',
#             'Loyal Customers': '#3498db',
#             'At Risk': '#f39c12',
#             'Lost': '#e74c3c'
#         }
#         fig = px.pie(
#             values=seg.values,
#             names=seg.index,
#             hole=0.4,
#             title="Customer Segmentation by RFM Score",
#             color=seg.index,
#             color_discrete_map=colors
#         )
#         fig.update_traces(
#             textposition='inside',
#             textinfo='percent+label',
#             hovertemplate='<b>%{label}</b><br>Customers: %{value}<br>Share: %{percent}<extra></extra>'
#         )
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         seg_val = rfm.groupby('Segment')['monetary'].sum().sort_values(ascending=True)
#         fig = px.bar(
#             x=seg_val.values,
#             y=seg_val.index,
#             orientation='h',
#             title="Total Revenue by Customer Segment",
#             color=seg_val.index,
#             color_discrete_map=colors,
#             text=seg_val.values
#         )
#         fig.update_traces(
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside'
#         )
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Segment descriptions
#     st.markdown("**📊 Segment Descriptions:**")
#     col1, col2, col3, col4 = st.columns(4)
#     with col1:
#         st.success("**Champions** 🏆")
#         st.write("ลูกค้าระดับพรีเมียม ซื้อบ่อย ซื้อเยอะ ซื้อเมื่อไม่นานมานี้")
#     with col2:
#         st.info("**Loyal Customers** 💙")
#         st.write("ลูกค้าภักดี ซื้อสม่ำเสมอ มีศักยภาพเป็น Champions")
#     with col3:
#         st.warning("**At Risk** ⚠️")
#         st.write("ลูกค้าที่อาจจะหายไป ต้องดูแลเป็นพิเศษ")
#     with col4:
#         st.error("**Lost** 😢")
#         st.write("ลูกค้าที่หายไปแล้ว ต้องมีแคมเปญดึงกลับมา")

# with tab3:
#     st.header("💰 Financial Analytics")
    
#     st.subheader("1️⃣ Financial Summary")
    
#     cogs = df_filtered['cost'].sum()
#     gross_profit = revenue - cogs
#     gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
#     net_margin = (profit / revenue * 100) if revenue > 0 else 0
    
#     col1, col2, col3, col4, col5 = st.columns(5)
#     col1.metric("💵 Revenue", f"฿{revenue:,.0f}", help="ยอดขายรวม")
#     col2.metric("📦 COGS", f"฿{cogs:,.0f}", help="ต้นทุนสินค้า")
#     col3.metric("💚 Gross Profit", f"฿{gross_profit:,.0f}", f"{gross_margin:.1f}%", help="กำไรขั้นต้น")
#     col4.metric("💎 Net Profit", f"฿{profit:,.0f}", f"{net_margin:.1f}%", help="กำไรสุทธิ")
#     col5.metric("📊 ROS", f"{net_margin:.1f}%", help="Return on Sales (กำไรสุทธิ/ยอดขาย)")
    
#     st.markdown("---")
    
#     st.subheader("2️⃣ Monthly Financial Performance")
    
#     mon_fin = df_filtered.groupby('order_month').agg({
#         'net_revenue': 'sum',
#         'cost': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     mon_fin['order_month'] = mon_fin['order_month'].dt.to_timestamp()
#     mon_fin['margin_%'] = (mon_fin['profit'] / mon_fin['net_revenue'] * 100).round(2)
#     mon_fin['month_label'] = mon_fin['order_month'].dt.strftime('%b %Y')
    
#     fig = go.Figure()
    
#     # Revenue bars
#     fig.add_trace(go.Bar(
#         x=mon_fin['month_label'],
#         y=mon_fin['net_revenue'],
#         name='Revenue',
#         marker_color='#3498db',
#         hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#     ))
    
#     # COGS bars
#     fig.add_trace(go.Bar(
#         x=mon_fin['month_label'],
#         y=mon_fin['cost'],
#         name='COGS',
#         marker_color='#e74c3c',
#         hovertemplate='<b>%{x}</b><br>COGS: ฿%{y:,.0f}<extra></extra>'
#     ))
    
#     # Margin line
#     fig.add_trace(go.Scatter(
#         x=mon_fin['month_label'],
#         y=mon_fin['margin_%'],
#         name='Profit Margin %',
#         yaxis='y2',
#         mode='lines+markers',
#         line=dict(color='#27ae60', width=3),
#         marker=dict(size=10),
#         hovertemplate='<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>'
#     ))
    
#     fig.update_layout(
#         yaxis=dict(title="Amount (฿)", showgrid=True),
#         yaxis2=dict(title="Profit Margin (%)", overlaying='y', side='right', showgrid=False),
#         barmode='group',
#         height=400,
#         hovermode='x unified',
#         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#     )
    
#     st.plotly_chart(fig, use_container_width=True)
    
#     st.markdown("---")
    
#     st.subheader("3️⃣ Working Capital Ratios")
    
#     avg_monthly_rev = mon_fin['net_revenue'].mean()
#     avg_ar = avg_monthly_rev * 0.3
#     ar_turnover = revenue * 0.3 / avg_ar if avg_ar > 0 else 0
#     dso = 365 / ar_turnover if ar_turnover > 0 else 0
    
#     avg_ap = cogs * 0.25
#     ap_turnover = cogs / avg_ap if avg_ap > 0 else 0
#     dpo = 365 / ap_turnover if ap_turnover > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("🔄 AR Turnover", f"{ar_turnover:.2f}x", help="เร็วเท่าไรที่เราเก็บเงินจากลูกค้าได้")
#     col2.metric("📅 DSO", f"{dso:.0f} days", help="Days Sales Outstanding (จำนวนวันที่เก็บเงินได้)")
#     col3.metric("🔄 AP Turnover", f"{ap_turnover:.2f}x", help="เร็วเท่าไรที่เราจ่ายเงินซัพพลายเออร์")
#     col4.metric("📅 DPO", f"{dpo:.0f} days", help="Days Payable Outstanding (จำนวนวันที่เราจ่ายเงิน)")

# with tab4:
#     st.header("📦 Warehouse & Inventory Management")
    
#     st.subheader("1️⃣ Inventory Performance Metrics")
    
#     avg_inv = df_filtered['cost'].mean() * df_filtered['product_id'].nunique()
#     inv_turnover = cogs / avg_inv if avg_inv > 0 else 0
#     dio = 365 / inv_turnover if inv_turnover > 0 else 0
    
#     units_sold = df_filtered['quantity'].sum()
#     units_received = units_sold * 1.2
#     sell_through = (units_sold / units_received * 100) if units_received > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("🔄 Inventory Turnover", f"{inv_turnover:.2f}x", help="จำนวนครั้งที่สินค้าหมุนเวียนต่อปี")
#     col2.metric("📅 DIO", f"{dio:.0f} days", help="Days Inventory Outstanding (จำนวนวันที่สินค้าอยู่ในคลัง)")
#     col3.metric("📈 Sell-Through Rate", f"{sell_through:.1f}%", help="อัตราการขายสินค้าที่รับเข้ามา")
#     col4.metric("💰 Inventory Value", f"฿{avg_inv:,.0f}", help="มูลค่าสินค้าคงคลัง")
    
#     st.markdown("---")
    
#     st.subheader("2️⃣ Product Movement Analysis")
    
#     prod_vel = df_filtered.groupby(['product_id', 'product_name', 'category']).agg({
#         'order_id': 'nunique',
#         'net_revenue': 'sum',
#         'cost': 'sum',
#         'quantity': 'sum'
#     }).reset_index()
#     prod_vel.columns = ['ID', 'Product', 'Category', 'Orders', 'Revenue', 'Cost', 'Units']
    
#     fast_th = prod_vel['Orders'].quantile(0.75)
#     slow_th = prod_vel['Orders'].quantile(0.25)
    
#     def classify(cnt):
#         if cnt >= fast_th:
#             return 'Fast Moving'
#         elif cnt <= slow_th:
#             return 'Slow Moving'
#         return 'Medium Moving'
    
#     prod_vel['Movement'] = prod_vel['Orders'].apply(classify)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         mov = prod_vel['Movement'].value_counts()
#         colors = {
#             'Fast Moving': '#27ae60',
#             'Medium Moving': '#f39c12',
#             'Slow Moving': '#e74c3c'
#         }
#         fig = px.pie(
#             values=mov.values,
#             names=mov.index,
#             hole=0.4,
#             title="Product Distribution by Movement Speed",
#             color=mov.index,
#             color_discrete_map=colors
#         )
#         fig.update_traces(
#             textposition='inside',
#             textinfo='percent+label',
#             hovertemplate='<b>%{label}</b><br>Products: %{value}<br>Share: %{percent}<extra></extra>'
#         )
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         mov_val = prod_vel.groupby('Movement')['Cost'].sum().sort_values(ascending=True)
#         fig = px.bar(
#             x=mov_val.values,
#             y=mov_val.index,
#             orientation='h',
#             title="Inventory Value by Movement Speed",
#             color=mov_val.index,
#             color_discrete_map=colors,
#             text=mov_val.values
#         )
#         fig.update_traces(
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside'
#         )
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Movement recommendations
#     st.markdown("**💡 Inventory Recommendations:**")
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         st.success("**Fast Moving** 🚀")
#         st.write("- เพิ่ม stock level")
#         st.write("- ลดโอกาสขาดสต็อก")
#         st.write("- พิจารณา bulk order")
#     with col2:
#         st.info("**Medium Moving** ⚖️")
#         st.write("- รักษาระดับ stock ปกติ")
#         st.write("- ติดตาม trend")
#         st.write("- พิจารณาโปรโมชั่น")
#     with col3:
#         st.warning("**Slow Moving** 🐌")
#         st.write("- ลด stock level")
#         st.write("- จัด clearance sale")
#         st.write("- หยุดสั่งซื้อชั่วคราว")
    
#     st.markdown("---")
    
#     col1, col2 = st.columns(2)
#     with col1:
#         st.markdown("#### 🚀 Top 10 Fast Moving Products")
#         fast = prod_vel[prod_vel['Movement'] == 'Fast Moving'].nlargest(10, 'Orders')
#         st.dataframe(
#             fast[['Product', 'Category', 'Orders', 'Units', 'Revenue']].style.format({
#                 'Revenue': '฿{:,.0f}',
#                 'Orders': '{:,}',
#                 'Units': '{:,}'
#             }),
#             height=350,
#             use_container_width=True
#         )
    
#     with col2:
#         st.markdown("#### 🐌 Top 10 Slow Moving Products")
#         slow = prod_vel[prod_vel['Movement'] == 'Slow Moving'].nlargest(10, 'Cost')
#         st.dataframe(
#             slow[['Product', 'Category', 'Orders', 'Units', 'Cost']].style.format({
#                 'Cost': '฿{:,.0f}',
#                 'Orders': '{:,}',
#                 'Units': '{:,}'
#             }),
#             height=350,
#             use_container_width=True
#         )
    
#     st.markdown("---")
    
#     st.subheader("3️⃣ Cash Conversion Cycle")
    
#     ccc = dio + dso - dpo
    
#     st.markdown("""
#     **Cash Conversion Cycle (CCC)** คือระยะเวลาที่เงินสดถูกล็อคอยู่ในธุรกิจ ตั้งแต่จ่ายเงินซื้อสินค้า จนกระทั่งได้รับเงินจากลูกค้า
    
#     - **สูตร:** CCC = DIO + DSO - DPO
#     - **เป้าหมาย:** ยิ่งต่ำยิ่งดี (แสดงว่าเงินสดหมุนเวียนเร็ว)
#     """)
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("📦 DIO", f"{dio:.0f} days", help="วันที่สินค้าอยู่ในคลัง")
#     col2.metric("💳 DSO", f"{dso:.0f} days", help="วันที่รอเก็บเงินจากลูกค้า")
#     col3.metric("💰 DPO", f"{dpo:.0f} days", help="วันที่เราจ่ายเงินซัพพลายเออร์")
#     col4.metric("⏱️ CCC", f"{ccc:.0f} days", 
#                 help="ระยะเวลารอบวงจรเงินสด (ยิ่งต่ำยิ่งดี)",
#                 delta=f"{'Better' if ccc < 60 else 'Needs improvement'}")
    
#     # CCC visualization
#     fig = go.Figure()
    
#     fig.add_trace(go.Bar(
#         x=['DIO', 'DSO', 'DPO', 'CCC'],
#         y=[dio, dso, -dpo, ccc],
#         text=[f"{dio:.0f}", f"{dso:.0f}", f"{dpo:.0f}", f"{ccc:.0f}"],
#         textposition='outside',
#         marker_color=['#3498db', '#9b59b6', '#e74c3c', '#27ae60'],
#         hovertemplate='<b>%{x}</b><br>Days: %{y:.0f}<extra></extra>'
#     ))
    
#     fig.update_layout(
#         title="Cash Conversion Cycle Breakdown (days)",
#         yaxis_title="Days",
#         height=400,
#         showlegend=False
#     )
    
#     st.plotly_chart(fig, use_container_width=True)
    
#     # CCC interpretation
#     if ccc < 30:
#         st.success("✅ **Excellent!** CCC ต่ำมาก เงินสดหมุนเวียนได้อย่างรวดเร็ว")
#     elif ccc < 60:
#         st.info("✔️ **Good!** CCC อยู่ในเกณฑ์ดี แต่ยังมีพื้นที่ปรับปรุงได้")
#     elif ccc < 90:
#         st.warning("⚠️ **Fair** CCC สูงพอสมควร ควรพิจารณาปรับปรุงการจัดการเงินสด")
#     else:
#         st.error("❌ **Needs Attention!** CCC สูงเกินไป เงินสดถูกล็อคอยู่นานเกินไป")

# st.markdown("---")
# st.markdown("""
# <div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px;'>
#     <h4>📊 Fashion E-commerce Analytics Dashboard</h4>
#     <p>Built with Streamlit | Data-Driven Insights for Better Business Decisions</p>
# </div>
# """, unsafe_allow_html=True)




































































































































































































































































































































































































































































# # Fashion E-commerce Analytics Dashboard - Improved Version
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# import numpy as np
# import warnings
# from datetime import datetime, timedelta

# warnings.filterwarnings('ignore')
# st.set_page_config(page_title="Fashion Analytics Pro", layout="wide", page_icon="👕")

# if 'data_loaded' not in st.session_state:
#     st.session_state.data_loaded = False
# if 'data' not in st.session_state:
#     st.session_state.data = {}

# REQUIRED_COLUMNS = {
#     'users': ['user_id', 'customer_type', 'created_at'],
#     'products': ['product_id', 'category', 'sale_price', 'cost'],
#     'orders': ['order_id', 'user_id', 'order_date', 'channel', 'status'],
#     'order_items': ['order_id', 'product_id', 'quantity', 'net_revenue', 'cost', 'profit']
# }

# def load_data():
#     st.sidebar.title("👕 Fashion Analytics Pro")
#     st.sidebar.markdown("---")
    
#     uploaded = st.sidebar.file_uploader("📁 Upload CSV Files", type=['csv'], accept_multiple_files=True)
    
#     if uploaded and st.sidebar.button("🔄 Load Data", type="primary"):
#         data = {}
#         mapping = {"users.csv": "users", "products.csv": "products", "orders.csv": "orders", 
#                    "order_items.csv": "order_items", "inventory_movements.csv": "inventory"}
        
#         for file in uploaded:
#             if file.name in mapping:
#                 try:
#                     df = pd.read_csv(file)
#                     table = mapping[file.name]
#                     if table in REQUIRED_COLUMNS:
#                         missing = [c for c in REQUIRED_COLUMNS[table] if c not in df.columns]
#                         if not missing:
#                             data[table] = df
#                             st.sidebar.success(f"✅ {file.name}")
#                         else:
#                             st.sidebar.error(f"❌ {file.name} - Missing: {', '.join(missing)}")
#                     else:
#                         data[table] = df
#                         st.sidebar.success(f"✅ {file.name}")
#                 except Exception as e:
#                     st.sidebar.error(f"❌ {file.name}: {str(e)}")
        
#         if all(t in data for t in ['users', 'products', 'orders', 'order_items']):
#             st.session_state.data = data
#             st.session_state.data_loaded = True
#             st.sidebar.success("✅ All data loaded!")
#             st.rerun()
#         else:
#             st.sidebar.error("❌ Missing required tables")
    
#     return st.session_state.data if st.session_state.data_loaded else None

# @st.cache_data
# def merge_data(data):
#     df = data['order_items'].copy()
#     df = df.merge(data['orders'], on='order_id', how='left', suffixes=('', '_o'))
#     df = df.merge(data['products'], on='product_id', how='left', suffixes=('', '_p'))
#     df = df.merge(data['users'], on='user_id', how='left', suffixes=('', '_u'))
    
#     for col in ['order_date', 'created_at']:
#         if col in df.columns:
#             df[col] = pd.to_datetime(df[col], errors='coerce')
    
#     if 'order_date' in df.columns:
#         df['order_month'] = df['order_date'].dt.to_period('M')
#         df['order_year'] = df['order_date'].dt.year
#         df['order_day'] = df['order_date'].dt.day
    
#     online = ['Shopee', 'Lazada', 'TikTok', 'LINE Shopping']
#     df['channel_type'] = df['channel'].apply(lambda x: 'Online' if x in online else 'Offline')
    
#     return df

# data = load_data()

# if not data:
#     st.title("👕 Fashion E-commerce Analytics Dashboard")
#     st.info("👈 Please upload CSV files to begin")
    
#     st.markdown("### 📋 Required Columns")
#     col1, col2 = st.columns(2)
#     with col1:
#         st.code("users.csv:\n- user_id\n- customer_type\n- created_at")
#         st.code("orders.csv:\n- order_id\n- user_id\n- order_date\n- channel\n- status")
#     with col2:
#         st.code("products.csv:\n- product_id\n- category\n- sale_price\n- cost")
#         st.code("order_items.csv:\n- order_id\n- product_id\n- quantity\n- net_revenue\n- cost\n- profit")
#     st.stop()

# df_master = merge_data(data)

# # ==================== IMPROVED FILTERS ====================
# st.sidebar.markdown("---")
# st.sidebar.markdown("### 🔍 Filters")

# # Date Range Filter with Quick Selections
# min_date = df_master['order_date'].min().date()
# max_date = df_master['order_date'].max().date()

# st.sidebar.markdown("**📅 Select Time Period:**")
# period_options = ["Custom Range", "Last 7 Days", "Last 30 Days", "Last 90 Days", "This Month", "Last Month", "This Quarter", "This Year", "All Time"]
# selected_period = st.sidebar.selectbox("Quick Select", period_options, index=0)

# # Calculate date range based on selection
# if selected_period == "Last 7 Days":
#     start_date = max_date - timedelta(days=7)
#     end_date = max_date
# elif selected_period == "Last 30 Days":
#     start_date = max_date - timedelta(days=30)
#     end_date = max_date
# elif selected_period == "Last 90 Days":
#     start_date = max_date - timedelta(days=90)
#     end_date = max_date
# elif selected_period == "This Month":
#     start_date = max_date.replace(day=1)
#     end_date = max_date
# elif selected_period == "Last Month":
#     first_day_this_month = max_date.replace(day=1)
#     end_date = first_day_this_month - timedelta(days=1)
#     start_date = end_date.replace(day=1)
# elif selected_period == "This Quarter":
#     quarter = (max_date.month - 1) // 3
#     start_date = datetime(max_date.year, quarter * 3 + 1, 1).date()
#     end_date = max_date
# elif selected_period == "This Year":
#     start_date = datetime(max_date.year, 1, 1).date()
#     end_date = max_date
# elif selected_period == "All Time":
#     start_date = min_date
#     end_date = max_date
# else:  # Custom Range
#     date_range = st.sidebar.date_input("Select Custom Range", [min_date, max_date], 
#                                        min_value=min_date, max_value=max_date)
#     if len(date_range) == 2:
#         start_date, end_date = date_range
#     else:
#         start_date, end_date = min_date, max_date

# # Display selected date range
# st.sidebar.info(f"📆 From: {start_date.strftime('%d %b %Y')}\n\n📆 To: {end_date.strftime('%d %b %Y')}")

# df_filtered = df_master[(df_master['order_date'].dt.date >= start_date) & 
#                         (df_master['order_date'].dt.date <= end_date)]

# st.sidebar.markdown("---")

# # Other Filters
# channels = st.sidebar.multiselect("🏪 Channel", df_filtered['channel'].unique(), df_filtered['channel'].unique())
# df_filtered = df_filtered[df_filtered['channel'].isin(channels)]

# statuses = st.sidebar.multiselect("📦 Status", df_filtered['status'].unique(), ['Completed'])
# df_filtered = df_filtered[df_filtered['status'].isin(statuses)]

# # Display metrics in sidebar
# st.sidebar.markdown("---")
# st.sidebar.markdown("### 📊 Quick Stats")
# st.sidebar.metric("💰 Total Revenue", f"฿{df_filtered['net_revenue'].sum():,.0f}")
# st.sidebar.metric("💵 Total Profit", f"฿{df_filtered['profit'].sum():,.0f}")
# st.sidebar.metric("📝 Total Orders", f"{df_filtered['order_id'].nunique():,}")
# st.sidebar.metric("👥 Total Customers", f"{df_filtered['user_id'].nunique():,}")

# tab1, tab2, tab3, tab4 = st.tabs(["💼 Sales", "📢 Marketing", "💰 Financial", "📦 Warehouse"])

# with tab1:
#     st.header("💼 Sales Analytics")
    
#     st.subheader("1️⃣ Key Performance Indicators")
    
#     revenue = df_filtered['net_revenue'].sum()
#     profit = df_filtered['profit'].sum()
#     margin = (profit / revenue * 100) if revenue > 0 else 0
    
#     monthly = df_filtered.groupby('order_month')['net_revenue'].sum().sort_index()
#     growth = ((monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2] * 100) if len(monthly) >= 2 else 0
    
#     aov = df_filtered.groupby('order_id')['net_revenue'].sum().mean()
#     target = 5000000
#     curr_sales = df_filtered[df_filtered['order_month'] == df_filtered['order_month'].max()]['net_revenue'].sum()
#     attainment = (curr_sales / target * 100) if target > 0 else 0
    
#     col1, col2, col3, col4, col5 = st.columns(5)
#     col1.metric("📈 Monthly Growth", f"{growth:+.1f}%", help="เปรียบเทียบเดือนปัจจุบันกับเดือนที่แล้ว")
#     col2.metric("💹 Profit Margin", f"{margin:.1f}%", help="กำไรหารด้วยยอดขาย")
#     col3.metric("🎯 Target Achievement", f"{attainment:.1f}%", help="เทียบกับเป้า 5M/เดือน")
#     col4.metric("🛒 Avg Order Value", f"฿{aov:,.0f}", help="ยอดขายเฉลี่ยต่อออเดอร์")
#     col5.metric("👥 Total Customers", f"{df_filtered['user_id'].nunique():,}", help="จำนวนลูกค้าทั้งหมด")
    
#     # ==================== IMPROVED SALES TREND ====================
#     st.subheader("2️⃣ Sales Trend Analysis")
    
#     # Monthly Bar Chart with Profit Margin %
#     monthly_data = df_filtered.groupby('order_month').agg({
#         'net_revenue': 'sum', 
#         'cost': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     monthly_data['order_month'] = monthly_data['order_month'].dt.to_timestamp()
#     monthly_data['margin_%'] = (monthly_data['profit'] / monthly_data['net_revenue'] * 100).clip(0, 100)
#     monthly_data['month_label'] = monthly_data['order_month'].dt.strftime('%b %Y')
    
#     col1, col2 = st.columns([2, 1])
    
#     with col1:
#         st.markdown("**📊 Monthly Revenue & Profit Margin**")
#         fig = go.Figure()
        
#         # Revenue bars
#         fig.add_trace(go.Bar(
#             x=monthly_data['month_label'],
#             y=monthly_data['net_revenue'],
#             name='Revenue',
#             marker_color='#3498db',
#             text=monthly_data['net_revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         # Profit margin line
#         fig.add_trace(go.Scatter(
#             x=monthly_data['month_label'],
#             y=monthly_data['margin_%'],
#             name='Profit Margin %',
#             yaxis='y2',
#             mode='lines+markers+text',
#             line=dict(color='#27ae60', width=3),
#             marker=dict(size=10),
#             text=monthly_data['margin_%'],
#             texttemplate='%{text:.1f}%',
#             textposition='top center',
#             hovertemplate='<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>'
#         ))
        
#         fig.update_layout(
#             yaxis=dict(title="Revenue (฿)", showgrid=True, gridcolor='lightgray'),
#             yaxis2=dict(
#                 title="Profit Margin (%)", 
#                 overlaying='y', 
#                 side='right',
#                 range=[0, 100],
#                 tickmode='linear',
#                 tick0=0,
#                 dtick=10,
#                 showgrid=False
#             ),
#             height=450,
#             hovermode='x unified',
#             showlegend=True,
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         st.markdown("**📈 Margin Gauge**")
#         current_margin = monthly_data['margin_%'].iloc[-1] if len(monthly_data) > 0 else 0
        
#         fig_gauge = go.Figure(go.Indicator(
#             mode="gauge+number+delta",
#             value=current_margin,
#             domain={'x': [0, 1], 'y': [0, 1]},
#             title={'text': "Current Month<br>Profit Margin"},
#             delta={'reference': monthly_data['margin_%'].iloc[-2] if len(monthly_data) >= 2 else current_margin},
#             gauge={
#                 'axis': {'range': [None, 100], 'ticksuffix': '%'},
#                 'bar': {'color': "#27ae60"},
#                 'steps': [
#                     {'range': [0, 30], 'color': "#e74c3c"},
#                     {'range': [30, 50], 'color': "#f39c12"},
#                     {'range': [50, 100], 'color': "#d5f4e6"}
#                 ],
#                 'threshold': {
#                     'line': {'color': "red", 'width': 4},
#                     'thickness': 0.75,
#                     'value': 40
#                 }
#             }
#         ))
        
#         fig_gauge.update_layout(height=450)
#         st.plotly_chart(fig_gauge, use_container_width=True)
    
#     # Daily Trend for Selected Month
#     st.markdown("**📅 Daily Sales Breakdown**")
    
#     # Month selector
#     available_months = sorted(df_filtered['order_month'].unique(), reverse=True)
#     month_labels = [m.strftime('%B %Y') for m in available_months]
    
#     col1, col2 = st.columns([1, 3])
#     with col1:
#         selected_month_label = st.selectbox("Select Month", month_labels, index=0)
#         selected_month = available_months[month_labels.index(selected_month_label)]
    
#     # Filter data for selected month
#     month_filtered = df_filtered[df_filtered['order_month'] == selected_month]
    
#     if len(month_filtered) > 0:
#         daily_data = month_filtered.groupby(month_filtered['order_date'].dt.date).agg({
#             'net_revenue': 'sum',
#             'profit': 'sum',
#             'order_id': 'nunique'
#         }).reset_index()
#         daily_data.columns = ['date', 'revenue', 'profit', 'orders']
#         daily_data['margin_%'] = (daily_data['profit'] / daily_data['revenue'] * 100).fillna(0)
        
#         fig_daily = go.Figure()
        
#         # Revenue line
#         fig_daily.add_trace(go.Scatter(
#             x=daily_data['date'],
#             y=daily_data['revenue'],
#             name='Daily Revenue',
#             mode='lines+markers',
#             line=dict(color='#3498db', width=2),
#             marker=dict(size=6),
#             fill='tozeroy',
#             fillcolor='rgba(52, 152, 219, 0.1)',
#             hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         # Orders line
#         fig_daily.add_trace(go.Scatter(
#             x=daily_data['date'],
#             y=daily_data['orders'],
#             name='Number of Orders',
#             mode='lines+markers',
#             line=dict(color='#9b59b6', width=2, dash='dash'),
#             marker=dict(size=6),
#             yaxis='y2',
#             hovertemplate='<b>%{x}</b><br>Orders: %{y}<extra></extra>'
#         ))
        
#         fig_daily.update_layout(
#             yaxis=dict(title="Revenue (฿)", showgrid=True, gridcolor='lightgray'),
#             yaxis2=dict(title="Number of Orders", overlaying='y', side='right', showgrid=False),
#             height=400,
#             hovermode='x unified',
#             showlegend=True,
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#         )
        
#         st.plotly_chart(fig_daily, use_container_width=True)
        
#         # Summary stats for selected month
#         col1, col2, col3, col4 = st.columns(4)
#         col1.metric("📊 Total Revenue", f"฿{daily_data['revenue'].sum():,.0f}")
#         col2.metric("📝 Total Orders", f"{daily_data['orders'].sum():,}")
#         col3.metric("📈 Avg Daily Revenue", f"฿{daily_data['revenue'].mean():,.0f}")
#         col4.metric("🎯 Best Day", f"฿{daily_data['revenue'].max():,.0f}")
#     else:
#         st.info("No data available for the selected month")
    
#     st.markdown("---")
    
#     # ==================== IMPROVED CHANNEL PERFORMANCE ====================
#     st.subheader("3️⃣ Channel Performance")
    
#     ch = df_filtered.groupby('channel').agg({
#         'net_revenue': 'sum', 
#         'profit': 'sum', 
#         'order_id': 'nunique', 
#         'user_id': 'nunique'
#     }).reset_index()
#     ch.columns = ['Channel', 'Revenue', 'Profit', 'Orders', 'Customers']
#     ch['Margin %'] = (ch['Profit'] / ch['Revenue'] * 100).round(1)
#     ch['AOV'] = (ch['Revenue'] / ch['Orders']).round(0)
#     ch = ch.sort_values('Revenue', ascending=False)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         fig = px.pie(
#             ch, 
#             values='Revenue', 
#             names='Channel', 
#             title="Revenue Distribution by Channel", 
#             hole=0.4,
#             color_discrete_sequence=px.colors.qualitative.Set3
#         )
#         fig.update_traces(
#             textposition='inside',
#             textinfo='percent+label',
#             hovertemplate='<b>%{label}</b><br>Revenue: ฿%{value:,.0f}<br>Share: %{percent}<extra></extra>'
#         )
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         fig = px.bar(
#             ch.sort_values('Revenue', ascending=True), 
#             x='Revenue', 
#             y='Channel', 
#             orientation='h',
#             title="Revenue by Channel (with Profit Margin)",
#             color='Margin %', 
#             color_continuous_scale='RdYlGn',
#             range_color=[0, 100],
#             text='Revenue'
#         )
#         fig.update_traces(
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<br>Margin: %{marker.color:.1f}%<extra></extra>'
#         )
#         st.plotly_chart(fig, use_container_width=True)
    
#     st.markdown("**📋 Detailed Channel Metrics**")
#     st.dataframe(
#         ch.style.format({
#             'Revenue': '฿{:,.0f}', 
#             'Profit': '฿{:,.0f}', 
#             'Orders': '{:,}',
#             'Customers': '{:,}', 
#             'Margin %': '{:.1f}%',
#             'AOV': '฿{:,.0f}'
#         }).background_gradient(subset=['Margin %'], cmap='RdYlGn', vmin=0, vmax=100),
#         use_container_width=True
#     )
    
#     st.markdown("---")
    
#     # ==================== IMPROVED PRODUCT PERFORMANCE ====================
#     st.subheader("4️⃣ Top Product Performance")
    
#     prod = df_filtered.groupby(['product_id', 'product_name', 'category']).agg({
#         'net_revenue': 'sum', 
#         'profit': 'sum', 
#         'quantity': 'sum'
#     }).reset_index()
#     prod.columns = ['ID', 'Product', 'Category', 'Revenue', 'Profit', 'Units']
#     prod['Margin %'] = (prod['Profit'] / prod['Revenue'] * 100).round(1)
#     prod = prod.sort_values('Revenue', ascending=False).head(20)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         top10 = prod.head(10).sort_values('Revenue', ascending=True)
#         fig = px.bar(
#             top10, 
#             x='Revenue', 
#             y='Product', 
#             orientation='h',
#             title="Top 10 Products by Revenue",
#             color='Margin %',
#             color_continuous_scale='RdYlGn',
#             range_color=[0, 100],
#             text='Revenue'
#         )
#         fig.update_traces(
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<br>Margin: %{marker.color:.1f}%<extra></extra>'
#         )
#         fig.update_layout(yaxis={'categoryorder': 'total ascending'})
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         fig = px.scatter(
#             prod, 
#             x='Revenue', 
#             y='Profit', 
#             size='Units',
#             color='Category',
#             hover_data=['Product'],
#             title="Revenue vs Profit (size = units sold)",
#             color_discrete_sequence=px.colors.qualitative.Set2
#         )
#         fig.update_traces(
#             hovertemplate='<b>%{customdata[0]}</b><br>Revenue: ฿%{x:,.0f}<br>Profit: ฿%{y:,.0f}<br>Units: %{marker.size}<extra></extra>'
#         )
#         st.plotly_chart(fig, use_container_width=True)
    
#     st.markdown("**📋 Top 20 Products Detail**")
#     st.dataframe(
#         prod.style.format({
#             'Revenue': '฿{:,.0f}', 
#             'Profit': '฿{:,.0f}',
#             'Units': '{:,}', 
#             'Margin %': '{:.1f}%'
#         }).background_gradient(subset=['Margin %'], cmap='RdYlGn', vmin=0, vmax=100),
#         use_container_width=True
#     )
    
#     st.markdown("---")
    
#     # ==================== IMPROVED CUSTOMER METRICS ====================
#     st.subheader("5️⃣ Customer Lifetime Value Metrics")
    
#     marketing_cost = df_filtered['discount_amount'].sum() if 'discount_amount' in df_filtered.columns else 0
#     new_cust = df_filtered['user_id'].nunique()
#     cac = marketing_cost / new_cust if new_cust > 0 else 0
    
#     analysis_date = df_filtered['order_date'].max()
#     last_purchase = df_filtered.groupby('user_id')['order_date'].max()
#     churned = ((analysis_date - last_purchase).dt.days > 90).sum()
#     churn = (churned / len(last_purchase) * 100) if len(last_purchase) > 0 else 0
#     retention = 100 - churn
    
#     avg_rev = df_filtered.groupby('user_id')['net_revenue'].sum().mean()
#     clv = (margin / 100) * (retention / 100) * avg_rev
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("💳 CAC", f"฿{cac:,.2f}", help="Customer Acquisition Cost (ค่าใช้จ่ายในการหาลูกค้าใหม่)")
#     col2.metric("🔄 Retention Rate", f"{retention:.1f}%", help="ลูกค้าที่ซื้อซ้ำภายใน 90 วัน")
#     col3.metric("❌ Churn Rate", f"{churn:.1f}%", help="ลูกค้าที่หายไป (ไม่ซื้อเกิน 90 วัน)")
#     col4.metric("💎 CLV", f"฿{clv:,.0f}", help="Customer Lifetime Value (มูลค่าของลูกค้าตลอดชีพ)")
    
#     # Customer cohort visualization
#     st.markdown("**👥 Customer Segmentation by Purchase Frequency**")
    
#     cust_orders = df_filtered.groupby('user_id')['order_id'].nunique().reset_index()
#     cust_orders.columns = ['user_id', 'order_count']
    
#     def segment_customer(count):
#         if count == 1:
#             return 'One-time'
#         elif count <= 3:
#             return 'Occasional'
#         elif count <= 5:
#             return 'Regular'
#         else:
#             return 'Loyal'
    
#     cust_orders['segment'] = cust_orders['order_count'].apply(segment_customer)
#     segment_dist = cust_orders['segment'].value_counts()
    
#     colors = {'One-time': '#e74c3c', 'Occasional': '#f39c12', 'Regular': '#3498db', 'Loyal': '#27ae60'}
#     fig = px.pie(
#         values=segment_dist.values,
#         names=segment_dist.index,
#         title="Customer Distribution by Purchase Frequency",
#         hole=0.4,
#         color=segment_dist.index,
#         color_discrete_map=colors
#     )
#     fig.update_traces(
#         textposition='inside',
#         textinfo='percent+label',
#         hovertemplate='<b>%{label}</b><br>Customers: %{value}<br>Share: %{percent}<extra></extra>'
#     )
#     st.plotly_chart(fig, use_container_width=True)

# with tab2:
#     st.header("📢 Marketing Analytics")
    
#     st.subheader("1️⃣ Campaign Effectiveness")
    
#     if 'campaign_type' in df_filtered.columns:
#         camp = df_filtered[df_filtered['campaign_type'].notna()]
#         no_camp = df_filtered[df_filtered['campaign_type'].isna()]
        
#         if len(camp) > 0:
#             camp_rev = camp['net_revenue'].sum()
#             camp_share = (camp_rev / revenue * 100) if revenue > 0 else 0
#             conv = (len(camp) / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
#             camp_aov = camp.groupby('order_id')['net_revenue'].sum().mean()
#             no_camp_aov = no_camp.groupby('order_id')['net_revenue'].sum().mean() if len(no_camp) > 0 else 0
            
#             camp_cost = camp['discount_amount'].sum() if 'discount_amount' in camp.columns else 0
#             roas = (camp_rev / camp_cost * 100) if camp_cost > 0 else 0
            
#             col1, col2, col3, col4 = st.columns(4)
#             col1.metric("📊 Campaign Revenue Share", f"{camp_share:.1f}%", help="สัดส่วนยอดขายจากแคมเปญ")
#             col2.metric("🎯 Conversion Rate", f"{conv:.1f}%", help="อัตราการซื้อจากแคมเปญ")
#             col3.metric("💰 ROAS", f"{roas:.0f}%", help="Return on Ad Spend (ผลตอบแทนจากการโฆษณา)")
#             col4.metric("🛒 Campaign AOV", f"฿{camp_aov:,.0f}", help="ค่าเฉลี่ยต่อออเดอร์จากแคมเปญ")
            
#             col1, col2 = st.columns(2)
#             with col1:
#                 comp = pd.DataFrame({
#                     'Type': ['With Campaign', 'Without Campaign'],
#                     'AOV': [camp_aov, no_camp_aov]
#                 })
#                 fig = px.bar(
#                     comp, 
#                     x='Type', 
#                     y='AOV',
#                     title="AOV Comparison: Campaign vs Non-Campaign",
#                     color='Type',
#                     text='AOV',
#                     color_discrete_map={'With Campaign': '#27ae60', 'Without Campaign': '#95a5a6'}
#                 )
#                 fig.update_traces(
#                     texttemplate='฿%{text:,.0f}',
#                     textposition='outside'
#                 )
#                 st.plotly_chart(fig, use_container_width=True)
            
#             with col2:
#                 camp_break = camp.groupby('campaign_type')['net_revenue'].sum().sort_values(ascending=False)
#                 fig = px.bar(
#                     x=camp_break.values,
#                     y=camp_break.index,
#                     orientation='h',
#                     title="Revenue by Campaign Type",
#                     labels={'x': 'Revenue', 'y': 'Campaign Type'},
#                     text=camp_break.values
#                 )
#                 fig.update_traces(
#                     texttemplate='฿%{text:,.0f}',
#                     textposition='outside',
#                     marker_color='#9b59b6'
#                 )
#                 st.plotly_chart(fig, use_container_width=True)
#     else:
#         st.info("Campaign data not available in the dataset")
    
#     st.markdown("---")
    
#     st.subheader("2️⃣ Acquisition Channel Analysis")
    
#     if 'acquisition_channel' in df_filtered.columns:
#         acq = df_filtered.groupby('acquisition_channel').agg({
#             'user_id': 'nunique',
#             'order_id': 'nunique',
#             'net_revenue': 'sum',
#             'profit': 'sum'
#         }).reset_index()
#         acq.columns = ['Channel', 'Customers', 'Orders', 'Revenue', 'Profit']
#         acq['Conv %'] = (acq['Orders'] / acq['Customers'] * 100).round(1)
#         acq['Rev/Cust'] = (acq['Revenue'] / acq['Customers']).round(0)
#         acq = acq.sort_values('Revenue', ascending=False)
        
#         col1, col2 = st.columns(2)
#         with col1:
#             fig = px.bar(
#                 acq.sort_values('Revenue', ascending=True),
#                 x='Revenue',
#                 y='Channel',
#                 orientation='h',
#                 title="Revenue by Acquisition Channel",
#                 text='Revenue',
#                 color='Conv %',
#                 color_continuous_scale='Blues'
#             )
#             fig.update_traces(
#                 texttemplate='฿%{text:,.0f}',
#                 textposition='outside'
#             )
#             st.plotly_chart(fig, use_container_width=True)
        
#         with col2:
#             fig = px.scatter(
#                 acq,
#                 x='Customers',
#                 y='Rev/Cust',
#                 size='Revenue',
#                 color='Channel',
#                 title="Customer Efficiency by Channel",
#                 labels={'Rev/Cust': 'Revenue per Customer'},
#                 color_discrete_sequence=px.colors.qualitative.Set2
#             )
#             fig.update_traces(
#                 hovertemplate='<b>%{fullData.name}</b><br>Customers: %{x}<br>Rev/Cust: ฿%{y:,.0f}<extra></extra>'
#             )
#             st.plotly_chart(fig, use_container_width=True)
        
#         st.markdown("**📋 Acquisition Channel Details**")
#         st.dataframe(
#             acq.style.format({
#                 'Revenue': '฿{:,.0f}',
#                 'Profit': '฿{:,.0f}',
#                 'Rev/Cust': '฿{:,.0f}',
#                 'Conv %': '{:.1f}%'
#             }).background_gradient(subset=['Conv %'], cmap='Blues'),
#             use_container_width=True
#         )
#     else:
#         st.info("Acquisition channel data not available in the dataset")
    
#     st.markdown("---")
    
#     st.subheader("3️⃣ RFM Customer Segmentation")
    
#     analysis_date = df_filtered['order_date'].max()
#     rfm = df_filtered.groupby('user_id').agg({
#         'order_date': lambda x: (analysis_date - x.max()).days,
#         'order_id': 'nunique',
#         'net_revenue': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     rfm.columns = ['user_id', 'recency', 'frequency', 'monetary', 'profit']
    
#     def safe_qcut(s, q, labels):
#         try:
#             return pd.qcut(s.rank(method='first'), q=q, labels=labels, duplicates='drop')
#         except:
#             return pd.Series([labels[0]] * len(s), index=s.index)
    
#     rfm['R'] = safe_qcut(rfm['recency'], 4, [4, 3, 2, 1])
#     rfm['F'] = safe_qcut(rfm['frequency'], 4, [1, 2, 3, 4])
#     rfm['M'] = safe_qcut(rfm['monetary'], 4, [1, 2, 3, 4])
#     rfm['RFM_Score'] = rfm[['R', 'F', 'M']].astype(int).sum(axis=1)
    
#     def segment(s):
#         if s >= 9:
#             return 'Champions'
#         elif s >= 6:
#             return 'Loyal Customers'
#         elif s >= 4:
#             return 'At Risk'
#         return 'Lost'
    
#     rfm['Segment'] = rfm['RFM_Score'].apply(segment)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         seg = rfm['Segment'].value_counts()
#         colors = {
#             'Champions': '#27ae60',
#             'Loyal Customers': '#3498db',
#             'At Risk': '#f39c12',
#             'Lost': '#e74c3c'
#         }
#         fig = px.pie(
#             values=seg.values,
#             names=seg.index,
#             hole=0.4,
#             title="Customer Segmentation by RFM Score",
#             color=seg.index,
#             color_discrete_map=colors
#         )
#         fig.update_traces(
#             textposition='inside',
#             textinfo='percent+label',
#             hovertemplate='<b>%{label}</b><br>Customers: %{value}<br>Share: %{percent}<extra></extra>'
#         )
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         seg_val = rfm.groupby('Segment')['monetary'].sum().sort_values(ascending=True)
#         fig = px.bar(
#             x=seg_val.values,
#             y=seg_val.index,
#             orientation='h',
#             title="Total Revenue by Customer Segment",
#             color=seg_val.index,
#             color_discrete_map=colors,
#             text=seg_val.values
#         )
#         fig.update_traces(
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside'
#         )
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Segment descriptions
#     st.markdown("**📊 Segment Descriptions:**")
#     col1, col2, col3, col4 = st.columns(4)
#     with col1:
#         st.success("**Champions** 🏆")
#         st.write("ลูกค้าระดับพรีเมียม ซื้อบ่อย ซื้อเยอะ ซื้อเมื่อไม่นานมานี้")
#     with col2:
#         st.info("**Loyal Customers** 💙")
#         st.write("ลูกค้าภักดี ซื้อสม่ำเสมอ มีศักยภาพเป็น Champions")
#     with col3:
#         st.warning("**At Risk** ⚠️")
#         st.write("ลูกค้าที่อาจจะหายไป ต้องดูแลเป็นพิเศษ")
#     with col4:
#         st.error("**Lost** 😢")
#         st.write("ลูกค้าที่หายไปแล้ว ต้องมีแคมเปญดึงกลับมา")

# with tab3:
#     st.header("💰 Financial Analytics")
    
#     st.subheader("1️⃣ Financial Summary")
    
#     cogs = df_filtered['cost'].sum()
#     gross_profit = revenue - cogs
#     gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
#     net_margin = (profit / revenue * 100) if revenue > 0 else 0
    
#     col1, col2, col3, col4, col5 = st.columns(5)
#     col1.metric("💵 Revenue", f"฿{revenue:,.0f}", help="ยอดขายรวม")
#     col2.metric("📦 COGS", f"฿{cogs:,.0f}", help="ต้นทุนสินค้า")
#     col3.metric("💚 Gross Profit", f"฿{gross_profit:,.0f}", f"{gross_margin:.1f}%", help="กำไรขั้นต้น")
#     col4.metric("💎 Net Profit", f"฿{profit:,.0f}", f"{net_margin:.1f}%", help="กำไรสุทธิ")
#     col5.metric("📊 ROS", f"{net_margin:.1f}%", help="Return on Sales (กำไรสุทธิ/ยอดขาย)")
    
#     st.markdown("---")
    
#     st.subheader("2️⃣ Monthly Financial Performance")
    
#     mon_fin = df_filtered.groupby('order_month').agg({
#         'net_revenue': 'sum',
#         'cost': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     mon_fin['order_month'] = mon_fin['order_month'].dt.to_timestamp()
#     mon_fin['margin_%'] = (mon_fin['profit'] / mon_fin['net_revenue'] * 100).round(2)
#     mon_fin['month_label'] = mon_fin['order_month'].dt.strftime('%b %Y')
    
#     fig = go.Figure()
    
#     # Revenue bars
#     fig.add_trace(go.Bar(
#         x=mon_fin['month_label'],
#         y=mon_fin['net_revenue'],
#         name='Revenue',
#         marker_color='#3498db',
#         hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#     ))
    
#     # COGS bars
#     fig.add_trace(go.Bar(
#         x=mon_fin['month_label'],
#         y=mon_fin['cost'],
#         name='COGS',
#         marker_color='#e74c3c',
#         hovertemplate='<b>%{x}</b><br>COGS: ฿%{y:,.0f}<extra></extra>'
#     ))
    
#     # Margin line
#     fig.add_trace(go.Scatter(
#         x=mon_fin['month_label'],
#         y=mon_fin['margin_%'],
#         name='Profit Margin %',
#         yaxis='y2',
#         mode='lines+markers',
#         line=dict(color='#27ae60', width=3),
#         marker=dict(size=10),
#         hovertemplate='<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>'
#     ))
    
#     fig.update_layout(
#         yaxis=dict(title="Amount (฿)", showgrid=True),
#         yaxis2=dict(title="Profit Margin (%)", overlaying='y', side='right', showgrid=False),
#         barmode='group',
#         height=400,
#         hovermode='x unified',
#         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#     )
    
#     st.plotly_chart(fig, use_container_width=True)
    
#     st.markdown("---")
    
#     st.subheader("3️⃣ Working Capital Ratios")
    
#     avg_monthly_rev = mon_fin['net_revenue'].mean()
#     avg_ar = avg_monthly_rev * 0.3
#     ar_turnover = revenue * 0.3 / avg_ar if avg_ar > 0 else 0
#     dso = 365 / ar_turnover if ar_turnover > 0 else 0
    
#     avg_ap = cogs * 0.25
#     ap_turnover = cogs / avg_ap if avg_ap > 0 else 0
#     dpo = 365 / ap_turnover if ap_turnover > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("🔄 AR Turnover", f"{ar_turnover:.2f}x", help="เร็วเท่าไรที่เราเก็บเงินจากลูกค้าได้")
#     col2.metric("📅 DSO", f"{dso:.0f} days", help="Days Sales Outstanding (จำนวนวันที่เก็บเงินได้)")
#     col3.metric("🔄 AP Turnover", f"{ap_turnover:.2f}x", help="เร็วเท่าไรที่เราจ่ายเงินซัพพลายเออร์")
#     col4.metric("📅 DPO", f"{dpo:.0f} days", help="Days Payable Outstanding (จำนวนวันที่เราจ่ายเงิน)")

# with tab4:
#     st.header("📦 Warehouse & Inventory Management")
    
#     st.subheader("1️⃣ Inventory Performance Metrics")
    
#     avg_inv = df_filtered['cost'].mean() * df_filtered['product_id'].nunique()
#     inv_turnover = cogs / avg_inv if avg_inv > 0 else 0
#     dio = 365 / inv_turnover if inv_turnover > 0 else 0
    
#     units_sold = df_filtered['quantity'].sum()
#     units_received = units_sold * 1.2
#     sell_through = (units_sold / units_received * 100) if units_received > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("🔄 Inventory Turnover", f"{inv_turnover:.2f}x", help="จำนวนครั้งที่สินค้าหมุนเวียนต่อปี")
#     col2.metric("📅 DIO", f"{dio:.0f} days", help="Days Inventory Outstanding (จำนวนวันที่สินค้าอยู่ในคลัง)")
#     col3.metric("📈 Sell-Through Rate", f"{sell_through:.1f}%", help="อัตราการขายสินค้าที่รับเข้ามา")
#     col4.metric("💰 Inventory Value", f"฿{avg_inv:,.0f}", help="มูลค่าสินค้าคงคลัง")
    
#     st.markdown("---")
    
#     st.subheader("2️⃣ Product Movement Analysis")
    
#     prod_vel = df_filtered.groupby(['product_id', 'product_name', 'category']).agg({
#         'order_id': 'nunique',
#         'net_revenue': 'sum',
#         'cost': 'sum',
#         'quantity': 'sum'
#     }).reset_index()
#     prod_vel.columns = ['ID', 'Product', 'Category', 'Orders', 'Revenue', 'Cost', 'Units']
    
#     fast_th = prod_vel['Orders'].quantile(0.75)
#     slow_th = prod_vel['Orders'].quantile(0.25)
    
#     def classify(cnt):
#         if cnt >= fast_th:
#             return 'Fast Moving'
#         elif cnt <= slow_th:
#             return 'Slow Moving'
#         return 'Medium Moving'
    
#     prod_vel['Movement'] = prod_vel['Orders'].apply(classify)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         mov = prod_vel['Movement'].value_counts()
#         colors = {
#             'Fast Moving': '#27ae60',
#             'Medium Moving': '#f39c12',
#             'Slow Moving': '#e74c3c'
#         }
#         fig = px.pie(
#             values=mov.values,
#             names=mov.index,
#             hole=0.4,
#             title="Product Distribution by Movement Speed",
#             color=mov.index,
#             color_discrete_map=colors
#         )
#         fig.update_traces(
#             textposition='inside',
#             textinfo='percent+label',
#             hovertemplate='<b>%{label}</b><br>Products: %{value}<br>Share: %{percent}<extra></extra>'
#         )
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         mov_val = prod_vel.groupby('Movement')['Cost'].sum().sort_values(ascending=True)
#         fig = px.bar(
#             x=mov_val.values,
#             y=mov_val.index,
#             orientation='h',
#             title="Inventory Value by Movement Speed",
#             color=mov_val.index,
#             color_discrete_map=colors,
#             text=mov_val.values
#         )
#         fig.update_traces(
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside'
#         )
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Movement recommendations
#     st.markdown("**💡 Inventory Recommendations:**")
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         st.success("**Fast Moving** 🚀")
#         st.write("- เพิ่ม stock level")
#         st.write("- ลดโอกาสขาดสต็อก")
#         st.write("- พิจารณา bulk order")
#     with col2:
#         st.info("**Medium Moving** ⚖️")
#         st.write("- รักษาระดับ stock ปกติ")
#         st.write("- ติดตาม trend")
#         st.write("- พิจารณาโปรโมชั่น")
#     with col3:
#         st.warning("**Slow Moving** 🐌")
#         st.write("- ลด stock level")
#         st.write("- จัด clearance sale")
#         st.write("- หยุดสั่งซื้อชั่วคราว")
    
#     st.markdown("---")
    
#     col1, col2 = st.columns(2)
#     with col1:
#         st.markdown("#### 🚀 Top 10 Fast Moving Products")
#         fast = prod_vel[prod_vel['Movement'] == 'Fast Moving'].nlargest(10, 'Orders')
#         st.dataframe(
#             fast[['Product', 'Category', 'Orders', 'Units', 'Revenue']].style.format({
#                 'Revenue': '฿{:,.0f}',
#                 'Orders': '{:,}',
#                 'Units': '{:,}'
#             }),
#             height=350,
#             use_container_width=True
#         )
    
#     with col2:
#         st.markdown("#### 🐌 Top 10 Slow Moving Products")
#         slow = prod_vel[prod_vel['Movement'] == 'Slow Moving'].nlargest(10, 'Cost')
#         st.dataframe(
#             slow[['Product', 'Category', 'Orders', 'Units', 'Cost']].style.format({
#                 'Cost': '฿{:,.0f}',
#                 'Orders': '{:,}',
#                 'Units': '{:,}'
#             }),
#             height=350,
#             use_container_width=True
#         )
    
#     st.markdown("---")
    
#     st.subheader("3️⃣ Cash Conversion Cycle")
    
#     ccc = dio + dso - dpo
    
#     st.markdown("""
#     **Cash Conversion Cycle (CCC)** คือระยะเวลาที่เงินสดถูกล็อคอยู่ในธุรกิจ ตั้งแต่จ่ายเงินซื้อสินค้า จนกระทั่งได้รับเงินจากลูกค้า
    
#     - **สูตร:** CCC = DIO + DSO - DPO
#     - **เป้าหมาย:** ยิ่งต่ำยิ่งดี (แสดงว่าเงินสดหมุนเวียนเร็ว)
#     """)
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("📦 DIO", f"{dio:.0f} days", help="วันที่สินค้าอยู่ในคลัง")
#     col2.metric("💳 DSO", f"{dso:.0f} days", help="วันที่รอเก็บเงินจากลูกค้า")
#     col3.metric("💰 DPO", f"{dpo:.0f} days", help="วันที่เราจ่ายเงินซัพพลายเออร์")
#     col4.metric("⏱️ CCC", f"{ccc:.0f} days", 
#                 help="ระยะเวลารอบวงจรเงินสด (ยิ่งต่ำยิ่งดี)",
#                 delta=f"{'Better' if ccc < 60 else 'Needs improvement'}")
    
#     # CCC visualization
#     fig = go.Figure()
    
#     fig.add_trace(go.Bar(
#         x=['DIO', 'DSO', 'DPO', 'CCC'],
#         y=[dio, dso, -dpo, ccc],
#         text=[f"{dio:.0f}", f"{dso:.0f}", f"{dpo:.0f}", f"{ccc:.0f}"],
#         textposition='outside',
#         marker_color=['#3498db', '#9b59b6', '#e74c3c', '#27ae60'],
#         hovertemplate='<b>%{x}</b><br>Days: %{y:.0f}<extra></extra>'
#     ))
    
#     fig.update_layout(
#         title="Cash Conversion Cycle Breakdown (days)",
#         yaxis_title="Days",
#         height=400,
#         showlegend=False
#     )
    
#     st.plotly_chart(fig, use_container_width=True)
    
#     # CCC interpretation
#     if ccc < 30:
#         st.success("✅ **Excellent!** CCC ต่ำมาก เงินสดหมุนเวียนได้อย่างรวดเร็ว")
#     elif ccc < 60:
#         st.info("✔️ **Good!** CCC อยู่ในเกณฑ์ดี แต่ยังมีพื้นที่ปรับปรุงได้")
#     elif ccc < 90:
#         st.warning("⚠️ **Fair** CCC สูงพอสมควร ควรพิจารณาปรับปรุงการจัดการเงินสด")
#     else:
#         st.error("❌ **Needs Attention!** CCC สูงเกินไป เงินสดถูกล็อคอยู่นานเกินไป")

# st.markdown("---")
# st.markdown("""
# <div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px;'>
#     <h4>📊 Fashion E-commerce Analytics Dashboard</h4>
#     <p>Built with Streamlit | Data-Driven Insights for Better Business Decisions</p>
# </div>
# """, unsafe_allow_html=True)















































# # Analytics Dashboard - Fixed Version
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# import numpy as np
# import warnings
# from datetime import datetime, timedelta

# warnings.filterwarnings('ignore')
# st.set_page_config(page_title="Fashion Analytics Pro", layout="wide", page_icon="👕")

# # Channel Color Mapping - consistent across all charts
# CHANNEL_COLORS = {
#     'TikTok': '#000000',      # Black
#     'Shopee': '#FF5722',      # Orange
#     'Lazada': '#1E88E5',      # Blue
#     'LINE Shopping': '#00C300', # Green
#     'Instagram': '#9C27B0',   # Purple
#     'Facebook': '#1877F2',    # FB Blue
#     'Store': '#795548',       # Brown
#     'Pop-up': '#FF9800',      # Amber
#     'Website': '#607D8B'      # Blue Grey
# }

# # Initialize session state
# if 'data_loaded' not in st.session_state:
#     st.session_state.data_loaded = False
# if 'data' not in st.session_state:
#     st.session_state.data = {}

# REQUIRED_COLUMNS = {
#     'users': ['user_id', 'customer_type', 'created_at'],
#     'products': ['product_id', 'category', 'sale_price', 'cost'],
#     'orders': ['order_id', 'user_id', 'order_date', 'channel', 'status'],
#     'order_items': ['order_id', 'product_id', 'quantity', 'net_revenue', 'cost', 'profit']
# }

# def load_data():
#     st.sidebar.title("Analytics Dashboard")
#     st.sidebar.markdown("---")
    
#     # Fixed: Added unique key to prevent duplicate element ID
#     uploaded = st.sidebar.file_uploader(
#         "📁 Upload CSV Files", 
#         type=['csv'], 
#         accept_multiple_files=True,
#         key="csv_uploader_main"  # Unique key added
#     )
    
#     if uploaded and st.sidebar.button("🔄 Load Data", type="primary", key="load_data_btn"):
#         data = {}
#         mapping = {
#             "users.csv": "users", 
#             "products.csv": "products", 
#             "orders.csv": "orders", 
#             "order_items.csv": "order_items", 
#             "inventory_movements.csv": "inventory"
#         }
        
#         for file in uploaded:
#             if file.name in mapping:
#                 try:
#                     df = pd.read_csv(file)
#                     table = mapping[file.name]
#                     if table in REQUIRED_COLUMNS:
#                         missing = [c for c in REQUIRED_COLUMNS[table] if c not in df.columns]
#                         if not missing:
#                             data[table] = df
#                             st.sidebar.success(f"✅ {file.name}")
#                         else:
#                             st.sidebar.error(f"❌ {file.name} - Missing: {', '.join(missing)}")
#                     else:
#                         data[table] = df
#                         st.sidebar.success(f"✅ {file.name}")
#                 except Exception as e:
#                     st.sidebar.error(f"❌ {file.name}: {str(e)}")
        
#         if all(t in data for t in ['users', 'products', 'orders', 'order_items']):
#             st.session_state.data = data
#             st.session_state.data_loaded = True
#             st.sidebar.success("✅ All data loaded!")
#             st.rerun()
#         else:
#             st.sidebar.error("❌ Missing required tables")
    
#     return st.session_state.data if st.session_state.data_loaded else None

# @st.cache_data
# def merge_data(data):
#     df = data['order_items'].copy()
#     df = df.merge(data['orders'], on='order_id', how='left', suffixes=('', '_o'))
#     df = df.merge(data['products'], on='product_id', how='left', suffixes=('', '_p'))
#     df = df.merge(data['users'], on='user_id', how='left', suffixes=('', '_u'))
    
#     for col in ['order_date', 'created_at']:
#         if col in df.columns:
#             df[col] = pd.to_datetime(df[col], errors='coerce')
    
#     if 'order_date' in df.columns:
#         df['order_month'] = df['order_date'].dt.to_period('M')
#         df['order_year'] = df['order_date'].dt.year
#         df['order_day'] = df['order_date'].dt.day
    
#     online = ['Shopee', 'Lazada', 'TikTok', 'LINE Shopping']
#     df['channel_type'] = df['channel'].apply(lambda x: 'Online' if x in online else 'Offline')
    
#     return df

# data = load_data()

# if not data:
#     st.title("Analytics Dashboard")
#     st.info("👈 Please upload CSV files to begin")
    
#     st.markdown("### 📋 Required Columns")
#     col1, col2 = st.columns(2)
#     with col1:
#         st.code("users.csv:\n- user_id\n- customer_type\n- created_at")
#         st.code("orders.csv:\n- order_id\n- user_id\n- order_date\n- channel\n- status")
#     with col2:
#         st.code("products.csv:\n- product_id\n- category\n- sale_price\n- cost")
#         st.code("order_items.csv:\n- order_id\n- product_id\n- quantity\n- net_revenue\n- cost\n- profit")
#     st.stop()

# df_master = merge_data(data)

# # ==================== IMPROVED FILTERS ====================
# st.sidebar.markdown("---")
# st.sidebar.markdown("### 🔍 Filters")

# # Date Range Filter with Quick Selections
# min_date = df_master['order_date'].min().date()
# max_date = df_master['order_date'].max().date()

# st.sidebar.markdown("**📅 Select Time Period:**")
# period_options = ["Custom Range", "Last 7 Days", "Last 30 Days", "Last 90 Days", "This Month", "Last Month", "This Quarter", "This Year", "All Time"]
# selected_period = st.sidebar.selectbox("Quick Select", period_options, index=0, key="period_selector")

# # Calculate date range based on selection
# if selected_period == "Last 7 Days":
#     start_date = max_date - timedelta(days=7)
#     end_date = max_date
# elif selected_period == "Last 30 Days":
#     start_date = max_date - timedelta(days=30)
#     end_date = max_date
# elif selected_period == "Last 90 Days":
#     start_date = max_date - timedelta(days=90)
#     end_date = max_date
# elif selected_period == "This Month":
#     start_date = max_date.replace(day=1)
#     end_date = max_date
# elif selected_period == "Last Month":
#     first_day_this_month = max_date.replace(day=1)
#     end_date = first_day_this_month - timedelta(days=1)
#     start_date = end_date.replace(day=1)
# elif selected_period == "This Quarter":
#     quarter = (max_date.month - 1) // 3
#     start_date = datetime(max_date.year, quarter * 3 + 1, 1).date()
#     end_date = max_date
# elif selected_period == "This Year":
#     start_date = datetime(max_date.year, 1, 1).date()
#     end_date = max_date
# elif selected_period == "All Time":
#     start_date = min_date
#     end_date = max_date
# else:  # Custom Range
#     date_range = st.sidebar.date_input(
#         "Select Custom Range", 
#         [min_date, max_date], 
#         min_value=min_date, 
#         max_value=max_date,
#         key="custom_date_range"
#     )
#     if len(date_range) == 2:
#         start_date, end_date = date_range
#     else:
#         start_date, end_date = min_date, max_date

# # Display selected date range
# st.sidebar.info(f"📆 From: {start_date.strftime('%d %b %Y')}\n\n📆 To: {end_date.strftime('%d %b %Y')}")

# df_filtered = df_master[(df_master['order_date'].dt.date >= start_date) & 
#                         (df_master['order_date'].dt.date <= end_date)]

# st.sidebar.markdown("---")

# # Other Filters
# channels = st.sidebar.multiselect(
#     "🏪 Channel", 
#     df_filtered['channel'].unique(), 
#     df_filtered['channel'].unique(),
#     key="channel_filter"
# )
# df_filtered = df_filtered[df_filtered['channel'].isin(channels)]

# statuses = st.sidebar.multiselect(
#     "📦 Status", 
#     df_filtered['status'].unique(), 
#     ['Completed'],
#     key="status_filter"
# )
# df_filtered = df_filtered[df_filtered['status'].isin(statuses)]

# # Display metrics in sidebar
# st.sidebar.markdown("---")
# st.sidebar.markdown("### 📊 Quick Stats")
# st.sidebar.metric("💰 Total Revenue", f"฿{df_filtered['net_revenue'].sum():,.0f}")
# st.sidebar.metric("💵 Total Profit", f"฿{df_filtered['profit'].sum():,.0f}")
# st.sidebar.metric("📝 Total Orders", f"{df_filtered['order_id'].nunique():,}")
# st.sidebar.metric("👥 Total Customers", f"{df_filtered['user_id'].nunique():,}")

# tab1, tab2, tab3, tab4 = st.tabs(["💼 Sales", "📢 Marketing", "💰 Financial", "📦 Warehouse"])

# with tab1:
#     st.header("💼 Sales Analytics")
    
#     st.subheader("1️⃣ Key Performance Indicators")
    
#     revenue = df_filtered['net_revenue'].sum()
#     profit = df_filtered['profit'].sum()
#     margin = (profit / revenue * 100) if revenue > 0 else 0
    
#     monthly = df_filtered.groupby('order_month')['net_revenue'].sum().sort_index()
#     growth = ((monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2] * 100) if len(monthly) >= 2 else 0
    
#     aov = df_filtered.groupby('order_id')['net_revenue'].sum().mean()
#     target = 5000000
#     curr_sales = df_filtered[df_filtered['order_month'] == df_filtered['order_month'].max()]['net_revenue'].sum()
#     attainment = (curr_sales / target * 100) if target > 0 else 0
    
#     col1, col2, col3, col4, col5 = st.columns(5)
#     col1.metric("📈 Monthly Growth", f"{growth:+.1f}%", help="เปรียบเทียบเดือนปัจจุบันกับเดือนที่แล้ว")
#     col2.metric("💹 Profit Margin", f"{margin:.1f}%", help="กำไรหารด้วยยอดขาย")
#     col3.metric("🎯 Target Achievement", f"{attainment:.1f}%", help="เทียบกับเป้า 5M/เดือน")
#     col4.metric("🛒 Avg Order Value", f"฿{aov:,.0f}", help="ยอดขายเฉลี่ยต่อออเดอร์")
#     col5.metric("👥 Total Customers", f"{df_filtered['user_id'].nunique():,}", help="จำนวนลูกค้าทั้งหมด")
    
#     # ==================== IMPROVED SALES TREND ====================
#     st.subheader("2️⃣ Sales Trend Analysis")
    
#     # Monthly Bar Chart with Profit Margin %
#     monthly_data = df_filtered.groupby('order_month').agg({
#         'net_revenue': 'sum', 
#         'cost': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     monthly_data['order_month'] = monthly_data['order_month'].dt.to_timestamp()
#     monthly_data['margin_%'] = (monthly_data['profit'] / monthly_data['net_revenue'] * 100).clip(0, 100)
#     monthly_data['month_label'] = monthly_data['order_month'].dt.strftime('%b %Y')
    
#     col1, col2 = st.columns([2, 1])
    
#     with col1:
#         st.markdown("**📊 Monthly Revenue & Profit Margin**")
#         fig = go.Figure()
        
#         # Revenue bars
#         fig.add_trace(go.Bar(
#             x=monthly_data['month_label'],
#             y=monthly_data['net_revenue'],
#             name='Revenue',
#             marker_color='#3498db',
#             text=monthly_data['net_revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         # Profit margin line
#         fig.add_trace(go.Scatter(
#             x=monthly_data['month_label'],
#             y=monthly_data['margin_%'],
#             name='Profit Margin %',
#             yaxis='y2',
#             mode='lines+markers+text',
#             line=dict(color='#27ae60', width=3),
#             marker=dict(size=10),
#             text=monthly_data['margin_%'],
#             texttemplate='%{text:.1f}%',
#             textposition='top center',
#             hovertemplate='<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>'
#         ))
        
#         fig.update_layout(
#             yaxis=dict(title="Revenue (฿)", showgrid=True, gridcolor='lightgray'),
#             yaxis2=dict(
#                 title="Profit Margin (%)", 
#                 overlaying='y', 
#                 side='right',
#                 range=[0, 100],
#                 tickmode='linear',
#                 tick0=0,
#                 dtick=10,
#                 showgrid=False
#             ),
#             height=450,
#             hovermode='x unified',
#             showlegend=True,
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="monthly_revenue_chart")
    
#     with col2:
#         st.markdown("**📈 Margin Gauge**")
#         current_margin = monthly_data['margin_%'].iloc[-1] if len(monthly_data) > 0 else 0
        
#         fig_gauge = go.Figure(go.Indicator(
#             mode="gauge+number+delta",
#             value=current_margin,
#             domain={'x': [0, 1], 'y': [0, 1]},
#             title={'text': "Current Month<br>Profit Margin"},
#             delta={'reference': monthly_data['margin_%'].iloc[-2] if len(monthly_data) >= 2 else current_margin},
#             gauge={
#                 'axis': {'range': [None, 100], 'ticksuffix': '%'},
#                 'bar': {'color': "#27ae60"},
#                 'steps': [
#                     {'range': [0, 30], 'color': "#e74c3c"},
#                     {'range': [30, 50], 'color': "#f39c12"},
#                     {'range': [50, 100], 'color': "#d5f4e6"}
#                 ],
#                 'threshold': {
#                     'line': {'color': "red", 'width': 4},
#                     'thickness': 0.75,
#                     'value': 40
#                 }
#             }
#         ))
        
#         fig_gauge.update_layout(height=450)
#         st.plotly_chart(fig_gauge, use_container_width=True, key="margin_gauge_chart")
    
#     # Daily Trend for Selected Month
#     st.markdown("**📅 Daily Sales Breakdown**")
    
#     # Month selector
#     available_months = sorted(df_filtered['order_month'].unique(), reverse=True)
#     month_labels = [m.strftime('%B %Y') for m in available_months]
    
#     col1, col2 = st.columns([1, 3])
#     with col1:
#         selected_month_label = st.selectbox("Select Month", month_labels, index=0, key="month_selector_daily")
#         selected_month = available_months[month_labels.index(selected_month_label)]
    
#     # Filter data for selected month
#     month_filtered = df_filtered[df_filtered['order_month'] == selected_month]
    
#     if len(month_filtered) > 0:
#         daily_data = month_filtered.groupby(month_filtered['order_date'].dt.date).agg({
#             'net_revenue': 'sum',
#             'profit': 'sum',
#             'order_id': 'nunique'
#         }).reset_index()
#         daily_data.columns = ['date', 'revenue', 'profit', 'orders']
#         daily_data['margin_%'] = (daily_data['profit'] / daily_data['revenue'] * 100).fillna(0)
        
#         fig_daily = go.Figure()
        
#         # Revenue line
#         fig_daily.add_trace(go.Scatter(
#             x=daily_data['date'],
#             y=daily_data['revenue'],
#             name='Daily Revenue',
#             mode='lines+markers',
#             line=dict(color='#3498db', width=2),
#             marker=dict(size=6),
#             fill='tozeroy',
#             fillcolor='rgba(52, 152, 219, 0.1)',
#             hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         # Orders line
#         fig_daily.add_trace(go.Scatter(
#             x=daily_data['date'],
#             y=daily_data['orders'],
#             name='Number of Orders',
#             mode='lines+markers',
#             line=dict(color='#9b59b6', width=2, dash='dash'),
#             marker=dict(size=6),
#             yaxis='y2',
#             hovertemplate='<b>%{x}</b><br>Orders: %{y}<extra></extra>'
#         ))
        
#         fig_daily.update_layout(
#             yaxis=dict(title="Revenue (฿)", showgrid=True, gridcolor='lightgray'),
#             yaxis2=dict(title="Number of Orders", overlaying='y', side='right', showgrid=False),
#             height=400,
#             hovermode='x unified',
#             showlegend=True,
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#         )
        
#         st.plotly_chart(fig_daily, use_container_width=True, key="daily_trend_chart")
        
#         # Summary stats for selected month
#         col1, col2, col3, col4 = st.columns(4)
#         col1.metric("📊 Total Revenue", f"฿{daily_data['revenue'].sum():,.0f}")
#         col2.metric("📝 Total Orders", f"{daily_data['orders'].sum():,}")
#         col3.metric("📈 Avg Daily Revenue", f"฿{daily_data['revenue'].mean():,.0f}")
#         col4.metric("🎯 Best Day", f"฿{daily_data['revenue'].max():,.0f}")
#     else:
#         st.info("No data available for the selected month")
    
#     st.markdown("---")
    
#     # ==================== IMPROVED CHANNEL PERFORMANCE ====================
#     st.subheader("3️⃣ Channel Performance")
    
#     ch = df_filtered.groupby('channel').agg({
#         'net_revenue': 'sum', 
#         'profit': 'sum', 
#         'order_id': 'nunique', 
#         'user_id': 'nunique'
#     }).reset_index()
#     ch.columns = ['Channel', 'Revenue', 'Profit', 'Orders', 'Customers']
#     ch['Margin %'] = (ch['Profit'] / ch['Revenue'] * 100).round(1)
#     ch['AOV'] = (ch['Revenue'] / ch['Orders']).round(0)
#     ch = ch.sort_values('Revenue', ascending=False)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         fig = px.pie(
#             ch, 
#             values='Revenue', 
#             names='Channel', 
#             title="Revenue Distribution by Channel", 
#             hole=0.4,
#             color='Channel',
#             color_discrete_map=CHANNEL_COLORS
#         )
#         fig.update_traces(
#             textposition='inside',
#             textinfo='percent+label',
#             hovertemplate='<b>%{label}</b><br>Revenue: ฿%{value:,.0f}<br>Share: %{percent}<extra></extra>'
#         )
#         st.plotly_chart(fig, use_container_width=True, key="channel_pie_chart")
    
#     with col2:
#         # Create color list matching the sorted channel order
#         ch_sorted = ch.sort_values('Revenue', ascending=True)
#         colors_list = [CHANNEL_COLORS.get(channel, '#95a5a6') for channel in ch_sorted['Channel']]
        
#         fig = go.Figure()
#         fig.add_trace(go.Bar(
#             x=ch_sorted['Revenue'],
#             y=ch_sorted['Channel'],
#             orientation='h',
#             marker=dict(
#                 color=colors_list,
#                 line=dict(color='white', width=1)
#             ),
#             text=ch_sorted['Revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<br>Margin: %{customdata:.1f}%<extra></extra>',
#             customdata=ch_sorted['Margin %']
#         ))
        
#         fig.update_layout(
#             title="Revenue by Channel",
#             xaxis_title="Revenue (฿)",
#             yaxis_title="Channel",
#             showlegend=False,
#             height=400
#         )
#         st.plotly_chart(fig, use_container_width=True, key="channel_bar_chart")
    
#     st.markdown("**📋 Detailed Channel Metrics**")
#     st.dataframe(
#         ch.style.format({
#             'Revenue': '฿{:,.0f}', 
#             'Profit': '฿{:,.0f}', 
#             'Orders': '{:,}',
#             'Customers': '{:,}', 
#             'Margin %': '{:.1f}%',
#             'AOV': '฿{:,.0f}'
#         }).background_gradient(subset=['Margin %'], cmap='RdYlGn', vmin=0, vmax=100),
#         use_container_width=True
#     )
    
#     st.markdown("---")
    
#     # ==================== IMPROVED PRODUCT PERFORMANCE ====================
#     st.subheader("4️⃣ Top Product Performance")
    
#     prod = df_filtered.groupby(['product_id', 'product_name', 'category']).agg({
#         'net_revenue': 'sum', 
#         'profit': 'sum', 
#         'quantity': 'sum'
#     }).reset_index()
#     prod.columns = ['ID', 'Product', 'Category', 'Revenue', 'Profit', 'Units']
#     prod['Margin %'] = (prod['Profit'] / prod['Revenue'] * 100).round(1)
#     prod = prod.sort_values('Revenue', ascending=False).head(20)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         top10 = prod.head(10).sort_values('Revenue', ascending=True)
#         fig = px.bar(
#             top10, 
#             x='Revenue', 
#             y='Product', 
#             orientation='h',
#             title="Top 10 Products by Revenue",
#             color='Margin %',
#             color_continuous_scale='RdYlGn',
#             range_color=[0, 100],
#             text='Revenue'
#         )
#         fig.update_traces(
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<br>Margin: %{marker.color:.1f}%<extra></extra>'
#         )
#         fig.update_layout(yaxis={'categoryorder': 'total ascending'})
#         st.plotly_chart(fig, use_container_width=True, key="product_top10_chart")
    
#     with col2:
#         fig = px.scatter(
#             prod, 
#             x='Revenue', 
#             y='Profit', 
#             size='Units',
#             color='Category',
#             hover_data=['Product'],
#             title="Revenue vs Profit (size = units sold)",
#             color_discrete_sequence=px.colors.qualitative.Set2
#         )
#         fig.update_traces(
#             hovertemplate='<b>%{customdata[0]}</b><br>Revenue: ฿%{x:,.0f}<br>Profit: ฿%{y:,.0f}<br>Units: %{marker.size}<extra></extra>'
#         )
#         st.plotly_chart(fig, use_container_width=True, key="product_scatter_chart")
    
#     st.markdown("**📋 Top 20 Products Detail**")
#     st.dataframe(
#         prod.style.format({
#             'Revenue': '฿{:,.0f}', 
#             'Profit': '฿{:,.0f}',
#             'Units': '{:,}', 
#             'Margin %': '{:.1f}%'
#         }).background_gradient(subset=['Margin %'], cmap='RdYlGn', vmin=0, vmax=100),
#         use_container_width=True
#     )
    
#     st.markdown("---")
    
#     # ==================== IMPROVED CUSTOMER METRICS ====================
#     st.subheader("5️⃣ Customer Lifetime Value Metrics")
    
#     marketing_cost = df_filtered['discount_amount'].sum() if 'discount_amount' in df_filtered.columns else 0
#     new_cust = df_filtered['user_id'].nunique()
#     cac = marketing_cost / new_cust if new_cust > 0 else 0
    
#     analysis_date = df_filtered['order_date'].max()
#     last_purchase = df_filtered.groupby('user_id')['order_date'].max()
#     churned = ((analysis_date - last_purchase).dt.days > 90).sum()
#     churn = (churned / len(last_purchase) * 100) if len(last_purchase) > 0 else 0
#     retention = 100 - churn
    
#     avg_rev = df_filtered.groupby('user_id')['net_revenue'].sum().mean()
#     clv = (margin / 100) * (retention / 100) * avg_rev
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("💳 CAC", f"฿{cac:,.2f}", help="Customer Acquisition Cost (ค่าใช้จ่ายในการหาลูกค้าใหม่)")
#     col2.metric("🔄 Retention Rate", f"{retention:.1f}%", help="ลูกค้าที่ซื้อซ้ำภายใน 90 วัน")
#     col3.metric("❌ Churn Rate", f"{churn:.1f}%", help="ลูกค้าที่หายไป (ไม่ซื้อเกิน 90 วัน)")
#     col4.metric("💎 CLV", f"฿{clv:,.0f}", help="Customer Lifetime Value (มูลค่าของลูกค้าตลอดชีพ)")
    
#     # Customer cohort visualization
#     st.markdown("**👥 Customer Segmentation by Purchase Frequency**")
    
#     cust_orders = df_filtered.groupby('user_id')['order_id'].nunique().reset_index()
#     cust_orders.columns = ['user_id', 'order_count']
    
#     def segment_customer(count):
#         if count == 1:
#             return 'One-time'
#         elif count <= 3:
#             return 'Occasional'
#         elif count <= 5:
#             return 'Regular'
#         else:
#             return 'Loyal'
    
#     cust_orders['segment'] = cust_orders['order_count'].apply(segment_customer)
#     segment_dist = cust_orders['segment'].value_counts()
    
#     colors = {'One-time': '#e74c3c', 'Occasional': '#f39c12', 'Regular': '#3498db', 'Loyal': '#27ae60'}
#     fig = px.pie(
#         values=segment_dist.values,
#         names=segment_dist.index,
#         title="Customer Distribution by Purchase Frequency",
#         hole=0.4,
#         color=segment_dist.index,
#         color_discrete_map=colors
#     )
#     fig.update_traces(
#         textposition='inside',
#         textinfo='percent+label',
#         hovertemplate='<b>%{label}</b><br>Customers: %{value}<br>Share: %{percent}<extra></extra>'
#     )
#     st.plotly_chart(fig, use_container_width=True, key="customer_segment_chart")

# with tab2:
#     st.header("📢 Marketing Analytics")
    
#     st.subheader("1️⃣ Campaign Effectiveness")
    
#     if 'campaign_type' in df_filtered.columns:
#         camp = df_filtered[df_filtered['campaign_type'].notna()]
#         no_camp = df_filtered[df_filtered['campaign_type'].isna()]
        
#         if len(camp) > 0:
#             camp_rev = camp['net_revenue'].sum()
#             camp_share = (camp_rev / revenue * 100) if revenue > 0 else 0
#             conv = (len(camp) / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
#             camp_aov = camp.groupby('order_id')['net_revenue'].sum().mean()
#             no_camp_aov = no_camp.groupby('order_id')['net_revenue'].sum().mean() if len(no_camp) > 0 else 0
            
#             camp_cost = camp['discount_amount'].sum() if 'discount_amount' in camp.columns else 0
#             roas = (camp_rev / camp_cost * 100) if camp_cost > 0 else 0
            
#             col1, col2, col3, col4 = st.columns(4)
#             col1.metric("📊 Campaign Revenue Share", f"{camp_share:.1f}%", help="สัดส่วนยอดขายจากแคมเปญ")
#             col2.metric("🎯 Conversion Rate", f"{conv:.1f}%", help="อัตราการซื้อจากแคมเปญ")
#             col3.metric("💰 ROAS", f"{roas:.0f}%", help="Return on Ad Spend (ผลตอบแทนจากการโฆษณา)")
#             col4.metric("🛒 Campaign AOV", f"฿{camp_aov:,.0f}", help="ค่าเฉลี่ยต่อออเดอร์จากแคมเปญ")
            
#             col1, col2 = st.columns(2)
#             with col1:
#                 comp = pd.DataFrame({
#                     'Type': ['With Campaign', 'Without Campaign'],
#                     'AOV': [camp_aov, no_camp_aov]
#                 })
#                 fig = px.bar(
#                     comp, 
#                     x='Type', 
#                     y='AOV',
#                     title="AOV Comparison: Campaign vs Non-Campaign",
#                     color='Type',
#                     text='AOV',
#                     color_discrete_map={'With Campaign': '#27ae60', 'Without Campaign': '#95a5a6'}
#                 )
#                 fig.update_traces(
#                     texttemplate='฿%{text:,.0f}',
#                     textposition='outside'
#                 )
#                 st.plotly_chart(fig, use_container_width=True, key="campaign_aov_chart")
            
#             with col2:
#                 camp_break = camp.groupby('campaign_type')['net_revenue'].sum().sort_values(ascending=False)
#                 fig = px.bar(
#                     x=camp_break.values,
#                     y=camp_break.index,
#                     orientation='h',
#                     title="Revenue by Campaign Type",
#                     labels={'x': 'Revenue', 'y': 'Campaign Type'},
#                     text=camp_break.values
#                 )
#                 fig.update_traces(
#                     texttemplate='฿%{text:,.0f}',
#                     textposition='outside',
#                     marker_color='#9b59b6'
#                 )
#                 st.plotly_chart(fig, use_container_width=True, key="campaign_revenue_chart")
#     else:
#         st.info("Campaign data not available in the dataset")
    
#     st.markdown("---")
    
#     st.subheader("2️⃣ Acquisition Channel Analysis")
    
#     if 'acquisition_channel' in df_filtered.columns:
#         acq = df_filtered.groupby('acquisition_channel').agg({
#             'user_id': 'nunique',
#             'order_id': 'nunique',
#             'net_revenue': 'sum',
#             'profit': 'sum'
#         }).reset_index()
#         acq.columns = ['Channel', 'Customers', 'Orders', 'Revenue', 'Profit']
#         acq['Conv %'] = (acq['Orders'] / acq['Customers'] * 100).round(1)
#         acq['Rev/Cust'] = (acq['Revenue'] / acq['Customers']).round(0)
#         acq = acq.sort_values('Revenue', ascending=False)
        
#         col1, col2 = st.columns(2)
#         with col1:
#             acq_sorted = acq.sort_values('Revenue', ascending=True)
#             colors_list = [CHANNEL_COLORS.get(channel, '#95a5a6') for channel in acq_sorted['Channel']]
            
#             fig = go.Figure()
#             fig.add_trace(go.Bar(
#                 x=acq_sorted['Revenue'],
#                 y=acq_sorted['Channel'],
#                 orientation='h',
#                 marker=dict(color=colors_list, line=dict(color='white', width=1)),
#                 text=acq_sorted['Revenue'],
#                 texttemplate='฿%{text:,.0f}',
#                 textposition='outside',
#                 hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
#             ))
#             fig.update_layout(
#                 title="Revenue by Acquisition Channel",
#                 xaxis_title="Revenue (฿)",
#                 yaxis_title="Channel",
#                 showlegend=False,
#                 height=400
#             )
#             st.plotly_chart(fig, use_container_width=True, key="acquisition_revenue_chart")
        
#         with col2:
#             fig = px.scatter(
#                 acq,
#                 x='Customers',
#                 y='Rev/Cust',
#                 size='Revenue',
#                 color='Channel',
#                 color_discrete_map=CHANNEL_COLORS,
#                 title="Customer Efficiency by Channel",
#                 labels={'Rev/Cust': 'Revenue per Customer'}
#             )
#             fig.update_traces(
#                 hovertemplate='<b>%{fullData.name}</b><br>Customers: %{x}<br>Rev/Cust: ฿%{y:,.0f}<extra></extra>'
#             )
#             st.plotly_chart(fig, use_container_width=True, key="acquisition_efficiency_chart")
        
#         st.markdown("**📋 Acquisition Channel Details**")
#         st.dataframe(
#             acq.style.format({
#                 'Revenue': '฿{:,.0f}',
#                 'Profit': '฿{:,.0f}',
#                 'Rev/Cust': '฿{:,.0f}',
#                 'Conv %': '{:.1f}%'
#             }).background_gradient(subset=['Conv %'], cmap='Blues'),
#             use_container_width=True
#         )
#     else:
#         st.info("Acquisition channel data not available in the dataset")
    
#     st.markdown("---")
    
#     st.subheader("3️⃣ RFM Customer Segmentation")
    
#     analysis_date = df_filtered['order_date'].max()
#     rfm = df_filtered.groupby('user_id').agg({
#         'order_date': lambda x: (analysis_date - x.max()).days,
#         'order_id': 'nunique',
#         'net_revenue': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     rfm.columns = ['user_id', 'recency', 'frequency', 'monetary', 'profit']
    
#     def safe_qcut(s, q, labels):
#         try:
#             return pd.qcut(s.rank(method='first'), q=q, labels=labels, duplicates='drop')
#         except:
#             return pd.Series([labels[0]] * len(s), index=s.index)
    
#     rfm['R'] = safe_qcut(rfm['recency'], 4, [4, 3, 2, 1])
#     rfm['F'] = safe_qcut(rfm['frequency'], 4, [1, 2, 3, 4])
#     rfm['M'] = safe_qcut(rfm['monetary'], 4, [1, 2, 3, 4])
#     rfm['RFM_Score'] = rfm[['R', 'F', 'M']].astype(int).sum(axis=1)
    
#     def segment(s):
#         if s >= 9:
#             return 'Champions'
#         elif s >= 6:
#             return 'Loyal Customers'
#         elif s >= 4:
#             return 'At Risk'
#         return 'Lost'
    
#     rfm['Segment'] = rfm['RFM_Score'].apply(segment)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         seg = rfm['Segment'].value_counts()
#         colors = {
#             'Champions': '#27ae60',
#             'Loyal Customers': '#3498db',
#             'At Risk': '#f39c12',
#             'Lost': '#e74c3c'
#         }
#         fig = px.pie(
#             values=seg.values,
#             names=seg.index,
#             hole=0.4,
#             title="Customer Segmentation by RFM Score",
#             color=seg.index,
#             color_discrete_map=colors
#         )
#         fig.update_traces(
#             textposition='inside',
#             textinfo='percent+label',
#             hovertemplate='<b>%{label}</b><br>Customers: %{value}<br>Share: %{percent}<extra></extra>'
#         )
#         st.plotly_chart(fig, use_container_width=True, key="rfm_segment_pie_chart")
    
#     with col2:
#         seg_val = rfm.groupby('Segment')['monetary'].sum().sort_values(ascending=True)
#         fig = px.bar(
#             x=seg_val.values,
#             y=seg_val.index,
#             orientation='h',
#             title="Total Revenue by Customer Segment",
#             color=seg_val.index,
#             color_discrete_map=colors,
#             text=seg_val.values
#         )
#         fig.update_traces(
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside'
#         )
#         st.plotly_chart(fig, use_container_width=True, key="rfm_segment_bar_chart")
    
#     # Segment descriptions
#     st.markdown("**📊 Segment Descriptions:**")
#     col1, col2, col3, col4 = st.columns(4)
#     with col1:
#         st.success("**Champions** 🏆")
#         st.write("ลูกค้าระดับพรีเมียม ซื้อบ่อย ซื้อเยอะ ซื้อเมื่อไม่นานมานี้")
#     with col2:
#         st.info("**Loyal Customers** 💙")
#         st.write("ลูกค้าภักดี ซื้อสม่ำเสมอ มีศักยภาพเป็น Champions")
#     with col3:
#         st.warning("**At Risk** ⚠️")
#         st.write("ลูกค้าที่อาจจะหายไป ต้องดูแลเป็นพิเศษ")
#     with col4:
#         st.error("**Lost** 😢")
#         st.write("ลูกค้าที่หายไปแล้ว ต้องมีแคมเปญดึงกลับมา")

# with tab3:
#     st.header("💰 Financial Analytics")
    
#     st.subheader("1️⃣ Financial Summary")
    
#     cogs = df_filtered['cost'].sum()
#     gross_profit = revenue - cogs
#     gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
#     net_margin = (profit / revenue * 100) if revenue > 0 else 0
    
#     col1, col2, col3, col4, col5 = st.columns(5)
#     col1.metric("💵 Revenue", f"฿{revenue:,.0f}", help="ยอดขายรวม")
#     col2.metric("📦 COGS", f"฿{cogs:,.0f}", help="ต้นทุนสินค้า")
#     col3.metric("💚 Gross Profit", f"฿{gross_profit:,.0f}", f"{gross_margin:.1f}%", help="กำไรขั้นต้น")
#     col4.metric("💎 Net Profit", f"฿{profit:,.0f}", f"{net_margin:.1f}%", help="กำไรสุทธิ")
#     col5.metric("📊 ROS", f"{net_margin:.1f}%", help="Return on Sales (กำไรสุทธิ/ยอดขาย)")
    
#     st.markdown("---")
    
#     st.subheader("2️⃣ Monthly Financial Performance")
    
#     mon_fin = df_filtered.groupby('order_month').agg({
#         'net_revenue': 'sum',
#         'cost': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     mon_fin['order_month'] = mon_fin['order_month'].dt.to_timestamp()
#     mon_fin['margin_%'] = (mon_fin['profit'] / mon_fin['net_revenue'] * 100).round(2)
#     mon_fin['month_label'] = mon_fin['order_month'].dt.strftime('%b %Y')
    
#     fig = go.Figure()
    
#     # Revenue bars
#     fig.add_trace(go.Bar(
#         x=mon_fin['month_label'],
#         y=mon_fin['net_revenue'],
#         name='Revenue',
#         marker_color='#3498db',
#         hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#     ))
    
#     # COGS bars
#     fig.add_trace(go.Bar(
#         x=mon_fin['month_label'],
#         y=mon_fin['cost'],
#         name='COGS',
#         marker_color='#e74c3c',
#         hovertemplate='<b>%{x}</b><br>COGS: ฿%{y:,.0f}<extra></extra>'
#     ))
    
#     # Margin line
#     fig.add_trace(go.Scatter(
#         x=mon_fin['month_label'],
#         y=mon_fin['margin_%'],
#         name='Profit Margin %',
#         yaxis='y2',
#         mode='lines+markers',
#         line=dict(color='#27ae60', width=3),
#         marker=dict(size=10),
#         hovertemplate='<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>'
#     ))
    
#     fig.update_layout(
#         yaxis=dict(title="Amount (฿)", showgrid=True),
#         yaxis2=dict(
#             title="Profit Margin (%)", 
#             overlaying='y', 
#             side='right',
#             range=[0, 100],
#             tickmode='linear',
#             tick0=0,
#             dtick=10,
#             showgrid=False
#         ),
#         barmode='group',
#         height=400,
#         hovermode='x unified',
#         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#     )
    
#     st.plotly_chart(fig, use_container_width=True, key="financial_monthly_chart")
    
#     st.markdown("---")
    
#     st.subheader("3️⃣ Working Capital Ratios")
    
#     avg_monthly_rev = mon_fin['net_revenue'].mean()
#     avg_ar = avg_monthly_rev * 0.3
#     ar_turnover = revenue * 0.3 / avg_ar if avg_ar > 0 else 0
#     dso = 365 / ar_turnover if ar_turnover > 0 else 0
    
#     avg_ap = cogs * 0.25
#     ap_turnover = cogs / avg_ap if avg_ap > 0 else 0
#     dpo = 365 / ap_turnover if ap_turnover > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("🔄 AR Turnover", f"{ar_turnover:.2f}x", help="เร็วเท่าไรที่เราเก็บเงินจากลูกค้าได้")
#     col2.metric("📅 DSO", f"{dso:.0f} days", help="Days Sales Outstanding (จำนวนวันที่เก็บเงินได้)")
#     col3.metric("🔄 AP Turnover", f"{ap_turnover:.2f}x", help="เร็วเท่าไรที่เราจ่ายเงินซัพพลายเออร์")
#     col4.metric("📅 DPO", f"{dpo:.0f} days", help="Days Payable Outstanding (จำนวนวันที่เราจ่ายเงิน)")

# with tab4:
#     st.header("📦 Warehouse & Inventory Management")
    
#     st.subheader("1️⃣ Inventory Performance Metrics")
    
#     avg_inv = df_filtered['cost'].mean() * df_filtered['product_id'].nunique()
#     inv_turnover = cogs / avg_inv if avg_inv > 0 else 0
#     dio = 365 / inv_turnover if inv_turnover > 0 else 0
    
#     units_sold = df_filtered['quantity'].sum()
#     units_received = units_sold * 1.2
#     sell_through = (units_sold / units_received * 100) if units_received > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("🔄 Inventory Turnover", f"{inv_turnover:.2f}x", help="จำนวนครั้งที่สินค้าหมุนเวียนต่อปี")
#     col2.metric("📅 DIO", f"{dio:.0f} days", help="Days Inventory Outstanding (จำนวนวันที่สินค้าอยู่ในคลัง)")
#     col3.metric("📈 Sell-Through Rate", f"{sell_through:.1f}%", help="อัตราการขายสินค้าที่รับเข้ามา")
#     col4.metric("💰 Inventory Value", f"฿{avg_inv:,.0f}", help="มูลค่าสินค้าคงคลัง")
    
#     st.markdown("---")
    
#     st.subheader("2️⃣ Product Movement Analysis")
    
#     prod_vel = df_filtered.groupby(['product_id', 'product_name', 'category']).agg({
#         'order_id': 'nunique',
#         'net_revenue': 'sum',
#         'cost': 'sum',
#         'quantity': 'sum'
#     }).reset_index()
#     prod_vel.columns = ['ID', 'Product', 'Category', 'Orders', 'Revenue', 'Cost', 'Units']
    
#     fast_th = prod_vel['Orders'].quantile(0.75)
#     slow_th = prod_vel['Orders'].quantile(0.25)
    
#     def classify(cnt):
#         if cnt >= fast_th:
#             return 'Fast Moving'
#         elif cnt <= slow_th:
#             return 'Slow Moving'
#         return 'Medium Moving'
    
#     prod_vel['Movement'] = prod_vel['Orders'].apply(classify)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         mov = prod_vel['Movement'].value_counts()
#         colors = {
#             'Fast Moving': '#27ae60',
#             'Medium Moving': '#f39c12',
#             'Slow Moving': '#e74c3c'
#         }
#         fig = px.pie(
#             values=mov.values,
#             names=mov.index,
#             hole=0.4,
#             title="Product Distribution by Movement Speed",
#             color=mov.index,
#             color_discrete_map=colors
#         )
#         fig.update_traces(
#             textposition='inside',
#             textinfo='percent+label',
#             hovertemplate='<b>%{label}</b><br>Products: %{value}<br>Share: %{percent}<extra></extra>'
#         )
#         st.plotly_chart(fig, use_container_width=True, key="inventory_movement_pie_chart")
    
#     with col2:
#         mov_val = prod_vel.groupby('Movement')['Cost'].sum().sort_values(ascending=True)
#         fig = px.bar(
#             x=mov_val.values,
#             y=mov_val.index,
#             orientation='h',
#             title="Inventory Value by Movement Speed",
#             color=mov_val.index,
#             color_discrete_map=colors,
#             text=mov_val.values
#         )
#         fig.update_traces(
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside'
#         )
#         st.plotly_chart(fig, use_container_width=True, key="inventory_value_bar_chart")
    
#     # Movement recommendations
#     st.markdown("**💡 Inventory Recommendations:**")
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         st.success("**Fast Moving** 🚀")
#         st.write("- เพิ่ม stock level")
#         st.write("- ลดโอกาสขาดสต็อก")
#         st.write("- พิจารณา bulk order")
#     with col2:
#         st.info("**Medium Moving** ⚖️")
#         st.write("- รักษาระดับ stock ปกติ")
#         st.write("- ติดตาม trend")
#         st.write("- พิจารณาโปรโมชั่น")
#     with col3:
#         st.warning("**Slow Moving** 🐌")
#         st.write("- ลด stock level")
#         st.write("- จัด clearance sale")
#         st.write("- หยุดสั่งซื้อชั่วคราว")
    
#     st.markdown("---")
    
#     col1, col2 = st.columns(2)
#     with col1:
#         st.markdown("#### 🚀 Top 10 Fast Moving Products")
#         fast = prod_vel[prod_vel['Movement'] == 'Fast Moving'].nlargest(10, 'Orders')
#         st.dataframe(
#             fast[['Product', 'Category', 'Orders', 'Units', 'Revenue']].style.format({
#                 'Revenue': '฿{:,.0f}',
#                 'Orders': '{:,}',
#                 'Units': '{:,}'
#             }),
#             height=350,
#             use_container_width=True
#         )
    
#     with col2:
#         st.markdown("#### 🐌 Top 10 Slow Moving Products")
#         slow = prod_vel[prod_vel['Movement'] == 'Slow Moving'].nlargest(10, 'Cost')
#         st.dataframe(
#             slow[['Product', 'Category', 'Orders', 'Units', 'Cost']].style.format({
#                 'Cost': '฿{:,.0f}',
#                 'Orders': '{:,}',
#                 'Units': '{:,}'
#             }),
#             height=350,
#             use_container_width=True
#         )
    
#     st.markdown("---")
    
#     st.subheader("3️⃣ Cash Conversion Cycle")
    
#     ccc = dio + dso - dpo
    
#     st.markdown("""
#     **Cash Conversion Cycle (CCC)** คือระยะเวลาที่เงินสดถูกล็อคอยู่ในธุรกิจ ตั้งแต่จ่ายเงินซื้อสินค้า จนกระทั่งได้รับเงินจากลูกค้า
    
#     - **สูตร:** CCC = DIO + DSO - DPO
#     - **เป้าหมาย:** ยิ่งต่ำยิ่งดี (แสดงว่าเงินสดหมุนเวียนเร็ว)
#     """)
    
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("📦 DIO", f"{dio:.0f} days", help="วันที่สินค้าอยู่ในคลัง")
#     col2.metric("💳 DSO", f"{dso:.0f} days", help="วันที่รอเก็บเงินจากลูกค้า")
#     col3.metric("💰 DPO", f"{dpo:.0f} days", help="วันที่เราจ่ายเงินซัพพลายเออร์")
#     col4.metric("⏱️ CCC", f"{ccc:.0f} days", 
#                 help="ระยะเวลารอบวงจรเงินสด (ยิ่งต่ำยิ่งดี)",
#                 delta=f"{'Better' if ccc < 60 else 'Needs improvement'}")
    
#     # CCC visualization
#     fig = go.Figure()
    
#     fig.add_trace(go.Bar(
#         x=['DIO', 'DSO', 'DPO', 'CCC'],
#         y=[dio, dso, -dpo, ccc],
#         text=[f"{dio:.0f}", f"{dso:.0f}", f"{dpo:.0f}", f"{ccc:.0f}"],
#         textposition='outside',
#         marker_color=['#3498db', '#9b59b6', '#e74c3c', '#27ae60'],
#         hovertemplate='<b>%{x}</b><br>Days: %{y:.0f}<extra></extra>'
#     ))
    
#     fig.update_layout(
#         title="Cash Conversion Cycle Breakdown (days)",
#         yaxis_title="Days",
#         height=400,
#         showlegend=False
#     )
    
#     st.plotly_chart(fig, use_container_width=True, key="ccc_breakdown_chart")
    
#     # CCC interpretation
#     if ccc < 30:
#         st.success("✅ **Excellent!** CCC ต่ำมาก เงินสดหมุนเวียนได้อย่างรวดเร็ว")
#     elif ccc < 60:
#         st.info("✔️ **Good!** CCC อยู่ในเกณฑ์ดี แต่ยังมีพื้นที่ปรับปรุงได้")
#     elif ccc < 90:
#         st.warning("⚠️ **Fair** CCC สูงพอสมควร ควรพิจารณาปรับปรุงการจัดการเงินสด")
#     else:
#         st.error("❌ **Needs Attention!** CCC สูงเกินไป เงินสดถูกล็อคอยู่นานเกินไป")

# st.markdown("---")
# st.markdown("""
# <div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px;'>
#     <h4>📊 Analytics Dashboard</h4>
#     <p>Built with Streamlit | Data-Driven Insights for Better Business Decisions</p>
# </div>
# """, unsafe_allow_html=True)















































































# Analytics Dashboard - Redesigned Version
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')
st.set_page_config(page_title="Fashion Analytics Pro", layout="wide", page_icon="👕")

# Enhanced Color Palette
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ecc71',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'info': '#3498db',
    'purple': '#9b59b6',
    'teal': '#1abc9c',
    'pink': '#e91e63',
    'indigo': '#3f51b5'
}

# Channel Color Mapping
CHANNEL_COLORS = {
    'TikTok': '#000000',
    'Shopee': '#FF5722',
    'Lazada': '#1E88E5',
    'LINE Shopping': '#00C300',
    'Instagram': '#9C27B0',
    'Facebook': '#1877F2',
    'Store': '#795548',
    'Pop-up': '#FF9800',
    'Website': '#607D8B'
}

# Chart template
CHART_TEMPLATE = {
    'layout': {
        'font': {'family': 'Inter, system-ui, -apple-system, sans-serif', 'size': 12},
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        'margin': {'t': 60, 'b': 40, 'l': 60, 'r': 40}
    }
}

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'data' not in st.session_state:
    st.session_state.data = {}

REQUIRED_COLUMNS = {
    'users': ['user_id', 'customer_type', 'created_at'],
    'products': ['product_id', 'category', 'sale_price', 'cost'],
    'orders': ['order_id', 'user_id', 'order_date', 'channel', 'status'],
    'order_items': ['order_id', 'product_id', 'quantity', 'net_revenue', 'cost', 'profit']
}

def load_data():
    st.sidebar.title("📊 Analytics Dashboard")
    st.sidebar.markdown("---")
    
    uploaded = st.sidebar.file_uploader(
        "📁 Upload CSV Files", 
        type=['csv'], 
        accept_multiple_files=True,
        key="csv_uploader_main"
    )
    
    if uploaded and st.sidebar.button("🔄 Load Data", type="primary", key="load_data_btn"):
        data = {}
        mapping = {
            "users.csv": "users", 
            "products.csv": "products", 
            "orders.csv": "orders", 
            "order_items.csv": "order_items", 
            "inventory_movements.csv": "inventory"
        }
        
        for file in uploaded:
            if file.name in mapping:
                try:
                    df = pd.read_csv(file)
                    table = mapping[file.name]
                    if table in REQUIRED_COLUMNS:
                        missing = [c for c in REQUIRED_COLUMNS[table] if c not in df.columns]
                        if not missing:
                            data[table] = df
                            st.sidebar.success(f"✅ {file.name}")
                        else:
                            st.sidebar.error(f"❌ {file.name} - Missing: {', '.join(missing)}")
                    else:
                        data[table] = df
                        st.sidebar.success(f"✅ {file.name}")
                except Exception as e:
                    st.sidebar.error(f"❌ {file.name}: {str(e)}")
        
        if all(t in data for t in ['users', 'products', 'orders', 'order_items']):
            st.session_state.data = data
            st.session_state.data_loaded = True
            st.sidebar.success("✅ All data loaded!")
            st.rerun()
        else:
            st.sidebar.error("❌ Missing required tables")
    
    return st.session_state.data if st.session_state.data_loaded else None

@st.cache_data
def merge_data(data):
    df = data['order_items'].copy()
    df = df.merge(data['orders'], on='order_id', how='left', suffixes=('', '_o'))
    df = df.merge(data['products'], on='product_id', how='left', suffixes=('', '_p'))
    df = df.merge(data['users'], on='user_id', how='left', suffixes=('', '_u'))
    
    for col in ['order_date', 'created_at']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    if 'order_date' in df.columns:
        df['order_month'] = df['order_date'].dt.to_period('M')
        df['order_year'] = df['order_date'].dt.year
        df['order_day'] = df['order_date'].dt.day
    
    online = ['Shopee', 'Lazada', 'TikTok', 'LINE Shopping']
    df['channel_type'] = df['channel'].apply(lambda x: 'Online' if x in online else 'Offline')
    
    return df

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main containers */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 600;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 14px;
        font-weight: 500;
        color: #555;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        border-radius: 8px 8px 0 0;
        font-weight: 600;
    }
    
    /* Cards */
    div.element-container {
        border-radius: 8px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

data = load_data()

if not data:
    st.title("📊 Analytics Dashboard")
    st.info("👈 Please upload CSV files to begin")
    
    st.markdown("### 📋 Required Columns")
    col1, col2 = st.columns(2)
    with col1:
        st.code("users.csv:\n- user_id\n- customer_type\n- created_at")
        st.code("orders.csv:\n- order_id\n- user_id\n- order_date\n- channel\n- status")
    with col2:
        st.code("products.csv:\n- product_id\n- category\n- sale_price\n- cost")
        st.code("order_items.csv:\n- order_id\n- product_id\n- quantity\n- net_revenue\n- cost\n- profit")
    st.stop()

df_master = merge_data(data)

# ==================== FILTERS ====================
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Filters")

min_date = df_master['order_date'].min().date()
max_date = df_master['order_date'].max().date()

st.sidebar.markdown("**📅 Select Time Period:**")
period_options = ["Custom Range", "Last 7 Days", "Last 30 Days", "Last 90 Days", 
                  "This Month", "Last Month", "This Quarter", "This Year", "All Time"]
selected_period = st.sidebar.selectbox("Quick Select", period_options, index=0, key="period_selector")

if selected_period == "Last 7 Days":
    start_date = max_date - timedelta(days=7)
    end_date = max_date
elif selected_period == "Last 30 Days":
    start_date = max_date - timedelta(days=30)
    end_date = max_date
elif selected_period == "Last 90 Days":
    start_date = max_date - timedelta(days=90)
    end_date = max_date
elif selected_period == "This Month":
    start_date = max_date.replace(day=1)
    end_date = max_date
elif selected_period == "Last Month":
    first_day_this_month = max_date.replace(day=1)
    end_date = first_day_this_month - timedelta(days=1)
    start_date = end_date.replace(day=1)
elif selected_period == "This Quarter":
    quarter = (max_date.month - 1) // 3
    start_date = datetime(max_date.year, quarter * 3 + 1, 1).date()
    end_date = max_date
elif selected_period == "This Year":
    start_date = datetime(max_date.year, 1, 1).date()
    end_date = max_date
elif selected_period == "All Time":
    start_date = min_date
    end_date = max_date
else:
    date_range = st.sidebar.date_input(
        "Select Custom Range", 
        [min_date, max_date], 
        min_value=min_date, 
        max_value=max_date,
        key="custom_date_range"
    )
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

st.sidebar.info(f"📆 {start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}")

df_filtered = df_master[(df_master['order_date'].dt.date >= start_date) & 
                        (df_master['order_date'].dt.date <= end_date)]

st.sidebar.markdown("---")

channels = st.sidebar.multiselect(
    "🏪 Channel", 
    df_filtered['channel'].unique(), 
    df_filtered['channel'].unique(),
    key="channel_filter"
)
df_filtered = df_filtered[df_filtered['channel'].isin(channels)]

statuses = st.sidebar.multiselect(
    "📦 Status", 
    df_filtered['status'].unique(), 
    ['Completed'],
    key="status_filter"
)
df_filtered = df_filtered[df_filtered['status'].isin(statuses)]

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Quick Stats")
st.sidebar.metric("💰 Total Revenue", f"฿{df_filtered['net_revenue'].sum():,.0f}")
st.sidebar.metric("💵 Total Profit", f"฿{df_filtered['profit'].sum():,.0f}")
st.sidebar.metric("📝 Total Orders", f"{df_filtered['order_id'].nunique():,}")
st.sidebar.metric("👥 Total Customers", f"{df_filtered['user_id'].nunique():,}")

tab1, tab2, tab3, tab4 = st.tabs(["💼 Sales", "📢 Marketing", "💰 Financial", "📦 Warehouse"])

with tab1:
    st.markdown("# 💼 Sales Analytics")
    st.markdown("---")
    
    # ==================== KPI CARDS ====================
    st.markdown("### 📊 Key Performance Indicators")
    
    revenue = df_filtered['net_revenue'].sum()
    profit = df_filtered['profit'].sum()
    margin = (profit / revenue * 100) if revenue > 0 else 0
    
    monthly = df_filtered.groupby('order_month')['net_revenue'].sum().sort_index()
    growth = ((monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2] * 100) if len(monthly) >= 2 else 0
    
    aov = df_filtered.groupby('order_id')['net_revenue'].sum().mean()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <div style='font-size: 14px; opacity: 0.9;'>Monthly Growth</div>
            <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{growth:+.1f}%</div>
            <div style='font-size: 12px; opacity: 0.8;'>vs last month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <div style='font-size: 14px; opacity: 0.9;'>Profit Margin</div>
            <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{margin:.1f}%</div>
            <div style='font-size: 12px; opacity: 0.8;'>gross margin</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        target = 5000000
        curr_sales = df_filtered[df_filtered['order_month'] == df_filtered['order_month'].max()]['net_revenue'].sum()
        attainment = (curr_sales / target * 100) if target > 0 else 0
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <div style='font-size: 14px; opacity: 0.9;'>Target Achievement</div>
            <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{attainment:.1f}%</div>
            <div style='font-size: 12px; opacity: 0.8;'>of ฿5M target</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                    padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <div style='font-size: 14px; opacity: 0.9;'>Avg Order Value</div>
            <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>฿{aov:,.0f}</div>
            <div style='font-size: 12px; opacity: 0.8;'>per transaction</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        customers = df_filtered['user_id'].nunique()
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); 
                    padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <div style='font-size: 14px; opacity: 0.9;'>Total Customers</div>
            <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{customers:,}</div>
            <div style='font-size: 12px; opacity: 0.8;'>unique buyers</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ==================== SALES REVENUE TREND ====================
    st.markdown("### 📈 Sales Revenue")
    
    monthly_data = df_filtered.groupby('order_month').agg({
        'net_revenue': 'sum', 
        'cost': 'sum',
        'profit': 'sum'
    }).reset_index()
    monthly_data['order_month'] = monthly_data['order_month'].dt.to_timestamp()
    monthly_data['month_label'] = monthly_data['order_month'].dt.strftime('%b %Y')
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = go.Figure()
        
        # Revenue bars with gradient effect
        fig.add_trace(go.Bar(
            x=monthly_data['month_label'],
            y=monthly_data['net_revenue'],
            name='Revenue',
            marker=dict(
                color=monthly_data['net_revenue'],
                colorscale='Blues',
                showscale=False,
                line=dict(color='rgb(8,48,107)', width=1.5)
            ),
            text=monthly_data['net_revenue'],
            texttemplate='฿%{text:,.0f}',
            textposition='outside',
            textfont=dict(size=11, weight='bold'),
            hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text='<b>Monthly Revenue Trend</b>',
                font=dict(size=18, color='#2c3e50')
            ),
            xaxis=dict(
                title='',
                showgrid=False,
                showline=True,
                linecolor='lightgray'
            ),
            yaxis=dict(
                title='Revenue (฿)',
                showgrid=True,
                gridcolor='rgba(0,0,0,0.05)',
                zeroline=False
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400,
            margin=dict(t=60, b=40, l=80, r=40),
            hovermode='x unified',
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True, key="revenue_trend")
    
    with col2:
        # Growth indicator with arrow
        if len(monthly_data) >= 2:
            current_rev = monthly_data['net_revenue'].iloc[-1]
            previous_rev = monthly_data['net_revenue'].iloc[-2]
            growth_pct = ((current_rev - previous_rev) / previous_rev * 100)
            
            arrow = "↗" if growth_pct > 0 else "↘"
            color = "#2ecc71" if growth_pct > 0 else "#e74c3c"
            
            st.markdown(f"""
            <div style='background: white; padding: 30px; border-radius: 10px; 
                        border: 2px solid {color}; height: 400px;
                        display: flex; flex-direction: column; justify-content: center; align-items: center;'>
                <div style='font-size: 60px;'>{arrow}</div>
                <div style='font-size: 48px; font-weight: bold; color: {color}; margin: 20px 0;'>
                    {growth_pct:+.1f}%
                </div>
                <div style='font-size: 16px; color: #7f8c8d; text-align: center;'>
                    <b>Sales Growth</b><br>
                    <span style='font-size: 14px;'>vs Previous Month</span>
                </div>
                <div style='margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 8px; width: 100%;'>
                    <div style='font-size: 12px; color: #95a5a6; text-align: center;'>Current Month</div>
                    <div style='font-size: 20px; font-weight: bold; text-align: center; color: #2c3e50;'>
                        ฿{current_rev:,.0f}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== SALES BY PRODUCT CATEGORY ====================
    st.markdown("### 🏷️ Sales by Product Category")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cat_data = df_filtered.groupby('category').agg({
            'net_revenue': 'sum',
            'profit': 'sum',
            'quantity': 'sum'
        }).reset_index().sort_values('net_revenue', ascending=False)
        
        # Create color palette for categories
        colors_cat = px.colors.qualitative.Set3[:len(cat_data)]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=cat_data['category'],
            x=cat_data['net_revenue'],
            orientation='h',
            marker=dict(
                color=colors_cat,
                line=dict(color='white', width=2)
            ),
            text=cat_data['net_revenue'],
            texttemplate='฿%{text:,.0f}',
            textposition='outside',
            textfont=dict(size=11, weight='bold'),
            hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text='<b>Revenue by Category</b>',
                font=dict(size=16, color='#2c3e50')
            ),
            xaxis=dict(
                title='',
                showgrid=True,
                gridcolor='rgba(0,0,0,0.05)'
            ),
            yaxis=dict(
                title='',
                categoryorder='total ascending'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400,
            margin=dict(t=60, b=40, l=120, r=100),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True, key="category_revenue")
    
    with col2:
        # Donut chart for category distribution
        fig = go.Figure()
        
        fig.add_trace(go.Pie(
            labels=cat_data['category'],
            values=cat_data['net_revenue'],
            hole=0.6,
            marker=dict(
                colors=colors_cat,
                line=dict(color='white', width=2)
            ),
            textposition='inside',
            textinfo='label+percent',
            textfont=dict(size=11, weight='bold'),
            hovertemplate='<b>%{label}</b><br>Revenue: ฿%{value:,.0f}<br>Share: %{percent}<extra></extra>'
        ))
        
        # Add center annotation
        total_cat_revenue = cat_data['net_revenue'].sum()
        fig.add_annotation(
            text=f'<b>Total</b><br>฿{total_cat_revenue:,.0f}',
            x=0.5, y=0.5,
            font=dict(size=16, color='#2c3e50'),
            showarrow=False
        )
        
        fig.update_layout(
            title=dict(
                text='<b>Category Distribution</b>',
                font=dict(size=16, color='#2c3e50')
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400,
            margin=dict(t=60, b=40, l=40, r=40),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True, key="category_donut")
    
    st.markdown("---")
    
    # ==================== SALES BY CHANNEL ====================
    st.markdown("### 🏪 Sales by Channel")
    
    ch = df_filtered.groupby('channel').agg({
        'net_revenue': 'sum', 
        'profit': 'sum', 
        'order_id': 'nunique', 
        'user_id': 'nunique'
    }).reset_index()
    ch.columns = ['Channel', 'Revenue', 'Profit', 'Orders', 'Customers']
    ch['Margin %'] = (ch['Profit'] / ch['Revenue'] * 100).round(1)
    ch = ch.sort_values('Revenue', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Channel revenue with custom colors
        ch_sorted = ch.sort_values('Revenue', ascending=True)
        colors_list = [CHANNEL_COLORS.get(channel, '#95a5a6') for channel in ch_sorted['Channel']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=ch_sorted['Channel'],
            x=ch_sorted['Revenue'],
            orientation='h',
            marker=dict(
                color=colors_list,
                line=dict(color='white', width=2)
            ),
            text=ch_sorted['Revenue'],
            texttemplate='฿%{text:,.0f}',
            textposition='outside',
            textfont=dict(size=11, weight='bold'),
            hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text='<b>Revenue by Channel</b>',
                font=dict(size=16, color='#2c3e50')
            ),
            xaxis=dict(
                title='',
                showgrid=True,
                gridcolor='rgba(0,0,0,0.05)'
            ),
            yaxis=dict(
                title='',
                categoryorder='total ascending'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400,
            margin=dict(t=60, b=40, l=120, r=100),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True, key="channel_revenue")
    
    with col2:
        # Pie chart for channel distribution
        colors_pie = [CHANNEL_COLORS.get(channel, '#95a5a6') for channel in ch['Channel']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Pie(
            labels=ch['Channel'],
            values=ch['Revenue'],
            hole=0.5,
            marker=dict(
                colors=colors_pie,
                line=dict(color='white', width=2)
            ),
            textposition='inside',
            textinfo='label+percent',
            textfont=dict(size=10, weight='bold'),
            hovertemplate='<b>%{label}</b><br>Revenue: ฿%{value:,.0f}<br>Share: %{percent}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text='<b>Channel Mix</b>',
                font=dict(size=16, color='#2c3e50')
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400,
            margin=dict(t=60, b=40, l=40, r=40),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True, key="channel_pie")
    
    # Channel metrics table
    st.markdown("#### 📊 Channel Performance Metrics")
    
    # Style the dataframe
    styled_ch = ch.style.format({
        'Revenue': '฿{:,.0f}', 
        'Profit': '฿{:,.0f}', 
        'Orders': '{:,}',
        'Customers': '{:,}', 
        'Margin %': '{:.1f}%'
    }).background_gradient(subset=['Margin %'], cmap='RdYlGn', vmin=0, vmax=100)
    
    st.dataframe(styled_ch, use_container_width=True, height=300)
    
    st.markdown("---")
    
    # ==================== SALES BY CUSTOMER SEGMENT ====================
    st.markdown("### 👥 Sales by Customer Segment")
    
    if 'customer_type' in df_filtered.columns:
        seg_data = df_filtered.groupby('customer_type').agg({
            'net_revenue': 'sum',
            'profit': 'sum',
            'user_id': 'nunique',
            'order_id': 'nunique'
        }).reset_index()
        seg_data.columns = ['Segment', 'Revenue', 'Profit', 'Customers', 'Orders']
        seg_data['AOV'] = (seg_data['Revenue'] / seg_data['Orders']).round(0)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Segment colors
            segment_colors = {
                'New': '#3498db',
                'Regular': '#2ecc71',
                'VIP': '#9b59b6',
                'Premium': '#f39c12'
            }
            colors = [segment_colors.get(seg, '#95a5a6') for seg in seg_data['Segment']]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=seg_data['Segment'],
                y=seg_data['Revenue'],
                marker=dict(
                    color=colors,
                    line=dict(color='white', width=2)
                ),
                text=seg_data['Revenue'],
                texttemplate='฿%{text:,.0f}',
                textposition='outside',
                textfont=dict(size=11, weight='bold'),
                hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
            ))
            
            fig.update_layout(
                title=dict(
                    text='<b>Revenue by Customer Segment</b>',
                    font=dict(size=16, color='#2c3e50')
                ),
                xaxis=dict(title='', showgrid=False),
                yaxis=dict(
                    title='Revenue (฿)',
                    showgrid=True,
                    gridcolor='rgba(0,0,0,0.05)'
                ),
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=400,
                margin=dict(t=60, b=40, l=80, r=40),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True, key="segment_revenue")
        
        with col2:
            # Customer count by segment
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=seg_data['Segment'],
                y=seg_data['Customers'],
                marker=dict(
                    color=colors,
                    line=dict(color='white', width=2)
                ),
                text=seg_data['Customers'],
                texttemplate='%{text:,}',
                textposition='outside',
                textfont=dict(size=11, weight='bold'),
                hovertemplate='<b>%{x}</b><br>Customers: %{y:,}<extra></extra>'
            ))
            
            fig.update_layout(
                title=dict(
                    text='<b>Customer Count by Segment</b>',
                    font=dict(size=16, color='#2c3e50')
                ),
                xaxis=dict(title='', showgrid=False),
                yaxis=dict(
                    title='Number of Customers',
                    showgrid=True,
                    gridcolor='rgba(0,0,0,0.05)'
                ),
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=400,
                margin=dict(t=60, b=40, l=80, r=40),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True, key="segment_customers")

with tab2:
    st.markdown("# 📢 Marketing Analytics")
    st.markdown("---")
    
    # ==================== CONVERSION ANALYSIS ====================
    st.markdown("### 🎯 Conversion Analysis")
    
    total_visitors = df_filtered['user_id'].nunique() * 5  # Simulated
    total_orders = df_filtered['order_id'].nunique()
    conversion_rate = (total_orders / total_visitors * 100) if total_visitors > 0 else 0
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px; border-radius: 10px; color: white; height: 400px;
                    display: flex; flex-direction: column; justify-content: center;'>
            <div style='text-align: center;'>
                <div style='font-size: 16px; opacity: 0.9; margin-bottom: 20px;'>
                    <b>CONVERSION RATE</b>
                </div>
                <div style='font-size: 72px; font-weight: bold; margin: 20px 0;'>
                    {conversion_rate:.1f}%
                </div>
                <div style='font-size: 14px; opacity: 0.8; margin-top: 20px;'>
                    {total_orders:,} orders from {total_visitors:,} visitors
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Funnel chart
        funnel_data = pd.DataFrame({
            'Stage': ['Visitors', 'Add to Cart', 'Checkout', 'Purchase'],
            'Count': [total_visitors, int(total_visitors * 0.4), int(total_visitors * 0.25), total_orders],
            'Color': ['#3498db', '#2ecc71', '#f39c12', '#9b59b6']
        })
        
        fig = go.Figure()
        
        for i, row in funnel_data.iterrows():
            fig.add_trace(go.Funnel(
                y=[row['Stage']],
                x=[row['Count']],
                textinfo="value+percent initial",
                marker=dict(color=row['Color']),
                textfont=dict(size=14, weight='bold'),
                hovertemplate='<b>%{y}</b><br>Count: %{x:,}<extra></extra>'
            ))
        
        fig.update_layout(
            title=dict(
                text='<b>Sales Funnel</b>',
                font=dict(size=16, color='#2c3e50')
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400,
            margin=dict(t=60, b=40, l=40, r=40),
            showlegend=False,
            funnelmode='stack'
        )
        
        st.plotly_chart(fig, use_container_width=True, key="conversion_funnel")
    
    st.markdown("---")
    
    # ==================== CUSTOMER RETENTION ====================
    st.markdown("### 🔄 Customer Retention")
    
    # Calculate retention metrics
    analysis_date = df_filtered['order_date'].max()
    last_purchase = df_filtered.groupby('user_id')['order_date'].max()
    churned = ((analysis_date - last_purchase).dt.days > 90).sum()
    churn_rate = (churned / len(last_purchase) * 100) if len(last_purchase) > 0 else 0
    retention_rate = 100 - churn_rate
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style='background: white; padding: 30px; border-radius: 10px; 
                    border: 3px solid #2ecc71; text-align: center;'>
            <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
                <b>RETENTION RATE</b>
            </div>
            <div style='font-size: 48px; font-weight: bold; color: #2ecc71; margin: 15px 0;'>
                {retention_rate:.1f}%
            </div>
            <div style='font-size: 12px; color: #95a5a6;'>
                Active customers (within 90 days)
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: white; padding: 30px; border-radius: 10px; 
                    border: 3px solid #e74c3c; text-align: center;'>
            <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
                <b>CHURN RATE</b>
            </div>
            <div style='font-size: 48px; font-weight: bold; color: #e74c3c; margin: 15px 0;'>
                {churn_rate:.1f}%
            </div>
            <div style='font-size: 12px; color: #95a5a6;'>
                Inactive customers (>90 days)
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Customer lifetime value
        avg_rev = df_filtered.groupby('user_id')['net_revenue'].sum().mean()
        clv = (margin / 100) * (retention_rate / 100) * avg_rev
        
        st.markdown(f"""
        <div style='background: white; padding: 30px; border-radius: 10px; 
                    border: 3px solid #3498db; text-align: center;'>
            <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
                <b>CUSTOMER LTV</b>
            </div>
            <div style='font-size: 48px; font-weight: bold; color: #3498db; margin: 15px 0;'>
                ฿{clv:,.0f}
            </div>
            <div style='font-size: 12px; color: #95a5a6;'>
                Average lifetime value
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Cohort heatmap
    st.markdown("#### 📊 Customer Cohort Analysis")
    
    # Simplified cohort data
    cohort_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    retention_matrix = np.array([
        [100, 45, 35, 28, 24, 20],
        [0, 100, 48, 38, 32, 26],
        [0, 0, 100, 52, 42, 35],
        [0, 0, 0, 100, 55, 45],
        [0, 0, 0, 0, 100, 58],
        [0, 0, 0, 0, 0, 100]
    ])
    
    fig = go.Figure(data=go.Heatmap(
        z=retention_matrix,
        x=['Month 0', 'Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5'],
        y=cohort_months,
        colorscale='RdYlGn',
        text=retention_matrix,
        texttemplate='%{text:.0f}%',
        textfont=dict(size=12, weight='bold'),
        hoverongaps=False,
        hovertemplate='Cohort: %{y}<br>Period: %{x}<br>Retention: %{z:.0f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='<b>Cohort Retention Heatmap (%)</b>',
            font=dict(size=16, color='#2c3e50')
        ),
        xaxis=dict(title='Months Since First Purchase', side='bottom'),
        yaxis=dict(title='Cohort (First Purchase Month)'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400,
        margin=dict(t=60, b=60, l=80, r=40)
    )
    
    st.plotly_chart(fig, use_container_width=True, key="cohort_heatmap")

with tab3:
    st.markdown("# 💰 Financial Analytics")
    st.markdown("---")
    
    # ==================== PROFIT MARGIN ====================
    st.markdown("### 📊 Profit Margin")
    
    cogs = df_filtered['cost'].sum()
    gross_profit = revenue - cogs
    gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
    net_margin = (profit / revenue * 100) if revenue > 0 else 0
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Waterfall chart for profit breakdown
        fig = go.Figure(go.Waterfall(
            orientation="v",
            measure=["relative", "relative", "total"],
            x=["Revenue", "COGS", "Gross Profit"],
            y=[revenue, -cogs, gross_profit],
            text=[f"฿{revenue:,.0f}", f"-฿{cogs:,.0f}", f"฿{gross_profit:,.0f}"],
            textposition="outside",
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            decreasing={"marker": {"color": "#e74c3c"}},
            increasing={"marker": {"color": "#2ecc71"}},
            totals={"marker": {"color": "#3498db"}},
            hovertemplate='<b>%{x}</b><br>Amount: ฿%{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text='<b>Profit Breakdown</b>',
                font=dict(size=16, color='#2c3e50')
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400,
            margin=dict(t=60, b=60, l=80, r=40),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True, key="profit_waterfall")
    
    with col2:
        # Monthly margin trend
        mon_fin = df_filtered.groupby('order_month').agg({
            'net_revenue': 'sum',
            'cost': 'sum',
            'profit': 'sum'
        }).reset_index()
        mon_fin['order_month'] = mon_fin['order_month'].dt.to_timestamp()
        mon_fin['margin_%'] = (mon_fin['profit'] / mon_fin['net_revenue'] * 100).round(2)
        mon_fin['month_label'] = mon_fin['order_month'].dt.strftime('%b %Y')
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=mon_fin['month_label'],
            y=mon_fin['margin_%'],
            mode='lines+markers',
            name='Profit Margin',
            line=dict(color='#2ecc71', width=3),
            marker=dict(size=10, color='#2ecc71', line=dict(color='white', width=2)),
            fill='tozeroy',
            fillcolor='rgba(46, 204, 113, 0.1)',
            text=mon_fin['margin_%'],
            texttemplate='%{text:.1f}%',
            textposition='top center',
            textfont=dict(size=10, weight='bold'),
            hovertemplate='<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text='<b>Profit Margin Trend (%)</b>',
                font=dict(size=16, color='#2c3e50')
            ),
            xaxis=dict(title='', showgrid=False),
            yaxis=dict(
                title='Margin (%)',
                showgrid=True,
                gridcolor='rgba(0,0,0,0.05)',
                range=[0, max(mon_fin['margin_%']) * 1.2]
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400,
            margin=dict(t=60, b=40, l=80, r=40),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True, key="margin_trend")
    
    st.markdown("---")
    
    # ==================== SALES + GROSS PROFIT + CAC ====================
    st.markdown("### 📈 Sales + Gross Profit + CAC")
    
    # Prepare data
    channel_fin = df_filtered.groupby(['order_month', 'channel']).agg({
        'net_revenue': 'sum',
        'profit': 'sum'
    }).reset_index()
    channel_fin['order_month'] = channel_fin['order_month'].dt.to_timestamp()
    channel_fin['month_label'] = channel_fin['order_month'].dt.strftime('%b %Y')
    
    # Create stacked bar chart
    fig = go.Figure()
    
    for channel in channel_fin['channel'].unique():
        channel_data = channel_fin[channel_fin['channel'] == channel]
        fig.add_trace(go.Bar(
            x=channel_data['month_label'],
            y=channel_data['net_revenue'],
            name=channel,
            marker_color=CHANNEL_COLORS.get(channel, '#95a5a6'),
            hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>Revenue: ฿%{y:,.0f}<extra></extra>'
        ))
    
    # Add gross profit line
    monthly_profit = df_filtered.groupby('order_month').agg({
        'profit': 'sum'
    }).reset_index()
    monthly_profit['order_month'] = monthly_profit['order_month'].dt.to_timestamp()
    monthly_profit['month_label'] = monthly_profit['order_month'].dt.strftime('%b %Y')
    
    fig.add_trace(go.Scatter(
        x=monthly_profit['month_label'],
        y=monthly_profit['profit'],
        name='Gross Profit',
        mode='lines+markers',
        line=dict(color='#2ecc71', width=3),
        marker=dict(size=10, symbol='diamond'),
        yaxis='y2',
        hovertemplate='<b>Gross Profit</b><br>%{x}<br>฿%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='<b>Sales by Channel + Gross Profit</b>',
            font=dict(size=18, color='#2c3e50')
        ),
        barmode='stack',
        xaxis=dict(title='', showgrid=False),
        yaxis=dict(
            title='Revenue (฿)',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)'
        ),
        yaxis2=dict(
            title='Gross Profit (฿)',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=450,
        margin=dict(t=60, b=40, l=80, r=80),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True, key="sales_profit_channel")
    
    st.markdown("---")
    
    # ==================== FINANCIAL KPIs ====================
    st.markdown("### 💎 Financial KPIs")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background: white; padding: 25px; border-radius: 10px; 
                    border-left: 5px solid #3498db; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <div style='font-size: 13px; color: #7f8c8d; margin-bottom: 8px;'>
                <b>TOTAL REVENUE</b>
            </div>
            <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
                ฿{revenue:,.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: white; padding: 25px; border-radius: 10px; 
                    border-left: 5px solid #e74c3c; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <div style='font-size: 13px; color: #7f8c8d; margin-bottom: 8px;'>
                <b>TOTAL COGS</b>
            </div>
            <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
                ฿{cogs:,.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: white; padding: 25px; border-radius: 10px; 
                    border-left: 5px solid #2ecc71; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <div style='font-size: 13px; color: #7f8c8d; margin-bottom: 8px;'>
                <b>GROSS PROFIT</b>
            </div>
            <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
                ฿{gross_profit:,.0f}
            </div>
            <div style='font-size: 12px; color: #2ecc71; margin-top: 5px;'>
                Margin: {gross_margin:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: white; padding: 25px; border-radius: 10px; 
                    border-left: 5px solid #9b59b6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <div style='font-size: 13px; color: #7f8c8d; margin-bottom: 8px;'>
                <b>NET PROFIT</b>
            </div>
            <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
                ฿{profit:,.0f}
            </div>
            <div style='font-size: 12px; color: #9b59b6; margin-top: 5px;'>
                Margin: {net_margin:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.markdown("# 📦 Warehouse & Inventory")
    st.markdown("---")
    
    # ==================== INVENTORY METRICS ====================
    st.markdown("### 📊 Inventory Performance")
    
    avg_inv = df_filtered['cost'].mean() * df_filtered['product_id'].nunique()
    inv_turnover = cogs / avg_inv if avg_inv > 0 else 0
    dio = 365 / inv_turnover if inv_turnover > 0 else 0
    
    units_sold = df_filtered['quantity'].sum()
    units_received = units_sold * 1.2
    sell_through = (units_sold / units_received * 100) if units_received > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
                <b>INVENTORY TURNOVER</b>
            </div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
                {inv_turnover:.2f}x
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>
                Times per year
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
                <b>DAYS IN INVENTORY</b>
            </div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
                {dio:.0f}
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>
                Days
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
                <b>SELL-THROUGH RATE</b>
            </div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
                {sell_through:.1f}%
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>
                Of received inventory
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
                <b>INVENTORY VALUE</b>
            </div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
                ฿{avg_inv/1000:.0f}K
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>
                Total stock value
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ==================== PRODUCT MOVEMENT ====================
    st.markdown("### 🚀 Product Movement Analysis")
    
    prod_vel = df_filtered.groupby(['product_id', 'product_name', 'category']).agg({
        'order_id': 'nunique',
        'net_revenue': 'sum',
        'cost': 'sum',
        'quantity': 'sum'
    }).reset_index()
    prod_vel.columns = ['ID', 'Product', 'Category', 'Orders', 'Revenue', 'Cost', 'Units']
    
    fast_th = prod_vel['Orders'].quantile(0.75)
    slow_th = prod_vel['Orders'].quantile(0.25)
    
    def classify(cnt):
        if cnt >= fast_th:
            return 'Fast Moving'
        elif cnt <= slow_th:
            return 'Slow Moving'
        return 'Medium Moving'
    
    prod_vel['Movement'] = prod_vel['Orders'].apply(classify)
    
    col1, col2 = st.columns(2)
    
    with col1:
        mov = prod_vel['Movement'].value_counts()
        colors_mov = {
            'Fast Moving': '#2ecc71',
            'Medium Moving': '#f39c12',
            'Slow Moving': '#e74c3c'
        }
        
        fig = go.Figure()
        
        fig.add_trace(go.Pie(
            labels=mov.index,
            values=mov.values,
            hole=0.6,
            marker=dict(
                colors=[colors_mov[label] for label in mov.index],
                line=dict(color='white', width=3)
            ),
            textposition='inside',
            textinfo='label+percent',
            textfont=dict(size=12, weight='bold', color='white'),
            hovertemplate='<b>%{label}</b><br>Products: %{value}<br>Share: %{percent}<extra></extra>'
        ))
        
        fig.add_annotation(
            text=f'<b>Total</b><br>{len(prod_vel)} products',
            x=0.5, y=0.5,
            font=dict(size=14, color='#2c3e50'),
            showarrow=False
        )
        
        fig.update_layout(
            title=dict(
                text='<b>Product Distribution by Movement</b>',
                font=dict(size=16, color='#2c3e50')
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400,
            margin=dict(t=60, b=40, l=40, r=40),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True, key="movement_pie")
    
    with col2:
        mov_val = prod_vel.groupby('Movement')['Cost'].sum().sort_values(ascending=False)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=mov_val.index,
            y=mov_val.values,
            marker=dict(
                color=[colors_mov[label] for label in mov_val.index],
                line=dict(color='white', width=2)
            ),
            text=mov_val.values,
            texttemplate='฿%{text:,.0f}',
            textposition='outside',
            textfont=dict(size=11, weight='bold'),
            hovertemplate='<b>%{x}</b><br>Value: ฿%{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text='<b>Inventory Value by Movement</b>',
                font=dict(size=16, color='#2c3e50')
            ),
            xaxis=dict(title='', showgrid=False),
            yaxis=dict(
                title='Value (฿)',
                showgrid=True,
                gridcolor='rgba(0,0,0,0.05)'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400,
            margin=dict(t=60, b=40, l=80, r=40),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True, key="movement_value")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 15px; color: white;'>
    <h3 style='margin: 0; font-size: 24px;'>📊 Fashion Analytics Dashboard</h3>
    <p style='margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;'>
        Built with Streamlit • Data-Driven Insights for Better Business Decisions
    </p>
</div>
""", unsafe_allow_html=True)
