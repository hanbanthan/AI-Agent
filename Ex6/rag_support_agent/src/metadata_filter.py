"""
metadata_filter.py - Lọc theo metadata trước khi tính similarity.

access control phải là PRE-filter (trước retrieval), không phải
post-filter - nếu lọc sau, nội dung nhạy cảm vẫn ảnh hưởng ranking dù
cuối cùng bị loại khỏi output.
"""
from .models import Chunk

def filter_chunks(
        chunks: list[Chunk],
        access_level: str | None = None,
        product: str | None = None,
        version: str | None = None,
) -> list[Chunk]:
    result = []
    for c in chunks:
        meta = c.metadata
        if access_level == "public" and meta.get("access_level") == "internal":
            continue
        if product is not None and meta.get("product") not in (product, "all"):
            continue
        if version is not None and meta.get("version") not in (version, "all"):
            continue
        result.append(c)
    return result

def drop_outdated_duplicates(chunks: list[Chunk]) -> list[Chunk]:
    """
    Giải quyết Conflicting/Outdated documents: Giữ bản có
    `updated_at` mới nhất trong (product, category, đoạn mở đầu).
    """
    best_by_key: dict[tuple, Chunk] = {}
    for c in chunks:
        key = (c.metadata.get("product"), c.metadata.get("category"), c.text[:40])
        current = best_by_key.get(key)
        if current is None or c.metadata.get("updated_at", 0) > current.metadata.get("updated_at", 0):
            best_by_key[key] = c
    return list(best_by_key.values())


