from validatorlib import check
import yaml
import sys

if '--help' in sys.argv or '-h' in sys.argv or '?' in sys.argv:
  print("USAGE:", sys.argv[0], 'file_to_validate.yaml', '[another_file.yaml ...]')
  print('If given no arguments, reads YAML from stdin')
  quit()

base_dir = os.path.join(os.path.dirname(__file__), 'GEDCOM.io')
try:
  schema_v7 = yaml.safe_load(open(os.path.join(base_dir, 'yaml-schema.yaml')))
  schema_v551 = yaml.safe_load(open(os.path.join(base_dir, 'yaml-schema-v5.5.1.yaml')))
except Exception as ex:
  print("Fatal Error loading schema(s):", ex, file=sys.stderr)
  exit(1)

def check(data, name, schemas):
  success = True
  for version, schema in schemas.items():
    try:
      validate(data, schema)
    except BaseException as ex:
      print("="*30, file=sys.stderr)
      print(f"Validation error with {name} against {version}", file=sys.stderr)
      print(ex, file=sys.stderr)
      success = False
  return success

def detect_versions(text):
  versions = {}
  if '/v7/' in text:
    versions['v7'] = schema_v7
  if '/v5.5.1/' in text:
    versions['v5.5.1'] = schema_v551
  if not versions:
    versions['default (v7)'] = schema_v7
  return versions

count = 0
ok = 0

def process_yaml(source, name):
  global ok, count
  count += 1
  try:
    raw_text = source.read()
    data = yaml.safe_load(raw_text)
    schemas = detect_versions(raw_text)
    if check(data, name, schemas): ok += 1
  except BaseException as ex:
    print("="*30, file=sys.stderr)
    print("Failed to load", name, file=sys.stderr)
    print(ex, file=sys.stderr)

if len(sys.argv) > 1:
  for arg in sys.argv[1:]:
    with open(arg, 'r') as f:
      process_yaml(f, arg)
else:
  process_yaml(sys.stdin, 'YAML sent to stdin')

if ok != count:
  print("="*30+'\n')
print("YAML files checked:", count)
print("YAML files passed:", ok)
if ok != count:
  sys.exit(1)
