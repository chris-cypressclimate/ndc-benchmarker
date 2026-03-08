from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from .chart_utils import _get_nice_y_ticks, add_outlined_annotation
import dash_bootstrap_components as dbc
import re

def _subscript_chemical_formulas(text):
    if not text:
        return ""
    
    parts = re.split(r'(CO2e|CH4|N2O|SF6)', text)
    
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
        else:
            new_parts.append(part)
            
    return new_parts

def get_net_zero_card(data, sl_df, iso3):
    nz_year_val = data.get('nz_year')
    has_nz = pd.notna(nz_year_val)

    s2z_aligned_label = data.get('s2z_aligned_label', '')
    if s2z_aligned_label == 'N/A':
        s2z_aligned_label = '—'

    # Check if all required series are null
    required_series = ['s2z_pk_high', 's2z_ndc30_high', 's2z_latest']
    all_series_are_null = all(col not in sl_df.columns or sl_df[col].isna().all() for col in required_series)

    # Exception for countries with NZ year and 2035 NDC target
    has_2035_target = pd.notna(data.get('ndc35_low_net')) and pd.notna(data.get('ndc35_high_net'))
    show_chart_anyway = has_nz and has_2035_target

    top_table = dbc.Table([
        html.Tbody([
            html.Tr([
                html.Td("Party's target year for net zero", style={'width': '300px'}),
                html.Td(data.get('nz_year_label', ''), className="fw-bold")
            ]),
            html.Tr([
                html.Td(["Is the party's 2035 target on a credible", html.Br(), "(linear or steeper) path to net zero?"], style={'width': '300px'}),
                html.Td(s2z_aligned_label, className="fw-bold")
            ]),
        ])
    ], className="clean-table", bordered=False, style={'max-width': '550px'})

    if not has_nz or (all_series_are_null and not show_chart_anyway):
        return html.Div([
            html.Div("Credible pathways to net zero", className="section-header"),
            html.Div([
                "What is the party's goal for reaching net zero? Does the party's 2035 target imply an average pace of emissions reductions that would put it on track to reach its net-zero goal if continued?"
            ], className="graph-notes", style={'padding-bottom': '15px', 'max-width': '650px'}),
            top_table
        ])

    fig_nz = go.Figure()
    
    y_unit_text = "million tons"
    y_axis_suffix = ""
    tooltip_suffix = " Mt CO<sub>2</sub>e"
    if data.get('scale') == 1:
        y_unit_text = "kilotons"
        y_axis_suffix = ""
        tooltip_suffix = " kt CO<sub>2</sub>e"


    series_to_plot = []
    end_year = int(nz_year_val)
    sl_sub = sl_df[(sl_df['year'] >= 1990) & (sl_df['year'] <= end_year)].copy()

    if not sl_sub.empty:
        scale_mult = 1
        if data.get('scale') == 1:
            scale_mult = 1000

        sl_sub['hover_text'] = sl_sub['past_ghg_net_source'].apply(
            lambda x: '<i>National inventory data</i>' if x == 'unfccc' 
            else ('<i>Interpolated estimate</i>' if x == 'interpolated' 
                    else ('<i>Extrapolated estimate</i>' if x == 'extrapolated' else '')))

        past_ghg_net_series = sl_sub[['year', 'past_ghg_net']].dropna()
        if len(past_ghg_net_series) > 1 and (past_ghg_net_series['year'].diff().max() <= 10):
            fig_nz.add_trace(go.Scatter(x=sl_sub['year'], y=sl_sub['past_ghg_net'] * scale_mult, mode='lines',
                                        customdata=sl_sub['hover_text'],
                                        line=dict(color='black', width=3),
                                        hovertemplate='<b>%{x}</b><br>%{customdata}<br>Total emissions (incl LULUCF): %{y:,.0f}' + tooltip_suffix + '<extra></extra>'))
        else:
            fig_nz.add_trace(go.Scatter(x=past_ghg_net_series['year'], y=past_ghg_net_series['past_ghg_net'] * scale_mult, mode='markers',
                                        marker=dict(color='black', size=6),
                                        hovertemplate='<b>%{x}</b><br>Total emissions (incl LULUCF): %{y:,.0f}' + tooltip_suffix + '<extra></extra>'))
        
        last_past_year = sl_sub[sl_sub['past_ghg_net'].notna()]['year'].max()
        s2z_ndc30_high_is_missing = 's2z_ndc30_high' not in sl_sub.columns or sl_sub['s2z_ndc30_high'].isna().all()
        
        s2z_pk_high_is_null = 's2z_pk_high' not in sl_sub.columns or sl_sub['s2z_pk_high'].isna().all()
        peak_yr_after_last_past = False
        peak_yr = None
        if not s2z_pk_high_is_null:
            peak_yr = sl_sub.loc[sl_sub['s2z_pk_high'].idxmax(), 'year'] if not s2z_pk_high_is_null else None
            if peak_yr:
                peak_yr_after_last_past = peak_yr > last_past_year

        show_s2z_latest = s2z_ndc30_high_is_missing and (s2z_pk_high_is_null or peak_yr_after_last_past)

        if not s2z_pk_high_is_null:
            series_to_plot.append({
                'type': 'range', 'high': 's2z_pk_high', 'low': 's2z_pk_low',
                'label': 'Linear path from emissions peak to net zero', 'color': '#296186', 'fillcolor': 'rgba(41, 97, 134, 0.2)',
                'marker_year': peak_yr + 2 if peak_yr else None,
                'tooltip_label_high': 'Linear from peak to net zero (upper): ',
                'tooltip_label_low': 'Linear from peak to net zero (lower): '
            })
        if show_s2z_latest:
            series_to_plot.append({
                'type': 'line', 'name': 's2z_latest',
                'label': 'Linear path from current levels to net zero', 'color': '#43a2ca', 'marker_year': 2026,
                'tooltip_label': 'Linear from current to net zero: '
            })
        if not s2z_ndc30_high_is_missing:
            series_to_plot.append({
                'type': 'range', 'high': 's2z_ndc30_high', 'low': 's2z_ndc30_low',
                'label': 'Linear path from 2030 NDC to net zero', 'color': '#7bccc4', 'fillcolor': 'rgba(123, 204, 196, 0.2)',
                'marker_year': 2032,
                'tooltip_label_high': 'Linear from 2030 NDC to net zero (upper): ',
                'tooltip_label_low': 'Linear from 2030 NDC to net zero (lower): '
            })

        for series in series_to_plot:
            if series['type'] == 'range':
                if series['high'] in sl_sub.columns and series['low'] in sl_sub.columns:
                    # Plot the high and low lines for the fill
                    fig_nz.add_trace(go.Scatter(x=sl_sub['year'], y=sl_sub[series['high']] * scale_mult, mode='lines',
                                                line=dict(color=series['color'], dash='dot', width=3), showlegend=False, hoverinfo='none'))
                    fig_nz.add_trace(go.Scatter(x=sl_sub['year'], y=sl_sub[series['low']] * scale_mult, mode='lines',
                                                line=dict(color=series['color'], dash='dot', width=3), fill='tonexty',
                                                fillcolor=series['fillcolor'],
                                                showlegend=False, hoverinfo='none'))
            elif series['type'] == 'line':
                if series['name'] in sl_sub.columns:
                    fig_nz.add_trace(go.Scatter(x=sl_sub['year'], y=sl_sub[series['name']] * scale_mult, mode='lines',
                                                line=dict(color=series['color'], dash='dot', width=3), hoverinfo='none', showlegend=False))

        all_vals_fig_nz = pd.Series(dtype='float64')
        cols_to_check_fig_nz = ['past_ghg_net', 's2z_pk_high', 's2z_ndc30_high', 's2z_latest', 'ndc35pt_low', 'ndc35pt_high', 'ndc30pt_low', 'ndc30pt_high']
        for col in cols_to_check_fig_nz:
            if col in sl_sub.columns and sl_sub[col].notna().any():
                all_vals_fig_nz = pd.concat([all_vals_fig_nz, sl_sub[col] * scale_mult])

        y_axis_config_fig_nz = _get_nice_y_ticks(all_vals_fig_nz, suffix=y_axis_suffix)
        
        min_year = sl_sub['year'].min()
        tickvals = [min_year, last_past_year, 2035, end_year]
        ticktext = [f"{val:.0f}" for val in tickvals]
        ticktext[2] = f"<b>{ticktext[2]}</b>"

        if pd.notna(last_past_year):
            fig_nz.add_shape(type="rect", xref="x", yref="paper", x0=last_past_year, y0=0, x1=end_year, y1=1, fillcolor="#f5f5f0", layer="below", line_width=0)

        def add_circled_marker(fig, x, y, number, color):
            fig.add_trace(go.Scatter(
                x=[x], y=[y],
                mode='markers+text',
                marker=dict(color=color, size=18, symbol='circle'),
                text=f"<b>{number}</b>",
                textfont=dict(color='white', size=10),
                hoverinfo='none',
                showlegend=False
            ))

        for i, series in enumerate(series_to_plot):
            if series['marker_year'] and series['marker_year'] in sl_sub['year'].values:
                if series['type'] == 'range':
                    high_val = sl_sub.loc[sl_sub['year'] == series['marker_year'], series['high']].values[0] * scale_mult
                    low_val = sl_sub.loc[sl_sub['year'] == series['marker_year'], series['low']].values[0] * scale_mult
                    if pd.notna(high_val) and pd.notna(low_val):
                        marker_val = (high_val + low_val) / 2
                        add_circled_marker(fig_nz, series['marker_year'], marker_val, i + 1, series['color'])
                elif series['type'] == 'line':
                    marker_val = sl_sub.loc[sl_sub['year'] == series['marker_year'], series['name']].values[0] * scale_mult
                    if pd.notna(marker_val):
                        add_circled_marker(fig_nz, series['marker_year'], marker_val, i + 1, series['color'])

        if 2035 in sl_sub['year'].values:
            ndc35_low = sl_sub.loc[sl_sub['year'] == 2035, 'ndc35pt_low'].values[0] * scale_mult
            ndc35_high = sl_sub.loc[sl_sub['year'] == 2035, 'ndc35pt_high'].values[0] * scale_mult
            
            if pd.notna(ndc35_low) or pd.notna(ndc35_high):
                fig_nz.add_trace(go.Scatter(x=[2035, 2035], y=[ndc35_low, ndc35_high], mode='markers', marker=dict(color='white', size=6, line=dict(color='black', width=1.5)), hoverinfo='none', showlegend=False))
                add_outlined_annotation(fig_nz, 2035, ndc35_high, "<b>2035<br>NDC</b>", "bottom", yshift=-1, xanchor='left', xshift=2)
                
                if pd.notna(ndc35_low) and pd.notna(ndc35_high) and ndc35_low == ndc35_high:
                    fig_nz.add_trace(go.Scatter(x=[2035], y=[ndc35_high], mode='markers', marker=dict(opacity=0), hovertemplate='<b>2035</b><br>2035 NDC: %{y:,.0f}' + tooltip_suffix + '<extra></extra>', showlegend=False))
                else:
                    if pd.notna(ndc35_high):
                        fig_nz.add_trace(go.Scatter(x=[2035], y=[ndc35_high], mode='markers', marker=dict(opacity=0), hovertemplate='<b>2035</b><br>2035 NDC (upper): %{y:,.0f}' + tooltip_suffix + '<extra></extra>', showlegend=False))
                    if pd.notna(ndc35_low):
                        fig_nz.add_trace(go.Scatter(x=[2035], y=[ndc35_low], mode='markers', marker=dict(opacity=0), hovertemplate='<b>2035</b><br>2035 NDC (lower): %{y:,.0f}' + tooltip_suffix + '<extra></extra>', showlegend=False))

            for series in series_to_plot:
                if series['type'] == 'range':
                    if 2035 in sl_sub['year'].values:
                        high_val = sl_sub.loc[sl_sub['year'] == 2035, series['high']].values[0] * scale_mult
                        low_val = sl_sub.loc[sl_sub['year'] == 2035, series['low']].values[0] * scale_mult
                        
                        if pd.notna(high_val):
                            fig_nz.add_trace(go.Scatter(x=[2035], y=[high_val], mode='markers', marker=dict(opacity=0), hovertemplate='<b>2035</b><br>' + series['tooltip_label_high'] + '%{y:,.0f}' + tooltip_suffix + '<extra></extra>', showlegend=False))
                        if pd.notna(low_val):
                            fig_nz.add_trace(go.Scatter(x=[2035], y=[low_val], mode='markers', marker=dict(opacity=0), hovertemplate='<b>2035</b><br>' + series['tooltip_label_low'] + '%{y:,.0f}' + tooltip_suffix + '<extra></extra>', showlegend=False))
                elif series['type'] == 'line' and series['name'] == 's2z_latest':
                    if 2035 in sl_sub['year'].values:
                        line_val = sl_sub.loc[sl_sub['year'] == 2035, series['name']].values[0] * scale_mult
                        if pd.notna(line_val):
                            fig_nz.add_trace(go.Scatter(x=[2035], y=[line_val], mode='markers', marker=dict(opacity=0), hovertemplate='<b>2035</b><br>' + series['tooltip_label'] + '%{y:,.0f}' + tooltip_suffix + '<extra></extra>', showlegend=False))

        if not sl_sub[sl_sub['year'] == 2030].empty and (pd.notna(sl_sub.loc[sl_sub['year'] == 2030, 'ndc30pt_low'].values[0]) or pd.notna(sl_sub.loc[sl_sub['year'] == 2030, 'ndc30pt_high'].values[0])):
            ndc30_low = sl_sub.loc[sl_sub['year'] == 2030, 'ndc30pt_low'].values[0] * scale_mult
            ndc30_high = sl_sub.loc[sl_sub['year'] == 2030, 'ndc30pt_high'].values[0] * scale_mult
            fig_nz.add_trace(go.Scatter(x=[2030, 2030], y=[ndc30_low, ndc30_high], mode='markers', marker=dict(color='white', size=6, line=dict(color='black', width=1.5)), hoverinfo='none', showlegend=False))
            add_outlined_annotation(fig_nz, 2030, ndc30_high, "<b>2030<br>NDC</b>", "bottom", yshift=5, xanchor='center', xshift=0)

            if pd.notna(ndc30_low) and pd.notna(ndc30_high) and ndc30_low == ndc30_high:
                fig_nz.add_trace(go.Scatter(x=[2030], y=[ndc30_high], mode='markers', marker=dict(opacity=0), hovertemplate='<b>2030</b><br>2030 NDC: %{y:,.0f}' + tooltip_suffix + '<extra></extra>', showlegend=False))
            else:
                if pd.notna(ndc30_high):
                    fig_nz.add_trace(go.Scatter(x=[2030], y=[ndc30_high], mode='markers', marker=dict(opacity=0), hovertemplate='<b>2030</b><br>2030 NDC (upper): %{y:,.0f}' + tooltip_suffix + '<extra></extra>', showlegend=False))
                if pd.notna(ndc30_low):
                    fig_nz.add_trace(go.Scatter(x=[2030], y=[ndc30_low], mode='markers', marker=dict(opacity=0), hovertemplate='<b>2030</b><br>2030 NDC (lower): %{y:,.0f}' + tooltip_suffix + '<extra></extra>', showlegend=False))

        add_outlined_annotation(fig_nz, end_year, 0, "<b>Net zero<br>target</b>", "bottom", yshift=5, xanchor='center', xshift=0)
        
        fig_nz.update_layout(
            template='plotly_white',
            margin=dict(l=20, r=15, t=20, b=40),
            xaxis=dict(tickvals=tickvals, ticktext=ticktext, showgrid=False, showline=True, linecolor='lightgrey', linewidth=1, ticks='outside', tickson='boundaries', fixedrange=True),
            yaxis=dict(y_axis_config_fig_nz, fixedrange=True),
            showlegend=False,
            hovermode="closest",
            hoverlabel=dict(
                bgcolor="rgba(255, 255, 255, 0.95)",
                bordercolor="black",
                font=dict(
                    color="#333333"
                )
            ),
            font=dict(family="Libre Franklin", size=14, color="#7f7f7f"),
        )

    table_header = [html.Thead(html.Tr([html.Th(""), html.Th("Emissions in 2035", style={'font-weight': 'normal', 'font-style': 'normal', 'color': '#7f7f7f'})]))]
    table_rows = [html.Tr([html.Td("2035 NDC target range"), html.Td(data.get('ndc35_label', ''), className="fw-bold")])]
    for i, series in enumerate(series_to_plot):
        table_rows.append(
            html.Tr([
                html.Td([
                    html.Span(str(i + 1), className="badge-circle", style={'backgroundColor': series['color']}),
                    series['label']
                ]),
                html.Td(data.get(f"s2z_{series['high'].split('_')[1] if series['type'] == 'range' else series['name'].split('_')[1]}_label", ''), className="fw-bold")
            ])
        )
    
    notes_div = html.Div()
    if pd.notna(data.get('nz_notes')) and data.get('nz_notes'):
        notes_div = dcc.Markdown(f"**Notes:** {data.get('nz_notes', '')}", className="graph-notes")

    data_sources_text = "**Data source:** Past emissions from official national inventory data reported to UN and [PRIMAP-hist](https://zenodo.org/records/17090760) estimates; net zero target years from [Climate Watch](https://www.climatewatchdata.org/net-zero-tracker) and [Net Zero Tracker](https://zerotracker.net/)."
    if data.get('iso3') == 'IND':
        data_sources_text = '**Data source:** Past emissions from official national inventory data reported to UN and [PRIMAP-hist](https://zenodo.org/records/17090760) estimates; emissions peak estimate from [Cui et al (2025)](http://www.country-ambition.cgs.umd.edu/); net zero target years from [Climate Watch](https://www.climatewatchdata.org/net-zero-tracker) and [Net Zero Tracker](https://zerotracker.net/).'

    data_sources_div = dcc.Markdown(data_sources_text, className="graph-notes")

    return html.Div([
        html.Div("Credible pathways to net zero", className="section-header"),
        html.Div([
            "What is the party's goal for reaching net zero? Does the party's 2035 target imply an average pace of emissions reductions that would put it on track to reach its net-zero goal if continued?"
        ], className="graph-notes", style={'padding-bottom': '15px', 'max-width': '650px'}),
        top_table,
        html.Div([
            html.Div(html.B("Linear trajectories to net zero"), style={'font-family': 'Libre Franklin', 'font-size': '16px', 'color': 'black'}),
            dbc.Table(table_header + [html.Tbody(table_rows)], className="clean-table compact-table net-zero-summary-table", bordered=False, style={'font-size': '14px'}),
            html.Div(f"Total emissions ({y_unit_text} CO2e)", style={'font-size': '14px', 'color': '#7f7f7f'}),
            dcc.Graph(figure=fig_nz, id='net-zero-chart', config={'displayModeBar': False, 'responsive': True}, style={'height': '450px', 'width': '100%', 'maxWidth': '550px'}),
        ], className="chart-with-table", style={'background-color': 'white', 'max-width': '550px', 'margin-top': '20px', 'paddingLeft': '10px', 'paddingTop': '10px'}),
        dbc.Button("Download chart data", id="download-net-zero-chart-csv-data", color="primary", className="mb-3", size="sm", style={'fontSize': '0.85rem', 'backgroundColor': '#7bccc4', 'border': 'none'}),
        data_sources_div,
        notes_div
    ])