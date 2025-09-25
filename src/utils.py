"""Utility functions for file operations and threat model processing."""

import json
import shutil


def load_json(path: str) -> dict:
    """Load and parse a JSON file."""
    print(f"Loading JSON from {path}")
    with open(path, 'r') as f:
        return json.load(f)


def copy_file(src: str, dest: str) -> None:
    """Copy a file from source to destination."""
    shutil.copy(src, dest)


def update_threats_in_file(file_path: str, threats_data: dict) -> None:
    """Update threat model with AI-generated threats while preserving formatting."""
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
                
                cell['data']['threats'] = threats_data[cell_id]
                
                # Update hasOpenThreats if it exists
                if 'hasOpenThreats' in cell['data']:
                    # Defensive programming: check if status field exists and default to 'Open' if missing
                    cell['data']['hasOpenThreats'] = any(t.get('status', 'Open') == 'Open' for t in threats_data[cell_id])
                
                # Change stroke color to red when threats are added
                if 'attrs' in cell and 'line' in cell['attrs']:
                    cell['attrs']['line']['stroke'] = 'red'
                elif 'attrs' in cell and 'body' in cell['attrs']:
                    cell['attrs']['body']['stroke'] = 'red'
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
