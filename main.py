from fastapi import FastAPI, Request
from typing import List, Dict
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from agent import run_conversation
from pydantic import BaseModel
import os

class ChatRequest(BaseModel):
    user_input: str
    mem0_user_id: str
    mem0_session_id: str
    signed_in: bool | None = None
    image_data: str | None = None
    messages: List[Dict[str, str]] | None = None

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.post("/chat")
async def chat(request: ChatRequest):
    user_input = request.user_input
    mem0_user_id = request.mem0_user_id
    mem0_session_id = request.mem0_session_id
    if mem0_user_id:
        signed_in = True
    else:
        signed_in = False
    image_data = request.image_data
    history = request.messages
    return HTMLResponse(await run_conversation(user_input, mem0_user_id, mem0_session_id, signed_in, image_data, history))

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
