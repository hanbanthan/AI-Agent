"""
ingestion.py - đọc dữ liệu thô từ data/{faq, support_docs, tickets}/*.json,
chuẩn hóa thành RawDoc. (part 2: bước ingestion của offline pipeline).

Đây là nơi duy nhất trong toàn bộ codebase biết về cấu trúc thư mục dữ liệu
- mọi module khác chỉ làm việc với RawDoc/Chunk, không quan tâm dữ liệu
gốc nằm ở đâu hay format gì. Khi đổi nguồn dữ liệu thật (CMS, ticket
system API...), chỉ cần sửa file này.
"""

import json
from pathlib import Path
from src.models import RawDoc

def _load_json_dir(directory: Path, document_type: str) -> list[RawDoc]:
    docs = []
    for path in sorted(directory.glob("*.json")):
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        docs.append(RawDoc(
            doc_id=raw["doc_id"],
            text=raw["text"],
            document_type=document_type,
            product=raw.get("product", "all"),
            version=raw.get("version", "all"),
            language=raw.get("language", "vi"),
            category=raw.get("category", "general"),
            created_at=raw.get("created_at", ""),
            updated_at=raw.get("updated_at", ""),
            customer_tier=raw.get("customer_tier", "all"),
            access_level=raw.get("access_level", "public"),
            source=raw.get("source", document_type),
        ))
    return docs

def load_documents(faq_dir: Path, support_docs_dir: Path, tickets_dir: Path) -> list[RawDoc]:
    docs = []
    docs.extend(_load_json_dir(faq_dir, "faq"))
    docs.extend(_load_json_dir(support_docs_dir, "doc"))
    docs.extend(_load_json_dir(tickets_dir, "ticket"))
    return docs
