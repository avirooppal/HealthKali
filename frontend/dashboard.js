/**
 * Dashboard functionality for Cancer Digital Twin
 */

// Import our API module
import digitalTwinAPI from './api.js';

document.addEventListener('DOMContentLoaded', function() {
    // Initialize database
    const patientDB = new PatientDatabase();
    
    // Initialize enhanced results handler
    const resultsHandler = new EnhancedResults();
    
    // Check if we're on the dashboard page
    if (!document.querySelector('.dashboard-container')) return;
    
    // --- Navigation and UI Setup ---
    setupNavigation();
    setupPatientSelector();
    setupModalHandlers();
    setupPredictionTypeTabs();
    
    // --- Button Event Listeners ---
    setupButtonHandlers();
    
    // --- Initialize with demo data ---
    loadDemoPatient('demo1');
    
    // Update dashboard counters
    updateDashboardCounters();
});

// --- Navigation ---
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const contentSections = document.querySelectorAll('.content-section');
    
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all items
            navItems.forEach(navItem => navItem.classList.remove('active'));
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Show corresponding section
            const targetSection = this.getAttribute('data-section');
            
            contentSections.forEach(section => {
                section.classList.remove('active');
                if (section.id === targetSection) {
                    section.classList.add('active');
                }
            });
        });
    });
}

// --- Patient Selector ---
function setupPatientSelector() {
    const patientSelector = document.getElementById('patientSelector');
    
    patientSelector.addEventListener('change', function() {
        const selectedValue = this.value;
        
        if (selectedValue === 'new') {
            // Show patient creation modal
            document.getElementById('patientCreationModal').style.display = 'block';
        } else if (selectedValue.startsWith('demo')) {
            // Load demo patient
            loadDemoPatient(selectedValue);
        } else {
            // Load existing patient from API
            loadPatient(selectedValue);
        }
    });
}

// --- Modal Handlers ---
function setupModalHandlers() {
    // Close modal buttons
    const closeButtons = document.querySelectorAll('.close-modal');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            document.getElementById('patientCreationModal').style.display = 'none';
            
            // Reset patient selector to current patient
            const currentPatient = getCurrentPatientId();
            if (currentPatient) {
                document.getElementById('patientSelector').value = currentPatient;
            }
        });
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('patientCreationModal');
        if (event.target === modal) {
            modal.style.display = 'none';
            
            // Reset patient selector
            const currentPatient = getCurrentPatientId();
            if (currentPatient) {
                document.getElementById('patientSelector').value = currentPatient;
            }
        }
    });
    
    // Patient creation form submission
    const newPatientForm = document.getElementById('newPatientForm');
    if (newPatientForm) {
        newPatientForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(this);
            const patientId = formData.get('patientID');
            
            // Create patient data object
            const patientData = {
                age: parseInt(formData.get('age')),
                tumor_size: parseInt(formData.get('tumor_size')),
                grade: parseInt(formData.get('grade')),
                nodes_positive: parseInt(formData.get('nodes_positive')),
                er_status: formData.get('er_status'),
                her2_status: formData.get('her2_status'),
                menopausal_status: formData.get('menopausal_status')
            };
            
            // Call API to create patient
            createPatient(patientId, patientData);
            
            // Close modal
            document.getElementById('patientCreationModal').style.display = 'none';
        });
    }
    
    // Create patient button
    const createPatientBtn = document.getElementById('createPatientBtn');
    if (createPatientBtn) {
        createPatientBtn.addEventListener('click', function() {
            document.getElementById('patientCreationModal').style.display = 'block';
        });
    }
    
    // Edit profile button
    const editProfileBtn = document.getElementById('editProfileBtn');
    if (editProfileBtn) {
        editProfileBtn.addEventListener('click', function() {
            document.getElementById('patientCreationModal').style.display = 'block';
            
            // Pre-fill form with current patient data
            const patientData = getPatientData();
            if (patientData) {
                document.getElementById('patientID').value = getCurrentPatientId();
                document.getElementById('patientAge').value = patientData.age || '';
                document.getElementById('patientTumorSize').value = patientData.tumor_size || '';
                document.getElementById('patientGrade').value = patientData.grade || '2';
                document.getElementById('patientNodes').value = patientData.nodes_positive || '0';
                document.getElementById('patientER').value = patientData.er_status || 'positive';
                document.getElementById('patientHER2').value = patientData.her2_status || 'negative';
                document.getElementById('patientMenopause').value = patientData.menopausal_status || 'pre';
            }
        });
    }
}

// --- Prediction Type Tabs ---
function setupPredictionTypeTabs() {
    const typeTabs = document.querySelectorAll('.prediction-type-selector .type-button');
    const typePanels = {
        'survival': document.getElementById('survival-prediction'),
        'recurrence': document.getElementById('recurrence-prediction'),
        'treatment': document.getElementById('treatment-prediction')
    };
    
    typeTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            typeTabs.forEach(t => t.classList.remove('active'));
            
            // Hide all panels
            Object.values(typePanels).forEach(panel => {
                if (panel) panel.classList.remove('active');
            });
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Show corresponding panel
            const type = this.getAttribute('data-type');
            if (typePanels[type]) {
                typePanels[type].classList.add('active');
            }
        });
    });
}

// --- Button Handlers ---
function setupButtonHandlers() {
    // Survival prediction button
    const runSurvivalBtn = document.getElementById('runSurvivalBtn');
    if (runSurvivalBtn) {
        runSurvivalBtn.addEventListener('click', runSurvivalPrediction);
    }
    
    // Recurrence prediction button
    const runRecurrenceBtn = document.getElementById('runRecurrenceBtn');
    if (runRecurrenceBtn) {
        runRecurrenceBtn.addEventListener('click', runRecurrencePrediction);
    }
    
    // Treatment response prediction button
    const runTreatmentBtn = document.getElementById('runTreatmentBtn');
    if (runTreatmentBtn) {
        runTreatmentBtn.addEventListener('click', runTreatmentResponsePrediction);
    }
    
    // Disease course simulation button
    const runDiseaseBtn = document.getElementById('runDiseaseSimulation');
    if (runDiseaseBtn) {
        runDiseaseBtn.addEventListener('click', runDiseaseSimulation);
    }
}

