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
