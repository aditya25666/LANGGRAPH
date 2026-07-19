# Load API key from .env
from dotenv import load_dotenv

# Import TypedDict for state
from typing import TypedDict

# Import LangGraph
from langgraph.graph import StateGraph, START, END

# Import Gemini Chat Model
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# Create Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)


# Define graph state
class ChatState(TypedDict):
    question: str
    answer: str


# Ask Gemini
def ask_gemini(state: ChatState):

    # Send question to Gemini
    response = llm.invoke(state["question"])

    # Store answer in state
    state["answer"] = response.content

    return state


# Print final answer
def display_answer(state: ChatState):

    print("\nQuestion:")
    print(state["question"])

    print("\nAnswer:")
    print(state["answer"])

    return state


# Create graph builder
builder = StateGraph(ChatState)

# Add nodes
builder.add_node("ask_gemini", ask_gemini)
builder.add_node("display_answer", display_answer)

# Connect nodes
builder.add_edge(START, "ask_gemini")
builder.add_edge("ask_gemini", "display_answer")
builder.add_edge("display_answer", END)

# Compile graph
app = builder.compile()

# Print graph
print(app.get_graph().draw_mermaid())

# Execute graph
app.invoke({
    "question": "What is Machine Learning?"
})