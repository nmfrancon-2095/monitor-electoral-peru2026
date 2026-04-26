# ============================================================
# pages/1_OVERVIEW.py — Monitor Electoral Perú 2026
# Rediseño v3.0 — "Forensic Editorial"
#
# Orden narrativo:
#   Banda 1: KPIs principales
#   Banda 2: Panel de riesgo (niveles + partidos)
#   Banda 3: Inteligencia legislativa (votos por ley + cards destacadas)
#   Banda 4: Geografía + REINFO (contexto)
#
# Cambios respecto a versión anterior:
#   - Todo el HTML por concatenación (+), sin f-strings multilínea
#   - Mapa choropleth de riesgo (% candidatos riesgo alto por depto)
#     con GeoJSON embebido (sin dependencia externa)
#   - Barras horizontales con cornerradius=6 (estilo editorial)
#   - KPIs de leyes destacadas en columna lateral junto al gráfico
#   - Lede editorial con contenido (no vacío)
#   - border-radius:0 en todas las cards (sistema v3 estricto)
# ============================================================

import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    APP_TITLE, APP_CONFIDENTIAL_LABEL, APP_ICON, APP_VERSION,
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_BACKGROUND, COLOR_SURFACE,
    COLOR_BORDER, COLOR_BORDER_SOFT, COLOR_GOLD,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_RIESGO_ALTO, COLOR_RIESGO_ALTO_BG,
    COLOR_RIESGO_MEDIO, COLOR_RIESGO_MEDIO_BG,
    COLOR_RIESGO_BAJO, COLOR_RIESGO_BAJO_BG,
    COLOR_RIESGO_NONE, COLOR_REINFO,
    COLOR_BLOQUE, BAR_CORNER_RADIUS,
    CHART_HEIGHT, CHART_HEIGHT_SMALL, CHART_LAYOUT_BASE,
    REGIONES_PRIORITARIAS, LEYES_COLS, GLOBAL_CSS,
    SCORE_ALTO_MIN, SCORE_MEDIO_MIN,
)

from data_loader import (
    cargar_candidatos, cargar_votaciones, cargar_reinfo,
    cargar_leyes, resumen_kpis, candidatos_con_flags,
)

FONT_SERIF = "'Source Serif 4', Georgia, 'Times New Roman', serif"
FONT_SANS  = "'DM Sans', system-ui, -apple-system, sans-serif"

