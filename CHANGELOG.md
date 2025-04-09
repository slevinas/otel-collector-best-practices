# CHANGELOG

## [Unreleased]
### Added
- **Randomized JSON Payload Generation for CLI Store Command**
  - New `--randomize` flag to generate random x and y values.
  - New `--min` and `--max` options to specify the range for generated random values.
  - When `--randomize` is set, any provided x and y values are ignored.
  - The generated JSON payload will have structure:  
    ```json
    {"x": {"value": <random_value>}, "y": {"value": <random_value>}}
    ```
  - Examples:
    - To store with randomized values (default range 0.0 - 10.0):  
      ```
      python cli.py store TestStore --randomize
      ```
    - To store with randomized values within a custom range (e.g., 5 to 20):  
      ```
      python cli.py store TestStore --randomize --min 5 --max 20
      ```
- CLI usage updated to include help messages for the new options.

## [0.3.1] - YYYY-MM-DD
### Added
- Implemented randomized JSON payload generation based on user-provided CLI options.
- Updated CLI command for `store` to check for `--randomize` flag and generate random float values using Python's `random.uniform()`.

### Changed
- The CLI command now requires that if `--randomize` is not set, both `x` and `y` values must be provided explicitly.

### Fixed
- Minor error handling improvements in the CLI store command.

---

