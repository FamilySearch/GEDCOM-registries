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

if __name__ == '__main__':
  if '--help' in sys.argv or '-h' in sys.argv or '?' in sys.argv:
    print("USAGE:", sys.argv[0], 'file_to_validate.yaml', '[another_file.yaml ...]')
    print('If given no arguments, reads YAML from stdin')
    quit()

  count = 0
  ok = 0
  if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
      count += 1
      try:
        data = yaml.safe_load(open(arg))
      except BaseException as ex:
        print("="*30, file=sys.stderr)
        print("Failed to load", arg, file=sys.stderr)
        print(ex, file=sys.stderr)
        continue
      if check(data, arg): ok += 1
  else:
    for data in yaml.safe_load_all(sys.stdin):
      count += 1
      if check(data, 'YAML sent to stdin'): ok += 1

  if ok != count:
    print("="*30+'\n')
  print("YAML files checked:",count)
  print("YAML files passed:",ok)
  if ok != count:
    sys.exit(1)
