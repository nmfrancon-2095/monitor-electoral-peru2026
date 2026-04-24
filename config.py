# ============================================================
# config.py — Monitor Electoral Perú 2026
# Sistema de diseño v3.0 — "Forensic Editorial"
#
# Cambios respecto a v2.0:
#   - Paleta: papel cálido + navy profundo + oro archivo
#       (antes: azul institucional frío sobre blanco tintado)
#   - Tipografía: Source Serif 4 (display) + DM Sans (UI/body)
#       (antes: Fraunces + DM Sans)
#   - Riesgo con luminosidad más baja, tonos más documentales
#   - Partidos políticos: paleta EXPANDIDA — 14 hues distintos
#       con separación ≥25° en OKLCH para máxima diferenciación
#   - Bordes rectos (radius 0-2px) en vez de 6-10px
#   - Cards con regla superior navy en vez de sombra
#   - Nuevas clases: .masthead, .hero-card, .kpi-grid,
#                    .forensic-table, .score-row
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
APP_VERSION             = "v3.0"
DATA_FILE               = "data/maestro_dashboard_electoral_v1.xlsx"

# -------------------------------------------------------
# SECTION: Paleta de colores — v3.0 "Forensic Editorial"
#
# OKLCH: oklch(lightness% chroma hue)
#
# Principio: papel cálido (hue 88, no azul frío) da sensación
# de documento de archivo. Navy profundo y oro archivo crean
# la jerarquía institucional. Los riesgos bajan de lightness
# 42-50% a 36-44% — más gravedad documental.
#
# Regla 60-30-10:
#   60% → paper, surface, border
#   30% → ink + ink-2 (texto)
#   10% → primary navy + archive gold (acentos y reglas)
# -------------------------------------------------------

# Primarios — Deep Navy + Archive Gold
COLOR_PRIMARY           = "#0B2545"   # oklch(22% 0.10 260)   navy profundo
COLOR_ACCENT            = "#13315C"   # oklch(30% 0.12 258)   navy medio
COLOR_GOLD              = "#C9A227"   # oklch(71% 0.14 85)    oro archivo — para reglas/índices
COLOR_GOLD_SOFT         = "#E6D089"   # oklch(86% 0.10 88)    oro suave

# Superficies — papel cálido (hue 88), no blanco clínico
COLOR_BACKGROUND        = "#F2F1EC"   # oklch(95% 0.007 88)   paper
COLOR_SURFACE           = "#FFFFFF"   # blanco puro sobre paper
COLOR_SURFACE_ALT       = "#F7F5F0"   # oklch(97% 0.008 85)   surface alt
COLOR_PAPER_ALT         = "#E8E6DE"   # paper más saturado
COLOR_BORDER            = "#DAD6CC"   # oklch(86% 0.012 85)
COLOR_BORDER_SOFT       = "#E5E1D6"
COLOR_BORDER_STRONG     = "#B8B2A3"   # oklch(72% 0.015 85)

# Texto — ink azulado, ink-2 más cálido
COLOR_TEXT_PRIMARY      = "#0E1B26"   # oklch(18% 0.020 248)  ink
COLOR_TEXT_SECONDARY    = "#45556A"   # oklch(42% 0.035 248)  ink-2
COLOR_TEXT_MUTED        = "#7A7366"   # oklch(52% 0.018 80)   muted warm

# Riesgo — deeper forensic tones (lightness 36-44%)
COLOR_RIESGO_ALTO       = "#8E1B1B"   # oklch(36% 0.17 25)    rojo profundo
COLOR_RIESGO_ALTO_BG    = "#FBF1F1"   # oklch(96% 0.012 25)
COLOR_RIESGO_MEDIO      = "#9E5200"   # oklch(44% 0.14 55)    ámbar profundo
COLOR_RIESGO_MEDIO_BG   = "#FBF4E8"   # oklch(96% 0.014 55)
COLOR_RIESGO_BAJO       = "#1B5E3A"   # oklch(37% 0.12 150)   verde profundo
COLOR_RIESGO_BAJO_BG    = "#EDF5EF"   # oklch(96% 0.012 145)
COLOR_RIESGO_NONE       = "#4B5A6B"   # oklch(42% 0.020 248)  gris neutro
COLOR_RIESGO_NONE_BG    = "#EEEFEC"   # oklch(95% 0.004 88)

