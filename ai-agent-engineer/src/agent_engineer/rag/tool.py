from typing import Any

from agent_engineer.rag.pipeline import RAGPipeline
from agent_engineer.tools.base import Tool
from agent_engineer.tools.types import (
    ToolSchema,
    ToolParameter,
)

class RAGTool(Tool):

    def __init__(
        self,
        pipeline: RAGPipeline,
    ) -> None:
        self.pipeline = pipeline

    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="search_documents",
            description="Search the knowledge base for relevant documents.",
            parameters=[
                ToolParameter(
                    name="query",
                    type=str,
                    description="The search query.",
                    required=True,
                ),
                ToolParameter(
                    name="top_k",
                    type=int,
                    description="The number of top results to retrieve.",
                    required=False,
                ),
            ],
        )

    def execute(
        self, 
        **kwargs: Any,
    ) -> Any:

        query = kwargs.get("query")
        top_k = kwargs.get("top_k", 5)

        results = self.pipeline.retrieve(
            query=query,
            top_k=top_k,
        )

        return [
            {
                "chunk_id": result.chunk.id,
                "document_id": result.chunk.document_id,
                "text": result.chunk.text,
                "score": result.score,  
            }
            for result in results
        ]
    