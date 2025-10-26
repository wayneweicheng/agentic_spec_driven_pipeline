#!/usr/bin/env python3
"""
Deterministic spec.json to CSV converter.
Creates multiple CSV files for different views of the specification.

Usage:
    python spec_to_csv.py <spec.json> [output_directory]

Example:
    python spec_to_csv.py examples/technical_requirements/spec.json ./review_csv/
"""

import json
import csv
import sys
from pathlib import Path
from typing import Any, Dict, List


class SpecToCSVConverter:
    """Converts spec.json to multiple CSV files for business review."""

    def __init__(self, spec_path: str):
        """Initialize converter with spec file path."""
        self.spec_path = Path(spec_path)
        with open(self.spec_path, 'r') as f:
            self.spec = json.load(f)

    def convert(self, output_dir: str) -> None:
        """Main conversion method - creates all CSV files."""
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        self._create_overview_csv(out_path)
        self._create_all_columns_csv(out_path)
        self._create_all_transforms_csv(out_path)
        self._create_all_joins_csv(out_path)
        self._create_all_tests_csv(out_path)
        self._create_data_lineage_csv(out_path)

        # Create individual model CSVs
        for model in self.spec.get('models', []):
            self._create_model_csv(model, out_path)

        print(f"\n✓ CSV files created in: {output_dir}")

    def _create_overview_csv(self, out_path: Path) -> None:
        """Create models overview CSV."""
        filepath = out_path / "00_overview.csv"

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(["Model Name", "Layer", "Source Tables", "Total Columns",
                           "Has Joins", "Has Aggregations", "Primary Key"])

            # Data rows
            for model in self.spec.get('models', []):
                total_cols = len(model.get('column_mapping', [])) + len(model.get('aggregations', []) or [])
                writer.writerow([
                    model.get('name', ''),
                    model.get('layer', ''),
                    ', '.join(model.get('sources', [])),
                    total_cols,
                    'Yes' if model.get('joins') else 'No',
                    'Yes' if model.get('aggregations') else 'No',
                    model.get('constraints', {}).get('primary_key', '')
                ])

        print(f"  ✓ {filepath.name}")

    def _create_all_columns_csv(self, out_path: Path) -> None:
        """Create consolidated columns CSV."""
        filepath = out_path / "01_all_columns.csv"

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(["Model", "Layer", "Column Name", "Type", "Source Table",
                           "Source Column", "Transform", "Nullable", "Tests", "Description"])

            # Data rows
            for model in self.spec.get('models', []):
                model_name = model.get('name', '')
                layer = model.get('layer', '')

                # Column mappings
                for col_map in model.get('column_mapping', []):
                    writer.writerow([
                        model_name,
                        layer,
                        col_map.get('target_column', ''),
                        col_map.get('type', ''),
                        col_map.get('from_table', ''),
                        col_map.get('from_column', ''),
                        col_map.get('transform', '') or 'None',
                        'Yes' if col_map.get('nullable') else 'No',
                        ', '.join(col_map.get('tests', [])),
                        col_map.get('description', '') or ''
                    ])

                # Aggregations
                for agg in model.get('aggregations', []) or []:
                    writer.writerow([
                        model_name,
                        layer,
                        agg.get('metric_column', ''),
                        agg.get('type', ''),
                        'AGGREGATION',
                        '',
                        agg.get('formula', ''),
                        '',
                        ', '.join(agg.get('tests', [])),
                        agg.get('description', '') or ''
                    ])

        print(f"  ✓ {filepath.name}")

    def _create_all_transforms_csv(self, out_path: Path) -> None:
        """Create CSV focusing on transformations."""
        filepath = out_path / "02_all_transforms.csv"

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(["Model", "Column", "Type", "Transform Logic", "Description"])

            # Data rows - only columns with transforms
            for model in self.spec.get('models', []):
                model_name = model.get('name', '')

                for col_map in model.get('column_mapping', []):
                    transform = col_map.get('transform')
                    if transform:
                        writer.writerow([
                            model_name,
                            col_map.get('target_column', ''),
                            'Column Transform',
                            transform,
                            col_map.get('description', '') or ''
                        ])

                for agg in model.get('aggregations', []) or []:
                    writer.writerow([
                        model_name,
                        agg.get('metric_column', ''),
                        'Aggregation',
                        agg.get('formula', ''),
                        agg.get('description', '') or ''
                    ])

        print(f"  ✓ {filepath.name}")

    def _create_all_joins_csv(self, out_path: Path) -> None:
        """Create CSV with all join definitions."""
        filepath = out_path / "03_all_joins.csv"

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(["Model", "Layer", "Left Table", "Right Table",
                           "Join Type", "Join Condition"])

            # Data rows
            for model in self.spec.get('models', []):
                model_name = model.get('name', '')
                layer = model.get('layer', '')

                for join in model.get('joins', []):
                    writer.writerow([
                        model_name,
                        layer,
                        join.get('left_table', ''),
                        join.get('right_table', ''),
                        join.get('type', ''),
                        join.get('condition', '')
                    ])

        print(f"  ✓ {filepath.name}")

    def _create_all_tests_csv(self, out_path: Path) -> None:
        """Create CSV with all data quality tests."""
        filepath = out_path / "04_all_tests.csv"

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(["Model", "Layer", "Column", "Test Type", "Description"])

            # Data rows
            for model in self.spec.get('models', []):
                model_name = model.get('name', '')
                layer = model.get('layer', '')

                # Column tests
                for col_map in model.get('column_mapping', []):
                    col_name = col_map.get('target_column', '')
                    for test in col_map.get('tests', []):
                        writer.writerow([
                            model_name,
                            layer,
                            col_name,
                            test,
                            col_map.get('description', '') or ''
                        ])

                # Aggregation tests
                for agg in model.get('aggregations', []) or []:
                    col_name = agg.get('metric_column', '')
                    for test in agg.get('tests', []):
                        writer.writerow([
                            model_name,
                            layer,
                            col_name,
                            test,
                            agg.get('description', '') or ''
                        ])

        print(f"  ✓ {filepath.name}")

    def _create_data_lineage_csv(self, out_path: Path) -> None:
        """Create data lineage CSV."""
        filepath = out_path / "05_data_lineage.csv"

        # Build dependency map
        model_names = {m['name'] for m in self.spec.get('models', [])}
        downstream_map = {name: [] for name in model_names}

        for model in self.spec.get('models', []):
            for source in model.get('sources', []):
                for potential_upstream in model_names:
                    if potential_upstream in source:
                        downstream_map[potential_upstream].append(model['name'])

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(["Model", "Layer", "Depends On (Sources)", "Used By (Downstream)"])

            # Data rows
            for model in self.spec.get('models', []):
                model_name = model.get('name', '')
                writer.writerow([
                    model_name,
                    model.get('layer', ''),
                    ', '.join(model.get('sources', [])),
                    ', '.join(sorted(set(downstream_map.get(model_name, []))))
                ])

        print(f"  ✓ {filepath.name}")

    def _create_model_csv(self, model: Dict[str, Any], out_path: Path) -> None:
        """Create detailed CSV for individual model."""
        model_name = model.get('name', 'unknown')
        # Sanitize filename
        safe_name = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in model_name)
        filepath = out_path / f"model_{safe_name}.csv"

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Model metadata
            writer.writerow(["MODEL", model_name])
            writer.writerow(["Layer", model.get('layer', '')])
            writer.writerow(["Sources", ', '.join(model.get('sources', []))])
            writer.writerow([])

            # Column mappings
            if model.get('column_mapping'):
                writer.writerow(["COLUMN MAPPINGS"])
                writer.writerow(["Target Column", "Type", "From Table", "From Column",
                               "Transform", "Nullable", "Tests", "Description"])

                for col_map in model['column_mapping']:
                    writer.writerow([
                        col_map.get('target_column', ''),
                        col_map.get('type', ''),
                        col_map.get('from_table', ''),
                        col_map.get('from_column', ''),
                        col_map.get('transform', '') or '',
                        'Yes' if col_map.get('nullable') else 'No',
                        ', '.join(col_map.get('tests', [])),
                        col_map.get('description', '') or ''
                    ])
                writer.writerow([])

            # Aggregations
            if model.get('aggregations'):
                writer.writerow(["AGGREGATIONS"])
                writer.writerow(["Metric Column", "Type", "Formula", "Tests", "Description"])

                for agg in model['aggregations']:
                    writer.writerow([
                        agg.get('metric_column', ''),
                        agg.get('type', ''),
                        agg.get('formula', ''),
                        ', '.join(agg.get('tests', [])),
                        agg.get('description', '') or ''
                    ])
                writer.writerow([])

            # Joins
            if model.get('joins'):
                writer.writerow(["JOINS"])
                writer.writerow(["Left Table", "Right Table", "Type", "Condition"])

                for join in model['joins']:
                    writer.writerow([
                        join.get('left_table', ''),
                        join.get('right_table', ''),
                        join.get('type', ''),
                        join.get('condition', '')
                    ])
                writer.writerow([])

            # Filters
            if model.get('filters'):
                writer.writerow(["FILTERS"])
                writer.writerow(["Applies To", "Predicate", "Rationale"])

                for filt in model['filters']:
                    writer.writerow([
                        filt.get('applies_to', ''),
                        filt.get('predicate', ''),
                        filt.get('rationale', '')
                    ])
                writer.writerow([])

            # Constraints
            if model.get('constraints'):
                writer.writerow(["CONSTRAINTS"])
                for key, value in model['constraints'].items():
                    writer.writerow([key, str(value) if value else ''])

        print(f"  ✓ {filepath.name}")


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python spec_to_csv.py <spec.json> [output_directory]")
        print("\nExample:")
        print("  python spec_to_csv.py examples/technical_requirements/spec.json")
        print("  python spec_to_csv.py examples/technical_requirements/spec.json ./custom_csv/")
        sys.exit(1)

    spec_path = sys.argv[1]

    if not Path(spec_path).exists():
        print(f"Error: File not found: {spec_path}")
        sys.exit(1)

    # Default output to examples/human_review/ directory
    if len(sys.argv) >= 3:
        output_dir = sys.argv[2]
    else:
        # Use examples/human_review/ if the spec is in examples/
        spec_file = Path(spec_path)
        if 'examples' in spec_file.parts:
            output_dir = Path('examples/human_review') / f"{spec_file.stem}_csv"
        else:
            output_dir = Path(spec_path).stem + "_csv"

    try:
        converter = SpecToCSVConverter(spec_path)
        converter.convert(output_dir)
        print(f"\n✓ Successfully converted {spec_path}")
        print(f"\nCSV files created:")
        print(f"  • Overview of all models")
        print(f"  • All columns consolidated")
        print(f"  • All transformations")
        print(f"  • All joins")
        print(f"  • All data quality tests")
        print(f"  • Data lineage & dependencies")
        print(f"  • Individual model details")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
