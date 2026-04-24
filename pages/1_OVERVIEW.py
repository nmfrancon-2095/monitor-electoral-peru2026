# ============================================================
# pages/1_Overview.py — Monitor Electoral Perú 2026
# Resumen ejecutivo: KPIs jerárquicos, mapa, distribución de
# riesgo, votos por bloque, alertas de congresistas.
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    APP_TITLE, APP_CONFIDENTIAL_LABEL, APP_ICON, APP_VERSION,
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_BACKGROUND, COLOR_SURFACE,
    COLOR_BORDER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_RIESGO_ALTO, COLOR_RIESGO_ALTO_BG,
    COLOR_RIESGO_MEDIO, COLOR_RIESGO_MEDIO_BG,
    COLOR_RIESGO_BAJO, COLOR_RIESGO_BAJO_BG,
    COLOR_RIESGO_NONE, COLOR_REINFO,
    COLOR_BLOQUE,
    CHART_HEIGHT, CHART_HEIGHT_SMALL, CHART_LAYOUT_BASE,
    REGIONES_PRIORITARIAS, LEYES_COLS, GLOBAL_CSS,
    SCORE_ALTO_MIN, SCORE_MEDIO_MIN,
)
from data_loader import (
    cargar_candidatos, cargar_votaciones, cargar_reinfo,
    cargar_leyes, resumen_kpis, candidatos_con_flags,
)

def layout_override(overrides: dict) -> dict:
    """
    Combina CHART_LAYOUT_BASE con overrides puntuales sin conflicto.
    Úsalo en update_layout(**layout_override({...})) en vez de
    pasar **CHART_LAYOUT_BASE y kwargs por separado.
    """
    base = {k: v for k, v in CHART_LAYOUT_BASE.items()}
    base.update(overrides)
    return base

