"""Utility functions for file operations and threat model updates."""

import json
import shutil
import uuid


def load_json(path: str) -> dict:
    """Load and parse a JSON file."""
    print(f"Loading JSON from {path}")
    with open(path, 'r') as f:
        return json.load(f)


def copy_file(src: str, dest: str) -> None:
    """Copy a file from source to destination."""
    shutil.copy(src, dest)


def update_threats_in_file(file_path: str, threats_data: dict) -> None:
    """Update threat model with AI-generated threats and visual indicators."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse the JSON to get the structure
    data = json.loads(content)
    
    # Update threats in the data structure
    for diagram in data.get('detail', {}).get('diagrams', []):
        for cell in diagram.get('cells', []):
            cell_id = cell.get('id')
            if cell_id and cell_id in threats_data:
                # Check if component is out of scope - skip if outOfScope is true
                if 'data' in cell and 'outOfScope' in cell['data'] and cell['data']['outOfScope'] == True:
                    print(f"Skipping component {cell_id} - outOfScope is true")
                    continue
                
                # Place threats inside the data object, not at cell level
                if 'data' not in cell:
                    cell['data'] = {}
                
                # Generate UUIDs for threats that don't have them
                threats_with_uuids = []
                for threat in threats_data[cell_id]:
                    if 'id' not in threat or not threat['id']:
                        threat['id'] = str(uuid.uuid4())
                    threats_with_uuids.append(threat)
                
                cell['data']['threats'] = threats_with_uuids
                
                # Update hasOpenThreats if it exists
                if 'hasOpenThreats' in cell['data']:
                    # Defensive programming: check if status field exists and default to 'Open' if missing
                    cell['data']['hasOpenThreats'] = any(t.get('status', 'Open') == 'Open' for t in threats_data[cell_id])
                
                # Change stroke color to red when threats are added
                if 'attrs' in cell and 'line' in cell['attrs']:
                    cell['attrs']['line']['stroke'] = 'red'
                elif 'attrs' in cell and 'body' in cell['attrs']:
                    cell['attrs']['body']['stroke'] = 'red'
                elif 'attrs' in cell and 'topLine' in cell['attrs']:
                    # Handle store shape with topLine and bottomLine
                    cell['attrs']['topLine']['stroke'] = 'red'
                    if 'bottomLine' in cell['attrs']:
                        cell['attrs']['bottomLine']['stroke'] = 'red'
                elif 'attrs' in cell:
                    # If attrs exists but doesn't have line or body, add stroke to the main attrs
                    if 'stroke' not in cell['attrs']:
                        cell['attrs']['stroke'] = 'red'
                else:
                    # If no attrs object exists, create one with red stroke
                    cell['attrs'] = {'stroke': 'red'}
    
    # Save back with minimal formatting changes
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, separators=(',', ': '), ensure_ascii=False)
