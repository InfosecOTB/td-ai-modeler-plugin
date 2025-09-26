"""AI Client for LLM-powered threat generation using STRIDE framework."""

import json
from typing import Dict, List
import litellm


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
    """Generate AI-powered threats for all in-scope components using STRIDE framework."""
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
        print(f"Generating threats with {model_name}")
        response = litellm.completion(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Generate threats for all elements in the model."}
            ],
            temperature=0.1
        )
        
        threats_data = json.loads(response.choices[0].message.content)
        
        # Validate and fix threat data structure
        for cell_id, threats in threats_data.items():
            for threat in threats:
                # Ensure all required fields exist with defaults
                if 'status' not in threat:
                    threat['status'] = 'Open'
                if 'type' not in threat:
                    threat['type'] = 'Unknown'
                if 'severity' not in threat:
                    threat['severity'] = 'Medium'
                if 'modelType' not in threat:
                    threat['modelType'] = 'STRIDE'
        
        return threats_data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response from AI: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error calling LLM: {str(e)}")
