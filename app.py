from __future__ import annotations

import hashlib
import html
import re

import pandas as pd
import streamlit as st

from backend.database import initialize_database, load_enriched_movies
from backend.recommender import build_model, recommend

TMDB_POSTER_BASE = "https://image.tmdb.org/t/p/w342"

st.set_page_config(
    page_title="CineHall · Recomendaciones",
    page_icon="▶",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data
def load_model() -> tuple[pd.DataFrame, object, list[str]]:
    initialize_database(force_reload=False)
    enriched = load_enriched_movies()
    movies, vectors = build_model(enriched)
    titles = sorted(movies["title"].dropna().astype(str).unique().tolist())
    return movies, vectors, titles


def _strip_html_tags(text: str) -> str:
    s = re.sub(r"<[^>]+>", "", text)
    s = html.unescape(s)
    return " ".join(s.split())


def _poster_gradient(title: str) -> tuple[str, str]:
    palettes = (
        ("#6a040f", "#e85d04"),
        ("#240046", "#7b2cbf"),
        ("#023e8a", "#00b4d8"),
        ("#1b4332", "#52b788"),
        ("#5c1a1b", "#e63946"),
        ("#3d0066", "#c77dff"),
        ("#004643", "#abd1c6"),
        ("#432818", "#bb9457"),
    )
    h = int(hashlib.md5(title.encode()).hexdigest(), 16)
    return palettes[h % len(palettes)]


def _tmdb_poster_url(row: pd.Series) -> str | None:
    if "poster_path" not in row.index:
        return None
    p = row.get("poster_path")
    if p is None or (isinstance(p, float) and pd.isna(p)):
        return None
    p = str(p).strip()
    if not p or p.lower() in ("nan", "none"):
        return None
    if not p.startswith("/"):
        p = "/" + p
    return f"{TMDB_POSTER_BASE}{p}"


def _match_percent(score: float, neutral: bool) -> str:
    if neutral:
        return "—"
    pct = min(100, max(0, round(float(score) * 100)))
    return f"{pct} % parecido"


def _movie_card_inner(row: pd.Series, neutral: bool) -> str:
    overview = row["overview"]
    if pd.isna(overview):
        overview = ""
    overview = _strip_html_tags(str(overview).strip())
    snippet = (overview[:160] + "…") if len(overview) > 160 else overview
    if not snippet:
        snippet = "Sinopsis no disponible."

    tagline = row["tagline"]
    if pd.isna(tagline):
        tagline = ""
    tagline = _strip_html_tags(str(tagline).strip())

    title_plain = str(row["title"])
    title_s = html.escape(title_plain)
    tag_s = html.escape(tagline) if tagline else ""

    release = row["release_date"]
    year = "—"
    if pd.notna(release) and str(release).strip():
        y = str(release).strip()[:4]
        if y.isdigit():
            year = html.escape(y)
    vote = row["vote_average"]
    stars = "—"
    if pd.notna(vote):
        stars = f"★ {float(vote):.1f}"

    match_lbl = _match_percent(float(row["score"]), neutral)
    tag_block = f'<div class="ch-tagline">{tag_s}</div>' if tag_s else ""

    poster_remote = _tmdb_poster_url(row)
    if poster_remote:
        poster_src_esc = html.escape(poster_remote)
        poster = (
            '<div class="ch-poster ch-poster--photo">'
            f'<img src="{poster_src_esc}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer" />'
            '<div class="ch-poster-shade"></div>'
            f'<div class="ch-poster-title">{title_s}</div></div>'
        )
    else:
        c1, c2 = _poster_gradient(title_plain)
        poster = (
            f'<div class="ch-poster" style="background: linear-gradient(145deg, {c1}, {c2});">'
            f'<span class="ch-poster-initial" aria-hidden="true">{html.escape(title_plain[:1])}</span>'
            '<div class="ch-poster-shade"></div>'
            f'<div class="ch-poster-title">{title_s}</div></div>'
        )

    snip_esc = html.escape(snippet)
    return (
        '<div class="ch-card">'
        + poster
        + '<div class="ch-body">'
        + '<div class="ch-meta"><span>'
        + year
        + '</span><span class="ch-dot">·</span><span>'
        + stars
        + '</span></div>'
        + '<div class="ch-match">'
        + html.escape(match_lbl)
        + "</div>"
        + tag_block
        + '<div class="ch-synopsis">'
        + snip_esc
        + "</div></div></div>"
    )


def _fix_row_lengths(df: pd.DataFrame, neutral: bool, n_cols: int) -> str:
    parts: list[str] = []
    i = 0
    while i < len(df):
        chunk = df.iloc[i : i + n_cols]
        cells = "".join(f'<div class="ch-cell">{_movie_card_inner(r, neutral)}</div>' for _, r in chunk.iterrows())
        for _ in range(n_cols - len(chunk)):
            cells += '<div class="ch-cell ch-cell--empty"></div>'
        parts.append(f'<div class="ch-grid-row">{cells}</div>')
        i += n_cols
    return "\n".join(parts)


st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"] {
            font-family: "DM Sans", system-ui, sans-serif;
        }
        .stApp {
            background: #0d0d0d;
            color: #f5f5f5;
        }
        .stApp .block-container {
            max-width: 1320px;
            /* Espacio bajo la cabecera fija de Streamlit (menú >>) para no tapar el logo */
            padding-top: clamp(3.5rem, 10vh, 4.75rem);
            padding-bottom: 3rem;
        }
        .stApp header[data-testid="stHeader"] {
            background: rgba(13, 13, 13, 0.92);
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }
        [data-testid="stSidebar"] {
            background: #141414;
            border-right: 1px solid rgba(255,255,255,0.06);
        }
        .ch-shell { margin: 0; padding: 0; }
        .ch-nav {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.85rem 0 1.25rem;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 1.5rem;
        }
        .ch-brand {
            font-family: "Bebas Neue", sans-serif;
            font-size: 2rem;
            letter-spacing: 0.04em;
            color: #fff;
            line-height: 1;
        }
        .ch-brand span { color: #e50914; }
        .ch-nav-tag {
            font-size: 0.8rem;
            color: #a3a3a3;
            font-weight: 500;
        }
        .ch-hero { margin-bottom: 1.75rem; }
        .ch-hero h1 {
            font-family: "Bebas Neue", sans-serif;
            font-size: clamp(2.4rem, 5vw, 3.75rem);
            letter-spacing: 0.02em;
            line-height: 1;
            margin: 0 0 0.5rem 0;
            color: #fff;
        }
        .ch-hero p {
            margin: 0;
            color: #a3a3a3;
            font-size: 1.05rem;
            max-width: 42rem;
        }
        .ch-section-label {
            font-family: "Bebas Neue", sans-serif;
            font-size: 1.35rem;
            letter-spacing: 0.06em;
            color: #fff;
            margin: 2rem 0 1rem;
        }
        .ch-grid-row {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1.1rem;
            margin-bottom: 1.25rem;
        }
        @media (max-width: 900px) {
            .ch-grid-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
        @media (max-width: 560px) {
            .ch-grid-row { grid-template-columns: 1fr; }
        }
        .ch-cell { min-width: 0; }
        .ch-cell--empty { min-height: 0; }
        .ch-card {
            border-radius: 12px;
            overflow: hidden;
            background: #1a1a1a;
            border: 1px solid rgba(255,255,255,0.06);
            height: 100%;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .ch-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 16px 40px rgba(0,0,0,0.55);
            border-color: rgba(229,9,20,0.35);
        }
        .ch-poster {
            position: relative;
            aspect-ratio: 2 / 3;
            display: flex;
            align-items: flex-end;
            justify-content: center;
        }
        .ch-poster--photo img {
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .ch-poster-initial {
            position: absolute;
            inset: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: "Bebas Neue", sans-serif;
            font-size: 4.5rem;
            color: rgba(255,255,255,0.25);
            user-select: none;
        }
        .ch-poster-shade {
            position: absolute;
            inset: 0;
            background: linear-gradient(180deg, transparent 40%, rgba(0,0,0,0.92) 100%);
            pointer-events: none;
        }
        .ch-poster-title {
            position: relative;
            z-index: 1;
            padding: 0.65rem 0.75rem;
            font-weight: 600;
            font-size: 0.95rem;
            line-height: 1.25;
            text-align: center;
            color: #fff;
        }
        .ch-body {
            padding: 0.85rem 1rem 1.1rem;
        }
        .ch-meta {
            font-size: 0.78rem;
            color: #737373;
            margin-bottom: 0.35rem;
        }
        .ch-dot { margin: 0 0.35rem; opacity: 0.5; }
        .ch-match {
            font-size: 0.75rem;
            font-weight: 600;
            color: #e50914;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.5rem;
        }
        .ch-tagline {
            font-size: 0.82rem;
            font-style: italic;
            color: #d4d4d4;
            margin: 0 0 0.45rem;
            line-height: 1.35;
        }
        .ch-synopsis {
            font-size: 0.8rem;
            color: #a3a3a3;
            line-height: 1.45;
        }
        div.stButton > button[kind="primary"] {
            background: #e50914 !important;
            border: none !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
        }
        div.stButton > button[kind="primary"]:hover {
            background: #f40612 !important;
        }
        [data-testid="stDeployButton"],
        .stDeployButton,
        .stAppDeployButton {
            display: none !important;
        }
        label[data-testid="stWidgetLabel"] p {
            color: #e5e5e5 !important;
            font-weight: 500;
        }
        .stSlider [data-testid="stWidgetLabel"] + div {
            color: #fafafa;
        }
        div[data-testid="stCaption"] {
            color: #a3a3a3 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.caption("Ajustes")
    if st.button("Sincronizar catálogo local", use_container_width=True):
        initialize_database(force_reload=True)
        load_model.clear()
        st.success("Listo.")
        st.rerun()

try:
    with st.spinner("Preparando tu catálogo…"):
        movies, item_vectors, title_options = load_model()
except FileNotFoundError:
    st.error("No hay catálogo disponible. Compruebe que los datos del proyecto estén instalados.")
    st.stop()

st.markdown(
    '<div class="ch-shell"><nav class="ch-nav" aria-label="Cabecera"><div class="ch-brand">Cine<span>Hall</span></div>'
    '<div class="ch-nav-tag">Recomendaciones personalizadas</div></nav><header class="ch-hero"><h1>Tu próxima maratón empieza aquí</h1>'
    "<p>Elige una película que te encante y te sugerimos títulos con el mismo espíritu: mismo ritmo, género y vibra.</p></header></div>",
    unsafe_allow_html=True,
)

c1, c2 = st.columns((1, 1.2), gap="medium")
with c1:
    filter_titles = st.text_input("Buscar en el catálogo", "", placeholder="Título…")
with c2:
    needle = filter_titles.strip().lower()
    if needle:
        filtered = [t for t in title_options if needle in t.lower()]
        title_pick_list = filtered[:800] if len(filtered) > 800 else (filtered if filtered else title_options)
        if len(filtered) > 800:
            st.caption("Refine la búsqueda: hay muchas coincidencias.")
    else:
        title_pick_list = title_options

    if not title_pick_list:
        title_pick_list = title_options

    default_idx = 0
    if needle and title_pick_list:
        for i, t in enumerate(title_pick_list):
            if needle in t.lower():
                default_idx = i
                break

    picked = st.selectbox(
        "¿Qué película te gustó?",
        title_pick_list,
        index=min(default_idx, len(title_pick_list) - 1),
    )

r1, r2 = st.columns((1.4, 1), gap="medium")
with r1:
    count = st.slider("Cuántas sugerencias", 3, 15, 6)
with r2:
    st.markdown('<div style="margin-top: 2.1rem;"></div>', unsafe_allow_html=True)
    go = st.button("Ver recomendaciones", type="primary", use_container_width=True)

target = picked.strip()

if "last_target" not in st.session_state:
    st.session_state["last_target"] = target
if "last_top_n" not in st.session_state:
    st.session_state["last_top_n"] = count

if go:
    st.session_state["last_target"] = target
    st.session_state["last_top_n"] = count

use_target = st.session_state["last_target"]
use_top = st.session_state["last_top_n"]

_rec_key = (use_target, use_top, id(item_vectors))
if st.session_state.get("_recommend_cache_key") != _rec_key:
    st.session_state["_recommend_cache_key"] = _rec_key
    st.session_state["_recommend_result"] = recommend(use_target, movies, item_vectors, use_top)

results, recommend_notice = st.session_state["_recommend_result"]
neutral_scores = recommend_notice is not None

st.markdown(
    f'<h2 class="ch-section-label">Porque te gustó «{html.escape(use_target)}»</h2>',
    unsafe_allow_html=True,
)

if recommend_notice:
    st.info(recommend_notice)

st.markdown(
    f'<div class="ch-results-wrap">{_fix_row_lengths(results, neutral_scores, 3)}</div>',
    unsafe_allow_html=True,
)
