# ============================================================
# pages/9_PERFIL_VICTIMA.py — Monitor Electoral Perú 2026
# Módulo de violencia electoral — Perfil individual de víctima.
# AgGrid + panel expandible + cruce con Monitor Electoral.
# ============================================================

import streamlit as st
import pandas as pd
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    APP_TITLE, APP_ICON, APP_CONFIDENTIAL_LABEL, APP_VERSION,
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_BACKGROUND, COLOR_SURFACE,
    COLOR_BORDER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_RIESGO_ALTO, COLOR_RIESGO_ALTO_BG,
    COLOR_RIESGO_MEDIO, COLOR_RIESGO_MEDIO_BG,
    COLOR_RIESGO_BAJO, COLOR_RIESGO_BAJO_BG,
    COLOR_RIESGO_NONE, GLOBAL_CSS,
    SCORE_ALTO_MIN, SCORE_MEDIO_MIN,
)
from data_loader_violencia import (
    cargar_datos_violencia, limpiar_cache_violencia, _buscar_candidato,
)

# Intentar cargar df_candidatos del monitor electoral
try:
    from data_loader import cargar_candidatos
    _df_candidatos = cargar_candidatos()
except Exception:
    _df_candidatos = None

# -------------------------------------------------------
# SECTION: Page setup
# -------------------------------------------------------
st.set_page_config(
    page_title="Perfil V\u00edctima \u00b7 " + APP_TITLE,
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
        + "Perfil de presunta v\u00edctima</div>"
        + "<div style='font-size:0.82rem; color:" + COLOR_TEXT_SECONDARY + "; margin-top:2px;'>"
        + "Ficha individual con todos los incidentes asociados y cruce con Monitor Electoral \u00b7 "
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
# SECTION: Helper — badge de tipo de víctima
# -------------------------------------------------------
_BADGE_TIPO = {
    "Individual":                   ("badge-medio",  "Individual"),
    "Colectivo":                    ("badge-none",   "Colectivo"),
    "Organizaciones / Instituciones":("badge-none",  "Organizaci\u00f3n"),
}

def _badge_tipo(tipo: str) -> str:
    cls, label = _BADGE_TIPO.get(str(tipo), ("badge-none", str(tipo)))
    return f"<span class='badge {cls}'>{label}</span>"

def _badge_victima_perfil(row) -> str:
    """Badge contextual según el rol de la víctima."""
    cargo = row.get("cargo_postula")
    factor = str(row.get("factor_diferencial") or "")
    if pd.notna(cargo) and str(cargo).strip():
        return "<span class='badge badge-alto'>Candidata/o</span>"
    if "periodista" in factor.lower() or "comunicadores" in factor.lower():
        return "<span class='badge badge-medio'>Periodista/Comunicador</span>"
    if "autoridades electorales" in factor.lower():
        return "<span class='badge badge-medio'>Funcionario Electoral</span>"
    if "pueblos ind\u00edgenas" in factor.lower():
        return "<span class='badge badge-bajo'>Pueblos Ind\u00edgenas</span>"
    return "<span class='badge badge-none'>V\u00edctima</span>"

def _badge_confianza(confianza: str) -> str:
    mapa = {
        "EXACTO":        ("badge-bajo",  "EXACTO"),
        "PROBABLE":      ("badge-medio", "PROBABLE"),
        "NO ENCONTRADO": ("badge-none",  "NO ENCONTRADO"),
    }
    cls, label = mapa.get(confianza, ("badge-none", confianza))
    return f"<span class='badge {cls}'>{label}</span>"

# -------------------------------------------------------
# SECTION: Buscador / selector de víctima
# -------------------------------------------------------
st.markdown(
    "<div class='section-header'>Seleccionar presunta v\u00edctima</div>"
    "<div class='section-subheader'>Busca por nombre, partido o tipo de v\u00edctima</div>",
    unsafe_allow_html=True,
)

col_bus, col_fil = st.columns([3, 1])
with col_bus:
    busqueda = st.text_input(
        "Buscar", placeholder="Nombre, partido o n\u00famero de serie...",
        label_visibility="collapsed",
    )
with col_fil:
    tipos_filter = ["Todos"] + sorted(df_joined["tipo_victima"].dropna().unique().tolist()) \
                   if "tipo_victima" in df_joined.columns else ["Todos"]
    f_tipo_sel = st.selectbox("Tipo", tipos_filter, label_visibility="collapsed")

# Construir tabla para selección
df_sel = df_joined.copy()
if busqueda.strip():
    mask = pd.Series(False, index=df_sel.index)
    for col_search in ["nombre", "org_politica", "num_serie_victima", "num_serie_incidente"]:
        if col_search in df_sel.columns:
            mask |= df_sel[col_search].astype(str).str.contains(
                busqueda, case=False, na=False
            )
    df_sel = df_sel[mask]
if f_tipo_sel != "Todos" and "tipo_victima" in df_sel.columns:
    df_sel = df_sel[df_sel["tipo_victima"] == f_tipo_sel]

# Tabla de selección
cols_tabla = [c for c in ["num_serie_victima", "nombre", "tipo_victima",
                           "cargo_postula", "org_politica", "genero",
                           "num_serie_incidente", "region", "tipo_ataque"]
              if c in df_sel.columns]

df_tabla_show = df_sel[cols_tabla].copy()
df_tabla_show.columns = [c.replace("_", " ").title() for c in cols_tabla]
st.dataframe(df_tabla_show, use_container_width=True, height=240)

# Selector de víctima individual
victimas_opciones = df_sel["num_serie_victima"].dropna().unique().tolist() \
                    if "num_serie_victima" in df_sel.columns else []
if not victimas_opciones:
    st.info("No se encontraron v\u00edctimas con los criterios aplicados.")
    st.stop()

serie_sel = st.selectbox(
    "Selecciona una v\u00edctima para ver su ficha completa",
    victimas_opciones,
)

# Obtener TODOS los registros de esta víctima (puede tener varios incidentes)
df_vic_sel = df_joined[df_joined["num_serie_victima"] == serie_sel]
if df_vic_sel.empty:
    st.warning("No se encontr\u00f3 informaci\u00f3n para esta v\u00edctima.")
    st.stop()

# Datos base de la víctima (primer registro, la información personal no varía)
row_vic = df_vic_sel.iloc[0]

# -------------------------------------------------------
# SECTION: Ficha de la víctima
# -------------------------------------------------------
st.markdown(
    "<div style='border-top:2px solid " + COLOR_BORDER + "; margin:20px 0 16px 0;'></div>",
    unsafe_allow_html=True,
)

# Nombre + badges
nombre_display = str(row_vic.get("nombre", "Presunta v\u00edctima"))
badge_perfil   = _badge_victima_perfil(row_vic)
badge_tipo     = _badge_tipo(str(row_vic.get("tipo_victima", "")))
vbg_badge      = ("<span class='badge badge-alto' style='margin-left:6px;'>VBG</span>"
                   if row_vic.get("tiene_vbg") else "")

st.markdown(
    "<div style='margin-bottom:16px;'>"
    "<div style='font-size:1.35rem; font-weight:700; color:" + COLOR_TEXT_PRIMARY + ";"
    " margin-bottom:6px;'>" + nombre_display + "</div>"
    "<div>" + badge_perfil + " " + badge_tipo + vbg_badge + "</div>"
    "</div>",
    unsafe_allow_html=True,
)

# Layout principal: perfil izq + incidentes der
col_perfil, col_incidentes = st.columns([2, 3], gap="medium")

# --- Panel izquierdo: perfil completo ---
with col_perfil:

    # Identidad
    st.markdown(
        "<div style='font-size:0.75rem; font-weight:700; letter-spacing:0.08em;"
        " text-transform:uppercase; color:" + COLOR_TEXT_MUTED + "; margin-bottom:8px;'>"
        "Perfil</div>",
        unsafe_allow_html=True,
    )
    campos_perfil = [
        ("Tipo de v\u00edctima",    "tipo_victima"),
        ("Perfil",                  "perfil"),
        ("Cargo que postula",       "cargo_postula"),
        ("Partido / Movimiento",    "org_politica"),
        ("Afiliaci\u00f3n pol\u00edtica", "afiliacion_politica"),
        ("Factor diferencial",      "factor_diferencial"),
        ("Actividad HRD",           "actividad_hrd"),
        ("Instituci\u00f3n electoral",    "institucion_electoral"),
        ("Reportada en HRD",        "en_hrd"),
    ]
    html_perfil = "<div class='profile-card'>"
    for label, key in campos_perfil:
        val = row_vic.get(key)
        if pd.notna(val) and str(val).strip() and str(val) not in ("nan", "None"):
            html_perfil += (
                "<div class='profile-field'>"
                "<strong>" + label + ":</strong> " + str(val)
                + "</div>"
            )
    html_perfil += "</div>"
    st.markdown(html_perfil, unsafe_allow_html=True)

    # Interseccionalidad
    st.markdown(
        "<div style='font-size:0.75rem; font-weight:700; letter-spacing:0.08em;"
        " text-transform:uppercase; color:" + COLOR_TEXT_MUTED + "; margin:14px 0 8px 0;'>"
        "Identidad</div>",
        unsafe_allow_html=True,
    )
    campos_id = [
        ("G\u00e9nero",             "genero"),
        ("Orientaci\u00f3n sexual", "orientacion_sexual"),
        ("Persona transg\u00e9nero","es_trans"),
        ("Identidad \u00e9tnica",   "etnia"),
        ("Rango de edad",           "edad"),
        ("Nacionalidad",            "nacionalidad"),
        ("Discapacidad",            "discapacidad"),
        ("Tipo de discapacidad",    "tipo_discapacidad"),
    ]
    html_id = "<div class='profile-card'>"
    for label, key in campos_id:
        val = row_vic.get(key)
        if pd.notna(val) and str(val).strip() and str(val) not in ("nan", "None", "No"):
            html_id += (
                "<div class='profile-field'>"
                "<strong>" + label + ":</strong> " + str(val)
                + "</div>"
            )
    html_id += "</div>"
    st.markdown(html_id, unsafe_allow_html=True)

    # VBG (condicional)
    if row_vic.get("tiene_vbg"):
        st.markdown(
            "<div style='font-size:0.75rem; font-weight:700; letter-spacing:0.08em;"
            " text-transform:uppercase; color:" + COLOR_RIESGO_ALTO + "; margin:14px 0 8px 0;'>"
            "Violencia de g\u00e9nero</div>",
            unsafe_allow_html=True,
        )
        campos_vbg = [
            ("Tipo de violencia",  "tipo_vbg"),
            ("Elementos VBG",      "elementos_vbg"),
        ]
        html_vbg = (
            "<div class='profile-card' style='border-left:3px solid "
            + COLOR_RIESGO_ALTO + ";'>"
        )
        for label, key in campos_vbg:
            val = row_vic.get(key)
            if pd.notna(val) and str(val).strip() and str(val) not in ("nan", "None"):
                html_vbg += (
                    "<div class='profile-field'>"
                    "<strong>" + label + ":</strong> " + str(val)
                    + "</div>"
                )
        html_vbg += "</div>"
        st.markdown(html_vbg, unsafe_allow_html=True)

    # Respuesta institucional
    st.markdown(
        "<div style='font-size:0.75rem; font-weight:700; letter-spacing:0.08em;"
        " text-transform:uppercase; color:" + COLOR_TEXT_MUTED + "; margin:14px 0 8px 0;'>"
        "Respuesta institucional</div>",
        unsafe_allow_html=True,
    )
    campos_resp = [
        ("Denuncia/reporte",    "instancia_denuncia"),
        ("Otra instancia",      "instancia_denuncia_otra"),
        ("Medidas de protecci\u00f3n", "medidas_proteccion"),
        ("Resultado",           "resultado_denuncia"),
        ("Cronolog\u00eda",     "cronologia"),
    ]
    html_resp = "<div class='profile-card'>"
    for label, key in campos_resp:
        val = row_vic.get(key)
        if pd.notna(val) and str(val).strip() and str(val) not in ("nan", "None"):
            html_resp += (
                "<div class='profile-field'>"
                "<strong>" + label + ":</strong> " + str(val)
                + "</div>"
            )
    html_resp += "</div>"
    st.markdown(html_resp, unsafe_allow_html=True)


# --- Panel derecho: todos los incidentes asociados ---
with col_incidentes:
    n_inc = len(df_vic_sel)
    st.markdown(
        "<div style='font-size:0.75rem; font-weight:700; letter-spacing:0.08em;"
        " text-transform:uppercase; color:" + COLOR_TEXT_MUTED + "; margin-bottom:8px;'>"
        + "Incidentes asociados (" + str(n_inc) + ")</div>",
        unsafe_allow_html=True,
    )

    for i, (_, row_inc) in enumerate(df_vic_sel.iterrows(), 1):
        serie_inc = row_inc.get("num_serie", row_inc.get("num_serie_incidente", f"#{i}"))
        fecha_inc = (row_inc["fecha"].strftime("%d/%m/%Y")
                     if "fecha" in row_inc and pd.notna(row_inc.get("fecha"))
                     else "—")
        tipo_inc  = str(row_inc.get("tipo_ataque") or "—")[:60]
        region_inc = str(row_inc.get("region") or "Sin regi\u00f3n")

        with st.expander(
            f"{serie_inc} \u00b7 {fecha_inc} \u00b7 {region_inc} \u00b7 {tipo_inc}",
            expanded=(i == 1),
        ):
            # Descripción
            desc = row_inc.get("descripcion")
            if pd.notna(desc) and str(desc).strip():
                st.markdown(
                    "<div style='font-size:0.83em; color:" + COLOR_TEXT_SECONDARY + ";"
                    " line-height:1.6; white-space:pre-wrap; margin-bottom:12px;'>"
                    + str(desc) + "</div>",
                    unsafe_allow_html=True,
                )

            # Metadatos del incidente
            campos_inc = [
                ("Lugar",           "lugar"),
                ("Provincia",       "provincia"),
                ("Distrito",        "distrito"),
                ("Forma de ataque", "forma_ataque"),
                ("Sub-proceso",     "subproceso_electoral"),
                ("Autor (tipo)",    "autor_tipo"),
                ("Autor (subtipo)", "autor_subtipo"),
                ("Verificaci\u00f3n","estado_verificacion"),
                ("Objetivo pol\u00edtico", "objetivo_politico"),
                ("Forma de ataque (v\u00edctima)", "forma_ataque_victima"),
            ]
            html_inc = "<div class='profile-card' style='margin-bottom:10px;'>"
            for label, key in campos_inc:
                val = row_inc.get(key)
                if pd.notna(val) and str(val).strip() and str(val) not in ("nan", "None"):
                    html_inc += (
                        "<div class='profile-field'>"
                        "<strong>" + label + ":</strong> " + str(val)
                        + "</div>"
                    )
            html_inc += "</div>"
            st.markdown(html_inc, unsafe_allow_html=True)

            # Fuentes
            fuentes = row_inc.get("fuentes_html", "")
            if fuentes and fuentes != "Sin fuentes registradas":
                st.markdown(
                    "<div style='font-size:0.78rem; font-weight:700; letter-spacing:0.06em;"
                    " text-transform:uppercase; color:" + COLOR_TEXT_MUTED + "; margin-bottom:4px;'>"
                    "Fuentes</div>"
                    "<div style='font-size:0.82em; color:" + COLOR_TEXT_SECONDARY + "; line-height:1.7;'>"
                    + fuentes + "</div>",
                    unsafe_allow_html=True,
                )

            # Seguimiento OACNUDH
            seg = row_inc.get("acciones_seguimiento")
            if pd.notna(seg) and str(seg).strip():
                st.markdown(
                    "<div class='nota-info' style='margin-top:8px;'>"
                    "<strong>Seguimiento OACNUDH:</strong> " + str(seg)
                    + "</div>",
                    unsafe_allow_html=True,
                )

# -------------------------------------------------------
# SECTION: Perfil electoral (condicional)
# Solo si la víctima es candidata/o
# -------------------------------------------------------
cargo_postula = row_vic.get("cargo_postula")
es_candidata  = pd.notna(cargo_postula) and str(cargo_postula).strip()

if es_candidata:
    st.markdown(
        "<div style='border-top:2px solid " + COLOR_BORDER + "; margin:24px 0 16px 0;'></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='font-size:0.75rem; font-weight:700; letter-spacing:0.08em;"
        " text-transform:uppercase; color:" + COLOR_ACCENT + "; margin-bottom:8px;'>"
        "Cruce con Monitor Electoral</div>"
        "<div style='font-size:0.82rem; color:" + COLOR_TEXT_SECONDARY + "; margin-bottom:14px;'>"
        "B\u00fasqueda autom\u00e1tica del perfil de candidatura en la base de datos del Monitor Electoral</div>",
        unsafe_allow_html=True,
    )

    nombre_vic   = str(row_vic.get("nombre", ""))
    partido_vic  = str(row_vic.get("org_politica", "") or "")
    resultado_fm = _buscar_candidato(nombre_vic, partido_vic, _df_candidatos)

    confianza    = resultado_fm["confianza"]
    badge_conf   = _badge_confianza(confianza)

    st.markdown(
        "<div style='margin-bottom:12px;'>"
        "Confianza del match: " + badge_conf
        + "</div>",
        unsafe_allow_html=True,
    )

    if resultado_fm["match"] and resultado_fm["candidato"] is not None:
        cand = resultado_fm["candidato"]

        # Detectar columnas de score y riesgo
        col_score  = next((c for c in (cand.index if hasattr(cand, "index") else [])
                           if "score" in str(c).lower()), None)
        col_riesgo = next((c for c in (cand.index if hasattr(cand, "index") else [])
                           if "riesgo" in str(c).lower()), None)

        score_val  = cand[col_score]  if col_score  else None
        riesgo_val = cand[col_riesgo] if col_riesgo else None

        # Badge de riesgo
        if pd.notna(riesgo_val):
            rv = str(riesgo_val).upper()
            riesgo_badge = (
                "<span class='badge badge-alto'>ALTO</span>"  if "ALTO"  in rv else
                "<span class='badge badge-medio'>MEDIO</span>" if "MEDIO" in rv else
                "<span class='badge badge-bajo'>BAJO</span>"
            )
        else:
            riesgo_badge = "<span class='badge badge-none'>Sin dato</span>"

        ce1, ce2, ce3 = st.columns(3)
        with ce1:
            st.markdown(
                "<div style='background:" + COLOR_SURFACE + "; border:1px solid " + COLOR_BORDER + ";"
                " border-radius:6px; padding:14px 16px; text-align:center;'>"
                "<div style='font-size:0.68rem; font-weight:700; letter-spacing:0.08em;"
                " text-transform:uppercase; color:" + COLOR_TEXT_MUTED + "; margin-bottom:4px;'>"
                "Score de riesgo</div>"
                "<div style='font-size:2rem; font-weight:700; color:" + COLOR_RIESGO_ALTO + ";"
                " font-variant-numeric:tabular-nums;'>"
                + (str(int(score_val)) if pd.notna(score_val) else "\u2014")
                + "</div></div>",
                unsafe_allow_html=True,
            )
        with ce2:
            st.markdown(
                "<div style='background:" + COLOR_SURFACE + "; border:1px solid " + COLOR_BORDER + ";"
                " border-radius:6px; padding:14px 16px; text-align:center;'>"
                "<div style='font-size:0.68rem; font-weight:700; letter-spacing:0.08em;"
                " text-transform:uppercase; color:" + COLOR_TEXT_MUTED + "; margin-bottom:6px;'>"
                "Nivel de riesgo</div>"
                + riesgo_badge
                + "</div>",
                unsafe_allow_html=True,
            )
        with ce3:
            col_region = next((c for c in (cand.index if hasattr(cand, "index") else [])
                               if "region" in str(c).lower()), None)
            region_cand = cand[col_region] if col_region else "—"
            st.markdown(
                "<div style='background:" + COLOR_SURFACE + "; border:1px solid " + COLOR_BORDER + ";"
                " border-radius:6px; padding:14px 16px; text-align:center;'>"
                "<div style='font-size:0.68rem; font-weight:700; letter-spacing:0.08em;"
                " text-transform:uppercase; color:" + COLOR_TEXT_MUTED + "; margin-bottom:4px;'>"
                "Regi\u00f3n de candidatura</div>"
                "<div style='font-size:1.1rem; font-weight:700; color:" + COLOR_TEXT_PRIMARY + ";'>"
                + str(region_cand) + "</div></div>",
                unsafe_allow_html=True,
            )

        # Detalle completo del candidato
        with st.expander("Ver ficha completa del Monitor Electoral"):
            campos_cand = [(str(k), cand[k]) for k in cand.index
                           if pd.notna(cand[k]) and str(cand[k]).strip()
                           and str(cand[k]) not in ("nan", "None")]
            html_cand = "<div class='profile-card'>"
            for k, v in campos_cand[:30]:  # máx 30 campos para no saturar
                html_cand += (
                    "<div class='profile-field'>"
                    "<strong>" + str(k).replace("_", " ").title() + ":</strong> "
                    + str(v) + "</div>"
                )
            html_cand += "</div>"
            st.markdown(html_cand, unsafe_allow_html=True)

    else:
        st.markdown(
            "<div class='nota-warning'>"
            "No se encontr\u00f3 un match confiable en la base de datos del Monitor Electoral "
            "para <strong>" + nombre_vic + "</strong> (" + partido_vic + ")."
            " Puede que el nombre no coincida exactamente o que no est\u00e9 registrada/o como candidata/o."
            "</div>",
            unsafe_allow_html=True,
        )

else:
    # No es candidata — nota informativa
    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='nota-info'>"
        "Esta presunta v\u00edctima no postula a ning\u00fan cargo electoral. "
        "El cruce con el Monitor Electoral aplica \u00fanicamente a v\u00edctimas candidatas."
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
