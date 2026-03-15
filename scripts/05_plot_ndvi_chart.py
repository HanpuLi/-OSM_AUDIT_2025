"""
05_plot_ndvi_chart.py
GEE 导出的 NDVI CSV -> 365D 滚动均线 + 2018 基线对比图
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def plot_ndvi_collapse(csv_path, output_path):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"[ERROR] Cannot find {csv_path}")
        return

    df['system:time_start'] = pd.to_datetime(df['system:time_start'])
    df = df.dropna(subset=['NDVI']).sort_values('system:time_start')
    df.set_index('system:time_start', inplace=True)

    # 365D 滚动均线 + 2018 基线
    df['Structural_Trend'] = df['NDVI'].rolling('365D', min_periods=5).mean()
    baseline_2018 = df.loc['2018', 'NDVI'].mean()

    # 动态 Y 轴范围
    ndvi_min = df['Structural_Trend'].min()
    y_low = min(ndvi_min * 0.8, baseline_2018 * 0.6)
    y_high = baseline_2018 * 1.2

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 8), dpi=400)

    ax.scatter(df.index, df['NDVI'], color='#555555', alpha=0.25, s=8, label='Raw (Seasonal Noise)')
    ax.axhline(y=baseline_2018, color='#00FFCC', linestyle='--', linewidth=3, 
               label=f'2018 Baseline (~{baseline_2018:.3f})')
    ax.plot(df.index, df['Structural_Trend'], color='#FF3333', linewidth=5, 
            label='Structural Trend (365D Rolling)', alpha=0.95)
    ax.fill_between(df.index, df['Structural_Trend'], baseline_2018, 
                    where=(df['Structural_Trend'] < baseline_2018), 
                    color='#FF3333', alpha=0.25, interpolate=True, label='Permanent Loss')

    ax.set_ylim(y_low, y_high)
    ax.set_title('Micro-Scale Spatial Audit: NDVI Collapse in Sprawl Zone (2018-2026)', 
                 fontsize=18, fontweight='bold', fontname='Courier New', color='white', pad=25)
    ax.set_ylabel('NDVI (Chlorophyll Reflectance)', fontsize=14, fontname='Courier New', color='#CCCCCC')
    ax.set_xlabel('Temporal Axis (Years)', fontsize=14, fontname='Courier New', color='#CCCCCC')

    ax.grid(True, color='#333333', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.legend(loc='upper right', frameon=False, prop={'family': 'Courier New', 'size': 11})
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator())

    plt.tight_layout()
    plt.savefig(output_path, facecolor='black', dpi=400, bbox_inches='tight')
    print(f"SAVED: {output_path}")
    plt.show()


if __name__ == "__main__":
    input_csv = os.path.join(PROJECT_ROOT, 'data', 'raw_telemetry', 'ee-chart_ndvi_2018_2026.csv')
    output_png = os.path.join(PROJECT_ROOT, 'visualisations', 'NDVICollapseChart.png')
    plot_ndvi_collapse(input_csv, output_png)
