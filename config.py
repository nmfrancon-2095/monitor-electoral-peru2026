# ============================================================
# config.py — Monitor Electoral Perú 2026
# Sistema de diseño v2.0 — "Rigor Editorial"
#
# Cambios respecto a v1.0:
#   - Paleta reconstruida en OKLCH (perceptualmente uniforme)
#   - Tipografía: Fraunces (display) + DM Sans (UI/cuerpo)
#   - Sistema de elevación 3 niveles (shadows, no solo bordes)
#   - Bloques temáticos con igual lightness → igual peso visual
#   - Barra de score 4px (más refinada que los 8px anteriores)
#   - Nuevas clases: .page-title, .score-bar-track, .elev-1/2
#
# Para cambiar cualquier aspecto visual, empieza aquí.
# Los cambios en este archivo se propagan a todas las páginas.
# ============================================================

# -------------------------------------------------------
# SECTION: Identidad del dashboard
# -------------------------------------------------------
APP_TITLE               = "Monitor Electoral Per\u00fa 2026"
APP_SUBTITLE            = "Integridad electoral y riesgos institucionales \u00b7 Per\u00fa 2026"
APP_ICON                = "\U0001f5f3\ufe0f"
APP_LOGO                = None
APP_CONFIDENTIAL_LABEL  = "CONFIDENCIAL \u2014 Uso interno"
APP_VERSION             = "v2.0"
DATA_FILE               = "data/maestro_dashboard_electoral_v1.xlsx"

# -------------------------------------------------------
# SECTION: Paleta de colores — v2.0
#
# Construida en OKLCH: oklch(lightness% chroma hue)
#   lightness: 0% negro → 100% blanco
#   chroma:    0 = gris puro, >0.20 = muy saturado
#   hue:       248 = azul, 25 = rojo, 55 = ámbar, 145 = verde
#
# Principio clave — tinte azul en todos los neutrales:
#   chroma 0.008-0.014 en hue 248 → nunca gris puro.
#   Crea cohesión subconsciente con la paleta institucional.
#
# Regla 60-30-10:
#   60% → fondos y superficies (BACKGROUND, SURFACE, BORDER)
#   30% → texto y elementos secundarios (TEXT_PRIMARY/SECONDARY)
#   10% → acento y acciones clave (PRIMARY, ACCENT)
# -------------------------------------------------------

# Primarios — UN Blue, recalibrado con más profundidad
COLOR_PRIMARY           = "#1A3F72"   # oklch(30% 0.13 248)
COLOR_ACCENT            = "#1E6FB5"   # oklch(50% 0.18 248)

# Superficies — tinte azul sutil (chroma 0.004-0.010)
COLOR_BACKGROUND        = "#EFF3F8"   # oklch(95% 0.010 248)
COLOR_SURFACE           = "#FAFCFF"   # oklch(99% 0.004 248) — no blanco puro
COLOR_SURFACE_ALT       = "#F4F7FB"   # oklch(97% 0.007 248)
COLOR_BORDER            = "#D4E2F0"   # oklch(88% 0.014 248)
COLOR_BORDER_STRONG     = "#B4CAE0"   # oklch(81% 0.020 248)

# Texto — tintado en azul, nunca gris puro
COLOR_TEXT_PRIMARY      = "#111E2D"   # oklch(16% 0.030 248)
COLOR_TEXT_SECONDARY    = "#3A5570"   # oklch(40% 0.040 248)
COLOR_TEXT_MUTED        = "#6B8BA0"   # oklch(58% 0.028 248)

# Riesgo — igual lightness oklch(~44%), hues distintos
# → mismo peso visual en leyendas y charts
COLOR_RIESGO_ALTO       = "#A82828"   # oklch(42% 0.20 25)   rojo
COLOR_RIESGO_ALTO_BG    = "#FBF0F0"   # oklch(96% 0.012 25)
COLOR_RIESGO_MEDIO      = "#B86000"   # oklch(50% 0.17 55)   ámbar
COLOR_RIESGO_MEDIO_BG   = "#FBF5EA"   # oklch(96% 0.014 55)
COLOR_RIESGO_BAJO       = "#1A7A40"   # oklch(44% 0.16 145)  verde
COLOR_RIESGO_BAJO_BG    = "#EAF6EF"   # oklch(96% 0.014 145)
COLOR_RIESGO_NONE       = "#5E7F96"   # oklch(56% 0.022 248)
COLOR_RIESGO_NONE_BG    = "#F2F6FA"   # oklch(96% 0.008 248)

