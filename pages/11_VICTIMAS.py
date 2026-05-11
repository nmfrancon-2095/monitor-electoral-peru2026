# ============================================================
# pages/8_VICTIMAS.py — Monitor Electoral Perú 2026
# Módulo de violencia electoral — Patrones sobre víctimas.
# Interseccionalidad, VBG, respuesta institucional.
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    APP_TITLE, APP_ICON, APP_CONFIDENTIAL_LABEL, APP_VERSION,
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_GOLD, COLOR_BACKGROUND, COLOR_SURFACE,
    COLOR_BORDER, COLOR_BORDER_STRONG,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_RIESGO_ALTO, COLOR_RIESGO_ALTO_BG,
    COLOR_RIESGO_MEDIO, COLOR_RIESGO_MEDIO_BG,
    COLOR_RIESGO_BAJO, COLOR_RIESGO_BAJO_BG,
    CHART_HEIGHT, CHART_HEIGHT_SMALL, GLOBAL_CSS,
)
from data_loader_violencia import (
    cargar_datos_violencia, limpiar_cache_violencia, kpis_violencia,
    _explode_multiselect,
)

# -------------------------------------------------------
# SECTION: Page setup
# -------------------------------------------------------
st.set_page_config(
    page_title="V\u00edctimas \u00b7 " + APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

if not st.session_state.get("autenticado", False):
    st.warning("Debes iniciar sesi\u00f3n primero.")
    st.stop()

_VIO_KEY = "violencia_auth"
if not st.session_state.get(_VIO_KEY, False):
    st.warning("Accede primero a la p\u00e1gina de Incidentes para autenticarte en el m\u00f3dulo de violencia.")
    st.stop()

# -------------------------------------------------------
# SECTION: Carga de datos
# -------------------------------------------------------
with st.spinner("Cargando datos..."):
    df_inc, df_vic, df_joined = cargar_datos_violencia()

kpis = kpis_violencia(df_inc, df_vic)

# -------------------------------------------------------
# SECTION: Header
# -------------------------------------------------------
col_h, col_btn = st.columns([5, 1])
with col_h:
    st.markdown(
        '<div class="page-title-wrap">'
        + '<div class="page-eyebrow">Monitor Electoral Per\u00fa 2026 \u00b7 M\u00f3dulo de Violencia Electoral</div>'
        + '<h1 class="page-title">Presuntas v\u00edctimas</h1>'
        + '<p style="font-size:0.85rem; color:' + COLOR_TEXT_SECONDARY + '; margin:6px 0 0 0;">'
        + 'Perfiles, interseccionalidad y respuesta institucional \u00b7 '
        + APP_VERSION + '</p>'
        + '</div>',
        unsafe_allow_html=True,
    )
with col_btn:
    st.markdown("<div style='padding-top:32px;'>", unsafe_allow_html=True)
    if st.button("Actualizar datos", use_container_width=True):
        limpiar_cache_violencia()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------
# SECTION: Filtros
# -------------------------------------------------------
with st.expander("Filtros", expanded=False):
    fv1, fv2, fv3, fv4 = st.columns(4)
    with fv1:
        tipos_vic = ["Todos"] + sorted(df_vic["tipo_victima"].dropna().unique().tolist()) \
                    if "tipo_victima" in df_vic.columns else ["Todos"]
        f_tipo = st.selectbox("Tipo de v\u00edctima", tipos_vic)
    with fv2:
        generos = ["Todos"] + sorted(df_vic["genero"].dropna().unique().tolist()) \
                  if "genero" in df_vic.columns else ["Todos"]
        f_genero = st.selectbox("Identidad de g\u00e9nero", generos)
    with fv3:
        cargos = ["Todos"] + sorted(df_vic["cargo_postula"].dropna().unique().tolist()) \
                 if "cargo_postula" in df_vic.columns else ["Todos"]
        f_cargo = st.selectbox("Cargo que postula", cargos)
    with fv4:
        factores = ["Todos"] + sorted(df_vic["factor_diferencial"].dropna().unique().tolist()) \
                   if "factor_diferencial" in df_vic.columns else ["Todos"]
        f_factor = st.selectbox("Factor diferencial", factores)

df_vf = df_vic.copy()
if f_tipo != "Todos":
    df_vf = df_vf[df_vf["tipo_victima"] == f_tipo]
if f_genero != "Todos":
    df_vf = df_vf[df_vf["genero"] == f_genero]
if f_cargo != "Todos":
    df_vf = df_vf[df_vf["cargo_postula"] == f_cargo]
if f_factor != "Todos":
    df_vf = df_vf[df_vf["factor_diferencial"] == f_factor]

# -------------------------------------------------------
# SECTION: KPI cards
# -------------------------------------------------------
k1, k2, k3, k4, k5 = st.columns(5)

def _kpi(col, label, value, sub=None, color=None, border_color=None):
    c = color or COLOR_TEXT_PRIMARY
    bc = border_color or COLOR_BORDER_STRONG
    with col:
        st.markdown(
            "<div style='background:" + COLOR_SURFACE + "; border:1px solid " + COLOR_BORDER + ";"
            " border-top:3px solid " + bc + ";"
            " border-radius:0; padding:16px 18px 14px 18px;'>"
            "<div style='font-size:0.62rem; font-weight:700; letter-spacing:0.12em;"
            " text-transform:uppercase; color:" + COLOR_TEXT_MUTED + "; margin-bottom:6px;'>"
            + label + "</div>"
            "<div style='font-family:\"Source Serif 4\",Georgia,serif; font-size:2.2rem;"
            " font-weight:600; color:" + c + ";"
            " font-variant-numeric:tabular-nums; line-height:1.1;'>"
            + str(value) + "</div>"
            + ("<div style='font-size:0.75rem; color:" + COLOR_TEXT_SECONDARY + "; margin-top:4px;'>"
               + str(sub) + "</div>" if sub else "")
            + "</div>",
            unsafe_allow_html=True,
        )

n_vf           = len(df_vf)
n_candidatas   = df_vf["es_candidata"].sum()  if "es_candidata"          in df_vf.columns else 0
n_vbg          = df_vf["tiene_vbg"].sum()      if "tiene_vbg"             in df_vf.columns else 0
n_factor       = df_vf["tiene_factor_diferencial"].sum() \
                 if "tiene_factor_diferencial" in df_vf.columns else 0
n_sin_denuncia = (df_vf["instancia_denuncia"] == "No se ha hecho una denuncia/reporte formal").sum() \
                  if "instancia_denuncia" in df_vf.columns else 0

_kpi(k1, "Total v\u00edctimas", n_vf, border_color=COLOR_PRIMARY)
_kpi(k2, "Candidatas/os", n_candidatas,
     f"{round(n_candidatas/n_vf*100,1) if n_vf else 0}% del total", border_color=COLOR_ACCENT)
_kpi(k3, "Con indicadores VBG", n_vbg,
     f"{round(n_vbg/n_vf*100,1) if n_vf else 0}% del total",
     color=COLOR_RIESGO_ALTO, border_color=COLOR_RIESGO_ALTO)
_kpi(k4, "Con factor diferencial", n_factor,
     f"{round(n_factor/n_vf*100,1) if n_vf else 0}% del total", border_color=COLOR_BORDER_STRONG)
_kpi(k5, "Sin denuncia formal", n_sin_denuncia,
     f"{round(n_sin_denuncia/n_vf*100,1) if n_vf else 0}% del total",
     color=COLOR_RIESGO_MEDIO, border_color=COLOR_RIESGO_MEDIO)

st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------
# SECTION: Helper — layout y estilo v3
# -------------------------------------------------------
def _L(height=300, xaxis_title=None, yaxis_title=None,
       showlegend=False, margin=None, extra=None):
    m = margin or dict(t=8, b=8, l=0, r=48)
    d = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'DM Sans', system-ui, sans-serif", size=11, color="#45556A"),
        height=height, showlegend=showlegend, margin=m,
        xaxis=dict(showgrid=False, zeroline=False, showline=False,
                   tickfont=dict(size=10, family="'DM Sans', sans-serif", color="#7A7366"),
                   title=xaxis_title),
        yaxis=dict(showgrid=False, zeroline=False, showline=False,
                   tickfont=dict(size=10, family="'DM Sans', sans-serif", color="#7A7366"),
                   title=yaxis_title),
    )
    if extra:
        d.update(extra)
    return d

