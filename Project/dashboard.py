
import dash
import dash_leaflet as dl
import pandas as pd
from dash import dash_table, ctx
from dash.dependencies import Input, Output
from dash import html, dcc

import plotly.express as px
from plotly.express import pie

# Import of animal_shelter module with MongoDB CRUD operations
from animal_shelter import AnimalShelter

###########################
# Data Manipulation / Model
###########################

# DB Credentials
username = "aacuser"
password = "superSecret"
shelter = AnimalShelter(username, password)

# Class method returning cursor object
df = pd.DataFrame.from_records(shelter.read_all())

#########################
# Dashboard Layout / View
#########################

# Using Dash to initialize an app server
app = dash.Dash(__name__, title="Animal Shelter")

# Begin building dashboard layout
app.layout = html.Div([
    html.Div(id='hidden-div', style={'display':'none'}),
    # Unique identifier of dashbord
    html.Center(html.B(html.H1('SNHU CS-340 Michael Kennedy'))),
    html.Hr(),
    html.Div(
        # Grazioso Salvare with hyperlink to http://www.snhu.edu
        html.A(
            href="http://www.snhu.edu",
            children=[
                html.Img(
                    src='assets/gs-logo.png',
                ),
            ],
        ),
        # Center logo
        style={
            'textAlign': 'center'
        }
    ),
    html.Hr(),
    # Row of buttons to be used for filtering
    html.Div(className='row',
            style={
                'display': 'flex'
            },
            children=[
                html.Button(id='submit-button-water', n_clicks=0, children='Water'),
                html.Button(id='submit-button-mtn-wild', n_clicks=0, children='Mountain or Wilderness'),
                html.Button(id='submit-button-dis-ind', n_clicks=0, children='Disaster or Individual Tracking'),
                html.Button(id='submit-button-reset', n_clicks=0, children='Reset')
            ]),
    html.Div(
        # Datatable div populated with data based on filters applied
        style={
            'width': '100%'
        },
        children=[
            dash_table.DataTable(
                id='datatable-id',
                style_header={
                    'backgroundColor': 'rgb(210, 210, 210)',
                    'color': 'black',
                    'fontWeight': 'bold'
                },
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                page_current=0,
                page_size=10,
                filter_action='native',
                sort_action='native',
                row_selectable='single',
                selected_rows=[0],
            ),
        ]
    ),
    html.Br(),
    html.Hr(),
    # Div containing map and pie chart
    html.Div(className='row',
         style={'display' : 'flex'},
             children=[
        # Map responding to selected row of data table
        html.Div(
            id='map-id',
            className='col s12 m6',
            ),
        # Pie chart responding to filters applied
        html.Div(
            id='graph-id',
            className='col s12 m6',
            children=[dcc.Graph(id="graph")]
            ),
        ])
])

#############################################
# Interaction Between Components / Controller
#############################################
#This callback will highlight a row on the data table when the user selects it
@app.callback(
    Output('datatable-id', 'style_data_conditional'),
    [Input('datatable-id', 'selected_rows')]
)
def update_styles(selected_rows):
    if selected_rows != None:
        return [{
            'if': {
                'row_index': i
            },
            'background_color': '#D2F3FF'
        } for i in selected_rows]
    else:
        return

# This callback will place a marker on the map based on the selected row
@app.callback(
    Output('map-id', "children"),
    [
        Input('datatable-id', "selected_rows"),
        Input('datatable-id', "derived_viewport_data")
    ]
)
def update_map(indexes, data):
    if indexes != None:
        dff = pd.DataFrame.from_dict(data)
        index = indexes[0]
        latitude = dff[index::]['location_lat'].values[0]
        longitude = dff[index::]['location_long'].values[0]
        return [
            dl.Map(
                style={
                    'width': '1000px',
                    'height': '500px'
                },
                center=[
                    latitude,
                    longitude,
                ],
                zoom=10,
                children=[
                    dl.TileLayer(id="base-layer-id"),
                    dl.Marker(
                        position=[
                            latitude,
                            longitude,
                        ],
                        children=[
                            dl.Tooltip(dff[index::]['name'].values[0]),
                            dl.Popup([
                                html.H1("Animal Name"),
                                html.P(dff[index::]['name'].values[0]),
                            ])
                        ]
                    )
                ]
            )
        ]
    else:
        return
    
# This callback will update the data table based on the filters applied from these buttons
@app.callback(
    Output('datatable-id', "data"),
    [
        Input(component_id='submit-button-water', component_property='n_clicks'),
        Input(component_id='submit-button-mtn-wild', component_property='n_clicks'),
        Input(component_id='submit-button-dis-ind', component_property='n_clicks'),
        Input(component_id='submit-button-reset', component_property='n_clicks')
    ])
def on_click(btn1, btn2, btn3, btn4):
    button_id = ctx.triggered_id

    # This button will reset filter to return all results
    if (button_id == None or button_id == "submit-button-reset"):
        df = pd.DataFrame.from_records(shelter.read_all())
    # Filter for water dogs
    elif (button_id == "submit-button-water"):
        df = pd.DataFrame(list(shelter.read({
            'animal_type': 'Dog', 
            'breed': {
                '$in': [
                    'Labrador Retriever Mix', 'Chesapeake Bay Retriever', 'Newfoundland'
                ]
            }, 
            'sex_upon_outcome': 'Intact Female', 
            'age_upon_outcome_in_weeks': {
                '$gte': 26, 
                '$lte': 156
            }
        })))
    # Filter for mountain and wilderness dogs
    elif (button_id == "submit-button-mtn-wild"):
        df = pd.DataFrame(list(shelter.read({
            'animal_type': 'Dog', 
            'breed': {
                '$in': [
                    'German Shepherd', 'Alaskan Malamute', 'Old English Sheepdog', 'Siberian Husky', 'Rottweiler'
                ]
            }, 
            'sex_upon_outcome': 'Intact Male', 
            'age_upon_outcome_in_weeks': {
                '$gte': 26, 
                '$lte': 156
            }
        })))
    # Filter for disaster and individual tracking dogs
    elif (button_id == "submit-button-dis-ind"):
        df = pd.DataFrame(list(shelter.read({
            'animal_type': 'Dog', 
            'breed': {
                '$in': [
                    'Doberman Pinscher', 'German Shepherd', 'Golden Retriever', 'Bloodhound', 'Rottweiler'
                ]
            }, 
            'sex_upon_outcome': 'Intact Male', 
            'age_upon_outcome_in_weeks': {
                '$gte': 20, 
                '$lte': 300
            }
        }))) 
    return df.to_dict('records')

# This callback will update pie chart based on filters applied to all data
@app.callback(
    Output("graph", "figure"), 
    [Input('datatable-id', "derived_virtual_data")])
def generate_chart(values):
    df = pd.DataFrame.from_dict(values)
    fig = pie(
        data_frame=df['outcome_type'],
        names=df['outcome_type'].name,
        hole=.3
    )
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)