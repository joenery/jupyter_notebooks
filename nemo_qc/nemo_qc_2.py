import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Function to load data from a CSV file
def load_data(file_path):
    return pd.read_csv(file_path)

# Function to calculate undetermined reads percentage
def calculate_undetermined_reads_percentage(data):
    undetermined_data = data[data['SampleID'].str.contains("Undetermined", case=False, na=False)]
    undetermined_reads_per_lane = undetermined_data.groupby('Lane')['# Reads'].sum()
    total_reads_per_lane = data.groupby('Lane')['# Reads'].sum()
    return (undetermined_reads_per_lane / total_reads_per_lane) * 100

# Function to calculate yield in gigabases
def calculate_yield_gb(data):
    yield_per_lane = data.groupby('Lane')['# of >= Q30 Bases (PF)'].sum()
    return yield_per_lane / 1e9

# Function to plot a combined chart for all lanes
def plot_combined_lane_chart(data, undetermined_percentage, yield_gb, top_two_barcode_percentage):
    sns.set(style="whitegrid")
    # Prefixing SampleID with Lane number
    data['Prefixed SampleID'] = data['Lane'].astype(str) + '_' + data['SampleID']

    # Adjusting the data for plotting
    data.loc[:, '# Reads'] = data['# Reads'] / 1e6  # Convert reads to millions

    # Plotting
    plt.figure(figsize=(20, 10))
    chart = sns.barplot(x='Prefixed SampleID', y='# Reads', hue='Lane', data=data, dodge=False)
    plt.xticks(rotation=90)
    plt.title('Number of Reads per Sample Across All Lanes (in Millions)')
    plt.xlabel('Sample ID')
    plt.ylabel('Number of Reads (Millions)')

    # Annotations
    total_yield_tb = yield_gb.sum() / 1000  # Convert total yield to terabases
    plt.text(0.5, 0.97, f'Total Yield: {total_yield_tb:.3f} Tb', ha='center', va='center', transform=chart.transAxes, fontsize=12, color='green')

    plt.tight_layout()
    plt.show()

# Example usage
file_path = 'your_file_path_here.csv'
data = load_data(file_path)
undetermined_percentage = calculate_undetermined_reads_percentage(data)
yield_gb = calculate_yield_gb(data)
# Assume top_two_barcode_percentage is already calculated
plot_combined_lane_chart(data, undetermined_percentage, yield_gb, top_two_barcode_percentage)

