import pandas as pd 
import networkx as nx
import numpy as np
from geopy.distance import geodesic
from itertools import combinations
from heapq import heappush, heappop

# === 1. Charger les données ===
file_path = "H:/Documents/ING1/Projet_Mai_2025/fichier_entierement_filtré.csv"
df = pd.read_csv(file_path, sep=';', encoding='utf-8')

# === 2. Nettoyer la pollution : transformer le texte en score numérique ===
# Faible = 1, Modérée = 2, Élevée = 3, Inconnue = 2 (par défaut)
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

# === 3. Supprimer les stations sans coordonnées GPS ===
df = df.dropna(subset=['stop_lat', 'stop_lon'])

# === 4. Construire le graphe ===
G = nx.Graph()

# Ajouter chaque station comme nœud avec : pollution, coordonnées, ligne
for _, row in df.iterrows():
    G.add_node(
        row['nom de la station'],
        pollution=row['pollution_score'],
        coords=(row['stop_lat'], row['stop_lon']),
        ligne=row['nom de la ligne']
    )

# === 5. Relier les stations proches sur la même ligne ===
# Pour chaque ligne, on connecte les stations proches (≤ 2km pour métro, ≤ 6km pour RER)
for line in df['nom de la ligne'].unique():
    stations_line = df[df['nom de la ligne'] == line]
    
    seuil_km = 6.0 if "rer" in line.lower() else 2.0

    # On teste toutes les paires de stations de cette ligne
    for (idx1, row1), (idx2, row2) in combinations(stations_line.iterrows(), 2):
        s1 = row1['nom de la station']
        s2 = row2['nom de la station']
        if s1 != s2:
            coord1 = (row1['stop_lat'], row1['stop_lon'])
            coord2 = (row2['stop_lat'], row2['stop_lon'])
            dist = geodesic(coord1, coord2).km
            if dist <= seuil_km:
                travel_time = dist / 0.5  # 30 km/h ≈ 0.5 km/min
                pol_score = (row1['pollution_score'] + row2['pollution_score']) / 2
                G.add_edge(s1, s2, time=travel_time, pollution=pol_score, ligne=line)

# === 6. Afficher la liste des stations disponibles à l'utilisateur ===
stations = sorted(G.nodes)
print("\n📍 Liste des stations disponibles :")
for i, station in enumerate(stations):
    print(f"{i}. {station}")

# === 7. Demander à l'utilisateur la station de départ, d'arrivée et le temps max ===
try:
    idx_depart = int(input("\n🔹 Numéro de la station de départ : "))
    idx_arrivee = int(input("🔹 Numéro de la station d'arrivée : "))
    max_time = float(input("⏱️ Temps maximum autorisé (en minutes) : "))
except ValueError:
    print("❌ Entrée invalide. Veuillez entrer des numéros et un temps correct.")
    exit()

# Vérification de la validité des entrées
if idx_depart < 0 or idx_depart >= len(stations) or idx_arrivee < 0 or idx_arrivee >= len(stations):
    print("❌ Numéro de station invalide.")
    exit()

start = stations[idx_depart]
end = stations[idx_arrivee]

# Vérifie si un chemin est possible dans le graphe
if not nx.has_path(G, start, end):
    print("❌ Il n'existe aucun chemin entre ces deux stations dans le graphe.")
    exit()

# === 8. Fonction de recherche : chemin le moins pollué sous contrainte de temps (algo modifié de Dijkstra) ===
def chemin_le_moins_pollue(G, start, end, temps_max):
    heap = [(0, 0, start, [start])]  # (pollution cumulée, temps total, station actuelle, chemin suivi)
    visited = set()

    while heap:
        pollution, temps, current, path = heappop(heap)

        # Si on atteint la destination, on retourne le chemin et stats
        if current == end:
            pollution_moy = pollution / (len(path) - 1) if len(path) > 1 else 0
            return path, temps, pollution_moy

        # Évite de revisiter avec un temps déjà exploré
        if (current, round(temps, 2)) in visited:
            continue
        visited.add((current, round(temps, 2)))

        # Explorer les voisins
        for neighbor in G.neighbors(current):
            edge = G[current][neighbor]
            temps_suivant = temps + edge['time']
            if temps_suivant <= temps_max:
                pol_suiv = pollution + edge['pollution']
                heappush(heap, (pol_suiv, temps_suivant, neighbor, path + [neighbor]))

    return None  # Aucun chemin trouvé

# === 9. Exécution de la recherche et affichage des résultats ===
result = chemin_le_moins_pollue(G, start, end, max_time)

if result:
    path, total_time, avg_pollution = result
    print("\n✅ Meilleur chemin trouvé :")
    print(" → ".join(path))
    print(f"🕓 Temps estimé : {round(total_time, 2)} min")
    print(f"🌫️ Pollution moyenne : {round(avg_pollution, 2)}")
else:
    print("❌ Aucun chemin trouvé dans le temps imparti.")
