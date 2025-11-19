import os
import pandas as pd

def load_data(data_path="data"):
    files = os.listdir(data_path)
    dfs = {}

    # Map file → key
    mapping = {
        "distribution_centers.csv": "dc",
        "order_items.csv": "order_items",
        "orders.csv": "orders",
        "products.csv": "products",
        "drivers.csv": "drivers"
    }

    for fname, key in mapping.items():
        full_path = os.path.join(data_path, fname)
        if os.path.exists(full_path):
            dfs[key] = pd.read_csv(full_path)
        else:
            raise FileNotFoundError(f"Missing file: {fname}")

    return dfs


def merge_data(d):

    # check required keys exist
    required_keys = ["order_items", "orders", "products", "dc", "drivers"]
    for k in required_keys:
        if k not in d:
            raise KeyError(f"Missing dataset key: {k}")

    df = (
        d["order_items"]
        .merge(d["orders"], on="order_id", how="left")
        .merge(d["products"], on="product_id", how="left")
        .merge(d["dc"], on="dc_id", how="left")
        .merge(d["drivers"], on="driver_id", how="left")
    )

    return df

