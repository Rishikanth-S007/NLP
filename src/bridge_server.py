from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow the browser to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Unified state for the UI to "pull" from
current_state = {
    "action": "IDLE",
    "last_transcript": "Waiting for command...",
    "system_status": "ONLINE"
}

class Command(BaseModel):
    action: str
    text: str = "" # Default to empty if not provided

@app.get("/")
def read_root():
    return {"message": "Nova Surgical Hub is Active"}

# Endpoint for both Gesture and Voice logic to send data
@app.post("/command")
async def receive_command(cmd: Command):
    current_state["action"] = cmd.action
    if cmd.text:
        current_state["last_transcript"] = cmd.text
    print(f"📢 Hub received: {cmd.action} | {cmd.text}")
    return {"status": "ok"}

# The UI Lead (app.js) calls this to update your Figma design
@app.get("/status")
async def get_status():
    action = current_state["action"]
    
    # After the browser reads a "one-time" trigger, reset it
    triggers = ["TRIGGER", "SWIPE", "CAPTURE", "MEASURE"]
    if any(t in action for t in triggers):
        current_state["action"] = "IDLE"
        
    return current_state

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)