Helix: A Multi-Modal Control Interface
Integrating Voice Intelligence and Spatial Computer Vision

Helix is a multi-modal interface designed to facilitate hands-free interaction with digital environments. By combining Natural Language Processing for vocal commands and high-fidelity skeletal tracking for hand gestures, this system provides a seamless way to navigate 3D models and complex datasets without traditional input devices.

Core Capabilities
Spatial Gesture Engine
The gesture recognition system is built on a skeletal tracking architecture that translates hand movements into specific system actions:

Dynamic Manipulation: Use a pinch gesture to zoom in and out or hold a pinch to rotate 3D objects along their axis.

Navigation: A two-finger vertical movement (Index and Middle fingers) enables scrolling through data or layers.

Control Commands: Rapid horizontal movements trigger swipes to switch between files, while a full palm extension resets the environment to its default state.

Data Capture: A specific pinky-extension gesture triggers an instantaneous system screenshot, which is saved locally for review.

Voice Intelligence
The NLP component allows for the execution of system-level commands through speech. This ensures that the user can switch modes, query data, or trigger complex workflows while their hands are occupied with spatial tasks.

System Architecture
The project is structured into distinct modules to ensure scalability and ease of integration:

Engine: Contains the core skeletal tracking logic that processes camera frames into coordinate data.

Logic: The mathematical layer that interprets coordinate changes as specific human gestures.

Bridge: A FastAPI-based server that acts as the communication layer, transmitting gestures from Python to the visual interface.

Frontend: A web-based 3D visualizer built with Three.js that provides real-time feedback for all interactions.

Source: Contains the primary execution scripts for both the gesture engine and the communication bridge.

Installation and Execution
Environment Configuration: Initialize a virtual environment and install the necessary dependencies:

Bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
System Launch: To run the full suite, execute the following components in separate terminal instances:

Communication Bridge: python src/bridge_server.py

Gesture Engine: python src/gesture_main.py

Interface Access: Open frontend/index.html in a web browser to view the 3D environment and begin spatial interaction.

Project Vision
Helix was developed to address the need for sterile, hands-free control in environments such as medical imaging suites and engineering laboratories. The goal is to reduce the friction between user intent and software response, creating a more intuitive relationship between the human and the machine.
