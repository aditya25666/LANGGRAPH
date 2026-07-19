# Load environment variables
from dotenv import load_dotenv

# Import TypedDict
from typing import TypedDict

# Import LangGraph
from langgraph.graph import StateGraph, START, END

# Import Gemini
from langchain_google_genai import ChatGoogleGenerativeAI

# Load .env file
load_dotenv()

# Create Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)


# Define the shared state
class ContentState(TypedDict):
    topic: str
    summary: str
    keywords: str


# Generate a summary
def generate_summary(state: ContentState):

    # Create prompt
    prompt = f"""
    Write a short summary about:

    {state["topic"]}
    """

    # Call Gemini
    response = llm.invoke(prompt)

    # Return only the updated key
    return {
        "summary": response.content
    }


# Generate SEO keywords
def generate_keywords(state: ContentState):

    # Create prompt
    prompt = f"""
    Generate 10 SEO keywords for:

    {state["topic"]}

    Return only comma-separated keywords.
    """

    # Call Gemini
    response = llm.invoke(prompt)

    # Return only the updated key
    return {
        "keywords": response.content
    }


# Display the final result
def display_result(state: ContentState):

    print("\n========== TOPIC ==========\n")
    print(state["topic"])

    print("\n========== SUMMARY ==========\n")
    print(state["summary"])

    print("\n========== KEYWORDS ==========\n")
    print(state["keywords"])

    # No updates, so return an empty dictionary
    return {}


# Create graph builder
builder = StateGraph(ContentState)

# Register nodes
builder.add_node("summary", generate_summary)
builder.add_node("keywords", generate_keywords)
builder.add_node("display", display_result)

# Fan-Out (Parallel Execution)
builder.add_edge(START, "summary")
builder.add_edge(START, "keywords")

# Fan-In (Merge Results)
builder.add_edge("summary", "display")
builder.add_edge("keywords", "display")

# Connect to END
builder.add_edge("display", END)

# Compile graph
app = builder.compile()

# Print graph structure
print(app.get_graph().draw_mermaid())

# Execute graph
app.invoke({
    "topic": "Artificial Intelligence in Healthcare"
})