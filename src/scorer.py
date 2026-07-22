import pandas as pd
from loader import load_sales_data
import rules

# 규칙 이름과 실제 함수를 짝지어 둔 목록
RULE_FUNCS = {
    '기말 집중 매출': rules.detect_yearend_concentration,
    '환불률 비정상': rules.detect_high_refund_rate,
    '거래 집중도': rules.detect_transaction_concentration,
    '수금 지연': rules.detect_payment_delay,
    '거래액 변동성': rules.detect_amount_volatility,
    '매출액 급증': rules.detect_sudden_sales_increase,
}

# 규칙별 가중치 (위험한 규칙일수록 높은 점수)
RULE_WEIGHTS = {
    '기말 집중 매출': 3,
    '환불률 비정상': 3,
    '거래 집중도': 2,
    '수금 지연': 2,
    '거래액 변동성': 2,
    '매출액 급증': 1,
}


def collect_flags(df):
    """각 거래(년월·거래처)가 어떤 규칙에 걸렸는지 모은다."""
    records = []
    for name, func in RULE_FUNCS.items():   # 규칙 이름과 함수를 하나씩 꺼내서
        flagged = func(df)                  # 그 규칙을 실행하고
        for _, row in flagged.iterrows():   # 걸린 전표들을 한 줄씩 돌면서
            records.append({
                '년월': row['년월'],
                '거래처': row['거래처'],
                '탐지사유': name,           # 어떤 규칙에 걸렸는지 기록
            })
    return pd.DataFrame(records).drop_duplicates()

def score_vouchers(df):
    """거래별로 가중치를 합산해 위험 점수를 매긴다."""
    flags = collect_flags(df)

    # 각 탐지사유에 가중치 점수를 붙이기
    flags['가중치'] = flags['탐지사유'].map(RULE_WEIGHTS)

    # (년월, 거래처)로 묶어서 집계
    scored = flags.groupby(['년월', '거래처']).agg(
        위험점수=('가중치', 'sum'),                          # 가중치 합 = 위험점수
        걸린규칙수=('탐지사유', 'count'),                    # 걸린 규칙 개수
        탐지사유목록=('탐지사유', lambda s: ', '.join(s)),   # 걸린 규칙 이름들
    ).reset_index()

    # 위험 점수 높은 순으로 정렬
    scored = scored.sort_values('위험점수', ascending=False).reset_index(drop=True)
    return scored


if __name__ == "__main__":
    df = load_sales_data()
    scored = score_vouchers(df)
    print(f"위험 거래: {len(scored)}건")
    print(scored.head(15))