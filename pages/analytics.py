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


dash.register_page(__name__,title='Analytics Dashboard',
    name='Analytics Dashboard')

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

first_card=dbc.Card([
    dbc.CardHeader(html.H4(id='perf',)),
    dbc.CardBody([
        html.H1(id='perf_chiffre')
    ])],color="primary",inverse=True
),

second_card=dbc.Card(
        dbc.CardBody([dbc.CardLink("Card link", href="#"),
        ]),
),

third_card=dbc.Card(
        dbc.CardBody([dbc.CardLink("Card link", href="#"),
        ]),
),

forth_card=dbc.Card(
        dbc.CardBody([dbc.CardLink("Card link", href="#"),
        ]),
),


line_graph=dbc.Card(
    dbc.CardBody([
        dcc.Graph(id='graph_stock_evol1')
    ])
)

candlestick_graph=dbc.Card(
    dbc.CardBody([
        dcc.Checklist(
        id='toggle-rangeslider',
        options=[{'label': 'Include Rangeslider', 
                  'value': 'slider'}],
        value=['slider']
        ),
        dcc.Graph(id='graph_stock_evol2')
    ])
)

earnings_graph=dbc.Card(
    dbc.CardBody([
        dcc.Graph(id='grap_earnings')
    ])
)

dividends_graph=dbc.Card(
    dbc.CardBody([
        dcc.Graph(id='graph_dividend')
    ])
)




for i in list_date:
    dropdown_date_items = [dbc.DropdownMenuItem(item) for item in list_date]
liste=[]
list_etf = pd.read_csv("tickers_symbols.csv")
list_etf = list_etf["Symbol"].to_list()
list_type = ['ETF', 'Stock']

all_options = {
    'ETF': list_etf_name,
    'Stock': list_stock_name
}



layout = html.Div([
    
    dbc.Row([
        dbc.Col(html.H1("Data Visualisation of", className="h1"),width='auto'),
        dbc.Col(html.H1(id="nom_complet"),width='auto'),
    ]),

    #Card
    dbc.Row([
        dbc.Col(first_card, width=6),
        #dbc.Col(second_card, width=3),
        dbc.Col(third_card, width=3),
        dbc.Col(forth_card, width=3),
    ]),

    #Menu déroulant permettant selection de l'actions à voir
    html.P("Select type:"),
    dcc.Dropdown(list_type, "Stock", multi=False,clearable=False, id="choix_type", className="m-1"),
    
    html.P("Select stock:"),
    dcc.Dropdown(liste, "Apple Inc. Common Stock", multi=False,clearable=False, id="choix_actions",style={'color': 'black'}),
    html.P("Select timeframe:"),
    dcc.Dropdown(list_date_complet, "1 an",multi=False,clearable=False, id="choix_date", className="m-1"),
    

    dbc.Row([
        dbc.Col(line_graph, width=6),
        dbc.Col(candlestick_graph, width=6),
    ]),
    dbc.Row([
        dbc.Col(width=6),
        dbc.Col(
        
        #Input pour la durée des dividendes
        html.Div(
        [
            html.P("Type a valuegreater than 1 to display dividends then"),
            dbc.Input(type="number",value=20, min=1, step=1, id='num_dividendes'),
            dbc.FormText("Type something in the box above"),
        ],
        id="styled-numeric-input",
        ), width=6)
    ]),
    dbc.Row([
        dbc.Col(earnings_graph, width=6),
        dbc.Col(dividends_graph, width=6)
    ]),

])


#Return list du type
@callback(
    Output('choix_actions', 'options'),
    Input('choix_type', 'value'))
def update_figure(choix_type):
    return all_options[choix_type]


