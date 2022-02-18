from dash import Dash
from layout import AppLayout
from callbacks import Callbacks
import dash_bootstrap_components as dbc


class Main():
    def __init__(self) -> None:
        self.app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.layout= AppLayout(self.app)
        self.callbacks = Callbacks(self.app, self.layout)
        





if __name__ == '__main__':
    App = Main()
    App.app.run_server(debug=True)