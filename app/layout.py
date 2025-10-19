from dash import html, dcc
import dash

def build_layout():
    return html.Div([
        html.H1("Austin Animal Center — Analytics Dashboard"),
        html.Div([
            html.Div([
                html.Label("Species"),
                dcc.Dropdown(id="filter-species", options=[
                    {"label": s, "value": s} for s in ["Dog", "Cat", "Other"]
                ], multi=True),
            ], className="filter"),
            html.Div([
                html.Label("Sex"),
                dcc.Dropdown(id="filter-sex", options=[
                    {"label": s, "value": s} for s in ["Intact Male", "Intact Female", "Neutered Male", "Spayed Female", "Unknown"]
                ], multi=True),
            ], className="filter"),
            html.Div([
                html.Label("Age (weeks)"),
                dcc.RangeSlider(0, 520, 26, id="filter-age", value=[0, 520], tooltip={"placement": "bottom"}),
            ], className="filter"),
        ], className="filters"),

        html.Div([
            html.Button("Export CSV", id="btn-export", n_clicks=0),
            dcc.Download(id="download-csv"),
        ], className="toolbar"),

        dcc.Store(id="filter-state"),
        dcc.Store(id="page-state", data={"last_id": None}),

        html.Div(id="metrics"),

        html.Div([
            dcc.Loading(
                id="loading-table",
                type="default",
                children=html.Table(id="animals-table")
            ),
            html.Div([
                html.Button("Prev", id="btn-prev", n_clicks=0),
                html.Span(id="page-indicator"),
                html.Button("Next", id="btn-next", n_clicks=0),
            ], className="pager")
        ])
    ], className="container")