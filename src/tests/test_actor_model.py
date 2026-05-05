"""Unit tests for actor_model module."""

from __future__ import annotations

import unittest

import pandas as pd

from src.models.actor_model import extract_actor_counts


class ActorModelTests(unittest.TestCase):
    def test_extract_actor_counts_removes_geography_and_noise(self) -> None:
        dataframe = pd.DataFrame(
            {
                "Actor1Name": ["BENIN", "ECOWAS", "GOVERNMENT", "FRANCE"],
                "Actor1CountryCode": ["BEN", "WAF", "Inconnu", "FRA"],
                "Actor2Name": ["Inconnu", "WORLD BANK", "COTONOU", "The Opposition"],
                "Actor2CountryCode": ["Inconnu", "Inconnu", "BEN", "Inconnu"],
                "ActionGeo_FullName": [
                    "Cotonou, Littoral, Benin",
                    "Porto-Novo, Oueme, Benin",
                    "Parakou, Borgou, Benin",
                    "Cotonou, Littoral, Benin",
                ],
            }
        )

        result = extract_actor_counts(dataframe, limit=10)

        actors = result["Acteur"].tolist()
        self.assertIn("Ecowas", actors)
        self.assertIn("World Bank", actors)
        self.assertIn("The Opposition", actors)
        self.assertNotIn("Benin", actors)
        self.assertNotIn("Cotonou", actors)
        self.assertNotIn("Government", actors)
        self.assertNotIn("France", actors)

    def test_extract_actor_counts_raises_on_invalid_limit(self) -> None:
        dataframe = pd.DataFrame({"Actor1Name": ["ECOWAS"]})

        with self.assertRaises(ValueError):
            extract_actor_counts(dataframe, limit=0)


if __name__ == "__main__":
    unittest.main()
