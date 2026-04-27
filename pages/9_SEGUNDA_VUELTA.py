# ============================================================
# 10_SEGUNDA_VUELTA.py — Monitor Electoral Perú 2026
# Análisis comparativo: Keiko Fujimori Higuchi vs. Roberto Sánchez Palomino
# Datos: hoja 06_SEGUNDA_VUELTA del Excel maestro
#
# Rediseño v3.0 "Forensic Editorial":
#   - Hero header con avatares de iniciales (color de partido)
#   - Scorecard visual de cobertura por tema (antes del contenido)
#   - Gráfico de resumen reposicionado arriba
#   - Cards v3 estricto: border-radius:0, colores del sistema
#   - Badge de nivel prominente en el frente de cada card
#   - Indicador de divergencia entre candidatos
#   - HTML siempre por concatenación (+)
# ============================================================

import streamlit as st
import plotly.graph_objects as go

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    APP_TITLE, APP_CONFIDENTIAL_LABEL, APP_VERSION, APP_ICON,
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_GOLD,
    COLOR_SURFACE, COLOR_SURFACE_ALT, COLOR_BACKGROUND,
    COLOR_BORDER, COLOR_BORDER_SOFT,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_ABORDAJE, COLOR_ABORDAJE_BG, LABEL_ABORDAJE,
    COLORES_PARTIDO,
    CHART_HEIGHT_SMALL, BAR_CORNER_RADIUS,
    GLOBAL_CSS,
)
from data_loader import cargar_segunda_vuelta

# ── Constantes de candidatos ─────────────────────────────────────────────────
COLOR_FUJ  = COLORES_PARTIDO.get("FUERZA POPULAR", "#D84315")
COLOR_SAN  = COLORES_PARTIDO.get("JUNTOS POR EL PER\u00da", COLORES_PARTIDO.get("JUNTOS POR EL PERU", "#AD1457"))

FONT_SERIF = "'Source Serif 4', Georgia, 'Times New Roman', serif"
FONT_SANS  = "'DM Sans', system-ui, -apple-system, sans-serif"

# ── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Segunda Vuelta \u00b7 " + APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

if not st.session_state.get("autenticado", False):
    st.warning("Accede desde la pantalla principal.")
    st.stop()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _foto_candidato(ruta: str, iniciales: str, color: str, size: int = 72) -> str:
    """
    Foto circular del candidato desde assets/.
    Si la imagen no existe o falla, cae a círculo con iniciales.
    ruta: ruta relativa desde la raíz del repo, ej: 'assets/keiko.jpg'
    """
    import os
    s = str(size)
    # Resolver ruta absoluta desde la raíz del repo
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    abs_path  = os.path.join(base_dir, ruta)
    fs = str(round(size * 0.36))

    if os.path.exists(abs_path):
        # Leer imagen y convertir a base64 para embeber inline
        import base64
        ext = ruta.split(".")[-1].lower()
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
        with open(abs_path, "rb") as f_img:
            b64 = base64.b64encode(f_img.read()).decode()
        return (
            '<div style="width:' + s + 'px;height:' + s + 'px;border-radius:50%;'
            'overflow:hidden;flex-shrink:0;border:2px solid ' + color + '44;">'
            '<img src="data:' + mime + ';base64,' + b64 + '" '
            'style="width:100%;height:100%;object-fit:cover;object-position:center top;" />'
            '</div>'
        )
    else:
        # Fallback: círculo con iniciales
        return (
            '<div style="width:' + s + 'px;height:' + s + 'px;border-radius:50%;'
            'background:' + color + ';display:flex;align-items:center;'
            'justify-content:center;flex-shrink:0;">'
            '<span style="font-family:' + FONT_SERIF + ';font-size:' + fs + 'px;'
            'font-weight:600;color:#FFFFFF;letter-spacing:-0.02em;">'
            + iniciales + '</span>'
            '</div>'
        )


