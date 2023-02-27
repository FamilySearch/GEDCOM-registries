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
    data = yaml.safe_load(open(src))
    if data['type'] == 'uri':
        continue
    tag = os.path.basename(src).replace(' ','-')
    dst = os.path.join('..',data['type'].replace(' ','-'),'standard',tag+'.yaml')
    if os.path.exists(dst) and filecmp.cmp(dst, src):
        continue
    print('update',dst,'with',src)
    shutil.copyfile(src,dst)
    
        
