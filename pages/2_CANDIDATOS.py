# ============================================================
# pages/2_Candidatos.py — Monitor Electoral Perú 2026
# Tabla filtrable de candidatos con perfil expandible.
# ============================================================

import streamlit as st
import pandas as pd
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

from config import (
    APP_TITLE, APP_ICON, APP_CONFIDENTIAL_LABEL, APP_VERSION,
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_BACKGROUND, COLOR_SURFACE,
    COLOR_BORDER, COLOR_BORDER_STRONG,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_RIESGO_ALTO, COLOR_RIESGO_ALTO_BG,
    COLOR_RIESGO_MEDIO, COLOR_RIESGO_MEDIO_BG,
    COLOR_RIESGO_BAJO, COLOR_RIESGO_BAJO_BG,
    COLOR_RIESGO_NONE, COLOR_RIESGO_NONE_BG,
    COLOR_REINFO, COLOR_REINFO_BG,
    COLOR_VOTO, COLOR_VOTO_TEXT,
    LABEL_RIESGO, REGIONES_PRIORITARIAS,
    LEYES_COLS, GLOBAL_CSS,
    SCORE_ALTO_MIN, SCORE_MEDIO_MIN,
)
from data_loader import (
    cargar_candidatos, cargar_votaciones, cargar_reinfo,
    cargar_leyes, normalizar_dni,
)

