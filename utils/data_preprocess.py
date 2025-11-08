import re
import numpy as np
import pandas as pd
import streamlit as st

# Chuẩn hoá tên cột "thân thiện"
CANONICAL = ["TASK","TITLE","FH","CY","CAL","CODE","INT_THRES"]

# Các biến thể tên cột thường gặp → map về chuẩn
VARIANTS = {
    "TASK": ["TASK","Task","task","TÂSK"],
    "TITLE": ["TITLE","Title","title","NAME","DESC","DESCRIPTION"],
    "FH": ["FH","Flight Hours","FLIGHT_HOURS","HOURS"],
    "CY": ["CY","FC","CYCLES","Flight Cycles"],
    "CAL": ["CAL","MONTH","MO","CALENDAR"],
    "CODE": ["CODE","UNIT","CAL UNIT","CAL_CODE"],
    "INT_THRES": ["INT/THRES","INT_THRES","INT-THRES","INT\\THRES","THRESHOLD"]
}

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = list(df.columns)
    col_map = {}
    for c in cols:
        cu = str(c).strip()
        mapped = cu
        for k, arr in VARIANTS.items():
            if cu in arr:
                mapped = k
                break
        col_map[c] = mapped
    df2 = df.rename(columns=col_map)
    # Bổ sung cột thiếu
    for c in CANONICAL:
        if c not in df2.columns:
            df2[c] = np.nan
    return df2

def to_float_safe(x):
    if pd.isna(x):
        return np.nan
    if isinstance(x, (int,float,np.number)):
        return float(x)
    s = str(x).strip()
    s2 = ''.join(ch for ch in s if ch.isdigit() or ch == '.')
    try:
        return float(s2) if s2 != "" else np.nan
    except:
        return np.nan

def extract_ata(task):
    if pd.isna(task):
        return np.nan
    s = str(task)
    m = re.search(r'(\d{2}(?:-\d{2}){0,2})', s)
    if m:
        return m.group(1)
    m2 = re.search(r'(\d{2})', s)
    return m2.group(1) if m2 else np.nan

def cal_to_fh(cal, code, mo_to_fh=435.0):
    if pd.isna(cal):
        return np.nan
    u = str(code).strip().upper() if not pd.isna(code) else "M"
    if u in ("M","MO","MON","MONTH","MONTHS"):
        months = cal
    elif u in ("Y","YR","YEAR","YEARS"):
        months = cal*12.0
    elif u in ("D","DAY","DAYS"):
        months = cal/30.0
    elif u in ("W","WK","WEEK","WEEKS"):
        months = cal/4.0
    else:
        months = cal
    return months * mo_to_fh

def compute_interval_efh(efh_fh, efh_fc, efh_cal):
    vals = [v for v in [efh_fh, efh_fc, efh_cal] if pd.notna(v) and v > 0]
    return min(vals) if vals else np.nan

def apply_mappings_ui(columns):
    cols = list(columns)
    st.write("Chọn cột tương ứng (app đã cố gắng nhận diện sẵn, nhưng anh có thể chỉnh):")
    # đề xuất mặc định nếu có
    def suggest(name):
        for v in VARIANTS.get(name, []):
            if v in cols: return v
        # fallback nếu đã normalized
        return name if name in cols else cols[0]

    mapping = {
        "TASK": st.selectbox("Cột TASK", cols, index=cols.index(suggest("TASK")) if suggest("TASK") in cols else 0),
        "TITLE": st.selectbox("Cột TITLE", cols, index=cols.index(suggest("TITLE")) if suggest("TITLE") in cols else 0),
        "FH": st.selectbox("Cột FH (flight hours)", cols, index=cols.index(suggest("FH")) if suggest("FH") in cols else 0),
        "CY": st.selectbox("Cột CY/FC (cycles)", cols, index=cols.index(suggest("CY")) if suggest("CY") in cols else 0),
        "CAL": st.selectbox("Cột CAL (calendar value)", cols, index=cols.index(suggest("CAL")) if suggest("CAL") in cols else 0),
        "CODE": st.selectbox("Cột CODE (đơn vị CAL)", cols, index=cols.index(suggest("CODE")) if suggest("CODE") in cols else 0),
        "INT_THRES": st.selectbox("Cột INT/THRES (nếu có)", cols, index=cols.index(suggest("INT_THRES")) if suggest("INT_THRES") in cols else 0),
    }
    return mapping
