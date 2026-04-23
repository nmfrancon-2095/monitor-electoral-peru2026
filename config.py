# ============================================================
# config.py — Monitor Electoral Perú 2026
# Sistema de diseño completo: colores, tipografía, espaciado, CSS.
# Para cambiar cualquier aspecto visual, empieza aquí.
# Los cambios en este archivo se propagan a todas las páginas.
# ============================================================

# -------------------------------------------------------
# SECTION: Identidad del dashboard
# -------------------------------------------------------
APP_TITLE               = "Monitor Electoral Perú 2026"
APP_SUBTITLE            = "Integridad electoral y riesgos institucionales · Perú 2026"
APP_ICON                = "🗳️"
APP_LOGO                = None
APP_CONFIDENTIAL_LABEL  = "CONFIDENCIAL — Uso interno"
APP_VERSION             = "v1.0"
DATA_FILE               = "data/maestro_dashboard_electoral_v1.xlsx"

# -------------------------------------------------------
# SECTION: Paleta de colores
#
# Basada en UN Blue, informada por OKLCH para coherencia
# perceptual. Los neutrales tienen tinte azulado sutil
# (chroma ~0.01) — nunca gris puro.
#
# Regla 60-30-10:
#   60% → fondos y superficies (BACKGROUND, SURFACE, BORDER)
#   30% → texto y elementos secundarios (TEXT_PRIMARY/SECONDARY)
#   10% → acento y acciones clave (PRIMARY, ACCENT)
# -------------------------------------------------------
COLOR_PRIMARY           = "#1A4F8A"
COLOR_ACCENT            = "#2878B5"

COLOR_BACKGROUND        = "#F2F5F9"
COLOR_SURFACE           = "#FFFFFF"
COLOR_SURFACE_ALT       = "#F8FAFC"
COLOR_BORDER            = "#D8E4EF"
COLOR_BORDER_STRONG     = "#B8CEDF"

COLOR_TEXT_PRIMARY      = "#152638"
COLOR_TEXT_SECONDARY    = "#456078"
COLOR_TEXT_MUTED        = "#7A95A8"

COLOR_RIESGO_ALTO       = "#B83232"
COLOR_RIESGO_ALTO_BG    = "#FDF0F0"
COLOR_RIESGO_MEDIO      = "#D4760A"
COLOR_RIESGO_MEDIO_BG   = "#FEF7EC"
COLOR_RIESGO_BAJO       = "#1E8A4A"
COLOR_RIESGO_BAJO_BG    = "#EEF8F2"
COLOR_RIESGO_NONE       = "#8A9BAA"
COLOR_RIESGO_NONE_BG    = "#F4F6F8"

COLOR_REINFO            = "#B85C0A"
COLOR_REINFO_BG         = "#FEF4EC"

# -------------------------------------------------------
# SECTION: Umbrales de score
# -------------------------------------------------------
SCORE_ALTO_MIN  = 20
SCORE_MEDIO_MIN = 10

# -------------------------------------------------------
# SECTION: Etiquetas de UI
# Sin emojis en títulos de sección ni en labels de filtro.
# Emojis solo en indicadores de estado en tablas (correcto).
# -------------------------------------------------------
LABEL_RIESGO = {
    "alto":  "Alto",
    "medio": "Medio",
    "bajo":  "Bajo",
    "none":  "Sin dato",
}

DOT_RIESGO = {
    "alto":  '<span style="color:#B83232; font-size:0.7em;">●</span>',
    "medio": '<span style="color:#D4760A; font-size:0.7em;">●</span>',
    "bajo":  '<span style="color:#1E8A4A; font-size:0.7em;">●</span>',
    "none":  '<span style="color:#8A9BAA; font-size:0.7em;">●</span>',
}

LABEL_VOTO = {
    "A FAVOR":    "A favor",
    "EN CONTRA":  "En contra",
    "ABSTENCION": "Abstención",
    "AUSENTE":    "Ausente",
    "LICENCIA":   "Licencia",
    "SIN DATO":   "Sin dato",
}

COLOR_VOTO = {
    "A FAVOR":    "#FDECEA",
    "EN CONTRA":  "#EBF5EE",
    "ABSTENCION": "#FEF8E7",
    "AUSENTE":    "#F4F6F8",
    "LICENCIA":   "#F4F6F8",
    "SIN DATO":   "#F4F6F8",
}

