# -*- coding: utf-8 -*-
"""
07_plot_thermal_chart.py
GEE 导出的 LST CSV -> DiD Seasonal Mann-Kendall + Savitzky-Golay + UQ
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import warnings
import pymannkendall as mk
from scipy.signal import savgol_filter

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
    df_daily['Delta_LST'] = df_daily['LST_Sprawl'] - df_daily['LST_Control']

    print(f"Raw data points: {len(df_sprawl.dropna())}")
    print(f"Interpolated daily points: {len(df_daily)}")

    # ---------------------------------------------------------
    # Savitzky-Golay 滤波 (181天窗口 — 适配 Landsat 8 的 16 天重访周期)
    # Landsat 8 数据密度约为 Sentinel-2 的 1/3，365 天窗口过度平滑
    # ---------------------------------------------------------
    sg_window = 181  # 半年窗口：保留季节振幅，消除高频噪声
    df_daily['Sprawl_SG'] = savgol_filter(df_daily['LST_Sprawl'], window_length=sg_window, polyorder=3)
    df_daily['Control_SG'] = savgol_filter(df_daily['LST_Control'], window_length=sg_window, polyorder=3)
    df_daily['Delta_SG'] = savgol_filter(df_daily['Delta_LST'], window_length=sg_window, polyorder=3)

    # 平滑化空间方差包络带 (UQ)
    df_daily['Sprawl_Std_SG'] = df_daily['LST_Sprawl_Std'].rolling('180D', min_periods=30, center=True).mean().bfill().ffill()
    df_daily['Sprawl_Upper'] = df_daily['Sprawl_SG'] + df_daily['Sprawl_Std_SG']
    df_daily['Sprawl_Lower'] = df_daily['Sprawl_SG'] - df_daily['Sprawl_Std_SG']

    # ---------------------------------------------------------
    # DiD Seasonal Mann-Kendall 检验 (替代 linregress)
    # 对 Delta_SG 信号执行季节性 MK 检验，剥离区域气候趋势和年度周期
    # ---------------------------------------------------------
    mk_result = mk.seasonal_test(df_daily['Delta_SG'].dropna(), period=365)
    print(f"DiD Seasonal MK test: trend={mk_result.trend}, p={mk_result.p:.6f}, "
          f"tau={mk_result.Tau:.4f}, slope={mk_result.slope:.6f}/obs")

    # 净温差变化 (用 SG 平滑后的 Sprawl 首尾差)
    net_increase = df_daily['Sprawl_SG'].iloc[-1] - df_daily['Sprawl_SG'].iloc[0]
    print(f"Net SG temperature shift: {'+' if net_increase > 0 else ''}{net_increase:.2f} °C")

    # ---------------------------------------------------------
    # 绘图
    # ---------------------------------------------------------
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 8), dpi=400)

    # 原始散点
    raw_sprawl = df_sprawl.dropna()
    ax.scatter(raw_sprawl.index, raw_sprawl['LST_Sprawl'], color='#888888', alpha=0.4, s=15,
               label='Raw LST Observations (Cloud-masked)')

    # Sprawl SG 趋势线
    ax.plot(df_daily.index, df_daily['Sprawl_SG'], color='#FF8C00', linewidth=2.5, alpha=0.9,
            label=f'Sprawl Trend (SG w={sg_window}d)')

    # UQ 误差带
    ax.fill_between(df_daily.index, df_daily['Sprawl_Lower'], df_daily['Sprawl_Upper'],
                    color='#FF8C00', alpha=0.15, label=r'Spatial Thermal Variance ($\pm 1\sigma$ UQ)', linewidth=0)

    # Control Zone 对照线
    ax.plot(df_daily.index, df_daily['Control_SG'], color='#33CC33', linewidth=3, linestyle='-.',
            label='Control Zone Trend (Climate Baseline)', alpha=0.8)

    # Mann-Kendall 结果标注
    sig = 'Significant' if mk_result.p < 0.05 else 'Not Significant'
    p_str = '< 1.000e-100' if mk_result.p == 0.0 else f'= {mk_result.p:.3e}'
    mk_label = r'DiD Seasonal MK ($\Delta$ LST): τ={:.3f}, p {} ({})'.format(mk_result.Tau, p_str, sig)
    ax.text(0.02, 0.02, mk_label, transform=ax.transAxes, fontsize=11,
            fontfamily='Courier New', color='#FFCC00',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#111111', edgecolor='#FFCC00', alpha=0.8))

    ax.set_title('Thermodynamic Spatial Audit: Algorithmic Metabolism in the Sprawl Zone (2015-2026)',
                 fontsize=18, fontweight='bold', fontname='Courier New', color='white', pad=25)
    ax.set_ylabel('Land Surface Temperature (°C)', fontsize=14, fontname='Courier New', color='#CCCCCC')
    ax.set_xlabel('Temporal Axis (Years)', fontsize=14, fontname='Courier New', color='#CCCCCC')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.tick_params(axis='both', which='major', labelsize=12, colors='#AAAAAA')
    ax.grid(True, color='#333333', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0, frameon=False, prop={'family': 'Courier New', 'size': 11})

    # 数据源署名
    fig.text(0.98, 0.02, 'Data: USGS Landsat 8 (TIRS) | Projection: EPSG:27700 | Author: H. Li',
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