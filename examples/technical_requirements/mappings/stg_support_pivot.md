# Model: stg_support_pivot (layer: staging)

Sources: raw.support_tickets

## Aggregations

| metric_column | type | formula | tests | description |
|---------------|------|---------|-------|-------------|
| open_tickets | INT64 | COUNTIF(status = 'OPEN') |  | Open ticket count per user |
| closed_tickets | INT64 | COUNTIF(status = 'CLOSED') |  | Closed ticket count per user |

## Group by

| group_key |
|-----------|
| customer_id |

## Output constraints

| primary_key | partition_by | cluster_by |
|-------------|--------------|------------|
| customer_id |  |  |
