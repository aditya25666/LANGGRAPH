# ==========================================================
#                    IMPORTS
# ==========================================================

# Loads environment variables from the .env file
from dotenv import load_dotenv

# Used to define the structure of the LangGraph state
from typing import TypedDict, Annotated

# Reducer used for merging lists from parallel nodes
from operator import add

# LangGraph
from langgraph.graph import StateGraph, START, END

# Gemini LLM
from langchain_google_genai import ChatGoogleGenerativeAI

# Pydantic models for structured output
from pydantic import BaseModel, Field


# ==========================================================
#             LOAD ENVIRONMENT VARIABLES
# ==========================================================

load_dotenv()


# ==========================================================
#                 CREATE GEMINI MODEL
# ==========================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)


# ==========================================================
#              PYDANTIC OUTPUT MODELS
# ==========================================================

class GrammarEvaluation(BaseModel):

    grammar_score: int = Field(
        description="Grammar score between 0 and 10"
    )

    grammar_feedback: str = Field(
        description="Feedback explaining the grammar score."
    )


class ClarityEvaluation(BaseModel):

    clarity_score: int = Field(
        description="Clarity score between 0 and 10"
    )

    clarity_feedback: str = Field(
        description="Feedback explaining the clarity score."
    )


class CreativityEvaluation(BaseModel):

    creativity_score: int = Field(
        description="Creativity score between 0 and 10"
    )

    creativity_feedback: str = Field(
        description="Feedback explaining the creativity score."
    )


# ==========================================================
#          CREATE STRUCTURED GEMINI MODELS
# ==========================================================

grammar_llm = llm.with_structured_output(
    GrammarEvaluation
)

clarity_llm = llm.with_structured_output(
    ClarityEvaluation
)

creativity_llm = llm.with_structured_output(
    CreativityEvaluation
)


# ==========================================================
#                  GRAPH STATE
# ==========================================================

class EssayState(TypedDict):

    # Input essay
    essay: str

    # Grammar Evaluation
    grammar_score: int
    grammar_feedback: str

    # Clarity Evaluation
    clarity_score: int
    clarity_feedback: str

    # Creativity Evaluation
    creativity_score: int
    creativity_feedback: str

    # Final Score
    overall_score: float

    # Shared logs (Reducer Example)
    logs: Annotated[list[str], add]


# ==========================================================
#              GRAMMAR EVALUATION NODE
# ==========================================================

def grammar_evaluator(state: EssayState):

    prompt = f"""
You are an expert English grammar evaluator.

Your task is to evaluate ONLY the grammar of the essay.

Ignore:
- Clarity
- Creativity
- Content Quality
- Writing Style

Evaluate grammar based on:

- Sentence structure
- Tense consistency
- Subject-verb agreement
- Punctuation
- Spelling
- Capitalization

Return:

1. Grammar score between 0 and 10
2. Constructive feedback

Essay:

{state["essay"]}
"""

    result = grammar_llm.invoke(prompt)

    return {

        "grammar_score": result.grammar_score,

        "grammar_feedback": result.grammar_feedback,

        "logs": [
            "✅ Grammar evaluation completed."
        ]
    }

# ==========================================================
#              CLARITY EVALUATION NODE
# ==========================================================

def clarity_evaluator(state: EssayState):

    prompt = f"""
You are an expert English writing evaluator.

Your task is to evaluate ONLY the clarity of the essay.

Ignore:
- Grammar
- Creativity
- Content Quality

Evaluate clarity based on:

- Ease of understanding
- Logical flow
- Sentence readability
- Organization of ideas
- Smooth transitions

Return:

1. Clarity score between 0 and 10
2. Constructive feedback

Essay:

{state["essay"]}
"""

    result = clarity_llm.invoke(prompt)

    return {

        "clarity_score": result.clarity_score,

        "clarity_feedback": result.clarity_feedback,

        "logs": [
            "✅ Clarity evaluation completed."
        ]
    }

