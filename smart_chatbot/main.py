from typing import Annotated
from typing_extensions import TypedDict

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver


# ------------------------------------
# Load Environment Variables
# ------------------------------------

load_dotenv()


# ------------------------------------
# LLM
# ------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)


# ------------------------------------
# State
# ------------------------------------

class ChatState(TypedDict):

    messages: Annotated[list, add_messages]


# ------------------------------------
# Chatbot Node
# ------------------------------------

def chatbot(state: ChatState):

    response = llm.invoke(state["messages"])

    return {
        "messages": [response]
    }


# ------------------------------------
# Memory
# ------------------------------------

memory = MemorySaver()


# ------------------------------------
# Build Graph
# ------------------------------------

builder = StateGraph(ChatState)

builder.add_node("chatbot", chatbot)

builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)


graph = builder.compile(
    checkpointer=memory
)


# ------------------------------------
# Thread Configuration
# ------------------------------------

config = {
    "configurable": {
        "thread_id": "chat-1"
    }
}


# ------------------------------------
# Continuous Chat
# ------------------------------------

print("\n===== AI Chatbot =====")
print("Type 'exit' to quit.\n")

while True:

    question = input("You : ")

    if question.lower() == "exit":
        break

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content=question)
            ]
        },
        config=config
    )

    print("\nAssistant :", result["messages"][-1].content)
    print()