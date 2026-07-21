import pandas as pd

def detect_high_refund_rate(df):
    df_copy = df.copy()                                   # 원본을 건드리지 않으려고 복사
    df_copy['refund_rate'] = df_copy['환불액'] / df_copy['매출액']   # 환불률 계산
    result = df_copy[df_copy['refund_rate'] > 0.15]       # 15% 넘는 행만 골라내기
    return result

from loader import load_sales_data

df = load_sales_data()
result = detect_high_refund_rate(df)
print(f"환불률 비정상 거래: {len(result)}건")
print(result[['년월', '거래처', '매출액', '환불액']])