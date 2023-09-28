import os, os.path
import sys
import yaml

root = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))

cardinalities = set() # super, sub, card
enumerations = [] # struct, set
enumerationsets = set() # set, value
payloads = [] # struct, payload
substructures = set() # super, tag, sub
registry_path = [] # uri, yaml path

tagsof = {}
for kind in ('structure', 'month', 'enumeration', 'calendar'):
    for p,t,fs in os.walk(os.path.join(root, kind)):
        for f in fs:
            doc = yaml.safe_load(open(os.path.join(p,f)))
            if 'standard tag' in doc:
                tagsof.setdefault(doc['uri'],set()).add(doc['standard tag'])
            if 'extension tags' in doc:
                tagsof.setdefault(doc['uri'],set()).update(doc['extension tags'])

for kind in os.scandir(root):
    if kind.is_dir() and '_' not in kind.name and kind.name[0] != '.':
        for p,t,fs in os.walk(os.path.join(root, kind.name)):
            for f in fs:
                doc = yaml.safe_load(open(os.path.join(p,f)))
                registry_path.append([doc['uri'], os.path.join(kind,os.path.split(p)[-1],f)])

for p,t,fs in os.walk(os.path.join(root, 'structure')):
    for f in fs:
        doc = yaml.safe_load(open(os.path.join(p,f)))
        for o,c in doc['superstructures'].items():
            for tag in tagsof[doc['uri']]:
                substructures.add((o,tag,doc['uri']))
            cardinalities.add((o,doc['uri'],c))
        for o,c in doc['substructures'].items():
            for tag in tagsof[o]:
                substructures.add((doc['uri'],tag,o))
            cardinalities.add((doc['uri'],o,c))
        payloads.append((doc['uri'],doc['payload']))
        if 'enumeration set' in doc:
            enumerations.append((doc['uri'],doc['enumeration set']))

for p,t,fs in os.walk(os.path.join(root, 'enumeration')):
    for f in fs:
        doc = yaml.safe_load(open(os.path.join(p,f)))
        for uri in doc['value of']:
            enumerationsets.add((uri, doc['uri']))

for p,t,fs in os.walk(os.path.join(root, 'enumeration-set')):
    for f in fs:
        doc = yaml.safe_load(open(os.path.join(p,f)))
        for uri in doc['enumeration values']:
            enumerationsets.add((doc['uri'],uri))

import csv
os.makedirs(os.path.join(root,'generated_files'), exist_ok=True)
for name in ('substructures','payloads','cardinalities','enumerations','enumerationsets', 'registry_path'):
    with open(os.path.join(root,'generated_files',name+'.tsv'), 'w') as dst:
        csv.writer(dst, dialect=csv.excel_tab).writerows(sorted(locals()[name]))
