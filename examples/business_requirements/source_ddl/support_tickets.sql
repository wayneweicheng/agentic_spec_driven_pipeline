CREATE TABLE IF NOT EXISTS `raw.support_tickets` (
  customer_id INT64 NOT NULL,
  created_at TIMESTAMP,
  status STRING
);
