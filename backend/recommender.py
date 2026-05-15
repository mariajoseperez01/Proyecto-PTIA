from __future__ import annotations

import ast

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _safe_parse(value: object) -> list[dict]:
    if value is None:
        return []
    s = str(value).strip()
    if not s or s.lower() == "nan":
        return []
    try:
        parsed = ast.literal_eval(s)
        return parsed if isinstance(parsed, list) else []
    except (ValueError, SyntaxError, TypeError):
        return []


def _extract_names(items: list[dict], key: str = "name", limit: int | None = None) -> list[str]:
    names: list[str] = []
    for item in items:
        if isinstance(item, dict) and key in item:
            token = str(item[key]).strip().lower()
            if token:
                names.append(token)
        if limit is not None and len(names) >= limit:
            break
    return names


def _build_tags(row: pd.Series) -> str:
    genres = _extract_names(_safe_parse(row["genres"]))
    keywords = _extract_names(_safe_parse(row["keywords"]))
    cast = _extract_names(_safe_parse(row["cast"]), limit=5)

    director = ""
    for item in _safe_parse(row["crew"]):
        if isinstance(item, dict) and item.get("job") == "Director":
            director = str(item.get("name", "")).strip().lower()
            break

    overview = str(row.get("overview", "") or "").strip().lower()
    tagline = str(row.get("tagline", "") or "").strip().lower()

    parts = genres + keywords + cast + ([director] if director else []) + [overview, tagline]
    return " ".join(p for p in parts if p)


def build_model(movies: pd.DataFrame) -> tuple[pd.DataFrame, csr_matrix]:
    """Devuelve (tabla preparada, matriz TF-IDF dispersa filas=películas)."""
    prepared = movies.copy().reset_index(drop=True)
    prepared["tags"] = prepared.apply(_build_tags, axis=1)

    vectorizer = TfidfVectorizer(
        max_features=8000,
        stop_words="english",
        min_df=2,
        max_df=0.9,
        ngram_range=(1, 2),
        sublinear_tf=True,
        dtype=np.float64,
    )
    tfidf_matrix = vectorizer.fit_transform(prepared["tags"])
    return prepared, tfidf_matrix.tocsr()


def _row_pos(movies: pd.DataFrame, index: int) -> int:
    loc = movies.index.get_loc(index)
    if isinstance(loc, slice):
        start = loc.start
        return int(start if start is not None else 0)
    return int(loc)


def _output_columns(movies: pd.DataFrame) -> list[str]:
    cols: list[str] = []
    if "movie_id" in movies.columns:
        cols.append("movie_id")
    if "poster_path" in movies.columns:
        cols.append("poster_path")
    cols.extend(["title", "tagline", "overview", "vote_average", "release_date"])
    return cols


def _fallback_frame(movies: pd.DataFrame, top_n: int) -> pd.DataFrame:
    c = _output_columns(movies)
    return movies.head(top_n)[c].assign(score=1.0)


def recommend(
    movie_title: str,
    movies: pd.DataFrame,
    item_vectors: csr_matrix,
    top_n: int = 5,
) -> tuple[pd.DataFrame, str | None]:
    """Devuelve (resultados, aviso_usuario). `item_vectors` debe alinearse fila a fila con `movies`."""
    query = movie_title.strip().lower()
    if not query:
        return (
            _fallback_frame(movies, top_n),
            "Indique una película de referencia para ordenar por afinidad. Se muestra un listado general del catálogo.",
        )

    titles_lower = movies["title"].str.lower()
    exact = movies[titles_lower == query]
    if not exact.empty:
        if len(exact) > 1 and "popularity" in movies.columns:
            exact = exact.sort_values("popularity", ascending=False, na_position="last")
        row_index = exact.index[0]
    else:
        partial = movies[titles_lower.str.contains(query, na=False, regex=False)]
        if partial.empty:
            return (
                _fallback_frame(movies, top_n),
                "No se encontró la película indicada. Se muestran sugerencias generales del catálogo.",
            )
        if "popularity" in movies.columns:
            partial = partial.sort_values("popularity", ascending=False, na_position="last")
        row_index = partial.index[0]

    row_pos = _row_pos(movies, row_index)

    if row_pos < 0 or row_pos >= item_vectors.shape[0]:
        return (
            _fallback_frame(movies, top_n),
            "No se pudieron calcular recomendaciones. Pruebe con otra película o actualice el catálogo.",
        )

    sim_row = cosine_similarity(item_vectors[row_pos], item_vectors).ravel()
    ranked = sorted(
        ((idx, float(score)) for idx, score in enumerate(sim_row) if idx != row_pos),
        key=lambda x: x[1],
        reverse=True,
    )[:top_n]

    if not ranked:
        return (
            _fallback_frame(movies, top_n),
            "No se pudieron calcular recomendaciones. Pruebe con otra película o actualice el catálogo.",
        )

    indexes = [idx for idx, _ in ranked]
    result = movies.iloc[indexes][_output_columns(movies)].copy()
    result["score"] = [round(score, 3) for _, score in ranked]
    return result.reset_index(drop=True), None
