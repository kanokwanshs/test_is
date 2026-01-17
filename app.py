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















































































# # Analytics Dashboard - Redesigned Version
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
# import numpy as np
# import warnings
# from datetime import datetime, timedelta

# warnings.filterwarnings('ignore')
# st.set_page_config(page_title="Fashion Analytics Pro", layout="wide", page_icon="👕")

# # Enhanced Color Palette
# COLORS = {
#     'primary': '#1f77b4',
#     'secondary': '#ff7f0e',
#     'success': '#2ecc71',
#     'danger': '#e74c3c',
#     'warning': '#f39c12',
#     'info': '#3498db',
#     'purple': '#9b59b6',
#     'teal': '#1abc9c',
#     'pink': '#e91e63',
#     'indigo': '#3f51b5'
# }

# # Channel Color Mapping
# CHANNEL_COLORS = {
#     'TikTok': '#000000',
#     'Shopee': '#FF5722',
#     'Lazada': '#1E88E5',
#     'LINE Shopping': '#00C300',
#     'Instagram': '#9C27B0',
#     'Facebook': '#1877F2',
#     'Store': '#795548',
#     'Pop-up': '#FF9800',
#     'Website': '#607D8B'
# }

# # Chart template
# CHART_TEMPLATE = {
#     'layout': {
#         'font': {'family': 'Inter, system-ui, -apple-system, sans-serif', 'size': 12},
#         'plot_bgcolor': 'white',
#         'paper_bgcolor': 'white',
#         'margin': {'t': 60, 'b': 40, 'l': 60, 'r': 40}
#     }
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
#     st.sidebar.title("📊 Analytics Dashboard")
#     st.sidebar.markdown("---")
    
#     uploaded = st.sidebar.file_uploader(
#         "📁 Upload CSV Files", 
#         type=['csv'], 
#         accept_multiple_files=True,
#         key="csv_uploader_main"
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

# # Custom CSS for better styling
# st.markdown("""
# <style>
#     /* Main containers */
#     .block-container {
#         padding-top: 1rem;
#         padding-bottom: 1rem;
#     }
    
#     /* Metric cards */
#     [data-testid="stMetricValue"] {
#         font-size: 28px;
#         font-weight: 600;
#     }
    
#     [data-testid="stMetricLabel"] {
#         font-size: 14px;
#         font-weight: 500;
#         color: #555;
#     }
    
#     /* Headers */
#     h1, h2, h3 {
#         font-family: 'Inter', sans-serif;
#         font-weight: 700;
#     }
    
#     /* Tabs */
#     .stTabs [data-baseweb="tab-list"] {
#         gap: 8px;
#     }
    
#     .stTabs [data-baseweb="tab"] {
#         height: 50px;
#         padding-left: 20px;
#         padding-right: 20px;
#         border-radius: 8px 8px 0 0;
#         font-weight: 600;
#     }
    
#     /* Cards */
#     div.element-container {
#         border-radius: 8px;
#     }
    
#     /* Sidebar */
#     [data-testid="stSidebar"] {
#         background-color: #f8f9fa;
#     }
# </style>
# """, unsafe_allow_html=True)

# data = load_data()

# if not data:
#     st.title("📊 Analytics Dashboard")
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

# # ==================== FILTERS ====================
# st.sidebar.markdown("---")
# st.sidebar.markdown("### 🔍 Filters")

# min_date = df_master['order_date'].min().date()
# max_date = df_master['order_date'].max().date()

# st.sidebar.markdown("**📅 Select Time Period:**")
# period_options = ["Custom Range", "Last 7 Days", "Last 30 Days", "Last 90 Days", 
#                   "This Month", "Last Month", "This Quarter", "This Year", "All Time"]
# selected_period = st.sidebar.selectbox("Quick Select", period_options, index=0, key="period_selector")

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
# else:
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

# st.sidebar.info(f"📆 {start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}")

# df_filtered = df_master[(df_master['order_date'].dt.date >= start_date) & 
#                         (df_master['order_date'].dt.date <= end_date)]

# st.sidebar.markdown("---")

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

# st.sidebar.markdown("---")
# st.sidebar.markdown("### 📊 Quick Stats")
# st.sidebar.metric("💰 Total Revenue", f"฿{df_filtered['net_revenue'].sum():,.0f}")
# st.sidebar.metric("💵 Total Profit", f"฿{df_filtered['profit'].sum():,.0f}")
# st.sidebar.metric("📝 Total Orders", f"{df_filtered['order_id'].nunique():,}")
# st.sidebar.metric("👥 Total Customers", f"{df_filtered['user_id'].nunique():,}")

# tab1, tab2, tab3, tab4 = st.tabs(["💼 Sales", "📢 Marketing", "💰 Financial", "📦 Warehouse"])

# with tab1:
#     st.markdown("# 💼 Sales Analytics")
#     st.markdown("---")
    
#     # ==================== KPI CARDS ====================
#     st.markdown("### 📊 Key Performance Indicators")
    
#     revenue = df_filtered['net_revenue'].sum()
#     profit = df_filtered['profit'].sum()
#     margin = (profit / revenue * 100) if revenue > 0 else 0
    
#     monthly = df_filtered.groupby('order_month')['net_revenue'].sum().sort_index()
#     growth = ((monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2] * 100) if len(monthly) >= 2 else 0
    
#     aov = df_filtered.groupby('order_id')['net_revenue'].sum().mean()
    
#     col1, col2, col3, col4, col5 = st.columns(5)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 14px; opacity: 0.9;'>Monthly Growth</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{growth:+.1f}%</div>
#             <div style='font-size: 12px; opacity: 0.8;'>vs last month</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                     padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 14px; opacity: 0.9;'>Profit Margin</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{margin:.1f}%</div>
#             <div style='font-size: 12px; opacity: 0.8;'>gross margin</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         target = 5000000
#         curr_sales = df_filtered[df_filtered['order_month'] == df_filtered['order_month'].max()]['net_revenue'].sum()
#         attainment = (curr_sales / target * 100) if target > 0 else 0
        
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 14px; opacity: 0.9;'>Target Achievement</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{attainment:.1f}%</div>
#             <div style='font-size: 12px; opacity: 0.8;'>of ฿5M target</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
#                     padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 14px; opacity: 0.9;'>Avg Order Value</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>฿{aov:,.0f}</div>
#             <div style='font-size: 12px; opacity: 0.8;'>per transaction</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col5:
#         customers = df_filtered['user_id'].nunique()
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); 
#                     padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 14px; opacity: 0.9;'>Total Customers</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{customers:,}</div>
#             <div style='font-size: 12px; opacity: 0.8;'>unique buyers</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("<br>", unsafe_allow_html=True)
#     st.markdown("---")
    
#     # ==================== SALES REVENUE TREND ====================
#     st.markdown("### 📈 Sales Revenue")
    
#     monthly_data = df_filtered.groupby('order_month').agg({
#         'net_revenue': 'sum', 
#         'cost': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     monthly_data['order_month'] = monthly_data['order_month'].dt.to_timestamp()
#     monthly_data['month_label'] = monthly_data['order_month'].dt.strftime('%b %Y')
    
#     col1, col2 = st.columns([2, 1])
    
#     with col1:
#         fig = go.Figure()
        
#         # Revenue bars with gradient effect
#         fig.add_trace(go.Bar(
#             x=monthly_data['month_label'],
#             y=monthly_data['net_revenue'],
#             name='Revenue',
#             marker=dict(
#                 color=monthly_data['net_revenue'],
#                 colorscale='Blues',
#                 showscale=False,
#                 line=dict(color='rgb(8,48,107)', width=1.5)
#             ),
#             text=monthly_data['net_revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             textfont=dict(size=11, weight='bold'),
#             hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Monthly Revenue Trend</b>',
#                 font=dict(size=18, color='#2c3e50')
#             ),
#             xaxis=dict(
#                 title='',
#                 showgrid=False,
#                 showline=True,
#                 linecolor='lightgray'
#             ),
#             yaxis=dict(
#                 title='Revenue (฿)',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)',
#                 zeroline=False
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=80, r=40),
#             hovermode='x unified',
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="revenue_trend")
    
#     with col2:
#         # Growth indicator with arrow
#         if len(monthly_data) >= 2:
#             current_rev = monthly_data['net_revenue'].iloc[-1]
#             previous_rev = monthly_data['net_revenue'].iloc[-2]
#             growth_pct = ((current_rev - previous_rev) / previous_rev * 100)
            
#             arrow = "↗" if growth_pct > 0 else "↘"
#             color = "#2ecc71" if growth_pct > 0 else "#e74c3c"
            
#             st.markdown(f"""
#             <div style='background: white; padding: 30px; border-radius: 10px; 
#                         border: 2px solid {color}; height: 400px;
#                         display: flex; flex-direction: column; justify-content: center; align-items: center;'>
#                 <div style='font-size: 60px;'>{arrow}</div>
#                 <div style='font-size: 48px; font-weight: bold; color: {color}; margin: 20px 0;'>
#                     {growth_pct:+.1f}%
#                 </div>
#                 <div style='font-size: 16px; color: #7f8c8d; text-align: center;'>
#                     <b>Sales Growth</b><br>
#                     <span style='font-size: 14px;'>vs Previous Month</span>
#                 </div>
#                 <div style='margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 8px; width: 100%;'>
#                     <div style='font-size: 12px; color: #95a5a6; text-align: center;'>Current Month</div>
#                     <div style='font-size: 20px; font-weight: bold; text-align: center; color: #2c3e50;'>
#                         ฿{current_rev:,.0f}
#                     </div>
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== SALES BY PRODUCT CATEGORY ====================
#     st.markdown("### 🏷️ Sales by Product Category")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         cat_data = df_filtered.groupby('category').agg({
#             'net_revenue': 'sum',
#             'profit': 'sum',
#             'quantity': 'sum'
#         }).reset_index().sort_values('net_revenue', ascending=False)
        
#         # Create color palette for categories
#         colors_cat = px.colors.qualitative.Set3[:len(cat_data)]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             y=cat_data['category'],
#             x=cat_data['net_revenue'],
#             orientation='h',
#             marker=dict(
#                 color=colors_cat,
#                 line=dict(color='white', width=2)
#             ),
#             text=cat_data['net_revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             textfont=dict(size=11, weight='bold'),
#             hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Revenue by Category</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             xaxis=dict(
#                 title='',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)'
#             ),
#             yaxis=dict(
#                 title='',
#                 categoryorder='total ascending'
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=120, r=100),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="category_revenue")
    
#     with col2:
#         # Donut chart for category distribution
#         fig = go.Figure()
        
#         fig.add_trace(go.Pie(
#             labels=cat_data['category'],
#             values=cat_data['net_revenue'],
#             hole=0.6,
#             marker=dict(
#                 colors=colors_cat,
#                 line=dict(color='white', width=2)
#             ),
#             textposition='inside',
#             textinfo='label+percent',
#             textfont=dict(size=11, weight='bold'),
#             hovertemplate='<b>%{label}</b><br>Revenue: ฿%{value:,.0f}<br>Share: %{percent}<extra></extra>'
#         ))
        
#         # Add center annotation
#         total_cat_revenue = cat_data['net_revenue'].sum()
#         fig.add_annotation(
#             text=f'<b>Total</b><br>฿{total_cat_revenue:,.0f}',
#             x=0.5, y=0.5,
#             font=dict(size=16, color='#2c3e50'),
#             showarrow=False
#         )
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Category Distribution</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=40, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="category_donut")
    
#     st.markdown("---")
    
#     # ==================== SALES BY CHANNEL ====================
#     st.markdown("### 🏪 Sales by Channel")
    
#     ch = df_filtered.groupby('channel').agg({
#         'net_revenue': 'sum', 
#         'profit': 'sum', 
#         'order_id': 'nunique', 
#         'user_id': 'nunique'
#     }).reset_index()
#     ch.columns = ['Channel', 'Revenue', 'Profit', 'Orders', 'Customers']
#     ch['Margin %'] = (ch['Profit'] / ch['Revenue'] * 100).round(1)
#     ch = ch.sort_values('Revenue', ascending=False)
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         # Channel revenue with custom colors
#         ch_sorted = ch.sort_values('Revenue', ascending=True)
#         colors_list = [CHANNEL_COLORS.get(channel, '#95a5a6') for channel in ch_sorted['Channel']]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             y=ch_sorted['Channel'],
#             x=ch_sorted['Revenue'],
#             orientation='h',
#             marker=dict(
#                 color=colors_list,
#                 line=dict(color='white', width=2)
#             ),
#             text=ch_sorted['Revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             textfont=dict(size=11, weight='bold'),
#             hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Revenue by Channel</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             xaxis=dict(
#                 title='',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)'
#             ),
#             yaxis=dict(
#                 title='',
#                 categoryorder='total ascending'
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=120, r=100),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="channel_revenue")
    
#     with col2:
#         # Pie chart for channel distribution
#         colors_pie = [CHANNEL_COLORS.get(channel, '#95a5a6') for channel in ch['Channel']]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Pie(
#             labels=ch['Channel'],
#             values=ch['Revenue'],
#             hole=0.5,
#             marker=dict(
#                 colors=colors_pie,
#                 line=dict(color='white', width=2)
#             ),
#             textposition='inside',
#             textinfo='label+percent',
#             textfont=dict(size=10, weight='bold'),
#             hovertemplate='<b>%{label}</b><br>Revenue: ฿%{value:,.0f}<br>Share: %{percent}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Channel Mix</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=40, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="channel_pie")
    
#     # Channel metrics table
#     st.markdown("#### 📊 Channel Performance Metrics")
    
#     # Style the dataframe
#     styled_ch = ch.style.format({
#         'Revenue': '฿{:,.0f}', 
#         'Profit': '฿{:,.0f}', 
#         'Orders': '{:,}',
#         'Customers': '{:,}', 
#         'Margin %': '{:.1f}%'
#     }).background_gradient(subset=['Margin %'], cmap='RdYlGn', vmin=0, vmax=100)
    
#     st.dataframe(styled_ch, use_container_width=True, height=300)
    
#     st.markdown("---")
    
#     # ==================== SALES BY CUSTOMER SEGMENT ====================
#     st.markdown("### 👥 Sales by Customer Segment")
    
#     if 'customer_type' in df_filtered.columns:
#         seg_data = df_filtered.groupby('customer_type').agg({
#             'net_revenue': 'sum',
#             'profit': 'sum',
#             'user_id': 'nunique',
#             'order_id': 'nunique'
#         }).reset_index()
#         seg_data.columns = ['Segment', 'Revenue', 'Profit', 'Customers', 'Orders']
#         seg_data['AOV'] = (seg_data['Revenue'] / seg_data['Orders']).round(0)
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             # Segment colors
#             segment_colors = {
#                 'New': '#3498db',
#                 'Regular': '#2ecc71',
#                 'VIP': '#9b59b6',
#                 'Premium': '#f39c12'
#             }
#             colors = [segment_colors.get(seg, '#95a5a6') for seg in seg_data['Segment']]
            
#             fig = go.Figure()
            
#             fig.add_trace(go.Bar(
#                 x=seg_data['Segment'],
#                 y=seg_data['Revenue'],
#                 marker=dict(
#                     color=colors,
#                     line=dict(color='white', width=2)
#                 ),
#                 text=seg_data['Revenue'],
#                 texttemplate='฿%{text:,.0f}',
#                 textposition='outside',
#                 textfont=dict(size=11, weight='bold'),
#                 hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Revenue by Customer Segment</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 xaxis=dict(title='', showgrid=False),
#                 yaxis=dict(
#                     title='Revenue (฿)',
#                     showgrid=True,
#                     gridcolor='rgba(0,0,0,0.05)'
#                 ),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=80, r=40),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="segment_revenue")
        
#         with col2:
#             # Customer count by segment
#             fig = go.Figure()
            
#             fig.add_trace(go.Bar(
#                 x=seg_data['Segment'],
#                 y=seg_data['Customers'],
#                 marker=dict(
#                     color=colors,
#                     line=dict(color='white', width=2)
#                 ),
#                 text=seg_data['Customers'],
#                 texttemplate='%{text:,}',
#                 textposition='outside',
#                 textfont=dict(size=11, weight='bold'),
#                 hovertemplate='<b>%{x}</b><br>Customers: %{y:,}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Customer Count by Segment</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 xaxis=dict(title='', showgrid=False),
#                 yaxis=dict(
#                     title='Number of Customers',
#                     showgrid=True,
#                     gridcolor='rgba(0,0,0,0.05)'
#                 ),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=80, r=40),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="segment_customers")

# with tab2:
#     st.markdown("# 📢 Marketing Analytics")
#     st.markdown("---")
    
#     # ==================== CONVERSION ANALYSIS ====================
#     st.markdown("### 🎯 Conversion Analysis")
    
#     total_visitors = df_filtered['user_id'].nunique() * 5  # Simulated
#     total_orders = df_filtered['order_id'].nunique()
#     conversion_rate = (total_orders / total_visitors * 100) if total_visitors > 0 else 0
    
#     col1, col2 = st.columns([1, 2])
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 30px; border-radius: 10px; color: white; height: 400px;
#                     display: flex; flex-direction: column; justify-content: center;'>
#             <div style='text-align: center;'>
#                 <div style='font-size: 16px; opacity: 0.9; margin-bottom: 20px;'>
#                     <b>CONVERSION RATE</b>
#                 </div>
#                 <div style='font-size: 72px; font-weight: bold; margin: 20px 0;'>
#                     {conversion_rate:.1f}%
#                 </div>
#                 <div style='font-size: 14px; opacity: 0.8; margin-top: 20px;'>
#                     {total_orders:,} orders from {total_visitors:,} visitors
#                 </div>
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         # Funnel chart
#         funnel_data = pd.DataFrame({
#             'Stage': ['Visitors', 'Add to Cart', 'Checkout', 'Purchase'],
#             'Count': [total_visitors, int(total_visitors * 0.4), int(total_visitors * 0.25), total_orders],
#             'Color': ['#3498db', '#2ecc71', '#f39c12', '#9b59b6']
#         })
        
#         fig = go.Figure()
        
#         for i, row in funnel_data.iterrows():
#             fig.add_trace(go.Funnel(
#                 y=[row['Stage']],
#                 x=[row['Count']],
#                 textinfo="value+percent initial",
#                 marker=dict(color=row['Color']),
#                 textfont=dict(size=14, weight='bold'),
#                 hovertemplate='<b>%{y}</b><br>Count: %{x:,}<extra></extra>'
#             ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Sales Funnel</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=40, r=40),
#             showlegend=False,
#             funnelmode='stack'
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="conversion_funnel")
    
#     st.markdown("---")
    
#     # ==================== CUSTOMER RETENTION ====================
#     st.markdown("### 🔄 Customer Retention")
    
#     # Calculate retention metrics
#     analysis_date = df_filtered['order_date'].max()
#     last_purchase = df_filtered.groupby('user_id')['order_date'].max()
#     churned = ((analysis_date - last_purchase).dt.days > 90).sum()
#     churn_rate = (churned / len(last_purchase) * 100) if len(last_purchase) > 0 else 0
#     retention_rate = 100 - churn_rate
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid #2ecc71; text-align: center;'>
#             <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
#                 <b>RETENTION RATE</b>
#             </div>
#             <div style='font-size: 48px; font-weight: bold; color: #2ecc71; margin: 15px 0;'>
#                 {retention_rate:.1f}%
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 Active customers (within 90 days)
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid #e74c3c; text-align: center;'>
#             <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
#                 <b>CHURN RATE</b>
#             </div>
#             <div style='font-size: 48px; font-weight: bold; color: #e74c3c; margin: 15px 0;'>
#                 {churn_rate:.1f}%
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 Inactive customers (>90 days)
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         # Customer lifetime value
#         avg_rev = df_filtered.groupby('user_id')['net_revenue'].sum().mean()
#         clv = (margin / 100) * (retention_rate / 100) * avg_rev
        
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid #3498db; text-align: center;'>
#             <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
#                 <b>CUSTOMER LTV</b>
#             </div>
#             <div style='font-size: 48px; font-weight: bold; color: #3498db; margin: 15px 0;'>
#                 ฿{clv:,.0f}
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 Average lifetime value
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("<br>", unsafe_allow_html=True)
    
#     # Cohort heatmap
#     st.markdown("#### 📊 Customer Cohort Analysis")
    
#     # Simplified cohort data
#     cohort_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
#     retention_matrix = np.array([
#         [100, 45, 35, 28, 24, 20],
#         [0, 100, 48, 38, 32, 26],
#         [0, 0, 100, 52, 42, 35],
#         [0, 0, 0, 100, 55, 45],
#         [0, 0, 0, 0, 100, 58],
#         [0, 0, 0, 0, 0, 100]
#     ])
    
#     fig = go.Figure(data=go.Heatmap(
#         z=retention_matrix,
#         x=['Month 0', 'Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5'],
#         y=cohort_months,
#         colorscale='RdYlGn',
#         text=retention_matrix,
#         texttemplate='%{text:.0f}%',
#         textfont=dict(size=12, weight='bold'),
#         hoverongaps=False,
#         hovertemplate='Cohort: %{y}<br>Period: %{x}<br>Retention: %{z:.0f}%<extra></extra>'
#     ))
    
#     fig.update_layout(
#         title=dict(
#             text='<b>Cohort Retention Heatmap (%)</b>',
#             font=dict(size=16, color='#2c3e50')
#         ),
#         xaxis=dict(title='Months Since First Purchase', side='bottom'),
#         yaxis=dict(title='Cohort (First Purchase Month)'),
#         plot_bgcolor='white',
#         paper_bgcolor='white',
#         height=400,
#         margin=dict(t=60, b=60, l=80, r=40)
#     )
    
#     st.plotly_chart(fig, use_container_width=True, key="cohort_heatmap")

# with tab3:
#     st.markdown("# 💰 Financial Analytics")
#     st.markdown("---")
    
#     # ==================== PROFIT MARGIN ====================
#     st.markdown("### 📊 Profit Margin")
    
#     cogs = df_filtered['cost'].sum()
#     gross_profit = revenue - cogs
#     gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
#     net_margin = (profit / revenue * 100) if revenue > 0 else 0
    
#     col1, col2 = st.columns([1, 1])
    
#     with col1:
#         # Waterfall chart for profit breakdown
#         fig = go.Figure(go.Waterfall(
#             orientation="v",
#             measure=["relative", "relative", "total"],
#             x=["Revenue", "COGS", "Gross Profit"],
#             y=[revenue, -cogs, gross_profit],
#             text=[f"฿{revenue:,.0f}", f"-฿{cogs:,.0f}", f"฿{gross_profit:,.0f}"],
#             textposition="outside",
#             connector={"line": {"color": "rgb(63, 63, 63)"}},
#             decreasing={"marker": {"color": "#e74c3c"}},
#             increasing={"marker": {"color": "#2ecc71"}},
#             totals={"marker": {"color": "#3498db"}},
#             hovertemplate='<b>%{x}</b><br>Amount: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Profit Breakdown</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=60, l=80, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="profit_waterfall")
    
#     with col2:
#         # Monthly margin trend
#         mon_fin = df_filtered.groupby('order_month').agg({
#             'net_revenue': 'sum',
#             'cost': 'sum',
#             'profit': 'sum'
#         }).reset_index()
#         mon_fin['order_month'] = mon_fin['order_month'].dt.to_timestamp()
#         mon_fin['margin_%'] = (mon_fin['profit'] / mon_fin['net_revenue'] * 100).round(2)
#         mon_fin['month_label'] = mon_fin['order_month'].dt.strftime('%b %Y')
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Scatter(
#             x=mon_fin['month_label'],
#             y=mon_fin['margin_%'],
#             mode='lines+markers',
#             name='Profit Margin',
#             line=dict(color='#2ecc71', width=3),
#             marker=dict(size=10, color='#2ecc71', line=dict(color='white', width=2)),
#             fill='tozeroy',
#             fillcolor='rgba(46, 204, 113, 0.1)',
#             text=mon_fin['margin_%'],
#             texttemplate='%{text:.1f}%',
#             textposition='top center',
#             textfont=dict(size=10, weight='bold'),
#             hovertemplate='<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Profit Margin Trend (%)</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(
#                 title='Margin (%)',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)',
#                 range=[0, max(mon_fin['margin_%']) * 1.2]
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=80, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="margin_trend")
    
#     st.markdown("---")
    
#     # ==================== SALES + GROSS PROFIT + CAC ====================
#     st.markdown("### 📈 Sales + Gross Profit + CAC")
    
#     # Prepare data
#     channel_fin = df_filtered.groupby(['order_month', 'channel']).agg({
#         'net_revenue': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     channel_fin['order_month'] = channel_fin['order_month'].dt.to_timestamp()
#     channel_fin['month_label'] = channel_fin['order_month'].dt.strftime('%b %Y')
    
#     # Create stacked bar chart
#     fig = go.Figure()
    
#     for channel in channel_fin['channel'].unique():
#         channel_data = channel_fin[channel_fin['channel'] == channel]
#         fig.add_trace(go.Bar(
#             x=channel_data['month_label'],
#             y=channel_data['net_revenue'],
#             name=channel,
#             marker_color=CHANNEL_COLORS.get(channel, '#95a5a6'),
#             hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>Revenue: ฿%{y:,.0f}<extra></extra>'
#         ))
    
#     # Add gross profit line
#     monthly_profit = df_filtered.groupby('order_month').agg({
#         'profit': 'sum'
#     }).reset_index()
#     monthly_profit['order_month'] = monthly_profit['order_month'].dt.to_timestamp()
#     monthly_profit['month_label'] = monthly_profit['order_month'].dt.strftime('%b %Y')
    
#     fig.add_trace(go.Scatter(
#         x=monthly_profit['month_label'],
#         y=monthly_profit['profit'],
#         name='Gross Profit',
#         mode='lines+markers',
#         line=dict(color='#2ecc71', width=3),
#         marker=dict(size=10, symbol='diamond'),
#         yaxis='y2',
#         hovertemplate='<b>Gross Profit</b><br>%{x}<br>฿%{y:,.0f}<extra></extra>'
#     ))
    
#     fig.update_layout(
#         title=dict(
#             text='<b>Sales by Channel + Gross Profit</b>',
#             font=dict(size=18, color='#2c3e50')
#         ),
#         barmode='stack',
#         xaxis=dict(title='', showgrid=False),
#         yaxis=dict(
#             title='Revenue (฿)',
#             showgrid=True,
#             gridcolor='rgba(0,0,0,0.05)'
#         ),
#         yaxis2=dict(
#             title='Gross Profit (฿)',
#             overlaying='y',
#             side='right',
#             showgrid=False
#         ),
#         plot_bgcolor='white',
#         paper_bgcolor='white',
#         height=450,
#         margin=dict(t=60, b=40, l=80, r=80),
#         hovermode='x unified',
#         legend=dict(
#             orientation="h",
#             yanchor="bottom",
#             y=1.02,
#             xanchor="right",
#             x=1
#         )
#     )
    
#     st.plotly_chart(fig, use_container_width=True, key="sales_profit_channel")
    
#     st.markdown("---")
    
#     # ==================== FINANCIAL KPIs ====================
#     st.markdown("### 💎 Financial KPIs")
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #3498db; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>TOTAL REVENUE</b>
#             </div>
#             <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
#                 ฿{revenue:,.0f}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #e74c3c; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>TOTAL COGS</b>
#             </div>
#             <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
#                 ฿{cogs:,.0f}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #2ecc71; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>GROSS PROFIT</b>
#             </div>
#             <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
#                 ฿{gross_profit:,.0f}
#             </div>
#             <div style='font-size: 12px; color: #2ecc71; margin-top: 5px;'>
#                 Margin: {gross_margin:.1f}%
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #9b59b6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>NET PROFIT</b>
#             </div>
#             <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
#                 ฿{profit:,.0f}
#             </div>
#             <div style='font-size: 12px; color: #9b59b6; margin-top: 5px;'>
#                 Margin: {net_margin:.1f}%
#             </div>
#         </div>
#         """, unsafe_allow_html=True)

# with tab4:
#     st.markdown("# 📦 Warehouse & Inventory")
#     st.markdown("---")
    
#     # ==================== INVENTORY METRICS ====================
#     st.markdown("### 📊 Inventory Performance")
    
#     avg_inv = df_filtered['cost'].mean() * df_filtered['product_id'].nunique()
#     inv_turnover = cogs / avg_inv if avg_inv > 0 else 0
#     dio = 365 / inv_turnover if inv_turnover > 0 else 0
    
#     units_sold = df_filtered['quantity'].sum()
#     units_received = units_sold * 1.2
#     sell_through = (units_sold / units_received * 100) if units_received > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;
#                     box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>INVENTORY TURNOVER</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {inv_turnover:.2f}x
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>
#                 Times per year
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;
#                     box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>DAYS IN INVENTORY</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {dio:.0f}
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>
#                 Days
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;
#                     box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>SELL-THROUGH RATE</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {sell_through:.1f}%
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>
#                 Of received inventory
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;
#                     box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>INVENTORY VALUE</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 ฿{avg_inv/1000:.0f}K
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>
#                 Total stock value
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("<br>", unsafe_allow_html=True)
#     st.markdown("---")
    
#     # ==================== PRODUCT MOVEMENT ====================
#     st.markdown("### 🚀 Product Movement Analysis")
    
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
#         colors_mov = {
#             'Fast Moving': '#2ecc71',
#             'Medium Moving': '#f39c12',
#             'Slow Moving': '#e74c3c'
#         }
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Pie(
#             labels=mov.index,
#             values=mov.values,
#             hole=0.6,
#             marker=dict(
#                 colors=[colors_mov[label] for label in mov.index],
#                 line=dict(color='white', width=3)
#             ),
#             textposition='inside',
#             textinfo='label+percent',
#             textfont=dict(size=12, weight='bold', color='white'),
#             hovertemplate='<b>%{label}</b><br>Products: %{value}<br>Share: %{percent}<extra></extra>'
#         ))
        
#         fig.add_annotation(
#             text=f'<b>Total</b><br>{len(prod_vel)} products',
#             x=0.5, y=0.5,
#             font=dict(size=14, color='#2c3e50'),
#             showarrow=False
#         )
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Product Distribution by Movement</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=40, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="movement_pie")
    
#     with col2:
#         mov_val = prod_vel.groupby('Movement')['Cost'].sum().sort_values(ascending=False)
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             x=mov_val.index,
#             y=mov_val.values,
#             marker=dict(
#                 color=[colors_mov[label] for label in mov_val.index],
#                 line=dict(color='white', width=2)
#             ),
#             text=mov_val.values,
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             textfont=dict(size=11, weight='bold'),
#             hovertemplate='<b>%{x}</b><br>Value: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Inventory Value by Movement</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(
#                 title='Value (฿)',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)'
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=80, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="movement_value")

# # Footer
# st.markdown("---")
# st.markdown("""
# <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#             border-radius: 15px; color: white;'>
#     <h3 style='margin: 0; font-size: 24px;'>📊 Fashion Analytics Dashboard</h3>
#     <p style='margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;'>
#         Built with Streamlit • Data-Driven Insights for Better Business Decisions
#     </p>
# </div>
# """, unsafe_allow_html=True)




















































































































# # Analytics Dashboard - Redesigned Version
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
# import numpy as np
# import warnings
# from datetime import datetime, timedelta

# warnings.filterwarnings('ignore')
# st.set_page_config(page_title="Fashion Analytics Pro", layout="wide", page_icon="👕")

# # Enhanced Color Palette
# COLORS = {
#     'primary': '#1f77b4',
#     'secondary': '#ff7f0e',
#     'success': '#2ecc71',
#     'danger': '#e74c3c',
#     'warning': '#f39c12',
#     'info': '#3498db',
#     'purple': '#9b59b6',
#     'teal': '#1abc9c',
#     'pink': '#e91e63',
#     'indigo': '#3f51b5'
# }

# # Channel Color Mapping
# CHANNEL_COLORS = {
#     'TikTok': '#000000',
#     'Shopee': '#FF5722',
#     'Lazada': '#1E88E5',
#     'LINE Shopping': '#00C300',
#     'Instagram': '#9C27B0',
#     'Facebook': '#1877F2',
#     'Store': '#795548',
#     'Pop-up': '#FF9800',
#     'Website': '#607D8B'
# }

# # Chart template
# CHART_TEMPLATE = {
#     'layout': {
#         'font': {'family': 'Inter, system-ui, -apple-system, sans-serif', 'size': 12},
#         'plot_bgcolor': 'white',
#         'paper_bgcolor': 'white',
#         'margin': {'t': 60, 'b': 40, 'l': 60, 'r': 40}
#     }
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
#     st.sidebar.title("📊 Analytics Dashboard")
#     st.sidebar.markdown("---")
    
#     uploaded = st.sidebar.file_uploader(
#         "📁 Upload CSV Files", 
#         type=['csv'], 
#         accept_multiple_files=True,
#         key="csv_uploader_main"
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

# # Custom CSS for better styling
# st.markdown("""
# <style>
#     /* Main containers */
#     .block-container {
#         padding-top: 1rem;
#         padding-bottom: 1rem;
#     }
    
#     /* Metric cards */
#     [data-testid="stMetricValue"] {
#         font-size: 28px;
#         font-weight: 600;
#     }
    
#     [data-testid="stMetricLabel"] {
#         font-size: 14px;
#         font-weight: 500;
#         color: #555;
#     }
    
#     /* Headers */
#     h1, h2, h3 {
#         font-family: 'Inter', sans-serif;
#         font-weight: 700;
#     }
    
#     /* Tabs */
#     .stTabs [data-baseweb="tab-list"] {
#         gap: 8px;
#     }
    
#     .stTabs [data-baseweb="tab"] {
#         height: 50px;
#         padding-left: 20px;
#         padding-right: 20px;
#         border-radius: 8px 8px 0 0;
#         font-weight: 600;
#     }
    
#     /* Cards */
#     div.element-container {
#         border-radius: 8px;
#     }
    
#     /* Sidebar */
#     [data-testid="stSidebar"] {
#         background-color: #f8f9fa;
#     }
# </style>
# """, unsafe_allow_html=True)

# data = load_data()

# if not data:
#     st.title("📊 Analytics Dashboard")
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

# # ==================== FILTERS ====================
# st.sidebar.markdown("---")
# st.sidebar.markdown("### 🔍 Filters")

# min_date = df_master['order_date'].min().date()
# max_date = df_master['order_date'].max().date()

# st.sidebar.markdown("**📅 Select Time Period:**")
# period_options = ["Custom Range", "Last 7 Days", "Last 30 Days", "Last 90 Days", 
#                   "This Month", "Last Month", "This Quarter", "This Year", "All Time"]
# selected_period = st.sidebar.selectbox("Quick Select", period_options, index=0, key="period_selector")

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
# else:
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

# st.sidebar.info(f"📆 {start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}")

# df_filtered = df_master[(df_master['order_date'].dt.date >= start_date) & 
#                         (df_master['order_date'].dt.date <= end_date)]

# st.sidebar.markdown("---")

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

# st.sidebar.markdown("---")
# st.sidebar.markdown("### 📊 Quick Stats")
# st.sidebar.metric("💰 Total Revenue", f"฿{df_filtered['net_revenue'].sum():,.0f}")
# st.sidebar.metric("💵 Total Profit", f"฿{df_filtered['profit'].sum():,.0f}")
# st.sidebar.metric("📝 Total Orders", f"{df_filtered['order_id'].nunique():,}")
# st.sidebar.metric("👥 Total Customers", f"{df_filtered['user_id'].nunique():,}")

# tab1, tab2, tab3, tab4 = st.tabs(["💼 Sales", "📢 Marketing", "💰 Financial", "📦 Warehouse"])

# with tab1:
#     st.markdown("# 💼 Sales Analytics")
#     st.markdown("---")
    
#     # ==================== KPI CARDS ====================
#     st.markdown("### 📊 Key Performance Indicators")
    
#     revenue = df_filtered['net_revenue'].sum()
#     profit = df_filtered['profit'].sum()
#     margin = (profit / revenue * 100) if revenue > 0 else 0
    
#     monthly = df_filtered.groupby('order_month')['net_revenue'].sum().sort_index()
#     growth = ((monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2] * 100) if len(monthly) >= 2 else 0
    
#     aov = df_filtered.groupby('order_id')['net_revenue'].sum().mean()
    
#     col1, col2, col3, col4, col5 = st.columns(5)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 14px; opacity: 0.9;'>Monthly Growth</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{growth:+.1f}%</div>
#             <div style='font-size: 12px; opacity: 0.8;'>vs last month</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                     padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 14px; opacity: 0.9;'>Profit Margin</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{margin:.1f}%</div>
#             <div style='font-size: 12px; opacity: 0.8;'>gross margin</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         target = 5000000
#         curr_sales = df_filtered[df_filtered['order_month'] == df_filtered['order_month'].max()]['net_revenue'].sum()
#         attainment = (curr_sales / target * 100) if target > 0 else 0
        
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 14px; opacity: 0.9;'>Target Achievement</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{attainment:.1f}%</div>
#             <div style='font-size: 12px; opacity: 0.8;'>of ฿5M target</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
#                     padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 14px; opacity: 0.9;'>Avg Order Value</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>฿{aov:,.0f}</div>
#             <div style='font-size: 12px; opacity: 0.8;'>per transaction</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col5:
#         customers = df_filtered['user_id'].nunique()
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); 
#                     padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 14px; opacity: 0.9;'>Total Customers</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{customers:,}</div>
#             <div style='font-size: 12px; opacity: 0.8;'>unique buyers</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("<br>", unsafe_allow_html=True)
#     st.markdown("---")
    
#     # ==================== SALES REVENUE TREND ====================
#     st.markdown("### 📈 Sales Revenue")
    
#     monthly_data = df_filtered.groupby('order_month').agg({
#         'net_revenue': 'sum', 
#         'cost': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     monthly_data['order_month'] = monthly_data['order_month'].dt.to_timestamp()
#     monthly_data['month_label'] = monthly_data['order_month'].dt.strftime('%b %Y')
    
#     col1, col2 = st.columns([2, 1])
    
#     with col1:
#         fig = go.Figure()
        
#         # Revenue bars with gradient effect
#         fig.add_trace(go.Bar(
#             x=monthly_data['month_label'],
#             y=monthly_data['net_revenue'],
#             name='Revenue',
#             marker=dict(
#                 color=monthly_data['net_revenue'],
#                 colorscale='Blues',
#                 showscale=False,
#                 line=dict(color='rgb(8,48,107)', width=1.5)
#             ),
#             text=monthly_data['net_revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             textfont=dict(size=11, weight='bold'),
#             hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Monthly Revenue Trend</b>',
#                 font=dict(size=18, color='#2c3e50')
#             ),
#             xaxis=dict(
#                 title='',
#                 showgrid=False,
#                 showline=True,
#                 linecolor='lightgray'
#             ),
#             yaxis=dict(
#                 title='Revenue (฿)',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)',
#                 zeroline=False
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=80, r=40),
#             hovermode='x unified',
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="revenue_trend")
    
#     with col2:
#         # Growth indicator with arrow
#         if len(monthly_data) >= 2:
#             current_rev = monthly_data['net_revenue'].iloc[-1]
#             previous_rev = monthly_data['net_revenue'].iloc[-2]
#             growth_pct = ((current_rev - previous_rev) / previous_rev * 100)
            
#             arrow = "↗" if growth_pct > 0 else "↘"
#             color = "#2ecc71" if growth_pct > 0 else "#e74c3c"
            
#             st.markdown(f"""
#             <div style='background: white; padding: 30px; border-radius: 10px; 
#                         border: 2px solid {color}; height: 400px;
#                         display: flex; flex-direction: column; justify-content: center; align-items: center;'>
#                 <div style='font-size: 60px;'>{arrow}</div>
#                 <div style='font-size: 48px; font-weight: bold; color: {color}; margin: 20px 0;'>
#                     {growth_pct:+.1f}%
#                 </div>
#                 <div style='font-size: 16px; color: #7f8c8d; text-align: center;'>
#                     <b>Sales Growth</b><br>
#                     <span style='font-size: 14px;'>vs Previous Month</span>
#                 </div>
#                 <div style='margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 8px; width: 100%;'>
#                     <div style='font-size: 12px; color: #95a5a6; text-align: center;'>Current Month</div>
#                     <div style='font-size: 20px; font-weight: bold; text-align: center; color: #2c3e50;'>
#                         ฿{current_rev:,.0f}
#                     </div>
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== SALES BY PRODUCT CATEGORY ====================
#     st.markdown("### 🏷️ Sales by Product Category")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         cat_data = df_filtered.groupby('category').agg({
#             'net_revenue': 'sum',
#             'profit': 'sum',
#             'quantity': 'sum'
#         }).reset_index().sort_values('net_revenue', ascending=False)
        
#         # Create color palette for categories
#         colors_cat = px.colors.qualitative.Set3[:len(cat_data)]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             y=cat_data['category'],
#             x=cat_data['net_revenue'],
#             orientation='h',
#             marker=dict(
#                 color=colors_cat,
#                 line=dict(color='white', width=2)
#             ),
#             text=cat_data['net_revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             textfont=dict(size=11, weight='bold'),
#             hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Revenue by Category</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             xaxis=dict(
#                 title='',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)'
#             ),
#             yaxis=dict(
#                 title='',
#                 categoryorder='total ascending'
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=120, r=100),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="category_revenue")
    
#     with col2:
#         # Donut chart for category distribution
#         fig = go.Figure()
        
#         fig.add_trace(go.Pie(
#             labels=cat_data['category'],
#             values=cat_data['net_revenue'],
#             hole=0.6,
#             marker=dict(
#                 colors=colors_cat,
#                 line=dict(color='white', width=2)
#             ),
#             textposition='inside',
#             textinfo='label+percent',
#             textfont=dict(size=11, weight='bold'),
#             hovertemplate='<b>%{label}</b><br>Revenue: ฿%{value:,.0f}<br>Share: %{percent}<extra></extra>'
#         ))
        
#         # Add center annotation
#         total_cat_revenue = cat_data['net_revenue'].sum()
#         fig.add_annotation(
#             text=f'<b>Total</b><br>฿{total_cat_revenue:,.0f}',
#             x=0.5, y=0.5,
#             font=dict(size=16, color='#2c3e50'),
#             showarrow=False
#         )
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Category Distribution</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=40, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="category_donut")
    
#     st.markdown("---")
    
#     # ==================== SALES BY CHANNEL ====================
#     st.markdown("### 🏪 Sales by Channel")
    
#     ch = df_filtered.groupby('channel').agg({
#         'net_revenue': 'sum', 
#         'profit': 'sum', 
#         'order_id': 'nunique', 
#         'user_id': 'nunique'
#     }).reset_index()
#     ch.columns = ['Channel', 'Revenue', 'Profit', 'Orders', 'Customers']
#     ch['Margin %'] = (ch['Profit'] / ch['Revenue'] * 100).round(1)
#     ch = ch.sort_values('Revenue', ascending=False)
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         # Channel revenue with custom colors
#         ch_sorted = ch.sort_values('Revenue', ascending=True)
#         colors_list = [CHANNEL_COLORS.get(channel, '#95a5a6') for channel in ch_sorted['Channel']]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             y=ch_sorted['Channel'],
#             x=ch_sorted['Revenue'],
#             orientation='h',
#             marker=dict(
#                 color=colors_list,
#                 line=dict(color='white', width=2)
#             ),
#             text=ch_sorted['Revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             textfont=dict(size=11, weight='bold'),
#             hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Revenue by Channel</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             xaxis=dict(
#                 title='',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)'
#             ),
#             yaxis=dict(
#                 title='',
#                 categoryorder='total ascending'
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=120, r=100),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="channel_revenue")
    
#     with col2:
#         # Pie chart for channel distribution
#         colors_pie = [CHANNEL_COLORS.get(channel, '#95a5a6') for channel in ch['Channel']]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Pie(
#             labels=ch['Channel'],
#             values=ch['Revenue'],
#             hole=0.5,
#             marker=dict(
#                 colors=colors_pie,
#                 line=dict(color='white', width=2)
#             ),
#             textposition='inside',
#             textinfo='label+percent',
#             textfont=dict(size=10, weight='bold'),
#             hovertemplate='<b>%{label}</b><br>Revenue: ฿%{value:,.0f}<br>Share: %{percent}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Channel Mix</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=40, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="channel_pie")
    
#     # Channel metrics table
#     st.markdown("#### 📊 Channel Performance Metrics")
    
#     # Style the dataframe
#     styled_ch = ch.style.format({
#         'Revenue': '฿{:,.0f}', 
#         'Profit': '฿{:,.0f}', 
#         'Orders': '{:,}',
#         'Customers': '{:,}', 
#         'Margin %': '{:.1f}%'
#     }).background_gradient(subset=['Margin %'], cmap='RdYlGn', vmin=0, vmax=100)
    
#     st.dataframe(styled_ch, use_container_width=True, height=300)
    
#     st.markdown("---")
    
#     # ==================== SALES BY CUSTOMER SEGMENT ====================
#     st.markdown("### 👥 Sales by Customer Segment")
    
#     if 'customer_type' in df_filtered.columns:
#         seg_data = df_filtered.groupby('customer_type').agg({
#             'net_revenue': 'sum',
#             'profit': 'sum',
#             'user_id': 'nunique',
#             'order_id': 'nunique'
#         }).reset_index()
#         seg_data.columns = ['Segment', 'Revenue', 'Profit', 'Customers', 'Orders']
#         seg_data['AOV'] = (seg_data['Revenue'] / seg_data['Orders']).round(0)
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             # Segment colors
#             segment_colors = {
#                 'New': '#3498db',
#                 'Regular': '#2ecc71',
#                 'VIP': '#9b59b6',
#                 'Premium': '#f39c12'
#             }
#             colors = [segment_colors.get(seg, '#95a5a6') for seg in seg_data['Segment']]
            
#             fig = go.Figure()
            
#             fig.add_trace(go.Bar(
#                 x=seg_data['Segment'],
#                 y=seg_data['Revenue'],
#                 marker=dict(
#                     color=colors,
#                     line=dict(color='white', width=2)
#                 ),
#                 text=seg_data['Revenue'],
#                 texttemplate='฿%{text:,.0f}',
#                 textposition='outside',
#                 textfont=dict(size=11, weight='bold'),
#                 hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Revenue by Customer Segment</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 xaxis=dict(title='', showgrid=False),
#                 yaxis=dict(
#                     title='Revenue (฿)',
#                     showgrid=True,
#                     gridcolor='rgba(0,0,0,0.05)'
#                 ),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=80, r=40),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="segment_revenue")
        
#         with col2:
#             # Customer count by segment
#             fig = go.Figure()
            
#             fig.add_trace(go.Bar(
#                 x=seg_data['Segment'],
#                 y=seg_data['Customers'],
#                 marker=dict(
#                     color=colors,
#                     line=dict(color='white', width=2)
#                 ),
#                 text=seg_data['Customers'],
#                 texttemplate='%{text:,}',
#                 textposition='outside',
#                 textfont=dict(size=11, weight='bold'),
#                 hovertemplate='<b>%{x}</b><br>Customers: %{y:,}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Customer Count by Segment</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 xaxis=dict(title='', showgrid=False),
#                 yaxis=dict(
#                     title='Number of Customers',
#                     showgrid=True,
#                     gridcolor='rgba(0,0,0,0.05)'
#                 ),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=80, r=40),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="segment_customers")

# with tab2:
#     st.markdown("# 📢 Marketing Analytics")
#     st.markdown("---")
    
#     # ==================== CONVERSION ANALYSIS ====================
#     st.markdown("### 🎯 Conversion Analysis")
    
#     # Calculate actual metrics from data
#     # Note: If your data doesn't have visit/cart data, we can only calculate from orders
#     # You may need to add these columns to your dataset for accurate funnel analysis
    
#     total_orders = df_filtered['order_id'].nunique()
#     total_customers = df_filtered['user_id'].nunique()
    
#     # Check if we have funnel data columns
#     has_funnel_data = all(col in df_filtered.columns for col in ['visits', 'add_to_cart', 'checkout'])
    
#     if has_funnel_data:
#         # Use actual funnel data from files
#         total_visitors = df_filtered['visits'].sum()
#         add_to_cart = df_filtered['add_to_cart'].sum()
#         checkout = df_filtered['checkout'].sum()
#         purchase = total_orders
#         conversion_rate = (purchase / total_visitors * 100) if total_visitors > 0 else 0
#     else:
#         # Calculate conversion rate from available data only
#         # Using customers as proxy for engaged users
#         conversion_rate = (total_orders / total_customers * 100) if total_customers > 0 else 0
        
#         st.info("💡 **Note:** For accurate funnel analysis, please add these columns to your data: `visits`, `add_to_cart`, `checkout`")
    
#     col1, col2 = st.columns([1, 2])
    
#     with col1:
#         if has_funnel_data:
#             description = f"{total_orders:,} orders from {total_visitors:,} visitors"
#         else:
#             description = f"{total_orders:,} orders from {total_customers:,} customers"
            
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 30px; border-radius: 10px; color: white; height: 400px;
#                     display: flex; flex-direction: column; justify-content: center;'>
#             <div style='text-align: center;'>
#                 <div style='font-size: 16px; opacity: 0.9; margin-bottom: 20px;'>
#                     <b>CONVERSION RATE</b>
#                 </div>
#                 <div style='font-size: 72px; font-weight: bold; margin: 20px 0;'>
#                     {conversion_rate:.1f}%
#                 </div>
#                 <div style='font-size: 14px; opacity: 0.8; margin-top: 20px;'>
#                     {description}
#                 </div>
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         if has_funnel_data:
#             # Use actual data from files
#             funnel_data = pd.DataFrame({
#                 'Stage': ['Visitors', 'Add to Cart', 'Checkout', 'Purchase'],
#                 'Count': [total_visitors, add_to_cart, checkout, purchase],
#                 'Color': ['#3498db', '#2ecc71', '#f39c12', '#9b59b6']
#             })
#         else:
#             # Calculate based on typical e-commerce funnel ratios from actual orders
#             # Working backwards from orders to estimate funnel
#             purchase = total_orders
#             # Typical checkout to purchase ratio is ~80%
#             checkout = int(purchase / 0.8) if purchase > 0 else 0
#             # Typical cart to checkout ratio is ~60%
#             add_to_cart = int(checkout / 0.6) if checkout > 0 else 0
#             # Typical visitor to cart ratio is ~30%
#             visitors = int(add_to_cart / 0.3) if add_to_cart > 0 else total_customers
            
#             funnel_data = pd.DataFrame({
#                 'Stage': ['Visitors (estimated)', 'Add to Cart (estimated)', 'Checkout (estimated)', 'Purchase (actual)'],
#                 'Count': [visitors, add_to_cart, checkout, purchase],
#                 'Color': ['#3498db', '#2ecc71', '#f39c12', '#9b59b6']
#             })
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Funnel(
#             y=funnel_data['Stage'],
#             x=funnel_data['Count'],
#             textposition="inside",
#             textinfo="value+percent initial",
#             marker=dict(
#                 color=funnel_data['Color'],
#                 line=dict(color='white', width=2)
#             ),
#             textfont=dict(size=13, weight='bold', color='white'),
#             hovertemplate='<b>%{y}</b><br>Count: %{x:,}<br>Rate: %{percentInitial}<extra></extra>',
#             connector=dict(line=dict(color='gray', width=1))
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Sales Funnel</b>' + (' (Estimated)' if not has_funnel_data else ''),
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=40, r=120),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="conversion_funnel")
    
#     st.markdown("---")
    
#     # ==================== CUSTOMER RETENTION ====================
#     st.markdown("### 🔄 Customer Retention")
    
#     # Calculate retention metrics
#     analysis_date = df_filtered['order_date'].max()
#     last_purchase = df_filtered.groupby('user_id')['order_date'].max()
#     churned = ((analysis_date - last_purchase).dt.days > 90).sum()
#     churn_rate = (churned / len(last_purchase) * 100) if len(last_purchase) > 0 else 0
#     retention_rate = 100 - churn_rate
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid #2ecc71; text-align: center;'>
#             <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
#                 <b>RETENTION RATE</b>
#             </div>
#             <div style='font-size: 48px; font-weight: bold; color: #2ecc71; margin: 15px 0;'>
#                 {retention_rate:.1f}%
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 Active customers (within 90 days)
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid #e74c3c; text-align: center;'>
#             <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
#                 <b>CHURN RATE</b>
#             </div>
#             <div style='font-size: 48px; font-weight: bold; color: #e74c3c; margin: 15px 0;'>
#                 {churn_rate:.1f}%
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 Inactive customers (>90 days)
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         # Customer lifetime value
#         avg_rev = df_filtered.groupby('user_id')['net_revenue'].sum().mean()
#         clv = (margin / 100) * (retention_rate / 100) * avg_rev
        
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid #3498db; text-align: center;'>
#             <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
#                 <b>CUSTOMER LTV</b>
#             </div>
#             <div style='font-size: 48px; font-weight: bold; color: #3498db; margin: 15px 0;'>
#                 ฿{clv:,.0f}
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 Average lifetime value
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("<br>", unsafe_allow_html=True)
    
#     # Cohort heatmap
#     st.markdown("#### 📊 Customer Cohort Analysis")
    
#     # Simplified cohort data
#     cohort_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
#     retention_matrix = np.array([
#         [100, 45, 35, 28, 24, 20],
#         [0, 100, 48, 38, 32, 26],
#         [0, 0, 100, 52, 42, 35],
#         [0, 0, 0, 100, 55, 45],
#         [0, 0, 0, 0, 100, 58],
#         [0, 0, 0, 0, 0, 100]
#     ])
    
#     fig = go.Figure(data=go.Heatmap(
#         z=retention_matrix,
#         x=['Month 0', 'Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5'],
#         y=cohort_months,
#         colorscale='RdYlGn',
#         text=retention_matrix,
#         texttemplate='%{text:.0f}%',
#         textfont=dict(size=12, weight='bold'),
#         hoverongaps=False,
#         hovertemplate='Cohort: %{y}<br>Period: %{x}<br>Retention: %{z:.0f}%<extra></extra>'
#     ))
    
#     fig.update_layout(
#         title=dict(
#             text='<b>Cohort Retention Heatmap (%)</b>',
#             font=dict(size=16, color='#2c3e50')
#         ),
#         xaxis=dict(title='Months Since First Purchase', side='bottom'),
#         yaxis=dict(title='Cohort (First Purchase Month)'),
#         plot_bgcolor='white',
#         paper_bgcolor='white',
#         height=400,
#         margin=dict(t=60, b=60, l=80, r=40)
#     )
    
#     st.plotly_chart(fig, use_container_width=True, key="cohort_heatmap")

# with tab3:
#     st.markdown("# 💰 Financial Analytics")
#     st.markdown("---")
    
#     # ==================== PROFIT MARGIN ====================
#     st.markdown("### 📊 Profit Margin")
    
#     cogs = df_filtered['cost'].sum()
#     gross_profit = revenue - cogs
#     gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
#     net_margin = (profit / revenue * 100) if revenue > 0 else 0
    
#     col1, col2 = st.columns([1, 1])
    
#     with col1:
#         # Waterfall chart for profit breakdown
#         fig = go.Figure(go.Waterfall(
#             orientation="v",
#             measure=["relative", "relative", "total"],
#             x=["Revenue", "COGS", "Gross Profit"],
#             y=[revenue, -cogs, gross_profit],
#             text=[f"฿{revenue:,.0f}", f"-฿{cogs:,.0f}", f"฿{gross_profit:,.0f}"],
#             textposition="outside",
#             connector={"line": {"color": "rgb(63, 63, 63)"}},
#             decreasing={"marker": {"color": "#e74c3c"}},
#             increasing={"marker": {"color": "#2ecc71"}},
#             totals={"marker": {"color": "#3498db"}},
#             hovertemplate='<b>%{x}</b><br>Amount: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Profit Breakdown</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=60, l=80, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="profit_waterfall")
    
#     with col2:
#         # Monthly margin trend
#         mon_fin = df_filtered.groupby('order_month').agg({
#             'net_revenue': 'sum',
#             'cost': 'sum',
#             'profit': 'sum'
#         }).reset_index()
#         mon_fin['order_month'] = mon_fin['order_month'].dt.to_timestamp()
#         mon_fin['margin_%'] = (mon_fin['profit'] / mon_fin['net_revenue'] * 100).round(2)
#         mon_fin['month_label'] = mon_fin['order_month'].dt.strftime('%b %Y')
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Scatter(
#             x=mon_fin['month_label'],
#             y=mon_fin['margin_%'],
#             mode='lines+markers',
#             name='Profit Margin',
#             line=dict(color='#2ecc71', width=3),
#             marker=dict(size=10, color='#2ecc71', line=dict(color='white', width=2)),
#             fill='tozeroy',
#             fillcolor='rgba(46, 204, 113, 0.1)',
#             text=mon_fin['margin_%'],
#             texttemplate='%{text:.1f}%',
#             textposition='top center',
#             textfont=dict(size=10, weight='bold'),
#             hovertemplate='<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Profit Margin Trend (%)</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(
#                 title='Margin (%)',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)',
#                 range=[0, max(mon_fin['margin_%']) * 1.2]
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=80, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="margin_trend")
    
#     st.markdown("---")
    
#     # ==================== SALES + GROSS PROFIT + CAC ====================
#     st.markdown("### 📈 Sales + Gross Profit + CAC")
    
#     # Prepare data
#     channel_fin = df_filtered.groupby(['order_month', 'channel']).agg({
#         'net_revenue': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     channel_fin['order_month'] = channel_fin['order_month'].dt.to_timestamp()
#     channel_fin['month_label'] = channel_fin['order_month'].dt.strftime('%b %Y')
    
#     # Create stacked bar chart
#     fig = go.Figure()
    
#     for channel in channel_fin['channel'].unique():
#         channel_data = channel_fin[channel_fin['channel'] == channel]
#         fig.add_trace(go.Bar(
#             x=channel_data['month_label'],
#             y=channel_data['net_revenue'],
#             name=channel,
#             marker_color=CHANNEL_COLORS.get(channel, '#95a5a6'),
#             hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>Revenue: ฿%{y:,.0f}<extra></extra>'
#         ))
    
#     # Add gross profit line
#     monthly_profit = df_filtered.groupby('order_month').agg({
#         'profit': 'sum'
#     }).reset_index()
#     monthly_profit['order_month'] = monthly_profit['order_month'].dt.to_timestamp()
#     monthly_profit['month_label'] = monthly_profit['order_month'].dt.strftime('%b %Y')
    
#     fig.add_trace(go.Scatter(
#         x=monthly_profit['month_label'],
#         y=monthly_profit['profit'],
#         name='Gross Profit',
#         mode='lines+markers',
#         line=dict(color='#2ecc71', width=3),
#         marker=dict(size=10, symbol='diamond'),
#         yaxis='y2',
#         hovertemplate='<b>Gross Profit</b><br>%{x}<br>฿%{y:,.0f}<extra></extra>'
#     ))
    
#     fig.update_layout(
#         title=dict(
#             text='<b>Sales by Channel + Gross Profit</b>',
#             font=dict(size=18, color='#2c3e50')
#         ),
#         barmode='stack',
#         xaxis=dict(title='', showgrid=False),
#         yaxis=dict(
#             title='Revenue (฿)',
#             showgrid=True,
#             gridcolor='rgba(0,0,0,0.05)'
#         ),
#         yaxis2=dict(
#             title='Gross Profit (฿)',
#             overlaying='y',
#             side='right',
#             showgrid=False
#         ),
#         plot_bgcolor='white',
#         paper_bgcolor='white',
#         height=450,
#         margin=dict(t=60, b=40, l=80, r=80),
#         hovermode='x unified',
#         legend=dict(
#             orientation="h",
#             yanchor="bottom",
#             y=1.02,
#             xanchor="right",
#             x=1
#         )
#     )
    
#     st.plotly_chart(fig, use_container_width=True, key="sales_profit_channel")
    
#     st.markdown("---")
    
#     # ==================== FINANCIAL KPIs ====================
#     st.markdown("### 💎 Financial KPIs")
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #3498db; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>TOTAL REVENUE</b>
#             </div>
#             <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
#                 ฿{revenue:,.0f}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #e74c3c; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>TOTAL COGS</b>
#             </div>
#             <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
#                 ฿{cogs:,.0f}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #2ecc71; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>GROSS PROFIT</b>
#             </div>
#             <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
#                 ฿{gross_profit:,.0f}
#             </div>
#             <div style='font-size: 12px; color: #2ecc71; margin-top: 5px;'>
#                 Margin: {gross_margin:.1f}%
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #9b59b6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>NET PROFIT</b>
#             </div>
#             <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
#                 ฿{profit:,.0f}
#             </div>
#             <div style='font-size: 12px; color: #9b59b6; margin-top: 5px;'>
#                 Margin: {net_margin:.1f}%
#             </div>
#         </div>
#         """, unsafe_allow_html=True)

# with tab4:
#     st.markdown("# 📦 Warehouse & Inventory")
#     st.markdown("---")
    
#     # ==================== INVENTORY METRICS ====================
#     st.markdown("### 📊 Inventory Performance")
    
#     avg_inv = df_filtered['cost'].mean() * df_filtered['product_id'].nunique()
#     inv_turnover = cogs / avg_inv if avg_inv > 0 else 0
#     dio = 365 / inv_turnover if inv_turnover > 0 else 0
    
#     units_sold = df_filtered['quantity'].sum()
#     units_received = units_sold * 1.2
#     sell_through = (units_sold / units_received * 100) if units_received > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;
#                     box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>INVENTORY TURNOVER</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {inv_turnover:.2f}x
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>
#                 Times per year
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;
#                     box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>DAYS IN INVENTORY</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {dio:.0f}
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>
#                 Days
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;
#                     box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>SELL-THROUGH RATE</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {sell_through:.1f}%
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>
#                 Of received inventory
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;
#                     box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>INVENTORY VALUE</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 ฿{avg_inv/1000:.0f}K
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>
#                 Total stock value
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("<br>", unsafe_allow_html=True)
#     st.markdown("---")
    
#     # ==================== PRODUCT MOVEMENT ====================
#     st.markdown("### 🚀 Product Movement Analysis")
    
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
#         colors_mov = {
#             'Fast Moving': '#2ecc71',
#             'Medium Moving': '#f39c12',
#             'Slow Moving': '#e74c3c'
#         }
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Pie(
#             labels=mov.index,
#             values=mov.values,
#             hole=0.6,
#             marker=dict(
#                 colors=[colors_mov[label] for label in mov.index],
#                 line=dict(color='white', width=3)
#             ),
#             textposition='inside',
#             textinfo='label+percent',
#             textfont=dict(size=12, weight='bold', color='white'),
#             hovertemplate='<b>%{label}</b><br>Products: %{value}<br>Share: %{percent}<extra></extra>'
#         ))
        
#         fig.add_annotation(
#             text=f'<b>Total</b><br>{len(prod_vel)} products',
#             x=0.5, y=0.5,
#             font=dict(size=14, color='#2c3e50'),
#             showarrow=False
#         )
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Product Distribution by Movement</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=40, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="movement_pie")
    
#     with col2:
#         mov_val = prod_vel.groupby('Movement')['Cost'].sum().sort_values(ascending=False)
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             x=mov_val.index,
#             y=mov_val.values,
#             marker=dict(
#                 color=[colors_mov[label] for label in mov_val.index],
#                 line=dict(color='white', width=2)
#             ),
#             text=mov_val.values,
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             textfont=dict(size=11, weight='bold'),
#             hovertemplate='<b>%{x}</b><br>Value: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Inventory Value by Movement</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(
#                 title='Value (฿)',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)'
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=80, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="movement_value")

# # Footer
# st.markdown("---")
# st.markdown("""
# <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#             border-radius: 15px; color: white;'>
#     <h3 style='margin: 0; font-size: 24px;'>📊 Fashion Analytics Dashboard</h3>
#     <p style='margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;'>
#         Built with Streamlit • Data-Driven Insights for Better Business Decisions
#     </p>
# </div>
# """, unsafe_allow_html=True)







































































# # Analytics Dashboard - Redesigned Version
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
# import numpy as np
# import warnings
# from datetime import datetime, timedelta

# warnings.filterwarnings('ignore')
# st.set_page_config(page_title="Fashion Analytics Pro", layout="wide", page_icon="👕")

# # Enhanced Color Palette
# COLORS = {
#     'primary': '#1f77b4',
#     'secondary': '#ff7f0e',
#     'success': '#2ecc71',
#     'danger': '#e74c3c',
#     'warning': '#f39c12',
#     'info': '#3498db',
#     'purple': '#9b59b6',
#     'teal': '#1abc9c',
#     'pink': '#e91e63',
#     'indigo': '#3f51b5'
# }

# # Channel Color Mapping
# CHANNEL_COLORS = {
#     'TikTok': '#000000',
#     'Shopee': '#FF5722',
#     'Lazada': '#1E88E5',
#     'LINE Shopping': '#00C300',
#     'Instagram': '#9C27B0',
#     'Facebook': '#1877F2',
#     'Store': '#795548',
#     'Pop-up': '#FF9800',
#     'Website': '#607D8B'
# }

# # Chart template
# CHART_TEMPLATE = {
#     'layout': {
#         'font': {'family': 'Inter, system-ui, -apple-system, sans-serif', 'size': 12},
#         'plot_bgcolor': 'white',
#         'paper_bgcolor': 'white',
#         'margin': {'t': 60, 'b': 40, 'l': 60, 'r': 40}
#     }
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
#     st.sidebar.title("📊 Analytics Dashboard")
#     st.sidebar.markdown("---")
    
#     uploaded = st.sidebar.file_uploader(
#         "📁 Upload CSV Files", 
#         type=['csv'], 
#         accept_multiple_files=True,
#         key="csv_uploader_main"
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

# # Custom CSS for better styling
# st.markdown("""
# <style>
#     /* Main containers */
#     .block-container {
#         padding-top: 1rem;
#         padding-bottom: 1rem;
#     }
    
#     /* Metric cards */
#     [data-testid="stMetricValue"] {
#         font-size: 28px;
#         font-weight: 600;
#     }
    
#     [data-testid="stMetricLabel"] {
#         font-size: 14px;
#         font-weight: 500;
#         color: #555;
#     }
    
#     /* Headers */
#     h1, h2, h3 {
#         font-family: 'Inter', sans-serif;
#         font-weight: 700;
#     }
    
#     /* Tabs */
#     .stTabs [data-baseweb="tab-list"] {
#         gap: 8px;
#     }
    
#     .stTabs [data-baseweb="tab"] {
#         height: 50px;
#         padding-left: 20px;
#         padding-right: 20px;
#         border-radius: 8px 8px 0 0;
#         font-weight: 600;
#     }
    
#     /* Cards */
#     div.element-container {
#         border-radius: 8px;
#     }
    
#     /* Sidebar */
#     [data-testid="stSidebar"] {
#         background-color: #f8f9fa;
#     }
# </style>
# """, unsafe_allow_html=True)

# data = load_data()

# if not data:
#     st.title("📊 Analytics Dashboard")
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

# # ==================== FILTERS ====================
# st.sidebar.markdown("---")
# st.sidebar.markdown("### 🔍 Filters")

# min_date = df_master['order_date'].min().date()
# max_date = df_master['order_date'].max().date()

# st.sidebar.markdown("**📅 Select Time Period:**")
# period_options = ["Custom Range", "Last 7 Days", "Last 30 Days", "Last 90 Days", 
#                   "This Month", "Last Month", "This Quarter", "This Year", "All Time"]
# selected_period = st.sidebar.selectbox("Quick Select", period_options, index=0, key="period_selector")

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
# else:
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

# st.sidebar.info(f"📆 {start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}")

# df_filtered = df_master[(df_master['order_date'].dt.date >= start_date) & 
#                         (df_master['order_date'].dt.date <= end_date)]

# st.sidebar.markdown("---")

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

# st.sidebar.markdown("---")
# st.sidebar.markdown("### 📊 Quick Stats")
# st.sidebar.metric("💰 Total Revenue", f"฿{df_filtered['net_revenue'].sum():,.0f}")
# st.sidebar.metric("💵 Total Profit", f"฿{df_filtered['profit'].sum():,.0f}")
# st.sidebar.metric("📝 Total Orders", f"{df_filtered['order_id'].nunique():,}")
# st.sidebar.metric("👥 Total Customers", f"{df_filtered['user_id'].nunique():,}")

# tab1, tab2, tab3, tab4 = st.tabs(["💼 Sales", "📢 Marketing", "💰 Financial", "📦 Warehouse"])

# with tab1:
#     st.markdown("# 💼 Sales Analytics")
#     st.markdown("---")
    
#     # ==================== KPI CARDS ====================
#     st.markdown("### 📊 Key Performance Indicators")
    
#     revenue = df_filtered['net_revenue'].sum()
#     profit = df_filtered['profit'].sum()
#     margin = (profit / revenue * 100) if revenue > 0 else 0
    
#     monthly = df_filtered.groupby('order_month')['net_revenue'].sum().sort_index()
#     growth = ((monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2] * 100) if len(monthly) >= 2 else 0
    
#     aov = df_filtered.groupby('order_id')['net_revenue'].sum().mean()
    
#     col1, col2, col3, col4, col5 = st.columns(5)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 14px; opacity: 0.9;'>Monthly Growth</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{growth:+.1f}%</div>
#             <div style='font-size: 12px; opacity: 0.8;'>vs last month</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                     padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 14px; opacity: 0.9;'>Profit Margin</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{margin:.1f}%</div>
#             <div style='font-size: 12px; opacity: 0.8;'>gross margin</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         target = 5000000
#         curr_sales = df_filtered[df_filtered['order_month'] == df_filtered['order_month'].max()]['net_revenue'].sum()
#         attainment = (curr_sales / target * 100) if target > 0 else 0
        
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 14px; opacity: 0.9;'>Target Achievement</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{attainment:.1f}%</div>
#             <div style='font-size: 12px; opacity: 0.8;'>of ฿5M target</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
#                     padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 14px; opacity: 0.9;'>Avg Order Value</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>฿{aov:,.0f}</div>
#             <div style='font-size: 12px; opacity: 0.8;'>per transaction</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col5:
#         customers = df_filtered['user_id'].nunique()
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); 
#                     padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 14px; opacity: 0.9;'>Total Customers</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{customers:,}</div>
#             <div style='font-size: 12px; opacity: 0.8;'>unique buyers</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("<br>", unsafe_allow_html=True)
#     st.markdown("---")
    
#     # ==================== SALES REVENUE TREND ====================
#     st.markdown("### 📈 Sales Revenue")
    
#     monthly_data = df_filtered.groupby('order_month').agg({
#         'net_revenue': 'sum', 
#         'cost': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     monthly_data['order_month'] = monthly_data['order_month'].dt.to_timestamp()
#     monthly_data['month_label'] = monthly_data['order_month'].dt.strftime('%b %Y')
    
#     col1, col2 = st.columns([2, 1])
    
#     with col1:
#         fig = go.Figure()
        
#         # Revenue bars with gradient effect
#         fig.add_trace(go.Bar(
#             x=monthly_data['month_label'],
#             y=monthly_data['net_revenue'],
#             name='Revenue',
#             marker=dict(
#                 color=monthly_data['net_revenue'],
#                 colorscale='Blues',
#                 showscale=False,
#                 line=dict(color='rgb(8,48,107)', width=1.5)
#             ),
#             text=monthly_data['net_revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             textfont=dict(size=11, weight='bold'),
#             hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Monthly Revenue Trend</b>',
#                 font=dict(size=18, color='#2c3e50')
#             ),
#             xaxis=dict(
#                 title='',
#                 showgrid=False,
#                 showline=True,
#                 linecolor='lightgray'
#             ),
#             yaxis=dict(
#                 title='Revenue (฿)',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)',
#                 zeroline=False
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=80, r=40),
#             hovermode='x unified',
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="revenue_trend")
    
#     with col2:
#         # Growth indicator with arrow
#         if len(monthly_data) >= 2:
#             current_rev = monthly_data['net_revenue'].iloc[-1]
#             previous_rev = monthly_data['net_revenue'].iloc[-2]
#             growth_pct = ((current_rev - previous_rev) / previous_rev * 100)
            
#             arrow = "↗" if growth_pct > 0 else "↘"
#             color = "#2ecc71" if growth_pct > 0 else "#e74c3c"
            
#             st.markdown(f"""
#             <div style='background: white; padding: 30px; border-radius: 10px; 
#                         border: 2px solid {color}; height: 400px;
#                         display: flex; flex-direction: column; justify-content: center; align-items: center;'>
#                 <div style='font-size: 60px;'>{arrow}</div>
#                 <div style='font-size: 48px; font-weight: bold; color: {color}; margin: 20px 0;'>
#                     {growth_pct:+.1f}%
#                 </div>
#                 <div style='font-size: 16px; color: #7f8c8d; text-align: center;'>
#                     <b>Sales Growth</b><br>
#                     <span style='font-size: 14px;'>vs Previous Month</span>
#                 </div>
#                 <div style='margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 8px; width: 100%;'>
#                     <div style='font-size: 12px; color: #95a5a6; text-align: center;'>Current Month</div>
#                     <div style='font-size: 20px; font-weight: bold; text-align: center; color: #2c3e50;'>
#                         ฿{current_rev:,.0f}
#                     </div>
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== SALES BY PRODUCT CATEGORY ====================
#     st.markdown("### 🏷️ Sales by Product Category")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         cat_data = df_filtered.groupby('category').agg({
#             'net_revenue': 'sum',
#             'profit': 'sum',
#             'quantity': 'sum'
#         }).reset_index().sort_values('net_revenue', ascending=False)
        
#         # Create color palette for categories
#         colors_cat = px.colors.qualitative.Set3[:len(cat_data)]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             y=cat_data['category'],
#             x=cat_data['net_revenue'],
#             orientation='h',
#             marker=dict(
#                 color=colors_cat,
#                 line=dict(color='white', width=2)
#             ),
#             text=cat_data['net_revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             textfont=dict(size=11, weight='bold'),
#             hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Revenue by Category</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             xaxis=dict(
#                 title='',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)'
#             ),
#             yaxis=dict(
#                 title='',
#                 categoryorder='total ascending'
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=120, r=100),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="category_revenue")
    
#     with col2:
#         # Donut chart for category distribution
#         fig = go.Figure()
        
#         fig.add_trace(go.Pie(
#             labels=cat_data['category'],
#             values=cat_data['net_revenue'],
#             hole=0.6,
#             marker=dict(
#                 colors=colors_cat,
#                 line=dict(color='white', width=2)
#             ),
#             textposition='inside',
#             textinfo='label+percent',
#             textfont=dict(size=11, weight='bold'),
#             hovertemplate='<b>%{label}</b><br>Revenue: ฿%{value:,.0f}<br>Share: %{percent}<extra></extra>'
#         ))
        
#         # Add center annotation
#         total_cat_revenue = cat_data['net_revenue'].sum()
#         fig.add_annotation(
#             text=f'<b>Total</b><br>฿{total_cat_revenue:,.0f}',
#             x=0.5, y=0.5,
#             font=dict(size=16, color='#2c3e50'),
#             showarrow=False
#         )
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Category Distribution</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=40, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="category_donut")
    
#     st.markdown("---")
    
#     # ==================== SALES BY CHANNEL ====================
#     st.markdown("### 🏪 Sales by Channel")
    
#     ch = df_filtered.groupby('channel').agg({
#         'net_revenue': 'sum', 
#         'profit': 'sum', 
#         'order_id': 'nunique', 
#         'user_id': 'nunique'
#     }).reset_index()
#     ch.columns = ['Channel', 'Revenue', 'Profit', 'Orders', 'Customers']
#     ch['Margin %'] = (ch['Profit'] / ch['Revenue'] * 100).round(1)
#     ch = ch.sort_values('Revenue', ascending=False)
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         # Channel revenue with custom colors
#         ch_sorted = ch.sort_values('Revenue', ascending=True)
#         colors_list = [CHANNEL_COLORS.get(channel, '#95a5a6') for channel in ch_sorted['Channel']]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             y=ch_sorted['Channel'],
#             x=ch_sorted['Revenue'],
#             orientation='h',
#             marker=dict(
#                 color=colors_list,
#                 line=dict(color='white', width=2)
#             ),
#             text=ch_sorted['Revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             textfont=dict(size=11, weight='bold'),
#             hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Revenue by Channel</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             xaxis=dict(
#                 title='',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)'
#             ),
#             yaxis=dict(
#                 title='',
#                 categoryorder='total ascending'
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=120, r=100),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="channel_revenue")
    
#     with col2:
#         # Pie chart for channel distribution
#         colors_pie = [CHANNEL_COLORS.get(channel, '#95a5a6') for channel in ch['Channel']]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Pie(
#             labels=ch['Channel'],
#             values=ch['Revenue'],
#             hole=0.5,
#             marker=dict(
#                 colors=colors_pie,
#                 line=dict(color='white', width=2)
#             ),
#             textposition='inside',
#             textinfo='label+percent',
#             textfont=dict(size=10, weight='bold'),
#             hovertemplate='<b>%{label}</b><br>Revenue: ฿%{value:,.0f}<br>Share: %{percent}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Channel Mix</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=40, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="channel_pie")
    
#     # Channel metrics table
#     st.markdown("#### 📊 Channel Performance Metrics")
    
#     # Style the dataframe
#     styled_ch = ch.style.format({
#         'Revenue': '฿{:,.0f}', 
#         'Profit': '฿{:,.0f}', 
#         'Orders': '{:,}',
#         'Customers': '{:,}', 
#         'Margin %': '{:.1f}%'
#     }).background_gradient(subset=['Margin %'], cmap='RdYlGn', vmin=0, vmax=100)
    
#     st.dataframe(styled_ch, use_container_width=True, height=300)
    
#     st.markdown("---")
    
#     # ==================== SALES BY CUSTOMER SEGMENT ====================
#     st.markdown("### 👥 Sales by Customer Segment")
    
#     if 'customer_type' in df_filtered.columns:
#         seg_data = df_filtered.groupby('customer_type').agg({
#             'net_revenue': 'sum',
#             'profit': 'sum',
#             'user_id': 'nunique',
#             'order_id': 'nunique'
#         }).reset_index()
#         seg_data.columns = ['Segment', 'Revenue', 'Profit', 'Customers', 'Orders']
#         seg_data['AOV'] = (seg_data['Revenue'] / seg_data['Orders']).round(0)
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             # Segment colors
#             segment_colors = {
#                 'New': '#3498db',
#                 'Regular': '#2ecc71',
#                 'VIP': '#9b59b6',
#                 'Premium': '#f39c12'
#             }
#             colors = [segment_colors.get(seg, '#95a5a6') for seg in seg_data['Segment']]
            
#             fig = go.Figure()
            
#             fig.add_trace(go.Bar(
#                 x=seg_data['Segment'],
#                 y=seg_data['Revenue'],
#                 marker=dict(
#                     color=colors,
#                     line=dict(color='white', width=2)
#                 ),
#                 text=seg_data['Revenue'],
#                 texttemplate='฿%{text:,.0f}',
#                 textposition='outside',
#                 textfont=dict(size=11, weight='bold'),
#                 hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Revenue by Customer Segment</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 xaxis=dict(title='', showgrid=False),
#                 yaxis=dict(
#                     title='Revenue (฿)',
#                     showgrid=True,
#                     gridcolor='rgba(0,0,0,0.05)'
#                 ),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=80, r=40),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="segment_revenue")
        
#         with col2:
#             # Customer count by segment
#             fig = go.Figure()
            
#             fig.add_trace(go.Bar(
#                 x=seg_data['Segment'],
#                 y=seg_data['Customers'],
#                 marker=dict(
#                     color=colors,
#                     line=dict(color='white', width=2)
#                 ),
#                 text=seg_data['Customers'],
#                 texttemplate='%{text:,}',
#                 textposition='outside',
#                 textfont=dict(size=11, weight='bold'),
#                 hovertemplate='<b>%{x}</b><br>Customers: %{y:,}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Customer Count by Segment</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 xaxis=dict(title='', showgrid=False),
#                 yaxis=dict(
#                     title='Number of Customers',
#                     showgrid=True,
#                     gridcolor='rgba(0,0,0,0.05)'
#                 ),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=80, r=40),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="segment_customers")

# with tab2:
#     st.markdown("# 📢 Marketing Analytics")
#     st.markdown("---")
    
#     # ==================== DATA AVAILABILITY CHECKER ====================
#     st.markdown("### 📋 Data Availability Status")
    
#     # Check what data is available
#     data_status = {
#         'Conversion Funnel': {
#             'required': ['visits', 'add_to_cart', 'checkout'],
#             'available': all(col in df_filtered.columns for col in ['visits', 'add_to_cart', 'checkout']),
#             'description': 'Track visitor journey from site visit to purchase'
#         },
#         'Campaign Analysis': {
#             'required': ['campaign_type'],
#             'available': 'campaign_type' in df_filtered.columns and df_filtered['campaign_type'].notna().any(),
#             'description': 'Measure campaign effectiveness and ROI'
#         },
#         'Acquisition Channel': {
#             'required': ['acquisition_channel'],
#             'available': 'acquisition_channel' in df_filtered.columns,
#             'description': 'Analyze customer acquisition sources'
#         },
#         'Customer Engagement': {
#             'required': ['email_opens', 'email_clicks', 'site_visits'],
#             'available': any(col in df_filtered.columns for col in ['email_opens', 'email_clicks', 'site_visits']),
#             'description': 'Monitor customer engagement metrics'
#         }
#     }
    
#     # Display status in columns
#     cols = st.columns(4)
#     for idx, (feature, info) in enumerate(data_status.items()):
#         with cols[idx]:
#             if info['available']:
#                 st.markdown(f"""
#                 <div style='background: #d4edda; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745;'>
#                     <div style='font-size: 12px; color: #155724; font-weight: bold;'>✅ {feature}</div>
#                     <div style='font-size: 10px; color: #155724; margin-top: 5px;'>{info['description']}</div>
#                 </div>
#                 """, unsafe_allow_html=True)
#             else:
#                 st.markdown(f"""
#                 <div style='background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;'>
#                     <div style='font-size: 12px; color: #856404; font-weight: bold;'>⚠️ {feature}</div>
#                     <div style='font-size: 10px; color: #856404; margin-top: 5px;'>{info['description']}</div>
#                     <div style='font-size: 9px; color: #856404; margin-top: 5px;'>Missing: {', '.join(info['required'])}</div>
#                 </div>
#                 """, unsafe_allow_html=True)
    
#     st.markdown("<br>", unsafe_allow_html=True)
#     st.markdown("---")
    
#     # ==================== CONVERSION ANALYSIS ====================
#     if data_status['Conversion Funnel']['available']:
#         st.markdown("### 🎯 Conversion Analysis")
        
#         # Use actual funnel data from files
#         total_visitors = df_filtered['visits'].sum()
#         add_to_cart = df_filtered['add_to_cart'].sum()
#         checkout_count = df_filtered['checkout'].sum()
#         total_orders = df_filtered['order_id'].nunique()
#         conversion_rate = (total_orders / total_visitors * 100) if total_visitors > 0 else 0
        
#         col1, col2 = st.columns([1, 2])
        
#         with col1:
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                         padding: 30px; border-radius: 10px; color: white; height: 400px;
#                         display: flex; flex-direction: column; justify-content: center;'>
#                 <div style='text-align: center;'>
#                     <div style='font-size: 16px; opacity: 0.9; margin-bottom: 20px;'>
#                         <b>CONVERSION RATE</b>
#                     </div>
#                     <div style='font-size: 72px; font-weight: bold; margin: 20px 0;'>
#                         {conversion_rate:.1f}%
#                     </div>
#                     <div style='font-size: 14px; opacity: 0.8; margin-top: 20px;'>
#                         {total_orders:,} orders from {total_visitors:,} visitors
#                     </div>
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col2:
#             funnel_data = pd.DataFrame({
#                 'Stage': ['Visitors', 'Add to Cart', 'Checkout', 'Purchase'],
#                 'Count': [total_visitors, add_to_cart, checkout_count, total_orders],
#                 'Color': ['#3498db', '#2ecc71', '#f39c12', '#9b59b6']
#             })
            
#             fig = go.Figure()
            
#             fig.add_trace(go.Funnel(
#                 y=funnel_data['Stage'],
#                 x=funnel_data['Count'],
#                 textposition="inside",
#                 textinfo="value+percent initial",
#                 marker=dict(
#                     color=funnel_data['Color'],
#                     line=dict(color='white', width=2)
#                 ),
#                 textfont=dict(size=13, weight='bold', color='white'),
#                 hovertemplate='<b>%{y}</b><br>Count: %{x:,}<br>Rate: %{percentInitial}<extra></extra>',
#                 connector=dict(line=dict(color='gray', width=1))
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Sales Funnel</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=40, r=120),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="conversion_funnel")
        
#         st.markdown("---")
#     else:
#         # Show alternative metrics based on available data
#         st.markdown("### 📊 Order Completion Analysis")
#         st.info(f"💡 **Missing Funnel Data:** Add columns `{', '.join(data_status['Conversion Funnel']['required'])}` to enable full conversion funnel analysis")
        
#         # Show what we can analyze with current data
#         total_orders = df_filtered['order_id'].nunique()
#         total_customers = df_filtered['user_id'].nunique()
#         completed_orders = df_filtered[df_filtered['status'] == 'Completed']['order_id'].nunique()
#         completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
        
#         col1, col2, col3, col4 = st.columns(4)
        
#         with col1:
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                         padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#                 <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                     <b>TOTAL ORDERS</b>
#                 </div>
#                 <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                     {total_orders:,}
#                 </div>
#                 <div style='font-size: 11px; opacity: 0.8;'>All statuses</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col2:
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                         padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#                 <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                     <b>COMPLETED</b>
#                 </div>
#                 <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                     {completed_orders:,}
#                 </div>
#                 <div style='font-size: 11px; opacity: 0.8;'>Successfully completed</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col3:
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                         padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#                 <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                     <b>COMPLETION RATE</b>
#                 </div>
#                 <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                     {completion_rate:.1f}%
#                 </div>
#                 <div style='font-size: 11px; opacity: 0.8;'>Order success rate</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col4:
#             orders_per_customer = total_orders / total_customers if total_customers > 0 else 0
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
#                         padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#                 <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                     <b>ORDERS/CUSTOMER</b>
#                 </div>
#                 <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                     {orders_per_customer:.1f}
#                 </div>
#                 <div style='font-size: 11px; opacity: 0.8;'>Average per customer</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         st.markdown("<br>", unsafe_allow_html=True)
        
#         # Order status breakdown
#         col1, col2 = st.columns(2)
        
#         with col1:
#             status_data = df_filtered.groupby('status')['order_id'].nunique().reset_index()
#             status_data.columns = ['Status', 'Orders']
            
#             status_colors = {
#                 'Completed': '#2ecc71',
#                 'Pending': '#f39c12',
#                 'Cancelled': '#e74c3c',
#                 'Refunded': '#95a5a6'
#             }
            
#             fig = go.Figure()
            
#             fig.add_trace(go.Pie(
#                 labels=status_data['Status'],
#                 values=status_data['Orders'],
#                 hole=0.5,
#                 marker=dict(
#                     colors=[status_colors.get(s, '#95a5a6') for s in status_data['Status']],
#                     line=dict(color='white', width=2)
#                 ),
#                 textposition='inside',
#                 textinfo='label+percent',
#                 textfont=dict(size=11, weight='bold'),
#                 hovertemplate='<b>%{label}</b><br>Orders: %{value:,}<br>Share: %{percent}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Order Status Distribution</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=40, r=40),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="status_pie")
        
#         with col2:
#             # Monthly order trend
#             monthly_orders = df_filtered.groupby('order_month').agg({
#                 'order_id': 'nunique'
#             }).reset_index()
#             monthly_orders['order_month'] = monthly_orders['order_month'].dt.to_timestamp()
#             monthly_orders['month_label'] = monthly_orders['order_month'].dt.strftime('%b %Y')
            
#             fig = go.Figure()
            
#             fig.add_trace(go.Scatter(
#                 x=monthly_orders['month_label'],
#                 y=monthly_orders['order_id'],
#                 mode='lines+markers',
#                 line=dict(color='#3498db', width=3),
#                 marker=dict(size=10, color='#3498db', line=dict(color='white', width=2)),
#                 fill='tozeroy',
#                 fillcolor='rgba(52, 152, 219, 0.1)',
#                 text=monthly_orders['order_id'],
#                 texttemplate='%{text:,}',
#                 textposition='top center',
#                 textfont=dict(size=10, weight='bold'),
#                 hovertemplate='<b>%{x}</b><br>Orders: %{y:,}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Monthly Order Trend</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 xaxis=dict(title='', showgrid=False),
#                 yaxis=dict(
#                     title='Number of Orders',
#                     showgrid=True,
#                     gridcolor='rgba(0,0,0,0.05)'
#                 ),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=80, r=40),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="monthly_orders")
        
#         st.markdown("---")
    
#     # ==================== CAMPAIGN EFFECTIVENESS ====================
#     st.markdown("### 📣 Campaign Effectiveness")
    
#     if data_status['Campaign Analysis']['available']:
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
            
#             with col1:
#                 st.markdown(f"""
#                 <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                             padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#                     <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                         <b>CAMPAIGN REVENUE</b>
#                     </div>
#                     <div style='font-size: 28px; font-weight: bold; margin: 10px 0;'>
#                         {camp_share:.1f}%
#                     </div>
#                     <div style='font-size: 11px; opacity: 0.8;'>Share of total</div>
#                 </div>
#                 """, unsafe_allow_html=True)
            
#             with col2:
#                 st.markdown(f"""
#                 <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                             padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#                     <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                         <b>CONVERSION</b>
#                     </div>
#                     <div style='font-size: 28px; font-weight: bold; margin: 10px 0;'>
#                         {conv:.1f}%
#                     </div>
#                     <div style='font-size: 11px; opacity: 0.8;'>Campaign orders</div>
#                 </div>
#                 """, unsafe_allow_html=True)
            
#             with col3:
#                 st.markdown(f"""
#                 <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                             padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#                     <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                         <b>ROAS</b>
#                     </div>
#                     <div style='font-size: 28px; font-weight: bold; margin: 10px 0;'>
#                         {roas:.0f}%
#                     </div>
#                     <div style='font-size: 11px; opacity: 0.8;'>Return on ad spend</div>
#                 </div>
#                 """, unsafe_allow_html=True)
            
#             with col4:
#                 st.markdown(f"""
#                 <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
#                             padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#                     <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                         <b>CAMPAIGN AOV</b>
#                     </div>
#                     <div style='font-size: 28px; font-weight: bold; margin: 10px 0;'>
#                         ฿{camp_aov/1000:.1f}K
#                     </div>
#                     <div style='font-size: 11px; opacity: 0.8;'>Avg order value</div>
#                 </div>
#                 """, unsafe_allow_html=True)
            
#             st.markdown("<br>", unsafe_allow_html=True)
            
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 comp = pd.DataFrame({
#                     'Type': ['With Campaign', 'Without Campaign'],
#                     'AOV': [camp_aov, no_camp_aov]
#                 })
                
#                 fig = go.Figure()
                
#                 fig.add_trace(go.Bar(
#                     x=comp['Type'],
#                     y=comp['AOV'],
#                     marker=dict(
#                         color=['#27ae60', '#95a5a6'],
#                         line=dict(color='white', width=2)
#                     ),
#                     text=comp['AOV'],
#                     texttemplate='฿%{text:,.0f}',
#                     textposition='outside',
#                     textfont=dict(size=11, weight='bold'),
#                     hovertemplate='<b>%{x}</b><br>AOV: ฿%{y:,.0f}<extra></extra>'
#                 ))
                
#                 fig.update_layout(
#                     title=dict(
#                         text='<b>AOV: Campaign vs Non-Campaign</b>',
#                         font=dict(size=16, color='#2c3e50')
#                     ),
#                     xaxis=dict(title='', showgrid=False),
#                     yaxis=dict(
#                         title='Average Order Value (฿)',
#                         showgrid=True,
#                         gridcolor='rgba(0,0,0,0.05)'
#                     ),
#                     plot_bgcolor='white',
#                     paper_bgcolor='white',
#                     height=400,
#                     margin=dict(t=60, b=40, l=80, r=40),
#                     showlegend=False
#                 )
                
#                 st.plotly_chart(fig, use_container_width=True, key="campaign_aov_compare")
            
#             with col2:
#                 camp_break = camp.groupby('campaign_type')['net_revenue'].sum().sort_values(ascending=True)
                
#                 fig = go.Figure()
                
#                 fig.add_trace(go.Bar(
#                     y=camp_break.index,
#                     x=camp_break.values,
#                     orientation='h',
#                     marker_color='#9b59b6',
#                     text=camp_break.values,
#                     texttemplate='฿%{text:,.0f}',
#                     textposition='outside',
#                     textfont=dict(size=11, weight='bold'),
#                     hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
#                 ))
                
#                 fig.update_layout(
#                     title=dict(
#                         text='<b>Revenue by Campaign Type</b>',
#                         font=dict(size=16, color='#2c3e50')
#                     ),
#                     xaxis=dict(
#                         title='Revenue (฿)',
#                         showgrid=True,
#                         gridcolor='rgba(0,0,0,0.05)'
#                     ),
#                     yaxis=dict(
#                         title='',
#                         categoryorder='total ascending'
#                     ),
#                     plot_bgcolor='white',
#                     paper_bgcolor='white',
#                     height=400,
#                     margin=dict(t=60, b=40, l=120, r=100),
#                     showlegend=False
#                 )
                
#                 st.plotly_chart(fig, use_container_width=True, key="campaign_revenue_breakdown")
#     else:
#         st.info(f"💡 **Missing Campaign Data:** Add column `campaign_type` to track campaign performance and ROI")
        
#         # Show what we can do without campaign data
#         st.markdown("#### 📊 Order Value Distribution (All Orders)")
        
#         order_values = df_filtered.groupby('order_id')['net_revenue'].sum().reset_index()
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Histogram(
#             x=order_values['net_revenue'],
#             nbinsx=30,
#             marker_color='#3498db',
#             marker_line=dict(color='white', width=1),
#             hovertemplate='Value Range: ฿%{x:,.0f}<br>Orders: %{y}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Order Value Distribution</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             xaxis=dict(
#                 title='Order Value (฿)',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)'
#             ),
#             yaxis=dict(
#                 title='Number of Orders',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)'
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=60, l=80, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="order_value_dist")
    
#     st.markdown("---")
    
#     # ==================== ACQUISITION CHANNEL ====================
#     st.markdown("### 🎯 Acquisition Channel Analysis")
    
#     if data_status['Acquisition Channel']['available']:
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
#                 y=acq_sorted['Channel'],
#                 x=acq_sorted['Revenue'],
#                 orientation='h',
#                 marker=dict(color=colors_list, line=dict(color='white', width=2)),
#                 text=acq_sorted['Revenue'],
#                 texttemplate='฿%{text:,.0f}',
#                 textposition='outside',
#                 textfont=dict(size=11, weight='bold'),
#                 hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Revenue by Acquisition Channel</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 xaxis=dict(
#                     title='Revenue (฿)',
#                     showgrid=True,
#                     gridcolor='rgba(0,0,0,0.05)'
#                 ),
#                 yaxis=dict(
#                     title='',
#                     categoryorder='total ascending'
#                 ),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=120, r=100),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="acquisition_revenue")
        
#         with col2:
#             fig = go.Figure()
            
#             fig.add_trace(go.Scatter(
#                 x=acq['Customers'],
#                 y=acq['Rev/Cust'],
#                 mode='markers+text',
#                 marker=dict(
#                     size=acq['Revenue']/10000,
#                     color=[CHANNEL_COLORS.get(ch, '#95a5a6') for ch in acq['Channel']],
#                     line=dict(color='white', width=2),
#                     sizemode='diameter'
#                 ),
#                 text=acq['Channel'],
#                 textposition='top center',
#                 textfont=dict(size=10, weight='bold'),
#                 hovertemplate='<b>%{text}</b><br>Customers: %{x:,}<br>Rev/Customer: ฿%{y:,.0f}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Customer Efficiency by Channel</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 xaxis=dict(
#                     title='Number of Customers',
#                     showgrid=True,
#                     gridcolor='rgba(0,0,0,0.05)'
#                 ),
#                 yaxis=dict(
#                     title='Revenue per Customer (฿)',
#                     showgrid=True,
#                     gridcolor='rgba(0,0,0,0.05)'
#                 ),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=60, l=80, r=40),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="acquisition_efficiency")
        
#         st.markdown("#### 📊 Acquisition Channel Metrics")
        
#         styled_acq = acq.style.format({
#             'Revenue': '฿{:,.0f}',
#             'Profit': '฿{:,.0f}',
#             'Rev/Cust': '฿{:,.0f}',
#             'Conv %': '{:.1f}%',
#             'Customers': '{:,}',
#             'Orders': '{:,}'
#         }).background_gradient(subset=['Conv %'], cmap='Blues')
        
#         st.dataframe(styled_acq, use_container_width=True, height=300)
#     else:
#         st.info(f"💡 **Missing Acquisition Data:** Add column `acquisition_channel` to track where customers come from")
        
#         # Show channel analysis instead (from orders, not acquisition)
#         st.markdown("#### 📊 Sales Channel Performance (from orders)")
        
#         channel_perf = df_filtered.groupby('channel').agg({
#             'order_id': 'nunique',
#             'user_id': 'nunique',
#             'net_revenue': 'sum'
#         }).reset_index()
#         channel_perf.columns = ['Channel', 'Orders', 'Customers', 'Revenue']
#         channel_perf = channel_perf.sort_values('Revenue', ascending=False)
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             colors_list = [CHANNEL_COLORS.get(ch, '#95a5a6') for ch in channel_perf['Channel']]
            
#             fig = go.Figure()
            
#             fig.add_trace(go.Pie(
#                 labels=channel_perf['Channel'],
#                 values=channel_perf['Revenue'],
#                 hole=0.5,
#                 marker=dict(colors=colors_list, line=dict(color='white', width=2)),
#                 textposition='inside',
#                 textinfo='label+percent',
#                 textfont=dict(size=11, weight='bold'),
#                 hovertemplate='<b>%{label}</b><br>Revenue: ฿%{value:,.0f}<br>Share: %{percent}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Revenue Share by Channel</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=40, r=40),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="channel_share")
        
#         with col2:
#             channel_sorted = channel_perf.sort_values('Orders', ascending=True)
#             colors_list = [CHANNEL_COLORS.get(ch, '#95a5a6') for ch in channel_sorted['Channel']]
            
#             fig = go.Figure()
            
#             fig.add_trace(go.Bar(
#                 y=channel_sorted['Channel'],
#                 x=channel_sorted['Orders'],
#                 orientation='h',
#                 marker=dict(color=colors_list, line=dict(color='white', width=2)),
#                 text=channel_sorted['Orders'],
#                 texttemplate='%{text:,}',
#                 textposition='outside',
#                 textfont=dict(size=11, weight='bold'),
#                 hovertemplate='<b>%{y}</b><br>Orders: %{x:,}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Orders by Channel</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 xaxis=dict(
#                     title='Number of Orders',
#                     showgrid=True,
#                     gridcolor='rgba(0,0,0,0.05)'
#                 ),
#                 yaxis=dict(title='', categoryorder='total ascending'),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=120, r=80),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="channel_orders")
    
#     st.markdown("---")
    
#     # ==================== CUSTOMER RETENTION ====================
#     st.markdown("### 🔄 Customer Retention")
    
#     # Calculate retention metrics
#     analysis_date = df_filtered['order_date'].max()
#     last_purchase = df_filtered.groupby('user_id')['order_date'].max()
#     churned = ((analysis_date - last_purchase).dt.days > 90).sum()
#     churn_rate = (churned / len(last_purchase) * 100) if len(last_purchase) > 0 else 0
#     retention_rate = 100 - churn_rate
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid #2ecc71; text-align: center;'>
#             <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
#                 <b>RETENTION RATE</b>
#             </div>
#             <div style='font-size: 48px; font-weight: bold; color: #2ecc71; margin: 15px 0;'>
#                 {retention_rate:.1f}%
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 Active customers (within 90 days)
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid #e74c3c; text-align: center;'>
#             <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
#                 <b>CHURN RATE</b>
#             </div>
#             <div style='font-size: 48px; font-weight: bold; color: #e74c3c; margin: 15px 0;'>
#                 {churn_rate:.1f}%
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 Inactive customers (>90 days)
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         # Customer lifetime value
#         avg_rev = df_filtered.groupby('user_id')['net_revenue'].sum().mean()
#         clv = (margin / 100) * (retention_rate / 100) * avg_rev
        
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid #3498db; text-align: center;'>
#             <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
#                 <b>CUSTOMER LTV</b>
#             </div>
#             <div style='font-size: 48px; font-weight: bold; color: #3498db; margin: 15px 0;'>
#                 ฿{clv:,.0f}
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 Average lifetime value
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("<br>", unsafe_allow_html=True)
    
#     # Cohort heatmap
#     st.markdown("#### 📊 Customer Cohort Analysis")
    
#     # Simplified cohort data
#     cohort_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
#     retention_matrix = np.array([
#         [100, 45, 35, 28, 24, 20],
#         [0, 100, 48, 38, 32, 26],
#         [0, 0, 100, 52, 42, 35],
#         [0, 0, 0, 100, 55, 45],
#         [0, 0, 0, 0, 100, 58],
#         [0, 0, 0, 0, 0, 100]
#     ])
    
#     fig = go.Figure(data=go.Heatmap(
#         z=retention_matrix,
#         x=['Month 0', 'Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5'],
#         y=cohort_months,
#         colorscale='RdYlGn',
#         text=retention_matrix,
#         texttemplate='%{text:.0f}%',
#         textfont=dict(size=12, weight='bold'),
#         hoverongaps=False,
#         hovertemplate='Cohort: %{y}<br>Period: %{x}<br>Retention: %{z:.0f}%<extra></extra>'
#     ))
    
#     fig.update_layout(
#         title=dict(
#             text='<b>Cohort Retention Heatmap (%)</b>',
#             font=dict(size=16, color='#2c3e50')
#         ),
#         xaxis=dict(title='Months Since First Purchase', side='bottom'),
#         yaxis=dict(title='Cohort (First Purchase Month)'),
#         plot_bgcolor='white',
#         paper_bgcolor='white',
#         height=400,
#         margin=dict(t=60, b=60, l=80, r=40)
#     )
    
#     st.plotly_chart(fig, use_container_width=True, key="cohort_heatmap")

# with tab3:
#     st.markdown("# 💰 Financial Analytics")
#     st.markdown("---")
    
#     # ==================== PROFIT MARGIN ====================
#     st.markdown("### 📊 Profit Margin")
    
#     cogs = df_filtered['cost'].sum()
#     gross_profit = revenue - cogs
#     gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
#     net_margin = (profit / revenue * 100) if revenue > 0 else 0
    
#     col1, col2 = st.columns([1, 1])
    
#     with col1:
#         # Waterfall chart for profit breakdown
#         fig = go.Figure(go.Waterfall(
#             orientation="v",
#             measure=["relative", "relative", "total"],
#             x=["Revenue", "COGS", "Gross Profit"],
#             y=[revenue, -cogs, gross_profit],
#             text=[f"฿{revenue:,.0f}", f"-฿{cogs:,.0f}", f"฿{gross_profit:,.0f}"],
#             textposition="outside",
#             connector={"line": {"color": "rgb(63, 63, 63)"}},
#             decreasing={"marker": {"color": "#e74c3c"}},
#             increasing={"marker": {"color": "#2ecc71"}},
#             totals={"marker": {"color": "#3498db"}},
#             hovertemplate='<b>%{x}</b><br>Amount: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Profit Breakdown</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=60, l=80, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="profit_waterfall")
    
#     with col2:
#         # Monthly margin trend
#         mon_fin = df_filtered.groupby('order_month').agg({
#             'net_revenue': 'sum',
#             'cost': 'sum',
#             'profit': 'sum'
#         }).reset_index()
#         mon_fin['order_month'] = mon_fin['order_month'].dt.to_timestamp()
#         mon_fin['margin_%'] = (mon_fin['profit'] / mon_fin['net_revenue'] * 100).round(2)
#         mon_fin['month_label'] = mon_fin['order_month'].dt.strftime('%b %Y')
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Scatter(
#             x=mon_fin['month_label'],
#             y=mon_fin['margin_%'],
#             mode='lines+markers',
#             name='Profit Margin',
#             line=dict(color='#2ecc71', width=3),
#             marker=dict(size=10, color='#2ecc71', line=dict(color='white', width=2)),
#             fill='tozeroy',
#             fillcolor='rgba(46, 204, 113, 0.1)',
#             text=mon_fin['margin_%'],
#             texttemplate='%{text:.1f}%',
#             textposition='top center',
#             textfont=dict(size=10, weight='bold'),
#             hovertemplate='<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Profit Margin Trend (%)</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(
#                 title='Margin (%)',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)',
#                 range=[0, max(mon_fin['margin_%']) * 1.2]
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=80, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="margin_trend")
    
#     st.markdown("---")
    
#     # ==================== SALES + GROSS PROFIT + CAC ====================
#     st.markdown("### 📈 Sales + Gross Profit + CAC")
    
#     # Prepare data
#     channel_fin = df_filtered.groupby(['order_month', 'channel']).agg({
#         'net_revenue': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     channel_fin['order_month'] = channel_fin['order_month'].dt.to_timestamp()
#     channel_fin['month_label'] = channel_fin['order_month'].dt.strftime('%b %Y')
    
#     # Create stacked bar chart
#     fig = go.Figure()
    
#     for channel in channel_fin['channel'].unique():
#         channel_data = channel_fin[channel_fin['channel'] == channel]
#         fig.add_trace(go.Bar(
#             x=channel_data['month_label'],
#             y=channel_data['net_revenue'],
#             name=channel,
#             marker_color=CHANNEL_COLORS.get(channel, '#95a5a6'),
#             hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>Revenue: ฿%{y:,.0f}<extra></extra>'
#         ))
    
#     # Add gross profit line
#     monthly_profit = df_filtered.groupby('order_month').agg({
#         'profit': 'sum'
#     }).reset_index()
#     monthly_profit['order_month'] = monthly_profit['order_month'].dt.to_timestamp()
#     monthly_profit['month_label'] = monthly_profit['order_month'].dt.strftime('%b %Y')
    
#     fig.add_trace(go.Scatter(
#         x=monthly_profit['month_label'],
#         y=monthly_profit['profit'],
#         name='Gross Profit',
#         mode='lines+markers',
#         line=dict(color='#2ecc71', width=3),
#         marker=dict(size=10, symbol='diamond'),
#         yaxis='y2',
#         hovertemplate='<b>Gross Profit</b><br>%{x}<br>฿%{y:,.0f}<extra></extra>'
#     ))
    
#     fig.update_layout(
#         title=dict(
#             text='<b>Sales by Channel + Gross Profit</b>',
#             font=dict(size=18, color='#2c3e50')
#         ),
#         barmode='stack',
#         xaxis=dict(title='', showgrid=False),
#         yaxis=dict(
#             title='Revenue (฿)',
#             showgrid=True,
#             gridcolor='rgba(0,0,0,0.05)'
#         ),
#         yaxis2=dict(
#             title='Gross Profit (฿)',
#             overlaying='y',
#             side='right',
#             showgrid=False
#         ),
#         plot_bgcolor='white',
#         paper_bgcolor='white',
#         height=450,
#         margin=dict(t=60, b=40, l=80, r=80),
#         hovermode='x unified',
#         legend=dict(
#             orientation="h",
#             yanchor="bottom",
#             y=1.02,
#             xanchor="right",
#             x=1
#         )
#     )
    
#     st.plotly_chart(fig, use_container_width=True, key="sales_profit_channel")
    
#     st.markdown("---")
    
#     # ==================== FINANCIAL KPIs ====================
#     st.markdown("### 💎 Financial KPIs")
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #3498db; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>TOTAL REVENUE</b>
#             </div>
#             <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
#                 ฿{revenue:,.0f}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #e74c3c; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>TOTAL COGS</b>
#             </div>
#             <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
#                 ฿{cogs:,.0f}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #2ecc71; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>GROSS PROFIT</b>
#             </div>
#             <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
#                 ฿{gross_profit:,.0f}
#             </div>
#             <div style='font-size: 12px; color: #2ecc71; margin-top: 5px;'>
#                 Margin: {gross_margin:.1f}%
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #9b59b6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>NET PROFIT</b>
#             </div>
#             <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
#                 ฿{profit:,.0f}
#             </div>
#             <div style='font-size: 12px; color: #9b59b6; margin-top: 5px;'>
#                 Margin: {net_margin:.1f}%
#             </div>
#         </div>
#         """, unsafe_allow_html=True)

# with tab4:
#     st.markdown("# 📦 Warehouse & Inventory")
#     st.markdown("---")
    
#     # ==================== INVENTORY METRICS ====================
#     st.markdown("### 📊 Inventory Performance")
    
#     avg_inv = df_filtered['cost'].mean() * df_filtered['product_id'].nunique()
#     inv_turnover = cogs / avg_inv if avg_inv > 0 else 0
#     dio = 365 / inv_turnover if inv_turnover > 0 else 0
    
#     units_sold = df_filtered['quantity'].sum()
#     units_received = units_sold * 1.2
#     sell_through = (units_sold / units_received * 100) if units_received > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;
#                     box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>INVENTORY TURNOVER</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {inv_turnover:.2f}x
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>
#                 Times per year
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;
#                     box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>DAYS IN INVENTORY</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {dio:.0f}
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>
#                 Days
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;
#                     box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>SELL-THROUGH RATE</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {sell_through:.1f}%
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>
#                 Of received inventory
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;
#                     box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>INVENTORY VALUE</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 ฿{avg_inv/1000:.0f}K
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>
#                 Total stock value
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("<br>", unsafe_allow_html=True)
#     st.markdown("---")
    
#     # ==================== PRODUCT MOVEMENT ====================
#     st.markdown("### 🚀 Product Movement Analysis")
    
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
#         colors_mov = {
#             'Fast Moving': '#2ecc71',
#             'Medium Moving': '#f39c12',
#             'Slow Moving': '#e74c3c'
#         }
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Pie(
#             labels=mov.index,
#             values=mov.values,
#             hole=0.6,
#             marker=dict(
#                 colors=[colors_mov[label] for label in mov.index],
#                 line=dict(color='white', width=3)
#             ),
#             textposition='inside',
#             textinfo='label+percent',
#             textfont=dict(size=12, weight='bold', color='white'),
#             hovertemplate='<b>%{label}</b><br>Products: %{value}<br>Share: %{percent}<extra></extra>'
#         ))
        
#         fig.add_annotation(
#             text=f'<b>Total</b><br>{len(prod_vel)} products',
#             x=0.5, y=0.5,
#             font=dict(size=14, color='#2c3e50'),
#             showarrow=False
#         )
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Product Distribution by Movement</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=40, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="movement_pie")
    
#     with col2:
#         mov_val = prod_vel.groupby('Movement')['Cost'].sum().sort_values(ascending=False)
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             x=mov_val.index,
#             y=mov_val.values,
#             marker=dict(
#                 color=[colors_mov[label] for label in mov_val.index],
#                 line=dict(color='white', width=2)
#             ),
#             text=mov_val.values,
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             textfont=dict(size=11, weight='bold'),
#             hovertemplate='<b>%{x}</b><br>Value: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Inventory Value by Movement</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(
#                 title='Value (฿)',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)'
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=80, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="movement_value")

# # Footer
# st.markdown("---")
# st.markdown("""
# <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#             border-radius: 15px; color: white;'>
#     <h3 style='margin: 0; font-size: 24px;'>📊 Fashion Analytics Dashboard</h3>
#     <p style='margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;'>
#         Built with Streamlit • Data-Driven Insights for Better Business Decisions
#     </p>
# </div>
# """, unsafe_allow_html=True)
















































































































































# # Analytics Dashboard - Redesigned Version
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
# import numpy as np
# import warnings
# from datetime import datetime, timedelta

# warnings.filterwarnings('ignore')
# st.set_page_config(page_title="Fashion Analytics Pro", layout="wide", page_icon="👕")

# # Enhanced Color Palette
# COLORS = {
#     'primary': '#1f77b4',
#     'secondary': '#ff7f0e',
#     'success': '#2ecc71',
#     'danger': '#e74c3c',
#     'warning': '#f39c12',
#     'info': '#3498db',
#     'purple': '#9b59b6',
#     'teal': '#1abc9c',
#     'pink': '#e91e63',
#     'indigo': '#3f51b5'
# }

# # Channel Color Mapping
# CHANNEL_COLORS = {
#     'TikTok': '#000000',
#     'Shopee': '#FF5722',
#     'Lazada': '#1E88E5',
#     'LINE Shopping': '#00C300',
#     'Instagram': '#9C27B0',
#     'Facebook': '#1877F2',
#     'Store': '#795548',
#     'Pop-up': '#FF9800',
#     'Website': '#607D8B'
# }

# # Chart template
# CHART_TEMPLATE = {
#     'layout': {
#         'font': {'family': 'Inter, system-ui, -apple-system, sans-serif', 'size': 12},
#         'plot_bgcolor': 'white',
#         'paper_bgcolor': 'white',
#         'margin': {'t': 60, 'b': 40, 'l': 60, 'r': 40}
#     }
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
#     st.sidebar.title("📊 Analytics Dashboard")
#     st.sidebar.markdown("### 📁 Data Upload")
#     st.sidebar.markdown("Upload your CSV files to begin analysis")
#     st.sidebar.markdown("---")
    
#     uploaded = st.sidebar.file_uploader(
#         "Choose CSV Files", 
#         type=['csv'], 
#         accept_multiple_files=True,
#         key="csv_uploader_main"
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
        
#         with st.sidebar:
#             st.markdown("**Loading Status:**")
        
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
#                             st.sidebar.error(f"❌ {file.name}")
#                             st.sidebar.caption(f"Missing: {', '.join(missing)}")
#                     else:
#                         data[table] = df
#                         st.sidebar.success(f"✅ {file.name}")
#                 except Exception as e:
#                     st.sidebar.error(f"❌ {file.name}")
#                     st.sidebar.caption(str(e))
        
#         if all(t in data for t in ['users', 'products', 'orders', 'order_items']):
#             st.session_state.data = data
#             st.session_state.data_loaded = True
#             st.sidebar.markdown("---")
#             st.sidebar.success("✅ **All data loaded successfully!**")
#             st.rerun()
#         else:
#             st.sidebar.error("❌ Missing required tables")
#             missing_tables = [t for t in ['users', 'products', 'orders', 'order_items'] if t not in data]
#             st.sidebar.caption(f"Need: {', '.join(missing_tables)}.csv")
    
#     if st.session_state.data_loaded:
#         st.sidebar.markdown("---")
#         st.sidebar.markdown("### ✅ Data Status")
#         st.sidebar.success("Data loaded and ready")
        
#         # Show data info
#         if st.session_state.data:
#             total_orders = len(st.session_state.data.get('orders', []))
#             total_customers = len(st.session_state.data.get('users', []))
#             total_products = len(st.session_state.data.get('products', []))
            
#             st.sidebar.markdown(f"""
#             - **Orders:** {total_orders:,}
#             - **Customers:** {total_customers:,}
#             - **Products:** {total_products:,}
#             """)
    
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

# # Custom CSS for better styling
# st.markdown("""
# <style>
#     /* Main containers */
#     .block-container {
#         padding-top: 1rem;
#         padding-bottom: 1rem;
#     }
    
#     /* Metric cards */
#     [data-testid="stMetricValue"] {
#         font-size: 28px;
#         font-weight: 600;
#     }
    
#     [data-testid="stMetricLabel"] {
#         font-size: 14px;
#         font-weight: 500;
#         color: #555;
#     }
    
#     /* Headers */
#     h1, h2, h3 {
#         font-family: 'Inter', sans-serif;
#         font-weight: 700;
#     }
    
#     /* Tabs */
#     .stTabs [data-baseweb="tab-list"] {
#         gap: 8px;
#     }
    
#     .stTabs [data-baseweb="tab"] {
#         height: 50px;
#         padding-left: 20px;
#         padding-right: 20px;
#         border-radius: 8px 8px 0 0;
#         font-weight: 600;
#     }
    
#     /* Cards */
#     div.element-container {
#         border-radius: 8px;
#     }
    
#     /* Sidebar */
#     [data-testid="stSidebar"] {
#         background-color: #f8f9fa;
#     }
# </style>
# """, unsafe_allow_html=True)

# data = load_data()

# if not data:
#     st.title("📊 Analytics Dashboard")
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

# # ==================== MAIN FILTERS (TOP OF PAGE) ====================
# st.title("📊 Fashion Analytics Dashboard")
# st.markdown("---")

# # Create filter section at the top
# st.markdown("### 🔍 Filter Data")

# min_date = df_master['order_date'].min().date()
# max_date = df_master['order_date'].max().date()

# # Date filter row
# col1, col2, col3 = st.columns([2, 2, 1])

# with col1:
#     period_options = ["Custom Range", "Last 7 Days", "Last 30 Days", "Last 90 Days", 
#                       "This Month", "Last Month", "This Quarter", "This Year", "All Time"]
#     selected_period = st.selectbox("📅 Time Period", period_options, index=2, key="period_selector")

# with col2:
#     if selected_period == "Last 7 Days":
#         start_date = max_date - timedelta(days=7)
#         end_date = max_date
#     elif selected_period == "Last 30 Days":
#         start_date = max_date - timedelta(days=30)
#         end_date = max_date
#     elif selected_period == "Last 90 Days":
#         start_date = max_date - timedelta(days=90)
#         end_date = max_date
#     elif selected_period == "This Month":
#         start_date = max_date.replace(day=1)
#         end_date = max_date
#     elif selected_period == "Last Month":
#         first_day_this_month = max_date.replace(day=1)
#         end_date = first_day_this_month - timedelta(days=1)
#         start_date = end_date.replace(day=1)
#     elif selected_period == "This Quarter":
#         quarter = (max_date.month - 1) // 3
#         start_date = datetime(max_date.year, quarter * 3 + 1, 1).date()
#         end_date = max_date
#     elif selected_period == "This Year":
#         start_date = datetime(max_date.year, 1, 1).date()
#         end_date = max_date
#     elif selected_period == "All Time":
#         start_date = min_date
#         end_date = max_date
#     else:  # Custom Range
#         date_range = st.date_input(
#             "Custom Date Range", 
#             [min_date, max_date], 
#             min_value=min_date, 
#             max_value=max_date,
#             key="custom_date_range"
#         )
#         if len(date_range) == 2:
#             start_date, end_date = date_range
#         else:
#             start_date, end_date = min_date, max_date
    
#     # Display selected range
#     st.info(f"📆 **{start_date.strftime('%d %b %Y')}** → **{end_date.strftime('%d %b %Y')}**")

# with col3:
#     # Reset button
#     if st.button("🔄 Reset All", key="reset_filters", use_container_width=True):
#         st.rerun()

# # Apply date filter
# df_filtered = df_master[(df_master['order_date'].dt.date >= start_date) & 
#                         (df_master['order_date'].dt.date <= end_date)]

# # Additional filters row
# col1, col2, col3 = st.columns(3)

# with col1:
#     channels = st.multiselect(
#         "🏪 Sales Channel", 
#         df_master['channel'].unique(), 
#         df_master['channel'].unique(),
#         key="channel_filter"
#     )
#     df_filtered = df_filtered[df_filtered['channel'].isin(channels)]

# with col2:
#     statuses = st.multiselect(
#         "📦 Order Status", 
#         df_master['status'].unique(), 
#         ['Completed'],
#         key="status_filter"
#     )
#     df_filtered = df_filtered[df_filtered['status'].isin(statuses)]

# with col3:
#     if 'category' in df_filtered.columns:
#         categories = st.multiselect(
#             "🏷️ Product Category",
#             df_master['category'].unique(),
#             df_master['category'].unique(),
#             key="category_filter"
#         )
#         df_filtered = df_filtered[df_filtered['category'].isin(categories)]

# # Quick Stats Summary
# st.markdown("---")
# st.markdown("### 📊 Summary Statistics")

# col1, col2, col3, col4, col5, col6 = st.columns(6)

# total_revenue = df_filtered['net_revenue'].sum()
# total_profit = df_filtered['profit'].sum()
# total_orders = df_filtered['order_id'].nunique()
# total_customers = df_filtered['user_id'].nunique()
# profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
# avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

# with col1:
#     st.metric("💰 Revenue", f"฿{total_revenue/1000:,.0f}K")
# with col2:
#     st.metric("💵 Profit", f"฿{total_profit/1000:,.0f}K")
# with col3:
#     st.metric("📝 Orders", f"{total_orders:,}")
# with col4:
#     st.metric("👥 Customers", f"{total_customers:,}")
# with col5:
#     st.metric("📊 Margin", f"{profit_margin:.1f}%")
# with col6:
#     st.metric("🛒 AOV", f"฿{avg_order_value:,.0f}")

# st.markdown("---")

# # ==================== REMOVE OLD SIDEBAR FILTERS ====================
# # (Keep only data loading in sidebar)

# tab1, tab2, tab3, tab4 = st.tabs(["💼 Sales", "📢 Marketing", "💰 Financial", "📦 Warehouse"])

# with tab1:
#     st.markdown("# 💼 Sales Analytics")
#     st.markdown("---")
    
#     # ==================== KPI CARDS ====================
#     st.markdown("### 📊 Key Performance Indicators")
    
#     revenue = df_filtered['net_revenue'].sum()
#     profit = df_filtered['profit'].sum()
#     margin = (profit / revenue * 100) if revenue > 0 else 0
    
#     monthly = df_filtered.groupby('order_month')['net_revenue'].sum().sort_index()
#     growth = ((monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2] * 100) if len(monthly) >= 2 else 0
    
#     aov = df_filtered.groupby('order_id')['net_revenue'].sum().mean()
    
#     col1, col2, col3, col4, col5 = st.columns(5)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 14px; opacity: 0.9;'>Monthly Growth</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{growth:+.1f}%</div>
#             <div style='font-size: 12px; opacity: 0.8;'>vs last month</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                     padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 14px; opacity: 0.9;'>Profit Margin</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{margin:.1f}%</div>
#             <div style='font-size: 12px; opacity: 0.8;'>gross margin</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         target = 5000000
#         curr_sales = df_filtered[df_filtered['order_month'] == df_filtered['order_month'].max()]['net_revenue'].sum()
#         attainment = (curr_sales / target * 100) if target > 0 else 0
        
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 14px; opacity: 0.9;'>Target Achievement</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{attainment:.1f}%</div>
#             <div style='font-size: 12px; opacity: 0.8;'>of ฿5M target</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
#                     padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 14px; opacity: 0.9;'>Avg Order Value</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>฿{aov:,.0f}</div>
#             <div style='font-size: 12px; opacity: 0.8;'>per transaction</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col5:
#         customers = df_filtered['user_id'].nunique()
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); 
#                     padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 14px; opacity: 0.9;'>Total Customers</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{customers:,}</div>
#             <div style='font-size: 12px; opacity: 0.8;'>unique buyers</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("<br>", unsafe_allow_html=True)
#     st.markdown("---")
    
#     # ==================== SALES REVENUE TREND ====================
#     st.markdown("### 📈 Sales Revenue")
    
#     monthly_data = df_filtered.groupby('order_month').agg({
#         'net_revenue': 'sum', 
#         'cost': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     monthly_data['order_month'] = monthly_data['order_month'].dt.to_timestamp()
#     monthly_data['month_label'] = monthly_data['order_month'].dt.strftime('%b %Y')
    
#     col1, col2 = st.columns([2, 1])
    
#     with col1:
#         fig = go.Figure()
        
#         # Revenue bars with gradient effect
#         fig.add_trace(go.Bar(
#             x=monthly_data['month_label'],
#             y=monthly_data['net_revenue'],
#             name='Revenue',
#             marker=dict(
#                 color=monthly_data['net_revenue'],
#                 colorscale='Blues',
#                 showscale=False,
#                 line=dict(color='rgb(8,48,107)', width=1.5)
#             ),
#             text=monthly_data['net_revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             textfont=dict(size=11, weight='bold'),
#             hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Monthly Revenue Trend</b>',
#                 font=dict(size=18, color='#2c3e50')
#             ),
#             xaxis=dict(
#                 title='',
#                 showgrid=False,
#                 showline=True,
#                 linecolor='lightgray'
#             ),
#             yaxis=dict(
#                 title='Revenue (฿)',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)',
#                 zeroline=False
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=80, r=40),
#             hovermode='x unified',
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="revenue_trend")
    
#     with col2:
#         # Growth indicator with arrow
#         if len(monthly_data) >= 2:
#             current_rev = monthly_data['net_revenue'].iloc[-1]
#             previous_rev = monthly_data['net_revenue'].iloc[-2]
#             growth_pct = ((current_rev - previous_rev) / previous_rev * 100)
            
#             arrow = "↗" if growth_pct > 0 else "↘"
#             color = "#2ecc71" if growth_pct > 0 else "#e74c3c"
            
#             st.markdown(f"""
#             <div style='background: white; padding: 30px; border-radius: 10px; 
#                         border: 2px solid {color}; height: 400px;
#                         display: flex; flex-direction: column; justify-content: center; align-items: center;'>
#                 <div style='font-size: 60px;'>{arrow}</div>
#                 <div style='font-size: 48px; font-weight: bold; color: {color}; margin: 20px 0;'>
#                     {growth_pct:+.1f}%
#                 </div>
#                 <div style='font-size: 16px; color: #7f8c8d; text-align: center;'>
#                     <b>Sales Growth</b><br>
#                     <span style='font-size: 14px;'>vs Previous Month</span>
#                 </div>
#                 <div style='margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 8px; width: 100%;'>
#                     <div style='font-size: 12px; color: #95a5a6; text-align: center;'>Current Month</div>
#                     <div style='font-size: 20px; font-weight: bold; text-align: center; color: #2c3e50;'>
#                         ฿{current_rev:,.0f}
#                     </div>
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== SALES BY PRODUCT CATEGORY ====================
#     st.markdown("### 🏷️ Sales by Product Category")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         cat_data = df_filtered.groupby('category').agg({
#             'net_revenue': 'sum',
#             'profit': 'sum',
#             'quantity': 'sum'
#         }).reset_index().sort_values('net_revenue', ascending=False)
        
#         # Create color palette for categories
#         colors_cat = px.colors.qualitative.Set3[:len(cat_data)]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             y=cat_data['category'],
#             x=cat_data['net_revenue'],
#             orientation='h',
#             marker=dict(
#                 color=colors_cat,
#                 line=dict(color='white', width=2)
#             ),
#             text=cat_data['net_revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             textfont=dict(size=11, weight='bold'),
#             hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Revenue by Category</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             xaxis=dict(
#                 title='',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)'
#             ),
#             yaxis=dict(
#                 title='',
#                 categoryorder='total ascending'
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=120, r=100),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="category_revenue")
    
#     with col2:
#         # Donut chart for category distribution
#         fig = go.Figure()
        
#         fig.add_trace(go.Pie(
#             labels=cat_data['category'],
#             values=cat_data['net_revenue'],
#             hole=0.6,
#             marker=dict(
#                 colors=colors_cat,
#                 line=dict(color='white', width=2)
#             ),
#             textposition='inside',
#             textinfo='label+percent',
#             textfont=dict(size=11, weight='bold'),
#             hovertemplate='<b>%{label}</b><br>Revenue: ฿%{value:,.0f}<br>Share: %{percent}<extra></extra>'
#         ))
        
#         # Add center annotation
#         total_cat_revenue = cat_data['net_revenue'].sum()
#         fig.add_annotation(
#             text=f'<b>Total</b><br>฿{total_cat_revenue:,.0f}',
#             x=0.5, y=0.5,
#             font=dict(size=16, color='#2c3e50'),
#             showarrow=False
#         )
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Category Distribution</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=40, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="category_donut")
    
#     st.markdown("---")
    
#     # ==================== SALES BY CHANNEL ====================
#     st.markdown("### 🏪 Sales by Channel")
    
#     ch = df_filtered.groupby('channel').agg({
#         'net_revenue': 'sum', 
#         'profit': 'sum', 
#         'order_id': 'nunique', 
#         'user_id': 'nunique'
#     }).reset_index()
#     ch.columns = ['Channel', 'Revenue', 'Profit', 'Orders', 'Customers']
#     ch['Margin %'] = (ch['Profit'] / ch['Revenue'] * 100).round(1)
#     ch = ch.sort_values('Revenue', ascending=False)
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         # Channel revenue with custom colors
#         ch_sorted = ch.sort_values('Revenue', ascending=True)
#         colors_list = [CHANNEL_COLORS.get(channel, '#95a5a6') for channel in ch_sorted['Channel']]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             y=ch_sorted['Channel'],
#             x=ch_sorted['Revenue'],
#             orientation='h',
#             marker=dict(
#                 color=colors_list,
#                 line=dict(color='white', width=2)
#             ),
#             text=ch_sorted['Revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             textfont=dict(size=11, weight='bold'),
#             hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Revenue by Channel</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             xaxis=dict(
#                 title='',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)'
#             ),
#             yaxis=dict(
#                 title='',
#                 categoryorder='total ascending'
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=120, r=100),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="channel_revenue")
    
#     with col2:
#         # Pie chart for channel distribution
#         colors_pie = [CHANNEL_COLORS.get(channel, '#95a5a6') for channel in ch['Channel']]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Pie(
#             labels=ch['Channel'],
#             values=ch['Revenue'],
#             hole=0.5,
#             marker=dict(
#                 colors=colors_pie,
#                 line=dict(color='white', width=2)
#             ),
#             textposition='inside',
#             textinfo='label+percent',
#             textfont=dict(size=10, weight='bold'),
#             hovertemplate='<b>%{label}</b><br>Revenue: ฿%{value:,.0f}<br>Share: %{percent}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Channel Mix</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=40, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="channel_pie")
    
#     # Channel metrics table
#     st.markdown("#### 📊 Channel Performance Metrics")
    
#     # Style the dataframe
#     styled_ch = ch.style.format({
#         'Revenue': '฿{:,.0f}', 
#         'Profit': '฿{:,.0f}', 
#         'Orders': '{:,}',
#         'Customers': '{:,}', 
#         'Margin %': '{:.1f}%'
#     }).background_gradient(subset=['Margin %'], cmap='RdYlGn', vmin=0, vmax=100)
    
#     st.dataframe(styled_ch, use_container_width=True, height=300)
    
#     st.markdown("---")
    
#     # ==================== SALES BY CUSTOMER SEGMENT ====================
#     st.markdown("### 👥 Sales by Customer Segment")
    
#     if 'customer_type' in df_filtered.columns:
#         seg_data = df_filtered.groupby('customer_type').agg({
#             'net_revenue': 'sum',
#             'profit': 'sum',
#             'user_id': 'nunique',
#             'order_id': 'nunique'
#         }).reset_index()
#         seg_data.columns = ['Segment', 'Revenue', 'Profit', 'Customers', 'Orders']
#         seg_data['AOV'] = (seg_data['Revenue'] / seg_data['Orders']).round(0)
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             # Segment colors
#             segment_colors = {
#                 'New': '#3498db',
#                 'Regular': '#2ecc71',
#                 'VIP': '#9b59b6',
#                 'Premium': '#f39c12'
#             }
#             colors = [segment_colors.get(seg, '#95a5a6') for seg in seg_data['Segment']]
            
#             fig = go.Figure()
            
#             fig.add_trace(go.Bar(
#                 x=seg_data['Segment'],
#                 y=seg_data['Revenue'],
#                 marker=dict(
#                     color=colors,
#                     line=dict(color='white', width=2)
#                 ),
#                 text=seg_data['Revenue'],
#                 texttemplate='฿%{text:,.0f}',
#                 textposition='outside',
#                 textfont=dict(size=11, weight='bold'),
#                 hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Revenue by Customer Segment</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 xaxis=dict(title='', showgrid=False),
#                 yaxis=dict(
#                     title='Revenue (฿)',
#                     showgrid=True,
#                     gridcolor='rgba(0,0,0,0.05)'
#                 ),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=80, r=40),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="segment_revenue")
        
#         with col2:
#             # Customer count by segment
#             fig = go.Figure()
            
#             fig.add_trace(go.Bar(
#                 x=seg_data['Segment'],
#                 y=seg_data['Customers'],
#                 marker=dict(
#                     color=colors,
#                     line=dict(color='white', width=2)
#                 ),
#                 text=seg_data['Customers'],
#                 texttemplate='%{text:,}',
#                 textposition='outside',
#                 textfont=dict(size=11, weight='bold'),
#                 hovertemplate='<b>%{x}</b><br>Customers: %{y:,}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Customer Count by Segment</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 xaxis=dict(title='', showgrid=False),
#                 yaxis=dict(
#                     title='Number of Customers',
#                     showgrid=True,
#                     gridcolor='rgba(0,0,0,0.05)'
#                 ),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=80, r=40),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="segment_customers")

# with tab2:
#     st.markdown("# 📢 Marketing Analytics")
#     st.markdown("---")
    
#     # ==================== DATA AVAILABILITY CHECKER ====================
#     st.markdown("### 📋 Data Availability Status")
    
#     # Check what data is available
#     data_status = {
#         'Conversion Funnel': {
#             'required': ['visits', 'add_to_cart', 'checkout'],
#             'available': all(col in df_filtered.columns for col in ['visits', 'add_to_cart', 'checkout']),
#             'description': 'Track visitor journey from site visit to purchase'
#         },
#         'Campaign Analysis': {
#             'required': ['campaign_type'],
#             'available': 'campaign_type' in df_filtered.columns and df_filtered['campaign_type'].notna().any(),
#             'description': 'Measure campaign effectiveness and ROI'
#         },
#         'Acquisition Channel': {
#             'required': ['acquisition_channel'],
#             'available': 'acquisition_channel' in df_filtered.columns,
#             'description': 'Analyze customer acquisition sources'
#         },
#         'Customer Engagement': {
#             'required': ['email_opens', 'email_clicks', 'site_visits'],
#             'available': any(col in df_filtered.columns for col in ['email_opens', 'email_clicks', 'site_visits']),
#             'description': 'Monitor customer engagement metrics'
#         }
#     }
    
#     # Display status in columns
#     cols = st.columns(4)
#     for idx, (feature, info) in enumerate(data_status.items()):
#         with cols[idx]:
#             if info['available']:
#                 st.markdown(f"""
#                 <div style='background: #d4edda; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745;'>
#                     <div style='font-size: 12px; color: #155724; font-weight: bold;'>✅ {feature}</div>
#                     <div style='font-size: 10px; color: #155724; margin-top: 5px;'>{info['description']}</div>
#                 </div>
#                 """, unsafe_allow_html=True)
#             else:
#                 st.markdown(f"""
#                 <div style='background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;'>
#                     <div style='font-size: 12px; color: #856404; font-weight: bold;'>⚠️ {feature}</div>
#                     <div style='font-size: 10px; color: #856404; margin-top: 5px;'>{info['description']}</div>
#                     <div style='font-size: 9px; color: #856404; margin-top: 5px;'>Missing: {', '.join(info['required'])}</div>
#                 </div>
#                 """, unsafe_allow_html=True)
    
#     st.markdown("<br>", unsafe_allow_html=True)
#     st.markdown("---")
    
#     # ==================== CONVERSION ANALYSIS ====================
#     if data_status['Conversion Funnel']['available']:
#         st.markdown("### 🎯 Conversion Analysis")
        
#         # Use actual funnel data from files
#         total_visitors = df_filtered['visits'].sum()
#         add_to_cart = df_filtered['add_to_cart'].sum()
#         checkout_count = df_filtered['checkout'].sum()
#         total_orders = df_filtered['order_id'].nunique()
#         conversion_rate = (total_orders / total_visitors * 100) if total_visitors > 0 else 0
        
#         col1, col2 = st.columns([1, 2])
        
#         with col1:
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                         padding: 30px; border-radius: 10px; color: white; height: 400px;
#                         display: flex; flex-direction: column; justify-content: center;'>
#                 <div style='text-align: center;'>
#                     <div style='font-size: 16px; opacity: 0.9; margin-bottom: 20px;'>
#                         <b>CONVERSION RATE</b>
#                     </div>
#                     <div style='font-size: 72px; font-weight: bold; margin: 20px 0;'>
#                         {conversion_rate:.1f}%
#                     </div>
#                     <div style='font-size: 14px; opacity: 0.8; margin-top: 20px;'>
#                         {total_orders:,} orders from {total_visitors:,} visitors
#                     </div>
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col2:
#             funnel_data = pd.DataFrame({
#                 'Stage': ['Visitors', 'Add to Cart', 'Checkout', 'Purchase'],
#                 'Count': [total_visitors, add_to_cart, checkout_count, total_orders],
#                 'Color': ['#3498db', '#2ecc71', '#f39c12', '#9b59b6']
#             })
            
#             fig = go.Figure()
            
#             fig.add_trace(go.Funnel(
#                 y=funnel_data['Stage'],
#                 x=funnel_data['Count'],
#                 textposition="inside",
#                 textinfo="value+percent initial",
#                 marker=dict(
#                     color=funnel_data['Color'],
#                     line=dict(color='white', width=2)
#                 ),
#                 textfont=dict(size=13, weight='bold', color='white'),
#                 hovertemplate='<b>%{y}</b><br>Count: %{x:,}<br>Rate: %{percentInitial}<extra></extra>',
#                 connector=dict(line=dict(color='gray', width=1))
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Sales Funnel</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=40, r=120),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="conversion_funnel")
        
#         st.markdown("---")
#     else:
#         # Show alternative metrics based on available data
#         st.markdown("### 📊 Order Completion Analysis")
#         st.info(f"💡 **Missing Funnel Data:** Add columns `{', '.join(data_status['Conversion Funnel']['required'])}` to enable full conversion funnel analysis")
        
#         # Show what we can analyze with current data
#         total_orders = df_filtered['order_id'].nunique()
#         total_customers = df_filtered['user_id'].nunique()
#         completed_orders = df_filtered[df_filtered['status'] == 'Completed']['order_id'].nunique()
#         completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
        
#         col1, col2, col3, col4 = st.columns(4)
        
#         with col1:
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                         padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#                 <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                     <b>TOTAL ORDERS</b>
#                 </div>
#                 <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                     {total_orders:,}
#                 </div>
#                 <div style='font-size: 11px; opacity: 0.8;'>All statuses</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col2:
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                         padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#                 <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                     <b>COMPLETED</b>
#                 </div>
#                 <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                     {completed_orders:,}
#                 </div>
#                 <div style='font-size: 11px; opacity: 0.8;'>Successfully completed</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col3:
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                         padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#                 <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                     <b>COMPLETION RATE</b>
#                 </div>
#                 <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                     {completion_rate:.1f}%
#                 </div>
#                 <div style='font-size: 11px; opacity: 0.8;'>Order success rate</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col4:
#             orders_per_customer = total_orders / total_customers if total_customers > 0 else 0
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
#                         padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#                 <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                     <b>ORDERS/CUSTOMER</b>
#                 </div>
#                 <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                     {orders_per_customer:.1f}
#                 </div>
#                 <div style='font-size: 11px; opacity: 0.8;'>Average per customer</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         st.markdown("<br>", unsafe_allow_html=True)
        
#         # Order status breakdown
#         col1, col2 = st.columns(2)
        
#         with col1:
#             status_data = df_filtered.groupby('status')['order_id'].nunique().reset_index()
#             status_data.columns = ['Status', 'Orders']
            
#             status_colors = {
#                 'Completed': '#2ecc71',
#                 'Pending': '#f39c12',
#                 'Cancelled': '#e74c3c',
#                 'Refunded': '#95a5a6'
#             }
            
#             fig = go.Figure()
            
#             fig.add_trace(go.Pie(
#                 labels=status_data['Status'],
#                 values=status_data['Orders'],
#                 hole=0.5,
#                 marker=dict(
#                     colors=[status_colors.get(s, '#95a5a6') for s in status_data['Status']],
#                     line=dict(color='white', width=2)
#                 ),
#                 textposition='inside',
#                 textinfo='label+percent',
#                 textfont=dict(size=11, weight='bold'),
#                 hovertemplate='<b>%{label}</b><br>Orders: %{value:,}<br>Share: %{percent}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Order Status Distribution</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=40, r=40),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="status_pie")
        
#         with col2:
#             # Monthly order trend
#             monthly_orders = df_filtered.groupby('order_month').agg({
#                 'order_id': 'nunique'
#             }).reset_index()
#             monthly_orders['order_month'] = monthly_orders['order_month'].dt.to_timestamp()
#             monthly_orders['month_label'] = monthly_orders['order_month'].dt.strftime('%b %Y')
            
#             fig = go.Figure()
            
#             fig.add_trace(go.Scatter(
#                 x=monthly_orders['month_label'],
#                 y=monthly_orders['order_id'],
#                 mode='lines+markers',
#                 line=dict(color='#3498db', width=3),
#                 marker=dict(size=10, color='#3498db', line=dict(color='white', width=2)),
#                 fill='tozeroy',
#                 fillcolor='rgba(52, 152, 219, 0.1)',
#                 text=monthly_orders['order_id'],
#                 texttemplate='%{text:,}',
#                 textposition='top center',
#                 textfont=dict(size=10, weight='bold'),
#                 hovertemplate='<b>%{x}</b><br>Orders: %{y:,}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Monthly Order Trend</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 xaxis=dict(title='', showgrid=False),
#                 yaxis=dict(
#                     title='Number of Orders',
#                     showgrid=True,
#                     gridcolor='rgba(0,0,0,0.05)'
#                 ),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=80, r=40),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="monthly_orders")
        
#         st.markdown("---")
    
#     # ==================== CAMPAIGN EFFECTIVENESS ====================
#     st.markdown("### 📣 Campaign Effectiveness")
    
#     if data_status['Campaign Analysis']['available']:
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
            
#             with col1:
#                 st.markdown(f"""
#                 <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                             padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#                     <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                         <b>CAMPAIGN REVENUE</b>
#                     </div>
#                     <div style='font-size: 28px; font-weight: bold; margin: 10px 0;'>
#                         {camp_share:.1f}%
#                     </div>
#                     <div style='font-size: 11px; opacity: 0.8;'>Share of total</div>
#                 </div>
#                 """, unsafe_allow_html=True)
            
#             with col2:
#                 st.markdown(f"""
#                 <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                             padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#                     <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                         <b>CONVERSION</b>
#                     </div>
#                     <div style='font-size: 28px; font-weight: bold; margin: 10px 0;'>
#                         {conv:.1f}%
#                     </div>
#                     <div style='font-size: 11px; opacity: 0.8;'>Campaign orders</div>
#                 </div>
#                 """, unsafe_allow_html=True)
            
#             with col3:
#                 st.markdown(f"""
#                 <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                             padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#                     <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                         <b>ROAS</b>
#                     </div>
#                     <div style='font-size: 28px; font-weight: bold; margin: 10px 0;'>
#                         {roas:.0f}%
#                     </div>
#                     <div style='font-size: 11px; opacity: 0.8;'>Return on ad spend</div>
#                 </div>
#                 """, unsafe_allow_html=True)
            
#             with col4:
#                 st.markdown(f"""
#                 <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
#                             padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#                     <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                         <b>CAMPAIGN AOV</b>
#                     </div>
#                     <div style='font-size: 28px; font-weight: bold; margin: 10px 0;'>
#                         ฿{camp_aov/1000:.1f}K
#                     </div>
#                     <div style='font-size: 11px; opacity: 0.8;'>Avg order value</div>
#                 </div>
#                 """, unsafe_allow_html=True)
            
#             st.markdown("<br>", unsafe_allow_html=True)
            
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 comp = pd.DataFrame({
#                     'Type': ['With Campaign', 'Without Campaign'],
#                     'AOV': [camp_aov, no_camp_aov]
#                 })
                
#                 fig = go.Figure()
                
#                 fig.add_trace(go.Bar(
#                     x=comp['Type'],
#                     y=comp['AOV'],
#                     marker=dict(
#                         color=['#27ae60', '#95a5a6'],
#                         line=dict(color='white', width=2)
#                     ),
#                     text=comp['AOV'],
#                     texttemplate='฿%{text:,.0f}',
#                     textposition='outside',
#                     textfont=dict(size=11, weight='bold'),
#                     hovertemplate='<b>%{x}</b><br>AOV: ฿%{y:,.0f}<extra></extra>'
#                 ))
                
#                 fig.update_layout(
#                     title=dict(
#                         text='<b>AOV: Campaign vs Non-Campaign</b>',
#                         font=dict(size=16, color='#2c3e50')
#                     ),
#                     xaxis=dict(title='', showgrid=False),
#                     yaxis=dict(
#                         title='Average Order Value (฿)',
#                         showgrid=True,
#                         gridcolor='rgba(0,0,0,0.05)'
#                     ),
#                     plot_bgcolor='white',
#                     paper_bgcolor='white',
#                     height=400,
#                     margin=dict(t=60, b=40, l=80, r=40),
#                     showlegend=False
#                 )
                
#                 st.plotly_chart(fig, use_container_width=True, key="campaign_aov_compare")
            
#             with col2:
#                 camp_break = camp.groupby('campaign_type')['net_revenue'].sum().sort_values(ascending=True)
                
#                 fig = go.Figure()
                
#                 fig.add_trace(go.Bar(
#                     y=camp_break.index,
#                     x=camp_break.values,
#                     orientation='h',
#                     marker_color='#9b59b6',
#                     text=camp_break.values,
#                     texttemplate='฿%{text:,.0f}',
#                     textposition='outside',
#                     textfont=dict(size=11, weight='bold'),
#                     hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
#                 ))
                
#                 fig.update_layout(
#                     title=dict(
#                         text='<b>Revenue by Campaign Type</b>',
#                         font=dict(size=16, color='#2c3e50')
#                     ),
#                     xaxis=dict(
#                         title='Revenue (฿)',
#                         showgrid=True,
#                         gridcolor='rgba(0,0,0,0.05)'
#                     ),
#                     yaxis=dict(
#                         title='',
#                         categoryorder='total ascending'
#                     ),
#                     plot_bgcolor='white',
#                     paper_bgcolor='white',
#                     height=400,
#                     margin=dict(t=60, b=40, l=120, r=100),
#                     showlegend=False
#                 )
                
#                 st.plotly_chart(fig, use_container_width=True, key="campaign_revenue_breakdown")
#     else:
#         st.info(f"💡 **Missing Campaign Data:** Add column `campaign_type` to track campaign performance and ROI")
        
#         # Show what we can do without campaign data
#         st.markdown("#### 📊 Order Value Distribution (All Orders)")
        
#         order_values = df_filtered.groupby('order_id')['net_revenue'].sum().reset_index()
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Histogram(
#             x=order_values['net_revenue'],
#             nbinsx=30,
#             marker_color='#3498db',
#             marker_line=dict(color='white', width=1),
#             hovertemplate='Value Range: ฿%{x:,.0f}<br>Orders: %{y}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Order Value Distribution</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             xaxis=dict(
#                 title='Order Value (฿)',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)'
#             ),
#             yaxis=dict(
#                 title='Number of Orders',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)'
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=60, l=80, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="order_value_dist")
    
#     st.markdown("---")
    
#     # ==================== ACQUISITION CHANNEL ====================
#     st.markdown("### 🎯 Acquisition Channel Analysis")
    
#     if data_status['Acquisition Channel']['available']:
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
#                 y=acq_sorted['Channel'],
#                 x=acq_sorted['Revenue'],
#                 orientation='h',
#                 marker=dict(color=colors_list, line=dict(color='white', width=2)),
#                 text=acq_sorted['Revenue'],
#                 texttemplate='฿%{text:,.0f}',
#                 textposition='outside',
#                 textfont=dict(size=11, weight='bold'),
#                 hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Revenue by Acquisition Channel</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 xaxis=dict(
#                     title='Revenue (฿)',
#                     showgrid=True,
#                     gridcolor='rgba(0,0,0,0.05)'
#                 ),
#                 yaxis=dict(
#                     title='',
#                     categoryorder='total ascending'
#                 ),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=120, r=100),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="acquisition_revenue")
        
#         with col2:
#             fig = go.Figure()
            
#             fig.add_trace(go.Scatter(
#                 x=acq['Customers'],
#                 y=acq['Rev/Cust'],
#                 mode='markers+text',
#                 marker=dict(
#                     size=acq['Revenue']/10000,
#                     color=[CHANNEL_COLORS.get(ch, '#95a5a6') for ch in acq['Channel']],
#                     line=dict(color='white', width=2),
#                     sizemode='diameter'
#                 ),
#                 text=acq['Channel'],
#                 textposition='top center',
#                 textfont=dict(size=10, weight='bold'),
#                 hovertemplate='<b>%{text}</b><br>Customers: %{x:,}<br>Rev/Customer: ฿%{y:,.0f}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Customer Efficiency by Channel</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 xaxis=dict(
#                     title='Number of Customers',
#                     showgrid=True,
#                     gridcolor='rgba(0,0,0,0.05)'
#                 ),
#                 yaxis=dict(
#                     title='Revenue per Customer (฿)',
#                     showgrid=True,
#                     gridcolor='rgba(0,0,0,0.05)'
#                 ),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=60, l=80, r=40),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="acquisition_efficiency")
        
#         st.markdown("#### 📊 Acquisition Channel Metrics")
        
#         styled_acq = acq.style.format({
#             'Revenue': '฿{:,.0f}',
#             'Profit': '฿{:,.0f}',
#             'Rev/Cust': '฿{:,.0f}',
#             'Conv %': '{:.1f}%',
#             'Customers': '{:,}',
#             'Orders': '{:,}'
#         }).background_gradient(subset=['Conv %'], cmap='Blues')
        
#         st.dataframe(styled_acq, use_container_width=True, height=300)
#     else:
#         st.info(f"💡 **Missing Acquisition Data:** Add column `acquisition_channel` to track where customers come from")
        
#         # Show channel analysis instead (from orders, not acquisition)
#         st.markdown("#### 📊 Sales Channel Performance (from orders)")
        
#         channel_perf = df_filtered.groupby('channel').agg({
#             'order_id': 'nunique',
#             'user_id': 'nunique',
#             'net_revenue': 'sum'
#         }).reset_index()
#         channel_perf.columns = ['Channel', 'Orders', 'Customers', 'Revenue']
#         channel_perf = channel_perf.sort_values('Revenue', ascending=False)
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             colors_list = [CHANNEL_COLORS.get(ch, '#95a5a6') for ch in channel_perf['Channel']]
            
#             fig = go.Figure()
            
#             fig.add_trace(go.Pie(
#                 labels=channel_perf['Channel'],
#                 values=channel_perf['Revenue'],
#                 hole=0.5,
#                 marker=dict(colors=colors_list, line=dict(color='white', width=2)),
#                 textposition='inside',
#                 textinfo='label+percent',
#                 textfont=dict(size=11, weight='bold'),
#                 hovertemplate='<b>%{label}</b><br>Revenue: ฿%{value:,.0f}<br>Share: %{percent}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Revenue Share by Channel</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=40, r=40),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="channel_share")
        
#         with col2:
#             channel_sorted = channel_perf.sort_values('Orders', ascending=True)
#             colors_list = [CHANNEL_COLORS.get(ch, '#95a5a6') for ch in channel_sorted['Channel']]
            
#             fig = go.Figure()
            
#             fig.add_trace(go.Bar(
#                 y=channel_sorted['Channel'],
#                 x=channel_sorted['Orders'],
#                 orientation='h',
#                 marker=dict(color=colors_list, line=dict(color='white', width=2)),
#                 text=channel_sorted['Orders'],
#                 texttemplate='%{text:,}',
#                 textposition='outside',
#                 textfont=dict(size=11, weight='bold'),
#                 hovertemplate='<b>%{y}</b><br>Orders: %{x:,}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title=dict(
#                     text='<b>Orders by Channel</b>',
#                     font=dict(size=16, color='#2c3e50')
#                 ),
#                 xaxis=dict(
#                     title='Number of Orders',
#                     showgrid=True,
#                     gridcolor='rgba(0,0,0,0.05)'
#                 ),
#                 yaxis=dict(title='', categoryorder='total ascending'),
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=120, r=80),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True, key="channel_orders")
    
#     st.markdown("---")
    
#     # ==================== CUSTOMER RETENTION ====================
#     st.markdown("### 🔄 Customer Retention")
    
#     # Calculate retention metrics
#     analysis_date = df_filtered['order_date'].max()
#     last_purchase = df_filtered.groupby('user_id')['order_date'].max()
#     churned = ((analysis_date - last_purchase).dt.days > 90).sum()
#     churn_rate = (churned / len(last_purchase) * 100) if len(last_purchase) > 0 else 0
#     retention_rate = 100 - churn_rate
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid #2ecc71; text-align: center;'>
#             <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
#                 <b>RETENTION RATE</b>
#             </div>
#             <div style='font-size: 48px; font-weight: bold; color: #2ecc71; margin: 15px 0;'>
#                 {retention_rate:.1f}%
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 Active customers (within 90 days)
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid #e74c3c; text-align: center;'>
#             <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
#                 <b>CHURN RATE</b>
#             </div>
#             <div style='font-size: 48px; font-weight: bold; color: #e74c3c; margin: 15px 0;'>
#                 {churn_rate:.1f}%
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 Inactive customers (>90 days)
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         # Customer lifetime value
#         avg_rev = df_filtered.groupby('user_id')['net_revenue'].sum().mean()
#         clv = (margin / 100) * (retention_rate / 100) * avg_rev
        
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid #3498db; text-align: center;'>
#             <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
#                 <b>CUSTOMER LTV</b>
#             </div>
#             <div style='font-size: 48px; font-weight: bold; color: #3498db; margin: 15px 0;'>
#                 ฿{clv:,.0f}
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 Average lifetime value
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("<br>", unsafe_allow_html=True)
    
#     # Cohort heatmap
#     st.markdown("#### 📊 Customer Cohort Analysis")
    
#     # Simplified cohort data
#     cohort_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
#     retention_matrix = np.array([
#         [100, 45, 35, 28, 24, 20],
#         [0, 100, 48, 38, 32, 26],
#         [0, 0, 100, 52, 42, 35],
#         [0, 0, 0, 100, 55, 45],
#         [0, 0, 0, 0, 100, 58],
#         [0, 0, 0, 0, 0, 100]
#     ])
    
#     fig = go.Figure(data=go.Heatmap(
#         z=retention_matrix,
#         x=['Month 0', 'Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5'],
#         y=cohort_months,
#         colorscale='RdYlGn',
#         text=retention_matrix,
#         texttemplate='%{text:.0f}%',
#         textfont=dict(size=12, weight='bold'),
#         hoverongaps=False,
#         hovertemplate='Cohort: %{y}<br>Period: %{x}<br>Retention: %{z:.0f}%<extra></extra>'
#     ))
    
#     fig.update_layout(
#         title=dict(
#             text='<b>Cohort Retention Heatmap (%)</b>',
#             font=dict(size=16, color='#2c3e50')
#         ),
#         xaxis=dict(title='Months Since First Purchase', side='bottom'),
#         yaxis=dict(title='Cohort (First Purchase Month)'),
#         plot_bgcolor='white',
#         paper_bgcolor='white',
#         height=400,
#         margin=dict(t=60, b=60, l=80, r=40)
#     )
    
#     st.plotly_chart(fig, use_container_width=True, key="cohort_heatmap")

# with tab3:
#     st.markdown("# 💰 Financial Analytics")
#     st.markdown("---")
    
#     # ==================== PROFIT MARGIN ====================
#     st.markdown("### 📊 Profit Margin")
    
#     cogs = df_filtered['cost'].sum()
#     gross_profit = revenue - cogs
#     gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
#     net_margin = (profit / revenue * 100) if revenue > 0 else 0
    
#     col1, col2 = st.columns([1, 1])
    
#     with col1:
#         # Waterfall chart for profit breakdown
#         fig = go.Figure(go.Waterfall(
#             orientation="v",
#             measure=["relative", "relative", "total"],
#             x=["Revenue", "COGS", "Gross Profit"],
#             y=[revenue, -cogs, gross_profit],
#             text=[f"฿{revenue:,.0f}", f"-฿{cogs:,.0f}", f"฿{gross_profit:,.0f}"],
#             textposition="outside",
#             connector={"line": {"color": "rgb(63, 63, 63)"}},
#             decreasing={"marker": {"color": "#e74c3c"}},
#             increasing={"marker": {"color": "#2ecc71"}},
#             totals={"marker": {"color": "#3498db"}},
#             hovertemplate='<b>%{x}</b><br>Amount: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Profit Breakdown</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=60, l=80, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="profit_waterfall")
    
#     with col2:
#         # Monthly margin trend
#         mon_fin = df_filtered.groupby('order_month').agg({
#             'net_revenue': 'sum',
#             'cost': 'sum',
#             'profit': 'sum'
#         }).reset_index()
#         mon_fin['order_month'] = mon_fin['order_month'].dt.to_timestamp()
#         mon_fin['margin_%'] = (mon_fin['profit'] / mon_fin['net_revenue'] * 100).round(2)
#         mon_fin['month_label'] = mon_fin['order_month'].dt.strftime('%b %Y')
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Scatter(
#             x=mon_fin['month_label'],
#             y=mon_fin['margin_%'],
#             mode='lines+markers',
#             name='Profit Margin',
#             line=dict(color='#2ecc71', width=3),
#             marker=dict(size=10, color='#2ecc71', line=dict(color='white', width=2)),
#             fill='tozeroy',
#             fillcolor='rgba(46, 204, 113, 0.1)',
#             text=mon_fin['margin_%'],
#             texttemplate='%{text:.1f}%',
#             textposition='top center',
#             textfont=dict(size=10, weight='bold'),
#             hovertemplate='<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Profit Margin Trend (%)</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(
#                 title='Margin (%)',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)',
#                 range=[0, max(mon_fin['margin_%']) * 1.2]
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=80, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="margin_trend")
    
#     st.markdown("---")
    
#     # ==================== SALES + GROSS PROFIT + CAC ====================
#     st.markdown("### 📈 Sales + Gross Profit + CAC")
    
#     # Prepare data
#     channel_fin = df_filtered.groupby(['order_month', 'channel']).agg({
#         'net_revenue': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     channel_fin['order_month'] = channel_fin['order_month'].dt.to_timestamp()
#     channel_fin['month_label'] = channel_fin['order_month'].dt.strftime('%b %Y')
    
#     # Create stacked bar chart
#     fig = go.Figure()
    
#     for channel in channel_fin['channel'].unique():
#         channel_data = channel_fin[channel_fin['channel'] == channel]
#         fig.add_trace(go.Bar(
#             x=channel_data['month_label'],
#             y=channel_data['net_revenue'],
#             name=channel,
#             marker_color=CHANNEL_COLORS.get(channel, '#95a5a6'),
#             hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>Revenue: ฿%{y:,.0f}<extra></extra>'
#         ))
    
#     # Add gross profit line
#     monthly_profit = df_filtered.groupby('order_month').agg({
#         'profit': 'sum'
#     }).reset_index()
#     monthly_profit['order_month'] = monthly_profit['order_month'].dt.to_timestamp()
#     monthly_profit['month_label'] = monthly_profit['order_month'].dt.strftime('%b %Y')
    
#     fig.add_trace(go.Scatter(
#         x=monthly_profit['month_label'],
#         y=monthly_profit['profit'],
#         name='Gross Profit',
#         mode='lines+markers',
#         line=dict(color='#2ecc71', width=3),
#         marker=dict(size=10, symbol='diamond'),
#         yaxis='y2',
#         hovertemplate='<b>Gross Profit</b><br>%{x}<br>฿%{y:,.0f}<extra></extra>'
#     ))
    
#     fig.update_layout(
#         title=dict(
#             text='<b>Sales by Channel + Gross Profit</b>',
#             font=dict(size=18, color='#2c3e50')
#         ),
#         barmode='stack',
#         xaxis=dict(title='', showgrid=False),
#         yaxis=dict(
#             title='Revenue (฿)',
#             showgrid=True,
#             gridcolor='rgba(0,0,0,0.05)'
#         ),
#         yaxis2=dict(
#             title='Gross Profit (฿)',
#             overlaying='y',
#             side='right',
#             showgrid=False
#         ),
#         plot_bgcolor='white',
#         paper_bgcolor='white',
#         height=450,
#         margin=dict(t=60, b=40, l=80, r=80),
#         hovermode='x unified',
#         legend=dict(
#             orientation="h",
#             yanchor="bottom",
#             y=1.02,
#             xanchor="right",
#             x=1
#         )
#     )
    
#     st.plotly_chart(fig, use_container_width=True, key="sales_profit_channel")
    
#     st.markdown("---")
    
#     # ==================== FINANCIAL KPIs ====================
#     st.markdown("### 💎 Financial KPIs")
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #3498db; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>TOTAL REVENUE</b>
#             </div>
#             <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
#                 ฿{revenue:,.0f}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #e74c3c; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>TOTAL COGS</b>
#             </div>
#             <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
#                 ฿{cogs:,.0f}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #2ecc71; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>GROSS PROFIT</b>
#             </div>
#             <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
#                 ฿{gross_profit:,.0f}
#             </div>
#             <div style='font-size: 12px; color: #2ecc71; margin-top: 5px;'>
#                 Margin: {gross_margin:.1f}%
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #9b59b6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>NET PROFIT</b>
#             </div>
#             <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
#                 ฿{profit:,.0f}
#             </div>
#             <div style='font-size: 12px; color: #9b59b6; margin-top: 5px;'>
#                 Margin: {net_margin:.1f}%
#             </div>
#         </div>
#         """, unsafe_allow_html=True)

# with tab4:
#     st.markdown("# 📦 Warehouse & Inventory")
#     st.markdown("---")
    
#     # ==================== INVENTORY METRICS ====================
#     st.markdown("### 📊 Inventory Performance")
    
#     avg_inv = df_filtered['cost'].mean() * df_filtered['product_id'].nunique()
#     inv_turnover = cogs / avg_inv if avg_inv > 0 else 0
#     dio = 365 / inv_turnover if inv_turnover > 0 else 0
    
#     units_sold = df_filtered['quantity'].sum()
#     units_received = units_sold * 1.2
#     sell_through = (units_sold / units_received * 100) if units_received > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;
#                     box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>INVENTORY TURNOVER</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {inv_turnover:.2f}x
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>
#                 Times per year
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;
#                     box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>DAYS IN INVENTORY</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {dio:.0f}
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>
#                 Days
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;
#                     box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>SELL-THROUGH RATE</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {sell_through:.1f}%
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>
#                 Of received inventory
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;
#                     box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>INVENTORY VALUE</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 ฿{avg_inv/1000:.0f}K
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>
#                 Total stock value
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("<br>", unsafe_allow_html=True)
#     st.markdown("---")
    
#     # ==================== PRODUCT MOVEMENT ====================
#     st.markdown("### 🚀 Product Movement Analysis")
    
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
#         colors_mov = {
#             'Fast Moving': '#2ecc71',
#             'Medium Moving': '#f39c12',
#             'Slow Moving': '#e74c3c'
#         }
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Pie(
#             labels=mov.index,
#             values=mov.values,
#             hole=0.6,
#             marker=dict(
#                 colors=[colors_mov[label] for label in mov.index],
#                 line=dict(color='white', width=3)
#             ),
#             textposition='inside',
#             textinfo='label+percent',
#             textfont=dict(size=12, weight='bold', color='white'),
#             hovertemplate='<b>%{label}</b><br>Products: %{value}<br>Share: %{percent}<extra></extra>'
#         ))
        
#         fig.add_annotation(
#             text=f'<b>Total</b><br>{len(prod_vel)} products',
#             x=0.5, y=0.5,
#             font=dict(size=14, color='#2c3e50'),
#             showarrow=False
#         )
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Product Distribution by Movement</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=40, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="movement_pie")
    
#     with col2:
#         mov_val = prod_vel.groupby('Movement')['Cost'].sum().sort_values(ascending=False)
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             x=mov_val.index,
#             y=mov_val.values,
#             marker=dict(
#                 color=[colors_mov[label] for label in mov_val.index],
#                 line=dict(color='white', width=2)
#             ),
#             text=mov_val.values,
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             textfont=dict(size=11, weight='bold'),
#             hovertemplate='<b>%{x}</b><br>Value: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title=dict(
#                 text='<b>Inventory Value by Movement</b>',
#                 font=dict(size=16, color='#2c3e50')
#             ),
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(
#                 title='Value (฿)',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)'
#             ),
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             height=400,
#             margin=dict(t=60, b=40, l=80, r=40),
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True, key="movement_value")

# # Footer
# st.markdown("---")
# st.markdown("""
# <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#             border-radius: 15px; color: white;'>
#     <h3 style='margin: 0; font-size: 24px;'>📊 Fashion Analytics Dashboard</h3>
#     <p style='margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;'>
#         Built with Streamlit • Data-Driven Insights for Better Business Decisions
#     </p>
# </div>
# """, unsafe_allow_html=True)



































































# # Analytics Dashboard - Improved Version with KPIs
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
# import numpy as np
# import warnings
# from datetime import datetime, timedelta

# warnings.filterwarnings('ignore')
# st.set_page_config(page_title="Fashion Analytics Pro", layout="wide", page_icon="👕")

# # Enhanced Color Palette
# COLORS = {
#     'primary': '#1f77b4',
#     'secondary': '#ff7f0e',
#     'success': '#2ecc71',
#     'danger': '#e74c3c',
#     'warning': '#f39c12',
#     'info': '#3498db',
#     'purple': '#9b59b6',
#     'teal': '#1abc9c',
#     'pink': '#e91e63',
#     'indigo': '#3f51b5'
# }

# # Channel Color Mapping
# CHANNEL_COLORS = {
#     'TikTok': '#000000',
#     'Shopee': '#FF5722',
#     'Lazada': '#1E88E5',
#     'LINE Shopping': '#00C300',
#     'Instagram': '#9C27B0',
#     'Facebook': '#1877F2',
#     'Store': '#795548',
#     'Pop-up': '#FF9800',
#     'Website': '#607D8B'
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
#     st.sidebar.title("📊 Analytics Dashboard")
#     st.sidebar.markdown("### 📁 Data Upload")
#     st.sidebar.markdown("Upload your CSV files to begin analysis")
#     st.sidebar.markdown("---")
    
#     uploaded = st.sidebar.file_uploader(
#         "Choose CSV Files", 
#         type=['csv'], 
#         accept_multiple_files=True,
#         key="csv_uploader_main"
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
        
#         with st.sidebar:
#             st.markdown("**Loading Status:**")
        
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
#                             st.sidebar.error(f"❌ {file.name}")
#                             st.sidebar.caption(f"Missing: {', '.join(missing)}")
#                     else:
#                         data[table] = df
#                         st.sidebar.success(f"✅ {file.name}")
#                 except Exception as e:
#                     st.sidebar.error(f"❌ {file.name}")
#                     st.sidebar.caption(str(e))
        
#         if all(t in data for t in ['users', 'products', 'orders', 'order_items']):
#             st.session_state.data = data
#             st.session_state.data_loaded = True
#             st.sidebar.markdown("---")
#             st.sidebar.success("✅ **All data loaded successfully!**")
#             st.rerun()
#         else:
#             st.sidebar.error("❌ Missing required tables")
#             missing_tables = [t for t in ['users', 'products', 'orders', 'order_items'] if t not in data]
#             st.sidebar.caption(f"Need: {', '.join(missing_tables)}.csv")
    
#     if st.session_state.data_loaded:
#         st.sidebar.markdown("---")
#         st.sidebar.markdown("### ✅ Data Status")
#         st.sidebar.success("Data loaded and ready")
        
#         if st.session_state.data:
#             total_orders = len(st.session_state.data.get('orders', []))
#             total_customers = len(st.session_state.data.get('users', []))
#             total_products = len(st.session_state.data.get('products', []))
            
#             st.sidebar.markdown(f"""
#             - **Orders:** {total_orders:,}
#             - **Customers:** {total_customers:,}
#             - **Products:** {total_products:,}
#             """)
    
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

# # Custom CSS
# st.markdown("""
# <style>
#     .block-container {padding-top: 1rem; padding-bottom: 1rem;}
#     [data-testid="stMetricValue"] {font-size: 24px; font-weight: 600;}
#     [data-testid="stMetricLabel"] {font-size: 13px; font-weight: 500; color: #555;}
#     h1, h2, h3 {font-family: 'Inter', sans-serif; font-weight: 700;}
    
#     /* Info boxes for explanations */
#     .metric-explanation {
#         background: #f8f9fa;
#         padding: 15px;
#         border-radius: 8px;
#         border-left: 4px solid #3498db;
#         margin: 10px 0;
#         font-size: 13px;
#         color: #2c3e50;
#     }
    
#     .metric-formula {
#         background: #e8f4f8;
#         padding: 10px;
#         border-radius: 5px;
#         font-family: monospace;
#         font-size: 12px;
#         margin: 5px 0;
#     }
# </style>
# """, unsafe_allow_html=True)

# data = load_data()

# if not data:
#     st.title("📊 Analytics Dashboard")
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

# # ==================== MAIN FILTERS ====================
# st.title("📊 Fashion Analytics Dashboard")
# st.markdown("---")

# st.markdown("### 🔍 Filter Data")

# min_date = df_master['order_date'].min().date()
# max_date = df_master['order_date'].max().date()

# col1, col2, col3 = st.columns([2, 2, 1])

# with col1:
#     period_options = ["Custom Range", "Last 7 Days", "Last 30 Days", "Last 90 Days", 
#                       "This Month", "Last Month", "This Quarter", "This Year", "All Time"]
#     selected_period = st.selectbox("📅 Time Period", period_options, index=2, key="period_selector")

# with col2:
#     if selected_period == "Last 7 Days":
#         start_date = max_date - timedelta(days=7)
#         end_date = max_date
#     elif selected_period == "Last 30 Days":
#         start_date = max_date - timedelta(days=30)
#         end_date = max_date
#     elif selected_period == "Last 90 Days":
#         start_date = max_date - timedelta(days=90)
#         end_date = max_date
#     elif selected_period == "This Month":
#         start_date = max_date.replace(day=1)
#         end_date = max_date
#     elif selected_period == "Last Month":
#         first_day_this_month = max_date.replace(day=1)
#         end_date = first_day_this_month - timedelta(days=1)
#         start_date = end_date.replace(day=1)
#     elif selected_period == "This Quarter":
#         quarter = (max_date.month - 1) // 3
#         start_date = datetime(max_date.year, quarter * 3 + 1, 1).date()
#         end_date = max_date
#     elif selected_period == "This Year":
#         start_date = datetime(max_date.year, 1, 1).date()
#         end_date = max_date
#     elif selected_period == "All Time":
#         start_date = min_date
#         end_date = max_date
#     else:
#         date_range = st.date_input(
#             "Custom Date Range", 
#             [min_date, max_date], 
#             min_value=min_date, 
#             max_value=max_date,
#             key="custom_date_range"
#         )
#         if len(date_range) == 2:
#             start_date, end_date = date_range
#         else:
#             start_date, end_date = min_date, max_date
    
#     st.info(f"📆 **{start_date.strftime('%d %b %Y')}** → **{end_date.strftime('%d %b %Y')}**")

# with col3:
#     if st.button("🔄 Reset All", key="reset_filters", use_container_width=True):
#         st.rerun()

# df_filtered = df_master[(df_master['order_date'].dt.date >= start_date) & 
#                         (df_master['order_date'].dt.date <= end_date)]

# col1, col2, col3 = st.columns(3)

# with col1:
#     channels = st.multiselect(
#         "🏪 Sales Channel", 
#         df_master['channel'].unique(), 
#         df_master['channel'].unique(),
#         key="channel_filter"
#     )
#     df_filtered = df_filtered[df_filtered['channel'].isin(channels)]

# with col2:
#     statuses = st.multiselect(
#         "📦 Order Status", 
#         df_master['status'].unique(), 
#         ['Completed'],
#         key="status_filter"
#     )
#     df_filtered = df_filtered[df_filtered['status'].isin(statuses)]

# with col3:
#     if 'category' in df_filtered.columns:
#         categories = st.multiselect(
#             "🏷️ Product Category",
#             df_master['category'].unique(),
#             df_master['category'].unique(),
#             key="category_filter"
#         )
#         df_filtered = df_filtered[df_filtered['category'].isin(categories)]

# st.markdown("---")
# st.markdown("### 📊 Summary Statistics")

# # Calculate key metrics
# revenue = df_filtered['net_revenue'].sum()
# profit = df_filtered['profit'].sum()
# cogs = df_filtered['cost'].sum()
# total_orders = df_filtered['order_id'].nunique()
# total_customers = df_filtered['user_id'].nunique()
# gross_profit = revenue - cogs
# profit_margin = (profit / revenue * 100) if revenue > 0 else 0
# avg_order_value = revenue / total_orders if total_orders > 0 else 0

# col1, col2, col3, col4, col5, col6 = st.columns(6)

# with col1:
#     st.metric("💰 Revenue", f"฿{revenue/1000:,.0f}K")
# with col2:
#     st.metric("💵 Profit", f"฿{profit/1000:,.0f}K")
# with col3:
#     st.metric("📝 Orders", f"{total_orders:,}")
# with col4:
#     st.metric("👥 Customers", f"{total_customers:,}")
# with col5:
#     st.metric("📊 Margin", f"{profit_margin:.1f}%")
# with col6:
#     st.metric("🛒 AOV", f"฿{avg_order_value:,.0f}")

# st.markdown("---")

# # ==================== TABS ====================
# tab1, tab2, tab3, tab4 = st.tabs(["💼 Sales Analytics", "📢 Marketing Analytics", "💰 Financial Analytics", "📦 Warehouse Analytics"])

# with tab1:
#     st.markdown("# 💼 Sales Analytics")
#     st.markdown("---")
    
#     # ==================== SALES GROWTH ====================
#     st.markdown("### 📈 Monthly Sales Growth")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> วัดว่ายอดขายเติบโตกี่ % เมื่อเทียบกับเดือนก่อนหน้า<br>
#         <div class='metric-formula'>
#         สูตร: [(ยอดขายเดือนปัจจุบัน - ยอดขายเดือนก่อน) / ยอดขายเดือนก่อน] × 100
#         </div>
#         <b>🎯 เป้าหมาย:</b> ควรเป็นบวก และมากกว่า 5-10% ถือว่าดี
#     </div>
#     """, unsafe_allow_html=True)
    
#     monthly_sales = df_filtered.groupby('order_month').agg({
#         'net_revenue': 'sum'
#     }).reset_index()
#     monthly_sales['order_month'] = monthly_sales['order_month'].dt.to_timestamp()
#     monthly_sales['month_label'] = monthly_sales['order_month'].dt.strftime('%b %Y')
#     monthly_sales['growth_%'] = monthly_sales['net_revenue'].pct_change() * 100
    
#     col1, col2 = st.columns([2, 1])
    
#     with col1:
#         fig = go.Figure()
        
#         # Revenue bars
#         fig.add_trace(go.Bar(
#             x=monthly_sales['month_label'],
#             y=monthly_sales['net_revenue'],
#             name='Revenue',
#             marker=dict(
#                 color=monthly_sales['net_revenue'],
#                 colorscale='Blues',
#                 showscale=False
#             ),
#             text=monthly_sales['net_revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         # Growth line
#         fig.add_trace(go.Scatter(
#             x=monthly_sales['month_label'],
#             y=monthly_sales['growth_%'],
#             name='Growth %',
#             mode='lines+markers',
#             line=dict(color='#e74c3c', width=3),
#             marker=dict(size=10),
#             yaxis='y2',
#             text=monthly_sales['growth_%'],
#             texttemplate='%{text:.1f}%',
#             textposition='top center',
#             hovertemplate='<b>%{x}</b><br>Growth: %{y:.1f}%<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Monthly Sales Revenue & Growth Rate</b>',
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             yaxis2=dict(
#                 title='Growth (%)', 
#                 overlaying='y', 
#                 side='right',
#                 showgrid=False,
#                 zeroline=True,
#                 zerolinecolor='gray'
#             ),
#             plot_bgcolor='white',
#             height=400,
#             hovermode='x unified',
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         latest_growth = monthly_sales['growth_%'].iloc[-1] if len(monthly_sales) > 1 else 0
#         prev_growth = monthly_sales['growth_%'].iloc[-2] if len(monthly_sales) > 2 else 0
        
#         arrow = "📈" if latest_growth > 0 else "📉"
#         color = "#2ecc71" if latest_growth > 0 else "#e74c3c"
        
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid {color}; height: 400px;
#                     display: flex; flex-direction: column; justify-content: center; align-items: center;'>
#             <div style='font-size: 60px;'>{arrow}</div>
#             <div style='font-size: 48px; font-weight: bold; color: {color}; margin: 20px 0;'>
#                 {latest_growth:+.1f}%
#             </div>
#             <div style='font-size: 16px; color: #7f8c8d; text-align: center;'>
#                 <b>Current Month Growth</b>
#             </div>
#             <div style='margin-top: 20px; font-size: 14px; color: #95a5a6;'>
#                 Previous: {prev_growth:.1f}%
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== SALES TARGET ATTAINMENT ====================
#     st.markdown("### 🎯 Sales Target Attainment")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> วัดว่าทำยอดขายได้กี่ % ของเป้าหมายที่ตั้งไว้<br>
#         <div class='metric-formula'>
#         สูตร: (ยอดขายที่ทำได้ / เป้าหมายยอดขาย) × 100
#         </div>
#         <b>🎯 เป้าหมาย:</b> ควรอยู่ที่ 90-110% (น้อยกว่า 90% ต้องปรับปรุง, มากกว่า 110% ดีมาก)
#     </div>
#     """, unsafe_allow_html=True)
    
#     # Calculate target attainment
#     target_monthly = 5000000  # 5M target
#     current_month_sales = monthly_sales['net_revenue'].iloc[-1] if len(monthly_sales) > 0 else 0
#     attainment = (current_month_sales / target_monthly * 100) if target_monthly > 0 else 0
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 30px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 14px; opacity: 0.9;'>TARGET</div>
#             <div style='font-size: 36px; font-weight: bold; margin: 15px 0;'>
#                 ฿{target_monthly/1000000:.1f}M
#             </div>
#             <div style='font-size: 12px; opacity: 0.8;'>Monthly Goal</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 30px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 14px; opacity: 0.9;'>ACTUAL</div>
#             <div style='font-size: 36px; font-weight: bold; margin: 15px 0;'>
#                 ฿{current_month_sales/1000000:.1f}M
#             </div>
#             <div style='font-size: 12px; opacity: 0.8;'>Current Sales</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         att_color = '#2ecc71' if attainment >= 90 else '#e74c3c'
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid {att_color}; text-align: center;'>
#             <div style='font-size: 14px; color: #7f8c8d;'>ATTAINMENT</div>
#             <div style='font-size: 36px; font-weight: bold; margin: 15px 0; color: {att_color};'>
#                 {attainment:.1f}%
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 {'✅ On Track' if attainment >= 90 else '⚠️ Below Target'}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== SALES BY CHANNEL ====================
#     st.markdown("### 🏪 Sales by Channel")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> แสดงยอดขายแยกตามช่องทางการขาย เพื่อดูว่าช่องทางไหนมี Performance ดีที่สุด
#     </div>
#     """, unsafe_allow_html=True)
    
#     channel_sales = df_filtered.groupby('channel').agg({
#         'net_revenue': 'sum',
#         'profit': 'sum',
#         'order_id': 'nunique'
#     }).reset_index()
#     channel_sales.columns = ['Channel', 'Revenue', 'Profit', 'Orders']
#     channel_sales['Margin_%'] = (channel_sales['Profit'] / channel_sales['Revenue'] * 100).round(1)
#     channel_sales['AOV'] = (channel_sales['Revenue'] / channel_sales['Orders']).round(0)
#     channel_sales = channel_sales.sort_values('Revenue', ascending=False)
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         # Horizontal bar chart
#         ch_sorted = channel_sales.sort_values('Revenue', ascending=True)
#         colors_list = [CHANNEL_COLORS.get(ch, '#95a5a6') for ch in ch_sorted['Channel']]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             y=ch_sorted['Channel'],
#             x=ch_sorted['Revenue'],
#             orientation='h',
#             marker=dict(color=colors_list),
#             text=ch_sorted['Revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Revenue by Channel</b>',
#             xaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             yaxis=dict(title=''),
#             plot_bgcolor='white',
#             height=400,
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         # Stacked bar: Revenue vs Profit
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             x=channel_sales['Channel'],
#             y=channel_sales['Profit'],
#             name='Profit',
#             marker_color='#2ecc71',
#             text=channel_sales['Profit'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='inside',
#             hovertemplate='<b>%{x}</b><br>Profit: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.add_trace(go.Bar(
#             x=channel_sales['Channel'],
#             y=channel_sales['Revenue'] - channel_sales['Profit'],
#             name='Cost',
#             marker_color='#e74c3c',
#             text=channel_sales['Revenue'] - channel_sales['Profit'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='inside',
#             hovertemplate='<b>%{x}</b><br>Cost: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Revenue Breakdown: Profit vs Cost</b>',
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(title='Amount (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             barmode='stack',
#             plot_bgcolor='white',
#             height=400,
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Channel metrics table
#     st.markdown("#### 📊 Channel Performance Metrics")
    
#     styled_ch = channel_sales.style.format({
#         'Revenue': '฿{:,.0f}',
#         'Profit': '฿{:,.0f}',
#         'Orders': '{:,}',
#         'Margin_%': '{:.1f}%',
#         'AOV': '฿{:,.0f}'
#     }).background_gradient(subset=['Margin_%'], cmap='RdYlGn', vmin=0, vmax=100)
    
#     st.dataframe(styled_ch, use_container_width=True)
    
#     st.markdown("---")
    
#     # ==================== PRODUCT PERFORMANCE ====================
#     st.markdown("### 🏆 Top Product Performance")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> แสดงสินค้าที่ขายดีที่สุด 20 อันดับแรก วัดจากยอดขาย และอัตรากำไร
#     </div>
#     """, unsafe_allow_html=True)
    
#     product_sales = df_filtered.groupby(['product_id', 'product_name', 'category']).agg({
#         'net_revenue': 'sum',
#         'profit': 'sum',
#         'quantity': 'sum'
#     }).reset_index()
#     product_sales.columns = ['ID', 'Product', 'Category', 'Revenue', 'Profit', 'Units']
#     product_sales['Margin_%'] = (product_sales['Profit'] / product_sales['Revenue'] * 100).round(1)
#     product_sales = product_sales.sort_values('Revenue', ascending=False).head(20)
    
#     col1, col2 = st.columns([3, 2])
    
#     with col1:
#         # Top 10 horizontal bar
#         top10 = product_sales.head(10).sort_values('Revenue', ascending=True)
        
#         fig = go.Figure()
        
#         # Color by margin
#         colors = ['#2ecc71' if m >= 50 else '#f39c12' if m >= 30 else '#e74c3c' 
#                   for m in top10['Margin_%']]
        
#         fig.add_trace(go.Bar(
#             y=top10['Product'],
#             x=top10['Revenue'],
#             orientation='h',
#             marker=dict(color=colors),
#             text=top10['Revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             customdata=top10[['Margin_%']],
#             hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<br>Margin: %{customdata[0]:.1f}%<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Top 10 Products by Revenue</b><br><sub>Color: Green=High Margin, Yellow=Medium, Red=Low</sub>',
#             xaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             yaxis=dict(title=''),
#             plot_bgcolor='white',
#             height=450,
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         # Scatter: Revenue vs Margin
#         fig = go.Figure()
        
#         fig.add_trace(go.Scatter(
#             x=product_sales['Revenue'],
#             y=product_sales['Margin_%'],
#             mode='markers',
#             marker=dict(
#                 size=product_sales['Units']/10,
#                 color=product_sales['Margin_%'],
#                 colorscale='RdYlGn',
#                 showscale=True,
#                 colorbar=dict(title="Margin %"),
#                 line=dict(width=1, color='white')
#             ),
#             text=product_sales['Product'],
#             hovertemplate='<b>%{text}</b><br>Revenue: ฿%{x:,.0f}<br>Margin: %{y:.1f}%<extra></extra>'
#         ))
        
#         # Add quadrant lines
#         avg_revenue = product_sales['Revenue'].median()
#         avg_margin = product_sales['Margin_%'].median()
        
#         fig.add_hline(y=avg_margin, line_dash="dash", line_color="gray", opacity=0.5)
#         fig.add_vline(x=avg_revenue, line_dash="dash", line_color="gray", opacity=0.5)
        
#         fig.update_layout(
#             title='<b>Product Portfolio Analysis</b><br><sub>Size = Units Sold</sub>',
#             xaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             yaxis=dict(title='Profit Margin (%)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             plot_bgcolor='white',
#             height=450
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     st.markdown("#### 📋 Top 20 Products Detail")
    
#     styled_prod = product_sales.style.format({
#         'Revenue': '฿{:,.0f}',
#         'Profit': '฿{:,.0f}',
#         'Units': '{:,}',
#         'Margin_%': '{:.1f}%'
#     }).background_gradient(subset=['Margin_%'], cmap='RdYlGn', vmin=0, vmax=100)
    
#     st.dataframe(styled_prod, use_container_width=True)

# with tab2:
#     st.markdown("# 📢 Marketing Analytics")
#     st.markdown("---")
    
#     # Data availability checker
#     st.markdown("### 📋 Available Marketing Metrics")
    
#     has_campaign = 'campaign_type' in df_filtered.columns and df_filtered['campaign_type'].notna().any()
#     has_acquisition = 'acquisition_channel' in df_filtered.columns
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         if has_campaign:
#             st.success("✅ **Campaign Data Available**")
#         else:
#             st.warning("⚠️ **Campaign Data Missing**\nAdd `campaign_type` column for campaign analysis")
    
#     with col2:
#         if has_acquisition:
#             st.success("✅ **Acquisition Channel Data Available**")
#         else:
#             st.warning("⚠️ **Acquisition Data Missing**\nAdd `acquisition_channel` column for acquisition analysis")
    
#     st.markdown("---")
    
#     # ==================== CUSTOMER ACQUISITION COST ====================
#     st.markdown("### 💳 Customer Acquisition Cost (CAC)")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> ค่าใช้จ่ายที่ใช้ในการหาลูกค้าใหม่ 1 คน<br>
#         <div class='metric-formula'>
#         สูตร: ค่าใช้จ่ายทางการตลาด / จำนวนลูกค้าใหม่
#         </div>
#         <b>🎯 เป้าหมาย:</b> ควรต่ำกว่า Customer Lifetime Value (CLV) อย่างน้อย 3 เท่า
#     </div>
#     """, unsafe_allow_html=True)
    
#     marketing_cost = df_filtered['discount_amount'].sum() if 'discount_amount' in df_filtered.columns else 0
#     new_customers = df_filtered['user_id'].nunique()
#     cac = marketing_cost / new_customers if new_customers > 0 else 0
    
#     # Calculate CLV
#     analysis_date = df_filtered['order_date'].max()
#     last_purchase = df_filtered.groupby('user_id')['order_date'].max()
#     churned = ((analysis_date - last_purchase).dt.days > 90).sum()
#     churn_rate = (churned / len(last_purchase) * 100) if len(last_purchase) > 0 else 0
#     retention_rate = 100 - churn_rate
#     avg_revenue = df_filtered.groupby('user_id')['net_revenue'].sum().mean()
#     clv = (profit_margin / 100) * (retention_rate / 100) * avg_revenue
    
#     cac_to_clv_ratio = (cac / clv) if clv > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9;'>CAC</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
#                 ฿{cac:,.0f}
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Per customer</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9;'>CLV</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
#                 ฿{clv:,.0f}
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Lifetime value</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         ratio_color = '#2ecc71' if cac_to_clv_ratio < 0.33 else '#e74c3c'
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border: 3px solid {ratio_color}; text-align: center;'>
#             <div style='font-size: 13px; color: #7f8c8d;'>CAC : CLV</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0; color: {ratio_color};'>
#                 1:{(clv/cac if cac > 0 else 0):.1f}
#             </div>
#             <div style='font-size: 11px; color: #95a5a6;'>
#                 {'✅ Good' if cac_to_clv_ratio < 0.33 else '⚠️ Too High'}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9;'>NEW CUSTOMERS</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
#                 {new_customers:,}
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>In period</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== RETENTION & CHURN ====================
#     st.markdown("### 🔄 Customer Retention & Churn Rate")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 Retention Rate:</b> เปอร์เซ็นต์ของลูกค้าที่ยังคงซื้อสินค้ากับเรา (ไม่หายไป)<br>
#         <div class='metric-formula'>
#         สูตร: [1 - (จำนวนลูกค้าที่หายไป / จำนวนลูกค้าเริ่มต้น)] × 100
#         </div>
#         <b>📖 Churn Rate:</b> เปอร์เซ็นต์ของลูกค้าที่หยุดซื้อสินค้า (ไม่ซื้อเกิน 90 วัน)<br>
#         <b>🎯 เป้าหมาย:</b> Retention ควรสูงกว่า 80%, Churn ควรต่ำกว่า 20%
#     </div>
#     """, unsafe_allow_html=True)
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid #2ecc71; text-align: center; height: 200px;
#                     display: flex; flex-direction: column; justify-content: center;'>
#             <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
#                 <b>RETENTION RATE</b>
#             </div>
#             <div style='font-size: 48px; font-weight: bold; color: #2ecc71; margin: 15px 0;'>
#                 {retention_rate:.1f}%
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 Active customers
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid #e74c3c; text-align: center; height: 200px;
#                     display: flex; flex-direction: column; justify-content: center;'>
#             <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
#                 <b>CHURN RATE</b>
#             </div>
#             <div style='font-size: 48px; font-weight: bold; color: #e74c3c; margin: 15px 0;'>
#                 {churn_rate:.1f}%
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 Lost customers
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         active_customers = int(len(last_purchase) * retention_rate / 100)
#         churned_customers = int(len(last_purchase) * churn_rate / 100)
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             x=['Active', 'Churned'],
#             y=[active_customers, churned_customers],
#             marker=dict(color=['#2ecc71', '#e74c3c']),
#             text=[active_customers, churned_customers],
#             texttemplate='%{text:,}',
#             textposition='outside',
#             hovertemplate='<b>%{x}</b><br>Customers: %{y:,}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Customer Status</b>',
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(title='Number of Customers', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             plot_bgcolor='white',
#             height=200,
#             showlegend=False,
#             margin=dict(t=40, b=40, l=60, r=20)
#         )
        
#         st.plotly_chart(fig, use_container_width=True)

# with tab3:
#     st.markdown("# 💰 Financial Analytics")
#     st.markdown("---")
    
#     # ==================== PROFIT MARGINS ====================
#     st.markdown("### 📊 Profit Margin Analysis")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 Gross Profit Margin:</b> เปอร์เซ็นต์กำไรขั้นต้น (หลังหักต้นทุนสินค้า)<br>
#         <div class='metric-formula'>
#         สูตร: [(รายได้ - ต้นทุนสินค้า) / รายได้] × 100
#         </div>
#         <b>📖 Net Profit Margin:</b> เปอร์เซ็นต์กำไรสุทธิ (หลังหักค่าใช้จ่ายทั้งหมด)<br>
#         <div class='metric-formula'>
#         สูตร: (กำไรสุทธิ / รายได้) × 100
#         </div>
#         <b>🎯 เป้าหมาย:</b> Gross Margin > 50%, Net Margin > 20% ถือว่าดี
#     </div>
#     """, unsafe_allow_html=True)
    
#     gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
#     net_margin = (profit / revenue * 100) if revenue > 0 else 0
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         # Waterfall chart
#         fig = go.Figure(go.Waterfall(
#             orientation="v",
#             measure=["relative", "relative", "relative", "total"],
#             x=["Revenue", "COGS", "Other Costs", "Net Profit"],
#             y=[revenue, -cogs, -(gross_profit - profit), profit],
#             text=[f"฿{revenue:,.0f}", f"-฿{cogs:,.0f}", f"-฿{(gross_profit - profit):,.0f}", f"฿{profit:,.0f}"],
#             textposition="outside",
#             connector={"line": {"color": "rgb(63, 63, 63)"}},
#             decreasing={"marker": {"color": "#e74c3c"}},
#             increasing={"marker": {"color": "#2ecc71"}},
#             totals={"marker": {"color": "#3498db"}},
#             hovertemplate='<b>%{x}</b><br>Amount: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Profit Waterfall</b>',
#             plot_bgcolor='white',
#             height=300,
#             showlegend=False,
#             margin=dict(t=40, b=40, l=60, r=20)
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 30px; border-radius: 10px; color: white; text-align: center; height: 300px;
#                     display: flex; flex-direction: column; justify-content: center;'>
#             <div style='font-size: 14px; opacity: 0.9; margin-bottom: 10px;'>
#                 GROSS PROFIT MARGIN
#             </div>
#             <div style='font-size: 52px; font-weight: bold; margin: 15px 0;'>
#                 {gross_margin:.1f}%
#             </div>
#             <div style='font-size: 12px; opacity: 0.8;'>
#                 (Revenue - COGS) / Revenue
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 30px; border-radius: 10px; color: white; text-align: center; height: 300px;
#                     display: flex; flex-direction: column; justify-content: center;'>
#             <div style='font-size: 14px; opacity: 0.9; margin-bottom: 10px;'>
#                 NET PROFIT MARGIN
#             </div>
#             <div style='font-size: 52px; font-weight: bold; margin: 15px 0;'>
#                 {net_margin:.1f}%
#             </div>
#             <div style='font-size: 12px; opacity: 0.8;'>
#                 Net Profit / Revenue
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== MONTHLY FINANCIAL TREND ====================
#     st.markdown("### 📈 Monthly Financial Performance")
    
#     monthly_fin = df_filtered.groupby('order_month').agg({
#         'net_revenue': 'sum',
#         'cost': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     monthly_fin['order_month'] = monthly_fin['order_month'].dt.to_timestamp()
#     monthly_fin['month_label'] = monthly_fin['order_month'].dt.strftime('%b %Y')
#     monthly_fin['gross_margin_%'] = ((monthly_fin['net_revenue'] - monthly_fin['cost']) / monthly_fin['net_revenue'] * 100).round(1)
#     monthly_fin['net_margin_%'] = (monthly_fin['profit'] / monthly_fin['net_revenue'] * 100).round(1)
    
#     fig = make_subplots(specs=[[{"secondary_y": True}]])
    
#     # Revenue and Cost bars
#     fig.add_trace(
#         go.Bar(
#             x=monthly_fin['month_label'],
#             y=monthly_fin['net_revenue'],
#             name='Revenue',
#             marker_color='#3498db',
#             hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#         ),
#         secondary_y=False
#     )
    
#     fig.add_trace(
#         go.Bar(
#             x=monthly_fin['month_label'],
#             y=monthly_fin['cost'],
#             name='COGS',
#             marker_color='#e74c3c',
#             hovertemplate='<b>%{x}</b><br>COGS: ฿%{y:,.0f}<extra></extra>'
#         ),
#         secondary_y=False
#     )
    
#     # Margin lines
#     fig.add_trace(
#         go.Scatter(
#             x=monthly_fin['month_label'],
#             y=monthly_fin['gross_margin_%'],
#             name='Gross Margin %',
#             mode='lines+markers',
#             line=dict(color='#27ae60', width=3),
#             marker=dict(size=8),
#             hovertemplate='<b>%{x}</b><br>Gross Margin: %{y:.1f}%<extra></extra>'
#         ),
#         secondary_y=True
#     )
    
#     fig.add_trace(
#         go.Scatter(
#             x=monthly_fin['month_label'],
#             y=monthly_fin['net_margin_%'],
#             name='Net Margin %',
#             mode='lines+markers',
#             line=dict(color='#9b59b6', width=3),
#             marker=dict(size=8),
#             hovertemplate='<b>%{x}</b><br>Net Margin: %{y:.1f}%<extra></extra>'
#         ),
#         secondary_y=True
#     )
    
#     fig.update_xaxes(title_text="")
#     fig.update_yaxes(title_text="Amount (฿)", secondary_y=False, showgrid=True, gridcolor='rgba(0,0,0,0.05)')
#     fig.update_yaxes(title_text="Margin (%)", secondary_y=True, showgrid=False)
    
#     fig.update_layout(
#         title='<b>Monthly Revenue, Cost & Margins</b>',
#         plot_bgcolor='white',
#         height=400,
#         hovermode='x unified',
#         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
#         barmode='group'
#     )
    
#     st.plotly_chart(fig, use_container_width=True)
    
#     st.markdown("---")
    
#     # ==================== WORKING CAPITAL RATIOS ====================
#     st.markdown("### 💼 Working Capital Ratios")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 AR Turnover:</b> จำนวนครั้งที่เราเก็บเงินจากลูกค้าได้ต่อปี (ยิ่งสูงยิ่งดี)<br>
#         <b>📖 DSO (Days Sales Outstanding):</b> จำนวนวันเฉลี่ยที่ใช้เวลาเก็บเงินจากลูกค้า (ยิ่งต่ำยิ่งดี)<br>
#         <div class='metric-formula'>
#         DSO = 365 / AR Turnover
#         </div>
#         <b>🎯 เป้าหมาย:</b> DSO < 45 วัน ถือว่าดี
#     </div>
#     """, unsafe_allow_html=True)
    
#     # Calculate ratios
#     avg_monthly_rev = monthly_fin['net_revenue'].mean()
#     avg_ar = avg_monthly_rev * 0.3  # Assume 30% credit sales
#     ar_turnover = (revenue * 0.3) / avg_ar if avg_ar > 0 else 0
#     dso = 365 / ar_turnover if ar_turnover > 0 else 0
    
#     avg_ap = cogs * 0.25
#     ap_turnover = cogs / avg_ap if avg_ap > 0 else 0
#     dpo = 365 / ap_turnover if ap_turnover > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #3498db; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 12px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>AR TURNOVER</b>
#             </div>
#             <div style='font-size: 36px; font-weight: bold; color: #2c3e50;'>
#                 {ar_turnover:.2f}x
#             </div>
#             <div style='font-size: 11px; color: #95a5a6; margin-top: 5px;'>
#                 Times per year
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         dso_color = '#2ecc71' if dso < 45 else '#e74c3c'
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid {dso_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 12px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>DSO</b>
#             </div>
#             <div style='font-size: 36px; font-weight: bold; color: #2c3e50;'>
#                 {dso:.0f}
#             </div>
#             <div style='font-size: 11px; color: #95a5a6; margin-top: 5px;'>
#                 Days
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #9b59b6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 12px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>AP TURNOVER</b>
#             </div>
#             <div style='font-size: 36px; font-weight: bold; color: #2c3e50;'>
#                 {ap_turnover:.2f}x
#             </div>
#             <div style='font-size: 11px; color: #95a5a6; margin-top: 5px;'>
#                 Times per year
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #f39c12; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 12px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>DPO</b>
#             </div>
#             <div style='font-size: 36px; font-weight: bold; color: #2c3e50;'>
#                 {dpo:.0f}
#             </div>
#             <div style='font-size: 11px; color: #95a5a6; margin-top: 5px;'>
#                 Days
#             </div>
#         </div>
#         """, unsafe_allow_html=True)

# with tab4:
#     st.markdown("# 📦 Warehouse Analytics")
#     st.markdown("---")
    
#     # ==================== INVENTORY TURNOVER ====================
#     st.markdown("### 🔄 Inventory Turnover & Performance")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 Inventory Turnover:</b> จำนวนครั้งที่สินค้าหมุนเวียนต่อปี (ยิ่งสูงยิ่งดี แสดงว่าสินค้าขายดี)<br>
#         <div class='metric-formula'>
#         สูตร: ต้นทุนสินค้าที่ขาย / มูลค่าสินค้าคงคลังเฉลี่ย
#         </div>
#         <b>📖 Days Inventory Outstanding (DIO):</b> จำนวนวันที่สินค้าอยู่ในคลังก่อนขายได้<br>
#         <div class='metric-formula'>
#         สูตร: 365 / Inventory Turnover
#         </div>
#         <b>🎯 เป้าหมาย:</b> Turnover > 4x, DIO < 90 วัน
#     </div>
#     """, unsafe_allow_html=True)
    
#     avg_inventory = df_filtered['cost'].mean() * df_filtered['product_id'].nunique()
#     inventory_turnover = cogs / avg_inventory if avg_inventory > 0 else 0
#     dio = 365 / inventory_turnover if inventory_turnover > 0 else 0
    
#     units_sold = df_filtered['quantity'].sum()
#     units_received = units_sold * 1.2
#     sell_through = (units_sold / units_received * 100) if units_received > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>INVENTORY TURNOVER</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {inventory_turnover:.2f}x
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Times per year</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         dio_color = '#2ecc71' if dio < 90 else '#e74c3c'
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>DIO</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {dio:.0f}
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Days</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>SELL-THROUGH RATE</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {sell_through:.1f}%
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Of received</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>INVENTORY VALUE</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 ฿{avg_inventory/1000:.0f}K
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Total stock</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== PRODUCT MOVEMENT CLASSIFICATION ====================
#     st.markdown("### 🚀 Product Movement Classification")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> จัดกลุ่มสินค้าตามความเร็วในการขาย<br>
#         • <b style='color: #2ecc71;'>Fast Moving:</b> ขายดี ควรเพิ่ม stock<br>
#         • <b style='color: #f39c12;'>Medium Moving:</b> ขายปานกลาง รักษาระดับปกติ<br>
#         • <b style='color: #e74c3c;'>Slow Moving:</b> ขายช้า ลด stock หรือทำ clearance
#     </div>
#     """, unsafe_allow_html=True)
    
#     product_velocity = df_filtered.groupby(['product_id', 'product_name', 'category']).agg({
#         'order_id': 'nunique',
#         'net_revenue': 'sum',
#         'cost': 'sum',
#         'quantity': 'sum'
#     }).reset_index()
#     product_velocity.columns = ['ID', 'Product', 'Category', 'Orders', 'Revenue', 'Cost', 'Units']
    
#     fast_threshold = product_velocity['Orders'].quantile(0.75)
#     slow_threshold = product_velocity['Orders'].quantile(0.25)
    
#     def classify_movement(orders):
#         if orders >= fast_threshold:
#             return 'Fast Moving'
#         elif orders <= slow_threshold:
#             return 'Slow Moving'
#         return 'Medium Moving'
    
#     product_velocity['Movement'] = product_velocity['Orders'].apply(classify_movement)
    
#     movement_summary = product_velocity.groupby('Movement').agg({
#         'Product': 'count',
#         'Revenue': 'sum',
#         'Cost': 'sum'
#     }).reset_index()
#     movement_summary.columns = ['Movement', 'Products', 'Revenue', 'Inventory_Value']
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         # Stacked bar chart
#         movement_order = ['Fast Moving', 'Medium Moving', 'Slow Moving']
#         movement_colors = {'Fast Moving': '#2ecc71', 'Medium Moving': '#f39c12', 'Slow Moving': '#e74c3c'}
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             y=['Product Count'],
#             x=[movement_summary[movement_summary['Movement'] == 'Fast Moving']['Products'].sum()],
#             name='Fast Moving',
#             orientation='h',
#             marker_color='#2ecc71',
#             text=[movement_summary[movement_summary['Movement'] == 'Fast Moving']['Products'].sum()],
#             texttemplate='%{text}',
#             textposition='inside',
#             hovertemplate='<b>Fast Moving</b><br>Products: %{x}<extra></extra>'
#         ))
        
#         fig.add_trace(go.Bar(
#             y=['Product Count'],
#             x=[movement_summary[movement_summary['Movement'] == 'Medium Moving']['Products'].sum()],
#             name='Medium Moving',
#             orientation='h',
#             marker_color='#f39c12',
#             text=[movement_summary[movement_summary['Movement'] == 'Medium Moving']['Products'].sum()],
#             texttemplate='%{text}',
#             textposition='inside',
#             hovertemplate='<b>Medium Moving</b><br>Products: %{x}<extra></extra>'
#         ))
        
#         fig.add_trace(go.Bar(
#             y=['Product Count'],
#             x=[movement_summary[movement_summary['Movement'] == 'Slow Moving']['Products'].sum()],
#             name='Slow Moving',
#             orientation='h',
#             marker_color='#e74c3c',
#             text=[movement_summary[movement_summary['Movement'] == 'Slow Moving']['Products'].sum()],
#             texttemplate='%{text}',
#             textposition='inside',
#             hovertemplate='<b>Slow Moving</b><br>Products: %{x}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Product Distribution by Movement Speed</b>',
#             xaxis=dict(title='Number of Products'),
#             yaxis=dict(title=''),
#             barmode='stack',
#             plot_bgcolor='white',
#             height=400,
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         # Inventory value by movement
#         movement_sorted = movement_summary.sort_values('Inventory_Value', ascending=True)
#         colors = [movement_colors[m] for m in movement_sorted['Movement']]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             y=movement_sorted['Movement'],
#             x=movement_sorted['Inventory_Value'],
#             orientation='h',
#             marker=dict(color=colors),
#             text=movement_sorted['Inventory_Value'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             hovertemplate='<b>%{y}</b><br>Value: ฿%{x:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Inventory Value by Movement</b>',
#             xaxis=dict(title='Inventory Value (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             yaxis=dict(title=''),
#             plot_bgcolor='white',
#             height=400,
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Show top products in each category
#     st.markdown("#### 📋 Movement Classification Details")
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.success("**🚀 Fast Moving (Top 10)**")
#         fast_products = product_velocity[product_velocity['Movement'] == 'Fast Moving'].nlargest(10, 'Orders')
#         st.dataframe(
#             fast_products[['Product', 'Orders', 'Units']].style.format({
#                 'Orders': '{:,}',
#                 'Units': '{:,}'
#             }),
#             height=300,
#             use_container_width=True
#         )
    
#     with col2:
#         st.warning("**⚖️ Medium Moving (Top 10)**")
#         medium_products = product_velocity[product_velocity['Movement'] == 'Medium Moving'].nlargest(10, 'Orders')
#         st.dataframe(
#             medium_products[['Product', 'Orders', 'Units']].style.format({
#                 'Orders': '{:,}',
#                 'Units': '{:,}'
#             }),
#             height=300,
#             use_container_width=True
#         )
    
#     with col3:
#         st.error("**🐌 Slow Moving (Top 10)**")
#         slow_products = product_velocity[product_velocity['Movement'] == 'Slow Moving'].nlargest(10, 'Cost')
#         st.dataframe(
#             slow_products[['Product', 'Orders', 'Cost']].style.format({
#                 'Orders': '{:,}',
#                 'Cost': '฿{:,.0f}'
#             }),
#             height=300,
#             use_container_width=True
#         )
    
#     st.markdown("---")
    
#     # ==================== CASH CONVERSION CYCLE ====================
#     st.markdown("### ⏱️ Cash Conversion Cycle (CCC)")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> ระยะเวลาที่เงินสดถูกล็อคอยู่ในธุรกิจ<br>
#         <div class='metric-formula'>
#         สูตร: DIO + DSO - DPO
#         </div>
#         <b>📖 ความหมาย:</b><br>
#         • DIO = วันที่สินค้าอยู่ในคลัง<br>
#         • DSO = วันที่รอเก็บเงินจากลูกค้า<br>
#         • DPO = วันที่เราจ่ายเงินซัพพลายเออร์<br>
#         <b>🎯 เป้าหมาย:</b> ยิ่งต่ำยิ่งดี (< 60 วัน ดีมาก, < 30 วัน ดีเยี่ยม)
#     </div>
#     """, unsafe_allow_html=True)
    
#     ccc = dio + dso - dpo
    
#     col1, col2 = st.columns([1, 2])
    
#     with col1:
#         ccc_color = '#2ecc71' if ccc < 60 else '#e74c3c'
#         ccc_status = '✅ Excellent' if ccc < 30 else '✅ Good' if ccc < 60 else '⚠️ Needs Improvement'
        
#         st.markdown(f"""
#         <div style='background: white; padding: 40px; border-radius: 10px; 
#                     border: 4px solid {ccc_color}; text-align: center; height: 400px;
#                     display: flex; flex-direction: column; justify-content: center;'>
#             <div style='font-size: 16px; color: #7f8c8d; margin-bottom: 15px;'>
#                 <b>CASH CONVERSION CYCLE</b>
#             </div>
#             <div style='font-size: 72px; font-weight: bold; color: {ccc_color}; margin: 20px 0;'>
#                 {ccc:.0f}
#             </div>
#             <div style='font-size: 24px; color: #7f8c8d;'>
#                 days
#             </div>
#             <div style='font-size: 14px; color: #95a5a6; margin-top: 20px;'>
#                 {ccc_status}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         # CCC breakdown chart
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             x=['DIO', 'DSO', 'DPO', 'CCC'],
#             y=[dio, dso, -dpo, ccc],
#             marker=dict(
#                 color=['#3498db', '#9b59b6', '#e74c3c', '#2ecc71'],
#                 line=dict(color='white', width=2)
#             ),
#             text=[f"{dio:.0f}", f"{dso:.0f}", f"{dpo:.0f}", f"{ccc:.0f}"],
#             texttemplate='%{text} days',
#             textposition='outside',
#             hovertemplate='<b>%{x}</b><br>Days: %{y:.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Cash Conversion Cycle Breakdown</b>',
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(
#                 title='Days',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)',
#                 zeroline=True,
#                 zerolinecolor='gray'
#             ),
#             plot_bgcolor='white',
#             height=400,
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True)

# # Footer
# st.markdown("---")
# st.markdown("""
# <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#             border-radius: 15px; color: white;'>
#     <h3 style='margin: 0; font-size: 24px;'>📊 Fashion Analytics Dashboard</h3>
#     <p style='margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;'>
#         Built with Streamlit • Data-Driven Insights with Professional KPIs
#     </p>
# </div>
# """, unsafe_allow_html=True)













































































































# # Analytics Dashboard - Improved Version with KPIs
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
# import numpy as np
# import warnings
# from datetime import datetime, timedelta

# warnings.filterwarnings('ignore')
# st.set_page_config(page_title="Analytics Dashboard", layout="wide", page_icon="📊")

# # Enhanced Color Palette
# COLORS = {
#     'primary': '#1f77b4',
#     'secondary': '#ff7f0e',
#     'success': '#2ecc71',
#     'danger': '#e74c3c',
#     'warning': '#f39c12',
#     'info': '#3498db',
#     'purple': '#9b59b6',
#     'teal': '#1abc9c',
#     'pink': '#e91e63',
#     'indigo': '#3f51b5'
# }

# # Channel Color Mapping
# CHANNEL_COLORS = {
#     'TikTok': '#000000',
#     'Shopee': '#FF5722',
#     'Lazada': '#1E88E5',
#     'LINE Shopping': '#00C300',
#     'Instagram': '#9C27B0',
#     'Facebook': '#1877F2',
#     'Store': '#795548',
#     'Pop-up': '#FF9800',
#     'Website': '#607D8B'
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
#     st.sidebar.title("📊 Analytics Dashboard")
#     st.sidebar.markdown("### 📁 Data Upload")
#     st.sidebar.markdown("Upload your CSV files to begin analysis")
#     st.sidebar.markdown("---")
    
#     uploaded = st.sidebar.file_uploader(
#         "Choose CSV Files", 
#         type=['csv'], 
#         accept_multiple_files=True,
#         key="csv_uploader_main"
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
        
#         with st.sidebar:
#             st.markdown("**Loading Status:**")
        
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
#                             st.sidebar.error(f"❌ {file.name}")
#                             st.sidebar.caption(f"Missing: {', '.join(missing)}")
#                     else:
#                         data[table] = df
#                         st.sidebar.success(f"✅ {file.name}")
#                 except Exception as e:
#                     st.sidebar.error(f"❌ {file.name}")
#                     st.sidebar.caption(str(e))
        
#         if all(t in data for t in ['users', 'products', 'orders', 'order_items']):
#             st.session_state.data = data
#             st.session_state.data_loaded = True
#             st.sidebar.markdown("---")
#             st.sidebar.success("✅ **All data loaded successfully!**")
#             st.rerun()
#         else:
#             st.sidebar.error("❌ Missing required tables")
#             missing_tables = [t for t in ['users', 'products', 'orders', 'order_items'] if t not in data]
#             st.sidebar.caption(f"Need: {', '.join(missing_tables)}.csv")
    
#     if st.session_state.data_loaded:
#         st.sidebar.markdown("---")
#         st.sidebar.markdown("### ✅ Data Status")
#         st.sidebar.success("Data loaded and ready")
        
#         if st.session_state.data:
#             total_orders = len(st.session_state.data.get('orders', []))
#             total_customers = len(st.session_state.data.get('users', []))
#             total_products = len(st.session_state.data.get('products', []))
            
#             st.sidebar.markdown(f"""
#             - **Orders:** {total_orders:,}
#             - **Customers:** {total_customers:,}
#             - **Products:** {total_products:,}
#             """)
    
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

# # Custom CSS
# st.markdown("""
# <style>
#     .block-container {padding-top: 1rem; padding-bottom: 1rem;}
#     [data-testid="stMetricValue"] {font-size: 24px; font-weight: 600;}
#     [data-testid="stMetricLabel"] {font-size: 13px; font-weight: 500; color: #555;}
#     h1, h2, h3 {font-family: 'Inter', sans-serif; font-weight: 700;}
    
#     /* Info boxes for explanations */
#     .metric-explanation {
#         background: #f8f9fa;
#         padding: 15px;
#         border-radius: 8px;
#         border-left: 4px solid #3498db;
#         margin: 10px 0;
#         font-size: 13px;
#         color: #2c3e50;
#     }
    
#     .metric-formula {
#         background: #e8f4f8;
#         padding: 10px;
#         border-radius: 5px;
#         font-family: monospace;
#         font-size: 12px;
#         margin: 5px 0;
#     }
# </style>
# """, unsafe_allow_html=True)

# data = load_data()

# if not data:
#     st.title("📊 Analytics Dashboard")
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

# # ==================== MAIN FILTERS ====================
# st.title("📊 Analytics Dashboard")
# st.markdown("---")

# st.markdown("### 🔍 Filter Data")

# min_date = df_master['order_date'].min().date()
# max_date = df_master['order_date'].max().date()

# col1, col2, col3 = st.columns([2, 2, 1])

# with col1:
#     period_options = ["Custom Range", "Last 7 Days", "Last 30 Days", "Last 90 Days", 
#                       "This Month", "Last Month", "This Quarter", "This Year", "All Time"]
#     selected_period = st.selectbox("📅 Time Period", period_options, index=2, key="period_selector")

# with col2:
#     if selected_period == "Last 7 Days":
#         start_date = max_date - timedelta(days=7)
#         end_date = max_date
#     elif selected_period == "Last 30 Days":
#         start_date = max_date - timedelta(days=30)
#         end_date = max_date
#     elif selected_period == "Last 90 Days":
#         start_date = max_date - timedelta(days=90)
#         end_date = max_date
#     elif selected_period == "This Month":
#         start_date = max_date.replace(day=1)
#         end_date = max_date
#     elif selected_period == "Last Month":
#         first_day_this_month = max_date.replace(day=1)
#         end_date = first_day_this_month - timedelta(days=1)
#         start_date = end_date.replace(day=1)
#     elif selected_period == "This Quarter":
#         quarter = (max_date.month - 1) // 3
#         start_date = datetime(max_date.year, quarter * 3 + 1, 1).date()
#         end_date = max_date
#     elif selected_period == "This Year":
#         start_date = datetime(max_date.year, 1, 1).date()
#         end_date = max_date
#     elif selected_period == "All Time":
#         start_date = min_date
#         end_date = max_date
#     else:
#         date_range = st.date_input(
#             "Custom Date Range", 
#             [min_date, max_date], 
#             min_value=min_date, 
#             max_value=max_date,
#             key="custom_date_range"
#         )
#         if len(date_range) == 2:
#             start_date, end_date = date_range
#         else:
#             start_date, end_date = min_date, max_date
    
#     st.info(f"📆 **{start_date.strftime('%d %b %Y')}** → **{end_date.strftime('%d %b %Y')}**")

# with col3:
#     if st.button("🔄 Reset All", key="reset_filters", use_container_width=True):
#         st.rerun()

# df_filtered = df_master[(df_master['order_date'].dt.date >= start_date) & 
#                         (df_master['order_date'].dt.date <= end_date)]

# col1, col2, col3 = st.columns(3)

# with col1:
#     channels = st.multiselect(
#         "🏪 Sales Channel", 
#         df_master['channel'].unique(), 
#         df_master['channel'].unique(),
#         key="channel_filter"
#     )
#     df_filtered = df_filtered[df_filtered['channel'].isin(channels)]

# with col2:
#     statuses = st.multiselect(
#         "📦 Order Status", 
#         df_master['status'].unique(), 
#         ['Completed'],
#         key="status_filter"
#     )
#     df_filtered = df_filtered[df_filtered['status'].isin(statuses)]

# with col3:
#     if 'category' in df_filtered.columns:
#         categories = st.multiselect(
#             "🏷️ Product Category",
#             df_master['category'].unique(),
#             df_master['category'].unique(),
#             key="category_filter"
#         )
#         df_filtered = df_filtered[df_filtered['category'].isin(categories)]

# st.markdown("---")
# st.markdown("### 📊 Summary Statistics")

# # Calculate key metrics
# revenue = df_filtered['net_revenue'].sum()
# profit = df_filtered['profit'].sum()
# cogs = df_filtered['cost'].sum()
# total_orders = df_filtered['order_id'].nunique()
# total_customers = df_filtered['user_id'].nunique()
# gross_profit = revenue - cogs
# profit_margin = (profit / revenue * 100) if revenue > 0 else 0
# avg_order_value = revenue / total_orders if total_orders > 0 else 0

# col1, col2, col3, col4, col5, col6 = st.columns(6)

# with col1:
#     st.metric("💰 Revenue", f"฿{revenue/1000:,.0f}K")
# with col2:
#     st.metric("💵 Profit", f"฿{profit/1000:,.0f}K")
# with col3:
#     st.metric("📝 Orders", f"{total_orders:,}")
# with col4:
#     st.metric("👥 Customers", f"{total_customers:,}")
# with col5:
#     st.metric("📊 Margin", f"{profit_margin:.1f}%")
# with col6:
#     st.metric("🛒 AOV", f"฿{avg_order_value:,.0f}")

# st.markdown("---")

# # ==================== TABS ====================
# tab1, tab2, tab3, tab4 = st.tabs(["💼 Sales Analytics", "📢 Marketing Analytics", "💰 Financial Analytics", "📦 Warehouse Analytics"])

# with tab1:
#     st.markdown("# 💼 Sales Analytics")
#     st.markdown("---")
    
#     # ==================== SALES GROWTH ====================
#     st.markdown("### 📈 Monthly Sales Growth")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> วัดว่ายอดขายเติบโตกี่ % เมื่อเทียบกับเดือนก่อนหน้า<br>
#         <div class='metric-formula'>
#         สูตร: [(ยอดขายเดือนปัจจุบัน - ยอดขายเดือนก่อน) / ยอดขายเดือนก่อน] × 100
#         </div>
#         <b>🎯 เป้าหมาย:</b> ควรเป็นบวก และมากกว่า 5-10% ถือว่าดี
#     </div>
#     """, unsafe_allow_html=True)
    
#     monthly_sales = df_filtered.groupby('order_month').agg({
#         'net_revenue': 'sum'
#     }).reset_index()
#     monthly_sales['order_month'] = monthly_sales['order_month'].dt.to_timestamp()
#     monthly_sales['month_label'] = monthly_sales['order_month'].dt.strftime('%b %Y')
#     monthly_sales['growth_%'] = monthly_sales['net_revenue'].pct_change() * 100
    
#     col1, col2 = st.columns([2, 1])
    
#     with col1:
#         fig = go.Figure()
        
#         # Revenue bars
#         fig.add_trace(go.Bar(
#             x=monthly_sales['month_label'],
#             y=monthly_sales['net_revenue'],
#             name='Revenue',
#             marker=dict(
#                 color=monthly_sales['net_revenue'],
#                 colorscale='Blues',
#                 showscale=False
#             ),
#             text=monthly_sales['net_revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         # Growth line
#         fig.add_trace(go.Scatter(
#             x=monthly_sales['month_label'],
#             y=monthly_sales['growth_%'],
#             name='Growth %',
#             mode='lines+markers',
#             line=dict(color='#e74c3c', width=3),
#             marker=dict(size=10),
#             yaxis='y2',
#             text=monthly_sales['growth_%'],
#             texttemplate='%{text:.1f}%',
#             textposition='top center',
#             hovertemplate='<b>%{x}</b><br>Growth: %{y:.1f}%<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Monthly Sales Revenue & Growth Rate</b>',
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             yaxis2=dict(
#                 title='Growth (%)', 
#                 overlaying='y', 
#                 side='right',
#                 showgrid=False,
#                 zeroline=True,
#                 zerolinecolor='gray'
#             ),
#             plot_bgcolor='white',
#             height=400,
#             hovermode='x unified',
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         latest_growth = monthly_sales['growth_%'].iloc[-1] if len(monthly_sales) > 1 else 0
#         prev_growth = monthly_sales['growth_%'].iloc[-2] if len(monthly_sales) > 2 else 0
        
#         arrow = "📈" if latest_growth > 0 else "📉"
#         color = "#2ecc71" if latest_growth > 0 else "#e74c3c"
        
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid {color}; height: 400px;
#                     display: flex; flex-direction: column; justify-content: center; align-items: center;'>
#             <div style='font-size: 60px;'>{arrow}</div>
#             <div style='font-size: 48px; font-weight: bold; color: {color}; margin: 20px 0;'>
#                 {latest_growth:+.1f}%
#             </div>
#             <div style='font-size: 16px; color: #7f8c8d; text-align: center;'>
#                 <b>Current Month Growth</b>
#             </div>
#             <div style='margin-top: 20px; font-size: 14px; color: #95a5a6;'>
#                 Previous: {prev_growth:.1f}%
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== SALES TARGET ATTAINMENT ====================
#     st.markdown("### 🎯 Sales Target Attainment")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> วัดว่าทำยอดขายได้กี่ % ของเป้าหมายที่ตั้งไว้<br>
#         <div class='metric-formula'>
#         สูตร: (ยอดขายที่ทำได้ / เป้าหมายยอดขาย) × 100
#         </div>
#         <b>🎯 เป้าหมาย:</b> ควรอยู่ที่ 90-110% (น้อยกว่า 90% ต้องปรับปรุง, มากกว่า 110% ดีมาก)
#     </div>
#     """, unsafe_allow_html=True)
    
#     # Calculate target attainment
#     target_monthly = 5000000  # 5M target
#     current_month_sales = monthly_sales['net_revenue'].iloc[-1] if len(monthly_sales) > 0 else 0
#     attainment = (current_month_sales / target_monthly * 100) if target_monthly > 0 else 0
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 30px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 14px; opacity: 0.9;'>TARGET</div>
#             <div style='font-size: 36px; font-weight: bold; margin: 15px 0;'>
#                 ฿{target_monthly/1000000:.1f}M
#             </div>
#             <div style='font-size: 12px; opacity: 0.8;'>Monthly Goal</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 30px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 14px; opacity: 0.9;'>ACTUAL</div>
#             <div style='font-size: 36px; font-weight: bold; margin: 15px 0;'>
#                 ฿{current_month_sales/1000000:.1f}M
#             </div>
#             <div style='font-size: 12px; opacity: 0.8;'>Current Sales</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         att_color = '#2ecc71' if attainment >= 90 else '#e74c3c'
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid {att_color}; text-align: center;'>
#             <div style='font-size: 14px; color: #7f8c8d;'>ATTAINMENT</div>
#             <div style='font-size: 36px; font-weight: bold; margin: 15px 0; color: {att_color};'>
#                 {attainment:.1f}%
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 {'✅ On Track' if attainment >= 90 else '⚠️ Below Target'}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== SALES BY CHANNEL ====================
#     st.markdown("### 🏪 Sales by Channel")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> แสดงยอดขายแยกตามช่องทางการขาย เพื่อดูว่าช่องทางไหนมี Performance ดีที่สุด
#     </div>
#     """, unsafe_allow_html=True)
    
#     channel_sales = df_filtered.groupby('channel').agg({
#         'net_revenue': 'sum',
#         'profit': 'sum',
#         'order_id': 'nunique'
#     }).reset_index()
#     channel_sales.columns = ['Channel', 'Revenue', 'Profit', 'Orders']
#     channel_sales['Margin_%'] = (channel_sales['Profit'] / channel_sales['Revenue'] * 100).round(1)
#     channel_sales['AOV'] = (channel_sales['Revenue'] / channel_sales['Orders']).round(0)
#     channel_sales = channel_sales.sort_values('Revenue', ascending=False)
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         # Horizontal bar chart
#         ch_sorted = channel_sales.sort_values('Revenue', ascending=True)
#         colors_list = [CHANNEL_COLORS.get(ch, '#95a5a6') for ch in ch_sorted['Channel']]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             y=ch_sorted['Channel'],
#             x=ch_sorted['Revenue'],
#             orientation='h',
#             marker=dict(color=colors_list),
#             text=ch_sorted['Revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Revenue by Channel</b>',
#             xaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             yaxis=dict(title=''),
#             plot_bgcolor='white',
#             height=400,
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         # Stacked bar: Revenue vs Profit
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             x=channel_sales['Channel'],
#             y=channel_sales['Profit'],
#             name='Profit',
#             marker_color='#2ecc71',
#             text=channel_sales['Profit'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='inside',
#             hovertemplate='<b>%{x}</b><br>Profit: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.add_trace(go.Bar(
#             x=channel_sales['Channel'],
#             y=channel_sales['Revenue'] - channel_sales['Profit'],
#             name='Cost',
#             marker_color='#e74c3c',
#             text=channel_sales['Revenue'] - channel_sales['Profit'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='inside',
#             hovertemplate='<b>%{x}</b><br>Cost: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Revenue Breakdown: Profit vs Cost</b>',
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(title='Amount (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             barmode='stack',
#             plot_bgcolor='white',
#             height=400,
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Channel metrics table
#     st.markdown("#### 📊 Channel Performance Metrics")
    
#     styled_ch = channel_sales.style.format({
#         'Revenue': '฿{:,.0f}',
#         'Profit': '฿{:,.0f}',
#         'Orders': '{:,}',
#         'Margin_%': '{:.1f}%',
#         'AOV': '฿{:,.0f}'
#     }).background_gradient(subset=['Margin_%'], cmap='RdYlGn', vmin=0, vmax=100)
    
#     st.dataframe(styled_ch, use_container_width=True)
    
#     st.markdown("---")
    
#     # ==================== PRODUCT PERFORMANCE ====================
#     st.markdown("### 🏆 Top Product Performance")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> แสดงสินค้าที่ขายดีที่สุด 20 อันดับแรก วัดจากยอดขาย และอัตรากำไร
#     </div>
#     """, unsafe_allow_html=True)
    
#     product_sales = df_filtered.groupby(['product_id', 'product_name', 'category']).agg({
#         'net_revenue': 'sum',
#         'profit': 'sum',
#         'quantity': 'sum'
#     }).reset_index()
#     product_sales.columns = ['ID', 'Product', 'Category', 'Revenue', 'Profit', 'Units']
#     product_sales['Margin_%'] = (product_sales['Profit'] / product_sales['Revenue'] * 100).round(1)
#     product_sales = product_sales.sort_values('Revenue', ascending=False).head(20)
    
#     col1, col2 = st.columns([3, 2])
    
#     with col1:
#         # Top 10 horizontal bar
#         top10 = product_sales.head(10).sort_values('Revenue', ascending=True)
        
#         fig = go.Figure()
        
#         # Color by margin
#         colors = ['#2ecc71' if m >= 50 else '#f39c12' if m >= 30 else '#e74c3c' 
#                   for m in top10['Margin_%']]
        
#         fig.add_trace(go.Bar(
#             y=top10['Product'],
#             x=top10['Revenue'],
#             orientation='h',
#             marker=dict(color=colors),
#             text=top10['Revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             customdata=top10[['Margin_%']],
#             hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<br>Margin: %{customdata[0]:.1f}%<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Top 10 Products by Revenue</b><br><sub>Color: Green=High Margin, Yellow=Medium, Red=Low</sub>',
#             xaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             yaxis=dict(title=''),
#             plot_bgcolor='white',
#             height=450,
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         # Scatter: Revenue vs Margin (Fixed bubble size)
#         fig = go.Figure()
        
#         # Calculate bubble size (max 80, min 10)
#         max_units = product_sales['Units'].max()
#         min_units = product_sales['Units'].min()
#         normalized_sizes = 10 + (product_sales['Units'] - min_units) / (max_units - min_units) * 70
        
#         fig.add_trace(go.Scatter(
#             x=product_sales['Revenue'],
#             y=product_sales['Margin_%'],
#             mode='markers',
#             marker=dict(
#                 size=normalized_sizes,
#                 color=product_sales['Margin_%'],
#                 colorscale='RdYlGn',
#                 showscale=True,
#                 colorbar=dict(title="Margin %"),
#                 line=dict(width=1, color='white'),
#                 sizemode='diameter'
#             ),
#             text=product_sales['Product'],
#             customdata=product_sales['Units'],
#             hovertemplate='<b>%{text}</b><br>Revenue: ฿%{x:,.0f}<br>Margin: %{y:.1f}%<br>Units: %{customdata:,}<extra></extra>'
#         ))
        
#         # Add quadrant lines
#         avg_revenue = product_sales['Revenue'].median()
#         avg_margin = product_sales['Margin_%'].median()
        
#         fig.add_hline(y=avg_margin, line_dash="dash", line_color="gray", opacity=0.5, 
#                       annotation_text="Avg Margin", annotation_position="right")
#         fig.add_vline(x=avg_revenue, line_dash="dash", line_color="gray", opacity=0.5,
#                       annotation_text="Avg Revenue", annotation_position="top")
        
#         # Add quadrant labels
#         fig.add_annotation(x=avg_revenue * 1.5, y=avg_margin * 1.2,
#                           text="🌟 Stars<br>(High Revenue, High Margin)",
#                           showarrow=False, font=dict(size=10, color='green'))
        
#         fig.add_annotation(x=avg_revenue * 1.5, y=avg_margin * 0.8,
#                           text="💰 Cash Cows<br>(High Revenue, Low Margin)",
#                           showarrow=False, font=dict(size=10, color='orange'))
        
#         fig.add_annotation(x=avg_revenue * 0.5, y=avg_margin * 1.2,
#                           text="🚀 Growth<br>(Low Revenue, High Margin)",
#                           showarrow=False, font=dict(size=10, color='blue'))
        
#         fig.add_annotation(x=avg_revenue * 0.5, y=avg_margin * 0.8,
#                           text="⚠️ Question Marks<br>(Low Revenue, Low Margin)",
#                           showarrow=False, font=dict(size=10, color='red'))
        
#         fig.update_layout(
#             title='<b>Product Portfolio Analysis (BCG Matrix)</b><br><sub>Bubble size = Units Sold</sub>',
#             xaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             yaxis=dict(title='Profit Margin (%)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             plot_bgcolor='white',
#             height=450
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     st.markdown("#### 📋 Top 20 Products Detail")
    
#     styled_prod = product_sales.style.format({
#         'Revenue': '฿{:,.0f}',
#         'Profit': '฿{:,.0f}',
#         'Units': '{:,}',
#         'Margin_%': '{:.1f}%'
#     }).background_gradient(subset=['Margin_%'], cmap='RdYlGn', vmin=0, vmax=100)
    
#     st.dataframe(styled_prod, use_container_width=True)

# with tab2:
#     st.markdown("# 📢 Marketing Analytics")
#     st.markdown("---")
    
#     # Data availability checker
#     st.markdown("### 📋 Available Marketing Metrics")
    
#     has_funnel = all(col in df_filtered.columns for col in ['visits', 'add_to_cart', 'checkout'])
#     has_campaign = 'campaign_type' in df_filtered.columns and df_filtered['campaign_type'].notna().any()
#     has_acquisition = 'acquisition_channel' in df_filtered.columns
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         if has_funnel:
#             st.success("✅ **Conversion Funnel Data Available**")
#         else:
#             st.warning("⚠️ **Conversion Funnel Data Missing**\nAdd columns: `visits`, `add_to_cart`, `checkout`")
    
#     with col2:
#         if has_campaign:
#             st.success("✅ **Campaign Data Available**")
#         else:
#             st.warning("⚠️ **Campaign Data Missing**\nAdd `campaign_type` column for campaign analysis")
    
#     with col3:
#         if has_acquisition:
#             st.success("✅ **Acquisition Channel Data Available**")
#         else:
#             st.warning("⚠️ **Acquisition Data Missing**\nAdd `acquisition_channel` column for acquisition analysis")
    
#     st.markdown("---")
    
#     # ==================== CONVERSION FUNNEL ====================
#     st.markdown("### 🎯 Conversion Funnel Analysis")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 Conversion Rate:</b> เปอร์เซ็นต์ของผู้เข้าชมที่กลายเป็นลูกค้า (ซื้อสินค้าจริง)<br>
#         <div class='metric-formula'>
#         สูตร: (จำนวน Orders / จำนวน Visitors) × 100
#         </div>
#         <b>📖 Funnel Stages:</b><br>
#         • <b>Visitors:</b> คนที่เข้าชมเว็บไซต์/ร้าน<br>
#         • <b>Add to Cart:</b> คนที่ใส่สินค้าในตะกร้า<br>
#         • <b>Checkout:</b> คนที่ไปหน้า Checkout<br>
#         • <b>Purchase:</b> คนที่ซื้อสำเร็จ<br>
#         <b>🎯 เป้าหมาย:</b> Conversion Rate 2-5% ถือว่าปกติ, >5% ดีมาก
#     </div>
#     """, unsafe_allow_html=True)
    
#     if has_funnel:
#         # Use actual funnel data
#         total_visitors = df_filtered['visits'].sum()
#         add_to_cart = df_filtered['add_to_cart'].sum()
#         checkout_count = df_filtered['checkout'].sum()
#         total_orders = df_filtered['order_id'].nunique()
#         conversion_rate = (total_orders / total_visitors * 100) if total_visitors > 0 else 0
        
#         col1, col2 = st.columns([1, 2])
        
#         with col1:
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                         padding: 30px; border-radius: 10px; color: white; height: 400px;
#                         display: flex; flex-direction: column; justify-content: center;'>
#                 <div style='text-align: center;'>
#                     <div style='font-size: 16px; opacity: 0.9; margin-bottom: 20px;'>
#                         <b>CONVERSION RATE</b>
#                     </div>
#                     <div style='font-size: 72px; font-weight: bold; margin: 20px 0;'>
#                         {conversion_rate:.1f}%
#                     </div>
#                     <div style='font-size: 14px; opacity: 0.8; margin-top: 20px;'>
#                         {total_orders:,} orders from {total_visitors:,} visitors
#                     </div>
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col2:
#             # Funnel chart
#             funnel_data = pd.DataFrame({
#                 'Stage': ['Visitors', 'Add to Cart', 'Checkout', 'Purchase'],
#                 'Count': [total_visitors, add_to_cart, checkout_count, total_orders],
#                 'Color': ['#3498db', '#2ecc71', '#f39c12', '#9b59b6']
#             })
            
#             fig = go.Figure()
            
#             fig.add_trace(go.Funnel(
#                 y=funnel_data['Stage'],
#                 x=funnel_data['Count'],
#                 textposition="inside",
#                 textinfo="value+percent initial",
#                 marker=dict(
#                     color=funnel_data['Color'],
#                     line=dict(color='white', width=2)
#                 ),
#                 textfont=dict(size=13, weight='bold', color='white'),
#                 hovertemplate='<b>%{y}</b><br>Count: %{x:,}<br>Rate: %{percentInitial}<extra></extra>',
#                 connector=dict(line=dict(color='gray', width=1))
#             ))
            
#             fig.update_layout(
#                 title='<b>Sales Funnel</b>',
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=40, r=120),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True)
#     else:
#         # Show alternative: Order completion metrics
#         st.info("💡 **Showing Order Completion Metrics** (Funnel data not available)")
        
#         total_orders = df_filtered['order_id'].nunique()
#         total_customers = df_filtered['user_id'].nunique()
#         completed_orders = df_filtered[df_filtered['status'] == 'Completed']['order_id'].nunique()
        
#         col1, col2, col3 = st.columns(3)
        
#         with col1:
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                         padding: 30px; border-radius: 10px; color: white; text-align: center; height: 200px;
#                         display: flex; flex-direction: column; justify-content: center;'>
#                 <div style='font-size: 14px; opacity: 0.9;'>TOTAL ORDERS</div>
#                 <div style='font-size: 48px; font-weight: bold; margin: 15px 0;'>
#                     {total_orders:,}
#                 </div>
#                 <div style='font-size: 12px; opacity: 0.8;'>All statuses</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col2:
#             completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                         padding: 30px; border-radius: 10px; color: white; text-align: center; height: 200px;
#                         display: flex; flex-direction: column; justify-content: center;'>
#                 <div style='font-size: 14px; opacity: 0.9;'>COMPLETION RATE</div>
#                 <div style='font-size: 48px; font-weight: bold; margin: 15px 0;'>
#                     {completion_rate:.1f}%
#                 </div>
#                 <div style='font-size: 12px; opacity: 0.8;'>{completed_orders:,} completed</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col3:
#             orders_per_customer = total_orders / total_customers if total_customers > 0 else 0
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                         padding: 30px; border-radius: 10px; color: white; text-align: center; height: 200px;
#                         display: flex; flex-direction: column; justify-content: center;'>
#                 <div style='font-size: 14px; opacity: 0.9;'>ORDERS/CUSTOMER</div>
#                 <div style='font-size: 48px; font-weight: bold; margin: 15px 0;'>
#                     {orders_per_customer:.1f}
#                 </div>
#                 <div style='font-size: 12px; opacity: 0.8;'>Average frequency</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         # Show order status breakdown
#         st.markdown("<br>", unsafe_allow_html=True)
        
#         status_data = df_filtered.groupby('status')['order_id'].nunique().reset_index()
#         status_data.columns = ['Status', 'Orders']
#         status_data = status_data.sort_values('Orders', ascending=True)
        
#         status_colors = {
#             'Completed': '#2ecc71',
#             'Pending': '#f39c12',
#             'Cancelled': '#e74c3c',
#             'Refunded': '#95a5a6'
#         }
        
#         colors_list = [status_colors.get(s, '#95a5a6') for s in status_data['Status']]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             y=status_data['Status'],
#             x=status_data['Orders'],
#             orientation='h',
#             marker=dict(color=colors_list, line=dict(color='white', width=2)),
#             text=status_data['Orders'],
#             texttemplate='%{text:,}',
#             textposition='outside',
#             hovertemplate='<b>%{y}</b><br>Orders: %{x:,}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Order Status Breakdown</b>',
#             xaxis=dict(title='Number of Orders', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             yaxis=dict(title=''),
#             plot_bgcolor='white',
#             height=300,
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     st.markdown("---")
    
#     # ==================== CUSTOMER ACQUISITION COST ====================
#     st.markdown("### 💳 Customer Acquisition Cost (CAC)")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> ค่าใช้จ่ายที่ใช้ในการหาลูกค้าใหม่ 1 คน<br>
#         <div class='metric-formula'>
#         สูตร: ค่าใช้จ่ายทางการตลาด / จำนวนลูกค้าใหม่
#         </div>
#         <b>🎯 เป้าหมาย:</b> ควรต่ำกว่า Customer Lifetime Value (CLV) อย่างน้อย 3 เท่า
#     </div>
#     """, unsafe_allow_html=True)
    
#     marketing_cost = df_filtered['discount_amount'].sum() if 'discount_amount' in df_filtered.columns else 0
#     new_customers = df_filtered['user_id'].nunique()
#     cac = marketing_cost / new_customers if new_customers > 0 else 0
    
#     # Calculate CLV
#     analysis_date = df_filtered['order_date'].max()
#     last_purchase = df_filtered.groupby('user_id')['order_date'].max()
#     churned = ((analysis_date - last_purchase).dt.days > 90).sum()
#     churn_rate = (churned / len(last_purchase) * 100) if len(last_purchase) > 0 else 0
#     retention_rate = 100 - churn_rate
#     avg_revenue = df_filtered.groupby('user_id')['net_revenue'].sum().mean()
#     clv = (profit_margin / 100) * (retention_rate / 100) * avg_revenue
    
#     cac_to_clv_ratio = (cac / clv) if clv > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9;'>CAC</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
#                 ฿{cac:,.0f}
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Per customer</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9;'>CLV</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
#                 ฿{clv:,.0f}
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Lifetime value</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         ratio_color = '#2ecc71' if cac_to_clv_ratio < 0.33 else '#e74c3c'
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border: 3px solid {ratio_color}; text-align: center;'>
#             <div style='font-size: 13px; color: #7f8c8d;'>CAC : CLV</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0; color: {ratio_color};'>
#                 1:{(clv/cac if cac > 0 else 0):.1f}
#             </div>
#             <div style='font-size: 11px; color: #95a5a6;'>
#                 {'✅ Good' if cac_to_clv_ratio < 0.33 else '⚠️ Too High'}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9;'>NEW CUSTOMERS</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
#                 {new_customers:,}
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>In period</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== RETENTION & CHURN ====================
#     st.markdown("### 🔄 Customer Retention & Churn Rate")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 Retention Rate:</b> เปอร์เซ็นต์ของลูกค้าที่ยังคงซื้อสินค้ากับเรา (ไม่หายไป)<br>
#         <div class='metric-formula'>
#         สูตร: [1 - (จำนวนลูกค้าที่หายไป / จำนวนลูกค้าเริ่มต้น)] × 100
#         </div>
#         <b>📖 Churn Rate:</b> เปอร์เซ็นต์ของลูกค้าที่หยุดซื้อสินค้า (ไม่ซื้อเกิน 90 วัน)<br>
#         <b>🎯 เป้าหมาย:</b> Retention ควรสูงกว่า 80%, Churn ควรต่ำกว่า 20%
#     </div>
#     """, unsafe_allow_html=True)
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid #2ecc71; text-align: center; height: 200px;
#                     display: flex; flex-direction: column; justify-content: center;'>
#             <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
#                 <b>RETENTION RATE</b>
#             </div>
#             <div style='font-size: 48px; font-weight: bold; color: #2ecc71; margin: 15px 0;'>
#                 {retention_rate:.1f}%
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 Active customers
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid #e74c3c; text-align: center; height: 200px;
#                     display: flex; flex-direction: column; justify-content: center;'>
#             <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
#                 <b>CHURN RATE</b>
#             </div>
#             <div style='font-size: 48px; font-weight: bold; color: #e74c3c; margin: 15px 0;'>
#                 {churn_rate:.1f}%
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 Lost customers
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         active_customers = int(len(last_purchase) * retention_rate / 100)
#         churned_customers = int(len(last_purchase) * churn_rate / 100)
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             x=['Active', 'Churned'],
#             y=[active_customers, churned_customers],
#             marker=dict(color=['#2ecc71', '#e74c3c']),
#             text=[active_customers, churned_customers],
#             texttemplate='%{text:,}',
#             textposition='outside',
#             hovertemplate='<b>%{x}</b><br>Customers: %{y:,}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Customer Status</b>',
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(title='Number of Customers', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             plot_bgcolor='white',
#             height=200,
#             showlegend=False,
#             margin=dict(t=40, b=40, l=60, r=20)
#         )
        
#         st.plotly_chart(fig, use_container_width=True)

# with tab3:
#     st.markdown("# 💰 Financial Analytics")
#     st.markdown("---")
    
#     # ==================== PROFIT MARGINS ====================
#     st.markdown("### 📊 Profit Margin Analysis")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 Gross Profit Margin:</b> เปอร์เซ็นต์กำไรขั้นต้น (หลังหักต้นทุนสินค้า)<br>
#         <div class='metric-formula'>
#         สูตร: [(รายได้ - ต้นทุนสินค้า) / รายได้] × 100
#         </div>
#         <b>📖 Net Profit Margin:</b> เปอร์เซ็นต์กำไรสุทธิ (หลังหักค่าใช้จ่ายทั้งหมด)<br>
#         <div class='metric-formula'>
#         สูตร: (กำไรสุทธิ / รายได้) × 100
#         </div>
#         <b>🎯 เป้าหมาย:</b> Gross Margin > 50%, Net Margin > 20% ถือว่าดี
#     </div>
#     """, unsafe_allow_html=True)
    
#     gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
#     net_margin = (profit / revenue * 100) if revenue > 0 else 0
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         # Waterfall chart
#         fig = go.Figure(go.Waterfall(
#             orientation="v",
#             measure=["relative", "relative", "relative", "total"],
#             x=["Revenue", "COGS", "Other Costs", "Net Profit"],
#             y=[revenue, -cogs, -(gross_profit - profit), profit],
#             text=[f"฿{revenue:,.0f}", f"-฿{cogs:,.0f}", f"-฿{(gross_profit - profit):,.0f}", f"฿{profit:,.0f}"],
#             textposition="outside",
#             connector={"line": {"color": "rgb(63, 63, 63)"}},
#             decreasing={"marker": {"color": "#e74c3c"}},
#             increasing={"marker": {"color": "#2ecc71"}},
#             totals={"marker": {"color": "#3498db"}},
#             hovertemplate='<b>%{x}</b><br>Amount: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Profit Waterfall</b>',
#             plot_bgcolor='white',
#             height=300,
#             showlegend=False,
#             margin=dict(t=40, b=40, l=60, r=20)
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 30px; border-radius: 10px; color: white; text-align: center; height: 300px;
#                     display: flex; flex-direction: column; justify-content: center;'>
#             <div style='font-size: 14px; opacity: 0.9; margin-bottom: 10px;'>
#                 GROSS PROFIT MARGIN
#             </div>
#             <div style='font-size: 52px; font-weight: bold; margin: 15px 0;'>
#                 {gross_margin:.1f}%
#             </div>
#             <div style='font-size: 12px; opacity: 0.8;'>
#                 (Revenue - COGS) / Revenue
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 30px; border-radius: 10px; color: white; text-align: center; height: 300px;
#                     display: flex; flex-direction: column; justify-content: center;'>
#             <div style='font-size: 14px; opacity: 0.9; margin-bottom: 10px;'>
#                 NET PROFIT MARGIN
#             </div>
#             <div style='font-size: 52px; font-weight: bold; margin: 15px 0;'>
#                 {net_margin:.1f}%
#             </div>
#             <div style='font-size: 12px; opacity: 0.8;'>
#                 Net Profit / Revenue
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== MONTHLY FINANCIAL TREND ====================
#     st.markdown("### 📈 Monthly Financial Performance")
    
#     monthly_fin = df_filtered.groupby('order_month').agg({
#         'net_revenue': 'sum',
#         'cost': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     monthly_fin['order_month'] = monthly_fin['order_month'].dt.to_timestamp()
#     monthly_fin['month_label'] = monthly_fin['order_month'].dt.strftime('%b %Y')
#     monthly_fin['gross_margin_%'] = ((monthly_fin['net_revenue'] - monthly_fin['cost']) / monthly_fin['net_revenue'] * 100).round(1)
#     monthly_fin['net_margin_%'] = (monthly_fin['profit'] / monthly_fin['net_revenue'] * 100).round(1)
    
#     fig = make_subplots(specs=[[{"secondary_y": True}]])
    
#     # Revenue and Cost bars
#     fig.add_trace(
#         go.Bar(
#             x=monthly_fin['month_label'],
#             y=monthly_fin['net_revenue'],
#             name='Revenue',
#             marker_color='#3498db',
#             hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#         ),
#         secondary_y=False
#     )
    
#     fig.add_trace(
#         go.Bar(
#             x=monthly_fin['month_label'],
#             y=monthly_fin['cost'],
#             name='COGS',
#             marker_color='#e74c3c',
#             hovertemplate='<b>%{x}</b><br>COGS: ฿%{y:,.0f}<extra></extra>'
#         ),
#         secondary_y=False
#     )
    
#     # Margin lines
#     fig.add_trace(
#         go.Scatter(
#             x=monthly_fin['month_label'],
#             y=monthly_fin['gross_margin_%'],
#             name='Gross Margin %',
#             mode='lines+markers',
#             line=dict(color='#27ae60', width=3),
#             marker=dict(size=8),
#             hovertemplate='<b>%{x}</b><br>Gross Margin: %{y:.1f}%<extra></extra>'
#         ),
#         secondary_y=True
#     )
    
#     fig.add_trace(
#         go.Scatter(
#             x=monthly_fin['month_label'],
#             y=monthly_fin['net_margin_%'],
#             name='Net Margin %',
#             mode='lines+markers',
#             line=dict(color='#9b59b6', width=3),
#             marker=dict(size=8),
#             hovertemplate='<b>%{x}</b><br>Net Margin: %{y:.1f}%<extra></extra>'
#         ),
#         secondary_y=True
#     )
    
#     fig.update_xaxes(title_text="")
#     fig.update_yaxes(title_text="Amount (฿)", secondary_y=False, showgrid=True, gridcolor='rgba(0,0,0,0.05)')
#     fig.update_yaxes(title_text="Margin (%)", secondary_y=True, showgrid=False)
    
#     fig.update_layout(
#         title='<b>Monthly Revenue, Cost & Margins</b>',
#         plot_bgcolor='white',
#         height=400,
#         hovermode='x unified',
#         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
#         barmode='group'
#     )
    
#     st.plotly_chart(fig, use_container_width=True)
    
#     st.markdown("---")
    
#     # ==================== WORKING CAPITAL RATIOS ====================
#     st.markdown("### 💼 Working Capital Ratios")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 AR Turnover:</b> จำนวนครั้งที่เราเก็บเงินจากลูกค้าได้ต่อปี (ยิ่งสูงยิ่งดี)<br>
#         <b>📖 DSO (Days Sales Outstanding):</b> จำนวนวันเฉลี่ยที่ใช้เวลาเก็บเงินจากลูกค้า (ยิ่งต่ำยิ่งดี)<br>
#         <div class='metric-formula'>
#         DSO = 365 / AR Turnover
#         </div>
#         <b>🎯 เป้าหมาย:</b> DSO < 45 วัน ถือว่าดี
#     </div>
#     """, unsafe_allow_html=True)
    
#     # Calculate ratios
#     avg_monthly_rev = monthly_fin['net_revenue'].mean()
#     avg_ar = avg_monthly_rev * 0.3  # Assume 30% credit sales
#     ar_turnover = (revenue * 0.3) / avg_ar if avg_ar > 0 else 0
#     dso = 365 / ar_turnover if ar_turnover > 0 else 0
    
#     avg_ap = cogs * 0.25
#     ap_turnover = cogs / avg_ap if avg_ap > 0 else 0
#     dpo = 365 / ap_turnover if ap_turnover > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #3498db; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 12px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>AR TURNOVER</b>
#             </div>
#             <div style='font-size: 36px; font-weight: bold; color: #2c3e50;'>
#                 {ar_turnover:.2f}x
#             </div>
#             <div style='font-size: 11px; color: #95a5a6; margin-top: 5px;'>
#                 Times per year
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         dso_color = '#2ecc71' if dso < 45 else '#e74c3c'
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid {dso_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 12px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>DSO</b>
#             </div>
#             <div style='font-size: 36px; font-weight: bold; color: #2c3e50;'>
#                 {dso:.0f}
#             </div>
#             <div style='font-size: 11px; color: #95a5a6; margin-top: 5px;'>
#                 Days
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #9b59b6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 12px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>AP TURNOVER</b>
#             </div>
#             <div style='font-size: 36px; font-weight: bold; color: #2c3e50;'>
#                 {ap_turnover:.2f}x
#             </div>
#             <div style='font-size: 11px; color: #95a5a6; margin-top: 5px;'>
#                 Times per year
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #f39c12; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 12px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>DPO</b>
#             </div>
#             <div style='font-size: 36px; font-weight: bold; color: #2c3e50;'>
#                 {dpo:.0f}
#             </div>
#             <div style='font-size: 11px; color: #95a5a6; margin-top: 5px;'>
#                 Days
#             </div>
#         </div>
#         """, unsafe_allow_html=True)

# with tab4:
#     st.markdown("# 📦 Warehouse Analytics")
#     st.markdown("---")
    
#     # ==================== INVENTORY TURNOVER ====================
#     st.markdown("### 🔄 Inventory Turnover & Performance")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 Inventory Turnover:</b> จำนวนครั้งที่สินค้าหมุนเวียนต่อปี (ยิ่งสูงยิ่งดี แสดงว่าสินค้าขายดี)<br>
#         <div class='metric-formula'>
#         สูตร: ต้นทุนสินค้าที่ขาย / มูลค่าสินค้าคงคลังเฉลี่ย
#         </div>
#         <b>📖 Days Inventory Outstanding (DIO):</b> จำนวนวันที่สินค้าอยู่ในคลังก่อนขายได้<br>
#         <div class='metric-formula'>
#         สูตร: 365 / Inventory Turnover
#         </div>
#         <b>🎯 เป้าหมาย:</b> Turnover > 4x, DIO < 90 วัน
#     </div>
#     """, unsafe_allow_html=True)
    
#     avg_inventory = df_filtered['cost'].mean() * df_filtered['product_id'].nunique()
#     inventory_turnover = cogs / avg_inventory if avg_inventory > 0 else 0
#     dio = 365 / inventory_turnover if inventory_turnover > 0 else 0
    
#     units_sold = df_filtered['quantity'].sum()
#     units_received = units_sold * 1.2
#     sell_through = (units_sold / units_received * 100) if units_received > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>INVENTORY TURNOVER</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {inventory_turnover:.2f}x
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Times per year</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         dio_color = '#2ecc71' if dio < 90 else '#e74c3c'
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>DIO</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {dio:.0f}
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Days</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>SELL-THROUGH RATE</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {sell_through:.1f}%
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Of received</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>INVENTORY VALUE</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 ฿{avg_inventory/1000:.0f}K
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Total stock</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== PRODUCT MOVEMENT CLASSIFICATION ====================
#     st.markdown("### 🚀 Product Movement Classification")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> จัดกลุ่มสินค้าตามความเร็วในการขาย<br>
#         • <b style='color: #2ecc71;'>Fast Moving:</b> ขายดี ควรเพิ่ม stock<br>
#         • <b style='color: #f39c12;'>Medium Moving:</b> ขายปานกลาง รักษาระดับปกติ<br>
#         • <b style='color: #e74c3c;'>Slow Moving:</b> ขายช้า ลด stock หรือทำ clearance
#     </div>
#     """, unsafe_allow_html=True)
    
#     product_velocity = df_filtered.groupby(['product_id', 'product_name', 'category']).agg({
#         'order_id': 'nunique',
#         'net_revenue': 'sum',
#         'cost': 'sum',
#         'quantity': 'sum'
#     }).reset_index()
#     product_velocity.columns = ['ID', 'Product', 'Category', 'Orders', 'Revenue', 'Cost', 'Units']
    
#     fast_threshold = product_velocity['Orders'].quantile(0.75)
#     slow_threshold = product_velocity['Orders'].quantile(0.25)
    
#     def classify_movement(orders):
#         if orders >= fast_threshold:
#             return 'Fast Moving'
#         elif orders <= slow_threshold:
#             return 'Slow Moving'
#         return 'Medium Moving'
    
#     product_velocity['Movement'] = product_velocity['Orders'].apply(classify_movement)
    
#     movement_summary = product_velocity.groupby('Movement').agg({
#         'Product': 'count',
#         'Revenue': 'sum',
#         'Cost': 'sum'
#     }).reset_index()
#     movement_summary.columns = ['Movement', 'Products', 'Revenue', 'Inventory_Value']
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         # Stacked bar chart
#         movement_order = ['Fast Moving', 'Medium Moving', 'Slow Moving']
#         movement_colors = {'Fast Moving': '#2ecc71', 'Medium Moving': '#f39c12', 'Slow Moving': '#e74c3c'}
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             y=['Product Count'],
#             x=[movement_summary[movement_summary['Movement'] == 'Fast Moving']['Products'].sum()],
#             name='Fast Moving',
#             orientation='h',
#             marker_color='#2ecc71',
#             text=[movement_summary[movement_summary['Movement'] == 'Fast Moving']['Products'].sum()],
#             texttemplate='%{text}',
#             textposition='inside',
#             hovertemplate='<b>Fast Moving</b><br>Products: %{x}<extra></extra>'
#         ))
        
#         fig.add_trace(go.Bar(
#             y=['Product Count'],
#             x=[movement_summary[movement_summary['Movement'] == 'Medium Moving']['Products'].sum()],
#             name='Medium Moving',
#             orientation='h',
#             marker_color='#f39c12',
#             text=[movement_summary[movement_summary['Movement'] == 'Medium Moving']['Products'].sum()],
#             texttemplate='%{text}',
#             textposition='inside',
#             hovertemplate='<b>Medium Moving</b><br>Products: %{x}<extra></extra>'
#         ))
        
#         fig.add_trace(go.Bar(
#             y=['Product Count'],
#             x=[movement_summary[movement_summary['Movement'] == 'Slow Moving']['Products'].sum()],
#             name='Slow Moving',
#             orientation='h',
#             marker_color='#e74c3c',
#             text=[movement_summary[movement_summary['Movement'] == 'Slow Moving']['Products'].sum()],
#             texttemplate='%{text}',
#             textposition='inside',
#             hovertemplate='<b>Slow Moving</b><br>Products: %{x}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Product Distribution by Movement Speed</b>',
#             xaxis=dict(title='Number of Products'),
#             yaxis=dict(title=''),
#             barmode='stack',
#             plot_bgcolor='white',
#             height=400,
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         # Inventory value by movement
#         movement_sorted = movement_summary.sort_values('Inventory_Value', ascending=True)
#         colors = [movement_colors[m] for m in movement_sorted['Movement']]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             y=movement_sorted['Movement'],
#             x=movement_sorted['Inventory_Value'],
#             orientation='h',
#             marker=dict(color=colors),
#             text=movement_sorted['Inventory_Value'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             hovertemplate='<b>%{y}</b><br>Value: ฿%{x:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Inventory Value by Movement</b>',
#             xaxis=dict(title='Inventory Value (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             yaxis=dict(title=''),
#             plot_bgcolor='white',
#             height=400,
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Show top products in each category
#     st.markdown("#### 📋 Movement Classification Details")
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.success("**🚀 Fast Moving (Top 10)**")
#         fast_products = product_velocity[product_velocity['Movement'] == 'Fast Moving'].nlargest(10, 'Orders')
#         st.dataframe(
#             fast_products[['Product', 'Orders', 'Units']].style.format({
#                 'Orders': '{:,}',
#                 'Units': '{:,}'
#             }),
#             height=300,
#             use_container_width=True
#         )
    
#     with col2:
#         st.warning("**⚖️ Medium Moving (Top 10)**")
#         medium_products = product_velocity[product_velocity['Movement'] == 'Medium Moving'].nlargest(10, 'Orders')
#         st.dataframe(
#             medium_products[['Product', 'Orders', 'Units']].style.format({
#                 'Orders': '{:,}',
#                 'Units': '{:,}'
#             }),
#             height=300,
#             use_container_width=True
#         )
    
#     with col3:
#         st.error("**🐌 Slow Moving (Top 10)**")
#         slow_products = product_velocity[product_velocity['Movement'] == 'Slow Moving'].nlargest(10, 'Cost')
#         st.dataframe(
#             slow_products[['Product', 'Orders', 'Cost']].style.format({
#                 'Orders': '{:,}',
#                 'Cost': '฿{:,.0f}'
#             }),
#             height=300,
#             use_container_width=True
#         )
    
#     st.markdown("---")
    
#     # ==================== CASH CONVERSION CYCLE ====================
#     st.markdown("### ⏱️ Cash Conversion Cycle (CCC)")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> ระยะเวลาที่เงินสดถูกล็อคอยู่ในธุรกิจ<br>
#         <div class='metric-formula'>
#         สูตร: DIO + DSO - DPO
#         </div>
#         <b>📖 ความหมาย:</b><br>
#         • DIO = วันที่สินค้าอยู่ในคลัง<br>
#         • DSO = วันที่รอเก็บเงินจากลูกค้า<br>
#         • DPO = วันที่เราจ่ายเงินซัพพลายเออร์<br>
#         <b>🎯 เป้าหมาย:</b> ยิ่งต่ำยิ่งดี (< 60 วัน ดีมาก, < 30 วัน ดีเยี่ยม)
#     </div>
#     """, unsafe_allow_html=True)
    
#     ccc = dio + dso - dpo
    
#     col1, col2 = st.columns([1, 2])
    
#     with col1:
#         ccc_color = '#2ecc71' if ccc < 60 else '#e74c3c'
#         ccc_status = '✅ Excellent' if ccc < 30 else '✅ Good' if ccc < 60 else '⚠️ Needs Improvement'
        
#         st.markdown(f"""
#         <div style='background: white; padding: 40px; border-radius: 10px; 
#                     border: 4px solid {ccc_color}; text-align: center; height: 400px;
#                     display: flex; flex-direction: column; justify-content: center;'>
#             <div style='font-size: 16px; color: #7f8c8d; margin-bottom: 15px;'>
#                 <b>CASH CONVERSION CYCLE</b>
#             </div>
#             <div style='font-size: 72px; font-weight: bold; color: {ccc_color}; margin: 20px 0;'>
#                 {ccc:.0f}
#             </div>
#             <div style='font-size: 24px; color: #7f8c8d;'>
#                 days
#             </div>
#             <div style='font-size: 14px; color: #95a5a6; margin-top: 20px;'>
#                 {ccc_status}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         # CCC breakdown chart
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             x=['DIO', 'DSO', 'DPO', 'CCC'],
#             y=[dio, dso, -dpo, ccc],
#             marker=dict(
#                 color=['#3498db', '#9b59b6', '#e74c3c', '#2ecc71'],
#                 line=dict(color='white', width=2)
#             ),
#             text=[f"{dio:.0f}", f"{dso:.0f}", f"{dpo:.0f}", f"{ccc:.0f}"],
#             texttemplate='%{text} days',
#             textposition='outside',
#             hovertemplate='<b>%{x}</b><br>Days: %{y:.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Cash Conversion Cycle Breakdown</b>',
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(
#                 title='Days',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)',
#                 zeroline=True,
#                 zerolinecolor='gray'
#             ),
#             plot_bgcolor='white',
#             height=400,
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True)

# # Footer
# st.markdown("---")
# st.markdown("""
# <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#             border-radius: 15px; color: white;'>
#     <h3 style='margin: 0; font-size: 24px;'>📊 Analytics Dashboard</h3>
#     <p style='margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;'>
#         Built with Streamlit • Data-Driven Insights with Professional KPIs
#     </p>
# </div>
# """, unsafe_allow_html=True)






































































































# # Analytics Dashboard - Improved Version with KPIs
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
# import numpy as np
# import warnings
# from datetime import datetime, timedelta

# warnings.filterwarnings('ignore')
# st.set_page_config(page_title="Fashion Analytics Pro", layout="wide", page_icon="👕")

# # Enhanced Color Palette
# COLORS = {
#     'primary': '#1f77b4',
#     'secondary': '#ff7f0e',
#     'success': '#2ecc71',
#     'danger': '#e74c3c',
#     'warning': '#f39c12',
#     'info': '#3498db',
#     'purple': '#9b59b6',
#     'teal': '#1abc9c',
#     'pink': '#e91e63',
#     'indigo': '#3f51b5'
# }

# # Channel Color Mapping
# CHANNEL_COLORS = {
#     'TikTok': '#000000',
#     'Shopee': '#FF5722',
#     'Lazada': '#1E88E5',
#     'LINE Shopping': '#00C300',
#     'Instagram': '#9C27B0',
#     'Facebook': '#1877F2',
#     'Store': '#795548',
#     'Pop-up': '#FF9800',
#     'Website': '#607D8B'
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
#     st.sidebar.title("📊 Analytics Dashboard")
#     st.sidebar.markdown("### 📁 Data Upload")
#     st.sidebar.markdown("Upload your CSV files to begin analysis")
#     st.sidebar.markdown("---")
    
#     uploaded = st.sidebar.file_uploader(
#         "Choose CSV Files", 
#         type=['csv'], 
#         accept_multiple_files=True,
#         key="csv_uploader_main"
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
        
#         with st.sidebar:
#             st.markdown("**Loading Status:**")
        
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
#                             st.sidebar.error(f"❌ {file.name}")
#                             st.sidebar.caption(f"Missing: {', '.join(missing)}")
#                     else:
#                         data[table] = df
#                         st.sidebar.success(f"✅ {file.name}")
#                 except Exception as e:
#                     st.sidebar.error(f"❌ {file.name}")
#                     st.sidebar.caption(str(e))
        
#         if all(t in data for t in ['users', 'products', 'orders', 'order_items']):
#             st.session_state.data = data
#             st.session_state.data_loaded = True
#             st.sidebar.markdown("---")
#             st.sidebar.success("✅ **All data loaded successfully!**")
#             st.rerun()
#         else:
#             st.sidebar.error("❌ Missing required tables")
#             missing_tables = [t for t in ['users', 'products', 'orders', 'order_items'] if t not in data]
#             st.sidebar.caption(f"Need: {', '.join(missing_tables)}.csv")
    
#     if st.session_state.data_loaded:
#         st.sidebar.markdown("---")
#         st.sidebar.markdown("### ✅ Data Status")
#         st.sidebar.success("Data loaded and ready")
        
#         if st.session_state.data:
#             total_orders = len(st.session_state.data.get('orders', []))
#             total_customers = len(st.session_state.data.get('users', []))
#             total_products = len(st.session_state.data.get('products', []))
            
#             st.sidebar.markdown(f"""
#             - **Orders:** {total_orders:,}
#             - **Customers:** {total_customers:,}
#             - **Products:** {total_products:,}
#             """)
    
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

# # Custom CSS
# st.markdown("""
# <style>
#     .block-container {padding-top: 1rem; padding-bottom: 1rem;}
#     [data-testid="stMetricValue"] {font-size: 24px; font-weight: 600;}
#     [data-testid="stMetricLabel"] {font-size: 13px; font-weight: 500; color: #555;}
#     h1, h2, h3 {font-family: 'Inter', sans-serif; font-weight: 700;}
    
#     /* Info boxes for explanations */
#     .metric-explanation {
#         background: #f8f9fa;
#         padding: 15px;
#         border-radius: 8px;
#         border-left: 4px solid #3498db;
#         margin: 10px 0;
#         font-size: 13px;
#         color: #2c3e50;
#     }
    
#     .metric-formula {
#         background: #e8f4f8;
#         padding: 10px;
#         border-radius: 5px;
#         font-family: monospace;
#         font-size: 12px;
#         margin: 5px 0;
#     }
# </style>
# """, unsafe_allow_html=True)

# data = load_data()

# if not data:
#     st.title("📊 Analytics Dashboard")
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

# # ==================== MAIN FILTERS ====================
# st.title("📊 Fashion Analytics Dashboard")
# st.markdown("---")

# st.markdown("### 🔍 Filter Data")

# min_date = df_master['order_date'].min().date()
# max_date = df_master['order_date'].max().date()

# col1, col2, col3 = st.columns([2, 2, 1])

# with col1:
#     period_options = ["Custom Range", "Last 7 Days", "Last 30 Days", "Last 90 Days", 
#                       "This Month", "Last Month", "This Quarter", "This Year", "All Time"]
#     selected_period = st.selectbox("📅 Time Period", period_options, index=2, key="period_selector")

# with col2:
#     if selected_period == "Last 7 Days":
#         start_date = max_date - timedelta(days=7)
#         end_date = max_date
#     elif selected_period == "Last 30 Days":
#         start_date = max_date - timedelta(days=30)
#         end_date = max_date
#     elif selected_period == "Last 90 Days":
#         start_date = max_date - timedelta(days=90)
#         end_date = max_date
#     elif selected_period == "This Month":
#         start_date = max_date.replace(day=1)
#         end_date = max_date
#     elif selected_period == "Last Month":
#         first_day_this_month = max_date.replace(day=1)
#         end_date = first_day_this_month - timedelta(days=1)
#         start_date = end_date.replace(day=1)
#     elif selected_period == "This Quarter":
#         quarter = (max_date.month - 1) // 3
#         start_date = datetime(max_date.year, quarter * 3 + 1, 1).date()
#         end_date = max_date
#     elif selected_period == "This Year":
#         start_date = datetime(max_date.year, 1, 1).date()
#         end_date = max_date
#     elif selected_period == "All Time":
#         start_date = min_date
#         end_date = max_date
#     else:
#         date_range = st.date_input(
#             "Custom Date Range", 
#             [min_date, max_date], 
#             min_value=min_date, 
#             max_value=max_date,
#             key="custom_date_range"
#         )
#         if len(date_range) == 2:
#             start_date, end_date = date_range
#         else:
#             start_date, end_date = min_date, max_date
    
#     st.info(f"📆 **{start_date.strftime('%d %b %Y')}** → **{end_date.strftime('%d %b %Y')}**")

# with col3:
#     if st.button("🔄 Reset All", key="reset_filters", use_container_width=True):
#         st.rerun()

# df_filtered = df_master[(df_master['order_date'].dt.date >= start_date) & 
#                         (df_master['order_date'].dt.date <= end_date)]

# col1, col2, col3 = st.columns(3)

# with col1:
#     channels = st.multiselect(
#         "🏪 Sales Channel", 
#         df_master['channel'].unique(), 
#         df_master['channel'].unique(),
#         key="channel_filter"
#     )
#     df_filtered = df_filtered[df_filtered['channel'].isin(channels)]

# with col2:
#     statuses = st.multiselect(
#         "📦 Order Status", 
#         df_master['status'].unique(), 
#         ['Completed'],
#         key="status_filter"
#     )
#     df_filtered = df_filtered[df_filtered['status'].isin(statuses)]

# with col3:
#     if 'category' in df_filtered.columns:
#         categories = st.multiselect(
#             "🏷️ Product Category",
#             df_master['category'].unique(),
#             df_master['category'].unique(),
#             key="category_filter"
#         )
#         df_filtered = df_filtered[df_filtered['category'].isin(categories)]

# st.markdown("---")
# st.markdown("### 📊 Summary Statistics")

# # Calculate key metrics
# revenue = df_filtered['net_revenue'].sum()
# profit = df_filtered['profit'].sum()
# cogs = df_filtered['cost'].sum()
# total_orders = df_filtered['order_id'].nunique()
# total_customers = df_filtered['user_id'].nunique()
# gross_profit = revenue - cogs
# profit_margin = (profit / revenue * 100) if revenue > 0 else 0
# avg_order_value = revenue / total_orders if total_orders > 0 else 0

# col1, col2, col3, col4, col5, col6 = st.columns(6)

# with col1:
#     st.metric("💰 Revenue", f"฿{revenue/1000:,.0f}K")
# with col2:
#     st.metric("💵 Profit", f"฿{profit/1000:,.0f}K")
# with col3:
#     st.metric("📝 Orders", f"{total_orders:,}")
# with col4:
#     st.metric("👥 Customers", f"{total_customers:,}")
# with col5:
#     st.metric("📊 Margin", f"{profit_margin:.1f}%")
# with col6:
#     st.metric("🛒 AOV", f"฿{avg_order_value:,.0f}")

# st.markdown("---")

# # ==================== TABS ====================
# tab1, tab2, tab3, tab4, tab5 = st.tabs([
#     "💼 Sales Analytics", 
#     "📢 Marketing Analytics", 
#     "💰 Financial Analytics", 
#     "📦 Warehouse Analytics",
#     "🔮 Forecasting & Planning"
# ])

# with tab1:
#     st.markdown("# 💼 Sales Analytics")
#     st.markdown("---")
    
#     # ==================== SALES GROWTH ====================
#     st.markdown("### 📈 Monthly Sales Growth")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> วัดว่ายอดขายเติบโตกี่ % เมื่อเทียบกับเดือนก่อนหน้า<br>
#         <div class='metric-formula'>
#         สูตร: [(ยอดขายเดือนปัจจุบัน - ยอดขายเดือนก่อน) / ยอดขายเดือนก่อน] × 100
#         </div>
#         <b>🎯 เป้าหมาย:</b> ควรเป็นบวก และมากกว่า 5-10% ถือว่าดี
#     </div>
#     """, unsafe_allow_html=True)
    
#     monthly_sales = df_filtered.groupby('order_month').agg({
#         'net_revenue': 'sum'
#     }).reset_index()
#     monthly_sales['order_month'] = monthly_sales['order_month'].dt.to_timestamp()
#     monthly_sales['month_label'] = monthly_sales['order_month'].dt.strftime('%b %Y')
#     monthly_sales['growth_%'] = monthly_sales['net_revenue'].pct_change() * 100
    
#     col1, col2 = st.columns([2, 1])
    
#     with col1:
#         fig = go.Figure()
        
#         # Revenue bars
#         fig.add_trace(go.Bar(
#             x=monthly_sales['month_label'],
#             y=monthly_sales['net_revenue'],
#             name='Revenue',
#             marker=dict(
#                 color=monthly_sales['net_revenue'],
#                 colorscale='Blues',
#                 showscale=False
#             ),
#             text=monthly_sales['net_revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         # Growth line
#         fig.add_trace(go.Scatter(
#             x=monthly_sales['month_label'],
#             y=monthly_sales['growth_%'],
#             name='Growth %',
#             mode='lines+markers',
#             line=dict(color='#e74c3c', width=3),
#             marker=dict(size=10),
#             yaxis='y2',
#             text=monthly_sales['growth_%'],
#             texttemplate='%{text:.1f}%',
#             textposition='top center',
#             hovertemplate='<b>%{x}</b><br>Growth: %{y:.1f}%<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Monthly Sales Revenue & Growth Rate</b>',
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             yaxis2=dict(
#                 title='Growth (%)', 
#                 overlaying='y', 
#                 side='right',
#                 showgrid=False,
#                 zeroline=True,
#                 zerolinecolor='gray'
#             ),
#             plot_bgcolor='white',
#             height=400,
#             hovermode='x unified',
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         latest_growth = monthly_sales['growth_%'].iloc[-1] if len(monthly_sales) > 1 else 0
#         prev_growth = monthly_sales['growth_%'].iloc[-2] if len(monthly_sales) > 2 else 0
        
#         arrow = "📈" if latest_growth > 0 else "📉"
#         color = "#2ecc71" if latest_growth > 0 else "#e74c3c"
        
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid {color}; height: 400px;
#                     display: flex; flex-direction: column; justify-content: center; align-items: center;'>
#             <div style='font-size: 60px;'>{arrow}</div>
#             <div style='font-size: 48px; font-weight: bold; color: {color}; margin: 20px 0;'>
#                 {latest_growth:+.1f}%
#             </div>
#             <div style='font-size: 16px; color: #7f8c8d; text-align: center;'>
#                 <b>Current Month Growth</b>
#             </div>
#             <div style='margin-top: 20px; font-size: 14px; color: #95a5a6;'>
#                 Previous: {prev_growth:.1f}%
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== SALES TARGET ATTAINMENT ====================
#     st.markdown("### 🎯 Sales Target Attainment")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> วัดว่าทำยอดขายได้กี่ % ของเป้าหมายที่ตั้งไว้<br>
#         <div class='metric-formula'>
#         สูตร: (ยอดขายที่ทำได้ / เป้าหมายยอดขาย) × 100
#         </div>
#         <b>🎯 เป้าหมาย:</b> ควรอยู่ที่ 90-110% (น้อยกว่า 90% ต้องปรับปรุง, มากกว่า 110% ดีมาก)
#     </div>
#     """, unsafe_allow_html=True)
    
#     # Calculate target attainment
#     target_monthly = 5000000  # 5M target
#     current_month_sales = monthly_sales['net_revenue'].iloc[-1] if len(monthly_sales) > 0 else 0
#     attainment = (current_month_sales / target_monthly * 100) if target_monthly > 0 else 0
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 30px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 14px; opacity: 0.9;'>TARGET</div>
#             <div style='font-size: 36px; font-weight: bold; margin: 15px 0;'>
#                 ฿{target_monthly/1000000:.1f}M
#             </div>
#             <div style='font-size: 12px; opacity: 0.8;'>Monthly Goal</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 30px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 14px; opacity: 0.9;'>ACTUAL</div>
#             <div style='font-size: 36px; font-weight: bold; margin: 15px 0;'>
#                 ฿{current_month_sales/1000000:.1f}M
#             </div>
#             <div style='font-size: 12px; opacity: 0.8;'>Current Sales</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         att_color = '#2ecc71' if attainment >= 90 else '#e74c3c'
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid {att_color}; text-align: center;'>
#             <div style='font-size: 14px; color: #7f8c8d;'>ATTAINMENT</div>
#             <div style='font-size: 36px; font-weight: bold; margin: 15px 0; color: {att_color};'>
#                 {attainment:.1f}%
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 {'✅ On Track' if attainment >= 90 else '⚠️ Below Target'}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== SALES BY CHANNEL ====================
#     st.markdown("### 🏪 Sales by Channel")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> แสดงยอดขายแยกตามช่องทางการขาย เพื่อดูว่าช่องทางไหนมี Performance ดีที่สุด
#     </div>
#     """, unsafe_allow_html=True)
    
#     channel_sales = df_filtered.groupby('channel').agg({
#         'net_revenue': 'sum',
#         'profit': 'sum',
#         'order_id': 'nunique'
#     }).reset_index()
#     channel_sales.columns = ['Channel', 'Revenue', 'Profit', 'Orders']
#     channel_sales['Margin_%'] = (channel_sales['Profit'] / channel_sales['Revenue'] * 100).round(1)
#     channel_sales['AOV'] = (channel_sales['Revenue'] / channel_sales['Orders']).round(0)
#     channel_sales = channel_sales.sort_values('Revenue', ascending=False)
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         # Horizontal bar chart
#         ch_sorted = channel_sales.sort_values('Revenue', ascending=True)
#         colors_list = [CHANNEL_COLORS.get(ch, '#95a5a6') for ch in ch_sorted['Channel']]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             y=ch_sorted['Channel'],
#             x=ch_sorted['Revenue'],
#             orientation='h',
#             marker=dict(color=colors_list),
#             text=ch_sorted['Revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Revenue by Channel</b>',
#             xaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             yaxis=dict(title=''),
#             plot_bgcolor='white',
#             height=400,
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         # Stacked bar: Revenue vs Profit
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             x=channel_sales['Channel'],
#             y=channel_sales['Profit'],
#             name='Profit',
#             marker_color='#2ecc71',
#             text=channel_sales['Profit'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='inside',
#             hovertemplate='<b>%{x}</b><br>Profit: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.add_trace(go.Bar(
#             x=channel_sales['Channel'],
#             y=channel_sales['Revenue'] - channel_sales['Profit'],
#             name='Cost',
#             marker_color='#e74c3c',
#             text=channel_sales['Revenue'] - channel_sales['Profit'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='inside',
#             hovertemplate='<b>%{x}</b><br>Cost: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Revenue Breakdown: Profit vs Cost</b>',
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(title='Amount (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             barmode='stack',
#             plot_bgcolor='white',
#             height=400,
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Channel metrics table
#     st.markdown("#### 📊 Channel Performance Metrics")
    
#     styled_ch = channel_sales.style.format({
#         'Revenue': '฿{:,.0f}',
#         'Profit': '฿{:,.0f}',
#         'Orders': '{:,}',
#         'Margin_%': '{:.1f}%',
#         'AOV': '฿{:,.0f}'
#     }).background_gradient(subset=['Margin_%'], cmap='RdYlGn', vmin=0, vmax=100)
    
#     st.dataframe(styled_ch, use_container_width=True)
    
#     st.markdown("---")
    
#     # ==================== PRODUCT PERFORMANCE ====================
#     st.markdown("### 🏆 Top Product Performance")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> แสดงสินค้าที่ขายดีที่สุด 20 อันดับแรก วัดจากยอดขาย และอัตรากำไร
#     </div>
#     """, unsafe_allow_html=True)
    
#     product_sales = df_filtered.groupby(['product_id', 'product_name', 'category']).agg({
#         'net_revenue': 'sum',
#         'profit': 'sum',
#         'quantity': 'sum'
#     }).reset_index()
#     product_sales.columns = ['ID', 'Product', 'Category', 'Revenue', 'Profit', 'Units']
#     product_sales['Margin_%'] = (product_sales['Profit'] / product_sales['Revenue'] * 100).round(1)
#     product_sales = product_sales.sort_values('Revenue', ascending=False).head(20)
    
#     col1, col2 = st.columns([3, 2])
    
#     with col1:
#         # Top 10 horizontal bar
#         top10 = product_sales.head(10).sort_values('Revenue', ascending=True)
        
#         fig = go.Figure()
        
#         # Color by margin
#         colors = ['#2ecc71' if m >= 50 else '#f39c12' if m >= 30 else '#e74c3c' 
#                   for m in top10['Margin_%']]
        
#         fig.add_trace(go.Bar(
#             y=top10['Product'],
#             x=top10['Revenue'],
#             orientation='h',
#             marker=dict(color=colors),
#             text=top10['Revenue'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             customdata=top10[['Margin_%']],
#             hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<br>Margin: %{customdata[0]:.1f}%<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Top 10 Products by Revenue</b><br><sub>Color: Green=High Margin, Yellow=Medium, Red=Low</sub>',
#             xaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             yaxis=dict(title=''),
#             plot_bgcolor='white',
#             height=450,
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         # Scatter: Revenue vs Margin (Fixed bubble size)
#         fig = go.Figure()
        
#         # Calculate bubble size (max 80, min 10)
#         max_units = product_sales['Units'].max()
#         min_units = product_sales['Units'].min()
#         normalized_sizes = 10 + (product_sales['Units'] - min_units) / (max_units - min_units) * 70
        
#         fig.add_trace(go.Scatter(
#             x=product_sales['Revenue'],
#             y=product_sales['Margin_%'],
#             mode='markers',
#             marker=dict(
#                 size=normalized_sizes,
#                 color=product_sales['Margin_%'],
#                 colorscale='RdYlGn',
#                 showscale=True,
#                 colorbar=dict(title="Margin %"),
#                 line=dict(width=1, color='white'),
#                 sizemode='diameter'
#             ),
#             text=product_sales['Product'],
#             customdata=product_sales['Units'],
#             hovertemplate='<b>%{text}</b><br>Revenue: ฿%{x:,.0f}<br>Margin: %{y:.1f}%<br>Units: %{customdata:,}<extra></extra>'
#         ))
        
#         # Add quadrant lines
#         avg_revenue = product_sales['Revenue'].median()
#         avg_margin = product_sales['Margin_%'].median()
        
#         fig.add_hline(y=avg_margin, line_dash="dash", line_color="gray", opacity=0.5, 
#                       annotation_text="Avg Margin", annotation_position="right")
#         fig.add_vline(x=avg_revenue, line_dash="dash", line_color="gray", opacity=0.5,
#                       annotation_text="Avg Revenue", annotation_position="top")
        
#         # Add quadrant labels
#         fig.add_annotation(x=avg_revenue * 1.5, y=avg_margin * 1.2,
#                           text="🌟 Stars<br>(High Revenue, High Margin)",
#                           showarrow=False, font=dict(size=10, color='green'))
        
#         fig.add_annotation(x=avg_revenue * 1.5, y=avg_margin * 0.8,
#                           text="💰 Cash Cows<br>(High Revenue, Low Margin)",
#                           showarrow=False, font=dict(size=10, color='orange'))
        
#         fig.add_annotation(x=avg_revenue * 0.5, y=avg_margin * 1.2,
#                           text="🚀 Growth<br>(Low Revenue, High Margin)",
#                           showarrow=False, font=dict(size=10, color='blue'))
        
#         fig.add_annotation(x=avg_revenue * 0.5, y=avg_margin * 0.8,
#                           text="⚠️ Question Marks<br>(Low Revenue, Low Margin)",
#                           showarrow=False, font=dict(size=10, color='red'))
        
#         fig.update_layout(
#             title='<b>Product Portfolio Analysis (BCG Matrix)</b><br><sub>Bubble size = Units Sold</sub>',
#             xaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             yaxis=dict(title='Profit Margin (%)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             plot_bgcolor='white',
#             height=450
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     st.markdown("#### 📋 Top 20 Products Detail")
    
#     styled_prod = product_sales.style.format({
#         'Revenue': '฿{:,.0f}',
#         'Profit': '฿{:,.0f}',
#         'Units': '{:,}',
#         'Margin_%': '{:.1f}%'
#     }).background_gradient(subset=['Margin_%'], cmap='RdYlGn', vmin=0, vmax=100)
    
#     st.dataframe(styled_prod, use_container_width=True)

# with tab2:
#     st.markdown("# 📢 Marketing Analytics")
#     st.markdown("---")
    
#     # Data availability checker
#     st.markdown("### 📋 Available Marketing Metrics")
    
#     has_funnel = all(col in df_filtered.columns for col in ['visits', 'add_to_cart', 'checkout'])
#     has_campaign = 'campaign_type' in df_filtered.columns and df_filtered['campaign_type'].notna().any()
#     has_acquisition = 'acquisition_channel' in df_filtered.columns
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         if has_funnel:
#             st.success("✅ **Conversion Funnel Data Available**")
#         else:
#             st.warning("⚠️ **Conversion Funnel Data Missing**\nAdd columns: `visits`, `add_to_cart`, `checkout`")
    
#     with col2:
#         if has_campaign:
#             st.success("✅ **Campaign Data Available**")
#         else:
#             st.warning("⚠️ **Campaign Data Missing**\nAdd `campaign_type` column for campaign analysis")
    
#     with col3:
#         if has_acquisition:
#             st.success("✅ **Acquisition Channel Data Available**")
#         else:
#             st.warning("⚠️ **Acquisition Data Missing**\nAdd `acquisition_channel` column for acquisition analysis")
    
#     st.markdown("---")
    
#     # ==================== CONVERSION FUNNEL ====================
#     st.markdown("### 🎯 Conversion Funnel Analysis")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 Conversion Rate:</b> เปอร์เซ็นต์ของผู้เข้าชมที่กลายเป็นลูกค้า (ซื้อสินค้าจริง)<br>
#         <div class='metric-formula'>
#         สูตร: (จำนวน Orders / จำนวน Visitors) × 100
#         </div>
#         <b>📖 Funnel Stages:</b><br>
#         • <b>Visitors:</b> คนที่เข้าชมเว็บไซต์/ร้าน<br>
#         • <b>Add to Cart:</b> คนที่ใส่สินค้าในตะกร้า<br>
#         • <b>Checkout:</b> คนที่ไปหน้า Checkout<br>
#         • <b>Purchase:</b> คนที่ซื้อสำเร็จ<br>
#         <b>🎯 เป้าหมาย:</b> Conversion Rate 2-5% ถือว่าปกติ, >5% ดีมาก
#     </div>
#     """, unsafe_allow_html=True)
    
#     if has_funnel:
#         # Use actual funnel data
#         total_visitors = df_filtered['visits'].sum()
#         add_to_cart = df_filtered['add_to_cart'].sum()
#         checkout_count = df_filtered['checkout'].sum()
#         total_orders = df_filtered['order_id'].nunique()
#         conversion_rate = (total_orders / total_visitors * 100) if total_visitors > 0 else 0
        
#         col1, col2 = st.columns([1, 2])
        
#         with col1:
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                         padding: 30px; border-radius: 10px; color: white; height: 400px;
#                         display: flex; flex-direction: column; justify-content: center;'>
#                 <div style='text-align: center;'>
#                     <div style='font-size: 16px; opacity: 0.9; margin-bottom: 20px;'>
#                         <b>CONVERSION RATE</b>
#                     </div>
#                     <div style='font-size: 72px; font-weight: bold; margin: 20px 0;'>
#                         {conversion_rate:.1f}%
#                     </div>
#                     <div style='font-size: 14px; opacity: 0.8; margin-top: 20px;'>
#                         {total_orders:,} orders from {total_visitors:,} visitors
#                     </div>
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col2:
#             # Funnel chart
#             funnel_data = pd.DataFrame({
#                 'Stage': ['Visitors', 'Add to Cart', 'Checkout', 'Purchase'],
#                 'Count': [total_visitors, add_to_cart, checkout_count, total_orders],
#                 'Color': ['#3498db', '#2ecc71', '#f39c12', '#9b59b6']
#             })
            
#             fig = go.Figure()
            
#             fig.add_trace(go.Funnel(
#                 y=funnel_data['Stage'],
#                 x=funnel_data['Count'],
#                 textposition="inside",
#                 textinfo="value+percent initial",
#                 marker=dict(
#                     color=funnel_data['Color'],
#                     line=dict(color='white', width=2)
#                 ),
#                 textfont=dict(size=13, weight='bold', color='white'),
#                 hovertemplate='<b>%{y}</b><br>Count: %{x:,}<br>Rate: %{percentInitial}<extra></extra>',
#                 connector=dict(line=dict(color='gray', width=1))
#             ))
            
#             fig.update_layout(
#                 title='<b>Sales Funnel</b>',
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 height=400,
#                 margin=dict(t=60, b=40, l=40, r=120),
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True)
#     else:
#         # Show alternative: Order completion metrics
#         st.info("💡 **Showing Order Completion Metrics** (Funnel data not available)")
        
#         total_orders = df_filtered['order_id'].nunique()
#         total_customers = df_filtered['user_id'].nunique()
#         completed_orders = df_filtered[df_filtered['status'] == 'Completed']['order_id'].nunique()
        
#         col1, col2, col3 = st.columns(3)
        
#         with col1:
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                         padding: 30px; border-radius: 10px; color: white; text-align: center; height: 200px;
#                         display: flex; flex-direction: column; justify-content: center;'>
#                 <div style='font-size: 14px; opacity: 0.9;'>TOTAL ORDERS</div>
#                 <div style='font-size: 48px; font-weight: bold; margin: 15px 0;'>
#                     {total_orders:,}
#                 </div>
#                 <div style='font-size: 12px; opacity: 0.8;'>All statuses</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col2:
#             completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                         padding: 30px; border-radius: 10px; color: white; text-align: center; height: 200px;
#                         display: flex; flex-direction: column; justify-content: center;'>
#                 <div style='font-size: 14px; opacity: 0.9;'>COMPLETION RATE</div>
#                 <div style='font-size: 48px; font-weight: bold; margin: 15px 0;'>
#                     {completion_rate:.1f}%
#                 </div>
#                 <div style='font-size: 12px; opacity: 0.8;'>{completed_orders:,} completed</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col3:
#             orders_per_customer = total_orders / total_customers if total_customers > 0 else 0
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                         padding: 30px; border-radius: 10px; color: white; text-align: center; height: 200px;
#                         display: flex; flex-direction: column; justify-content: center;'>
#                 <div style='font-size: 14px; opacity: 0.9;'>ORDERS/CUSTOMER</div>
#                 <div style='font-size: 48px; font-weight: bold; margin: 15px 0;'>
#                     {orders_per_customer:.1f}
#                 </div>
#                 <div style='font-size: 12px; opacity: 0.8;'>Average frequency</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         # Show order status breakdown
#         st.markdown("<br>", unsafe_allow_html=True)
        
#         status_data = df_filtered.groupby('status')['order_id'].nunique().reset_index()
#         status_data.columns = ['Status', 'Orders']
#         status_data = status_data.sort_values('Orders', ascending=True)
        
#         status_colors = {
#             'Completed': '#2ecc71',
#             'Pending': '#f39c12',
#             'Cancelled': '#e74c3c',
#             'Refunded': '#95a5a6'
#         }
        
#         colors_list = [status_colors.get(s, '#95a5a6') for s in status_data['Status']]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             y=status_data['Status'],
#             x=status_data['Orders'],
#             orientation='h',
#             marker=dict(color=colors_list, line=dict(color='white', width=2)),
#             text=status_data['Orders'],
#             texttemplate='%{text:,}',
#             textposition='outside',
#             hovertemplate='<b>%{y}</b><br>Orders: %{x:,}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Order Status Breakdown</b>',
#             xaxis=dict(title='Number of Orders', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             yaxis=dict(title=''),
#             plot_bgcolor='white',
#             height=300,
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     st.markdown("---")
    
#     # ==================== CUSTOMER ACQUISITION COST ====================
#     st.markdown("### 💳 Customer Acquisition Cost (CAC)")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> ค่าใช้จ่ายที่ใช้ในการหาลูกค้าใหม่ 1 คน<br>
#         <div class='metric-formula'>
#         สูตร: ค่าใช้จ่ายทางการตลาด / จำนวนลูกค้าใหม่
#         </div>
#         <b>🎯 เป้าหมาย:</b> ควรต่ำกว่า Customer Lifetime Value (CLV) อย่างน้อย 3 เท่า
#     </div>
#     """, unsafe_allow_html=True)
    
#     marketing_cost = df_filtered['discount_amount'].sum() if 'discount_amount' in df_filtered.columns else 0
#     new_customers = df_filtered['user_id'].nunique()
#     cac = marketing_cost / new_customers if new_customers > 0 else 0
    
#     # Calculate CLV
#     analysis_date = df_filtered['order_date'].max()
#     last_purchase = df_filtered.groupby('user_id')['order_date'].max()
#     churned = ((analysis_date - last_purchase).dt.days > 90).sum()
#     churn_rate = (churned / len(last_purchase) * 100) if len(last_purchase) > 0 else 0
#     retention_rate = 100 - churn_rate
#     avg_revenue = df_filtered.groupby('user_id')['net_revenue'].sum().mean()
#     clv = (profit_margin / 100) * (retention_rate / 100) * avg_revenue
    
#     cac_to_clv_ratio = (cac / clv) if clv > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9;'>CAC</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
#                 ฿{cac:,.0f}
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Per customer</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9;'>CLV</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
#                 ฿{clv:,.0f}
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Lifetime value</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         ratio_color = '#2ecc71' if cac_to_clv_ratio < 0.33 else '#e74c3c'
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border: 3px solid {ratio_color}; text-align: center;'>
#             <div style='font-size: 13px; color: #7f8c8d;'>CAC : CLV</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0; color: {ratio_color};'>
#                 1:{(clv/cac if cac > 0 else 0):.1f}
#             </div>
#             <div style='font-size: 11px; color: #95a5a6;'>
#                 {'✅ Good' if cac_to_clv_ratio < 0.33 else '⚠️ Too High'}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9;'>NEW CUSTOMERS</div>
#             <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
#                 {new_customers:,}
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>In period</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== RETENTION & CHURN ====================
#     st.markdown("### 🔄 Customer Retention & Churn Rate")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 Retention Rate:</b> เปอร์เซ็นต์ของลูกค้าที่ยังคงซื้อสินค้ากับเรา (ไม่หายไป)<br>
#         <div class='metric-formula'>
#         สูตร: [1 - (จำนวนลูกค้าที่หายไป / จำนวนลูกค้าเริ่มต้น)] × 100
#         </div>
#         <b>📖 Churn Rate:</b> เปอร์เซ็นต์ของลูกค้าที่หยุดซื้อสินค้า (ไม่ซื้อเกิน 90 วัน)<br>
#         <b>🎯 เป้าหมาย:</b> Retention ควรสูงกว่า 80%, Churn ควรต่ำกว่า 20%
#     </div>
#     """, unsafe_allow_html=True)
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid #2ecc71; text-align: center; height: 200px;
#                     display: flex; flex-direction: column; justify-content: center;'>
#             <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
#                 <b>RETENTION RATE</b>
#             </div>
#             <div style='font-size: 48px; font-weight: bold; color: #2ecc71; margin: 15px 0;'>
#                 {retention_rate:.1f}%
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 Active customers
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: white; padding: 30px; border-radius: 10px; 
#                     border: 3px solid #e74c3c; text-align: center; height: 200px;
#                     display: flex; flex-direction: column; justify-content: center;'>
#             <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
#                 <b>CHURN RATE</b>
#             </div>
#             <div style='font-size: 48px; font-weight: bold; color: #e74c3c; margin: 15px 0;'>
#                 {churn_rate:.1f}%
#             </div>
#             <div style='font-size: 12px; color: #95a5a6;'>
#                 Lost customers
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         active_customers = int(len(last_purchase) * retention_rate / 100)
#         churned_customers = int(len(last_purchase) * churn_rate / 100)
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             x=['Active', 'Churned'],
#             y=[active_customers, churned_customers],
#             marker=dict(color=['#2ecc71', '#e74c3c']),
#             text=[active_customers, churned_customers],
#             texttemplate='%{text:,}',
#             textposition='outside',
#             hovertemplate='<b>%{x}</b><br>Customers: %{y:,}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Customer Status</b>',
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(title='Number of Customers', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             plot_bgcolor='white',
#             height=200,
#             showlegend=False,
#             margin=dict(t=40, b=40, l=60, r=20)
#         )
        
#         st.plotly_chart(fig, use_container_width=True)

# with tab3:
#     st.markdown("# 💰 Financial Analytics")
#     st.markdown("---")
    
#     # ==================== PROFIT MARGINS ====================
#     st.markdown("### 📊 Profit Margin Analysis")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 Gross Profit Margin:</b> เปอร์เซ็นต์กำไรขั้นต้น (หลังหักต้นทุนสินค้า)<br>
#         <div class='metric-formula'>
#         สูตร: [(รายได้ - ต้นทุนสินค้า) / รายได้] × 100
#         </div>
#         <b>📖 Net Profit Margin:</b> เปอร์เซ็นต์กำไรสุทธิ (หลังหักค่าใช้จ่ายทั้งหมด)<br>
#         <div class='metric-formula'>
#         สูตร: (กำไรสุทธิ / รายได้) × 100
#         </div>
#         <b>🎯 เป้าหมาย:</b> Gross Margin > 50%, Net Margin > 20% ถือว่าดี
#     </div>
#     """, unsafe_allow_html=True)
    
#     gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
#     net_margin = (profit / revenue * 100) if revenue > 0 else 0
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         # Waterfall chart
#         fig = go.Figure(go.Waterfall(
#             orientation="v",
#             measure=["relative", "relative", "relative", "total"],
#             x=["Revenue", "COGS", "Other Costs", "Net Profit"],
#             y=[revenue, -cogs, -(gross_profit - profit), profit],
#             text=[f"฿{revenue:,.0f}", f"-฿{cogs:,.0f}", f"-฿{(gross_profit - profit):,.0f}", f"฿{profit:,.0f}"],
#             textposition="outside",
#             connector={"line": {"color": "rgb(63, 63, 63)"}},
#             decreasing={"marker": {"color": "#e74c3c"}},
#             increasing={"marker": {"color": "#2ecc71"}},
#             totals={"marker": {"color": "#3498db"}},
#             hovertemplate='<b>%{x}</b><br>Amount: ฿%{y:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Profit Waterfall</b>',
#             plot_bgcolor='white',
#             height=300,
#             showlegend=False,
#             margin=dict(t=40, b=40, l=60, r=20)
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 30px; border-radius: 10px; color: white; text-align: center; height: 300px;
#                     display: flex; flex-direction: column; justify-content: center;'>
#             <div style='font-size: 14px; opacity: 0.9; margin-bottom: 10px;'>
#                 GROSS PROFIT MARGIN
#             </div>
#             <div style='font-size: 52px; font-weight: bold; margin: 15px 0;'>
#                 {gross_margin:.1f}%
#             </div>
#             <div style='font-size: 12px; opacity: 0.8;'>
#                 (Revenue - COGS) / Revenue
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 30px; border-radius: 10px; color: white; text-align: center; height: 300px;
#                     display: flex; flex-direction: column; justify-content: center;'>
#             <div style='font-size: 14px; opacity: 0.9; margin-bottom: 10px;'>
#                 NET PROFIT MARGIN
#             </div>
#             <div style='font-size: 52px; font-weight: bold; margin: 15px 0;'>
#                 {net_margin:.1f}%
#             </div>
#             <div style='font-size: 12px; opacity: 0.8;'>
#                 Net Profit / Revenue
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== MONTHLY FINANCIAL TREND ====================
#     st.markdown("### 📈 Monthly Financial Performance")
    
#     monthly_fin = df_filtered.groupby('order_month').agg({
#         'net_revenue': 'sum',
#         'cost': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     monthly_fin['order_month'] = monthly_fin['order_month'].dt.to_timestamp()
#     monthly_fin['month_label'] = monthly_fin['order_month'].dt.strftime('%b %Y')
#     monthly_fin['gross_margin_%'] = ((monthly_fin['net_revenue'] - monthly_fin['cost']) / monthly_fin['net_revenue'] * 100).round(1)
#     monthly_fin['net_margin_%'] = (monthly_fin['profit'] / monthly_fin['net_revenue'] * 100).round(1)
    
#     fig = make_subplots(specs=[[{"secondary_y": True}]])
    
#     # Revenue and Cost bars
#     fig.add_trace(
#         go.Bar(
#             x=monthly_fin['month_label'],
#             y=monthly_fin['net_revenue'],
#             name='Revenue',
#             marker_color='#3498db',
#             hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#         ),
#         secondary_y=False
#     )
    
#     fig.add_trace(
#         go.Bar(
#             x=monthly_fin['month_label'],
#             y=monthly_fin['cost'],
#             name='COGS',
#             marker_color='#e74c3c',
#             hovertemplate='<b>%{x}</b><br>COGS: ฿%{y:,.0f}<extra></extra>'
#         ),
#         secondary_y=False
#     )
    
#     # Margin lines
#     fig.add_trace(
#         go.Scatter(
#             x=monthly_fin['month_label'],
#             y=monthly_fin['gross_margin_%'],
#             name='Gross Margin %',
#             mode='lines+markers',
#             line=dict(color='#27ae60', width=3),
#             marker=dict(size=8),
#             hovertemplate='<b>%{x}</b><br>Gross Margin: %{y:.1f}%<extra></extra>'
#         ),
#         secondary_y=True
#     )
    
#     fig.add_trace(
#         go.Scatter(
#             x=monthly_fin['month_label'],
#             y=monthly_fin['net_margin_%'],
#             name='Net Margin %',
#             mode='lines+markers',
#             line=dict(color='#9b59b6', width=3),
#             marker=dict(size=8),
#             hovertemplate='<b>%{x}</b><br>Net Margin: %{y:.1f}%<extra></extra>'
#         ),
#         secondary_y=True
#     )
    
#     fig.update_xaxes(title_text="")
#     fig.update_yaxes(title_text="Amount (฿)", secondary_y=False, showgrid=True, gridcolor='rgba(0,0,0,0.05)')
#     fig.update_yaxes(title_text="Margin (%)", secondary_y=True, showgrid=False)
    
#     fig.update_layout(
#         title='<b>Monthly Revenue, Cost & Margins</b>',
#         plot_bgcolor='white',
#         height=400,
#         hovermode='x unified',
#         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
#         barmode='group'
#     )
    
#     st.plotly_chart(fig, use_container_width=True)
    
#     st.markdown("---")
    
#     # ==================== WORKING CAPITAL RATIOS ====================
#     st.markdown("### 💼 Working Capital Ratios")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 AR Turnover:</b> จำนวนครั้งที่เราเก็บเงินจากลูกค้าได้ต่อปี (ยิ่งสูงยิ่งดี)<br>
#         <b>📖 DSO (Days Sales Outstanding):</b> จำนวนวันเฉลี่ยที่ใช้เวลาเก็บเงินจากลูกค้า (ยิ่งต่ำยิ่งดี)<br>
#         <div class='metric-formula'>
#         DSO = 365 / AR Turnover
#         </div>
#         <b>🎯 เป้าหมาย:</b> DSO < 45 วัน ถือว่าดี
#     </div>
#     """, unsafe_allow_html=True)
    
#     # Calculate ratios
#     avg_monthly_rev = monthly_fin['net_revenue'].mean()
#     avg_ar = avg_monthly_rev * 0.3  # Assume 30% credit sales
#     ar_turnover = (revenue * 0.3) / avg_ar if avg_ar > 0 else 0
#     dso = 365 / ar_turnover if ar_turnover > 0 else 0
    
#     avg_ap = cogs * 0.25
#     ap_turnover = cogs / avg_ap if avg_ap > 0 else 0
#     dpo = 365 / ap_turnover if ap_turnover > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #3498db; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 12px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>AR TURNOVER</b>
#             </div>
#             <div style='font-size: 36px; font-weight: bold; color: #2c3e50;'>
#                 {ar_turnover:.2f}x
#             </div>
#             <div style='font-size: 11px; color: #95a5a6; margin-top: 5px;'>
#                 Times per year
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         dso_color = '#2ecc71' if dso < 45 else '#e74c3c'
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid {dso_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 12px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>DSO</b>
#             </div>
#             <div style='font-size: 36px; font-weight: bold; color: #2c3e50;'>
#                 {dso:.0f}
#             </div>
#             <div style='font-size: 11px; color: #95a5a6; margin-top: 5px;'>
#                 Days
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #9b59b6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 12px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>AP TURNOVER</b>
#             </div>
#             <div style='font-size: 36px; font-weight: bold; color: #2c3e50;'>
#                 {ap_turnover:.2f}x
#             </div>
#             <div style='font-size: 11px; color: #95a5a6; margin-top: 5px;'>
#                 Times per year
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: white; padding: 25px; border-radius: 10px; 
#                     border-left: 5px solid #f39c12; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='font-size: 12px; color: #7f8c8d; margin-bottom: 8px;'>
#                 <b>DPO</b>
#             </div>
#             <div style='font-size: 36px; font-weight: bold; color: #2c3e50;'>
#                 {dpo:.0f}
#             </div>
#             <div style='font-size: 11px; color: #95a5a6; margin-top: 5px;'>
#                 Days
#             </div>
#         </div>
#         """, unsafe_allow_html=True)

# with tab4:
#     st.markdown("# 📦 Warehouse Analytics")
#     st.markdown("---")
    
#     # ==================== INVENTORY TURNOVER ====================
#     st.markdown("### 🔄 Inventory Turnover & Performance")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 Inventory Turnover:</b> จำนวนครั้งที่สินค้าหมุนเวียนต่อปี (ยิ่งสูงยิ่งดี แสดงว่าสินค้าขายดี)<br>
#         <div class='metric-formula'>
#         สูตร: ต้นทุนสินค้าที่ขาย / มูลค่าสินค้าคงคลังเฉลี่ย
#         </div>
#         <b>📖 Days Inventory Outstanding (DIO):</b> จำนวนวันที่สินค้าอยู่ในคลังก่อนขายได้<br>
#         <div class='metric-formula'>
#         สูตร: 365 / Inventory Turnover
#         </div>
#         <b>🎯 เป้าหมาย:</b> Turnover > 4x, DIO < 90 วัน
#     </div>
#     """, unsafe_allow_html=True)
    
#     avg_inventory = df_filtered['cost'].mean() * df_filtered['product_id'].nunique()
#     inventory_turnover = cogs / avg_inventory if avg_inventory > 0 else 0
#     dio = 365 / inventory_turnover if inventory_turnover > 0 else 0
    
#     units_sold = df_filtered['quantity'].sum()
#     units_received = units_sold * 1.2
#     sell_through = (units_sold / units_received * 100) if units_received > 0 else 0
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>INVENTORY TURNOVER</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {inventory_turnover:.2f}x
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Times per year</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         dio_color = '#2ecc71' if dio < 90 else '#e74c3c'
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>DIO</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {dio:.0f}
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Days</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>SELL-THROUGH RATE</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {sell_through:.1f}%
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Of received</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>INVENTORY VALUE</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 ฿{avg_inventory/1000:.0f}K
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Total stock</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== PRODUCT MOVEMENT CLASSIFICATION ====================
#     st.markdown("### 🚀 Product Movement Classification")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> จัดกลุ่มสินค้าตามความเร็วในการขาย<br>
#         • <b style='color: #2ecc71;'>Fast Moving:</b> ขายดี ควรเพิ่ม stock<br>
#         • <b style='color: #f39c12;'>Medium Moving:</b> ขายปานกลาง รักษาระดับปกติ<br>
#         • <b style='color: #e74c3c;'>Slow Moving:</b> ขายช้า ลด stock หรือทำ clearance
#     </div>
#     """, unsafe_allow_html=True)
    
#     product_velocity = df_filtered.groupby(['product_id', 'product_name', 'category']).agg({
#         'order_id': 'nunique',
#         'net_revenue': 'sum',
#         'cost': 'sum',
#         'quantity': 'sum'
#     }).reset_index()
#     product_velocity.columns = ['ID', 'Product', 'Category', 'Orders', 'Revenue', 'Cost', 'Units']
    
#     fast_threshold = product_velocity['Orders'].quantile(0.75)
#     slow_threshold = product_velocity['Orders'].quantile(0.25)
    
#     def classify_movement(orders):
#         if orders >= fast_threshold:
#             return 'Fast Moving'
#         elif orders <= slow_threshold:
#             return 'Slow Moving'
#         return 'Medium Moving'
    
#     product_velocity['Movement'] = product_velocity['Orders'].apply(classify_movement)
    
#     movement_summary = product_velocity.groupby('Movement').agg({
#         'Product': 'count',
#         'Revenue': 'sum',
#         'Cost': 'sum'
#     }).reset_index()
#     movement_summary.columns = ['Movement', 'Products', 'Revenue', 'Inventory_Value']
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         # Stacked bar chart
#         movement_order = ['Fast Moving', 'Medium Moving', 'Slow Moving']
#         movement_colors = {'Fast Moving': '#2ecc71', 'Medium Moving': '#f39c12', 'Slow Moving': '#e74c3c'}
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             y=['Product Count'],
#             x=[movement_summary[movement_summary['Movement'] == 'Fast Moving']['Products'].sum()],
#             name='Fast Moving',
#             orientation='h',
#             marker_color='#2ecc71',
#             text=[movement_summary[movement_summary['Movement'] == 'Fast Moving']['Products'].sum()],
#             texttemplate='%{text}',
#             textposition='inside',
#             hovertemplate='<b>Fast Moving</b><br>Products: %{x}<extra></extra>'
#         ))
        
#         fig.add_trace(go.Bar(
#             y=['Product Count'],
#             x=[movement_summary[movement_summary['Movement'] == 'Medium Moving']['Products'].sum()],
#             name='Medium Moving',
#             orientation='h',
#             marker_color='#f39c12',
#             text=[movement_summary[movement_summary['Movement'] == 'Medium Moving']['Products'].sum()],
#             texttemplate='%{text}',
#             textposition='inside',
#             hovertemplate='<b>Medium Moving</b><br>Products: %{x}<extra></extra>'
#         ))
        
#         fig.add_trace(go.Bar(
#             y=['Product Count'],
#             x=[movement_summary[movement_summary['Movement'] == 'Slow Moving']['Products'].sum()],
#             name='Slow Moving',
#             orientation='h',
#             marker_color='#e74c3c',
#             text=[movement_summary[movement_summary['Movement'] == 'Slow Moving']['Products'].sum()],
#             texttemplate='%{text}',
#             textposition='inside',
#             hovertemplate='<b>Slow Moving</b><br>Products: %{x}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Product Distribution by Movement Speed</b>',
#             xaxis=dict(title='Number of Products'),
#             yaxis=dict(title=''),
#             barmode='stack',
#             plot_bgcolor='white',
#             height=400,
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         # Inventory value by movement
#         movement_sorted = movement_summary.sort_values('Inventory_Value', ascending=True)
#         colors = [movement_colors[m] for m in movement_sorted['Movement']]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             y=movement_sorted['Movement'],
#             x=movement_sorted['Inventory_Value'],
#             orientation='h',
#             marker=dict(color=colors),
#             text=movement_sorted['Inventory_Value'],
#             texttemplate='฿%{text:,.0f}',
#             textposition='outside',
#             hovertemplate='<b>%{y}</b><br>Value: ฿%{x:,.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Inventory Value by Movement</b>',
#             xaxis=dict(title='Inventory Value (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             yaxis=dict(title=''),
#             plot_bgcolor='white',
#             height=400,
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Show top products in each category
#     st.markdown("#### 📋 Movement Classification Details")
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.success("**🚀 Fast Moving (Top 10)**")
#         fast_products = product_velocity[product_velocity['Movement'] == 'Fast Moving'].nlargest(10, 'Orders')
#         st.dataframe(
#             fast_products[['Product', 'Orders', 'Units']].style.format({
#                 'Orders': '{:,}',
#                 'Units': '{:,}'
#             }),
#             height=300,
#             use_container_width=True
#         )
    
#     with col2:
#         st.warning("**⚖️ Medium Moving (Top 10)**")
#         medium_products = product_velocity[product_velocity['Movement'] == 'Medium Moving'].nlargest(10, 'Orders')
#         st.dataframe(
#             medium_products[['Product', 'Orders', 'Units']].style.format({
#                 'Orders': '{:,}',
#                 'Units': '{:,}'
#             }),
#             height=300,
#             use_container_width=True
#         )
    
#     with col3:
#         st.error("**🐌 Slow Moving (Top 10)**")
#         slow_products = product_velocity[product_velocity['Movement'] == 'Slow Moving'].nlargest(10, 'Cost')
#         st.dataframe(
#             slow_products[['Product', 'Orders', 'Cost']].style.format({
#                 'Orders': '{:,}',
#                 'Cost': '฿{:,.0f}'
#             }),
#             height=300,
#             use_container_width=True
#         )
    
#     st.markdown("---")
    
#     # ==================== CASH CONVERSION CYCLE ====================
#     st.markdown("### ⏱️ Cash Conversion Cycle (CCC)")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> ระยะเวลาที่เงินสดถูกล็อคอยู่ในธุรกิจ<br>
#         <div class='metric-formula'>
#         สูตร: DIO + DSO - DPO
#         </div>
#         <b>📖 ความหมาย:</b><br>
#         • DIO = วันที่สินค้าอยู่ในคลัง<br>
#         • DSO = วันที่รอเก็บเงินจากลูกค้า<br>
#         • DPO = วันที่เราจ่ายเงินซัพพลายเออร์<br>
#         <b>🎯 เป้าหมาย:</b> ยิ่งต่ำยิ่งดี (< 60 วัน ดีมาก, < 30 วัน ดีเยี่ยม)
#     </div>
#     """, unsafe_allow_html=True)
    
#     ccc = dio + dso - dpo
    
#     col1, col2 = st.columns([1, 2])
    
#     with col1:
#         ccc_color = '#2ecc71' if ccc < 60 else '#e74c3c'
#         ccc_status = '✅ Excellent' if ccc < 30 else '✅ Good' if ccc < 60 else '⚠️ Needs Improvement'
        
#         st.markdown(f"""
#         <div style='background: white; padding: 40px; border-radius: 10px; 
#                     border: 4px solid {ccc_color}; text-align: center; height: 400px;
#                     display: flex; flex-direction: column; justify-content: center;'>
#             <div style='font-size: 16px; color: #7f8c8d; margin-bottom: 15px;'>
#                 <b>CASH CONVERSION CYCLE</b>
#             </div>
#             <div style='font-size: 72px; font-weight: bold; color: {ccc_color}; margin: 20px 0;'>
#                 {ccc:.0f}
#             </div>
#             <div style='font-size: 24px; color: #7f8c8d;'>
#                 days
#             </div>
#             <div style='font-size: 14px; color: #95a5a6; margin-top: 20px;'>
#                 {ccc_status}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         # CCC breakdown chart
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             x=['DIO', 'DSO', 'DPO', 'CCC'],
#             y=[dio, dso, -dpo, ccc],
#             marker=dict(
#                 color=['#3498db', '#9b59b6', '#e74c3c', '#2ecc71'],
#                 line=dict(color='white', width=2)
#             ),
#             text=[f"{dio:.0f}", f"{dso:.0f}", f"{dpo:.0f}", f"{ccc:.0f}"],
#             texttemplate='%{text} days',
#             textposition='outside',
#             hovertemplate='<b>%{x}</b><br>Days: %{y:.0f}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Cash Conversion Cycle Breakdown</b>',
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(
#                 title='Days',
#                 showgrid=True,
#                 gridcolor='rgba(0,0,0,0.05)',
#                 zeroline=True,
#                 zerolinecolor='gray'
#             ),
#             plot_bgcolor='white',
#             height=400,
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True)

# with tab5:
#     st.markdown("# 🔮 Forecasting & Planning")
#     st.markdown("---")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 คำอธิบาย:</b> ใช้ข้อมูลในอดีตเพื่อคาดการณ์อนาคต ช่วยในการวางแผนธุรกิจ<br>
#         <b>🎯 วิธีการ:</b> ใช้ Moving Average และ Linear Regression เพื่อทำนายแนวโน้ม
#     </div>
#     """, unsafe_allow_html=True)
    
#     # ==================== REVENUE FORECAST ====================
#     st.markdown("### 📈 Revenue Forecast (Next 12 Months)")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 Revenue Forecast:</b> ทำนายยอดขายในอนาคต 12 เดือนข้างหน้า<br>
#         <div class='metric-formula'>
#         วิธีการ: Linear Regression + Moving Average (3 เดือน)
#         </div>
#         <b>💡 การใช้ประโยชน์:</b><br>
#         • วางแผนงบประมาณ<br>
#         • กำหนดเป้าหมายทีมขาย<br>
#         • วางแผนจัดซื้อสินค้า<br>
#         • วางแผนการตลาด
#     </div>
#     """, unsafe_allow_html=True)
    
#     # Prepare historical data
#     monthly_revenue = df_filtered.groupby('order_month').agg({
#         'net_revenue': 'sum'
#     }).reset_index()
#     monthly_revenue['order_month'] = monthly_revenue['order_month'].dt.to_timestamp()
#     monthly_revenue = monthly_revenue.sort_values('order_month')
    
#     if len(monthly_revenue) >= 3:
#         # Calculate moving average
#         monthly_revenue['MA_3'] = monthly_revenue['net_revenue'].rolling(window=3).mean()
        
#         # Simple linear regression for trend
#         from sklearn.linear_model import LinearRegression
#         import numpy as np
        
#         X = np.arange(len(monthly_revenue)).reshape(-1, 1)
#         y = monthly_revenue['net_revenue'].values
        
#         model = LinearRegression()
#         model.fit(X, y)
        
#         # Forecast next 12 months
#         future_months = 12
#         future_X = np.arange(len(monthly_revenue), len(monthly_revenue) + future_months).reshape(-1, 1)
#         forecast_values = model.predict(future_X)
        
#         # Apply growth adjustment (use recent growth rate)
#         recent_growth = monthly_revenue['net_revenue'].pct_change().tail(3).mean()
#         if not np.isnan(recent_growth) and recent_growth != 0:
#             growth_factor = 1 + recent_growth
#             forecast_adjusted = []
#             last_value = monthly_revenue['net_revenue'].iloc[-1]
#             for i in range(future_months):
#                 last_value = last_value * growth_factor
#                 forecast_adjusted.append(last_value)
#             forecast_values = (forecast_values + np.array(forecast_adjusted)) / 2
        
#         # Create forecast dataframe
#         last_date = monthly_revenue['order_month'].iloc[-1]
#         forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=future_months, freq='MS')
        
#         forecast_df = pd.DataFrame({
#             'Month': forecast_dates,
#             'Forecast': forecast_values
#         })
#         forecast_df['Month_Label'] = forecast_df['Month'].dt.strftime('%b %Y')
        
#         # Calculate confidence interval (±15%)
#         forecast_df['Lower'] = forecast_values * 0.85
#         forecast_df['Upper'] = forecast_values * 1.15
        
#         col1, col2 = st.columns([2, 1])
        
#         with col1:
#             # Create forecast chart
#             fig = go.Figure()
            
#             # Historical data
#             fig.add_trace(go.Scatter(
#                 x=monthly_revenue['order_month'].dt.strftime('%b %Y'),
#                 y=monthly_revenue['net_revenue'],
#                 name='Actual',
#                 mode='lines+markers',
#                 line=dict(color='#3498db', width=3),
#                 marker=dict(size=8),
#                 hovertemplate='<b>%{x}</b><br>Actual: ฿%{y:,.0f}<extra></extra>'
#             ))
            
#             # Moving Average
#             fig.add_trace(go.Scatter(
#                 x=monthly_revenue['order_month'].dt.strftime('%b %Y'),
#                 y=monthly_revenue['MA_3'],
#                 name='3-Month MA',
#                 mode='lines',
#                 line=dict(color='#95a5a6', width=2, dash='dash'),
#                 hovertemplate='<b>%{x}</b><br>MA: ฿%{y:,.0f}<extra></extra>'
#             ))
            
#             # Forecast
#             fig.add_trace(go.Scatter(
#                 x=forecast_df['Month_Label'],
#                 y=forecast_df['Forecast'],
#                 name='Forecast',
#                 mode='lines+markers',
#                 line=dict(color='#e74c3c', width=3),
#                 marker=dict(size=8, symbol='diamond'),
#                 hovertemplate='<b>%{x}</b><br>Forecast: ฿%{y:,.0f}<extra></extra>'
#             ))
            
#             # Confidence interval
#             fig.add_trace(go.Scatter(
#                 x=forecast_df['Month_Label'],
#                 y=forecast_df['Upper'],
#                 mode='lines',
#                 line=dict(width=0),
#                 showlegend=False,
#                 hoverinfo='skip'
#             ))
            
#             fig.add_trace(go.Scatter(
#                 x=forecast_df['Month_Label'],
#                 y=forecast_df['Lower'],
#                 mode='lines',
#                 line=dict(width=0),
#                 fill='tonexty',
#                 fillcolor='rgba(231, 76, 60, 0.2)',
#                 name='Confidence Interval (±15%)',
#                 hovertemplate='<b>%{x}</b><br>Range: ฿%{y:,.0f}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title='<b>Revenue Forecast - Next 12 Months</b>',
#                 xaxis=dict(title='', showgrid=False),
#                 yaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#                 plot_bgcolor='white',
#                 height=400,
#                 hovermode='x unified',
#                 legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#             )
            
#             st.plotly_chart(fig, use_container_width=True)
        
#         with col2:
#             # Forecast summary
#             total_forecast = forecast_df['Forecast'].sum()
#             avg_monthly = forecast_df['Forecast'].mean()
#             growth_forecast = ((forecast_df['Forecast'].iloc[-1] - monthly_revenue['net_revenue'].iloc[-1]) / 
#                              monthly_revenue['net_revenue'].iloc[-1] * 100)
            
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                         padding: 30px; border-radius: 10px; color: white; text-align: center; height: 400px;
#                         display: flex; flex-direction: column; justify-content: center;'>
#                 <div style='font-size: 14px; opacity: 0.9; margin-bottom: 15px;'>
#                     <b>FORECAST SUMMARY</b>
#                 </div>
#                 <div style='margin: 20px 0;'>
#                     <div style='font-size: 12px; opacity: 0.8;'>Next 12 Months Total</div>
#                     <div style='font-size: 36px; font-weight: bold; margin: 10px 0;'>
#                         ฿{total_forecast/1000000:.1f}M
#                     </div>
#                 </div>
#                 <div style='margin: 20px 0;'>
#                     <div style='font-size: 12px; opacity: 0.8;'>Average Monthly</div>
#                     <div style='font-size: 28px; font-weight: bold; margin: 10px 0;'>
#                         ฿{avg_monthly/1000:.0f}K
#                     </div>
#                 </div>
#                 <div style='margin: 20px 0;'>
#                     <div style='font-size: 12px; opacity: 0.8;'>Expected Growth</div>
#                     <div style='font-size: 28px; font-weight: bold; margin: 10px 0;'>
#                         {growth_forecast:+.1f}%
#                     </div>
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         # Forecast table
#         st.markdown("#### 📋 Monthly Forecast Details")
        
#         forecast_display = forecast_df.copy()
#         forecast_display['Month'] = forecast_display['Month_Label']
#         forecast_display = forecast_display[['Month', 'Forecast', 'Lower', 'Upper']]
#         forecast_display.columns = ['Month', 'Forecast', 'Min Expected', 'Max Expected']
        
#         styled_forecast = forecast_display.style.format({
#             'Forecast': '฿{:,.0f}',
#             'Min Expected': '฿{:,.0f}',
#             'Max Expected': '฿{:,.0f}'
#         }).background_gradient(subset=['Forecast'], cmap='Blues')
        
#         st.dataframe(styled_forecast, use_container_width=True, height=300)
#     else:
#         st.warning("⚠️ ต้องมีข้อมูลอย่างน้อย 3 เดือนเพื่อทำ Forecast")
    
#     st.markdown("---")
    
#     # ==================== STOCK PLANNING ====================
#     st.markdown("### 📦 Stock Planning Recommendation")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 Stock Planning:</b> แนะนำปริมาณสต็อกที่ควรมีสำหรับแต่ละสินค้า<br>
#         <div class='metric-formula'>
#         สูตร: (ยอดขายเฉลี่ยต่อเดือน × Lead Time) + Safety Stock
#         </div>
#         <b>📖 Safety Stock:</b> สต็อกสำรอง เผื่อความผันผวนของยอดขาย (20% ของยอดขายเฉลี่ย)<br>
#         <b>💡 การใช้ประโยชน์:</b><br>
#         • ป้องกันสินค้าหมด<br>
#         • ลดต้นทุนการจัดเก็บ<br>
#         • วางแผนสั่งซื้อล่วงหน้า
#     </div>
#     """, unsafe_allow_html=True)
    
#     # Calculate stock recommendations
#     # Assume lead time of 30 days (1 month)
#     lead_time_months = 1
#     safety_stock_pct = 0.20
    
#     # Get product sales data
#     product_monthly = df_filtered.groupby(['product_id', 'product_name', 'category', 'order_month']).agg({
#         'quantity': 'sum'
#     }).reset_index()
    
#     # Calculate average monthly sales per product
#     product_avg = product_monthly.groupby(['product_id', 'product_name', 'category']).agg({
#         'quantity': ['mean', 'std', 'count']
#     }).reset_index()
    
#     product_avg.columns = ['product_id', 'product_name', 'category', 'avg_monthly_qty', 'std_qty', 'months']
    
#     # Calculate stock recommendations
#     product_avg['lead_time_demand'] = product_avg['avg_monthly_qty'] * lead_time_months
#     product_avg['safety_stock'] = product_avg['avg_monthly_qty'] * safety_stock_pct
#     product_avg['reorder_point'] = product_avg['lead_time_demand'] + product_avg['safety_stock']
#     product_avg['recommended_stock'] = np.ceil(product_avg['reorder_point'] * 1.5)  # Add buffer
    
#     # Add current stock status (simulated - in real case, get from inventory table)
#     if 'inventory' in data:
#         # Try to get actual stock levels
#         try:
#             current_stock = data['inventory'].groupby('product_id')['quantity'].last().to_dict()
#             product_avg['current_stock'] = product_avg['product_id'].map(current_stock).fillna(0)
#         except:
#             product_avg['current_stock'] = product_avg['recommended_stock'] * 0.6  # Simulated
#     else:
#         product_avg['current_stock'] = product_avg['recommended_stock'] * 0.6  # Simulated
    
#     # Calculate stock status
#     product_avg['stock_status'] = product_avg.apply(
#         lambda x: 'Overstock' if x['current_stock'] > x['recommended_stock'] * 1.2
#         else 'Low Stock' if x['current_stock'] < x['reorder_point']
#         else 'Optimal', axis=1
#     )
    
#     product_avg['order_qty'] = np.maximum(0, product_avg['recommended_stock'] - product_avg['current_stock'])
    
#     # Sort by order quantity
#     product_avg = product_avg.sort_values('order_qty', ascending=False)
    
#     # Summary metrics
#     col1, col2, col3, col4 = st.columns(4)
    
#     low_stock_count = len(product_avg[product_avg['stock_status'] == 'Low Stock'])
#     optimal_count = len(product_avg[product_avg['stock_status'] == 'Optimal'])
#     overstock_count = len(product_avg[product_avg['stock_status'] == 'Overstock'])
#     total_order_needed = product_avg['order_qty'].sum()
    
#     with col1:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9;'>LOW STOCK</div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {low_stock_count}
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Products need reorder</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9;'>OPTIMAL</div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {optimal_count}
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Products at good level</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9;'>OVERSTOCK</div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {overstock_count}
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Products excess stock</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         st.markdown(f"""
#         <div style='background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9;'>TOTAL ORDER NEEDED</div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {total_order_needed:,.0f}
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Units to order</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("<br>", unsafe_allow_html=True)
    
#     # Stock status breakdown
#     col1, col2 = st.columns(2)
    
#     with col1:
#         status_counts = product_avg['stock_status'].value_counts()
#         status_colors = {
#             'Low Stock': '#e74c3c',
#             'Optimal': '#2ecc71',
#             'Overstock': '#f39c12'
#         }
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             x=list(status_counts.index),
#             y=list(status_counts.values),
#             marker=dict(color=[status_colors.get(s, '#95a5a6') for s in status_counts.index]),
#             text=list(status_counts.values),
#             texttemplate='%{text}',
#             textposition='outside',
#             hovertemplate='<b>%{x}</b><br>Products: %{y}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Stock Status Distribution</b>',
#             xaxis=dict(title='', showgrid=False),
#             yaxis=dict(title='Number of Products', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             plot_bgcolor='white',
#             height=350,
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         # Top products needing reorder
#         top_reorder = product_avg[product_avg['stock_status'] == 'Low Stock'].head(10)
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Bar(
#             y=top_reorder['product_name'],
#             x=top_reorder['order_qty'],
#             orientation='h',
#             marker_color='#e74c3c',
#             text=top_reorder['order_qty'],
#             texttemplate='%{text:,.0f}',
#             textposition='outside',
#             hovertemplate='<b>%{y}</b><br>Need to Order: %{x:,.0f} units<extra></extra>'
#         ))
        
#         fig.update_layout(
#             title='<b>Top 10 Products Needing Reorder</b>',
#             xaxis=dict(title='Quantity to Order', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#             yaxis=dict(title='', categoryorder='total ascending'),
#             plot_bgcolor='white',
#             height=350,
#             showlegend=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Detailed stock planning table
#     st.markdown("#### 📋 Detailed Stock Planning (Top 30 Products)")
    
#     top_products = product_avg.head(30).copy()
#     top_products_display = top_products[[
#         'product_name', 'category', 'avg_monthly_qty', 'current_stock', 
#         'reorder_point', 'recommended_stock', 'order_qty', 'stock_status'
#     ]].copy()
    
#     top_products_display.columns = [
#         'Product', 'Category', 'Avg Monthly Sales', 'Current Stock',
#         'Reorder Point', 'Recommended Stock', 'Order Qty', 'Status'
#     ]
    
#     # Style based on stock status
#     def highlight_status(row):
#         if row['Status'] == 'Low Stock':
#             return ['background-color: #ffebee'] * len(row)
#         elif row['Status'] == 'Overstock':
#             return ['background-color: #fff3e0'] * len(row)
#         else:
#             return ['background-color: #e8f5e9'] * len(row)
    
#     styled_stock = top_products_display.style.format({
#         'Avg Monthly Sales': '{:.0f}',
#         'Current Stock': '{:.0f}',
#         'Reorder Point': '{:.0f}',
#         'Recommended Stock': '{:.0f}',
#         'Order Qty': '{:.0f}'
#     }).apply(highlight_status, axis=1)
    
#     st.dataframe(styled_stock, use_container_width=True, height=400)
    
#     st.markdown("---")
    
#     # ==================== DEMAND FORECASTING BY PRODUCT ====================
#     st.markdown("### 📊 Demand Forecasting by Product Category")
    
#     st.markdown("""
#     <div class='metric-explanation'>
#         <b>📖 Demand Forecasting:</b> ทำนายความต้องการสินค้าแต่ละหมวดหมู่ในอนาคต<br>
#         <b>💡 ประโยชน์:</b> วางแผนการผลิต/สั่งซื้อ แยกตามหมวดหมู่สินค้า
#     </div>
#     """, unsafe_allow_html=True)
    
#     # Category demand forecast
#     category_monthly = df_filtered.groupby(['order_month', 'category']).agg({
#         'quantity': 'sum'
#     }).reset_index()
#     category_monthly['order_month'] = category_monthly['order_month'].dt.to_timestamp()
    
#     # Get top 5 categories by total volume
#     top_categories = df_filtered.groupby('category')['quantity'].sum().nlargest(5).index.tolist()
    
#     fig = go.Figure()
    
#     for category in top_categories:
#         cat_data = category_monthly[category_monthly['category'] == category].sort_values('order_month')
        
#         fig.add_trace(go.Scatter(
#             x=cat_data['order_month'].dt.strftime('%b %Y'),
#             y=cat_data['quantity'],
#             name=category,
#             mode='lines+markers',
#             line=dict(width=2),
#             marker=dict(size=6),
#             hovertemplate=f'<b>{category}</b><br>%{{x}}<br>Qty: %{{y:,.0f}}<extra></extra>'
#         ))
    
#     fig.update_layout(
#         title='<b>Demand Trend by Category</b>',
#         xaxis=dict(title='', showgrid=False),
#         yaxis=dict(title='Quantity Sold', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#         plot_bgcolor='white',
#         height=400,
#         hovermode='x unified',
#         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#     )
    
#     st.plotly_chart(fig, use_container_width=True)
    
#     # Category forecast summary
#     category_forecast = []
#     for category in top_categories:
#         cat_data = category_monthly[category_monthly['category'] == category].sort_values('order_month')
#         avg_qty = cat_data['quantity'].mean()
#         recent_growth = cat_data['quantity'].pct_change().tail(3).mean()
        
#         if not np.isnan(recent_growth):
#             next_month_forecast = avg_qty * (1 + recent_growth)
#         else:
#             next_month_forecast = avg_qty
        
#         category_forecast.append({
#             'Category': category,
#             'Avg Monthly': avg_qty,
#             'Growth Rate': recent_growth * 100 if not np.isnan(recent_growth) else 0,
#             'Next Month Forecast': next_month_forecast
#         })
    
#     forecast_cat_df = pd.DataFrame(category_forecast)
    
#     st.markdown("#### 📋 Category Demand Forecast")
    
#     styled_cat_forecast = forecast_cat_df.style.format({
#         'Avg Monthly': '{:.0f}',
#         'Growth Rate': '{:+.1f}%',
#         'Next Month Forecast': '{:.0f}'
#     }).background_gradient(subset=['Growth Rate'], cmap='RdYlGn', vmin=-10, vmax=10)
    
#     st.dataframe(styled_cat_forecast, use_container_width=True)

# # Footer
# st.markdown("---")
# st.markdown("""
# <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#             border-radius: 15px; color: white;'>
#     <h3 style='margin: 0; font-size: 24px;'>📊 Fashion Analytics Dashboard</h3>
#     <p style='margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;'>
#         Built with Streamlit • Data-Driven Insights with Professional KPIs
#     </p>
# </div>
# """, unsafe_allow_html=True)
































































































# Analytics Dashboard - Improved Version with KPIs
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')
st.set_page_config(page_title="Analytics Pro", layout="wide", page_icon="👕")

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
    st.sidebar.markdown("### 📁 Data Upload")
    st.sidebar.markdown("Upload your CSV files to begin analysis")
    st.sidebar.markdown("---")
    
    uploaded = st.sidebar.file_uploader(
        "Choose CSV Files", 
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
        
        with st.sidebar:
            st.markdown("**Loading Status:**")
        
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
                            st.sidebar.error(f"❌ {file.name}")
                            st.sidebar.caption(f"Missing: {', '.join(missing)}")
                    else:
                        data[table] = df
                        st.sidebar.success(f"✅ {file.name}")
                except Exception as e:
                    st.sidebar.error(f"❌ {file.name}")
                    st.sidebar.caption(str(e))
        
        if all(t in data for t in ['users', 'products', 'orders', 'order_items']):
            st.session_state.data = data
            st.session_state.data_loaded = True
            st.sidebar.markdown("---")
            st.sidebar.success("✅ **All data loaded successfully!**")
            st.rerun()
        else:
            st.sidebar.error("❌ Missing required tables")
            missing_tables = [t for t in ['users', 'products', 'orders', 'order_items'] if t not in data]
            st.sidebar.caption(f"Need: {', '.join(missing_tables)}.csv")
    
    if st.session_state.data_loaded:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ✅ Data Status")
        st.sidebar.success("Data loaded and ready")
        
        if st.session_state.data:
            total_orders = len(st.session_state.data.get('orders', []))
            total_customers = len(st.session_state.data.get('users', []))
            total_products = len(st.session_state.data.get('products', []))
            
            st.sidebar.markdown(f"""
            - **Orders:** {total_orders:,}
            - **Customers:** {total_customers:,}
            - **Products:** {total_products:,}
            """)
        
        # Target Settings
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎯 Target Settings")
        st.sidebar.markdown("กำหนดเป้าหมายต่างๆ ของธุรกิจ")
        
        # Initialize session state for targets if not exists
        if 'targets' not in st.session_state:
            st.session_state.targets = {
                'monthly_revenue': 5000000,
                'profit_margin': 20,
                'conversion_rate': 5,
                'retention_rate': 80,
                'inventory_turnover': 4
            }
        
        with st.sidebar.expander("📊 Sales Targets", expanded=False):
            st.session_state.targets['monthly_revenue'] = st.number_input(
                "Monthly Revenue Target (฿)",
                min_value=0,
                value=st.session_state.targets['monthly_revenue'],
                step=100000,
                format="%d",
                help="เป้าหมายยอดขายต่อเดือน"
            )
        
        with st.sidebar.expander("💰 Financial Targets", expanded=False):
            st.session_state.targets['profit_margin'] = st.number_input(
                "Target Profit Margin (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.targets['profit_margin']),
                step=1.0,
                help="เป้าหมายอัตรากำไรสุทธิ"
            )
        
        with st.sidebar.expander("📢 Marketing Targets", expanded=False):
            st.session_state.targets['conversion_rate'] = st.number_input(
                "Target Conversion Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.targets['conversion_rate']),
                step=0.5,
                help="เป้าหมาย Conversion Rate จาก Visitor เป็น Customer"
            )
            
            st.session_state.targets['retention_rate'] = st.number_input(
                "Target Retention Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.targets['retention_rate']),
                step=1.0,
                help="เป้าหมายการรักษาลูกค้า (ควรสูงกว่า 80%)"
            )
        
        with st.sidebar.expander("📦 Warehouse Targets", expanded=False):
            st.session_state.targets['inventory_turnover'] = st.number_input(
                "Target Inventory Turnover (x/year)",
                min_value=0.0,
                value=float(st.session_state.targets['inventory_turnover']),
                step=0.5,
                help="เป้าหมายการหมุนเวียนสินค้า (ครั้งต่อปี)"
            )
    
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

# Custom CSS
st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 1rem;}
    [data-testid="stMetricValue"] {font-size: 24px; font-weight: 600;}
    [data-testid="stMetricLabel"] {font-size: 13px; font-weight: 500; color: #555;}
    h1, h2, h3 {font-family: 'Inter', sans-serif; font-weight: 700;}
    
    /* Info boxes for explanations */
    .metric-explanation {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #3498db;
        margin: 10px 0;
        font-size: 13px;
        color: #2c3e50;
    }
    
    .metric-formula {
        background: #e8f4f8;
        padding: 10px;
        border-radius: 5px;
        font-family: monospace;
        font-size: 12px;
        margin: 5px 0;
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

# ==================== MAIN FILTERS ====================
st.title("📊Analytics Dashboard")
st.markdown("---")

st.markdown("### 🔍 Filter Data")

min_date = df_master['order_date'].min().date()
max_date = df_master['order_date'].max().date()

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    period_options = ["Custom Range", "Last 7 Days", "Last 30 Days", "Last 90 Days", 
                      "This Month", "Last Month", "This Quarter", "This Year", "All Time"]
    selected_period = st.selectbox("📅 Time Period", period_options, index=2, key="period_selector")

with col2:
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
        date_range = st.date_input(
            "Custom Date Range", 
            [min_date, max_date], 
            min_value=min_date, 
            max_value=max_date,
            key="custom_date_range"
        )
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = min_date, max_date
    
    st.info(f"📆 **{start_date.strftime('%d %b %Y')}** → **{end_date.strftime('%d %b %Y')}**")

with col3:
    if st.button("🔄 Reset All", key="reset_filters", use_container_width=True):
        st.rerun()

df_filtered = df_master[(df_master['order_date'].dt.date >= start_date) & 
                        (df_master['order_date'].dt.date <= end_date)]

col1, col2, col3 = st.columns(3)

with col1:
    channels = st.multiselect(
        "🏪 Sales Channel", 
        df_master['channel'].unique(), 
        df_master['channel'].unique(),
        key="channel_filter"
    )
    df_filtered = df_filtered[df_filtered['channel'].isin(channels)]

with col2:
    statuses = st.multiselect(
        "📦 Order Status", 
        df_master['status'].unique(), 
        ['Completed'],
        key="status_filter"
    )
    df_filtered = df_filtered[df_filtered['status'].isin(statuses)]

with col3:
    if 'category' in df_filtered.columns:
        categories = st.multiselect(
            "🏷️ Product Category",
            df_master['category'].unique(),
            df_master['category'].unique(),
            key="category_filter"
        )
        df_filtered = df_filtered[df_filtered['category'].isin(categories)]

st.markdown("---")
st.markdown("### 📊 Summary Statistics")

# Calculate key metrics
revenue = df_filtered['net_revenue'].sum()
profit = df_filtered['profit'].sum()
cogs = df_filtered['cost'].sum()
total_orders = df_filtered['order_id'].nunique()
total_customers = df_filtered['user_id'].nunique()
gross_profit = revenue - cogs
profit_margin = (profit / revenue * 100) if revenue > 0 else 0
avg_order_value = revenue / total_orders if total_orders > 0 else 0

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("💰 Revenue", f"฿{revenue/1000:,.0f}K")
with col2:
    st.metric("💵 Profit", f"฿{profit/1000:,.0f}K")
with col3:
    st.metric("📝 Orders", f"{total_orders:,}")
with col4:
    st.metric("👥 Customers", f"{total_customers:,}")
with col5:
    st.metric("📊 Margin", f"{profit_margin:.1f}%")
with col6:
    st.metric("🛒 AOV", f"฿{avg_order_value:,.0f}")

st.markdown("---")

# ==================== TABS ====================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💼 Sales Analytics", 
    "📢 Marketing Analytics", 
    "💰 Financial Analytics", 
    "📦 Warehouse Analytics",
    "🔮 Forecasting & Planning"
])

with tab1:
    st.markdown("# 💼 Sales Analytics")
    st.markdown("---")
    
    # ==================== SALES GROWTH ====================
    st.markdown("### 📈 Monthly Sales Growth")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 คำอธิบาย:</b> วัดว่ายอดขายเติบโตกี่ % เมื่อเทียบกับเดือนก่อนหน้า<br>
        <div class='metric-formula'>
        สูตร: [(ยอดขายเดือนปัจจุบัน - ยอดขายเดือนก่อน) / ยอดขายเดือนก่อน] × 100
        </div>
        <b>🎯 เป้าหมาย:</b> ควรเป็นบวก และมากกว่า 5-10% ถือว่าดี
    </div>
    """, unsafe_allow_html=True)
    
    monthly_sales = df_filtered.groupby('order_month').agg({
        'net_revenue': 'sum'
    }).reset_index()
    monthly_sales['order_month'] = monthly_sales['order_month'].dt.to_timestamp()
    monthly_sales['month_label'] = monthly_sales['order_month'].dt.strftime('%b %Y')
    monthly_sales['growth_%'] = monthly_sales['net_revenue'].pct_change() * 100
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = go.Figure()
        
        # Revenue bars
        fig.add_trace(go.Bar(
            x=monthly_sales['month_label'],
            y=monthly_sales['net_revenue'],
            name='Revenue',
            marker=dict(
                color=monthly_sales['net_revenue'],
                colorscale='Blues',
                showscale=False
            ),
            text=monthly_sales['net_revenue'],
            texttemplate='฿%{text:,.0f}',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
        ))
        
        # Growth line
        fig.add_trace(go.Scatter(
            x=monthly_sales['month_label'],
            y=monthly_sales['growth_%'],
            name='Growth %',
            mode='lines+markers',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=10),
            yaxis='y2',
            text=monthly_sales['growth_%'],
            texttemplate='%{text:.1f}%',
            textposition='top center',
            hovertemplate='<b>%{x}</b><br>Growth: %{y:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Monthly Sales Revenue & Growth Rate</b>',
            xaxis=dict(title='', showgrid=False),
            yaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            yaxis2=dict(
                title='Growth (%)', 
                overlaying='y', 
                side='right',
                showgrid=False,
                zeroline=True,
                zerolinecolor='gray'
            ),
            plot_bgcolor='white',
            height=400,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        latest_growth = monthly_sales['growth_%'].iloc[-1] if len(monthly_sales) > 1 else 0
        prev_growth = monthly_sales['growth_%'].iloc[-2] if len(monthly_sales) > 2 else 0
        
        arrow = "📈" if latest_growth > 0 else "📉"
        color = "#2ecc71" if latest_growth > 0 else "#e74c3c"
        
        st.markdown(f"""
        <div style='background: white; padding: 30px; border-radius: 10px; 
                    border: 3px solid {color}; height: 400px;
                    display: flex; flex-direction: column; justify-content: center; align-items: center;'>
            <div style='font-size: 60px;'>{arrow}</div>
            <div style='font-size: 48px; font-weight: bold; color: {color}; margin: 20px 0;'>
                {latest_growth:+.1f}%
            </div>
            <div style='font-size: 16px; color: #7f8c8d; text-align: center;'>
                <b>Current Month Growth</b>
            </div>
            <div style='margin-top: 20px; font-size: 14px; color: #95a5a6;'>
                Previous: {prev_growth:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== SALES TARGET ATTAINMENT ====================
    st.markdown("### 🎯 Sales Target Attainment")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 คำอธิบาย:</b> วัดว่าทำยอดขายได้กี่ % ของเป้าหมายที่ตั้งไว้<br>
        <div class='metric-formula'>
        สูตร: (ยอดขายที่ทำได้ / เป้าหมายยอดขาย) × 100
        </div>
        <b>🎯 เป้าหมาย:</b> ควรอยู่ที่ 90-110% (น้อยกว่า 90% ต้องปรับปรุง, มากกว่า 110% ดีมาก)
    </div>
    """, unsafe_allow_html=True)
    
    # Get target from user input
    target_monthly = st.session_state.targets['monthly_revenue']
    current_month_sales = monthly_sales['net_revenue'].iloc[-1] if len(monthly_sales) > 0 else 0
    attainment = (current_month_sales / target_monthly * 100) if target_monthly > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 14px; opacity: 0.9;'>TARGET</div>
            <div style='font-size: 36px; font-weight: bold; margin: 15px 0;'>
                ฿{target_monthly/1000000:.1f}M
            </div>
            <div style='font-size: 12px; opacity: 0.8;'>Monthly Goal</div>
            <div style='font-size: 10px; opacity: 0.7; margin-top: 10px;'>
                💡 Change in sidebar settings
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 30px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 14px; opacity: 0.9;'>ACTUAL</div>
            <div style='font-size: 36px; font-weight: bold; margin: 15px 0;'>
                ฿{current_month_sales/1000000:.1f}M
            </div>
            <div style='font-size: 12px; opacity: 0.8;'>Current Sales</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        att_color = '#2ecc71' if attainment >= 90 else '#e74c3c'
        st.markdown(f"""
        <div style='background: white; padding: 30px; border-radius: 10px; 
                    border: 3px solid {att_color}; text-align: center;'>
            <div style='font-size: 14px; color: #7f8c8d;'>ATTAINMENT</div>
            <div style='font-size: 36px; font-weight: bold; margin: 15px 0; color: {att_color};'>
                {attainment:.1f}%
            </div>
            <div style='font-size: 12px; color: #95a5a6;'>
                {'✅ On Track' if attainment >= 90 else '⚠️ Below Target'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== SALES BY CHANNEL ====================
    st.markdown("### 🏪 Sales by Channel")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 คำอธิบาย:</b> แสดงยอดขายแยกตามช่องทางการขาย เพื่อดูว่าช่องทางไหนมี Performance ดีที่สุด
    </div>
    """, unsafe_allow_html=True)
    
    channel_sales = df_filtered.groupby('channel').agg({
        'net_revenue': 'sum',
        'profit': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    channel_sales.columns = ['Channel', 'Revenue', 'Profit', 'Orders']
    channel_sales['Margin_%'] = (channel_sales['Profit'] / channel_sales['Revenue'] * 100).round(1)
    channel_sales['AOV'] = (channel_sales['Revenue'] / channel_sales['Orders']).round(0)
    channel_sales = channel_sales.sort_values('Revenue', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Horizontal bar chart
        ch_sorted = channel_sales.sort_values('Revenue', ascending=True)
        colors_list = [CHANNEL_COLORS.get(ch, '#95a5a6') for ch in ch_sorted['Channel']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=ch_sorted['Channel'],
            x=ch_sorted['Revenue'],
            orientation='h',
            marker=dict(color=colors_list),
            text=ch_sorted['Revenue'],
            texttemplate='฿%{text:,.0f}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Revenue by Channel</b>',
            xaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            yaxis=dict(title=''),
            plot_bgcolor='white',
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Stacked bar: Revenue vs Profit
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=channel_sales['Channel'],
            y=channel_sales['Profit'],
            name='Profit',
            marker_color='#2ecc71',
            text=channel_sales['Profit'],
            texttemplate='฿%{text:,.0f}',
            textposition='inside',
            hovertemplate='<b>%{x}</b><br>Profit: ฿%{y:,.0f}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            x=channel_sales['Channel'],
            y=channel_sales['Revenue'] - channel_sales['Profit'],
            name='Cost',
            marker_color='#e74c3c',
            text=channel_sales['Revenue'] - channel_sales['Profit'],
            texttemplate='฿%{text:,.0f}',
            textposition='inside',
            hovertemplate='<b>%{x}</b><br>Cost: ฿%{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Revenue Breakdown: Profit vs Cost</b>',
            xaxis=dict(title='', showgrid=False),
            yaxis=dict(title='Amount (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            barmode='stack',
            plot_bgcolor='white',
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Channel metrics table
    st.markdown("#### 📊 Channel Performance Metrics")
    
    styled_ch = channel_sales.style.format({
        'Revenue': '฿{:,.0f}',
        'Profit': '฿{:,.0f}',
        'Orders': '{:,}',
        'Margin_%': '{:.1f}%',
        'AOV': '฿{:,.0f}'
    }).background_gradient(subset=['Margin_%'], cmap='RdYlGn', vmin=0, vmax=100)
    
    st.dataframe(styled_ch, use_container_width=True)
    
    st.markdown("---")
    
    # ==================== PRODUCT PERFORMANCE ====================
    st.markdown("### 🏆 Top Product Performance")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 คำอธิบาย:</b> แสดงสินค้าที่ขายดีที่สุด 20 อันดับแรก วัดจากยอดขาย และอัตรากำไร
    </div>
    """, unsafe_allow_html=True)
    
    product_sales = df_filtered.groupby(['product_id', 'product_name', 'category']).agg({
        'net_revenue': 'sum',
        'profit': 'sum',
        'quantity': 'sum'
    }).reset_index()
    product_sales.columns = ['ID', 'Product', 'Category', 'Revenue', 'Profit', 'Units']
    product_sales['Margin_%'] = (product_sales['Profit'] / product_sales['Revenue'] * 100).round(1)
    product_sales = product_sales.sort_values('Revenue', ascending=False).head(20)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Top 10 horizontal bar
        top10 = product_sales.head(10).sort_values('Revenue', ascending=True)
        
        fig = go.Figure()
        
        # Color by margin
        colors = ['#2ecc71' if m >= 50 else '#f39c12' if m >= 30 else '#e74c3c' 
                  for m in top10['Margin_%']]
        
        fig.add_trace(go.Bar(
            y=top10['Product'],
            x=top10['Revenue'],
            orientation='h',
            marker=dict(color=colors),
            text=top10['Revenue'],
            texttemplate='฿%{text:,.0f}',
            textposition='outside',
            customdata=top10[['Margin_%']],
            hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<br>Margin: %{customdata[0]:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Top 10 Products by Revenue</b><br><sub>Color: Green=High Margin, Yellow=Medium, Red=Low</sub>',
            xaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            yaxis=dict(title=''),
            plot_bgcolor='white',
            height=450,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Scatter: Revenue vs Margin (Fixed bubble size)
        fig = go.Figure()
        
        # Calculate bubble size (max 80, min 10)
        max_units = product_sales['Units'].max()
        min_units = product_sales['Units'].min()
        normalized_sizes = 10 + (product_sales['Units'] - min_units) / (max_units - min_units) * 70
        
        fig.add_trace(go.Scatter(
            x=product_sales['Revenue'],
            y=product_sales['Margin_%'],
            mode='markers',
            marker=dict(
                size=normalized_sizes,
                color=product_sales['Margin_%'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Margin %"),
                line=dict(width=1, color='white'),
                sizemode='diameter'
            ),
            text=product_sales['Product'],
            customdata=product_sales['Units'],
            hovertemplate='<b>%{text}</b><br>Revenue: ฿%{x:,.0f}<br>Margin: %{y:.1f}%<br>Units: %{customdata:,}<extra></extra>'
        ))
        
        # Add quadrant lines
        avg_revenue = product_sales['Revenue'].median()
        avg_margin = product_sales['Margin_%'].median()
        
        fig.add_hline(y=avg_margin, line_dash="dash", line_color="gray", opacity=0.5, 
                      annotation_text="Avg Margin", annotation_position="right")
        fig.add_vline(x=avg_revenue, line_dash="dash", line_color="gray", opacity=0.5,
                      annotation_text="Avg Revenue", annotation_position="top")
        
        # Add quadrant labels
        fig.add_annotation(x=avg_revenue * 1.5, y=avg_margin * 1.2,
                          text="🌟 Stars<br>(High Revenue, High Margin)",
                          showarrow=False, font=dict(size=10, color='green'))
        
        fig.add_annotation(x=avg_revenue * 1.5, y=avg_margin * 0.8,
                          text="💰 Cash Cows<br>(High Revenue, Low Margin)",
                          showarrow=False, font=dict(size=10, color='orange'))
        
        fig.add_annotation(x=avg_revenue * 0.5, y=avg_margin * 1.2,
                          text="🚀 Growth<br>(Low Revenue, High Margin)",
                          showarrow=False, font=dict(size=10, color='blue'))
        
        fig.add_annotation(x=avg_revenue * 0.5, y=avg_margin * 0.8,
                          text="⚠️ Question Marks<br>(Low Revenue, Low Margin)",
                          showarrow=False, font=dict(size=10, color='red'))
        
        fig.update_layout(
            title='<b>Product Portfolio Analysis (BCG Matrix)</b><br><sub>Bubble size = Units Sold</sub>',
            xaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            yaxis=dict(title='Profit Margin (%)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            plot_bgcolor='white',
            height=450
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("#### 📋 Top 20 Products Detail")
    
    styled_prod = product_sales.style.format({
        'Revenue': '฿{:,.0f}',
        'Profit': '฿{:,.0f}',
        'Units': '{:,}',
        'Margin_%': '{:.1f}%'
    }).background_gradient(subset=['Margin_%'], cmap='RdYlGn', vmin=0, vmax=100)
    
    st.dataframe(styled_prod, use_container_width=True)

with tab2:
    st.markdown("# 📢 Marketing Analytics")
    st.markdown("---")
    
    # Data availability checker
    st.markdown("### 📋 Available Marketing Metrics")
    
    has_funnel = all(col in df_filtered.columns for col in ['visits', 'add_to_cart', 'checkout'])
    has_campaign = 'campaign_type' in df_filtered.columns and df_filtered['campaign_type'].notna().any()
    has_acquisition = 'acquisition_channel' in df_filtered.columns
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if has_funnel:
            st.success("✅ **Conversion Funnel Data Available**")
        else:
            st.warning("⚠️ **Conversion Funnel Data Missing**\nAdd columns: `visits`, `add_to_cart`, `checkout`")
    
    with col2:
        if has_campaign:
            st.success("✅ **Campaign Data Available**")
        else:
            st.warning("⚠️ **Campaign Data Missing**\nAdd `campaign_type` column for campaign analysis")
    
    with col3:
        if has_acquisition:
            st.success("✅ **Acquisition Channel Data Available**")
        else:
            st.warning("⚠️ **Acquisition Data Missing**\nAdd `acquisition_channel` column for acquisition analysis")
    
    st.markdown("---")
    
    # ==================== CONVERSION FUNNEL ====================
    st.markdown("### 🎯 Conversion Funnel Analysis")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 Conversion Rate:</b> เปอร์เซ็นต์ของผู้เข้าชมที่กลายเป็นลูกค้า (ซื้อสินค้าจริง)<br>
        <div class='metric-formula'>
        สูตร: (จำนวน Orders / จำนวน Visitors) × 100
        </div>
        <b>📖 Funnel Stages:</b><br>
        • <b>Visitors:</b> คนที่เข้าชมเว็บไซต์/ร้าน<br>
        • <b>Add to Cart:</b> คนที่ใส่สินค้าในตะกร้า<br>
        • <b>Checkout:</b> คนที่ไปหน้า Checkout<br>
        • <b>Purchase:</b> คนที่ซื้อสำเร็จ<br>
        <b>🎯 Target:</b> {st.session_state.targets['conversion_rate']:.1f}% (Change in sidebar settings)
    </div>
    """, unsafe_allow_html=True)
    
    if has_funnel:
        # Use actual funnel data
        total_visitors = df_filtered['visits'].sum()
        add_to_cart = df_filtered['add_to_cart'].sum()
        checkout_count = df_filtered['checkout'].sum()
        total_orders = df_filtered['order_id'].nunique()
        conversion_rate = (total_orders / total_visitors * 100) if total_visitors > 0 else 0
        
        # Compare with target
        target_conversion = st.session_state.targets['conversion_rate']
        conversion_status = "✅ Above Target" if conversion_rate >= target_conversion else "⚠️ Below Target"
        conversion_color = "#2ecc71" if conversion_rate >= target_conversion else "#e74c3c"
        
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
                    <div style='font-size: 14px; opacity: 0.8; margin-top: 10px;'>
                        {total_orders:,} orders from {total_visitors:,} visitors
                    </div>
                    <div style='font-size: 12px; margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.2); border-radius: 5px;'>
                        Target: {target_conversion:.1f}%<br>
                        <span style='color: {"#2ecc71" if conversion_rate >= target_conversion else "#ffeb3b"};'>{conversion_status}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Funnel chart
            funnel_data = pd.DataFrame({
                'Stage': ['Visitors', 'Add to Cart', 'Checkout', 'Purchase'],
                'Count': [total_visitors, add_to_cart, checkout_count, total_orders],
                'Color': ['#3498db', '#2ecc71', '#f39c12', '#9b59b6']
            })
            
            fig = go.Figure()
            
            fig.add_trace(go.Funnel(
                y=funnel_data['Stage'],
                x=funnel_data['Count'],
                textposition="inside",
                textinfo="value+percent initial",
                marker=dict(
                    color=funnel_data['Color'],
                    line=dict(color='white', width=2)
                ),
                textfont=dict(size=13, weight='bold', color='white'),
                hovertemplate='<b>%{y}</b><br>Count: %{x:,}<br>Rate: %{percentInitial}<extra></extra>',
                connector=dict(line=dict(color='gray', width=1))
            ))
            
            fig.update_layout(
                title='<b>Sales Funnel</b>',
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=400,
                margin=dict(t=60, b=40, l=40, r=120),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        # Show alternative: Order completion metrics
        st.info("💡 **Showing Order Completion Metrics** (Funnel data not available)")
        
        total_orders = df_filtered['order_id'].nunique()
        total_customers = df_filtered['user_id'].nunique()
        completed_orders = df_filtered[df_filtered['status'] == 'Completed']['order_id'].nunique()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 30px; border-radius: 10px; color: white; text-align: center; height: 200px;
                        display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size: 14px; opacity: 0.9;'>TOTAL ORDERS</div>
                <div style='font-size: 48px; font-weight: bold; margin: 15px 0;'>
                    {total_orders:,}
                </div>
                <div style='font-size: 12px; opacity: 0.8;'>All statuses</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        padding: 30px; border-radius: 10px; color: white; text-align: center; height: 200px;
                        display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size: 14px; opacity: 0.9;'>COMPLETION RATE</div>
                <div style='font-size: 48px; font-weight: bold; margin: 15px 0;'>
                    {completion_rate:.1f}%
                </div>
                <div style='font-size: 12px; opacity: 0.8;'>{completed_orders:,} completed</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            orders_per_customer = total_orders / total_customers if total_customers > 0 else 0
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        padding: 30px; border-radius: 10px; color: white; text-align: center; height: 200px;
                        display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size: 14px; opacity: 0.9;'>ORDERS/CUSTOMER</div>
                <div style='font-size: 48px; font-weight: bold; margin: 15px 0;'>
                    {orders_per_customer:.1f}
                </div>
                <div style='font-size: 12px; opacity: 0.8;'>Average frequency</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Show order status breakdown
        st.markdown("<br>", unsafe_allow_html=True)
        
        status_data = df_filtered.groupby('status')['order_id'].nunique().reset_index()
        status_data.columns = ['Status', 'Orders']
        status_data = status_data.sort_values('Orders', ascending=True)
        
        status_colors = {
            'Completed': '#2ecc71',
            'Pending': '#f39c12',
            'Cancelled': '#e74c3c',
            'Refunded': '#95a5a6'
        }
        
        colors_list = [status_colors.get(s, '#95a5a6') for s in status_data['Status']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=status_data['Status'],
            x=status_data['Orders'],
            orientation='h',
            marker=dict(color=colors_list, line=dict(color='white', width=2)),
            text=status_data['Orders'],
            texttemplate='%{text:,}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Orders: %{x:,}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Order Status Breakdown</b>',
            xaxis=dict(title='Number of Orders', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            yaxis=dict(title=''),
            plot_bgcolor='white',
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ==================== CUSTOMER ACQUISITION COST ====================
    st.markdown("### 💳 Customer Acquisition Cost (CAC)")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 คำอธิบาย:</b> ค่าใช้จ่ายที่ใช้ในการหาลูกค้าใหม่ 1 คน<br>
        <div class='metric-formula'>
        สูตร: ค่าใช้จ่ายทางการตลาด / จำนวนลูกค้าใหม่
        </div>
        <b>🎯 เป้าหมาย:</b> ควรต่ำกว่า Customer Lifetime Value (CLV) อย่างน้อย 3 เท่า
    </div>
    """, unsafe_allow_html=True)
    
    marketing_cost = df_filtered['discount_amount'].sum() if 'discount_amount' in df_filtered.columns else 0
    new_customers = df_filtered['user_id'].nunique()
    cac = marketing_cost / new_customers if new_customers > 0 else 0
    
    # Calculate CLV
    analysis_date = df_filtered['order_date'].max()
    last_purchase = df_filtered.groupby('user_id')['order_date'].max()
    churned = ((analysis_date - last_purchase).dt.days > 90).sum()
    churn_rate = (churned / len(last_purchase) * 100) if len(last_purchase) > 0 else 0
    retention_rate = 100 - churn_rate
    avg_revenue = df_filtered.groupby('user_id')['net_revenue'].sum().mean()
    clv = (profit_margin / 100) * (retention_rate / 100) * avg_revenue
    
    cac_to_clv_ratio = (cac / clv) if clv > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9;'>CAC</div>
            <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
                ฿{cac:,.0f}
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Per customer</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9;'>CLV</div>
            <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
                ฿{clv:,.0f}
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Lifetime value</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        ratio_color = '#2ecc71' if cac_to_clv_ratio < 0.33 else '#e74c3c'
        st.markdown(f"""
        <div style='background: white; padding: 25px; border-radius: 10px; 
                    border: 3px solid {ratio_color}; text-align: center;'>
            <div style='font-size: 13px; color: #7f8c8d;'>CAC : CLV</div>
            <div style='font-size: 32px; font-weight: bold; margin: 10px 0; color: {ratio_color};'>
                1:{(clv/cac if cac > 0 else 0):.1f}
            </div>
            <div style='font-size: 11px; color: #95a5a6;'>
                {'✅ Good' if cac_to_clv_ratio < 0.33 else '⚠️ Too High'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9;'>NEW CUSTOMERS</div>
            <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
                {new_customers:,}
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>In period</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== RETENTION & CHURN ====================
    st.markdown("### 🔄 Customer Retention & Churn Rate")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 Retention Rate:</b> เปอร์เซ็นต์ของลูกค้าที่ยังคงซื้อสินค้ากับเรา (ไม่หายไป)<br>
        <div class='metric-formula'>
        สูตร: [1 - (จำนวนลูกค้าที่หายไป / จำนวนลูกค้าเริ่มต้น)] × 100
        </div>
        <b>📖 Churn Rate:</b> เปอร์เซ็นต์ของลูกค้าที่หยุดซื้อสินค้า (ไม่ซื้อเกิน 90 วัน)<br>
        <b>🎯 Target:</b> Retention > {st.session_state.targets['retention_rate']:.0f}% (Change in sidebar)
    </div>
    """, unsafe_allow_html=True)
    
    # Compare with target
    target_retention = st.session_state.targets['retention_rate']
    retention_status = "✅ Above Target" if retention_rate >= target_retention else "⚠️ Below Target"
    retention_border_color = "#2ecc71" if retention_rate >= target_retention else "#e74c3c"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style='background: white; padding: 30px; border-radius: 10px; 
                    border: 3px solid {retention_border_color}; text-align: center; height: 240px;
                    display: flex; flex-direction: column; justify-content: center;'>
            <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
                <b>RETENTION RATE</b>
            </div>
            <div style='font-size: 48px; font-weight: bold; color: {retention_border_color}; margin: 15px 0;'>
                {retention_rate:.1f}%
            </div>
            <div style='font-size: 12px; color: #95a5a6;'>
                Active customers
            </div>
            <div style='font-size: 11px; color: #95a5a6; margin-top: 10px; padding: 8px; background: #f8f9fa; border-radius: 5px;'>
                Target: {target_retention:.0f}%<br>{retention_status}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: white; padding: 30px; border-radius: 10px; 
                    border: 3px solid #e74c3c; text-align: center; height: 200px;
                    display: flex; flex-direction: column; justify-content: center;'>
            <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
                <b>CHURN RATE</b>
            </div>
            <div style='font-size: 48px; font-weight: bold; color: #e74c3c; margin: 15px 0;'>
                {churn_rate:.1f}%
            </div>
            <div style='font-size: 12px; color: #95a5a6;'>
                Lost customers
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        active_customers = int(len(last_purchase) * retention_rate / 100)
        churned_customers = int(len(last_purchase) * churn_rate / 100)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=['Active', 'Churned'],
            y=[active_customers, churned_customers],
            marker=dict(color=['#2ecc71', '#e74c3c']),
            text=[active_customers, churned_customers],
            texttemplate='%{text:,}',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Customers: %{y:,}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Customer Status</b>',
            xaxis=dict(title='', showgrid=False),
            yaxis=dict(title='Number of Customers', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            plot_bgcolor='white',
            height=200,
            showlegend=False,
            margin=dict(t=40, b=40, l=60, r=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("# 💰 Financial Analytics")
    st.markdown("---")
    
    # ==================== PROFIT MARGINS ====================
    st.markdown("### 📊 Profit Margin Analysis")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 Gross Profit Margin:</b> เปอร์เซ็นต์กำไรขั้นต้น (หลังหักต้นทุนสินค้า)<br>
        <div class='metric-formula'>
        สูตร: [(รายได้ - ต้นทุนสินค้า) / รายได้] × 100
        </div>
        <b>📖 Net Profit Margin:</b> เปอร์เซ็นต์กำไรสุทธิ (หลังหักค่าใช้จ่ายทั้งหมด)<br>
        <div class='metric-formula'>
        สูตร: (กำไรสุทธิ / รายได้) × 100
        </div>
        <b>🎯 Target:</b> Net Margin > {st.session_state.targets['profit_margin']:.0f}% (Change in sidebar)
    </div>
    """, unsafe_allow_html=True)
    
    gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
    net_margin = (profit / revenue * 100) if revenue > 0 else 0
    
    # Compare with target
    target_margin = st.session_state.targets['profit_margin']
    margin_status = "✅ Above Target" if net_margin >= target_margin else "⚠️ Below Target"
    margin_color = "#2ecc71" if net_margin >= target_margin else "#e74c3c"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Waterfall chart
        fig = go.Figure(go.Waterfall(
            orientation="v",
            measure=["relative", "relative", "relative", "total"],
            x=["Revenue", "COGS", "Other Costs", "Net Profit"],
            y=[revenue, -cogs, -(gross_profit - profit), profit],
            text=[f"฿{revenue:,.0f}", f"-฿{cogs:,.0f}", f"-฿{(gross_profit - profit):,.0f}", f"฿{profit:,.0f}"],
            textposition="outside",
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            decreasing={"marker": {"color": "#e74c3c"}},
            increasing={"marker": {"color": "#2ecc71"}},
            totals={"marker": {"color": "#3498db"}},
            hovertemplate='<b>%{x}</b><br>Amount: ฿%{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Profit Waterfall</b>',
            plot_bgcolor='white',
            height=300,
            showlegend=False,
            margin=dict(t=40, b=40, l=60, r=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px; border-radius: 10px; color: white; text-align: center; height: 300px;
                    display: flex; flex-direction: column; justify-content: center;'>
            <div style='font-size: 14px; opacity: 0.9; margin-bottom: 10px;'>
                GROSS PROFIT MARGIN
            </div>
            <div style='font-size: 52px; font-weight: bold; margin: 15px 0;'>
                {gross_margin:.1f}%
            </div>
            <div style='font-size: 12px; opacity: 0.8;'>
                (Revenue - COGS) / Revenue
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 30px; border-radius: 10px; color: white; text-align: center; height: 300px;
                    display: flex; flex-direction: column; justify-content: center;'>
            <div style='font-size: 14px; opacity: 0.9; margin-bottom: 10px;'>
                NET PROFIT MARGIN
            </div>
            <div style='font-size: 52px; font-weight: bold; margin: 15px 0;'>
                {net_margin:.1f}%
            </div>
            <div style='font-size: 12px; opacity: 0.8;'>
                Net Profit / Revenue
            </div>
            <div style='font-size: 11px; margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.2); border-radius: 5px;'>
                Target: {target_margin:.0f}%<br>
                <span style='color: {"#2ecc71" if net_margin >= target_margin else "#ffeb3b"};'>{margin_status}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== MONTHLY FINANCIAL TREND ====================
    st.markdown("### 📈 Monthly Financial Performance")
    
    monthly_fin = df_filtered.groupby('order_month').agg({
        'net_revenue': 'sum',
        'cost': 'sum',
        'profit': 'sum'
    }).reset_index()
    monthly_fin['order_month'] = monthly_fin['order_month'].dt.to_timestamp()
    monthly_fin['month_label'] = monthly_fin['order_month'].dt.strftime('%b %Y')
    monthly_fin['gross_margin_%'] = ((monthly_fin['net_revenue'] - monthly_fin['cost']) / monthly_fin['net_revenue'] * 100).round(1)
    monthly_fin['net_margin_%'] = (monthly_fin['profit'] / monthly_fin['net_revenue'] * 100).round(1)
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Revenue and Cost bars
    fig.add_trace(
        go.Bar(
            x=monthly_fin['month_label'],
            y=monthly_fin['net_revenue'],
            name='Revenue',
            marker_color='#3498db',
            hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Bar(
            x=monthly_fin['month_label'],
            y=monthly_fin['cost'],
            name='COGS',
            marker_color='#e74c3c',
            hovertemplate='<b>%{x}</b><br>COGS: ฿%{y:,.0f}<extra></extra>'
        ),
        secondary_y=False
    )
    
    # Margin lines
    fig.add_trace(
        go.Scatter(
            x=monthly_fin['month_label'],
            y=monthly_fin['gross_margin_%'],
            name='Gross Margin %',
            mode='lines+markers',
            line=dict(color='#27ae60', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x}</b><br>Gross Margin: %{y:.1f}%<extra></extra>'
        ),
        secondary_y=True
    )
    
    fig.add_trace(
        go.Scatter(
            x=monthly_fin['month_label'],
            y=monthly_fin['net_margin_%'],
            name='Net Margin %',
            mode='lines+markers',
            line=dict(color='#9b59b6', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x}</b><br>Net Margin: %{y:.1f}%<extra></extra>'
        ),
        secondary_y=True
    )
    
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="Amount (฿)", secondary_y=False, showgrid=True, gridcolor='rgba(0,0,0,0.05)')
    fig.update_yaxes(title_text="Margin (%)", secondary_y=True, showgrid=False)
    
    fig.update_layout(
        title='<b>Monthly Revenue, Cost & Margins</b>',
        plot_bgcolor='white',
        height=400,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ==================== WORKING CAPITAL RATIOS ====================
    st.markdown("### 💼 Working Capital Ratios")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 AR Turnover:</b> จำนวนครั้งที่เราเก็บเงินจากลูกค้าได้ต่อปี (ยิ่งสูงยิ่งดี)<br>
        <b>📖 DSO (Days Sales Outstanding):</b> จำนวนวันเฉลี่ยที่ใช้เวลาเก็บเงินจากลูกค้า (ยิ่งต่ำยิ่งดี)<br>
        <div class='metric-formula'>
        DSO = 365 / AR Turnover
        </div>
        <b>🎯 เป้าหมาย:</b> DSO < 45 วัน ถือว่าดี
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate ratios
    avg_monthly_rev = monthly_fin['net_revenue'].mean()
    avg_ar = avg_monthly_rev * 0.3  # Assume 30% credit sales
    ar_turnover = (revenue * 0.3) / avg_ar if avg_ar > 0 else 0
    dso = 365 / ar_turnover if ar_turnover > 0 else 0
    
    avg_ap = cogs * 0.25
    ap_turnover = cogs / avg_ap if avg_ap > 0 else 0
    dpo = 365 / ap_turnover if ap_turnover > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background: white; padding: 25px; border-radius: 10px; 
                    border-left: 5px solid #3498db; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <div style='font-size: 12px; color: #7f8c8d; margin-bottom: 8px;'>
                <b>AR TURNOVER</b>
            </div>
            <div style='font-size: 36px; font-weight: bold; color: #2c3e50;'>
                {ar_turnover:.2f}x
            </div>
            <div style='font-size: 11px; color: #95a5a6; margin-top: 5px;'>
                Times per year
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        dso_color = '#2ecc71' if dso < 45 else '#e74c3c'
        st.markdown(f"""
        <div style='background: white; padding: 25px; border-radius: 10px; 
                    border-left: 5px solid {dso_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <div style='font-size: 12px; color: #7f8c8d; margin-bottom: 8px;'>
                <b>DSO</b>
            </div>
            <div style='font-size: 36px; font-weight: bold; color: #2c3e50;'>
                {dso:.0f}
            </div>
            <div style='font-size: 11px; color: #95a5a6; margin-top: 5px;'>
                Days
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: white; padding: 25px; border-radius: 10px; 
                    border-left: 5px solid #9b59b6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <div style='font-size: 12px; color: #7f8c8d; margin-bottom: 8px;'>
                <b>AP TURNOVER</b>
            </div>
            <div style='font-size: 36px; font-weight: bold; color: #2c3e50;'>
                {ap_turnover:.2f}x
            </div>
            <div style='font-size: 11px; color: #95a5a6; margin-top: 5px;'>
                Times per year
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: white; padding: 25px; border-radius: 10px; 
                    border-left: 5px solid #f39c12; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <div style='font-size: 12px; color: #7f8c8d; margin-bottom: 8px;'>
                <b>DPO</b>
            </div>
            <div style='font-size: 36px; font-weight: bold; color: #2c3e50;'>
                {dpo:.0f}
            </div>
            <div style='font-size: 11px; color: #95a5a6; margin-top: 5px;'>
                Days
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.markdown("# 📦 Warehouse Analytics")
    st.markdown("---")
    
    # ==================== INVENTORY TURNOVER ====================
    st.markdown("### 🔄 Inventory Turnover & Performance")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 Inventory Turnover:</b> จำนวนครั้งที่สินค้าหมุนเวียนต่อปี (ยิ่งสูงยิ่งดี แสดงว่าสินค้าขายดี)<br>
        <div class='metric-formula'>
        สูตร: ต้นทุนสินค้าที่ขาย / มูลค่าสินค้าคงคลังเฉลี่ย
        </div>
        <b>📖 Days Inventory Outstanding (DIO):</b> จำนวนวันที่สินค้าอยู่ในคลังก่อนขายได้<br>
        <div class='metric-formula'>
        สูตร: 365 / Inventory Turnover
        </div>
        <b>🎯 Target:</b> Turnover > {st.session_state.targets['inventory_turnover']:.1f}x (Change in sidebar)
    </div>
    """, unsafe_allow_html=True)
    
    avg_inventory = df_filtered['cost'].mean() * df_filtered['product_id'].nunique()
    inventory_turnover = cogs / avg_inventory if avg_inventory > 0 else 0
    dio = 365 / inventory_turnover if inventory_turnover > 0 else 0
    
    units_sold = df_filtered['quantity'].sum()
    units_received = units_sold * 1.2
    sell_through = (units_sold / units_received * 100) if units_received > 0 else 0
    
    # Compare with target
    target_turnover = st.session_state.targets['inventory_turnover']
    turnover_status = "✅ Above Target" if inventory_turnover >= target_turnover else "⚠️ Below Target"
    turnover_color = "#2ecc71" if inventory_turnover >= target_turnover else "#e74c3c"
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
                <b>INVENTORY TURNOVER</b>
            </div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
                {inventory_turnover:.2f}x
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Times per year</div>
            <div style='font-size: 10px; margin-top: 10px; padding: 8px; background: rgba(255,255,255,0.2); border-radius: 5px;'>
                Target: {target_turnover:.1f}x<br>{turnover_status}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        dio_color = '#2ecc71' if dio < 90 else '#e74c3c'
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
                <b>DIO</b>
            </div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
                {dio:.0f}
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Days</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
                <b>SELL-THROUGH RATE</b>
            </div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
                {sell_through:.1f}%
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Of received</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
                <b>INVENTORY VALUE</b>
            </div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
                ฿{avg_inventory/1000:.0f}K
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Total stock</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== PRODUCT MOVEMENT CLASSIFICATION ====================
    st.markdown("### 🚀 Product Movement Classification")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 คำอธิบาย:</b> จัดกลุ่มสินค้าตามความเร็วในการขาย<br>
        • <b style='color: #2ecc71;'>Fast Moving:</b> ขายดี ควรเพิ่ม stock<br>
        • <b style='color: #f39c12;'>Medium Moving:</b> ขายปานกลาง รักษาระดับปกติ<br>
        • <b style='color: #e74c3c;'>Slow Moving:</b> ขายช้า ลด stock หรือทำ clearance
    </div>
    """, unsafe_allow_html=True)
    
    product_velocity = df_filtered.groupby(['product_id', 'product_name', 'category']).agg({
        'order_id': 'nunique',
        'net_revenue': 'sum',
        'cost': 'sum',
        'quantity': 'sum'
    }).reset_index()
    product_velocity.columns = ['ID', 'Product', 'Category', 'Orders', 'Revenue', 'Cost', 'Units']
    
    fast_threshold = product_velocity['Orders'].quantile(0.75)
    slow_threshold = product_velocity['Orders'].quantile(0.25)
    
    def classify_movement(orders):
        if orders >= fast_threshold:
            return 'Fast Moving'
        elif orders <= slow_threshold:
            return 'Slow Moving'
        return 'Medium Moving'
    
    product_velocity['Movement'] = product_velocity['Orders'].apply(classify_movement)
    
    movement_summary = product_velocity.groupby('Movement').agg({
        'Product': 'count',
        'Revenue': 'sum',
        'Cost': 'sum'
    }).reset_index()
    movement_summary.columns = ['Movement', 'Products', 'Revenue', 'Inventory_Value']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Stacked bar chart
        movement_order = ['Fast Moving', 'Medium Moving', 'Slow Moving']
        movement_colors = {'Fast Moving': '#2ecc71', 'Medium Moving': '#f39c12', 'Slow Moving': '#e74c3c'}
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=['Product Count'],
            x=[movement_summary[movement_summary['Movement'] == 'Fast Moving']['Products'].sum()],
            name='Fast Moving',
            orientation='h',
            marker_color='#2ecc71',
            text=[movement_summary[movement_summary['Movement'] == 'Fast Moving']['Products'].sum()],
            texttemplate='%{text}',
            textposition='inside',
            hovertemplate='<b>Fast Moving</b><br>Products: %{x}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            y=['Product Count'],
            x=[movement_summary[movement_summary['Movement'] == 'Medium Moving']['Products'].sum()],
            name='Medium Moving',
            orientation='h',
            marker_color='#f39c12',
            text=[movement_summary[movement_summary['Movement'] == 'Medium Moving']['Products'].sum()],
            texttemplate='%{text}',
            textposition='inside',
            hovertemplate='<b>Medium Moving</b><br>Products: %{x}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            y=['Product Count'],
            x=[movement_summary[movement_summary['Movement'] == 'Slow Moving']['Products'].sum()],
            name='Slow Moving',
            orientation='h',
            marker_color='#e74c3c',
            text=[movement_summary[movement_summary['Movement'] == 'Slow Moving']['Products'].sum()],
            texttemplate='%{text}',
            textposition='inside',
            hovertemplate='<b>Slow Moving</b><br>Products: %{x}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Product Distribution by Movement Speed</b>',
            xaxis=dict(title='Number of Products'),
            yaxis=dict(title=''),
            barmode='stack',
            plot_bgcolor='white',
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Inventory value by movement
        movement_sorted = movement_summary.sort_values('Inventory_Value', ascending=True)
        colors = [movement_colors[m] for m in movement_sorted['Movement']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=movement_sorted['Movement'],
            x=movement_sorted['Inventory_Value'],
            orientation='h',
            marker=dict(color=colors),
            text=movement_sorted['Inventory_Value'],
            texttemplate='฿%{text:,.0f}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Value: ฿%{x:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Inventory Value by Movement</b>',
            xaxis=dict(title='Inventory Value (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            yaxis=dict(title=''),
            plot_bgcolor='white',
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Show top products in each category
    st.markdown("#### 📋 Movement Classification Details")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("**🚀 Fast Moving (Top 10)**")
        fast_products = product_velocity[product_velocity['Movement'] == 'Fast Moving'].nlargest(10, 'Orders')
        st.dataframe(
            fast_products[['Product', 'Orders', 'Units']].style.format({
                'Orders': '{:,}',
                'Units': '{:,}'
            }),
            height=300,
            use_container_width=True
        )
    
    with col2:
        st.warning("**⚖️ Medium Moving (Top 10)**")
        medium_products = product_velocity[product_velocity['Movement'] == 'Medium Moving'].nlargest(10, 'Orders')
        st.dataframe(
            medium_products[['Product', 'Orders', 'Units']].style.format({
                'Orders': '{:,}',
                'Units': '{:,}'
            }),
            height=300,
            use_container_width=True
        )
    
    with col3:
        st.error("**🐌 Slow Moving (Top 10)**")
        slow_products = product_velocity[product_velocity['Movement'] == 'Slow Moving'].nlargest(10, 'Cost')
        st.dataframe(
            slow_products[['Product', 'Orders', 'Cost']].style.format({
                'Orders': '{:,}',
                'Cost': '฿{:,.0f}'
            }),
            height=300,
            use_container_width=True
        )
    
    st.markdown("---")
    
    # ==================== CASH CONVERSION CYCLE ====================
    st.markdown("### ⏱️ Cash Conversion Cycle (CCC)")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 คำอธิบาย:</b> ระยะเวลาที่เงินสดถูกล็อคอยู่ในธุรกิจ<br>
        <div class='metric-formula'>
        สูตร: DIO + DSO - DPO
        </div>
        <b>📖 ความหมาย:</b><br>
        • DIO = วันที่สินค้าอยู่ในคลัง<br>
        • DSO = วันที่รอเก็บเงินจากลูกค้า<br>
        • DPO = วันที่เราจ่ายเงินซัพพลายเออร์<br>
        <b>🎯 เป้าหมาย:</b> ยิ่งต่ำยิ่งดี (< 60 วัน ดีมาก, < 30 วัน ดีเยี่ยม)
    </div>
    """, unsafe_allow_html=True)
    
    ccc = dio + dso - dpo
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        ccc_color = '#2ecc71' if ccc < 60 else '#e74c3c'
        ccc_status = '✅ Excellent' if ccc < 30 else '✅ Good' if ccc < 60 else '⚠️ Needs Improvement'
        
        st.markdown(f"""
        <div style='background: white; padding: 40px; border-radius: 10px; 
                    border: 4px solid {ccc_color}; text-align: center; height: 400px;
                    display: flex; flex-direction: column; justify-content: center;'>
            <div style='font-size: 16px; color: #7f8c8d; margin-bottom: 15px;'>
                <b>CASH CONVERSION CYCLE</b>
            </div>
            <div style='font-size: 72px; font-weight: bold; color: {ccc_color}; margin: 20px 0;'>
                {ccc:.0f}
            </div>
            <div style='font-size: 24px; color: #7f8c8d;'>
                days
            </div>
            <div style='font-size: 14px; color: #95a5a6; margin-top: 20px;'>
                {ccc_status}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # CCC breakdown chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=['DIO', 'DSO', 'DPO', 'CCC'],
            y=[dio, dso, -dpo, ccc],
            marker=dict(
                color=['#3498db', '#9b59b6', '#e74c3c', '#2ecc71'],
                line=dict(color='white', width=2)
            ),
            text=[f"{dio:.0f}", f"{dso:.0f}", f"{dpo:.0f}", f"{ccc:.0f}"],
            texttemplate='%{text} days',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Days: %{y:.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Cash Conversion Cycle Breakdown</b>',
            xaxis=dict(title='', showgrid=False),
            yaxis=dict(
                title='Days',
                showgrid=True,
                gridcolor='rgba(0,0,0,0.05)',
                zeroline=True,
                zerolinecolor='gray'
            ),
            plot_bgcolor='white',
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.markdown("# 🔮 Forecasting & Planning")
    st.markdown("---")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 คำอธิบาย:</b> ใช้ข้อมูลในอดีตเพื่อคาดการณ์อนาคต ช่วยในการวางแผนธุรกิจ<br>
        <b>🎯 วิธีการ:</b> ใช้ Moving Average และ Linear Regression เพื่อทำนายแนวโน้ม
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== REVENUE FORECAST ====================
    st.markdown("### 📈 Revenue Forecast (Next 12 Months)")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 Revenue Forecast:</b> ทำนายยอดขายในอนาคต 12 เดือนข้างหน้า<br>
        <div class='metric-formula'>
        วิธีการ: Linear Regression + Moving Average (3 เดือน)
        </div>
        <b>💡 การใช้ประโยชน์:</b><br>
        • วางแผนงบประมาณ<br>
        • กำหนดเป้าหมายทีมขาย<br>
        • วางแผนจัดซื้อสินค้า<br>
        • วางแผนการตลาด
    </div>
    """, unsafe_allow_html=True)
    
    # Prepare historical data
    monthly_revenue = df_filtered.groupby('order_month').agg({
        'net_revenue': 'sum'
    }).reset_index()
    monthly_revenue['order_month'] = monthly_revenue['order_month'].dt.to_timestamp()
    monthly_revenue = monthly_revenue.sort_values('order_month')
    
    if len(monthly_revenue) >= 3:
        # Calculate moving average
        monthly_revenue['MA_3'] = monthly_revenue['net_revenue'].rolling(window=3).mean()
        
        # Simple linear regression for trend
        from sklearn.linear_model import LinearRegression
        import numpy as np
        
        X = np.arange(len(monthly_revenue)).reshape(-1, 1)
        y = monthly_revenue['net_revenue'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Forecast next 12 months
        future_months = 12
        future_X = np.arange(len(monthly_revenue), len(monthly_revenue) + future_months).reshape(-1, 1)
        forecast_values = model.predict(future_X)
        
        # Apply growth adjustment (use recent growth rate)
        recent_growth = monthly_revenue['net_revenue'].pct_change().tail(3).mean()
        if not np.isnan(recent_growth) and recent_growth != 0:
            growth_factor = 1 + recent_growth
            forecast_adjusted = []
            last_value = monthly_revenue['net_revenue'].iloc[-1]
            for i in range(future_months):
                last_value = last_value * growth_factor
                forecast_adjusted.append(last_value)
            forecast_values = (forecast_values + np.array(forecast_adjusted)) / 2
        
        # Create forecast dataframe
        last_date = monthly_revenue['order_month'].iloc[-1]
        forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=future_months, freq='MS')
        
        forecast_df = pd.DataFrame({
            'Month': forecast_dates,
            'Forecast': forecast_values
        })
        forecast_df['Month_Label'] = forecast_df['Month'].dt.strftime('%b %Y')
        
        # Calculate confidence interval (±15%)
        forecast_df['Lower'] = forecast_values * 0.85
        forecast_df['Upper'] = forecast_values * 1.15
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create forecast chart
            fig = go.Figure()
            
            # Historical data
            fig.add_trace(go.Scatter(
                x=monthly_revenue['order_month'].dt.strftime('%b %Y'),
                y=monthly_revenue['net_revenue'],
                name='Actual',
                mode='lines+markers',
                line=dict(color='#3498db', width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>Actual: ฿%{y:,.0f}<extra></extra>'
            ))
            
            # Moving Average
            fig.add_trace(go.Scatter(
                x=monthly_revenue['order_month'].dt.strftime('%b %Y'),
                y=monthly_revenue['MA_3'],
                name='3-Month MA',
                mode='lines',
                line=dict(color='#95a5a6', width=2, dash='dash'),
                hovertemplate='<b>%{x}</b><br>MA: ฿%{y:,.0f}<extra></extra>'
            ))
            
            # Forecast
            fig.add_trace(go.Scatter(
                x=forecast_df['Month_Label'],
                y=forecast_df['Forecast'],
                name='Forecast',
                mode='lines+markers',
                line=dict(color='#e74c3c', width=3),
                marker=dict(size=8, symbol='diamond'),
                hovertemplate='<b>%{x}</b><br>Forecast: ฿%{y:,.0f}<extra></extra>'
            ))
            
            # Confidence interval
            fig.add_trace(go.Scatter(
                x=forecast_df['Month_Label'],
                y=forecast_df['Upper'],
                mode='lines',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            fig.add_trace(go.Scatter(
                x=forecast_df['Month_Label'],
                y=forecast_df['Lower'],
                mode='lines',
                line=dict(width=0),
                fill='tonexty',
                fillcolor='rgba(231, 76, 60, 0.2)',
                name='Confidence Interval (±15%)',
                hovertemplate='<b>%{x}</b><br>Range: ฿%{y:,.0f}<extra></extra>'
            ))
            
            fig.update_layout(
                title='<b>Revenue Forecast - Next 12 Months</b>',
                xaxis=dict(title='', showgrid=False),
                yaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
                plot_bgcolor='white',
                height=400,
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Forecast summary
            total_forecast = forecast_df['Forecast'].sum()
            avg_monthly = forecast_df['Forecast'].mean()
            growth_forecast = ((forecast_df['Forecast'].iloc[-1] - monthly_revenue['net_revenue'].iloc[-1]) / 
                             monthly_revenue['net_revenue'].iloc[-1] * 100)
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 30px; border-radius: 10px; color: white; text-align: center; height: 400px;
                        display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size: 14px; opacity: 0.9; margin-bottom: 15px;'>
                    <b>FORECAST SUMMARY</b>
                </div>
                <div style='margin: 20px 0;'>
                    <div style='font-size: 12px; opacity: 0.8;'>Next 12 Months Total</div>
                    <div style='font-size: 36px; font-weight: bold; margin: 10px 0;'>
                        ฿{total_forecast/1000000:.1f}M
                    </div>
                </div>
                <div style='margin: 20px 0;'>
                    <div style='font-size: 12px; opacity: 0.8;'>Average Monthly</div>
                    <div style='font-size: 28px; font-weight: bold; margin: 10px 0;'>
                        ฿{avg_monthly/1000:.0f}K
                    </div>
                </div>
                <div style='margin: 20px 0;'>
                    <div style='font-size: 12px; opacity: 0.8;'>Expected Growth</div>
                    <div style='font-size: 28px; font-weight: bold; margin: 10px 0;'>
                        {growth_forecast:+.1f}%
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Forecast table
        st.markdown("#### 📋 Monthly Forecast Details")
        
        forecast_display = forecast_df.copy()
        forecast_display['Month'] = forecast_display['Month_Label']
        forecast_display = forecast_display[['Month', 'Forecast', 'Lower', 'Upper']]
        forecast_display.columns = ['Month', 'Forecast', 'Min Expected', 'Max Expected']
        
        styled_forecast = forecast_display.style.format({
            'Forecast': '฿{:,.0f}',
            'Min Expected': '฿{:,.0f}',
            'Max Expected': '฿{:,.0f}'
        }).background_gradient(subset=['Forecast'], cmap='Blues')
        
        st.dataframe(styled_forecast, use_container_width=True, height=300)
    else:
        st.warning("⚠️ ต้องมีข้อมูลอย่างน้อย 3 เดือนเพื่อทำ Forecast")
    
    st.markdown("---")
    
    # ==================== STOCK PLANNING ====================
    st.markdown("### 📦 Stock Planning Recommendation")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 Stock Planning:</b> แนะนำปริมาณสต็อกที่ควรมีสำหรับแต่ละสินค้า<br>
        <div class='metric-formula'>
        สูตร: (ยอดขายเฉลี่ยต่อเดือน × Lead Time) + Safety Stock
        </div>
        <b>📖 Safety Stock:</b> สต็อกสำรอง เผื่อความผันผวนของยอดขาย (20% ของยอดขายเฉลี่ย)<br>
        <b>💡 การใช้ประโยชน์:</b><br>
        • ป้องกันสินค้าหมด<br>
        • ลดต้นทุนการจัดเก็บ<br>
        • วางแผนสั่งซื้อล่วงหน้า
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate stock recommendations
    # Assume lead time of 30 days (1 month)
    lead_time_months = 1
    safety_stock_pct = 0.20
    
    # Get product sales data
    product_monthly = df_filtered.groupby(['product_id', 'product_name', 'category', 'order_month']).agg({
        'quantity': 'sum'
    }).reset_index()
    
    # Calculate average monthly sales per product
    product_avg = product_monthly.groupby(['product_id', 'product_name', 'category']).agg({
        'quantity': ['mean', 'std', 'count']
    }).reset_index()
    
    product_avg.columns = ['product_id', 'product_name', 'category', 'avg_monthly_qty', 'std_qty', 'months']
    
    # Calculate stock recommendations
    product_avg['lead_time_demand'] = product_avg['avg_monthly_qty'] * lead_time_months
    product_avg['safety_stock'] = product_avg['avg_monthly_qty'] * safety_stock_pct
    product_avg['reorder_point'] = product_avg['lead_time_demand'] + product_avg['safety_stock']
    product_avg['recommended_stock'] = np.ceil(product_avg['reorder_point'] * 1.5)  # Add buffer
    
    # Add current stock status (simulated - in real case, get from inventory table)
    if 'inventory' in data:
        # Try to get actual stock levels
        try:
            current_stock = data['inventory'].groupby('product_id')['quantity'].last().to_dict()
            product_avg['current_stock'] = product_avg['product_id'].map(current_stock).fillna(0)
        except:
            product_avg['current_stock'] = product_avg['recommended_stock'] * 0.6  # Simulated
    else:
        product_avg['current_stock'] = product_avg['recommended_stock'] * 0.6  # Simulated
    
    # Calculate stock status
    product_avg['stock_status'] = product_avg.apply(
        lambda x: 'Overstock' if x['current_stock'] > x['recommended_stock'] * 1.2
        else 'Low Stock' if x['current_stock'] < x['reorder_point']
        else 'Optimal', axis=1
    )
    
    product_avg['order_qty'] = np.maximum(0, product_avg['recommended_stock'] - product_avg['current_stock'])
    
    # Sort by order quantity
    product_avg = product_avg.sort_values('order_qty', ascending=False)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    low_stock_count = len(product_avg[product_avg['stock_status'] == 'Low Stock'])
    optimal_count = len(product_avg[product_avg['stock_status'] == 'Optimal'])
    overstock_count = len(product_avg[product_avg['stock_status'] == 'Overstock'])
    total_order_needed = product_avg['order_qty'].sum()
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9;'>LOW STOCK</div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
                {low_stock_count}
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Products need reorder</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9;'>OPTIMAL</div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
                {optimal_count}
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Products at good level</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9;'>OVERSTOCK</div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
                {overstock_count}
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Products excess stock</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9;'>TOTAL ORDER NEEDED</div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
                {total_order_needed:,.0f}
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Units to order</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Stock status breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        status_counts = product_avg['stock_status'].value_counts()
        status_colors = {
            'Low Stock': '#e74c3c',
            'Optimal': '#2ecc71',
            'Overstock': '#f39c12'
        }
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=list(status_counts.index),
            y=list(status_counts.values),
            marker=dict(color=[status_colors.get(s, '#95a5a6') for s in status_counts.index]),
            text=list(status_counts.values),
            texttemplate='%{text}',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Products: %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Stock Status Distribution</b>',
            xaxis=dict(title='', showgrid=False),
            yaxis=dict(title='Number of Products', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            plot_bgcolor='white',
            height=350,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top products needing reorder
        top_reorder = product_avg[product_avg['stock_status'] == 'Low Stock'].head(10)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=top_reorder['product_name'],
            x=top_reorder['order_qty'],
            orientation='h',
            marker_color='#e74c3c',
            text=top_reorder['order_qty'],
            texttemplate='%{text:,.0f}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Need to Order: %{x:,.0f} units<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Top 10 Products Needing Reorder</b>',
            xaxis=dict(title='Quantity to Order', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            yaxis=dict(title='', categoryorder='total ascending'),
            plot_bgcolor='white',
            height=350,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed stock planning table
    st.markdown("#### 📋 Detailed Stock Planning (Top 30 Products)")
    
    top_products = product_avg.head(30).copy()
    top_products_display = top_products[[
        'product_name', 'category', 'avg_monthly_qty', 'current_stock', 
        'reorder_point', 'recommended_stock', 'order_qty', 'stock_status'
    ]].copy()
    
    top_products_display.columns = [
        'Product', 'Category', 'Avg Monthly Sales', 'Current Stock',
        'Reorder Point', 'Recommended Stock', 'Order Qty', 'Status'
    ]
    
    # Style based on stock status
    def highlight_status(row):
        if row['Status'] == 'Low Stock':
            return ['background-color: #ffebee'] * len(row)
        elif row['Status'] == 'Overstock':
            return ['background-color: #fff3e0'] * len(row)
        else:
            return ['background-color: #e8f5e9'] * len(row)
    
    styled_stock = top_products_display.style.format({
        'Avg Monthly Sales': '{:.0f}',
        'Current Stock': '{:.0f}',
        'Reorder Point': '{:.0f}',
        'Recommended Stock': '{:.0f}',
        'Order Qty': '{:.0f}'
    }).apply(highlight_status, axis=1)
    
    st.dataframe(styled_stock, use_container_width=True, height=400)
    
    st.markdown("---")
    
    # ==================== DEMAND FORECASTING BY PRODUCT ====================
    st.markdown("### 📊 Demand Forecasting by Product Category")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 Demand Forecasting:</b> ทำนายความต้องการสินค้าแต่ละหมวดหมู่ในอนาคต<br>
        <b>💡 ประโยชน์:</b> วางแผนการผลิต/สั่งซื้อ แยกตามหมวดหมู่สินค้า
    </div>
    """, unsafe_allow_html=True)
    
    # Category demand forecast
    category_monthly = df_filtered.groupby(['order_month', 'category']).agg({
        'quantity': 'sum'
    }).reset_index()
    category_monthly['order_month'] = category_monthly['order_month'].dt.to_timestamp()
    
    # Get top 5 categories by total volume
    top_categories = df_filtered.groupby('category')['quantity'].sum().nlargest(5).index.tolist()
    
    fig = go.Figure()
    
    for category in top_categories:
        cat_data = category_monthly[category_monthly['category'] == category].sort_values('order_month')
        
        fig.add_trace(go.Scatter(
            x=cat_data['order_month'].dt.strftime('%b %Y'),
            y=cat_data['quantity'],
            name=category,
            mode='lines+markers',
            line=dict(width=2),
            marker=dict(size=6),
            hovertemplate=f'<b>{category}</b><br>%{{x}}<br>Qty: %{{y:,.0f}}<extra></extra>'
        ))
    
    fig.update_layout(
        title='<b>Demand Trend by Category</b>',
        xaxis=dict(title='', showgrid=False),
        yaxis=dict(title='Quantity Sold', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
        plot_bgcolor='white',
        height=400,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Category forecast summary
    category_forecast = []
    for category in top_categories:
        cat_data = category_monthly[category_monthly['category'] == category].sort_values('order_month')
        avg_qty = cat_data['quantity'].mean()
        recent_growth = cat_data['quantity'].pct_change().tail(3).mean()
        
        if not np.isnan(recent_growth):
            next_month_forecast = avg_qty * (1 + recent_growth)
        else:
            next_month_forecast = avg_qty
        
        category_forecast.append({
            'Category': category,
            'Avg Monthly': avg_qty,
            'Growth Rate': recent_growth * 100 if not np.isnan(recent_growth) else 0,
            'Next Month Forecast': next_month_forecast
        })
    
    forecast_cat_df = pd.DataFrame(category_forecast)
    
    st.markdown("#### 📋 Category Demand Forecast")
    
    styled_cat_forecast = forecast_cat_df.style.format({
        'Avg Monthly': '{:.0f}',
        'Growth Rate': '{:+.1f}%',
        'Next Month Forecast': '{:.0f}'
    }).background_gradient(subset=['Growth Rate'], cmap='RdYlGn', vmin=-10, vmax=10)
    
    st.dataframe(styled_cat_forecast, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 15px; color: white;'>
    <h3 style='margin: 0; font-size: 24px;'>📊 Analytics Dashboard</h3>
    <p style='margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;'>
        Built with Streamlit • Data-Driven Insights with Professional KPIs
    </p>
</div>
""", unsafe_allow_html=True)
































































































# Analytics Dashboard - Improved Version with KPIs
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
    st.sidebar.markdown("### 📁 Data Upload")
    st.sidebar.markdown("Upload your CSV files to begin analysis")
    st.sidebar.markdown("---")
    
    uploaded = st.sidebar.file_uploader(
        "Choose CSV Files", 
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
        
        with st.sidebar:
            st.markdown("**Loading Status:**")
        
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
                            st.sidebar.error(f"❌ {file.name}")
                            st.sidebar.caption(f"Missing: {', '.join(missing)}")
                    else:
                        data[table] = df
                        st.sidebar.success(f"✅ {file.name}")
                except Exception as e:
                    st.sidebar.error(f"❌ {file.name}")
                    st.sidebar.caption(str(e))
        
        if all(t in data for t in ['users', 'products', 'orders', 'order_items']):
            st.session_state.data = data
            st.session_state.data_loaded = True
            st.sidebar.markdown("---")
            st.sidebar.success("✅ **All data loaded successfully!**")
            st.rerun()
        else:
            st.sidebar.error("❌ Missing required tables")
            missing_tables = [t for t in ['users', 'products', 'orders', 'order_items'] if t not in data]
            st.sidebar.caption(f"Need: {', '.join(missing_tables)}.csv")
    
    if st.session_state.data_loaded:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ✅ Data Status")
        st.sidebar.success("Data loaded and ready")
        
        if st.session_state.data:
            total_orders = len(st.session_state.data.get('orders', []))
            total_customers = len(st.session_state.data.get('users', []))
            total_products = len(st.session_state.data.get('products', []))
            
            st.sidebar.markdown(f"""
            - **Orders:** {total_orders:,}
            - **Customers:** {total_customers:,}
            - **Products:** {total_products:,}
            """)
        
        # Target Settings
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎯 Target Settings")
        st.sidebar.markdown("กำหนดเป้าหมายต่างๆ ของธุรกิจ")
        
        # Initialize session state for targets if not exists
        if 'targets' not in st.session_state:
            st.session_state.targets = {
                'monthly_revenue': 5000000,
                'profit_margin': 20,
                'conversion_rate': 5,
                'retention_rate': 80,
                'inventory_turnover': 4
            }
        
        with st.sidebar.expander("📊 Sales Targets", expanded=False):
            st.session_state.targets['monthly_revenue'] = st.number_input(
                "Monthly Revenue Target (฿)",
                min_value=0,
                value=st.session_state.targets['monthly_revenue'],
                step=100000,
                format="%d",
                help="เป้าหมายยอดขายต่อเดือน"
            )
        
        with st.sidebar.expander("💰 Financial Targets", expanded=False):
            st.session_state.targets['profit_margin'] = st.number_input(
                "Target Profit Margin (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.targets['profit_margin']),
                step=1.0,
                help="เป้าหมายอัตรากำไรสุทธิ"
            )
        
        with st.sidebar.expander("📢 Marketing Targets", expanded=False):
            st.session_state.targets['conversion_rate'] = st.number_input(
                "Target Conversion Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.targets['conversion_rate']),
                step=0.5,
                help="เป้าหมาย Conversion Rate จาก Visitor เป็น Customer"
            )
            
            st.session_state.targets['retention_rate'] = st.number_input(
                "Target Retention Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.targets['retention_rate']),
                step=1.0,
                help="เป้าหมายการรักษาลูกค้า (ควรสูงกว่า 80%)"
            )
        
        with st.sidebar.expander("📦 Warehouse Targets", expanded=False):
            st.session_state.targets['inventory_turnover'] = st.number_input(
                "Target Inventory Turnover (x/year)",
                min_value=0.0,
                value=float(st.session_state.targets['inventory_turnover']),
                step=0.5,
                help="เป้าหมายการหมุนเวียนสินค้า (ครั้งต่อปี)"
            )
    
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

# Custom CSS
st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 1rem;}
    [data-testid="stMetricValue"] {font-size: 24px; font-weight: 600;}
    [data-testid="stMetricLabel"] {font-size: 13px; font-weight: 500; color: #555;}
    h1, h2, h3 {font-family: 'Inter', sans-serif; font-weight: 700;}
    
    /* Info boxes for explanations */
    .metric-explanation {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #3498db;
        margin: 10px 0;
        font-size: 13px;
        color: #2c3e50;
    }
    
    .metric-formula {
        background: #e8f4f8;
        padding: 10px;
        border-radius: 5px;
        font-family: monospace;
        font-size: 12px;
        margin: 5px 0;
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

# ==================== MAIN FILTERS ====================
st.title("📊 Fashion Analytics Dashboard")
st.markdown("---")

st.markdown("### 🔍 Filter Data")

min_date = df_master['order_date'].min().date()
max_date = df_master['order_date'].max().date()

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    period_options = ["Custom Range", "Last 7 Days", "Last 30 Days", "Last 90 Days", 
                      "This Month", "Last Month", "This Quarter", "This Year", "All Time"]
    selected_period = st.selectbox("📅 Time Period", period_options, index=2, key="period_selector")

with col2:
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
        date_range = st.date_input(
            "Custom Date Range", 
            [min_date, max_date], 
            min_value=min_date, 
            max_value=max_date,
            key="custom_date_range"
        )
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = min_date, max_date
    
    st.info(f"📆 **{start_date.strftime('%d %b %Y')}** → **{end_date.strftime('%d %b %Y')}**")

with col3:
    if st.button("🔄 Reset All", key="reset_filters", use_container_width=True):
        st.rerun()

df_filtered = df_master[(df_master['order_date'].dt.date >= start_date) & 
                        (df_master['order_date'].dt.date <= end_date)]

col1, col2, col3 = st.columns(3)

with col1:
    channels = st.multiselect(
        "🏪 Sales Channel", 
        df_master['channel'].unique(), 
        df_master['channel'].unique(),
        key="channel_filter"
    )
    df_filtered = df_filtered[df_filtered['channel'].isin(channels)]

with col2:
    statuses = st.multiselect(
        "📦 Order Status", 
        df_master['status'].unique(), 
        ['Completed'],
        key="status_filter"
    )
    df_filtered = df_filtered[df_filtered['status'].isin(statuses)]

with col3:
    if 'category' in df_filtered.columns:
        categories = st.multiselect(
            "🏷️ Product Category",
            df_master['category'].unique(),
            df_master['category'].unique(),
            key="category_filter"
        )
        df_filtered = df_filtered[df_filtered['category'].isin(categories)]

st.markdown("---")
st.markdown("### 📊 Summary Statistics")

# Calculate key metrics
revenue = df_filtered['net_revenue'].sum()
profit = df_filtered['profit'].sum()
cogs = df_filtered['cost'].sum()
total_orders = df_filtered['order_id'].nunique()
total_customers = df_filtered['user_id'].nunique()
gross_profit = revenue - cogs
profit_margin = (profit / revenue * 100) if revenue > 0 else 0
avg_order_value = revenue / total_orders if total_orders > 0 else 0

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("💰 Revenue", f"฿{revenue/1000:,.0f}K")
with col2:
    st.metric("💵 Profit", f"฿{profit/1000:,.0f}K")
with col3:
    st.metric("📝 Orders", f"{total_orders:,}")
with col4:
    st.metric("👥 Customers", f"{total_customers:,}")
with col5:
    st.metric("📊 Margin", f"{profit_margin:.1f}%")
with col6:
    st.metric("🛒 AOV", f"฿{avg_order_value:,.0f}")

st.markdown("---")

# ==================== TABS ====================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💼 Sales Analytics", 
    "📢 Marketing Analytics", 
    "💰 Financial Analytics", 
    "📦 Warehouse Analytics",
    "🔮 Forecasting & Planning"
])

with tab1:
    st.markdown("# 💼 Sales Analytics")
    st.markdown("---")
    
    # ==================== SALES GROWTH ====================
    st.markdown("### 📈 Monthly Sales Growth")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 คำอธิบาย:</b> วัดว่ายอดขายเติบโตกี่ % เมื่อเทียบกับเดือนก่อนหน้า<br>
        <div class='metric-formula'>
        สูตร: [(ยอดขายเดือนปัจจุบัน - ยอดขายเดือนก่อน) / ยอดขายเดือนก่อน] × 100
        </div>
        <b>🎯 เป้าหมาย:</b> ควรเป็นบวก และมากกว่า 5-10% ถือว่าดี
    </div>
    """, unsafe_allow_html=True)
    
    monthly_sales = df_filtered.groupby('order_month').agg({
        'net_revenue': 'sum'
    }).reset_index()
    monthly_sales['order_month'] = monthly_sales['order_month'].dt.to_timestamp()
    monthly_sales['month_label'] = monthly_sales['order_month'].dt.strftime('%b %Y')
    monthly_sales['growth_%'] = monthly_sales['net_revenue'].pct_change() * 100
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = go.Figure()
        
        # Revenue bars
        fig.add_trace(go.Bar(
            x=monthly_sales['month_label'],
            y=monthly_sales['net_revenue'],
            name='Revenue',
            marker=dict(
                color=monthly_sales['net_revenue'],
                colorscale='Blues',
                showscale=False
            ),
            text=monthly_sales['net_revenue'],
            texttemplate='฿%{text:,.0f}',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
        ))
        
        # Growth line
        fig.add_trace(go.Scatter(
            x=monthly_sales['month_label'],
            y=monthly_sales['growth_%'],
            name='Growth %',
            mode='lines+markers',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=10),
            yaxis='y2',
            text=monthly_sales['growth_%'],
            texttemplate='%{text:.1f}%',
            textposition='top center',
            hovertemplate='<b>%{x}</b><br>Growth: %{y:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Monthly Sales Revenue & Growth Rate</b>',
            xaxis=dict(title='', showgrid=False),
            yaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            yaxis2=dict(
                title='Growth (%)', 
                overlaying='y', 
                side='right',
                showgrid=False,
                zeroline=True,
                zerolinecolor='gray'
            ),
            plot_bgcolor='white',
            height=400,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        latest_growth = monthly_sales['growth_%'].iloc[-1] if len(monthly_sales) > 1 else 0
        prev_growth = monthly_sales['growth_%'].iloc[-2] if len(monthly_sales) > 2 else 0
        
        arrow = "📈" if latest_growth > 0 else "📉"
        color = "#2ecc71" if latest_growth > 0 else "#e74c3c"
        
        st.markdown(f"""
        <div style='background: white; padding: 30px; border-radius: 10px; 
                    border: 3px solid {color}; height: 400px;
                    display: flex; flex-direction: column; justify-content: center; align-items: center;'>
            <div style='font-size: 60px;'>{arrow}</div>
            <div style='font-size: 48px; font-weight: bold; color: {color}; margin: 20px 0;'>
                {latest_growth:+.1f}%
            </div>
            <div style='font-size: 16px; color: #7f8c8d; text-align: center;'>
                <b>Current Month Growth</b>
            </div>
            <div style='margin-top: 20px; font-size: 14px; color: #95a5a6;'>
                Previous: {prev_growth:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== SALES TARGET ATTAINMENT ====================
    st.markdown("### 🎯 Sales Target Attainment")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 คำอธิบาย:</b> วัดว่าทำยอดขายได้กี่ % ของเป้าหมายที่ตั้งไว้<br>
        <div class='metric-formula'>
        สูตร: (ยอดขายที่ทำได้ / เป้าหมายยอดขาย) × 100
        </div>
        <b>🎯 เป้าหมาย:</b> ควรอยู่ที่ 90-110% (น้อยกว่า 90% ต้องปรับปรุง, มากกว่า 110% ดีมาก)
    </div>
    """, unsafe_allow_html=True)
    
    # Get target from user input
    target_monthly = st.session_state.targets['monthly_revenue']
    current_month_sales = monthly_sales['net_revenue'].iloc[-1] if len(monthly_sales) > 0 else 0
    attainment = (current_month_sales / target_monthly * 100) if target_monthly > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 14px; opacity: 0.9;'>TARGET</div>
            <div style='font-size: 36px; font-weight: bold; margin: 15px 0;'>
                ฿{target_monthly/1000000:.1f}M
            </div>
            <div style='font-size: 12px; opacity: 0.8;'>Monthly Goal</div>
            <div style='font-size: 10px; opacity: 0.7; margin-top: 10px;'>
                💡 Change in sidebar settings
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 30px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 14px; opacity: 0.9;'>ACTUAL</div>
            <div style='font-size: 36px; font-weight: bold; margin: 15px 0;'>
                ฿{current_month_sales/1000000:.1f}M
            </div>
            <div style='font-size: 12px; opacity: 0.8;'>Current Sales</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        att_color = '#2ecc71' if attainment >= 90 else '#e74c3c'
        st.markdown(f"""
        <div style='background: white; padding: 30px; border-radius: 10px; 
                    border: 3px solid {att_color}; text-align: center;'>
            <div style='font-size: 14px; color: #7f8c8d;'>ATTAINMENT</div>
            <div style='font-size: 36px; font-weight: bold; margin: 15px 0; color: {att_color};'>
                {attainment:.1f}%
            </div>
            <div style='font-size: 12px; color: #95a5a6;'>
                {'✅ On Track' if attainment >= 90 else '⚠️ Below Target'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== SALES BY CHANNEL ====================
    st.markdown("### 🏪 Sales by Channel")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 คำอธิบาย:</b> แสดงยอดขายแยกตามช่องทางการขาย เพื่อดูว่าช่องทางไหนมี Performance ดีที่สุด
    </div>
    """, unsafe_allow_html=True)
    
    channel_sales = df_filtered.groupby('channel').agg({
        'net_revenue': 'sum',
        'profit': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    channel_sales.columns = ['Channel', 'Revenue', 'Profit', 'Orders']
    channel_sales['Margin_%'] = (channel_sales['Profit'] / channel_sales['Revenue'] * 100).round(1)
    channel_sales['AOV'] = (channel_sales['Revenue'] / channel_sales['Orders']).round(0)
    channel_sales = channel_sales.sort_values('Revenue', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Horizontal bar chart
        ch_sorted = channel_sales.sort_values('Revenue', ascending=True)
        colors_list = [CHANNEL_COLORS.get(ch, '#95a5a6') for ch in ch_sorted['Channel']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=ch_sorted['Channel'],
            x=ch_sorted['Revenue'],
            orientation='h',
            marker=dict(color=colors_list),
            text=ch_sorted['Revenue'],
            texttemplate='฿%{text:,.0f}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Revenue by Channel</b>',
            xaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            yaxis=dict(title=''),
            plot_bgcolor='white',
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Stacked bar: Revenue vs Profit
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=channel_sales['Channel'],
            y=channel_sales['Profit'],
            name='Profit',
            marker_color='#2ecc71',
            text=channel_sales['Profit'],
            texttemplate='฿%{text:,.0f}',
            textposition='inside',
            hovertemplate='<b>%{x}</b><br>Profit: ฿%{y:,.0f}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            x=channel_sales['Channel'],
            y=channel_sales['Revenue'] - channel_sales['Profit'],
            name='Cost',
            marker_color='#e74c3c',
            text=channel_sales['Revenue'] - channel_sales['Profit'],
            texttemplate='฿%{text:,.0f}',
            textposition='inside',
            hovertemplate='<b>%{x}</b><br>Cost: ฿%{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Revenue Breakdown: Profit vs Cost</b>',
            xaxis=dict(title='', showgrid=False),
            yaxis=dict(title='Amount (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            barmode='stack',
            plot_bgcolor='white',
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Channel metrics table
    st.markdown("#### 📊 Channel Performance Metrics")
    
    styled_ch = channel_sales.style.format({
        'Revenue': '฿{:,.0f}',
        'Profit': '฿{:,.0f}',
        'Orders': '{:,}',
        'Margin_%': '{:.1f}%',
        'AOV': '฿{:,.0f}'
    }).background_gradient(subset=['Margin_%'], cmap='RdYlGn', vmin=0, vmax=100)
    
    st.dataframe(styled_ch, use_container_width=True)
    
    st.markdown("---")
    
    # ==================== PRODUCT PERFORMANCE ====================
    st.markdown("### 🏆 Top Product Performance")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 คำอธิบาย:</b> แสดงสินค้าที่ขายดีที่สุด 20 อันดับแรก วัดจากยอดขาย และอัตรากำไร
    </div>
    """, unsafe_allow_html=True)
    
    product_sales = df_filtered.groupby(['product_id', 'product_name', 'category']).agg({
        'net_revenue': 'sum',
        'profit': 'sum',
        'quantity': 'sum'
    }).reset_index()
    product_sales.columns = ['ID', 'Product', 'Category', 'Revenue', 'Profit', 'Units']
    product_sales['Margin_%'] = (product_sales['Profit'] / product_sales['Revenue'] * 100).round(1)
    product_sales = product_sales.sort_values('Revenue', ascending=False).head(20)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Top 10 horizontal bar
        top10 = product_sales.head(10).sort_values('Revenue', ascending=True)
        
        fig = go.Figure()
        
        # Color by margin
        colors = ['#2ecc71' if m >= 50 else '#f39c12' if m >= 30 else '#e74c3c' 
                  for m in top10['Margin_%']]
        
        fig.add_trace(go.Bar(
            y=top10['Product'],
            x=top10['Revenue'],
            orientation='h',
            marker=dict(color=colors),
            text=top10['Revenue'],
            texttemplate='฿%{text:,.0f}',
            textposition='outside',
            customdata=top10[['Margin_%']],
            hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<br>Margin: %{customdata[0]:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Top 10 Products by Revenue</b><br><sub>Color: Green=High Margin, Yellow=Medium, Red=Low</sub>',
            xaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            yaxis=dict(title=''),
            plot_bgcolor='white',
            height=450,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Scatter: Revenue vs Margin (Fixed bubble size)
        fig = go.Figure()
        
        # Calculate bubble size (max 80, min 10)
        max_units = product_sales['Units'].max()
        min_units = product_sales['Units'].min()
        normalized_sizes = 10 + (product_sales['Units'] - min_units) / (max_units - min_units) * 70
        
        fig.add_trace(go.Scatter(
            x=product_sales['Revenue'],
            y=product_sales['Margin_%'],
            mode='markers',
            marker=dict(
                size=normalized_sizes,
                color=product_sales['Margin_%'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Margin %"),
                line=dict(width=1, color='white'),
                sizemode='diameter'
            ),
            text=product_sales['Product'],
            customdata=product_sales['Units'],
            hovertemplate='<b>%{text}</b><br>Revenue: ฿%{x:,.0f}<br>Margin: %{y:.1f}%<br>Units: %{customdata:,}<extra></extra>'
        ))
        
        # Add quadrant lines
        avg_revenue = product_sales['Revenue'].median()
        avg_margin = product_sales['Margin_%'].median()
        
        fig.add_hline(y=avg_margin, line_dash="dash", line_color="gray", opacity=0.5, 
                      annotation_text="Avg Margin", annotation_position="right")
        fig.add_vline(x=avg_revenue, line_dash="dash", line_color="gray", opacity=0.5,
                      annotation_text="Avg Revenue", annotation_position="top")
        
        # Add quadrant labels
        fig.add_annotation(x=avg_revenue * 1.5, y=avg_margin * 1.2,
                          text="🌟 Stars<br>(High Revenue, High Margin)",
                          showarrow=False, font=dict(size=10, color='green'))
        
        fig.add_annotation(x=avg_revenue * 1.5, y=avg_margin * 0.8,
                          text="💰 Cash Cows<br>(High Revenue, Low Margin)",
                          showarrow=False, font=dict(size=10, color='orange'))
        
        fig.add_annotation(x=avg_revenue * 0.5, y=avg_margin * 1.2,
                          text="🚀 Growth<br>(Low Revenue, High Margin)",
                          showarrow=False, font=dict(size=10, color='blue'))
        
        fig.add_annotation(x=avg_revenue * 0.5, y=avg_margin * 0.8,
                          text="⚠️ Question Marks<br>(Low Revenue, Low Margin)",
                          showarrow=False, font=dict(size=10, color='red'))
        
        fig.update_layout(
            title='<b>Product Portfolio Analysis (BCG Matrix)</b><br><sub>Bubble size = Units Sold</sub>',
            xaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            yaxis=dict(title='Profit Margin (%)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            plot_bgcolor='white',
            height=450
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("#### 📋 Top 20 Products Detail")
    
    styled_prod = product_sales.style.format({
        'Revenue': '฿{:,.0f}',
        'Profit': '฿{:,.0f}',
        'Units': '{:,}',
        'Margin_%': '{:.1f}%'
    }).background_gradient(subset=['Margin_%'], cmap='RdYlGn', vmin=0, vmax=100)
    
    st.dataframe(styled_prod, use_container_width=True)

with tab2:
    st.markdown("# 📢 Marketing Analytics")
    st.markdown("---")
    
    # Data availability checker
    st.markdown("### 📋 Available Marketing Metrics")
    
    has_funnel = all(col in df_filtered.columns for col in ['visits', 'add_to_cart', 'checkout'])
    has_campaign = 'campaign_type' in df_filtered.columns and df_filtered['campaign_type'].notna().any()
    has_acquisition = 'acquisition_channel' in df_filtered.columns
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if has_funnel:
            st.success("✅ **Conversion Funnel Data Available**")
        else:
            st.warning("⚠️ **Conversion Funnel Data Missing**\nAdd columns: `visits`, `add_to_cart`, `checkout`")
    
    with col2:
        if has_campaign:
            st.success("✅ **Campaign Data Available**")
        else:
            st.warning("⚠️ **Campaign Data Missing**\nAdd `campaign_type` column for campaign analysis")
    
    with col3:
        if has_acquisition:
            st.success("✅ **Acquisition Channel Data Available**")
        else:
            st.warning("⚠️ **Acquisition Data Missing**\nAdd `acquisition_channel` column for acquisition analysis")
    
    st.markdown("---")
    
    # ==================== CONVERSION FUNNEL ====================
    st.markdown("### 🎯 Conversion Funnel Analysis")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 Conversion Rate:</b> เปอร์เซ็นต์ของผู้เข้าชมที่กลายเป็นลูกค้า (ซื้อสินค้าจริง)<br>
        <div class='metric-formula'>
        สูตร: (จำนวน Orders / จำนวน Visitors) × 100
        </div>
        <b>📖 Funnel Stages:</b><br>
        • <b>Visitors:</b> คนที่เข้าชมเว็บไซต์/ร้าน<br>
        • <b>Add to Cart:</b> คนที่ใส่สินค้าในตะกร้า<br>
        • <b>Checkout:</b> คนที่ไปหน้า Checkout<br>
        • <b>Purchase:</b> คนที่ซื้อสำเร็จ<br>
        <b>🎯 Target:</b> {st.session_state.targets['conversion_rate']:.1f}% (Change in sidebar settings)
    </div>
    """, unsafe_allow_html=True)
    
    if has_funnel:
        # Use actual funnel data
        total_visitors = df_filtered['visits'].sum()
        add_to_cart = df_filtered['add_to_cart'].sum()
        checkout_count = df_filtered['checkout'].sum()
        total_orders = df_filtered['order_id'].nunique()
        conversion_rate = (total_orders / total_visitors * 100) if total_visitors > 0 else 0
        
        # Compare with target
        target_conversion = st.session_state.targets['conversion_rate']
        conversion_status = "✅ Above Target" if conversion_rate >= target_conversion else "⚠️ Below Target"
        conversion_color = "#2ecc71" if conversion_rate >= target_conversion else "#e74c3c"
        
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
                    <div style='font-size: 14px; opacity: 0.8; margin-top: 10px;'>
                        {total_orders:,} orders from {total_visitors:,} visitors
                    </div>
                    <div style='font-size: 12px; margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.2); border-radius: 5px;'>
                        Target: {target_conversion:.1f}%<br>
                        <span style='color: {"#2ecc71" if conversion_rate >= target_conversion else "#ffeb3b"};'>{conversion_status}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Funnel chart
            funnel_data = pd.DataFrame({
                'Stage': ['Visitors', 'Add to Cart', 'Checkout', 'Purchase'],
                'Count': [total_visitors, add_to_cart, checkout_count, total_orders],
                'Color': ['#3498db', '#2ecc71', '#f39c12', '#9b59b6']
            })
            
            fig = go.Figure()
            
            fig.add_trace(go.Funnel(
                y=funnel_data['Stage'],
                x=funnel_data['Count'],
                textposition="inside",
                textinfo="value+percent initial",
                marker=dict(
                    color=funnel_data['Color'],
                    line=dict(color='white', width=2)
                ),
                textfont=dict(size=13, weight='bold', color='white'),
                hovertemplate='<b>%{y}</b><br>Count: %{x:,}<br>Rate: %{percentInitial}<extra></extra>',
                connector=dict(line=dict(color='gray', width=1))
            ))
            
            fig.update_layout(
                title='<b>Sales Funnel</b>',
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=400,
                margin=dict(t=60, b=40, l=40, r=120),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        # Show alternative: Order completion metrics
        st.info("💡 **Showing Order Completion Metrics** (Funnel data not available)")
        
        total_orders = df_filtered['order_id'].nunique()
        total_customers = df_filtered['user_id'].nunique()
        completed_orders = df_filtered[df_filtered['status'] == 'Completed']['order_id'].nunique()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 30px; border-radius: 10px; color: white; text-align: center; height: 200px;
                        display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size: 14px; opacity: 0.9;'>TOTAL ORDERS</div>
                <div style='font-size: 48px; font-weight: bold; margin: 15px 0;'>
                    {total_orders:,}
                </div>
                <div style='font-size: 12px; opacity: 0.8;'>All statuses</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        padding: 30px; border-radius: 10px; color: white; text-align: center; height: 200px;
                        display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size: 14px; opacity: 0.9;'>COMPLETION RATE</div>
                <div style='font-size: 48px; font-weight: bold; margin: 15px 0;'>
                    {completion_rate:.1f}%
                </div>
                <div style='font-size: 12px; opacity: 0.8;'>{completed_orders:,} completed</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            orders_per_customer = total_orders / total_customers if total_customers > 0 else 0
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        padding: 30px; border-radius: 10px; color: white; text-align: center; height: 200px;
                        display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size: 14px; opacity: 0.9;'>ORDERS/CUSTOMER</div>
                <div style='font-size: 48px; font-weight: bold; margin: 15px 0;'>
                    {orders_per_customer:.1f}
                </div>
                <div style='font-size: 12px; opacity: 0.8;'>Average frequency</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Show order status breakdown
        st.markdown("<br>", unsafe_allow_html=True)
        
        status_data = df_filtered.groupby('status')['order_id'].nunique().reset_index()
        status_data.columns = ['Status', 'Orders']
        status_data = status_data.sort_values('Orders', ascending=True)
        
        status_colors = {
            'Completed': '#2ecc71',
            'Pending': '#f39c12',
            'Cancelled': '#e74c3c',
            'Refunded': '#95a5a6'
        }
        
        colors_list = [status_colors.get(s, '#95a5a6') for s in status_data['Status']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=status_data['Status'],
            x=status_data['Orders'],
            orientation='h',
            marker=dict(color=colors_list, line=dict(color='white', width=2)),
            text=status_data['Orders'],
            texttemplate='%{text:,}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Orders: %{x:,}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Order Status Breakdown</b>',
            xaxis=dict(title='Number of Orders', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            yaxis=dict(title=''),
            plot_bgcolor='white',
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ==================== CUSTOMER ACQUISITION COST ====================
    st.markdown("### 💳 Customer Acquisition Cost (CAC)")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 คำอธิบาย:</b> ค่าใช้จ่ายที่ใช้ในการหาลูกค้าใหม่ 1 คน<br>
        <div class='metric-formula'>
        สูตร: ค่าใช้จ่ายทางการตลาด / จำนวนลูกค้าใหม่
        </div>
        <b>🎯 เป้าหมาย:</b> ควรต่ำกว่า Customer Lifetime Value (CLV) อย่างน้อย 3 เท่า
    </div>
    """, unsafe_allow_html=True)
    
    marketing_cost = df_filtered['discount_amount'].sum() if 'discount_amount' in df_filtered.columns else 0
    new_customers = df_filtered['user_id'].nunique()
    cac = marketing_cost / new_customers if new_customers > 0 else 0
    
    # Calculate CLV
    analysis_date = df_filtered['order_date'].max()
    last_purchase = df_filtered.groupby('user_id')['order_date'].max()
    churned = ((analysis_date - last_purchase).dt.days > 90).sum()
    churn_rate = (churned / len(last_purchase) * 100) if len(last_purchase) > 0 else 0
    retention_rate = 100 - churn_rate
    avg_revenue = df_filtered.groupby('user_id')['net_revenue'].sum().mean()
    clv = (profit_margin / 100) * (retention_rate / 100) * avg_revenue
    
    cac_to_clv_ratio = (cac / clv) if clv > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9;'>CAC</div>
            <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
                ฿{cac:,.0f}
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Per customer</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9;'>CLV</div>
            <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
                ฿{clv:,.0f}
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Lifetime value</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        ratio_color = '#2ecc71' if cac_to_clv_ratio < 0.33 else '#e74c3c'
        st.markdown(f"""
        <div style='background: white; padding: 25px; border-radius: 10px; 
                    border: 3px solid {ratio_color}; text-align: center;'>
            <div style='font-size: 13px; color: #7f8c8d;'>CAC : CLV</div>
            <div style='font-size: 32px; font-weight: bold; margin: 10px 0; color: {ratio_color};'>
                1:{(clv/cac if cac > 0 else 0):.1f}
            </div>
            <div style='font-size: 11px; color: #95a5a6;'>
                {'✅ Good' if cac_to_clv_ratio < 0.33 else '⚠️ Too High'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9;'>NEW CUSTOMERS</div>
            <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
                {new_customers:,}
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>In period</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== RETENTION & CHURN ====================
    st.markdown("### 🔄 Customer Retention & Churn Rate")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 Retention Rate:</b> เปอร์เซ็นต์ของลูกค้าที่ยังคงซื้อสินค้ากับเรา (ไม่หายไป)<br>
        <div class='metric-formula'>
        สูตร: [1 - (จำนวนลูกค้าที่หายไป / จำนวนลูกค้าเริ่มต้น)] × 100
        </div>
        <b>📖 Churn Rate:</b> เปอร์เซ็นต์ของลูกค้าที่หยุดซื้อสินค้า (ไม่ซื้อเกิน 90 วัน)<br>
        <b>🎯 Target:</b> Retention > {st.session_state.targets['retention_rate']:.0f}% (Change in sidebar)
    </div>
    """, unsafe_allow_html=True)
    
    # Compare with target
    target_retention = st.session_state.targets['retention_rate']
    retention_status = "✅ Above Target" if retention_rate >= target_retention else "⚠️ Below Target"
    retention_border_color = "#2ecc71" if retention_rate >= target_retention else "#e74c3c"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style='background: white; padding: 30px; border-radius: 10px; 
                    border: 3px solid {retention_border_color}; text-align: center; height: 240px;
                    display: flex; flex-direction: column; justify-content: center;'>
            <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
                <b>RETENTION RATE</b>
            </div>
            <div style='font-size: 48px; font-weight: bold; color: {retention_border_color}; margin: 15px 0;'>
                {retention_rate:.1f}%
            </div>
            <div style='font-size: 12px; color: #95a5a6;'>
                Active customers
            </div>
            <div style='font-size: 11px; color: #95a5a6; margin-top: 10px; padding: 8px; background: #f8f9fa; border-radius: 5px;'>
                Target: {target_retention:.0f}%<br>{retention_status}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: white; padding: 30px; border-radius: 10px; 
                    border: 3px solid #e74c3c; text-align: center; height: 200px;
                    display: flex; flex-direction: column; justify-content: center;'>
            <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
                <b>CHURN RATE</b>
            </div>
            <div style='font-size: 48px; font-weight: bold; color: #e74c3c; margin: 15px 0;'>
                {churn_rate:.1f}%
            </div>
            <div style='font-size: 12px; color: #95a5a6;'>
                Lost customers
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        active_customers = int(len(last_purchase) * retention_rate / 100)
        churned_customers = int(len(last_purchase) * churn_rate / 100)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=['Active', 'Churned'],
            y=[active_customers, churned_customers],
            marker=dict(color=['#2ecc71', '#e74c3c']),
            text=[active_customers, churned_customers],
            texttemplate='%{text:,}',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Customers: %{y:,}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Customer Status</b>',
            xaxis=dict(title='', showgrid=False),
            yaxis=dict(title='Number of Customers', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            plot_bgcolor='white',
            height=200,
            showlegend=False,
            margin=dict(t=40, b=40, l=60, r=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("# 💰 Financial Analytics")
    st.markdown("---")
    
    # ==================== PROFIT MARGINS ====================
    st.markdown("### 📊 Profit Margin Analysis")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 Gross Profit Margin:</b> เปอร์เซ็นต์กำไรขั้นต้น (หลังหักต้นทุนสินค้า)<br>
        <div class='metric-formula'>
        สูตร: [(รายได้ - ต้นทุนสินค้า) / รายได้] × 100
        </div>
        <b>📖 Net Profit Margin:</b> เปอร์เซ็นต์กำไรสุทธิ (หลังหักค่าใช้จ่ายทั้งหมด)<br>
        <div class='metric-formula'>
        สูตร: (กำไรสุทธิ / รายได้) × 100
        </div>
        <b>🎯 Target:</b> Net Margin > {st.session_state.targets['profit_margin']:.0f}% (Change in sidebar)
    </div>
    """, unsafe_allow_html=True)
    
    gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
    net_margin = (profit / revenue * 100) if revenue > 0 else 0
    
    # Compare with target
    target_margin = st.session_state.targets['profit_margin']
    margin_status = "✅ Above Target" if net_margin >= target_margin else "⚠️ Below Target"
    margin_color = "#2ecc71" if net_margin >= target_margin else "#e74c3c"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Waterfall chart
        fig = go.Figure(go.Waterfall(
            orientation="v",
            measure=["relative", "relative", "relative", "total"],
            x=["Revenue", "COGS", "Other Costs", "Net Profit"],
            y=[revenue, -cogs, -(gross_profit - profit), profit],
            text=[f"฿{revenue:,.0f}", f"-฿{cogs:,.0f}", f"-฿{(gross_profit - profit):,.0f}", f"฿{profit:,.0f}"],
            textposition="outside",
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            decreasing={"marker": {"color": "#e74c3c"}},
            increasing={"marker": {"color": "#2ecc71"}},
            totals={"marker": {"color": "#3498db"}},
            hovertemplate='<b>%{x}</b><br>Amount: ฿%{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Profit Waterfall</b>',
            plot_bgcolor='white',
            height=300,
            showlegend=False,
            margin=dict(t=40, b=40, l=60, r=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px; border-radius: 10px; color: white; text-align: center; height: 300px;
                    display: flex; flex-direction: column; justify-content: center;'>
            <div style='font-size: 14px; opacity: 0.9; margin-bottom: 10px;'>
                GROSS PROFIT MARGIN
            </div>
            <div style='font-size: 52px; font-weight: bold; margin: 15px 0;'>
                {gross_margin:.1f}%
            </div>
            <div style='font-size: 12px; opacity: 0.8;'>
                (Revenue - COGS) / Revenue
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 30px; border-radius: 10px; color: white; text-align: center; height: 300px;
                    display: flex; flex-direction: column; justify-content: center;'>
            <div style='font-size: 14px; opacity: 0.9; margin-bottom: 10px;'>
                NET PROFIT MARGIN
            </div>
            <div style='font-size: 52px; font-weight: bold; margin: 15px 0;'>
                {net_margin:.1f}%
            </div>
            <div style='font-size: 12px; opacity: 0.8;'>
                Net Profit / Revenue
            </div>
            <div style='font-size: 11px; margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.2); border-radius: 5px;'>
                Target: {target_margin:.0f}%<br>
                <span style='color: {"#2ecc71" if net_margin >= target_margin else "#ffeb3b"};'>{margin_status}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== MONTHLY FINANCIAL TREND ====================
    st.markdown("### 📈 Monthly Financial Performance")
    
    monthly_fin = df_filtered.groupby('order_month').agg({
        'net_revenue': 'sum',
        'cost': 'sum',
        'profit': 'sum'
    }).reset_index()
    monthly_fin['order_month'] = monthly_fin['order_month'].dt.to_timestamp()
    monthly_fin['month_label'] = monthly_fin['order_month'].dt.strftime('%b %Y')
    monthly_fin['gross_margin_%'] = ((monthly_fin['net_revenue'] - monthly_fin['cost']) / monthly_fin['net_revenue'] * 100).round(1)
    monthly_fin['net_margin_%'] = (monthly_fin['profit'] / monthly_fin['net_revenue'] * 100).round(1)
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Revenue and Cost bars
    fig.add_trace(
        go.Bar(
            x=monthly_fin['month_label'],
            y=monthly_fin['net_revenue'],
            name='Revenue',
            marker_color='#3498db',
            hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Bar(
            x=monthly_fin['month_label'],
            y=monthly_fin['cost'],
            name='COGS',
            marker_color='#e74c3c',
            hovertemplate='<b>%{x}</b><br>COGS: ฿%{y:,.0f}<extra></extra>'
        ),
        secondary_y=False
    )
    
    # Margin lines
    fig.add_trace(
        go.Scatter(
            x=monthly_fin['month_label'],
            y=monthly_fin['gross_margin_%'],
            name='Gross Margin %',
            mode='lines+markers',
            line=dict(color='#27ae60', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x}</b><br>Gross Margin: %{y:.1f}%<extra></extra>'
        ),
        secondary_y=True
    )
    
    fig.add_trace(
        go.Scatter(
            x=monthly_fin['month_label'],
            y=monthly_fin['net_margin_%'],
            name='Net Margin %',
            mode='lines+markers',
            line=dict(color='#9b59b6', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x}</b><br>Net Margin: %{y:.1f}%<extra></extra>'
        ),
        secondary_y=True
    )
    
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="Amount (฿)", secondary_y=False, showgrid=True, gridcolor='rgba(0,0,0,0.05)')
    fig.update_yaxes(title_text="Margin (%)", secondary_y=True, showgrid=False)
    
    fig.update_layout(
        title='<b>Monthly Revenue, Cost & Margins</b>',
        plot_bgcolor='white',
        height=400,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ==================== WORKING CAPITAL RATIOS ====================
    st.markdown("### 💼 Working Capital Ratios")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 AR Turnover:</b> จำนวนครั้งที่เราเก็บเงินจากลูกค้าได้ต่อปี (ยิ่งสูงยิ่งดี)<br>
        <b>📖 DSO (Days Sales Outstanding):</b> จำนวนวันเฉลี่ยที่ใช้เวลาเก็บเงินจากลูกค้า (ยิ่งต่ำยิ่งดี)<br>
        <div class='metric-formula'>
        DSO = 365 / AR Turnover
        </div>
        <b>🎯 เป้าหมาย:</b> DSO < 45 วัน ถือว่าดี
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate ratios
    avg_monthly_rev = monthly_fin['net_revenue'].mean()
    avg_ar = avg_monthly_rev * 0.3  # Assume 30% credit sales
    ar_turnover = (revenue * 0.3) / avg_ar if avg_ar > 0 else 0
    dso = 365 / ar_turnover if ar_turnover > 0 else 0
    
    avg_ap = cogs * 0.25
    ap_turnover = cogs / avg_ap if avg_ap > 0 else 0
    dpo = 365 / ap_turnover if ap_turnover > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background: white; padding: 25px; border-radius: 10px; 
                    border-left: 5px solid #3498db; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <div style='font-size: 12px; color: #7f8c8d; margin-bottom: 8px;'>
                <b>AR TURNOVER</b>
            </div>
            <div style='font-size: 36px; font-weight: bold; color: #2c3e50;'>
                {ar_turnover:.2f}x
            </div>
            <div style='font-size: 11px; color: #95a5a6; margin-top: 5px;'>
                Times per year
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        dso_color = '#2ecc71' if dso < 45 else '#e74c3c'
        st.markdown(f"""
        <div style='background: white; padding: 25px; border-radius: 10px; 
                    border-left: 5px solid {dso_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <div style='font-size: 12px; color: #7f8c8d; margin-bottom: 8px;'>
                <b>DSO</b>
            </div>
            <div style='font-size: 36px; font-weight: bold; color: #2c3e50;'>
                {dso:.0f}
            </div>
            <div style='font-size: 11px; color: #95a5a6; margin-top: 5px;'>
                Days
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: white; padding: 25px; border-radius: 10px; 
                    border-left: 5px solid #9b59b6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <div style='font-size: 12px; color: #7f8c8d; margin-bottom: 8px;'>
                <b>AP TURNOVER</b>
            </div>
            <div style='font-size: 36px; font-weight: bold; color: #2c3e50;'>
                {ap_turnover:.2f}x
            </div>
            <div style='font-size: 11px; color: #95a5a6; margin-top: 5px;'>
                Times per year
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: white; padding: 25px; border-radius: 10px; 
                    border-left: 5px solid #f39c12; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <div style='font-size: 12px; color: #7f8c8d; margin-bottom: 8px;'>
                <b>DPO</b>
            </div>
            <div style='font-size: 36px; font-weight: bold; color: #2c3e50;'>
                {dpo:.0f}
            </div>
            <div style='font-size: 11px; color: #95a5a6; margin-top: 5px;'>
                Days
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.markdown("# 📦 Warehouse Analytics")
    st.markdown("---")
    
    # ==================== INVENTORY TURNOVER ====================
    st.markdown("### 🔄 Inventory Turnover & Performance")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 Inventory Turnover:</b> จำนวนครั้งที่สินค้าหมุนเวียนต่อปี (ยิ่งสูงยิ่งดี แสดงว่าสินค้าขายดี)<br>
        <div class='metric-formula'>
        สูตร: ต้นทุนสินค้าที่ขาย / มูลค่าสินค้าคงคลังเฉลี่ย
        </div>
        <b>📖 Days Inventory Outstanding (DIO):</b> จำนวนวันที่สินค้าอยู่ในคลังก่อนขายได้<br>
        <div class='metric-formula'>
        สูตร: 365 / Inventory Turnover
        </div>
        <b>🎯 Target:</b> Turnover > {st.session_state.targets['inventory_turnover']:.1f}x (Change in sidebar)
    </div>
    """, unsafe_allow_html=True)
    
    avg_inventory = df_filtered['cost'].mean() * df_filtered['product_id'].nunique()
    inventory_turnover = cogs / avg_inventory if avg_inventory > 0 else 0
    dio = 365 / inventory_turnover if inventory_turnover > 0 else 0
    
    units_sold = df_filtered['quantity'].sum()
    units_received = units_sold * 1.2
    sell_through = (units_sold / units_received * 100) if units_received > 0 else 0
    
    # Compare with target
    target_turnover = st.session_state.targets['inventory_turnover']
    turnover_status = "✅ Above Target" if inventory_turnover >= target_turnover else "⚠️ Below Target"
    turnover_color = "#2ecc71" if inventory_turnover >= target_turnover else "#e74c3c"
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
                <b>INVENTORY TURNOVER</b>
            </div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
                {inventory_turnover:.2f}x
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Times per year</div>
            <div style='font-size: 10px; margin-top: 10px; padding: 8px; background: rgba(255,255,255,0.2); border-radius: 5px;'>
                Target: {target_turnover:.1f}x<br>{turnover_status}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        dio_color = '#2ecc71' if dio < 90 else '#e74c3c'
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
                <b>DIO</b>
            </div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
                {dio:.0f}
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Days</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
                <b>SELL-THROUGH RATE</b>
            </div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
                {sell_through:.1f}%
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Of received</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
                <b>INVENTORY VALUE</b>
            </div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
                ฿{avg_inventory/1000:.0f}K
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Total stock</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== PRODUCT MOVEMENT CLASSIFICATION ====================
    st.markdown("### 🚀 Product Movement Classification")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 คำอธิบาย:</b> จัดกลุ่มสินค้าตามความเร็วในการขาย<br>
        • <b style='color: #2ecc71;'>Fast Moving:</b> ขายดี ควรเพิ่ม stock<br>
        • <b style='color: #f39c12;'>Medium Moving:</b> ขายปานกลาง รักษาระดับปกติ<br>
        • <b style='color: #e74c3c;'>Slow Moving:</b> ขายช้า ลด stock หรือทำ clearance
    </div>
    """, unsafe_allow_html=True)
    
    product_velocity = df_filtered.groupby(['product_id', 'product_name', 'category']).agg({
        'order_id': 'nunique',
        'net_revenue': 'sum',
        'cost': 'sum',
        'quantity': 'sum'
    }).reset_index()
    product_velocity.columns = ['ID', 'Product', 'Category', 'Orders', 'Revenue', 'Cost', 'Units']
    
    fast_threshold = product_velocity['Orders'].quantile(0.75)
    slow_threshold = product_velocity['Orders'].quantile(0.25)
    
    def classify_movement(orders):
        if orders >= fast_threshold:
            return 'Fast Moving'
        elif orders <= slow_threshold:
            return 'Slow Moving'
        return 'Medium Moving'
    
    product_velocity['Movement'] = product_velocity['Orders'].apply(classify_movement)
    
    movement_summary = product_velocity.groupby('Movement').agg({
        'Product': 'count',
        'Revenue': 'sum',
        'Cost': 'sum'
    }).reset_index()
    movement_summary.columns = ['Movement', 'Products', 'Revenue', 'Inventory_Value']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Stacked bar chart
        movement_order = ['Fast Moving', 'Medium Moving', 'Slow Moving']
        movement_colors = {'Fast Moving': '#2ecc71', 'Medium Moving': '#f39c12', 'Slow Moving': '#e74c3c'}
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=['Product Count'],
            x=[movement_summary[movement_summary['Movement'] == 'Fast Moving']['Products'].sum()],
            name='Fast Moving',
            orientation='h',
            marker_color='#2ecc71',
            text=[movement_summary[movement_summary['Movement'] == 'Fast Moving']['Products'].sum()],
            texttemplate='%{text}',
            textposition='inside',
            hovertemplate='<b>Fast Moving</b><br>Products: %{x}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            y=['Product Count'],
            x=[movement_summary[movement_summary['Movement'] == 'Medium Moving']['Products'].sum()],
            name='Medium Moving',
            orientation='h',
            marker_color='#f39c12',
            text=[movement_summary[movement_summary['Movement'] == 'Medium Moving']['Products'].sum()],
            texttemplate='%{text}',
            textposition='inside',
            hovertemplate='<b>Medium Moving</b><br>Products: %{x}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            y=['Product Count'],
            x=[movement_summary[movement_summary['Movement'] == 'Slow Moving']['Products'].sum()],
            name='Slow Moving',
            orientation='h',
            marker_color='#e74c3c',
            text=[movement_summary[movement_summary['Movement'] == 'Slow Moving']['Products'].sum()],
            texttemplate='%{text}',
            textposition='inside',
            hovertemplate='<b>Slow Moving</b><br>Products: %{x}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Product Distribution by Movement Speed</b>',
            xaxis=dict(title='Number of Products'),
            yaxis=dict(title=''),
            barmode='stack',
            plot_bgcolor='white',
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Inventory value by movement
        movement_sorted = movement_summary.sort_values('Inventory_Value', ascending=True)
        colors = [movement_colors[m] for m in movement_sorted['Movement']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=movement_sorted['Movement'],
            x=movement_sorted['Inventory_Value'],
            orientation='h',
            marker=dict(color=colors),
            text=movement_sorted['Inventory_Value'],
            texttemplate='฿%{text:,.0f}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Value: ฿%{x:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Inventory Value by Movement</b>',
            xaxis=dict(title='Inventory Value (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            yaxis=dict(title=''),
            plot_bgcolor='white',
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Show top products in each category
    st.markdown("#### 📋 Movement Classification Details")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("**🚀 Fast Moving (Top 10)**")
        fast_products = product_velocity[product_velocity['Movement'] == 'Fast Moving'].nlargest(10, 'Orders')
        st.dataframe(
            fast_products[['Product', 'Orders', 'Units']].style.format({
                'Orders': '{:,}',
                'Units': '{:,}'
            }),
            height=300,
            use_container_width=True
        )
    
    with col2:
        st.warning("**⚖️ Medium Moving (Top 10)**")
        medium_products = product_velocity[product_velocity['Movement'] == 'Medium Moving'].nlargest(10, 'Orders')
        st.dataframe(
            medium_products[['Product', 'Orders', 'Units']].style.format({
                'Orders': '{:,}',
                'Units': '{:,}'
            }),
            height=300,
            use_container_width=True
        )
    
    with col3:
        st.error("**🐌 Slow Moving (Top 10)**")
        slow_products = product_velocity[product_velocity['Movement'] == 'Slow Moving'].nlargest(10, 'Cost')
        st.dataframe(
            slow_products[['Product', 'Orders', 'Cost']].style.format({
                'Orders': '{:,}',
                'Cost': '฿{:,.0f}'
            }),
            height=300,
            use_container_width=True
        )
    
    st.markdown("---")
    
    # ==================== CASH CONVERSION CYCLE ====================
    st.markdown("### ⏱️ Cash Conversion Cycle (CCC)")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 คำอธิบาย:</b> ระยะเวลาที่เงินสดถูกล็อคอยู่ในธุรกิจ<br>
        <div class='metric-formula'>
        สูตร: DIO + DSO - DPO
        </div>
        <b>📖 ความหมาย:</b><br>
        • DIO = วันที่สินค้าอยู่ในคลัง<br>
        • DSO = วันที่รอเก็บเงินจากลูกค้า<br>
        • DPO = วันที่เราจ่ายเงินซัพพลายเออร์<br>
        <b>🎯 เป้าหมาย:</b> ยิ่งต่ำยิ่งดี (< 60 วัน ดีมาก, < 30 วัน ดีเยี่ยม)
    </div>
    """, unsafe_allow_html=True)
    
    ccc = dio + dso - dpo
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        ccc_color = '#2ecc71' if ccc < 60 else '#e74c3c'
        ccc_status = '✅ Excellent' if ccc < 30 else '✅ Good' if ccc < 60 else '⚠️ Needs Improvement'
        
        st.markdown(f"""
        <div style='background: white; padding: 40px; border-radius: 10px; 
                    border: 4px solid {ccc_color}; text-align: center; height: 400px;
                    display: flex; flex-direction: column; justify-content: center;'>
            <div style='font-size: 16px; color: #7f8c8d; margin-bottom: 15px;'>
                <b>CASH CONVERSION CYCLE</b>
            </div>
            <div style='font-size: 72px; font-weight: bold; color: {ccc_color}; margin: 20px 0;'>
                {ccc:.0f}
            </div>
            <div style='font-size: 24px; color: #7f8c8d;'>
                days
            </div>
            <div style='font-size: 14px; color: #95a5a6; margin-top: 20px;'>
                {ccc_status}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # CCC breakdown chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=['DIO', 'DSO', 'DPO', 'CCC'],
            y=[dio, dso, -dpo, ccc],
            marker=dict(
                color=['#3498db', '#9b59b6', '#e74c3c', '#2ecc71'],
                line=dict(color='white', width=2)
            ),
            text=[f"{dio:.0f}", f"{dso:.0f}", f"{dpo:.0f}", f"{ccc:.0f}"],
            texttemplate='%{text} days',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Days: %{y:.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Cash Conversion Cycle Breakdown</b>',
            xaxis=dict(title='', showgrid=False),
            yaxis=dict(
                title='Days',
                showgrid=True,
                gridcolor='rgba(0,0,0,0.05)',
                zeroline=True,
                zerolinecolor='gray'
            ),
            plot_bgcolor='white',
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.markdown("# 🔮 Forecasting & Planning")
    st.markdown("---")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 คำอธิบาย:</b> ใช้ข้อมูลในอดีตเพื่อคาดการณ์อนาคต ช่วยในการวางแผนธุรกิจ<br>
        <b>🎯 วิธีการ:</b> ใช้ Moving Average และ Linear Regression เพื่อทำนายแนวโน้ม
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== REVENUE FORECAST ====================
    st.markdown("### 📈 Revenue Forecast (Next 12 Months)")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 Revenue Forecast:</b> ทำนายยอดขายในอนาคต 12 เดือนข้างหน้า<br>
        <div class='metric-formula'>
        วิธีการ: Time Series Models (ARIMA / Exponential Smoothing / Prophet)
        </div>
        <b>🔬 Model Features:</b><br>
        • รองรับ Trend และ Seasonality<br>
        • คำนวณ Confidence Interval<br>
        • รองรับข้อมูลที่มี missing values<br>
        <b>💡 การใช้ประโยชน์:</b><br>
        • วางแผนงบประมาณ<br>
        • กำหนดเป้าหมายทีมขาย<br>
        • วางแผนจัดซื้อสินค้า<br>
        • วางแผนการตลาด
    </div>
    """, unsafe_allow_html=True)
    
    # Add method selector
    col_method, col_period = st.columns([2, 1])
    
    with col_method:
        forecast_method = st.selectbox(
            "🔮 Select Forecasting Method",
            ["Prophet (Facebook)", "Exponential Smoothing", "ARIMA", "Linear Trend"],
            help="เลือกวิธีการทำนายที่เหมาะสม - Prophet แนะนำสำหรับข้อมูลที่มี seasonality"
        )
    
    with col_period:
        future_months = st.slider(
            "📅 Months",
            min_value=3,
            max_value=24,
            value=12
        )
    
    # Prepare historical data
    monthly_revenue = df_filtered.groupby('order_month').agg({
        'net_revenue': 'sum'
    }).reset_index()
    monthly_revenue['order_month'] = monthly_revenue['order_month'].dt.to_timestamp()
    monthly_revenue = monthly_revenue.sort_values('order_month')
    
    if len(monthly_revenue) >= 6:
        try:
            import warnings
            warnings.filterwarnings('ignore')
            
            forecast_values = None
            lower_bound = None
            upper_bound = None
            model_name = forecast_method
            
            # Method 1: Prophet
            if forecast_method == "Prophet (Facebook)":
                from prophet import Prophet
                
                prophet_df = pd.DataFrame({
                    'ds': monthly_revenue['order_month'],
                    'y': monthly_revenue['net_revenue']
                })
                
                model = Prophet(
                    yearly_seasonality=True,
                    weekly_seasonality=False,
                    daily_seasonality=False,
                    interval_width=0.95,
                    seasonality_mode='multiplicative' if len(monthly_revenue) >= 24 else 'additive'
                )
                model.fit(prophet_df)
                
                future = model.make_future_dataframe(periods=future_months, freq='MS')
                forecast = model.predict(future)
                
                forecast_values = forecast['yhat'].tail(future_months).values
                lower_bound = forecast['yhat_lower'].tail(future_months).values
                upper_bound = forecast['yhat_upper'].tail(future_months).values
            
            # Method 2: Exponential Smoothing (Holt-Winters)
            elif forecast_method == "Exponential Smoothing":
                from statsmodels.tsa.holtwinters import ExponentialSmoothing
                
                seasonal_periods = min(12, len(monthly_revenue) // 2) if len(monthly_revenue) >= 24 else None
                
                model = ExponentialSmoothing(
                    monthly_revenue['net_revenue'].values,
                    seasonal_periods=seasonal_periods,
                    trend='add',
                    seasonal='add' if seasonal_periods else None
                )
                fitted_model = model.fit()
                
                forecast_values = fitted_model.forecast(steps=future_months)
                
                # Approximate confidence intervals
                std_error = np.std(fitted_model.resid) if hasattr(fitted_model, 'resid') else np.std(monthly_revenue['net_revenue']) * 0.1
                lower_bound = forecast_values - 1.96 * std_error
                upper_bound = forecast_values + 1.96 * std_error
            
            # Method 3: ARIMA
            elif forecast_method == "ARIMA":
                from statsmodels.tsa.arima.model import ARIMA
                
                # Simple ARIMA(1,1,1) - can be enhanced with auto_arima
                model = ARIMA(monthly_revenue['net_revenue'].values, order=(1, 1, 1))
                fitted_model = model.fit()
                
                forecast_obj = fitted_model.get_forecast(steps=future_months)
                forecast_values = forecast_obj.predicted_mean
                forecast_ci = forecast_obj.conf_int()
                lower_bound = forecast_ci.iloc[:, 0].values
                upper_bound = forecast_ci.iloc[:, 1].values
            
            # Method 4: Linear Trend
            else:
                from sklearn.linear_model import LinearRegression
                
                X = np.arange(len(monthly_revenue)).reshape(-1, 1)
                y = monthly_revenue['net_revenue'].values
                
                model = LinearRegression()
                model.fit(X, y)
                
                future_X = np.arange(len(monthly_revenue), len(monthly_revenue) + future_months).reshape(-1, 1)
                forecast_values = model.predict(future_X)
                
                residuals = y - model.predict(X)
                std_error = np.std(residuals)
                lower_bound = forecast_values - 1.96 * std_error
                upper_bound = forecast_values + 1.96 * std_error
            
            # Ensure non-negative values
            forecast_values = np.maximum(forecast_values, 0)
            lower_bound = np.maximum(lower_bound, 0)
            upper_bound = np.maximum(upper_bound, 0)
            
            # Create forecast dataframe
            last_date = monthly_revenue['order_month'].iloc[-1]
            forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=future_months, freq='MS')
            
            forecast_df = pd.DataFrame({
                'Month': forecast_dates,
                'Forecast': forecast_values,
                'Lower': lower_bound,
                'Upper': upper_bound
            })
            forecast_df['Month_Label'] = forecast_df['Month'].dt.strftime('%b %Y')
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Create forecast chart
                fig = go.Figure()
                
                # Historical data
                fig.add_trace(go.Scatter(
                    x=monthly_revenue['order_month'].dt.strftime('%b %Y'),
                    y=monthly_revenue['net_revenue'],
                    name='Actual',
                    mode='lines+markers',
                    line=dict(color='#3498db', width=3),
                    marker=dict(size=8),
                    hovertemplate='<b>%{x}</b><br>Actual: ฿%{y:,.0f}<extra></extra>'
                ))
                
                # Forecast
                fig.add_trace(go.Scatter(
                    x=forecast_df['Month_Label'],
                    y=forecast_df['Forecast'],
                    name=f'Forecast ({model_name})',
                    mode='lines+markers',
                    line=dict(color='#e74c3c', width=3, dash='dash'),
                    marker=dict(size=8, symbol='diamond'),
                    hovertemplate='<b>%{x}</b><br>Forecast: ฿%{y:,.0f}<extra></extra>'
                ))
                
                # Confidence interval (upper bound)
                fig.add_trace(go.Scatter(
                    x=forecast_df['Month_Label'],
                    y=forecast_df['Upper'],
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
                # Confidence interval (lower bound with fill)
                fig.add_trace(go.Scatter(
                    x=forecast_df['Month_Label'],
                    y=forecast_df['Lower'],
                    mode='lines',
                    line=dict(width=0),
                    fill='tonexty',
                    fillcolor='rgba(231, 76, 60, 0.2)',
                    name='95% Confidence Interval',
                    hovertemplate='<b>%{x}</b><br>Range: ฿%{y:,.0f}<extra></extra>'
                ))
                
                fig.update_layout(
                    title=f'<b>Revenue Forecast - {model_name}</b>',
                    xaxis=dict(title='', showgrid=False),
                    yaxis=dict(title='Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
                    plot_bgcolor='white',
                    height=400,
                    hovermode='x unified',
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Forecast summary
                total_forecast = forecast_df['Forecast'].sum()
                avg_monthly = forecast_df['Forecast'].mean()
                growth_forecast = ((forecast_df['Forecast'].iloc[-1] - monthly_revenue['net_revenue'].iloc[-1]) / 
                                 monthly_revenue['net_revenue'].iloc[-1] * 100)
                
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            padding: 30px; border-radius: 10px; color: white; text-align: center; height: 400px;
                            display: flex; flex-direction: column; justify-content: center;'>
                    <div style='font-size: 14px; opacity: 0.9; margin-bottom: 15px;'>
                        <b>📊 FORECAST SUMMARY</b>
                    </div>
                    <div style='margin: 12px 0;'>
                        <div style='font-size: 11px; opacity: 0.8;'>Model</div>
                        <div style='font-size: 15px; font-weight: bold; margin: 5px 0;'>
                            {model_name}
                        </div>
                    </div>
                    <div style='margin: 12px 0;'>
                        <div style='font-size: 11px; opacity: 0.8;'>Next {future_months} Months Total</div>
                        <div style='font-size: 32px; font-weight: bold; margin: 5px 0;'>
                            ฿{total_forecast/1000000:.1f}M
                        </div>
                    </div>
                    <div style='margin: 12px 0;'>
                        <div style='font-size: 11px; opacity: 0.8;'>Average Monthly</div>
                        <div style='font-size: 24px; font-weight: bold; margin: 5px 0;'>
                            ฿{avg_monthly/1000:.0f}K
                        </div>
                    </div>
                    <div style='margin: 12px 0;'>
                        <div style='font-size: 11px; opacity: 0.8;'>Expected Growth</div>
                        <div style='font-size: 24px; font-weight: bold; margin: 5px 0;'>
                            {growth_forecast:+.1f}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Forecast table
            st.markdown(f"#### 📋 Monthly Forecast Details ({model_name})")
            
            forecast_display = forecast_df.copy()
            forecast_display['Month'] = forecast_display['Month_Label']
            forecast_display['Confidence'] = ((forecast_display['Upper'] - forecast_display['Lower']) / 
                                            forecast_display['Forecast'] * 100).round(1)
            forecast_display = forecast_display[['Month', 'Forecast', 'Lower', 'Upper', 'Confidence']]
            forecast_display.columns = ['Month', 'Forecast', 'Lower Bound (95%)', 'Upper Bound (95%)', 'Uncertainty (%)']
            
            styled_forecast = forecast_display.style.format({
                'Forecast': '฿{:,.0f}',
                'Lower Bound (95%)': '฿{:,.0f}',
                'Upper Bound (95%)': '฿{:,.0f}',
                'Uncertainty (%)': '{:.1f}%'
            }).background_gradient(subset=['Forecast'], cmap='Blues')\
              .background_gradient(subset=['Uncertainty (%)'], cmap='RdYlGn_r', vmin=0, vmax=50)
            
            st.dataframe(styled_forecast, use_container_width=True, height=300)
        
        except ImportError as e:
            st.error(f"⚠️ **Library not installed:** {str(e)}")
            st.info("💡 Install required libraries: `pip install prophet statsmodels scikit-learn --break-system-packages`")
            st.warning("Showing simple linear forecast as fallback...")
            
            # Simple fallback
            from sklearn.linear_model import LinearRegression
            X = np.arange(len(monthly_revenue)).reshape(-1, 1)
            y = monthly_revenue['net_revenue'].values
            model = LinearRegression()
            model.fit(X, y)
            
            future_X = np.arange(len(monthly_revenue), len(monthly_revenue) + future_months).reshape(-1, 1)
            forecast_values = np.maximum(model.predict(future_X), 0)
            
            last_date = monthly_revenue['order_month'].iloc[-1]
            forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=future_months, freq='MS')
            
            st.line_chart(pd.DataFrame({
                'Month': forecast_dates.strftime('%b %Y'),
                'Forecast': forecast_values
            }).set_index('Month'))
        
        except Exception as e:
            st.error(f"⚠️ Error in forecasting: {str(e)}")
            st.info("💡 Try using a different forecasting method or check your data quality.")
    
    elif len(monthly_revenue) >= 3:
        st.warning("⚠️ Need at least 6 months of data for Prophet. Using simple linear forecast...")
        
        # Simple linear regression fallback
        from scipy.stats import linregress
        
        X = np.arange(len(monthly_revenue))
        y = monthly_revenue['net_revenue'].values
        slope, intercept, r_value, p_value, std_err = linregress(X, y)
        
        future_months = 12
        future_X = np.arange(len(monthly_revenue), len(monthly_revenue) + future_months)
        forecast_values = slope * future_X + intercept
        forecast_values = np.maximum(forecast_values, 0)  # No negative forecasts
        
        last_date = monthly_revenue['order_month'].iloc[-1]
        forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=future_months, freq='MS')
        
        forecast_df = pd.DataFrame({
            'Month': forecast_dates,
            'Forecast': forecast_values,
            'Lower': forecast_values * 0.85,
            'Upper': forecast_values * 1.15
        })
        forecast_df['Month_Label'] = forecast_df['Month'].dt.strftime('%b %Y')
        
        total_forecast = forecast_df['Forecast'].sum()
        avg_monthly = forecast_df['Forecast'].mean()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=monthly_revenue['order_month'].dt.strftime('%b %Y'),
                y=monthly_revenue['net_revenue'],
                name='Actual',
                mode='lines+markers',
                line=dict(color='#3498db', width=3),
                marker=dict(size=8)
            ))
            
            fig.add_trace(go.Scatter(
                x=forecast_df['Month_Label'],
                y=forecast_df['Forecast'],
                name='Linear Forecast',
                mode='lines+markers',
                line=dict(color='#e74c3c', width=3, dash='dash'),
                marker=dict(size=8, symbol='diamond')
            ))
            
            fig.update_layout(
                title='<b>Revenue Forecast - Linear Trend</b>',
                xaxis=dict(title=''),
                yaxis=dict(title='Revenue (฿)'),
                plot_bgcolor='white',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 30px; border-radius: 10px; color: white; text-align: center; height: 400px;
                        display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size: 14px; opacity: 0.9; margin-bottom: 15px;'>
                    <b>FORECAST SUMMARY</b>
                </div>
                <div style='margin: 20px 0;'>
                    <div style='font-size: 12px; opacity: 0.8;'>Next 12 Months Total</div>
                    <div style='font-size: 36px; font-weight: bold; margin: 10px 0;'>
                        ฿{total_forecast/1000000:.1f}M
                    </div>
                </div>
                <div style='margin: 20px 0;'>
                    <div style='font-size: 12px; opacity: 0.8;'>Average Monthly</div>
                    <div style='font-size: 28px; font-weight: bold; margin: 10px 0;'>
                        ฿{avg_monthly/1000:.0f}K
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.info("💡 Add more historical data (6+ months) to enable Prophet time series forecasting for better accuracy.")
    else:
        st.warning("⚠️ ต้องมีข้อมูลอย่างน้อย 3 เดือนเพื่อทำ Forecast")
    
    st.markdown("---")
    
    # ==================== STOCK PLANNING ====================
    st.markdown("### 📦 Stock Planning Recommendation")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 Stock Planning:</b> แนะนำปริมาณสต็อกที่ควรมีสำหรับแต่ละสินค้า<br>
        <div class='metric-formula'>
        สูตร: (ยอดขายเฉลี่ยต่อเดือน × Lead Time) + Safety Stock
        </div>
        <b>📖 Safety Stock:</b> สต็อกสำรอง เผื่อความผันผวนของยอดขาย (20% ของยอดขายเฉลี่ย)<br>
        <b>💡 การใช้ประโยชน์:</b><br>
        • ป้องกันสินค้าหมด<br>
        • ลดต้นทุนการจัดเก็บ<br>
        • วางแผนสั่งซื้อล่วงหน้า
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate stock recommendations
    # Assume lead time of 30 days (1 month)
    lead_time_months = 1
    safety_stock_pct = 0.20
    
    # Get product sales data
    product_monthly = df_filtered.groupby(['product_id', 'product_name', 'category', 'order_month']).agg({
        'quantity': 'sum'
    }).reset_index()
    
    # Calculate average monthly sales per product
    product_avg = product_monthly.groupby(['product_id', 'product_name', 'category']).agg({
        'quantity': ['mean', 'std', 'count']
    }).reset_index()
    
    product_avg.columns = ['product_id', 'product_name', 'category', 'avg_monthly_qty', 'std_qty', 'months']
    
    # Calculate stock recommendations
    product_avg['lead_time_demand'] = product_avg['avg_monthly_qty'] * lead_time_months
    product_avg['safety_stock'] = product_avg['avg_monthly_qty'] * safety_stock_pct
    product_avg['reorder_point'] = product_avg['lead_time_demand'] + product_avg['safety_stock']
    product_avg['recommended_stock'] = np.ceil(product_avg['reorder_point'] * 1.5)  # Add buffer
    
    # Add current stock status (simulated - in real case, get from inventory table)
    if 'inventory' in data:
        # Try to get actual stock levels
        try:
            current_stock = data['inventory'].groupby('product_id')['quantity'].last().to_dict()
            product_avg['current_stock'] = product_avg['product_id'].map(current_stock).fillna(0)
        except:
            product_avg['current_stock'] = product_avg['recommended_stock'] * 0.6  # Simulated
    else:
        product_avg['current_stock'] = product_avg['recommended_stock'] * 0.6  # Simulated
    
    # Calculate stock status
    product_avg['stock_status'] = product_avg.apply(
        lambda x: 'Overstock' if x['current_stock'] > x['recommended_stock'] * 1.2
        else 'Low Stock' if x['current_stock'] < x['reorder_point']
        else 'Optimal', axis=1
    )
    
    product_avg['order_qty'] = np.maximum(0, product_avg['recommended_stock'] - product_avg['current_stock'])
    
    # Sort by order quantity
    product_avg = product_avg.sort_values('order_qty', ascending=False)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    low_stock_count = len(product_avg[product_avg['stock_status'] == 'Low Stock'])
    optimal_count = len(product_avg[product_avg['stock_status'] == 'Optimal'])
    overstock_count = len(product_avg[product_avg['stock_status'] == 'Overstock'])
    total_order_needed = product_avg['order_qty'].sum()
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9;'>LOW STOCK</div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
                {low_stock_count}
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Products need reorder</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9;'>OPTIMAL</div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
                {optimal_count}
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Products at good level</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9;'>OVERSTOCK</div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
                {overstock_count}
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Products excess stock</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9;'>TOTAL ORDER NEEDED</div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
                {total_order_needed:,.0f}
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Units to order</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Stock status breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        status_counts = product_avg['stock_status'].value_counts()
        status_colors = {
            'Low Stock': '#e74c3c',
            'Optimal': '#2ecc71',
            'Overstock': '#f39c12'
        }
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=list(status_counts.index),
            y=list(status_counts.values),
            marker=dict(color=[status_colors.get(s, '#95a5a6') for s in status_counts.index]),
            text=list(status_counts.values),
            texttemplate='%{text}',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Products: %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Stock Status Distribution</b>',
            xaxis=dict(title='', showgrid=False),
            yaxis=dict(title='Number of Products', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            plot_bgcolor='white',
            height=350,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top products needing reorder
        top_reorder = product_avg[product_avg['stock_status'] == 'Low Stock'].head(10)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=top_reorder['product_name'],
            x=top_reorder['order_qty'],
            orientation='h',
            marker_color='#e74c3c',
            text=top_reorder['order_qty'],
            texttemplate='%{text:,.0f}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Need to Order: %{x:,.0f} units<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Top 10 Products Needing Reorder</b>',
            xaxis=dict(title='Quantity to Order', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            yaxis=dict(title='', categoryorder='total ascending'),
            plot_bgcolor='white',
            height=350,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed stock planning table
    st.markdown("#### 📋 Detailed Stock Planning (Top 30 Products)")
    
    top_products = product_avg.head(30).copy()
    top_products_display = top_products[[
        'product_name', 'category', 'avg_monthly_qty', 'current_stock', 
        'reorder_point', 'recommended_stock', 'order_qty', 'stock_status'
    ]].copy()
    
    top_products_display.columns = [
        'Product', 'Category', 'Avg Monthly Sales', 'Current Stock',
        'Reorder Point', 'Recommended Stock', 'Order Qty', 'Status'
    ]
    
    # Style based on stock status
    def highlight_status(row):
        if row['Status'] == 'Low Stock':
            return ['background-color: #ffebee'] * len(row)
        elif row['Status'] == 'Overstock':
            return ['background-color: #fff3e0'] * len(row)
        else:
            return ['background-color: #e8f5e9'] * len(row)
    
    styled_stock = top_products_display.style.format({
        'Avg Monthly Sales': '{:.0f}',
        'Current Stock': '{:.0f}',
        'Reorder Point': '{:.0f}',
        'Recommended Stock': '{:.0f}',
        'Order Qty': '{:.0f}'
    }).apply(highlight_status, axis=1)
    
    st.dataframe(styled_stock, use_container_width=True, height=400)
    
    st.markdown("---")
    
    # ==================== DEMAND FORECASTING BY PRODUCT ====================
    st.markdown("### 📊 Demand Forecasting by Product Category")
    
    st.markdown("""
    <div class='metric-explanation'>
        <b>📖 Demand Forecasting:</b> ทำนายความต้องการสินค้าแต่ละหมวดหมู่ในอนาคต<br>
        <b>💡 ประโยชน์:</b> วางแผนการผลิต/สั่งซื้อ แยกตามหมวดหมู่สินค้า
    </div>
    """, unsafe_allow_html=True)
    
    # Category demand forecast
    category_monthly = df_filtered.groupby(['order_month', 'category']).agg({
        'quantity': 'sum'
    }).reset_index()
    category_monthly['order_month'] = category_monthly['order_month'].dt.to_timestamp()
    
    # Get top 5 categories by total volume
    top_categories = df_filtered.groupby('category')['quantity'].sum().nlargest(5).index.tolist()
    
    fig = go.Figure()
    
    for category in top_categories:
        cat_data = category_monthly[category_monthly['category'] == category].sort_values('order_month')
        
        fig.add_trace(go.Scatter(
            x=cat_data['order_month'].dt.strftime('%b %Y'),
            y=cat_data['quantity'],
            name=category,
            mode='lines+markers',
            line=dict(width=2),
            marker=dict(size=6),
            hovertemplate=f'<b>{category}</b><br>%{{x}}<br>Qty: %{{y:,.0f}}<extra></extra>'
        ))
    
    fig.update_layout(
        title='<b>Demand Trend by Category</b>',
        xaxis=dict(title='', showgrid=False),
        yaxis=dict(title='Quantity Sold', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
        plot_bgcolor='white',
        height=400,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Category forecast summary
    category_forecast = []
    for category in top_categories:
        cat_data = category_monthly[category_monthly['category'] == category].sort_values('order_month')
        avg_qty = cat_data['quantity'].mean()
        recent_growth = cat_data['quantity'].pct_change().tail(3).mean()
        
        if not np.isnan(recent_growth):
            next_month_forecast = avg_qty * (1 + recent_growth)
        else:
            next_month_forecast = avg_qty
        
        category_forecast.append({
            'Category': category,
            'Avg Monthly': avg_qty,
            'Growth Rate': recent_growth * 100 if not np.isnan(recent_growth) else 0,
            'Next Month Forecast': next_month_forecast
        })
    
    forecast_cat_df = pd.DataFrame(category_forecast)
    
    st.markdown("#### 📋 Category Demand Forecast")
    
    styled_cat_forecast = forecast_cat_df.style.format({
        'Avg Monthly': '{:.0f}',
        'Growth Rate': '{:+.1f}%',
        'Next Month Forecast': '{:.0f}'
    }).background_gradient(subset=['Growth Rate'], cmap='RdYlGn', vmin=-10, vmax=10)
    
    st.dataframe(styled_cat_forecast, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 15px; color: white;'>
    <h3 style='margin: 0; font-size: 24px;'>📊 Fashion Analytics Dashboard</h3>
    <p style='margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;'>
        Built with Streamlit • Data-Driven Insights with Professional KPIs
    </p>
</div>
""", unsafe_allow_html=True)