def _avatar(iniciales: str, color: str, size: int = 72) -> str:
    """Mantener por compatibilidad — usa círculo con iniciales."""
    s = str(size)
    fs = str(round(size * 0.36))
    return (
        '<div style="width:' + s + 'px;height:' + s + 'px;border-radius:50%;'
        'background:' + color + ';display:flex;align-items:center;'
        'justify-content:center;flex-shrink:0;">'
        '<span style="font-family:' + FONT_SERIF + ';font-size:' + fs + 'px;'
        'font-weight:600;color:#FFFFFF;letter-spacing:-0.02em;">'
        + iniciales + '</span>'
        '</div>'
    )


def _nivel_pill(nivel: str, grande: bool = False) -> str:
    """Badge de nivel de abordaje."""
    color = COLOR_ABORDAJE.get(nivel, "#4B5A6B")
    bg    = COLOR_ABORDAJE_BG.get(nivel, "#EEEFEC")
    label = LABEL_ABORDAJE.get(nivel, nivel.capitalize())
    pad   = "5px 12px" if grande else "3px 9px"
    fs    = "0.72rem" if grande else "0.65rem"
    return (
        '<span style="background:' + bg + ';color:' + color + ';'
        'border:1px solid ' + color + '55;'
        'padding:' + pad + ';border-radius:0;'
        'font-size:' + fs + ';font-weight:700;'
        'letter-spacing:0.08em;text-transform:uppercase;'
        'display:inline-block;white-space:nowrap;">'
        + label + '</span>'
    )


def _dot(nivel: str) -> str:
    """Punto de color para el scorecard."""
    color = COLOR_ABORDAJE.get(nivel, "#4B5A6B")
    return (
        '<span style="display:inline-block;width:10px;height:10px;'
        'border-radius:50%;background:' + color + ';'
        'flex-shrink:0;margin-top:3px;"></span>'
    )


def _eyebrow(text: str) -> str:
    return (
        '<div style="font-size:0.60rem;font-weight:700;letter-spacing:0.18em;'
        'text-transform:uppercase;color:' + COLOR_GOLD + ';margin-bottom:6px;">'
        + text + '</div>'
    )


def _gold_rule() -> str:
    return (
        '<div style="margin:32px 0 26px 0;display:flex;align-items:center;gap:12px;">'
        '<div style="flex:1;height:1px;background:' + COLOR_GOLD + ';"></div>'
        '<div style="width:5px;height:5px;background:' + COLOR_TEXT_PRIMARY + ';'
        'transform:rotate(45deg);flex-shrink:0;"></div>'
        '<div style="flex:1;height:1px;background:' + COLOR_GOLD + ';"></div>'
        '</div>'
    )


def _render_card(candidato: str, partido: str,
                 texto: str, nivel: str, color_borde: str) -> str:
    """Card de análisis v3: border-radius:0, badge prominente arriba."""
    color_n = COLOR_ABORDAJE.get(nivel, "#4B5A6B")
    bg_n    = COLOR_ABORDAJE_BG.get(nivel, "#EEEFEC")
    label_n = LABEL_ABORDAJE.get(nivel, nivel.capitalize())

    return (
        '<div style="background:' + COLOR_SURFACE + ';'
        'border:1px solid ' + COLOR_BORDER + ';'
        'border-top:3px solid ' + color_borde + ';'
        'border-radius:0;padding:16px 18px;height:100%;">'
        # Eyebrow candidato
        '<div style="font-size:0.60rem;font-weight:700;letter-spacing:0.14em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:2px;">'
        + candidato + '</div>'
        # Partido
        '<div style="font-size:0.73rem;color:' + color_borde + ';'
        'font-weight:500;margin-bottom:12px;">'
        + partido + '</div>'
        # Texto del análisis
        '<div style="font-size:0.84rem;color:' + COLOR_TEXT_SECONDARY + ';'
        'line-height:1.65;margin-bottom:14px;">'
        + texto + '</div>'
        # Badge de nivel — prominente, al fondo de la card
        '<div style="display:inline-block;background:' + bg_n + ';'
        'color:' + color_n + ';'
        'border:1px solid ' + color_n + '44;'
        'padding:4px 11px;border-radius:0;'
        'font-size:0.68rem;font-weight:700;'
        'letter-spacing:0.08em;text-transform:uppercase;">'
        + label_n + '</div>'
        '</div>'
    )


