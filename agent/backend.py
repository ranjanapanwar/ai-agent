from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from agent.graph import agent_graph
from dotenv import load_dotenv
from langgraph.types import Command
from langgraph.errors import GraphInterrupt

load_dotenv()

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    thread_id: str

class ResumeRequest(BaseModel):
    thread_id: str
    approved: bool

@app.post("/chat")
def chat(chat_request: ChatRequest):
    try:
        human_message = HumanMessage(content=chat_request.message)
        final_response = ""
        interrupted = False
        for chunk in agent_graph.stream({"messages": [human_message]}, config={"configurable": {"thread_id": chat_request.thread_id}},):
            print("CHUNK KEYS:", chunk.keys()) 
            print(chunk)  # logs tool calls to terminal
            if "__interrupt__" in chunk:
                interrupted = True
                break
            if "agent" in chunk:
                messages = chunk["agent"].get("messages", [])
                if messages:
                    final_response = messages[-1].content

        if interrupted:
            return {"status": "interrupted", "message": "Agent wants to search the web. Approve?", "thread_id": chat_request.thread_id}
        return {"status": "success", "response": final_response, "thread_id": chat_request.thread_id}
    except Exception as e:
        return {"status": "error", "error": str(e), "thread_id": chat_request.thread_id}

@app.post("/chat/resume")
def resume_chat(resume_request: ResumeRequest):
    try:
        final_response = ""
        interrupted = False
        for chunk in agent_graph.stream(
            Command(resume=resume_request.approved),
            config={"configurable": {"thread_id": resume_request.thread_id}},
        ):
            print("RESUME CHUNK KEYS:", chunk.keys())
            print(chunk)
            if "__interrupt__" in chunk:
                interrupted = True
                break
            if "agent" in chunk:
                messages = chunk["agent"].get("messages", [])
                if messages:
                    final_response = messages[-1].content

        if interrupted:
            return {"status": "interrupted", "message": "Agent needs approval. Approve?", "thread_id": resume_request.thread_id}
        return {"status": "success", "response": final_response, "thread_id": resume_request.thread_id}
    except Exception as e:
        return {"status": "error", "error": str(e), "thread_id": resume_request.thread_id}
