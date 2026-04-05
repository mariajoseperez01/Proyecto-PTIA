from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "tmdb.sqlite3"
MOVIES_PATH = BASE_DIR / "tmdb_5000_movies.csv"
CREDITS_PATH = BASE_DIR / "tmdb_5000_credits.csv"


def initialize_database(force_reload: bool = False) -> None:
    """Create and populate SQLite database from CSV files."""
    if DB_PATH.exists() and not force_reload:
        return

    movies = pd.read_csv(MOVIES_PATH)
    credits = pd.read_csv(CREDITS_PATH)

    with sqlite3.connect(DB_PATH) as conn:
        movies.to_sql("movies", conn, if_exists="replace", index=False)
        credits.to_sql("credits", conn, if_exists="replace", index=False)


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
            m.popularity
        FROM movies m
        INNER JOIN credits c ON m.id = c.movie_id
    """

    with sqlite3.connect(DB_PATH) as conn:
        movies = pd.read_sql_query(query, conn)

    for column in ["overview", "genres", "keywords", "tagline", "cast", "crew", "title"]:
        movies[column] = movies[column].fillna("")

    return movies
