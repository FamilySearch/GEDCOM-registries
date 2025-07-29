#!/usr/bin/env python3
import yaml
import sys
import os

def fix_yaml_file(filepath):
    """Fix YAML file formatting issues"""
    with open(filepath, 'r') as f:
        content = yaml.safe_load(f)
    
    # Fix extension tags to be an array if it's a string
    if 'extension tags' in content and isinstance(content['extension tags'], str):
        content['extension tags'] = [content['extension tags']]
    
    # Ensure specification items are properly formatted
    if 'specification' in content and isinstance(content['specification'], list):
        # Already a list, good
        pass
    
    # Reorder keys to match standard format
    ordered_keys = [
        'lang', 'type', 'uri', 'standard tag', 'extension tags', 
        'specification', 'label', 'payload', 'enumeration values',
        'substructures', 'superstructures', 'contact'
    ]
    
    ordered_content = {}
    # First add keys in the preferred order
    for key in ordered_keys:
        if key in content:
            ordered_content[key] = content[key]
    
    # Then add any remaining keys
    for key in content:
        if key not in ordered_content:
            ordered_content[key] = content[key]
    
    # Write back with proper formatting
    with open(filepath, 'w') as f:
        f.write('%YAML 1.2\n---\n')
        
        for i, (key, value) in enumerate(ordered_content.items()):
            if i > 0 and key in ['type', 'uri', 'extension tags', 'specification', 
                                 'label', 'payload', 'substructures', 'superstructures']:
                f.write('\n')
            
            if key == 'specification' and isinstance(value, list) and len(value) > 1:
                f.write(f'{key}:\n')
                f.write(f'  - {value[0]}\n')
                f.write('  - |\n')
                # Split long descriptions into lines
                desc_lines = value[1].strip().split('\n')
                for line in desc_lines:
                    f.write(f'    {line}\n')
            elif isinstance(value, list):
                f.write(f'{key}:\n')
                for item in value:
                    f.write(f'  - "{item}"\n' if key == 'enumeration values' else f'  - {item}\n')
            elif isinstance(value, dict):
                f.write(f'{key}:\n')
                for k, v in value.items():
                    f.write(f'  "{k}": "{v}"\n')
            elif value is None:
                f.write(f'{key}: null\n')
            elif key == 'payload' and '@' in str(value):
                # Quote payloads that contain @ symbols
                f.write(f'{key}: "{value}"\n')
            elif key == 'superstructures' and value is None:
                # Empty superstructures should be {}
                f.write(f'{key}: {{}}\n')
            else:
                f.write(f'{key}: {value}\n')
        
        f.write('...\n')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: fix_yaml_format.py <yaml_file> [...]")
        sys.exit(1)
    
    for filepath in sys.argv[1:]:
        print(f"Fixing {filepath}")
        try:
            fix_yaml_file(filepath)
            print(f"  ✓ Fixed")
        except Exception as e:
            print(f"  ✗ Error: {e}")