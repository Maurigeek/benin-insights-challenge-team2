# TODO — Modele Anomalies

## Architecture
- [ ] Refondre `anomaly_model` en modules separes
- [ ] Creer `features`
- [ ] Creer `detector`
- [ ] Creer `postprocessing`
- [ ] Creer `schemas/results`
- [ ] Creer `config`

## Logique metier
- [ ] Gerer explicitement les mois incomplets
- [ ] Distinguer `anomalie reelle` vs `donnee partielle`
- [ ] Definir une vraie strategie de scoring
- [ ] Expliciter les seuils, hypotheses et cas limites
- [ ] Ajouter des `reason codes` / explications par anomalie
- [ ] Produire un objet de sortie plus riche et auditable

## Feature Engineering
- [ ] Ajouter la variation `MoM`
- [ ] Ajouter `rolling mean`
- [ ] Ajouter `rolling std`
- [ ] Ajouter l'intensite negative
- [ ] Ajouter la concentration par type
- [ ] Ajouter la concentration par acteurs

## Qualite du code
- [ ] Retirer les heuristviques hardcodees du coeur du code
- [ ] Centraliser constantes et parametres en config
- [ ] Eviter toute logique metier anomalies dans dashboard/API

## Tests
- [ ] Ajouter des tests unitaires sur les mois incomplets
- [ ] Ajouter des tests unitaires sur les faux positifs
- [ ] Ajouter des tests unitaires sur les petits echantillons
- [ ] Ajouter des tests unitaires sur la stabilite des scores
- [ ] Ajouter des jeux de tests metier

## Observabilite
- [ ] Journaliser la methode utilisee
- [ ] Journaliser les features utilisees
- [ ] Journaliser la periode analysee
- [ ] Journaliser le nombre de mois
- [ ] Journaliser les raisons de detection

## Integration
- [ ] Recalibrer ensuite les resultats visibles dans dashboard/API
