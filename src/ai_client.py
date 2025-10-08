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
    logger = logging.getLogger("threat_modeling.ai_client")
    logger.info("Starting threat generation...")
    
  
    # Prepare prompt
    prompt_template = open('prompt.txt', 'r', encoding='utf-8').read()
    
    system_prompt = prompt_template.format(
        schema_json=json.dumps(schema, indent=2),
        model_json=json.dumps(model, indent=2),
    )
    
    try:
        logger.info(f"Calling LLM: {model_name}")

        # ============================================================================
        # CONFIGURATION: Adjust these settings based on your LLM provider
        # See README.md "Tested LLM Providers" section for recommended configurations
        # ============================================================================
        
        # JSON Schema Validation: Enable for OpenAI, xAI (comment out for Anthropic, Gemini, and some Novita models)
        litellm.enable_json_schema_validation = True
        
        litellm.drop_params = True

        response = litellm.completion(
            model = model_name,
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Analyze provided Threat Dragon model, generate threats and mitigations for elements and return a valid JSON following the rules."}
            ],
            
            # Temperature: Controls randomness (0.0=deterministic, 1.0=creative)
            # Lower values (0.1) provide consistent, focused threat modeling results
            temperature = 0.1,

            # Response Format: Forces structured JSON output (comment out for Anthropic, Gemini, some Novita models)
            # Requires JSON schema validation support from the LLM provider
            response_format = AIThreatsResponseList,

            # Timeout: Request timeout in seconds (14400 = 4 hours for large models)
            timeout = 14400,
            
            # Max Tokens: Maximum response length - adjust based on model capabilities
            # Higher values allow more comprehensive threat descriptions
            max_tokens=24000,

            # API Base URL: Override for custom endpoints (required for Novita, custom deployments)
            # Examples:
            #   - Custom: api_base="https://your-custom-endpoint.com"
        )
        
        # Parse response
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