# REINFO — ocre profundo, distinto del ámbar de riesgo-medio
COLOR_REINFO            = "#8A3D00"   # oklch(37% 0.12 42)
COLOR_REINFO_BG         = "#FAF0E4"   # oklch(96% 0.016 42)

# -------------------------------------------------------
# SECTION: Colores de niveles de abordaje (Segunda Vuelta)
# Semáforo: ABORDA = verde, PARCIAL = navy, TANGENCIAL = ámbar, AUSENTE = gris
# Mismos hues que COLOR_RIESGO / COLOR_BLOQUE — coherencia de paleta
# -------------------------------------------------------
COLOR_ABORDAJE = {
    "ABORDA":     "#1B5E3A",   # verde profundo
    "PARCIAL":    "#13315C",   # navy medio
    "TANGENCIAL": "#9E5200",   # ámbar profundo
    "AUSENTE":    "#4B5A6B",   # gris neutro
}

COLOR_ABORDAJE_BG = {
    "ABORDA":     "#EDF5EF",
    "PARCIAL":    "#EAEEF5",
    "TANGENCIAL": "#FBF4E8",
    "AUSENTE":    "#EEEFEC",
}

LABEL_ABORDAJE = {
    "ABORDA":     "Aborda",
    "PARCIAL":    "Parcial",
    "TANGENCIAL": "Tangencial",
    "AUSENTE":    "Ausente",
}

# -------------------------------------------------------
# SECTION: Umbrales de score
# Score total máximo: 38 (19 leyes x 2 pts) + bonus_autoria
# -------------------------------------------------------
SCORE_ALTO_MIN  = 20
SCORE_MEDIO_MIN = 10

# -------------------------------------------------------
# SECTION: Etiquetas de UI
# -------------------------------------------------------
LABEL_RIESGO = {
    "alto":  "Alto",
    "medio": "Medio",
    "bajo":  "Bajo",
    "none":  "Sin dato",
}

DOT_RIESGO = {
    "alto":  '<span style="color:#8E1B1B; font-size:0.7em;">\u25a0</span>',
    "medio": '<span style="color:#9E5200; font-size:0.7em;">\u25a0</span>',
    "bajo":  '<span style="color:#1B5E3A; font-size:0.7em;">\u25a0</span>',
    "none":  '<span style="color:#4B5A6B; font-size:0.7em;">\u25a0</span>',
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
    "A FAVOR":    "#FBF1F1",
    "EN CONTRA":  "#EDF5EF",
    "ABSTENCION": "#FBF4E8",
    "AUSENTE":    "#EEEFEC",
    "LICENCIA":   "#EEEFEC",
    "SIN DATO":   "#F7F5F0",
}

COLOR_VOTO_TEXT = {
    "A FAVOR":    "#8E1B1B",
    "EN CONTRA":  "#1B5E3A",
    "ABSTENCION": "#9E5200",
    "AUSENTE":    "#45556A",
    "LICENCIA":   "#45556A",
    "SIN DATO":   "#7A7366",
}

# -------------------------------------------------------
# SECTION: Bloques temáticos — Forensic palette
#
# Lightness 36-42% para igual peso visual
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
    "pro-crimen":     "#8E1B1B",   # oklch(36% 0.17 25)    rojo profundo
    "reinfo":         "#8A3D00",   # oklch(37% 0.12 42)    ocre
    "ambiental":      "#1B5E3A",   # oklch(37% 0.12 145)   verde profundo
    "espacio-civico": "#4A2E7A",   # oklch(32% 0.15 295)   violeta profundo
    "bicameralidad":  "#13315C",   # oklch(30% 0.12 258)   navy
    "genero":         "#8C1247",   # oklch(36% 0.17 358)   burgundy
}