# -------------------------------------------------------
# SECTION: Page setup
# -------------------------------------------------------
st.set_page_config(
    page_title=f"Overview · {APP_TITLE}",
    page_icon=APP_ICON,
    layout="wide",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

if not st.session_state.get("autenticado", False):
    st.warning("Debes iniciar sesión primero.")
    st.stop()

# -------------------------------------------------------
# SECTION: Cargar datos
# -------------------------------------------------------
with st.spinner("Cargando datos..."):
    kpis   = resumen_kpis()
    cands  = cargar_candidatos()
    votos  = cargar_votaciones()
    reinfo = cargar_reinfo()
    leyes_df = cargar_leyes()

# -------------------------------------------------------
# SECTION: Header de página
# Tipografía con peso como sistema de jerarquía, sin emoji
# como ícono principal (solo en indicadores de estado).
# -------------------------------------------------------
st.markdown(
    f"""
    <div style="padding:4px 0 20px 0; border-bottom:2px solid {COLOR_BORDER};
                margin-bottom:28px;">
        <div style="font-size:0.63rem; font-weight:700; letter-spacing:0.12em;
                    text-transform:uppercase; color:{COLOR_ACCENT}; margin-bottom:6px;">
            Resumen ejecutivo
        </div>
        <h1 style="font-size:1.6rem; font-weight:700; color:{COLOR_TEXT_PRIMARY};
                   margin:0 0 4px 0; letter-spacing:-0.02em; line-height:1.2;">
            Monitor Electoral Perú 2026
        </h1>
        <p style="font-size:0.85rem; color:{COLOR_TEXT_SECONDARY}; margin:0;">
            Panorama general del monitoreo · JNE · REINFO · Congreso del Perú
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------
# SECTION: KPIs — jerarquía visual intencional
#
# Principio: no 5 cards idénticas (anti-patrón "hero metric").
# Estructura: 1 protagonista (total candidatos, dato de escala)
# + 4 secundarias más compactas.
# El protagonista establece contexto; los secundarios señalan
# lo que importa analíticamente.
# -------------------------------------------------------

# Fila de KPIs: col grande + 4 pequeñas
kpi_main, kpi_gap, k1, k2, k3 = st.columns([2.2, 0.2, 1, 1, 1])

with kpi_main:
    st.markdown(
        f"""
        <div style="background:{COLOR_SURFACE}; border:1px solid {COLOR_BORDER};
                    border-radius:8px; padding:20px 24px 18px 24px;">
            <div style="font-size:0.63rem; font-weight:700; letter-spacing:0.10em;
                        text-transform:uppercase; color:{COLOR_TEXT_MUTED};
                        margin-bottom:6px;">
                Total candidatos inscritos
            </div>
            <div style="font-size:3.2rem; font-weight:700; color:{COLOR_TEXT_PRIMARY};
                        font-variant-numeric:tabular-nums; letter-spacing:-0.03em;
                        line-height:1;">
                {kpis['total_candidatos']:,}
            </div>
            <div style="font-size:0.78rem; color:{COLOR_TEXT_SECONDARY}; margin-top:6px;">
                Candidatos inscritos en el JNE · Elecciones 2026
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Helper para las 4 KPIs secundarias
def kpi_secundaria(label, valor, nota, color_valor=None):
    color_v = color_valor or COLOR_TEXT_PRIMARY
    return f"""
        <div style="background:{COLOR_SURFACE}; border:1px solid {COLOR_BORDER};
                    border-radius:8px; padding:16px 18px 14px 18px; height:100%;">
            <div style="font-size:0.60rem; font-weight:700; letter-spacing:0.09em;
                        text-transform:uppercase; color:{COLOR_TEXT_MUTED};
                        margin-bottom:6px; line-height:1.3;">
                {label}
            </div>
            <div style="font-size:2rem; font-weight:700; color:{color_v};
                        font-variant-numeric:tabular-nums; letter-spacing:-0.02em;
                        line-height:1;">
                {valor}
            </div>
            <div style="font-size:0.72rem; color:{COLOR_TEXT_SECONDARY};
                        margin-top:4px; line-height:1.4;">
                {nota}
            </div>
        </div>"""

with k1:
    st.markdown(kpi_secundaria(
        "Congresistas postulando",
        kpis["congresistas_postulando"],
        "En ejercicio · postulan a cargo en 2026",
    ), unsafe_allow_html=True)

with k2:
    st.markdown(kpi_secundaria(
        "Vínculo REINFO",
        kpis["con_reinfo"],
        "Candidatos con derechos mineros registrados",
        color_valor=COLOR_REINFO,
    ), unsafe_allow_html=True)

with k3:
    st.markdown(kpi_secundaria(
        "Riesgo alto",
        kpis["riesgo_alto"],
        f"Score ≥ {SCORE_ALTO_MIN} · Congresistas postulantes",
        color_valor=COLOR_RIESGO_ALTO,
    ), unsafe_allow_html=True)

st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

# -------------------------------------------------------
# SECTION: Fila principal — Mapa + Panel de riesgo
# -------------------------------------------------------
col_mapa, col_riesgo = st.columns([3, 2], gap="large")

# --- Mapa de burbujas ---
with col_mapa:
    st.markdown(
        f"""<div style="font-size:0.75rem; font-weight:700; letter-spacing:0.08em;
                        text-transform:uppercase; color:{COLOR_TEXT_MUTED};
                        margin-bottom:4px;">Distribución geográfica</div>
            <div class="section-header" style="margin-bottom:4px;">
                Candidatos por región</div>
            <div class="section-subheader">
                Regiones prioritarias destacadas · tamaño proporcional al número de candidatos
            </div>""",
        unsafe_allow_html=True,
    )

    coords_peru = {
        "Lima": (-12.046, -77.043), "Arequipa": (-16.409, -71.537),
        "Cusco": (-13.531, -71.967), "La Libertad": (-8.115, -79.028),
        "Piura": (-5.194, -80.632), "Cajamarca": (-7.163, -78.500),
        "Junín": (-12.065, -75.204), "Puno": (-15.840, -70.022),
        "Lambayeque": (-6.701, -79.906), "Ancash": (-9.530, -77.528),
        "Loreto": (-3.749, -73.253), "San Martín": (-6.485, -76.361),
        "Ayacucho": (-13.158, -74.223), "Ica": (-14.068, -75.729),
        "Huánuco": (-9.930, -76.242), "Ucayali": (-8.379, -74.553),
        "Tacna": (-18.013, -70.253), "Moquegua": (-17.193, -70.935),
        "Tumbes": (-3.566, -80.451), "Madre De Dios": (-12.593, -69.189),
        "Amazonas": (-6.231, -77.870), "Apurímac": (-14.051, -72.882),
        "Huancavelica": (-12.786, -74.976), "Pasco": (-10.682, -76.261),
        "Callao": (-12.056, -77.118),
    }

    mapa_data = (
        cands.groupby("region")
        .agg(total=("dni", "count"), es_prioritaria=("es_region_prioritaria", "max"))
        .reset_index()
    )

    reinfo_exploded = (
        reinfo["dptos_mineros"].str.split(";").explode()
        .str.strip().str.title()
        .reset_index(drop=True).to_frame(name="region")
    )
    reinfo_por_region = (
        reinfo_exploded.groupby("region").size().reset_index(name="con_reinfo")
    )
    mapa_data = mapa_data.merge(reinfo_por_region, on="region", how="left")
    mapa_data["con_reinfo"] = mapa_data["con_reinfo"].fillna(0).astype(int)
    mapa_data["tipo_region"] = mapa_data["es_prioritaria"].map(
        {True: "Prioritaria", False: "Estándar"}
    )
    mapa_data["lat"] = mapa_data["region"].map(
        lambda r: coords_peru.get(r, (None, None))[0]
    )
    mapa_data["lon"] = mapa_data["region"].map(
        lambda r: coords_peru.get(r, (None, None))[1]
    )
    mapa_data = mapa_data.dropna(subset=["lat", "lon"])

    fig_mapa = px.scatter_mapbox(
        mapa_data,
        lat="lat", lon="lon",
        size="total",
        color="tipo_region",
        color_discrete_map={
            "Prioritaria": COLOR_RIESGO_ALTO,
            "Estándar":    COLOR_ACCENT,
        },
        hover_name="region",
        hover_data={
            "total": True, "con_reinfo": True,
            "tipo_region": True, "lat": False, "lon": False,
        },
        labels={
            "total": "Candidatos",
            "con_reinfo": "Con REINFO",
            "tipo_region": "Región",
        },
        size_max=40, zoom=4,
        center={"lat": -9.19, "lon": -75.0},
        mapbox_style="carto-positron",
        height=CHART_HEIGHT,
    )
    fig_mapa.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=COLOR_SURFACE,
        legend=dict(
            orientation="h",
            yanchor="bottom", y=0.01,
            xanchor="right", x=0.99,
            bgcolor="rgba(255,255,255,0.88)",
            bordercolor=COLOR_BORDER,
            borderwidth=1,
            font=dict(size=11),
        ),
    )
    st.plotly_chart(fig_mapa, use_container_width=True)

# --- Panel de riesgo (congresistas) ---
with col_riesgo:
    st.markdown(
        f"""<div style="font-size:0.75rem; font-weight:700; letter-spacing:0.08em;
                        text-transform:uppercase; color:{COLOR_TEXT_MUTED};
                        margin-bottom:4px;">Congresistas postulantes</div>
            <div class="section-header" style="margin-bottom:4px;">
                Niveles de riesgo</div>
            <div class="section-subheader">
                89 congresistas en ejercicio que postulan en 2026
            </div>""",
        unsafe_allow_html=True,
    )

    # Distribución de riesgo: barras horizontales apiladas en 1 fila
    # Razón: con solo 3-4 categorías, las barras apiladas son más honestas
    # y compactas que un donut — el donut con tan pocas categorías
    # fuerza al ojo a estimar ángulos, que es cognitivamente costoso.
    riesgo_counts = votos["nivel_riesgo"].value_counts().reset_index()
    riesgo_counts.columns = ["nivel", "cantidad"]
    orden = ["alto", "medio", "bajo", "none"]
    etiquetas = {"alto": "Alto", "medio": "Medio", "bajo": "Bajo", "none": "Sin dato"}
    colores_riesgo_map = {
        "alto": COLOR_RIESGO_ALTO, "medio": COLOR_RIESGO_MEDIO,
        "bajo": COLOR_RIESGO_BAJO, "none": COLOR_RIESGO_NONE,
    }
    riesgo_counts["orden"] = riesgo_counts["nivel"].map(
        {v: i for i, v in enumerate(orden)}
    )
    riesgo_counts = riesgo_counts.sort_values("orden")
    riesgo_counts["etiqueta"] = riesgo_counts["nivel"].map(etiquetas)
    riesgo_counts["color"] = riesgo_counts["nivel"].map(colores_riesgo_map)

    # Cards de conteo por nivel — más legibles que un gráfico para N=4
    total_congs = len(votos)
    rc_dict = dict(zip(riesgo_counts["nivel"], riesgo_counts["cantidad"]))

    niveles_display = [
        ("alto",  "Riesgo alto",   COLOR_RIESGO_ALTO,  COLOR_RIESGO_ALTO_BG),
        ("medio", "Riesgo medio",  COLOR_RIESGO_MEDIO, COLOR_RIESGO_MEDIO_BG),
        ("bajo",  "Riesgo bajo",   COLOR_RIESGO_BAJO,  COLOR_RIESGO_BAJO_BG),
        ("none",  "Sin dato",      COLOR_RIESGO_NONE,  "#F4F6F8"),
    ]

    for nivel, label, color, bg in niveles_display:
        n = rc_dict.get(nivel, 0)
        pct = round(n / total_congs * 100) if total_congs > 0 else 0
        # Barra de progreso como fondo — más honesta que un gráfico
        st.markdown(
            f"""
            <div style="background:{bg}; border:1px solid {COLOR_BORDER};
                        border-left:4px solid {color};
                        border-radius:0 6px 6px 0;
                        padding:10px 14px; margin-bottom:8px;
                        display:flex; justify-content:space-between;
                        align-items:center;">
                <div>
                    <div style="font-size:0.72rem; font-weight:700;
                                letter-spacing:0.06em; text-transform:uppercase;
                                color:{color};">
                        {label}
                    </div>
                    <div style="font-size:0.75rem; color:{COLOR_TEXT_SECONDARY};
                                margin-top:1px;">
                        {pct}% de los congresistas postulantes
                    </div>
                </div>
                <div style="font-size:1.8rem; font-weight:700; color:{color};
                            font-variant-numeric:tabular-nums;
                            letter-spacing:-0.02em; line-height:1;">
                    {n}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Top partidos con riesgo alto — barras horizontales limpias
    st.markdown(
        f"""<div style="font-size:0.72rem; font-weight:700; letter-spacing:0.07em;
                        text-transform:uppercase; color:{COLOR_TEXT_MUTED};
                        margin-bottom:8px;">
                Partidos · congresistas de riesgo alto
            </div>""",
        unsafe_allow_html=True,
    )

    riesgo_partido = (
        votos[votos["nivel_riesgo"] == "alto"]
        .groupby("partido").size()
        .reset_index(name="n")
        .sort_values("n", ascending=True)
        .tail(12)
    )
    riesgo_partido["partido_label"] = riesgo_partido["partido"].str.upper()

    # Margen izquierdo dinámico: ~6.5px por carácter del nombre más largo
    max_chars = riesgo_partido["partido_label"].str.len().max()
    margen_izq = min(int(max_chars * 6.5), 280)

    altura_partidos = max(240, len(riesgo_partido) * 42 + 20)

    fig_partidos = go.Figure()
    fig_partidos.add_trace(go.Bar(
        x=riesgo_partido["n"],
        y=riesgo_partido["partido_label"],
        orientation="h",
        marker_color=COLOR_RIESGO_ALTO,
        text=riesgo_partido["n"],
        textposition="outside",
        textfont=dict(size=12, color=COLOR_TEXT_PRIMARY,
                      family="'Plus Jakarta Sans', system-ui, sans-serif"),
        hovertemplate="<b>%{y}</b><br>%{x} congresistas riesgo alto<extra></extra>",
        cliponaxis=False,
    ))
    fig_partidos.update_layout(
        height=altura_partidos,
        margin=dict(l=margen_izq, r=48, t=4, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        font=dict(family="'Plus Jakarta Sans', system-ui, sans-serif",
                  size=11, color=COLOR_TEXT_PRIMARY),
        xaxis=dict(
            visible=False,
            showgrid=False,
            zeroline=False,
            range=[0, riesgo_partido["n"].max() * 1.25],
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=10.5, color=COLOR_TEXT_SECONDARY),
            automargin=False,
        ),
    )
    st.plotly_chart(fig_partidos, use_container_width=True)

st.markdown(
    f'<div style="border-top:1px solid {COLOR_BORDER}; margin:24px 0;"></div>',
    unsafe_allow_html=True,
)

# -------------------------------------------------------
# SECTION: Fila secundaria — Votos por bloque + REINFO
# -------------------------------------------------------
col_bloques, col_reinfo_viz = st.columns([2, 1], gap="large")

with col_bloques:
    st.markdown(
        f"""<div style="font-size:0.75rem; font-weight:700; letter-spacing:0.08em;
                        text-transform:uppercase; color:{COLOR_TEXT_MUTED};
                        margin-bottom:4px;">Análisis de votaciones</div>
            <div class="section-header" style="margin-bottom:4px;">
                Votos a favor por ley</div>
            <div class="section-subheader">
                % de congresistas postulantes que votaron a favor · agrupado por bloque temático
            </div>""",
        unsafe_allow_html=True,
    )

    # Calcular % A FAVOR por ley
    # Los colores por bloque vienen del config centralizado (COLOR_BLOQUE)
    # para que cualquier cambio de paleta se propague desde un solo lugar.
    resultados = []
    for col in LEYES_COLS:
        if col not in votos.columns:
            continue
        total_validos = votos[col].isin(["A FAVOR", "EN CONTRA", "ABSTENCION"]).sum()
        a_favor = (votos[col] == "A FAVOR").sum()
        pct = round(a_favor / total_validos * 100, 1) if total_validos > 0 else 0

        clave_match = leyes_df[leyes_df["etiqueta"] == col]
        bloque = clave_match["bloque"].values[0] if len(clave_match) > 0 else "otro"

        resultados.append({
            "ley":        col.split(" ", 1)[1] if " " in col else col,
            "a_favor_pct": pct,
            "bloque":     bloque,
            "n_favor":    int(a_favor),
            "clave":      col.split(" ")[0],
        })

    res_df = pd.DataFrame(resultados).sort_values("a_favor_pct", ascending=True)
    colores_bloque = {**COLOR_BLOQUE, "otro": COLOR_RIESGO_NONE}
    res_df["color"] = res_df["bloque"].map(colores_bloque).fillna(COLOR_RIESGO_NONE)
    res_df["pct_label"] = res_df["a_favor_pct"].apply(lambda x: f"{x:.0f}%")

    # Margen izquierdo dinámico según nombre de ley más largo
    max_chars_leyes = res_df["ley"].str.len().max()
    margen_leyes = min(int(max_chars_leyes * 6.2), 260)

    altura_leyes = max(380, len(res_df) * 34 + 40)

    fig_leyes = go.Figure()
    for bloque_nombre, grupo in res_df.groupby("bloque"):
        color_b = colores_bloque.get(bloque_nombre, COLOR_RIESGO_NONE)
        fig_leyes.add_trace(go.Bar(
            x=grupo["a_favor_pct"],
            y=grupo["ley"],
            orientation="h",
            name=bloque_nombre.capitalize(),
            marker_color=color_b,
            text=grupo["pct_label"],
            textposition="outside",
            textfont=dict(size=11, color=COLOR_TEXT_PRIMARY,
                          family="'Plus Jakarta Sans', system-ui, sans-serif"),
            customdata=grupo[["n_favor", "clave"]].values,
            hovertemplate=(
                "<b>%{customdata[1]}</b> %{y}<br>"
                "%{x:.1f}% a favor · %{customdata[0]} congresistas<extra></extra>"
            ),
            cliponaxis=False,
        ))

    fig_leyes.update_layout(
        height=altura_leyes,
        margin=dict(l=margen_leyes, r=52, t=4, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        barmode="overlay",
        font=dict(family="'Plus Jakarta Sans', system-ui, sans-serif",
                  size=11, color=COLOR_TEXT_PRIMARY),
        legend=dict(
            orientation="h",
            y=-0.06, x=0,
            font=dict(size=10),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            visible=False,
            showgrid=False,
            zeroline=False,
            range=[0, 115],
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=10, color=COLOR_TEXT_SECONDARY),
            automargin=False,
        ),
    )
    st.plotly_chart(fig_leyes, use_container_width=True)

with col_reinfo_viz:
    st.markdown(
        f"""<div style="font-size:0.75rem; font-weight:700; letter-spacing:0.08em;
                        text-transform:uppercase; color:{COLOR_TEXT_MUTED};
                        margin-bottom:4px;">Minería informal</div>
            <div class="section-header" style="margin-bottom:4px;">
                Vínculos REINFO</div>
            <div class="section-subheader">
                Candidatos con derechos mineros registrados · top departamentos
            </div>""",
        unsafe_allow_html=True,
    )

    dptos = (
        reinfo["dptos_mineros"].str.split(";").explode()
        .str.strip().value_counts()
        .reset_index()
    )
    dptos.columns = ["departamento", "candidatos"]
    dptos = dptos.head(10).sort_values("candidatos", ascending=True)

    max_chars_dptos = dptos["departamento"].str.len().max()
    margen_reinfo = min(int(max_chars_dptos * 6.5), 180)

    altura_reinfo = max(260, len(dptos) * 34 + 20)

    fig_reinfo = go.Figure()
    fig_reinfo.add_trace(go.Bar(
        x=dptos["candidatos"],
        y=dptos["departamento"],
        orientation="h",
        marker_color=COLOR_REINFO,
        text=dptos["candidatos"],
        textposition="outside",
        textfont=dict(size=11, color=COLOR_TEXT_PRIMARY,
                      family="'Plus Jakarta Sans', system-ui, sans-serif"),
        hovertemplate="<b>%{y}</b><br>%{x} candidatos con REINFO<extra></extra>",
        cliponaxis=False,
    ))
    fig_reinfo.update_layout(
        height=altura_reinfo,
        margin=dict(l=margen_reinfo, r=40, t=4, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        font=dict(family="'Plus Jakarta Sans', system-ui, sans-serif",
                  size=11, color=COLOR_TEXT_PRIMARY),
        xaxis=dict(
            visible=False,
            showgrid=False,
            zeroline=False,
            range=[0, dptos["candidatos"].max() * 1.3],
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=10.5, color=COLOR_TEXT_SECONDARY),
            automargin=False,
        ),
    )
    st.plotly_chart(fig_reinfo, use_container_width=True)


st.markdown(
    f'<div style="border-top:1px solid {COLOR_BORDER}; margin:24px 0;"></div>',
    unsafe_allow_html=True,
)

# -------------------------------------------------------
# SECTION: KPIs analíticos — leyes clave
#
# Leyes seleccionadas por relevancia para el proyecto:
#   - 4 pro-crimen de mayor impacto (las más votadas a favor)
#   - APCI (espacio cívico)
#   - REINFO 5a ampliación (la más reciente)
#   - Bicameralidad (reforma institucional)
#
# Se calcula % de congresistas postulantes que votaron A FAVOR
# sobre el total que emitió voto válido (A FAVOR + EN CONTRA + ABSTENCIÓN).
# -------------------------------------------------------
st.markdown(
    f"""
    <div style="margin-bottom:20px;">
        <div style="font-size:0.63rem; font-weight:700; letter-spacing:0.12em;
                    text-transform:uppercase; color:{COLOR_ACCENT}; margin-bottom:6px;">
            Leyes clave · votos a favor
        </div>
        <div class="section-header" style="margin-bottom:2px;">
            ¿Cuántos congresistas postulantes votaron a favor?
        </div>
        <div class="section-subheader">
            % sobre votos válidos (A favor + En contra + Abstención) · congresistas en ejercicio que postulan en 2026
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Definición de leyes a destacar: (clave_col, etiqueta_corta, bloque, color)
LEYES_DESTACADAS = [
    ("L31751 Prescripción 1 año",                                          "Prescripción 1 año",         "pro-crimen",     COLOR_RIESGO_ALTO),
    ("L31989 Elimina incautación",                                         "Elimina incautación",        "pro-crimen",     COLOR_RIESGO_ALTO),
    ("L31990 Limita colaboración eficaz",                                  "Limita colaboración eficaz", "pro-crimen",     COLOR_RIESGO_ALTO),
    ("L32181 Elimina detención preliminar",                                "Elimina detención prelim.",  "pro-crimen",     COLOR_RIESGO_ALTO),
    ("L32301 Ley APCI",                                                    "Ley APCI",                   "espacio-civico", "#6B4FA0"),
    ("L32537 REINFO 5a amp",                                               "REINFO 5ª ampliación",       "reinfo",         COLOR_REINFO),
    ("L31988 Bicameralidad",                                               "Bicameralidad",              "bicameralidad",  COLOR_ACCENT),
]

def pct_a_favor(col_name):
    """% de votos A FAVOR sobre votos válidos para una columna de ley."""
    if col_name not in votos.columns:
        return None, None
    validos = votos[col_name].isin(["A FAVOR", "EN CONTRA", "ABSTENCION"]).sum()
    n_favor = (votos[col_name] == "A FAVOR").sum()
    pct = round(n_favor / validos * 100) if validos > 0 else 0
    return pct, int(n_favor)

# Renderizar en filas de 4 columnas
cols_por_fila = 4
for fila_inicio in range(0, len(LEYES_DESTACADAS), cols_por_fila):
    fila = LEYES_DESTACADAS[fila_inicio : fila_inicio + cols_por_fila]
    cols = st.columns(len(fila), gap="small")
    for col_widget, (clave, etiqueta, bloque, color) in zip(cols, fila):
        pct, n = pct_a_favor(clave)
        if pct is None:
            continue
        # Barra de progreso visual inline
        with col_widget:
            st.markdown(
                f"""
                <div style="background:{COLOR_SURFACE}; border:1px solid {COLOR_BORDER};
                            border-top:3px solid {color};
                            border-radius:0 0 6px 6px;
                            padding:14px 16px 12px 16px;">
                    <div style="font-size:0.60rem; font-weight:700; letter-spacing:0.08em;
                                text-transform:uppercase; color:{COLOR_TEXT_MUTED};
                                margin-bottom:6px; line-height:1.3;">
                        {bloque}
                    </div>
                    <div style="font-size:1.75rem; font-weight:700; color:{color};
                                font-variant-numeric:tabular-nums;
                                letter-spacing:-0.02em; line-height:1;">
                        {pct}%
                    </div>
                    <div style="font-size:0.78rem; font-weight:600;
                                color:{COLOR_TEXT_PRIMARY}; margin:4px 0 2px 0;
                                line-height:1.3;">
                        {etiqueta}
                    </div>
                    <div style="font-size:0.70rem; color:{COLOR_TEXT_MUTED};">
                        {n} de {len(votos)} votaron a favor
                    </div>
                    <div style="margin-top:8px; background:{COLOR_BORDER};
                                border-radius:2px; height:4px; overflow:hidden;">
                        <div style="background:{color}; width:{pct}%;
                                    height:4px; border-radius:2px;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# -------------------------------------------------------
# SECTION: Footer
# -------------------------------------------------------
st.markdown(
    f"""
    <div class="page-footer">
        <span>{APP_CONFIDENTIAL_LABEL} · {APP_VERSION}</span>
        <span>Fuentes: JNE · REINFO · Congreso del Perú · porEstosNo.pe</span>
    </div>
    """,
    unsafe_allow_html=True,
)
