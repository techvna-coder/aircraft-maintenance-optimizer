"""
APBC Optimizer Module
Adaptive Peak-Based Clustering Algorithm
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
import streamlit as st


class APBCOptimizer:
    """
    Adaptive Peak-Based Clustering Optimizer
    Thuật toán tối ưu cho phân nhóm task bảo dưỡng
    """
    
    def __init__(self, 
                 target_coverage: float = 0.80,
                 base_tolerance: float = 0.10,
                 compliance_tolerance: float = 0.20,
                 nested_ratio_range: Tuple[float, float] = (1.8, 2.2),
                 verbose: bool = True):
        """
        Parameters:
        -----------
        target_coverage: Mục tiêu phủ tasks (mặc định 80%)
        base_tolerance: Tolerance cơ bản để merge peaks (mặc định 10%)
        compliance_tolerance: Tolerance để gán tasks (mặc định 20%)
        nested_ratio_range: Khoảng ratio để phát hiện nested (mặc định 1.8-2.2)
        verbose: Hiển thị log chi tiết
        """
        self.target_coverage = target_coverage
        self.base_tolerance = base_tolerance
        self.compliance_tolerance = compliance_tolerance
        self.nested_ratio_range = nested_ratio_range
        self.verbose = verbose
        
        self.group_centers = []
        self.nested_relationships = []
        self.results = {}
        self.execution_log = []
    
    def _log(self, message: str):
        """
        Log message
        """
        self.execution_log.append(message)
        if self.verbose:
            print(message)
    
    def find_optimal_threshold(self, value_counts: pd.Series, total_tasks: int) -> int:
        """
        Bước 1: Tìm threshold tối ưu động
        """
        self._log(f"\n📌 BƯỚC 1: Tìm threshold tối ưu (target: {self.target_coverage*100:.0f}%)")
        
        for threshold in range(20, 0, -1):
            peaks = value_counts[value_counts >= threshold]
            coverage = peaks.sum() / total_tasks
            
            if coverage >= self.target_coverage:
                self._log(f"  ✅ Threshold = {threshold}")
                self._log(f"     → {len(peaks)} peaks")
                self._log(f"     → Coverage: {coverage*100:.1f}%")
                return threshold
        
        return 1  # Fallback
    
    def adaptive_merge(self, peaks: List[float], value_counts: pd.Series) -> List[float]:
        """
        Bước 2: Merge peaks với tolerance động
        """
        self._log(f"\n📌 BƯỚC 2: Merge peaks với adaptive tolerance")
        
        merged = []
        current_group = [peaks[0]]
        
        for peak in peaks[1:]:
            # Tolerance tăng theo scale
            if peak < 10000:
                tolerance = self.base_tolerance
            elif peak < 30000:
                tolerance = self.base_tolerance * 1.2
            else:
                tolerance = self.base_tolerance * 1.5
            
            ratio = peak / current_group[0]
            
            if ratio <= (1 + tolerance):
                current_group.append(peak)
            else:
                # Chọn giá trị PHỔ BIẾN NHẤT
                center = max(current_group, key=lambda x: value_counts[x])
                merged.append(center)
                current_group = [peak]
        
        # Group cuối
        center = max(current_group, key=lambda x: value_counts[x])
        merged.append(center)
        
        self._log(f"  ✅ {len(peaks)} peaks → {len(merged)} groups")
        
        return sorted(merged)
    
    def assign_tasks(self, df: pd.DataFrame, centers: List[float]) -> pd.DataFrame:
        """
        Bước 3: Gán tasks vào groups với compliance check
        """
        self._log(f"\n📌 BƯỚC 3: Gán tasks (tolerance ±{self.compliance_tolerance*100:.0f}%)")
        
        df['Group_ID'] = -1
        df['Group_Center'] = 0.0
        df['Deviation'] = 0.0
        
        for idx, row in df.iterrows():
            interval_efh = row['Interval_EFH']
            best_group = -1
            min_deviation = float('inf')
            
            for i, center in enumerate(centers):
                deviation = abs(interval_efh - center) / center
                
                if deviation <= self.compliance_tolerance and deviation < min_deviation:
                    min_deviation = deviation
                    best_group = i
            
            df.at[idx, 'Group_ID'] = best_group
            if best_group >= 0:
                df.at[idx, 'Group_Center'] = centers[best_group]
                df.at[idx, 'Deviation'] = min_deviation
        
        in_group = df[df['Group_ID'] >= 0]
        out_of_phase = df[df['Group_ID'] == -1]
        
        self._log(f"  ✅ In-group: {len(in_group)} ({len(in_group)/len(df)*100:.1f}%)")
        self._log(f"  ❌ Out-of-phase: {len(out_of_phase)} ({len(out_of_phase)/len(df)*100:.1f}%)")
        
        return df
    
    def detect_nested(self, centers: List[float]) -> List[Dict]:
        """
        Bước 4: Phát hiện nested relationships
        """
        self._log("\n📌 BƯỚC 4: Phát hiện nested groups")
        
        nested_info = []
        min_ratio, max_ratio = self.nested_ratio_range
        
        for i in range(len(centers)):
            for j in range(i+1, len(centers)):
                ratio = centers[j] / centers[i]
                
                # Bội số 2
                if min_ratio <= ratio <= max_ratio:
                    nested_info.append({
                        'Small_Group': i,
                        'Small_Center': centers[i],
                        'Large_Group': j,
                        'Large_Center': centers[j],
                        'Ratio': ratio,
                        'Multiple': 2
                    })
                # Bội số 3
                elif 2.7 <= ratio <= 3.3:
                    nested_info.append({
                        'Small_Group': i,
                        'Small_Center': centers[i],
                        'Large_Group': j,
                        'Large_Center': centers[j],
                        'Ratio': ratio,
                        'Multiple': 3
                    })
                # Bội số 4
                elif 3.6 <= ratio <= 4.4:
                    nested_info.append({
                        'Small_Group': i,
                        'Small_Center': centers[i],
                        'Large_Group': j,
                        'Large_Center': centers[j],
                        'Ratio': ratio,
                        'Multiple': 4
                    })
        
        if nested_info:
            unique_small = len(set([n['Small_Group'] for n in nested_info]))
            self._log(f"  ✅ {len(nested_info)} nested relationships")
            self._log(f"     → {unique_small} groups có thể nested")
            self._log(f"     → Giảm {unique_small}/{len(centers)} = {unique_small/len(centers)*100:.1f}%")
        else:
            self._log("  ❌ Không phát hiện nested groups")
        
        return nested_info
    
    def build_nested_chains(self, nested_relationships: List[Dict]) -> List[List[int]]:
        """
        Xây dựng nested chains từ relationships
        """
        if not nested_relationships:
            return []
        
        chains = []
        processed = set()
        
        # Tìm các starting points (groups không là large của bất kỳ ai)
        all_large = set([n['Large_Group'] for n in nested_relationships])
        all_small = set([n['Small_Group'] for n in nested_relationships])
        starting_points = all_small - all_large
        
        for start in starting_points:
            if start in processed:
                continue
            
            chain = [start]
            current = start
            
            while True:
                # Tìm large group tiếp theo
                next_groups = [n for n in nested_relationships if n['Small_Group'] == current]
                if not next_groups:
                    break
                
                # Lấy large group lớn nhất
                next_rel = max(next_groups, key=lambda x: x['Large_Center'])
                next_group = next_rel['Large_Group']
                
                if next_group in chain:  # Tránh vòng lặp
                    break
                
                chain.append(next_group)
                current = next_group
            
            if len(chain) >= 2:
                chains.append(chain)
                processed.update(chain)
        
        return chains
    
    def fit(self, df: pd.DataFrame) -> Dict:
        """
        Chạy toàn bộ thuật toán APBC
        """
        self.execution_log = []
        self._log("=" * 70)
        self._log("🚀 ADAPTIVE PEAK-BASED CLUSTERING (APBC)")
        self._log("=" * 70)
        
        # Kiểm tra dữ liệu
        if 'Interval_EFH' not in df.columns:
            raise ValueError("Dataframe phải có cột 'Interval_EFH'")
        
        # Lọc tasks hợp lệ
        valid_df = df[(df['Interval_EFH'].notna()) & (df['Interval_EFH'] > 0)].copy()
        self._log(f"\n📊 Dữ liệu: {len(valid_df)}/{len(df)} tasks hợp lệ")
        
        # Phân tích phân bố
        value_counts = valid_df['Interval_EFH'].value_counts()
        
        # Bước 1: Dynamic threshold
        threshold = self.find_optimal_threshold(value_counts, len(valid_df))
        peaks = value_counts[value_counts >= threshold].index.sort_values().tolist()
        
        # Bước 2: Adaptive merge
        self.group_centers = self.adaptive_merge(peaks, value_counts)
        
        # Bước 3: Task assignment
        valid_df = self.assign_tasks(valid_df, self.group_centers)
        
        # Bước 4: Nested detection
        self.nested_relationships = self.detect_nested(self.group_centers)
        
        # Build nested chains
        nested_chains = self.build_nested_chains(self.nested_relationships)
        
        # Lưu kết quả
        self.results = {
            'processed_df': valid_df,
            'group_centers': self.group_centers,
            'nested_relationships': self.nested_relationships,
            'nested_chains': nested_chains,
            'in_group': valid_df[valid_df['Group_ID'] >= 0],
            'out_of_phase': valid_df[valid_df['Group_ID'] == -1],
            'execution_log': self.execution_log
        }
        
        self._log("\n" + "=" * 70)
        self._log("✅ HOÀN THÀNH!")
        self._log("=" * 70)
        
        return self.results
    
    def get_summary(self) -> pd.DataFrame:
        """
        Tạo bảng tóm tắt các groups
        """
        if not self.results:
            return None
        
        df = self.results['in_group']
        
        summary = []
        for i, center in enumerate(self.group_centers):
            group_tasks = df[df['Group_ID'] == i]
            
            if len(group_tasks) > 0:
                # Check if nested
                is_nested_small = any(
                    n['Small_Group'] == i for n in self.nested_relationships
                )
                
                summary.append({
                    'Group_ID': i + 1,
                    'Center_EFH': center,
                    'Num_Tasks': len(group_tasks),
                    'Avg_Deviation_%': group_tasks['Deviation'].mean() * 100,
                    'Max_Deviation_%': group_tasks['Deviation'].max() * 100,
                    'Is_Nested': '✅' if is_nested_small else ''
                })
        
        return pd.DataFrame(summary)
    
    def export_results(self, output_path: str):
        """
        Export kết quả ra Excel (4+ sheets)
        """
        if not self.results:
            raise ValueError("Chưa có kết quả! Hãy chạy fit() trước.")
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet 1: Summary
            summary_df = self.get_summary()
            if summary_df is not None:
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Sheet 2: In-Group
            in_group_df = self.results['in_group'][
                ['TASK', 'TITLE', 'Interval_EFH', 'Group_ID', 'Group_Center', 'Deviation']
            ].copy()
            in_group_df['Group_ID'] = in_group_df['Group_ID'] + 1  # Start from 1
            in_group_df['Deviation_%'] = in_group_df['Deviation'] * 100
            in_group_df = in_group_df.drop('Deviation', axis=1)
            in_group_df.to_excel(writer, sheet_name='In-Group', index=False)
            
            # Sheet 3: Out-of-Phase
            out_df = self.results['out_of_phase'][
                ['TASK', 'TITLE', 'Interval_EFH']
            ].copy()
            out_df.to_excel(writer, sheet_name='Out-of-Phase', index=False)
            
            # Sheet 4: Nested
            if self.nested_relationships:
                nested_df = pd.DataFrame(self.nested_relationships)
                nested_df['Small_Group'] = nested_df['Small_Group'] + 1
                nested_df['Large_Group'] = nested_df['Large_Group'] + 1
                nested_df.to_excel(writer, sheet_name='Nested', index=False)
            
            # Sheet 5: Nested Chains
            if self.results.get('nested_chains'):
                chains_data = []
                for i, chain in enumerate(self.results['nested_chains'], 1):
                    chain_str = ' → '.join([f"G{g+1}" for g in chain])
                    chains_data.append({
                        'Chain_ID': i,
                        'Chain': chain_str,
                        'Length': len(chain),
                        'Groups': str([g+1 for g in chain])
                    })
                chains_df = pd.DataFrame(chains_data)
                chains_df.to_excel(writer, sheet_name='Nested_Chains', index=False)


# Example usage
if __name__ == "__main__":
    optimizer = APBCOptimizer()
    print("✅ APBCOptimizer module loaded successfully")