// --- Patient Data Handling ---
function createPatient(patientId, patientData) {
    // Call API to create patient
    digitalTwinAPI.fetchAPI(`/twins/create/${patientId}`, 'POST', patientData)
        .then(result => {
            console.log('Patient created:', result);
            
            // Update patient selector with new option
            const patientSelector = document.getElementById('patientSelector');
            const option = document.createElement('option');
            option.value = patientId;
            option.textContent = `Patient: ${patientId}`;
            patientSelector.appendChild(option);
            
            // Select the new patient
            patientSelector.value = patientId;
            
            // Update patient data in session storage
            sessionStorage.setItem('currentPatientId', patientId);
            sessionStorage.setItem('patientData', JSON.stringify(patientData));
            
            // Update UI with patient data
            updatePatientProfile(patientData);
        })
        .catch(error => {
            console.error('Error creating patient:', error);
            alert('Error creating patient: ' + error.message);
        });
}

function loadPatient(patientId) {
    // Call API to get patient data
    digitalTwinAPI.fetchAPI(`/twins/${patientId}`, 'GET')
        .then(patientData => {
            console.log('Patient data loaded:', patientData);
            
            // Update patient data in session storage
            sessionStorage.setItem('currentPatientId', patientId);
            sessionStorage.setItem('patientData', JSON.stringify(patientData));
            
            // Update UI with patient data
            updatePatientProfile(patientData);
        })
        .catch(error => {
            console.error('Error loading patient:', error);
            alert('Error loading patient: ' + error.message);
        });
}

function loadDemoPatient(demoId) {
    // Demo patient data
    const demoPatients = {
        'demo1': {
            // Early-Stage, Good Prognosis
            age: 62,
            tumor_size: 8,
            grade: 1,
            nodes_positive: 0,
            er_status: 'positive',
            her2_status: 'negative',
            menopausal_status: 'post'
        },
        'demo2': {
            // Locally Advanced, Intermediate Prognosis
            age: 51,
            tumor_size: 35,
            grade: 2,
            nodes_positive: 2,
            er_status: 'positive',
            her2_status: 'negative',
            menopausal_status: 'post'
        },
        'demo3': {
            // Triple Negative, Poor Prognosis
            age: 42,
            tumor_size: 28,
            grade: 3,
            nodes_positive: 3,
            er_status: 'negative',
            her2_status: 'negative',
            menopausal_status: 'pre'
        },
        'demo4': {
            // HER2-Positive, Responsive to Treatment
            age: 38,
            tumor_size: 20,
            grade: 3,
            nodes_positive: 1,
            er_status: 'negative',
            her2_status: 'positive',
            menopausal_status: 'pre'
        }
    };
    
    // Get demo patient data
    const patientData = demoPatients[demoId];
    
    if (patientData) {
        // Update patient data in session storage
        sessionStorage.setItem('currentPatientId', demoId);
        sessionStorage.setItem('patientData', JSON.stringify(patientData));
        
        // Update UI with patient data
        updatePatientProfile(patientData);
    }
}

function updatePatientProfile(patientData) {
    // Update profile display
    const patientId = getCurrentPatientId();
    document.getElementById('profilePatientID').textContent = `Patient ID: ${patientId || 'Demo'}`;
    document.getElementById('profilePatientAge').textContent = `Age: ${patientData.age || '--'}`;
    document.getElementById('profilePatientMenopause').textContent = `Menopausal Status: ${patientData.menopausal_status === 'pre' ? 'Pre-menopausal' : 'Post-menopausal'}`;
    
    document.getElementById('profileTumorSize').textContent = `${patientData.tumor_size || '--'} mm`;
    
    let gradeText = '--';
    if (patientData.grade === 1) gradeText = 'Grade 1 (Well differentiated)';
    else if (patientData.grade === 2) gradeText = 'Grade 2 (Moderately differentiated)';
    else if (patientData.grade === 3) gradeText = 'Grade 3 (Poorly differentiated)';
    document.getElementById('profileTumorGrade').textContent = gradeText;
    
    document.getElementById('profileLymphNodes').textContent = `${patientData.nodes_positive || 0} positive`;
    document.getElementById('profileER').textContent = patientData.er_status === 'positive' ? 'Positive' : 'Negative';
    document.getElementById('profileHER2').textContent = patientData.her2_status === 'positive' ? 'Positive' : 'Negative';
    
    // Determine molecular subtype
    let subtype = 'Unknown';
    if (patientData.er_status === 'positive' && patientData.her2_status === 'negative') {
        subtype = patientData.grade === 3 ? 'Luminal B' : 'Luminal A';
    } else if (patientData.er_status === 'positive' && patientData.her2_status === 'positive') {
        subtype = 'Luminal B (HER2+)';
    } else if (patientData.er_status === 'negative' && patientData.her2_status === 'positive') {
        subtype = 'HER2 Enriched';
    } else if (patientData.er_status === 'negative' && patientData.her2_status === 'negative') {
        subtype = 'Triple Negative';
    }
    document.getElementById('profileSubtype').textContent = subtype;
    
    // Update risk level
    const riskLevelEl = document.getElementById('riskLevel');
    let riskLevel = 'Low';
    let riskClass = 'low';
    
    // Very simplified risk assessment
    if (patientData.grade === 3 || patientData.nodes_positive > 0 || patientData.tumor_size > 30 || patientData.er_status === 'negative') {
        if ((patientData.grade === 3 && patientData.nodes_positive > 0) || 
            (patientData.nodes_positive > 2) || 
            (patientData.er_status === 'negative' && patientData.her2_status === 'negative')) {
            riskLevel = 'High';
            riskClass = 'high';
        } else {
            riskLevel = 'Intermediate';
            riskClass = 'medium';
        }
    }
    
    riskLevelEl.textContent = riskLevel;
    riskLevelEl.className = 'risk-level ' + riskClass;
    
    // Update survival chart
    updateSurvivalPreview(patientData);
    
    // Update recurrence preview
    updateRecurrencePreview(patientData);
}

