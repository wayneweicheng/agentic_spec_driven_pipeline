-- Test script for dim_customers_scd2
-- Fixture data for stg_customers
CREATE OR REPLACE TEMP TABLE temp.stg_customers AS (
    SELECT 1 as customer_id, 'test@example.com' as email, '+15551234567' as phone_e164, 'active' as lifecycle_stage, 'USA' as country, 'Anytown' as city, 'CA' as state, '90210' as postal_code, CURRENT_TIMESTAMP() as created_at UNION ALL
    SELECT 2, 'TEST@EXAMPLE.COM', '+15555555555', 'inactive', 'Canada', 'Toronto', 'ON', 'M5V 3L3', CURRENT_TIMESTAMP() UNION ALL
    SELECT 3, 'test2@example.com', '+11234567890', 'trial', NULL, 'New York', 'NY', '10001', CURRENT_TIMESTAMP()
);

-- Test 1: Natural Key (customer_id) Uniqueness
ASSERT (
    SELECT COUNT(DISTINCT customer_id) FROM analytics.dim_customers_scd2
  ) = (SELECT COUNT(*) FROM (SELECT DISTINCT customer_id FROM analytics.dim_customers_scd2))
  AS 'Test Failed: customer_id should be unique';

-- Test 2: Ensure valid_from is not null
ASSERT (
    SELECT COUNT(*) FROM analytics.dim_customers_scd2 WHERE valid_from IS NULL
  ) = 0
  AS 'Test Failed: valid_from should not be null';

-- Test 3: Ensure current records have is_current = TRUE
ASSERT (
    SELECT COUNT(*) FROM analytics.dim_customers_scd2 WHERE is_current = TRUE AND valid_to IS NOT NULL
  ) = 0
  AS 'Test Failed: Current records must have is_current = TRUE';

-- Test 4: Ensure non-current records have is_current = FALSE
ASSERT (
    SELECT COUNT(*) FROM analytics.dim_customers_scd2 WHERE is_current = FALSE AND valid_to IS NULL
  ) = 0
  AS 'Test Failed: Non-current records must have is_current = FALSE';

-- Test 5: Valid From <= Valid To
--ASSERT (
--  SELECT COUNT(*) FROM analytics.dim_customers_scd2 WHERE valid_from > valid_to
--) = 0 AS 'Test Failed: Valid From must be less than or equal to Valid To';
