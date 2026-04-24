# ============================================================
# data_loader.py — Monitor Electoral Perú 2026
# Carga y transforma los datos del Excel maestro.
# Todas las transformaciones de datos van aquí.
# Los módulos de páginas solo importan funciones de este archivo.
# ============================================================

import pandas as pd
import streamlit as st
from config import (
    DATA_FILE, LEYES_COLS,
    SCORE_ALTO_MIN, SCORE_MEDIO_MIN,
    LABEL_RIESGO, REGIONES_PRIORITARIAS
)


# --- Utilidades de normalización ---

def normalizar_dni(serie: pd.Series) -> pd.Series:
    """
    Normaliza DNIs: convierte a string, rellena con ceros hasta 8 dígitos.
    Crítico para hacer joins correctos entre hojas.
    Ejemplo: 1234567 → '01234567'
    """
    return serie.astype(str).str.strip().str.zfill(8)


def nivel_riesgo(score: float) -> str:
    """
    Convierte un score numérico en etiqueta de riesgo.
    Umbrales definidos en config.py.
    """
    if pd.isna(score):
        return "none"
    if score >= SCORE_ALTO_MIN:
        return "alto"
    if score >= SCORE_MEDIO_MIN:
        return "medio"
    return "bajo"


def etiqueta_riesgo(score: float) -> str:
    """Devuelve la etiqueta con emoji para mostrar en UI."""
    return LABEL_RIESGO[nivel_riesgo(score)]


# --- Funciones de carga (con caché de Streamlit) ---
# @st.cache_data significa: "la primera vez carga el archivo;
# las siguientes veces devuelve el resultado guardado en memoria".
# Esto hace la app mucho más rápida al navegar entre páginas.

@st.cache_data
def cargar_candidatos() -> pd.DataFrame:
    """
    Carga la hoja 01_CANDIDATOS.
    Columnas clave: dni, nombre_completo, partido, tipo_eleccion,
                    cargo, posicion, region, estado_jne, guid_foto
    """
    df = pd.read_excel(DATA_FILE, sheet_name="01_CANDIDATOS", dtype={"dni": str})
    df["dni"] = normalizar_dni(df["dni"])
    df["region"] = df["region"].str.strip().str.title()
    df["partido"] = df["partido"].str.strip()
    df["es_region_prioritaria"] = df["region"].isin(
        [r.title() for r in REGIONES_PRIORITARIAS]
    )
    return df


@st.cache_data
def cargar_congresistas() -> pd.DataFrame:
    """
    Carga la hoja 02_CONGRESISTAS.
    Columnas clave: dni, nombre_completo, grupo_parlamentario,
                    partido, cargo, tipo_eleccion, region
    """
    df = pd.read_excel(DATA_FILE, sheet_name="02_CONGRESISTAS", dtype={"dni": str})
    df["dni"] = normalizar_dni(df["dni"])
    df["grupo_parlamentario"] = df["grupo_parlamentario"].str.strip()
    df["partido"] = df["partido"].str.strip()
    return df


@st.cache_data
def cargar_votaciones() -> pd.DataFrame:
    """
    Carga la hoja 03_VOTACIONES (congresistas que también postulan).
    Incluye scores y votos por ley.
    Agrega columna 'nivel_riesgo' basada en score_total.
    """
    df = pd.read_excel(DATA_FILE, sheet_name="03_VOTACIONES", dtype={"dni": str})
    df["dni"] = normalizar_dni(df["dni"])

    # Calcular nivel de riesgo a partir del score total
    df["nivel_riesgo"] = df["score_total"].apply(nivel_riesgo)
    df["etiqueta_riesgo"] = df["score_total"].apply(etiqueta_riesgo)

    # Normalizar valores de voto (por si hay espacios extra)
    for col in LEYES_COLS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()
            df[col] = df[col].replace("NAN", "SIN DATO")

    return df


@st.cache_data
def cargar_reinfo() -> pd.DataFrame:
    """
    Carga la hoja 04_REINFO.
    Columnas clave: dni, nombre_completo, partido, cargo,
                    n_derechos_mineros, dptos_mineros, tipo_match
    """
    df = pd.read_excel(DATA_FILE, sheet_name="04_REINFO", dtype={"dni": str})
    df["dni"] = normalizar_dni(df["dni"])
    return df


