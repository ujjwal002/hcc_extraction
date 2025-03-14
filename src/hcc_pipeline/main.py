import os
import logging
from dotenv import load_dotenv
from typing import Dict, Any
from langsmith import Client
from langsmith.run_helpers import traceable  # Add this import

from .utils import (
    configure_logging,
    load_config,
    read_input_files,
    save_output
)
from .core import extraction, evaluation
from .workflows.hcc_workflow import create_hcc_workflow
import google.generativeai as genai

load_dotenv()
client = Client(
    api_key=os.getenv("LANGSMITH_API_KEY"),
    # project_name=os.getenv("LANGSMITH_PROJECT", "hcc-pipeline")
)

def initialize_components(config: Dict[str, Any]):
    """Initialize core components"""
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    return create_hcc_workflow()

@traceable  
def process_notes(workflow, config: Dict[str, Any]):
    """Process all notes with tracing"""
    hcc_codes = evaluation.load_hcc_codes(config["hcc_csv_path"])
    notes = read_input_files(config["input_dir"])
    
    results = {}
    for note_name, note_text in notes.items():
        try:
            with traceable(name="process_note", run_type="chain"): 
                result = workflow.invoke({
                    "note_text": note_text,
                    "hcc_codes": hcc_codes
                })
                results[note_name] = {
                    "extracted_conditions": result["conditions"],
                    "hcc_relevant": result["hcc_relevant"]
                }
                logging.info(f"Processed {note_name} successfully")
        except Exception as e:
            logging.error(f"Failed to process {note_name}: {str(e)}")
            results[note_name] = {"error": str(e)}
    
    return results

def main():
    """Entry point with full observability"""
    configure_logging()
    config = load_config()
    workflow = initialize_components(config)
    
    with traceable(name="hcc_pipeline", run_type="chain") as cb:
        results = process_notes(workflow, config)
        cb.add_output(results) 
    
    save_output(results, config["output_dir"])

if __name__ == "__main__":
    main()