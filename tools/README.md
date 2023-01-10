# Validating YAML files

The file `yaml-schema.yaml` contains a [JSON Schema](https://json-schema.org/) in [YAML format](https://yaml.org/) they checks most (but not all) of the requirements of [the YAML format used to specify GEDCOM structures](https://gedcom.io/terms/format).
Constraints not checked are generally non-syntactic, such as the requirement that some URIs identify structure types or the like.

A Python 3 script is provided as `validator.py` that uses the schema to check YAML files named on the command line or piped into stdin.
It depends on [jsonschema](https://pypi.org/project/jsonschema/) and [pyyaml](https://pypi.org/project/PyYAML/).

Similar scripts in other languages are welcome.

The schema should also be compatible with most other JSON schema validators, of which there are [many](https://json-schema.org/implementations.html).

