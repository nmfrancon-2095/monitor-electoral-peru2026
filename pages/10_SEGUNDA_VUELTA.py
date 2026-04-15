# ============================================================
# 10_SEGUNDA_VUELTA.py — Monitor Electoral Perú 2026
# Análisis comparativo Capa 2: Keiko Fujimori vs. Roberto Sánchez Palomino
# Datos: hoja 06_SEGUNDA_VUELTA del Excel maestro
# ============================================================

import streamlit as st
from config import (
    COLOR_PRIMARY, COLOR_BACKGROUND, COLOR_SURFACE,
    COLOR_BORDER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_ACCENT, COLOR_SURFACE_ALT,
    COLOR_ABORDAJE, COLOR_ABORDAJE_BG, LABEL_ABORDAJE,
    GLOBAL_CSS,
)
from data_loader import cargar_segunda_vuelta

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# -------------------------------------------------------
# SECTION: Autenticación heredada
# -------------------------------------------------------
if not st.session_state.get("autenticado", False):
    st.warning("Accede desde la pantalla principal.")
    st.stop()


# -------------------------------------------------------
# SECTION: Helpers de UI
# -------------------------------------------------------

def badge_nivel(nivel: str) -> str:
    """
    Devuelve un badge HTML con color según nivel de abordaje.
    Usa las clases CSS definidas en config.py GLOBAL_CSS.
    """
    clase = nivel.lower() if nivel in LABEL_ABORDAJE else "ausente"
    label = LABEL_ABORDAJE.get(nivel, nivel.capitalize())
    return (
        '<span class="badge badge-' + clase + '">'
        + label
        + '</span>'
    )


def semaforo_dot(nivel: str) -> str:
    """
    Devuelve un círculo de color (●) para uso inline junto al nombre del nivel.
    """
    color = COLOR_ABORDAJE.get(nivel, "#8A9BAA")
    return '<span style="color:' + color + '; font-size:0.75em;">&#9679;</span>'


def render_card_analisis(candidato_label: str, partido: str,
                          texto: str, nivel: str, color_acento: str) -> str:
    """
    Construye el HTML de una card de análisis para un candidato.
    color_acento: color del borde izquierdo superior de la card.
    """
    bg_nivel = COLOR_ABORDAJE_BG.get(nivel, "#F4F6F8")
    color_nivel = COLOR_ABORDAJE.get(nivel, "#8A9BAA")
    label_nivel = LABEL_ABORDAJE.get(nivel, nivel.capitalize())

    return (
        '<div style="'
        'background:#FFFFFF;'
        'border:1px solid #D8E4EF;'
        'border-top:3px solid ' + color_acento + ';'
        'border-radius:0 0 8px 8px;'
        'padding:16px 18px;'
        'height:100%;'
        '">'
        '<div style="'
        'font-size:0.63rem; font-weight:700; letter-spacing:0.10em;'
        'text-transform:uppercase; color:#7A95A8; margin-bottom:2px;'
        '">' + candidato_label + '</div>'
        '<div style="'
        'font-size:0.75rem; color:#7A95A8; margin-bottom:10px;'
        '">' + partido + '</div>'
        '<div style="'
        'font-size:0.84rem; color:#456078; line-height:1.65; margin-bottom:12px;'
        '">' + texto + '</div>'
        '<div style="'
        'display:inline-block;'
        'background:' + bg_nivel + ';'
        'color:' + color_nivel + ';'
        'border:1px solid ' + color_nivel + '33;'
        'padding:3px 9px; border-radius:3px;'
        'font-size:0.68rem; font-weight:700;'
        'letter-spacing:0.07em; text-transform:uppercase;'
        '">'
        + label_nivel +
        '</div>'
        '</div>'
    )


# -------------------------------------------------------
# SECTION: Carga de datos
# -------------------------------------------------------
try:
    df = cargar_segunda_vuelta()
except Exception as e:
    st.error(
        "No se pudo cargar la hoja **06_SEGUNDA_VUELTA** del Excel maestro. "
        "Verifica que la hoja exista con el nombre exacto y el formato correcto."
    )
    st.caption("Detalle técnico: " + str(e))
    st.stop()

if df.empty:
    st.warning("La hoja 06_SEGUNDA_VUELTA está vacía. Agrega los datos y recarga.")
    st.stop()


