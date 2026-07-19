# Import TypedDict to define the structure of our state
from typing import TypedDict

# Import the main LangGraph classes
from langgraph.graph import StateGraph, START, END


# ============================================================
# STEP 1: Define the State
# ============================================================

# Every LangGraph application has a "State".
# Think of State as a shared object or a global variable
# that every node (function) can read and update.

class State(TypedDict):
    # Our state contains one variable called 'message'
    message: str


# ============================================================
# STEP 2: Create a Node
# ============================================================

# A node is simply a Python function.
# It receives the current state,
# performs some work,
# and returns the updated state.

def hello_node(state: State):

    # Print a message to the console
    print("Hello LangGraph!")

    # Return the state.
    # Even if we don't modify it,
    # every node must return the state.
    return state


# ============================================================
# STEP 3: Create the Graph Builder
# ============================================================

# Create a graph builder.
# It knows what type of state our graph will use.

graph = StateGraph(State)


# ============================================================
# STEP 4: Add Nodes
# ============================================================

# Register our function as a node.

# Syntax:
# add_node("Node Name", Function)

graph.add_node("hello", hello_node)


# ============================================================
# STEP 5: Connect the Nodes
# ============================================================

# Every graph starts from START.

# START ---> hello

graph.add_edge(START, "hello")

# hello ---> END

graph.add_edge("hello", END)


# ============================================================
# STEP 6: Compile the Graph
# ============================================================

# Convert the graph builder into an executable graph.

app = graph.compile()


# ============================================================
# STEP 7: Execute the Graph
# ============================================================

# invoke() starts the execution.

# Since our state requires a "message",
# we pass one.

app.invoke({
    "message": "Hi"
})