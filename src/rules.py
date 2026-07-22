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

def detect_amount_volatility(df):
    df_copy = df.copy()

    # 거래처별 매출의 평균과 표준편차 구하기
    company_stats = df_copy.groupby('거래처')['매출액'].agg(['mean', 'std']).fillna(0)
    company_stats.columns = ['company_mean', 'company_std']

    # 각 행에 그 거래처의 평균·표준편차를 붙이기
    df_copy = df_copy.join(company_stats, on='거래처')

    # 표준편차가 평균의 2배를 넘는 행만
    result = df_copy[df_copy['company_std'] > df_copy['company_mean'] * 2.0].copy()
    result = result.drop(['company_mean', 'company_std'], axis=1)
    return result


def detect_sudden_sales_increase(df):
    df_copy = df.copy()

    # 거래처·년월별 매출 합계 (시간순 정렬)
    monthly = df_copy.groupby(['거래처', '년월'])['매출액'].sum().reset_index()
    monthly = monthly.sort_values(['거래처', '년월'])

    # 거래처별로 '전월 매출'을 한 칸 밀어서 가져오기
    monthly['prev_sales'] = monthly.groupby('거래처')['매출액'].shift(1)

    # 전월 대비 증가율
    monthly['ratio'] = monthly['매출액'] / monthly['prev_sales']

    # 3배 초과 급증한 (거래처, 년월)만 추리기
    surged = monthly[monthly['ratio'] > 3.0][['거래처', '년월']]

    # 원본에서 해당 (거래처, 년월) 행만 골라내기
    result = df_copy.merge(surged, on=['거래처', '년월'], how='inner')
    return result



if __name__ == "__main__":
    from loader import load_sales_data

    df = load_sales_data()

    result = detect_yearend_concentration(df)
    print(f"기말 집중 매출: {len(result)}건")
    print(result[['년월', '거래처', '매출액']])

    result = detect_amount_volatility(df)
    print(f"거래액 변동성: {len(result)}건")
    print(result[['년월', '거래처', '매출액']])

    result = detect_sudden_sales_increase(df)
    print(f"매출액 급증: {len(result)}건")
    print(result[['년월', '거래처', '매출액']])