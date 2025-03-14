import os
import logging
from dotenv import load_dotenv
from typing import Dict, Any
from langsmith import Client
from langsmith.run_helpers import traceable
from .utils import configure_logging, load_config, read_input_files, save_output
from .core import extraction, evaluation
from .workflows.hcc_workflow import create_hcc_workflow, PipelineState 
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

load_dotenv()
client = Client(
    api_key=os.getenv("LANGSMITH_API_KEY"),
    # project_name=os.getenv("LANGSMITH_PROJECT", "hcc-pipeline")
)

def initialize_components(config: Dict[str, Any]):
    """Initialize core components with validation"""
    if "GEMINI_API_KEY" not in os.environ:
        raise ValueError("Missing GEMINI_API_KEY in environment variables")
    
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    return create_hcc_workflow()

@traceable
def process_notes(workflow, config: Dict[str, Any]):
    """Process notes with comprehensive state handling"""
    hcc_codes = evaluation.load_hcc_codes(config["hcc_csv_path"])
    notes = read_input_files(config["input_dir"])
    
    results = {}
    for note_name, note_text in notes.items():
        try:
            initial_state = PipelineState(
                note_text=str(note_text),
                hcc_codes=hcc_codes,
                conditions=[], 
                hcc_relevant=[]
            )
            
            logger.info("Processing note: %s", note_name)
            result = workflow.invoke(initial_state)
            
            output = {
                "extracted_conditions": result.get("conditions", []),
                "hcc_relevant": result.get("hcc_relevant", []),
                "warnings": result.get("warnings", []),
                "errors": result.get("errors", [])
            }
            results[note_name] = output
            
        except Exception as e:
            logger.error("Critical failure processing %s: %s", note_name, str(e))
            results[note_name] = {
                "error": str(e),
                "extracted_conditions": [],
                "hcc_relevant": []
            }
    
    return results
def main():
    """Main entry point with proper tracing"""
    configure_logging()
    try:
        config = load_config()
        workflow = initialize_components(config)
        
        @traceable(name="hcc_pipeline", run_type="chain")
        def execute_pipeline():
            return process_notes(workflow, config)
        
        results = execute_pipeline()
        save_output(results, config["output_dir"])
        logging.info("Pipeline completed successfully")
        
    except Exception as e:
        logging.critical(f"Critical pipeline failure: {str(e)}")
        raise
if __name__ == "__main__":
    main()