import pandas as pd

# Charger le fichier source
input_path = "H:/Documents/ING1/Projet_Mai_2025/qualite-de-lair-dans-le-reseau-de-transport-francilien.csv"
df = pd.read_csv(input_path, sep=';', encoding='utf-8')

# Supprimer les colonnes entièrement vides
df = df.dropna(axis=1, how='all')

# Supprimer les lignes entièrement vides
df = df.dropna(axis=0, how='all')

# Supprimer les doublons
df = df.drop_duplicates()

# Normaliser les noms de colonnes
df.columns = df.columns.str.strip().str.lower()

# Colonnes redondantes à fusionner pour le niveau de pollution
pollution_cols = [
    'niveau de pollution aux particules',
    'niveau de pollution',
    'pollution_air',
    'niveau',
    'niveau_pollution'
]

# Conserver les colonnes existantes parmi celles listées
pollution_cols_existing = [col for col in pollution_cols if col in df.columns]

# Fusionner les colonnes redondantes dans 'pollution_finale'
if pollution_cols_existing:
    df['pollution_finale'] = df[pollution_cols_existing].bfill(axis=1).iloc[:, 0]
    df = df.drop(columns=pollution_cols_existing)

# Exporter le fichier nettoyé avec encodage utf-8-sig pour compatibilité Excel
output_path = "H:/Documents/ING1/Projet_Mai_2025/fichier_entierement_filtré.csv"
df.to_csv(output_path, sep=';', index=False, encoding='utf-8-sig')

print("✅ Fichier nettoyé généré avec succès avec fusion des colonnes de pollution :")
print(f"➡ {output_path}")
