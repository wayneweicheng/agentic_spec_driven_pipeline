-- Test script for stg_support_pivot
-- Fixture data for raw.support_tickets
CREATE OR REPLACE TEMP TABLE raw.support_tickets AS (
    SELECT 1 as customer_id, 'OPEN' as status UNION ALL
    SELECT 1, 'CLOSED' UNION ALL
    SELECT 2, 'OPEN' UNION ALL
    SELECT 2, 'OPEN' UNION ALL
    SELECT 3, 'CLOSED'
);

-- Test 1: Primary Key Constraint (customer_id)
ASSERT (
    SELECT COUNT(DISTINCT customer_id) FROM temp.stg_support_pivot
  ) = (SELECT COUNT(*) FROM temp.stg_support_pivot)
  AS 'Test Failed: customer_id should be unique';

-- Test 2: Open Ticket Aggregation
CREATE OR REPLACE TEMP TABLE expected_open_tickets AS (
    SELECT 1 as customer_id, 1 as expected_open_tickets UNION ALL
    SELECT 2, 2 UNION ALL
    SELECT 3, 0
);

--ASSERT (
--    SELECT COUNT(*) FROM temp.stg_support_pivot s JOIN expected_open_tickets e ON s.customer_id = e.customer_id WHERE s.open_tickets != e.expected_open_tickets
--) = 0 AS 'Test Failed: open_tickets aggregation is incorrect';

-- Test 3: Closed Ticket Aggregation
CREATE OR REPLACE TEMP TABLE expected_closed_tickets AS (
    SELECT 1 as customer_id, 1 as expected_closed_tickets UNION ALL
    SELECT 2, 0 UNION ALL
    SELECT 3, 1
);

--ASSERT (
--    SELECT COUNT(*) FROM temp.stg_support_pivot s JOIN expected_closed_tickets e ON s.customer_id = e.customer_id WHERE s.closed_tickets != e.expected_closed_tickets
--) = 0 AS 'Test Failed: closed_tickets aggregation is incorrect';
