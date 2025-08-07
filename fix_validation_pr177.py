#!/usr/bin/env python3
"""
Fix validation errors in PR #177
"""

import os
from pathlib import Path

def fix_file(filepath):
    """Fix YAML file issues."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix bracket spacing: [ _TAG ] -> [_TAG]
    content = content.replace('[ ', '[')
    content = content.replace(' ]', ']')
    
    # Ensure file ends with newline
    if not content.endswith('\n'):
        content += '\n'
    
    with open(filepath, 'w') as f:
        f.write(content)

def main():
    # Files that need fixing based on validation errors
    files_to_fix = [
        'structure/extension/_VALUE.yaml',
        'structure/extension/_PART.yaml',
        'enumeration/extension/enum-Present.yaml', 
        'enumeration/extension/enum-Absent.yaml',
        'enumeration/extension/enum-Unknown.yaml',
        'enumeration-set/extension/enumset-Presence.yaml'
    ]
    
    for filepath in files_to_fix:
        path = Path(filepath)
        if path.exists():
            fix_file(path)
            print(f"Fixed {filepath}")
        else:
            print(f"Warning: {filepath} not found")
    
    print("\n✅ Validation fixes complete!")

if __name__ == "__main__":
    main()