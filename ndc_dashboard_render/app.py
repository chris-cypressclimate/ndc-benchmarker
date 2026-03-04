import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from data_loader import dfs, count_new_ndcs, count_no_new_ndcs
from pages import view_single, view_all, sources
import datetime
import pandas as pd
import plotly.graph_objects as go # Import plotly.graph_objects

# Initialize App with Bootstrap Theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, '/assets/styles.css'],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}], # CRITICAL for mobile
    suppress_callback_exceptions=True
)
server = app.server

# Footer
current_year = datetime.datetime.now().year
footer = html.Div(
    dbc.Container(
        dbc.Row([
            dbc.Col([
                html.Img(src=app.get_asset_url("footer_logo.png"), className="footer-logo"),
            ], width="auto"),
            dbc.Col([
                html.Div([
                    html.Div("Chris Sall", className="footer-text"),
                    html.Div(f"Cypress Climate Advisory, LLC © {current_year}", className="footer-text"),
                    dbc.Button("Questions? Feedback?", href="mailto:chris@cypressclimate.earth", style={'backgroundColor': '#43a2ca', 'border': '1px solid white', 'width': 'fit-content'}, size="sm")
                ], className="footer-contact-details")
            ], width="auto")
        ], align="start", justify="start"),
        fluid=True,
        style={'maxWidth': '1200px', 'margin': 'auto'}
    ),
    className="footer"
)

# App Layout
app.layout = html.Div(id='app-container', children=[
    dcc.Store(id='dummy-output'),
    dcc.Download(id="download-chart-csv"),
    dcc.Download(id="download-net-zero-chart-csv"),
    dcc.Download(id="download-ipcc-chart-csv"),
    dcc.Download(id="download-ngfs-chart-csv"),
    html.Div(id='banner-container', children=[
        dbc.Container(style={'maxWidth': '1200px', 'margin': 'auto'}, children=[
            # --- Top Banner ---
            dbc.Row([
                dbc.Col(
                    html.Img(src=app.get_asset_url("updated_logo.png"), style={"height": "5.25rem"}, className="banner-logo"),
                    width="auto",
                    className="text-start mb-3"
                ),
            ], className="align-items-center"),

            # --- Explainer Text ---
            dcc.Markdown("""
            **Welcome to the NDC benchmarker**
            
            [Nationally Determined Contributions](https://unfccc.int/process-and-meetings/the-paris-agreement/nationally-determined-contributions-ndcs) (NDCs) are at the core of the [Paris Agreement](https://unfccc.int/process-and-meetings/the-paris-agreement) and collective efforts by countries to reduce the risks and impacts of climate change.  The Paris Agreement requires that countries submit new NDCs every five years.  With the latest round of NDCs, due in 2025, countries were encouraged to set economy-wide targets for reducing their greenhouse gas (GHG) emissions by 2035 in line with holding long-term temperature rise to 1.5°C.
            
            This data dashboard compares countries’ new NDCs against common benchmarks for ambition and credibility, assessing whether their 2035 targets are on track to net zero and in line with goals for limiting warming.  The **View single** tab below shows detailed data for individual countries/parties, while the **View all** tab provides a summary datasheet for all countries/parties.  The **Sources & notes** tab contains details on methods and data sources.
            """, className="mb-4 explainer-text"),

            # --- Country Counts Table ---
            html.Div(
                html.Table([
                    html.Tbody([
                        html.Tr([
                            html.Td(f"{count_new_ndcs}", className="banner-count-a text-start text-sm-end align-middle"),
                            html.Td(className="spacer-col"),
                            html.Td([
                                "countries with new climate targets",
                                html.Br(),
                                dcc.Markdown("(NDCs) announced since 2024", className="banner-markdown")
                            ], className="banner-text align-middle")
                        ]),
                        html.Tr([
                            html.Td(f"{count_no_new_ndcs}", className="banner-count-b-bold text-start text-sm-end align-middle"),
                            html.Td(className="spacer-col"),
                            html.Td("countries without new NDCs", className="banner-text align-middle")
                        ])
                    ])
                ], className="banner-table"),
                className="mb-3 country-counts-container"
            ),
        ])
    ]),
    # --- Sticky Tabs ---
    html.Div([
        dbc.Tabs([
            dbc.Tab(label="View single", tab_id="tab-single"),
            dbc.Tab(label="View all", tab_id="tab-all"),
            dbc.Tab(label="Sources & notes", tab_id="tab-sources"),
        ], id="main-tabs", active_tab="tab-single", className="custom-tabs")
    ], className="sticky-tabs", id="tabs-container"),

    # --- Content Container ---
    html.Div(id="page-content", className="mt-4 desktop-margin"),

    # --- Footer ---
    footer
])

# --- Callbacks ---

