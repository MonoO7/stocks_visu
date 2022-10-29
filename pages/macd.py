# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output, callback
import dash
import plotly.express as px
import pandas as pd
import yfinance as yf
import quandl
import plotly.io as pio
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import datetime as dt
from pandas_datareader import data as web
from dateutil.relativedelta import relativedelta
import pandas_ta as ta
from plotly.subplots import make_subplots




dash.register_page(__name__,title='MACD & Moving Average',name='MACD & Moving Average')

#Templates pra défaut choisi
pio.templates
pio.templates.default = "plotly_dark"

#Liste des Tickers
tickers_csv = pd.read_csv("nasdaq_screener.csv")
list_stock_name = tickers_csv["Name"]
list_tickers_symbol = tickers_csv["Symbol"]

ticker_etf = pd.read_csv("tickers_symbols.csv")
list_etf_name = ticker_etf["Name"].to_list()
list_etf_symbol = ticker_etf["Symbol"].to_list()


#Listes des dates
list_date =["1d","5d", "1mo","3mo","6mo","1y","2y","5y","10y", "ytd","max"]
list_date_complet =["1 Jour","5 Jour", "1 Mois","3 Mois","6 mois","1 an","2 ans","5 ans","10 ans", "Year-To-Date","Maximum"]
df_date = pd.DataFrame (list_date,list_date_complet, columns = ['Date'])
df_date = df_date.reset_index()
df_date = df_date.rename(columns={'index': 'DateComplet'})

#Création du graphe MACD et Moving Average
macd_graph = dcc.Graph(id='graph_macd')
moving_aver_graph = dcc.Graph(id='graph_moving_average')

#Placer le graphe MACD dans une Card
macd_graph_card=dbc.Card(
    dbc.CardBody([
        dcc.Graph(id='graph_macd')
    ])
)


liste=[]
list_etf = pd.read_csv("tickers_symbols.csv")
list_etf = list_etf["Symbol"].to_list()
list_type = ['ETF', 'Stock']
all_options = {
    'ETF': list_etf_name,
    'Stock': list_stock_name
}

first_card=dbc.Card([
    dbc.CardHeader(html.H4(id='perf',)),
    dbc.CardBody([
        html.H1(id='perf_chiffre')
    ])],color="primary",inverse=True
),

layout = html.Div([

    dbc.Row([
        dbc.Col(html.H1("Data Visualisation of", className="h1"),width='auto'),
        dbc.Col(html.H1(id="nom_complet"),width='auto'),
    ]),
    #Card
    dbc.Row([
        dbc.Col(first_card, width=6),
    ]),
    #Menu déroulant permettant selection de l'actions à voir
    html.P("Select type:"),
    dcc.Dropdown(list_type, "Stock", multi=False,clearable=False, id="choix_type", className="m-1"),
    
    html.P("Select stock:"),
    dcc.Dropdown(liste, "Apple Inc. Common Stock", multi=False,clearable=False, id="choix_actions", className="m-1"),
    html.P("Select a time frame:"),    
    dcc.Dropdown(list_date_complet, "1 an",multi=False,clearable=False, id="choix_date", className="m-1"),
    
    dbc.Row([
        dbc.Col(macd_graph, width=12),
    ]),

    dbc.Row([
        dbc.Col(width=6),
        dbc.Col(
        
        #Input pour le MACD
        html.Div(
        [
            html.P("Type a valuegreater than 1 to display the specified MACD"),
            dbc.Input(type="number",value=15, min=10, step=1, id='num_moving_av'),
            dbc.FormText("Type something in the box above"),
        ],
        id="styled-numeric-input",
        ), width=6)
    ]),

    dbc.Row([
        dbc.Col(moving_aver_graph, width=12),
    ]),


])


#Line graph + MACD
@callback(
    Output('graph_macd', 'figure'),
    Input('choix_actions', 'value'),
    Input('choix_date', 'value'),
    Input('choix_type', 'value'))

