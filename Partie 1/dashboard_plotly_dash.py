
import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px

# Charger les données
df = pd.read_csv("train_kmeans.csv", sep=";")

# Appliquer un nom plus lisible pour les clusters
df["Cluster"] = df["cluster"].astype(str)

# Application Dash
app = dash.Dash(__name__)
app.title = "Dashboard Qualité de l'air"

app.layout = html.Div([
    html.H1("Qualité de l'air dans les stations de métro", style={'textAlign': 'center'}),

    dcc.Graph(
        id='map-clusters',
        figure=px.scatter_mapbox(
            df,
            lat="stop_lat",
            lon="stop_lon",
            color="Cluster",
            hover_name="Nom de la Station",
            zoom=10,
            mapbox_style="open-street-map",
            title="Clustering des stations de métro (K-Means)"
        )
    ),

    html.Div([
        dcc.Graph(
            id='bar-niveaux',
            figure=px.histogram(
                df,
                x="niveau_pollution",
                color="Cluster",
                barmode="group",
                title="Répartition des niveaux de pollution par cluster"
            )
        )
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
