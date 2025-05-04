CREATE TABLE IF NOT EXISTS configs (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,

    proxy_host TEXT NOT NULL,
    proxy_port SMALLINT UNSIGNED NOT NULL,
    
    real_host TEXT NOT NULL,
    real_port SMALLINT UNSIGNED NOT NULL,

    max_bytes_per_request INT UNSIGNED,
    max_bytes_per_response INT UNSIGNED,
    max_requests_per_second FLOAT
);

Create TABLE IF NOT EXISTS requests (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    password VARCHAR(64) NOT NULL,
);