def _bar(fig, orientation="h"):
    fig.update_traces(
        marker_line_width=0, textposition="outside", cliponaxis=False,
        textfont=dict(size=10, family="'DM Sans', sans-serif", color="#45556A"),
    )
    if orientation == "v":
        fig.update_xaxes(tickangle=-30)
        fig.update_yaxes(showgrid=True, gridcolor="#E5E1D6", gridwidth=1)
    return fig

# -------------------------------------------------------
# SECTION: Tabs de análisis
# -------------------------------------------------------
tab_perfil, tab_intersec, tab_vbg, tab_resp, tab_ae = st.tabs([
    "Perfil predominante",
    "Interseccionalidad",
    "Violencia de g\u00e9nero",
    "Respuesta institucional",
    "\U0001f3db Autoridades electorales",
])

# --- TAB 1: Perfil predominante ---
with tab_perfil:
    r1c1, r1c2 = st.columns(2, gap="medium")

    with r1c1:
        st.markdown(
            "<div class='section-header'>Tipo de v\u00edctima</div>"
            "<div class='section-subheader'>Individual, colectivo u organizaci\u00f3n</div>",
            unsafe_allow_html=True,
        )
        if "tipo_victima" in df_vf.columns:
            df_tv = df_vf["tipo_victima"].value_counts().reset_index()
            df_tv.columns = ["tipo", "n"]
            fig_tv = px.bar(df_tv.sort_values("n"),
                            x="n", y="tipo", orientation="h",
                            color_discrete_sequence=[COLOR_PRIMARY],
                            text="n")
            fig_tv.update_layout(**_L(height=220, xaxis_title="V\u00edctimas", yaxis_title=None, showlegend=False))
            fig_tv.update_traces(marker_line_width=0, textposition="outside", cliponaxis=False, textfont=dict(size=10, family="'DM Sans', sans-serif", color="#45556A"))
            st.plotly_chart(fig_tv, use_container_width=True)

    with r1c2:
        st.markdown(
            "<div class='section-header'>Factor diferencial</div>"
            "<div class='section-subheader'>Perfil de riesgo espec\u00edfico de la v\u00edctima</div>",
            unsafe_allow_html=True,
        )
        if "factor_diferencial" in df_vf.columns:
            serie_fd = _explode_multiselect(df_vf, "factor_diferencial")
            df_fd = serie_fd.value_counts().reset_index()
            df_fd.columns = ["factor", "n"]
            fig_fd = px.bar(df_fd.sort_values("n"),
                            x="n", y="factor", orientation="h",
                            color_discrete_sequence=[COLOR_ACCENT],
                            text="n")
            fig_fd.update_layout(**_L(height=max(220, len(df_fd))*30+60),
                                 xaxis_title="V\u00edctimas", yaxis_title=None)
            fig_fd.update_traces(marker_line_width=0, textposition="outside", cliponaxis=False, textfont=dict(size=10, family="'DM Sans', sans-serif", color="#45556A"))
            st.plotly_chart(fig_fd, use_container_width=True)

    r2c1, r2c2 = st.columns(2, gap="medium")
    with r2c1:
        st.markdown(
            "<div class='section-header'>Cargo que postula</div>"
            "<div class='section-subheader'>Solo v\u00edctimas candidatas</div>",
            unsafe_allow_html=True,
        )
        if "cargo_postula" in df_vf.columns:
            df_cargo = df_vf["cargo_postula"].dropna().value_counts().reset_index()
            df_cargo.columns = ["cargo", "n"]
            if not df_cargo.empty:
                fig_cargo = px.bar(df_cargo.sort_values("n"),
                                   x="n", y="cargo", orientation="h",
                                   color_discrete_sequence=["#4A9BD4"],
                                   text="n")
                fig_cargo.update_layout(**_L(height=220, xaxis_title="V\u00edctimas", yaxis_title=None))
                fig_cargo.update_traces(marker_line_width=0, textposition="outside", cliponaxis=False, textfont=dict(size=10, family="'DM Sans', sans-serif", color="#45556A"))
                st.plotly_chart(fig_cargo, use_container_width=True)
            else:
                st.info("No hay v\u00edctimas candidatas en la selecci\u00f3n actual.")

    with r2c2:
        st.markdown(
            "<div class='section-header'>Partido / movimiento</div>"
            "<div class='section-subheader'>Afiliaci\u00f3n pol\u00edtica de las v\u00edctimas</div>",
            unsafe_allow_html=True,
        )
        if "org_politica" in df_vf.columns:
            df_part = df_vf["org_politica"].dropna().value_counts().reset_index()
            df_part.columns = ["partido", "n"]
            if not df_part.empty:
                fig_part = px.bar(df_part.sort_values("n"),
                                  x="n", y="partido", orientation="h",
                                  color_discrete_sequence=["#6B4FA0"],
                                  text="n")
                fig_part.update_layout(**_L(height=max(220, len(df_part))*30+60),
                                       xaxis_title="V\u00edctimas", yaxis_title=None)
                fig_part.update_traces(marker_line_width=0, textposition="outside", cliponaxis=False, textfont=dict(size=10, family="'DM Sans', sans-serif", color="#45556A"))
                st.plotly_chart(fig_part, use_container_width=True)

    # Objetivo político
    st.markdown(
        "<div class='section-header' style='margin-top:8px;'>Objetivo pol\u00edtico aparente</div>"
        "<div class='section-subheader'>Finalidad del ataque seg\u00fan an\u00e1lisis contextual</div>",
        unsafe_allow_html=True,
    )
    if "objetivo_politico" in df_vf.columns:
        serie_obj = _explode_multiselect(df_vf, "objetivo_politico")
        df_obj = serie_obj.value_counts().reset_index()
        df_obj.columns = ["objetivo", "n"]
        fig_obj = px.bar(df_obj.sort_values("n"),
                         x="n", y="objetivo", orientation="h",
                         color_discrete_sequence=[COLOR_RIESGO_ALTO],
                         text="n")
        fig_obj.update_layout(**_L(height=max(220, len(df_obj))*30+60),
                              xaxis_title="V\u00edctimas", yaxis_title=None)
        fig_obj.update_traces(marker_line_width=0, textposition="outside", cliponaxis=False, textfont=dict(size=10, family="'DM Sans', sans-serif", color="#45556A"))
        st.plotly_chart(fig_obj, use_container_width=True)

