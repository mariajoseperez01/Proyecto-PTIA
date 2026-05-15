"""Rellenar carátulas con la API de TMDB (rutas guardadas en tmdb_poster_cache; imágenes en image.tmdb.org).

La tabla de caché persiste aunque se vuelvan a importar los CSV desde la app.

Uso (PowerShell):
  $env:TMDB_API_KEY="tu_clave_v3"
  python -m backend.poster_enrichment

Registro de clave: https://www.themoviedb.org/settings/api
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import time
from pathlib import Path

import requests

from backend.database import DB_PATH, ensure_schema

_PROJECT_ROOT = Path(__file__).resolve().parents[1]

try:
    from dotenv import load_dotenv
except ImportError:
    if (_PROJECT_ROOT / ".env").is_file():
        raise SystemExit(
            "Existe .env en la raíz del proyecto pero falta el paquete python-dotenv.\n"
            "Ejecuta: pip install -r requirements.txt\n"
            "(o activa el mismo entorno virtual que usas para Streamlit)."
        ) from None
else:
    load_dotenv(_PROJECT_ROOT / ".env")

TMDB_MOVIE_URL = "https://api.themoviedb.org/3/movie/{movie_id}"


def _get_api_key() -> str:
    key = (os.environ.get("TMDB_API_KEY") or "").strip()
    if not key:
        raise SystemExit(
            "Define TMDB_API_KEY (variable de entorno o archivo .env en la raíz del proyecto).\n"
            "Ejemplo .env: TMDB_API_KEY=tu_clave\n"
            "https://www.themoviedb.org/settings/api"
        )
    return key


def fetch_poster_path(movie_id: int, api_key: str, session: requests.Session) -> str | None:
    try:
        r = session.get(
            TMDB_MOVIE_URL.format(movie_id=movie_id),
            params={"api_key": api_key},
            timeout=15,
        )
        if r.status_code == 404:
            return None
        r.raise_for_status()
        data = r.json()
        pp = data.get("poster_path")
        if pp and isinstance(pp, str) and pp.strip():
            return pp.strip()
    except (requests.RequestException, ValueError, KeyError):
        return None
    return None


def enrich_posters(
    db_path: Path | None = None,
    *,
    api_key: str | None = None,
    delay_s: float = 0.27,
    limit: int | None = None,
    verbose: bool = True,
) -> tuple[int, int]:
    """Inserta en tmdb_poster_cache los poster_path faltantes. Devuelve (guardados, sin_póster)."""
    path = db_path or DB_PATH
    if not path.is_file():
        raise FileNotFoundError(f"No existe la base de datos: {path}")

    api_key = api_key or _get_api_key()
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})

    with sqlite3.connect(path) as conn:
        ensure_schema(conn)
        cur = conn.execute(
            """
            SELECT m.id FROM movies m
            LEFT JOIN tmdb_poster_cache pc ON m.id = pc.movie_id
            WHERE pc.movie_id IS NULL
            ORDER BY m.id
            """
        )
        ids = [row[0] for row in cur.fetchall()]

    if limit is not None:
        ids = ids[:limit]

    updated = 0
    missing = 0
    total = len(ids)

    for i, mid in enumerate(ids, start=1):
        pp = fetch_poster_path(int(mid), api_key, session)
        time.sleep(delay_s)
        if pp:
            with sqlite3.connect(path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO tmdb_poster_cache (movie_id, poster_path, updated_at)
                    VALUES (?, ?, datetime('now'))
                    """,
                    (mid, pp),
                )
                conn.commit()
            updated += 1
            if verbose and updated % 50 == 0:
                print(f"  … {i}/{total} consultadas, {updated} carátulas guardadas")
        else:
            missing += 1

    if verbose:
        print(f"Listo: {updated} nuevas carátulas en caché, {missing} sin póster en TMDB, {total} procesadas.")

    return updated, missing


def main() -> None:
    parser = argparse.ArgumentParser(description="Rellenar tmdb_poster_cache vía API TMDB.")
    parser.add_argument("--delay", type=float, default=0.27, help="Pausa entre peticiones (s). ~0,25 respeta límites gratuitos.")
    parser.add_argument("--limit", type=int, default=None, help="Solo N películas (prueba).")
    parser.add_argument("--db", type=Path, default=None, help="Ruta al sqlite del proyecto.")
    args = parser.parse_args()
    enrich_posters(args.db, delay_s=args.delay, limit=args.limit, verbose=True)


if __name__ == "__main__":
    main()
