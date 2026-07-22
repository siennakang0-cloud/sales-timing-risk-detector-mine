import pandas as pd

def detect_high_refund_rate(df):
    df_copy = df.copy()                                   # 원본을 건드리지 않으려고 복사
    df_copy['refund_rate'] = df_copy['환불액'] / df_copy['매출액']   # 환불률 계산
    result = df_copy[df_copy['refund_rate'] > 0.15]       # 15% 넘는 행만 골라내기
    return result

def detect_transaction_concentration(df):
    df_copy = df.copy()

    monthly_total = df_copy.groupby('년월')['매출액'].sum()   # ① 월별 총 매출 구하기
    df_copy['month_total'] = df_copy['년월'].map(monthly_total) # ② 각 행에 그 달의 총액 붙이기
    df_copy['ratio'] = df_copy['매출액'] / df_copy['month_total']  # ③ 이 거래가 차지하는 비율

    result = df_copy[df_copy['ratio'] > 0.50]   # ④ 50% 넘는 행만
    return result

def detect_payment_delay(df):
    df_copy = df.copy()
    df_copy['unpaid_ratio'] = df_copy['미수금'] / df_copy['매출액']   # 미수금 비율

    result = df_copy[
        (df_copy['unpaid_ratio'] > 0.50) & (df_copy['미수금'] >= 20000000)
    ]
    return result

def detect_yearend_concentration(df):
    overall_avg = df['매출액'].mean()          # 전체 평균 매출

    df_copy = df.copy()
    # '년월'에서 '월' 숫자만 뽑기 (예: '2024-12' → 12)
    df_copy['month_num'] = df_copy['년월'].str.split('-').str[1].astype(int)

    is_period_end = df_copy['month_num'].isin([3, 6, 9, 12])   # 분기말/연말인가
    is_high_sales = df_copy['매출액'] > overall_avg * 3.0        # 평균의 3배 초과인가

    result = df_copy[is_period_end & is_high_sales].copy()
    result = result.drop('month_num', axis=1)
    return result


from loader import load_sales_data

df = load_sales_data()  

result = detect_yearend_concentration(df)
print(f"기말 집중 매출: {len(result)}건")
print(result[['년월', '거래처', '매출액']])