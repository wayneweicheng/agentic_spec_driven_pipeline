#!/usr/bin/env python3
"""
Converts spec.json to HTML with embedded Mermaid diagrams for easy browser viewing.
No server required - generates a standalone HTML file.

Usage:
    python spec_to_html.py <spec.json> [output.html]

Example:
    python spec_to_html.py examples/technical_requirements/spec.json
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict


class SpecToHTMLConverter:
    """Converts spec.json to standalone HTML with embedded Mermaid diagrams."""

    def __init__(self, spec_path: str):
        """Initialize converter with spec file path."""
        self.spec_path = Path(spec_path)
        with open(self.spec_path, 'r') as f:
            self.spec = json.load(f)

    def convert(self, output_path: str) -> None:
        """Main conversion method - creates standalone HTML."""
        html = self._generate_html()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✓ HTML file created: {output_path}")
        print(f"\nTo view:")
        print(f"  • Open {output_path} in any web browser")
        print(f"  • Diagrams will render automatically (uses mermaid.js CDN)")

    def _generate_toc_items(self, models) -> str:
        """Generate table of contents items for models."""
        items = []
        for i, model in enumerate(models):
            name = model.get("name", "Unknown")
            items.append(f'                        <li><a href="#model-{i}">{name}</a></li>')
        return '\n'.join(items)

    def _generate_html(self) -> str:
        """Generate complete HTML document."""
        models = self.spec.get('models', [])

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Pipeline Specification - {self.spec_path.stem}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        h1 {{
            color: #1a1a1a;
            font-size: 2.5em;
            margin-bottom: 10px;
            border-bottom: 4px solid #366092;
            padding-bottom: 10px;
        }}

        h2 {{
            color: #366092;
            font-size: 1.8em;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-bottom: 8px;
            border-bottom: 2px solid #dce6f1;
        }}

        h3 {{
            color: #555;
            font-size: 1.3em;
            margin-top: 30px;
            margin-bottom: 15px;
        }}

        .metadata {{
            background: #f8f9fa;
            padding: 15px 20px;
            border-radius: 4px;
            margin-bottom: 30px;
            border-left: 4px solid #366092;
        }}

        .metadata p {{
            margin: 5px 0;
        }}

        .metadata strong {{
            color: #366092;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}

        thead {{
            background: #366092;
            color: white;
        }}

        th {{
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}

        td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }}

        tbody tr:hover {{
            background: #f8f9fa;
        }}

        .diagram-container {{
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
            border: 1px solid #e0e0e0;
        }}

        .model-section {{
            background: #fafafa;
            padding: 25px;
            margin: 30px 0;
            border-radius: 6px;
            border-left: 4px solid #4caf50;
        }}

        .layer-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
            margin-left: 10px;
        }}

        .layer-staging {{
            background: #bbdefb;
            color: #01579b;
        }}

        .layer-final {{
            background: #c8e6c9;
            color: #2e7d32;
        }}

        code {{
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
        }}

        pre {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            border-left: 4px solid #366092;
        }}

        .toc {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 4px;
            margin-bottom: 30px;
        }}

        .toc ul {{
            list-style: none;
            padding-left: 20px;
        }}

        .toc li {{
            margin: 8px 0;
        }}

        .toc a {{
            color: #366092;
            text-decoration: none;
            font-weight: 500;
        }}

        .toc a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Data Pipeline Specification</h1>

        <div class="metadata">
            <p><strong>Source File:</strong> <code>{self.spec_path.name}</code></p>
            <p><strong>Total Models:</strong> {len(models)}</p>
            <p><strong>Generated:</strong> <span id="timestamp"></span></p>
        </div>

        <nav class="toc">
            <h3>Table of Contents</h3>
            <ul>
                <li><a href="#overview">Overview</a></li>
                <li><a href="#data-flow">Data Flow Diagram</a></li>
                <li><a href="#models">Models</a>
                    <ul>
{self._generate_toc_items(models)}
                    </ul>
                </li>
            </ul>
        </nav>

        <h2 id="overview">Overview</h2>
        {self._generate_overview_table()}

        <h2 id="data-flow">Data Flow Diagram</h2>
        <div class="diagram-container">
            <pre class="mermaid">
{self._generate_mermaid_flow()}
            </pre>
        </div>

        <h2 id="models">Models</h2>
        {self._generate_model_sections()}

    </div>

    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
        document.getElementById('timestamp').textContent = new Date().toLocaleString();
    </script>
</body>
</html>
"""
        return html

    def _generate_overview_table(self) -> str:
        """Generate overview table HTML."""
        rows = []
        for model in self.spec.get('models', []):
            layer = model.get('layer', '')
            badge_class = f'layer-{layer}' if layer else ''
            total_cols = len(model.get('column_mapping', [])) + len(model.get('aggregations', []) or [])

            rows.append(f"""
            <tr>
                <td><strong>{model.get('name', '')}</strong></td>
                <td><span class="layer-badge {badge_class}">{layer}</span></td>
                <td>{', '.join(model.get('sources', []))}</td>
                <td>{total_cols}</td>
                <td>{'Yes' if model.get('joins') else 'No'}</td>
                <td>{'Yes' if model.get('aggregations') else 'No'}</td>
            </tr>
            """)

        return f"""
        <table>
            <thead>
                <tr>
                    <th>Model Name</th>
                    <th>Layer</th>
                    <th>Source Tables</th>
                    <th>Columns</th>
                    <th>Has Joins</th>
                    <th>Has Aggregations</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """

    def _generate_mermaid_flow(self) -> str:
        """Generate Mermaid data flow diagram."""
        lines = ["graph TD"]

        raw_sources = set()
        for model in self.spec.get('models', []):
            for source in model.get('sources', []):
                if source.startswith('raw.'):
                    raw_sources.add(source)

        # Define nodes
        for source in sorted(raw_sources):
            safe_id = source.replace('.', '_').replace('-', '_')
            lines.append(f"    {safe_id}[({source})]:::rawSource")

        for model in self.spec.get('models', []):
            name = model.get('name', '')
            layer = model.get('layer', '')
            safe_id = name.replace('.', '_').replace('-', '_')

            if layer == 'staging':
                lines.append(f"    {safe_id}[[{name}]]:::staging")
            elif layer == 'final':
                lines.append(f"    {safe_id}[/{name}/]:::final")

        lines.append("")

        # Add connections
        for model in self.spec.get('models', []):
            model_id = model.get('name', '').replace('.', '_').replace('-', '_')
            for source in model.get('sources', []):
                source_id = source.replace('.', '_').replace('-', '_')
                lines.append(f"    {source_id} --> {model_id}")

        lines.append("")
        lines.append("    classDef rawSource fill:#f9f,stroke:#333,stroke-width:2px")
        lines.append("    classDef staging fill:#bbf,stroke:#333,stroke-width:2px")
        lines.append("    classDef final fill:#bfb,stroke:#333,stroke-width:3px")

        return "\n".join(lines)

    def _generate_model_sections(self) -> str:
        """Generate HTML for all model sections."""
        sections = []

        for i, model in enumerate(self.spec.get('models', [])):
            layer = model.get('layer', '')
            badge_class = f'layer-{layer}' if layer else ''

            sections.append(f"""
        <div class="model-section" id="model-{i}">
            <h3>{model.get('name', 'Unknown')} <span class="layer-badge {badge_class}">{layer}</span></h3>

            <p><strong>Sources:</strong> {', '.join(f'<code>{s}</code>' for s in model.get('sources', []))}</p>

            {self._generate_columns_table(model) if model.get('column_mapping') else ''}
            {self._generate_aggregations_table(model) if model.get('aggregations') else ''}
            {self._generate_joins_table(model) if model.get('joins') else ''}
        </div>
            """)

        return ''.join(sections)

    def _generate_columns_table(self, model: Dict[str, Any]) -> str:
        """Generate columns table for a model."""
        rows = []
        for col in model.get('column_mapping', []):
            transform = col.get('transform', '') or ''
            transform_display = f'<code>{transform[:100]}...</code>' if len(transform) > 100 else f'<code>{transform}</code>' if transform else ''

            rows.append(f"""
            <tr>
                <td><strong>{col.get('target_column', '')}</strong></td>
                <td>{col.get('type', '')}</td>
                <td><code>{col.get('from_table', '')}.{col.get('from_column', '')}</code></td>
                <td>{transform_display}</td>
                <td>{col.get('description', '') or ''}</td>
            </tr>
            """)

        return f"""
        <h4>Columns</h4>
        <table>
            <thead>
                <tr>
                    <th>Column</th>
                    <th>Type</th>
                    <th>Source</th>
                    <th>Transform</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """

    def _generate_aggregations_table(self, model: Dict[str, Any]) -> str:
        """Generate aggregations table for a model."""
        rows = []
        for agg in model.get('aggregations', []):
            rows.append(f"""
            <tr>
                <td><strong>{agg.get('metric_column', '')}</strong></td>
                <td>{agg.get('type', '')}</td>
                <td><code>{agg.get('formula', '')}</code></td>
                <td>{agg.get('description', '') or ''}</td>
            </tr>
            """)

        return f"""
        <h4>Aggregations</h4>
        <table>
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Type</th>
                    <th>Formula</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """

    def _generate_joins_table(self, model: Dict[str, Any]) -> str:
        """Generate joins table for a model."""
        rows = []
        for join in model.get('joins', []):
            rows.append(f"""
            <tr>
                <td><code>{join.get('left_table', '')}</code></td>
                <td><code>{join.get('right_table', '')}</code></td>
                <td>{join.get('type', '')}</td>
                <td><code>{join.get('condition', '')}</code></td>
            </tr>
            """)

        return f"""
        <h4>Joins</h4>
        <table>
            <thead>
                <tr>
                    <th>Left Table</th>
                    <th>Right Table</th>
                    <th>Type</th>
                    <th>Condition</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python spec_to_html.py <spec.json> [output.html]")
        print("\nExample:")
        print("  python spec_to_html.py examples/technical_requirements/spec.json")
        sys.exit(1)

    spec_path = sys.argv[1]

    if not Path(spec_path).exists():
        print(f"Error: File not found: {spec_path}")
        sys.exit(1)

    # Default output to examples/human_review/ directory
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        spec_file = Path(spec_path)
        if 'examples' in spec_file.parts:
            output_dir = Path('examples/human_review')
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{spec_file.stem}_review.html"
        else:
            output_path = Path(spec_path).stem + "_review.html"

    try:
        converter = SpecToHTMLConverter(spec_path)
        converter.convert(output_path)
        print(f"\n✓ Successfully converted {spec_path}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
