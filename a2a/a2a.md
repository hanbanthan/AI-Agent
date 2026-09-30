# Multi-Agent Systems with Google ADK and Vertex AI — Study Guide

> **Goal:** Learn the concepts behind the course, not just copy the course code.
>
> This guide follows the 15-course-module structure and adds:
> - concepts you should understand,
> - Google ADK APIs/classes to recognize,
> - small exercises,
> - official learning resources,
> - a final distributed multi-agent banking-system project.
>
> **Last reviewed:** 2026-09-29

---

# 0. What you should know before starting

You do **not** need to be an expert in distributed systems, but these topics will make the course much easier.

## Python fundamentals

Be comfortable with:

- functions and classes,
- dictionaries and lists,
- type hints,
- `async` / `await`,
- exceptions,
- modules and packages,
- HTTP APIs,
- JSON.

Useful review:

- Python tutorial: https://docs.python.org/3/tutorial/
- `asyncio`: https://docs.python.org/3/library/asyncio.html

## API fundamentals

Understand:

```text
Client -> HTTP request -> Server -> response
```

Know the meaning of:

- `GET`
- `POST`
- JSON request/response
- status codes
- REST endpoints
- authentication tokens

## Database fundamentals

Know:

- tables,
- rows,
- primary keys,
- foreign keys,
- `SELECT`,
- `INSERT`,
- `UPDATE`,
- transactions.

For the final project, SQL matters because multiple agents may share structured state through a database.

## LLM-agent fundamentals

Before multi-agent systems, understand the basic single-agent loop:

```text
User
  |
  v
Agent
  |
  +--> LLM decides what to do
  |
  +--> Tool call
  |
  +--> Tool result
  |
  +--> LLM reasons again
  |
  v
Final answer
```

Important distinction:

```text
LLM = language/reasoning model
Agent = LLM + instructions + tools + state + control loop
Multi-agent system = several agents that coordinate
```

---

# 1. Introduction to Multi-Agent Systems with ADK

## Main idea

A multi-agent system decomposes a large task into several agents with narrower responsibilities.

Instead of:

```text
One giant agent
    |
    +--> everything
```

you might have:

```text
                  +--> Search Agent
User -> Coordinator
                  +--> Database Agent
                  +--> Analysis Agent
                  +--> Report Agent
```

Each specialist should have:

- a clear responsibility,
- a limited set of tools,
- an input contract,
- an output contract.

## Why use multiple agents?

Useful reasons include:

1. **Separation of concerns**  
   One agent does not need every tool and every instruction.

2. **Specialization**  
   Each agent can receive instructions optimized for its task.

3. **Parallel execution**  
   Independent tasks can run concurrently.

4. **Security boundaries**  
   A read-only database agent can be separated from an agent allowed to write data.

5. **Maintainability**  
   Individual agents can be changed or deployed separately.

6. **Distributed architecture**  
   Remote agents can run as independent services.

## When NOT to use multi-agent architecture

Do not split an application merely because multi-agent sounds advanced.

A single agent is often better when:

- there are only 2-3 simple tools,
- tasks strongly depend on the same context,
- latency is important,
- agent boundaries are artificial,
- coordination complexity is greater than the original problem.

A useful rule:

> Add an agent when it represents a meaningful responsibility boundary, not just another prompt.

## ADK concepts to learn

Start with:

- `Agent` / `LlmAgent`
- tools
- sub-agents
- Runner / runtime
- events
- sessions
- state

## Mini exercise

Build one simple assistant with two tools:

```text
calculator
weather_lookup
```

Do this as **one agent first**.

Only after that works, split the responsibilities into separate agents.

## Official material

- ADK documentation index: https://adk.dev/llms.txt
- ADK Get Started: https://adk.dev/get-started/
- ADK Agents: https://adk.dev/agents/
- ADK agent-team tutorial: https://adk.dev/tutorials/agent-team/

---

# 2. Designing Multi-Agent Architecture

Before coding, design the system.

## Core architectural questions

For every agent, answer:

```text
1. What is this agent responsible for?
2. What input does it receive?
3. What output must it produce?
4. What tools may it call?
5. What state may it read?
6. What state may it modify?
7. Which other agents may it call?
8. What happens when it fails?
```

## Agent responsibility table

Example:

| Agent | Responsibility | Tools | Output |
|---|---|---|---|
| Coordinator | Understand request and delegate | sub-agents | final response |
| AccountAgent | Retrieve account data | SQL read tools | account info |
| TransactionAgent | Work with transactions | SQL transaction tools | transaction result |
| FraudAgent | Evaluate suspicious patterns | rules/model | risk result |
| SupportAgent | Explain results to user | knowledge search | explanation |

## Important principle: narrow capabilities

Bad:

```text
bank_agent:
- database admin
- customer service
- transfers
- analytics
- fraud detection
- document retrieval
```

Better:

```text
account_agent
transaction_agent
fraud_agent
knowledge_agent
coordinator
```

## Architecture quality questions

Ask:

- Can each component be tested independently?
- Can one agent fail without breaking everything?
- Is shared state explicit?
- Are permissions minimized?
- Are outputs structured?
- Is routing deterministic where business rules require certainty?

---

# 3. Orchestrator–Worker Pattern and Agent Cards

One of the most important multi-agent patterns is:

```text
                  +--> Worker A
                  |
User -> Orchestrator +--> Worker B
                  |
                  +--> Worker C
```

## Orchestrator

The orchestrator:

- interprets the overall task,
- chooses workers,
- passes input,
- combines results,
- decides when the job is complete.

## Worker

A worker:

- has a narrow purpose,
- performs one domain-specific task,
- returns a predictable result.

## Example

User:

```text
"Give me a financial overview and explain unusual transactions."
```

Possible workflow:

```text
Coordinator
    |
    +--> Account Agent
    |
    +--> Transaction Agent
    |
    +--> Fraud Analysis Agent
    |
    +--> Report Agent
```

## A2A Agent Card

In distributed systems, another agent needs a way to discover:

- who an agent is,
- what it can do,
- how to communicate with it.

A2A uses an **Agent Card** for capability discovery.

Conceptually:

```json
{
  "name": "fraud_agent",
  "description": "Analyzes transaction patterns",
  "skills": [
    {
      "id": "analyze_transactions",
      "name": "Transaction Analysis"
    }
  ]
}
```

Treat the card like an API/service capability contract.

## Learn the difference

### Tool

A function/API used *by* an agent.

```text
Agent -> SQL tool
```

### Sub-agent

Another agent controlled inside an application.

```text
Coordinator -> AccountAgent
```

### Remote A2A agent

An independently running agent service.

```text
Coordinator service
       |
      A2A
       |
Fraud-agent service
```

## Official material

- ADK A2A overview: https://adk.dev/a2a/
- A2A introduction: https://adk.dev/a2a/intro/
- Consume an A2A agent in Python: https://adk.dev/a2a/quickstart-consuming/
- Expose an A2A agent in Python: https://adk.dev/a2a/quickstart-exposing/

Additional background:

- Google developer guide to agent protocols:
  https://developers.googleblog.com/developers-guide-to-ai-agent-protocols/

---

# 4. Multi-Agent Architecture with Python

Before learning framework-specific syntax, implement a minimal architecture yourself.

## Minimal mental model

```python
class Agent:
    async def run(self, request):
        ...
```

Then:

```python
class Coordinator:
    def __init__(self, workers):
        self.workers = workers

    async def run(self, request):
        ...
```

## Example architecture

```text
app/
|
+-- agents/
|   +-- coordinator.py
|   +-- account_agent.py
|   +-- fraud_agent.py
|   +-- support_agent.py
|
+-- tools/
|   +-- database.py
|   +-- search.py
|
+-- models/
|   +-- schemas.py
|
+-- services/
|   +-- state.py
|
+-- main.py
```

## Why do this before ADK?

Because you should understand that ADK is helping you implement concepts such as:

- lifecycle,
- delegation,
- event flow,
- sessions,
- tools,
- routing,
- orchestration.