app.clientside_callback(
    """
    function(tab_value) {
        if (tab_value === 'tab-sources') {
            window.scrollTo(0, 0);
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('dummy-output', 'data'),
    Input('main-tabs', 'active_tab')
)

@app.callback(
    Output('banner-container', 'style'),
    Input('main-tabs', 'active_tab')
)
def toggle_banner(active_tab):
    if active_tab == 'tab-sources':
        return {'display': 'none'}
    return {'display': 'block'}

@app.callback(
    Output("page-content", "children"),
    Input("main-tabs", "active_tab")
)
def render_content(active_tab):
    if active_tab == "tab-single":
        return view_single.get_layout()
    elif active_tab == "tab-all":
        return view_all.get_layout()
    elif active_tab == "tab-sources":
        return sources.get_layout()
    return html.Div("404 Error")

# Callback for Single Country Dropdown
# This bridges the layout in view_single.py with the logic in view_single.py
@app.callback(
    Output('single-country-content', 'children'),
    Input('party-dropdown', 'value')
)
def update_view(iso3):
    if not iso3:
        return html.Div()
    return view_single.generate_single_country_view(iso3)

@app.callback(
    Output("download-chart-csv", "data"),
    Input("download-chart-csv-data", "n_clicks"),
    State("party-dropdown", "value"),
    prevent_initial_call=True,
)
def download_chart_csv(n_clicks, iso3):
    if n_clicks:
        ts_df = dfs['target_ts'][dfs['target_ts']['iso3'] == iso3].copy()
        ts_df['iso3'] = iso3
        cols_to_keep = [
            'iso3', 'year', 'past_ghg_net', 'past_ghg_net_source', 'past_ghg_gross', 'past_ghg_gross_source',
            'ndc_low', 'ndc_high', 'ndc30pt_high', 'ndc30pt_low', 'ndc35pt_high',
            'ndc35pt_low', 'ndc35pt_base'
        ]
        download_df = ts_df[cols_to_keep]
        return dcc.send_data_frame(download_df.to_csv, f"{iso3}_emissions_pathways.csv", index=False)

@app.callback(
    Output("download-net-zero-chart-csv", "data"),
    Input("download-net-zero-chart-csv-data", "n_clicks"),
    State("party-dropdown", "value"),
    prevent_initial_call=True,
)
def download_net_zero_chart_csv(n_clicks, iso3):
    if n_clicks:
        sl_df = dfs['straight_line'][dfs['straight_line']['iso3'] == iso3]
        cols_to_keep = [
            'iso3', 'year', 'past_ghg_net', 'ndc_low', 'ndc_high', 'ndc30pt_low', 
            'ndc30pt_high', 'ndc35pt_low', 'ndc35pt_high', 'nz_year', 
            'peak_net_ghg', 's2z_pk_low', 's2z_pk_high', 's2z_ndc30_low', 
            's2z_ndc30_high', 's2z_latest'
        ]
        download_df = sl_df[cols_to_keep]
        return dcc.send_data_frame(download_df.to_csv, f"{iso3}_net_zero_pathways.csv", index=False)

@app.callback(
    Output("download-ipcc-chart-csv", "data"),
    Input("download-ipcc-chart-csv-data", "n_clicks"),
    State("party-dropdown", "value"),
    prevent_initial_call=True,
)
def download_ipcc_chart_csv(n_clicks, iso3):
    if n_clicks:
        sc_df = dfs['scenario'][dfs['scenario']['iso3'] == iso3]
        cols_to_keep = [
            'iso3', 'year', 'past_ghg_net', 'ndc_low', 'ndc_high', 'ndc35pt_high', 
            'ndc35pt_low', 'c1_ghg_p5', 'c1_ghg_p95', 'c2_ghg_p5', 'c2_ghg_p95', 
            'c3_ghg_p5', 'c3_ghg_p95', 'c4_ghg_p5', 'c4_ghg_p95', 'c5_ghg_p5', 
            'c5_ghg_p95', 'c6_ghg_p5', 'c6_ghg_p95', 'c7_ghg_p5', 'c7_ghg_p95'
        ]
        download_df = sc_df[cols_to_keep]
        return dcc.send_data_frame(download_df.to_csv, f"{iso3}_ipcc_scenarios.csv", index=False)

@app.callback(
    Output("download-ngfs-chart-csv", "data"),
    Input("download-ngfs-chart-csv-data", "n_clicks"),
    State("party-dropdown", "value"),
    prevent_initial_call=True,
)
def download_ngfs_chart_csv(n_clicks, iso3):
    if n_clicks:
        sc_df = dfs['scenario'][dfs['scenario']['iso3'] == iso3]
        cols_to_keep = [
            'iso3', 'year', 'past_ghg_net', 'ndc_low', 'ndc_high', 'ndc35pt_high',
            'ndc35pt_low', 'nz_min', 'nz_max', 'b2c_min', 'b2c_max', 'fw_min',
            'fw_max', 'cp_min', 'cp_max'
        ]
        download_df = sc_df[cols_to_keep]
        return dcc.send_data_frame(download_df.to_csv, f"{iso3}_ngfs_scenarios.csv", index=False)

if __name__ == "__main__":
    app.run(debug=True)