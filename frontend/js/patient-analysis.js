async function displayPatientAnalysis(patientData) {
    try {
        // Show loading state
        const resultsContainer = document.getElementById('analysisResults');
        resultsContainer.innerHTML = '<div class="loader">Analyzing patient data...</div>';
        
        // Call API
        const response = await fetch('/api/patient/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(patientData)
        });
        
        const analysis = await response.json();
        
        // Create detailed HTML display
        const resultsHTML = `
            <div class="analysis-container">
                <div class="risk-summary card">
                    <h3>Risk Assessment</h3>
                    <div class="risk-badge ${analysis.patient_summary.risk_category.toLowerCase()}">
                        ${analysis.patient_summary.risk_category} Risk
                    </div>
                    <div class="risk-score">
                        Score: ${analysis.patient_summary.risk_score}
                    </div>
                </div>
                
                <div class="survival-analysis card">
                    <h3>Survival Analysis</h3>
                    <div class="survival-metrics">
                        <div class="metric">
                            <label>5-Year Survival</label>
                            <value>${analysis.survival_analysis.5_year_survival}%</value>
                            <span class="confidence-interval">
                                (${analysis.survival_analysis.confidence_interval.lower}% - 
                                ${analysis.survival_analysis.confidence_interval.upper}%)
                            </span>
                        </div>
                        <div class="metric">
                            <label>10-Year Survival</label>
                            <value>${analysis.survival_analysis.10_year_survival}%</value>
                        </div>
                        <div class="metric">
                            <label>Disease-Free Survival</label>
                            <value>${analysis.survival_analysis.disease_free_survival}%</value>
                        </div>
                    </div>
                </div>
                
                <div class="molecular-profile card">
                    <h3>Molecular Profile</h3>
                    <div class="subtype-distribution">
                        ${Object.entries(analysis.molecular_profile.subtype_probabilities)
                            .map(([subtype, prob]) => `
                                <div class="subtype-bar">
                                    <label>${subtype.replace('_', ' ').toUpperCase()}</label>
                                    <div class="bar" style="width: ${prob * 100}%"></div>
                                    <span>${(prob * 100).toFixed(1)}%</span>
                                </div>
                            `).join('')}
                    </div>
                    <div class="genomic-markers">
                        ${Object.entries(analysis.molecular_profile.genomic_markers)
                            .map(([marker, value]) => `
                                <div class="marker">
                                    <label>${marker.replace('_', ' ').toUpperCase()}</label>
                                    <value>${value}</value>
                                </div>
                            `).join('')}
                    </div>
                </div>
                
                <div class="treatment-recommendations card">
                    <h3>Treatment Recommendations</h3>
                    <div class="surgery-recommendation">
                        <h4>Surgery</h4>
                        <div class="recommendation">
                            <strong>${analysis.treatment_recommendations.surgery.recommendation}</strong>
                            <div class="confidence">${analysis.treatment_recommendations.surgery.confidence} Confidence</div>
                            <ul>
                                ${analysis.treatment_recommendations.surgery.rationale
                                    .map(reason => `<li>${reason}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                    
                    <div class="systemic-therapy">
                        <h4>Systemic Therapy</h4>
                        ${Object.entries(analysis.treatment_recommendations.systemic_therapy)
                            .map(([therapy, details]) => `
                                <div class="therapy-recommendation ${details.recommended ? 'recommended' : ''}">
                                    <h5>${therapy.replace('_', ' ').toUpperCase()}</h5>
                                    ${details.recommended ? `
                                        <div class="details">
                                            <div>Regimen: ${details.regimen}</div>
                                            <div>Duration: ${details.duration}</div>
                                            <div>Expected Benefit: ${details.expected_benefit}</div>
                                        </div>
                                    ` : '<div class="not-recommended">Not Recommended</div>'}
                                </div>
                            `).join('')}
                    </div>
                </div>
                
                <div class="follow-up-plan card">
                    <h3>Follow-up Plan</h3>
                    <div class="schedule">
                        ${analysis.follow_up_plan.schedule
                            .map(period => `
                                <div class="period">
                                    <strong>${period.timing}</strong>
                                    <span>${period.duration}</span>
                                </div>
                            `).join('')}
                    </div>
                    <div class="recommended-tests">
                        <h4>Recommended Tests</h4>
                        <ul>
                            ${analysis.follow_up_plan.recommended_tests
                                .map(test => `<li>${test}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                
                <div class="quality-of-life card">
                    <h3>Quality of Life Considerations</h3>
                    <div class="side-effects">
                        <div class="short-term">
                            <h4>Short-term Effects</h4>
                            <ul>
                                ${analysis.quality_of_life.expected_side_effects.short_term
                                    .map(effect => `<li>${effect}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="long-term">
                            <h4>Long-term Effects</h4>
                            <ul>
                                ${analysis.quality_of_life.expected_side_effects.long_term
                                    .map(effect => `<li>${effect}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                    <div class="supportive-care">
                        <h4>Supportive Care</h4>
                        <ul>
                            ${analysis.quality_of_life.supportive_care
                                .map(care => `<li>${care}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        `;
        
        resultsContainer.innerHTML = resultsHTML;
        
        // Load validation results
        loadValidationResults();
        
    } catch (error) {
        console.error('Error analyzing patient data:', error);
        resultsContainer.innerHTML = `
            <div class="error-message">
                Error analyzing patient data. Please try again.
            </div>
        `;
    }
}

async function loadValidationResults() {
    const validationContainer = document.getElementById('validationResults');
    if (!validationContainer) return;
    
    try {
        const response = await fetch('/api/validation/results');
        const results = await response.json();
        
        const validationHTML = Object.entries(results)
            .map(([filename, data]) => `
                <div class="validation-card">
                    <img src="${data.path}" alt="${data.info.title}">
                    <div class="validation-info">
                        <h4>${data.info.title}</h4>
                        <p>${data.info.description}</p>
                        <div class="metrics">
                            ${Object.entries(data.info.metrics)
                                .map(([metric, value]) => `
                                    <div class="metric">
                                        <label>${metric.replace(/_/g, ' ').toUpperCase()}</label>
                                        <value>${typeof value === 'number' ? value.toFixed(3) : value}</value>
                                    </div>
                                `).join('')}
                        </div>
                    </div>
                </div>
            `).join('');
        
        validationContainer.innerHTML = validationHTML;
        
    } catch (error) {
        console.error('Error loading validation results:', error);
        validationContainer.innerHTML = `
            <div class="error-message">
                Error loading validation results. Please try again.
            </div>
        `;
    }
} 