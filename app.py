"""
AI Maintenance Task Optimizer
Streamlit Application
"""

import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils import DataProcessor, APBCOptimizer, Visualizer

# Page config
st.set_page_config(
    page_title="AI Maintenance Task Optimizer",
    page_icon="🛩️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF4B4B;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stAlert {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'data_processed' not in st.session_state:
        st.session_state.data_processed = False
    if 'optimization_done' not in st.session_state:
        st.session_state.optimization_done = False
    if 'processor' not in st.session_state:
        st.session_state.processor = DataProcessor()
    if 'optimizer' not in st.session_state:
        st.session_state.optimizer = None
    if 'visualizer' not in st.session_state:
        st.session_state.visualizer = Visualizer()


def render_header():
    """Render page header"""
    st.markdown('<div class="main-header">🛩️ AI Maintenance Task Optimizer</div>', 
                unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Tối ưu hóa kế hoạch bảo dưỡng máy bay bằng AI</div>', 
                unsafe_allow_html=True)
    
    # Info box
    with st.expander("ℹ️ Về ứng dụng này"):
        st.markdown("""
        **AI Maintenance Task Optimizer** sử dụng thuật toán **APBC** (Adaptive Peak-Based Clustering) 
        để tự động phân nhóm các task bảo dưỡng, phát hiện nested groups, và tối ưu hóa kế hoạch bảo dưỡng.
        
        **Tính năng chính:**
        - ✅ Tự động phân nhóm tasks theo tần suất
        - ✅ Kiểm tra tuân thủ ±20% compliance
        - ✅ Phát hiện nested groups (giảm 60%+ công việc)
        - ✅ Visualization tương tác
        - ✅ Export Excel với 5 sheets
        
        **Thuật toán APBC:**
        1. Dynamic Threshold Selection
        2. Adaptive Merge
        3. Task Assignment (±20%)
        4. Nested Detection (bội 2 ±10%)
        """)


def render_sidebar():
    """Render sidebar with settings"""
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/FF4B4B/FFFFFF?text=APBC+Optimizer", 
                use_column_width=True)
        
        st.markdown("### ⚙️ Cấu hình")
        
        # Advanced settings
        with st.expander("🔧 Advanced Settings"):
            target_coverage = st.slider(
                "Target Coverage (%)",
                min_value=70,
                max_value=95,
                value=80,
                step=5,
                help="Mục tiêu phủ tasks khi chọn threshold"
            ) / 100
            
            base_tolerance = st.slider(
                "Base Tolerance (%)",
                min_value=5,
                max_value=20,
                value=10,
                step=1,
                help="Tolerance cơ bản để merge peaks"
            ) / 100
            
            compliance_tolerance = st.slider(
                "Compliance Tolerance (%)",
                min_value=15,
                max_value=25,
                value=20,
                step=1,
                help="Tolerance để gán tasks vào groups"
            ) / 100
            
            nested_min = st.number_input(
                "Nested Min Ratio",
                min_value=1.6,
                max_value=1.9,
                value=1.8,
                step=0.1,
                help="Ratio tối thiểu cho nested"
            )
            
            nested_max = st.number_input(
                "Nested Max Ratio",
                min_value=2.0,
                max_value=2.4,
                value=2.2,
                step=0.1,
                help="Ratio tối đa cho nested"
            )
        
        # About
        st.markdown("---")
        st.markdown("### 📚 Tài liệu")
        st.markdown("""
        - [GitHub Repository](https://github.com/yourusername/ai-maintenance-optimizer)
        - [Algorithm Documentation](https://github.com/yourusername/ai-maintenance-optimizer/blob/main/docs/ALGORITHM.md)
        - [User Guide](https://github.com/yourusername/ai-maintenance-optimizer/blob/main/docs/USER_GUIDE.md)
        """)
        
        st.markdown("---")
        st.markdown("### 👥 Team")
        st.markdown("AI Maintenance Optimization Team © 2025")
        
        return {
            'target_coverage': target_coverage,
            'base_tolerance': base_tolerance,
            'compliance_tolerance': compliance_tolerance,
            'nested_ratio_range': (nested_min, nested_max)
        }


