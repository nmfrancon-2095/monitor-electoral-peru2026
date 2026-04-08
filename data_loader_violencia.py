# ============================================================
# data_loader_violencia.py — Monitor Electoral Perú 2026
# Carga de datos de violencia electoral desde ActivityInfo API.
# Join incidentes ↔ víctimas + cruce opcional con candidatos.
#
# Autenticación: API key en secrets.toml → [violencia] activityinfo_api_key
# Endpoints:
#   Incidentes: ch9y74cmlh0lwo31er
#   Víctimas:   cjtck5mlh0lwo41es
# ============================================================

import streamlit as st
import pandas as pd
import requests
import base64
from difflib import SequenceMatcher

# -------------------------------------------------------
# SECTION: Configuración de endpoints
# -------------------------------------------------------
_BASE_URL    = "https://www.activityinfo.org/resources/query/v43/form"
_FORM_INC    = "ch9y74cmlh0lwo31er"
_FORM_VIC    = "cjtck5mlh0lwo41es"

# -------------------------------------------------------
# SECTION: Mapeo de columnas API → nombres internos
# Facilita el mantenimiento si ActivityInfo cambia nombres.
# -------------------------------------------------------
COLS_INC = {
    "_id":                                                  "id",
    "NÚMERO DE SERIE":                                      "num_serie",
    "RESPONSABLE.RESPONSABLE":                              "responsable",
    "FECHA":                                                "fecha",
    "LUGAR DEL HECHO":                                      "lugar",
    "GEO.REGION":                                           "region",
    "GEO.PROVINCIA":                                        "provincia",
    "GEO.DISTRITO":                                         "distrito",
    "UBICACIÓN":                                            "ubicacion",
    "TIPO DE ATAQUE DEL INCIDENTE":                         "tipo_ataque",
    "TIPO DE ATAQUE DEL INCIDENTE: OTRO":                   "tipo_ataque_otro",
    "BREVE DESCRIPCIÓN DE LOS HECHOS":                      "descripcion",
    "FORMA DE ATAQUE":                                      "forma_ataque",
    "PROCESO ELECTORAL AFECTADO.Proceso electoral":         "proceso_electoral",
    "PROCESO ELECTORAL AFECTADO.Sub-proceso electoral":     "subproceso_electoral",
    "PRESUNTO AUTOR/AGRESOR.Tipo de Presunto Autor":        "autor_tipo",
    "PRESUNTO AUTOR/AGRESOR.Sub-tipo del Presunto Autor":   "autor_subtipo",
    "PRESUNTO AUTOR/AGRESOR: OTRO":                         "autor_otro",
    "NÚMERO DE PRESUNTO/S AGRESOR/ES":                      "num_agresores",
    "NÚMERO DE PRESUNTO/S AGRESOR/ES: COLECTIVO":           "num_agresores_colectivo",
    "ESTADO DE VERIFICACIÓN":                               "estado_verificacion",
    "FUENTE DIRECTA":                                       "fuente_directa",
    "FUENTES INDIRECTAS (ENLACE) #1":                       "fuente_indirecta_1",
    "FUENTES INDIRECTAS (ENLACE) #2":                       "fuente_indirecta_2",
    "ACCIONES DE SEGUIMIENTO OACNUDH":                      "acciones_seguimiento",
}