# ==========================================================
#            CREATIVITY EVALUATION NODE
# ==========================================================

def creativity_evaluator(state: EssayState):

    prompt = f"""
You are an expert English writing evaluator.

Your task is to evaluate ONLY the creativity of the essay.

Ignore:
- Grammar
- Clarity
- Content Accuracy

Evaluate creativity based on:

- Originality
- Imagination
- Expression
- Interesting ideas
- Engagement

Return:

1. Creativity score between 0 and 10
2. Constructive feedback

Essay:

{state["essay"]}
"""

    result = creativity_llm.invoke(prompt)

    return {

        "creativity_score": result.creativity_score,

        "creativity_feedback": result.creativity_feedback,

        "logs": [
            "✅ Creativity evaluation completed."
        ]
    }

# ==========================================================
#              OVERALL EVALUATION NODE
# ==========================================================

def overall_evaluator(state: EssayState):

    overall_score = round(
        (
            state["grammar_score"] +
            state["clarity_score"] +
            state["creativity_score"]
        ) / 3,
        2
    )

    return {
        "overall_score": overall_score
    }

# ==========================================================
#                DISPLAY RESULT NODE
# ==========================================================

def display_result(state: EssayState):

    print("\n" + "=" * 60)
    print("            ESSAY EVALUATION REPORT")
    print("=" * 60)

    print("\nEssay:\n")
    print(state["essay"])

    print("\nGrammar")
    print("-" * 30)
    print(f"Score    : {state['grammar_score']}/10")
    print(f"Feedback : {state['grammar_feedback']}")

    print("\nClarity")
    print("-" * 30)
    print(f"Score    : {state['clarity_score']}/10")
    print(f"Feedback : {state['clarity_feedback']}")

    print("\nCreativity")
    print("-" * 30)
    print(f"Score    : {state['creativity_score']}/10")
    print(f"Feedback : {state['creativity_feedback']}")

    print("\nOverall Score")
    print("-" * 30)
    print(f"{state['overall_score']}/10")

    print("\nLogs")
    print("-" * 30)

    for log in state["logs"]:
        print(log)

    print("=" * 60)

    return {}

# ==========================================================
#                  BUILD THE GRAPH
# ==========================================================

builder = StateGraph(EssayState)

# ==========================
# Add Nodes
# ==========================

builder.add_node("grammar", grammar_evaluator)
builder.add_node("clarity", clarity_evaluator)
builder.add_node("creativity", creativity_evaluator)
builder.add_node("overall", overall_evaluator)
builder.add_node("display", display_result)

# ==========================
# Add Edges
# ==========================

# Fan-Out
builder.add_edge(START, "grammar")
builder.add_edge(START, "clarity")
builder.add_edge(START, "creativity")

# Fan-In
builder.add_edge(
    ["grammar", "clarity", "creativity"],
    "overall"
)

# Final Flow
builder.add_edge("overall", "display")
builder.add_edge("display", END)

# ==========================================================
#                 COMPILE THE GRAPH
# ==========================================================

graph = builder.compile()

# ==========================================================
#              PRINT GRAPH (OPTIONAL)
# ==========================================================

print(graph.get_graph().draw_mermaid())

# ==========================================================
#                 RUN THE GRAPH
# ==========================================================

graph.invoke(
    {
        "essay": """
The Impact of Artificial Intelligence on Education

Artificial Intelligence is changing the way students learn in schools and colleges. It helps teachers by reducing repetitive work and giving more time to focus on students. AI can also provide personalized learning, where every student learns according to their own speed and understanding.

However, there are also some challenges. Many students become too dependent on AI tools for completing their assignments, which reduce their critical thinking skills. Schools should teach students how to use AI responsibly instead of completely banning it. Teachers should guide students so they can use technology in a productive manner.

In my opinion, Artificial Intelligence is a powerful tool, but it should never replace teachers because human interaction, motivation, and emotional support are very important in education. If AI and teachers work together, the quality of education will become much better in the future.
"""
    }
)