COLOR_VOTO_TEXT = {
    "A FAVOR":    "#B83232",
    "EN CONTRA":  "#1E8A4A",
    "ABSTENCION": "#D4760A",
    "AUSENTE":    "#456078",
    "LICENCIA":   "#456078",
    "SIN DATO":   "#7A95A8",
}

# -------------------------------------------------------
# SECTION: Bloques temáticos
# -------------------------------------------------------
BLOQUES = {
    "pro-crimen":     "Pro-crimen",
    "reinfo":         "REINFO",
    "ambiental":      "Ambiental",
    "espacio-civico": "Espacio cívico",
    "bicameralidad":  "Bicameralidad",
}

BLOQUES_LARGO = {
    "pro-crimen":     "Pro-crimen — debilitan el sistema de justicia",
    "reinfo":         "REINFO — registro minero informal",
    "ambiental":      "Ambiental — protección de bosques",
    "espacio-civico": "Espacio cívico — sociedad civil",
    "bicameralidad":  "Bicameralidad — reforma institucional",
}

COLOR_BLOQUE = {
    "pro-crimen":     "#B83232",
    "reinfo":         "#B85C0A",
    "ambiental":      "#1E8A4A",
    "espacio-civico": "#6B4FA0",
    "bicameralidad":  "#2878B5",
}

# -------------------------------------------------------
# SECTION: Columnas de leyes
# -------------------------------------------------------
LEYES_COLS = [
    "L31751 Prescripción 1 año",
    "L31880 Prisión preventiva",
    "L31989 Elimina incautación",
    "L31990 Limita colaboración eficaz",
    "L32054 Exonera partidos",
    "L32104 Interpretación autentica",
    "L32108 Redefine el término organización criminal",
    "L32130 Designa a la PNP para que realice las investigaciones preliminares",
    "L32181 Elimina detención preliminar",
    "L32326 Restringe extinción de dominio",
    "L31388 REINFO 3a amp",
    "L32213 REINFO 4a amp",
    "L32537 REINFO 5a amp",
    "L31973 Ley Forestal",
    "L32301 Ley APCI",
    "L31988 Bicameralidad",
]

REGIONES_PRIORITARIAS = ["Ucayali", "Loreto", "Madre de Dios", "Puno"]

TIPOS_ELECCION = [
    "PRESIDENCIAL",
    "SENADORES DISTRITO ÚNICO",
    "DIPUTADOS",
]

# -------------------------------------------------------
# SECTION: Configuración de gráficos Plotly
# Usa CHART_LAYOUT_BASE con: fig.update_layout(**CHART_LAYOUT_BASE)
# -------------------------------------------------------
CHART_HEIGHT        = 420
CHART_HEIGHT_SMALL  = 280
CHART_HEIGHT_TALL   = 520

CHART_FONT = dict(
    family="'Plus Jakarta Sans', 'DM Sans', system-ui, sans-serif",
    size=12,
    color="#152638",
)

CHART_LAYOUT_BASE = dict(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#F2F5F9",
    font=CHART_FONT,
    margin=dict(l=8, r=8, t=16, b=8),
    legend=dict(
        orientation="h",
        y=-0.15,
        xanchor="left",
        x=0,
        font=dict(size=11),
        bgcolor="rgba(0,0,0,0)",
    ),
    xaxis=dict(
        showgrid=True,
        gridcolor="#D8E4EF",
        zeroline=False,
        tickfont=dict(size=11),
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="#D8E4EF",
        zeroline=False,
        tickfont=dict(size=11),
    ),
)

# -------------------------------------------------------
# SECTION: CSS global
#
# Inyectado en app.py una sola vez. Principios:
#   - Plus Jakarta Sans (Google Fonts) — institucional con carácter
#   - Espaciado sistema 4pt
#   - Tabular numbers para datos numéricos
#   - Sidebar limpio
#   - Componentes reutilizables como clases CSS
# -------------------------------------------------------
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

/* BASE */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'DM Sans', system-ui, -apple-system, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

.stApp { background-color: #F2F5F9; }

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #1A4F8A;
}
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div {
    color: rgba(255,255,255,0.92) !important;
}
section[data-testid="stSidebar"] a {
    color: rgba(255,255,255,0.78) !important;
    font-size: 0.88rem;
    font-weight: 400;
    text-decoration: none;
}
section[data-testid="stSidebar"] a:hover {
    color: #FFFFFF !important;
}

