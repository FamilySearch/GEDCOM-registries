"""
This file checks rules that apply between files rather than within a single file.
It also validates each file individually using the schema checking code in validator.py

A few places where the code may be overly constrained and need to be loosened in the future are commented with comments beginning "# Note:"
"""

from validatorlib import check as check_one_file, detect_versions
import yaml
had_error = False


def err(*msg):
  global had_error
  print('ERROR',*msg)
  had_error = True
  
def find_all_yaml():
  """A generator function producing all yaml files in the repository
  Each is returned as (openable, canonical) path"""
  from os.path import isfile, dirname, join, relpath, abspath
  from pathlib import Path
  from os import walk
  
  repo = abspath(join(dirname(__file__), '..'))
  for dirpath, dirnames, filenames in walk(repo):
    for d in tuple(dirnames):
      if d[0] == '.': dirnames.remove(d)
      if d == 'registry_tools': dirnames.remove(d)
      if d == 'generated_files': dirnames.remove(d)
    for fn in filenames:
      if fn[0] != '.' and (fn.lower().endswith('.yml') or fn.lower().endswith('.yaml')):
        yield join(dirpath,fn), Path(relpath(join(dirpath,fn), start=repo))


def extension_matches_standard(extension_data, standard_structures):
  """
  Check if an extension-defined substructure matches a standard structure with the same tag.
  According to the specification, extension-defined substructures should match the structure type,
  payload, and substructure collection of at least one standard type with the same tag.
  They can add more substructures to the substructure collection.
  """
  if 'standard tag' not in extension_data:
    return False
    
  tag = extension_data['standard tag']
  
  # Find all standard structures with the same tag
  matching_standards = []
  for data in standard_structures:
    if data.get('standard tag') == tag:
      matching_standards.append(data)
  
  if not matching_standards:
    return False
  
  # Check if extension matches at least one standard structure
  for standard_data in matching_standards:
    # Check structure type
    if extension_data.get('type') != standard_data.get('type'):
      continue
      
    # Check payload
    if extension_data.get('payload') != standard_data.get('payload'):
      continue
      
    # Check substructure collection - extension must include all standard substructures
    # but can add more
    standard_substructures = standard_data.get('substructures', {})
    extension_substructures = extension_data.get('substructures', {})
    
    # All standard substructures must be present in extension
    match = True
    for uri, cardinality in standard_substructures.items():
      if uri not in extension_substructures:
        match = False
        break
      # The cardinality should also match (this could be relaxed in future if needed)
      if extension_substructures[uri] != cardinality:
        match = False
        break
    
    if match:
      return True
  
  return False


def check_paths(files=None):
  """
  Checks the paths of each YAML file.
  Returns {(type,subtype,name):{...contents of YAML file...}} for all files that pass the check
  """
  if files is None: files = find_all_yaml()
  ans = {}
  standard_structures = []  # Collect standard structures for extension validation
  
  # First pass: collect all files and identify standard structures
  all_files = []
  for a,r in files:
    if not r.suffix == '.yaml':
      err("YAML files should use extension .yaml, not",r.suffix)
      continue
    if len(r.parts) != 3:
      err("YAML files should be in path type/subtype/name.yaml but",r,"is not")
      continue
    if r.parts[0] != 'uri' and r.parts[1] not in ['standard','extension']:
      err("Path",r,"wrong; expected 'standard' or 'extension', not",repr(r.parts[1]))
      continue
    with open(a, 'r') as f:
      raw_text = f.read()
    data = yaml.safe_load(raw_text)
    schemas = detect_versions(raw_text)
    if not check_one_file(data, r, schemas):
      had_error = True
      continue
    if data['type'].replace(' ','-') != r.parts[0]:
      err("Path",r,"wrong; expected", repr(data['type'].replace(' ','-')), 'not', repr(r.parts[0]))
      continue
    
    data[None] = r # store path in collision-free location for later use
    all_files.append((data, r))
    
    # Collect standard structures for later validation
    if r.parts[1] == 'standard':
      standard_structures.append(data)
  
  # Second pass: validate 'standard tag' usage
  for data, r in all_files:
    if 'standard tag' in data and r.parts[1] != 'standard':
      # Check if this extension matches a standard structure
      if not extension_matches_standard(data, standard_structures):
        print("WARNING:",r,"has 'standard tag' but is not in a path for standard files and does not match any standard structure with the same tag")
    
    ans[r] = data
  return ans

tocheck = check_paths()

# uri+lang never repeated
uri_lang = {}
for (r, d) in tocheck.items():
  u_l = d['uri'], d['lang']
  if u_l in uri_lang:
    err('both',uri_lang[u_l],'and',r,'have URI',u_l[0][None],'and language',u_l[1])
  else:
    uri_lang[u_l] = d

# translations are from present values
for ((u,l),d) in uri_lang.items():
  if 'translated from' in d and (u,d['translated from']) not in uri_lang:
    err(d[None],'was translated from',d['translated from'],'but no file for',u,'in that language was registered')