COLS_VIC = {
    "_id":                                                              "id_victima",
    "Parent":                                                           "id_incidente",
    "Parent.NÚMERO DE SERIE":                                           "num_serie_incidente",
    "NÚMERO DE SERIE DEL NIVEL DE LA VÍCTIMA":                         "num_serie_victima",
    "TIPO DE VICTIMA":                                                  "tipo_victima",
    "REPORTE DE VÍCTIMA EN LA BASE DE DATOS DE HRD":                   "en_hrd",
    "NOMBRE DE LA VÍCTIMA: NUEVA.NOMBRE DE LA VÍCTIMA":                "nombre_nuevo",
    "NOMBRE DE LA VÍCTIMA: PREVIAMENTE REPORTADA EN HRD.NOMBRE DE LA VÍCTIMA": "nombre_hrd",
    "PERFIL DE LA VÍCTIMA":                                             "perfil",
    "CARGO AL QUE POSTULA":                                             "cargo_postula",
    "AFILIACIÓN POLÍTICA DE LA VÍCTIMA":                               "afiliacion_politica",
    "PARTIDO POLÍTICO.Partidos políticos":                              "partido",
    "MOVIMIENTO REGIONAL.Movimientos regionales":                      "movimiento",
    "FACTOR DIFERENCIAL DE LA VICTIMA":                                "factor_diferencial",
    "ACTIVIDAD DE DEFENSA DE DERECHOS HUMANOS / LIDERAZGO":            "actividad_hrd",
    "INSTITUCIÓN DE LA AUTORIDAD/FUNCIONARIO ELECTORAL":               "institucion_electoral",
    "RANGO DE EDAD":                                                    "edad",
    "IDENTIDAD ÉTNICA":                                                 "etnia",
    "IDENTIDAD DE GÉNERO":                                              "genero",
    "ORIENTACIÓN SEXUAL":                                               "orientacion_sexual",
    "¿ES UNA PERSONA TRANSGÉNERO?":                                    "es_trans",
    "NACIONALIDAD":                                                     "nacionalidad",
    "DISCAPACIDAD":                                                     "discapacidad",
    "TIPO DE DISCAPACIDAD":                                             "tipo_discapacidad",
    "TIPO DE VIOLENCIA ESPECÍFICA: GÉNERO":                            "tipo_vbg",
    "ELEMENTOS VINCULADOS A LA VIOLENCIA DE BASADA EN GÉNERO":         "elementos_vbg",
    "FORMA DE ATAQUE":                                                  "forma_ataque_victima",
    "OBJETIVO POLÍTICO APARENTE":                                       "objetivo_politico",
    "INSTANCIA DE DENUNCIA/REPORTE":                                   "instancia_denuncia",
    "INSTANCIA DE DENUNCIA/REPORTE: OTRA":                             "instancia_denuncia_otra",
    "MEDIDAS DE PROTECCIÓN ADOPTADAS":                                 "medidas_proteccion",
    "RESULTADO DEL PROCESO DENUNCIADO/REPORTADO":                      "resultado_denuncia",
    "ACTUALIZACIONES DEL CASO - CRONOLOGÍA":                           "cronologia",
}


# -------------------------------------------------------
# SECTION: Fetch desde la API
# -------------------------------------------------------
def _get_headers() -> dict:
    """Construye el header de autenticación Basic con el API key."""
    try:
        api_key = st.secrets["violencia"]["activityinfo_api_key"]
    except (KeyError, AttributeError):
        st.error(
            "API key de ActivityInfo no configurada. "
            "Agrega `[violencia] activityinfo_api_key` en secrets.toml"
        )
        st.stop()
    token = base64.b64encode(f"token:{api_key}".encode()).decode()
    return {"Authorization": f"Basic {token}", "Accept": "application/json"}


def _fetch_form(form_id: str) -> list[dict]:
    """Fetch de todos los registros de un formulario ActivityInfo."""
    url = f"{_BASE_URL}/{form_id}"
    resp = requests.get(url, headers=_get_headers(), timeout=30)
    resp.raise_for_status()
    data = resp.json()
    # ActivityInfo puede devolver lista directa o envuelto en {"rows": [...]}
    if isinstance(data, list):
        return data
    return data.get("rows", data.get("records", []))


# -------------------------------------------------------
# SECTION: Procesamiento
# -------------------------------------------------------
def _consolidar_nombre(row) -> str:
    """Toma el nombre no-nulo entre nombre_nuevo y nombre_hrd."""
    nuevo = row.get("nombre_nuevo")
    hrd   = row.get("nombre_hrd")
    if pd.notna(nuevo) and str(nuevo).strip():
        return str(nuevo).strip()
    if pd.notna(hrd) and str(hrd).strip():
        return str(hrd).strip()
    return "Presunta víctima"


