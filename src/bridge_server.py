from fastapi import FastAPI, HTTPException
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

class Command(BaseModel):
    action: str

# This stores the latest action
latest_gesture = {"action": "IDLE"}

@app.post("/command")
async def receive_command(cmd: Command):
    latest_gesture["action"] = cmd.action
    return {"status": "ok"}

@app.get("/get_action")
async def get_action():
    # After the browser reads it once, we reset it to IDLE for triggers
    action = latest_gesture["action"]
    if "TRIGGER" in action or "SWIPE" in action or "CAPTURE" in action:
        latest_gesture["action"] = "IDLE"
    return {"action": action}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)