"""Validation module for AI threat generation responses."""

import json
import os
from datetime import datetime
from typing import Dict, List, Set, Tuple
from models import AIThreatsResponseList, Threats


class ThreatValidationResult:
    """Result of threat validation process."""
    
    def __init__(self):
        self.is_valid: bool = True
        self.missing_elements: List[str] = []
        self.invalid_response_ids: List[str] = []
        self.validation_errors: List[str] = []
        self.validation_warnings: List[str] = []
        self.total_elements_in_scope: int = 0
        self.elements_with_threats: int = 0
        self.total_threats_generated: int = 0


class ThreatValidator:
    """Validates AI-generated threats against the original model."""
    
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        print(f"Validator initialized with output directory: {os.path.abspath(output_dir)}")
    
    def validate_ai_response(
        self, 
        original_model: dict, 
        ai_response: List[dict],
        model_filename: str
    ) -> ThreatValidationResult:
        """
        Validate AI response against the original model.
        
        Args:
            original_model: The original threat model JSON
            ai_response: List of AI-generated threat responses
            model_filename: Original model filename for logging
            
        Returns:
            ThreatValidationResult: Validation results
        """
        result = ThreatValidationResult()
        
        # Parse AI response using Pydantic models
        try:
            validated_response = AIThreatsResponseList(root=ai_response)
            ai_threats_data = {item.id: item.threats for item in validated_response.root}
        except Exception as e:
            result.is_valid = False
            result.validation_errors.append(f"Failed to parse AI response: {str(e)}")
            ai_threats_data = {}  # Create empty dict to avoid errors
        
        # Get all elements that should have threats (outOfScope = false)
        elements_in_scope = self._get_elements_in_scope(original_model)
        result.total_elements_in_scope = len(elements_in_scope)
        
        # Only perform validation if AI response parsing was successful
        if 'ai_threats_data' in locals():
            # Validation 1: Check if all in-scope elements have threats in response
            missing_elements = self._validate_missing_elements(
                elements_in_scope, ai_threats_data, result
            )
            
            # Validation 2: Check if all response IDs are valid element IDs
            invalid_ids = self._validate_response_ids(
                original_model, ai_threats_data, result
            )
        else:
            # If parsing failed, create empty dict to avoid errors
            ai_threats_data = {}
        
        # Count statistics
        result.elements_with_threats = len(ai_threats_data)
        result.total_threats_generated = sum(len(threats) for threats in ai_threats_data.values())
        
        # Determine overall validity - only invalid response IDs are actual errors
        result.is_valid = (
            len(result.invalid_response_ids) == 0 and
            len(result.validation_errors) == 0
        )
        
        # Write validation log
        self._write_validation_log(result, model_filename, ai_response)
        
        return result
    
    def _get_elements_in_scope(self, model: dict) -> Dict[str, dict]:
        """
        Extract all elements that have outOfScope = false.
        
        Args:
            model: The threat model JSON
            
        Returns:
            Dict mapping element IDs to their data objects
        """
        elements_in_scope = {}
        
        for diagram in model.get('detail', {}).get('diagrams', []):
            for cell in diagram.get('cells', []):
                cell_id = cell.get('id')
                cell_data = cell.get('data', {})
                
                # Check if element is in scope (outOfScope is false or not set)
                out_of_scope = cell_data.get('outOfScope', False)
                cell_shape = cell.get('shape', '')
                
                # Skip trust boundary boxes from validation
                if not out_of_scope and cell_id and cell_shape != 'trust-boundary-box':
                    elements_in_scope[cell_id] = cell_data
        
        return elements_in_scope
    
    def _validate_missing_elements(
        self, 
        elements_in_scope: Dict[str, dict], 
        ai_threats_data: Dict[str, List[Threats]], 
        result: ThreatValidationResult
    ) -> List[str]:
        """
        Check if all in-scope elements have threats in the AI response.
        
        Args:
            elements_in_scope: Elements that should have threats
            ai_threats_data: AI-generated threats data
            result: Validation result object to update
            
        Returns:
            List of missing element IDs
        """
        missing_elements = []
        
        for element_id, element_data in elements_in_scope.items():
            if element_id not in ai_threats_data:
                missing_elements.append(element_id)
                result.missing_elements.append(element_id)
                result.validation_warnings.append(
                    f"Element '{element_id}' (name: '{element_data.get('name', 'Unknown')}') "
                    f"is in scope but missing from AI response"
                )
            else:
                # Check if threats have required fields
                threats = ai_threats_data[element_id]
                for i, threat in enumerate(threats):
                    if not threat.mitigation or threat.mitigation.strip() == "":
                        result.validation_warnings.append(
                            f"Element '{element_id}' threat {i+1} has empty mitigation"
                        )
        
        return missing_elements
    
    def _validate_response_ids(
        self, 
        model: dict, 
        ai_threats_data: Dict[str, List[Threats]], 
        result: ThreatValidationResult
    ) -> List[str]:
        """
        Check if all response IDs correspond to valid elements with threats structure.
        
        Args:
            model: The original threat model
            ai_threats_data: AI-generated threats data
            result: Validation result object to update
            
        Returns:
            List of invalid response IDs
        """
        invalid_ids = []
        valid_element_ids = set()
        
        # Collect all valid element IDs from the model
        for diagram in model.get('detail', {}).get('diagrams', []):
            for cell in diagram.get('cells', []):
                cell_id = cell.get('id')
                if cell_id:
                    valid_element_ids.add(cell_id)
        
        # Check each response ID
        for response_id in ai_threats_data.keys():
            if response_id not in valid_element_ids:
                invalid_ids.append(response_id)
                result.invalid_response_ids.append(response_id)
                result.validation_errors.append(
                    f"Response ID '{response_id}' does not correspond to any valid element in the model"
                )
        
        return invalid_ids
    
    def _write_validation_log(
        self, 
        result: ThreatValidationResult, 
        model_filename: str, 
        ai_response: List[dict]
    ) -> None:
        """
        Write detailed validation log with timestamp.
        
        Args:
            result: Validation result
            model_filename: Original model filename
            ai_response: Raw AI response for reference
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"validation_log_{model_filename.replace('.json', '')}_{timestamp}.log"
        log_path = os.path.join(self.output_dir, log_filename)
        
        # Create text log content
        coverage_pct = (result.elements_with_threats / result.total_elements_in_scope * 100) if result.total_elements_in_scope > 0 else 0
        
        log_content = f"""THREAT VALIDATION LOG
{'='*60}
Timestamp: {timestamp}
Model File: {model_filename}

