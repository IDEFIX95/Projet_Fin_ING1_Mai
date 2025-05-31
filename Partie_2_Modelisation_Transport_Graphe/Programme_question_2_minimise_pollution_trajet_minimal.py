import pandas as pd
import networkx as nx
from geopy.distance import geodesic
from heapq import heappush, heappop

# === 1. Charger les données des stations ===
stations_df = pd.read_csv("H:/Documents/ING1/Projet_Mai_2025/fichier_entierement_filtré.csv", sep=';', encoding='utf-8')

# === 2. Nettoyer et convertir la pollution en score numérique ===
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

stations_df['pollution_score'] = stations_df['pollution_finale'].apply(pollution_score)
stations_df = stations_df.dropna(subset=['stop_lat', 'stop_lon'])

# === 3. Charger les connexions entre stations consécutives ===
edges_df = pd.read_csv("H:/Documents/ING1/Projet_Mai_2025/connection_lignes_avec_metro_associe.csv", sep=';', encoding='utf-8')

# === 4. Construire le graphe ===
G = nx.Graph()

# Ajouter chaque station comme nœud avec : pollution, coordonnées, ligne
for _, row in stations_df.iterrows():
    G.add_node(
        row['nom de la station'],
        pollution=row['pollution_score'],
        coords=(row['stop_lat'], row['stop_lon']),
        ligne=row['nom de la ligne']
    )

# Ajouter les connexions depuis le fichier (conformément à l'ordre spatial)
for _, row in edges_df.iterrows():
    s1 = row['station1']
    s2 = row['station2']
    if s1 in G.nodes and s2 in G.nodes:
        coord1 = G.nodes[s1]['coords']
        coord2 = G.nodes[s2]['coords']
        dist = geodesic(coord1, coord2).km
        travel_time = dist / 0.5  # 30 km/h ≈ 0.5 km/min
        pol_score = (G.nodes[s1]['pollution'] + G.nodes[s2]['pollution']) / 2
        G.add_edge(s1, s2, time=travel_time, pollution=pol_score, ligne=row.get('ligne', ''))

# === 5. Interface utilisateur ===
stations = sorted(G.nodes)
print("\n Liste des stations disponibles :")
for i, station in enumerate(stations):
    print(f"{i}. {station}")

try:
    idx_depart = int(input("\n Numéro de la station de départ : "))
    idx_arrivee = int(input(" Numéro de la station d'arrivée : "))
    max_time = float(input(" Temps maximum autorisé (en minutes) : "))
except ValueError:
    print(" Entrée invalide. Veuillez entrer des numéros et un temps correct.")
    exit()

if idx_depart < 0 or idx_depart >= len(stations) or idx_arrivee < 0 or idx_arrivee >= len(stations):
    print(" Numéro de station invalide.")
    exit()

start = stations[idx_depart]
end = stations[idx_arrivee]

if not nx.has_path(G, start, end):
    print(" Il n'existe aucun chemin entre ces deux stations dans le graphe.")
    exit()

# === 6. Chemin le moins pollué sous contrainte de temps ===
def chemin_le_moins_pollue(G, start, end, temps_max):
    heap = [(0, 0, start, [start])]  # (pollution, temps, station, chemin)
    visited = set()

    while heap:
        pollution, temps, current, path = heappop(heap)
        if current == end:
            avg_poll = pollution / (len(path) - 1) if len(path) > 1 else 0
            return path, temps, avg_poll

        if (current, round(temps, 2)) in visited:
            continue
        visited.add((current, round(temps, 2)))

        for neighbor in G.neighbors(current):
            edge = G[current][neighbor]
            next_time = temps + edge['time']
            if next_time <= temps_max:
                next_pollution = pollution + edge['pollution']
                heappush(heap, (next_pollution, next_time, neighbor, path + [neighbor]))

    return None

# === 7. Exécution et affichage ===
result = chemin_le_moins_pollue(G, start, end, max_time)

if result:
    path, total_time, avg_pollution = result
    print("\n Meilleur chemin trouvé :")
    print(" → ".join(path))
    print(f" Temps estimé : {round(total_time, 2)} min")
    print(f" Pollution moyenne : {round(avg_pollution, 2)}")
else:
    print(" Aucun chemin trouvé dans le temps imparti.")