/* MÉTRICAS KPI */
div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #D8E4EF;
    border-radius: 6px;
    padding: 16px 20px 14px 20px;
}
div[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    color: #7A95A8 !important;
}
div[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #152638 !important;
    font-variant-numeric: tabular-nums;
    line-height: 1.1 !important;
}
div[data-testid="stMetricDelta"] {
    font-size: 0.78rem !important;
    color: #456078 !important;
}

/* TABLAS */
[data-testid="stDataFrame"] th {
    background-color: #F2F5F9 !important;
    font-weight: 600 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    color: #456078 !important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 2px solid #D8E4EF;
}
.stTabs [data-baseweb="tab"] {
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: #456078 !important;
    padding: 8px 16px !important;
    border-radius: 4px 4px 0 0 !important;
    border: none !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #1A4F8A !important;
    background: #F2F5F9 !important;
}
.stTabs [aria-selected="true"] {
    color: #1A4F8A !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #1A4F8A !important;
}

/* EXPANDERS */
details[data-testid="stExpander"] {
    border: 1px solid #D8E4EF !important;
    border-radius: 6px !important;
    background: #FFFFFF !important;
    margin-bottom: 8px !important;
}
details[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    color: #152638 !important;
    padding: 12px 16px !important;
}
details[data-testid="stExpander"] summary:hover {
    background: #F2F5F9 !important;
}

/* INPUTS */
[data-testid="stTextInput"] input {
    border-color: #D8E4EF !important;
    border-radius: 5px !important;
    font-size: 0.875rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #2878B5 !important;
    box-shadow: 0 0 0 2px rgba(40,120,181,0.15) !important;
}

/* BOTONES */
.stDownloadButton > button {
    border-radius: 5px !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    border-color: #D8E4EF !important;
    color: #456078 !important;
}
.stDownloadButton > button:hover {
    border-color: #2878B5 !important;
    color: #1A4F8A !important;
}

hr {
    border: none !important;
    border-top: 1px solid #D8E4EF !important;
    margin: 20px 0 !important;
}

/* COMPONENTES REUTILIZABLES */

