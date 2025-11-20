# # app.py - Modern E-commerce Analytics Dashboard with Geographic Analysis
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, timedelta
# import numpy as np
# from sklearn.cluster import KMeans
# from sklearn.preprocessing import StandardScaler
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import classification_report, roc_auc_score
# import warnings
# import zipfile
# import io

# warnings.filterwarnings('ignore')

# # Page config
# st.set_page_config(page_title="E-commerce Analytics", layout="wide", page_icon="📊")

# # Initialize session state
# if 'data_loaded' not in st.session_state:
#     st.session_state.data_loaded = False
# if 'data' not in st.session_state:
#     st.session_state.data = None

# # Utility function to map channel to type
# def get_channel_type(channel):
#     """Map channel to Online/Offline"""
#     online_channels = ['line shopping', 'lazada', 'shopee', 'tiktok']
#     offline_channels = ['siam center']
#     channel_lower = str(channel).lower()
#     for oc in online_channels:
#         if oc in channel_lower:
#             return 'Online'
#     for of in offline_channels:
#         if of in channel_lower:
#             return 'Offline'
#     return 'Other'

# # File upload options
# def upload_data():
#     """Flexible data upload - ZIP file or folder path"""
#     st.sidebar.title("📊 E-commerce Analytics")
#     st.sidebar.markdown("---")
    
#     upload_method = st.sidebar.radio(
#         "📁 Data Source",
#         ["Upload ZIP File", "Load from Folder Path"]
#     )
    
#     data = None
    
#     if upload_method == "Upload ZIP File":
#         st.sidebar.subheader("Upload ZIP containing CSV files")
#         st.sidebar.caption("ZIP should contain: user.csv, product.csv, order.csv, order_item.csv")
#         uploaded_zip = st.sidebar.file_uploader("Choose ZIP file", type=['zip'])
        
#         if uploaded_zip is not None:
#             if st.sidebar.button("🔄 Load Data", type="primary"):
#                 try:
#                     with zipfile.ZipFile(uploaded_zip) as z:
#                         data = {}
#                         file_mapping = {
#                             "distribution_centers.csv": "dc",
#                             "user.csv": "user",
#                             "product.csv": "product",
#                             "inventory_item.csv": "inventory",
#                             "order.csv": "order",
#                             "order_item.csv": "order_item",
#                             "event.csv": "event"
#                         }
                        
#                         for filename in z.namelist():
#                             base_name = filename.split('/')[-1]
#                             if base_name in file_mapping:
#                                 key = file_mapping[base_name]
#                                 with z.open(filename) as f:
#                                     data[key] = pd.read_csv(f)
#                                 st.sidebar.success(f"✅ {base_name}")
                        
#                         required = ['user', 'product', 'order', 'order_item']
#                         missing = [r for r in required if r not in data]
#                         if missing:
#                             st.sidebar.error(f"❌ Missing: {', '.join(missing)}")
#                             return None
                        
#                         st.session_state.data = data
#                         st.session_state.data_loaded = True
#                         st.sidebar.success("✅ All data loaded!")
#                         return data
#                 except Exception as e:
#                     st.sidebar.error(f"❌ Error: {str(e)}")
#                     return None
#     else:
#         data_path = st.sidebar.text_input("Folder path", value="data")
#         if st.sidebar.button("🔄 Load Data", type="primary"):
#             try:
#                 import os
#                 data = {}
#                 file_mapping = {
#                     "distribution_centers.csv": "dc",
#                     "user.csv": "user",
#                     "product.csv": "product",
#                     "inventory_item.csv": "inventory",
#                     "order.csv": "order",
#                     "order_item.csv": "order_item",
#                     "event.csv": "event"
#                 }
                
#                 for filename, key in file_mapping.items():
#                     filepath = os.path.join(data_path, filename)
#                     if os.path.exists(filepath):
#                         data[key] = pd.read_csv(filepath)
#                         st.sidebar.success(f"✅ {filename}")
                
#                 required = ['user', 'product', 'order', 'order_item']
#                 missing = [r for r in required if r not in data]
#                 if missing:
#                     st.sidebar.error(f"❌ Missing: {', '.join(missing)}")
#                     return None
                
#                 st.session_state.data = data
#                 st.session_state.data_loaded = True
#                 st.sidebar.success("✅ All data loaded!")
#                 return data
#             except Exception as e:
#                 st.sidebar.error(f"❌ Error: {str(e)}")
#                 return None
    
#     return st.session_state.data if st.session_state.data_loaded else None

# @st.cache_data
# def merge_and_preprocess(data):
#     """Merge all tables and create master dataframe"""
#     df = data['order_item'].merge(
#         data['order'][['order_id', 'channel', 'discount_pct', 'status', 'num_of_item', 'created_at']],
#         on='order_id', how='left', suffixes=('', '_order')
#     )
#     df = df.merge(
#         data['product'][['product_id', 'product_category', 'product_collection', 'retail_price', 'product_name']],
#         on='product_id', how='left', suffixes=('', '_prod')
#     )
#     df = df.merge(
#         data['user'][['user_id', 'city', 'traffic_source', 'age', 'gender']],
#         on='user_id', how='left'
#     )
    
#     # Date conversions
#     for col in ['created_at', 'shipped_at', 'delivered_at', 'returned_at']:
#         if col in df.columns:
#             df[col] = pd.to_datetime(df[col], errors='coerce')
    
#     # Derived fields
#     df['profit'] = df['sale_price'] - df['cost']
#     df['order_date'] = df['created_at'].dt.date
#     df['order_month'] = df['created_at'].dt.to_period('M')
#     df['order_year'] = df['created_at'].dt.year
#     df['order_quarter'] = df['created_at'].dt.quarter
#     df['order_hour'] = df['created_at'].dt.hour
#     df['order_dayofweek'] = df['created_at'].dt.dayofweek
#     df['channel_type'] = df['channel'].apply(get_channel_type)
    
#     return df, data

# # ========================================== 
# # SIDEBAR - Data Upload
# # ========================================== 
# data = upload_data()

# if data is None or not st.session_state.data_loaded:
#     st.title("📊 E-commerce Analytics Dashboard")
#     st.info("👈 Please load your data in the sidebar to begin analysis")
    
#     col1, col2 = st.columns(2)
#     with col1:
#         st.markdown("""
#         ### 📦 Option 1: Upload ZIP File
#         - Create a ZIP file containing your CSV files
#         - Upload it directly through the web interface
#         - Quick and easy!
#         """)
#     with col2:
#         st.markdown("""
#         ### 📁 Option 2: Load from Folder
#         - Place CSV files in a folder (e.g., 'data/')
#         - Specify the folder path
#         - Great for local development
#         """)
    
#     st.markdown("""
#     ---
#     ### Required Files:
#     - ✅ **user.csv** - User information
#     - ✅ **product.csv** - Product catalog
#     - ✅ **order.csv** - Order details
#     - ✅ **order_item.csv** - Order line items
    
#     ### Optional Files:
#     - distribution_centers.csv
#     - inventory_item.csv
#     - event.csv
#     """)
#     st.stop()

# # Process data
# df_master, data_dict = merge_and_preprocess(data)

# st.sidebar.markdown("---")
# st.sidebar.success(f"✅ {len(df_master):,} transactions")
# st.sidebar.metric("Total Revenue", f"฿{df_master['sale_price'].sum():,.0f}")
# st.sidebar.metric("Total Profit", f"฿{df_master['profit'].sum():,.0f}")

# # ========================================== 
# # MAIN TABS
# # ========================================== 
# tab1, tab2, tab3, tab4 = st.tabs([
#     "👥 Customer Analytics",
#     "📦 Inventory Forecast",
#     "💰 Accounting & Profit",
#     "🎯 Marketing Analytics"
# ])

# # ========================================== 
# # TAB 1: CUSTOMER ANALYTICS
# # ========================================== 
# with tab1:
#     st.header("👥 Customer Analytics")
    
#     # Date Range Filter
#     st.subheader("📅 Analysis Period")
#     col1, col2, col3 = st.columns([2, 2, 1])
    
#     with col1:
#         min_date = df_master['created_at'].min().date()
#         max_date = df_master['created_at'].max().date()
#         date_range = st.date_input(
#             "Select Date Range",
#             value=(min_date, max_date),
#             min_value=min_date,
#             max_value=max_date
#         )
    
#     with col2:
#         quick_filter = st.selectbox(
#             "Quick Filter",
#             ["All Time", "Last 30 Days", "Last 90 Days", "2024", "2025", 
#              "Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024", "Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025"]
#         )
        
#         # Apply quick filters
#         if quick_filter != "All Time":
#             max_dt = df_master['created_at'].max()
#             if quick_filter == "Last 30 Days":
#                 date_range = (max_dt - timedelta(days=30)).date(), max_dt.date()
#             elif quick_filter == "Last 90 Days":
#                 date_range = (max_dt - timedelta(days=90)).date(), max_dt.date()
#             elif quick_filter == "2024":
#                 date_range = pd.Timestamp('2024-01-01').date(), pd.Timestamp('2024-12-31').date()
#             elif quick_filter == "2025":
#                 date_range = pd.Timestamp('2025-01-01').date(), max_dt.date()
#             elif quick_filter == "Q1 2024":
#                 date_range = pd.Timestamp('2024-01-01').date(), pd.Timestamp('2024-03-31').date()
#             elif quick_filter == "Q2 2024":
#                 date_range = pd.Timestamp('2024-04-01').date(), pd.Timestamp('2024-06-30').date()
#             elif quick_filter == "Q3 2024":
#                 date_range = pd.Timestamp('2024-07-01').date(), pd.Timestamp('2024-09-30').date()
#             elif quick_filter == "Q4 2024":
#                 date_range = pd.Timestamp('2024-10-01').date(), pd.Timestamp('2024-12-31').date()
#             elif quick_filter == "Q1 2025":
#                 date_range = pd.Timestamp('2025-01-01').date(), pd.Timestamp('2025-03-31').date()
#             elif quick_filter == "Q2 2025":
#                 date_range = pd.Timestamp('2025-04-01').date(), pd.Timestamp('2025-06-30').date()
#             elif quick_filter == "Q3 2025":
#                 date_range = pd.Timestamp('2025-07-01').date(), pd.Timestamp('2025-09-30').date()
#             elif quick_filter == "Q4 2025":
#                 date_range = pd.Timestamp('2025-10-01').date(), pd.Timestamp('2025-12-31').date()
#     with col3:
#         # Apply filter
#         if len(date_range) == 2:
#             df_filtered = df_master[
#                 (df_master['created_at'].dt.date >= date_range[0]) & 
#                 (df_master['created_at'].dt.date <= date_range[1])
#             ]
#         else:
#             df_filtered = df_master
        
#         st.metric("Transactions", f"{len(df_filtered):,}")
    
#     # Display selected period info
#     st.info(f"📊 Analyzing data from **{date_range[0]}** to **{date_range[1]}** ({len(df_filtered):,} transactions)")
    
#     # Geographic Analysis
#     st.subheader("🗺️ Geographic Customer Distribution")
    
#     # Thai provinces to regions mapping
#     province_to_region = {
#         'Bangkok':'Central','Samut Prakan':'Central','Nonthaburi':'Central','Pathum Thani':'Central','Phra Nakhon Si Ayutthaya':'Central',
#         'Ang Thong':'Central','Lop Buri':'Central','Sing Buri':'Central','Chai Nat':'Central','Saraburi':'Central','Chon Buri':'Central',
#         'Rayong':'Central','Chanthaburi':'Central','Trat':'Central','Chachoengsao':'Central','Prachin Buri':'Central','Nakhon Nayok':'Central',
#         'Sra Kaew':'Central','Ratchaburi':'Central','Kanchanaburi':'Central','Suphan Buri':'Central','Nakhon Pathom':'Central','Samut Sakon':'Central',
#         'Samut Songkram':'Central','Phetchaburi':'Central','Prachuapkhiri Khan':'Central',
#         'Chiang Mai':'Northern','Lamphun':'Northern','Lampang':'Northern','Uttaradit':'Northern','Phrae':'Northern','Nan':'Northern','Phayao':'Northern',
#         'Chiang Rai':'Northern','Mae Hong Son':'Northern','Nakhon Sawan':'Northern','Uthai Thani':'Northern','Kamphaeng Phet':'Northern',
#         'Tak':'Northern','Sukhothai':'Northern','Phisanulok':'Northern','Phichit':'Northern','Phetchabun':'Northern',
#         'Nakhon Ratchasima':'Northeastern','Buri Ram':'Northeastern','Surin':'Northeastern','Si Sa Ket':'Northeastern','Ubon Ratchathani':'Northeastern',
#         'Yasothon':'Northeastern','Chaiyaphum':'Northeastern','Amnat Charoen':'Northeastern','Bungkan':'Northeastern','Nong Bua Lam Phu':'Northeastern',
#         'Khon Kaen ':'Northeastern','Udon Thani':'Northeastern','Loei':'Northeastern','Nong Khai':'Northeastern','Maha Sarakham':'Northeastern',
#         'Roi Et':'Northeastern','Kalasin':'Northeastern','Sakon Nakhon':'Northeastern','Naknon Phanom':'Northeastern','Mukdahan':'Northeastern',
#         'Nakhon Si Thammarat':'Southern','Krabi':'Southern','Phangnga':'Southern','Phuket':'Southern','Surat Thani':'Southern','Ranong':'Southern',
#         'Chumphon':'Southern','Songkhla':'Southern','Satun':'Southern','Trang':'Southern','Phatthalung':'Southern','Pattani':'Southern','Yala':'Southern',
#         'Narathiwat':'Southern',
#         # 'Bangkok': 'กลาง', 'Samut Prakan': 'กลาง', 'Nonthaburi': 'กลาง',
#         # 'Pathum Thani': 'กลาง', 'Phra Nakhon Si Ayutthaya': 'กลาง', 'Ayutthaya': 'กลาง',
#         # 'Saraburi': 'กลาง', 'Lop Buri': 'กลาง', 'Sing Buri': 'กลาง', 'Chai Nat': 'กลาง',
#         # 'Suphan Buri': 'กลาง', 'Ang Thong': 'กลาง', 'Nakhon Pathom': 'กลาง',
#         # 'Chiang Mai': 'เหนือ', 'Chiang Rai': 'เหนือ', 'Lampang': 'เหนือ', 'Lamphun': 'เหนือ',
#         # 'Mae Hong Son': 'เหนือ', 'Nan': 'เหนือ', 'Phayao': 'เหนือ', 'Phrae': 'เหนือ',
#         # 'Uttaradit': 'เหนือ', 'Phitsanulok': 'เหนือ', 'Sukhothai': 'เหนือ', 'Tak': 'เหนือ',
#         # 'Kamphaeng Phet': 'เหนือ', 'Phichit': 'เหนือ', 'Phetchabun': 'เหนือ',
#         # 'Nakhon Ratchasima': 'อีสาน', 'Buriram': 'อีสาน', 'Surin': 'อีสาน',
#         # 'Si Sa Ket': 'อีสาน', 'Ubon Ratchathani': 'อีสาน', 'Yasothon': 'อีสาน',
#         # 'Chaiyaphum': 'อีสาน', 'Amnat Charoen': 'อีสาน', 'Nong Bua Lamphu': 'อีสาน',
#         # 'Khon Kaen': 'อีสาน', 'Udon Thani': 'อีสาน', 'Loei': 'อีสาน',
#         # 'Nong Khai': 'อีสาน', 'Maha Sarakham': 'อีสาน', 'Roi Et': 'อีสาน',
#         # 'Kalasin': 'อีสาน', 'Sakon Nakhon': 'อีสาน', 'Nakhon Phanom': 'อีสาน',
#         # 'Mukdahan': 'อีสาน', 'Bueng Kan': 'อีสาน',
#         # 'Phuket': 'ใต้', 'Krabi': 'ใต้', 'Phang Nga': 'ใต้', 'Surat Thani': 'ใต้',
#         # 'Ranong': 'ใต้', 'Chumphon': 'ใต้', 'Nakhon Si Thammarat': 'ใต้', 'Trang': 'ใต้',
#         # 'Phatthalung': 'ใต้', 'Songkhla': 'ใต้', 'Satun': 'ใต้', 'Pattani': 'ใต้',
#         # 'Yala': 'ใต้', 'Narathiwat': 'ใต้',
#         # 'Ratchaburi': 'ตะวันตก', 'Kanchanaburi': 'ตะวันตก', 'Samut Songkhram': 'ตะวันตก',
#         # 'Samut Sakhon': 'ตะวันตก', 'Phetchaburi': 'ตะวันตก', 'Prachuap Khiri Khan': 'ตะวันตก',
#         # 'Chonburi': 'ตะวันออก', 'Rayong': 'ตะวันออก', 'Chanthaburi': 'ตะวันออก',
#         # 'Trat': 'ตะวันออก', 'Chachoengsao': 'ตะวันออก', 'Prachin Buri': 'ตะวันออก',
#         # 'Nakhon Nayok': 'ตะวันออก', 'Sa Kaeo': 'ตะวันออก'
#     }
    
