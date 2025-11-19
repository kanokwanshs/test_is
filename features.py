# features.py
import pandas as pd
import numpy as np

def build_features(df):
    df_feat = df.copy()

    # normalize column names
    df_feat.columns = df_feat.columns.str.strip().str.lower().str.replace(" ", "_")

    # Basic derived features
    if 'sale_price' in df_feat.columns:
        df_feat["total_revenue"] = df_feat["sale_price"]
        df_feat["margin"] = df_feat["sale_price"] - df_feat.get("cost", 0)
    else:
        # fallback if price column different
        price_col = None
        for c in ['price','amount','amount_total','price_unit']:
            if c in df_feat.columns:
                price_col = c
                break
        if price_col:
            df_feat["total_revenue"] = df_feat[price_col]
            df_feat["margin"] = df_feat[price_col] - df_feat.get("cost", 0)

    # order_date
    if 'created_at' in df_feat.columns:
        df_feat["order_date"] = pd.to_datetime(df_feat["created_at"], errors='coerce')
    else:
        df_feat["order_date"] = pd.to_datetime(df_feat.get("date_order", pd.NaT), errors='coerce')

    # Customer RFM
    if 'user_id' in df_feat.columns:
        rfm = df_feat.groupby("user_id").agg(
            recency = ("order_date", lambda x: (df_feat["order_date"].max() - x.max()).days if x.notna().any() else None),
            frequency = ("order_id", "nunique"),
            monetary = ("sale_price", "sum")
        ).reset_index()
    else:
        rfm = pd.DataFrame(columns=["user_id","recency","frequency","monetary"])

    # Product demand per month
    df_feat["month"] = df_feat["order_date"].dt.to_period("M")
    demand = df_feat.groupby(["product_id", "month"]).size().reset_index(name="demand")
    # convert month back to timestamp for plotting convenience
    if not demand.empty:
        demand['month'] = demand['month'].dt.to_timestamp()

    return df_feat, rfm, demand