# -------------------------------------------------------
# SECTION: Header de página
# -------------------------------------------------------
st.markdown(
    '<div style="padding:32px 0 8px 0; max-width:760px;">'
    '<div style="font-size:0.63rem; font-weight:700; letter-spacing:0.12em;'
    'text-transform:uppercase; color:' + COLOR_ACCENT + '; margin-bottom:10px;">'
    'Resultados Elecciones Nacionales 2026 &middot; Segunda Vuelta'
    '</div>'
    '<h1 style="color:' + COLOR_TEXT_PRIMARY + '; font-size:1.65rem; font-weight:700;'
    'margin:0 0 6px 0; letter-spacing:-0.02em; line-height:1.2;">'
    'Análisis comparativo de planes de gobierno'
    '</h1>'
    '<p style="color:' + COLOR_TEXT_SECONDARY + '; font-size:0.88em; margin:0; line-height:1.6;">'
    'Keiko Fujimori (Fuerza Popular) &nbsp;&bull;&nbsp; Roberto Sánchez Palomino (Juntos por el Perú)'
    '</p>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div style="border-top:2px solid ' + COLOR_BORDER + '; margin:12px 0 20px 0;"></div>',
    unsafe_allow_html=True,
)

# Nota metodológica inline
st.markdown(
    '<div class="nota-info">'
    'Análisis descriptivo basado exclusivamente en los planes de gobierno registrados ante el JNE. '
    'Solo lo que dicen los planes &mdash; cero inferencias externas. '
    '<strong>Niveles:</strong> '
    '<strong style="color:#1E8A4A;">Aborda</strong> = &ge;1 párrafo con propuesta concreta &nbsp;&bull;&nbsp; '
    '<strong style="color:#2878B5;">Parcial</strong> = menciona en marco más amplio sin desarrollar &nbsp;&bull;&nbsp; '
    '<strong style="color:#D4760A;">Tangencial</strong> = mención incidental sin propuesta &nbsp;&bull;&nbsp; '
    '<strong style="color:#8A9BAA;">Ausente</strong> = no aparece en el plan'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)


# -------------------------------------------------------
# SECTION: Filtros
# -------------------------------------------------------

# Construir opciones de tema desde los datos
temas_disponibles = []
visto = set()
for _, row in df.iterrows():
    key = str(row.get("tema_num", "")).strip()
    label = str(row.get("tema_label", "")).strip()
    if key and key != "nan" and key not in visto:
        temas_disponibles.append({"key": key, "label": label, "display": "T" + key + " — " + label})
        visto.add(key)

opciones_display = ["Todos los temas"] + [t["display"] for t in temas_disponibles]

col_filtro, col_spacer = st.columns([2, 3])
with col_filtro:
    seleccion = st.selectbox(
        "Filtrar por tema",
        options=opciones_display,
        index=0,
        label_visibility="collapsed",
    )

# Determinar tema_num seleccionado
tema_activo = None
if seleccion != "Todos los temas":
    for t in temas_disponibles:
        if t["display"] == seleccion:
            tema_activo = t["key"]
            break

# Aplicar filtro
if tema_activo:
    df_vista = df[df["tema_num"] == tema_activo].copy()
else:
    df_vista = df.copy()

st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)


# -------------------------------------------------------
# SECTION: Tabla comparativa por subtema
# -------------------------------------------------------

if df_vista.empty:
    st.info("No hay datos para el tema seleccionado.")
    st.stop()

# Agrupar por tema para mostrar encabezados de sección
temas_en_vista = []
visto_vista = set()
for _, row in df_vista.iterrows():
    k = str(row.get("tema_num", "")).strip()
    if k not in visto_vista:
        temas_en_vista.append(k)
        visto_vista.add(k)

