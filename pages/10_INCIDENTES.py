# ============================================================
# pages/7_INCIDENTES.py — Monitor Electoral Perú 2026
# Módulo de violencia electoral — Panorama de incidentes.
# Patrones, distribuciones, mapa, línea de tiempo.
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
    COLOR_RIESGO_NONE,
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
    page_title="Incidentes · " + APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

if not st.session_state.get("autenticado", False):
    st.warning("Debes iniciar sesi\u00f3n primero.")
    st.stop()

# Verificación de contraseña adicional para módulo de violencia
_VIO_KEY = "violencia_auth"
if not st.session_state.get(_VIO_KEY, False):
    st.markdown(
        "<div style='max-width:420px; margin:60px auto; padding:36px 32px;"
        " background:" + COLOR_SURFACE + "; border:1px solid " + COLOR_BORDER + ";"
        " border-radius:10px; text-align:center;'>"
        "<div style='font-size:0.65rem; font-weight:700; letter-spacing:0.12em;"
        " text-transform:uppercase; color:" + COLOR_RIESGO_ALTO + "; margin-bottom:14px;'>"
        "Acceso restringido \u2014 M\u00f3dulo confidencial</div>"
        "<div style='font-size:1rem; font-weight:700; color:" + COLOR_TEXT_PRIMARY + "; margin-bottom:8px;'>"
        "Violencia Electoral</div>"
        "<div style='font-size:0.82em; color:" + COLOR_TEXT_SECONDARY + "; margin-bottom:0;'>"
        "Este m\u00f3dulo contiene informaci\u00f3n sensible sobre v\u00edctimas."
        " Requiere autorizaci\u00f3n adicional.</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        pw = st.text_input("Contrase\u00f1a del m\u00f3dulo",
                           type="password", label_visibility="collapsed",
                           placeholder="Contrase\u00f1a del m\u00f3dulo de violencia")
        if st.button("Acceder", use_container_width=True, type="primary"):
            try:
                if pw == st.secrets["violencia"]["password"]:
                    st.session_state[_VIO_KEY] = True
                    st.rerun()
                else:
                    st.error("Contrase\u00f1a incorrecta.")
            except KeyError:
                st.warning("\u2699\ufe0f Configura `[violencia] password` en secrets.toml")
    st.stop()

# -------------------------------------------------------
# SECTION: Carga de datos
# -------------------------------------------------------
with st.spinner("Cargando datos de violencia electoral..."):
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
        + "Incidentes</div>"
        + "<div style='font-size:0.82rem; color:" + COLOR_TEXT_SECONDARY + "; margin-top:2px;'>"
        + "Patrones, distribuciones y an\u00e1lisis de incidentes registrados \u00b7 "
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
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        regiones = ["Todas"] + sorted(df_inc["region"].dropna().unique().tolist())
        f_region = st.selectbox("Regi\u00f3n", regiones)
    with fc2:
        subprocesos = ["Todos"] + sorted(df_inc["subproceso_electoral"].dropna().unique().tolist())
        f_subproceso = st.selectbox("Sub-proceso electoral", subprocesos)
    with fc3:
        autores = ["Todos"] + sorted(df_inc["autor_tipo"].dropna().unique().tolist())
        f_autor = st.selectbox("Tipo de presunto autor", autores)
    with fc4:
        verificaciones = ["Todos"] + sorted(df_inc["estado_verificacion"].dropna().unique().tolist())
        f_verif = st.selectbox("Estado de verificaci\u00f3n", verificaciones)

# Aplicar filtros
df_f = df_inc.copy()
if f_region != "Todas":
    df_f = df_f[df_f["region"] == f_region]
if f_subproceso != "Todos":
    df_f = df_f[df_f["subproceso_electoral"] == f_subproceso]
if f_autor != "Todos":
    df_f = df_f[df_f["autor_tipo"] == f_autor]
if f_verif != "Todos":
    df_f = df_f[df_f["estado_verificacion"] == f_verif]

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

_kpi(k1, "Total incidentes", len(df_f))
_kpi(k2, "Con fuente directa",
     df_f["estado_verificacion"].str.contains("Fuente Directa", case=False, na=False).sum()
     if "estado_verificacion" in df_f.columns else 0,
     "verificaci\u00f3n primaria")
_kpi(k3, "Por verificar",
     df_f["estado_verificacion"].str.contains("Por Verificar", case=False, na=False).sum()
     if "estado_verificacion" in df_f.columns else 0,
     "pendientes",
     COLOR_RIESGO_ALTO)
