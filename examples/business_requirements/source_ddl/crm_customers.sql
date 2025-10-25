CREATE TABLE IF NOT EXISTS `raw.crm_customers` (
  customer_id INT64 NOT NULL,
  email STRING,
  phone STRING,
  status STRING,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
