# Analytics Dashboard - Improved Version with KPIs
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import warnings
from datetime import datetime, timedelta

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

REQUIRED_COLUMNS = {
    "users": ["user_id", "customer_type", "created_at"],
    "products": ["product_id", "category", "sale_price", "cost"],
    "orders": ["order_id", "user_id", "order_date", "channel", "status"],
    "order_items": [
        "order_id",
        "product_id",
        "quantity",
        "net_revenue",
        "cost",
        "profit",
    ],
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

        # Initialize session state for targets if not exists
        if "targets" not in st.session_state:
            st.session_state.targets = {
                "monthly_revenue": 5000000,
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
                help="เป้าหมาย Conversion Rate จาก Visitor เป็น Customer",
            )

            st.session_state.targets["retention_rate"] = st.number_input(
                "Target Retention Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.targets["retention_rate"]),
                step=1.0,
                help="เป้าหมายการรักษาลูกค้า (ควรสูงกว่า 80%)",
            )

        with st.sidebar.expander("📦 Warehouse Targets", expanded=False):
            st.session_state.targets["inventory_turnover"] = st.number_input(
                "Target Inventory Turnover (x/year)",
                min_value=0.0,
                value=float(st.session_state.targets["inventory_turnover"]),
                step=0.5,
                help="เป้าหมายการหมุนเวียนสินค้า (ครั้งต่อปี)",
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
""",
    unsafe_allow_html=True,
)

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
            st.code(
                "order_items.csv:\n- order_id\n- product_id\n- quantity\n- net_revenue\n- cost\n- profit"
            )

    st.stop()

df_master = merge_data(data)

# ==================== MAIN FILTERS ====================
st.title("📊 Analytics Dashboard")
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
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "💼 Sales Analytics",
        "📢 Marketing Analytics",
        "💰 Financial Analytics",
        "📦 Warehouse Analytics",
        "🔮 Forecasting & Planning",
    ]
)

with tab1:
    st.markdown("# 💼 Sales Analytics")
    st.markdown("---")

    # ==================== SALES GROWTH ====================
    st.markdown("### 📈 Monthly Sales Growth")

    with st.expander("📖 ดูคำอธิบาย & สูตรการคำนวณ", expanded=False):
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

    with st.expander("📖 ดูคำอธิบาย & สูตรการคำนวณ", expanded=False):
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

    with st.expander("📖 ดูคำอธิบาย & สูตรการคำนวณ", expanded=False):
        st.markdown(
            """
        <div class='metric-explanation'>
            <b>📖 คำอธิบาย:</b> แสดงยอดขายแยกตามช่องทางการขาย เพื่อดูว่าช่องทางไหนมี Performance ดีที่สุด
        </div>
        """,
            unsafe_allow_html=True,
        )

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

    with st.expander("📖 ดูคำอธิบาย & สูตรการคำนวณ", expanded=False):
        st.markdown(
            """
        <div class='metric-explanation'>
            <b>📖 คำอธิบาย:</b> แสดงสินค้าที่ขายดีที่สุด 20 อันดับแรก วัดจากยอดขาย และอัตรากำไร
        </div>
        """,
            unsafe_allow_html=True,
        )

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

    with st.expander("📖 ดูคำอธิบาย", expanded=False):
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

    with st.expander("📖 ดูคำอธิบาย", expanded=False):
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

    with st.expander("📖 ดูคำอธิบาย & สูตรการคำนวณ", expanded=False):
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

    with st.expander("📖 ดูคำอธิบาย & สูตรการคำนวณ", expanded=False):
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

    # ==================== RETENTION & CHURN ====================
    st.markdown("### 🔄 Customer Retention & Churn Rate")

    with st.expander("📖 ดูคำอธิบาย & สูตรการคำนวณ", expanded=False):
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

    with st.expander("📖 ดูคำอธิบาย & สูตรการคำนวณ", expanded=False):
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

    # ==================== WORKING CAPITAL RATIOS ====================
    st.markdown("### 💼 Working Capital Ratios")

    with st.expander("📖 ดูคำอธิบาย & สูตรการคำนวณ", expanded=False):
        st.markdown(
            """
        <div class='metric-explanation'>
            <b>📖 AR Turnover:</b> จำนวนครั้งที่เราเก็บเงินจากลูกค้าได้ต่อปี (ยิ่งสูงยิ่งดี)<br>
            <b>📖 DSO (Days Sales Outstanding):</b> จำนวนวันเฉลี่ยที่ใช้เวลาเก็บเงินจากลูกค้า (ยิ่งต่ำยิ่งดี)<br>
            <div class='metric-formula'>
                DSO = 365 / AR Turnover
            </div>
            <b>🎯 เป้าหมาย:</b> DSO &lt; 45 วัน ถือว่าดี
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Calculate ratios
    avg_monthly_rev = monthly_fin["net_revenue"].mean()
    avg_ar = avg_monthly_rev * 0.3  # Assume 30% credit sales
    ar_turnover = (revenue * 0.3) / avg_ar if avg_ar > 0 else 0
    dso = 365 / ar_turnover if ar_turnover > 0 else 0

    avg_ap = cogs * 0.25
    ap_turnover = cogs / avg_ap if avg_ap > 0 else 0
    dpo = 365 / ap_turnover if ap_turnover > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
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
        """,
            unsafe_allow_html=True,
        )

    with col2:
        dso_color = "#2ecc71" if dso < 45 else "#e74c3c"
        st.markdown(
            f"""
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
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
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
        """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
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
        """,
            unsafe_allow_html=True,
        )

with tab4:
    st.markdown("# 📦 Warehouse Analytics")
    st.markdown("---")

    # ==================== INVENTORY TURNOVER ====================
    st.markdown("### 🔄 Inventory Turnover & Performance")

    with st.expander("📖 ดูคำอธิบาย & สูตรการคำนวณ", expanded=False):
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

    avg_inventory = df_filtered["cost"].mean() * df_filtered["product_id"].nunique()
    inventory_turnover = cogs / avg_inventory if avg_inventory > 0 else 0
    dio = 365 / inventory_turnover if inventory_turnover > 0 else 0

    units_sold = df_filtered["quantity"].sum()
    units_received = units_sold * 1.2
    sell_through = (units_sold / units_received * 100) if units_received > 0 else 0

    # Compare with target
    target_turnover = st.session_state.targets["inventory_turnover"]
    turnover_status = (
        "✅ Above Target" if inventory_turnover >= target_turnover else "⚠️ Below Target"
    )
    turnover_color = "#2ecc71" if inventory_turnover >= target_turnover else "#e74c3c"

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
            ฿{avg_inventory/1000:.0f}K
            </div>
            <div style='font-size: 11px; opacity: 0.8;'>Total stock</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    
    # END OF TAB 4

# ==================== TAB 5 START ====================
with tab5:
    st.markdown("# 🔮 Forecasting & Planning")
    st.markdown("---")

    with st.expander("📖 ดูคำอธิบาย & สูตรการคำนวณ", expanded=False):
        st.markdown(
            """
        <div class='metric-explanation'>
            <b>📖 คำอธิบาย:</b> ใช้ข้อมูลในอดีตเพื่อคาดการณ์อนาคต ช่วยในการวางแผนธุรกิจ<br>
            <b>🎯 วิธีการ:</b> ใช้ Moving Average และ Linear Regression เพื่อทำนายแนวโน้ม
        </div>
        """,
            unsafe_allow_html=True,
        )

    # ==================== REVENUE FORECAST ====================
    st.markdown("### 📈 Revenue Forecast (Next 12 Months)")

    with st.expander("📖 ดูคำอธิบาย & สูตรการคำนวณ", expanded=False):
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

    with st.expander("📖 ดูคำอธิบาย & สูตรการคำนวณ", expanded=False):
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

    with st.expander("📖 ดูคำอธิบาย & สูตรการคำนวณ", expanded=False):
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
