from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
import time

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared State
class SystemState:
    def __init__(self):
        self.last_action = "IDLE"
        self.last_text = ""
        self.timestamp = 0
        self.source = ""

state = SystemState()

class Command(BaseModel):
    action: str
    text: str = ""
    source: str = "unknown"

@app.get("/status")
async def get_status():
    """Frontend polls this to get the latest state."""
    # Auto-reset after 2s
    age = time.time() - state.timestamp
    if age > 2.0:
        state.last_action = "IDLE"
        state.last_text = ""
        state.source = ""
    
    return {
        "action": state.last_action,
        "text": state.last_text,
        "source": state.source,
        "age": age
    }

@app.post("/command")
async def receive_command(cmd: Command):
    """Voice and Gesture engines push data here."""
    state.last_action = cmd.action
    state.last_text = cmd.text
    state.source = cmd.source
    state.timestamp = time.time()
    
    print(f"[{cmd.source.upper()}] Cmd: {cmd.action} | Text: {cmd.text}")
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)