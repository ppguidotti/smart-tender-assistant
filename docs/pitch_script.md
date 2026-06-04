# Pitch — Smart Tender Compliance Assistant (STCA)
### BOOM × GEN AI Innovation Sprint 2026 · VEM Sistemi · Milano, 11 giugno 2026
**Durata target: 10 min (demo inclusa) · Stile: pitch startup**

> Budget tempo a fondo pagina. I `[…]` sono numeri che DEVI sostituire con dati reali/difendibili prima della presentazione.
> La giuria valuta 6 criteri (1–5): esposizione, sostenibilità, allineamento mercato, qualità tecnica AI, innovazione, fattibilità. Ogni sezione qui sotto è ancorata ad almeno uno.

---

## 0 · Hook / Cold open — 0:00–0:30 (30s)
*Una frase, niente "buongiorno siamo il team X". Apri sul dolore.*

> "Un commerciale senior di una system integration apre un bando della PA: 80 pagine, 30 requisiti nascosti tra rinvii normativi e tabelle. Gli servono **ore** solo per capire se può partecipare. E se sbaglia un requisito escludente, l'offerta è già persa prima di scriverla.
> Noi quelle ore le abbiamo trasformate in **minuti** — con una decisione tracciabile e auditabile. Questo è Smart Tender Compliance Assistant."

*Coperti: esposizione, innovazione (anticipo).*

---

## 1 · Problema + Chi (target persona) — 0:30–2:00 (90s)

**Il pain (4 punti, secchi):**
- **Tempo**: analisi manuale di un bando PA medio = ore-uomo di un pre-sales senior. Collo di bottiglia su una risorsa costosa.
- **Errore costoso**: il match requisiti ↔ certificazioni è fatto a mano → una svista su un requisito **escludente** = offerta persa o esclusione in gara.
- **Zero standardizzazione**: ogni analista ha il suo metodo → decisioni GO/NO-GO non confrontabili nel tempo.
- **Knowledge loss**: l'esperienza su gare passate (referenze, gap risolti, esiti) resta nella testa delle persone, non in un sistema.

**Chi è (il target, qui — non dopo):**
- **Utente interno**: pre-sales / ufficio gare / business developer di **system integrator e fornitori IT** che vendono alla PA.
- **Segmento**: **B2B** (e B2B2G — il cliente finale è la Pubblica Amministrazione).
- Lo diciamo con un volto: *"Il nostro utente è Marco, ufficio gare di VEM. Oggi fa questo lavoro a mano. Vediamo cosa gli mettiamo in mano."*

**Perché è rilevante / vale l'investimento:**
> Ogni gara non valutata o valutata male è fatturato potenziale perso. Per chi vive di gare PA, la velocità e l'accuratezza dell'analisi GO/NO-GO **sono** il vantaggio competitivo.

*Coperti: allineamento mercato, esposizione.*

---

## 2 · Soluzione — 2:00–3:30 (90s)
*Cosa è, in una riga, poi come funziona, poi il differenziatore.*

> "STCA legge un bando, lo confronta con il profilo aziendale, e in pochi minuti produce una decisione **GO/NO-GO motivata, tracciabile e auditabile**. Non è un estrattore di requisiti: è un **assistente decisionale**."

**Come funziona — pipeline in 4 mosse (mostra il diagramma):**
1. **Ingestion** — qualsiasi formato (PDF nativi/scansionati, DOCX, allegati) → testo strutturato che preserva articoli, tabelle, riferimenti.
2. **Estrazione requisiti (LLM)** — ogni requisito classificato: categoria (normativa/tecnica/amministrativa), tipo (**escludente**/preferenziale), fonte, riferimenti normativi, evidenze richieste, penali.
3. **Gap Analysis** — match requisito-per-requisito col profilo: `full / partial / none`, severità, rimedio suggerito. **Gap critici (escludenti) separati dai minori.**
4. **Scoring & Decisione** — hard gate sugli escludenti (un solo gap critico → NO-GO) + checklist amministrativa auto-generata.

**Il differenziatore (dillo forte, è il nostro asso):**
> "**Tracciabilità non negoziabile**: ogni singola affermazione del sistema linka all'articolo e alla pagina di origine. Per la PA non è un nice-to-have — è la differenza tra un output usabile in gara e un black-box inutilizzabile. È il nostro vantaggio rispetto a un ChatGPT generico."

*Coperti: qualità tecnica AI, innovazione, esposizione.*

---

## 3 · DEMO LIVE — 3:30–6:15 (~2:45) ⭐
*Il cuore. Tenila stretta sullo "happy path". Niente debugging dal vivo: usa dati già pronti.*

**Caso d'uso narrato:** "Carico il capitolato della gara EDR — quella reale, anonimizzata. Guardate."

**Sequenza schermate (da `demo.html`), con cosa dire su ognuna:**

1. **Caricamento + "🤖 Analisi AI in corso"** (~15s)
   > "Trascino il PDF. Parte la pipeline: ingestion → M1 estrazione → M2/M3 normativa+gap → score."

2. **M1 — Estrazione requisiti** (~45s) — *qui mostri il differenziatore*
   > "Ha trovato **30 requisiti**. Notate: ognuno ha la **fonte cliccabile** — Art. 8 del capitolato. Click → mi porta esattamente al punto del documento. Questa è la tracciabilità."
   > "E ha capito una cosa che conta: in questa gara **tutti i requisiti sono escludenti**. Nessun punteggio — è un pass/fail. Sbagliarne uno = fuori."