The framework should not be magic.

## Exercise

Create three plain Python classes:

```text
ResearchAgent
SummarizerAgent
Coordinator
```

Flow:

```text
question
   |
Coordinator
   |
ResearchAgent
   |
SummarizerAgent
   |
answer
```

Then rebuild the same architecture using ADK.

---

# 5. Implementing Multi-Agent Architectures with ADK

Now map the architecture into ADK.

## Important ADK objects

Learn these concepts:

- `Agent` / `LlmAgent`
- `sub_agents`
- tools
- workflow agents
- custom agents
- sessions
- state
- callbacks/events

## Delegation

A root agent can coordinate specialized sub-agents.

Conceptually:

```text
root_agent
|
+-- account_agent
+-- fraud_agent
+-- support_agent
```

The root agent receives user input and delegates when needed.

## Good sub-agent instruction

Bad:

```text
You are useful and help with banking.
```

Better:

```text
You are the Account Information Agent.

Responsibilities:
- retrieve account information,
- summarize account status,
- never initiate transfers,
- never modify customer data.

When information is unavailable, return a structured failure.
```

## Design principle

The agent's:

```text
instructions + tools + permissions
```

should all describe the **same responsibility**.

## Exercise

Build:

```text
Coordinator
+-- ProductInfoAgent
+-- OrderStatusAgent
+-- FAQAgent
```

Give each agent different tools.

Then test prompts that should route to each one.

## Official material

- Agents: https://adk.dev/agents/
- Agent routing: https://adk.dev/agents/routing/
- Simple LLM agents: https://adk.dev/agents/llm-agents/
- Custom agents: https://adk.dev/agents/custom-agents/
- Workflow agents: https://adk.dev/agents/workflow-agents/

---

# 6. Orchestrating Agent Activities

There are several common orchestration patterns.

## Pattern 1: Sequential

```text
A -> B -> C
```

Use when B requires A's result, and C requires B's result.

Example:

```text
Document Retriever
        |
        v
Fact Extractor
        |
        v
Report Writer
```

## Pattern 2: Parallel

```text
       +--> A --+
Input -+--> B --+--> Merge
       +--> C --+
```

Use when branches are independent.

Example:

```text
               +--> News analysis
User request --+--> Database analysis
               +--> Document analysis
```

## Pattern 3: Router

```text
                 +--> A
Input -> Router -+--> B
                 +--> C
```

Use when only one or some agents should receive a task.

## Pattern 4: Loop

```text
Generate
  |
Evaluate
  |
Improve
  |
repeat
```

Useful for iterative workflows.

## Pattern 5: Hierarchical

```text
Main Coordinator
|
+-- Team Coordinator A
|   +-- Worker A1
|   +-- Worker A2
|
+-- Team Coordinator B
    +-- Worker B1
```

Useful only when the problem is genuinely large.

## Key engineering trade-off

More agent calls usually mean:

- more latency,
- more tokens,
- more failure points,
- more difficult tracing.

Therefore design the **smallest orchestration graph** that solves the problem.

---

# 7. SequentialAgent and ParallelAgent

ADK provides workflow agents for deterministic orchestration.

## SequentialAgent

Mental model:

```text
Step 1 completes
      |
      v
Step 2 completes
      |
      v
Step 3 completes
```

Good use cases:

- validate -> execute -> summarize,
- retrieve -> analyze -> write,
- parse -> transform -> verify.

Official docs:

https://adk.dev/agents/workflow-agents/sequential-agents/

## ParallelAgent

Mental model:

```text
             +--> Agent A
             |
Input ------ +--> Agent B
             |
             +--> Agent C
```

All independent branches can run concurrently.

Good use cases:

- query multiple knowledge sources,
- run several independent analyses,
- collect information from multiple services.

Official docs:

https://adk.dev/agents/workflow-agents/parallel-agents/

## Loop workflow

Also study:

https://adk.dev/agents/workflow-agents/loop-agents/

## Exercise

Create a research pipeline:

```text
ParallelAgent
|
+-- TechnicalResearchAgent
+-- BusinessResearchAgent
+-- RiskResearchAgent

then

Sequential:
parallel_results
    ->
SynthesisAgent
    ->
FinalReportAgent
```

## Important design question

Before using `ParallelAgent`, ask:

> Does any branch require another branch's result?

If yes, those branches are not truly parallel.

---

# 8. Routing and Data Flow in Agentic Systems

Routing determines where a request or intermediate result goes.

## LLM routing

The model interprets intent.

Example:

```text
"Why was my payment rejected?"
```

LLM selects:

```text
PaymentSupportAgent
```

Advantages:

- flexible,
- handles natural language well.

Disadvantages:

- not perfectly deterministic,
- can choose the wrong branch.

## Deterministic routing

Code decides.

Example:

```python
if transaction_amount > limit:
    route = "manual_review"
else:
    route = "automatic_processing"
```

Advantages:

- predictable,
- testable,
- appropriate for strict business rules.

## Hybrid routing

Often the best architecture:

```text
LLM understands user intent
          |
          v
deterministic code enforces policy
```

Example:

```text
User language -> Intent Agent -> Rule Engine -> Approved workflow
```

## Never make hard policy purely prompt-based

Bad:

```text
"Please remember to reject transactions above the limit."
```

Better:

```python
if amount > configured_limit:
    reject()
```

Use the LLM for fuzzy interpretation.

Use normal code for rules that must always hold.

---

# 9. CustomAgent for Deterministic Routing

A custom agent is useful when built-in orchestration is insufficient.

## Why CustomAgent?

You may need to:

- inspect events,
- run Python branching logic,
- transform intermediate results,
- call agents based on exact rules,
- implement retries,
- enforce invariants.

## Mental model

```python
class BusinessRouter(CustomAgent):
    async def run(...):
        if condition_a:
            ...
        elif condition_b:
            ...
        else:
            ...
```

The exact ADK interface may evolve, so use the current official docs while implementing.

Official material:

- Custom agents:
  https://adk.dev/agents/custom-agents/
- Routing:
  https://adk.dev/agents/routing/
- Events:
  https://adk.dev/events/
- Callbacks:
  https://adk.dev/callbacks/

## Exercise

Build a discount router:

```text
order
 |
 +-- if invalid -> ValidationAgent
 |
 +-- if premium customer -> PremiumPricingAgent
 |
 +-- otherwise -> StandardPricingAgent
```

Make the rule **code-based**, not LLM-decided.

---

# 10. State Management in Multi-Agent Systems

This is one of the most important sections.

## What is state?

State is data that must survive across steps or turns.

Example:

```json
{
  "customer_id": "C100",
  "selected_account": "A123",
  "verification_status": "verified",
  "workflow_step": "confirm_transfer"
}
```

## Stateless vs stateful

### Stateless

Each request is independent.

```text
request -> response
```

### Stateful

Later requests depend on previous information.

```text
Turn 1: "Use my savings account."
Turn 2: "Show recent transactions."
```

Turn 2 needs the earlier selection.

## Different types of state

Think in scopes.

### Request/invocation state

Exists during one execution.

### Session state

Persists throughout one conversation/session.

### User state

May persist across sessions.

### Shared application state

Accessible by multiple services/agents.

### Durable database state

Stored in MySQL/PostgreSQL/etc.

## Do not confuse conversation history with structured state

Conversation history:

```text
User: My account is A123.
Assistant: Okay.
```

Structured state:

```json
{
  "account_id": "A123"
}
```

For business logic, structured state is much safer.

## Official material

- Sessions:
  https://adk.dev/sessions/
- Session:
  https://adk.dev/sessions/session/
- State:
  https://adk.dev/sessions/state/
- Memory:
  https://adk.dev/sessions/memory/
- Agent context:
  https://adk.dev/context/

---

# 11. ToolContext and InvocationContext

You should understand *context objects* instead of memorizing their syntax.

## ToolContext

A tool may need access to execution/session information.

Conceptually:

```text
Tool
 |
 +--> read state
 +--> update state
 +--> inspect current context
```