# --- TAB 2: Interseccionalidad ---
with tab_intersec:
    ti1, ti2 = st.columns(2, gap="medium")

    with ti1:
        st.markdown(
            "<div class='section-header'>Identidad de g\u00e9nero</div>",
            unsafe_allow_html=True,
        )
        if "genero" in df_vf.columns:
            df_gen = df_vf["genero"].value_counts(dropna=False).reset_index()
            df_gen.columns = ["genero", "n"]
            df_gen["genero"] = df_gen["genero"].fillna("Sin dato")
            color_gen = {
                "Masculino": COLOR_PRIMARY, "Femenino": COLOR_RIESGO_MEDIO,
                "No binario/gender queer": COLOR_ACCENT, "Sin dato": "#8A9BAA", "Otra": "#C9A227",
            }
            fig_gen = px.bar(df_gen.sort_values("n"), x="n", y="genero",
                             orientation="h", color="genero",
                             color_discrete_map=color_gen, text="n")
            fig_gen.update_layout(**_L(height=220, xaxis_title="V\u00edctimas",
                                       showlegend=True, margin=dict(t=8,b=40,l=0,r=48),
                                       extra=dict(legend=dict(orientation="h", y=-0.25, x=0,
                                           font=dict(size=10, family="'DM Sans', sans-serif")))))
            _bar(fig_gen)
            st.plotly_chart(fig_gen, use_container_width=True)

    with ti2:
        st.markdown(
            "<div class='section-header'>Identidad \u00e9tnica</div>",
            unsafe_allow_html=True,
        )
        if "etnia" in df_vf.columns:
            df_etnia = df_vf["etnia"].value_counts(dropna=False).reset_index()
            df_etnia.columns = ["etnia", "n"]
            df_etnia["etnia"] = df_etnia["etnia"].fillna("Sin dato")
            fig_etnia = px.bar(df_etnia.sort_values("n"),
                               x="n", y="etnia", orientation="h",
                               color_discrete_sequence=["#1E8A4A"],
                               text="n")
            fig_etnia.update_layout(**_L(height=260, xaxis_title="V\u00edctimas", yaxis_title=None))
            fig_etnia.update_traces(marker_line_width=0, textposition="outside", cliponaxis=False, textfont=dict(size=10, family="'DM Sans', sans-serif", color="#45556A"))
            st.plotly_chart(fig_etnia, use_container_width=True)

    ti3, ti4 = st.columns(2, gap="medium")
    with ti3:
        st.markdown(
            "<div class='section-header'>Rango de edad</div>",
            unsafe_allow_html=True,
        )
        if "edad" in df_vf.columns:
            df_edad = df_vf["edad"].value_counts(dropna=False).reset_index()
            df_edad.columns = ["edad", "n"]
            df_edad["edad"] = df_edad["edad"].fillna("Sin dato")
            fig_edad = px.bar(df_edad.sort_values("edad"),
                              x="edad", y="n",
                              color_discrete_sequence=[COLOR_ACCENT],
                              text="n")
            fig_edad.update_layout(**_L(height=240, xaxis_title=None, yaxis_title="V\u00edctimas"))
            fig_edad.update_traces(marker_line_width=0, textposition="outside", cliponaxis=False, textfont=dict(size=10, family="'DM Sans', sans-serif", color="#45556A"))
            st.plotly_chart(fig_edad, use_container_width=True)

    with ti4:
        st.markdown(
            "<div class='section-header'>G\u00e9nero \u00d7 tipo de v\u00edctima</div>",
            unsafe_allow_html=True,
        )
        if "genero" in df_vf.columns and "tipo_victima" in df_vf.columns:
            df_cross = df_vf.groupby(
                ["tipo_victima", "genero"], dropna=False
            ).size().reset_index(name="n")
            df_cross["genero"] = df_cross["genero"].fillna("Sin dato")
            fig_cross = px.bar(df_cross, x="tipo_victima", y="n",
                               color="genero", barmode="stack",
                               color_discrete_sequence=[
                                   COLOR_PRIMARY, COLOR_RIESGO_MEDIO,
                                   COLOR_ACCENT, "#8A9BAA"
                               ],
                               text="n")
            fig_cross.update_layout(**_L(height=240, xaxis_title=None, yaxis_title="V\u00edctimas"))
            fig_cross.update_traces(marker_line_width=0,
                                    textposition="inside", textfont_size=10)
            st.plotly_chart(fig_cross, use_container_width=True)

    # Personas trans
    if "es_trans" in df_vf.columns:
        n_trans = (df_vf["es_trans"] == "Si").sum()
        if n_trans > 0:
            st.markdown(
                "<div class='nota-card' style='border-left:3px solid " + COLOR_RIESGO_MEDIO + ";'>"
                + str(n_trans)
                + " v\u00edctima(s) son personas transg\u00e9nero. "
                  "Este dato es relevante para el an\u00e1lisis de patrones de discriminaci\u00f3n por prejuicio."
                + "</div>",
                unsafe_allow_html=True,
            )

