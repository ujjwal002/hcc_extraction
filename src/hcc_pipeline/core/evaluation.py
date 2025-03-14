import pandas as pd
from pathlib import Path
from typing import Set, List, Dict
import logging

logger = logging.getLogger(__name__)

def load_hcc_codes(csv_path: str) -> Set[str]:
    """Load HCC codes from CSV file"""
    try:
        if not Path(csv_path).exists():
            raise FileNotFoundError(f"HCC codes file not found: {csv_path}")
            
        df = pd.read_csv(csv_path)
        return {
            code.upper().replace(".", "").strip()
            for code in df["ICD-10-CM Codes"].astype(str).tolist()
        }
    except Exception as e:
        logger.error(f"HCC code loading failed: {str(e)}")
        raise

def evaluate_hcc(conditions: List[Dict], hcc_codes: Set[str]) -> List[Dict]:
    """Evaluate HCC-relevant conditions"""
    try:
        return [
            cond for cond in conditions
            if cond.get("code", "").upper().replace(".", "").strip() in hcc_codes
        ]
    except Exception as e:
        logger.error(f"HCC evaluation failed: {str(e)}")
        return []