for tema_key in temas_en_vista:
    bloque = df_vista[df_vista["tema_num"] == tema_key]
    if bloque.empty:
        continue

    # Encabezado del tema
    tema_lbl = str(bloque.iloc[0].get("tema_label", "")).strip()
    st.markdown(
        '<div style="margin:24px 0 10px 0;">'
        '<div style="'
        'font-size:0.63rem; font-weight:700; letter-spacing:0.10em;'
        'text-transform:uppercase; color:' + COLOR_TEXT_MUTED + '; margin-bottom:4px;'
        '">Tema ' + tema_key + '</div>'
        '<div style="'
        'font-size:1.05rem; font-weight:700; color:' + COLOR_TEXT_PRIMARY + ';'
        'letter-spacing:-0.01em;'
        '">' + tema_lbl + '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Una fila por subtema
    for _, row in bloque.iterrows():
        subtema  = str(row.get("subtema", "")).strip()
        txt_fuj  = str(row.get("analisis_fujimori", "")).strip()
        txt_san  = str(row.get("analisis_sanchez", "")).strip()
        niv_fuj  = str(row.get("nivel_fujimori", "AUSENTE")).strip().upper()
        niv_san  = str(row.get("nivel_sanchez", "AUSENTE")).strip().upper()

        # Reemplazar "NAN" que pueda quedar por celdas vacías
        if txt_fuj in ("", "nan", "NAN"):
            txt_fuj = "Sin información registrada."
        if txt_san in ("", "nan", "NAN"):
            txt_san = "Sin información registrada."

        # Título del subtema
        st.markdown(
            '<div style="'
            'font-size:0.82rem; font-weight:600; color:' + COLOR_TEXT_SECONDARY + ';'
            'margin:10px 0 6px 0; padding-left:2px;'
            '">' + subtema + '</div>',
            unsafe_allow_html=True,
        )

        # Cards lado a lado
        col_fuj, col_san = st.columns(2, gap="small")

        with col_fuj:
            st.markdown(
                render_card_analisis(
                    candidato_label="Keiko Fujimori",
                    partido="Fuerza Popular",
                    texto=txt_fuj,
                    nivel=niv_fuj,
                    color_acento="#B83232",
                ),
                unsafe_allow_html=True,
            )

        with col_san:
            st.markdown(
                render_card_analisis(
                    candidato_label="Roberto Sánchez Palomino",
                    partido="Juntos por el Perú",
                    texto=txt_san,
                    nivel=niv_san,
                    color_acento="#2878B5",
                ),
                unsafe_allow_html=True,
            )

        st.markdown("<div style='margin-bottom:6px;'></div>", unsafe_allow_html=True)

    # Separador entre temas
    st.markdown(
        '<div style="border-top:1px solid ' + COLOR_BORDER + '; margin:20px 0 4px 0;"></div>',
        unsafe_allow_html=True,
    )


# -------------------------------------------------------
# SECTION: Resumen visual de niveles (solo si "Todos")
# -------------------------------------------------------
if tema_activo is None and not df_vista.empty:
    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div class="section-header">Resumen de cobertura por nivel</div>'
        '<div class="section-subheader">Distribución de niveles de abordaje en los 7 temas analizados</div>',
        unsafe_allow_html=True,
    )

    import plotly.graph_objects as go
    from config import CHART_LAYOUT_BASE, CHART_HEIGHT_SMALL

    orden_niveles = ["ABORDA", "PARCIAL", "TANGENCIAL", "AUSENTE"]
    colores_barras = [COLOR_ABORDAJE[n] for n in orden_niveles]

    conteo_fuj = [int((df_vista["nivel_fujimori"] == n).sum()) for n in orden_niveles]
    conteo_san = [int((df_vista["nivel_sanchez"] == n).sum()) for n in orden_niveles]
    labels_display = [LABEL_ABORDAJE[n] for n in orden_niveles]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Fujimori",
        x=labels_display,
        y=conteo_fuj,
        marker_color=[COLOR_ABORDAJE[n] for n in orden_niveles],
        opacity=0.92,
        text=conteo_fuj,
        textposition="outside",
        textfont=dict(size=12, color="#152638"),
    ))
    fig.add_trace(go.Bar(
        name="Sánchez Palomino",
        x=labels_display,
        y=conteo_san,
        marker_color=[COLOR_ABORDAJE[n] for n in orden_niveles],
        opacity=0.55,
        text=conteo_san,
        textposition="outside",
        textfont=dict(size=12, color="#152638"),
        marker_pattern_shape="/",
    ))

    layout = dict(**CHART_LAYOUT_BASE)
    layout.update(
        height=CHART_HEIGHT_SMALL + 40,
        barmode="group",
        bargap=0.25,
        bargroupgap=0.08,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        yaxis=dict(showgrid=True, gridcolor="#D8E4EF", zeroline=False,
                   tickfont=dict(size=11), title="Número de subtemas"),
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=12)),
        legend=dict(orientation="h", y=-0.18, xanchor="left", x=0,
                    font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=8, r=8, t=24, b=8),
    )
    fig.update_layout(**layout)

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# -------------------------------------------------------
# SECTION: Nota metodológica footer
# -------------------------------------------------------
st.markdown(
    '<div class="page-footer">'
    '<span>Análisis basado en planes de gobierno registrados ante el JNE &mdash; Per&uacute; 2026</span>'
    '<span>Monitor Electoral Per&uacute; 2026 &nbsp;&middot;&nbsp; OACNUDH</span>'
    '</div>',
    unsafe_allow_html=True,
)
