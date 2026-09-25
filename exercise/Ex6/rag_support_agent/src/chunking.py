"""
chunking.py - Cắt RawDoc thành các chunk

chunk_size/overlap_ratio đọc default từ config.py - truyền tham số khác vào để chạy experiment 
VD: so sánh Recall@K giữa các chunk_size
"""
from src.models import RawDoc, Chunk

def chunk_document(doc: RawDoc, chunk_size: int, overlap_ratio: float) -> list[Chunk]:
    words = doc.text.split()
    if not words:
        return []

    step = max(1, int(chunk_size * (1 - overlap_ratio)))
    chunks: list[Chunk] = []
    idx = 0
    start = 0
    while start < len(words):
        piece = words[start:start + chunk_size]
        if not piece:
            break
        chunk_text = " ".join(piece)
        chunk_id = f"{doc.doc_id}::chunk{idx}"
        metadata = {
            "doc_id": doc.doc_id,
            "document_type": doc.document_type,
            "product": doc.product,
            "version": doc.version,
            "language": doc.language,
            "category": doc.category,
            "created_at": doc.created_at,
            "updated_at": doc.updated_at,
            "customer_tier": doc.customer_tier,
            "access_level": doc.access_level,
            "source": doc.source,
        }
        chunks.append(Chunk(chunk_id=chunk_id, doc_id=doc.doc_id, text=chunk_text, metadata=metadata))
        idx += 1
        if start + chunk_size >= len(words):
            break
        start += step

    return chunks

def chunk_documents(docs: list[RawDoc], chunk_size: int, overlap_ratio: float) -> list[Chunk]:
    all_chunks: list[Chunk] = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc, chunk_size, overlap_ratio))
    return all_chunks
