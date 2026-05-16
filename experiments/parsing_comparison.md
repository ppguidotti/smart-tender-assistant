# Confronto parsing documentale: Apache Tika vs LLM/Azure

## Obiettivo

Confrontare possibili approcci per estrarre e strutturare informazioni da bandi di gara.

## Approcci

### Apache Tika

Scopo:
- estrazione di testo grezzo e metadati da PDF/DOCX.

Pro:
- deterministico
- economico
- eseguibile localmente
- buona baseline multi-formato

Contro:
- nessuna comprensione semantica
- possibile fragilità con tabelle, scansioni, layout complessi

### LLM / Azure

Scopo:
- estrazione strutturata di informazioni rilevanti.

Campi potenziali:
- requisiti amministrativi
- requisiti tecnici
- requisiti economici
- certificazioni richieste
- scadenze
- documentazione richiesta
- segnali GO/NO-GO

Pro:
- comprensione semantica
- classificazione e normalizzazione
- utile per gap analysis

Contro:
- costo
- latenza
- necessità di validazione
- rischio allucinazioni se non ancorato a testo reale

## Prima ipotesi architetturale

Approccio consigliato:

Apache Tika come layer di estrazione  
LLM/Azure come layer di comprensione e classificazione

Pipeline:

1. caricamento documento
2. estrazione testo con Tika
3. pulizia / chunking
4. estrazione strutturata via LLM
5. validazione schema JSON
6. scoring GO/NO-GO

## Primo test su gara 3222-25

Cartella analizzata: `data/raw/bandi_gara_pubblici/3222-25`

### Primo avvio

Risultato iniziale con `tika-python`:

- documenti totali: 5
- parsing riusciti: 3
- parsing falliti: 2
- caratteri estratti: 68.582

Errori osservati:

- `Unable to start Tika server.`
- `HTTPConnectionPool(host='localhost', port=9998): Read timed out. (read timeout=60)`

### Secondo avvio / server già inizializzato

Risultato dopo warm-up del server Tika:

- documenti totali: 5
- parsing riusciti: 5
- parsing falliti: 0
- caratteri estratti: 91.200

### Osservazione

Apache Tika è in grado di estrarre testo utile da tutti i documenti PDF della gara testata.
La criticità principale osservata non riguarda la qualità dell’estrazione, ma l’avvio automatico del server Tika tramite `tika-python`.

Per un uso più stabile nel progetto conviene valutare:

1. Tika server avviato esplicitamente come servizio/container;
2. warm-up iniziale del parser prima dell’elaborazione batch;
3. aumento timeout e retry lato parser;
4. fallback con parser specifici per formato;
5. Azure Document Intelligence per documenti complessi, scansioni o layout tabellari.