function updateSurvivalPreview(patientData) {
    // Calculate a quick survival estimate
    let survivalRate = 0.95; // Base 5-year survival
    
    // Adjust based on risk factors
    if (patientData.grade === 3) survivalRate -= 0.1;
    else if (patientData.grade === 1) survivalRate += 0.02;
    
    if (patientData.nodes_positive > 3) survivalRate -= 0.2;
    else if (patientData.nodes_positive > 0) survivalRate -= 0.1;
    
    if (patientData.tumor_size > 30) survivalRate -= 0.1;
    else if (patientData.tumor_size < 10) survivalRate += 0.02;
    
    if (patientData.er_status === 'negative') survivalRate -= 0.1;
    if (patientData.her2_status === 'negative') survivalRate -= 0.05;
    
    // Ensure it's between 0.5 and 0.98
    survivalRate = Math.min(0.98, Math.max(0.5, survivalRate));
    
    // Update the survival chart
    const survivalPercentage = Math.round(survivalRate * 100);
    document.getElementById('survivalPercentage').textContent = `${survivalPercentage}%`;
    document.getElementById('survivalPath').setAttribute('stroke-dasharray', `${survivalPercentage}, 100`);
}

function updateRecurrencePreview(patientData) {
    // Calculate a quick recurrence estimate (inverse of survival with adjustments)
    let recurrenceRate = 0.15; // Base 5-year recurrence
    
    // Adjust based on risk factors
    if (patientData.grade === 3) recurrenceRate += 0.1;
    else if (patientData.grade === 1) recurrenceRate -= 0.05;
    
    if (patientData.nodes_positive > 3) recurrenceRate += 0.25;
    else if (patientData.nodes_positive > 0) recurrenceRate += 0.15;
    
    if (patientData.tumor_size > 30) recurrenceRate += 0.1;
    else if (patientData.tumor_size < 10) recurrenceRate -= 0.05;
    
    if (patientData.er_status === 'negative') recurrenceRate += 0.15;
    if (patientData.her2_status === 'positive') recurrenceRate += 0.05;
    
    // Ensure it's between 0.02 and 0.5
    recurrenceRate = Math.min(0.5, Math.max(0.02, recurrenceRate));
    
    // Update the recurrence chart
    const recurrencePercentage = Math.round(recurrenceRate * 100);
    document.getElementById('recurrencePercentage').textContent = `${recurrencePercentage}%`;
    document.getElementById('recurrencePath').setAttribute('stroke-dasharray', `${recurrencePercentage}, 100`);
}

// --- Helper Functions ---
function getCurrentPatientId() {
    return sessionStorage.getItem('currentPatientId');
}

function getPatientData() {
    const data = sessionStorage.getItem('patientData');
    return data ? JSON.parse(data) : null;
}

// --- Prediction and Simulation Functions ---

// Survival Prediction
async function runSurvivalPrediction() {
    const patientData = getPatientData();
    if (!patientData) {
        alert('Please select a patient first');
        return;
    }
    
    // Show loading indicator
    document.getElementById('survivalLoadingIndicator').style.display = 'flex';
    document.getElementById('survivalResultsContainer').querySelector('.prediction-summary').innerHTML = '';
    document.querySelector('.chart-container').style.display = 'none';
    document.querySelector('.risk-factors').style.display = 'none';
    
    // Get years from selector
    const years = parseInt(document.getElementById('survivalYears').value);
    
    try {
        // Call API
        const result = await digitalTwinAPI.fetchAPI('/prediction/survival', 'POST', {
            patient: patientData,
            years: years
        });
        
        // Display results
        displaySurvivalResults(result);
    } catch (error) {
        console.error('Prediction error:', error);
        document.getElementById('survivalResultsContainer').querySelector('.prediction-summary').innerHTML = `
            <div class="error-message">
                <p><i class="fas fa-exclamation-triangle"></i> Error running prediction: ${error.message || 'Unknown error'}</p>
            </div>
        `;
    } finally {
        // Hide loading indicator
        document.getElementById('survivalLoadingIndicator').style.display = 'none';
    }
}

function displaySurvivalResults(result) {
    // Set summary
    const summaryElement = document.getElementById('survivalResultsContainer').querySelector('.prediction-summary');
    summaryElement.innerHTML = `
        <div class="prediction-result">
            <h4>${result.patient_risk_category || 'Intermediate Risk'}</h4>
            <p class="main-result">5-Year Survival: <strong>${(result.overall_5yr_survival * 100).toFixed(1)}%</strong></p>
            <p>This patient's survival probability is based on ${Object.keys(result.modifiers || {}).length} clinical and molecular factors. The prediction represents the most likely outcome based on similar patients in our database.</p>
        </div>
    `;
    
    // Show chart container
    const chartContainer = document.querySelector('.chart-container');
    chartContainer.style.display = 'block';
    
    // Create chart
    createSurvivalChart(result.survival_curve, result.lower_ci, result.upper_ci);
    
    // Show risk modifiers
    const riskFactors = document.querySelector('.risk-factors');
    riskFactors.style.display = 'block';
    
    // Populate risk modifiers
    const modifiersElement = document.getElementById('riskModifiers');
    if (result.modifiers && Object.keys(result.modifiers).length > 0) {
        let modifiersHTML = '<ul class="modifiers-list">';
        for (const [factor, value] of Object.entries(result.modifiers)) {
            let factorName = factor;
            if (factor === 'age') factorName = 'Age';
            else if (factor === 'grade') factorName = 'Tumor Grade';
            else if (factor === 'nodes') factorName = 'Lymph Node Status';
            else if (factor === 'size') factorName = 'Tumor Size';
            else if (factor === 'er') factorName = 'ER Status';
            else if (factor === 'her2') factorName = 'HER2 Status';
            
            let impact = 'neutral';
            if (value < 0.95) impact = 'negative';
            else if (value > 1.05) impact = 'positive';
            
            modifiersHTML += `<li class="modifier-item">
                <span class="modifier-name">${factorName}</span>
                <span class="modifier-value ${impact}">${value.toFixed(2)}</span>
            </li>`;
        }
        modifiersHTML += '</ul>';
        modifiersElement.innerHTML = modifiersHTML;
    } else {
        modifiersElement.innerHTML = '<p>No specific risk modifiers available.</p>';
    }
}

