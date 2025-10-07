"""
This file will

1. Load the git submodule for GEDCOM
2. Pull any changes to GEDCOM's main
3. Check the extracted_files/tags/* against current YAML
4. Update any that differ
5. Clone/checkout GEDCOM v7.1 branch and process v7.1 files

FIX ME: does not currently handle `type: uri` at all
"""

import yaml
from glob import glob
from subprocess import run
import os.path
import filecmp
import shutil
import sys

os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

run(['git','submodule','init'])
run(['git','submodule','update'])

os.chdir('GEDCOM')
run(['git','pull','origin','main'])
os.chdir('..')


for src in glob(os.path.join('GEDCOM','extracted-files','tags','*')):
    data = yaml.safe_load(open(src))
    if data['type'] == 'uri':
        continue
    tag = os.path.basename(src).replace(' ','-')
    dst = os.path.join('..',data['type'].replace(' ','-'),'standard',tag+'.yaml')
    if os.path.exists(dst) and filecmp.cmp(dst, src):
        continue
    print('update',dst,'with',src)
    shutil.copyfile(src,dst)


# Process v7.1 files
if not os.path.exists('GEDCOM-v7.1'):
    # Clone the GEDCOM repo for v7.1
    run(['git','clone','https://github.com/FamilySearch/GEDCOM','GEDCOM-v7.1'])

os.chdir('GEDCOM-v7.1')
run(['git','fetch','origin','v7.1'])
run(['git','checkout','v7.1'])
run(['git','pull','origin','v7.1'])
os.chdir('..')

for src in glob(os.path.join('GEDCOM-v7.1','extracted-files','tags','*')):
    with open(src, 'r') as f:
        raw_text = f.read()
    data = yaml.safe_load(raw_text)
    
    if data['type'] == 'uri':
        continue
    
    # Only process files with v7.1 URIs
    if '/v7.1/' not in data['uri']:
        continue
    
    tag = os.path.basename(src).replace(' ','-')
    dst = os.path.join('..',data['type'].replace(' ','-'),'standard',tag+'-v71.yaml')
    
    # Check if we need to union superstructures from subsumed file
    needs_modification = False
    if 'subsumes' in data and data['subsumes']:
        subsumed_uri = data['subsumes']
        # Find the file with the subsumed URI
        subsumed_file = None
        for existing_file in glob(os.path.join('..',data['type'].replace(' ','-'),'standard','*.yaml')):
            existing_data = yaml.safe_load(open(existing_file))
            if existing_data.get('uri') == subsumed_uri:
                subsumed_file = existing_file
                break
        
        if subsumed_file:
            existing_data = yaml.safe_load(open(subsumed_file))
            existing_superstructures = existing_data.get('superstructures', {})
            
            # Union the superstructures - only if the existing file has non-empty superstructures
            if existing_superstructures:
                needs_modification = True
                v71_superstructures = data.get('superstructures', {})
                merged_superstructures = dict(v71_superstructures)
                merged_superstructures.update(existing_superstructures)
                data['superstructures'] = merged_superstructures
    
    # Write the file
    if needs_modification:
        # Need to dump YAML with proper formatting
        output_lines = []
        output_lines.append('%YAML 1.2')
        output_lines.append('---')
        
        # Manually format to match source style
        for key in ['lang', 'type', 'uri', 'standard tag', 'specification', 'label', 'payload', 
                    'substructures', 'superstructures', 'prerelease', 'subsumes', 'contact']:
            if key in data:
                output_lines.append('')  # blank line before each major key
                if key == 'specification':
                    output_lines.append('specification:')
                    for item in data[key]:
                        if '\n' in item:
                            output_lines.append('  - |')
                            for line in item.split('\n'):
                                output_lines.append('    ' + line)
                        else:
                            output_lines.append(f'  - {item}')
                elif key == 'substructures' or key == 'superstructures':
                    structures = data[key]
                    if structures:
                        output_lines.append(f'{key}:')
                        for uri, cardinality in sorted(structures.items()):
                            output_lines.append(f'  "{uri}": "{cardinality}"')
                    else:
                        output_lines.append(f'{key}: {{}}')
                elif key == 'payload':
                    if data[key] is None:
                        output_lines.append('payload: null')
                    else:
                        output_lines.append(f'payload: {data[key]}')
                elif key == 'prerelease':
                    output_lines.append(f'prerelease: {str(data[key]).lower()}')
                else:
                    val = data[key]
                    if isinstance(val, str) and (' ' in val or ':' in val):
                        output_lines.append(f"{key}: '{val}'")
                    else:
                        output_lines.append(f'{key}: {val}')
        
        output_lines.append('...')
        output_lines.append('')  # final newline
        
        with open(dst, 'w') as f:
            f.write('\n'.join(output_lines))
    else:
        # Just copy as-is to preserve exact formatting
        with open(dst, 'w') as f:
            f.write(raw_text)
    
    print('created/updated',dst,'with',src)
    
        
