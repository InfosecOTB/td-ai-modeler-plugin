"""
AI-Powered Threat Modeling Tool

Generates security threats for Threat Dragon models using LLMs and STRIDE framework.
"""

import os
from dotenv import load_dotenv
from utils import load_json, copy_file, update_threats_in_file
from ai_client import generate_threats
from models import ThreatDragonModel


def main():
    """Main entry point for threat modeling application."""
    load_dotenv()
    
    llm_model_name = os.getenv('LLM_MODEL_NAME')
    input_schema_filename = os.getenv('INPUT_THREAT_SCHEMA_JSON')
    input_model_filename = os.getenv('INPUT_THREAT_MODEL_JSON')
    
    if not all([llm_model_name, input_schema_filename, input_model_filename]):
        raise ValueError("Missing required environment variables: LLM_MODEL_NAME, INPUT_THREAT_SCHEMA_JSON, INPUT_THREAT_MODEL_JSON")
    
    input_schema_path = f'./input/{input_schema_filename}'
    input_model_path = f'./input/{input_model_filename}'
    output_model_path = f'./output/{input_model_filename}'
    
    schema = load_json(input_schema_path)
    model = load_json(input_model_path)
    
    # Copy model to output
    copy_file(input_model_path, output_model_path)
    
    # Generate threats
    threats_data = generate_threats(schema, model, llm_model_name)
    
    # Update only the threats in the output file, preserving original formatting
    update_threats_in_file(output_model_path, threats_data)
    
    # Validate the updated model by loading it back
    try:
        updated_model = load_json(output_model_path)
        validated_model = ThreatDragonModel(**updated_model)
        print(f"Updated and validated model saved to {output_model_path}")
    except Exception as e:
        raise ValueError(f"Validation failed: {str(e)}")

if __name__ == "__main__":
    main()
