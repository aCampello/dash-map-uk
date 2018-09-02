import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import json

app = dash.Dash()
app.title = 'Map of Immigration'
server = app.server

# Main dropdown buttons
dictionaries_of_years = [{'label': year, 'value': year} for year in np.arange(2005, 2018)]
dictionaries_of_outcomes = [{'label': 'Granted', 'value': 'granted'}, {'label': 'Rejected', 'value': 'rejected'}]

dropdown_years = dcc.Dropdown(id='year_to_display', options=dictionaries_of_years, value='2016')
radio_items_type_of_outcome = dcc.RadioItems(id='outcome_of_application', options=dictionaries_of_outcomes,
                                             value='granted', labelStyle={'display': 'inline-block',
                                                                          'margin-right': 10,
                                                                          'margin-top': 30})

# The html structure of the file
# Loads/cache data in a hidden div for more reative app
app.layout = html.Div([html.Div(id="data-loading", style={'display': 'none'}),
                       html.Div([html.H4('Map of Legal Immigration in the UK', style={"margin-bottom": 0,
                                                                                      "margin-top": "30px",
                                                                                      "padding": 0}),
                                 html.H5(['Source: ', html.A('Home Office', href="https://www.gov.uk/government/"
                                                                                 "publications/immigration-statistics"
                                                                                 "-october-to-december-"
                                                                                 "2016/work#data-tables")],
                                         style={"margin-top": 0, "padding": 0})],
                                style={'text-align': 'center'}),
                       html.Hr(),
                       html.Div([html.Div([html.Label('Year'),
                                           dropdown_years,
                                           html.Label('Type of Visa(*)',style={"margin-top": "30px"}),
                                           html.Div([dcc.Dropdown(id='type_of_visa_to_display',
                                                                  options=[{'label': 'Work', 'value': 'work'},
                                                                           {'label': 'Study', 'value': 'study'},
                                                                           {'label': 'All (incl. visitors)', 'value': 'all'}],
                                                                  value='work')],
                                                    id='type_of_visa_to_display_div'),
                                           html.P(''), radio_items_type_of_outcome],
                                          className="three columns", style={"margin-top": 40}),
                                 html.Div([dcc.Graph(id='map')], className="three columns")],
                                className="row"),
                    html.Hr(),
                       html.Div([html.Div([dcc.Graph(id='bar-plot', config={"displayModeBar": False},
                                                     style={"margin-left": 0})], className="five columns"),
                                 html.Div([dcc.Graph(id='graph-total', config={"displayModeBar": False})],
                                          className="seven columns")],
                                className="row"),
                       html.Hr(),
                       html.Div(  # There is a bug with markdown that does not allow me to indent it PEP-8 properly
                       dcc.Markdown('''
(*) Work visas include mainly High-value (Tier 1), Skilled (Tier 2), Youth mobility and
temporary workers (Tier 5), as well as non-PBS/Other work visas.
Student visas include mainly Tier 4 (excluding short-term study). 
Sources: [gov.uk work-visas](https://www.gov.uk/browse/visas-immigration/work-visas) and
[gov.uk student-visas](https://www.gov.uk/browse/visas-immigration/student-visas).

(**) Rejected applications are only available per country including all categories, and visitors. A FOIA request has 
been made for the missing information.                    
                       ''')
                       )],
                      className='container')


@app.callback(dash.dependencies.Output('type_of_visa_to_display', 'options'),
              [dash.dependencies.Input('outcome_of_application', 'value')])
def disable_types(selected_outcome):
    """
    Callback to disable "work of study" in case of "rejected outcomes
    :param selected_outcome:
    :return:
    """
    if selected_outcome == "rejected":
        dictionaries_of_visas = [{'label': 'Work', 'value': 'work', 'disabled': True},
                                 {'label': 'Study', 'value': 'study', 'disabled': True},
                                 {'label': 'All (incl. visitors)', 'value': 'all'}]
    else:
        dictionaries_of_visas = [{'label': 'Work', 'value': 'work'}, {'label': 'Study', 'value': 'study'},
                                 {'label': 'All (incl. visitors)', 'value': 'all'}]

    return dictionaries_of_visas


@app.callback(dash.dependencies.Output('type_of_visa_to_display', 'value'),
              [dash.dependencies.Input('outcome_of_application', 'value')])
def disable_types(selected_outcome):
    """
    Callback to pass to "all" in case of "rejected outcomes"
    :param selected_outcome:
    :return:
    """

    return "all"


@app.callback(dash.dependencies.Output('data-loading', 'children'),
              [dash.dependencies.Input('year_to_display', 'value'),
               dash.dependencies.Input('type_of_visa_to_display', 'value'),
               dash.dependencies.Input('outcome_of_application', 'value')])
