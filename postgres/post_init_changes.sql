-- UPSERTS
-- I like this approach because it can run either when the table is first init, or after the fact

INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES ('BC:45:5B:9E:81:AA', '192.168.1.117', 'Samsung', '34 inch Odyssey G85SB Series QD-OLED Ultra WQHD Curved Gaming Monitor, 175Hz, 0.03ms, DisplayHDR True Black 400, AMD FreeSync Premium Pro, Advanced Game Streaming, LS34BG850SNXZA, 2023', true)
ON CONFLICT (mac_address)
DO UPDATE
    SET ip_address  = EXCLUDED.ip_address,
        vendor      = EXCLUDED.vendor,
        description = EXCLUDED.description,
        known       = EXCLUDED.known;

INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES ('46:56:EA:28:D1:22', '192.168.1.115', 'Apple', 'Cadence IPad', true)
ON CONFLICT (mac_address)
DO UPDATE
    SET ip_address  = EXCLUDED.ip_address,
        vendor      = EXCLUDED.vendor,
        description = EXCLUDED.description,
        known       = EXCLUDED.known;

INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES ('A2:18:A4:AA:CE:1E', '192.168.1.113', 'Apple', 'Natalie IPad', true)
ON CONFLICT (mac_address)
DO UPDATE
    SET ip_address  = EXCLUDED.ip_address,
        vendor      = EXCLUDED.vendor,
        description = EXCLUDED.description,
        known       = EXCLUDED.known;

INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES ('B0:AC:82:C6:1E:69', '192.168.1.119', 'GMKtec', 'Nucbox G3 PLUS', true)
ON CONFLICT (mac_address)
DO UPDATE
    SET ip_address  = EXCLUDED.ip_address,
        vendor      = EXCLUDED.vendor,
        description = EXCLUDED.description,
        known       = EXCLUDED.known;

INSERT INTO devices (mac_address, ip_address, vendor, description, known)
VALUES ('E8:FF:1E:D9:88:7B', '192.168.1.1', 'Beelink', 'EQ14 Mini PC', true)
ON CONFLICT (mac_address)
DO UPDATE
    SET ip_address  = EXCLUDED.ip_address,
        vendor      = EXCLUDED.vendor,
        description = EXCLUDED.description,
        known       = EXCLUDED.known;