import pandas as pd
import matplotlib.pyplot as plt
import re

def get_pool_string(file):
    # Use regular expression to extract "SALK034"
    pool_string = re.search(r'SALK\d+', file).group()
    return pool_string

def find_transition_row(file_path):
    """
    Finds the row number of the transition string "[Top Unknown Barcodes]"
    and the last non-empty row above it.
    """
    with open(file_path, 'r') as file:
        for i, line in enumerate(file):
            if "[Top Unknown Barcodes]" in line:
                return i  # Returns the row number of the header
    return None

def read_dataframes(file_path):
    """
    Reads two tables from a CSV file into pandas dataframes,
    dynamically determining the transition based on a specific string.
    """
    transition_row = find_transition_row(file_path)
    if transition_row is None:
        raise ValueError("Transition string '[Top Unknown Barcodes]' not found in the file.")

    # Adjust for 0-based indexing in pandas and to skip the header of the second table
    second_table_start = transition_row + 1  # To start reading from the data right after the header

    # Read the first table, ignoring empty lines just above the transition string
    demux_stats = pd.read_csv(file_path, nrows=transition_row - 1)  # Read up to the row before the transition row

    # Read the second table, skipping rows up to and including the transition row
    top_unknown_barcodes = pd.read_csv(file_path, skiprows=second_table_start)

    return demux_stats, top_unknown_barcodes

def calculate_metrics(demux_stats, top_unknown_barcodes):
    run_yield = demux_stats["# of >= Q30 Bases (PF)"].sum()
    run_yield_excluding_undetermined = demux_stats[~demux_stats["SampleID"].fillna('').str.contains("Undetermined")]["# of >= Q30 Bases (PF)"].sum()
    total_reads = demux_stats["# Reads"].sum()
    phiX_condition1 = (top_unknown_barcodes["index"] == "TGCCGTGGAT") & (top_unknown_barcodes["index2"] == "GATATAGAGT")
    phiX_condition2 = (top_unknown_barcodes["index"] == "GATATAGAGT") & (top_unknown_barcodes["index2"] == "GATATAGAGT")
    assumed_phiX_reads = top_unknown_barcodes[phiX_condition1 | phiX_condition2]["# Reads"].sum()
    percent_phix_assumed = assumed_phiX_reads / total_reads if total_reads != 0 else 0

    return {
        "run_yield": run_yield,
        "run_yield_excluding_undetermined": run_yield_excluding_undetermined,
        "total_reads": total_reads,
        "assumed_phiX_reads": assumed_phiX_reads,
        "percent_phix_assumed": percent_phix_assumed
    }

def format_metrics(metrics):
    formatted_metrics = {}
    for key in ['run_yield', 'run_yield_excluding_undetermined']:
        formatted_metrics[key] = "{:,} >= Q30 Bases".format(metrics[key])
    for key in ['total_reads', 'assumed_phiX_reads']:
        formatted_metrics[key] = "{:,} Reads PF".format(metrics[key])
    formatted_metrics['percent_phix_assumed'] = "{:.2%}".format(metrics['percent_phix_assumed'])
    return formatted_metrics

def plot_reads_vs_sampleID_reversed(demux_stats, pool_string):
    pivot_table = demux_stats.pivot_table(index='SampleID', columns='Lane', values='# Reads', fill_value=0)
    pivot_table.plot(kind='barh', figsize=(10, 6))  
    plt.title('Reads PF for Each Plate in Each Lane')
    plt.ylabel('SampleID')
    plt.xlabel('# Reads')
    plt.legend(title='Lane')
    plt.tight_layout()
    plt.savefig(f"{pool_string}_reads_pf_broad.png")
    plt.show()

# Main execution block
if __name__ == "__main__":
    file_path = '/path/to/your/file.csv'
    demux_stats, top_unknown_barcodes = read_dataframes(file_path)
    pool_string = get_pool_string(file_path)
    metrics = calculate_metrics(demux_stats, top_unknown_barcodes)
    formatted_metrics = format_metrics(metrics)

    for key, value in formatted_metrics.items():
        print(f"{key}: {value}")

    plot_reads_vs_sampleID_reversed(demux_stats, pool_string)
