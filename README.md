# Laboratorio Django + Wireshark

Progetto didattico per scuole superiori e istituti tecnici: analisi del traffico HTTP di un'applicazione Django con Wireshark.

## Obiettivo

Questo progetto fornisce un'applicazione web Django minimale che permette agli studenti di:
- Osservare il flusso HTTP di un login (GET form, POST credenziali, redirect con sessionid)
- Distinguere un **login riuscito** (HTTP 302 + Set-Cookie sessionid) da un **login fallito** (HTTP 200 senza sessionid)
- Analizzare i cookie CSRF e di sessione in Wireshark
- Comprendere il protocollo HTTP su TCP in un contesto reale

## Requisiti

- Python 3.8 o superiore
- Wireshark (per la cattura del traffico)

## Installazione

### 1. Clona il repository

```bash
git clone <URL_REPOSITORY>
cd <DIRECTORY_PROGETTO>
```

### 2. Crea e attiva un ambiente virtuale

```bash
python3 -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate
```

### 3. Installa le dipendenze

```bash
pip install -r requirements.txt
```

### 4. Esegui le migrazioni del database

```bash
python manage.py migrate
```

### 5. Crea l'utente demo

```bash
python manage.py crea_utente_demo
```

Questo comando crea l'utente:
- **Username**: `pippo`
- **Password**: `lab2024`

## Avvio del server

```bash
python manage.py runserver 127.0.0.1:8000
```

Il server sarà raggiungibile all'indirizzo: **http://127.0.0.1:8000**

## Utilizzo in laboratorio

### Scenario 1: Login riuscito

1. Apri Wireshark e avvia la cattura sull'interfaccia di loopback (`lo` o `Loopback: lo0`)
2. Applica il filtro: `tcp.port == 8000`
3. Apri il browser e vai su **http://127.0.0.1:8000**
4. Clicca su "Vai al login"
5. Inserisci le credenziali corrette: username `pippo`, password `lab2024`
6. Ferma la cattura in Wireshark

### Scenario 2: Login fallito

1. Ripeti i passaggi 1-4
2. Inserisci credenziali **errate** (es. password sbagliata)
3. Ferma la cattura

## Cosa osservare in Wireshark

### Filtri utili

| Filtro Wireshark | Descrizione |
|------------------|-------------|
| `tcp.port == 8000` | Tutto il traffico verso/da Django |
| `http.request.method == GET` | Tutte le richieste GET |
| `http.request.method == POST` | Richiesta POST del login |
| `http.response.code == 302` | Redirect (login riuscito) |
| `http.response.code == 200` | Risposta normale |
| `http.cookie contains "sessionid"` | Richieste con sessionid |
| `http.set_cookie contains "sessionid"` | Risposte che impostano sessionid |
| `http.set_cookie contains "csrftoken"` | Cookie CSRF |

### Sequenza HTTP completa (login riuscito)

#### 1. GET / (home anonimo)
- **Richiesta**: GET / HTTP/1.1
- **Risposta**: 200 OK
- Pagina home per utente anonimo

#### 2. GET /accounts/login/ (richiesta form)
- **Richiesta**: GET /accounts/login/ HTTP/1.1
- **Risposta**: 200 OK + **Set-Cookie: csrftoken=...**
- Il server invia il form HTML con campo nascosto `csrfmiddlewaretoken`

#### 3. POST /accounts/login/ (invio credenziali)
- **Richiesta**: POST /accounts/login/ HTTP/1.1
  - `Content-Type: application/x-www-form-urlencoded`
  - Body (in chiaro!): `username=pippo&password=lab2024&csrfmiddlewaretoken=...`
  - Header: `Cookie: csrftoken=...`
  
**Se login riuscito:**
- **Risposta**: **302 Found**
- Header: `Location: /`
- Header: **`Set-Cookie: sessionid=...`** ← **chiave del successo!**

**Se login fallito:**
- **Risposta**: **200 OK**
- **Nessun Set-Cookie sessionid**
- Body: form HTML re-renderizzato con messaggio di errore

