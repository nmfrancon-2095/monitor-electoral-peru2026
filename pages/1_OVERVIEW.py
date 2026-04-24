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

# Fuentes forenses (v3.0)
FONT_SERIF = "'Source Serif 4', Georgia, 'Times New Roman', serif"
FONT_SANS  = "'DM Sans', system-ui, -apple-system, sans-serif"

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
    <div class="masthead">
      <div class="masthead-title">
        {APP_TITLE} <em>· Resumen ejecutivo</em>
      </div>
      <div class="masthead-meta">
        <span class="pill red">{APP_CONFIDENTIAL_LABEL}</span>
        <span>{APP_VERSION}</span>
      </div>
    </div>

    <div class="page-title-wrap">
      <div class="page-eyebrow" style="font-size:0.62rem;font-weight:700;
           letter-spacing:0.18em;text-transform:uppercase;
           color:{COLOR_TEXT_SECONDARY};margin-bottom:8px;">
        OVERVIEW · PANORAMA GENERAL
      </div>
      <h1 class="page-title" style="font-size:2.4rem;margin:0 0 6px 0;
           color:{COLOR_TEXT_PRIMARY};">
        Integridad electoral y riesgos institucionales
      </h1>
      <div class="page-title-light" style="font-size:1.05rem;color:{COLOR_TEXT_SECONDARY};
           font-style:italic;">
        {APP_SUBTITLE} · JNE · REINFO · Congreso del Perú
      </div>
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
        <div style="background:{COLOR_SURFACE};border:1px solid {COLOR_BORDER};
                    border-top:3px solid {COLOR_PRIMARY};border-radius:2px;
                    padding:24px 28px 22px 28px;height:100%;">
            <div style="font-size:0.62rem;font-weight:700;letter-spacing:0.14em;
                        text-transform:uppercase;color:{COLOR_GOLD};
                        margin-bottom:10px;">
                Total · Candidatos inscritos
            </div>
            <div style="font-family:{FONT_SERIF};font-size:4rem;font-weight:500;
                        color:{COLOR_TEXT_PRIMARY};font-variant-numeric:tabular-nums;
                        letter-spacing:-0.03em;line-height:0.95;">
                {kpis['total_candidatos']:,}
            </div>
            <div style="width:42px;height:2px;background:{COLOR_GOLD};
                        margin:14px 0 10px 0;"></div>
            <div style="font-size:0.88rem;color:{COLOR_TEXT_SECONDARY};
                        line-height:1.5;max-width:380px;">
                Candidatos inscritos ante el JNE para las Elecciones Generales 2026.
                Universo total sobre el que se construye el monitoreo.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Helper para las 4 KPIs secundarias
def kpi_secundaria(label, valor, nota, color_rule=None):
    rule = color_rule or COLOR_PRIMARY
    val_color = color_rule or COLOR_TEXT_PRIMARY
    return f"""
        <div style="background:{COLOR_SURFACE};border:1px solid {COLOR_BORDER};
                    border-top:3px solid {rule};border-radius:2px;
                    padding:18px 18px 16px 18px;height:100%;">
            <div style="font-size:0.58rem;font-weight:700;letter-spacing:0.12em;
                        text-transform:uppercase;color:{COLOR_TEXT_MUTED};
                        margin-bottom:8px;line-height:1.3;">
                {label}
            </div>
            <div style="font-family:{FONT_SERIF};font-size:2.4rem;font-weight:500;
                        color:{val_color};font-variant-numeric:tabular-nums;
                        letter-spacing:-0.02em;line-height:1;">
                {valor}
            </div>
            <div style="font-size:0.72rem;color:{COLOR_TEXT_SECONDARY};
                        margin-top:6px;line-height:1.4;">
                {nota}
            </div>
        </div>"""

with k1:
    st.markdown(kpi_secundaria(
        "Congresistas postulando",
        kpis["congresistas_postulando"],
        "En ejercicio · postulan en 2026",
        color_rule=COLOR_PRIMARY,
    ), unsafe_allow_html=True)

with k2:
    st.markdown(kpi_secundaria(
        "Vínculo REINFO",
        kpis["con_reinfo"],
        "Candidatos con derechos mineros",
        color_rule=COLOR_REINFO,
    ), unsafe_allow_html=True)

