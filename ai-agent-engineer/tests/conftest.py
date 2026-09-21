from typing import Any

import pytest

from agent_engineer.rag.base import Retriever
from agent_engineer.rag.document import Chunk, RetrievedChunk
from agent_engineer.rag.pipeline import RAGPipeline
from agent_engineer.tools.base import Tool
from agent_engineer.tools.types import ToolParameter, ToolSchema


class SearchTool(Tool):

    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="search",
            description="Search for information.",
            parameters=[
                ToolParameter(
                    name="query",
                    type=str,
                    description="Search query.",
                    required=True,
                )
            ],
        )

    def execute(self, **kwargs: Any) -> Any:
        query = kwargs["query"]

        return [
            f"Result for: {query}"
        ]

@pytest.fixture
def search_tool() -> Tool:
    return SearchTool()


class FixtureRetriever(Retriever):
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        chunks = [
            RetrievedChunk(
                chunk=Chunk(
                    id="rag-1",
                    document_id="doc-1",
                    text="AI agents use tools to interact with systems.",
                ),
                score=1.0,
            ),
        ]
        return chunks[:top_k]


@pytest.fixture
def rag_pipeline() -> RAGPipeline:
    return RAGPipeline(retriever=FixtureRetriever())

