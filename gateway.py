
import json
import paho.mqtt.client as mqtt

PRAG_CO2 = 1800
PRAG_SPIKE_CO2 = 700

# Ultima secventa si ultima valoare pentru fiecare senzor
ultimele_secvente = {}
ultimele_valori = {}


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("GATEWAY EDGE conectat la MQTT!", flush=True)
        client.subscribe("wsn/sensors/+", qos=1)
        print("Monitorizare: DATE LIPSA + SPIKES + CO2", flush=True)
    else:
        print("Eroare conectare:", reason_code, flush=True)


def on_message(client, userdata, msg):
    try:
        date = json.loads(msg.payload.decode("utf-8"))

        senzor = date["senzor"]
        seq = int(date["seq"])
        valoare = float(date["valoare"])

        print(
            f"PRIMIT: {senzor} seq={seq} "
            f"valoare={valoare} {date['unitate']}",
            flush=True
        )

        # 1. Detectarea datelor lipsa
        date_lipsa = 0

        if senzor in ultimele_secvente:
            ultima = ultimele_secvente[senzor]

            if seq > ultima + 1:
                date_lipsa = seq - ultima - 1
                print(
                    f"EDGE DATE LIPSA: {senzor} "
                    f"lipsesc {date_lipsa} masuratori "
                    f"(intre seq={ultima} si seq={seq})",
                    flush=True
                )

        # Gestionam si repornirea senzorului (seq revine la 0)
        if senzor in ultimele_secvente and seq < ultimele_secvente[senzor]:
            print(
                f"INFO: {senzor} - secventa resetata",
                flush=True
            )
            ultimele_valori.pop(senzor, None)

        ultimele_secvente[senzor] = seq

        # 2. Detectarea spike-urilor CO2
        spike = False

        if senzor == "co2" and senzor in ultimele_valori:
            diferenta = abs(valoare - ultimele_valori[senzor])

            if diferenta > PRAG_SPIKE_CO2:
                spike = True
                print(
                    f"EDGE SPIKE: CO2 modificare brusca "
                    f"de {diferenta:.1f} ppm",
                    flush=True
                )

        ultimele_valori[senzor] = valoare

        # 3. Detectarea depasirii pragului CO2
        alerta_co2 = senzor == "co2" and valoare > PRAG_CO2

        if alerta_co2:
            print(
                f"ALERTA EDGE: CO2 = {valoare} ppm "
                f"(prag {PRAG_CO2} ppm)",
                flush=True
            )

        # Adaugam rezultatele detectiei in mesaj
        date["date_lipsa"] = date_lipsa
        date["spike"] = spike
        date["alerta"] = bool(alerta_co2 or spike or date_lipsa > 0)
        date["status"] = (
            "ANOMALIE" if date["alerta"] else "NORMAL"
        )

        # Retransmitere catre Backend
        rezultat = client.publish(
            "wsn/backend/measurements",
            json.dumps(date),
            qos=1
        )

        if rezultat.rc == mqtt.MQTT_ERR_SUCCESS:
            print(
                f"TRIMIS Backend: {senzor} seq={seq} "
                f"status={date['status']} "
                f"spike={spike} lipsa={date_lipsa}",
                flush=True
            )
        else:
            print("Eroare transmitere Backend!", flush=True)

    except (ValueError, KeyError, TypeError) as eroare:
        print("Mesaj invalid:", eroare, flush=True)


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="gateway_edge"
)

client.on_connect = on_connect
client.on_message = on_message

print("Pornire Gateway EDGE - Missing Data + Spikes", flush=True)
client.connect("127.0.0.1", 1883, 60)
client.loop_forever()
