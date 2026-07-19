from typing import TypedDict

from langgraph.graph import StateGraph, START, END


# ==========================================================
#                       STATE
# ==========================================================

class GuessState(TypedDict):

    secret_number: int

    current_guess: int

    attempts: int


# ==========================================================
#                  GENERATE GUESS NODE
# ==========================================================

def generate_guess(state: GuessState):

    new_guess = state["current_guess"] + 1

    new_attempts = state["attempts"] + 1

    print("\n==============================")
    print(f"Attempt : {new_attempts}")
    print(f"Guess   : {new_guess}")

    return {

        "current_guess": new_guess,

        "attempts": new_attempts

    }


# ==========================================================
#                    CHECK GUESS NODE
# ==========================================================

def check_guess(state: GuessState):

    print("Checking Guess...")

    if state["current_guess"] == state["secret_number"]:

        print("✅ Correct Guess!")

    else:

        print("❌ Wrong Guess")

    return {}


# ==========================================================
#                     ROUTER
# ==========================================================

def guess_router(state: GuessState):

    if state["current_guess"] == state["secret_number"]:

        return "correct"

    return "retry"


# ==========================================================
#                    BUILD GRAPH
# ==========================================================

builder = StateGraph(GuessState)

builder.add_node("generate_guess", generate_guess)

builder.add_node("check_guess", check_guess)


builder.add_edge(
    START,
    "generate_guess"
)

builder.add_edge(
    "generate_guess",
    "check_guess"
)


builder.add_conditional_edges(

    "check_guess",

    guess_router,

    {

        "correct": END,

        "retry": "generate_guess"

    }

)


graph = builder.compile()


# ==========================================================
#                 PRINT GRAPH
# ==========================================================

print(graph.get_graph().draw_mermaid())


# ==========================================================
#                    RUN GRAPH
# ==========================================================

result = graph.invoke(

    {

        "secret_number": 5,

        "current_guess": 0,

        "attempts": 0

    }

)


print("\n==============================")
print("FINAL STATE")
print("==============================")

print(result)