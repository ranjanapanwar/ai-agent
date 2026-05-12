from urllib import response

from langchain_core.tools import tool
import httpx
import os
from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()  # Load environment variables from .env file
doc_search_url = os.getenv("ASK_MY_DOCS_URL", "http://localhost:8000")
summarizer_url = os.getenv("SMART_SUMMARIZER_URL", "http://localhost:7860")



@tool
def web_search(query: str) -> str:
    """Search the web for the 
       given query for current events, recent information 
       and anything not in uploaded documents
       and return the results.
    """
    try:
        tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        response = tavily_client.search(query, max_results=5)
        return str(response)
    except Exception as e:
        return f"Error occurred while searching the web: {str(e)}"

@tool
def doc_search(query: str) -> str:
    """Use this when the user asks questions about the uploaded documents."""
    try:
        response = httpx.post(doc_search_url + "/ask", params={"query": query, "query_namespace": "c7981f89-b3a6-49c3-8025-44da406c1a5a"})
        print(f">>> tool: doc_search")
       
        return response.json()["answer"]
    except Exception as e:
        return f"Error occurred while searching documents: {str(e)}"

@tool
def summarize_text(text: str) -> str:
    """Use this ONLY when the user explicitly says 'summarize' in their message. Do NOT call this automatically after web_search or doc_search."""
    try:
        response = httpx.post(summarizer_url+"/summarize-sync", json={"text": text})
        print(f">>> tool: summarize_text")

        return response.json()["summary"]
    except Exception as e:
        return f"Error occurred while summarizing text: {str(e)}"
    
tools = [web_search, doc_search, summarize_text]