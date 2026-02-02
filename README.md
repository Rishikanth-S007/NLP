Aether: Surgical Voice Assistant (NLP Engine)
This repository contains the Natural Language Processing (NLP) module for Aether, a multimodal surgical interface designed to assist healthcare professionals. The system enables hands-free control of 3D medical visualizations, allowing surgeons to manipulate digital models without breaking sterile field protocols.

Core Capabilities
The NLP module is built to provide low-latency, reliable performance in a clinical environment through three primary layers:

Wake Word Detection: Utilizes a custom-trained model for the trigger word "Aether," optimized for high accuracy in environments with background noise.

Local Transcription: Employs the Faster-Whisper (tiny.en) model for real-time, offline speech-to-text processing, ensuring patient data privacy by keeping audio processing local.

Surgical Command Logic: A robust mapping system using regular expressions to interpret various medical and directional terminologies into actionable system commands.

Communication Bridge: A centralized FastAPI server acts as the project's hub, broadcasting interpreted commands to the Computer Vision (CV) and User Interface (UI) modules.

Installation and Setup
To deploy this module within the Aether ecosystem, follow these steps:

Clone the Repository: git clone https://github.com/Rishikanth-S007/NLP.git

Configure Environment Variables: Create a .env file in the root directory and add your Picovoice API Key: PICOVOICE_API_KEY=your_key_here

Install Dependencies: Ensure your virtual environment is active, then run: pip install -r requirements.txt

Add Custom Models: Place the platform-specific aether.ppn wake-word file into the src/models/ directory.

Integration Architecture
The system operates as a distributed service. Other modules (CV and UI) can interact with the NLP engine through the following local API endpoints:

POST /command: The voice engine sends detected actions and full transcripts to this endpoint.

GET /status: Returns the most recent system action and transcript, allowing other modules to synchronize their state with user intent.
