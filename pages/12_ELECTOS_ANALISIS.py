# ============================================================
# 12_ELECTOS_ANALISIS.py — Monitor Electoral Perú 2026
# Análisis de candidatos electos proyectados:
#   → Cruce con congresistas 2021-2026 (reelectos)
#   → Score legislativo y votaciones en leyes clave
#   → Vínculos REINFO (minería informal)
#   → Alertas combinadas
#
# NOTA: HTML por concatenación (+), nunca f-strings multilínea
# ni comentarios HTML. Ver arquitectura en 3_CONGRESISTAS.py
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

from config import (
    APP_TITLE, APP_ICON, APP_CONFIDENTIAL_LABEL,
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_BACKGROUND,
    COLOR_SURFACE, COLOR_SURFACE_ALT, COLOR_BORDER, COLOR_BORDER_STRONG,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_RIESGO_ALTO, COLOR_RIESGO_ALTO_BG,
    COLOR_RIESGO_MEDIO, COLOR_RIESGO_MEDIO_BG,
    COLOR_RIESGO_BAJO, COLOR_RIESGO_BAJO_BG,
    COLOR_RIESGO_NONE, COLOR_RIESGO_NONE_BG,
    COLOR_REINFO, COLOR_REINFO_BG,
    LABEL_RIESGO, LEYES_COLS, GLOBAL_CSS,
    COLORES_PARTIDO, SIGLAS_PARTIDO,
)
from data_loader import (
    cargar_electos_con_cruces,
    cargar_votaciones,
    cargar_reinfo,
    cargar_leyes,
)

# ── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Electos 2026 \u00b7 " + APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

if not st.session_state.get("autenticado", False):
    st.warning("Debes iniciar sesi\u00f3n primero.")
    st.stop()


# ── Helpers HTML ──────────────────────────────────────────────────────────────

def _field(label, value):
    return (
        '<div>'
        '<p style="font-size:0.63rem;font-weight:700;letter-spacing:0.10em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 3px 0;">'
        + label + '</p>'
        '<p style="font-size:0.88rem;color:' + COLOR_TEXT_PRIMARY + ';margin:0;font-weight:500;">'
        + str(value) + '</p>'
        '</div>'
    )


def _field_sm(label, value):
    return (
        '<div>'
        '<p style="font-size:0.60rem;font-weight:700;letter-spacing:0.10em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 2px 0;">'
        + label + '</p>'
        '<p style="font-size:0.80rem;color:' + COLOR_TEXT_PRIMARY + ';margin:0;">'
        + str(value) + '</p>'
        '</div>'
    )


def _sep():
    return (
        '<div style="border-top:1px solid ' + COLOR_BORDER + ';'
        'margin:14px 0;"></div>'
    )


def _badge(texto, color, bg):
    return (
        '<span style="background:' + bg + ';color:' + color + ';'
        'border:1px solid ' + color + ';padding:3px 10px;border-radius:0;'
        'font-size:0.70rem;font-weight:700;letter-spacing:0.06em;'
        'text-transform:uppercase;margin-right:6px;">'
        + texto + '</span>'
    )


def _kpi(label, valor, sub="", color=None):
    c = color or COLOR_PRIMARY
    return (
        '<div style="background:' + COLOR_SURFACE + ';border:1px solid ' + COLOR_BORDER + ';'
        'border-top:3px solid ' + c + ';border-radius:0;padding:16px 20px;">'
        '<div style="font-size:0.62rem;font-weight:700;letter-spacing:0.10em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:4px;">'
        + label + '</div>'
        '<div style="font-family:\'Source Serif 4\',Georgia,serif;font-size:1.55rem;'
        'font-weight:500;color:' + c + ';'
        'letter-spacing:-0.02em;font-variant-numeric:tabular-nums;">'
        + str(valor) + '</div>'
        + ('<div style="font-size:0.72rem;color:' + COLOR_TEXT_SECONDARY + ';margin-top:2px;">'
           + sub + '</div>' if sub else '')
        + '</div>'
    )


def _voto_badge(voto: str) -> str:
    """Badge de color para cada tipo de voto en leyes."""
    v = str(voto).strip().upper()
    MAP = {
        "A FAVOR":    ("#C0392B", "#FDECEA"),
        "EN CONTRA":  ("#1E8A4A", "#EAF4EC"),
        "ABSTENCIÓN": ("#D4760A", "#FEF7EC"),
        "ABSTENCION": ("#D4760A", "#FEF7EC"),
        "AUSENTE":    ("#5D6D7E", "#F2F3F4"),
        "SIN DATO":   ("#9AA5B1", "#F8F9FA"),
        "NO VOTÓ":    ("#9AA5B1", "#F8F9FA"),
    }
    color, bg = MAP.get(v, ("#9AA5B1", "#F8F9FA"))
    return (
        '<span style="background:' + bg + ';color:' + color + ';'
        'border:1px solid ' + color + '22;padding:2px 7px;border-radius:3px;'
        'font-size:0.68rem;font-weight:700;white-space:nowrap;">'
        + (v[:10] if len(v) > 10 else v) + '</span>'
    )