_kpi(k4, "Con seguimiento OACNUDH",
     df_f["acciones_seguimiento"].notna().sum() if "acciones_seguimiento" in df_f.columns else 0,
     "incidentes con acci\u00f3n registrada")
_kpi(k5, "Regiones afectadas",
     df_f["region"].dropna().nunique(),
     "regiones distintas")

st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------
# SECTION: Helper — layout base sin fondo para gráficos
# Sobreescribe paper_bgcolor y plot_bgcolor de CHART_LAYOUT_BASE
# para que los gráficos floten sobre el fondo de la página.
# -------------------------------------------------------
_LAYOUT_TRANSP = {k: v for k, v in CHART_LAYOUT_BASE.items()}
_LAYOUT_TRANSP["paper_bgcolor"] = "rgba(0,0,0,0)"
_LAYOUT_TRANSP["plot_bgcolor"]  = "rgba(0,0,0,0)"

# -------------------------------------------------------
# SECTION: Fila 1 — línea de tiempo + sub-proceso electoral
# -------------------------------------------------------
row1_l, row1_r = st.columns([3, 2], gap="medium")

with row1_l:
    st.markdown(
        "<div class='section-header'>Incidentes por semana</div>"
        "<div class='section-subheader'>Evoluci\u00f3n temporal del n\u00famero de incidentes registrados</div>",
        unsafe_allow_html=True,
    )
    if "fecha" in df_f.columns and df_f["fecha"].notna().any():
        df_tiempo = (
            df_f.groupby("semana").size().reset_index(name="n")
            .sort_values("semana")
        )
        fig_tiempo = px.bar(
            df_tiempo, x="semana", y="n",
            color_discrete_sequence=[COLOR_PRIMARY],
            text="n",
        )
        fig_tiempo.update_layout(
            **_LAYOUT_TRANSP,
            height=CHART_HEIGHT_SMALL,
            xaxis_title=None, yaxis_title="Incidentes",
            bargap=0.25,
        )
        fig_tiempo.update_traces(
            marker_line_width=0,
            textposition="outside",
            textfont_size=10,
        )
        st.plotly_chart(fig_tiempo, use_container_width=True)
    else:
        st.info("Sin datos de fecha disponibles.")

with row1_r:
    st.markdown(
        "<div class='section-header'>Sub-proceso electoral</div>"
        "<div class='section-subheader'>Distribuci\u00f3n por tipo de competencia afectada</div>",
        unsafe_allow_html=True,
    )
    if "subproceso_electoral" in df_f.columns:
        df_sub = df_f["subproceso_electoral"].dropna().value_counts().reset_index()
        df_sub.columns = ["subproceso", "n"]
        fig_sub = px.bar(
            df_sub.sort_values("n"),
            x="n", y="subproceso", orientation="h",
            color_discrete_sequence=[COLOR_ACCENT],
            text="n",
        )
        fig_sub.update_layout(
            **_LAYOUT_TRANSP,
            height=CHART_HEIGHT_SMALL,
            xaxis_title="Incidentes", yaxis_title=None,
        )
        fig_sub.update_traces(
            marker_line_width=0,
            textposition="outside",
            textfont_size=10,
        )
        st.plotly_chart(fig_sub, use_container_width=True)

# -------------------------------------------------------
# SECTION: Fila 2 — tipos de ataque (explode) + forma de ataque (barras verticales)
# -------------------------------------------------------
row2_l, row2_r = st.columns([2, 2], gap="medium")

with row2_l:
    st.markdown(
        "<div class='section-header'>Tipos de ataque</div>"
        "<div class='section-subheader'>Un incidente puede tener m\u00faltiples tipos</div>",
        unsafe_allow_html=True,
    )
    if "tipo_ataque" in df_f.columns and df_f["tipo_ataque"].notna().any():
        serie_tipos = _explode_multiselect(df_f, "tipo_ataque")
        df_tipos = serie_tipos.value_counts().reset_index()
        df_tipos.columns = ["tipo", "n"]
        fig_tipos = px.bar(
            df_tipos.sort_values("n"),
            x="n", y="tipo", orientation="h",
            color_discrete_sequence=[COLOR_PRIMARY],
            text="n",
        )
        fig_tipos.update_layout(
            **_LAYOUT_TRANSP,
            height=max(280, len(df_tipos) * 28 + 60),
            xaxis_title="Frecuencia", yaxis_title=None,
        )
        fig_tipos.update_traces(
            marker_line_width=0,
            textposition="outside",
            textfont_size=10,
        )
        st.plotly_chart(fig_tipos, use_container_width=True)

