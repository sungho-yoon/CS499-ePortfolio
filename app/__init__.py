from dash import Dash

def create_app():
    app = Dash(__name__, suppress_callback_exceptions=True, title="AAC Animals Dashboard")
    return app