import pandas as pd
import networkx as nx
from geopy.distance import geodesic

# === 1. Charger les données préparées ===
df = pd.read_csv("H:/Documents/ING1/Projet_Mai_2025/fichier_entierement_filtré.csv", sep=';', encoding='utf-8')

# === 2. Garder les stations valides (coordonnées + pollution_score déjà préparé) ===
df = df.dropna(subset=['stop_lat', 'stop_lon', 'pollution_score'])

# === 3. Créer le graphe ===
G = nx.Graph()
connections = []

# === 4. Ajouter les stations comme nœuds ===
for _, row in df.iterrows():
    G.add_node(
        row['nom de la station'],
        pollution=row['pollution_score'],
        coords=(row['stop_lat'], row['stop_lon']),
        ligne=row['nom de la ligne']
    )

# === 5. Relier automatiquement chaque station à sa plus proche voisine sur la même ligne ===
for line in df['nom de la ligne'].unique():
    stations_line = df[df['nom de la ligne'] == line]
    seuil_km = 6.0 if "rer" in line.lower() else 2.0

    for idx1, row1 in stations_line.iterrows():
        s1 = row1['nom de la station']
        coord1 = (row1['stop_lat'], row1['stop_lon'])
        poll1 = row1['pollution_score']

        # Chercher la station la plus proche
        voisins = []
        for idx2, row2 in stations_line.iterrows():
            s2 = row2['nom de la station']
            if s1 != s2:
                coord2 = (row2['stop_lat'], row2['stop_lon'])
                dist = geodesic(coord1, coord2).km
                if dist <= seuil_km:
                    voisins.append((dist, s2, row2['pollution_score']))

        # Ajouter l’arête vers la plus proche voisine uniquement
        if voisins:
            voisins.sort()
            dist, s2, poll2 = voisins[0]
            if not G.has_edge(s1, s2):  # Éviter les doublons
                pollution_moy = (poll1 + poll2) / 2
                G.add_edge(s1, s2, distance=dist, pollution=pollution_moy, ligne=line)

                connections.append({
                    "station1": s1,
                    "station2": s2,
                    "ligne": line,
                    "distance_km": round(dist, 3),
                    "pollution_moyenne": round(pollution_moy, 2)
                })

# === 6. Exporter le fichier CSV des connexions ===
df_conn = pd.DataFrame(connections)
df_conn.to_csv("H:/Documents/ING1/Projet_Mai_2025/connexions_reseau_graph.csv", sep=';', index=False, encoding='utf-8-sig')

print(f" Fichier de connexions généré avec {len(df_conn)} liens.")
print("➡ Chemin :", "H:/Documents/ING1/Projet_Mai_2025/connexions_reseau_graph.csv")
