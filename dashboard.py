import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from dash import Dash, html, dcc, callback_context
from dash.dependencies import Input, Output, ClientsideFunction


LATITUDE, LONGITUDE = -14.272572694355336, -51.25567404158474
SELECT_COLUMNS = {
    "casosAcumulado": "Casos Acumulados", 
    "casosNovos": "Novos Casos", 
    "obitosAcumulado": "Óbitos Totais",
    "obitosNovos": "Óbitos por dia"
}

state_data = pd.read_csv("data/df_states.csv")
brasil_data = pd.read_csv("data/df_brasil.csv")
geolocation = json.load(open("geojson/brazil_geo.json"))

state_data_ = state_data[state_data["data"] == "2020-05-13"]
data_ = state_data[state_data["estado"] == "RJ"]

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
fig = px.choropleth_mapbox(
    state_data_,
    locations="estado",
    color="casosNovos",
    zoom=4,
    geojson=geolocation,
    color_continuous_scale="Redor",
    center={
        "lat": LATITUDE,
        "lon": LONGITUDE
    },
    opacity=0.4,
    hover_data={
        "casosAcumulado": True, 
        "casosNovos": True, 
        "obitosNovos": True, 
        "estado": True
    }
)

fig.update_layout(
    paper_bgcolor="#242424",
    autosize=True,
    margin=go.layout.Margin(l=0, r=0, t=0, b=0),
    showlegend=False,
    mapbox_style="carto-darkmatter"
)

fig2 = go.Figure(
    layout={
        "template": "plotly_dark"
    }
)

fig2.add_trace(
    go.Scatter(
        x=data_["data"],
        y=data_["casosAcumulado"]
    )
)

fig2.update_layout(
    paper_bgcolor="#242424",
    plot_bgcolor="#242424",
    autosize=True,
    margin=go.layout.Margin(l=10, r=10, t=10, b=10)
)

app.layout = dbc.Container(
    dbc.Row([
        dbc.Col([
            html.Div(
                [
                    html.H5("Evolução COVID-19"),
                    dbc.Button(
                        "Brasil",
                        color="primary",
                        id="location-button",
                        size="lg"
                    )
                ], 
                style={}
            ),
            html.P("Informe a data na qual deseja obter informações:", style={"margin-top": "40px"}),
            html.Div(
                    className="div-for-dropdown",
                    id="div-test",
                    children=[
                        dcc.DatePickerSingle(
                            id="date-picker",
                            min_date_allowed=state_data.groupby("estado")["data"].min().max(),
                            max_date_allowed=state_data.groupby("estado")["data"].max().min(),
                            initial_visible_month=state_data.groupby("estado")["data"].min().max(),
                            date=state_data.groupby("estado")["data"].max().min(),
                            display_format="MMMM D, YYYY",
                            style={"border": "0px solid black"},
                        )
                    ],
                ),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("Casos recuperados"),
                            html.H3(
                                style={
                                    "color": "#adfc92"
                                },
                                id="casos-recuperados-text"
                            ),
                            html.Span("Em acompanhamento"),
                            html.H5(id="em-acompanhamento-text")
                        ])
                        ], color="light",
                        outline=True,
                        style={
                            "margin-top": "10px",
                            "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)",
                            "color": "#FFFFFF"
                        }
                    )
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("Casos confirmados totais"),
                            html.H3(
                                style={
                                    "color": "#389fd6"
                                },
                                id="casos-confirmados-text"
                            ),
                            html.Span("Novos casos na data"),
                            html.H5(id="novos-casos-text")
                        ])
                        ], color="light",
                        outline=True,
                        style={
                            "margin-top": "10px",
                            "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)",
                            "color": "#FFFFFF"
                        }
                    )
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("Óbitos confirmados"),
                            html.H3(
                                style={
                                    "color": "#df2935"
                                },
                                id="obitos-text"
                            ),
                            html.Span("Óbito na data"),
                            html.H5(id="obitos-na-data-text")
                        ])
                        ], color="light",
                        outline=True,
                        style={
                            "margin-top": "10px",
                            "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)",
                            "color": "#FFFFFF"
                        }
                    )
                ], md=4)
            ]),
            html.Div([
                html.P("Selecione que tipo de dado deseja visualizar:", style={"margin-top": "25px"}),
                dcc.Dropdown(
                    id="location-dropdown",
                    options=[{"label": j, "value": i} for i, j in SELECT_COLUMNS.items()],
                    value="casosNovos",
                    style={"margin-top": "10px"}
                ),
                dcc.Graph(
                    id="line-graph",
                    figure=fig2
                )
            ])
        ], 
        md=5, 
        style={
            "padding": "25px",
            "background-color": "#242424"
        }),
        dbc.Col([
            dcc.Loading(
                id="loading-1",
                type="default",
                children=[
                    dcc.Graph(
                        id="choropleth-map",
                        figure=fig,
                        style={
                            "height": "100vh",
                            "margin-right": "10px"
                        }
                    )
                ]
            )
        ], md=7)
    ]),
    fluid=True
)

