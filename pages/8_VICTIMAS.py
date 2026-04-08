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
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_BACKGROUND, COLOR_SURFACE,
    COLOR_BORDER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_RIESGO_ALTO, COLOR_RIESGO_ALTO_BG,
    COLOR_RIESGO_MEDIO, COLOR_RIESGO_MEDIO_BG,
    COLOR_RIESGO_BAJO, COLOR_RIESGO_BAJO_BG,
    CHART_HEIGHT, CHART_HEIGHT_SMALL, CHART_LAYOUT_BASE, GLOBAL_CSS,
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
        "<div style='margin-bottom:8px;'>"
        + "<div style='font-size:0.68rem; font-weight:600; letter-spacing:0.08em;"
        + " text-transform:uppercase; color:" + COLOR_TEXT_MUTED + "; margin-bottom:2px;'>"
        + "MONITOR ELECTORAL PER\u00da 2026 \u00b7 M\u00f3dulo de Violencia Electoral</div>"
        + "<div style='font-size:1.55rem; font-weight:700; color:" + COLOR_TEXT_PRIMARY + "; margin:0;'>"
        + "Presuntas v\u00edctimas</div>"
        + "<div style='font-size:0.82rem; color:" + COLOR_TEXT_SECONDARY + "; margin-top:2px;'>"
        + "Perfiles, interseccionalidad y respuesta institucional \u00b7 "
        + APP_VERSION + "</div>"
        + "</div>",
        unsafe_allow_html=True,
    )
with col_btn:
    st.markdown("<div style='padding-top:24px;'>", unsafe_allow_html=True)
    if st.button("Actualizar datos", use_container_width=True):
        limpiar_cache_violencia()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    "<div style='border-top:2px solid " + COLOR_BORDER + "; margin-bottom:20px;'></div>",
    unsafe_allow_html=True,
)

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

def _kpi(col, label, value, sub=None, color=COLOR_TEXT_PRIMARY):
    with col:
        st.markdown(
            "<div style='background:" + COLOR_SURFACE + "; border:1px solid " + COLOR_BORDER + ";"
            " border-radius:6px; padding:16px 18px 14px 18px;'>"
            "<div style='font-size:0.70rem; font-weight:700; letter-spacing:0.07em;"
            " text-transform:uppercase; color:" + COLOR_TEXT_MUTED + "; margin-bottom:4px;'>"
            + label + "</div>"
            "<div style='font-size:1.9rem; font-weight:700; color:" + color + ";"
            " font-variant-numeric:tabular-nums; line-height:1.1;'>"
            + str(value) + "</div>"
            + ("<div style='font-size:0.75rem; color:" + COLOR_TEXT_SECONDARY + "; margin-top:3px;'>"
               + str(sub) + "</div>" if sub else "")
            + "</div>",
            unsafe_allow_html=True,
        )

n_vf          = len(df_vf)
n_candidatas  = df_vf["es_candidata"].sum()  if "es_candidata"          in df_vf.columns else 0
n_vbg         = df_vf["tiene_vbg"].sum()      if "tiene_vbg"             in df_vf.columns else 0
n_factor      = df_vf["tiene_factor_diferencial"].sum() \
                if "tiene_factor_diferencial" in df_vf.columns else 0
n_sin_denuncia = (df_vf["instancia_denuncia"] == "No se ha hecho una denuncia/reporte formal").sum() \
                  if "instancia_denuncia" in df_vf.columns else 0

_kpi(k1, "Total v\u00edctimas", n_vf)
_kpi(k2, "Candidatas/os", n_candidatas,
     f"{round(n_candidatas/n_vf*100,1) if n_vf else 0}% del total")
_kpi(k3, "Con indicadores VBG", n_vbg,
     f"{round(n_vbg/n_vf*100,1) if n_vf else 0}% del total",
     COLOR_RIESGO_ALTO)
_kpi(k4, "Con factor diferencial", n_factor,
     f"{round(n_factor/n_vf*100,1) if n_vf else 0}% del total")
_kpi(k5, "Sin denuncia formal", n_sin_denuncia,
     f"{round(n_sin_denuncia/n_vf*100,1) if n_vf else 0}% del total",
     COLOR_RIESGO_MEDIO)

