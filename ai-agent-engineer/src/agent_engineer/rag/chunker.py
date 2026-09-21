from agent_engineer.rag.document import Document, Chunk

class Chunker:
    def __init__(
        self,
        chunk_size: int = 100,
        overlap: int = 20,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0:
            raise ValueError("overlap must be non-negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be less than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, document: Document) -> list[Chunk]:
        words = document.text.split

        if not words:
            return []

        chunks: list[Chunk] = []

        start = 0
        index = 0

        while start < len(words):
            end = start + self.chunk_size

            chunk_text = " ".join(words[start:end])

            chunks.append(
                Chunk(
                    id=f"{document.id}:{index}",
                    document_id=document.id,
                    text=chunk_text,
                    metadata=dict(document.metadata),
                )
            )

            index += 1
            start += self.chunk_size - self.overlap
        
        return chunks