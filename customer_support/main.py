
from typing import TypedDict
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm=ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0)

class Intent(BaseModel):
    intent:str=Field(description="One of: order, refund, technical, general")

classifier=llm.with_structured_output(Intent)

class SupportState(TypedDict):
    query:str
    intent:str
    response:str

def classify_intent(state:SupportState):
    prompt=f"""
You classify customer requests.
Return ONLY one intent:
- order
- refund
- technical
- general

Customer:
{state["query"]}
"""
    result=classifier.invoke(prompt)
    print("Intent:",result.intent)
    return {"intent":result.intent.strip().lower()}

def order_agent(state:SupportState):
    prompt=f"""You are an Order Support Specialist.
Help with tracking, shipping, delayed deliveries and order status.

Customer:
{state["query"]}"""
    return {"response":llm.invoke(prompt).content}

def refund_agent(state:SupportState):
    prompt=f"""You are a Refund Specialist.
Help with returns, refunds, damaged or wrong products.

Customer:
{state["query"]}"""
    return {"response":llm.invoke(prompt).content}

def technical_agent(state:SupportState):
    prompt=f"""You are a Technical Support Engineer.
Help diagnose login, payment, app and website problems.

Customer:
{state["query"]}"""
    return {"response":llm.invoke(prompt).content}

def general_agent(state:SupportState):
    prompt=f"""You are a friendly Customer Support Representative.

Customer:
{state["query"]}"""
    return {"response":llm.invoke(prompt).content}

def display_response(state:SupportState):
    print("\n=== FINAL RESPONSE ===\n")
    print(state["response"])
    return {}

def router(state:SupportState):
    intent=state["intent"]
    if intent in {"order","refund","technical","general"}:
        return intent
    return "general"

builder=StateGraph(SupportState)
builder.add_node("classify",classify_intent)
builder.add_node("order",order_agent)
builder.add_node("refund",refund_agent)
builder.add_node("technical",technical_agent)
builder.add_node("general",general_agent)
builder.add_node("display",display_response)

builder.add_edge(START,"classify")
builder.add_conditional_edges(
    "classify",
    router,
    {
        "order":"order",
        "refund":"refund",
        "technical":"technical",
        "general":"general",
    }
)

for n in ["order","refund","technical","general"]:
    builder.add_edge(n,"display")
builder.add_edge("display",END)

graph=builder.compile()

print(graph.get_graph().draw_mermaid())

tests=[
    "Where is my order? It hasn't arrived.",
    "I want to return my shoes.",
    "My payment keeps failing.",
    "Hello, I need some help."
]

for q in tests:
    print("\n"+"="*60)
    print("CUSTOMER:",q)
    graph.invoke({"query":q})
