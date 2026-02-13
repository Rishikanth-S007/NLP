// --- CONFIGURATION ---
const BRIDGE_URL = "http://127.0.0.1:8000";
const logContainer = document.getElementById('log-container');
let lastAction = "IDLE";

// --- 1. THREE.JS SCENE SETUP (Surgical Model) ---
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });

renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('threejs-container').appendChild(renderer.domElement);

// Create a placeholder surgical model (A Low-Poly Octahedron)
const geometry = new THREE.OctahedronGeometry(1, 0);
const material = new THREE.MeshPhongMaterial({
    color: 0x00f2ff,
    wireframe: true,
    emissive: 0x004444
});
const surgicalModel = new THREE.Mesh(geometry, material);
scene.add(surgicalModel);

// Lighting
const light = new THREE.PointLight(0xffffff, 1, 100);
light.position.set(10, 10, 10);
scene.add(light);
scene.add(new THREE.AmbientLight(0x404040));

camera.position.z = 3;

// --- 2. GESTURE INTERPRETER (The Bridge) ---
async function pollGestures() {
    try {
        const response = await fetch(`${BRIDGE_URL}/status`);
        const data = await response.json();
        const action = data.action;
        const text = data.text;
        const source = data.source;

        // If we have a voice command with text, we might want to log it specifically
        if (source === "voice" && text && action !== lastAction) {
            console.log(`Voice: ${text}`);
        }

        if (action !== "IDLE") {
            handleAction(action, text);
        }
    } catch (err) {
        console.warn("Waiting for Bridge Server...");
    }
}

function handleAction(action, text = "") {
    // 3D Model Manipulations
    switch (action) {
        case "ACTION_ROTATE":
            surgicalModel.rotation.y += 0.05;
            break;
        case "ACTION_ZOOM_IN":
            surgicalModel.scale.multiplyScalar(1.05);
            break;
        case "ACTION_ZOOM_OUT":
            surgicalModel.scale.multiplyScalar(0.95);
            break;
        case "ACTION_RESET":
            surgicalModel.rotation.set(0, 0, 0);
            surgicalModel.scale.set(1, 1, 1);
            break;
    }

    // UI Log Update (Only log if the action changed)
    if (action !== lastAction) {
        addLogEntry(action, text);
        lastAction = action;
    }
}

function addLogEntry(msg, text = "") {
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    const time = new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });

    // Clean up text (e.g., ACTION_ZOOM_IN -> ZOOM IN)
    const cleanMsg = msg.replace('ACTION_', '').replace('_', ' ');

    let finalHtml = `<span class="cyan">[${time}]</span> ${cleanMsg}`;
    if (text) {
        finalHtml += ` <small style="color: #aaa">"${text}"</small>`;
    }

    entry.innerHTML = finalHtml;
    logContainer.prepend(entry);

    // Keep the log clean
    if (logContainer.children.length > 8) {
        logContainer.removeChild(logContainer.lastChild);
    }
}

// --- 3. ANIMATION LOOPS ---
function animate() {
    requestAnimationFrame(animate);

    // Subtle auto-rotation when idle
    if (lastAction === "IDLE") {
        surgicalModel.rotation.y += 0.005;
    }

    renderer.render(scene, camera);
}

// Handle Window Resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// Initialization
animate();
setInterval(pollGestures, 100); // Poll every 100ms for responsiveness

// --- 4. SIMULATED VITALS ---
setInterval(() => {
    const hrValue = document.querySelector('.vital-card .value');
    if (hrValue) {
        let currentHR = parseInt(hrValue.innerText);
        let variance = Math.floor(Math.random() * 3) - 1;
        hrValue.innerHTML = `${currentHR + variance} <small>BPM</small>`;
    }
}, 2000);