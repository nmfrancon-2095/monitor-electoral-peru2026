# ============================================================
# app.py — Monitor Electoral Perú 2026
# Punto de entrada: autenticación, CSS global, sidebar, home.
# Cómo correr: python -m streamlit run app.py
# ============================================================

import streamlit as st
from config import (
    APP_TITLE, APP_SUBTITLE, APP_ICON, APP_LOGO,
    APP_CONFIDENTIAL_LABEL, APP_VERSION,
    COLOR_PRIMARY, COLOR_BACKGROUND, COLOR_SURFACE,
    COLOR_BORDER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_ACCENT, GLOBAL_CSS
)

# -------------------------------------------------------
# SECTION: Page config — debe ser la primera llamada Streamlit
# -------------------------------------------------------
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------
# SECTION: CSS global (del nuevo config.py)
# -------------------------------------------------------
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# -------------------------------------------------------
# SECTION: Autenticación
# Contraseña en .streamlit/secrets.toml → [auth] password = "..."
# -------------------------------------------------------
def check_password() -> bool:
    if st.session_state.get("autenticado", False):
        return True

    st.markdown(
        f"""
        <div style="
            max-width:400px; margin:80px auto; padding:40px 36px;
            background:{COLOR_SURFACE}; border:1px solid {COLOR_BORDER};
            border-radius:10px; text-align:center;
        ">
            <div style="font-size:0.65rem; font-weight:700; letter-spacing:0.12em;
                        text-transform:uppercase; color:{COLOR_ACCENT};
                        margin-bottom:16px;">
                Acceso restringido
            </div>
            <h2 style="color:{COLOR_PRIMARY}; margin:0 0 6px 0;
                       font-size:1.25rem; letter-spacing:-0.01em;">
                {APP_TITLE}
            </h2>
            <p style="color:{COLOR_TEXT_SECONDARY}; font-size:0.83em; margin:0;">
                {APP_SUBTITLE}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        password_input = st.text_input(
            "Contraseña",
            type="password",
            label_visibility="collapsed",
            placeholder="Contraseña de acceso",
        )
        if st.button("Ingresar", use_container_width=True, type="primary"):
            try:
                if password_input == st.secrets["auth"]["password"]:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta.")
            except KeyError:
                st.warning(
                    "⚙️ Configura `[auth] password` en `.streamlit/secrets.toml`."
                )
    return False


if not check_password():
    st.stop()


# -------------------------------------------------------
# SECTION: Sidebar
# -------------------------------------------------------
with st.sidebar:
    if APP_LOGO:
        st.image(APP_LOGO, use_container_width=True)

    # Título y subtítulo
    st.markdown(
        f"""
        <div style="padding:8px 0 6px 0;">
            <div style="font-size:1.05rem; font-weight:700; letter-spacing:-0.01em;
                        color:#FFFFFF; line-height:1.3;">
                {APP_TITLE}
            </div>
            <div style="font-size:0.75rem; color:rgba(255,255,255,0.70);
                        margin-top:4px; line-height:1.4;">
                {APP_SUBTITLE}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="border-top:1px solid rgba(255,255,255,0.15); margin:12px 0;"></div>',
        unsafe_allow_html=True,
    )

    # Badge confidencial — usa la nueva clase del CSS
    st.markdown(
        f'<span class="badge-confidencial">{APP_CONFIDENTIAL_LABEL}</span>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div style="font-size:0.70rem; color:rgba(255,255,255,0.50);
                    margin-top:8px; line-height:1.6;">
            {APP_VERSION} · JNE · REINFO · Congreso del Perú
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="border-top:1px solid rgba(255,255,255,0.15); margin:16px 0 12px 0;"></div>',
        unsafe_allow_html=True,
    )

    if st.button("Cerrar sesión", use_container_width=True):
        st.session_state["autenticado"] = False
        st.rerun()


# -------------------------------------------------------
# SECTION: Home — pantalla de bienvenida
# Se ve cuando el usuario está en app.py sin seleccionar página.
# -------------------------------------------------------

# Encabezado limpio — sin emoji gigante, tipografía con peso
st.markdown(
    f"""
    <div style="padding:48px 0 32px 0; max-width:640px;">
        <div style="font-size:0.65rem; font-weight:700; letter-spacing:0.12em;
                    text-transform:uppercase; color:{COLOR_ACCENT}; margin-bottom:12px;">
            Herramienta de análisis interno · {APP_VERSION}
        </div>
        <h1 style="color:{COLOR_PRIMARY}; font-size:2rem; font-weight:700;
                   margin:0 0 8px 0; letter-spacing:-0.02em; line-height:1.2;">
            {APP_TITLE}
        </h1>
        <p style="color:{COLOR_TEXT_SECONDARY}; font-size:0.95em;
                  margin:0; line-height:1.6;">
            {APP_SUBTITLE}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Separador fino
st.markdown(
    f'<div style="border-top:2px solid {COLOR_BORDER}; margin-bottom:28px;"></div>',
    unsafe_allow_html=True,
)

# Accesos directos — sin emojis grandes, diseño limpio
SECCIONES = [
    {
        "titulo":    "Overview",
        "desc":      "KPIs de cobertura, mapa por región, distribución de riesgo y alerta de congresistas.",
        "pagina":    "overview",
    },
    {
        "titulo":    "Candidatos",
        "desc":      "Explorador de los 9,065 candidatos con perfil individual, flags y expediente JNE.",
        "pagina":    "candidatos",
    },
    {
        "titulo":    "Análisis temático",
        "desc":      "Patrones de votación por bloque y ley, distribución de score, heatmap parlamentario.",
        "pagina":    "analisis tematico",
    },
    {
        "titulo":    "Análisis de Incidentes Electorales",
        "desc":      "Patrones de violencia electoral y protestas, con identificación de presuntas víctimas.",
        "pagina":    "incidentes",
    },
    {
        "titulo":    "Resultados 2026",
        "desc":      "Resultados electorales en tiempo real: presidencial, senado, diputados y parlamento andino.",
        "pagina":    "resultados 2026",
    },
    {
        "titulo":    "Electos — Análisis de riesgo",
        "desc":      "Candidatos electos proyectados cruzados con REINFO, score legislativo y reelección.",
        "pagina":    "electos analisis",
    },
]

cols = st.columns(6, gap="medium")
for col, sec in zip(cols, SECCIONES):
    with col:
        st.markdown(
            f"""
            <div style="
                background:{COLOR_SURFACE};
                border:1px solid {COLOR_BORDER};
                border-radius:8px;
                padding:22px 20px 20px 20px;
                height:100%;
                transition: border-color 150ms ease;
            ">
                <div style="font-size:0.65rem; font-weight:700; letter-spacing:0.08em;
                            text-transform:uppercase; color:{COLOR_ACCENT};
                            margin-bottom:8px;">
                    {sec['pagina']}
                </div>
                <div style="font-size:1rem; font-weight:700; color:{COLOR_TEXT_PRIMARY};
                            margin-bottom:8px; letter-spacing:-0.01em;">
                    {sec['titulo']}
                </div>
                <div style="font-size:0.82em; color:{COLOR_TEXT_SECONDARY};
                            line-height:1.55;">
                    {sec['desc']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Nota de uso
st.markdown(
    f"""
    <p style="color:{COLOR_TEXT_SECONDARY}; font-size:0.80em;
              margin-top:24px; text-align:center;">
        Selecciona una sección en el menú lateral para comenzar.
    </p>
    """,
    unsafe_allow_html=True,
)
