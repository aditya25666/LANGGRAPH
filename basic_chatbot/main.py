from typing import TypedDict

from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END

from langchain_google_genai import ChatGoogleGenerativeAI


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
    question: str
    answer: str


# ------------------------------------
# Chatbot Node
# ------------------------------------

def chatbot(state: ChatState):

    print("\n===== CHATBOT =====")

    response = llm.invoke(state["question"])

    return {
        "answer": response.content
    }


# ------------------------------------
# Build Graph
# ------------------------------------

builder = StateGraph(ChatState)

builder.add_node("chatbot", chatbot)

builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)


# ------------------------------------
# Compile Graph
# ------------------------------------

graph = builder.compile()


# ------------------------------------
# Continuous Chat
# ------------------------------------

print("\n===== AI Chatbot =====")
print("Type 'exit' to quit.\n")

while True:

    question = input("You : ")

    if question.lower() == "exit":
        print("\nGoodbye!")
        break

    result = graph.invoke(
        {
            "question": question,
            "answer": ""
        }
    )

    print("\nAssistant :", result["answer"])
    print()

