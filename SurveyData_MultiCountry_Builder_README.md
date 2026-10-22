# Multi-country survey workbook builder

This document describes how to run `prepare_multicountry_workbook.mjs` without changing the existing `SurveyData_DE_US.xlsx` workbook.

## Prerequisites

- Node.js with ES modules and the `@oai/artifact-tool` module available to the builder.
- Python 3 with `pandas` for reading the pooled Stata file.
- The external respondent-level `ZA10020_v2-0-0.dta` file (Release 2.0.0). The data file is not stored in this repository; provide its path at run time.

The successful build in the current workspace used Node.js 24.19.0, `@oai/artifact-tool` 2.8.99, and Python 3 with pandas 2.2.3. These are observed runtime versions, not project pins. The repository has no package manifest, lockfile, or Python dependency file for this builder. Make the approved artifact-tool runtime available through normal Node resolution or `NODE_PATH`; use `--python` if `python3` or `$PYTHON` does not identify the intended Python executable. No package installation is performed by the builder.

## Run from the repository root

Supply the DTA path explicitly. Absolute paths avoid ambiguity; relative `--data` and `--output` paths resolve from the current working directory.

```sh
cd /path/to/LLM-Project
NODE_PATH=/path/to/node_modules \
  node prepare_multicountry_workbook.mjs \
  --data /path/to/ZA10020_v2-0-0.dta \
  --output /path/to/new/SurveyData_MultiCountry.xlsx \
  --python /path/to/python3
```

Omit `--output` to target `SurveyData_MultiCountry.xlsx` beside the builder. That default is separate from `SurveyData_DE_US.xlsx`. The builder refuses an existing destination and has no overwrite option; choose a new filename or destination for each run. The output is copied into place exclusively after source checks, export validation, and rendering succeed.

The builder creates its temporary XLSX and sheet previews in a unique system temporary directory and removes that directory on success or failure. Any `.inspect.ndjson` sidecar emitted by the artifact-tool during export or validation is contained there and removed with the temporary directory. The selected output workbook is the only persistent output.

## What it validates and preserves

The builder keeps the six-country sample policy, eight item mappings, original codes and labels, unweighted percentages, and both Q10d denominator views. It checks source counts and item labels, Canada’s exact `INTLANG == "eng (English)"` filter, the German Q10d routing discrepancy, Q1 × v26 margins (including system-missing categories), count reconciliation, and substantive denominators. After export it reopens the XLSX and compares every generated table cell—including raw counts, denominators, and percentages—with the corresponding calculated source table before copying the file to the requested destination. Existing project reference inputs are hash-checked; the local P2 audit files are not read or required.

The workbook remains unweighted. This builder does not resolve the Q10d primary denominator decision or survey-weight documentation.
