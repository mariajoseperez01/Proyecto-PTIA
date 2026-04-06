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
| `backend/recommender.py` | Construcción de etiquetas, `CountVectorizer`, matriz de similitud y recomendación |
| `tests/test_recommender.py` | Pruebas mínimas del recomendador (`unittest`) |
| `Informacion.md` | Documentación / memoria del curso |
| `requirements.txt` | Dependencias de Python |

## Cómo funciona (resumen técnico)

1. **Datos:** se unen `movies` y `credits` por `movie_id` / `id` y se exponen columnas como géneros, palabras clave, reparto, crew, resumen y tagline.  
2. **Características:** por cada película se arma un texto (`tags`) concatenando esos metadatos.  
3. **Vectorización:** `sklearn.feature_extraction.text.CountVectorizer` (hasta 5000 términos, stop words en inglés).  
4. **Similitud:** `sklearn.metrics.pairwise.cosine_similarity` entre vectores.  
5. **Recomendación:** dado un título (exacto o parcial), se toma la fila correspondiente y se ordenan las demás por similitud descendente (excluyendo la propia película). Si hay varias coincidencias, se prioriza la de mayor **popularidad** en TMDB (columna `popularity`).

## Pruebas automáticas

Con los CSV en su sitio:

```bash
python -m unittest discover -s tests -v
```
