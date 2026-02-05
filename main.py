from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse 
from agent import run_conversation

from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_input: str
    mem0_user_id: str
    mem0_session_id: str
    signed_in: bool

app = FastAPI()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data["user_input"]
    mem0_user_id = data["mem0_user_id"]
    mem0_session_id = data["mem0_session_id"]
    signed_in = data["signed_in"]
    return HTMLResponse(run_conversation(user_input, mem0_user_id, mem0_session_id, signed_in))

@app.get("/")
async def root():
    return HTMLResponse("<h1>Welcome to DHs 2026!</h1><p>How can I assist you today?</p>")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
