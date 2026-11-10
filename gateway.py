
import json
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("GATEWAY conectat la MQTT!", flush=True)
        client.subscribe("wsn/sensors/+", qos=1)
        print("Gateway asteapta date de la senzori...", flush=True)
    else:
        print("Eroare conectare:", reason_code, flush=True)

def on_message(client, userdata, msg):
    try:
        date = json.loads(msg.payload.decode("utf-8"))

        print(
            f"PRIMIT de la {date['senzor']}: "
            f"{date['valoare']} {date['unitate']}",
            flush=True
        )

        # Retransmitere catre Backend pe un topic separat
        rezultat = client.publish(
            "wsn/backend/measurements",
            json.dumps(date),
            qos=1
        )

        if rezultat.rc == mqtt.MQTT_ERR_SUCCESS:
            print(
                f"TRIMIS catre Backend: {date['senzor']} "
                f"seq={date['seq']}",
                flush=True
            )
        else:
            print("Eroare la transmiterea catre Backend!", flush=True)

    except (ValueError, KeyError) as eroare:
        print("Mesaj invalid:", eroare, flush=True)

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="gateway_edge"
)

client.on_connect = on_connect
client.on_message = on_message

print("Pornire Gateway Edge...", flush=True)
client.connect("127.0.0.1", 1883, 60)
client.loop_forever()
