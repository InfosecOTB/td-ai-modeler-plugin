"""AI-Powered Threat Modeling Tool - Generate threats for Threat Dragon models using LLMs."""

import os
import logging
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from utils import load_json, update_threats_in_file, handle_user_friendly_error
from ai_client import generate_threats
from validator import ThreatValidator

# Project directory structure
PROJECT_ROOT = Path(__file__).parent.parent
SCHEMA_DIR = PROJECT_ROOT / "schema"
LOGS_DIR = PROJECT_ROOT / "logs"

# Load environment variables and configuration
load_dotenv(override=True)
api_key = os.getenv('API_KEY')
schema_file = "owasp.threat-dragon.schema.V2.json"


def parse_arguments():
    """Parse and validate command-line arguments."""
    parser = argparse.ArgumentParser(
        description='AI-Powered Threat Modeling Tool - Generate threats for Threat Dragon models using LLMs'
    )
    
    parser.add_argument(
        '--llm-model',
        type=str,
        required=True,
        help='LLM model identifier (e.g., "openai/gpt-5", "anthropic/claude-sonnet-4-5-20250929")'
    )
    
    parser.add_argument(
        '--model-file',
        type=str,
        required=True,
        help='Input threat model JSON file path (full path including filename)'
    )
    
    parser.add_argument(
        '--temperature',
        type=float,
        default=0.1,
        help='LLM temperature for randomness (default: 0.1, range: 0-2)'
    )
    
    parser.add_argument(
        '--response-format',
        action='store_true',
        help='Enable structured JSON response format (default: False)'
    )
    
    parser.add_argument(
        '--api-base',
        type=str,
        help='Custom API base URL (default: None)'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['INFO', 'DEBUG'],
        help='Logging level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Validate temperature range
    if not (0 <= args.temperature <= 2):
        error_msg = handle_user_friendly_error(ValueError(f"Temperature {args.temperature} is out of range"), "temperature", None)
        print(error_msg)
        raise SystemExit(1)
    
    return args


def setup_logging(log_level: str = 'INFO'):
    """Configure logging with both file and console handlers."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOGS_DIR / f"threat_modeling_{timestamp}.log"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Create logger instance (not root logger to avoid conflicts)
    logger = logging.getLogger("threat_modeling")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.handlers.clear()

    # File handler: only enabled in DEBUG mode for detailed logs
    if log_level.upper() == 'DEBUG':
        file_handler = logging.FileHandler(str(log_path), encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        file_handler.setFormatter(file_fmt)
        logger.addHandler(file_handler)

    # Console handler: always enabled for INFO+ messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    return logger


def main():
    """Main application entry point."""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Initialize logging system
    logger = setup_logging(args.log_level)
    
    logger.info("="*60)
    logger.info("STARTING AI-POWERED THREAT MODELING TOOL")
    logger.info("="*60)
    
    # Display configuration
    logger.info("Configuration:")
    logger.info(f"  LLM Model: {args.llm_model}")
    logger.info(f"  Model File: {args.model_file}")
    logger.info(f"  Temperature: {args.temperature}")
    logger.info(f"  Response Format: {args.response_format}")
    logger.info(f"  API Base: {args.api_base if args.api_base else 'None'}")
    logger.info(f"  Log Level: {args.log_level}")
    
    # Validate file paths
    schema_path = SCHEMA_DIR / schema_file
    model_file_path = Path(args.model_file)
    
    if not schema_path.exists():
        error_msg = handle_user_friendly_error(FileNotFoundError(f"Schema file not found: {schema_path}"), "model_file", logger)
        logger.error(error_msg)
        raise SystemExit(1)
    if not model_file_path.exists():
        error_msg = handle_user_friendly_error(FileNotFoundError(f"Input file not found: {model_file_path}"), "model_file", logger)
        logger.error(error_msg)
        raise SystemExit(1)
    
    # Load threat model and schema
    logger.info("Loading files...")
    try:
        schema = load_json(schema_path)
        model = load_json(model_file_path)
    except Exception as e:
        error_msg = handle_user_friendly_error(e, "model_file", logger)
        logger.error(error_msg)
        raise SystemExit(1)
    
    # Generate threats using AI
    logger.info("Generating threats...")
    try:
        threats_data = generate_threats(schema, model, args.llm_model, api_key, args.temperature, args.response_format, args.api_base)
    except Exception as e:
        # Determine error type based on the exception
        error_str = str(e).lower()

        if "litellm.AuthenticationError".lower() in error_str:
            error_type = "api_key"
        elif "litellm.NotFoundError".lower() in error_str or "litellm.BadRequestError".lower() in error_str:
            error_type = "llm_model"
        elif "temperature" in error_str:
            error_type = "temperature"
        elif "litellm.InternalServerError".lower() in error_str:
            error_type = "api_base"
        elif "litellm.JSONSchemaValidationError".lower() in error_str:
            error_type = "response_format"
        else:
            error_type = "unknown"
 
        
        error_msg = handle_user_friendly_error(e, error_type, logger)
        logger.error(error_msg)
        raise SystemExit(1)
    
    # Log detailed threat information (DEBUG only)
    logger.debug("AI Response Details:")
    for elem_id, threats in threats_data.items():
        logger.debug(f"  Element {elem_id}: {len(threats)} threats")
        for i, threat in enumerate(threats):
            logger.debug(f"    Threat {i+1}: {threat.get('title', 'No title')} ({threat.get('severity', 'Unknown severity')}) - {threat.get('status', 'Unknown status')}")
    
    # Update threat model file with generated threats
    update_threats_in_file(model_file_path, threats_data)
    logger.info(f"Updated model saved to {model_file_path}")
    
    # Validate AI response quality
    validation_result = None
    try:
        logger.info("Validating AI response...")
        validator = ThreatValidator(log_level=args.log_level)
        
        # Convert threats data to validation format
        ai_response_format = [
            {'id': elem_id, 'threats': threats} 
            for elem_id, threats in threats_data.items()
        ]
        
        validation_result = validator.validate_ai_response(model, ai_response_format, args.model_file)
        validator.print_summary(validation_result)
            
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
    
    logger.info("="*60)
    logger.info("THREAT MODELING PROCESS COMPLETED")
    logger.info("="*60)
    
    return validation_result


if __name__ == "__main__":
    main()