from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
FAQ_DIR = DATA_DIR / "faq"
SUPPORT_DOCS_DIR = DATA_DIR / "support_docs"
TICKETS_DIR = DATA_DIR / "tickets"

CHUNK_SIZE = 60
CHUNK_OVERLAP_RATIO = 0.15

RETRIEVAL_TOP_K = 25
RRF_K = 60

RERANK_TOP_N = 5

CONTEXT_WORD_BUDGET = 300

DEFAULT_METHOD = "hybrid_rerank"
DEFAULT_ACCESS_LEVEL = "public"
