from jsonschema import validate
import yaml
import os.path
import sys

base_dir = os.path.join(os.path.dirname(__file__), 'GEDCOM.io')
try:
  schema_v7 = yaml.safe_load(open(os.path.join(base_dir, 'yaml-schema.yaml')))
  schema_v71 = yaml.safe_load(open(os.path.join(base_dir, 'yaml-schema.yaml')))
  schema_v551 = yaml.safe_load(open(os.path.join(base_dir, 'yaml-schema-v5.5.1.yaml')))
except Exception as ex:
  print("Fatal error loading schema(s):", ex, file=sys.stderr)
  exit(1)

def check(data, name, schemas):
  """Validates one opened-and-parsed YAML file.
  If it has errors, prints an error message to stderr using 'name' to identify the case and returns False
  Otherwise prints nothing and returns True"""
  success = True
  for version, schema in schemas.items():
    try:
      validate(data, schema)
      return True
    except BaseException as ex:
      print("="*30, file=sys.stderr)
      print(f"Validation error with {name} against {version}", file=sys.stderr)
      print(ex, file=sys.stderr)
      success = False
  return success

def detect_versions(text):
  versions = {}
  if '/v7.1/' in text:
    versions['v7.1'] = schema_v71
  elif '/v7/' in text:
    versions['v7'] = schema_v7
  if '/v5.5.1/' in text:
    versions['v5.5.1'] = schema_v551
  if not versions:
    versions['default (v7)'] = schema_v7
  return versions
