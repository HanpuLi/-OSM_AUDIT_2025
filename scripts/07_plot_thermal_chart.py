# -*- coding: utf-8 -*-
"""
07_plot_thermal_chart.py
GEE 导出的 LST CSV -> STL 时间序列分解 + DiD Mann-Kendall 趋势检验
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import warnings
import pymannkendall as mk
from statsmodels.tsa.seasonal import STL

# Suppress interactive mode warnings for CLI execution
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib.figure")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def render_thermodynamic_chart(csv_path, output_image_path):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"[ERROR] Cannot find {csv_path}")
        return

    # ---------------------------------------------------------
    # 数据验证
    # ---------------------------------------------------------
    required = ['Sprawl_Zone_Core_mean', 'Sprawl_Zone_Core_std',
                'Control_Zone_mean', 'Control_Zone_std']
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"[ERROR] CSV missing columns: {missing}. Did you update the GEE LST script?")
        return

    # ---------------------------------------------------------
    # 数据预处理
    # ---------------------------------------------------------
    df['system:time_start'] = pd.to_datetime(df['system:time_start'])
    df = df.sort_values('system:time_start').set_index('system:time_start')

    # 提取 Sprawl Core
    df_sprawl = df[['Sprawl_Zone_Core_mean', 'Sprawl_Zone_Core_std']].copy()
    df_sprawl.rename(columns={
        'Sprawl_Zone_Core_mean': 'LST_Sprawl',
        'Sprawl_Zone_Core_std': 'LST_Sprawl_Std'
    }, inplace=True)

    # 提取 Control Zone
    df_control = df[['Control_Zone_mean', 'Control_Zone_std']].copy()
    df_control.rename(columns={
        'Control_Zone_mean': 'LST_Control',
        'Control_Zone_std': 'LST_Control_Std'
    }, inplace=True)

    # 合并并重采样为每日序列
    df_daily_sprawl = df_sprawl.resample('D').mean().interpolate(method='time')
    df_daily_control = df_control.resample('D').mean().interpolate(method='time')
    df_daily = pd.concat([df_daily_sprawl, df_daily_control], axis=1).dropna()

    print(f"Raw data points: {len(df_sprawl.dropna())}")
    print(f"Interpolated daily points: {len(df_daily)}")

    # ---------------------------------------------------------
    # STL 时间序列分解 (Seasonal-Trend decomposition using LOESS)
    # period=365 对应年度季节周期
    # ---------------------------------------------------------
    stl_sprawl = STL(df_daily['LST_Sprawl'], period=365, robust=True).fit()
    stl_control = STL(df_daily['LST_Control'], period=365, robust=True).fit()

    sprawl_trend = stl_sprawl.trend
    control_trend = stl_control.trend

    # DiD: 去季节化后的纯趋势差分
    delta_trend = sprawl_trend - control_trend

    # ---------------------------------------------------------
    # Mann-Kendall 检验 (在去季节化的 DiD 趋势信号上)
    # ---------------------------------------------------------
    mk_result = mk.original_test(delta_trend.dropna())
    print(f"STL DiD MK test: trend={mk_result.trend}, p={mk_result.p:.6f}, "
          f"tau={mk_result.Tau:.4f}, slope={mk_result.slope:.6f}/day")

    # 净趋势变化
    net_trend_shift = sprawl_trend.iloc[-1] - sprawl_trend.iloc[0]
    net_control_shift = control_trend.iloc[-1] - control_trend.iloc[0]
    net_did = delta_trend.iloc[-1] - delta_trend.iloc[0]
    print(f"Sprawl trend shift: {net_trend_shift:+.2f} °C")
    print(f"Control trend shift: {net_control_shift:+.2f} °C")
    print(f"Net DiD trend shift: {net_did:+.2f} °C")

    # ---------------------------------------------------------
    # 空间方差 UQ (在趋势分量上叠加)
    # ---------------------------------------------------------
    std_smooth = df_daily['LST_Sprawl_Std'].rolling('180D', min_periods=30, center=True).mean().bfill().ffill()
    trend_upper = sprawl_trend + std_smooth
    trend_lower = sprawl_trend - std_smooth

    # ---------------------------------------------------------
    # 绘图
    # ---------------------------------------------------------
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 8), dpi=400)

    # 原始观测散点 (季节性振荡的全貌)
    raw_sprawl = df_sprawl.dropna()
    ax.scatter(raw_sprawl.index, raw_sprawl['LST_Sprawl'], color='#555555', alpha=0.2, s=8,
               label='Raw LST Observations (Seasonal)')

    # STL 提取的趋势分量
    ax.plot(sprawl_trend.index, sprawl_trend, color='#FF8C00', linewidth=3, alpha=0.95,
            label='Sprawl Deseasonalized Trend (STL)')

    # Control Zone 趋势分量
    ax.plot(control_trend.index, control_trend, color='#33CC33', linewidth=3, linestyle='-.',
            label='Control Deseasonalized Trend (STL)', alpha=0.8)

    # UQ 误差带
    ax.fill_between(sprawl_trend.index, trend_lower, trend_upper,
                    color='#FF8C00', alpha=0.15, label=r'Spatial Thermal Variance ($\pm 1\sigma$ UQ)', linewidth=0)

    # DiD 趋势差分 (缩放到可视范围，用右侧 y 轴)
    ax2 = ax.twinx()
    ax2.plot(delta_trend.index, delta_trend, color='#FF4444', linewidth=2, alpha=0.7,
             label=r'$\Delta$ Trend (Sprawl − Control)')
    ax2.set_ylabel(r'$\Delta$ LST Trend (°C)', fontsize=12, fontname='Courier New', color='#FF6666')
    ax2.tick_params(axis='y', colors='#FF6666', labelsize=11)
    ax2.spines['right'].set_color('#FF6666')

    # Mann-Kendall 结果标注
    sig = 'Significant' if mk_result.p < 0.05 else 'Not Significant'
    p_str = '< 1.000e-100' if mk_result.p == 0.0 else f'= {mk_result.p:.3e}'
    mk_label = r'STL DiD MK ($\Delta$ LST Trend): τ={:.3f}, p {} ({})'.format(mk_result.Tau, p_str, sig)
    ax.text(0.02, 0.02, mk_label, transform=ax.transAxes, fontsize=11,
            fontfamily='Courier New', color='#FFCC00',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#111111', edgecolor='#FFCC00', alpha=0.8))

    ax.set_title('Thermodynamic Spatial Audit: STL-Decomposed UHI Trend (2015-2026)',
                 fontsize=18, fontweight='bold', fontname='Courier New', color='white', pad=25)
    ax.set_ylabel('Land Surface Temperature (°C) — Trend Component', fontsize=14, fontname='Courier New', color='#CCCCCC')
    ax.set_xlabel('Temporal Axis (Years)', fontsize=14, fontname='Courier New', color='#CCCCCC')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.tick_params(axis='both', which='major', labelsize=12, colors='#AAAAAA')
    ax.grid(True, color='#333333', linestyle='--', linewidth=0.8, alpha=0.5)

    # 合并两个轴的图例
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2,
              loc='upper left', bbox_to_anchor=(1.12, 1), borderaxespad=0, frameon=False,
              prop={'family': 'Courier New', 'size': 10})

    # 数据源署名
    fig.text(0.98, 0.02, 'Data: USGS Landsat 8 (TIRS) | Decomposition: STL-LOESS | Author: H. Li',
             fontsize=9, color='#888888', ha='right', va='bottom', fontfamily='Helvetica')

    plt.tight_layout()
    plt.savefig(output_image_path, dpi=300, bbox_inches='tight', facecolor='#111111')
    print(f"SAVED: {output_image_path}")
    if os.environ.get('MPLBACKEND') != 'Agg':
        plt.show(block=False)


if __name__ == "__main__":
    input_csv = os.path.join(PROJECT_ROOT, 'data', 'raw_telemetry', 'ee-chart_lst.csv')
    output_png = os.path.join(PROJECT_ROOT, 'visualisations', 'thermodynamic_scar_chart.png')
    render_thermodynamic_chart(input_csv, output_png)