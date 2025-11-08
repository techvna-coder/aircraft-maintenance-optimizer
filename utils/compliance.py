import numpy as np
import pandas as pd

def compliance_check(df: pd.DataFrame, tol: float = 0.20) -> pd.DataFrame:
    """Thêm Deviation_Ratio, Compliance_Status, Late_Risk theo ± tol so với chính interval của task."""
    df = df.copy()
    def _row(r):
        interval = r["Interval_EFH"]
        center = r["Group_Center_EFH"]
        if pd.isna(interval) or pd.isna(center) or interval <= 0:
            return np.nan, "Out-of-Phase", True
        dev = (center - interval) / interval
        status = "In-Group" if abs(dev) <= tol else "Out-of-Phase"
        late = (center > interval)
        return dev, status, late
    out = df.apply(lambda r: _row(r), axis=1, result_type="expand")
    df["Deviation_Ratio"] = out[0]
    df["Compliance_Status"] = out[1]
    df["Late_Risk"] = out[2]
    return df
