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