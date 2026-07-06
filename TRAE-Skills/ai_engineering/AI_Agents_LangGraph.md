# Skill: Building AI Agents with LangGraph

## Purpose
To build stateful, multi-agent, and agentic systems using LangGraph for complex workflows (reasoning, tool use, multi-step tasks).

## When to Use
- When building customer support agents that use multiple tools
- For research assistants that can browse, analyze, and summarize
- When creating multi-agent collaboration systems
- For building RAG with reasoning loops
- When you need agentic workflows with human-in-the-loop

## Procedure

### 1. Basic LangGraph Agent
Create a simple agent with tools.

```python
from typing import Annotated, Literal, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# Define tools
@tool
def search_web(query: str) -> str:
    """Search the web for a query."""
    return f"Search results for '{query}': LangGraph is a library for building stateful agents."

@tool
def calculate(expression: str) -> str:
    """Calculate a mathematical expression."""
    try:
        return str(eval(expression))
    except:
        return "Invalid expression"

tools = [search_web, calculate]

# Define state
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize model
llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_with_tools = llm.bind_tools(tools)

# Define nodes
def agent_node(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

tool_node = ToolNode(tools)

# Define conditional edge
def should_continue(state: AgentState) -> Literal["tools", END]:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

# Build graph
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")

app = graph.compile()

# Run agent
result = app.invoke({"messages": [("user", "What's 25 * 4 + 10? Also, tell me about LangGraph.")]})
print(result["messages"][-1].content)
```

### 2. Multi-Agent Collaboration
Build a team of specialized agents.

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END

# Define specialized agents
researcher_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a researcher. Use the search tool to find information."),
    MessagesPlaceholder(variable_name="messages")
])

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a writer. Take research and write a concise summary."),
    MessagesPlaceholder(variable_name="messages")
])

reviewer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a reviewer. Check the summary and improve it if needed."),
    MessagesPlaceholder(variable_name="messages")
])

class TeamState(TypedDict):
    messages: Annotated[list, add_messages]
    current_agent: str
    final_summary: str

def researcher_node(state: TeamState):
    researcher_llm = researcher_prompt | llm_with_tools
    response = researcher_llm.invoke(state["messages"])
    return {"messages": [response], "current_agent": "researcher"}

def writer_node(state: TeamState):
    writer_llm = writer_prompt | llm
    response = writer_llm.invoke(state["messages"])
    return {"messages": [response], "current_agent": "writer", "final_summary": response.content}

def reviewer_node(state: TeamState):
    reviewer_llm = reviewer_prompt | llm
    response = reviewer_llm.invoke(state["messages"])
    return {"messages": [response], "current_agent": "reviewer", "final_summary": response.content}

def route_team(state: TeamState) -> Literal["researcher", "writer", "reviewer", END]:
    if not state["current_agent"]:
        return "researcher"
    elif state["current_agent"] == "researcher":
        return "writer"
    elif state["current_agent"] == "writer":
        return "reviewer"
    return END

team_graph = StateGraph(TeamState)
team_graph.add_node("researcher", researcher_node)
team_graph.add_node("writer", writer_node)
team_graph.add_node("reviewer", reviewer_node)
team_graph.add_conditional_edges(START, route_team)
team_graph.add_conditional_edges("researcher", route_team)
team_graph.add_conditional_edges("writer", route_team)

team_app = team_graph.compile()

# Run team
result = team_app.invoke({"messages": [("user", "Research LangGraph and write a summary.")]})
print("Final Summary:", result["final_summary"])
```

### 3. Human-in-the-Loop (HITL)
Add human approval steps.

```python
from langgraph.checkpoint.memory import MemorySaver

class HITLState(TypedDict):
    messages: Annotated[list, add_messages]
    approved: bool

def agent_node_with_approval(state: HITLState):
    if not state.get("approved", False):
        # Wait for human approval (interrupt)
        pass
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

checkpointer = MemorySaver()

hitl_graph = StateGraph(HITLState)
hitl_graph.add_node("agent", agent_node_with_approval)
hitl_graph.add_edge(START, "agent")
hitl_graph.add_conditional_edges("agent", should_continue)
hitl_graph.add_edge("tools", "agent")

hitl_app = hitl_graph.compile(checkpointer=checkpointer, interrupt_before=["agent"])

config = {"configurable": {"thread_id": "1"}}

# Initial run (interrupts before agent)
initial_result = hitl_app.invoke({"messages": [("user", "Approve this action?")]}, config)

# Human approves
human_approved_state = hitl_app.update_state(config, {"approved": True})

# Continue execution
final_result = hitl_app.invoke(None, config)
```

### 4. RAG Agent with LangGraph
Build an agent that does RAG with reasoning.

```python
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# Sample documents
documents = [
    Document(page_content="LangGraph is for building stateful agents.", metadata={"source": "doc1"}),
    Document(page_content="Agents can use tools and have memory.", metadata={"source": "doc2"})
]

vector_store = InMemoryVectorStore.from_documents(documents, OpenAIEmbeddings())
retriever = vector_store.as_retriever(k=2)

@tool
def retrieve_documents(query: str) -> str:
    """Retrieve relevant documents from the knowledge base."""
    docs = retriever.invoke(query)
    return "\n\n".join([f"Source: {d.metadata['source']}\n{d.page_content}" for d in docs])

rag_tools = [retrieve_documents]
rag_llm = llm.bind_tools(rag_tools)

# RAG agent graph
rag_graph = StateGraph(AgentState)
rag_graph.add_node("agent", lambda s: {"messages": [rag_llm.invoke(s["messages"])]})
rag_graph.add_node("tools", ToolNode(rag_tools))
rag_graph.add_edge(START, "agent")
rag_graph.add_conditional_edges("agent", should_continue)
rag_graph.add_edge("tools", "agent")

rag_app = rag_graph.compile()

result = rag_app.invoke({"messages": [("user", "What is LangGraph used for?")]})
print(result["messages"][-1].content)
```

## Best Practices
- **State Design**: Keep state minimal and typed
- **Tool Design**: Make tools with clear, specific descriptions
- **Error Handling**: Add fallback edges for failures
- **Checkpoints**: Use checkpoints for long-running workflows
- **Evaluation**: Test agent workflows with LangSmith
- **Cost**: Limit tool calls to control costs
- **Human-in-the-Loop**: Add approval steps for high-stakes actions
