/**
 * Simple 3D Body Model for Cancer Digital Twin
 * This file contains the code for rendering and interacting with a 3D body model
 * to visualize tumor locations and simulate disease progression.
 */

// Initialize global variables
let scene, camera, renderer;
let bodyModel = {};
let tumor = null;
let animationId = null;

// Initialize the 3D environment
function initializeBodyModel(containerId = 'bodyModel3D') {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error('Body model container not found:', containerId);
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
    
    // Create body model
    createBodyModel();
    
    // Add controls
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;
    controls.enableZoom = true;
    
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
    
    // Start animation
    animate();
    
    return true;
}

// Create the body model with all components
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
    
    // Add labels
    createLabel('Right Breast', new THREE.Vector3(2.5, 6, 4));
    createLabel('Left Breast', new THREE.Vector3(-2.5, 6, 4));
}

// Create floating text label
function createLabel(text, position) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 64;
    
    context.font = '24px Arial';
    context.fillStyle = 'rgba(0, 0, 0, 0.8)';
    context.fillRect(0, 0, canvas.width, canvas.height);
    
    context.fillStyle = 'white';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(text, canvas.width / 2, canvas.height / 2);
    
    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(material);
    
    sprite.position.copy(position);
    sprite.scale.set(5, 1.25, 1);
    
    scene.add(sprite);
}

// Add or update tumor visualization
function updateTumorLocation(location, size = 20) {
    // Remove existing tumor if any
    if (tumor) {
        scene.remove(tumor);
    }
    
    // Create new tumor
    const tumorGeometry = new THREE.SphereGeometry(0.6, 16, 16);
    const tumorMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
    tumor = new THREE.Mesh(tumorGeometry, tumorMaterial);
    
    // Convert mm to scene units (roughly 1:10 scale)
    const sceneSize = 0.3 + (size / 50);
    tumor.scale.set(sceneSize, sceneSize, sceneSize);
    
    // Set position based on location
    switch (location) {
        case 'right_breast_uoq':
            tumor.position.set(3.5, 5, 4.5);
            break;
        case 'right_breast_uiq':
            tumor.position.set(1.5, 5, 4.5);
            break;
        case 'right_breast_loq':
            tumor.position.set(3.5, 3, 4.5);
            break;
        case 'right_breast_liq':
            tumor.position.set(1.5, 3, 4.5);
            break;
        case 'left_breast_uoq':
            tumor.position.set(-3.5, 5, 4.5);
            break;
        case 'left_breast_uiq':
            tumor.position.set(-1.5, 5, 4.5);
            break;
        case 'left_breast_loq':
            tumor.position.set(-3.5, 3, 4.5);
            break;
        case 'left_breast_liq':
            tumor.position.set(-1.5, 3, 4.5);
            break;
        default:
            tumor.position.set(3.5, 5, 4.5); // Default to right upper outer
    }
    
    scene.add(tumor);
    
    // Create or update tumor highlight effect
    createTumorHighlight(tumor.position.clone(), sceneSize * 1.5);
}

// Create a pulsing highlight around the tumor
function createTumorHighlight(position, size) {
    const highlightGeometry = new THREE.SphereGeometry(1, 16, 16);
    const highlightMaterial = new THREE.MeshBasicMaterial({ 
        color: 0xff3333, 
        transparent: true, 
        opacity: 0.3 
    });
    
    const highlight = new THREE.Mesh(highlightGeometry, highlightMaterial);
    highlight.position.copy(position);
    highlight.scale.set(size, size, size);
    highlight.userData.baseSize = size;
    highlight.userData.pulseFactor = 0;
    
    // Remove any existing highlights
    scene.children.forEach(child => {
        if (child.userData && child.userData.isTumorHighlight) {
            scene.remove(child);
        }
    });
    
    highlight.userData.isTumorHighlight = true;
    scene.add(highlight);
}

