"""
Script to run validation of the Cancer Digital Twin against real-world data.
"""

import os
import sys
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validation.model_validation import DigitalTwinValidator
from data.import_export.data_importer import DataImporter

def inspect_data_files():
    """Inspect data files to understand structure."""
    print("Inspecting data files to understand structure...")
    importer = DataImporter('data')
    
    # Inspect data files
    print("\n==== METABRIC File Structure ====")
    metabric_info = importer.inspect_file_structure('brca_metabric_clinical_data.tsv')
    if 'columns' in metabric_info:
        print(f"Columns: {metabric_info['columns']}")
    else:
        print(f"Error: {metabric_info.get('error', 'Unknown error')}")
    
    print("\n==== TCGA File Structure ====")
    tcga_info = importer.inspect_file_structure('tcga_clinical.csv')
    if 'columns' in tcga_info:
        print(f"Columns: {tcga_info['columns']}")
    else:
        print(f"Error: {tcga_info.get('error', 'Unknown error')}")
    
    print("\n==== Wisconsin File Structure ====")
    wisconsin_info = importer.inspect_file_structure('wisconsin_breast_cancer.csv')
    if 'columns' in wisconsin_info:
        print(f"Columns: {wisconsin_info['columns']}")
    else:
        print(f"Error: {wisconsin_info.get('error', 'Unknown error')}")

def main():
    """Run Digital Twin validation."""
    parser = argparse.ArgumentParser(description='Validate Cancer Digital Twin against real data')
    parser.add_argument('--dataset', type=str, default='both', 
                        choices=['metabric', 'tcga', 'both'],
                        help='Dataset to use for validation')
    parser.add_argument('--inspect', action='store_true',
                       help='Inspect data files before validation')
    
    args = parser.parse_args()
    
    # Optionally inspect data files
    if args.inspect:
        inspect_data_files()
        print("\nContinuing with validation...\n")
    
    # Initialize validator
    validator = DigitalTwinValidator()
    
    # Load datasets
    validator.load_datasets()
    
    # Run validation on selected datasets
    if args.dataset in ['metabric', 'both']:
        validator.validate_metabric()
        validator.plot_survival_comparison('metabric')
        validator.plot_calibration_curve('metabric', 'survival')
        if 'recurrence_5yr' in validator.preprocess_metabric().columns:
            validator.plot_calibration_curve('metabric', 'recurrence')
    
    if args.dataset in ['tcga', 'both']:
        validator.validate_tcga()
        validator.plot_survival_comparison('tcga')
        validator.plot_calibration_curve('tcga', 'survival')
        if 'recurrence_5yr' in validator.preprocess_tcga().columns:
            validator.plot_calibration_curve('tcga', 'recurrence')
    
    # Print summary
    validator.summarize_results()

if __name__ == "__main__":
    main() 