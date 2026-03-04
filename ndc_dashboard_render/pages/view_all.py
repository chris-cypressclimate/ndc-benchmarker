import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
import dash_ag_grid as dag
from data_loader import dfs
import numpy as np

def get_layout():
    df = dfs['public'].replace('—', np.nan)

    columnDefs = [
        {"headerName": "UNFCCC Party", "field": "party", "pinned": "left", "width": 120, "headerClass": "header-dark-grey"},
        {"headerName": "ISO3", "field": "iso3", "width": 80, "headerClass": "header-light-grey"},
        {
            "headerName": "Latest inventory",
            "headerClass": "header-dark-grey",
            "children": [
                {"headerName": "Year", "field": "unfccc_yr", "width": 80, "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
                {"headerName": "Total emissions\nincl LULUCF\n(kt CO2e)", "width": 140, "field": "unfccc_net", "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
                {"headerName": "Total emissions\nexcl LULUCF\n(kt CO2e)", "width": 140, "field": "unfccc_gross", "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
            ]
        },
        {
            "headerName": "Latest PRIMAP-hist data",
            "headerClass": "header-light-grey",
            "children": [
                {"headerName": "Year", "field": "primap_yr", "width": 80, "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
                {"headerName": "Total emissions\nincl LULUCF\n(kt CO2e)", "width": 140, "field": "primap_net", "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
                {"headerName": "Total emissions\nexcl LULUCF\n(kt CO2e)", "width": 140, "field": "primap_gross", "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
            ]
        },
        {
            "headerName": "Peak emissions",
            "headerClass": "header-dark-grey",
            "children": [
                {"headerName": "Incl LULUCF\n(year)", "width": 120, "field": "peak_yr_net", "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
                {"headerName": "Incl LULUCF\n(kt CO2e)", "width": 120, "field": "peak_ghg_net", "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
                {"headerName": "Excl LULUCF\n(year)", "width": 120, "field": "peak_yr_gross", "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
                {"headerName": "Excl LULUCF\n(kt CO2e)", "width": 120, "field": "peak_ghg_gross", "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
            ]
        },
        {
            "headerName": "Net Zero Target",
            "headerClass": "header-light-grey",
            "children": [
                {"headerName": "Year", "width": 100, "field": "nz_yr", "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
            ]
        },
        {
            "headerName": "2030 NDC Target Range",
            "headerClass": "header-dark-grey",
            "children": [
                {"headerName": "Lower end\n(kt CO2e)", "width": 120, "field": "ndc30_low", "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
                {"headerName": "Upper end\n(kt CO2e)", "width": 120, "field": "ndc30_high", "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
                {"headerName": "Includes LULUCF?", "width": 115, "field": "ndc30_lulucf", "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
            ]
        },
        {
            "headerName": "2035 NDC Target Range",
            "headerClass": "header-light-grey",
            "children": [
                {"headerName": "Lower end\n(kt CO2e)", "width": 120, "field": "ndc35_low", "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
                {"headerName": "Upper end\n(kt CO2e)", "width": 120, "field": "ndc35_high", "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
                {"headerName": "Includes LULUCF?", "width": 115, "field": "ndc35_lulucf", "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
                {"headerName": "On linear path to net zero?", "width": 140, "field": "s2z_aligned_label", "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
            ]
        },
        {
            "headerName": "Linear pathways to net zero,\nImplied emissions level in 2035",
            "headerClass": "header-dark-grey",
            "children": [
                {"headerName": "Linear from peak,\nLower end\n(kt CO2e)", "width": 140, "field": "s2z_pk_low", "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
                {"headerName": "Linear from peak,\nUpper end\n(kt CO2e)", "width": 140, "field": "s2z_pk_high", "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
                {"headerName": "Linear from 2030 NDC,\nLower end\n(kt CO2e)", "width": 140, "field": "s2z_ndc30_low", "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
                {"headerName": "Linear from 2030 NDC,\nUpper end\n(kt CO2e)", "width": 140, "field": "s2z_ndc30_high", "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
                {"headerName": "Linear from current\n(kt CO2e)", "width": 140, "field": "s2z_latest", "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
            ]
        },
        {
            "headerName": "IPCC scenarios by warming category,\nModeled emissions in 2035",
            "headerClass": "header-light-grey",
            "children": [
                {"headerName": "1.5°C\n5th pctile\n(kt CO2e)", "field": "c1_ghg_p5", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
                {"headerName": "1.5°C\n95th pctile\n(kt CO2e)", "field": "c1_ghg_p95", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
                {"headerName": "1.5°C w/ overshoot\n5th pctile\n(kt CO2e)", "field": "c2_ghg_p5", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
                {"headerName": "1.5°C w/ overshoot\n95th pctile\n(kt CO2e)", "field": "c2_ghg_p95", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
                {"headerName": "2°C (>67%)\n5th pctile\n(kt CO2e)", "field": "c3_ghg_p5", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
                {"headerName": "2°C (>67%)\n95th pctile\n(kt CO2e)", "field": "c3_ghg_p95", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
                {"headerName": "2°C (>50%)\n5th pctile\n(kt CO2e)", "field": "c4_ghg_p5", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
                {"headerName": "2°C (>50%)\n95th pctile\n(kt CO2e)", "field": "c4_ghg_p95", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
                {"headerName": "2.5°C\n5th pctile\n(kt CO2e)", "field": "c5_ghg_p5", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
                {"headerName": "2.5°C\n95th pctile\n(kt CO2e)", "field": "c5_ghg_p95", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
                {"headerName": "3°C\n5th pctile\n(kt CO2e)", "field": "c6_ghg_p5", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
                {"headerName": "3°C\n95th pctile\n(kt CO2e)", "field": "c6_ghg_p95", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
                {"headerName": "4°C\n5th pctile\n(kt CO2e)", "field": "c7_ghg_p5", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
                {"headerName": "4°C\n95th pctile\n(kt CO2e)", "field": "c7_ghg_p95", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-light-grey text-left", "cellClass": "text-right"},
            ]
        },
        {
            "headerName": "NGFS scenarios by level of warming,\nModeled emissions in 2035",
            "headerClass": "header-dark-grey",
            "children": [
                {"headerName": "1.4°C w/ overshoot,\nMin\n(kt CO2e)", "field": "nz_min", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
                {"headerName": "1.4°C w/ overshoot,\nMax\n(kt CO2e)", "field": "nz_max", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
                {"headerName": "1.8°C,\nMin\n(kt CO2e)", "field": "b2c_min", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
                {"headerName": "1.8°C,\nMax\n(kt CO2e)", "field": "b2c_max", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
                {"headerName": "2.4°C,\nMin\n(kt CO2e)", "field": "fw_min", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
                {"headerName": "2.4°C,\nMax\n(kt CO2e)", "field": "fw_max", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
                {"headerName": "3°C,\nMin\n(kt CO2e)", "field": "cp_min", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
                {"headerName": "3°C,\nMax\n(kt CO2e)", "field": "cp_max", "width": 140, "valueFormatter": {"function": "params.value == null ? '—' : d3.format(',.0f')(params.value)"}, "headerClass": "header-dark-grey text-left", "cellClass": "text-right"},
            ]
        }
    ]

    defaultColDef = {
        "sortable": True,
        "filter": True,
        "resizable": True,
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "wrapText": True,
        "autoHeight": True,
        "valueFormatter": {"function": "params.value == null ? '—' : params.value"},
        "cellStyle": {
            "styleConditions": [
                {
                    "condition": "params.value == null",
                    "style": {"color": "#d3d3d3"}
                },
                {
                    "condition": "params.value != null",
                    "style": {"color": "#808080"}
                }
            ]
        }
    }

    return html.Div([
        html.Div("Summary data sheet for all countries", className="section-title"),

        html.Div([
            dag.AgGrid(
                id="summary-table",
                rowData=df.to_dict('records'),
                columnDefs=columnDefs,
                className="ag-theme-alpine",
                defaultColDef=defaultColDef,
                dashGridOptions={"rowSelection": "single"},
                style={"height": "70vh"},
                getRowStyle={
                    "styleConditions": [
                        {"condition": "params.node.isSelected()", "style": {"backgroundColor": "#bae4bc"}},
                    ]
                },
            )
        ], style={'border': '1px solid #ddd'}),  # Container border
        
        html.Div([
            dbc.Button("Download data", id="download-button", color="primary", className="mb-3"),
            dcc.Download(id="download-csv")
        ], style={'paddingTop': '20px'})
    ])

@callback(
    Output("download-csv", "data"),
    Input("download-button", "n_clicks"),
    State("summary-table", "virtualRowData"),
    prevent_initial_call=True,
)
def download_csv(n_clicks, virtual_row_data):
    if n_clicks:
        import pandas as pd
        df = pd.DataFrame(virtual_row_data)
        return dcc.send_data_frame(df.to_csv, "ndc_summary_data.csv", index=False)
    return dash.no_update