# --- TAB 3: Violencia de género ---
with tab_vbg:
    df_vbg = df_vf[df_vf["tiene_vbg"]] if "tiene_vbg" in df_vf.columns else pd.DataFrame()

    if df_vbg.empty:
        st.info("No hay v\u00edctimas con indicadores de violencia de g\u00e9nero en la selecci\u00f3n actual.")
    else:
        vb1, vb2 = st.columns(2, gap="medium")

        with vb1:
            st.markdown(
                "<div class='section-header'>Tipo de violencia espec\u00edfica</div>",
                unsafe_allow_html=True,
            )
            if "tipo_vbg" in df_vbg.columns:
                serie_vbg = _explode_multiselect(df_vbg, "tipo_vbg")
                df_tvbg = serie_vbg.value_counts().reset_index()
                df_tvbg.columns = ["tipo", "n"]
                fig_tvbg = px.bar(df_tvbg.sort_values("n"),
                                  x="n", y="tipo", orientation="h",
                                  color_discrete_sequence=[COLOR_RIESGO_ALTO],
                                  text="n")
                fig_tvbg.update_layout(**_L(height=max(220, len(df_tvbg))*30+60),
                                       xaxis_title="V\u00edctimas", yaxis_title=None)
                fig_tvbg.update_traces(marker_line_width=0, textposition="outside", cliponaxis=False, textfont=dict(size=10, family="'DM Sans', sans-serif", color="#45556A"))
                st.plotly_chart(fig_tvbg, use_container_width=True)

        with vb2:
            st.markdown(
                "<div class='section-header'>Elementos vinculados a VBG</div>",
                unsafe_allow_html=True,
            )
            if "elementos_vbg" in df_vbg.columns:
                serie_evbg = _explode_multiselect(df_vbg, "elementos_vbg")
                df_evbg = serie_evbg.value_counts().reset_index()
                df_evbg.columns = ["elemento", "n"]
                fig_evbg = px.bar(df_evbg.sort_values("n"),
                                  x="n", y="elemento", orientation="h",
                                  color_discrete_sequence=[COLOR_RIESGO_MEDIO],
                                  text="n")
                fig_evbg.update_layout(**_L(height=max(220, len(df_evbg))*30+60),
                                       xaxis_title="V\u00edctimas", yaxis_title=None)
                fig_evbg.update_traces(marker_line_width=0, textposition="outside", cliponaxis=False, textfont=dict(size=10, family="'DM Sans', sans-serif", color="#45556A"))
                st.plotly_chart(fig_evbg, use_container_width=True)

        # Tabla VBG
        st.markdown(
            "<div class='section-header' style='margin-top:8px;'>V\u00edctimas con VBG</div>",
            unsafe_allow_html=True,
        )
        cols_vbg_tabla = [c for c in ["nombre", "genero", "es_trans", "cargo_postula",
                                      "tipo_vbg", "elementos_vbg", "num_serie_incidente"]
                          if c in df_vbg.columns]
        label_map_vbg = {
            "nombre":              "Nombre",
            "genero":              "G\u00e9nero",
            "es_trans":            "Transg\u00e9nero",
            "cargo_postula":       "Cargo que postula",
            "tipo_vbg":            "Tipo de VBG",
            "elementos_vbg":       "Elementos VBG",
            "num_serie_incidente": "N\u00b0 incidente",
        }
        st.dataframe(
            df_vbg[cols_vbg_tabla].rename(
                columns={c: label_map_vbg.get(c, c) for c in cols_vbg_tabla}
            ),
            use_container_width=True,
            height=280,
        )

