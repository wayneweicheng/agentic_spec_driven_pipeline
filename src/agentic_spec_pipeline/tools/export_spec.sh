#!/bin/bash
# Convenience wrapper to export spec.json to human-readable formats
# Usage: ./export_spec.sh <spec.json> [format]
#   format: excel, csv, or both (default: both)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPEC_FILE="${1:-examples/technical_requirements/spec.json}"
FORMAT="${2:-both}"

if [ ! -f "$SPEC_FILE" ]; then
    echo "Error: Spec file not found: $SPEC_FILE"
    echo ""
    echo "Usage: $0 <spec.json> [format]"
    echo "  format: excel, csv, diagram, html, or both (default: both)"
    exit 1
fi

SPEC_NAME=$(basename "$SPEC_FILE" .json)

# Check if spec is in examples/ directory
if [[ "$SPEC_FILE" == *"examples/"* ]]; then
    OUTPUT_DIR="examples/human_review"
    mkdir -p "$OUTPUT_DIR"
else
    OUTPUT_DIR=$(dirname "$SPEC_FILE")
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Spec Export Tool"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Input:  $SPEC_FILE"
echo "Format: $FORMAT"
echo ""

if [ "$FORMAT" = "excel" ] || [ "$FORMAT" = "both" ]; then
    OUTPUT_EXCEL="${OUTPUT_DIR}/${SPEC_NAME}_review.xlsx"
    echo "📊 Generating Excel..."
    python3 "$SCRIPT_DIR/spec_to_excel.py" "$SPEC_FILE" "$OUTPUT_EXCEL"
    echo ""
fi

if [ "$FORMAT" = "csv" ] || [ "$FORMAT" = "both" ]; then
    OUTPUT_CSV="${OUTPUT_DIR}/${SPEC_NAME}_csv"
    echo "📋 Generating CSV files..."
    python3 "$SCRIPT_DIR/spec_to_csv.py" "$SPEC_FILE" "$OUTPUT_CSV"
    echo ""
fi

if [ "$FORMAT" = "diagram" ] || [ "$FORMAT" = "both" ]; then
    OUTPUT_DIAGRAM="${OUTPUT_DIR}/${SPEC_NAME}_diagram.md"
    echo "📐 Generating Mermaid diagram..."
    python3 "$SCRIPT_DIR/spec_to_diagram.py" "$SPEC_FILE" "$OUTPUT_DIAGRAM"
    echo ""
fi

if [ "$FORMAT" = "html" ] || [ "$FORMAT" = "both" ]; then
    OUTPUT_HTML="${OUTPUT_DIR}/${SPEC_NAME}_review.html"
    echo "🌐 Generating HTML..."
    python3 "$SCRIPT_DIR/spec_to_html.py" "$SPEC_FILE" "$OUTPUT_HTML"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ Export complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$FORMAT" = "excel" ] || [ "$FORMAT" = "both" ]; then
    echo "Excel:   $OUTPUT_EXCEL"
fi

if [ "$FORMAT" = "csv" ] || [ "$FORMAT" = "both" ]; then
    echo "CSV:     $OUTPUT_CSV/"
fi

if [ "$FORMAT" = "diagram" ] || [ "$FORMAT" = "both" ]; then
    echo "Diagram: $OUTPUT_DIAGRAM"
fi

if [ "$FORMAT" = "html" ] || [ "$FORMAT" = "both" ]; then
    echo "HTML:    $OUTPUT_HTML"
    echo ""
    echo "💡 Tip: Open $OUTPUT_HTML in a browser to view interactive diagrams"
fi