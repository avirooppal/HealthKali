"""
Validation module for comparing Cancer Digital Twin predictions with real-world data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Any
from sklearn.metrics import roc_curve, auc, confusion_matrix
from lifelines import KaplanMeierFitter
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.utils.config import Config
from data.import_export.data_importer import DataImporter
from backend.core.progression.models import ProgressionSimulator
from backend.core.risk_models import calculate_baseline_risk
from backend.core.treatment import simulate_treatment_response, generate_treatment_recommendations

class DigitalTwinValidator:
    """Validation tool for Digital Twin predictions against real-world data."""
    
    def __init__(self, data_path: str = 'data'):
        """
        Initialize validator
        
        Args:
            data_path: Path to data folder
        """
        self.config = Config('config/default.yaml')
        self.data_importer = DataImporter(data_path)
        self.progression_simulator = ProgressionSimulator()
        
        # Load datasets
        self.metabric_data = None
        self.tcga_data = None
        
        # Results storage
        self.validation_results = {}
    
    def load_datasets(self) -> None:
        """Load and preprocess real-world datasets."""
        print("Loading datasets...")
        
        # Load METABRIC data
        try:
            self.metabric_data = self.data_importer.load_metabric_data()
            print(f"Loaded METABRIC data: {len(self.metabric_data)} patients")
        except Exception as e:
            print(f"Error loading METABRIC data: {str(e)}")
            self.metabric_data = pd.DataFrame()
        
        # Load TCGA data
        try:
            self.tcga_data = self.data_importer.load_tcga_data()
            print(f"Loaded TCGA data: {len(self.tcga_data)} patients")
        except Exception as e:
            print(f"Error loading TCGA data: {str(e)}")
            self.tcga_data = pd.DataFrame()
    
    def preprocess_metabric(self) -> pd.DataFrame:
        """
        Preprocess METABRIC data for validation
        
        Returns:
            Processed DataFrame ready for validation
        """
        if self.metabric_data is None or self.metabric_data.empty:
            print("METABRIC data not loaded. Call load_datasets() first.")
            return pd.DataFrame()
        
        # Make a copy to avoid modifying original
        data = self.metabric_data.copy()
        
        # Convert column names to standard format
        column_mapping = {
            'PATIENT_ID': 'patient_id',
            'AGE_AT_DIAGNOSIS': 'age',
            'TUMOR_SIZE': 'tumor_size',
            'GRADE': 'grade',
            'LYMPH_NODES_EXAMINED_POSITIVE': 'nodes_positive',
            'ER_STATUS': 'er_status',
            'PR_STATUS': 'pr_status',
            'HER2_STATUS': 'her2_status',
            'CLAUDIN_SUBTYPE': 'molecular_subtype',
            'OVERALL_SURVIVAL_MONTHS': 'overall_survival_months',
            'DEATH_FROM_CANCER': 'died_from_cancer'
        }
        
        # Apply mapping for columns that exist
        existing_columns = [col for col in column_mapping if col in data.columns]
        data = data.rename(columns={col: column_mapping[col] for col in existing_columns})
        
        # Convert statuses to lowercase
        for col in ['er_status', 'pr_status', 'her2_status']:
            if col in data.columns:
                data[col] = data[col].str.lower() if data[col].dtype == 'object' else data[col]
                # Convert binary indicators to positive/negative
                if data[col].dtype != 'object':
                    data[col] = data[col].map({1: 'positive', 0: 'negative'})
        
        # Map molecular subtypes if needed
        if 'molecular_subtype' in data.columns:
            subtype_mapping = {
                'LumA': 'Luminal A',
                'LumB': 'Luminal B HER2-',
                'Her2': 'HER2 Enriched',
                'Basal': 'Triple Negative',
                'claudin-low': 'Triple Negative',
                'Normal': 'Normal-like'
            }
            data['molecular_subtype'] = data['molecular_subtype'].map(subtype_mapping)
        
        # Add status columns if needed
        if 'nodes_positive' not in data.columns and 'nodes_examined_positive' in data.columns:
            data['nodes_positive'] = data['nodes_examined_positive']
        
        # Calculate outcomes at 5 years (60 months)
        if 'overall_survival_months' in data.columns:
            data['survived_5yr'] = (data['overall_survival_months'] > 60).astype(int)
            
            # Determine recurrence status if available
            if 'disease_free_months' in data.columns:
                data['recurrence_5yr'] = (
                    (data['disease_free_months'] <= 60) & 
                    (data['disease_free_status'] == 1)
                ).astype(int)
        
        # Filter for complete data
        required_cols = ['age', 'tumor_size', 'grade', 'nodes_positive', 
                        'er_status', 'pr_status', 'her2_status']
        
        # Keep only rows with all required data
        for col in required_cols:
            if col in data.columns:
                data = data[data[col].notna()]
        
        print(f"Preprocessed METABRIC data: {len(data)} patients with complete data")
        return data
    
    def preprocess_tcga(self) -> pd.DataFrame:
        """
        Preprocess TCGA data for validation
        
        Returns:
            Processed DataFrame ready for validation
        """
        if self.tcga_data is None or self.tcga_data.empty:
            print("TCGA data not loaded. Call load_datasets() first.")
            return pd.DataFrame()
        
        # Make a copy to avoid modifying original
        data = self.tcga_data.copy()
        
        # Standardize column names based on your TCGA file structure
        # You'll need to adjust this based on your actual column names
        column_mapping = {
            'patient_id': 'patient_id',
            'age_at_diagnosis': 'age',
            'tumor_size': 'tumor_size',
            'tumor_grade': 'grade',
            'lymph_nodes_positive': 'nodes_positive',
            'er_status': 'er_status',
            'pr_status': 'pr_status',
            'her2_status': 'her2_status',
            'subtype': 'molecular_subtype',
            'overall_survival_months': 'overall_survival_months',
            'vital_status': 'vital_status'
        }
        
        # Apply mapping for columns that exist
        existing_columns = [col for col in column_mapping if col in data.columns]
        data = data.rename(columns={col: column_mapping[col] for col in existing_columns})
        
        # Process status columns
        for col in ['er_status', 'pr_status', 'her2_status']:
            if col in data.columns:
                if data[col].dtype != 'object':
                    data[col] = data[col].map({1: 'positive', 0: 'negative'})
                else:
                    data[col] = data[col].str.lower()
        
        # Calculate outcomes
        if 'overall_survival_months' in data.columns and 'vital_status' in data.columns:
            data['survived_5yr'] = ((data['overall_survival_months'] > 60) | 
                                   ((data['overall_survival_months'] <= 60) & 
                                    (data['vital_status'] != 'DECEASED'))).astype(int)
        
        # Filter for complete data
        required_cols = ['age', 'tumor_size', 'grade', 'nodes_positive', 
                        'er_status', 'pr_status', 'her2_status']
        
        # Keep only rows with all required data
        for col in required_cols:
            if col in data.columns:
                data = data[data[col].notna()]
        
        print(f"Preprocessed TCGA data: {len(data)} patients with complete data")
        return data
    
    def run_digital_twin_on_cohort(self, 
                                  cohort: pd.DataFrame, 
                                  months: int = 60
                                  ) -> pd.DataFrame:
        """
        Run Digital Twin model on a patient cohort
        
        Args:
            cohort: DataFrame with patient data
            months: Number of months to simulate
            
        Returns:
            DataFrame with original data and Digital Twin predictions
        """
        results = cohort.copy()
        
        # Add columns for Digital Twin predictions
        results['dt_risk_5yr'] = None
        results['dt_ned_5yr'] = None
        results['dt_recurrence_any_5yr'] = None
        results['dt_death_5yr'] = None
        
        # Process each patient
        for idx, patient in results.iterrows():
            # Convert patient data to Digital Twin format
            patient_data = {
                'age': patient.get('age', 60),
                'tumor_size': patient.get('tumor_size', 20),
                'grade': patient.get('grade', 2),
                'nodes_positive': patient.get('nodes_positive', 0),
                'er_status': patient.get('er_status', 'positive'),
                'pr_status': patient.get('pr_status', 'positive'),
                'her2_status': patient.get('her2_status', 'negative'),
                'molecular_subtype': patient.get('molecular_subtype', 'Luminal A')
            }
            
            try:
                # Calculate risk
                risk = calculate_baseline_risk(patient_data)
                results.loc[idx, 'dt_risk_5yr'] = risk['5_year_risk']
                
                # Simulate progression
                progression = self.progression_simulator.simulate_progression(
                    patient_data, months=months, n_simulations=100
                )
                
                # Record results
                results.loc[idx, 'dt_ned_5yr'] = progression.get('NED', 0)
                results.loc[idx, 'dt_recurrence_any_5yr'] = (
                    progression.get('Local Recurrence', 0) + 
                    progression.get('Regional Recurrence', 0) + 
                    progression.get('Distant Metastasis', 0)
                )
                results.loc[idx, 'dt_death_5yr'] = progression.get('Death', 0)
                
            except Exception as e:
                print(f"Error processing patient {idx}: {str(e)}")
        
        print(f"Completed Digital Twin predictions for {len(results)} patients")
        return results
    
    def validate_metabric(self) -> Dict:
        """
        Validate Digital Twin against METABRIC data
        
        Returns:
            Dictionary with validation metrics
        """
        print("Validating against METABRIC dataset...")
        
        # Preprocess data
        cohort = self.preprocess_metabric()
        if cohort.empty:
            return {"error": "No valid METABRIC data"}
        
        # Filter for Stage II-like patients for better comparison
        stage_ii = cohort[
            (cohort['nodes_positive'] >= 1) & 
            (cohort['nodes_positive'] <= 3) &
            (cohort['tumor_size'] >= 10) & 
            (cohort['tumor_size'] <= 50)
        ]
        
        if len(stage_ii) > 0:
            print(f"Validating on {len(stage_ii)} Stage II patients")
            cohort = stage_ii
        
        # Run Digital Twin
        results = self.run_digital_twin_on_cohort(cohort)
        
        # Calculate metrics
        metrics = self._calculate_validation_metrics(results)
        
        # Store results
        self.validation_results['metabric'] = {
            'dataset': 'METABRIC',
            'n_patients': len(results),
            'metrics': metrics,
            'data': results
        }
        
        return metrics
    
    def validate_tcga(self) -> Dict:
        """
        Validate Digital Twin against TCGA data
        
        Returns:
            Dictionary with validation metrics
        """
        print("Validating against TCGA dataset...")
        
        # Preprocess data
        cohort = self.preprocess_tcga()
        if cohort.empty:
            return {"error": "No valid TCGA data"}
        
        # Filter for Stage II-like patients
        stage_ii = cohort[
            (cohort['nodes_positive'] >= 1) & 
            (cohort['nodes_positive'] <= 3) &
            (cohort['tumor_size'] >= 10) & 
            (cohort['tumor_size'] <= 50)
        ]
        
        if len(stage_ii) > 0:
            print(f"Validating on {len(stage_ii)} Stage II patients")
            cohort = stage_ii
        
        # Run Digital Twin
        results = self.run_digital_twin_on_cohort(cohort)
        
        # Calculate metrics
        metrics = self._calculate_validation_metrics(results)
        
        # Store results
        self.validation_results['tcga'] = {
            'dataset': 'TCGA',
            'n_patients': len(results),
            'metrics': metrics,
            'data': results
        }
        
        return metrics
    
    def _calculate_validation_metrics(self, results: pd.DataFrame) -> Dict:
        """
        Calculate validation metrics comparing predictions with actual outcomes
        
        Args:
            results: DataFrame with predictions and actual outcomes
            
        Returns:
            Dictionary of metrics
        """
        metrics = {}
        
        # Check if we have survival data
        if 'survived_5yr' in results.columns and 'dt_death_5yr' in results.columns:
            # Overall survival metrics
            actual_survival = results['survived_5yr'].fillna(0).values
            pred_survival = 1 - results['dt_death_5yr'].fillna(0).values
            
            # Binary classification metrics
            pred_survived = (pred_survival >= 0.5).astype(int)
            
            metrics['survival'] = {
                'accuracy': np.mean(pred_survived == actual_survival),
                'mean_predicted': np.mean(pred_survival),
                'mean_actual': np.mean(actual_survival),
                'absolute_error': np.abs(np.mean(pred_survival) - np.mean(actual_survival))
            }
            
            # Calculate ROC curve if we have enough data
            if len(set(actual_survival)) > 1:
                fpr, tpr, _ = roc_curve(actual_survival, pred_survival)
                metrics['survival']['auc'] = auc(fpr, tpr)
        
        # Check if we have recurrence data
        if 'recurrence_5yr' in results.columns and 'dt_recurrence_any_5yr' in results.columns:
            # Recurrence metrics
            actual_recurrence = results['recurrence_5yr'].fillna(0).values
            pred_recurrence = results['dt_recurrence_any_5yr'].fillna(0).values
            
            # Binary classification metrics
            pred_recurred = (pred_recurrence >= 0.15).astype(int)  # Using 15% threshold
            
            metrics['recurrence'] = {
                'accuracy': np.mean(pred_recurred == actual_recurrence),
                'mean_predicted': np.mean(pred_recurrence),
                'mean_actual': np.mean(actual_recurrence),
                'absolute_error': np.abs(np.mean(pred_recurrence) - np.mean(actual_recurrence))
            }
            
            # Calculate ROC curve if we have enough data
            if len(set(actual_recurrence)) > 1:
                fpr, tpr, _ = roc_curve(actual_recurrence, pred_recurrence)
                metrics['recurrence']['auc'] = auc(fpr, tpr)
        
        return metrics
    
    def plot_survival_comparison(self, dataset: str = 'metabric') -> None:
        """
        Plot Kaplan-Meier survival curves comparing actual vs predicted
        
        Args:
            dataset: Which dataset to use ('metabric' or 'tcga')
        """
        if dataset not in self.validation_results:
            print(f"No validation results for {dataset}. Run validate_{dataset}() first.")
            return
        
        results = self.validation_results[dataset]['data']
        
        if 'overall_survival_months' not in results.columns or 'vital_status' not in results.columns:
            print(f"No survival data available in {dataset} results")
            return
        
        # Set up the figure
        plt.figure(figsize=(10, 6))
        
        # Actual KM curve
        kmf_actual = KaplanMeierFitter()
        event_observed = (results['vital_status'] == 'DECEASED').astype(int)
        kmf_actual.fit(results['overall_survival_months'], event_observed, label='Actual')
        kmf_actual.plot(ci_show=True)
        
        # Predicted KM curve (based on Digital Twin death probabilities)
        # We'll create synthetic data based on predictions
        times = np.arange(0, 61)  # 0-60 months
        surv_probs = np.zeros(len(times))
        
        # Convert death probabilities to survival curve
        for t in times:
            if t == 0:
                surv_probs[t] = 1.0
            else:
                # Adjust survival probability based on Digital Twin death rate
                # This is a simplification - ideally we'd have time-to-event predictions
                mean_death_prob = results['dt_death_5yr'].mean()
                monthly_death_prob = 1 - (1 - mean_death_prob) ** (1/60)
                surv_probs[t] = surv_probs[t-1] * (1 - monthly_death_prob)
        
        plt.step(times, surv_probs, where='post', label='Digital Twin Predicted', linestyle='--')
        
        plt.title(f'Survival Comparison - {dataset.upper()} vs Digital Twin')
        plt.xlabel('Months')
        plt.ylabel('Survival Probability')
        plt.xlim(0, 60)
        plt.ylim(0, 1)
        plt.grid(alpha=0.3)
        plt.legend()
        
        # Save the figure
        os.makedirs('validation_results', exist_ok=True)
        plt.savefig(f'validation_results/survival_comparison_{dataset}.png')
        plt.close()
        
        print(f"Survival comparison plot saved to validation_results/survival_comparison_{dataset}.png")
    
    def plot_calibration_curve(self, dataset: str = 'metabric', outcome: str = 'survival') -> None:
        """
        Plot calibration curve showing predicted vs observed probabilities
        
        Args:
            dataset: Which dataset to use ('metabric' or 'tcga')
            outcome: Which outcome to evaluate ('survival' or 'recurrence')
        """
        if dataset not in self.validation_results:
            print(f"No validation results for {dataset}. Run validate_{dataset}() first.")
            return
        
        results = self.validation_results[dataset]['data']
        
        # Determine columns based on outcome
        if outcome == 'survival':
            if 'survived_5yr' not in results.columns or 'dt_death_5yr' not in results.columns:
                print(f"No survival data available in {dataset} results")
                return
            actual_col = 'survived_5yr'
            pred_col = 'dt_death_5yr'
            pred_label = '1 - Death Probability'
            title_outcome = 'Survival'
            
        elif outcome == 'recurrence':
            if 'recurrence_5yr' not in results.columns or 'dt_recurrence_any_5yr' not in results.columns:
                print(f"No recurrence data available in {dataset} results")
                return
            actual_col = 'recurrence_5yr'
            pred_col = 'dt_recurrence_any_5yr'
            pred_label = 'Recurrence Probability'
            title_outcome = 'Recurrence'
        else:
            print(f"Unknown outcome: {outcome}")
            return
        
        # Create prediction bins
        results['pred_bin'] = pd.qcut(results[pred_col], 10, duplicates='drop')
        
        # Calculate observed rates in each bin
        calibration_data = results.groupby('pred_bin').agg({
            actual_col: 'mean',
            pred_col: 'mean'
        }).reset_index()
        
        # Plot
        plt.figure(figsize=(8, 8))
        plt.scatter(calibration_data[pred_col], calibration_data[actual_col], 
                   s=100, alpha=0.7, label='Observed')
        
        # Add reference line
        plt.plot([0, 1], [0, 1], 'k--', label='Ideal Calibration')
        
        plt.title(f'{title_outcome} Calibration - {dataset.upper()} vs Digital Twin')
        plt.xlabel(f'Predicted {title_outcome} Probability')
        plt.ylabel(f'Observed {title_outcome} Probability')
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.grid(alpha=0.3)
        plt.legend()
        
        # Save the figure
        os.makedirs('validation_results', exist_ok=True)
        plt.savefig(f'validation_results/calibration_{outcome}_{dataset}.png')
        plt.close()
        
        print(f"Calibration plot saved to validation_results/calibration_{outcome}_{dataset}.png")
    
    def summarize_results(self) -> None:
        """Print summary of validation results."""
        if not self.validation_results:
            print("No validation results available. Run validation first.")
            return
        
        print("\n===== DIGITAL TWIN VALIDATION SUMMARY =====\n")
        
        for dataset, results in self.validation_results.items():
            print(f"\n{results['dataset']} Dataset ({results['n_patients']} patients):")
            
            metrics = results['metrics']
            
            if 'survival' in metrics:
                survival = metrics['survival']
                print("\nSurvival Prediction:")
                print(f"  Mean Predicted 5-year Survival: {(1 - survival['mean_predicted']) * 100:.1f}%")
                print(f"  Mean Actual 5-year Survival: {survival['mean_actual'] * 100:.1f}%")
                print(f"  Absolute Error: {survival['absolute_error'] * 100:.1f}%")
                if 'auc' in survival:
                    print(f"  AUC: {survival['auc']:.3f}")
            
            if 'recurrence' in metrics:
                recurrence = metrics['recurrence']
                print("\nRecurrence Prediction:")
                print(f"  Mean Predicted 5-year Recurrence: {recurrence['mean_predicted'] * 100:.1f}%")
                print(f"  Mean Actual 5-year Recurrence: {recurrence['mean_actual'] * 100:.1f}%")
                print(f"  Absolute Error: {recurrence['absolute_error'] * 100:.1f}%")
                if 'auc' in recurrence:
                    print(f"  AUC: {recurrence['auc']:.3f}")
            
            print("\n" + "-" * 40)
        
        print("\nValidation plots saved to validation_results/ directory") 