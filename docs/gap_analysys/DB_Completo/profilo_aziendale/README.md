# Profilo Aziendale Vivo — TechServ Italia S.p.A. (ESEMPIO DIDATTICO)

Questo pacchetto contiene il Profilo Aziendale Vivo di esempio per il progetto
Smart Tender Compliance Assistant — BOOM Gen AI Innovation Sprint 2026.

> **Nota:** core.json, referenze.json e certificazioni.json usano dati
> dell'azienda fittizia TechServ Italia S.p.A. (solo scopo didattico).
> Il file **competenze.json** è stato aggiornato con i dati reali del
> **Gruppo VEM** (VEM Sistemi + Certego) dal documento interno
> "Certificazioni_per_offerte_gruppo_VEM_rev_20-04-2026".

## Struttura

```
profilo_aziendale/
  core.json              → Dati anagrafici, fatturato, iscrizioni        [TechServ — fittizio]
  certificazioni.json    → Registry certificazioni con stato validità     [TechServ — fittizio]
  referenze.json         → Portfolio contratti con requisiti_dimostrati[] [TechServ — fittizio]
  competenze.json        → Skill tecniche con livello evidenza            [VEM Sistemi — REALE]
  coda_revisione.json    → Requisiti nuovi emersi — da esaminare         [TechServ — fittizio]
  storico_gare/
    gara_202503_comune_bologna_rete.json   → Gara vinta (GO → VINTA)
    gara_202501_ospedale_edr.json          → Gara non partecipata (NO_GO)
```

## Contenuto di competenze.json (dati reali Gruppo VEM)

| Area | N. skill | N. tag gara |
|------|----------|-------------|
| Cybersecurity — Network & Endpoint Security | 11 | ~45 |
| Networking & SD-WAN | 6 | ~30 |
| Cloud & Virtualizzazione | 7 | ~25 |
| Data Center & Storage | 3 | ~15 |
| Data Protection, Backup & BC | 4 | ~15 |
| Collaboration, AV & UC | 5 | ~20 |
| OT / Industrial & Building Automation | 4 | ~15 |
| Cybersecurity — Certificazioni Personali | 16 | ~40 |
| Project Management & Governance | 4 | ~12 |
| **TOTALE** | **60** | **~217** |

Certificazioni aziendali indipendenti: 6 VEM Sistemi + 10 Certego.

## Come usare

Vedi la Guida Rapida PDF inclusa nel pacchetto ZIP.
Funzione di caricamento: `load_profilo('./profilo_aziendale')` — vedi doc tecnico v2.0.
