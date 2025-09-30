"""AI Client for LLM-powered threat generation."""

import json
from typing import Dict, List
import litellm
from models import AIThreatsResponseList


def filter_out_of_scope_components(model: Dict) -> Dict:
    """Filter out components marked as out-of-scope from the threat model."""
    filtered_model = model.copy()
    
    for diagram in filtered_model.get('detail', {}).get('diagrams', []):
        if 'cells' in diagram:
            # Filter out cells that are out of scope
            diagram['cells'] = [
                cell for cell in diagram['cells']
                if not (cell.get('data', {}).get('outOfScope') == True)
            ]
    
    return filtered_model

def generate_threats(schema: Dict, model: Dict, model_name: str) -> Dict[str, List[Dict]]:
    """Generate AI-powered threats for all in-scope components."""
    # Filter out components that are out of scope
    filtered_model = filter_out_of_scope_components(model)
    
    schema_json = json.dumps(schema, indent=2)
    model_json = json.dumps(filtered_model, indent=2)
    
    # Read prompt from file
    with open('prompt.txt', 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    system_prompt = prompt_template.format(
        schema_json=schema_json,
        model_json=model_json
    )
    
    try:
        # Use LiteLLM to call the specified model
        litellm.enable_json_schema_validation = True
        print(f"Generating threats with {model_name}")
        response = litellm.completion(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Generate threats for all elements in the model."}
            ],
            temperature=0.3,
            response_format=AIThreatsResponseList,
            timeout=7200,
            # api_base="http://192.168.110.99:11434"
            api_base="https://550ffac8b6d1bb37-11434.af-za-1.gpu-instance.novita.ai"
        )
        
        # Parse the response using the Pydantic model
        ai_response = AIThreatsResponseList.model_validate_json(response.choices[0].message.content)

        
        # Convert to the format expected by utils.py
        threats_data = {}
        for item in ai_response.root:
            threats_data[item.id] = [threat.model_dump() for threat in item.threats]
#        print(threats_data)
        return threats_data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response from AI: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error calling LLM: {str(e)}")