function createSurvivalChart(survivalCurve, lowerCI, upperCI) {
    const ctx = document.getElementById('survivalChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (window.survivalChart) {
        window.survivalChart.destroy();
    }
    
    // Prepare data
    const labels = survivalCurve.map(point => `Year ${point.year}`);
    const survivalData = survivalCurve.map(point => point.survival_probability * 100);
    
    // Prepare confidence intervals if available
    let lowerData = [];
    let upperData = [];
    
    if (lowerCI && upperCI) {
        lowerData = lowerCI.map(point => point.survival_probability * 100);
        upperData = upperCI.map(point => point.survival_probability * 100);
    }
    
    // Create chart
    window.survivalChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Survival Probability',
                    data: survivalData,
                    backgroundColor: 'rgba(14, 165, 233, 0.2)',
                    borderColor: 'rgba(14, 165, 233, 1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.1
                },
                ...(lowerData.length > 0 ? [{
                    label: 'Lower Confidence Interval',
                    data: lowerData,
                    borderColor: 'rgba(14, 165, 233, 0.3)',
                    borderWidth: 1,
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0
                }] : []),
                ...(upperData.length > 0 ? [{
                    label: 'Upper Confidence Interval',
                    data: upperData,
                    borderColor: 'rgba(14, 165, 233, 0.3)',
                    borderWidth: 1,
                    borderDash: [5, 5],
                    fill: '-2',
                    backgroundColor: 'rgba(14, 165, 233, 0.1)',
                    pointRadius: 0
                }] : [])
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Survival Probability (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

// Recurrence Prediction
async function runRecurrencePrediction() {
    const patientData = getPatientData();
    if (!patientData) {
        alert('Please select a patient first');
        return;
    }
    
    // Show loading indicator
    document.getElementById('recurrenceLoadingIndicator').style.display = 'flex';
    document.getElementById('recurrenceResultsContainer').querySelector('.prediction-summary').innerHTML = '';
    document.querySelector('.recurrence-breakdown').style.display = 'none';
    document.querySelector('.recurrence-timeline').style.display = 'none';
    
    // Get years from selector
    const years = parseInt(document.getElementById('recurrenceYears').value);
    
    try {
        // Call API
        const result = await digitalTwinAPI.fetchAPI('/prediction/recurrence', 'POST', {
            patient: patientData,
            years: years
        });
        
        // Display results
        displayRecurrenceResults(result);
    } catch (error) {
        console.error('Prediction error:', error);
        document.getElementById('recurrenceResultsContainer').querySelector('.prediction-summary').innerHTML = `
            <div class="error-message">
                <p><i class="fas fa-exclamation-triangle"></i> Error running prediction: ${error.message || 'Unknown error'}</p>
            </div>
        `;
    } finally {
        // Hide loading indicator
        document.getElementById('recurrenceLoadingIndicator').style.display = 'none';
    }
}

function displayRecurrenceResults(result) {
    // Set summary
    const summaryElement = document.getElementById('recurrenceResultsContainer').querySelector('.prediction-summary');
    summaryElement.innerHTML = `
        <div class="prediction-result">
            <h4>${result.patient_risk_category || 'Intermediate Risk'}</h4>
            <p class="main-result">5-Year Recurrence: <strong>${(result.overall_5yr_recurrence * 100).toFixed(1)}%</strong></p>
            <p>This patient's recurrence probability is based on ${Object.keys(result.modifiers || {}).length} clinical and molecular factors. The prediction represents the most likely outcome based on similar patients in our database.</p>
        </div>
    `;
    
    // Show recurrence breakdown
    const breakdownEl = document.querySelector('.recurrence-breakdown');
    breakdownEl.style.display = 'block';
    
    // Create recurrence breakdown chart
    createRecurrenceBreakdownChart(result.recurrence_breakdown);
    
    // Show recurrence timeline
    const timelineEl = document.querySelector('.recurrence-timeline');
    timelineEl.style.display = 'block';
    
    // Create recurrence timeline chart
    createRecurrenceTimelineChart(result.recurrence_timeline);
}

function createRecurrenceBreakdownChart(breakdown) {
    const canvasEl = document.getElementById('recurrenceBreakdownChart');
    if (!canvasEl) return;
    
    const ctx = canvasEl.getContext('2d');
    
    // Destroy existing chart if it exists
    if (window.recurrenceBreakdownChart) {
        window.recurrenceBreakdownChart.destroy();
    }
    
    // Prepare data
    const labels = Object.keys(breakdown);
    const data = Object.values(breakdown);
    
    // Create chart
    window.recurrenceBreakdownChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Recurrence Probability',
                data: data,
                backgroundColor: 'rgba(14, 165, 233, 0.7)',
                borderColor: 'rgba(14, 165, 233, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Recurrence Probability (%)'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

function createRecurrenceTimelineChart(recurrenceCurves) {
    const canvasEl = document.getElementById('recurrenceTimelineChart');
    if (!canvasEl) return;
    
    const ctx = canvasEl.getContext('2d');
    
    // Destroy existing chart if it exists
    if (window.recurrenceTimelineChart) {
        window.recurrenceTimelineChart.destroy();
    }
    
    // Prepare data
    const datasets = [];
    
    if (recurrenceCurves) {
        // Get common labels (years)
        const firstCurve = Object.values(recurrenceCurves)[0];
        const labels = firstCurve.map(point => `Year ${point.year}`);
        
        // Colors for different recurrence types
        const colors = {
            'local': 'rgba(255, 170, 0, 1)',
            'regional': 'rgba(255, 100, 0, 1)',
            'distant': 'rgba(220, 50, 50, 1)'
        };
        
        // Create datasets for each recurrence type
        for (const [type, curve] of Object.entries(recurrenceCurves)) {
            const typeName = type.replace('_', ' ');
            datasets.push({
                label: typeName.charAt(0).toUpperCase() + typeName.slice(1),
                data: curve.map(point => point.recurrence_probability * 100),
                borderColor: colors[type.split('_')[0]],
                backgroundColor: colors[type.split('_')[0]].replace('1)', '0.1)'),
                borderWidth: 2,
                fill: false
            });
        }
        
        // Create chart
        window.recurrenceTimelineChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        min: 0,
                        title: {
                            display: true,
                            text: 'Cumulative Recurrence Risk (%)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}%`;
                            }
                        }
                    }
                }
            }
        });
    }
}