# REINFO — naranja distinguible del ámbar de riesgo-medio
COLOR_REINFO            = "#A04A00"   # oklch(46% 0.19 42)
COLOR_REINFO_BG         = "#FAF1E8"   # oklch(96% 0.016 42)

# -------------------------------------------------------
# SECTION: Umbrales de score
# Score total máximo: 38 (19 leyes x 2 pts) + bonus_autoria
# -------------------------------------------------------
SCORE_ALTO_MIN  = 20
SCORE_MEDIO_MIN = 10

# -------------------------------------------------------
# SECTION: Etiquetas de UI
# Sin emojis en títulos de sección ni labels de filtro.
# Emojis solo en indicadores de estado en tablas.
# -------------------------------------------------------
LABEL_RIESGO = {
    "alto":  "Alto",
    "medio": "Medio",
    "bajo":  "Bajo",
    "none":  "Sin dato",
}

DOT_RIESGO = {
    "alto":  '<span style="color:#A82828; font-size:0.7em;">\u25cf</span>',
    "medio": '<span style="color:#B86000; font-size:0.7em;">\u25cf</span>',
    "bajo":  '<span style="color:#1A7A40; font-size:0.7em;">\u25cf</span>',
    "none":  '<span style="color:#5E7F96; font-size:0.7em;">\u25cf</span>',
}

LABEL_VOTO = {
    "A FAVOR":    "A favor",
    "EN CONTRA":  "En contra",
    "ABSTENCION": "Abstenci\u00f3n",
    "AUSENTE":    "Ausente",
    "LICENCIA":   "Licencia",
    "SIN DATO":   "Sin dato",
}

COLOR_VOTO = {
    "A FAVOR":    "#F9EAEA",
    "EN CONTRA":  "#E8F4EC",
    "ABSTENCION": "#FBF5EA",
    "AUSENTE":    "#F2F6FA",
    "LICENCIA":   "#F2F6FA",
    "SIN DATO":   "#F2F6FA",
}

COLOR_VOTO_TEXT = {
    "A FAVOR":    "#A82828",
    "EN CONTRA":  "#1A7A40",
    "ABSTENCION": "#B86000",
    "AUSENTE":    "#3A5570",
    "LICENCIA":   "#3A5570",
    "SIN DATO":   "#6B8BA0",
}

# -------------------------------------------------------
# SECTION: Bloques temáticos
#
# COLOR_BLOQUE: todos en oklch lightness 42-50%
# → igual peso visual en gráficos
# Hues separados ≥30° para distinguibilidad en daltonismo
# -------------------------------------------------------
BLOQUES = {
    "pro-crimen":     "Pro-crimen",
    "reinfo":         "REINFO",
    "ambiental":      "Ambiental",
    "espacio-civico": "Espacio c\u00edvico",
    "bicameralidad":  "Bicameralidad",
    "genero":         "G\u00e9nero",
}

BLOQUES_LARGO = {
    "pro-crimen":     "Pro-crimen \u2014 debilitan el sistema de justicia",
    "reinfo":         "REINFO \u2014 registro minero informal",
    "ambiental":      "Ambiental \u2014 protecci\u00f3n de bosques",
    "espacio-civico": "Espacio c\u00edvico \u2014 sociedad civil",
    "bicameralidad":  "Bicameralidad \u2014 reforma institucional",
    "genero":         "G\u00e9nero \u2014 igualdad y protecci\u00f3n frente a violencia",
}

COLOR_BLOQUE = {
    "pro-crimen":     "#A82828",   # oklch(42% 0.20 25)   rojo       hue  25
    "reinfo":         "#A04A00",   # oklch(46% 0.19 42)   naranja    hue  42
    "ambiental":      "#1A7A40",   # oklch(44% 0.16 145)  verde      hue 145
    "espacio-civico": "#5A3E96",   # oklch(40% 0.18 295)  violeta    hue 295
    "bicameralidad":  "#1E6FB5",   # oklch(50% 0.18 248)  azul       hue 248
    "genero":         "#A8185A",   # oklch(42% 0.20 358)  crimson    hue 358
}

