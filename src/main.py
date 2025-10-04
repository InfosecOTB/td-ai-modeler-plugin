"""Simplified AI-Powered Threat Modeling Tool."""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from utils import load_json, copy_file, update_threats_in_file
from ai_client import generate_threats
from validator import ThreatValidator


def setup_logging():
    """Setup logging for the application."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = f"./output/logs/threat_modeling_{timestamp}.log"
    os.makedirs("./output/logs", exist_ok=True)

    # ---- Application logger (NOT root) ----
    logger = logging.getLogger("threat_modeling")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False            # <--- don't pass to root

    # remove any existing handlers if re-running
    logger.handlers.clear()

    # File handler: full detail
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    file_handler.setFormatter(file_fmt)
    logger.addHandler(file_handler)

    # Console handler: brief info+
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    return logger




def main():
    """Main entry point for threat modeling application."""
    logger = setup_logging()
    
    logger.info("="*60)
    logger.info("STARTING AI-POWERED THREAT MODELING TOOL")
    logger.info("="*60)
    
    # Load configuration
    load_dotenv()
    llm_model = os.getenv('LLM_MODEL_NAME')
    schema_file = os.getenv('INPUT_THREAT_SCHEMA_JSON')
    model_file = os.getenv('INPUT_THREAT_MODEL_JSON')
    
    logger.info(f"Configuration: {llm_model}, {schema_file}, {model_file}")
    
    if not all([llm_model, schema_file, model_file]):
        raise ValueError("Missing required environment variables")
    
    # Setup file paths
    schema_path = f'./input/{schema_file}'
    input_path = f'./input/{model_file}'
    output_path = f'./output/{model_file}'
    
    # Load files
    logger.info("Loading files...")
    schema = load_json(schema_path)
    model = load_json(input_path)
    
    # Copy model to output
    copy_file(input_path, output_path)
    
    # Generate threats
    logger.info("Generating threats...")
    threats_data = generate_threats(schema, model, llm_model)
    
    # Log detailed AI response
    logger.debug("AI Response Details:")
    for elem_id, threats in threats_data.items():
        logger.debug(f"  Element {elem_id}: {len(threats)} threats")
        for i, threat in enumerate(threats):
            logger.debug(f"    Threat {i+1}: {threat.get('title', 'No title')} ({threat.get('severity', 'Unknown severity')}) - {threat.get('status', 'Unknown status')}")
    
    # Update model with threats
    update_threats_in_file(output_path, threats_data)
    logger.info(f"Updated model saved to {output_path}")
    
    # Validate response
    validation_result = None
    try:
        logger.info("Validating AI response...")
        validator = ThreatValidator()
        
        # Convert threats to validator format
        ai_response_format = [
            {'id': elem_id, 'threats': threats} 
            for elem_id, threats in threats_data.items()
        ]
        
        validation_result = validator.validate_ai_response(model, ai_response_format, model_file)
        
        # Always print validation summary
        validator.print_summary(validation_result)
            
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
    
    logger.info("="*60)
    logger.info("THREAT MODELING PROCESS COMPLETED")
    logger.info("="*60)
    
    return validation_result


if __name__ == "__main__":
    main()