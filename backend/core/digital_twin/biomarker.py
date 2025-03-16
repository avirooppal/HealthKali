from pydantic import BaseModel
from typing import Optional, Dict, List

class BiomarkerStatus(BaseModel):
    """Class representing cancer biomarker status"""
    
    er_status: bool  # Estrogen Receptor
    pr_status: bool  # Progesterone Receptor
    her2_status: bool  # Human Epidermal Growth Factor Receptor 2
    
    # Advanced biomarkers - optional
    ki67_high: Optional[bool] = None  # Ki-67 proliferation marker
    pdl1_positive: Optional[bool] = None  # PD-L1 expression
    brca_mutation: Optional[bool] = None  # BRCA1/2 mutation
    
    # Genomic data - optional
    gene_expression: Optional[Dict[str, float]] = None  # Gene expression values
    mutations: Optional[List[str]] = None  # List of mutations
    
    def get_molecular_subtype(self) -> str:
        """
        Determine breast cancer molecular subtype based on biomarker status
        
        Returns:
            str: One of 'Luminal A', 'Luminal B HER2-', 'Luminal B HER2+', 
                 'HER2 Enriched', or 'Triple Negative'
        """
        if self.er_status or self.pr_status:
            if self.her2_status:
                return "Luminal B HER2+"
            else:
                # Differentiate Luminal A vs B based on Ki67 if available
                if self.ki67_high is True:
                    return "Luminal B HER2-"
                elif self.ki67_high is False:
                    return "Luminal A"
                else:
                    # Default classification without Ki67
                    return "Luminal A" if self.er_status and self.pr_status else "Luminal B HER2-"
        else:
            return "HER2 Enriched" if self.her2_status else "Triple Negative"
    
    def get_treatment_sensitivity(self) -> Dict[str, float]:
        """
        Calculate predicted sensitivity to different treatment types
        
        Returns:
            Dict[str, float]: Sensitivity scores for different treatments
        """
        # Base sensitivity values
        sensitivity = {
            "chemotherapy": 0.5,
            "hormone_therapy": 0.1,
            "anti_her2_therapy": 0.1,
            "immunotherapy": 0.2,
            "parp_inhibitors": 0.1
        }
        
        # Adjust based on biomarkers
        # Hormone therapy
        if self.er_status or self.pr_status:
            sensitivity["hormone_therapy"] = 0.7 if self.er_status and self.pr_status else 0.5
        
        # HER2-targeted therapy
        if self.her2_status:
            sensitivity["anti_her2_therapy"] = 0.8
        
        # Chemotherapy - triple negative or high ki67 more sensitive
        if not (self.er_status or self.pr_status or self.her2_status):
            sensitivity["chemotherapy"] = 0.7  # Triple negative
        elif self.ki67_high:
            sensitivity["chemotherapy"] = 0.65  # High proliferation
        
        # Immunotherapy
        if self.pdl1_positive:
            sensitivity["immunotherapy"] = 0.6
        
        # PARP inhibitors
        if self.brca_mutation:
            sensitivity["parp_inhibitors"] = 0.7
        
        return sensitivity
    
    def is_triple_negative(self) -> bool:
        """Check if the cancer is triple negative"""
        return not (self.er_status or self.pr_status or self.her2_status)
    
    def is_hormone_positive(self) -> bool:
        """Check if the cancer is hormone receptor positive"""
        return self.er_status or self.pr_status
    
    def is_her2_positive(self) -> bool:
        """Check if the cancer is HER2 positive"""
        return self.her2_status 