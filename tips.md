# Tips for Registering Older Extensions

The GEDCOM 7 registered extension mechanism was designed to be compatible with any standards-compliant extension to any GEDCOM standard version 5.3 or later. 5.3 was when the requirement that extensions use underscores to start their tags was added. However, not all extensions that were circulated followed that rule, and changes to some other aspects of the standard (such as payload length limitations, allowing `{0:3}` cardinality, and use of lower-case enumerated values) may require some small adjustments when registering some extant extensions. This document is intended as a guide to assist that registration process.

## 7.0 compliant

This section covers parts of extensions that are fully 7.0 compliant, meaning they can be parsed and serialized in the exact same format (modulo adding appropriate URI references to the HEAD.SCHMA).

### One URI/YAML per purpose

It is common for extensions to use the same tag for both a record and for a substructure with a pointer pointing to that record.
This is permitted in 7.0, but those two should have separate URIs and separate YAML files.

### Point to single record type

Each structure must allow only a single payload type.
If that payload type is a pointer, it must allow pointing to only a single type of record.

This rule can be found in [1.2. Structures](https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#structures).

### Mixed new and standard structure types

Extensions often introduce new structure types and mix them with existing standard structure types.

To share the various cases, we used the following metasyntactic variables:

- `_NEW` is a tag used for a new (non-standard) extension structure type with URI `ext:NEW`.

- `_SUB` is a tag used for of a new (non-standard) extension structure type with URI `ext:SUB`.

- `OLD` is the tag of a standard structure type with URI `std:OLD`.

- `_OLD` is an extension tag used for a standard structure type with URI `std:OLD`.

- `OSB` is the tag of a standard structure type with URI `std:OSB`.

- `_OSB` is an extension tag used for a standard structure type with URI `std:OSB`.


The following are cases to handle:

####`_NEW`.`_SUB`

The YAML file for `ext:SUB`'s `superstructures` field should include `ext:NEW`,
and the YAML file for `ext:NEW`'s `substructures` field should include `ext:SUB`,
both with the same cardinality.

If one of these YAML files has a different change controller, including the connection in only the other YAML file is appropriate.

#### `OLD`.`_SUB`

The YAML file for `ext:SUB`'s `superstructures` field should include `std:OLD`

If an extension allows this only in some contexts,
such as `_SUB` being allowed under `CREA`.`DATE` but not under `CHAN`.`DATE`,
then they are actually creating a [subtype of a standard type](#subtype-of-a-standard-type) instead.

#### `_NEW`.`OLD`

The YAML file for `ext:NEW`'s `substructures` field should include `std:OLD`.

> [!WARNING]
> The YAML file should also express what tag is used for this extension-defined substructure, but there is no YAML support for that yet.
>
> See [GEDCOM.io#298](https://github.com/FamilySearch/GEDCOM.io/issues/298) for more details.

#### `_NEW`.`SUB`

> [!WARNING]
> This is allowed (though deprecated) by [1.5. Extensions](https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#extensions) but not yet supported in any way by the registry.
>
> See [GEDCOM.io#298](https://github.com/FamilySearch/GEDCOM.io/issues/298) for more details.

#### `_NEW`.`_OLD`

The YAML file for `ext:NEW`'s `substructures` field should include `std:OLD`.

The `HEAD`.`SCHMA` of the file should include `2 TAG _OLD std:OLD` (where `std:` is expanded from prefix notation).

> [!WARNING]
> There is currently no way of indicating in the YAML that this tag is used for this structure; it requires a `HEAD`.`SCHMA` instead.

#### `OLD`.`_OSB`

The `HEAD`.`SCHMA` of the file should include `2 TAG _OSB std:OSB` (where `std:` is expanded from prefix notation).

> [!WARNING]
> There is currently no way of indicating in the YAML that this tag is used for this structure; it requires a `HEAD`.`SCHMA` instead.
>
> [GEDCOM-registries#179](https://github.com/FamilySearch/GEDCOM-registries/issues/179) includes a recommendation that this be capable of being registered in the future.




## Requires conversion

### Standard tag as an extension subtype of a standard structure

If a file contains `ABC`.`DEF` where `ABC` parses as a standard structure type
and `DEF` is not the tag of one of that types' standard substructures,
then this is an extension that violates every version of GEDCOM since 5.3
and must be converted to a different format to be compliant with the 7.0 standard.

The conversion requires replacing `DEF` with an extension tag,
at which point it falls under one of the cases described in [Mixed new and standard structure types](#mixed-new-and-standard-structure-types).

See [GEDCOM.io#290](https://github.com/FamilySearch/GEDCOM.io/issues/290) for progress on registry support for making such a conversion easier.

### Subtype of a standard type

Some extensions support a new substructure to a standard structure,
but only do so in some of the places that standard structure appears.
Because a structure type defines its set of allowed substructures (see [1.2. Structures](https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#structures)),
this actually means that the extension is splitting the standard superstructure type into two different types.

To take a concrete example, <https://gedcom.io/terms/v7/DATE-exact> is a standard structure with four superstructures.
If an extension added a substructure to it when it is `HEAD`.`SOUR`.`DATA`.`DATE` but not when it is under `CHAN`, `CREA`, or `ord-STAT`
then the extension is actually defining an extension of `HEAD`.`SOUR`.`DATA`.
This would involve registering a YAML file for that extension, largely a copy of the current <https://gedcom.io/terms/v7/HEAD-SOUR-DATA> but using `subsumes` to indicate the subtype relationship.
The changed fields would be

```yaml
uri: https://example.com/my/replacement/of/HEAD-SOUR-DATA

subsumes:
  - https://gedcom.io/terms/v7/HEAD-SOUR-DATA

extension tags:
  - '_DATA'

substructures:
  "https://gedcom.io/terms/v7/COPR": "{0:1}"
  "https://gedcom.io/terms/v7/DATE-exact": "{0:1}"
  "https://example.com/my/new/structure": "{0:1}"

contact: "how to contact the extension proposer"
...
```

This would also mean that the extension would need to use `_DATA` instead of `DATA` for the substructure of `HEAD`.`SOUR`.

> [!WARNING]
> While the above replacement of a standard structure with an extension that extends it is fully compliant with the 7.0 standard, partial implementations might fail to realize that the extension type can be treated like the structure type it subsumes, resulting in those implementations losing data.

### More restrictive versions of standard types

Some applications fail to support the full flexibility of the GEDCOM standard they (partially) implement.
For example, they might chose not to support the `ALIA` substructure of `INDI` records
or only allow QUAY values 0 and 3, not 1 or 2.

It is not appropriate to define an extension that is a more limited version of a standard structure.
These should be converted to the corresponding standard structure during export,
and the application should identify and warn about values it cannot handle during import.

In some cases, what appears to be a restriction actually enables new functionality,
such as a string-valued payload being limited to an enumeration set
or a UID checksum being used to detect user error.
These may be registered as extensions, but per [Section 1.5.3. Extension versus Standard](https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#extension-versus-standard)
they should be accompanied by and kept in sync with the corresponding standard structures.


### Enumerations not following Enum production

The enumeration datatype ([Section 2.3. Enumeration](https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#enumeration) restricts the values that may appear in a limited vocabulary payload.
Versions 5.5.1 and before were less constrained on this, with lower-case letters and slashes in some payloads,
and some extensions were even less constrained.

When converting an extension that expects one of a fixed set of values as a payload,
there are two choices.
Either, those values can be converted to the enumeration datatype, registering one YAML file for each along with a `type: enumeration set` YAML file for the full set of values;
or the original values can be kept as-is with the `xsd:string` datatype, meaning there is nothing to prevent users from editing the strings arbitrarily.


### Cardinality violations

Cardinality is intended to be intrinsic to meaning:
either a superstructure without a substructure makes sense or it does not,
and either a superstructure without multiple substructures makes sense or it does not.
Because of this, there is no provision for extending cardinality.

If an extension uses a singular substructure plurally,
a new extension structure should be created to explain the meaning of this usage.
This is more than documenting the possibility: the meaning is also required,
including the significance of the order of the substructures (if any).

For example, `g7:record-SOUR` allows at most one `g7:TEXT` substructure.
An extension might have several `g7:TEXT`-like structures which are alternative texts (most-preferred first),
or several `g7:TEXT`-like structures which are discontiguous segments of the source (in document order),
or several `g7:TEXT`-like structures which are the same text translated into different languages or media types (in arbitrary order).
Any one of these is a fine extension, but the extension should be clear which one it is implementing
and none would use the standard structure's URI.


### Pointers to substructures

GEDCOM syntax is capable of putting cross-reference identifiers on substructures
and having pointers point to them,
but doing so is forbidden by the 7.0 specification and implicitly not supported in 5.5.1 and earlier specifications.

[GEDCOM#328](https://github.com/FamilySearch/GEDCOM/discussions/328) discusses an extension that uses pointers to substructures, along with various ideas abut how to resolve them,
such as refactoring to use records or using extensions for storing pseudo-pointers.
None fully satisfied the original poster of that discussion, but they do allow expressing most data.


### Standard substructure types promoted to records or vice-versa

Record types and substructure types are different.
Substructure types clarify or expand on their superstructure;
records do not.
For example, a `g7:PLAC` structure is not just a description of a place,
it is also an assertion that its superstructure occurred at that place.

Extensions that wish to relocate substructures to records or vice-versa
must instead create a new extension type for the new location.
Extensions that wish to use the same new extension structure type in both record and substructure locations
must instead create two types, one as a record and one as a substructure.

### Multi-type payloads

Each structure type has one payload datatype.
If an extension allows multiple payload types,
each one must be registered with a separate URI and serialized with a separate tag.
Note that "pointer to record type 1" and "pointer to record type 2" are separate payload types, and both are distinct from `xsd:string`.
