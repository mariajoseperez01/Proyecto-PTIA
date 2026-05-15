# Recomendación de películas

Proyecto de recomendación de películas.

## Autores

- María José Pérez Zamora  
- Josué David Hernández Martínez  

## Requisitos

- Python 3.10 o superior (recomendado 3.11+)
- Archivos de datos en la raíz del repositorio:
  - `tmdb_5000_movies.csv`
  - `tmdb_5000_credits.csv`

La primera ejecución genera `tmdb.sqlite3` (SQLite) a partir de esos CSV.

### Carátulas oficiales (TMDB)

El CSV clásico **no trae** rutas de póster. El proyecto guarda las rutas en la tabla **`tmdb_poster_cache`** (solo texto; las imágenes las sirve `https://image.tmdb.org`). Esa caché **no se borra** al pulsar «Sincronizar catálogo» (solo se regeneran `movies` y `credits` desde CSV).

1. Crea una **API Key (v3)** en [TMDB → Ajustes → API](https://www.themoviedb.org/settings/api).
2. En la carpeta del proyecto (con el venv activado):

**PowerShell**

```powershell
$env:TMDB_API_KEY = "pega_aqui_tu_clave"
python -m backend.poster_enrichment
```

**O** crea un archivo **`.env`** en la raíz del proyecto (no lo subas a git):

```env
TMDB_API_KEY=pega_aqui_tu_clave
```

El script carga automáticamente ese archivo si instalaste las dependencias (`python-dotenv`).

**Prueba rápida (solo 30 películas):**

```powershell
python -m backend.poster_enrichment --limit 30
```

La primera carga completa (~4800 id) puede tardar **unos 20–25 minutos** (límite de uso razonable de la API). Las siguientes ejecuciones solo completan títulos nuevos.
3. Reinicia o recarga Streamlit para vaciar la caché del modelo (`load_model`).

## Instalación

Desde la carpeta del proyecto:

```bash
python -m venv .venv
```

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Ejecución de la aplicación

```bash
python -m streamlit run app.py
```

Se abrirá la aplicación en el navegador (por defecto `http://localhost:8501`). En la barra lateral puedes **recargar la base de datos** desde los CSV (vuelve a construir SQLite y vacía la caché del modelo).

La **interfaz de usuario del proyecto** es esta aplicación Streamlit (`app.py`), conectada al dataset y al motor de recomendación.

## Estructura del repositorio

| Ruta | Descripción |
|------|-------------|
| `app.py` | Aplicación Streamlit: consulta, resultados y estilos |
| `backend/database.py` | Carga CSV → SQLite y consulta enriquecida (JOIN películas + créditos) |
| `backend/poster_enrichment.py` | Consulta API TMDB; rellena tabla `tmdb_poster_cache` con rutas de carátula |
| `tests/test_recommender.py` | Pruebas mínimas del recomendador (`unittest`) |
| `Informacion.md` | Documentación / memoria del curso |
| `requirements.txt` | Dependencias de Python |

## Cómo funciona (resumen técnico)

1. **Datos:** se unen `movies` y `credits` por `movie_id` / `id` y se exponen columnas como géneros, palabras clave, reparto, crew, resumen y tagline.  
2. **Características:** por cada película se arma un texto (`tags`) concatenando esos metadatos.  
3. **Vectorización:** `TfidfVectorizer` (hasta 8000 rasgos, *n*-gramas 1–2, TF sublineal, filtrado `min_df` / `max_df`).  
4. **Similitud:** `cosine_similarity` fila contra el catálogo completo en **matriz dispersa** (no se materializa una matriz \(n \times n\) densa).  
5. **Recomendación:** se identifica la película por título exacto o parcial (desempate por popularidad TMDB), se excluye la propia película del ranking y se devuelven las \(k\) mayores afinidades.

## Pruebas automáticas

Con los CSV en su sitio:

```bash
python -m unittest discover -s tests -v
```