with row2_r:
    st.markdown(
        "<div class='section-header'>Forma de ataque</div>"
        "<div class='section-subheader'>Modalidad a nivel del incidente</div>",
        unsafe_allow_html=True,
    )
    if "forma_ataque" in df_f.columns and df_f["forma_ataque"].notna().any():
        serie_forma = _explode_multiselect(df_f, "forma_ataque")
        df_forma = serie_forma.value_counts().reset_index()
        df_forma.columns = ["forma", "n"]

        # CAMBIO: pie chart → barras verticales (mejor comparabilidad entre categorías)
        fig_forma = px.bar(
            df_forma.sort_values("n", ascending=False),
            x="forma", y="n",
            color_discrete_sequence=[COLOR_ACCENT],
            text="n",
        )
        fig_forma.update_layout(
            **_LAYOUT_TRANSP,
            height=CHART_HEIGHT_SMALL,
            xaxis_title=None,
            yaxis_title="Frecuencia",
        )
        fig_forma.update_xaxes(
            tickangle=-30,
            tickfont=dict(size=10),
            showgrid=False,
        )
        fig_forma.update_traces(
            marker_line_width=0,
            textposition="outside",
            textfont_size=10,
        )
        st.plotly_chart(fig_forma, use_container_width=True)

# -------------------------------------------------------
# SECTION: Fila 3 — presunto autor + distribución regional
# -------------------------------------------------------
row3_l, row3_r = st.columns([2, 2], gap="medium")

with row3_l:
    st.markdown(
        "<div class='section-header'>Presunto autor</div>"
        "<div class='section-subheader'>Tipo y sub-tipo del agresor presunto</div>",
        unsafe_allow_html=True,
    )
    if "autor_tipo" in df_f.columns and df_f["autor_tipo"].notna().any():
        df_autor = df_f["autor_tipo"].value_counts().reset_index()
        df_autor.columns = ["tipo", "n"]
        color_map = {
            "Estado":                     COLOR_RIESGO_ALTO,
            "Actor pol\u00edtico":        COLOR_RIESGO_MEDIO,
            "Candidato":                  COLOR_RIESGO_MEDIO,
            "Candidato a la presidencia": COLOR_RIESGO_MEDIO,
            "Privado":                    COLOR_ACCENT,
        }
        fig_autor = px.bar(
            df_autor.sort_values("n"),
            x="n", y="tipo", orientation="h",
            color="tipo",
            color_discrete_map=color_map,
            text="n",
        )
        fig_autor.update_layout(
            **_LAYOUT_TRANSP,
            height=CHART_HEIGHT_SMALL,
            showlegend=False,
            xaxis_title="Incidentes", yaxis_title=None,
        )
        fig_autor.update_traces(
            marker_line_width=0,
            textposition="outside",
            textfont_size=10,
        )
        st.plotly_chart(fig_autor, use_container_width=True)

with row3_r:
    st.markdown(
        "<div class='section-header'>Distribuci\u00f3n regional</div>"
        "<div class='section-subheader'>Incidentes por regi\u00f3n (con geograf\u00eda registrada)</div>",
        unsafe_allow_html=True,
    )
    if "region" in df_f.columns and df_f["region"].notna().any():
        df_reg = df_f["region"].dropna().value_counts().reset_index()
        df_reg.columns = ["region", "n"]
        fig_reg = px.bar(
            df_reg.sort_values("n"),
            x="n", y="region", orientation="h",
            color_discrete_sequence=["#4A9BD4"],
            text="n",
        )
        fig_reg.update_layout(
            **_LAYOUT_TRANSP,
            height=CHART_HEIGHT_SMALL,
            xaxis_title="Incidentes", yaxis_title=None,
        )
        fig_reg.update_traces(
            marker_line_width=0,
            textposition="outside",
            textfont_size=10,
        )
        st.plotly_chart(fig_reg, use_container_width=True)

        sin_geo = df_f["region"].isna().sum()
        if sin_geo > 0:
            st.markdown(
                "<div class='nota-info'>"
                + str(sin_geo)
                + " incidentes sin regi\u00f3n registrada"
                " (incidentes online o ubicaci\u00f3n no disponible)."
                + "</div>",
                unsafe_allow_html=True,
            )

