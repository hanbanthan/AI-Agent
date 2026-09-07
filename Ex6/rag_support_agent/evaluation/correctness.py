"""
evaluation/correctness.py - Answer Correctness + Faithfulness (Part 7)

STAND-IN quan trọng: đánh giá đúng ngữ nghĩa và có bám sát context không chính xác 
thường cần LLM-as-judge (Chủ đề bài 12 - level 8 trong curriculum, chưa tới lượt). 
Ở đây dùng 2 heuristic đơn giản (word overlap) làm placeholder để pipeline có con số 
chạy được ngay - KHÔNG đủ tin cậy cho production, chỉ để bạn thấy hình dạng của 2 metric này 
trước khi học LLM-as-judge.
"""

import re
from statistics import mean 

def _normalize(text: str) -> set:
    return set(re.findall(r"[\wÀ-ỹ]+", text.lower()))

def answer_correctness(predicted: str, ground_truth: str) -> float:
    """Heuristic: tỷ lệ từ trong ground-truth cũng xuất hiện trong predicted.
    Thay thế bằng LLM-as-judge khi có (so sánh ngữ nghĩa, không chỉ từ khóa)."""
    gt_words = _normalize(ground_truth)
    pred_words = _normalize(predicted)
    if not gt_words:
        return 0.0
    overlap = len(gt_words & pred_words)
    return overlap / len(gt_words)

def faithfulness(predicted: str, context: str) -> float:
    """
    Heuristic: tỷ lệ từ 'nội dung' trong answer cũng xuất hiện trong
    context - proxy thô cho việc answer có 'bịa' thông tin ngoài context hay không. 
    THAY THẾ bằng LLM-as-judge fact-check từng claim khi có
    """
    answer_words = _normalize(predicted)
    context_words = _normalize(context)
    if not answer_words:
        return 0.0
    grounded = len(answer_words & context_words)
    return grounded / len(answer_words)

def evaluate_generation(cases_with_answers: list[dict]) -> dict:
    """cases with answers: list of {"predicted": str, "ground_truth": str, "context": str}"""
    correctness_scores = [answer_correctness(c["predicted"], c["ground_truth"]) for c in cases_with_answers]
    faithfulness_scores = [faithfulness(c["predicted"], c["context"]) for c in cases_with_answers]
    return {
        "answer_correctness": round(mean(correctness_scores), 3) if correctness_scores else 0.0,
        "faithfulness": round(mean(faithfulness_scores), 3) if faithfulness_scores else 0.0,
        "n_cases": len(cases_with_answers),
    }

