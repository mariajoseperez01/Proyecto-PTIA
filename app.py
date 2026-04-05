from __future__ import annotations

import pandas as pd
import streamlit as st

from backend.database import DB_PATH, initialize_database, load_enriched_movies
from backend.recommender import build_model, recommend


st.set_page_config(page_title="Recomendador TMDB", page_icon="🎬", layout="wide")


@st.cache_data
def load_model() -> tuple[pd.DataFrame, pd.DataFrame]:
    initialize_database(force_reload=False)
    enriched = load_enriched_movies()
    movies, similarity = build_model(enriched)
    return movies, similarity


def render_card(row: pd.Series) -> None:
    st.markdown(
        f"""
        <div style="
            padding: 16px;
            border-radius: 18px;
            background: #f7fafc;
            border: 1px solid #d8e2eb;
            margin-bottom: 14px;
        ">
            <h4 style="margin:0 0 6px 0; color:#102a43;">{row['title']}</h4>
            <div style="color:#334e68; font-size:0.92rem; margin-bottom:8px;">
                Similitud: {row['score']}
            </div>
            <div style="color:#243b53; font-size:0.94rem; line-height:1.6;">
                <strong>{row['tagline'] or 'Sin tagline disponible.'}</strong><br/>
                {row['overview'][:320] + ('...' if len(row['overview']) > 320 else '')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


movies, similarity = load_model()

st.markdown(
    """
    <style>
        .stApp .block-container {
            max-width: 1200px;
        }

        .layer-box {
            padding: 12px 14px;
            border: 1px solid #d9e2ec;
            border-radius: 10px;
            background: #f8fbff;
            margin-bottom: 8px;
        }

        .layer-title {
            margin: 0;
            font-weight: 700;
            color: #102a43;
        }

        .layer-text {
            margin: 3px 0 0;
            color: #334e68;
            font-size: 0.92rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Sistema de Recomendación de Cine")
st.caption("Versión preliminar en Python conectada a base de datos SQLite y motor de similitud por contenido.")

st.markdown(
    f"""
    <div class="layer-box">
        <p class="layer-title">Arquitectura implementada (como en el documento)</p>
        <p class="layer-text">Capa de Datos: SQLite en <strong>{DB_PATH.name}</strong> | Capa de Lógica: vectorización + similitud del coseno | Capa de Presentación: Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Controles")
    selected_movie = st.selectbox("Selecciona una película base", sorted(movies["title"].dropna().unique().tolist()))
    top_n = st.slider("Número de recomendaciones", 3, 10, 5)
    query_text = st.text_input("O escribe parte del título", "")
    st.markdown("---")
    st.markdown("Esta interfaz usa TMDB 5000, crea una BD local y ejecuta recomendaciones sobre datos reales.")
    if st.button("Recargar base de datos desde CSV", use_container_width=True):
        initialize_database(force_reload=True)
        st.cache_data.clear()
        st.success("Base de datos recargada desde los CSV.")

col1, col2 = st.columns([1.05, 1.4], gap="large")

with col1:
    st.subheader("Backend implementado")
    st.write("La app está separada por capas para que quede claro el backend y la conexión con base de datos.")
    st.info("Base de datos: backend/database.py | Motor de recomendación: backend/recommender.py")

    if st.button("Generar recomendaciones", use_container_width=True):
        target = query_text.strip() if query_text.strip() else selected_movie
        st.session_state["results"] = recommend(target, movies, similarity, top_n)

    st.markdown(
        """
        **Estado del prototipo**
        - Interfaz navegable para validar UX
        - Conectado a base de datos local
        - Motor de similitud implementado
        - Base para mejoras futuras
        """
    )

    st.markdown("**Código del backend**")
    with st.expander("Ver implementación de base de datos"):
        st.code(
            """
# backend/database.py
initialize_database(force_reload=False)
load_enriched_movies()
            """.strip(),
            language="python",
        )

    with st.expander("Ver implementación del motor"):
        st.code(
            """
# backend/recommender.py
build_model(movies)
recommend(movie_title, movies, similarity, top_n)
            """.strip(),
            language="python",
        )

with col2:
    st.subheader("Resultados")
    results = st.session_state.get("results")
    if results is None:
        initial_target = query_text.strip() if query_text.strip() else selected_movie
        results = recommend(initial_target, movies, similarity, top_n)
        st.session_state["results"] = results

    for _, row in results.iterrows():
        render_card(row)
