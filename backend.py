
import json
import sqlite3
from pathlib import Path
from collections import deque

import paho.mqtt.client as mqtt

DB = Path(__file__).resolve().parent / "sensors.sqlite3"

FEREASTRA = 5
PRAG_DRIFT = 400
istoric_co2 = deque(maxlen=FEREASTRA)


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
                alerta INTEGER DEFAULT 0,
                status TEXT DEFAULT 'NORMAL',
                injected INTEGER DEFAULT 0,
                UNIQUE(senzor, seq, timestamp)
            )
        """)

        coloane = {
            rand[1]
            for rand in conn.execute(
                "PRAGMA table_info(measurements)"
            )
        }

        coloane_noi = {
            "alerta": "INTEGER DEFAULT 0",
            "status": "TEXT DEFAULT 'NORMAL'",
            "injected": "INTEGER DEFAULT 0",
            "spike": "INTEGER DEFAULT 0",
            "date_lipsa": "INTEGER DEFAULT 0",
            "drift": "INTEGER DEFAULT 0"
        }

        for nume, definitie in coloane_noi.items():
            if nume not in coloane:
                conn.execute(
                    f"ALTER TABLE measurements "
                    f"ADD COLUMN {nume} {definitie}"
                )
                print(f"Coloana adaugata: {nume}", flush=True)

    print(f"Baza de date pregatita: {DB}", flush=True)


def detecteaza_drift(valoare):
    istoric_co2.append(valoare)

    if len(istoric_co2) < FEREASTRA:
        return False

    valori = list(istoric_co2)

    crestere_continua = all(
        valori[i] > valori[i - 1]
        for i in range(1, len(valori))
    )

    crestere_totala = valori[-1] - valori[0]

    if crestere_continua and crestere_totala >= PRAG_DRIFT:
        print(
            f"CLOUD DRIFT DETECTAT: {valori} "
            f"crestere={crestere_totala:.1f} ppm",
            flush=True
        )
        return True

    return False


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        client.subscribe("wsn/backend/measurements", qos=1)
        print("BACKEND CLOUD conectat la MQTT!", flush=True)
        print("Monitorizare tendinte CO2 (drift)...", flush=True)
    else:
        print("Eroare conectare:", reason_code, flush=True)


def on_message(client, userdata, msg):
    try:
        date = json.loads(msg.payload.decode("utf-8"))

        senzor = date["senzor"]
        valoare = float(date["valoare"])

        alerta = int(bool(date.get("alerta", False)))
        status = date.get("status", "NORMAL")
        injected = int(bool(date.get("injected", False)))
        spike = int(bool(date.get("spike", False)))
        date_lipsa = int(date.get("date_lipsa", 0))

        # Salvam doar mesajele noi
        with sqlite3.connect(DB) as conn:
            cursor = conn.execute("""
                INSERT OR IGNORE INTO measurements
                (
                    senzor, seq, valoare, unitate,
                    timestamp, alerta, status, injected,
                    spike, date_lipsa, drift
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """, (
                senzor,
                int(date["seq"]),
                valoare,
                date["unitate"],
                date["timestamp"],
                alerta,
                status,
                injected,
                spike,
                date_lipsa
            ))

            if cursor.rowcount == 0:
                print("Mesaj duplicat ignorat.", flush=True)
                return

            drift = False

            if senzor == "co2":
                # O intrerupere de secventa rupe seria continua
                if date_lipsa > 0:
                    istoric_co2.clear()

                drift = detecteaza_drift(valoare)

                if drift:
                    conn.execute(
                        "UPDATE measurements SET drift = 1 WHERE id = ?",
                        (cursor.lastrowid,)
                    )

        print(
            f"SALVAT: {senzor} = {valoare} "
            f"{date['unitate']} seq={date['seq']} "
            f"spike={spike} lipsa={date_lipsa} "
            f"drift={int(drift)}",
            flush=True
        )

    except (ValueError, KeyError, TypeError, sqlite3.Error) as eroare:
        print("Eroare procesare:", eroare, flush=True)


initializare_baza()

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="backend_storage"
)

client.on_connect = on_connect
client.on_message = on_message

print("Pornire Backend CLOUD - Trends / Drift", flush=True)
client.connect("127.0.0.1", 1883, 60)
client.loop_forever()
