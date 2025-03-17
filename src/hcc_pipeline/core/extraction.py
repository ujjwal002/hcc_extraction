import json
import re
import logging
from typing import List, Dict
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
import google.generativeai as genai
import time

logger = logging.getLogger(__name__)

class Condition(BaseModel):
    condition: str = Field(..., description="The medical condition name")
    code: str = Field(..., description="The ICD-10 code")

    def get(self, key: str, default=None):
        return getattr(self, key, default)

    def to_dict(self) -> Dict[str, str]:
        return {"condition": self.condition, "code": self.code}

CONDITION_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["text"],
    template="""Extract medical conditions and ICD-10 codes from this text.
    Return ONLY JSON array with 'condition' and 'code' keys. Example:
    [{{"condition": "Diabetes", "code": "E11"}}]
    
    Text: {text}
    """
)

def extract_conditions(text: str, max_retries: int = 3) -> List[Dict[str, str]]:
    """Extract conditions using Gemini API with retry logic"""
    try:
        assessment_plan = re.search(
            r'Assessment\s*[\/]\s*Plan\s*(.*?)(\n\w+:|$)',
            text, 
            re.DOTALL | re.IGNORECASE
        )
        if not assessment_plan:
            logger.warning("No Assessment/Plan section found")
            return []
            
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = CONDITION_EXTRACTION_PROMPT.format(text=assessment_plan.group(1)[:5000])
        
        for attempt in range(max_retries):
            try:
                response = model.generate_content(prompt)
                json_str = response.text.strip().replace('```json', '').replace('```', '')
                conditions_raw = json.loads(json_str)
                break  
            except Exception as e:
                logger.error(f"API call failed: {type(e).__name__} - {str(e)}")
                if "429" in str(e).lower(): 
                    if attempt < max_retries - 1:
                        delay = 2 ** attempt  
                        logger.warning(f"Quota exceeded, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                        continue
                    logger.error(f"Max retries reached: {str(e)}")
                    return []
                raise 

        conditions = []
        for cond in conditions_raw:
            condition_name = cond.get("condition") or ""
            code_value = cond.get("code") or ""
            condition = Condition(
                condition=condition_name,
                code=code_value.upper().replace('.', '').strip()
            )
            conditions.append(condition.to_dict())
            
        return conditions
        
    except json.JSONDecodeError:
        logger.error("Failed to parse LLM response")
        return []
    except AttributeError as e:
        logger.error(f"Extraction error - invalid data format: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Extraction error: {str(e)}")
        return []