from __future__ import annotations

import unittest

import pandas as pd

from src.models.geo_model import build_geo_event_points


class GeoModelTests(unittest.TestCase):
    def test_build_geo_event_points_aggregates_real_locations(self) -> None:
        dataframe = pd.DataFrame(
            {
                "ActionGeo_FullName": ["Cotonou, Benin", "Cotonou, Benin", "Parakou, Benin"],
                "ActionGeo_Lat": [6.3654, 6.3654, 9.3372],
                "ActionGeo_Long": [2.4183, 2.4183, 2.6303],
                "AvgTone": [-1.0, -2.0, 0.5],
                "event_label": ["Appel / Demande", "Appel / Demande", "Accord / Coopération"],
            }
        )

        points = build_geo_event_points(dataframe)

        self.assertEqual(len(points), 2)
        self.assertEqual(points.iloc[0]["location"], "Cotonou, Benin")
        self.assertEqual(int(points.iloc[0]["event_count"]), 2)
        self.assertEqual(points.iloc[0]["dominant_event"], "Appel / Demande")

    def test_build_geo_event_points_excludes_generic_centroid(self) -> None:
        dataframe = pd.DataFrame(
            {
                "ActionGeo_FullName": ["Benin", "Ouidah, Benin"],
                "ActionGeo_Lat": [9.5, 6.36307],
                "ActionGeo_Long": [2.25, 2.08506],
                "AvgTone": [-1.0, 1.0],
                "event_label": ["Appel / Demande", "Accord / Coopération"],
            }
        )

        points = build_geo_event_points(dataframe)

        self.assertEqual(len(points), 1)
        self.assertEqual(points.iloc[0]["location"], "Ouidah, Benin")


if __name__ == "__main__":
    unittest.main()
