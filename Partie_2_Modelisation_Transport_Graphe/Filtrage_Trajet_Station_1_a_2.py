import pandas as pd
import re

# === Charger le fichier source nettoyé ===
source_file_path = "H:/Documents/ING1/Projet_Mai_2025/qualite-de-lair-dans-le-reseau-de-transport-francilien.csv"
cleaned_df = pd.read_csv(source_file_path, sep=';', encoding='utf-8')

# === Filtrer les stations de Métro et de RER ===
mask = cleaned_df['Nom de la ligne'].str.contains("Métro|RER", case=False, na=False)
transport_df = cleaned_df[mask].copy()

# === Nettoyage de base ===
transport_df = transport_df.dropna(subset=["Nom de la Station"])
transport_df = transport_df.drop_duplicates(subset=["Nom de la Station", "Nom de la ligne"])

# === Extraire un numéro ou lettre pour trier les lignes logiquement ===
def extract_line_key(line_name):
    match = re.search(r"(métro|rer)[\s\-]*([a-zA-Z]|\d+)", line_name, re.IGNORECASE)
    if match:
        val = match.group(2)
        return ord(val.upper()) if val.isalpha() else int(val)
    return float('inf')  # lignes mal formatées mises à la fin

transport_df['Tri Ligne'] = transport_df['Nom de la ligne'].apply(extract_line_key)

# === Tri logique : par ligne, puis par nom de station ===
transport_df = transport_df.sort_values(by=["Tri Ligne", "Nom de la Station"])

# === Générer les connexions hypothétiques ===
connections = []
previous_station = None
previous_line = None

for _, row in transport_df.iterrows():
    current_station = row["Nom de la Station"]
    current_line = row["Nom de la ligne"]

    if previous_line == current_line:
        connections.append({
            "station1": previous_station,
            "station2": current_station,
            "connected": True,
            "ligne": current_line
        })

    previous_station = current_station
    previous_line = current_line

# === Enregistrer le fichier CSV avec le bon encodage et séparateur ===
connections_df = pd.DataFrame(connections)
output_path = "H:/Documents/ING1/Projet_Mai_2025/connection_lignes_avec_metro_associe.csv"
connections_df.to_csv(output_path, sep=';', index=False, encoding='utf-8-sig')

print(f"\n✅ Le fichier '{output_path}' a été généré avec succès avec métro + RER et encodage compatible Excel.")
