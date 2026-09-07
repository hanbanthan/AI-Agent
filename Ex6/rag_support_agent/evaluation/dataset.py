"""
evaluation/dataset.py — Evaluation dataset (Part 5 của Bài 6).

relevant_chunk_ids được resolve SAU KHI chunking đã chạy (chunk_id phụ
thuộc chunk_size/overlap) — build_eval_dataset() nhận `chunks` đã build
sẵn, tự tìm chunk thuộc đúng doc_id ground-truth.

Bộ test case này NHỎ, minh họa đủ category ở Part 5 — production cần
100-300 case, bạn tự mở rộng theo đúng schema TestCase.
"""
from src.models import Chunk, TestCase


def _chunk_ids_for_doc(chunks: list[Chunk], doc_id: str) -> list[str]:
    return [c.chunk_id for c in chunks if c.doc_id == doc_id]


def build_eval_dataset(chunks: list[Chunk]) -> list[TestCase]:
    cases = []

    cases.append(TestCase(
        query="Làm sao để đặt lại mật khẩu?",
        ground_truth_answer="Vào trang đăng nhập, chọn Quên mật khẩu, kiểm tra email chứa link reset (30 phút).",
        relevant_doc_ids=["faq_001"],
        relevant_chunk_ids=_chunk_ids_for_doc(chunks, "faq_001"),
        category="easy", difficulty="easy", language="vi", expected_source="faq",
    ))

    cases.append(TestCase(
        query="Tôi quên thông tin đăng nhập, phải làm gì để lấy lại quyền truy cập?",
        ground_truth_answer="Dùng chức năng Quên mật khẩu ở trang đăng nhập để nhận email reset.",
        relevant_doc_ids=["faq_001"],
        relevant_chunk_ids=_chunk_ids_for_doc(chunks, "faq_001"),
        category="semantic", difficulty="medium", language="vi", expected_source="faq",
    ))

    cases.append(TestCase(
        query="Error E-4021 là lỗi gì và cách fix?",
        ground_truth_answer="Lỗi kết nối tới máy chủ xác thực — đồng bộ thời gian hệ thống và mở firewall cổng 443.",
        relevant_doc_ids=["doc_e4021"],
        relevant_chunk_ids=_chunk_ids_for_doc(chunks, "doc_e4021"),
        category="keyword_heavy", difficulty="easy", language="vi", expected_source="doc",
    ))

    cases.append(TestCase(
        query="Tại sao tôi gặp E-4021 và bản vá mới nhất khắc phục thế nào?",
        ground_truth_answer="Dùng thông tin từ bản CẬP NHẬT (doc_e4021, updated 2025-06-15), không dùng bản cũ 2024.",
        relevant_doc_ids=["doc_e4021"],
        relevant_chunk_ids=_chunk_ids_for_doc(chunks, "doc_e4021"),
        category="outdated_document", difficulty="hard", language="vi", expected_source="doc",
    ))

    cases.append(TestCase(
        query="Server CPU 100% sau khi nâng cấp version 3.1, các nguyên nhân đã từng gặp là gì?",
        ground_truth_answer=(
            "Có 2 nguyên nhân đã ghi nhận: (1) background job đồng bộ lặp vô hạn do "
            "đổi API ở 3.1, fix bằng downgrade/patch 3.1.2; (2) cache_size quá nhỏ, "
            "fix bằng tăng cache_size lên tối thiểu 512MB."
        ),
        relevant_doc_ids=["ticket_8821", "ticket_9013"],
        relevant_chunk_ids=(
            _chunk_ids_for_doc(chunks, "ticket_8821") + _chunk_ids_for_doc(chunks, "ticket_9013")
        ),
        category="multi_hop", difficulty="hard", language="vi", expected_source="ticket",
    ))

    cases.append(TestCase(
        query="How can I reset my password?",
        ground_truth_answer="Click Forgot Password on the login page, check email for reset link (valid 30 min).",
        relevant_doc_ids=["faq_001_en"],
        relevant_chunk_ids=_chunk_ids_for_doc(chunks, "faq_001_en"),
        category="easy", difficulty="easy", language="en", expected_source="faq",
    ))

    cases.append(TestCase(
        query="Làm sao để tích hợp sản phẩm với hệ thống SAP ERP?",
        ground_truth_answer="(không có trong knowledge base — kỳ vọng hệ thống từ chối trả lời thay vì bịa)",
        relevant_doc_ids=[],
        relevant_chunk_ids=[],
        category="no_answer", difficulty="hard", language="vi", expected_source="none",
    ))

    return cases