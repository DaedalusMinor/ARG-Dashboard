import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import seaborn as sns
import plotly.express as px
import dash_leaflet as dl

# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '20%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa'
}

# the style arguments for the main content page.
CONTENT_STYLE = {
    'margin-left': '5%',
    'margin-right': '5%',
    'padding': '20px 10p'
}

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#191970'
}

CARD_TEXT_STYLE = {
    'margin-left': '5%',
    'margin-right': '5%',
    'textAlign': 'center',
    'color': '#0074D9'
}

num_players = 8001 # NUMBER OF PLAYERS
num_challenges_completed = 27805 # CHALLENGES COMPLETED

content_first_row = dbc.Row([
    dbc.Col(
        dbc.Card([
            dbc.CardBody([
                    html.H4('Number of Players', style=CARD_TEXT_STYLE),
                    html.P(num_players, style=CARD_TEXT_STYLE),
                ])
            ]),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4('Total Challenges Completed', style=CARD_TEXT_STYLE),
                        html.P(num_challenges_completed, style=CARD_TEXT_STYLE),
                    ]
                ),
            ]

        ),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4('Card Title 3', className='card-title', style=CARD_TEXT_STYLE),
                        html.P('Sample text.', style=CARD_TEXT_STYLE),
                    ]
                ),
            ]

        ),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4('Card Title 4', className='card-title', style=CARD_TEXT_STYLE),
                        html.P('Sample text.', style=CARD_TEXT_STYLE),
                    ]
                ),
            ]
        ),
        md=3
    )
])

df = px.data.gapminder().query("year == 2007").query("continent == 'Europe'")
df.loc[df['pop'] < 2.e6, 'country'] = 'Other countries' # Represent only large countries
prison_dec_fig = px.pie(df, values='pop', names='country', title='Prisoner\'s Dilemma Challenge Decisions')
prison_dec_fig.update_layout(title_x=0.5)

import plotly.graph_objects as go
import urllib, json

url = 'https://raw.githubusercontent.com/plotly/plotly.js/master/test/image/mocks/sankey_energy.json'
response = urllib.request.urlopen(url)
data = json.loads(response.read()) # replace with your own data source

node = data['data'][0]['node']
node['color'] = [
    f'rgba(255,0,255,0.8)' 
    if c == "magenta" else c.replace('0.8', '0.9') 
    for c in node['color']]

link = data['data'][0]['link']
link['color'] = [
    node['color'][src] for src in link['source']]

sankey_event_completion_fig = go.Figure(go.Sankey(link=link, node=node))
sankey_event_completion_fig.update_layout(title_text="Challenge Progression", title_x=0.5)

map = dbc.Col()
content_second_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_1', figure=prison_dec_fig), md=6
        ),
        dbc.Col(
            dcc.Graph(id='graph_2', figure=sankey_event_completion_fig), md=6
        ),
    ]
)

content_third_row = dbc.Row([
    dbc.Col([
        dl.Map(dl.TileLayer(), center=[40.42868532391918, -86.91529455097324], style={'width': '100%', 'height': '100%'}, zoom=15,)],
        style={'margin-bottom': '5%', 'margin-top': '5%', 'margin-right': '5%', 'margin-left': '5%', 'width': '90%', 'height': '400px'}
    )
])

content_fourth_row = dbc.Row([
    dbc.Col([
        dl.Map(dl.TileLayer(), center=[40.42868532391918, -86.91529455097324], style={'width': '100%', 'height': '100%'}, zoom=15,)],
        style={'margin-bottom': '5%', 'margin-top': '5%', 'margin-right': '5%', 'margin-left': '5%', 'width': '90%', 'height': '400px'})
])

content = html.Div(
    [
        html.H2('Analytics', style=TEXT_STYLE),
        html.Hr(),
        content_first_row,
        content_second_row,
        content_third_row,
        content_fourth_row
    ],
    style=CONTENT_STYLE
)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([content])

if __name__ == '__main__':
    app.run_server(port='8085')