// Treatment Response Prediction
async function runTreatmentResponsePrediction() {
    const patientData = getPatientData();
    if (!patientData) {
        alert('Please select a patient first');
        return;
    }
    
    // Show loading indicator
    document.getElementById('treatmentLoadingIndicator').style.display = 'flex';
    document.getElementById('treatmentResultsContainer').querySelector('.prediction-summary').innerHTML = '';
    
    const efficacyEl = document.querySelector('.treatment-efficacy');
    if (efficacyEl) efficacyEl.style.display = 'none';
    
    const sideEffectsEl = document.querySelector('.side-effects');
    if (sideEffectsEl) sideEffectsEl.style.display = 'none';
    
    // Get treatment data
    const treatments = [];
    if (document.getElementById('tp-surgery').checked) treatments.push('surgery');
    if (document.getElementById('tp-chemotherapy').checked) treatments.push('chemotherapy');
    if (document.getElementById('tp-radiation').checked) treatments.push('radiation');
    if (document.getElementById('tp-endocrine').checked) treatments.push('endocrine');
    if (document.getElementById('tp-targeted').checked) treatments.push('targeted');
    
    try {
        // Call API
        const result = await digitalTwinAPI.fetchAPI('/prediction/treatment_response', 'POST', {
            patient: patientData,
            treatment: {
                treatments: treatments
            }
        });
        
        // Display results
        displayTreatmentResults(result);
    } catch (error) {
        console.error('Prediction error:', error);
        document.getElementById('treatmentResultsContainer').querySelector('.prediction-summary').innerHTML = `
            <div class="error-message">
                <p><i class="fas fa-exclamation-triangle"></i> Error running prediction: ${error.message || 'Unknown error'}</p>
            </div>
        `;
    } finally {
        // Hide loading indicator
        document.getElementById('treatmentLoadingIndicator').style.display = 'none';
    }
}

function displayTreatmentResults(result) {
    // Set summary
    const summaryElement = document.getElementById('treatmentResultsContainer').querySelector('.prediction-summary');
    summaryElement.innerHTML = `
        <div class="prediction-result">
            <h4>${result.efficacy_category || 'Good'} Response Expected</h4>
            <p class="main-result">Overall Response Rate: <strong>${(result.overall_response_probability * 100).toFixed(1)}%</strong></p>
            <p>This prediction is based on the selected treatment plan and patient characteristics. Response rates represent the probability of clinical benefit from the treatment.</p>
        </div>
    `;
    
    // Show efficacy chart
    const efficacyEl = document.querySelector('.treatment-efficacy');
    if (efficacyEl) efficacyEl.style.display = 'block';
    
    // Create efficacy chart
    createEfficacyChart(result.treatment_specific_responses);
    
    // Show side effects
    const sideEffectsEl = document.querySelector('.side-effects');
    if (sideEffectsEl) sideEffectsEl.style.display = 'block';
    
    // Display side effects
    displaySideEffects(result.side_effect_probabilities);
}

