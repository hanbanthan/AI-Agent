
"""
context_builder.py - Context Construction
"""

from .models import RetrievalResult

def build_context(results: list[RetrievalResult], word_budget: int) -> str:
    parts = []
    used = 0
    for r in results:
        n_words = len(r.chunk.text.split())
        if used + n_words > word_budget:
            break

        tag = f"[Source: {r.chunk.doc_id} | updated_at={r.chunk.metadata.get('updated_at')}]"

        parts.append(f"{tag}\n{r.chunk.text}\n")
        used += n_words
    return "\n\n---\n\n".join(parts)

def detect_conflicts(results: list[RetrievalResult]) -> list[str]:
    seen: dict[str, set] = {}
    for r in results:
        cat = r.chunk.metadata.get("category")
        seen.setdefault(cat, set()).add(r.chunk.metadata.get("updated_at"))
    return any(len(times) > 1 for times in seen.values())