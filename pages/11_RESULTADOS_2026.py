# ============================================================
# 11_RESULTADOS_2026.py — Monitor Electoral Perú 2026
# Resultados electorales en tiempo real — Elecciones Generales 12/04/2026
# Fuente: API ONPE via onpe_extractor_v14.py --candidatos
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math
from config import (
    GLOBAL_CSS, COLOR_PRIMARY, COLOR_ACCENT, COLOR_BACKGROUND,
    COLOR_SURFACE, COLOR_SURFACE_ALT, COLOR_BORDER, COLOR_BORDER_STRONG,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_RIESGO_BAJO, COLORES_PARTIDO, SIGLAS_PARTIDO, ONPE_CODIGOS_ESPECIALES,
)
from data_loader import (
    cargar_presidenciales, cargar_pres_departamento,
    cargar_senado_nacional_partidos, cargar_senado_regional_partidos,
    cargar_diputados_partidos, cargar_parlamento_partidos,
    cargar_umbral_escanos,
    cargar_candidatos_senado_nac, cargar_candidatos_senado_reg,
    cargar_candidatos_diputados, cargar_candidatos_parlamento,
    cargar_onpe_meta,
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Auth ──────────────────────────────────────────────────────────────────────
if not st.session_state.get("autenticado", False):
    st.warning("Accede desde la pantalla principal.")
    st.stop()


# ── Helpers ───────────────────────────────────────────────────────────────────

def color_partido(nombre: str) -> str:
    return COLORES_PARTIDO.get(nombre, COLORES_PARTIDO["_DEFAULT"])


def sigla_partido(nombre: str) -> str:
    return SIGLAS_PARTIDO.get(nombre, nombre[:3].upper())


def fmt_votos(n) -> str:
    try:
        return f"{int(n):,}".replace(",", "\u00a0")
    except Exception:
        return str(n)


def fmt_pct(n, decimals=1) -> str:
    try:
        return f"{float(n):.{decimals}f}%"
    except Exception:
        return "—"


def _kpi(label: str, valor: str, sub: str = "") -> str:
    return (
        '<div style="background:' + COLOR_SURFACE + ';border:1px solid ' + COLOR_BORDER + ';'
        'border-radius:8px;padding:16px 20px;">'
        '<div style="font-size:0.62rem;font-weight:700;letter-spacing:0.10em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:4px;">'
        + label +
        '</div>'
        '<div style="font-size:1.45rem;font-weight:700;color:' + COLOR_TEXT_PRIMARY + ';'
        'letter-spacing:-0.02em;font-variant-numeric:tabular-nums;">'
        + valor +
        '</div>'
        + ('<div style="font-size:0.75rem;color:' + COLOR_TEXT_SECONDARY + ';margin-top:2px;">' + sub + '</div>' if sub else '')
        + '</div>'
    )


def barra_escrutinio(pct: float, color: str = None) -> str:
    c = color or COLOR_PRIMARY
    pct_safe = min(100, max(0, float(pct) if pct else 0))
    return (
        '<div class="escrutinio-bar-wrap" style="background:' + COLOR_BORDER + ';">'
        '<div class="escrutinio-bar-fill" style="width:' + str(pct_safe) + '%;background:' + c + ';"></div>'
        '</div>'
    )


def hemiciclo_plotly(
    escanos_dict: dict,
    titulo: str = "",
    total_escanos: int = None,
) -> go.Figure:
    """
    Construye un hemiciclo de escaños estilo parlamento.
    escanos_dict: {nombre_partido: n_escanos}
    """
    # Construir lista ordenada por escaños desc
    items = sorted(
        [(p, e) for p, e in escanos_dict.items() if e > 0],
        key=lambda x: x[1], reverse=True
    )
    if not items:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=220,
            margin=dict(t=10, b=10, l=10, r=10),
        )
        return fig

    total = total_escanos or sum(e for _, e in items)

    # Distribución en filas semicirculares (de dentro hacia afuera)
    dots_x, dots_y, dots_color, dots_text = [], [], [], []

    # Calcular número de filas y distribución radial
    n_filas = max(3, math.ceil(math.sqrt(total / 3)))
    radios = [0.4 + i * (0.55 / (n_filas - 1)) for i in range(n_filas)]
    capacidades = [max(3, round(math.pi * r * 28)) for r in radios]

    # Aplanar lista de partidos en orden
    partido_list = []
    for nombre, n in items:
        partido_list.extend([(nombre, color_partido(nombre))] * n)

    idx = 0
    for fila, (r, cap) in enumerate(zip(radios, capacidades)):
        if idx >= len(partido_list):
            break
        n_en_fila = min(cap, len(partido_list) - idx)
        angulos = [math.pi * (j / (n_en_fila - 1)) for j in range(n_en_fila)] if n_en_fila > 1 else [math.pi / 2]
        for ang in angulos:
            if idx >= len(partido_list):
                break
            nombre, color = partido_list[idx]
            x = r * math.cos(math.pi - ang)
            y = r * math.sin(ang) * 0.85
            dots_x.append(x)
            dots_y.append(y)
            dots_color.append(color)
            dots_text.append(f"<b>{nombre}</b><br>{escanos_dict.get(nombre, 0)} escaños")
            idx += 1

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dots_x, y=dots_y,
        mode="markers",
        marker=dict(
            size=10,
            color=dots_color,
            line=dict(width=0.8, color="rgba(255,255,255,0.6)"),
        ),
        hovertext=dots_text,
        hovertemplate="%{hovertext}<extra></extra>",
        showlegend=False,
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=210,
        margin=dict(t=8, b=4, l=8, r=8),
        xaxis=dict(visible=False, range=[-1.1, 1.1]),
        yaxis=dict(visible=False, range=[-0.12, 1.05]),
        hoverlabel=dict(
            bgcolor=COLOR_SURFACE,
            bordercolor=COLOR_BORDER,
            font=dict(color=COLOR_TEXT_PRIMARY, size=12),
        ),
    )
    return fig