# -------------------------------------------------------
# SECTION: Paleta de PARTIDOS POLÍTICOS — v3.0
#
# Paleta EXPANDIDA con 14 hues distintos, separación ≥22°
# en el círculo OKLCH. Los colores buscan evocar la identidad
# del partido cuando es reconocible, pero priorizan la
# DIFERENCIACIÓN visual en gráficos sobre la literalidad.
#
# Todos los colores tienen lightness 40-54% → igual peso
# visual. Diseñados para ser distinguibles también en
# blanco y negro y en daltonismo (deuteranopia).
#
# Cuando un partido no está en la lista, usar COLOR_PARTIDO_DEFAULT.
# -------------------------------------------------------
COLOR_PARTIDO = {
    # Derecha / centro-derecha
    "FUERZA POPULAR":                      "#D84315",   # naranja-rojo vibrante (fujimorismo)
    "RENOVACION POPULAR":                  "#00695C",   # teal profundo
    "AVANZA PAIS - PARTIDO DE INTEGRACION SOCIAL": "#5D4037",  # sepia
    "AVANZA PAIS":                         "#5D4037",
    "ALIANZA PARA EL PROGRESO":            "#1565C0",   # azul APP
    "UNIDAD NACIONAL":                     "#1565C0",   # alias
    "PARTIDO DEMOCRATICO SOMOS PERU":      "#EF6C00",   # naranja Somos Perú
    "SOMOS PERU":                          "#EF6C00",
    "PARTIDO POPULAR CRISTIANO - PPC":     "#388E3C",   # verde PPC
    "PARTIDO MORADO":                      "#7B1FA2",   # morado
    "PARTIDO APRISTA PERUANO":             "#C62828",   # rojo APRA

    # Izquierda / progresistas
    "JUNTOS POR EL PERU":                  "#AD1457",   # magenta profundo
    "PERU LIBRE":                          "#B71C1C",   # rojo Perú Libre
    "PARTIDO POLITICO NACIONAL PERU LIBRE": "#B71C1C",
    "NUEVO PERU":                          "#6A1B9A",   # violeta

    # Centro / emergentes
    "PODEMOS PERU":                        "#F9A825",   # amarillo-dorado
    "ACCION POPULAR":                      "#E65100",   # naranja AP
    "PARTIDO CIVICO OBRAS":                "#4E342E",   # marrón oscuro
    "FE EN EL PERU":                       "#00838F",   # cyan profundo
    "UN CAMINO DIFERENTE":                 "#2E7D32",   # verde bosque
    "PARTIDO POLITICO PERU PRIMERO":       "#283593",   # indigo
    "PARTIDO DEL BUEN GOBIERNO":           "#00897B",   # teal
    "PARTIDO SICREO":                      "#795548",   # café
    "JUNTOS POR EL PERU - AGRUPACION POLITICA": "#AD1457",

    # Frentes y alianzas
    "FRENTE POPULAR AGRICOLA FIA DEL PERU": "#558B2F",   # verde oliva
    "ALIANZA ELECTORAL VERDADERA DEMOCRACIA": "#00579B",  # azul oscuro

    # Default para partidos no listados
}
COLOR_PARTIDO_DEFAULT = "#607D8B"   # blue-grey neutro

# Grupos parlamentarios (bancadas actuales) — mismos tonos
# cuando aplica, pero con pequeñas variaciones para evitar
# colisión cuando partido y bancada son distintos
COLOR_BANCADA = {
    "FUERZA POPULAR":           "#D84315",
    "ALIANZA PARA EL PROGRESO": "#1565C0",
    "RENOVACIÓN POPULAR":       "#00695C",
    "AVANZA PAÍS":              "#5D4037",
    "SOMOS PERÚ":               "#EF6C00",
    "PODEMOS PERÚ":             "#F9A825",
    "PERÚ LIBRE":               "#B71C1C",
    "JUNTOS POR EL PERÚ":       "#AD1457",
    "ACCIÓN POPULAR":           "#E65100",
    "HONOR Y DEMOCRACIA":       "#4527A0",   # violeta oscuro
    "BLOQUE DEMOCRÁTICO POPULAR": "#37474F",  # gris-azulado
    "BANCADA SOCIALISTA":       "#6A1B9A",   # violeta
    "CAMBIO DEMOCRÁTICO":       "#00838F",
    "NO AGRUPADO":              "#78909C",   # blue-grey claro
}

# Escala ordenada para asignación automática si hay más
# partidos que colores definidos
PALETTE_PARTIDOS_EXTRA = [
    "#D84315",  # naranja-rojo
    "#1565C0",  # azul
    "#00695C",  # teal profundo
    "#EF6C00",  # naranja
    "#7B1FA2",  # morado
    "#388E3C",  # verde
    "#C62828",  # rojo
    "#AD1457",  # magenta
    "#F9A825",  # amarillo-dorado
    "#283593",  # indigo
    "#5D4037",  # sepia
    "#00838F",  # cyan
    "#558B2F",  # oliva
    "#6A1B9A",  # violeta
    "#4527A0",  # violeta oscuro
    "#795548",  # café
    "#00897B",  # teal medio
    "#E65100",  # naranja oscuro
    "#37474F",  # gris-azulado
    "#2E7D32",  # verde bosque
]