function createEfficacyChart(treatmentResponses) {
    const canvasEl = document.getElementById('efficacyChart');
    if (!canvasEl) return;
    
    const ctx = canvasEl.getContext('2d');
    
    // Destroy existing chart if it exists
    if (window.efficacyChart) {
        window.efficacyChart.destroy();
    }
    
    // Prepare data
    const labels = [];
    const data = [];
    
    if (treatmentResponses) {
        for (const [treatment, response] of Object.entries(treatmentResponses)) {
            // Format treatment name
            let label = treatment;
            if (treatment === 'chemotherapy') label = 'Chemotherapy';
            else if (treatment === 'radiation') label = 'Radiation';
            else if (treatment === 'surgery') label = 'Surgery';
            else if (treatment === 'endocrine') label = 'Endocrine';
            else if (treatment === 'targeted') label = 'Targeted';
            
            labels.push(label);
            data.push(response * 100);
        }
    }
    
    // Create chart
    window.efficacyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Response Rate (%)',
                data: data,
                backgroundColor: 'rgba(14, 165, 233, 0.7)',
                borderColor: 'rgba(14, 165, 233, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Response Rate (%)'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Response Rate: ${context.parsed.y.toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

function displaySideEffects(sideEffects) {
    const container = document.getElementById('sideEffectsContainer');
    if (!container) return;
    
    let html = '';
    
    if (sideEffects && Object.keys(sideEffects).length > 0) {
        for (const [treatment, effects] of Object.entries(sideEffects)) {
            // Format treatment name
            let treatmentName = treatment;
            if (treatment === 'chemotherapy') treatmentName = 'Chemotherapy';
            else if (treatment === 'radiation') treatmentName = 'Radiation';
            else if (treatment === 'surgery') treatmentName = 'Surgery';
            else if (treatment === 'endocrine') treatmentName = 'Endocrine Therapy';
            else if (treatment === 'targeted') treatmentName = 'Targeted Therapy';
            
            html += `<div class="side-effect-group">
                <h5>${treatmentName}</h5>
                <ul class="side-effect-list">`;
            
            for (const [effect, probability] of Object.entries(effects)) {
                // Format effect name
                let effectName = effect.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
                
                // Determine severity class
                let severityClass = 'low';
                if (probability > 0.5) severityClass = 'high';
                else if (probability > 0.2) severityClass = 'medium';
                
                html += `<li>
                    <span class="effect-name">${effectName}</span>
                    <span class="effect-probability ${severityClass}">${(probability * 100).toFixed(0)}%</span>
                </li>`;
            }
            
            html += `</ul></div>`;
        }
    } else {
        html = '<p>No side effect data available for the selected treatments.</p>';
    }
    
    container.innerHTML = html;
}

// Disease Course Simulation
async function runDiseaseSimulation() {
    const patientData = getPatientData();
    if (!patientData) {
        alert('Please select a patient first');
        return;
    }
    
    // Show loading indicator
    document.getElementById('diseaseLoadingIndicator').style.display = 'flex';
    document.getElementById('diseaseResultsContainer').querySelector('.simulation-summary').innerHTML = '';
    
    const stateEl = document.querySelector('.state-trajectories');
    if (stateEl) stateEl.style.display = 'none';
    
    const tumorEl = document.querySelector('.tumor-growth');
    if (tumorEl) tumorEl.style.display = 'none';
    
    const detailsEl = document.querySelector('.simulation-details');
    if (detailsEl) detailsEl.style.display = 'none';
    
    // Get simulation parameters
    const months = parseInt(document.getElementById('dc-months').value);
    const numSimulations = parseInt(document.getElementById('dc-simulations').value);
    
    // Get treatment data
    const treatments = [];
    if (document.getElementById('dc-surgery').checked) treatments.push('surgery');
    if (document.getElementById('dc-chemotherapy').checked) treatments.push('chemotherapy');
    if (document.getElementById('dc-radiation').checked) treatments.push('radiation');
    if (document.getElementById('dc-endocrine').checked) treatments.push('endocrine');
    if (document.getElementById('dc-targeted').checked) treatments.push('targeted');
    
    try {
        // Call API
        const result = await digitalTwinAPI.fetchAPI('/simulation/disease_course', 'POST', {
            patient: patientData,
            treatment: {
                treatments: treatments
            },
            months: months,
            num_simulations: numSimulations
        });
        
        // Display results
        displayDiseaseSimulationResults(result);
    } catch (error) {
        console.error('Simulation error:', error);
        document.getElementById('diseaseResultsContainer').querySelector('.simulation-summary').innerHTML = `
            <div class="error-message">
                <p><i class="fas fa-exclamation-triangle"></i> Error running simulation: ${error.message || 'Unknown error'}</p>
            </div>
        `;
    } finally {
        // Hide loading indicator
        document.getElementById('diseaseLoadingIndicator').style.display = 'none';
    }
}

function displayDiseaseSimulationResults(result) {
    // Set summary
    const summaryElement = document.getElementById('diseaseResultsContainer').querySelector('.simulation-summary');
    
    // Format state probabilities
    const stateProbs = result.state_probabilities || {};
    const nedProb = (stateProbs.NED || 0) * 100;
    const recurrenceProb = ((stateProbs['Local Recurrence'] || 0) + 
                          (stateProbs['Regional Recurrence'] || 0) + 
                          (stateProbs['Distant Metastasis'] || 0)) * 100;
    const deathProb = (stateProbs.Death || 0) * 100;
    
    summaryElement.innerHTML = `
        <div class="simulation-result">
            <h4>Disease Course Simulation</h4>
            <p class="main-result">At ${result.total_months || 60} months: <strong>${nedProb.toFixed(1)}%</strong> disease-free, <strong>${recurrenceProb.toFixed(1)}%</strong> recurrence, <strong>${deathProb.toFixed(1)}%</strong> mortality</p>
            <p>Based on ${result.num_simulations || 10} simulations of disease progression. Each simulation represents a possible trajectory for this patient.</p>
        </div>
    `;
    
    // Show state trajectories
    const stateEl = document.querySelector('.state-trajectories');
    if (stateEl) stateEl.style.display = 'block';
    
    // Create state trajectory chart
    createStateTrajectoryChart(result.state_probability_trajectory);
    
    // Show tumor growth if available
    if (result.tumor_growth_trajectory && result.tumor_growth_trajectory.length > 0) {
        const tumorEl = document.querySelector('.tumor-growth');
        if (tumorEl) tumorEl.style.display = 'block';
        
        createTumorGrowthChart(result.tumor_growth_trajectory);
    }
    
    // Show simulation details
    const detailsEl = document.querySelector('.simulation-details');
    if (detailsEl) detailsEl.style.display = 'block';
    
    // Display simulation details
    displaySimulationDetails(result);
}

function createStateTrajectoryChart(trajectoryPoints) {
    const canvasEl = document.getElementById('stateTrajectoryChart');
    if (!canvasEl) return;
    
    const ctx = canvasEl.getContext('2d');
    
    // Destroy existing chart if it exists
    if (window.stateTrajectoryChart) {
        window.stateTrajectoryChart.destroy();
    }
    
    // Prepare data
    const months = trajectoryPoints.map(point => `Month ${point.month}`);
    
    // Create datasets
    const datasets = [
        {
            label: 'No Evidence of Disease',
            data: trajectoryPoints.map(point => point.state_probabilities.NED * 100),
            backgroundColor: 'rgba(34, 197, 94, 0.2)',
            borderColor: 'rgba(34, 197, 94, 1)',
            borderWidth: 2,
            fill: true
        },
        {
            label: 'Local Recurrence',
            data: trajectoryPoints.map(point => (point.state_probabilities['Local Recurrence'] || 0) * 100),
            backgroundColor: 'rgba(255, 170, 0, 0.2)',
            borderColor: 'rgba(255, 170, 0, 1)',
            borderWidth: 2,
            fill: true
        },
        {
            label: 'Regional Recurrence',
            data: trajectoryPoints.map(point => (point.state_probabilities['Regional Recurrence'] || 0) * 100),
            backgroundColor: 'rgba(255, 100, 0, 0.2)',
            borderColor: 'rgba(255, 100, 0, 1)',
            borderWidth: 2,
            fill: true
        },
        {
            label: 'Distant Metastasis',
            data: trajectoryPoints.map(point => (point.state_probabilities['Distant Metastasis'] || 0) * 100),
            backgroundColor: 'rgba(220, 50, 50, 0.2)',
            borderColor: 'rgba(220, 50, 50, 1)',
            borderWidth: 2,
            fill: true
        },
        {
            label: 'Death',
            data: trajectoryPoints.map(point => (point.state_probabilities.Death || 0) * 100),
            backgroundColor: 'rgba(100, 100, 100, 0.2)',
            borderColor: 'rgba(100, 100, 100, 1)',
            borderWidth: 2,
            fill: true
        }
    ];
    
    // Create chart
    window.stateTrajectoryChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    stacked: true,
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Probability (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

function createTumorGrowthChart(growthTrajectory) {
    const canvasEl = document.getElementById('tumorGrowthChart');
    if (!canvasEl) return;
    
    const ctx = canvasEl.getContext('2d');
    
    // Destroy existing chart if it exists
    if (window.tumorGrowthChart) {
        window.tumorGrowthChart.destroy();
    }
    
    // Prepare data
    const months = growthTrajectory.map(point => `Month ${point.month}`);
    
    // Find confidence intervals if available
    let meanData = growthTrajectory.map(point => point.mean_size);
    let lowerCI = growthTrajectory.map(point => point.lower_ci || null);
    let upperCI = growthTrajectory.map(point => point.upper_ci || null);
    
    // Create datasets
    const datasets = [
        {
            label: 'Tumor Size (Mean)',
            data: meanData,
            backgroundColor: 'rgba(14, 165, 233, 0.2)',
            borderColor: 'rgba(14, 165, 233, 1)',
            borderWidth: 2,
            fill: false
        }
    ];
    
    // Add confidence intervals if they exist
    if (lowerCI.some(val => val !== null) && upperCI.some(val => val !== null)) {
        datasets.push({
            label: 'Lower 95% CI',
            data: lowerCI,
            borderColor: 'rgba(14, 165, 233, 0.3)',
            borderWidth: 1,
            borderDash: [5, 5],
            fill: false,
            pointRadius: 0
        });
        
        datasets.push({
            label: 'Upper 95% CI',
            data: upperCI,
            borderColor: 'rgba(14, 165, 233, 0.3)',
            borderWidth: 1,
            borderDash: [5, 5],
            fill: '-2',
            backgroundColor: 'rgba(14, 165, 233, 0.1)',
            pointRadius: 0
        });
    }
    
    // Create chart
    window.tumorGrowthChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    min: 0,
                    title: {
                        display: true,
                        text: 'Tumor Size (mm)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)} mm`;
                        }
                    }
                }
            }
        }
    });
}