#### 4. GET / (redirect dopo login riuscito)
- **Richiesta**: GET / HTTP/1.1
  - Header: **`Cookie: sessionid=...`** ← il browser invia il cookie ricevuto
- **Risposta**: 200 OK
- Pagina home personalizzata con nome utente

#### 5. POST /accounts/logout/ (logout)
- **Richiesta**: POST /accounts/logout/ con Cookie: sessionid
- **Risposta**: 302 Found verso /
- Il sessionid viene invalidato sul server

### Differenze chiave: login OK vs KO

| Aspetto | Login riuscito | Login fallito |
|---------|----------------|---------------|
| Status code POST | **302 Found** | **200 OK** |
| Set-Cookie sessionid | **Presente** ✓ | **Assente** ✗ |
| Redirect | Location: / | Nessun redirect |
| Pagina successiva | Home autenticato | Form con errore |

### Note TCP (contesto)

- Prima del traffico HTTP vedrai il **three-way handshake TCP** (SYN, SYN-ACK, ACK)
- Header `Connection: keep-alive` → la connessione TCP rimane aperta per più richieste HTTP
- Alla fine vedrai i pacchetti **FIN/ACK** di chiusura TCP (se il browser chiude la connessione)

## Struttura del progetto

```
.
├── lablogin/              # Configurazione Django
│   ├── settings.py        # Impostazioni (DEBUG=True per lab)
│   └── urls.py            # URL routing
├── sito/                  # Applicazione principale
│   ├── views.py           # View home
│   ├── templates/sito/    # Template HTML didattici
│   │   ├── home.html      # Pagina home (con note Wireshark)
│   │   └── login.html     # Form login (con note Wireshark)
│   └── management/commands/
│       └── crea_utente_demo.py  # Comando per utente demo
├── manage.py              # Script Django
├── requirements.txt       # Dipendenze Python
└── README.md              # Questo file
```

## Note di sicurezza (SOLO per laboratorio)

⚠️ **Questo progetto è SOLO per scopi didattici in ambiente locale.**

- `DEBUG = True` (non usare in produzione!)
- Password validator disabilitati (per permettere password semplici come `lab2024`)
- Traffico HTTP **in chiaro** (no HTTPS)
- Secret key hardcoded (non importa per localhost)
- Database SQLite gitignored (ogni studente crea il proprio)

**In produzione:** usare sempre HTTPS, password forti, DEBUG=False, secret key in variabili d'ambiente.

## Esercizi proposti per gli studenti

1. Cattura il traffico di un login **fallito** e uno **riuscito**, salva i due file .pcap e confrontali
2. Trova il campo `csrfmiddlewaretoken` nel body del POST usando Wireshark
3. Copia il valore del `sessionid` da Wireshark e confrontalo con il cookie nel browser (Strumenti sviluppatore > Storage/Cookies)
4. Modifica il codice per cambiare il messaggio di benvenuto e osserva la risposta HTTP in Wireshark
5. Prova a fare il logout e verifica che le richieste successive **non** contengano più il cookie sessionid valido

## Troubleshooting

### Il server non parte
- Verifica che la porta 8000 non sia già occupata: `lsof -i :8000`
- Verifica di aver attivato il virtual environment: `source venv/bin/activate`

### L'utente demo non esiste
- Esegui: `python manage.py crea_utente_demo`

### Wireshark non mostra traffico
- Assicurati di catturare sull'interfaccia **Loopback** (non Ethernet/WiFi)
- Su Linux: interfaccia `lo`
- Su macOS: `Loopback: lo0`
- Su Windows: `Adapter for loopback traffic capture`

### Non vedo HTTP in Wireshark, solo TCP
- Wireshark potrebbe non decodificare automaticamente la porta 8000 come HTTP
- Click destro su un pacchetto TCP > "Decode As..." > seleziona "HTTP"
- Oppure usa il filtro: `tcp.port == 8000 && tcp.len > 0`

## Licenza

Progetto didattico open source per scopi educativi.
