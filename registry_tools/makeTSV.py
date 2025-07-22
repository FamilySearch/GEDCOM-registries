import os, os.path
import sys
import yaml

root = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))

cardinalities, cardinalities_header = set(), 'superstructure structure cardinality'.split()
enumerations, enumerations_header = [], 'structure set'.split()
enumerationsets, enumerationsets_header = set(), 'set value'.split()
payloads, payloads_header = [], 'structure payload'.split()
substructures, substructures_header = set(), 'superstructure tag structure'.split()
registry_path, registry_path_header = [], 'uri yaml_path language'.split()
manifest70, manifest70_header = [], 'yaml_path'.split()
extensions, extensions_header = [], 'tag yaml_path language'.split()

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
                doc = yaml.safe_load(open(os.path.join(p, f)))
                if isinstance(doc, dict) and 'uri' in doc:
                    lang = doc['lang']
                    registry_path.append([doc['uri'], os.path.join(kind.name, os.path.split(p)[-1], f), lang])
                    if 'extension tags' in doc:
                        for e in doc['extension tags']:
                            extensions.append([e, os.path.join(kind.name, os.path.split(p)[-1], f), lang])
                    if 'standard tag' in doc or 'extension tags' not in doc:
                        manifest70.append([os.path.join(kind.name, os.path.split(p)[-1], f)])
                else:
                    print(f"Warning: No URI found in {os.path.join(kind.name, os.path.split(p)[-1], f)}")

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
        w = csv.writer(dst, dialect=csv.excel_tab)
        w.writerow(locals()[name+'_header'])
        w.writerows(sorted(locals()[name]))

with open(os.path.join(root,'generated_files','manifest-7.0-en-US.tsv'), 'w') as dst:
    w = csv.writer(dst, dialect=csv.excel_tab)
    w.writerow(locals()['manifest70_header'])
    w.writerows(sorted(locals()['manifest70']))

with open(os.path.join(root,'generated_files','manifest-extensions-en-US.tsv'), 'w') as dst:
    w = csv.writer(dst, dialect=csv.excel_tab)
    w.writerow(locals()['extensions_header'])
    w.writerows(sorted(locals()['extensions']))
