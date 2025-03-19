# hcc_pipeline/workflows/hcc_workflow.py
from typing import TypedDict, Set, List, Dict, Any
from langgraph.graph import StateGraph, END
from ..core import extraction
from ..core import evaluation
from ..utils.file_handlers import read_input_files
import logging
import os
from dotenv import load_dotenv
import anthropic

logger = logging.getLogger(__name__)

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    logger.critical("ANTHROPIC_API_KEY not found in environment variables")
    raise ValueError("ANTHROPIC_API_KEY is required for Claude API")
logger.info(f"Configuring Claude API with key: {api_key[:4]}...")
client = anthropic.Anthropic(api_key=api_key)

class PipelineState(TypedDict):
    notes: List[Dict[str, str]]  
    hcc_codes: Set[str]
    conditions: List[Dict[str, List[Dict]]]  
    hcc_relevant: List[Dict[str, List[Dict]]] 
    errors: List[str]
    warnings: List[str]

def create_hcc_workflow():
    builder = StateGraph(PipelineState)
    
    def validate_input_state(state: PipelineState) -> Dict[str, Any]:
        logger.info(f"Received state in validate_input: {state}")
        notes = state.get("notes", [])
        
        if not notes:
            try:
                file_notes = read_input_files("data/progress_notes")
                if file_notes:
                    notes = [{"filename": name, "content": content} for name, content in file_notes.items()]
                    logger.info(f"Loaded {len(notes)} notes from data/progress_notes")
                else:
                    logger.warning("No notes found in data/progress_notes")
            except Exception as e:
                error_msg = f"Failed to load notes from files: {str(e)}"
                logger.error(error_msg)
                return {
                    "errors": state.get("errors", []) + [error_msg],
                    "warnings": state.get("warnings", []),
                    "notes": [],
                    "conditions": [],
                    "hcc_relevant": [],
                    "hcc_codes": state.get("hcc_codes", set())
                }
        
        if not notes:
            error_msg = "No notes provided and no files found"
            logger.error(error_msg)
            return {
                "errors": state.get("errors", []) + [error_msg],
                "warnings": state.get("warnings", []),
                "notes": [],
                "conditions": [],
                "hcc_relevant": [],
                "hcc_codes": state.get("hcc_codes", set())
            }
        
        logger.info(f"Validated {len(notes)} notes")
        return {
            "notes": notes,
            "warnings": state.get("warnings", []),
            "errors": state.get("errors", []),
            "hcc_codes": state.get("hcc_codes", set()),
            "conditions": [],
            "hcc_relevant": []
        }

    def extract_node(state: PipelineState) -> Dict[str, Any]:
        logger.debug("Extract node received state: %s", state)
        conditions_by_file = []
        try:
            for note in state["notes"]:
                filename = note["filename"]
                content = note["content"]
                conditions = extraction.extract_conditions(content) or []
                conditions_by_file.append({filename: conditions})
                logger.info(f"Extracted {len(conditions)} conditions from {filename}")
            return {
                "conditions": conditions_by_file,
                "warnings": state.get("warnings", []),
                "errors": state.get("errors", [])
            }
        except Exception as e:
            logger.error("Extraction failed: %s", str(e))
            return {
                "conditions": [],
                "errors": state.get("errors", []) + [f"Extraction failed: {str(e)}"],
                "warnings": state.get("warnings", [])
            }

    def validate_extraction(state: PipelineState) -> Dict[str, Any]:
        logger.debug("Validation node received state: %s", state)
        warnings = state.get("warnings", [])
        if not state.get("conditions"):
            warnings.append("No conditions extracted from any note")
            logger.warning("No conditions extracted from any note")
        else:
            for cond_dict in state["conditions"]:
                for filename, conds in cond_dict.items():
                    if not conds:
                        warnings.append(f"No conditions extracted from {filename}")
                        logger.warning(f"No conditions extracted from {filename}")
                    else:
                        logger.info(f"Validated conditions for {filename}: {conds}")
        return {"warnings": warnings, "errors": state.get("errors", [])}

    def evaluate_node(state: PipelineState) -> Dict[str, Any]:
        logger.debug("Evaluate node received state: %s", state)
        try:
            hcc_codes = state.get("hcc_codes", set())
            if not hcc_codes:
                hcc_codes = evaluation.load_hcc_codes("data/HCC_relevant_codes.csv")
                logger.info(f"Loaded {len(hcc_codes)} HCC codes from file")
            hcc_relevant_by_file = []
            for cond_dict in state.get("conditions", []):
                for filename, conditions in cond_dict.items():
                    hcc_relevant = evaluation.evaluate_hcc(conditions, hcc_codes)
                    hcc_relevant_by_file.append({filename: hcc_relevant})
                    logger.info(f"Found {len(hcc_relevant)} HCC-relevant conditions in {filename}")
            return {
                "hcc_relevant": hcc_relevant_by_file,
                "warnings": state.get("warnings", []),
                "errors": state.get("errors", [])
            }
        except Exception as e:
            logger.error("Evaluation failed: %s", str(e))
            return {
                "hcc_relevant": [],
                "errors": state.get("errors", []) + [f"Evaluation failed: {str(e)}"],
                "warnings": state.get("warnings", [])
            }

    builder.add_node("validate_input", validate_input_state)
    builder.add_node("extract", extract_node)
    builder.add_node("validate_extraction", validate_extraction)
    builder.add_node("evaluate", evaluate_node)
    
    builder.set_entry_point("validate_input")
    builder.add_edge("validate_input", "extract")
    builder.add_edge("extract", "validate_extraction")
    builder.add_edge("validate_extraction", "evaluate")
    builder.add_edge("evaluate", END)
    
    return builder.compile()