# -------------------------------------------------------
# SECTION: Listado de incidentes — tabla clickeable + panel de detalle
#
# Patrón idéntico a 2_CANDIDATOS.py:
#   1. Tabla con st.dataframe y columna "num_serie" como selector
#   2. st.selectbox para elegir el incidente
#   3. Panel de detalle se despliega debajo al seleccionar
# -------------------------------------------------------
st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-header'>Listado de incidentes</div>"
    "<div class='section-subheader'>"
    "Selecciona un incidente de la tabla para ver su ficha completa"
    "</div>",
    unsafe_allow_html=True,
)

# Construir tabla de selección
cols_tabla = [c for c in ["num_serie", "fecha", "region", "tipo_ataque",
                           "forma_ataque", "subproceso_electoral",
                           "autor_tipo", "estado_verificacion"]
              if c in df_f.columns]

df_tabla = df_f[cols_tabla].copy()
if "fecha" in df_tabla.columns:
    df_tabla["fecha"] = df_tabla["fecha"].dt.strftime("%d/%m/%Y")

# Labels de columna legibles
label_map = {
    "num_serie":            "N\u00b0 serie",
    "fecha":                "Fecha",
    "region":               "Regi\u00f3n",
    "tipo_ataque":          "Tipo de ataque",
    "forma_ataque":         "Forma",
    "subproceso_electoral": "Sub-proceso",
    "autor_tipo":           "Autor (tipo)",
    "estado_verificacion":  "Verificaci\u00f3n",
}
df_tabla = df_tabla.rename(columns={c: label_map.get(c, c) for c in df_tabla.columns})
st.dataframe(df_tabla, use_container_width=True, height=300)

# Selector de incidente (usa num_serie como clave)
series_disponibles = df_f["num_serie"].dropna().unique().tolist() \
    if "num_serie" in df_f.columns else []

if not series_disponibles:
    st.info("No hay incidentes disponibles con los filtros aplicados.")
