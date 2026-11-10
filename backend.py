
import json
import sqlite3
from pathlib import Path

import paho.mqtt.client as mqtt

DB = Path(__file__).resolve().parent / "sensors.sqlite3"


def initializare_baza():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                senzor TEXT NOT NULL,
                seq INTEGER NOT NULL,
                valoare REAL NOT NULL,
                unitate TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                UNIQUE(senzor, seq, timestamp)
            )
        """)
    print(f"Baza de date pregatita: {DB}", flush=True)


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        client.subscribe("wsn/backend/measurements", qos=1)
        print("BACKEND conectat la MQTT!", flush=True)
        print("Astept mesaje de la Gateway...", flush=True)
    else:
        print("Eroare conectare:", reason_code, flush=True)


def on_message(client, userdata, msg):
    try:
        date = json.loads(msg.payload.decode("utf-8"))

        with sqlite3.connect(DB) as conn:
            cursor = conn.execute("""
                INSERT OR IGNORE INTO measurements
                (senzor, seq, valoare, unitate, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                date["senzor"],
                int(date["seq"]),
                float(date["valoare"]),
                date["unitate"],
                date["timestamp"]
            ))

        if cursor.rowcount == 1:
            print(
                f"SALVAT: {date['senzor']} = "
                f"{date['valoare']} {date['unitate']} "
                f"(seq={date['seq']})",
                flush=True
            )
        else:
            print("Mesaj duplicat ignorat.", flush=True)

    except (ValueError, KeyError, TypeError, sqlite3.Error) as eroare:
        print("Eroare procesare:", eroare, flush=True)


initializare_baza()

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="backend_storage"
)

client.on_connect = on_connect
client.on_message = on_message

print("Pornire Backend...", flush=True)
client.connect("127.0.0.1", 1883, 60)
client.loop_forever()
