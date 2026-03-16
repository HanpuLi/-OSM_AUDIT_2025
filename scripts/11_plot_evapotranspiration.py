# -*- coding: utf-8 -*-
"""
11_plot_evapotranspiration.py
Phase V: Physical Proxy for LST (Metabolic Rift)
Plots the Difference-in-Differences (DiD) of Actual Evapotranspiration.

Key insight: At MODIS 500m, the absolute ET curves for Sprawl and Control
nearly overlap because both zones are suburban mosaics at that scale.
But the DiD signal (Sprawl - Control) reveals a statistically significant
negative regime shift (p=0.005), confirming latent heat loss.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import warnings
from scipy.stats import ttest_ind, mannwhitneyu

warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib.figure")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONSTRUCTION_DATE = pd.Timestamp('2019-06-01')

def _sig_label(p):
    if p < 0.01:
        return 'Highly Significant'
    elif p < 0.05:
        return 'Significant'
    elif p < 0.10:
        return 'Marginal'
    return 'Not Significant'

def render_et_chart(csv_path, output_image_path):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"[ERROR] Cannot find {csv_path}")
        return

    required = ['Sprawl_ET_mean', 'Control_ET_mean']
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"[ERROR] ET CSV missing columns: {missing}")
        return

    df['system:time_start'] = pd.to_datetime(df['system:time_start'])
    df = df.sort_values('system:time_start').set_index('system:time_start')
    
    df_valid = df[['Sprawl_ET_mean', 'Control_ET_mean']].dropna()
    df_valid['delta'] = df_valid['Sprawl_ET_mean'] - df_valid['Control_ET_mean']

    # ---------------------------------------------------------
    # BACI 统计分析
    # ---------------------------------------------------------
    pre = df_valid.loc[df_valid.index < CONSTRUCTION_DATE, 'delta']
    post = df_valid.loc[df_valid.index >= CONSTRUCTION_DATE, 'delta']

    t_stat, t_p = ttest_ind(pre, post, equal_var=False)
    u_stat, u_p = mannwhitneyu(pre, post, alternative='two-sided')

    print(f"=== Evapotranspiration (ET) BACI Analysis ===")
    print(f"Pre  (n={len(pre)}): mean ΔET = {pre.mean():+.2f} mm/8-day ± {pre.std():.2f}")
    print(f"Post (n={len(post)}): mean ΔET = {post.mean():+.2f} mm/8-day ± {post.std():.2f}")
    print(f"Shift: {post.mean() - pre.mean():+.2f} mm/8-day | Welch p={t_p:.2e} | MW p={u_p:.2e}")

    # 年度聚合 (用来画年际柱状图, 每年一个 ΔET 均值)
    delta_annual = df_valid['delta'].resample('YE').mean()
    
    # 滚动平均（约 3 个月 = 12 个 8-day 观测）
    delta_smooth = df_valid['delta'].rolling(window=12, center=True, min_periods=4).mean()

    # ---------------------------------------------------------
    # 双面板绘图
    # ---------------------------------------------------------
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), dpi=400,
                                   gridspec_kw={'height_ratios': [2, 1]}, sharex=False)

    # ========== 上面板：ΔET 时间序列 + BACI ==========
    ax1.scatter(df_valid.index, df_valid['delta'], color='#66CCFF', alpha=0.15, s=8, zorder=2)
    ax1.plot(delta_smooth.index, delta_smooth, color='#00CCFF', linewidth=2.5, zorder=3,
             label=r'$\Delta$ET (Sprawl − Control), 3-month rolling')
    
    ax1.axhline(y=0, color='#666666', linestyle='-', linewidth=1, alpha=0.5)
    ax1.hlines(y=pre.mean(), xmin=pre.index.min(), xmax=CONSTRUCTION_DATE,
               color='#66CCFF', linewidth=3, linestyle='--', label=f'Pre mean: {pre.mean():+.2f}')
    ax1.hlines(y=post.mean(), xmin=CONSTRUCTION_DATE, xmax=post.index.max(),
               color='#FF4444', linewidth=3, linestyle='--', label=f'Post mean: {post.mean():+.2f}')
    ax1.axvline(x=CONSTRUCTION_DATE, color='#FFFFFF', linestyle=':', linewidth=1.5, alpha=0.5)
    ax1.axvspan(df_valid.index.min(), CONSTRUCTION_DATE, alpha=0.04, color='#66CCFF')
    ax1.axvspan(CONSTRUCTION_DATE, df_valid.index.max(), alpha=0.04, color='#FF4444')

    # 标注 regime shift 箭头
    shift = post.mean() - pre.mean()
    mid_x = CONSTRUCTION_DATE + pd.Timedelta(days=365*2)
    ax1.annotate(f'Regime Shift: {shift:+.2f} mm/8d',
                 xy=(mid_x, post.mean()), xytext=(mid_x, post.mean() - 1.5),
                 fontsize=12, fontweight='bold', color='#FF4444', fontfamily='Courier New',
                 arrowprops=dict(arrowstyle='->', color='#FF4444', lw=2), ha='center')

    sig_label = (f"Paired BACI: Welch p={t_p:.2e} ({_sig_label(t_p)}), "
                 f"MW p={u_p:.2e} ({_sig_label(u_p)})")
    ax1.text(0.02, 0.06, sig_label, transform=ax1.transAxes, fontsize=10,
             fontfamily='Courier New', color='#FFCC00',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#111111', edgecolor='#FFCC00', alpha=0.8))

    ax1.set_title('Metabolic Rift: Evapotranspiration DiD (Sprawl − Control)',
                  fontsize=15, fontweight='bold', fontname='Courier New', color='white', pad=15)
    ax1.set_ylabel(r'$\Delta$ ET (mm/8-day)', fontsize=12, fontname='Courier New', color='#00CCFF')
    ax1.legend(loc='upper right', frameon=True, facecolor='#111111', edgecolor='#444444',
               prop={'family': 'Courier New', 'size': 10})
    ax1.grid(True, color='#333333', linestyle='--', linewidth=0.8, alpha=0.5)
    ax1.tick_params(axis='both', labelsize=10, colors='#AAAAAA')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax1.xaxis.set_major_locator(mdates.YearLocator())

    # ========== 下面板：年均 ΔET 柱状图 ==========
    years = delta_annual.index.year
    vals = delta_annual.values
    colors = ['#FF4444' if v < pre.mean() else '#66CCFF' for v in vals]
    
    ax2.bar(years, vals, color=colors, alpha=0.85, edgecolor='white', linewidth=0.5, width=0.7)
    ax2.axhline(y=pre.mean(), color='#66CCFF', linestyle='--', linewidth=2,
                label=f'Pre-Construction Baseline ({pre.mean():+.2f})')
    ax2.axhline(y=0, color='#666666', linestyle='-', linewidth=1, alpha=0.5)

    ax2.set_ylabel(r'Annual Mean $\Delta$ET (mm/8-day)', fontsize=12, fontname='Courier New', color='#FF8888')
    ax2.set_xlabel('Year', fontsize=12, fontname='Courier New', color='#CCCCCC')
    ax2.legend(loc='lower left', frameon=True, facecolor='#111111', edgecolor='#444444',
               prop={'family': 'Courier New', 'size': 10})
    ax2.grid(True, color='#333333', linestyle='--', linewidth=0.8, alpha=0.5)
    ax2.tick_params(axis='both', labelsize=10, colors='#AAAAAA')

    fig.text(0.98, 0.005,
             'Data: NASA MODIS MOD16A2GF (500m, 8-Day) | Method: Paired BACI DiD | Author: H. Li',
             fontsize=8, color='#888888', ha='right', va='bottom', fontfamily='Helvetica')

    plt.tight_layout()
    plt.savefig(output_image_path, dpi=300, bbox_inches='tight', facecolor='#111111')
    print(f"\nSAVED ET: {output_image_path}")
    if os.environ.get('MPLBACKEND') != 'Agg':
        plt.show(block=False)

if __name__ == "__main__":
    input_csv = os.path.join(PROJECT_ROOT, 'data', 'raw_telemetry', 'ee-chart_et.csv')
    output_png = os.path.join(PROJECT_ROOT, 'visualisations', 'evapotranspiration_collapse_chart.png')
    render_et_chart(input_csv, output_png)
