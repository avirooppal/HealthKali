// Interactive 3D Body Model for Cancer Digital Twin

let scene, camera, renderer, controls;
let bodyModel = {};
let tumor = null;

// Initialize the 3D scene
function initBodyModel(containerId = 'bodyModelContainer') {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container ${containerId} not found`);
        return false;
    }

    // Set up scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);

    // Set up camera
    const width = container.clientWidth;
    const height = container.clientHeight || 400;
    camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.z = 30;

    // Set up renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(0, 1, 1).normalize();
    scene.add(directionalLight);

    // Create the body model
    createBodyModel();

    // Add controls if OrbitControls is available
    if (typeof THREE.OrbitControls !== 'undefined') {
        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.25;
        controls.screenSpacePanning = false;
        controls.maxPolarAngle = Math.PI / 1.5;
        controls.minDistance = 20;
        controls.maxDistance = 50;
    }

    // Handle window resize
    window.addEventListener('resize', () => {
        if (container) {
            const width = container.clientWidth;
            const height = container.clientHeight || 400;
            
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
            renderer.setSize(width, height);
        }
    });

    // Start animation loop
    animate();
    return true;
}

// Create body model components
function createBodyModel() {
    // Create torso
    const bodyGeometry = new THREE.CylinderGeometry(5, 3, 14, 32);
    const bodyMaterial = new THREE.MeshLambertMaterial({ color: 0xffdbac });
    bodyModel.torso = new THREE.Mesh(bodyGeometry, bodyMaterial);
    scene.add(bodyModel.torso);

    // Create head
    const headGeometry = new THREE.SphereGeometry(2.5, 32, 32);
    const headMaterial = new THREE.MeshLambertMaterial({ color: 0xffdbac });
    bodyModel.head = new THREE.Mesh(headGeometry, headMaterial);
    bodyModel.head.position.y = 10;
    scene.add(bodyModel.head);

    // Create right arm
    const armGeometry = new THREE.CylinderGeometry(1, 1, 10, 32);
    const armMaterial = new THREE.MeshLambertMaterial({ color: 0xffdbac });
    bodyModel.rightArm = new THREE.Mesh(armGeometry, armMaterial);
    bodyModel.rightArm.position.set(7, 2, 0);
    bodyModel.rightArm.rotation.z = Math.PI / 2;
    scene.add(bodyModel.rightArm);

    // Create left arm
    bodyModel.leftArm = new THREE.Mesh(armGeometry, armMaterial);
    bodyModel.leftArm.position.set(-7, 2, 0);
    bodyModel.leftArm.rotation.z = -Math.PI / 2;
    scene.add(bodyModel.leftArm);

    // Create right breast
    const breastGeometry = new THREE.SphereGeometry(1.5, 32, 32);
    const breastMaterial = new THREE.MeshLambertMaterial({ color: 0xffc0a0 });
    bodyModel.rightBreast = new THREE.Mesh(breastGeometry, breastMaterial);
    bodyModel.rightBreast.position.set(2.5, 4, 4);
    bodyModel.rightBreast.name = 'rightBreast';
    scene.add(bodyModel.rightBreast);

    // Create left breast
    bodyModel.leftBreast = new THREE.Mesh(breastGeometry, breastMaterial);
    bodyModel.leftBreast.position.set(-2.5, 4, 4);
    bodyModel.leftBreast.name = 'leftBreast';
    scene.add(bodyModel.leftBreast);
}

// Update tumor location and size
function updateTumor(location, size = 15) {
    // Remove existing tumor if any
    if (tumor) {
        scene.remove(tumor);
    }

    // Create new tumor
    const tumorGeometry = new THREE.SphereGeometry(0.6, 16, 16);
    const tumorMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
    tumor = new THREE.Mesh(tumorGeometry, tumorMaterial);

    // Scale based on size (mm)
    const scaleValue = 0.5 + (size / 30);
    tumor.scale.set(scaleValue, scaleValue, scaleValue);

    // Position based on location
    switch (location) {
        case 'Right Breast (Upper Outer)':
            tumor.position.set(3.5, 5, 4.5);
            break;
        case 'Right Breast (Upper Inner)':
            tumor.position.set(1.5, 5, 4.5);
            break;
        case 'Right Breast (Lower Outer)':
            tumor.position.set(3.5, 3, 4.5);
            break;
        case 'Right Breast (Lower Inner)':
            tumor.position.set(1.5, 3, 4.5);
            break;
        case 'Left Breast (Upper Outer)':
            tumor.position.set(-3.5, 5, 4.5);
            break;
        case 'Left Breast (Upper Inner)':
            tumor.position.set(-1.5, 5, 4.5);
            break;
        case 'Left Breast (Lower Outer)':
            tumor.position.set(-3.5, 3, 4.5);
            break;
        case 'Left Breast (Lower Inner)':
            tumor.position.set(-1.5, 3, 4.5);
            break;
        default:
            tumor.position.set(3.5, 5, 4.5);
    }

    scene.add(tumor);
    addTumorHighlight(tumor.position.clone(), scaleValue * 1.5);
}

// Add tumor highlight effect
function addTumorHighlight(position, size) {
    // Remove any existing highlights
    scene.children.forEach(child => {
        if (child.userData && child.userData.isHighlight) {
            scene.remove(child);
        }
    });

    // Create highlight sphere
    const highlightGeometry = new THREE.SphereGeometry(1, 16, 16);
    const highlightMaterial = new THREE.MeshBasicMaterial({
        color: 0xff3333,
        transparent: true,
        opacity: 0.3
    });

    const highlight = new THREE.Mesh(highlightGeometry, highlightMaterial);
    highlight.position.copy(position);
    highlight.scale.set(size, size, size);
    highlight.userData.isHighlight = true;
    highlight.userData.pulseRate = 0;
    highlight.userData.baseSize = size;

    scene.add(highlight);
}

// Animation loop
function animate() {
    requestAnimationFrame(animate);

    // Gentle rotation
    if (bodyModel.torso) bodyModel.torso.rotation.y += 0.003;
    if (bodyModel.head) bodyModel.head.rotation.y += 0.003;
    if (bodyModel.rightArm) bodyModel.rightArm.rotation.y += 0.003;
    if (bodyModel.leftArm) bodyModel.leftArm.rotation.y += 0.003;
    if (bodyModel.rightBreast) bodyModel.rightBreast.rotation.y += 0.003;
    if (bodyModel.leftBreast) bodyModel.leftBreast.rotation.y += 0.003;
    if (tumor) tumor.rotation.y += 0.003;

    // Pulse effect for highlight
    scene.children.forEach(child => {
        if (child.userData && child.userData.isHighlight) {
            child.userData.pulseRate += 0.05;
            const pulse = Math.sin(child.userData.pulseRate) * 0.2 + 1;
            const baseSize = child.userData.baseSize;
            
            child.scale.set(
                baseSize * pulse,
                baseSize * pulse,
                baseSize * pulse
            );
            
            child.material.opacity = 0.2 + Math.sin(child.userData.pulseRate) * 0.1;
        }
    });

    // Update controls if available
    if (controls) controls.update();

    // Render scene
    renderer.render(scene, camera);
}

// Connect model to UI controls
function connectModelControls() {
    // Find tumor location selector
    const locationSelect = document.getElementById('tumorLocation');
    if (locationSelect) {
        locationSelect.addEventListener('change', function() {
            updateTumor(this.value);
        });
        
        // Initialize with current value
        updateTumor(locationSelect.value);
    }
    
    // Find tumor size slider
    const sizeSlider = document.getElementById('tumorSizeSlider');
    if (sizeSlider) {
        sizeSlider.addEventListener('input', function() {
            const size = parseInt(this.value);
            const sizeDisplay = document.getElementById('tumorSizeValue');
            if (sizeDisplay) {
                sizeDisplay.textContent = size + 'mm';
            }
            
            // Update tumor with current location and new size
            const location = locationSelect ? locationSelect.value : 'Right Breast (Upper Outer)';
            updateTumor(location, size);
        });
    }
    
    // Find simulation button
    const simulateBtn = document.getElementById('runSimulation');
    if (simulateBtn) {
        simulateBtn.addEventListener('click', function() {
            alert('Simulation results will be displayed here in a future update!');
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize body model when demo tab is shown
    const demoTab = document.getElementById('demo-tab');
    if (demoTab) {
        demoTab.addEventListener('click', function() {
            // Give the DOM time to update
            setTimeout(() => {
                initBodyModel('bodyModelContainer');
                connectModelControls();
            }, 100);
        });
    } else {
        // If no tab, initialize directly
        initBodyModel('bodyModelContainer');
        connectModelControls();
    }
});