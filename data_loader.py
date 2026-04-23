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


@st.cache_data
def cargar_umbral_escanos() -> pd.DataFrame:
    """
    Hoja 11_UMBRAL_ESCANOS — resultado D'Hondt por cámara, circunscripción y partido.
    Columnas clave: camara, circunscripcion, partido, votos,
                    pct_validos, pasa_umbral, escanos, escanos_circunscripcion
    """
    df = pd.read_excel(ONPE_FILE, sheet_name="11_UMBRAL_ESCANOS")
    return df


@st.cache_data
def cargar_candidatos_senado_nac() -> pd.DataFrame:
    """
    Hoja 07_CAND_SENADO_NAC — candidatos individuales al senado nacional.
    Nota: ONPE solo expone los top-56 más votados (limitación del endpoint).
    La columna electo_proyectado se recalcula aquí cruzando con el umbral.
    Columnas clave: nombreCandidato, dniCandidato, nombreAgrupacionPolitica,
                    totalVotosValidos, lista, ranking_preferencial,
                    pasa_umbral_partido, escanos_partido, electo_proyectado
    """
    df = pd.read_excel(ONPE_FILE, sheet_name="07_CAND_SENADO_NAC")
    df["dni_candidato"] = df["dniCandidato"].astype(str).str.split(".").str[0].str.zfill(8)

    # Recalcular pasa_umbral_partido desde hoja 11 (más fiable)
    umbral = cargar_umbral_escanos()
    sen_nac = umbral[
        (umbral["camara"] == "Senado Nacional") &
        (umbral["circunscripcion"] == "NACIONAL")
    ][["partido", "pasa_umbral", "escanos"]].copy()

    df = df.merge(
        sen_nac.rename(columns={"partido": "nombreAgrupacionPolitica",
                                 "pasa_umbral": "pasa_umbral_v2",
                                 "escanos": "escanos_v2"}),
        on="nombreAgrupacionPolitica", how="left"
    )
    df["pasa_umbral_partido"] = df["pasa_umbral_v2"].fillna(False)
    df["escanos_partido"]     = df["escanos_v2"].fillna(0).astype(int)
    df = df.drop(columns=["pasa_umbral_v2", "escanos_v2"])

    # Recalcular ranking y electo dentro de los 56 disponibles
    df = df.sort_values(["nombreAgrupacionPolitica", "totalVotosValidos"],
                        ascending=[True, False])
    df["ranking_preferencial"] = df.groupby("nombreAgrupacionPolitica").cumcount() + 1
    df["electo_proyectado"] = (
        df["pasa_umbral_partido"] &
        (df["ranking_preferencial"] <= df["escanos_partido"])
    )
    df["datos_completos"] = df["ranking_preferencial"] <= df["escanos_partido"]
    df = df.sort_values("totalVotosValidos", ascending=False).reset_index(drop=True)
    return df


@st.cache_data
def cargar_candidatos_senado_reg() -> pd.DataFrame:
    """
    Hoja 08_CAND_SENADO_REG — candidatos individuales al senado regional.
    Columnas clave: distrito_electoral, nombreCandidato, dniCandidato,
                    nombreAgrupacionPolitica, totalVotosValidos,
                    electo_proyectado, ranking_preferencial
    """
    df = pd.read_excel(ONPE_FILE, sheet_name="08_CAND_SENADO_REG")
    df["dni_candidato"] = df["dniCandidato"].astype(str).str.split(".").str[0].str.zfill(8)
    df = df.sort_values(
        ["distrito_electoral", "nombreAgrupacionPolitica", "totalVotosValidos"],
        ascending=[True, True, False]
    ).reset_index(drop=True)
    return df


@st.cache_data
def cargar_candidatos_diputados() -> pd.DataFrame:
    """
    Hoja 09_CAND_DIPUTADOS — candidatos individuales a diputados.
    Columnas clave: circunscripcion, nombreCandidato, dniCandidato,
                    nombreAgrupacionPolitica, totalVotosValidos,
                    electo_proyectado, ranking_preferencial
    """
    df = pd.read_excel(ONPE_FILE, sheet_name="09_CAND_DIPUTADOS")
    df["dni_candidato"] = df["dniCandidato"].astype(str).str.split(".").str[0].str.zfill(8)
    df = df.sort_values(
        ["circunscripcion", "nombreAgrupacionPolitica", "totalVotosValidos"],
        ascending=[True, True, False]
    ).reset_index(drop=True)
    return df


@st.cache_data
def cargar_candidatos_parlamento() -> pd.DataFrame:
    """
    Hoja 10_CAND_PARLAMENTO — candidatos al Parlamento Andino.
    """
    df = pd.read_excel(ONPE_FILE, sheet_name="10_CAND_PARLAMENTO")
    df["dni_candidato"] = df["dniCandidato"].astype(str).str.split(".").str[0].str.zfill(8)
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