def _explode_multiselect(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Expande columnas de multiselección separadas por comas.
    Retorna un DataFrame con una fila por valor, útil para conteos.
    """
    s = df[col].dropna().str.split(r",\s*").explode().str.strip()
    return s[s != ""].reset_index(drop=True)


def _fuentes_html(row) -> str:
    """
    Construye HTML legible con las fuentes de un incidente.
    Fuente directa → texto. Fuentes indirectas → links clicables.
    """
    partes = []
    if pd.notna(row.get("fuente_directa")) and str(row["fuente_directa"]).strip():
        partes.append(
            "<span style='font-weight:600;'>Fuente directa:</span> "
            + str(row["fuente_directa"]).strip()
        )
    for i, key in enumerate(["fuente_indirecta_1", "fuente_indirecta_2"], 1):
        val = row.get(key)
        if pd.notna(val) and str(val).strip():
            v = str(val).strip()
            if v.startswith("http"):
                partes.append(
                    f"<span style='font-weight:600;'>Fuente indirecta {i}:</span> "
                    f"<a href='{v}' target='_blank' style='color:#2878B5;'>{v[:60]}{'...' if len(v)>60 else ''}</a>"
                )
            else:
                partes.append(
                    f"<span style='font-weight:600;'>Fuente indirecta {i}:</span> {v}"
                )
    return "<br>".join(partes) if partes else "Sin fuentes registradas"


def _badge_verificacion(estado: str) -> str:
    """Devuelve badge HTML según el estado de verificación."""
    if pd.isna(estado) or not str(estado).strip():
        return "<span class='badge badge-none'>Sin dato</span>"
    e = str(estado).lower()
    if "fuente directa" in e and "indirecta" in e:
        return "<span class='badge badge-bajo'>Verificado</span>"
    if "fuente directa" in e:
        return "<span class='badge badge-bajo'>Fuente directa</span>"
    if "indirecta" in e:
        return "<span class='badge badge-medio'>Fuente indirecta</span>"
    if "por verificar" in e:
        return "<span class='badge badge-alto'>Por verificar</span>"
    return "<span class='badge badge-none'>" + str(estado)[:30] + "</span>"


# -------------------------------------------------------
# SECTION: Fuzzy match víctima → candidato
# -------------------------------------------------------
def _similaridad(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _buscar_candidato(nombre_victima: str, partido_victima: str,
                      df_candidatos: pd.DataFrame) -> dict:
    """
    Intenta encontrar al candidato correspondiente a una víctima.
    Retorna dict con: match (bool), confianza, candidato (row o None).
    """
    if df_candidatos is None or df_candidatos.empty:
        return {"match": False, "confianza": "NO ENCONTRADO", "candidato": None}

    # Columnas esperadas en df_candidatos (del maestro electoral)
    col_nombre  = next((c for c in df_candidatos.columns
                        if "nombre" in c.lower() and "candidato" in c.lower()), None)
    col_partido = next((c for c in df_candidatos.columns
                        if "partido" in c.lower() or "organización" in c.lower()), None)

    if col_nombre is None:
        return {"match": False, "confianza": "NO ENCONTRADO", "candidato": None}

    mejor_score = 0.0
    mejor_fila  = None

    for _, row in df_candidatos.iterrows():
        score_nombre = _similaridad(nombre_victima, str(row[col_nombre]))
        score_partido = 0.0
        if col_partido and pd.notna(partido_victima) and str(partido_victima).strip():
            score_partido = _similaridad(str(partido_victima), str(row[col_partido]))
        score_total = score_nombre * 0.75 + score_partido * 0.25
        if score_total > mejor_score:
            mejor_score = score_total
            mejor_fila  = row

    if mejor_score >= 0.90:
        confianza = "EXACTO"
    elif mejor_score >= 0.72:
        confianza = "PROBABLE"
    else:
        confianza = "NO ENCONTRADO"

    return {
        "match":     confianza != "NO ENCONTRADO",
        "confianza": confianza,
        "score":     round(mejor_score, 3),
        "candidato": mejor_fila if confianza != "NO ENCONTRADO" else None,
    }


# -------------------------------------------------------
# SECTION: Funciones principales cacheadas
# TTL 3600 = refresca cada hora. Botón manual disponible en UI.
# -------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def cargar_incidentes() -> pd.DataFrame:
    """Carga y normaliza incidentes desde ActivityInfo."""
    registros = _fetch_form(_FORM_INC)
    df = pd.DataFrame(registros)

    # Renombrar solo las columnas que existan
    rename_map = {k: v for k, v in COLS_INC.items() if k in df.columns}
    df = df.rename(columns=rename_map)

    # Normalizar fecha
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        df["anio_mes"] = df["fecha"].dt.to_period("M").astype(str)
        df["semana"]   = df["fecha"].dt.to_period("W").astype(str)

    # Limpiar strings
    str_cols = ["region", "provincia", "tipo_ataque", "forma_ataque",
                "proceso_electoral", "subproceso_electoral",
                "autor_tipo", "autor_subtipo", "estado_verificacion"]
    for c in str_cols:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
            df[c] = df[c].replace({"nan": None, "None": None, "": None})

    # Badge de verificación como columna HTML
    if "estado_verificacion" in df.columns:
        df["verificacion_badge"] = df["estado_verificacion"].apply(_badge_verificacion)

    # HTML de fuentes
    df["fuentes_html"] = df.apply(_fuentes_html, axis=1)

    return df


@st.cache_data(ttl=3600, show_spinner=False)
def cargar_victimas() -> pd.DataFrame:
    """Carga y normaliza víctimas desde ActivityInfo."""
    registros = _fetch_form(_FORM_VIC)
    df = pd.DataFrame(registros)

    rename_map = {k: v for k, v in COLS_VIC.items() if k in df.columns}
    df = df.rename(columns=rename_map)

    # Consolidar nombre
    df["nombre"] = df.apply(_consolidar_nombre, axis=1)

    # Flag candidata/o (cargo_postula no nulo)
    if "cargo_postula" in df.columns:
        df["es_candidata"] = df["cargo_postula"].notna() & (df["cargo_postula"] != "")

    # Flag VBG (tiene tipo_vbg o elementos_vbg)
    vbg_cols = [c for c in ["tipo_vbg", "elementos_vbg"] if c in df.columns]
    if vbg_cols:
        df["tiene_vbg"] = df[vbg_cols].notna().any(axis=1)
    else:
        df["tiene_vbg"] = False

    # Flag factor diferencial
    if "factor_diferencial" in df.columns:
        df["tiene_factor_diferencial"] = df["factor_diferencial"].notna()

    # Partido consolidado (partido o movimiento)
    partido_col    = "partido"    if "partido"    in df.columns else None
    movimiento_col = "movimiento" if "movimiento" in df.columns else None
    if partido_col and movimiento_col:
        df["org_politica"] = df[partido_col].fillna(df[movimiento_col])
    elif partido_col:
        df["org_politica"] = df[partido_col]
    else:
        df["org_politica"] = None

    return df


@st.cache_data(ttl=3600, show_spinner=False)
def cargar_datos_violencia() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Retorna (df_inc, df_vic, df_joined).
    df_joined = víctimas con columnas de incidente adjuntas (para perfil individual).
    """
    df_inc = cargar_incidentes()
    df_vic = cargar_victimas()

    # Join: víctimas ← incidente padre
    cols_inc_join = ["id", "num_serie", "fecha", "region", "provincia", "distrito",
                     "lugar", "tipo_ataque", "forma_ataque", "descripcion",
                     "autor_tipo", "autor_subtipo", "proceso_electoral",
                     "subproceso_electoral", "estado_verificacion",
                     "verificacion_badge", "fuentes_html", "acciones_seguimiento"]
    cols_inc_join = [c for c in cols_inc_join if c in df_inc.columns]

    df_joined = df_vic.merge(
        df_inc[cols_inc_join].rename(columns={"id": "id_incidente_join"}),
        left_on="id_incidente",
        right_on="id_incidente_join",
        how="left",
    )

    return df_inc, df_vic, df_joined


def limpiar_cache_violencia():
    """Llamar desde botón UI para forzar recarga desde API."""
    cargar_incidentes.clear()
    cargar_victimas.clear()
    cargar_datos_violencia.clear()


# -------------------------------------------------------
# SECTION: KPIs resumen
# -------------------------------------------------------
def kpis_violencia(df_inc: pd.DataFrame, df_vic: pd.DataFrame) -> dict:
    total_inc      = len(df_inc)
    total_vic      = len(df_vic)
    verificados    = df_inc["estado_verificacion"].str.contains(
                         "Fuente Directa", case=False, na=False).sum() \
                     if "estado_verificacion" in df_inc.columns else 0
    candidatas     = df_vic["es_candidata"].sum() if "es_candidata" in df_vic.columns else 0
    con_vbg        = df_vic["tiene_vbg"].sum() if "tiene_vbg" in df_vic.columns else 0
    con_seguimiento = df_inc["acciones_seguimiento"].notna().sum() \
                      if "acciones_seguimiento" in df_inc.columns else 0

    return {
        "total_incidentes":     int(total_inc),
        "total_victimas":       int(total_vic),
        "verificados":          int(verificados),
        "candidatas_victimas":  int(candidatas),
        "con_vbg":              int(con_vbg),
        "con_seguimiento":      int(con_seguimiento),
        "pct_verificados":      round(verificados / total_inc * 100, 1) if total_inc else 0,
        "pct_vbg":              round(con_vbg / total_vic * 100, 1) if total_vic else 0,
    }
