# ============================================================
# pages/3_congresistas.py — Monitor Electoral Perú 2026
# Tabla de congresistas en ejercicio que postulan en 2026.
# Filtros: nombre, tipo elección 2026, grupo parlamentario, ley.
# Perfil con votaciones detalladas por ley y score desglosado.
#
# NOTA DE ARQUITECTURA: todo el HTML custom se construye por
# concatenación de strings (operador +), NUNCA con f-strings
# multilínea ni comentarios HTML (<!-- -->). Streamlit convierte
# el Markdown antes del HTML y esas construcciones se rompen.
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

from config import (
    APP_TITLE, APP_ICON, APP_CONFIDENTIAL_LABEL,
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_SURFACE, COLOR_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_RIESGO_ALTO, COLOR_RIESGO_ALTO_BG,
    COLOR_RIESGO_MEDIO, COLOR_RIESGO_MEDIO_BG,
    COLOR_RIESGO_BAJO, COLOR_RIESGO_BAJO_BG,
    COLOR_RIESGO_NONE, COLOR_RIESGO_NONE_BG,
    COLOR_REINFO, COLOR_REINFO_BG,
    LABEL_RIESGO, LEYES_COLS, GLOBAL_CSS
)
from data_loader import (
    cargar_congresistas, cargar_votaciones, cargar_reinfo, cargar_leyes,
)