# --- TAB 4: Respuesta institucional ---
with tab_resp:
    tr1, tr2 = st.columns(2, gap="medium")

    with tr1:
        st.markdown(
            "<div class='section-header'>Instancia de denuncia</div>"
            "<div class='section-subheader'>\u00bfD\u00f3nde report\u00f3 la v\u00edctima?</div>",
            unsafe_allow_html=True,
        )
        if "instancia_denuncia" in df_vf.columns:
            serie_inst = _explode_multiselect(df_vf, "instancia_denuncia")
            df_inst = serie_inst.value_counts().reset_index()
            df_inst.columns = ["instancia", "n"]
            fig_inst = px.bar(df_inst.sort_values("n"),
                              x="n", y="instancia", orientation="h",
                              color_discrete_sequence=[COLOR_PRIMARY],
                              text="n")
            fig_inst.update_layout(**_L(height=max(220, len(df_inst))*32+60),
                                   xaxis_title="V\u00edctimas", yaxis_title=None)
            fig_inst.update_traces(marker_line_width=0, textposition="outside", cliponaxis=False, textfont=dict(size=10, family="'DM Sans', sans-serif", color="#45556A"))
            st.plotly_chart(fig_inst, use_container_width=True)

    with tr2:
        st.markdown(
            "<div class='section-header'>Resultado del proceso</div>"
            "<div class='section-subheader'>Estado de la denuncia o reporte</div>",
            unsafe_allow_html=True,
        )
        if "resultado_denuncia" in df_vf.columns:
            df_res = df_vf["resultado_denuncia"].value_counts(dropna=False).reset_index()
            df_res.columns = ["resultado", "n"]
            df_res["resultado"] = df_res["resultado"].fillna("Sin dato")
            # CAMBIO: pie → barras horizontales (más legible con etiquetas largas)
            fig_res = px.bar(df_res.sort_values("n"),
                             x="n", y="resultado", orientation="h",
                             color_discrete_sequence=[
                                 COLOR_RIESGO_BAJO, COLOR_RIESGO_MEDIO,
                                 COLOR_RIESGO_ALTO, "#4A9BD4", "#8A9BAA"
                             ],
                             text="n")
            fig_res.update_layout(**_L(height=max(220, len(df_res))*32+60),
                                  xaxis_title="V\u00edctimas", yaxis_title=None)
            fig_res.update_traces(marker_line_width=0, textposition="outside", cliponaxis=False, textfont=dict(size=10, family="'DM Sans', sans-serif", color="#45556A"))
            st.plotly_chart(fig_res, use_container_width=True)

    st.markdown(
        "<div class='section-header' style='margin-top:8px;'>Medidas de protecci\u00f3n adoptadas</div>"
        "<div class='section-subheader'>V\u00edctimas con alguna medida registrada</div>",
        unsafe_allow_html=True,
    )
    if "medidas_proteccion" in df_vf.columns:
        df_mp = df_vf[df_vf["medidas_proteccion"].notna()][
            [c for c in ["nombre", "tipo_victima", "cargo_postula",
                         "medidas_proteccion", "resultado_denuncia"]
             if c in df_vf.columns]
        ]
        if df_mp.empty:
            st.info("No hay medidas de protecci\u00f3n registradas en la selecci\u00f3n actual.")
        else:
            label_map_mp = {
                "nombre":             "Nombre",
                "tipo_victima":       "Tipo",
                "cargo_postula":      "Cargo que postula",
                "medidas_proteccion": "Medidas de protecci\u00f3n",
                "resultado_denuncia": "Resultado",
            }
            st.dataframe(
                df_mp.rename(columns={c: label_map_mp.get(c, c) for c in df_mp.columns}),
                use_container_width=True,
                height=280,
            )


