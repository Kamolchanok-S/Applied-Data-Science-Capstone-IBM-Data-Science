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
print(spacex_df)

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36', 
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                    options=[
                                        {'label': 'All Sites', 'value': 'ALL'},
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                    ],
                                    value='ALL',
                                    id='site-dropdown',
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                                    value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
 # Function decorator to specify function input and output
@app.callback([Output(component_id='success-pie-chart', component_property='figure'),
               Output(component_id='success-payload-scatter-chart', component_property='figure')],
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])
def get_pie_chart(entered_site, payload_range):
    
    # Filter the dataframe based on payload range
    min_payload, max_payload = payload_range
    range_filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= min_payload) & 
                            (spacex_df['Payload Mass (kg)'] <= max_payload)]

    if entered_site == 'ALL':
        filtered_df = spacex_df.groupby('Launch Site')['class'].mean().reset_index()
        pie_fig = px.pie(filtered_df, values='class', # col name use value in each pie
            names='Launch Site',  # col name for each pies
            title='Total Success Launches By Site')
        
        scatter_df = range_filtered_df  # No site filter, show all
    else:
        # Filter dataframe for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]

        # Count occurrences of each class (0 = failed, 1 = success)
        class_counts = filtered_df['class'].value_counts(normalize=True).reset_index()
        # Replace numerical values with labels
        class_counts['class'] = class_counts['class'].replace({1: 'Success', 0: 'Failed'})
        
        pie_fig = px.pie(class_counts, values='proportion',
            names='class',
            title=f'Total Success Launches for site {entered_site}')
        
        scatter_df = range_filtered_df[range_filtered_df['Launch Site'] == entered_site]  # Filter by site
    
    scatter_fig = px.scatter(scatter_df, 
                             x='Payload Mass (kg)', 
                             y='class', 
                             color='Booster Version Category',  # Use booster version as color
                             title='Payload vs. Success',
                             labels={'class': 'Launch Outcome'},
                             color_discrete_sequence=px.colors.qualitative.Set1)

    
    return pie_fig, scatter_fig
 # return the outcomes piechart for a selected site
 
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output


# Run the app
if __name__ == '__main__':
    app.run_server()
