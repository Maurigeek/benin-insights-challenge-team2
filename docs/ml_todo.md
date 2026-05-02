## Data
- [x] Load and inspect: columns, nulls, volume
- [x] Extract the useful text column(s): titles / Tone / Themes
- [x] GoldsteinScale moyen par mois -> courbe de tension globale
- [x] Top acteurs (Actor1Name) -> qui parle du Benin ?
- [x] Distribution des EventCode -> quels types d'evenements dominent ?
- [x] Creux juin 2025 -> confirmer biais ou realite
- [x] bias_metadata -> documenter tout ce qui est observe

## Model 1 — Topics (BERTopic)
- [x] Define input contract for `extract_topics(texts)` (types, preconditions, failures)
- [x] Select text field for topics (`event_label` vs other candidate columns)
- [x] Build Benin-only filter for training subset
- [x] Clean and normalize texts (trim, empty filtering, dedup if needed)
- [x] Fit BERTopic model on filtered texts
- [x] Export topic summary (topic id, size, top keywords)
- [x] Add `topic` column back to dataframe on original indices
- [x] Manual validation on a sample per topic (semantic coherence)
- [x] Document limitations/biases observed on Benin context
- [x] Add/maintain unit tests for edge cases and contract validation

## Model 3 — Entities (spaCy NER)
- [x] Implement `extract_entities()`
- [x] Validate that persons, places, and organizations are detected correctly

## Model 4 — Anomalies (Isolation Forest)
- [x] Implement `detect_anomalies()`
- [x] Add/maintain unit tests for contract and edge cases
- [ ] Validate that identified spikes match real events

## API
- [ ] Endpoint `/topics`
- [ ] Endpoint `/entities`
- [ ] Endpoint `/anomalies`
- [ ] Orchestrate with `asyncio.gather()` -> unified JSON
- [ ] Endpoint `/analyze` (runs the 3 in parallel)

## Rule
- [ ] Update this TODO whenever scope changes
