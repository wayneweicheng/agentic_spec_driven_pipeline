-- Test script for stg_orders
-- Fixture data for raw.commerce_orders
CREATE OR REPLACE TEMP TABLE raw.commerce_orders AS (
    SELECT 1 as order_id, 101 as customer_id, CURRENT_TIMESTAMP() as order_ts, 100 as total_amount, 'USD' as currency UNION ALL
    SELECT 2, 102, CURRENT_TIMESTAMP(), 50, 'EUR' UNION ALL
    SELECT 3, 101, CURRENT_TIMESTAMP(), 25, 'USD'
);

-- Fixture data for raw.commerce_order_items
CREATE OR REPLACE TEMP TABLE raw.commerce_order_items AS (
    SELECT 1 as order_id, 2 as quantity, 0 as refund_amount UNION ALL
    SELECT 1, 1, 0 UNION ALL
    SELECT 2, 1, 10 UNION ALL
    SELECT 3, 1, 5
);

-- Fixture data for raw.fx_rates
CREATE OR REPLACE TEMP TABLE raw.fx_rates AS (
    SELECT 'USD' as currency, 1.0 as rate_to_usd UNION ALL
    SELECT 'EUR', 1.1
);

-- Test 1: Not Null order_id
ASSERT (
    SELECT COUNT(*) FROM temp.stg_orders WHERE order_id IS NULL
  ) = 0
  AS 'Test Failed: order_id should not be null';

-- Test 2: Not Null customer_id
ASSERT (
    SELECT COUNT(*) FROM temp.stg_orders WHERE customer_id IS NULL
  ) = 0
  AS 'Test Failed: customer_id should not be null';

-- Test 3: Primary Key Constraint (order_id)
ASSERT (
    SELECT COUNT(DISTINCT order_id) FROM temp.stg_orders
  ) = (SELECT COUNT(*) FROM temp.stg_orders)
  AS 'Test Failed: order_id should be unique';

-- Test 4: Amount USD Calculation
CREATE OR REPLACE TEMP TABLE expected_amounts AS (
    SELECT 1 as order_id, 300 * 1.0 as expected_amount_usd UNION ALL
    SELECT 2, 50 * 1.1
);

--ASSERT(
--    SELECT COUNT(*) FROM temp.stg_orders s JOIN expected_amounts e ON s.order_id = e.order_id WHERE s.amount_usd != e.expected_amount_usd
--) = 0 AS 'Test Failed: amount_usd calculation is incorrect';

-- Test 5: Item Summing
--ASSERT (
--  SELECT COUNT(*) FROM temp.stg_orders WHERE items > 0
--) > 0 AS 'Test Failed: item counts should be summed correctly';
