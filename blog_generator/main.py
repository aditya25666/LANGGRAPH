# Load environment variables
from dotenv import load_dotenv

# Import TypedDict for state
from typing import TypedDict

# Import LangGraph
from langgraph.graph import StateGraph, START, END

# Import Gemini model
from langchain_google_genai import ChatGoogleGenerativeAI

# Load .env file
load_dotenv()

# Create Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)


# Define data shared between all nodes
class BlogState(TypedDict):
    topic: str
    outline: str
    blog: str


# Generate blog outline
def generate_outline(state: BlogState):

    # Create outline prompt
    prompt = f"""
    Create a detailed outline for a blog on:

    {state["topic"]}

    Include:
    - Title
    - Introduction
    - Main headings
    - Conclusion
    """

    # Call Gemini
    response = llm.invoke(prompt)

    # Save outline
    state["outline"] = response.content

    # Return updated state
    return state


# Generate blog using outline
def generate_blog(state: BlogState):

    # Create blog prompt
    prompt = f"""
    Write a complete blog using this outline.

    {state["outline"]}

    Make it:
    - Beginner friendly
    - Around 700 words
    - Simple English
    """

    # Call Gemini
    response = llm.invoke(prompt)

    # Save blog
    state["blog"] = response.content

    # Return updated state
    return state


# Display results
def display_blog(state: BlogState):

    print("\n=========== OUTLINE ===========\n")
    print(state["outline"])

    print("\n=========== BLOG ==============\n")
    print(state["blog"])

    return state


# Create graph builder
builder = StateGraph(BlogState)

# Register nodes
builder.add_node("generate_outline", generate_outline)
builder.add_node("generate_blog", generate_blog)
builder.add_node("display_blog", display_blog)

# Connect START to outline
builder.add_edge(START, "generate_outline")

# Connect outline to blog generation
builder.add_edge("generate_outline", "generate_blog")

# Connect blog generation to display
builder.add_edge("generate_blog", "display_blog")

# Connect display to END
builder.add_edge("display_blog", END)

# Compile graph
app = builder.compile()

# Print graph
print(app.get_graph().draw_mermaid())

# Execute graph
app.invoke({
    "topic": "What is Reinforcement Learning?"
})