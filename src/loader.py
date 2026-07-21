import pandas as pd
import os

def load_sales_data(filepath='data/sample_sales_data.csv'):
    # 1) 파일이 있는지 확인하고 없으면 에러
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {filepath}")
    
    df = pd.read_csv(filepath)
    return df
    # 2) pd.read_csv 로 불러와서 반환
    ...

def validate_columns(df):
    required = ['년월','거래처','매출액','환불액','수금액','미수금','입력일시','담당자']
    # required 중에 df.columns 에 없는 게 있으면 알려주기
    ...

def validate_missing_values(df):
    # df.isnull().sum() 으로 결측치 개수 세기
    ...


print(load_sales_data())