A registry of GEDCOM concepts, as proposed in [GEDCOM issue #204](https://github.com/FamilySearch/GEDCOM/issues/204)

# Repository organization

The repository is primarily made up of [YAML](https://yaml.org) files organized as documented at <https://gedcom.io/terms/format>.

If you know the URI of the extension you want, you can look up its YAML file path in [registry_path.tsv](generated_files/registry_path.tsv).
Other files in the [generated_files/](generated_files/) directory may also be of interest to GEDCOM tool developers.

YAML files are placed in this repository in subdirectories *type*`/`*subtype*`/`*name*`.yaml` where

- *type* is the value of the YAML file's `type:` key with any spaces replaced by hypens
- *subtype* is one of
    - the general meaning of the URI for `type: uri` files; otherwise
    - `standard` if the YAML file represents a concept from the official [FamilySearch GEDCOM 7 specification](https://gedcom.io/)
    - `extension` if the YAML file is not in the official specification
- *name* is an identifier selected at time of registration

The [registry_tools/](registry_tools/) directory contains various files and stripts for assisting in maintaining this repository. Notably, that includes a YAML schema validator that should be used by any new or edited YAML before it is pushed to the repository.

# Proposing changes or new files

To propose a new entry or change to an existing entry,

1. Fork this repo
1. Modify the YAML file, or create the YAML file in the right directory
1. Check it using the schema checker from the [registry_tools/](registry_tools/) directory of this repo
1. Make a pull request

If the change is to a `standard` term, the change needs to be made to the specification itself instead; changes to `standard` terms here will be overwritten on the next patch release of the FamilySearch GEDCOM spec.

When YAML files reference one another, either directly  by URI (for example, an enumeration set referencing is enumerated values) or indirectly (for example, a `translated from` field suggesting the existance of anther YAML file for the same URI), any files that are not already in the registry should be submitted together.

If you are unsure if your proposed change is appropriate or are uncomfortable directly editing YAML files and making pull requests, submit an [issue](https://github.com/FamilySearch/GEDCOM-registries/issues) instead.

If you have questions or suggestions about this repository or its contents, please direct those to the main [GEDCOM Discussions page](https://github.com/FamilySearch/GEDCOM/discussions).

## Registering extensions

There are two types of extensions whose files appear in the same 'extension' subdirectories, allowing for
two paths for standardization of additions:

* Vendor-specific: Extensions that are already used by one or more specific vendors, websites, or applications.
  Such an extension is typically registered after it is already implemented and deployed.
* Community proposed: Extensions that are potentially of interest to multiple vendors, websites, and/or
  applications.
  Such an extension is typically registered before being implemented or deployed, as a result of discussion
  in GitHub.

In either case, once an extension meets the
[Valuable, Absent, and Used criteria](https://github.com/FamilySearch/GEDCOM/tree/main/attribute-event-requests#proposing-new-family-and-individual-attributes-and-events)
then a standard tag/URI can be added into the 'v7.1' branch of the
[FamilySearch/GEDCOM repository](https://github.com/FamilySearch/GEDCOM) for inclusion into a future release.

## Updating extensions

Three kinds of updates might be made to an extension.

- Changes in presentation or documentation that do not change how the extension is used in GEDCOM files (a "patch").
- Changes that result in all files that followed the old version remaining valid and having the same meaning under the new version (a "minor update").
- Changes that change or remove components of the extension, such that files that followed the old version would have a different meaning or be invalid under the new version (a "major update").

The first two (patches and minor updates) of these changes can be made by updating the existing YAML file, leaving the extension's URI unchanged. The third (major updates) should be made by registering a new YAML file with a new URI.

Note that this is a different set of criteria than are applied to standard structures, where both major and minor updates are also given new URIs and YAML files. Extensions provide the same flexibility as would a new minor version GEDCOM, and hence new URIs for minor changes to them are not needed. That said, if an extension author wishes to provide a new URI and YAML file for a minor update, that is permitted with the `subsumes` entry in the YAML file providing a way to indicate the previous minor version.
