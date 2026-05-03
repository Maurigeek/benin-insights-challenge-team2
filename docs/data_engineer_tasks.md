# Tâches Data Engineer

### DE-01 — Valider le cadrage
- Vérifier la période extraite.
- Vérifier les filtres Bénin appliqués.
- Compter les événements par mois.
- Repérer les mois incomplets ou anormaux.
- Livrable : tableau court de validation.

### DE-02 — Finaliser l’extraction
- Vérifier la requête SQL principale.
- Vérifier les colonnes exportées.
- Confirmer que `data/raw/gdelt_benin_main.csv` peut être régénéré.
- Livrable : export brut validé.

### DE-03 — Finaliser le nettoyage et les agrégats
- Vérifier les dates, les types et les valeurs manquantes.
- Vérifier les doublons critiques.
- Régénérer les fichiers `data/processed/`.
- Livrable : fichiers processed validés.

### DE-04 — Sécuriser la reproductibilité
- Vérifier `requirements.txt`.
- Compléter le `Makefile` si besoin.
- Documenter les commandes utiles.
- Vérifier que le pipeline tourne depuis zéro.
- Livrable : projet reproductible.

### DE-05 — Débloquer les autres profils
- Confirmer les fichiers nécessaires au Data Analyst.
- Confirmer le dataset de features pour le ML Engineer.
- Corriger les formats bloquants si besoin.
- Livrable : données validées pour l’équipe.