# Model: stg_orders (layer: staging)

Sources: raw.commerce_orders, raw.commerce_order_items, raw.fx_rates

## Column mapping

| target_column | type | from_table | from_column | transform | nullable | tests | description |
|---------------|------|------------|-------------|-----------|----------|-------|-------------|
| order_id | INT64 | commerce_orders | order_id |  | False |  |  |
| customer_id | INT64 | commerce_orders | customer_id |  | False |  |  |
| order_ts | TIMESTAMP | commerce_orders | order_ts |  | True |  |  |
| amount_usd | NUMERIC | commerce_orders | total_amount | {from} * fx_rates.rate_to_usd | True |  | Normalized to USD |
| items | INT64 | commerce_order_items | quantity | SUM({from}) | True |  | Total items per order |
| refund_usd | NUMERIC | commerce_order_items | refund_amount | SUM({from}) * fx_rates.rate_to_usd | True |  | Refund amount normalized |

## Joins

| left_table | right_table | type | condition |
|------------|-------------|------|-----------|
| commerce_orders | commerce_order_items | LEFT | commerce_orders.order_id = commerce_order_items.order_id |
| commerce_orders | fx_rates | LEFT | commerce_orders.currency = fx_rates.currency |

## Output constraints

| primary_key | partition_by | cluster_by |
|-------------|--------------|------------|
| order_id |  |  |
