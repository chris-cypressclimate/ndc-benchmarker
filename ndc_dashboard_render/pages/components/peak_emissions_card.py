import dash_bootstrap_components as dbc
from dash import html
import re

def _clean_label(text):
    """Converts potential float (NaN) or other non-string types to an empty string."""
    if not isinstance(text, str):
        return ""
    return text

def _subscript_chemical_formulas(text):
    if not text:
        return ""
    
    parts = re.split(r'(CO2e|CH4|N2O|SF6|LULUCF)', text)
    
    new_parts = []
    for part in parts:
        if part == "CO2e":
            new_parts.append("CO")
            new_parts.append(html.Sub("2"))
            new_parts.append("e")
        elif part == "CH4":
            new_parts.append("CH")
            new_parts.append(html.Sub("4"))
        elif part == "N2O":
            new_parts.append("N")
            new_parts.append(html.Sub("2"))
            new_parts.append("O")
        elif part == "SF6":
            new_parts.append("SF")
            new_parts.append(html.Sub("6"))
        elif part == "LULUCF":
            new_parts.append(html.A("LULUCF", href="https://unfccc.int/topics/land-use/workstreams/land-use--land-use-change-and-forestry-lulucf", target="_blank"))
        else:
            new_parts.append(part)
            
    return new_parts

def get_peak_emissions_card(data):
    
    unfccc_latest_label_1 = _clean_label(data.get('unfccc_latest_label_1'))
    unfccc_latest_label_2 = _clean_label(data.get('unfccc_latest_label_2'))

    if "(without LULUCF)" in unfccc_latest_label_1:
        unfccc_latest_label_1 = unfccc_latest_label_1.replace("(without LULUCF)", "").strip()
        unfccc_latest_label_2 = "(without LULUCF)"

    peak_notes_str = _clean_label(data.get('peak_notes'))
    peak_notes_content = []
    if 'PRIMAP-hist' in peak_notes_str:
        parts = peak_notes_str.split('PRIMAP-hist')
        for i, part in enumerate(parts):
            peak_notes_content.extend(_subscript_chemical_formulas(part))
            if i < len(parts) - 1:
                peak_notes_content.append(html.A("PRIMAP-hist", href="https://zenodo.org/records/17090760", target="_blank"))
    else:
        peak_notes_content.extend(_subscript_chemical_formulas(peak_notes_str))

    peak_ghg_label_2 = _clean_label(data.get('peak_ghg_label_2'))
    peak_gross_ghg_content = _subscript_chemical_formulas(peak_ghg_label_2) if peak_ghg_label_2 else ""

    return html.Div([
        html.Div("Current and peak GHG emissions", className="section-header"),
        dbc.Table([
            html.Tbody([
                html.Tr([
                    html.Td("Latest country-reported emissions"),
                    html.Td([
                        html.B(_subscript_chemical_formulas(unfccc_latest_label_1)),
                        html.Br(),
                        *_subscript_chemical_formulas(unfccc_latest_label_2)
                    ])
                ]),
                html.Tr([html.Td("Have emissions peaked yet?"),
                         html.Td(data.get('peak_label', ''), className="fw-bold")]),
                html.Tr([
                    html.Td("Year of peak (1990 or later)"),
                    html.Td([html.B(data.get('peak_yr_label1', '')), html.Br(), data.get('peak_yr_label2', '')])
                ]),
                html.Tr([
                    html.Td("Peak emissions level"),
                    html.Td([html.B(_subscript_chemical_formulas(_clean_label(data.get('peak_ghg_label_1')))), html.Br(), *peak_gross_ghg_content])
                ]),
                html.Tr([html.Td("Notes on peak emissions"), html.Td(peak_notes_content)]),
            ])
        ], className="clean-table peak-emissions-table", bordered=False, style={'maxWidth': '550px'})
    ])