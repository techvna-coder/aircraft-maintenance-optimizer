# 🚀 Deployment Guide - AI Maintenance Task Optimizer

Hướng dẫn deploy ứng dụng lên Streamlit Cloud

---

## 📋 Checklist Trước Khi Deploy

- [ ] Code đã hoàn chỉnh và test local
- [ ] File `requirements.txt` có đầy đủ dependencies
- [ ] File `.gitignore` đã được cấu hình
- [ ] Sample data đã được include (nếu cần)
- [ ] README.md đã được cập nhật

---

## 🔧 Chuẩn Bị

### 1. Tạo GitHub Repository

```bash
# Initialize git (nếu chưa có)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: AI Maintenance Task Optimizer"

# Create repository trên GitHub: 
# https://github.com/new

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/ai-maintenance-optimizer.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 2. Kiểm Tra Cấu Trúc

Đảm bảo cấu trúc như sau:

```
ai-maintenance-optimizer/
├── app.py                    # ✅ Main app
├── requirements.txt          # ✅ Dependencies
├── README.md                 # ✅ Documentation
├── LICENSE                   # ✅ MIT License
├── .gitignore               # ✅ Git ignore
├── .streamlit/
│   └── config.toml          # ✅ Streamlit config
├── utils/
│   ├── __init__.py          # ✅
│   ├── data_processor.py    # ✅
│   ├── apbc_optimizer.py    # ✅
│   └── visualizer.py        # ✅
└── sample_data.xlsx         # ✅ Example data
```

---

## 🌐 Deploy Lên Streamlit Cloud

### Step 1: Truy Cập Streamlit Cloud

1. Đi tới: https://share.streamlit.io/
2. Đăng nhập bằng GitHub account

### Step 2: Deploy New App

1. Click **"New app"**
2. Chọn repository: `YOUR_USERNAME/ai-maintenance-optimizer`
3. Branch: `main`
4. Main file path: `app.py`
5. App URL (optional): Customize your URL
   - Example: `ai-maintenance-optimizer`
   - Full URL: `https://YOUR_USERNAME-ai-maintenance-optimizer.streamlit.app`

### Step 3: Advanced Settings (Optional)

Click "Advanced settings" nếu cần:

- **Python version**: 3.9 hoặc 3.10
- **Secrets**: Không cần (trừ khi có API keys)

### Step 4: Deploy!

Click **"Deploy!"** và đợi vài phút.

Streamlit Cloud sẽ:
1. Clone repository
2. Install dependencies từ `requirements.txt`
3. Run `app.py`
4. Provide public URL

---

## ✅ Verify Deployment

Sau khi deploy:

1. **Check App Status**: 
   - Green = Running ✅
   - Yellow = Building 🔄
   - Red = Error ❌

2. **Test Functionality**:
   - Upload sample_data.xlsx
   - Run full workflow
   - Check all visualizations
   - Test export features

3. **Monitor Logs**:
   - Click "Manage app" → "Logs"
   - Kiểm tra errors (nếu có)

---

## 🔧 Troubleshooting

### Issue 1: Import Errors

**Lỗi**: `ModuleNotFoundError: No module named 'xxx'`

**Giải pháp**:
1. Kiểm tra `requirements.txt`
2. Thêm missing packages
3. Push update lên GitHub
4. Streamlit sẽ tự động redeploy

### Issue 2: App Không Start

**Lỗi**: App stuck ở "Running..."

**Giải pháp**:
1. Check logs để xem error message
2. Test local trước: `streamlit run app.py`
3. Fix errors và push lại

### Issue 3: Memory Limit

**Lỗi**: App killed do out of memory

**Giải pháp**:
- Streamlit Cloud free tier: 1GB RAM
- Tối ưu code:
  - Không load quá nhiều data cùng lúc
  - Use `@st.cache_data` cho heavy computations
  - Clear unused variables

### Issue 4: File Upload Issues

**Lỗi**: Không upload được file lớn

**Giải pháp**:
- Max file size: 200MB (set trong config.toml)
- Nếu cần lớn hơn, upgrade plan

---

## 🎨 Customization Sau Deploy

### 1. Update App

```bash
# Make changes locally
git add .
git commit -m "Update: description of changes"
git push

# Streamlit Cloud tự động redeploy trong vài phút
```

### 2. Custom Domain (Optional)

Streamlit Cloud Pro features:
- Custom domain
- Password protection
- Private apps
- More resources

Free tier đủ cho most use cases!

### 3. Analytics

Monitor usage:
- "Manage app" → "Analytics"
- View visitor count, popular pages, etc.

---

## 📊 Post-Deployment

### Share Your App

Update README.md với deployed URL:

```markdown
## 🚀 Live Demo

Try it now: [https://your-username-ai-maintenance-optimizer.streamlit.app](https://your-username-ai-maintenance-optimizer.streamlit.app)
```

### Promote

- Share on LinkedIn
- Internal company communication
- Aviation maintenance communities
- Technical forums

---

## 🔐 Security Notes

### For Production Use:

1. **API Keys**: 
   - Use Streamlit secrets: `.streamlit/secrets.toml`
   - Never commit secrets to GitHub

2. **Authentication**:
   - Consider adding login (Streamlit Pro)
   - Or use internal network only

3. **Data Privacy**:
   - Uploaded files are temporary
   - Not stored permanently on server
   - Use HTTPS (automatic with Streamlit Cloud)

---

## 📈 Monitoring & Maintenance

### Regular Tasks:

- **Weekly**: Check logs for errors
- **Monthly**: Update dependencies
- **Quarterly**: Review user feedback

### Updates:

```bash
# Update packages
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt

# Test locally
streamlit run app.py

# Push if OK
git add requirements.txt
git commit -m "Update: dependencies"
git push
```

---

## 🆘 Support

### Streamlit Cloud Support:
- Docs: https://docs.streamlit.io/streamlit-community-cloud
- Forum: https://discuss.streamlit.io/
- GitHub Issues: https://github.com/streamlit/streamlit/issues

### App-Specific Issues:
- GitHub Issues: https://github.com/YOUR_USERNAME/ai-maintenance-optimizer/issues
- Email: your-team@example.com

---

## ✅ Deployment Checklist

Before going live:

- [ ] All features working locally
- [ ] Sample data tested
- [ ] README updated with live URL
- [ ] GitHub repo is public (or invite collaborators)
- [ ] App deployed successfully on Streamlit Cloud
- [ ] All visualizations rendering correctly
- [ ] Export functionality working
- [ ] Mobile responsive (test on phone)
- [ ] Share with initial users for feedback

---

## 🎉 Success!

Congratulations! Your AI Maintenance Task Optimizer is now live! 🚀

Next steps:
1. Gather user feedback
2. Iterate and improve
3. Add advanced features
4. Scale as needed

**Happy Optimizing!** 🛩️

---

*AI Maintenance Optimization Team © 2025*
