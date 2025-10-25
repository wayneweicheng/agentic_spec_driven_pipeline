# Model: fact_customer_orders (layer: final)

Sources: stg_orders, stg_support_pivot

## Aggregations

| metric_column | type | formula | tests | description |
|---------------|------|---------|-------|-------------|
| order_count | INT64 | COUNT(*) | not_null | Total orders per customer |
| total_spent_usd | NUMERIC | SUM(amount_usd) | not_null | Spend normalized to USD |
| aov_usd | NUMERIC | AVG(amount_usd) |  | Average order value |
| total_refund_usd | NUMERIC | SUM(refund_usd) |  | Refunds normalized to USD |
| first_order_ts | TIMESTAMP | MIN(order_ts) |  | First order timestamp |
| last_order_ts | TIMESTAMP | MAX(order_ts) |  | Most recent order timestamp |
| open_tickets | INT64 | SUM(open_tickets) |  | Total open tickets |
| closed_tickets | INT64 | SUM(closed_tickets) |  | Total closed tickets |

## Group by

| group_key |
|-----------|
| customer_id |

## Output constraints

| primary_key | partition_by | cluster_by |
|-------------|--------------|------------|
| customer_id |  | customer_id, last_order_ts |
