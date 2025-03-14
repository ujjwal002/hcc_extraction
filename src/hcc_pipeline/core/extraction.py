import json
import re
import logging
from typing import List, Dict
import google.generativeai as genai

logger = logging.getLogger(__name__)

def extract_conditions(text: str) -> List[Dict]:
    """Extract conditions with validation"""
    try:
        assessment_plan = re.search(
            r'Assessment / Plan\s*(.*?)(\n\w+:|$)',
            text,
            re.DOTALL | re.IGNORECASE
        )
        if not assessment_plan:
            return []
            
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""Extract medical conditions and ICD-10 codes from this text.
        Return ONLY JSON array with 'condition' and 'code' keys. Example:
        [{{"condition": "Diabetes", "code": "E11"}}]
        
        Text: {assessment_plan.group(1)[:5000]}
        """
        
        response = model.generate_content(prompt)
        json_str = response.text.strip().replace('```json', '').replace('```', '')
        
        conditions = []
        for item in json.loads(json_str):
            if 'condition' in item and 'code' in item:
                code = str(item['code']).upper().replace('.', '').strip()
                if code:  
                    conditions.append({
                        'condition': str(item['condition']).strip(),
                        'code': code
                    })
            else:
                logger.warning(f"Invalid condition format: {item}")
        
        return conditions
        
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON response: {response.text}")
        return []
    except Exception as e:
        logger.error(f"Extraction error: {str(e)}")
        return []
    """Extract conditions using Gemini API"""
    try:
        assessment_plan = re.search(
            r'Assessment / Plan\s*(.*?)(\n\w+:|$)',
            text,
            re.DOTALL | re.IGNORECASE
        )
        if not assessment_plan:
            logger.warning("No Assessment/Plan section found")
            return []
            
        model = genai.GenerativeModel('gemini-1.5-flash')  # or 'gemini-1.0-pro'
        prompt = f"""Extract medical conditions and ICD-10 codes from this text.
        Return ONLY JSON array with 'condition' and 'code' keys. Example:
        [{{"condition": "Diabetes", "code": "E11"}}]
        
        Text: {assessment_plan.group(1)[:5000]}
        """
        
        response = model.generate_content(prompt)
        json_str = response.text.strip().replace('```json', '').replace('```', '')
        conditions = json.loads(json_str)
        
        # Normalize codes
        for cond in conditions:
            cond['code'] = cond['code'].upper().replace('.', '').strip()
        return conditions
        
    except json.JSONDecodeError:
        logger.error("Failed to parse LLM response")
        return []
    except Exception as e:
        logger.error(f"Extraction error: {str(e)}")
        return []