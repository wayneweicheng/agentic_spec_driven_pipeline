# Spec Export Tools - Quick Reference

Deterministic (non-LLM) tools to convert `spec.json` to human-readable formats for business review and approval.

## Available Tools

| Tool | Output | Best For |
|------|--------|----------|
| `spec_to_excel.py` | Single .xlsx file | Business stakeholder review, formatted documentation |
| `spec_to_csv.py` | Multiple .csv files | Version control diffs, programmatic processing |
| `spec_to_diagram.py` | Mermaid diagrams | Visual data flow, architecture documentation |
| `export_spec.sh` | All formats at once | Quick export for review packages |

## Quick Start

### Install Dependencies

```bash
pip install -e .
```

Or just the required package:

```bash
pip install openpyxl>=3.1.0
```

### Generate All Formats

```bash
# From project root
./src/agentic_spec_pipeline/tools/export_spec.sh examples/technical_requirements/spec.json

# Or individually
python3 src/agentic_spec_pipeline/tools/spec_to_excel.py examples/technical_requirements/spec.json review.xlsx
python3 src/agentic_spec_pipeline/tools/spec_to_csv.py examples/technical_requirements/spec.json review_csv/
python3 src/agentic_spec_pipeline/tools/spec_to_diagram.py examples/technical_requirements/spec.json diagram.md
```

## Output Examples

### Excel Workbook (`review.xlsx`)

Multi-sheet workbook with:
- **Overview**: All models summary table
- **Schema Config**: Schema configuration
- **1. stg_customers, 2. stg_orders, ...**: Individual model sheets with:
  - Column mappings with transformations
  - Aggregations
  - Join definitions
  - Filters and constraints
- **All Columns**: Consolidated data dictionary
- **Data Lineage**: Dependencies and downstream usage

Perfect for: Sharing with business stakeholders, documentation, Confluence/SharePoint

### CSV Files (`review_csv/`)

Multiple focused CSV files:
```
00_overview.csv          - Quick model inventory
01_all_columns.csv       - Complete data dictionary
02_all_transforms.csv    - All transformation logic
03_all_joins.csv         - Join definitions
04_all_tests.csv         - Data quality tests
05_data_lineage.csv      - Dependencies
model_*.csv              - Individual model details
```

Perfect for: Version control, automated processing, change tracking

### Mermaid Diagrams (`diagram.md`)

Visual data flow diagrams:
- High-level pipeline flow (raw → staging → final)
- Detailed model-level diagrams showing:
  - Source tables
  - Join types
  - Output columns

Perfect for: Architecture docs, presentations, GitHub/GitLab wikis

## Why These Tools?

### 100% Deterministic
- No LLM calls = no hallucinations
- Same input always produces same output
- Fully repeatable and testable

### Fast & Accurate
- Instant generation (no API calls)
- Direct JSON transformation
- Zero interpretation errors

### Version Control Friendly
- CSV diffs show exactly what changed
- Diagrams render in GitHub/GitLab
- Can be automated in CI/CD

### Business Ready
- Excel formatting for stakeholder review
- Clear, organized structure
- Professional presentation

## Integration Examples

### Pre-commit Hook

Auto-generate documentation when spec.json changes:

```bash
#!/bin/bash
# .git/hooks/pre-commit
if git diff --cached --name-only | grep -q "spec.json"; then
    echo "Regenerating spec documentation..."
    ./src/agentic_spec_pipeline/tools/export_spec.sh spec.json
    git add *_review.xlsx *_csv/ *_diagram.md
fi
```

### GitHub Actions

```yaml
name: Spec Documentation
on:
  push:
    paths: ['**/spec.json']
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install openpyxl
      - name: Generate documentation
        run: |
          python3 src/agentic_spec_pipeline/tools/spec_to_excel.py spec.json
          python3 src/agentic_spec_pipeline/tools/spec_to_csv.py spec.json
          python3 src/agentic_spec_pipeline/tools/spec_to_diagram.py spec.json
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: spec-documentation
          path: |
            *_review.xlsx
            *_csv/
            *_diagram.md
```

### Review Workflow

1. **Generate** spec.json using LLM from requirements
2. **Export** to Excel using these tools
3. **Review** with business stakeholders
4. **Approve** and version control
5. **Generate** code from approved spec.json
6. **Regenerate** docs if spec changes

## File Locations

```
src/agentic_spec_pipeline/tools/
├── spec_to_excel.py         # Excel exporter
├── spec_to_csv.py           # CSV exporter
├── spec_to_diagram.py       # Diagram generator
├── export_spec.sh           # Convenience wrapper
└── README_SPEC_EXPORT.md    # Detailed documentation
```

## Viewing Outputs

### Excel
- Open in Microsoft Excel, Google Sheets, LibreOffice
- All sheets are formatted and ready to share

### CSV
- Open in any spreadsheet app
- Great for version control diffs
- Easy to process programmatically

### Mermaid Diagrams
- Auto-render in GitHub/GitLab
- VS Code: Install Mermaid Preview extension
- Online: Paste into https://mermaid.live

## Testing

All tools have been tested with the example spec:

```bash
# Test Excel export
python3 src/agentic_spec_pipeline/tools/spec_to_excel.py examples/technical_requirements/spec.json

# Test CSV export
python3 src/agentic_spec_pipeline/tools/spec_to_csv.py examples/technical_requirements/spec.json

# Test diagram export
python3 src/agentic_spec_pipeline/tools/spec_to_diagram.py examples/technical_requirements/spec.json
```

All tests passed! ✓

## Next Steps

1. **Review** the generated outputs from your spec.json
2. **Share** the Excel file with stakeholders
3. **Commit** CSV files to version control
4. **Add** diagrams to your documentation
5. **Automate** using the shell wrapper or CI/CD

## Support

For detailed usage and troubleshooting, see:
- [README_SPEC_EXPORT.md](src/agentic_spec_pipeline/tools/README_SPEC_EXPORT.md)

For issues or questions, check the main project README.
