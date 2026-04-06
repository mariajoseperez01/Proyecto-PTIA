from __future__ import annotations

import html
import pandas as pd
import streamlit as st

from backend.database import initialize_database, load_enriched_movies
from backend.recommender import build_model, recommend


st.set_page_config(
    page_title="Recomendación de películas",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_model() -> tuple[pd.DataFrame, pd.DataFrame]:
    initialize_database(force_reload=False)
    enriched = load_enriched_movies()
    movies, similarity = build_model(enriched)
    return movies, similarity


st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(180deg, #070b16 0%, #0b1020 45%, #060913 100%);
            color: #eef2ff;
        }
        .stApp .block-container {
            max-width: 1200px;
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        .stApp header[data-testid="stHeader"] {
            background: rgba(7, 11, 22, 0.85);
        }
        div[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f1628 0%, #0b1020 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }
        .hero-panel {
            padding: 22px 24px;
            border-radius: 18px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            background: rgba(16, 23, 48, 0.72);
            margin-bottom: 1.25rem;
            box-shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
        }
        .hero-panel h1 {
            margin: 0 0 8px 0;
            font-size: 1.65rem;
            letter-spacing: -0.02em;
            color: #f8fafc;
        }
        .hero-panel .subtitle {
            color: #a8b3d6;
            font-size: 0.98rem;
            line-height: 1.65;
            margin: 0;
        }
        .rec-card {
            padding: 16px 18px;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            background: rgba(255, 255, 255, 0.04);
            margin-bottom: 12px;
        }
        .rec-card h4 {
            margin: 0 0 8px 0;
            color: #f1f5f9;
            font-size: 1.05rem;
        }
        .rec-meta {
            color: #a8b3d6;
            font-size: 0.85rem;
            margin-bottom: 10px;
        }
        .rec-overview {
            color: #dfe6ff;
            font-size: 0.92rem;
            line-height: 1.55;
            margin: 0;
        }
        div[data-testid="stExpander"] {
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.03);
        }
        /* Ocultar el botón «Deploy» de Streamlit (selectores según versión) */
        [data-testid="stDeployButton"],
        .stDeployButton,
        .stAppDeployButton {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Opciones")
    if st.button("Actualizar catálogo", use_container_width=True):
        initialize_database(force_reload=True)
        load_model.clear()
        st.success("Catálogo actualizado.")
        st.rerun()

try:
    movies, similarity = load_model()
except FileNotFoundError:
    st.error("No se encontraron los datos necesarios. Revise la instalación o los permisos de la carpeta del proyecto.")
    st.stop()

st.markdown(
    """
    <div class="hero-panel">
        <h1>Recomendación de películas</h1>
        <p class="subtitle">Elija una película de referencia y obtenga títulos afines según el catálogo disponible.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col_a, col_b = st.columns((1.15, 1), gap="large")

with col_a:
    st.subheader("Búsqueda")
    title_options = sorted(movies["title"].dropna().astype(str).unique().tolist())
    selected_movie = st.selectbox("Película de referencia", title_options, index=0)
    query_text = st.text_input("Texto alternativo (si lo rellena, sustituye a la selección)", "")
    top_n = st.slider("Cantidad de resultados", 3, 15, 5)
    run_search = st.button("Obtener recomendaciones", type="primary", use_container_width=True)

with col_b:
    st.subheader("Instrucciones")
    st.markdown(
        """
        1. Elija una película en la lista **o** escriba parte del título en el campo de texto (si hay texto, se usa en lugar de la lista).  
        2. Indique cuántos resultados desea ver.  
        3. Pulse **Obtener recomendaciones** para actualizar la lista.
        """
    )

target = (query_text.strip() or selected_movie).strip()

if "last_target" not in st.session_state:
    st.session_state["last_target"] = target
if "last_top_n" not in st.session_state:
    st.session_state["last_top_n"] = top_n

if run_search:
    st.session_state["last_target"] = target
    st.session_state["last_top_n"] = top_n

use_target = st.session_state["last_target"]
use_top = st.session_state["last_top_n"]

results, recommend_notice = recommend(use_target, movies, similarity, use_top)

st.divider()
st.subheader("Recomendaciones")
st.caption(f"Referencia actual: **{use_target}** · **{len(results)}** resultados.")
if recommend_notice:
    st.warning(recommend_notice)

for _, row in results.iterrows():
    overview = row["overview"]
    if pd.isna(overview):
        overview = ""
    overview = str(overview).strip()
    snippet = (overview[:280] + "…") if len(overview) > 280 else overview
    tagline = row["tagline"]
    if pd.isna(tagline):
        tagline = ""
    tagline = str(tagline).strip()

    title_safe = html.escape(str(row["title"]))
    tagline_safe = html.escape(tagline)
    snippet_safe = html.escape(snippet or "Sin resumen disponible.")
    release = row["release_date"]
    release_disp = "—" if pd.isna(release) or release == "" else html.escape(str(release))
    vote = row["vote_average"]
    vote_disp = "—" if pd.isna(vote) else f"{float(vote):.1f}"

    tagline_block = (
        f"<p class='rec-overview'><em>{tagline_safe}</em></p>" if tagline_safe else ""
    )
    st.markdown(
        f"""
        <div class="rec-card">
            <h4>{title_safe}</h4>
            <div class="rec-meta">
                Afinidad: <strong>{row["score"]:.3f}</strong>
                &nbsp;·&nbsp; Valoración media: <strong>{vote_disp}</strong>
                &nbsp;·&nbsp; Estreno: <strong>{release_disp}</strong>
            </div>
            {tagline_block}
            <p class="rec-overview">{snippet_safe}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
