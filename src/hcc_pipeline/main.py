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

logger = logging.getLogger(__name__)

load_dotenv()
logger.info(f"GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY')}")


client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))

def initialize_components(config: Dict[str, Any]):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in environment variables")
    logger.info(f"Initializing with GEMINI_API_KEY: {api_key[:4]}...")
    genai.configure(api_key=api_key)
    return create_hcc_workflow()

@traceable
def process_notes(workflow, config: Dict[str, Any]) -> Dict[str, Any]:
    hcc_codes = evaluation.load_hcc_codes(config["hcc_csv_path"])
    notes = read_input_files(config["input_dir"])
    
    if not notes:
        logger.warning("No notes found in input directory: %s", config["input_dir"])
        return {"results": {}, "errors": ["No notes found in input directory"]}
    
    results = {}
    for note_name, note_text in notes.items():
        try:
            initial_state = PipelineState(
                note_text=str(note_text),
                hcc_codes=hcc_codes,
                conditions=[],
                hcc_relevant=[],
                errors=[],
                warnings=[]
            )
            
            logger.info("Processing note: %s", note_name)
            result = workflow.invoke(initial_state)
            logger.debug(f"Workflow result for {note_name}: {result}")
            
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
                "extracted_conditions": [],
                "hcc_relevant": [],
                "warnings": [],
                "errors": [str(e)]
            }
    
    return {"results": results, "errors": []}

def main(config: Dict[str, Any] = None) -> Dict[str, Any]:
    configure_logging()
    try:
        config = config or {
            "input_dir": "data/progress_notes",
            "output_dir": "data/output",
            "hcc_csv_path": "data/HCC_relevant_codes.csv"
        }
        logger.info(f"Running pipeline with config: {config}")
        workflow = initialize_components(config)
        
        @traceable(name="hcc_pipeline", run_type="chain")
        def execute_pipeline():
            results = process_notes(workflow, config)
            logger.info(f"Pipeline results: {results}")
            save_output(results["results"], config["output_dir"])
            return results
        
        return execute_pipeline()
        
    except Exception as e:
        logger.critical(f"Critical pipeline failure: {str(e)}")
        return {"results": {}, "errors": [str(e)]}

if __name__ == "__main__":
    main()