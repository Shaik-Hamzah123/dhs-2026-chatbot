from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from agent import run_conversation
from pydantic import BaseModel
import os

class ChatRequest(BaseModel):
    user_input: str
    mem0_user_id: str
    mem0_session_id: str
    signed_in: bool
    image_data: str | None = None

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data["user_input"]
    mem0_user_id = data["mem0_user_id"]
    mem0_session_id = data["mem0_session_id"]
    signed_in = data["signed_in"]
    image_data = data.get("image_data")
    return HTMLResponse(await run_conversation(user_input, mem0_user_id, mem0_session_id, signed_in, image_data))

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
