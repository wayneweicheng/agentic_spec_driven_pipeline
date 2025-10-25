# Customer 360 Data Pipeline Requirements (Table-Driven)

## Business Context
We need a unified Customer 360 for analytics. Data comes from multiple source systems:
- CRM (customers, addresses)
- Commerce (orders, order_items)
- Support (tickets)

Goals:
- Standardize identifiers, emails, phone numbers, and addresses
- Map CRM customer status to standardized lifecycle stage
- Calculate LTV, order counts, AOV, first/last order dates
- Flag risky customers (high refund rate or many tickets)
- Produce final analytics tables in `analytics` schema

## Sources
DDL files for all sources are provided under `examples/business_requirements/source_ddl`.

Schemas:
- Raw: `raw`
- Staging: `temp`
- Final: `analytics`

---

### Model: stg_customers (schema: temp)
Sources: `raw.crm_customers`, `raw.crm_addresses`

Column mapping
```markdown
| target_column   | type      | from_table    | from_column | transform                                                                                                                                     | nullable | tests                | description                |
|-----------------|-----------|---------------|-------------|------------------------------------------------------------------------------------------------------------------------------------------------|----------|----------------------|----------------------------|
| customer_id     | INT64     | crm_customers | customer_id |                                                                                                                                                | false    | not_null, unique     | Primary business key       |
| email           | STRING    | crm_customers | email       | LOWER(TRIM({from}))                                                                                                                            | false    | not_null             | Standardized email         |
| phone_e164      | STRING    | crm_customers | phone       | CASE WHEN REGEXP_CONTAINS(REGEXP_REPLACE({from}, '[^0-9]', ''), r'^1?[0-9]{10}$') THEN CONCAT('+1', RIGHT(REGEXP_REPLACE({from}, '[^0-9]', ''), 10)) WHEN REGEXP_CONTAINS(REGEXP_REPLACE({from}, '[^0-9]', ''), r'^[0-9]{11,15}$') THEN CONCAT('+', REGEXP_REPLACE({from}, '[^0-9]', '')) ELSE NULL END | true     |                      | Normalized phone           |
| lifecycle_stage | STRING    | crm_customers | status      | CASE WHEN {from} = 'active' THEN 'active' WHEN {from} = 'inactive' THEN 'churned' WHEN {from} = 'trial' THEN 'trial' WHEN {from} = 'prospect' THEN 'prospect' ELSE 'unknown' END | false    | accepted_values(...) | Standardized lifecycle     |
| country         | STRING    | crm_addresses | country     |                                                                                                                                                | true     |                      | Country from best address  |
| city            | STRING    | crm_addresses | city        |                                                                                                                                                | true     |                      | City                       |
| state           | STRING    | crm_addresses | state       |                                                                                                                                                | true     |                      | State                      |
| postal_code     | STRING    | crm_addresses | postal_code |                                                                                                                                                | true     |                      | Postal code                |
| created_at      | TIMESTAMP | crm_customers | created_at  |                                                                                                                                                | false    | not_null             | Ingestion baseline         |
```

Joins
```markdown
| left_table    | right_table   | type | condition                                             |
|---------------|---------------|------|-------------------------------------------------------|
| crm_customers | crm_addresses | LEFT | crm_customers.customer_id = crm_addresses.customer_id |
```

Filters
```markdown
| applies_to    | predicate           | rationale                  |
|---------------|---------------------|----------------------------|
| crm_addresses | country IS NOT NULL | drop incomplete addresses  |
```

Constraints
```markdown
| primary_key | partition_by | cluster_by |
|-------------|--------------|------------|
| customer_id | (none)       | (none)     |
```

---

### Model: stg_orders (schema: temp)
Sources: `raw.commerce_orders`, `raw.commerce_order_items`, `raw.fx_rates`

Notes:
- Aggregate order items by order to compute `items` and `refund_usd`.
- Normalize amounts to USD via `fx_rates`.