def color_partido(nombre: str) -> str:
    """Devuelve el color del partido, con fallback consistente.

    Si el partido no está en COLOR_PARTIDO, hashea su nombre
    contra PALETTE_PARTIDOS_EXTRA para asignar un color estable.
    """
    if not nombre:
        return COLOR_PARTIDO_DEFAULT
    key = str(nombre).strip().upper()
    if key in COLOR_PARTIDO:
        return COLOR_PARTIDO[key]
    # hash estable → mismo partido siempre mismo color extra
    idx = sum(ord(c) for c in key) % len(PALETTE_PARTIDOS_EXTRA)
    return PALETTE_PARTIDOS_EXTRA[idx]


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

SCORE_COLS = [
    "score_procrimen",
    "score_reinfo",
    "score_ambiental",
    "score_espacio_civico",
    "score_bicameralidad",
    "score_genero",
]

SCORE_MAX = {
    "score_procrimen":      20,   # 10 leyes x 2
    "score_reinfo":          6,   #  3 leyes x 2
    "score_ambiental":       2,   #  1 ley  x 2
    "score_espacio_civico":  2,   #  1 ley  x 2
    "score_bicameralidad":   2,   #  1 ley  x 2
    "score_genero":          6,   #  3 leyes x 2
    "score_total":          38,
}

REGIONES_PRIORITARIAS = ["Ucayali", "Loreto", "Madre de Dios", "Puno"]

TIPOS_ELECCION = [
    "PRESIDENCIAL",
    "SENADORES DISTRITO \u00daNICO",
    "SENADORES DISTRITO M\u00daLTIPLE",
    "DIPUTADOS",
]

# -------------------------------------------------------
# SECTION: Configuración de gráficos Plotly — v3.0
#
# paper_bgcolor: transparente → hereda paper cálido de la página
# plot_bgcolor: blanco puro → máximo contraste para datos
# Usa CHART_LAYOUT_BASE con: fig.update_layout(**CHART_LAYOUT_BASE)
#
# Para barras con extremos redondeados (estilo Economist):
#   fig.update_traces(marker_line_width=0, cornerradius=6)
#   (cornerradius requiere Plotly ≥5.18)
# -------------------------------------------------------
CHART_HEIGHT        = 420
CHART_HEIGHT_SMALL  = 280
CHART_HEIGHT_TALL   = 540

CHART_FONT = dict(
    family="'DM Sans', system-ui, sans-serif",
    size=12,
    color="#0E1B26",
)

CHART_FONT_TITLE = dict(
    family="'Source Serif 4', Georgia, serif",
    size=15,
    color="#0E1B26",
)

CHART_LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",       # transparente
    plot_bgcolor="#FFFFFF",              # blanco puro
    font=CHART_FONT,
    margin=dict(l=8, r=8, t=28, b=8),
    legend=dict(
        orientation="h",
        y=-0.18,
        xanchor="left",
        x=0,
        font=dict(family="'DM Sans', sans-serif", size=10.5, color="#45556A"),
        bgcolor="rgba(0,0,0,0)",
    ),
    xaxis=dict(
        showgrid=True,
        gridcolor="#E5E1D6",
        gridwidth=0.5,
        zeroline=False,
        tickfont=dict(family="'DM Sans', sans-serif", size=10.5, color="#7A7366"),
        linecolor="#DAD6CC",
        title_font=dict(family="'DM Sans', sans-serif", size=11, color="#45556A"),
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="#E5E1D6",
        gridwidth=0.5,
        zeroline=False,
        tickfont=dict(family="'DM Sans', sans-serif", size=10.5, color="#7A7366"),
        linecolor="#DAD6CC",
        title_font=dict(family="'DM Sans', sans-serif", size=11, color="#45556A"),
    ),
)

# Barras con extremos redondeados (Plotly ≥5.18)
BAR_CORNER_RADIUS = 6

