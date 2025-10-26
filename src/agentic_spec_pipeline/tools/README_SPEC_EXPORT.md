# Spec Export Tools

Deterministic (non-LLM) tools to convert `spec.json` to human-readable formats for business review and approval.

## Overview

These tools transform the structured JSON specification into formats that business owners can easily review:
- **Excel** (.xlsx) - Multi-sheet workbook with formatted tables
- **CSV** - Multiple CSV files for different views

Both tools are:
- **Deterministic**: Same input always produces same output
- **Fast**: No LLM calls, pure data transformation
- **Accurate**: Direct mapping from JSON structure
- **Version-controllable**: Outputs can be committed and diffed

## Installation

The required dependency is included in the project:

```bash
pip install -e .
```

Or install just openpyxl:

```bash
pip install openpyxl>=3.1.0
```

## Usage

### Excel Export

```bash
# Basic usage
python src/agentic_spec_pipeline/tools/spec_to_excel.py examples/technical_requirements/spec.json

# Custom output path
python src/agentic_spec_pipeline/tools/spec_to_excel.py examples/technical_requirements/spec.json review.xlsx
```

**Output**: Single Excel workbook with multiple sheets:
- **Overview**: Summary of all models
- **Schema Config**: Schema configuration
- **1. stg_customers**, **2. stg_orders**, etc.: Detailed model sheets
- **All Columns**: Consolidated view of all columns
- **Data Lineage**: Dependencies and downstream usage

### CSV Export

```bash
# Basic usage
python src/agentic_spec_pipeline/tools/spec_to_csv.py examples/technical_requirements/spec.json

# Custom output directory
python src/agentic_spec_pipeline/tools/spec_to_csv.py examples/technical_requirements/spec.json ./review_csv/
```

**Output**: Directory with multiple CSV files:
- `00_overview.csv` - Models summary
- `01_all_columns.csv` - All columns across models
- `02_all_transforms.csv` - All transformation logic
- `03_all_joins.csv` - All join definitions
- `04_all_tests.csv` - All data quality tests
- `05_data_lineage.csv` - Dependencies
- `model_*.csv` - Individual model details

## Use Cases

### Business Review
1. Generate Excel from approved spec.json
2. Share with business stakeholders
3. Collect feedback/approvals
4. Update spec.json based on feedback
5. Regenerate for final approval

### Documentation
- CSV files can be committed to git for diffing
- Excel provides formatted documentation
- Easy to include in Confluence/SharePoint

### Change Management
```bash
# Before changes
python spec_to_excel.py spec.json before_changes.xlsx

# After changes
python spec_to_excel.py spec.json after_changes.xlsx

# Compare in Excel or version control
```

## Output Details

### Excel Workbook Structure

#### Overview Sheet
| Model Name | Layer | Source Tables | Target Columns | Has Joins | Has Aggregations |
|------------|-------|---------------|----------------|-----------|------------------|
| stg_customers | staging | raw.crm_customers, raw.crm_addresses | 9 | Yes | No |

#### Model Sheets
Each model gets a detailed sheet with:
- **Column Mappings**: All column transformations
- **Aggregations**: Aggregation logic (if applicable)
- **Joins**: Join definitions
- **Filters**: Filter predicates
- **Constraints**: Primary keys, partitions, etc.

#### All Columns Sheet
Consolidated view of every column across all models with full lineage.

#### Data Lineage Sheet
Shows dependencies between models (upstream sources and downstream consumers).

### CSV Files

Each CSV is designed for a specific review purpose:
- **Overview**: Quick model inventory
- **All Columns**: Complete data dictionary
- **Transforms**: Review transformation logic
- **Joins**: Validate join logic
- **Tests**: Review data quality rules
- **Lineage**: Understand dependencies

## Why Deterministic?

Using structured transformation (no LLM) ensures:
1. **Repeatability**: Same spec always produces same output
2. **Speed**: Instant generation
3. **Accuracy**: No hallucinations or interpretation errors
4. **Trust**: Business can rely on exact representation
5. **Automation**: Can be integrated into CI/CD pipelines

## Integration Examples

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit
if git diff --cached --name-only | grep -q "spec.json"; then
    python src/agentic_spec_pipeline/tools/spec_to_excel.py spec.json docs/spec_review.xlsx
    git add docs/spec_review.xlsx
fi
```

### CI/CD Pipeline
```yaml
# .github/workflows/spec-docs.yml
name: Generate Spec Documentation
on:
  push:
    paths:
      - '**.json'
jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Generate Excel
        run: |
          python src/agentic_spec_pipeline/tools/spec_to_excel.py spec.json
          python src/agentic_spec_pipeline/tools/spec_to_csv.py spec.json
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: spec-documentation
          path: |
            *.xlsx
            *_csv/
```

## Troubleshooting

### Import Error: No module named 'openpyxl'
```bash
pip install openpyxl
```

### File Not Found
Ensure you're providing the correct path to spec.json:
```bash
# Use absolute or relative path
python spec_to_excel.py ./examples/technical_requirements/spec.json
```

### Permission Denied on Output
Ensure the output directory is writable and the file isn't open in Excel.

## Future Enhancements

Potential additions (all deterministic):
- [ ] Diagram generation (Mermaid, GraphViz)
- [ ] Markdown documentation
- [ ] HTML report with interactive tables
- [ ] PDF generation
- [ ] Schema comparison tool (diff two specs)