# -------------------------------------------------------
# SECTION: Page setup
# -------------------------------------------------------
st.set_page_config(
    page_title="Congresistas · " + APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

if not st.session_state.get("autenticado", False):
    st.warning("Debes iniciar sesión primero.")
    st.stop()

# -------------------------------------------------------
# SECTION: Cargar y combinar datos
# -------------------------------------------------------
@st.cache_data
def preparar_tabla_congresistas():
    congs  = cargar_congresistas()
    votos  = cargar_votaciones()
    reinfo = cargar_reinfo()

    df = congs.merge(votos, on="dni", how="left", suffixes=("", "_vot"))
    df["nombre_display"] = df["nombre_oficial"].fillna(df["nombre_completo"])

    dni_reinfo = set(reinfo["dni"].unique())
    df["tiene_reinfo"] = df["dni"].isin(dni_reinfo)

    def nivel(s):
        if pd.isna(s): return "none"
        if s >= 20: return "alto"
        if s >= 10: return "medio"
        return "bajo"

    df["nivel_riesgo"]    = df["score_total"].apply(nivel)
    df["etiqueta_riesgo"] = df["nivel_riesgo"].map(LABEL_RIESGO)

    for col in LEYES_COLS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()
            df[col] = df[col].replace("NAN", "SIN DATO")

    df["url_foto"] = None
    return df


with st.spinner("Cargando congresistas..."):
    df_full  = preparar_tabla_congresistas()
    leyes_df = cargar_leyes()

# -------------------------------------------------------
# SECTION: Helpers de HTML
# Funciones reutilizables para construir fragmentos HTML.
# -------------------------------------------------------
def _sep():
    """Divisor horizontal sutil entre filas de la card."""
    return '<div style="border-top:1px solid ' + COLOR_BORDER + ';margin:14px 0;"></div>'


def _field(label, value):
    """Campo label+valor para la grilla de perfil."""
    return (
        '<div>'
        '<p style="font-size:0.63rem;font-weight:700;letter-spacing:0.10em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 2px 0;">'
        + label + '</p>'
        '<p style="font-size:0.92rem;font-weight:600;color:' + COLOR_TEXT_PRIMARY + ';margin:0;">'
        + str(value) + '</p>'
        '</div>'
    )


def _field_sm(label, value):
    """Campo label+valor en tamaño pequeño (fila de postulación)."""
    return (
        '<div>'
        '<p style="font-size:0.63rem;font-weight:700;letter-spacing:0.10em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 2px 0;">'
        + label + '</p>'
        '<p style="font-size:0.88rem;font-weight:500;color:' + COLOR_TEXT_PRIMARY + ';margin:0;">'
        + str(value) + '</p>'
        '</div>'
    )


def _desglose_row(label, value):
    """Fila label-valor para desglose de score."""
    return (
        '<div style="display:flex;justify-content:space-between;'
        'font-size:0.80rem;color:' + COLOR_TEXT_SECONDARY + ';margin-bottom:6px;">'
        '<span>' + label + '</span>'
        '<span style="font-weight:700;color:' + COLOR_TEXT_PRIMARY + ';'
        'font-variant-numeric:tabular-nums;">' + str(value) + '</span>'
        '</div>'
    )


def _kpi_card(label, value, sub, bg, border, color):
    """Card KPI individual."""
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


# -------------------------------------------------------
# SECTION: Header con mini-KPIs custom
# -------------------------------------------------------
n_total  = len(df_full)
n_alto   = int((df_full["nivel_riesgo"] == "alto").sum())
n_medio  = int((df_full["nivel_riesgo"] == "medio").sum())
n_bajo   = int((df_full["nivel_riesgo"] == "bajo").sum())
n_reinfo = int(df_full["tiene_reinfo"].sum())
pct_alto  = round(n_alto  / n_total * 100) if n_total else 0
pct_medio = round(n_medio / n_total * 100) if n_total else 0
pct_bajo  = round(n_bajo  / n_total * 100) if n_total else 0

_card_total = (
    '<div style="background:' + COLOR_PRIMARY + ';border-radius:8px;padding:18px 22px;'
    'display:flex;flex-direction:column;justify-content:space-between;">'
    '<p style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;'
    'text-transform:uppercase;color:rgba(255,255,255,0.65);margin:0 0 8px 0;">Total</p>'
    '<p style="font-size:2.6rem;font-weight:700;color:#FFFFFF;margin:0;line-height:1;'
    'font-variant-numeric:tabular-nums;letter-spacing:-0.03em;">' + str(n_total) + '</p>'
    '<p style="font-size:0.72rem;color:rgba(255,255,255,0.55);margin:6px 0 0 0;">'
    'congresistas en 2026</p>'
    '</div>'
)

_html_header = (
    '<div style="margin-bottom:24px;">'
    '<p style="font-size:0.68rem;font-weight:700;letter-spacing:0.12em;'
    'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 4px 0;">'
    'Congresistas en ejercicio</p>'
    '<h2 style="color:' + COLOR_TEXT_PRIMARY + ';margin:0 0 4px 0;'
    'font-size:1.55rem;font-weight:700;letter-spacing:-0.02em;">'
    'Congresistas postulantes</h2>'
    '<p style="color:' + COLOR_TEXT_SECONDARY + ';font-size:0.85em;margin:0;">'
    + str(n_total) + ' congresistas en ejercicio postulan en 2026 &middot; '
    'Votaciones en 16 leyes clave &middot; '
    '<span style="color:' + COLOR_RIESGO_ALTO + ';font-weight:600;">'
    + str(pct_alto) + '% con riesgo alto</span></p>'
    '</div>'
)

_html_kpis = (
    '<div style="display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr 1fr;'
    'gap:12px;margin-bottom:24px;">'
    + _card_total
    + _kpi_card("Riesgo alto",  n_alto,   str(pct_alto) + "% del total",  COLOR_RIESGO_ALTO_BG,  "#EEC8C8", COLOR_RIESGO_ALTO)
    + _kpi_card("Riesgo medio", n_medio,  str(pct_medio) + "% del total", COLOR_RIESGO_MEDIO_BG, "#EDD6A8", COLOR_RIESGO_MEDIO)
    + _kpi_card("Riesgo bajo",  n_bajo,   str(pct_bajo) + "% del total",  COLOR_RIESGO_BAJO_BG,  "#B8DFC8", COLOR_RIESGO_BAJO)
    + _kpi_card("Con REINFO",   n_reinfo, "v\u00ednculo miner\u00eda informal", COLOR_REINFO_BG, "#E8C8A8", COLOR_REINFO)
    + '</div>'
)

st.markdown(_html_header + _html_kpis, unsafe_allow_html=True)

# -------------------------------------------------------
# SECTION: Filtros
# -------------------------------------------------------
with st.expander("Filtros", expanded=True):
    f1, f2, f3, f4 = st.columns([2, 2, 2, 2])

    with f1:
        busqueda = st.text_input("Buscar por nombre", placeholder="Ej: Flores Ruiz...")
    with f2:
        grupos = ["Todos"] + sorted(df_full["grupo_parlamentario"].dropna().unique().tolist())
        grupo_sel = st.selectbox("Grupo parlamentario", grupos)
    with f3:
        tipos_2026 = ["Todos"] + sorted(df_full["tipo_eleccion"].dropna().unique().tolist())
        tipo_sel = st.selectbox("Cargo que postula 2026", tipos_2026)
    with f4:
        ley_opts = ["Todas las leyes"] + [
            col.split(" ", 1)[1] if " " in col else col for col in LEYES_COLS
        ]
        ley_sel = st.selectbox("Filtrar por voto en ley", ley_opts)
        if ley_sel != "Todas las leyes":
            voto_tipo = st.radio(
                "Tipo de voto", ["A FAVOR", "EN CONTRA", "ABSTENCION", "AUSENTE"],
                horizontal=True,
            )

# -------------------------------------------------------
# SECTION: Aplicar filtros
# -------------------------------------------------------
df_f = df_full.copy()
if busqueda:
    df_f = df_f[df_f["nombre_display"].str.upper().str.contains(busqueda.upper(), na=False)]
if grupo_sel != "Todos":
    df_f = df_f[df_f["grupo_parlamentario"] == grupo_sel]
if tipo_sel != "Todos":
    df_f = df_f[df_f["tipo_eleccion"] == tipo_sel]
if ley_sel != "Todas las leyes":
    col_ley = next((c for c in LEYES_COLS if c.split(" ", 1)[-1] == ley_sel), None)
    if col_ley and col_ley in df_f.columns:
        df_f = df_f[df_f[col_ley] == voto_tipo]

# -------------------------------------------------------
# SECTION: Contador + descarga
# -------------------------------------------------------
col_count, col_dl = st.columns([3, 1])
with col_count:
    st.markdown(
        '<p style="color:' + COLOR_TEXT_SECONDARY + ';font-size:0.88em;margin:4px 0;">'
        'Mostrando <b>' + str(len(df_f)) + '</b> congresistas</p>',
        unsafe_allow_html=True,
    )
with col_dl:
    cols_desc = (
        ["dni", "nombre_display", "grupo_parlamentario", "partido",
         "cargo", "tipo_eleccion", "region", "estado_jne",
         "score_total", "score_procrimen", "nivel_riesgo", "tiene_reinfo", "leyes_autoria"]
        + [c for c in LEYES_COLS if c in df_f.columns]
    )
    csv_bytes = df_f[[c for c in cols_desc if c in df_f.columns]].to_csv(
        index=False).encode("utf-8")
    st.download_button(
        label="Descargar filtrado (CSV)",
        data=csv_bytes, file_name="congresistas_filtrado.csv",
        mime="text/csv", use_container_width=True,
    )

# -------------------------------------------------------
# SECTION: Tabla principal AgGrid
# -------------------------------------------------------
COLS_TABLA = [
    "nombre_display", "grupo_parlamentario", "partido",
    "cargo", "tipo_eleccion", "region",
    "score_total", "etiqueta_riesgo", "tiene_reinfo",
]

df_tabla = df_f[COLS_TABLA].copy()
df_tabla["tiene_reinfo"] = df_tabla["tiene_reinfo"].map({True: "Sí", False: "No"})

row_style = JsCode("""
function(params) {
    var nivel = params.data.etiqueta_riesgo;
    if (nivel && nivel.includes('Alto'))  return {'background-color': '#FDECEA'};
    if (nivel && nivel.includes('Medio')) return {'background-color': '#FEF9E7'};
    if (nivel && nivel.includes('Bajo'))  return {'background-color': '#EAF4EC'};
    return {};
}
""")

gb = GridOptionsBuilder.from_dataframe(df_tabla)
gb.configure_default_column(resizable=True, sortable=True, filter=True)
gb.configure_column("nombre_display",      header_name="Nombre",              minWidth=220)
gb.configure_column("grupo_parlamentario", header_name="Grupo parlamentario", minWidth=180)
gb.configure_column("partido",             header_name="Partido",             minWidth=160)
gb.configure_column("cargo",               header_name="Cargo actual",        minWidth=120)
gb.configure_column("tipo_eleccion",       header_name="Postula a",           minWidth=160)
gb.configure_column("region",              header_name="Regi\u00f3n",         minWidth=120)
gb.configure_column("score_total",         header_name="Score",               maxWidth=85)
gb.configure_column("etiqueta_riesgo",     header_name="Riesgo",              minWidth=110)
gb.configure_column("tiene_reinfo",        header_name="REINFO",              maxWidth=90)
gb.configure_selection(selection_mode="single", use_checkbox=False)
gb.configure_grid_options(rowStyle=row_style, rowHeight=32, headerHeight=36)

grid_resp = AgGrid(
    df_tabla,
    gridOptions=gb.build(),
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    allow_unsafe_jscode=True,
    height=400,
    theme="alpine",
)

# -------------------------------------------------------
# SECTION: Panel de perfil del congresista seleccionado
# -------------------------------------------------------
selected_raw = grid_resp.get("selected_rows")
if selected_raw is None:
    selected = []
elif hasattr(selected_raw, "empty"):
    selected = [] if selected_raw.empty else selected_raw.to_dict("records")
else:
    selected = list(selected_raw) if selected_raw else []

if selected:
    nombre_sel = selected[0].get("nombre_display", "")
    datos = df_full[df_full["nombre_display"] == nombre_sel]
    if datos.empty:
        st.info("No se encontraron datos completos.")
    else:
        datos = datos.iloc[0]

        # --- Encabezado de perfil ---
        st.markdown(
            '<div style="border-top:3px solid ' + COLOR_PRIMARY + ';margin:28px 0 20px 0;padding-top:20px;">'
            '<p style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 4px 0;">'
            'Perfil del congresista</p>'
            '<h3 style="color:' + COLOR_TEXT_PRIMARY + ';margin:0;'
            'font-size:1.35rem;font-weight:700;letter-spacing:-0.02em;">'
            + str(datos["nombre_display"]) + '</h3>'
            '</div>',
            unsafe_allow_html=True,
        )

        col_datos, col_score = st.columns([3, 1])

        with col_datos:
            # Valores con fallback
            dni_val     = str(datos.get("dni", "—"))
            exp_val     = str(datos.get("expediente", "—"))
            gp_val      = str(datos.get("grupo_parlamentario", "—"))
            partido_val = str(datos.get("partido", "—"))
            cargo_val   = str(datos.get("cargo", "—"))
            region_val  = str(datos.get("region", "—"))
            tipo_val    = str(datos.get("tipo_eleccion", "—"))
            pos_val     = str(datos.get("posicion", "—"))
            estado_val  = str(datos.get("estado_jne", "—"))

            # Badge estado JNE con color semántico
            if estado_val.upper() == "INSCRITO":
                est_color, est_bg = COLOR_RIESGO_BAJO, COLOR_RIESGO_BAJO_BG
            else:
                est_color, est_bg = COLOR_RIESGO_MEDIO, COLOR_RIESGO_MEDIO_BG

            _estado_badge = (
                '<span style="background:' + est_bg + ';color:' + est_color + ';'
                'padding:2px 8px;border-radius:3px;font-size:0.72rem;font-weight:700;'
                'letter-spacing:0.06em;text-transform:uppercase;">' + estado_val + '</span>'
            )

            # Badges de flags (REINFO / Autoría)
            badges_html = ""
            if datos.get("tiene_reinfo"):
                badges_html += (
                    '<span style="background:' + COLOR_REINFO_BG + ';color:' + COLOR_REINFO + ';'
                    'border:1px solid ' + COLOR_REINFO + ';padding:3px 10px;border-radius:3px;'
                    'font-size:0.72rem;font-weight:700;letter-spacing:0.06em;'
                    'text-transform:uppercase;margin-right:6px;">V\u00ednculo REINFO</span>'
                )
            if pd.notna(datos.get("leyes_autoria")) and datos.get("leyes_autoria"):
                badges_html += (
                    '<span style="background:' + COLOR_RIESGO_ALTO_BG + ';color:' + COLOR_RIESGO_ALTO + ';'
                    'border:1px solid ' + COLOR_RIESGO_ALTO + ';padding:3px 10px;border-radius:3px;'
                    'font-size:0.72rem;font-weight:700;letter-spacing:0.06em;'
                    'text-transform:uppercase;">Autor de ley(es) clave</span>'
                )
            badges_block = (
                '<div style="margin-top:14px;display:flex;gap:6px;flex-wrap:wrap;">'
                + badges_html + '</div>'
            ) if badges_html else ""

            _html_card = (
                '<div style="background:' + COLOR_SURFACE + ';border:1px solid ' + COLOR_BORDER + ';'
                'border-radius:8px;padding:20px 24px;">'
                # Fila 1: DNI · Expediente · Estado JNE
                + '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px 24px;">'
                + _field("DNI", dni_val)
                + _field("Expediente JNE", exp_val)
                + '<div><p style="font-size:0.63rem;font-weight:700;letter-spacing:0.10em;'
                'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 4px 0;">'
                'Estado JNE</p>' + _estado_badge + '</div>'
                + '</div>'
                + _sep()
                # Fila 2: Grupo · Partido
                + '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px 24px;">'
                + _field("Grupo parlamentario", gp_val)
                + _field("Partido", partido_val)
                + '</div>'
                + _sep()
                # Fila 3: Cargo · Región · Postula · Posición
                + '<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:16px 24px;">'
                + _field_sm("Cargo actual", cargo_val)
                + _field_sm("Regi\u00f3n", region_val)
                + _field_sm("Postula a 2026", tipo_val)
                + _field_sm("Posici\u00f3n", "#" + pos_val)
                + '</div>'
                + badges_block
                + '</div>'
            )
            st.markdown(_html_card, unsafe_allow_html=True)

        with col_score:
            nivel   = datos.get("nivel_riesgo", "none")
            color_n = {"alto": COLOR_RIESGO_ALTO, "medio": COLOR_RIESGO_MEDIO,
                       "bajo": COLOR_RIESGO_BAJO,  "none": COLOR_RIESGO_NONE}.get(nivel, COLOR_RIESGO_NONE)
            bg_n    = {"alto": COLOR_RIESGO_ALTO_BG, "medio": COLOR_RIESGO_MEDIO_BG,
                       "bajo": COLOR_RIESGO_BAJO_BG,  "none": COLOR_RIESGO_NONE_BG}.get(nivel, COLOR_RIESGO_NONE_BG)

            score       = datos.get("score_total", None)
            score_val   = int(score) if pd.notna(score) else 0
            score_txt   = str(score_val) if pd.notna(score) else "\u2014"
            SCORE_MAX   = 32   # 16 leyes x 2 puntos máx
            score_pct   = min(round(score_val / SCORE_MAX * 100), 100)
            s_procrimen = int(datos.get("score_procrimen", 0) or 0)
            s_contexto  = int(datos.get("score_contexto",  0) or 0)
            s_autoria   = int(datos.get("bonus_autoria",   0) or 0)
            etiqueta    = str(datos.get("etiqueta_riesgo", "Sin dato"))

            _html_score = (
                '<div style="background:' + COLOR_SURFACE + ';border:1px solid ' + COLOR_BORDER + ';'
                'border-top:3px solid ' + color_n + ';border-radius:8px;padding:20px 18px;">'
                '<p style="font-size:0.63rem;font-weight:700;letter-spacing:0.12em;'
                'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 6px 0;">'
                'Score total</p>'
                '<p style="font-size:3.2rem;font-weight:700;color:' + color_n + ';'
                'line-height:1;margin:0 0 4px 0;font-variant-numeric:tabular-nums;'
                'letter-spacing:-0.03em;">' + score_txt + '</p>'
                '<span style="display:inline-block;background:' + bg_n + ';color:' + color_n + ';'
                'border:1px solid ' + color_n + ';padding:2px 9px;border-radius:3px;'
                'font-size:0.70rem;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;'
                'margin-bottom:14px;">' + etiqueta + '</span>'
                # Gauge bar de progreso
                + '<div style="margin-bottom:16px;">'
                '<div style="display:flex;justify-content:space-between;'
                'font-size:0.65rem;color:' + COLOR_TEXT_MUTED + ';margin-bottom:4px;">'
                '<span>0</span><span>m\u00e1x ' + str(SCORE_MAX) + '</span></div>'
                '<div style="background:' + COLOR_BORDER + ';border-radius:4px;height:8px;overflow:hidden;">'
                '<div style="width:' + str(score_pct) + '%;height:100%;background:' + color_n + ';'
                'border-radius:4px;"></div>'
                '</div>'
                '<p style="font-size:0.68rem;color:' + COLOR_TEXT_MUTED + ';'
                'margin:4px 0 0 0;text-align:right;">'
                + str(score_pct) + '% del m\u00e1ximo</p>'
                '</div>'
                # Desglose por componente
                + '<div style="border-top:1px solid ' + COLOR_BORDER + ';padding-top:12px;">'
                + _desglose_row("Pro-crimen", s_procrimen)
                + _desglose_row("Contexto",   s_contexto)
                + _desglose_row("Autor\u00eda", s_autoria)
                + '</div>'
                '</div>'
            )
            st.markdown(_html_score, unsafe_allow_html=True)

        # -------------------------------------------------------
        # SECTION: Tabla de votaciones por ley
        # -------------------------------------------------------
        st.markdown(
            '<div style="margin:28px 0 10px 0;">'
            '<p style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 2px 0;">'
            'Registro de votaci\u00f3n</p>'
            '<p style="font-size:1.05rem;font-weight:700;color:' + COLOR_TEXT_PRIMARY + ';'
            'margin:0;letter-spacing:-0.01em;">Votaciones en leyes clave</p>'
            '</div>',
            unsafe_allow_html=True,
        )

        COLORES_VOTO_BG = {
            "A FAVOR": "#FDECEA", "EN CONTRA": "#EAF4EC",
            "ABSTENCION": "#FEF9E7", "AUSENTE": "#F2F3F4",
            "LICENCIA": "#F2F3F4", "SIN DATO": "#F2F3F4",
        }

        filas_voto = []
        for col in LEYES_COLS:
            if col not in datos.index:
                continue
            voto_val   = str(datos[col]) if pd.notna(datos[col]) else "SIN DATO"
            match_ley  = leyes_df[leyes_df["etiqueta"] == col]
            bloque     = match_ley["bloque"].values[0]       if len(match_ley) > 0 else "—"
            tipo_vot   = match_ley["tipo_votacion"].values[0] if len(match_ley) > 0 else "—"
            fecha      = match_ley["fecha"].values[0]         if len(match_ley) > 0 else "—"
            nombre_ley = col.split(" ", 1)[1] if " " in col else col
            score_voto = 2 if voto_val == "A FAVOR" else (1 if voto_val in ("ABSTENCION", "AUSENTE", "LICENCIA") else 0)
            filas_voto.append({
                "Ley": nombre_ley, "Bloque": bloque, "Voto": voto_val,
                "Score aportado": score_voto, "Fecha": fecha,
                "Tipo votaci\u00f3n": tipo_vot,
            })

        df_votos_perfil = pd.DataFrame(filas_voto)
        COLS_VOTO_DISPLAY = ["Ley", "Bloque", "Voto", "Score aportado", "Fecha", "Tipo votaci\u00f3n"]

        tab_todo, tab_afavor = st.tabs([
            "Todas las leyes (" + str(len(df_votos_perfil)) + ")",
            "Solo A FAVOR (" + str((df_votos_perfil["Voto"] == "A FAVOR").sum()) + ")"
        ])

        def highlight_voto(val):
            return "background-color: " + COLORES_VOTO_BG.get(str(val).upper(), "#F2F3F4") + ";"

        with tab_todo:
            st.dataframe(
                df_votos_perfil[COLS_VOTO_DISPLAY].style.map(highlight_voto, subset=["Voto"]),
                hide_index=True, use_container_width=True, height=380,
            )
        with tab_afavor:
            df_solo_favor = df_votos_perfil[df_votos_perfil["Voto"] == "A FAVOR"]
            if df_solo_favor.empty:
                st.info("Este congresista no registra votos 'A favor' en las leyes analizadas.")
            else:
                st.dataframe(
                    df_solo_favor[COLS_VOTO_DISPLAY].style.map(highlight_voto, subset=["Voto"]),
                    hide_index=True, use_container_width=True,
                    height=min(80 + len(df_solo_favor) * 36, 380),
                )

        # -------------------------------------------------------
        # SECTION: Gráficos — barras apiladas por bloque + donut
        # -------------------------------------------------------
        st.markdown(
            '<div style="margin:28px 0 10px 0;">'
            '<p style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 2px 0;">'
            'An\u00e1lisis visual</p>'
            '<p style="font-size:1.05rem;font-weight:700;color:' + COLOR_TEXT_PRIMARY + ';'
            'margin:0;letter-spacing:-0.01em;">Distribuci\u00f3n de votos por bloque</p>'
            '</div>',
            unsafe_allow_html=True,
        )

        col_graf1, col_graf2 = st.columns([3, 2])

        with col_graf1:
            # Barras horizontales apiladas — todos los bloques siempre visibles.
            # Iteramos BLOQUES_ORDEN explícitamente para que nunca falte un bloque
            # aunque el congresista tenga 0 votos en ese bloque.
            BLOQUES_ORDEN = ["pro-crimen", "reinfo", "ambiental", "espacio-civico", "bicameralidad"]
            BLOQUES_LABEL = {
                "pro-crimen": "Pro-crimen", "reinfo": "REINFO",
                "ambiental": "Ambiental", "espacio-civico": "Espacio c\u00edvico",
                "bicameralidad": "Bicameralidad",
            }

            filas_stack = []
            for bk in BLOQUES_ORDEN:
                sub = df_votos_perfil[df_votos_perfil["Bloque"] == bk]
                filas_stack.append({
                    "Bloque":          BLOQUES_LABEL.get(bk, bk),
                    "A favor":         int((sub["Voto"] == "A FAVOR").sum()),
                    "Ausente/Abstenc": int(sub["Voto"].isin(["AUSENTE", "ABSTENCION", "LICENCIA"]).sum()),
                    "En contra":       int((sub["Voto"] == "EN CONTRA").sum()),
                    "Total":           len(sub),
                })
            df_stack = pd.DataFrame(filas_stack)

            fig_stack = go.Figure()
            for nombre_traza, col_datos_stack, color_traza in [
                ("A favor",                "A favor",         COLOR_RIESGO_ALTO),
                ("Ausente / Abstenci\u00f3n", "Ausente/Abstenc", COLOR_RIESGO_MEDIO),
                ("En contra",              "En contra",       COLOR_RIESGO_BAJO),
            ]:
                vals = df_stack[col_datos_stack].tolist()
                fig_stack.add_trace(go.Bar(
                    name=nombre_traza,
                    y=df_stack["Bloque"].tolist(),
                    x=vals,
                    orientation="h",
                    marker_color=color_traza,
                    text=[str(v) if v > 0 else "" for v in vals],
                    textposition="inside",
                    insidetextanchor="middle",
                    textfont=dict(color="#FFFFFF", size=11),
                    hovertemplate="<b>%{y}</b><br>" + nombre_traza + ": %{x}<extra></extra>",
                ))

            max_total = max(df_stack["Total"].max(), 1)
            fig_stack.update_layout(
                barmode="stack",
                height=240,
                margin=dict(l=0, r=16, t=8, b=8),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(
                    orientation="h", y=-0.22, x=0,
                    font=dict(size=11), bgcolor="rgba(0,0,0,0)",
                ),
                xaxis=dict(
                    showgrid=False, zeroline=False,
                    showticklabels=False, range=[0, max_total],
                ),
                yaxis=dict(
                    showgrid=False, zeroline=False,
                    tickfont=dict(size=12, color=COLOR_TEXT_SECONDARY),
                    autorange="reversed",
                ),
            )
            st.plotly_chart(fig_stack, use_container_width=True)

        with col_graf2:
            # Donut: distribución global de tipos de voto
            ORDEN_VOTO  = ["A FAVOR", "AUSENTE", "ABSTENCION", "LICENCIA", "EN CONTRA", "SIN DATO"]
            LABELS_DISP = {
                "A FAVOR": "A favor", "EN CONTRA": "En contra",
                "ABSTENCION": "Abstenci\u00f3n", "AUSENTE": "Ausente",
                "LICENCIA": "Licencia", "SIN DATO": "Sin dato",
            }
            COL_DONUT = {
                "A FAVOR": COLOR_RIESGO_ALTO, "EN CONTRA": COLOR_RIESGO_BAJO,
                "ABSTENCION": COLOR_RIESGO_MEDIO, "AUSENTE": "#7A95A8",
                "LICENCIA": "#A8BDC8", "SIN DATO": "#C8D4DC",
            }
            voto_counts = df_votos_perfil["Voto"].value_counts()
            labels_ord  = [v for v in ORDEN_VOTO if v in voto_counts.index]
            fig_donut = go.Figure(go.Pie(
                labels=[LABELS_DISP.get(v, v) for v in labels_ord],
                values=[voto_counts[v] for v in labels_ord],
                hole=0.55,
                marker=dict(
                    colors=[COL_DONUT.get(v, "#C8D4DC") for v in labels_ord],
                    line=dict(color=COLOR_SURFACE, width=2),
                ),
                textinfo="percent",
                textfont=dict(size=12, color="#FFFFFF"),
                hovertemplate="<b>%{label}</b><br>%{value} leyes \u00b7 %{percent}<extra></extra>",
                sort=False,
            ))
            fig_donut.update_layout(
                height=260,
                margin=dict(l=0, r=0, t=8, b=8),
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=True,
                legend=dict(
                    orientation="v", x=1.02, y=0.5,
                    font=dict(size=11, color=COLOR_TEXT_SECONDARY),
                    bgcolor="rgba(0,0,0,0)",
                ),
                annotations=[dict(
                    text="<b>" + str(len(df_votos_perfil)) + "</b><br>leyes",
                    x=0.5, y=0.5,
                    font=dict(size=14, color=COLOR_TEXT_PRIMARY),
                    showarrow=False,
                )],
            )
            st.plotly_chart(fig_donut, use_container_width=True)

# -------------------------------------------------------
# SECTION: Footer
# -------------------------------------------------------
st.markdown(
    '<div style="margin-top:32px;padding-top:12px;border-top:1px solid ' + COLOR_BORDER + ';'
    'font-size:0.78em;color:' + COLOR_TEXT_SECONDARY + ';display:flex;justify-content:space-between;">'
    '<span>' + APP_CONFIDENTIAL_LABEL + '</span>'
    '<span>Fuentes: JNE \u00b7 Congreso del Per\u00fa \u00b7 porEstosNo.pe</span>'
    '</div>',
    unsafe_allow_html=True,
)