def update_figure(choix_actions,choix_date,choix_type):
    if choix_type == 'Stock':
        index = tickers_csv[tickers_csv['Name']==choix_actions].index.item()
        choix_actions = tickers_csv['Symbol'].iloc[index]
    elif choix_type == 'ETF':
        index = ticker_etf[ticker_etf['Name']==choix_actions].index.item()
        choix_actions = ticker_etf['Symbol'].iloc[index]

    index_date = df_date[df_date['DateComplet']==choix_date].index.item()
    choix_date = df_date['Date'].iloc[index_date]
    # Request historic pricing data via finance.yahoo.com API
    df = yf.Ticker(choix_actions).history(period=choix_date)[map(str.title, ['open', 'close', 'low', 'high', 'volume'])]    # Calculate MACD values using the pandas_ta library
    df.ta.macd(close='close', fast=12, slow=26, signal=9, append=True)
    # Force lowercase (optional)
    df.columns = [x.lower() for x in df.columns]
    # Construct a 2 x 1 Plotly figure
    fig = make_subplots(rows=2, cols=1)
    # price Line
    fig.append_trace(
        go.Scatter(
            x=df.index,
            y=df['open'],
            line=dict(color='#ff9900', width=1),
            name='open',
            # showlegend=False,
            legendgroup='1',
        ), row=1, col=1
    )
    # Candlestick chart for pricing
    fig.append_trace(
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            increasing_line_color='#ff9900',
            decreasing_line_color='black',
            showlegend=False
        ), row=1, col=1
    )
        # Fast Signal (%k)
    fig.append_trace(
            go.Scatter(
                x=df.index,
                y=df['macd_12_26_9'],
                line=dict(color='#ff9900', width=2),
                name='macd',
                # showlegend=False,
                legendgroup='2',
            ), row=2, col=1
        )
        # Slow signal (%d)
    fig.append_trace(
            go.Scatter(
                x=df.index,
                y=df['macds_12_26_9'],
                line=dict(color='#000000', width=2),
                # showlegend=False,
                legendgroup='2',
                name='signal'
            ), row=2, col=1
        )
        # Colorize the histogram values
    colors = np.where(df['macdh_12_26_9'] < 0, '#000', '#ff9900')
        # Plot the histogram
    fig.append_trace(
            go.Bar(
                x=df.index,
                y=df['macdh_12_26_9'],
                name='histogram',
                marker_color=colors,
            ), row=2, col=1
        )
        # Make it pretty
    layout = go.Layout(
        plot_bgcolor='#efefef',
        # Font Families
        font_family='Monospace',
        font_color='#000000',
        font_size=12,
        template='plotly_white',
        xaxis=dict(
            rangeslider=dict(
                visible=False
            )
        )
    )
    # Update options and show plot
    fig.update_layout(layout)

    return fig


#Moving average + Line graph --> Arrive pas a afficher la date sur le graphe
@callback(
    Output('graph_moving_average', 'figure'),
    Input('choix_actions', 'value'),
    Input('choix_date', 'value'),
    Input('num_moving_av', 'value'))
def update_figure(choix_actions,choix_date,moving_av):
    index = tickers_csv[tickers_csv['Name']==choix_actions].index.item()
    choix_actions = tickers_csv['Symbol'].iloc[index]
    index_date = df_date[df_date['DateComplet']==choix_date].index.item()
    choix_date = df_date['Date'].iloc[index_date]
    ticker = yf.Ticker(choix_actions)
    data = ticker.history(period=choix_date)
    data = data.reset_index()
    moving_average = data['Close'].rolling(window = moving_av).mean()
    fig = px.line(data, y="Close", title=f"Graphique : {ticker.info['longName']} depuis {choix_date}")
    fig.add_scatter(y=moving_average, mode = 'lines', name = "Moving average")
    fig.update_layout(hovermode="x unified")
    fig.update_yaxes(tickprefix="$")
    return fig