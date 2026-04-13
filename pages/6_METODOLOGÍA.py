# ============================================================
# pages/6_metodologia.py — Monitor Electoral Perú 2026
# Nota metodológica, sistema de scoring, fuentes de datos
# y notas técnicas. Basado en nota_metodologica_electoral_v2.
# ============================================================

import streamlit as st
import pandas as pd
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    APP_TITLE, APP_ICON, APP_CONFIDENTIAL_LABEL, APP_VERSION,
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_BACKGROUND, COLOR_SURFACE,
    COLOR_BORDER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_RIESGO_ALTO, COLOR_RIESGO_MEDIO, COLOR_RIESGO_BAJO,
    COLOR_RIESGO_NONE, COLOR_REINFO,
    SCORE_ALTO_MIN, SCORE_MEDIO_MIN, GLOBAL_CSS
)

# -------------------------------------------------------
# SECTION: Page setup
# -------------------------------------------------------
st.set_page_config(
    page_title="Metodología · " + APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

if not st.session_state.get("autenticado", False):
    st.warning("Debes iniciar sesión primero.")
    st.stop()

# -------------------------------------------------------
# SECTION: Header
# -------------------------------------------------------
st.markdown(
    "<div style='margin-bottom:8px;'>"
    + "<div style='font-size:0.68rem; font-weight:600; letter-spacing:0.08em;"
    + " text-transform:uppercase; color:" + COLOR_TEXT_MUTED + "; margin-bottom:2px;'>"
    + "MONITOR ELECTORAL PERÚ 2026</div>"
    + "<div style='font-size:1.55rem; font-weight:700; color:" + COLOR_TEXT_PRIMARY + "; margin:0;'>"
    + "Nota metodológica</div>"
    + "<div style='font-size:0.82rem; color:" + COLOR_TEXT_SECONDARY + "; margin-top:2px;'>"
    + "Objetivos · Fuentes de datos · Sistema de scoring · Notas técnicas · "
    + APP_VERSION + " · Marzo 2026</div>"
    + "</div>",
    unsafe_allow_html=True,
)

st.markdown(
    "<div style='background:" + COLOR_SURFACE + "; border:1px solid " + COLOR_BORDER + ";"
    + " border-left:4px solid " + COLOR_PRIMARY + "; border-radius:6px;"
    + " padding:12px 20px; margin-bottom:16px; font-size:0.88em; color:" + COLOR_TEXT_SECONDARY + ";'>"
    + "<b>USO INTERNO</b> — Este dashboard es una herramienta de análisis interno "
    + "diseñada para sistematizar y analizar comportamientos congresales y electorales. "
    + "Las hipótesis de riesgo generadas se basan en datos públicos verificables "
    + "y deben interpretarse a la luz de los estándares internacionales de derechos humanos."
    + "</div>",
    unsafe_allow_html=True,
)

st.markdown("---")

# -------------------------------------------------------
# SECTION: Tabs de contenido
# -------------------------------------------------------
tab_obj, tab_fuentes, tab_scoring, tab_leyes_meta, tab_tecnico = st.tabs([
    "🎯 Objetivos",
    "📂 Fuentes de datos",
    "⚖️ Sistema de scoring",
    "📜 Las 19 leyes",
    "🔧 Notas técnicas",
])

# ===================================================
# TAB 1 — OBJETIVOS
# ===================================================
with tab_obj:
    st.markdown(
        "<h3 style='color:" + COLOR_TEXT_PRIMARY + ";margin-bottom:12px;'>"
        + "Objetivos del dashboard</h3>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        El **Monitor Electoral Perú 2026** es una herramienta de análisis interno
        diseñada para sistematizar y analizar diferentes comportamientos congresales
        y electorales que permitan:

        - Identificar indicios de **interferencia del crimen organizado** en el
          proceso electoral peruano de 2026.
        - Analizar las **dinámicas del voto** de congresistas que se están
          presentando a elecciones nacionales.
        - Generar **hipótesis de riesgo** basadas en datos públicos verificables,
          interpretadas a la luz de estándares internacionales de derechos humanos.
        """
    )

    st.markdown(
        "<h4 style='color:" + COLOR_TEXT_PRIMARY + ";margin:20px 0 8px 0;'>"
        + "Preguntas de análisis</h4>",
        unsafe_allow_html=True,
    )

    preguntas = [
        ("🗳️ ¿Quiénes votaron?",
         "¿Qué congresistas votaron a favor de las 19 leyes identificadas como "
         "preocupantes en términos de seguridad, criminalidad y/o derechos humanos? "
         "¿Con qué frecuencia y en qué bloques temáticos?"),
        ("⚡ ¿Quiénes impulsaron las leyes?",
         "¿Qué congresistas presentaron los proyectos de ley que componen estas "
         "normas, y/o tienen conflicto de interés documentado?"),
        ("⛏️ ¿Quiénes están en REINFO?",
         "¿Cuántos candidatos o congresistas tienen registros activos en el REINFO "
         "(minería informal/artesanal) a título personal o por vía familiar/empresarial?"),
        ("📊 ¿Cuál es el perfil de riesgo agregado?",
         "¿Qué score acumulan los candidatos al cruzar las dimensiones anteriores, "
         "y qué nivel de riesgo representa eso?"),
        ("📍 ¿Qué patrones regionales existen?",
         "¿Hay concentración de perfiles de riesgo en determinadas regiones "
         "o grupos políticos?"),
    ]

    for icon_title, desc in preguntas:
        st.markdown(
            f"""
            <div style="
                background:{COLOR_SURFACE};
                border:1px solid {COLOR_BORDER};
                border-radius:6px;
                padding:12px 16px;
                margin-bottom:8px;
            ">
                <div style="font-weight:600; color:{COLOR_TEXT_PRIMARY};
                            margin-bottom:4px;">{icon_title}</div>
                <div style="font-size:0.88em; color:{COLOR_TEXT_SECONDARY};">
                    {desc}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ===================================================
# TAB 2 — FUENTES DE DATOS
# ===================================================
with tab_fuentes:
    st.markdown(
        f"<p style='color:{COLOR_TEXT_SECONDARY}; font-size:0.9em; margin-bottom:16px;'>"
        f"El proyecto integra cinco fuentes de datos. La clave de cruce principal "
        f"entre fuentes es el <b>DNI</b>, normalizado consistentemente a 8 dígitos "
        f"con ceros a la izquierda (<code>zfill(8)</code>).</p>",
        unsafe_allow_html=True,
    )

    fuentes = [
        {
            "titulo": "🏛️ JNE — Registro de Candidatos",
            "color": COLOR_PRIMARY,
            "fuente": "JNE · API votoinformado.jne.gob.pe y portal oficial",
            "contenido": "Candidatos presidenciales, vicepresidenciales y "
                         "congresales por región",
            "variables": "DNI, nombre completo, partido, región, cargo postulado, "
                         "estado de candidatura (inscrito/excluido/pendiente)",
            "nota": "Datos dinámicos durante el proceso electoral; se requiere "
                    "verificación periódica. Hoja 'candidatos' en Excel maestro.",
        },
        {
            "titulo": "⛏️ REINFO — Registro Integral de Formalización Minera",
            "color": COLOR_REINFO,
            "fuente": "Ministerio de Energía y Minas (MINEM) — base pública REINFO",
            "contenido": "Personas naturales y jurídicas con registros de minería "
                         "informal en proceso de formalización",
            "variables": "DNI del titular, nombre, región, estado del registro, "
                         "código de unidad minera",
            "nota": "⚠️ Figurar en REINFO no implica minería ilegal por sí solo. "
                    "La ilegalidad se determina por el estado del registro y el "
                    "contexto (p.ej. operación en zonas prohibidas). "
                    "Todos los matches actuales son MATCH_NOMBRE_verificar y "
                    "requieren verificación manual. Hoja 'reinfo' en Excel maestro.",
        },
        {
            "titulo": "🏛️ Congreso — Registro de Legisladores",
            "color": COLOR_ACCENT,
            "fuente": "Portal oficial del Congreso; web scraping y extracción manual",
            "contenido": "Congresistas en ejercicio 2021-2026 con datos de "
                         "identificación y grupo parlamentario",
            "variables": "DNI, nombre completo, grupo parlamentario, región de "
                         "elección",
            "nota": "Los 130 congresistas del período 2021-2026. Solo 89 postulan "
                    "a algún cargo en 2026. Hoja 'congresistas' en Excel maestro.",
        },
        {
            "titulo": "📜 Registros de Votación Legislativa",
            "color": COLOR_RIESGO_ALTO,
            "fuente": "votaciones.congreso.gob.pe (oficial)",
            "contenido": "Voto nominal de cada congresista en cada una de las "
                         "19 leyes analizadas",
            "variables": "DNI/nombre congresista, ID ley, tipo de voto "
                         "(A favor / En contra / Abstención / Ausente / Licencia), "
                         "fecha, tipo de votación",
            "nota": "Criterio de voto definitivo: insistencia > segunda votación > "
                    "primera votación. 'Exoneración de segunda votación' se trata "
                    "como no sustantiva y se excluye. Hoja 'votaciones' en Excel maestro.",
        },
    ]

    for f in fuentes:
        with st.expander(f["titulo"], expanded=False):
            st.markdown(
                f"""
                <div style="font-size:0.9em; line-height:1.9;">
                    <b style="color:{COLOR_TEXT_PRIMARY};">Fuente:</b>
                    <span style="color:{COLOR_TEXT_SECONDARY};">{f['fuente']}</span><br>
                    <b style="color:{COLOR_TEXT_PRIMARY};">Contenido:</b>
                    <span style="color:{COLOR_TEXT_SECONDARY};">{f['contenido']}</span><br>
                    <b style="color:{COLOR_TEXT_PRIMARY};">Variables clave:</b>
                    <span style="color:{COLOR_TEXT_SECONDARY};">{f['variables']}</span>
                </div>
                <div style="
                    background:{COLOR_BACKGROUND};
                    border-left:3px solid {f['color']};
                    padding:8px 12px;
                    margin-top:10px;
                    font-size:0.85em;
                    color:{COLOR_TEXT_SECONDARY};
                    border-radius:0 4px 4px 0;
                ">
                    📌 {f['nota']}
                </div>
                """,
                unsafe_allow_html=True,
            )


# ===================================================
# TAB 3 — SISTEMA DE SCORING
# ===================================================
with tab_scoring:
    st.markdown(
        f"""
        <p style='color:{COLOR_TEXT_SECONDARY}; font-size:0.9em; margin-bottom:16px;'>
        El sistema de scoring asigna una puntuación numérica a cada congresista
        basada en su comportamiento observable en datos públicos. Actualmente
        solo se aplica a congresistas con historial legislativo en las 19 leyes.
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Tabla de componentes del score
    st.markdown(
        "<h4 style='color:" + COLOR_TEXT_PRIMARY + ";margin-bottom:10px;'>"
        + "4.1 Componentes del score</h4>",
        unsafe_allow_html=True,
    )

    componentes = [
        ("✅ Voto a favor", "Votó SÍ en la votación definitiva de una ley del análisis", "+2 por ley", COLOR_RIESGO_ALTO),
        ("🟡 Abstención / ausencia", "Se abstuvo o estuvo ausente en la votación definitiva", "+1 por ley", COLOR_RIESGO_MEDIO),
        ("❌ Voto en contra", "Votó NO en la votación definitiva", "+0", COLOR_RIESGO_BAJO),
        ("⚡ Autoría de proyecto de ley", "Fue ponente de uno o más proyectos que componen la norma", "+1 adicional por ley", COLOR_RIESGO_ALTO),
        ("🔗 Conflicto de interés documentado", "Vínculo documentado con actores beneficiados por la ley (fuente interna o periodística)", "+1 adicional por ley", "#8E44AD"),
        ("⛏️ Vínculo REINFO directo", "Figura como titular en REINFO a nombre propio", "+3 al score total", COLOR_REINFO),
        ("⛏️ Vínculo REINFO indirecto", "Vínculo familiar o empresarial documentado con titular REINFO", "+1 al score total (requiere verificación manual)", COLOR_REINFO),
    ]

    for comp, criterio, puntos, color in componentes:
        st.markdown(
            f"""
            <div style="
                display:flex;
                align-items:center;
                gap:12px;
                background:{COLOR_SURFACE};
                border:1px solid {COLOR_BORDER};
                border-left:4px solid {color};
                border-radius:6px;
                padding:10px 14px;
                margin-bottom:6px;
            ">
                <div style="flex:2;">
                    <div style="font-weight:600; color:{COLOR_TEXT_PRIMARY};
                                font-size:0.9em;">{comp}</div>
                    <div style="font-size:0.83em; color:{COLOR_TEXT_SECONDARY};
                                margin-top:2px;">{criterio}</div>
                </div>
                <div style="
                    background:{color}20;
                    color:{color};
                    font-weight:700;
                    font-size:1em;
                    padding:6px 14px;
                    border-radius:4px;
                    min-width:120px;
                    text-align:center;
                    white-space:nowrap;
                ">{puntos}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Criterio de votación definitiva
    st.markdown(
        "<h4 style='color:" + COLOR_TEXT_PRIMARY + ";margin:20px 0 10px 0;'>"
        + "4.2 Votación definitiva — criterio de prioridad</h4>",
        unsafe_allow_html=True,
    )

    prioridades = [
        ("1°", "Insistencia", "Voto para promulgar una ley devuelta por el Ejecutivo — máxima prioridad"),
        ("2°", "Segunda votación", "Segunda ronda de votación sobre la misma ley"),
        ("3°", "Primera votación", "Solo si no existe registro de instancias posteriores"),
    ]
    for num, tipo, desc in prioridades:
        st.markdown(
            f"""
            <div style="
                display:flex; align-items:center; gap:12px;
                background:{COLOR_SURFACE}; border:1px solid {COLOR_BORDER};
                border-radius:6px; padding:10px 14px; margin-bottom:6px;
            ">
                <div style="
                    background:{COLOR_PRIMARY}; color:white;
                    font-weight:700; font-size:1em;
                    width:32px; height:32px; border-radius:50%;
                    display:flex; align-items:center; justify-content:center;
                    flex-shrink:0;
                ">{num}</div>
                <div>
                    <div style="font-weight:600; color:{COLOR_TEXT_PRIMARY};
                                font-size:0.9em;">{tipo}</div>
                    <div style="font-size:0.83em; color:{COLOR_TEXT_SECONDARY};">
                        {desc}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div style="
            background:{COLOR_BACKGROUND};
            border:1px dashed {COLOR_BORDER};
            border-radius:6px; padding:10px 14px;
            font-size:0.85em; color:{COLOR_TEXT_SECONDARY};
            margin-top:4px;
        ">
            📌 <b>Exoneración de segunda votación:</b> Cuando el Congreso aprueba
            exonerar una ley de segunda votación, ese trámite no se considera como
            voto sustantivo sobre el fondo de la ley. En esos casos, se usa la
            primera votación como voto definitivo.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Niveles de riesgo
    st.markdown(
        "<h4 style='color:" + COLOR_TEXT_PRIMARY + ";margin:20px 0 10px 0;'>"
        + "4.3 Niveles de riesgo</h4>",
        unsafe_allow_html=True,
    )

    niveles = [
        ("🔴 Alto",       f"≥ {SCORE_ALTO_MIN} puntos",  COLOR_RIESGO_ALTO,
         "Patrón consistente de apoyo legislativo a agendas identificadas + "
         "posibles vínculos REINFO. Requiere análisis de contexto prioritario."),
        ("🟡 Medio",      f"{SCORE_MEDIO_MIN}–{SCORE_ALTO_MIN-1} puntos", COLOR_RIESGO_MEDIO,
         "Apoyo significativo en varios bloques temáticos. "
         "Perfil que merece seguimiento."),
        ("🟢 Bajo",       f"< {SCORE_MEDIO_MIN} puntos", COLOR_RIESGO_BAJO,
         "Apoyo parcial o concentrado en uno o dos bloques, "
         "o sin historial legislativo. Contexto determinante."),
    ]

    for label, rango, color, desc in niveles:
        st.markdown(
            f"""
            <div style="
                display:flex; align-items:center; gap:12px;
                background:{COLOR_SURFACE}; border:1px solid {COLOR_BORDER};
                border-left:4px solid {color}; border-radius:6px;
                padding:12px 16px; margin-bottom:8px;
            ">
                <div style="min-width:80px; text-align:center;">
                    <div style="font-size:1.1em; font-weight:700; color:{color};">
                        {label}</div>
                    <div style="font-size:0.8em; color:{color}; font-weight:600;">
                        {rango}</div>
                </div>
                <div style="font-size:0.88em; color:{COLOR_TEXT_SECONDARY};">
                    {desc}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div style="
            background:{COLOR_BACKGROUND}; border:1px dashed {COLOR_BORDER};
            border-radius:6px; padding:10px 14px;
            font-size:0.85em; color:{COLOR_TEXT_SECONDARY};
        ">
            ⚠️ <b>Nota de calibración:</b> Los umbrales son provisionales y deben
            calibrarse cuando se complete el dataset de votación. La distribución
            real del score determinará si los cortes actuales son apropiados.
            Los umbrales se configuran en <code>config.py</code>:
            <code>SCORE_ALTO_MIN</code> y <code>SCORE_MEDIO_MIN</code>.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ===================================================
# TAB 4 — LAS 16 LEYES (descripción extendida)
# ===================================================
with tab_leyes_meta:
    st.markdown(
        f"""
        <div style="
            background:{COLOR_SURFACE}; border:1px solid {COLOR_BORDER};
            border-left:4px solid {COLOR_PRIMARY}; border-radius:6px;
            padding:12px 16px; margin-bottom:16px; font-size:0.88em;
            color:{COLOR_TEXT_SECONDARY};
        ">
            <b>Criterio de inclusión:</b> Una ley se incluye cuando su contenido
            normativo tiene el efecto objetivo de reducir la capacidad del Estado
            para perseguir actividades ilícitas, debilitar mecanismos de control
            institucional, ampliar zonas de impunidad, beneficiar directamente a
            sectores vinculados a la informalidad y la ilegalidad, debilitar el
            espacio cívico, o ser preocupante en términos de derechos humanos
            relativos a género, acceso a la justicia, migración y seguridad.
        </div>
        """,
        unsafe_allow_html=True,
    )

    leyes_meta = [
        # (número, nombre corto, nombre largo, bloque, efecto, notas)
        ("1", "Ley 31751 — Prescripción penal 1 año", "pro-crimen",
         "Modifica el artículo 84 del Código Penal para establecer que la "
         "suspensión de la prescripción de un delito no puede exceder un año. "
         "Conocida como 'Ley Soto'. Permitió a su impulsor salvarse de un juicio "
         "por estafa; se acogió a ella de inmediato.",
         "PL 03991/2022-CR"),
        ("2", "Ley 32104 — 'Interpretación auténtica'", "pro-crimen",
         "Cuando el Poder Judicial comenzó a inaplicar la Ley 31751 por "
         "inconstitucional, el Parlamento aprobó esta ley como 'interpretación "
         "auténtica', obligando a los jueces a aplicar el límite de un año "
         "a todos los casos.",
         "PL 06589/2023-CR"),
        ("3", "Ley 31880 — Prisión preventiva", "pro-crimen",
         "Modifica límites y condiciones de la prisión preventiva, reduciendo "
         "la capacidad del sistema para asegurar la presencia de imputados "
         "durante investigaciones complejas. Vinculada al DL 1585.",
         "DL 1585"),
        ("4", "Ley 31989 — Elimina incautación de bienes", "pro-crimen",
         "Restringe la posibilidad de incautar bienes de terceros relacionados "
         "con delitos, debilitando la capacidad de recuperación de activos "
         "producto de la corrupción.",
         "—"),
        ("5", "Ley 31990 — Limita colaboración eficaz", "pro-crimen",
         "Introduce restricciones al mecanismo de colaboración eficaz "
         "(testigos protegidos), que ha sido clave en casos de corrupción "
         "de alto perfil en Perú.",
         "Insistencia"),
        ("6", "Ley 32054 — Exonera partidos de fiscalización", "pro-crimen",
         "Reduce los mecanismos de fiscalización del financiamiento de partidos "
         "políticos, debilitando la transparencia electoral.",
         "—"),
        ("7", "Ley 32108 — Redefine organización criminal", "pro-crimen",
         "Modifica la definición de organización criminal en el Código Penal, "
         "elevando el umbral probatorio requerido y dificultando la persecución "
         "de redes criminales complejas.",
         "—"),
        ("8", "Ley 32130 — Investigación preliminar PNP", "pro-crimen",
         "Modifica los plazos y condiciones de la investigación preliminar "
         "policial, con impacto en la capacidad de actuar en casos urgentes.",
         "—"),
        ("9", "Ley 32181 — Elimina detención preliminar", "pro-crimen",
         "Restringe o elimina la figura de detención preliminar para ciertos "
         "supuestos, reduciendo herramientas de los fiscales en etapas "
         "iniciales de investigación.",
         "—"),
        ("10", "Ley 32326 — Restringe extinción de dominio", "pro-crimen",
         "Introduce restricciones al proceso de extinción de dominio, que "
         "permite al Estado recuperar bienes de origen ilícito.",
         "—"),
        ("11", "Ley 31388 — REINFO 3ª ampliación (2021)", "reinfo",
         "Primera ampliación del REINFO analizada. Extiende plazos del registro "
         "de minería informal, manteniendo la cobertura para actividades "
         "que no han completado el proceso de formalización.",
         "Votación final"),
        ("12", "Ley 32213 — REINFO 4ª ampliación (2024)", "reinfo",
         "Segunda ampliación en el período analizado. Prolonga nuevamente los "
         "plazos, generando un patrón de extensiones sucesivas que algunos "
         "analistas vinculan con la perpetuación de la minería informal.",
         "Votación final"),
        ("13", "Ley 32537 — REINFO 5ª ampliación (2025)", "reinfo",
         "Aprobada en Comisión Permanente con voto individual. Quinta extensión "
         "del REINFO. El patrón de ampliaciones sucesivas es uno de los ejes "
         "centrales del análisis de interferencia.",
         "Comisión Permanente · voto parcial"),
        ("14", "Ley 31973 — Ley Forestal", "ambiental",
         "Modifica la Ley Forestal y de Fauna Silvestre, reduciendo protecciones "
         "para bosques y facilitando cambios de uso del suelo. Criticada por "
         "organizaciones ambientales y pueblos indígenas por su impacto en la "
         "Amazonía. Aprobada por insistencia.",
         "Insistencia"),
        ("15", "Ley 32301 — Ley APCI", "espacio-civico",
         "Modifica la Agencia Peruana de Cooperación Internacional (APCI), "
         "incrementando controles sobre organizaciones de la sociedad civil "
         "que reciben financiamiento extranjero. Señalada como restricción al "
         "espacio cívico y a la libertad de asociación.",
         "Comisión Permanente · voto parcial"),
        ("16", "Ley 31988 — Bicameralidad", "bicameralidad",
         "Reforma constitucional que restaura el Senado en el Parlamento peruano. "
         "Se analiza en el contexto del proceso de reforma institucional y los "
         "patrones de voto asociados.",
         "Segunda votación definitiva"),
         ("17", "Ley 32535 — Igualdad de oportunidades", "genero",
         "Ley de Igualdad de Oportunidades entre Mujeres y Hombres. "
         "Establece un marco normativo para garantizar la igualdad en el acceso "
         "a oportunidades económicas, sociales y políticas. Se analiza como "
         "indicador de posicionamiento legislativo frente a la agenda de igualdad formal.",
         "Primera votación"),
         ("18", "Ley 31498 — Materiales educativos", "genero",
         "Ley que regula la calidad de materiales y recursos educativos "
         "con participación de padres de familia en su revisión. "
         "Impulsada por sectores críticos de la educación en igualdad de género, "
         "se analiza como indicador de posición frente a contenidos de igualdad "
         "en el sistema educativo.",
         "Primera votación"),
         ("19", "Ley 32331 — Indemnidad sexual de NNA", "genero",
         "Ley que fortalece la protección de la indemnidad sexual de niños, niñas "
         "y adolescentes. Conocida por incluir disposiciones que restringen el acceso "
         "de personas trans a espacios según su identidad de género. Se analiza "
         "como indicador de posición frente a derechos de grupos en situación "
         "de vulnerabilidad.",
         "Primera votación")
    ]

    COLORES_BLOQUE = {
    "pro-crimen":     "#B83232",
    "reinfo":         "#B85C0A",
    "ambiental":      "#1E8A4A",
    "espacio-civico": "#6B4FA0",
    "bicameralidad":  "#2878B5",
    "genero":         "#C2185B"
    }
    ETIQUETA_BLOQUE = {
        "pro-crimen":     "⚖️ Pro-crimen",
        "reinfo":         "⛏️ REINFO",
        "ambiental":      "🌿 Ambiental",
        "espacio-civico": "🏛️ Espacio cívico",
        "bicameralidad":  "🏛️ Bicameralidad",
        "genero":         "👥 Género"
    }

    bloque_actual = None
    for num, nombre, bloque, efecto, ref in leyes_meta:
        if bloque != bloque_actual:
            color_b = COLORES_BLOQUE.get(bloque, "#999")
            etiq_b  = ETIQUETA_BLOQUE.get(bloque, bloque)
            st.markdown(
                f"""
                <div style="
                    background:{color_b}18;
                    border-bottom:2px solid {color_b};
                    padding:6px 12px; margin:16px 0 6px 0;
                    border-radius:4px 4px 0 0;
                    font-weight:700; font-size:0.88em; color:{color_b};
                    letter-spacing:0.04em; text-transform:uppercase;
                ">{etiq_b}</div>
                """,
                unsafe_allow_html=True,
            )
            bloque_actual = bloque

        color_b = COLORES_BLOQUE.get(bloque, "#999")
        st.markdown(
            f"""
            <div style="
                background:{COLOR_SURFACE};
                border:1px solid {COLOR_BORDER};
                border-left:3px solid {color_b};
                border-radius:0 6px 6px 0;
                padding:10px 14px; margin-bottom:5px;
            ">
                <div style="display:flex; justify-content:space-between;
                            align-items:flex-start; gap:8px;">
                    <div style="font-weight:600; color:{COLOR_TEXT_PRIMARY};
                                font-size:0.9em;">{num}. {nombre}</div>
                    <div style="font-size:0.78em; color:{COLOR_TEXT_SECONDARY};
                                white-space:nowrap; flex-shrink:0;">
                        Ref: {ref}</div>
                </div>
                <div style="font-size:0.84em; color:{COLOR_TEXT_SECONDARY};
                            margin-top:4px; line-height:1.5;">{efecto}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ===================================================
# TAB 5 — NOTAS TÉCNICAS
# ===================================================
with tab_tecnico:
    st.markdown(
        "<h4 style='color:" + COLOR_TEXT_PRIMARY + ";margin-bottom:12px;'>"
        + "Arquitectura y decisiones técnicas</h4>",
        unsafe_allow_html=True,
    )

    notas_tecnicas = [
        ("🔑 Normalización de DNI",
         "Los DNIs se normalizan con zfill(8) en todas las fuentes antes de "
         "hacer cualquier cruce. Un DNI sin cero inicial (ej: 1234567) y "
         "con cero (01234567) son el mismo registro — sin normalización, "
         "los joins fallan silenciosamente.",
         "data_loader.py · función normalizar_dni()"),
        ("📊 Excel maestro",
         "Un solo archivo Excel con 5 hojas: 01_CANDIDATOS, 02_CONGRESISTAS, "
         "03_VOTACIONES, 04_REINFO, 05_LEYES. Es la única fuente de datos "
         "de la aplicación. Para actualizar datos, reemplaza el archivo en "
         "data/ y reinicia la app.",
         "data/maestro_dashboard_electoral_v1.xlsx"),
        ("⚡ Caché de datos",
         "@st.cache_data en todas las funciones de carga. El Excel se lee "
         "una sola vez por sesión de la app. Si actualizas el archivo, "
         "presiona 'C' en el navegador para limpiar caché, o reinicia "
         "el servidor.",
         "data_loader.py · decorador @st.cache_data"),
        ("🎨 Sistema de diseño",
         "Todos los colores, etiquetas y constantes están en config.py. "
         "Para cambiar un color: busca la variable (ej: COLOR_RIESGO_ALTO) "
         "y cambia el valor hex. Afecta a todas las páginas automáticamente.",
         "config.py · sección de colores"),
        ("🔐 Autenticación",
         "Contraseña simple almacenada en .streamlit/secrets.toml (local) "
         "o en App Settings > Secrets (Streamlit Cloud). "
         "El archivo secrets.toml nunca debe subirse a GitHub — "
         "está en .gitignore.",
         "app.py · función check_password()"),
        ("📦 Dependencias",
         "streamlit, pandas, plotly, openpyxl, streamlit-aggrid. "
         "Versiones en requirements.txt. Instalar con: "
         "pip install -r requirements.txt",
         "requirements.txt"),
        ("🗺️ Mapas",
         "El mapa del Overview usa Plotly scatter_mapbox con coordenadas "
         "aproximadas de capitales regionales definidas en el código. "
         "No requiere API key (usa carto-positron, gratuito).",
         "pages/1_overview.py · sección Mapa"),
        ("🌐 Deploy en Streamlit Cloud",
         "1. Sube el repositorio a GitHub (sin secrets.toml ni el Excel). "
         "2. Crea una app en share.streamlit.io apuntando a app.py. "
         "3. En App Settings > Secrets, pega el contenido de secrets.toml. "
         "4. Sube el Excel maestro manualmente o via Git LFS.",
         "share.streamlit.io"),
    ]

    for titulo, descripcion, referencia in notas_tecnicas:
        st.markdown(
            f"""
            <div style="
                background:{COLOR_SURFACE};
                border:1px solid {COLOR_BORDER};
                border-radius:6px; padding:12px 16px; margin-bottom:8px;
            ">
                <div style="font-weight:600; color:{COLOR_TEXT_PRIMARY};
                            font-size:0.9em; margin-bottom:4px;">{titulo}</div>
                <div style="font-size:0.85em; color:{COLOR_TEXT_SECONDARY};
                            line-height:1.5; margin-bottom:6px;">{descripcion}</div>
                <div style="
                    font-size:0.78em; color:{COLOR_ACCENT};
                    font-family:monospace; background:{COLOR_BACKGROUND};
                    padding:2px 8px; border-radius:3px; display:inline-block;
                ">📁 {referencia}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Bloques en desarrollo
    st.markdown(
        "<h4 style='color:" + COLOR_TEXT_PRIMARY + ";margin:20px 0 10px 0;'>"
        + "Bloques de leyes en desarrollo</h4>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div style="
            background:{COLOR_BACKGROUND}; border:1px dashed {COLOR_BORDER};
            border-radius:6px; padding:14px 16px; font-size:0.88em;
            color:{COLOR_TEXT_SECONDARY}; line-height:1.8;
        ">
            Los siguientes bloques están planificados para incorporarse en
            próximas versiones del dashboard:<br><br>
            <b>🕊️ Bloque 7 — Leyes que eliminan rendición de cuentas por
            el conflicto armado interno:</b>
            Normas que favorecen la impunidad por violaciones de derechos humanos
            cometidas durante el conflicto armado interno (1980-2000).
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------------------------------------------
# SECTION: Footer
# -------------------------------------------------------
st.markdown(
    "<div style='margin-top:32px; padding-top:12px; border-top:1px solid " + COLOR_BORDER + ";"
    + " font-size:0.78em; color:" + COLOR_TEXT_SECONDARY + ";"
    + " display:flex; justify-content:space-between;'>"
    + "<span>" + APP_CONFIDENTIAL_LABEL + " · " + APP_VERSION + "</span>"
    + "<span>Fuentes: JNE · REINFO · Congreso del Perú</span>"
    + "</div>",
    unsafe_allow_html=True,
)
