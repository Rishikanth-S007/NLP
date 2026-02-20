// --- CONFIGURATION ---
const BRIDGE_URL = "http://127.0.0.1:8000";
const logContainer = document.getElementById('log-container');
const waveformContainer = document.getElementById('waveform');
let lastAction = "IDLE";

// --- 1. UI INITIALIZATION (Waveform) ---
function initWaveform() {
    for (let i = 0; i < 40; i++) {
        const bar = document.createElement('div');
        bar.className = 'waveform-bar';
        waveformContainer.appendChild(bar);
    }
}

function updateWaveform() {
    const bars = document.querySelectorAll('.waveform-bar');
    bars.forEach(bar => {
        const height = Math.random() * 80 + 10;
        bar.style.height = `${height}%`;
        bar.style.opacity = Math.random() * 0.5 + 0.5;
    });
}

// --- 2. THREE.JS SCENE SETUP (Surgical Model) ---
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });

renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.getElementById('threejs-container').appendChild(renderer.domElement);

// HUD Scene Assets (Radar Grid)
const gridHelper = new THREE.GridHelper(10, 20, 0x00f2ff, 0x004444);
gridHelper.position.y = -2;
gridHelper.material.transparent = true;
gridHelper.material.opacity = 0.2;
scene.add(gridHelper);

// Circular "Radar" segments
const ringGeo = new THREE.RingGeometry(1.8, 1.82, 64);
const ringMat = new THREE.MeshBasicMaterial({ color: 0x00f2ff, transparent: true, opacity: 0.3, side: THREE.DoubleSide });
const ring = new THREE.Mesh(ringGeo, ringMat);
ring.rotation.x = Math.PI / 2;
scene.add(ring);

let surgicalModel = new THREE.Group();
scene.add(surgicalModel);

// Load the Heart Model
const loader = new THREE.GLTFLoader();
loader.load(
    'assets/heart.glb',
    function (gltf) {
        const heart = gltf.scene;
        const box = new THREE.Box3().setFromObject(heart);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());

        heart.position.x += (heart.position.x - center.x);
        heart.position.y += (heart.position.y - center.y);
        heart.position.z += (heart.position.z - center.z);

        const maxDim = Math.max(size.x, size.y, size.z);
        const scale = 2.5 / maxDim;
        heart.scale.set(scale, scale, scale);

        // Holographic Shader-like Material
        const holographicMaterial = new THREE.MeshPhongMaterial({
            color: 0x00f2ff,
            emissive: 0x004444,
            specular: 0xffffff,
            shininess: 100,
            transparent: true,
            opacity: 0.7,
            wireframe: false
        });

        heart.traverse((node) => {
            if (node.isMesh) {
                node.material = holographicMaterial;
            }
        });

        surgicalModel.add(heart);
        addLogEntry("HEART MODEL", "Assets mapped to GPU");
    },
    undefined,
    function (error) {
        console.warn("Heart model fallback triggered.");
        const geometry = new THREE.OctahedronGeometry(1.2, 2);
        const material = new THREE.MeshPhongMaterial({ color: 0x00f2ff, wireframe: true });
        surgicalModel.add(new THREE.Mesh(geometry, material));
    }
);

// Lighting
const mainLight = new THREE.PointLight(0xffffff, 1.5, 100);
mainLight.position.set(5, 5, 5);
scene.add(mainLight);
scene.add(new THREE.AmbientLight(0x404040, 2));

camera.position.z = 5;

// --- 3. GESTURE & BRIDGE LOGIC ---
async function pollGestures() {
    try {
        const response = await fetch(`${BRIDGE_URL}/status`);
        const data = await response.json();
        if (data.action !== "IDLE") handleAction(data.action, data.text);
    } catch (err) {
        // Silent fail for dev
    }
}

function handleAction(action, text = "") {
    const voiceModule = document.querySelector('.voice-module');
    const transcript = document.getElementById('voice-transcript');

    // Reset listening state if a command is processed or IDLE
    if (action !== "STATUS_HEARING" && action !== "IDLE") {
        voiceModule.classList.remove('listening');
    }

    switch (action) {
        case "STATUS_HEARING":
            voiceModule.classList.add('listening');
            if (transcript) transcript.innerText = "Hearing...";
            break;
        case "ACTION_ROTATE":
            surgicalModel.rotation.y += 0.08; // Slightly faster rotation
            highlightGesture('gesture-rotate');
            break;
        case "ACTION_ZOOM_IN":
            surgicalModel.scale.multiplyScalar(1.05); // 5% instead of 2%
            highlightGesture('gesture-zoom');
            break;
        case "ACTION_ZOOM_OUT":
            surgicalModel.scale.multiplyScalar(0.95); // 5% instead of 2%
            highlightGesture('gesture-zoom');
            break;
        case "ACTION_RESET":
            surgicalModel.rotation.set(0, 0, 0);
            surgicalModel.scale.set(1, 1, 1);
            highlightGesture('gesture-reset');
            break;
        case "ACTION_CAPTURE":
            highlightGesture('gesture-capture');
            break;
    }

    if (action !== lastAction) {
        if (action !== "STATUS_HEARING") {
            addLogEntry(action, text);
            if (transcript && text) transcript.innerText = `"${text}"`;
        }
        lastAction = action;
        // Visual feedback on waveform
        updateWaveform();
    }
}

function highlightGesture(elementId) {
    const el = document.getElementById(elementId);
    if (!el) return;

    el.classList.add('gesture-active');
    // Clear after a brief period (gesture duration)
    clearTimeout(el.highlightTimeout);
    el.highlightTimeout = setTimeout(() => el.classList.remove('gesture-active'), 1200);
}

function addLogEntry(msg, details = "") {
    const entry = document.createElement('div');
    entry.className = 'log-entry new';
    const time = new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });

    const cleanMsg = msg.replace('ACTION_', '').replace('_', ' ');
    entry.innerHTML = `<span style="color:var(--cyan)">[${time}]</span> ${cleanMsg} <small style="display:block; opacity:0.5">${details}</small>`;

    logContainer.prepend(entry);
    setTimeout(() => entry.classList.remove('new'), 2000);

    if (logContainer.children.length > 12) logContainer.removeChild(logContainer.lastChild);
}

// --- 4. ANIMATION & UPDATES ---
function animate() {
    requestAnimationFrame(animate);

    if (lastAction === "IDLE") {
        surgicalModel.rotation.y += 0.005;
    }

    // Pulse the grid
    gridHelper.material.opacity = 0.1 + Math.sin(Date.now() * 0.002) * 0.05;
    ring.rotation.z += 0.01;

    renderer.render(scene, camera);
}

// Handle Window Resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// Vitals Simulation
function updateVitals() {
    const hr = document.getElementById('hr-value');
    if (hr) hr.innerText = 70 + Math.floor(Math.random() * 5);

    const ox = document.getElementById('ox-value');
    if (ox) ox.innerText = 97 + Math.floor(Math.random() * 3);
}

// Start everything
initWaveform();
animate();
setInterval(updateWaveform, 150);
setInterval(pollGestures, 100);
setInterval(updateVitals, 3000);
