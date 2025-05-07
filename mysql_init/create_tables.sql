-- A table to store the users
CREATE TABLE IF NOT EXISTS users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    password VARCHAR(64) NOT NULL
);

-- A table to store configurations data for the proxy
CREATE TABLE IF NOT EXISTS configs (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED,
    name VARCHAR(64) UNIQUE NOT NULL,

    proxy_host TEXT NOT NULL,
    proxy_port SMALLINT UNSIGNED NOT NULL,
    
    real_host TEXT NOT NULL,
    real_port SMALLINT UNSIGNED NOT NULL,

    max_bytes_per_request INT UNSIGNED,
    max_bytes_per_response INT UNSIGNED,
    max_requests_per_second FLOAT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- A table to store whitelist and blacklist data
CREATE TABLE IF NOT EXISTS access_control (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(64) NOT NULL,
    list_type ENUM('whitelist', 'blacklist') NOT NULL,
    config_id INT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (config_id) REFERENCES configs(id) ON DELETE CASCADE,
    UNIQUE (ip_address, config_id)
);
