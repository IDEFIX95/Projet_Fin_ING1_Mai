import pandas as pd


# PArtie 2 de la question 1 de la Partie 2

# === 1. Charger le fichier CSV existant ===
input_path = "H:/Documents/ING1/Projet_Mai_2025/connection_lignes_avec_metro_associe.csv"
df = pd.read_csv(input_path, sep=';', encoding='utf-8')

# === 2. Afficher les colonnes détectées ===
print("\n Colonnes détectées :", df.columns.tolist())

# === 3. Normaliser les noms de colonnes ===
df.columns = df.columns.str.strip().str.lower()

# === 4. Vérification directe des colonnes ===
required_cols = {'station1', 'station2'}
if not required_cols.issubset(df.columns):
    raise ValueError(f" Les colonnes attendues {required_cols} sont manquantes.\nColonnes actuelles : {df.columns.tolist()}")

# === 5. Créer un booléen "connected" si absent
if 'connected' not in df.columns:
    df['connected'] = True

# === 6. Supprimer les doublons directionnels A-B = B-A
df['station_min'] = df[['station1', 'station2']].min(axis=1)
df['station_max'] = df[['station1', 'station2']].max(axis=1)

# === 7. Garder uniquement les connexions uniques
df_unique = df[['station_min', 'station_max', 'connected']].drop_duplicates()
df_unique.columns = ['station1', 'station2', 'connected']

# === 8. Sauvegarder le fichier final avec ; et utf-8-sig
output_path = "H:/Documents/ING1/Projet_Mai_2025/graphe_connexions_optimise.csv"
df_unique.to_csv(output_path, index=False, sep=';', encoding='utf-8-sig')

print("\n Fichier optimisé créé avec succès :")
print(f"➡ {output_path}")
