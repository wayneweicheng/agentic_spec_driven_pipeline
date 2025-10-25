-- Test script for fact_customer_orders
-- Fixture data for stg_orders
CREATE OR REPLACE TEMP TABLE temp.stg_orders AS (
    SELECT 101 as order_id, 1 as customer_id, CURRENT_TIMESTAMP() as order_ts, 100.0 as amount_usd, 2 as items, 0.0 as refund_usd UNION ALL
    SELECT 102, 2, CURRENT_TIMESTAMP(), 50.0, 1, 10.0 UNION ALL
    SELECT 103, 1, CURRENT_TIMESTAMP(), 25.0, 1, 5.0
);

-- Fixture data for stg_support_pivot
CREATE OR REPLACE TEMP TABLE temp.stg_support_pivot AS (
    SELECT 1 as customer_id, 1 as open_tickets, 1 as closed_tickets UNION ALL
    SELECT 2, 2, 0 UNION ALL
    SELECT 3, 0, 1
);

-- Test 1: Primary Key Constraint (customer_id)
ASSERT (
    SELECT COUNT(DISTINCT customer_id) FROM analytics.fact_customer_orders
  ) = (SELECT COUNT(*) FROM analytics.fact_customer_orders)
  AS 'Test Failed: customer_id should be unique';

-- Test 2: Not Null order_count
ASSERT (
    SELECT COUNT(*) FROM analytics.fact_customer_orders WHERE order_count IS NULL
  ) = 0
  AS 'Test Failed: order_count should not be null';

-- Test 3: Not Null total_spent_usd
ASSERT (
    SELECT COUNT(*) FROM analytics.fact_customer_orders WHERE total_spent_usd IS NULL
  ) = 0
  AS 'Test Failed: total_spent_usd should not be null';

-- Test 4: Correct order count aggregation
CREATE OR REPLACE TEMP TABLE expected_order_counts AS (
  SELECT 1 as customer_id, 2 AS expected_order_count UNION ALL
  SELECT 2, 1
);

--ASSERT (
--    SELECT COUNT(*) FROM analytics.fact_customer_orders s JOIN expected_order_counts e ON s.customer_id = e.customer_id WHERE s.order_count != e.expected_order_count
--) = 0 AS 'Test Failed: Order count aggregation is incorrect';

-- Test 5: Check total_spent_usd
--ASSERT (
--  SELECT COUNT(*) FROM analytics.fact_customer_orders WHERE total_spent_usd > 0
--) > 0 AS 'Test Failed: Total spend should be aggregated correctly';
