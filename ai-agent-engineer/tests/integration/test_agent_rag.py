from agent_engineer.agent import Agent
from agent_engineer.llm import (
    LLMResponse,
    MockLLM,
)
from agent_engineer.rag import RAGPipeline
from agent_engineer.rag.tool import RAGTool
from agent_engineer.tools import (
    ToolCall,
    ToolExecutor,
    ToolRegistry,
)


def test_agent_can_use_rag_tool(
    rag_pipeline,
) -> None:

    rag_tool = RAGTool(rag_pipeline)

    registry = ToolRegistry()
    registry.register(rag_tool)

    executor = ToolExecutor(registry)

    llm = MockLLM(
        responses=[
            LLMResponse(
                content=None,
                model="mock-model",
                tool_calls=[
                    ToolCall(
                        id="call-1",
                        name="search_documents",
                        arguments={
                            "query": "AI agents",
                            "top_k": 2,
                        },
                    )
                ],
            ),
            LLMResponse(
                content=(
                    "AI agents can use tools "
                    "to interact with systems."
                ),
                model="mock-model",
            ),
        ]
    )

    agent = Agent(
        llm=llm,
        tool_executor=executor,
    )

    result = agent.run(
        "How do AI agents use tools?"
    )

    assert (
        result.answer
        == "AI agents can use tools to interact with systems."
    )

    assert len(llm.requests) == 2