// Animation loop
function animate() {
    animationId = requestAnimationFrame(animate);
    
    // Gentle rotation of the body model
    if (bodyModel.torso) bodyModel.torso.rotation.y += 0.003;
    if (bodyModel.head) bodyModel.head.rotation.y += 0.003;
    if (bodyModel.rightArm) bodyModel.rightArm.rotation.y += 0.003;
    if (bodyModel.leftArm) bodyModel.leftArm.rotation.y += 0.003;
    if (bodyModel.rightBreast) bodyModel.rightBreast.rotation.y += 0.003;
    if (bodyModel.leftBreast) bodyModel.leftBreast.rotation.y += 0.003;
    if (tumor) tumor.rotation.y += 0.003;
    
    // Pulse effect for tumor highlight
    scene.children.forEach(child => {
        if (child.userData && child.userData.isTumorHighlight) {
            child.userData.pulseFactor += 0.05;
            const pulseMagnitude = Math.sin(child.userData.pulseFactor) * 0.2 + 1;
            const baseSize = child.userData.baseSize;
            
            child.scale.set(
                baseSize * pulseMagnitude,
                baseSize * pulseMagnitude,
                baseSize * pulseMagnitude
            );
            
            // Update opacity based on pulse
            child.material.opacity = 0.2 + Math.sin(child.userData.pulseFactor) * 0.15;
        }
    });
    
    // Update controller if exists
    if (window.controls) {
        window.controls.update();
    }
    
    // Render scene
    renderer.render(scene, camera);
}

// Stop animation and clean up resources
function disposeBodyModel() {
    if (animationId) {
        cancelAnimationFrame(animationId);
        animationId = null;
    }
    
    // Dispose geometries and materials to free memory
    if (scene) {
        scene.traverse(object => {
            if (object.geometry) object.geometry.dispose();
            if (object.material) {
                if (Array.isArray(object.material)) {
                    object.material.forEach(material => material.dispose());
                } else {
                    object.material.dispose();
                }
            }
        });
        scene = null;
    }
    
    if (renderer) {
        renderer.dispose();
        renderer = null;
    }
    
    // Clear references
    camera = null;
    bodyModel = {};
    tumor = null;
}

// Connect event listeners to form elements
function connectFormElements() {
    // Connect tumor location dropdown
    const locationSelect = document.getElementById('demoTumorLocation') || document.getElementById('tumorLocation');
    if (locationSelect) {
        locationSelect.addEventListener('change', (event) => {
            updateTumorLocation(event.target.value);
        });
        
        // Initialize with current value
        updateTumorLocation(locationSelect.value);
    }
    
    // Connect tumor size slider
    const sizeSlider = document.getElementById('demoTumorSize') || document.getElementById('tumorSize');
    const sizeValue = document.getElementById('demoSizeValue') || document.getElementById('sizeValue');
    
    if (sizeSlider) {
        sizeSlider.addEventListener('input', (event) => {
            const size = parseFloat(event.target.value);
            if (sizeValue) {
                sizeValue.textContent = size + 'mm';
            }
            
            // Get current location
            const location = locationSelect ? locationSelect.value : 'right_breast_uoq';
            updateTumorLocation(location, size);
        });
    }
}

// Initialize model when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize if tab is active or when it becomes active
    const demoTab = document.getElementById('demo-tab');
    
    if (demoTab) {
        demoTab.addEventListener('shown.bs.tab', function (e) {
            initializeBodyModel();
            connectFormElements();
        });
        
        // Also initialize if we're already on the demo tab
        if (demoTab.classList.contains('active')) {
            initializeBodyModel();
            connectFormElements();
        }
    } else {
        // If there's no tab system, just initialize directly
        setTimeout(() => {
            initializeBodyModel();
            connectFormElements();
        }, 500);
    }
});

// Export functions for external use
window.bodyModelFunctions = {
    initialize: initializeBodyModel,
    updateTumorLocation: updateTumorLocation,
    dispose: disposeBodyModel
};
