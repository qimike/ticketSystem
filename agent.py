from typing import TypedDict, Optional
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command


def fake_triage(title: str, description: str) -> dict:
  text = (title + " " + description).lower()

  if "login" in text or "password" in text or "sso" in text:
     category = "account_access"
  elif "payment" in text or "charge" in text or "refund" in text:
     category = "billing"
  elif "crash" in text or "error" in text or "500" in text:
     category = "bug"
  else:
     category = 'general'

  if "urgent" in text or "down" in text or "cannot" in text or "500" in text:
        priority = "high"
  elif "question" in text or "how to" in text:
        priority = "low"
  else:
        priority = "medium"

  summary = f"User reports '{title}', auto-classified as {category}"
  return {"category": category, "priority": priority, "summary": summary}

# 1) State：整张图共享的一块白板，每个节点往上读/写
class TriageState(TypedDict):
    title: str
    description: str
    suggested_category: Optional[str]
    suggested_priority: Optional[str]
    ai_summary: Optional[str]
    approved: Optional[bool]
    final_category: Optional[str]
    final_priority: Optional[str]

# 2) LLM 的输出格式先用 Pydantic 定死 —— 模型只能按这个结构回，不许自由发挥
class TriageResult(BaseModel):
    category: str        # account_access / billing / bug / general
    priority: str        # high / medium / low
    summary: str

def classify(state: TriageState):
    # 生产版就这一行是真的：
    #   result = llm.with_structured_output(TriageResult).invoke(
    #       f"Title: {state['title']}\nDescription: {state['description']}")
    result = fake_triage(state["title"], state["description"])  # 先用假的占位
    return {
        "suggested_category": result["category"],
        "suggested_priority": result["priority"],
        "ai_summary": result["summary"],
    }

def human_review(state: TriageState):
    # interrupt() = 在这里把整张图冻住，状态存进 checkpointer，等人来处理
    decision = interrupt({
        "suggested_category": state["suggested_category"],
        "suggested_priority": state["suggested_priority"],
        "ai_summary": state["ai_summary"],
    })
    return {"approved": bool(decision)}

def save(state: TriageState):
    # 人 approve 之后才执行：把建议复制进正式字段 —— 和你 FastAPI 版 approve 端点干的事一模一样
    return {
        "final_category": state["suggested_category"],
        "final_priority": state["suggested_priority"],
    }

def route_after_review(state: TriageState):
    return "save" if state["approved"] else END

graph = StateGraph(TriageState)
graph.add_node("classify", classify)
graph.add_node("human_review", human_review)
graph.add_node("save", save)
graph.add_edge(START, "classify")
graph.add_edge("classify", "human_review")
graph.add_conditional_edges("human_review", route_after_review, ["save", END])
graph.add_edge("save", END)

triage_graph = graph.compile(checkpointer=InMemorySaver())
