"""Palette colori semantici e token tipografici.

Allineato al prototipo `docs/STCA_Platform_v2.html` (palette navy/orange STCA).
Importa sempre da qui — mai colori inline nel codice UI.
"""

from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# Palette STCA (mirror dell'HTML)
# ---------------------------------------------------------------------------

# Sidebar / navy
COLOR_NAVY = "#0D0D1A"
COLOR_NAVY_2 = "#16162B"
COLOR_NAVY_3 = "#21213A"

# Brand orange (primary)
COLOR_OR = "#E87722"
COLOR_OR_2 = "#F5913A"
COLOR_OR_PALE = "#FEF3E8"
COLOR_OR_MID = "#FDDCBB"

# Backgrounds
COLOR_BG = "#F5F4F1"
COLOR_SF = "#FFFFFF"
COLOR_SF_2 = "#F8F7F5"
COLOR_BD = "rgba(0,0,0,0.07)"
COLOR_BD_2 = "rgba(0,0,0,0.12)"

# Text
COLOR_T1 = "#0D0D1A"
COLOR_T2 = "#4A4A62"
COLOR_T3 = "#8A8AA4"

# Semantic
COLOR_GN = "#15803D"
COLOR_GN_BG = "#F0FDF4"
COLOR_GN_BD = "#BBF7D0"
COLOR_AM = "#A16207"
COLOR_AM_BG = "#FEFCE8"
COLOR_AM_BD = "#FDE68A"
COLOR_RD = "#B91C1C"
COLOR_RD_BG = "#FEF2F2"
COLOR_RD_BD = "#FECACA"
COLOR_BL = "#1D4ED8"
COLOR_BL_BG = "#EFF6FF"
COLOR_BL_BD = "#BFDBFE"
COLOR_GO = "#78350F"
COLOR_GO_BG = "#FEF3C7"
COLOR_GO_BD = "#FDE68A"
COLOR_GR_BG = "#F9FAFB"
COLOR_GR_BD = "#E5E7EB"
COLOR_GR_T = "#6B7280"

# ---------------------------------------------------------------------------
# Backward-compat alias (vecchi nomi usati dal frontend originale)
# ---------------------------------------------------------------------------

COLOR_BG_PRIMARY = COLOR_SF
COLOR_BG_SECONDARY = COLOR_BG
COLOR_BORDER = "#D3D1C7"
COLOR_TEXT_PRIMARY = COLOR_T1
COLOR_TEXT_SECONDARY = COLOR_T2

COLOR_GO_LEGACY = "#1D9E75"  # vecchio verde "decisione GO"
COLOR_GO_RESERVATIONS = "#BA7517"
COLOR_NO_GO = COLOR_RD
COLOR_INFO = COLOR_BL
COLOR_PARTIAL = "#888780"

COLOR_VEM_NAVY = COLOR_NAVY
COLOR_VEM_ORANGE = COLOR_OR

# ---------------------------------------------------------------------------
# Mapping semantici
# ---------------------------------------------------------------------------

# Decisione (legacy)
DECISION_COLORS: dict[str, str] = {
    "GO": COLOR_GO_LEGACY,
    "GO_WITH_RESERVATIONS": COLOR_GO_RESERVATIONS,
    "NO_GO": COLOR_NO_GO,
}
DECISION_LABELS: dict[str, str] = {
    "GO": "GO",
    "GO_WITH_RESERVATIONS": "GO con riserve",
    "NO_GO": "NO GO",
}
DECISION_ICONS: dict[str, str] = {"GO": "✅", "GO_WITH_RESERVATIONS": "⚠️", "NO_GO": "❌"}

# Stato bando HTML (analisi/go/no-go/vinta/persa/pending/go_cond)
BANDO_STATUS_LABELS: dict[str, str] = {
    "analisi": "● In analisi",
    "go": "✓ Go",
    "no-go": "⊘ No-Go",
    "vinta": "🏆 Vinta",
    "persa": "✕ Persa",
    "pending": "○ Da analizzare",
    "go_cond": "~ Go condizionale",
}
BANDO_STATUS_TONE: dict[str, str] = {
    "analisi": "analisi",
    "go": "go",
    "no-go": "nogo",
    "vinta": "vinta",
    "persa": "persa",
    "pending": "pending",
    "go_cond": "cond",
}

# Filtri dashboard
DASH_FILTER_LABELS: dict[str, str] = {
    "all": "Tutti",
    "analisi": "In analisi",
    "go": "Go",
    "no-go": "No-Go",
    "vinta": "Vinte",
    "persa": "Perse",
    "pending": "Da analizzare",
}

# Severity (legacy)
SEVERITY_COLORS: dict[str, str] = {
    "CRITICAL": COLOR_NO_GO,
    "MAJOR": COLOR_GO_RESERVATIONS,
    "MINOR": COLOR_PARTIAL,
}
MATCH_STATUS_COLORS: dict[str, str] = {
    "FULL": COLOR_GO_LEGACY,
    "PARTIAL": COLOR_GO_RESERVATIONS,
    "NONE": COLOR_NO_GO,
    "UNKNOWN": COLOR_PARTIAL,
}
MATCH_STATUS_LABELS: dict[str, str] = {
    "FULL": "Completo",
    "PARTIAL": "Parziale",
    "NONE": "Assente",
    "UNKNOWN": "Da verificare",
}
CATEGORY_COLORS: dict[str, str] = {
    "QUALIFICAZIONE": "#6366F1",
    "NORMATIVA": "#0EA5E9",
    "TECNICA": "#8B5CF6",
    "AMMINISTRATIVA": "#64748B",
}
CATEGORY_LABELS: dict[str, str] = {
    "QUALIFICAZIONE": "Qualificazione",
    "NORMATIVA": "Normativa",
    "TECNICA": "Tecnica",
    "AMMINISTRATIVA": "Amministrativa",
}
EVIDENCE_TYPE_COLORS: dict[str, str] = {
    "CERTIFICATION": "#6366F1",
    "REFERENCE": "#0EA5E9",
    "COMPETENCY": "#8B5CF6",
    "FINANCIAL": "#10B981",
    "DOCUMENT": "#64748B",
    "PARTNERSHIP": "#F59E0B",
}
EVIDENCE_TYPE_LABELS: dict[str, str] = {
    "CERTIFICATION": "Certificazioni",
    "REFERENCE": "Referenze",
    "COMPETENCY": "Competenze",
    "FINANCIAL": "Finanziario",
    "DOCUMENT": "Documenti",
    "PARTNERSHIP": "Partnership",
}
STATUS_COLORS: dict[str, str] = {
    "COMPLETED": COLOR_GO_LEGACY,
    "FAILED": COLOR_NO_GO,
    "QUEUED": COLOR_PARTIAL,
    "PARSING": COLOR_INFO,
    "EXTRACTING": COLOR_INFO,
    "ANALYZING": COLOR_INFO,
    "SCORING": COLOR_INFO,
    "REPORTING": COLOR_INFO,
}
STATUS_LABELS: dict[str, str] = {
    "QUEUED": "In coda",
    "PARSING": "Parsing documento",
    "EXTRACTING": "Estrazione requisiti",
    "ANALYZING": "Analisi gap",
    "SCORING": "Scoring",
    "REPORTING": "Generazione report",
    "COMPLETED": "Completata",
    "FAILED": "Errore",
}


# ---------------------------------------------------------------------------
# Helpers HTML — badge / chip / etc.
# ---------------------------------------------------------------------------


