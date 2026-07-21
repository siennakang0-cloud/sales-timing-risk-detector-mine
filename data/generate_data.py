# -*- coding: utf-8 -*-
"""매출 데이터 생성 스크립트"""

import pandas as pd
import numpy as np
import random

np.random.seed(1)
random.seed(1)

months = [f'2024-{m:02d}' for m in range(1, 13)]
companies = [f'거래처{i:03d}' for i in range(1, 51)]
employees = ['김팀장', '이과장', '박대리', '최사원', '유실무']

records = []

# 1. 정상 거래
for month in months:
    for company in companies:
        if random.random() > 0.1:
            sales = np.random.randint(1_000_000, 5_000_000)
            refund = int(sales * np.random.uniform(0.01, 0.03))
            payment = sales - refund if random.random() > 0.15 else int(sales * 0.5)
            unpaid = sales - payment
            day = np.random.randint(1, 21)
            hour = np.random.randint(9, 18)
            minute = np.random.randint(0, 60)
            records.append({
                '년월': month, '거래처': company, '매출액': sales,
                '환불액': refund, '수금액': payment, '미수금': unpaid,
                '입력일시': f"{month}-{day:02d} {hour:02d}:{minute:02d}:00",
                '담당자': random.choice(employees), 'is_anomaly': False,
            })

# 2-1. 기말 집중 매출
for i in range(5):
    sales = np.random.randint(20_000_000, 30_000_000)
    refund = int(sales * 0.02); payment = int(sales * 0.3); unpaid = sales - payment
    records.append({'년월': '2024-12', '거래처': f'거래처{i+1:03d}', '매출액': sales,
        '환불액': refund, '수금액': payment, '미수금': unpaid,
        '입력일시': f"2024-12-{np.random.randint(20,31):02d} 14:30:00",
        '담당자': random.choice(employees), 'is_anomaly': True})

# 2-2. 환불률 비정상
for i in range(5):
    month = random.choice(months)
    sales = np.random.randint(2_000_000, 5_000_000)
    refund = int(sales * np.random.uniform(0.25, 0.40)); payment = sales - refund
    records.append({'년월': month, '거래처': f'거래처{i+6:03d}', '매출액': sales,
        '환불액': refund, '수금액': payment, '미수금': 0,
        '입력일시': f"{month}-{np.random.randint(1,21):02d} 10:15:00",
        '담당자': random.choice(employees), 'is_anomaly': True})

# 2-3. 거래 집중도
for i in range(5):
    month = months[i]
    month_total = sum(r['매출액'] for r in records if r['년월'] == month)
    sales = int(month_total * 0.75)
    refund = int(sales * 0.02); payment = sales - refund
    records.append({'년월': month, '거래처': f'거래처{i+11:03d}', '매출액': sales,
        '환불액': refund, '수금액': payment, '미수금': 0,
        '입력일시': f"{month}-{np.random.randint(1,21):02d} 11:00:00",
        '담당자': random.choice(employees), 'is_anomaly': True})

# 2-4. 수금 지연
for i in range(5):
    month = months[i % len(months)]
    sales = np.random.randint(30_000_000, 50_000_000)
    refund = int(sales * 0.02); payment = int(sales * 0.2); unpaid = sales - refund - payment
    records.append({'년월': month, '거래처': f'거래처{i+16:03d}', '매출액': sales,
        '환불액': refund, '수금액': payment, '미수금': unpaid,
        '입력일시': f"{month}-{np.random.randint(1,21):02d} 09:30:00",
        '담당자': random.choice(employees), 'is_anomaly': True})

# 2-5. 거래액 변동성
for i in range(5):
    month1, month2 = months[i], months[(i+1) % len(months)]
    sales1 = np.random.randint(300_000, 800_000)
    sales2 = np.random.randint(8_000_000, 12_000_000)
    for month, sales in [(month1, sales1), (month2, sales2)]:
        refund = int(sales * 0.02)
        records.append({'년월': month, '거래처': f'거래처{i+21:03d}', '매출액': sales,
            '환불액': refund, '수금액': sales - refund, '미수금': 0,
            '입력일시': f"{month}-{np.random.randint(1,21):02d} 13:45:00",
            '담당자': random.choice(employees), 'is_anomaly': True})

# 2-6. 매출액 급증
for i in range(5):
    month1, month2 = months[i], months[(i+1) % len(months)]
    sales1 = np.random.randint(1_000_000, 2_000_000)
    sales2 = sales1 * np.random.randint(4, 6)
    for month, sales in [(month1, sales1), (month2, sales2)]:
        refund = int(sales * 0.02); payment = int(sales * 0.7); unpaid = sales - refund - payment
        records.append({'년월': month, '거래처': f'거래처{i+26:03d}', '매출액': sales,
            '환불액': refund, '수금액': payment, '미수금': unpaid,
            '입력일시': f"{month}-{np.random.randint(1,21):02d} 16:00:00",
            '담당자': random.choice(employees), 'is_anomaly': True})

# 3. 저장
df = pd.DataFrame(records).sort_values(['년월', '거래처']).reset_index(drop=True)
df.to_csv('sample_sales_data.csv', index=False, encoding='utf-8-sig')

print(f"총 {len(df)}건 (정상 {len(df[df['is_anomaly']==False])} / 이상 {len(df[df['is_anomaly']==True])})")