3. **M2+M3 — Gap certificazioni** (~45s)
   > "Confronto col profilo aziendale: **X gap escludenti, Y preferenziali**. Per ognuno il sistema dice cosa manca e come rimediare. Qui c'è un vendor lock-in flaggato automaticamente."

4. **Output — Score & GO/NO-GO** (~40s) — *il momento clou*
   > "Decisione: **✓ GO — Presentare offerta**, con la motivazione leggibile e la **checklist amministrativa** (CIG, CUP, IBAN dedicato, MePA) già pronta. Da ore a **questo**, in minuti."

**Regola d'oro demo:** se qualcosa va storto, hai gli screenshot di backup nelle slide. Non improvvisare debugging.

*Coperti: fattibilità (funziona!), qualità tecnica, innovazione.*

---

## 4 · Mercato & Business case — 6:15–7:45 (90s)
*Ora che hanno visto che funziona, sizing + sostenibilità.*

**Mercato (B2B, fornitori IT della PA italiana):**
- Spesa pubblica italiana in appalti ≈ **€[…] mld/anno**; la quota ICT/digitale gestita via MePA/gare è il bacino. *(inserisci stima difendibile, cita la fonte)*
- **Target diretto (SAM)**: system integrator e fornitori IT che partecipano a gare PA — **[…] aziende** in Italia. Ognuna gestisce **[…] gare/anno**.

**Business case / sostenibilità (NF6 — costo per gara):**
- **Valore generato**: da ~[…] ore/uomo per analisi a < 5 minuti → risparmio diretto sul personale più costoso + più gare valutabili a parità di organico.
- **Costo per gara analizzata**: ~€[…] di compute LLM → margine enorme vs ore-uomo risparmiate. *(metti il numero, è la domanda che ti farà la giuria sulla sostenibilità)*
- **Modello**: SaaS B2B per posti / per gara, oppure on-prem per chi ha vincoli di confidenzialità sul profilo aziendale e storico gare (NF4).

*Coperti: allineamento mercato, sostenibilità.*

---

## 5 · Competitor & Differenziazione — 7:45–8:45 (60s)
*Tabella mentale: 3 colonne.*

| Alternativa | Limite |
|---|---|
| **ChatGPT / LLM generico** | Nessuna tracciabilità, allucina riferimenti normativi, niente gap analysis sul *tuo* profilo, non auditabile → inutilizzabile in gara PA |
| **Analisi manuale (status quo)** | Lenta, non standardizzata, knowledge persa, soggetta a sviste sugli escludenti |
| **Piattaforme gare/info-provider** (es. monitoraggio bandi) | Ti *trovano* il bando, non ti dicono **se puoi/devi parteciparci** né dove sei carente |

**La nostra wedge:**
> "Siamo gli unici che uniscono **estrazione tracciabile** + **gap analysis sul profilo reale dell'azienda** + **decisione auditabile**. E il sistema **impara**: ogni gara chiusa arricchisce il profilo aziendale come knowledge base."

*Coperti: innovazione, allineamento mercato.*

---

## 6 · Team — 8:45–9:30 (45s)
*Breve. Perché VOI siete quelli giusti.*
- [Nome — ruolo]: architettura / LLM strategy / document processing.
- [Nome — ruolo]: [block ownership].
- [Nome — ruolo]: [block ownership].
> "Mix di competenze su LLM, data engineering e dominio gare PA. Architettura **modulare a 10 blocchi** con contratti stabili — costruita per evolvere oltre l'hackathon, non solo per la demo."

*Coperti: fattibilità, qualità tecnica.*

---

## 7 · Vision / Close / Ask — 9:30–10:00 (30s)
*Chiudi sul futuro + una frase memorabile. Stesso tono dell'hook.*

> "Oggi: da ore a minuti su una gara. Domani: un profilo aziendale che si arricchisce da solo a ogni gara, che ti dice **prima** quali bandi vincerai e quali gap colmare per vincerne di più.
> Smart Tender Compliance Assistant — la decisione GO/NO-GO, tracciabile, in minuti. Grazie."

*(Ricorda: dopo ci sono 5 min di Q&A della giuria — tieni pronti i numeri di costo/gara e la fonte del sizing di mercato.)*

---

## ⏱ Budget tempo
| # | Sezione | Durata | Cumulato |
|---|---|---|---|
| 0 | Hook | 0:30 | 0:30 |
| 1 | Problema + Chi | 1:30 | 2:00 |
| 2 | Soluzione | 1:30 | 3:30 |
| 3 | **DEMO LIVE** | **2:45** | 6:15 |
| 4 | Mercato & Business | 1:30 | 7:45 |
| 5 | Competitor | 1:00 | 8:45 |
| 6 | Team | 0:45 | 9:30 |
| 7 | Vision/Close | 0:30 | 10:00 |

## Checklist pre-pitch
- [ ] Sostituire tutti i `[…]` con numeri reali (sizing mercato + **costo/gara** + ore risparmiate).
- [ ] Screenshot di backup di OGNI schermata demo nelle slide (se la live cade).
- [ ] Provare la demo 2× col PDF EDR reale; cronometrare i tempi di pipeline.
- [ ] Decidere chi parla quando (1 voce per la demo, max 2 speaker totali per fluidità).
- [ ] Preparare 3 risposte Q&A: costo/gara, privacy profilo (on-prem vs cloud), precisione vs golden test.
