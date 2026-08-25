import os
from decimal import Decimal
import psycopg2
import psycopg2.extras


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "jensen_iot"),
        user=os.getenv("DB_USER", "student"),
        password=os.getenv("DB_PASSWORD", "student"),
    )


def _json_ready(row):
    if row is None:
        return None
    result = dict(row)
    for key in ("temperature", "humidity"):
        if isinstance(result.get(key), Decimal):
            result[key] = float(result[key])
    if result.get("created_at") is not None:
        result["created_at"] = result["created_at"].isoformat()
    return result


def get_devices():
    query = """
        SELECT id, device_id, location, device_type
        FROM devices
        ORDER BY device_id;
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query)
            return [dict(row) for row in cur.fetchall()]


def get_measurements():
    query = """
        SELECT id, device_id, temperature, humidity, battery, created_at
        FROM measurements
        ORDER BY created_at DESC
        LIMIT 100;
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query)
            return [_json_ready(row) for row in cur.fetchall()]


def device_exists(device_id):
    # TODO M1:
    # Kontrollera om device_id finns i tabellen devices.
    # Returnera True eller False.
     query = """
        SELECT 1
        FROM devices
        WHERE device_id = %s;
    """

     with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (device_id,))
            return cur.fetchone() is not None


def get_latest_measurement(device_id):
    # TODO M1:
    # Implementera senaste mätvärdet för en sensor.
    query = """
        SELECT id, device_id, temperature, humidity, battery, created_at
        FROM measurements
        WHERE device_id = %s
        ORDER BY created_at DESC, id DESC
        LIMIT 1;
    """

    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            cur.execute(query, (device_id,))
            row = cur.fetchone()
            return _json_ready(row)


def get_measurements_for_device(device_id):
    # TODO M1:
    # Implementera historik för en sensor.
    query = """
        SELECT id, device_id, temperature, humidity, battery, created_at
        FROM measurements
        WHERE device_id = %s
        ORDER BY created_at DESC;
    """

    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            cur.execute(query, (device_id,))
            return [_json_ready(row) for row in cur.fetchall()]


def insert_measurement(data):
    # TODO M1:
    # Spara ett validerat mätvärde i PostgreSQL.
    query = """
        INSERT INTO measurements (
            device_id,
            temperature,
            humidity,
            battery
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id, device_id, temperature, humidity, battery, created_at;
    """

    values = (
        data["deviceId"],
        data["temperature"],
        data.get("humidity"),
        data.get("battery"),
    )

    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            cur.execute(query, values)
            row = cur.fetchone()

            return _json_ready(row)

def get_statistics_summary():
    # SQL-fråga som beräknar statistik direkt i PostgreSQL.
    query = """
        SELECT
            (SELECT COUNT(*) FROM devices) AS device_count,
            COUNT(*) AS measurement_count,
            ROUND(AVG(temperature), 2) AS average_temperature,
            MIN(temperature) AS minimum_temperature,
            MAX(temperature) AS maximum_temperature,
            ROUND(AVG(humidity), 2) AS average_humidity,
            ROUND(AVG(battery), 2) AS average_battery
        FROM measurements;
    """

    # Öppna en anslutning till PostgreSQL.
    # 'with' ser till att anslutningen stängs korrekt efteråt.
    with get_connection() as conn:

        # Skapa en cursor som returnerar varje databasrad
        # som en dictionary-liknande struktur.
        with conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:

            # Kör SQL-frågan mot PostgreSQL.
            cur.execute(query)

            # Hämta den enda raden med statistik som SQL-frågan
            # returnerar.
            row = cur.fetchone()

            # Om databasen mot förmodan inte returnerar någon rad
            # returneras en tom dictionary.
            if row is None:
                return {}

            # Konvertera RealDictRow till en vanlig Python-dictionary.
            row = dict(row)

            # PostgreSQL kan returnera numeriska värden som Decimal.
            # Konvertera Decimal till float så att resultatet enkelt
            # kan skickas som JSON från Flask.
            return {
                key: float(value) if isinstance(value, Decimal) else value
                for key, value in row.items()
            }