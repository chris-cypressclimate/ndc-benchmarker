import plotly.graph_objects as go
import numpy as np
import math
import pandas as pd

def create_empty_figure(text="No Data Available"):
    fig = go.Figure()
    fig.add_annotation(text=text, showarrow=False, font=dict(size=20))
    fig.update_layout(xaxis={'visible': False}, yaxis={'visible': False})
    return fig

def _get_nice_y_ticks(all_vals, num_target_intervals=4, suffix=None, padding_multiplier=0):
    if all_vals.empty or not all_vals.notna().any():
        return {'rangemode': 'tozero'}

    min_data_val = all_vals.min()
    max_data_val = all_vals.max()

    # If all data is non-negative, start y-axis at 0
    if min_data_val >= 0:
        min_y_val = 0
        padded_max_y = max_data_val * (1 + padding_multiplier)
    else:
        # If there are negative values, give a buffer to both min and max
        min_y_val = min_data_val * (1 + padding_multiplier)
        padded_max_y = max_data_val * (1 + padding_multiplier)

    # Handle cases where max_data_val is 0 or very small positive
    if max_data_val == 0 and min_data_val >= 0:
        ticktext = ["", "25", "50", "75", "100"]
        if suffix:
            ticktext[-1] = f"{ticktext[-1]}{suffix}"
        return {
            'tickvals': [0, 25, 50, 75, 100],
            'ticktext': ticktext,
            'range': [0, 100]
        }
    
    if padded_max_y <= min_y_val:
        padded_max_y = min_y_val + 10

    # Determine a 'nice' tick step
    data_range = padded_max_y - min_y_val
    rough_step = data_range / num_target_intervals
    
    if rough_step <= 0: # Fallback for very small or zero range
        rough_step = 1

    nice_step_bases = [1, 2, 2.5, 5]
    power_of_10 = 10**math.floor(math.log10(rough_step))
    scaled_rough_step = rough_step / power_of_10

    tick_step_base = 1
    for base in nice_step_bases:
        if base >= scaled_rough_step:
            tick_step_base = base
            break
    else:
        tick_step_base = 1
        power_of_10 *= 10
    
    tick_step = tick_step_base * power_of_10

    # Calculate the final bounds for the axis, rounded to the nearest tick_step
    final_min_y = math.floor(min_y_val / tick_step) * tick_step
    final_max_y = math.ceil(padded_max_y / tick_step) * tick_step

    # Generate tick values
    y_tickvals = np.arange(final_min_y, final_max_y + tick_step, tick_step).tolist()
    y_tickvals = sorted(list(set([round(v) for v in y_tickvals])))

    # Format tick text, replacing 0 with "" if it's not the only tick
    if len(y_tickvals) > 1:
        y_ticktext = [f"{int(v):,.0f}" if v != 0 else "" for v in y_tickvals]
    else:
        y_ticktext = [f"{int(v):,.0f}" for v in y_tickvals]

    if suffix and y_ticktext:
        y_ticktext[-1] = f"{y_ticktext[-1]}{suffix}"

    config = {
        'tickvals': y_tickvals,
        'ticktext': y_ticktext,
        'range': [final_min_y, final_max_y],
        'gridcolor': '#e9e9e9'
    }

    if min_data_val < 0:
        config['zeroline'] = True
        config['zerolinecolor'] = '#696969'
        config['zerolinewidth'] = 1
    
    return config

def add_outlined_annotation(fig, x, y, text, yanchor, xanchor="left", xshift=0, yshift=0):
    # Add outline annotations
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        fig.add_annotation(x=x, y=y, text=text, showarrow=False,
                           xanchor=xanchor, yanchor=yanchor, xshift=xshift + dx, yshift=yshift + dy,
                           font=dict(color="white"))
    # Add main annotation
    fig.add_annotation(x=x, y=y, text=text, showarrow=False,
                       xanchor=xanchor, yanchor=yanchor, xshift=xshift, yshift=yshift,
                       font=dict(color="#7f7f7f"))