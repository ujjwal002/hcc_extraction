from typing import TypedDict, Set, List, Dict
from langgraph.graph import StateGraph, END
from ..core import extraction, evaluation
import logging

logger = logging.getLogger(__name__)

class PipelineState(TypedDict):
    note_text: str
    hcc_codes: Set[str]
    conditions: List[Dict]
    hcc_relevant: List[Dict]

def create_hcc_workflow():
    """Create workflow with state validation and fallbacks"""
    builder = StateGraph(PipelineState)
    
    def validate_input_state(state: PipelineState):
        """Pre-extraction validation"""
        logger.debug("Validating input state: %s", state.keys())
        if not state.get("note_text"):
            logger.error("Missing note_text in input state")
            raise ValueError("note_text is required")
        return state

    def extract_node(state: PipelineState):
        """Enhanced extraction with fallbacks"""
        try:
            logger.debug("Extract node received state: %s", state.keys())
            conditions = extraction.extract_conditions(state["note_text"]) or []
            return {"conditions": conditions}
        except Exception as e:
            logger.error("Extraction failed: %s", str(e))
            return {"conditions": [], "error": str(e)}

    def validate_extraction(state: PipelineState):
        """Post-extraction validation"""
        logger.debug("Validation node received state: %s", state.keys())
        if not state.get("conditions"):
            logger.warning("No conditions extracted from note")
        return state

    def evaluate_node(state: PipelineState):
        """Safe evaluation with validation"""
        logger.debug("Evaluate node received state: %s", state.keys())
        try:
            return {
                "hcc_relevant": evaluation.evaluate_hcc(
                    state.get("conditions", []),
                    state["hcc_codes"]
                )
            }
        except Exception as e:
            logger.error("Evaluation failed: %s", str(e))
            return {"hcc_relevant": [], "error": str(e)}

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