else:
    # Inicializar sesión si no existe
    if "incidente_sel" not in st.session_state:
        st.session_state["incidente_sel"] = None

    serie_sel = st.selectbox(
        "Selecciona un incidente para ver su ficha completa",
        options=["— Selecciona un incidente —"] + series_disponibles,
        key="incidente_sel_box",
    )

    # -------------------------------------------------------
    # SECTION: Panel de ficha de incidente
    # Se despliega debajo de la tabla al seleccionar un número de serie.
    # -------------------------------------------------------
    if serie_sel != "— Selecciona un incidente —":
        row_sel = df_f[df_f["num_serie"] == serie_sel]
        if row_sel.empty:
            st.warning("No se encontraron datos para este incidente.")
        else:
            row = row_sel.iloc[0]

            fecha_disp  = row["fecha"].strftime("%d/%m/%Y") \
                          if pd.notna(row.get("fecha")) else "\u2014"
            region_disp = str(row.get("region") or "Sin regi\u00f3n registrada")
            tipo_disp   = str(row.get("tipo_ataque") or "\u2014")

            st.markdown(
                "<div style='border-top:2px solid " + COLOR_BORDER + "; margin:24px 0 20px 0;'></div>",
                unsafe_allow_html=True,
            )

            # Encabezado del incidente
            st.markdown(
                "<div style='margin-bottom:20px;'>"
                "<div style='font-size:0.63rem; font-weight:700; letter-spacing:0.12em;"
                " text-transform:uppercase; color:" + COLOR_ACCENT + "; margin-bottom:6px;'>"
                "Ficha del incidente</div>"
                "<div style='font-size:1.35rem; font-weight:700; color:" + COLOR_TEXT_PRIMARY + ";"
                " margin:0 0 4px 0; letter-spacing:-0.02em; line-height:1.2;'>"
                + str(serie_sel) + " \u00b7 " + fecha_disp + "</div>"
                "<div style='font-size:0.85rem; color:" + COLOR_TEXT_SECONDARY + "; margin:0;'>"
                + region_disp + " \u00b7 " + tipo_disp
                + "</div>"
                "</div>",
                unsafe_allow_html=True,
            )

            col_desc, col_meta = st.columns([3, 2], gap="medium")

            # --- Descripción y fuentes ---
            with col_desc:
                descripcion = str(row.get("descripcion") or "Sin descripci\u00f3n registrada.")
                st.markdown(
                    "<div style='background:" + COLOR_SURFACE + "; border:1px solid " + COLOR_BORDER + ";"
                    " border-radius:8px; padding:20px 22px;'>"
                    "<div style='font-size:0.60rem; font-weight:700; letter-spacing:0.10em;"
                    " text-transform:uppercase; color:" + COLOR_TEXT_MUTED + "; margin-bottom:10px;'>"
                    "Descripci\u00f3n de los hechos</div>"
                    "<div style='font-size:0.85em; color:" + COLOR_TEXT_SECONDARY + ";"
                    " line-height:1.65; white-space:pre-wrap;'>"
                    + descripcion
                    + "</div>"
                    "</div>",
                    unsafe_allow_html=True,
                )
                st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
                fuentes_html = row.get("fuentes_html", "Sin fuentes registradas.")
                st.markdown(
                    "<div style='background:" + COLOR_SURFACE + "; border:1px solid " + COLOR_BORDER + ";"
                    " border-radius:8px; padding:18px 22px;'>"
                    "<div style='font-size:0.60rem; font-weight:700; letter-spacing:0.10em;"
                    " text-transform:uppercase; color:" + COLOR_TEXT_MUTED + "; margin-bottom:10px;'>"
                    "Fuentes</div>"
                    "<div style='font-size:0.83em; color:" + COLOR_TEXT_SECONDARY + "; line-height:1.7;'>"
                    + fuentes_html
                    + "</div>"
                    "</div>",
                    unsafe_allow_html=True,
                )

            # --- Metadatos y seguimiento ---
            with col_meta:
                campos_meta = [
                    ("Lugar",            row.get("lugar")),
                    ("Provincia",        row.get("provincia")),
                    ("Distrito",         row.get("distrito")),
                    ("Forma de ataque",  row.get("forma_ataque")),
                    ("Proceso",          row.get("proceso_electoral")),
                    ("Sub-proceso",      row.get("subproceso_electoral")),
                    ("Autor (tipo)",     row.get("autor_tipo")),
                    ("Autor (subtipo)",  row.get("autor_subtipo")),
                    ("N\u00b0 agresores", row.get("num_agresores")),
                    ("Verificaci\u00f3n", row.get("estado_verificacion")),
                ]
                filas_meta = ""
                for label, val in campos_meta:
                    if pd.notna(val) and str(val).strip() and str(val) not in ("nan", "None"):
                        filas_meta += (
                            "<tr>"
                            "<td style='color:" + COLOR_TEXT_MUTED + "; padding-right:14px;"
                            " white-space:nowrap; font-weight:500; padding-bottom:4px;"
                            " vertical-align:top;'>" + label + "</td>"
                            "<td style='color:" + COLOR_TEXT_PRIMARY + "; padding-bottom:4px;"
                            " line-height:1.45;'>" + str(val) + "</td>"
                            "</tr>"
                        )

                st.markdown(
                    "<div style='background:" + COLOR_SURFACE + "; border:1px solid " + COLOR_BORDER + ";"
                    " border-radius:8px; padding:20px 22px;'>"
                    "<div style='font-size:0.60rem; font-weight:700; letter-spacing:0.10em;"
                    " text-transform:uppercase; color:" + COLOR_TEXT_MUTED + "; margin-bottom:14px;'>"
                    "Datos del incidente</div>"
                    "<table style='width:100%; border-collapse:collapse; font-size:0.84rem; line-height:1.7;'>"
                    + filas_meta +
                    "</table>"
                    "</div>",
                    unsafe_allow_html=True,
                )

                # Seguimiento OACNUDH (si existe)
                seguimiento = row.get("acciones_seguimiento")
                if pd.notna(seguimiento) and str(seguimiento).strip():
                    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
                    st.markdown(
                        "<div style='background:" + COLOR_RIESGO_BAJO_BG + ";"
                        " border-left:3px solid " + COLOR_RIESGO_BAJO + ";"
                        " border-radius:0 6px 6px 0; padding:14px 16px;'>"
                        "<div style='font-size:0.60rem; font-weight:700; letter-spacing:0.10em;"
                        " text-transform:uppercase; color:" + COLOR_RIESGO_BAJO + "; margin-bottom:6px;'>"
                        "Seguimiento OACNUDH</div>"
                        "<div style='font-size:0.83em; color:" + COLOR_TEXT_SECONDARY + "; line-height:1.55;'>"
                        + str(seguimiento) +
                        "</div>"
                        "</div>",
                        unsafe_allow_html=True,
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