with k3:
    st.markdown(kpi_secundaria(
        "Riesgo alto",
        kpis["riesgo_alto"],
        f"Score ≥ {SCORE_ALTO_MIN} · congresistas",
        color_rule=COLOR_RIESGO_ALTO,
    ), unsafe_allow_html=True)

st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

# -------------------------------------------------------
# SECTION: Fila principal — Mapa + Panel de riesgo
# -------------------------------------------------------
col_mapa, col_riesgo = st.columns([3, 2], gap="large")

# ---- Helper: section header forensic ----
def section_header(eyebrow, title, sub):
    return f"""
        <div style="margin-bottom:14px;">
            <div style="font-size:0.60rem;font-weight:700;letter-spacing:0.14em;
                        text-transform:uppercase;color:{COLOR_GOLD};
                        margin-bottom:4px;">{eyebrow}</div>
            <div style="font-family:{FONT_SERIF};font-size:1.4rem;font-weight:500;
                        color:{COLOR_TEXT_PRIMARY};letter-spacing:-0.01em;
                        line-height:1.2;margin-bottom:4px;">{title}</div>
            <div style="font-size:0.82rem;color:{COLOR_TEXT_SECONDARY};
                        font-style:italic;line-height:1.45;">{sub}</div>
        </div>"""

# --- Mapa de burbujas ---
with col_mapa:
    st.markdown(section_header(
        "DISTRIBUCIÓN GEOGRÁFICA",
        "Candidatos por región",
        "Regiones prioritarias destacadas · tamaño proporcional al número de candidatos",
    ), unsafe_allow_html=True)

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
            "Estándar":    COLOR_PRIMARY,
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
        size_max=38, zoom=4,
        center={"lat": -9.19, "lon": -75.0},
        mapbox_style="carto-positron",
        height=CHART_HEIGHT,
    )
    fig_mapa.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=COLOR_SURFACE,
        font=dict(family=FONT_SANS, size=11, color=COLOR_TEXT_PRIMARY),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=0.01,
            xanchor="right", x=0.99,
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor=COLOR_BORDER,
            borderwidth=1,
            font=dict(family=FONT_SANS, size=11, color=COLOR_TEXT_SECONDARY),
        ),
    )
    # Card wrapper con regla navy superior
    st.markdown(
        f"""<div style="background:{COLOR_SURFACE};border:1px solid {COLOR_BORDER};
                       border-top:3px solid {COLOR_PRIMARY};border-radius:2px;
                       padding:2px;">""",
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig_mapa, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Panel de riesgo (congresistas) ---
with col_riesgo:
    st.markdown(section_header(
        "CONGRESISTAS POSTULANTES",
        "Niveles de riesgo",
        "89 congresistas en ejercicio que postulan en 2026",
    ), unsafe_allow_html=True)

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

    total_congs = len(votos)
    rc_dict = dict(zip(riesgo_counts["nivel"], riesgo_counts["cantidad"]))

    niveles_display = [
        ("alto",  "Riesgo alto",   COLOR_RIESGO_ALTO,  COLOR_RIESGO_ALTO_BG),
        ("medio", "Riesgo medio",  COLOR_RIESGO_MEDIO, COLOR_RIESGO_MEDIO_BG),
        ("bajo",  "Riesgo bajo",   COLOR_RIESGO_BAJO,  COLOR_RIESGO_BAJO_BG),
        ("none",  "Sin dato",      COLOR_RIESGO_NONE,  COLOR_RIESGO_NONE_BG),
    ]

    for nivel, label, color, bg in niveles_display:
        n = rc_dict.get(nivel, 0)
        pct = round(n / total_congs * 100) if total_congs > 0 else 0
        st.markdown(
            f"""
            <div style="background:{COLOR_SURFACE};border:1px solid {COLOR_BORDER};
                        border-left:4px solid {color};border-radius:0 2px 2px 0;
                        padding:12px 16px;margin-bottom:8px;
                        display:flex;justify-content:space-between;
                        align-items:center;">
                <div>
                    <div style="font-size:0.68rem;font-weight:700;
                                letter-spacing:0.10em;text-transform:uppercase;
                                color:{color};">
                        {label}
                    </div>
                    <div style="font-size:0.74rem;color:{COLOR_TEXT_SECONDARY};
                                margin-top:2px;">
                        {pct}% de los congresistas postulantes
                    </div>
                </div>
                <div style="font-family:{FONT_SERIF};font-size:2rem;font-weight:500;
                            color:{color};font-variant-numeric:tabular-nums;
                            letter-spacing:-0.02em;line-height:1;">
                    {n}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # Partidos con riesgo alto — ahora usando color_partido() dinámico
    st.markdown(
        f"""<div style="font-family:{FONT_SERIF};font-size:1rem;font-weight:500;
                    color:{COLOR_TEXT_PRIMARY};margin-bottom:2px;
                    letter-spacing:-0.01em;">
                Partidos · congresistas de riesgo alto
            </div>
            <div style="font-size:0.75rem;color:{COLOR_TEXT_SECONDARY};
                    font-style:italic;margin-bottom:10px;">
                Top 8 por concentración
            </div>""",
        unsafe_allow_html=True,
    )

    riesgo_partido = (
        votos[votos["nivel_riesgo"] == "alto"]
        .groupby("partido").size()
        .reset_index(name="n")
        .sort_values("n", ascending=True)
        .tail(8)
    )
    riesgo_partido["partido_label"] = riesgo_partido["partido"].str.upper()
    # Color dinámico por partido desde config (v3.0)
    riesgo_partido["color"] = riesgo_partido["partido"].apply(color_partido)

    max_chars = riesgo_partido["partido_label"].str.len().max()
    margen_izq = min(int(max_chars * 6.5), 280)
    altura_partidos = max(240, len(riesgo_partido) * 42 + 20)

    fig_partidos = go.Figure()
    fig_partidos.add_trace(go.Bar(
        x=riesgo_partido["n"],
        y=riesgo_partido["partido_label"],
        orientation="h",
        marker=dict(
            color=riesgo_partido["color"].tolist(),
            line=dict(width=0),
        ),
        text=riesgo_partido["n"],
        textposition="outside",
        textfont=dict(family=FONT_SERIF, size=13, color=COLOR_TEXT_PRIMARY),
        hovertemplate="<b>%{y}</b><br>%{x} congresistas riesgo alto<extra></extra>",
        cliponaxis=False,
    ))
    try:
        fig_partidos.update_traces(marker_cornerradius=BAR_CORNER_RADIUS)
    except Exception:
        pass

    fig_partidos.update_layout(
        height=altura_partidos,
        margin=dict(l=margen_izq, r=48, t=4, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        font=dict(family=FONT_SANS, size=11, color=COLOR_TEXT_PRIMARY),
        xaxis=dict(
            visible=False, showgrid=False, zeroline=False,
            range=[0, riesgo_partido["n"].max() * 1.28],
        ),
        yaxis=dict(
            showgrid=False, zeroline=False,
            tickfont=dict(family=FONT_SANS, size=10.5, color=COLOR_TEXT_SECONDARY),
            automargin=False,
        ),
    )
    st.plotly_chart(fig_partidos, use_container_width=True)

# Separador editorial (oro + navy)
st.markdown(
    f"""<div style="margin:32px 0 28px 0;display:flex;align-items:center;gap:12px;">
          <div style="flex:1;height:1px;background:{COLOR_BORDER};"></div>
          <div style="width:6px;height:6px;background:{COLOR_GOLD};
                      transform:rotate(45deg);"></div>
          <div style="flex:1;height:1px;background:{COLOR_BORDER};"></div>
       </div>""",
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
    <div style="margin-bottom:22px;">
        <div style="font-size:0.60rem;font-weight:700;letter-spacing:0.14em;
                    text-transform:uppercase;color:{COLOR_GOLD};
                    margin-bottom:6px;">
            LEYES CLAVE · VOTOS A FAVOR
        </div>
        <div style="font-family:{FONT_SERIF};font-size:1.6rem;font-weight:500;
                    color:{COLOR_TEXT_PRIMARY};letter-spacing:-0.015em;
                    line-height:1.2;margin-bottom:4px;">
            ¿Cuántos congresistas postulantes votaron a favor?
        </div>
        <div style="font-size:0.88rem;color:{COLOR_TEXT_SECONDARY};
                    font-style:italic;line-height:1.5;max-width:760px;">
            % sobre votos válidos (A favor + En contra + Abstención) · congresistas
            en ejercicio que postulan en 2026.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

LEYES_DESTACADAS = [
    ("L31751 Prescripción 1 año",           "Prescripción 1 año",         "pro-crimen",     COLOR_RIESGO_ALTO),
    ("L31989 Elimina incautación",          "Elimina incautación",        "pro-crimen",     COLOR_RIESGO_ALTO),
    ("L31990 Limita colaboración eficaz",   "Limita colaboración eficaz", "pro-crimen",     COLOR_RIESGO_ALTO),
    ("L32181 Elimina detención preliminar", "Elimina detención prelim.",  "pro-crimen",     COLOR_RIESGO_ALTO),
    ("L32301 Ley APCI",                     "Ley APCI",                   "espacio-civico", COLOR_BLOQUE.get("espacio-civico", COLOR_ACCENT)),
    ("L32537 REINFO 5a amp",                "REINFO 5ª ampliación",       "reinfo",         COLOR_REINFO),
    ("L31988 Bicameralidad",                "Bicameralidad",              "bicameralidad",  COLOR_PRIMARY),
]

def pct_a_favor(col_name):
    if col_name not in votos.columns:
        return None, None
    validos = votos[col_name].isin(["A FAVOR", "EN CONTRA", "ABSTENCION"]).sum()
    n_favor = (votos[col_name] == "A FAVOR").sum()
    pct = round(n_favor / validos * 100) if validos > 0 else 0
    return pct, int(n_favor)

cols_por_fila = 4
for fila_inicio in range(0, len(LEYES_DESTACADAS), cols_por_fila):
    fila = LEYES_DESTACADAS[fila_inicio : fila_inicio + cols_por_fila]
    cols = st.columns(len(fila), gap="small")
    for col_widget, (clave, etiqueta, bloque, color) in zip(cols, fila):
        pct, n = pct_a_favor(clave)
        if pct is None:
            continue
        with col_widget:
            st.markdown(
                f"""
                <div style="background:{COLOR_SURFACE};border:1px solid {COLOR_BORDER};
                            border-top:3px solid {color};border-radius:2px;
                            padding:16px 18px 14px 18px;height:100%;">
                    <div style="font-size:0.56rem;font-weight:700;letter-spacing:0.12em;
                                text-transform:uppercase;color:{color};
                                margin-bottom:8px;line-height:1.3;">
                        {bloque}
                    </div>
                    <div style="font-family:{FONT_SERIF};font-size:2rem;font-weight:500;
                                color:{color};font-variant-numeric:tabular-nums;
                                letter-spacing:-0.02em;line-height:1;">
                        {pct}%
                    </div>
                    <div style="font-size:0.82rem;font-weight:600;
                                color:{COLOR_TEXT_PRIMARY};margin:6px 0 2px 0;
                                line-height:1.35;">
                        {etiqueta}
                    </div>
                    <div style="font-size:0.70rem;color:{COLOR_TEXT_MUTED};
                                font-style:italic;">
                        {n} de {len(votos)} votaron a favor
                    </div>
                    <div style="margin-top:10px;background:{COLOR_BORDER_SOFT};
                                border-radius:0;height:3px;overflow:hidden;">
                        <div style="background:{color};width:{pct}%;
                                    height:3px;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# -------------------------------------------------------
# SECTION: Footer
# -------------------------------------------------------
st.markdown(
    f"""
    <div class="page-footer" style="margin-top:48px;padding-top:14px;
         border-top:1px solid {COLOR_BORDER};display:flex;
         justify-content:space-between;font-size:0.70rem;color:{COLOR_TEXT_MUTED};
         letter-spacing:0.04em;">
        <span>{APP_CONFIDENTIAL_LABEL} · {APP_VERSION}</span>
        <span>Fuentes: JNE · REINFO · Congreso del Perú · porEstosNo.pe</span>
    </div>
    """,
    unsafe_allow_html=True,
)