def leyenda_partidos(escanos_dict: dict, max_cols: int = 3) -> str:
    """HTML de leyenda de partidos con escaños."""
    items = sorted(
        [(p, e) for p, e in escanos_dict.items() if e > 0],
        key=lambda x: x[1], reverse=True
    )
    partes = []
    for nombre, n in items:
        color = color_partido(nombre)
        sigla = sigla_partido(nombre)
        partes.append(
            '<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">'
            '<div style="width:10px;height:10px;border-radius:50%;background:' + color + ';flex-shrink:0;"></div>'
            '<span style="font-size:0.78rem;font-weight:700;color:' + COLOR_TEXT_PRIMARY + ';">' + str(n) + '</span>'
            '<span style="font-size:0.73rem;color:' + COLOR_TEXT_SECONDARY + ';">' + sigla + '</span>'
            '</div>'
        )
    # Organizar en columnas
    n = len(partes)
    cols = min(max_cols, n)
    rows = math.ceil(n / cols)
    html = '<div style="display:grid;grid-template-columns:repeat(' + str(cols) + ',auto);gap:2px 16px;">'
    for p in partes:
        html += p
    html += '</div>'
    return html


def tabla_candidatos_html(df: pd.DataFrame, col_circ: str = None,
                           mostrar_electo: bool = True) -> str:
    """Tabla HTML compacta de candidatos con votos y badge de electo."""
    filas = ""
    for _, row in df.iterrows():
        nombre = str(row.get("nombreCandidato", "")).title()
        partido = str(row.get("nombreAgrupacionPolitica", ""))
        votos = fmt_votos(row.get("totalVotosValidos", 0))
        pct = fmt_pct(row.get("porcentajeVotosValidos", row.get("pct_validos", 0)))
        electo = bool(row.get("electo_proyectado", False))
        color = color_partido(partido)
        circ = str(row.get(col_circ, "")) if col_circ else ""

        badge = ""
        if mostrar_electo and electo:
            badge = '<span class="electo-badge">Electo</span>'

        dot = '<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:' + color + ';margin-right:6px;"></span>'

        fila_bg = "#F0FAF4" if electo else COLOR_SURFACE

        circ_cell = ('<td style="font-size:0.75rem;color:' + COLOR_TEXT_MUTED + ';padding:8px 10px;">'
                     + circ + '</td>') if col_circ else ""

        filas += (
            '<tr style="background:' + fila_bg + ';border-bottom:1px solid ' + COLOR_BORDER + ';">'
            + circ_cell +
            '<td style="padding:8px 10px;">'
            + dot +
            '<span style="font-size:0.82rem;font-weight:600;color:' + COLOR_TEXT_PRIMARY + ';">' + nombre + '</span>'
            ' <span style="font-size:0.72rem;color:' + COLOR_TEXT_MUTED + ';">' + partido[:25] + ('…' if len(partido) > 25 else '') + '</span>'
            + (' &nbsp;' + badge if badge else '') +
            '</td>'
            '<td style="text-align:right;padding:8px 10px;font-size:0.82rem;font-weight:600;'
            'color:' + COLOR_TEXT_PRIMARY + ';font-variant-numeric:tabular-nums;">' + votos + '</td>'
            '<td style="text-align:right;padding:8px 10px;font-size:0.78rem;color:' + COLOR_TEXT_SECONDARY + ';">' + pct + '</td>'
            '</tr>'
        )

    if not filas:
        filas = '<tr><td colspan="4" style="text-align:center;padding:24px;color:' + COLOR_TEXT_MUTED + ';font-size:0.82rem;">Sin datos</td></tr>'

    circ_th = ('<th style="text-align:left;padding:8px 10px;font-size:0.68rem;font-weight:700;'
               'letter-spacing:0.08em;text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';">Circunsc.</th>') if col_circ else ""

    return (
        '<div style="overflow-x:auto;">'
        '<table style="width:100%;border-collapse:collapse;background:' + COLOR_SURFACE + ';'
        'border:1px solid ' + COLOR_BORDER + ';border-radius:8px;overflow:hidden;">'
        '<thead><tr style="background:' + COLOR_SURFACE_ALT + ';border-bottom:2px solid ' + COLOR_BORDER + ';">'
        + circ_th +
        '<th style="text-align:left;padding:8px 10px;font-size:0.68rem;font-weight:700;'
        'letter-spacing:0.08em;text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';">Candidato</th>'
        '<th style="text-align:right;padding:8px 10px;font-size:0.68rem;font-weight:700;'
        'letter-spacing:0.08em;text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';">Votos</th>'
        '<th style="text-align:right;padding:8px 10px;font-size:0.68rem;font-weight:700;'
        'letter-spacing:0.08em;text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';">% válidos</th>'
        '</tr></thead>'
        '<tbody>' + filas + '</tbody>'
        '</table>'
        '</div>'
    )


def _csv_download(df: pd.DataFrame, label: str, filename: str, key: str):
    """Botón de descarga CSV para cualquier DataFrame."""
    cols_excluir = [c for c in df.columns if c.startswith("timestamp") or c.startswith("_")]
    df_clean = df.drop(columns=cols_excluir, errors="ignore")
    csv = df_clean.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label=f"⬇ {label}",
        data=csv.encode("utf-8-sig"),
        file_name=filename,
        mime="text/csv",
        key=key,
        use_container_width=False,
    )