@app.callback(
    [
        Output("casos-recuperados-text", "children"),
        Output("em-acompanhamento-text", "children"),
        Output("casos-confirmados-text", "children"),
        Output("novos-casos-text", "children"),
        Output("obitos-text", "children"),
        Output("obitos-na-data-text", "children"),
    ], 
    [
        Input("date-picker", "date"), 
        Input("location-button", "children")
    ]
)
def display_status(date, location):
    location = location.upper()

    if location == "BRASIL":
        df_data_on_date = brasil_data[brasil_data["data"] == date]
    else:
        df_data_on_date = state_data[(state_data["estado"] == location) & (state_data["data"] == date)]
    
    recuperados_novos = "-" if df_data_on_date["Recuperadosnovos"].isna().values[0] else f'{int(df_data_on_date["Recuperadosnovos"].values[0]):,}'.replace(",", ".") 
    acompanhamentos_novos = "-" if df_data_on_date["emAcompanhamentoNovos"].isna().values[0]  else f'{int(df_data_on_date["emAcompanhamentoNovos"].values[0]):,}'.replace(",", ".") 
    casos_acumulados = "-" if df_data_on_date["casosAcumulado"].isna().values[0]  else f'{int(df_data_on_date["casosAcumulado"].values[0]):,}'.replace(",", ".") 
    casos_novos = "-" if df_data_on_date["casosNovos"].isna().values[0]  else f'{int(df_data_on_date["casosNovos"].values[0]):,}'.replace(",", ".") 
    obitos_acumulado = "-" if df_data_on_date["obitosAcumulado"].isna().values[0]  else f'{int(df_data_on_date["obitosAcumulado"].values[0]):,}'.replace(",", ".") 
    obitos_novos = "-" if df_data_on_date["obitosNovos"].isna().values[0]  else f'{int(df_data_on_date["obitosNovos"].values[0]):,}'.replace(",", ".") 

    return (
        recuperados_novos,
        acompanhamentos_novos,
        casos_acumulados,
        casos_novos,
        obitos_acumulado,
        obitos_novos
    )

@app.callback(
    Output("line-graph", "figure"),
    [
        Input("location-dropdown", "value"), 
        Input("location-button", "children")
    ]
)
def plot_line_graph(plot_type, location):
    location = location.upper()

    if location == "BRASIL":
        df_data_on_location = brasil_data.copy()
    else:
        df_data_on_location = state_data[(state_data["estado"] == location)]
    fig2 = go.Figure(layout={"template":"plotly_dark"})
    bar_plots = ["casosNovos", "obitosNovos"]

    if plot_type in bar_plots:
        fig2.add_trace(go.Bar(x=df_data_on_location["data"], y=df_data_on_location[plot_type]))
    else:
        fig2.add_trace(go.Scatter(x=df_data_on_location["data"], y=df_data_on_location[plot_type]))
    
    fig2.update_layout(
        paper_bgcolor="#242424",
        plot_bgcolor="#242424",
        autosize=True,
        margin=dict(l=10, r=10, b=10, t=10),
    )
    return fig2

@app.callback(
    Output("choropleth-map", "figure"), 
    [Input("date-picker", "date")]
)
def update_map(date):
    df_data_on_states = state_data[state_data["data"] == date]

    fig = px.choropleth_mapbox(
        df_data_on_states, 
        locations="estado", 
        geojson=geolocation, 
        center={
            "lat": LATITUDE, 
            "lon": LONGITUDE
        },
        zoom=4, 
        color="casosAcumulado", 
        color_continuous_scale="Redor", 
        opacity=0.55,
        hover_data={
            "casosAcumulado": True, 
            "casosNovos": True, 
            "obitosNovos": True, 
            "estado": False
        }
    )

    fig.update_layout(
        paper_bgcolor="#242424", 
        mapbox_style="carto-darkmatter", 
        autosize=True,
        margin=go.layout.Margin(l=0, r=0, t=0, b=0), 
        showlegend=False
    )
    
    return fig


@app.callback(
    Output("location-button", "children"),
    [
        Input("choropleth-map", "clickData"), 
        Input("location-button", "n_clicks")
    ]
)
def update_location(click_data, n_clicks):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if click_data is not None and changed_id != "location-button.n_clicks":
        state = click_data["points"][0]["location"]
        return "{}".format(state)
    else:
        return "BRASIL"

if __name__ == "__main__":
    app.run_server(debug=True)