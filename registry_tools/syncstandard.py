"""
This file will

1. Load the git submodule for GEDCOM
2. Pull any changes to GEDCOM's main
3. Check the extracted_files/tags/* against current YAML
4. Update any that differ

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
    print('loading',src,'...')
    with open(src) as f:
        data = yaml.safe_load(f)
    if data['type'] == 'uri':
        continue
    tag = os.path.basename(src).replace(' ','-')
    dst = os.path.join('..',data['type'].replace(' ','-'),'standard',tag+'.yaml')
    if os.path.exists(dst) and filecmp.cmp(dst, src):
        continue
    print('update',dst,'with',src)
    shutil.copyfile(src,dst)
    
        
os.chdir('GEDCOM-v7.1')
run(['git','checkout','v7.1'])
run(['git','pull','origin','v7.1'])
os.chdir('..')


for src in glob(os.path.join('GEDCOM-v7.1','extracted-files','tags','*')):
    print('loading',src,'...')
    with open(src) as f:
        data = yaml.safe_load(f)
    if data['type'] == 'uri':
        continue
    tag = os.path.basename(src).replace(' ','-')
    dst = os.path.join('..', data['type'].replace(' ', '-'), 'standard', tag + '.yaml')

    if '/v7.1/' in data.get('uri', ''):
        base_tag = tag
        base_dst = dst

        tag += '-v71'
        dst = os.path.join('..', data['type'].replace(' ', '-'), 'standard', tag + '.yaml')

        # If base file exists, merge superstructures
        if os.path.exists(base_dst):
            with open(base_dst) as f:
                base_data = yaml.safe_load(f)
            merged = data.copy()
            merged_superstructures = {}
            merged_superstructures.update(merged.get('superstructures', {}))
            merged_superstructures.update(base_data.get('superstructures', {}))
            merged['superstructures'] = merged_superstructures

            print('merging',dst,'from',base_dst)
            with open(dst, 'w') as f:
                yaml.dump(merged, f)
            continue

    # Handle relocations
    if '/v7/' in data.get('uri', '') and data.get('prerelease') is True:
        tag += '-v71'
        dst = os.path.join('..', data['type'].replace(' ', '-'), 'standard', tag + '.yaml')
        print('creating a prerelease version of',dst)

    if os.path.exists(dst):
        continue
    print('update',dst,'with',src)
    shutil.copyfile(src,dst)
