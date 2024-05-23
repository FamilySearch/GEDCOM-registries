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

When an implementation has an extension and makes changes that affect its use in GEDCOM files,
the YAML file should be updated. The appropriate changes to the YAML file depend on the nature
of the changes in the implementation.

If the implementation merely starts using a documented extension with another GEDCOM version,
no changes to the YAML file are needed.

If the implementation updates its use (e.g., to add a new substructure) for all GEDCOM versions
that it the structure can appear in, and it is the only implementation using the extension then
it can simply update the existing YAML file.

If the implementation updates its use but only for some versions of GEDCOM, or is not the only
implementation using the extension, then it should create and register a new YAML file with a new URI.
