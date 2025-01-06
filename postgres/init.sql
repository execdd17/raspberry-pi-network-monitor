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

INSERT INTO devices (mac_address, ip_address, vendor, known, first_seen, last_seen)
VALUES
('8C:3B:AD:CF:8E:62', '192.168.1.1', 'NETGEAR', false, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, known, first_seen, last_seen)
VALUES
('B0:4A:39:71:4C:DB', '192.168.1.100', 'Beijing Roborock Technology Co., Ltd.', false, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, known, first_seen, last_seen)
VALUES
('D4:91:0F:9E:0F:8C', '192.168.1.102', 'Amazon Technologies Inc.', false, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, known, first_seen, last_seen)
VALUES
('BC:45:5B:9E:81:AA', '192.168.1.105', 'Samsung Electronics Co.,Ltd', false, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, known, first_seen, last_seen)
VALUES
('10:09:F9:97:7B:D8', '192.168.1.106', 'Amazon Technologies Inc.', false, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, known, first_seen, last_seen)
VALUES
('68:DB:F5:4A:E9:7A', '192.168.1.108', 'Amazon Technologies Inc.', false, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, known, first_seen, last_seen)
VALUES
('F8:54:B8:7B:91:B4', '192.168.1.109', 'Amazon Technologies Inc.', false, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, known, first_seen, last_seen)
VALUES
('A8:B5:7C:79:36:80', '192.168.1.111', 'Roku, Inc', false, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, known, first_seen, last_seen)
VALUES
('8C:3B:AD:CD:78:A8', '192.168.1.113', 'NETGEAR', false, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, known, first_seen, last_seen)
VALUES
('AC:63:BE:B6:1A:55', '192.168.1.114', 'Amazon Technologies Inc.', false, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, known, first_seen, last_seen)
VALUES
('9C:6B:00:1E:D3:AA', '192.168.1.115', 'ASRock Incorporation', false, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, known, first_seen, last_seen)
VALUES
('6C:7E:67:B9:EE:F2', '192.168.1.129', 'Apple, Inc.', false, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, known, first_seen, last_seen)
VALUES
('E0:F6:B5:9B:69:0B', '192.168.1.136', 'Nintendo Co.,Ltd', false, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, known, first_seen, last_seen)
VALUES
('B8:27:EB:01:C6:C6', '192.168.1.21', 'Raspberry Pi Foundation', false, NOW(), NOW());
