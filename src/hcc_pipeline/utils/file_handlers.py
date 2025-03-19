import os
import json
from pathlib import Path
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    return {
        "input_dir": os.getenv("INPUT_DIR", "data/progress_notes"),
        "output_dir": os.getenv("OUTPUT_DIR", "data/output"),
        "hcc_csv_path": os.getenv("HCC_CSV_PATH", "data/HCC_relevant_codes.csv") 
    }

def read_input_files(input_dir: str) -> Dict[str, str]:
    """Read all text files from input directory"""
    notes = {}
    input_path = Path(input_dir)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory {input_dir} not found")
    
    for file_path in input_path.glob("*"):
        if file_path.is_file() and not file_path.name.startswith('.'):
            with open(file_path, "r") as f:
                notes[file_path.name] = f.read()
    return notes

def save_output(results: Dict[str, Any], output_dir: str) -> None:
    """Save results to JSON file"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(output_path / "hcc_results.json", "w") as f:
        json.dump(results, f, indent=2)