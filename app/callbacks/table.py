from dash import callback, Input, Output, State, html
from app.services.animals import build_query, fetch_page, top_breeds, age_histogram

@callback(
    Output("filter-state", "data"),
    Input("filter-species", "value"),
    Input("filter-sex", "value"),
    Input("filter-age", "value"),
)
def update_filter_state(species, sex, age):
    return build_query(species, sex, age)


def _render_table(rows):
    header = html.Thead(html.Tr([html.Th("Type"), html.Th("Breed"), html.Th("Sex"), html.Th("Age (wks)")]))
    body = html.Tbody([
        html.Tr([
            html.Td(r.get("animal_type")),
            html.Td(r.get("breed")),
            html.Td(r.get("sex_upon_outcome")),
            html.Td(r.get("age_upon_outcome_in_weeks")),
        ]) for r in rows
    ])
    return [header, body]


@callback(
    Output("animals-table", "children"),
    Output("page-state", "data"),
    Output("page-indicator", "children"),
    Input("filter-state", "data"),
    Input("btn-next", "n_clicks"),
    Input("btn-prev", "n_clicks"),
    State("page-state", "data"),
    prevent_initial_call=False,
)
def paginate_table(filters, n_next, n_prev, page_state):
    # Determine direction
    triggered = [i["prop_id"] for i in dash.callback_context.triggered][0] if dash.callback_context.triggered else "filter-state.data"

    last_id = None if triggered == "filter-state.data" else page_state.get("last_id")
    rows, next_last_id = fetch_page(filters or {}, last_id)

    page_label = f"Next page after _id > {last_id}" if last_id else "Page 1"
    return _render_table(rows), {"last_id": next_last_id}, page_label


@callback(
    Output("metrics", "children"),
    Input("filter-state", "data")
)
def update_metrics(filters):
    breeds = top_breeds(filters or {})
    return html.Ul([html.Li(f"{b['_id']}: {b['count']}") for b in breeds])

@callback(
    Output("metrics", "children"),
    Input("filter-state", "data")
)
def update_metrics(filters):
    filters = filters or {}
    breeds = top_breeds(filters)                   # <- cached
    ages = age_histogram(filters, step=26, max_weeks=520)  # <- cached

    age_items = [html.Li(f"{b['bucket']}: {b['count']}") for b in ages]
    breed_items = [html.Li(f"{b['_id']}: {b['count']}") for b in breeds]

    return html.Div([
        html.H4("Top Breeds"),
        html.Ul(breed_items),
        html.H4("Age Buckets (weeks)"),
        html.Ul(age_items)
    ])