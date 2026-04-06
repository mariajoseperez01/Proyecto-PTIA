from __future__ import annotations

import ast

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
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
            names.append(str(item[key]).replace(" ", ""))
        if limit is not None and len(names) >= limit:
            break
    return names


def _build_tags(row: pd.Series) -> str:
    genres = _extract_names(_safe_parse(row["genres"]))
    keywords = _extract_names(_safe_parse(row["keywords"]))
    cast = _extract_names(_safe_parse(row["cast"]), limit=3)

    director = ""
    for item in _safe_parse(row["crew"]):
        if isinstance(item, dict) and item.get("job") == "Director":
            director = str(item.get("name", "")).replace(" ", "")
            break

    parts = genres + keywords + cast + [director, str(row["overview"]), str(row["tagline"])]
    return " ".join(part for part in parts if part)


def build_model(movies: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    prepared = movies.copy().reset_index(drop=True)
    prepared["tags"] = prepared.apply(_build_tags, axis=1)

    vectorizer = CountVectorizer(max_features=5000, stop_words="english")
    vectors = vectorizer.fit_transform(prepared["tags"]).toarray()
    similarity = cosine_similarity(vectors)

    return prepared, pd.DataFrame(similarity)


def _fallback_frame(movies: pd.DataFrame, top_n: int) -> pd.DataFrame:
    return movies.head(top_n)[["title", "tagline", "overview", "vote_average", "release_date"]].assign(score=1.0)


def recommend(
    movie_title: str,
    movies: pd.DataFrame,
    similarity: pd.DataFrame,
    top_n: int = 5,
) -> tuple[pd.DataFrame, str | None]:
    """Devuelve (resultados, aviso_usuario). El aviso es None si hubo coincidencia y similitud real."""
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
        index = exact.index[0]
    else:
        partial = movies[titles_lower.str.contains(query, na=False, regex=False)]
        if partial.empty:
            return (
                _fallback_frame(movies, top_n),
                "No se encontró la película indicada. Se muestran sugerencias generales del catálogo.",
            )
        if "popularity" in movies.columns:
            partial = partial.sort_values("popularity", ascending=False, na_position="last")
        index = partial.index[0]

    loc = movies.index.get_loc(index)
    if isinstance(loc, slice):
        row_pos = int(loc.start if loc.start is not None else 0)
    else:
        row_pos = int(loc)

    if row_pos >= len(similarity) or row_pos < 0:
        return (
            _fallback_frame(movies, top_n),
            "No se pudieron calcular recomendaciones. Pruebe con otra película o actualice el catálogo.",
        )

    distances = list(enumerate(similarity.iloc[row_pos]))
    ranked = sorted(distances, key=lambda item: item[1], reverse=True)[1 : top_n + 1]
    indexes = [idx for idx, _ in ranked]

    result = movies.iloc[indexes][["title", "tagline", "overview", "vote_average", "release_date"]].copy()
    result["score"] = [round(score, 3) for _, score in ranked]
    return result.reset_index(drop=True), None
