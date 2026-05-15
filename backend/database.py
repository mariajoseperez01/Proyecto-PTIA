from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "tmdb.sqlite3"
MOVIES_PATH = BASE_DIR / "tmdb_5000_movies.csv"
CREDITS_PATH = BASE_DIR / "tmdb_5000_credits.csv"


def ensure_poster_path_column(conn: sqlite3.Connection) -> None:
    """Columna opcional en movies (p. ej. si el CSV trae poster_path)."""
    cur = conn.execute("PRAGMA table_info(movies)")
    cols = {row[1] for row in cur.fetchall()}
    if "poster_path" not in cols:
        conn.execute("ALTER TABLE movies ADD COLUMN poster_path TEXT")
    conn.commit()


def ensure_poster_cache_table(conn: sqlite3.Connection) -> None:
    """Caché persistente de carátulas vía API TMDB (sobrevive a recargar CSV)."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tmdb_poster_cache (
            movie_id INTEGER PRIMARY KEY,
            poster_path TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


def ensure_schema(conn: sqlite3.Connection) -> None:
    ensure_poster_path_column(conn)
    ensure_poster_cache_table(conn)


def initialize_database(force_reload: bool = False) -> None:
    """Create and populate SQLite database from CSV files."""
    if DB_PATH.exists() and not force_reload:
        with sqlite3.connect(DB_PATH) as conn:
            ensure_schema(conn)
        return

    missing = [p for p in (MOVIES_PATH, CREDITS_PATH) if not p.is_file()]
    if missing:
        names = ", ".join(p.name for p in missing)
        raise FileNotFoundError(
            f"No se encontraron los CSV necesarios en {BASE_DIR}: {names}. "
            "Coloca tmdb_5000_movies.csv y tmdb_5000_credits.csv en la raíz del proyecto."
        )

    movies = pd.read_csv(MOVIES_PATH)
    credits = pd.read_csv(CREDITS_PATH)

    with sqlite3.connect(DB_PATH) as conn:
        movies.to_sql("movies", conn, if_exists="replace", index=False)
        credits.to_sql("credits", conn, if_exists="replace", index=False)
        ensure_schema(conn)


def load_enriched_movies() -> pd.DataFrame:
    """Load merged movie metadata used by the recommender."""
    query = """
        SELECT
            m.id AS movie_id,
            m.title,
            m.overview,
            m.genres,
            m.keywords,
            m.tagline,
            c.cast,
            c.crew,
            m.release_date,
            m.vote_average,
            m.popularity,
            COALESCE(
                NULLIF(TRIM(COALESCE(m.poster_path, '')), ''),
                pc.poster_path
            ) AS poster_path
        FROM movies m
        INNER JOIN credits c ON m.id = c.movie_id
        LEFT JOIN tmdb_poster_cache pc ON m.id = pc.movie_id
    """

    with sqlite3.connect(DB_PATH) as conn:
        ensure_schema(conn)
        movies = pd.read_sql_query(query, conn)

    for column in ["overview", "genres", "keywords", "tagline", "cast", "crew", "title"]:
        movies[column] = movies[column].fillna("")
    if "poster_path" in movies.columns:
        movies["poster_path"] = movies["poster_path"].fillna("").astype(str).replace("nan", "")

    return movies
