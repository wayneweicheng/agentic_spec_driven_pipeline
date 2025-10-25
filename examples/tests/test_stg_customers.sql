-- Test script for stg_customers
-- Fixture data for raw.crm_customers
CREATE OR REPLACE TEMP TABLE raw.crm_customers AS (
  SELECT 1 as customer_id, 'test@example.com' as email, '+15551234567' as phone, 'active' as status, CURRENT_TIMESTAMP() as created_at UNION ALL
  SELECT 2, 'TEST@EXAMPLE.COM', '555-555-5555', 'inactive', CURRENT_TIMESTAMP() UNION ALL
  SELECT 3, 'test2@example.com', '1234567890', 'trial', CURRENT_TIMESTAMP() UNION ALL
  SELECT 4, 'test3@example.com', '123456789012345', 'prospect', CURRENT_TIMESTAMP() UNION ALL
  SELECT 5, 'test4@example.com', NULL, 'unknown', CURRENT_TIMESTAMP() -- Edge case: NULL phone
);

-- Fixture data for raw.crm_addresses
CREATE OR REPLACE TEMP TABLE raw.crm_addresses AS (
  SELECT 1 as customer_id, 'USA' as country, 'Anytown' as city, 'CA' as state, '90210' as postal_code UNION ALL
  SELECT 2, 'Canada', 'Toronto', 'ON', 'M5V 3L3' UNION ALL
  SELECT 3, NULL, 'New York', 'NY', '10001' -- Edge case: NULL country
);

-- Test 1: Not Null customer_id
ASSERT (
    SELECT COUNT(*) FROM temp.stg_customers WHERE customer_id IS NULL
  ) = 0
  AS 'Test Failed: customer_id should not be null';

-- Test 2: Unique customer_id
ASSERT (
    SELECT COUNT(DISTINCT customer_id) FROM temp.stg_customers
  ) = (SELECT COUNT(*) FROM temp.stg_customers)
  AS 'Test Failed: customer_id should be unique';

-- Test 3: Not Null email
ASSERT (
    SELECT COUNT(*) FROM temp.stg_customers WHERE email IS NULL
  ) = 0
  AS 'Test Failed: email should not be null';

-- Test 4: Not Null created_at
ASSERT (
    SELECT COUNT(*) FROM temp.stg_customers WHERE created_at IS NULL
  ) = 0
  AS 'Test Failed: created_at should not be null';

-- Test 5: Accepted Values lifecycle_stage
CREATE OR REPLACE TEMP TABLE expected_lifecycle_stages AS (
  SELECT 'active' AS lifecycle_stage UNION ALL
  SELECT 'churned' UNION ALL
  SELECT 'trial' UNION ALL
  SELECT 'prospect' UNION ALL
  SELECT 'unknown'
);

ASSERT (
  SELECT COUNT(*) FROM temp.stg_customers
  WHERE lifecycle_stage NOT IN (SELECT lifecycle_stage FROM expected_lifecycle_stages)
) = 0 AS 'Test Failed: lifecycle_stage contains unexpected values';

-- Test 6: Phone normalization (E.164)
ASSERT(
  SELECT COUNT(*) FROM temp.stg_customers WHERE phone_e164 LIKE '+1%'
) > 0 AS 'Test Failed: Phone numbers should be normalized to E.164 format';

-- Test 7: Email Lowercase
ASSERT (
  SELECT COUNT(*) FROM temp.stg_customers WHERE email != LOWER(email)
) = 0 AS 'Test Failed: Email should be in lowercase';

-- Test 8: Filter on addresses
ASSERT (
  SELECT COUNT(*) FROM raw.crm_addresses WHERE country IS NULL
) = 0 AS 'Test Failed: Addresses with NULL country must be filtered out';