def _filtro_partido_electos(df: pd.DataFrame, col_circuns: str | None,
                             camara_label: str, key_prefix: str):
    """
    Muestra selector de partido + tabla de electos filtrada + descarga.
    df debe tener columna electo_proyectado y nombreAgrupacionPolitica.
    """
    PARTIDOS_PASARON = sorted(
        df[df["electo_proyectado"] == True]["nombreAgrupacionPolitica"].unique()
    )
    if not PARTIDOS_PASARON:
        st.markdown(
            '<p style="color:' + COLOR_TEXT_MUTED + ';font-size:0.82rem;">Sin datos de electos aún.</p>',
            unsafe_allow_html=True
        )
        return

    opciones = ["— Todos los partidos —"] + PARTIDOS_PASARON
    partido_sel = st.selectbox(
        "Filtrar por partido",
        opciones,
        key=f"{key_prefix}_partido_sel",
    )
    solo_electos_chk = st.checkbox(
        "Solo electos proyectados",
        value=True,
        key=f"{key_prefix}_solo_electos",
    )

    df_filt = df.copy()
    if partido_sel != "— Todos los partidos —":
        df_filt = df_filt[df_filt["nombreAgrupacionPolitica"] == partido_sel]
    if solo_electos_chk:
        df_filt = df_filt[df_filt["electo_proyectado"] == True]

    n_electos = int(df_filt["electo_proyectado"].sum()) if "electo_proyectado" in df_filt.columns else 0
    n_total   = len(df_filt)

    col_info, col_dl = st.columns([3, 1])
    with col_info:
        st.markdown(
            f'<div style="font-size:0.78rem;color:{COLOR_TEXT_SECONDARY};margin-bottom:8px;">'
            f'Mostrando <strong>{n_total}</strong> candidatos'
            + (f' · <strong style="color:#1E8A4A">{n_electos} electos proyectados</strong>' if n_electos else "")
            + f'</div>',
            unsafe_allow_html=True,
        )
    with col_dl:
        partido_fn = partido_sel.replace("— Todos los partidos —", "todos").replace(" ", "_")[:20]
        _csv_download(
            df_filt,
            "Descargar CSV",
            f"{camara_label}_{partido_fn}.csv",
            key=f"{key_prefix}_dl",
        )

    st.markdown(
        tabla_candidatos_html(
            df_filt.sort_values("totalVotosValidos", ascending=False).head(80),
            col_circ=col_circuns if partido_sel == "— Todos los partidos —" else None,
        ),
        unsafe_allow_html=True,
    )


# ── Carga de datos ────────────────────────────────────────────────────────────
try:
    df_pres         = cargar_presidenciales()
    df_pres_dpto    = cargar_pres_departamento()
    df_sen_nac_p    = cargar_senado_nacional_partidos()
    df_sen_reg_p    = cargar_senado_regional_partidos()
    df_dip_p        = cargar_diputados_partidos()
    df_parl_p       = cargar_parlamento_partidos()
    df_umbral       = cargar_umbral_escanos()
    df_cand_sn      = cargar_candidatos_senado_nac()
    df_cand_sr      = cargar_candidatos_senado_reg()
    df_cand_dip     = cargar_candidatos_diputados()
    df_cand_parl    = cargar_candidatos_parlamento()
    meta_raw        = cargar_onpe_meta()
    DATA_OK = True
except Exception as e:
    DATA_OK = False
    st.error(f"Error cargando datos ONPE: {e}")
    st.stop()

# Metadatos de escrutinio rápido
ts_extraccion = df_pres["timestamp_extraccion"].iloc[0] if len(df_pres) else "—"
ts_onpe       = df_pres["fecha_actualizacion_onpe"].iloc[0] if len(df_pres) else "—"
actas_pct_pres = df_pres["actas_contabilizadas_pct"].iloc[0] if len(df_pres) else 0
votos_validos_pres = df_pres["votos_validos_total"].iloc[0] if len(df_pres) else 0
participacion_pres = df_pres["participacion_ciudadana_pct"].iloc[0] if len(df_pres) else 0

actas_pct_sen  = df_sen_nac_p["actas_contabilizadas_pct"].iloc[0] if len(df_sen_nac_p) else 0
actas_pct_dip  = df_dip_p["actas_contabilizadas_pct"].iloc[0] if len(df_dip_p) else 0
actas_pct_parl = df_parl_p["actas_contabilizadas_pct"].iloc[0] if len(df_parl_p) else 0

# Escaños D'Hondt por cámara — solo partidos que pasaron la valla completa JNE
# pasa_umbral=True ya refleja la doble condición (votos + escaños mínimos)
def _escanos_camara(camara: str) -> dict:
    sub = df_umbral[
        (df_umbral["camara"] == camara) &
        (df_umbral["pasa_umbral"] == True)
    ]
    if camara in ("Senado Regional", "Diputados"):
        return sub.groupby("partido")["escanos"].sum().to_dict()
    return sub.set_index("partido")["escanos"].to_dict()

esc_sen_nac  = _escanos_camara("Senado Nacional")
esc_sen_reg  = _escanos_camara("Senado Regional")
esc_dip      = _escanos_camara("Diputados")
esc_parl     = _escanos_camara("Parlamento Andino")