if had_error:
  print("Errors found with structure of files, preventing reliable checks within files; exiting.")
  quit(1)


# Find a canonical entry for each known URI
byuri = {}
for (r, d) in tocheck.items():
  if 'translated from' in d: continue
  if d['uri'] in byuri:
    print('WARNING: both',r,'and',byuri[d['uri']],'have the same URI and neither is marked as a translation of the other')
  byuri[d['uri']] = d


# A list of keys shows values are expected to change between different languages
# Note: if new keys are added, they may need to be added to this function
translatable_keys = ('lang', 'change controller', 'contact', 'documentation', 'fragment', 'help text', 'label', 'specification', 'translated from')

# Verify that translations agree in everything that is not translatable
# Note: this currently enforces orders of lists, but most lists are "in no particular order" per https://gedcom.io/terms/format
for (r,d) in tocheck.items():
  if d != byuri[d['uri']]:
    for key in set(d.keys()) | set(byuri[d['uri']].keys()):
      if key is None or key in translatable_keys: continue
      if d.get(key) != byuri[d['uri']].get(key):
        err(d[None],'and',byuri[d['uri']]['None'],'share URI', d['uri'], 'but differ in their',key,'entry')


def check_references(d):
  """Checks that each key that has a URI pointing to something else both (a) points to something registered and (b) points to the right type of thing"""
  
  # Note: if new keys are added, they may need a case in this function
  
  if 'calendars' in d:
    for uri in d['calendars']:
      if uri not in byuri:
        err(d['uri'],'calendars references unregistered',uri)
      elif byuri[uri]['type'] != 'calendar': 
        err(d['uri'],'calendars references',uri,'which has type:',byuri[uri]['type'],'(not calendar)')
  
  if 'enumeration set' in d:
    uri = d['enumeration set']
    if uri not in byuri:
      err(d['uri'],'enumeration set references unregistered',uri)
    elif byuri[uri]['type'] != 'enumeration set': 
      err(d['uri'],'enumeration set references',uri,'which has type:',byuri[uri]['type'],'(not enumeration set)')
    
  if 'enumeration values' in d:
    for uri in d['enumeration values']:
      if uri not in byuri:
        err(d['uri'],'enumeration values references unregistered',uri)
    
  if 'months' in d:
    for uri in d['months']:
      if uri not in byuri:
        err(d['uri'],'months references unregistered',uri)
      elif byuri[uri]['type'] != 'month': 
        err(d['uri'],'months references',uri,'which has type:',byuri[uri]['type'],'(not month)')
  
  if 'payload' in d:
    if not d['payload'] or d['payload'] == 'Y|<NULL>': pass
    elif d['payload'].startswith('@<') and d['payload'].endswith('>@'):
      uri = d['payload'][2:-2]
      if uri not in byuri:
        err(d['uri'],'points to unregistered structure type',uri)
      elif byuri[uri]['type'] != 'structure': 
        err(d['uri'],'points to',uri,'which has type:',byuri[uri]['type'],'(not structure)')
      elif len(byuri[uri]['superstructures']) != 0: 
        err(d['uri'],'points to',uri,'which is a substructure, not a record')
    else:
      uri = d['payload']
      if uri.startswith('http://www.w3.org/2001/XMLSchema#') or uri.startswith('http://www.w3.org/ns/dcat#'):
        pass # Note: there are other 3rd-party datatypes that we could probably allow too
      else:
        if uri not in byuri:
          err(d['uri'],'has unregistered payload type',uri)
        elif byuri[uri]['type'] != 'data type': 
          err(d['uri'],'has payload type',uri,'which has type:',byuri[uri]['type'],'(not data type)')
        
  if 'subsumes' in d:
    for uri in d['subsumes']:
      if uri not in byuri:
        err(d['uri'],'subsumes references unregistered',uri)
      elif byuri[uri]['type'] != d['type']: 
        err(d['uri'],'subsumes',uri,'which has type:',byuri[uri]['type'],'(not',d['type']+')')
  
  if 'substructures' in d:
    for uri in d['substructures']:
      if uri not in byuri:
        err(d['uri'],'substructures references unregistered',uri)
      elif byuri[uri]['type'] != 'structure': 
        err(d['uri'],'has substructure',uri,'which has type:',byuri[uri]['type'],'(not structure)')

  if 'superstructures' in d:
    for uri in d['superstructures']:
      if uri not in byuri:
        err(d['uri'],'superstructures references unregistered',uri)
      elif byuri[uri]['type'] != 'structure': 
        err(d['uri'],'has superstructure',uri,'which has type:',byuri[uri]['type'],'(not structure)')
  
  if 'value of' in d:
    for uri in d['value of']:
      if uri not in byuri:
        err(d['uri'],'value of references unregistered',uri)
      elif byuri[uri]['type'] != 'enumeration set': 
        err(d['uri'],'value of references',uri,'which has type:',byuri[uri]['type'],'(not enumeration set)')
    
  
      
for d in byuri.values():
  check_references(d)


if had_error:
  quit(1)
