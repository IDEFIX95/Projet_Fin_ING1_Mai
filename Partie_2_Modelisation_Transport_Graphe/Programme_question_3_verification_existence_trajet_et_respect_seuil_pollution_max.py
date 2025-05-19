import pandas as pd 
import networkx as nx
from geopy.distance import geodesic
from itertools import combinations

# === 1. Charger les données ===
file_path = "H:/Documents/ING1/Projet_Mai_2025/fichier_entierement_filtré.csv"
df = pd.read_csv(file_path, sep=';', encoding='utf-8')

# === 2. Convertir les niveaux de pollution en score numérique ===
def pollution_score(pollution_text):
    if isinstance(pollution_text, str):
        pollution_text = pollution_text.lower()
        if "faible" in pollution_text:
            return 1
        elif "modérée" in pollution_text or "modere" in pollution_text:
            return 2
        elif "élevée" in pollution_text or "elevee" in pollution_text:
            return 3
    return 2

df['pollution_score'] = df['pollution_finale'].apply(pollution_score)

# === 3. Supprimer les stations sans coordonnées ===
df = df.dropna(subset=['stop_lat', 'stop_lon'])

# === 4. Créer le graphe complet (sans filtrage de pollution) ===
G = nx.Graph()

# Ajouter les nœuds avec leurs attributs
for _, row in df.iterrows():
    G.add_node(
        row['nom de la station'],
        pollution=row['pollution_score'],
        coords=(row['stop_lat'], row['stop_lon']),
        ligne=row['nom de la ligne']
    )

# Ajouter les arêtes entre stations proches sur la même ligne
for line in df['nom de la ligne'].unique():
    stations_line = df[df['nom de la ligne'] == line]
    seuil_km = 6.0 if "rer" in line.lower() else 2.0

    for (idx1, row1), (idx2, row2) in combinations(stations_line.iterrows(), 2):
        s1 = row1['nom de la station']
        s2 = row2['nom de la station']
        if s1 != s2:
            coord1 = (row1['stop_lat'], row1['stop_lon'])
            coord2 = (row2['stop_lat'], row2['stop_lon'])
            dist = geodesic(coord1, coord2).km
            if dist <= seuil_km:
                G.add_edge(s1, s2, ligne=line)

# === 5. Afficher les stations disponibles ===
stations = sorted(G.nodes)
print("\n📍 Liste des stations disponibles :")
for i, station in enumerate(stations):
    print(f"{i}. {station}")

# === 6. Saisie des paramètres utilisateur ===
try:
    idx_depart = int(input("\n🔹 Numéro de la station de départ : "))
    idx_arrivee = int(input("🔹 Numéro de la station d'arrivée : "))
    seuil_pollution = int(input("🌫️ Pollution maximale autorisée (1 = faible, 2 = modérée, 3 = élevée) : "))
except ValueError:
    print("❌ Entrée invalide.")
    exit()

if idx_depart < 0 or idx_depart >= len(stations) or idx_arrivee < 0 or idx_arrivee >= len(stations):
    print("❌ Numéro de station invalide.")
    exit()

start = stations[idx_depart]
end = stations[idx_arrivee]

# === 7. Créer un sous-graphe avec uniquement les stations respectant le seuil ===
stations_autorisees = [n for n, attr in G.nodes(data=True) if attr['pollution'] <= seuil_pollution]
G_filtré = G.subgraph(stations_autorisees)

# === 8. Vérifier si un chemin existe dans ce sous-graphe ===
if start in G_filtré and end in G_filtré and nx.has_path(G_filtré, start, end):
    print("\n✅ Un chemin existe entre les deux stations avec pollution ≤ seuil demandé.")
    path = nx.shortest_path(G_filtré, source=start, target=end)
    print("🧭 Chemin possible :", " → ".join(path))
else:
    print("\n❌ Aucun chemin ne respecte la contrainte de pollution.")