# -------------------------------------------------------
# SECTION: CSS global — v3.0 "Forensic Editorial"
#
# Tipografía:
#   Source Serif 4 (display) — Autoritario, editorial, UN-report feel
#     Usar en: page-title, section-header, score-number, KPI values
#   DM Sans (UI/body)
#     Usar en: todo lo demás. NO hay fuente monoespaciada.
#
# Elevación: preferir REGLAS (border-top 3px navy) sobre sombras.
# La regla comunica jerarquía institucional sin sugerir "tarjeta táctil".
# -------------------------------------------------------
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;0,8..60,500;0,8..60,600;0,8..60,700;1,8..60,400;1,8..60,600&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&display=swap');

/* =====================================================
   BASE
   ===================================================== */
:root, html, body, * {
    font-family: 'DM Sans', system-ui, -apple-system, sans-serif !important;
}

/* Excepción: elementos editoriales usan Source Serif 4 */
.section-header,
.score-number,
.page-title,
.page-title-light,
.kpi-val,
.hero-title,
.hero-stat,
.profile-name,
.chart-title {
    font-family: 'Source Serif 4', Georgia, 'Times New Roman', serif !important;
}

.stApp { background-color: #F2F1EC; }

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1280px;
}

/* =====================================================
   SIDEBAR — navy profundo, oro para hover
   ===================================================== */
section[data-testid="stSidebar"] {
    background-color: #0B2545;
    border-right: 1px solid #13315C;
}
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div {
    color: rgba(255,255,255,0.88) !important;
}
section[data-testid="stSidebar"] a {
    color: rgba(255,255,255,0.72) !important;
    font-size: 0.875rem;
    font-weight: 400;
    text-decoration: none;
    transition: color 150ms ease, border-color 150ms ease;
    border-left: 2px solid transparent;
    padding-left: 10px;
    margin-left: -10px;
}
section[data-testid="stSidebar"] a:hover {
    color: #FFFFFF !important;
    border-left-color: #C9A227;
}

/* =====================================================
   MASTHEAD (top rule + title bar)
   ===================================================== */
.masthead {
    border-top: 3px solid #0B2545;
    border-bottom: 1px solid #DAD6CC;
    padding: 16px 0 14px;
    margin-bottom: 36px;
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 40px;
    flex-wrap: wrap;
}
.masthead-title {
    font-family: 'Source Serif 4', Georgia, serif !important;
    font-weight: 600;
    font-size: 22px;
    letter-spacing: -0.015em;
    line-height: 1.1;
    color: #0E1B26;
}
.masthead-title em { font-style: italic; font-weight: 400; color: #45556A; }
.masthead-meta {
    font-size: 10px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #7A7366;
    font-weight: 700;
    display: flex;
    gap: 12px;
    align-items: center;
}
.masthead-meta .pill {
    padding: 4px 9px;
    border: 1px solid #B8B2A3;
    border-radius: 1px;
    color: #45556A;
}
.masthead-meta .pill.red {
    color: #8E1B1B;
    border-color: #8E1B1B;
}

/* =====================================================
   KPI METRICS — Streamlit st.metric restyled
   ===================================================== */
div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #DAD6CC;
    border-top: 3px solid #0B2545;
    border-radius: 0 !important;
    padding: 22px 22px 18px 22px;
}
div[data-testid="stMetric"]:hover {
    border-top-color: #C9A227;
}
div[data-testid="stMetricLabel"] {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    color: #7A7366 !important;
    margin-bottom: 8px !important;
}
div[data-testid="stMetricValue"] {
    font-family: 'Source Serif 4', Georgia, serif !important;
    font-size: 2.6rem !important;
    font-weight: 600 !important;
    color: #0E1B26 !important;
    font-variant-numeric: tabular-nums;
    line-height: 0.95 !important;
    letter-spacing: -0.025em !important;
}
div[data-testid="stMetricDelta"] {
    font-size: 0.76rem !important;
    color: #45556A !important;
    margin-top: 8px !important;
}

/* =====================================================
   TABLAS — cabeceras small-caps sobre surface alt
   ===================================================== */
[data-testid="stDataFrame"] {
    border: 1px solid #DAD6CC !important;
    border-radius: 0 !important;
}
[data-testid="stDataFrame"] th {
    background-color: #F7F5F0 !important;
    font-weight: 700 !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #7A7366 !important;
    border-bottom: 1px solid #DAD6CC !important;
}
[data-testid="stDataFrame"] td {
    color: #0E1B26 !important;
    font-size: 0.82rem !important;
}

