"""
Data importer for Cancer Digital Twin application
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, Optional, Union, List, Any
import tarfile
import zipfile

class DataImporter:
    def __init__(self, base_path: Union[str, Path]):
        """
        Initialize DataImporter
        
        Args:
            base_path: Base path to data directory
        """
        self.base_path = Path(base_path)
        self._setup_logging()
        
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('DataImporter')

    def load_metabric_data(self) -> pd.DataFrame:
        """Load METABRIC clinical data"""
        try:
            file_path = self.base_path / 'brca_metabric_clinical_data.tsv'
            self.logger.info(f"Loading METABRIC data from {file_path}")
            
            # First peek at the file to see what columns actually exist
            try:
                sample_data = pd.read_csv(file_path, sep='\t', nrows=5)
                self.logger.info(f"METABRIC columns available: {sample_data.columns.tolist()}")
            except Exception as e:
                self.logger.warning(f"Failed to peek at METABRIC columns: {str(e)}")
            
            # Load the data
            data = pd.read_csv(file_path, sep='\t')
            
            # Basic preprocessing with flexible column handling
            data = self._preprocess_metabric(data)
            
            self.logger.info(f"Loaded METABRIC data: {len(data)} records")
            return data
        except Exception as e:
            self.logger.error(f"Error loading METABRIC data: {str(e)}")
            raise

    def load_tcga_data(self) -> pd.DataFrame:
        """Load TCGA clinical data"""
        try:
            file_path = self.base_path / 'tcga_clinical.csv'
            self.logger.info(f"Loading TCGA data from {file_path}")
            
            # First peek at the file to see what columns actually exist
            try:
                sample_data = pd.read_csv(file_path, nrows=5)
                self.logger.info(f"TCGA columns available: {sample_data.columns.tolist()}")
            except Exception as e:
                self.logger.warning(f"Failed to peek at TCGA columns: {str(e)}")
            
            # Load the data
            data = pd.read_csv(file_path)
            
            # Basic preprocessing with flexible column handling
            data = self._preprocess_tcga(data)
            
            self.logger.info(f"Loaded TCGA data: {len(data)} records")
            return data
        except Exception as e:
            self.logger.error(f"Error loading TCGA data: {str(e)}")
            raise

    def load_wisconsin_data(self) -> pd.DataFrame:
        """Load Wisconsin Breast Cancer data"""
        try:
            file_path = self.base_path / 'wisconsin_breast_cancer.csv'
            self.logger.info(f"Loading Wisconsin data from {file_path}")
            
            # First peek at the file to see what columns actually exist
            try:
                sample_data = pd.read_csv(file_path, nrows=5)
                self.logger.info(f"Wisconsin columns available: {sample_data.columns.tolist()}")
            except Exception as e:
                self.logger.warning(f"Failed to peek at Wisconsin columns: {str(e)}")
            
            # Load the data
            data = pd.read_csv(file_path)
            
            # Basic preprocessing with flexible column handling
            data = self._preprocess_wisconsin(data)
            
            self.logger.info(f"Loaded Wisconsin data: {len(data)} records")
            return data
        except Exception as e:
            self.logger.error(f"Error loading Wisconsin data: {str(e)}")
            raise

    def _preprocess_metabric(self, data: pd.DataFrame) -> pd.DataFrame:
        """Basic METABRIC data preprocessing with flexible column handling"""
        # Create a mapping of expected columns to potential actual column names
        column_mappings = {
            'PATIENT_ID': ['PATIENT_ID', 'patient_id', 'METABRIC_ID'],
            'AGE_AT_DIAGNOSIS': ['AGE_AT_DIAGNOSIS', 'age_at_diagnosis', 'Age'],
            'OVERALL_SURVIVAL_MONTHS': ['OVERALL_SURVIVAL_MONTHS', 'OS_MONTHS', 'survival_months'],
            'DEATH_FROM_CANCER': ['DEATH_FROM_CANCER', 'DSS_EVENT', 'died_from_cancer'],
            'TUMOR_SIZE': ['TUMOR_SIZE', 'tumor_size', 'size_mm'],
            'GRADE': ['GRADE', 'grade', 'Neoplasm_Histologic_Grade', 'tumor_grade'],
            'LYMPH_NODES_EXAMINED_POSITIVE': ['LYMPH_NODES_EXAMINED_POSITIVE', 'positive_nodes', 'nodal_status'],
            'ER_STATUS': ['ER_STATUS', 'ER_IHC', 'er_status'],
            'PR_STATUS': ['PR_STATUS', 'PR_IHC', 'pr_status'],
            'HER2_STATUS': ['HER2_STATUS', 'HER2_SNP6', 'her2_status', 'HER2_IHC_status']
        }
        
        # Create a dictionary to rename columns
        rename_dict = {}
        for expected_col, potential_cols in column_mappings.items():
            for potential_col in potential_cols:
                if potential_col in data.columns:
                    rename_dict[potential_col] = expected_col
                    break
        
        # Rename columns that exist
        data = data.rename(columns=rename_dict)
        
        # Create synthetic grade column if missing
        if 'GRADE' not in data.columns:
            self.logger.warning("Creating synthetic GRADE column (random values)")
            data['GRADE'] = np.random.choice([1, 2, 3], size=len(data), p=[0.2, 0.5, 0.3])
        
        # Create synthetic tumor size if missing
        if 'TUMOR_SIZE' not in data.columns:
            self.logger.warning("Creating synthetic TUMOR_SIZE column (random values)")
            data['TUMOR_SIZE'] = np.random.normal(loc=25, scale=10, size=len(data))
            data['TUMOR_SIZE'] = data['TUMOR_SIZE'].clip(lower=5, upper=70)
        
        # Create synthetic nodes positive if missing
        if 'LYMPH_NODES_EXAMINED_POSITIVE' not in data.columns:
            self.logger.warning("Creating synthetic LYMPH_NODES_EXAMINED_POSITIVE column (random values)")
            data['LYMPH_NODES_EXAMINED_POSITIVE'] = np.random.choice(
                [0, 1, 2, 3, 4, 5, 6], size=len(data), p=[0.5, 0.2, 0.1, 0.1, 0.05, 0.03, 0.02]
            )
        
        # Fill missing receptor status values
        for col in ['ER_STATUS', 'PR_STATUS', 'HER2_STATUS']:
            if col not in data.columns:
                self.logger.warning(f"Creating synthetic {col} column (random values)")
                data[col] = np.random.choice(['Positive', 'Negative'], size=len(data))
            
            # Standardize values
            if col in data.columns:
                status_map = {
                    'positive': 'Positive', 'pos': 'Positive', '1': 'Positive', 1: 'Positive', 'yes': 'Positive',
                    'negative': 'Negative', 'neg': 'Negative', '0': 'Negative', 0: 'Negative', 'no': 'Negative'
                }
                data[col] = data[col].astype(str).str.lower().map(status_map).fillna('Unknown')
        
        return data

    def _preprocess_tcga(self, data: pd.DataFrame) -> pd.DataFrame:
        """Basic TCGA data preprocessing with flexible column handling"""
        # Create a mapping of expected columns to potential actual column names
        column_mappings = {
            'patient_id': ['patient_id', 'bcr_patient_barcode', 'PATIENT_ID', 'ID'],
            'age_at_diagnosis': ['age_at_diagnosis', 'age_at_initial_pathologic_diagnosis', 'AGE', 'age'],
            'overall_survival_months': ['overall_survival_months', 'OS_MONTHS', 'days_to_last_followup', 'survival_months'],
            'vital_status': ['vital_status', 'OS_STATUS', 'patient_status'],
            'tumor_size': ['tumor_size', 'tumor_size_cm', 'tumor_size_mm'],
            'tumor_grade': ['tumor_grade', 'grade', 'neoplasm_histologic_grade'],
            'lymph_nodes_positive': ['lymph_nodes_positive', 'positive_lymph_nodes', 'nodal_status'],
            'er_status': ['er_status', 'estrogen_receptor_status', 'ER_STATUS'],
            'pr_status': ['pr_status', 'progesterone_receptor_status', 'PR_STATUS'],
            'her2_status': ['her2_status', 'her2_neu_status', 'HER2_STATUS']
        }
        
        # Create a dictionary to rename columns
        rename_dict = {}
        for expected_col, potential_cols in column_mappings.items():
            for potential_col in potential_cols:
                if potential_col in data.columns:
                    rename_dict[potential_col] = expected_col
                    break
        
        # Rename columns that exist
        data = data.rename(columns=rename_dict)
        
        # Create synthetic grade column if missing
        if 'tumor_grade' not in data.columns:
            self.logger.warning("Creating synthetic tumor_grade column (random values)")
            data['tumor_grade'] = np.random.choice([1, 2, 3], size=len(data), p=[0.2, 0.5, 0.3])
        
        # Create synthetic tumor size if missing
        if 'tumor_size' not in data.columns:
            self.logger.warning("Creating synthetic tumor_size column (random values)")
            data['tumor_size'] = np.random.normal(loc=25, scale=10, size=len(data))
            data['tumor_size'] = data['tumor_size'].clip(lower=5, upper=70)
        
        # Create synthetic nodes positive if missing
        if 'lymph_nodes_positive' not in data.columns:
            self.logger.warning("Creating synthetic lymph_nodes_positive column (random values)")
            data['lymph_nodes_positive'] = np.random.choice(
                [0, 1, 2, 3, 4, 5, 6], size=len(data), p=[0.5, 0.2, 0.1, 0.1, 0.05, 0.03, 0.02]
            )
        
        # Fill missing receptor status values
        for col in ['er_status', 'pr_status', 'her2_status']:
            if col not in data.columns:
                self.logger.warning(f"Creating synthetic {col} column (random values)")
                data[col] = np.random.choice(['Positive', 'Negative'], size=len(data))
            
            # Standardize values
            if col in data.columns:
                status_map = {
                    'positive': 'positive', 'pos': 'positive', '1': 'positive', 1: 'positive', 'yes': 'positive',
                    'negative': 'negative', 'neg': 'negative', '0': 'negative', 0: 'negative', 'no': 'negative'
                }
                data[col] = data[col].astype(str).str.lower().map(status_map).fillna('unknown')
        
        return data

    def _preprocess_wisconsin(self, data: pd.DataFrame) -> pd.DataFrame:
        """Basic Wisconsin data preprocessing with flexible column handling"""
        # Rename columns if needed (adjust based on your file structure)
        column_mapping = {
            'diagnosis': 'target',
            'radius_mean': 'tumor_size',
            'texture_mean': 'texture',
            'perimeter_mean': 'perimeter',
            'area_mean': 'area'
        }
        
        # Only rename columns that exist
        rename_dict = {col: new_col for col, new_col in column_mapping.items() if col in data.columns}
        data = data.rename(columns=rename_dict)
        
        # Convert diagnosis to binary
        if 'target' in data.columns:
            data['target'] = (data['target'] == 'M').astype(int)
        
        return data

    def get_ct_scan_paths(self) -> List[Path]:
        """Get list of CT scan file paths"""
        ct_dir = self.base_path / 'ct_scans'
        return list(ct_dir.glob('*.dcm'))  # Adjust pattern based on your file types

    def inspect_file_structure(self, file_path: str) -> Dict[str, Any]:
        """
        Inspect a data file and return structure information
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file structure info
        """
        try:
            full_path = self.base_path / file_path
            self.logger.info(f"Inspecting file: {full_path}")
            
            # Determine file type from extension
            if str(full_path).endswith('.csv'):
                df = pd.read_csv(full_path, nrows=5)
                sep = ','
            elif str(full_path).endswith('.tsv'):
                df = pd.read_csv(full_path, sep='\t', nrows=5)
                sep = '\t'
            else:
                # Try to infer separator
                with open(full_path, 'r') as f:
                    first_line = f.readline()
                if '\t' in first_line:
                    df = pd.read_csv(full_path, sep='\t', nrows=5)
                    sep = '\t'
                else:
                    df = pd.read_csv(full_path, nrows=5)
                    sep = ','
            
            # Get basic statistics
            file_size = full_path.stat().st_size / (1024 * 1024)  # Size in MB
            num_rows = len(pd.read_csv(full_path, sep=sep))
            num_cols = len(df.columns)
            
            return {
                'file_path': str(full_path),
                'file_size_mb': round(file_size, 2),
                'num_rows': num_rows,
                'num_columns': num_cols,
                'columns': df.columns.tolist(),
                'sample_data': df.head().to_dict()
            }
            
        except Exception as e:
            self.logger.error(f"Error inspecting file {file_path}: {str(e)}")
            return {
                'file_path': str(full_path),
                'error': str(e)
            }

def test_data_importer():
    """Test the DataImporter functionality"""
    importer = DataImporter('data')
    
    # Inspect data files first to see what columns are available
    metabric_info = importer.inspect_file_structure('brca_metabric_clinical_data.tsv')
    tcga_info = importer.inspect_file_structure('tcga_clinical.csv')
    wisconsin_info = importer.inspect_file_structure('wisconsin_breast_cancer.csv')
    
    print("\n=== METABRIC File Structure ===")
    print(f"Columns: {metabric_info.get('columns', 'Error')}")
    
    print("\n=== TCGA File Structure ===")
    print(f"Columns: {tcga_info.get('columns', 'Error')}")
    
    print("\n=== Wisconsin File Structure ===")
    print(f"Columns: {wisconsin_info.get('columns', 'Error')}")
    
    try:
        # Test METABRIC data loading
        metabric_data = importer.load_metabric_data()
        print("\nMETABRIC Data Sample:")
        print(metabric_data.head())
        print(f"METABRIC Shape: {metabric_data.shape}")
        
        # Test TCGA data loading
        tcga_data = importer.load_tcga_data()
        print("\nTCGA Data Sample:")
        print(tcga_data.head())
        print(f"TCGA Shape: {tcga_data.shape}")
        
        # Test Wisconsin data loading
        wisconsin_data = importer.load_wisconsin_data()
        print("\nWisconsin Data Sample:")
        print(wisconsin_data.head())
        print(f"Wisconsin Shape: {wisconsin_data.shape}")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    test_data_importer()