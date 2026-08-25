import json
import os
import redis

client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,
)

def get_latest_from_cache(device_id):
    # M2: Läs senaste mätvärdet från Redis.

    # Skapa Redis-nyckeln för den aktuella sensorn.
    # Exempel: latest:sensor-01
    cached = client.get(f"latest:{device_id}")

    # Cache miss:
    # Om ingen mätning finns i Redis returneras None.
    if cached is None:
        return None

    # Redis innehåller mätningen som JSON.
    # Konvertera JSON-strängen till en Python-dictionary.
    return json.loads(cached)


def set_latest_in_cache(device_id, measurement):
    # M2: Spara senaste mätvärdet i Redis.

    # Konvertera Python-dictionary till JSON
    # och spara den under sensorns Redis-nyckel.
    client.set(
        f"latest:{device_id}",
        json.dumps(measurement)
    )
