# Multi-Agent Systems with Google ADK and Vertex AI — Tickable Study Plan

Use this as the main progress tracker.

---

## Phase 1 — ADK Basics

- [x] **1. Learn what Google ADK is**
  - Study: https://adk.dev/get-started/
  - Goal: Understand Agent, model, instructions, tools, Runner, Session.

- [x] **2. Build one simple ADK agent**
  - Study: https://adk.dev/agents/
  - Build: One agent that answers questions.

- [x] **3. Learn tool calling**
  - Study: https://adk.dev/tools/
  - Study: https://adk.dev/tools-custom/
  - Build: Agent with 2 Python tools.

- [ ] **4. Learn Runner, Session, and Events**
  - Study: https://adk.dev/tutorials/agent-team/
  - Study: https://adk.dev/sessions/
  - Study: https://adk.dev/events/
  - Goal: Understand how an ADK agent actually executes.

---

## Phase 2 — Multi-Agent Fundamentals

- [ ] **5. Learn sub-agents**
  - Study: https://adk.dev/agents/
  - Build:
    ```text
    Coordinator
    ├── ProductAgent
    └── SupportAgent
    ```

- [ ] **6. Learn agent delegation**
  - Study: https://adk.dev/tutorials/agent-team/
  - Goal: Let the coordinator choose the correct specialist.

- [ ] **7. Learn how to design multi-agent architecture**
  - Learn:
    - agent responsibility,
    - input/output,
    - tools,
    - permissions,
    - state ownership.
  - Build an architecture diagram before coding.

---

## Phase 3 — Orchestration

- [ ] **8. Learn SequentialAgent**
  - Study: https://adk.dev/agents/workflow-agents/sequential-agents/
  - Build:
    ```text
    Retrieve -> Analyze -> Write
    ```

- [ ] **9. Learn ParallelAgent**
  - Study: https://adk.dev/agents/workflow-agents/parallel-agents/
  - Build:
    ```text
              ┌-> SearchAgent
    Question -+-> DatabaseAgent
              └-> DocumentAgent
    ```

- [ ] **10. Learn LoopAgent**
  - Study: https://adk.dev/agents/workflow-agents/loop-agents/
  - Build:
    ```text
    Generate -> Evaluate -> Improve -> Repeat
    ```

- [ ] **11. Build one workflow combining Parallel + Sequential**
  - Example:
    ```text
              ┌-> TechnicalResearch
    Question -+-> BusinessResearch
              └-> RiskResearch
                       |
                       v
                    Synthesis
    ```

---

## Phase 4 — Routing

- [ ] **12. Learn LLM-based routing**
  - Study: https://adk.dev/agents/routing/
  - Goal: Route natural-language requests to specialists.

- [ ] **13. Learn deterministic routing**
  - Study: https://adk.dev/agents/custom-agents/
  - Build Python rules such as:
    ```python
    if customer_type == "premium":
        ...
    ```

- [ ] **14. Learn when to use LLM routing vs Python rules**
  - Rule:
    ```text
    fuzzy language -> LLM
    strict business rule -> Python
    ```

---

## Phase 5 — State Management

- [ ] **15. Learn Sessions**
  - Study: https://adk.dev/sessions/
  - Goal: Understand multi-turn conversations.

- [ ] **16. Learn session.state**
  - Study: https://adk.dev/sessions/state/
  - Build:
    ```text
    Turn 1: Use account A123
    Turn 2: Show its balance
    ```

- [ ] **17. Learn ToolContext and execution context**
  - Study: https://adk.dev/context/
  - Goal: Read/update state from tools and agents.

- [ ] **18. Learn state ownership**
  - Decide which agent owns:
    - customer state,
    - transaction state,
    - workflow state,
    - retrieved data.

- [ ] **19. Build a stateful workflow**
  - Example:
    ```text
    NEW
     ↓
    VALIDATED
     ↓
    APPROVED
     ↓
    COMPLETED
    ```

---

## Phase 6 — Modern Workflow Graphs

- [ ] **20. Learn ADK graph workflows**
  - Study: https://adk.dev/workflows/
  - Goal: Understand nodes, edges, branches, conditions, and loops.

- [ ] **21. Convert one earlier workflow into a graph**

---

## Phase 7 — A2A

- [ ] **22. Learn what A2A is**
  - Study: https://adk.dev/a2a/
  - Study: https://adk.dev/a2a/intro/

- [ ] **23. Learn Agent Cards**
  - Goal: Understand how remote agents describe their capabilities.

- [ ] **24. Expose an agent using A2A**
  - Study: https://adk.dev/a2a/quickstart-exposing/

- [ ] **25. Consume a remote agent**
  - Study: https://adk.dev/a2a/quickstart-consuming/

- [ ] **26. Build two services**
  - Build:
    ```text
    Coordinator Service
            |
           A2A
            |
            v
       Risk Service
    ```

- [ ] **27. Add remote-agent error handling**
  - Handle timeout, unavailable service, invalid response.

---

