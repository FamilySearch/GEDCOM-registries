# GEDCOM Registries Repository

GEDCOM Registries is a Python-based repository containing YAML files that define GEDCOM concepts and structures. The repository validates YAML files against JSON schemas and generates summary files.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap, Build, and Validate the Repository

Follow these steps in exact order for any fresh clone:

1. **Initialize Git Submodules** (REQUIRED FIRST STEP):
   ```bash
   git submodule update --init --recursive
   ```
   Takes ~5 seconds. NEVER CANCEL. This downloads GEDCOM.io and GEDCOM repositories needed for validation schemas.

2. **Install Python Dependencies** (if not already available):
   ```bash
   pip3 install PyYAML jsonschema
   ```
   PyYAML and jsonschema are required. yamllint is typically pre-installed.

3. **Run Full Validation Workflow**:
   ```bash
   # YAML syntax validation (2 seconds)
   yamllint .
   
   # Schema validation (9 seconds) - NEVER CANCEL
   cd registry_tools
   find .. -type f -name "*.yaml" -not -path "../registry_tools/*" -exec dirname {} \; | sort -u | while read -r dir; do
     yaml_files=("$dir"/*.yaml)
     if [ "${#yaml_files[@]}" -gt 0 ]; then
       echo "Checking directory $dir"
       python3 validator.py "${yaml_files[@]}"
       if [ $? -ne 0 ]; then
         exit 1
       fi
     fi
   done
   cd ..
   
   # Global validation (1 second)
   python3 ./registry_tools/global-validator.py
   ```
   Total validation time: ~18 seconds. NEVER CANCEL. Set timeout to 60+ seconds.

4. **Generate Summary Files**:
   ```bash
   # Sync with GEDCOM standard (1 second)
   python3 registry_tools/syncstandard.py
   
   # Generate TSV files (2 seconds)
   python3 registry_tools/makeTSV.py
   
   # Generate JSON validation file (2 seconds)
   python3 registry_tools/makeJSON.py
   ```
   Total generation time: ~5 seconds. NEVER CANCEL. Set timeout to 30+ seconds.

### Key Validation Commands

- **Single file validation**: `cd registry_tools && python3 validator.py ../path/to/file.yaml`
- **YAML syntax check**: `yamllint path/to/file.yaml`
- **Global validation**: `python3 ./registry_tools/global-validator.py`

## Validation

- ALWAYS run the complete validation workflow after making changes to YAML files.
- NEVER CANCEL validation or generation commands - they complete quickly but timeouts should be generous.
- The CI (.github/workflows/validate-yaml.yml) will fail if validation does not pass.
- Changes to standard YAML files require corresponding changes in the GEDCOM specification itself.

## Repository Structure

### Key Directories
- **`calendar/standard/`** - Calendar-related YAML files (4 files)
- **`data-type/standard/`** - Data type definitions (44 files)
- **`enumeration/standard/`** - Enumeration values (71 files)
- **`enumeration-set/standard/`** - Enumeration sets (12 files)
- **`month/standard/`** - Month definitions (38 files)
- **`structure/standard/`** - Standard GEDCOM structures (375 files)
- **`structure/extension/`** - Extension structures (2 files)
- **`uri/exid-types/`** - URI external ID types (14 files)
- **`generated_files/`** - Auto-generated summary files (TSV, JSON)
- **`registry_tools/`** - Python validation and generation scripts

### Important Files
- **`.yamllint.yml`** - YAML linting configuration
- **`registry_tools/validator.py`** - YAML schema validation script
- **`registry_tools/validatorlib.py`** - Validation library
- **`registry_tools/global-validator.py`** - Cross-file validation
- **`registry_tools/GEDCOM.io/yaml-schema.yaml`** - Main validation schema (submodule)

## Common Tasks

### Adding or Modifying YAML Files

1. Create or edit YAML file in appropriate directory following naming convention
2. Run schema validation: `cd registry_tools && python3 validator.py ../path/to/file.yaml`
3. Run complete validation workflow (see above)
4. Run generation scripts to update summary files
5. Always commit both the YAML changes and regenerated files

### YAML File Structure

All YAML files must follow the basic structure defined in the official documentation:

- **YAML File Format**: https://github.com/FamilySearch/GEDCOM.io/blob/main/_pages/yaml-file-format.md
- **Schema for v7 files**: https://github.com/FamilySearch/GEDCOM.io/blob/main/yaml-schema.yaml  
- **Schema for v5.5.1 files**: https://github.com/FamilySearch/GEDCOM.io/blob/main/yaml-schema-v5.5.1.yaml

Key required fields for all YAML files:
- `lang`: Language tag (e.g., "en-US")
- `type`: One of "structure", "enumeration", "enumeration set", "calendar", "month", "data type", "uri"
- `uri`: The URI that identifies the concept
- `specification`: List of descriptions (required for most types except "enumeration set")

### File Naming Convention

Files are organized as: `type/subtype/name.yaml` where:
- **type**: Value of YAML file's `type:` key (spaces → hyphens)
- **subtype**: `standard` (official GEDCOM 7 spec) or `extension` (community extensions)
- **name**: Identifier selected at registration time

### Git Submodules

The repository uses two git submodules:
- **`registry_tools/GEDCOM`** - FamilySearch GEDCOM specification
- **`registry_tools/GEDCOM.io`** - GEDCOM.io schemas and documentation

ALWAYS run `git submodule update --init --recursive` after cloning.

## Time Expectations

- **Submodule initialization**: 5 seconds - NEVER CANCEL
- **YAML syntax validation**: 2 seconds - NEVER CANCEL
- **Schema validation**: 9 seconds - NEVER CANCEL, set timeout 60+ seconds
- **Global validation**: 1 second - NEVER CANCEL
- **File generation**: 5 seconds total - NEVER CANCEL, set timeout 30+ seconds
- **Complete validation workflow**: 18 seconds - NEVER CANCEL, set timeout 60+ seconds

## Common Command Reference

```bash
# Complete fresh setup
git submodule update --init --recursive

# Validate single file
cd registry_tools && python3 validator.py ../structure/standard/record-INDI.yaml

# Run complete validation (like CI)
yamllint . && cd registry_tools && find .. -type f -name "*.yaml" -not -path "../registry_tools/*" -exec dirname {} \; | sort -u | while read -r dir; do yaml_files=("$dir"/*.yaml); if [ "${#yaml_files[@]}" -gt 0 ]; then echo "Checking directory $dir"; python3 validator.py "${yaml_files[@]}"; if [ $? -ne 0 ]; then exit 1; fi; fi; done && cd .. && python3 ./registry_tools/global-validator.py

# Generate all summary files
python3 registry_tools/syncstandard.py && python3 registry_tools/makeTSV.py && python3 registry_tools/makeJSON.py

# View directory structure
find . -maxdepth 2 -type d | grep -v "\.git" | sort
```

## Generated Files Output

Running the generation scripts creates these files in `generated_files/`:
- `registry_path.tsv` - Maps URIs to file paths
- `cardinalities.tsv` - Cardinality information
- `enumerations.tsv` - Enumeration data
- `enumerationsets.tsv` - Enumeration set data  
- `payloads.tsv` - Payload type information
- `substructures.tsv` - Substructure relationships
- `g7validation.json` - JSON validation data
- Various manifest files for different GEDCOM versions