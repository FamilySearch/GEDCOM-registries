#!/usr/bin/env python3
"""
Fix all issues identified in PR #174 review
"""

import os
from pathlib import Path

def fix_file(filepath, fixes):
    """Apply fixes to a file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    for old, new in fixes:
        content = content.replace(old, new)
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    return True

def main():
    base_dir = Path('structure/extension')
    
    # Fix 1: Remove "standard tag" lines and fix array syntax
    files_to_fix = [
        '_ATTR.yaml',
        '_COLOR.yaml', 
        '_TAG.yaml',
        '_TAG_ref.yaml',
        '_VALUE.yaml'
    ]
    
    for filename in files_to_fix:
        filepath = base_dir / filename
        if filepath.exists():
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Remove standard tag lines
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if 'standard tag:' not in line:
                    new_lines.append(line)
            
            # Fix array syntax for extension tags
            content = '\n'.join(new_lines)
            content = content.replace('extension tags: _', 'extension tags:\n  - _')
            
            # Add blank line before ...
            content = content.replace('\n...', '\n\n...')
            
            # Remove double blank lines
            while '\n\n\n' in content:
                content = content.replace('\n\n\n', '\n\n')
            
            with open(filepath, 'w') as f:
                f.write(content)
            
            print(f"Fixed {filename}")
    
    # Fix 2: Update _TAG_ref.yaml URI and payload
    tag_ref_file = base_dir / '_TAG_ref.yaml'
    if tag_ref_file.exists():
        with open(tag_ref_file, 'r') as f:
            content = f.read()
        
        # Change URI to make it unique
        content = content.replace(
            'uri: https://github.com/glamberson/gedcom-tags/_TAG',
            'uri: https://github.com/glamberson/gedcom-tags/_TAG_ref'
        )
        
        # Fix payload format
        content = content.replace(
            'payload: https://gedcom.io/terms/v7/type-Pointer',
            'payload: "@<https://github.com/glamberson/gedcom-tags/_TAG>@"'
        )
        
        with open(tag_ref_file, 'w') as f:
            f.write(content)
        
        print("Fixed _TAG_ref.yaml URI and payload")
    
    # Fix 3: Remove extension-tags.yaml if it exists
    ext_file = Path('extension-tags.yaml')
    if ext_file.exists():
        os.remove(ext_file)
        print("Removed extension-tags.yaml")
    
    print("\n✅ All PR #174 issues fixed!")

if __name__ == "__main__":
    main()