# ── Carga de datos ────────────────────────────────────────────────────────────
try:
    df = cargar_segunda_vuelta()
except Exception as e:
    st.error(
        "No se pudo cargar la hoja **06_SEGUNDA_VUELTA** del Excel maestro. "
        "Verifica que la hoja exista y tenga el formato correcto."
    )
    st.caption("Detalle: " + str(e))
    st.stop()

if df.empty:
    st.warning("La hoja 06_SEGUNDA_VUELTA est\u00e1 vac\u00eda.")
    st.stop()

# ── Pre-calcular métricas de cobertura ────────────────────────────────────────
orden_niveles  = ["ABORDA", "PARCIAL", "TANGENCIAL", "AUSENTE"]
conteo_fuj = {n: int((df["nivel_fujimori"] == n).sum()) for n in orden_niveles}
conteo_san = {n: int((df["nivel_sanchez"]  == n).sum()) for n in orden_niveles}
total_subtemas = len(df)

# Temas únicos ordenados
temas_lista = []
visto = set()
for _, row in df.iterrows():
    k = str(row.get("tema_num", "")).strip()
    l = str(row.get("tema_label", "")).strip()
    if k and k != "nan" and k not in visto:
        temas_lista.append({"key": k, "label": l})
        visto.add(k)


# ════════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1 — Masthead + Hero header
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="masthead">'
    '<div class="masthead-title">'
    + APP_TITLE +
    ' <em>\u00b7 Segunda Vuelta</em>'
    '</div>'
    '<div class="masthead-meta">'
    '<span class="pill red">' + APP_CONFIDENTIAL_LABEL + '</span>'
    '<span>' + APP_VERSION + '</span>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

# Hero: dos columnas de candidatos con avatar + datos + score rápido
col_hero_fuj, col_hero_vs, col_hero_san = st.columns([5, 1, 5])

with col_hero_fuj:
    # Score compacto de Fujimori
    score_chips_fuj = ""
    for n in orden_niveles:
        c   = COLOR_ABORDAJE[n]
        bg  = COLOR_ABORDAJE_BG[n]
        lbl = LABEL_ABORDAJE[n]
        cnt = conteo_fuj[n]
        score_chips_fuj += (
            '<div style="display:flex;align-items:center;gap:6px;margin-bottom:5px;">'
            + _dot(n) +
            '<span style="font-size:0.78rem;color:' + COLOR_TEXT_SECONDARY + ';'
            'flex:1;">' + lbl + '</span>'
            '<span style="font-family:' + FONT_SERIF + ';font-size:1.05rem;'
            'font-weight:600;color:' + c + ';font-variant-numeric:tabular-nums;">'
            + str(cnt) + '</span>'
            '</div>'
        )

    st.markdown(
        '<div style="background:' + COLOR_SURFACE + ';border:1px solid ' + COLOR_BORDER + ';'
        'border-top:4px solid ' + COLOR_FUJ + ';border-radius:0;padding:24px 28px;">'
        # Avatar + nombre
        '<div style="display:flex;align-items:center;gap:16px;margin-bottom:18px;">'
        + _foto_candidato("assets/keiko.jpeg", "KF", COLOR_FUJ, 64) +
        '<div>'
        '<div style="font-family:' + FONT_SERIF + ';font-size:1.5rem;font-weight:500;'
        'color:' + COLOR_TEXT_PRIMARY + ';letter-spacing:-0.02em;line-height:1.1;">'
        'Keiko Fujimori Higuchi</div>'
        '<div style="font-size:0.80rem;color:' + COLOR_FUJ + ';font-weight:600;'
        'margin-top:3px;">Fuerza Popular</div>'
        '</div>'
        '</div>'
        # Separador
        '<div style="border-top:1px solid ' + COLOR_BORDER_SOFT + ';margin-bottom:14px;"></div>'
        # Score
        '<div style="font-size:0.60rem;font-weight:700;letter-spacing:0.14em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:10px;">'
        'Cobertura en ' + str(total_subtemas) + ' subtemas</div>'
        + score_chips_fuj +
        '</div>',
        unsafe_allow_html=True,
    )

