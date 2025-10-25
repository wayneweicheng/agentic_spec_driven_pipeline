CREATE TABLE IF NOT EXISTS `raw.commerce_order_items` (
  order_id INT64 NOT NULL,
  quantity INT64,
  refund_amount NUMERIC
);
