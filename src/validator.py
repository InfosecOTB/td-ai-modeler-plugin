"""Simplified validation module for AI threat generation responses."""

import os
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Simple validation result."""
    is_valid: bool
    missing_elements: List[str]
    invalid_ids: List[str]
    warnings: List[str]
    stats: Dict[str, int]


class ThreatValidator:
    """Simplified threat validator."""
    
    def __init__(self, output_dir: str = "./output/logs"):
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir
    
    def validate_ai_response(self, model: dict, ai_response: List[dict], filename: str) -> ValidationResult:
        """Validate AI response against the original model."""
        # Get elements that should have threats (in scope, not trust boundaries)
        in_scope_elements = self._get_in_scope_elements(model)
        ai_element_ids = {item['id'] for item in ai_response}
        
        # Find missing and invalid elements
        missing = [elem_id for elem_id in in_scope_elements if elem_id not in ai_element_ids]
        invalid = [elem_id for elem_id in ai_element_ids if elem_id not in in_scope_elements]
        
        # Check for empty mitigations
        warnings = []
        for item in ai_response:
            for i, threat in enumerate(item.get('threats', [])):
                if not threat.get('mitigation', '').strip():
                    warnings.append(f"Element {item['id']} threat {i+1} has empty mitigation")
        
        # Calculate stats
        total_threats = sum(len(item.get('threats', [])) for item in ai_response)
        coverage = (len(ai_element_ids) / len(in_scope_elements) * 100) if in_scope_elements else 0
        
        result = ValidationResult(
            is_valid=len(invalid) == 0,  # Only invalid IDs are errors
            missing_elements=missing,
            invalid_ids=invalid,
            warnings=warnings,
            stats={
                'in_scope_elements': len(in_scope_elements),
                'elements_with_threats': len(ai_element_ids),
                'total_threats': total_threats,
                'coverage_percent': round(coverage, 1)
            }
        )
        
        self._write_log(result, filename, ai_response)
        return result
    
    def _get_in_scope_elements(self, model: dict) -> List[str]:
        """Get element IDs that should have threats."""
        elements = []
        for diagram in model.get('detail', {}).get('diagrams', []):
            for cell in diagram.get('cells', []):
                cell_id = cell.get('id')
                cell_data = cell.get('data', {})
                cell_shape = cell.get('shape', '')
                
                # Include if: in scope, not trust boundary, has ID
                if (cell_id and 
                    not cell_data.get('outOfScope', False) and 
                    cell_shape not in ['trust-boundary-box', 'trust-boundary-curve']):
                    elements.append(cell_id)
        
        return elements
    
    def _write_log(self, result: ValidationResult, filename: str, ai_response: List[dict]):
        """Write validation log."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(self.output_dir, f"validation_log_{filename.replace('.json', '')}_{timestamp}.log")
        
        content = f"""THREAT VALIDATION LOG
{'='*60}
Timestamp: {timestamp}
Model File: {filename}

VALIDATION NOTES:
- Trust boundary boxes and curves are excluded from validation
- Missing elements are warnings, not errors
- Only invalid response IDs are validation errors

VALIDATION SUMMARY:
Overall Status: {'✅ VALID' if result.is_valid else '❌ INVALID'}
Elements in Scope: {result.stats['in_scope_elements']}
Elements with Threats: {result.stats['elements_with_threats']}
Total Threats Generated: {result.stats['total_threats']}
Coverage: {result.stats['coverage_percent']}%

VALIDATION RESULTS:
"""
        
        if result.invalid_ids:
            content += f"\n❌ VALIDATION ERRORS ({len(result.invalid_ids)}):\n"
            for elem_id in result.invalid_ids:
                content += f"  • {elem_id}\n"
        
        if result.warnings:
            content += f"\n⚠️  WARNINGS ({len(result.warnings)}):\n"
            for warning in result.warnings:
                content += f"  • {warning}\n"
        
        if result.missing_elements:
            content += f"\n📋 MISSING ELEMENTS ({len(result.missing_elements)}):\n"
            for elem_id in result.missing_elements:
                content += f"  • {elem_id}\n"
        
        content += f"\nAI RESPONSE PREVIEW:\n"
        content += f"Total Responses: {len(ai_response)}\n"
        content += f"Response IDs: {[item.get('id') for item in ai_response]}\n"
        
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Validation log saved to: {log_path}")
        except Exception as e:
            print(f"Failed to save validation log: {str(e)}")
    
    def print_summary(self, result: ValidationResult):
        """Print validation summary."""
        print("\n" + "="*60)
        print("THREAT VALIDATION SUMMARY")
        print("="*60)
        print("Note: Trust boundary boxes and curves are excluded from validation")
        print("Note: Missing elements are warnings, not errors")
        
        print(f"Overall Status: {'✅ VALID' if result.is_valid else '❌ INVALID'}")
        print(f"Elements in Scope: {result.stats['in_scope_elements']}")
        print(f"Elements with Threats: {result.stats['elements_with_threats']}")
        print(f"Coverage: {result.stats['coverage_percent']}%")
        print(f"Total Threats Generated: {result.stats['total_threats']}")
        
        if result.invalid_ids:
            print(f"\n❌ VALIDATION ERRORS ({len(result.invalid_ids)}):")
            for elem_id in result.invalid_ids:
                print(f"  • {elem_id}")
        
        if result.warnings:
            print(f"\n⚠️  WARNINGS ({len(result.warnings)}):")
            for warning in result.warnings:
                print(f"  • {warning}")
        
        if result.missing_elements:
            print(f"\n📋 MISSING ELEMENTS ({len(result.missing_elements)}):")
            for elem_id in result.missing_elements:
                print(f"  • {elem_id}")
        
        print("="*60)