/* =====================================================
   TABS — linea navy bajo tab activa
   ===================================================== */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    border-bottom: 1px solid #DAD6CC;
}
.stTabs [data-baseweb="tab"] {
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: #45556A !important;
    padding: 10px 18px !important;
    border-radius: 0 !important;
    border: none !important;
    background: transparent !important;
    transition: color 120ms ease;
    letter-spacing: 0.02em;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #0B2545 !important;
    background: #F7F5F0 !important;
}
.stTabs [aria-selected="true"] {
    color: #0B2545 !important;
    font-weight: 700 !important;
    border-bottom: 2px solid #0B2545 !important;
}

/* =====================================================
   EXPANDERS
   ===================================================== */
details[data-testid="stExpander"] {
    border: 1px solid #DAD6CC !important;
    border-radius: 0 !important;
    background: #FFFFFF !important;
    margin-bottom: 8px !important;
    box-shadow: none !important;
}
details[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    color: #0E1B26 !important;
    padding: 12px 16px !important;
}
details[data-testid="stExpander"] summary:hover {
    background: #F7F5F0 !important;
}

/* =====================================================
   INPUTS
   ===================================================== */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    border-color: #DAD6CC !important;
    border-radius: 0 !important;
    font-size: 0.875rem !important;
    background: #FFFFFF !important;
    color: #0E1B26 !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #0B2545 !important;
    box-shadow: 0 0 0 2px rgba(11,37,69,0.12) !important;
}

/* =====================================================
   BOTONES
   ===================================================== */
.stDownloadButton > button,
.stButton > button {
    border-radius: 0 !important;
    font-weight: 600 !important;
    font-size: 0.80rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border: 1px solid #DAD6CC !important;
    color: #45556A !important;
    background: #FFFFFF !important;
    transition: border-color 150ms ease, color 150ms ease, background 150ms ease;
}
.stDownloadButton > button:hover,
.stButton > button:hover {
    border-color: #0B2545 !important;
    color: #0B2545 !important;
    background: #F7F5F0 !important;
}

hr {
    border: none !important;
    border-top: 1px solid #DAD6CC !important;
    margin: 28px 0 !important;
}

/* =====================================================
   COMPONENTES REUTILIZABLES
   ===================================================== */

