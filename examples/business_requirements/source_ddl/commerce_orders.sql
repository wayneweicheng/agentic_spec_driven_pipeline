CREATE TABLE IF NOT EXISTS `raw.commerce_orders` (
  order_id INT64 NOT NULL,
  customer_id INT64 NOT NULL,
  order_ts TIMESTAMP,
  currency STRING,
  total_amount NUMERIC
);
