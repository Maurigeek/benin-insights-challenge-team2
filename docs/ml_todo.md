## TODO unique
- [x] Garder ce fichier comme source unique de pilotage

## P0 — Modele ML et verifications
- [ ] Verifier et finaliser le modele principal
- [ ] Corriger les enormites encore visibles dans les sorties
- [ ] Valider que les spikes identifies correspondent a de vrais evenements
- [ ] Verifier la coherence des features, predictions et exports
- [ ] Documenter clairement comment relancer entrainement et prediction
- [ ] Verifier la premiere version du modele ML dans le notebook

## P0 — Topics et structure analytique
- [ ] Evaluer si la section topics apporte une vraie valeur
- [ ] Supprimer la partie topics si elle duplique les types d'evenements
- [ ] Sinon, rendre les topics plus pertinents et plus interpretables
- [ ] Valider manuellement un echantillon des sorties conservees

## P0 — Insights dashboard
- [ ] Ajouter des insights dynamiques directement dans le dashboard
- [ ] Lier chaque insight a une preuve visible ou un graphique
- [ ] Prioriser 5 a 7 insights courts, utiles et non techniques

## P1 — Cartes et visualisations
- [ ] Inserer des graphiques plus pertinents
- [ ] Mettre les cartes en priorite dans le dashboard
- [ ] Verifier la lisibilite des visualisations, titres, axes et legendes
- [ ] Verifier au moins 3 visualisations pertinentes sur les donnees du Benin
- [ ] Verifier les 5 visualisations commentees minimum dans le notebook

## P1 — Dashboard et integration
- [ ] Rendre la periode dynamique sur tout le dashboard
- [ ] Rendre les filtres temporels coherents partout
- [ ] Integrer les sorties utiles du modele dans les vues dashboard
- [ ] Ajouter un tableau filtrable (date, acteur, region, type)
- [ ] Integrer le graphe reseau interactif filtrable par periode
- [ ] Verifier que le dashboard en ligne est accessible et fonctionnel

## P1 — Design et presentation
- [ ] Ameliorer le design global
- [ ] Ameliorer la presentation globale
- [ ] Verifier la hierarchie visuelle, l'espacement et la lisibilite
- [ ] Verifier la coherence globale du parcours utilisateur

## P2 — Donnees et reproductibilite
- [ ] Verifier la periode extraite et les filtres Benin appliques
- [ ] Verifier les mois incomplets, les valeurs manquantes et les doublons critiques
- [ ] Confirmer que `data/raw/gdelt_benin_main.csv` peut etre regenere
- [ ] Regenerer et verifier les fichiers `data/processed/`
- [ ] Verifier `requirements.txt`, `Makefile` et les commandes utiles
- [ ] Verifier que le notebook EDA est reproductible

## P2 — Depot et livrables
- [ ] Rendre le depot GitHub public et propre
- [ ] Verifier le `README`, `requirements.txt`, `data/`, `notebooks/`, `models/`, `dashboard/`
- [ ] Ajouter le resume d'une page dans le depot
- [ ] Finaliser et publier la video pitch 3 min
- [ ] Verifier que tous les liens sont publics et ouvrables directement

## P3 — Validation globale et soumission
- [ ] Faire une validation globale du projet (all notebooks executable)
- [ ] Verifier la coherence entre notebook, dashboard, modele et resume
- [ ] Verifier les livrables attendus de la phase 1 une derniere fois
- [ ] Tester le full pipeline: extract → transform → train → predict → dashboard
- [ ] Soumettre le formulaire avant la deadline
