from dash import callback, Input, Output
from dash import dcc
import pandas as pd
from app.services.animals import fetch_page

@callback(
    Output("download-csv", "data"),
    Input("btn-export", "n_clicks"),
    prevent_initial_call=True
)
def export_csv(n_clicks):
    rows, _ = fetch_page({}, None, page_size=1000)  # export first 1000 rows by default
    df = pd.DataFrame(rows)
    return dcc.send_data_frame(df.to_csv, filename="animals_export.csv", index=False)
