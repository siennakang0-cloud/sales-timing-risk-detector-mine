from loader import load_sales_data
from scorer import score_vouchers


def evaluate_detection(df, scored_df):
    """정답(심어둔 이상)과 탐지 결과를 비교해 성능을 계산한다."""
    # 정답: 심어둔 이상 거래
    answer = set(df[df['is_anomaly'] == True][['년월', '거래처']].apply(tuple, axis=1))
    # 탐지: 규칙이 찾은 거래
    detected = set(scored_df[['년월', '거래처']].apply(tuple, axis=1))

    tp = len(answer & detected)   # 정답이면서 탐지됨 (맞게 찾음)
    fp = len(detected - answer)   # 탐지됐지만 정답 아님 (오탐)
    fn = len(answer - detected)   # 정답인데 못 찾음 (미탐)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    return tp, fp, fn, precision, recall, f1


if __name__ == "__main__":
    df = load_sales_data()
    scored = score_vouchers(df)
    tp, fp, fn, precision, recall, f1 = evaluate_detection(df, scored)

    print("=" * 50)
    print("탐지 성능 평가")
    print("=" * 50)
    print(f"참양성(TP, 맞게 찾음) : {tp}건")
    print(f"거짓양성(FP, 오탐)   : {fp}건")
    print(f"거짓음성(FN, 미탐)   : {fn}건")
    print("-" * 50)
    print(f"정밀도(Precision) : {precision:.1%}")
    print(f"재현율(Recall)    : {recall:.1%}")
    print(f"F1-Score         : {f1:.3f}")
    print("=" * 50)