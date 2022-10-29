# Import necessary libraries
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import yfinance as yf
from dash import Dash, html, dcc, Input, Output, callback
import dash
import plotly.express as px
import pandas as pd
import quandl
import plotly.io as pio
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import datetime as dt
from pandas_datareader import data as web
from dateutil.relativedelta import relativedelta

dash.register_page(__name__,title='RSI',
    name='RSI')

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
RSI_graph_card=dbc.Card(
    dbc.CardBody([
        dcc.Graph(id='graph_RSI')
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
        #dbc.Col(second_card, width=3),
    ]),
    
    #Menu déroulant permettant selection de l'actions à voir
    html.P("Select type:"),
    dcc.Dropdown(list_type, "Stock", multi=False,clearable=False, id="choix_type", className="m-1"),
    
    html.P("Select stock:"),
    dcc.Dropdown(liste, "Apple Inc. Common Stock", multi=False,clearable=False, id="choix_actions",style={'color': 'black'}),
    html.P("Select timeframe:"),
    dcc.Dropdown(list_date_complet, "1 an",multi=False,clearable=False, id="choix_date", className="m-1"),
    

    dbc.Row([
        dbc.Col(RSI_graph_card, width=12),
    ]),


])


#RSI Line graph 
@callback(
    Output('graph_RSI', 'figure'),
    Input('choix_actions', 'value'),
    Input('choix_date', 'value'),
    Input('choix_type', 'value'))
def update_figure(choix_actions,choix_date,choix_type):
    pio.templates.default = "plotly"

    if choix_type == 'Stock':
        index = tickers_csv[tickers_csv['Name']==choix_actions].index.item()
        choix_actions = tickers_csv['Symbol'].iloc[index]
    elif choix_type == 'ETF':
        index = ticker_etf[ticker_etf['Name']==choix_actions].index.item()
        choix_actions = ticker_etf['Symbol'].iloc[index]
    index_date = df_date[df_date['DateComplet']==choix_date].index.item()
    choix_date = df_date['Date'].iloc[index_date]

    def pandas_rsi(df: pd.DataFrame, window_length: int = 14, output: str = None, price: str = 'Close'):
        """
        An implementation of Wells Wilder's RSI calculation as outlined in
        his 1978 book "New Concepts in Technical Trading Systems" which makes
        use of the α-1 Wilder Smoothing Method of calculating the average
        gains and losses across trading periods and the Pandas library.
        @author: https://github.com/alphazwest
        Args:
            df: pandas.DataFrame - a Pandas Dataframe object
            window_length: int - the period over which the RSI is calculated. Default is 14
            output: str or None - optional output path to save data as CSV
            price: str - the column name from which the RSI values are calcuated. Default is 'Close'
        Returns:
            DataFrame object with columns as such, where xxx denotes an inconsequential
            name of the provided first column:
                ['xxx', 'diff', 'gain', 'loss', 'avg_gain', 'avg_loss', 'rs', 'rsi']
        """
        # Calculate Price Differences using the column specified as price.
        df['diff1'] = df[price].diff(1)

        # Calculate Avg. Gains/Losses
        df['gain'] = df['diff1'].clip(lower=0).round(2)
        df['loss'] = df['diff1'].clip(upper=0).abs().round(2)

        # Get initial Averages
        df['avg_gain'] = df['gain'].rolling(window=window_length, min_periods=window_length).mean()[:window_length+1]
        df['avg_loss'] = df['loss'].rolling(window=window_length, min_periods=window_length).mean()[:window_length+1]

        # Calculate Average Gains
        for i, row in enumerate(df['avg_gain'].iloc[window_length+1:]):
            df['avg_gain'].iloc[i + window_length + 1] =\
                (df['avg_gain'].iloc[i + window_length] *
                (window_length - 1) +
                df['gain'].iloc[i + window_length + 1])\
                / window_length

        # Calculate Average Losses
        for i, row in enumerate(df['avg_loss'].iloc[window_length+1:]):
            df['avg_loss'].iloc[i + window_length + 1] =\
                (df['avg_loss'].iloc[i + window_length] *
                (window_length - 1) +
                df['loss'].iloc[i + window_length + 1])\
                / window_length

        # Calculate RS Values
        df['rs'] = df['avg_gain'] / df['avg_loss']

        # Calculate RSI
        df['rsi'] = 100 - (100 / (1.0 + df['rs']))

        # Save if specified
        if output is not None:
            df.to_csv(output)

        return df

    # Download historic pricing data for $BTC-USD
    ticker = yf.Ticker(choix_actions)
    data = ticker.history(period=choix_date)
    # Force lowercase column names
    data.columns = map(str.lower, data.columns)

    # Make RSI Calculations
    pandas_rsi(df=data, window_length=14, price='close')

    # Set option to view all columns
    pd.set_option('display.max_columns', None)
    # Create Figure
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_width=[0.25, 0.75])

    # Create Candlestick chart for price data
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close'],
        increasing_line_color='#ff9900',
        decreasing_line_color='black',
        showlegend=False
    ), row=1, col=1)

    # Make RSI Plot
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['rsi'],
        line=dict(color='#ff9900', width=2),
        showlegend=False,
    ), row=2, col=1
    )

    # Add upper/lower bounds
    fig.update_yaxes(range=[-10, 110], row=2, col=1)
    fig.add_hline(y=0, col=1, row=2, line_color="#666", line_width=2)
    fig.add_hline(y=100, col=1, row=2, line_color="#666", line_width=2)

    # Add overbought/oversold
    fig.add_hline(y=30, col=1, row=2, line_color='#336699', line_width=2, line_dash='dash')
    fig.add_hline(y=70, col=1, row=2, line_color='#336699', line_width=2, line_dash='dash')

    # Customize font, colors, hide range slider
    layout = go.Layout(
        plot_bgcolor='#efefef',
        # Font Families
        font_family='Monospace',
        font_color='#000000',
        font_size=20,
        xaxis=dict(
            rangeslider=dict(
                visible=False
            )
        )
    )

    # update and display
    fig.update_layout(layout)
    return fig