def _csv_dl(df, label, filename, key):
    cols_ex = [c for c in df.columns if c.startswith("_")]
    df_c = df.drop(columns=cols_ex, errors="ignore")
    csv = df_c.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(label="\u2b07 " + label, data=csv.encode("utf-8-sig"),
                       file_name=filename, mime="text/csv", key=key)


def _mostrar_perfil_electo(row, df_votos_full, df_reinfo_full, df_leyes_full,
                            expandido: bool = True):
    """
    Panel de perfil completo para un electo seleccionado.
    Muestra: datos básicos, score (si era congresista), votaciones por ley,
    detalle REINFO (si aplica).
    """
    nombre    = str(row.get("nombreCandidato", "—")).title()
    partido   = str(row.get("nombreAgrupacionPolitica", "—"))
    camara    = str(row.get("camara", "—"))
    circ      = str(row.get("circunscripcion", "—"))
    votos     = row.get("totalVotosValidos", 0)
    reelecto  = bool(row.get("era_congresista_2021", False))
    reinfo    = bool(row.get("tiene_reinfo", False))
    score     = row.get("score_total", None)
    nivel     = str(row.get("nivel_riesgo", "none"))
    dni       = str(row.get("dni_candidato", ""))
    color_p   = COLORES_PARTIDO.get(partido, COLORES_PARTIDO["_DEFAULT"])

    # Colores de riesgo
    RIESGO_COLORS = {
        "alto":   (COLOR_RIESGO_ALTO,   COLOR_RIESGO_ALTO_BG),
        "medio":  (COLOR_RIESGO_MEDIO,  COLOR_RIESGO_MEDIO_BG),
        "bajo":   (COLOR_RIESGO_BAJO,   COLOR_RIESGO_BAJO_BG),
        "none":   (COLOR_RIESGO_NONE,   COLOR_RIESGO_NONE_BG),
    }
    risk_color, risk_bg = RIESGO_COLORS.get(nivel, RIESGO_COLORS["none"])

    st.markdown(
        '<div style="border-top:3px solid ' + COLOR_PRIMARY + ';'
        'margin:24px 0 16px 0;padding-top:20px;">'
        '<p style="font-size:0.63rem;font-weight:700;letter-spacing:0.12em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 4px 0;">'
        'Perfil del electo proyectado</p>'
        '<div style="display:flex;align-items:center;gap:12px;">'
        '<div style="width:12px;height:12px;border-radius:50%;background:' + color_p + ';flex-shrink:0;"></div>'
        '<h3 style="color:' + COLOR_TEXT_PRIMARY + ';margin:0;font-size:1.25rem;'
        'font-weight:700;letter-spacing:-0.02em;">' + nombre + '</h3>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    col_info, col_flags = st.columns([3, 1])

    with col_info:
        # Datos básicos
        st.markdown(
            '<div style="background:' + COLOR_SURFACE + ';border:1px solid ' + COLOR_BORDER + ';'
            'border-radius:0;padding:18px 22px;">'
            '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px 20px;">'
            + _field("Partido", partido)
            + _field("C\u00e1mara", camara)
            + _field("Circunscripci\u00f3n", circ)
            + '</div>'
            + _sep()
            + '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px 20px;">'
            + _field_sm("DNI", dni)
            + _field_sm("Votos preferenciales", f"{int(votos):,}" if votos else "—")
            + _field_sm("Período anterior", "Congresista 2021\u201326" if reelecto else "Candidato nuevo")
            + '</div>'
            + '</div>',
            unsafe_allow_html=True,
        )

    with col_flags:
        badges = ""
        if reelecto:
            badges += _badge("Reelecto", COLOR_RIESGO_MEDIO, COLOR_RIESGO_MEDIO_BG) + "<br><br>"
        if reinfo:
            badges += _badge("V\u00ednculo REINFO", COLOR_REINFO, COLOR_REINFO_BG) + "<br><br>"
        if pd.notna(score) and score:
            badges += _badge(
                "Score " + str(int(score)) + " \u00b7 " + LABEL_RIESGO.get(nivel, ""),
                risk_color, risk_bg
            )
        if badges:
            st.markdown(
                '<div style="background:' + COLOR_SURFACE + ';border:1px solid ' + COLOR_BORDER + ';'
                'border-radius:0;padding:18px 16px;display:flex;flex-direction:column;gap:8px;">'
                + badges + '</div>',
                unsafe_allow_html=True,
            )

    # ── Score legislativo (solo reelectos) ────────────────────────────────────
    if reelecto and pd.notna(score):
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:10px;">'
            'Historial legislativo \u00b7 Período 2021\u20132026</div>',
            unsafe_allow_html=True,
        )

        voto_row = df_votos_full[df_votos_full["dni"].astype(str).str.zfill(8) == dni]

        if not voto_row.empty:
            voto_row = voto_row.iloc[0]

            # Score por bloques
            score_proc  = voto_row.get("score_procrimen", 0) or 0
            score_ctx   = voto_row.get("score_contexto", 0) or 0
            score_bonus = voto_row.get("bonus_autoria", 0) or 0
            score_tot   = voto_row.get("score_total", 0) or 0

            sc1, sc2, sc3, sc4 = st.columns(4)
            for col, lbl, val in [
                (sc1, "Score total",    score_tot),
                (sc2, "Procrimen",      score_proc),
                (sc3, "Contexto",       score_ctx),
                (sc4, "Bonus autoría",  score_bonus),
            ]:
                with col:
                    st.markdown(
                        '<div style="background:' + risk_bg + ';border:1px solid ' + risk_color + '44;'
                        'border-radius:6px;padding:10px 14px;text-align:center;">'
                        '<div style="font-size:0.60rem;font-weight:700;letter-spacing:0.10em;'
                        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';">' + lbl + '</div>'
                        '<div style="font-size:1.35rem;font-weight:700;color:' + risk_color + ';'
                        'font-variant-numeric:tabular-nums;">' + str(int(val)) + '</div>'
                        '</div>',
                        unsafe_allow_html=True,
                    )

            # Votaciones por ley
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            st.markdown(
                '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
                'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:8px;">'
                'Votaciones en leyes clave</div>',
                unsafe_allow_html=True,
            )

            # Agrupar leyes por bloque usando df_leyes
            leyes_disponibles = [c for c in LEYES_COLS if c in voto_row.index]

            filas_ley = ""
            for col_ley in leyes_disponibles:
                voto_val = str(voto_row.get(col_ley, "SIN DATO")).strip().upper()
                if voto_val in ("NAN", ""):
                    voto_val = "SIN DATO"

                # Nombre de la ley desde df_leyes si está disponible
                nombre_ley = col_ley
                if df_leyes_full is not None and not df_leyes_full.empty:
                    match = df_leyes_full[df_leyes_full["codigo"] == col_ley]
                    if not match.empty:
                        nombre_ley = str(match.iloc[0].get("nombre_corto", col_ley))

                filas_ley += (
                    '<tr style="border-bottom:1px solid ' + COLOR_BORDER + ';">'
                    '<td style="padding:6px 12px;font-size:0.78rem;color:' + COLOR_TEXT_SECONDARY + ';">'
                    + nombre_ley + '</td>'
                    '<td style="padding:6px 12px;font-size:0.75rem;color:' + COLOR_TEXT_MUTED + ';">'
                    + col_ley + '</td>'
                    '<td style="padding:6px 12px;">' + _voto_badge(voto_val) + '</td>'
                    '</tr>'
                )

            st.markdown(
                '<div style="overflow-x:auto;">'
                '<table style="width:100%;border-collapse:collapse;background:' + COLOR_SURFACE + ';'
                'border:1px solid ' + COLOR_BORDER + ';border-radius:0;overflow:hidden;">'
                '<thead><tr style="background:' + COLOR_SURFACE_ALT + ';border-bottom:2px solid ' + COLOR_BORDER + ';">'
                '<th style="text-align:left;padding:8px 12px;font-size:0.68rem;font-weight:700;'
                'letter-spacing:0.08em;text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';">Ley</th>'
                '<th style="text-align:left;padding:8px 12px;font-size:0.68rem;font-weight:700;'
                'letter-spacing:0.08em;text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';">Código</th>'
                '<th style="text-align:left;padding:8px 12px;font-size:0.68rem;font-weight:700;'
                'letter-spacing:0.08em;text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';">Voto</th>'
                '</tr></thead>'
                '<tbody>' + filas_ley + '</tbody>'
                '</table></div>',
                unsafe_allow_html=True,
            )

    # ── Detalle REINFO ────────────────────────────────────────────────────────
    if reinfo:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:8px;">'
            'V\u00ednculo REINFO \u00b7 Minería informal</div>',
            unsafe_allow_html=True,
        )
        reinfo_row = df_reinfo_full[
            df_reinfo_full["dni"].astype(str).str.zfill(8) == dni
        ]
        if not reinfo_row.empty:
            reinfo_row = reinfo_row.iloc[0]
            n_der      = reinfo_row.get("n_derechos_mineros", "—")
            dptos      = reinfo_row.get("dptos_mineros", "—")
            prior      = reinfo_row.get("es_region_prioritaria", False)
            estado_r   = reinfo_row.get("estado_reinfo_cons", "—")

            st.markdown(
                '<div style="background:' + COLOR_REINFO_BG + ';border:1px solid ' + COLOR_REINFO + ';'
                'border-radius:0;padding:16px 20px;">'
                '<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:14px 20px;">'
                + _field_sm("N\u00ba derechos mineros", str(n_der))
                + _field_sm("Departamentos", str(dptos))
                + _field_sm("Regi\u00f3n prioritaria proyecto", "S\u00ed" if prior else "No")
                + _field_sm("Estado REINFO consolidado", str(estado_r))
                + '</div>'
                '</div>',
                unsafe_allow_html=True,
            )


