A registry of GEDCOM concepts, as proposed in [GEDCOM issue #204](https://github.com/FamilySearch/GEDCOM/issues/204)

# Repository organization

The repository is primarily made up of [YAML](https://yaml.org) files organized as documented at <https://gedcom.io/terms/format>.

YAML files are placed in this repository in subdirectories *type*`/`*subtype*`/`*name*`.yaml` where

- *type* is the value of the YAML file's `type:` key with any spaces replaced by hypens
- *subtype* is one of
    - the general meaning of the URI for `type: uri` files; otherwise
    - `standard` if the YAML file represents a concept from the official [FamilySearch GEDCOM 7 specification](https://gedcom.io/)
    - `extension` if the YAML file is defined by a third party

The `standard-addenda/`directory contains information to be added to standard YAML files. Standard files are extracted automatically from the official specification, but can be augmented with additional non-normative information such as known extension substructures, help text, etc.

The `tools/` directory contains various files and stripts for assisting in maintaining this repository. Notably, that includes a YAML schema validator that should be used by any new or edited YAML before it is pushed to the repository.

# Proposing addenda or changes

To propose a new entry or change to an existing entry,

1. Fork this repo
1. Modify the YAML file, or make the YAML file in the right directory
1. Check it using the schema checker from the `tools/` directory of this repo
1. Make a pull request

If you are unsure if your proposed change is appropriate or are uncomfortable directly editing YAML files, submit an [issue](https://github.com/FamilySearch/GEDCOM-registries/issues) instead.

If you have questions or suggestions about this repository or its contents, please direct those to the main [GEDCOM Discussions page](https://github.com/FamilySearch/GEDCOM/discussions).
