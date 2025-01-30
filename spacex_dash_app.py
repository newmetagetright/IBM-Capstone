# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown to select launch site
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL', placeholder="Select Launch Site", searchable=True
    ),
    html.Br(),

    # Pie chart for launch success
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # Payload range slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # Scatter plot for correlation between payload and success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# Callback to update the pie chart based on selected site
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='class', 
                     names='Launch Site', 
                     title='Total Success Launches By Site')
        return fig
    else:
                # For a specific site, filter by that site and show Success/Failure breakdown
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(filtered_df,
                     names='class',  # 0 = Failure, 1 = Success
                     title=f'Success vs Failure for {entered_site}',
                     labels={0:'Failure',1:'Success'},  
                     color='class',  # Color based on success/failure
                     )
        return fig


# Callback to update scatter plot based on selected site and payload range
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value')
)
def update_scatter_chart(entered_site, payload_range):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        scatter = px.scatter(
            filtered_df[(filtered_df['Payload Mass (kg)'] >= payload_range[0]) & 
                        (filtered_df['Payload Mass (kg)'] <= payload_range[1])],
            x='Payload Mass (kg)', y='class', 
            color='Booster Version Category',
            title='Correlation between Payload and Success for all sites'
        )
        return scatter
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        scatter = px.scatter(
            filtered_df[(filtered_df['Payload Mass (kg)'] >= payload_range[0]) & 
                        (filtered_df['Payload Mass (kg)'] <= payload_range[1])],
            x='Payload Mass (kg)', y='class', 
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for {entered_site}'
        )
        return scatter


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8070)
