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
PERU_GEOJSON = {
  "type": "FeatureCollection",
  "features": [
    {"type":"Feature","id":"AMAZONAS","properties":{"NOMBDEP":"AMAZONAS"},"geometry":{"type":"Polygon","coordinates":[[[-78.67,2.01],[-78.23,2.00],[-77.85,1.76],[-77.50,1.48],[-77.31,1.53],[-77.01,1.25],[-76.52,0.91],[-75.82,0.85],[-75.53,1.22],[-75.27,1.57],[-75.51,1.85],[-75.99,2.17],[-76.28,2.38],[-76.79,2.27],[-77.02,2.58],[-77.47,2.96],[-77.93,3.04],[-78.35,2.77],[-78.67,2.01]]]}},
    {"type":"Feature","id":"ANCASH","properties":{"NOMBDEP":"ANCASH"},"geometry":{"type":"Polygon","coordinates":[[[-77.18,-8.00],[-76.74,-8.11],[-76.48,-8.39],[-76.19,-8.65],[-76.38,-9.00],[-76.62,-9.29],[-76.85,-9.60],[-77.08,-9.91],[-77.36,-10.20],[-77.68,-10.43],[-78.03,-10.55],[-78.22,-10.20],[-78.48,-9.83],[-78.52,-9.32],[-78.38,-8.98],[-78.02,-8.72],[-77.72,-8.43],[-77.47,-8.21],[-77.18,-8.00]]]}},
    {"type":"Feature","id":"APURIMAC","properties":{"NOMBDEP":"APURIMAC"},"geometry":{"type":"Polygon","coordinates":[[[-72.60,-13.17],[-72.18,-13.25],[-71.82,-13.50],[-71.52,-13.76],[-71.25,-14.05],[-71.05,-14.38],[-71.28,-14.61],[-71.64,-14.78],[-72.08,-14.90],[-72.46,-14.78],[-72.85,-14.62],[-73.13,-14.35],[-73.35,-14.05],[-73.32,-13.74],[-73.08,-13.49],[-72.83,-13.31],[-72.60,-13.17]]]}},
    {"type":"Feature","id":"AREQUIPA","properties":{"NOMBDEP":"AREQUIPA"},"geometry":{"type":"Polygon","coordinates":[[[-74.27,-14.79],[-73.89,-14.93],[-73.47,-15.08],[-73.09,-15.22],[-72.73,-15.38],[-72.39,-15.55],[-72.07,-15.74],[-71.78,-15.96],[-71.52,-16.21],[-71.30,-16.49],[-71.12,-16.80],[-70.99,-17.13],[-71.00,-17.46],[-71.22,-17.73],[-71.57,-17.93],[-72.00,-18.04],[-72.45,-17.99],[-72.87,-17.83],[-73.19,-17.54],[-73.47,-17.21],[-73.73,-16.87],[-73.96,-16.52],[-74.15,-16.16],[-74.29,-15.79],[-74.31,-15.41],[-74.27,-14.79]]]}},
    {"type":"Feature","id":"AYACUCHO","properties":{"NOMBDEP":"AYACUCHO"},"geometry":{"type":"Polygon","coordinates":[[[-74.93,-12.37],[-74.56,-12.45],[-74.18,-12.56],[-73.83,-12.69],[-73.53,-12.85],[-73.27,-13.05],[-73.04,-13.29],[-72.84,-13.57],[-72.73,-13.87],[-72.68,-14.19],[-72.71,-14.51],[-72.82,-14.81],[-73.00,-15.07],[-73.23,-15.27],[-73.50,-15.40],[-73.83,-15.44],[-74.14,-15.37],[-74.42,-15.22],[-74.66,-15.01],[-74.85,-14.76],[-74.97,-14.47],[-75.01,-14.17],[-74.95,-13.87],[-74.81,-13.60],[-74.65,-13.36],[-74.93,-12.37]]]}},
    {"type":"Feature","id":"CAJAMARCA","properties":{"NOMBDEP":"CAJAMARCA"},"geometry":{"type":"Polygon","coordinates":[[[-79.46,-4.45],[-79.10,-4.50],[-78.72,-4.56],[-78.36,-4.62],[-78.04,-4.69],[-77.78,-4.77],[-77.56,-4.88],[-77.38,-5.01],[-77.24,-5.17],[-77.14,-5.36],[-77.09,-5.57],[-77.10,-5.79],[-77.17,-6.01],[-77.30,-6.22],[-77.47,-6.42],[-77.69,-6.60],[-77.95,-6.75],[-78.24,-6.86],[-78.53,-6.92],[-78.80,-6.93],[-79.06,-6.88],[-79.30,-6.78],[-79.51,-6.63],[-79.67,-6.43],[-79.77,-6.19],[-79.82,-5.93],[-79.80,-5.67],[-79.72,-5.42],[-79.60,-5.18],[-79.46,-4.45]]]}},
    {"type":"Feature","id":"CALLAO","properties":{"NOMBDEP":"CALLAO"},"geometry":{"type":"Polygon","coordinates":[[[-77.18,-11.97],[-77.08,-11.97],[-77.01,-12.02],[-77.00,-12.09],[-77.06,-12.14],[-77.15,-12.13],[-77.21,-12.07],[-77.18,-11.97]]]}},
    {"type":"Feature","id":"CUSCO","properties":{"NOMBDEP":"CUSCO"},"geometry":{"type":"Polygon","coordinates":[[[-70.60,-12.66],[-70.84,-12.66],[-71.20,-12.69],[-71.56,-12.74],[-71.91,-12.81],[-72.24,-12.90],[-72.56,-13.01],[-72.84,-13.17],[-73.09,-13.37],[-73.30,-13.62],[-73.46,-13.90],[-73.55,-14.20],[-73.57,-14.51],[-73.51,-14.81],[-73.38,-15.09],[-73.20,-15.33],[-72.97,-15.52],[-72.70,-15.65],[-72.43,-15.70],[-72.16,-15.67],[-71.91,-15.56],[-71.69,-15.38],[-71.52,-15.16],[-71.42,-14.91],[-71.40,-14.64],[-71.46,-14.38],[-71.60,-14.15],[-71.62,-13.82],[-71.56,-13.50],[-71.47,-13.19],[-71.38,-12.90],[-71.26,-12.62],[-71.07,-12.37],[-70.85,-12.16],[-70.62,-11.97],[-70.38,-11.81],[-70.17,-11.73],[-70.13,-12.00],[-70.22,-12.29],[-70.44,-12.50],[-70.60,-12.66]]]}},
    {"type":"Feature","id":"HUANCAVELICA","properties":{"NOMBDEP":"HUANCAVELICA"},"geometry":{"type":"Polygon","coordinates":[[[-75.59,-11.98],[-75.25,-12.03],[-74.91,-12.10],[-74.59,-12.20],[-74.30,-12.33],[-74.07,-12.50],[-73.89,-12.72],[-73.79,-12.97],[-73.79,-13.23],[-73.89,-13.47],[-74.07,-13.67],[-74.32,-13.82],[-74.60,-13.90],[-74.89,-13.92],[-75.16,-13.86],[-75.40,-13.73],[-75.61,-13.55],[-75.76,-13.32],[-75.84,-13.07],[-75.85,-12.81],[-75.78,-12.56],[-75.63,-12.34],[-75.59,-11.98]]]}},
    {"type":"Feature","id":"HUANUCO","properties":{"NOMBDEP":"HUANUCO"},"geometry":{"type":"Polygon","coordinates":[[[-76.72,-8.35],[-76.38,-8.45],[-76.08,-8.58],[-75.83,-8.74],[-75.63,-8.94],[-75.49,-9.17],[-75.44,-9.43],[-75.47,-9.69],[-75.59,-9.94],[-75.80,-10.16],[-76.07,-10.32],[-76.38,-10.40],[-76.70,-10.40],[-76.99,-10.32],[-77.24,-10.16],[-77.44,-9.94],[-77.56,-9.68],[-77.60,-9.42],[-77.56,-9.16],[-77.44,-8.93],[-77.26,-8.73],[-77.04,-8.57],[-76.72,-8.35]]]}},
    {"type":"Feature","id":"ICA","properties":{"NOMBDEP":"ICA"},"geometry":{"type":"Polygon","coordinates":[[[-76.13,-13.09],[-75.82,-13.19],[-75.53,-13.32],[-75.28,-13.48],[-75.07,-13.68],[-74.91,-13.92],[-74.82,-14.19],[-74.82,-14.46],[-74.90,-14.73],[-75.06,-14.96],[-75.29,-15.13],[-75.56,-15.23],[-75.85,-15.24],[-76.14,-15.16],[-76.38,-14.99],[-76.56,-14.75],[-76.66,-14.48],[-76.68,-14.20],[-76.60,-13.94],[-76.45,-13.71],[-76.24,-13.53],[-76.13,-13.09]]]}},
    {"type":"Feature","id":"JUNIN","properties":{"NOMBDEP":"JUNIN"},"geometry":{"type":"Polygon","coordinates":[[[-75.62,-10.49],[-75.30,-10.57],[-75.01,-10.68],[-74.76,-10.82],[-74.56,-11.01],[-74.42,-11.23],[-74.36,-11.48],[-74.38,-11.74],[-74.49,-11.97],[-74.66,-12.17],[-74.88,-12.31],[-75.14,-12.39],[-75.41,-12.39],[-75.67,-12.32],[-75.89,-12.18],[-76.06,-11.99],[-76.17,-11.75],[-76.19,-11.50],[-76.14,-11.25],[-76.01,-11.03],[-75.82,-10.85],[-75.62,-10.49]]]}},
    {"type":"Feature","id":"LA LIBERTAD","properties":{"NOMBDEP":"LA LIBERTAD"},"geometry":{"type":"Polygon","coordinates":[[[-79.71,-6.97],[-79.38,-7.02],[-79.04,-7.08],[-78.71,-7.14],[-78.39,-7.22],[-78.09,-7.31],[-77.83,-7.42],[-77.61,-7.56],[-77.43,-7.73],[-77.31,-7.93],[-77.25,-8.15],[-77.27,-8.38],[-77.37,-8.60],[-77.54,-8.79],[-77.77,-8.95],[-78.05,-9.06],[-78.34,-9.11],[-78.61,-9.10],[-78.86,-9.02],[-79.08,-8.88],[-79.26,-8.69],[-79.39,-8.47],[-79.46,-8.23],[-79.45,-7.98],[-79.38,-7.74],[-79.71,-6.97]]]}},
    {"type":"Feature","id":"LAMBAYEQUE","properties":{"NOMBDEP":"LAMBAYEQUE"},"geometry":{"type":"Polygon","coordinates":[[[-80.63,-5.46],[-80.35,-5.51],[-80.06,-5.58],[-79.78,-5.67],[-79.52,-5.78],[-79.29,-5.91],[-79.09,-6.07],[-78.93,-6.26],[-78.82,-6.47],[-78.77,-6.70],[-78.79,-6.93],[-78.88,-7.15],[-79.04,-7.33],[-79.26,-7.46],[-79.51,-7.53],[-79.76,-7.53],[-80.00,-7.47],[-80.21,-7.35],[-80.37,-7.18],[-80.47,-6.98],[-80.52,-6.76],[-80.52,-6.54],[-80.47,-6.32],[-80.37,-6.11],[-80.63,-5.46]]]}},
    {"type":"Feature","id":"LIMA","properties":{"NOMBDEP":"LIMA"},"geometry":{"type":"Polygon","coordinates":[[[-77.55,-10.49],[-77.22,-10.57],[-76.92,-10.68],[-76.67,-10.83],[-76.47,-11.02],[-76.34,-11.25],[-76.30,-11.50],[-76.35,-11.75],[-76.49,-11.97],[-76.69,-12.15],[-76.95,-12.27],[-77.22,-12.32],[-77.49,-12.30],[-77.73,-12.20],[-77.93,-12.04],[-78.07,-11.83],[-78.14,-11.60],[-78.12,-11.36],[-78.03,-11.14],[-77.87,-10.95],[-77.67,-10.80],[-77.55,-10.49]]]}},
    {"type":"Feature","id":"LORETO","properties":{"NOMBDEP":"LORETO"},"geometry":{"type":"Polygon","coordinates":[[[-75.54,0.16],[-75.20,0.15],[-74.85,0.13],[-74.50,0.10],[-74.15,0.05],[-73.82,-0.02],[-73.50,-0.10],[-73.21,-0.19],[-72.95,-0.30],[-72.72,-0.42],[-72.55,-0.55],[-72.44,-0.70],[-72.41,-0.86],[-72.46,-1.02],[-72.59,-1.16],[-72.79,-1.28],[-73.05,-1.37],[-73.34,-1.42],[-73.63,-1.43],[-73.90,-1.39],[-74.13,-1.30],[-74.32,-1.16],[-74.45,-0.98],[-74.51,-0.77],[-74.50,-0.57],[-74.42,-0.37],[-74.49,-0.13],[-74.63,0.12],[-74.84,0.34],[-75.11,0.51],[-75.40,0.61],[-75.54,0.16]]]}},
    {"type":"Feature","id":"MADRE DE DIOS","properties":{"NOMBDEP":"MADRE DE DIOS"},"geometry":{"type":"Polygon","coordinates":[[[-69.58,-10.93],[-69.81,-11.02],[-70.10,-11.12],[-70.42,-11.22],[-70.75,-11.31],[-71.06,-11.39],[-71.35,-11.46],[-71.60,-11.52],[-71.82,-11.57],[-72.02,-11.61],[-72.18,-11.64],[-72.30,-11.66],[-72.38,-11.93],[-72.38,-12.22],[-72.31,-12.50],[-72.17,-12.77],[-71.97,-12.99],[-71.72,-13.17],[-71.44,-13.29],[-71.15,-13.36],[-70.87,-13.37],[-70.61,-13.31],[-70.38,-13.19],[-70.19,-13.01],[-70.06,-12.79],[-69.99,-12.55],[-69.99,-12.30],[-70.05,-12.06],[-70.17,-11.84],[-70.33,-11.65],[-69.92,-11.44],[-69.66,-11.29],[-69.58,-10.93]]]}},
    {"type":"Feature","id":"MOQUEGUA","properties":{"NOMBDEP":"MOQUEGUA"},"geometry":{"type":"Polygon","coordinates":[[[-70.89,-16.03],[-70.61,-16.12],[-70.37,-16.24],[-70.17,-16.40],[-70.02,-16.59],[-69.93,-16.81],[-69.91,-17.04],[-69.97,-17.27],[-70.10,-17.48],[-70.30,-17.65],[-70.55,-17.77],[-70.83,-17.83],[-71.11,-17.81],[-71.36,-17.72],[-71.56,-17.56],[-71.70,-17.36],[-71.76,-17.14],[-71.73,-16.91],[-71.63,-16.70],[-71.47,-16.53],[-71.26,-16.40],[-71.03,-16.32],[-70.89,-16.03]]]}},
    {"type":"Feature","id":"PASCO","properties":{"NOMBDEP":"PASCO"},"geometry":{"type":"Polygon","coordinates":[[[-76.12,-9.61],[-75.82,-9.65],[-75.55,-9.72],[-75.32,-9.83],[-75.15,-9.99],[-75.04,-10.18],[-75.01,-10.40],[-75.07,-10.62],[-75.20,-10.81],[-75.40,-10.96],[-75.64,-11.05],[-75.89,-11.07],[-76.12,-11.03],[-76.32,-10.92],[-76.48,-10.75],[-76.56,-10.54],[-76.56,-10.32],[-76.49,-10.11],[-76.34,-9.94],[-76.14,-9.82],[-76.12,-9.61]]]}},
    {"type":"Feature","id":"PIURA","properties":{"NOMBDEP":"PIURA"},"geometry":{"type":"Polygon","coordinates":[[[-81.31,-3.45],[-80.99,-3.50],[-80.67,-3.57],[-80.35,-3.65],[-80.05,-3.74],[-79.77,-3.85],[-79.52,-3.98],[-79.30,-4.13],[-79.12,-4.31],[-78.99,-4.51],[-78.93,-4.73],[-78.94,-4.96],[-79.02,-5.18],[-79.17,-5.37],[-79.38,-5.52],[-79.63,-5.62],[-79.89,-5.65],[-80.15,-5.62],[-80.38,-5.52],[-80.58,-5.36],[-80.73,-5.16],[-80.82,-4.93],[-80.84,-4.70],[-80.80,-4.47],[-80.70,-4.26],[-80.96,-4.01],[-81.13,-3.78],[-81.31,-3.45]]]}},
    {"type":"Feature","id":"PUNO","properties":{"NOMBDEP":"PUNO"},"geometry":{"type":"Polygon","coordinates":[[[-70.00,-13.39],[-70.25,-13.41],[-70.52,-13.43],[-70.79,-13.45],[-71.06,-13.46],[-71.32,-13.46],[-71.55,-13.44],[-71.76,-13.42],[-71.93,-13.38],[-72.07,-13.32],[-72.16,-13.25],[-72.19,-13.16],[-72.15,-13.05],[-72.05,-12.95],[-71.91,-12.85],[-71.73,-12.76],[-71.53,-12.68],[-71.33,-12.61],[-71.12,-12.55],[-70.91,-12.50],[-70.71,-12.46],[-70.52,-12.43],[-70.35,-12.43],[-70.20,-12.44],[-70.08,-12.48],[-69.99,-12.54],[-69.95,-12.63],[-69.95,-12.74],[-70.00,-12.86],[-70.10,-12.98],[-70.24,-13.10],[-70.41,-13.20],[-70.59,-13.29],[-70.00,-13.39]]]}},
    {"type":"Feature","id":"SAN MARTIN","properties":{"NOMBDEP":"SAN MARTIN"},"geometry":{"type":"Polygon","coordinates":[[[-77.76,-5.36],[-77.44,-5.41],[-77.13,-5.47],[-76.84,-5.54],[-76.58,-5.63],[-76.36,-5.74],[-76.18,-5.88],[-76.06,-6.05],[-76.00,-6.25],[-76.01,-6.46],[-76.09,-6.66],[-76.23,-6.85],[-76.43,-7.01],[-76.68,-7.14],[-76.95,-7.24],[-77.24,-7.29],[-77.53,-7.29],[-77.80,-7.24],[-78.03,-7.13],[-78.22,-6.97],[-78.35,-6.78],[-78.40,-6.56],[-78.36,-6.34],[-78.25,-6.14],[-78.08,-5.96],[-77.87,-5.82],[-77.63,-5.72],[-77.76,-5.36]]]}},
    {"type":"Feature","id":"TACNA","properties":{"NOMBDEP":"TACNA"},"geometry":{"type":"Polygon","coordinates":[[[-69.97,-17.27],[-70.15,-17.35],[-70.37,-17.43],[-70.62,-17.49],[-70.88,-17.53],[-71.14,-17.53],[-71.38,-17.50],[-71.59,-17.43],[-71.76,-17.33],[-71.87,-17.19],[-71.92,-17.03],[-71.88,-16.87],[-71.78,-16.72],[-71.61,-16.59],[-71.41,-16.49],[-71.17,-16.42],[-70.94,-16.40],[-70.71,-16.43],[-70.50,-16.50],[-70.33,-16.62],[-70.20,-16.78],[-70.14,-16.96],[-70.15,-17.15],[-69.97,-17.27]]]}},
    {"type":"Feature","id":"TUMBES","properties":{"NOMBDEP":"TUMBES"},"geometry":{"type":"Polygon","coordinates":[[[-80.43,-3.38],[-80.21,-3.43],[-80.00,-3.50],[-79.80,-3.58],[-79.63,-3.68],[-79.49,-3.80],[-79.40,-3.93],[-79.36,-4.08],[-79.38,-4.23],[-79.46,-4.37],[-79.60,-4.49],[-79.79,-4.58],[-80.00,-4.63],[-80.22,-4.63],[-80.42,-4.58],[-80.59,-4.47],[-80.71,-4.33],[-80.77,-4.17],[-80.77,-4.00],[-80.71,-3.84],[-80.61,-3.70],[-80.47,-3.58],[-80.43,-3.38]]]}},
    {"type":"Feature","id":"UCAYALI","properties":{"NOMBDEP":"UCAYALI"},"geometry":{"type":"Polygon","coordinates":[[[-74.50,-7.20],[-74.22,-7.28],[-73.97,-7.38],[-73.76,-7.50],[-73.59,-7.65],[-73.47,-7.82],[-73.41,-8.01],[-73.41,-8.21],[-73.47,-8.40],[-73.58,-8.58],[-73.74,-8.73],[-73.93,-8.85],[-74.14,-8.93],[-74.37,-8.97],[-74.60,-8.96],[-74.81,-8.90],[-75.00,-8.79],[-75.15,-8.65],[-75.25,-8.48],[-75.28,-8.29],[-75.25,-8.10],[-75.15,-7.93],[-74.99,-7.79],[-74.80,-7.68],[-74.50,-7.20]]]}},
  ]
}

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
