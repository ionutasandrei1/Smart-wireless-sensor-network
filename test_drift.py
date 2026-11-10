
import json
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect("127.0.0.1", 1883, 60)
client.loop_start()

valori = [600, 750, 900, 1050, 1200]

for i, valoare in enumerate(valori):
    mesaj = {
        "senzor": "co2",
        "seq": 20001 + i,
        "valoare": valoare,
        "unitate": "ppm",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "injected": True
    }

    rezultat = client.publish(
        "wsn/sensors/co2",
        json.dumps(mesaj),
        qos=1
    )
    rezultat.wait_for_publish()

    print(f"TRIMIS TEST DRIFT: CO2 = {valoare} ppm")
    time.sleep(2)

client.disconnect()
client.loop_stop()
print("Test drift terminat.")