#     def get_region(city):
#         if pd.isna(city):
#             return 'N/A'
#         city_lower = str(city).lower()
#         for province, region in province_to_region.items():
#             if province.lower() in city_lower:
#                 return region
#         return 'Other'
    
#     # Add region to filtered data
#     df_filtered_geo = df_filtered.copy()
#     df_filtered_geo['region'] = df_filtered_geo['city'].apply(get_region)
    
#     # Customer geographic analysis
#     customer_geo = df_filtered_geo.groupby(['user_id', 'city', 'region', 'age', 'gender']).agg({
#         'sale_price': 'sum',
#         'order_id': 'nunique'
#     }).reset_index()
#     customer_geo.columns = ['user_id', 'city', 'region', 'age', 'gender', 'total_spent', 'total_orders']
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         # Region distribution
#         region_dist = customer_geo.groupby('region').agg({
#             'user_id': 'nunique',
#             'total_spent': 'sum'
#         }).reset_index()
#         region_dist.columns = ['Region', 'no. of Customers', 'Sale']
        
#         fig = px.pie(region_dist, 
#                      values='no. of Customers', 
#                      names='Region',
#                      title="การกระจายลูกค้าตามภูมิภาค",
#                      hole=0.4,
#                      color_discrete_sequence=px.colors.sequential.RdBu)
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         # Top cities by customers
#         top_cities = customer_geo.groupby('city')['user_id'].nunique().nlargest(10).reset_index()
#         top_cities.columns = ['จังหวัด', 'จำนวนลูกค้า']
        
#         fig = px.bar(top_cities, 
#                      x='จำนวนลูกค้า', 
#                      y='จังหวัด',
#                      orientation='h',
#                      title="Top 10 จังหวัด (จำนวนลูกค้า)",
#                      color='จำนวนลูกค้า',
#                      color_continuous_scale='Viridis')
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col3:
#         # Age distribution
#         age_dist = customer_geo[customer_geo['age'].notna()].copy()
#         age_dist['age_group'] = pd.cut(age_dist['age'], 
#                                        bins=[0, 20, 30, 40, 50, 60, 100],
#                                        labels=['<20', '20-30', '30-40', '40-50', '50-60', '60+'])
#         age_group_dist = age_dist.groupby('age_group')['user_id'].nunique().reset_index()
#         age_group_dist.columns = ['กลุ่มอายุ', 'จำนวนลูกค้า']
        
#         fig = px.bar(age_group_dist, 
#                      x='กลุ่มอายุ', 
#                      y='จำนวนลูกค้า',
#                      title="การกระจายลูกค้าตามช่วงอายุ",
#                      color='จำนวนลูกค้า',
#                      color_continuous_scale='Teal')
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Detailed geographic table
#     st.subheader("📊 สรุปข้อมูลตามภูมิภาคและจังหวัด")
    
#     geo_summary = customer_geo.groupby(['region', 'city']).agg({
#         'user_id': 'nunique',
#         'total_spent': 'sum',
#         'total_orders': 'sum'
#     }).reset_index()
#     geo_summary.columns = ['ภูมิภาค', 'จังหวัด', 'จำนวนลูกค้า', 'ยอดขายรวม (฿)', 'จำนวนคำสั่งซื้อ']
#     geo_summary['ยอดเฉลี่ยต่อลูกค้า (฿)'] = (geo_summary['ยอดขายรวม (฿)'] / geo_summary['จำนวนลูกค้า']).round(2)
#     geo_summary = geo_summary.sort_values('ยอดขายรวม (฿)', ascending=False)
    
#     # Filter by region
#     selected_regions = st.multiselect(
#         "เลือกภูมิภาค",
#         options=geo_summary['ภูมิภาค'].unique(),
#         default=geo_summary['ภูมิภาค'].unique()
#     )
    
#     filtered_geo = geo_summary[geo_summary['ภูมิภาค'].isin(selected_regions)]
#     st.dataframe(filtered_geo, use_container_width=True, height=400)
    
#     # Monthly trends by region
#     st.subheader("📈 Trend การขายตามภูมิภาคและเวลา")
    
#     monthly_region = df_filtered_geo.groupby([df_filtered_geo['created_at'].dt.to_period('M'), 'region']).agg({
#         'sale_price': 'sum',
#         'order_id': 'nunique'
#     }).reset_index()
#     monthly_region['created_at'] = monthly_region['created_at'].dt.to_timestamp()
#     monthly_region.columns = ['เดือน', 'ภูมิภาค', 'ยอดขาย', 'จำนวนคำสั่งซื้อ']
    
#     fig = px.line(monthly_region, 
#                   x='เดือน', 
#                   y='ยอดขาย',
#                   color='ภูมิภาค',
#                   title="ยอดขายรายเดือนแยกตามภูมิภาค",
#                   markers=True)
#     st.plotly_chart(fig, use_container_width=True)
    
#     # Customer Segmentation by Value
#     st.subheader("1️⃣ Customer Value Segmentation")
    
#     # Calculate customer metrics
#     customer_metrics = df_filtered.groupby('user_id').agg({
#         'created_at': lambda x: (df_filtered['created_at'].max() - x.max()).days,
#         'order_id': 'nunique',
#         'sale_price': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     customer_metrics.columns = ['user_id', 'days_since_last_order', 'total_orders', 'total_revenue', 'total_profit']
    
#     # Segment by value
#     customer_metrics['segment'] = pd.qcut(
#         customer_metrics['total_revenue'],
#         q=4,
#         labels=['Bronze', 'Silver', 'Gold', 'Platinum'],
#         duplicates='drop'
#     )
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         seg_dist = customer_metrics['segment'].value_counts()
#         fig = px.pie(values=seg_dist.values, 
#                      names=seg_dist.index,
#                      title="Customer Distribution by Value",
#                      hole=0.4,
#                      color_discrete_sequence=px.colors.sequential.Agsunset)
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         seg_value = customer_metrics.groupby('segment')['total_revenue'].sum().sort_values(ascending=True)
#         fig = px.bar(x=seg_value.values, 
#                      y=seg_value.index,
#                      orientation='h',
#                      title="Total Revenue by Segment",
#                      labels={'x': 'Revenue (฿)', 'y': 'Segment'},
#                      color=seg_value.index,
#                      color_discrete_sequence=px.colors.sequential.Agsunset)
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Segment metrics
#     st.subheader("Segment Performance Metrics")
#     seg_metrics = customer_metrics.groupby('segment').agg({
#         'user_id': 'count',
#         'total_orders': 'mean',
#         'total_revenue': 'mean',
#         'total_profit': 'mean',
#         'days_since_last_order': 'mean'
#     }).round(2)
#     seg_metrics.columns = ['Customers', 'Avg Orders', 'Avg Revenue (฿)', 'Avg Profit (฿)', 'Avg Days Since Order']
#     st.dataframe(seg_metrics, use_container_width=True)
    
#     # Customer Behavior Patterns
#     st.subheader("2️⃣ Customer Behavior Patterns")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         hourly = df_filtered.groupby('order_hour').size().reset_index(name='orders')
#         fig = px.area(hourly, 
#                       x='order_hour', 
#                       y='orders',
#                       title="Orders by Hour of Day",
#                       labels={'order_hour': 'Hour', 'orders': 'Orders'})
#         fig.update_traces(line_color='#FF6B6B', fillcolor='rgba(255,107,107,0.3)')
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         dow_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
#         daily = df_filtered.groupby('order_dayofweek').size().reset_index(name='orders')
#         daily['day'] = daily['order_dayofweek'].map(dow_map)
#         fig = px.bar(daily, 
#                      x='day', 
#                      y='orders',
#                      title="Orders by Day of Week",
#                      color='orders',
#                      color_continuous_scale='blues')
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Churn Analysis
#     st.subheader("3️⃣ Customer Retention & Churn")
    
#     customer_metrics['is_churned'] = (customer_metrics['days_since_last_order'] > 60).astype(int)
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         active_customers = (customer_metrics['is_churned'] == 0).sum()
#         st.metric("Active Customers", f"{active_customers:,}")
    
#     with col2:
#         churned_customers = (customer_metrics['is_churned'] == 1).sum()
#         st.metric("Churned Customers", f"{churned_customers:,}")
    
#     with col3:
#         churn_rate = customer_metrics['is_churned'].mean() * 100
#         st.metric("Churn Rate", f"{churn_rate:.1f}%")
    
#     with col4:
#         avg_customer_lifetime = customer_metrics['total_orders'].mean()
#         st.metric("Avg Orders per Customer", f"{avg_customer_lifetime:.1f}")
    
#     churn_by_seg = customer_metrics.groupby('segment')['is_churned'].mean() * 100
#     fig = px.bar(x=churn_by_seg.index, 
#                  y=churn_by_seg.values,
#                  title="Churn Rate by Customer Segment (%)",
#                  labels={'x': 'Segment', 'y': 'Churn Rate (%)'},
#                  color=churn_by_seg.values,
#                  color_continuous_scale='reds')
#     st.plotly_chart(fig, use_container_width=True)

# # ========================================== 
# # TAB 2: INVENTORY FORECAST
# # ========================================== 
# with tab2:
#     st.header("📦 Inventory Forecasting")
    
#     # Product filters
#     st.subheader("🔍 Product Filters")
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         categories = ['All'] + sorted(df_master['product_category'].dropna().unique().tolist())
#         selected_category = st.selectbox("Category", categories)
    
#     with col2:
#         if selected_category != 'All':
#             filtered_df = df_master[df_master['product_category'] == selected_category]
#         else:
#             filtered_df = df_master
        
#         product_list = filtered_df.groupby(['product_id', 'product_name']).size().reset_index(name='count')
#         product_list = product_list.nlargest(50, 'count')
#         product_options = {f"{row['product_name']} (ID: {row['product_id']})": row['product_id'] 
#                           for _, row in product_list.iterrows()}
#         selected_product_name = st.selectbox("Select Product", list(product_options.keys()))
#         selected_product = product_options[selected_product_name]
    
#     with col3:
#         st.metric("Total Products", f"{df_master['product_id'].nunique():,}")
    
#     # Product demand analysis
#     st.subheader("1️⃣ Demand Forecast & Analysis")
    
#     demand_df = df_master.groupby(['order_date', 'product_id']).size().reset_index(name='quantity')
#     demand_df['order_date'] = pd.to_datetime(demand_df['order_date'])
#     prod_demand = demand_df[demand_df['product_id'] == selected_product].sort_values('order_date')
    
#     if len(prod_demand) > 7:
#         prod_demand['MA_7'] = prod_demand['quantity'].rolling(window=min(7, len(prod_demand))).mean()
#         if len(prod_demand) > 30:
#             prod_demand['MA_30'] = prod_demand['quantity'].rolling(window=30).mean()
        
#         col1, col2 = st.columns([2, 1])
        
#         with col1:
#             fig = go.Figure()
#             fig.add_trace(go.Scatter(x=prod_demand['order_date'], 
#                                     y=prod_demand['quantity'],
#                                     mode='lines+markers',
#                                     name='Actual Demand',
#                                     line=dict(color='lightblue', width=1),
#                                     marker=dict(size=4)))
#             fig.add_trace(go.Scatter(x=prod_demand['order_date'], 
#                                     y=prod_demand['MA_7'],
#                                     mode='lines',
#                                     name='7-Day MA',
#                                     line=dict(color='orange', width=2)))
#             if len(prod_demand) > 30:
#                 fig.add_trace(go.Scatter(x=prod_demand['order_date'], 
#                                         y=prod_demand['MA_30'],
#                                         mode='lines',
#                                         name='30-Day MA',
#                                         line=dict(color='red', width=2)))
            
#             fig.update_layout(title=f"Demand Trend: {selected_product_name}",
#                             xaxis_title="Date",
#                             yaxis_title="Quantity",
#                             hovermode='x unified')
#             st.plotly_chart(fig, use_container_width=True)
        
#         with col2:
#             last_7_avg = prod_demand['quantity'].tail(7).mean()
#             last_30_avg = prod_demand['quantity'].tail(30).mean() if len(prod_demand) >= 30 else last_7_avg
#             forecast_7d = last_7_avg * 7
#             forecast_30d = last_30_avg * 30
            
#             st.metric("Avg Daily Demand (7d)", f"{last_7_avg:.1f} units")
#             st.metric("Forecast Next 7 Days", f"{forecast_7d:.0f} units")
#             st.metric("Forecast Next 30 Days", f"{forecast_30d:.0f} units")
            
#             std_dev = prod_demand['quantity'].std()
#             safety_stock = 1.65 * std_dev * np.sqrt(7)
#             st.metric("Safety Stock (95% SL)", f"{safety_stock:.0f} units")
            
#             lead_time_days = 7
#             reorder_point = (last_7_avg * lead_time_days) + safety_stock
#             st.metric("Reorder Point", f"{reorder_point:.0f} units")
#     else:
#         st.warning("⚠️ Not enough data for this product (minimum 7 days required)")
    
#     # Fast vs Slow Moving Analysis
#     st.subheader("2️⃣ Product Movement Analysis")
    
#     product_velocity = df_master.groupby(['product_id', 'product_name']).agg({
#         'order_id': 'nunique',
#         'sale_price': 'sum'
#     }).reset_index()
#     product_velocity.columns = ['product_id', 'product_name', 'order_count', 'total_revenue']
    
#     velocity_threshold_fast = product_velocity['order_count'].quantile(0.75)
#     velocity_threshold_slow = product_velocity['order_count'].quantile(0.25)
    
#     def classify_movement(count):
#         if count >= velocity_threshold_fast:
#             return 'Fast Moving'
#         elif count <= velocity_threshold_slow:
#             return 'Slow Moving'
#         else:
#             return 'Medium Moving'
    
#     product_velocity['movement'] = product_velocity['order_count'].apply(classify_movement)
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         movement_dist = product_velocity['movement'].value_counts()
#         fig = px.pie(values=movement_dist.values, 
#                      names=movement_dist.index,
#                      title="Product Movement Distribution",
#                      hole=0.4,
#                      color_discrete_map={
#                          'Fast Moving': '#2ecc71',
#                          'Medium Moving': '#f39c12',
#                          'Slow Moving': '#e74c3c'
#                      })
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         top_fast = product_velocity[product_velocity['movement'] == 'Fast Moving'].nlargest(10, 'order_count')
#         fig = px.bar(top_fast, 
#                      x='order_count', 
#                      y='product_name',
#                      orientation='h',
#                      title="Top 10 Fast Moving Products",
#                      labels={'order_count': 'Order Count', 'product_name': 'Product'})
#         st.plotly_chart(fig, use_container_width=True)
    
#     st.subheader("Product Movement Details")
#     movement_filter = st.multiselect("Filter by Movement", 
#                                      ['Fast Moving', 'Medium Moving', 'Slow Moving'],
#                                      default=['Fast Moving'])
#     filtered_products = product_velocity[product_velocity['movement'].isin(movement_filter)]
#     st.dataframe(filtered_products.sort_values('order_count', ascending=False), 
#                 use_container_width=True, height=400)

# # ========================================== 
# # TAB 3: ACCOUNTING & PROFIT
# # ========================================== 
# with tab3:
#     st.header("💰 Accounting & Profitability Analysis")
    
#     st.subheader("1️⃣ Key Financial Metrics")
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         total_revenue = df_master['sale_price'].sum()
#         st.metric("Total Revenue", f"฿{total_revenue:,.0f}")
    
#     with col2:
#         total_cost = df_master['cost'].sum()
#         st.metric("Total Cost", f"฿{total_cost:,.0f}")
    
#     with col3:
#         total_profit = df_master['profit'].sum()
#         st.metric("Total Profit", f"฿{total_profit:,.0f}")
    
#     with col4:
#         profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
#         st.metric("Profit Margin", f"{profit_margin:.1f}%")
    
#     # Channel Performance
#     st.subheader("2️⃣ Channel Performance (Online vs Offline)")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         channel_type_perf = df_master.groupby('channel_type').agg({
#             'sale_price': 'sum',
#             'profit': 'sum',
#             'order_id': 'nunique'
#         }).reset_index()
#         channel_type_perf['profit_margin_%'] = (channel_type_perf['profit'] / channel_type_perf['sale_price'] * 100).round(1)
        
