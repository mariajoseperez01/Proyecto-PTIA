from __future__ import annotations

import ast

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _safe_parse(value: str) -> list[dict]:
    try:
        parsed = ast.literal_eval(value)
        return parsed if isinstance(parsed, list) else []
    except (ValueError, SyntaxError):
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
    prepared = movies.copy()
    prepared["tags"] = prepared.apply(_build_tags, axis=1)

    vectorizer = CountVectorizer(max_features=5000, stop_words="english")
    vectors = vectorizer.fit_transform(prepared["tags"]).toarray()
    similarity = cosine_similarity(vectors)

    return prepared, pd.DataFrame(similarity)


def recommend(movie_title: str, movies: pd.DataFrame, similarity: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    query = movie_title.strip().lower()
    if not query:
        return movies.head(top_n)[["title", "tagline", "overview", "vote_average", "release_date"]].assign(score=1.0)

    exact = movies[movies["title"].str.lower() == query]
    if exact.empty:
        partial = movies[movies["title"].str.lower().str.contains(query, na=False)]
        if partial.empty:
            return movies.head(top_n)[["title", "tagline", "overview", "vote_average", "release_date"]].assign(score=1.0)
        index = partial.index[0]
    else:
        index = exact.index[0]

    distances = list(enumerate(similarity.iloc[index]))
    ranked = sorted(distances, key=lambda item: item[1], reverse=True)[1 : top_n + 1]
    indexes = [idx for idx, _ in ranked]

    result = movies.iloc[indexes][["title", "tagline", "overview", "vote_average", "release_date"]].copy()
    result["score"] = [round(score, 3) for _, score in ranked]
    return result.reset_index(drop=True)
