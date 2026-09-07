"""
models.py - Data model dùng chung cho toàn bộ pipeline
"""

from dataclasses import dataclass, field

@dataclass
class RawDoc:
    """1 tài liệu gốc trước khi chunk - support doc, FAQ, hoặc ticket"""
    doc_id: str
    text: str
    document_type: str  # doc|faq|ticket
    product: str
    version: str
    language: str
    category: str
    created_at: str
    updated_at: str
    customer_tier: str = "all"
    access_level: str = "public" #public|internal
    source: str = ""

@dataclass
class Chunk:
    """1 đơn vị tìm kiếm - sinh ra từ chunking 1 RawDoc"""
    chunk_id: str
    doc_id: str
    text: str
    metadata: dict = field(default_factory=dict)

@dataclass
class RetrievalResult:
    """Kết quả 1 làn retrieve - giữ score để debug/so sánh."""
    chunk: Chunk
    score: float
    method: str = "" # vector|bm25|hybrid|rerank

@dataclass
class TestCase:
    """1 case trong evaluation dataset (part 5)"""
    query: str
    ground_truth_answer: str
    relevant_doc_ids: list
    relevant_chunk_ids: list
    category: str
    difficulty: str
    language: str
    expected_source: str

    