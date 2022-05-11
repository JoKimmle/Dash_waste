import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go

app = dash.Dash(__name__)
server = app.server


# function to select data:
def SelectData(DF, flow, time=0, waste="0", geo="0"):
    """
    get selected data from merged_df
    PARAMETER:
    DF: var (Dataframe)
    flow: str
    time: int, optional
    waste: str, optional
    geo: str, optional
    RETURNS:
    dataframe of selected parameters
    """
    if (time != 0 and waste != "0" and geo != "0"):
        selected_data_df = DF[(DF.time == time) & (DF.stk_flow_label == flow)
                              & (DF.waste_label == waste) & (DF.geo == geo)]
        #print("not restricted")

    elif (time == 0 and waste != "0" and geo != "0"):
        selected_data_df = DF[(DF.stk_flow_label == flow) & (DF.waste_label == waste)
                              & (DF.geo == geo)]
        #print("time unrestricted")

    elif (time != 0 and waste == "0" and geo != "0"):
        selected_data_df = DF[(DF.time == time) & (DF.stk_flow_label == flow)
                              & (DF.geo == geo)]
        #print("waste unrestricted")

    elif (time != 0 and waste != "0" and geo == "0"):
        selected_data_df = DF[(DF.time == time) & (DF.stk_flow_label == flow)
                              & (DF.waste_label == waste)]
        #print("geo unrestricted")

    elif (time == 0 and waste == "0" and geo != "0"):
        selected_data_df = DF[(DF.stk_flow_label == flow) & (DF.geo == geo)]
        #print("time & waste unrestricted")

    elif (time == 0 and waste != "0" and geo == "0"):
        selected_data_df = DF[(DF.stk_flow_label == flow) & (DF.waste_label == waste)]
        #print("time and geo unrestricted")

    elif (time != 0 and waste == "0" and geo == "0"):
        selected_data_df = DF[(DF.time == time) & (DF.stk_flow_label == flow)]
        #print("waste and geo unrestricted")

    else:
        selected_data_df = DF[(DF.stk_flow_label == flow)]
        #print("time, waste & geo unrestricted")

    return selected_data_df




# https://stooq.com/

df = pd.read_csv("full_df.csv")

#print(df[:15])




# https://www.bootstrapcdn.com/bootswatch/
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )


# Layout section: Bootstrap (https://hackerthemes.com/bootstrap-cheatsheet/)
# ************************************************************************
app.layout = dbc.Container([

    dbc.Row(
        dbc.Col(html.H1("Waste Import&Export from and to Europe",
                        className='text-center text-primary mb-4'),
                width=12)
    ),
    dbc.Row(
        dcc.Slider(2004,2023,1,marks={
        2004: {'label':'2004'},
        2005: {'label':'`05'},
        2006: {'label':'`06'},
        2007: {'label':'`07'},
        2008: {'label':'`08'},
        2009: {'label':'`09'},
        2010: {'label':'`10'},
        2011: {'label':'`11'},
        2012: {'label':'`12'},
        2013: {'label':'`13'},
        2014: {'label':'`14'},
        2015: {'label':'`15'},
        2016: {'label':'`16'},
        2017: {'label':'`17'},
        2018: {'label':'`18'},
        2019: {'label':'`19'},
        2020: {'label':'`20'},
        2021: {'label':'pred `21', 'style': {'color': '#f50'}},#für prediction rot
        2022: {'label':'pred `22', 'style': {'color': '#f50'}},
        2023: {'label':'pred `23', 'style': {'color': '#f50'}},
        },
        value=2004, id="year_slider")
    ),

    dbc.Row([

        dbc.Col([
            dcc.Dropdown(id='waste_dpdn', multi=True, value=['Cu,Al,Ni', 'Iron&Steel', 'Precious Metals', 'Paper',
                                                             'Plastics','Glass', 'Wood', 'Textile', 'Animal&Veg',
                                                             'Others'],
                         options=[{'label':x, 'value':x}
                                  for x in sorted(df['waste_label'].unique())],
                         ),
            dcc.Graph(id='geo-fig', figure={})
        ],# width={'size':5, 'offset':1, 'order':1},
           xs=6, sm=6, md=6, lg=6, xl=6
        ),



        dbc.Col([
            dcc.RadioItems(id='radio_but',
                           options={
                               'Imports': 'Imports',
                               'Exports': 'Exports',
                           },
                           value='Exports',
                           inline=True),

            dcc.Graph(id='pie-fig2', figure={})  # children=figure
        ],  # width={'size':5, 'offset':0, 'order':2},
            xs=6, sm=6, md=6, lg=6, xl=6
        ),


    ], justify='start'),  # Horizontal:start,center,end,between,around

], fluid=True)


# Callback section: connecting the components
# ************************************************************************
# Geo Plot
@app.callback(
    Output('geo-fig', 'figure'),
    Input('waste_dpdn', 'value'),
    Input('year_slider', 'value'),
    Input('radio_but', 'value'),
)
def update_graph(waste_chosen,year_slider,radio_but):
    dfc = SelectData(DF=df, flow=radio_but, time=year_slider)
    dff = dfc[dfc.waste_label.isin(waste_chosen)]
    #dff = df

    figgeo = px.scatter_geo(dff, locations="geo",
                   size="Tsd_Euro",# animation_frame="time",
                   projection="natural earth", size_max=70,
                   hover_name="partner_label", width=800, height=600,
                   color="waste_label",
                   title="Price of Waste "+str(radio_but)+" Map"
                   )
    figgeo.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.0,
        xanchor="right",
        x=1
    ))

    return figgeo


# pie diagramm euro:
@app.callback(
    Output('pie-fig2', 'figure'),
    Input('geo-fig', 'hoverData'),
    Input('year_slider', 'value'),
    Input('radio_but', 'value'),
)
def update_side_graph(hoverData, year_slider, radio_but):
    if hoverData is None:
        loc="ZAF"
    else:
        loc = hoverData['points'][0]['location']
    yearselected = year_slider
    #loc = hoverData['points'][0]['location']
    dff2 = SelectData(DF=df, flow=radio_but, time=yearselected, geo=loc)

    labels = dff2["waste_label"].to_list()
    valuesEu = dff2["Tsd_Euro"].to_list()
    valuesTo = dff2["Tonnes"].to_list()

    trace1 = go.Pie(
        hole=0.5,
        sort=False,
        direction='clockwise',
        domain={'x': [0.15, 0.85], 'y': [0.15, 0.85]},
        values=valuesTo,
        labels=labels,
        text = ['{} Tonnes'.format(i) for i in valuesTo],
        textinfo='text',
        textposition='inside',
        marker={'line': {'color': 'white', 'width': 1}}
    )

    trace2 = go.Pie(
        hole=0.7,
        sort=False,
        direction='clockwise',
        values=valuesEu,
        labels=labels,
        text = ['{} Tsd Euro'.format(i) for i in valuesEu],
        textinfo='text',
        textposition='outside',
        marker={'line': {'color': 'white', 'width': 1}}
    )

    fig2 = go.FigureWidget(data=[trace1, trace2])
    fig2.update_layout(showlegend=True, title="Weight (inner circle) & Cost (outer circle) of waste types for: "+ str(loc))

    return fig2

# ************************************************************************


if __name__=='__main__':
    app.run_server(debug=True, port=3221)