def bando_status_badge(status: str) -> str:
    """HTML del badge stato bando (allineato a .b-* dell'HTML)."""
    label = BANDO_STATUS_LABELS.get(status, status)
    tone = BANDO_STATUS_TONE.get(status, "pending")
    return f'<span class="stca-badge stca-b-{tone}">{label}</span>'


def fmt_val(v: float) -> str:
    """Formatta un valore € come l'HTML (M, K, full)."""
    if v >= 1_000_000:
        return f"€ {v / 1_000_000:.2f}M"
    if v >= 1_000:
        return f"€ {round(v / 1_000)}K"
    return f"€ {v:,.0f}".replace(",", ".")


# ---------------------------------------------------------------------------
# CSS injection
# ---------------------------------------------------------------------------


def inject_custom_css() -> None:
    """Inietta CSS che ricalca il prototipo `STCA_Platform_v2.html`."""
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {{
  --stca-navy: {COLOR_NAVY};
  --stca-navy2: {COLOR_NAVY_2};
  --stca-or: {COLOR_OR};
  --stca-or2: {COLOR_OR_2};
  --stca-or-pale: {COLOR_OR_PALE};
  --stca-or-mid: {COLOR_OR_MID};
  --stca-bg: {COLOR_BG};
  --stca-sf: {COLOR_SF};
  --stca-sf2: {COLOR_SF_2};
  --stca-bd: {COLOR_BD};
  --stca-bd2: {COLOR_BD_2};
  --stca-t1: {COLOR_T1};
  --stca-t2: {COLOR_T2};
  --stca-t3: {COLOR_T3};
  --stca-gn: {COLOR_GN};
  --stca-gn-bg: {COLOR_GN_BG};
  --stca-gn-bd: {COLOR_GN_BD};
  --stca-am: {COLOR_AM};
  --stca-am-bg: {COLOR_AM_BG};
  --stca-am-bd: {COLOR_AM_BD};
  --stca-rd: {COLOR_RD};
  --stca-rd-bg: {COLOR_RD_BG};
  --stca-rd-bd: {COLOR_RD_BD};
  --stca-bl: {COLOR_BL};
  --stca-bl-bg: {COLOR_BL_BG};
  --stca-bl-bd: {COLOR_BL_BD};
  --stca-go: {COLOR_GO};
  --stca-go-bg: {COLOR_GO_BG};
  --stca-go-bd: {COLOR_GO_BD};
  --stca-gr-bg: {COLOR_GR_BG};
  --stca-gr-bd: {COLOR_GR_BD};
  --stca-gr-t: {COLOR_GR_T};
}}

/* Tipografia globale */
html, body, .stApp, [class*="st-emotion"] {{
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
  color: {COLOR_T1};
}}
.stApp {{
  background: {COLOR_BG};
}}
code, .stCodeBlock, .stCode {{
  font-family: 'JetBrains Mono', monospace !important;
}}

/* Eccezione: ripristino il font icona Material Symbols sugli elementi
   interni di Streamlit (collapse sidebar, expander/status, icone widget) —
   altrimenti il glyph appare come testo (es. "keyboard_double_arrow_left"
   o "expand_more" per st.status). */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] *,
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapsedControl"] *,
[data-testid="stExpandSidebarButton"],
[data-testid="stExpandSidebarButton"] *,
[data-testid="stExpanderIcon"],
[data-testid="stExpanderIcon"] *,
[data-testid="stExpanderIconCheck"],
[data-testid="stExpanderIconCheck"] *,
[data-testid="stExpanderIconError"],
[data-testid="stExpanderIconError"] *,
[data-testid="stExpanderIconSpinner"],
[data-testid="stExpanderIconSpinner"] *,
[data-testid^="stExpanderIcon"],
[data-testid^="stExpanderIcon"] *,
[data-testid="stIconMaterial"],
[data-testid="stMaterialIcon"],
[data-testid="stToolbarActionButton"] *,
[data-testid="stToolbarActionButtonIcon"],
[data-testid="baseButton-headerNoPadding"] *,
button [class*="st-emotion"][class*="icon" i] {{
  font-family:
    'Material Symbols Rounded',
    'Material Symbols Outlined',
    'Material Symbols Sharp',
    'Material Icons' !important;
}}

/* Padding superiore ridotto */
.stMainBlockContainer {{
  padding-top: 1.6rem !important;
  padding-bottom: 3rem !important;
}}

/* ────────────────────────────────────────────────
   SIDEBAR — versione semplificata, navy STCA
   ──────────────────────────────────────────────── */

section[data-testid="stSidebar"] {{
  background: {COLOR_NAVY} !important;
  border-right: 1px solid rgba(255,255,255,.06);
}}
section[data-testid="stSidebar"] > div {{
  background: {COLOR_NAVY} !important;
}}

/* Tutti i testi della sidebar di default bianchi-grigi */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] a {{
  color: rgba(255,255,255,.7);
}}

/* Page links: stilizzazione (catch-all, non dipende dal testid esatto) */
section[data-testid="stSidebar"] a[href] {{
  background: transparent !important;
  border-radius: 8px !important;
  padding: 8px 12px !important;
  margin-bottom: 2px !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  text-decoration: none !important;
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  color: rgba(255,255,255,.6) !important;
  min-height: 0 !important;
}}
section[data-testid="stSidebar"] a[href]:hover {{
  background: rgba(255,255,255,.07) !important;
  color: #fff !important;
}}
section[data-testid="stSidebar"] a[href][aria-current="page"] {{
  background: rgba(232,119,34,.20) !important;
  color: {COLOR_OR_2} !important;
}}
section[data-testid="stSidebar"] a[href] * {{
  color: inherit !important;
  font-weight: inherit !important;
  font-size: inherit !important;
}}

/* Sezione labels — bianco semi-trasparente, chiaramente visibile */
.stca-sb-section {{
  font-size: 10px !important;
  font-weight: 700 !important;
  color: rgba(255,255,255,.45) !important;
  letter-spacing: .14em !important;
  padding: 16px 12px 6px 12px !important;
  text-transform: uppercase !important;
}}

/* Logo */
.stca-sb-logo {{
  padding: 4px 12px 14px 12px;
  border-bottom: 1px solid rgba(255,255,255,.08);
  margin-bottom: 4px;
}}
.stca-sb-logo .mark {{
  font-size: 16px !important;
  font-weight: 700 !important;
  color: #fff !important;
  letter-spacing: .04em;
}}
.stca-sb-logo .sub {{
  font-size: 10.5px !important;
  color: rgba(255,255,255,.5) !important;
  margin-top: 3px;
  line-height: 1.25;
}}