# -------------------------------------------------------
# SECTION: Columnas de leyes
# -------------------------------------------------------
LEYES_COLS = [
    "L31751 Prescripci\u00f3n 1 a\u00f1o",
    "L31880 Prisi\u00f3n preventiva",
    "L31989 Elimina incautaci\u00f3n",
    "L31990 Limita colaboraci\u00f3n eficaz",
    "L32054 Exonera partidos",
    "L32104 Interpretaci\u00f3n autentica",
    "L32108 Redefine el t\u00e9rmino organizaci\u00f3n criminal",
    "L32130 Designa a la PNP para que realice las investigaciones preliminares",
    "L32181 Elimina detenci\u00f3n preliminar",
    "L32326 Restringe extinci\u00f3n de dominio",
    "L31388 REINFO 3a amp",
    "L32213 REINFO 4a amp",
    "L32537 REINFO 5a amp",
    "L31973 Ley Forestal",
    "L32301 Ley APCI",
    "L31988 Bicameralidad",
    "L32535 Igualdad de oportunidades",
    "L31498 Materiales educativos",
    "L32331 Indemnidad sexual NNA",
]

# Columnas de score por bloque (excluye bonus_autoria y score_total)
SCORE_COLS = [
    "score_procrimen",
    "score_reinfo",
    "score_ambiental",
    "score_espacio_civico",
    "score_bicameralidad",
    "score_genero",
]

# Máximos teóricos por bloque (A FAVOR = 2 pts por ley)
SCORE_MAX = {
    "score_procrimen":      20,   # 10 leyes x 2
    "score_reinfo":          6,   #  3 leyes x 2
    "score_ambiental":       2,   #  1 ley  x 2
    "score_espacio_civico":  2,   #  1 ley  x 2
    "score_bicameralidad":   2,   #  1 ley  x 2
    "score_genero":          6,   #  3 leyes x 2
    "score_total":          38,   # suma sin bonus_autoria
}

REGIONES_PRIORITARIAS = ["Ucayali", "Loreto", "Madre de Dios", "Puno"]

TIPOS_ELECCION = [
    "PRESIDENCIAL",
    "SENADORES DISTRITO \u00daNCO",
    "DIPUTADOS",
]

# -------------------------------------------------------
# SECTION: Configuración de gráficos Plotly
#
# paper_bgcolor = transparente → hereda fondo de la página
# plot_bgcolor  = COLOR_SURFACE_ALT → diferenciación sutil
# Usa CHART_LAYOUT_BASE con: fig.update_layout(**CHART_LAYOUT_BASE)
# -------------------------------------------------------
CHART_HEIGHT        = 420
CHART_HEIGHT_SMALL  = 280
CHART_HEIGHT_TALL   = 540

CHART_FONT = dict(
    family="'DM Sans', 'Instrument Sans', system-ui, sans-serif",
    size=12,
    color="#111E2D",
)

CHART_LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",   # transparente
    plot_bgcolor="#F4F7FB",          # COLOR_SURFACE_ALT
    font=CHART_FONT,
    margin=dict(l=8, r=8, t=20, b=8),
    legend=dict(
        orientation="h",
        y=-0.18,
        xanchor="left",
        x=0,
        font=dict(size=11),
        bgcolor="rgba(0,0,0,0)",
    ),
    xaxis=dict(
        showgrid=True,
        gridcolor="#D4E2F0",
        gridwidth=1,
        zeroline=False,
        tickfont=dict(size=11),
        linecolor="#D4E2F0",
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="#D4E2F0",
        gridwidth=1,
        zeroline=False,
        tickfont=dict(size=11),
        linecolor="#D4E2F0",
    ),
)

# -------------------------------------------------------
# SECTION: CSS global — v2.0 "Rigor Editorial"
#
# Tipografía:
#   Fraunces (variable, serif) — títulos/display
#     Autoritario, editorial, peso institucional
#     Usar en: page-title, section-header, score-number
#   DM Sans (variable, sans) — UI y cuerpo
#     Más carácter que Plus Jakarta Sans, legible en datos
#     Usar en: todo lo demás
#
# Sistema de elevación:
#   elev-0  sin sombra, solo border-bottom (tablas, listas)
#   elev-1  sombra sutil 0 1px 3px (cards KPI, filtros)
#   elev-2  sombra media 0 4px 12px (perfil, score activo)
#
# Diferencias vs v1.0:
#   + Fuentes: Fraunces + DM Sans en vez de Plus Jakarta Sans
#   + Todos los colores actualizados a tokens v2.0
#   + Cards con box-shadow en vez de solo border
#   + section-header usa Fraunces (serif)
#   + Badges: letter-spacing 0.04em (antes 0.06em)
#   + Barra de score: 4px (antes 8px)
#   + notas: border-left 2px (antes 3px), border-radius 6px
#   + Nuevas clases: .page-title, .page-title-light,
#                    .score-bar-track, .score-bar-fill,
#                    .elev-1, .elev-2
# -------------------------------------------------------
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;0,9..144,700;1,9..144,300&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&display=swap');

