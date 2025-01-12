-- Create a table for your devices with a new 'description' column
CREATE TABLE IF NOT EXISTS devices (
    mac_address  VARCHAR(50) PRIMARY KEY,
    ip_address   VARCHAR(50),
    vendor       VARCHAR(100),
    description  VARCHAR(255),
    known        BOOLEAN DEFAULT false,
    state        VARCHAR(10) DEFAULT 'down',
    first_seen   TIMESTAMP,
    last_seen    TIMESTAMP,
    open_ports JSONB DEFAULT '[]'::JSONB
);

-- Router and Satellites
INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('8C:3B:AD:CF:8E:62', '192.168.1.1', 'NETGEAR', 'Orbi Router', true);

INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('8C:3B:AD:CD:78:A8', '192.168.1.102', 'NETGEAR', 'Orbi Satellite-1', true);

INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('78:D2:94:3F:A5:D1', '192.168.1.100', 'NETGEAR', 'Orbi Satellite-2', true);

-- Raspberry Pis
INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('B8:27:EB:98:B6:7F', '192.168.1.130', 'Raspberry Pi', 'Ethernet adapter on Pi 3B+. Has docker to run containers', true);

INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('B8:27:EB:01:C6:C6', '192.168.1.21', 'Raspberry Pi', 'Ethernet adapter on Pi 3B+. Pi-hole', true);

--- My Personal Devices
INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('EA:7E:DE:52:AF:FE', '192.168.1.131', 'Apple', 'Alex Iphone 15 Pro', true);

INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('6C:7E:67:B9:EE:F2', '192.168.1.129', 'Apple', 'Alex Work Macbook Pro', true);

INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('06:51:74:2B:44:5F', '192.168.1.122', 'Apple', 'Alex Apple Watch Series 9 with GPS', true);

INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('9C:6B:00:1E:D3:AA', '192.168.1.101', 'Asus', 'Alex Desktop Computer', true);

--- Smart Home Devices
-- Wifi Guest Network
INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('20:3D:BD:A2:8B:96', '192.168.1.112', 'LG', 'Basement TV', true);

INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('74:38:B7:84:F0:DE', '192.168.1.135', 'Cannon', 'Printer', true);

INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('0C:AE:7D:F8:B4:F1', '192.168.1.104', 'Lennox', 'iComfort HVAC Thermostat', true);

INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('88:57:1D:73:C4:F4', '192.168.1.103', 'Samsung', 'Family Hub smart refrigerator', true);

INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('00:23:A7:3C:C3:92', '192.168.1.107', 'Carrier', 'Infinity Thermostat', true);

INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('34:7D:E4:0E:55:FB', '192.168.1.108', 'Arcade 1UP', 'Pac Man and Retro Games Arcade Cabinet', true);

--- Smart Home Devices
-- Skynet Wifi or Wired
INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('B0:37:95:48:A0:87', '192.168.1.121', 'LG', 'UHD 80 Series 75 inch Class 4K Smart UHD TV with AI ThinQ® (UP8070PUR)', true);

INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('8A:A9:A7:05:7E:B4', '192.168.1.110', 'Flashforge', 'Adventurer 3', true);

INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('10:09:F9:97:7B:D8', '192.168.1.111', 'Amazon', 'Large screen Echo Show in family room', true);

--- Kid's Public Devices on the Guest Network
INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('CC:15:31:C8:05:05', '192.168.1.109', 'Dell', 'Natalie School Computer. Latitude 7420', true);

INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('DC:45:46:58:6D:D5', '192.168.1.133', 'Dell', 'Layla School Computer. Latitude 3140', true);

--- Kid's Devices on Skynet

--- Laura's Devices
INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES
('6E:59:19:D2:C5:BA', '192.168.1.116', 'Apple', 'Laura IPhone 15 Pro', true);