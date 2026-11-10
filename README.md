# Smart Wireless Sensor Network Monitoring with Edge AI

## 1. Descriere și scenariu

Proiect realizat pentru disciplina **Tehnici de Programare în IoT**.

Scopul proiectului este simularea unei rețele de senzori wireless și analizarea eficienței procesării datelor în arhitecturi Edge, Cloud și Hibride.

Proiectul utilizează două componente demonstrative:

1. **Prototipul bazat pe datasetul UCI Room Occupancy Estimation**, cu redarea măsurătorilor prin MQTT, stocare SQLite, dashboard Streamlit și experimentarea detecției anomaliilor prin Edge AI.
2. **Implementarea practică a comunicației IoT**, cu trei procese senzor independente, un Gateway, broker MQTT Eclipse Mosquitto și Backend SQLite.

Ambele componente pot funcționa fără senzori fizici.

## 2. Întrebare de cercetare (RQ1)

**Unde este mai eficient să executăm detecția anomaliilor: pe edge, în cloud sau într-o arhitectură hibridă?**

**Ipoteză H1:** În condiții de rețea degradată, detecția pe edge poate reduce latența P95 a alertelor față de procesarea centralizată, cu o posibilă creștere a consumului local de CPU.

**Baseline:** detecție centralizată prin reguli fixe.

**Abordare propusă:** compararea detecției locale, centralizate și hibride, utilizând aceleași date și aceleași criterii de evaluare.

## 3. Dataset și proveniență

Dataset utilizat în prototipul inițial:

- **Denumire:** UCI Room Occupancy Estimation.
- **Sursă:** https://archive.ics.uci.edu/dataset/864/room+occupancy+estimation
- **DOI:** https://doi.org/10.24432/C5P605
- **Număr înregistrări:** 10.129.
- **Variabile:** temperatură, lumină, sunet, CO₂, PIR și numărul persoanelor din încăpere.
- **Licență:** CC BY 4.0.
- **Autori:** A. P. Singh și S. Chaudhari.

Datasetul conține măsurători istorice, nu date provenite de la senzori fizici conectați în timp real.

În implementarea practică a cerințelor 2 și 3 sunt utilizate **date sintetice generate de procese Python independente**.

Eticheta `Room_Occupancy_Count` nu reprezintă o etichetă de anomalie. Anomaliile experimentale trebuie definite și marcate separat.

## 4. Arhitectura sistemului

### 4.1. Prototipul bazat pe datasetul UCI

`Dataset UCI → Python Replay → MQTT Mosquitto → Consumer → SQLite → Dashboard Streamlit`

Prototipul permite retransmiterea periodică a datelor, stocarea și vizualizarea măsurătorilor.

Pentru cercetare sunt prevăzute trei moduri de procesare:

- **Edge:** detecția anomaliilor înainte de transmiterea către backend.
- **Cloud:** detecția după recepția datelor în backend.
- **Hibrid:** detecție locală și verificare centralizată.

Comparația experimentală completă a celor trei moduri nu este încă finalizată.

### 4.2. Implementarea practică fără Docker

`3 senzori virtuali → MQTT Mosquitto → Gateway → MQTT Mosquitto → Backend → SQLite`

Senzorii simulați sunt:

- Senzor CO₂.
- Senzor temperatură.
- Senzor luminozitate.

Fiecare senzor rulează într-un proces Python independent.

Gateway-ul recepționează mesajele și le retransmite către Backend, care le salvează în SQLite.

În această demonstrație, Gateway-ul realizează **comunicarea și retransmiterea datelor**, fără să execute încă detecția anomaliilor prin AI.

## 5. Obiective și stadiul implementării

### Funcționalități realizate

- [x] Definirea scenariului IoT și a întrebării de cercetare.
- [x] Identificarea datasetului public UCI.
- [x] Realizarea prototipului Python cu MQTT, SQLite și Streamlit.
- [x] Testarea unui model Edge AI pe 500 de măsurători.
- [x] Implementarea a trei procese senzor independente.
- [x] Transmiterea mesajelor MQTT către Gateway.
- [x] Retransmiterea mesajelor de la Gateway către Backend.
- [x] Stocarea măsurătorilor în SQLite.
- [x] Verificarea bazei de date prin interogări SQL.
- [x] Documentarea cerințelor 2 și 3 prin capturi și explicații PDF.

### Funcționalități planificate

