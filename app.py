import io
import sys
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from utils.data_preprocess import (
    normalize_columns,
    to_float_safe,
    extract_ata,
    cal_to_fh,
    compute_interval_efh,
    apply_mappings_ui
)
from utils.clustering import choose_k_elbow, kmeans_cluster_1d
from utils.compliance import compliance_check
from utils.nested import detect_nested_groups
from utils.export_utils import build_excel_report

st.set_page_config(page_title="AI Maintenance Task Optimizer", layout="wide")

# ---------------- Sidebar – Parameters ----------------
st.sidebar.title("Thiết lập")
st.sidebar.caption("Chuẩn hoá EFH & ràng buộc kỹ thuật")

# Quy đổi mặc định (đã thống nhất)
fc_to_fh_default = 4.83
mo_to_fh_default = 435.0

fc_to_fh = st.sidebar.number_input("Quy đổi 1 FC → FH", value=fc_to_fh_default, step=0.01, min_value=0.1)
mo_to_fh = st.sidebar.number_input("Quy đổi 1 Month → FH", value=mo_to_fh_default, step=1.0, min_value=10.0)

# Tolerance cố định theo yêu cầu (20%)
tol = 0.20
st.sidebar.write(f"Tolerance (±) cố định: **{int(tol*100)}%**")

# Nested detection ±10% quanh bội 2
nested_eps = st.sidebar.slider("Nested: biên ± quanh bội 2", min_value=0.05, max_value=0.2, value=0.10, step=0.01)
st.sidebar.caption("Nếu tỷ lệ giữa 2 tâm liên tiếp nằm trong [2×(1-ε); 2×(1+ε)] → nhóm nhỏ nested vào nhóm lớn.")

st.title("✈️ AI Maintenance Task Optimizer")
st.markdown("**Mục tiêu:** Gom nhóm theo chu kỳ tự nhiên (EFH), bảo đảm **tuân thủ ±20%**, và tính **nested 2× ±10%** để giảm số lần vào check.")

# ---------------- File Upload ----------------
uploaded = st.file_uploader("📂 Tải file Task List (CSV/XLSX)", type=["csv", "xlsx"])
if not uploaded:
    st.info("Tải lên file để bắt đầu. Có thể tham khảo `sample_data/a350_task_list_example.csv` trong repo.")
    st.stop()

# ---------------- Read Data ----------------
try:
    if uploaded.name.lower().endswith(".csv"):
        raw_df = pd.read_csv(uploaded)
    else:
        raw_df = pd.read_excel(uploaded)
except Exception as e:
    st.error(f"Không đọc được file: {e}")
    st.stop()

st.subheader("1) Dữ liệu gốc (preview)")
st.dataframe(raw_df.head(20), use_container_width=True)

# ---------------- Column Mapping UI ----------------
st.subheader("2) Ánh xạ cột bắt buộc")
df = raw_df.copy()
df.columns = [str(c).strip() for c in df.columns]
df_norm = normalize_columns(df)

mapping = apply_mappings_ui(df_norm.columns)
# Map cột theo lựa chọn
df_work = df_norm.rename(columns={
    mapping["TASK"]: "TASK",
    mapping["TITLE"]: "TITLE",
    mapping["FH"]: "FH",
    mapping["CY"]: "CY",
    mapping["CAL"]: "CAL",
    mapping["CODE"]: "CODE",
    mapping["INT_THRES"]: "INT_THRES"
})

# Chuẩn hoá giá trị số và ATA
for c in ["FH", "CY", "CAL"]:
    df_work[c] = df_work[c].apply(to_float_safe)
df_work["ATA"] = df_work["TASK"].apply(extract_ata)

# ---------------- EFH Conversion ----------------
st.subheader("3) Quy đổi sang EFH")
df_work["EFH_FH"] = df_work["FH"]
df_work["EFH_FC"] = df_work["CY"] * fc_to_fh
df_work["EFH_CAL"] = df_work.apply(lambda r: cal_to_fh(r["CAL"], r["CODE"], mo_to_fh), axis=1)
df_work["Interval_EFH"] = df_work.apply(
    lambda r: compute_interval_efh(r["EFH_FH"], r["EFH_FC"], r["EFH_CAL"]),
    axis=1
)
st.dataframe(df_work[["TASK","TITLE","ATA","FH","CY","CAL","CODE","EFH_FH","EFH_FC","EFH_CAL","Interval_EFH"]].head(20), use_container_width=True)

work = df_work[df_work["Interval_EFH"].notna() & (df_work["Interval_EFH"] > 0)].copy()
if work.empty:
    st.warning("Không có dòng nào có `Interval_EFH` hợp lệ.")
    st.stop()

