/**
 * Cancer Digital Twin API Client
 * Handles all communications with the backend API
 */

class DigitalTwinAPI {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
        this.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
    }

    /**
     * Helper method to make API requests
     */
    async fetchAPI(endpoint, method = 'GET', data = null) {
        const url = `${this.baseURL}${endpoint}`;
        const options = {
            method,
            headers: this.headers,
            credentials: 'include',
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            
            // Handle API errors
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({
                    detail: `API Error: ${response.status} ${response.statusText}`
                }));
                throw new Error(errorData.detail || 'Unknown API error');
            }
            
            // Parse JSON response
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // ===== Patient Digital Twin Methods =====
    
    /**
     * Create a digital twin for a patient
     */
    async createDigitalTwin(patientData) {
        return this.fetchAPI('/digital_twin/create', 'POST', patientData);
    }

    /**
     * Get a digital twin by ID
     */
    async getDigitalTwin(twinId) {
        return this.fetchAPI(`/digital_twin/${twinId}`);
    }

    // ===== Risk Assessment Methods =====

    /**
     * Calculate baseline risk for a patient
     */
    async calculateRisk(patientData) {
        return this.fetchAPI('/risk/baseline', 'POST', patientData);
    }

    /**
     * Calculate advanced risk with genomic features
     */
    async calculateAdvancedRisk(patientData) {
        return this.fetchAPI('/risk/advanced', 'POST', patientData);
    }

    // ===== Treatment Methods =====

    /**
     * Simulate treatment response
     */
    async simulateTreatment(patientData, treatmentPlan) {
        return this.fetchAPI('/treatment/simulate', 'POST', {
            patient: patientData,
            treatment: treatmentPlan
        });
    }

    /**
     * Get treatment recommendations
     */
    async getTreatmentRecommendations(patientData) {
        return this.fetchAPI('/treatment/recommendations', 'POST', patientData);
    }

    // ===== Disease Progression Methods =====

    /**
     * Project disease progression
     */
    async projectProgression(patientData, treatmentPlan, months = 60) {
        return this.fetchAPI('/progression/project', 'POST', {
            patient: patientData,
            treatment: treatmentPlan,
            months: months
        });
    }

    /**
     * Predict survival curve
     */
    async predictSurvival(patientData, treatmentPlan, years = 5) {
        return this.fetchAPI('/progression/survival', 'POST', {
            patient: patientData,
            treatment: treatmentPlan,
            years: years
        });
    }

    // ===== Validation Methods =====

    /**
     * Get validation statistics
     */
    async getValidationStats(dataset = 'metabric') {
        return this.fetchAPI(`/validation/stats?dataset=${dataset}`);
    }

    /**
     * Get validation comparison data
     */
    async getValidationComparison() {
        return this.fetchAPI('/validation/comparison');
    }
}

// Create and export a singleton instance
const digitalTwinAPI = new DigitalTwinAPI();
export default digitalTwinAPI;