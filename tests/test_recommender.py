"""Pruebas mínimas del recomendador (requieren CSV en la raíz del proyecto)."""

from __future__ import annotations

import unittest

from backend.database import initialize_database, load_enriched_movies
from backend.recommender import build_model, recommend


class TestRecommend(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        initialize_database(force_reload=False)
        enriched = load_enriched_movies()
        cls.movies, cls.similarity = build_model(enriched)

    def test_no_match_returns_notice(self) -> None:
        df, notice = recommend("___titulo_inexistente_xyz___", self.movies, self.similarity, top_n=3)
        self.assertIsNotNone(notice)
        self.assertIn("No se encontró", notice)
        self.assertEqual(len(df), 3)
        self.assertTrue((df["score"] == 1.0).all())

    def test_match_returns_no_notice(self) -> None:
        df, notice = recommend("Avatar", self.movies, self.similarity, top_n=3)
        self.assertIsNone(notice)
        self.assertEqual(len(df), 3)
        self.assertTrue((df["score"] != 1.0).any() or len(df) == 0)


if __name__ == "__main__":
    unittest.main()