Column mapping
```markdown
| target_column | type      | from_table           | from_column  | transform                           | nullable | tests | description               |
|---------------|-----------|----------------------|--------------|--------------------------------------|----------|-------|---------------------------|
| order_id      | INT64     | commerce_orders      | order_id     |                                      | false    |       |                           |
| customer_id   | INT64     | commerce_orders      | customer_id  |                                      | false    |       |                           |
| order_ts      | TIMESTAMP | commerce_orders      | order_ts     |                                      | true     |       |                           |
| amount_usd    | NUMERIC   | commerce_orders      | total_amount | {from} * fx_rates.rate_to_usd        | true     |       | Normalized to USD         |
| items         | INT64     | commerce_order_items | quantity     | SUM({from})                          | true     |       | Total items per order     |
| refund_usd    | NUMERIC   | commerce_order_items | refund_amount| SUM({from}) * fx_rates.rate_to_usd   | true     |       | Refund amount normalized  |
```

Joins
```markdown
| left_table       | right_table          | type | condition                                                  |
|------------------|----------------------|------|------------------------------------------------------------|
| commerce_orders  | commerce_order_items | LEFT | commerce_orders.order_id = commerce_order_items.order_id    |
| commerce_orders  | fx_rates             | LEFT | commerce_orders.currency = fx_rates.currency               |
```

Filters
```markdown
| applies_to | predicate | rationale |
|------------|-----------|-----------|
| (none)     |           |           |
```

Constraints
```markdown
| primary_key | partition_by | cluster_by |
|-------------|--------------|------------|
| order_id    | (none)       | (none)     |
```

---

### Model: stg_support_pivot (schema: temp)
Sources: `raw.support_tickets`

Notes:
- Produce per-customer ticket counts by status (OPEN, CLOSED) using pivot.

Aggregations/Pivot
```markdown
| metric_column | type  | formula                                | tests | description                  |
|---------------|-------|----------------------------------------|-------|------------------------------|
| open_tickets  | INT64 | COUNTIF(status = 'OPEN')               |       | Open ticket count per user   |
| closed_tickets| INT64 | COUNTIF(status = 'CLOSED')             |       | Closed ticket count per user |
```

Group by
```markdown
| group_key   |
|-------------|
| customer_id |
```

Constraints
```markdown
| primary_key | partition_by | cluster_by |
|-------------|--------------|------------|
| customer_id | (none)       | (none)     |
```

---

### Model: dim_customers_scd2 (schema: analytics)
Depends on: `stg_customers`

Notes:
- Build SCD2 dimension for customers with effective and expiry timestamps.
- Natural key: `customer_id`.
- Track changes on `email`, `phone_e164`, `lifecycle_stage`, address fields.

Constraints
```markdown
| scd_type | natural_key  | effective_at | expiry_at   | current_flag |
|----------|---------------|--------------|-------------|--------------|
| 2        | customer_id   | valid_from   | valid_to    | is_current   |
```

---

### Model: fact_customer_orders (schema: analytics)
Depends on: `stg_orders`, `stg_support_pivot`

Aggregations
```markdown
| metric_column     | type      | formula           | tests    | description                   |
|-------------------|-----------|-------------------|----------|-------------------------------|
| order_count       | INT64     | COUNT(*)          | not_null | Total orders per customer     |
| total_spent_usd   | NUMERIC   | SUM(amount_usd)   | not_null | Spend normalized to USD       |
| aov_usd           | NUMERIC   | AVG(amount_usd)   |          | Average order value           |
| total_refund_usd  | NUMERIC   | SUM(refund_usd)   |          | Refunds normalized to USD     |
| first_order_ts    | TIMESTAMP | MIN(order_ts)     |          | First order timestamp         |
| last_order_ts     | TIMESTAMP | MAX(order_ts)     |          | Most recent order timestamp   |
| open_tickets      | INT64     | SUM(open_tickets) |          | Total open tickets            |
| closed_tickets    | INT64     | SUM(closed_tickets)|         | Total closed tickets          |
```

Group by
```markdown
| group_key   |
|-------------|
| customer_id |
```

Constraints
```markdown
| primary_key | partition_by | cluster_by                   |
|-------------|--------------|------------------------------|
| customer_id | (none)       | customer_id, last_order_ts   |
```
