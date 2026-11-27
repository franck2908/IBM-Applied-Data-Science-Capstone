
from pathlib import Path
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Charger les données
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "spacex_dashboard_data.csv"
df = pd.read_csv(DATA_PATH)

app = Dash(__name__)

sites = ["Tous"] + sorted(df["LaunchSite"].dropna().unique())

app.layout = html.Div([
    html.H1("SpaceX Launch Analysis Dashboard"),

    html.Label("Sélectionner un site de lancement :"),

    dcc.Dropdown(
        id="site-dropdown",
        options=[{"label": s, "value": s} for s in sites],
        value="Tous",
        clearable=False
    ),

    html.H2("Répartition des résultats d'atterrissage"),
    dcc.Graph(id="success-pie"),

    html.H2("Masse de la charge utile par numéro de vol"),
    dcc.Graph(id="payload-scatter")
])


@app.callback(
    [Output("success-pie", "figure"),
     Output("payload-scatter", "figure")],
    Input("site-dropdown", "value")
)
def update_dashboard(selected_site):

    filtered = df.copy()

    if selected_site != "Tous":
        filtered = filtered[filtered["LaunchSite"] == selected_site]

    confirmed = filtered.dropna(subset=["LandingSuccess"])

    pie_data = (
        confirmed["LandingSuccess"]
        .map({1: "Réussite", 0: "Échec"})
        .value_counts()
        .rename_axis("Résultat")
        .reset_index(name="Nombre")
    )

    pie_fig = px.pie(
        pie_data,
        names="Résultat",
        values="Nombre",
        title="Réussites et échecs des atterrissages"
    )

    scatter_fig = px.scatter(
        filtered,
        x="FlightNumber",
        y="PayloadMass",
        color="LandingSuccess",
        hover_data=["LaunchSite", "Orbit"],
        title="Charge utile selon le numéro de vol",
        labels={
            "FlightNumber": "Numéro de vol",
            "PayloadMass": "Masse de la charge utile (kg)",
            "LandingSuccess": "Réussite"
        }
    )

    return pie_fig, scatter_fig


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
