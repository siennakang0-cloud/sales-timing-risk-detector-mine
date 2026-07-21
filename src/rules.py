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




from loader import load_sales_data

df = load_sales_data()  
result = detect_transaction_concentration(df)
print(f"거래 집중도 이상: {len(result)}건")
print(result[['년월', '거래처', '매출액']])