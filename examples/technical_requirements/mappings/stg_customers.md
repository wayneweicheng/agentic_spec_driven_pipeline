# Model: stg_customers (layer: staging)

Sources: raw.crm_customers, raw.crm_addresses

## Column mapping

| target_column | type | from_table | from_column | transform | nullable | tests | description |
|---------------|------|------------|-------------|-----------|----------|-------|-------------|
| customer_id | INT64 | crm_customers | customer_id |  | False | not_null,unique | Primary business key |
| email | STRING | crm_customers | email | LOWER(TRIM({from})) | False | not_null | Standardized email |
| phone_e164 | STRING | crm_customers | phone | CASE WHEN REGEXP_CONTAINS(REGEXP_REPLACE({from}, '[^0-9]', ''), r'^1?[0-9]{10}$') THEN CONCAT('+1', RIGHT(REGEXP_REPLACE({from}, '[^0-9]', ''), 10)) WHEN REGEXP_CONTAINS(REGEXP_REPLACE({from}, '[^0-9]', ''), r'^[0-9]{11,15}$') THEN CONCAT('+', REGEXP_REPLACE({from}, '[^0-9]', '')) ELSE NULL END | True |  | Normalized phone |
| lifecycle_stage | STRING | crm_customers | status | CASE WHEN {from} = 'active' THEN 'active' WHEN {from} = 'inactive' THEN 'churned' WHEN {from} = 'trial' THEN 'trial' WHEN {from} = 'prospect' THEN 'prospect' ELSE 'unknown' END | False | accepted_values(...) | Standardized lifecycle |
| country | STRING | crm_addresses | country |  | True |  | Country from best address |
| city | STRING | crm_addresses | city |  | True |  | City |
| state | STRING | crm_addresses | state |  | True |  | State |
| postal_code | STRING | crm_addresses | postal_code |  | True |  | Postal code |
| created_at | TIMESTAMP | crm_customers | created_at |  | False | not_null | Ingestion baseline |

## Joins

| left_table | right_table | type | condition |
|------------|-------------|------|-----------|
| crm_customers | crm_addresses | LEFT | crm_customers.customer_id = crm_addresses.customer_id |

## Filters

| applies_to | predicate | rationale |
|------------|-----------|-----------|
| crm_addresses | country IS NOT NULL | drop incomplete addresses |

## Output constraints

| primary_key | partition_by | cluster_by |
|-------------|--------------|------------|
| customer_id |  |  |
