import pandas as pd

# === Charger le fichier source ===
input_path = "H:/Documents/ING1/Projet_Mai_2025/connection_lignes_avec_metro_associe.csv"
df = pd.read_csv(input_path, sep=';', encoding='utf-8')

# === Obtenir toutes les stations uniques ===
stations = pd.unique(df[['station1', 'station2']].values.ravel())

# === Générer le fichier nodes.csv ===
nodes_df = pd.DataFrame({
    'Node Type': ['Station'] * len(stations),
    'Name': stations
})

# === Générer le fichier edges.csv (Edge Type = ligne de métro ou RER) ===
edges_df = pd.DataFrame({
    'From Type': ['Station'] * len(df),
    'From Name': df['station1'],
    'Edge Type': df['ligne'],     # <= Pour la coloration automatique
    'To Type': ['Station'] * len(df),
    'To Name': df['station2'],
    'Weight': [1] * len(df),
    'Label': df['ligne']
})

# === Enregistrer les fichiers CSV ===
nodes_output = "H:/Documents/ING1/Projet_Mai_2025/nodes.csv"
edges_output = "H:/Documents/ING1/Projet_Mai_2025/edges.csv"

nodes_df.to_csv(nodes_output, index=False, sep=';', encoding='utf-8-sig')
edges_df.to_csv(edges_output, index=False, sep=';', encoding='utf-8-sig')

print("✅ Fichiers CSV générés avec succès pour GraphCommons (chaque ligne colorable) :")
print(f" - Nodes : {nodes_output}")
print(f" - Edges : {edges_output}")
