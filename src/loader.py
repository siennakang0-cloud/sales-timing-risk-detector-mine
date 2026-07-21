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
    required = ['년월', '거래처', '매출액', '환불액', '수금액', '미수금', '입력일시', '담당자']

    missing = []                    # ① 없는 컬럼을 담을 빈 상자를 준비
    for col in required:            # ② 필요한 컬럼을 하나씩 꺼내서
        if col not in df.columns:   # ③ 실제 파일에 그게 없으면
            missing.append(col)     # ④ 빈 상자에 그 컬럼 이름을 넣는다

    if missing:                     # ⑤ 상자에 뭔가 담겼다면 (= 빠진 게 있다면)
        print(f"[ERROR] 없는 컬럼: {missing}")
        return False
    else:                           # ⑥ 상자가 여전히 비어 있다면 (= 다 있다면)
        print("[OK] 필요한 컬럼이 모두 있습니다.")
        return True
    

def validate_missing_values(df):
    # df.isnull().sum() 으로 결측치 개수 세기

    missing_count = df.isnull().sum()   # 컬럼별 빈칸 개수

    if missing_count.sum() > 0:         # 전체 빈칸 개수가 0보다 크면 (= 빈칸이 있으면)
        print("[ERROR] 결측치 발견:")
        print(missing_count[missing_count > 0])   # 빈칸이 있는 컬럼만 보여주기
        return False
    else:
        print("[OK] 결측치가 없습니다.")
        return True

def validate_balance(df):
    # 환불 + 수금 + 미수금을 더한 값
    expected = df['환불액'] + df['수금액'] + df['미수금']

    # 매출액과 다른 행이 있는지 확인 (1원 정도 오차는 허용)
    mismatches = df[abs(df['매출액'] - expected) > 1]

    if len(mismatches) > 0:
        print(f"[ERROR] 금액 불일치 {len(mismatches)}건 발견")
        return False
    else:
        print("[OK] 모든 거래의 금액이 일치합니다 (매출액 = 환불액 + 수금액 + 미수금)")
        return True


print(load_sales_data())

df = load_sales_data()
validate_columns(df)
validate_missing_values(df)
validate_balance(df)