@st.cache_data
def cargar_leyes() -> pd.DataFrame:
    """
    Carga la hoja 05_LEYES (catálogo de las 16 leyes analizadas).
    Columnas: clave, etiqueta, bloque, fecha, tipo_votacion, notas
    """
    df = pd.read_excel(DATA_FILE, sheet_name="05_LEYES")
    return df

@st.cache_data
def cargar_segunda_vuelta() -> pd.DataFrame:
    """
    Carga la hoja 06_SEGUNDA_VUELTA del Excel maestro.
    Análisis comparativo Capa 2: Fujimori vs. Sánchez Palomino.

    Columnas esperadas:
        tema_num, tema_label, subtema,
        analisis_fujimori, analisis_sanchez,
        nivel_fujimori, nivel_sanchez

    Normaliza niveles a mayúsculas para coincidir con
    COLOR_ABORDAJE / LABEL_ABORDAJE de config.py.
    Hace forward-fill de tema_num y tema_label (pueden estar
    solo en la primera fila de cada bloque en el Excel).
    """
    df = pd.read_excel(DATA_FILE, sheet_name="06_SEGUNDA_VUELTA")

    # Normalizar nombres de columnas
    df.columns = df.columns.str.strip().str.lower()

    # Eliminar filas completamente vacías
    df = df.dropna(how="all").reset_index(drop=True)

    # Normalizar niveles a mayúsculas
    for col in ["nivel_fujimori", "nivel_sanchez"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.upper()
                .replace("NAN", "AUSENTE")
            )

    # tema_num como string para filtros
    if "tema_num" in df.columns:
        df["tema_num"] = df["tema_num"].astype(str).str.strip()

    # Forward-fill: tema_num y tema_label solo en primera fila del bloque
    for col in ["tema_num", "tema_label"]:
        if col in df.columns:
            df[col] = df[col].replace("NAN", pd.NA).ffill()

    return df

# --- Función de datos combinados ---

@st.cache_data
def cargar_todo() -> dict:
    """
    Carga las 5 hojas y devuelve un diccionario.
    Uso: datos = cargar_todo(); df_cands = datos['candidatos']
    Útil en páginas que necesitan cruzar varias fuentes.
    """
    return {
        "candidatos":   cargar_candidatos(),
        "congresistas": cargar_congresistas(),
        "votaciones":   cargar_votaciones(),
        "reinfo":       cargar_reinfo(),
        "leyes":        cargar_leyes(),
        "segunda_vuelta": cargar_segunda_vuelta(),
    }


# --- Funciones de análisis / resumen ---

@st.cache_data
def resumen_kpis() -> dict:
    """
    Calcula los KPIs principales para la página Overview.
    Devuelve un diccionario con valores listos para st.metric().
    """
    cands  = cargar_candidatos()
    votos  = cargar_votaciones()
    reinfo = cargar_reinfo()

    total_cands      = len(cands)
    total_congs_post = len(votos)
    total_reinfo     = len(reinfo)

    riesgo_alto  = (votos["nivel_riesgo"] == "alto").sum()
    riesgo_medio = (votos["nivel_riesgo"] == "medio").sum()
    riesgo_bajo  = (votos["nivel_riesgo"] == "bajo").sum()

    cands_prioritarias = cands[cands["es_region_prioritaria"]].shape[0]

    return {
        "total_candidatos":       total_cands,
        "congresistas_postulando": total_congs_post,
        "con_reinfo":             total_reinfo,
        "riesgo_alto":            int(riesgo_alto),
        "riesgo_medio":           int(riesgo_medio),
        "riesgo_bajo":            int(riesgo_bajo),
        "cands_regiones_prio":    int(cands_prioritarias),
    }


