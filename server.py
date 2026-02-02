from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# This stores the latest command so the UI can "pull" it
current_state = {
    "last_action": "NONE",
    "last_transcript": "",
    "system_status": "READY"
}

class VoiceCommand(BaseModel):
    action: str
    text: str

@app.get("/")
def read_root():
    return {"message": "Aether Central Hub is Active"}

@app.post("/command")
def receive_command(cmd: VoiceCommand):
    global current_state
    current_state["last_action"] = cmd.action
    current_state["last_transcript"] = cmd.text
    print(f"📢 Hub received: {cmd.action} ('{cmd.text}')")
    return {"status": "success", "received": cmd.action}

@app.get("/status")
def get_status():
    # The UI Lead will call this every 100ms to see what to do
    return current_state

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)