# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output, callback
import dash







dash.register_page(__name__,title='Home page',
    name='Home page')


layout = html.Div([
    html.H1("This is the home page")


])