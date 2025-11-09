"""
Data Processor Module
Xử lý và chuẩn hóa dữ liệu đầu vào
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import streamlit as st


class DataProcessor:
    """
    Class xử lý dữ liệu cho AI Maintenance Task Optimizer
    """
    
    # Mapping các tên cột có thể có
    COLUMN_MAPPINGS = {
        'task': ['task', 'task_id', 'task_number', 'taskcard', 'card'],
        'title': ['title', 'description', 'task_description', 'desc'],
        'fh': ['fh', 'flight_hours', 'flight_hour', 'flighthours'],
        'cy': ['cy', 'fc', 'cycles', 'cycle', 'flight_cycles'],
        'cal': ['cal', 'calendar', 'months', 'month', 'mo'],
        'code': ['code', 'unit', 'type', 'cal_type']
    }
    
    # Hệ số quy đổi CODE
    CODE_FACTORS = {
        'MO': 1.0,      # Month
        'WK': 4.35,     # Week (1 month = 4.35 weeks)
        'DY': 0.14,     # Day (1 month = 30 days, 1 day = 1/30 month ≈ 0.033)
        'MONTH': 1.0,
        'WEEK': 4.35,
        'DAY': 0.14
    }
    
    def __init__(self):
        self.original_df = None
        self.processed_df = None
        self.column_mapping = {}
        self.stats = {}
    
    def load_data(self, file) -> pd.DataFrame:
        """
        Load dữ liệu từ file Excel hoặc CSV
        """
        try:
            if file.name.endswith('.xlsx') or file.name.endswith('.xls'):
                df = pd.read_excel(file)
            elif file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                raise ValueError("Chỉ hỗ trợ file .xlsx, .xls, hoặc .csv")
            
            self.original_df = df.copy()
            return df
        
        except Exception as e:
            st.error(f"❌ Lỗi khi đọc file: {str(e)}")
            return None
    
    def auto_detect_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Tự động phát hiện mapping các cột
        """
        detected = {}
        df_columns_lower = {col: col.lower().strip() for col in df.columns}
        
        for standard_name, possible_names in self.COLUMN_MAPPINGS.items():
            for col, col_lower in df_columns_lower.items():
                if any(name in col_lower for name in possible_names):
                    detected[standard_name] = col
                    break
        
        return detected
    
    def validate_columns(self, mapping: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Kiểm tra xem có đủ cột bắt buộc không
        """
        required = ['task', 'title']
        missing = [col for col in required if col not in mapping or not mapping[col]]
        
        # Kiểm tra ít nhất có 1 trong FH, CY, CAL
        has_interval = any(col in mapping and mapping[col] for col in ['fh', 'cy', 'cal'])
        
        if not has_interval:
            missing.append('FH/CY/CAL (ít nhất 1)')
        
        return len(missing) == 0, missing
    
    def process_data(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
        """
        Xử lý và chuẩn hóa dữ liệu
        """
        self.column_mapping = column_mapping
        
        # Tạo dataframe mới với tên cột chuẩn
        processed = pd.DataFrame()
        
        # Copy các cột bắt buộc
        processed['TASK'] = df[column_mapping['task']].astype(str)
        processed['TITLE'] = df[column_mapping['title']].astype(str)
        
        # Copy các cột interval (nếu có)
        for col in ['fh', 'cy', 'cal', 'code']:
            if col in column_mapping and column_mapping[col]:
                processed[col.upper()] = df[column_mapping[col]]
            else:
                processed[col.upper()] = np.nan
        
        # Trích xuất ATA code
        processed['ATA'] = processed['TASK'].str.extract(r'^(\d{2})', expand=False)
        
        # Tính toán EFH
        processed = self._calculate_efh(processed)
        
        # Tính thống kê
        self._calculate_stats(processed)
        
        self.processed_df = processed
        return processed
    
    def _calculate_efh(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tính Equivalent Flight Hours (EFH)
        """
        # EFH_FH = FH
        df['EFH_FH'] = pd.to_numeric(df['FH'], errors='coerce')
        
        # EFH_FC = CY × 4.83
        df['EFH_FC'] = pd.to_numeric(df['CY'], errors='coerce') * 4.83
        
        # EFH_CAL = CAL × code_factor × 435
        def calc_efh_cal(row):
            try:
                cal = pd.to_numeric(row['CAL'], errors='coerce')
                if pd.isna(cal):
                    return np.nan
                
                code = str(row['CODE']).strip().upper() if pd.notna(row['CODE']) else 'MO'
                factor = self.CODE_FACTORS.get(code, 1.0)
                
                return cal * factor * 435
            except:
                return np.nan
        
        df['EFH_CAL'] = df.apply(calc_efh_cal, axis=1)
        
        # Interval_EFH = MIN của các giá trị có
        df['Interval_EFH'] = df[['EFH_FH', 'EFH_FC', 'EFH_CAL']].min(axis=1)
        
        return df
    
    def _calculate_stats(self, df: pd.DataFrame):
        """
        Tính thống kê về dữ liệu
        """
        valid_tasks = df[df['Interval_EFH'].notna() & (df['Interval_EFH'] > 0)]
        
        self.stats = {
            'total_tasks': len(df),
            'valid_tasks': len(valid_tasks),
            'invalid_tasks': len(df) - len(valid_tasks),
            'has_fh': df['FH'].notna().sum(),
            'has_cy': df['CY'].notna().sum(),
            'has_cal': df['CAL'].notna().sum(),
            'min_efh': valid_tasks['Interval_EFH'].min() if len(valid_tasks) > 0 else 0,
            'max_efh': valid_tasks['Interval_EFH'].max() if len(valid_tasks) > 0 else 0,
            'mean_efh': valid_tasks['Interval_EFH'].mean() if len(valid_tasks) > 0 else 0,
            'median_efh': valid_tasks['Interval_EFH'].median() if len(valid_tasks) > 0 else 0,
            'ata_count': df['ATA'].nunique()
        }
    
    def get_valid_tasks(self) -> pd.DataFrame:
        """
        Lấy các tasks có interval hợp lệ
        """
        if self.processed_df is None:
            return None
        
        return self.processed_df[
            (self.processed_df['Interval_EFH'].notna()) & 
            (self.processed_df['Interval_EFH'] > 0)
        ].copy()
    
    def get_stats_summary(self) -> Dict:
        """
        Trả về thống kê tổng hợp
        """
        return self.stats
    
    def export_processed_data(self, output_path: str):
        """
        Export dữ liệu đã xử lý
        """
        if self.processed_df is not None:
            self.processed_df.to_excel(output_path, index=False)
    
    @staticmethod
    def get_sample_data_info() -> str:
        """
        Trả về thông tin về format dữ liệu mẫu
        """
        return """
        📋 **Yêu cầu dữ liệu đầu vào:**
        
        **Cột bắt buộc:**
        - TASK: Mã task (ví dụ: 08-VNA-01-1)
        - TITLE: Mô tả task
        
        **Cột interval (ít nhất 1):**
        - FH: Flight Hours
        - CY: Cycles (Flight Cycles)
        - CAL: Calendar (thời gian theo lịch)
        - CODE: Đơn vị CAL (MO=Month, WK=Week, DY=Day)
        
        **Công thức quy đổi:**
        - EFH_FH = FH
        - EFH_FC = CY × 4.83
        - EFH_CAL = CAL × code_factor × 435
        - Interval_EFH = MIN(EFH_FH, EFH_FC, EFH_CAL)
        """


# Example usage
if __name__ == "__main__":
    processor = DataProcessor()
    print("✅ DataProcessor module loaded successfully")
