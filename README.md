# 🛩️ AI Maintenance Task Optimizer

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

Tối ưu hóa kế hoạch bảo dưỡng máy bay bằng AI - Adaptive Peak-Based Clustering

## 🎯 Tính năng

- ✅ Upload file Excel/CSV chứa task bảo dưỡng
- ✅ Tự động phân nhóm tasks bằng thuật toán APBC
- ✅ Kiểm tra tuân thủ ±20% compliance
- ✅ Phát hiện nested groups (bội số 2 ±10%)
- ✅ Visualization tương tác với Plotly
- ✅ Export kết quả Excel 4 sheets
- ✅ Hỗ trợ ATA chapter analysis

## 🚀 Quick Start

### Online (Streamlit Cloud)
Truy cập: [https://your-app-url.streamlit.app](https://your-app-url.streamlit.app)

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/ai-maintenance-optimizer.git
cd ai-maintenance-optimizer

# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py
```

## 📊 Thuật toán APBC

**Adaptive Peak-Based Clustering** - 4 bước:

1. **Dynamic Threshold**: Tự động chọn peaks phủ ~80% tasks
2. **Adaptive Merge**: Merge peaks với tolerance tăng dần
3. **Task Assignment**: Gán tasks với ±20% compliance
4. **Nested Detection**: Phát hiện bội số 2 ±10%

**Kết quả với A350**: 19 groups, 97.8% tuân thủ, giảm 63.2% công việc

## 📁 Cấu trúc dự án

```
ai-maintenance-optimizer/
├── app.py                 # Streamlit app chính
├── utils/
│   ├── __init__.py
│   ├── data_processor.py  # Xử lý dữ liệu
│   ├── apbc_optimizer.py  # Thuật toán APBC
│   └── visualizer.py      # Tạo charts
├── requirements.txt       # Dependencies
├── .streamlit/
│   └── config.toml       # Cấu hình Streamlit
└── README.md
```

## 🛠️ Tech Stack

- **Python 3.9+**
- **Streamlit** - Web framework
- **Pandas** - Data processing
- **Plotly** - Interactive charts
- **OpenPyXL** - Excel export

## 📝 License

MIT License - Free to use and modify

## 👥 Contributors

AI Maintenance Optimization Team - 2025
