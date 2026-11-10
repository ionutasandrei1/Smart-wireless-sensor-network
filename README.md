# Smart Wireless Sensor Network Monitoring with Edge AI

## 1. Descriere și scenariu
Proiect pentru disciplina **Tehnici de Programare în IoT**. Simulează o rețea wireless cu șapte noduri de senzori și un gateway edge, utilizând înregistrări reale din datasetul UCI *Room Occupancy Estimation*. Datele sunt redate periodic prin MQTT, analizate local sau centralizat și afișate într-un dashboard web. **Nu necesită hardware fizic.**

## 2. Întrebare de cercetare (RQ1)
**Unde este mai eficient să executăm detecția anomaliilor: pe edge, în cloud sau într-o arhitectură hibridă?**

**Ipoteză H1:** În condiții de rețea degradată, detecția pe edge reduce latența P95 a alertelor față de cloud, cu o posibilă creștere a consumului local CPU.

**Baseline:** detecție centralizată prin reguli fixe. **Abordare propusă:** detecție locală, centralizată și hibridă, cu aceeași regulă/model, evaluată pe aceleași date.

## 3. Dataset și proveniență
- Sursă: [UCI Room Occupancy Estimation](https://archive.ics.uci.edu/dataset/864/room+occupancy+estimation)
- DOI: [10.24432/C5P605](https://doi.org/10.24432/C5P605)
- 10.129 înregistrări; șapte noduri wireless, un nod edge; variabile de temperatură, lumină, sunet, CO₂, PIR; etichetă `Room_Occupancy_Count` (0–3 persoane).
- Licență: **CC BY 4.0**, cu atribuirea autorilor A. P. Singh și S. Chaudhari.
- Datele sunt măsurători istorice, **nu** senzori conectați live. Simulatorul le retransmite ca mesaje MQTT.
- Eticheta de ocupare **nu** este o etichetă de anomalie. Anomaliile introduse experimental vor fi marcate separat.

## 4. Arhitectură
`Dataset UCI → Python replay → MQTT Mosquitto → Gateway/Edge → Backend SQLite → Dashboard Streamlit`

În modul edge, gateway-ul decide local și transmite alertele. În modul cloud, backend-ul decide după recepția măsurătorilor. Modul hibrid combină decizia locală cu verificarea în backend.

## 5. Obiective MVP
- [x] Scenariu și dataset public identificat
- [x] Cod de replay MQTT, ingestie, stocare și dashboard furnizat
- [ ] Validarea rulării integrale în Docker pe calculator
- [ ] Măsurarea latenței, traficului și consumului CPU/RAM
- [ ] Implementarea comparației complete edge/cloud/hibrid
- [ ] Evaluarea precision, recall și F1 pe anomalii etichetate experimental
- [ ] Implementarea unui asistent AI conversațional care analizează măsurătorile, explică anomaliile și răspunde la întrebări despre comunicația MQTT.

## 6. Tehnologii
Python 3.11, pandas, scikit-learn (pentru extindere ML), paho-mqtt, Eclipse Mosquitto, SQLite, Streamlit, Docker Compose.

## 7. Experiment propus
1. Replay fără anomalii.
2. Injectarea unor anomalii etichetate (de exemplu valori CO₂ crescute artificial) în datele de test.
3. Simularea întârzierilor și pierderilor de pachete.
4. Repetarea fiecărui scenariu în modurile edge, cloud și hibrid, cu seed-uri fixe.
5. Compararea latenței P50/P95, traficului în octeți, CPU/RAM, precision/recall/F1 și alarmelor false.

**Important:** rezultatele experimentale nu au fost încă măsurate; nu se pretinde o superioritate a unei metode înaintea testelor.

## 8. Pornire demo
1. Instalează Docker Desktop și pornește Docker Engine.
2. În directorul proiectului rulează `docker compose up --build`.
3. Deschide `http://localhost:8501` pentru dashboard.
4. Simulatorul descarcă datasetul UCI la prima pornire (este necesar internet); apoi redă câte un rând la fiecare 2 secunde.
5. Oprește cu `Ctrl+C` sau `docker compose down`.

Acest pachet reprezintă un **prototip demonstrativ**, nu o implementare complet validată a tuturor experimentelor RQ1.

## 9. API și procesare
Demo-ul folosește MQTT ca transport, un consumer Python pentru stocare și Streamlit pentru vizualizare. Nu include încă un API REST public; acesta poate fi adăugat într-un sprint ulterior.

## 10. Structura repository-ului
- `app/replay.py`: replay date și injectare de anomalii controlate
- `app/consumer.py`: ingestie MQTT, SQLite și reguli
- `app/dashboard.py`: vizualizare date și alerte
- `docker-compose.yml`: pornirea serviciilor
- `requirements.txt`: biblioteci Python
- `docs/PLAN.md`: etape, criterii și limitări

## 11. Riscuri și limitări
Replay-ul datelor istorice nu reproduce toate proprietățile unei rețele radio reale. Datasetul nu include RSL, BER, RSSI sau pierderi de pachete măsurate; degradarea rețelei trebuie simulată și documentată distinct. Pragurile de CO₂ din demo sunt ilustrative, nu recomandări de siguranță.

## 12. Referințe
Singh, A. P. & Chaudhari, S. (2018). *Room Occupancy Estimation*. UCI Machine Learning Repository. https://doi.org/10.24432/C5P605

Model de structură: exemplul Smart Greenhouse Monitoring furnizat la curs; întrebarea RQ1 și metodologia experimentală provin din documentul `RQs(1).pdf` al disciplinei.
## Implementarea practică – Cerințele 2 și 3

### Cerința 2 – Comunicarea senzorilor cu Gateway-ul

Au fost implementate trei procese Python independente, care simulează senzori de CO₂, temperatură și luminozitate.

Fiecare senzor generează date sintetice la intervale de două secunde și transmite măsurătorile prin protocolul MQTT, folosind brokerul Eclipse Mosquitto.

Gateway-ul primește datele de la toți senzorii prin abonarea la topicul `wsn/sensors/+`.

**Pornirea aplicației:**

Se deschid patru ferestre CMD în folderul proiectului și se execută:

```bash
python gateway.py
python senzor.py co2
python senzor.py temperatura
python senzor.py lumina
```

Fiecare comandă se execută într-o fereastră CMD separată.

### Cerința 3 – Transmiterea datelor către Backend

Gateway-ul retransmite măsurătorile către topicul MQTT `wsn/backend/measurements`.

Procesul `backend.py` primește mesajele și le stochează într-o bază de date SQLite numită `sensors.sqlite3`.

**Pornirea Backend-ului:**

```bash
python backend.py
```

Se execută într-o fereastră CMD separată, în timp ce Gateway-ul și senzorii funcționează.

**Verificarea bazei de date:**

```bash
python -c "import sqlite3; c=sqlite3.connect('sensors.sqlite3'); print(c.execute('SELECT COUNT(*) FROM measurements').fetchone()[0]); c.close()"
```

În timpul testului efectuat au fost confirmate 57 de măsurători salvate, câte 19 pentru fiecare senzor.

### Arhitectura implementată

Senzori virtuali (CO₂, temperatură, lumină) → Broker MQTT → Gateway Edge → Broker MQTT → Backend → SQLite.

**Cerințe de rulare:** Python, biblioteca `paho-mqtt` și un broker Eclipse Mosquitto accesibil pe `localhost:1883`. Această demonstrație funcționează local, fără Docker și fără senzori fizici.

### Documentația testelor

- `Cerinta_2_Senzori_Gateway.pdf` – capturi și explicații pentru comunicația senzori–Gateway.
- `Cerinta_3_Gateway_Backend_SQLite.pdf` – capturi și explicații pentru transmiterea și stocarea datelor.
