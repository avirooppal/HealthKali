/**
 * Enhanced Results Handler
 * Creates detailed prediction and simulation displays
 */
class EnhancedResults {
    constructor() {
        // Initialize references to DOM elements
        this.resultsContainer = document.getElementById('patientResults');
        this.demoResultsContainer = document.getElementById('demoResults');
    }
    
    // Show detailed results for a patient
    showDetailedResults(patientData, container = null) {
        // Use specified container or default
        const targetContainer = container || this.resultsContainer;
        
        // If no container is available, return
        if (!targetContainer) return;
        
        // Show the container and create loading indicator
        targetContainer.style.display = 'block';
        targetContainer.innerHTML = `
            <div class="text-center my-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="sr-only">Loading...</span>
                </div>
                <p class="mt-2">Analyzing patient data and generating digital twin...</p>
            </div>
        `;
        
        // Simulate processing delay
        setTimeout(() => {
            // Create the detailed analysis content
            this.generateDetailedAnalysis(patientData, targetContainer);
            
            // Scroll to the results
            targetContainer.scrollIntoView({ behavior: 'smooth' });
        }, 1500);
    }
    
    // Generate detailed analysis HTML
    generateDetailedAnalysis(patientData, container) {
        // Calculate risk metrics
        const riskMetrics = this.calculateRiskMetrics(patientData);
        
        // Create HTML for the analysis
        const html = `
            <div class="card mb-4">
                <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">Digital Twin Analysis Results</h5>
                    <div>
                        <button class="btn btn-sm btn-outline-light mr-2" id="printResultsBtn">
                            <i class="fas fa-print"></i> Print
                        </button>
                        <button class="btn btn-sm btn-light" id="exportResultsBtn">
                            <i class="fas fa-file-export"></i> Export
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <!-- Patient Summary -->
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6 class="mb-0">Patient Information</h6>
                                </div>
                                <div class="card-body">
                                    <table class="table table-sm">
                                        <tr>
                                            <th>Patient ID:</th>
                                            <td>${patientData.patientID}</td>
                                        </tr>
                                        <tr>
                                            <th>Age:</th>
                                            <td>${patientData.age}</td>
                                        </tr>
                                        <tr>
                                            <th>Tumor Size:</th>
                                            <td>${patientData.tumor_size} mm</td>
                                        </tr>
                                        <tr>
                                            <th>Tumor Grade:</th>
                                            <td>Grade ${patientData.grade}</td>
                                        </tr>
                                        <tr>
                                            <th>Positive Nodes:</th>
                                            <td>${patientData.nodes_positive}</td>
                                        </tr>
                                        <tr>
                                            <th>ER Status:</th>
                                            <td>${patientData.er_status}</td>
                                        </tr>
                                        <tr>
                                            <th>HER2 Status:</th>
                                            <td>${patientData.her2_status}</td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6 class="mb-0">Risk Assessment</h6>
                                </div>
                                <div class="card-body">
                                    <div class="text-center mb-3">
                                        <div class="risk-gauge">
                                            <div class="risk-score">${riskMetrics.riskScore.toFixed(2)}</div>
                                            <div class="risk-category ${riskMetrics.riskCategory.toLowerCase()}">${riskMetrics.riskCategory} Risk</div>
                                        </div>
                                    </div>
                                    <p class="risk-summary">
                                        This patient has a ${riskMetrics.riskCategory.toLowerCase()} risk profile based on tumor characteristics 
                                        and biomarkers. The composite risk score is ${riskMetrics.riskScore.toFixed(2)} on a scale of 0-1.
                                    </p>
                                    <div class="risk-factors mt-3">
                                        <h6>Key Risk Factors:</h6>
                                        <ul>
                                            ${this.generateRiskFactorsList(patientData, riskMetrics)}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Survival Metrics -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h6 class="mb-0">Survival & Recurrence Projections</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-3">
                                    <div class="metric-card text-center">
                                        <h2>${riskMetrics.survival5yr.toFixed(1)}%</h2>
                                        <p>5-Year Survival</p>
                                        <small class="text-muted">CI: ${riskMetrics.survival5yrLower.toFixed(1)}-${riskMetrics.survival5yrUpper.toFixed(1)}%</small>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="metric-card text-center">
                                        <h2>${riskMetrics.survival10yr.toFixed(1)}%</h2>
                                        <p>10-Year Survival</p>
                                        <small class="text-muted">CI: ${riskMetrics.survival10yrLower.toFixed(1)}-${riskMetrics.survival10yrUpper.toFixed(1)}%</small>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="metric-card text-center">
                                        <h2>${riskMetrics.recurrenceRisk.toFixed(1)}%</h2>
                                        <p>Recurrence Risk</p>
                                        <small class="text-muted">CI: ${riskMetrics.recurrenceRiskLower.toFixed(1)}-${riskMetrics.recurrenceRiskUpper.toFixed(1)}%</small>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="metric-card text-center">
                                        <h2>${riskMetrics.diseaseFree5yr.toFixed(1)}%</h2>
                                        <p>5-Year DFS</p>
                                        <small class="text-muted">CI: ${riskMetrics.diseaseFree5yrLower.toFixed(1)}-${riskMetrics.diseaseFree5yrUpper.toFixed(1)}%</small>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="row mt-4">
                                <div class="col-md-8">
                                    <canvas id="survivalCurveChart" height="250"></canvas>
                                </div>
                                <div class="col-md-4">
                                    <div class="survival-summary">
                                        <h6>Summary Analysis</h6>
                                        <p>
                                            Based on molecular and clinical features, this patient has a 
                                            ${riskMetrics.survival5yr.toFixed(1)}% probability of 5-year overall survival.
                                        </p>
                                        <p>
                                            The risk of recurrence within 5 years is ${riskMetrics.recurrenceRisk.toFixed(1)}%,
                                            with local recurrence being more likely than distant metastasis given the 
                                            ${patientData.nodes_positive > 0 ? 'presence' : 'absence'} of positive lymph nodes.
                                        </p>
                                        <p>
                                            Key prognostic factors include tumor grade (${patientData.grade}), 
                                            ${patientData.er_status} ER status, and ${patientData.her2_status} HER2 status.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Disease Progression -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h6 class="mb-0">Disease Progression Simulation</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-8">
                                    <canvas id="progressionChart" height="300"></canvas>
                                </div>
                                <div class="col-md-4">
                                    <div class="simulation-stats">
                                        <table class="table table-sm">
                                            <tr>
                                                <th>Initial Tumor Size:</th>
                                                <td>${(parseFloat(patientData.tumor_size) / 10).toFixed(1)} cm</td>
                                            </tr>
                                            <tr>
                                                <th>Estimated Doubling Time:</th>
                                                <td>${this.calculateDoublingTime(patientData)} days</td>
                                            </tr>
                                            <tr>
                                                <th>Growth Rate:</th>
                                                <td>${this.calculateGrowthRate(patientData)} mm/month</td>
                                            </tr>
                                            <tr>
                                                <th>Likely Metastasis Sites:</th>
                                                <td>${this.predictMetastasisSites(patientData).join(', ')}</td>
                                            </tr>
                                        </table>
                                        
                                        <h6 class="mt-3">Disease Course Summary</h6>
                                        <p>
                                            Without intervention, the simulation predicts ${riskMetrics.recurrenceRisk > 50 ? 'high' : 'moderate'} 
                                            probability of progression. The tumor growth model accounts for the ${patientData.grade == 3 ? 'high' : patientData.grade == 2 ? 'moderate' : 'low'} 
                                            proliferation rate associated with grade ${patientData.grade} tumors and 
                                            ${patientData.er_status} ER status.
                                        </p>
                                        <p>
                                            Natural history projection shows a ${riskMetrics.naturalHistorySurvival.toFixed(0)}% 
                                            5-year survival without treatment.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Treatment Recommendations -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h6 class="mb-0">Treatment Recommendations</h6>
                        </div>
                        <div class="card-body">
                            <div id="treatmentRecommendations">
                                ${this.generateTreatmentRecommendations(patientData)}
                            </div>
                            
                            <div class="mt-4">
                                <canvas id="treatmentImpactChart" height="250"></canvas>
                            </div>
                            
                            <div class="mt-3 treatment-explanation">
                                <h6>Predicted Treatment Benefits</h6>
                                <p>
                                    The recommended treatment plan is projected to improve 5-year survival from 
                                    ${riskMetrics.naturalHistorySurvival.toFixed(0)}% to ${riskMetrics.survival5yr.toFixed(1)}%, 
                                    representing an absolute benefit of ${(riskMetrics.survival5yr - riskMetrics.naturalHistorySurvival).toFixed(1)}%.
                                </p>
                                <p>
                                    Each treatment modality contributes to risk reduction:
                                </p>
                                <ul>
                                    ${this.generateTreatmentBenefitsList(patientData)}
                                </ul>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Quality of Life and Long-term Follow-up -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h6 class="mb-0">Quality of Life & Follow-up</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Expected Side Effects</h6>
                                    <div class="side-effects">
                                        <h6>Short-term Effects</h6>
                                        <ul>
                                            ${this.generateSideEffectsList(patientData, 'short')}
                                        </ul>
                                        
                                        <h6>Long-term Effects</h6>
                                        <ul>
                                            ${this.generateSideEffectsList(patientData, 'long')}
                                        </ul>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <h6>Recommended Follow-up Schedule</h6>
                                    <table class="table table-sm">
                                        <thead>
                                            <tr>
                                                <th>Timeframe</th>
                                                <th>Recommended Tests</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>Years 1-2</td>
                                                <td>Physical exam every 3-6 months, Annual mammogram</td>
                                            </tr>
                                            <tr>
                                                <td>Years 3-5</td>
                                                <td>Physical exam every 6 months, Annual mammogram</td>
                                            </tr>
                                            <tr>
                                                <td>After 5 years</td>
                                                <td>Annual physical exam and mammogram</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                    
                                    <h6 class="mt-3">Quality of Life Projections</h6>
                                    <canvas id="qualityOfLifeChart" height="180"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Update the container with the analysis HTML
        container.innerHTML = html;
        
        // Initialize the charts
        this.initializeCharts(patientData, riskMetrics);
        
        // Add event listeners for export and print buttons
        this.addExportPrintListeners();
    }
    
    // Calculate risk metrics based on patient data
    calculateRiskMetrics(patientData) {
        // Basic risk calculation
        const tumorSize = parseFloat(patientData.tumor_size);
        const grade = parseInt(patientData.grade);
        const nodesPositive = parseInt(patientData.nodes_positive);
        const erStatus = patientData.er_status;
        const her2Status = patientData.her2_status;
        
        let riskScore = (tumorSize * 0.004 + grade * 0.05 + nodesPositive * 0.03);
        
        // Adjust for receptor status
        if (erStatus === 'negative') riskScore += 0.1;
        if (her2Status === 'positive') riskScore += 0.05;
        
        // Cap between 0.1 and 0.9
        riskScore = Math.max(0.1, Math.min(0.9, riskScore));
        
        // Determine risk category
        let riskCategory = 'Low';
        if (riskScore > 0.6) {
            riskCategory = 'High';
        } else if (riskScore > 0.3) {
            riskCategory = 'Intermediate';
        }
        
        // Calculate survival metrics
        const survival5yr = (1 - riskScore) * 100;
        const survival5yrLower = Math.max(0, survival5yr - 5);
        const survival5yrUpper = Math.min(100, survival5yr + 5);
        
        const survival10yr = (1 - riskScore * 1.2) * 100;
        const survival10yrLower = Math.max(0, survival10yr - 7);
        const survival10yrUpper = Math.min(100, survival10yr + 7);
        
        const recurrenceRisk = riskScore * 100;
        const recurrenceRiskLower = Math.max(0, recurrenceRisk - 4);
        const recurrenceRiskUpper = Math.min(100, recurrenceRisk + 4);
        
        const diseaseFree5yr = (1 - riskScore * 0.9) * 100;
        const diseaseFree5yrLower = Math.max(0, diseaseFree5yr - 6);
        const diseaseFree5yrUpper = Math.min(100, diseaseFree5yr + 6);
        
        // Natural history (no treatment) survival
        const naturalHistorySurvival = (1 - riskScore * 2) * 100;
        
        return {
            riskScore,
            riskCategory,
            survival5yr,
            survival5yrLower,
            survival5yrUpper,
            survival10yr,
            survival10yrLower,
            survival10yrUpper,
            recurrenceRisk,
            recurrenceRiskLower,
            recurrenceRiskUpper,
            diseaseFree5yr,
            diseaseFree5yrLower,
            diseaseFree5yrUpper,
            naturalHistorySurvival
        };
    }
    
    // Generate list of risk factors
    generateRiskFactorsList(patientData, riskMetrics) {
        const factors = [];
        
        // Add factors based on patient data
        if (parseInt(patientData.grade) >= 3) {
            factors.push('High tumor grade (Grade ' + patientData.grade + ') indicates aggressive disease');
        }
        
        if (parseFloat(patientData.tumor_size) > 20) {
            factors.push('Tumor size (' + patientData.tumor_size + 'mm) exceeds 2cm threshold');
        }
        
        if (parseInt(patientData.nodes_positive) > 0) {
            factors.push('Presence of ' + patientData.nodes_positive + ' positive lymph nodes indicates spread');
        }
        
        if (patientData.er_status === 'negative') {
            factors.push('ER-negative status limits hormonal therapy options');
        }
        
        if (patientData.her2_status === 'positive') {
            factors.push('HER2-positive status indicates potential for targeted therapy');
        }
        
        // Add general age-related factor
        const age = parseInt(patientData.age);
        if (age < 40) {
            factors.push('Young age (<40) associated with more aggressive disease');
        } else if (age > 70) {
            factors.push('Advanced age (>70) may affect treatment tolerance');
        }
        
        // Return as HTML list items
        return factors.map(factor => `<li>${factor}</li>`).join('');
    }
    
    // Calculate tumor doubling time
    calculateDoublingTime(patientData) {
        // Base doubling time by grade
        let baseDoublingTime = 150; // days
        const grade = parseInt(patientData.grade);
        
        if (grade === 2) {
            baseDoublingTime = 120;
        } else if (grade === 3) {
            baseDoublingTime = 90;
        }
        
        // Adjust for ER/HER2 status
        if (patientData.er_status === 'negative') {
            baseDoublingTime *= 0.8; // Faster growth
        }
        
        if (patientData.her2_status === 'positive') {
            baseDoublingTime *= 0.7; // Faster growth
        }
        
        return Math.round(baseDoublingTime);
    }
    
    // Calculate tumor growth rate (mm/month)
    calculateGrowthRate(patientData) {
        const doublingTime = this.calculateDoublingTime(patientData);
        const tumorSize = parseFloat(patientData.tumor_size);
        
        // Estimate monthly growth rate
        const growthRate = (tumorSize * 0.693 * 30) / doublingTime;
        
        return growthRate.toFixed(2);
    }
    
    // Predict likely metastasis sites
    predictMetastasisSites(patientData) {
        const sites = ['Bone', 'Liver', 'Lung', 'Brain'];
        
        // For HER2+ disease, brain metastases are more common
        if (patientData.her2_status === 'positive') {
            return ['Bone', 'Brain', 'Liver', 'Lung'];
        }
        
        return sites;
    }
    
    // Generate treatment recommendations
    generateTreatmentRecommendations(patientData) {
        let surgeryRec, radiationRec, chemoRec, hormonalRec, targetedRec;
        
        // Surgery recommendations
        const tumorSize = parseFloat(patientData.tumor_size);
        if (tumorSize <= 20) {
            surgeryRec = 'Breast Conserving Surgery (Lumpectomy)';
        } else {
            surgeryRec = 'Mastectomy with consideration for reconstruction';
        }
        
        // Radiation therapy
        if (tumorSize <= 20) {
            radiationRec = 'Whole breast radiation following lumpectomy';
        } else {
            radiationRec = 'Post-mastectomy radiation if high risk features present';
        }
        
        // Chemotherapy
        const grade = parseInt(patientData.grade);
        const nodesPositive = parseInt(patientData.nodes_positive);
        
        if (grade >= 3 || nodesPositive > 0 || tumorSize > 20 || patientData.er_status === 'negative') {
            chemoRec = 'Adjuvant chemotherapy recommended';
        } else {
            chemoRec = 'Chemotherapy may be omitted (consider genomic testing)';
        }
        
        // Hormonal therapy
        if (patientData.er_status === 'positive') {
            const age = parseInt(patientData.age);
            if (patientData.menopausal_status === 'pre') {
                hormonalRec = 'Tamoxifen for 5-10 years';
            } else {
                hormonalRec = 'Aromatase inhibitor for 5-10 years';
            }
        } else {
            hormonalRec = 'No hormonal therapy indicated (ER-negative)';
        }
        
        // Targeted therapy
        if (patientData.her2_status === 'positive') {
            targetedRec = 'Trastuzumab (Herceptin) for 1 year';
        } else {
            targetedRec = 'No HER2-targeted therapy indicated';
        }
        
        // Format recommendations as HTML
        return `
            <div class="treatment-plan">
                <div class="row">
                    <div class="col-md-4">
                        <div class="treatment-category">
                            <h6><i class="fas fa-procedures"></i> Surgery</h6>
                            <p>${surgeryRec}</p>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="treatment-category">
                            <h6><i class="fas fa-radiation"></i> Radiation</h6>
                            <p>${radiationRec}</p>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="treatment-category">
                            <h6><i class="fas fa-syringe"></i> Chemotherapy</h6>
                            <p>${chemoRec}</p>
                        </div>
                    </div>
                </div>
                <div class="row mt-3">
                    <div class="col-md-6">
                        <div class="treatment-category">
                            <h6><i class="fas fa-pills"></i> Hormonal Therapy</h6>
                            <p>${hormonalRec}</p>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="treatment-category">
                            <h6><i class="fas fa-dna"></i> Targeted Therapy</h6>
                            <p>${targetedRec}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Generate treatment benefits list
    generateTreatmentBenefitsList(patientData) {
        const benefits = [];
        
        // Surgery benefit
        benefits.push('Surgery: Local control with 80-90% reduction in recurrence risk');
        
        // Radiation benefit
        if (parseFloat(patientData.tumor_size) <= 20) {
            benefits.push('Radiation: 50-60% reduction in local recurrence after lumpectomy');
        } else {
            benefits.push('Radiation: 30-40% reduction in locoregional recurrence after mastectomy');
        }
        
        // Chemotherapy benefit
        const grade = parseInt(patientData.grade);
        const nodesPositive = parseInt(patientData.nodes_positive);
        
        if (grade >= 3 || nodesPositive > 0 || patientData.er_status === 'negative') {
            benefits.push('Chemotherapy: 30-35% reduction in recurrence risk and 20-25% reduction in mortality');
        } else {
            benefits.push('Chemotherapy: 15-20% reduction in recurrence risk');
        }
        
        // Hormonal therapy benefit
        if (patientData.er_status === 'positive') {
            benefits.push('Hormonal therapy: 40-50% reduction in recurrence risk over 5-10 years');
        }
        
        // Targeted therapy benefit
        if (patientData.her2_status === 'positive') {
            benefits.push('HER2-targeted therapy: 40-50% reduction in recurrence risk');
        }
        
        // Return as HTML list items
        return benefits.map(benefit => `<li>${benefit}</li>`).join('');
    }
    
    // Generate side effects list
    generateSideEffectsList(patientData, timeframe) {
        const effects = [];
        
        if (timeframe === 'short') {
            // Short-term effects
            effects.push('Surgery: Pain, swelling, limited mobility, infection risk');
            
            if (parseFloat(patientData.tumor_size) <= 20) {
                effects.push('Radiation: Skin irritation, fatigue, breast swelling');
            } else {
                effects.push('Radiation: Skin irritation, fatigue, chest wall discomfort');
            }
            
            const grade = parseInt(patientData.grade);
            const nodesPositive = parseInt(patientData.nodes_positive);
            
            if (grade >= 3 || nodesPositive > 0 || patientData.er_status === 'negative') {
                effects.push('Chemotherapy: Nausea, hair loss, fatigue, risk of infection');
            }
            
            if (patientData.er_status === 'positive') {
                if (patientData.menopausal_status === 'pre') {
                    effects.push('Tamoxifen: Hot flashes, mood changes, menstrual irregularities');
                } else {
                    effects.push('Aromatase inhibitors: Joint pain, bone pain, hot flashes');
                }
            }
            
            if (patientData.her2_status === 'positive') {
                effects.push('Trastuzumab: Cardiac monitoring required, potential for heart function changes');
            }
        } else {
            // Long-term effects
            if (parseFloat(patientData.tumor_size) > 20) {
                effects.push('Mastectomy: Body image concerns, potential for chronic pain');
            } else {
                effects.push('Lumpectomy: Breast asymmetry, localized numbness');
            }
            
            effects.push('Radiation: Breast firmness, skin changes, rare risk of secondary malignancies');
            
            const grade = parseInt(patientData.grade);
            const nodesPositive = parseInt(patientData.nodes_positive);
            
            if (grade >= 3 || nodesPositive > 0 || patientData.er_status === 'negative') {
                effects.push('Chemotherapy: Early menopause, cognitive changes, rare heart/nerve damage');
            }
            
            if (patientData.er_status === 'positive') {
                if (patientData.menopausal_status === 'pre') {
                    effects.push('Tamoxifen: Small increased risk of endometrial cancer, thromboembolic events');
                } else {
                    effects.push('Aromatase inhibitors: Accelerated bone loss, increased fracture risk');
                }
            }
            
            if (patientData.her2_status === 'positive') {
                effects.push('Trastuzumab: Potential for long-term cardiac effects (generally reversible)');
            }
        }
        
        // Return as HTML list items
        return effects.map(effect => `<li>${effect}</li>`).join('');
    }
    
    // Initialize charts for the results display
    initializeCharts(patientData, riskMetrics) {
        // Create survival curve chart
        this.createSurvivalCurveChart(patientData, riskMetrics);
        
        // Create disease progression chart
        this.createProgressionChart(patientData, riskMetrics);
        
        // Create treatment impact chart
        this.createTreatmentImpactChart(patientData, riskMetrics);
        
        // Create quality of life chart
        this.createQualityOfLifeChart(patientData, riskMetrics);
    }
    
    // Create survival curve chart
    createSurvivalCurveChart(patientData, riskMetrics) {
        const ctx = document.getElementById('survivalCurveChart').getContext('2d');
        
        // Generate survival curve data points
        const years = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
        const survivalWithTreatment = years.map(year => {
            if (year === 0) return 100;
            if (year <= 5) {
                return 100 - (year * (100 - riskMetrics.survival5yr) / 5);
            } else {
                const base5yr = riskMetrics.survival5yr;
                const decline = (base5yr - riskMetrics.survival10yr) * (year - 5) / 5;
                return base5yr - decline;
            }
        });
        
        const survivalNoTreatment = years.map(year => {
            if (year === 0) return 100;
            const baseSurvival = riskMetrics.naturalHistorySurvival;
            return Math.max(0, 100 - (year * (100 - baseSurvival) / 3));
        });
        
        // Create chart
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: years,
                datasets: [
                    {
                        label: 'With Treatment',
                        data: survivalWithTreatment,
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        borderWidth: 2,
                        fill: true
                    },
                    {
                        label: 'Without Treatment',
                        data: survivalNoTreatment,
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                title: {
                    display: true,
                    text: 'Survival Projections'
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Years'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Survival Probability (%)'
                        },
                        min: 0,
                        max: 100
                    }
                },
                tooltips: {
                    mode: 'index',
                    intersect: false
                },
                hover: {
                    mode: 'nearest',
                    intersect: true
                }
            }
        });
    }
    
    // Create disease progression chart
    createProgressionChart(patientData, riskMetrics) {
        const ctx = document.getElementById('progressionChart').getContext('2d');
        
        // Generate progression data
        const months = Array.from({length: 25}, (_, i) => i);
        const initialSize = parseFloat(patientData.tumor_size);
        const growthRate = parseFloat(this.calculateGrowthRate(patientData));
        
        // Calculate progression (with Gompertz growth model)
        const progression = months.map(month => {
            const maxSize = 100; // maximum size in mm
            const growthK = 0.1 + (0.05 * parseInt(patientData.grade)); // growth constant
            
            if (month === 0) return initialSize;
            
            // Gompertz growth model
            const size = maxSize * Math.exp(
                -Math.exp(1 - (growthK * month * (1 - Math.log(initialSize) / Math.log(maxSize))))
            );
            
            return Math.min(maxSize, size);
        });
        
        // Create chart
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [
                    {
                        label: 'Tumor Size (mm)',
                        data: progression,
                        borderColor: 'rgba(153, 102, 255, 1)',
                        backgroundColor: 'rgba(153, 102, 255, 0.1)',
                        borderWidth: 2,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                title: {
                    display: true,
                    text: 'Untreated Disease Progression'
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Months'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Tumor Size (mm)'
                        },
                        min: 0
                    }
                },
                tooltips: {
                    mode: 'index',
                    intersect: false
                },
                hover: {
                    mode: 'nearest',
                    intersect: true
                }
            }
        });
    }
    
    // Create treatment impact chart
    createTreatmentImpactChart(patientData, riskMetrics) {
        const ctx = document.getElementById('treatmentImpactChart').getContext('2d');
        
        // Calculate treatment impacts
        const noTreatment = 100 - riskMetrics.naturalHistorySurvival;
        const withSurgery = noTreatment * 0.3; // 70% reduction
        let withRadiation = withSurgery * 0.6; // Additional 40% reduction
        
        // Different impacts based on treatments needed
        let withChemo = withRadiation;
        if (parseInt(patientData.grade) >= 3 || parseInt(patientData.nodes_positive) > 0) {
            withChemo = withRadiation * 0.7; // 30% additional reduction
        }
        
        let withHormonal = withChemo;
        if (patientData.er_status === 'positive') {
            withHormonal = withChemo * 0.6; // 40% additional reduction
        }
        
        let withTargeted = withHormonal;
        if (patientData.her2_status === 'positive') {
            withTargeted = withHormonal * 0.5; // 50% additional reduction
        }
        
        // Treatment labels and corresponding recurrence risks
        const treatments = ['No Treatment', 'Surgery', 'Radiation', 'Chemotherapy', 'Hormonal', 'Targeted'];
        const recurrenceRisks = [
            noTreatment.toFixed(1),
            withSurgery.toFixed(1),
            withRadiation.toFixed(1),
            withChemo.toFixed(1),
            withHormonal.toFixed(1),
            withTargeted.toFixed(1)
        ];
        
        // Filter out unnecessary treatments
        const filteredTreatments = [];
        const filteredRisks = [];
        
        filteredTreatments.push(treatments[0], treatments[1], treatments[2]);
        filteredRisks.push(recurrenceRisks[0], recurrenceRisks[1], recurrenceRisks[2]);
        
        if (parseInt(patientData.grade) >= 3 || parseInt(patientData.nodes_positive) > 0) {
            filteredTreatments.push(treatments[3]);
            filteredRisks.push(recurrenceRisks[3]);
        }
        
        if (patientData.er_status === 'positive') {
            filteredTreatments.push(treatments[4]);
            filteredRisks.push(recurrenceRisks[4]);
        }
        
        if (patientData.her2_status === 'positive') {
            filteredTreatments.push(treatments[5]);
            filteredRisks.push(recurrenceRisks[5]);
        }
        
        // Create chart
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: filteredTreatments,
                datasets: [
                    {
                        label: 'Recurrence Risk (%)',
                        data: filteredRisks,
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.7)',
                            'rgba(255, 159, 64, 0.7)',
                            'rgba(255, 205, 86, 0.7)',
                            'rgba(75, 192, 192, 0.7)',
                            'rgba(54, 162, 235, 0.7)',
                            'rgba(153, 102, 255, 0.7)'
                        ],
                        borderColor: [
                            'rgb(255, 99, 132)',
                            'rgb(255, 159, 64)',
                            'rgb(255, 205, 86)',
                            'rgb(75, 192, 192)',
                            'rgb(54, 162, 235)',
                            'rgb(153, 102, 255)'
                        ],
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                title: {
                    display: true,
                    text: 'Treatment Impact on Recurrence Risk'
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Recurrence Risk (%)'
                        }
                    }
                }
            }
        });
    }
    
    // Create quality of life chart
    createQualityOfLifeChart(patientData, riskMetrics) {
        const ctx = document.getElementById('qualityOfLifeChart').getContext('2d');
        
        // Generate QoL data points
        const timepoints = ['Diagnosis', '3 months', '6 months', '1 year', '2 years', '5 years'];
        
        // Base QoL score (0-100)
        let qolBaseline = 70;
        
        // Adjust based on treatments
        const qolScores = [
            qolBaseline, // Diagnosis
            qolBaseline - 20, // 3 months - Surgery, chemo, radiation
            qolBaseline - 15, // 6 months - Recovery in progress
            qolBaseline - 10, // 1 year - Early recovery
            qolBaseline - 5,  // 2 years - Later recovery
            qolBaseline      // 5 years - Return to baseline
        ];
        
        // Create chart
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: timepoints,
                datasets: [
                    {
                        label: 'Quality of Life Score',
                        data: qolScores,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        borderWidth: 2,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 40,
                        max: 100,
                        title: {
                            display: true,
                            text: 'QoL Score'
                        }
                    }
                }
            }
        });
    }
    
    // Add listeners for export and print functionality
    addExportPrintListeners() {
        const printBtn = document.getElementById('printResultsBtn');
        const exportBtn = document.getElementById('exportResultsBtn');
        
        if (printBtn) {
            printBtn.addEventListener('click', () => {
                window.print();
            });
        }
        
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                // Create a blob with the HTML content
                const content = document.getElementById('patientResults').innerHTML;
                const html = `
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Patient Report</title>
                        <style>
                            body { font-family: Arial, sans-serif; line-height: 1.6; }
                            .card { border: 1px solid #ccc; margin-bottom: 20px; border-radius: 5px; }
                            .card-header { background-color: #007bff; color: white; padding: 10px; }
                            .card-body { padding: 15px; }
                            h5, h6 { margin-top: 0; }
                            table { width: 100%; border-collapse: collapse; }
                            th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
                        </style>
                    </head>
                    <body>
                        ${content}
                    </body>
                    </html>
                `;
                
                const blob = new Blob([html], { type: 'text/html' });
                const url = URL.createObjectURL(blob);
                
                // Create download link
                const a = document.createElement('a');
                a.href = url;
                a.download = 'patient_report.html';
                document.body.appendChild(a);
                a.click();
                
                // Clean up
                setTimeout(() => {
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                }, 100);
            });
        }
    }
} 