# ── Carga de datos ────────────────────────────────────────────────────────────
try:
    df_electos = cargar_electos_con_cruces()
    df_votos   = cargar_votaciones()
    df_reinfo  = cargar_reinfo()
    df_leyes   = cargar_leyes()
    DATA_OK    = True
except Exception as e:
    DATA_OK = False
    st.error("Error cargando datos: " + str(e))
    st.stop()

if df_electos.empty:
    st.warning("Sin datos de electos proyectados. Verifica el archivo ONPE.")
    st.stop()

# ── Métricas globales ─────────────────────────────────────────────────────────
total_electos    = len(df_electos)
total_reelectos  = int(df_electos["era_congresista_2021"].sum())
total_reinfo     = int(df_electos["tiene_reinfo"].sum())
total_riesgo_alto = int(
    df_electos[df_electos["nivel_riesgo"].isin(["alto", "muy_alto"])].shape[0]
)
reelectos_reinfo = int(
    df_electos[df_electos["era_congresista_2021"] & df_electos["tiene_reinfo"]].shape[0]
)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="padding:32px 0 8px 0;">'
    '<div style="font-size:0.63rem;font-weight:700;letter-spacing:0.12em;'
    'text-transform:uppercase;color:' + COLOR_ACCENT + ';margin-bottom:8px;">An\u00e1lisis de riesgo</div>'
    '<h1 style="color:' + COLOR_PRIMARY + ';font-size:1.75rem;font-weight:700;'
    'margin:0 0 4px 0;letter-spacing:-0.02em;">Candidatos Electos 2026</h1>'
    '<p style="color:' + COLOR_TEXT_SECONDARY + ';font-size:0.85em;margin:0;">'
    'Electos proyectados cruzados con historial legislativo y v\u00ednculos REINFO \u00b7 '
    'Resultados preliminares al ~85% de escrutinio'
    '</p>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div style="background:#F0F4FA;border:1px solid ' + COLOR_BORDER + ';border-radius:6px;'
    'padding:8px 14px;margin-bottom:20px;font-size:0.80rem;color:' + COLOR_TEXT_SECONDARY + ';">'
    '<strong>Nota metodológica.</strong> Los electos proyectados se calculan con el m\u00e9todo D\'Hondt '
    'aplicando la doble valla JNE (Acuerdo 12/03/2026): \u22655% votos nacionales y m\u00ednimo de esca\u00f1os. '
    'Los cruces con historial legislativo aplican solo a quienes fueron congresistas 2021\u20132026.'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div style="border-top:2px solid ' + COLOR_BORDER + ';margin-bottom:24px;"></div>',
    unsafe_allow_html=True,
)

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(_kpi("Electos proyectados", total_electos, "todas las c\u00e1maras"), unsafe_allow_html=True)
with k2:
    st.markdown(_kpi("Reelectos", total_reelectos,
                     "eran congresistas 2021\u201326",
                     COLOR_RIESGO_MEDIO), unsafe_allow_html=True)
