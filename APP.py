# ============================================================
# APP.py — Monitor Electoral Perú 2026
# Punto de entrada: autenticación, CSS global, sidebar, home.
# Cómo correr: python -m streamlit run APP.py
#
# Rediseño v3.0 "Forensic Editorial":
#   - Login: border-radius:0, Source Serif 4, eyebrow gold
#   - Sidebar: dos bloques separados con etiquetas de módulo
#   - Segunda contraseña inline en sidebar (violencia_auth)
#   - Home: dos secciones de cards v3, numeración continua
#   - HTML siempre por concatenación (+), sin f-strings multilínea
# ============================================================

import streamlit as st
import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import (
    APP_TITLE, APP_SUBTITLE, APP_ICON, APP_LOGO,
    APP_CONFIDENTIAL_LABEL, APP_VERSION,
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_GOLD,
    COLOR_SURFACE, COLOR_SURFACE_ALT, COLOR_BACKGROUND,
    COLOR_BORDER, COLOR_BORDER_SOFT,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_RIESGO_ALTO, COLOR_RIESGO_ALTO_BG,
    GLOBAL_CSS,
)

FONT_SERIF = "'Source Serif 4', Georgia, 'Times New Roman', serif"
FONT_SANS  = "'DM Sans', system-ui, -apple-system, sans-serif"

