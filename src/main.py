"""
AI-Powered Threat Modeling Tool

Generates security threats for Threat Dragon models using LLMs.
"""

import os
from dotenv import load_dotenv
from utils import load_json, copy_file, update_threats_in_file
from ai_client import generate_threats
from validator import ThreatValidator


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
    
    print(f"Updated model saved to {output_model_path}")

    # Validate AI response (silent, non-blocking)
    validation_result = None
    try:
        print("Starting validation...")
        validator = ThreatValidator()
        print(f"Calling validate_ai_response with model: {input_model_filename}")
        
        # Convert threats_data to the format expected by validator
        ai_response_format = []
        for element_id, threats_list in threats_data.items():
            ai_response_format.append({
                'id': element_id,
                'threats': threats_list
            })
        
        validation_result = validator.validate_ai_response(model, ai_response_format, input_model_filename)
        print("Validation completed successfully")
        
        # Only print summary if there are issues, otherwise silent
        if not validation_result.is_valid or validation_result.validation_warnings:
            validator.print_validation_summary(validation_result)
    except Exception as e:
        # Validation errors should not stop the main process
        print(f"Validation completed with errors (see log): {str(e)}")
        import traceback
        traceback.print_exc()
        pass 
   
    # Return validation result for programmatic use (if available)
    return validation_result

if __name__ == "__main__":
    main()
