import math
import re
from collections import Counter

from agent_engineer.rag.document import Chunk, RetrievedChunk
from agent_engineer.rag.base import Retriever

def tokenize(text: str) -> list[str]:
    return re.findall(r'\w+', text.lower())

class BM25Retriever(Retriever):

    def __init__(
        self,
        chunks: list[Chunk],
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        self.chunks = chunks
        self.k1 = k1
        self.b = b

        self._tokenized = [
            tokenize(chunk.text)
            for chunk in chunks
        ]

        if self._tokenized:
            self._avgdl = (
                sum(
                    len(tokens)
                    for tokens in self._tokenized
                )
                / len(self._tokenized)
            )
        else:
            self._avgdl = 0.0

        self._document_frequencies = self._build_df()

    def _build_df(self) -> dict[str, int]:
        df: Counter[str] = Counter()

        for tokens in self._tokenized:
            for term in set(tokens):
                df[term] += 1

        return dict(df)

    def _score(
        self,
        query_tokens: list[str],
        document_tokens: list[str],
    ) -> float:

        if not document_tokens:
            return 0.0

        frequencies = Counter(document_tokens)

        score = 0.0
        number_documents = len(self.chunks)

        for term in query_tokens:
            frequency = frequencies.get(term, 0)

            if frequency == 0:
                continue

            document_frequency = self._document_frequencies.get(term, 0)

            idf = math.log(
                1 
                + (
                    number_documents - document_frequency + 0.5
                )
                / (document_frequency + 0.5)
            )

            document_length = len(document_tokens)

            denominator = (
                frequency
                + self.k1 * (
                    1 - self.b
                    + self.b * (document_length / self._avgdl)
                )
            )

            score += idf * (frequency * (self.k1 + 1)) / denominator

        return score

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:

        if top_k <= 0 or not self.chunks:
            return []

        query_tokens = tokenize(query)

        results = [
            RetrievedChunk(
                chunk=chunk,
                score=self._score(query_tokens, tokens),
            )
            for chunk, tokens in zip(self.chunks, self._tokenized)
        ]

        return sorted(results, key=lambda x: x.score, reverse=True)[:top_k]