def load_data(selected_year, selected_type, selected_outcome):
    """

    Callback to load data from dataframe and serve it to a hidden div, jsonified.

    :param selected_year: int: Year of visa
    :param selected_type: str: type of visa (Tier 2 or Tier 4)
    :param selected_outcome: str: granted or rejected

    :return: list [df, filters]
             df is a jsonified dataframe after applying all the filters and
             filters is a json with information about the applied filters
    """

    filters = {"selected_year": selected_year,
               "selected_type": selected_type,
               "selected_outcome": selected_outcome}

    # Reads the correct dataframe
    if selected_outcome == 'rejected':
        file_to_read = 'map_of_immigration_rejected_' + str(selected_year) + '.csv'
    else:
        file_to_read = 'map_of_immigration_' + str(selected_type) + '_' + str(selected_year) + '.csv'

    data_frame = pd.read_csv('data/' + file_to_read, index_col=0)

    # Dumps a json to be able to share across divs
    return json.dumps({"df": data_frame.to_json(orient='split'), "filters": filters})


@app.callback(dash.dependencies.Output('map', 'figure'),
              [dash.dependencies.Input('data-loading', 'children')])
def update_map(hidden_div):
    """
    Updates the map based on the input hidden div

    :param data_frame:
    :return:
    """
    # Loads the json

    hidden_div = json.loads(hidden_div)

    data_frame = pd.read_json(hidden_div['df'], orient='split')
    filters = hidden_div['filters']

    selected_year = filters.get("selected_year", 2016)
    selected_type = filters.get("selected_type", "work")
    selected_outcome = filters.get("selected_outcome", "granted")
    selected_exclusion = filters.get('selected_exclusions', [])

    total = data_frame['Total'].sum()

    plotly_data = go.Data([dict(
        type='choropleth',
        locations=data_frame['country_code'],
        z=data_frame['Total'],
        text=data_frame['Country'] + '<br>' + data_frame['Geographical region'],
        colorscale='Blues',
        hoverinfo="location+z+text",
        reversescale=True,
        marker=dict(
            line=dict(
                color='rgb(180,180,180)',
                width=1
            )),
        colorbar=dict(
            thickness=10,
            lenmode="fraction",
            len=0.8,
            title='Total {} visas'.format(selected_type))
    ), dict(
        type='choropleth',
        locations=['GBR'],
        z=[1],
        text=['United Kingdom'],
        colorscale=[[0, "rgb(255, 10, 17)"], [1, "rgb(255, 10, 17)"]],
        showscale=False)])

    selected_exclusion_to_display = ('<br>(excluding countries from the {})'.format(selected_exclusion[0])
                                     if len(selected_exclusion) > 0 else '')
    selected_outcome_to_display = (selected_outcome + ' ' if selected_outcome != 'all' else '')
    plotly_layout = go.Layout(dict(title='Total number of {}{} visas in {}: {:,}.{}'.format(selected_outcome_to_display,
                                                                                            selected_type,
                                                                                            selected_year,
                                                                                            total,
                                                                                            selected_exclusion_to_display),
                                   width=800, height=400, margin=dict(l=20, r=0, b=0, t=80),
                                   geo=dict(showframe=False, showcoastlines=False,
                                            projection=dict(type='natural earth'),
                                            center={"lon": 0, "lat": 5})))

    return dict(data=plotly_data, layout=plotly_layout)


@app.callback(dash.dependencies.Output('bar-plot', 'figure'),
              [dash.dependencies.Input('data-loading', 'children')])
def plot_sorted_countries(hidden_div):
    """
    Callback to update a list of top 8 countries with respect to data-loading stats

    :param hidden_div: hidden div with data information
    :return: plotly barplot
    """
    hidden_div = json.loads(hidden_div)

    data_frame = pd.read_json(hidden_div['df'], orient='split')
    filters = hidden_div['filters']

    sorted_countries = data_frame.sort_values(by='Total', ascending=False)[:8][['Total', 'Country']].get_values()[::-1]

    plotly_data = [go.Bar(
            x=sorted_countries[:, 0],
            y=sorted_countries[:, 1],
            orientation='h',
            marker={'color': 'rgb(16, 39, 206)'},
            opacity=0.7
    )]

    plotly_layout = go.Layout(dict(title='Top countries'))

    return dict(data=plotly_data, layout=plotly_layout)


@app.callback(dash.dependencies.Output('graph-total', 'figure'),
              [dash.dependencies.Input('type_of_visa_to_display', 'value')])
def plot_total_graph(selected_type):
    """
    Callback to update the graph

    :param selected_type:
    :return: plotly scatter
    """
    data_frame = pd.read_csv('data/total_year_{}.csv'.format(selected_type), index_col=0)

    x = data_frame.index
    y = data_frame['Total'].get_values()

    plotly_data = [go.Scatter(x=x, y=y, line={'color': 'rgb(16, 39, 190)'})]
    plotly_layout = go.Layout(dict(title="Total number of {} visas per year".format(selected_type)), xaxis={"tickangle": -60,
                                                                                   "tickmode": "array",
                                                                                   "tickvals": np.arange(2005, 2017)})

    return dict(data=plotly_data, layout=plotly_layout)


# Adds skeleton for a nicer template
app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})

if __name__ == '__main__':
    app.run_server(port=8060, debug=True)