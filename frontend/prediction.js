/**
 * Prediction page functionality for Cancer Digital Twin
 */

import digitalTwinAPI from './api.js';

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the prediction page
    if (!document.querySelector('.prediction-types')) return;
    
    // Tab switching functionality
    const predictionTabs = document.querySelectorAll('.prediction-tab');
    const predictionPanels = document.querySelectorAll('.prediction-panel');
    
    predictionTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and panels
            predictionTabs.forEach(t => t.classList.remove('active'));
            predictionPanels.forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked tab
            tab.classList.add('active');
            
            // Show corresponding panel
            const targetId = tab.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');
        });
    });
    
    // Survival Prediction
    const runSurvivalBtn = document.getElementById('runSurvivalPrediction');
    if (runSurvivalBtn) {
        runSurvivalBtn.addEventListener('click', runSurvivalPrediction);
    }
    
    // Recurrence Prediction
    const runRecurrenceBtn = document.getElementById('runRecurrencePrediction');
    if (runRecurrenceBtn) {
        runRecurrenceBtn.addEventListener('click', runRecurrencePrediction);
    }
    
    // Treatment Response Prediction
    const runTreatmentBtn = document.getElementById('runTreatmentPrediction');
    if (runTreatmentBtn) {
        runTreatmentBtn.addEventListener('click', runTreatmentResponsePrediction);
    }
    
    // --- Survival Prediction Functions ---
    async function runSurvivalPrediction() {
        // Show loading
        document.getElementById('survivalLoadingIndicator').style.display = 'flex';
        document.getElementById('survivalResultsContainer').querySelector('.prediction-summary').innerHTML = '';
        document.querySelector('.chart-container').style.display = 'none';
        document.querySelector('.risk-factors').style.display = 'none';
        
        // Get patient data
        const patientData = {
            age: parseInt(document.getElementById('sp-patientAge').value),
            tumor_size: parseInt(document.getElementById('sp-tumorSize').value),
            grade: parseInt(document.getElementById('sp-tumorGrade').value),
            nodes_positive: parseInt(document.getElementById('sp-nodesPositive').value),
            er_status: document.getElementById('sp-erStatus').value,
            her2_status: document.getElementById('sp-her2Status').value
        };
        
        const years = parseInt(document.getElementById('sp-years').value);
        
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
            // Hide loading
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
    
    // --- Recurrence Prediction Functions ---
    async function runRecurrencePrediction() {
        // Show loading
        document.getElementById('recurrenceLoadingIndicator').style.display = 'flex';
        document.getElementById('recurrenceResultsContainer').querySelector('.prediction-summary').innerHTML = '';
        document.querySelector('.recurrence-breakdown').style.display = 'none';
        document.querySelector('.recurrence-timeline').style.display = 'none';
        
        // Get patient data
        const patientData = {
            age: parseInt(document.getElementById('rp-patientAge').value),
            tumor_size: parseInt(document.getElementById('rp-tumorSize').value),
            grade: parseInt(document.getElementById('rp-tumorGrade').value),
            nodes_positive: parseInt(document.getElementById('rp-nodesPositive').value),
            er_status: document.getElementById('rp-erStatus').value,
            her2_status: document.getElementById('rp-her2Status').value
        };
        
        const years = parseInt(document.getElementById('rp-years').value);
        
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
            // Hide loading
            document.getElementById('recurrenceLoadingIndicator').style.display = 'none';
        }
    }
    
    function displayRecurrenceResults(result) {
        // Set summary
        const summaryElement = document.getElementById('recurrenceResultsContainer').querySelector('.prediction-summary');
        summaryElement.innerHTML = `
            <div class="prediction-result">
                <h4>${result.recurrence_category || 'Intermediate Risk'}</h4>
                <p class="main-result">5-Year Recurrence Risk: <strong>${(result.total_recurrence_5yr * 100).toFixed(1)}%</strong></p>
                <p>This patient's recurrence risk is distributed across local, regional, and distant sites. The prediction represents the most likely outcome based on similar patients in our database.</p>
            </div>
        `;
        
        // Show recurrence breakdown
        document.querySelector('.recurrence-breakdown').style.display = 'block';
        
        // Create breakdown chart
        createRecurrenceBreakdownChart(result.recurrence_breakdown);
        
        // Show recurrence timeline
        document.querySelector('.recurrence-timeline').style.display = 'block';
        
        // Create timeline chart
        createRecurrenceTimelineChart(result.recurrence_curves);
    }
    
    function createRecurrenceBreakdownChart(recurrenceBreakdown) {
        const ctx = document.getElementById('recurrenceChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (window.recurrenceChart) {
            window.recurrenceChart.destroy();
        }
        
        // Prepare data
        const labels = Object.keys(recurrenceBreakdown).map(key => {
            if (key === 'local_recurrence') return 'Local';
            if (key === 'regional_recurrence') return 'Regional';
            if (key === 'distant_metastasis') return 'Distant';
            return key;
        });
        
        const data = Object.values(recurrenceBreakdown).map(val => val * 100);
        
        // Create chart
        window.recurrenceChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Recurrence Risk (%)',
                    data: data,
                    backgroundColor: [
                        'rgba(255, 170, 0, 0.7)',   // Orange for local
                        'rgba(255, 100, 0, 0.7)',   // Darker orange for regional
                        'rgba(220, 50, 50, 0.7)'    // Red for distant
                    ],
                    borderColor: [
                        'rgba(255, 170, 0, 1)',
                        'rgba(255, 100, 0, 1)',
                        'rgba(220, 50, 50, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        min: 0,
                        max: Math.max(20, Math.ceil(Math.max(...data))),
                        title: {
                            display: true,
                            text: 'Risk (%)'
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Risk: ${context.parsed.y.toFixed(1)}%`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    function createRecurrenceTimelineChart(recurrenceCurves) {
        const ctx = document.getElementById('recurrenceTimelineChart').getContext('2d');
        
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
    
    // --- Treatment Response Prediction Functions ---
    async function runTreatmentResponsePrediction() {
        // Show loading
        document.getElementById('treatmentLoadingIndicator').style.display = 'flex';
        document.getElementById('treatmentResultsContainer').querySelector('.prediction-summary').innerHTML = '';
        document.querySelector('.treatment-efficacy').style.display = 'none';
        document.querySelector('.side-effects').style.display = 'none';
        
        // Get patient data
        const patientData = {
            age: parseInt(document.getElementById('tp-patientAge').value),
            tumor_size: parseInt(document.getElementById('tp-tumorSize').value),
            grade: parseInt(document.getElementById('tp-tumorGrade').value),
            er_status: document.getElementById('tp-erStatus').value,
            her2_status: document.getElementById('tp-her2Status').value
        };
        
        // Get treatment data
        const treatmentPlan = {
            treatments: []
        };
        
        if (document.getElementById('tp-surgery').checked) treatmentPlan.treatments.push('surgery');
        if (document.getElementById('tp-chemotherapy').checked) treatmentPlan.treatments.push('chemotherapy');
        if (document.getElementById('tp-radiation').checked) treatmentPlan.treatments.push('radiation');
        if (document.getElementById('tp-endocrine').checked) treatmentPlan.treatments.push('endocrine');
        if (document.getElementById('tp-targeted').checked) treatmentPlan.treatments.push('targeted');
        
        try {
            // Call API
            const result = await digitalTwinAPI.fetchAPI('/prediction/treatment_response', 'POST', {
                patient: patientData,
                treatment: treatmentPlan
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
            // Hide loading
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
        document.querySelector('.treatment-efficacy').style.display = 'block';
        
        // Create efficacy chart
        createEfficacyChart(result.treatment_specific_responses);
        
        // Show side effects
        document.querySelector('.side-effects').style.display = 'block';
        
        // Display side effects
        displaySideEffects(result.side_effect_probabilities);
    }
    
    function createEfficacyChart(treatmentResponses) {
        const ctx = document.getElementById('efficacyChart').getContext('2d');
        
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
}); 