/* =====================================================
   BASE
   ===================================================== */
html, body, [class*="css"] {
    font-family: 'DM Sans', 'Instrument Sans', system-ui, -apple-system, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.stApp { background-color: #EFF3F8; }

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1200px;
}

/* =====================================================
   SIDEBAR
   ===================================================== */
section[data-testid="stSidebar"] {
    background-color: #1A3F72;
}
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div {
    color: rgba(255,255,255,0.90) !important;
}
section[data-testid="stSidebar"] a {
    color: rgba(255,255,255,0.72) !important;
    font-size: 0.875rem;
    font-weight: 400;
    text-decoration: none;
    transition: color 150ms ease;
}
section[data-testid="stSidebar"] a:hover {
    color: #FFFFFF !important;
}

/* =====================================================
   KPI METRICS
   ===================================================== */
div[data-testid="stMetric"] {
    background-color: #FAFCFF;
    border: 1px solid #D4E2F0;
    border-radius: 8px;
    padding: 16px 20px 14px 20px;
    box-shadow: 0 1px 3px rgba(17,30,45,0.06);
    transition: box-shadow 150ms ease;
}
div[data-testid="stMetric"]:hover {
    box-shadow: 0 3px 8px rgba(17,30,45,0.10);
}
div[data-testid="stMetricLabel"] {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #6B8BA0 !important;
}
div[data-testid="stMetricValue"] {
    font-size: 2.1rem !important;
    font-weight: 700 !important;
    color: #111E2D !important;
    font-variant-numeric: tabular-nums;
    line-height: 1.1 !important;
    letter-spacing: -0.02em !important;
}
div[data-testid="stMetricDelta"] {
    font-size: 0.76rem !important;
    color: #3A5570 !important;
}

/* =====================================================
   TABLAS
   ===================================================== */
[data-testid="stDataFrame"] th {
    background-color: #EFF3F8 !important;
    font-weight: 600 !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: #3A5570 !important;
}

/* =====================================================
   TABS
   ===================================================== */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    border-bottom: 2px solid #D4E2F0;
}
.stTabs [data-baseweb="tab"] {
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    color: #3A5570 !important;
    padding: 8px 18px !important;
    border-radius: 4px 4px 0 0 !important;
    border: none !important;
    background: transparent !important;
    transition: color 120ms ease, background 120ms ease;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #1A3F72 !important;
    background: #EFF3F8 !important;
}
.stTabs [aria-selected="true"] {
    color: #1A3F72 !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #1A3F72 !important;
}

/* =====================================================
   EXPANDERS
   ===================================================== */
details[data-testid="stExpander"] {
    border: 1px solid #D4E2F0 !important;
    border-radius: 8px !important;
    background: #FAFCFF !important;
    margin-bottom: 8px !important;
    box-shadow: 0 1px 3px rgba(17,30,45,0.05);
}
details[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    color: #111E2D !important;
    padding: 12px 16px !important;
}
details[data-testid="stExpander"] summary:hover {
    background: #F4F7FB !important;
    border-radius: 8px;
}

/* =====================================================
   INPUTS
   ===================================================== */
[data-testid="stTextInput"] input {
    border-color: #D4E2F0 !important;
    border-radius: 6px !important;
    font-size: 0.875rem !important;
    background: #FAFCFF !important;
    color: #111E2D !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #1E6FB5 !important;
    box-shadow: 0 0 0 3px rgba(30,111,181,0.12) !important;
}

/* =====================================================
   BOTONES DE DESCARGA
   ===================================================== */
.stDownloadButton > button {
    border-radius: 6px !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    border-color: #D4E2F0 !important;
    color: #3A5570 !important;
    transition: border-color 150ms ease, color 150ms ease;
}
.stDownloadButton > button:hover {
    border-color: #1E6FB5 !important;
    color: #1A3F72 !important;
}

hr {
    border: none !important;
    border-top: 1px solid #D4E2F0 !important;
    margin: 24px 0 !important;
}

/* =====================================================
   COMPONENTES REUTILIZABLES
   ===================================================== */