def render_upload_section():
    """Render file upload section"""
    st.markdown("## 📂 Bước 1: Upload Dữ Liệu")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Chọn file Excel hoặc CSV",
            type=['xlsx', 'xls', 'csv'],
            help="File chứa danh sách tasks bảo dưỡng"
        )
    
    with col2:
        with st.expander("📋 Yêu cầu dữ liệu"):
            st.markdown(DataProcessor.get_sample_data_info())
    
    if uploaded_file is not None:
        with st.spinner("Đang đọc file..."):
            df = st.session_state.processor.load_data(uploaded_file)
            
            if df is not None:
                st.session_state.data_loaded = True
                st.session_state.raw_df = df
                
                st.success(f"✅ Đã load {len(df)} tasks từ file '{uploaded_file.name}'")
                
                # Preview data
                with st.expander("👀 Xem dữ liệu gốc"):
                    st.dataframe(df.head(10), use_container_width=True)
                
                return True
    
    return False


def render_column_mapping():
    """Render column mapping section"""
    st.markdown("## 🔄 Bước 2: Mapping Cột")
    
    df = st.session_state.raw_df
    
    # Auto-detect columns
    auto_mapping = st.session_state.processor.auto_detect_columns(df)
    
    st.info("💡 Hệ thống đã tự động phát hiện mapping. Vui lòng kiểm tra và điều chỉnh nếu cần.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Cột bắt buộc")
        task_col = st.selectbox(
            "TASK *",
            options=[''] + list(df.columns),
            index=list(df.columns).index(auto_mapping['task']) + 1 if 'task' in auto_mapping else 0
        )
        
        title_col = st.selectbox(
            "TITLE *",
            options=[''] + list(df.columns),
            index=list(df.columns).index(auto_mapping['title']) + 1 if 'title' in auto_mapping else 0
        )
    
    with col2:
        st.markdown("### Cột Interval")
        fh_col = st.selectbox(
            "FH (Flight Hours)",
            options=[''] + list(df.columns),
            index=list(df.columns).index(auto_mapping['fh']) + 1 if 'fh' in auto_mapping else 0
        )
        
        cy_col = st.selectbox(
            "CY (Cycles)",
            options=[''] + list(df.columns),
            index=list(df.columns).index(auto_mapping['cy']) + 1 if 'cy' in auto_mapping else 0
        )
    
    with col3:
        st.markdown("### Cột Calendar")
        cal_col = st.selectbox(
            "CAL (Calendar)",
            options=[''] + list(df.columns),
            index=list(df.columns).index(auto_mapping['cal']) + 1 if 'cal' in auto_mapping else 0
        )
        
        code_col = st.selectbox(
            "CODE (Unit)",
            options=[''] + list(df.columns),
            index=list(df.columns).index(auto_mapping['code']) + 1 if 'code' in auto_mapping else 0
        )
    
    # Build mapping
    column_mapping = {}
    if task_col: column_mapping['task'] = task_col
    if title_col: column_mapping['title'] = title_col
    if fh_col: column_mapping['fh'] = fh_col
    if cy_col: column_mapping['cy'] = cy_col
    if cal_col: column_mapping['cal'] = cal_col
    if code_col: column_mapping['code'] = code_col
    
    # Validate
    is_valid, missing = st.session_state.processor.validate_columns(column_mapping)
    
    if not is_valid:
        st.error(f"❌ Thiếu cột bắt buộc: {', '.join(missing)}")
        return None
    
    # Process button
    if st.button("🚀 Xử lý dữ liệu", type="primary", use_container_width=True):
        with st.spinner("Đang xử lý..."):
            processed_df = st.session_state.processor.process_data(df, column_mapping)
            st.session_state.processed_df = processed_df
            st.session_state.data_processed = True
            st.success("✅ Dữ liệu đã được xử lý thành công!")
            st.rerun()
    
    return column_mapping


