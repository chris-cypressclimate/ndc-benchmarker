from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from .chart_utils import _get_nice_y_ticks, add_outlined_annotation
import dash_bootstrap_components as dbc

def get_emissions_pathways_chart(data, ts_df, iso3):
    has_ndc40 = pd.notna(data.get('ndc40pt_low')) and pd.notna(data.get('ndc40pt_high'))
    end_year = 2040 if has_ndc40 else 2035
    chart1_df = ts_df[(ts_df['year'] >= 1990) & (ts_df['year'] <= end_year)].copy()

    scale_mult = 1.0
    y_unit = "million tons"
    tooltip_suffix = " Mt CO<sub>2</sub>e"
    y_axis_suffix = ""
    if not chart1_df.empty:
        min_past_ghg_net = chart1_df['past_ghg_net'].min() if 'past_ghg_net' in chart1_df.columns and chart1_df['past_ghg_net'].notna().any() else 0
        
        if -100 <= min_past_ghg_net < -1:
            data['scale'] = 2
        elif min_past_ghg_net < -100:
            data['scale'] = 3
        else:
            ndc35pt_low = chart1_df['ndc35pt_low'].iloc[0] if 'ndc35pt_low' in chart1_df.columns and not chart1_df['ndc35pt_low'].empty else 0
            if ndc35pt_low <= 1 or min_past_ghg_net <= 1:
                data['scale'] = 1

        if data.get('scale') > 1:
            y_unit = "million tons CO<sub>2</sub>e"
            tooltip_suffix = " Mt CO<sub>2</sub>e"
        elif data.get('scale') == 1:
            scale_mult = 1000
            y_unit = "kilotons CO<sub>2</sub>e"
            tooltip_suffix = " kt CO<sub>2</sub>e"
            y_axis_suffix = ""

    fig1 = go.Figure()

    if not chart1_df.empty:
        # Apply scaling
        for col in ['ndc_low', 'ndc_high', 'past_ghg_net', 'past_ghg_gross', 'ndc35pt_low', 'ndc35pt_high', 'ndc30pt_low', 'ndc30pt_high', 'ndc35pt_base', 'ndc40pt_low', 'ndc40pt_high']:
            if col in chart1_df.columns:
                chart1_df[col] *= scale_mult

        last_past_year = chart1_df[chart1_df['past_ghg_net'].notna() | chart1_df['past_ghg_gross'].notna()]['year'].max()

        chart1_df['hover_text'] = chart1_df['past_ghg_net_source'].apply(
            lambda x: '<i>National inventory data</i>' if x == 'unfccc' 
            else ('<i>Interpolated estimate</i>' if x == 'interpolated' 
                  else ('<i>Extrapolated estimate</i>' if x == 'extrapolated' else '')))

        # Conditional logic for displaying GHG series
        ndc35_ng = data.get('ndc35_ng')
        ndc35_base_ng = data.get('ndc35_base_ng')

        show_net_solid = False
        show_gross_solid = False
        show_gross_dotted = False

        if ndc35_ng != "gross" and ndc35_base_ng == "gross":
            show_net_solid = True
            show_gross_dotted = True
        elif ndc35_ng == "gross" and ndc35_base_ng != "gross":
            show_net_solid = True
            show_gross_dotted = True
        elif ndc35_ng == "gross":
            show_gross_solid = True
        else: # ndc35_ng != "gross"
            show_net_solid = True

        if show_net_solid:
            past_ghg_net_series = chart1_df[['year', 'past_ghg_net']].dropna()
            if len(past_ghg_net_series) > 1 and (past_ghg_net_series['year'].diff().max() <= 10):
                fig1.add_trace(go.Scatter(
                    x=chart1_df['year'], 
                    y=chart1_df['past_ghg_net'],
                    mode='lines', 
                    line=dict(color='black', width=2.5), 
                    name='Including LULUCF',
                    customdata=chart1_df['hover_text'],
                    hovertemplate='<b>%{x}</b><br>%{customdata}<br>Total emissions (incl LULUCF): %{y:,.0f}' + tooltip_suffix + '<extra></extra>'
                ))
            else:
                fig1.add_trace(go.Scatter(
                    x=past_ghg_net_series['year'], 
                    y=past_ghg_net_series['past_ghg_net'],
                    mode='markers', 
                    marker=dict(color='black', size=6),
                    name='Including LULUCF',
                    customdata=past_ghg_net_series.index.map(chart1_df['hover_text']),
                    hovertemplate='<b>%{x}</b><br>%{customdata}<br>Total emissions (incl LULUCF): %{y:,.0f}' + tooltip_suffix + '<extra></extra>'
                ))

        if show_gross_solid:
            past_ghg_gross_series = chart1_df[['year', 'past_ghg_gross']].dropna()
            if len(past_ghg_gross_series) > 1 and (past_ghg_gross_series['year'].diff().max() <= 10):
                fig1.add_trace(go.Scatter(
                    x=chart1_df['year'], 
                    y=chart1_df['past_ghg_gross'],
                    mode='lines', 
                    line=dict(color='black', width=2.5), 
                    name='Excluding LULUCF',
                    customdata=chart1_df['hover_text'],
                    hovertemplate='<b>%{x}</b><br>%{customdata}<br>Total emissions (excl LULUCF): %{y:,.0f}' + tooltip_suffix + '<extra></extra>'
                ))
            else:
                fig1.add_trace(go.Scatter(
                    x=past_ghg_gross_series['year'], 
                    y=past_ghg_gross_series['past_ghg_gross'],
                    mode='markers', 
                    marker=dict(color='black', size=6),
                    name='Excluding LULUCF',
                    customdata=past_ghg_gross_series.index.map(chart1_df['hover_text']),
                    hovertemplate='<b>%{x}</b><br>%{customdata}<br>Total emissions (excl LULUCF): %{y:,.0f}' + tooltip_suffix + '<extra></extra>'
                ))

        if show_gross_dotted:
            past_ghg_gross_series = chart1_df[['year', 'past_ghg_gross']].dropna()
            if len(past_ghg_gross_series) > 1 and (past_ghg_gross_series['year'].diff().max() <= 10):
                fig1.add_trace(go.Scatter(
                    x=chart1_df['year'], 
                    y=chart1_df['past_ghg_gross'],
                    mode='lines', 
                    line=dict(color='black', width=2.5, dash='dot'), 
                    name='Excluding LULUCF',
                    customdata=chart1_df['hover_text'],
                    hovertemplate='<b>%{x}</b><br>%{customdata}<br>Total emissions (excl LULUCF): %{y:,.0f}' + tooltip_suffix + '<extra></extra>'
                ))
            else:
                fig1.add_trace(go.Scatter(
                    x=past_ghg_gross_series['year'], 
                    y=past_ghg_gross_series['past_ghg_gross'],
                    mode='markers', 
                    marker=dict(color='black', size=6, symbol='circle-open'),
                    name='Excluding LULUCF',
                    customdata=past_ghg_gross_series.index.map(chart1_df['hover_text']),
                    hovertemplate='<b>%{x}</b><br>%{customdata}<br>Total emissions (excl LULUCF): %{y:,.0f}' + tooltip_suffix + '<extra></extra>'
                ))
        
        # --- Base Year ---
        base_pt = chart1_df[chart1_df['ndc35pt_base'].notna()]
        if not base_pt.empty:
            base_year = base_pt['year'].values[0]
            base_val = base_pt['ndc35pt_base'].values[0]
            
            fig1.add_trace(go.Scatter(
                x=[base_year], 
                y=[base_val],
                mode='markers', 
                marker=dict(color='white', size=6, line=dict(color='black', width=1.5)), 
                name='NDC base year',
                hovertemplate='<b>%{x}</b><br>NDC base: %{y:,.0f}' + tooltip_suffix + '<extra></extra>',
                showlegend=False
            ))
            add_outlined_annotation(fig1, base_year, base_val, "<b>NDC<br>base<br>year</b>", "top", yshift=-5)

        # Range area with outline
        outline_color = 'rgba(112, 128, 144, 0.5)'
        fill_color = 'rgba(112, 128, 144, 0.3)'
        range_df = chart1_df[chart1_df['year'] >= last_past_year]
        fig1.add_trace(go.Scatter(
            x=range_df['year'], y=range_df['ndc_low'],
            mode='lines', line=dict(width=1, color=outline_color), showlegend=False, hoverinfo='skip'
        ))
        fig1.add_trace(go.Scatter(
            x=range_df['year'], y=range_df['ndc_high'],
            fill='tonexty', mode='lines', line=dict(width=1, color=outline_color),
            fillcolor=fill_color, showlegend=False, hoverinfo='skip'
        ))
        
        yaxis_dict_fig1 = dict(side='left', tickformat=",.0f", tickprefix="", ticksuffix="", showgrid=True)
        all_vals_fig1 = pd.Series(dtype='float64')
        cols_to_check_fig1 = ['ndc_low', 'ndc_high', 'past_ghg_net', 'past_ghg_gross', 'ndc35pt_low', 'ndc35pt_high', 'ndc30pt_low', 'ndc30pt_high', 'ndc35pt_base', 'ndc40pt_low', 'ndc40pt_high']
        for col in cols_to_check_fig1:
            if col in chart1_df.columns and chart1_df[col].notna().any():
                all_vals_fig1 = pd.concat([all_vals_fig1, chart1_df[col]])
        
        y_axis_config_fig1 = _get_nice_y_ticks(all_vals_fig1, suffix=y_axis_suffix)
        yaxis_dict_fig1.update(y_axis_config_fig1)

        val_35_low_series = chart1_df.loc[chart1_df['year'] == 2035, 'ndc35pt_low']
        val_35_high_series = chart1_df.loc[chart1_df['year'] == 2035, 'ndc35pt_high']
        val_30_low_series = chart1_df.loc[chart1_df['year'] == 2030, 'ndc30pt_low']
        val_30_high_series = chart1_df.loc[chart1_df['year'] == 2030, 'ndc30pt_high']
        val_40_low_series = chart1_df.loc[chart1_df['year'] == 2040, 'ndc40pt_low'] if has_ndc40 else pd.Series()
        val_40_high_series = chart1_df.loc[chart1_df['year'] == 2040, 'ndc40pt_high'] if has_ndc40 else pd.Series()

        y_range = y_axis_config_fig1['range']
        y_max = y_range[1]
        y_min = y_range[0]
        
        ndc30_high_val = val_30_high_series.values[0] if not val_30_high_series.empty else None
        ndc35_high_val = val_35_high_series.values[0] if not val_35_high_series.empty else None
        ndc40_high_val = val_40_high_series.values[0] if not val_40_high_series.empty else None
        ndc30_low_val = val_30_low_series.values[0] if not val_30_low_series.empty else None
        ndc35_low_val = val_35_low_series.values[0] if not val_35_low_series.empty else None
        ndc40_low_val = val_40_low_series.values[0] if not val_40_low_series.empty else None

        move_annotations_down = False
        if (ndc30_high_val is not None and ndc30_high_val > y_max * 0.7) or \
           (ndc35_high_val is not None and ndc35_high_val > y_max * 0.7) or \
           (ndc40_high_val is not None and ndc40_high_val > y_max * 0.7):
            move_annotations_down = True

        move_annotations_up = False
        if (ndc30_low_val is not None and ndc30_low_val < y_min + (y_max - y_min) * 0.25) or \
           (ndc35_low_val is not None and ndc35_low_val < y_min + (y_max - y_min) * 0.25) or \
           (ndc40_low_val is not None and ndc40_low_val < y_min + (y_max - y_min) * 0.25):
            move_annotations_up = True

        if pd.notna(last_past_year):
            fig1.add_shape(type="rect", xref="x", yref="paper", x0=last_past_year, y0=0, x1=end_year, y1=1, fillcolor="#f5f5f0", layer="below", line_width=0)
            if move_annotations_down:
                fig1.add_annotation(x=last_past_year, y=0, yref="paper", text="<b>Path to<br>NDC targets</b>", showarrow=False, xanchor="left", yanchor="bottom", xshift=0, yshift=5, font=dict(color="#7f7f7f", size=13), align="left")
            else:
                fig1.add_annotation(x=last_past_year, y=1, yref="paper", text="<b>Path to<br>NDC targets</b>", showarrow=False, xanchor="left", yanchor="top", xshift=0, yshift=-5, font=dict(color="#7f7f7f", size=13), align="left")

        # Tooltips for target ranges
        for year, title in [(2035, "2035 target"), (2030, "2030 target"), (2040, "2040 target")]:
            df_year = chart1_df[chart1_df['year'] == year]
            if not df_year.empty:
                low_col, high_col = f'ndc{str(year)[-2:]}pt_low', f'ndc{str(year)[-2:]}pt_high'
                if low_col in df_year and high_col in df_year:
                    low_val, high_val = df_year[low_col].values[0], df_year[high_col].values[0]
                    
                    marker_style = dict(color='white', size=6, line=dict(color='black', width=1.5))

                    if pd.notna(low_val) and pd.notna(high_val) and low_val == high_val:
                        fig1.add_trace(go.Scatter(
                            x=[year], y=[high_val], mode='markers', marker=marker_style,
                            showlegend=False, name=title,
                            hovertemplate=f'<b>{title}</b><br>%{{y:,.0f}}' + tooltip_suffix + '<extra></extra>'
                        ))
                    else:
                        if pd.notna(high_val):
                            fig1.add_trace(go.Scatter(
                                x=[year], y=[high_val], mode='markers', marker=marker_style,
                                showlegend=False, name='Upper',
                                hovertemplate=f'<b>{title}</b><br>Upper: %{{y:,.0f}}' + tooltip_suffix + '<extra></extra>'
                            ))
                        if pd.notna(low_val):
                            fig1.add_trace(go.Scatter(
                                x=[year], y=[low_val], mode='markers', marker=marker_style,
                                showlegend=False, name='Lower',
                                hovertemplate=f'<b>{title}</b><br>Lower: %{{y:,.0f}}' + tooltip_suffix + '<extra></extra>'
                            ))
        
        # Annotations for NDC targets
        if not val_35_high_series.empty and pd.notna(val_35_high_series.values[0]):
            y_pos_35 = val_35_high_series.values[0]
            y_anchor_35 = "bottom"
            if move_annotations_down:
                y_pos_35 = val_35_low_series.values[0] if not val_35_low_series.empty and pd.notna(val_35_low_series.values[0]) else y_pos_35
                y_anchor_35 = "top"
            add_outlined_annotation(fig1, 2035, y_pos_35, "<b>2035<br>NDC</b>", y_anchor_35, xshift=5)

        if not val_30_high_series.empty and pd.notna(val_30_high_series.values[0]):
            y_pos_30 = val_30_high_series.values[0]
            y_anchor_30 = "bottom"
            y_shift_30 = 5
            if move_annotations_down:
                y_pos_30 = val_30_low_series.values[0] if not val_30_low_series.empty and pd.notna(val_30_low_series.values[0]) else y_pos_30
                y_anchor_30 = "top"
                y_shift_30 = -5
            add_outlined_annotation(fig1, 2030, y_pos_30, "<b>2030<br>NDC</b>", y_anchor_30, yshift=y_shift_30)

        if has_ndc40 and not val_40_high_series.empty and pd.notna(val_40_high_series.values[0]):
            y_pos_40 = val_40_high_series.values[0]
            y_anchor_40 = "bottom"
            if move_annotations_down:
                y_pos_40 = val_40_low_series.values[0] if not val_40_low_series.empty and pd.notna(val_40_low_series.values[0]) else y_pos_40
                y_anchor_40 = "top"
            add_outlined_annotation(fig1, 2040, y_pos_40, "<b>2040<br>NDC</b>", y_anchor_40, xshift=5)


    if not chart1_df.empty and 'year' in chart1_df.columns:
        min_year = chart1_df['year'].min()
        min_year_rounded = int(min_year / 5) * 5
        tickvals = list(range(min_year_rounded, 2031, 10))
        if 2035 not in tickvals:
            tickvals.append(2035)
        if has_ndc40 and 2040 not in tickvals:
            tickvals.append(2040)
        ticktext = [f"{y}" for y in tickvals]
    else:
        tickvals = [1990, 2000, 2010, 2020, 2030, 2035]
        if has_ndc40:
            tickvals.append(2040)
        ticktext = [f"{y}" for y in tickvals]

    fig1.update_layout(
        template='plotly_white',
        margin=dict(l=20, r=15, t=80, b=40),
        xaxis=dict(tickvals=tickvals, ticktext=ticktext, showgrid=False, showline=True, linecolor='lightgrey', linewidth=1, ticks='outside', tickson='boundaries', tickangle=-90, fixedrange=True),
        yaxis=dict(yaxis_dict_fig1, fixedrange=True),
        showlegend=False,
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.95)",
            bordercolor="black",
            font=dict(
                color="#333333"
            )
        ),
        title=dict(text=f"<b>Past Emissions and NDC Targets</b><br><span style='font-size: 14px; color: #7f7f7f'>Total emissions ({y_unit})</span>", x=0.01, y=0.95, xanchor='left', yanchor="top", font=dict(family="Libre Franklin", size=16, color="black")),
        font=dict(family="Libre Franklin", size=14, color="#7f7f7f"),
    )

    notes_text = ""
    if pd.notna(data.get('ndc_graph_notes')):
        notes_text += data.get('ndc_graph_notes')

    if 'past_ghg_net_source' in chart1_df.columns and chart1_df['past_ghg_net_source'].isin(['interpolated', 'extrapolated']).any():
        if notes_text:
            notes_text += " "
        notes_text += "Gaps in official national inventory data shown in the chart are interpolated and extrapolated for additional years based on year-on-year trends in [PRIMAP-hist](https://zenodo.org/records/17090760) estimated emissions."

    ndc_graph_notes_div = dcc.Markdown(f"**Notes:** {notes_text}", className="graph-notes")

    return html.Div([
        dcc.Graph(figure=fig1, id='emissions-pathways-chart', config={'displayModeBar': False, 'responsive': True}, style={'height': '450px', 'width': '100%', 'maxWidth': '550px'}),
        dbc.Button("Download chart data", id="download-chart-csv-data", color="primary", className="mb-3", size="sm", style={'fontSize': '0.85rem', 'backgroundColor': '#7bccc4', 'border': 'none'}),
        html.Div([
            dcc.Markdown(f"**Data source:** Past emissions from official national inventory data reported to UN and [PRIMAP-hist](https://zenodo.org/records/17090760) estimates.", className="graph-notes"),
            ndc_graph_notes_div,
        ], style={'width': '80%'})
    ])