# Senado combinado (nac + reg)
esc_sen_total = {}
for p, n in {**esc_sen_nac, **esc_sen_reg}.items():
    esc_sen_total[p] = esc_sen_total.get(p, 0) + n


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="padding:32px 0 8px 0;">'
    '<div style="font-size:0.63rem;font-weight:700;letter-spacing:0.12em;'
    'text-transform:uppercase;color:' + COLOR_ACCENT + ';margin-bottom:8px;">Resultados electorales</div>'
    '<h1 style="color:' + COLOR_PRIMARY + ';font-size:1.75rem;font-weight:700;'
    'margin:0 0 4px 0;letter-spacing:-0.02em;">Elecciones Generales 2026</h1>'
    '<p style="color:' + COLOR_TEXT_SECONDARY + ';font-size:0.85em;margin:0;">'
    'Resultados preliminares \u00b7 Fuente: API ONPE \u00b7 '
    'Extracción: ' + str(ts_extraccion) + ' (Lima)'
    '</p>'
    '</div>',
    unsafe_allow_html=True,
)

# Banner PRELIMINAR
st.markdown(
    '<div style="background:#FEF7EC;border:1px solid #F0C97A;border-radius:6px;'
    'padding:8px 14px;margin-bottom:20px;font-size:0.80rem;color:#7A4A00;">'
    '<strong>Resultados preliminares.</strong> Datos sujetos a variación hasta el 100% de actas contabilizadas. '
    'Última actualización ONPE: ' + str(ts_onpe) + '.'
    '</div>',
    unsafe_allow_html=True,
)

col_refresh, _ = st.columns([1, 4])
with col_refresh:
    if st.button("🔄 Actualizar datos", key="refresh_cache"):
        st.cache_data.clear()
        st.rerun()
        
st.markdown(
    '<div style="border-top:2px solid ' + COLOR_BORDER + ';margin-bottom:24px;"></div>',
    unsafe_allow_html=True,
)


# ── KPIs globales ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(_kpi("Actas contabilizadas", fmt_pct(actas_pct_pres),
                     f"{int(df_pres['actas_contabilizadas_n'].iloc[0]):,} / {int(df_pres['actas_total'].iloc[0]):,}"),
                unsafe_allow_html=True)
with c2:
    st.markdown(_kpi("Participación ciudadana", fmt_pct(participacion_pres)), unsafe_allow_html=True)
with c3:
    st.markdown(_kpi("Votos válidos (presidencial)", fmt_votos(votos_validos_pres)), unsafe_allow_html=True)
with c4:
    st.markdown(_kpi("Última actualiz. ONPE", str(ts_onpe).split(" ")[1] if " " in str(ts_onpe) else str(ts_onpe),
                     str(ts_onpe).split(" ")[0] if " " in str(ts_onpe) else ""),
                unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:28px;'></div>", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_resumen, tab_pres, tab_sen, tab_dip, tab_parl = st.tabs([
    "Resumen", "Presidencial", "Senado", "Diputados", "Parlamento Andino"
])


