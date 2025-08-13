from jsonschema import validate
import yaml
import os.path
import sys

try:
  schema = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), 'GEDCOM.io', 'yaml-schema.yaml')))
except:
  print("Fatal Error! GEDCOM.io/yaml-schema.yaml not found.", file=sys.stderr)
  exit(1)

def check(data, name):
  """Validates one opened-and-parsed YAML file.
  If it has errors, prints an error message to stderr using 'name' to identify the case and returns False
  Otherwise prints nothing and returns True"""
  global schema
  try:
    validate(data, schema)
    return True
  except BaseException as ex:
    print("="*30, file=sys.stderr)
    print("Validation error with", name, file=sys.stderr)
    print(ex, file=sys.stderr)
    return False