/* --- Badges de riesgo ---
   letter-spacing 0.04em vs 0.06em anterior — más editorial */
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 3px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    line-height: 1.7;
}
.badge-alto    { background: #A82828; color: #FFF; }
.badge-medio   { background: #B86000; color: #FFF; }
.badge-bajo    { background: #1A7A40; color: #FFF; }
.badge-reinfo  { background: #A04A00; color: #FFF; }
.badge-none    { background: #5E7F96; color: #FFF; }

/* Badge CONFIDENCIAL — sobre sidebar oscuro */
.badge-confidencial {
    display: inline-block;
    background: rgba(255,255,255,0.10);
    color: rgba(255,255,255,0.92);
    border: 1px solid rgba(255,255,255,0.20);
    padding: 3px 10px;
    border-radius: 3px;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.11em;
    text-transform: uppercase;
}

/* --- Notas informativas ---
   Border 2px (antes 3px), fondo tintado correctamente */
.nota-info {
    background: #EDF4FB;
    border-left: 2px solid #1E6FB5;
    border-radius: 0 6px 6px 0;
    padding: 10px 16px;
    font-size: 0.84rem;
    color: #3A5570;
    line-height: 1.6;
    margin: 8px 0;
}
.nota-warning {
    background: #FAF3E8;
    border-left: 2px solid #B86000;
    border-radius: 0 6px 6px 0;
    padding: 10px 16px;
    font-size: 0.84rem;
    color: #6B3800;
    line-height: 1.6;
    margin: 8px 0;
}

/* --- Encabezados de sección ---
   section-header: Fraunces serif — peso editorial
   section-subheader: DM Sans — claridad de datos */
.section-header {
    font-family: 'Fraunces', Georgia, serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #111E2D;
    margin: 0 0 2px 0;
    letter-spacing: -0.02em;
    line-height: 1.25;
}
.section-subheader {
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 0.80rem;
    color: #6B8BA0;
    margin: 0 0 20px 0;
    line-height: 1.5;
}

/* --- Títulos de página (para h1 custom inline) ---
   page-title: Fraunces 700 — títulos principales
   page-title-light: Fraunces 300 italic — subtítulos editoriales */
.page-title {
    font-family: 'Fraunces', Georgia, serif;
    font-weight: 700;
    letter-spacing: -0.025em;
    line-height: 1.15;
    color: #111E2D;
}
.page-title-light {
    font-family: 'Fraunces', Georgia, serif;
    font-weight: 300;
    font-style: italic;
    color: #6B8BA0;
}

/* --- Card de perfil --- */
.profile-card {
    background: #FAFCFF;
    border: 1px solid #D4E2F0;
    border-radius: 10px;
    padding: 20px 24px;
    box-shadow: 0 1px 4px rgba(17,30,45,0.07);
}
.profile-field {
    font-size: 0.85rem;
    line-height: 1.9;
    color: #3A5570;
}
.profile-field strong {
    color: #111E2D;
    font-weight: 600;
}

/* --- Score card ---
   Número usa Fraunces para peso editorial
   Barra de progreso 4px — más refinada que los 8px anteriores */
.score-card {
    background: #FAFCFF;
    border: 1px solid #D4E2F0;
    border-radius: 10px;
    padding: 20px 24px;
    box-shadow: 0 2px 8px rgba(17,30,45,0.08);
}
.score-number {
    font-family: 'Fraunces', Georgia, serif;
    font-size: 3.2rem;
    font-weight: 700;
    line-height: 1;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.03em;
}
.score-label {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: #6B8BA0;
    margin-bottom: 4px;
}
.score-bar-track {
    background: #D4E2F0;
    border-radius: 4px;
    height: 4px;
    overflow: hidden;
    margin: 6px 0 2px 0;
}
.score-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 400ms ease;
}

/* --- Sistema de elevación ---
   elev-1: cards estándar (KPIs, filtros, expanders)
   elev-2: cards destacadas (perfil activo, score card) */
.elev-1 {
    box-shadow: 0 1px 3px rgba(17,30,45,0.06), 0 1px 2px rgba(17,30,45,0.04);
}
.elev-2 {
    box-shadow: 0 4px 12px rgba(17,30,45,0.10), 0 1px 4px rgba(17,30,45,0.06);
}

/* --- Footer de página --- */
.page-footer {
    margin-top: 48px;
    padding-top: 14px;
    border-top: 1px solid #D4E2F0;
    display: flex;
    justify-content: space-between;
    font-size: 0.70rem;
    color: #6B8BA0;
    letter-spacing: 0.01em;
}

/* --- Números tabulares --- */
.tabular { font-variant-numeric: tabular-nums; }

</style>
"""
