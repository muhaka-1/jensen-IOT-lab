from flask import Flask, jsonify, request, render_template
import os
import socket

from db import (
    device_exists,
    get_devices,
    get_measurements,
    get_latest_measurement,
    get_measurements_for_device,
    get_statistics_summary,
    insert_measurement,
)
from validation import validate_measurement
from cache import get_latest_from_cache, set_latest_in_cache

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "v1")
POD_NAME = socket.gethostname()


@app.get("/")
def dashboard():
    return render_template("index.html", version=APP_VERSION, pod=POD_NAME)


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "version": APP_VERSION,
        "pod": POD_NAME,
    }), 200


@app.get("/devices")
def devices():
    return jsonify(get_devices()), 200


@app.get("/measurements")
def measurements():
    return jsonify(get_measurements()), 200


@app.get("/devices/<device_id>/latest")
def latest(device_id):
    # M1: Verify that the device exists.
    # En okänd sensor returnerar HTTP 404.
    if not device_exists(device_id):
        return jsonify({
            "error": "device not found",
            "deviceId": device_id
        }), 404

    # M2: Cache-aside – försök först läsa den senaste
    # mätningen från Redis.
    measurement = get_latest_from_cache(device_id)

    # Cache HIT:
    # Om mätningen finns i Redis behöver vi inte fråga PostgreSQL.
    if measurement is not None:
        return jsonify(measurement), 200

    # M1/M2: Cache MISS:
    # Om mätningen inte finns i Redis hämtar vi den senaste
    # mätningen från PostgreSQL.
    measurement = get_latest_measurement(device_id)

    # M1: En känd sensor utan några mätningar returnerar HTTP 404.
    if measurement is None:
        return jsonify({
            "error": "no measurements found",
            "deviceId": device_id
        }), 404

    # M2: Cache-aside – spara resultatet från PostgreSQL
    # i Redis så att nästa request kan hämtas från cachen.
    set_latest_in_cache(device_id, measurement)

    # Returnera den senaste mätningen.
    return jsonify(measurement), 200

   

@app.get("/devices/<device_id>/measurements")
def device_history(device_id):
    # M1: Verify that the device exists.
    # En okänd sensor returnerar HTTP 404.
    if not device_exists(device_id):
        return jsonify({
            "error": "device not found",
            "deviceId": device_id
        }), 404

    # M1: Hämta sensorhistoriken från PostgreSQL.
    measurements = get_measurements_for_device(device_id)

    # M1: En känd sensor utan mätningar returnerar
    # HTTP 200 och en tom lista.
    if not measurements:
        return jsonify([]), 200

    # M1: Returnera sensorhistoriken.
    return jsonify(measurements), 200


@app.post("/measurements")
def create_measurement():
    # Läs JSON-data från request.
    # Om requesten saknar JSON-data används en tom dictionary.
    data = request.get_json(silent=True) or {}

    # Validera mätningen innan den sparas.
    errors = validate_measurement(data)

    # Om valideringen misslyckas returneras HTTP 400
    # tillsammans med information om vilka fält som är fel.
    if errors:
        print(
            f"INVALID measurement from "
            f"{data.get('deviceId', 'unknown')}: {errors}"
        )
        return jsonify({"errors": errors}), 400

    # M1: Kontrollera att deviceId tillhör en känd sensor.
    # En okänd sensor får inte skapa någon mätning.
    device_id = data["deviceId"]

    if not device_exists(device_id):
        return jsonify({
            "error": "device not found",
            "deviceId": device_id
        }), 400

    # M1: Spara den validerade mätningen i PostgreSQL.
    measurements = insert_measurement(data)

    # M2: Uppdatera latest-cache i Redis.
    # Den nya mätningen blir den senaste mätningen för sensorn.
    set_latest_in_cache(device_id, measurements)

    # M1/M2: Mätningen har validerats, sparats i PostgreSQL
    # och latest-cache har uppdaterats.
    print(f"VALID measurement received: {measurements}")

    return jsonify({
        "status": "Created",
        "measurement": measurements
    }), 201


@app.get("/statistics")
def statistics():
    summary = get_statistics_summary()
    return jsonify(summary), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
