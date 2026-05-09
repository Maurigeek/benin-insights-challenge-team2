"""Unit tests for media labeling."""

from __future__ import annotations

import unittest

import pandas as pd

from src.models.media.labeling import build_media_label, extract_source_domain


class MediaLabelingTests(unittest.TestCase):
    def test_extract_source_domain_handles_basic_urls(self) -> None:
        self.assertEqual(extract_source_domain("https://www.example.com/news"), "example.com")
        self.assertEqual(extract_source_domain("http://example.org"), "example.org")
        self.assertEqual(extract_source_domain(""), "")

    def test_build_media_label_assigns_known_domains(self) -> None:
        dataframe = pd.DataFrame(
            {
                "SOURCEURL": [
                    "https://benin.example/info",
                    "https://international.example/article",
                    "https://unknown.example",
                ]
            }
        )
        labels = build_media_label(
            dataframe=dataframe,
            benin_domains={"benin.example"},
            international_domains={"international.example"},
        )

        self.assertEqual(labels.iloc[0], 0)
        self.assertEqual(labels.iloc[1], 1)
        self.assertTrue(pd.isna(labels.iloc[2]))


if __name__ == "__main__":
    unittest.main()
