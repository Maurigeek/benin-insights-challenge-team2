## Data
- [ ] Load and inspect: columns, nulls, volume
- [ ] Extract the useful text column(s): titles / Tone / Themes

## Model 1 — Sentiment (VADER)
- [ ] Implement `analyze_sentiment()`
- [ ] Validate on 20 titles manually

## Model 2 — Topics (BERTopic)
- [ ] Implement `extract_topics()`
- [ ] Validate that topics are consistent with Benin data

## Model 3 — Entities (spaCy NER)
- [ ] Implement `extract_entities()`
- [ ] Validate that persons, places, and organizations are detected correctly

## Model 4 — Anomalies (Isolation Forest)
- [ ] Implement `detect_anomalies()`
- [ ] Validate that identified spikes match real events

## API
- [ ] Endpoint `/sentiment`
- [ ] Endpoint `/topics`
- [ ] Endpoint `/entities`
- [ ] Endpoint `/anomalies`
- [ ] Orchestrate with `asyncio.gather()` -> unified JSON
- [ ] Endpoint `/analyze` (runs the 4 in parallel)

## Rule
- [ ] Update this TODO whenever scope changes
