# Bias Metadata

- dataset_rows: 6647
- date_range: 2025-01-01 00:00:00 -> 2026-04-28 00:00:00
- june_2025_rows: 209 (3.14%)
- language heuristic: fr-like=5.73%, en-like=36.18%
- topic_outlier_pct: 9.37

## Top Domains
- punchng.com: 447
- dailypost.ng: 426
- nigerianobservernews.com: 278
- lanouvelletribune.info: 236
- allafrica.com: 185
- guardian.ng: 174
- leadership.ng: 153
- www.thisdaylive.com: 141
- thesun.ng: 136
- quicknews-africa.net: 135

## NER Limitations
- Input NER is structured fields concatenated, not natural article text.
- en_core_web_sm may miss Benin-specific Francophone and local entities.
- Actor placeholders like Inconnu can inject noise.