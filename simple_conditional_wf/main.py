# ==========================================================
#                    IMPORTS
# ==========================================================

from typing import TypedDict

from langgraph.graph import StateGraph, START, END


# ==========================================================
#                    STATE
# ==========================================================

class StudentState(TypedDict):

    name: str

    marks: int

    result: str


# ==========================================================
#                  CHECK MARKS NODE
# ==========================================================

def check_marks(state: StudentState):

    print(f"\nChecking marks for {state['name']}...")
    print(f"Marks : {state['marks']}")

    # No state update required
    return {}


# ==========================================================
#                  PASS NODE
# ==========================================================

def pass_node(state: StudentState):

    print("\n Student Passed")

    return {
        "result": "PASS"
    }


# ==========================================================
#                  FAIL NODE
# ==========================================================

def fail_node(state: StudentState):

    print("\n Student Failed")

    return {
        "result": "FAIL"
    }


# ==========================================================
#              ROUTING FUNCTION
# ==========================================================

def decide_result(state: StudentState):

    if state["marks"] >= 40:
        return "pass"

    return "fail"


# ==========================================================
#                  BUILD GRAPH
# ==========================================================

builder = StateGraph(StudentState)

# Add Nodes
builder.add_node("check", check_marks)
builder.add_node("pass", pass_node)
builder.add_node("fail", fail_node)

# Start Edge
builder.add_edge(START, "check")

# Conditional Edge
builder.add_conditional_edges(
    "check",
    decide_result,
    {
        "pass": "pass",
        "fail": "fail"
    }
)

# End Edges
builder.add_edge("pass", END)
builder.add_edge("fail", END)


# ==========================================================
#                 COMPILE GRAPH
# ==========================================================

graph = builder.compile()


# ==========================================================
#             PRINT MERMAID DIAGRAM
# ==========================================================

print(graph.get_graph().draw_mermaid())


# ==========================================================
#               RUN THE GRAPH
# ==========================================================

result = graph.invoke(
    {
        "name": "Aditya",
        "marks": 75
    }
)


# ==========================================================
#                 FINAL STATE
# ==========================================================

print("\nFinal State")
print(result)