# ---------------- KMeans Clustering ----------------
st.subheader("4) AI clustering theo EFH")
X = work[["Interval_EFH"]].values
best_model, k = choose_k_elbow(X, k_min=2, k_max=min(8, len(work)))
labels, centers = kmeans_cluster_1d(X, best_model)

work["Cluster"] = labels
# Sắp xếp tâm tăng dần và gán Group_ID
order = np.argsort(centers)
sorted_centers = [centers[i] for i in order]
label_map = {int(order[i]): i+1 for i in range(len(order))}
work["Group_ID"] = work["Cluster"].map(label_map)
group_center_map = {i+1: sorted_centers[i] for i in range(len(sorted_centers))}
work["Group_Center_EFH"] = work["Group_ID"].map(group_center_map)

# Biểu đồ phân bố EFH và tâm cụm
fig, ax = plt.subplots(figsize=(7,4))
ax.hist(work["Interval_EFH"], bins=30)
for c in sorted_centers:
    ax.axvline(c, linestyle="--")
ax.set_xlabel("Interval (EFH)")
ax.set_ylabel("Count")
ax.set_title("Phân bố Interval_EFH & tâm cụm")
st.pyplot(fig, use_container_width=True)

# ---------------- Compliance ±20% ----------------
st.subheader("5) Kiểm tra tuân thủ hạn (±20%) & đánh dấu Out-of-Phase")
work = compliance_check(work, tol=tol)  # thêm Deviation_Ratio, Compliance_Status, Late_Risk

in_group = work[work["Compliance_Status"] == "In-Group"].copy()
ooph = work[work["Compliance_Status"] == "Out-of-Phase"].copy()

col_out = ["TASK","TITLE","ATA","FH","CY","CAL","CODE","Interval_EFH","Group_ID","Group_Center_EFH","Deviation_Ratio","Compliance_Status","Late_Risk"]
st.markdown("**In-Group (tuân ±20%) – preview**")
st.dataframe(in_group[col_out].head(100), use_container_width=True)
st.markdown("**Out-of-Phase (> ±20%) – preview**")
st.dataframe(ooph[col_out].head(100), use_container_width=True)

# ---------------- Nested detection ----------------
st.subheader("6) Nested (bội 2 ±10%) và hiệu quả giảm số nhóm thực hiện")
cent_df, effective_groups, effective_reduction = detect_nested_groups(sorted_centers, eps=nested_eps)

st.markdown("**Tổng quan Nested Summary**")
st.dataframe(cent_df, use_container_width=True)
st.write(f"**Số nhóm thực cần làm**: {len(effective_groups)} / {len(sorted_centers)}  →  **Effective reduction:** {effective_reduction:.1%}")

# ---------------- Group Summary ----------------
st.subheader("7) Group Summary (chỉ tính In-Group)")
summary = (in_group
           .groupby("Group_ID", as_index=False)
           .agg(
               Tasks=("TASK","count"),
               Mean_EFH=("Interval_EFH","mean"),
               Median_EFH=("Interval_EFH","median"),
               Min_EFH=("Interval_EFH","min"),
               Max_EFH=("Interval_EFH","max"),
               Center_EFH=("Group_Center_EFH","first")
           ))
summary["Suggested_Label"] = summary.apply(
    lambda r: f"Group-{int(r['Group_ID'])} (~{int(round(r['Center_EFH']))} EFH)",
    axis=1
)
st.dataframe(summary, use_container_width=True)

# ---------------- Download Excel ----------------
st.subheader("8) Xuất báo cáo Excel")
buf = io.BytesIO()
assumptions = {
    "Chosen_k (elbow)": k,
    "FC_TO_FH": fc_to_fh,
    "MO_TO_FH": mo_to_fh,
    "Tolerance_±": tol,
    "Nested_Target_Ratio": 2.0,
    "Nested_EPS_±": nested_eps,
    "Effective_Groups": len(effective_groups),
    "Total_Groups": len(sorted_centers),
    "Effective_Reduction": effective_reduction
}
build_excel_report(
    buffer=buf,
    in_group_df=in_group[col_out],
    ooph_df=ooph[col_out],
    nested_df=cent_df,
    summary_df=summary,
    assumptions=assumptions
)
st.download_button(
    "⬇️ Tải Excel kết quả",
    data=buf.getvalue(),
    file_name="AI_Compliance_Nested_Output.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.success("Hoàn tất. Anh có thể dùng file Excel này để trình bày và/hoặc nhập lại vào hệ thống lập kế hoạch.")
