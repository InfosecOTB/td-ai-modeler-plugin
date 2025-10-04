"""Simplified AI Client for LLM-powered threat generation."""

import json
import re
import logging
from typing import Dict, List
import litellm
from models import AIThreatsResponseList

logger = logging.getLogger(__name__)


def generate_threats(schema: Dict, model: Dict, model_name: str) -> Dict[str, List[Dict]]:
    """Generate AI-powered threats for all in-scope components."""
    logger.info("Starting threat generation...")
    
  
    # Prepare prompt
    prompt_template = open('prompt.txt', 'r', encoding='utf-8').read()
    
    system_prompt = prompt_template.format(
        schema_json=json.dumps(schema, indent=2),
        model_json=json.dumps(model, indent=2),
    )
    
    try:
        # Call LLM
        logger.info(f"Calling LLM: {model_name}")
        # litellm.enable_json_schema_validation = True
        litellm.drop_params = True

        response = litellm.completion(
            model = model_name,
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Generate threats for all elements in the model. Return a JSON object with an 'items' array containing threat data for each element."}
            ],
            temperature = 0.1,
            response_format = AIThreatsResponseList,
            timeout = 17200,
            max_tokens=24000,
            # api_base="https://d246c05785707d50-11434.af-za-1.gpu-instance.novita.ai"
            # api_base="http://192.168.110.99:11434"
        )
        
        # Parse response
        # ai_response = AIThreatsResponseList.model_validate_json(response.choices[0].message.content)
        logger.debug(f"/\n\nResponse: {response}")
        try:
            ai_response = AIThreatsResponseList.model_validate_json(response.choices[0].message.content)
        except Exception:
            logger.warning("LLM returned invalid JSON. Trying to extract JSON...")
            # Try to find JSON substring
            match = re.search(r"\{.*\}", response.choices[0].message.content, re.S)
            if match:
                ai_response = AIThreatsResponseList.model_validate_json(match.group())
            else:
                raise

        
        logger.debug(f"/\n\nAI Response: {ai_response}")
        
        # Convert to expected format
        threats_data = {
            item.id: [threat.model_dump() for threat in item.threats] 
            for item in ai_response.items
        }
        
        total_threats = sum(len(threats) for threats in threats_data.values())
        logger.info(f"Generated {total_threats} threats for {len(threats_data)} elements")
        
        return threats_data
        
    except Exception as e:
        logger.error(f"LLM error: {str(e)}")
        raise ValueError(f"Error calling LLM: {str(e)}")