/* User box — fixed in basso usando position */
section[data-testid="stSidebar"] {{
  position: relative !important;
}}
.stca-sb-user {{
  margin-top: 24px;
  padding: 12px 12px 8px 12px;
  border-top: 1px solid rgba(255,255,255,.08);
  display: flex;
  align-items: center;
  gap: 10px;
  background: {COLOR_NAVY};
}}
.stca-sb-user .av {{
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(232,119,34,.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11.5px;
  font-weight: 700;
  color: {COLOR_OR_2};
  flex-shrink: 0;
}}
.stca-sb-user .name {{
  font-size: 12px !important;
  font-weight: 500 !important;
  color: rgba(255,255,255,.9) !important;
  line-height: 1.2;
}}
.stca-sb-user .role {{
  font-size: 10.5px !important;
  color: rgba(255,255,255,.45) !important;
  line-height: 1.2;
  margin-top: 1px;
}}

/* ────────────────────────────────────────────────
   BUTTONS — primary orange
   ──────────────────────────────────────────────── */
button[kind="primary"], .stButton button[kind="primary"] {{
  background: {COLOR_OR} !important;
  color: #fff !important;
  border: 1px solid {COLOR_OR} !important;
  font-weight: 500 !important;
  border-radius: 8px !important;
}}
button[kind="primary"]:hover {{
  background: {COLOR_OR_2} !important;
  border-color: {COLOR_OR_2} !important;
}}
button[kind="secondary"] {{
  background: {COLOR_SF} !important;
  border: 1px solid {COLOR_BD_2} !important;
  border-radius: 8px !important;
  color: {COLOR_T1} !important;
  font-weight: 500 !important;
}}
button[kind="secondary"]:hover {{
  background: {COLOR_SF_2} !important;
  border-color: {COLOR_T3} !important;
}}

/* ────────────────────────────────────────────────
   STCA components — stat card, brow, chip, badge
   ──────────────────────────────────────────────── */

/* Topbar */
.stca-topbar {{
  background: {COLOR_SF};
  border-bottom: 1px solid {COLOR_BD};
  padding: 12px 18px;
  border-radius: 12px;
  margin-bottom: 14px;
}}
.stca-topbar h2 {{ font-size: 15px; font-weight: 600; margin: 0; }}
.stca-topbar .sub {{ font-size: 11.5px; color: {COLOR_T3}; margin-top: 2px; }}

/* Stat grid */
.stca-stat-card {{
  background: {COLOR_SF};
  border: 1px solid {COLOR_BD};
  border-radius: 8px;
  padding: 12px 14px;
}}
.stca-stat-lbl {{
  font-size: 9.5px;
  color: {COLOR_T3};
  margin-bottom: 4px;
  font-weight: 500;
  letter-spacing: .02em;
  text-transform: uppercase;
}}
.stca-stat-val {{
  font-size: 22px;
  font-weight: 600;
  font-family: 'JetBrains Mono', monospace;
  line-height: 1;
}}

/* Chip */
.stca-chip {{
  display: inline-block;
  font-size: 11px;
  padding: 4px 11px;
  border-radius: 100px;
  border: 1px solid {COLOR_BD_2};
  color: {COLOR_T2};
  background: {COLOR_SF};
  cursor: pointer;
  margin-right: 4px;
  margin-bottom: 4px;
  user-select: none;
  text-decoration: none;
}}
.stca-chip:hover {{ border-color: {COLOR_OR}; color: {COLOR_OR}; }}
.stca-chip.on {{ background: {COLOR_OR_PALE}; border-color: {COLOR_OR_MID}; color: {COLOR_OR}; font-weight: 500; }}

/* Chip clickable wrapper using streamlit buttons */
div[data-testid="stHorizontalBlock"] .stca-chip {{
  display: inline-block;
}}

/* Bando row */
.stca-brow {{
  display: grid;
  grid-template-columns: 2fr 1fr 80px 100px 75px 95px;
  gap: 8px;
  padding: 10px 12px;
  background: {COLOR_SF};
  border: 1px solid {COLOR_BD};
  border-radius: 8px;
  margin-bottom: 3px;
  align-items: center;
  transition: all .12s;
  cursor: pointer;
  text-decoration: none;
  color: inherit;
}}
.stca-brow:hover {{
  border-color: {COLOR_OR_MID};
  box-shadow: 0 1px 6px rgba(232,119,34,.1);
}}
.stca-brow-name {{ font-size: 12px; font-weight: 500; color: {COLOR_T1}; }}
.stca-brow-cpv {{ font-size: 10px; color: {COLOR_T3}; margin-top: 1px; }}
.stca-brow-ente {{ font-size: 11px; color: {COLOR_T2}; }}
.stca-brow-val {{ font-size: 11.5px; font-weight: 500; font-family: 'JetBrains Mono', monospace; }}
.stca-brow-urgent {{ color: {COLOR_RD}; font-weight: 600; }}
.stca-brow-channel {{ font-size: 11px; color: {COLOR_T2}; }}
.stca-tbl-hd {{
  display: grid;
  grid-template-columns: 2fr 1fr 80px 100px 75px 95px;
  gap: 8px;
  padding: 5px 12px;
  font-size: 9.5px;
  font-weight: 600;
  color: {COLOR_T3};
  letter-spacing: .07em;
  text-transform: uppercase;
}}

/* Badges (b-*) */
.stca-badge {{
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 8px;
  border-radius: 100px;
  font-size: 10.5px;
  font-weight: 500;
  white-space: nowrap;
  border: 1px solid transparent;
}}
.stca-b-analisi {{ background: {COLOR_BL_BG}; color: {COLOR_BL}; border-color: {COLOR_BL_BD}; }}
.stca-b-go {{ background: {COLOR_GN_BG}; color: {COLOR_GN}; border-color: {COLOR_GN_BD}; }}
.stca-b-nogo {{ background: {COLOR_RD_BG}; color: {COLOR_RD}; border-color: {COLOR_RD_BD}; }}
.stca-b-vinta {{ background: {COLOR_GO_BG}; color: {COLOR_GO}; border-color: {COLOR_GO_BD}; }}
.stca-b-persa {{ background: {COLOR_GR_BG}; color: {COLOR_GR_T}; border-color: {COLOR_GR_BD}; }}
.stca-b-pending {{ background: {COLOR_SF_2}; color: {COLOR_T3}; border-color: {COLOR_BD_2}; }}
.stca-b-cond {{ background: #FFF7ED; color: #C2410C; border-color: #FED7AA; }}

/* Card */
.stca-card {{
  background: {COLOR_SF};
  border: 1px solid {COLOR_BD};
  border-radius: 12px;
  padding: 16px;
}}
.stca-card-sm {{
  background: {COLOR_SF};
  border: 1px solid {COLOR_BD};
  border-radius: 8px;
  padding: 12px;
}}

/* Tag tipo requisito */
.stca-tag {{
  font-size: 9.5px;
  padding: 2px 7px;
  border-radius: 100px;
  font-weight: 600;
  white-space: nowrap;
  border: 1px solid transparent;
}}
.stca-tag-esc {{ background: {COLOR_RD_BG}; color: {COLOR_RD}; border-color: {COLOR_RD_BD}; }}
.stca-tag-pref {{ background: {COLOR_AM_BG}; color: {COLOR_AM}; border-color: {COLOR_AM_BD}; }}
.stca-tag-info {{ background: {COLOR_BL_BG}; color: {COLOR_BL}; border-color: {COLOR_BL_BD}; }}

/* Match pill */
.stca-mp {{
  font-size: 10px;
  padding: 3px 8px;
  border-radius: 100px;
  white-space: nowrap;
  display: inline-block;
  border: 1px solid transparent;
}}
.stca-mp-gn {{ background: {COLOR_GN_BG}; color: {COLOR_GN}; border-color: {COLOR_GN_BD}; }}
.stca-mp-am {{ background: {COLOR_AM_BG}; color: {COLOR_AM}; border-color: {COLOR_AM_BD}; }}
.stca-mp-rd {{ background: {COLOR_RD_BG}; color: {COLOR_RD}; border-color: {COLOR_RD_BD}; }}
.stca-mp-gr {{ background: {COLOR_GR_BG}; color: {COLOR_GR_T}; border-color: {COLOR_GR_BD}; }}

/* Requisito row */
.stca-req-table {{
  background: {COLOR_SF};
  border: 1px solid {COLOR_BD};
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 14px;
}}
.stca-req-sec-hd {{
  font-size: 9.5px;
  font-weight: 700;
  color: {COLOR_T3};
  letter-spacing: .07em;
  padding: 8px 12px;
  background: {COLOR_SF_2};
  border-bottom: 1.5px solid {COLOR_BD_2};
  display: flex;
  justify-content: space-between;
  align-items: center;
  text-transform: uppercase;
}}
.stca-req-row {{
  display: grid;
  grid-template-columns: 16px 1fr 70px 110px 170px;
  gap: 8px;
  padding: 9px 12px;
  border-bottom: 1px solid {COLOR_BD};
  align-items: start;
  font-size: 12px;
}}
.stca-req-row:last-child {{ border-bottom: none; }}
.stca-req-row.warn {{ border-left: 3px solid #D97706; background: #FFFDF4; }}
.stca-req-row.alert {{ border-left: 3px solid {COLOR_RD}; background: #FFFBFB; }}
.stca-req-dot {{
  width: 8px; height: 8px; border-radius: 50%;
  margin-top: 4px;
}}
.stca-d-gn {{ background: #16A34A; }}
.stca-d-am {{ background: #D97706; }}
.stca-d-rd {{ background: #DC2626; }}
.stca-d-gr {{ background: #9CA3AF; }}
.stca-req-txt {{ color: {COLOR_T1}; line-height: 1.4; }}
.stca-req-note {{ font-size: 10px; color: {COLOR_T3}; margin-top: 2px; line-height: 1.35; }}
.stca-req-note.wn {{ color: #92400E; font-weight: 500; }}
.stca-req-note.rn {{ color: {COLOR_RD}; font-weight: 600; }}
.stca-req-fonte {{ font-size: 10.5px; color: {COLOR_T3}; font-family: 'JetBrains Mono', monospace; }}

/* Checklist */
.stca-pb-wrap {{ height: 6px; background: {COLOR_BD}; border-radius: 100px; overflow: hidden; margin-bottom: 14px; }}
.stca-pb-fill {{ height: 100%; background: {COLOR_GN}; border-radius: 100px; transition: width .5s ease; }}
.stca-chk-item {{
  display: flex; align-items: flex-start; gap: 9px;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid transparent;
  margin-bottom: 2px;
}}
.stca-chk-item.done .stca-chk-lbl {{ text-decoration: line-through; color: {COLOR_T3}; }}
.stca-chk-item.urgente {{ background: {COLOR_RD_BG}; border-color: {COLOR_RD_BD}; }}
.stca-chk-item.warn-chk {{ background: {COLOR_AM_BG}; border-color: {COLOR_AM_BD}; }}
.stca-chk-box {{
  width: 16px; height: 16px;
  border-radius: 4px;
  border: 1.5px solid {COLOR_BD_2};
  flex-shrink: 0; margin-top: 1px;
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; color: #fff;
}}
.stca-chk-item.done .stca-chk-box {{ background: {COLOR_GN}; border-color: {COLOR_GN}; }}
.stca-chk-lbl {{ font-size: 12px; color: {COLOR_T1}; line-height: 1.4; }}
.stca-chk-sub {{ font-size: 10px; color: {COLOR_T3}; margin-top: 1px; }}
.stca-chk-sub.urgent {{ color: {COLOR_RD}; font-weight: 600; }}

/* Score gauge / score bars */
.stca-score-bar {{ height: 5px; background: {COLOR_BD}; border-radius: 100px; overflow: hidden; }}
.stca-score-fill {{ height: 100%; border-radius: 100px; }}
.stca-ai-box {{
  background: {COLOR_AM_BG};
  border-left: 3px solid #D97706;
  border-radius: 0 8px 8px 0;
  padding: 9px 11px;
  margin-top: 10px;
}}
.stca-kpi-card {{
  background: {COLOR_SF};
  border: 1px solid {COLOR_BD};
  border-radius: 8px;
  padding: 11px 12px;
}}
.stca-kpi-lbl {{ font-size: 10px; color: {COLOR_T3}; margin-bottom: 3px; }}
.stca-kpi-val {{ font-size: 18px; font-weight: 600; font-family: 'JetBrains Mono', monospace; line-height: 1; }}
.stca-info-card-t {{ font-size: 11px; font-weight: 600; margin-bottom: 7px; }}

/* Info row (key/val) */
.stca-irow {{ display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid {COLOR_BD}; font-size: 11.5px; gap: 6px; }}
.stca-irow:last-child {{ border-bottom: none; }}
.stca-irow .k {{ color: {COLOR_T3}; }}
.stca-irow .v {{ color: {COLOR_T1}; font-weight: 500; text-align: right; flex: 1; }}

/* Upload zone */
.stca-uzone {{
  border: 2px dashed {COLOR_BD_2};
  border-radius: 12px;
  padding: 28px;
  text-align: center;
  margin-bottom: 14px;
}}
.stca-uzone:hover {{ border-color: {COLOR_OR}; background: {COLOR_OR_PALE}; }}
.stca-file-chip {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 10.5px;
  padding: 4px 10px;
  background: {COLOR_SF_2};
  border: 1px solid {COLOR_BD_2};
  border-radius: 8px;
  margin: 3px 3px 3px 0;
}}
.stca-agent-bar {{
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 10px 13px;
  background: {COLOR_SF};
  border: 1px solid {COLOR_BD};
  border-radius: 8px;
  margin-bottom: 16px;
}}
.stca-beta-tag {{
  font-size: 9px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 100px;
  background: {COLOR_OR_PALE};
  color: {COLOR_OR};
  border: 1px solid {COLOR_OR_MID};
  margin-left: 5px;
}}
.stca-notif {{
  padding: 12px 13px;
  border-bottom: 1px solid {COLOR_BD};
}}
.stca-notif:last-child {{ border-bottom: none; }}

/* Roadmap row */
.stca-road-row {{
  display: grid;
  grid-template-columns: 2.3fr 60px 110px 100px 1fr;
  gap: 8px;
  padding: 10px 12px;
  background: {COLOR_SF};
  border: 1px solid {COLOR_BD};
  border-radius: 8px;
  margin-bottom: 3px;
  align-items: center;
}}
.stca-road-row.crit {{ background: {COLOR_RD_BG}; border-color: {COLOR_RD_BD}; }}
.stca-road-row.warn {{ background: {COLOR_AM_BG}; border-color: {COLOR_AM_BD}; }}
.stca-road-hd {{
  display: grid;
  grid-template-columns: 2.3fr 60px 110px 100px 1fr;
  gap: 8px;
  padding: 5px 12px;
  font-size: 9.5px;
  font-weight: 600;
  color: {COLOR_T3};
  letter-spacing: .07em;
  text-transform: uppercase;
}}
.stca-freq-bar {{ height: 4px; background: {COLOR_BD}; border-radius: 100px; overflow: hidden; margin-top: 3px; }}
.stca-freq-fill {{ height: 100%; border-radius: 100px; }}
.stca-prio-pill {{
  font-size: 11px;
  padding: 4px 11px;
  border-radius: 100px;
  font-weight: 500;
  margin-right: 6px;
  display: inline-block;
}}

/* Alert section */
.stca-alrt-hd {{
  font-size: 10.5px;
  font-weight: 600;
  padding: 8px 12px;
  border-radius: 8px 8px 0 0;
  display: flex; align-items: center; gap: 6px;
  text-transform: uppercase;
  letter-spacing: .04em;
}}
.stca-alrt-row {{
  padding: 10px 13px;
  border-bottom: 1px solid {COLOR_BD};
  display: flex; align-items: center; gap: 10px;
}}
.stca-alrt-row:last-child {{ border-bottom: none; }}
.stca-days-pill {{
  font-size: 10.5px;
  padding: 3px 9px;
  border-radius: 100px;
  font-weight: 600;
  font-family: 'JetBrains Mono', monospace;
  white-space: nowrap;
}}
.stca-cert-tbl {{ width: 100%; border-collapse: collapse; font-size: 11.5px; }}
.stca-cert-tbl th {{
  font-size: 9.5px; font-weight: 600;
  color: {COLOR_T3}; letter-spacing: .06em;
  padding: 7px 10px;
  text-align: left;
  background: {COLOR_SF_2};
  border-bottom: 1px solid {COLOR_BD};
}}
.stca-cert-tbl td {{
  padding: 8px 10px;
  border-bottom: 1px solid {COLOR_BD};
}}
.stca-cert-tbl tr:last-child td {{ border-bottom: none; }}

/* Insight box */
.stca-insight {{
  padding: 10px 14px;
  background: {COLOR_SF};
  border: 1px solid {COLOR_BD};
  border-left: 3px solid {COLOR_OR};
  border-radius: 0 8px 8px 0;
  font-size: 11.5px;
  color: {COLOR_T2};
  line-height: 1.5;
  margin-top: 12px;
}}

/* Breadcrumb */
.stca-breadcrumb {{
  display: flex; align-items: center; gap: 6px;
  font-size: 11px;
  color: {COLOR_T3};
  margin-bottom: 6px;
}}
.stca-breadcrumb .sep {{ opacity: .5; }}
.stca-breadcrumb .cur {{ color: {COLOR_T1}; font-weight: 500; }}
.stca-meta {{
  display: flex; gap: 12px; font-size: 11px; color: {COLOR_T2}; margin-top: 4px; flex-wrap: wrap;
}}
.stca-urgency {{ color: {COLOR_RD}; font-weight: 600; }}
.stca-legend {{ display: flex; gap: 14px; flex-wrap: wrap; }}
.stca-leg-i {{ display: flex; align-items: center; gap: 5px; font-size: 10.5px; color: {COLOR_T3}; }}
.stca-leg-dot {{ width: 7px; height: 7px; border-radius: 50%; }}

/* Hide stuff (deploy, decoration, hamburger) */
.stAppDeployButton, .stDeployButton,
[data-testid="stHeaderActionElements"],
div[data-testid="stDeployButton"],
#MainMenu,
div[data-testid="stDecoration"] {{
  display: none !important;
}}
header {{ background-color: transparent !important; }}

/* Tertiary buttons left-aligned (legacy) */
button[data-testid="stBaseButton-tertiary"],
button[kind="tertiary"] {{
  justify-content: flex-start !important;
  text-align: left !important;
  padding-left: 0 !important;
}}

/* Hide tender_detail from sidebar nav (link not shown) */
a[data-testid="stSidebarNavLink"][href*="tender_detail"] {{
  display: none !important;
}}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {{
  background: {COLOR_SF};
  border-bottom: 1px solid {COLOR_BD};
  padding: 0 8px;
  border-radius: 8px 8px 0 0;
  gap: 4px;
}}
.stTabs [data-baseweb="tab"] {{
  font-size: 12px;
  font-weight: 500;
  color: {COLOR_T3};
  padding: 10px 16px;
  border-bottom: 2px solid transparent;
}}
.stTabs [data-baseweb="tab"][aria-selected="true"] {{
  color: {COLOR_OR};
  border-bottom-color: {COLOR_OR};
}}

/* Section header */
.stca-sec-hd {{
  font-size: 12px;
  font-weight: 600;
  color: {COLOR_T1};
  margin: 6px 0 9px 0;
  display: flex; align-items: center; justify-content: space-between;
}}

/* Reset margins dei markdown container DENTRO i st.container(key=...) STCA — evita
   l'overlap del testo col bordo card (descenders + spacing default di Streamlit). */
[class*="st-key-"] [data-testid="stMarkdownContainer"] {{
  margin: 0 !important;
}}
[class*="st-key-"] [data-testid="stMarkdownContainer"] > *:last-child {{
  margin-bottom: 0 !important;
}}

/* ────────────────────────────────────────────────
   STCA layout grids — replicano l'HTML 1:1
   ──────────────────────────────────────────────── */

/* Topbar header con sub e azioni a destra */
.stca-topbar .head-row {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}}
.stca-topbar h2 {{ font-size: 15px; font-weight: 600; margin: 0; }}
.stca-topbar .sub {{ font-size: 11.5px; color: {COLOR_T3}; margin-top: 3px; }}

/* Stat grid (5 colonne come HTML) */
.stca-stat-grid {{
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  margin-bottom: 14px;
}}
.stca-stat-grid.cols-4 {{ grid-template-columns: repeat(4, 1fr); }}

/* Filter bar */
.stca-filter-bar {{
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}}

/* Bandi table grid identico HTML */
.stca-brow,
.stca-tbl-hd {{
  display: grid;
  grid-template-columns: 2fr 1fr 80px 100px 75px 95px;
  gap: 6px;
  align-items: center;
}}

/* Pulsanti come anchor (rimangono link ma sembrano bottoni) */
.stca-btn,
.stca-btn-pr {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-family: inherit;
  font-size: 12px;
  font-weight: 500;
  padding: 7px 14px;
  border-radius: 8px;
  text-decoration: none;
  cursor: pointer;
  border: 1px solid {COLOR_BD_2};
  background: {COLOR_SF};
  color: {COLOR_T1};
  transition: all .12s;
}}
.stca-btn:hover {{ background: {COLOR_SF_2}; border-color: {COLOR_T3}; }}
.stca-btn-pr {{
  background: {COLOR_OR};
  color: #fff !important;
  border-color: {COLOR_OR};
}}
.stca-btn-pr:hover {{ background: {COLOR_OR_2}; border-color: {COLOR_OR_2}; }}
.stca-btn-sm {{ font-size: 11px; padding: 4px 10px; }}
.stca-btn-rd {{
  background: {COLOR_RD_BG};
  color: {COLOR_RD} !important;
  border-color: {COLOR_RD_BD};
}}
.stca-btn-gn {{
  background: {COLOR_GN_BG};
  color: {COLOR_GN} !important;
  border-color: {COLOR_GN_BD};
}}

/* Stat-card colorate */
.stca-stat-val.c-bl {{ color: {COLOR_BL}; }}
.stca-stat-val.c-gn {{ color: {COLOR_GN}; }}
.stca-stat-val.c-rd {{ color: {COLOR_RD}; }}
.stca-stat-val.c-am {{ color: {COLOR_AM}; }}

/* Anchor reset — niente underline su tutti gli stca-* anchors */
a.stca-brow, a.stca-brow:hover, a.stca-brow:visited,
a.stca-chip, a.stca-chip:hover, a.stca-chip:visited,
a.stca-btn, a.stca-btn:hover, a.stca-btn:visited,
a.stca-btn-pr, a.stca-btn-pr:hover, a.stca-btn-pr:visited,
a.stca-btn-sm, a.stca-btn-sm:hover, a.stca-btn-sm:visited,
a.stca-btn-gn, a.stca-btn-gn:hover, a.stca-btn-gn:visited,
a.stca-btn-rd, a.stca-btn-rd:hover, a.stca-btn-rd:visited {{
  color: inherit;
  text-decoration: none !important;
}}
a.stca-btn-pr, a.stca-btn-pr:hover, a.stca-btn-pr:visited {{ color: #fff !important; }}

/* Search input STCA */
.stca-search-wrap input {{
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: 12px !important;
  padding: 6px 11px !important;
  border: 1px solid {COLOR_BD_2} !important;
  border-radius: 8px !important;
  background: {COLOR_SF} !important;
  outline: none !important;
}}
.stca-search-wrap input:focus {{
  border-color: {COLOR_OR} !important;
  box-shadow: 0 0 0 2px rgba(232,119,34,.12) !important;
}}

/* Chip-style Streamlit buttons (key="dash_chips") */
.st-key-dash_chips [data-testid="stHorizontalBlock"] {{
  gap: 6px !important;
  flex-wrap: wrap;
  align-items: center;
}}
.st-key-dash_chips [data-testid="stColumn"] {{
  flex: 0 0 auto !important;
  width: auto !important;
}}
.st-key-dash_chips [data-testid="stElementContainer"] {{ width: auto !important; }}
.st-key-dash_chips button {{
  font-size: 11px !important;
  padding: 4px 12px !important;
  border-radius: 100px !important;
  font-weight: 500 !important;
  min-height: 0 !important;
  height: auto !important;
  white-space: nowrap !important;
}}
.st-key-dash_chips button[kind="secondary"] {{
  background: {COLOR_SF} !important;
  border: 1px solid {COLOR_BD_2} !important;
  color: {COLOR_T2} !important;
}}
.st-key-dash_chips button[kind="secondary"]:hover {{
  border-color: {COLOR_OR} !important;
  color: {COLOR_OR} !important;
}}
.st-key-dash_chips button[kind="primary"] {{
  background: {COLOR_OR_PALE} !important;
  border: 1px solid {COLOR_OR_MID} !important;
  color: {COLOR_OR} !important;
}}

/* Topbar row (key="dash_topbar") — title sx + search + bottone Nuovo bando */
.st-key-dash_topbar {{
  background: {COLOR_SF};
  border: 1px solid {COLOR_BD};
  border-radius: 12px;
  padding: 16px 20px 18px 20px;
  margin-bottom: 18px;
}}
.st-key-dash_topbar [data-testid="stHorizontalBlock"] {{
  gap: 14px !important;
  align-items: center;
}}
.st-key-dash_topbar [data-testid="stMarkdownContainer"] {{
  margin: 0 !important;
  padding: 0 !important;
}}
.st-key-dash_topbar h2 {{
  font-size: 15px;
  font-weight: 600;
  margin: 0 !important;
  padding: 0 !important;
  line-height: 1.25;
}}
.st-key-dash_topbar .sub {{
  font-size: 11.5px;
  color: {COLOR_T3};
  margin: 4px 0 2px 0;
  line-height: 1.3;
}}
.st-key-dash_topbar [data-testid="stTextInput"] input {{
  font-size: 12px !important;
  padding: 6px 11px !important;
  border-radius: 8px !important;
}}
.st-key-dash_topbar button {{
  background: {COLOR_OR} !important;
  color: #fff !important;
  border: 1px solid {COLOR_OR} !important;
  border-radius: 8px !important;
  font-weight: 500 !important;
  font-size: 12px !important;
  white-space: nowrap !important;
}}
.st-key-dash_topbar button:hover {{ background: {COLOR_OR_2} !important; border-color: {COLOR_OR_2} !important; }}

/* ────────────────────────────────────────────────
   REPOSITORY page
   ──────────────────────────────────────────────── */

/* Upload zone — puramente decorativa (HTML, niente file_uploader Streamlit).
   Replica il `.uzone` del prototipo HTML. */
.stca-uzone {{
  border: 2px dashed {COLOR_BD_2};
  border-radius: 12px;
  background: {COLOR_SF};
  padding: 28px 22px;
  text-align: center;
  margin-bottom: 16px;
  transition: all .15s;
}}
.stca-uzone:hover {{
  border-color: {COLOR_OR};
  background: {COLOR_OR_PALE};
}}
.stca-uzone .cloud {{
  font-size: 30px;
  color: {COLOR_T3};
  line-height: 1;
  margin-bottom: 8px;
}}
.stca-uzone .title {{
  font-size: 13px;
  font-weight: 500;
  color: {COLOR_T1};
  line-height: 1.3;
}}
.stca-uzone .sub {{
  font-size: 11.5px;
  color: {COLOR_T3};
  margin-top: 4px;
  line-height: 1.3;
}}

/* Pending files card */
.st-key-rep_pending {{
  background: {COLOR_SF};
  border: 1px solid {COLOR_BD};
  border-radius: 8px;
  padding: 14px 16px 16px 16px;
  margin-bottom: 14px;
}}
.st-key-rep_pending [data-testid="stMarkdownContainer"] {{ margin: 0 !important; padding: 0 !important; }}
.st-key-rep_pending [data-testid="stHorizontalBlock"] {{ gap: 7px !important; align-items: center; }}
.st-key-rep_pending button {{
  border-radius: 8px !important;
  font-size: 12px !important;
  font-weight: 500 !important;
}}
.st-key-rep_pending button[kind="primary"] {{
  background: {COLOR_OR} !important;
  color: #fff !important;
  border-color: {COLOR_OR} !important;
}}
.st-key-rep_pending button[kind="primary"]:hover {{
  background: {COLOR_OR_2} !important;
  border-color: {COLOR_OR_2} !important;
}}

/* Agent bar */
.st-key-rep_agent {{
  background: {COLOR_SF};
  border: 1px solid {COLOR_BD};
  border-radius: 8px;
  padding: 14px 16px 16px 16px;
  margin-bottom: 16px;
}}
.st-key-rep_agent [data-testid="stMarkdownContainer"] {{ margin: 0 !important; padding: 0 !important; }}
.st-key-rep_agent [data-testid="stHorizontalBlock"] {{
  gap: 12px !important;
  align-items: center;
}}
.st-key-rep_agent button {{
  border-radius: 8px !important;
  font-size: 12px !important;
  white-space: nowrap !important;
}}
.st-key-rep_agent button[kind="primary"] {{
  background: {COLOR_OR} !important;
  color: #fff !important;
  border-color: {COLOR_OR} !important;
}}
.st-key-rep_agent button[kind="primary"]:hover {{
  background: {COLOR_OR_2} !important;
  border-color: {COLOR_OR_2} !important;
}}

/* EDR card "Da avviare" */
.st-key-rep_edr {{
  background: {COLOR_SF};
  border: 1px solid {COLOR_BD};
  border-radius: 12px;
  padding: 16px 18px 18px 18px;
  margin-bottom: 18px;
}}
.st-key-rep_edr [data-testid="stMarkdownContainer"] {{ margin: 0 !important; padding: 0 !important; }}
.st-key-rep_edr [data-testid="stHorizontalBlock"] {{ gap: 14px !important; align-items: center; }}
.st-key-rep_edr button[kind="primary"] {{
  background: {COLOR_OR} !important;
  color: #fff !important;
  border-color: {COLOR_OR} !important;
  border-radius: 8px !important;
  font-size: 12px !important;
  font-weight: 500 !important;
}}
.st-key-rep_edr button[kind="primary"]:hover {{
  background: {COLOR_OR_2} !important;
  border-color: {COLOR_OR_2} !important;
}}

/* ────────────────────────────────────────────────
   TENDER DETAIL page
   ──────────────────────────────────────────────── */

/* Back button + topbar */
.st-key-tdet_back button {{
  background: transparent !important;
  border: none !important;
  color: {COLOR_T3} !important;
  font-size: 11.5px !important;
  padding: 0 !important;
  font-weight: 500 !important;
}}
.st-key-tdet_back button:hover {{ color: {COLOR_OR} !important; }}

/* Chip filtri tab Requisiti */
.st-key-tdet_req_chips [data-testid="stHorizontalBlock"] {{
  gap: 6px !important;
  flex-wrap: wrap;
  align-items: center;
}}
.st-key-tdet_req_chips [data-testid="stColumn"] {{
  flex: 0 0 auto !important;
  width: auto !important;
}}
.st-key-tdet_req_chips [data-testid="stElementContainer"] {{ width: auto !important; }}
.st-key-tdet_req_chips button {{
  font-size: 11px !important;
  padding: 4px 12px !important;
  border-radius: 100px !important;
  font-weight: 500 !important;
  min-height: 0 !important;
  height: auto !important;
  white-space: nowrap !important;
}}
.st-key-tdet_req_chips button[kind="secondary"] {{
  background: {COLOR_SF} !important;
  border: 1px solid {COLOR_BD_2} !important;
  color: {COLOR_T2} !important;
}}
.st-key-tdet_req_chips button[kind="secondary"]:hover {{
  border-color: {COLOR_OR} !important;
  color: {COLOR_OR} !important;
}}
.st-key-tdet_req_chips button[kind="primary"] {{
  background: {COLOR_OR_PALE} !important;
  border: 1px solid {COLOR_OR_MID} !important;
  color: {COLOR_OR} !important;
}}

/* Requirement rows — grid 6 col compatto */
[class*="st-key-tdet_req_row_"] {{
  border-bottom: 1px solid {COLOR_BD};
  padding: 0;
  margin: 0;
}}
[class*="st-key-tdet_req_row_"] [data-testid="stMarkdownContainer"] {{
  margin: 0 !important;
  padding: 0 !important;
}}
[class*="st-key-tdet_req_row_"] [data-testid="stElementContainer"] {{
  margin: 0 !important;
  padding: 0 !important;
}}
[class*="st-key-tdet_req_row_"] [data-testid="stVerticalBlock"] {{
  gap: 0 !important;
}}
[class*="st-key-tdet_req_row_"] [data-testid="stHorizontalBlock"] {{
  gap: 8px !important;
  padding: 5px 12px !important;
  align-items: center !important;
}}
[class*="st-key-tdet_req_row_"][data-warn="1"] {{
  border-left: 3px solid #D97706;
  background: #FFFDF4;
}}
[class*="st-key-tdet_req_row_"][data-alert="1"] {{
  border-left: 3px solid {COLOR_RD};
  background: #FFFBFB;
}}

/* Bottoni Revisiona/Gestisci dentro la riga — compatti */
[class*="st-key-tdet_req_row_"] button {{
  font-size: 10.5px !important;
  padding: 3px 10px !important;
  border-radius: 8px !important;
  min-height: 0 !important;
  height: 26px !important;
  line-height: 1 !important;
  white-space: nowrap !important;
}}
[class*="st-key-tdet_req_row_"] button[kind="primary"] {{
  background: {COLOR_RD_BG} !important;
  color: {COLOR_RD} !important;
  border: 1px solid {COLOR_RD_BD} !important;
}}
[class*="st-key-tdet_req_row_"] button[kind="primary"]:hover {{
  background: #FEE2E2 !important;
}}

/* Pannello revisione inline (rev-panel) */
[class*="st-key-tdet_req_rev_"] {{
  background: {COLOR_SF_2};
  border: 1px solid {COLOR_BD_2};
  border-radius: 8px;
  padding: 14px 16px 16px 16px;
  margin: 4px 0 12px 32px;
}}
[class*="st-key-tdet_req_rev_"] [data-testid="stMarkdownContainer"] {{
  margin: 0 !important;
  padding: 0 !important;
}}
[class*="st-key-tdet_req_rev_"] button[kind="primary"] {{
  background: {COLOR_OR} !important;
  color: #fff !important;
  border-color: {COLOR_OR} !important;
  border-radius: 8px !important;
  font-size: 12px !important;
}}

/* Checklist items — compatti */
[class*="st-key-tdet_chk_item_"] {{
  padding: 0;
  border-radius: 6px;
  margin: 0 0 1px 0;
}}
[class*="st-key-tdet_chk_item_"] [data-testid="stMarkdownContainer"] {{
  margin: 0 !important;
  padding: 0 !important;
}}
[class*="st-key-tdet_chk_item_"] [data-testid="stElementContainer"] {{
  margin: 0 !important;
  padding: 0 !important;
}}
[class*="st-key-tdet_chk_item_"] [data-testid="stVerticalBlock"] {{
  gap: 0 !important;
}}
[class*="st-key-tdet_chk_item_"] [data-testid="stHorizontalBlock"] {{
  gap: 8px !important;
  padding: 4px 10px !important;
  align-items: center !important;
}}
[class*="st-key-tdet_chk_item_"][data-urgente="1"] {{
  background: {COLOR_RD_BG};
  border: 1px solid {COLOR_RD_BD};
}}
[class*="st-key-tdet_chk_item_"][data-warn="1"] {{
  background: {COLOR_AM_BG};
  border: 1px solid {COLOR_AM_BD};
}}
/* Checkbox più compatto */
[class*="st-key-tdet_chk_item_"] [data-testid="stCheckbox"] {{
  margin: 0 !important;
  padding: 0 !important;
}}
[class*="st-key-tdet_chk_item_"] [data-testid="stCheckbox"] label {{
  margin: 0 !important;
  padding: 0 !important;
  min-height: 0 !important;
}}
[class*="st-key-tdet_chk_item_"] [data-testid="stCheckbox"] > label > div:first-child {{
  width: 14px !important;
  height: 14px !important;
}}
/* Chk label/sub testuali leggermente più stretti */
[class*="st-key-tdet_chk_item_"] .stca-chk-lbl {{
  font-size: 11.5px;
  line-height: 1.3;
}}
[class*="st-key-tdet_chk_item_"] .stca-chk-sub {{
  font-size: 9.5px;
  line-height: 1.25;
  margin-top: 1px;
}}

/* Tab Checklist toolbar */
.st-key-tdet_chk_toolbar [data-testid="stHorizontalBlock"] {{
  gap: 10px !important;
  align-items: center;
}}
.st-key-tdet_chk_toolbar button {{
  font-size: 12px !important;
  border-radius: 8px !important;
}}
.st-key-tdet_chk_mark_all button {{
  background: {COLOR_GN_BG} !important;
  color: {COLOR_GN} !important;
  border: 1px solid {COLOR_GN_BD} !important;
  border-radius: 8px !important;
  font-size: 12px !important;
}}

/* ────────────────────────────────────────────────
   SETTINGS page
   ──────────────────────────────────────────────── */

.st-key-set_topbar {{
  background: {COLOR_SF};
  border: 1px solid {COLOR_BD};
  border-radius: 12px;
  padding: 14px 18px 16px 18px;
  margin-bottom: 14px;
}}
.st-key-set_topbar h2 {{ font-size: 15px; font-weight: 600; margin: 0; }}

[class*="st-key-set_card_"] {{
  background: {COLOR_SF};
  border: 1px solid {COLOR_BD};
  border-radius: 12px;
  padding: 14px 18px 16px 18px;
  margin-bottom: 12px;
}}
[class*="st-key-set_card_"] [data-testid="stMarkdownContainer"] {{ margin: 0 !important; }}
[class*="st-key-set_card_"] [data-testid="stHorizontalBlock"] {{
  gap: 10px !important;
  align-items: center !important;
  margin-top: 12px !important;
}}
[class*="st-key-set_card_"] button {{
  font-size: 12px !important;
  border-radius: 8px !important;
}}
[class*="st-key-set_card_"] button[kind="primary"] {{
  background: {COLOR_OR} !important;
  color: #fff !important;
  border-color: {COLOR_OR} !important;
}}
[class*="st-key-set_card_"] button[kind="primary"]:hover {{
  background: {COLOR_OR_2} !important;
  border-color: {COLOR_OR_2} !important;
}}

/* ────────────────────────────────────────────────
   ALERT page
   ──────────────────────────────────────────────── */

.st-key-alr_topbar {{
  background: {COLOR_SF};
  border: 1px solid {COLOR_BD};
  border-radius: 12px;
  padding: 14px 18px 16px 18px;
  margin-bottom: 14px;
}}
.st-key-alr_topbar h2 {{ font-size: 15px; font-weight: 600; margin: 0; }}
.st-key-alr_topbar .sub {{ font-size: 11.5px; color: {COLOR_T3}; margin-top: 3px; }}

/* Row alert urgenti — testo sx + days-pill + bottone "Avvia rinnovo" */
[class*="st-key-alr_urgent_"] {{
  background: {COLOR_RD_BG};
  border-left: 1px solid {COLOR_RD_BD};
  border-right: 1px solid {COLOR_RD_BD};
  padding: 0;
}}
[class*="st-key-alr_urgent_"]:first-of-type {{ border-top: 1px solid {COLOR_RD_BD}; }}
[class*="st-key-alr_urgent_"]:last-of-type {{
  border-bottom: 1px solid {COLOR_RD_BD};
  border-radius: 0 0 8px 8px;
  margin-bottom: 14px;
}}
[class*="st-key-alr_urgent_"] [data-testid="stMarkdownContainer"] {{ margin: 0 !important; }}
[class*="st-key-alr_urgent_"] [data-testid="stHorizontalBlock"] {{
  gap: 10px !important;
  align-items: center !important;
  padding: 10px 14px !important;
}}
[class*="st-key-alr_urgent_"] button {{
  background: {COLOR_RD_BG} !important;
  color: {COLOR_RD} !important;
  border: 1px solid {COLOR_RD_BD} !important;
  font-size: 11px !important;
  border-radius: 8px !important;
  white-space: nowrap !important;
}}
[class*="st-key-alr_urgent_"] button:hover {{ background: #FEE2E2 !important; }}

/* Row scadenza bandi 60gg */
[class*="st-key-alr_bando_"] {{
  background: {COLOR_SF};
  border-left: 1px solid {COLOR_BD};
  border-right: 1px solid {COLOR_BD};
  padding: 0;
}}
[class*="st-key-alr_bando_"]:first-of-type {{ border-top: 1px solid {COLOR_BD}; }}
[class*="st-key-alr_bando_"]:last-of-type {{
  border-bottom: 1px solid {COLOR_BD};
  border-radius: 0 0 8px 8px;
  margin-bottom: 14px;
}}
[class*="st-key-alr_bando_"] [data-testid="stMarkdownContainer"] {{ margin: 0 !important; }}
[class*="st-key-alr_bando_"] [data-testid="stHorizontalBlock"] {{
  gap: 10px !important;
  align-items: center !important;
  padding: 10px 14px !important;
}}
[class*="st-key-alr_bando_"] button {{
  background: {COLOR_OR} !important;
  color: #fff !important;
  border-color: {COLOR_OR} !important;
  font-size: 11px !important;
  border-radius: 8px !important;
  white-space: nowrap !important;
}}
[class*="st-key-alr_bando_"] button:hover {{
  background: {COLOR_OR_2} !important;
  border-color: {COLOR_OR_2} !important;
}}

/* ────────────────────────────────────────────────
   ROADMAP page
   ──────────────────────────────────────────────── */

.st-key-rmp_topbar {{
  background: {COLOR_SF};
  border: 1px solid {COLOR_BD};
  border-radius: 12px;
  padding: 16px 20px 18px 20px;
  margin-bottom: 16px;
}}
.st-key-rmp_topbar [data-testid="stHorizontalBlock"] {{
  gap: 10px !important;
  align-items: center;
}}
.st-key-rmp_topbar h2 {{ font-size: 15px; font-weight: 600; margin: 0; }}
.st-key-rmp_topbar .sub {{ font-size: 11.5px; color: {COLOR_T3}; margin-top: 3px; }}
.st-key-rmp_topbar button {{
  border-radius: 8px !important;
  font-size: 12px !important;
  white-space: nowrap !important;
}}
.st-key-rmp_topbar button[kind="primary"] {{
  background: {COLOR_OR} !important;
  color: #fff !important;
  border-color: {COLOR_OR} !important;
}}
.st-key-rmp_topbar button[kind="primary"]:hover {{
  background: {COLOR_OR_2} !important;
  border-color: {COLOR_OR_2} !important;
}}

/* Tab Go/No-Go decision bar */
.st-key-tdet_gng_dec [data-testid="stHorizontalBlock"] {{
  gap: 10px !important;
  align-items: center;
}}
.st-key-tdet_gng_dec button {{
  font-size: 12px !important;
  border-radius: 8px !important;
  padding: 8px 14px !important;
  font-weight: 500 !important;
}}
.st-key-tdet_gng_dec button[kind="primary"] {{
  background: {COLOR_OR} !important;
  color: #fff !important;
  border-color: {COLOR_OR} !important;
}}

/* Notification rows */
[class*="st-key-rep_notif_"] {{
  background: {COLOR_SF};
  border: 1px solid {COLOR_BD};
  border-radius: 0;
  border-bottom: none;
  padding: 14px 16px 16px 16px;
}}
[class*="st-key-rep_notif_"]:first-of-type {{
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
}}
[class*="st-key-rep_notif_"]:last-of-type {{
  border-bottom: 1px solid {COLOR_BD};
  border-bottom-left-radius: 12px;
  border-bottom-right-radius: 12px;
  margin-bottom: 14px;
}}
[class*="st-key-rep_notif_"] [data-testid="stMarkdownContainer"] {{
  margin: 0 !important;
  padding: 0 !important;
}}
[class*="st-key-rep_notif_"] [data-testid="stHorizontalBlock"] {{
  gap: 8px !important;
  align-items: center;
}}
[class*="st-key-rep_notif_"] button {{
  font-size: 11px !important;
  padding: 4px 10px !important;
  border-radius: 8px !important;
  white-space: nowrap !important;
}}
[class*="st-key-rep_notif_"] button[kind="primary"] {{
  background: {COLOR_OR} !important;
  color: #fff !important;
  border-color: {COLOR_OR} !important;
}}
[class*="st-key-rep_notif_"] button[kind="primary"]:hover {{
  background: {COLOR_OR_2} !important;
  border-color: {COLOR_OR_2} !important;
}}
</style>
        """,
        unsafe_allow_html=True,
    )