/* Badges de riesgo */
.badge {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 3px;
    font-size: 0.70rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    line-height: 1.6;
}
.badge-alto    { background: #B83232; color: #FFF; }
.badge-medio   { background: #D4760A; color: #FFF; }
.badge-bajo    { background: #1E8A4A; color: #FFF; }
.badge-reinfo  { background: #B85C0A; color: #FFF; }
.badge-none    { background: #8A9BAA; color: #FFF; }

/* Badge CONFIDENCIAL (para sidebar, fondo oscuro) */
.badge-confidencial {
    display: inline-block;
    background: rgba(255,255,255,0.12);
    color: rgba(255,255,255,0.95);
    border: 1px solid rgba(255,255,255,0.22);
    padding: 3px 10px;
    border-radius: 3px;
    font-size: 0.67rem;
    font-weight: 700;
    letter-spacing: 0.10em;
    text-transform: uppercase;
}

/* Nota informativa */
.nota-info {
    background: #F0F6FB;
    border-left: 3px solid #2878B5;
    border-radius: 0 5px 5px 0;
    padding: 10px 14px;
    font-size: 0.84rem;
    color: #456078;
    line-height: 1.55;
    margin: 8px 0;
}

/* Nota de advertencia */
.nota-warning {
    background: #FEF7EC;
    border-left: 3px solid #D4760A;
    border-radius: 0 5px 5px 0;
    padding: 10px 14px;
    font-size: 0.84rem;
    color: #7A4A08;
    line-height: 1.55;
    margin: 8px 0;
}

/* Encabezados de sección — tipografía con peso, sin emoji */
.section-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: #152638;
    margin: 0 0 2px 0;
    letter-spacing: -0.01em;
}
.section-subheader {
    font-size: 0.80rem;
    color: #7A95A8;
    margin: 0 0 16px 0;
}

/* Card de perfil */
.profile-card {
    background: #FFFFFF;
    border: 1px solid #D8E4EF;
    border-radius: 8px;
    padding: 20px 24px;
}
.profile-field {
    font-size: 0.85rem;
    line-height: 1.85;
    color: #456078;
}
.profile-field strong {
    color: #152638;
    font-weight: 600;
}

/* Score card */
.score-card {
    background: #FFFFFF;
    border-radius: 8px;
    padding: 20px 24px;
    text-align: center;
}
.score-number {
    font-size: 3rem;
    font-weight: 700;
    line-height: 1;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.02em;
}
.score-label {
    font-size: 0.63rem;
    font-weight: 700;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    color: #7A95A8;
    margin-bottom: 4px;
}

/* Footer de página */
.page-footer {
    margin-top: 40px;
    padding-top: 12px;
    border-top: 1px solid #D8E4EF;
    display: flex;
    justify-content: space-between;
    font-size: 0.72rem;
    color: #7A95A8;
}

/* Números tabulares donde sea necesario */
.tabular { font-variant-numeric: tabular-nums; }

/* ── Resultados ONPE ──────────────────────────────── */
.electo-badge {
    display: inline-block;
    background: #1E8A4A;
    color: #FFFFFF;
    font-size: 0.60rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 2px 7px;
    border-radius: 3px;
}
.preliminar-badge {
    display: inline-block;
    background: #D4760A;
    color: #FFFFFF;
    font-size: 0.60rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 2px 7px;
    border-radius: 3px;
}
.escrutinio-bar-wrap {
    background: #D8E4EF;
    border-radius: 4px;
    height: 6px;
    overflow: hidden;
    margin-top: 4px;
}
.escrutinio-bar-fill {
    height: 6px;
    border-radius: 4px;
    background: #1A4F8A;
}

</style>
"""

# -------------------------------------------------------
# SECTION: Datos ONPE — resultados electorales 2026
# -------------------------------------------------------
ONPE_DATA_FILE = "data/onpe_resultados_latest.xlsx"

# Colores oficiales por partido (para hemiciclos y gráficos)
# Basados en identidad visual de cada agrupación
COLORES_PARTIDO = {
    "FUERZA POPULAR":                                              "#E8540A",
    "JUNTOS POR EL PERÚ":                                         "#C0392B",
    "RENOVACIÓN POPULAR":                                          "#2E86C1",
    "PARTIDO DEL BUEN GOBIERNO":                                   "#27AE60",
    "PARTIDO CÍVICO OBRAS":                                        "#8E6BBE",
    "AHORA NACIÓN - AN":                                           "#16A085",
    "ALIANZA PARA EL PROGRESO":                                    "#E67E22",
    "PARTIDO APRISTA PERUANO":                                     "#922B21",
    "PODEMOS PERÚ":                                                "#1ABC9C",
    "PARTIDO PAÍS PARA TODOS":                                     "#D4AC0D",
    "PRIMERO LA GENTE \u2013 COMUNIDAD, ECOLOG\u00cdA, LIBERTAD Y PROGRESO": "#6C3483",
    "PARTIDO SICREO":                                              "#117A65",
    "PARTIDO DEMÓCRATA UNIDO PERÚ":                                "#5D6D7E",
    "FRENTE POPULAR AGRÍCOLA FÍA DEL PERÚ":                        "#784212",
    "PARTIDO DEMOCRÁTICO SOMOS PERÚ":                              "#E74C3C",
    "PARTIDO FRENTE DE LA ESPERANZA 2021":                         "#1F618D",
    "PARTIDO POLÍTICO COOPERACIÓN POPULAR":                        "#148F77",
    "PARTIDO POLÍTICO PERÚ PRIMERO":                               "#B7950B",
    "ALIANZA ELECTORAL VENCEREMOS":                                "#76448A",
    "PROGRESEMOS":                                                 "#2E4057",
    # Fallback para partidos no listados
    "_DEFAULT":                                                    "#7A95A8",
}

# Nombres cortos para visualizaciones compactas (hemiciclo, leyendas)
SIGLAS_PARTIDO = {
    "FUERZA POPULAR":               "FP",
    "JUNTOS POR EL PERÚ":           "JPP",
    "RENOVACIÓN POPULAR":           "RP",
    "PARTIDO DEL BUEN GOBIERNO":    "PBG",
    "PARTIDO CÍVICO OBRAS":         "PCO",
    "AHORA NACIÓN - AN":            "AN",
    "ALIANZA PARA EL PROGRESO":     "APP",
    "PARTIDO APRISTA PERUANO":      "APRA",
    "PODEMOS PERÚ":                 "PP",
    "PARTIDO PAÍS PARA TODOS":      "PPT",
    "PARTIDO SICREO":               "SCR",
    "PARTIDO DEMÓCRATA UNIDO PERÚ": "PDUP",
    "PROGRESEMOS":                  "PRO",
}

# Códigos ONPE de filas especiales (no son partidos reales)
ONPE_CODIGOS_ESPECIALES = {80, 81, 82}  # blancos, nulos, impugnados
