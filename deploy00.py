import dash

import plotly.express as px

import pandas as pd
import json
import dash_bootstrap_components as dbc
from dash import Dash, dash_table, dcc,html, Input,Output,callback,State,no_update
import geopandas as gpd
import dash_ag_grid as dag
import dash_player as player
#read data
from pandas import DataFrame
from plotly.graph_objs import Figure

MAP_URL = 'https://raw.githubusercontent.com/datasett/maps/master/norway/data/2020/counties_2020_s_geojson.json'
gdf = gpd.read_file(MAP_URL)
gdf1=gdf.drop('oppdateringsdato',axis=1)
geojson = json.loads(gdf1.to_json())
dft=pd.read_excel('dv_0111.xlsx')
dft_sorted = dft.sort_values(by='k_n', ascending=True)
dft_sorted=dft_sorted.reset_index(drop=True)
dft_sorted.iloc[0, -1] = '0301'
df = dft_sorted.drop([18,68,79])# får ike med ' KVITSØY ', ' TRÆNA',' RØSTnoe feil med geosjon file
df=df.reset_index(drop=True)


dft01=pd.read_excel('dv_011.xlsx')
dft01_sorted = dft01.sort_values(by='k_n', ascending=True)
dft01_sorted=dft01_sorted.reset_index(drop=True)
dft01_sorted.iloc[0, 0] = '0301'
df00 = dft01_sorted.drop([18,68,79])


print(df00.head(3))





app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server=app.server
#app = dash.Dash(__name__, suppress_callback_exceptions=True)




def fig_map (df):
    custom_colorscale = [
        [0.0, '#aaf0aa'],
        [0.0004, 'gray'],
        [0.00175,'yellow'],
        [0.00875,'orange'],
        [1.0, 'red']  # High values
    ]

    # Apply the color mapping to the 'tildelt_beløp' column


    fig01 = px.choropleth(df, geojson=json.loads(gdf1.to_json()),
                      color="tildelt_beløp",
                      hover_name='søker_poststed',
                      color_continuous_scale=custom_colorscale,

                      locations="k_n", featureidkey="properties.kommunenummer",
                      projection="orthographic"
                      #projection="mercator"

                      )
    annotations = [dict(
        x=0.55,
        y=0.48,
        xref='paper',
        yref='paper',
        text='klikk på kommune',
        showarrow=False,
        font=dict(size=10),
    )]


    #fig01.update_geos(fitbounds="geojson", visible=False)
    #fig01.update_layout(margin={"r":100, "t": 0, "l": 0, "b": 0})
    #fig01.update_traces(showlegend=False)
    #fig01.update_layout(coloraxis_colorbar=None)

    fig01.update_layout(
        coloraxis_showscale=False,  # Remove color scale legend
        geo=dict(
            fitbounds="geojson",  # Fit the map to GeoJSON data
            visible=False,  # Hide the base map

        ),
        margin={"r": 100, "t": 0, "l": 0, "b": 0},  # Adjust margins
        #width=800,
        #height=400,
        #legend=dict(y=1.05)  # Adjust the position of the legend
    )
    fig01.update_layout(geo=dict(showcoastlines=False))
    fig01.update_traces(marker=dict(opacity=0.6))
    fig01.update_layout(annotations=annotations)
    return fig01





#calbacken
@callback(
    Output(component_id='my-graph-container', component_property='children'),
    Input(component_id='map_plot1', component_property='clickData')
)


def update_graph(clickData):
    if clickData:
        city = clickData['points'][0]['hovertext']
        print(city)

        dff00 = df00[df00['søker_poststed'] == city]
        print(dff00.head())
        fig1 = px.histogram(dff00,  x='søker_poststed',y=['drift','små_nystartede','norsk_opplæring','kommunal_tilskudd','NRM','IFO'])
        return dcc.Graph(figure=fig1)
    else:
        no_update

df = pd.read_excel('dv_000.xlsx', sheet_name='Ark1')
preselected_columns = ['tilskuddsordning', 'tittel','søker_navn','tildelt_beløp']
# Initial column definitions
column_defs = [{"headerName": col, "field": col} for col in df.columns]



app.layout = dbc.Container([

    html.H4('IMDis fordelinger av tilskudd til frivillige organisasjoner i 2023'),

    html.H6('IMDis tilskudd generer aktiviter i hele landet, tilskuddsmottakeres kommunene har en annen farge enn grønt.'),

    html.Div(

        dcc.Graph(id='map_plot1', figure=fig_map(df00)
        ),
        style={'width':'75%','display': 'inline-block'}
    ),

    html.Div(style={'width': '25%' ,  'display': 'inline-block'}, id='my-graph-container'),
    html.Div([
        html.H4("Dette gjør IMDi"),
        player.DashPlayer(
            id='video-player',
            url="https://vimeo.com/900763561",  # Replace with the path or URL to your video file
            controls=True,
            width="20%",
            height="150px",
        )


    ]),

    dcc.Markdown('# Hvem har fått tilskudd i 2023' , style={'textAlign':'center'}),




    html.Div([
        dag.AgGrid(
            id='ag-grid',
            columnDefs=column_defs,
            rowData=df.to_dict('records'),
            defaultColDef={'sortable':True,'resizable':True,'filter':True}
            ),
    dcc.Dropdown(
        id='dropdown',
        options=[{'label': col, 'value': col} for col in df.columns],
        multi=True,
        value=df.columns,  # Initially all columns are visible
        placeholder="Select your columns"
        ),
    ]),
])

@app.callback(
    Output('ag-grid', 'columnDefs'),
    Input('dropdown', 'value')
)
def update_columns(selected_columns):
    updated_column_defs = [{"headerName": col, "field": col} for col in selected_columns]
    return updated_column_defs




if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)


#https://www3.cs.stonybrook.edu/~mueller/teaching/cse332/Dash%20Intro.pdf
#https://community.plotly.com/t/use-hoverdata-and-clickdata-from-scatter-plot-to-interact-with-datatable/43937/5
#https://www.youtube.com/watch?v=pNMWbY0AUJ0&t=157s about call back
#https://campus.datacamp.com/courses/building-dashboards-with-dash-and-plotly/styling-dash-apps?ex=1 about text in dash
#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 API keys ChatGPT
#https://community.plotly.com/t/want-to-update-table-based-on-clickdata-in-map/38975/3
