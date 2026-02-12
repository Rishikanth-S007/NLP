// 1. --- CONFIGURATION & STATE ---
const SERVER_URL = "http://localhost:8000/status";
const logContainer = document.getElementById('log-container');
const voiceTranscript = document.getElementById('voice-transcript');
const pinchIcon = document.getElementById('pinch-icon');

// 2. --- HUB SYNCHRONIZATION (POLLING) ---
async function fetchSystemStatus() {
    try {
        const response = await fetch(SERVER_URL);
        const data = await response.json();

        // Update Voice Display
        if (data.last_transcript) {
            voiceTranscript.innerText = `"${data.last_transcript}"`;
        }

        // Update Action Log on new Trigger
        if (data.action !== "IDLE" && data.action !== "NONE") {
            updateActionLog(data.action);
        }

        // Visual Feedback for Gestures
        updateGestureUI(data.action);

        // Optional: Link 3D Rotation to specific gestures
        handle3DRotation(data.action);

    } catch (error) {
        console.error("Connection to Bridge Server failed. Ensure main.py is running.");
    }
}

function updateActionLog(action) {
    const entry = document.createElement('div');
    entry.className = "log-entry";
    const timestamp = new Date().toLocaleTimeString([], { hour12: false });
    
    // Styling matches your Figma design
    entry.innerHTML = `<span class="gray">[${timestamp}]</span> <span class="lime">[TRIGGER]</span> ${action}`;
    
    logContainer.prepend(entry);
    if (logContainer.children.length > 10) logContainer.removeChild(logContainer.lastChild);
}

function updateGestureUI(action) {
    if(action === "PINCH") {
        pinchIcon.style.backgroundColor = "var(--cyan)";
        pinchIcon.style.boxShadow = "0 0 15px var(--cyan)";
    } else {
        pinchIcon.style.backgroundColor = "transparent";
        pinchIcon.style.boxShadow = "none";
    }
}

// 3. --- THREE.JS 3D ENGINE ---
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });

renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.getElementById('threejs-container').appendChild(renderer.domElement);

// Setup Lighting for Medical Models
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);
const pointLight = new THREE.PointLight(0x00f2ff, 1);
pointLight.position.set(5, 5, 5);
scene.add(pointLight);

// Placeholder Object (Replace with GLTFLoader for your heart.glb)
const geometry = new THREE.IcosahedronGeometry(2, 1);
const material = new THREE.MeshBasicMaterial({ 
    color: 0x00f2ff, 
    wireframe: true,
    transparent: true,
    opacity: 0.8
});
const medicalModel = new THREE.Mesh(geometry, material);
scene.add(medicalModel);

camera.position.z = 5;

// 4. --- ANIMATION & INTERACTION ---
function handle3DRotation(action) {
    // Example: Rotate the model based on specific gesture inputs
    if (action === "ROTATE_LEFT") medicalModel.rotation.y -= 0.05;
    if (action === "ROTATE_RIGHT") medicalModel.rotation.y += 0.05;
    if (action === "ZOOM_IN") camera.position.z -= 0.1;
    if (action === "ZOOM_OUT") camera.position.z += 0.1;
}

function animate() {
    requestAnimationFrame(animate);
    
    // Constant subtle rotation for "Live" effect
    medicalModel.rotation.y += 0.002;
    
    renderer.render(scene, camera);
}

// Handle Window Resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// 5. --- START SYSTEM ---
animate();
setInterval(fetchSystemStatus, 100); // Poll server every 100ms