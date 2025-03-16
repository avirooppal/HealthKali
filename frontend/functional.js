/**
 * Cancer Digital Twin Dashboard Functionality
 * This file handles all the interactions and data management
 */

// Initialize database handling
class PatientDatabase {
    constructor() {
        // Use localStorage for simplicity - we can upgrade to IndexedDB later
        this.storageKey = 'cancerDigitalTwinPatients';
        
        // Initialize with sample data if empty
        if (!localStorage.getItem(this.storageKey)) {
            localStorage.setItem(this.storageKey, JSON.stringify([]));
        }
    }
    
    // Get all patients
    getAllPatients() {
        try {
            return JSON.parse(localStorage.getItem(this.storageKey)) || [];
        } catch (error) {
            console.error('Error retrieving patients:', error);
            return [];
        }
    }
    
    // Add a new patient
    addPatient(patientData) {
        try {
            // Get existing patients
            const patients = this.getAllPatients();
            
            // Check if patient ID already exists
            if (patients.some(p => p.patientID === patientData.patientID)) {
                throw new Error('Patient ID already exists');
            }
            
            // Add metadata
            patientData.dateAdded = new Date().toISOString();
            
            // Calculate risk score if not provided
            if (!patientData.riskScore) {
                patientData.riskScore = this.calculateRiskScore(patientData);
            }
            
            // Add to array and save back to storage
            patients.push(patientData);
            localStorage.setItem(this.storageKey, JSON.stringify(patients));
            
            return patientData;
        } catch (error) {
            console.error('Error adding patient:', error);
            throw error;
        }
    }
    
    // Get patient by ID
    getPatient(patientID) {
        try {
            const patients = this.getAllPatients();
            const patient = patients.find(p => p.patientID === patientID);
            
            if (!patient) {
                throw new Error('Patient not found');
            }
            
            return patient;
        } catch (error) {
            console.error('Error getting patient:', error);
            throw error;
        }
    }
    
    // Delete a patient
    deletePatient(patientID) {
        try {
            const patients = this.getAllPatients();
            const updatedPatients = patients.filter(p => p.patientID !== patientID);
            
            localStorage.setItem(this.storageKey, JSON.stringify(updatedPatients));
            return true;
        } catch (error) {
            console.error('Error deleting patient:', error);
            throw error;
        }
    }
    
    // Calculate risk score based on patient data
    calculateRiskScore(patientData) {
        // Basic risk calculation
        const tumorSize = parseFloat(patientData.tumor_size || 0);
        const grade = parseInt(patientData.grade || 1);
        const nodesPositive = parseInt(patientData.nodes_positive || 0);
        const erStatus = patientData.er_status || 'positive';
        const her2Status = patientData.her2_status || 'negative';
        
        let riskScore = (tumorSize * 0.004 + grade * 0.05 + nodesPositive * 0.03);
        
        // Adjust for receptor status
        if (erStatus === 'negative') riskScore += 0.1;
        if (her2Status === 'positive') riskScore += 0.05;
        
        // Cap between 0.1 and 0.9
        riskScore = Math.max(0.1, Math.min(0.9, riskScore));
        
        return riskScore;
    }
    
    // Get risk stats
    getRiskStats() {
        const patients = this.getAllPatients();
        
        return {
            total: patients.length,
            highRisk: patients.filter(p => p.riskScore > 0.6).length,
            mediumRisk: patients.filter(p => p.riskScore > 0.3 && p.riskScore <= 0.6).length,
            lowRisk: patients.filter(p => p.riskScore <= 0.3).length
        };
    }
    
    // Add sample patients for testing
    addSamplePatients() {
        const samplePatients = [
            {
                patientID: "PT001",
                age: 45,
                tumor_size: 15,
                grade: 2,
                nodes_positive: 0,
                er_status: "positive",
                her2_status: "negative",
                menopausal_status: "pre"
            },
            {
                patientID: "PT002",
                age: 67,
                tumor_size: 28,
                grade: 3,
                nodes_positive: 2,
                er_status: "positive",
                her2_status: "positive",
                menopausal_status: "post"
            },
            {
                patientID: "PT003",
                age: 52,
                tumor_size: 12,
                grade: 1,
                nodes_positive: 0,
                er_status: "positive",
                her2_status: "negative",
                menopausal_status: "post"
            }
        ];
        
        // Try to add each sample patient
        samplePatients.forEach(patient => {
            try {
                this.addPatient(patient);
            } catch (error) {
                // Skip if already exists
                console.log(`Sample patient ${patient.patientID} already exists`);
            }
        });
    }
}