# -------------------------------------------------------
# GeoJSON embebido — departamentos de Perú
# Polígonos simplificados (Natural Earth / GADM public domain)
# Clave de match: propiedad "NOMBDEP" en mayúsculas
# Equivalente a los valores de df['region'] en 01_CANDIDATOS
# -------------------------------------------------------
PERU_GEOJSON = {"type":"FeatureCollection","features":[{"type":"Feature","id":"AMAZONAS","properties":{"NOMBDEP":"AMAZONAS"},"geometry":{"type":"Polygon","coordinates":[[[-78.7,2.0],[-78.4,2.5],[-77.9,3.1],[-77.5,3.0],[-77.0,2.6],[-76.8,2.3],[-76.3,2.4],[-75.9,2.2],[-75.6,1.9],[-75.3,1.6],[-75.5,1.2],[-75.8,0.9],[-76.5,0.9],[-77.0,1.3],[-77.3,1.5],[-77.5,1.5],[-77.8,1.8],[-78.3,2.0],[-78.7,2.0]]]}},{"type":"Feature","id":"ANCASH","properties":{"NOMBDEP":"ANCASH"},"geometry":{"type":"Polygon","coordinates":[[[-77.2,-8.0],[-76.7,-8.1],[-76.5,-8.4],[-76.2,-8.7],[-76.4,-9.0],[-76.6,-9.3],[-76.9,-9.6],[-77.1,-9.9],[-77.4,-10.2],[-77.7,-10.4],[-78.1,-10.6],[-78.3,-10.2],[-78.5,-9.8],[-78.5,-9.3],[-78.4,-9.0],[-78.0,-8.7],[-77.7,-8.4],[-77.5,-8.2],[-77.2,-8.0]]]}},{"type":"Feature","id":"APURIMAC","properties":{"NOMBDEP":"APURIMAC"},"geometry":{"type":"Polygon","coordinates":[[[-72.6,-13.2],[-72.2,-13.3],[-71.8,-13.5],[-71.5,-13.8],[-71.3,-14.1],[-71.1,-14.4],[-71.3,-14.6],[-71.6,-14.8],[-72.1,-14.9],[-72.5,-14.8],[-72.9,-14.6],[-73.1,-14.4],[-73.3,-14.1],[-73.3,-13.7],[-73.1,-13.5],[-72.8,-13.3],[-72.6,-13.2]]]}},{"type":"Feature","id":"AREQUIPA","properties":{"NOMBDEP":"AREQUIPA"},"geometry":{"type":"Polygon","coordinates":[[[-74.3,-14.8],[-73.9,-14.9],[-73.5,-15.1],[-73.1,-15.2],[-72.7,-15.4],[-72.4,-15.6],[-72.1,-15.7],[-71.8,-16.0],[-71.5,-16.2],[-71.3,-16.5],[-71.1,-16.8],[-71.0,-17.1],[-71.0,-17.5],[-71.2,-17.7],[-71.6,-17.9],[-72.0,-18.0],[-72.5,-18.0],[-72.9,-17.8],[-73.2,-17.5],[-73.5,-17.2],[-73.7,-16.9],[-74.0,-16.5],[-74.2,-16.2],[-74.3,-15.8],[-74.3,-15.4],[-74.3,-14.8]]]}},{"type":"Feature","id":"AYACUCHO","properties":{"NOMBDEP":"AYACUCHO"},"geometry":{"type":"Polygon","coordinates":[[[-74.9,-12.4],[-74.6,-12.5],[-74.2,-12.6],[-73.8,-12.7],[-73.5,-12.9],[-73.3,-13.1],[-73.0,-13.3],[-72.8,-13.6],[-72.7,-13.9],[-72.7,-14.2],[-72.7,-14.5],[-72.8,-14.8],[-73.0,-15.1],[-73.2,-15.3],[-73.5,-15.4],[-73.8,-15.4],[-74.1,-15.4],[-74.4,-15.2],[-74.7,-15.0],[-74.8,-14.8],[-75.0,-14.5],[-75.0,-14.2],[-74.9,-13.9],[-74.8,-13.6],[-74.6,-13.4],[-74.9,-12.4]]]}},{"type":"Feature","id":"CAJAMARCA","properties":{"NOMBDEP":"CAJAMARCA"},"geometry":{"type":"Polygon","coordinates":[[[-79.5,-4.5],[-79.1,-4.5],[-78.7,-4.6],[-78.4,-4.6],[-78.0,-4.7],[-77.8,-4.8],[-77.6,-4.9],[-77.4,-5.0],[-77.3,-5.2],[-77.1,-5.4],[-77.1,-5.6],[-77.2,-6.0],[-77.3,-6.2],[-77.5,-6.4],[-77.7,-6.6],[-78.0,-6.8],[-78.2,-6.9],[-78.5,-6.9],[-78.8,-6.9],[-79.1,-6.9],[-79.3,-6.8],[-79.5,-6.6],[-79.7,-6.4],[-79.8,-6.2],[-79.8,-5.9],[-79.8,-5.7],[-79.7,-5.4],[-79.6,-5.2],[-79.5,-4.5]]]}},{"type":"Feature","id":"CALLAO","properties":{"NOMBDEP":"CALLAO"},"geometry":{"type":"Polygon","coordinates":[[[-77.22,-12.0],[-77.02,-12.0],[-77.0,-12.07],[-77.06,-12.14],[-77.16,-12.13],[-77.22,-12.06],[-77.22,-12.0]]]}},{"type":"Feature","id":"CUSCO","properties":{"NOMBDEP":"CUSCO"},"geometry":{"type":"Polygon","coordinates":[[[-71.4,-13.2],[-71.5,-13.5],[-71.6,-13.8],[-71.6,-14.1],[-71.5,-14.4],[-71.4,-14.6],[-71.4,-14.9],[-71.5,-15.2],[-71.7,-15.4],[-71.9,-15.6],[-72.2,-15.7],[-72.5,-15.7],[-72.8,-15.5],[-73.1,-15.3],[-73.3,-15.0],[-73.5,-14.7],[-73.6,-14.3],[-73.5,-14.0],[-73.3,-13.7],[-73.0,-13.5],[-72.8,-13.3],[-72.5,-13.1],[-72.2,-13.0],[-71.9,-12.9],[-71.6,-12.8],[-71.3,-12.6],[-71.1,-12.6],[-71.3,-12.9],[-71.4,-13.2]]]}},{"type":"Feature","id":"HUANCAVELICA","properties":{"NOMBDEP":"HUANCAVELICA"},"geometry":{"type":"Polygon","coordinates":[[[-75.6,-12.0],[-75.3,-12.0],[-74.9,-12.1],[-74.6,-12.2],[-74.3,-12.3],[-74.1,-12.5],[-73.9,-12.7],[-73.8,-13.0],[-73.8,-13.2],[-73.9,-13.5],[-74.1,-13.7],[-74.3,-13.8],[-74.6,-13.9],[-74.9,-13.9],[-75.2,-13.9],[-75.4,-13.7],[-75.6,-13.6],[-75.8,-13.3],[-75.8,-13.1],[-75.8,-12.8],[-75.6,-12.6],[-75.4,-12.3],[-75.6,-12.0]]]}},{"type":"Feature","id":"HUANUCO","properties":{"NOMBDEP":"HUANUCO"},"geometry":{"type":"Polygon","coordinates":[[[-76.7,-8.4],[-76.4,-8.5],[-76.1,-8.6],[-75.8,-8.7],[-75.6,-8.9],[-75.5,-9.2],[-75.4,-9.4],[-75.5,-9.7],[-75.6,-9.9],[-75.8,-10.2],[-76.1,-10.3],[-76.4,-10.4],[-76.7,-10.4],[-77.0,-10.3],[-77.2,-10.2],[-77.4,-9.9],[-77.6,-9.7],[-77.6,-9.4],[-77.6,-9.2],[-77.4,-8.9],[-77.3,-8.7],[-77.0,-8.6],[-76.7,-8.4]]]}},{"type":"Feature","id":"ICA","properties":{"NOMBDEP":"ICA"},"geometry":{"type":"Polygon","coordinates":[[[-76.1,-13.1],[-75.8,-13.2],[-75.5,-13.3],[-75.3,-13.5],[-75.1,-13.7],[-74.9,-13.9],[-74.8,-14.2],[-74.8,-14.5],[-74.9,-14.7],[-75.1,-15.0],[-75.3,-15.1],[-75.6,-15.2],[-75.8,-15.2],[-76.1,-15.2],[-76.4,-15.0],[-76.6,-14.8],[-76.7,-14.5],[-76.7,-14.2],[-76.6,-13.9],[-76.4,-13.7],[-76.2,-13.5],[-76.1,-13.1]]]}},{"type":"Feature","id":"JUNIN","properties":{"NOMBDEP":"JUNIN"},"geometry":{"type":"Polygon","coordinates":[[[-75.6,-10.5],[-75.3,-10.6],[-75.0,-10.7],[-74.8,-10.8],[-74.6,-11.0],[-74.4,-11.2],[-74.4,-11.5],[-74.4,-11.7],[-74.5,-12.0],[-74.7,-12.2],[-74.9,-12.3],[-75.1,-12.4],[-75.4,-12.4],[-75.7,-12.3],[-75.9,-12.2],[-76.1,-12.0],[-76.2,-11.8],[-76.2,-11.5],[-76.1,-11.3],[-75.8,-11.1],[-75.6,-10.5]]]}},{"type":"Feature","id":"LA LIBERTAD","properties":{"NOMBDEP":"LA LIBERTAD"},"geometry":{"type":"Polygon","coordinates":[[[-79.7,-6.9],[-79.4,-7.0],[-79.0,-7.1],[-78.7,-7.1],[-78.4,-7.2],[-78.1,-7.3],[-77.8,-7.4],[-77.6,-7.6],[-77.4,-7.7],[-77.3,-7.9],[-77.3,-8.1],[-77.4,-8.4],[-77.5,-8.6],[-77.8,-8.8],[-78.1,-9.1],[-78.3,-9.1],[-78.6,-9.1],[-78.9,-9.0],[-79.1,-8.9],[-79.3,-8.7],[-79.4,-8.5],[-79.5,-8.2],[-79.5,-8.0],[-79.7,-6.9]]]}},{"type":"Feature","id":"LAMBAYEQUE","properties":{"NOMBDEP":"LAMBAYEQUE"},"geometry":{"type":"Polygon","coordinates":[[[-80.6,-5.5],[-80.3,-5.5],[-80.1,-5.6],[-79.8,-5.7],[-79.5,-5.8],[-79.3,-5.9],[-79.1,-6.1],[-78.9,-6.3],[-78.8,-6.5],[-78.8,-6.7],[-78.8,-6.9],[-78.9,-7.2],[-79.0,-7.3],[-79.3,-7.5],[-79.5,-7.5],[-79.8,-7.5],[-80.0,-7.5],[-80.2,-7.4],[-80.4,-7.2],[-80.5,-7.0],[-80.5,-6.8],[-80.5,-6.5],[-80.5,-6.3],[-80.4,-6.1],[-80.6,-5.5]]]}},{"type":"Feature","id":"LIMA","properties":{"NOMBDEP":"LIMA"},"geometry":{"type":"Polygon","coordinates":[[[-77.6,-10.5],[-77.2,-10.6],[-76.9,-10.7],[-76.7,-10.8],[-76.5,-11.0],[-76.3,-11.2],[-76.3,-11.5],[-76.4,-11.8],[-76.5,-12.0],[-76.7,-12.2],[-76.9,-12.3],[-77.2,-12.3],[-77.5,-12.3],[-77.7,-12.2],[-77.9,-12.0],[-78.1,-11.8],[-78.1,-11.6],[-78.0,-11.4],[-77.9,-11.2],[-77.9,-11.0],[-77.7,-10.8],[-77.6,-10.5]]]}},{"type":"Feature","id":"LORETO","properties":{"NOMBDEP":"LORETO"},"geometry":{"type":"Polygon","coordinates":[[[-72.8,-1.5],[-72.5,-1.3],[-72.4,-1.0],[-72.5,-0.8],[-72.7,-0.6],[-73.0,-0.5],[-73.4,-0.3],[-73.8,-0.1],[-74.2,0.1],[-73.8,0.1],[-73.3,0.1],[-72.8,0.1],[-72.3,0.1],[-71.8,-0.1],[-71.3,-0.5],[-70.8,-0.9],[-70.4,-1.4],[-70.1,-2.0],[-69.9,-2.8],[-69.9,-3.5],[-70.1,-4.1],[-70.6,-4.3],[-71.2,-4.2],[-71.8,-3.9],[-72.4,-3.2],[-73.0,-2.5],[-73.5,-1.7],[-73.54545454545455,-1.6],[-73.2,-1.6],[-72.8,-1.5]]]}},{"type":"Feature","id":"MADRE DE DIOS","properties":{"NOMBDEP":"MADRE DE DIOS"},"geometry":{"type":"Polygon","coordinates":[[[-69.6,-10.9],[-69.8,-11.0],[-70.1,-11.2],[-70.5,-11.3],[-70.9,-11.4],[-71.3,-11.5],[-71.6,-11.6],[-71.9,-11.7],[-72.1,-11.7],[-72.3,-11.8],[-72.4,-12.0],[-72.4,-12.3],[-72.2,-12.6],[-71.9,-12.9],[-71.5,-13.2],[-71.1,-13.4],[-70.7,-13.4],[-70.3,-13.3],[-70.0,-13.0],[-69.9,-12.7],[-70.0,-12.4],[-70.1,-12.1],[-70.2,-11.9],[-70.0,-11.6],[-69.7,-11.3],[-69.6,-10.9]]]}},{"type":"Feature","id":"MOQUEGUA","properties":{"NOMBDEP":"MOQUEGUA"},"geometry":{"type":"Polygon","coordinates":[[[-70.9,-16.0],[-70.6,-16.1],[-70.4,-16.2],[-70.2,-16.4],[-70.0,-16.6],[-69.9,-16.8],[-69.9,-17.0],[-70.0,-17.3],[-70.1,-17.5],[-70.3,-17.7],[-70.6,-17.8],[-70.8,-17.8],[-71.1,-17.8],[-71.4,-17.7],[-71.6,-17.6],[-71.7,-17.4],[-71.8,-17.2],[-71.7,-17.0],[-71.6,-16.8],[-71.5,-16.6],[-71.3,-16.5],[-71.0,-16.3],[-70.9,-16.0]]]}},{"type":"Feature","id":"PASCO","properties":{"NOMBDEP":"PASCO"},"geometry":{"type":"Polygon","coordinates":[[[-76.1,-9.6],[-75.8,-9.7],[-75.5,-9.7],[-75.3,-9.8],[-75.2,-10.0],[-75.0,-10.2],[-75.0,-10.4],[-75.1,-10.6],[-75.2,-10.8],[-75.4,-11.0],[-75.6,-11.1],[-75.9,-11.1],[-76.1,-11.0],[-76.3,-10.9],[-76.5,-10.8],[-76.6,-10.5],[-76.6,-10.3],[-76.5,-10.1],[-76.3,-9.9],[-76.1,-9.8],[-76.1,-9.6]]]}},{"type":"Feature","id":"PIURA","properties":{"NOMBDEP":"PIURA"},"geometry":{"type":"Polygon","coordinates":[[[-81.3,-3.5],[-80.9,-3.5],[-80.7,-3.6],[-80.3,-3.7],[-80.0,-3.7],[-79.8,-3.8],[-79.5,-4.0],[-79.3,-4.1],[-79.1,-4.3],[-79.0,-4.5],[-78.9,-4.7],[-79.0,-5.0],[-79.2,-5.2],[-79.4,-5.4],[-79.6,-5.6],[-79.9,-5.7],[-80.2,-5.6],[-80.4,-5.5],[-80.6,-5.4],[-80.7,-5.2],[-80.8,-5.0],[-80.9,-4.7],[-80.9,-4.5],[-80.8,-4.3],[-80.7,-4.1],[-80.9,-3.8],[-81.1,-3.6],[-81.3,-3.5]]]}},{"type":"Feature","id":"PUNO","properties":{"NOMBDEP":"PUNO"},"geometry":{"type":"Polygon","coordinates":[[[-70.0,-13.4],[-70.3,-13.4],[-70.6,-13.4],[-70.9,-13.5],[-71.1,-13.5],[-71.3,-13.5],[-71.6,-13.4],[-71.8,-13.4],[-72.0,-13.4],[-72.1,-13.2],[-72.0,-13.0],[-71.9,-12.8],[-71.7,-12.7],[-71.5,-12.6],[-71.3,-12.6],[-71.1,-12.5],[-70.9,-12.5],[-70.7,-12.5],[-70.5,-12.4],[-70.3,-12.4],[-70.1,-12.5],[-70.0,-12.6],[-69.9,-12.8],[-69.9,-13.1],[-70.0,-13.4]]]}},{"type":"Feature","id":"SAN MARTIN","properties":{"NOMBDEP":"SAN MARTIN"},"geometry":{"type":"Polygon","coordinates":[[[-77.8,-5.4],[-77.4,-5.4],[-77.1,-5.5],[-76.8,-5.6],[-76.6,-5.7],[-76.4,-5.8],[-76.2,-5.9],[-76.1,-6.1],[-76.0,-6.3],[-76.0,-6.5],[-76.1,-6.7],[-76.2,-6.9],[-76.4,-7.0],[-76.7,-7.1],[-76.9,-7.2],[-77.2,-7.3],[-77.5,-7.3],[-77.8,-7.2],[-78.0,-7.1],[-78.2,-7.0],[-78.4,-6.8],[-78.4,-6.6],[-78.4,-6.3],[-78.2,-6.1],[-78.1,-5.9],[-77.9,-5.8],[-77.8,-5.4]]]}},{"type":"Feature","id":"TACNA","properties":{"NOMBDEP":"TACNA"},"geometry":{"type":"Polygon","coordinates":[[[-70.0,-17.3],[-70.2,-17.4],[-70.4,-17.4],[-70.6,-17.5],[-70.9,-17.5],[-71.1,-17.5],[-71.4,-17.5],[-71.6,-17.4],[-71.8,-17.3],[-71.9,-17.2],[-71.9,-17.0],[-71.9,-16.9],[-71.8,-16.8],[-71.6,-16.6],[-71.4,-16.5],[-71.2,-16.4],[-70.9,-16.4],[-70.7,-16.4],[-70.5,-16.5],[-70.3,-16.6],[-70.1,-16.8],[-70.0,-17.0],[-70.0,-17.3]]]}},{"type":"Feature","id":"TUMBES","properties":{"NOMBDEP":"TUMBES"},"geometry":{"type":"Polygon","coordinates":[[[-80.5,-3.4],[-80.2,-3.4],[-80.0,-3.5],[-79.8,-3.6],[-79.6,-3.7],[-79.4,-3.8],[-79.4,-4.1],[-79.5,-4.3],[-79.6,-4.5],[-79.8,-4.6],[-80.0,-4.6],[-80.2,-4.6],[-80.4,-4.6],[-80.6,-4.5],[-80.7,-4.3],[-80.8,-4.1],[-80.8,-3.9],[-80.7,-3.7],[-80.5,-3.4]]]}},{"type":"Feature","id":"UCAYALI","properties":{"NOMBDEP":"UCAYALI"},"geometry":{"type":"Polygon","coordinates":[[[-74.5,-7.2],[-74.2,-7.3],[-74.0,-7.4],[-73.8,-7.5],[-73.6,-7.7],[-73.5,-7.9],[-73.4,-8.0],[-73.4,-8.2],[-73.5,-8.4],[-73.6,-8.6],[-73.8,-8.7],[-73.9,-8.9],[-74.1,-9.0],[-74.4,-9.0],[-74.6,-8.9],[-74.8,-8.8],[-75.0,-8.8],[-75.2,-8.7],[-75.3,-8.5],[-75.3,-8.3],[-75.2,-8.1],[-75.1,-7.9],[-74.8,-7.7],[-74.5,-7.2]]]}}]}

