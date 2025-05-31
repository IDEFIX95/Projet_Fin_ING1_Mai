import pandas as pd
import re

# === 1. Charger le fichier source filtré ===
df = pd.read_csv("H:/Documents/ING1/Projet_Mai_2025/fichier_entierement_filtré.csv", sep=';', encoding='utf-8')

# === 2. Ne garder que les stations valides Métro ou RER ===
df = df[df['nom de la ligne'].str.contains("Métro|RER", case=False, na=False)]
df = df.dropna(subset=["nom de la station", "stop_lon", "stop_lat"])
df = df.drop_duplicates(subset=["nom de la station", "nom de la ligne"])

# === 3. Extraire clé de tri logique de ligne (ex: Métro 1 -> 1, RER A -> A) ===
def extract_line_key(line_name):
    match = re.search(r"(métro|rer)[\s\-]*([a-zA-Z]|\d+)", line_name, re.IGNORECASE)
    if match:
        val = match.group(2)
        return ord(val.upper()) if val.isalpha() else int(val)
    return float('inf')

df['Tri Ligne'] = df['nom de la ligne'].apply(extract_line_key)

# === 4. Tri spatial 2D : Nord-Sud + Est-Ouest ===
# Cela donne un ordre plus logique dans l'espace (évite erreurs Cergy/Poissy)
df_sorted = df.sort_values(by=["Tri Ligne", "nom de la ligne", "stop_lat", "stop_lon"])

# === 5. Créer les connexions consécutives (par ligne triée) ===
connections = []
prev_station = None
prev_line = None

for _, row in df_sorted.iterrows():
    current_station = row["nom de la station"]
    current_line = row["nom de la ligne"]

    if prev_line == current_line:
        connections.append({
            "station1": prev_station,
            "station2": current_station,
            "connected": True,
            "ligne": current_line
        })

    prev_station = current_station
    prev_line = current_line

# === 6. Exporter le fichier de connexions corrigées ===
output_path = "H:/Documents/ING1/Projet_Mai_2025/connection_lignes_avec_metro_associe.csv"
pd.DataFrame(connections).to_csv(output_path, sep=';', index=False, encoding='utf-8-sig')

print(f"\n Connexions générées avec succès dans : {output_path}")