// Main dashboard functionality
class Dashboard {
    constructor() {
        this.db = new PatientDatabase();
        this.initEventListeners();
        this.updateDashboard();
    }
    
    // Initialize event listeners
    initEventListeners() {
        // Nav links
        document.querySelectorAll('a[href]').forEach(link => {
            link.addEventListener('click', (e) => {
                // Prevent default for non-tab links
                if (!link.classList.contains('nav-link')) {
                    e.preventDefault();
                    this.handleNavigation(link.getAttribute('href') || '');
                }
            });
        });
        
        // Create new patient link
        const createPatientLink = document.querySelector('a[href*="Create New Patient"]');
        if (createPatientLink) {
            createPatientLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.showCreatePatientForm();
            });
        }
        
        // Add sample data button - we'll add this to the UI
        const mainContainer = document.querySelector('.container-fluid');
        if (mainContainer) {
            const sampleBtn = document.createElement('button');
            sampleBtn.classList.add('btn', 'btn-secondary', 'mt-3');
            sampleBtn.textContent = 'Add Sample Data';
            sampleBtn.addEventListener('click', () => {
                this.db.addSamplePatients();
                this.updateDashboard();
                alert('Sample patients added successfully!');
            });
            
            // Find a good place to insert the button
            const overview = document.querySelector('.patient-overview, h2, h3');
            if (overview) {
                overview.parentNode.insertBefore(sampleBtn, overview.nextSibling);
            } else {
                mainContainer.appendChild(sampleBtn);
            }
        }
    }
    
    // Handle navigation clicks
    handleNavigation(href) {
        console.log('Navigation to:', href);
        
        // Extract the route from the href
        const route = href.replace(/^[/#]+/, '');
        
        switch (route) {
            case 'Create New Patient':
                this.showCreatePatientForm();
                break;
            case 'Profile':
                this.showPatientProfile();
                break;
            case 'Risk Assessment':
                this.showRiskAssessment();
                break;
            case 'Prediction':
                this.showPrediction();
                break;
            case 'Disease Course':
                this.showDiseaseCourse();
                break;
            case 'Treatment Scenarios':
                this.showTreatmentScenarios();
                break;
            case 'Summary Report':
                this.showSummaryReport();
                break;
            default:
                // Default to dashboard
                this.showDashboard();
                break;
        }
    }
    
    // Update dashboard with current stats
    updateDashboard() {
        const stats = this.db.getRiskStats();
        
        // Update counter elements
        this.updateElement('Total Patients', stats.total);
        this.updateElement('High Risk', stats.highRisk);
        this.updateElement('Medium Risk', stats.mediumRisk);
        this.updateElement('Low Risk', stats.lowRisk);
    }
    
    // Helper to update element text content
    updateElement(label, value) {
        // Try different selectors to find the right element
        const selectors = [
            `.card:contains("${label}") h1`,
            `.card:contains("${label}") h3`,
            `.card:contains("${label}") .card-body h1`,
            `.card:contains("${label}") .card-body h3`,
            `h1:contains("${label}")`,
            `h3:contains("${label}")`,
            `div:contains("${label}") h1`,
            `div:contains("${label}") h3`
        ];
        
        // Find the element that contains the label
        let cardElement = null;
        document.querySelectorAll('.card').forEach(card => {
            if (card.textContent.includes(label)) {
                cardElement = card;
            }
        });
        
        if (cardElement) {
            // Find the number element within the card
            const numberElement = cardElement.querySelector('h1') || 
                                  cardElement.querySelector('h3') ||
                                  cardElement.querySelector('div > h1') ||
                                  cardElement.querySelector('div > h3');
            
            if (numberElement) {
                numberElement.textContent = value;
            }
        } else {
            console.warn(`Could not find element for ${label}`);
        }
    }
    
    // Show create patient form
    showCreatePatientForm() {
        // Find main content area
        const mainContent = document.querySelector('.tab-content') || 
                          document.querySelector('main') || 
                          document.querySelector('.container-fluid');
        
        if (!mainContent) {
            console.error('Could not find main content area');
            return;
        }
        
        // Create form HTML
        const formHtml = `
            <div class="card mt-3">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0">Create New Patient</h5>
                </div>
                <div class="card-body">
                    <form id="patientForm">
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="patientID">Patient ID</label>
                                <input type="text" class="form-control" id="patientID" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="age">Age</label>
                                <input type="number" class="form-control" id="age" min="0" max="120" required>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="tumor_size">Tumor Size (mm)</label>
                                <input type="number" class="form-control" id="tumor_size" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="grade">Tumor Grade</label>
                                <select class="form-control" id="grade" required>
                                    <option value="1">Grade 1 (Well-differentiated)</option>
                                    <option value="2">Grade 2 (Moderately-differentiated)</option>
                                    <option value="3">Grade 3 (Poorly-differentiated)</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="nodes_positive">Positive Lymph Nodes</label>
                                <input type="number" class="form-control" id="nodes_positive" value="0" min="0">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="er_status">ER Status</label>
                                <select class="form-control" id="er_status">
                                    <option value="positive">Positive</option>
                                    <option value="negative">Negative</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="her2_status">HER2 Status</label>
                                <select class="form-control" id="her2_status">
                                    <option value="negative">Negative</option>
                                    <option value="positive">Positive</option>
                                </select>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="menopausal_status">Menopausal Status</label>
                                <select class="form-control" id="menopausal_status">
                                    <option value="pre">Pre-menopausal</option>
                                    <option value="post">Post-menopausal</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="text-center mt-4">
                            <button type="submit" class="btn btn-primary">Create Digital Twin</button>
                            <button type="button" class="btn btn-secondary" id="cancelBtn">Cancel</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        
        // Create a container for the form
        const formContainer = document.createElement('div');
        formContainer.innerHTML = formHtml;
        
        // Clear content area and append form
        this.clearTabContent();
        mainContent.appendChild(formContainer);
        
        // Add form submission handler
        const form = document.getElementById('patientForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.savePatient();
            });
        }
        
        // Add cancel button handler
        const cancelBtn = document.getElementById('cancelBtn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.showDashboard();
            });
        }
    }
    
    // Save patient from form
    savePatient() {
        try {
            // Collect form data
            const patientData = {
                patientID: document.getElementById('patientID').value,
                age: parseInt(document.getElementById('age').value),
                tumor_size: parseFloat(document.getElementById('tumor_size').value),
                grade: parseInt(document.getElementById('grade').value),
                nodes_positive: parseInt(document.getElementById('nodes_positive').value),
                er_status: document.getElementById('er_status').value,
                her2_status: document.getElementById('her2_status').value,
                menopausal_status: document.getElementById('menopausal_status').value
            };
            
            // Save to database
            this.db.addPatient(patientData);
            
            // Show success message
            alert('Patient digital twin created successfully!');
            
            // Return to dashboard
            this.showDashboard();
        } catch (error) {
            alert('Error creating patient: ' + error.message);
        }
    }
    
    // Show dashboard
    showDashboard() {
        // Return to dashboard tab
        const dashboardTab = document.querySelector('[href="Dashboard"]') || 
                            document.querySelector('[href="#Dashboard"]');
        if (dashboardTab) {
            dashboardTab.click();
        }
        
        // Update counters
        this.updateDashboard();
    }
    
    // Clear tab content for new views
    clearTabContent() {
        const tabContent = document.querySelector('.tab-pane.active .row') || 
                          document.querySelector('.tab-pane.active') ||
                          document.querySelector('.tab-content');
        
        if (tabContent) {
            // Save the first row with counters
            const firstRow = tabContent.querySelector('.row:first-child');
            if (firstRow && firstRow.innerHTML.includes('Total Patients')) {
                // Keep the first row, remove others
                Array.from(tabContent.children).forEach((child, index) => {
                    if (index > 0 && child !== firstRow) {
                        child.remove();
                    }
                });
            } else {
                // Clear all
                tabContent.innerHTML = '';
            }
        }
    }
    
    // Placeholder methods for other views
    showPatientProfile() {
        alert('Patient Profile functionality will be implemented soon!');
    }
    
    showRiskAssessment() {
        alert('Risk Assessment functionality will be implemented soon!');
    }
    
    showPrediction() {
        alert('Prediction functionality will be implemented soon!');
    }
    
    showDiseaseCourse() {
        alert('Disease Course functionality will be implemented soon!');
    }
    
    showTreatmentScenarios() {
        alert('Treatment Scenarios functionality will be implemented soon!');
    }
    
    showSummaryReport() {
        alert('Summary Report functionality will be implemented soon!');
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard
    window.dashboard = new Dashboard();
    
    // jQuery-like contains selector
    if (!Element.prototype.matches) {
        Element.prototype.matches = Element.prototype.msMatchesSelector || 
                                   Element.prototype.webkitMatchesSelector;
    }
    
    if (!Element.prototype.closest) {
        Element.prototype.closest = function(s) {
            var el = this;
            do {
                if (el.matches(s)) return el;
                el = el.parentElement || el.parentNode;
            } while (el !== null && el.nodeType === 1);
            return null;
        };
    }
}); 