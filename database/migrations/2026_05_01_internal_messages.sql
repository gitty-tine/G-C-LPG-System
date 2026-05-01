CREATE TABLE IF NOT EXISTS internal_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    body TEXT NOT NULL,
    read_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_internal_messages_receiver_read (receiver_id, read_at),
    KEY idx_internal_messages_pair_created (sender_id, receiver_id, created_at),
    KEY idx_internal_messages_created (created_at)
);