function displaySimulationDetails(result) {
    const detailsContainer = document.getElementById('simulationDetailsContainer');
    if (!detailsContainer) return;
    
    let html = '<h4>Key Simulation Details</h4><ul class="simulation-detail-list">';
    
    // Add simulation metadata
    html += `<li><span class="detail-label">Number of Simulations:</span> <span class="detail-value">${result.num_simulations || 10}</span></li>`;
    html += `<li><span class="detail-label">Time Horizon:</span> <span class="detail-value">${result.total_months || 60} months</span></li>`;
    
    // Add model parameters
    if (result.model_parameters) {
        for (const [param, value] of Object.entries(result.model_parameters)) {
            // Format parameter name
            let paramName = param.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
            
            // Format value
            let formattedValue = value;
            if (typeof value === 'number') {
                formattedValue = value.toFixed(4);
            }
            
            html += `<li><span class="detail-label">${paramName}:</span> <span class="detail-value">${formattedValue}</span></li>`;
        }
    }
    
    html += '</ul>';
    
    // Add key events if available
    if (result.key_events && result.key_events.length > 0) {
        html += '<h4>Key Events</h4><ul class="event-list">';
        
        for (const event of result.key_events) {
            const eventType = event.event_type || 'Unknown Event';
            const eventTime = event.time || 'Unknown Time';
            const eventProb = event.probability ? `${(event.probability * 100).toFixed(1)}%` : 'N/A';
            
            html += `<li class="event-item">
                <span class="event-type">${eventType}</span>
                <span class="event-time">Month ${eventTime}</span>
                <span class="event-probability">Probability: ${eventProb}</span>
            </li>`;
        }
        
        html += '</ul>';
    }
    
    detailsContainer.innerHTML = html;
}

// Update dashboard counters
async function updateDashboardCounters() {
    try {
        // Get all patients
        const patients = await patientDB.getAllPatients();
        
        // Update total count
        const totalPatientsEl = document.getElementById('totalPatients');
        if (totalPatientsEl) {
            totalPatientsEl.textContent = patients.length;
        }
        
        // Get risk category counts
        const riskCounts = await patientDB.getRiskCategoryCounts();
        
        // Update risk counters
        const highRiskCountEl = document.getElementById('highRiskCount');
        if (highRiskCountEl) highRiskCountEl.textContent = riskCounts.high;
        const mediumRiskCountEl = document.getElementById('mediumRiskCount');
        if (mediumRiskCountEl) mediumRiskCountEl.textContent = riskCounts.medium;
        const lowRiskCountEl = document.getElementById('lowRiskCount');
        if (lowRiskCountEl) lowRiskCountEl.textContent = riskCounts.low;
        
        // Update recent patients table
        updateRecentPatientsTable(patients);
    } catch (error) {
        console.error('Error updating dashboard counters:', error);
    }
}

