import pandas as pd
import pathlib

# Define paths to data
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()


def load_data():
    """Loads all CSV/Excel files into pandas DataFrames."""
    data = {}

    # 1. Base Metadata
    data['base'] = pd.read_csv(DATA_PATH.joinpath("ndc_tool_data_base.csv"))

    # 2. Charts Data
    data['target_ts'] = pd.read_csv(DATA_PATH.joinpath("ndc_tool_target_time_series_chart_base.csv"))
    data['straight_line'] = pd.read_csv(DATA_PATH.joinpath("ndc_tool_straight_line_trajectories_chart_data.csv"))
    data['scenario'] = pd.read_csv(DATA_PATH.joinpath("ndc_tool_scenario_modeling_time_series.csv"))
    data['ipcc_scenarios'] = pd.read_csv(DATA_PATH.joinpath("ipcc_scenarios_emissions_by_category_2035.csv"))
    data['ngfs_scatter'] = pd.read_csv(DATA_PATH.joinpath("ngfs_scatter_plot.csv"))

    # 3. Public Upload File (Try CSV first, fallback to Excel)
    try:
        data['public'] = pd.read_csv(DATA_PATH.joinpath("ndc_tool_public_file_for_upload.csv"))
    except FileNotFoundError:
        data['public'] = pd.read_excel(DATA_PATH.joinpath("ndc_tool_public_file_for_upload.xlsx"))

    return data


# Load data globally so it's accessible to other files
dfs = load_data()

# Calculate Banner Counters
# Logic: [A] = sum("new") + 26
count_new_ndcs = dfs['base']['new'].sum() + 26
# Logic: [B] = 197 - [A]
count_no_new_ndcs = 197 - count_new_ndcs