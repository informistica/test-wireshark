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

#### Come combinare i filtri display (AND / OR)

Nella barra filtro di Wireshark puoi unire condizioni con operatori logici:

- **AND (e)**: usa `&&` oppure la parola `and`. Entrambe le condizioni devono essere vere.
  - Schema: `tcp.port == <numero_porta> && http`
  - Schema: `http.request.method == "<METODO>" && http.request.uri contains "<testo>"`

- **OR (o)**: usa `||` oppure la parola `or`. Basta che una delle condizioni sia vera.
  - Schema: `http.response.code == <codice1> || http.response.code == <codice2>`

- **NOT / raggruppamento**: usa `!` (negazione) e parentesi `( )` per l'ordine delle operazioni.
  - Schema: `tcp.port == <numero_porta> && (http.request.method == "GET" || http.request.method == "POST")`

#### Filtri in forma generale (da soli o combinati)

Sostituisci i parametri tra `< >` con i valori della tua cattura. Negli esercizi dovrai costruire tu il filtro combinando questi elementi base.

| Filtro | Descrizione |
|--------|-------------|
| `tcp.port == <numero_porta>` | Traffico TCP sulla porta del servizio (es. 8000 per runserver) |
| `http` | Solo pacchetti riconosciuti come HTTP |
| `http.request.method == "<METODO>"` | METODO tipicamente `"GET"` o `"POST"` |
| `http.request.uri == "<url>"` | URL esatto della risorsa richiesta (es. `/accounts/login/`) |
| `http.request.uri contains "<testo>"` | URI che contiene un frammento (es. parte del percorso) |
| `http.response.code == <codice>` | Risposte con uno status HTTP (es. 200, 302, …) |
| `tcp.flags.syn == 1` | Segmenti con flag SYN (apertura / handshake) |
| `tcp.flags.ack == 0` | Senza flag ACK (utile insieme a SYN per il solo SYN iniziale) |
| `tcp.flags.ack == 1` | Con flag ACK (utile insieme a SYN per il SYN-ACK) |
| `tcp.flags.fin == 1` | Segmenti con flag FIN (chiusura) |
| `tcp.stream eq <N>` | Tutti i pacchetti dello stream TCP numero N (sostituisci N) |
| `http.cookie` | Richieste che trasportano header Cookie |
| `http.set_cookie` | Risposte che trasportano header Set-Cookie |

**Suggerimento**: Dopo aver selezionato un pacchetto, tasto destro → Follow → TCP Stream per vedere richiesta/risposta in chiaro.

#### Filtri concreti forniti solo per l'handshake (SYN e SYN-ACK)

Per vedere i pacchetti dell'handshake TCP sulla porta 8000:

- **SYN e SYN-ACK**: `tcp.port == 8000 && tcp.flags.syn == 1`
- **Solo SYN iniziale**: `tcp.flags.syn == 1 && tcp.flags.ack == 0`
- **Solo SYN-ACK**: `tcp.flags.syn == 1 && tcp.flags.ack == 1`

**Nota**: Il terzo passo dell'handshake (ACK senza SYN) non ha il flag SYN attivo, quindi con questi filtri non compare. Dopo aver trovato lo stream, usa `tcp.stream eq <N>` e guarda i primi tre pacchetti per vedere l'handshake completo.

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
| Set-Cookie sessionid | **Presente** (SI) | **Assente** (NO) |
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
