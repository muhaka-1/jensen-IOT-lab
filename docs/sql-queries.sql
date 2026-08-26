-- Jensen IoT Lab – Grundläggande SQL-uppgifter

-- 1. Totalt antal mätningar
SELECT COUNT(*) AS total_measurements
FROM measurements;


-- 2. Medeltemperatur
SELECT AVG(temperature) AS average_temperature
FROM measurements;


-- 3. Mätningar från de senaste 24 timmarna
SELECT *
FROM measurements
WHERE created_at >= NOW() - INTERVAL '24 hours';