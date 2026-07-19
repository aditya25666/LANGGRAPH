# Import TypedDict
from typing import TypedDict

# Import LangGraph
from langgraph.graph import StateGraph, START, END


# Define shared state
class MathState(TypedDict):
    number: int
    square: int
    cube: int


# Calculate square
def calculate_square(state: MathState):

    # Get input number
    number = state["number"]

    # Return only updated key
    return {
        "square": number ** 2
    }


# Calculate cube
def calculate_cube(state: MathState):

    # Get input number
    number = state["number"]

    # Return only updated key
    return {
        "cube": number ** 3
    }


# Display result
def display_result(state: MathState):

    print(f"Number : {state['number']}")
    print(f"Square : {state['square']}")
    print(f"Cube   : {state['cube']}")

    return {}


# Create graph
builder = StateGraph(MathState)

# Register nodes
builder.add_node("square", calculate_square)
builder.add_node("cube", calculate_cube)
builder.add_node("display", display_result)

# Fan-Out
builder.add_edge(START, "square")
builder.add_edge(START, "cube")

# Fan-In
builder.add_edge("square", "display")
builder.add_edge("cube", "display")

# Connect to END
builder.add_edge("display", END)

# Compile graph
app = builder.compile()

# Print graph
print(app.get_graph().draw_mermaid())

# Execute graph
app.invoke({
    "number": 5
})