#Return perf
@callback(
    Output('perf', 'children'),
    Output('perf_chiffre', 'children'),
    Output('nom_complet', 'children'),
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
    data = data.reset_index()
    last = data['Close'].iloc[0] # first element 
    today = data['Close'].iloc[-1] # last element 
    perf = "Performance sur la période : "
    perf_chiffre = " {0:.2f}".format(((today-last)/last)*100) + "%"
    nom_complet = ticker.info['longName']
    return perf, perf_chiffre,nom_complet

#Line graph
@callback(
    Output('graph_stock_evol1', 'figure'),
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

    date_complete = choix_date
    index_date = df_date[df_date['DateComplet']==choix_date].index.item()
    choix_date = df_date['Date'].iloc[index_date]

    ticker = yf.Ticker(choix_actions)
    data = ticker.history(period=choix_date)
    data = data.reset_index()
    fig = px.line(data, x='Date', y="Close", title=f"Graphique : {ticker.info['longName']} depuis {date_complete}")
    fig.update_layout(hovermode="x unified")
    fig.update_yaxes(tickprefix="$")
    return fig

#Candlestick graph
@callback(
    Output('graph_stock_evol2', 'figure'),
    Input('choix_actions', 'value'),
    Input('choix_date', 'value'),
    Input("toggle-rangeslider", "value"),
    Input('choix_type', 'value'))

def update_figure(choix_actions,choix_date,value,choix_type):
    if choix_type == 'Stock':
        index = tickers_csv[tickers_csv['Name']==choix_actions].index.item()
        choix_actions = tickers_csv['Symbol'].iloc[index]
    elif choix_type == 'ETF':
        index = ticker_etf[ticker_etf['Name']==choix_actions].index.item()
        choix_actions = ticker_etf['Symbol'].iloc[index]

    date_complete = choix_date
    index_date = df_date[df_date['DateComplet']==choix_date].index.item()
    choix_date = df_date['Date'].iloc[index_date]

    ticker = yf.Ticker(choix_actions)
    df = ticker.history(period=choix_date)
    df = df.reset_index()
    fig = go.Figure(data=[go.Candlestick(
                x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])
    fig.update_layout(hovermode="x unified")
    fig.update_layout(
        xaxis_rangeslider_visible='slider' in value
    )
    fig.update_layout(
    title=f"Graphique : {ticker.info['longName']} depuis {date_complete}",
    yaxis_title=f"{ticker.info['longName']} Stock",
    )
    fig.update_yaxes(tickprefix="$")
    return fig

#Earnings graph
@callback(
    Output('grap_earnings', 'figure'),
    Input('choix_actions', 'value'),
    Input('choix_type', 'value'))

def update_figure(choix_actions,choix_type):
    if choix_type == 'Stock':
        index = tickers_csv[tickers_csv['Name']==choix_actions].index.item()
        choix_actions = tickers_csv['Symbol'].iloc[index]
    elif choix_type == 'ETF':
        index = ticker_etf[ticker_etf['Name']==choix_actions].index.item()
        choix_actions = ticker_etf['Symbol'].iloc[index]

    if choix_type == 'Stock':
        ticker = yf.Ticker(choix_actions)
        fig = px.bar(ticker.earnings.reset_index(),x='Year', y="Earnings",text_auto=True,title=f"{ticker.info['longName']}, Earnings")
        fig.update_layout(bargap=0.1)
        fig.update_yaxes(tickprefix="$")
        return fig
    draft_template = go.layout.Template()
    draft_template.layout.annotations = [
    dict(
        name="draft watermark",
        text="Not a Stock",
        textangle=-30,
        opacity=0.1,
        font=dict(color="black", size=80),
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
    )
    ]
    fig=go.Figure()
    fig.update_layout(template=draft_template)
    return fig

#Dividends graph
@callback(
    Output('graph_dividend', 'figure'),
    Input('choix_actions', 'value'),
    Input('num_dividendes', 'value'),
    Input('choix_type', 'value'))

def update_figure(choix_actions,num_dividende,choix_type):
    if choix_type == 'Stock':
        index = tickers_csv[tickers_csv['Name']==choix_actions].index.item()
        choix_actions = tickers_csv['Symbol'].iloc[index]
    elif choix_type == 'ETF':
        index = ticker_etf[ticker_etf['Name']==choix_actions].index.item()
        choix_actions = ticker_etf['Symbol'].iloc[index]

    ticker = yf.Ticker(choix_actions)
    data = ticker.dividends.tail(num_dividende)
    data = data.reset_index()
    data['Date'] = data['Date'].dt.strftime('%Y')
    data['test'] = data.groupby(["Date"])["Dividends"].transform(sum)
    data=data.groupby(["Date"])["Dividends"].sum()
    data = data.reset_index()
    #If no dividend, print the message "No Dividend"
    if data['Dividends'].sum() == 0:
        draft_template = go.layout.Template()
        draft_template.layout.annotations = [
        dict(
        name="draft watermark",
        text="No Dividend",
        textangle=-30,
        opacity=0.1,
        font=dict(color="black", size=80),
        xref="paper",yref="paper", x=0.5,y=0.5,showarrow=False,)]
        fig=go.Figure()
        fig.update_layout(template=draft_template)
        return fig

    fig = px.bar(data,x='Date', y="Dividends",text_auto=".2f",title=f"{ticker.info['longName']}, Dividends")
    fig.update_layout(bargap=0.1)
    fig.update_yaxes(tickprefix="$")
    return fig

#Card with stock info
#@callback(
#    Output('card_info', 'children'),
#    Input('choix_actions', 'value'))
#def update_figure(choix_actions):
#    ticker = yf.Ticker(choix_actions)
#    text=""
#    text+=ticker.info['sector']
#    return text

#@app.callback(
#    Output('stock_info', 'children'),
#    Input('choix_actions', 'value'))
#def update_figure(choix_actions):
#   ticker = yf.Ticker(choix_actions)
#    infos = f"Employees : {ticker.info['fullTimeEmployees']}", html.Br(), f"Business Summary : \n{ticker.info['longBusinessSummary']}"
#    return infos