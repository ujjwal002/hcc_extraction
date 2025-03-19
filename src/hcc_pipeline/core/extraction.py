import re
import logging
from typing import List
from pydantic import BaseModel, Field, ValidationError
from langchain.prompts import PromptTemplate
import anthropic
import time
import json
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')

# Load API key
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    logger.critical("ANTHROPIC_API_KEY not found in environment variables")
    raise ValueError("ANTHROPIC_API_KEY is required")
logger.info(f"Using API key: {api_key[:4]}...")

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=api_key)

class Condition(BaseModel):
    condition: str = Field(..., description="The medical condition name")
    code: str = Field(..., description="The ICD-10 code")

CONDITION_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["text"],
    template="Extract medical conditions and ICD-10 codes from this text: {text}. Return a JSON array of objects with 'condition' and 'code' keys, or [] if none. Provide only the JSON array, no additional text."
)

def extract_conditions(text: str, max_retries: int = 3) -> List[dict]:
    """Extract conditions using Claude API with a simplified PromptTemplate"""
    logger.debug(f"Input text: {text}")
    
    try:
        assessment_plan = re.search(
            r'Assessment\s*[\/]\s*Plan\s*:\s*(.*?)(\n\w+:|$)',
            text,
            re.DOTALL | re.IGNORECASE
        )
        if not assessment_plan:
            logger.warning("No Assessment/Plan section found in text")
            return []
        text_to_process = assessment_plan.group(1)[:5000].strip()
        logger.debug(f"Extracted Assessment/Plan: {text_to_process}")

        try:
            prompt = CONDITION_EXTRACTION_PROMPT.format(text=text_to_process)
            logger.debug(f"Generated prompt: {prompt}")
        except Exception as e:
            logger.error(f"Prompt formatting failed: {type(e).__name__} - {str(e)}")
            return []

        for attempt in range(max_retries):
            try:
                logger.info(f"Calling Claude API, attempt {attempt + 1}/{max_retries}")
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",  # Use a suitable Claude model
                    max_tokens=1000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                json_str = response.content[0].text.strip()
                logger.debug(f"Raw Claude response: {json_str}")

                try:
                    parsed_conditions = json.loads(json_str)
                    logger.debug(f"Parsed JSON: {parsed_conditions}")
                except json.JSONDecodeError as jde:
                    logger.error(f"Failed to parse response as JSON: {json_str}, error: {jde}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return []

                if not isinstance(parsed_conditions, list):
                    logger.error(f"Response is not a JSON array: {parsed_conditions}")
                    return []

                conditions = []
                for cond in parsed_conditions:
                    try:
                        validated_cond = Condition(**cond).dict()
                        validated_cond["code"] = validated_cond["code"].upper().replace('.', '').strip()
                        conditions.append(validated_cond)
                        logger.debug(f"Validated condition: {validated_cond}")
                    except ValidationError as ve:
                        logger.warning(f"Validation failed for condition: {cond}, error: {ve}")
                        continue

                logger.info(f"Successfully extracted {len(conditions)} conditions: {conditions}")
                return conditions

            except Exception as e:
                logger.error(f"API call failed, attempt {attempt + 1}: {type(e).__name__} - {str(e)}")
                if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise

    except Exception as e:
        logger.error(f"Extraction error: {type(e).__name__} - {str(e)}")
        return []

if __name__ == "__main__":
    test_text = "Assessment/Plan:\n1. Diabetes (E11.9)\n2. Hypertension (I10)"
    result = extract_conditions(test_text)
    print(f"Test result: {result}")