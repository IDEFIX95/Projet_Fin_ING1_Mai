# Projet_Fin_ING1_Mai

#  Analyse de la Pollution dans le Réseau de Transport Francilien

##  Description du Projet

Ce projet a pour but d'analyser la qualité de l'air dans les stations du métro et du RER en Île-de-France.  
Il repose sur la modélisation du réseau de transport sous forme de graphe afin de :
- visualiser les stations les plus polluées,
- effectuer une **analyse spectrale** du graphe,
- **trouver un chemin entre deux stations** en minimisant la pollution et respectant une contrainte de temps.

---

##  Fonctionnalités principales

- Génération d’un **graphe du réseau de transport** à partir des fichiers CSV.
- Nettoyage et traitement des données de pollution (`faible`, `modérée`, `élevée`).
- Recherche du **meilleur chemin** (le moins pollué) entre deux stations selon une durée limite.
- Visualisation :
  -  avec **matplotlib** pour l'analyse spectrale,
  -  avec **Dash + Plotly** pour une carte interactive.

---

##  Organisation

| Fichier | Rôle |
|--------|------|
| `fichier_entierement_filtré.csv` | Données principales : stations, pollution, lignes |
| `connection_lignes_avec_metro_associe.csv` | Connexions hypothétiques entre stations |
| `graphe_connexions_optimise.csv` | Connexions uniques nettoyées (format final pour graphe) |
| `Script_optimisation_filtrage.py` | Génère le fichier de connexions |
| `Filtrage_Trajet_Station_1_a_2.py` | Script principal de recherche de trajet optimisé |
| `Analyse_spectrale_pollution.py` | Analyse spectrale et carte interactive Dash |

---

##  Prérequis et dépendances

Pour exécuter les scripts Python, assure-toi d’avoir Python **3.10+** installé, puis installe les bibliothèques suivantes :

```bashq
pip install pandas numpy networkx matplotlib geopy dash plotly scipy scikit-learn