- [ ] Validarea completă a tuturor componentelor Docker.
- [ ] Integrarea detecției Edge AI în fluxul practic al Gateway-ului.
- [ ] Implementarea completă a modurilor Edge, Cloud și Hibrid.
- [ ] Simularea întârzierilor și pierderilor de pachete.
- [ ] Măsurarea latenței P50/P95 și a traficului.
- [ ] Evaluarea consumului CPU și RAM.
- [ ] Calcularea precision, recall și F1 pentru anomalii etichetate.
- [ ] Implementarea unui asistent AI conversațional pentru interpretarea măsurătorilor.

## 6. Tehnologii utilizate

- **Python:** generarea, transmiterea și procesarea datelor.
- **paho-mqtt:** comunicarea MQTT.
- **Eclipse Mosquitto:** broker MQTT.
- **SQLite:** stocarea măsurătorilor.
- **Streamlit:** dashboard web în prototipul inițial.
- **pandas:** prelucrarea datelor.
- **scikit-learn:** experimentarea detecției anomaliilor.
- **Docker Compose:** orchestrarea serviciilor din prototipul inițial.

Implementarea practică a cerințelor 2 și 3 nu necesită Docker.

## 7. Experimentul de cercetare propus

Experimentul urmărește compararea detecției anomaliilor în arhitecturi Edge, Cloud și Hibride.

Etapele propuse sunt:

1. Redarea măsurătorilor fără anomalii.
2. Introducerea unor anomalii controlate, de exemplu valori CO₂ crescute artificial.
3. Marcarea anomaliilor pentru evaluare.
4. Simularea întârzierilor și a pierderilor de pachete.
5. Executarea acelorași scenarii în modurile Edge, Cloud și Hibrid.
6. Măsurarea latenței, traficului și consumului de resurse.
7. Compararea rezultatelor experimentale.

Indicatori propuși:

- Latența P50 și P95.
- Traficul de date.
- Consumul CPU și RAM.
- Precision, recall și F1.
- Numărul alarmelor false.

**Rezultatele comparative nu au fost încă măsurate integral.**

## 8. Pornirea aplicației

### 8.1. Varianta Docker – prototipul inițial

Este necesar Docker Desktop.

Din directorul repository-ului se execută:

```bash
docker compose up --build
```

Dashboard-ul poate fi accesat la:

`http://localhost:8501`

Pentru oprire:

```bash
docker compose down
```

La prima rulare, descărcarea datasetului UCI poate necesita conexiune la internet.

### 8.2. Varianta fără Docker – implementarea practică

Sunt necesare:

- Python instalat.
- Biblioteca `paho-mqtt`.
- Broker Eclipse Mosquitto pornit pe `localhost:1883`.

Instalarea bibliotecii:

```bash
python -m pip install paho-mqtt
```

Se deschid cinci ferestre CMD în folderul care conține fișierele Python.

**Fereastra 1 – Backend:**

```bash
python backend.py
```

**Fereastra 2 – Gateway:**

```bash
python gateway.py
```

**Fereastra 3 – Senzor CO₂:**

```bash
python senzor.py co2
```

**Fereastra 4 – Senzor temperatură:**

```bash
python senzor.py temperatura
```

**Fereastra 5 – Senzor luminozitate:**

```bash
python senzor.py lumina
```

Fiecare proces rămâne activ și afișează mesajele transmise sau recepționate.

## 9. Comunicarea MQTT și stocarea datelor

Senzorii transmit măsurători sintetice la intervale de aproximativ două secunde.

### Topicuri MQTT

| Componentă | Topic |
|---|---|
| Senzor CO₂ | `wsn/sensors/co2` |
| Senzor temperatură | `wsn/sensors/temperatura` |
| Senzor luminozitate | `wsn/sensors/lumina` |
| Gateway – recepție | `wsn/sensors/+` |
| Gateway – transmitere | `wsn/backend/measurements` |
| Backend – recepție | `wsn/backend/measurements` |

Mesajele sunt transmise în format JSON și includ:

- Tipul senzorului.
- Numărul secvențial.
- Valoarea măsurată.
- Unitatea de măsură.
- Marcajul temporal.

Comunicația folosește MQTT cu QoS 1.

Backend-ul primește mesajele și le introduce în baza de date `sensors.sqlite3`, în tabelul `measurements`.

### Verificarea stocării

Din directorul proiectului se execută:

```bash
python -c "import sqlite3; c=sqlite3.connect('sensors.sqlite3'); print('Total:', c.execute('SELECT COUNT(*) FROM measurements').fetchone()[0]); print('Pe senzori:', c.execute('SELECT senzor, COUNT(*) FROM measurements GROUP BY senzor').fetchall()); c.close()"
```

Această comandă afișează numărul total de măsurători și distribuția acestora pe senzori.

## 10. Structura repository-ului

### Prototipul inițial

- `app/replay.py` – retransmiterea datelor din dataset.
- `app/consumer.py` – recepție MQTT, procesare și stocare.
- `app/dashboard.py` – interfață de vizualizare.
- `docker-compose.yml` – configurarea serviciilor Docker.
- `requirements.txt` – biblioteci Python.
- `docs/PLAN.md` – planificarea proiectului.

### Implementarea practică

- `senzor.py` – simularea senzorilor CO₂, temperatură și luminozitate.
- `gateway.py` – recepția și retransmiterea mesajelor MQTT.
- `backend.py` – recepția și stocarea datelor în SQLite.
- `Cerinta_2_Senzori_Gateway.pdf` – documentarea comunicației senzorilor cu Gateway-ul.
- `Cerinta_3_Gateway_Backend_SQLite.pdf` – documentarea transmiterii și stocării măsurătorilor.

Fișierul `sensors.sqlite3` este generat local în timpul rulării și nu trebuie încărcat în repository.

## 11. Riscuri și limitări

Rețeaua wireless este simulată software. Testele locale MQTT nu demonstrează caracteristicile unei legături radio fizice.

Datasetul UCI nu include măsurători radio precum RSSI, RSL sau BER.

În implementarea practică, brokerul, Gateway-ul și Backend-ul rulează pe același calculator, iar comunicația se realizează prin `localhost`.

Degradarea rețelei și comparația Edge/Cloud/Hibrid trebuie simulate și evaluate separat.

Pragurile CO₂ utilizate experimental sunt ilustrative și nu reprezintă recomandări de siguranță.

## 12. Referințe

Singh, A. P. & Chaudhari, S. (2018). *Room Occupancy Estimation*. UCI Machine Learning Repository.

https://doi.org/10.24432/C5P605

Materiale didactice utilizate:

- Documentul `RQs(1).pdf`.
- Catalogul proiectelor IoT și al dataseturilor.
- Ghidul de analiză arhitecturală a sistemelor IoT.
- Exemplul Smart Greenhouse Monitoring.

## 13. Implementarea practică – Validarea cerințelor 2 și 3

### Cerința 2 – Senzori → Gateway

Au fost implementate trei procese Python independente, care simulează senzori de CO₂, temperatură și luminozitate.

Fiecare senzor generează măsurători sintetice și le transmite către brokerul Eclipse Mosquitto.

Gateway-ul se abonează la topicul `wsn/sensors/+` și recepționează datele de la toți cei trei senzori.

Funcționarea a fost verificată prin afișarea mesajelor în ferestrele CMD.

**Rezultat:** comunicarea dintre mai multe procese senzor și un Gateway a fost demonstrată.

Documentație: `Cerinta_2_Senzori_Gateway.pdf`.

### Cerința 3 – Gateway → Backend → SQLite

Gateway-ul retransmite mesajele către topicul `wsn/backend/measurements`.

Backend-ul recepționează măsurătorile și le salvează în baza de date SQLite.

Verificarea experimentală a confirmat:

| Senzor | Măsurători salvate |
|---|---:|
| CO₂ | 19 |
| Temperatură | 19 |
| Luminozitate | 19 |
| **Total** | **57** |

Valorile reprezintă un rezultat intermediar al testului, deoarece aplicația poate continua să genereze și să stocheze măsurători.

**Rezultat:** a fost demonstrat fluxul complet de comunicație și stocare:

`Senzori → MQTT → Gateway → MQTT → Backend → SQLite`

Documentație: `Cerinta_3_Gateway_Backend_SQLite.pdf`.

### Concluzie

Cerințele 2 și 3 au fost implementate și testate folosind procese Python independente, protocolul MQTT și baza de date SQLite.

Rezultatele confirmă funcționarea fluxului de transmitere și stocare a măsurătorilor.

Această implementare constituie baza pentru extinderea proiectului cu detecție de anomalii Edge AI și evaluarea comparativă a arhitecturilor Edge, Cloud și Hibride.
