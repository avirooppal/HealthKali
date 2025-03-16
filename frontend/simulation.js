/**
 * Simulation page functionality for Cancer Digital Twin
 */

import digitalTwinAPI from './api.js';

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the simulation page
    if (!document.querySelector('.simulation-types')) return;
    
    // Tab switching functionality
    const simulationTabs = document.querySelectorAll('.simulation-tab');
    const simulationPanels = document.querySelectorAll('.simulation-panel');
    
    simulationTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and panels
            simulationTabs.forEach(t => t.classList.remove('active'));
            simulationPanels.forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked tab
            tab.classList.add('active');
            
            // Show corresponding panel
            const targetId = tab.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');
        });
    });
    
    // Disease Course Simulation
    const runDiseaseBtn = document.getElementById('runDiseaseSimulation');
    if (runDiseaseBtn) {
        runDiseaseBtn.addEventListener('click', runDiseaseSimulation);
    }
    
    // Treatment Scenarios Simulation
    const runScenariosBtn = document.getElementById('runScenariosSimulation');
    if (runScenariosBtn) {
        runScenariosBtn.addEventListener('click', runScenariosSimulation);
    }
    
    // Add scenario button
    const addScenarioBtn = document.getElementById('addScenario');
    if (addScenarioBtn) {
        addScenarioBtn.addEventListener('click', addScenario);
    }
    
    // Molecular Subtypes Simulation
    const runSubtypesBtn = document.getElementById('runSubtypesSimulation');
    if (runSubtypesBtn) {
        runSubtypesBtn.addEventListener('click', runSubtypesSimulation);
    }
    
    // Track number of scenarios
    let scenarioCount = 2;
    
    // --- Disease Course Simulation Functions ---
    async function runDiseaseSimulation() {
        // Show loading
        document.getElementById('diseaseLoadingIndicator').style.display = 'flex';
        document.getElementById('diseaseResultsContainer').querySelector('.simulation-summary').innerHTML = '';
        document.querySelector('.state-trajectories').style.display = 'none';
        document.querySelector('.tumor-growth').style.display = 'none';
        document.querySelector('.simulation-details').style.display = 'none';
        
        // Get patient data
        const patientData = {
            age: parseInt(document.getElementById('dc-patientAge').value),
            tumor_size: parseInt(document.getElementById('dc-tumorSize').value),
            grade: parseInt(document.getElementById('dc-tumorGrade').value),
            nodes_positive: parseInt(document.getElementById('dc-nodesPositive').value),
            er_status: document.getElementById('dc-erStatus').value,
            her2_status: document.getElementById('dc-her2Status').value
        };
        
        // Get simulation parameters
        const months = parseInt(document.getElementById('dc-months').value);
        const numSimulations = parseInt(document.getElementById('dc-simulations').value);
        
        // Get treatment data if any
        const treatmentPlan = {
            treatments: []
        };
        
        if (document.getElementById('dc-surgery').checked) treatmentPlan.treatments.push('surgery');
        if (document.getElementById('dc-chemotherapy').checked) treatmentPlan.treatments.push('chemotherapy');
        if (document.getElementById('dc-radiation').checked) treatmentPlan.treatments.push('radiation');
        if (document.getElementById('dc-endocrine').checked) treatmentPlan.treatments.push('endocrine');
        if (document.getElementById('dc-targeted').checked) treatmentPlan.treatments.push('targeted');
        
        try {
            // Call API
            const result = await digitalTwinAPI.fetchAPI('/simulation/disease_course', 'POST', {
                patient: patientData,
                treatment: treatmentPlan.treatments.length > 0 ? treatmentPlan : null,
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
            // Hide loading
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
        document.querySelector('.state-trajectories').style.display = 'block';
        
        // Create state trajectory chart
        createStateTrajectoryChart(result.state_probability_trajectory);
        
        // Show tumor growth if available
        if (result.tumor_growth_trajectory && result.tumor_growth_trajectory.length > 0) {
            document.querySelector('.tumor-growth').style.display = 'block';
            createTumorGrowthChart(result.tumor_growth_trajectory);
        }
        
        // Show simulation details
        document.querySelector('.simulation-details').style.display = 'block';
        
        // Display simulation details
        displaySimulationDetails(result);
    }
    
    function createStateTrajectoryChart(trajectoryPoints) {
        const ctx = document.getElementById('stateTrajectoryChart').getContext('2d');
        
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
    
    function createTumorGrowthChart(tumorGrowthTrajectory) {
        const ctx = document.getElementById('tumorGrowthChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (window.tumorGrowthChart) {
            window.tumorGrowthChart.destroy();
        }
        
        // Prepare data
        const months = tumorGrowthTrajectory.map(point => `Month ${point.month}`);
        const tumorSizes = tumorGrowthTrajectory.map(point => point.tumor_size);
        
        // Create chart
        window.tumorGrowthChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Tumor Size',
                    data: tumorSizes,
                    backgroundColor: 'rgba(14, 165, 233, 0.2)',
                    borderColor: 'rgba(14, 165, 233, 1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        min: 0,
                        title: {
                            display: true,
                            text: 'Tumor Size'
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
                                return `Tumor Size: ${context.parsed.y.toFixed(2)}`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    function displaySimulationDetails(result) {
        const detailsContainer = document.getElementById('simulationDetailsContainer');
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
    
    function addScenario() {
        scenarioCount++;
        const scenariosContainer = document.getElementById('scenariosContainer');
        const newScenario = document.createElement('div');
        newScenario.className = 'scenario-card';
        newScenario.innerHTML = `
            <div class="scenario-header">
                <h4>Scenario ${scenarioCount}</h4>
                <button class="remove-scenario-btn" data-scenario="${scenarioCount}">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="treatment-options">
                <label><input type="checkbox" name="scenario${scenarioCount}-surgery"> Surgery</label>
                <label><input type="checkbox" name="scenario${scenarioCount}-chemotherapy"> Chemotherapy</label>
                <label><input type="checkbox" name="scenario${scenarioCount}-radiation"> Radiation</label>
                <label><input type="checkbox" name="scenario${scenarioCount}-endocrine"> Endocrine Therapy</label>
                <label><input type="checkbox" name="scenario${scenarioCount}-targeted"> Targeted Therapy</label>
            </div>
        `;
        
        scenariosContainer.appendChild(newScenario);
        
        // Add event listener to remove button
        newScenario.querySelector('.remove-scenario-btn').addEventListener('click', function() {
            const scenarioNum = this.getAttribute('data-scenario');
            removeScenario(scenarioNum);
        });
    }
    
    function removeScenario(scenarioNum) {
        const scenarios = document.querySelectorAll('.scenario-card');
        
        // Find the scenario to remove
        for (const scenario of scenarios) {
            const header = scenario.querySelector('.scenario-header h4');
            if (header && header.textContent === `Scenario ${scenarioNum}`) {
                scenario.remove();
                break;
            }
        }
        
        // No need to renumber scenarios for simplicity
    }
    
    function runScenariosSimulation() {
        // Implementation of runScenariosSimulation function
    }
    
    function runSubtypesSimulation() {
        // Implementation of runSubtypesSimulation function
    }
}); 

function createTreatmentTimeline(patientData) {
    const timelineContainer = document.getElementById('treatmentTimeline');
    if (!timelineContainer) return;
    
    // Generate treatment timeline based on recommendations
    const tumorSize = parseFloat(patientData.tumor_size);
    const nodesPositive = parseInt(patientData.nodes_positive);
    const erStatus = patientData.er_status;
    const her2Status = patientData.her2_status;
    
    // Create SVG timeline
    const svgNamespace = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNamespace, "svg");
    svg.setAttribute("width", "100%");
    svg.setAttribute("height", "100");
    svg.style.overflow = "visible";
    
    // Create timeline base line
    const timeline = document.createElementNS(svgNamespace, "line");
    timeline.setAttribute("x1", "0");
    timeline.setAttribute("y1", "50");
    timeline.setAttribute("x2", "100%");
    timeline.setAttribute("y2", "50");
    timeline.setAttribute("stroke", "rgba(56, 189, 248, 0.5)");
    timeline.setAttribute("stroke-width", "2");
    svg.appendChild(timeline);
    
    // Add month markers
    for (let month = 0; month <= 60; month += 12) {
        const x = (month / 60) * 100;
        
        // Marker line
        const markerLine = document.createElementNS(svgNamespace, "line");
        markerLine.setAttribute("x1", `${x}%`);
        markerLine.setAttribute("y1", "45");
        markerLine.setAttribute("x2", `${x}%`);
        markerLine.setAttribute("y2", "55");
        markerLine.setAttribute("stroke", "rgba(56, 189, 248, 0.8)");
        markerLine.setAttribute("stroke-width", "1");
        svg.appendChild(markerLine);
        
        // Month label
        const markerText = document.createElementNS(svgNamespace, "text");
        markerText.setAttribute("x", `${x}%`);
        markerText.setAttribute("y", "70");
        markerText.setAttribute("text-anchor", "middle");
        markerText.setAttribute("fill", "#94a3b8");
        markerText.setAttribute("font-size", "12");
        markerText.textContent = `${month}m`;
        svg.appendChild(markerText);
    }
    
    // Add treatment bars
    const treatments = [];
    
    // Surgery (Month 0-1)
    treatments.push({
        name: tumorSize > 50 ? "Mastectomy" : "Lumpectomy",
        start: 0,
        end: 1,
        color: "#0ea5e9"
    });
    
    // Chemotherapy (if applicable, typically months 1-4)
    if (nodesPositive > 0 || erStatus === 'negative' || her2Status === 'positive') {
        treatments.push({
            name: "Chemotherapy",
            start: 1,
            end: 5,
            color: "#ef4444"
        });
    }
    
    // Radiation (after surgery or chemo, typically 3-6 months)
    const radStart = treatments.length > 1 ? 5 : 1;
    treatments.push({
        name: "Radiation",
        start: radStart,
        end: radStart + 2,
        color: "#f59e0b"
    });
    
    // Endocrine therapy (if ER+, starts after chemo/radiation, lasts 5-10 years)
    if (erStatus === 'positive') {
        treatments.push({
            name: "Endocrine therapy",
            start: Math.max(radStart + 2, 6),
            end: 60, // 5 years
            color: "#10b981"
        });
    }
    
    // HER2-targeted therapy (if HER2+, typically with chemo and then continues for a year)
    if (her2Status === 'positive') {
        treatments.push({
            name: "HER2-targeted",
            start: 1,
            end: 13, // 1 year
            color: "#8b5cf6"
        });
    }
    
    // Draw treatment bars
    const barHeight = 15;
    const barSpacing = 20;
    
    treatments.forEach((treatment, index) => {
        const yPos = 20 + (index * barSpacing);
        const startX = (treatment.start / 60) * 100;
        const endX = (treatment.end / 60) * 100;
        const width = endX - startX;
        
        // Treatment bar
        const bar = document.createElementNS(svgNamespace, "rect");
        bar.setAttribute("x", `${startX}%`);
        bar.setAttribute("y", yPos);
        bar.setAttribute("width", `${width}%`);
        bar.setAttribute("height", barHeight);
        bar.setAttribute("rx", "4");
        bar.setAttribute("ry", "4");
        bar.setAttribute("fill", treatment.color);
        bar.setAttribute("opacity", "0.7");
        svg.appendChild(bar);
        
        // Treatment label
        const label = document.createElementNS(svgNamespace, "text");
        label.setAttribute("x", `${startX + 1}%`);
        label.setAttribute("y", yPos + barHeight / 2 + 4);
        label.setAttribute("fill", "white");
        label.setAttribute("font-size", "10");
        label.setAttribute("font-weight", "bold");
        label.textContent = treatment.name;
        svg.appendChild(label);
    });
    
    // Adjust SVG height based on number of treatments
    svg.setAttribute("height", 40 + treatments.length * barSpacing);
    
    // Add to container
    timelineContainer.appendChild(svg);
} 