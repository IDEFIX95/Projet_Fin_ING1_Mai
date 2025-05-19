import pandas as pd
import networkx as nx
from geopy.distance import geodesic
from itertools import combinations

# === 1. Charger les données ===
file_path = "H:/Documents/ING1/Projet_Mai_2025/fichier_entierement_filtré.csv"
df = pd.read_csv(file_path, sep=';', encoding='utf-8')

# === 2. Filtrer uniquement les lignes Métro ===
df = df[df['nom de la ligne'].str.contains("métro", case=False, na=False)]

# === 3. Supprimer les stations sans coordonnées GPS ===
df = df.dropna(subset=['stop_lat', 'stop_lon'])

# === 4. Construire le graphe non orienté du métro ===
G = nx.Graph()

# Ajouter les stations comme nœuds
for _, row in df.iterrows():
    G.add_node(
        row['nom de la station'],
        coords=(row['stop_lat'], row['stop_lon']),
        ligne=row['nom de la ligne']
    )

# Connecter les stations proches sur la même ligne (logique identique à avant)
for line in df['nom de la ligne'].unique():
    stations_line = df[df['nom de la ligne'] == line]
    for (idx1, row1), (idx2, row2) in combinations(stations_line.iterrows(), 2):
        s1 = row1['nom de la station']
        s2 = row2['nom de la station']
        if s1 != s2:
            coord1 = (row1['stop_lat'], row1['stop_lon'])
            coord2 = (row2['stop_lat'], row2['stop_lon'])
            dist = geodesic(coord1, coord2).km
            if dist <= 2.0:  # seuil pour métro uniquement
                G.add_edge(s1, s2, ligne=line)

# === 5. Détection des cycles ===
cycles = nx.cycle_basis(G)

# === 6. Affichage ===
if cycles:
    print(f"✅ {len(cycles)} cycle(s) détecté(s) dans le graphe du métro.")
    print("🔁 Exemple de cycle :", " → ".join(cycles[0]))
else:
    print("❌ Aucun cycle détecté dans le réseau métro.")
