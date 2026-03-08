from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from .chart_utils import _get_nice_y_ticks, add_outlined_annotation
import dash_bootstrap_components as dbc
from data_loader import dfs
import re
from plotly.subplots import make_subplots
import copy

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
        elif part[0:2] == "N2":
            new_parts.append("N")
            new_parts.append(html.Sub("2"))
            new_parts.append("O")
        elif part == "SF6":
            new_parts.append("SF")
            new_parts.append(html.Sub("6"))
        else:
            new_parts.append(part)
            
    return new_parts

def get_scenarios_card(data, sc_df):
    has_nz = pd.notna(data.get('nz_year'))
    sc_end_year = 2050
    sc_sub = sc_df[(sc_df['year'] >= 1990) & (sc_df['year'] <= sc_end_year)].copy()
    sc_sub['hover_text'] = sc_sub['past_ghg_net_source'].apply(
        lambda x: '<i>National inventory data</i>' if x == 'unfccc' 
        else ('<i>Interpolated estimate</i>' if x == 'interpolated' 
                else ('<i>Extrapolated estimate</i>' if x == 'extrapolated' else '')))
    sc_ranges = sc_sub[sc_sub['year'] >= 2025]
    scale_mult = 1
    y_axis_suffix = " Mt"
    tooltip_suffix = " Mt CO<sub>2</sub>e"
    y_unit = "million tons"
    if data.get('scale') == 1:
        scale_mult = 1000
        y_axis_suffix = " kt"
        tooltip_suffix = " kt CO<sub>2</sub>e"
        y_unit = "kilotons"

    has_ndc35 = pd.notna(data.get('ndc35_low_net')) and pd.notna(data.get('ndc35_high_net'))

    fig_ipcc = go.Figure()
    ipcc_layers = [
        ('c7', '#f03b20', "4°C"),
        ('c6', '#fd8d3c', "3°C"),
        ('c5', '#fecc5c', "2.5°C"),
        ('c4', '#bae4bc', "2°C (>50% chance)"),
        ('c3', '#7bccc4', "2°C (>67% chance)"),
        ('c2', '#43a2ca', "1.5°C (after high overshoot)"),
        ('c1', '#296186', "1.5°C")
    ]

    has_ipcc_data = False
    for i, (prefix, color, label) in enumerate(ipcc_layers):
        low_col = 'c1_ghg_p5' if i < 6 else f'{prefix}_ghg_p5'
        high_col = f'{prefix}_ghg_p95'
        
        if high_col in sc_ranges.columns and low_col in sc_ranges.columns and (sc_ranges[high_col].notna().any() or sc_ranges[low_col].notna().any()):
            has_ipcc_data = True
            font_color = 'white' if prefix in ['c1', 'c2', 'c7', 'c8'] else 'black'
            
            fig_ipcc.add_trace(go.Scatter(
                x=sc_ranges['year'], y=sc_ranges[low_col] * scale_mult,
                mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'
            ))
            fig_ipcc.add_trace(go.Scatter(
                x=sc_ranges['year'], y=sc_ranges[high_col] * scale_mult,
                fill='tonexty', mode='lines', line=dict(width=0), fillcolor=color,
                name=label,
                hovertemplate=f'{label}<extra></extra>',
                hoverlabel=dict(
                    bgcolor=color,
                    font=dict(color=font_color, size=14)
                )
            ))

    if 'past_ghg_net' in sc_sub.columns and sc_sub['past_ghg_net'].notna().any():
        past_ghg_net_series = sc_sub[['year', 'past_ghg_net']].dropna()
        if len(past_ghg_net_series) > 1 and (past_ghg_net_series['year'].diff().max() <= 10):
            fig_ipcc.add_trace(go.Scatter(x=sc_sub['year'], y=sc_sub['past_ghg_net'] * scale_mult, mode='lines',
                                          line=dict(color='black', width=3),
                                          customdata=sc_sub['hover_text'],
                                          hovertemplate='<b>%{x}</b><br>%{customdata}<br>Total emissions (incl LULUCF): %{y:,.0f}' + tooltip_suffix + '<extra></extra>',
                                          hoverlabel=dict(
                                              bgcolor="rgba(255, 255, 255, 0.9)",
                                              bordercolor="black",
                                              font=dict(color="black")
                                          )))
        else:
            fig_ipcc.add_trace(go.Scatter(x=past_ghg_net_series['year'], y=past_ghg_net_series['past_ghg_net'] * scale_mult, mode='markers',
                                          marker=dict(color='black', size=6),
                                          customdata=past_ghg_net_series.index.map(sc_sub['hover_text']),
                                          hovertemplate='<b>%{x}</b><br>%{customdata}<br>Total emissions (incl LULUCF): %{y:,.0f}' + tooltip_suffix + '<extra></extra>',
                                          hoverlabel=dict(
                                              bgcolor="rgba(255, 255, 255, 0.9)",
                                              bordercolor="black",
                                              font=dict(color="black")
                                          )))
    if has_ndc35:
        n35_low = sc_sub.loc[sc_sub['year'] == 2035, 'ndc35pt_low'].values[0] * scale_mult
        n35_high = sc_sub.loc[sc_sub['year'] == 2035, 'ndc35pt_high'].values[0] * scale_mult
        mid_point = (n35_low + n35_high) / 2
        fig_ipcc.add_trace(go.Scatter(x=[2035], y=[n35_low], mode='markers',
                                      marker=dict(color='white', size=6, line=dict(color='black', width=1.5)),
                                      hovertemplate='<b>2035</b><br>2035 NDC (lower): %{y:,.0f}' + tooltip_suffix + '<extra></extra>', showlegend=False))
        fig_ipcc.add_trace(go.Scatter(x=[2035], y=[n35_high], mode='markers',
                                      marker=dict(color='white', size=6, line=dict(color='black', width=1.5)),
                                      hovertemplate='<b>2035</b><br>2035 NDC (upper): %{y:,.0f}' + tooltip_suffix + '<extra></extra>', showlegend=False))
        add_outlined_annotation(fig_ipcc, 2035, mid_point, "<b>2035<br>NDC</b>", "middle", yshift=0, xanchor='left', xshift=5)


    all_vals_fig_ipcc_2035 = pd.Series(dtype='float64')
    for prefix, _, _ in ipcc_layers:
        if prefix == 'c8':
            continue
        if f'{prefix}_ghg_p5' in sc_ranges.columns and sc_ranges[sc_ranges['year'] == 2035][f'{prefix}_ghg_p5'].notna().any():
            all_vals_fig_ipcc_2035 = pd.concat([all_vals_fig_ipcc_2035, sc_ranges[sc_ranges['year'] == 2035][f'{prefix}_ghg_p5'] * scale_mult])
        if f'{prefix}_ghg_p95' in sc_ranges.columns and sc_ranges[sc_ranges['year'] == 2035][f'{prefix}_ghg_p95'].notna().any():
            all_vals_fig_ipcc_2035 = pd.concat([all_vals_fig_ipcc_2035, sc_ranges[sc_ranges['year'] == 2035][f'{prefix}_ghg_p95'] * scale_mult])
    if 'past_ghg_net' in sc_sub.columns and sc_sub['past_ghg_net'].notna().any():
        all_vals_fig_ipcc_2035 = pd.concat([all_vals_fig_ipcc_2035, sc_sub['past_ghg_net'] * scale_mult])
    if has_ndc35:
        n35_low = sc_sub.loc[sc_sub['year'] == 2035, 'ndc35pt_low']
        n35_high = sc_sub.loc[sc_sub['year'] == 2035, 'ndc35pt_high']
        all_vals_fig_ipcc_2035 = pd.concat([all_vals_fig_ipcc_2035, pd.Series([n35_low.values[0] * scale_mult])])
        all_vals_fig_ipcc_2035 = pd.concat([all_vals_fig_ipcc_2035, pd.Series([n35_high.values[0] * scale_mult])])

    y_axis_config_fig_ipcc = _get_nice_y_ticks(all_vals_fig_ipcc_2035, padding_multiplier=0.05)

    if not has_ipcc_data:
        fig_ipcc.add_annotation(
            text="No IPCC<br>scenario data",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=40, color="lightgrey")
        )

    fig_ipcc.update_layout(
        template='plotly_white', margin=dict(l=20, r=20, t=10, b=40),
        xaxis=dict(tickvals=[1990, 2025, 2035, sc_end_year], ticktext=["1990", "2025", "<b>2035</b>", str(sc_end_year)], showgrid=False, showline=True, linecolor='lightgrey', linewidth=1, ticks='outside', tickson='boundaries', fixedrange=True),
        yaxis=dict(y_axis_config_fig_ipcc, fixedrange=True),
        showlegend=False,
        hovermode="closest",
        font=dict(family="Libre Franklin", size=14, color="#7f7f7f")
    )

    # IPCC Jitter Plot
    fig_jitter = go.Figure()

    jitter_df = dfs['ipcc_scenarios']
    country_iso = data.get('iso3')
    country_jitter_df = jitter_df[jitter_df['iso3'] == country_iso]

    category_map = {
        "C1": "<b>1.5°C</b>",
        "C2": "<b>1.5°C<br>with<br>overshoot</b>",
        "C3": "<b>2°C<br>(>67%)</b>",
        "C4": "<b>2°C<br>(>50%)</b>",
        "C5": "<b>2.5°C</b>",
        "C6": "<b>3°C</b>",
        "C7": "<b>4°C</b>"
    }
    
    color_map = {
        "C1" : '#296186',
        "C2" : '#43a2ca',
        "C3" : '#7bccc4',
        "C4" : '#bae4bc',
        "C5" : '#fecc5c',
        "C6" : '#fd8d3c',
        "C7" : '#f03b20'
    }

    has_ipcc_jitter_data = False
    for i, category in enumerate(category_map.keys()):
        cat_df = country_jitter_df[country_jitter_df['category'] == category]
        if not cat_df.empty:
            has_ipcc_jitter_data = True
            x_jitter = np.random.uniform(-0.1, 0.1, size=len(cat_df))
            fig_jitter.add_trace(go.Scatter(
                y=cat_df['ipcc_ghg_tot'] * scale_mult,
                x=i + x_jitter,
                mode='markers',
                name=category_map[category],
                marker=dict(
                    color=color_map[category],
                    opacity=0.4,
                    line=dict(
                        color=color_map[category],
                        width=0.2
                    )
                ),
                hovertemplate='%{y:,.0f}<extra></extra>',
                hoverlabel=dict(
                    bgcolor=color_map[category],
                    font=dict(color='white' if category in ['C1', 'C2', 'C7'] else 'black')
                ),
                showlegend=False
            ))

    if has_ndc35:
        n35_low = sc_sub.loc[sc_sub['year'] == 2035, 'ndc35pt_low']
        n35_high = sc_sub.loc[sc_sub['year'] == 2035, 'ndc35pt_high']
        fig_jitter.add_hline(y=n35_low.values[0] * scale_mult, line_dash="dot", line_color="black", line_width=1)
        fig_jitter.add_hline(y=n35_high.values[0] * scale_mult, line_dash="dot", line_color="black", line_width=1)
        add_outlined_annotation(fig_jitter, -0.4, n35_high.values[0] * scale_mult, "<b>2035 NDC range</b>", "bottom", yshift=2, xanchor="left", xshift=0)


    if not has_ipcc_jitter_data:
        fig_jitter.add_annotation(
            text="No IPCC<br>scenario data",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=40, color="lightgrey")
        )

    fig_jitter.update_layout(
        template='plotly_white',
        yaxis=y_axis_config_fig_ipcc,
        xaxis=dict(
            tickvals=list(range(len(category_map))),
            ticktext=list(category_map.values()),
            showgrid=False,
            showline=True,
            zeroline=False,
            tickson='boundaries',
            tickangle=0,
            tickfont=dict(size=11, weight='bold'),
            fixedrange=True
        ),
        margin=dict(l=0, r=20, t=10, b=40),
        font=dict(family="Libre Franklin", size=14, color="#7f7f7f"),
        showlegend=False,
        hovermode="closest"
    )

    fig_ngfs = go.Figure()
    ngfs_layers = [
        ('cp', '#f03b20', "3°C"), 
        ('fw', '#fecc5c', "2.4°C"),
        ('b2c', '#43a2ca', "1.8°C"), 
        ('nz', '#296186', "1.4°C (after 1.7°C overshoot)")
    ]
    has_ngfs_data = False
    for prefix, color, label in ngfs_layers:
        min_col = 'nz_min' if prefix != 'nz' else f'{prefix}_min'
        if min_col in sc_ranges.columns and f'{prefix}_max' in sc_ranges.columns and sc_ranges[min_col].notna().any() and sc_ranges[f'{prefix}_max'].notna().any():
            has_ngfs_data = True
            fig_ngfs.add_trace(go.Scatter(
                x=sc_ranges['year'], y=sc_ranges[min_col] * scale_mult,
                mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'
            ))
            fig_ngfs.add_trace(go.Scatter(
                x=sc_ranges['year'], y=sc_ranges[f'{prefix}_max'] * scale_mult,
                fill='tonexty', mode='lines', line=dict(width=0), fillcolor=color,
                name=label,
                hovertemplate=f'{label}<extra></extra>',
                hoverlabel=dict(
                    bgcolor=color,
                    font=dict(color='black' if prefix in ['fw', 'b2c'] else 'white', size=14)
                )
            ))
    if 'past_ghg_net' in sc_sub.columns and sc_sub['past_ghg_net'].notna().any():
        past_ghg_net_series = sc_sub[['year', 'past_ghg_net']].dropna()
        if len(past_ghg_net_series) > 1 and (past_ghg_net_series['year'].diff().max() <= 10):
            fig_ngfs.add_trace(go.Scatter(x=sc_sub['year'], y=sc_sub['past_ghg_net'] * scale_mult, mode='lines',
                                          line=dict(color='black', width=3),
                                          customdata=sc_sub['hover_text'],
                                          hovertemplate='<b>%{x}</b><br>%{customdata}<br>Total emissions (incl LULUCF): %{y:,.0f}' + tooltip_suffix + '<extra></extra>',
                                          hoverlabel=dict(
                                              bgcolor="rgba(255, 255, 255, 0.9)",
                                              bordercolor="black",
                                              font=dict(color="black")
                                          )))
        else:
            fig_ngfs.add_trace(go.Scatter(x=past_ghg_net_series['year'], y=past_ghg_net_series['past_ghg_net'] * scale_mult, mode='markers',
                                          marker=dict(color='black', size=6),
                                          customdata=past_ghg_net_series.index.map(sc_sub['hover_text']),
                                          hovertemplate='<b>%{x}</b><br>%{customdata}<br>Total emissions (incl LULUCF): %{y:,.0f}' + tooltip_suffix + '<extra></extra>',
                                          hoverlabel=dict(
                                              bgcolor="rgba(255, 255, 255, 0.9)",
                                              bordercolor="black",
                                              font=dict(color="black")
                                          )))
    if has_ndc35:
        n35_low = sc_sub.loc[sc_sub['year'] == 2035, 'ndc35pt_low'].values[0] * scale_mult
        n35_high = sc_sub.loc[sc_sub['year'] == 2035, 'ndc35pt_high'].values[0] * scale_mult
        mid_point = (n35_low + n35_high) / 2
        fig_ngfs.add_trace(go.Scatter(x=[2035], y=[n35_low], mode='markers',
                                      marker=dict(color='white', size=6, line=dict(color='black', width=1.5)),
                                      hovertemplate='<b>2035</b><br>2035 NDC (lower): %{y:,.0f}' + tooltip_suffix + '<extra></extra>', showlegend=False))
        fig_ngfs.add_trace(go.Scatter(x=[2035], y=[n35_high], mode='markers',
                                      marker=dict(color='white', size=6, line=dict(color='black', width=1.5)),
                                      hovertemplate='<b>2035</b><br>2035 NDC (upper): %{y:,.0f}' + tooltip_suffix + '<extra></extra>', showlegend=False))
        add_outlined_annotation(fig_ngfs, 2035, mid_point, "<b>2035<br>NDC</b>", "middle", yshift=0, xanchor='left', xshift=5)


    all_vals_fig_ngfs_2035 = pd.Series(dtype='float64')
    for prefix, _, _ in ngfs_layers:
        min_col = 'nz_min' if prefix != 'nz' else f'{prefix}_min'
        if min_col in sc_ranges.columns and sc_ranges[sc_ranges['year'] == 2035][min_col].notna().any():
            all_vals_fig_ngfs_2035 = pd.concat([all_vals_fig_ngfs_2035, sc_ranges[sc_ranges['year'] == 2035][min_col] * scale_mult])
        if f'{prefix}_max' in sc_ranges.columns and sc_ranges[sc_ranges['year'] == 2035][f'{prefix}_max'].notna().any():
            all_vals_fig_ngfs_2035 = pd.concat([all_vals_fig_ngfs_2035, sc_ranges[sc_ranges['year'] == 2035][f'{prefix}_max'] * scale_mult])
    if 'past_ghg_net' in sc_sub.columns and sc_sub['past_ghg_net'].notna().any():
        all_vals_fig_ngfs_2035 = pd.concat([all_vals_fig_ngfs_2035, sc_sub['past_ghg_net'] * scale_mult])
    if has_ndc35:
        n35_low = sc_sub.loc[sc_sub['year'] == 2035, 'ndc35pt_low']
        n35_high = sc_sub.loc[sc_sub['year'] == 2035, 'ndc35pt_high']
        all_vals_fig_ngfs_2035 = pd.concat([all_vals_fig_ngfs_2035, pd.Series([n35_low.values[0] * scale_mult])])
        all_vals_fig_ngfs_2035 = pd.concat([all_vals_fig_ngfs_2035, pd.Series([n35_high.values[0] * scale_mult])])

    y_axis_config_fig_ngfs = _get_nice_y_ticks(all_vals_fig_ngfs_2035, padding_multiplier=0.1)

    if not has_ngfs_data:
        fig_ngfs.add_annotation(
            text="No NGFS<br>scenario data",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=40, color="lightgrey")
        )

    fig_ngfs.update_layout(
        template='plotly_white', margin=dict(l=20, r=20, t=10, b=40),
        xaxis=dict(tickvals=[1990, 2025, 2035, sc_end_year], ticktext=["1990", "2025", "<b>2035</b>", str(sc_end_year)], showgrid=False, showline=True, linecolor='lightgrey', linewidth=1, ticks='outside', tickson='boundaries', fixedrange=True),
        yaxis=dict(y_axis_config_fig_ngfs, fixedrange=True),
        showlegend=False,
        hovermode="closest",
        font=dict(family="Libre Franklin", size=14, color="#7f7f7f")
    )

    # NGFS Jitter Plot
    fig_ngfs_jitter = go.Figure()

    ngfs_jitter_df = dfs['ngfs_scatter']
    country_iso = data.get('iso3')
    country_ngfs_jitter_df = ngfs_jitter_df[ngfs_jitter_df['iso3'] == country_iso]

    ngfs_category_map = {
        "nz": "1.4°C",
        "b2c": "1.8°C",
        "fw": "2.4°C",
        "cp": "3°C"
    }

    ngfs_color_map = {
        "1.4°C" : '#296186',
        "1.8°C" : '#43a2ca',
        "2.4°C" : '#fecc5c',
        "3°C" : '#f03b20'
    }

    has_ngfs_jitter_data = False
    for i, category in enumerate(ngfs_category_map.keys()):
        cat_df = country_ngfs_jitter_df[country_ngfs_jitter_df['catgen'] == category]
        if not cat_df.empty:
            has_ngfs_jitter_data = True
            min_y = cat_df['ngfs_ghg'].min() * scale_mult
            max_y = cat_df['ngfs_ghg'].max() * scale_mult
            fig_ngfs_jitter.add_trace(go.Scatter(
                x=[i, i],
                y=[min_y, max_y],
                mode='lines',
                line=dict(
                    color=ngfs_color_map[ngfs_category_map[category]],
                    width=10
                ),
                hoverinfo='none',
                showlegend=False
            ))
            
            # Add invisible markers for tooltips
            fig_ngfs_jitter.add_trace(go.Scatter(
                x=[i],
                y=[min_y],
                mode='markers',
                marker=dict(opacity=0),
                hovertemplate='Min: %{y:,.0f}<extra></extra>',
                hoverlabel=dict(
                    bgcolor=ngfs_color_map[ngfs_category_map[category]],
                    font=dict(color='white' if ngfs_category_map[category] in ['1.4°C', '1.8°C', '3°C'] else 'black')
                ),
                showlegend=False
            ))
            fig_ngfs_jitter.add_trace(go.Scatter(
                x=[i],
                y=[max_y],
                mode='markers',
                marker=dict(opacity=0),
                hovertemplate='Max: %{y:,.0f}<extra></extra>',
                hoverlabel=dict(
                    bgcolor=ngfs_color_map[ngfs_category_map[category]],
                    font=dict(color='white' if ngfs_category_map[category] in ['1.4°C', '1.8°C', '3°C'] else 'black')
                ),
                showlegend=False
            ))

    if has_ndc35:
        n35_low = sc_sub.loc[sc_sub['year'] == 2035, 'ndc35pt_low']
        n35_high = sc_sub.loc[sc_sub['year'] == 2035, 'ndc35pt_high']
        fig_ngfs_jitter.add_hline(y=n35_low.values[0] * scale_mult, line_dash="dot", line_color="black", line_width=1)
        fig_ngfs_jitter.add_hline(y=n35_high.values[0] * scale_mult, line_dash="dot", line_color="black", line_width=1)
        add_outlined_annotation(fig_ngfs_jitter, -0.4, n35_high.values[0] * scale_mult, "<b>2035 NDC range</b>", "bottom", yshift=2, xanchor="left", xshift=0)


    if not has_ngfs_jitter_data:
        fig_ngfs_jitter.add_annotation(
            text="No NGFS<br>scenario data",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=40, color="lightgrey")
        )

    fig_ngfs_jitter.update_layout(
        template='plotly_white',
        yaxis=y_axis_config_fig_ipcc,
        xaxis=dict(
            tickvals=list(range(len(ngfs_category_map))),
            ticktext=[f"<b>{v.replace('°C', '°C<br>')}</b>" for v in ngfs_category_map.values()],
            showgrid=False,
            showline=True,
            zeroline=False,
            tickson='boundaries',
            tickangle=0,
            tickfont=dict(size=14),
            fixedrange=True
        ),
        margin=dict(l=0, r=20, t=10, b=40),
        font=dict(family="Libre Franklin", size=14, color="#7f7f7f"),
        showlegend=False,
        hovermode="closest"
    )

    low_label_ipcc = data.get('ndc35_low_ipcc_label', '')
    high_label_ipcc = data.get('ndc35_high_ipcc_label', '')

    label_map = {
        "1.5°C (>50% chance)": "1.5°C",
        "1.5°C with overshoot (>50% chance)": "1.5°C (after high overshoot)",
        "1.5°C after high overshoot (>50% chance)": "1.5°C (after high overshoot)",
        "2°C (>67% chance)": "2°C (>67% chance)",
        "2°C (>50% chance)": "2°C (>50% chance)",
        "2.5°C (>50% chance)": "2.5°C",
        "3°C (>50% chance)": "3°C",
        "4°C (>50% chance)": "4°C",
    }
    low_label_ipcc = label_map.get(low_label_ipcc, low_label_ipcc)
    high_label_ipcc = label_map.get(high_label_ipcc, high_label_ipcc)

    style_map = {
        "1.5°C": {"color": "#296186", "fontWeight": "bold"},
        "1.5°C with overshoot": {"color": "#43a2ca", "fontWeight": "bold"},
        "1.5°C (after high overshoot)": {"color": "#43a2ca", "fontWeight": "bold"},
        "2°C (>67% chance)": {"color": "#7bccc4", "fontWeight": "bold"},
        "2°C (>50% chance)": {"color": "#bae4bc", "fontWeight": "bold"},
        "2.5°C": {"color": "#fecc5c", "fontWeight": "bold"},
        "3°C": {"color": "#fd8d3c", "fontWeight": "bold"},
        "4°C": {"color": "#f03b20", "fontWeight": "bold"},
    }

    ngfs_style_map = {
        "1.4°C": {"color": "#296186", "fontWeight": "bold"},
        "1.8°C": {"color": "#43a2ca", "fontWeight": "bold"},
        "2.4°C": {"color": "#fecc5c", "fontWeight": "bold"},
        "3°C": {"color": "#f03b20", "fontWeight": "bold"},
    }

    ipcc_summary = html.Div([
        html.Span("The party's 2035 target is in the range of "),
        html.A("IPCC AR6", href="https://www.ipcc.ch/assessment-report/ar6/", target="_blank"),
        html.Span(" least-cost scenarios for "),
        html.Span(low_label_ipcc, style=style_map.get(low_label_ipcc, {})),
        html.Span(" to "),
        html.Span(high_label_ipcc, style=style_map.get(high_label_ipcc, {})),
        html.Span(" of long-term warming."),
    ], style={'font-size': '14px', 'line-height': '1.2', 'margin-top': '5px', 'margin-bottom': '20px'})

    low_ngfs_label = data.get('ndc35_low_ngfs_label', '').replace(" (with 1.7°C peak)", "")
    high_ngfs_label = data.get('ndc35_high_ngfs_label', '').replace(" (with 1.7°C peak)", "")

    ngfs_summary_condition = False
    if has_ndc35:
        n35_low_series = sc_sub.loc[sc_sub['year'] == 2035, 'ndc35pt_low']
        if 'cp_max' in sc_ranges.columns:
            cp_max_series = sc_ranges.loc[sc_ranges['year'] == 2035, 'cp_max']
            if not n35_low_series.empty and not cp_max_series.empty and pd.notna(n35_low_series.iloc[0]) and pd.notna(cp_max_series.iloc[0]):
                if n35_low_series.iloc[0] > cp_max_series.iloc[0]:
                    ngfs_summary_condition = True

    if ngfs_summary_condition:
        ngfs_summary = html.Div([
            html.Span("The party's 2035 target exceeds the range of NGFS scenarios for "),
            html.Span(low_ngfs_label, style=ngfs_style_map.get(low_ngfs_label, {})),
            html.Span(" of long-term warming."),
        ], style={'font-size': '14px', 'line-height': '1.2', 'margin-top': '5px', 'margin-bottom': '20px'})
    elif low_ngfs_label == high_ngfs_label:
        ngfs_summary = html.Div([
            html.Span("The party's 2035 target is in the range of NGFS scenarios for "),
            html.Span(low_ngfs_label, style=ngfs_style_map.get(low_ngfs_label, {})),
            html.Span(" of long-term warming."),
        ], style={'font-size': '14px', 'line-height': '1.2', 'margin-top': '5px', 'margin-bottom': '20px'})
    else:
        ngfs_summary = html.Div([
            html.Span("The party's 2035 target is in the range of "),
            html.A("NGFS", href="https://www.ngfs.net/ngfs-scenarios-portal/", target="_blank"),
            html.Span(" scenarios for "),
            html.Span(low_ngfs_label, style=ngfs_style_map.get(low_ngfs_label, {})),
            html.Span(" to "),
            html.Span(high_ngfs_label, style=ngfs_style_map.get(high_ngfs_label, {})),
            html.Span(" of long-term warming."),
        ], style={'font-size': '14px', 'line-height': '1.2', 'margin-top': '5px', 'margin-bottom': '20px'})

    return html.Div([
        html.Div("Scenarios for limiting warming", className="section-header"),
        html.Div(
            "How does the party's 2035 target compare to global cost-minimizing scenarios for different levels of warming by century's end?",
            className="graph-notes",
            style={'padding-bottom': '15px'}
        ),
        html.Div([
            html.Div(html.B("IPCC Climate Scenarios"), style={'font-family': 'Libre Franklin', 'font-size': '16px', 'color': 'black'}),
            ipcc_summary,
            dbc.Row([
                dbc.Col([
                    html.Div(html.B(f"Projected annual emissions, 2025-60"), style={'font-size': '12px'}),
                    dcc.Markdown(f"5th-95th percentile ({y_unit} CO<sub>2</sub>e)", dangerously_allow_html=True, style={'font-size': '12px', 'color': '#7f7f7f'}),
                    dcc.Graph(figure=fig_ipcc, config={'displayModeBar': False, 'responsive': True}, style={'height': '450px', 'maxWidth': '550px'})
                ], lg=6, md=12),
                dbc.Col([
                    html.Div(html.B(f"Range of modeled emissions in 2035 by warming category"), style={'font-size': '12px'}),
                    dcc.Markdown(f"5th-95th percentile ({y_unit} CO<sub>2</sub>e)", dangerously_allow_html=True, style={'font-size': '12px', 'color': '#7f7f7f'}),
                    dcc.Graph(figure=fig_jitter, config={'displayModeBar': False, 'scrollZoom': False, 'showTips': True}, style={'height': '450px', 'maxWidth': '550px'})
                ], lg=6, md=12)
            ]),
        ], className="chart-with-table", style={'background-color': 'white', 'paddingLeft': '10px', 'paddingTop': '10px'}),
        dbc.Button("Download chart data", id="download-ipcc-chart-csv-data", color="primary", className="mb-3", size="sm", style={'fontSize': '0.85rem', 'backgroundColor': '#7bccc4', 'border': 'none'}),
        html.Div([
            html.B("Data source: "),
            html.Span("Past emissions from official national inventory data reported to UN and "),
            html.A("PRIMAP-hist", href="https://zenodo.org/records/17090760", target="_blank"),
            html.Span(" estimates. IPCC scenario data from the "),
            html.A("AR6 Scenario Explorer", href="https://data.ene.iiasa.ac.at/ar6/#/login?redirect=%2Fworkspaces", target="_blank"),
            html.Span(" hosted by IIASA.")
        ], className="graph-notes", style={'max-width': '600px'}),
        html.Div([
            html.Div(html.B("NGFS Climate Scenarios"), style={'font-family': 'Libre Franklin', 'font-size': '16px', 'color': 'black'}),
            ngfs_summary,
            dbc.Row([
                dbc.Col([
                    html.Div(html.B(f"Projected annual emissions, 2025-50"), style={'font-size': '12px'}),
                    dcc.Markdown(f"Min-max spread of modeled emissions ({y_unit} CO<sub>2</sub>e)", dangerously_allow_html=True, style={'font-size': '12px', 'color': '#7f7f7f'}),
                    dcc.Graph(figure=fig_ngfs, config={'displayModeBar': False, 'responsive': True}, style={'height': '450px', 'maxWidth': '550px'})
                ], lg=6, md=12),
                dbc.Col([
                    html.Div(html.B(f"Range of modeled emissions in 2035 by warming category"), style={'font-size': '12px'}),
                    dcc.Markdown(f"Min-max spread of modeled emissions ({y_unit} CO<sub>2</sub>e)", dangerously_allow_html=True, style={'font-size': '12px', 'color': '#7f7f7f'}),
                    dcc.Graph(figure=fig_ngfs_jitter, config={'displayModeBar': False, 'scrollZoom': False, 'showTips': True}, style={'height': '450px', 'maxWidth': '550px'})
                ], lg=6, md=12)
            ])
        ], className="chart-with-table", style={'background-color': 'white', 'margin-top': '20px', 'paddingLeft': '10px', 'paddingTop': '10px'}),
        dbc.Button("Download chart data", id="download-ngfs-chart-csv-data", color="primary", className="mb-3", size="sm", style={'fontSize': '0.85rem', 'backgroundColor': '#7bccc4', 'border': 'none'}),
        html.Div([
            html.B("Data source: "),
            html.Span("Past emissions from official national inventory data reported to UN and "),
            html.A("PRIMAP-hist", href="https://zenodo.org/records/17090760", target="_blank"),
            html.Span(" estimates. NGFS scenario data from the "),
            html.A("NGFS Scenario Explorer", href="https://data.ene.iiasa.ac.at/ngfs/#/login", target="_blank"),
            html.Span(" hosted by IIASA.")
        ], className="graph-notes", style={'max-width': '600px', 'margin-top': '10px'}),
        html.Div([
            html.B("Notes: "),
            "'1.4°C' in the chart above corresponds with the NGFS 'Net Zero World' scenario in which temperatures return to 1.4°C at century's end after reaching 1.7°C. ' 1.8°C' corresponds with the NGFS 'Below 2°C' scenario. '2.4°' corresponds with the NGFS 'Fragmented World' scenario. '3°C' corresponds with the NGFS 'Current Policies' scenario"
        ], className="graph-notes", style={'max-width': '600px', 'margin-top': '10px'})
    ])