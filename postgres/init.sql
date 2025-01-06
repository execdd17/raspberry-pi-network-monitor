-- Create a table for your devices
CREATE TABLE IF NOT EXISTS devices (
    mac_address  VARCHAR(50) PRIMARY KEY,
    ip_address   VARCHAR(50),
    vendor       VARCHAR(100),
    known        BOOLEAN DEFAULT false,
    state        VARCHAR(10) DEFAULT 'down',
    first_seen   TIMESTAMP NOT NULL,
    last_seen    TIMESTAMP NOT NULL
);

-- If you want more tables or initial data, add it here
-- INSERT INTO devices (mac_address, ip_address, vendor, known, first_seen, last_seen)
-- VALUES ('AA:BB:CC:DD:EE:FF', '192.168.1.100', 'SampleVendor', false, NOW(), NOW());
