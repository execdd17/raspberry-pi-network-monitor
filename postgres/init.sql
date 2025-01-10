-- Create a table for your devices with a new 'description' column
CREATE TABLE IF NOT EXISTS devices (
    mac_address  VARCHAR(50) PRIMARY KEY,
    ip_address   VARCHAR(50),
    vendor       VARCHAR(100),
    description  VARCHAR(255) DEFAULT NULL,
    known        BOOLEAN DEFAULT false,
    state        VARCHAR(10) DEFAULT 'down',
    first_seen   TIMESTAMP NOT NULL,
    last_seen    TIMESTAMP NOT NULL
);

-- Router and Satellites
INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
VALUES
('8C:3B:AD:CF:8E:62', '192.168.1.1', 'NETGEAR', 'Orbi Router', true, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
VALUES
('8C:3B:AD:CD:78:A8', '192.168.1.102', 'NETGEAR', 'Orbi Satellite-1', true, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
VALUES
('78:D2:94:3F:A5:D1', '192.168.1.100', 'NETGEAR', 'Orbi Satellite-2', true, NOW(), NOW());

-- Raspberry Pis
INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
VALUES
('B8:27:EB:98:B6:7F', '192.168.1.130', 'Raspberry Pi', 'Ethernet adapter on Pi 3B+. Has docker to run containers', true, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
VALUES
('B8:27:EB:01:C6:C6', '192.168.1.21', 'Raspberry Pi', 'Ethernet adapter on Pi 3B+. Pi-hole', true, NOW(), NOW());

--- My Personal Devices
INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
VALUES
('EA:7E:DE:52:AF:FE', '192.168.1.131', 'Apple', 'Alex Iphone 15 Pro', true, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
VALUES
('6C:7E:67:B9:EE:F2', '192.168.1.129', 'Apple', 'Alex Work Macbook Pro', true, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
VALUES
('06:51:74:2B:44:5F', '192.168.1.122', 'Apple', 'Alex Apple Watch Series 9 with GPS', true, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
VALUES
('9C:6B:00:1E:D3:AA', '192.168.1.101', 'Asus', 'Alex Desktop Computer', true, NOW(), NOW());

--- Smart Home Devices
-- Wifi Guest Network
INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
VALUES
('0C:AE:7D:F8:B4:F1', '192.168.1.104', 'Lennox', 'iComfort HVAC Thermostat', true, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
VALUES
('88:57:1D:73:C4:F4', '192.168.1.103', 'Samsung', 'Family Hub smart refrigerator', true, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
VALUES
('00:23:A7:3C:C3:92', '192.168.1.107', 'Carrier', 'Infinity Thermostat', true, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
VALUES
('34:7D:E4:0E:55:FB', '192.168.1.108', 'Arcade 1UP', 'Pac Man and Retro Games Arcade Cabinet', true, NOW(), NOW());

--- Smart Home Devices
-- Skynet Wifi or Wired
INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
VALUES
('B0:37:95:48:A0:87', '192.168.1.121', 'LG', 'UHD 80 Series 75 inch Class 4K Smart UHD TV with AI ThinQ® (UP8070PUR)', true, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
VALUES
('8A:A9:A7:05:7E:B4', '192.168.1.110', 'Flashforge', 'Adventurer 3', true, NOW(), NOW());

INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
VALUES
('10:09:F9:97:7B:D8', '192.168.1.111', 'Amazon', 'Large screen Echo Show in family room', true, NOW(), NOW());

--- Kid's Public Devices on the Guest Network
INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
VALUES
('CC:15:31:C8:05:05', '192.168.1.109', 'Dell', 'Natalie School Computer. Latitude 7420', true, NOW(), NOW());

--- Kid's Public Devices on Skynet

--- Laura's Devices
INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
VALUES
('6E:59:19:D2:C5:BA', '192.168.1.116', 'Apple', 'Laura IPhone 15 Pro', true, NOW(), NOW());


-- INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
-- VALUES
-- ('B0:4A:39:71:4C:DB', '192.168.1.100', 'Beijing Roborock Technology Co., Ltd.', 'Robot Vacuum', true, NOW(), NOW());

-- INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
-- VALUES
-- ('D4:91:0F:9E:0F:8C', '192.168.1.102', 'Amazon Technologies Inc.', NULL, true, NOW(), NOW());

-- INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
-- VALUES
-- ('BC:45:5B:9E:81:AA', '192.168.1.105', 'Samsung Electronics Co.,Ltd', NULL, true, NOW(), NOW());

-- INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
-- VALUES
-- ('10:09:F9:97:7B:D8', '192.168.1.106', 'Amazon Technologies Inc.', NULL, true, NOW(), NOW());

-- INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
-- VALUES
-- ('68:DB:F5:4A:E9:7A', '192.168.1.108', 'Amazon Technologies Inc.', NULL, true, NOW(), NOW());

-- INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
-- VALUES
-- ('F8:54:B8:7B:91:B4', '192.168.1.109', 'Amazon Technologies Inc.', NULL, true, NOW(), NOW());

-- INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
-- VALUES
-- ('A8:B5:7C:79:36:80', '192.168.1.111', 'Roku, Inc', NULL, true, NOW(), NOW());

-- INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
-- VALUES
-- ('8C:3B:AD:CD:78:A8', '192.168.1.113', 'NETGEAR', NULL, true, NOW(), NOW());

-- INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
-- VALUES
-- ('AC:63:BE:B6:1A:55', '192.168.1.114', 'Amazon Technologies Inc.', NULL, true, NOW(), NOW());

-- INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
-- VALUES
-- ('9C:6B:00:1E:D3:AA', '192.168.1.115', 'ASRock Incorporation', NULL, true, NOW(), NOW());

-- INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
-- VALUES
-- ('6C:7E:67:B9:EE:F2', '192.168.1.129', 'Apple, Inc.', NULL, true, NOW(), NOW());

-- INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
-- VALUES
-- ('E0:F6:B5:9B:69:0B', '192.168.1.136', 'Nintendo Co.,Ltd', NULL, true, NOW(), NOW());

-- INSERT INTO devices (mac_address, ip_address, vendor, description, known, first_seen, last_seen)
-- VALUES
-- ('B8:27:EB:01:C6:C6', '192.168.1.21', 'Raspberry Pi Foundation', NULL, true, NOW(), NOW());
