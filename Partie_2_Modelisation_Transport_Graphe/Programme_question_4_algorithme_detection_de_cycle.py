import pandas as pd
import networkx as nx
from geopy.distance import geodesic

# === 1. Charger les données des stations ===
stations_df = pd.read_csv("H:/Documents/ING1/Projet_Mai_2025/fichier_entierement_filtré.csv", sep=';', encoding='utf-8')

# === 2. Filtrer uniquement les stations du métro ===
stations_df = stations_df[stations_df['nom de la ligne'].str.contains("métro", case=False, na=False)]
stations_df = stations_df.dropna(subset=['nom de la station', 'stop_lat', 'stop_lon'])

# === 3. Charger les connexions station1 → station2 ===
edges_df = pd.read_csv("H:/Documents/ING1/Projet_Mai_2025/connection_lignes_avec_metro_associe.csv", sep=';', encoding='utf-8')
edges_df = edges_df[edges_df['ligne'].str.contains("métro", case=False, na=False)]

# === 4. Construire le graphe ===
G = nx.Graph()

# Ajouter les nœuds
for _, row in stations_df.iterrows():
    G.add_node(
        row['nom de la station'],
        coords=(row['stop_lat'], row['stop_lon']),
        ligne=row['nom de la ligne']
    )

# Ajouter les arêtes
for _, row in edges_df.iterrows():
    s1 = row['station1']
    s2 = row['station2']
    if s1 in G.nodes and s2 in G.nodes:
        coord1 = G.nodes[s1]['coords']
        coord2 = G.nodes[s2]['coords']
        dist = geodesic(coord1, coord2).km
        G.add_edge(s1, s2, ligne=row['ligne'], distance_km=round(dist, 3))

# === 5. Détection des cycles ===
cycles = nx.cycle_basis(G)

# === 6. Affichage ===
if cycles:
    print(f"\n {len(cycles)} cycle(s) détecté(s) dans le graphe du métro.")

    # Exemple : afficher le premier cycle avec retour au départ
    exemple = cycles[0] + [cycles[0][0]]

    # Calculer la distance totale du cycle
    distance_totale = 0
    for i in range(len(exemple) - 1):
        s1 = exemple[i]
        s2 = exemple[i + 1]
        if G.has_edge(s1, s2):
            distance_totale += G[s1][s2].get("distance_km", 0)

    print("\n Exemple de cycle fermé :")
    print(" → ".join(exemple))
    print(f" Longueur du cycle : {round(distance_totale, 2)} km")
    print(f" Nombre de stations dans le cycle : {len(exemple) - 1}")
else:
    print("\n Aucun cycle détecté dans le réseau métro.")
