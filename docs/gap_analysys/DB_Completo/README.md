# Istruzioni Ripristino Database

Questo pacchetto contiene i dump di backup per ripristinare in locale il Knowledge Graph (Neo4j) e il Vector DB (Qdrant).

**File necessari forniti:**
1. `neo4j_full_backup.dump`
2. `qdrant_full_backup.tar.gz`

---

## 1. Come ripristinare Neo4j

Assicuratevi di avere il container di Neo4j creato e posizionatevi da terminale nella cartella dove avete salvato il file `neo4j_full_backup.dump`.

*Nota: Sostituite `mio_neo4j` con il nome del vostro container locale.*

**Step 1: Fermate il database**
docker stop mio_neo4j

**Step 2: Caricate il dump**
Eseguite questo comando per sovrascrivere i dati attuali con quelli del dump tramite un container temporaneo:

docker run --rm --volumes-from mio_neo4j -v "$(pwd):/backup" neo4j neo4j-admin database load neo4j --from-path=/backup --overwrite-destination=true

*(Se il terminale restituisce un errore sulla versione dell'immagine "neo4j", aggiungete il tag che utilizzate di solito, ad esempio "neo4j:5").*

**Step 3: Riaccendete il database**
docker start mio_neo4j

Il grafo è ora ripristinato e accessibile all'indirizzo http://localhost:7474.

---

## 2. Come ripristinare Qdrant

Per Qdrant basta rimpiazzare i file fisici dello storage locale collegato al container.

*Nota: Sostituite `mio_qdrant` con il nome del vostro container locale.*

**Step 1: Fermate il database**
docker stop mio_qdrant

**Step 2: Sostituite lo storage**
1. Individuate la cartella locale del vostro PC mappata come volume per Qdrant (solitamente `/qdrant/storage` nel file `docker-compose.yml`).
2. Svuotate completamente quella cartella locale.
3. Scompattate il file `qdrant_full_backup.tar.gz` e copiate tutto il suo contenuto all'interno della cartella locale appena svuotata.

**Step 3: Riaccendete il database**
docker start mio_qdrant

I vettori sono ora ripristinati e accessibili dalla dashboard all'indirizzo http://localhost:6333/dashboard.