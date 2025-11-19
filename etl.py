import os

def load_data(data_path, uploaded=None):

    if uploaded is not None:
        return uploaded   # ใช้ไฟล์ upload แทน

    def safe_read(file):
        fp = os.path.join(data_path, file)
        if not os.path.exists(fp):
            return None
        return pd.read_csv(fp)

    return {
        "distribution_centers.csv": safe_read("distribution_centers.csv"),
        "user.csv": safe_read("user.csv"),
        "product.csv": safe_read("product.csv"),
        "inventory_item.csv": safe_read("inventory_item.csv"),
        "order.csv": safe_read("order.csv"),
        "order_item.csv": safe_read("order_item.csv"),
        "event.csv": safe_read("event.csv"),
    }



def merge_data(d):
    # --- Merge orders + order_items ---
    df = d["order_item"].merge(d["order"], on="order_id", how="left", suffixes=("_item", "_order"))

    # Add customer info
    df = df.merge(d["user"], on="user_id", how="left")

    # Add product info
    df = df.merge(d["product"], on="product_id", how="left")

    return df
