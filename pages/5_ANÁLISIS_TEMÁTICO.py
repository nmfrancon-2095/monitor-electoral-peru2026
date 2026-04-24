# ============================================================
# pages/5_analisis_tematico.py — Monitor Electoral Perú 2026
# Análisis temático de patrones de votación y riesgo.
# PRINCIPIO: visualizaciones de patrones, sin nombres individuales.
# Pensado para pantallazos y presentaciones a audiencias externas.
#
# Tabs:
#   1. Leyes clave — descripción por bloque + link a normativa
#   2. Patrones de votación — gráficos agregados
#   3. Patrones de riesgo — distribución y concentración
#
# NOTA DE ARQUITECTURA: todo el HTML custom se construye por
# concatenación de strings (operador +), NUNCA con f-strings
# multilínea ni comentarios HTML (<!-- -->). Streamlit convierte
# el Markdown antes del HTML y esas construcciones se rompen.
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    APP_TITLE, APP_ICON, APP_CONFIDENTIAL_LABEL,
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_BACKGROUND, COLOR_SURFACE,
    COLOR_BORDER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_RIESGO_ALTO, COLOR_RIESGO_ALTO_BG,
    COLOR_RIESGO_MEDIO, COLOR_RIESGO_MEDIO_BG,
    COLOR_RIESGO_BAJO, COLOR_RIESGO_BAJO_BG,
    COLOR_RIESGO_NONE, COLOR_RIESGO_NONE_BG,
    COLOR_REINFO, COLOR_REINFO_BG,
    LABEL_RIESGO, LEYES_COLS, BLOQUES, COLOR_BLOQUE, GLOBAL_CSS
)
from data_loader import cargar_votaciones, cargar_leyes, cargar_candidatos

# -------------------------------------------------------
# SECTION: Constantes visuales
# -------------------------------------------------------
TRANSPARENT = "rgba(0,0,0,0)"

# Paleta de bloques viene de COLOR_BLOQUE en config.py
COLORES_BLOQUE = COLOR_BLOQUE

DESCRIPCION_BLOQUES = {
    "pro-crimen": (
        "Leyes que debilitan el sistema de justicia penal. "
        "Incluyen modificaciones que reducen plazos de prescripción, "
        "limitan la prisión preventiva, restringen la extinción de dominio, "
        "redefinen el concepto de organización criminal y debilitan "
        "la colaboración eficaz. Consideradas 'pro-crimen' por su efecto "
        "de reducir la capacidad del Estado para investigar y sancionar "
        "la corrupción y el crimen organizado."
    ),
    "reinfo": (
        "Leyes de ampliación del REINFO (Registro Integral de Formalización Minera). "
        "Extienden sucesivamente los plazos del registro informal, permitiendo "
        "que actividades mineras ilegales o en proceso de formalización continúen "
        "operando. Tres ampliaciones aprobadas: 2021, 2024 y 2025."
    ),
    "ambiental": (
        "Ley Forestal (Ley 31973): modifica la Ley Forestal y de Fauna Silvestre "
        "reduciendo protecciones para bosques y facilitando cambios de uso del suelo. "
        "Criticada por organizaciones ambientales y pueblos indígenas por su impacto "
        "en la Amazonía."
    ),
    "espacio-civico": (
        "Ley APCI (Ley 32301): modifica la Agencia Peruana de Cooperación Internacional, "
        "incrementando controles sobre organizaciones de la sociedad civil que reciben "
        "financiamiento extranjero. Señalada como restricción al espacio cívico "
        "y a la libertad de asociación."
    ),
    "bicameralidad": (
        "Ley de Bicameralidad (Ley 31988): reforma constitucional que restaura el "
        "Senado en el Parlamento peruano. Analizamos los patrones de voto "
        "en el contexto del proceso de reforma institucional."
    ),
    "genero": (
        "Leyes relacionadas con igualdad de género y educación."
        "Incluyen la Ley de Igualdad de Oportunidades entre mujeres y hombres (L32535), "
        "la ley que regula los materiales educativos con participación de padres de familia (L31498) "
        "— impulsada por sectores críticos de la educación con enfoque de género — "
        "y la ley de indemnidad sexual de niños, niñas y adolescentes (L32331), "
        "conocida por restringir el acceso de personas trans a espacios según su identidad. "
        "El patrón de votación en este bloque permite identificar posiciones legislativas "
        "frente a agendas de igualdad de género y derechos de grupos en situación de vulnerabilidad."
    )
}

