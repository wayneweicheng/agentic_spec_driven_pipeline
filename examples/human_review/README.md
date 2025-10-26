# Human Review Directory

This directory contains **human-readable exports** of the `spec.json` technical specification, generated using deterministic (non-LLM) tools.

## Purpose

The `spec.json` file is a structured, machine-readable specification that drives the entire pipeline code generation. However, it needs to be reviewed and approved by:
- Business stakeholders
- Data analysts
- Product owners
- Technical reviewers

This directory contains the same specification in formats that are easy to review, comment on, and approve.

## Contents

### HTML Interactive Review (`spec_review.html`)
**✨ RECOMMENDED FOR VIEWING ✨**

**Best for: Quick visual review with interactive diagrams**

A standalone HTML file that opens in any web browser with:
- Interactive Mermaid diagrams (auto-rendered)
- Professionally formatted tables
- Table of contents with jump links
- Styled and easy to navigate

**How to view:**
1. Double-click `spec_review.html` to open in your default browser
2. Or right-click → Open With → Your preferred browser
3. No server or internet required (uses CDN for Mermaid rendering)

### Excel Workbook (`spec_review.xlsx`)
**Best for: Business stakeholder review, sharing, and approval**

A professionally formatted Excel workbook with multiple sheets:
- **Overview**: Summary of all data models
- **Schema Config**: Schema/database configuration
- **Individual Model Sheets** (e.g., "1. stg_customers"): Detailed specifications for each model
- **All Columns**: Consolidated data dictionary
- **Data Lineage**: Dependencies and relationships

Open in Microsoft Excel, Google Sheets, or LibreOffice Calc.

### CSV Files Directory (`spec_csv/`)
**Best for: Version control, detailed review, and automated processing**

Multiple CSV files for different aspects:
- `00_overview.csv` - Quick model inventory
- `01_all_columns.csv` - Complete data dictionary
- `02_all_transforms.csv` - All transformation logic
- `03_all_joins.csv` - Join definitions
- `04_all_tests.csv` - Data quality test rules
- `05_data_lineage.csv` - Model dependencies
- `model_*.csv` - Individual model details

### Mermaid Diagram (`spec_diagram.md`)
**Best for: Visual understanding, documentation, and presentations**

Visual data flow diagrams showing:
- High-level pipeline flow (raw → staging → final layers)
- Individual model diagrams with sources and outputs
- Join relationships

**How to view:**
- **In GitHub/GitLab**: Diagrams auto-render when viewing the .md file
- **In VS Code**: Install the "Markdown Preview Mermaid Support" extension
- **Online**: Copy contents and paste into [Mermaid Live Editor](https://mermaid.live)
- **Easier option**: Just open `spec_review.html` in a browser instead!

## Regenerating These Files

These files are automatically generated from `spec.json`. To regenerate:

```bash
# From project root

# Generate all formats at once (recommended)
./src/agentic_spec_pipeline/tools/export_spec.sh examples/technical_requirements/spec.json

# Or generate individually
python3 src/agentic_spec_pipeline/tools/spec_to_html.py examples/technical_requirements/spec.json
python3 src/agentic_spec_pipeline/tools/spec_to_excel.py examples/technical_requirements/spec.json
python3 src/agentic_spec_pipeline/tools/spec_to_csv.py examples/technical_requirements/spec.json
python3 src/agentic_spec_pipeline/tools/spec_to_diagram.py examples/technical_requirements/spec.json
```

## Review Workflow

1. **Generate** `spec.json` from business requirements (using LLM)
2. **Export** to human-readable formats (using these deterministic tools)
3. **Review** the Excel/CSV/diagrams with stakeholders
4. **Collect** feedback and approval
5. **Update** `spec.json` based on feedback
6. **Regenerate** exports for final approval
7. **Version control** the approved spec.json
8. **Generate code** from the approved specification

## Why Multiple Formats?

- **HTML**: Interactive diagrams, easy navigation, works in any browser (no software needed)
- **Excel**: Easy to share with non-technical stakeholders, supports comments and annotations
- **CSV**: Great for line-by-line review, version control diffs, and programmatic validation
- **Diagrams**: Visual understanding of data flow and architecture (also embedded in HTML)

## Version Control

All files in this directory are generated outputs. You can choose to:

### Option 1: Commit Generated Files (Recommended for business review)
- Makes review accessible without running tools
- Stakeholders can download and review immediately
- Diffs show what changed in human terms

### Option 2: Gitignore Generated Files (Recommended for large teams)
- Keep only `spec.json` in version control
- Regenerate on-demand
- Smaller repository size

Add to `.gitignore` if you choose Option 2:
```
examples/human_review/*.xlsx
examples/human_review/spec_csv/
examples/human_review/*.md
```

## Notes

- **Deterministic**: Same `spec.json` always produces identical outputs
- **No LLM**: Pure data transformation, no AI interpretation
- **Accurate**: Direct 1:1 mapping from spec.json structure
- **Fast**: Instant generation, no API calls

## Questions?

See the main tool documentation:
- [Tool Documentation](../../src/agentic_spec_pipeline/tools/README_SPEC_EXPORT.md)
- [Quick Reference](../../SPEC_EXPORT_TOOLS.md)
