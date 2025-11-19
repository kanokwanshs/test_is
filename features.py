import pandas as pd
import numpy as np

def build_features(df):

    df_feat = df.copy()

    # Basic derived features
    df_feat["total_revenue"] = df_feat["sale_price"]
    df_feat["margin"] = df_feat["sale_price"] - df_feat["cost"]

    # Customer RFM
    df_feat["order_date"] = pd.to_datetime(df_feat["created_at"])
    rfm = df_feat.groupby("user_id").agg(
        recency=("order_date", lambda x: (df_feat["order_date"].max() - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("sale_price", "sum")
    ).reset_index()

    # Product demand per month
    df_feat["month"] = df_feat["order_date"].dt.to_period("M")
    demand = df_feat.groupby(["product_id", "month"]).size().reset_index(name="demand")

    return df_feat, rfm, demand