// Update recent patients table
function updateRecentPatientsTable(patients) {
    const tableBody = document.querySelector('#recentPatientsTable tbody');
    if (!tableBody) return;
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    // Sort patients by date added (newest first)
    patients.sort((a, b) => new Date(b.dateAdded) - new Date(a.dateAdded));
    
    // Take only the first 5 patients
    const recentPatients = patients.slice(0, 5);
    
    // Add rows to the table
    recentPatients.forEach(patient => {
        // Determine risk category
        let riskCategory = 'Low';
        let riskClass = 'text-success';
        
        if (patient.riskScore > 0.6) {
            riskCategory = 'High';
            riskClass = 'text-danger';
        } else if (patient.riskScore > 0.3) {
            riskCategory = 'Medium';
            riskClass = 'text-warning';
        }
        
        // Create row HTML
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${patient.patientID}</td>
            <td>${patient.age}</td>
            <td>${patient.tumor_size} mm</td>
            <td>${patient.grade}</td>
            <td class="${riskClass}">${riskCategory}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary view-patient" data-id="${patient.patientID}">
                    <i class="fas fa-eye"></i> View
                </button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // Add event listeners to view buttons
    document.querySelectorAll('.view-patient').forEach(button => {
        button.addEventListener('click', async (event) => {
            const patientID = event.currentTarget.getAttribute('data-id');
            
            try {
                // Get patient data
                const patient = await patientDB.getPatient(patientID);
                
                // Switch to patient tab
                const patientsTab = document.getElementById('patients-tab');
                if (patientsTab) {
                    patientsTab.click();
                }
                
                // Show detailed results
                resultsHandler.showDetailedResults(patient);
            } catch (error) {
                console.error('Error viewing patient:', error);
                alert('Could not retrieve patient data.');
            }
        });
    });
}

// Initialize 3D Body Model
function initializeBodyModel() {
    const modelContainer = document.getElementById('bodyModel3D');
    if (!modelContainer) return;
    
    // Initialize Three.js components
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);
    
    const camera = new THREE.PerspectiveCamera(75, modelContainer.clientWidth / modelContainer.clientHeight, 0.1, 1000);
    camera.position.z = 30;
    
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(modelContainer.clientWidth, modelContainer.clientHeight);
    modelContainer.appendChild(renderer.domElement);
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(0, 1, 1).normalize();
    scene.add(directionalLight);
    
    // Create simple body model
    const bodyGeometry = new THREE.CylinderGeometry(5, 3, 14, 32);
    const bodyMaterial = new THREE.MeshLambertMaterial({ color: 0xffdbac });
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    scene.add(body);
    
    // Create head
    const headGeometry = new THREE.SphereGeometry(2.5, 32, 32);
    const headMaterial = new THREE.MeshLambertMaterial({ color: 0xffdbac });
    const head = new THREE.Mesh(headGeometry, headMaterial);
    head.position.y = 10;
    scene.add(head);
    
    // Create right arm
    const armGeometry = new THREE.CylinderGeometry(1, 1, 10, 32);
    const armMaterial = new THREE.MeshLambertMaterial({ color: 0xffdbac });
    const rightArm = new THREE.Mesh(armGeometry, armMaterial);
    rightArm.position.set(7, 2, 0);
    rightArm.rotation.z = Math.PI / 2;
    scene.add(rightArm);
    
    // Create left arm
    const leftArm = new THREE.Mesh(armGeometry, armMaterial);
    leftArm.position.set(-7, 2, 0);
    leftArm.rotation.z = -Math.PI / 2;
    scene.add(leftArm);
    
    // Create right breast
    const breastGeometry = new THREE.SphereGeometry(1.5, 32, 32);
    const breastMaterial = new THREE.MeshLambertMaterial({ color: 0xffc0a0 });
    const rightBreast = new THREE.Mesh(breastGeometry, breastMaterial);
    rightBreast.position.set(2.5, 4, 4);
    rightBreast.name = 'rightBreast';
    scene.add(rightBreast);
    
    // Create left breast
    const leftBreast = new THREE.Mesh(breastGeometry, breastMaterial);
    leftBreast.position.set(-2.5, 4, 4);
    leftBreast.name = 'leftBreast';
    scene.add(leftBreast);
    
    // Variables for tumor
    let tumor = null;
    
    // Function to update tumor location
    function updateTumorLocation(location) {
        // Remove existing tumor if any
        if (tumor) {
            scene.remove(tumor);
        }
        
        // Create new tumor
        const tumorGeometry = new THREE.SphereGeometry(0.6, 16, 16);
        const tumorMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
        tumor = new THREE.Mesh(tumorGeometry, tumorMaterial);
        
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
    }
    
    // Update tumor location on dropdown change
    const locationSelect = document.getElementById('demoTumorLocation');
    if (locationSelect) {
        locationSelect.addEventListener('change', (event) => {
            updateTumorLocation(event.target.value);
        });
        
        // Set initial tumor location
        updateTumorLocation(locationSelect.value);
    }
    
    // Update tumor size on slider change
    const sizeSlider = document.getElementById('demoTumorSize');
    const sizeValue = document.getElementById('demoSizeValue');
    
    if (sizeSlider) {
        sizeSlider.addEventListener('input', (event) => {
            const size = parseFloat(event.target.value);
            if (sizeValue) {
                sizeValue.textContent = size + 'mm';
            }
            
            if (tumor) {
                // Convert mm to scene units (roughly 1:10 scale)
                const sceneSize = 0.3 + (size / 50);
                tumor.scale.set(sceneSize, sceneSize, sceneSize);
            }
        });
    }
    
    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        
        // Rotate the body slightly
        body.rotation.y += 0.003;
        head.rotation.y += 0.003;
        rightArm.rotation.y += 0.003;
        leftArm.rotation.y += 0.003;
        rightBreast.rotation.y += 0.003;
        leftBreast.rotation.y += 0.003;
        if (tumor) tumor.rotation.y += 0.003;
        
        renderer.render(scene, camera);
    }
    
    // Handle window resize
    window.addEventListener('resize', () => {
        if (modelContainer) {
            const width = modelContainer.clientWidth;
            const height = modelContainer.clientHeight;
            
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
            
            renderer.setSize(width, height);
        }
    });
    
    animate();
    
    // Return control functions
    return {
        updateTumorLocation,
        scene
    };
}

// Handle patient form submission
if (patientForm) {
    patientForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        
        // Collect form data
        const formData = new FormData(patientForm);
        const patientData = {};
        
        // Convert form data to object
        for (const [key, value] of formData.entries()) {
            patientData[key] = value;
        }
        
        try {
            // Add patient to database
            const savedPatient = await patientDB.addPatient(patientData);
            
            // Show success message
            alert('Patient digital twin created successfully!');
            
            // Show detailed results
            resultsHandler.showDetailedResults(savedPatient);
            
            // Update dashboard
            updateDashboardCounters();
            
            // Reset form
            patientForm.reset();
        } catch (error) {
            console.error('Error creating patient:', error);
            alert('Error creating patient digital twin: ' + error);
        }
    });
}

// Handle demo form submission
if (demoForm) {
    demoForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        
        // Collect form data
        const formData = new FormData(demoForm);
        const demoData = {};
        
        // Convert form data to object
        for (const [key, value] of formData.entries()) {
            demoData[key] = value;
        }
        
        // Add demo patient ID and missing fields
        demoData.patientID = 'DEMO-' + Date.now();
        demoData.age = 50;
        demoData.nodes_positive = 0;
        demoData.er_status = 'positive';
        demoData.her2_status = 'negative';
        demoData.menopausal_status = 'post';
        
        // Show results in demo results container
        resultsHandler.showDetailedResults(demoData, document.getElementById('demoResults'));
    });
}

// Initialize body model
const bodyModel = initializeBodyModel();

// Update dashboard on load
updateDashboardCounters();

// Add tab switching functionality
document.querySelectorAll('.nav-tabs .nav-link').forEach(tabLink => {
    tabLink.addEventListener('click', (event) => {
        event.preventDefault();
        
        // Remove active class from all tabs
        document.querySelectorAll('.nav-tabs .nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Add active class to clicked tab
        event.target.classList.add('active');
        
        // Hide all tab panes
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('show', 'active');
        });
        
        // Show the corresponding tab pane
        const target = event.target.getAttribute('href');
        const pane = document.querySelector(target);
        if (pane) {
            pane.classList.add('show', 'active');
        }
    });
}); 