Example use:

```text
select_account(account_id)
```

The tool can update session state:

```json
{
  "selected_account": "A123"
}
```

A later agent/tool can use it.

## InvocationContext

Represents broader information associated with an agent invocation.

Think of it as information needed while an agent execution is flowing through the runtime.

Possible concerns include:

- current session,
- events,
- state,
- agent invocation,
- runtime services.

## Important concept

Do not pass 15 unrelated values manually through every function:

```python
agent_a(user_id, session_id, customer_id, state, history, ...)
```

A context abstraction exists to carry execution information cleanly.

## Learn by experiment

Create a 3-turn conversation:

```text
Turn 1:
"Use account A123"

State:
selected_account = A123

Turn 2:
"Show its balance"

Turn 3:
"Now switch to A456"
```

Print/log state changes after each turn.

## Cloud persistence

Once local state works, move to a durable/cloud-backed session implementation.

Study:

- Firestore session service:
  https://adk.dev/integrations/firestore-session-service/
- Agent Runtime / deployment:
  https://adk.dev/deploy/agent-runtime/

---

# 12. Multi-Agent Orchestration and State Coordination

Multiple agents introduce a new problem:

> Who owns each piece of state?

## Bad architecture

Every agent writes arbitrary keys:

```text
Agent A -> shared_state
Agent B -> shared_state
Agent C -> shared_state
```

This easily causes conflicts.

## Better architecture

Define ownership.

Example:

| State | Owner |
|---|---|
| customer identity | IdentityAgent |
| account selection | AccountAgent |
| transaction draft | TransactionAgent |
| fraud result | FraudAgent |
| workflow status | Coordinator |

## State transition model

Treat workflow state like a state machine.

Example:

```text
START
  |
  v
IDENTIFIED
  |
  v
ACCOUNT_SELECTED
  |
  v
TRANSACTION_DRAFTED
  |
  v
VALIDATED
  |
  +--> REJECTED
  |
  +--> CONFIRMED
```

## Why state machines help

They make invalid transitions obvious.

For example:

```text
START -> CONFIRMED
```

should be impossible.

## Exercise

Build an order workflow with:

```text
NEW
VALIDATED
PAID
FULFILLED
CANCELLED
```

Make agents propose actions, but use deterministic code to validate allowed transitions.

---

# 13. Distributed Multi-Agent Systems with A2A

Until now, agents may all live inside one Python process.

Distributed A2A means:

```text
Service A              Service B
Coordinator  --A2A-->  Fraud Agent
     |
     +------A2A------>  Account Agent
```

Each agent may have:

- its own codebase,
- its own runtime,
- its own deployment,
- its own scaling,
- its own permissions.

## Why A2A?

A2A provides a standardized way for agents to discover and communicate with remote agents.

Core concepts:

- Agent Card
- capabilities / skills
- messages
- tasks
- artifacts/results
- remote agent endpoints

## `RemoteA2aAgent`

ADK can represent a remote A2A service as an agent that the local orchestrator can work with.

Conceptually:

```text
Local coordinator
      |
RemoteA2aAgent wrapper
      |
HTTP/A2A
      |
Remote service
```

## A2A vs MCP

This distinction is extremely important.

### MCP

Connects an agent to **tools/data/services**.

```text
Agent -> MCP -> Database tool
```

### A2A

Connects **agent to agent**.

```text
Agent -> A2A -> Agent
```

Simple memory trick:

```text
MCP = agent uses capabilities
A2A = agent collaborates with another agent
```

## Official material

- ADK + A2A:
  https://adk.dev/a2a/
- A2A introduction:
  https://adk.dev/a2a/intro/
- A2A Python consumer:
  https://adk.dev/a2a/quickstart-consuming/
- A2A Python exposing:
  https://adk.dev/a2a/quickstart-exposing/

Google Cloud also documents deploying A2A agents to managed runtimes and Cloud Run.

## Exercise

Create:

```text
coordinator-service :8000
risk-agent-service  :8001
```

The coordinator should call the risk agent remotely rather than importing its Python object directly.

---

# 14. MCP Toolbox for Databases

A distributed application often needs shared structured data.

Google's MCP Toolbox for Databases can expose database operations as agent tools.

Architecture:

```text
ADK Agent
   |
   v
MCP Toolbox
   |
   v
MySQL / PostgreSQL / Cloud SQL
```

## Why not let the LLM directly execute arbitrary SQL?

Because uncontrolled SQL generation can be risky and difficult to govern.

A better production pattern is to expose narrow tools such as:

```text
get_customer_accounts(customer_id)
get_recent_transactions(account_id)
create_transaction_draft(...)
update_transaction_status(...)
```

instead of:

```text
execute_any_sql(sql)
```

## Principle of least privilege

Each agent should receive only the tools it needs.

Example:

```text
AccountAgent:
- read_accounts
- read_balances

TransactionAgent:
- read_accounts
- create_transaction_draft

SupportAgent:
- no database write permission
```

## Official material

- MCP Toolbox for Databases:
  https://googleapis.github.io/mcp-toolbox/
- ADK MCP Toolbox integration:
  https://adk.dev/integrations/mcp-toolbox-for-databases/
- ADK MCP tools:
  https://adk.dev/tools-custom/mcp-tools/

## Exercise

Create a local database:

```text
customers
accounts
transactions
```

Expose only these operations:

```text
get_customer
get_accounts
get_transactions
```

Do **not** add writes initially.

Once reads work reliably, add a controlled write operation.

---

# 15. Multi-Agent Retrieval-Augmented Generation

## What is RAG?

RAG has two major stages:

```text
1. Retrieve relevant information
2. Give it to the model to generate a grounded answer
```

Basic architecture:

```text
Question
   |
Retriever
   |
Relevant chunks
   |
LLM
   |
Grounded answer
```

## Why multi-agent RAG?

Different sources may need different retrieval strategies.

Example:

```text
                         +--> Policy document retriever
Question -> Coordinator -+--> SQL customer-data agent
                         +--> FAQ/search agent
```

Then:

```text
retrieved evidence
      |
Synthesis Agent
      |
answer
```

## Structured vs unstructured retrieval

### Structured data

Example:

```text
customers
accounts
transactions
```

Use:

```text
SQL / database tools
```

### Unstructured data

Example:

```text
PDFs
policy documents
support documents
web pages
```

Use:

```text
search / vector retrieval / Agent Search / RAG Engine
```

A strong enterprise architecture often combines both.

## Vertex AI retrieval options

Study these concepts:

- Agent Search
- Vertex AI RAG Engine
- grounding
- vector retrieval
- chunking
- embeddings
- metadata filters
- citations / source attribution

Official material:

- Vertex AI APIs for Search/RAG:
  https://cloud.google.com/generative-ai-app-builder/docs/builder-apis
- ADK Agent Search integration:
  https://adk.dev/integrations/agent-search/
- ADK grounding:
  https://adk.dev/grounding/

## Core RAG concepts you must understand

### Chunking

Documents are split into retrieval units.

Too small:

```text
missing context
```

Too large:

```text
irrelevant content + expensive context
```

### Embeddings

Text is represented as vectors so semantically related content can be retrieved.

### Top-k retrieval

Retrieve the most relevant `k` chunks.

### Metadata filtering

Example:

```text
document_type = "bank_policy"
country = "VN"
effective_year = 2026
```

### Grounding

The answer should be based on retrieved evidence rather than unsupported model memory.

## Exercise

Build:

```text
PolicyAgent -> searches policy documents
CustomerDataAgent -> queries SQL
Coordinator -> combines both
```

Question:

```text
"Why did this customer's transaction fail, and what policy applies?"
```

The answer should use:

- structured transaction data,
- relevant policy text.

---

# 16. Vertex AI Agent Runtime / Agent Engine

Once your system works locally, learn managed deployment.

## Development stages

Do not deploy too early.

Recommended progression:

```text
1. Pure Python prototype
2. Local ADK agent
3. Local multi-agent system
4. Add state
5. Add tests/evaluation
6. Add database/RAG
7. Split selected agents into services
8. Add A2A
9. Deploy
10. Add observability
```

## Deployment concepts

Learn:

- Google Cloud project
- IAM
- service accounts
- Application Default Credentials
- runtime environment
- environment variables
- secrets
- logs
- traces
- autoscaling

## Official material

- Agent Runtime deployment:
  https://adk.dev/deploy/agent-runtime/
- Cloud Run deployment:
  https://adk.dev/deploy/cloud-run/
- GKE deployment:
  https://adk.dev/deploy/gke/
- Observability:
  https://adk.dev/observability/

---

# 17. Evaluation and Observability

A multi-agent system that "worked once" is not enough.

You need to evaluate:

```text
Did the router choose the correct agent?
Did the tool call use correct parameters?
Did state update correctly?
Did the workflow terminate?
Did retrieval return relevant evidence?
Did the final answer use the evidence?
```

## Evaluation dimensions

### Routing accuracy

Test:

```text
input -> expected agent
```

### Tool selection

Test:

```text
input -> expected tool
```

### Tool arguments

Check that calls use correct structured parameters.

### Workflow correctness

Check expected sequence:

```text
Validate -> RiskCheck -> Execute
```

rather than:

```text
Execute -> Validate
```

### State correctness

Verify state after each step.

### Retrieval quality

Measure whether relevant documents appear in top-k.

### Final response quality

Check:

- correctness,
- completeness,
- groundedness,
- format.

## Trace mindset

For each request, you should be able to answer:

```text
Which agent handled it?
Why?
Which tools were called?
What arguments were passed?
What state changed?
Which remote agents were contacted?
Which documents were retrieved?
Where did latency occur?
Where did the failure happen?
```

## Official material

- ADK evaluation:
  https://adk.dev/evaluate/
- Evaluation criteria:
  https://adk.dev/evaluate/criteria/
- Observability:
  https://adk.dev/observability/
- Traces:
  https://adk.dev/observability/traces/
- Logging:
  https://adk.dev/observability/logging/

---

# 18. Security Concepts You Should Learn

Multi-agent systems increase the number of trust boundaries.

## Principle of least privilege

Do not give every agent every tool.

## Separate read and write tools

Prefer:

```text
read_account
create_transfer_draft
confirm_transfer
```

instead of one unrestricted:

```text
database_admin
```

## Validate tool arguments

Never assume model-generated tool arguments are valid.

```python
if amount <= 0:
    raise ValueError(...)
```

## Require deterministic checks for critical rules

Examples:

```text
permissions
business limits
state transitions
required confirmation
schema validation
```

## Treat external content as untrusted

Retrieved documents or remote-agent responses can contain misleading instructions.

Your system should distinguish:

```text
data from instructions
```

## Learn action confirmation

For actions that change external state, study confirmation/approval mechanisms.

Official material:

- ADK safety:
  https://adk.dev/safety/
- Tool authentication:
  https://adk.dev/tools-custom/authentication/
- Action confirmations:
  https://adk.dev/tools-custom/confirmation/

---

# 19. Final Project — Distributed Banking Multi-Agent System

Build this as a **simulation/demo system**, not as a real banking deployment.

## Suggested architecture

```text
                         +---------------------+
                         |   Policy RAG Agent  |
                         | Vertex AI Search/RAG|
                         +----------+----------+
                                    |
                                    |
+------+      +---------------------v---------------------+
| User | ---> |             Coordinator Agent            |
+------+      +------------------+------------------------+
                                 |
              +------------------+------------------+
              |                  |                  |
              v                  v                  v
      +---------------+  +---------------+  +---------------+
      | Account Agent |  |Transfer Agent |  |  Risk Agent   |
      +-------+-------+  +-------+-------+  +-------+-------+
              |                  |                  |
              +--------+---------+------------------+
                       |
                       v
                +-------------+
                | MCP Toolbox |
                +------+------+
                       |
                       v
                    MySQL
```

Later split specialist agents into remote services:

```text
Coordinator
   |
   +-- A2A --> Account Service
   |
   +-- A2A --> Transfer Service
   |
   +-- A2A --> Risk Service
   |
   +-- A2A --> Policy RAG Service
```

## Agents

### 1. CoordinatorAgent

Responsibilities:

- interpret user request,
- route/delegate,
- combine results,
- maintain workflow-level state.

It should **not** directly modify the database.

### 2. AccountAgent

Responsibilities:

- account details,
- balance retrieval,
- transaction-history retrieval.

Tools:

```text
get_accounts
get_balance
get_recent_transactions
```

### 3. TransferAgent

Responsibilities:

- construct transfer draft,
- validate transfer fields,
- execute simulated transfer after required checks.

State:

```text
draft_transfer
transfer_status
```

### 4. RiskAgent

Responsibilities:

- inspect transaction details,
- evaluate deterministic risk rules,
- return structured result.

Output example:

```json
{
  "decision": "review",
  "reasons": ["amount_above_threshold"]
}
```

### 5. PolicyRagAgent

Responsibilities:

- search policy documents,
- retrieve relevant sections,
- return source-backed explanations.

### 6. SupportAgent

Optional.

Responsibilities:

- explain system results clearly,
- answer FAQ questions,
- never modify transactions.

---

# 20. Suggested Database Schema

For a learning project:

```sql
customers(
    customer_id,
    name
)

accounts(
    account_id,
    customer_id,
    account_type,
    balance
)

transactions(
    transaction_id,
    source_account_id,
    destination_account_id,
    amount,
    status,
    created_at
)

workflow_events(
    event_id,
    workflow_id,
    agent_name,
    event_type,
    payload,
    created_at
)
```

Important:

- Use fake/demo data only.
- Keep credentials in environment variables or Secret Manager.
- Do not hard-code secrets into source code.

---

# 21. Final Project Workflow

Example request:

```text
"Transfer 100 from account A1 to A2."
```

Suggested workflow:

```text
1. Coordinator understands intent
2. AccountAgent validates accounts
3. TransferAgent creates draft
4. RiskAgent evaluates draft
5. deterministic policy gate checks result
6. user confirmation step
7. TransferAgent executes simulation
8. transaction state is updated
9. Coordinator summarizes result
```

State progression:

```text
NEW
 |
 v
ACCOUNT_VALIDATED
 |
 v
DRAFT_CREATED
 |
 v
RISK_CHECKED
 |
 +--> BLOCKED
 |
 v
AWAITING_CONFIRMATION
 |
 v
EXECUTED
```

---

# 22. Project Milestones

## Milestone 1 — Single ADK agent

Build:

```text
one agent + two tools
```

Goal:

Understand ADK basics.

---

## Milestone 2 — Local multi-agent system

Build:

```text
Coordinator
+-- AccountAgent
+-- SupportAgent
```

Goal:

Understand delegation.

---

## Milestone 3 — Deterministic workflows

Add:

```text
SequentialAgent
ParallelAgent
CustomAgent
```

Goal:

Understand orchestration.

---

## Milestone 4 — Explicit state

Add:

```text
session state
workflow state
state transitions
```

Goal:

Understand multi-turn behavior.

---

## Milestone 5 — Database

Add:

```text
MySQL
MCP Toolbox
```

Goal:

Understand structured external state.

---

## Milestone 6 — RAG

Add:

```text
PolicyRagAgent
```

Goal:

Combine structured + unstructured knowledge.

---

## Milestone 7 — A2A

Move:

```text
RiskAgent
```

into its own service.

Goal:

Learn real distributed agent communication.

---

## Milestone 8 — Deployment

Deploy selected services to:

```text
Agent Runtime / Cloud Run
```

Goal:

Learn cloud architecture.

---

## Milestone 9 — Evaluation and observability

Create test cases for:

- routing,
- tool calls,
- state transitions,
- RAG retrieval,
- A2A failures,
- final responses.

Goal:

Make the project production-like.

---

# 23. Recommended Learning Order

Do **not** study all 15 modules independently.

Use this dependency order:

```text
Phase A — Agent fundamentals
1 -> 2 -> 4 -> 5

Phase B — Orchestration
6 -> 7 -> 8 -> 9

Phase C — State
10 -> 11 -> 12

Phase D — Distributed systems
3 -> 13

Phase E — Data and knowledge
14 -> 15

Phase F — Production
deployment -> evaluation -> observability -> security
```

A simpler version:

```text
Agent
  ↓
Sub-agents
  ↓
Sequential / Parallel
  ↓
Routing
  ↓
State
  ↓
A2A
  ↓
Database + MCP
  ↓
RAG
  ↓
Deployment
  ↓
Evaluation
```

---

# 24. Six-Week Study Plan

## Week 1 — ADK fundamentals

Learn:

- Agent
- tools
- sub-agents
- runner/runtime
- events

Build:

```text
Coordinator + 2 specialists
```

Read:

- https://adk.dev/get-started/
- https://adk.dev/agents/
- https://adk.dev/tutorials/agent-team/

---

## Week 2 — Orchestration

Learn:

- SequentialAgent
- ParallelAgent
- LoopAgent
- CustomAgent
- routing

Build:

```text
Research pipeline
```

Read:

- https://adk.dev/agents/workflow-agents/
- https://adk.dev/agents/workflow-agents/sequential-agents/
- https://adk.dev/agents/workflow-agents/parallel-agents/
- https://adk.dev/agents/custom-agents/
- https://adk.dev/agents/routing/

---

## Week 3 — State and sessions

Learn:

- session
- state
- context
- events
- state ownership

Build:

```text
multi-turn order workflow
```

Read:

- https://adk.dev/sessions/
- https://adk.dev/sessions/state/
- https://adk.dev/context/
- https://adk.dev/events/

---

## Week 4 — A2A + distributed architecture

Learn:

- A2A
- Agent Cards
- remote agents
- service boundaries
- failure handling

Build:

```text
Coordinator service
     |
     +-- A2A --> Specialist service
```

Read:

- https://adk.dev/a2a/
- https://adk.dev/a2a/intro/
- https://adk.dev/a2a/quickstart-consuming/
- https://adk.dev/a2a/quickstart-exposing/

---

## Week 5 — MCP database + RAG

Learn:

- MCP
- database tools
- structured retrieval
- vector/search retrieval
- RAG
- grounding

Build:

```text
SQL Agent
+
Policy RAG Agent
+
Coordinator
```

Read:

- https://googleapis.github.io/mcp-toolbox/
- https://adk.dev/integrations/mcp-toolbox-for-databases/
- https://adk.dev/tools-custom/mcp-tools/
- https://adk.dev/integrations/agent-search/
- https://adk.dev/grounding/

---

## Week 6 — Production architecture

Learn:

- deployment
- IAM
- observability
- tracing
- evaluation
- safety

Build:

```text
Distributed banking demo
```

Read:

- https://adk.dev/deploy/agent-runtime/
- https://adk.dev/deploy/cloud-run/
- https://adk.dev/observability/
- https://adk.dev/evaluate/
- https://adk.dev/safety/

---

# 25. What You Should Be Able to Explain After the Course

Do not consider a topic learned until you can answer these without looking at code.

## Multi-agent fundamentals

- Why use multiple agents instead of one large agent?
- What responsibility should belong to a separate agent?
- What are the costs of multi-agent architecture?

## Orchestration

- When should workflow be sequential?
- When should it be parallel?
- When should routing be LLM-based?
- When must routing be deterministic?
- Why use a custom agent?

## State

- What is the difference between conversation history and structured state?
- What is session state?
- Who owns each state variable?
- How do you avoid conflicting updates?

## Protocols

- What is MCP?
- What is A2A?
- What is an Agent Card?
- What is a remote agent?
- Why is A2A different from calling a normal function?

## RAG

- What is retrieval?
- What is chunking?
- What is an embedding?
- What is top-k?
- What is grounding?
- Why combine SQL and document search?

## Production

- How do you trace one user request through five agents?
- How do you test routing?
- How do you handle an unavailable remote agent?
- How do you minimize permissions?
- How do you validate model-generated tool arguments?

---

# 26. Practice Questions

Try answering these before checking documentation.

### Q1

You have three independent agents that retrieve:

```text
news
SQL statistics
company documents
```

Should they be sequential or parallel?

**Expected idea:** parallel, because their retrieval tasks are independent.

---

### Q2

A discount must be exactly 20% when `customer_tier == "gold"`.

Should an LLM decide this?

**Expected idea:** no. Use deterministic code for strict rules.

---

### Q3

An agent needs access to a remote specialist owned by another team.

Should you import its Python class?

**Expected idea:** no. This is a service boundary; A2A can provide standardized agent-to-agent communication.

---

### Q4

Your support agent needs to read account status but must never update balances.

How should you design tools?

**Expected idea:** give it read-only tools only.

---

### Q5

The user says:

```text
"Use account A123."
```

Two turns later they say:

```text
"Show its recent transactions."
```

What is needed?

**Expected idea:** session/structured state storing the selected account.

---

### Q6

Policy documents are PDFs, while account balances are in MySQL.

Should both be retrieved using vector search?

**Expected idea:** usually no. Use document retrieval/RAG for unstructured policy documents and SQL/database tools for structured account data.

---

# 27. Suggested Repository Structure

For your final learning project:

```text
multi-agent-banking/
|
+-- coordinator/
|   +-- agent.py
|   +-- routing.py
|
+-- agents/
|   +-- account/
|   |   +-- agent.py
|   |
|   +-- transfer/
|   |   +-- agent.py
|   |
|   +-- risk/
|   |   +-- agent.py
|   |
|   +-- policy_rag/
|       +-- agent.py
|
+-- tools/
|   +-- account_tools.py
|   +-- transaction_tools.py
|
+-- state/
|   +-- schemas.py
|   +-- transitions.py
|
+-- database/
|   +-- schema.sql
|   +-- toolbox/
|
+-- a2a/
|   +-- cards/
|
+-- evals/
|   +-- routing_cases.json
|   +-- workflow_cases.json
|   +-- rag_cases.json
|
+-- tests/
|   +-- unit/
|   +-- integration/
|
+-- app.py
+-- requirements.txt
+-- README.md
```

Do not start with all these folders.

Start tiny and grow the architecture as concepts are added.

---

# 28. Windows-Friendly Environment Notes

Use a project virtual environment so packages do not accidentally install into the wrong Python interpreter.

Example PowerShell workflow:

```powershell
mkdir multi-agent-adk
cd multi-agent-adk

py -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install google-adk
```

Verify that `python` and `pip` refer to the same environment:

```powershell
where.exe python
python -c "import sys; print(sys.executable)"
python -m pip --version
```

For Google Cloud authentication during local development, learn Application Default Credentials rather than placing credentials directly in source code.

Official Google Cloud setup material should be followed for your environment:

- https://cloud.google.com/docs/authentication/provide-credentials-adc

---

# 29. Where to Study — Resource Map

Use the resources in this order. Do not try to read every page before coding.

## Stage 1 — ADK Fundamentals

### 1. ADK overview

**Study:**

- ADK technical overview:  
  https://adk.dev/get-started/about/

- ADK getting started:  
  https://adk.dev/get-started/

- ADK documentation index:  
  https://adk.dev/llms.txt

**Learn:**

- what ADK is,
- `Agent`,
- model,
- instructions,
- tools,
- Runner,
- SessionService,
- events.

**Practice:**

Build:

```text
User
 |
 v
Agent
 |
 +--> calculator_tool
 +--> search_tool
```

Do not move on until you can build and run one agent yourself.

---

### 2. Tools

**Study:**

- ADK tools documentation:  
  https://adk.dev/tools/

- Custom tools:  
  https://adk.dev/tools-custom/

**Learn:**

- function tools,
- tool descriptions,
- tool arguments,
- tool results,
- validation,
- error handling.

**Practice:**

Create tools such as:

```python
get_product(product_id)
calculate_total(price, quantity)
```