st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------
# SECTION: Tabs de análisis
# -------------------------------------------------------
tab_perfil, tab_intersec, tab_vbg, tab_resp = st.tabs([
    "Perfil predominante",
    "Interseccionalidad",
    "Violencia de g\u00e9nero",
    "Respuesta institucional",
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
                            color_discrete_sequence=[COLOR_PRIMARY])
            fig_tv.update_layout(**{k: v for k, v in CHART_LAYOUT_BASE.items()},
                                 height=220, xaxis_title="V\u00edctimas",
                                 yaxis_title=None, showlegend=False)
            fig_tv.update_traces(marker_line_width=0)
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
                            color_discrete_sequence=[COLOR_ACCENT])
            fig_fd.update_layout(**{k: v for k, v in CHART_LAYOUT_BASE.items()},
                                 height=max(220, len(df_fd)*30+60),
                                 xaxis_title="V\u00edctimas", yaxis_title=None)
            fig_fd.update_traces(marker_line_width=0)
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
                                   color_discrete_sequence=["#4A9BD4"])
                fig_cargo.update_layout(**{k: v for k, v in CHART_LAYOUT_BASE.items()},
                                        height=220, xaxis_title="V\u00edctimas",
                                        yaxis_title=None)
                fig_cargo.update_traces(marker_line_width=0)
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
                                  color_discrete_sequence=["#6B4FA0"])
                fig_part.update_layout(**{k: v for k, v in CHART_LAYOUT_BASE.items()},
                                       height=max(220, len(df_part)*30+60),
                                       xaxis_title="V\u00edctimas", yaxis_title=None)
                fig_part.update_traces(marker_line_width=0)
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
                         color_discrete_sequence=[COLOR_RIESGO_ALTO])
        fig_obj.update_layout(**{k: v for k, v in CHART_LAYOUT_BASE.items()},
                              height=max(220, len(df_obj)*30+60),
                              xaxis_title="V\u00edctimas", yaxis_title=None)
        fig_obj.update_traces(marker_line_width=0)
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
                "Masculino": COLOR_PRIMARY,
                "Femenino":  COLOR_RIESGO_MEDIO,
                "No binario/gender queer": COLOR_ACCENT,
                "Sin dato":  "#8A9BAA",
            }
            fig_gen = px.pie(df_gen, names="genero", values="n",
                             color="genero", color_discrete_map=color_gen, hole=0.4)
            fig_gen.update_layout(**{k: v for k, v in CHART_LAYOUT_BASE.items()},
                                  height=260)
            fig_gen.update_traces(textinfo="percent+label", textfont_size=11)
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
                               color_discrete_sequence=["#1E8A4A"])
            fig_etnia.update_layout(**{k: v for k, v in CHART_LAYOUT_BASE.items()},
                                    height=260, xaxis_title="V\u00edctimas",
                                    yaxis_title=None)
            fig_etnia.update_traces(marker_line_width=0)
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
                              color_discrete_sequence=[COLOR_ACCENT])
            fig_edad.update_layout(**{k: v for k, v in CHART_LAYOUT_BASE.items()},
                                   height=240, xaxis_title=None,
                                   yaxis_title="V\u00edctimas")
            fig_edad.update_traces(marker_line_width=0)
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
                               ])
            fig_cross.update_layout(**{k: v for k, v in CHART_LAYOUT_BASE.items()},
                                    height=240, xaxis_title=None,
                                    yaxis_title="V\u00edctimas")
            fig_cross.update_traces(marker_line_width=0)
            st.plotly_chart(fig_cross, use_container_width=True)

    # Personas trans
    if "es_trans" in df_vf.columns:
        n_trans = (df_vf["es_trans"] == "Si").sum()
        if n_trans > 0:
            st.markdown(
                "<div class='nota-warning'>"
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
                                  color_discrete_sequence=[COLOR_RIESGO_ALTO])
                fig_tvbg.update_layout(**{k: v for k, v in CHART_LAYOUT_BASE.items()},
                                       height=max(220, len(df_tvbg)*30+60),
                                       xaxis_title="V\u00edctimas", yaxis_title=None)
                fig_tvbg.update_traces(marker_line_width=0)
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
                                  color_discrete_sequence=[COLOR_RIESGO_MEDIO])
                fig_evbg.update_layout(**{k: v for k, v in CHART_LAYOUT_BASE.items()},
                                       height=max(220, len(df_evbg)*30+60),
                                       xaxis_title="V\u00edctimas", yaxis_title=None)
                fig_evbg.update_traces(marker_line_width=0)
                st.plotly_chart(fig_evbg, use_container_width=True)

        # Tabla VBG
        st.markdown(
            "<div class='section-header' style='margin-top:8px;'>V\u00edctimas con VBG</div>",
            unsafe_allow_html=True,
        )
        cols_vbg_tabla = [c for c in ["nombre", "genero", "es_trans", "cargo_postula",
                                      "tipo_vbg", "elementos_vbg", "num_serie_incidente"]
                          if c in df_vbg.columns]
        st.dataframe(df_vbg[cols_vbg_tabla].rename(
            columns={c: c.replace("_", " ").title() for c in cols_vbg_tabla}
        ), use_container_width=True, height=280)

# --- TAB 4: Respuesta institucional ---
with tab_resp:
    tr1, tr2 = st.columns(2, gap="medium")

    with tr1:
        st.markdown(
            "<div class='section-header'>Instancia de denuncia</div>"
            "<div class='section-subheader'>\u00bfDonde report\u00f3 la v\u00edctima?</div>",
            unsafe_allow_html=True,
        )
        if "instancia_denuncia" in df_vf.columns:
            serie_inst = _explode_multiselect(df_vf, "instancia_denuncia")
            df_inst = serie_inst.value_counts().reset_index()
            df_inst.columns = ["instancia", "n"]
            color_inst = df_inst["instancia"].apply(
                lambda x: COLOR_RIESGO_ALTO
                if "no se ha hecho" in str(x).lower()
                else COLOR_RIESGO_BAJO
            ).tolist()
            fig_inst = px.bar(df_inst.sort_values("n"),
                              x="n", y="instancia", orientation="h",
                              color_discrete_sequence=[COLOR_PRIMARY])
            fig_inst.update_layout(**{k: v for k, v in CHART_LAYOUT_BASE.items()},
                                   height=max(220, len(df_inst)*32+60),
                                   xaxis_title="V\u00edctimas", yaxis_title=None)
            fig_inst.update_traces(marker_line_width=0)
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
            fig_res = px.pie(df_res, names="resultado", values="n",
                             color_discrete_sequence=[
                                 COLOR_RIESGO_BAJO, COLOR_RIESGO_MEDIO,
                                 COLOR_RIESGO_ALTO, "#4A9BD4", "#8A9BAA"
                             ], hole=0.4)
            fig_res.update_layout(**{k: v for k, v in CHART_LAYOUT_BASE.items()},
                                  height=280)
            fig_res.update_traces(textinfo="percent+label", textfont_size=11)
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
            st.dataframe(df_mp.rename(
                columns={c: c.replace("_", " ").title() for c in df_mp.columns}
            ), use_container_width=True, height=280)

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
