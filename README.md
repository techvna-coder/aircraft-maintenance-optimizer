# AI Maintenance Task Optimizer (EFH + Compliance ±20% + Nested 2× ±10%)

Web-app Streamlit giúp gom nhóm các task bảo dưỡng theo chu kỳ tự nhiên (EFH), đảm bảo **tuân thủ hạn ±20%**, phát hiện **Nested** (bội 2 ±10%) để giảm số lần vào check. Phù hợp để hài hoà định kỳ, lập kế hoạch A-check/C-check chuyên nghiệp.

## Tính năng
- Upload CSV/XLSX, map cột linh hoạt.
- Quy đổi EFH: `EFH_FH = FH`, `EFH_FC = CY × 4.83`, `EFH_CAL = CAL (theo CODE) × 435`.
- Clustering 1D bằng KMeans, chọn `k` theo elbow (inertia).
- Compliance: ±20% (so với chính interval của task) → **In-Group/Out-of-Phase**, cảnh báo **Late_Risk** khi center > interval.
- Nested: phát hiện chuỗi bội 2 (±10%) → nhóm nhỏ nested vào nhóm lớn → tính **Effective_Check_Reduction**.
- Export Excel: In-Group, Out-of-Phase, Nested Summary, Group Summary, Assumptions.

## Cài đặt & Chạy
```bash
pip install -r requirements.txt
streamlit run app.py
