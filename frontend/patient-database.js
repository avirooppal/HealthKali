/**
 * Patient Database using IndexedDB
 * Handles storing and retrieving patient data
 */
class PatientDatabase {
    constructor() {
        this.dbName = 'CancerDigitalTwinDB';
        this.dbVersion = 1;
        this.dbReady = false;
        this.db = null;
        this.initDB();
    }
    
    // Initialize the database
    async initDB() {
        return new Promise((resolve, reject) => {
            if (!window.indexedDB) {
                console.error("Your browser doesn't support IndexedDB");
                reject("IndexedDB not supported");
                return;
            }
            
            const request = window.indexedDB.open(this.dbName, this.dbVersion);
            
            request.onerror = (event) => {
                console.error("Database error:", event.target.error);
                reject("Could not open database");
            };
            
            request.onsuccess = (event) => {
                this.db = event.target.result;
                this.dbReady = true;
                console.log("Database opened successfully");
                resolve(this.db);
            };
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                // Create patients object store
                if (!db.objectStoreNames.contains('patients')) {
                    const store = db.createObjectStore('patients', { keyPath: 'patientID' });
                    
                    // Create indexes for common queries
                    store.createIndex('by_risk_score', 'riskScore', { unique: false });
                    store.createIndex('by_date_added', 'dateAdded', { unique: false });
                    
                    console.log("Database schema created");
                }
            };
        });
    }
    
    // Add a new patient
    async addPatient(patientData) {
        // Ensure database is ready
        if (!this.dbReady) {
            await this.initDB();
        }
        
        return new Promise((resolve, reject) => {
            // Add metadata
            patientData.dateAdded = new Date().toISOString();
            patientData.lastUpdated = new Date().toISOString();
            
            // Calculate risk score if not provided
            if (!patientData.riskScore) {
                patientData.riskScore = this.calculateRiskScore(patientData);
            }
            
            // Start transaction
            const transaction = this.db.transaction(['patients'], 'readwrite');
            const store = transaction.objectStore('patients');
            
            const request = store.add(patientData);
            
            request.onsuccess = () => {
                console.log("Patient added successfully");
                resolve(patientData);
            };
            
            request.onerror = (event) => {
                console.error("Error adding patient:", event.target.error);
                reject("Failed to add patient");
            };
        });
    }
    
    // Get a patient by ID
    async getPatient(patientID) {
        // Ensure database is ready
        if (!this.dbReady) {
            await this.initDB();
        }
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['patients'], 'readonly');
            const store = transaction.objectStore('patients');
            
            const request = store.get(patientID);
            
            request.onsuccess = (event) => {
                if (event.target.result) {
                    resolve(event.target.result);
                } else {
                    reject("Patient not found");
                }
            };
            
            request.onerror = (event) => {
                console.error("Error getting patient:", event.target.error);
                reject("Failed to get patient");
            };
        });
    }
    
    // Get all patients
    async getAllPatients() {
        // Ensure database is ready
        if (!this.dbReady) {
            await this.initDB();
        }
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['patients'], 'readonly');
            const store = transaction.objectStore('patients');
            
            const request = store.getAll();
            
            request.onsuccess = (event) => {
                resolve(event.target.result);
            };
            
            request.onerror = (event) => {
                console.error("Error getting patients:", event.target.error);
                reject("Failed to get patients");
            };
        });
    }
    
    // Get recent patients (limited number, sorted by date)
    async getRecentPatients(limit = 5) {
        // Ensure database is ready
        if (!this.dbReady) {
            await this.initDB();
        }
        
        const patients = await this.getAllPatients();
        
        // Sort by date added (newest first)
        patients.sort((a, b) => {
            return new Date(b.dateAdded) - new Date(a.dateAdded);
        });
        
        // Limit the number of results
        return patients.slice(0, limit);
    }
    
    // Update an existing patient
    async updatePatient(patientData) {
        // Ensure database is ready
        if (!this.dbReady) {
            await this.initDB();
        }
        
        return new Promise((resolve, reject) => {
            // Update metadata
            patientData.lastUpdated = new Date().toISOString();
            
            // Recalculate risk score if needed
            if (!patientData.riskScore) {
                patientData.riskScore = this.calculateRiskScore(patientData);
            }
            
            const transaction = this.db.transaction(['patients'], 'readwrite');
            const store = transaction.objectStore('patients');
            
            const request = store.put(patientData);
            
            request.onsuccess = () => {
                console.log("Patient updated successfully");
                resolve(patientData);
            };
            
            request.onerror = (event) => {
                console.error("Error updating patient:", event.target.error);
                reject("Failed to update patient");
            };
        });
    }
    
    // Delete a patient
    async deletePatient(patientID) {
        // Ensure database is ready
        if (!this.dbReady) {
            await this.initDB();
        }
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['patients'], 'readwrite');
            const store = transaction.objectStore('patients');
            
            const request = store.delete(patientID);
            
            request.onsuccess = () => {
                console.log("Patient deleted successfully");
                resolve(true);
            };
            
            request.onerror = (event) => {
                console.error("Error deleting patient:", event.target.error);
                reject("Failed to delete patient");
            };
        });
    }
    
    // Calculate risk score based on patient data
    calculateRiskScore(patientData) {
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
        
        return riskScore;
    }
    
    // Get risk category counts
    async getRiskCategoryCounts() {
        const patients = await this.getAllPatients();
        
        const counts = {
            high: 0,
            medium: 0,
            low: 0
        };
        
        patients.forEach(patient => {
            if (patient.riskScore > 0.6) {
                counts.high++;
            } else if (patient.riskScore > 0.3) {
                counts.medium++;
            } else {
                counts.low++;
            }
        });
        
        return counts;
    }
} 