# -------------------------------------------------------
# SECTION: Page setup
# -------------------------------------------------------
st.set_page_config(
    page_title=f"Candidatos · {APP_TITLE}",
    page_icon=APP_ICON,
    layout="wide",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

if not st.session_state.get("autenticado", False):
    st.warning("Debes iniciar sesión primero.")
    st.stop()

# -------------------------------------------------------
# SECTION: Cargar y preparar datos
# -------------------------------------------------------
@st.cache_data
def preparar_tabla_candidatos() -> pd.DataFrame:
    cands  = cargar_candidatos()
    votos  = cargar_votaciones()
    reinfo = cargar_reinfo()

    df = cands.merge(
        votos[[
            "dni", "score_total", "score_procrimen", "score_contexto",
            "bonus_autoria", "es_congresista", "grupo_parl", "leyes_autoria",
        ]],
        on="dni", how="left",
    )

    dni_reinfo = set(reinfo["dni"].unique())
    df["tiene_reinfo"] = df["dni"].isin(dni_reinfo)

    def nivel(s):
        if pd.isna(s): return "none"
        if s >= SCORE_ALTO_MIN: return "alto"
        if s >= SCORE_MEDIO_MIN: return "medio"
        return "bajo"

    df["nivel_riesgo"]    = df["score_total"].apply(nivel)
    df["etiqueta_riesgo"] = df["nivel_riesgo"].map(LABEL_RIESGO)
    # es_congresista: derivado del cruce de DNIs con la hoja 03_VOTACIONES.
    # La columna del Excel contiene solo "NO" — el flag real es si el DNI
    # del candidato aparece en el padrón de congresistas con registro de votos.
    dni_congresistas = set(votos["dni"].unique())
    df["es_congresista"] = df["dni"].isin(dni_congresistas).map({True: "SI", False: "NO"})

    # Flag: candidato presidencial titular (excluye vicepresidentes)
    df["es_presidencial"] = (
        df["tipo_eleccion"].str.upper().str.contains("PRESIDENCIAL", na=False)
        & ~df["cargo"].str.upper().str.contains("VICE", na=False)
    )

    if "fecha_nac" in df.columns:
        df["fecha_nac"] = pd.to_datetime(
            df["fecha_nac"], errors="coerce"
        ).dt.strftime("%d/%m/%Y")

    return df


with st.spinner("Cargando candidatos..."):
    df_full    = preparar_tabla_candidatos()
    leyes_df   = cargar_leyes()
    votos_full = cargar_votaciones()

# -------------------------------------------------------
# SECTION: Header
# -------------------------------------------------------
st.markdown(
    f"""
    <div style="padding:4px 0 20px 0; border-bottom:2px solid {COLOR_BORDER};
                margin-bottom:24px;">
        <div style="font-size:0.63rem; font-weight:700; letter-spacing:0.12em;
                    text-transform:uppercase; color:{COLOR_ACCENT}; margin-bottom:6px;">
            Explorador
        </div>
        <h1 style="font-size:1.6rem; font-weight:700; color:{COLOR_TEXT_PRIMARY};
                   margin:0 0 4px 0; letter-spacing:-0.02em; line-height:1.2;">
            Candidatos
        </h1>
        <p style="font-size:0.85rem; color:{COLOR_TEXT_SECONDARY}; margin:0;">
            {len(df_full):,} candidatos inscritos · JNE · Elecciones 2026
            · Haz clic en una fila para ver el perfil completo
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------
# SECTION: Filtros — siempre visibles
# -------------------------------------------------------
f1, f2, f3, f4, f5 = st.columns([2, 2, 2, 2, 2], gap="small")

with f1:
    busqueda = st.text_input("Buscar por nombre", placeholder="Ej: García López...")
with f2:
    tipos = ["Todos"] + sorted(df_full["tipo_eleccion"].dropna().unique().tolist())
    tipo_sel = st.selectbox("Tipo de elección", tipos)
with f3:
    regiones = ["Todas"] + sorted(df_full["region"].dropna().unique().tolist())
    region_sel = st.selectbox("Región", regiones)
with f4:
    estados = ["Todos"] + sorted(df_full["estado_jne"].dropna().unique().tolist())
    estado_sel = st.selectbox("Estado JNE", estados)
with f5:
    flag_opts = [
        "Todos", "Congresistas postulando", "Con vínculo REINFO",
        "Riesgo alto", "Candidatos presidenciales",
    ]
    flag_sel = st.selectbox("Filtro rápido", flag_opts)

# -------------------------------------------------------
# SECTION: Aplicar filtros
# -------------------------------------------------------
df_filtrado = df_full.copy()

if busqueda:
    df_filtrado = df_filtrado[
        df_filtrado["nombre_completo"].str.contains(busqueda.upper(), na=False)
    ]
if tipo_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["tipo_eleccion"] == tipo_sel]
if region_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["region"] == region_sel]
if estado_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["estado_jne"] == estado_sel]
if flag_sel == "Congresistas postulando":
    df_filtrado = df_filtrado[df_filtrado["es_congresista"] == "SI"]
elif flag_sel == "Con vínculo REINFO":
    df_filtrado = df_filtrado[df_filtrado["tiene_reinfo"] == True]
elif flag_sel == "Riesgo alto":
    df_filtrado = df_filtrado[df_filtrado["nivel_riesgo"] == "alto"]
elif flag_sel == "Candidatos presidenciales":
    df_filtrado = df_filtrado[df_filtrado["es_presidencial"] == True]

# -------------------------------------------------------
# SECTION: Contador y descarga
# -------------------------------------------------------
c_count, c_dl = st.columns([4, 1])
with c_count:
    st.markdown(
        f"<p style='color:{COLOR_TEXT_MUTED}; font-size:0.82em; margin:8px 0 6px 0;'>"
        f"Mostrando <b style='color:{COLOR_TEXT_PRIMARY};'>{len(df_filtrado):,}</b>"
        f" candidatos</p>",
        unsafe_allow_html=True,
    )
with c_dl:
    cols_dl = [
        "dni", "nombre_completo", "partido", "tipo_eleccion", "cargo",
        "posicion", "region", "estado_jne", "es_congresista",
        "tiene_reinfo", "score_total", "nivel_riesgo",
    ]
    csv_bytes = df_filtrado[cols_dl].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descargar (CSV)",
        data=csv_bytes,
        file_name="candidatos_filtrado.csv",
        mime="text/csv",
        use_container_width=True,
    )

# -------------------------------------------------------
# SECTION: Tabla principal AgGrid
#
# Solo datos de identificación y contexto.
# Score, riesgo, REINFO y congresista se reservan al perfil.
# -------------------------------------------------------
COLS_TABLA = [
    "nombre_completo", "partido", "cargo",
    "posicion", "region", "tipo_eleccion", "estado_jne",
    "score_total", "etiqueta_riesgo", "flags_tabla",
]

# Construir columna flags_tabla compacta para la tabla
def _build_flags(row):
    f = []
    if row["es_congresista"] == "SI":    f.append("Congresista")
    if row["tiene_reinfo"]:              f.append("REINFO")
    if row["es_presidencial"]:           f.append("Presidencial")
    return " · ".join(f) if f else "—"

df_filtrado = df_filtrado.copy()
df_filtrado["flags_tabla"] = df_filtrado.apply(_build_flags, axis=1)

df_tabla = df_filtrado[COLS_TABLA].copy()

gb = GridOptionsBuilder.from_dataframe(df_tabla)
gb.configure_default_column(
    resizable=True, sortable=True, filter=True,
    wrapText=False, autoHeight=False,
)
gb.configure_column("nombre_completo", header_name="Nombre",        minWidth=230, flex=2)
gb.configure_column("partido",         header_name="Partido",       minWidth=160, flex=2)
gb.configure_column("cargo",           header_name="Cargo",         minWidth=140, flex=1)
gb.configure_column("posicion",        header_name="Pos.",          maxWidth=65)
gb.configure_column("region",          header_name="Región",        minWidth=120, flex=1)
gb.configure_column("tipo_eleccion",   header_name="Tipo elección", minWidth=140, flex=1)
gb.configure_column("estado_jne",      header_name="Estado JNE",    minWidth=110, flex=1)
gb.configure_column("score_total",     header_name="Score",         maxWidth=75)
gb.configure_column("etiqueta_riesgo", header_name="Riesgo",        minWidth=110, flex=1)
gb.configure_column("flags_tabla",     header_name="Flags",         minWidth=170, flex=1)

# Color de fila según nivel de riesgo
row_style_jscode = JsCode("""
function(params) {
    var r = params.data.etiqueta_riesgo;
    if (r && r.includes('Alto'))  return {'background-color': '#FDECEA'};
    if (r && r.includes('Medio')) return {'background-color': '#FEF9E7'};
    if (r && r.includes('Bajo'))  return {'background-color': '#EAF4EC'};
    return {};
}
""")
gb.configure_grid_options(
    rowStyle=row_style_jscode,
    rowHeight=32, headerHeight=36,
    suppressMovableColumns=False, enableBrowserTooltips=True,
)

gb.configure_selection(selection_mode="single", use_checkbox=False, pre_selected_rows=[])

grid_response = AgGrid(
    df_tabla,
    gridOptions=gb.build(),
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=False,
    height=400,
    theme="alpine",
)

# -------------------------------------------------------
# SECTION: Panel de perfil
# -------------------------------------------------------
selected_raw = grid_response.get("selected_rows")
if selected_raw is None:
    selected = []
elif hasattr(selected_raw, "empty"):
    selected = [] if selected_raw.empty else selected_raw.to_dict("records")
else:
    selected = list(selected_raw) if selected_raw else []

if selected:
    fila       = selected[0]
    nombre_sel = fila.get("nombre_completo", "")
    datos_rows = df_full[df_full["nombre_completo"] == nombre_sel]

    if datos_rows.empty:
        st.info("No se encontraron datos completos para este candidato.")
    else:
        datos = datos_rows.iloc[0]

        st.markdown(
            f'<div style="border-top:2px solid {COLOR_BORDER}; margin:24px 0 20px 0;"></div>',
            unsafe_allow_html=True,
        )

        nivel_riesgo = datos.get("nivel_riesgo", "none")
        color_riesgo = {
            "alto": COLOR_RIESGO_ALTO, "medio": COLOR_RIESGO_MEDIO,
            "bajo": COLOR_RIESGO_BAJO, "none": COLOR_RIESGO_NONE,
        }.get(nivel_riesgo, COLOR_RIESGO_NONE)
        bg_riesgo = {
            "alto": COLOR_RIESGO_ALTO_BG, "medio": COLOR_RIESGO_MEDIO_BG,
            "bajo": COLOR_RIESGO_BAJO_BG, "none": COLOR_RIESGO_NONE_BG,
        }.get(nivel_riesgo, COLOR_RIESGO_NONE_BG)

        score     = datos.get("score_total", None)
        score_txt = f"{int(score)}" if pd.notna(score) else "—"
        etiqueta_r = datos.get("etiqueta_riesgo", "Sin dato")

        # Nombre como protagonista
        st.markdown(
            f"""
            <div style="margin-bottom:20px;">
                <div style="font-size:0.63rem; font-weight:700; letter-spacing:0.12em;
                            text-transform:uppercase; color:{COLOR_ACCENT}; margin-bottom:6px;">
                    Perfil del candidato
                </div>
                <h2 style="font-size:1.45rem; font-weight:700; color:{COLOR_TEXT_PRIMARY};
                           margin:0 0 4px 0; letter-spacing:-0.02em; line-height:1.2;">
                    {datos["nombre_completo"]}
                </h2>
                <p style="font-size:0.85rem; color:{COLOR_TEXT_SECONDARY}; margin:0;">
                    {datos.get("partido","—")} · {datos.get("cargo","—")} · {datos.get("region","—")}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_datos, col_score, col_flags = st.columns([3, 2, 2], gap="medium")

        # --- Ficha de identidad ---
        with col_datos:
            filas_html = ""
            campos = [
                ("DNI",           datos.get("dni","—")),
                ("Partido",       datos.get("partido","—")),
                ("Cargo",         datos.get("cargo","—")),
                ("Tipo elección", datos.get("tipo_eleccion","—")),
                ("Posición",      datos.get("posicion","—")),
                ("Región",        datos.get("region","—")),
                ("Estado JNE",    datos.get("estado_jne","—")),
                ("Expediente",    datos.get("expediente","—")),
                ("Nacimiento",    datos.get("fecha_nac","—")),
                ("Sexo",          datos.get("sexo","—")),
            ]
            for label, valor in campos:
                filas_html += (
                    f'<tr><td style="color:{COLOR_TEXT_MUTED}; padding-right:14px; ' +
                    f'white-space:nowrap; font-weight:500; padding-bottom:2px;">{label}</td>' +
                    f'<td style="color:{COLOR_TEXT_PRIMARY}; padding-bottom:2px;">{valor}</td></tr>'
                )
            st.markdown(
                f"""
                <div style="background:{COLOR_SURFACE}; border:1px solid {COLOR_BORDER};
                            border-radius:8px; padding:20px 22px;">
                    <div style="font-size:0.60rem; font-weight:700; letter-spacing:0.10em;
                                text-transform:uppercase; color:{COLOR_TEXT_MUTED};
                                margin-bottom:14px;">
                        Datos de inscripción
                    </div>
                    <table style="width:100%; border-collapse:collapse;
                                  font-size:0.84rem; line-height:1.85;">
                        {filas_html}
                    </table>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # --- Score de riesgo ---
        with col_score:
            def _safe_int(val):
                """Convierte a int de forma segura: NaN y None → 0."""
                return int(val) if pd.notna(val) and val is not None else 0

            s_procrimen = _safe_int(datos.get("score_procrimen"))
            s_contexto  = _safe_int(datos.get("score_contexto"))
            s_bonus     = _safe_int(datos.get("bonus_autoria"))

            st.markdown(
                f"""
                <div style="background:{bg_riesgo}; border:1px solid {color_riesgo}44;
                            border-top:3px solid {color_riesgo};
                            border-radius:0 0 8px 8px; padding:20px 22px 18px 22px;">
                    <div style="font-size:0.60rem; font-weight:700; letter-spacing:0.10em;
                                text-transform:uppercase; color:{COLOR_TEXT_MUTED};
                                margin-bottom:10px;">
                        Score de riesgo
                    </div>
                    <div style="font-size:3.5rem; font-weight:700; color:{color_riesgo};
                                font-variant-numeric:tabular-nums; letter-spacing:-0.03em;
                                line-height:1; margin-bottom:8px;">
                        {score_txt}
                    </div>
                    <div style="display:inline-block; background:{color_riesgo};
                                color:white; font-size:0.67rem; font-weight:700;
                                letter-spacing:0.08em; text-transform:uppercase;
                                padding:3px 10px; border-radius:3px; margin-bottom:16px;">
                        Riesgo {etiqueta_r}
                    </div>
                    <div style="border-top:1px solid {color_riesgo}33; padding-top:14px;
                                display:flex; gap:0; justify-content:space-between;">
                        <div style="text-align:center; flex:1;">
                            <div style="font-size:1.3rem; font-weight:700;
                                        color:{color_riesgo}; font-variant-numeric:tabular-nums;">
                                {s_procrimen}
                            </div>
                            <div style="font-size:0.58rem; font-weight:600;
                                        letter-spacing:0.06em; text-transform:uppercase;
                                        color:{COLOR_TEXT_MUTED}; margin-top:2px;">
                                Pro-crimen
                            </div>
                        </div>
                        <div style="text-align:center; flex:1; border-left:1px solid {color_riesgo}22;">
                            <div style="font-size:1.3rem; font-weight:700;
                                        color:{color_riesgo}; font-variant-numeric:tabular-nums;">
                                {s_contexto}
                            </div>
                            <div style="font-size:0.58rem; font-weight:600;
                                        letter-spacing:0.06em; text-transform:uppercase;
                                        color:{COLOR_TEXT_MUTED}; margin-top:2px;">
                                Contexto
                            </div>
                        </div>
                        <div style="text-align:center; flex:1; border-left:1px solid {color_riesgo}22;">
                            <div style="font-size:1.3rem; font-weight:700;
                                        color:{color_riesgo}; font-variant-numeric:tabular-nums;">
                                {s_bonus}
                            </div>
                            <div style="font-size:0.58rem; font-weight:600;
                                        letter-spacing:0.06em; text-transform:uppercase;
                                        color:{COLOR_TEXT_MUTED}; margin-top:2px;">
                                Bonus
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # --- Para tener en cuenta ---
        with col_flags:
            st.markdown(
                f"""
                <div style="background:{COLOR_SURFACE}; border:1px solid {COLOR_BORDER};
                            border-radius:8px; padding:20px 22px; height:100%;">
                    <div style="font-size:0.60rem; font-weight:700; letter-spacing:0.10em;
                                text-transform:uppercase; color:{COLOR_TEXT_MUTED};
                                margin-bottom:14px;">
                        Para tener en cuenta
                    </div>
                """,
                unsafe_allow_html=True,
            )

            flags_activos = []

            if datos.get("es_congresista") == "SI":
                flags_activos.append((
                    "Congresista en ejercicio",
                    "Postula mientras ejerce el cargo",
                    COLOR_PRIMARY, "#EBF2FA",
                ))

            if datos.get("es_presidencial"):
                flags_activos.append((
                    "Candidato presidencial",
                    "Postula a la Presidencia de la República",
                    "#6B4FA0", "#F3EFF9",
                ))

            if datos.get("tiene_reinfo"):
                reinfo_full = cargar_reinfo()
                dni_norm = str(datos["dni"]).zfill(8)
                row_r = reinfo_full[reinfo_full["dni"] == dni_norm]
                dptos_txt = row_r["dptos_mineros"].values[0] if not row_r.empty else "—"
                n_der = row_r["n_derechos_mineros"].values[0] if not row_r.empty else "—"
                flags_activos.append((
                    "Vínculo REINFO",
                    f"{n_der} derecho(s) minero(s) · {dptos_txt}",
                    COLOR_REINFO, COLOR_REINFO_BG,
                ))

            if datos.get("nivel_riesgo") == "alto":
                leyes_aut = datos.get("leyes_autoria","")
                nota_aut = f" · Autoría: {leyes_aut}" if pd.notna(leyes_aut) and leyes_aut else ""
                flags_activos.append((
                    "Score de riesgo alto",
                    f"Score {score_txt} — por encima del umbral de alerta{nota_aut}",
                    COLOR_RIESGO_ALTO, COLOR_RIESGO_ALTO_BG,
                ))

            if not flags_activos:
                st.markdown(
                    f'<p style="font-size:0.82rem; color:{COLOR_TEXT_MUTED}; ' +
                    f'font-style:italic;">Sin alertas registradas para este candidato.</p>',
                    unsafe_allow_html=True,
                )
            else:
                for titulo, desc, color, bg in flags_activos:
                    st.markdown(
                        f"""
                        <div style="background:{bg}; border-left:3px solid {color};
                                    border-radius:0 6px 6px 0;
                                    padding:10px 14px; margin-bottom:8px;">
                            <div style="font-size:0.72rem; font-weight:700;
                                        letter-spacing:0.05em; text-transform:uppercase;
                                        color:{color}; margin-bottom:2px;">
                                {titulo}
                            </div>
                            <div style="font-size:0.78rem; color:{COLOR_TEXT_SECONDARY};
                                        line-height:1.4;">
                                {desc}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # --- Link hoja de vida JNE ---
            url_jne = datos.get("url_jne", None)
            if pd.notna(url_jne) and str(url_jne).startswith("http"):
                st.markdown(
                    f"""
                    <div style="margin-top:12px; padding-top:12px;
                                border-top:1px solid {COLOR_BORDER};">
                        <a href="{url_jne}" target="_blank"
                           style="display:inline-flex; align-items:center; gap:6px;
                                  font-size:0.78rem; font-weight:600;
                                  color:{COLOR_PRIMARY}; text-decoration:none;">
                            <span style="font-size:0.9em;">\U0001f517</span>
                            Ver hoja de vida en JNE
                        </a>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)

        # -------------------------------------------------------
        # SUBSECTION: Tabla de votaciones (solo congresistas)
        # -------------------------------------------------------
        dni_norm  = str(datos["dni"]).zfill(8)
        voto_row  = votos_full[votos_full["dni"] == dni_norm]

        if not voto_row.empty:
            st.markdown(
                f'<div style="border-top:1px solid {COLOR_BORDER}; margin:24px 0 16px 0;"></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div style="font-size:0.75rem; font-weight:700; letter-spacing:0.08em;
                            text-transform:uppercase; color:{COLOR_TEXT_MUTED};
                            margin-bottom:4px;">
                    Historial parlamentario
                </div>
                <div class="section-header" style="margin-bottom:4px;">
                    Votaciones en leyes clave
                </div>
                <div class="section-subheader">
                    16 leyes monitoreadas · bloque temático y fecha
                </div>
                """,
                unsafe_allow_html=True,
            )

            voto_data  = voto_row.iloc[0]
            filas_voto = []
            for col in LEYES_COLS:
                if col not in voto_data.index:
                    continue
                voto_val = str(voto_data[col]) if pd.notna(voto_data[col]) else "SIN DATO"
                match_ley = leyes_df[leyes_df["etiqueta"] == col]
                bloque    = match_ley["bloque"].values[0]    if len(match_ley) > 0 else "—"
                fecha     = match_ley["fecha"].values[0]     if len(match_ley) > 0 else "—"
                nombre_ley = col.split(" ", 1)[1] if " " in col else col
                clave_ley  = col.split(" ")[0]
                filas_voto.append({
                    "Clave":  clave_ley,
                    "Ley":    nombre_ley,
                    "Bloque": bloque,
                    "Voto":   voto_val,
                    "Fecha":  fecha,
                })

            df_votos_perfil = pd.DataFrame(filas_voto)

            def highlight_voto(val):
                bg   = COLOR_VOTO.get(str(val).upper(), "#F4F6F8")
                text = COLOR_VOTO_TEXT.get(str(val).upper(), COLOR_TEXT_SECONDARY)
                return f"background-color:{bg}; color:{text}; font-weight:600;"

            st.dataframe(
                df_votos_perfil.style.applymap(highlight_voto, subset=["Voto"]),
                hide_index=True,
                use_container_width=True,
                height=340,
            )

            # Desglose de score — mini KPIs en fila
            gp = datos.get("grupo_parl", "—")
            st.markdown(
                f"""
                <div style="background:{COLOR_SURFACE}; border:1px solid {COLOR_BORDER};
                            border-radius:8px; padding:14px 20px; margin-top:8px;
                            display:flex; gap:24px; align-items:center; flex-wrap:wrap;">
                    <div>
                        <div style="font-size:0.58rem; font-weight:700; letter-spacing:0.08em;
                                    text-transform:uppercase; color:{COLOR_TEXT_MUTED};">
                            Grupo parlamentario
                        </div>
                        <div style="font-size:0.88rem; font-weight:600; color:{COLOR_TEXT_PRIMARY};
                                    margin-top:2px;">
                            {gp}
                        </div>
                    </div>
                    <div style="border-left:1px solid {COLOR_BORDER}; padding-left:24px;">
                        <div style="font-size:0.58rem; font-weight:700; letter-spacing:0.08em;
                                    text-transform:uppercase; color:{COLOR_TEXT_MUTED};">
                            Score pro-crimen
                        </div>
                        <div style="font-size:0.88rem; font-weight:600;
                                    color:{COLOR_RIESGO_ALTO}; margin-top:2px;
                                    font-variant-numeric:tabular-nums;">
                            {int(voto_data.get("score_procrimen", 0) or 0)}
                        </div>
                    </div>
                    <div style="border-left:1px solid {COLOR_BORDER}; padding-left:24px;">
                        <div style="font-size:0.58rem; font-weight:700; letter-spacing:0.08em;
                                    text-transform:uppercase; color:{COLOR_TEXT_MUTED};">
                            Score contexto
                        </div>
                        <div style="font-size:0.88rem; font-weight:600;
                                    color:{COLOR_TEXT_PRIMARY}; margin-top:2px;
                                    font-variant-numeric:tabular-nums;">
                            {int(voto_data.get("score_contexto", 0) or 0)}
                        </div>
                    </div>
                    <div style="border-left:1px solid {COLOR_BORDER}; padding-left:24px;">
                        <div style="font-size:0.58rem; font-weight:700; letter-spacing:0.08em;
                                    text-transform:uppercase; color:{COLOR_TEXT_MUTED};">
                            Bonus autoría
                        </div>
                        <div style="font-size:0.88rem; font-weight:600;
                                    color:{COLOR_REINFO}; margin-top:2px;
                                    font-variant-numeric:tabular-nums;">
                            {int(voto_data.get("bonus_autoria", 0) or 0)}
                        </div>
                    </div>
                    <div style="border-left:1px solid {COLOR_BORDER}; padding-left:24px;">
                        <div style="font-size:0.58rem; font-weight:700; letter-spacing:0.08em;
                                    text-transform:uppercase; color:{COLOR_TEXT_MUTED};">
                            Score total
                        </div>
                        <div style="font-size:0.88rem; font-weight:700;
                                    color:{color_riesgo}; margin-top:2px;
                                    font-variant-numeric:tabular-nums;">
                            {int(voto_data.get("score_total", 0) or 0)}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# -------------------------------------------------------
# SECTION: Footer
# -------------------------------------------------------
st.markdown(
    f"""
    <div class="page-footer">
        <span>{APP_CONFIDENTIAL_LABEL} · {APP_VERSION}</span>
        <span>Fuentes: JNE · REINFO · Congreso del Perú</span>
    </div>
    """,
    unsafe_allow_html=True,
)
