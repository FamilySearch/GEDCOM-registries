# Summary files

The files in this directory contain summary information
extracted from the YAML files in this repository
by scripts in the `../registry_tools/` directory.

Files in this directory should not be manually updated.

The files generated here are:

## cardinalities.tsv

This table has the following key columns:

* superstructure: The URI of a superstructure.
* structure: The URI of a structure that has the given superstructure.

This table has the following non-key columns:

* cardinality: The cardinality of the structure under its superstructure.

## enumerations.tsv

This table has the following key columns:

* structure: The URI of a structure that uses enumerations.

This table has the following non-key columns:

* set: The URI of the enumeration set used by the structure.

## enumerationsets.tsv

This table has the following key columns:

* set: The URI of an enumeration set.
* value: The URI of an enumeration value in the set.

## g7validation.json

(description to be added)

## payloads.tsv

This table can be used to look up the payload syntax for a given structure.

The table has the following key columns:

* structure: The URI that identifies the concept documented in a YAML file.

The table has the following non-key columns:

* payload: The payload definition as it appears in the structure's YAM file.

## registry_path.tsv

This table can be used to look up the location of the YAML file for a given
URI in a given language.

The table has the following key columns:

* uri: The URI that identifies the concept documented in a YAML file.
* language: The language tag for the YAML file.

The table has the following non-key columns:

* yaml_path: The path, relative to the root of this repository, of the YAML file.

## substructures.tsv

This table has the following key columns:

* superstructure: The URI of a structure.
* tag: The tag of a substructure.

This table has the following non-key columns:

* structure: The URI of the substructure.
