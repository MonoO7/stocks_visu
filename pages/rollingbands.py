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

import yfinance as yf
import plotly.io as pio
import plotly.graph_objects as go


dash.register_page(__name__,title='Rolling Bands',
    name='Rolling Bands')

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

list_date =["1d","5d", "1mo","3mo","6mo","1y","2y","5y","10y", "ytd","max"]
list_date_complet =["1 Jour","5 Jour", "1 Mois","3 Mois","6 mois","1 an","2 ans","5 ans","10 ans", "Year-To-Date","Maximum"]

df_date = pd.DataFrame (list_date,list_date_complet, columns = ['Date'])
df_date = df_date.reset_index()
df_date = df_date.rename(columns={'index': 'DateComplet'})


liste=[]
list_etf = pd.read_csv("tickers_symbols.csv")
list_etf = list_etf["Symbol"].to_list()
list_type = ['ETF', 'Stock']
all_options = {
    'ETF': list_etf_name,
    'Stock': list_stock_name
}

#Placer le graphe MACD dans une Card
rolling_bands_graph_card=dbc.Card(
    dbc.CardBody([
        dcc.Graph(id='graph_rolling_bands')
    ])
)

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
    dcc.Dropdown(liste, "Apple Inc. Common Stock", multi=False,clearable=False, id="choix_actions",style={'color': 'black'}),
    html.P("Select timeframe:"),
    dcc.Dropdown(list_date_complet, "1 an",multi=False,clearable=False, id="choix_date", className="m-1"),
    

    dbc.Row([
        dbc.Col(rolling_bands_graph_card, width=12),
    ]),

])



#Line graph + MACD
@callback(
    Output('graph_rolling_bands', 'figure'),
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

    ticker = yf.Ticker(choix_actions)
    data = ticker.history(period=choix_date)
    df = data[['Close']]

    sma = df.rolling(window=20).mean().dropna()
    rstd = df.rolling(window=20).std().dropna()

    upper_band = sma + 2 * rstd
    lower_band = sma - 2 * rstd

    upper_band = upper_band.rename(columns={'Close': 'upper'})
    lower_band = lower_band.rename(columns={'Close': 'lower'})
    bb = df.join(upper_band).join(lower_band)
    bb = bb.dropna()

    buyers = bb[bb['Close'] <= bb['lower']]
    sellers = bb[bb['Close'] >= bb['upper']]

    # Plotting
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=lower_band.index, 
                            y=lower_band['lower'], 
                            name='Lower Band', 
                            line_color='rgba(173,204,255,0.2)'
                            ))
    fig.add_trace(go.Scatter(x=upper_band.index, 
                            y=upper_band['upper'], 
                            name='Upper Band', 
                            fill='tonexty', 
                            fillcolor='rgba(173,204,255,0.2)', 
                            line_color='rgba(173,204,255,0.2)'
                            ))
    fig.add_trace(go.Scatter(x=df.index, 
                            y=df['Close'], 
                            name='Close', 
                            line_color='#636EFA'
                            ))
    fig.add_trace(go.Scatter(x=sma.index, 
                            y=sma['Close'], 
                            name='SMA', 
                            line_color='#FECB52'
                            ))
    fig.add_trace(go.Scatter(x=buyers.index, 
                            y=buyers['Close'], 
                            name='Buyers', 
                            mode='markers',
                            marker=dict(
                                color='#00CC96',
                                size=10,
                                )
                            ))
    fig.add_trace(go.Scatter(x=sellers.index, 
                            y=sellers['Close'], 
                            name='Sellers', 
                            mode='markers', 
                            marker=dict(
                                color='#EF553B',
                                size=10,
                                )
                            ))

    return fig