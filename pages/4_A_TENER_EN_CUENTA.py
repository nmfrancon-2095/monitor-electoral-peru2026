# ============================================================
# pages/4_a_tener_en_cuenta.py — Monitor Electoral Perú 2026
# Subvistas en tres tabs:
#   1. Con REINFO — candidatos con derechos mineros registrados
#   2. Congresistas postulando — cruce votación + candidatura
#   3. Presidenciables — con detalle modal por candidato
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

from config import (
    APP_TITLE, APP_ICON, APP_CONFIDENTIAL_LABEL,
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_BACKGROUND, COLOR_SURFACE,
    COLOR_BORDER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_RIESGO_ALTO, COLOR_RIESGO_ALTO_BG,
    COLOR_RIESGO_MEDIO, COLOR_RIESGO_MEDIO_BG,
    COLOR_RIESGO_BAJO, COLOR_RIESGO_BAJO_BG,
    COLOR_RIESGO_NONE, COLOR_RIESGO_NONE_BG,
    COLOR_REINFO, COLOR_REINFO_BG,
    LABEL_RIESGO, LEYES_COLS, REGIONES_PRIORITARIAS, GLOBAL_CSS
)
from data_loader import (
    cargar_candidatos, cargar_votaciones, cargar_reinfo, cargar_leyes,
    normalizar_dni
)

# -------------------------------------------------------
# SECTION: Configuración visual
# -------------------------------------------------------
CHART_HEIGHT_MAIN   = 460   # scatter principal
CHART_HEIGHT_BAR    = 320   # barras secundarias
SCATTER_MARKER_SIZE = 10    # tamaño de puntos en strip plot
SCATTER_JITTER      = 0.4   # separación horizontal entre puntos

COLOR_NIVEL = {
    "alto":  COLOR_RIESGO_ALTO,
    "medio": COLOR_RIESGO_MEDIO,
    "bajo":  COLOR_RIESGO_BAJO,
    "none":  COLOR_RIESGO_NONE,
}
COLOR_NIVEL_BG = {
    "alto":  COLOR_RIESGO_ALTO_BG,
    "medio": COLOR_RIESGO_MEDIO_BG,
    "bajo":  COLOR_RIESGO_BAJO_BG,
    "none":  COLOR_RIESGO_NONE_BG,
}

TRANSPARENT = "rgba(0,0,0,0)"  # fondo transparente para todos los gráficos

# CSS adicional para el modal de presidenciables
MODAL_CSS = f"""
<style>
.modal-overlay {{
    display: none;
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0,0,0,0.45);
    z-index: 9999;
    justify-content: center;
    align-items: center;
}}
.modal-overlay.visible {{
    display: flex;
}}
.modal-box {{
    background: {COLOR_SURFACE};
    border-radius: 12px;
    padding: 28px 32px;
    max-width: 560px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 24px 64px rgba(0,0,0,0.22);
    position: relative;
    animation: modalIn 0.22s ease;
}}
@keyframes modalIn {{
    from {{ opacity: 0; transform: translateY(16px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.modal-close {{
    position: absolute;
    top: 14px; right: 18px;
    font-size: 1.3em;
    cursor: pointer;
    color: {COLOR_TEXT_SECONDARY};
    border: none;
    background: none;
    line-height: 1;
}}
.modal-close:hover {{ color: {COLOR_TEXT_PRIMARY}; }}
.modal-score-badge {{
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.82em;
    font-weight: 700;
    margin-top: 6px;
}}
.modal-row {{
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid {COLOR_BORDER};
    font-size: 0.87em;
}}
.modal-row:last-child {{ border-bottom: none; }}
.modal-label {{ color: {COLOR_TEXT_SECONDARY}; }}
.modal-value {{ color: {COLOR_TEXT_PRIMARY}; font-weight: 500; text-align: right; max-width: 60%; }}
.modal-section-title {{
    font-size: 0.78em;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: {COLOR_TEXT_SECONDARY};
    margin: 16px 0 8px 0;
}}
.nota-card {{
    background: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 12px 16px;
    margin-bottom: 16px;
    font-size: 0.87em;
    line-height: 1.55;
}}
.kpi-sublabel {{
    font-size: 0.75em;
    color: {COLOR_TEXT_SECONDARY};
    margin-top: 2px;
}}
</style>
"""

