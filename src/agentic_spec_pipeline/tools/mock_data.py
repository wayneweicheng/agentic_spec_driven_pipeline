from typing import Dict, List
from faker import Faker

fake = Faker()


def generate_mock_fixtures(ref_tables: List[str], num_rows: int = 5) -> Dict[str, str]:
    """
    Generate minimal CSV fixtures for referenced tables. In a later phase,
    schema will be inferred via BigQuery. For now, emit generic id/value rows.
    Returns a mapping: table_name -> CSV string.
    """
    fixtures: Dict[str, str] = {}
    for table in ref_tables:
        rows = ["id,value"]
        for i in range(num_rows):
            rows.append(f"{i+1},{fake.random_int(min=0, max=1000)}")
        fixtures[table] = "\n".join(rows) + "\n"
    return fixtures