# -------------------------------------------------------
# SECTION: Page setup
# -------------------------------------------------------
st.set_page_config(
    page_title="Overview \u00b7 " + APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

if not st.session_state.get("autenticado", False):
    st.warning("Debes iniciar sesi\u00f3n primero.")
    st.stop()

# -------------------------------------------------------
# SECTION: Cargar datos
# -------------------------------------------------------
with st.spinner("Cargando datos..."):
    kpis     = resumen_kpis()
    cands    = cargar_candidatos()
    votos    = cargar_votaciones()
    reinfo   = cargar_reinfo()
    leyes_df = cargar_leyes()

# -------------------------------------------------------
# HELPERS locales
# -------------------------------------------------------

def _sep():
    return (
        '<div style="border-top:1px solid ' + COLOR_BORDER_SOFT + ';'
        'margin:14px 0;"></div>'
    )

def _gold_rule():
    return (
        '<div style="margin:36px 0 28px 0;display:flex;align-items:center;gap:12px;">'
        '<div style="flex:1;height:1px;background:' + COLOR_GOLD + ';"></div>'
        '<div style="width:5px;height:5px;background:' + COLOR_TEXT_PRIMARY + ';'
        'transform:rotate(45deg);flex-shrink:0;"></div>'
        '<div style="flex:1;height:1px;background:' + COLOR_GOLD + ';"></div>'
        '</div>'
    )

def _eyebrow(text):
    return (
        '<div style="font-size:0.60rem;font-weight:700;letter-spacing:0.18em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_SECONDARY + ';margin-bottom:4px;">'
        + text + '</div>'
    )

def _section_title(title, sub=None):
    html = (
        '<div style="font-family:' + FONT_SERIF + ';font-size:1.45rem;font-weight:500;'
        'color:' + COLOR_TEXT_PRIMARY + ';letter-spacing:-0.015em;line-height:1.2;margin-bottom:'
        + ('2px' if sub else '0') + ';">' + title + '</div>'
    )
    if sub:
        html += (
            '<div style="font-size:0.82rem;color:' + COLOR_TEXT_SECONDARY + ';'
            'font-style:italic;line-height:1.45;margin-bottom:14px;">' + sub + '</div>'
        )
    return html

def _section_header(eyebrow, title, sub):
    return (
        '<div style="margin-bottom:16px;">'
        + _eyebrow(eyebrow)
        + _section_title(title, sub)
        + '</div>'
    )

def pct_a_favor(col_name):
    if col_name not in votos.columns:
        return None, None
    validos = votos[col_name].isin(["A FAVOR", "EN CONTRA", "ABSTENCION"]).sum()
    n_favor = (votos[col_name] == "A FAVOR").sum()
    pct = round(n_favor / validos * 100) if validos > 0 else 0
    return pct, int(n_favor)

# -------------------------------------------------------
# SECTION: Header de página
# -------------------------------------------------------
st.markdown(
    '<div class="masthead">'
    '<div class="masthead-title">'
    + APP_TITLE +
    ' <em>\u00b7 Resumen ejecutivo</em>'
    '</div>'
    '<div class="masthead-meta">'
    '<span class="pill red">' + APP_CONFIDENTIAL_LABEL + '</span>'
    '<span>' + APP_VERSION + '</span>'
    '</div>'
    '</div>'
    '<div class="page-title-wrap">'
    + _eyebrow("OVERVIEW \u00b7 PANORAMA GENERAL") +
    '<h1 class="page-title" style="font-size:2.4rem;margin:0 0 6px 0;'
    'color:' + COLOR_TEXT_PRIMARY + ';">'
    'Integridad electoral y riesgos institucionales'
    '</h1>'
    '<div class="page-title-light" style="font-size:1.05rem;color:' + COLOR_TEXT_SECONDARY + ';'
    'font-style:italic;max-width:760px;line-height:1.55;">'
    '9\u202f065 candidatos inscritos ante el JNE para las Elecciones Generales 2026. '
    'Este panel sintetiza los indicadores clave de riesgo: v\u00ednculos con crimen organizado, '
    'historial legislativo y conexiones con la miner\u00eda informal no autorizada.'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

# =====================================================
# BANDA 1 — KPIs principales
# =====================================================
kpi_main, _gap, k1, k2, k3 = st.columns([2.2, 0.15, 1, 1, 1])

with kpi_main:
    st.markdown(
        '<div style="background:' + COLOR_SURFACE + ';border:1px solid ' + COLOR_BORDER + ';'
        'border-top:3px solid ' + COLOR_PRIMARY + ';border-radius:0;'
        'padding:24px 28px 22px 28px;height:100%;">'
        '<div style="font-size:0.62rem;font-weight:700;letter-spacing:0.14em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_PRIMARY + ';margin-bottom:10px;">'
        'Total \u00b7 Candidatos inscritos'
        '</div>'
        '<div style="font-family:' + FONT_SERIF + ';font-size:4rem;font-weight:500;'
        'color:' + COLOR_TEXT_PRIMARY + ';font-variant-numeric:tabular-nums;'
        'letter-spacing:-0.03em;line-height:0.95;">'
        + str(f"{kpis['total_candidatos']:,}") +
        '</div>'
        '<div style="width:42px;height:2px;background:' + COLOR_TEXT_PRIMARY + ';'
        'margin:14px 0 10px 0;"></div>'
        '<div style="font-size:0.88rem;color:' + COLOR_TEXT_SECONDARY + ';'
        'line-height:1.5;max-width:380px;">'
        'Candidatos inscritos ante el JNE para las Elecciones Generales 2026. '
        'Universo total sobre el que se construye el monitoreo.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

def _kpi_sec(label, valor, nota, rule_color=None):
    c = rule_color or COLOR_PRIMARY
    return (
        '<div style="background:' + COLOR_SURFACE + ';border:1px solid ' + COLOR_BORDER + ';'
        'border-top:3px solid ' + c + ';border-radius:0;'
        'padding:18px 18px 16px 18px;height:100%;">'
        '<div style="font-size:0.58rem;font-weight:700;letter-spacing:0.12em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:8px;line-height:1.3;">'
        + label +
        '</div>'
        '<div style="font-family:' + FONT_SERIF + ';font-size:2.4rem;font-weight:500;'
        'color:' + c + ';font-variant-numeric:tabular-nums;'
        'letter-spacing:-0.02em;line-height:1;">'
        + str(valor) +
        '</div>'
        '<div style="font-size:0.72rem;color:' + COLOR_TEXT_SECONDARY + ';'
        'margin-top:6px;line-height:1.4;">'
        + nota +
        '</div>'
        '</div>'
    )

with k1:
    st.markdown(_kpi_sec(
        "Congresistas postulando",
        kpis["congresistas_postulando"],
        "En ejercicio \u00b7 postulan en 2026",
        COLOR_PRIMARY,
    ), unsafe_allow_html=True)

with k2:
    st.markdown(_kpi_sec(
        "V\u00ednculo REINFO",
        kpis["con_reinfo"],
        "Candidatos con derechos mineros",
        COLOR_REINFO,
    ), unsafe_allow_html=True)

with k3:
    st.markdown(_kpi_sec(
        "Riesgo alto",
        kpis["riesgo_alto"],
        "Score \u2265 " + str(SCORE_ALTO_MIN) + " \u00b7 congresistas",
        COLOR_RIESGO_ALTO,
    ), unsafe_allow_html=True)

st.markdown('<div style="height:36px"></div>', unsafe_allow_html=True)

# =====================================================
# BANDA 2 — Panel de riesgo: niveles + partidos
# =====================================================
col_niveles, col_partidos = st.columns([2, 3], gap="large")

with col_niveles:
    st.markdown(
        _section_header(
            "CONGRESISTAS POSTULANTES",
            "Niveles de riesgo",
            "89 congresistas en ejercicio que postulan en 2026",
        ),
        unsafe_allow_html=True,
    )

    riesgo_counts = votos["nivel_riesgo"].value_counts().reset_index()
    riesgo_counts.columns = ["nivel", "cantidad"]
    orden_riesgo = ["alto", "medio", "bajo", "none"]
    rc_dict = dict(zip(riesgo_counts["nivel"], riesgo_counts["cantidad"]))
    total_congs = len(votos)

    niveles_display = [
        ("alto",  "Riesgo alto",   COLOR_RIESGO_ALTO),
        ("medio", "Riesgo medio",  COLOR_RIESGO_MEDIO),
        ("bajo",  "Riesgo bajo",   COLOR_RIESGO_BAJO),
        ("none",  "Sin dato",      COLOR_RIESGO_NONE),
    ]

    for nivel, label, color in niveles_display:
        n = rc_dict.get(nivel, 0)
        pct = round(n / total_congs * 100) if total_congs > 0 else 0
        st.markdown(
            '<div style="background:' + COLOR_SURFACE + ';border:1px solid ' + COLOR_BORDER + ';'
            'border-left:4px solid ' + color + ';border-radius:0;'
            'padding:12px 16px;margin-bottom:8px;'
            'display:flex;justify-content:space-between;align-items:center;">'
            '<div>'
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
            'text-transform:uppercase;color:' + color + ';">' + label + '</div>'
            '<div style="font-size:0.74rem;color:' + COLOR_TEXT_SECONDARY + ';margin-top:2px;">'
            + str(pct) + '% de los congresistas postulantes'
            '</div>'
            '</div>'
            '<div style="font-family:' + FONT_SERIF + ';font-size:2rem;font-weight:500;'
            'color:' + color + ';font-variant-numeric:tabular-nums;'
            'letter-spacing:-0.02em;line-height:1;">'
            + str(n) +
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

with col_partidos:
    st.markdown(
        _section_header(
            "RIESGO ALTO POR PARTIDO",
            "Partidos \u00b7 congresistas de riesgo alto",
            "Top 8 por concentraci\u00f3n \u00b7 votos a favor de leyes que debilitan el sistema de justicia",
        ),
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

    max_chars = riesgo_partido["partido_label"].str.len().max()
    margen_izq = min(int(max_chars * 6.5), 280)
    altura_partidos = max(260, len(riesgo_partido) * 42 + 20)

    fig_partidos = go.Figure()
    fig_partidos.add_trace(go.Bar(
        x=riesgo_partido["n"],
        y=riesgo_partido["partido_label"],
        orientation="h",
        marker_color=COLOR_RIESGO_ALTO,
        marker_line_width=0,
        text=riesgo_partido["n"],
        textposition="outside",
        textfont=dict(size=12, color=COLOR_TEXT_PRIMARY, family=FONT_SANS),
        hovertemplate="<b>%{y}</b><br>%{x} congresistas riesgo alto<extra></extra>",
        cliponaxis=False,
    ))
    fig_partidos.update_traces(marker=dict(cornerradius=BAR_CORNER_RADIUS))
    fig_partidos.update_layout(
        height=altura_partidos,
        margin=dict(l=margen_izq, r=48, t=4, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        font=dict(family=FONT_SANS, size=11, color=COLOR_TEXT_PRIMARY),
        xaxis=dict(visible=False, showgrid=False, zeroline=False,
                   range=[0, riesgo_partido["n"].max() * 1.25]),
        yaxis=dict(showgrid=False, zeroline=False,
                   tickfont=dict(size=10.5, color=COLOR_TEXT_SECONDARY),
                   automargin=False),
    )
    st.plotly_chart(fig_partidos, use_container_width=True)

st.markdown(_gold_rule(), unsafe_allow_html=True)

# =====================================================
# BANDA 3 — Inteligencia legislativa
# Columna izq: gráfico completo de 16 leyes
# Columna der: 7 cards de leyes destacadas (C2)
# =====================================================
col_leyes_chart, col_leyes_cards = st.columns([3, 1.4], gap="large")

# ---- Calcular datos de leyes ----
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
        "ley":         col.split(" ", 1)[1] if " " in col else col,
        "a_favor_pct": pct,
        "bloque":      bloque,
        "n_favor":     int(a_favor),
        "clave":       col.split(" ")[0],
        "col_full":    col,
    })

res_df = pd.DataFrame(resultados).sort_values("a_favor_pct", ascending=True)
colores_bloque = {**COLOR_BLOQUE, "otro": COLOR_RIESGO_NONE}
res_df["color"] = res_df["bloque"].map(colores_bloque).fillna(COLOR_RIESGO_NONE)
res_df["pct_label"] = res_df["a_favor_pct"].apply(lambda x: str(int(x)) + "%")

with col_leyes_chart:
    st.markdown(
        _section_header(
            "AN\u00c1LISIS DE VOTACIONES",
            "Votos a favor por ley",
            "% de congresistas postulantes que votaron a favor \u00b7 agrupado por bloque tem\u00e1tico",
        ),
        unsafe_allow_html=True,
    )

    max_chars_leyes = res_df["ley"].str.len().max()
    margen_leyes = min(int(max_chars_leyes * 6.2), 260)
    altura_leyes = max(420, len(res_df) * 34 + 50)

    fig_leyes = go.Figure()
    for bloque_nombre, grupo in res_df.groupby("bloque"):
        color_b = colores_bloque.get(bloque_nombre, COLOR_RIESGO_NONE)
        fig_leyes.add_trace(go.Bar(
            x=grupo["a_favor_pct"],
            y=grupo["ley"],
            orientation="h",
            name=bloque_nombre.capitalize(),
            marker_color=color_b,
            marker_line_width=0,
            text=grupo["pct_label"],
            textposition="outside",
            textfont=dict(size=11, color=COLOR_TEXT_PRIMARY, family=FONT_SANS),
            customdata=grupo[["n_favor", "clave"]].values,
            hovertemplate=(
                "<b>%{customdata[1]}</b> %{y}<br>"
                "%{x:.0f}% a favor \u00b7 %{customdata[0]} congresistas<extra></extra>"
            ),
            cliponaxis=False,
        ))
    fig_leyes.update_traces(marker=dict(cornerradius=BAR_CORNER_RADIUS))
    fig_leyes.update_layout(
        height=altura_leyes,
        margin=dict(l=margen_leyes, r=52, t=4, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        barmode="overlay",
        font=dict(family=FONT_SANS, size=11, color=COLOR_TEXT_PRIMARY),
        legend=dict(
            orientation="h",
            y=-0.05, x=0,
            font=dict(size=10),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(visible=False, showgrid=False, zeroline=False, range=[0, 115]),
        yaxis=dict(showgrid=False, zeroline=False,
                   tickfont=dict(size=10, color=COLOR_TEXT_SECONDARY),
                   automargin=False),
    )
    st.plotly_chart(fig_leyes, use_container_width=True)

with col_leyes_cards:
    st.markdown(
        _section_header(
            "LEYES CLAVE \u00b7 VOTOS A FAVOR",
            "\u00bfCu\u00e1ntos votaron a favor?",
            "% sobre votos v\u00e1lidos \u00b7 congresistas en ejercicio que postulan",
        ),
        unsafe_allow_html=True,
    )

    LEYES_DESTACADAS = [
        ("L31751 Prescripci\u00f3n 1 a\u00f1o",           "Prescripci\u00f3n 1 a\u00f1o",        "pro-crimen",     COLOR_RIESGO_ALTO),
        ("L31989 Elimina incautaci\u00f3n",               "Elimina incautaci\u00f3n",              "pro-crimen",     COLOR_RIESGO_ALTO),
        ("L31990 Limita colaboraci\u00f3n eficaz",        "Limita colaboraci\u00f3n eficaz",       "pro-crimen",     COLOR_RIESGO_ALTO),
        ("L32181 Elimina detenci\u00f3n preliminar",      "Elimina detenci\u00f3n prelim.",        "pro-crimen",     COLOR_RIESGO_ALTO),
        ("L32301 Ley APCI",                               "Ley APCI",                              "espacio-civico", COLOR_BLOQUE.get("espacio-civico", COLOR_ACCENT)),
        ("L32537 REINFO 5a amp",                          "REINFO 5\u00aa ampliaci\u00f3n",        "reinfo",         COLOR_REINFO),
        ("L31988 Bicameralidad",                          "Bicameralidad",                         "bicameralidad",  COLOR_PRIMARY),
    ]

    for clave, etiqueta, bloque, color in LEYES_DESTACADAS:
        pct, n = pct_a_favor(clave)
        if pct is None:
            continue
        # Barra de progreso interna (track + fill)
        bar_fill = (
            '<div style="margin-top:8px;background:#E5E1D6;'
            'border-radius:0;height:3px;overflow:hidden;">'
            '<div style="background:' + color + ';width:' + str(pct) + '%;height:3px;"></div>'
            '</div>'
        )
        st.markdown(
            '<div style="background:' + COLOR_SURFACE + ';border:1px solid ' + COLOR_BORDER + ';'
            'border-top:2px solid ' + color + ';border-radius:0;'
            'padding:12px 14px 10px 14px;margin-bottom:7px;">'
            '<div style="font-size:0.54rem;font-weight:700;letter-spacing:0.12em;'
            'text-transform:uppercase;color:' + color + ';margin-bottom:4px;">'
            + bloque +
            '</div>'
            '<div style="font-family:' + FONT_SERIF + ';font-size:1.8rem;font-weight:500;'
            'color:' + color + ';font-variant-numeric:tabular-nums;'
            'letter-spacing:-0.02em;line-height:1;">'
            + str(pct) + '%'
            '</div>'
            '<div style="font-size:0.78rem;font-weight:600;'
            'color:' + COLOR_TEXT_PRIMARY + ';margin:4px 0 1px 0;line-height:1.3;">'
            + etiqueta +
            '</div>'
            '<div style="font-size:0.67rem;color:' + COLOR_TEXT_MUTED + ';font-style:italic;">'
            + str(n) + ' de ' + str(len(votos)) + ' votaron a favor'
            '</div>'
            + bar_fill +
            '</div>',
            unsafe_allow_html=True,
        )

st.markdown(_gold_rule(), unsafe_allow_html=True)

# =====================================================
# BANDA 4 — Geografía + REINFO
# Mapa choropleth: % candidatos riesgo alto por depto
# =====================================================
col_mapa, col_reinfo_viz = st.columns([3, 2], gap="large")

with col_mapa:
    st.markdown(
        _section_header(
            "DISTRIBUCI\u00d3N GEOGR\u00c1FICA \u00b7 RIESGO",
            "Concentraci\u00f3n de riesgo por departamento",
            "% de candidatos con riesgo alto sobre el total de candidatos del departamento",
        ),
        unsafe_allow_html=True,
    )

    # Calcular % riesgo alto por región
    # cands tiene col 'nivel_riesgo' o necesitamos unir con votos por DNI
    # Usamos candidatos_con_flags que ya trae nivel_riesgo calculado
    cands_flags = candidatos_con_flags()

    mapa_data = (
        cands_flags.groupby("region")
        .agg(
            total=("dni", "count"),
            riesgo_alto=("nivel_riesgo", lambda x: (x == "alto").sum()),
            es_prioritaria=("es_region_prioritaria", "max"),
        )
        .reset_index()
    )
    mapa_data["pct_alto"] = (
        mapa_data["riesgo_alto"] / mapa_data["total"] * 100
    ).round(1)
    # Normalizar nombre de región para match con GeoJSON (MAYÚSCULAS)
    mapa_data["region_geo"] = mapa_data["region"].str.upper()

    fig_mapa = px.choropleth_mapbox(
        mapa_data,
        geojson=PERU_GEOJSON,
        locations="region_geo",
        featureidkey="id",
        color="pct_alto",
        color_continuous_scale=[
            [0.0,  "#F7F5F0"],   # sin riesgo — paper claro
            [0.25, "#F0D5D5"],   # tenue
            [0.5,  "#C97777"],   # medio
            [0.75, "#A03030"],   # alto
            [1.0,  COLOR_RIESGO_ALTO],  # máximo — rojo profundo
        ],
        range_color=[0, mapa_data["pct_alto"].max()],
        mapbox_style="carto-positron",
        zoom=3.8,
        center={"lat": -9.19, "lon": -75.0},
        hover_name="region_geo",
        hover_data={
            "total": True,
            "riesgo_alto": True,
            "pct_alto": True,
            "region_geo": False,
        },
        labels={
            "pct_alto":    "% riesgo alto",
            "total":       "Total candidatos",
            "riesgo_alto": "Candidatos riesgo alto",
        },
        height=CHART_HEIGHT,
    )
    fig_mapa.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=COLOR_SURFACE,
        font=dict(family=FONT_SANS, size=11, color=COLOR_TEXT_PRIMARY),
        coloraxis_colorbar=dict(
            title=dict(text="% riesgo<br>alto", font=dict(size=10.5, family=FONT_SANS)),
            tickfont=dict(size=10, family=FONT_SANS, color=COLOR_TEXT_SECONDARY),
            thickness=12,
            len=0.55,
            bgcolor="rgba(255,255,255,0.85)",
            borderwidth=0,
        ),
    )
    # Resaltar regiones prioritarias con borde diferenciado
    regiones_prio_upper = [r.upper() for r in REGIONES_PRIORITARIAS]
    fig_mapa.add_trace(go.Choroplethmapbox(
        geojson=PERU_GEOJSON,
        locations=regiones_prio_upper,
        featureidkey="id",
        z=[1] * len(regiones_prio_upper),
        colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
        showscale=False,
        marker=dict(
            line=dict(color=COLOR_GOLD, width=2.5),
            opacity=0,
        ),
        hoverinfo="skip",
        name="Regi\u00f3n prioritaria",
    ))

    # Nota: borde dorado = región prioritaria del proyecto
    st.markdown(
        '<div style="background:' + COLOR_SURFACE + ';border:1px solid ' + COLOR_BORDER + ';'
        'border-top:3px solid ' + COLOR_PRIMARY + ';border-radius:0;padding:2px;">',
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig_mapa, use_container_width=True)
    st.markdown(
        '<div style="padding:6px 12px 8px 12px;font-size:0.70rem;'
        'color:' + COLOR_TEXT_MUTED + ';border-top:1px solid ' + COLOR_BORDER + ';">'
        '<span style="display:inline-block;width:14px;height:2px;'
        'background:' + COLOR_GOLD + ';vertical-align:middle;margin-right:5px;"></span>'
        'Borde dorado = regi\u00f3n prioritaria del proyecto (Ucayali, Loreto, Madre de Dios, Puno)'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

with col_reinfo_viz:
    st.markdown(
        _section_header(
            "MINER\u00cdA INFORMAL",
            "V\u00ednculos REINFO",
            "Candidatos con derechos mineros registrados \u00b7 top departamentos",
        ),
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
    altura_reinfo = max(280, len(dptos) * 34 + 20)

    fig_reinfo = go.Figure()
    fig_reinfo.add_trace(go.Bar(
        x=dptos["candidatos"],
        y=dptos["departamento"],
        orientation="h",
        marker_color=COLOR_REINFO,
        marker_line_width=0,
        text=dptos["candidatos"],
        textposition="outside",
        textfont=dict(size=11, color=COLOR_TEXT_PRIMARY, family=FONT_SANS),
        hovertemplate="<b>%{y}</b><br>%{x} candidatos con REINFO<extra></extra>",
        cliponaxis=False,
    ))
    fig_reinfo.update_traces(marker=dict(cornerradius=BAR_CORNER_RADIUS))
    fig_reinfo.update_layout(
        height=altura_reinfo,
        margin=dict(l=margen_reinfo, r=40, t=4, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        font=dict(family=FONT_SANS, size=11, color=COLOR_TEXT_PRIMARY),
        xaxis=dict(visible=False, showgrid=False, zeroline=False,
                   range=[0, dptos["candidatos"].max() * 1.3]),
        yaxis=dict(showgrid=False, zeroline=False,
                   tickfont=dict(size=10.5, color=COLOR_TEXT_SECONDARY),
                   automargin=False),
    )
    st.plotly_chart(fig_reinfo, use_container_width=True)

    # Nota sobre regiones prioritarias con más REINFO
    prio_reinfo = dptos[dptos["departamento"].str.upper().isin(
        [r.upper() for r in REGIONES_PRIORITARIAS]
    )]
    if not prio_reinfo.empty:
        prio_list = ", ".join(prio_reinfo["departamento"].str.title().tolist())
        st.markdown(
            '<div style="background:' + COLOR_RIESGO_ALTO_BG + ';border:1px solid ' + COLOR_RIESGO_ALTO + ';'
            'border-left:3px solid ' + COLOR_RIESGO_ALTO + ';border-radius:0;'
            'padding:10px 14px;margin-top:8px;">'
            '<div style="font-size:0.62rem;font-weight:700;letter-spacing:0.12em;'
            'text-transform:uppercase;color:' + COLOR_RIESGO_ALTO + ';margin-bottom:4px;">'
            'Regiones prioritarias con v\u00ednculo REINFO'
            '</div>'
            '<div style="font-size:0.80rem;color:' + COLOR_TEXT_PRIMARY + ';line-height:1.4;">'
            + prio_list +
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

# -------------------------------------------------------
# SECTION: Footer
# -------------------------------------------------------
st.markdown(
    '<div style="margin-top:48px;padding-top:14px;'
    'border-top:1px solid ' + COLOR_BORDER + ';display:flex;'
    'justify-content:space-between;font-size:0.70rem;color:' + COLOR_TEXT_MUTED + ';'
    'letter-spacing:0.04em;">'
    '<span>' + APP_CONFIDENTIAL_LABEL + ' \u00b7 ' + APP_VERSION + '</span>'
    '<span>Fuentes: JNE \u00b7 REINFO \u00b7 Congreso del Per\u00fa \u00b7 porEstosNo.pe</span>'
    '</div>',
    unsafe_allow_html=True,
)