# ── Page config — debe ser la primera llamada Streamlit ───────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# SECCIÓN: Autenticación principal
# Contraseña en .streamlit/secrets.toml → [auth] password = "..."
# ════════════════════════════════════════════════════════════════════════════════
def check_password() -> bool:
    if st.session_state.get("autenticado", False):
        return True

    # Pantalla de login v3
    st.markdown(
        '<div style="max-width:420px;margin:80px auto 0 auto;">'
        # Masthead mínimo
        '<div style="text-align:center;margin-bottom:32px;">'
        '<div style="font-size:0.60rem;font-weight:700;letter-spacing:0.20em;'
        'text-transform:uppercase;color:' + COLOR_GOLD + ';margin-bottom:10px;">'
        'OACNUDH Per\u00fa \u00b7 Uso interno</div>'
        '<div style="font-family:' + FONT_SERIF + ';font-size:2rem;font-weight:500;'
        'color:' + COLOR_TEXT_PRIMARY + ';letter-spacing:-0.025em;line-height:1.15;'
        'margin-bottom:6px;">'
        'Monitor Electoral<br>Per\u00fa 2026</div>'
        '<div style="font-size:0.82rem;color:' + COLOR_TEXT_SECONDARY + ';'
        'line-height:1.5;max-width:300px;margin:0 auto;">'
        + APP_SUBTITLE +
        '</div>'
        '</div>'
        # Card de login
        '<div style="background:' + COLOR_SURFACE + ';border:1px solid ' + COLOR_BORDER + ';'
        'border-top:3px solid ' + COLOR_PRIMARY + ';border-radius:0;'
        'padding:32px 36px;">'
        '<div style="font-size:0.60rem;font-weight:700;letter-spacing:0.16em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:20px;">'
        'Acceso restringido</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        # El input y botón van dentro de la card via columns
        # (Streamlit no permite widgets dentro de HTML, usamos columnas para centrar)
        password_input = st.text_input(
            "Contrase\u00f1a",
            type="password",
            label_visibility="collapsed",
            placeholder="Contrase\u00f1a de acceso",
            key="login_password",
        )
        if st.button("Ingresar", use_container_width=True, type="primary", key="login_btn"):
            try:
                if password_input == st.secrets["auth"]["password"]:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Contrase\u00f1a incorrecta.")
            except KeyError:
                st.warning(
                    "\u2699\ufe0f Configura `[auth] password` en `.streamlit/secrets.toml`."
                )

        st.markdown(
            '<div style="margin-top:20px;text-align:center;'
            'font-size:0.70rem;color:' + COLOR_TEXT_MUTED + ';">'
            + APP_CONFIDENTIAL_LABEL + ' \u00b7 ' + APP_VERSION +
            '</div>',
            unsafe_allow_html=True,
        )

    return False


if not check_password():
    st.stop()


# ════════════════════════════════════════════════════════════════════════════════
# SECCIÓN: Sidebar — dos módulos con separación visual
# ════════════════════════════════════════════════════════════════════════════════
_VIO_KEY = "violencia_auth"

with st.sidebar:
    # ── Identidad de la app ──────────────────────────────────────────────────
    st.markdown(
        '<div style="padding:10px 0 8px 0;">'
        '<div style="font-family:' + FONT_SERIF + ';font-size:1.05rem;font-weight:500;'
        'letter-spacing:-0.01em;color:#FFFFFF;line-height:1.25;margin-bottom:4px;">'
        'Monitor Electoral<br>Per\u00fa 2026</div>'
        '<div style="font-size:0.68rem;color:rgba(255,255,255,0.55);'
        'line-height:1.4;margin-top:4px;">'
        'OACNUDH \u00b7 ' + APP_VERSION +
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="border-top:1px solid rgba(255,255,255,0.12);margin:10px 0 14px 0;"></div>',
        unsafe_allow_html=True,
    )

    # Badge confidencial
    st.markdown(
        '<span style="background:rgba(201,162,39,0.12);color:#C9A227;'
        'border:1px solid rgba(201,162,39,0.35);padding:3px 10px;'
        'border-radius:0;font-size:0.60rem;font-weight:700;'
        'letter-spacing:0.14em;text-transform:uppercase;">'
        + APP_CONFIDENTIAL_LABEL +
        '</span>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="border-top:1px solid rgba(255,255,255,0.12);margin:14px 0 12px 0;"></div>',
        unsafe_allow_html=True,
    )

    # ── Módulo 1: Principal ──────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:0.58rem;font-weight:700;letter-spacing:0.18em;'
        'text-transform:uppercase;color:rgba(255,255,255,0.40);'
        'margin-bottom:6px;padding-left:2px;">'
        '\u25ae M\u00f3dulo principal</div>',
        unsafe_allow_html=True,
    )

    # Las páginas del módulo principal — listadas como referencia visual
    # La navegación real la hace Streamlit automáticamente desde /pages
    PAGINAS_PRINCIPAL = [
        ("1", "Overview"),
        ("2", "Candidatos"),
        ("3", "Congresistas"),
        ("4", "A Tener en Cuenta"),
        ("5", "An\u00e1lisis Tem\u00e1tico"),
        ("6", "Metodolog\u00eda"),
        ("9", "Resultados 2026"),
        ("10", "Electos Análisis"),
        ("11", "Segunda Vuelta"),
    ]

    # Detectar página activa desde query params
    pagina_activa = st.query_params.get("page", "")

    nav_html = '<div style="margin-bottom:4px;">'
    for num, nombre in PAGINAS_PRINCIPAL:
        nav_html += (
            '<div style="font-size:0.80rem;color:rgba(255,255,255,0.75);'
            'padding:4px 6px;line-height:1.3;">'
            '<span style="color:rgba(255,255,255,0.30);font-size:0.65rem;'
            'margin-right:6px;font-variant-numeric:tabular-nums;">' + num + '</span>'
            + nombre +
            '</div>'
        )
    nav_html += '</div>'
    st.markdown(nav_html, unsafe_allow_html=True)

    # ── Separador entre módulos ───────────────────────────────────────────────
    st.markdown(
        '<div style="border-top:1px solid rgba(255,255,255,0.12);margin:14px 0 12px 0;"></div>',
        unsafe_allow_html=True,
    )

    # ── Módulo 2: Violencia electoral ─────────────────────────────────────────
    if st.session_state.get(_VIO_KEY, False):
        # Módulo desbloqueado
        st.markdown(
            '<div style="font-size:0.58rem;font-weight:700;letter-spacing:0.18em;'
            'text-transform:uppercase;color:rgba(255,255,255,0.40);'
            'margin-bottom:6px;padding-left:2px;">'
            '\u25ae M\u00f3dulo violencia electoral</div>',
            unsafe_allow_html=True,
        )
        PAGINAS_VIOLENCIA = [
            ("7", "Incidentes"),
            ("8", "V\u00edctimas"),
            ("9", "Perfil V\u00edctima"),
        ]
        nav_vio = '<div style="margin-bottom:4px;">'
        for num, nombre in PAGINAS_VIOLENCIA:
            nav_vio += (
                '<div style="font-size:0.80rem;color:rgba(255,255,255,0.75);'
                'padding:4px 6px;line-height:1.3;">'
                '<span style="color:rgba(255,255,255,0.30);font-size:0.65rem;'
                'margin-right:6px;font-variant-numeric:tabular-nums;">' + num + '</span>'
                + nombre +
                '</div>'
            )
        nav_vio += '</div>'
        st.markdown(nav_vio, unsafe_allow_html=True)

        # Botón de cerrar sesión del módulo violencia
        if st.button("Bloquear m\u00f3dulo violencia",
                     use_container_width=True, key="lock_violencia"):
            st.session_state[_VIO_KEY] = False
            st.rerun()

    else:
        # Módulo bloqueado — formulario inline
        st.markdown(
            '<div style="font-size:0.58rem;font-weight:700;letter-spacing:0.18em;'
            'text-transform:uppercase;color:rgba(255,255,255,0.40);'
            'margin-bottom:8px;padding-left:2px;">'
            '&#128274; M\u00f3dulo violencia electoral</div>'
            '<div style="font-size:0.72rem;color:rgba(255,255,255,0.45);'
            'margin-bottom:10px;line-height:1.4;padding-left:2px;">'
            'Incidentes \u00b7 V\u00edctimas \u00b7 Perfil V\u00edctima'
            '</div>',
            unsafe_allow_html=True,
        )
        pw_vio = st.text_input(
            "Contrase\u00f1a m\u00f3dulo",
            type="password",
            label_visibility="collapsed",
            placeholder="Contrase\u00f1a confidencial",
            key="sidebar_vio_pw",
        )
        if st.button("Desbloquear", use_container_width=True,
                     key="sidebar_vio_btn", type="secondary"):
            try:
                if pw_vio == st.secrets["violencia"]["password"]:
                    st.session_state[_VIO_KEY] = True
                    st.rerun()
                else:
                    st.error("Contrase\u00f1a incorrecta.")
            except KeyError:
                st.warning("Configura `[violencia] password` en secrets.toml")

    # ── Separador final + cerrar sesión ───────────────────────────────────────
    st.markdown(
        '<div style="border-top:1px solid rgba(255,255,255,0.12);margin:16px 0 10px 0;"></div>',
        unsafe_allow_html=True,
    )

    if st.button("Cerrar sesi\u00f3n", use_container_width=True, key="logout_btn"):
        st.session_state["autenticado"]  = False
        st.session_state[_VIO_KEY]       = False
        st.rerun()

    st.markdown(
        '<div style="font-size:0.62rem;color:rgba(255,255,255,0.25);'
        'margin-top:12px;line-height:1.5;">'
        'JNE \u00b7 REINFO \u00b7 Congreso del Per\u00fa</div>',
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════════════════════
# SECCIÓN: Home — pantalla de bienvenida con dos módulos
# ════════════════════════════════════════════════════════════════════════════════

# Masthead
st.markdown(
    '<div class="masthead">'
    '<div class="masthead-title">'
    + APP_TITLE +
    ' <em>\u00b7 Inicio</em>'
    '</div>'
    '<div class="masthead-meta">'
    '<span class="pill red">' + APP_CONFIDENTIAL_LABEL + '</span>'
    '<span>' + APP_VERSION + '</span>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

# Header de página
st.markdown(
    '<div style="padding:8px 0 28px 0;max-width:680px;">'
    '<div style="font-size:0.60rem;font-weight:700;letter-spacing:0.18em;'
    'text-transform:uppercase;color:' + COLOR_GOLD + ';margin-bottom:10px;">'
    'Herramienta de an\u00e1lisis interno \u00b7 ' + APP_VERSION +
    '</div>'
    '<h1 style="font-family:' + FONT_SERIF + ';color:' + COLOR_TEXT_PRIMARY + ';'
    'font-size:2.4rem;font-weight:500;margin:0 0 10px 0;'
    'letter-spacing:-0.025em;line-height:1.15;">'
    + APP_TITLE +
    '</h1>'
    '<p style="color:' + COLOR_TEXT_SECONDARY + ';font-size:0.95rem;'
    'margin:0;line-height:1.65;font-style:italic;">'
    + APP_SUBTITLE +
    '</p>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Módulo 1: Análisis electoral ──────────────────────────────────────────────
st.markdown(
    '<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">'
    '<div style="font-size:0.60rem;font-weight:700;letter-spacing:0.18em;'
    'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';">'
    'M\u00f3dulo 1 \u00b7 An\u00e1lisis electoral</div>'
    '<div style="flex:1;height:1px;background:' + COLOR_BORDER_SOFT + ';"></div>'
    '</div>',
    unsafe_allow_html=True,
)

SECCIONES_PRINCIPAL = [
    {
        "num":    "01",
        "titulo": "Overview",
        "desc":   "KPIs de cobertura, mapa de riesgo por departamento, distribuci\u00f3n de riesgo y alerta de congresistas.",
        "color":  COLOR_PRIMARY,
    },
    {
        "num":    "02",
        "titulo": "Candidatos",
        "desc":   "Explorador de los 9\u202f065 candidatos con perfil individual, flags REINFO y expediente JNE.",
        "color":  COLOR_PRIMARY,
    },
    {
        "num":    "03",
        "titulo": "Congresistas",
        "desc":   "89 congresistas en ejercicio que postulan en 2026, con score de riesgo y votaciones en leyes clave.",
        "color":  COLOR_PRIMARY,
    },
    {
        "num":    "04",
        "titulo": "A Tener en Cuenta",
        "desc":   "Candidatos que requieren atenci\u00f3n prioritaria por acumulaci\u00f3n de factores de riesgo.",
        "color":  COLOR_PRIMARY,
    },
    {
        "num":    "05",
        "titulo": "An\u00e1lisis Tem\u00e1tico",
        "desc":   "Patrones de votaci\u00f3n por bloque y ley, distribuci\u00f3n de score, heatmap parlamentario.",
        "color":  COLOR_PRIMARY,
    },
    {
        "num":    "06",
        "titulo": "Metodolog\u00eda",
        "desc":   "Marco metodol\u00f3gico del sistema de scoring, fuentes de datos y criterios de clasificaci\u00f3n.",
        "color":  COLOR_PRIMARY,
    },
    {
        "num":    "09",
        "titulo": "Segunda Vuelta",
        "desc":   "An\u00e1lisis comparativo de planes de gobierno: Fujimori vs. S\u00e1nchez Palomino.",
        "color":  COLOR_PRIMARY,
    },
    {
        "num":    "10",
        "titulo": "Resultados 2026",
        "desc":   "Resultados electorales: presidencial, senado, diputados y parlamento andino.",
        "color":  COLOR_PRIMARY,
    },
    {
        "num":    "11",
        "titulo": "Electos \u2014 An\u00e1lisis",
        "desc":   "Electos proyectados cruzados con score legislativo, REINFO y reelecci\u00f3n 2021\u20132026.",
        "color":  COLOR_PRIMARY,
    },
]


def _card_seccion(num, titulo, desc, color, locked=False):
    lock_html = ""
    if locked:
        lock_html = (
            '<div style="position:absolute;top:14px;right:14px;'
            'font-size:0.75rem;color:' + COLOR_TEXT_MUTED + ';">&#128274;</div>'
        )
    opacity = "0.55" if locked else "1"
    return (
        '<div style="background:' + COLOR_SURFACE + ';'
        'border:1px solid ' + COLOR_BORDER + ';'
        'border-top:3px solid ' + color + ';'
        'border-radius:0;padding:18px 18px 16px 18px;'
        'height:100%;position:relative;opacity:' + opacity + ';">'
        + lock_html +
        '<div style="font-family:' + FONT_SERIF + ';font-size:1.8rem;'
        'font-weight:300;color:' + COLOR_BORDER_SOFT + ';'
        'line-height:1;margin-bottom:8px;letter-spacing:-0.03em;">'
        + num +
        '</div>'
        '<div style="font-size:0.95rem;font-weight:600;'
        'color:' + COLOR_TEXT_PRIMARY + ';margin-bottom:8px;'
        'letter-spacing:-0.01em;line-height:1.2;">'
        + titulo +
        '</div>'
        '<div style="font-size:0.80rem;color:' + COLOR_TEXT_SECONDARY + ';'
        'line-height:1.55;">'
        + desc +
        '</div>'
        '</div>'
    )


# Grid 3 columnas para módulo 1 (9 páginas = 3 filas de 3)
for fila in range(3):
    cols = st.columns(3, gap="small")
    for i, col in enumerate(cols):
        idx = fila * 3 + i
        if idx < len(SECCIONES_PRINCIPAL):
            sec = SECCIONES_PRINCIPAL[idx]
            with col:
                st.markdown(
                    _card_seccion(sec["num"], sec["titulo"],
                                  sec["desc"], sec["color"]),
                    unsafe_allow_html=True,
                )

# ── Módulo 2: Violencia electoral ─────────────────────────────────────────────
st.markdown(
    '<div style="display:flex;align-items:center;gap:12px;'
    'margin:36px 0 16px 0;">'
    '<div style="font-size:0.60rem;font-weight:700;letter-spacing:0.18em;'
    'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';">'
    'M\u00f3dulo 2 \u00b7 Violencia electoral \u2014 Confidencial</div>'
    '<div style="flex:1;height:1px;background:' + COLOR_BORDER_SOFT + ';"></div>'
    '</div>',
    unsafe_allow_html=True,
)

vio_desbloqueado = st.session_state.get(_VIO_KEY, False)

SECCIONES_VIOLENCIA = [
    {
        "num":    "07",
        "titulo": "Incidentes",
        "desc":   "Panorama de incidentes de violencia electoral: patrones, distribuciones, mapa y l\u00ednea de tiempo.",
        "color":  COLOR_RIESGO_ALTO,
    },
    {
        "num":    "08",
        "titulo": "V\u00edctimas",
        "desc":   "Registro de v\u00edctimas de violencia electoral con caracterizaci\u00f3n de perfiles y factores de riesgo.",
        "color":  COLOR_RIESGO_ALTO,
    },
    {
        "num":    "09",
        "titulo": "Perfil V\u00edctima",
        "desc":   "Perfil individual de v\u00edctimas con cruce contra candidatos inscritos y detalle de incidentes.",
        "color":  COLOR_RIESGO_ALTO,
    },
]

cols_vio = st.columns(3, gap="small")
for col, sec in zip(cols_vio, SECCIONES_VIOLENCIA):
    with col:
        st.markdown(
            _card_seccion(sec["num"], sec["titulo"], sec["desc"],
                          sec["color"], locked=not vio_desbloqueado),
            unsafe_allow_html=True,
        )

if not vio_desbloqueado:
    st.markdown(
        '<div style="background:' + COLOR_RIESGO_ALTO_BG + ';'
        'border:1px solid ' + COLOR_RIESGO_ALTO + '44;'
        'border-left:3px solid ' + COLOR_RIESGO_ALTO + ';'
        'border-radius:0;padding:12px 16px;margin-top:14px;'
        'font-size:0.82rem;color:' + COLOR_TEXT_SECONDARY + ';line-height:1.5;">'
        'Este m\u00f3dulo contiene informaci\u00f3n sensible sobre v\u00edctimas de violencia electoral. '
        'Para desbloquear, ingresa la contrase\u00f1a del m\u00f3dulo en el panel lateral.'
        '</div>',
        unsafe_allow_html=True,
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="margin-top:48px;padding-top:14px;'
    'border-top:1px solid ' + COLOR_BORDER + ';display:flex;'
    'justify-content:space-between;font-size:0.70rem;'
    'color:' + COLOR_TEXT_MUTED + ';letter-spacing:0.04em;">'
    '<span>' + APP_CONFIDENTIAL_LABEL + ' \u00b7 ' + APP_VERSION + '</span>'
    '<span>Fuentes: JNE \u00b7 REINFO \u00b7 Congreso del Per\u00fa \u00b7 ActivityInfo</span>'
    '</div>',
    unsafe_allow_html=True,
)