# ═══════════════════════════════════════════════════════════════
# TAB 0 — RESUMEN
# ═══════════════════════════════════════════════════════════════
with tab_resumen:
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    col_pres, col_sen, col_dip = st.columns([1.1, 1, 1])

    # ── Presidencial ──
    with col_pres:
        st.markdown(
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:12px;">'
            'Presidencial \u00b7 36 candidatos</div>',
            unsafe_allow_html=True,
        )
        # Top 2 más votados
        top2 = df_pres.head(2)
        for _, row in top2.iterrows():
            color = color_partido(row["nombreAgrupacionPolitica"])
            partes_n = str(row["nombreCandidato"]).title().split(" ")
            nombre = partes_n[0] + " " + partes_n[1] if len(partes_n) >= 2 else partes_n[0]
            st.markdown(
                '<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">'
                '<div style="width:4px;height:40px;background:' + color + ';border-radius:2px;flex-shrink:0;"></div>'
                '<div>'
                '<div style="font-size:0.95rem;font-weight:700;color:' + COLOR_TEXT_PRIMARY + ';">' + nombre + '</div>'
                '<div style="font-size:0.72rem;color:' + COLOR_TEXT_MUTED + ';">' + str(row["nombreAgrupacionPolitica"]) + '</div>'
                '</div>'
                '<div style="margin-left:auto;text-align:right;">'
                '<div style="font-size:1.15rem;font-weight:700;color:' + color + ';font-variant-numeric:tabular-nums;">'
                + fmt_pct(row["porcentajeVotosValidos"]) + '</div>'
                '<div style="font-size:0.72rem;color:' + COLOR_TEXT_MUTED + ';">' + fmt_votos(row["totalVotosValidos"]) + ' votos</div>'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        # Barra de avance
        st.markdown(
            '<div style="font-size:0.72rem;color:' + COLOR_TEXT_MUTED + ';margin-top:4px;">'
            + fmt_pct(actas_pct_pres) + ' contabilizado</div>'
            + barra_escrutinio(actas_pct_pres),
            unsafe_allow_html=True,
        )

    # ── Senado ──
    with col_sen:
        st.markdown(
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:8px;">'
            'Senado \u00b7 60 esca\u00f1os</div>',
            unsafe_allow_html=True,
        )
        fig_sen = hemiciclo_plotly(esc_sen_total, total_escanos=60)
        st.plotly_chart(fig_sen, use_container_width=True, config={"displayModeBar": False}, key="hemiciclo_sen_resumen")
        st.markdown(leyenda_partidos(esc_sen_total), unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.72rem;color:' + COLOR_TEXT_MUTED + ';margin-top:6px;">'
            + fmt_pct(actas_pct_sen) + ' contabilizado</div>'
            + barra_escrutinio(actas_pct_sen),
            unsafe_allow_html=True,
        )

    # ── Diputados ──
    with col_dip:
        st.markdown(
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:8px;">'
            'Diputados \u00b7 130 esca\u00f1os</div>',
            unsafe_allow_html=True,
        )
        fig_dip = hemiciclo_plotly(esc_dip, total_escanos=130)
        st.plotly_chart(fig_dip, use_container_width=True, config={"displayModeBar": False}, key="hemiciclo_dip_resumen")
        st.markdown(leyenda_partidos(esc_dip), unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.72rem;color:' + COLOR_TEXT_MUTED + ';margin-top:6px;">'
            + fmt_pct(actas_pct_dip) + ' contabilizado</div>'
            + barra_escrutinio(actas_pct_dip),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div style="border-top:1px solid ' + COLOR_BORDER + ';margin:16px 0 12px 0;"></div>',
        unsafe_allow_html=True,
    )

    # Nota metodológica del umbral
    partidos_pasan = df_umbral[df_umbral["pasa_umbral"] == True]["partido"].unique()
    st.markdown(
        '<div style="font-size:0.78rem;color:' + COLOR_TEXT_MUTED + ';line-height:1.6;">'
        '<strong style="color:' + COLOR_TEXT_SECONDARY + ';">Nota metodológica.</strong> '
        'Escaños calculados con método D\u2019Hondt sobre resultados al ' + fmt_pct(actas_pct_sen) + ' de escrutinio. '
        'Partidos que superan la valla del 5%%: '
        + ', '.join(sorted(partidos_pasan)) + '. '
        'Senado nacional: datos preliminares (ONPE expone top-56 candidatos del endpoint).'
        '</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════
# TAB 1 — PRESIDENCIAL
# ═══════════════════════════════════════════════════════════════
with tab_pres:
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # KPIs presidencial
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(_kpi("Actas contabilizadas", fmt_pct(actas_pct_pres),
                         f"{int(df_pres['actas_contabilizadas_n'].iloc[0]):,} / {int(df_pres['actas_total'].iloc[0]):,}"),
                    unsafe_allow_html=True)
    with k2:
        st.markdown(_kpi("Votos válidos", fmt_votos(votos_validos_pres)), unsafe_allow_html=True)
    with k3:
        st.markdown(_kpi("Participación", fmt_pct(participacion_pres)), unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # Barra horizontal de candidatos
    col_tabla, col_chart = st.columns([1, 1.2])

    with col_tabla:
        st.markdown(
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:10px;">'
            'Resultados por candidato</div>',
            unsafe_allow_html=True,
        )
        st.markdown(tabla_candidatos_html(df_pres, mostrar_electo=False), unsafe_allow_html=True)

    with col_chart:
        st.markdown(
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:10px;">'
            'Distribución de votos válidos</div>',
            unsafe_allow_html=True,
        )
        df_chart = df_pres.head(10).copy()
        nombres_cortos = [
            str(r["nombreCandidato"]).title().split(" ")[0] + " " + str(r["nombreCandidato"]).title().split(" ")[-1]
            for _, r in df_chart.iterrows()
        ]
        colors = [color_partido(r["nombreAgrupacionPolitica"]) for _, r in df_chart.iterrows()]

        fig_pres = go.Figure(go.Bar(
            x=df_chart["porcentajeVotosValidos"],
            y=nombres_cortos,
            orientation="h",
            marker=dict(color=colors, line=dict(width=0)),
            text=[fmt_pct(v) for v in df_chart["porcentajeVotosValidos"]],
            textposition="outside",
            textfont=dict(size=11, color=COLOR_TEXT_SECONDARY),
            hovertemplate="<b>%{y}</b><br>%{x:.2f}% votos válidos<extra></extra>",
        ))
        fig_pres.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=350,
            margin=dict(t=8, b=8, l=8, r=60),
            xaxis=dict(visible=False, range=[0, df_chart["porcentajeVotosValidos"].max() * 1.25]),
            yaxis=dict(autorange="reversed", tickfont=dict(size=11, color=COLOR_TEXT_PRIMARY)),
            font=dict(family="sans-serif"),
            hoverlabel=dict(bgcolor=COLOR_SURFACE, bordercolor=COLOR_BORDER,
                            font=dict(color=COLOR_TEXT_PRIMARY, size=12)),
        )
        st.plotly_chart(fig_pres, use_container_width=True, config={"displayModeBar": False}, key="bar_presidencial")

    # Mapa por departamento
    st.markdown(
        '<div style="border-top:1px solid ' + COLOR_BORDER + ';margin:20px 0 16px 0;"></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
        'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:12px;">'
        'Candidato más votado por departamento</div>',
        unsafe_allow_html=True,
    )

    # Tabla de ganador por departamento
    idx_max = df_pres_dpto.groupby("departamento")["totalVotosValidos"].idxmax()
    ganadores = df_pres_dpto.loc[idx_max].copy()
    ganadores = ganadores.sort_values("departamento")

    cols_dept = st.columns(3)
    for i, (_, row) in enumerate(ganadores.iterrows()):
        with cols_dept[i % 3]:
            color = color_partido(row["nombreAgrupacionPolitica"])
            nombre = str(row["nombreCandidato"]).title()
            nombre_corto = nombre.split(" ")[0] + " " + nombre.split(" ")[-1]
            st.markdown(
                '<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">'
                '<div style="width:3px;height:32px;background:' + color + ';border-radius:2px;flex-shrink:0;"></div>'
                '<div>'
                '<div style="font-size:0.70rem;font-weight:700;color:' + COLOR_TEXT_SECONDARY + ';">'
                + str(row["departamento"]).title() + '</div>'
                '<div style="font-size:0.78rem;color:' + COLOR_TEXT_PRIMARY + ';font-weight:600;">'
                + nombre_corto + '</div>'
                '<div style="font-size:0.68rem;color:' + COLOR_TEXT_MUTED + ';">'
                + fmt_pct(row["porcentajeVotosValidos"]) + '</div>'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )


# ═══════════════════════════════════════════════════════════════
# TAB 2 — SENADO
# ═══════════════════════════════════════════════════════════════
with tab_sen:
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    sub_nac, sub_reg = st.tabs(["Distrito Único Nacional", "Distrito Regional"])

    # ── Senado Nacional ──
    with sub_nac:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        k1, k2, k3 = st.columns(3)
        with k1:
            st.markdown(_kpi("Actas contabilizadas", fmt_pct(actas_pct_sen),
                             f"{int(df_sen_nac_p['actas_contabilizadas_n'].iloc[0]):,} / {int(df_sen_nac_p['actas_total'].iloc[0]):,}"),
                        unsafe_allow_html=True)
        with k2:
            st.markdown(_kpi("Votos válidos", fmt_votos(df_sen_nac_p["votos_validos_total"].iloc[0])), unsafe_allow_html=True)
        with k3:
            n_pasan = len(df_umbral[(df_umbral["camara"] == "Senado Nacional") & (df_umbral["pasa_umbral"] == True)])
            st.markdown(_kpi("Partidos sobre la valla", str(n_pasan), "umbral 5% votos válidos"), unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        col_hem, col_tabla2 = st.columns([1, 1.4])

        with col_hem:
            st.markdown(
                '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
                'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:6px;">'
                '30 escaños \u00b7 D\u2019Hondt</div>',
                unsafe_allow_html=True,
            )
            fig_sn = hemiciclo_plotly(esc_sen_nac, total_escanos=30)
            st.plotly_chart(fig_sn, use_container_width=True, config={"displayModeBar": False}, key="hemiciclo_sen_nac")
            st.markdown(leyenda_partidos(esc_sen_nac, max_cols=2), unsafe_allow_html=True)

        with col_tabla2:
            st.markdown(
                '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
                'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:6px;">'
                'Candidatos — datos preliminares</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div style="background:#FEF7EC;border:1px solid #F0C97A;border-radius:5px;'
                'padding:6px 10px;margin-bottom:10px;font-size:0.74rem;color:#7A4A00;">'
                'ONPE expone los top-56 candidatos de este endpoint. Los electos marcados son preliminares.'
                '</div>',
                unsafe_allow_html=True,
            )
            _filtro_partido_electos(df_cand_sn, col_circuns=None,
                                    camara_label="senado_nacional", key_prefix="sn")

        # Votos por partido
        st.markdown(
            '<div style="border-top:1px solid ' + COLOR_BORDER + ';margin:20px 0 14px 0;"></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:10px;">'
            'Votos por partido \u00b7 senado nacional</div>',
            unsafe_allow_html=True,
        )
        df_sn_sorted = df_sen_nac_p.sort_values("totalVotosValidos", ascending=False)
        umbral_sn = df_umbral[(df_umbral["camara"] == "Senado Nacional") & (df_umbral["circunscripcion"] == "NACIONAL")]
        umbral_sn_dict = umbral_sn.set_index("partido")[["pasa_umbral", "escanos"]].to_dict("index")

        for _, row in df_sn_sorted.iterrows():
            partido = row["nombreAgrupacionPolitica"]
            color = color_partido(partido)
            u = umbral_sn_dict.get(partido, {})
            pasa = u.get("pasa_umbral", False)
            esc = int(u.get("escanos", 0))
            badge_u = ('<span class="electo-badge">Pasa valla \u00b7 ' + str(esc) + ' esc.</span> '
                       if pasa else
                       '<span style="font-size:0.68rem;color:' + COLOR_TEXT_MUTED + ';">No supera valla</span>')
            pct_v = float(row.get("porcentajeVotosValidos", 0) or 0)
            st.markdown(
                '<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">'
                '<div style="width:10px;height:10px;border-radius:50%;background:' + color + ';flex-shrink:0;"></div>'
                '<div style="min-width:200px;font-size:0.80rem;color:' + COLOR_TEXT_PRIMARY + ';font-weight:600;">'
                + partido[:35] + ('…' if len(partido) > 35 else '') + '</div>'
                '<div style="flex:1;background:' + COLOR_BORDER + ';border-radius:3px;height:8px;">'
                '<div style="width:' + str(min(100, pct_v * 4)) + '%;background:' + color + ';height:8px;border-radius:3px;"></div>'
                '</div>'
                '<div style="min-width:60px;text-align:right;font-size:0.78rem;'
                'font-variant-numeric:tabular-nums;color:' + COLOR_TEXT_SECONDARY + ';">'
                + fmt_pct(pct_v) + '</div>'
                '<div style="min-width:80px;text-align:right;font-size:0.75rem;color:' + COLOR_TEXT_MUTED + ';">'
                + fmt_votos(row["totalVotosValidos"]) + '</div>'
                '<div>' + badge_u + '</div>'
                '</div>',
                unsafe_allow_html=True,
            )

    # ── Senado Regional ──
    with sub_reg:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        k1, k2 = st.columns(2)
        with k1:
            actas_sr = df_sen_reg_p["actas_contabilizadas_pct"].mean()
            st.markdown(_kpi("Avance promedio distritos", fmt_pct(actas_sr)), unsafe_allow_html=True)
        with k2:
            st.markdown(_kpi("Escaños regionales", "30", "1 por circunscripción + Lima Metropolitana 4"), unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        col_hem2, col_info = st.columns([1, 1.4])
        with col_hem2:
            st.markdown(
                '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
                'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:6px;">'
                '30 escaños regionales</div>',
                unsafe_allow_html=True,
            )
            fig_sr = hemiciclo_plotly(esc_sen_reg, total_escanos=30)
            st.plotly_chart(fig_sr, use_container_width=True, config={"displayModeBar": False}, key="hemiciclo_sen_reg")
            st.markdown(leyenda_partidos(esc_sen_reg, max_cols=2), unsafe_allow_html=True)

        with col_info:
            st.markdown(
                '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
                'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:8px;">'
                'Senadores electos proyectados por región</div>',
                unsafe_allow_html=True,
            )
            electos_sr = df_cand_sr[df_cand_sr["electo_proyectado"] == True].copy()
            if len(electos_sr):
                st.markdown(tabla_candidatos_html(
                    electos_sr.sort_values(["distrito_electoral", "totalVotosValidos"], ascending=[True, False]),
                    col_circ="distrito_electoral"
                ), unsafe_allow_html=True)
            else:
                st.markdown(
                    '<p style="color:' + COLOR_TEXT_MUTED + ';font-size:0.82rem;">Sin electos proyectados aún.</p>',
                    unsafe_allow_html=True,
                )

        # Filtro por partido + distrito
        st.markdown(
            '<div style="border-top:1px solid ' + COLOR_BORDER + ';margin:20px 0 14px 0;"></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:10px;">'
            'Explorar candidatos</div>',
            unsafe_allow_html=True,
        )
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            distritos = sorted(df_cand_sr["distrito_electoral"].unique())
            dist_sel = st.selectbox("Distrito electoral", ["— Todos —"] + distritos,
                                    key="sel_dist_sr")
        with col_f2:
            partidos_sr = ["— Todos —"] + sorted(df_cand_sr["nombreAgrupacionPolitica"].unique())
            partido_sr_sel = st.selectbox("Partido", partidos_sr, key="sel_partido_sr")

        solo_electos_sr = st.checkbox("Solo electos proyectados", value=False, key="ck_electos_sr")

        df_sr_filt = df_cand_sr.copy()
        if dist_sel != "— Todos —":
            df_sr_filt = df_sr_filt[df_sr_filt["distrito_electoral"] == dist_sel]
        if partido_sr_sel != "— Todos —":
            df_sr_filt = df_sr_filt[df_sr_filt["nombreAgrupacionPolitica"] == partido_sr_sel]
        if solo_electos_sr:
            df_sr_filt = df_sr_filt[df_sr_filt["electo_proyectado"] == True]

        col_info_sr, col_dl_sr = st.columns([3, 1])
        n_sr = int(df_sr_filt["electo_proyectado"].sum())
        with col_info_sr:
            st.markdown(
                f'<div style="font-size:0.78rem;color:{COLOR_TEXT_SECONDARY};margin-bottom:8px;">'
                f'<strong>{len(df_sr_filt)}</strong> candidatos'
                + (f' · <strong style="color:#1E8A4A">{n_sr} electos proyectados</strong>' if n_sr else "")
                + '</div>', unsafe_allow_html=True)
        with col_dl_sr:
            _csv_download(df_sr_filt, "Descargar CSV",
                          f"senado_regional_{dist_sel[:15]}_{partido_sr_sel[:10]}.csv",
                          key="dl_sr")

        col_circ_sr = "distrito_electoral" if dist_sel == "— Todos —" else None
        st.markdown(tabla_candidatos_html(
            df_sr_filt.sort_values("totalVotosValidos", ascending=False).head(60),
            col_circ=col_circ_sr,
        ), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# TAB 3 — DIPUTADOS
# ═══════════════════════════════════════════════════════════════
with tab_dip:
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(_kpi("Actas contabilizadas", fmt_pct(actas_pct_dip),
                         f"{int(df_dip_p['actas_contabilizadas_n'].iloc[0]):,} / {int(df_dip_p['actas_total'].iloc[0]):,}"),
                    unsafe_allow_html=True)
    with k2:
        total_electos_dip = int(df_cand_dip["electo_proyectado"].sum())
        st.markdown(_kpi("Diputados electos proyectados", str(total_electos_dip), "de 130 escaños"), unsafe_allow_html=True)
    with k3:
        n_pasan_dip = len(df_umbral[(df_umbral["camara"] == "Diputados") & (df_umbral["pasa_umbral"] == True)]["partido"].unique())
        st.markdown(_kpi("Partidos sobre la valla", str(n_pasan_dip), "umbral 5% por circunscripción"), unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    col_hem3, col_leyenda3 = st.columns([1.2, 1])
    with col_hem3:
        st.markdown(
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:6px;">'
            '130 escaños \u00b7 D\u2019Hondt por circunscripción</div>',
            unsafe_allow_html=True,
        )
        fig_dip2 = hemiciclo_plotly(esc_dip, total_escanos=130)
        st.plotly_chart(fig_dip2, use_container_width=True, config={"displayModeBar": False}, key="hemiciclo_dip_tab")

    with col_leyenda3:
        st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
        st.markdown(leyenda_partidos(esc_dip, max_cols=2), unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.72rem;color:' + COLOR_TEXT_MUTED + ';margin-top:8px;">'
            + fmt_pct(actas_pct_dip) + ' contabilizado</div>'
            + barra_escrutinio(actas_pct_dip),
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div style="border-top:1px solid ' + COLOR_BORDER + ';margin:20px 0 14px 0;"></div>',
        unsafe_allow_html=True,
    )

    # Filtro por circunscripción
    col_f1d, col_f2d = st.columns(2)
    with col_f1d:
        circs = sorted(df_cand_dip["circunscripcion"].unique())
        circ_sel = st.selectbox("Circunscripción", ["— Todas —"] + circs, key="sel_circ_dip")
    with col_f2d:
        partidos_dip = ["— Todos —"] + sorted(df_cand_dip["nombreAgrupacionPolitica"].unique())
        partido_dip_sel = st.selectbox("Partido", partidos_dip, key="sel_partido_dip")

    solo_electos = st.checkbox("Solo electos proyectados", value=False, key="ck_electos_dip")

    df_dip_filt = df_cand_dip.copy()
    if circ_sel != "— Todas —":
        df_dip_filt = df_dip_filt[df_dip_filt["circunscripcion"] == circ_sel]
    if partido_dip_sel != "— Todos —":
        df_dip_filt = df_dip_filt[df_dip_filt["nombreAgrupacionPolitica"] == partido_dip_sel]
    if solo_electos:
        df_dip_filt = df_dip_filt[df_dip_filt["electo_proyectado"] == True]

    col_info_dip, col_dl_dip = st.columns([3, 1])
    n_dip = int(df_dip_filt["electo_proyectado"].sum())
    with col_info_dip:
        st.markdown(
            f'<div style="font-size:0.78rem;color:{COLOR_TEXT_SECONDARY};margin-bottom:8px;">'
            f'<strong>{len(df_dip_filt)}</strong> candidatos'
            + (f' · <strong style="color:#1E8A4A">{n_dip} electos proyectados</strong>' if n_dip else "")
            + '</div>', unsafe_allow_html=True)
    with col_dl_dip:
        _csv_download(df_dip_filt, "Descargar CSV",
                      f"diputados_{circ_sel[:15]}_{partido_dip_sel[:10]}.csv",
                      key="dl_dip")

    col_circ_dip = "circunscripcion" if circ_sel == "— Todas —" else None
    st.markdown(tabla_candidatos_html(
        df_dip_filt.sort_values("totalVotosValidos", ascending=False).head(80),
        col_circ=col_circ_dip,
    ), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# TAB 4 — PARLAMENTO ANDINO
# ═══════════════════════════════════════════════════════════════
with tab_parl:
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    k1, k2 = st.columns(2)
    with k1:
        st.markdown(_kpi("Actas contabilizadas", fmt_pct(actas_pct_parl),
                         f"{int(df_parl_p['actas_contabilizadas_n'].iloc[0]):,} / {int(df_parl_p['actas_total'].iloc[0]):,}"),
                    unsafe_allow_html=True)
    with k2:
        st.markdown(_kpi("Escaños", "5", "Parlamento Andino \u00b7 Perú"), unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    col_p1, col_p2 = st.columns([1, 1.5])

    with col_p1:
        st.markdown(
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:6px;">'
            '5 escaños \u00b7 D\u2019Hondt</div>',
            unsafe_allow_html=True,
        )
        fig_parl = hemiciclo_plotly(esc_parl, total_escanos=5)
        st.plotly_chart(fig_parl, use_container_width=True, config={"displayModeBar": False}, key="hemiciclo_parlamento")
        st.markdown(leyenda_partidos(esc_parl, max_cols=2), unsafe_allow_html=True)

        # Votos por partido
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:8px;">'
            'Votos por partido</div>',
            unsafe_allow_html=True,
        )
        umbral_parl = df_umbral[(df_umbral["camara"] == "Parlamento Andino") & (df_umbral["circunscripcion"] == "NACIONAL")]
        umbral_parl_dict = umbral_parl.set_index("partido")[["pasa_umbral", "escanos"]].to_dict("index")
        for _, row in df_parl_p.iterrows():
            partido = row["nombreAgrupacionPolitica"]
            color = color_partido(partido)
            u = umbral_parl_dict.get(partido, {})
            pasa = u.get("pasa_umbral", False)
            esc = int(u.get("escanos", 0))
            badge_u = ('<span class="electo-badge">' + str(esc) + ' esc.</span>'
                       if pasa else "")
            pct_v = float(row.get("porcentajeVotosValidos", 0) or 0)
            st.markdown(
                '<div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">'
                '<div style="width:8px;height:8px;border-radius:50%;background:' + color + ';flex-shrink:0;"></div>'
                '<div style="min-width:140px;font-size:0.76rem;color:' + COLOR_TEXT_PRIMARY + ';">'
                + partido[:22] + ('…' if len(partido) > 22 else '') + '</div>'
                '<div style="flex:1;background:' + COLOR_BORDER + ';border-radius:3px;height:6px;">'
                '<div style="width:' + str(min(100, pct_v * 5)) + '%;background:' + color + ';height:6px;border-radius:3px;"></div>'
                '</div>'
                '<div style="min-width:45px;text-align:right;font-size:0.75rem;color:' + COLOR_TEXT_SECONDARY + ';">'
                + fmt_pct(pct_v) + '</div>'
                + (' <div>' + badge_u + '</div>' if badge_u else '')
                + '</div>',
                unsafe_allow_html=True,
            )

    with col_p2:
        st.markdown(
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.10em;'
            'text-transform:uppercase;color:' + COLOR_TEXT_MUTED + ';margin-bottom:8px;">'
            'Candidatos por partido</div>',
            unsafe_allow_html=True,
        )
        col_dl_parl, _ = st.columns([1, 2])
        with col_dl_parl:
            _csv_download(df_cand_parl, "Descargar CSV",
                          "parlamento_andino_candidatos.csv", key="dl_parl")
        _filtro_partido_electos(df_cand_parl, col_circuns=None,
                                camara_label="parlamento_andino", key_prefix="parl")


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="page-footer">'
    '<span>Monitor Electoral Per\u00fa 2026 \u00b7 OACNUDH</span>'
    '<span>Fuente: API ONPE \u00b7 Resultados preliminares</span>'
    '</div>',
    unsafe_allow_html=True,
)
