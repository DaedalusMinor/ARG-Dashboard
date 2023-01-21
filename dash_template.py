import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
import seaborn as sns
import plotly.express as px
import dash_leaflet as dl
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

num_players = 8001 # NUMBER OF PLAYERS
num_challenges_completed = 27805 # CHALLENGES COMPLETED

# MAIN NUMBERS TO DISPLAY
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
                dbc.CardBody([
                    html.H4('Total Challenges Completed', style=CARD_TEXT_STYLE),
                    html.P(num_challenges_completed, style=CARD_TEXT_STYLE),
                ]),
            ]
        ),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody([
                    html.H4('Card Title 3', className='card-title', style=CARD_TEXT_STYLE),
                    html.P('Sample text.', style=CARD_TEXT_STYLE),
                ]),
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
prison_dec_fig.update_layout(title_x=0.5)

# EXTRACTING DATA FOR SANKEY DIAGRAM, USED FOR CHALLENGE PROGRESSION
# FOR REFERENCE https://plotly.com/python/sankey-diagram/
import plotly.graph_objects as go
import urllib, json


frags = pd.read_csv('data/Boilermake Fake Data - CollectedDataFragment.csv')['DataFragmentId'].to_list()
print(frags)
idx = max(frags) * 2
labels = []
for i in range(0, max(frags) + 1):
    labels.append('Pass Task ' + str(i))
    labels.append('Fail Task ' + str(i))
print('LABELS:', labels)
sources = []
for i in range(0, idx + 1):
    sources.append(math.floor(i / 2) * 2)

print('SOURCES', sources)

targets = []
for i in range(0, idx + 1):
    targets.append(i + 2)
print('TARGETS:', targets)

values = []
counts = dict()
for i in frags:
    counts[i] = 0
for i in frags:
    counts[i]+=1
print('COUNTS:', counts)
for x in counts:
    values.append(counts[x])
    if x == 0:
        values.append(0)
    else:
        values.append(counts[x-1] - counts[x])
print('VALUES:', values)
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
sankey_event_completion_fig.update_layout(title_text="Challenge Progression", title_x=0.5)

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

# NFC TAG MAP OF FLOW
content_third_row = dbc.Row([
    dbc.Col([
        html.H4('NFC Tag Flow', className='card-title', style=CARD_TEXT_STYLE),
        dl.Map(dl.TileLayer(), center=[40.42868532391918, -86.91529455097324], style={'width': '100%', 'height': '100%'}, zoom=15,)],
        style={'margin-bottom': '5%', 'margin-top': '5%', 'margin-right': '5%', 'margin-left': '5%', 'width': '90%', 'height': '400px'}
    )
])

# NFC TAG MAP OF TAG STATUS
df = pd.read_csv('data/Boilermake Fake Data - DataFragment.csv')
lon_lat_df = df[['Name', 'Latitude', 'Longitude']].to_dict()
tag_locations = []
for i in range(len(lon_lat_df['Latitude'])):
    tag_locations.append([lon_lat_df['Name'][i],lon_lat_df['Latitude'][i], lon_lat_df['Longitude'][i]])

markers = []
# tag_locations = [[77, -119], [11, 151], [-94, 51], [-139, -138], [-178, -139], [77, 146], [-80, 28], [-11, -118]]
for tl in tag_locations:
    markers.append(
        dl.Marker(
            title=tl[0],
            position=(tl[1], tl[2]),
        )
    )
content_fourth_row = dbc.Row([
    dbc.Col([
        html.H4('NFC Tag Status', className='card-title', style=CARD_TEXT_STYLE),
        dl.Map([dl.TileLayer(), dl.MarkerClusterGroup(id='markers', children=markers)], center=[40.42868532391918, -86.91529455097324], style={'width': '100%', 'height': '100%'}, zoom=15,)],
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
