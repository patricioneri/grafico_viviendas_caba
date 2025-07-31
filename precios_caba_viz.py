import dash
from dash import dcc, html, Input, Output
import dash_table
import plotly.express as px
import pandas as pd
import requests

# Carga datos
#ruta = r"C:\Users\PatricioGarcia\OneDrive - GO EXP Company\Documentos\Master\Visualización de la información\Trabajo Final\viviendas_caba_clean.csv"
ruta = "viviendas_caba_clean.csv"
df_raw = pd.read_csv(ruta)

# Trae polígonos para delimitar los barrios
geojson_url = "https://cdn.buenosaires.gob.ar/datosabiertos/datasets/barrios/barrios.geojson"
response = requests.get(geojson_url)
barrios_geojson = response.json()

# Agrupa cantidad de propiedades por barrio para el mapa
df_barrio = df_raw.groupby("BARRIO").size().reset_index(name="cantidad")

# Crea app
app = dash.Dash(__name__)
server = app.server

# Layout
app.layout = html.Div([
    html.H1("Mapa interactivo de precio de propiedades en CABA", style={"textAlign": "center"}),

    html.Div([

        # Columna izquierda -> mapa
        html.Div([
            dcc.Graph(id="mapa", figure=px.choropleth_mapbox(
                df_barrio,
                geojson=barrios_geojson,
                locations="BARRIO",
                featureidkey="properties.BARRIO",
                color="cantidad",
                color_continuous_scale="Viridis",
                mapbox_style="carto-positron",
                center={"lat": -34.61, "lon": -58.42},
                zoom=10.5,
                opacity=0.6,
                height=600
            )),
        ], style={"width": "60%", "display": "inline-block", "verticalAlign": "top"}),

        # Columna derecha -> título, subtítulo e histograma
        html.Div([
            html.Div([
                html.Div(id="titulo-barrio", style={
                    "fontSize": "20px",
                    "fontWeight": "bold",
                    "marginBottom": "0.5em",
                    "marginLeft": "60px"
                }),
                html.Div(id="subtitulo-barrio", style={
                    "fontSize": "18px",
                    "marginBottom": "1em",
                    "color": "#333",
                    "marginLeft": "60px"
                }),
            ]),
            dcc.Graph(id="histograma", style={"height": "550px"}),
        ], style={"width": "38%", "display": "inline-block", "paddingLeft": "2%", "verticalAlign": "top"})

    ]),

    # Tabla inferior
    html.Div(id="tabla-barrio", style={"marginTop": "40px", "padding": "0 60px"})
])

# -------------------------------
# CALLBACK Y FUNCIÓN
# -------------------------------

# Este callback se activa cuando el usuario hace clic en un barrio del mapa
@app.callback(
    Output("histograma", "figure"),           # Actualiza el gráfico de histograma
    Output("titulo-barrio", "children"),      # Actualiza el texto del título
    Output("subtitulo-barrio", "children"),   # Actualiza el subtítulo del histograma
    Output("tabla-barrio", "children"),       # Muestra una tabla debajo con los datos del barrio
    Input("mapa", "clickData")                # Escucha el clic del usuario en el mapa
)
def actualizar_histograma(clickData):
    # Si aún no se ha hecho clic en ningún barrio
    if clickData is None:
        return {}, "Hacé clic en un barrio", "", ""

    # Extrae el nombre del barrio del clic en el mapa
    barrio = clickData["points"][0]["location"]

    # Filtra el DataFrame original por ese barrio
    df_filtrado = df_raw[df_raw["BARRIO"] == barrio]

    # Crea histograma de precios en dólares
    fig = px.histogram(
        df_filtrado,
        x="DOLARES",
        nbins=30,
        labels={"DOLARES": "Precio en USD", "y": "Cantidad"}
    )
    fig.update_yaxes(title="Cantidad")

    # Crea una tabla con los datos del barrio filtrado
    tabla = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df_filtrado.columns],  # Usa todas las columnas
        data=df_filtrado.to_dict("records"),                          # Convierte a registros por fila
        page_size=10,                                                 # Muestra 10 registros por página
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left",
            "minWidth": "100px",
            "maxWidth": "300px",
            "whiteSpace": "normal"
        },
        style_header={
            "fontWeight": "bold",
            "backgroundColor": "#f0f0f0"
        },
    )

    # Devuelve todos los outputs
    return (
        fig,
        f"Barrio seleccionado: {barrio}",
        f"Distribución de precios en {barrio}",
        tabla
    )

# Ejecuta la app en modo debug
if __name__ == "__main__":
    app.run(debug=True)