# -------------------------------------------------------
# SECTION: Page setup
# -------------------------------------------------------
st.set_page_config(
    page_title=f"A tener en cuenta · {APP_TITLE}",
    page_icon=APP_ICON,
    layout="wide",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown(MODAL_CSS, unsafe_allow_html=True)

if not st.session_state.get("autenticado", False):
    st.warning("Debes iniciar sesión primero.")
    st.stop()

# -------------------------------------------------------
# SECTION: Cargar datos
# -------------------------------------------------------
with st.spinner("Cargando datos..."):
    cands    = cargar_candidatos()
    votos    = cargar_votaciones()
    reinfo   = cargar_reinfo()
    leyes_df = cargar_leyes()

# -------------------------------------------------------
# SECTION: Preparar subconjuntos de datos
# -------------------------------------------------------

def nivel(s):
    """Asigna nivel de riesgo según score total."""
    if pd.isna(s): return "none"
    if s >= 20:    return "alto"
    if s >= 10:    return "medio"
    return "bajo"

votos["nivel_riesgo"]    = votos["score_total"].apply(nivel)
votos["etiqueta_riesgo"] = votos["nivel_riesgo"].map(LABEL_RIESGO)

# REINFO enriquecido con candidatura 2026
reinfo_enrich = reinfo.merge(
    cands[["dni", "tipo_eleccion", "region", "partido", "estado_jne", "expediente"]],
    on="dni", how="left", suffixes=("", "_cand")
)
reinfo_enrich = reinfo_enrich.merge(
    votos[["dni", "score_total", "nivel_riesgo", "etiqueta_riesgo"]],
    on="dni", how="left"
)
reinfo_enrich["nivel_riesgo"]    = reinfo_enrich["nivel_riesgo"].fillna("none")
reinfo_enrich["etiqueta_riesgo"] = reinfo_enrich["etiqueta_riesgo"].fillna(LABEL_RIESGO["none"])
reinfo_enrich["tiene_score"]     = reinfo_enrich["score_total"].notna()

# Presidenciables
pres = cands[cands["tipo_eleccion"] == "PRESIDENCIAL"].copy()
pres = pres.merge(
    votos[["dni", "score_total", "nivel_riesgo", "etiqueta_riesgo",
           "grupo_parl", "score_procrimen", "bonus_autoria", "leyes_autoria"]],
    on="dni", how="left"
)
pres["nivel_riesgo"]    = pres["nivel_riesgo"].fillna("none")
pres["etiqueta_riesgo"] = pres["etiqueta_riesgo"].fillna(LABEL_RIESGO["none"])
pres["es_congresista"]  = pres["score_total"].notna()
pres["url_jne"]         = pres["url_jne"].fillna("") if "url_jne" in pres.columns else ""

pres["cargo_corto"] = pres["cargo"].str.replace(
    "PRIMER VICEPRESIDENTE DE LA REPÚBLICA", "1er Vicepresidente", regex=False
).str.replace(
    "SEGUNDO VICEPRESIDENTE DE LA REPÚBLICA", "2do Vicepresidente", regex=False
).str.replace(
    "PRESIDENTE DE LA REPÚBLICA", "Presidente", regex=False
)

solo_pres  = pres[pres["cargo_corto"] == "Presidente"].copy()
formulas   = pres.copy()

# -------------------------------------------------------
# SECTION: Header
# -------------------------------------------------------
_html_header_atec = (
    '<div style="margin-bottom:24px;">'
    '<p style="font-size:0.68rem;font-weight:700;letter-spacing:0.12em;'
    'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 4px 0;">'
    'Monitor Electoral Per\u00fa 2026</p>'
    '<h2 style="color:' + COLOR_TEXT_PRIMARY + ';margin:0 0 4px 0;'
    'font-size:1.55rem;font-weight:700;letter-spacing:-0.02em;">'
    '\U0001f4cc A tener en cuenta</h2>'
    '<p style="color:' + COLOR_TEXT_SECONDARY + ';font-size:0.85em;margin:0;">'
    'Cruces entre candidatura 2026, registro REINFO y votaciones legislativas</p>'
    '</div>'
)

# -------------------------------------------------------
# SECTION: KPIs — helper + render
# -------------------------------------------------------
def _kpi_card_atec(label, value, sub, bg, border, color):
    """Card KPI individual — mismo patrón que 3_congresistas."""
    return (
        '<div style="background:' + bg + ';border:1px solid ' + border + ';'
        'border-radius:8px;padding:18px;">'
        '<p style="font-size:0.65rem;font-weight:700;letter-spacing:0.10em;'
        'text-transform:uppercase;color:' + color + ';margin:0 0 8px 0;opacity:0.8;">'
        + label + '</p>'
        '<p style="font-size:2.2rem;font-weight:700;color:' + color + ';'
        'margin:0;line-height:1;font-variant-numeric:tabular-nums;">'
        + str(value) + '</p>'
        '<p style="font-size:0.72rem;color:' + color + ';margin:6px 0 0 0;opacity:0.6;">'
        + sub + '</p>'
        '</div>'
    )

n_reinfo_kpi  = len(reinfo_enrich)
n_congs_kpi   = len(votos)
alto_count_kpi = int((votos["nivel_riesgo"] == "alto").sum())
n_pres_kpi    = len(solo_pres)
ex_cong_kpi   = int(pres["es_congresista"].sum())

_html_kpis_atec = (
    '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:24px;">'
    + _kpi_card_atec(
        "\u26cf\ufe0f Con v\u00ednculo REINFO",
        n_reinfo_kpi,
        "Pendiente verificaci\u00f3n manual",
        COLOR_REINFO_BG, "#E8C8A8", COLOR_REINFO,
    )
    + _kpi_card_atec(
        "\U0001f3db\ufe0f Congresistas postulando",
        n_congs_kpi,
        str(alto_count_kpi) + " con riesgo alto (score \u2265 20)",
        COLOR_RIESGO_ALTO_BG, "#EEC8C8", COLOR_RIESGO_ALTO,
    )
    + _kpi_card_atec(
        "\U0001f5f3\ufe0f Candidatos a la Presidencia",
        n_pres_kpi,
        str(ex_cong_kpi) + " son congresistas en ejercicio",
        COLOR_SURFACE, COLOR_BORDER, COLOR_TEXT_SECONDARY,
    )
    + '</div>'
)

st.markdown(_html_header_atec + _html_kpis_atec, unsafe_allow_html=True)

# -------------------------------------------------------
# SECTION: Tres tabs
# -------------------------------------------------------
tab_reinfo, tab_congs, tab_pres = st.tabs([
    f"⛏️ Con REINFO ({len(reinfo_enrich)})",
    f"🏛️ Congresistas postulando ({len(votos)})",
    f"📋 Presidenciables ({len(solo_pres)})",
])


# ===================================================
# TAB 1 — CON REINFO
# ===================================================
with tab_reinfo:
    st.markdown(
        f"""
        <div class="nota-card" style="border-left: 4px solid {COLOR_REINFO};">
            <b>Nota metodológica:</b> Los vínculos REINFO fueron identificados mediante
            cruce de nombres entre el padrón JNE y el registro REINFO del Ministerio
            de Energía y Minas. Todos los matches son de tipo
            <code>MATCH_NOMBRE_verificar</code> y requieren verificación manual.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Filtros
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        busq_reinfo = st.text_input("Buscar nombre", key="busq_reinfo",
                                     placeholder="Ej: Mamani...")
    with col_f2:
        prio_opts = ["Todos", "Solo regiones prioritarias", "Fuera de regiones prioritarias"]
        prio_sel  = st.selectbox("Región prioritaria", prio_opts, key="prio_reinfo")
    with col_f3:
        cargo_opts = ["Todos"] + sorted(reinfo_enrich["cargo"].dropna().unique().tolist())
        cargo_sel  = st.selectbox("Cargo postulado", cargo_opts, key="cargo_reinfo")

    # Aplicar filtros
    df_r = reinfo_enrich.copy()
    if busq_reinfo:
        df_r = df_r[df_r["nombre_completo"].str.upper().str.contains(
            busq_reinfo.upper(), na=False)]
    if prio_sel == "Solo regiones prioritarias":
        df_r = df_r[df_r["es_region_prioritaria"] == "SÍ"]
    elif prio_sel == "Fuera de regiones prioritarias":
        df_r = df_r[df_r["es_region_prioritaria"] != "SÍ"]
    if cargo_sel != "Todos":
        df_r = df_r[df_r["cargo"] == cargo_sel]

    col_c, col_d = st.columns([3, 1])
    with col_c:
        st.markdown(
            f"<p style='color:{COLOR_TEXT_SECONDARY}; font-size:0.88em;'>"
            f"Mostrando <b>{len(df_r)}</b> registros</p>",
            unsafe_allow_html=True,
        )
    with col_d:
        st.download_button(
            "⬇️ Descargar (CSV)",
            data=df_r[[
                "dni","nombre_completo","partido","cargo","tipo_eleccion",
                "dptos_mineros","n_derechos_mineros","estado_reinfo_cons",
                "es_region_prioritaria","score_total","nivel_riesgo"
            ]].to_csv(index=False).encode("utf-8"),
            file_name="reinfo_filtrado.csv", mime="text/csv",
            use_container_width=True, key="dl_reinfo"
        )

    # Tabla AgGrid
    cols_reinfo = [
        "nombre_completo", "cargo", "partido", "tipo_eleccion",
        "dptos_mineros", "n_derechos_mineros", "estado_reinfo_cons",
        "es_region_prioritaria", "etiqueta_riesgo"
    ]
    df_r_tabla = df_r[cols_reinfo].copy()

    row_style_reinfo = JsCode("""
    function(params) {
        if (params.data.es_region_prioritaria === 'SÍ')
            return {'background-color': '#FEF6EC'};
        return {};
    }
    """)

    gb_r = GridOptionsBuilder.from_dataframe(df_r_tabla)
    gb_r.configure_default_column(resizable=True, sortable=True, filter=True)
    gb_r.configure_column("nombre_completo",       header_name="Nombre",             minWidth=200)
    gb_r.configure_column("cargo",                 header_name="Cargo postulado",    minWidth=120)
    gb_r.configure_column("partido",               header_name="Partido",            minWidth=160)
    gb_r.configure_column("tipo_eleccion",         header_name="Tipo elección",      minWidth=160)
    gb_r.configure_column("dptos_mineros",         header_name="Dptos. REINFO",      minWidth=150)
    gb_r.configure_column("n_derechos_mineros",    header_name="N° derechos",        maxWidth=100)
    gb_r.configure_column("estado_reinfo_cons",    header_name="Estado REINFO",      minWidth=120)
    gb_r.configure_column("es_region_prioritaria", header_name="Reg. prioritaria",   maxWidth=120)
    gb_r.configure_column("etiqueta_riesgo",       header_name="Riesgo vot.",        minWidth=110)
    gb_r.configure_selection(selection_mode="single", use_checkbox=False)
    gb_r.configure_grid_options(rowStyle=row_style_reinfo, rowHeight=32, headerHeight=36)

    AgGrid(
        df_r_tabla,
        gridOptions=gb_r.build(),
        update_mode=GridUpdateMode.NO_UPDATE,
        allow_unsafe_jscode=True,
        height=380,
        theme="alpine",
        key="grid_reinfo",
    )

    # Gráficos REINFO
    st.markdown("<br>", unsafe_allow_html=True)
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown(
            '<div style="margin:20px 0 10px 0;">'
            '<p style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 2px 0;">'
            'Distribuci\u00f3n geogr\u00e1fica</p>'
            '<p style="font-size:1.05rem;font-weight:700;color:' + COLOR_TEXT_PRIMARY + ';'
            'margin:0;letter-spacing:-0.01em;">Por departamento REINFO</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        dptos = (
            reinfo_enrich["dptos_mineros"]
            .str.split(";").explode().str.strip()
            .value_counts().reset_index()
        )
        dptos.columns = ["Departamento", "Candidatos"]
        dptos = dptos.head(12)

        fig_dptos = px.bar(
            dptos, x="Candidatos", y="Departamento",
            orientation="h",
            color_discrete_sequence=[COLOR_REINFO],
            height=CHART_HEIGHT_BAR,
            text="Candidatos",
        )
        fig_dptos.update_traces(
            textposition="outside",
            textfont_size=11,
        )
        fig_dptos.update_layout(
            margin=dict(l=0, r=48, t=4, b=0),
            paper_bgcolor=TRANSPARENT,
            plot_bgcolor=TRANSPARENT,
            xaxis=dict(showgrid=False, showticklabels=False, title=None),
            yaxis=dict(tickfont_size=11, title=None),
        )
        st.plotly_chart(fig_dptos, use_container_width=True)

    with col_g2:
        st.markdown(
            '<div style="margin:20px 0 10px 0;">'
            '<p style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 2px 0;">'
            'Distribuci\u00f3n por cargo</p>'
            '<p style="font-size:1.05rem;font-weight:700;color:' + COLOR_TEXT_PRIMARY + ';'
            'margin:0;letter-spacing:-0.01em;">REINFO por cargo postulado</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        por_cargo = reinfo_enrich["cargo"].value_counts().reset_index()
        por_cargo.columns = ["Cargo", "Candidatos"]

        # Barra horizontal en lugar de donut — más legible con varias categorías
        fig_cargo = px.bar(
            por_cargo, x="Candidatos", y="Cargo",
            orientation="h",
            color_discrete_sequence=["#E07B2A", "#F0A050", "#F5C078",
                                     "#D4691A", "#B8561A"],
            height=CHART_HEIGHT_BAR,
            text="Candidatos",
        )
        fig_cargo.update_traces(
            textposition="outside",
            textfont_size=11,
        )
        fig_cargo.update_layout(
            margin=dict(l=0, r=48, t=4, b=0),
            paper_bgcolor=TRANSPARENT,
            plot_bgcolor=TRANSPARENT,
            xaxis=dict(showgrid=False, showticklabels=False, title=None),
            yaxis=dict(tickfont_size=11, title=None),
            showlegend=False,
        )
        st.plotly_chart(fig_cargo, use_container_width=True)


# ===================================================
# TAB 2 — CONGRESISTAS POSTULANDO
# ===================================================
with tab_congs:
    st.markdown(
        f"""
        <div class="nota-card" style="border-left: 4px solid {COLOR_PRIMARY};">
            <b>Criterio de análisis:</b> Estos {len(votos)} congresistas están en ejercicio
            durante el período electoral. Su historial de votación en las 16 leyes
            clave es el insumo principal del score de riesgo.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Filtros
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        busq_c = st.text_input("Buscar nombre", key="busq_cong2",
                                placeholder="Ej: Torres...")
    with col_f2:
        nivel_opts = ["Todos", "🔴 Alto", "🟡 Medio", "🟢 Bajo"]
        nivel_sel  = st.selectbox("Nivel de riesgo", nivel_opts, key="nivel_cong2")

    df_v = votos.copy()
    if busq_c:
        df_v = df_v[df_v["nombre_completo"].str.upper().str.contains(
            busq_c.upper(), na=False)]
    if nivel_sel == "🔴 Alto":
        df_v = df_v[df_v["nivel_riesgo"] == "alto"]
    elif nivel_sel == "🟡 Medio":
        df_v = df_v[df_v["nivel_riesgo"] == "medio"]
    elif nivel_sel == "🟢 Bajo":
        df_v = df_v[df_v["nivel_riesgo"] == "bajo"]

    col_c, col_d = st.columns([3, 1])
    with col_c:
        st.markdown(
            f"<p style='color:{COLOR_TEXT_SECONDARY}; font-size:0.88em;'>"
            f"Mostrando <b>{len(df_v)}</b> congresistas</p>",
            unsafe_allow_html=True,
        )
    with col_d:
        st.download_button(
            "⬇️ Descargar (CSV)",
            data=df_v[[
                "dni","nombre_completo","partido","grupo_parl","cargo",
                "tipo_eleccion","region","score_total","score_procrimen",
                "nivel_riesgo","tiene_reinfo","leyes_autoria"
            ]].to_csv(index=False).encode("utf-8"),
            file_name="congresistas_riesgo.csv", mime="text/csv",
            use_container_width=True, key="dl_cong2"
        )

    # Tabla
    cols_v = [
        "nombre_completo","partido","grupo_parl","cargo","tipo_eleccion",
        "score_total","score_procrimen","etiqueta_riesgo","tiene_reinfo"
    ]
    df_v_tabla = df_v[cols_v].copy()
    df_v_tabla["tiene_reinfo"] = df_v_tabla["tiene_reinfo"].map({"SI":"Sí","NO":"No"})

    row_style_v = JsCode("""
    function(params) {
        var nivel = params.data.etiqueta_riesgo;
        if (nivel && nivel.includes('Alto'))  return {'background-color': '#FDECEA'};
        if (nivel && nivel.includes('Medio')) return {'background-color': '#FEF9E7'};
        if (nivel && nivel.includes('Bajo'))  return {'background-color': '#EAF4EC'};
        return {};
    }
    """)

    gb_v = GridOptionsBuilder.from_dataframe(df_v_tabla)
    gb_v.configure_default_column(resizable=True, sortable=True, filter=True)
    gb_v.configure_column("nombre_completo",  header_name="Nombre",               minWidth=200)
    gb_v.configure_column("partido",          header_name="Partido",              minWidth=160)
    gb_v.configure_column("grupo_parl",       header_name="Grupo parlamentario",  minWidth=160)
    gb_v.configure_column("cargo",            header_name="Cargo postulado",      minWidth=120)
    gb_v.configure_column("tipo_eleccion",    header_name="Tipo elección",        minWidth=150)
    gb_v.configure_column("score_total",      header_name="Score total",          maxWidth=100)
    gb_v.configure_column("score_procrimen",  header_name="Score pro-crimen",     maxWidth=120)
    gb_v.configure_column("etiqueta_riesgo",  header_name="Riesgo",               minWidth=110)
    gb_v.configure_column("tiene_reinfo",     header_name="REINFO",               maxWidth=90)
    gb_v.configure_grid_options(rowStyle=row_style_v, rowHeight=32, headerHeight=36)

    AgGrid(
        df_v_tabla,
        gridOptions=gb_v.build(),
        update_mode=GridUpdateMode.NO_UPDATE,
        allow_unsafe_jscode=True,
        height=400,
        theme="alpine",
        key="grid_cong2",
    )

    # ---- Gráfico strip: score total por congresista ----
    st.markdown(
        '<div style="margin:24px 0 10px 0;">'
        '<p style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 2px 0;">'
        'An\u00e1lisis visual</p>'
        '<p style="font-size:1.05rem;font-weight:700;color:' + COLOR_TEXT_PRIMARY + ';'
        'margin:0 0 2px 0;letter-spacing:-0.01em;">Score total por congresista</p>'
        '<p style="font-size:0.82rem;color:' + COLOR_TEXT_SECONDARY + ';margin:0;">'
        'Cada punto es un congresista. Pasa el cursor para ver el nombre y score.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    votos["color_nivel"] = votos["nivel_riesgo"].map(COLOR_NIVEL)

    fig_scatter = px.strip(
        votos,
        x="grupo_parl",
        y="score_total",
        color="nivel_riesgo",
        color_discrete_map=COLOR_NIVEL,
        hover_name="nombre_completo",
        hover_data={
            "score_total":  True,
            "partido":      True,
            "grupo_parl":   True,
            "nivel_riesgo": False,
        },
        labels={
            "grupo_parl":   "Grupo parlamentario",
            "score_total":  "Score total",
            "nivel_riesgo": "Riesgo",
        },
        stripmode="overlay",
        height=CHART_HEIGHT_MAIN,
    )

    # Personalizar hover
    fig_scatter.update_traces(
        marker=dict(size=SCATTER_MARKER_SIZE, opacity=0.85, line=dict(width=0.5, color="white")),
        jitter=SCATTER_JITTER,
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Score: %{y}<br>"
            "Partido: %{customdata[0]}<br>"
            "Grupo: %{customdata[1]}<extra></extra>"
        ),
    )

    fig_scatter.update_layout(
        margin=dict(l=8, r=24, t=16, b=80),
        paper_bgcolor=TRANSPARENT,
        plot_bgcolor=TRANSPARENT,
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(size=11),
            title=None,
            showgrid=False,
            showline=True,
            linecolor=COLOR_BORDER,
        ),
        yaxis=dict(
            showgrid=False,
            showline=True,
            linecolor=COLOR_BORDER,
            title=dict(text="Score total", font=dict(size=12)),
            zeroline=False,
        ),
        legend=dict(
            orientation="h",
            y=-0.22,
            font_size=12,
            title_text="Riesgo",
            title_font_size=12,
        ),
    )

    # Líneas de umbral con anotaciones más visibles
    fig_scatter.add_hline(
        y=20, line_dash="dash", line_color=COLOR_RIESGO_ALTO, line_width=1.5,
        annotation_text="  Umbral alto (20)",
        annotation_position="right",
        annotation_font=dict(size=11, color=COLOR_RIESGO_ALTO),
    )
    fig_scatter.add_hline(
        y=10, line_dash="dot", line_color=COLOR_RIESGO_MEDIO, line_width=1.5,
        annotation_text="  Umbral medio (10)",
        annotation_position="right",
        annotation_font=dict(size=11, color=COLOR_RIESGO_MEDIO),
    )

    st.plotly_chart(fig_scatter, use_container_width=True)


# ===================================================
# TAB 3 — PRESIDENCIABLES
# ===================================================
with tab_pres:

    # ---- session_state: controla qué fila está expandida ----
    # "pres_sel_nombre" guarda el nombre del candidato seleccionado.
    # Cuando el usuario hace clic en "Cerrar", lo ponemos a None
    # y Streamlit re-renderiza la página sin el panel abierto.
    if "pres_sel_nombre" not in st.session_state:
        st.session_state["pres_sel_nombre"] = None

    st.markdown(
        f"""
        <div class="nota-card" style="border-left: 4px solid {COLOR_PRIMARY};">
            <b>Nota:</b> Se muestran {len(solo_pres)} candidatos a la Presidencia de la República.
            El score de votación solo aplica a quienes son también congresistas en ejercicio
            ({int(pres["es_congresista"].sum())} de {len(formulas)} miembros de fórmulas presidenciales).
            Haz clic en cualquier fila para ver el perfil completo.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Gráfico: score de presidenciables ex-congresistas ----
    pres_cong_scores = solo_pres[solo_pres["es_congresista"]].copy()
    if not pres_cong_scores.empty:
        pres_cong_scores = pres_cong_scores.sort_values("score_total", ascending=True)
        pres_cong_scores["nombre_corto"] = (
            pres_cong_scores["nombre_completo"].str.split().str[:2].str.join(" ")
        )

        st.markdown(
            '<div style="margin:0 0 10px 0;">'
            '<p style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 2px 0;">'
            'Historial legislativo</p>'
            '<p style="font-size:1.05rem;font-weight:700;color:' + COLOR_TEXT_PRIMARY + ';'
            'margin:0 0 2px 0;letter-spacing:-0.01em;">'
            'Score legislativo \u2014 presidenciables congresistas</p>'
            '<p style="font-size:0.82rem;color:' + COLOR_TEXT_SECONDARY + ';margin:0;">'
            'Solo los candidatos presidenciales con historial en el Congreso actual.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

        fig_pres_scores = px.bar(
            pres_cong_scores,
            x="score_total",
            y="nombre_corto",
            orientation="h",
            color="nivel_riesgo",
            color_discrete_map=COLOR_NIVEL,
            text="score_total",
            hover_name="nombre_completo",
            hover_data={"partido": True, "score_total": True, "nivel_riesgo": False},
            labels={"score_total": "Score total", "nombre_corto": ""},
            height=max(200, len(pres_cong_scores) * 44),
        )
        fig_pres_scores.update_traces(textposition="outside", textfont_size=12)
        fig_pres_scores.update_layout(
            margin=dict(l=0, r=48, t=8, b=8),
            paper_bgcolor=TRANSPARENT,
            plot_bgcolor=TRANSPARENT,
            xaxis=dict(showgrid=False, showticklabels=False, title=None),
            yaxis=dict(tickfont_size=12, title=None),
            showlegend=False,
        )
        fig_pres_scores.add_vline(
            x=20, line_dash="dash", line_color=COLOR_RIESGO_ALTO, line_width=1.5,
            annotation_text="Umbral alto",
            annotation_position="top",
            annotation_font=dict(size=10, color=COLOR_RIESGO_ALTO),
        )
        st.plotly_chart(fig_pres_scores, use_container_width=True)

    st.markdown("---")

    # ---- Tabla de presidenciables ----
    st.markdown(
        '<div style="margin:0 0 8px 0;">'
        '<p style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 2px 0;">'
        'Tabla principal</p>'
        '<p style="font-size:1.05rem;font-weight:700;color:' + COLOR_TEXT_PRIMARY + ';'
        'margin:0;letter-spacing:-0.01em;">'
        'Candidatos a la Presidencia (' + str(len(solo_pres)) + ')'
        '<span style="font-size:0.72rem;font-weight:400;color:' + COLOR_TEXT_SECONDARY + ';'
        'margin-left:12px;">Selecciona una fila para ver el perfil completo</span></p>'
        '</div>',
        unsafe_allow_html=True,
    )

    cols_pres = [
        "nombre_completo", "partido", "region", "estado_jne",
        "es_congresista", "score_total", "etiqueta_riesgo"
    ]
    df_pres_tabla = solo_pres[cols_pres].copy()
    df_pres_tabla["es_congresista"] = df_pres_tabla["es_congresista"].map(
        {True: "✅ Sí", False: "—"}
    )

    row_style_pres = JsCode("""
    function(params) {
        var nivel = params.data.etiqueta_riesgo;
        if (nivel && nivel.includes('Alto'))  return {'background-color': '#FDECEA'};
        if (nivel && nivel.includes('Medio')) return {'background-color': '#FEF9E7'};
        if (nivel && nivel.includes('Bajo'))  return {'background-color': '#EAF4EC'};
        return {};
    }
    """)

    gb_p = GridOptionsBuilder.from_dataframe(df_pres_tabla)
    gb_p.configure_default_column(resizable=True, sortable=True, filter=True)
    gb_p.configure_column("nombre_completo",  header_name="Nombre",          minWidth=220)
    gb_p.configure_column("partido",          header_name="Partido",         minWidth=180)
    gb_p.configure_column("region",           header_name="Región",          minWidth=120)
    gb_p.configure_column("estado_jne",       header_name="Estado JNE",      minWidth=110)
    gb_p.configure_column("es_congresista",   header_name="Congresista",     maxWidth=110)
    gb_p.configure_column("score_total",      header_name="Score",           maxWidth=80)
    gb_p.configure_column("etiqueta_riesgo",  header_name="Riesgo",          minWidth=110)
    gb_p.configure_selection(selection_mode="single", use_checkbox=False)
    gb_p.configure_grid_options(rowStyle=row_style_pres, rowHeight=32, headerHeight=36)

    grid_pres_resp = AgGrid(
        df_pres_tabla,
        gridOptions=gb_p.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        height=340,
        theme="alpine",
        key="grid_pres",
    )

    # Descarga
    st.download_button(
        "⬇️ Descargar presidenciables (CSV)",
        data=solo_pres[[
            "dni","nombre_completo","partido","region","estado_jne",
            "es_congresista","score_total","nivel_riesgo","etiqueta_riesgo"
        ]].to_csv(index=False).encode("utf-8"),
        file_name="presidenciables.csv",
        mime="text/csv",
        key="dl_pres",
    )

    # ---- Leer selección de la tabla y guardar en session_state ----
    # Si el usuario selecciona una fila nueva, actualizamos session_state.
    # Si no hay selección (deseleccionó), mantenemos el último valor
    # hasta que el usuario presione "Cerrar perfil".
    sel_rows = grid_pres_resp.get("selected_rows", [])
    if sel_rows is None:
        sel_rows = []
    if isinstance(sel_rows, pd.DataFrame):
        sel_rows = sel_rows.to_dict("records")
    if len(sel_rows) > 0:
        st.session_state["pres_sel_nombre"] = sel_rows[0]["nombre_completo"]

    # ---- Panel de perfil expandible ----
    sel_nombre = st.session_state.get("pres_sel_nombre")
    if sel_nombre:
        match = solo_pres[solo_pres["nombre_completo"] == sel_nombre]
        if not match.empty:
            row_p = match.iloc[0]
            nivel_r = row_p.get("nivel_riesgo", "none")
            color_n = COLOR_NIVEL.get(nivel_r, COLOR_RIESGO_NONE)
            score_txt = (
                f"{int(row_p['score_total'])}"
                if pd.notna(row_p.get("score_total")) else None
            )
            es_cong = bool(row_p.get("es_congresista", False))

            badge_bg = {
                "alto": "#FDECEA", "medio": "#FEF9E7",
                "bajo": "#EAF4EC", "none": "#F4F4F4",
            }.get(nivel_r, "#F4F4F4")
            badge_label = (
                row_p.get("etiqueta_riesgo", "Sin score")
                if score_txt else "Sin historial legislativo"
            )
            url_jne_val = str(row_p.get("url_jne", "")).strip()

            # Separador visual y encabezado del panel
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style="
                    background:{COLOR_SURFACE};
                    border:1px solid {COLOR_BORDER};
                    border-left:5px solid {color_n};
                    border-radius:8px;
                    padding:20px 24px 16px 24px;
                ">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <div style="font-size:1.1em; font-weight:700;
                                        color:{COLOR_TEXT_PRIMARY}; line-height:1.3;">
                                {row_p["nombre_completo"]}
                            </div>
                            <div style="font-size:0.85em; color:{COLOR_TEXT_SECONDARY}; margin-top:3px;">
                                Candidato/a a la Presidencia &middot; {row_p.get("partido","—")}
                            </div>
                            <div style="margin-top:8px; display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
                                <span style="
                                    display:inline-block;
                                    padding:3px 12px; border-radius:20px;
                                    font-size:0.8em; font-weight:700;
                                    background:{badge_bg}; color:{color_n};
                                ">{badge_label}</span>
                                {('<a href="' + url_jne_val + '" target="_blank" rel="noopener" style="'
                                  'display:inline-flex;align-items:center;gap:4px;'
                                  'padding:3px 10px;border-radius:4px;'
                                  'border:1px solid ' + COLOR_BORDER + ';'
                                  'background:' + COLOR_SURFACE + ';'
                                  'color:' + COLOR_TEXT_SECONDARY + ';'
                                  'font-size:0.78em;font-weight:600;'
                                  'text-decoration:none;letter-spacing:0.02em;">'
                                  '\U0001f517 Hoja de vida JNE</a>') if url_jne_val else ""}
                            </div>
                        </div>
                        {'<div style="text-align:center; min-width:64px;"><div style="font-size:2em; font-weight:700; color:' + color_n + '; line-height:1;">' + score_txt + '</div><div style="font-size:0.75em; color:' + color_n + ';">score</div></div>' if score_txt else ""}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Columnas con los datos del perfil
            col_izq, col_der = st.columns(2)

            with col_izq:
                st.markdown(
                    f"<p style='font-size:0.75em; font-weight:700; letter-spacing:0.08em;"
                    f"text-transform:uppercase; color:{COLOR_TEXT_SECONDARY}; margin:12px 0 6px 0;'>"
                    f"Datos de candidatura</p>",
                    unsafe_allow_html=True,
                )
                datos_cand = {
                    "Partido":         row_p.get("partido", "—"),
                    "Región":          row_p.get("region", "—"),
                    "Estado JNE":      row_p.get("estado_jne", "—"),
                    "Expediente JNE":  row_p.get("expediente", "—"),
                    "Congresista":     "✅ Sí" if es_cong else "No",
                }
                for lbl, val in datos_cand.items():
                    st.markdown(
                        f"<div style='display:flex; justify-content:space-between;"
                        f"padding:5px 0; border-bottom:1px solid {COLOR_BORDER};"
                        f"font-size:0.86em;'>"
                        f"<span style='color:{COLOR_TEXT_SECONDARY};'>{lbl}</span>"
                        f"<span style='color:{COLOR_TEXT_PRIMARY}; font-weight:500;'>{val}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

            with col_der:
                if es_cong and score_txt:
                    st.markdown(
                        f"<p style='font-size:0.75em; font-weight:700; letter-spacing:0.08em;"
                        f"text-transform:uppercase; color:{COLOR_TEXT_SECONDARY}; margin:12px 0 6px 0;'>"
                        f"Historial legislativo</p>",
                        unsafe_allow_html=True,
                    )
                    sp = row_p.get("score_procrimen", None)
                    ba = row_p.get("bonus_autoria", None)
                    la = row_p.get("leyes_autoria", None)
                    gp = row_p.get("grupo_parl", "—")
                    datos_leg = {
                        "Score total":         score_txt,
                        "Score pro-crimen":    str(int(sp)) if pd.notna(sp) else "—",
                        "Bonus autoría":       str(int(ba)) if pd.notna(ba) else "0",
                        "Grupo parlamentario": gp,
                        "Leyes de autoría":    str(la) if pd.notna(la) else "—",
                    }
                    for lbl, val in datos_leg.items():
                        val_color = color_n if lbl == "Score total" else COLOR_TEXT_PRIMARY
                        val_weight = "700" if lbl == "Score total" else "500"
                        st.markdown(
                            f"<div style='display:flex; justify-content:space-between;"
                            f"padding:5px 0; border-bottom:1px solid {COLOR_BORDER};"
                            f"font-size:0.86em;'>"
                            f"<span style='color:{COLOR_TEXT_SECONDARY};'>{lbl}</span>"
                            f"<span style='color:{val_color}; font-weight:{val_weight};'>{val}</span>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown(
                        f"<p style='font-size:0.85em; color:{COLOR_TEXT_SECONDARY};"
                        f"margin-top:16px; font-style:italic;'>"
                        f"Este candidato no tiene historial legislativo en el Congreso actual.</p>",
                        unsafe_allow_html=True,
                    )

            # Botón Cerrar: limpia session_state → Streamlit re-renderiza sin el panel
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.button("✕ Cerrar perfil", key="btn_cerrar_pres"):
                st.session_state["pres_sel_nombre"] = None
                st.rerun()

    # ---- Sección: Fórmulas con congresistas ----
    st.markdown(
        '<div style="margin:28px 0 8px 0;">'
        '<p style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 2px 0;">'
        'An\u00e1lisis complementario</p>'
        '<p style="font-size:1.05rem;font-weight:700;color:' + COLOR_TEXT_PRIMARY + ';'
        'margin:0;letter-spacing:-0.01em;">'
        'F\u00f3rmulas presidenciales con congresistas en ejercicio</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    formulas_cong = formulas[formulas["es_congresista"]].copy()

    if formulas_cong.empty:
        st.info("No se encontraron miembros de fórmulas presidenciales que sean congresistas.")
    else:
        for _, row_f in formulas_cong.sort_values("score_total", ascending=False).iterrows():
            nivel_r = row_f.get("nivel_riesgo", "none")
            color_n = COLOR_NIVEL.get(nivel_r, COLOR_RIESGO_NONE)
            score_txt_f = (
                f"{int(row_f['score_total'])}"
                if pd.notna(row_f.get("score_total")) else "—"
            )
            st.markdown(
                f"""
                <div style="
                    background:{COLOR_SURFACE};
                    border:1px solid {COLOR_BORDER};
                    border-left:4px solid {color_n};
                    border-radius:6px;
                    padding:12px 20px;
                    margin-bottom:8px;
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                ">
                    <div>
                        <div style="font-weight:600; color:{COLOR_TEXT_PRIMARY}; font-size:0.97em;">
                            {row_f["nombre_completo"]}
                        </div>
                        <div style="font-size:0.82em; color:{COLOR_TEXT_SECONDARY}; margin-top:3px;">
                            {row_f["cargo_corto"]} &middot; {row_f["partido"]}
                        </div>
                        <div style="font-size:0.8em; color:{COLOR_TEXT_SECONDARY};">
                            Grupo parlamentario: {row_f.get("grupo_parl","—")}
                        </div>
                    </div>
                    <div style="text-align:center; min-width:72px;">
                        <div style="font-size:1.9em; font-weight:700;
                                    color:{color_n}; line-height:1.1;">
                            {score_txt_f}
                        </div>
                        <div style="font-size:0.75em; color:{color_n};
                                    font-weight:600; margin-top:2px;">
                            {row_f.get("etiqueta_riesgo","—")}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
# -------------------------------------------------------
# SECTION: Footer
# -------------------------------------------------------
st.markdown(
    f"""
    <div style="
        margin-top: 32px;
        padding-top: 12px;
        border-top: 1px solid {COLOR_BORDER};
        font-size: 0.78em;
        color: {COLOR_TEXT_SECONDARY};
        display: flex;
        justify-content: space-between;
    ">
        <span>{APP_CONFIDENTIAL_LABEL}</span>
        <span>Fuentes: JNE · REINFO · Congreso del Perú</span>
    </div>
    """,
    unsafe_allow_html=True,
)
