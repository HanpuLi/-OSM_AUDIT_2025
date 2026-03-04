# -*- coding: utf-8 -*-
"""
OSM_AUDIT_2025: Thermodynamic Time-Series Render
Processes raw LST (Land Surface Temperature) CSV data from GEE.
Filters seasonal noise via 365-day rolling mean to expose structural heating trends.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

def render_thermodynamic_chart(csv_path, output_image_path):
    print(f"--- INITIATING THERMODYNAMIC DATA PARSING: {csv_path} ---")
    
    # 1. 读取数据并处理日期
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"[ERROR] Cannot find {csv_path}. Please check the path.")
        return

    # 清洗数据：删除缺失值 (NaN)
    df = df.dropna(subset=['LST_Celsius'])
    
    # 转换时间戳并排序
    df['system:time_start'] = pd.to_datetime(df['system:time_start'])
    df = df.sort_values('system:time_start')
    df = df.set_index('system:time_start')

    print(f"Data points extracted: {len(df)}")
    
    # 2. 算法过滤：365天滚动平均 (消除冬夏温差的季节性噪音)
    # min_periods=1 确保即使窗口内数据少也能计算，防止线条断裂
    df['Rolling_Mean'] = df['LST_Celsius'].rolling('365D', min_periods=1).mean()

    # 3. 算法提取：长期结构性趋势线 (线性回归)
    # 将日期转换为数字以进行多项式拟合
    x_num = mdates.date2num(df.index)
    y_vals = df['LST_Celsius'].values
    
    # 1阶多项式拟合 (y = mx + c)
    z = np.polyfit(x_num, y_vals, 1)
    p = np.poly1d(z)
    df['Trendline'] = p(x_num)
    
    # 计算总升温幅度
    start_temp = df['Trendline'].iloc[0]
    end_temp = df['Trendline'].iloc[-1]
    net_increase = end_temp - start_temp
    print(f"Structural Temperature Trend: {'+' if net_increase > 0 else ''}{net_increase:.2f} °C")

    # ==========================================
    # 视觉渲染 (Data Visualisation) - 匹配 PPT 极客深色风格
    # ==========================================
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 7), dpi=300)
    
    # 图层 1: 原始观测数据点 (半透明灰色，作为背景噪音)
    ax.scatter(df.index, df['LST_Celsius'], color='#888888', alpha=0.4, s=15, 
               label='Raw LST Observations (Cloud-masked)')
    
    # 图层 2: 365天滚动均线 (警示橙色，展示平滑后的真实代谢波动)
    ax.plot(df.index, df['Rolling_Mean'], color='#FF8C00', linewidth=2.5, alpha=0.9, 
            label='365-Day Rolling Mean (Seasonal Noise Removed)')
    
    # 图层 3: 长期趋势线 (血红色虚线，展示不可逆的物理疤痕)
    ax.plot(df.index, df['Trendline'], color='#FF0000', linestyle='--', linewidth=3, 
            label=f'Structural Trendline (Net Δ: +{net_increase:.2f}°C)')

    # 图表修饰
    ax.set_title('Thermodynamic Spatial Audit: Algorithmic Metabolism in the Sprawl Zone (2015-2023)', 
                 fontsize=18, fontweight='bold', color='white', pad=20, fontfamily='monospace')
    ax.set_ylabel('Land Surface Temperature (°C)', fontsize=14, fontweight='bold', color='#CCCCCC')
    ax.set_xlabel('Temporal Axis (Years)', fontsize=14, fontweight='bold', color='#CCCCCC')
    
    # 坐标轴格式化
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.tick_params(axis='both', which='major', labelsize=12, colors='#AAAAAA')
    
    # 网格线
    ax.grid(True, color='#333333', linestyle=':', linewidth=1)
    
    # 图例
    ax.legend(loc='upper left', fontsize=12, frameon=True, facecolor='#111111', edgecolor='#444444')

    # 保存与展示
    plt.tight_layout()
    plt.savefig(output_image_path, facecolor=fig.get_facecolor(), edgecolor='none')
    print(f"--- CHART RENDERED SUCCESSFULLY: {output_image_path} ---")
    plt.show()

if __name__ == "__main__":
    # 请确保此处的文件名与你的本地文件一致
    input_csv = "ee-chart.csv" 
    output_png = "thermodynamic_scar_chart.png"
    
    render_thermodynamic_chart(input_csv, output_png)