VALIDATION NOTES:
- Trust boundary boxes are excluded from validation
- Missing elements are warnings, not errors
- Only invalid response IDs are validation errors

VALIDATION SUMMARY:
Overall Status: {'✅ VALID' if result.is_valid else '❌ INVALID'}
Elements in Scope: {result.total_elements_in_scope}
Elements with Threats: {result.elements_with_threats}
Total Threats Generated: {result.total_threats_generated}
Coverage: {coverage_pct:.1f}%

VALIDATION RESULTS:
"""

        if result.validation_errors:
            log_content += f"\n❌ VALIDATION ERRORS ({len(result.validation_errors)}):\n"
            for error in result.validation_errors:
                log_content += f"  • {error}\n"

        if result.validation_warnings:
            log_content += f"\n⚠️  WARNINGS ({len(result.validation_warnings)}):\n"
            for warning in result.validation_warnings:
                log_content += f"  • {warning}\n"

        if result.missing_elements:
            log_content += f"\n📋 MISSING ELEMENTS ({len(result.missing_elements)}):\n"
            for element_id in result.missing_elements:
                log_content += f"  • {element_id}\n"

        if result.invalid_response_ids:
            log_content += f"\n🔍 INVALID RESPONSE IDs ({len(result.invalid_response_ids)}):\n"
            for response_id in result.invalid_response_ids:
                log_content += f"  • {response_id}\n"

        log_content += f"\nAI RESPONSE PREVIEW:\n"
        log_content += f"Total Responses: {len(ai_response)}\n"
        log_content += f"Response IDs: {list({item.get('id') for item in ai_response if 'id' in item})}\n"
        
        if ai_response:
            log_content += f"\nSample Response:\n"
            log_content += f"ID: {ai_response[0].get('id', 'N/A')}\n"
            log_content += f"Threats Count: {len(ai_response[0].get('threats', []))}\n"

        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(log_content)
            print(f"Validation log saved to: {log_path}")
        except Exception as e:
            print(f"Failed to save validation log: {str(e)}")
            pass
    
    def print_validation_summary(self, result: ThreatValidationResult) -> None:
        """Print a human-readable validation summary."""
        print("\n" + "="*60)
        print("THREAT VALIDATION SUMMARY")
        print("="*60)
        print("Note: Trust boundary boxes are excluded from validation")
        print("Note: Missing elements are warnings, not errors")
        
        print(f"Overall Status: {'✅ VALID' if result.is_valid else '❌ INVALID'}")
        print(f"Elements in Scope: {result.total_elements_in_scope}")
        print(f"Elements with Threats: {result.elements_with_threats}")
        coverage_pct = (result.elements_with_threats / result.total_elements_in_scope * 100) if result.total_elements_in_scope > 0 else 0
        print(f"Coverage: {coverage_pct:.1f}%")
        print(f"Total Threats Generated: {result.total_threats_generated}")
        
        if result.validation_errors:
            print(f"\n❌ VALIDATION ERRORS ({len(result.validation_errors)}):")
            for error in result.validation_errors:
                print(f"  • {error}")
        
        if result.validation_warnings:
            print(f"\n⚠️  WARNINGS ({len(result.validation_warnings)}):")
            for warning in result.validation_warnings:
                print(f"  • {warning}")
        
        if result.missing_elements:
            print(f"\n📋 MISSING ELEMENTS ({len(result.missing_elements)}):")
            for element_id in result.missing_elements:
                print(f"  • {element_id}")
        
        if result.invalid_response_ids:
            print(f"\n🔍 INVALID RESPONSE IDs ({len(result.invalid_response_ids)}):")
            for response_id in result.invalid_response_ids:
                print(f"  • {response_id}")
        
        print("="*60)
