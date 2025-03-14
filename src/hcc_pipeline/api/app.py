from fastapi import FastAPI
from ..workflows import hcc_workflow

app = FastAPI()
workflow = hcc_workflow.create_hcc_workflow()

@app.post("/process")
async def process_document(text: str):
    """API endpoint for single document processing"""
    result = workflow.invoke({"raw_text": text})
    return {
        "conditions": result["conditions"],
        "hcc_relevant": result["hcc_relevant"]
    }