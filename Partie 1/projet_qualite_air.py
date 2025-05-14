
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix, silhouette_score, accuracy_score
import matplotlib.pyplot as plt

# === QUESTION 1 : Nettoyage du dataset ===

print("\n=== Nettoyage du fichier CSV ===")
fichier_csv = "qualite-de-lair-dans-le-reseau-de-transport-francilien (1).csv"
df = pd.read_csv(fichier_csv, sep=";", encoding='utf-8')
print("Taille initiale :", df.shape)

df.dropna(axis=1, how='all', inplace=True)
df.dropna(axis=0, how='all', inplace=True)
colonnes_uniques = [col for col in df.columns if df[col].nunique() <= 1]
df.drop(columns=colonnes_uniques, inplace=True)
df.drop_duplicates(inplace=True)
print("Taille après nettoyage :", df.shape)

df.to_csv("dataset_nettoye.csv", index=False, sep=";", encoding='utf-8')
print("✅ Fichier 'dataset_nettoye.csv' enregistré")

# === QUESTION 3 : Filtrage métro + séparation ===

print("\n=== Filtrage des stations de métro et découpage train/test ===")
df_metro = df[df["Nom de la ligne"].str.startswith("Métro", na=False)].copy()
print("Nombre de lignes de métro :", df_metro.shape[0])

train_df, test_df = train_test_split(df_metro, test_size=0.3, random_state=42)
train_df.to_csv("train.csv", index=False, sep=";", encoding='utf-8')
test_df.to_csv("test.csv", index=False, sep=";", encoding='utf-8')
print(f"✅ Fichier 'train.csv' : {len(train_df)} lignes")
print(f"✅ Fichier 'test.csv' : {len(test_df)} lignes")

# === QUESTION 4 : K-Means ===

print("\n=== Modèle K-Means (3 clusters) ===")
train_df = pd.read_csv("train.csv", sep=";", encoding='utf-8')
colonnes_utiles = ['stop_lat', 'stop_lon', 'niveau_pollution']
colonnes_utiles = [col for col in colonnes_utiles if col in train_df.columns]

if 'niveau_pollution' in colonnes_utiles and train_df['niveau_pollution'].dtype == 'object':
    train_df['niveau_pollution'] = train_df['niveau_pollution'].astype('category').cat.codes

X = train_df[colonnes_utiles].dropna()
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X_scaled)

train_df_cleaned = train_df.loc[X.index].copy()
train_df_cleaned['cluster'] = clusters
train_df_cleaned.to_csv("train_kmeans.csv", index=False, sep=";", encoding='utf-8')
print("✅ Fichier 'train_kmeans.csv' enregistré avec les clusters")

plt.figure(figsize=(8,6))
plt.scatter(train_df_cleaned['stop_lon'], train_df_cleaned['stop_lat'],
            c=train_df_cleaned['cluster'], cmap='viridis', s=50)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Clustering des stations de métro (K-Means)")
plt.colorbar(label="Cluster")
plt.grid(True)
plt.tight_layout()
plt.show()

# === Évaluation K-Means ===

print("\n=== Évaluation du modèle K-Means ===")
print(f"Inertie du modèle : {kmeans.inertia_:.2f}")
sil_score = silhouette_score(X_scaled, clusters)
print(f"Silhouette Score : {sil_score:.3f}")

# === QUESTION 5 : KNN ===

print("\n=== Modèle K-Plus-Proches-Voisins (KNN) ===")
train_df = pd.read_csv("train.csv", sep=";", encoding='utf-8')
test_df = pd.read_csv("test.csv", sep=";", encoding='utf-8')

features = ['stop_lat', 'stop_lon']
target = 'niveau_pollution'

if target not in train_df.columns or not all(f in train_df.columns for f in features):
    print("❌ Données manquantes pour le KNN.")
else:
    train_df = train_df[features + [target]].dropna()
    test_df = test_df[features + [target]].dropna()

    encoder = LabelEncoder()
    y_train = encoder.fit_transform(train_df[target])
    y_test = encoder.transform(test_df[target])

    scaler = StandardScaler()
    X_train = scaler.fit_transform(train_df[features])
    X_test = scaler.transform(test_df[features])

    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X_train, y_train)
    y_pred = knn.predict(X_test)

    print("\nClassification Report :")
    print(classification_report(y_test, y_pred, target_names=encoder.classes_))

    print("\nMatrice de confusion :")
    print(confusion_matrix(y_test, y_pred))

    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nTaux de bonne classification (Accuracy) : {accuracy:.2%}")
