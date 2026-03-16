# -*- coding: utf-8 -*-
"""
09_plot_transect_decay.py
Phase IV: Spatial Transect Analysis
Plots the Post-minus-Pre LST Anomaly per distance ring.
This eliminates inter-annual climate variability and isolates the
spatial signature of the new impervious surface.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib.figure")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def render_decay_curve(csv_path, output_image_path):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"[ERROR] Cannot find {csv_path}")
        return

    required = ['Distance_m', 'Pre_LST_mean', 'Post_LST_mean']
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"[ERROR] CSV missing columns: {missing}")
        return

    df = df.dropna(subset=required).sort_values('Distance_m').reset_index(drop=True)
    
    dist = df['Distance_m'].values
    pre = df['Pre_LST_mean'].values
    post = df['Post_LST_mean'].values
    
    # 核心：计算每个环的异常值 (Post - Pre)
    # 如果 2016-18 年夏天整体偏热，那么 Post - Pre 在所有环都是负值。
    # 但我们关注的是：核心区（0m）的异常值是否比远处（800m）的更大（更不负/更正）。
    # 这个"相对梯度"就证明了核心区特异性地增温了。
    anomaly = post - pre
    
    # 求背景异常（远场 400-800m 的均值）作为 baseline
    far_mask = dist >= 400
    background_anomaly = anomaly[far_mask].mean()
    
    # 对照后的"净热力疤痕"
    net_scar = anomaly - background_anomaly
    
    print(f"=== Spatial Transect Analysis ===")
    print(f"Core (0m) raw anomaly: {anomaly[0]:+.2f}°C")
    print(f"Background (400-800m) mean anomaly: {background_anomaly:+.2f}°C")
    print(f"Core NET scar (above background): {net_scar[0]:+.2f}°C")
    print(f"Scar decays to background (~0) at: ~{dist[np.argmin(np.abs(net_scar[1:]))+1]:.0f}m")

    # ---------------------------------------------------------
    # 双面板绘图
    # ---------------------------------------------------------
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), dpi=400,
                                   gridspec_kw={'height_ratios': [1, 1]})

    # ========== 上面板：绝对 LST 双曲线 ==========
    ax1.plot(dist, pre, color='#33CC33', linewidth=3, marker='o', markersize=6,
             label='Pre-Construction (JJA 2016-2018)')
    ax1.plot(dist, post, color='#FF4500', linewidth=3, marker='s', markersize=6,
             label='Post-Construction (JJA 2023-2025)')
    ax1.fill_between(dist, pre, post, color='#AAAAAA', alpha=0.1)
    ax1.axvline(x=0, color='#FFFFFF', linestyle='--', linewidth=1.5, alpha=0.5)
    ax1.set_ylabel('Mean Summer LST (°C)', fontsize=12, fontname='Courier New', color='#CCCCCC')
    ax1.set_title('Spatial Transect (0-800m): Absolute LST vs. Net Thermal Scar',
                  fontsize=14, fontweight='bold', fontname='Courier New', color='white', pad=15)
    ax1.legend(loc='upper right', frameon=True, facecolor='#111111', edgecolor='#444444',
               prop={'family': 'Courier New', 'size': 10})
    ax1.grid(True, color='#333333', linestyle=':', linewidth=1.5, alpha=0.6)
    ax1.tick_params(axis='both', labelsize=10, colors='#AAAAAA')
    ax1.text(0.02, 0.06,
             f'Note: 2016-18 summers were ~{abs(background_anomaly):.1f}°C warmer than 2023-25 regionally.\n'
             f'Absolute comparison is confounded. See lower panel for controlled analysis.',
             transform=ax1.transAxes, fontsize=9, fontfamily='Courier New', color='#FFCC00',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#111111', edgecolor='#FFCC00', alpha=0.8))

    # ========== 下面板：Net Thermal Scar (background-subtracted anomaly) ==========
    colors = ['#FF0000' if v > 0 else '#3399FF' for v in net_scar]
    ax2.bar(dist, net_scar, width=40, color=colors, alpha=0.8, edgecolor='white', linewidth=0.5)
    ax2.axhline(y=0, color='#AAAAAA', linestyle='-', linewidth=1.5, alpha=0.7)
    ax2.axvline(x=0, color='#FFFFFF', linestyle='--', linewidth=1.5, alpha=0.5)
    
    # 标注核心疤痕值
    ax2.annotate(f'Net Scar: {net_scar[0]:+.2f}°C',
                 xy=(0, net_scar[0]), xytext=(120, net_scar[0] + 0.5),
                 fontsize=12, fontweight='bold', color='#FF4444', fontfamily='Courier New',
                 arrowprops=dict(arrowstyle='->', color='#FF4444', lw=2))

    ax2.set_ylabel('Net Thermal Scar (°C above background)', fontsize=12, fontname='Courier New', color='#FF8888')
    ax2.set_xlabel('Distance from Impact Zone Boundary (meters)', fontsize=12, fontname='Courier New', color='#CCCCCC')
    ax2.grid(True, color='#333333', linestyle=':', linewidth=1.5, alpha=0.6)
    ax2.tick_params(axis='both', labelsize=10, colors='#AAAAAA')
    ax2.text(0.02, 0.88,
             'Background-subtracted: each bar = (Post−Pre at ring) − mean(Post−Pre at 400-800m)',
             transform=ax2.transAxes, fontsize=9, fontfamily='Courier New', color='#00FF88',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#111111', edgecolor='#00FF88', alpha=0.8))

    fig.text(0.98, 0.005,
             'Data: USGS Landsat 7+8+9 (100m) | Method: 50m Concentric Buffers, Background-Subtracted | Author: H. Li',
             fontsize=8, color='#666666', ha='right', va='bottom', fontfamily='Helvetica')

    plt.tight_layout()
    plt.savefig(output_image_path, dpi=300, bbox_inches='tight', facecolor='#111111')
    print(f"\nSAVED TRANSECT: {output_image_path}")
    if os.environ.get('MPLBACKEND') != 'Agg':
        plt.show(block=False)

if __name__ == "__main__":
    input_csv = os.path.join(PROJECT_ROOT, 'data', 'raw_telemetry', 'ee-chart_decay.csv')
    output_png = os.path.join(PROJECT_ROOT, 'visualisations', 'spatial_transect_decay_chart.png')
    render_decay_curve(input_csv, output_png)
