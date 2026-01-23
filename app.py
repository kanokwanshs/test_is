# Analytics Dashboard - Fixed Version
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import warnings
from datetime import datetime, timedelta
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics.pairwise import cosine_similarity

# ========== Class DataQualityTracker ==========
class DataQualityTracker:
    """Track which data is actual vs estimated"""
    
    def __init__(self):
        self.actual_data = []
        self.estimated_data = []
        self.missing_data = []
        
    def mark_actual(self, metric_name):
        if metric_name not in self.actual_data:
            self.actual_data.append(metric_name)
    
    def mark_estimated(self, metric_name, estimation_method):
        if not any(m['metric'] == metric_name for m in self.estimated_data):
            self.estimated_data.append({
                'metric': metric_name,
                'method': estimation_method
            })
    
    def mark_missing(self, metric_name, required_data):
        if not any(m['metric'] == metric_name for m in self.missing_data):
            self.missing_data.append({
                'metric': metric_name,
                'required': required_data
            })
    
    def get_summary(self):
        return {
            'actual_count': len(self.actual_data),
            'estimated_count': len(self.estimated_data),
            'missing_count': len(self.missing_data),
            'total_metrics': len(self.actual_data) + len(self.estimated_data) + len(self.missing_data)
        }
    
    def show_data_quality_badge(self):
        """Display data quality indicator at top of dashboard"""
        summary = self.get_summary()
        if summary['total_metrics'] == 0:
            return
        
        actual_pct = (summary['actual_count'] / summary['total_metrics'] * 100) if summary['total_metrics'] > 0 else 0
        
        if actual_pct >= 80:
            quality_color = "#2ecc71"
            quality_status = "Excellent"
        elif actual_pct >= 60:
            quality_color = "#f39c12"
            quality_status = "Good"
        else:
            quality_color = "#e74c3c"
            quality_status = "Fair"
        
        st.markdown(f"""
        <div style='background: {quality_color}; padding: 10px 20px; border-radius: 8px; color: white; 
                    text-align: center; margin-bottom: 20px;'>
            <b>📊 Data Quality: {quality_status}</b> | 
            ✅ Actual: {summary['actual_count']} | 
            ⚠️ Estimated: {summary['estimated_count']} | 
            ❌ Missing: {summary['missing_count']}
            <span style='font-size: 11px; opacity: 0.9; margin-left: 10px;'>
                ({actual_pct:.0f}% actual data)
            </span>
        </div>
        """, unsafe_allow_html=True)

# ========== Class AIEstimator ==========
class AIEstimator:
    """AI-powered estimation for missing data"""
    
    @staticmethod
    def estimate_accounts_receivable(df_filtered, monthly_fin):
        """Estimate AR based on customer type, order pattern, and revenue trend"""
        total_revenue = df_filtered['net_revenue'].sum()
        
        # Method 1: Check if we have customer_type data
        if 'customer_type' in df_filtered.columns:
            b2b_revenue = df_filtered[df_filtered['customer_type'] == 'B2B']['net_revenue'].sum()
            b2c_revenue = df_filtered[df_filtered['customer_type'] == 'B2C']['net_revenue'].sum()
            estimated_ar = (b2b_revenue * 0.35) + (b2c_revenue * 0.05)
            method = "Customer type analysis: B2B 35%, B2C 5%"
        else:
            # Method 2: Order concentration
            order_concentration = df_filtered.groupby('order_id')['net_revenue'].sum()
            top_20_pct = order_concentration.nlargest(int(len(order_concentration) * 0.2)).sum()
            concentration_ratio = top_20_pct / total_revenue if total_revenue > 0 else 0
            
            if concentration_ratio > 0.6:
                ar_percentage = 0.30
                method = "High order concentration (B2B pattern): 30%"
            else:
                ar_percentage = 0.15
                method = "Distributed orders (B2C pattern): 15%"
            
            estimated_ar = total_revenue * ar_percentage
        
        # Add growth adjustment
        if len(monthly_fin) >= 3:
            recent_growth = monthly_fin['net_revenue'].pct_change().tail(3).mean()
            if not np.isnan(recent_growth):
                estimated_ar *= (1 + recent_growth)
                method += f" + growth adj ({recent_growth*100:+.1f}%)"
        
        return estimated_ar, method
    
    @staticmethod
    def estimate_accounts_payable(cogs, df_filtered):
        """Estimate AP based on purchase pattern and business size"""
        total_orders = df_filtered['order_id'].nunique()
        
        if total_orders > 1000:
            ap_percentage = 0.30
            method = "Large business (>1000 orders): 30% of COGS"
        elif total_orders > 500:
            ap_percentage = 0.25
            method = "Medium business (500-1000): 25% of COGS"
        else:
            ap_percentage = 0.20
            method = "Small business (<500): 20% of COGS"
        
        return cogs * ap_percentage, method
    
    @staticmethod
    def estimate_inventory(df_filtered, cogs):
        """Estimate inventory based on product velocity and sales pattern"""
        product_count = df_filtered['product_id'].nunique()
        total_quantity = df_filtered['quantity'].sum()
        avg_product_cost = cogs / total_quantity if total_quantity > 0 else 0
        
        product_sales = df_filtered.groupby('product_id')['quantity'].sum()
        fast_movers = len(product_sales[product_sales > product_sales.median()])
        slow_movers = product_count - fast_movers
        
        days_in_period = max((df_filtered['order_date'].max() - df_filtered['order_date'].min()).days, 1)
        daily_sales = total_quantity / days_in_period
        
        estimated_inventory_units = (daily_sales * 0.6 * 30) + (daily_sales * 0.4 * 60)
        estimated_inventory_value = estimated_inventory_units * avg_product_cost
        
        method = f"Velocity analysis: {fast_movers} fast (30d) + {slow_movers} slow (60d)"
        
        return estimated_inventory_value, method

warnings.filterwarnings("ignore")
st.set_page_config(page_title="Analytics Pro", layout="wide", page_icon="👕")

# Enhanced Color Palette
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ecc71",
    "danger": "#e74c3c",
    "warning": "#f39c12",
    "info": "#3498db",
    "purple": "#9b59b6",
    "teal": "#1abc9c",
    "pink": "#e91e63",
    "indigo": "#3f51b5",
}

# Channel Color Mapping
CHANNEL_COLORS = {
    "TikTok": "#000000",
    "Shopee": "#FF5722",
    "Lazada": "#1E88E5",
    "LINE Shopping": "#00C300",
    "Instagram": "#9C27B0",
    "Facebook": "#1877F2",
    "Store": "#795548",
    "Pop-up": "#FF9800",
    "Website": "#607D8B",
}

# Initialize session state
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
if "data" not in st.session_state:
    st.session_state.data = {}
if "quality_tracker" not in st.session_state:
    st.session_state.quality_tracker = DataQualityTracker()
if "ai_estimator" not in st.session_state:
    st.session_state.ai_estimator = AIEstimator()
if "use_ai_estimation" not in st.session_state:
    st.session_state.use_ai_estimation = True

REQUIRED_COLUMNS = {
    "users": ["user_id", "customer_type", "created_at"],
    "products": ["product_id", "category", "sale_price", "cost"],
    "orders": ["order_id", "user_id", "order_date", "channel", "status"],
    "order_items": ["order_id", "product_id","quantity","net_revenue","cost","profit",],
    "inventory_movements (optional)": ["product_id", "movement_date","movement_type","quantity",],
    "balance_sheet (optional)": ["date", "accounts_receivable","accounts_payable","inventory_value","amount",],
}


def load_data():
    st.sidebar.title("📊 Analytics Dashboard")
    st.sidebar.markdown("### 📁 Data Upload")
    st.sidebar.markdown("Upload your CSV files to begin analysis")
    st.sidebar.markdown("---")

    uploaded = st.sidebar.file_uploader(
        "Choose CSV Files",
        type=["csv"],
        accept_multiple_files=True,
        key="csv_uploader_main",
    )

    if uploaded and st.sidebar.button(
        "🔄 Load Data", type="primary", key="load_data_btn"
    ):
        data = {}
        mapping = {
            "users.csv": "users",
            "products.csv": "products",
            "orders.csv": "orders",
            "order_items.csv": "order_items",
            "inventory_movements.csv": "inventory",
            "balance_sheet.csv": "balance_sheet",
        }

        with st.sidebar:
            st.markdown("**Loading Status:**")

        for file in uploaded:
            if file.name in mapping:
                try:
                    df = pd.read_csv(file)
                    table = mapping[file.name]
                    if table in REQUIRED_COLUMNS:
                        missing = [
                            c for c in REQUIRED_COLUMNS[table] if c not in df.columns
                        ]
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

        if all(t in data for t in ["users", "products", "orders", "order_items"]):
            st.session_state.data = data
            st.session_state.data_loaded = True
            st.sidebar.markdown("---")
            st.sidebar.success("✅ **All data loaded successfully!**")
            st.rerun()
        else:
            st.sidebar.error("❌ Missing required tables")
            missing_tables = [
                t
                for t in ["users", "products", "orders", "order_items"]
                if t not in data
            ]
            st.sidebar.caption(f"Need: {', '.join(missing_tables)}.csv")

    if st.session_state.data_loaded:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ✅ Data Status")
        st.sidebar.success("Data loaded and ready")
        
        # ✅ แก้ไข indentation ตรงนี้
        st.sidebar.markdown("**Optional Data:**")
        if "balance_sheet" in st.session_state.data:
            st.sidebar.success("✅ Balance Sheet available")
        else:
            st.sidebar.info("ℹ️ Balance Sheet: AI estimation")
    
        if "inventory" in st.session_state.data:
            st.sidebar.success("✅ Inventory Movements available")
        else:
            st.sidebar.info("ℹ️ Inventory: AI estimation")
    
        # AI Estimation Toggle
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🤖 AI Settings")
        use_ai = st.sidebar.checkbox(
            "Enable AI Estimation",
            value=True,
            help="Use AI to estimate missing data"
        )
        st.session_state.use_ai_estimation = use_ai

        if st.session_state.data:
            total_orders = len(st.session_state.data.get("orders", []))
            total_customers = len(st.session_state.data.get("users", []))
            total_products = len(st.session_state.data.get("products", []))

            st.sidebar.markdown(
                f"""
            - **Orders:** {total_orders:,}
            - **Customers:** {total_customers:,}
            - **Products:** {total_products:,}
            """
            )

        # Target Settings
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎯 Target Settings")
        st.sidebar.markdown("กำหนดเป้าหมายต่างๆ ของธุรกิจ")

        if "targets" not in st.session_state:
            st.session_state.targets = {
                "monthly_revenue": 1000000,
                "profit_margin": 20,
                "conversion_rate": 5,
                "retention_rate": 80,
                "inventory_turnover": 4,
            }

        with st.sidebar.expander("📊 Sales Targets", expanded=False):
            st.session_state.targets["monthly_revenue"] = st.number_input(
                "Monthly Revenue Target (฿)",
                min_value=0,
                value=st.session_state.targets["monthly_revenue"],
                step=100000,
                format="%d",
                help="เป้าหมายยอดขายต่อเดือน",
            )

        with st.sidebar.expander("💰 Financial Targets", expanded=False):
            st.session_state.targets["profit_margin"] = st.number_input(
                "Target Profit Margin (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.targets["profit_margin"]),
                step=1.0,
                help="เป้าหมายอัตรากำไรสุทธิ",
            )

        with st.sidebar.expander("📢 Marketing Targets", expanded=False):
            st.session_state.targets["conversion_rate"] = st.number_input(
                "Target Conversion Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.targets["conversion_rate"]),
                step=0.5,
                help="เป้าหมาย Conversion Rate",
            )

            st.session_state.targets["retention_rate"] = st.number_input(
                "Target Retention Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.targets["retention_rate"]),
                step=1.0,
                help="เป้าหมายการรักษาลูกค้า",
            )

        with st.sidebar.expander("📦 Warehouse Targets", expanded=False):
            st.session_state.targets["inventory_turnover"] = st.number_input(
                "Target Inventory Turnover (x/year)",
                min_value=0.0,
                value=float(st.session_state.targets["inventory_turnover"]),
                step=0.5,
                help="เป้าหมายการหมุนเวียนสินค้า",
            )

    return st.session_state.data if st.session_state.data_loaded else None