# -------------------------------------------------------
# SECTION: Page setup
# -------------------------------------------------------
st.set_page_config(
    page_title="Análisis temático · " + APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

if not st.session_state.get("autenticado", False):
    st.warning("Debes iniciar sesión primero.")
    st.stop()

# -------------------------------------------------------
# SECTION: Cargar datos
# -------------------------------------------------------
with st.spinner("Cargando datos..."):
    votos    = cargar_votaciones()
    leyes_df = cargar_leyes()
    cands    = cargar_candidatos()

# Precalcular número de votos A FAVOR por congresista
votos["n_afavor"] = sum(
    (votos[col] == "A FAVOR").astype(int)
    for col in LEYES_COLS if col in votos.columns
)

# Normalizar nivel de riesgo
if "nivel_riesgo" not in votos.columns:
    def nivel(s):
        if pd.isna(s): return "none"
        if s >= 20: return "alto"
        if s >= 10: return "medio"
        return "bajo"
    votos["nivel_riesgo"] = votos["score_total"].apply(nivel)

# -------------------------------------------------------
# SECTION: Header — eyebrow + título (patrón sistema)
# -------------------------------------------------------
st.markdown(
    '<div style="margin-bottom:24px;">'
    '<p style="font-size:0.68rem;font-weight:700;letter-spacing:0.12em;'
    'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 4px 0;">'
    'Monitor Electoral Per\u00fa 2026</p>'
    '<h2 style="color:' + COLOR_TEXT_PRIMARY + ';margin:0 0 4px 0;'
    'font-size:1.55rem;font-weight:700;letter-spacing:-0.02em;">'
    'An\u00e1lisis tem\u00e1tico</h2>'
    '<p style="color:' + COLOR_TEXT_SECONDARY + ';font-size:0.85em;margin:0;">'
    'Patrones de votaci\u00f3n y distribuci\u00f3n de riesgo \u00b7 89 congresistas postulantes'
    '</p>'
    '</div>',
    unsafe_allow_html=True,
)

# -------------------------------------------------------
# SECTION: Tres tabs
# -------------------------------------------------------
tab_leyes, tab_patrones, tab_riesgo = st.tabs([
    "Leyes clave",
    "Patrones de votaci\u00f3n",
    "Patrones de riesgo",
])


# ===================================================
# TAB 1 — LEYES CLAVE
# ===================================================
with tab_leyes:
    st.markdown(
        '<p style="color:' + COLOR_TEXT_SECONDARY + ';font-size:0.9em;margin-bottom:16px;">'
        'Las 19 leyes analizadas se agrupan en 6 bloques temáticos. '
        'Cada ley tiene un tipo de votación definitiva que determina si el voto '
        'cuenta para el score. Haz clic en el enlace de cada ley para acceder al texto oficial.</p>',
        unsafe_allow_html=True,
    )

    for bloque, descripcion in DESCRIPCION_BLOQUES.items():
        leyes_bloque = leyes_df[leyes_df["bloque"] == bloque]
        color_b      = COLORES_BLOQUE.get(bloque, "#95A5A6")
        etiqueta_b   = BLOQUES.get(bloque, bloque)
        n_leyes_b    = len(leyes_bloque)

        with st.expander(etiqueta_b + " (" + str(n_leyes_b) + " ley" + ("es" if n_leyes_b != 1 else "") + ")", expanded=(bloque == "pro-crimen")):

            # Descripción del bloque con franja de color
            st.markdown(
                '<div style="border-left:4px solid ' + color_b + ';'
                'padding:8px 16px;margin-bottom:16px;'
                'font-size:0.88em;color:' + COLOR_TEXT_SECONDARY + ';">'
                + descripcion +
                '</div>',
                unsafe_allow_html=True,
            )

            # Construir filas para la tabla — SIN columna Notas
            filas = []
            for _, ley in leyes_bloque.iterrows():
                col_vot   = ley["etiqueta"]
                nombre_ley = col_vot.split(" ", 1)[1] if " " in col_vot else col_vot

                if col_vot in votos.columns:
                    n_afavor_ley  = (votos[col_vot] == "A FAVOR").sum()
                    n_validos_ley = votos[col_vot].isin(
                        ["A FAVOR", "EN CONTRA", "ABSTENCION"]
                    ).sum()
                    pct = round(n_afavor_ley / n_validos_ley * 100, 1) if n_validos_ley > 0 else 0
                else:
                    n_afavor_ley, n_validos_ley, pct = 0, 0, 0

                link_url = str(ley.get("links_leyes", "")) if pd.notna(ley.get("links_leyes")) else ""

                filas.append({
                    "Ley":           nombre_ley,
                    "Fecha":         ley["fecha"],
                    "Tipo vot.":     ley["tipo_votacion"],
                    "A favor":       str(int(n_afavor_ley)) + " / " + str(int(n_validos_ley)),
                    "% A favor":     pct,
                    "_link":         link_url,
                })

            df_bloque = pd.DataFrame(filas)

            # Layout: tabla izquierda, gráfica derecha
            col_tbl, col_bar = st.columns([3, 2])

            with col_tbl:
                # Tabla con botones de enlace — construida en HTML custom
                # para poder incluir los links sin usar columnas no renderizables
                tbl_html = (
                    '<table style="width:100%;border-collapse:collapse;'
                    'font-size:0.83rem;">'
                    '<thead>'
                    '<tr style="border-bottom:2px solid ' + color_b + ';">'
                    '<th style="text-align:left;padding:6px 8px;font-size:0.68rem;'
                    'font-weight:700;letter-spacing:0.08em;text-transform:uppercase;'
                    'color:' + COLOR_TEXT_MUTED + ';">Ley</th>'
                    '<th style="text-align:left;padding:6px 8px;font-size:0.68rem;'
                    'font-weight:700;letter-spacing:0.08em;text-transform:uppercase;'
                    'color:' + COLOR_TEXT_MUTED + ';">Fecha</th>'
                    '<th style="text-align:left;padding:6px 8px;font-size:0.68rem;'
                    'font-weight:700;letter-spacing:0.08em;text-transform:uppercase;'
                    'color:' + COLOR_TEXT_MUTED + ';">Tipo vot.</th>'
                    '<th style="text-align:center;padding:6px 8px;font-size:0.68rem;'
                    'font-weight:700;letter-spacing:0.08em;text-transform:uppercase;'
                    'color:' + COLOR_TEXT_MUTED + ';">A favor</th>'
                    '<th style="text-align:center;padding:6px 8px;font-size:0.68rem;'
                    'font-weight:700;letter-spacing:0.08em;text-transform:uppercase;'
                    'color:' + COLOR_TEXT_MUTED + ';">Enlace</th>'
                    '</tr>'
                    '</thead>'
                    '<tbody>'
                )

                for i, row_l in df_bloque.iterrows():
                    row_bg = COLOR_SURFACE if i % 2 == 0 else "#F8F9FA"
                    link_btn = ""
                    if row_l["_link"]:
                        link_btn = (
                            '<a href="' + row_l["_link"] + '" target="_blank" rel="noopener" '
                            'style="display:inline-block;padding:2px 8px;border-radius:4px;'
                            'border:1px solid ' + COLOR_BORDER + ';'
                            'font-size:0.75rem;font-weight:600;text-decoration:none;'
                            'color:' + COLOR_TEXT_SECONDARY + ';'
                            'background:' + COLOR_SURFACE + ';">Ver ley</a>'
                        )
                    else:
                        link_btn = '<span style="color:' + COLOR_TEXT_MUTED + ';font-size:0.75rem;">—</span>'

                    tbl_html = tbl_html + (
                        '<tr style="background:' + row_bg + ';border-bottom:1px solid ' + COLOR_BORDER + ';">'
                        '<td style="padding:7px 8px;color:' + COLOR_TEXT_PRIMARY + ';font-weight:500;">'
                        + str(row_l["Ley"]) + '</td>'
                        '<td style="padding:7px 8px;color:' + COLOR_TEXT_SECONDARY + ';">'
                        + str(row_l["Fecha"]) + '</td>'
                        '<td style="padding:7px 8px;color:' + COLOR_TEXT_SECONDARY + ';">'
                        + str(row_l["Tipo vot."]) + '</td>'
                        '<td style="padding:7px 8px;text-align:center;'
                        'font-weight:600;color:' + color_b + ';">'
                        + str(row_l["A favor"]) + '</td>'
                        '<td style="padding:7px 8px;text-align:center;">'
                        + link_btn + '</td>'
                        '</tr>'
                    )

                tbl_html = tbl_html + '</tbody></table>'

                # Altura mínima para alinear con la gráfica de al lado
                n_filas_tbl = len(df_bloque)
                altura_wrapper = str(max(200, n_filas_tbl * 48 + 60)) + "px"
                st.markdown(
                    '<div style="min-height:' + altura_wrapper + ';overflow-y:auto;">'
                    + tbl_html +
                    '</div>',
                    unsafe_allow_html=True,
                )

            with col_bar:
                # Gráfica sin fondo blanco, sin gridlines, con etiquetas en barras
                # Filtrar filas con pct == 0 solo si son ley sin datos — mostrar todas
                altura_grafica = max(200, n_filas_tbl * 48 + 40)
                fig_b = px.bar(
                    df_bloque,
                    x="% A favor",
                    y="Ley",
                    orientation="h",
                    color_discrete_sequence=[color_b],
                    range_x=[0, 100],
                    height=altura_grafica,
                    labels={"% A favor": "% congresistas a favor", "Ley": ""},
                    text="% A favor",
                )
                fig_b.update_traces(
                    texttemplate="%{text:.1f}%",
                    textposition="outside",
                    textfont=dict(size=11, color=COLOR_TEXT_PRIMARY),
                    hovertemplate="<b>%{y}</b><br>%{x:.1f}% a favor<extra></extra>",
                )
                fig_b.update_layout(
                    margin=dict(l=0, r=60, t=4, b=4),
                    paper_bgcolor=TRANSPARENT,
                    plot_bgcolor=TRANSPARENT,
                    xaxis=dict(
                        ticksuffix="%",
                        showgrid=False,
                        zeroline=False,
                        showticklabels=False,
                        title=None,
                    ),
                    yaxis=dict(
                        showgrid=False,
                        zeroline=False,
                        tickfont=dict(size=10, color=COLOR_TEXT_SECONDARY),
                    ),
                )
                st.plotly_chart(fig_b, use_container_width=True)


# ===================================================
# TAB 2 — PATRONES DE VOTACIÓN
# ===================================================
with tab_patrones:
    st.markdown(
        '<p style="color:' + COLOR_TEXT_SECONDARY + ';font-size:0.9em;margin-bottom:12px;">'
        'Patrones agregados \u2014 sin nombres individuales. '
        'Usa los filtros para explorar subgrupos.</p>',
        unsafe_allow_html=True,
    )

    # Filtros
    fp1, fp2 = st.columns(2)
    with fp1:
        grupos_opts = ["Todos"] + sorted(votos["grupo_parl"].dropna().unique().tolist())
        grupo_pat   = st.selectbox("Filtrar por grupo parlamentario", grupos_opts, key="gp_pat")
    with fp2:
        bloque_opts = ["Todos los bloques"] + list(BLOQUES.keys())
        bloque_pat  = st.selectbox(
            "Filtrar por bloque tem\u00e1tico",
            bloque_opts,
            format_func=lambda x: BLOQUES.get(x, x),
            key="bloque_pat",
        )

    df_pat = votos.copy()
    if grupo_pat != "Todos":
        df_pat = df_pat[df_pat["grupo_parl"] == grupo_pat]

    # Calcular % A FAVOR por ley
    resultados_pat = []
    for col in LEYES_COLS:
        if col not in df_pat.columns:
            continue
        n_afavor_p  = (df_pat[col] == "A FAVOR").sum()
        n_validos_p = df_pat[col].isin(["A FAVOR", "EN CONTRA", "ABSTENCION"]).sum()
        pct_p       = round(n_afavor_p / n_validos_p * 100, 1) if n_validos_p > 0 else 0

        match_ley  = leyes_df[leyes_df["etiqueta"] == col]
        bloque_ley = match_ley["bloque"].values[0] if len(match_ley) > 0 else "otro"
        nombre_ley = col.split(" ", 1)[1] if " " in col else col

        resultados_pat.append({
            "ley":       nombre_ley,
            "col":       col,
            "bloque":    bloque_ley,
            "pct":       pct_p,
            "n_afavor":  int(n_afavor_p),
            "n_validos": int(n_validos_p),
        })

    df_res = pd.DataFrame(resultados_pat)

    if bloque_pat != "Todos los bloques":
        df_res = df_res[df_res["bloque"] == bloque_pat]

    df_res = df_res.sort_values("pct", ascending=True)

    # Título de sección — patrón eyebrow+título
    st.markdown(
        '<div style="margin:8px 0 10px 0;">'
        '<p style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 2px 0;">'
        'An\u00e1lisis de votaci\u00f3n</p>'
        '<p style="font-size:1.05rem;font-weight:700;color:' + COLOR_TEXT_PRIMARY + ';'
        'margin:0;letter-spacing:-0.01em;">'
        '% de congresistas postulantes que votaron A FAVOR por ley</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    fig_pct = px.bar(
        df_res,
        x="pct", y="ley",
        orientation="h",
        color="bloque",
        color_discrete_map=COLORES_BLOQUE,
        custom_data=["n_afavor", "n_validos", "bloque"],
        labels={"pct": "% a favor", "ley": "", "bloque": "Bloque"},
        range_x=[0, 100],
        height=460,
        text="pct",
    )
    fig_pct.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        textfont=dict(size=10, color=COLOR_TEXT_PRIMARY),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "%{x:.1f}% a favor<br>"
            "%{customdata[0]} de %{customdata[1]} congresistas<br>"
            "Bloque: %{customdata[2]}<extra></extra>"
        ),
    )
    fig_pct.update_layout(
        margin=dict(l=0, r=72, t=4, b=0),
        paper_bgcolor=TRANSPARENT,
        plot_bgcolor=TRANSPARENT,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=None),
        yaxis=dict(
            showgrid=False, zeroline=False,
            tickfont=dict(size=10, color=COLOR_TEXT_SECONDARY),
        ),
        legend=dict(
            orientation="h", y=-0.10,
            xanchor="left", x=0,
            font=dict(size=10),
            bgcolor=TRANSPARENT,
        ),
    )
    st.plotly_chart(fig_pct, use_container_width=True)

    st.markdown("---")

    # Heatmap
    st.markdown(
        '<div style="margin:8px 0 10px 0;">'
        '<p style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 2px 0;">'
        'Vista cruzada</p>'
        '<p style="font-size:1.05rem;font-weight:700;color:' + COLOR_TEXT_PRIMARY + ';'
        'margin:0;letter-spacing:-0.01em;">'
        'Heatmap: % A FAVOR por grupo parlamentario</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.caption("Cada celda = % de congresistas del grupo que votaron A FAVOR de esa ley")

    grupos_unicos   = sorted(votos["grupo_parl"].dropna().unique().tolist())
    leyes_nombres   = [col.split(" ", 1)[1] if " " in col else col for col in LEYES_COLS if col in votos.columns]
    leyes_cols_valid = [col for col in LEYES_COLS if col in votos.columns]

    matrix_data = []
    for grupo in grupos_unicos:
        fila = {"grupo": grupo}
        sub  = votos[votos["grupo_parl"] == grupo]
        for col, nombre in zip(leyes_cols_valid, leyes_nombres):
            n_af  = (sub[col] == "A FAVOR").sum()
            n_val = sub[col].isin(["A FAVOR","EN CONTRA","ABSTENCION"]).sum()
            fila[nombre] = round(n_af / n_val * 100, 0) if n_val > 0 else 0
        matrix_data.append(fila)

    df_matrix = pd.DataFrame(matrix_data).set_index("grupo")

    fig_heat = px.imshow(
        df_matrix,
        color_continuous_scale=[
            [0.0, "#EAF4EC"],
            [0.5, "#FEF9E7"],
            [1.0, "#C0392B"],
        ],
        zmin=0, zmax=100,
        aspect="auto",
        height=420,
        labels=dict(color="% A favor"),
    )
    fig_heat.update_traces(
        hovertemplate="<b>%{y}</b><br>%{x}<br>%{z:.0f}% a favor<extra></extra>"
    )
    fig_heat.update_layout(
        margin=dict(l=0, r=0, t=4, b=0),
        paper_bgcolor=TRANSPARENT,
        xaxis=dict(tickfont=dict(size=9), tickangle=-35),
        yaxis=dict(tickfont=dict(size=10)),
        coloraxis_colorbar=dict(title="% A favor", ticksuffix="%", thickness=12),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("---")

    # Histograma distribución de votos A FAVOR
    st.markdown(
        '<div style="margin:8px 0 10px 0;">'
        '<p style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 2px 0;">'
        'Distribución individual</p>'
        '<p style="font-size:1.05rem;font-weight:700;color:' + COLOR_TEXT_PRIMARY + ';'
        'margin:0;letter-spacing:-0.01em;">'
        'Cuántas leyes votó A FAVOR cada congresista?</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    fig_hist = px.histogram(
        votos,
        x="n_afavor",
        nbins=17,
        color="nivel_riesgo",
        color_discrete_map={
            "alto":  COLOR_RIESGO_ALTO,
            "medio": COLOR_RIESGO_MEDIO,
            "bajo":  COLOR_RIESGO_BAJO,
            "none":  COLOR_RIESGO_NONE,
        },
        labels={
            "n_afavor":    "Número de leyes votadas A FAVOR (de 19)",
            "nivel_riesgo": "Riesgo",
            "count":        "Congresistas",
        },
        barmode="stack",
        height=320,
    )
    fig_hist.update_layout(
        margin=dict(l=0, r=0, t=4, b=0),
        paper_bgcolor=TRANSPARENT,
        plot_bgcolor=TRANSPARENT,
        xaxis=dict(dtick=1, showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        legend=dict(orientation="h", y=-0.2, font=dict(size=11), bgcolor=TRANSPARENT),
        bargap=0.1,
    )
    st.plotly_chart(fig_hist, use_container_width=True)


# ===================================================
# TAB 3 — PATRONES DE RIESGO
# ===================================================
with tab_riesgo:
    st.markdown(
        '<p style="color:' + COLOR_TEXT_SECONDARY + ';font-size:0.9em;margin-bottom:12px;">'
        'Distribución del score de riesgo y concentración por partido, '
        'grupo parlamentario y región.</p>',
        unsafe_allow_html=True,
    )

    # KPIs — usar _kpi_card custom (nunca st.metric())
    def _kpi_card(label, value, sub, bg, border, color):
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

    n_alto_r   = int((votos["nivel_riesgo"] == "alto").sum())
    n_total_r  = len(votos)
    pct_alto_r = round(n_alto_r / n_total_r * 100, 1) if n_total_r else 0
    score_med  = round(votos["score_total"].mean(), 1)
    n_rei_alto = int(votos[(votos.get("tiene_reinfo", pd.Series()) == "SI") &
                            (votos["nivel_riesgo"] == "alto")].shape[0])
    n_autores  = int(votos["bonus_autoria"].gt(0).sum())

    kpi_html = (
        '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px;">'
        + _kpi_card(
            "\U0001f534 Riesgo alto",
            n_alto_r,
            str(pct_alto_r) + "% del total",
            COLOR_RIESGO_ALTO_BG, "#EEC8C8", COLOR_RIESGO_ALTO,
        )
        + _kpi_card(
            "\U0001f4ca Score promedio",
            score_med,
            "89 congresistas postulantes",
            COLOR_SURFACE, COLOR_BORDER, COLOR_TEXT_SECONDARY,
        )
        + _kpi_card(
            "\u26cf\ufe0f REINFO + riesgo alto",
            n_rei_alto,
            "Cruce registro minero y voto",
            COLOR_REINFO_BG, "#E8C8A8", COLOR_REINFO,
        )
        + _kpi_card(
            "\u26a1 Con bonus autor/a",
            n_autores,
            "Autores de al menos 1 ley clave",
            COLOR_RIESGO_MEDIO_BG, "#E8D8B0", COLOR_RIESGO_MEDIO,
        )
        + '</div>'
    )
    st.markdown(kpi_html, unsafe_allow_html=True)

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.markdown(
            '<div style="margin:8px 0 10px 0;">'
            '<p style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 2px 0;">'
            'Por grupo parlamentario</p>'
            '<p style="font-size:1.05rem;font-weight:700;color:' + COLOR_TEXT_PRIMARY + ';'
            'margin:0;letter-spacing:-0.01em;">Score promedio</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        score_grupo = (
            votos.groupby("grupo_parl")["score_total"]
            .agg(["mean","count"])
            .reset_index()
            .rename(columns={"mean":"Score promedio","count":"N"})
            .sort_values("Score promedio", ascending=True)
        )
        score_grupo["Score promedio"] = score_grupo["Score promedio"].round(1)

        fig_grupo = px.bar(
            score_grupo,
            x="Score promedio",
            y="grupo_parl",
            orientation="h",
            color="Score promedio",
            color_continuous_scale=[
                [0.0, COLOR_RIESGO_BAJO],
                [0.4, COLOR_RIESGO_MEDIO],
                [0.7, COLOR_RIESGO_ALTO],
                [1.0, "#7B241C"],
            ],
            custom_data=["N"],
            labels={"grupo_parl": "", "Score promedio": "Score promedio"},
            height=360,
            text="Score promedio",
        )
        fig_grupo.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside",
            textfont=dict(size=10, color=COLOR_TEXT_PRIMARY),
            hovertemplate=(
                "<b>%{y}</b><br>Score promedio: %{x:.1f}"
                "<br>N = %{customdata[0]} congresistas<extra></extra>"
            ),
        )
        fig_grupo.update_layout(
            margin=dict(l=0, r=48, t=4, b=0),
            paper_bgcolor=TRANSPARENT,
            plot_bgcolor=TRANSPARENT,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 34]),
            yaxis=dict(
                showgrid=False, zeroline=False,
                tickfont=dict(size=10, color=COLOR_TEXT_SECONDARY),
            ),
            coloraxis_showscale=False,
        )
        fig_grupo.add_vline(
            x=20, line_dash="dash", line_color=COLOR_RIESGO_ALTO,
            annotation_text="Umbral alto",
            annotation_font_size=9,
            annotation_position="top right",
        )
        st.plotly_chart(fig_grupo, use_container_width=True)

    with col_r2:
        st.markdown(
            '<div style="margin:8px 0 10px 0;">'
            '<p style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 2px 0;">'
            'Distribuci\u00f3n general</p>'
            '<p style="font-size:1.05rem;font-weight:700;color:' + COLOR_TEXT_PRIMARY + ';'
            'margin:0;letter-spacing:-0.01em;">Distribuci\u00f3n del score total</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        fig_violin = go.Figure()
        fig_violin.add_trace(go.Violin(
            y=votos["score_total"],
            box_visible=True,
            meanline_visible=True,
            fillcolor=COLOR_ACCENT,
            opacity=0.7,
            line_color=COLOR_PRIMARY,
            name="Score total",
            hoverinfo="y",
        ))
        fig_violin.update_layout(
            height=360,
            margin=dict(l=0, r=0, t=4, b=0),
            paper_bgcolor=TRANSPARENT,
            plot_bgcolor=TRANSPARENT,
            yaxis=dict(
                title="Score total",
                showgrid=False,
                zeroline=False,
            ),
            showlegend=False,
        )
        fig_violin.add_hline(
            y=20, line_dash="dash", line_color=COLOR_RIESGO_ALTO,
            annotation_text="Umbral alto (20)",
            annotation_font_size=9,
        )
        fig_violin.add_hline(
            y=10, line_dash="dot", line_color=COLOR_RIESGO_MEDIO,
            annotation_text="Umbral medio (10)",
            annotation_font_size=9,
        )
        st.plotly_chart(fig_violin, use_container_width=True)

    st.markdown("---")

    # Candidatos en regiones prioritarias
    st.markdown(
        '<div style="margin:8px 0 10px 0;">'
        '<p style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 2px 0;">'
        'Concentración territorial</p>'
        '<p style="font-size:1.05rem;font-weight:700;color:' + COLOR_TEXT_PRIMARY + ';'
        'margin:0;letter-spacing:-0.01em;">'
        'Candidatos en regiones prioritarias por tipo de elección</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    REGIONES_PRIORITARIAS = ["Ucayali", "Loreto", "Madre De Dios", "Puno"]
    st.caption("Regiones prioritarias: " + ", ".join(REGIONES_PRIORITARIAS))

    cands_prio = cands[cands["region"].str.title().isin(REGIONES_PRIORITARIAS)].copy()
    prio_tipo  = (
        cands_prio.groupby(["region", "tipo_eleccion"])
        .size().reset_index(name="candidatos")
    )

    fig_prio = px.bar(
        prio_tipo,
        x="region", y="candidatos",
        color="tipo_eleccion",
        barmode="stack",
        labels={"region": "Región", "candidatos": "Número de candidatos", "tipo_eleccion": "Tipo de elección"},
        color_discrete_sequence=px.colors.qualitative.Set2,
        height=320,
        text="candidatos",
    )
    fig_prio.update_traces(
        textposition="inside",
        textfont=dict(size=10, color="#FFFFFF"),
    )
    fig_prio.update_layout(
        margin=dict(l=0, r=0, t=4, b=0),
        paper_bgcolor=TRANSPARENT,
        plot_bgcolor=TRANSPARENT,
        xaxis=dict(tickfont=dict(size=11), showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        legend=dict(orientation="h", y=-0.2, font=dict(size=10), bgcolor=TRANSPARENT),
    )
    st.plotly_chart(fig_prio, use_container_width=True)

    st.markdown("---")

    # Tabla resumen descargable
    st.markdown(
        '<div style="margin:8px 0 10px 0;">'
        '<p style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin:0 0 2px 0;">'
        'Datos agregados</p>'
        '<p style="font-size:1.05rem;font-weight:700;color:' + COLOR_TEXT_PRIMARY + ';'
        'margin:0;letter-spacing:-0.01em;">'
        'Resumen por grupo parlamentario</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    resumen_gp = (
        votos.groupby("grupo_parl")
        .agg(
            total=("dni","count"),
            score_promedio=("score_total","mean"),
            score_max=("score_total","max"),
            riesgo_alto=("nivel_riesgo", lambda x: (x=="alto").sum()),
            riesgo_medio=("nivel_riesgo", lambda x: (x=="medio").sum()),
            con_reinfo=("tiene_reinfo", lambda x: (x=="SI").sum()),
            n_afavor_prom=("n_afavor","mean"),
        )
        .reset_index()
        .rename(columns={
            "grupo_parl":    "Grupo parlamentario",
            "total":         "Total",
            "score_promedio":"Score prom.",
            "score_max":     "Score max.",
            "riesgo_alto":   "Riesgo alto",
            "riesgo_medio":  "Riesgo medio",
            "con_reinfo":    "Con REINFO",
            "n_afavor_prom": "Leyes A favor (prom.)",
        })
        .sort_values("Score prom.", ascending=False)
    )
    resumen_gp["Score prom."]           = resumen_gp["Score prom."].round(1)
    resumen_gp["Leyes A favor (prom.)"] = resumen_gp["Leyes A favor (prom.)"].round(1)

    st.dataframe(resumen_gp, hide_index=True, use_container_width=True, height=360)

    col_dl1, col_dl2 = st.columns([3, 1])
    with col_dl2:
        st.download_button(
            "\u2b07\ufe0f Descargar resumen (CSV)",
            data=resumen_gp.to_csv(index=False).encode("utf-8"),
            file_name="resumen_grupos_parlamentarios.csv",
            mime="text/csv",
            use_container_width=True,
        )

# -------------------------------------------------------
# SECTION: Footer — concatenación, sin f-string
# -------------------------------------------------------
st.markdown(
    '<div style="margin-top:32px;padding-top:12px;border-top:1px solid ' + COLOR_BORDER + ';'
    'font-size:0.78em;color:' + COLOR_TEXT_SECONDARY + ';display:flex;justify-content:space-between;">'
    '<span>' + APP_CONFIDENTIAL_LABEL + '</span>'
    '<span>Fuentes: JNE \u00b7 Congreso del Perú \u00b7 REINFO</span>'
    '</div>',
    unsafe_allow_html=True,
)
