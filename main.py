'''
Build a small system where users can submit support tickets. 
An AI agent should triage each ticket — classify it, suggest a priority, 
and write a short summary. A human must approve the agent's suggestion before it is saved.
'''

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title = 'Ticket Triage')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_methods=['*'],
    allow_headers=['*']
)
class TicketCreate(BaseModel):
  title: str
  description: str
  created_by: int

class TicketOut(TicketCreate):
  id: int
  status: str = 'open'
  category: Optional[str] = None
  priority: Optional[str] = None
  suggested_category: Optional[str] = None
  suggested_priority: Optional[str] = None
  ai_summary: Optional[str]=None

tickets = []
next_id = 1

def fake_Triage(title: str, description: str) -> dict:
  text = title + " " + description

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

def find_ticket(ticket_id: int) -> TicketOut:
    for t in tickets:
        if t.id == ticket_id:
            return t
    raise HTTPException(status_code=404, detail="Ticket not found")

@app.post("/tickets", response_model=TicketOut, status_code=201)
def create_ticket(payload:TicketCreate):
    global next_id
    ticket = TicketOut(id=next_id, **payload.model_dump())
    next_id +=1
    tickets.append(ticket)
    return ticket

@app.get("/tickets", response_model=list[TicketOut])
def list_tickets(status: Optional[str] = None, search: Optional[str] = None):
    result = tickets
    if status is not None:
        result = [t for t in result if t.status == status]
    if search:
        q = search.lower()
        result = [t for t in result
                  if q in t.title.lower() or q in t.description.lower()]
    return result

@app.post("/tickets/{ticket_id}/triage", response_model=TicketOut)
def triage_ticket(ticket_id: int):
    ticket = find_ticket(ticket_id)
    result = fake_Triage(ticket.title, ticket.description)

    ticket.suggested_category = result['category']
    ticket.suggested_priority = result['priority']
    ticket.ai_summary = result['summary']
    ticket.status = 'needs_review'
    return ticket

@app.post("/tickets/{ticket_id}/approve", response_model=TicketOut)
def approve_ticket(ticket_id: int):
    ticket = find_ticket(ticket_id)
    if ticket.status != "needs_review":
        raise HTTPException(status_code=400, detail="Ticket has not been triaged yet")

    ticket.category = ticket.suggested_category
    ticket.priority = ticket.suggested_priority
    ticket.status = "assigned"
    return ticket



  

