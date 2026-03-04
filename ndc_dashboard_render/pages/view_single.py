import dash_bootstrap_components as dbc
from dash import dcc, html
import pandas as pd
from data_loader import dfs
from .components.overview_card import get_overview_card
from .components.emissions_pathways_chart import get_emissions_pathways_chart
from .components.peak_emissions_card import get_peak_emissions_card
from .components.net_zero_card import get_net_zero_card
from .components.scenarios_card import get_scenarios_card

# --- Layout Function ---
def get_layout():
    # Create dropdown options sorted alphabetically
    party_options = [
        {'label': row['party'], 'value': row['iso3']}
        for index, row in dfs['base'].sort_values('party').iterrows()
    ]

    return html.Div([
        # Dropdown
        dbc.Row([
            dbc.Col([
                html.H5("Select country/party", className="fw-bold"), # Changed from html.Label to html.H5
                dcc.Dropdown(
                    id='party-dropdown',
                    options=party_options,
                    value='EUU',
                    placeholder="Select a country...",
                    clearable=False,
                    className="mb-2"
                )
            ], width=12, md=6)
        ], className="mb-4"),

        # The content area is filled by the callback below
        html.Div(id='single-country-content')
    ])

# --- Main Logic to Generate Content ---
def generate_single_country_view(iso3):
    # 1. Filter Data for specific country
    base_df = dfs['base']
    row = base_df[base_df['iso3'] == iso3].iloc[0]

    ts_df = dfs['target_ts'][dfs['target_ts']['iso3'] == iso3]
    sl_df = dfs['straight_line'][dfs['straight_line']['iso3'] == iso3]
    sc_df = dfs['scenario'][dfs['scenario']['iso3'] == iso3]

    # Merge the past_ghg_net_source column into sl_df and sc_df
    ts_source_df = ts_df[['year', 'past_ghg_net_source']].drop_duplicates()
    sl_df = pd.merge(sl_df, ts_source_df, on='year', how='left')
    sc_df = pd.merge(sc_df, ts_source_df, on='year', how='left')

    # 2. Generate Cards and Charts
    overview_card = get_overview_card(row)
    emissions_pathways_chart = get_emissions_pathways_chart(row, ts_df, iso3)
    peak_emissions_card = get_peak_emissions_card(row)
    net_zero_card = get_net_zero_card(row, sl_df, iso3)
    scenarios_card = get_scenarios_card(row, sc_df)

    return html.Div([
        overview_card,
        emissions_pathways_chart,
        peak_emissions_card,
        net_zero_card,
        scenarios_card
    ])