@st.cache_data
def candidatos_con_flags() -> pd.DataFrame:
    """
    Cruza candidatos con votaciones y REINFO.
    Devuelve un DataFrame enriquecido con:
      - score_total, nivel_riesgo, etiqueta_riesgo
      - tiene_reinfo
      - es_congresista
    Usado en la tabla principal de Candidatos.
    """
    cands  = cargar_candidatos()
    votos  = cargar_votaciones()
    reinfo = cargar_reinfo()

    # Merge con votaciones (congresistas que postulan)
    df = cands.merge(
        votos[["dni", "score_total", "nivel_riesgo", "etiqueta_riesgo",
               "es_congresista", "tiene_reinfo", "grupo_parl"]],
        on="dni",
        how="left"
    )

    # Merge con REINFO (puede haber candidatos en REINFO que no están en votaciones)
    dni_reinfo = set(reinfo["dni"].unique())
    df["tiene_reinfo"] = df["dni"].isin(dni_reinfo)
    df["tiene_reinfo"] = df["tiene_reinfo"].fillna(False)

    # Para candidatos sin score (no son congresistas), nivel = 'none'
    df["nivel_riesgo"] = df["nivel_riesgo"].fillna("none")
    df["etiqueta_riesgo"] = df["etiqueta_riesgo"].fillna(LABEL_RIESGO["none"])
    df["es_congresista"] = df["es_congresista"].fillna("NO")

    return df


# ============================================================
# BLOQUE ONPE — Resultados electorales 2026
# Fuente: data/onpe_resultados_latest.xlsx
# Generado por onpe_extractor_v14.py --candidatos
# ============================================================

from config import ONPE_DATA_FILE, ONPE_CODIGOS_ESPECIALES

ONPE_FILE = ONPE_DATA_FILE


