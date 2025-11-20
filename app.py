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
    
    # Geographic Analysis
    st.subheader("🗺️ Geographic Customer Distribution")
    
    # Thai provinces to regions mapping
    province_to_region = {
        'Bangkok':'Central','Samut Prakan':'Central','Nonthaburi':'Central','Pathum Thani':'Central','Phra Nakhon Si Ayutthaya':'Central',
        'Ang Thong':'Central','Lop Buri':'Central','Sing Buri':'Central','Chai Nat':'Central','Saraburi':'Central','Chon Buri':'Central',
        'Rayong':'Central','Chanthaburi':'Central','Trat':'Central','Chachoengsao':'Central','Prachin Buri':'Central','Nakhon Nayok':'Central',
        'Sra Kaew':'Central','Ratchaburi':'Central','Kanchanaburi':'Central','Suphan Buri':'Central','Nakhon Pathom':'Central','Samut Sakon':'Central',
        'Samut Songkram':'Central','Phetchaburi':'Central','Prachuapkhiri Khan':'Central',
        'Chiang Mai':'Northern','Lamphun':'Northern','Lampang':'Northern','Uttaradit':'Northern','Phrae':'Northern','Nan':'Northern','Phayao':'Northern',
        'Chiang Rai':'Northern','Mae Hong Son':'Northern','Nakhon Sawan':'Northern','Uthai Thani':'Northern','Kamphaeng Phet':'Northern',
        'Tak':'Northern','Sukhothai':'Northern','Phisanulok':'Northern','Phichit':'Northern','Phetchabun':'Northern',
        'Nakhon Ratchasima':'Northeastern','Buri Ram':'Northeastern','Surin':'Northeastern','Si Sa Ket':'Northeastern','Ubon Ratchathani':'Northeastern',
        'Yasothon':'Northeastern','Chaiyaphum':'Northeastern','Amnat Charoen':'Northeastern','Bungkan':'Northeastern','Nong Bua Lam Phu':'Northeastern',
        'Khon Kaen ':'Northeastern','Udon Thani':'Northeastern','Loei':'Northeastern','Nong Khai':'Northeastern','Maha Sarakham':'Northeastern',
        'Roi Et':'Northeastern','Kalasin':'Northeastern','Sakon Nakhon':'Northeastern','Naknon Phanom':'Northeastern','Mukdahan':'Northeastern',
        'Nakhon Si Thammarat':'Southern','Krabi':'Southern','Phangnga':'Southern','Phuket':'Southern','Surat Thani':'Southern','Ranong':'Southern',
        'Chumphon':'Southern','Songkhla':'Southern','Satun':'Southern','Trang':'Southern','Phatthalung':'Southern','Pattani':'Southern','Yala':'Southern',
        'Narathiwat':'Southern',
        # 'Bangkok': 'กลาง', 'Samut Prakan': 'กลาง', 'Nonthaburi': 'กลาง',
        # 'Pathum Thani': 'กลาง', 'Phra Nakhon Si Ayutthaya': 'กลาง', 'Ayutthaya': 'กลาง',
        # 'Saraburi': 'กลาง', 'Lop Buri': 'กลาง', 'Sing Buri': 'กลาง', 'Chai Nat': 'กลาง',
        # 'Suphan Buri': 'กลาง', 'Ang Thong': 'กลาง', 'Nakhon Pathom': 'กลาง',
        # 'Chiang Mai': 'เหนือ', 'Chiang Rai': 'เหนือ', 'Lampang': 'เหนือ', 'Lamphun': 'เหนือ',
        # 'Mae Hong Son': 'เหนือ', 'Nan': 'เหนือ', 'Phayao': 'เหนือ', 'Phrae': 'เหนือ',
        # 'Uttaradit': 'เหนือ', 'Phitsanulok': 'เหนือ', 'Sukhothai': 'เหนือ', 'Tak': 'เหนือ',
        # 'Kamphaeng Phet': 'เหนือ', 'Phichit': 'เหนือ', 'Phetchabun': 'เหนือ',
        # 'Nakhon Ratchasima': 'อีสาน', 'Buriram': 'อีสาน', 'Surin': 'อีสาน',
        # 'Si Sa Ket': 'อีสาน', 'Ubon Ratchathani': 'อีสาน', 'Yasothon': 'อีสาน',
        # 'Chaiyaphum': 'อีสาน', 'Amnat Charoen': 'อีสาน', 'Nong Bua Lamphu': 'อีสาน',
        # 'Khon Kaen': 'อีสาน', 'Udon Thani': 'อีสาน', 'Loei': 'อีสาน',
        # 'Nong Khai': 'อีสาน', 'Maha Sarakham': 'อีสาน', 'Roi Et': 'อีสาน',
        # 'Kalasin': 'อีสาน', 'Sakon Nakhon': 'อีสาน', 'Nakhon Phanom': 'อีสาน',
        # 'Mukdahan': 'อีสาน', 'Bueng Kan': 'อีสาน',
        # 'Phuket': 'ใต้', 'Krabi': 'ใต้', 'Phang Nga': 'ใต้', 'Surat Thani': 'ใต้',
        # 'Ranong': 'ใต้', 'Chumphon': 'ใต้', 'Nakhon Si Thammarat': 'ใต้', 'Trang': 'ใต้',
        # 'Phatthalung': 'ใต้', 'Songkhla': 'ใต้', 'Satun': 'ใต้', 'Pattani': 'ใต้',
        # 'Yala': 'ใต้', 'Narathiwat': 'ใต้',
        # 'Ratchaburi': 'ตะวันตก', 'Kanchanaburi': 'ตะวันตก', 'Samut Songkhram': 'ตะวันตก',
        # 'Samut Sakhon': 'ตะวันตก', 'Phetchaburi': 'ตะวันตก', 'Prachuap Khiri Khan': 'ตะวันตก',
        # 'Chonburi': 'ตะวันออก', 'Rayong': 'ตะวันออก', 'Chanthaburi': 'ตะวันออก',
        # 'Trat': 'ตะวันออก', 'Chachoengsao': 'ตะวันออก', 'Prachin Buri': 'ตะวันออก',
        # 'Nakhon Nayok': 'ตะวันออก', 'Sa Kaeo': 'ตะวันออก'
    }
    
    def get_region(city):
        if pd.isna(city):
            return 'N/A'
        city_lower = str(city).lower()
        for province, region in province_to_region.items():
            if province.lower() in city_lower:
                return region
        return 'Other'
    
    # Add region to filtered data
    df_filtered_geo = df_filtered.copy()
    df_filtered_geo['region'] = df_filtered_geo['city'].apply(get_region)
    
    # Customer geographic analysis
    customer_geo = df_filtered_geo.groupby(['user_id', 'city', 'region', 'age', 'gender']).agg({
        'sale_price': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    customer_geo.columns = ['user_id', 'city', 'region', 'age', 'gender', 'total_spent', 'total_orders']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Region distribution
        region_dist = customer_geo.groupby('region').agg({
            'user_id': 'nunique',
            'total_spent': 'sum'
        }).reset_index()
        region_dist.columns = ['Region', 'no. of Customers', 'Sale']
        
        fig = px.pie(region_dist, 
                     values='no. of Customers', 
                     names='Region',
                     title="การกระจายลูกค้าตามภูมิภาค",
                     hole=0.4,
                     color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top cities by customers
        top_cities = customer_geo.groupby('city')['user_id'].nunique().nlargest(10).reset_index()
        top_cities.columns = ['จังหวัด', 'จำนวนลูกค้า']
        
        fig = px.bar(top_cities, 
                     x='จำนวนลูกค้า', 
                     y='จังหวัด',
                     orientation='h',
                     title="Top 10 จังหวัด (จำนวนลูกค้า)",
                     color='จำนวนลูกค้า',
                     color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        # Age distribution
        age_dist = customer_geo[customer_geo['age'].notna()].copy()
        age_dist['age_group'] = pd.cut(age_dist['age'], 
                                       bins=[0, 20, 30, 40, 50, 60, 100],
                                       labels=['<20', '20-30', '30-40', '40-50', '50-60', '60+'])
        age_group_dist = age_dist.groupby('age_group')['user_id'].nunique().reset_index()
        age_group_dist.columns = ['กลุ่มอายุ', 'จำนวนลูกค้า']
        
        fig = px.bar(age_group_dist, 
                     x='กลุ่มอายุ', 
                     y='จำนวนลูกค้า',
                     title="การกระจายลูกค้าตามช่วงอายุ",
                     color='จำนวนลูกค้า',
                     color_continuous_scale='Teal')
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed geographic table
    st.subheader("📊 สรุปข้อมูลตามภูมิภาคและจังหวัด")
    
    geo_summary = customer_geo.groupby(['region', 'city']).agg({
        'user_id': 'nunique',
        'total_spent': 'sum',
        'total_orders': 'sum'
    }).reset_index()
    geo_summary.columns = ['ภูมิภาค', 'จังหวัด', 'จำนวนลูกค้า', 'ยอดขายรวม (฿)', 'จำนวนคำสั่งซื้อ']
    geo_summary['ยอดเฉลี่ยต่อลูกค้า (฿)'] = (geo_summary['ยอดขายรวม (฿)'] / geo_summary['จำนวนลูกค้า']).round(2)
    geo_summary = geo_summary.sort_values('ยอดขายรวม (฿)', ascending=False)
    
    # Filter by region
    selected_regions = st.multiselect(
        "เลือกภูมิภาค",
        options=geo_summary['ภูมิภาค'].unique(),
        default=geo_summary['ภูมิภาค'].unique()
    )
    
    filtered_geo = geo_summary[geo_summary['ภูมิภาค'].isin(selected_regions)]
    st.dataframe(filtered_geo, use_container_width=True, height=400)
    
    # Monthly trends by region
    st.subheader("📈 Trend การขายตามภูมิภาคและเวลา")
    
    monthly_region = df_filtered_geo.groupby([df_filtered_geo['created_at'].dt.to_period('M'), 'region']).agg({
        'sale_price': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    monthly_region['created_at'] = monthly_region['created_at'].dt.to_timestamp()
    monthly_region.columns = ['เดือน', 'ภูมิภาค', 'ยอดขาย', 'จำนวนคำสั่งซื้อ']
    
    fig = px.line(monthly_region, 
                  x='เดือน', 
                  y='ยอดขาย',
                  color='ภูมิภาค',
                  title="ยอดขายรายเดือนแยกตามภูมิภาค",
                  markers=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # Customer Segmentation by Value
    st.subheader("1️⃣ Customer Value Segmentation")
    
    # Calculate customer metrics
    customer_metrics = df_filtered.groupby('user_id').agg({
        'created_at': lambda x: (df_filtered['created_at'].max() - x.max()).days,
        'order_id': 'nunique',
        'sale_price': 'sum',
        'profit': 'sum'
    }).reset_index()
    customer_metrics.columns = ['user_id', 'days_since_last_order', 'total_orders', 'total_revenue', 'total_profit']
    
    # Segment by value
    customer_metrics['segment'] = pd.qcut(
        customer_metrics['total_revenue'],
        q=4,
        labels=['Bronze', 'Silver', 'Gold', 'Platinum'],
        duplicates='drop'
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        seg_dist = customer_metrics['segment'].value_counts()
        fig = px.pie(values=seg_dist.values, 
                     names=seg_dist.index,
                     title="Customer Distribution by Value",
                     hole=0.4,
                     color_discrete_sequence=px.colors.sequential.Agsunset)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        seg_value = customer_metrics.groupby('segment')['total_revenue'].sum().sort_values(ascending=True)
        fig = px.bar(x=seg_value.values, 
                     y=seg_value.index,
                     orientation='h',
                     title="Total Revenue by Segment",
                     labels={'x': 'Revenue (฿)', 'y': 'Segment'},
                     color=seg_value.index,
                     color_discrete_sequence=px.colors.sequential.Agsunset)
        st.plotly_chart(fig, use_container_width=True)
    
    # Segment metrics
    st.subheader("Segment Performance Metrics")
    seg_metrics = customer_metrics.groupby('segment').agg({
        'user_id': 'count',
        'total_orders': 'mean',
        'total_revenue': 'mean',
        'total_profit': 'mean',
        'days_since_last_order': 'mean'
    }).round(2)
    seg_metrics.columns = ['Customers', 'Avg Orders', 'Avg Revenue (฿)', 'Avg Profit (฿)', 'Avg Days Since Order']
    st.dataframe(seg_metrics, use_container_width=True)
    
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
        dow_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
        daily = df_filtered.groupby('order_dayofweek').size().reset_index(name='orders')
        daily['day'] = daily['order_dayofweek'].map(dow_map)
        fig = px.bar(daily, 
                     x='day', 
                     y='orders',
                     title="Orders by Day of Week",
                     color='orders',
                     color_continuous_scale='blues')
        st.plotly_chart(fig, use_container_width=True)
    
    # Churn Analysis
    st.subheader("3️⃣ Customer Retention & Churn")
    
    customer_metrics['is_churned'] = (customer_metrics['days_since_last_order'] > 60).astype(int)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        active_customers = (customer_metrics['is_churned'] == 0).sum()
        st.metric("Active Customers", f"{active_customers:,}")
    
    with col2:
        churned_customers = (customer_metrics['is_churned'] == 1).sum()
        st.metric("Churned Customers", f"{churned_customers:,}")
    
    with col3:
        churn_rate = customer_metrics['is_churned'].mean() * 100
        st.metric("Churn Rate", f"{churn_rate:.1f}%")
    
    with col4:
        avg_customer_lifetime = customer_metrics['total_orders'].mean()
        st.metric("Avg Orders per Customer", f"{avg_customer_lifetime:.1f}")
    
    churn_by_seg = customer_metrics.groupby('segment')['is_churned'].mean() * 100
    fig = px.bar(x=churn_by_seg.index, 
                 y=churn_by_seg.values,
                 title="Churn Rate by Customer Segment (%)",
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
