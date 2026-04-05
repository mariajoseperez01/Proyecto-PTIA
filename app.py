from __future__ import annotations

import pandas as pd
import streamlit as st

from backend.database import DB_PATH, initialize_database, load_enriched_movies
from backend.recommender import build_model, recommend


st.set_page_config(page_title="Recomendador TMDB", page_icon="🎬", layout="centered")


@st.cache_data
def load_model() -> tuple[pd.DataFrame, pd.DataFrame]:
    initialize_database(force_reload=False)
    enriched = load_enriched_movies()
    movies, similarity = build_model(enriched)
    return movies, similarity


movies, similarity = load_model()

st.markdown(
    """
    <style>
        .stApp {
            background: #f6f8fb;
            color: #102a43;
        }
        .stApp .block-container {
            max-width: 900px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .panel {
            padding: 18px 20px;
            border: 1px solid #d9e2ec;
            border-radius: 14px;
            background: #ffffff;
            margin-bottom: 16px;
        }
        .muted {
            color: #52606d;
            font-size: 0.95rem;
            line-height: 1.6;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Sistema de Recomendación de Cine")
st.write("Prototipo funcional en Python para recomendar películas por similitud de contenido usando TMDB.")

st.markdown(
    f"""
    <div class="panel">
        <strong>Capa de datos:</strong> SQLite local ({DB_PATH.name}) alimentada desde los CSV de TMDB.<br/>
        <strong>Capa de lógica:</strong> vectorización de metadatos y similitud del coseno.<br/>
        <strong>Capa de presentación:</strong> esta interfaz en Streamlit, pensada solo para validar el flujo principal.
    </div>
    """,
    unsafe_allow_html=True,
)

selected_movie = st.selectbox(
    "Selecciona una película base",
    sorted(movies["title"].dropna().unique().tolist()),
)
top_n = st.slider("Número de recomendaciones", 3, 10, 5)
query_text = st.text_input("O escribe parte del título", "")

col1, col2 = st.columns(2)
with col1:
    run_search = st.button("Generar recomendaciones", use_container_width=True)
with col2:
    reload_db = st.button("Recargar BD desde CSV", use_container_width=True)

if reload_db:
    initialize_database(force_reload=True)
    st.cache_data.clear()
    st.success("Base de datos recargada desde los CSV.")
    st.stop()

target = query_text.strip() if query_text.strip() else selected_movie
if run_search:
    st.session_state["results"] = recommend(target, movies, similarity, top_n)

results = st.session_state.get("results")
if results is None:
    results = recommend(target, movies, similarity, top_n)
    st.session_state["results"] = results

st.subheader("Resultados")
st.dataframe(
    results[["title", "score", "vote_average", "release_date"]],
    use_container_width=True,
    hide_index=True,
)

with st.expander("Ver descripción técnica del backend"):
    st.markdown(
        """
        La aplicación usa dos capas de datos: `tmdb_5000_movies.csv` como fuente principal y `tmdb_5000_credits.csv` como complemento.
        Ambas se cargan a una base SQLite local para centralizar la consulta y luego se unen para construir los metadatos usados por el recomendador.

        El motor de recomendación vive en `backend/recommender.py`, donde se generan vectores a partir de géneros, palabras clave, elenco, director, resumen y tagline.
        Luego se calcula similitud del coseno para devolver títulos cercanos al elegido.
        """
    )