def _onpe_sin_especiales(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra filas de votos blancos (80), nulos (81) e impugnados (82)."""
    if "codigoAgrupacionPolitica" in df.columns:
        return df[~df["codigoAgrupacionPolitica"].isin(ONPE_CODIGOS_ESPECIALES)].copy()
    return df.copy()


@st.cache_data
def cargar_onpe_meta() -> dict:
    """
    Lee la hoja METADATA del Excel ONPE.
    Devuelve un dict con los KPIs de escrutinio por tipo de elección.
    """
    df = pd.read_excel(ONPE_FILE, sheet_name="METADATA")
    meta = {}
    current_key = None
    for _, row in df.iterrows():
        campo = str(row.get("campo", "") or "").strip()
        valor = row.get("valor", "")
        if campo.startswith("▸"):
            current_key = campo.replace("▸", "").strip()
            meta[current_key] = {}
        elif current_key and campo.startswith("  "):
            campo_clean = campo.strip()
            meta[current_key][campo_clean] = valor
    return meta


@st.cache_data
def cargar_presidenciales() -> pd.DataFrame:
    """
    Hoja 01_PRESIDENCIALES — resultados presidenciales nacionales por candidato.
    Columnas clave: nombreCandidato, nombreAgrupacionPolitica,
                    totalVotosValidos, porcentajeVotosValidos, porcentajeVotosEmitidos
    """
    df = pd.read_excel(ONPE_FILE, sheet_name="01_PRESIDENCIALES")
    df = _onpe_sin_especiales(df)
    df["dniCandidato"] = df["dniCandidato"].astype(str).str.split(".").str[0].str.zfill(8)
    df = df.sort_values("totalVotosValidos", ascending=False).reset_index(drop=True)
    df["ranking"] = df.index + 1
    return df


@st.cache_data
def cargar_pres_departamento() -> pd.DataFrame:
    """
    Hoja 02_PRES_DEPARTAMENTO — resultados presidenciales por departamento.
    Columnas clave: departamento, nombreCandidato, nombreAgrupacionPolitica,
                    totalVotosValidos, porcentajeVotosValidos
    """
    df = pd.read_excel(ONPE_FILE, sheet_name="02_PRES_DEPARTAMENTO")
    df = _onpe_sin_especiales(df)
    df["dniCandidato"] = df["dniCandidato"].astype(str).str.split(".").str[0].str.zfill(8)
    return df


@st.cache_data
def cargar_senado_nacional_partidos() -> pd.DataFrame:
    """
    Hoja 03_SENADO_NACIONAL — votos por partido en senado nacional.
    Columnas clave: nombreAgrupacionPolitica, totalVotosValidos,
                    porcentajeVotosValidos, totalCandidatos
    """
    df = pd.read_excel(ONPE_FILE, sheet_name="03_SENADO_NACIONAL")
    df = _onpe_sin_especiales(df)
    df = df.sort_values("totalVotosValidos", ascending=False).reset_index(drop=True)
    return df


@st.cache_data
def cargar_senado_regional_partidos() -> pd.DataFrame:
    """
    Hoja 04_SENADO_REGIONAL — votos por partido por distrito electoral.
    Columnas clave: distrito_electoral, nombreAgrupacionPolitica,
                    totalVotosValidos, porcentajeVotosValidos
    """
    df = pd.read_excel(ONPE_FILE, sheet_name="04_SENADO_REGIONAL")
    df = _onpe_sin_especiales(df)
    return df


@st.cache_data
def cargar_diputados_partidos() -> pd.DataFrame:
    """
    Hoja 05_DIPUTADOS — votos por partido por circunscripción.
    Columnas clave: circunscripcion, nombreAgrupacionPolitica,
                    totalVotosValidos, porcentajeVotosValidos
    """
    df = pd.read_excel(ONPE_FILE, sheet_name="05_DIPUTADOS")
    df = _onpe_sin_especiales(df)
    return df


@st.cache_data
def cargar_parlamento_partidos() -> pd.DataFrame:
    """
    Hoja 06_PARLAMENTO_ANDINO — votos por partido.
    """
    df = pd.read_excel(ONPE_FILE, sheet_name="06_PARLAMENTO_ANDINO")
    df = _onpe_sin_especiales(df)
    df = df.sort_values("totalVotosValidos", ascending=False).reset_index(drop=True)
    return df


# Tablas de escaños JNE — Resolución 0053-2025-JNE
_ESCANOS_DIPUTADOS = {
    "AMAZONAS":2,"ÁNCASH":5,"ANCASH":5,"APURÍMAC":2,"APURIMAC":2,
    "AREQUIPA":6,"AYACUCHO":3,"CAJAMARCA":6,"CALLAO":4,"CUSCO":5,
    "HUANCAVELICA":2,"HUÁNUCO":3,"HUANUCO":3,"ICA":4,"JUNÍN":5,"JUNIN":5,
    "LA LIBERTAD":7,"LAMBAYEQUE":5,"LIMA METROPOLITANA":32,"LIMA PROVINCIAS":4,
    "LORETO":4,"MADRE DE DIOS":2,"MOQUEGUA":2,"PASCO":2,"PIURA":7,"PUNO":5,
    "SAN MARTÍN":4,"SAN MARTIN":4,"TACNA":2,"TUMBES":2,"UCAYALI":3,
    "PERUANOS RESIDENTES EN EL EXTRANJERO":2,
}
_ESCANOS_SENADO_REG = {
    "AMAZONAS":1,"ÁNCASH":1,"ANCASH":1,"APURÍMAC":1,"APURIMAC":1,
    "AREQUIPA":1,"AYACUCHO":1,"CAJAMARCA":1,"CALLAO":1,"CUSCO":1,
    "HUANCAVELICA":1,"HUÁNUCO":1,"HUANUCO":1,"ICA":1,"JUNÍN":1,"JUNIN":1,
    "LA LIBERTAD":1,"LAMBAYEQUE":1,"LIMA METROPOLITANA":4,"LIMA PROVINCIAS":1,
    "LORETO":1,"MADRE DE DIOS":1,"MOQUEGUA":1,"PASCO":1,"PIURA":1,"PUNO":1,
    "SAN MARTÍN":1,"SAN MARTIN":1,"TACNA":1,"TUMBES":1,"UCAYALI":1,
    "PERUANOS RESIDENTES EN EL EXTRANJERO":1,
}
_UMBRAL_VOTOS_PCT  = 5.0
_UMBRAL_ESC_SEN    = 3
_UMBRAL_ESC_DIP    = 7
_ESPECIALES        = {80, 81, 82}


def _dhondt_puro(votos: dict, n_escanos: int, elegibles: set = None) -> dict:
    """D'Hondt sin umbral propio. elegibles filtra quién participa."""
    participantes = {p: v for p, v in votos.items()
                     if v > 0 and (elegibles is None or p in elegibles)}
    if not participantes or n_escanos <= 0:
        return {p: 0 for p in votos}
    cocientes = [(v / d, p) for p, v in participantes.items()
                 for d in range(1, n_escanos + 1)]
    cocientes.sort(reverse=True)
    asignados = {}
    for _, p in cocientes[:n_escanos]:
        asignados[p] = asignados.get(p, 0) + 1
    return {p: asignados.get(p, 0) for p in votos}


def _lookup_esc(circ: str, mapa: dict) -> int:
    import unicodedata
    def _strip(s):
        return "".join(c for c in unicodedata.normalize("NFD", s.upper().strip())
                       if unicodedata.category(c) != "Mn")
    n = mapa.get(circ.strip().upper())
    if n is None:
        plain = _strip(circ)
        n = next((v for k, v in mapa.items() if _strip(k) == plain), 1)
    return n


@st.cache_data
def cargar_umbral_escanos() -> pd.DataFrame:
    """
    Recalcula D'Hondt con la doble valla JNE (Acuerdo 12/03/2026) directamente
    desde las hojas de partidos del Excel ONPE.

    Doble condición concurrente:
      SENADO:    ≥ 5% votos (SN+SR combinados) Y ≥ 3 senadores
      DIPUTADOS: ≥ 5% votos nacionales           Y ≥ 7 diputados

    Siempre recalcula desde cero — no depende de la hoja 11_UMBRAL_ESCANOS
    del Excel, que puede venir de una versión anterior del extractor.
    """
    # Cargar hojas de partidos (ya limpias de especiales por _onpe_sin_especiales)
    df_sn  = cargar_senado_nacional_partidos()
    df_sr  = cargar_senado_regional_partidos()
    df_dip = cargar_diputados_partidos()
    df_pa  = cargar_parlamento_partidos()

    # ── Votos nacionales combinados para la valla ─────────────────────────────
    # Senado: SN + SR
    votos_sn  = df_sn.groupby("nombreAgrupacionPolitica")["totalVotosValidos"].sum()
    total_sn  = int(df_sn["votos_validos_total"].iloc[0]) if len(df_sn) else 0

    votos_sr_nac = df_sr.groupby("nombreAgrupacionPolitica")["totalVotosValidos"].sum()
    # total SR = suma de primer registro de cada distrito
    total_sr = int(df_sr.groupby("distrito_electoral")["votos_validos_total"].first().sum())

    votos_sen = votos_sn.add(votos_sr_nac, fill_value=0)
    total_sen = total_sn + total_sr
    umbral_votos_sen = total_sen * _UMBRAL_VOTOS_PCT / 100

    # Diputados
    votos_dip_nac = df_dip.groupby("nombreAgrupacionPolitica")["totalVotosValidos"].sum()
    total_dip = int(df_dip.groupby("circunscripcion")["votos_validos_total"].first().sum())
    umbral_votos_dip = total_dip * _UMBRAL_VOTOS_PCT / 100

    # ── Escaños preliminares (sin valla) para verificar requisito mínimo ─────
    # Senado nacional
    esc_sn_pre = _dhondt_puro(votos_sn.to_dict(), 30)
    # Senado regional (suma por circunscripción)
    esc_sr_pre = {}
    for circ, sub in df_sr.groupby("distrito_electoral"):
        n = _lookup_esc(circ, _ESCANOS_SENADO_REG)
        v = sub.groupby("nombreAgrupacionPolitica")["totalVotosValidos"].sum().to_dict()
        for p, e in _dhondt_puro(v, n).items():
            esc_sr_pre[p] = esc_sr_pre.get(p, 0) + e
    esc_sen_pre = {p: esc_sn_pre.get(p, 0) + esc_sr_pre.get(p, 0)
                   for p in set(list(esc_sn_pre) + list(esc_sr_pre))}

    # Diputados (suma por circunscripción)
    esc_dip_pre = {}
    for circ, sub in df_dip.groupby("circunscripcion"):
        n = _lookup_esc(circ, _ESCANOS_DIPUTADOS)
        v = sub.groupby("nombreAgrupacionPolitica")["totalVotosValidos"].sum().to_dict()
        for p, e in _dhondt_puro(v, n).items():
            esc_dip_pre[p] = esc_dip_pre.get(p, 0) + e

    # ── Doble valla ───────────────────────────────────────────────────────────
    elegibles_sen = {
        p for p, v in votos_sen.items()
        if (v / total_sen * 100 >= _UMBRAL_VOTOS_PCT if total_sen else False)
        and esc_sen_pre.get(p, 0) >= _UMBRAL_ESC_SEN
    }
    elegibles_dip = {
        p for p, v in votos_dip_nac.items()
        if (v / total_dip * 100 >= _UMBRAL_VOTOS_PCT if total_dip else False)
        and esc_dip_pre.get(p, 0) >= _UMBRAL_ESC_DIP
    }

    filas = []
    ts = str(df_sn["timestamp_extraccion"].iloc[0]) if "timestamp_extraccion" in df_sn.columns and len(df_sn) else ""

    # ── Senado Nacional ───────────────────────────────────────────────────────
    votos_sn_d = votos_sn.to_dict()
    esc_sn = _dhondt_puro(votos_sn_d, 30, elegibles_sen)
    for p, v in votos_sn_d.items():
        pct = v / total_sen * 100 if total_sen else 0
        filas.append({"camara": "Senado Nacional", "circunscripcion": "NACIONAL",
                      "escanos_circunscripcion": 30, "partido": p, "votos": v,
                      "pct_validos": round(pct, 2),
                      "pasa_umbral": p in elegibles_sen,
                      "escanos": esc_sn.get(p, 0), "timestamp_extraccion": ts})

    # ── Senado Regional ───────────────────────────────────────────────────────
    for circ, sub in df_sr.groupby("distrito_electoral"):
        n = _lookup_esc(circ, _ESCANOS_SENADO_REG)
        v_circ = sub.groupby("nombreAgrupacionPolitica")["totalVotosValidos"].sum().to_dict()
        total_circ = int(sub["votos_validos_total"].iloc[0])
        esc_circ = _dhondt_puro(v_circ, n, elegibles_sen)
        for p, v in v_circ.items():
            filas.append({"camara": "Senado Regional", "circunscripcion": circ,
                          "escanos_circunscripcion": n, "partido": p, "votos": v,
                          "pct_validos": round(v / total_circ * 100 if total_circ else 0, 2),
                          "pasa_umbral": p in elegibles_sen,
                          "escanos": esc_circ.get(p, 0), "timestamp_extraccion": ts})

    # ── Diputados ─────────────────────────────────────────────────────────────
    for circ, sub in df_dip.groupby("circunscripcion"):
        n = _lookup_esc(circ, _ESCANOS_DIPUTADOS)
        v_circ = sub.groupby("nombreAgrupacionPolitica")["totalVotosValidos"].sum().to_dict()
        total_circ = int(sub["votos_validos_total"].iloc[0])
        esc_circ = _dhondt_puro(v_circ, n, elegibles_dip)
        for p, v in v_circ.items():
            filas.append({"camara": "Diputados", "circunscripcion": circ,
                          "escanos_circunscripcion": n, "partido": p, "votos": v,
                          "pct_validos": round(v / total_circ * 100 if total_circ else 0, 2),
                          "pasa_umbral": p in elegibles_dip,
                          "escanos": esc_circ.get(p, 0), "timestamp_extraccion": ts})

    # ── Parlamento Andino ─────────────────────────────────────────────────────
    votos_pa_d = df_pa.groupby("nombreAgrupacionPolitica")["totalVotosValidos"].sum().to_dict()
    total_pa = int(df_pa["votos_validos_total"].iloc[0]) if len(df_pa) else 0
    esc_pa = _dhondt_puro(votos_pa_d, 5)
    for p, v in votos_pa_d.items():
        pct = v / total_pa * 100 if total_pa else 0
        filas.append({"camara": "Parlamento Andino", "circunscripcion": "NACIONAL",
                      "escanos_circunscripcion": 5, "partido": p, "votos": v,
                      "pct_validos": round(pct, 2),
                      "pasa_umbral": pct >= _UMBRAL_VOTOS_PCT,
                      "escanos": esc_pa.get(p, 0), "timestamp_extraccion": ts})

    return pd.DataFrame(filas) if filas else pd.DataFrame()


def _recalcular_electos(df: pd.DataFrame,
                        umbral_df: pd.DataFrame,
                        camara: str,
                        col_circuns: str | None) -> pd.DataFrame:
    """
    Recalcula electo_proyectado para cualquier hoja de candidatos usando
    el resultado de cargar_umbral_escanos() (que aplica la doble valla JNE).

    Lógica:
      1. Merge por (partido, circunscripción) para obtener pasa_umbral y escanos
      2. Ranking por votos dentro de cada (partido, circunscripción)
      3. electo = pasa_umbral AND ranking <= escanos_partido
    """
    sub = umbral_df[umbral_df["camara"] == camara][
        ["partido", "circunscripcion", "pasa_umbral", "escanos"]
    ].copy()

    # Para cámaras nacionales (senado nac, parlamento) usar circunscripcion=NACIONAL
    if col_circuns is None:
        df["_circ_join"] = "NACIONAL"
    else:
        df["_circ_join"] = df[col_circuns].astype(str).str.strip().str.upper()

    sub["_circ_join"] = sub["circunscripcion"].astype(str).str.strip().str.upper()
    sub = sub.rename(columns={"partido": "nombreAgrupacionPolitica",
                               "pasa_umbral": "_pasa",
                               "escanos": "_esc"})

    df = df.drop(columns=["pasa_umbral_partido", "escanos_partido",
                           "electo_proyectado", "ranking_preferencial"],
                 errors="ignore")

    df = df.merge(sub[["nombreAgrupacionPolitica", "_circ_join", "_pasa", "_esc"]],
                  on=["nombreAgrupacionPolitica", "_circ_join"], how="left")

    df["pasa_umbral_partido"] = df["_pasa"].fillna(False).astype(bool)
    df["escanos_partido"]     = df["_esc"].fillna(0).astype(int)
    df = df.drop(columns=["_pasa", "_esc", "_circ_join"])

    # Ranking preferencial dentro de (partido, circunscripción)
    group_cols = ["nombreAgrupacionPolitica"] + ([col_circuns] if col_circuns else [])
    df = df.sort_values(group_cols + ["totalVotosValidos"],
                        ascending=[True] * len(group_cols) + [False])
    df["ranking_preferencial"] = df.groupby(group_cols).cumcount() + 1

    df["electo_proyectado"] = (
        df["pasa_umbral_partido"] &
        (df["ranking_preferencial"] <= df["escanos_partido"])
    )
    return df


@st.cache_data
def cargar_candidatos_senado_nac() -> pd.DataFrame:
    """
    Hoja 07_CAND_SENADO_NAC — candidatos individuales al senado nacional.
    Nota: ONPE solo expone los top-56 más votados (limitación del endpoint).
    electo_proyectado se recalcula desde cargar_umbral_escanos() (doble valla JNE).
    """
    df = pd.read_excel(ONPE_FILE, sheet_name="07_CAND_SENADO_NAC")
    df["dni_candidato"] = df["dniCandidato"].astype(str).str.split(".").str[0].str.zfill(8)
    umbral = cargar_umbral_escanos()
    df = _recalcular_electos(df, umbral, "Senado Nacional", col_circuns=None)
    df = df.sort_values("totalVotosValidos", ascending=False).reset_index(drop=True)
    return df


@st.cache_data
def cargar_candidatos_senado_reg() -> pd.DataFrame:
    """
    Hoja 08_CAND_SENADO_REG — candidatos individuales al senado regional.
    electo_proyectado se recalcula desde cargar_umbral_escanos() (doble valla JNE).
    """
    df = pd.read_excel(ONPE_FILE, sheet_name="08_CAND_SENADO_REG")
    df["dni_candidato"] = df["dniCandidato"].astype(str).str.split(".").str[0].str.zfill(8)
    umbral = cargar_umbral_escanos()
    df = _recalcular_electos(df, umbral, "Senado Regional", col_circuns="distrito_electoral")
    df = df.sort_values(
        ["distrito_electoral", "totalVotosValidos"], ascending=[True, False]
    ).reset_index(drop=True)
    return df


@st.cache_data
def cargar_candidatos_diputados() -> pd.DataFrame:
    """
    Hoja 09_CAND_DIPUTADOS — candidatos individuales a diputados.
    electo_proyectado se recalcula desde cargar_umbral_escanos() (doble valla JNE).
    """
    df = pd.read_excel(ONPE_FILE, sheet_name="09_CAND_DIPUTADOS")
    df["dni_candidato"] = df["dniCandidato"].astype(str).str.split(".").str[0].str.zfill(8)
    umbral = cargar_umbral_escanos()
    df = _recalcular_electos(df, umbral, "Diputados", col_circuns="circunscripcion")
    df = df.sort_values(
        ["circunscripcion", "totalVotosValidos"], ascending=[True, False]
    ).reset_index(drop=True)
    return df


@st.cache_data
def cargar_candidatos_parlamento() -> pd.DataFrame:
    """
    Hoja 10_CAND_PARLAMENTO — candidatos al Parlamento Andino.
    electo_proyectado se recalcula desde cargar_umbral_escanos() (doble valla JNE).
    """
    df = pd.read_excel(ONPE_FILE, sheet_name="10_CAND_PARLAMENTO")
    df["dni_candidato"] = df["dniCandidato"].astype(str).str.split(".").str[0].str.zfill(8)
    umbral = cargar_umbral_escanos()
    df = _recalcular_electos(df, umbral, "Parlamento Andino", col_circuns=None)
    df = df.sort_values("totalVotosValidos", ascending=False).reset_index(drop=True)
    return df


@st.cache_data
def cargar_electos_con_cruces() -> pd.DataFrame:
    """
    Construye tabla de electos proyectados (senado reg + diputados + parlamento)
    cruzada con el maestro: congresistas 2021-26, score de votación y REINFO.
    Usada en la página 12_ELECTOS_ANALISIS.
    """
    # 1. Reunir todos los electos proyectados
    frames = []

    sen_reg = cargar_candidatos_senado_reg()
    sen_reg_electos = sen_reg[sen_reg["electo_proyectado"] == True].copy()
    sen_reg_electos["camara"]         = "Senado Regional"
    sen_reg_electos["circunscripcion"] = sen_reg_electos["distrito_electoral"]
    frames.append(sen_reg_electos)

    dip = cargar_candidatos_diputados()
    dip_electos = dip[dip["electo_proyectado"] == True].copy()
    dip_electos["camara"] = "Diputados"
    frames.append(dip_electos)

    parl = cargar_candidatos_parlamento()
    parl_electos = parl[parl["electo_proyectado"] == True].copy()
    parl_electos["camara"]         = "Parlamento Andino"
    parl_electos["circunscripcion"] = "NACIONAL"
    frames.append(parl_electos)

    # Senado nacional (datos parciales)
    sen_nac = cargar_candidatos_senado_nac()
    sen_nac_electos = sen_nac[sen_nac["electo_proyectado"] == True].copy()
    sen_nac_electos["camara"]         = "Senado Nacional"
    sen_nac_electos["circunscripcion"] = "NACIONAL"
    frames.append(sen_nac_electos)

    cols_comunes = ["dni_candidato", "nombreCandidato", "nombreAgrupacionPolitica",
                    "camara", "circunscripcion", "totalVotosValidos",
                    "ranking_preferencial", "escanos_partido"]
    electos = pd.concat(
        [f[[c for c in cols_comunes if c in f.columns]] for f in frames],
        ignore_index=True
    )

    # 2. Cruce con congresistas 2021-2026
    congs = cargar_congresistas()[["dni", "nombre_completo", "grupo_parlamentario",
                                    "partido"]].copy()
    congs = congs.rename(columns={"nombre_completo": "nombre_congresista_2021",
                                   "grupo_parlamentario": "grupo_parl_2021",
                                   "partido": "partido_2021"})
    electos = electos.merge(congs, left_on="dni_candidato", right_on="dni", how="left")
    electos["era_congresista_2021"] = electos["dni"].notna()
    electos = electos.drop(columns=["dni"], errors="ignore")

    # 3. Cruce con score de votación
    votos = cargar_votaciones()[["dni", "score_total", "nivel_riesgo",
                                   "etiqueta_riesgo"]].copy()
    electos = electos.merge(votos, left_on="dni_candidato", right_on="dni", how="left")
    electos = electos.drop(columns=["dni"], errors="ignore")
    electos["nivel_riesgo"]   = electos["nivel_riesgo"].fillna("none")
    electos["etiqueta_riesgo"] = electos["etiqueta_riesgo"].fillna(LABEL_RIESGO["none"])

    # 4. Cruce con REINFO
    reinfo = cargar_reinfo()
    dni_reinfo = set(reinfo["dni"].unique())
    electos["tiene_reinfo"] = electos["dni_candidato"].isin(dni_reinfo)

    return electos
