from fastapi import FastAPI
from pydantic import BaseModel
from agent import run_conversation

app = FastAPI()

class ChatRequest(BaseModel):
    user_input: str
    mem0_user_id: str
    mem0_session_id: str
    signed_in: bool | None = None

@app.get("/")
async def root():
    return {"message": "Working..."}

@app.post("/chat")
async def chat(request: ChatRequest):
    response = await run_conversation(
        request.user_input, 
        request.mem0_user_id, 
        request.mem0_session_id, 
        request.signed_in
    )
    return {
        "user_input": request.user_input,
        "response": response
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
