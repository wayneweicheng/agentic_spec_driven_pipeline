#!/usr/bin/env python3
"""
Deterministic spec.json to Mermaid diagram converter.
Generates data flow diagrams in Mermaid syntax for easy visualization.

Usage:
    python spec_to_diagram.py <spec.json> [output.md]

Example:
    python spec_to_diagram.py examples/technical_requirements/spec.json diagram.md

The generated Mermaid diagram can be:
- Viewed in GitHub/GitLab (automatic rendering)
- Rendered in VS Code with Mermaid extension
- Converted to PNG/SVG using Mermaid CLI
- Embedded in documentation
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set


class SpecToDiagramConverter:
    """Converts spec.json to Mermaid diagram for data flow visualization."""

    def __init__(self, spec_path: str):
        """Initialize converter with spec file path."""
        self.spec_path = Path(spec_path)
        with open(self.spec_path, 'r') as f:
            self.spec = json.load(f)

    def convert(self, output_path: str) -> None:
        """Main conversion method - creates Mermaid diagram."""
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write title and description
            f.write("# Data Pipeline Specification - Flow Diagram\n\n")
            f.write(f"Generated from: `{self.spec_path.name}`\n\n")

            # Main data flow diagram
            f.write("## Data Flow\n\n")
            f.write("```mermaid\n")
            f.write(self._generate_data_flow())
            f.write("```\n\n")

            # Individual model diagrams
            for model in self.spec.get('models', []):
                if model.get('column_mapping') or model.get('aggregations'):
                    f.write(f"## Model: {model.get('name', 'Unknown')}\n\n")
                    f.write("```mermaid\n")
                    f.write(self._generate_model_diagram(model))
                    f.write("```\n\n")

        print(f"✓ Mermaid diagram created: {output_path}")
        print(f"\nTo view:")
        print(f"  • Open in GitHub/GitLab (auto-renders)")
        print(f"  • Use VS Code Mermaid extension")
        print(f"  • Use https://mermaid.live for online rendering")

    def _generate_data_flow(self) -> str:
        """Generate high-level data flow diagram."""
        lines = ["graph TD\n"]

        # Track all sources and models
        raw_sources: Set[str] = set()
        staging_models: List[str] = []
        final_models: List[str] = []

        for model in self.spec.get('models', []):
            model_name = model.get('name', '')
            layer = model.get('layer', '')

            if layer == 'staging':
                staging_models.append(model_name)
            elif layer == 'final':
                final_models.append(model_name)

            # Collect raw sources
            for source in model.get('sources', []):
                if source.startswith('raw.'):
                    raw_sources.add(source)

        # Define raw sources
        for source in sorted(raw_sources):
            safe_id = self._sanitize_id(source)
            lines.append(f"    {safe_id}[({source})]:::rawSource\n")

        # Define staging models
        for model in staging_models:
            safe_id = self._sanitize_id(model)
            lines.append(f"    {safe_id}[[{model}]]:::staging\n")

        # Define final models
        for model in final_models:
            safe_id = self._sanitize_id(model)
            lines.append(f"    {safe_id}[/{model}/]:::final\n")

        lines.append("\n")

        # Add connections
        for model in self.spec.get('models', []):
            model_name = model.get('name', '')
            model_id = self._sanitize_id(model_name)

            for source in model.get('sources', []):
                source_id = self._sanitize_id(source)
                # Only show if source exists as a node
                if source.startswith('raw.') or any(m.get('name') == source for m in self.spec.get('models', [])):
                    lines.append(f"    {source_id} --> {model_id}\n")

        # Styling
        lines.append("\n")
        lines.append("    classDef rawSource fill:#f9f,stroke:#333,stroke-width:2px\n")
        lines.append("    classDef staging fill:#bbf,stroke:#333,stroke-width:2px\n")
        lines.append("    classDef final fill:#bfb,stroke:#333,stroke-width:3px\n")

        return "".join(lines)

    def _generate_model_diagram(self, model: Dict[str, Any]) -> str:
        """Generate detailed diagram for a single model."""
        lines = ["graph LR\n"]

        model_name = model.get('name', 'Unknown')
        sources = model.get('sources', [])

        # Source tables
        for idx, source in enumerate(sources, 1):
            safe_id = self._sanitize_id(f"{source}_src")
            lines.append(f"    SRC{idx}[{source}]:::source\n")

        # Model node
        lines.append(f"    MODEL[{model_name}]:::model\n")

        # Target columns
        all_columns = []

        # From column mappings
        for col_map in model.get('column_mapping', []):
            col_name = col_map.get('target_column', '')
            if col_name:
                all_columns.append(col_name)

        # From aggregations
        for agg in model.get('aggregations', []) or []:
            col_name = agg.get('metric_column', '')
            if col_name:
                all_columns.append(col_name)

        # Show key columns (up to 10)
        display_cols = all_columns[:10]
        if len(all_columns) > 10:
            display_cols.append(f"... +{len(all_columns) - 10} more")

        if display_cols:
            lines.append(f"    OUT[{model_name}<br/>")
            for col in display_cols:
                lines.append(f"• {col}<br/>")
            lines[-1] = lines[-1].rstrip('<br/>')  # Remove last break
            lines.append("]:::output\n")

        lines.append("\n")

        # Connections
        for idx in range(1, len(sources) + 1):
            lines.append(f"    SRC{idx} -->|")

            # Show join type if available
            joins = model.get('joins', [])
            if joins and idx <= len(joins):
                join_type = joins[idx - 1].get('type', 'JOIN')
                lines.append(f"{join_type}| MODEL\n")
            else:
                lines.append("| MODEL\n")

        if display_cols:
            lines.append("    MODEL --> OUT\n")

        # Styling
        lines.append("\n")
        lines.append("    classDef source fill:#e1f5ff,stroke:#01579b,stroke-width:2px\n")
        lines.append("    classDef model fill:#fff9c4,stroke:#f57f17,stroke-width:3px\n")
        lines.append("    classDef output fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px\n")

        return "".join(lines)

    def _sanitize_id(self, name: str) -> str:
        """Sanitize name for use as Mermaid node ID."""
        # Replace dots, hyphens, and special chars with underscores
        return name.replace('.', '_').replace('-', '_').replace(' ', '_')


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python spec_to_diagram.py <spec.json> [output.md]")
        print("\nExample:")
        print("  python spec_to_diagram.py examples/technical_requirements/spec.json")
        print("  python spec_to_diagram.py examples/technical_requirements/spec.json custom_diagram.md")
        sys.exit(1)

    spec_path = sys.argv[1]

    if not Path(spec_path).exists():
        print(f"Error: File not found: {spec_path}")
        sys.exit(1)

    # Default output to examples/human_review/ directory
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        # Use examples/human_review/ if the spec is in examples/
        spec_file = Path(spec_path)
        if 'examples' in spec_file.parts:
            output_dir = Path('examples/human_review')
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{spec_file.stem}_diagram.md"
        else:
            output_path = Path(spec_path).stem + "_diagram.md"

    try:
        converter = SpecToDiagramConverter(spec_path)
        converter.convert(output_path)
        print(f"\n✓ Successfully converted {spec_path}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