def render_data_overview():
    """Render processed data overview"""
    st.markdown("## 📊 Bước 3: Tổng Quan Dữ Liệu")
    
    stats = st.session_state.processor.get_stats_summary()
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Tổng Tasks", f"{stats['total_tasks']:,}")
    
    with col2:
        st.metric("Tasks Hợp Lệ", f"{stats['valid_tasks']:,}",
                 delta=f"{stats['valid_tasks']/stats['total_tasks']*100:.1f}%")
    
    with col3:
        st.metric("Trung Bình EFH", f"{stats['mean_efh']:,.0f}")
    
    with col4:
        st.metric("ATA Chapters", f"{stats['ata_count']}")
    
    # Distribution chart
    valid_df = st.session_state.processor.get_valid_tasks()
    
    fig = st.session_state.visualizer.plot_distribution_histogram(
        valid_df, [], 
        title="Phân Bố Interval EFH (Chưa Clustering)"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed stats
    with st.expander("📈 Thống kê chi tiết"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Phân Bố Interval Types:**")
            st.write(f"- Có FH: {stats['has_fh']}")
            st.write(f"- Có CY: {stats['has_cy']}")
            st.write(f"- Có CAL: {stats['has_cal']}")
        
        with col2:
            st.markdown("**Range EFH:**")
            st.write(f"- Min: {stats['min_efh']:,.0f}")
            st.write(f"- Max: {stats['max_efh']:,.0f}")
            st.write(f"- Median: {stats['median_efh']:,.0f}")


def render_optimization_section(settings):
    """Render optimization section"""
    st.markdown("## 🎯 Bước 4: Chạy Thuật Toán APBC")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("✨ Sẵn sàng chạy thuật toán Adaptive Peak-Based Clustering!")
    
    with col2:
        run_button = st.button(
            "🚀 Bắt Đầu Tối Ưu",
            type="primary",
            use_container_width=True
        )
    
    if run_button:
        with st.spinner("🔄 Đang chạy APBC..."):
            # Initialize optimizer
            optimizer = APBCOptimizer(
                target_coverage=settings['target_coverage'],
                base_tolerance=settings['base_tolerance'],
                compliance_tolerance=settings['compliance_tolerance'],
                nested_ratio_range=settings['nested_ratio_range'],
                verbose=False
            )
            
            # Run optimization
            valid_df = st.session_state.processor.get_valid_tasks()
            results = optimizer.fit(valid_df)
            
            # Save to session state
            st.session_state.optimizer = optimizer
            st.session_state.results = results
            st.session_state.optimization_done = True
            
            st.success("✅ Tối ưu hóa hoàn thành!")
            st.rerun()


def render_results_section():
    """Render optimization results"""
    st.markdown("## 📊 Kết Quả Tối Ưu")
    
    results = st.session_state.results
    
    # Metrics
    metrics = st.session_state.visualizer.create_summary_metrics(results)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Số Groups", metrics['num_groups'])
    
    with col2:
        st.metric("In-Group Rate", f"{metrics['in_group_rate']:.1f}%")
    
    with col3:
        st.metric("Nested Rels", metrics['num_nested'])
    
    with col4:
        st.metric("Giảm Công Việc", f"{metrics['reduction_rate']:.1f}%")
    
    with col5:
        st.metric("Avg Deviation", f"{metrics['avg_deviation']:.2f}%")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "📈 Groups",
        "🔗 Nested",
        "📋 Data Tables",
        "🏢 ATA Analysis"
    ])
    
    with tab1:
        render_overview_tab(results, metrics)
    
    with tab2:
        render_groups_tab(results)
    
    with tab3:
        render_nested_tab(results)
    
    with tab4:
        render_data_tables_tab(results)
    
    with tab5:
        render_ata_tab(results)