## Phase 8 — MCP + Database

- [ ] **28. Learn what MCP is**
  - Study: https://adk.dev/tools-custom/mcp-tools/

- [ ] **29. Understand MCP vs A2A**
  - Remember:
    ```text
    MCP = Agent -> Tool / Service
    A2A = Agent -> Agent
    ```

- [ ] **30. Learn MCP Toolbox for Databases**
  - Study: https://googleapis.github.io/mcp-toolbox/

- [ ] **31. Connect ADK to MCP Toolbox**
  - Study: https://adk.dev/integrations/mcp-toolbox-for-databases/

- [ ] **32. Create a small MySQL database**
  - Tables: customers, accounts, transactions.

- [ ] **33. Create read-only database tools**
  - Example: get_customer, get_accounts, get_transactions.

- [ ] **34. Add controlled write tools**
  - Example: create_transaction_draft, update_transaction_status.

---

## Phase 9 — RAG

- [ ] **35. Learn basic RAG**
  - Study: https://cloud.google.com/vertex-ai/generative-ai/docs/rag-overview
  - Learn chunking, embeddings, vector search, top-k, metadata filters, grounding.

- [ ] **36. Learn grounding**
  - Study: https://adk.dev/grounding/

- [ ] **37. Learn Agent Search**
  - Study: https://adk.dev/integrations/agent-search/

- [ ] **38. Build a simple document RAG agent**
  - Build: Question -> Retrieve documents -> LLM -> Answer.

- [ ] **39. Combine SQL + RAG**
  - Build: Coordinator -> SQL Agent + Policy RAG Agent -> Synthesis.

- [ ] **40. Build multi-agent RAG**

---

## Phase 10 — Deployment

- [ ] **41. Learn Google Cloud authentication**
  - Study: https://cloud.google.com/docs/authentication/provide-credentials-adc

- [ ] **42. Learn Agent Runtime deployment**
  - Study: https://adk.dev/deploy/agent-runtime/

- [ ] **43. Learn Cloud Run deployment**
  - Study: https://adk.dev/deploy/cloud-run/

- [ ] **44. Deploy one agent service**

- [ ] **45. Deploy one remote A2A service**

---

## Phase 11 — Evaluation

- [ ] **46. Learn ADK evaluation**
  - Study: https://adk.dev/evaluate/

- [ ] **47. Learn evaluation criteria**
  - Study: https://adk.dev/evaluate/criteria/

- [ ] **48. Create routing tests**
- [ ] **49. Create tool-call tests**
- [ ] **50. Create state tests**
- [ ] **51. Create RAG tests**

---

## Phase 12 — Observability

- [ ] **52. Learn tracing**
  - Study: https://adk.dev/observability/traces/

- [ ] **53. Learn logging**
  - Study: https://adk.dev/observability/logging/

- [ ] **54. Trace one complete multi-agent request**

---

## Phase 13 — Security

- [ ] **55. Learn ADK safety basics**
  - Study: https://adk.dev/safety/

- [ ] **56. Learn tool authentication**
  - Study: https://adk.dev/tools-custom/authentication/

- [ ] **57. Learn action confirmation**
  - Study: https://adk.dev/tools-custom/confirmation/

- [ ] **58. Apply least privilege**
- [ ] **59. Validate all tool inputs**

---

# Final Project — Distributed Multi-Agent Banking Simulation

- [ ] **60. Create CoordinatorAgent**
- [ ] **61. Create AccountAgent**
- [ ] **62. Create TransferAgent**
- [ ] **63. Create RiskAgent**
- [ ] **64. Create PolicyRagAgent**
- [ ] **65. Add session state**
- [ ] **66. Add workflow-state transitions**
- [ ] **67. Add deterministic routing**
- [ ] **68. Add MySQL**
- [ ] **69. Add MCP Toolbox**
- [ ] **70. Add document RAG**
- [ ] **71. Move RiskAgent to separate A2A service**
- [ ] **72. Add Agent Card**
- [ ] **73. Add remote-agent failure handling**
- [ ] **74. Add evaluation dataset**
- [ ] **75. Add traces and logging**
- [ ] **76. Add security/permission boundaries**
- [ ] **77. Deploy**
- [ ] **78. Write README + architecture diagram**
- [ ] **79. Demo 3 complete scenarios**

---

# Recommended Order at a Glance

```text
[ ] ADK basics
     ↓
[ ] Tools
     ↓
[ ] Sub-agents
     ↓
[ ] Sequential / Parallel / Loop
     ↓
[ ] Routing
     ↓
[ ] State
     ↓
[ ] Graph workflows
     ↓
[ ] A2A
     ↓
[ ] MCP + MySQL
     ↓
[ ] RAG
     ↓
[ ] Deployment
     ↓
[ ] Evaluation
     ↓
[ ] Observability
     ↓
[ ] Security
     ↓
[ ] Final project
```

## Rule for ticking a box

Only tick an item when you can do both:

1. Explain the concept in your own words.
2. Build a small working example without copying the tutorial line by line.
