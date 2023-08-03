"""
The goal of this file is to create a JSON file
that contains everything needed to parse and validate a GEDCOM file,
correctly identifying structure types, enumerations, and so on;
and everything needed to generate a GEDCOM file,
correctly mapping structure types, enumeration values, and so on to tags.

The JSON file structure is

- "substructure":
    - "" -or- structure type URI:
        - standard tag -or- extension structure type URI:
            - "type": uri
            - "cardinality": GEDCOM cardinality marker
- "payload":
    - structure type URI:
        - "type": "pointer" -or- "Y|<NULL>" -or- datatype URI
        - "set": enumeration set URI -- if "type" is g7:type-Enum or g7:type-List#Enum
        - "to": structure type URI -- if  "type" is "pointer"

- "set":
    - enumeration set URI:
        - standard tag -or- extension enumeration value URI: enumeration value URI

- "calendar":
    - standard tag -or- extension calendar URI:
        - "type": calendar URI
        - "months":
            - tag: month URI
        - "epochs": list of tags

- "tag":
    - URI: standard or recommended extension tag

- "label":
    - URI:
        - lang: UI label to display

"""

import os, os.path
import sys
import yaml
import json

root = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))

stdtagof = {}
for kind in ('structure', 'month', 'enumeration', 'calendar'):
    for p,t,fs in os.walk(os.path.join(root, kind)):
        for f in fs:
            doc = yaml.safe_load(open(os.path.join(p,f)))
            if 'standard tag' in doc:
                stdtagof[doc['uri']] = doc['standard tag']

ans = {
    'substructure':{},
    'payload':{},
    'set':{},
    'calendar':{},
    'tag':{},
    'label':{},
}


for p,t,fs in os.walk(os.path.join(root, 'structure')):
    for f in fs:
        doc = yaml.safe_load(open(os.path.join(p,f)))
        if doc['superstructures'] == {}:
            if doc['uri'] == 'https://gedcom.io/terms/v7/CONT': continue
            elif doc['uri'] == 'https://gedcom.io/terms/v7/HEAD':
                doc['superstructures'] = {"":"{1:1}"}
            elif doc['uri'] == 'https://gedcom.io/terms/v7/TRLR':
                doc['superstructures'] = {"":"{1:1}"}
            else:
                doc['superstructures'] = {"":"{0:M}"}
        for o,c in doc['superstructures'].items():
            tag = stdtagof.get(doc['uri'], doc['uri'])
            ans['substructure'].setdefault(o,{})[tag] = {
                'type': doc['uri'],
                'cardinality': c,
            }
        for o,c in doc['substructures'].items():
            tag = stdtagof.get(o, o)
            ans['substructure'].setdefault(doc['uri'], {})[tag] = {
                'type': o,
                'cardinality': c,
            }
        
        if doc['payload'] and doc['payload'][0] == '@':
            ans['payload'][doc['uri']] = {'type':'pointer','to':doc['payload'][2:-2]}
        else:
            ans['payload'][doc['uri']] = {'type':doc['payload']}
        if 'enumeration set' in doc:
            ans['payload'][doc['uri']]['set'] = doc['enumeration set']

for p,t,fs in os.walk(os.path.join(root, 'enumeration')):
    for f in fs:
        doc = yaml.safe_load(open(os.path.join(p,f)))
        for uri in doc['value of']:
            tag = stdtagof.get(doc['uri'], doc['uri'])
            ans['set'].setdefault(uri, {})[tag] = doc['uri']

for p,t,fs in os.walk(os.path.join(root, 'enumeration-set')):
    for f in fs:
        doc = yaml.safe_load(open(os.path.join(p,f)))
        for uri in doc['enumeration values']:
            tag = stdtagof.get(uri, uri)
            ans['set'].setdefault(doc['uri'], {})[tag] = uri

for p,t,fs in os.walk(os.path.join(root, 'calendar')):
    for f in fs:
        doc = yaml.safe_load(open(os.path.join(p,f)))
        tag = stdtagof.get(doc['uri'], doc['uri'])
        ans['calendar'][tag] = {
            'type': doc['uri'],
            'months': {stdtagof.get(_,_):_ for _ in doc['months']},
            'epochs': doc['epochs']
        }

for p,t,fs in os.walk(root):
    for f in fs:
        if f.endswith('.yaml') and '_' not in os.path.dirname(f):
            doc = yaml.safe_load(open(os.path.join(p,f)))
            if 'standard tag' in doc:
                ans['tag'][doc['uri']] = doc['standard tag']
            elif 'extension tags' in doc and len(doc['extension tags']) > 0 and doc['uri'] not in ans['tag']:
                ans['tag'][doc['uri']] = doc['extension tags'][0]
            if 'label' in doc:
                ans['label'].setdefault(doc['uri'],{})[doc['lang']] = doc['label']


os.makedirs(os.path.join(root,'generated_files'), exist_ok=True)
with open(os.path.join(root,'generated_files','g7validation.json'), 'w') as dst:
    json.dump(ans, dst, indent=2, sort_keys=True)
