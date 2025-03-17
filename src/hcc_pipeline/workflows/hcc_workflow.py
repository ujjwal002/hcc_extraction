from typing import TypedDict, Set, List, Dict, Any
from langgraph.graph import StateGraph, END
from ..core import extraction, evaluation
import logging
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time


logger = logging.getLogger(__name__)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.critical("GEMINI_API_KEY not found in environment variables")
    raise ValueError("GEMINI_API_KEY is required for Google Generative AI")
logger.info(f"Configuring Google API with key: {api_key[:4]}...")
genai.configure(api_key=api_key)

class PipelineState(TypedDict):
    note_text: str
    hcc_codes: Set[str]
    conditions: List[Dict]
    hcc_relevant: List[Dict]
    errors: List[str]
    warnings: List[str]

def create_hcc_workflow():
    """Create workflow with state validation and fallbacks"""
    builder = StateGraph(PipelineState)
    
    def validate_input_state(state: PipelineState) -> Dict[str, Any]:
        logger.info(f"Received state in validate_input: {state}")
        if not state.get("note_text"):
            error_msg = "Missing note_text in input state"
            logger.error(error_msg)
            return {
                "errors": state.get("errors", []) + [error_msg],
                "warnings": state.get("warnings", []),
                "note_text": state.get("note_text", ""),
                "conditions": state.get("conditions", []),
                "hcc_relevant": state.get("hcc_relevant", []),
                "hcc_codes": state.get("hcc_codes", set())
            }
        logger.info("Input state validated successfully")
        return {"warnings": state.get("warnings", []), "errors": state.get("errors", [])}

    def extract_node(state: PipelineState) -> Dict[str, Any]:
        logger.debug("Extract node received state: %s", state)
        time.sleep(1)  

        try:
            if not state.get("note_text"):
                raise ValueError("Cannot extract conditions without note_text")
            conditions = extraction.extract_conditions(state["note_text"]) or []
            logger.info(f"Extracted {len(conditions)} conditions: {conditions}")
            return {
                "conditions": conditions,
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
            warnings.append("No conditions extracted from note")
            logger.warning("No conditions extracted from note")
        else:
            logger.info("Conditions validated: %s", state["conditions"])
        return {"warnings": warnings, "errors": state.get("errors", [])}

    def evaluate_node(state: PipelineState) -> Dict[str, Any]:
        logger.debug("Evaluate node received state: %s", state)
        try:
            hcc_relevant = evaluation.evaluate_hcc(
                state.get("conditions", []),
                state["hcc_codes"]
            )
            logger.info(f"Found {len(hcc_relevant)} HCC-relevant conditions: {hcc_relevant}")
            return {
                "hcc_relevant": hcc_relevant,
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

def run_hcc_workflow(state: Dict[str, Any] = None) -> Dict[str, Any]:
    """Wrapper function to run the workflow with a given state."""
    logger.info(f"Raw input state received: {state}")
    if not state:
        logger.warning("No input state provided, using default")
        state = {
            "note_text": "Assessment/Plan:\n1. Diabetes (E11.9)\n2. Hypertension (I10)",
            "hcc_codes": {"E119", "I10"},
            "conditions": [],
            "hcc_relevant": [],
            "errors": [],
            "warnings": []
        }
    
    initial_state = {
        "note_text": state.get("note_text", ""),
        "hcc_codes": set(state.get("hcc_codes", [])),
        "conditions": state.get("conditions", []),
        "hcc_relevant": state.get("hcc_relevant", []),
        "errors": state.get("errors", []),
        "warnings": state.get("warnings", [])
    }
    logger.info(f"Running workflow with initial state: {initial_state}")
    workflow = create_hcc_workflow()
    result = workflow.invoke(initial_state)
    logger.info(f"Workflow result: {result}")
    return result

# if __name__ == "__main__":
#     test_state = {
#         "note_text": "Assessment/Plan:\n1. Diabetes (E11.9)\n2. Hypertension (I10)",
#         "hcc_codes": {"E119", "I10"},
#         "conditions": [],
#         "hcc_relevant": [],
#         "errors": [],
#         "warnings": []
#     }
#     result = run_hcc_workflow(test_state)
#     print("Workflow result:", result)