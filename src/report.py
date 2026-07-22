# -*- coding: utf-8 -*-
"""매출 위험 리포트 생성 (HTML 대시보드)"""

import pandas as pd
from loader import load_sales_data
from scorer import score_vouchers, collect_flags


def generate_html_report(df, scored_df, flags_df):
    # 거래별 매출액을 붙이기 (표시용)
    amt = df.groupby(['년월', '거래처'])['매출액'].sum().reset_index()
    scored = scored_df.merge(amt, on=['년월', '거래처'], how='left')

    # 규칙별 적중 횟수
    rule_counts = flags_df['탐지사유'].value_counts()
    rule_html = "".join([
        f"<tr><td>{rule}</td><td style='text-align:right;'>{int(count)}</td></tr>"
        for rule, count in rule_counts.items()
    ])

    # 위험 거래 목록
    rows = "".join([
        f"""
        <tr>
            <td>{row['년월']}</td>
            <td>{row['거래처']}</td>
            <td style="text-align:right; color:{'#dc3545' if row['위험점수'] >= 5 else '#ff9800' if row['위험점수'] >= 3 else '#28a745'}; font-weight:bold;">{int(row['위험점수'])}</td>
            <td style="text-align:right;">{int(row['걸린규칙수'])}</td>
            <td style="text-align:right;">{int(row['매출액']):,}</td>
            <td>{row['탐지사유목록']}</td>
        </tr>
        """
        for _, row in scored.iterrows()
    ])

    total_tx = df.groupby(['년월', '거래처']).ngroups
    risky = len(scored)
    max_score = int(scored['위험점수'].max()) if risky else 0

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>매출 인식 타이밍 위험 분석 리포트</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;
       background:linear-gradient(135deg,#667eea 0%,#764ba2 100%); padding:40px 20px; min-height:100vh; }}
.container {{ max-width:1200px; margin:0 auto; background:#fff; border-radius:12px;
       box-shadow:0 20px 60px rgba(0,0,0,0.3); overflow:hidden; }}
.header {{ background:linear-gradient(135deg,#667eea 0%,#764ba2 100%); color:#fff; padding:40px; text-align:center; }}
.header h1 {{ font-size:2.3em; margin-bottom:10px; }}
.header p {{ opacity:0.9; }}
.summary {{ display:grid; grid-template-columns:repeat(4,1fr); gap:20px; padding:30px; background:#f8f9fa; border-bottom:1px solid #e9ecef; }}
.card {{ text-align:center; padding:20px; background:#fff; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.1); }}
.card .num {{ font-size:2.2em; font-weight:bold; color:#667eea; margin-bottom:8px; }}
.card .label {{ font-size:0.9em; color:#6c757d; }}
.content {{ padding:40px; }}
.section {{ margin-bottom:45px; }}
.section h2 {{ font-size:1.6em; color:#333; margin-bottom:18px; padding-bottom:10px; border-bottom:3px solid #667eea; }}
table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:0.93em; }}
th {{ background:#667eea; color:#fff; padding:11px; text-align:left; }}
td {{ padding:11px; border-bottom:1px solid #e9ecef; }}
tr:hover {{ background:#f8f9fa; }}
.footer {{ background:#f8f9fa; padding:25px; text-align:center; color:#6c757d; font-size:0.88em; border-top:1px solid #e9ecef; }}
ul {{ margin-left:20px; line-height:2; color:#555; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>📊 매출 인식 타이밍 위험 분석 리포트</h1>
    <p>Sales Timing Risk Detector · ISA 540/330 기반 위험 기반 감사</p>
  </div>
  <div class="summary">
    <div class="card"><div class="num">{df['거래처'].nunique()}</div><div class="label">분석 거래처</div></div>
    <div class="card"><div class="num" style="color:#dc3545;">{risky}</div><div class="label">위험 거래</div></div>
    <div class="card"><div class="num">{max_score}</div><div class="label">최고 위험점수</div></div>
    <div class="card"><div class="num">{(100*risky/total_tx):.1f}%</div><div class="label">위험 거래 비율</div></div>
  </div>
  <div class="content">
    <div class="section">
      <h2>🎯 탐지 규칙 분포</h2>
      <table><thead><tr><th>탐지 규칙</th><th style="text-align:right;">적중 횟수</th></tr></thead>
      <tbody>{rule_html}</tbody></table>
    </div>
    <div class="section">
      <h2>⚠️ 위험 거래 목록 (위험도순)</h2>
      <table><thead><tr><th>년월</th><th>거래처</th><th>위험점수</th><th>규칙수</th><th>매출액</th><th>탐지 사유</th></tr></thead>
      <tbody>{rows if rows.strip() else '<tr><td colspan="6" style="text-align:center;color:#999;">위험 거래 없음</td></tr>'}</tbody></table>
    </div>
    <div class="section">
      <h2>📋 감사 방법론</h2>
      <p style="line-height:1.8; color:#555;">본 리포트는 <strong>ISA 540(회계추정)</strong>과 <strong>ISA 330(감사절차)</strong>에 기반한 위험 기반 감사를 자동화한 것입니다. 매출 인식 타이밍의 위험을 6개 지표로 식별합니다:</p>
      <ul>
        <li><strong>기말 집중 매출</strong> (가중치 3): 분기말·연말 비정상 매출 급증</li>
        <li><strong>환불률 비정상</strong> (가중치 3): 매출 대비 환불률 과도</li>
        <li><strong>거래 집중도</strong> (가중치 2): 월 매출의 50%↑ 단일 거래처 편중</li>
        <li><strong>수금 지연</strong> (가중치 2): 미수금 장기 미회수</li>
        <li><strong>거래액 변동성</strong> (가중치 2): 거래처별 매출 편차 극단적</li>
        <li><strong>매출액 급증</strong> (가중치 1): 전월 대비 300%↑ 증가</li>
      </ul>
    </div>
  </div>
  <div class="footer">
    <div>한정된 감사 자원을 위험 점수 높은 거래부터 우선 배분합니다. (규칙 기반 1차 스크리닝)</div>
    <div style="color:#999; margin-top:8px;">리포트 생성: {pd.Timestamp.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}</div>
  </div>
</div>
</body>
</html>"""
    return html


def main():
    df = load_sales_data()
    scored_df = score_vouchers(df)
    flags_df = collect_flags(df)
    html = generate_html_report(df, scored_df, flags_df)

    import os
    os.makedirs("reports", exist_ok=True)
    with open("reports/risk_report.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✓ 리포트 생성 완료: reports/risk_report.html")
    print(f"  - 거래처 {df['거래처'].nunique()}개 분석")
    print(f"  - 위험 거래 {len(scored_df)}건 탐지")


if __name__ == "__main__":
    main()