# --- TAB 5: Autoridades electorales ---
with tab_ae:
    FACTOR_AE = "Autoridades Electorales"
    df_ae = df_vf[
        df_vf["factor_diferencial"].str.contains(FACTOR_AE, case=False, na=False)
    ].copy() if "factor_diferencial" in df_vf.columns else pd.DataFrame()

    if df_ae.empty:
        st.info("No hay v\u00edctimas con factor diferencial 'Autoridades Electorales' en la selecci\u00f3n actual.")
    else:
        n_ae = len(df_ae)
        n_inc_ae = df_ae["num_serie_incidente"].nunique() if "num_serie_incidente" in df_ae.columns else 0
        orgs_ae = df_ae["org_politica"].dropna().nunique() if "org_politica" in df_ae.columns else 0

        ka1, ka2, ka3 = st.columns(3)
        for _col, _lbl, _val, _bc in [
            (ka1, "Autoridades afectadas",    n_ae,     COLOR_PRIMARY),
            (ka2, "Incidentes asociados",     n_inc_ae, COLOR_RIESGO_ALTO),
            (ka3, "Organizaciones afectadas", orgs_ae,  COLOR_ACCENT),
        ]:
            with _col:
                st.markdown(
                    "<div style='background:" + COLOR_SURFACE + "; border:1px solid " + COLOR_BORDER + ";"
                    " border-top:3px solid " + _bc + ";"
                    " border-radius:0; padding:16px 18px 14px 18px;'>"
                    "<div style='font-size:0.62rem; font-weight:700; letter-spacing:0.12em;"
                    " text-transform:uppercase; color:" + COLOR_TEXT_MUTED + "; margin-bottom:6px;'>"
                    + _lbl + "</div>"
                    "<div style='font-family:\"Source Serif 4\",Georgia,serif; font-size:2.2rem;"
                    " font-weight:600; color:" + _bc + ";"
                    " font-variant-numeric:tabular-nums; line-height:1.1;'>"
                    + str(_val) + "</div></div>",
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
        ae1, ae2 = st.columns(2, gap="medium")

        with ae1:
            st.markdown(
                '<div class="page-eyebrow">Organizaci\u00f3n</div>'
                '<div class="section-header">Ataques por organizaci\u00f3n electoral</div>'
                '<div class="section-subheader">ONPE, JNE y otras autoridades</div>',
                unsafe_allow_html=True,
            )
            if "org_politica" in df_ae.columns:
                df_ae_org = df_ae["org_politica"].fillna("Sin dato").value_counts().reset_index()
                df_ae_org.columns = ["org", "n"]
                fig_ae_org = px.bar(df_ae_org.sort_values("n"), x="n", y="org",
                                    orientation="h", color_discrete_sequence=[COLOR_PRIMARY], text="n")
                fig_ae_org.update_layout(**_L(height=max(220, len(df_ae_org)*30+60), xaxis_title="V\u00edctimas"))
                _bar(fig_ae_org)
                st.plotly_chart(fig_ae_org, use_container_width=True)

        with ae2:
            st.markdown(
                '<div class="page-eyebrow">Persona</div>'
                '<div class="section-header">Ataques por autoridad individual</div>'
                '<div class="section-subheader">Corvetto, Burneo y otras autoridades nominadas</div>',
                unsafe_allow_html=True,
            )
            if "nombre" in df_ae.columns:
                df_ae_nom = df_ae["nombre"].fillna("Sin dato").value_counts().reset_index()
                df_ae_nom.columns = ["nombre", "n"]
                fig_ae_nom = px.bar(df_ae_nom.sort_values("n").head(15),
                                    x="n", y="nombre", orientation="h",
                                    color_discrete_sequence=[COLOR_ACCENT], text="n")
                fig_ae_nom.update_layout(**_L(height=max(220, min(15, len(df_ae_nom))*30+60), xaxis_title="Incidentes"))
                _bar(fig_ae_nom)
                st.plotly_chart(fig_ae_nom, use_container_width=True)

        st.markdown(
            '<div class="page-eyebrow" style="margin-top:8px;">Tipolog\u00eda</div>'
            '<div class="section-header">Tipos de ataque contra autoridades electorales</div>',
            unsafe_allow_html=True,
        )
        col_ta = next((c for c in ["tipo_ataque_vic", "tipo_ataque"] if c in df_ae.columns), None)
        if col_ta:
            serie_ae_ta = _explode_multiselect(df_ae, col_ta)
            df_ae_ta = serie_ae_ta.value_counts().reset_index()
            df_ae_ta.columns = ["tipo", "n"]
            fig_ae_ta = px.bar(df_ae_ta.sort_values("n"), x="n", y="tipo",
                               orientation="h", color_discrete_sequence=[COLOR_RIESGO_ALTO], text="n")
            fig_ae_ta.update_layout(**_L(height=max(220, len(df_ae_ta)*28+60), xaxis_title="Frecuencia"))
            _bar(fig_ae_ta)
            st.plotly_chart(fig_ae_ta, use_container_width=True)

        st.markdown(
            '<div class="page-eyebrow" style="margin-top:8px;">Detalle</div>'
            '<div class="section-header">Resumen por autoridad electoral</div>'
            '<div class="section-subheader">N\u00famero de ataques y descripciones por persona u organizaci\u00f3n</div>',
            unsafe_allow_html=True,
        )
        cols_ae = [c for c in ["nombre", "org_politica", "cargo_postula", "tipo_victima",
                                "genero", "num_serie_incidente"] if c in df_ae.columns]
        if cols_ae:
            lm_ae = {"nombre": "Nombre / ID", "org_politica": "Organizaci\u00f3n",
                     "cargo_postula": "Cargo", "tipo_victima": "Tipo",
                     "genero": "G\u00e9nero", "num_serie_incidente": "N\u00b0 incidente"}
            df_ae_t = df_ae[cols_ae].copy()
            st.dataframe(
                df_ae_t.rename(columns={c: lm_ae.get(c, c) for c in df_ae_t.columns}),
                use_container_width=True,
                height=min(120 + len(df_ae_t)*35, 400),
                hide_index=True,
            )
            st.download_button(
                "\u2b07\ufe0f Descargar tabla (CSV)",
                data=df_ae_t.to_csv(index=False).encode("utf-8"),
                file_name="autoridades_electorales_ataques.csv",
                mime="text/csv", key="dl_ae",
            )

# -------------------------------------------------------
# SECTION: Footer
# -------------------------------------------------------
st.markdown(
    "<div class='page-footer'>"
    "<span>Monitor Electoral Per\u00fa 2026 \u00b7 " + APP_CONFIDENTIAL_LABEL + "</span>"
    "<span>" + APP_VERSION + " \u00b7 Fuente: ActivityInfo OACNUDH</span>"
    "</div>",
    unsafe_allow_html=True,
)