/* --- Badges de riesgo --- */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 9px 3px 8px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.66rem;
    font-weight: 700;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    line-height: 1.6;
    border: 1px solid transparent;
    border-radius: 0;
}
.badge::before {
    content: '';
    width: 5px;
    height: 5px;
    background: currentColor;
    display: inline-block;
}
.badge-alto    { background: #FBF1F1; color: #8E1B1B; border-color: #E7C9C9; }
.badge-medio   { background: #FBF4E8; color: #9E5200; border-color: #E6D4B2; }
.badge-bajo    { background: #EDF5EF; color: #1B5E3A; border-color: #C9DDCE; }
.badge-reinfo  { background: #FAF0E4; color: #8A3D00; border-color: #E3CAA8; }
.badge-none    { background: #EEEFEC; color: #4B5A6B; border-color: #D3D5CF; }

/* Versión sólida para casos críticos */
.badge-solid-alto { background: #8E1B1B; color: #FFF; border-color: #8E1B1B; }
.badge-solid-alto::before { background: #FFF; }

/* Badges de abordaje */
.badge-aborda     { background: #EDF5EF; color: #1B5E3A; border-color: #C9DDCE; }
.badge-parcial    { background: #EAEEF5; color: #13315C; border-color: #C5CEDC; }
.badge-tangencial { background: #FBF4E8; color: #9E5200; border-color: #E6D4B2; }
.badge-ausente    { background: #EEEFEC; color: #4B5A6B; border-color: #D3D5CF; }

/* Badge CONFIDENCIAL — sobre sidebar oscuro */
.badge-confidencial {
    display: inline-block;
    background: rgba(201,162,39,0.12);
    color: #C9A227;
    border: 1px solid rgba(201,162,39,0.4);
    padding: 3px 10px;
    border-radius: 0;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

/* Card comparativa segunda vuelta */
.sv-card {
    background: #FFFFFF;
    border: 1px solid #DAD6CC;
    border-top: 2px solid #0B2545;
    border-radius: 0;
    padding: 18px 20px;
    height: 100%;
}
.sv-card-name {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #7A7366;
    margin-bottom: 6px;
}
.sv-card-text {
    font-size: 0.84rem;
    color: #45556A;
    line-height: 1.65;
}

/* --- Notas (regla izquierda coloreada + glyph en header) --- */
.nota-info, .nota-warning, .nota-danger {
    border: 1px solid #DAD6CC;
    border-left: 4px solid #13315C;
    background: #FFFFFF;
    border-radius: 0;
    padding: 14px 20px;
    font-size: 0.84rem;
    color: #45556A;
    line-height: 1.6;
    margin: 10px 0;
}
.nota-warning  { border-left-color: #9E5200; }
.nota-danger   { border-left-color: #8E1B1B; }
.nota-info .nota-hd,
.nota-warning .nota-hd,
.nota-danger .nota-hd {
    display: block;
    font-weight: 700;
    color: #0E1B26;
    font-size: 0.70rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 6px;
}

/* --- Section header --- */
.section-header {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.4rem;
    font-weight: 500;
    color: #0E1B26;
    margin: 0 0 2px 0;
    letter-spacing: -0.015em;
    line-height: 1.2;
}
.section-subheader {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.80rem;
    color: #7A7366;
    margin: 0 0 22px 0;
    line-height: 1.5;
}

/* --- Page title con regla navy superior --- */
.page-title-wrap {
    border-top: 3px solid #0B2545;
    padding-top: 14px;
    margin-bottom: 24px;
}
.page-title {
    font-family: 'Source Serif 4', Georgia, serif;
    font-weight: 500;
    font-size: 2.5rem;
    letter-spacing: -0.025em;
    line-height: 1.08;
    color: #0E1B26;
    margin: 0;
}
.page-title-light {
    font-family: 'Source Serif 4', Georgia, serif;
    font-weight: 400;
    font-style: italic;
    color: #45556A;
}
.page-eyebrow {
    font-size: 10.5px;
    letter-spacing: 0.20em;
    text-transform: uppercase;
    color: #C9A227;
    font-weight: 700;
    margin-bottom: 10px;
}

/* --- Profile card (broadsheet) --- */
.profile-card {
    background: #FFFFFF;
    border: 1px solid #DAD6CC;
    border-top: 2px solid #0B2545;
    border-radius: 0;
    padding: 24px 28px;
}
.profile-name {
    font-family: 'Source Serif 4', Georgia, serif;
    font-weight: 500;
    font-size: 1.75rem;
    letter-spacing: -0.015em;
    line-height: 1.1;
    color: #0E1B26;
    margin: 0 0 6px;
}
.profile-meta {
    font-size: 12.5px;
    color: #45556A;
    margin-bottom: 18px;
}
.profile-field {
    font-size: 0.85rem;
    line-height: 1.8;
    color: #45556A;
}
.profile-field strong {
    color: #0E1B26;
    font-weight: 600;
}

/* --- Score card --- */
.score-card {
    background: #FFFFFF;
    border: 1px solid #DAD6CC;
    border-top: 2px solid #0B2545;
    border-radius: 0;
    padding: 24px 28px;
}
.score-number {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 4rem;
    font-weight: 600;
    line-height: 0.9;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.035em;
}
.score-label {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #7A7366;
    margin-bottom: 8px;
}
.score-bar-track {
    background: #DAD6CC;
    border-radius: 1.5px;
    height: 3px;
    overflow: hidden;
    margin: 4px 0 2px 0;
}
.score-bar-fill {
    height: 100%;
    border-radius: 1.5px;
    transition: width 400ms ease;
}

/* --- Sistema de elevación (legado) ---
   v3.0 prefiere reglas superiores a sombras, pero estas clases
   siguen disponibles para compatibilidad. */
.elev-1 {
    border-top: 2px solid #0B2545 !important;
    border-radius: 0 !important;
}
.elev-2 {
    border-top: 3px solid #0B2545 !important;
    border-radius: 0 !important;
}

/* --- Footer --- */
.page-footer {
    margin-top: 56px;
    padding-top: 16px;
    border-top: 1px solid #DAD6CC;
    display: flex;
    justify-content: space-between;
    font-size: 0.68rem;
    color: #7A7366;
    letter-spacing: 0.06em;
}
.page-footer span.label {
    font-weight: 700;
    color: #45556A;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

/* --- Tabulares --- */
.tabular { font-variant-numeric: tabular-nums; }

</style>
"""
