# Import TypedDict to define the structure of the state
from typing import TypedDict

# Import LangGraph components
from langgraph.graph import StateGraph, START, END


# Define the data that will flow through the graph
class BMIState(TypedDict):
    height: float
    weight: float
    bmi: float
    category: str


# Calculate BMI using height and weight
def calculate_bmi(state: BMIState):

    # Calculate BMI
    bmi = state["weight"] / (state["height"] ** 2)

    # Store BMI in the state
    state["bmi"] = round(bmi, 2)

    # Return updated state
    return state


# Determine BMI category
def classify_bmi(state: BMIState):

    # Get BMI from state
    bmi = state["bmi"]

    # Check BMI range
    if bmi < 18.5:
        state["category"] = "Underweight"

    elif bmi < 25:
        state["category"] = "Normal Weight"

    elif bmi < 30:
        state["category"] = "Overweight"

    else:
        state["category"] = "Obese"

    # Return updated state
    return state


# Display the final result
def display_result(state: BMIState):

    # Print height
    print(f"Height   : {state['height']} m")

    # Print weight
    print(f"Weight   : {state['weight']} kg")

    # Print BMI
    print(f"BMI      : {state['bmi']}")

    # Print category
    print(f"Category : {state['category']}")

    # Return state
    return state


# Create a graph builder
builder = StateGraph(BMIState)

# Register all nodes
builder.add_node("calculate_bmi", calculate_bmi)
builder.add_node("classify_bmi", classify_bmi)
builder.add_node("display_result", display_result)

# Connect START to first node
builder.add_edge(START, "calculate_bmi")

# Connect first node to second node
builder.add_edge("calculate_bmi", "classify_bmi")

# Connect second node to third node
builder.add_edge("classify_bmi", "display_result")

# Connect last node to END
builder.add_edge("display_result", END)

# Compile the graph
app = builder.compile()

# Print graph structure in Mermaid format
#print(app.get_graph().draw_mermaid())

# Execute the graph with input data
app.invoke({
    "height": 1.75,
    "weight": 70
})