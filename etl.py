# etl.py
import os
import pandas as pd

# load_data: อ่านจาก folder "data" และแมปเป็นคีย์สั้นที่ app.py/merge_data คาดหวัง
def load_data(data_path="data"):
    required_files = {
        "distribution_centers.csv": "dc",
        "user.csv": "user",
        "product.csv": "product",
        "inventory_item.csv": "inventory_item",
        "order.csv": "order",
        "order_item.csv": "order_item",
        "event.csv": "event",
    }

    dfs = {}
    missing = []
    for fname, key in required_files.items():
        fp = os.path.join(data_path, fname)
        if not os.path.exists(fp):
            missing.append(fp)
        else:
            dfs[key] = pd.read_csv(fp)

    if missing:
        raise FileNotFoundError(f"Missing files in '{data_path}':\n" + "\n".join(missing))

    return dfs

# merge_data: รวมตารางอย่างยืดหยุ่น โดยไม่โยน KeyError แบบเดิม — ให้ข้อความชัดเจนแทน
def merge_data(d):
    """
    d: dict ที่มี keys เช่น 'order_item','order','product','user','dc','inventory_item','event'
    จะคืน DataFrame แบบ flattened สำหรับการวิเคราะห์ (order_item join order -> product -> user)
    """
    # required minimal keys
    required_min = ["order_item", "order", "product"]
    for k in required_min:
        if k not in d:
            raise KeyError(f"Missing dataset key required for merge: {k}. Available keys: {list(d.keys())}")

    oi = d["order_item"].copy()
    order = d["order"].copy()
    product = d["product"].copy()

    # normalize column names to avoid case/space issues
    def norm_cols(df):
        df = df.copy()
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        return df

    oi = norm_cols(oi)
    order = norm_cols(order)
    product = norm_cols(product)

    # common join column names expected: order_id, product_id, user_id
    # try to detect if order uses 'name' as id (fallback)
    if 'order_id' not in oi.columns and 'orderid' in oi.columns:
        oi = oi.rename(columns={'orderid':'order_id'})
    if 'order_id' not in order.columns and 'id' in order.columns:
        order = order.rename(columns={'id':'order_id'})

    if 'product_id' not in oi.columns and 'product' in oi.columns:
        oi = oi.rename(columns={'product':'product_id'})
    if 'product_id' not in product.columns and 'product_id' not in product.columns and 'productid' in product.columns:
        product = product.rename(columns={'productid':'product_id'})
    if 'user_id' not in oi.columns and 'user' in oi.columns:
        oi = oi.rename(columns={'user':'user_id'})

    # perform joins
    df = oi.merge(order, on='order_id', how='left', suffixes=('_item','_order'))
    df = df.merge(product, on='product_id', how='left', suffixes=('','_prod'))

    # optionally merge user if provided
    if 'user' in d:
        user = norm_cols(d['user'])
        # try to harmonize
        if 'user_id' not in user.columns and 'id' in user.columns:
            user = user.rename(columns={'id':'user_id'})
        if 'user_id' in df.columns and 'user_id' in user.columns:
            df = df.merge(user, on='user_id', how='left', suffixes=('','_user'))

    # optionally merge distribution centers (dc)
    if 'dc' in d:
        dc = norm_cols(d['dc'])
        # if product has distribution center id column, try common names
        possible_fk = None
        for col in ['distribution_centers_id','distribution_center_id','dc_id','distribution_centersid','dcid']:
            if col in df.columns:
                possible_fk = col
                break
        # find dc id column in dc
        dc_id_col = None
        for col in ['distribution_centers_id','distribution_center_id','dc_id','id','distributioncentersid']:
            if col in dc.columns:
                dc_id_col = col
                break
        if possible_fk and dc_id_col:
            df = df.merge(dc, left_on=possible_fk, right_on=dc_id_col, how='left', suffixes=('','_dc'))

    # return merged dataframe
    return df
