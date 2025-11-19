import pandas as pd

def load_data(data_path="data"):

    df_dc       = pd.read_csv(f"{data_path}/distribution_centers.csv")
    df_user     = pd.read_csv(f"{data_path}/user.csv")
    df_product  = pd.read_csv(f"{data_path}/product.csv")
    df_inventory = pd.read_csv(f"{data_path}/inventory_item.csv")
    df_order    = pd.read_csv(f"{data_path}/order.csv")
    df_order_item = pd.read_csv(f"{data_path}/order_item.csv")
    df_event    = pd.read_csv(f"{data_path}/event.csv")

    return {
        "dc": df_dc,
        "user": df_user,
        "product": df_product,
        "inventory": df_inventory,
        "order": df_order,
        "order_item": df_order_item,
        "event": df_event
    }


def merge_data(d):
    # --- Merge orders + order_items ---
    df = d["order_item"].merge(d["order"], on="order_id", how="left", suffixes=("_item", "_order"))

    # Add customer info
    df = df.merge(d["user"], on="user_id", how="left")

    # Add product info
    df = df.merge(d["product"], on="product_id", how="left")

    return df
