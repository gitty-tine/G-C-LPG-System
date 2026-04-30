CREATE INDEX idx_transactions_payment_delivery
ON transactions (payment_status, delivery_id);
