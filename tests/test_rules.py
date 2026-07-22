# -*- coding: utf-8 -*-
"""
매출 이상탐지 규칙 단위테스트
==============================

각 규칙이 의도대로 동작하는지 unittest로 검증한다.

실행:
  python3 tests/test_rules.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import pandas as pd
import rules


def make_df(rows):
    return pd.DataFrame(rows, columns=[
        '년월', '거래처', '매출액', '환불액', '수금액', '미수금', '입력일시', '담당자',
    ])


class TestSalesRules(unittest.TestCase):

    def test_high_refund_detected(self):
        """환불률 비정상: 환불률 15% 초과 탐지"""
        df = make_df([
            ['2024-01', '거래처001', 1_000_000, 200_000, 800_000, 0, '2024-01-10 10:00:00', 'A'],
        ])
        self.assertEqual(len(rules.detect_high_refund_rate(df)), 1)

    def test_high_refund_normal(self):
        """환불률 비정상: 정상 환불률(2%)은 탐지 안 됨"""
        df = make_df([
            ['2024-01', '거래처001', 1_000_000, 20_000, 980_000, 0, '2024-01-10 10:00:00', 'A'],
        ])
        self.assertEqual(len(rules.detect_high_refund_rate(df)), 0)

    def test_concentration_detected(self):
        """거래 집중도: 월 매출의 50% 초과 단일 거래처 탐지"""
        df = make_df([
            ['2024-01', '거래처001', 6_000_000, 0, 6_000_000, 0, '2024-01-10 10:00:00', 'A'],
            ['2024-01', '거래처002', 2_000_000, 0, 2_000_000, 0, '2024-01-11 10:00:00', 'B'],
            ['2024-01', '거래처003', 2_000_000, 0, 2_000_000, 0, '2024-01-12 10:00:00', 'C'],
        ])
        result = rules.detect_transaction_concentration(df)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['거래처'], '거래처001')

    def test_concentration_normal(self):
        """거래 집중도: 분산된 거래는 탐지 안 됨"""
        df = make_df([
            ['2024-01', '거래처001', 3_000_000, 0, 3_000_000, 0, '2024-01-10 10:00:00', 'A'],
            ['2024-01', '거래처002', 3_000_000, 0, 3_000_000, 0, '2024-01-11 10:00:00', 'B'],
            ['2024-01', '거래처003', 4_000_000, 0, 4_000_000, 0, '2024-01-12 10:00:00', 'C'],
        ])
        self.assertEqual(len(rules.detect_transaction_concentration(df)), 0)

    def test_payment_delay_detected(self):
        """수금 지연: 미수금 비율 50%↑ 이면서 2천만원↑ 탐지"""
        df = make_df([
            ['2024-01', '거래처001', 50_000_000, 1_000_000, 19_000_000, 30_000_000, '2024-01-10 09:00:00', 'A'],
        ])
        self.assertEqual(len(rules.detect_payment_delay(df)), 1)

    def test_payment_delay_normal(self):
        """수금 지연: 정상 수금은 탐지 안 됨"""
        df = make_df([
            ['2024-01', '거래처001', 10_000_000, 200_000, 8_800_000, 1_000_000, '2024-01-10 09:00:00', 'A'],
        ])
        self.assertEqual(len(rules.detect_payment_delay(df)), 0)

    def test_yearend_detected(self):
        """기말 집중 매출: 분기말/연말에 평균의 3배 초과 탐지"""
        rows = [[f'2024-{m:02d}', '거래처001', 1_000_000, 20_000, 980_000, 0, f'2024-{m:02d}-10 10:00:00', 'A']
                for m in range(1, 12)]
        rows.append(['2024-12', '거래처002', 10_000_000, 200_000, 9_800_000, 0, '2024-12-20 14:00:00', 'B'])
        df = make_df(rows)
        result = rules.detect_yearend_concentration(df)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['년월'], '2024-12')

    def test_yearend_normal(self):
        """기말 집중 매출: 평범한 월말 거래는 탐지 안 됨"""
        df = make_df([
            ['2024-01', '거래처001', 1_000_000, 20_000, 980_000, 0, '2024-01-10 10:00:00', 'A'],
            ['2024-12', '거래처002', 1_200_000, 24_000, 1_176_000, 0, '2024-12-20 10:00:00', 'B'],
        ])
        self.assertEqual(len(rules.detect_yearend_concentration(df)), 0)

    def test_volatility_detected(self):
        """거래액 변동성: 극단적으로 들쭉날쭉한 거래처 탐지"""
        df = make_df([
            ['2024-01', '거래처001', 1_000_000, 0, 1_000_000, 0, '2024-01-10 10:00:00', 'A'],
            ['2024-02', '거래처001', 1_000_000, 0, 1_000_000, 0, '2024-02-10 10:00:00', 'A'],
            ['2024-03', '거래처001', 1_000_000, 0, 1_000_000, 0, '2024-03-10 10:00:00', 'A'],
            ['2024-04', '거래처001', 1_000_000, 0, 1_000_000, 0, '2024-04-10 10:00:00', 'A'],
            ['2024-05', '거래처001', 100_000_000, 0, 100_000_000, 0, '2024-05-10 10:00:00', 'A'],
        ])
        self.assertTrue(len(rules.detect_amount_volatility(df)) > 0)

    def test_volatility_normal(self):
        """거래액 변동성: 안정적인 거래처는 탐지 안 됨"""
        df = make_df([
            ['2024-01', '거래처001', 1_000_000, 0, 1_000_000, 0, '2024-01-10 10:00:00', 'A'],
            ['2024-02', '거래처001', 1_100_000, 0, 1_100_000, 0, '2024-02-10 10:00:00', 'A'],
            ['2024-03', '거래처001', 950_000, 0, 950_000, 0, '2024-03-10 10:00:00', 'A'],
        ])
        self.assertEqual(len(rules.detect_amount_volatility(df)), 0)

    def test_sudden_increase_detected(self):
        """매출액 급증: 전월 대비 300% 초과 탐지"""
        df = make_df([
            ['2024-01', '거래처001', 1_000_000, 0, 1_000_000, 0, '2024-01-10 10:00:00', 'A'],
            ['2024-02', '거래처001', 4_000_000, 0, 4_000_000, 0, '2024-02-10 10:00:00', 'A'],
        ])
        result = rules.detect_sudden_sales_increase(df)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['년월'], '2024-02')

    def test_sudden_increase_normal(self):
        """매출액 급증: 완만한 성장은 탐지 안 됨"""
        df = make_df([
            ['2024-01', '거래처001', 1_000_000, 0, 1_000_000, 0, '2024-01-10 10:00:00', 'A'],
            ['2024-02', '거래처001', 1_500_000, 0, 1_500_000, 0, '2024-02-10 10:00:00', 'A'],
        ])
        self.assertEqual(len(rules.detect_sudden_sales_increase(df)), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
