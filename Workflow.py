import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

from RAG import get_retriever

from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.documents import Document

from langgraph.graph import StateGraph, START, END

load_dotenv()

model = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ.get("GROQ_API_KEY")
)

retriever = get_retriever()

conn = sqlite3.connect('chat_history.db',check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

class ChatState(TypedDict):
    query: str
    context: list[Document]
    message: Annotated[list[BaseMessage],add_messages]

def retrive(state: ChatState):
    pass

def chatNode(state: ChatState):
    pass

graph = StateGraph(ChatState)

graph.add_node('retriever',retrive)
graph.add_node('llm',chatNode)

graph.add_edge(START,'retriever')
graph.add_edge('retriever','llm')
graph.add_edge('llm',END)

workflow = graph.compile(checkpointer=checkpointer)