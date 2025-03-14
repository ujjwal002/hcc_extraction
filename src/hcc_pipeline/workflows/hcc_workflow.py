from typing import TypedDict, Set, List, Dict  # Added Set import
from langgraph.graph import StateGraph, END
from ..core import extraction, evaluation

class PipelineState(TypedDict):
    note_text: str
    hcc_codes: Set[str]  # Now properly referenced
    conditions: List[Dict]
    hcc_relevant: List[Dict]

def create_hcc_workflow():
    """Create LangGraph workflow"""
    builder = StateGraph(PipelineState)
    
    def extract_node(state: PipelineState):
        return {"conditions": extraction.extract_conditions(state["note_text"])}
    
    def evaluate_node(state: PipelineState):
        return {"hcc_relevant": evaluation.evaluate_hcc(
            state["conditions"], 
            state["hcc_codes"]
        )}
    
    builder.add_node("extract", extract_node)
    builder.add_node("evaluate", evaluate_node)
    
    builder.set_entry_point("extract")
    builder.add_edge("extract", "evaluate")
    builder.add_edge("evaluate", END)
    
    return builder.compile()