import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import seaborn as sns
import plotly.express as px
import dash_leaflet as dl
import geopandas as gpd
import dash_leaflet.express as dlx
import ssl
import math

ssl._create_default_https_context = ssl._create_unverified_context

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

import mysql.connector
cnx = mysql.connector.connect(user="ruben", password="3A5fpWfaRcg7r3V", host="argo.mysql.database.azure.com", database="app", port=3306, ssl_ca="{ca-cert filename}", ssl_disabled=False)
cursor = cnx.cursor()
query = "SELECT Id FROM players"
cursor.execute(query)
num_players = 0
for (id) in cursor:
  num_players += 1

cursor.close()
cnx.close()

players = pd.read_csv('data/Boilermake Fake Data - Player.csv')
collected_dfs = pd.read_csv('data/Boilermake Fake Data - CollectedDataFragment.csv')
player_ids = players['Id'].to_list()
cdf_per_player = {}
for id in player_ids:
    cdf_per_player[id] = len(collected_dfs.loc[collected_dfs['PlayerId'] == id].index)

cdf_per_player = sorted(cdf_per_player.items(), key=lambda x: x[1], reverse=True)
cdf_per_player_names = {}
for cdf_player in cdf_per_player:
    pn = players.loc[players['Id'] == cdf_player[0]]['Name'].iloc[0]
    cdf_per_player_names[pn] = cdf_player[1]
    
data_fragments = pd.read_csv("data/Boilermake Fake Data - DataFragment.csv")
frags = pd.read_csv("data/Boilermake Fake Data - CollectedDataFragment.csv")['DataFragmentId'].to_list()
num_challenges_completed = len(frags) # CHALLENGES COMPLETED

# EXTRACTING DATA FOR SANKEY DIAGRAM, USED FOR CHALLENGE PROGRESSION
# FOR REFERENCE https://plotly.com/python/sankey-diagram/
import plotly.graph_objects as go
import urllib, json
from dash import dash_table
# FIRST ROW OF GRAPHS
cdf_df = pd.DataFrame.from_dict(cdf_per_player_names, orient='index', columns=['Data Fragments'])
cdf_df['Player'] = cdf_df.index
datafragment_table = dash_table.DataTable(cdf_df.to_dict('records'), [{"name": 'Player', "id": 'Player'}, {"name": 'Data Fragments', "id": 'Data Fragments'}])
# MAIN NUMBERS TO DISPLAY
content_first_row = dbc.Row([
    dbc.Col(
        dbc.Card([
            dbc.CardBody([
                    html.H4('Number of Players', style=CARD_TEXT_STYLE),
                    html.P(num_players, style=CARD_TEXT_STYLE),
                ])
            ]),
        md=6
    ),
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody([
                    html.H4('Total Challenges Completed', style=CARD_TEXT_STYLE),
                    html.P(num_challenges_completed, style=CARD_TEXT_STYLE),
                ]),
            ]
        ),
        md=6
    )
])
# SUCCESS
# EXTRACTING DATA FOR PIE CHART, USED FOR PRISONER'S DILEMMA
df = pd.read_csv('data/Boilermake Fake Data - Player.csv')
count_dict = dict()
df.loc[df['IsBetrayer'] == 1] = 'Betrayer'
df.loc[df['IsBetrayer'] == 0] = 'Honest'
dfvals = df['IsBetrayer'].value_counts().to_frame()
dfvals.reset_index(inplace=True)
dfvals = dfvals.rename(columns = {'index':'Name'})

prison_dec_fig = px.pie(dfvals, values='IsBetrayer', names='Name', title='Prisoner\'s Dilemma Challenge Decisions')
prison_dec_fig.update_layout(title_x=0.5, font_size=16, font_color="#0074D9")

# EXTRACTING DATA FOR SANKEY DIAGRAM, USED FOR CHALLENGE PROGRESSION
# FOR REFERENCE https://plotly.com/python/sankey-diagram/
import plotly.graph_objects as go
import urllib, json

idx = max(frags) * 2
labels = []
for i in range(0, int(max(frags)) + 1):
    labels.append('Pass Task ' + str(i))
    labels.append('Fail Task ' + str(i))
sources = []
for i in range(0, int(idx) + 1):
    sources.append(math.floor(i / 2) * 2)

targets = []
for i in range(0, int(idx) + 1):
    targets.append(i + 2)

values = []
counts = dict()
for i in frags:
    counts[i] = 0
for i in frags:
    counts[i]+=1
for x in counts:
    values.append(counts[x])
    if x == 0:
        values.append(0)
    else:
        values.append(counts[x-1] - counts[x])
sankey_event_completion_fig = fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = labels,
      color = "blue"
    ),
    link = dict(
      source = sources, # indices correspond to labels, eg A1, A2, A1, B1, ...
      target = targets,
      value = values
  ))])
sankey_event_completion_fig.update_layout(title_text="Challenge Progression", font_size=16, font_color="#0074D9", title_x=0.5)

# FIRST ROW OF GRAPHS
content_second_row = dbc.Row(
    [
        # PIE CHART
        dbc.Col(
            dcc.Graph(id='graph_1', figure=prison_dec_fig, style=CARD_TEXT_STYLE), md=6
        ),
        # SANKEY DIAGRAM
        dbc.Col(
            dcc.Graph(id='graph_2', figure=sankey_event_completion_fig, style=CARD_TEXT_STYLE), md=6
        ),
    ]
)
# FIRST ROW OF GRAPHS
content_second_row = dbc.Row(
    [
        # PIE CHART
        dbc.Col(
            dcc.Graph(id='graph_1', figure=prison_dec_fig), md=6
        ),
        # SANKEY DIAGRAM
        dbc.Col(
            dcc.Graph(id='graph_2', figure=sankey_event_completion_fig), md=6
        ),
    ]
)

# NFC TAG MAP OF TAG STATUS
data_fragment_locations = data_fragments[['Latitude', 'Longitude']].to_numpy()
tag_locations = data_fragment_locations
patterns = [dict(offset='5%', repeat='10%')]
polyline = dl.Polyline(positions=tag_locations)
marker_pattern = dl.PolylineDecorator(children=polyline, patterns=patterns)
status_map = dl.Map([dl.TileLayer(), marker_pattern] +
    [dl.Circle(center=(tl[0], tl[1]), radius=10, color='rgb(0,256,0)', children=[dl.Popup('Status: Active')]) for tl in tag_locations], center=[40.423072485094345, -86.9227297175381], style={'width': '100%', 'height': '100%'}, zoom=15,)

content_third_row = dbc.Row([
    dbc.Col([
        html.H4('NFC Tag Status', className='card-title', style=CARD_TEXT_STYLE),
        status_map],
        style={'margin-bottom': '5%', 'margin-top': '5%', 'margin-right': '5%', 'margin-left': '5%', 'width': '90%', 'height': '400px'})
])

content = html.Div(
    [
        html.H2('Analytics', style=TEXT_STYLE),
        html.Hr(),
        content_first_row,
        content_second_row,
        content_third_row,
        html.H4('Leaderboard', style=CARD_TEXT_STYLE),
        datafragment_table,
    ],
    style=CONTENT_STYLE
)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([content])

if __name__ == '__main__':
    app.run_server(port='8085')