Checklist:

- [ ] I can create a Python function tool.
- [ ] I understand how the LLM chooses a tool.
- [ ] I validate tool arguments.
- [ ] I can handle tool failure.

---

## Stage 2 — Multi-Agent Architecture

### 3. Sub-agents and delegation

**Study:**

- Agents:  
  https://adk.dev/agents/

- Agent-team tutorial:  
  https://adk.dev/tutorials/agent-team/

- LLM agents:  
  https://adk.dev/agents/llm-agents/

**Learn:**

```text
root_agent
|
+-- specialist_A
+-- specialist_B
+-- specialist_C
```

Understand:

- root agent,
- sub-agent,
- delegation,
- specialist responsibilities,
- tool boundaries.

**Practice project:**

```text
CustomerSupportCoordinator
|
+-- ProductAgent
+-- OrderAgent
+-- FAQAgent
```

Checklist:

- [ ] I can create a root agent.
- [ ] I can attach sub-agents.
- [ ] I can give each agent different tools.
- [ ] I understand when one agent should become a separate specialist.
- [ ] I can explain tool vs sub-agent.

---

### 4. Architecture design

**Study conceptually before framework syntax:**

- Orchestrator–Worker pattern
- separation of concerns
- capability boundaries
- input/output contracts
- least privilege

Use the architecture section of this guide as the main study material.

For every agent, write:

```text
Agent name:
Responsibility:
Input:
Output:
Tools:
State read:
State write:
Can call:
Failure behavior:
```

Checklist:

- [ ] Every agent has one clear responsibility.
- [ ] I know which agent owns each tool.
- [ ] I know which agent owns each state variable.
- [ ] I avoid one giant "do everything" agent.

---

## Stage 3 — Orchestration

### 5. Sequential workflows

**Study:**

- Workflow agents overview:  
  https://adk.dev/agents/workflow-agents/

- SequentialAgent:  
  https://adk.dev/agents/workflow-agents/sequential-agents/

**Learn:**

```text
A -> B -> C
```

Use when:

```text
B depends on A
C depends on B
```

Example:

```text
Retrieve
   ↓
Analyze
   ↓
Write
```

**Practice:**

Build:

```text
ResearchAgent
   ↓
AnalysisAgent
   ↓
ReportAgent
```

Checklist:

- [ ] I know when sequential execution is necessary.
- [ ] I can pass results between stages.
- [ ] I understand why dependent tasks cannot safely run in parallel.

---

### 6. Parallel workflows

**Study:**

- ParallelAgent:  
  https://adk.dev/agents/workflow-agents/parallel-agents/

**Learn:**

```text
         +--> A
Input ---+--> B
         +--> C
```

Use only when the tasks are independent.

**Practice:**

```text
Question
 |
 +--> SearchAgent
 |
 +--> DatabaseAgent
 |
 +--> DocumentAgent
 |
 v
SynthesisAgent
```

Checklist:

- [ ] I can identify independent tasks.
- [ ] I understand the latency benefit of parallel execution.
- [ ] I know when parallel execution would create dependency problems.

---

### 7. Loop workflows

**Study:**

- LoopAgent:  
  https://adk.dev/agents/workflow-agents/loop-agents/

**Learn:**

```text
Generate
   ↓
Evaluate
   ↓
Improve
   └------> repeat
```

Checklist:

- [ ] I understand loop termination.
- [ ] I set a maximum iteration count.
- [ ] I can explain why uncontrolled agent loops are dangerous.

---

### 8. ADK 2.0 graph workflows

After understanding Sequential / Parallel / Loop agents, study the newer workflow model.

**Study:**

- ADK workflows:  
  https://adk.dev/workflows/

- Live graph workflows:  
  https://adk.dev/live/workflows/

**Important:**

The template workflow agents are useful for learning deterministic orchestration, but newer ADK versions also provide graph/dynamic workflows.

Think:

```text
        +--> B --> D
A ------|
        +--> C --> E
                 |
                 v
                 F
```

Learn:

- nodes,
- edges,
- conditional routing,
- branching,
- loops,
- graph state.

Checklist:

- [ ] I understand template workflows first.
- [ ] I understand why graph workflows are more flexible.
- [ ] I can represent my workflow as nodes and edges.

---

## Stage 4 — Routing

### 9. LLM-based delegation

Study:

- Agents:  
  https://adk.dev/agents/

- Agent-team tutorial:  
  https://adk.dev/tutorials/agent-team/

Learn when the model can decide:

```text
Which specialist should answer this request?
```

Good for:

- natural-language intent,
- fuzzy categories,
- flexible delegation.

Checklist:

- [ ] I understand LLM-based routing.
- [ ] I know it is probabilistic rather than guaranteed.

---

### 10. Deterministic routing

**Study:**

- Agent routing:  
  https://adk.dev/agents/routing/

- Custom agents:  
  https://adk.dev/agents/custom-agents/

- Events:  
  https://adk.dev/events/

- Callbacks:  
  https://adk.dev/callbacks/

Learn:

```python
if customer_tier == "gold":
    ...
elif customer_tier == "silver":
    ...
```

Use code for:

- permissions,
- compliance rules,
- price calculations,
- limits,
- workflow transitions,
- required approvals.

Checklist:

- [ ] I know when routing can be LLM-based.
- [ ] I know when routing must be deterministic.
- [ ] I can implement rule-based routing.
- [ ] I understand why critical rules should not rely only on prompts.
- [ ] I know when a CustomAgent is useful.

---

## Stage 5 — Sessions and State

### 11. Sessions

**Study:**

- Sessions overview:  
  https://adk.dev/sessions/

- Session object:  
  https://adk.dev/sessions/session/

- Agent-team tutorial session section:  
  https://adk.dev/tutorials/agent-team/

Learn:

```text
User
  |
Session
  |
conversation history + state
```

Checklist:

- [ ] I understand what a session represents.
- [ ] I understand `SessionService`.
- [ ] I know the difference between a session and one model call.

---

### 12. State

**Study carefully:**

- State:  
  https://adk.dev/sessions/state/

Learn the difference:

```text
conversation history
vs
structured state
```

Example:

```python
session.state["selected_account"] = "A123"
```

Study scopes such as:

```text
temporary/invocation state
session state
user-related state
application state
external durable state
```

**Practice:**

```text
Turn 1:
"Use account A123"

Turn 2:
"Show its balance"

Turn 3:
"Switch to A456"
```

Checklist:

- [ ] I understand structured state.
- [ ] I can update session state.
- [ ] I can read state in a later turn.
- [ ] I understand state ownership.
- [ ] I know why important business data should not exist only in chat history.

---

### 13. Context objects

**Study:**

- Context:  
  https://adk.dev/context/

- State:  
  https://adk.dev/sessions/state/

Learn conceptually:

```text
ToolContext
InvocationContext
```

Understand why context objects exist:

```text
tool
 |
 +--> state
 +--> session
 +--> execution information
```

Checklist:

- [ ] I understand what `ToolContext` is for.
- [ ] I understand what invocation context represents.
- [ ] I can access/update relevant state from a tool.
- [ ] I avoid manually passing huge parameter lists throughout my application.

---

### 14. Events

**Study:**

- Events:  
  https://adk.dev/events/

Learn:

- agent activity produces events,
- events help inspect execution,
- events are useful for state changes and debugging.

Checklist:

- [ ] I can inspect an ADK event.
- [ ] I know how events help trace a workflow.

---

## Stage 6 — A2A and Distributed Agents

### 15. First understand the architecture

Before A2A code, understand:

```text
same-process sub-agent
```

versus:

```text
remote agent service
```

Same process:

```text
Coordinator
 |
 +--> Python AccountAgent object
```

Distributed:

```text
Coordinator service
 |
 | HTTP / A2A
 v
AccountAgent service
```

Checklist:

- [ ] I understand why distributed agents are more complex.
- [ ] I know when separate deployment is useful.

---

### 16. A2A fundamentals

**Study:**