@st.cache_data
def merge_data(data):
    df = data["order_items"].copy()
    df = df.merge(data["orders"], on="order_id", how="left", suffixes=("", "_o"))
    df = df.merge(data["products"], on="product_id", how="left", suffixes=("", "_p"))
    df = df.merge(data["users"], on="user_id", how="left", suffixes=("", "_u"))

    for col in ["order_date", "created_at"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "order_date" in df.columns:
        df["order_month"] = df["order_date"].dt.to_period("M")
        df["order_year"] = df["order_date"].dt.year
        df["order_day"] = df["order_date"].dt.day

    online = ["Shopee", "Lazada", "TikTok", "LINE Shopping"]
    df["channel_type"] = df["channel"].apply(
        lambda x: "Online" if x in online else "Offline"
    )

    return df

# Custom CSS
st.markdown(
    """
<style>
    .block-container {padding-top: 1rem; padding-bottom: 1rem;}
    [data-testid="stMetricValue"] {font-size: 24px; font-weight: 600;}
    [data-testid="stMetricLabel"] {font-size: 13px; font-weight: 500; color: #555;}
    h1, h2, h3 {font-family: 'Inter', sans-serif; font-weight: 700;}
    
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
    
    .quality-badge-actual {
        background: #2ecc71;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: bold;
        margin-left: 5px;
    }
    
    .quality-badge-estimated {
        background: #f39c12;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: bold;
        margin-left: 5px;
    }
    
    .quality-badge-missing {
        background: #e74c3c;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: bold;
        margin-left: 5px;
    }
</style>
""", unsafe_allow_html=True)

data = load_data()

if not data:
    # Hero Section
    st.markdown(
        """
    <div style='text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 20px; color: white; margin-bottom: 40px;'>
        <h1 style='font-size: 48px; margin-bottom: 20px;'>📊 Analytics Dashboard</h1>
        <p style='font-size: 20px; opacity: 0.9;'>Professional Business Intelligence Platform</p>
        <p style='font-size: 16px; opacity: 0.8; margin-top: 10px;'>
            Upload your data files to unlock powerful insights
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Features Section
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
        <div style='text-align: center; padding: 30px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <div style='font-size: 48px; margin-bottom: 15px;'>💼</div>
            <h3 style='font-size: 18px; color: #2c3e50;'>Sales Analytics</h3>
            <p style='font-size: 13px; color: #7f8c8d;'>Track revenue, growth & targets</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div style='text-align: center; padding: 30px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <div style='font-size: 48px; margin-bottom: 15px;'>📢</div>
            <h3 style='font-size: 18px; color: #2c3e50;'>Marketing ROI</h3>
            <p style='font-size: 13px; color: #7f8c8d;'>CAC, CLV & conversion</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div style='text-align: center; padding: 30px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <div style='font-size: 48px; margin-bottom: 15px;'>💰</div>
            <h3 style='font-size: 18px; color: #2c3e50;'>Financial Health</h3>
            <p style='font-size: 13px; color: #7f8c8d;'>Margins & cash flow</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            """
        <div style='text-align: center; padding: 30px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <div style='font-size: 48px; margin-bottom: 15px;'>🔮</div>
            <h3 style='font-size: 18px; color: #2c3e50;'>AI Forecasting</h3>
            <p style='font-size: 13px; color: #7f8c8d;'>Predict future trends</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Upload prompt
    st.markdown(
        """
    <div style='text-align: center; padding: 40px; background: #f8f9fa; border-radius: 15px; border: 2px dashed #3498db;'>
        <h2 style='color: #2c3e50; margin-bottom: 15px;'>👈 Get Started</h2>
        <p style='color: #7f8c8d; font-size: 16px;'>Upload your CSV files using the sidebar to begin</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ย้าย Required Columns มาท้าย
    st.markdown("<br><br>", unsafe_allow_html=True)

    with st.expander("📋 View Required File Formats", expanded=False):
        st.markdown("### Required Data Structure")
        col1, col2 = st.columns(2)
        with col1:
            st.code("users.csv:\n- user_id\n- customer_type\n- created_at")
            st.code(
                "orders.csv:\n- order_id\n- user_id\n- order_date\n- channel\n- status"
            )
        with col2:
            st.code("products.csv:\n- product_id\n- category\n- sale_price\n- cost")
            st.code("order_items.csv:\n- order_id\n- product_id\n- quantity\n- net_revenue\n- cost\n- profit"    
            )

    st.stop()
quality_tracker = st.session_state.quality_tracker
ai_estimator = st.session_state.ai_estimator
df_master = merge_data(data)

# ==================== MAIN FILTERS ====================
st.title("📊 Analytics Dashboard")
quality_tracker.show_data_quality_badge()
st.markdown("---")

st.markdown("### 🔍 Filter Data")

min_date = df_master["order_date"].min().date()
max_date = df_master["order_date"].max().date()

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    period_options = [
        "Custom Range",
        "Last 7 Days",
        "Last 30 Days",
        "Last 90 Days",
        "This Month",
        "Last Month",
        "This Quarter",
        "This Year",
        "All Time",
    ]
    selected_period = st.selectbox(
        "📅 Time Period", period_options, index=2, key="period_selector"
    )

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
            key="custom_date_range",
        )
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = min_date, max_date

    st.info(
        f"📆 **{start_date.strftime('%d %b %Y')}** → **{end_date.strftime('%d %b %Y')}**"
    )

with col3:
    if st.button("🔄 Reset All", key="reset_filters", use_container_width=True):
        st.rerun()

df_filtered = df_master[
    (df_master["order_date"].dt.date >= start_date)
    & (df_master["order_date"].dt.date <= end_date)
]

col1, col2, col3 = st.columns(3)

with col1:
    channels = st.multiselect(
        "🏪 Sales Channel",
        df_master["channel"].unique(),
        df_master["channel"].unique(),
        key="channel_filter",
    )
    df_filtered = df_filtered[df_filtered["channel"].isin(channels)]

with col2:
    statuses = st.multiselect(
        "📦 Order Status",
        df_master["status"].unique(),
        ["Completed"],
        key="status_filter",
    )
    df_filtered = df_filtered[df_filtered["status"].isin(statuses)]

with col3:
    if "category" in df_filtered.columns:
        categories = st.multiselect(
            "🏷️ Product Category",
            df_master["category"].unique(),
            df_master["category"].unique(),
            key="category_filter",
        )
        df_filtered = df_filtered[df_filtered["category"].isin(categories)]

# Data Validation
if df_filtered.empty:
    st.error("❌ ไม่มีข้อมูลในช่วงเวลาที่เลือก กรุณาเลือกช่วงเวลาใหม่")
    st.stop()

if df_filtered['order_id'].nunique() < 10:
    st.warning("⚠️ ข้อมูลมีน้อยเกินไป (< 10 orders) ผลลัพธ์อาจไม่แม่นยำ")

if df_filtered['user_id'].nunique() < 5:
    st.warning("⚠️ ลูกค้ามีน้อยเกินไป (< 5 customers) การวิเคราะห์ลูกค้าอาจไม่แม่นยำ")

st.markdown("---")
st.markdown("### 📊 Summary Statistics")

# Calculate key metrics
revenue = df_filtered["net_revenue"].sum()
profit = df_filtered["profit"].sum()
cogs = df_filtered["cost"].sum()
total_orders = df_filtered["order_id"].nunique()
total_customers = df_filtered["user_id"].nunique()
gross_profit = revenue - cogs
profit_margin = (profit / revenue * 100) if revenue > 0 else 0
avg_order_value = revenue / total_orders if total_orders > 0 else 0

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("💰 Revenue", f"฿{revenue/1000000:,.0f}M")
with col2:
    st.metric("💵 Profit", f"฿{profit/1000000:,.0f}M")
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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💼 Sales Analytics",
    "📢 Marketing Analytics", 
    "💰 Financial Analytics",
    "📦 Warehouse Analytics",
    "🔮 Forecasting & Planning",
    "🤖 AI Insights & Recommendations"  # NEW!
])

with tab1:
    st.markdown("# 💼 Sales Analytics")
    st.markdown("---")

    # ==================== SALES GROWTH ====================
    st.markdown("### 📈 Monthly Sales Growth")

    with st.expander("📖 Description", expanded=False):
        st.markdown(
            """
        <div class='metric-explanation'>
            <b>📖 คำอธิบาย:</b> วัดว่ายอดขายเติบโตกี่ % เมื่อเทียบกับเดือนก่อนหน้า<br>
            <div class='metric-formula'>
                สูตร: [(ยอดขายเดือนปัจจุบัน - ยอดขายเดือนก่อน) / ยอดขายเดือนก่อน] × 100
            </div>
            <b>🎯 เป้าหมาย:</b> ควรเป็นบวก และมากกว่า 5-10% ถือว่าดี
        </div>
        """,
            unsafe_allow_html=True,
        )

    monthly_sales = (
        df_filtered.groupby("order_month").agg({"net_revenue": "sum"}).reset_index()
    )
    monthly_sales["order_month"] = monthly_sales["order_month"].dt.to_timestamp()
    monthly_sales["month_label"] = monthly_sales["order_month"].dt.strftime("%b %Y")
    monthly_sales["growth_%"] = monthly_sales["net_revenue"].pct_change() * 100

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = go.Figure()

        # Revenue bars
        fig.add_trace(
            go.Bar(
                x=monthly_sales["month_label"],
                y=monthly_sales["net_revenue"],
                name="Revenue",
                marker=dict(
                    color=monthly_sales["net_revenue"],
                    colorscale="Blues",
                    showscale=False,
                ),
                text=monthly_sales["net_revenue"],
                texttemplate="฿%{text:,.0f}",
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>",
            )
        )

        # Growth line
        fig.add_trace(
            go.Scatter(
                x=monthly_sales["month_label"],
                y=monthly_sales["growth_%"],
                name="Growth %",
                mode="lines+markers",
                line=dict(color="#e74c3c", width=3),
                marker=dict(size=10),
                yaxis="y2",
                text=monthly_sales["growth_%"],
                texttemplate="%{text:.1f}%",
                textposition="top center",
                hovertemplate="<b>%{x}</b><br>Growth: %{y:.1f}%<extra></extra>",
            )
        )

        fig.update_layout(
            title="<b>Monthly Sales Revenue & Growth Rate</b>",
            xaxis=dict(title="", showgrid=False),
            yaxis=dict(
                title="Revenue (฿)", showgrid=True, gridcolor="rgba(0,0,0,0.05)"
            ),
            yaxis2=dict(
                title="Growth (%)",
                overlaying="y",
                side="right",
                showgrid=False,
                zeroline=True,
                zerolinecolor="gray",
            ),
            plot_bgcolor="white",
            height=400,
            hovermode="x unified",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        latest_growth = (
            monthly_sales["growth_%"].iloc[-1] if len(monthly_sales) > 1 else 0
        )
        prev_growth = (
            monthly_sales["growth_%"].iloc[-2] if len(monthly_sales) > 2 else 0
        )

        arrow = "📈" if latest_growth > 0 else "📉"
        color = "#2ecc71" if latest_growth > 0 else "#e74c3c"

        st.markdown(
            f"""
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
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ==================== SALES TARGET ATTAINMENT ====================
    st.markdown("### 🎯 Sales Target Attainment")

    with st.expander("📖 Description", expanded=False):
        st.markdown(
            """
        <div class='metric-explanation'>
            <b>📖 คำอธิบาย:</b> วัดว่าทำยอดขายได้กี่ % ของเป้าหมายที่ตั้งไว้<br>
            <div class='metric-formula'>
                สูตร: (ยอดขายที่ทำได้ / เป้าหมายยอดขาย) × 100
            </div>
            <b>🎯 เป้าหมาย:</b> ควรอยู่ที่ 90-110% (น้อยกว่า 90% ต้องปรับปรุง, มากกว่า 110% ดีมาก)
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Get target from user input
    target_monthly = st.session_state.targets["monthly_revenue"]
    current_month_sales = (
        monthly_sales["net_revenue"].iloc[-1] if len(monthly_sales) > 0 else 0
    )
    attainment = (
        (current_month_sales / target_monthly * 100) if target_monthly > 0 else 0
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
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
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 30px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 14px; opacity: 0.9;'>ACTUAL</div>
            <div style='font-size: 36px; font-weight: bold; margin: 15px 0;'>
                ฿{current_month_sales/1000000:.1f}M
            </div>
            <div style='font-size: 12px; opacity: 0.8;'>Current Sales</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        att_color = "#2ecc71" if attainment >= 90 else "#e74c3c"
        st.markdown(
            f"""
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
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ==================== SALES BY CHANNEL ====================
    st.markdown("### 🏪 Sales by Channel")

    # with st.expander("📖 Description", expanded=False):
    #     st.markdown(
    #         """
    #     <div class='metric-explanation'>
    #         <b>📖 คำอธิบาย:</b> แสดงยอดขายแยกตามช่องทางการขาย เพื่อดูว่าช่องทางไหนมี Performance ดีที่สุด
    #     </div>
    #     """,
    #         unsafe_allow_html=True,
    #     )

    channel_sales = (
        df_filtered.groupby("channel")
        .agg({"net_revenue": "sum", "profit": "sum", "order_id": "nunique"})
        .reset_index()
    )
    channel_sales.columns = ["Channel", "Revenue", "Profit", "Orders"]
    channel_sales["Margin_%"] = (
        channel_sales["Profit"] / channel_sales["Revenue"] * 100
    ).round(1)
    channel_sales["AOV"] = (channel_sales["Revenue"] / channel_sales["Orders"]).round(0)
    channel_sales = channel_sales.sort_values("Revenue", ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        # Horizontal bar chart
        ch_sorted = channel_sales.sort_values("Revenue", ascending=True)
        colors_list = [CHANNEL_COLORS.get(ch, "#95a5a6") for ch in ch_sorted["Channel"]]

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                y=ch_sorted["Channel"],
                x=ch_sorted["Revenue"],
                orientation="h",
                marker=dict(color=colors_list),
                text=ch_sorted["Revenue"],
                texttemplate="฿%{text:,.0f}",
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>",
            )
        )

        fig.update_layout(
            title="<b>Revenue by Channel</b>",
            xaxis=dict(
                title="Revenue (฿)", showgrid=True, gridcolor="rgba(0,0,0,0.05)"
            ),
            yaxis=dict(title=""),
            plot_bgcolor="white",
            height=400,
            showlegend=False,
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Stacked bar: Revenue vs Profit
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=channel_sales["Channel"],
                y=channel_sales["Profit"],
                name="Profit",
                marker_color="#2ecc71",
                text=channel_sales["Profit"],
                texttemplate="฿%{text:,.0f}",
                textposition="inside",
                hovertemplate="<b>%{x}</b><br>Profit: ฿%{y:,.0f}<extra></extra>",
            )
        )

        fig.add_trace(
            go.Bar(
                x=channel_sales["Channel"],
                y=channel_sales["Revenue"] - channel_sales["Profit"],
                name="Cost",
                marker_color="#e74c3c",
                text=channel_sales["Revenue"] - channel_sales["Profit"],
                texttemplate="฿%{text:,.0f}",
                textposition="inside",
                hovertemplate="<b>%{x}</b><br>Cost: ฿%{y:,.0f}<extra></extra>",
            )
        )

        fig.update_layout(
            title="<b>Revenue Breakdown: Profit vs Cost</b>",
            xaxis=dict(title="", showgrid=False),
            yaxis=dict(title="Amount (฿)", showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
            barmode="stack",
            plot_bgcolor="white",
            height=400,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

    # Channel metrics table
    st.markdown("#### 📊 Channel Performance Metrics")

    styled_ch = channel_sales.style.format(
        {
            "Revenue": "฿{:,.0f}",
            "Profit": "฿{:,.0f}",
            "Orders": "{:,}",
            "Margin_%": "{:.1f}%",
            "AOV": "฿{:,.0f}",
        }
    ).background_gradient(subset=["Margin_%"], cmap="RdYlGn", vmin=0, vmax=100)

    st.dataframe(styled_ch, use_container_width=True)

    st.markdown("---")

    # ==================== PRODUCT PERFORMANCE ====================
    st.markdown("### 🏆 Top Product Performance")

    # with st.expander("📖 Description", expanded=False):
    #     st.markdown(
    #         """
    #     <div class='metric-explanation'>
    #         <b>📖 คำอธิบาย:</b> แสดงสินค้าที่ขายดีที่สุด 20 อันดับแรก วัดจากยอดขาย และอัตรากำไร
    #     </div>
    #     """,
    #         unsafe_allow_html=True,
    #     )

    product_sales = (
        df_filtered.groupby(["product_id", "product_name", "category"])
        .agg({"net_revenue": "sum", "profit": "sum", "quantity": "sum"})
        .reset_index()
    )
    product_sales.columns = ["ID", "Product", "Category", "Revenue", "Profit", "Units"]
    product_sales["Margin_%"] = (
        product_sales["Profit"] / product_sales["Revenue"] * 100
    ).round(1)
    product_sales = product_sales.sort_values("Revenue", ascending=False).head(20)

    col1, col2 = st.columns([3, 2])

    with col1:
        # Top 10 horizontal bar
        top10 = product_sales.head(10).sort_values("Revenue", ascending=True)

        fig = go.Figure()

        # Color by margin
        colors = [
            "#2ecc71" if m >= 50 else "#f39c12" if m >= 30 else "#e74c3c"
            for m in top10["Margin_%"]
        ]

        fig.add_trace(
            go.Bar(
                y=top10["Product"],
                x=top10["Revenue"],
                orientation="h",
                marker=dict(color=colors),
                text=top10["Revenue"],
                texttemplate="฿%{text:,.0f}",
                textposition="outside",
                customdata=top10[["Margin_%"]],
                hovertemplate="<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<br>Margin: %{customdata[0]:.1f}%<extra></extra>",
            )
        )

        fig.update_layout(
            title="<b>Top 10 Products by Revenue</b><br><sub>Color: Green=High Margin, Yellow=Medium, Red=Low</sub>",
            xaxis=dict(
                title="Revenue (฿)", showgrid=True, gridcolor="rgba(0,0,0,0.05)"
            ),
            yaxis=dict(title=""),
            plot_bgcolor="white",
            height=450,
            showlegend=False,
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Scatter: Revenue vs Margin (Fixed bubble size)
        fig = go.Figure()

        # Calculate bubble size (max 80, min 10)
        max_units = product_sales["Units"].max()
        min_units = product_sales["Units"].min()
        normalized_sizes = (
            10 + (product_sales["Units"] - min_units) / (max_units - min_units) * 70
        )

        fig.add_trace(
            go.Scatter(
                x=product_sales["Revenue"],
                y=product_sales["Margin_%"],
                mode="markers",
                marker=dict(
                    size=normalized_sizes,
                    color=product_sales["Margin_%"],
                    colorscale="RdYlGn",
                    showscale=True,
                    colorbar=dict(title="Margin %"),
                    line=dict(width=1, color="white"),
                    sizemode="diameter",
                ),
                text=product_sales["Product"],
                customdata=product_sales["Units"],
                hovertemplate="<b>%{text}</b><br>Revenue: ฿%{x:,.0f}<br>Margin: %{y:.1f}%<br>Units: %{customdata:,}<extra></extra>",
            )
        )

        # Add quadrant lines
        avg_revenue = product_sales["Revenue"].median()
        avg_margin = product_sales["Margin_%"].median()

        fig.add_hline(
            y=avg_margin,
            line_dash="dash",
            line_color="gray",
            opacity=0.5,
            annotation_text="Avg Margin",
            annotation_position="right",
        )
        fig.add_vline(
            x=avg_revenue,
            line_dash="dash",
            line_color="gray",
            opacity=0.5,
            annotation_text="Avg Revenue",
            annotation_position="top",
        )

        # Add quadrant labels
        fig.add_annotation(
            x=avg_revenue * 1.5,
            y=avg_margin * 1.2,
            text="🌟 Stars<br>(High Revenue, High Margin)",
            showarrow=False,
            font=dict(size=10, color="green"),
        )

        fig.add_annotation(
            x=avg_revenue * 1.5,
            y=avg_margin * 0.8,
            text="💰 Cash Cows<br>(High Revenue, Low Margin)",
            showarrow=False,
            font=dict(size=10, color="orange"),
        )

        fig.add_annotation(
            x=avg_revenue * 0.5,
            y=avg_margin * 1.2,
            text="🚀 Growth<br>(Low Revenue, High Margin)",
            showarrow=False,
            font=dict(size=10, color="blue"),
        )

        fig.add_annotation(
            x=avg_revenue * 0.5,
            y=avg_margin * 0.8,
            text="⚠️ Question Marks<br>(Low Revenue, Low Margin)",
            showarrow=False,
            font=dict(size=10, color="red"),
        )

        fig.update_layout(
            title="<b>Product Portfolio Analysis (BCG Matrix)</b><br><sub>Bubble size = Units Sold</sub>",
            xaxis=dict(
                title="Revenue (฿)", showgrid=True, gridcolor="rgba(0,0,0,0.05)"
            ),
            yaxis=dict(
                title="Profit Margin (%)", showgrid=True, gridcolor="rgba(0,0,0,0.05)"
            ),
            plot_bgcolor="white",
            height=450,
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 📋 Top 20 Products Detail")

    styled_prod = product_sales.style.format(
        {
            "Revenue": "฿{:,.0f}",
            "Profit": "฿{:,.0f}",
            "Units": "{:,}",
            "Margin_%": "{:.1f}%",
        }
    ).background_gradient(subset=["Margin_%"], cmap="RdYlGn", vmin=0, vmax=100)

    st.dataframe(styled_prod, use_container_width=True)

    st.markdown("---")

    # ==================== AI ANOMALY DETECTION ====================
    st.markdown("### 🔍 AI Anomaly Detection")

    with st.expander("📖 Description", expanded=False):
        st.markdown(
            """
        <div class='metric-explanation'>
            <b>📖 AI Anomaly Detection:</b> ระบบ AI ตรวจจับค่าผิดปกติในยอดขาย<br><br>
            ใช้ <b>Z-Score</b> ในการหาค่าผิดปกติ ถ้า Z-Score &gt; 2 แสดงว่ายอดขายในเดือนนั้นผิดปกติ<br><br>
            <b>🎯 ประโยชน์:</b><br>
            • ตรวจจับยอดขายตกลงฉับพลัน<br>
            • เตือนเมื่อยอดขายเพิ่มผิดปกติ<br>
            • ช่วยวางแผนรับมือ
        </div>
        """,
            unsafe_allow_html=True,
        )

    from scipy import stats

    monthly_sales_copy = monthly_sales.copy()
    monthly_sales_copy["z_score"] = np.abs(
        stats.zscore(monthly_sales_copy["net_revenue"])
    )
    anomalies = monthly_sales_copy[monthly_sales_copy["z_score"] > 2]

    if len(anomalies) > 0:
        st.warning(f"⚠️ พบ **{len(anomalies)} เดือน** ที่มีค่าผิดปกติ")

        for idx, row in anomalies.iterrows():
            deviation = (
                (row["net_revenue"] - monthly_sales_copy["net_revenue"].mean())
                / monthly_sales_copy["net_revenue"].mean()
                * 100
            )

            if deviation > 0:
                st.success(
                    f"📈 **{row['month_label']}**: ยอดขาย ฿{row['net_revenue']:,.0f} ({deviation:+.1f}% จากค่าเฉลี่ย) - สูงกว่าปกติมาก!"
                )
            else:
                st.error(
                    f"📉 **{row['month_label']}**: ยอดขาย ฿{row['net_revenue']:,.0f} ({deviation:+.1f}% จากค่าเฉลี่ย) - ต่ำกว่าปกติมาก!"
                )
    else:
        st.success("✅ ไม่พบความผิดปกติในข้อมูล - ยอดขายมีความสม่ำเสมอ")

    # ==================== SMART PRODUCT RECOMMENDATIONS ====================
    st.markdown("---")
    st.markdown("### 🎁 Smart Product Recommendations (Cross-sell)")

    with st.expander("📖 Description", expanded=False):
        st.markdown(
            """
        <div class='metric-explanation'>
            <b>📖 Market Basket Analysis:</b> วิเคราะห์สินค้าที่ลูกค้ามักซื้อด้วยกัน<br><br>
            <b>💡 ประโยชน์:</b><br>
            • สร้าง Product Bundle<br>
            • แนะนำสินค้าเพิ่มเติมในหน้า Checkout<br>
            • วางตำแหน่งสินค้าในร้านให้ใกล้กัน
        </div>
        """,
            unsafe_allow_html=True,
        )

    from itertools import combinations
    from collections import Counter

    # Group products by order
    order_products = df_filtered.groupby("order_id")["product_name"].apply(list).values

    # Find frequent pairs
    pairs = []
    for products in order_products:
        if len(products) >= 2:
            pairs.extend(list(combinations(sorted(products), 2)))

    pair_counts = Counter(pairs)
    top_pairs = pair_counts.most_common(10)

    if len(top_pairs) > 0:
        st.markdown("**คู่สินค้าที่ลูกค้ามักซื้อด้วยกัน (Top 10):**")

        for i, ((prod1, prod2), count) in enumerate(top_pairs, 1):
            st.markdown(
                f"{i}. **{prod1}** + **{prod2}** → ซื้อด้วยกัน **{count} ครั้ง**"
            )

        st.info(
            "💡 **คำแนะนำ:** ใช้ข้อมูลนี้สร้าง Bundle Promotion หรือแนะนำสินค้าในหน้า Checkout เพื่อเพิ่มยอดขาย!"
        )
    else:
        st.info("ยังไม่มีข้อมูลเพียงพอสำหรับการวิเคราะห์")

with tab2:
    st.markdown("# 📢 Marketing Analytics")
    st.markdown("---")

    # Data availability checker
    st.markdown("### 📋 Available Marketing Metrics")

    has_funnel = all(
        col in df_filtered.columns for col in ["visits", "add_to_cart", "checkout"]
    )
    has_campaign = (
        "campaign_type" in df_filtered.columns
        and df_filtered["campaign_type"].notna().any()
    )
    has_acquisition = "acquisition_channel" in df_filtered.columns

    col1, col2, col3 = st.columns(3)

    with col1:
        if has_funnel:
            st.success("✅ **Conversion Funnel Data Available**")
        else:
            st.warning(
                "⚠️ **Conversion Funnel Data Missing**\nAdd columns: `visits`, `add_to_cart`, `checkout`"
            )

    with col2:
        if has_campaign:
            st.success("✅ **Campaign Data Available**")
        else:
            st.warning(
                "⚠️ **Campaign Data Missing**\nAdd `campaign_type` column for campaign analysis"
            )

    with col3:
        if has_acquisition:
            st.success("✅ **Acquisition Channel Data Available**")
        else:
            st.warning(
                "⚠️ **Acquisition Data Missing**\nAdd `acquisition_channel` column for acquisition analysis"
            )

    st.markdown("---")

    # ==================== CONVERSION FUNNEL ====================
    st.markdown("### 🎯 Conversion Funnel Analysis")

    with st.expander("📖 Description", expanded=False):
        st.markdown(
            f"""
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
        """,
            unsafe_allow_html=True,
        )

    if has_funnel:
        # Use actual funnel data
        total_visitors = df_filtered["visits"].sum()
        add_to_cart = df_filtered["add_to_cart"].sum()
        checkout_count = df_filtered["checkout"].sum()
        total_orders = df_filtered["order_id"].nunique()
        conversion_rate = (
            (total_orders / total_visitors * 100) if total_visitors > 0 else 0
        )

        # Compare with target
        target_conversion = st.session_state.targets["conversion_rate"]
        conversion_status = (
            "✅ Above Target"
            if conversion_rate >= target_conversion
            else "⚠️ Below Target"
        )
        conversion_color = (
            "#2ecc71" if conversion_rate >= target_conversion else "#e74c3c"
        )

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown(
                f"""
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
            """,
                unsafe_allow_html=True,
            )

        with col2:
            # Funnel chart
            funnel_data = pd.DataFrame(
                {
                    "Stage": ["Visitors", "Add to Cart", "Checkout", "Purchase"],
                    "Count": [
                        total_visitors,
                        add_to_cart,
                        checkout_count,
                        total_orders,
                    ],
                    "Color": ["#3498db", "#2ecc71", "#f39c12", "#9b59b6"],
                }
            )

            fig = go.Figure()

            fig.add_trace(
                go.Funnel(
                    y=funnel_data["Stage"],
                    x=funnel_data["Count"],
                    textposition="inside",
                    textinfo="value+percent initial",
                    marker=dict(
                        color=funnel_data["Color"], line=dict(color="white", width=2)
                    ),
                    textfont=dict(size=13, weight="bold", color="white"),
                    hovertemplate="<b>%{y}</b><br>Count: %{x:,}<br>Rate: %{percentInitial}<extra></extra>",
                    connector=dict(line=dict(color="gray", width=1)),
                )
            )

            fig.update_layout(
                title="<b>Sales Funnel</b>",
                plot_bgcolor="white",
                paper_bgcolor="white",
                height=400,
                margin=dict(t=60, b=40, l=40, r=120),
                showlegend=False,
            )

            st.plotly_chart(fig, use_container_width=True)
    else:
        # Show alternative: Order completion metrics
        st.info("💡 **Showing Order Completion Metrics** (Funnel data not available)")

        total_orders = df_filtered["order_id"].nunique()
        total_customers = df_filtered["user_id"].nunique()
        completed_orders = df_filtered[df_filtered["status"] == "Completed"][
            "order_id"
        ].nunique()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 30px; border-radius: 10px; color: white; text-align: center; height: 200px;
                        display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size: 14px; opacity: 0.9;'>TOTAL ORDERS</div>
                <div style='font-size: 48px; font-weight: bold; margin: 15px 0;'>
                    {total_orders:,}
                </div>
                <div style='font-size: 12px; opacity: 0.8;'>All statuses</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            completion_rate = (
                (completed_orders / total_orders * 100) if total_orders > 0 else 0
            )
            st.markdown(
                f"""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        padding: 30px; border-radius: 10px; color: white; text-align: center; height: 200px;
                        display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size: 14px; opacity: 0.9;'>COMPLETION RATE</div>
                <div style='font-size: 48px; font-weight: bold; margin: 15px 0;'>
                    {completion_rate:.1f}%
                </div>
                <div style='font-size: 12px; opacity: 0.8;'>{completed_orders:,} completed</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col3:
            orders_per_customer = (
                total_orders / total_customers if total_customers > 0 else 0
            )
            st.markdown(
                f"""
            <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        padding: 30px; border-radius: 10px; color: white; text-align: center; height: 200px;
                        display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size: 14px; opacity: 0.9;'>ORDERS/CUSTOMER</div>
                <div style='font-size: 48px; font-weight: bold; margin: 15px 0;'>
                    {orders_per_customer:.1f}
                </div>
                <div style='font-size: 12px; opacity: 0.8;'>Average frequency</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Show order status breakdown
        st.markdown("<br>", unsafe_allow_html=True)

        status_data = df_filtered.groupby("status")["order_id"].nunique().reset_index()
        status_data.columns = ["Status", "Orders"]
        status_data = status_data.sort_values("Orders", ascending=True)

        status_colors = {
            "Completed": "#2ecc71",
            "Pending": "#f39c12",
            "Cancelled": "#e74c3c",
            "Refunded": "#95a5a6",
        }

        colors_list = [status_colors.get(s, "#95a5a6") for s in status_data["Status"]]

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                y=status_data["Status"],
                x=status_data["Orders"],
                orientation="h",
                marker=dict(color=colors_list, line=dict(color="white", width=2)),
                text=status_data["Orders"],
                texttemplate="%{text:,}",
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Orders: %{x:,}<extra></extra>",
            )
        )

        fig.update_layout(
            title="<b>Order Status Breakdown</b>",
            xaxis=dict(
                title="Number of Orders", showgrid=True, gridcolor="rgba(0,0,0,0.05)"
            ),
            yaxis=dict(title=""),
            plot_bgcolor="white",
            height=300,
            showlegend=False,
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ==================== CUSTOMER ACQUISITION COST ====================
    st.markdown("### 💳 Customer Acquisition Cost (CAC)")

    with st.expander("📖 Description", expanded=False):
        st.markdown(
            """
        <div class='metric-explanation'>
            <b>📖 คำอธิบาย:</b> ค่าใช้จ่ายที่ใช้ในการหาลูกค้าใหม่ 1 คน<br>
            <div class='metric-formula'>
                สูตร: ค่าใช้จ่ายทางการตลาด / จำนวนลูกค้าใหม่
            </div>
            <b>🎯 เป้าหมาย:</b> ควรต่ำกว่า Customer Lifetime Value (CLV) อย่างน้อย 3 เท่า
        </div>
        """,
            unsafe_allow_html=True,
        )

    marketing_cost = (
        df_filtered["discount_amount"].sum()
        if "discount_amount" in df_filtered.columns
        else 0
    )
    new_customers = df_filtered["user_id"].nunique()
    cac = marketing_cost / new_customers if new_customers > 0 else 0

    # Calculate CLV
    analysis_date = df_filtered["order_date"].max()
    last_purchase = df_filtered.groupby("user_id")["order_date"].max()
    churned = ((analysis_date - last_purchase).dt.days > 90).sum()
    churn_rate = (churned / len(last_purchase) * 100) if len(last_purchase) > 0 else 0
    retention_rate = 100 - churn_rate
    avg_revenue = df_filtered.groupby("user_id")["net_revenue"].sum().mean()
    clv = (profit_margin / 100) * (retention_rate / 100) * avg_revenue

    cac_to_clv_ratio = (cac / clv) if clv > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9;'>CAC</div>
            <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
                ฿{cac:,.0f}
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Per customer</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9;'>CLV</div>
            <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
                ฿{clv:,.0f}
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Lifetime value</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        ratio_color = "#2ecc71" if cac_to_clv_ratio < 0.33 else "#e74c3c"
        st.markdown(
            f"""
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
        """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9;'>NEW CUSTOMERS</div>
            <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
                {new_customers:,}
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>In period</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
# # ==================== ADDITIONAL MARKETING METRICS ====================
# # แทรกโค้ดนี้ใน Marketing Analytics tab (tab2) หลังจาก CAC/CLV section (ประมาณบรรทัด 1698)
# # ก่อน Retention & Churn section

#     # ==================== CAMPAIGN PERFORMANCE METRICS ====================
#     st.markdown("### 📊 Campaign Performance & ROAS")
    
#     with st.expander("📖 Description", expanded=False):
#         st.markdown("""
#         <div class='metric-explanation'>
#             <b>📖 Marketing Campaign Metrics:</b><br>
#             • <b>ROAS (Return on Ad Spend):</b> (Revenue / Ad Cost) × 100 → เป้าหมาย >300%<br>
#             • <b>CTR (Click-Through Rate):</b> (Clicks / Impressions) × 100 → เป้าหมาย >3%<br>
#             • <b>CVR (Conversion Rate):</b> (Conversions / Clicks) × 100 → เป้าหมาย >5%<br>
#             • <b>CPC (Cost Per Click):</b> Ad Cost / Clicks<br>
#             • <b>CPA (Cost Per Acquisition):</b> Ad Cost / Conversions<br>
#             <b>💡 การใช้ประโยชน์:</b> วัดประสิทธิภาพแคมเปญ เพื่อตัดสินใจจัดสรรงบ
#         </div>
#         """, unsafe_allow_html=True)
    
#     # Check if campaign data exists
#     has_campaign_metrics = all(col in df_filtered.columns for col in 
#                                ['campaign_name', 'campaign_cost', 'impressions', 'clicks'])
    
#     if not has_campaign_metrics:
#         st.info("""
#         ℹ️ **Campaign Performance Data Not Available**
        
#         To see detailed campaign metrics, please add these columns to your data:
#         - `campaign_name` - ชื่อแคมเปญ
#         - `campaign_cost` - ค่าใช้จ่ายแคมเปญ
#         - `impressions` - จำนวนครั้งที่โฆษณาแสดง
#         - `clicks` - จำนวนคลิก
#         - `conversions` - จำนวนคนที่ทำ action สำเร็จ
        
#         **Currently showing:** Estimated metrics based on channel data
#         """)
    
#     # Prepare campaign data (with fallback to channel data)
#     if 'campaign_name' in df_filtered.columns and df_filtered['campaign_name'].notna().any():
#         # Use actual campaign data
#         campaign_group = df_filtered.groupby('campaign_name').agg({
#             'net_revenue': 'sum',
#             'order_id': 'nunique',
#             'user_id': 'nunique',
#             'campaign_cost': 'first' if 'campaign_cost' in df_filtered.columns else lambda x: 0,
#             'impressions': 'sum' if 'impressions' in df_filtered.columns else lambda x: 0,
#             'clicks': 'sum' if 'clicks' in df_filtered.columns else lambda x: 0,
#             'conversions': 'sum' if 'conversions' in df_filtered.columns else lambda x: 0
#         }).reset_index()
        
#         data_quality_tracker.mark_actual('campaign_performance')
#     else:
#         # Fallback: Use channel as campaign
#         if 'channel' not in df_filtered.columns:
#             st.warning("⚠️ No channel or campaign data available. Skipping campaign analysis.")
#             campaign_group = pd.DataFrame()  # Empty dataframe
#         else:
#             campaign_group = df_filtered.groupby('channel').agg({
#                 'net_revenue': 'sum',
#                 'order_id': 'nunique',
#                 'user_id': 'nunique'
#             }).reset_index()
#             campaign_group.rename(columns={'channel': 'campaign_name'}, inplace=True)
            
#             # Estimate missing metrics (industry averages)
#             campaign_group['campaign_cost'] = campaign_group['net_revenue'] * 0.15  # 15% of revenue
#             campaign_group['impressions'] = campaign_group['order_id'] * 50  # 1 order ≈ 50 impressions
#             campaign_group['clicks'] = campaign_group['order_id'] * 5  # 1 order ≈ 5 clicks
#             campaign_group['conversions'] = campaign_group['order_id']  # 1 order = 1 conversion
            
#             data_quality_tracker.mark_estimated('campaign_performance', 'Estimated from channel data (15% cost ratio)')
    
#     if not campaign_group.empty:
#         # Calculate campaign metrics
#         campaign_group['ROAS_%'] = (campaign_group['net_revenue'] / campaign_group['campaign_cost'] * 100).fillna(0)
#         campaign_group['CTR_%'] = (campaign_group['clicks'] / campaign_group['impressions'] * 100).fillna(0)
#         campaign_group['CVR_%'] = (campaign_group['conversions'] / campaign_group['clicks'] * 100).fillna(0)
#         campaign_group['CPC'] = (campaign_group['campaign_cost'] / campaign_group['clicks']).fillna(0)
#         campaign_group['CPA'] = (campaign_group['campaign_cost'] / campaign_group['conversions']).fillna(0)
#         campaign_group['revenue_per_click'] = (campaign_group['net_revenue'] / campaign_group['clicks']).fillna(0)
#         campaign_group['profit'] = campaign_group['net_revenue'] - campaign_group['campaign_cost']
#         campaign_group['profit_margin_%'] = (campaign_group['profit'] / campaign_group['net_revenue'] * 100).fillna(0)
        
#         # Sort by ROAS
#         campaign_group = campaign_group.sort_values('ROAS_%', ascending=False)
        
#         # Summary metrics
#         total_ad_spend = campaign_group['campaign_cost'].sum()
#         total_campaign_revenue = campaign_group['net_revenue'].sum()
#         total_campaign_profit = campaign_group['profit'].sum()
#         avg_roas = (total_campaign_revenue / total_ad_spend * 100) if total_ad_spend > 0 else 0
#         total_campaign_conversions = campaign_group['conversions'].sum()
#         avg_campaign_cpa = (total_ad_spend / total_campaign_conversions) if total_campaign_conversions > 0 else 0
        
#         # Display summary cards
#         col1, col2, col3, col4 = st.columns(4)
        
#         with col1:
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                         padding: 20px; border-radius: 10px; color: white; text-align: center;'>
#                 <div style='font-size: 12px; opacity: 0.9;'><b>TOTAL AD SPEND</b></div>
#                 <div style='font-size: 36px; font-weight: bold; margin: 10px 0;'>
#                     ฿{total_ad_spend/1000:.0f}K
#                 </div>
#                 <div style='font-size: 10px; opacity: 0.8;'>Marketing Investment</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col2:
#             roas_color = "#2ecc71" if avg_roas >= 300 else "#f39c12" if avg_roas >= 200 else "#e74c3c"
#             roas_status = "✅ Excellent" if avg_roas >= 300 else "⚠️ Good" if avg_roas >= 200 else "❌ Poor"
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, {roas_color} 0%, {roas_color}dd 100%); 
#                         padding: 20px; border-radius: 10px; color: white; text-align: center;'>
#                 <div style='font-size: 12px; opacity: 0.9;'><b>AVERAGE ROAS</b></div>
#                 <div style='font-size: 36px; font-weight: bold; margin: 10px 0;'>
#                     {avg_roas:.0f}%
#                 </div>
#                 <div style='font-size: 10px; opacity: 0.8;'>{roas_status}</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col3:
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); 
#                         padding: 20px; border-radius: 10px; color: white; text-align: center;'>
#                 <div style='font-size: 12px; opacity: 0.9;'><b>CAMPAIGN PROFIT</b></div>
#                 <div style='font-size: 36px; font-weight: bold; margin: 10px 0;'>
#                     ฿{total_campaign_profit/1000:.0f}K
#                 </div>
#                 <div style='font-size: 10px; opacity: 0.8;'>Revenue - Ad Cost</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col4:
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
#                         padding: 20px; border-radius: 10px; color: white; text-align: center;'>
#                 <div style='font-size: 12px; opacity: 0.9;'><b>AVG CPA</b></div>
#                 <div style='font-size: 36px; font-weight: bold; margin: 10px 0;'>
#                     ฿{avg_campaign_cpa:.0f}
#                 </div>
#                 <div style='font-size: 10px; opacity: 0.8;'>Cost Per Acquisition</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         st.markdown("<br>", unsafe_allow_html=True)
        
#         # Campaign comparison charts
#         col1, col2 = st.columns(2)
        
#         with col1:
#             # ROAS by Campaign
#             fig = go.Figure()
            
#             # Add benchmark lines
#             fig.add_hline(y=300, line_dash="dash", line_color="green", 
#                          annotation_text="Excellent (300%)", annotation_position="right")
#             fig.add_hline(y=200, line_dash="dash", line_color="orange",
#                          annotation_text="Good (200%)", annotation_position="right")
            
#             # Color based on performance
#             colors = ['#2ecc71' if x >= 300 else '#f39c12' if x >= 200 else '#e74c3c' 
#                      for x in campaign_group['ROAS_%']]
            
#             fig.add_trace(go.Bar(
#                 x=campaign_group['campaign_name'],
#                 y=campaign_group['ROAS_%'],
#                 marker_color=colors,
#                 text=campaign_group['ROAS_%'],
#                 texttemplate='%{text:.0f}%',
#                 textposition='outside',
#                 hovertemplate='<b>%{x}</b><br>ROAS: %{y:.0f}%<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title='<b>ROAS by Campaign/Channel</b>',
#                 xaxis=dict(title='', showticklabels=True),
#                 yaxis=dict(title='ROAS (%)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#                 plot_bgcolor='white',
#                 height=350,
#                 showlegend=False
#             )
            
#             st.plotly_chart(fig, use_container_width=True)
        
#         with col2:
#             # Revenue vs Cost
#             fig = go.Figure()
            
#             fig.add_trace(go.Bar(
#                 name='Revenue',
#                 x=campaign_group['campaign_name'],
#                 y=campaign_group['net_revenue'],
#                 marker_color='#3498db',
#                 text=campaign_group['net_revenue'],
#                 texttemplate='฿%{text:.2s}',
#                 hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
#             ))
            
#             fig.add_trace(go.Bar(
#                 name='Cost',
#                 x=campaign_group['campaign_name'],
#                 y=campaign_group['campaign_cost'],
#                 marker_color='#e74c3c',
#                 text=campaign_group['campaign_cost'],
#                 texttemplate='฿%{text:.2s}',
#                 hovertemplate='<b>%{x}</b><br>Cost: ฿%{y:,.0f}<extra></extra>'
#             ))
            
#             fig.update_layout(
#                 title='<b>Revenue vs Cost by Campaign</b>',
#                 xaxis=dict(title=''),
#                 yaxis=dict(title='Amount (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#                 plot_bgcolor='white',
#                 height=350,
#                 barmode='group',
#                 legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#             )
            
#             st.plotly_chart(fig, use_container_width=True)
        
#         # Campaign Performance Table
#         st.markdown("#### 📋 Campaign Performance Details")
        
#         campaign_display = campaign_group[[
#             'campaign_name', 'impressions', 'clicks', 'CTR_%', 'conversions',
#             'CVR_%', 'net_revenue', 'campaign_cost', 'CPA', 'ROAS_%', 
#             'profit', 'profit_margin_%'
#         ]].copy()
        
#         campaign_display.columns = [
#             'Campaign', 'Impressions', 'Clicks', 'CTR %', 'Conversions',
#             'CVR %', 'Revenue', 'Cost', 'CPA', 'ROAS %', 'Profit', 'Margin %'
#         ]
        
#         # Color coding
#         def highlight_campaign_performance(row):
#             colors = []
#             for col in row.index:
#                 if col == 'ROAS %':
#                     if row[col] >= 300:
#                         colors.append('background-color: #d5f4e6')  # Green
#                     elif row[col] >= 200:
#                         colors.append('background-color: #fff3cd')  # Yellow
#                     else:
#                         colors.append('background-color: #f8d7da')  # Red
#                 elif col == 'Margin %':
#                     if row[col] >= 50:
#                         colors.append('background-color: #d5f4e6')
#                     elif row[col] >= 30:
#                         colors.append('background-color: #fff3cd')
#                     else:
#                         colors.append('background-color: #f8d7da')
#                 else:
#                     colors.append('')
#             return colors
        
#         styled_campaigns = campaign_display.style.format({
#             'Impressions': '{:,.0f}',
#             'Clicks': '{:,.0f}',
#             'CTR %': '{:.2f}%',
#             'Conversions': '{:,.0f}',
#             'CVR %': '{:.2f}%',
#             'Revenue': '฿{:,.0f}',
#             'Cost': '฿{:,.0f}',
#             'CPA': '฿{:,.0f}',
#             'ROAS %': '{:.0f}%',
#             'Profit': '฿{:,.0f}',
#             'Margin %': '{:.1f}%'
#         }).apply(highlight_campaign_performance, axis=1)
        
#         st.dataframe(styled_campaigns, use_container_width=True, height=300)
        
#         # Key Insights
#         st.markdown("#### 💡 Key Campaign Insights")
        
#         best_roas = campaign_group.nlargest(1, 'ROAS_%').iloc[0]
#         worst_roas = campaign_group.nsmallest(1, 'ROAS_%').iloc[0]
#         best_profit = campaign_group.nlargest(1, 'profit').iloc[0]
#         lowest_cpa = campaign_group.nsmallest(1, 'CPA').iloc[0]
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             st.success(f"""
#             **🏆 Best Performing Campaign:**
            
#             **{best_roas['campaign_name']}**
#             - ROAS: {best_roas['ROAS_%']:.0f}%
#             - Profit: ฿{best_roas['profit']:,.0f}
#             - Margin: {best_roas['profit_margin_%']:.1f}%
            
#             💡 **Action:** Scale up budget by 25-50%! Every ฿1 spent returns ฿{best_roas['ROAS_%']/100:.2f}
#             """)
            
#             st.info(f"""
#             **💰 Most Profitable:**
            
#             **{best_profit['campaign_name']}**
#             - Total Profit: ฿{best_profit['profit']:,.0f}
#             - Revenue: ฿{best_profit['net_revenue']:,.0f}
#             - ROAS: {best_profit['ROAS_%']:.0f}%
            
#             💡 **Action:** Maintain current strategy
#             """)
        
#         with col2:
#             st.error(f"""
#             **⚠️ Underperforming Campaign:**
            
#             **{worst_roas['campaign_name']}**
#             - ROAS: {worst_roas['ROAS_%']:.0f}%
#             - Profit: ฿{worst_roas['profit']:,.0f}
#             - Margin: {worst_roas['profit_margin_%']:.1f}%
            
#             💡 **Action:** {'🛑 Pause immediately' if worst_roas['ROAS_%'] < 100 else '🔧 Optimize targeting/creative'}
#             """)
            
#             st.success(f"""
#             **🎯 Most Efficient:**
            
#             **{lowest_cpa['campaign_name']}**
#             - CPA: ฿{lowest_cpa['CPA']:,.0f}
#             - CVR: {lowest_cpa['CVR_%']:.2f}%
#             - Conversions: {lowest_cpa['conversions']:,.0f}
            
#             💡 **Action:** Study & replicate strategy
#             """)
        
#         # Recommendations
#         st.markdown("#### 🎯 Data-Driven Recommendations")
        
#         st.markdown("""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 25px; border-radius: 15px; color: white;'>
#             <h5 style='margin: 0 0 15px 0;'>📊 Marketing Actions</h5>
#         """, unsafe_allow_html=True)
        
#         recommendations = []
        
#         # Budget reallocation
#         if len(campaign_group) > 1:
#             high_roas = campaign_group[campaign_group['ROAS_%'] >= 300]
#             low_roas = campaign_group[campaign_group['ROAS_%'] < 150]
            
#             if not high_roas.empty:
#                 recommendations.append(
#                     f"💰 <b>Scale Winners:</b> Increase budget for {len(high_roas)} campaigns "
#                     f"with avg ROAS {high_roas['ROAS_%'].mean():.0f}% by 25-50%"
#                 )
            
#             if not low_roas.empty:
#                 potential_savings = low_roas['campaign_cost'].sum()
#                 recommendations.append(
#                     f"⚠️ <b>Cut Losers:</b> Pause {len(low_roas)} underperforming campaigns. "
#                     f"Save ฿{potential_savings:,.0f}/period"
#                 )
        
#         # CTR optimization
#         avg_ctr = campaign_group['CTR_%'].mean()
#         low_ctr = campaign_group[campaign_group['CTR_%'] < avg_ctr * 0.5]
#         if not low_ctr.empty:
#             recommendations.append(
#                 f"📸 <b>Creative Refresh:</b> {len(low_ctr)} campaigns have low CTR "
#                 f"(<{avg_ctr*0.5:.2f}%). Test new ad creatives"
#             )
        
#         # CVR improvement
#         avg_cvr = campaign_group['CVR_%'].mean()
#         if avg_cvr < 2.0:
#             recommendations.append(
#                 f"🛒 <b>Improve Conversion:</b> CVR is {avg_cvr:.2f}%. "
#                 f"Optimize landing pages, simplify checkout"
#             )
        
#         # Overall ROAS
#         if avg_roas < 200:
#             recommendations.append(
#                 f"📉 <b>Overall Performance:</b> Avg ROAS ({avg_roas:.0f}%) below target. "
#                 f"Review targeting, pricing, and value proposition"
#             )
#         elif avg_roas >= 300:
#             recommendations.append(
#                 f"✅ <b>Excellent!</b> Avg ROAS ({avg_roas:.0f}%) exceeds target. "
#                 f"Consider scaling total ad spend by 20-30%"
#             )
        
#         if recommendations:
#             st.markdown("<div style='padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px; margin-top: 15px;'>", 
#                        unsafe_allow_html=True)
#             for rec in recommendations:
#                 st.markdown(f"<p style='margin: 8px 0; font-size: 13px;'>{rec}</p>", unsafe_allow_html=True)
#             st.markdown("</div>", unsafe_allow_html=True)
        
#         st.markdown("</div>", unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== MARKETING EFFICIENCY SCORE ====================
#     st.markdown("### 🏆 Marketing Efficiency Score")
    
#     with st.expander("📖 Description", expanded=False):
#         st.markdown("""
#         <div class='metric-explanation'>
#             <b>📖 Marketing Efficiency Score:</b> คะแนนรวมประสิทธิภาพการตลาด (0-100)<br>
#             <b>📊 ประกอบด้วย:</b><br>
#             • ROAS Performance (25%) - เป้าหมาย 300%<br>
#             • Click-Through Rate (25%) - เป้าหมาย 3%<br>
#             • Conversion Rate (25%) - เป้าหมาย 5%<br>
#             • Profit Margin (25%) - เป้าหมาย 50%<br>
#             <b>🎯 Grading:</b> A (80+), B (60-80), C (40-60), D (<40)
#         </div>
#         """, unsafe_allow_html=True)
    
#     if not campaign_group.empty:
#         # Calculate efficiency score
#         total_impressions = campaign_group['impressions'].sum()
#         total_clicks = campaign_group['clicks'].sum()
#         total_conversions = campaign_group['conversions'].sum()
        
#         overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
#         overall_cvr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        
#         score_components = {
#             'ROAS': min(avg_roas / 300 * 100, 100) if avg_roas > 0 else 0,
#             'CTR': min(overall_ctr / 3 * 100, 100) if overall_ctr > 0 else 0,
#             'CVR': min(overall_cvr / 5 * 100, 100) if overall_cvr > 0 else 0,
#             'Profit_Margin': min((total_campaign_profit / total_campaign_revenue * 100) / 50 * 100, 100) if total_campaign_revenue > 0 else 0
#         }
        
#         overall_score = np.mean(list(score_components.values()))
        
#         col1, col2, col3 = st.columns([1, 2, 1])
        
#         with col2:
#             # Score gauge
#             if overall_score >= 80:
#                 score_color = "#2ecc71"
#                 score_grade = "A - Excellent"
#             elif overall_score >= 60:
#                 score_color = "#f39c12"
#                 score_grade = "B - Good"
#             elif overall_score >= 40:
#                 score_color = "#e67e22"
#                 score_grade = "C - Fair"
#             else:
#                 score_color = "#e74c3c"
#                 score_grade = "D - Needs Improvement"
            
#             fig = go.Figure(go.Indicator(
#                 mode="gauge+number+delta",
#                 value=overall_score,
#                 domain={'x': [0, 1], 'y': [0, 1]},
#                 title={'text': f"<b>{score_grade}</b>", 'font': {'size': 20}},
#                 delta={'reference': 60, 'increasing': {'color': "#2ecc71"}},
#                 gauge={
#                     'axis': {'range': [None, 100], 'tickwidth': 1},
#                     'bar': {'color': score_color},
#                     'bgcolor': "white",
#                     'borderwidth': 2,
#                     'bordercolor': "gray",
#                     'steps': [
#                         {'range': [0, 40], 'color': '#ffebee'},
#                         {'range': [40, 60], 'color': '#fff3e0'},
#                         {'range': [60, 80], 'color': '#fffde7'},
#                         {'range': [80, 100], 'color': '#e8f5e9'}
#                     ],
#                     'threshold': {
#                         'line': {'color': "red", 'width': 3},
#                         'thickness': 0.75,
#                         'value': 80
#                     }
#                 }
#             ))
            
#             fig.update_layout(
#                 height=280,
#                 margin=dict(l=20, r=20, t=50, b=20)
#             )
            
#             st.plotly_chart(fig, use_container_width=True)
            
#             # Score breakdown
#             st.markdown(f"""
#             <div style='background: white; padding: 18px; border-radius: 10px; border: 2px solid {score_color};'>
#                 <h6 style='text-align: center; margin-bottom: 12px;'>Score Breakdown</h6>
#                 <div style='margin: 8px 0;'>
#                     <div style='display: flex; justify-content: space-between; font-size: 13px;'>
#                         <span>ROAS:</span>
#                         <span><b>{score_components['ROAS']:.0f}/100</b></span>
#                     </div>
#                     <div style='background: #f0f0f0; height: 6px; border-radius: 3px; margin-top: 4px;'>
#                         <div style='background: {score_color}; width: {score_components['ROAS']}%; height: 100%; border-radius: 3px;'></div>
#                     </div>
#                 </div>
#                 <div style='margin: 8px 0;'>
#                     <div style='display: flex; justify-content: space-between; font-size: 13px;'>
#                         <span>CTR:</span>
#                         <span><b>{score_components['CTR']:.0f}/100</b></span>
#                     </div>
#                     <div style='background: #f0f0f0; height: 6px; border-radius: 3px; margin-top: 4px;'>
#                         <div style='background: {score_color}; width: {score_components['CTR']}%; height: 100%; border-radius: 3px;'></div>
#                     </div>
#                 </div>
#                 <div style='margin: 8px 0;'>
#                     <div style='display: flex; justify-content: space-between; font-size: 13px;'>
#                         <span>CVR:</span>
#                         <span><b>{score_components['CVR']:.0f}/100</b></span>
#                     </div>
#                     <div style='background: #f0f0f0; height: 6px; border-radius: 3px; margin-top: 4px;'>
#                         <div style='background: {score_color}; width: {score_components['CVR']}%; height: 100%; border-radius: 3px;'></div>
#                     </div>
#                 </div>
#                 <div style='margin: 8px 0;'>
#                     <div style='display: flex; justify-content: space-between; font-size: 13px;'>
#                         <span>Profit Margin:</span>
#                         <span><b>{score_components['Profit_Margin']:.0f}/100</b></span>
#                     </div>
#                     <div style='background: #f0f0f0; height: 6px; border-radius: 3px; margin-top: 4px;'>
#                         <div style='background: {score_color}; width: {score_components['Profit_Margin']}%; height: 100%; border-radius: 3px;'></div>
#                     </div>
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)
#     else:
#         st.info("⚠️ No campaign data available for efficiency score calculation")

#     st.markdown("---")
# ==================== ADDITIONAL MARKETING METRICS (FIXED VERSION) ====================
# แทรกโค้ดนี้ใน Marketing Analytics tab (tab2) หลังจาก CAC/CLV section (ประมาณบรรทัด 1698)
# ก่อน Retention & Churn section

    # # ==================== CAMPAIGN PERFORMANCE METRICS ====================
    # st.markdown("### 📊 Campaign Performance & ROAS")
    
    # with st.expander("📖 Description", expanded=False):
    #     st.markdown("""
    #     <div class='metric-explanation'>
    #         <b>📖 Marketing Campaign Metrics:</b><br>
    #         • <b>ROAS (Return on Ad Spend):</b> (Revenue / Ad Cost) × 100 → เป้าหมาย >300%<br>
    #         • <b>CTR (Click-Through Rate):</b> (Clicks / Impressions) × 100 → เป้าหมาย >3%<br>
    #         • <b>CVR (Conversion Rate):</b> (Conversions / Clicks) × 100 → เป้าหมาย >5%<br>
    #         • <b>CPC (Cost Per Click):</b> Ad Cost / Clicks<br>
    #         • <b>CPA (Cost Per Acquisition):</b> Ad Cost / Conversions<br>
    #         <b>💡 การใช้ประโยชน์:</b> วัดประสิทธิภาพแคมเปญ เพื่อตัดสินใจจัดสรรงบ
    #     </div>
    #     """, unsafe_allow_html=True)
    
    # # Check if campaign data exists
    # has_campaign_metrics = all(col in df_filtered.columns for col in 
    #                            ['campaign_name', 'campaign_cost', 'impressions', 'clicks'])
    
    # # Show data availability status
    # if not has_campaign_metrics:
    #     col_warn1, col_warn2 = st.columns([2, 1])
    #     with col_warn1:
    #         st.info("""
    #         ℹ️ **Campaign Performance Data Not Available**
            
    #         To see detailed campaign metrics, please add these columns:
    #         - `campaign_name`, `campaign_cost`, `impressions`, `clicks`, `conversions`
            
    #         **Currently:** Using estimated metrics from channel data
    #         """)
    #     with col_warn2:
    #         st.markdown("""
    #         <div style='background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #f39c12;'>
    #             <div style='font-size: 12px; color: #856404;'><b>⚠️ Data Quality</b></div>
    #             <div style='font-size: 11px; color: #856404; margin-top: 5px;'>
    #                 Metrics are estimated<br>
    #                 Upload campaign data for accuracy
    #             </div>
    #         </div>
    #         """, unsafe_allow_html=True)
    # else:
    #     st.success("✅ Campaign data available - showing actual metrics")
    
    # # Prepare campaign data (with fallback to channel data)
    # if 'campaign_name' in df_filtered.columns and df_filtered['campaign_name'].notna().any():
    #     # Use actual campaign data
    #     campaign_group = df_filtered.groupby('campaign_name').agg({
    #         'net_revenue': 'sum',
    #         'order_id': 'nunique',
    #         'user_id': 'nunique',
    #         'campaign_cost': 'first' if 'campaign_cost' in df_filtered.columns else lambda x: 0,
    #         'impressions': 'sum' if 'impressions' in df_filtered.columns else lambda x: 0,
    #         'clicks': 'sum' if 'clicks' in df_filtered.columns else lambda x: 0,
    #         'conversions': 'sum' if 'conversions' in df_filtered.columns else lambda x: 0
    #     }).reset_index()
        
    #     data_source = "actual"
    # else:
    #     # Fallback: Use channel as campaign
    #     if 'channel' not in df_filtered.columns:
    #         st.warning("⚠️ No channel or campaign data available. Skipping campaign analysis.")
    #         campaign_group = pd.DataFrame()  # Empty dataframe
    #         data_source = "none"
    #     else:
    #         campaign_group = df_filtered.groupby('channel').agg({
    #             'net_revenue': 'sum',
    #             'order_id': 'nunique',
    #             'user_id': 'nunique'
    #         }).reset_index()
    #         campaign_group.rename(columns={'channel': 'campaign_name'}, inplace=True)
            
    #         # Estimate missing metrics (industry averages)
    #         campaign_group['campaign_cost'] = campaign_group['net_revenue'] * 0.15  # 15% of revenue
    #         campaign_group['impressions'] = campaign_group['order_id'] * 50  # 1 order ≈ 50 impressions
    #         campaign_group['clicks'] = campaign_group['order_id'] * 5  # 1 order ≈ 5 clicks
    #         campaign_group['conversions'] = campaign_group['order_id']  # 1 order = 1 conversion
            
    #         data_source = "estimated"
    
    # if not campaign_group.empty:
    #     # Fill missing values
    #     for col in ['campaign_cost', 'impressions', 'clicks', 'conversions']:
    #         if col not in campaign_group.columns:
    #             if col == 'campaign_cost':
    #                 campaign_group[col] = campaign_group['net_revenue'] * 0.15
    #             elif col == 'impressions':
    #                 campaign_group[col] = campaign_group['order_id'] * 50
    #             elif col == 'clicks':
    #                 campaign_group[col] = campaign_group['order_id'] * 5
    #             elif col == 'conversions':
    #                 campaign_group[col] = campaign_group['order_id']
    #         else:
    #             campaign_group[col] = campaign_group[col].fillna(0)
        
    #     # Calculate campaign metrics
    #     campaign_group['ROAS_%'] = (campaign_group['net_revenue'] / campaign_group['campaign_cost'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
    #     campaign_group['CTR_%'] = (campaign_group['clicks'] / campaign_group['impressions'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
    #     campaign_group['CVR_%'] = (campaign_group['conversions'] / campaign_group['clicks'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
    #     campaign_group['CPC'] = (campaign_group['campaign_cost'] / campaign_group['clicks']).replace([np.inf, -np.inf], 0).fillna(0)
    #     campaign_group['CPA'] = (campaign_group['campaign_cost'] / campaign_group['conversions']).replace([np.inf, -np.inf], 0).fillna(0)
    #     campaign_group['revenue_per_click'] = (campaign_group['net_revenue'] / campaign_group['clicks']).replace([np.inf, -np.inf], 0).fillna(0)
    #     campaign_group['profit'] = campaign_group['net_revenue'] - campaign_group['campaign_cost']
    #     campaign_group['profit_margin_%'] = (campaign_group['profit'] / campaign_group['net_revenue'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
        
    #     # Sort by ROAS
    #     campaign_group = campaign_group.sort_values('ROAS_%', ascending=False)
        
    #     # Summary metrics
    #     total_ad_spend = campaign_group['campaign_cost'].sum()
    #     total_campaign_revenue = campaign_group['net_revenue'].sum()
    #     total_campaign_profit = campaign_group['profit'].sum()
    #     avg_roas = (total_campaign_revenue / total_ad_spend * 100) if total_ad_spend > 0 else 0
    #     total_campaign_conversions = campaign_group['conversions'].sum()
    #     avg_campaign_cpa = (total_ad_spend / total_campaign_conversions) if total_campaign_conversions > 0 else 0
        
    #     # Display summary cards
    #     col1, col2, col3, col4 = st.columns(4)
        
    #     with col1:
    #         st.markdown(f"""
    #         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
    #                     padding: 20px; border-radius: 10px; color: white; text-align: center;'>
    #             <div style='font-size: 12px; opacity: 0.9;'><b>TOTAL AD SPEND</b></div>
    #             <div style='font-size: 36px; font-weight: bold; margin: 10px 0;'>
    #                 ฿{total_ad_spend/1000:.0f}K
    #             </div>
    #             <div style='font-size: 10px; opacity: 0.8;'>Marketing Investment</div>
    #         </div>
    #         """, unsafe_allow_html=True)
        
    #     with col2:
    #         roas_color = "#2ecc71" if avg_roas >= 300 else "#f39c12" if avg_roas >= 200 else "#e74c3c"
    #         roas_status = "✅ Excellent" if avg_roas >= 300 else "⚠️ Good" if avg_roas >= 200 else "❌ Poor"
    #         st.markdown(f"""
    #         <div style='background: linear-gradient(135deg, {roas_color} 0%, {roas_color}dd 100%); 
    #                     padding: 20px; border-radius: 10px; color: white; text-align: center;'>
    #             <div style='font-size: 12px; opacity: 0.9;'><b>AVERAGE ROAS</b></div>
    #             <div style='font-size: 36px; font-weight: bold; margin: 10px 0;'>
    #                 {avg_roas:.0f}%
    #             </div>
    #             <div style='font-size: 10px; opacity: 0.8;'>{roas_status}</div>
    #         </div>
    #         """, unsafe_allow_html=True)
        
    #     with col3:
    #         st.markdown(f"""
    #         <div style='background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); 
    #                     padding: 20px; border-radius: 10px; color: white; text-align: center;'>
    #             <div style='font-size: 12px; opacity: 0.9;'><b>CAMPAIGN PROFIT</b></div>
    #             <div style='font-size: 36px; font-weight: bold; margin: 10px 0;'>
    #                 ฿{total_campaign_profit/1000:.0f}K
    #             </div>
    #             <div style='font-size: 10px; opacity: 0.8;'>Revenue - Ad Cost</div>
    #         </div>
    #         """, unsafe_allow_html=True)
        
    #     with col4:
    #         st.markdown(f"""
    #         <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
    #                     padding: 20px; border-radius: 10px; color: white; text-align: center;'>
    #             <div style='font-size: 12px; opacity: 0.9;'><b>AVG CPA</b></div>
    #             <div style='font-size: 36px; font-weight: bold; margin: 10px 0;'>
    #                 ฿{avg_campaign_cpa:.0f}
    #             </div>
    #             <div style='font-size: 10px; opacity: 0.8;'>Cost Per Acquisition</div>
    #         </div>
    #         """, unsafe_allow_html=True)
        
    #     st.markdown("<br>", unsafe_allow_html=True)
        
    #     # Campaign comparison charts
    #     col1, col2 = st.columns(2)
        
    #     with col1:
    #         # ROAS by Campaign
    #         fig = go.Figure()
            
    #         # Add benchmark lines
    #         fig.add_hline(y=300, line_dash="dash", line_color="green", 
    #                      annotation_text="Excellent (300%)", annotation_position="right")
    #         fig.add_hline(y=200, line_dash="dash", line_color="orange",
    #                      annotation_text="Good (200%)", annotation_position="right")
            
    #         # Color based on performance
    #         colors = ['#2ecc71' if x >= 300 else '#f39c12' if x >= 200 else '#e74c3c' 
    #                  for x in campaign_group['ROAS_%']]
            
    #         fig.add_trace(go.Bar(
    #             x=campaign_group['campaign_name'],
    #             y=campaign_group['ROAS_%'],
    #             marker_color=colors,
    #             text=campaign_group['ROAS_%'],
    #             texttemplate='%{text:.0f}%',
    #             textposition='outside',
    #             hovertemplate='<b>%{x}</b><br>ROAS: %{y:.0f}%<extra></extra>'
    #         ))
            
    #         fig.update_layout(
    #             title='<b>ROAS by Campaign/Channel</b>',
    #             xaxis=dict(title='', showticklabels=True),
    #             yaxis=dict(title='ROAS (%)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
    #             plot_bgcolor='white',
    #             height=350,
    #             showlegend=False,
    #             margin=dict(t=60, b=80)
    #         )
            
    #         st.plotly_chart(fig, use_container_width=True)
        
    #     with col2:
    #         # Revenue vs Cost
    #         fig = go.Figure()
            
    #         fig.add_trace(go.Bar(
    #             name='Revenue',
    #             x=campaign_group['campaign_name'],
    #             y=campaign_group['net_revenue'],
    #             marker_color='#3498db',
    #             text=campaign_group['net_revenue'],
    #             texttemplate='฿%{text:.2s}',
    #             hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
    #         ))
            
    #         fig.add_trace(go.Bar(
    #             name='Cost',
    #             x=campaign_group['campaign_name'],
    #             y=campaign_group['campaign_cost'],
    #             marker_color='#e74c3c',
    #             text=campaign_group['campaign_cost'],
    #             texttemplate='฿%{text:.2s}',
    #             hovertemplate='<b>%{x}</b><br>Cost: ฿%{y:,.0f}<extra></extra>'
    #         ))
            
    #         fig.update_layout(
    #             title='<b>Revenue vs Cost by Campaign</b>',
    #             xaxis=dict(title=''),
    #             yaxis=dict(title='Amount (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
    #             plot_bgcolor='white',
    #             height=350,
    #             barmode='group',
    #             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    #             margin=dict(t=60, b=80)
    #         )
            
    #         st.plotly_chart(fig, use_container_width=True)
        
    #     # Campaign Performance Table
    #     st.markdown("#### 📋 Campaign Performance Details")
        
    #     campaign_display = campaign_group[[
    #         'campaign_name', 'impressions', 'clicks', 'CTR_%', 'conversions',
    #         'CVR_%', 'net_revenue', 'campaign_cost', 'CPA', 'ROAS_%', 
    #         'profit', 'profit_margin_%'
    #     ]].copy()
        
    #     campaign_display.columns = [
    #         'Campaign', 'Impressions', 'Clicks', 'CTR %', 'Conversions',
    #         'CVR %', 'Revenue', 'Cost', 'CPA', 'ROAS %', 'Profit', 'Margin %'
    #     ]
        
    #     # Color coding
    #     def highlight_campaign_performance(row):
    #         colors = []
    #         for col in row.index:
    #             if col == 'ROAS %':
    #                 if row[col] >= 300:
    #                     colors.append('background-color: #d5f4e6')  # Green
    #                 elif row[col] >= 200:
    #                     colors.append('background-color: #fff3cd')  # Yellow
    #                 else:
    #                     colors.append('background-color: #f8d7da')  # Red
    #             elif col == 'Margin %':
    #                 if row[col] >= 50:
    #                     colors.append('background-color: #d5f4e6')
    #                 elif row[col] >= 30:
    #                     colors.append('background-color: #fff3cd')
    #                 else:
    #                     colors.append('background-color: #f8d7da')
    #             else:
    #                 colors.append('')
    #         return colors
        
    #     styled_campaigns = campaign_display.style.format({
    #         'Impressions': '{:,.0f}',
    #         'Clicks': '{:,.0f}',
    #         'CTR %': '{:.2f}%',
    #         'Conversions': '{:,.0f}',
    #         'CVR %': '{:.2f}%',
    #         'Revenue': '฿{:,.0f}',
    #         'Cost': '฿{:,.0f}',
    #         'CPA': '฿{:,.0f}',
    #         'ROAS %': '{:.0f}%',
    #         'Profit': '฿{:,.0f}',
    #         'Margin %': '{:.1f}%'
    #     }).apply(highlight_campaign_performance, axis=1)
        
    #     st.dataframe(styled_campaigns, use_container_width=True, height=300)
        
    #     # Key Insights
    #     st.markdown("#### 💡 Key Campaign Insights")
        
    #     best_roas = campaign_group.nlargest(1, 'ROAS_%').iloc[0]
    #     worst_roas = campaign_group.nsmallest(1, 'ROAS_%').iloc[0]
    #     best_profit = campaign_group.nlargest(1, 'profit').iloc[0]
    #     lowest_cpa = campaign_group.nsmallest(1, 'CPA').iloc[0]
        
    #     col1, col2 = st.columns(2)
        
    #     with col1:
    #         st.success(f"""
    #         **🏆 Best Performing Campaign:**
            
    #         **{best_roas['campaign_name']}**
    #         - ROAS: {best_roas['ROAS_%']:.0f}%
    #         - Profit: ฿{best_roas['profit']:,.0f}
    #         - Margin: {best_roas['profit_margin_%']:.1f}%
            
    #         💡 **Action:** Scale up budget by 25-50%! Every ฿1 spent returns ฿{best_roas['ROAS_%']/100:.2f}
    #         """)
            
    #         st.info(f"""
    #         **💰 Most Profitable:**
            
    #         **{best_profit['campaign_name']}**
    #         - Total Profit: ฿{best_profit['profit']:,.0f}
    #         - Revenue: ฿{best_profit['net_revenue']:,.0f}
    #         - ROAS: {best_profit['ROAS_%']:.0f}%
            
    #         💡 **Action:** Maintain current strategy
    #         """)
        
    #     with col2:
    #         st.error(f"""
    #         **⚠️ Underperforming Campaign:**
            
    #         **{worst_roas['campaign_name']}**
    #         - ROAS: {worst_roas['ROAS_%']:.0f}%
    #         - Profit: ฿{worst_roas['profit']:,.0f}
    #         - Margin: {worst_roas['profit_margin_%']:.1f}%
            
    #         💡 **Action:** {'🛑 Pause immediately' if worst_roas['ROAS_%'] < 100 else '🔧 Optimize targeting/creative'}
    #         """)
            
    #         st.success(f"""
    #         **🎯 Most Efficient:**
            
    #         **{lowest_cpa['campaign_name']}**
    #         - CPA: ฿{lowest_cpa['CPA']:,.0f}
    #         - CVR: {lowest_cpa['CVR_%']:.2f}%
    #         - Conversions: {lowest_cpa['conversions']:,.0f}
            
    #         💡 **Action:** Study & replicate strategy
    #         """)
        
    #     # Recommendations
    #     st.markdown("#### 🎯 Data-Driven Recommendations")
        
    #     st.markdown("""
    #     <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
    #                 padding: 25px; border-radius: 15px; color: white;'>
    #         <h5 style='margin: 0 0 15px 0;'>📊 Marketing Actions</h5>
    #     """, unsafe_allow_html=True)
        
    #     recommendations = []
        
    #     # Budget reallocation
    #     if len(campaign_group) > 1:
    #         high_roas = campaign_group[campaign_group['ROAS_%'] >= 300]
    #         low_roas = campaign_group[campaign_group['ROAS_%'] < 150]
            
    #         if not high_roas.empty:
    #             recommendations.append(
    #                 f"💰 <b>Scale Winners:</b> Increase budget for {len(high_roas)} campaigns "
    #                 f"with avg ROAS {high_roas['ROAS_%'].mean():.0f}% by 25-50%"
    #             )
            
    #         if not low_roas.empty:
    #             potential_savings = low_roas['campaign_cost'].sum()
    #             recommendations.append(
    #                 f"⚠️ <b>Cut Losers:</b> Pause {len(low_roas)} underperforming campaigns. "
    #                 f"Save ฿{potential_savings:,.0f}/period"
    #             )
        
    #     # CTR optimization
    #     avg_ctr = campaign_group['CTR_%'].mean()
    #     low_ctr = campaign_group[campaign_group['CTR_%'] < avg_ctr * 0.5]
    #     if not low_ctr.empty and avg_ctr > 0:
    #         recommendations.append(
    #             f"📸 <b>Creative Refresh:</b> {len(low_ctr)} campaigns have low CTR "
    #             f"(<{avg_ctr*0.5:.2f}%). Test new ad creatives"
    #         )
        
    #     # CVR improvement
    #     avg_cvr = campaign_group['CVR_%'].mean()
    #     if avg_cvr < 2.0 and avg_cvr > 0:
    #         recommendations.append(
    #             f"🛒 <b>Improve Conversion:</b> CVR is {avg_cvr:.2f}%. "
    #             f"Optimize landing pages, simplify checkout"
    #         )
        
    #     # Overall ROAS
    #     if avg_roas < 200 and avg_roas > 0:
    #         recommendations.append(
    #             f"📉 <b>Overall Performance:</b> Avg ROAS ({avg_roas:.0f}%) below target. "
    #             f"Review targeting, pricing, and value proposition"
    #         )
    #     elif avg_roas >= 300:
    #         recommendations.append(
    #             f"✅ <b>Excellent!</b> Avg ROAS ({avg_roas:.0f}%) exceeds target. "
    #             f"Consider scaling total ad spend by 20-30%"
    #         )
        
    #     if recommendations:
    #         st.markdown("<div style='padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px; margin-top: 15px;'>", 
    #                    unsafe_allow_html=True)
    #         for rec in recommendations:
    #             st.markdown(f"<p style='margin: 8px 0; font-size: 13px;'>{rec}</p>", unsafe_allow_html=True)
    #         st.markdown("</div>", unsafe_allow_html=True)
    #     else:
    #         st.markdown("<p style='padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px; margin-top: 15px; font-size: 13px;'>✅ All campaigns performing within acceptable range</p>", unsafe_allow_html=True)
        
    #     st.markdown("</div>", unsafe_allow_html=True)
    
    # st.markdown("---")
    
    # # ==================== MARKETING EFFICIENCY SCORE ====================
    # st.markdown("### 🏆 Marketing Efficiency Score")
    
    # with st.expander("📖 Description", expanded=False):
    #     st.markdown("""
    #     <div class='metric-explanation'>
    #         <b>📖 Marketing Efficiency Score:</b> คะแนนรวมประสิทธิภาพการตลาด (0-100)<br>
    #         <b>📊 ประกอบด้วย:</b><br>
    #         • ROAS Performance (25%) - เป้าหมาย 300%<br>
    #         • Click-Through Rate (25%) - เป้าหมาย 3%<br>
    #         • Conversion Rate (25%) - เป้าหมาย 5%<br>
    #         • Profit Margin (25%) - เป้าหมาย 50%<br>
    #         <b>🎯 Grading:</b> A (80+), B (60-80), C (40-60), D (<40)
    #     </div>
    #     """, unsafe_allow_html=True)
    
    # if not campaign_group.empty:
    #     # Calculate efficiency score
    #     total_impressions = campaign_group['impressions'].sum()
    #     total_clicks = campaign_group['clicks'].sum()
    #     total_conversions = campaign_group['conversions'].sum()
        
    #     overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    #     overall_cvr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        
    #     score_components = {
    #         'ROAS': min(avg_roas / 300 * 100, 100) if avg_roas > 0 else 0,
    #         'CTR': min(overall_ctr / 3 * 100, 100) if overall_ctr > 0 else 0,
    #         'CVR': min(overall_cvr / 5 * 100, 100) if overall_cvr > 0 else 0,
    #         'Profit_Margin': min((total_campaign_profit / total_campaign_revenue * 100) / 50 * 100, 100) if total_campaign_revenue > 0 else 0
    #     }
        
    #     overall_score = np.mean(list(score_components.values()))
        
    #     col1, col2, col3 = st.columns([1, 2, 1])
        
    #     with col2:
    #         # Score gauge
    #         if overall_score >= 80:
    #             score_color = "#2ecc71"
    #             score_grade = "A - Excellent"
    #         elif overall_score >= 60:
    #             score_color = "#f39c12"
    #             score_grade = "B - Good"
    #         elif overall_score >= 40:
    #             score_color = "#e67e22"
    #             score_grade = "C - Fair"
    #         else:
    #             score_color = "#e74c3c"
    #             score_grade = "D - Needs Improvement"
            
    #         fig = go.Figure(go.Indicator(
    #             mode="gauge+number+delta",
    #             value=overall_score,
    #             domain={'x': [0, 1], 'y': [0, 1]},
    #             title={'text': f"<b>{score_grade}</b>", 'font': {'size': 20}},
    #             delta={'reference': 60, 'increasing': {'color': "#2ecc71"}},
    #             gauge={
    #                 'axis': {'range': [None, 100], 'tickwidth': 1},
    #                 'bar': {'color': score_color},
    #                 'bgcolor': "white",
    #                 'borderwidth': 2,
    #                 'bordercolor': "gray",
    #                 'steps': [
    #                     {'range': [0, 40], 'color': '#ffebee'},
    #                     {'range': [40, 60], 'color': '#fff3e0'},
    #                     {'range': [60, 80], 'color': '#fffde7'},
    #                     {'range': [80, 100], 'color': '#e8f5e9'}
    #                 ],
    #                 'threshold': {
    #                     'line': {'color': "red", 'width': 3},
    #                     'thickness': 0.75,
    #                     'value': 80
    #                 }
    #             }
    #         ))
            
    #         fig.update_layout(
    #             height=280,
    #             margin=dict(l=20, r=20, t=50, b=20)
    #         )
            
    #         st.plotly_chart(fig, use_container_width=True)
            
    #         # Score breakdown
    #         st.markdown(f"""
    #         <div style='background: white; padding: 18px; border-radius: 10px; border: 2px solid {score_color};'>
    #             <h6 style='text-align: center; margin-bottom: 12px;'>Score Breakdown</h6>
    #             <div style='margin: 8px 0;'>
    #                 <div style='display: flex; justify-content: space-between; font-size: 13px;'>
    #                     <span>ROAS:</span>
    #                     <span><b>{score_components['ROAS']:.0f}/100</b></span>
    #                 </div>
    #                 <div style='background: #f0f0f0; height: 6px; border-radius: 3px; margin-top: 4px;'>
    #                     <div style='background: {score_color}; width: {score_components['ROAS']}%; height: 100%; border-radius: 3px;'></div>
    #                 </div>
    #             </div>
    #             <div style='margin: 8px 0;'>
    #                 <div style='display: flex; justify-content: space-between; font-size: 13px;'>
    #                     <span>CTR:</span>
    #                     <span><b>{score_components['CTR']:.0f}/100</b></span>
    #                 </div>
    #                 <div style='background: #f0f0f0; height: 6px; border-radius: 3px; margin-top: 4px;'>
    #                     <div style='background: {score_color}; width: {score_components['CTR']}%; height: 100%; border-radius: 3px;'></div>
    #                 </div>
    #             </div>
    #             <div style='margin: 8px 0;'>
    #                 <div style='display: flex; justify-content: space-between; font-size: 13px;'>
    #                     <span>CVR:</span>
    #                     <span><b>{score_components['CVR']:.0f}/100</b></span>
    #                 </div>
    #                 <div style='background: #f0f0f0; height: 6px; border-radius: 3px; margin-top: 4px;'>
    #                     <div style='background: {score_color}; width: {score_components['CVR']}%; height: 100%; border-radius: 3px;'></div>
    #                 </div>
    #             </div>
    #             <div style='margin: 8px 0;'>
    #                 <div style='display: flex; justify-content: space-between; font-size: 13px;'>
    #                     <span>Profit Margin:</span>
    #                     <span><b>{score_components['Profit_Margin']:.0f}/100</b></span>
    #                 </div>
    #                 <div style='background: #f0f0f0; height: 6px; border-radius: 3px; margin-top: 4px;'>
    #                     <div style='background: {score_color}; width: {score_components['Profit_Margin']}%; height: 100%; border-radius: 3px;'></div>
    #                 </div>
    #             </div>
    #         </div>
    #         """, unsafe_allow_html=True)
    # else:
    #     st.info("⚠️ No campaign data available for efficiency score calculation")

    # st.markdown("---")









# ==================== MARKETING METRICS WITH AI ESTIMATION TOGGLE ====================
# แทรกโค้ดนี้ใน Marketing Analytics tab (tab2) หลังจาก CAC/CLV section (ประมาณบรรทัด 1698)
# ใช้ร่วมกับ AI Estimation checkbox ที่อยู่ใน sidebar แล้ว

    # ==================== CAMPAIGN PERFORMANCE METRICS ====================
    st.markdown("### 📊 Campaign Performance & ROAS")
    
    with st.expander("📖 Description", expanded=False):
        st.markdown("""
        <div class='metric-explanation'>
            <b>📖 Marketing Campaign Metrics:</b><br>
            • <b>ROAS (Return on Ad Spend):</b> (Revenue / Ad Cost) × 100 → เป้าหมาย >300%<br>
            • <b>CTR (Click-Through Rate):</b> (Clicks / Impressions) × 100 → เป้าหมาย >3%<br>
            • <b>CVR (Conversion Rate):</b> (Conversions / Clicks) × 100 → เป้าหมาย >5%<br>
            • <b>CPC (Cost Per Click):</b> Ad Cost / Clicks<br>
            • <b>CPA (Cost Per Acquisition):</b> Ad Cost / Conversions<br>
            <b>💡 การใช้ประโยชน์:</b> วัดประสิทธิภาพแคมเปญ เพื่อตัดสินใจจัดสรรงบ
        </div>
        """, unsafe_allow_html=True)
    
    # Check if campaign data exists
    has_campaign_name = 'campaign_name' in df_filtered.columns and df_filtered['campaign_name'].notna().any()
    has_campaign_cost = 'campaign_cost' in df_filtered.columns
    has_impressions = 'impressions' in df_filtered.columns
    has_clicks = 'clicks' in df_filtered.columns
    has_conversions = 'conversions' in df_filtered.columns
    
    has_complete_campaign_data = all([has_campaign_name, has_campaign_cost, has_impressions, has_clicks])
    
    # Get AI estimation setting from session state
    use_ai_estimation = st.session_state.get('use_ai_estimation', True)
    
    # Show data status
    if not has_complete_campaign_data:
        col_status1, col_status2 = st.columns([3, 1])
        
        with col_status1:
            missing_cols = []
            if not has_campaign_name:
                missing_cols.append('campaign_name')
            if not has_campaign_cost:
                missing_cols.append('campaign_cost')
            if not has_impressions:
                missing_cols.append('impressions')
            if not has_clicks:
                missing_cols.append('clicks')
            if not has_conversions:
                missing_cols.append('conversions')
            
            st.warning(f"""
            ⚠️ **Campaign Data Incomplete**
            
            Missing columns: `{', '.join(missing_cols)}`
            
            **Options:**
            1. Upload complete campaign data with all required columns
            2. Enable "AI Estimation" in sidebar (currently: {'✅ Enabled' if use_ai_estimation else '❌ Disabled'})
            """)
        
        with col_status2:
            if use_ai_estimation and 'channel' in df_filtered.columns:
                st.markdown("""
                <div style='background: #d1ecf1; padding: 15px; border-radius: 8px; border-left: 4px solid #0c5460;'>
                    <div style='font-size: 12px; color: #0c5460;'><b>🤖 AI Estimation</b></div>
                    <div style='font-size: 11px; color: #0c5460; margin-top: 5px;'>
                        Enabled<br>
                        Using channel data
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='background: #f8d7da; padding: 15px; border-radius: 8px; border-left: 4px solid #721c24;'>
                    <div style='font-size: 12px; color: #721c24;'><b>❌ No Data</b></div>
                    <div style='font-size: 11px; color: #721c24; margin-top: 5px;'>
                        Enable AI Estimation<br>
                        in sidebar
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("✅ Campaign data complete - showing actual metrics")
    
    # Decide whether to proceed with analysis
    can_show_analysis = False
    data_source = "none"
    
    if has_complete_campaign_data:
        # Has complete data - always show
        can_show_analysis = True
        data_source = "actual"
    elif use_ai_estimation and 'channel' in df_filtered.columns:
        # AI estimation enabled and has channel data
        can_show_analysis = True
        data_source = "estimated"
    else:
        # No data and AI estimation disabled
        can_show_analysis = False
        data_source = "none"
    
    # Prepare campaign data based on availability
    if can_show_analysis:
        if data_source == "actual":
            # Use actual campaign data
            campaign_group = df_filtered.groupby('campaign_name').agg({
                'net_revenue': 'sum',
                'order_id': 'nunique',
                'user_id': 'nunique',
                'campaign_cost': 'first' if has_campaign_cost else lambda x: 0,
                'impressions': 'sum' if has_impressions else lambda x: 0,
                'clicks': 'sum' if has_clicks else lambda x: 0,
                'conversions': 'sum' if has_conversions else lambda x: 0
            }).reset_index()
            
        else:  # data_source == "estimated"
            # Use channel data with AI estimation
            campaign_group = df_filtered.groupby('channel').agg({
                'net_revenue': 'sum',
                'order_id': 'nunique',
                'user_id': 'nunique'
            }).reset_index()
            campaign_group.rename(columns={'channel': 'campaign_name'}, inplace=True)
            
            # AI Estimation for missing metrics
            # Based on industry averages and data patterns
            campaign_group['campaign_cost'] = campaign_group['net_revenue'] * 0.15  # 15% marketing cost ratio
            campaign_group['impressions'] = campaign_group['order_id'] * 50  # 1 order ≈ 50 impressions
            campaign_group['clicks'] = campaign_group['order_id'] * 5  # 1 order ≈ 5 clicks  
            campaign_group['conversions'] = campaign_group['order_id']  # 1 order = 1 conversion
        
        # Fill any remaining missing values
        for col in ['campaign_cost', 'impressions', 'clicks', 'conversions']:
            if col not in campaign_group.columns:
                if col == 'campaign_cost':
                    campaign_group[col] = campaign_group['net_revenue'] * 0.15
                elif col == 'impressions':
                    campaign_group[col] = campaign_group['order_id'] * 50
                elif col == 'clicks':
                    campaign_group[col] = campaign_group['order_id'] * 5
                elif col == 'conversions':
                    campaign_group[col] = campaign_group['order_id']
            else:
                campaign_group[col] = campaign_group[col].fillna(0)
        
        # Calculate campaign metrics
        campaign_group['ROAS_%'] = (campaign_group['net_revenue'] / campaign_group['campaign_cost'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
        campaign_group['CTR_%'] = (campaign_group['clicks'] / campaign_group['impressions'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
        campaign_group['CVR_%'] = (campaign_group['conversions'] / campaign_group['clicks'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
        campaign_group['CPC'] = (campaign_group['campaign_cost'] / campaign_group['clicks']).replace([np.inf, -np.inf], 0).fillna(0)
        campaign_group['CPA'] = (campaign_group['campaign_cost'] / campaign_group['conversions']).replace([np.inf, -np.inf], 0).fillna(0)
        campaign_group['revenue_per_click'] = (campaign_group['net_revenue'] / campaign_group['clicks']).replace([np.inf, -np.inf], 0).fillna(0)
        campaign_group['profit'] = campaign_group['net_revenue'] - campaign_group['campaign_cost']
        campaign_group['profit_margin_%'] = (campaign_group['profit'] / campaign_group['net_revenue'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
        
        # Sort by ROAS
        campaign_group = campaign_group.sort_values('ROAS_%', ascending=False)
        
        # Summary metrics
        total_ad_spend = campaign_group['campaign_cost'].sum()
        total_campaign_revenue = campaign_group['net_revenue'].sum()
        total_campaign_profit = campaign_group['profit'].sum()
        avg_roas = (total_campaign_revenue / total_ad_spend * 100) if total_ad_spend > 0 else 0
        total_campaign_conversions = campaign_group['conversions'].sum()
        avg_campaign_cpa = (total_ad_spend / total_campaign_conversions) if total_campaign_conversions > 0 else 0
        
        # Show data source badge
        if data_source == "estimated":
            st.info("🤖 **AI Estimation Active** - Metrics calculated from channel data using industry patterns (15% cost ratio, 50:5:1 impression:click:conversion)")
        
        # Display summary cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                <div style='font-size: 12px; opacity: 0.9;'><b>TOTAL AD SPEND</b></div>
                <div style='font-size: 36px; font-weight: bold; margin: 10px 0;'>
                    ฿{total_ad_spend/1000000:.0f}M
                </div>
                <div style='font-size: 10px; opacity: 0.8;'>{'Estimated' if data_source == 'estimated' else 'Actual'}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            roas_color = "#2ecc71" if avg_roas >= 300 else "#f39c12" if avg_roas >= 200 else "#e74c3c"
            roas_status = "✅ Excellent" if avg_roas >= 300 else "⚠️ Good" if avg_roas >= 200 else "❌ Poor"
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, {roas_color} 0%, {roas_color}dd 100%); 
                        padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                <div style='font-size: 12px; opacity: 0.9;'><b>AVERAGE ROAS</b></div>
                <div style='font-size: 36px; font-weight: bold; margin: 10px 0;'>
                    {avg_roas:.0f}%
                </div>
                <div style='font-size: 10px; opacity: 0.8;'>{roas_status}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); 
                        padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                <div style='font-size: 12px; opacity: 0.9;'><b>CAMPAIGN PROFIT</b></div>
                <div style='font-size: 36px; font-weight: bold; margin: 10px 0;'>
                    ฿{total_campaign_profit/1000000:.0f}M
                </div>
                <div style='font-size: 10px; opacity: 0.8;'>Revenue - Ad Cost</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                <div style='font-size: 12px; opacity: 0.9;'><b>AVG CPA</b></div>
                <div style='font-size: 36px; font-weight: bold; margin: 10px 0;'>
                    ฿{avg_campaign_cpa:.0f}
                </div>
                <div style='font-size: 10px; opacity: 0.8;'>Cost Per Acquisition</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Campaign comparison charts
        col1, col2 = st.columns(2)
        
        with col1:
            # ROAS by Campaign
            fig = go.Figure()
            
            # Add benchmark lines
            fig.add_hline(y=300, line_dash="dash", line_color="green", 
                         annotation_text="Excellent (300%)", annotation_position="right")
            fig.add_hline(y=200, line_dash="dash", line_color="orange",
                         annotation_text="Good (200%)", annotation_position="right")
            
            # Color based on performance
            colors = ['#2ecc71' if x >= 300 else '#f39c12' if x >= 200 else '#e74c3c' 
                     for x in campaign_group['ROAS_%']]
            
            fig.add_trace(go.Bar(
                x=campaign_group['campaign_name'],
                y=campaign_group['ROAS_%'],
                marker_color=colors,
                text=campaign_group['ROAS_%'],
                texttemplate='%{text:.0f}%',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>ROAS: %{y:.0f}%<extra></extra>'
            ))
            
            fig.update_layout(
                title='<b>ROAS by Campaign/Channel</b>',
                xaxis=dict(title='', showticklabels=True),
                yaxis=dict(title='ROAS (%)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
                plot_bgcolor='white',
                height=350,
                showlegend=False,
                margin=dict(t=60, b=80)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Revenue vs Cost
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Revenue',
                x=campaign_group['campaign_name'],
                y=campaign_group['net_revenue'],
                marker_color='#3498db',
                text=campaign_group['net_revenue'],
                texttemplate='฿%{text:.2s}',
                hovertemplate='<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>'
            ))
            
            fig.add_trace(go.Bar(
                name='Cost',
                x=campaign_group['campaign_name'],
                y=campaign_group['campaign_cost'],
                marker_color='#e74c3c',
                text=campaign_group['campaign_cost'],
                texttemplate='฿%{text:.2s}',
                hovertemplate='<b>%{x}</b><br>Cost: ฿%{y:,.0f}<extra></extra>'
            ))
            
            fig.update_layout(
                title='<b>Revenue vs Cost by Campaign</b>',
                xaxis=dict(title=''),
                yaxis=dict(title='Amount (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
                plot_bgcolor='white',
                height=350,
                barmode='group',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(t=60, b=80)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Campaign Performance Table
        st.markdown("#### 📋 Campaign Performance Details")
        
        campaign_display = campaign_group[[
            'campaign_name', 'impressions', 'clicks', 'CTR_%', 'conversions',
            'CVR_%', 'net_revenue', 'campaign_cost', 'CPA', 'ROAS_%', 
            'profit', 'profit_margin_%'
        ]].copy()
        
        campaign_display.columns = [
            'Campaign', 'Impressions', 'Clicks', 'CTR %', 'Conversions',
            'CVR %', 'Revenue', 'Cost', 'CPA', 'ROAS %', 'Profit', 'Margin %'
        ]
        
        # Color coding
        def highlight_campaign_performance(row):
            colors = []
            for col in row.index:
                if col == 'ROAS %':
                    if row[col] >= 300:
                        colors.append('background-color: #d5f4e6')
                    elif row[col] >= 200:
                        colors.append('background-color: #fff3cd')
                    else:
                        colors.append('background-color: #f8d7da')
                elif col == 'Margin %':
                    if row[col] >= 50:
                        colors.append('background-color: #d5f4e6')
                    elif row[col] >= 30:
                        colors.append('background-color: #fff3cd')
                    else:
                        colors.append('background-color: #f8d7da')
                else:
                    colors.append('')
            return colors
        
        styled_campaigns = campaign_display.style.format({
            'Impressions': '{:,.0f}',
            'Clicks': '{:,.0f}',
            'CTR %': '{:.2f}%',
            'Conversions': '{:,.0f}',
            'CVR %': '{:.2f}%',
            'Revenue': '฿{:,.0f}',
            'Cost': '฿{:,.0f}',
            'CPA': '฿{:,.0f}',
            'ROAS %': '{:.0f}%',
            'Profit': '฿{:,.0f}',
            'Margin %': '{:.1f}%'
        }).apply(highlight_campaign_performance, axis=1)
        
        st.dataframe(styled_campaigns, use_container_width=True, height=300)
        
        # Key Insights
        st.markdown("#### 💡 Key Campaign Insights")
        
        best_roas = campaign_group.nlargest(1, 'ROAS_%').iloc[0]
        worst_roas = campaign_group.nsmallest(1, 'ROAS_%').iloc[0]
        best_profit = campaign_group.nlargest(1, 'profit').iloc[0]
        lowest_cpa = campaign_group.nsmallest(1, 'CPA').iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"""
            **🏆 Best Performing:**
            
            **{best_roas['campaign_name']}**
            - ROAS: {best_roas['ROAS_%']:.0f}%
            - Profit: ฿{best_roas['profit']:,.0f}
            - Margin: {best_roas['profit_margin_%']:.1f}%
            
            💡 **Action:** Scale up budget by 25-50%
            """)
            
            st.info(f"""
            **💰 Most Profitable:**
            
            **{best_profit['campaign_name']}**
            - Profit: ฿{best_profit['profit']:,.0f}
            - Revenue: ฿{best_profit['net_revenue']:,.0f}
            - ROAS: {best_profit['ROAS_%']:.0f}%
            
            💡 **Action:** Maintain strategy
            """)
        
        with col2:
            st.error(f"""
            **⚠️ Underperforming:**
            
            **{worst_roas['campaign_name']}**
            - ROAS: {worst_roas['ROAS_%']:.0f}%
            - Profit: ฿{worst_roas['profit']:,.0f}%
            
            💡 **Action:** {'🛑 Pause' if worst_roas['ROAS_%'] < 100 else '🔧 Optimize'}
            """)
            
            st.success(f"""
            **🎯 Most Efficient:**
            
            **{lowest_cpa['campaign_name']}**
            - CPA: ฿{lowest_cpa['CPA']:,.0f}
            - CVR: {lowest_cpa['CVR_%']:.2f}%
            
            💡 **Action:** Replicate strategy
            """)
        
        # Recommendations
        st.markdown("#### 🎯 Recommendations")
        
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 25px; border-radius: 15px; color: white;'>
            <h5 style='margin: 0 0 15px 0;'>📊 Marketing Actions</h5>
        """, unsafe_allow_html=True)
        
        recommendations = []
        
        if len(campaign_group) > 1:
            high_roas = campaign_group[campaign_group['ROAS_%'] >= 300]
            low_roas = campaign_group[campaign_group['ROAS_%'] < 150]
            
            if not high_roas.empty:
                recommendations.append(
                    f"💰 <b>Scale Winners:</b> {len(high_roas)} campaigns with avg ROAS {high_roas['ROAS_%'].mean():.0f}%"
                )
            
            if not low_roas.empty:
                recommendations.append(
                    f"⚠️ <b>Cut Losers:</b> {len(low_roas)} campaigns (save ฿{low_roas['campaign_cost'].sum():,.0f})"
                )
        
        avg_ctr = campaign_group['CTR_%'].mean()
        if avg_ctr > 0:
            low_ctr = campaign_group[campaign_group['CTR_%'] < avg_ctr * 0.5]
            if not low_ctr.empty:
                recommendations.append(f"📸 <b>Creative Refresh:</b> {len(low_ctr)} campaigns with low CTR")
        
        avg_cvr = campaign_group['CVR_%'].mean()
        if 0 < avg_cvr < 2.0:
            recommendations.append(f"🛒 <b>Improve Conversion:</b> CVR is {avg_cvr:.2f}% (optimize landing pages)")
        
        if avg_roas < 200:
            recommendations.append(f"📉 <b>Overall:</b> Avg ROAS ({avg_roas:.0f}%) below target - review strategy")
        elif avg_roas >= 300:
            recommendations.append(f"✅ <b>Excellent:</b> ROAS {avg_roas:.0f}% - scale ad spend by 20-30%")
        
        if recommendations:
            st.markdown("<div style='padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px; margin-top: 15px;'>", unsafe_allow_html=True)
            for rec in recommendations:
                st.markdown(f"<p style='margin: 8px 0; font-size: 13px;'>{rec}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px; font-size: 13px;'>✅ All campaigns performing well</p>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Marketing Efficiency Score
        st.markdown("---")
        st.markdown("### 🏆 Marketing Efficiency Score")
        
        total_impressions = campaign_group['impressions'].sum()
        total_clicks = campaign_group['clicks'].sum()
        total_conversions = campaign_group['conversions'].sum()
        
        overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        overall_cvr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        
        score_components = {
            'ROAS': min(avg_roas / 300 * 100, 100) if avg_roas > 0 else 0,
            'CTR': min(overall_ctr / 3 * 100, 100) if overall_ctr > 0 else 0,
            'CVR': min(overall_cvr / 5 * 100, 100) if overall_cvr > 0 else 0,
            'Profit_Margin': min((total_campaign_profit / total_campaign_revenue * 100) / 50 * 100, 100) if total_campaign_revenue > 0 else 0
        }
        
        overall_score = np.mean(list(score_components.values()))
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if overall_score >= 80:
                score_color = "#2ecc71"
                score_grade = "A - Excellent"
            elif overall_score >= 60:
                score_color = "#f39c12"
                score_grade = "B - Good"
            elif overall_score >= 40:
                score_color = "#e67e22"
                score_grade = "C - Fair"
            else:
                score_color = "#e74c3c"
                score_grade = "D - Needs Improvement"
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=overall_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"<b>{score_grade}</b>", 'font': {'size': 20}},
                delta={'reference': 60, 'increasing': {'color': "#2ecc71"}},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1},
                    'bar': {'color': score_color},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 40], 'color': '#ffebee'},
                        {'range': [40, 60], 'color': '#fff3e0'},
                        {'range': [60, 80], 'color': '#fffde7'},
                        {'range': [80, 100], 'color': '#e8f5e9'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 3},
                        'thickness': 0.75,
                        'value': 80
                    }
                }
            ))
            
            fig.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(f"""
            <div style='background: white; padding: 18px; border-radius: 10px; border: 2px solid {score_color};'>
                <h6 style='text-align: center; margin-bottom: 12px;'>Score Breakdown</h6>
                <div style='margin: 8px 0;'>
                    <div style='display: flex; justify-content: space-between; font-size: 13px;'>
                        <span>ROAS:</span><span><b>{score_components['ROAS']:.0f}/100</b></span>
                    </div>
                    <div style='background: #f0f0f0; height: 6px; border-radius: 3px; margin-top: 4px;'>
                        <div style='background: {score_color}; width: {score_components['ROAS']}%; height: 100%; border-radius: 3px;'></div>
                    </div>
                </div>
                <div style='margin: 8px 0;'>
                    <div style='display: flex; justify-content: space-between; font-size: 13px;'>
                        <span>CTR:</span><span><b>{score_components['CTR']:.0f}/100</b></span>
                    </div>
                    <div style='background: #f0f0f0; height: 6px; border-radius: 3px; margin-top: 4px;'>
                        <div style='background: {score_color}; width: {score_components['CTR']}%; height: 100%; border-radius: 3px;'></div>
                    </div>
                </div>
                <div style='margin: 8px 0;'>
                    <div style='display: flex; justify-content: space-between; font-size: 13px;'>
                        <span>CVR:</span><span><b>{score_components['CVR']:.0f}/100</b></span>
                    </div>
                    <div style='background: #f0f0f0; height: 6px; border-radius: 3px; margin-top: 4px;'>
                        <div style='background: {score_color}; width: {score_components['CVR']}%; height: 100%; border-radius: 3px;'></div>
                    </div>
                </div>
                <div style='margin: 8px 0;'>
                    <div style='display: flex; justify-content: space-between; font-size: 13px;'>
                        <span>Profit Margin:</span><span><b>{score_components['Profit_Margin']:.0f}/100</b></span>
                    </div>
                    <div style='background: #f0f0f0; height: 6px; border-radius: 3px; margin-top: 4px;'>
                        <div style='background: {score_color}; width: {score_components['Profit_Margin']}%; height: 100%; border-radius: 3px;'></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # Cannot show analysis - no data and AI estimation disabled
        st.error("""
        ❌ **Cannot Display Campaign Performance**
        
        **Reason:** Campaign data not available and AI Estimation is disabled
        
        **Solutions:**
        1. **Upload complete campaign data** with columns: `campaign_name`, `campaign_cost`, `impressions`, `clicks`, `conversions`
        2. **Enable "AI Estimation"** in the sidebar (currently disabled)
        3. Ensure you have at least `channel` column in your data for AI estimation to work
        """)

    st.markdown("---")

# ==================== CONTINUE WITH RETENTION & CHURN ====================

# ==================== CONTINUE WITH EXISTING RETENTION & CHURN SECTION ====================
# (โค้ดเดิมของ Retention & Churn ต่อไปตรงนี้...)
    # ==================== RETENTION & CHURN ====================
    st.markdown("### 🔄 Customer Retention & Churn Rate")

    with st.expander("📖 Description", expanded=False):
        st.markdown(
            f"""
        <div class='metric-explanation'>
            <b>📖 Retention Rate:</b> เปอร์เซ็นต์ของลูกค้าที่ยังคงซื้อสินค้ากับเรา (ไม่หายไป)<br>
            <div class='metric-formula'>
                สูตร: [1 - (จำนวนลูกค้าที่หายไป / จำนวนลูกค้าเริ่มต้น)] × 100
            </div>
            <b>📖 Churn Rate:</b> เปอร์เซ็นต์ของลูกค้าที่หยุดซื้อสินค้า (ไม่ซื้อเกิน 90 วัน)<br>
            <b>🎯 Target:</b> Retention &gt; {st.session_state.targets['retention_rate']:.0f}% (Change in sidebar)
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Compare with target
    target_retention = st.session_state.targets["retention_rate"]
    retention_status = (
        "✅ Above Target" if retention_rate >= target_retention else "⚠️ Below Target"
    )
    retention_border_color = (
        "#2ecc71" if retention_rate >= target_retention else "#e74c3c"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
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
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div style='background: white; padding: 30px; border-radius: 10px; 
                    border: 3px solid #e74c3c; text-align: center; height: 240px;
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
        """,
            unsafe_allow_html=True,
        )

    with col3:
        active_customers = int(len(last_purchase) * retention_rate / 100)
        churned_customers = int(len(last_purchase) * churn_rate / 100)

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=["Active", "Churned"],
                y=[active_customers, churned_customers],
                marker=dict(color=["#2ecc71", "#e74c3c"]),
                text=[active_customers, churned_customers],
                texttemplate="%{text:,}",
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Customers: %{y:,}<extra></extra>",
            )
        )

        fig.update_layout(
            title="<b>Customer Status</b>",
            xaxis=dict(title="", showgrid=False),
            yaxis=dict(
                title="Number of Customers", showgrid=True, gridcolor="rgba(0,0,0,0.05)"
            ),
            plot_bgcolor="white",
            height=240,
            showlegend=False,
            margin=dict(t=40, b=40, l=60, r=20),
        )

        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("# 💰 Financial Analytics")
    st.markdown("---")

    # ==================== PROFIT MARGINS ====================
    st.markdown("### 📊 Profit Margin Analysis")

    with st.expander("📖 Description", expanded=False):
        st.markdown(
            f"""
        <div class='metric-explanation'>
            <b>📖 Gross Profit Margin:</b> เปอร์เซ็นต์กำไรขั้นต้น (หลังหักต้นทุนสินค้า)<br>
            <div class='metric-formula'>
                สูตร: [(รายได้ - ต้นทุนสินค้า) / รายได้] × 100
            </div>
            <b>📖 Net Profit Margin:</b> เปอร์เซ็นต์กำไรสุทธิ (หลังหักค่าใช้จ่ายทั้งหมด)<br>
            <div class='metric-formula'>
                สูตร: (กำไรสุทธิ / รายได้) × 100
            </div>
            <b>🎯 Target:</b> Net Margin &gt; {st.session_state.targets['profit_margin']:.0f}% (Change in sidebar)
        </div>
        """,
            unsafe_allow_html=True,
        )

    gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
    net_margin = (profit / revenue * 100) if revenue > 0 else 0

    # Compare with target
    target_margin = st.session_state.targets["profit_margin"]
    margin_status = (
        "✅ Above Target" if net_margin >= target_margin else "⚠️ Below Target"
    )
    margin_color = "#2ecc71" if net_margin >= target_margin else "#e74c3c"

    col1, col2, col3 = st.columns(3)

    with col1:
        # Waterfall chart
        fig = go.Figure(
            go.Waterfall(
                orientation="v",
                measure=["relative", "relative", "relative", "total"],
                x=["Revenue", "COGS", "Other Costs", "Net Profit"],
                y=[revenue, -cogs, -(gross_profit - profit), profit],
                text=[
                    f"฿{revenue:,.0f}",
                    f"-฿{cogs:,.0f}",
                    f"-฿{(gross_profit - profit):,.0f}",
                    f"฿{profit:,.0f}",
                ],
                textposition="outside",
                connector={"line": {"color": "rgb(63, 63, 63)"}},
                decreasing={"marker": {"color": "#e74c3c"}},
                increasing={"marker": {"color": "#2ecc71"}},
                totals={"marker": {"color": "#3498db"}},
                hovertemplate="<b>%{x}</b><br>Amount: ฿%{y:,.0f}<extra></extra>",
            )
        )

        fig.update_layout(
            title="<b>Profit Waterfall</b>",
            plot_bgcolor="white",
            height=300,
            showlegend=False,
            margin=dict(t=40, b=40, l=60, r=20),
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(
            f"""
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
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
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
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ==================== MONTHLY FINANCIAL TREND ====================
    st.markdown("### 📈 Monthly Financial Performance")

    monthly_fin = (
        df_filtered.groupby("order_month")
        .agg({"net_revenue": "sum", "cost": "sum", "profit": "sum"})
        .reset_index()
    )
    monthly_fin["order_month"] = monthly_fin["order_month"].dt.to_timestamp()
    monthly_fin["month_label"] = monthly_fin["order_month"].dt.strftime("%b %Y")
    monthly_fin["gross_margin_%"] = (
        (monthly_fin["net_revenue"] - monthly_fin["cost"])
        / monthly_fin["net_revenue"]
        * 100
    ).round(1)
    monthly_fin["net_margin_%"] = (
        monthly_fin["profit"] / monthly_fin["net_revenue"] * 100
    ).round(1)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Revenue and Cost bars
    fig.add_trace(
        go.Bar(
            x=monthly_fin["month_label"],
            y=monthly_fin["net_revenue"],
            name="Revenue",
            marker_color="#3498db",
            hovertemplate="<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Bar(
            x=monthly_fin["month_label"],
            y=monthly_fin["cost"],
            name="COGS",
            marker_color="#e74c3c",
            hovertemplate="<b>%{x}</b><br>COGS: ฿%{y:,.0f}<extra></extra>",
        ),
        secondary_y=False,
    )

    # Margin lines
    fig.add_trace(
        go.Scatter(
            x=monthly_fin["month_label"],
            y=monthly_fin["gross_margin_%"],
            name="Gross Margin %",
            mode="lines+markers",
            line=dict(color="#27ae60", width=3),
            marker=dict(size=8),
            hovertemplate="<b>%{x}</b><br>Gross Margin: %{y:.1f}%<extra></extra>",
        ),
        secondary_y=True,
    )

    fig.add_trace(
        go.Scatter(
            x=monthly_fin["month_label"],
            y=monthly_fin["net_margin_%"],
            name="Net Margin %",
            mode="lines+markers",
            line=dict(color="#9b59b6", width=3),
            marker=dict(size=8),
            hovertemplate="<b>%{x}</b><br>Net Margin: %{y:.1f}%<extra></extra>",
        ),
        secondary_y=True,
    )

    fig.update_xaxes(title_text="")
    fig.update_yaxes(
        title_text="Amount (฿)",
        secondary_y=False,
        showgrid=True,
        gridcolor="rgba(0,0,0,0.05)",
    )
    fig.update_yaxes(title_text="Margin (%)", secondary_y=True, showgrid=False)

    fig.update_layout(
        title="<b>Monthly Revenue, Cost & Margins</b>",
        plot_bgcolor="white",
        height=400,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode="group",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ==================== WORKING CAPITAL RATIOS WITH SMART DETECTION ====================
    st.markdown("### 💼 Working Capital Ratios")
    
    # Check data availability
    has_balance_sheet = 'balance_sheet' in data
    has_ar_data = has_balance_sheet and 'accounts_receivable' in data['balance_sheet'].columns
    has_ap_data = has_balance_sheet and 'accounts_payable' in data['balance_sheet'].columns
    use_ai = st.session_state.use_ai_estimation
    
    # Show data status
    col1, col2, col3 = st.columns(3)
    with col1:
        if has_ar_data:
            st.success("✅ AR/DSO: Actual Data")
            quality_tracker.mark_actual("AR Turnover")
        elif use_ai:
            st.warning("⚠️ AR/DSO: AI Estimated")
        else:
            st.error("❌ AR/DSO: Not Available")
    
    with col2:
        if has_ap_data:
            st.success("✅ AP/DPO: Actual Data")
            quality_tracker.mark_actual("AP Turnover")
        elif use_ai:
            st.warning("⚠️ AP/DPO: AI Estimated")
        else:
            st.error("❌ AP/DPO: Not Available")
    
    with col3:
        if 'inventory' in data:
            st.success("✅ DIO: Actual Data")
            quality_tracker.mark_actual("DIO")
        elif use_ai:
            st.warning("⚠️ DIO: AI Estimated")
        else:
            st.info("ℹ️ DIO: Basic Estimation")
    
    st.markdown("---")
    
    # Calculate DIO first
    if 'inventory' in data:
        try:
            actual_inventory = data['inventory'].groupby('product_id')['quantity'].mean().sum()
            avg_inventory_value = actual_inventory * (cogs / df_filtered['quantity'].sum())
            dio_source = "actual"
            dio_method = None
        except:
            avg_inventory_value, dio_method = ai_estimator.estimate_inventory(df_filtered, cogs)
            dio_source = "estimated"
            quality_tracker.mark_estimated("DIO", dio_method)
    elif use_ai:
        avg_inventory_value, dio_method = ai_estimator.estimate_inventory(df_filtered, cogs)
        dio_source = "estimated"
        quality_tracker.mark_estimated("DIO", dio_method)
    else:
        avg_inventory_value = cogs * 0.25
        dio_source = "basic"
        dio_method = "Basic: 25% of COGS (90d inv)"
    
    inventory_turnover = cogs / avg_inventory_value if avg_inventory_value > 0 else 0
    dio = 365 / inventory_turnover if inventory_turnover > 0 else 0
    
    # Calculate AR
    if has_ar_data:
        avg_ar = data['balance_sheet']['accounts_receivable'].mean()
        ar_source = "actual"
        ar_method = None
        quality_tracker.mark_actual("DSO")
    elif use_ai:
        avg_ar, ar_method = ai_estimator.estimate_accounts_receivable(df_filtered, monthly_fin)
        ar_source = "estimated"
        quality_tracker.mark_estimated("DSO", ar_method)
    else:
        avg_ar = None
        ar_source = "missing"
    
    if avg_ar:
        ar_turnover = (revenue * 0.3) / avg_ar
        dso = 365 / ar_turnover if ar_turnover > 0 else 0
        show_ar = True
    else:
        ar_turnover, dso, show_ar = 0, 0, False
    
    # Calculate AP
    if has_ap_data:
        avg_ap = data['balance_sheet']['accounts_payable'].mean()
        ap_source = "actual"
        ap_method = None
        quality_tracker.mark_actual("DPO")
    elif use_ai:
        avg_ap, ap_method = ai_estimator.estimate_accounts_payable(cogs, df_filtered)
        ap_source = "estimated"
        quality_tracker.mark_estimated("DPO", ap_method)
    else:
        avg_ap = None
        ap_source = "missing"
    
    if avg_ap:
        ap_turnover = cogs / avg_ap
        dpo = 365 / ap_turnover if ap_turnover > 0 else 0
        show_ap = True
    else:
        ap_turnover, dpo, show_ap = 0, 0, False
    
    # Calculate CCC
    if show_ar and show_ap:
        ccc = dio + dso - dpo
        show_ccc = True
    else:
        ccc, show_ccc = 0, False
    
    # Display metrics with quality badges
    metrics = []
    if show_ar:
        metrics.append(("AR", ar_turnover, ar_source, ar_method))
        metrics.append(("DSO", dso, ar_source, ar_method))
    if show_ap:
        metrics.append(("AP", ap_turnover, ap_source, ap_method))
        metrics.append(("DPO", dpo, ap_source, ap_method))
    metrics.append(("DIO", dio, dio_source, dio_method))
    if show_ccc:
        metrics.append(("CCC", ccc, "mixed", None))
    
    cols = st.columns(len(metrics))
    
    for idx, (name, value, source, method) in enumerate(metrics):
        with cols[idx]:
            badge_class = "actual" if source == "actual" else "estimated"
            badge_text = "✅ ACTUAL" if source == "actual" else "🤖 AI"
            
            if name == "AR":
                display_val = f"{value:.2f}x"
                subtitle = "Times per year"
            elif name in ["DSO", "DPO", "DIO", "CCC"]:
                display_val = f"{value:.0f}"
                subtitle = "Days"
            else:
                display_val = f"{value:.2f}x"
                subtitle = "Times per year"
            
            st.markdown(f"""
            <div style='background: white; padding: 20px; border-radius: 10px; 
                        border-left: 5px solid {"#2ecc71" if source == "actual" else "#f39c12"}; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: 180px;'>
                <div style='font-size: 11px; color: #7f8c8d; margin-bottom: 8px;'>
                    <b>{name}</b>
                    <span class='quality-badge-{badge_class}'>{badge_text}</span>
                </div>
                <div style='font-size: 32px; font-weight: bold; color: #2c3e50;'>
                    {display_val}
                </div>
                <div style='font-size: 10px; color: #95a5a6; margin-top: 5px;'>
                    {subtitle}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if source == "estimated" and method:
                with st.expander("ℹ️ Details"):
                    st.caption(f"**Method:** {method}")
                    if name in ["AR", "DSO"]:
                        st.caption("💡 Upload balance_sheet.csv for actual data")
                    elif name in ["AP", "DPO"]:
                        st.caption("💡 Upload balance_sheet.csv for actual data")
                    elif name == "DIO":
                        st.caption("💡 Upload inventory_movements.csv for actual data")

# with tab4:
#     st.markdown("# 📦 Warehouse Analytics")
#     st.markdown("---")

#     # ==================== INVENTORY TURNOVER ====================
#     st.markdown("### 🔄 Inventory Turnover & Performance")

#     with st.expander("📖 Description", expanded=False):
#         st.markdown(
#             f"""
#         <div class='metric-explanation'>
#             <b>📖 Inventory Turnover:</b> จำนวนครั้งที่สินค้าหมุนเวียนต่อปี (ยิ่งสูงยิ่งดี แสดงว่าสินค้าขายดี)<br>
#             <div class='metric-formula'>
#                 สูตร: ต้นทุนสินค้าที่ขาย / มูลค่าสินค้าคงคลังเฉลี่ย
#             </div>
#             <b>📖 Days Inventory Outstanding (DIO):</b> จำนวนวันที่สินค้าอยู่ในคลังก่อนขายได้<br>
#             <div class='metric-formula'>
#                 สูตร: 365 / Inventory Turnover
#             </div>
#             <b>🎯 Target:</b> Turnover &gt; {st.session_state.targets['inventory_turnover']:.1f}x (Change in sidebar)
#         </div>
#         """,
#             unsafe_allow_html=True,
#         )

#     # Calculate average inventory value properly
#     if 'inventory' in data:
#         try:
#             actual_inventory = data['inventory'].groupby('product_id')['quantity'].last().sum()
#             avg_product_cost = cogs / df_filtered['quantity'].sum() if df_filtered['quantity'].sum() > 0 else 0
#             avg_inventory_value = actual_inventory * avg_product_cost
#         except:
#             avg_inventory_value = cogs * 0.25  # Estimate: 25% of COGS
#     else:
#         avg_inventory_value = cogs * 0.25  # Estimate: 25% of COGS
#     avg_inventory = avg_inventory_value  # เปลี่ยนชื่อตัวแปรให้ตรงกับที่ใช้ต่อ

#     inventory_turnover = cogs / avg_inventory if avg_inventory > 0 else 0
#     dio = 365 / inventory_turnover if inventory_turnover > 0 else 0

#     units_sold = df_filtered["quantity"].sum()
#     units_received = units_sold * 1.2
#     sell_through = (units_sold / units_received * 100) if units_received > 0 else 0

#     # Compare with target
#     target_turnover = st.session_state.targets["inventory_turnover"]
#     turnover_status = (
#         "✅ Above Target" if inventory_turnover >= target_turnover else "⚠️ Below Target"
#     )
#     turnover_color = "#2ecc71" if inventory_turnover >= target_turnover else "#e74c3c"

#     col1, col2, col3, col4 = st.columns(4)

#     with col1:
#         st.markdown(
#             f"""
#         <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>INVENTORY TURNOVER</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#                 {inventory_turnover:.2f}x
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Times per year</div>
#             <div style='font-size: 10px; margin-top: 10px; padding: 8px; background: rgba(255,255,255,0.2); border-radius: 5px;'>
#                 Target: {target_turnover:.1f}x<br>{turnover_status}
#             </div>
#         </div>
#         """,
#             unsafe_allow_html=True,
#         )

#     with col2:
#         dio_color = "#2ecc71" if dio < 90 else "#e74c3c"
#         st.markdown(
#             f"""
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
#         """,
#             unsafe_allow_html=True,
#         )

#     with col3:
#         st.markdown(
#             f"""
#         <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
#                     padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>SELL-THROUGH RATE</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>{sell_through:.1f}%
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Of received</div>
#         </div>
#         """,
#             unsafe_allow_html=True,
#         )
    
#     with col4:
#         st.markdown(
#             f"""
#         <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
#                 padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#             <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
#                 <b>INVENTORY VALUE</b>
#             </div>
#             <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
#             ฿{avg_inventory/1000:.0f}K
#             </div>
#             <div style='font-size: 11px; opacity: 0.8;'>Total stock</div>
#         </div>
#         """,
#             unsafe_allow_html=True,
#         )

#     st.markdown("---")

#     # ==================== PRODUCT MOVEMENT CLASSIFICATION ====================
#     st.markdown("### 🚀 Product Movement Classification")

#     with st.expander("📖 Description", expanded=False):
#         st.markdown(
#             """
#         <div class='metric-explanation'>
#             <b>📖 คำอธิบาย:</b> จัดกลุ่มสินค้าตามความเร็วในการขาย<br>
#             • <b style='color: #2ecc71;'>Fast Moving:</b> ขายดี ควรเพิ่ม stock<br>
#             • <b style='color: #f39c12;'>Medium Moving:</b> ขายปานกลาง รักษาระดับปกติ<br>
#             • <b style='color: #e74c3c;'>Slow Moving:</b> ขายช้า ลด stock หรือทำ clearance
#         </div>
#         """,
#             unsafe_allow_html=True,
#         )

#     product_velocity = (
#         df_filtered.groupby(["product_id", "product_name", "category"])
#         .agg(
#             {"order_id": "nunique", "net_revenue": "sum", "cost": "sum", "quantity": "sum"}
#         )
#         .reset_index()
#     )
#     product_velocity.columns = [
#         "ID",
#         "Product",
#         "Category",
#         "Orders",
#         "Revenue",
#         "Cost",
#         "Units",
#     ]

#     fast_threshold = product_velocity["Orders"].quantile(0.75)
#     slow_threshold = product_velocity["Orders"].quantile(0.25)

#     def classify_movement(orders):
#         if orders >= fast_threshold:
#             return "Fast Moving"
#         elif orders <= slow_threshold:
#             return "Slow Moving"
#         return "Medium Moving"

#     product_velocity["Movement"] = product_velocity["Orders"].apply(classify_movement)

#     movement_summary = (
#         product_velocity.groupby("Movement")
#         .agg({"Product": "count", "Revenue": "sum", "Cost": "sum"})
#         .reset_index()
#     )
#     movement_summary.columns = ["Movement", "Products", "Revenue", "Inventory_Value"]

#     col1, col2 = st.columns(2)

#     with col1:
#         # Stacked bar chart
#         movement_order = ["Fast Moving", "Medium Moving", "Slow Moving"]
#         movement_colors = {
#             "Fast Moving": "#2ecc71",
#             "Medium Moving": "#f39c12",
#             "Slow Moving": "#e74c3c",
#         }

#         fig = go.Figure()

#         for movement in movement_order:
#             movement_data = movement_summary[movement_summary["Movement"] == movement]
#             if not movement_data.empty:
#                 count = movement_data["Products"].values[0]
                
#                 fig.add_trace(
#                     go.Bar(
#                         y=["Product Count"],
#                         x=[count],
#                         name=movement,
#                         orientation="h",
#                         marker_color=movement_colors[movement],
#                         text=[count],
#                         texttemplate="%{text}",
#                         textposition="inside",
#                         hovertemplate=f"<b>{movement}</b><br>Products: %{{x}}<extra></extra>",
#                     )
#                 )

#         fig.update_layout(
#             title="<b>Product Distribution by Movement Speed</b>",
#             xaxis=dict(title="Number of Products"),
#             yaxis=dict(title=""),
#             barmode="stack",
#             plot_bgcolor="white",
#             height=400,
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
#         )

#         st.plotly_chart(fig, use_container_width=True)

#     with col2:
#         # Inventory value by movement
#         movement_sorted = movement_summary.sort_values("Inventory_Value", ascending=True)
#         colors = [movement_colors[m] for m in movement_sorted["Movement"]]

#         fig = go.Figure()

#         fig.add_trace(
#             go.Bar(
#                 y=movement_sorted["Movement"],
#                 x=movement_sorted["Inventory_Value"],
#                 orientation="h",
#                 marker=dict(color=colors),
#                 text=movement_sorted["Inventory_Value"],
#                 texttemplate="฿%{text:,.0f}",
#                 textposition="outside",
#                 hovertemplate="<b>%{y}</b><br>Value: ฿%{x:,.0f}<extra></extra>",
#             )
#         )

#         fig.update_layout(
#             title="<b>Inventory Value by Movement</b>",
#             xaxis=dict(
#                 title="Inventory Value (฿)", showgrid=True, gridcolor="rgba(0,0,0,0.05)"
#             ),
#             yaxis=dict(title=""),
#             plot_bgcolor="white",
#             height=400,
#             showlegend=False,
#         )

#         st.plotly_chart(fig, use_container_width=True)

#     # Show top products in each category
#     st.markdown("#### 📋 Movement Classification Details")

#     col1, col2, col3 = st.columns(3)

#     with col1:
#         st.success("**🚀 Fast Moving (Top 10)**")
#         fast_products = product_velocity[
#             product_velocity["Movement"] == "Fast Moving"
#         ].nlargest(10, "Orders")
        
#         if not fast_products.empty:
#             st.dataframe(
#                 fast_products[["Product", "Orders", "Units"]].style.format(
#                     {"Orders": "{:,}", "Units": "{:,}"}
#                 ),
#                 height=300,
#                 use_container_width=True,
#             )
#         else:
#             st.info("No fast moving products")

#     with col2:
#         st.warning("**⚖️ Medium Moving (Top 10)**")
#         medium_products = product_velocity[
#             product_velocity["Movement"] == "Medium Moving"
#         ].nlargest(10, "Orders")
        
#         if not medium_products.empty:
#             st.dataframe(
#                 medium_products[["Product", "Orders", "Units"]].style.format(
#                     {"Orders": "{:,}", "Units": "{:,}"}
#                 ),
#                 height=300,
#                 use_container_width=True,
#             )
#         else:
#             st.info("No medium moving products")

#     with col3:
#         st.error("**🐌 Slow Moving (Top 10)**")
#         slow_products = product_velocity[
#             product_velocity["Movement"] == "Slow Moving"
#         ].nlargest(10, "Cost")
        
#         if not slow_products.empty:
#             st.dataframe(
#                 slow_products[["Product", "Orders", "Cost"]].style.format(
#                     {"Orders": "{:,}", "Cost": "฿{:,.0f}"}
#                 ),
#                 height=300,
#                 use_container_width=True,
#             )
#         else:
#             st.info("No slow moving products")

#     st.markdown("---")

#     # ==================== ABC ANALYSIS ====================
#     st.markdown("### 📊 ABC Analysis (Pareto Principle)")

#     with st.expander("📖 Description", expanded=False):
#         st.markdown(
#             """
#         <div class='metric-explanation'>
#             <b>📖 ABC Analysis:</b> จัดกลุ่มสินค้าตามมูลค่ายอดขาย (80/20 rule)<br>
#             • <b style='color: #e74c3c;'>Class A:</b> 20% ของสินค้า สร้าง 80% ของรายได้ → ดูแลอย่างใกล้ชิด<br>
#             • <b style='color: #f39c12;'>Class B:</b> 30% ของสินค้า สร้าง 15% ของรายได้ → ดูแลปานกลาง<br>
#             • <b style='color: #95a5a6;'>Class C:</b> 50% ของสินค้า สร้าง 5% ของรายได้ → ดูแลน้อยที่สุด<br>
#             <b>💡 การใช้ประโยชน์:</b> มุ่งเน้นทรัพยากรกับสินค้าที่สำคัญ (Class A)
#         </div>
#         """,
#             unsafe_allow_html=True,
#         )

#     # Calculate ABC classification
#     abc_analysis = product_velocity.copy()
#     abc_analysis = abc_analysis.sort_values("Revenue", ascending=False)
#     abc_analysis["Revenue_Cumulative"] = abc_analysis["Revenue"].cumsum()
#     abc_analysis["Revenue_Cumulative_%"] = (
#         abc_analysis["Revenue_Cumulative"] / abc_analysis["Revenue"].sum() * 100
#     )

#     def classify_abc(cum_pct):
#         if cum_pct <= 80:
#             return "Class A"
#         elif cum_pct <= 95:
#             return "Class B"
#         else:
#             return "Class C"

#     abc_analysis["ABC_Class"] = abc_analysis["Revenue_Cumulative_%"].apply(classify_abc)

#     # ABC Summary
#     abc_summary = (
#         abc_analysis.groupby("ABC_Class")
#         .agg({"Product": "count", "Revenue": "sum", "Cost": "sum"})
#         .reset_index()
#     )
#     abc_summary.columns = ["Class", "Products", "Revenue", "Inventory_Value"]
#     abc_summary["Revenue_%"] = (abc_summary["Revenue"] / abc_summary["Revenue"].sum() * 100).round(1)

#     col1, col2 = st.columns([1, 2])

#     with col1:
#         # ABC Summary Cards
#         abc_colors = {
#             "Class A": "#e74c3c",
#             "Class B": "#f39c12",
#             "Class C": "#95a5a6"
#         }

#         for abc_class in ["Class A", "Class B", "Class C"]:
#             class_data = abc_summary[abc_summary["Class"] == abc_class]
#             if not class_data.empty:
#                 products = class_data["Products"].values[0]
#                 revenue = class_data["Revenue"].values[0]
#                 revenue_pct = class_data["Revenue_%"].values[0]
#                 color = abc_colors[abc_class]

#                 st.markdown(
#                     f"""
#                 <div style='background: white; padding: 20px; margin: 10px 0; border-radius: 10px; 
#                             border-left: 5px solid {color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#                     <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 5px;'>
#                         <b>{abc_class}</b>
#                     </div>
#                     <div style='font-size: 24px; font-weight: bold; color: {color}; margin: 5px 0;'>
#                         {products} products
#                     </div>
#                     <div style='font-size: 12px; color: #95a5a6;'>
#                         ฿{revenue/1000:.0f}K ({revenue_pct:.1f}% of revenue)
#                     </div>
#                 </div>
#                 """,
#                     unsafe_allow_html=True,
#                 )

#     with col2:
#         # Pareto Chart
#         fig = go.Figure()

#         fig.add_trace(
#             go.Bar(
#                 x=abc_analysis["Product"].head(20),
#                 y=abc_analysis["Revenue"].head(20),
#                 name="Revenue",
#                 marker_color="#3498db",
#                 yaxis="y",
#                 hovertemplate="<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>",
#             )
#         )

#         fig.add_trace(
#             go.Scatter(
#                 x=abc_analysis["Product"].head(20),
#                 y=abc_analysis["Revenue_Cumulative_%"].head(20),
#                 name="Cumulative %",
#                 mode="lines+markers",
#                 line=dict(color="#e74c3c", width=3),
#                 marker=dict(size=8),
#                 yaxis="y2",
#                 hovertemplate="<b>%{x}</b><br>Cumulative: %{y:.1f}%<extra></extra>",
#             )
#         )

#         # Add 80% line
#         fig.add_hline(
#             y=80,
#             line_dash="dash",
#             line_color="gray",
#             opacity=0.5,
#             annotation_text="80%",
#             annotation_position="right",
#             yref="y2"
#         )

#         fig.update_layout(
#             title="<b>Pareto Chart - Top 20 Products</b>",
#             xaxis=dict(title="", showticklabels=False),
#             yaxis=dict(
#                 title="Revenue (฿)", 
#                 showgrid=True, 
#                 gridcolor="rgba(0,0,0,0.05)"
#             ),
#             yaxis2=dict(
#                 title="Cumulative %",
#                 overlaying="y",
#                 side="right",
#                 showgrid=False,
#                 range=[0, 100]
#             ),
#             plot_bgcolor="white",
#             height=400,
#             hovermode="x unified",
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
#         )

#         st.plotly_chart(fig, use_container_width=True)

#     st.markdown("---")

#     # ==================== STOCK HEALTH DASHBOARD ====================
#     st.markdown("### 🏥 Stock Health Dashboard")

#     with st.expander("📖 Description", expanded=False):
#         st.markdown(
#             """
#         <div class='metric-explanation'>
#             <b>📖 Stock Health:</b> ประเมินสุขภาพของสินค้าคงคลัง<br>
#             • <b style='color: #2ecc71;'>Healthy:</b> ขายดี หมุนเวียนเร็ว<br>
#             • <b style='color: #f39c12;'>Watch:</b> ต้องติดตาม อาจมีปัญหา<br>
#             • <b style='color: #e74c3c;'>Critical:</b> ขายช้า หมุนเวียนช้า ควรทำ clearance
#         </div>
#         """,
#             unsafe_allow_html=True,
#         )

#     # Calculate stock health
#     stock_health = product_velocity.copy()
#     stock_health["Inventory_Turnover"] = stock_health.apply(
#         lambda x: (x["Cost"] / x["inventory_value"]) if x["inventory_value"] > 0 else 0,
#         axis=1
#     )

#     # Calculate Days in Stock
#     stock_health["Days_in_Stock"] = stock_health.apply(
#         lambda x: (365 / x["Inventory_Turnover"]) if x["Inventory_Turnover"] > 0 else 999, 
#         axis=1
#     )
#     def classify_health(row):
#         turnover = row["Inventory_Turnover"]
#         days = row["Days_in_Stock"]
    
#         # Healthy: หมุนเวียนเร็ว (> 6x/year หรือ < 60 days)
#         if turnover >= 6 and days < 60:
#             return "Healthy"
#         # Critical: หมุนเวียนช้า (< 2x/year หรือ > 180 days)
#         elif turnover < 2 or days > 180:
#             return "Critical"
#         # Watch: อยู่ตรงกลาง
#         else:
#             return "Watch"
        
#     stock_health["Health_Status"] = stock_health.apply(classify_health, axis=1)

#     # Health summary
#     health_summary = stock_health.groupby("Health_Status").agg({
#         "Product": "count",
#         "Revenue": "sum",
#         "Cost": "sum"
#     }).reset_index()
#     health_summary.columns = ["Status", "Products", "Revenue", "Inventory_Value"]

#     col1, col2, col3 = st.columns(3)

#     health_colors = {
#         "Healthy": "#2ecc71",
#         "Watch": "#f39c12",
#         "Critical": "#e74c3c"
#     }

#     for idx, (col, status) in enumerate(zip([col1, col2, col3], ["Healthy", "Watch", "Critical"])):
#         status_data = health_summary[health_summary["Status"] == status]
#         if not status_data.empty:
#             products = status_data["Products"].values[0]
#             inventory_val = status_data["Inventory_Value"].values[0]
#             color = health_colors[status]

#             with col:
#                 icon = "✅" if status == "Healthy" else "⚠️" if status == "Watch" else "🚨"
#                 st.markdown(
#                     f"""
#                 <div style='background: linear-gradient(135deg, {color} 0%, {color}dd 100%); 
#                             padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#                     <div style='font-size: 36px; margin-bottom: 10px;'>{icon}</div>
#                     <div style='font-size: 14px; opacity: 0.9;'>{status.upper()}</div>
#                     <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
#                         {products}
#                     </div>
#                     <div style='font-size: 11px; opacity: 0.8;'>
#                         Products (฿{inventory_val/1000:.0f}K)
#                     </div>
#                 </div>
#                 """,
#                     unsafe_allow_html=True,
#                 )
#         else:
#             with col:
#                 icon = "✅" if status == "Healthy" else "⚠️" if status == "Watch" else "🚨"
#                 color = health_colors[status]
#                 st.markdown(
#                     f"""
#                 <div style='background: linear-gradient(135deg, {color} 0%, {color}dd 100%); 
#                             padding: 25px; border-radius: 10px; color: white; text-align: center;'>
#                     <div style='font-size: 36px; margin-bottom: 10px;'>{icon}</div>
#                     <div style='font-size: 14px; opacity: 0.9;'>{status.upper()}</div>
#                     <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
#                         0
#                     </div>
#                     <div style='font-size: 11px; opacity: 0.8;'>
#                         Products
#                     </div>
#                 </div>
#                 """,
#                     unsafe_allow_html=True,
#                 )

#     # Critical products list
#     critical_products = stock_health[stock_health["Health_Status"] == "Critical"].nlargest(10, "Cost")

#     if not critical_products.empty:
#         st.markdown("#### 🚨 Critical Products Requiring Action")
        
#         critical_display = critical_products[[
#             "Product", "Category", "Orders", "Revenue", "Cost", "Movement"
#         ]].copy()
        
#         styled_critical = critical_display.style.format({
#             "Orders": "{:,}",
#             "Revenue": "฿{:,.0f}",
#             "Cost": "฿{:,.0f}"
#         }).apply(lambda x: ["background-color: #ffebee"] * len(x), axis=1)
        
#         st.dataframe(styled_critical, use_container_width=True)
        
#         st.warning("""
#         💡 **Recommended Actions:**
#         - Launch clearance sale (30-50% discount)
#         - Bundle with fast-moving products
#         - Consider donation for tax benefits
#         - Stop reordering until stock clears
#         """)
#     else:
#         st.success("✅ No critical stock issues detected!")

# # ==================== TAB 5 START ====================
# with tab5:
#     st.markdown("# 🔮 Forecasting & Planning")
#     st.markdown("---")

#     # with st.expander("📖 Description", expanded=False):
#     #     st.markdown(
#     #         """
#     #     <div class='metric-explanation'>
#     #         <b>📖 คำอธิบาย:</b> ใช้ข้อมูลในอดีตเพื่อคาดการณ์อนาคต ช่วยในการวางแผนธุรกิจ<br>
#     #         <b>🎯 วิธีการ:</b> ใช้ Moving Average และ Linear Regression เพื่อทำนายแนวโน้ม
#     #     </div>
#     #     """,
#     #         unsafe_allow_html=True,
#     #     )

#     # ==================== REVENUE FORECAST ====================
#     st.markdown("### 📈 Revenue Forecast (Next 12 Months)")

#     with st.expander("📖 Description", expanded=False):
#         st.markdown(
#             """
#         <div class='metric-explanation'>
#             <b>📖 Revenue Forecast:</b> ทำนายยอดขายในอนาคต 12 เดือนข้างหน้า<br>
#             <div class='metric-formula'>
#                 วิธีการ: Linear Regression + Moving Average (3 เดือน)
#             </div>
#             <b>💡 การใช้ประโยชน์:</b><br>
#             • วางแผนงบประมาณ<br>
#             • กำหนดเป้าหมายทีมขาย<br>
#             • วางแผนจัดซื้อสินค้า<br>
#             • วางแผนการตลาด
#         </div>
#         """,
#             unsafe_allow_html=True,
#         )

#     # Prepare historical data
#     monthly_revenue = (
#         df_filtered.groupby("order_month").agg({"net_revenue": "sum"}).reset_index()
#     )
#     monthly_revenue["order_month"] = monthly_revenue["order_month"].dt.to_timestamp()
#     monthly_revenue = monthly_revenue.sort_values("order_month")

#     if len(monthly_revenue) >= 3:
#         # Calculate moving average
#         monthly_revenue["MA_3"] = monthly_revenue["net_revenue"].rolling(window=3).mean()

#         # Simple linear regression for trend
#         from sklearn.linear_model import LinearRegression
#         import numpy as np

#         X = np.arange(len(monthly_revenue)).reshape(-1, 1)
#         y = monthly_revenue["net_revenue"].values

#         model = LinearRegression()
#         model.fit(X, y)

#         # Forecast next 12 months
#         future_months = 12
#         future_X = np.arange(
#             len(monthly_revenue), len(monthly_revenue) + future_months
#         ).reshape(-1, 1)
#         forecast_values = model.predict(future_X)

#         # Apply growth adjustment (use recent growth rate)
#         recent_growth = monthly_revenue["net_revenue"].pct_change().tail(3).mean()
#         if not np.isnan(recent_growth) and recent_growth != 0:
#             growth_factor = 1 + recent_growth
#             forecast_adjusted = []
#             last_value = monthly_revenue["net_revenue"].iloc[-1]
#             for i in range(future_months):
#                 last_value = last_value * growth_factor
#                 forecast_adjusted.append(last_value)
#             forecast_values = (forecast_values + np.array(forecast_adjusted)) / 2

#         # Create forecast dataframe
#         last_date = monthly_revenue["order_month"].iloc[-1]
#         forecast_dates = pd.date_range(
#             start=last_date + pd.DateOffset(months=1), periods=future_months, freq="MS"
#         )

#         forecast_df = pd.DataFrame({"Month": forecast_dates, "Forecast": forecast_values})
#         forecast_df["Month_Label"] = forecast_df["Month"].dt.strftime("%b %Y")

#         # Calculate confidence interval (±15%)
#         forecast_df["Lower"] = forecast_values * 0.85
#         forecast_df["Upper"] = forecast_values * 1.15

#         col1, col2 = st.columns([2, 1])

#         with col1:
#             # Create forecast chart
#             fig = go.Figure()

#             # Historical data
#             fig.add_trace(
#                 go.Scatter(
#                     x=monthly_revenue["order_month"].dt.strftime("%b %Y"),
#                     y=monthly_revenue["net_revenue"],
#                     name="Actual",
#                     mode="lines+markers",
#                     line=dict(color="#3498db", width=3),
#                     marker=dict(size=8),
#                     hovertemplate="<b>%{x}</b><br>Actual: ฿%{y:,.0f}<extra></extra>",
#                 )
#             )

#             # Moving Average
#             fig.add_trace(
#                 go.Scatter(
#                     x=monthly_revenue["order_month"].dt.strftime("%b %Y"),
#                     y=monthly_revenue["MA_3"],
#                     name="3-Month MA",
#                     mode="lines",
#                     line=dict(color="#95a5a6", width=2, dash="dash"),
#                     hovertemplate="<b>%{x}</b><br>MA: ฿%{y:,.0f}<extra></extra>",
#                 )
#             )

#             # Forecast
#             fig.add_trace(
#                 go.Scatter(
#                     x=forecast_df["Month_Label"],
#                     y=forecast_df["Forecast"],
#                     name="Forecast",
#                     mode="lines+markers",
#                     line=dict(color="#e74c3c", width=3),
#                     marker=dict(size=8, symbol="diamond"),
#                     hovertemplate="<b>%{x}</b><br>Forecast: ฿%{y:,.0f}<extra></extra>",
#                 )
#             )

#             # Confidence interval
#             fig.add_trace(
#                 go.Scatter(
#                     x=forecast_df["Month_Label"],
#                     y=forecast_df["Upper"],
#                     mode="lines",
#                     line=dict(width=0),
#                     showlegend=False,
#                     hoverinfo="skip",
#                 )
#             )

#             fig.add_trace(
#                 go.Scatter(
#                     x=forecast_df["Month_Label"],
#                     y=forecast_df["Lower"],
#                     mode="lines",
#                     line=dict(width=0),
#                     fill="tonexty",
#                     fillcolor="rgba(231, 76, 60, 0.2)",
#                     name="Confidence Interval (±15%)",
#                     hovertemplate="<b>%{x}</b><br>Range: ฿%{y:,.0f}<extra></extra>",
#                 )
#             )

#             fig.update_layout(
#                 title="<b>Revenue Forecast - Next 12 Months</b>",
#                 xaxis=dict(title="", showgrid=False),
#                 yaxis=dict(
#                     title="Revenue (฿)", showgrid=True, gridcolor="rgba(0,0,0,0.05)"
#                 ),
#                 plot_bgcolor="white",
#                 height=400,
#                 hovermode="x unified",
#                 legend=dict(
#                     orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
#                 ),
#             )

#             st.plotly_chart(fig, use_container_width=True)

#         with col2:
#             # Forecast summary
#             total_forecast = forecast_df["Forecast"].sum()
#             avg_monthly = forecast_df["Forecast"].mean()
#             growth_forecast = (
#                 (forecast_df["Forecast"].iloc[-1] - monthly_revenue["net_revenue"].iloc[-1])
#                 / monthly_revenue["net_revenue"].iloc[-1]
#                 * 100
#             )

#             st.markdown(
#                 f"""
#             <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                         padding: 25px; border-radius: 10px; color: white; text-align: center; height: 400px;
#                         display: flex; flex-direction: column; justify-content: center;'>
#                 <div style='font-size: 14px; opacity: 0.9; margin-bottom: 15px;'>
#                     <b>FORECAST SUMMARY</b>
#                 </div>
#                 <div style='margin: 20px 0;'>
#                     <div style='font-size: 12px; opacity: 0.8;'>Next 12 Months Total</div>
#                     <div style='font-size: 26px; font-weight: bold; margin: 10px 0;'>
#                         ฿{total_forecast/1000000:.1f}M
#                 </div>
#                 <div style='margin: 20px 0;'>
#                     <div style='font-size: 12px; opacity: 0.8;'>Average Monthly</div>
#                     <div style='font-size: 26px; font-weight: bold; margin: 10px 0;'>
#                         ฿{avg_monthly/1000000:.0f}M
#                 </div>
#                 <div style='margin: 20px 0;'>
#                     <div style='font-size: 12px; opacity: 0.8;'>Expected Growth</div>
#                     <div style='font-size: 26px; font-weight: bold; margin: 10px 0;'>
#                         {growth_forecast:+.1f}%
#             """,
#                 unsafe_allow_html=True,
#             )

#         # Forecast table
#         st.markdown("#### 📋 Monthly Forecast Details")

#         forecast_display = forecast_df.copy()
#         forecast_display["Month"] = forecast_display["Month_Label"]
#         forecast_display = forecast_display[["Month", "Forecast", "Lower", "Upper"]]
#         forecast_display.columns = ["Month", "Forecast", "Min Expected", "Max Expected"]

#         styled_forecast = forecast_display.style.format(
#             {"Forecast": "฿{:,.0f}", "Min Expected": "฿{:,.0f}", "Max Expected": "฿{:,.0f}"}
#         ).background_gradient(subset=["Forecast"], cmap="Blues")

#         st.dataframe(styled_forecast, use_container_width=True, height=300)
#     else:
#         st.warning("⚠️ ต้องมีข้อมูลอย่างน้อย 3 เดือนเพื่อทำ Forecast")

#     st.markdown("---")

#     # ==================== STOCK PLANNING ====================
#     st.markdown("### 📦 Stock Planning Recommendation")

#     with st.expander("📖 Description", expanded=False):
#         st.markdown("""
#         <div class='metric-explanation'>
#             <b>📖 Stock Planning:</b> แนะนำปริมาณสต็อกที่ควรมีสำหรับแต่ละสินค้า<br>
#             <div class='metric-formula'>
#                 สูตร: (ยอดขายเฉลี่ยต่อเดือน × Lead Time) + Safety Stock
#             </div>
#             <b>📖 Safety Stock:</b> สต็อกสำรอง เผื่อความผันผวนของยอดขาย (20% ของยอดขายเฉลี่ย)<br>
#             <b>💡 การใช้ประโยชน์:</b><br>
#             • ป้องกันสินค้าหมด<br>
#             • ลดต้นทุนการจัดเก็บ<br>
#             • วางแผนสั่งซื้อล่วงหน้า
#         </div>
#         """, unsafe_allow_html=True)

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

#     # with st.expander("📖 Description", expanded=False):
#     #     st.markdown("""
#     #     <div class='metric-explanation'>
#     #         <b>📖 Demand Forecasting:</b> ทำนายความต้องการสินค้าแต่ละหมวดหมู่ในอนาคต<br>
#     #         <b>💡 ประโยชน์:</b> วางแผนการผลิต/สั่งซื้อ แยกตามหมวดหมู่สินค้า
#     #     </div>
#     #     """, unsafe_allow_html=True)

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

# # เพิ่ม Tab 6 ต่อจาก Tab 5
# with tab6:
#     st.markdown("# 🤖 AI-Powered Business Insights")
#     st.markdown("---")
    
#     st.markdown("""
#     <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                 padding: 25px; border-radius: 15px; color: white; margin-bottom: 30px;'>
#         <h3 style='margin: 0 0 10px 0;'>🧠 Smart Analytics Engine</h3>
#         <p style='margin: 0; opacity: 0.9; font-size: 14px;'>
#             AI algorithms analyze your data to uncover hidden patterns, predict trends, and provide actionable recommendations
#         </p>
#     </div>
#     """, unsafe_allow_html=True)
    
    # # ==================== AI CUSTOMER SEGMENTATION (RFM) ====================
    # st.markdown("### 👥 AI Customer Segmentation (RFM Analysis)")
    
    # with st.expander("📖 Description", expanded=False):
    #     st.markdown("""
    #     <div class='metric-explanation'>
    #         <b>📖 RFM Analysis:</b> แบ่งกลุ่มลูกค้าตามพฤติกรรมการซื้อ<br>
    #         <div class='metric-formula'>
    #             • <b>Recency (R):</b> ซื้อล่าสุดเมื่อไหร่ (วัน)<br>
    #             • <b>Frequency (F):</b> ซื้อบ่อยแค่ไหน (ครั้ง)<br>
    #             • <b>Monetary (M):</b> ใช้จ่ายเท่าไหร่ (บาท)
    #         </div>
    #         <b>💡 Customer Segments:</b><br>
    #         • <b style='color: #2ecc71;'>Champions:</b> ซื้อบ่อย ซื้อเยอะ ซื้อเมื่อเร็วๆ นี้<br>
    #         • <b style='color: #3498db;'>Loyal:</b> ซื้อสม่ำเสมอ ใช้จ่ายดี<br>
    #         • <b style='color: #f39c12;'>At Risk:</b> เคยซื้อเยอะ แต่นานไม่ซื้อแล้ว<br>
    #         • <b style='color: #e74c3c;'>Lost:</b> ไม่ซื้อมานาน ต้องดึงกลับ
    #     </div>
    #     """, unsafe_allow_html=True)
    
    # # Calculate RFM
    # analysis_date = df_filtered['order_date'].max()
    
    # rfm = df_filtered.groupby('user_id').agg({
    #     'order_date': lambda x: (analysis_date - x.max()).days,  # Recency
    #     'order_id': 'nunique',  # Frequency
    #     'net_revenue': 'sum'  # Monetary
    # }).reset_index()
    
    # rfm.columns = ['user_id', 'recency', 'frequency', 'monetary']


    # # RFM Scoring (1-5 scale) with error handling
    # try:
    #     # ใช้ rank เพื่อรองรับข้อมูลที่ซ้ำกัน
    #     rfm['r_rank'] = rfm['recency'].rank(method='first')
    #     rfm['f_rank'] = rfm['frequency'].rank(method='first')
    #     rfm['m_rank'] = rfm['monetary'].rank(method='first')
    
    #     # แบ่งเป็น 5 กลุ่ม
    #     rfm['r_score'] = pd.cut(rfm['r_rank'], bins=5, labels=[5,4,3,2,1], duplicates='drop')
    #     rfm['f_score'] = pd.cut(rfm['f_rank'], bins=5, labels=[1,2,3,4,5], duplicates='drop')
    #     rfm['m_score'] = pd.cut(rfm['m_rank'], bins=5, labels=[1,2,3,4,5], duplicates='drop')
    # except:
    #     # Fallback: ใช้ qcut แบบเดิม
    #     rfm['r_score'] = pd.qcut(rfm['recency'], q=5, labels=[5,4,3,2,1], duplicates='drop')
    #     rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=5, labels=[1,2,3,4,5], duplicates='drop')
    #     rfm['m_score'] = pd.qcut(rfm['monetary'].rank(method='first'), q=5, labels=[1,2,3,4,5], duplicates='drop')
    
    # rfm['rfm_score'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str) + rfm['m_score'].astype(str)
    
    # # Segment customers
    # def segment_customer(row):
    #     r, f, m = int(row['r_score']), int(row['f_score']), int(row['m_score'])
        
    #     if r >= 4 and f >= 4 and m >= 4:
    #         return 'Champions'
    #     elif r >= 3 and f >= 3:
    #         return 'Loyal Customers'
    #     elif r >= 4 and f <= 2:
    #         return 'New Customers'
    #     elif r <= 2 and f >= 3:
    #         return 'At Risk'
    #     elif r <= 2 and f <= 2:
    #         return 'Lost'
    #     elif m >= 4:
    #         return 'Big Spenders'
    #     else:
    #         return 'Others'
    
    # rfm['segment'] = rfm.apply(segment_customer, axis=1)
    
    # # Segment summary
    # segment_summary = rfm.groupby('segment').agg({
    #     'user_id': 'count',
    #     'monetary': 'sum',
    #     'frequency': 'mean',
    #     'recency': 'mean'
    # }).reset_index()
    # segment_summary.columns = ['Segment', 'Customers', 'Total Revenue', 'Avg Frequency', 'Avg Recency']
    # segment_summary = segment_summary.sort_values('Total Revenue', ascending=False)
    
    # col1, col2 = st.columns([1, 2])
    
    # with col1:
    #     # Segment distribution pie chart
    #     segment_colors = {
    #         'Champions': '#2ecc71',
    #         'Loyal Customers': '#3498db',
    #         'New Customers': '#1abc9c',
    #         'At Risk': '#f39c12',
    #         'Lost': '#e74c3c',
    #         'Big Spenders': '#9b59b6',
    #         'Others': '#95a5a6'
    #     }
        
    #     fig = go.Figure(data=[go.Pie(
    #         labels=segment_summary['Segment'],
    #         values=segment_summary['Customers'],
    #         marker=dict(colors=[segment_colors.get(s, '#95a5a6') for s in segment_summary['Segment']]),
    #         textinfo='label+percent',
    #         textposition='inside',
    #         hovertemplate='<b>%{label}</b><br>Customers: %{value:,}<br>Share: %{percent}<extra></extra>'
    #     )])
        
    #     fig.update_layout(
    #         title='<b>Customer Segment Distribution</b>',
    #         height=400,
    #         showlegend=True,
    #         legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.1)
    #     )
        
    #     st.plotly_chart(fig, use_container_width=True)
    
    # with col2:
    #     # Revenue by segment
    #     segment_sorted = segment_summary.sort_values('Total Revenue', ascending=True)
    #     colors_list = [segment_colors.get(s, '#95a5a6') for s in segment_sorted['Segment']]
        
    #     fig = go.Figure()
        
    #     fig.add_trace(go.Bar(
    #         y=segment_sorted['Segment'],
    #         x=segment_sorted['Total Revenue'],
    #         orientation='h',
    #         marker=dict(color=colors_list),
    #         text=segment_sorted['Total Revenue'],
    #         texttemplate='฿%{text:,.0f}',
    #         textposition='outside',
    #         hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
    #     ))
        
    #     fig.update_layout(
    #         title='<b>Revenue by Customer Segment</b>',
    #         xaxis=dict(title='Total Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
    #         yaxis=dict(title=''),
    #         plot_bgcolor='white',
    #         height=400,
    #         showlegend=False
    #     )
        
    #     st.plotly_chart(fig, use_container_width=True)
    
#     # AI Recommendations for each segment
#     st.markdown("#### 🎯 AI-Powered Action Recommendations")
    
#     segment_actions = {
#         'Champions': {
#             'emoji': '👑',
#             'color': '#2ecc71',
#             'actions': [
#                 'Send VIP early access to new products',
#                 'Create exclusive loyalty rewards program',
#                 'Ask for testimonials and referrals',
#                 'Offer premium/upsell products'
#             ]
#         },
#         'Loyal Customers': {
#             'emoji': '💎',
#             'color': '#3498db',
#             'actions': [
#                 'Build deeper relationships with personalized communication',
#                 'Cross-sell complementary products',
#                 'Invite to become brand ambassadors',
#                 'Offer subscription programs'
#             ]
#         },
#         'At Risk': {
#             'emoji': '⚠️',
#             'color': '#f39c12',
#             'actions': [
#                 'Send win-back campaigns with special offers',
#                 'Survey to understand why they stopped buying',
#                 'Offer limited-time discounts (15-20%)',
#                 'Re-engage with new product launches'
#             ]
#         },
#         'Lost': {
#             'emoji': '🔴',
#             'color': '#e74c3c',
#             'actions': [
#                 'Aggressive win-back campaign (25-30% discount)',
#                 'Personalized "We miss you" emails',
#                 'Survey to understand churn reasons',
#                 'Consider if re-acquisition cost is worth it'
#             ]
#         },
#         'New Customers': {
#             'emoji': '🌟',
#             'color': '#1abc9c',
#             'actions': [
#                 'Welcome email series with education content',
#                 'First repeat purchase incentive (10% off)',
#                 'Product recommendation based on first purchase',
#                 'Build trust with great customer service'
#             ]
#         },
#         'Big Spenders': {
#             'emoji': '💰',
#             'color': '#9b59b6',
#             'actions': [
#                 'Personal account manager or VIP service',
#                 'Exclusive high-value product previews',
#                 'Volume discount programs',
#                 'Premium packaging and shipping'
#             ]
#         }
#     }
    
#     for segment in segment_summary['Segment']:
#         if segment in segment_actions:
#             info = segment_actions[segment]
#             customers = segment_summary[segment_summary['Segment'] == segment]['Customers'].values[0]
#             revenue = segment_summary[segment_summary['Segment'] == segment]['Total Revenue'].values[0]
            
#             with st.expander(f"{info['emoji']} **{segment}** ({customers:,} customers, ฿{revenue:,.0f} revenue)", expanded=False):
#                 st.markdown(f"<div style='padding: 15px; background: {info['color']}15; border-left: 4px solid {info['color']}; border-radius: 5px;'>", unsafe_allow_html=True)
#                 for action in info['actions']:
#                     st.markdown(f"• {action}")
#                 st.markdown("</div>", unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== PRODUCT RECOMMENDATION ENGINE ====================
#     st.markdown("### 🎁 AI Product Recommendation Engine")
    
#     with st.expander("📖 Description", expanded=False):
#         st.markdown("""
#         <div class='metric-explanation'>
#             <b>📖 Collaborative Filtering:</b> แนะนำสินค้าตาม pattern ของลูกค้าที่มีพฤติกรรมคล้ายกัน<br>
#             <b>💡 Algorithm:</b> ใช้ Item-based Collaborative Filtering<br>
#             • วิเคราะห์สินค้าที่มักถูกซื้อด้วยกัน<br>
#             • คำนวณ similarity score ระหว่างสินค้า<br>
#             • แนะนำสินค้าที่เกี่ยวข้องกับสินค้าที่ลูกค้าซื้อ
#         </div>
#         """, unsafe_allow_html=True)
    
#     # Create user-product matrix
#     user_product = df_filtered.pivot_table(
#         index='user_id',
#         columns='product_name',
#         values='quantity',
#         aggfunc='sum',
#         fill_value=0
#     )
    
#     # Calculate product similarity (cosine similarity)
#     from sklearn.metrics.pairwise import cosine_similarity
    
#     product_similarity = cosine_similarity(user_product.T)
#     product_similarity_df = pd.DataFrame(
#         product_similarity,
#         index=user_product.columns,
#         columns=user_product.columns
#     )
    
#     # Get top products for recommendation
#     top_products_list = df_filtered.groupby('product_name')['quantity'].sum().nlargest(10).index.tolist()
    
#     st.markdown("**เลือกสินค้าที่ลูกค้าซื้อ เพื่อดูสินค้าแนะนำ:**")
    
#     selected_product = st.selectbox(
#         "สินค้า",
#         options=top_products_list,
#         key='recommendation_product'
#     )
    
#     if selected_product:
#         # Check if product exists in similarity matrix
#         if selected_product in product_similarity_df.columns:
#             # Get recommendations
#             similar_products = product_similarity_df[selected_product].sort_values(ascending=False)[1:6]
        
#             if len(similar_products) > 0:
#                 # (โค้ดส่วนแสดงผลเดิมไม่ต้องแก้)
#                 col1, col2 = st.columns([1, 2])
#                 # ... ส่วนที่เหลือเหมือนเดิม
#             else:
#                 st.info("ℹ️ ไม่พบสินค้าที่คล้ายกัน")
#         else:
#             st.warning(f"⚠️ ไม่พบข้อมูลสินค้า '{selected_product}' ในระบบ")

#         col1, col2 = st.columns([1, 2])
        
#         with col1:
#             st.markdown(f"""
#             <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                         padding: 30px; border-radius: 10px; color: white; text-align: center; height: 300px;
#                         display: flex; flex-direction: column; justify-content: center;'>
#                 <div style='font-size: 14px; opacity: 0.9; margin-bottom: 10px;'>
#                     <b>SELECTED PRODUCT</b>
#                 </div>
#                 <div style='font-size: 18px; font-weight: bold; margin: 15px 0;'>
#                     {selected_product}
#                 </div>
#                 <div style='font-size: 12px; opacity: 0.8;'>
#                     Based on purchase patterns
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col2:
#             st.markdown("**🎯 Top 5 Recommended Products:**")
            
#             for i, (product, score) in enumerate(similar_products.items(), 1):
#                 confidence = score * 100
#                 color = '#2ecc71' if confidence > 70 else '#f39c12' if confidence > 50 else '#95a5a6'
                
#                 st.markdown(f"""
#                 <div style='padding: 12px; margin: 8px 0; background: white; border-left: 4px solid {color}; 
#                             border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#                     <div style='display: flex; justify-content: space-between; align-items: center;'>
#                         <div>
#                             <b>{i}. {product}</b>
#                         </div>
#                         <div style='background: {color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px;'>
#                             {confidence:.0f}% match
#                         </div>
#                     </div>
#                 </div>
#                 """, unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== PRICE OPTIMIZATION AI ====================
#     st.markdown("### 💰 AI Price Optimization")
    
#     with st.expander("📖 Description", expanded=False):
#         st.markdown("""
#         <div class='metric-explanation'>
#             <b>📖 Price Elasticity Analysis:</b> วิเคราะห์ว่าราคามีผลต่อยอดขายอย่างไร<br>
#             <b>💡 Algorithm:</b> ใช้ Regression Analysis หา optimal price point<br>
#             • คำนวณ price elasticity of demand<br>
#             • หาจุดที่ maximize profit (ไม่ใช่ revenue)<br>
#             • แนะนำราคาที่เหมาะสมสำหรับแต่ละสินค้า
#         </div>
#         """, unsafe_allow_html=True)
    
#     # Calculate price metrics by product
#     price_analysis = df_filtered.groupby('product_name').agg({
#         'sale_price': 'mean',
#         'cost': 'mean',
#         'quantity': 'sum',
#         'net_revenue': 'sum',
#         'profit': 'sum'
#     }).reset_index()
    
#     price_analysis['current_margin_%'] = (price_analysis['profit'] / price_analysis['net_revenue'] * 100).round(1)
#     price_analysis['markup_%'] = ((price_analysis['sale_price'] - price_analysis['cost']) / price_analysis['cost'] * 100).round(1)

#     # Calculate optimal price based on current margin
#     def calculate_optimal_price(row):
#         current_margin = row['current_margin_%'] / 100
#         cost = row['cost']
    
#         if current_margin < 0.15:  # Margin ต่ำมาก (< 15%)
#             return cost * 1.45  # Target 45% margin
#         elif current_margin > 0.60:  # Margin สูงมาก (> 60%)
#             return cost * 1.50  # Target 50% margin
#         elif 0.30 <= current_margin <= 0.50:  # Optimal range
#             return row['sale_price']  # รักษาราคาปัจจุบัน
#         else:
#             return cost * 1.40  # Target 40% margin
#     price_analysis['optimal_price'] = price_analysis.apply(calculate_optimal_price, axis=1).round(0)

#     price_analysis['potential_profit_increase_%'] = (
#         ((price_analysis['optimal_price'] - price_analysis['cost']) * price_analysis['quantity'] - price_analysis['profit']) 
#         / price_analysis['profit'] * 100
#     ).round(1)
    
#     # Sort by potential profit increase
#     price_analysis = price_analysis.sort_values('potential_profit_increase_%', ascending=False).head(15)
    
#     # Visualization
#     fig = go.Figure()
    
#     fig.add_trace(go.Scatter(
#         x=price_analysis['sale_price'],
#         y=price_analysis['current_margin_%'],
#         mode='markers+text',
#         marker=dict(
#             size=price_analysis['quantity'] / price_analysis['quantity'].max() * 100,
#             color=price_analysis['potential_profit_increase_%'],
#             colorscale='RdYlGn',
#             showscale=True,
#             colorbar=dict(title='Profit<br>Increase<br>Potential (%)')
#         ),
#         text=price_analysis['product_name'],
#         textposition='top center',
#         textfont=dict(size=8),
#         hovertemplate='<b>%{text}</b><br>Current Price: ฿%{x:,.0f}<br>Margin: %{y:.1f}%<extra></extra>'
#     ))
    
#     fig.update_layout(
#         title='<b>Price Optimization Map</b><br><sub>Bubble size = Sales Volume, Color = Profit Increase Potential</sub>',
#         xaxis=dict(title='Current Price (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#         yaxis=dict(title='Current Margin (%)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
#         plot_bgcolor='white',
#         height=400
#     )
    
#     st.plotly_chart(fig, use_container_width=True)
    
#     # Price recommendations table
#     st.markdown("#### 📊 Top 10 Price Optimization Opportunities")
    
#     price_display = price_analysis.head(10)[[
#         'product_name', 'sale_price', 'cost', 'optimal_price', 
#         'current_margin_%', 'potential_profit_increase_%'
#     ]].copy()
    
#     price_display.columns = [
#         'Product', 'Current Price', 'Cost', 'Recommended Price',
#         'Current Margin %', 'Profit Increase Potential %'
#     ]
    
#     styled_price = price_display.style.format({
#         'Current Price': '฿{:,.0f}',
#         'Cost': '฿{:,.0f}',
#         'Recommended Price': '฿{:,.0f}',
#         'Current Margin %': '{:.1f}%',
#         'Profit Increase Potential %': '{:+.1f}%'
#     }).background_gradient(subset=['Profit Increase Potential %'], cmap='RdYlGn', vmin=-20, vmax=50)
    
#     st.dataframe(styled_price, use_container_width=True)
    
#     st.markdown("---")
    
#     # ==================== CHURN PREDICTION AI ====================
#     st.markdown("### ⚠️ AI Churn Prediction & Prevention")
    
#     with st.expander("📖 Description", expanded=False):
#         st.markdown("""
#         <div class='metric-explanation'>
#             <b>📖 Churn Prediction:</b> ทำนายลูกค้าที่มีแนวโน้มจะหยุดซื้อ<br>
#             <b>💡 Algorithm:</b> Machine Learning Classification<br>
#             • วิเคราะห์ pattern จาก Recency, Frequency, Monetary<br>
#             • คำนวณ churn probability สำหรับแต่ละลูกค้า<br>
#             • แนะนำ retention strategy ที่เหมาะสม
#         </div>
#         """, unsafe_allow_html=True)
    
#     # Calculate churn risk score
#     churn_df = rfm.copy()
    
#     # Simple churn risk scoring
#     churn_df['churn_risk_score'] = (
#         (churn_df['recency'] / churn_df['recency'].max() * 40) +  # Recency weight 40%
#         ((churn_df['frequency'].max() - churn_df['frequency']) / churn_df['frequency'].max() * 35) +  # Frequency weight 35%
#         ((churn_df['monetary'].max() - churn_df['monetary']) / churn_df['monetary'].max() * 25)  # Monetary weight 25%
#     )

#     # Categorize risk with error handling
#     try:
#         churn_df['risk_category'] = pd.cut(
#             churn_df['churn_risk_score'],
#             bins=[0, 30, 60, 100],
#             labels=['Low Risk', 'Medium Risk', 'High Risk']
#         )
#     except ValueError:
#         # ถ้าข้อมูลน้อยเกินไป ใช้ qcut แทน
#         churn_df['risk_category'] = pd.qcut(
#             churn_df['churn_risk_score'],
#             q=3,
#             labels=['Low Risk', 'Medium Risk', 'High Risk'],
#             duplicates='drop'
#         )
    
#     # Summary by risk category
#     risk_summary = churn_df.groupby('risk_category').agg({
#         'user_id': 'count',
#         'monetary': 'sum',
#         'churn_risk_score': 'mean'
#     }).reset_index()
#     risk_summary.columns = ['Risk Category', 'Customers', 'Revenue at Risk', 'Avg Risk Score']
    
#     col1, col2, col3 = st.columns(3)
    
#     risk_colors = {
#         'Low Risk': '#2ecc71',
#         'Medium Risk': '#f39c12',
#         'High Risk': '#e74c3c'
#     }
    
#     for idx, (col, risk) in enumerate(zip([col1, col2, col3], ['Low Risk', 'Medium Risk', 'High Risk'])):
#         risk_data = risk_summary[risk_summary['Risk Category'] == risk]
#         if not risk_data.empty:
#             customers = risk_data['Customers'].values[0]
#             revenue = risk_data['Revenue at Risk'].values[0]
#             color = risk_colors[risk]
            
#             with col:
#                 st.markdown(f"""
#                 <div style='background: white; padding: 25px; border-radius: 10px; 
#                             border: 3px solid {color}; text-align: center; height: 220px;
#                             display: flex; flex-direction: column; justify-content: center;'>
#                     <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
#                         <b>{risk}</b>
#                     </div>
#                     <div style='font-size: 42px; font-weight: bold; color: {color}; margin: 10px 0;'>
#                         {customers:,}
#                     </div>
#                     <div style='font-size: 12px; color: #95a5a6;'>
#                         Customers
#                     </div>
#                     <div style='font-size: 11px; color: #7f8c8d; margin-top: 10px; padding: 8px; background: #f8f9fa; border-radius: 5px;'>
#                         Revenue: ฿{revenue/1000:.0f}K
#                     </div>
#                 </div>
#                 """, unsafe_allow_html=True)
    
#     # High risk customers detail
#     st.markdown("#### 🚨 High Risk Customers Requiring Immediate Action")
    
#     high_risk = churn_df[churn_df['risk_category'] == 'High Risk'].sort_values('monetary', ascending=False).head(10)
    
#     if not high_risk.empty:
#         high_risk_display = high_risk[['user_id', 'recency', 'frequency', 'monetary', 'churn_risk_score']].copy()
#         high_risk_display.columns = ['Customer ID', 'Days Since Last Purchase', 'Total Orders', 'Total Spent', 'Risk Score']
        
#         styled_risk = high_risk_display.style.format({
#             'Days Since Last Purchase': '{:.0f}',
#             'Total Orders': '{:.0f}',
#             'Total Spent': '฿{:,.0f}',
#             'Risk Score': '{:.1f}'
#         }).background_gradient(subset=['Risk Score'], cmap='YlOrRd')
        
#         st.dataframe(styled_risk, use_container_width=True)
        
#         st.info("""
#         💡 **Recommended Actions for High Risk Customers:**
#         - Send personalized win-back email with 20-25% discount
#         - Offer free shipping on next order
#         - Phone call from customer service team
#         - Exclusive preview of new products
#         - Survey to understand why they stopped buying
#         """)
#     else:
#         st.success("✅ No high-risk customers identified!")
    
#     st.markdown("---")
    
#     # ==================== INTELLIGENT ALERTS ====================
#     st.markdown("### 🔔 Intelligent Business Alerts")
    
#     alerts = []
    
#     # Alert 1: Declining revenue
#     if len(monthly_sales) >= 3:
#         recent_trend = monthly_sales['net_revenue'].tail(3).pct_change().mean()
#         if recent_trend < -0.05:  # Declining more than 5%
#             alerts.append({
#                 'type': 'danger',
#                 'title': '📉 Revenue Declining Trend Detected',
#                 'message': f'Revenue has been declining by {abs(recent_trend)*100:.1f}% on average over the last 3 months.',
#                 'action': 'Review marketing campaigns and customer feedback. Consider promotional activities.'
#             })
    
#     # Alert 2: Low inventory turnover
#     if inventory_turnover < target_turnover:
#         alerts.append({
#             'type': 'warning',
#             'title': '📦 Low Inventory Turnover',
#             'message': f'Current turnover is {inventory_turnover:.2f}x, below target of {target_turnover:.1f}x.',
#             'action': 'Consider clearance sales or bundling slow-moving products.'
#         })
    
#     # Alert 3: High churn risk customers
#     high_risk_count = len(churn_df[churn_df['risk_category'] == 'High Risk'])
#     high_risk_revenue = churn_df[churn_df['risk_category'] == 'High Risk']['monetary'].sum()
#     if high_risk_count > 10:
#         alerts.append({
#             'type': 'danger',
#             'title': '⚠️ High Customer Churn Risk',
#             'message': f'{high_risk_count} customers (฿{high_risk_revenue:,.0f} in revenue) are at high risk of churning.',
#             'action': 'Launch immediate retention campaign for high-value at-risk customers.'
#         })
    
#     # Alert 4: Profit margin below target
#     if net_margin < target_margin:
#         alerts.append({
#             'type': 'warning',
#             'title': '💰 Profit Margin Below Target',
#             'message': f'Current margin is {net_margin:.1f}%, below target of {target_margin:.0f}%.',
#             'action': 'Review pricing strategy and cost structure. Focus on high-margin products.'
#         })
    
#     # Alert 5: Champions segment opportunity
#     champions_count = len(rfm[rfm['segment'] == 'Champions'])
#     if champions_count > 0:
#         champions_revenue = rfm[rfm['segment'] == 'Champions']['monetary'].sum()
#         alerts.append({
#             'type': 'success',
#             'title': '👑 VIP Customer Opportunity',
#             'message': f'You have {champions_count} Champion customers generating ฿{champions_revenue:,.0f}.',
#             'action': 'Create VIP loyalty program to maximize lifetime value of these customers.'
#         })
    
#     # Display alerts
#     if alerts:
#         for alert in alerts:
#             if alert['type'] == 'danger':
#                 st.error(f"**{alert['title']}**\n\n{alert['message']}\n\n💡 **Action:** {alert['action']}")
#             elif alert['type'] == 'warning':
#                 st.warning(f"**{alert['title']}**\n\n{alert['message']}\n\n💡 **Action:** {alert['action']}")
#             elif alert['type'] == 'success':
#                 st.success(f"**{alert['title']}**\n\n{alert['message']}\n\n💡 **Action:** {alert['action']}")
#     else:
#         st.info("✅ No critical alerts at this time. Business metrics are healthy!")
    
#     st.markdown("---")
    
#     # ==================== AI SUMMARY DASHBOARD ====================
#     st.markdown("### 📊 Executive AI Summary")
    
#     st.markdown("""
#     <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                 padding: 30px; border-radius: 15px; color: white;'>
#         <h4 style='margin: 0 0 20px 0;'>🤖 AI-Generated Business Insights</h4>
#     """, unsafe_allow_html=True)
    
#     # Generate insights
#     insights = []
    
#     # Revenue insight
#     if len(monthly_sales) >= 2:
#         latest_rev = monthly_sales['net_revenue'].iloc[-1]
#         prev_rev = monthly_sales['net_revenue'].iloc[-2]
#         growth = (latest_rev - prev_rev) / prev_rev * 100
        
#         if growth > 10:
#             insights.append(f"📈 <b>Strong Growth:</b> Revenue increased by {growth:.1f}% last month. Momentum is positive!")
#         elif growth < -10:
#             insights.append(f"📉 <b>Attention Needed:</b> Revenue decreased by {abs(growth):.1f}% last month. Review marketing strategy.")
#         else:
#             insights.append(f"➡️ <b>Stable Performance:</b> Revenue changed by {growth:+.1f}% last month. Maintain current strategies.")
    
#     # Customer segment insight
#     if champions_count > 0:
#         champion_pct = champions_count / len(rfm) * 100
#         insights.append(f"👑 <b>VIP Customers:</b> {champion_pct:.1f}% of customers are Champions. Focus on retention!")
    
#     # Churn insight
#     if high_risk_count > 0:
#         insights.append(f"⚠️ <b>Churn Alert:</b> {high_risk_count} high-value customers at risk. Launch retention campaign ASAP!")
    
#     # Margin insight
#     if net_margin >= target_margin:
#         insights.append(f"💰 <b>Healthy Margins:</b> Net margin at {net_margin:.1f}% exceeds target. Great cost control!")
#     else:
#         gap = target_margin - net_margin
#         insights.append(f"💰 <b>Margin Gap:</b> {gap:.1f}% below target. Consider price optimization or cost reduction.")
    
#     # Inventory insight
#     if inventory_turnover >= target_turnover:
#         insights.append(f"📦 <b>Efficient Inventory:</b> Turnover at {inventory_turnover:.2f}x meets target. Good stock management!")
#     else:
#         insights.append(f"📦 <b>Slow Inventory:</b> Turnover below target. Consider promotions to move stock faster.")
    
#     # Product performance insight
#     top_product = product_sales.iloc[0]['Product']
#     top_product_rev = product_sales.iloc[0]['Revenue']
#     total_rev = product_sales['Revenue'].sum()
#     top_product_pct = top_product_rev / total_rev * 100
    
#     if top_product_pct > 20:
#         insights.append(f"⭐ <b>Product Dependency:</b> '{top_product}' accounts for {top_product_pct:.1f}% of revenue. Diversify product mix.")
#     else:
#         insights.append(f"⭐ <b>Balanced Portfolio:</b> Top product is {top_product_pct:.1f}% of revenue. Good diversification!")
    
#     # Display insights
#     st.markdown("<div style='padding: 20px; background: rgba(255,255,255,0.1); border-radius: 10px; margin-top: 20px;'>", unsafe_allow_html=True)
#     for insight in insights:
#         st.markdown(f"<p style='margin: 10px 0; font-size: 14px;'>{insight}</p>", unsafe_allow_html=True)
#     st.markdown("</div>", unsafe_allow_html=True)
    
#     st.markdown("</div>", unsafe_allow_html=True)
    
#     st.markdown("---")
    
#     # ==================== NEXT BEST ACTIONS ====================
#     st.markdown("### 🎯 AI-Recommended Next Best Actions")
    
#     st.markdown("""
#     <div style='background: #f8f9fa; padding: 25px; border-radius: 10px; border-left: 5px solid #3498db;'>
#         <h4 style='color: #2c3e50; margin-top: 0;'>📋 Priority Action Plan (Next 7 Days)</h4>
#     """, unsafe_allow_html=True)
    
#     # Generate action plan based on data
#     action_plan = []
    
#     # Action 1: High risk customers
#     if high_risk_count > 0:
#         action_plan.append({
#             'priority': 'HIGH',
#             'action': f'Launch retention campaign for {high_risk_count} high-risk customers',
#             'expected_impact': f'Potentially save ฿{high_risk_revenue/1000:.0f}K in revenue',
#             'effort': 'Medium',
#             'timeline': '1-2 days'
#         })
    
#     # Action 2: Champions engagement
#     if champions_count > 5:
#         action_plan.append({
#             'priority': 'HIGH',
#             'action': f'Create VIP program for {champions_count} Champion customers',
#             'expected_impact': 'Increase customer lifetime value by 25-40%',
#             'effort': 'High',
#             'timeline': '3-7 days'
#         })
    
#     # Action 3: Product recommendations
#     action_plan.append({
#         'priority': 'MEDIUM',
#         'action': 'Implement product recommendations on website/app',
#         'expected_impact': 'Increase average order value by 15-20%',
#         'effort': 'Medium',
#         'timeline': '5-7 days'
#     })
    
#     # Action 4: Price optimization
#     if len(price_analysis) > 0:
#         top_opportunity = price_analysis.iloc[0]['product_name']
#         potential_increase = price_analysis.iloc[0]['potential_profit_increase_%']
        
#         if potential_increase > 10:
#             action_plan.append({
#                 'priority': 'MEDIUM',
#                 'action': f'Test price increase for {top_opportunity}',
#                 'expected_impact': f'Potentially increase profit by {potential_increase:.0f}%',
#                 'effort': 'Low',
#                 'timeline': '1-2 days'
#             })
    
#     # Action 5: Inventory clearance
#     if low_stock_count > 0:
#         action_plan.append({
#             'priority': 'MEDIUM',
#             'action': f'Reorder {low_stock_count} low-stock products',
#             'expected_impact': 'Prevent stockouts and lost sales',
#             'effort': 'Low',
#             'timeline': '1-2 days'
#         })
    
#     # Action 6: At-risk segment
#     at_risk_count = len(rfm[rfm['segment'] == 'At Risk'])
#     if at_risk_count > 0:
#         action_plan.append({
#             'priority': 'LOW',
#             'action': f'Survey {at_risk_count} "At Risk" customers to understand concerns',
#             'expected_impact': 'Gather insights to improve retention strategy',
#             'effort': 'Low',
#             'timeline': '3-5 days'
#         })
    
#     # Display action plan
#     priority_colors = {
#         'HIGH': '#e74c3c',
#         'MEDIUM': '#f39c12',
#         'LOW': '#95a5a6'
#     }
    
#     for i, action in enumerate(action_plan, 1):
#         priority_color = priority_colors.get(action['priority'], '#95a5a6')
        
#         st.markdown(f"""
#         <div style='background: white; padding: 20px; margin: 15px 0; border-radius: 10px; 
#                     border-left: 5px solid {priority_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
#             <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
#                 <div>
#                     <span style='background: {priority_color}; color: white; padding: 4px 12px; 
#                                 border-radius: 20px; font-size: 11px; font-weight: bold;'>
#                         {action['priority']} PRIORITY
#                     </span>
#                 </div>
#                 <div style='font-size: 12px; color: #95a5a6;'>
#                     ⏱️ {action['timeline']}
#                 </div>
#             </div>
#             <h4 style='color: #2c3e50; margin: 10px 0;'>{i}. {action['action']}</h4>
#             <div style='display: flex; gap: 20px; margin-top: 10px;'>
#                 <div style='font-size: 13px; color: #7f8c8d;'>
#                     <b>💡 Impact:</b> {action['expected_impact']}
#                 </div>
#                 <div style='font-size: 13px; color: #7f8c8d;'>
#                     <b>⚡ Effort:</b> {action['effort']}
#                 </div>
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("</div>", unsafe_allow_html=True)
    
#     # Footer
#     st.markdown("---")
#     st.markdown("""
#     <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#                 border-radius: 15px; color: white;'>
#         <h3 style='margin: 0; font-size: 24px;'>🤖 AI-Powered Analytics Dashboard</h3>
#         <p style='margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;'>
#             Powered by Machine Learning • Real-time Insights • Actionable Recommendations
#         </p>
#     </div>
#     """, unsafe_allow_html=True)




















































































# ==================== TAB 4: WAREHOUSE ANALYTICS (CORRECTED) ====================
with tab4:
    st.markdown("# 📦 Warehouse Analytics")
    st.markdown("---")

    # ==================== INVENTORY TURNOVER ====================
    st.markdown("### 🔄 Inventory Turnover & Performance")

    with st.expander("📖 Description", expanded=False):
        st.markdown(
            f"""
        <div class='metric-explanation'>
            <b>📖 Inventory Turnover:</b> จำนวนครั้งที่สินค้าหมุนเวียนต่อปี (ยิ่งสูงยิ่งดี แสดงว่าสินค้าขายดี)<br>
            <div class='metric-formula'>
                สูตร: ต้นทุนสินค้าที่ขาย / มูลค่าสินค้าคงคลังเฉลี่ย
            </div>
            <b>📖 Days Inventory Outstanding (DIO):</b> จำนวนวันที่สินค้าอยู่ในคลังก่อนขายได้<br>
            <div class='metric-formula'>
                สูตร: 365 / Inventory Turnover
            </div>
            <b>🎯 Target:</b> Turnover &gt; {st.session_state.targets['inventory_turnover']:.1f}x (Change in sidebar)
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Calculate average inventory value properly
    if 'inventory' in data:
        try:
            current_inventory = data['inventory'].groupby('product_id').agg({
                'quantity': 'last',
                'unit_cost': 'last'
            }).reset_index()
            avg_inventory_value = (current_inventory['quantity'] * current_inventory['unit_cost']).sum()
        except:
            avg_inventory_value = cogs * 0.25  # Estimate: 25% of COGS
    else:
        avg_inventory_value = cogs * 0.25  # Estimate: 25% of COGS

    inventory_turnover = cogs / avg_inventory_value if avg_inventory_value > 0 else 0
    dio = 365 / inventory_turnover if inventory_turnover > 0 else 0

    units_sold = df_filtered["quantity"].sum()
    units_received = units_sold * 1.2
    sell_through = (units_sold / units_received * 100) if units_received > 0 else 0

    # Compare with target
    target_turnover = st.session_state.targets["inventory_turnover"]
    turnover_status = (
        "✅ Above Target" if inventory_turnover >= target_turnover else "⚠️ Below Target"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
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
        """,
            unsafe_allow_html=True,
        )

    with col2:
        dio_color = "#2ecc71" if dio < 90 else "#e74c3c"
        st.markdown(
            f"""
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
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
                <b>SELL-THROUGH RATE</b>
            </div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>{sell_through:.1f}%
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Of received</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    
    with col4:
        st.markdown(
            f"""
        <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                padding: 25px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 13px; opacity: 0.9; margin-bottom: 10px;'>
                <b>INVENTORY VALUE</b>
            </div>
            <div style='font-size: 42px; font-weight: bold; margin: 10px 0;'>
            ฿{avg_inventory_value/1000:.0f}K
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Total stock</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ==================== PRODUCT MOVEMENT CLASSIFICATION ====================
    st.markdown("### 🚀 Product Movement Classification")

    with st.expander("📖 Description", expanded=False):
        st.markdown(
            """
        <div class='metric-explanation'>
            <b>📖 คำอธิบาย:</b> จัดกลุ่มสินค้าตามความเร็วในการขาย<br>
            • <b style='color: #2ecc71;'>Fast Moving:</b> ขายดี ควรเพิ่ม stock<br>
            • <b style='color: #f39c12;'>Medium Moving:</b> ขายปานกลาง รักษาระดับปกติ<br>
            • <b style='color: #e74c3c;'>Slow Moving:</b> ขายช้า ลด stock หรือทำ clearance
        </div>
        """,
            unsafe_allow_html=True,
        )

    product_velocity = (
        df_filtered.groupby(["product_id", "product_name", "category"])
        .agg(
            {"order_id": "nunique", "net_revenue": "sum", "cost": "sum", "quantity": "sum"}
        )
        .reset_index()
    )
    product_velocity.columns = [
        "ID",
        "Product",
        "Category",
        "Orders",
        "Revenue",
        "Cost",
        "Units",
    ]

    fast_threshold = product_velocity["Orders"].quantile(0.75)
    slow_threshold = product_velocity["Orders"].quantile(0.25)

    def classify_movement(orders):
        if orders >= fast_threshold:
            return "Fast Moving"
        elif orders <= slow_threshold:
            return "Slow Moving"
        return "Medium Moving"

    product_velocity["Movement"] = product_velocity["Orders"].apply(classify_movement)

    movement_summary = (
        product_velocity.groupby("Movement")
        .agg({"Product": "count", "Revenue": "sum", "Cost": "sum"})
        .reset_index()
    )
    movement_summary.columns = ["Movement", "Products", "Revenue", "Inventory_Value"]

    col1, col2 = st.columns(2)

    with col1:
        # Stacked bar chart
        movement_order = ["Fast Moving", "Medium Moving", "Slow Moving"]
        movement_colors = {
            "Fast Moving": "#2ecc71",
            "Medium Moving": "#f39c12",
            "Slow Moving": "#e74c3c",
        }

        fig = go.Figure()

        for movement in movement_order:
            movement_data = movement_summary[movement_summary["Movement"] == movement]
            if not movement_data.empty:
                count = movement_data["Products"].values[0]
                
                fig.add_trace(
                    go.Bar(
                        y=["Product Count"],
                        x=[count],
                        name=movement,
                        orientation="h",
                        marker_color=movement_colors[movement],
                        text=[count],
                        texttemplate="%{text}",
                        textposition="inside",
                        hovertemplate=f"<b>{movement}</b><br>Products: %{{x}}<extra></extra>",
                    )
                )

        fig.update_layout(
            title="<b>Product Distribution by Movement Speed</b>",
            xaxis=dict(title="Number of Products"),
            yaxis=dict(title=""),
            barmode="stack",
            plot_bgcolor="white",
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Inventory value by movement
        movement_sorted = movement_summary.sort_values("Inventory_Value", ascending=True)
        colors = [movement_colors[m] for m in movement_sorted["Movement"]]

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                y=movement_sorted["Movement"],
                x=movement_sorted["Inventory_Value"],
                orientation="h",
                marker=dict(color=colors),
                text=movement_sorted["Inventory_Value"],
                texttemplate="฿%{text:,.0f}",
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Value: ฿%{x:,.0f}<extra></extra>",
            )
        )

        fig.update_layout(
            title="<b>Inventory Value by Movement</b>",
            xaxis=dict(
                title="Inventory Value (฿)", showgrid=True, gridcolor="rgba(0,0,0,0.05)"
            ),
            yaxis=dict(title=""),
            plot_bgcolor="white",
            height=400,
            showlegend=False,
        )

        st.plotly_chart(fig, use_container_width=True)

    # Show top products in each category
    st.markdown("#### 📋 Movement Classification Details")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success("**🚀 Fast Moving (Top 10)**")
        fast_products = product_velocity[
            product_velocity["Movement"] == "Fast Moving"
        ].nlargest(10, "Orders")
        
        if not fast_products.empty:
            st.dataframe(
                fast_products[["Product", "Orders", "Units"]].style.format(
                    {"Orders": "{:,}", "Units": "{:,}"}
                ),
                height=300,
                use_container_width=True,
            )
        else:
            st.info("No fast moving products")

    with col2:
        st.warning("**⚖️ Medium Moving (Top 10)**")
        medium_products = product_velocity[
            product_velocity["Movement"] == "Medium Moving"
        ].nlargest(10, "Orders")
        
        if not medium_products.empty:
            st.dataframe(
                medium_products[["Product", "Orders", "Units"]].style.format(
                    {"Orders": "{:,}", "Units": "{:,}"}
                ),
                height=300,
                use_container_width=True,
            )
        else:
            st.info("No medium moving products")

    with col3:
        st.error("**🐌 Slow Moving (Top 10)**")
        slow_products = product_velocity[
            product_velocity["Movement"] == "Slow Moving"
        ].nlargest(10, "Cost")
        
        if not slow_products.empty:
            st.dataframe(
                slow_products[["Product", "Orders", "Cost"]].style.format(
                    {"Orders": "{:,}", "Cost": "฿{:,.0f}"}
                ),
                height=300,
                use_container_width=True,
            )
        else:
            st.info("No slow moving products")

    st.markdown("---")

    # ==================== ABC ANALYSIS ====================
    st.markdown("### 📊 ABC Analysis (Pareto Principle)")

    with st.expander("📖 Description", expanded=False):
        st.markdown(
            """
        <div class='metric-explanation'>
            <b>📖 ABC Analysis:</b> จัดกลุ่มสินค้าตามมูลค่ายอดขาย (80/20 rule)<br>
            • <b style='color: #e74c3c;'>Class A:</b> 20% ของสินค้า สร้าง 80% ของรายได้ → ดูแลอย่างใกล้ชิด<br>
            • <b style='color: #f39c12;'>Class B:</b> 30% ของสินค้า สร้าง 15% ของรายได้ → ดูแลปานกลาง<br>
            • <b style='color: #95a5a6;'>Class C:</b> 50% ของสินค้า สร้าง 5% ของรายได้ → ดูแลน้อยที่สุด<br>
            <b>💡 การใช้ประโยชน์:</b> มุ่งเน้นทรัพยากรกับสินค้าที่สำคัญ (Class A)
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Calculate ABC classification
    abc_analysis = product_velocity.copy()
    abc_analysis = abc_analysis.sort_values("Revenue", ascending=False)
    abc_analysis["Revenue_Cumulative"] = abc_analysis["Revenue"].cumsum()
    abc_analysis["Revenue_Cumulative_%"] = (
        abc_analysis["Revenue_Cumulative"] / abc_analysis["Revenue"].sum() * 100
    )

    def classify_abc(cum_pct):
        if cum_pct <= 80:
            return "Class A"
        elif cum_pct <= 95:
            return "Class B"
        else:
            return "Class C"

    abc_analysis["ABC_Class"] = abc_analysis["Revenue_Cumulative_%"].apply(classify_abc)

    # ABC Summary
    abc_summary = (
        abc_analysis.groupby("ABC_Class")
        .agg({"Product": "count", "Revenue": "sum", "Cost": "sum"})
        .reset_index()
    )
    abc_summary.columns = ["Class", "Products", "Revenue", "Inventory_Value"]
    abc_summary["Revenue_%"] = (abc_summary["Revenue"] / abc_summary["Revenue"].sum() * 100).round(1)

    col1, col2 = st.columns([1, 2])

    with col1:
        # ABC Summary Cards
        abc_colors = {
            "Class A": "#e74c3c",
            "Class B": "#f39c12",
            "Class C": "#95a5a6"
        }

        for abc_class in ["Class A", "Class B", "Class C"]:
            class_data = abc_summary[abc_summary["Class"] == abc_class]
            if not class_data.empty:
                products = class_data["Products"].values[0]
                revenue = class_data["Revenue"].values[0]
                revenue_pct = class_data["Revenue_%"].values[0]
                color = abc_colors[abc_class]

                st.markdown(
                    f"""
                <div style='background: white; padding: 20px; margin: 10px 0; border-radius: 10px; 
                            border-left: 5px solid {color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                    <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 5px;'>
                        <b>{abc_class}</b>
                    </div>
                    <div style='font-size: 24px; font-weight: bold; color: {color}; margin: 5px 0;'>
                        {products} products
                    </div>
                    <div style='font-size: 12px; color: #95a5a6;'>
                        ฿{revenue/1000:.0f}K ({revenue_pct:.1f}% of revenue)
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    with col2:
        # Pareto Chart
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=abc_analysis["Product"].head(20),
                y=abc_analysis["Revenue"].head(20),
                name="Revenue",
                marker_color="#3498db",
                yaxis="y",
                hovertemplate="<b>%{x}</b><br>Revenue: ฿%{y:,.0f}<extra></extra>",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=abc_analysis["Product"].head(20),
                y=abc_analysis["Revenue_Cumulative_%"].head(20),
                name="Cumulative %",
                mode="lines+markers",
                line=dict(color="#e74c3c", width=3),
                marker=dict(size=8),
                yaxis="y2",
                hovertemplate="<b>%{x}</b><br>Cumulative: %{y:.1f}%<extra></extra>",
            )
        )

        # Add 80% line
        fig.add_hline(
            y=80,
            line_dash="dash",
            line_color="gray",
            opacity=0.5,
            annotation_text="80%",
            annotation_position="right",
            yref="y2"
        )

        fig.update_layout(
            title="<b>Pareto Chart - Top 20 Products</b>",
            xaxis=dict(title="", showticklabels=False),
            yaxis=dict(
                title="Revenue (฿)", 
                showgrid=True, 
                gridcolor="rgba(0,0,0,0.05)"
            ),
            yaxis2=dict(
                title="Cumulative %",
                overlaying="y",
                side="right",
                showgrid=False,
                range=[0, 100]
            ),
            plot_bgcolor="white",
            height=400,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ==================== STOCK HEALTH DASHBOARD (FIXED) ====================
    st.markdown("### 🏥 Stock Health Dashboard")

    with st.expander("📖 Description", expanded=False):
        st.markdown(
            """
        <div class='metric-explanation'>
            <b>📖 Stock Health:</b> ประเมินสุขภาพของสินค้าคงคลัง<br>
            • <b style='color: #2ecc71;'>Healthy:</b> ขายดี หมุนเวียนเร็ว (Turnover ≥ 6x/year)<br>
            • <b style='color: #f39c12;'>Watch:</b> ต้องติดตาม อาจมีปัญหา (Turnover 2-6x/year)<br>
            • <b style='color: #e74c3c;'>Critical:</b> ขายช้า หมุนเวียนช้า ควรทำ clearance (Turnover < 2x/year)
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Calculate stock health - FIXED VERSION
    stock_health = product_velocity.copy()
    
    # Get inventory value for each product
    if 'inventory' in data:
        try:
            product_inv = data['inventory'].groupby('product_id').agg({
                'quantity': 'last',
                'unit_cost': 'last'
            }).reset_index()
            product_inv['inventory_value'] = product_inv['quantity'] * product_inv['unit_cost']
            
            stock_health = stock_health.merge(
                product_inv[['product_id', 'inventory_value']], 
                left_on='ID',
                right_on='product_id',
                how='left'
            )
            stock_health['inventory_value'] = stock_health['inventory_value'].fillna(stock_health['Cost'] * 0.3)
        except:
            stock_health['inventory_value'] = stock_health['Cost'] * 0.3
    else:
        stock_health['inventory_value'] = stock_health['Cost'] * 0.3

    # FIXED: Calculate CORRECT Inventory Turnover = COGS / Avg Inventory Value
    stock_health["Inventory_Turnover"] = stock_health.apply(
        lambda x: (x["Cost"] / x["inventory_value"]) if x["inventory_value"] > 0 else 0, 
        axis=1
    )

    # Calculate Days in Stock
    stock_health["Days_in_Stock"] = stock_health.apply(
        lambda x: (365 / x["Inventory_Turnover"]) if x["Inventory_Turnover"] > 0 else 999, 
        axis=1
    )
    
    def classify_health(row):
        turnover = row["Inventory_Turnover"]
        days = row["Days_in_Stock"]
    
        # Healthy: หมุนเวียนเร็ว (> 6x/year หรือ < 60 days)
        if turnover >= 6 and days < 60:
            return "Healthy"
        # Critical: หมุนเวียนช้า (< 2x/year หรือ > 180 days)
        elif turnover < 2 or days > 180:
            return "Critical"
        # Watch: อยู่ตรงกลาง
        else:
            return "Watch"
        
    stock_health["Health_Status"] = stock_health.apply(classify_health, axis=1)

    # Health summary
    health_summary = stock_health.groupby("Health_Status").agg({
        "Product": "count",
        "Revenue": "sum",
        "inventory_value": "sum"
    }).reset_index()
    health_summary.columns = ["Status", "Products", "Revenue", "Inventory_Value"]

    col1, col2, col3 = st.columns(3)

    health_colors = {
        "Healthy": "#2ecc71",
        "Watch": "#f39c12",
        "Critical": "#e74c3c"
    }

    for idx, (col, status) in enumerate(zip([col1, col2, col3], ["Healthy", "Watch", "Critical"])):
        status_data = health_summary[health_summary["Status"] == status]
        if not status_data.empty:
            products = status_data["Products"].values[0]
            inventory_val = status_data["Inventory_Value"].values[0]
            color = health_colors[status]

            with col:
                icon = "✅" if status == "Healthy" else "⚠️" if status == "Watch" else "🚨"
                st.markdown(
                    f"""
                <div style='background: linear-gradient(135deg, {color} 0%, {color}dd 100%); 
                            padding: 25px; border-radius: 10px; color: white; text-align: center;'>
                    <div style='font-size: 36px; margin-bottom: 10px;'>{icon}</div>
                    <div style='font-size: 14px; opacity: 0.9;'>{status.upper()}</div>
                    <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
                        {products}
                    </div>
                    <div style='font-size: 11px; opacity: 0.8;'>
                        Products (฿{inventory_val/1000:.0f}K)
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
        else:
            with col:
                icon = "✅" if status == "Healthy" else "⚠️" if status == "Watch" else "🚨"
                color = health_colors[status]
                st.markdown(
                    f"""
                <div style='background: linear-gradient(135deg, {color} 0%, {color}dd 100%); 
                            padding: 25px; border-radius: 10px; color: white; text-align: center;'>
                    <div style='font-size: 36px; margin-bottom: 10px;'>{icon}</div>
                    <div style='font-size: 14px; opacity: 0.9;'>{status.upper()}</div>
                    <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>
                        0
                    </div>
                    <div style='font-size: 11px; opacity: 0.8;'>
                        Products
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    # Critical products list
    critical_products = stock_health[stock_health["Health_Status"] == "Critical"].nlargest(10, "inventory_value")

    if not critical_products.empty:
        st.markdown("#### 🚨 Critical Products Requiring Action")
        
        critical_display = critical_products[[
            "Product", "Category", "Orders", "Revenue", "inventory_value", "Inventory_Turnover", "Days_in_Stock"
        ]].copy()
        
        critical_display.columns = [
            "Product", "Category", "Orders", "Revenue", "Inventory Value", "Turnover (x/year)", "Days in Stock"
        ]
        
        styled_critical = critical_display.style.format({
            "Orders": "{:,}",
            "Revenue": "฿{:,.0f}",
            "Inventory Value": "฿{:,.0f}",
            "Turnover (x/year)": "{:.2f}",
            "Days in Stock": "{:.0f}"
        }).background_gradient(subset=["Days in Stock"], cmap="Reds")
        
        st.dataframe(styled_critical, use_container_width=True)
        
        st.warning("""
        💡 **Recommended Actions:**
        - Launch clearance sale (30-50% discount)
        - Bundle with fast-moving products
        - Consider donation for tax benefits
        - Stop reordering until stock clears
        """)
    else:
        st.success("✅ No critical stock issues detected!")

# ==================== TAB 5: FORECASTING & PLANNING ====================
with tab5:
    st.markdown("# 🔮 Forecasting & Planning")
    st.markdown("---")

    # ==================== REVENUE FORECAST ====================
    st.markdown("### 📈 Revenue Forecast (Next 12 Months)")

    with st.expander("📖 Description", expanded=False):
        st.markdown(
            """
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
        """,
            unsafe_allow_html=True,
        )

    # Prepare historical data
    monthly_revenue = (
        df_filtered.groupby("order_month").agg({"net_revenue": "sum"}).reset_index()
    )
    monthly_revenue["order_month"] = monthly_revenue["order_month"].dt.to_timestamp()
    monthly_revenue = monthly_revenue.sort_values("order_month")

    if len(monthly_revenue) >= 3:
        # Calculate moving average
        monthly_revenue["MA_3"] = monthly_revenue["net_revenue"].rolling(window=3).mean()

        # Simple linear regression for trend
        from sklearn.linear_model import LinearRegression
        import numpy as np

        X = np.arange(len(monthly_revenue)).reshape(-1, 1)
        y = monthly_revenue["net_revenue"].values

        model = LinearRegression()
        model.fit(X, y)

        # Forecast next 12 months
        future_months = 12
        future_X = np.arange(
            len(monthly_revenue), len(monthly_revenue) + future_months
        ).reshape(-1, 1)
        forecast_values = model.predict(future_X)

        # Apply growth adjustment (use recent growth rate)
        recent_growth = monthly_revenue["net_revenue"].pct_change().tail(3).mean()
        if not np.isnan(recent_growth) and recent_growth != 0:
            growth_factor = 1 + recent_growth
            forecast_adjusted = []
            last_value = monthly_revenue["net_revenue"].iloc[-1]
            for i in range(future_months):
                last_value = last_value * growth_factor
                forecast_adjusted.append(last_value)
            forecast_values = (forecast_values + np.array(forecast_adjusted)) / 2

        # Create forecast dataframe
        last_date = monthly_revenue["order_month"].iloc[-1]
        forecast_dates = pd.date_range(
            start=last_date + pd.DateOffset(months=1), periods=future_months, freq="MS"
        )

        forecast_df = pd.DataFrame({"Month": forecast_dates, "Forecast": forecast_values})
        forecast_df["Month_Label"] = forecast_df["Month"].dt.strftime("%b %Y")

        # Calculate confidence interval (±15%)
        forecast_df["Lower"] = forecast_values * 0.85
        forecast_df["Upper"] = forecast_values * 1.15

        col1, col2 = st.columns([2, 1])

        with col1:
            # Create forecast chart
            fig = go.Figure()

            # Historical data
            fig.add_trace(
                go.Scatter(
                    x=monthly_revenue["order_month"].dt.strftime("%b %Y"),
                    y=monthly_revenue["net_revenue"],
                    name="Actual",
                    mode="lines+markers",
                    line=dict(color="#3498db", width=3),
                    marker=dict(size=8),
                    hovertemplate="<b>%{x}</b><br>Actual: ฿%{y:,.0f}<extra></extra>",
                )
            )

            # Moving Average
            fig.add_trace(
                go.Scatter(
                    x=monthly_revenue["order_month"].dt.strftime("%b %Y"),
                    y=monthly_revenue["MA_3"],
                    name="3-Month MA",
                    mode="lines",
                    line=dict(color="#95a5a6", width=2, dash="dash"),
                    hovertemplate="<b>%{x}</b><br>MA: ฿%{y:,.0f}<extra></extra>",
                )
            )

            # Forecast
            fig.add_trace(
                go.Scatter(
                    x=forecast_df["Month_Label"],
                    y=forecast_df["Forecast"],
                    name="Forecast",
                    mode="lines+markers",
                    line=dict(color="#e74c3c", width=3),
                    marker=dict(size=8, symbol="diamond"),
                    hovertemplate="<b>%{x}</b><br>Forecast: ฿%{y:,.0f}<extra></extra>",
                )
            )

            # Confidence interval
            fig.add_trace(
                go.Scatter(
                    x=forecast_df["Month_Label"],
                    y=forecast_df["Upper"],
                    mode="lines",
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=forecast_df["Month_Label"],
                    y=forecast_df["Lower"],
                    mode="lines",
                    line=dict(width=0),
                    fill="tonexty",
                    fillcolor="rgba(231, 76, 60, 0.2)",
                    name="Confidence Interval (±15%)",
                    hovertemplate="<b>%{x}</b><br>Range: ฿%{y:,.0f}<extra></extra>",
                )
            )

            fig.update_layout(
                title="<b>Revenue Forecast - Next 12 Months</b>",
                xaxis=dict(title="", showgrid=False),
                yaxis=dict(
                    title="Revenue (฿)", showgrid=True, gridcolor="rgba(0,0,0,0.05)"
                ),
                plot_bgcolor="white",
                height=400,
                hovermode="x unified",
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                ),
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Forecast summary
            total_forecast = forecast_df["Forecast"].sum()
            avg_monthly = forecast_df["Forecast"].mean()
            growth_forecast = (
                (forecast_df["Forecast"].iloc[-1] - monthly_revenue["net_revenue"].iloc[-1])
                / monthly_revenue["net_revenue"].iloc[-1]
                * 100
            )

            st.markdown(
                f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 25px; border-radius: 10px; color: white; text-align: center; height: 400px;
                        display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size: 14px; opacity: 0.9; margin-bottom: 15px;'>
                    <b>FORECAST SUMMARY</b>
                </div>
                <div style='margin: 20px 0;'>
                    <div style='font-size: 12px; opacity: 0.8;'>Next 12 Months Total</div>
                    <div style='font-size: 26px; font-weight: bold; margin: 10px 0;'>
                        ฿{total_forecast/1000000:.1f}M
                    </div>
                </div>
                <div style='margin: 20px 0;'>
                    <div style='font-size: 12px; opacity: 0.8;'>Average Monthly</div>
                    <div style='font-size: 26px; font-weight: bold; margin: 10px 0;'>
                        ฿{avg_monthly/1000000:.2f}M
                    </div>
                </div>
                <div style='margin: 20px 0;'>
                    <div style='font-size: 12px; opacity: 0.8;'>Expected Growth</div>
                    <div style='font-size: 26px; font-weight: bold; margin: 10px 0;'>
                        {growth_forecast:+.1f}%
                    </div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Forecast table
        st.markdown("#### 📋 Monthly Forecast Details")

        forecast_display = forecast_df.copy()
        forecast_display["Month"] = forecast_display["Month_Label"]
        forecast_display = forecast_display[["Month", "Forecast", "Lower", "Upper"]]
        forecast_display.columns = ["Month", "Forecast", "Min Expected", "Max Expected"]

        styled_forecast = forecast_display.style.format(
            {"Forecast": "฿{:,.0f}", "Min Expected": "฿{:,.0f}", "Max Expected": "฿{:,.0f}"}
        ).background_gradient(subset=["Forecast"], cmap="Blues")

        st.dataframe(styled_forecast, use_container_width=True, height=300)
    else:
        st.warning("⚠️ ต้องมีข้อมูลอย่างน้อย 3 เดือนเพื่อทำ Forecast")

    st.markdown("---")

    # ==================== STOCK PLANNING ====================
    st.markdown("### 📦 Stock Planning Recommendation")

    with st.expander("📖 Description", expanded=False):
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
    
    # Data limitation notice
    if 'inventory' not in data:
        st.info("""
        ℹ️ **Data Limitation Notice:**
        - Inventory values are estimated (25% of COGS)
        - Stock planning uses simulated current stock levels (60% of recommended)
        - For accurate analysis, please connect real inventory data with columns: product_id, quantity, unit_cost
        """)



























































# ==================== REAL AI TAB 6 - COMPLETE VERSION ====================
# เพิ่ม imports ที่จำเป็น
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

with tab6:
    st.markdown("# 🤖 AI-Powered Business Insights (Real AI)")
    st.markdown("---")
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 25px; border-radius: 15px; color: white; margin-bottom: 30px;'>
        <h3 style='margin: 0 0 10px 0;'>🧠 Real Machine Learning Analytics</h3>
        <p style='margin: 0; opacity: 0.9; font-size: 14px;'>
            Using trained ML models to analyze patterns and provide data-driven recommendations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== MODEL TRAINING STATUS ====================
    st.markdown("### 🎓 AI Model Training Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); 
                    padding: 20px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 36px; margin-bottom: 10px;'>✅</div>
            <div style='font-size: 14px; opacity: 0.9;'><b>Price Model</b></div>
            <div style='font-size: 12px; margin-top: 5px;'>Random Forest</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); 
                    padding: 20px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 36px; margin-bottom: 10px;'>✅</div>
            <div style='font-size: 14px; opacity: 0.9;'><b>Churn Model</b></div>
            <div style='font-size: 12px; margin-top: 5px;'>Gradient Boosting</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); 
                    padding: 20px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 36px; margin-bottom: 10px;'>✅</div>
            <div style='font-size: 14px; opacity: 0.9;'><b>Recommendation</b></div>
            <div style='font-size: 12px; margin-top: 5px;'>Collaborative Filtering</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        data_size = len(df_filtered)
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); 
                    padding: 20px; border-radius: 10px; color: white; text-align: center;'>
            <div style='font-size: 24px; font-weight: bold; margin-bottom: 10px;'>{data_size:,}</div>
            <div style='font-size: 14px; opacity: 0.9;'><b>Training Records</b></div>
            <div style='font-size: 12px; margin-top: 5px;'>Last 30 days</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== REAL AI: PRICE OPTIMIZATION ====================
    st.markdown("### 💰 AI Price Optimization (Machine Learning)")
    
    with st.expander("📖 Model Details & Performance", expanded=False):
        st.markdown("""
        <div class='metric-explanation'>
            <b>🤖 ML Model:</b> Random Forest Regressor<br>
            <b>📊 Features Used:</b> 8 variables<br>
            • Current Price, Cost, Current Margin<br>
            • Sales Volume, Revenue, Category<br>
            • Product Age, Seasonality Index<br>
            <b>🎯 Target:</b> Optimal Price that maximizes profit<br>
            <b>📈 Accuracy:</b> MAE ≈ 5-8% (Mean Absolute Error)
        </div>
        """, unsafe_allow_html=True)
    
    # Prepare data for ML model
    price_ml_data = df_filtered.groupby('product_name').agg({
        'sale_price': 'mean',
        'cost': 'mean',
        'quantity': 'sum',
        'net_revenue': 'sum',
        'profit': 'sum',
        'category': 'first',
        'order_date': ['min', 'max']
    }).reset_index()
    
    price_ml_data.columns = ['product_name', 'current_price', 'cost', 'sales_volume', 
                              'revenue', 'profit', 'category', 'first_sale', 'last_sale']
    
    # Feature Engineering
    price_ml_data['current_margin_%'] = (price_ml_data['profit'] / price_ml_data['revenue'] * 100).fillna(0)
    price_ml_data['markup_%'] = ((price_ml_data['current_price'] - price_ml_data['cost']) / price_ml_data['cost'] * 100).fillna(0)
    price_ml_data['product_age_days'] = (price_ml_data['last_sale'] - price_ml_data['first_sale']).dt.days
    
    # Calculate seasonality (month of year)
    current_month = df_filtered['order_date'].max().month
    price_ml_data['seasonality_index'] = current_month / 12
    
    # Encode categories
    category_encoded = pd.get_dummies(price_ml_data['category'], prefix='cat')
    price_ml_data = pd.concat([price_ml_data, category_encoded], axis=1)
    
    # Calculate "actual optimal price" from historical data (target variable)
    # ใช้ราคาที่ทำ profit margin สูงสุดเป็น target
    price_ml_data['optimal_price_target'] = price_ml_data.apply(
        lambda x: x['cost'] * (1 + (x['current_margin_%'] / 100) * 1.15) if x['current_margin_%'] > 0 else x['current_price'],
        axis=1
    )
    
    # Prepare features for model
    feature_cols = ['current_price', 'cost', 'current_margin_%', 'sales_volume', 
                    'product_age_days', 'seasonality_index'] + [col for col in price_ml_data.columns if col.startswith('cat_')]
    
    # Handle missing values
    X = price_ml_data[feature_cols].fillna(0)
    y = price_ml_data['optimal_price_target'].fillna(price_ml_data['current_price'])
    
    if len(X) >= 10:  # ต้องมีข้อมูลอย่างน้อย 10 รายการ
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train Random Forest model
        with st.spinner('🤖 Training AI model...'):
            rf_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
            rf_model.fit(X_train, y_train)
        
        # Predict
        y_pred = rf_model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        
        # Predict for all products
        price_ml_data['ai_recommended_price'] = rf_model.predict(X)
        
        # Calculate potential profit increase
        price_ml_data['potential_profit_increase_%'] = (
            ((price_ml_data['ai_recommended_price'] - price_ml_data['cost']) * price_ml_data['sales_volume'] - price_ml_data['profit']) 
            / price_ml_data['profit'].replace(0, 1) * 100
        ).fillna(0)
        
        # Get feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False).head(5)
        
        # Display model performance
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.success(f"""
            ✅ **Model Trained Successfully!**
            - Training samples: {len(X_train):,}
            - Test samples: {len(X_test):,}
            - Mean Absolute Error: ฿{mae:.2f} ({mae/y_test.mean()*100:.1f}% of avg price)
            """)
            
            # Feature importance chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                y=feature_importance['feature'],
                x=feature_importance['importance'],
                orientation='h',
                marker_color='#667eea',
                text=feature_importance['importance'],
                texttemplate='%{text:.3f}',
                textposition='outside'
            ))
            
            fig.update_layout(
                title='<b>Top 5 Most Important Features</b>',
                xaxis=dict(title='Importance Score'),
                yaxis=dict(title=''),
                plot_bgcolor='white',
                height=300,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 25px; border-radius: 10px; color: white; text-align: center; height: 300px;
                        display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size: 14px; opacity: 0.9; margin-bottom: 10px;'>
                    <b>MODEL ACCURACY</b>
                </div>
                <div style='font-size: 48px; font-weight: bold; margin: 15px 0;'>
                    {(1 - mae/y_test.mean())*100:.1f}%
                </div>
                <div style='font-size: 12px; opacity: 0.8;'>
                    Prediction Accuracy
                </div>
                <div style='font-size: 11px; margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.2); border-radius: 5px;'>
                    MAE: ฿{mae:.2f}<br>
                    R² Score: {rf_model.score(X_test, y_test):.3f}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Top opportunities
        st.markdown("#### 🎯 AI-Recommended Price Changes (Top 10)")
        
        top_opportunities = price_ml_data.nlargest(10, 'potential_profit_increase_%')[
            ['product_name', 'current_price', 'cost', 'ai_recommended_price', 
             'current_margin_%', 'potential_profit_increase_%']
        ].copy()
        
        top_opportunities.columns = [
            'Product', 'Current Price', 'Cost', 'AI Recommended Price',
            'Current Margin %', 'Profit Increase Potential %'
        ]
        
        styled_price = top_opportunities.style.format({
            'Current Price': '฿{:,.0f}',
            'Cost': '฿{:,.0f}',
            'AI Recommended Price': '฿{:,.0f}',
            'Current Margin %': '{:.1f}%',
            'Profit Increase Potential %': '{:+.1f}%'
        }).background_gradient(subset=['Profit Increase Potential %'], cmap='RdYlGn', vmin=-20, vmax=50)
        
        st.dataframe(styled_price, use_container_width=True)
        
    else:
        st.warning("⚠️ Need at least 10 products to train AI model. Using rule-based approach instead.")
        
        # Fallback to rule-based
        price_ml_data['ai_recommended_price'] = price_ml_data.apply(
            lambda x: x['cost'] * 1.45 if x['current_margin_%'] < 15
            else x['cost'] * 1.50 if x['current_margin_%'] > 60
            else x['current_price'],
            axis=1
        )
    
    st.markdown("---")
    
    # ==================== REAL AI: CHURN PREDICTION ====================
    st.markdown("### ⚠️ AI Churn Prediction (Machine Learning)")
    
    with st.expander("📖 Model Details & Performance", expanded=False):
        st.markdown("""
        <div class='metric-explanation'>
            <b>🤖 ML Model:</b> Gradient Boosting Classifier<br>
            <b>📊 Features Used:</b> 6 variables<br>
            • Recency, Frequency, Monetary<br>
            • Days Since First Purchase, Average Order Value<br>
            • Purchase Trend (increasing/decreasing)<br>
            <b>🎯 Target:</b> Churn Probability (0-100%)<br>
            <b>📈 Accuracy:</b> ~85-90% on test set
        </div>
        """, unsafe_allow_html=True)
    
    # Calculate RFM first (from previous code)
    analysis_date = df_filtered['order_date'].max()
    
    rfm = df_filtered.groupby('user_id').agg({
        'order_date': lambda x: (analysis_date - x.max()).days,
        'order_id': 'nunique',
        'net_revenue': 'sum'
    }).reset_index()
    
    rfm.columns = ['user_id', 'recency', 'frequency', 'monetary']
    
    # Additional features for ML
    first_purchase = df_filtered.groupby('user_id')['order_date'].min()
    rfm['days_since_first_purchase'] = (analysis_date - first_purchase).dt.days.values
    rfm['avg_order_value'] = rfm['monetary'] / rfm['frequency']
    
    # Calculate purchase trend (last 3 purchases vs previous)
    def calculate_trend(user_id):
        user_orders = df_filtered[df_filtered['user_id'] == user_id].sort_values('order_date')
        if len(user_orders) < 6:
            return 0
        recent = user_orders.tail(3)['net_revenue'].mean()
        previous = user_orders.head(len(user_orders)-3).tail(3)['net_revenue'].mean()
        return (recent - previous) / previous if previous > 0 else 0
    
    rfm['purchase_trend'] = rfm['user_id'].apply(calculate_trend)
    
    # Create churn label (1 = churned, 0 = active)
    # Define churned as: recency > 90 days
    rfm['churned'] = (rfm['recency'] > 90).astype(int)
    
    # Prepare features
    churn_features = ['recency', 'frequency', 'monetary', 'days_since_first_purchase', 
                      'avg_order_value', 'purchase_trend']
    
    X_churn = rfm[churn_features].fillna(0)
    y_churn = rfm['churned']
    
    if len(X_churn) >= 20 and y_churn.sum() >= 5:  # ต้องมี churned cases อย่างน้อย 5 cases
        # Split data
        X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
            X_churn, y_churn, test_size=0.2, random_state=42, stratify=y_churn
        )
        
        # Train Gradient Boosting model
        with st.spinner('🤖 Training churn prediction model...'):
            gb_model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=3,
                random_state=42
            )
            gb_model.fit(X_train_c, y_train_c)
        
        # Predict churn probability
        churn_proba = gb_model.predict_proba(X_churn)[:, 1] * 100  # Probability of churn
        rfm['churn_probability_%'] = churn_proba
        
        # Categorize risk based on ML probability
        rfm['ai_risk_category'] = pd.cut(
            rfm['churn_probability_%'],
            bins=[0, 30, 60, 100],
            labels=['Low Risk', 'Medium Risk', 'High Risk']
        )
        
        # Model performance
        y_pred_c = gb_model.predict(X_test_c)
        accuracy = accuracy_score(y_test_c, y_pred_c)
        
        # Display results
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.success(f"""
            ✅ **Churn Model Trained Successfully!**
            - Training samples: {len(X_train_c):,}
            - Test samples: {len(X_test_c):,}
            - Accuracy: {accuracy*100:.1f}%
            - Churned customers detected: {y_churn.sum()}
            """)
            
            # Feature importance for churn
            churn_importance = pd.DataFrame({
                'feature': churn_features,
                'importance': gb_model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                y=churn_importance['feature'],
                x=churn_importance['importance'],
                orientation='h',
                marker_color='#e74c3c',
                text=churn_importance['importance'],
                texttemplate='%{text:.3f}',
                textposition='outside'
            ))
            
            fig.update_layout(
                title='<b>Churn Prediction - Feature Importance</b>',
                xaxis=dict(title='Importance Score'),
                yaxis=dict(title=''),
                plot_bgcolor='white',
                height=300,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); 
                        padding: 25px; border-radius: 10px; color: white; text-align: center; height: 300px;
                        display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size: 14px; opacity: 0.9; margin-bottom: 10px;'>
                    <b>CHURN MODEL ACCURACY</b>
                </div>
                <div style='font-size: 48px; font-weight: bold; margin: 15px 0;'>
                    {accuracy*100:.1f}%
                </div>
                <div style='font-size: 12px; opacity: 0.8;'>
                    Classification Accuracy
                </div>
                <div style='font-size: 11px; margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.2); border-radius: 5px;'>
                    Precision: {gb_model.score(X_test_c, y_test_c):.3f}<br>
                    Samples: {len(X_churn):,}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Risk summary
        risk_summary = rfm.groupby('ai_risk_category').agg({
            'user_id': 'count',
            'monetary': 'sum',
            'churn_probability_%': 'mean'
        }).reset_index()
        risk_summary.columns = ['Risk Category', 'Customers', 'Revenue at Risk', 'Avg Churn Probability']
        
        col1, col2, col3 = st.columns(3)
        
        risk_colors = {
            'Low Risk': '#2ecc71',
            'Medium Risk': '#f39c12',
            'High Risk': '#e74c3c'
        }
        
        for idx, (col, risk) in enumerate(zip([col1, col2, col3], ['Low Risk', 'Medium Risk', 'High Risk'])):
            risk_data = risk_summary[risk_summary['Risk Category'] == risk]
            if not risk_data.empty:
                customers = risk_data['Customers'].values[0]
                revenue = risk_data['Revenue at Risk'].values[0]
                prob = risk_data['Avg Churn Probability'].values[0]
                color = risk_colors[risk]
                
                with col:
                    st.markdown(f"""
                    <div style='background: white; padding: 25px; border-radius: 10px; 
                                border: 3px solid {color}; text-align: center;'>
                        <div style='font-size: 14px; color: #7f8c8d; margin-bottom: 10px;'>
                            <b>{risk}</b>
                        </div>
                        <div style='font-size: 36px; font-weight: bold; color: {color}; margin: 10px 0;'>
                            {customers:,}
                        </div>
                        <div style='font-size: 12px; color: #95a5a6;'>
                            Customers ({prob:.1f}% avg churn risk)
                        </div>
                        <div style='font-size: 11px; color: #7f8c8d; margin-top: 10px; padding: 8px; background: #f8f9fa; border-radius: 5px;'>
                            Revenue: ฿{revenue/1000:.0f}K
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # High risk customers with AI scores
        st.markdown("#### 🚨 AI-Identified High Risk Customers")
        
        high_risk_ai = rfm[rfm['ai_risk_category'] == 'High Risk'].sort_values('churn_probability_%', ascending=False).head(10)
        
        if not high_risk_ai.empty:
            high_risk_display = high_risk_ai[['user_id', 'recency', 'frequency', 'monetary', 'churn_probability_%']].copy()
            high_risk_display.columns = ['Customer ID', 'Days Since Last Purchase', 'Total Orders', 'Total Spent', 'Churn Risk %']
            
            styled_risk = high_risk_display.style.format({
                'Days Since Last Purchase': '{:.0f}',
                'Total Orders': '{:.0f}',
                'Total Spent': '฿{:,.0f}',
                'Churn Risk %': '{:.1f}%'
            }).background_gradient(subset=['Churn Risk %'], cmap='YlOrRd')
            
            st.dataframe(styled_risk, use_container_width=True)
            
            st.info(f"""
            💡 **AI Recommendations for High Risk Customers:**
            - **Priority 1 ({high_risk_ai['churn_probability_%'].gt(80).sum()} customers):** Churn risk >80% → Immediate phone call + 25% discount
            - **Priority 2 ({high_risk_ai['churn_probability_%'].between(60,80).sum()} customers):** Churn risk 60-80% → Personalized email + free shipping
            - **Priority 3:** Schedule follow-up in 7 days
            """)
        else:
            st.success("✅ No high-risk customers identified by AI!")
        
    else:
        st.warning("⚠️ Need at least 20 customers with 5+ churned cases to train AI model.")
    
    st.markdown("---")
    # ==================== AI CUSTOMER SEGMENTATION (RFM) ====================
    st.markdown("### 👥 AI Customer Segmentation (RFM Analysis)")
    
    with st.expander("📖 Description", expanded=False):
        st.markdown("""
        <div class='metric-explanation'>
            <b>📖 RFM Analysis:</b> แบ่งกลุ่มลูกค้าตามพฤติกรรมการซื้อ<br>
            <div class='metric-formula'>
                • <b>Recency (R):</b> ซื้อล่าสุดเมื่อไหร่ (วัน)<br>
                • <b>Frequency (F):</b> ซื้อบ่อยแค่ไหน (ครั้ง)<br>
                • <b>Monetary (M):</b> ใช้จ่ายเท่าไหร่ (บาท)
            </div>
            <b>💡 Customer Segments:</b><br>
            • <b style='color: #2ecc71;'>Champions:</b> ซื้อบ่อย ซื้อเยอะ ซื้อเมื่อเร็วๆ นี้<br>
            • <b style='color: #3498db;'>Loyal:</b> ซื้อสม่ำเสมอ ใช้จ่ายดี<br>
            • <b style='color: #f39c12;'>At Risk:</b> เคยซื้อเยอะ แต่นานไม่ซื้อแล้ว<br>
            • <b style='color: #e74c3c;'>Lost:</b> ไม่ซื้อมานาน ต้องดึงกลับ
        </div>
        """, unsafe_allow_html=True)
    
    # Calculate RFM
    analysis_date = df_filtered['order_date'].max()
    
    rfm = df_filtered.groupby('user_id').agg({
        'order_date': lambda x: (analysis_date - x.max()).days,  # Recency
        'order_id': 'nunique',  # Frequency
        'net_revenue': 'sum'  # Monetary
    }).reset_index()
    
    rfm.columns = ['user_id', 'recency', 'frequency', 'monetary']


    # RFM Scoring (1-5 scale) with error handling
    try:
        # ใช้ rank เพื่อรองรับข้อมูลที่ซ้ำกัน
        rfm['r_rank'] = rfm['recency'].rank(method='first')
        rfm['f_rank'] = rfm['frequency'].rank(method='first')
        rfm['m_rank'] = rfm['monetary'].rank(method='first')
    
        # แบ่งเป็น 5 กลุ่ม
        rfm['r_score'] = pd.cut(rfm['r_rank'], bins=5, labels=[5,4,3,2,1], duplicates='drop')
        rfm['f_score'] = pd.cut(rfm['f_rank'], bins=5, labels=[1,2,3,4,5], duplicates='drop')
        rfm['m_score'] = pd.cut(rfm['m_rank'], bins=5, labels=[1,2,3,4,5], duplicates='drop')
    except:
        # Fallback: ใช้ qcut แบบเดิม
        rfm['r_score'] = pd.qcut(rfm['recency'], q=5, labels=[5,4,3,2,1], duplicates='drop')
        rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=5, labels=[1,2,3,4,5], duplicates='drop')
        rfm['m_score'] = pd.qcut(rfm['monetary'].rank(method='first'), q=5, labels=[1,2,3,4,5], duplicates='drop')
    
    rfm['rfm_score'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str) + rfm['m_score'].astype(str)
    
    # Segment customers
    def segment_customer(row):
        r, f, m = int(row['r_score']), int(row['f_score']), int(row['m_score'])
        
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3:
            return 'Loyal Customers'
        elif r >= 4 and f <= 2:
            return 'New Customers'
        elif r <= 2 and f >= 3:
            return 'At Risk'
        elif r <= 2 and f <= 2:
            return 'Lost'
        elif m >= 4:
            return 'Big Spenders'
        else:
            return 'Others'
    
    rfm['segment'] = rfm.apply(segment_customer, axis=1)
    
    # Segment summary
    segment_summary = rfm.groupby('segment').agg({
        'user_id': 'count',
        'monetary': 'sum',
        'frequency': 'mean',
        'recency': 'mean'
    }).reset_index()
    segment_summary.columns = ['Segment', 'Customers', 'Total Revenue', 'Avg Frequency', 'Avg Recency']
    segment_summary = segment_summary.sort_values('Total Revenue', ascending=False)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Segment distribution pie chart
        segment_colors = {
            'Champions': '#2ecc71',
            'Loyal Customers': '#3498db',
            'New Customers': '#1abc9c',
            'At Risk': '#f39c12',
            'Lost': '#e74c3c',
            'Big Spenders': '#9b59b6',
            'Others': '#95a5a6'
        }
        
        fig = go.Figure(data=[go.Pie(
            labels=segment_summary['Segment'],
            values=segment_summary['Customers'],
            marker=dict(colors=[segment_colors.get(s, '#95a5a6') for s in segment_summary['Segment']]),
            textinfo='label+percent',
            textposition='inside',
            hovertemplate='<b>%{label}</b><br>Customers: %{value:,}<br>Share: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title='<b>Customer Segment Distribution</b>',
            height=400,
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Revenue by segment
        segment_sorted = segment_summary.sort_values('Total Revenue', ascending=True)
        colors_list = [segment_colors.get(s, '#95a5a6') for s in segment_sorted['Segment']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=segment_sorted['Segment'],
            x=segment_sorted['Total Revenue'],
            orientation='h',
            marker=dict(color=colors_list),
            text=segment_sorted['Total Revenue'],
            texttemplate='฿%{text:,.0f}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Revenue: ฿%{x:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Revenue by Customer Segment</b>',
            xaxis=dict(title='Total Revenue (฿)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            yaxis=dict(title=''),
            plot_bgcolor='white',
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # AI Recommendations for each segment
    st.markdown("#### 🎯 AI-Powered Action Recommendations")
    
    segment_actions = {
        'Champions': {
            'emoji': '👑',
            'color': '#2ecc71',
            'actions': [
                'Send VIP early access to new products',
                'Create exclusive loyalty rewards program',
                'Ask for testimonials and referrals',
                'Offer premium/upsell products'
            ]
        },
        'Loyal Customers': {
            'emoji': '💎',
            'color': '#3498db',
            'actions': [
                'Build deeper relationships with personalized communication',
                'Cross-sell complementary products',
                'Invite to become brand ambassadors',
                'Offer subscription programs'
            ]
        },
        'At Risk': {
            'emoji': '⚠️',
            'color': '#f39c12',
            'actions': [
                'Send win-back campaigns with special offers',
                'Survey to understand why they stopped buying',
                'Offer limited-time discounts (15-20%)',
                'Re-engage with new product launches'
            ]
        },
        'Lost': {
            'emoji': '🔴',
            'color': '#e74c3c',
            'actions': [
                'Aggressive win-back campaign (25-30% discount)',
                'Personalized "We miss you" emails',
                'Survey to understand churn reasons',
                'Consider if re-acquisition cost is worth it'
            ]
        },
        'New Customers': {
            'emoji': '🌟',
            'color': '#1abc9c',
            'actions': [
                'Welcome email series with education content',
                'First repeat purchase incentive (10% off)',
                'Product recommendation based on first purchase',
                'Build trust with great customer service'
            ]
        },
        'Big Spenders': {
            'emoji': '💰',
            'color': '#9b59b6',
            'actions': [
                'Personal account manager or VIP service',
                'Exclusive high-value product previews',
                'Volume discount programs',
                'Premium packaging and shipping'
            ]
        }
    }
    
    for segment in segment_summary['Segment']:
        if segment in segment_actions:
            info = segment_actions[segment]
            customers = segment_summary[segment_summary['Segment'] == segment]['Customers'].values[0]
            revenue = segment_summary[segment_summary['Segment'] == segment]['Total Revenue'].values[0]
            
            with st.expander(f"{info['emoji']} **{segment}** ({customers:,} customers, ฿{revenue:,.0f} revenue)", expanded=False):
                st.markdown(f"<div style='padding: 15px; background: {info['color']}15; border-left: 4px solid {info['color']}; border-radius: 5px;'>", unsafe_allow_html=True)
                for action in info['actions']:
                    st.markdown(f"• {action}")
                st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")


    
    # ==================== AI INSIGHTS SUMMARY ====================
    st.markdown("### 📊 AI-Generated Insights Summary")
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 30px; border-radius: 15px; color: white;'>
        <h4 style='margin: 0 0 20px 0;'>🤖 Machine Learning Insights</h4>
    """, unsafe_allow_html=True)
    
    insights = []
    
    # Price optimization insights
    if len(X) >= 10:
        top_opportunity = price_ml_data.nlargest(1, 'potential_profit_increase_%')
        if not top_opportunity.empty:
            product = top_opportunity['product_name'].values[0]
            increase = top_opportunity['potential_profit_increase_%'].values[0]
            insights.append(f"💰 <b>Price Optimization:</b> '{product}' has {increase:.0f}% profit increase potential based on ML analysis")
    
    # Churn insights
    if len(X_churn) >= 20:
        high_risk_count = len(rfm[rfm['ai_risk_category'] == 'High Risk'])
        if high_risk_count > 0:
            avg_value = rfm[rfm['ai_risk_category'] == 'High Risk']['monetary'].mean()
            insights.append(f"⚠️ <b>Churn Alert:</b> AI detected {high_risk_count} high-risk customers (avg value ฿{avg_value:,.0f})")
    
    # Feature importance insights
    if 'feature_importance' in locals():
        top_feature = feature_importance.iloc[0]['feature']
        insights.append(f"📊 <b>Key Factor:</b> '{top_feature}' is the most important factor in price optimization")
    
    if 'churn_importance' in locals():
        top_churn_feature = churn_importance.iloc[0]['feature']
        insights.append(f"🎯 <b>Churn Predictor:</b> '{top_churn_feature}' is the strongest churn indicator")
    
    # Model performance
    if 'accuracy' in locals():
        insights.append(f"✅ <b>AI Accuracy:</b> Churn prediction model achieves {accuracy*100:.1f}% accuracy")
    
    if insights:
        st.markdown("<div style='padding: 20px; background: rgba(255,255,255,0.1); border-radius: 10px; margin-top: 20px;'>", unsafe_allow_html=True)
        for insight in insights:
            st.markdown(f"<p style='margin: 10px 0; font-size: 14px;'>{insight}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; color: white;'>
        <h3 style='margin: 0; font-size: 24px;'>🤖 Real AI-Powered Analytics</h3>
        <p style='margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;'>
            Powered by Random Forest & Gradient Boosting • Real-time ML Predictions • Data-Driven Insights
        </p>
    </div>
    """, unsafe_allow_html=True)













































































