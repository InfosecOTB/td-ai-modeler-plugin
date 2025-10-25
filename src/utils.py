"""Utility functions for file operations and threat model updates."""

import json
import uuid
import logging
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)


def load_json(path: Union[str, Path]) -> dict:
    """Load and parse a JSON file."""
    logger.info(f"Loading JSON from {path}")
    with open(str(path), 'r') as f:
        return json.load(f)


def update_threats_in_file(file_path: Union[str, Path], threats_data: dict) -> None:
    """Update threat model file with AI-generated threats and visual indicators."""
    logger.info(f"Updating threats in file: {file_path}")
    
    # Load existing threat model
    with open(str(file_path), 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updated_count = 0
    
    # Iterate through all diagrams and cells
    for diagram in data.get('detail', {}).get('diagrams', []):
        for cell in diagram.get('cells', []):
            cell_id = cell.get('id')
            
            # Skip if this cell doesn't have generated threats
            if cell_id in threats_data:
                # Skip out-of-scope components and trust boundaries
                if cell.get('data', {}).get('outOfScope') or cell.get('shape', '') in ['trust-boundary-box', 'trust-boundary-curve']:
                    continue
                
                # Ensure cell has data object
                if 'data' not in cell:
                    cell['data'] = {}
                
                # Add unique IDs to threats if missing
                threats_with_ids = []
                for threat in threats_data[cell_id]:
                    if 'id' not in threat:
                        threat['id'] = str(uuid.uuid4())
                    threats_with_ids.append(threat)
                
                # Update cell with new threats
                cell['data']['threats'] = threats_with_ids
                
                # Update hasOpenThreats flag based on threat status
                if 'hasOpenThreats' in cell['data']:
                    cell['data']['hasOpenThreats'] = any(
                        t.get('status', 'Open') == 'Open' for t in threats_data[cell_id]
                    )
                
                # Add visual indicator (red stroke) for cells with threats
                _add_red_stroke(cell)
                updated_count += 1
    
    # Save updated model back to file
    with open(str(file_path), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, separators=(',', ': '), ensure_ascii=False)
    
    logger.info(f"Updated {updated_count} cells with threats")


def _add_red_stroke(cell: dict) -> None:
    """Add red stroke visual indicator to threat-bearing cells (different shapes need different attributes)."""
    if 'attrs' not in cell:
        cell['attrs'] = {'stroke': 'red'}
        return
    
    attrs = cell['attrs']
    
    # Different cell shapes store stroke in different locations
    if 'line' in attrs:
        attrs['line']['stroke'] = 'red'
    elif 'body' in attrs:
        attrs['body']['stroke'] = 'red'
    elif 'topLine' in attrs:
        attrs['topLine']['stroke'] = 'red'
        if 'bottomLine' in attrs:
            attrs['bottomLine']['stroke'] = 'red'
    else:
        attrs['stroke'] = 'red'