- ADK A2A overview:  
  https://adk.dev/a2a/

- A2A introduction:  
  https://adk.dev/a2a/intro/

Learn:

- Agent Card,
- capability discovery,
- messages,
- tasks,
- remote services,
- standardized agent communication.

Checklist:

- [ ] I can explain A2A in one sentence.
- [ ] I understand Agent Cards.
- [ ] I understand remote agent discovery.
- [ ] I understand A2A vs normal Python function calls.

---

### 17. Build an A2A service

**Study:**

- Consume remote A2A agent:  
  https://adk.dev/a2a/quickstart-consuming/

- Expose an A2A agent:  
  https://adk.dev/a2a/quickstart-exposing/

**Practice:**

Run:

```text
Coordinator service
        |
        | A2A
        v
RiskAgent service
```

Checklist:

- [ ] I can expose an agent through A2A.
- [ ] I can consume a remote A2A agent.
- [ ] I understand `RemoteA2aAgent`.
- [ ] I can handle a remote-agent failure.

---

## Stage 7 — MCP and Databases

### 18. Understand MCP first

Mental model:

```text
Agent -> MCP -> Tool / Service / Database
```

Compare:

```text
MCP = agent-to-tool/service integration
A2A = agent-to-agent communication
```

Checklist:

- [ ] I can explain MCP.
- [ ] I can explain MCP vs A2A without notes.

---

### 19. MCP Toolbox for Databases

**Study:**

- MCP Toolbox documentation:  
  https://googleapis.github.io/mcp-toolbox/

- ADK MCP Toolbox integration:  
  https://adk.dev/integrations/mcp-toolbox-for-databases/

- ADK MCP tools:  
  https://adk.dev/tools-custom/mcp-tools/

Learn:

- MCP server,
- database source,
- toolset,
- restricted tools,
- authentication,
- connection pooling,
- predefined queries.

**Practice:**

Database:

```text
customers
accounts
transactions
```

Start with read-only tools:

```text
get_customer
get_accounts
get_transactions
```

Then add controlled write operations.

Checklist:

- [ ] I can connect ADK to MCP Toolbox.
- [ ] I can expose a database query as a tool.
- [ ] I understand read vs write permissions.
- [ ] I understand least privilege.
- [ ] I avoid unrestricted arbitrary SQL in production-style agents.

---

## Stage 8 — RAG

### 20. Basic RAG theory

Before Vertex AI, learn:

```text
Question
   ↓
Retrieve
   ↓
Relevant chunks
   ↓
LLM
   ↓
Grounded response
```

Concept checklist:

- [ ] I understand chunking.
- [ ] I understand embeddings.
- [ ] I understand vector similarity.
- [ ] I understand top-k retrieval.
- [ ] I understand metadata filtering.
- [ ] I understand grounding.
- [ ] I understand retrieval quality vs generation quality.

Good conceptual starting point:

- Google Cloud RAG documentation:  
  https://cloud.google.com/vertex-ai/generative-ai/docs/rag-overview

---

### 21. Agent Search / enterprise retrieval

**Study:**

- ADK Agent Search integration:  
  https://adk.dev/integrations/agent-search/

- ADK grounding:  
  https://adk.dev/grounding/

- Vertex AI Search / discovery APIs:  
  https://cloud.google.com/generative-ai-app-builder/docs/builder-apis

Learn:

```text
unstructured documents -> search/retrieval
structured records -> SQL/database tools
```

Checklist:

- [ ] I can retrieve relevant documents.
- [ ] I can return sources with an answer.
- [ ] I understand why SQL is normally better than vector search for exact structured fields.
- [ ] I can combine structured + unstructured retrieval.

---

### 22. Multi-agent RAG

**Practice architecture:**

```text
                    +--> PolicyRagAgent
User -> Coordinator +--> CustomerDatabaseAgent
                    +--> TransactionAgent
                              |
                              v
                         SynthesisAgent
```

Checklist:

- [ ] Each retrieval agent has a specific data source.
- [ ] Retrieval outputs are structured.
- [ ] The synthesis agent receives evidence, not unrestricted database access.
- [ ] Final answers are grounded in retrieved evidence.

---

## Stage 9 — Deployment

### 23. Local development first

Before cloud deployment, make sure you can run:

```text
local ADK agent
local multi-agent workflow
local state
local database/RAG
```

Only then deploy.

Checklist:

- [ ] My project works locally.
- [ ] My tests run locally.
- [ ] Secrets are not hard-coded.

---

### 24. Google Cloud deployment

**Study:**

- Agent Runtime:  
  https://adk.dev/deploy/agent-runtime/

- Cloud Run:  
  https://adk.dev/deploy/cloud-run/

- GKE:  
  https://adk.dev/deploy/gke/

- Google Cloud Application Default Credentials:  
  https://cloud.google.com/docs/authentication/provide-credentials-adc

Learn:

- GCP project,
- IAM,
- service accounts,
- ADC,
- Secret Manager,
- environment variables,
- deployment configuration.

Checklist:

- [ ] I understand service accounts.
- [ ] I understand IAM at a basic level.
- [ ] I use ADC locally.
- [ ] I keep credentials outside source code.
- [ ] I can deploy at least one agent service.

---

## Stage 10 — Evaluation

### 25. ADK evaluation

**Study:**

- Evaluation overview:  
  https://adk.dev/evaluate/

- Evaluation criteria:  
  https://adk.dev/evaluate/criteria/

Learn how to test:

```text
input
  ↓
routing
  ↓
tool trajectory
  ↓
tool arguments
  ↓
state changes
  ↓
final response
```

Important evaluation targets:

- routing correctness,
- tool selection,
- tool arguments,
- tool trajectory,
- final-response correctness,
- multi-turn behavior,
- RAG groundedness.

Checklist:

- [ ] I can create evaluation cases.
- [ ] I can test expected tool calls.
- [ ] I can test routing.
- [ ] I can test multi-turn behavior.
- [ ] I can test final response quality.
- [ ] I can detect regression after changing prompts/code.

---

## Stage 11 — Observability

### 26. Tracing and logging

**Study:**

- Observability:  
  https://adk.dev/observability/

- Traces:  
  https://adk.dev/observability/traces/

- Logging:  
  https://adk.dev/observability/logging/

For every request you should eventually be able to answer:

```text
Which agent ran?
Which model was called?
Which tool was called?
What arguments were passed?
What state changed?
How long did each step take?
Did a remote agent fail?
What information was retrieved?
```

Checklist:

- [ ] I can inspect a request trace.
- [ ] I can identify which agent caused a failure.
- [ ] I can inspect tool calls and latency.
- [ ] I can inspect important state transitions.

---

## Stage 12 — Security

### 27. Agent safety and permissions

**Study:**

- ADK safety:  
  https://adk.dev/safety/

- Tool authentication:  
  https://adk.dev/tools-custom/authentication/

- Tool confirmation:  
  https://adk.dev/tools-custom/confirmation/

Learn:

- least privilege,
- read/write separation,
- argument validation,
- authentication,
- authorization,
- user confirmation,
- external-data trust boundaries.

Checklist:

- [ ] Agents only receive necessary tools.
- [ ] Read-only agents do not receive write tools.
- [ ] Tool inputs are validated.
- [ ] Sensitive actions require deterministic checks.
- [ ] External retrieved text is treated as data, not trusted instructions.
- [ ] Important actions can require explicit confirmation.

---

# 30. Master Learning Checklist

Use this as your actual progress tracker.

Do not tick a topic because you watched a video.

Tick it only when you can **explain it and build a small example yourself**.

## Level 1 — Single-Agent ADK

- [ ] Understand `Agent`.
  - Study: https://adk.dev/get-started/
- [ ] Understand Runner.
  - Study: https://adk.dev/tutorials/agent-team/
- [ ] Understand SessionService.
  - Study: https://adk.dev/tutorials/agent-team/
- [ ] Create function tools.
  - Study: https://adk.dev/tools-custom/
- [ ] Inspect agent events.
  - Study: https://adk.dev/events/
