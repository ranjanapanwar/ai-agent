import os

from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.redis import RedisSaver
from .nodes import agent_node, human_review_node, tools_node

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

def create_agent_graph():
    graph = StateGraph(MessagesState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tools_node)
    graph.add_node("human_review_node", human_review_node)

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition, {"tools": "human_review_node", END: END})
    graph.add_conditional_edges("human_review_node", tools_condition, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    return graph

memory = RedisSaver(REDIS_URL)
agent_graph = create_agent_graph().compile(checkpointer=memory)