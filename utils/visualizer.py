"""
Visualizer Module
Tạo các biểu đồ tương tác với Plotly
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Dict, Optional
import streamlit as st


class Visualizer:
    """
    Class tạo các visualization cho APBC results
    """
    
    # Color schemes
    COLORS = {
        'primary': '#FF4B4B',
        'secondary': '#0068C9',
        'success': '#29B09D',
        'warning': '#FF8C00',
        'nested': '#FFA500',
        'normal': '#4CAF50'
    }
    
    def __init__(self):
        pass
    
    def plot_distribution_histogram(self, 
                                    df: pd.DataFrame, 
                                    group_centers: List[float],
                                    title: str = "Phân Bố Interval EFH") -> go.Figure:
        """
        Biểu đồ histogram phân bố EFH với group centers
        """
        fig = go.Figure()
        
        # Histogram
        fig.add_trace(go.Histogram(
            x=df['Interval_EFH'],
            nbinsx=50,
            name='Tasks',
            marker_color=self.COLORS['secondary'],
            opacity=0.7,
            hovertemplate='EFH: %{x:,.0f}<br>Count: %{y}<extra></extra>'
        ))
        
        # Group centers
        for i, center in enumerate(group_centers):
            fig.add_vline(
                x=center,
                line_dash="dash",
                line_color=self.COLORS['primary'],
                line_width=2,
                annotation_text=f"G{i+1}: {center:,.0f}",
                annotation_position="top",
                annotation_font_size=9
            )
        
        fig.update_layout(
            title=title,
            xaxis_title="Interval EFH",
            yaxis_title="Số lượng Tasks",
            hovermode='x unified',
            showlegend=True,
            height=500,
            template='plotly_white'
        )
        
        return fig
    
    def plot_groups_bar_chart(self, 
                              summary_df: pd.DataFrame,
                              nested_relationships: List[Dict] = None,
                              title: str = "Group Centers") -> go.Figure:
        """
        Biểu đồ cột các groups với nested highlighting
        """
        # Determine colors
        colors = []
        nested_small = set([n['Small_Group'] for n in nested_relationships]) if nested_relationships else set()
        
        for idx in range(len(summary_df)):
            if idx in nested_small:
                colors.append(self.COLORS['nested'])
            else:
                colors.append(self.COLORS['normal'])
        
        fig = go.Figure()
        
        # Bar chart
        fig.add_trace(go.Bar(
            x=summary_df['Group_ID'],
            y=summary_df['Center_EFH'],
            marker_color=colors,
            text=summary_df['Center_EFH'].apply(lambda x: f'{x:,.0f}'),
            textposition='outside',
            hovertemplate='<b>Group %{x}</b><br>' +
                         'Center: %{y:,.0f} EFH<br>' +
                         '<extra></extra>',
            showlegend=False
        ))
        
        # Add nested arrows
        if nested_relationships:
            for rel in nested_relationships[:10]:  # Limit to avoid clutter
                small_idx = rel['Small_Group']
                large_idx = rel['Large_Group']
                
                # Find y positions
                small_y = summary_df[summary_df['Group_ID'] == small_idx + 1]['Center_EFH'].values[0]
                large_y = summary_df[summary_df['Group_ID'] == large_idx + 1]['Center_EFH'].values[0]
                
                fig.add_annotation(
                    x=large_idx + 1,
                    y=large_y,
                    ax=small_idx + 1,
                    ay=small_y,
                    xref='x',
                    yref='y',
                    axref='x',
                    ayref='y',
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor='red',
                    opacity=0.6
                )
        
        fig.update_layout(
            title=title,
            xaxis_title="Group ID",
            yaxis_title="Center (EFH)",
            height=500,
            template='plotly_white',
            xaxis=dict(tickmode='linear', tick0=1, dtick=1)
        )
        
        return fig
    
    def plot_nested_relationships_tree(self,
                                       nested_chains: List[List[int]],
                                       group_centers: List[float],
                                       title: str = "Nested Chains") -> go.Figure:
        """
        Biểu đồ tree cho nested chains
        """
        if not nested_chains:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="Không có nested chains",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(height=400)
            return fig
        
        fig = go.Figure()
        
        # Plot each chain
        for chain_idx, chain in enumerate(nested_chains):
            x_positions = list(range(len(chain)))
            y_position = chain_idx
            
            # Plot nodes
            labels = [f"G{g+1}<br>{group_centers[g]:,.0f}" for g in chain]
            
            fig.add_trace(go.Scatter(
                x=x_positions,
                y=[y_position] * len(chain),
                mode='markers+text',
                marker=dict(size=20, color=self.COLORS['nested']),
                text=labels,
                textposition='top center',
                name=f'Chain {chain_idx + 1}',
                hovertemplate='<b>%{text}</b><extra></extra>'
            ))
            
            # Plot edges
            for i in range(len(chain) - 1):
                fig.add_trace(go.Scatter(
                    x=[x_positions[i], x_positions[i+1]],
                    y=[y_position, y_position],
                    mode='lines',
                    line=dict(color='red', width=2),
                    showlegend=False,
                    hoverinfo='skip'
                ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Position in Chain",
            yaxis_title="Chain ID",
            height=max(400, len(nested_chains) * 100),
            template='plotly_white',
            showlegend=True,
            yaxis=dict(tickmode='linear', tick0=0, dtick=1)
        )
        
        return fig
    
    def plot_compliance_scatter(self,
                               df: pd.DataFrame,
                               title: str = "Task Compliance") -> go.Figure:
        """
        Scatter plot deviation của tasks
        """
        in_group = df[df['Group_ID'] >= 0].copy()
        
        # Color by deviation level
        def get_color(deviation):
            if deviation <= 0.10:
                return 'green'
            elif deviation <= 0.20:
                return 'orange'
            else:
                return 'red'
        
        in_group['Color'] = in_group['Deviation'].apply(get_color)
        
        fig = go.Figure()
        
        for color in ['green', 'orange']:
            subset = in_group[in_group['Color'] == color]
            if len(subset) > 0:
                fig.add_trace(go.Scatter(
                    x=subset['Interval_EFH'],
                    y=subset['Deviation'] * 100,
                    mode='markers',
                    marker=dict(
                        color=color,
                        size=8,
                        opacity=0.6
                    ),
                    name=f'≤{10 if color=="green" else 20}%',
                    hovertemplate='<b>%{customdata[0]}</b><br>' +
                                 'EFH: %{x:,.0f}<br>' +
                                 'Deviation: %{y:.2f}%<br>' +
                                 '<extra></extra>',
                    customdata=subset[['TASK']].values
                ))
        
        # Compliance lines
        fig.add_hline(y=10, line_dash="dash", line_color="orange", 
                     annotation_text="±10%", annotation_position="right")
        fig.add_hline(y=20, line_dash="dash", line_color="red", 
                     annotation_text="±20%", annotation_position="right")
        
        fig.update_layout(
            title=title,
            xaxis_title="Interval EFH",
            yaxis_title="Deviation (%)",
            height=500,
            template='plotly_white',
            showlegend=True
        )
        
        return fig
    
    def plot_ata_analysis(self,
                         df: pd.DataFrame,
                         title: str = "Phân Tích Theo ATA Chapter") -> go.Figure:
        """
        Phân tích tasks theo ATA chapters
        """
        ata_stats = df.groupby('ATA').agg({
            'TASK': 'count',
            'Interval_EFH': 'mean'
        }).reset_index()
        ata_stats.columns = ['ATA', 'Task_Count', 'Avg_EFH']
        ata_stats = ata_stats.sort_values('Task_Count', ascending=False).head(20)
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Số Tasks theo ATA', 'Avg EFH theo ATA'),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Tasks count
        fig.add_trace(
            go.Bar(
                x=ata_stats['ATA'],
                y=ata_stats['Task_Count'],
                marker_color=self.COLORS['secondary'],
                name='Task Count',
                hovertemplate='ATA %{x}<br>Tasks: %{y}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Avg EFH
        fig.add_trace(
            go.Bar(
                x=ata_stats['ATA'],
                y=ata_stats['Avg_EFH'],
                marker_color=self.COLORS['success'],
                name='Avg EFH',
                hovertemplate='ATA %{x}<br>Avg EFH: %{y:,.0f}<extra></extra>'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text=title,
            height=500,
            showlegend=False,
            template='plotly_white'
        )
        
        return fig
    
    def create_summary_metrics(self, results: Dict) -> Dict[str, any]:
        """
        Tạo metrics summary cho dashboard
        """
        in_group = results['in_group']
        out_of_phase = results['out_of_phase']
        total = len(in_group) + len(out_of_phase)
        
        metrics = {
            'total_tasks': total,
            'in_group_count': len(in_group),
            'in_group_rate': len(in_group) / total * 100 if total > 0 else 0,
            'out_of_phase_count': len(out_of_phase),
            'num_groups': len(results['group_centers']),
            'num_nested': len(results['nested_relationships']),
            'nested_groups': len(set([n['Small_Group'] for n in results['nested_relationships']])),
            'reduction_rate': len(set([n['Small_Group'] for n in results['nested_relationships']])) / len(results['group_centers']) * 100 if len(results['group_centers']) > 0 else 0,
            'avg_deviation': in_group['Deviation'].mean() * 100 if len(in_group) > 0 else 0,
            'max_deviation': in_group['Deviation'].max() * 100 if len(in_group) > 0 else 0
        }
        
        return metrics


# Example usage
if __name__ == "__main__":
    visualizer = Visualizer()
    print("✅ Visualizer module loaded successfully")
