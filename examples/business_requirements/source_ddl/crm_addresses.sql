CREATE TABLE IF NOT EXISTS `raw.crm_addresses` (
  customer_id INT64 NOT NULL,
  country STRING,
  city STRING,
  state STRING,
  postal_code STRING,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