with k3:
    st.markdown(_kpi("Con v\u00ednculo REINFO", total_reinfo,
                     "registro miner\u00eda informal",
                     COLOR_REINFO), unsafe_allow_html=True)
with k4:
    st.markdown(_kpi("Riesgo alto (reelectos)", total_riesgo_alto,
                     "score legislativo \u226520",
                     COLOR_RIESGO_ALTO), unsafe_allow_html=True)
with k5:
    st.markdown(_kpi("Reelecto + REINFO", reelectos_reinfo,
                     "doble alerta",
                     "#6C2FA0"), unsafe_allow_html=True)

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_todos, tab_reelectos, tab_reinfo, tab_alertas = st.tabs([
    "Todos los electos",
    "Reelectos \u00b7 historial legislativo",
    "V\u00ednculos REINFO",
    "Alertas combinadas",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — TODOS LOS ELECTOS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_todos:
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── Filtros ──
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        camaras = ["— Todas —"] + sorted(df_electos["camara"].dropna().unique())
        camara_sel = st.selectbox("C\u00e1mara", camaras, key="f_camara_todos")
    with fc2:
        partidos = ["— Todos —"] + sorted(df_electos["nombreAgrupacionPolitica"].dropna().unique())
        partido_sel = st.selectbox("Partido", partidos, key="f_partido_todos")
    with fc3:
        flags = ["— Todos —", "Reelectos", "Con REINFO", "Reelecto + REINFO"]
        flag_sel = st.selectbox("Filtro especial", flags, key="f_flag_todos")
    with fc4:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        _csv_dl(df_electos, "Descargar todos", "electos_2026_todos.csv", "dl_todos")

    # Aplicar filtros
    df_filt = df_electos.copy()
    if camara_sel != "— Todas —":
        df_filt = df_filt[df_filt["camara"] == camara_sel]
    if partido_sel != "— Todos —":
        df_filt = df_filt[df_filt["nombreAgrupacionPolitica"] == partido_sel]
    if flag_sel == "Reelectos":
        df_filt = df_filt[df_filt["era_congresista_2021"] == True]
    elif flag_sel == "Con REINFO":
        df_filt = df_filt[df_filt["tiene_reinfo"] == True]
    elif flag_sel == "Reelecto + REINFO":
        df_filt = df_filt[df_filt["era_congresista_2021"] & df_filt["tiene_reinfo"]]

    st.markdown(
        '<div style="font-size:0.78rem;color:' + COLOR_TEXT_SECONDARY + ';margin-bottom:8px;">'
        'Mostrando <strong>' + str(len(df_filt)) + '</strong> candidatos electos. '
        'Haz clic en una fila para ver el perfil completo.'
        '</div>',
        unsafe_allow_html=True,
    )

    # Preparar tabla para AgGrid
    cols_tabla = ["nombreCandidato", "nombreAgrupacionPolitica", "camara",
                  "circunscripcion", "totalVotosValidos",
                  "era_congresista_2021", "tiene_reinfo", "nivel_riesgo", "score_total"]
    df_tabla = df_filt[[c for c in cols_tabla if c in df_filt.columns]].copy()
    df_tabla = df_tabla.rename(columns={
        "nombreCandidato":           "Nombre",
        "nombreAgrupacionPolitica":  "Partido",
        "camara":                    "C\u00e1mara",
        "circunscripcion":           "Circunscripci\u00f3n",
        "totalVotosValidos":         "Votos",
        "era_congresista_2021":      "Reelecto",
        "tiene_reinfo":              "REINFO",
        "nivel_riesgo":              "Nivel riesgo",
        "score_total":               "Score",
    })
    df_tabla["Reelecto"] = df_tabla["Reelecto"].map({True: "Sí", False: "No"}) if "Reelecto" in df_tabla.columns else "—"
    df_tabla["REINFO"]   = df_tabla["REINFO"].map({True: "Sí", False: "No"}) if "REINFO" in df_tabla.columns else "—"
    df_tabla["Nivel riesgo"] = df_tabla["Nivel riesgo"].map(LABEL_RIESGO).fillna("—") if "Nivel riesgo" in df_tabla.columns else "—"
    df_tabla["Score"] = df_tabla["Score"].fillna("—") if "Score" in df_tabla.columns else "—"

    row_style_todos = JsCode("""
    function(params) {
        var reinfo  = params.data['REINFO'];
        var reelecto = params.data['Reelecto'];
        var riesgo  = params.data['Nivel riesgo'] || '';
        if (reinfo === 'Sí' && reelecto === 'Sí') return {'background-color': '#F3E8FD'};
        if (reinfo === 'Sí')   return {'background-color': '#FEF7EC'};
        if (riesgo.includes('Alto'))  return {'background-color': '#FDECEA'};
        if (riesgo.includes('Medio')) return {'background-color': '#FEF9E7'};
        return {};
    }
    """)

    gb = GridOptionsBuilder.from_dataframe(df_tabla)
    gb.configure_default_column(resizable=True, sortable=True, filter=True)
    gb.configure_column("Nombre",             minWidth=220)
    gb.configure_column("Partido",            minWidth=200)
    gb.configure_column("C\u00e1mara",        minWidth=150)
    gb.configure_column("Circunscripci\u00f3n", minWidth=160)
    gb.configure_column("Votos",              minWidth=100, type=["numericColumn"])
    gb.configure_column("Reelecto",           maxWidth=100)
    gb.configure_column("REINFO",             maxWidth=90)
    gb.configure_column("Score",              maxWidth=80)
    gb.configure_column("Nivel riesgo",       minWidth=120)
    gb.configure_selection(selection_mode="single", use_checkbox=False)
    gb.configure_grid_options(rowStyle=row_style_todos, rowHeight=32, headerHeight=36)

    grid_resp = AgGrid(
        df_tabla,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        height=420,
        theme="alpine",
        key="grid_todos",
    )

    # ── Panel de perfil al seleccionar ────────────────────────────────────────
    selected_raw = grid_resp.get("selected_rows")
    if selected_raw is None:
        selected = []
    elif hasattr(selected_raw, "empty"):
        selected = [] if selected_raw.empty else selected_raw.to_dict("records")
    else:
        selected = list(selected_raw) if selected_raw else []

    if selected:
        nombre_sel = selected[0].get("Nombre", "")
        row = df_filt[df_filt["nombreCandidato"] == nombre_sel]
        if not row.empty:
            row = row.iloc[0]
            _mostrar_perfil_electo(row, df_votos, df_reinfo, df_leyes)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — REELECTOS · HISTORIAL LEGISLATIVO
# ═══════════════════════════════════════════════════════════════════════════════
with tab_reelectos:
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    df_reelectos = df_electos[df_electos["era_congresista_2021"] == True].copy()

    if df_reelectos.empty:
        st.info("No se encontraron reelectos con datos del período 2021-2026.")
    else:
        st.markdown(
            '<div style="font-size:0.78rem;color:' + COLOR_TEXT_SECONDARY + ';margin-bottom:12px;">'
            '<strong>' + str(len(df_reelectos)) + '</strong> congresistas del período 2021\u20132026 '
            'resultaron electos proyectados en 2026. Haz clic en una fila para ver su historial.'
            '</div>',
            unsafe_allow_html=True,
        )

        # Filtros
        fr1, fr2, fr3 = st.columns([2, 2, 1])
        with fr1:
            partidos_r = ["— Todos —"] + sorted(df_reelectos["nombreAgrupacionPolitica"].dropna().unique())
            partido_r_sel = st.selectbox("Partido", partidos_r, key="f_partido_r")
        with fr2:
            niveles = ["— Todos —", "Alto", "Medio", "Bajo", "Sin score"]
            nivel_sel = st.selectbox("Nivel de riesgo", niveles, key="f_nivel_r")
        with fr3:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            _csv_dl(df_reelectos, "Descargar", "reelectos_2026.csv", "dl_reelectos")

        df_re_filt = df_reelectos.copy()
        if partido_r_sel != "— Todos —":
            df_re_filt = df_re_filt[df_re_filt["nombreAgrupacionPolitica"] == partido_r_sel]
        if nivel_sel == "Alto":
            df_re_filt = df_re_filt[df_re_filt["nivel_riesgo"] == "alto"]
        elif nivel_sel == "Medio":
            df_re_filt = df_re_filt[df_re_filt["nivel_riesgo"] == "medio"]
        elif nivel_sel == "Bajo":
            df_re_filt = df_re_filt[df_re_filt["nivel_riesgo"] == "bajo"]
        elif nivel_sel == "Sin score":
            df_re_filt = df_re_filt[df_re_filt["score_total"].isna()]

        # Tabla AgGrid
        cols_r = ["nombreCandidato", "nombreAgrupacionPolitica", "camara",
                  "circunscripcion", "score_total", "nivel_riesgo", "tiene_reinfo"]
        df_r_tabla = df_re_filt[[c for c in cols_r if c in df_re_filt.columns]].copy()
        df_r_tabla = df_r_tabla.rename(columns={
            "nombreCandidato":          "Nombre",
            "nombreAgrupacionPolitica": "Partido",
            "camara":                   "C\u00e1mara",
            "circunscripcion":          "Circunscripci\u00f3n",
            "score_total":              "Score",
            "nivel_riesgo":             "Nivel riesgo",
            "tiene_reinfo":             "REINFO",
        })
        df_r_tabla["Nivel riesgo"] = df_r_tabla["Nivel riesgo"].map(LABEL_RIESGO).fillna("Sin score") if "Nivel riesgo" in df_r_tabla.columns else "—"
        df_r_tabla["REINFO"] = df_r_tabla["REINFO"].map({True: "Sí", False: "No"}) if "REINFO" in df_r_tabla.columns else "—"

        row_style_r = JsCode("""
        function(params) {
            var riesgo = params.data['Nivel riesgo'] || '';
            var reinfo = params.data['REINFO'];
            if (reinfo === 'Sí' && riesgo.includes('Alto')) return {'background-color': '#F3E8FD'};
            if (riesgo.includes('Alto'))  return {'background-color': '#FDECEA'};
            if (riesgo.includes('Medio')) return {'background-color': '#FEF9E7'};
            if (riesgo.includes('Bajo'))  return {'background-color': '#EAF4EC'};
            return {};
        }
        """)

        gb_r = GridOptionsBuilder.from_dataframe(df_r_tabla)
        gb_r.configure_default_column(resizable=True, sortable=True, filter=True)
        gb_r.configure_column("Nombre",             minWidth=220)
        gb_r.configure_column("Partido",            minWidth=200)
        gb_r.configure_column("C\u00e1mara",        minWidth=150)
        gb_r.configure_column("Circunscripci\u00f3n", minWidth=150)
        gb_r.configure_column("Score",              maxWidth=85, type=["numericColumn"])
        gb_r.configure_column("Nivel riesgo",       minWidth=120)
        gb_r.configure_column("REINFO",             maxWidth=90)
        gb_r.configure_selection(selection_mode="single", use_checkbox=False)
        gb_r.configure_grid_options(rowStyle=row_style_r, rowHeight=32, headerHeight=36)

        grid_r = AgGrid(
            df_r_tabla,
            gridOptions=gb_r.build(),
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            allow_unsafe_jscode=True,
            height=380,
            theme="alpine",
            key="grid_reelectos",
        )

        # Perfil al seleccionar
        sel_r_raw = grid_r.get("selected_rows")
        if sel_r_raw is None:
            sel_r = []
        elif hasattr(sel_r_raw, "empty"):
            sel_r = [] if sel_r_raw.empty else sel_r_raw.to_dict("records")
        else:
            sel_r = list(sel_r_raw) if sel_r_raw else []

        if sel_r:
            nombre_r = sel_r[0].get("Nombre", "")
            row_r = df_re_filt[df_re_filt["nombreCandidato"] == nombre_r]
            if not row_r.empty:
                _mostrar_perfil_electo(row_r.iloc[0], df_votos, df_reinfo, df_leyes)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — VÍNCULOS REINFO
# ═══════════════════════════════════════════════════════════════════════════════
with tab_reinfo:
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    df_con_reinfo = df_electos[df_electos["tiene_reinfo"] == True].copy()

    if df_con_reinfo.empty:
        st.success("Ningún electo proyectado tiene vínculo REINFO en la base de datos.")
    else:
        st.markdown(
            '<div style="background:' + COLOR_REINFO_BG + ';border:1px solid ' + COLOR_REINFO + ';'
            'border-radius:6px;padding:10px 14px;margin-bottom:16px;'
            'font-size:0.82rem;color:' + COLOR_REINFO + ';">'
            '<strong>' + str(len(df_con_reinfo)) + ' candidatos electos proyectados</strong> '
            'tienen registro en REINFO (minería informal). '
            + ('<strong>' + str(reelectos_reinfo) + ' son reelectos</strong> con historial legislativo disponible.'
               if reelectos_reinfo else '') +
            '</div>',
            unsafe_allow_html=True,
        )

        fi1, fi2 = st.columns([3, 1])
        with fi1:
            partidos_i = ["— Todos —"] + sorted(df_con_reinfo["nombreAgrupacionPolitica"].dropna().unique())
            partido_i_sel = st.selectbox("Partido", partidos_i, key="f_partido_reinfo")
        with fi2:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            _csv_dl(df_con_reinfo, "Descargar", "electos_con_reinfo.csv", "dl_reinfo_tab")

        df_i_filt = df_con_reinfo.copy()
        if partido_i_sel != "— Todos —":
            df_i_filt = df_i_filt[df_i_filt["nombreAgrupacionPolitica"] == partido_i_sel]

        # Enriquecer con datos REINFO
        df_reinfo_det = df_reinfo[["dni", "n_derechos_mineros", "dptos_mineros",
                                    "es_region_prioritaria", "estado_reinfo_cons"]].copy()
        df_reinfo_det["dni"] = df_reinfo_det["dni"].astype(str).str.zfill(8)
        df_i_filt = df_i_filt.merge(df_reinfo_det,
                                     left_on="dni_candidato", right_on="dni", how="left")

        cols_i = ["nombreCandidato", "nombreAgrupacionPolitica", "camara",
                  "circunscripcion", "era_congresista_2021",
                  "n_derechos_mineros", "dptos_mineros", "es_region_prioritaria"]
        df_i_tabla = df_i_filt[[c for c in cols_i if c in df_i_filt.columns]].copy()
        df_i_tabla = df_i_tabla.rename(columns={
            "nombreCandidato":          "Nombre",
            "nombreAgrupacionPolitica": "Partido",
            "camara":                   "C\u00e1mara",
            "circunscripcion":          "Circunscripci\u00f3n",
            "era_congresista_2021":     "Reelecto",
            "n_derechos_mineros":       "N\u00ba derechos",
            "dptos_mineros":            "Departamentos",
            "es_region_prioritaria":    "Regi\u00f3n prioritaria",
        })
        df_i_tabla["Reelecto"] = df_i_tabla["Reelecto"].map({True: "Sí", False: "No"}) if "Reelecto" in df_i_tabla.columns else "—"
        df_i_tabla["Regi\u00f3n prioritaria"] = df_i_tabla["Regi\u00f3n prioritaria"].map(
            {True: "Sí", False: "No", 1: "Sí", 0: "No"}).fillna("—") if "Regi\u00f3n prioritaria" in df_i_tabla.columns else "—"

        row_style_i = JsCode("""
        function(params) {
            var prior = params.data['Región prioritaria'];
            var reelecto = params.data['Reelecto'];
            if (prior === 'Sí' && reelecto === 'Sí') return {'background-color': '#F3E8FD'};
            if (prior === 'Sí')    return {'background-color': '#FEF7EC'};
            if (reelecto === 'Sí') return {'background-color': '#EAF4EC'};
            return {};
        }
        """)

        gb_i = GridOptionsBuilder.from_dataframe(df_i_tabla)
        gb_i.configure_default_column(resizable=True, sortable=True, filter=True)
        gb_i.configure_column("Nombre",              minWidth=220)
        gb_i.configure_column("Partido",             minWidth=190)
        gb_i.configure_column("C\u00e1mara",         minWidth=140)
        gb_i.configure_column("Circunscripci\u00f3n", minWidth=160)
        gb_i.configure_column("Reelecto",            maxWidth=95)
        gb_i.configure_column("N\u00ba derechos",    maxWidth=110, type=["numericColumn"])
        gb_i.configure_column("Departamentos",       minWidth=180)
        gb_i.configure_column("Regi\u00f3n prioritaria", maxWidth=140)
        gb_i.configure_selection(selection_mode="single", use_checkbox=False)
        gb_i.configure_grid_options(rowStyle=row_style_i, rowHeight=32, headerHeight=36)

        grid_i = AgGrid(
            df_i_tabla,
            gridOptions=gb_i.build(),
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            allow_unsafe_jscode=True,
            height=380,
            theme="alpine",
            key="grid_reinfo",
        )

        # Perfil al seleccionar
        sel_i_raw = grid_i.get("selected_rows")
        if sel_i_raw is None:
            sel_i = []
        elif hasattr(sel_i_raw, "empty"):
            sel_i = [] if sel_i_raw.empty else sel_i_raw.to_dict("records")
        else:
            sel_i = list(sel_i_raw) if sel_i_raw else []

        if sel_i:
            nombre_i = sel_i[0].get("Nombre", "")
            row_i = df_i_filt[df_i_filt["nombreCandidato"] == nombre_i]
            if not row_i.empty:
                _mostrar_perfil_electo(row_i.iloc[0], df_votos, df_reinfo, df_leyes)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ALERTAS COMBINADAS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_alertas:
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Reelecto + REINFO
    df_alerta_max = df_electos[
        df_electos["era_congresista_2021"] & df_electos["tiene_reinfo"]
    ].copy()

    # Reelecto + score alto
    df_alerta_score = df_electos[
        df_electos["era_congresista_2021"] &
        df_electos["nivel_riesgo"].isin(["alto"])
    ].copy()

    # Con REINFO + región prioritaria
    df_reinfo_prior = df_reinfo[df_reinfo["es_region_prioritaria"] == True][["dni"]].copy()
    df_reinfo_prior["dni"] = df_reinfo_prior["dni"].astype(str).str.zfill(8)
    dni_prior = set(df_reinfo_prior["dni"])
    df_alerta_region = df_electos[df_electos["dni_candidato"].isin(dni_prior)].copy()

    st.markdown(
        '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:16px;">'
        'Intersección de criterios de riesgo — candidatos que activan múltiples alertas'
        '</div>',
        unsafe_allow_html=True,
    )

    al1, al2, al3 = st.columns(3)
    with al1:
        st.markdown(
            _kpi("Reelecto + REINFO", len(df_alerta_max),
                 "historial legislativo y minería", "#6C2FA0"),
            unsafe_allow_html=True,
        )
    with al2:
        st.markdown(
            _kpi("Reelecto + riesgo alto", len(df_alerta_score),
                 "score legislativo \u226520", COLOR_RIESGO_ALTO),
            unsafe_allow_html=True,
        )
    with al3:
        st.markdown(
            _kpi("REINFO en región prioritaria", len(df_alerta_region),
                 "Ucayali, Loreto, MdD, Puno", COLOR_REINFO),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Alerta máxima: reelecto + REINFO + score alto
    df_triple = df_electos[
        df_electos["era_congresista_2021"] &
        df_electos["tiene_reinfo"] &
        df_electos["nivel_riesgo"].isin(["alto"])
    ].copy()

    if not df_triple.empty:
        st.markdown(
            '<div style="background:#F0EDF8;border:1px solid #4A2E7A;border-radius:0;'
            'border-left:4px solid #4A2E7A;padding:10px 14px;margin-bottom:12px;">'
            '<strong style="color:#4A2E7A;">Alerta m\u00e1xima \u2014 triple criterio ('
            + str(len(df_triple)) + ' candidatos):</strong> '
            'reelectos con score legislativo alto Y v\u00ednculo REINFO.'
            '</div>',
            unsafe_allow_html=True,
        )
        for _, row in df_triple.iterrows():
            color_p = COLORES_PARTIDO.get(row["nombreAgrupacionPolitica"],
                                           COLORES_PARTIDO["_DEFAULT"])
            st.markdown(
                '<div style="background:' + COLOR_SURFACE + ';border-left:4px solid #4A2E7A;'
                'border:1px solid ' + COLOR_BORDER + ';border-left:4px solid #4A2E7A;'
                'border-radius:0;padding:12px 16px;margin-bottom:8px;">'
                '<div style="display:flex;align-items:center;gap:10px;">'
                '<div style="width:10px;height:10px;border-radius:50%;background:' + color_p + ';flex-shrink:0;"></div>'
                '<strong style="font-size:0.90rem;color:' + COLOR_TEXT_PRIMARY + ';">'
                + str(row["nombreCandidato"]).title() + '</strong>'
                '<span style="font-size:0.75rem;color:' + COLOR_TEXT_MUTED + ';">'
                + str(row["nombreAgrupacionPolitica"]) + ' \u00b7 '
                + str(row["camara"]) + ' \u00b7 '
                + str(row.get("circunscripcion", "")) + '</span>'
                '</div>'
                '<div style="display:flex;gap:6px;margin-top:8px;">'
                + _badge("Score " + str(int(row["score_total"])) if pd.notna(row.get("score_total")) else "Score —",
                         COLOR_RIESGO_ALTO, COLOR_RIESGO_ALTO_BG)
                + _badge("V\u00ednculo REINFO", COLOR_REINFO, COLOR_REINFO_BG)
                + _badge("Reelecto 2021-26", COLOR_RIESGO_MEDIO, COLOR_RIESGO_MEDIO_BG)
                + '</div>'
                '</div>',
                unsafe_allow_html=True,
            )
    else:
        st.success("Ningún electo proyectado activa los tres criterios simultáneamente.")

    st.markdown(
        '<div style="border-top:1px solid ' + COLOR_BORDER + ';margin:20px 0 14px 0;"></div>',
        unsafe_allow_html=True,
    )

    # Tabla completa de alertas combinadas (reelecto + REINFO)
    if not df_alerta_max.empty:
        st.markdown(
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:10px;">'
            'Detalle — Reelectos con vínculo REINFO</div>',
            unsafe_allow_html=True,
        )
        col_dl_al, _ = st.columns([1, 4])
        with col_dl_al:
            _csv_dl(df_alerta_max, "Descargar", "alertas_reelecto_reinfo.csv", "dl_alertas")

        for _, row in df_alerta_max.sort_values(
            "score_total", ascending=False, na_position="last"
        ).iterrows():
            _mostrar_perfil_electo(row, df_votos, df_reinfo, df_leyes,
                                    expandido=False)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="page-footer">'
    '<span>Monitor Electoral Per\u00fa 2026 \u00b7 OACNUDH</span>'
    '<span>Fuente: ONPE \u00b7 JNE \u00b7 REINFO \u00b7 porEstosNo.pe</span>'
    '</div>',
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIÓN PERFIL — definida al final para referenciarla desde los tabs
# (Python permite llamar funciones antes de definirlas si están en el mismo
# módulo, pero para mayor claridad la incluimos después de los tabs)
# ═══════════════════════════════════════════════════════════════════════════════