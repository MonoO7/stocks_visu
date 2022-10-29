# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, dcc, html, Input, Output
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


app = Dash(__name__, use_pages=True )
menu = [
    dbc.NavItem(dbc.NavLink(page['name'], href=page["relative_path"]))
    for page in dash.page_registry.values()
],
    #Bar de navigation
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/home")),
        dbc.NavItem(dbc.NavLink("Analytics", href="/analytics")),
        dbc.NavItem(dbc.NavLink("MACD", href="/macd")),
        dbc.NavItem(dbc.NavLink("Rolling Bands", href="/rollingbands")),
        dbc.NavItem(dbc.NavLink("RSI", href="/rsi")),


        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Homepage", href="/home"),
                dbc.DropdownMenuItem("Analytics dashboard", href="/analytics"),
                dbc.DropdownMenuItem("MACD", href="/macd"),
                dbc.DropdownMenuItem("Rolling Bands", href="/rollingbands"),
                dbc.DropdownMenuItem("RSI", href="/rsi"),

            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="Navbar",
    #brand_href="#",
    color="primary",
    dark=True,
)

app.layout = html.Div([

	html.H1('Multi-page app with Dash Pages'),
    navbar,
    dash.page_container
])

if __name__ == '__main__':
    app.run_server(debug=True)