- [ ] Build one working agent with at least two tools.

**Mini-project:**

```text
Personal Research Assistant
+ calculator
+ simple information lookup
```

---

## Level 2 — Multi-Agent ADK

- [ ] Create sub-agents.
  - Study: https://adk.dev/agents/
- [ ] Understand delegation.
  - Study: https://adk.dev/tutorials/agent-team/
- [ ] Design specialist responsibilities.
  - Study: Section 2 of this guide.
- [ ] Give different agents different tools.
- [ ] Build a coordinator with at least two specialists.

**Mini-project:**

```text
SupportCoordinator
+ ProductAgent
+ OrderAgent
+ FAQAgent
```

---

## Level 3 — Orchestration

- [ ] Understand sequential execution.
  - Study: https://adk.dev/agents/workflow-agents/sequential-agents/
- [ ] Understand parallel execution.
  - Study: https://adk.dev/agents/workflow-agents/parallel-agents/
- [ ] Understand loop execution.
  - Study: https://adk.dev/agents/workflow-agents/loop-agents/
- [ ] Understand deterministic workflow agents.
  - Study: https://adk.dev/agents/workflow-agents/
- [ ] Learn graph workflows after template workflows.
  - Study: https://adk.dev/workflows/
- [ ] Build a workflow combining parallel + sequential stages.

**Mini-project:**

```text
        +--> TechnicalResearch
Question+--> BusinessResearch
        +--> RiskResearch
                 |
                 v
              Synthesis
```

---

## Level 4 — Routing

- [ ] Understand LLM delegation.
  - Study: https://adk.dev/agents/
- [ ] Understand deterministic routing.
  - Study: https://adk.dev/agents/routing/
- [ ] Understand CustomAgent.
  - Study: https://adk.dev/agents/custom-agents/
- [ ] Know when rules must be normal Python code.
- [ ] Build at least one rule-based router.

**Mini-project:**

```text
Request
 |
 +-- valid? ------ no --> ValidationAgent
 |
 +-- premium? ---- yes -> PremiumAgent
 |
 +---------------------> StandardAgent
```

---

## Level 5 — State Management

- [ ] Understand sessions.
  - Study: https://adk.dev/sessions/
- [ ] Understand `session.state`.
  - Study: https://adk.dev/sessions/state/
- [ ] Understand context objects.
  - Study: https://adk.dev/context/
- [ ] Understand events.
  - Study: https://adk.dev/events/
- [ ] Understand state ownership.
- [ ] Model workflow states explicitly.
- [ ] Build a multi-turn stateful workflow.

**Mini-project:**

```text
Order Assistant

NEW
 ↓
VALIDATED
 ↓
PAID
 ↓
FULFILLED
```

---

## Level 6 — A2A

- [ ] Understand Agent Cards.
  - Study: https://adk.dev/a2a/intro/
- [ ] Understand A2A communication.
  - Study: https://adk.dev/a2a/
- [ ] Expose one agent as an A2A service.
  - Study: https://adk.dev/a2a/quickstart-exposing/
- [ ] Consume one remote agent.
  - Study: https://adk.dev/a2a/quickstart-consuming/
- [ ] Understand `RemoteA2aAgent`.
- [ ] Handle remote-agent failure.

**Mini-project:**

```text
Coordinator Service
       |
       | A2A
       v
Risk Service
```

---

## Level 7 — MCP + Database

- [ ] Understand MCP.
  - Study: https://adk.dev/tools-custom/mcp-tools/
- [ ] Understand MCP Toolbox.
  - Study: https://googleapis.github.io/mcp-toolbox/
- [ ] Connect ADK to Toolbox.
  - Study: https://adk.dev/integrations/mcp-toolbox-for-databases/
- [ ] Expose read-only DB tools.
- [ ] Add controlled DB writes.
- [ ] Apply least privilege.

**Mini-project:**

```text
AccountAgent
    |
    v
MCP Toolbox
    |
    v
MySQL
```

---

## Level 8 — RAG

- [ ] Understand chunking.
- [ ] Understand embeddings.
- [ ] Understand top-k.
- [ ] Understand metadata filters.
- [ ] Understand grounding.
  - Study: https://adk.dev/grounding/
- [ ] Understand Agent Search.
  - Study: https://adk.dev/integrations/agent-search/
- [ ] Understand Vertex AI RAG concepts.
  - Study: https://cloud.google.com/vertex-ai/generative-ai/docs/rag-overview
- [ ] Combine SQL and document retrieval.
- [ ] Build multi-agent RAG.

**Mini-project:**

```text
Question
 |
 +--> SQL Agent
 |
 +--> Policy RAG Agent
 |
 v
Synthesis Agent
```

---

## Level 9 — Production

- [ ] Understand deployment options.
  - Study: https://adk.dev/deploy/agent-runtime/
- [ ] Deploy one service to Cloud Run or Agent Runtime.
  - Study: https://adk.dev/deploy/cloud-run/
- [ ] Understand evaluation.
  - Study: https://adk.dev/evaluate/
- [ ] Understand evaluation criteria.
  - Study: https://adk.dev/evaluate/criteria/
- [ ] Understand tracing.
  - Study: https://adk.dev/observability/traces/
- [ ] Understand logging.
  - Study: https://adk.dev/observability/logging/
- [ ] Understand ADK safety.
  - Study: https://adk.dev/safety/
- [ ] Create routing tests.
- [ ] Create tool-use tests.
- [ ] Create state-transition tests.
- [ ] Create RAG evaluation cases.

---

## Level 10 — Final Project

Build the distributed banking **simulation** from this guide.

Completion checklist:

- [ ] CoordinatorAgent
- [ ] AccountAgent
- [ ] TransferAgent
- [ ] RiskAgent
- [ ] PolicyRagAgent
- [ ] explicit session/workflow state
- [ ] deterministic policy routing
- [ ] Sequential/Parallel or graph workflow
- [ ] MySQL demo database
- [ ] MCP Toolbox
- [ ] structured database tools
- [ ] document retrieval/RAG
- [ ] at least one agent moved to an A2A service
- [ ] Agent Card
- [ ] remote-agent error handling
- [ ] evaluation dataset
- [ ] traces/logging
- [ ] permission boundaries
- [ ] README architecture diagram
- [ ] demo scenarios

---

# 30.1 Recommended Study Order

Follow this exact order:

```text
1. Agent + tools
        ↓
2. Runner + sessions + events
        ↓
3. Sub-agents
        ↓
4. Sequential / Parallel / Loop
        ↓
5. Custom routing
        ↓
6. State + ToolContext
        ↓
7. Graph workflows
        ↓
8. A2A
        ↓
9. MCP + MySQL
        ↓
10. RAG / Agent Search
        ↓
11. Deployment
        ↓
12. Evaluation + Observability + Security
        ↓
13. Final distributed project
```

Do **not** start with A2A or Vertex deployment.

First become comfortable building a local multi-agent application.

---

# 30.2 What to Learn Deeply vs What to Know

## Learn deeply

These are core Agent Engineer skills:

```text
Agent architecture
Tool calling
Routing
State management
Workflow orchestration
Error handling
Evaluation
Observability
Security boundaries
RAG
```

## Understand well

```text
A2A
MCP
Agent Cards
Vertex AI deployment
Agent Search
```

## Do not memorize

Do not spend time memorizing:

```text
exact ADK class signatures
every constructor parameter
every cloud CLI option
every deployment configuration field
```

APIs change.

Instead, understand:

```text
why the component exists
when to use it
what data goes in
what comes out
what can fail
how to test it
```

---

# 31. The Most Important Mental Model

Do not think:

```text
multi-agent = many LLMs talking to each other
```

Think:

```text
multi-agent system =
    software architecture
    + specialized agents
    + deterministic workflows where needed
    + tools
    + explicit state
    + communication protocols
    + databases/retrieval
    + evaluation
    + observability
    + security boundaries
```

The LLM is only one component.

If you understand the architecture around the model, the Google ADK syntax becomes much easier to learn.
