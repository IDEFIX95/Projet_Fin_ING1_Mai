import pandas as pd
import numpy as np
import networkx as nx
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# === 1. Charger les données de connexions ===
df_conn = pd.read_csv("H:/Documents/ING1/Projet_Mai_2025/connexions_reseau_graph.csv", sep=';', encoding='utf-8-sig')

# === 2. Construire le graphe ===
G = nx.Graph()
for _, row in df_conn.iterrows():
    s1, s2 = row['station1'], row['station2']
    pollution = row['pollution_moyenne']
    distance = row['distance_km']
    ligne = row['ligne']
    G.add_node(s1)
    G.add_node(s2)
    G.add_edge(s1, s2, pollution=pollution, weight=1, ligne=ligne, distance=distance)

# === 3. Générer un signal pollution (moyenne des arêtes connectées à chaque nœud) ===
pollution_dict = {}
for node in G.nodes():
    edges = G.edges(node, data=True)
    pollution_dict[node] = np.mean([data['pollution'] for _, _, data in edges]) if edges else 2
nx.set_node_attributes(G, pollution_dict, "pollution")

# === 4. Analyse spectrale ===
nodes = list(G.nodes())
pollution_signal = np.array([G.nodes[n]['pollution'] for n in nodes])
L = nx.normalized_laplacian_matrix(G, nodelist=nodes).astype(float)
eigvals, eigvecs = eigsh(L, k=5, which='SM')
projection = eigvecs.T @ pollution_signal

# === 5. Matplotlib : projection spectrale + export en PNG
plt.figure(figsize=(9, 5))
plt.plot(range(1, 6), projection, marker='o', linestyle='-', color='royalblue')
plt.title("Analyse spectrale du signal de pollution\n(projection sur les 5 premières composantes)", fontsize=13)
plt.xlabel("Composante spectrale (valeurs propres)", fontsize=11)
plt.ylabel("Amplitude projetée", fontsize=11)
plt.xticks(range(1, 6))
plt.grid(True)
plt.tight_layout()
plt.savefig("H:/Documents/ING1/Projet_Mai_2025/graphique_projection_spectrale.png", dpi=300)
plt.show()

# === 6. Top stations spectrales ===
dominants = np.argsort(np.abs(eigvecs[:, 1]))[::-1][:10]
print("\n🏭 Top 10 stations les plus influentes (composante spectrale 2) :")
for i in dominants:
    station = nodes[i]
    print(f" - {station} (pollution ≈ {round(G.nodes[station]['pollution'], 2)})")

# === 7. Charger les coordonnées GPS ===
df_coords = pd.read_csv("H:/Documents/ING1/Projet_Mai_2025/fichier_entierement_filtré.csv", sep=';', encoding='utf-8')
df_coords = df_coords.dropna(subset=['stop_lat', 'stop_lon'])

# ⚠️ Inverser lon/lat pour Plotly
coord_dict = {
    row['nom de la station']: (row['stop_lon'], row['stop_lat'])  # lon, lat
    for _, row in df_coords.iterrows()
}

# === 8. Fusion coordonnées + pollution pour la carte ===
stations = []
for node in G.nodes():
    if node in coord_dict:
        lon, lat = coord_dict[node]
        stations.append({
            "station": node,
            "lat": float(lat),
            "lon": float(lon),
            "pollution": G.nodes[node]["pollution"]
        })
df_map = pd.DataFrame(stations)

# === 9. Dash App ===
app = Dash(__name__)
app.title = "Carte pollution - Analyse spectrale"

app.layout = html.Div([
    html.H2("🌍 Carte interactive des stations selon leur pollution", style={'textAlign': 'center'}),
    html.Div([
        dcc.Slider(
            id='slider-seuil',
            min=1,
            max=3,
            step=0.1,
            value=1,
            marks={1: '1', 2: '2', 3: '3'},
            tooltip={"placement": "bottom", "always_visible": True}
        )
    ], style={'padding': '30px'}),
    dcc.Graph(id='carte-pollution')
])

@app.callback(
    Output('carte-pollution', 'figure'),
    Input('slider-seuil', 'value')
)
def update_map(seuil):
    df_filtered = df_map[df_map['pollution'] >= seuil]
    fig = px.scatter_mapbox(
        df_filtered,
        lat="lat",
        lon="lon",
        color="pollution",
        hover_name="station",
        zoom=10,
        color_continuous_scale="YlOrRd",
        mapbox_style="open-street-map",
        title=f"🌫️ Stations avec pollution ≥ {seuil}"
    )
    return fig

# ✅ Utilisation correcte avec Dash >= 2.0
if __name__ == '__main__':
    app.run(debug=True)
