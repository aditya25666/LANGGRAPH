
# Complete Phase 1 main.py
from typing import TypedDict
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
MAX_REVISIONS=3

llm=ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0.8)

class ReviewResult(BaseModel):
    approved: bool = Field(description="Ready to publish")
    score: int = Field(description="Score from 1 to 10")
    feedback: str = Field(description="Improvement suggestions")

review_llm=llm.with_structured_output(ReviewResult)

class TweetState(TypedDict):
    topic:str
    tweet:str
    approved:bool
    score:int
    feedback:str
    revision_count:int

def generate_tweet(state:TweetState):
    tweet=llm.invoke(f"""Write one engaging tweet about {state['topic']}.
Requirements:
- Under 280 characters
- Strong hook
- Clear and concise
Return only the tweet.""").content
    print("\nGenerated Tweet:\n",tweet)
    return {"tweet":tweet,"revision_count":0}

def review_tweet(state:TweetState):
    review=review_llm.invoke(f"""Review this tweet.

Approve only if it is engaging, clear and under 280 characters.

Tweet:
{state['tweet']}""")
    print(f"\nReview -> approved={review.approved}, score={review.score}")
    print("Feedback:",review.feedback)
    return {"approved":review.approved,"score":review.score,"feedback":review.feedback}

def improve_tweet(state:TweetState):
    improved=llm.invoke(f"""Improve this tweet using the feedback.

Tweet:
{state['tweet']}

Feedback:
{state['feedback']}

Return only the improved tweet.""").content
    print("\nImproved Tweet:\n",improved)
    return {"tweet":improved,"revision_count":state["revision_count"]+1}

def router(state:TweetState):
    if state["approved"] or state["revision_count"]>=MAX_REVISIONS:
        return "end"
    return "improve"

builder=StateGraph(TweetState)
builder.add_node("generate",generate_tweet)
builder.add_node("review",review_tweet)
builder.add_node("improve",improve_tweet)

builder.add_edge(START,"generate")
builder.add_edge("generate","review")
builder.add_edge("improve","review")

builder.add_conditional_edges(
    "review",
    router,
    {
        "improve":"improve",
        "end":END
    }
)

graph=builder.compile()

print(graph.get_graph().draw_mermaid())

result=graph.invoke({
    "topic":"Reinforcement Learning",
    "tweet":"",
    "approved":False,
    "score":0,
    "feedback":"",
    "revision_count":0
})

print("\nFinal Tweet:\n",result["tweet"])
print("Approved:",result["approved"])
print("Score:",result["score"])
print("Feedback:",result["feedback"])
print("Revisions:",result["revision_count"])
