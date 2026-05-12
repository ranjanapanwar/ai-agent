from langchain_groq import ChatGroq
from .tools import tools
from langgraph.prebuilt import ToolNode
import os
from dotenv import load_dotenv
from langgraph.graph import MessagesState
from langgraph.types import interrupt
from langchain_core.messages import ToolMessage, SystemMessage

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=GROQ_API_KEY)
llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = SystemMessage(content="""You are a helpful assistant with access to tools.

Tool usage rules:
- Use `web_search` for current events or information not in documents.
- Use `doc_search` when the user asks about uploaded documents.
- Use `summarize_text` ONLY if the user explicitly says "summarize" in their message. Never call it automatically after web_search or doc_search.
- Call only ONE tool per step. Do not chain tools unless the user asks for it.
- After getting tool results, respond directly to the user in plain text.""")

tools_node = ToolNode(tools)

def agent_node(state: MessagesState):
    messages = [SYSTEM_PROMPT] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def human_review_node(state: MessagesState):
    if state["messages"][-1].tool_calls and state["messages"][-1].tool_calls[0]["name"]=="web_search":
        approved = interrupt("Agent wants to use web search tool. Approve?")
        if approved:
            return {}
        else:
            toolMessage = ToolMessage(content="Web search denied. Answer using only what you know", tool_call_id=state["messages"][-1].tool_calls[0]["id"])
            return {"messages": [toolMessage]}
    return {}

