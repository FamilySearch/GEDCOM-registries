from validatorlib import check
import yaml
import sys

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