#         fig = px.pie(channel_type_perf, 
#                      values='sale_price', 
#                      names='channel_type',
#                      title="Revenue: Online vs Offline",
#                      hole=0.4,
#                      color_discrete_map={'Online': '#3498db', 'Offline': '#e67e22', 'Other': '#95a5a6'})
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         fig = px.bar(channel_type_perf, 
#                      x='channel_type', 
#                      y='profit_margin_%',
#                      title="Profit Margin: Online vs Offline (%)",
#                      color='channel_type',
#                      color_discrete_map={'Online': '#3498db', 'Offline': '#e67e22', 'Other': '#95a5a6'})
#         st.plotly_chart(fig, use_container_width=True)
    
#     st.subheader("Detailed Channel Breakdown")
#     channel_detail = df_master.groupby(['channel', 'channel_type']).agg({
#         'sale_price': 'sum',
#         'profit': 'sum',
#         'order_id': 'nunique'
#     }).reset_index()
#     channel_detail.columns = ['Channel', 'Type', 'Revenue (฿)', 'Profit (฿)', 'Orders']
#     channel_detail['Profit Margin (%)'] = (channel_detail['Profit (฿)'] / channel_detail['Revenue (฿)'] * 100).round(1)
#     channel_detail['AOV (฿)'] = (channel_detail['Revenue (฿)'] / channel_detail['Orders']).round(2)
#     st.dataframe(channel_detail.sort_values('Revenue (฿)', ascending=False), 
#                 use_container_width=True, height=300)
    
#     # Category profitability
#     st.subheader("3️⃣ Product Category Profitability")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         cat_profit = df_master.groupby('product_category').agg({
#             'sale_price': 'sum',
#             'profit': 'sum'
#         }).reset_index()
#         cat_profit['margin_%'] = (cat_profit['profit'] / cat_profit['sale_price'] * 100).round(1)
#         cat_profit = cat_profit.sort_values('profit', ascending=True)
        
#         fig = px.bar(cat_profit, 
#                      x='profit', 
#                      y='product_category',
#                      orientation='h',
#                      title="Profit by Product Category",
#                      labels={'profit': 'Profit (฿)', 'product_category': 'Category'},
#                      color='margin_%',
#                      color_continuous_scale='RdYlGn')
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         fig = px.scatter(cat_profit, 
#                         x='sale_price', 
#                         y='profit',
#                         size='margin_%',
#                         text='product_category',
#                         title="Revenue vs Profit by Category",
#                         labels={'sale_price': 'Revenue (฿)', 'profit': 'Profit (฿)'},
#                         color='margin_%',
#                         color_continuous_scale='RdYlGn')
#         fig.update_traces(textposition='top center')
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Monthly revenue trend
#     st.subheader("4️⃣ Revenue & Profit Trends")
    
#     monthly_metrics = df_master.groupby('order_month').agg({
#         'sale_price': 'sum',
#         'profit': 'sum',
#         'order_id': 'nunique'
#     }).reset_index()
#     monthly_metrics['order_month'] = monthly_metrics['order_month'].dt.to_timestamp()
#     monthly_metrics['profit_margin_%'] = (monthly_metrics['profit'] / monthly_metrics['sale_price'] * 100).round(1)
    
#     fig = go.Figure()
#     fig.add_trace(go.Bar(x=monthly_metrics['order_month'], 
#                         y=monthly_metrics['sale_price'],
#                         name='Revenue',
#                         marker_color='lightblue'))
#     fig.add_trace(go.Bar(x=monthly_metrics['order_month'], 
#                         y=monthly_metrics['profit'],
#                         name='Profit',
#                         marker_color='lightgreen'))
#     fig.add_trace(go.Scatter(x=monthly_metrics['order_month'], 
#                             y=monthly_metrics['profit_margin_%'],
#                             name='Profit Margin %',
#                             yaxis='y2',
#                             mode='lines+markers',
#                             line=dict(color='red', width=3)))
    
#     fig.update_layout(
#         title="Monthly Revenue, Profit & Margin Trends",
#         xaxis_title="Month",
#         yaxis_title="Amount (฿)",
#         yaxis2=dict(title="Profit Margin (%)", overlaying='y', side='right'),
#         hovermode='x unified',
#         barmode='group'
#     )
#     st.plotly_chart(fig, use_container_width=True)

# # ========================================== 
# # TAB 4: MARKETING ANALYTICS
# # ========================================== 
# with tab4:
#     st.header("🎯 Marketing Analytics")
    
#     st.subheader("1️⃣ Campaign Effectiveness")
    
#     campaign_df = df_master[df_master['discount_pct'] > 0].copy()
#     non_campaign_df = df_master[df_master['discount_pct'] == 0].copy()
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         campaign_revenue = campaign_df['sale_price'].sum()
#         non_campaign_revenue = non_campaign_df['sale_price'].sum()
#         campaign_share = (campaign_revenue / (campaign_revenue + non_campaign_revenue) * 100)
#         st.metric("Campaign Revenue Share", f"{campaign_share:.1f}%")
#         st.caption(f"฿{campaign_revenue:,.0f}")
    
#     with col2:
#         campaign_orders = len(campaign_df)
#         total_orders = len(df_master)
#         campaign_order_share = (campaign_orders / total_orders * 100)
#         st.metric("Campaign Order Share", f"{campaign_order_share:.1f}%")
#         st.caption(f"{campaign_orders:,} orders")
    
#     with col3:
#         campaign_aov = campaign_df['sale_price'].mean()
#         non_campaign_aov = non_campaign_df['sale_price'].mean()
#         aov_lift = ((campaign_aov / non_campaign_aov - 1) * 100) if non_campaign_aov > 0 else 0
#         st.metric("AOV Lift from Campaign", f"{aov_lift:+.1f}%")
#         st.caption(f"Campaign: ฿{campaign_aov:,.0f}")
    
#     with col4:
#         avg_discount = campaign_df['discount_pct'].mean() * 100
#         st.metric("Avg Discount Rate", f"{avg_discount:.1f}%")
#         st.caption(f"{len(campaign_df):,} discounted orders")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         comparison = pd.DataFrame({
#             'Type': ['With Campaign', 'Without Campaign'],
#             'AOV': [campaign_aov, non_campaign_aov],
#             'Orders': [len(campaign_df), len(non_campaign_df)],
#             'Revenue': [campaign_revenue, non_campaign_revenue]
#         })
        
#         fig = px.bar(comparison, 
#                      x='Type', 
#                      y='AOV',
#                      title="Average Order Value: Campaign Impact",
#                      color='Type',
#                      color_discrete_map={'With Campaign': '#e74c3c', 'Without Campaign': '#3498db'})
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         fig = px.pie(comparison, 
#                      values='Revenue', 
#                      names='Type',
#                      title="Revenue Distribution",
#                      hole=0.4,
#                      color_discrete_map={'With Campaign': '#e74c3c', 'Without Campaign': '#3498db'})
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Traffic source analysis
#     st.subheader("2️⃣ Traffic Source Performance")
    
#     traffic_perf = df_master.groupby('traffic_source').agg({
#         'user_id': 'nunique',
#         'sale_price': 'sum',
#         'profit': 'sum',
#         'order_id': 'nunique'
#     }).reset_index()
#     traffic_perf.columns = ['Traffic Source', 'Customers', 'Revenue', 'Profit', 'Orders']
#     traffic_perf['Revenue per Customer'] = (traffic_perf['Revenue'] / traffic_perf['Customers']).round(2)
#     traffic_perf['Profit Margin (%)'] = (traffic_perf['Profit'] / traffic_perf['Revenue'] * 100).round(1)
#     traffic_perf['Conversion Rate (%)'] = ((traffic_perf['Orders'] / traffic_perf['Customers']) * 100).round(1)
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         fig = px.bar(traffic_perf.sort_values('Revenue', ascending=True),
#                      x='Revenue', 
#                      y='Traffic Source',
#                      orientation='h',
#                      title="Revenue by Traffic Source",
#                      color='Profit Margin (%)',
#                      color_continuous_scale='viridis')
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         fig = px.scatter(traffic_perf, 
#                         x='Customers', 
#                         y='Revenue per Customer',
#                         size='Revenue',
#                         text='Traffic Source',
#                         title="Customer Value by Traffic Source",
#                         labels={'Customers': 'Total Customers', 'Revenue per Customer': 'Revenue per Customer (฿)'},
#                         color='Profit Margin (%)',
#                         color_continuous_scale='plasma')
#         fig.update_traces(textposition='top center')
#         st.plotly_chart(fig, use_container_width=True)
    
#     st.dataframe(traffic_perf.sort_values('Revenue', ascending=False), 
#                 use_container_width=True, height=300)
    
#     # Customer clustering
#     st.subheader("3️⃣ Customer Segmentation (K-Means Clustering)")
    
#     cluster_data = df_master.groupby('user_id').agg({
#         'created_at': lambda x: (df_master['created_at'].max() - x.max()).days,
#         'order_id': 'nunique',
#         'sale_price': 'sum'
#     }).reset_index()
#     cluster_data.columns = ['user_id', 'recency', 'frequency', 'monetary']
    
#     scaler = StandardScaler()
#     features_scaled = scaler.fit_transform(cluster_data[['recency', 'frequency', 'monetary']])
    
#     col1, col2, col3 = st.columns([1, 1, 1])
#     with col1:
#         n_clusters = st.slider("Number of Clusters", 2, 6, 4)
    
#     kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
#     cluster_data['cluster'] = kmeans.fit_predict(features_scaled)
    
#     fig = px.scatter_3d(cluster_data, 
#                         x='recency', 
#                         y='frequency', 
#                         z='monetary',
#                         color='cluster',
#                         title="Customer Clusters (3D Visualization)",
#                         labels={'cluster': 'Cluster', 
#                                'recency': 'Recency (days)', 
#                                'frequency': 'Frequency (orders)', 
#                                'monetary': 'Monetary (฿)'},
#                         color_continuous_scale='viridis')
#     fig.update_traces(marker=dict(size=5))
#     st.plotly_chart(fig, use_container_width=True)
    
#     cluster_stats = cluster_data.groupby('cluster').agg({
#         'recency': 'mean',
#         'frequency': 'mean',
#         'monetary': 'mean',
#         'user_id': 'count'
#     }).round(2)
#     cluster_stats.columns = ['Avg Recency (days)', 'Avg Frequency', 'Avg Monetary (฿)', 'Customer Count']
#     cluster_stats['Total Value (฿)'] = (cluster_stats['Avg Monetary (฿)'] * cluster_stats['Customer Count']).round(0)
    
#     st.subheader("Cluster Characteristics")
#     st.dataframe(cluster_stats, use_container_width=True)
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         cluster_dist = cluster_data['cluster'].value_counts().sort_index()
#         fig = px.bar(x=cluster_dist.index.astype(str), 
#                      y=cluster_dist.values,
#                      title="Customer Distribution by Cluster",
#                      labels={'x': 'Cluster', 'y': 'Number of Customers'},
#                      color=cluster_dist.values,
#                      color_continuous_scale='blues')
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         cluster_value = cluster_data.groupby('cluster')['monetary'].sum()
#         fig = px.pie(values=cluster_value.values, 
#                      names=[f"Cluster {i}" for i in cluster_value.index],
#                      title="Revenue Distribution by Cluster",
#                      hole=0.4)
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Marketing recommendations
#     st.subheader("4️⃣ Marketing Insights & Recommendations")
    
#     with st.expander("📊 View Detailed Insights"):
#         col1, col2 = st.columns(2)
        
#         with col1:
#             st.markdown("### 🎯 Campaign Insights")
#             if campaign_order_share > 50:
#                 st.success(f"✅ High campaign engagement ({campaign_order_share:.0f}% of orders)")
#             else:
#                 st.info(f"💡 Opportunity to increase campaign coverage (current: {campaign_order_share:.0f}%)")
            
#             if aov_lift > 10:
#                 st.success(f"✅ Strong AOV lift from campaigns (+{aov_lift:.1f}%)")
#             elif aov_lift > 0:
#                 st.warning(f"⚠️ Moderate AOV lift (+{aov_lift:.1f}%) - optimize discount strategy")
#             else:
#                 st.error(f"❌ Negative AOV impact ({aov_lift:.1f}%) - review campaign effectiveness")
        
#         with col2:
#             st.markdown("### 📱 Channel Insights")
#             best_channel = channel_detail.loc[channel_detail['Profit Margin (%)'].idxmax()]
#             st.success(f"✅ Best performing channel: **{best_channel['Channel']}** ({best_channel['Type']})")
#             st.metric("Profit Margin", f"{best_channel['Profit Margin (%)']}%")
#             st.metric("Total Revenue", f"฿{best_channel['Revenue (฿)']:,.0f}")

# st.markdown("---")
# st.caption("📊 E-commerce Analytics Dashboard | Built with Streamlit")

# app.py - Modern E-commerce Analytics Dashboard with Geographic Analysis (MODIFIED)
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, timedelta
# import numpy as np
# from sklearn.cluster import KMeans
# from sklearn.preprocessing import StandardScaler
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import classification_report, roc_auc_score
# import warnings
# import zipfile
# import io
# import os # Import os for folder path loading

# warnings.filterwarnings('ignore')

# # Page config
# st.set_page_config(page_title="E-commerce Analytics", layout="wide", page_icon="📊")

# # Initialize session state
# if 'data_loaded' not in st.session_state:
#     st.session_state.data_loaded = False
# if 'data' not in st.session_state:
#     st.session_state.data = None

# # Utility function to map channel to type
# def get_channel_type(channel):
#     """Map channel to Online/Offline"""
#     online_channels = ['line shopping', 'lazada', 'shopee', 'tiktok', 'facebook', 'instagram', 'website', 'app']
#     offline_channels = ['siam center', 'store', 'pop-up']
#     channel_lower = str(channel).lower()
    
#     # Check for Online channels
#     for oc in online_channels:
#         if oc in channel_lower:
#             return 'Online'
#     # Check for Offline channels
#     for of in offline_channels:
#         if of in channel_lower:
#             return 'Offline'
#     return 'Other'

# # File upload options
# def upload_data():
#     """Flexible data upload - ZIP file or folder path"""
#     st.sidebar.title("📊 E-commerce Analytics")
#     st.sidebar.markdown("---")
    
#     upload_method = st.sidebar.radio(
#         "📁 Data Source",
#         ["Upload ZIP File", "Load from Folder Path"]
#     )
    
#     data = None
    
#     if upload_method == "Upload ZIP File":
#         st.sidebar.subheader("Upload ZIP containing CSV files")
#         st.sidebar.caption("ZIP should contain: user.csv, product.csv, order.csv, order_item.csv")
#         uploaded_zip = st.sidebar.file_uploader("Choose ZIP file", type=['zip'])
        
#         if uploaded_zip is not None:
#             if st.sidebar.button("🔄 Load Data", type="primary"):
#                 try:
#                     with zipfile.ZipFile(uploaded_zip) as z:
#                         data = {}
#                         file_mapping = {
#                             "distribution_centers.csv": "dc",
#                             "user.csv": "user",
#                             "product.csv": "product",
#                             "inventory_item.csv": "inventory",
#                             "order.csv": "order",
#                             "order_item.csv": "order_item",
#                             "event.csv": "event"
#                         }
                        
#                         for filename in z.namelist():
#                             base_name = filename.split('/')[-1]
#                             if base_name in file_mapping:
#                                 key = file_mapping[base_name]
#                                 with z.open(filename) as f:
#                                     # Ensure the file is not empty before reading
#                                     content = f.read()
#                                     if content:
#                                         data[key] = pd.read_csv(io.BytesIO(content))
#                                         st.sidebar.success(f"✅ {base_name}")
#                                     else:
#                                         st.sidebar.warning(f"⚠️ {base_name} is empty.")
                        
#                         required = ['user', 'product', 'order', 'order_item']
#                         missing = [r for r in required if r not in data]
#                         if missing:
#                             st.sidebar.error(f"❌ Missing required files: {', '.join(missing)}")
#                             return None
                        
#                         st.session_state.data = data
#                         st.session_state.data_loaded = True
#                         st.sidebar.success("✅ All data loaded!")
#                         return data
#                 except Exception as e:
#                     st.sidebar.error(f"❌ Error loading ZIP file: {str(e)}")
#                     return None
#     else:
#         data_path = st.sidebar.text_input("Folder path", value="data")
#         if st.sidebar.button("🔄 Load Data", type="primary"):
#             try:
#                 data = {}
#                 file_mapping = {
#                     "distribution_centers.csv": "dc",
#                     "user.csv": "user",
#                     "product.csv": "product",
#                     "inventory_item.csv": "inventory",
#                     "order.csv": "order",
#                     "order_item.csv": "order_item",
#                     "event.csv": "event"
#                 }
                
#                 for filename, key in file_mapping.items():
#                     filepath = os.path.join(data_path, filename)
#                     if os.path.exists(filepath):
#                         data[key] = pd.read_csv(filepath)
#                         st.sidebar.success(f"✅ {filename}")
                
#                 required = ['user', 'product', 'order', 'order_item']
#                 missing = [r for r in required if r not in data]
#                 if missing:
#                     st.sidebar.error(f"❌ Missing required files: {', '.join(missing)}")
#                     return None
                
#                 st.session_state.data = data
#                 st.session_state.data_loaded = True
#                 st.sidebar.success("✅ All data loaded!")
#                 return data
#             except Exception as e:
#                 st.sidebar.error(f"❌ Error loading folder data: {str(e)}")
#                 return None
    
#     return st.session_state.data if st.session_state.data_loaded else None

# @st.cache_data
# def merge_and_preprocess(data):
#     """Merge all tables and create master dataframe"""
#     df = data['order_item'].merge(
#         data['order'][['order_id', 'user_id', 'channel', 'discount_pct', 'status', 'num_of_item', 'created_at']],
#         on='order_id', how='left', suffixes=('', '_order')
#     )
#     df = df.merge(
#         data['product'][['product_id', 'product_category', 'product_collection', 'retail_price', 'product_name']],
#         on='product_id', how='left', suffixes=('', '_prod')
#     )
#     df = df.merge(
#         data['user'][['user_id', 'city', 'traffic_source', 'age', 'gender']],
#         on='user_id', how='left'
#     )
    
#     # Date conversions
#     for col in ['created_at', 'shipped_at', 'delivered_at', 'returned_at']:
#         if col in df.columns:
#             # Coerce errors to NaT, then handle as date/time
#             df[col] = pd.to_datetime(df[col], errors='coerce')
    
#     # Remove rows where 'created_at' is NaT or 'sale_price' is missing/negative
#     df.dropna(subset=['created_at'], inplace=True)
#     df = df[df['sale_price'].notna() & (df['sale_price'] >= 0)]

#     # Derived fields
#     df['profit'] = df['sale_price'] - df['cost']
#     df['order_date'] = df['created_at'].dt.date
#     df['order_month'] = df['created_at'].dt.to_period('M')
#     df['order_year'] = df['created_at'].dt.year
#     df['order_quarter'] = df['created_at'].dt.quarter
#     df['order_hour'] = df['created_at'].dt.hour
#     df['order_dayofweek'] = df['created_at'].dt.dayofweek
#     df['channel_type'] = df['channel'].apply(get_channel_type)
    
#     return df, data

# # ==========================================
# # SIDEBAR - Data Upload
# # ==========================================
# data = upload_data()

# if data is None or not st.session_state.data_loaded:
#     # Initial loading screen remains the same
#     st.title("📊 E-commerce Analytics Dashboard")
#     st.info("👈 Please load your data in the sidebar to begin analysis")
    
#     col1, col2 = st.columns(2)
#     with col1:
#         st.markdown("""
#         ### 📦 Option 1: Upload ZIP File
#         - Create a ZIP file containing your CSV files
#         - Upload it directly through the web interface
#         - Quick and easy!
#         """)
#     with col2:
#         st.markdown("""
#         ### 📁 Option 2: Load from Folder
#         - Place CSV files in a folder (e.g., 'data/')
#         - Specify the folder path
#         - Great for local development
#         """)
    
#     st.markdown("""
#     ---
#     ### Required Files:
#     - ✅ **user.csv** - User information
#     - ✅ **product.csv** - Product catalog
#     - ✅ **order.csv** - Order details
#     - ✅ **order_item.csv** - Order line items
#     """)
#     st.stop()

# # Process data
# df_master, data_dict = merge_and_preprocess(data)

# st.sidebar.markdown("---")
# st.sidebar.success(f"✅ {len(df_master):,} transactions")
# st.sidebar.metric("Total Revenue", f"฿{df_master['sale_price'].sum():,.0f}")
# st.sidebar.metric("Total Profit", f"฿{df_master['profit'].sum():,.0f}")

# # ==========================================
# # THAI REGION MAPPING (MUST BE DEFINED HERE FOR GLOBAL USE)
# # ==========================================
# province_to_region = {
#     # Central/Eastern/Western Thailand
#     'Bangkok':'Central','Samut Prakan':'Central','Nonthaburi':'Central','Pathum Thani':'Central','Phra Nakhon Si Ayutthaya':'Central',
#     'Ang Thong':'Central','Lop Buri':'Central','Sing Buri':'Central','Chai Nat':'Central','Saraburi':'Central','Chon Buri':'Central',
#     'Rayong':'Central','Chanthaburi':'Central','Trat':'Central','Chachoengsao':'Central','Prachin Buri':'Central','Nakhon Nayok':'Central',
#     'Sra Kaew':'Central','Ratchaburi':'Central','Kanchanaburi':'Central','Suphan Buri':'Central','Nakhon Pathom':'Central','Samut Sakon':'Central',
#     'Samut Songkram':'Central','Phetchaburi':'Central','Prachuapkhiri Khan':'Central',
#     # Northern Thailand
#     'Chiang Mai':'Northern','Lamphun':'Northern','Lampang':'Northern','Uttaradit':'Northern','Phrae':'Northern','Nan':'Northern','Phayao':'Northern',
#     'Chiang Rai':'Northern','Mae Hong Son':'Northern','Nakhon Sawan':'Northern','Uthai Thani':'Northern','Kamphaeng Phet':'Northern',
#     'Tak':'Northern','Sukhothai':'Northern','Phisanulok':'Northern','Phichit':'Northern','Phetchabun':'Northern',
#     # Northeastern (Isaan) Thailand
#     'Nakhon Ratchasima':'Northeastern','Buri Ram':'Northeastern','Surin':'Northeastern','Si Sa Ket':'Northeastern','Ubon Ratchathani':'Northeastern',
#     'Yasothon':'Northeastern','Chaiyaphum':'Northeastern','Amnat Charoen':'Northeastern','Bungkan':'Northeastern','Nong Bua Lam Phu':'Northeastern',
#     'Khon Kaen ':'Northeastern','Udon Thani':'Northeastern','Loei':'Northeastern','Nong Khai':'Northeastern','Maha Sarakham':'Northeastern',
#     'Roi Et':'Northeastern','Kalasin':'Northeastern','Sakon Nakhon':'Northeastern','Naknon Phanom':'Northeastern','Mukdahan':'Northeastern',
#     # Southern Thailand
#     'Nakhon Si Thammarat':'Southern','Krabi':'Southern','Phangnga':'Southern','Phuket':'Southern','Surat Thani':'Southern','Ranong':'Southern',
#     'Chumphon':'Southern','Songkhla':'Southern','Satun':'Southern','Trang':'Southern','Phatthalung':'Southern','Pattani':'Southern','Yala':'Southern',
#     'Narathiwat':'Southern',
# }
# def get_region(city):
#     if pd.isna(city):
#         return 'N/A'
#     city_lower = str(city).lower()
#     for province, region in province_to_region.items():
#         if province.lower() in city_lower:
#             return region
#     return 'Other'

# # Add region to master data once
# if 'region' not in df_master.columns:
#     df_master['region'] = df_master['city'].apply(get_region)

# # ==========================================
# # MAIN TABS
# # ==========================================
# tab1, tab2, tab3, tab4 = st.tabs([
#     "👥 Customer Analytics",
#     "📦 Inventory Forecast",
#     "💰 Accounting & Profit",
#     "🎯 Marketing Analytics"
# ])

# # ==========================================
# # TAB 1: CUSTOMER ANALYTICS (NEW INTERACTIVE VERSION)
# # ==========================================
# with tab1:
#     st.header("👥 Customer Analytics (Interactive)")

#     # ----------------------------------------------------
#     # 1. GLOBAL FILTERS (Date, Channel, Status)
#     # ----------------------------------------------------
#     st.subheader("⚙️ Global Filters")

#     # Date Range Filter Logic
#     col1, col2, col3 = st.columns([2, 2, 1])

#     min_date = df_master['created_at'].min().date()
#     max_date = df_master['created_at'].max().date()

#     with col1:
#         date_range = st.date_input(
#             "Select Date Range",
#             value=(min_date, max_date),
#             min_value=min_date,
#             max_value=max_date
#         )

#     # Apply filter based on date_range selection
#     if len(date_range) == 2:
#         df_base = df_master[
#             (df_master['created_at'].dt.date >= date_range[0]) &
#             (df_master['created_at'].dt.date <= date_range[1])
#         ]
#     else:
#         df_base = df_master

#     with col2:
#         selected_channels = st.multiselect(
#             "Filter by Channel Type",
#             options=['Online', 'Offline', 'Other'],
#             default=['Online', 'Offline']
#         )
#         df_base = df_base[df_base['channel_type'].isin(selected_channels)]

#     with col3:
#         status_options = df_base['status'].unique().tolist()
#         # Ensure 'Complete' is always an option if it exists
#         default_status = ['Complete'] if 'Complete' in status_options else status_options[:1] 
#         selected_status = st.multiselect(
#             "Filter by Status",
#             options=status_options,
#             default=default_status 
#         )
#         df_filtered = df_base[df_base['status'].isin(selected_status)]

#     st.info(f"📊 Analyzing **{len(df_filtered):,}** line items from **{df_filtered['order_id'].nunique():,}** orders across **{df_filtered['user_id'].nunique():,}** unique customers.")

#     # Check for empty filtered data
#     if df_filtered.empty:
#         st.warning("⚠️ No data found based on the selected filters.")
#         # Ensure rfm_df is initialized even if df_filtered is empty
#         rfm_df = pd.DataFrame(columns=['user_id', 'Recency', 'Frequency', 'Monetary', 'R_Score', 'F_Score', 'M_Score', 'Customer_Segment'])
#     else:
#         # ----------------------------------------------------
#         # 2. KEY METRICS (Kpis)
#         # ----------------------------------------------------
#         st.subheader("💰 Key Performance Indicators (KPIs)")
#         df_order_kpi = df_filtered.drop_duplicates(subset=['order_id'])

#         col1, col2, col3, col4 = st.columns(4)
#         with col1:
#             st.metric("Total Revenue", f"฿{df_filtered['sale_price'].sum():,.0f}")
#         with col2:
#             st.metric("Total Orders", f"{df_filtered['order_id'].nunique():,}")
#         with col3:
#             st.metric("Total Customers", f"{df_filtered['user_id'].nunique():,}")
#         with col4:
#             if df_order_kpi['order_id'].nunique() > 0:
#                 avg_order_value = df_order_kpi['sale_price'].sum() / df_order_kpi['order_id'].nunique()
#                 st.metric("Avg. Order Value", f"฿{avg_order_value:,.2f}")
#             else:
#                 st.metric("Avg. Order Value", "฿0.00")

#         st.markdown("---")

#         # ----------------------------------------------------
#         # 3. INTERACTIVE CUSTOMER/ORDER TRENDS
#         # ----------------------------------------------------
#         st.subheader("📈 Customer and Order Trends")

#         # Group by month for trend analysis
#         df_trend = df_filtered.groupby('order_month').agg(
#             Total_Revenue=('sale_price', 'sum'),
#             Unique_Customers=('user_id', 'nunique'),
#             Total_Orders=('order_id', 'nunique')
#         ).reset_index()
#         df_trend['order_month_str'] = df_trend['order_month'].astype(str)

#         # Plot 1: Revenue Trend
#         fig_rev = px.line(df_trend, 
#                           x='order_month_str', 
#                           y='Total_Revenue',
#                           title='Revenue Trend Over Time',
#                           labels={'order_month_str': 'Month', 'Total_Revenue': 'Revenue (฿)'},
#                           markers=True)
#         fig_rev.update_xaxes(dtick="M1", tickformat="%b\n%Y")
#         st.plotly_chart(fig_rev, use_container_width=True)

#         # Plot 2: Customer Acquisition Trend
#         fig_cust = px.bar(df_trend, 
#                           x='order_month_str', 
#                           y='Unique_Customers',
#                           title='New/Active Customer Trend',
#                           labels={'order_month_str': 'Month', 'Unique_Customers': 'Unique Customers'},
#                           color='Unique_Customers',
#                           color_continuous_scale='Blues')
#         st.plotly_chart(fig_cust, use_container_width=True)

#         # ----------------------------------------------------
#         # 4. GEOGRAPHIC ANALYSIS (Interactive)
#         # ----------------------------------------------------
#         st.markdown("---")
#         st.subheader("🗺️ Geographic Customer Distribution")

#         # Aggregate data for visualization (using filtered data)
#         geo_density = df_filtered.groupby(['city', 'region']).agg({
#             'user_id': 'nunique',
#             'sale_price': 'sum'
#         }).reset_index()
#         geo_density.columns = ['City', 'Region', 'Customer_Count', 'Total_Spent']

#         # Top 10 Bar Chart (Placeholder for Map)
#         st.markdown("##### 📍 Top 10 จังหวัดตามจำนวนลูกค้า (หลังกรอง)")
#         geo_viz = geo_density.nlargest(10, 'Customer_Count')
#         fig_map_placeholder = px.bar(geo_viz,
#                                      x='Customer_Count',
#                                      y='City',
#                                      orientation='h',
#                                      title="ความหนาแน่นลูกค้าตามจังหวัด",
#                                      labels={'Customer_Count': 'จำนวนลูกค้า', 'City': 'จังหวัด'},
#                                      color='Customer_Count',
#                                      color_continuous_scale='Reds')
#         st.plotly_chart(fig_map_placeholder, use_container_width=True)

#         # Detailed geographic table
#         st.subheader("📊 สรุปข้อมูลตามจังหวัด")

#         # Re-aggregate data for the table metrics
#         city_summary = df_filtered.groupby('city').agg(
#             total_revenue=('sale_price', 'sum'),
#             total_orders=('order_id', 'nunique'),
#             total_items=('product_id', 'count'), # count of product_id is total items
#             num_customers=('user_id', 'nunique')
#         ).reset_index()

#         # Handle division by zero
#         city_summary['Avg Sale per Order (฿)'] = (city_summary['total_revenue'] / city_summary['total_orders']).round(2).fillna(0)
#         city_summary['Avg Items per Order'] = (city_summary['total_items'] / city_summary['total_orders']).round(2).fillna(0)

#         # Select and rename columns as requested 
#         display_cols = city_summary[['city', 'num_customers', 'total_revenue', 
#                                      'total_orders', 'Avg Sale per Order (฿)', 
#                                      'Avg Items per Order', 'total_items']]
#         display_cols.columns = ['จังหวัด', 'จำนวนลูกค้า', 'ยอดขายรวม (฿)', 'จำนวนคำสั่งซื้อ', 
#                                 'ยอดเฉลี่ยต่อคำสั่งซื้อ (฿)', 'จำนวนสินค้าเฉลี่ยต่อออเดอร์', 'จำนวนสินค้าทั้งหมดที่ขายได้']

#         st.dataframe(display_cols.sort_values('ยอดขายรวม (฿)', ascending=False), use_container_width=True, height=400)
        
#         # ----------------------------------------------------
#         # 5. CUSTOMER VALUE SEGMENTATION (RFM Analysis)
#         # ----------------------------------------------------
#         st.markdown("---")
#         st.subheader("1️⃣ Customer Value Segmentation: RFM Analysis")
#         st.markdown("ใช้ **RFM (Recency, Frequency, Monetary) Analysis** เพื่อแบ่งกลุ่มลูกค้าเชิงพฤติกรรม")
        
#         # Define the most recent date in the filtered dataset
#         current_date = df_filtered['created_at'].max()

#         # Calculate R, F, M
#         rfm_df = df_filtered.groupby('user_id').agg(
#             Recency=('created_at', lambda x: (current_date - x.max()).days),
#             Frequency=('order_id', 'nunique'),
#             Monetary=('sale_price', 'sum')
#         ).reset_index()

#         # ตรวจสอบจำนวนลูกค้าที่เหลืออยู่ 
#         if len(rfm_df) == 0:
#             st.warning("⚠️ ไม่พบลูกค้าที่ไม่ซ้ำกันที่ตรงตามเงื่อนไขการกรอง ไม่สามารถคำนวณ RFM ได้")
#             rfm_df = pd.DataFrame(columns=['user_id', 'Recency', 'Frequency', 'Monetary', 'R_Score', 'F_Score', 'M_Score', 'Customer_Segment'])
        
#         else:
# # --- การให้คะแนน RFM อย่างแข็งแกร่งที่สุด (Scoring with Individual Fallbacks) ---
# # (ใช้ฟังก์ชัน calculate_score ที่คุณได้สร้างไว้ก่อนหน้านี้)
 
#             def calculate_score(series, is_recency=False):
#                 unique_count = series.nunique()
#                 k = min(5, unique_count)
    
#                 if k < 2:
#                     return 3 # Fallback score
    
#             try:
#                 # 1. Attempt qcut without explicit labels to get the actual bins created
#                 # Use 'drop' to handle duplicates in the quantile calculation
#                 qcut_result = pd.qcut(series, k, duplicates='drop')
        
#                 # 2. Get the actual number of bins created
#                 actual_bins = len(qcut_result.categories)
                
#                 # 3. Create labels based on the actual number of bins (actual_bins)
#                 labels_base = list(range(1, actual_bins + 1))
        
#                 # Apply Recency inversion logic to the actual number of bins
#                 qcut_labels = list(reversed(labels_base)) if is_recency else labels_base
        
#                 # 4. Map the categories codes to the new labels
#                 score = qcut_result.codes + 1 # qcut_result.codes is 0-indexed, convert to 1-indexed score
        
#                 # Use the correct labels list to map the codes to the final score
#                 score_mapping = {i: label for i, label in enumerate(qcut_labels)}
#                 score = pd.Series(score).replace(score_mapping).astype(int)

#             except ValueError as e:
#             # This handles extreme edge cases where qcut still fails, though rare with 'duplicates="drop"'
#                 st.warning(f"⚠️ Warning: qcut failed for {series.name}. Falling back to score 3.")
#                 score = pd.Series(3, index=series.index)
        
#             # If the number of actual bins is less than 5, scale the score to a 5-point system
#             if actual_bins < 5: # Changed k to actual_bins for scaling robustness
#                 # Scale the score to 5 points (e.g., if 3 bins, score 1 -> 1, 2 -> 3, 3 -> 5)
#                 score_multiplier = 5 / actual_bins
#                 score = (score * score_multiplier).round(0).clip(1, 5).astype(int)
        
#             return score
#         # ----------------------------------------------------
#         # 6. VISUALIZATION (Now safe because RFM is calculated above)
#         # ----------------------------------------------------
        
#         # ตรวจสอบอีกครั้งก่อนทำ Visualization
#         if 'Customer_Segment' in rfm_df.columns and len(rfm_df) > 0:
            
#             # Visualization
#             col1, col2 = st.columns(2)

#             with col1:
#                 seg_dist = rfm_df['Customer_Segment'].value_counts()
#                 fig = px.pie(values=seg_dist.values,
#                             names=seg_dist.index,
#                             title="Customer Distribution by RFM Segment",
#                             hole=0.4,
#                             color_discrete_sequence=px.colors.sequential.Agsunset)
#                 st.plotly_chart(fig, use_container_width=True)

#             with col2:
#                 seg_value = rfm_df.groupby('Customer_Segment')['Monetary'].sum().sort_values(ascending=True)
#                 fig = px.bar(x=seg_value.values,
#                             y=seg_value.index,
#                             orientation='h',
#                             title="Total Revenue by RFM Segment",
#                             labels={'x': 'Revenue (฿)', 'y': 'Segment'},
#                             color=seg_value.index,
#                             color_discrete_sequence=px.colors.sequential.Agsunset)
#                 st.plotly_chart(fig, use_container_width=True)

#             # Segment metrics
#             st.subheader("Segment Performance Metrics (RFM)")
#             seg_metrics = rfm_df.groupby('Customer_Segment').agg(
#                 Customers=('user_id', 'count'),
#                 Avg_Recency=('Recency', 'mean'),
#                 Avg_Frequency=('Frequency', 'mean'),
#                 Avg_Monetary=('Monetary', 'mean')
#             ).round(2)
#             seg_metrics.columns = ['Customers', 'Avg Recency (Days)', 'Avg Orders', 'Avg Revenue (฿)']
#             st.dataframe(seg_metrics.sort_values('Customers', ascending=False), use_container_width=True)
            
#         # ----------------------------------------------------
#         # 7. CUSTOMER RETENTION & CHURN (Uses rfm_df)
#         # ----------------------------------------------------
#         st.markdown("---")
#         st.subheader("3️⃣ Customer Retention & Churn")
        
#         # Check if rfm_df is available and not empty before proceeding with Churn
#         if len(rfm_df) > 0 and 'is_churned' not in rfm_df.columns:
#             # Only proceed if RFM calculation was successful and rfm_df is populated
            
#             customer_metrics = rfm_df.copy() # Reuse RFM data for Churn
            
#             customer_metrics['days_since_last_order'] = customer_metrics['Recency']
            
#             # Churn threshold setting
#             churn_threshold = st.slider("กำหนดเกณฑ์การ Churn (Days)", min_value=30, max_value=180, value=60, key='churn_slider')
#             customer_metrics['is_churned'] = (customer_metrics['days_since_last_order'] > churn_threshold).astype(int)
            
#             col1, col2, col3, col4 = st.columns(4)
            
#             with col1:
#                 active_customers = (customer_metrics['is_churned'] == 0).sum()
#                 st.metric("Active Customers", f"{active_customers:,}")
            
#             with col2:
#                 churned_customers = (customer_metrics['is_churned'] == 1).sum()
#                 st.metric("Churned Customers", f"{churned_customers:,}")
            
#             with col3:
#                 total_customers = len(customer_metrics)
#                 if total_customers > 0:
#                     churn_rate = churned_customers / total_customers * 100
#                 else:
#                     churn_rate = 0
#                 st.metric("Churn Rate", f"{churn_rate:.1f}%")
            
#             with col4:
#                 avg_customer_lifetime = customer_metrics['Frequency'].mean() 
#                 st.metric("Avg Orders per Customer", f"{avg_customer_lifetime:.1f}")
            
#             # Churn by Segment
#             churn_by_seg = customer_metrics.groupby('Customer_Segment')['is_churned'].mean() * 100
#             fig = px.bar(x=churn_by_seg.index, 
#                         y=churn_by_seg.values,
#                         title="Churn Rate by Customer Segment (%)",
#                         labels={'x': 'Segment', 'y': 'Churn Rate (%)'},
#                         color=churn_by_seg.values,
#                         color_continuous_scale='reds')
#             st.plotly_chart(fig, use_container_width=True)
#         elif len(rfm_df) == 0:
#              st.info("ไม่สามารถคำนวณ Churn Metrics เนื่องจากไม่มีข้อมูลลูกค้าในเงื่อนไขที่กรอง")
        
#     # else block for df_filtered.empty ends here

# # ==========================================
# # TAB 2: INVENTORY FORECAST 
# # ==========================================
# with tab2:
#     st.header("📦 Inventory Forecasting")
    
#     # Product filters
#     st.subheader("🔍 Product Filters")
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         categories = ['All'] + sorted(df_master['product_category'].dropna().unique().tolist())
#         selected_category = st.selectbox("Category", categories)
    
#     with col2:
#         if selected_category != 'All':
#             filtered_df = df_master[df_master['product_category'] == selected_category]
#         else:
#             filtered_df = df_master
        
#         product_list = filtered_df.groupby(['product_id', 'product_name']).size().reset_index(name='count')
#         # Filter for products with some sales
#         product_list = product_list[product_list['count'] > 0].nlargest(50, 'count') 
#         product_options = {f"{row['product_name']} (ID: {row['product_id']})": row['product_id'] 
#                              for _, row in product_list.iterrows()}
        
#         if not product_options:
#              st.warning("No products found for the selected category.")
#              selected_product_name = None
#              selected_product = None
#         else:
#             selected_product_name = st.selectbox("Select Product", list(product_options.keys()))
#             selected_product = product_options[selected_product_name]
    
#     with col3:
#         st.metric("Total Products", f"{df_master['product_id'].nunique():,}")
    
#     if selected_product:
#         # Product demand analysis
#         st.subheader("1️⃣ Demand Forecast & Analysis")
        
#         # Demand aggregation at daily level
#         demand_df = df_master[df_master['status'] == 'Complete'].groupby(['order_date', 'product_id']).size().reset_index(name='quantity')
#         demand_df['order_date'] = pd.to_datetime(demand_df['order_date'])
#         prod_demand = demand_df[demand_df['product_id'] == selected_product].sort_values('order_date')
        
#         # Ensure we have enough data points for moving averages
#         if len(prod_demand) > 7:
#             prod_demand['MA_7'] = prod_demand['quantity'].rolling(window=7, min_periods=1).mean()
            
#             col1, col2 = st.columns([2, 1])
            
#             with col1:
#                 fig = go.Figure()
#                 # Actual Demand
#                 fig.add_trace(go.Scatter(x=prod_demand['order_date'], 
#                                          y=prod_demand['quantity'],
#                                          mode='lines+markers',
#                                          name='Actual Demand',
#                                          line=dict(color='lightblue', width=1),
#                                          marker=dict(size=4)))
#                 # 7-Day MA
#                 fig.add_trace(go.Scatter(x=prod_demand['order_date'], 
#                                          y=prod_demand['MA_7'],
#                                          mode='lines',
#                                          name='7-Day MA',
#                                          line=dict(color='orange', width=2)))
#                 # 30-Day MA (if enough data)
#                 if len(prod_demand) >= 30:
#                     prod_demand['MA_30'] = prod_demand['quantity'].rolling(window=30, min_periods=1).mean()
#                     fig.add_trace(go.Scatter(x=prod_demand['order_date'], 
#                                              y=prod_demand['MA_30'],
#                                              mode='lines',
#                                              name='30-Day MA',
#                                              line=dict(color='red', width=2, dash='dash')))
                
#                 fig.update_layout(title=f'Daily Demand Trend for {selected_product_name}',
#                                   xaxis_title='Date',
#                                   yaxis_title='Quantity Sold',
#                                   hovermode="x unified")
#                 st.plotly_chart(fig, use_container_width=True)

#             with col2:
#                 # Key Demand Metrics
#                 st.subheader("Demand Metrics")
#                 st.metric("Total Sales", f"{prod_demand['quantity'].sum():,}")
#                 st.metric("Avg Daily Demand (7D)", f"{prod_demand['MA_7'].iloc[-1]:.2f}")
                
#                 if len(prod_demand) >= 30:
#                     st.metric("Avg Daily Demand (30D)", f"{prod_demand['MA_30'].iloc[-1]:.2f}")
#                 else:
#                     st.info("Need 30 days of data for 30D MA.")

#                 # Simple Forecast (Next 7 days based on 7-day MA)
#                 st.markdown("---")
#                 st.subheader("Simple 7-Day Forecast")
#                 forecast_demand = prod_demand['MA_7'].iloc[-1]
#                 st.metric("Est. Sales (Next 7D)", f"{forecast_demand * 7:,.0f}")
#                 st.metric("Recommended Stock", f"{forecast_demand * 14:,.0f} (14 days buffer)")

#         else:
#             st.warning("⚠️ Need at least 7 days of sales data for this product to show trends and forecasts.")
#     else:
#         st.info("โปรดเลือกสินค้าเพื่อดูการวิเคราะห์ความต้องการและการคาดการณ์")


# # ==========================================
# # TAB 3: ACCOUNTING & PROFIT
# # ==========================================
# with tab3:
#     st.header("💰 Accounting & Profit")

#     if df_filtered.empty:
#         st.warning("⚠️ No data found based on the selected filters.")
#     else:
#         # ----------------------------------------------------
#         # 1. PROFIT & COST STRUCTURE
#         # ----------------------------------------------------
#         st.subheader("1️⃣ Profit & Cost Structure")

#         total_revenue = df_filtered['sale_price'].sum()
#         total_cost = df_filtered['cost'].sum()
#         total_profit = df_filtered['profit'].sum()

#         col1, col2, col3 = st.columns(3)
#         with col1:
#             st.metric("Total Revenue", f"฿{total_revenue:,.0f}")
#         with col2:
#             st.metric("Total Cost (COGS)", f"฿{total_cost:,.0f}")
#         with col3:
#             st.metric("Total Profit", f"฿{total_profit:,.0f}")
        
#         if total_revenue > 0:
#             profit_margin = (total_profit / total_revenue) * 100
#             st.metric("Gross Profit Margin", f"{profit_margin:.1f}%")
#         else:
#             st.metric("Gross Profit Margin", "N/A")
        
#         # Breakdown of Revenue vs Cost vs Profit
#         data_breakdown = pd.DataFrame({
#             'Metric': ['Revenue', 'Cost', 'Profit'],
#             'Value': [total_revenue, total_cost, total_profit]
#         })

#         fig_breakdown = px.bar(data_breakdown, x='Metric', y='Value', 
#                                title='Revenue vs Cost vs Profit',
#                                color='Metric',
#                                color_discrete_map={'Revenue': 'blue', 'Cost': 'red', 'Profit': 'green'})
#         st.plotly_chart(fig_breakdown, use_container_width=True)

#         st.markdown("---")

#         # ----------------------------------------------------
#         # 2. PROFIT TREND OVER TIME
#         # ----------------------------------------------------
#         st.subheader("2️⃣ Profit Trend")

#         df_profit_trend = df_filtered.groupby('order_month').agg(
#             Total_Profit=('profit', 'sum'),
#             Total_Revenue=('sale_price', 'sum')
#         ).reset_index()
#         df_profit_trend['order_month_str'] = df_profit_trend['order_month'].astype(str)
#         df_profit_trend['Profit_Margin'] = (df_profit_trend['Total_Profit'] / df_profit_trend['Total_Revenue']) * 100
        
#         # Plot Profit Trend
#         fig_profit_line = go.Figure()

#         # Profit Line
#         fig_profit_line.add_trace(go.Scatter(
#             x=df_profit_trend['order_month_str'], y=df_profit_trend['Total_Profit'],
#             mode='lines+markers', name='Total Profit (฿)', yaxis='y1',
#             line=dict(color='green')
#         ))

#         # Margin as secondary Y-axis
#         fig_profit_line.add_trace(go.Scatter(
#             x=df_profit_trend['order_month_str'], y=df_profit_trend['Profit_Margin'],
#             mode='lines', name='Profit Margin (%)', yaxis='y2',
#             line=dict(color='red', dash='dash')
#         ))

#         fig_profit_line.update_layout(
#             title='Profit and Margin Trend Over Time',
#             xaxis_title='Month',
#             yaxis=dict(title='Total Profit (฿)', titlefont=dict(color='green'), tickfont=dict(color='green')),
#             yaxis2=dict(title='Profit Margin (%)', titlefont=dict(color='red'), tickfont=dict(color='red'),
#                         overlaying='y', side='right', range=[0, 100]), # Force 0-100% scale
#             hovermode="x unified"
#         )
#         st.plotly_chart(fig_profit_line, use_container_width=True)

#         st.markdown("---")

#         # ----------------------------------------------------
#         # 3. PROFIT BY CATEGORY/REGION
#         # ----------------------------------------------------
#         st.subheader("3️⃣ Profit Breakdown")

#         col1, col2 = st.columns(2)

#         # Profit by Category
#         profit_by_cat = df_filtered.groupby('product_category')['profit'].sum().sort_values(ascending=False).nlargest(10)
#         with col1:
#             fig_cat = px.bar(x=profit_by_cat.index, y=profit_by_cat.values,
#                              title='Top 10 Profit by Category',
#                              labels={'x': 'Category', 'y': 'Total Profit (฿)'},
#                              color=profit_by_cat.values,
#                              color_continuous_scale=px.colors.sequential.Teal)
#             st.plotly_chart(fig_cat, use_container_width=True)
        
#         # Profit by Region
#         profit_by_region = df_filtered.groupby('region')['profit'].sum().sort_values(ascending=False)
#         with col2:
#             fig_region = px.pie(values=profit_by_region.values, names=profit_by_region.index,
#                                 title='Profit Distribution by Region', hole=0.3,
#                                 color_discrete_sequence=px.colors.sequential.Electric)
#             st.plotly_chart(fig_region, use_container_width=True)

# # ==========================================
# # TAB 4: MARKETING ANALYTICS
# # ==========================================
# with tab4:
#     st.header("🎯 Marketing Analytics")

#     if df_filtered.empty:
#         st.warning("⚠️ No data found based on the selected filters.")
#     else:
#         # ----------------------------------------------------
#         # 1. CHANNEL PERFORMANCE (Revenue/Orders)
#         # ----------------------------------------------------
#         st.subheader("1️⃣ Channel Performance")

#         channel_metrics = df_filtered.groupby('channel').agg(
#             Revenue=('sale_price', 'sum'),
#             Orders=('order_id', 'nunique'),
#             Customers=('user_id', 'nunique'),
#             Items=('product_id', 'count')
#         ).reset_index()
#         channel_metrics['AOV'] = (channel_metrics['Revenue'] / channel_metrics['Orders']).round(2)

#         st.dataframe(channel_metrics.sort_values('Revenue', ascending=False), 
#                      use_container_width=True, 
#                      column_order=['channel', 'Revenue', 'Orders', 'Customers', 'AOV', 'Items'],
#                      column_config={
#                          'Revenue': st.column_config.NumberColumn("Revenue (฿)", format="฿%d"),
#                          'AOV': st.column_config.NumberColumn("AOV (฿)", format="฿%.2f")
#                      })

#         col1, col2 = st.columns(2)

#         # Plot 1: Revenue by Channel
#         with col1:
#             fig_channel_rev = px.bar(channel_metrics, x='channel', y='Revenue', 
#                                      title='Revenue by Channel',
#                                      labels={'Revenue': 'Total Revenue (฿)'},
#                                      color='Revenue',
#                                      color_continuous_scale=px.colors.sequential.Plasma)
#             st.plotly_chart(fig_channel_rev, use_container_width=True)

#         # Plot 2: Orders by Channel
#         with col2:
#             fig_channel_orders = px.pie(channel_metrics, values='Orders', names='channel', 
#                                          title='Order Distribution by Channel', hole=0.4,
#                                          color_discrete_sequence=px.colors.sequential.Plasma)
#             st.plotly_chart(fig_channel_orders, use_container_width=True)

#         st.markdown("---")

#         # ----------------------------------------------------
#         # 2. TRAFFIC SOURCE ANALYSIS
#         # ----------------------------------------------------
#         st.subheader("2️⃣ Traffic Source Analysis")
        
#         # Calculate Acquisition Metrics by Traffic Source (First Order Only)
#         # Find the first order date for each user
#         df_first_order = df_master.sort_values('created_at').drop_duplicates(subset=['user_id'], keep='first')
#         df_first_order = df_first_order[df_first_order['status'].isin(selected_status)]
        
#         source_acquisition = df_first_order.groupby('traffic_source').agg(
#             New_Customers=('user_id', 'nunique'),
#             Total_Revenue=('sale_price', 'sum')
#         ).reset_index()
#         source_acquisition['Revenue_per_New_Customer'] = (source_acquisition['Total_Revenue'] / source_acquisition['New_Customers']).round(2).fillna(0)

#         st.dataframe(source_acquisition.sort_values('New_Customers', ascending=False), 
#                      use_container_width=True,
#                      column_config={
#                          'Total_Revenue': st.column_config.NumberColumn("Total Revenue (฿)", format="฿%d"),
#                          'Revenue_per_New_Customer': st.column_config.NumberColumn("Rev/New Customer (฿)", format="฿%.2f")
#                      })

#         # Plot Acquisition by Source
#         fig_source = px.bar(source_acquisition, x='traffic_source', y='New_Customers',
#                             title='Customer Acquisition by Traffic Source',
#                             labels={'New_Customers': 'New Customers Acquired'},
#                             color='New_Customers',
#                             color_continuous_scale=px.colors.sequential.Electric)
#         st.plotly_chart(fig_source, use_container_width=True)






















































# app.py - Modern E-commerce Analytics Dashboard with Geographic Analysis
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
import zipfile
import io

warnings.filterwarnings('ignore')

# Page config
st.set_page_config(page_title="E-commerce Analytics", layout="wide", page_icon="📊")

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'data' not in st.session_state:
    st.session_state.data = None

# Utility function to map channel to type
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

# File upload options
def upload_data():
    """Flexible data upload - ZIP file or folder path"""
    st.sidebar.title("📊 E-commerce Analytics")
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
                    "user.csv": "user",
                    "product.csv": "product",
                    "inventory_item.csv": "inventory",
                    "order.csv": "order",
                    "order_item.csv": "order_item",
                    "event.csv": "event"
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
    df = data['order_item'].merge(
        data['order'][['order_id', 'channel', 'discount_pct', 'status', 'num_of_item', 'created_at']],
        on='order_id', how='left', suffixes=('', '_order')
    )
    df = df.merge(
        data['product'][['product_id', 'product_category', 'product_collection', 'retail_price', 'product_name']],
        on='product_id', how='left', suffixes=('', '_prod')
    )
    df = df.merge(
        data['user'][['user_id', 'city', 'traffic_source', 'age', 'gender']],
        on='user_id', how='left'
    )
    
    # Date conversions
    for col in ['created_at', 'shipped_at', 'delivered_at', 'returned_at']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
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
    st.title("📊 E-commerce Analytics Dashboard")
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
tab1, tab2, tab3, tab4 = st.tabs([
    "👥 Customer Analytics",
    "📦 Inventory Forecast",
    "💰 Accounting & Profit",
    "🎯 Marketing Analytics"
])

# ========================================== 
# TAB 1: CUSTOMER ANALYTICS
# ========================================== 
with tab1:
    st.header("👥 Customer Analytics")
    
    # Date Range Filter
    st.subheader("📅 Analysis Period")
    col1, col2, col3 = st.columns([2, 2, 1])
    
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
        quick_filter = st.selectbox(
            "Quick Filter",
            ["All Time", "Last 30 Days", "Last 90 Days", "2024", "2025", 
             "Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024", "Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025"]
        )
        
        # Apply quick filters
        if quick_filter != "All Time":
            max_dt = df_master['created_at'].max()
            if quick_filter == "Last 30 Days":
                date_range = (max_dt - timedelta(days=30)).date(), max_dt.date()
            elif quick_filter == "Last 90 Days":
                date_range = (max_dt - timedelta(days=90)).date(), max_dt.date()
            elif quick_filter == "2024":
                date_range = pd.Timestamp('2024-01-01').date(), pd.Timestamp('2024-12-31').date()
            elif quick_filter == "2025":
                date_range = pd.Timestamp('2025-01-01').date(), max_dt.date()
            elif quick_filter == "Q1 2024":
                date_range = pd.Timestamp('2024-01-01').date(), pd.Timestamp('2024-03-31').date()
            elif quick_filter == "Q2 2024":
                date_range = pd.Timestamp('2024-04-01').date(), pd.Timestamp('2024-06-30').date()
            elif quick_filter == "Q3 2024":
                date_range = pd.Timestamp('2024-07-01').date(), pd.Timestamp('2024-09-30').date()
            elif quick_filter == "Q4 2024":
                date_range = pd.Timestamp('2024-10-01').date(), pd.Timestamp('2024-12-31').date()
            elif quick_filter == "Q1 2025":
                date_range = pd.Timestamp('2025-01-01').date(), pd.Timestamp('2025-03-31').date()
            elif quick_filter == "Q2 2025":
                date_range = pd.Timestamp('2025-04-01').date(), pd.Timestamp('2025-06-30').date()
            elif quick_filter == "Q3 2025":
                date_range = pd.Timestamp('2025-07-01').date(), pd.Timestamp('2025-09-30').date()
            elif quick_filter == "Q4 2025":
                date_range = pd.Timestamp('2025-10-01').date(), pd.Timestamp('2025-12-31').date()
    
    with col3:
        # Apply filter
        if len(date_range) == 2:
            df_filtered = df_master[
                (df_master['created_at'].dt.date >= date_range[0]) & 
                (df_master['created_at'].dt.date <= date_range[1])
            ]
        else:
            df_filtered = df_master
        
        st.metric("Transactions", f"{len(df_filtered):,}")
    
    # Display selected period info
    st.info(f"📊 Analyzing data from **{date_range[0]}** to **{date_range[1]}** ({len(df_filtered):,} transactions)")
    
    # Geographic Analysis with Interactive Map
    st.subheader("🗺️ Geographic Customer Distribution")
    
    # Thai provinces to regions mapping (expanded)
    province_to_region = {
        'Bangkok':'Central','Samut Prakan':'Central','Nonthaburi':'Central','Pathum Thani':'Central','Phra Nakhon Si Ayutthaya':'Central',
        'Ang Thong':'Central','Lop Buri':'Central','Sing Buri':'Central','Chai Nat':'Central','Saraburi':'Central','Chon Buri':'Central',
        'Rayong':'Central','Chanthaburi':'Central','Trat':'Central','Chachoengsao':'Central','Prachin Buri':'Central','Nakhon Nayok':'Central',
        'Sra Kaew':'Central','Ratchaburi':'Central','Kanchanaburi':'Central','Suphan Buri':'Central','Nakhon Pathom':'Central','Samut Sakon':'Central',
        'Samut Songkram':'Central','Phetchaburi':'Central','Prachuapkhiri Khan':'Central','Prachuap Khiri Khan':'Central',
        'Chiang Mai':'Northern','Lamphun':'Northern','Lampang':'Northern','Uttaradit':'Northern','Phrae':'Northern','Nan':'Northern','Phayao':'Northern',
        'Chiang Rai':'Northern','Mae Hong Son':'Northern','Nakhon Sawan':'Northern','Uthai Thani':'Northern','Kamphaeng Phet':'Northern',
        'Tak':'Northern','Sukhothai':'Northern','Phisanulok':'Northern','Phichit':'Northern','Phetchabun':'Northern','Phitsanulok':'Northern',
        'Nakhon Ratchasima':'Northeastern','Buri Ram':'Northeastern','Surin':'Northeastern','Si Sa Ket':'Northeastern','Ubon Ratchathani':'Northeastern',
        'Yasothon':'Northeastern','Chaiyaphum':'Northeastern','Amnat Charoen':'Northeastern','Bungkan':'Northeastern','Nong Bua Lam Phu':'Northeastern',
        'Khon Kaen':'Northeastern','Udon Thani':'Northeastern','Loei':'Northeastern','Nong Khai':'Northeastern','Maha Sarakham':'Northeastern',
        'Roi Et':'Northeastern','Kalasin':'Northeastern','Sakon Nakhon':'Northeastern','Naknon Phanom':'Northeastern','Mukdahan':'Northeastern',
        'Nakhon Phanom':'Northeastern','Buriram':'Northeastern','Bueng Kan':'Northeastern',
        'Nakhon Si Thammarat':'Southern','Krabi':'Southern','Phangnga':'Southern','Phuket':'Southern','Surat Thani':'Southern','Ranong':'Southern',
        'Chumphon':'Southern','Songkhla':'Southern','Satun':'Southern','Trang':'Southern','Phatthalung':'Southern','Pattani':'Southern','Yala':'Southern',
        'Narathiwat':'Southern','Phang Nga':'Southern',
    }
    
    def get_region(city):
        if pd.isna(city):
            return 'N/A'
        city_lower = str(city).lower()
        for province, region in province_to_region.items():
            if province.lower() in city_lower:
                return region
        return 'Other'
    
    def standardize_province(city):
        """Standardize province names for mapping"""
        if pd.isna(city):
            return 'N/A'
        city_lower = str(city).lower()
        for province in province_to_region.keys():
            if province.lower() in city_lower:
                return province
        return str(city)
    
    # Add region to filtered data
    df_filtered_geo = df_filtered.copy()
    df_filtered_geo['region'] = df_filtered_geo['city'].apply(get_region)
    df_filtered_geo['province'] = df_filtered_geo['city'].apply(standardize_province)
    
    # Customer geographic analysis
    customer_geo = df_filtered_geo.groupby(['user_id', 'city', 'province', 'region', 'age', 'gender']).agg({
        'sale_price': 'sum',
        'order_id': 'nunique',
        'product_id': 'nunique'
    }).reset_index()
    customer_geo.columns = ['user_id', 'city', 'province', 'region', 'age', 'gender', 'total_spent', 'total_orders', 'unique_products']
    
    # Advanced Filters
    st.subheader("🔍 ฟิลเตอร์ข้อมูล")
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        available_regions = ['All'] + sorted([r for r in customer_geo['region'].unique() if r != 'N/A'])
        selected_filter_region = st.multiselect(
            "เลือกภูมิภาค",
            options=available_regions,
            default=['All']
        )
    
    with col_f2:
        if 'All' not in selected_filter_region and len(selected_filter_region) > 0:
            filtered_provinces = customer_geo[customer_geo['region'].isin(selected_filter_region)]['province'].unique()
        else:
            filtered_provinces = customer_geo['province'].unique()
        
        available_provinces = ['All'] + sorted([p for p in filtered_provinces if p != 'N/A'])
        selected_filter_province = st.multiselect(
            "เลือกจังหวัด",
            options=available_provinces,
            default=['All']
        )
    
    with col_f3:
        age_groups = ['All', '<20', '20-30', '30-40', '40-50', '50-60', '60+']
        selected_age_group = st.multiselect(
            "เลือกกลุ่มอายุ",
            options=age_groups,
            default=['All']
        )
    
    # Apply filters
    filtered_customer_geo = customer_geo.copy()
    
    if 'All' not in selected_filter_region and len(selected_filter_region) > 0:
        filtered_customer_geo = filtered_customer_geo[filtered_customer_geo['region'].isin(selected_filter_region)]
    
    if 'All' not in selected_filter_province and len(selected_filter_province) > 0:
        filtered_customer_geo = filtered_customer_geo[filtered_customer_geo['province'].isin(selected_filter_province)]
    
    if 'All' not in selected_age_group and len(selected_age_group) > 0:
        filtered_customer_geo_age = filtered_customer_geo[filtered_customer_geo['age'].notna()].copy()
        filtered_customer_geo_age['age_group'] = pd.cut(filtered_customer_geo_age['age'], 
                                       bins=[0, 20, 30, 40, 50, 60, 100],
                                       labels=['<20', '20-30', '30-40', '40-50', '50-60', '60+'])
        filtered_customer_geo = filtered_customer_geo_age[filtered_customer_geo_age['age_group'].isin(selected_age_group)]
    
    st.info(f"📊 กรองแล้ว: {len(filtered_customer_geo):,} ลูกค้า | ยอดขายรวม: ฿{filtered_customer_geo['total_spent'].sum():,.0f}")
    
    # Thailand Map Visualization
    st.subheader("🗺️ แผนที่ความหนาแน่นลูกค้าในประเทศไทย")
    
    # Aggregate by province
    province_data = filtered_customer_geo.groupby('province').agg({
        'user_id': 'nunique',
        'total_spent': 'sum',
        'total_orders': 'sum'
    }).reset_index()
    province_data.columns = ['province', 'customers', 'revenue', 'orders']
    
    # Create choropleth map (using text-based visualization since actual Thai map requires geojson)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Heatmap-style visualization by province
        top_provinces = province_data.nlargest(15, 'customers')
        fig = px.bar(top_provinces, 
                     x='customers', 
                     y='province',
                     orientation='h',
                     title="Top 15 จังหวัด - ความหนาแน่นลูกค้า",
                     color='customers',
                     color_continuous_scale='Reds',
                     labels={'customers': 'จำนวนลูกค้า', 'province': 'จังหวัด'})
        fig.update_traces(texttemplate='฿%{text:.2f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(promo_comparison, 
                     x='ประเภทวัน', 
                     y='จำนวน Order',
                     title="จำนวน Order ตามประเภทวัน",
                     color='จำนวน Order',
                     color_continuous_scale='Greens',
                     text='จำนวน Order')
        fig.update_traces(texttemplate='%{text:,}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(promo_comparison, use_container_width=True)
    
    # Calculate lift vs regular days
    regular_avg = promo_comparison[promo_comparison['ประเภทวัน'] == 'Regular Day']['ยอดเฉลี่ยต่อ Transaction'].values[0] if len(promo_comparison[promo_comparison['ประเภทวัน'] == 'Regular Day']) > 0 else 0
    
    st.markdown("### 📊 Performance Lift vs Regular Days")
    lift_metrics = []
    for _, row in promo_comparison[promo_comparison['ประเภทวัน'] != 'Regular Day'].iterrows():
        lift_pct = ((row['ยอดเฉลี่ยต่อ Transaction'] / regular_avg - 1) * 100) if regular_avg > 0 else 0
        lift_metrics.append({
            'ประเภทวัน': row['ประเภทวัน'],
            'Lift %': f"{lift_pct:+.1f}%",
            'ยอดเฉลี่ย Promo Day': f"฿{row['ยอดเฉลี่ยต่อ Transaction']:,.2f}",
            'ยอดเฉลี่ย Regular Day': f"฿{regular_avg:,.2f}"
        })
    
    if lift_metrics:
        st.dataframe(pd.DataFrame(lift_metrics), use_container_width=True)
    
    # RFM-based Customer Segmentation
    st.subheader("1️⃣ Customer Value Segmentation (RFM Analysis)")
    
    st.markdown("""
    **RFM Analysis** เป็นเทคนิคการแบ่งกลุ่มลูกค้าตามพฤติกรรม 3 มิติ:
    - **Recency (R)**: ความใหม่ของการซื้อครั้งล่าสุด (วัน) - ยิ่งน้อยยิ่งดี
    - **Frequency (F)**: ความถี่ในการซื้อ (จำนวนคำสั่งซื้อ) - ยิ่งมากยิ่งดี  
    - **Monetary (M)**: มูลค่าการซื้อทั้งหมด (฿) - ยิ่งมากยิ่งดี
    
    ลูกค้าจะถูกแบ่งเป็น 4 กลุ่มตามคะแนน RFM รวม:
    - **Champions (คะแนน 9-12)**: ลูกค้า VIP - ซื้อบ่อย, ซื้อเยอะ, ซื้อล่าสุด
    - **Loyal (คะแนน 6-8)**: ลูกค้าภักดี - มีศักยภาพสูง
    - **At Risk (คะแนน 4-5)**: เสี่ยงหลุด - ต้องดูแลเพื่อรักษา
    - **Lost (คะแนน 3)**: ลูกค้าหาย - ต้องกระตุ้นกลับมา
    """)
    
    # Calculate RFM metrics
    analysis_date = df_filtered['created_at'].max()
    
    rfm_data = df_filtered.groupby('user_id').agg({
        'created_at': lambda x: (analysis_date - x.max()).days,
        'order_id': 'nunique',
        'sale_price': 'sum',
        'profit': 'sum'
    }).reset_index()
    rfm_data.columns = ['user_id', 'recency', 'frequency', 'monetary', 'total_profit']
    
    # Calculate RFM scores (1-4 scale)
    rfm_data['R_score'] = pd.qcut(rfm_data['recency'], q=4, labels=[4,3,2,1], duplicates='drop')  # Lower recency = better
    rfm_data['F_score'] = pd.qcut(rfm_data['frequency'], q=4, labels=[1,2,3,4], duplicates='drop')  # Higher frequency = better
    rfm_data['M_score'] = pd.qcut(rfm_data['monetary'], q=4, labels=[1,2,3,4], duplicates='drop')  # Higher monetary = better
    
    # Calculate total RFM score
    rfm_data['RFM_score'] = (rfm_data['R_score'].astype(int) + 
                             rfm_data['F_score'].astype(int) + 
                             rfm_data['M_score'].astype(int))
    
    # Segment customers based on RFM score
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
                     labels={'x': 'Revenue (฿)', 'y': 'Segment'},
                     color=seg_value.index,
                     color_discrete_map=colors)
        st.plotly_chart(fig, use_container_width=True)
    
    # Segment metrics with RFM scores
    st.subheader("RFM Segment Performance Metrics")
    seg_metrics = rfm_data.groupby('segment').agg({
        'user_id': 'count',
        'recency': 'mean',
        'frequency': 'mean',
        'monetary': 'mean',
        'total_profit': 'mean',
        'RFM_score': 'mean'
    }).round(2)
    seg_metrics.columns = ['Customers', 'Avg Recency (days)', 'Avg Frequency', 'Avg Revenue (฿)', 'Avg Profit (฿)', 'Avg RFM Score']
    
    # Reorder for better display
    segment_order = ['Champions', 'Loyal', 'At Risk', 'Lost']
    seg_metrics = seg_metrics.reindex([s for s in segment_order if s in seg_metrics.index])
    
    st.dataframe(seg_metrics.style.background_gradient(cmap='RdYlGn', subset=['Avg RFM Score']), 
                use_container_width=True)
    
    # Marketing recommendations by segment
    st.markdown("### 💡 แนะนำกลยุทธ์ตามกลุ่ม RFM")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Champions** 🏆
        - Reward loyalty programs
        - Early access to new products
        - Personalized experiences
        - Request referrals
        
        **At Risk** ⚠️
        - Win-back campaigns
        - Limited-time offers
        - Personalized recommendations
        - Re-engagement emails
        """)
    
    with col2:
        st.markdown("""
        **Loyal** 💎
        - Upsell & cross-sell
        - Loyalty rewards
        - Member-exclusive deals
        - Product recommendations
        
        **Lost** 😔
        - Aggressive win-back campaigns
        - Deep discounts
        - Survey for feedback
        - Retargeting ads
        """)
    
    # Customer Behavior Patterns
    st.subheader("2️⃣ Customer Behavior Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        hourly = df_filtered.groupby('order_hour').size().reset_index(name='orders')
        fig = px.area(hourly, 
                      x='order_hour', 
                      y='orders',
                      title="Orders by Hour of Day",
                      labels={'order_hour': 'Hour', 'orders': 'Orders'})
        fig.update_traces(line_color='#FF6B6B', fillcolor='rgba(255,107,107,0.3)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Show promotion day analysis instead of day of week
        promo_days_hourly = df_promo.groupby(['day_type', 'order_hour']).size().reset_index(name='orders')
        fig = px.line(promo_days_hourly, 
                     x='order_hour', 
                     y='orders',
                     color='day_type',
                     title="Orders by Hour - Promo Days vs Regular Days",
                     labels={'order_hour': 'Hour', 'orders': 'Orders'},
                     markers=True)
        st.plotly_chart(fig, use_container_width=True)
    
    # Churn Analysis
    st.subheader("3️⃣ Customer Retention & Churn")
    
    rfm_data['is_churned'] = (rfm_data['recency'] > 60).astype(int)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        active_customers = (rfm_data['is_churned'] == 0).sum()
        st.metric("Active Customers", f"{active_customers:,}")
    
    with col2:
        churned_customers = (rfm_data['is_churned'] == 1).sum()
        st.metric("Churned Customers", f"{churned_customers:,}")
    
    with col3:
        churn_rate = rfm_data['is_churned'].mean() * 100
        st.metric("Churn Rate", f"{churn_rate:.1f}%")
    
    with col4:
        avg_customer_lifetime = rfm_data['frequency'].mean()
        st.metric("Avg Orders per Customer", f"{avg_customer_lifetime:.1f}")
    
    churn_by_seg = rfm_data.groupby('segment')['is_churned'].mean() * 100
    fig = px.bar(x=churn_by_seg.index, 
                 y=churn_by_seg.values,
                 title="Churn Rate by RFM Segment (%)",
                 labels={'x': 'Segment', 'y': 'Churn Rate (%)'},
                 color=churn_by_seg.values,
                 color_continuous_scale='reds')
    st.plotly_chart(fig, use_container_width=True)

# ========================================== 
# TAB 2: INVENTORY FORECAST
# ========================================== 
with tab2:
    st.header("📦 Inventory Forecasting")
    
    # Product filters
    st.subheader("🔍 Product Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ['All'] + sorted(df_master['product_category'].dropna().unique().tolist())
        selected_category = st.selectbox("Category", categories)
    
    with col2:
        if selected_category != 'All':
            filtered_df = df_master[df_master['product_category'] == selected_category]
        else:
            filtered_df = df_master
        
        product_list = filtered_df.groupby(['product_id', 'product_name']).size().reset_index(name='count')
        product_list = product_list.nlargest(50, 'count')
        product_options = {f"{row['product_name']} (ID: {row['product_id']})": row['product_id'] 
                          for _, row in product_list.iterrows()}
        selected_product_name = st.selectbox("Select Product", list(product_options.keys()))
        selected_product = product_options[selected_product_name]
    
    with col3:
        st.metric("Total Products", f"{df_master['product_id'].nunique():,}")
    
    # Product demand analysis
    st.subheader("1️⃣ Demand Forecast & Analysis")
    
    demand_df = df_master.groupby(['order_date', 'product_id']).size().reset_index(name='quantity')
    demand_df['order_date'] = pd.to_datetime(demand_df['order_date'])
    prod_demand = demand_df[demand_df['product_id'] == selected_product].sort_values('order_date')
    
    if len(prod_demand) > 7:
        prod_demand['MA_7'] = prod_demand['quantity'].rolling(window=min(7, len(prod_demand))).mean()
        if len(prod_demand) > 30:
            prod_demand['MA_30'] = prod_demand['quantity'].rolling(window=30).mean()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=prod_demand['order_date'], 
                                    y=prod_demand['quantity'],
                                    mode='lines+markers',
                                    name='Actual Demand',
                                    line=dict(color='lightblue', width=1),
                                    marker=dict(size=4)))
            fig.add_trace(go.Scatter(x=prod_demand['order_date'], 
                                    y=prod_demand['MA_7'],
                                    mode='lines',
                                    name='7-Day MA',
                                    line=dict(color='orange', width=2)))
            if len(prod_demand) > 30:
                fig.add_trace(go.Scatter(x=prod_demand['order_date'], 
                                        y=prod_demand['MA_30'],
                                        mode='lines',
                                        name='30-Day MA',
                                        line=dict(color='red', width=2)))
            
            fig.update_layout(title=f"Demand Trend: {selected_product_name}",
                            xaxis_title="Date",
                            yaxis_title="Quantity",
                            hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            last_7_avg = prod_demand['quantity'].tail(7).mean()
            last_30_avg = prod_demand['quantity'].tail(30).mean() if len(prod_demand) >= 30 else last_7_avg
            forecast_7d = last_7_avg * 7
            forecast_30d = last_30_avg * 30
            
            st.metric("Avg Daily Demand (7d)", f"{last_7_avg:.1f} units")
            st.metric("Forecast Next 7 Days", f"{forecast_7d:.0f} units")
            st.metric("Forecast Next 30 Days", f"{forecast_30d:.0f} units")
            
            std_dev = prod_demand['quantity'].std()
            safety_stock = 1.65 * std_dev * np.sqrt(7)
            st.metric("Safety Stock (95% SL)", f"{safety_stock:.0f} units")
            
            lead_time_days = 7
            reorder_point = (last_7_avg * lead_time_days) + safety_stock
            st.metric("Reorder Point", f"{reorder_point:.0f} units")
    else:
        st.warning("⚠️ Not enough data for this product (minimum 7 days required)")
    
    # Fast vs Slow Moving Analysis
    st.subheader("2️⃣ Product Movement Analysis")
    
    product_velocity = df_master.groupby(['product_id', 'product_name']).agg({
        'order_id': 'nunique',
        'sale_price': 'sum'
    }).reset_index()
    product_velocity.columns = ['product_id', 'product_name', 'order_count', 'total_revenue']
    
    velocity_threshold_fast = product_velocity['order_count'].quantile(0.75)
    velocity_threshold_slow = product_velocity['order_count'].quantile(0.25)
    
    def classify_movement(count):
        if count >= velocity_threshold_fast:
            return 'Fast Moving'
        elif count <= velocity_threshold_slow:
            return 'Slow Moving'
        else:
            return 'Medium Moving'
    
    product_velocity['movement'] = product_velocity['order_count'].apply(classify_movement)
    
    col1, col2 = st.columns(2)
    
    with col1:
        movement_dist = product_velocity['movement'].value_counts()
        fig = px.pie(values=movement_dist.values, 
                     names=movement_dist.index,
                     title="Product Movement Distribution",
                     hole=0.4,
                     color_discrete_map={
                         'Fast Moving': '#2ecc71',
                         'Medium Moving': '#f39c12',
                         'Slow Moving': '#e74c3c'
                     })
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        top_fast = product_velocity[product_velocity['movement'] == 'Fast Moving'].nlargest(10, 'order_count')
        fig = px.bar(top_fast, 
                     x='order_count', 
                     y='product_name',
                     orientation='h',
                     title="Top 10 Fast Moving Products",
                     labels={'order_count': 'Order Count', 'product_name': 'Product'})
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Product Movement Details")
    movement_filter = st.multiselect("Filter by Movement", 
                                     ['Fast Moving', 'Medium Moving', 'Slow Moving'],
                                     default=['Fast Moving'])
    filtered_products = product_velocity[product_velocity['movement'].isin(movement_filter)]
    st.dataframe(filtered_products.sort_values('order_count', ascending=False), 
                use_container_width=True, height=400)

# ========================================== 
# TAB 3: ACCOUNTING & PROFIT
# ========================================== 
with tab3:
    st.header("💰 Accounting & Profitability Analysis")
    
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
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        st.metric("Profit Margin", f"{profit_margin:.1f}%")
    
    # Channel Performance
    st.subheader("2️⃣ Channel Performance (Online vs Offline)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        channel_type_perf = df_master.groupby('channel_type').agg({
            'sale_price': 'sum',
            'profit': 'sum',
            'order_id': 'nunique'
        }).reset_index()
        channel_type_perf['profit_margin_%'] = (channel_type_perf['profit'] / channel_type_perf['sale_price'] * 100).round(1)
        
        fig = px.pie(channel_type_perf, 
                     values='sale_price', 
                     names='channel_type',
                     title="Revenue: Online vs Offline",
                     hole=0.4,
                     color_discrete_map={'Online': '#3498db', 'Offline': '#e67e22', 'Other': '#95a5a6'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(channel_type_perf, 
                     x='channel_type', 
                     y='profit_margin_%',
                     title="Profit Margin: Online vs Offline (%)",
                     color='channel_type',
                     color_discrete_map={'Online': '#3498db', 'Offline': '#e67e22', 'Other': '#95a5a6'})
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Detailed Channel Breakdown")
    channel_detail = df_master.groupby(['channel', 'channel_type']).agg({
        'sale_price': 'sum',
        'profit': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    channel_detail.columns = ['Channel', 'Type', 'Revenue (฿)', 'Profit (฿)', 'Orders']
    channel_detail['Profit Margin (%)'] = (channel_detail['Profit (฿)'] / channel_detail['Revenue (฿)'] * 100).round(1)
    channel_detail['AOV (฿)'] = (channel_detail['Revenue (฿)'] / channel_detail['Orders']).round(2)
    st.dataframe(channel_detail.sort_values('Revenue (฿)', ascending=False), 
                use_container_width=True, height=300)
    
    # Category profitability
    st.subheader("3️⃣ Product Category Profitability")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cat_profit = df_master.groupby('product_category').agg({
            'sale_price': 'sum',
            'profit': 'sum'
        }).reset_index()
        cat_profit['margin_%'] = (cat_profit['profit'] / cat_profit['sale_price'] * 100).round(1)
        cat_profit = cat_profit.sort_values('profit', ascending=True)
        
        fig = px.bar(cat_profit, 
                     x='profit', 
                     y='product_category',
                     orientation='h',
                     title="Profit by Product Category",
                     labels={'profit': 'Profit (฿)', 'product_category': 'Category'},
                     color='margin_%',
                     color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(cat_profit, 
                        x='sale_price', 
                        y='profit',
                        size='margin_%',
                        text='product_category',
                        title="Revenue vs Profit by Category",
                        labels={'sale_price': 'Revenue (฿)', 'profit': 'Profit (฿)'},
                        color='margin_%',
                        color_continuous_scale='RdYlGn')
        fig.update_traces(textposition='top center')
        st.plotly_chart(fig, use_container_width=True)
    
    # Monthly revenue trend
    st.subheader("4️⃣ Revenue & Profit Trends")
    
    monthly_metrics = df_master.groupby('order_month').agg({
        'sale_price': 'sum',
        'profit': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    monthly_metrics['order_month'] = monthly_metrics['order_month'].dt.to_timestamp()
    monthly_metrics['profit_margin_%'] = (monthly_metrics['profit'] / monthly_metrics['sale_price'] * 100).round(1)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly_metrics['order_month'], 
                        y=monthly_metrics['sale_price'],
                        name='Revenue',
                        marker_color='lightblue'))
    fig.add_trace(go.Bar(x=monthly_metrics['order_month'], 
                        y=monthly_metrics['profit'],
                        name='Profit',
                        marker_color='lightgreen'))
    fig.add_trace(go.Scatter(x=monthly_metrics['order_month'], 
                            y=monthly_metrics['profit_margin_%'],
                            name='Profit Margin %',
                            yaxis='y2',
                            mode='lines+markers',
                            line=dict(color='red', width=3)))
    
    fig.update_layout(
        title="Monthly Revenue, Profit & Margin Trends",
        xaxis_title="Month",
        yaxis_title="Amount (฿)",
        yaxis2=dict(title="Profit Margin (%)", overlaying='y', side='right'),
        hovermode='x unified',
        barmode='group'
    )
    st.plotly_chart(fig, use_container_width=True)

# # ========================================== 
# # TAB 4: MARKETING ANALYTICS
# # ========================================== 
# with tab4:
#     st.header("🎯 Marketing Analytics")
    
#     st.subheader("1️⃣ Campaign Effectiveness")
    
#     campaign_df = df_master[df_master['discount_pct'] > 0].copy()
#     non_campaign_df = df_master[df_master['discount_pct'] == 0].copy()
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         campaign_revenue = campaign_df['sale_price'].sum()
#         non_campaign_revenue = non_campaign_df['sale_price'].sum()
#         campaign_share = (campaign_revenue / (campaign_revenue + non_campaign_revenue) * 100)
#         st.metric("Campaign Revenue Share", f"{campaign_share:.1f}%")
#         st.caption(f"฿{campaign_revenue:,.0f}")
    
#     with col2:
#         campaign_orders = len(campaign_df)
#         total_orders = len(df_master)
#         campaign_order_share = (campaign_orders / total_orders * 100)
#         st.metric("Campaign Order Share", f"{campaign_order_share:.1f}%")
#         st.caption(f"{campaign_orders:,} orders")
    
#     with col3:
#         campaign_aov = campaign_df['sale_price'].mean()
#         non_campaign_aov = non_campaign_df['sale_price'].mean()
#         aov_lift = ((campaign_aov / non_campaign_aov - 1) * 100) if non_campaign_aov > 0 else 0
#         st.metric("AOV Lift from Campaign", f"{aov_lift:+.1f}%")
#         st.caption(f"Campaign: ฿{campaign_aov:,.0f}")
    
#     with col4:
#         avg_discount = campaign_df['discount_pct'].mean() * 100
#         st.metric("Avg Discount Rate", f"{avg_discount:.1f}%")
#         st.caption(f"{len(campaign_df):,} discounted orders")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         comparison = pd.DataFrame({
#             'Type': ['With Campaign', 'Without Campaign'],
#             'AOV': [campaign_aov, non_campaign_aov],
#             'Orders': [len(campaign_df), len(non_campaign_df)],
#             'Revenue': [campaign_revenue, non_campaign_revenue]
#         })
        
#         fig = px.bar(comparison, 
#                      x='Type', 
#                      y='AOV',
#                      title="Average Order Value: Campaign Impact",
#                      color='Type',
#                      color_discrete_map={'With Campaign': '#e74c3c', 'Without Campaign': '#3498db'})
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         fig = px.pie(comparison, 
#                      values='Revenue', 
#                      names='Type',
#                      title="Revenue Distribution",
#                      hole=0.4,
#                      color_discrete_map={'With Campaign': '#e74c3c', 'Without Campaign': '#3498db'})
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Traffic source analysis
#     st.subheader("2️⃣ Traffic Source Performance")
    
#     traffic_perf = df_master.groupby('traffic_source').agg({
#         'user_id': 'nunique',
#         'sale_price': 'sum',
#         'profit': 'sum',
#         'order_id': 'nunique'
#     }).reset_index()
#     traffic_perf.columns = ['Traffic Source', 'Customers', 'Revenue', 'Profit', 'Orders']
#     traffic_perf['Revenue per Customer'] = (traffic_perf['Revenue'] / traffic_perf['Customers']).round(2)
#     traffic_perf['Profit Margin (%)'] = (traffic_perf['Profit'] / traffic_perf['Revenue'] * 100).round(1)
#     traffic_perf['Conversion Rate (%)'] = ((traffic_pe_layout(height=500)
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         # Revenue heatmap
#         top_revenue_provinces = province_data.nlargest(15, 'revenue')
#         fig = px.bar(top_revenue_provinces, 
#                      x='revenue', 
#                      y='province',
#                      orientation='h',
#                      title="Top 15 จังหวัด - ยอดขาย",
#                      color='revenue',
#                      color_continuous_scale='Greens',
#                      labels={'revenue': 'ยอดขาย (฿)', 'province': 'จังหวัด'})
#         fig.update_layout(height=500)
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col3:
#         # Region distribution with actual filtered data
#         region_dist = filtered_customer_geo.groupby('region').agg({
#             'user_id': 'nunique',
#             'total_spent': 'sum'
#         }).reset_index()
#         region_dist.columns = ['Region', 'Customers', 'Revenue']
        
#         fig = px.pie(region_dist, 
#                      values='Customers', 
#                      names='Region',
#                      title="การกระจายลูกค้าตามภูมิภาค",
#                      hole=0.4,
#                      color_discrete_sequence=px.colors.sequential.RdBu)
#         st.plotly_chart(fig, use_container_width=True)
        
#         # Age distribution
#         if not filtered_customer_geo.empty:
#             age_dist = filtered_customer_geo[filtered_customer_geo['age'].notna()].copy()
#             age_dist['age_group'] = pd.cut(age_dist['age'], 
#                                            bins=[0, 20, 30, 40, 50, 60, 100],
#                                            labels=['<20', '20-30', '30-40', '40-50', '50-60', '60+'])
#             age_group_dist = age_dist.groupby('age_group')['user_id'].nunique().reset_index()
#             age_group_dist.columns = ['กลุ่มอายุ', 'จำนวนลูกค้า']
            
#             fig = px.bar(age_group_dist, 
#                          x='กลุ่มอายุ', 
#                          y='จำนวนลูกค้า',
#                          title="การกระจายลูกค้าตามช่วงอายุ",
#                          color='จำนวนลูกค้า',
#                          color_continuous_scale='Teal')
#             st.plotly_chart(fig, use_container_width=True)
    
#     # Detailed geographic table
#     st.subheader("📊 สรุปข้อมูลตามจังหวัด")
    
#     # Prepare transaction-level data for calculations
#     trans_geo = df_filtered_geo.groupby(['province', 'order_id']).agg({
#         'sale_price': 'sum',
#         'product_id': 'nunique'
#     }).reset_index()
#     trans_geo.columns = ['province', 'order_id', 'order_value', 'items_per_order']
    
#     geo_summary = filtered_customer_geo.groupby('province').agg({
#         'user_id': 'nunique',
#         'total_spent': 'sum',
#         'total_orders': 'sum',
#         'unique_products': 'sum'
#     }).reset_index()
    
#     # Calculate avg per order
#     order_avg = trans_geo.groupby('province').agg({
#         'order_value': 'mean',
#         'items_per_order': 'mean'
#     }).reset_index()
    
#     geo_summary = geo_summary.merge(order_avg, on='province', how='left')
    
#     geo_summary.columns = ['จังหวัด', 'จำนวนลูกค้า', 'ยอดขายรวม (฿)', 'จำนวนคำสั่งซื้อ', 
#                            'สินค้าทั้งหมด', 'ยอดเฉลี่ยต่อ Order (฿)', 'สินค้าเฉลี่ยต่อ Order']
#     geo_summary['ยอดเฉลี่ยต่อลูกค้า (฿)'] = (geo_summary['ยอดขายรวม (฿)'] / geo_summary['จำนวนลูกค้า']).round(2)
#     geo_summary = geo_summary.sort_values('ยอดขายรวม (฿)', ascending=False)
    
#     # Round values
#     geo_summary['ยอดเฉลี่ยต่อ Order (฿)'] = geo_summary['ยอดเฉลี่ยต่อ Order (฿)'].round(2)
#     geo_summary['สินค้าเฉลี่ยต่อ Order'] = geo_summary['สินค้าเฉลี่ยต่อ Order'].round(1)
    
#     st.dataframe(geo_summary, use_container_width=True, height=400)
    
#     # Monthly trends by region
#     st.subheader("📈 Trend การขายตามภูมิภาคและเวลา")
    
#     monthly_region = df_filtered_geo.groupby([df_filtered_geo['created_at'].dt.to_period('M'), 'region']).agg({
#         'sale_price': 'sum',
#         'order_id': 'nunique'
#     }).reset_index()
#     monthly_region['created_at'] = monthly_region['created_at'].dt.to_timestamp()
#     monthly_region.columns = ['เดือน', 'ภูมิภาค', 'ยอดขาย', 'จำนวนคำสั่งซื้อ']
    
#     fig = px.line(monthly_region, 
#                   x='เดือน', 
#                   y='ยอดขาย',
#                   color='ภูมิภาค',
#                   title="ยอดขายรายเดือนแยกตามภูมิภาค",
#                   markers=True)
#     st.plotly_chart(fig, use_container_width=True)
    
#     # Promotional Days Analysis
#     st.subheader("🎉 วิเคราะห์ยอดขายในวัน Promotion")
    
#     df_promo = df_filtered.copy()
#     df_promo['day'] = df_promo['created_at'].dt.day
#     df_promo['month'] = df_promo['created_at'].dt.month
#     df_promo['year'] = df_promo['created_at'].dt.year
    
#     # Define special promotion days
#     def classify_day_type(row):
#         day = row['day']
#         month = row['month']
        
#         # Special days: 1.1, 2.2, 3.3, etc.
#         if day == month and day <= 12:
#             return f'{day}.{month} Special'
#         # Every 25th
#         elif day == 25:
#             return '25th Monthly'
#         else:
#             return 'Regular Day'
    
#     df_promo['day_type'] = df_promo.apply(classify_day_type, axis=1)
    
#     # Compare performance
#     promo_comparison = df_promo.groupby('day_type').agg({
#         'sale_price': ['sum', 'mean', 'count'],
#         'order_id': 'nunique'
#     }).reset_index()
#     promo_comparison.columns = ['ประเภทวัน', 'ยอดขายรวม', 'ยอดเฉลี่ยต่อ Transaction', 'จำนวน Transaction', 'จำนวน Order']
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         fig = px.bar(promo_comparison, 
#                      x='ประเภทวัน', 
#                      y='ยอดเฉลี่ยต่อ Transaction',
#                      title="ยอดขายเฉลี่ยต่อ Transaction ตามประเภทวัน",
#                      color='ยอดเฉลี่ยต่อ Transaction',
#                      color_continuous_scale='Blues',
#                      text='ยอดเฉลี่ยต่อ Transaction')
#         fig.update







# ========================================== 
# TAB 4: MARKETING ANALYTICS
# ========================================== 
with tab4:
    st.header("🎯 Marketing Analytics")
    
    st.subheader("1️⃣ Campaign Effectiveness")
    
    campaign_df = df_master[df_master['discount_pct'] > 0].copy()
    non_campaign_df = df_master[df_master['discount_pct'] == 0].copy()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        campaign_revenue = campaign_df['sale_price'].sum()
        non_campaign_revenue = non_campaign_df['sale_price'].sum()
        campaign_share = (campaign_revenue / (campaign_revenue + non_campaign_revenue) * 100)
        st.metric("Campaign Revenue Share", f"{campaign_share:.1f}%")
        st.caption(f"฿{campaign_revenue:,.0f}")
    
    with col2:
        campaign_orders = len(campaign_df)
        total_orders = len(df_master)
        campaign_order_share = (campaign_orders / total_orders * 100)
        st.metric("Campaign Order Share", f"{campaign_order_share:.1f}%")
        st.caption(f"{campaign_orders:,} orders")
    
    with col3:
        campaign_aov = campaign_df['sale_price'].mean()
        non_campaign_aov = non_campaign_df['sale_price'].mean()
        aov_lift = ((campaign_aov / non_campaign_aov - 1) * 100) if non_campaign_aov > 0 else 0
        st.metric("AOV Lift from Campaign", f"{aov_lift:+.1f}%")
        st.caption(f"Campaign: ฿{campaign_aov:,.0f}")
    
    with col4:
        avg_discount = campaign_df['discount_pct'].mean() * 100
        st.metric("Avg Discount Rate", f"{avg_discount:.1f}%")
        st.caption(f"{len(campaign_df):,} discounted orders")
    
    col1, col2 = st.columns(2)
    
    with col1:
        comparison = pd.DataFrame({
            'Type': ['With Campaign', 'Without Campaign'],
            'AOV': [campaign_aov, non_campaign_aov],
            'Orders': [len(campaign_df), len(non_campaign_df)],
            'Revenue': [campaign_revenue, non_campaign_revenue]
        })
        
        fig = px.bar(comparison, 
                     x='Type', 
                     y='AOV',
                     title="Average Order Value: Campaign Impact",
                     color='Type',
                     color_discrete_map={'With Campaign': '#e74c3c', 'Without Campaign': '#3498db'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(comparison, 
                     values='Revenue', 
                     names='Type',
                     title="Revenue Distribution",
                     hole=0.4,
                     color_discrete_map={'With Campaign': '#e74c3c', 'Without Campaign': '#3498db'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Traffic source analysis
    st.subheader("2️⃣ Traffic Source Performance")
    
    traffic_perf = df_master.groupby('traffic_source').agg({
        'user_id': 'nunique',
        'sale_price': 'sum',
        'profit': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    traffic_perf.columns = ['Traffic Source', 'Customers', 'Revenue', 'Profit', 'Orders']
    traffic_perf['Revenue per Customer'] = (traffic_perf['Revenue'] / traffic_perf['Customers']).round(2)
    traffic_perf['Profit Margin (%)'] = (traffic_perf['Profit'] / traffic_perf['Revenue'] * 100).round(1)
    traffic_perf['Conversion Rate (%)'] = ((traffic_perf['Orders'] / traffic_perf['Customers']) * 100).round(1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(traffic_perf.sort_values('Revenue', ascending=True),
                     x='Revenue', 
                     y='Traffic Source',
                     orientation='h',
                     title="Revenue by Traffic Source",
                     color='Profit Margin (%)',
                     color_continuous_scale='viridis')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(traffic_perf, 
                        x='Customers', 
                        y='Revenue per Customer',
                        size='Revenue',
                        text='Traffic Source',
                        title="Customer Value by Traffic Source",
                        labels={'Customers': 'Total Customers', 'Revenue per Customer': 'Revenue per Customer (฿)'},
                        color='Profit Margin (%)',
                        color_continuous_scale='plasma')
        fig.update_traces(textposition='top center')
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(traffic_perf.sort_values('Revenue', ascending=False), 
                use_container_width=True, height=300)
    
    # Customer clustering
    st.subheader("3️⃣ Customer Segmentation (K-Means Clustering)")
    
    cluster_data = df_master.groupby('user_id').agg({
        'created_at': lambda x: (df_master['created_at'].max() - x.max()).days,
        'order_id': 'nunique',
        'sale_price': 'sum'
    }).reset_index()
    cluster_data.columns = ['user_id', 'recency', 'frequency', 'monetary']
    
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(cluster_data[['recency', 'frequency', 'monetary']])
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        n_clusters = st.slider("Number of Clusters", 2, 6, 4)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_data['cluster'] = kmeans.fit_predict(features_scaled)
    
    fig = px.scatter_3d(cluster_data, 
                        x='recency', 
                        y='frequency', 
                        z='monetary',
                        color='cluster',
                        title="Customer Clusters (3D Visualization)",
                        labels={'cluster': 'Cluster', 
                               'recency': 'Recency (days)', 
                               'frequency': 'Frequency (orders)', 
                               'monetary': 'Monetary (฿)'},
                        color_continuous_scale='viridis')
    fig.update_traces(marker=dict(size=5))
    st.plotly_chart(fig, use_container_width=True)
    
    cluster_stats = cluster_data.groupby('cluster').agg({
        'recency': 'mean',
        'frequency': 'mean',
        'monetary': 'mean',
        'user_id': 'count'
    }).round(2)
    cluster_stats.columns = ['Avg Recency (days)', 'Avg Frequency', 'Avg Monetary (฿)', 'Customer Count']
    cluster_stats['Total Value (฿)'] = (cluster_stats['Avg Monetary (฿)'] * cluster_stats['Customer Count']).round(0)
    
    st.subheader("Cluster Characteristics")
    st.dataframe(cluster_stats, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        cluster_dist = cluster_data['cluster'].value_counts().sort_index()
        fig = px.bar(x=cluster_dist.index.astype(str), 
                     y=cluster_dist.values,
                     title="Customer Distribution by Cluster",
                     labels={'x': 'Cluster', 'y': 'Number of Customers'},
                     color=cluster_dist.values,
                     color_continuous_scale='blues')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        cluster_value = cluster_data.groupby('cluster')['monetary'].sum()
        fig = px.pie(values=cluster_value.values, 
                     names=[f"Cluster {i}" for i in cluster_value.index],
                     title="Revenue Distribution by Cluster",
                     hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    # Marketing recommendations
    st.subheader("4️⃣ Marketing Insights & Recommendations")
    
    with st.expander("📊 View Detailed Insights"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Campaign Insights")
            if campaign_order_share > 50:
                st.success(f"✅ High campaign engagement ({campaign_order_share:.0f}% of orders)")
            else:
                st.info(f"💡 Opportunity to increase campaign coverage (current: {campaign_order_share:.0f}%)")
            
            if aov_lift > 10:
                st.success(f"✅ Strong AOV lift from campaigns (+{aov_lift:.1f}%)")
            elif aov_lift > 0:
                st.warning(f"⚠️ Moderate AOV lift (+{aov_lift:.1f}%) - optimize discount strategy")
            else:
                st.error(f"❌ Negative AOV impact ({aov_lift:.1f}%) - review campaign effectiveness")
        
        with col2:
            st.markdown("### 📱 Channel Insights")
            best_channel = channel_detail.loc[channel_detail['Profit Margin (%)'].idxmax()]
            st.success(f"✅ Best performing channel: **{best_channel['Channel']}** ({best_channel['Type']})")
            st.metric("Profit Margin", f"{best_channel['Profit Margin (%)']}%")
            st.metric("Total Revenue", f"฿{best_channel['Revenue (฿)']:,.0f}")

st.markdown("---")
st.caption("📊 E-commerce Analytics Dashboard | Built with Streamlit")

