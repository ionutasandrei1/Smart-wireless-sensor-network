
import json
import random
import sys
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

if len(sys.argv) != 2 or sys.argv[1] not in ("co2", "temperatura", "lumina"):
    print("Utilizare: python senzor.py co2|temperatura|lumina")
    sys.exit(1)

tip = sys.argv[1]

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=f"senzor_{tip}"
)

client.connect("127.0.0.1", 1883, 60)
client.loop_start()

seq = 0

try:
    while True:
        if tip == "co2":
            # Anomalie controlata la fiecare 10 masuratori
            if seq > 0 and seq % 10 == 0:
                valoare = 2500.0
                print(
                    "TEST: anomalie CO2 injectata!",
                    flush=True
                )
            else:
                valoare = round(random.uniform(400, 1200), 1)

            unitate = "ppm"

        elif tip == "temperatura":
            valoare = round(random.uniform(18, 30), 1)
            unitate = "C"

        else:
            valoare = round(random.uniform(100, 800), 1)
            unitate = "lux"

        mesaj = {
            "senzor": tip,
            "seq": seq,
            "valoare": valoare,
            "unitate": unitate,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "injected": tip == "co2" and seq > 0 and seq % 10 == 0
        }

        client.publish(
            f"wsn/sensors/{tip}",
            json.dumps(mesaj),
            qos=1
        ).wait_for_publish()

        print(f"TRIMIS: {mesaj}", flush=True)

        seq += 1
        time.sleep(2)

except KeyboardInterrupt:
    print("Senzor oprit.")

finally:
    client.loop_stop()
    client.disconnect()
