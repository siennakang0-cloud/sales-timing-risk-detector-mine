# -*- coding: utf-8 -*-
"""매출 위험 차트 생성 (PNG) — 리포트와 같은 데이터 사용"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

from loader import load_sales_data
from scorer import score_vouchers, collect_flags

_FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if os.path.exists(_FONT):
    font_manager.fontManager.addfont(_FONT)
    plt.rcParams["font.family"] = font_manager.FontProperties(fname=_FONT).get_name()
plt.rcParams["axes.unicode_minus"] = False

COLOR_NORMAL = "#5b6b80"
COLOR_FLAG = "#c0392b"


def make_normal_vs_flagged_chart(df, scored_df, path):
    total = df.groupby(['년월', '거래처']).ngroups
    flagged = len(scored_df)
    normal = total - flagged

    fig, ax = plt.subplots(figsize=(7, 6))
    bars = ax.bar(['정상', '위험'], [normal, flagged], color=[COLOR_NORMAL, COLOR_FLAG], width=0.6)
    for bar, v in zip(bars, [normal, flagged]):
        ax.text(bar.get_x() + bar.get_width() / 2, v, f"{v}\n({100*v/total:.1f}%)",
                ha="center", va="bottom", fontsize=12)
    ax.set_title("정상 vs 위험 거래", fontsize=16, fontweight="bold")
    ax.set_ylabel("거래 수 (거래처×월)", fontsize=12)
    ax.set_ylim(0, total * 1.15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def make_rule_chart(flags_df, path):
    counts = flags_df["탐지사유"].value_counts()
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(counts.index, counts.values, color=COLOR_FLAG, width=0.6)
    for bar, v in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, v, str(v), ha="center", va="bottom", fontsize=11)
    ax.set_title("탐지 규칙별 위험 거래 건수", fontsize=16, fontweight="bold")
    ax.set_ylabel("위험 거래 수", fontsize=12)
    ax.set_ylim(0, max(counts.values) * 1.15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def main():
    df = load_sales_data()
    scored_df = score_vouchers(df)
    flags_df = collect_flags(df)

    os.makedirs("reports", exist_ok=True)
    make_normal_vs_flagged_chart(df, scored_df, "reports/chart_normal_vs_flagged.png")
    make_rule_chart(flags_df, "reports/chart_by_rule.png")
    print("✓ 차트 생성 완료: reports/chart_normal_vs_flagged.png, reports/chart_by_rule.png")


if __name__ == "__main__":
    main()
