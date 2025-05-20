import pandas as pd

# Charger le fichier CSV filtré
df = pd.read_csv("H:/Documents/ING1/Projet_Mai_2025/fichier_entierement_filtré.csv", sep=';', encoding='utf-8')

# Nettoyer : garder uniquement les stations avec coordonnées et pollution
df = df.dropna(subset=['stop_lat', 'stop_lon', 'pollution_finale'])

# Convertir le texte de pollution en score numérique
def pollution_score(text):
    if isinstance(text, str):
        text = text.lower()
        if "faible" in text:
            return 1
        elif "modérée" in text or "modere" in text:
            return 2
        elif "élevée" in text or "elevee" in text:
            return 3
    return 2  # Valeur par défaut

df['pollution_score'] = df['pollution_finale'].apply(pollution_score)

# ✅ Sauvegarder le fichier mis à jour avec pollution_score
df.to_csv("H:/Documents/ING1/Projet_Mai_2025/fichier_entierement_filtré.csv", sep=';', index=False, encoding='utf-8-sig')

print("Colonne 'pollution_score' ajoutée et fichier mis à jour.")