def render_overview_tab(results, metrics):
    """Render overview tab"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution with groups
        fig = st.session_state.visualizer.plot_distribution_histogram(
            results['processed_df'],
            results['group_centers'],
            title="Phân Bố EFH với Group Centers"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Groups bar chart
        summary_df = st.session_state.optimizer.get_summary()
        fig = st.session_state.visualizer.plot_groups_bar_chart(
            summary_df,
            results['nested_relationships'],
            title="Group Centers (Cam = Nested)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Compliance scatter
    fig = st.session_state.visualizer.plot_compliance_scatter(
        results['processed_df'],
        title="Task Compliance Analysis"
    )
    st.plotly_chart(fig, use_container_width=True)


def render_groups_tab(results):
    """Render groups detail tab"""
    summary_df = st.session_state.optimizer.get_summary()
    
    st.markdown("### 📊 Chi Tiết Các Groups")
    st.dataframe(summary_df, use_container_width=True, height=400)
    
    # Download button
    csv = summary_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ Download Summary CSV",
        csv,
        "groups_summary.csv",
        "text/csv"
    )


def render_nested_tab(results):
    """Render nested relationships tab"""
    if not results['nested_relationships']:
        st.warning("Không có nested relationships")
        return
    
    # Nested chains visualization
    fig = st.session_state.visualizer.plot_nested_relationships_tree(
        results['nested_chains'],
        results['group_centers'],
        title="Nested Chains Visualization"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Nested table
    st.markdown("### 🔗 Chi Tiết Nested Relationships")
    nested_df = pd.DataFrame(results['nested_relationships'])
    nested_df['Small_Group'] = nested_df['Small_Group'] + 1
    nested_df['Large_Group'] = nested_df['Large_Group'] + 1
    st.dataframe(nested_df, use_container_width=True)


def render_data_tables_tab(results):
    """Render data tables tab"""
    tab1, tab2 = st.tabs(["✅ In-Group Tasks", "❌ Out-of-Phase Tasks"])
    
    with tab1:
        in_group = results['in_group'][
            ['TASK', 'TITLE', 'Interval_EFH', 'Group_ID', 'Group_Center', 'Deviation']
        ].copy()
        in_group['Group_ID'] = in_group['Group_ID'] + 1
        in_group['Deviation_%'] = (in_group['Deviation'] * 100).round(2)
        in_group = in_group.drop('Deviation', axis=1)
        
        st.dataframe(in_group, use_container_width=True, height=500)
        st.metric("Tổng số", f"{len(in_group):,} tasks")
    
    with tab2:
        out_of_phase = results['out_of_phase'][
            ['TASK', 'TITLE', 'Interval_EFH']
        ].copy()
        
        if len(out_of_phase) > 0:
            st.dataframe(out_of_phase, use_container_width=True, height=500)
            st.metric("Tổng số", f"{len(out_of_phase):,} tasks")
        else:
            st.success("🎉 Tất cả tasks đều in-group!")


def render_ata_tab(results):
    """Render ATA analysis tab"""
    fig = st.session_state.visualizer.plot_ata_analysis(
        results['processed_df'],
        title="Phân Tích Theo ATA Chapter"
    )
    st.plotly_chart(fig, use_container_width=True)


def render_export_section():
    """Render export section"""
    st.markdown("## 📥 Export Kết Quả")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Excel (5 Sheets)", use_container_width=True):
            with st.spinner("Đang tạo file Excel..."):
                output = BytesIO()
                st.session_state.optimizer.export_results(output)
                output.seek(0)
                
                st.download_button(
                    "⬇️ Download Excel",
                    output,
                    "APBC_Results.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    with col2:
        summary_df = st.session_state.optimizer.get_summary()
        csv = summary_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📄 Export Summary CSV",
            csv,
            "groups_summary.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col3:
        # Execution log
        log_text = "\n".join(st.session_state.results['execution_log'])
        st.download_button(
            "📝 Download Execution Log",
            log_text,
            "execution_log.txt",
            "text/plain",
            use_container_width=True
        )


def main():
    """Main application"""
    initialize_session_state()
    
    render_header()
    
    settings = render_sidebar()
    
    # Step 1: Upload
    if not st.session_state.data_loaded:
        if not render_upload_section():
            st.info("👆 Vui lòng upload file để bắt đầu")
            return
    
    # Step 2: Column mapping
    if st.session_state.data_loaded and not st.session_state.data_processed:
        render_column_mapping()
        return
    
    # Step 3: Data overview
    if st.session_state.data_processed and not st.session_state.optimization_done:
        render_data_overview()
        render_optimization_section(settings)
        return
    
    # Step 4: Results
    if st.session_state.optimization_done:
        render_results_section()
        render_export_section()


if __name__ == "__main__":
    main()
