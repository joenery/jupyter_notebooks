import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(file_path):
    """
    Load the data from a CSV file.

    Args:
    file_path (str): The file path to the CSV file.

    Returns:
    pandas.DataFrame: The loaded data.
    """
    return pd.read_csv(file_path)

def calculate_undetermined_reads_percentage(data):
    """
    Calculate the percentage of undetermined reads per lane.

    Args:
    data (pandas.DataFrame): The sequencing data.

    Returns:
    pandas.Series: The percentage of undetermined reads per lane.
    """
    undetermined_data = data[data['SampleID'].str.contains("Undetermined", case=False, na=False)]
    undetermined_reads_per_lane = undetermined_data.groupby('Lane')['# Reads'].sum()
    total_reads_per_lane = data.groupby('Lane')['# Reads'].sum()
    return (undetermined_reads_per_lane / total_reads_per_lane) * 100

def calculate_yield_gb(data):
    """
    Calculate the yield in gigabases per lane.

    Args:
    data (pandas.DataFrame): The sequencing data.

    Returns:
    pandas.Series: The yield in gigabases per lane.
    """
    yield_per_lane = data.groupby('Lane')['# of >= Q30 Bases (PF)'].sum()
    return yield_per_lane / 1e9

def plot_lane_charts(data, undetermined_percentage, yield_gb):
    """
    Plot the bar charts for each lane with annotations.

    Args:
    data (pandas.DataFrame): The sequencing data.
    undetermined_percentage (pandas.Series): The percentage of undetermined reads per lane.
    yield_gb (pandas.Series): The yield in gigabases per lane.
    """
    sns.set(style="whitegrid")
    lanes = data['Lane'].unique()
    total_yield_tb = yield_gb.sum() / 1000  # Convert total yield to terabases
    for lane in lanes:
        lane_data = data[data['Lane'] == lane].copy()
        lane_data.loc[:, '# Reads'] = lane_data['# Reads'] / 1e6
        plt.figure(figsize=(10, 6))
        chart = sns.barplot(x='SampleID', y='# Reads', data=lane_data)
        plt.xticks(rotation=90)
        plt.title(f'Lane {lane} - Number of Reads per Sample (in Millions)')
        plt.xlabel('Sample ID')
        plt.ylabel('Number of Reads (Millions)')

        undetermined_percentage_lane = undetermined_percentage[lane]
        yield_value_gb_lane = yield_gb[lane]

        # Increasing vertical spacing between annotations
        plt.text(0.5, 0.97, f'Total Yield: {total_yield_tb:.3f} Tb', ha='center', va='center', transform=chart.transAxes, fontsize=12, color='green')
        plt.text(0.5, 0.91, f'Yield (Lane {lane}): {yield_value_gb_lane:.2f} Gb', ha='center', va='center', transform=chart.transAxes, fontsize=12, color='blue')
        plt.text(0.5, 0.85, f'% Undetermined Reads: {undetermined_percentage_lane:.2f}%', ha='center', va='center', transform=chart.transAxes, fontsize=12, color='red')

        plt.tight_layout()
        plt.show()

def generate_nemo_qc_plots(file_path):
    """
    Wrapper function to generate plots for sequencing data.

    Args:
    file_path (str): The file path to the CSV file.
    """
    # Load the data
    data = load_data(file_path)

    # Calculate the metrics
    undetermined_percentage = calculate_undetermined_reads_percentage(data)
    yield_gb = calculate_yield_gb(data)

    # Generate and display the plots
    plot_lane_charts(data, undetermined_percentage, yield_gb)

