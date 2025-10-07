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

- "tagInContext":
    - "struct":
        - superstructure URI:
            - structure URI: tag
    - "enum":
        - structure URI:
            - enumeration value URI: tag
    - "cal":
        - calendar URI: tag
    - "month":
        - calendar URI:
            - month URI: tag
    
- "label":
    - URI:
        - lang: UI label to display

"""

import os, os.path
import sys
import yaml
import json

def is_v551(uri):
    return uri.startswith('https://gedcom.io/terms/v5.5.1/')

def is_v71(uri):
    return uri.startswith('https://gedcom.io/terms/v7.1/')

root = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))

# Build a set of URIs from GEDCOM-v7.1/extracted-files/tags to identify v7.1-derived files
v71_derived_uris = set()
v71_tags_dir = os.path.join(root, 'registry_tools', 'GEDCOM-v7.1', 'extracted-files', 'tags')
if os.path.exists(v71_tags_dir):
    for filename in os.listdir(v71_tags_dir):
        filepath = os.path.join(v71_tags_dir, filename)
        if os.path.isfile(filepath):
            try:
                doc = yaml.safe_load(open(filepath))
                if isinstance(doc, dict) and 'uri' in doc:
                    v71_derived_uris.add(doc['uri'])
            except:
                pass  # Skip files that can't be parsed

stdtagof = {}
exttagof = {}
for kind in ('structure', 'month', 'enumeration', 'calendar'):
    for p,t,fs in os.walk(os.path.join(root, kind)):
        for f in fs:
            doc = yaml.safe_load(open(os.path.join(p,f)))
            if 'standard tag' in doc:
                stdtagof[doc['uri']] = doc['standard tag']
            if 'extension tags' in doc:
                exttagof.setdefault(doc['uri'],[]).extend(doc['extension tags'])

ans7 = {
    'substructure':{},
    'payload':{},
    'set':{},
    'calendar':{},
    'tag':{},
    'tagInContext':{},
    'label':{},
}

ans71 = {
    'substructure':{},
    'payload':{},
    'set':{},
    'calendar':{},
    'tag':{},
    'tagInContext':{},
    'label':{},
}

for p,t,fs in os.walk(os.path.join(root, 'structure')):
    for f in fs:
        doc = yaml.safe_load(open(os.path.join(p,f)))
        if is_v551(doc['uri']):
            continue
        
        # Determine which answer dict to use based on whether it's from GEDCOM-v7.1
        ans = ans71 if doc['uri'] in v71_derived_uris else ans7
        
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
            # Add based on whether it's from GEDCOM-v7.1
            if doc['uri'] in v71_derived_uris:
                ans71['set'].setdefault(uri, {})[tag] = doc['uri']
            elif not is_v551(doc['uri']):
                ans7['set'].setdefault(uri, {})[tag] = doc['uri']

for p,t,fs in os.walk(os.path.join(root, 'enumeration-set')):
    for f in fs:
        doc = yaml.safe_load(open(os.path.join(p,f)))
        for uri in doc['enumeration values']:
            tag = stdtagof.get(uri, uri)
            # Add based on whether it's from GEDCOM-v7.1
            if doc['uri'] in v71_derived_uris:
                ans71['set'].setdefault(doc['uri'], {})[tag] = uri
            elif not is_v551(doc['uri']):
                ans7['set'].setdefault(doc['uri'], {})[tag] = uri

for p,t,fs in os.walk(os.path.join(root, 'calendar')):
    for f in fs:
        doc = yaml.safe_load(open(os.path.join(p,f)))
        tag = stdtagof.get(doc['uri'], doc['uri'])
        cal_data = {
            'type': doc['uri'],
            'months': {stdtagof.get(_,_):_ for _ in doc['months']},
            'epochs': doc['epochs']
        }
        # Add based on whether it's from GEDCOM-v7.1
        if doc['uri'] in v71_derived_uris:
            ans71['calendar'][tag] = cal_data
        elif not is_v551(doc['uri']):
            ans7['calendar'][tag] = cal_data


for p,t,fs in os.walk(root):
    for f in fs:
        if f.endswith('.yaml') and '_' not in os.path.dirname(f):
            doc = yaml.safe_load(open(os.path.join(p,f)))
            if 'uri' in doc and is_v551(doc['uri']):
                continue
            # Determine which answer dict to use based on whether it's from GEDCOM-v7.1
            ans = ans71 if 'uri' in doc and doc['uri'] in v71_derived_uris else ans7
            if 'standard tag' in doc:
                ans['tag'][doc['uri']] = doc['standard tag']
            elif 'extension tags' in doc and len(doc['extension tags']) > 0 and doc['uri'] not in ans['tag']:
                ans['tag'][doc['uri']] = doc['extension tags'][0]
            if 'label' in doc:
                ans['label'].setdefault(doc['uri'],{})[doc['lang']] = doc['label']


def postprocess(ans):
    ans['tagInContext']['struct'] = {}
    for uri,tmap in ans['substructure'].items():
        ans['tagInContext']['struct'][uri] = {}
        for tag, details in tmap.items():
            if ':' in tag:
                if tag in exttagof: tag = exttagof[tag][0]
                else: tag = '_'
            ans['tagInContext']['struct'][uri][details['type']] = tag
    ans['tagInContext']['enum'] = {}
    for uri,pmap in ans['payload'].items():
        if 'set' in pmap:
            ans['tagInContext']['enum'][uri] = {}
            for tag, val in ans['set'][pmap['set']].items():
                if ':' in tag:
                    if tag in exttagof: tag = exttagof[tag][0]
                    else: tag = '_'
                ans['tagInContext']['enum'][uri][val] = tag
    ans['tagInContext']['cal'] = {}
    ans['tagInContext']['month'] = {}
    for cal,cmap in ans['calendar'].items():
        if ':' in cal:
            if cal in exttagof: cal = exttagof[cal][0]
            else: cal = '_'
        ans['tagInContext']['cal'][cmap['type']] = cal
        ans['tagInContext']['month'][cmap['type']] = {}
        for tag,uri in cmap['months'].items():
            ans['tagInContext']['month'][cmap['type']][uri] = tag

postprocess(ans7)
postprocess(ans71)

os.makedirs(os.path.join(root,'generated_files'), exist_ok=True)
with open(os.path.join(root, 'generated_files', 'g7validation.json'), 'w') as dst:
    json.dump(ans7, dst, indent=2, sort_keys=True)

with open(os.path.join(root, 'generated_files', 'g71validation.json'), 'w') as dst:
    json.dump(ans71, dst, indent=2, sort_keys=True)