with col_hero_vs:
    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:center;'
        'height:100%;min-height:200px;">'
        '<div style="font-family:' + FONT_SERIF + ';font-size:1.6rem;font-weight:300;'
        'color:' + COLOR_TEXT_MUTED + ';letter-spacing:0.05em;">vs.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

with col_hero_san:
    score_chips_san = ""
    for n in orden_niveles:
        c   = COLOR_ABORDAJE[n]
        cnt = conteo_san[n]
        lbl = LABEL_ABORDAJE[n]
        score_chips_san += (
            '<div style="display:flex;align-items:center;gap:6px;margin-bottom:5px;">'
            + _dot(n) +
            '<span style="font-size:0.78rem;color:' + COLOR_TEXT_SECONDARY + ';'
            'flex:1;">' + lbl + '</span>'
            '<span style="font-family:' + FONT_SERIF + ';font-size:1.05rem;'
            'font-weight:600;color:' + c + ';font-variant-numeric:tabular-nums;">'
            + str(cnt) + '</span>'
            '</div>'
        )

    st.markdown(
        '<div style="background:' + COLOR_SURFACE + ';border:1px solid ' + COLOR_BORDER + ';'
        'border-top:4px solid ' + COLOR_SAN + ';border-radius:0;padding:24px 28px;">'
        '<div style="display:flex;align-items:center;gap:16px;margin-bottom:18px;">'
        + _foto_candidato("assets/roberto.jpg", "RS", COLOR_SAN, 64) +
        '<div>'
        '<div style="font-family:' + FONT_SERIF + ';font-size:1.5rem;font-weight:500;'
        'color:' + COLOR_TEXT_PRIMARY + ';letter-spacing:-0.02em;line-height:1.1;">'
        'Roberto S\u00e1nchez Palomino</div>'
        '<div style="font-size:0.80rem;color:' + COLOR_SAN + ';font-weight:600;'
        'margin-top:3px;">Juntos por el Per\u00fa</div>'
        '</div>'
        '</div>'
        '<div style="border-top:1px solid ' + COLOR_BORDER_SOFT + ';margin-bottom:14px;"></div>'
        '<div style="font-size:0.60rem;font-weight:700;letter-spacing:0.14em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:10px;">'
        'Cobertura en ' + str(total_subtemas) + ' subtemas</div>'
        + score_chips_san +
        '</div>',
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2 — Gráfico de cobertura + scorecard de temas
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(_gold_rule(), unsafe_allow_html=True)

col_chart, col_scorecard = st.columns([3, 2], gap="large")

with col_chart:
    st.markdown(
        _eyebrow("RESUMEN \u00b7 COBERTURA GLOBAL") +
        '<div style="font-family:' + FONT_SERIF + ';font-size:1.35rem;font-weight:500;'
        'color:' + COLOR_TEXT_PRIMARY + ';letter-spacing:-0.015em;margin-bottom:4px;">'
        'Distribuci\u00f3n de niveles de abordaje</div>'
        '<div style="font-size:0.82rem;color:' + COLOR_TEXT_SECONDARY + ';'
        'font-style:italic;margin-bottom:14px;">'
        'Sobre ' + str(total_subtemas) + ' subtemas analizados en 7 temas</div>',
        unsafe_allow_html=True,
    )

    labels_display = [LABEL_ABORDAJE[n] for n in orden_niveles]
    vals_fuj = [conteo_fuj[n] for n in orden_niveles]
    vals_san = [conteo_san[n] for n in orden_niveles]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Fujimori Higuchi",
        x=labels_display,
        y=vals_fuj,
        marker_color=[COLOR_ABORDAJE[n] for n in orden_niveles],
        marker_line_width=0,
        opacity=0.95,
        text=vals_fuj,
        textposition="outside",
        textfont=dict(size=13, color=COLOR_TEXT_PRIMARY, family=FONT_SANS),
        hovertemplate="<b>Fujimori</b><br>%{x}: %{y} subtemas<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="S\u00e1nchez Palomino",
        x=labels_display,
        y=vals_san,
        marker_color=[COLOR_ABORDAJE[n] for n in orden_niveles],
        marker_line_width=0,
        opacity=0.45,
        text=vals_san,
        textposition="outside",
        textfont=dict(size=13, color=COLOR_TEXT_PRIMARY, family=FONT_SANS),
        marker_pattern_shape="/",
        hovertemplate="<b>S\u00e1nchez</b><br>%{x}: %{y} subtemas<extra></extra>",
    ))
    fig.update_traces(marker=dict(cornerradius=BAR_CORNER_RADIUS))
    fig.update_layout(
        height=CHART_HEIGHT_SMALL + 30,
        barmode="group",
        bargap=0.28,
        bargroupgap=0.06,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_SANS, size=11, color=COLOR_TEXT_PRIMARY),
        yaxis=dict(
            showgrid=True, gridcolor=COLOR_BORDER_SOFT, zeroline=False,
            tickfont=dict(size=11), title="N\u00famero de subtemas",
        ),
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=12)),
        legend=dict(
            orientation="h", y=-0.22, xanchor="left", x=0,
            font=dict(size=11), bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=8, r=8, t=24, b=8),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with col_scorecard:
    st.markdown(
        _eyebrow("MAPA \u00b7 COBERTURA POR TEMA") +
        '<div style="font-family:' + FONT_SERIF + ';font-size:1.35rem;font-weight:500;'
        'color:' + COLOR_TEXT_PRIMARY + ';letter-spacing:-0.015em;margin-bottom:4px;">'
        'Comparativa por tema</div>'
        '<div style="font-size:0.82rem;color:' + COLOR_TEXT_SECONDARY + ';'
        'font-style:italic;margin-bottom:14px;">'
        'Nivel dominante por tema (primer subtema)</div>',
        unsafe_allow_html=True,
    )

    # Tabla compacta: tema | nivel FUJ | nivel SAN
    # Header
    scorecard_html = (
        '<div style="background:' + COLOR_SURFACE + ';border:1px solid ' + COLOR_BORDER + ';'
        'border-top:2px solid ' + COLOR_PRIMARY + ';border-radius:0;">'
        # Header de columnas
        '<div style="display:grid;grid-template-columns:1fr 90px 90px;'
        'background:' + COLOR_SURFACE_ALT + ';'
        'border-bottom:1px solid ' + COLOR_BORDER + ';'
        'padding:8px 12px;">'
        '<div style="font-size:0.60rem;font-weight:700;letter-spacing:0.12em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';">Tema</div>'
        '<div style="font-size:0.60rem;font-weight:700;letter-spacing:0.12em;'
        'text-transform:uppercase;color:' + COLOR_FUJ + ';text-align:center;">KF</div>'
        '<div style="font-size:0.60rem;font-weight:700;letter-spacing:0.12em;'
        'text-transform:uppercase;color:' + COLOR_SAN + ';text-align:center;">RSP</div>'
        '</div>'
    )

    for t in temas_lista:
        bloque = df[df["tema_num"] == t["key"]]
        if bloque.empty:
            continue
        # Nivel más frecuente del tema para cada candidato
        niv_f = bloque["nivel_fujimori"].mode().iloc[0] if not bloque["nivel_fujimori"].mode().empty else "AUSENTE"
        niv_s = bloque["nivel_sanchez"].mode().iloc[0]  if not bloque["nivel_sanchez"].mode().empty  else "AUSENTE"

        # Fondo de fila: highlight si hay divergencia fuerte
        is_divergent = (
            (niv_f == "ABORDA" and niv_s == "AUSENTE") or
            (niv_s == "ABORDA" and niv_f == "AUSENTE")
        )
        row_bg = "#FBF4E8" if is_divergent else COLOR_SURFACE

        scorecard_html += (
            '<div style="display:grid;grid-template-columns:1fr 90px 90px;'
            'padding:9px 12px;background:' + row_bg + ';'
            'border-bottom:1px solid ' + COLOR_BORDER_SOFT + ';'
            'align-items:center;">'
            '<div style="font-size:0.80rem;color:' + COLOR_TEXT_PRIMARY + ';'
            'font-weight:500;padding-right:8px;line-height:1.3;">'
            + t["label"] + '</div>'
            '<div style="text-align:center;">' + _nivel_pill(niv_f) + '</div>'
            '<div style="text-align:center;">' + _nivel_pill(niv_s) + '</div>'
            '</div>'
        )

    scorecard_html += (
        '<div style="padding:8px 12px;font-size:0.68rem;'
        'color:' + COLOR_TEXT_MUTED + ';border-top:1px solid ' + COLOR_BORDER + ';'
        'background:' + COLOR_SURFACE_ALT + ';">'
        '<span style="background:#FBF4E8;padding:2px 6px;margin-right:4px;'
        'font-size:0.63rem;">\u25a0</span>'
        'Divergencia significativa entre candidatos'
        '</div>'
        '</div>'
    )

    st.markdown(scorecard_html, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3 — Nota metodológica + filtro
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(_gold_rule(), unsafe_allow_html=True)

st.markdown(
    '<div class="nota-info">'
    '<span class="nota-hd">Nota metodol\u00f3gica</span>'
    'An\u00e1lisis descriptivo basado exclusivamente en los planes de gobierno '
    'registrados ante el JNE. Solo lo que dicen los planes &mdash; cero inferencias externas. '
    '<strong>Niveles:</strong> '
    '<strong style="color:#1B5E3A;">Aborda</strong> = \u22651 p\u00e1rrafo con propuesta concreta &nbsp;&bull;&nbsp; '
    '<strong style="color:#13315C;">Parcial</strong> = menciona en marco m\u00e1s amplio sin desarrollar &nbsp;&bull;&nbsp; '
    '<strong style="color:#9E5200;">Tangencial</strong> = menci\u00f3n incidental sin propuesta &nbsp;&bull;&nbsp; '
    '<strong style="color:#4B5A6B;">Ausente</strong> = no aparece en el plan'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)

# Filtro de tema
opciones_display = ["Todos los temas"] + [
    "T" + t["key"] + " \u2014 " + t["label"] for t in temas_lista
]
col_filtro, _ = st.columns([2, 3])
with col_filtro:
    seleccion = st.selectbox(
        "Filtrar por tema",
        options=opciones_display,
        index=0,
        label_visibility="collapsed",
    )

tema_activo = None
if seleccion != "Todos los temas":
    for t in temas_lista:
        if seleccion == "T" + t["key"] + " \u2014 " + t["label"]:
            tema_activo = t["key"]
            break

df_vista = df[df["tema_num"] == tema_activo].copy() if tema_activo else df.copy()

if df_vista.empty:
    st.info("No hay datos para el tema seleccionado.")
    st.stop()


# ════════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4 — Análisis por tema y subtema
# ════════════════════════════════════════════════════════════════════════════════
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

    tema_lbl = str(bloque.iloc[0].get("tema_label", "")).strip()

    # Encabezado editorial del tema
    st.markdown(
        '<div style="margin:32px 0 16px 0;">'
        '<div style="display:flex;align-items:baseline;gap:14px;margin-bottom:6px;">'
        '<span style="font-family:' + FONT_SERIF + ';font-size:3rem;font-weight:300;'
        'color:' + COLOR_BORDER_SOFT + ';line-height:1;letter-spacing:-0.04em;">'
        + tema_key + '</span>'
        '<div>'
        '<div style="font-size:0.60rem;font-weight:700;letter-spacing:0.16em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:3px;">'
        'Tema ' + tema_key + '</div>'
        '<div style="font-family:' + FONT_SERIF + ';font-size:1.55rem;font-weight:500;'
        'color:' + COLOR_TEXT_PRIMARY + ';letter-spacing:-0.02em;line-height:1.15;">'
        + tema_lbl + '</div>'
        '</div>'
        '</div>'
        '<div style="height:2px;background:linear-gradient(to right,'
        + COLOR_FUJ + ',' + COLOR_SAN + ');margin-top:4px;"></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    for _, row in bloque.iterrows():
        subtema = str(row.get("subtema", "")).strip()
        txt_fuj = str(row.get("analisis_fujimori", "")).strip()
        txt_san = str(row.get("analisis_sanchez", "")).strip()
        niv_fuj = str(row.get("nivel_fujimori", "AUSENTE")).strip().upper()
        niv_san = str(row.get("nivel_sanchez",  "AUSENTE")).strip().upper()

        if txt_fuj in ("", "nan", "NAN"):
            txt_fuj = "Sin informaci\u00f3n registrada."
        if txt_san in ("", "nan", "NAN"):
            txt_san = "Sin informaci\u00f3n registrada."

        # Detectar divergencia entre candidatos
        is_strong_div = (
            (niv_fuj == "ABORDA" and niv_san in ("AUSENTE", "TANGENCIAL")) or
            (niv_san == "ABORDA" and niv_fuj in ("AUSENTE", "TANGENCIAL"))
        )

        # Subtema header con indicador de divergencia si aplica
        div_badge = ""
        if is_strong_div:
            div_badge = (
                '<span style="background:#FBF4E8;color:#9E5200;'
                'border:1px solid #9E520044;'
                'padding:2px 8px;border-radius:0;'
                'font-size:0.60rem;font-weight:700;letter-spacing:0.08em;'
                'text-transform:uppercase;margin-left:10px;">'
                'Divergencia</span>'
            )

        st.markdown(
            '<div style="display:flex;align-items:center;margin:14px 0 8px 0;">'
            '<div style="width:3px;height:16px;background:' + COLOR_GOLD + ';'
            'margin-right:10px;flex-shrink:0;"></div>'
            '<span style="font-size:0.88rem;font-weight:600;'
            'color:' + COLOR_TEXT_PRIMARY + ';">' + subtema + '</span>'
            + div_badge +
            '</div>',
            unsafe_allow_html=True,
        )

        col_fuj, col_san = st.columns(2, gap="small")
        with col_fuj:
            st.markdown(
                _render_card("Keiko Fujimori Higuchi", "Fuerza Popular",
                             txt_fuj, niv_fuj, COLOR_FUJ),
                unsafe_allow_html=True,
            )
        with col_san:
            st.markdown(
                _render_card("Roberto S\u00e1nchez Palomino", "Juntos por el Per\u00fa",
                             txt_san, niv_san, COLOR_SAN),
                unsafe_allow_html=True,
            )

        st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

    # Separador entre temas
    st.markdown(
        '<div style="border-top:1px solid ' + COLOR_BORDER + ';'
        'margin:24px 0 4px 0;"></div>',
        unsafe_allow_html=True,
    )


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="margin-top:40px;padding-top:14px;'
    'border-top:1px solid ' + COLOR_BORDER + ';display:flex;'
    'justify-content:space-between;font-size:0.70rem;'
    'color:' + COLOR_TEXT_MUTED + ';letter-spacing:0.04em;">'
    '<span>An\u00e1lisis basado en planes de gobierno registrados ante el JNE \u00b7 Per\u00fa 2026</span>'
    '<span>Monitor Electoral Per\u00fa 2026 \u00b7 OACNUDH</span>'
    '</div>',
    unsafe_allow_html=True,
)
