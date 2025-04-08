// Dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all charts and components
    initializeCharts();
    setupEventListeners();
});

function initializeCharts() {
    // Risk Assessment Chart
    const riskCtx = document.getElementById('riskFactorsChart').getContext('2d');
    new Chart(riskCtx, {
        type: 'radar',
        data: {
            labels: ['Genetic', 'Environmental', 'Lifestyle', 'Clinical', 'Demographic'],
            datasets: [{
                label: 'Risk Factors',
                data: [0, 0, 0, 0, 0],
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });

    // Progression Prediction Chart
    const progressionCtx = document.getElementById('progressionChart').getContext('2d');
    new Chart(progressionCtx, {
        type: 'line',
        data: {
            labels: ['Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Month 6'],
            datasets: [{
                label: 'Predicted Progression',
                data: [0, 0, 0, 0, 0, 0],
                borderColor: 'rgba(75, 192, 192, 1)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Simulation Chart
    const simulationCtx = document.getElementById('simulationChart').getContext('2d');
    new Chart(simulationCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Simulation Results',
                data: [],
                borderColor: 'rgba(153, 102, 255, 1)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            animation: false
        }
    });

    // Disease Timeline Chart
    const timelineCtx = document.getElementById('diseaseTimelineChart').getContext('2d');
    new Chart(timelineCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Disease Progression',
                data: [],
                borderColor: 'rgba(255, 159, 64, 1)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true
        }
    });

    // Scenario Comparison Chart
    const scenarioCtx = document.getElementById('scenarioComparisonChart').getContext('2d');
    new Chart(scenarioCtx, {
        type: 'bar',
        data: {
            labels: ['Scenario 1', 'Scenario 2', 'Scenario 3'],
            datasets: [{
                label: 'Success Rate',
                data: [0, 0, 0],
                backgroundColor: 'rgba(54, 162, 235, 0.5)'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });

    // Subtype Analysis Chart
    const subtypeCtx = document.getElementById('subtypeAnalysisChart').getContext('2d');
    new Chart(subtypeCtx, {
        type: 'pie',
        data: {
            labels: ['Subtype A', 'Subtype B', 'Subtype C'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 206, 86, 0.5)'
                ]
            }]
        },
        options: {
            responsive: true
        }
    });
}

function setupEventListeners() {
    // Simulation Controls
    document.getElementById('startSimulation').addEventListener('click', startSimulation);
    document.getElementById('pauseSimulation').addEventListener('click', pauseSimulation);
    document.getElementById('resetSimulation').addEventListener('click', resetSimulation);

    // Report Generation
    document.getElementById('generateReport').addEventListener('click', generateReport);
    document.getElementById('downloadReport').addEventListener('click', downloadReport);

    // Export Data
    document.getElementById('exportData').addEventListener('click', exportData);

    // Treatment Scenarios
    const treatmentScenariosLink = document.querySelector('a[data-section="treatment-scenarios"]');
    if (treatmentScenariosLink) {
        treatmentScenariosLink.addEventListener('click', function(e) {
            e.preventDefault();
            initializeTreatmentScenarios();
        });
    }
}

// Simulation Functions
let simulationInterval;
let isSimulationRunning = false;

function startSimulation() {
    if (!isSimulationRunning) {
        isSimulationRunning = true;
        simulationInterval = setInterval(updateSimulation, 1000);
    }
}

function pauseSimulation() {
    isSimulationRunning = false;
    clearInterval(simulationInterval);
}

function resetSimulation() {
    pauseSimulation();
    // Reset simulation data
    const chart = Chart.getChart('simulationChart');
    if (chart) {
        chart.data.labels = [];
        chart.data.datasets[0].data = [];
        chart.update();
    }
}

function updateSimulation() {
    // Update simulation data
    const chart = Chart.getChart('simulationChart');
    if (chart) {
        const currentTime = chart.data.labels.length;
        chart.data.labels.push(`Time ${currentTime + 1}`);
        chart.data.datasets[0].data.push(Math.random() * 100);
        chart.update();
    }
}

// Treatment Recommendations Data
const treatmentRecommendations = {
    standardTreatments: [
        {
            name: 'Chemotherapy',
            description: 'Standard chemotherapy regimen using common cancer drugs',
            duration: '4-6 months',
            frequency: 'Every 3 weeks',
            cost: {
                perCycle: 5000,
                total: 30000,
                insurance: 'Usually covered',
                outOfPocket: '20-30%'
            },
            sideEffects: ['Nausea', 'Fatigue', 'Hair Loss', 'Decreased Blood Counts'],
            successRate: '70-80%'
        },
        {
            name: 'Radiation Therapy',
            description: 'Targeted radiation treatment to specific areas',
            duration: '6-8 weeks',
            frequency: '5 times per week',
            cost: {
                perSession: 2000,
                total: 40000,
                insurance: 'Usually covered',
                outOfPocket: '10-20%'
            },
            sideEffects: ['Skin Changes', 'Fatigue', 'Local Pain'],
            successRate: '75-85%'
        }
    ],
    targetedTherapies: [
        {
            name: 'HER2-Targeted Therapy',
            description: 'Monoclonal antibody treatment targeting HER2 receptors',
            duration: '12 months',
            frequency: 'Every 3 weeks',
            cost: {
                perCycle: 8000,
                total: 120000,
                insurance: 'Usually covered with prior authorization',
                outOfPocket: '30-40%'
            },
            sideEffects: ['Cardiac Effects', 'Infusion Reactions', 'Diarrhea'],
            successRate: '80-90%'
        },
        {
            name: 'Hormone Therapy',
            description: 'Treatment targeting hormone receptors',
            duration: '5-10 years',
            frequency: 'Daily oral medication',
            cost: {
                perMonth: 500,
                total: 30000,
                insurance: 'Usually covered',
                outOfPocket: '10-20%'
            },
            sideEffects: ['Hot Flashes', 'Joint Pain', 'Mood Changes'],
            successRate: '75-85%'
        }
    ],
    immunotherapy: [
        {
            name: 'PD-1/PD-L1 Inhibitor',
            description: 'Immune checkpoint inhibitor therapy',
            duration: '12-24 months',
            frequency: 'Every 2-4 weeks',
            cost: {
                perCycle: 12000,
                total: 180000,
                insurance: 'Usually covered with prior authorization',
                outOfPocket: '40-50%'
            },
            sideEffects: ['Immune Reactions', 'Fatigue', 'Skin Changes'],
            successRate: '85-95%'
        }
    ]
};

// Update the generateReport function
function generateReport() {
    const reportContent = document.getElementById('reportContent');
    reportContent.innerHTML = `
        <h3>Patient Summary Report</h3>
        <div class="report-section">
            <h4>Risk Assessment</h4>
            <p>Current risk score: <span id="reportRiskScore">0</span></p>
        </div>
        <div class="report-section">
            <h4>Predictions</h4>
            <p>Predicted progression: <span id="reportProgression">0</span></p>
        </div>
        <div class="report-section">
            <h4>Treatment Recommendations</h4>
            <div class="treatment-recommendations">
                <div class="treatment-category">
                    <h5>Standard Treatments</h5>
                    ${generateTreatmentCards(treatmentRecommendations.standardTreatments)}
                </div>
                <div class="treatment-category">
                    <h5>Targeted Therapies</h5>
                    ${generateTreatmentCards(treatmentRecommendations.targetedTherapies)}
                </div>
                <div class="treatment-category">
                    <h5>Immunotherapy</h5>
                    ${generateTreatmentCards(treatmentRecommendations.immunotherapy)}
                </div>
            </div>
        </div>
    `;
}

function generateTreatmentCards(treatments) {
    return treatments.map(treatment => `
        <div class="treatment-card">
            <div class="treatment-header">
                <h6>${treatment.name}</h6>
                <span class="success-rate">${treatment.successRate} Success Rate</span>
            </div>
            <p class="treatment-description">${treatment.description}</p>
            <div class="treatment-details">
                <div class="detail-row">
                    <span class="detail-label">Duration:</span>
                    <span class="detail-value">${treatment.duration}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Frequency:</span>
                    <span class="detail-value">${treatment.frequency}</span>
                </div>
            </div>
            <div class="cost-breakdown">
                <h6>Cost Breakdown</h6>
                <div class="cost-details">
                    <div class="cost-row">
                        <span class="cost-label">Per Cycle/Session:</span>
                        <span class="cost-value">$${treatment.cost.perCycle.toLocaleString()}</span>
                    </div>
                    <div class="cost-row">
                        <span class="cost-label">Total Cost:</span>
                        <span class="cost-value">$${treatment.cost.total.toLocaleString()}</span>
                    </div>
                    <div class="cost-row">
                        <span class="cost-label">Insurance Coverage:</span>
                        <span class="cost-value">${treatment.cost.insurance}</span>
                    </div>
                    <div class="cost-row">
                        <span class="cost-label">Estimated Out-of-Pocket:</span>
                        <span class="cost-value">${treatment.cost.outOfPocket}</span>
                    </div>
                </div>
            </div>
            <div class="side-effects">
                <h6>Common Side Effects</h6>
                <div class="side-effects-list">
                    ${treatment.sideEffects.map(effect => 
                        `<span class="side-effect-badge">${effect}</span>`
                    ).join('')}
                </div>
            </div>
        </div>
    `).join('');
}

function downloadReport() {
    // Implementation for PDF download
    console.log('Downloading report...');
}

// Export Data
function exportData() {
    const format = document.getElementById('exportFormat').value;
    const selectedData = {
        patient: document.getElementById('patientData').checked,
        analysis: document.getElementById('analysisData').checked,
        predictions: document.getElementById('predictionsData').checked
    };

    // Implementation for data export
    console.log(`Exporting data in ${format} format:`, selectedData);
}

// Update dashboard data
function updateDashboardData(data) {
    // Update risk score
    document.getElementById('riskScore').textContent = data.riskScore || 0;

    // Update charts with new data
    updateCharts(data);
}

function updateCharts(data) {
    // Update each chart with new data
    // Implementation depends on the data structure
    console.log('Updating charts with:', data);
}

// Treatment Scenarios Functions
function initializeTreatmentScenarios() {
    const scenarios = [
        {
            name: 'Standard Treatment',
            description: 'Conventional chemotherapy followed by radiation therapy',
            successRate: 75,
            sideEffects: ['Nausea', 'Fatigue', 'Hair Loss'],
            duration: '6 months',
            cost: 'Standard'
        },
        {
            name: 'Targeted Therapy',
            description: 'HER2-targeted therapy with chemotherapy',
            successRate: 85,
            sideEffects: ['Cardiac Effects', 'Infusion Reactions'],
            duration: '12 months',
            cost: 'High'
        },
        {
            name: 'Combination Approach',
            description: 'Combined chemotherapy, targeted therapy, and immunotherapy',
            successRate: 90,
            sideEffects: ['Immune Reactions', 'Fatigue', 'Skin Changes'],
            duration: '18 months',
            cost: 'Very High'
        }
    ];

    // Update scenario comparison chart
    const scenarioCtx = document.getElementById('scenarioComparisonChart');
    if (scenarioCtx) {
        new Chart(scenarioCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: scenarios.map(s => s.name),
                datasets: [{
                    label: 'Success Rate (%)',
                    data: scenarios.map(s => s.successRate),
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    // Update scenario details
    const scenarioDetails = document.getElementById('scenarioDetails');
    if (scenarioDetails) {
        scenarioDetails.innerHTML = scenarios.map(scenario => `
            <div class="scenario-card">
                <h6>${scenario.name}</h6>
                <p class="mb-2">${scenario.description}</p>
                <div class="scenario-metrics">
                    <div class="row">
                        <div class="col-6">
                            <small class="text-muted">Success Rate</small>
                            <div class="h5 mb-0">${scenario.successRate}%</div>
                        </div>
                        <div class="col-6">
                            <small class="text-muted">Duration</small>
                            <div class="h5 mb-0">${scenario.duration}</div>
                        </div>
                    </div>
                    <div class="mt-2">
                        <small class="text-muted">Common Side Effects</small>
                        <div class="side-effects">
                            ${scenario.sideEffects.map(effect => 
                                `<span class="badge bg-light text-dark me-1">${effect}</span>`
                            ).join('')}
                        </div>
                    </div>
                    <div class="mt-2">
                        <small class="text-muted">Cost Level</small>
                        <div class="cost-level">
                            <span class="badge ${getCostBadgeClass(scenario.cost)}">${scenario.cost}</span>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }
}

function getCostBadgeClass(cost) {
    switch(cost.toLowerCase()) {
        case 'standard':
            return 'bg-success';
        case 'high':
            return 'bg-warning';
        case 'very high':
            return 'bg-danger';
        default:
            return 'bg-secondary';
    }
} 