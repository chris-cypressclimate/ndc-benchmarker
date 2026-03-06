import dash_bootstrap_components as dbc
from dash import html
import pandas as pd

def get_overview_card(data):
    target_statement_text = data.get('target_statement', '')
    target_statement_children = []
    if pd.notna(target_statement_text):
        for line in str(target_statement_text).split('<br>'):
            target_statement_children.append(line)
            target_statement_children.append(html.Br())
        target_statement_children.pop()

    return html.Div([
        html.Div("2035 NDC overview", className="section-header"),
        dbc.Table([
            html.Tbody([
                html.Tr([html.Td("New NDC submitted?"), html.Td(data.get('status_label', ''), className="fw-bold")]),
                html.Tr([html.Td("GHG target covers entire economy?"),
                         html.Td(data.get('all_sectors_label', ''), className="fw-bold")]),
                html.Tr([html.Td("GHG target covers all gases?"),
                         html.Td(data.get('all_gases_label', ''), className="fw-bold")]),
                html.Tr([html.Td("Specifies 2035 total emissions level?"),
                         html.Td(data.get('target35_label', ''), className="fw-bold")]),
                html.Tr(
                    [html.Td("Includes conditionality?"), html.Td(data.get('conditionality', ''), className="fw-bold")]),
                html.Tr([html.Td("Target statement from NDC:"),
                         html.Td(target_statement_children)]),
            ])
        ], className="clean-table", bordered=False, style={'margin-bottom': '0'}),
        html.Div([
            html.B("Sources: "),
            html.A("UNFCCC NDC registry", href="https://unfccc.int/NDCREG", target="_blank"),
            "; ",
            html.A("Climate Watch NDC Tracker", href="https://www.climatewatchdata.org/ndc-tracker", target="_blank"),
            "."
        ], className="graph-notes", style={'margin-top': '0', 'margin-bottom': '20px'})
    ])