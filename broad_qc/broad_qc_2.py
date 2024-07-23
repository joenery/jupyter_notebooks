import pandas as pd
import matplotlib.pyplot as plt
import re

def get_pool_string(file):
    pool_string = re.search(r'SALK\d+', file).group()
    return pool_string

def read_dataframes(file_path):
    """
    Reads two tables from a CSV file into pandas dataframes.
    Adjusts for the structure observed in the CSV file.
    """
    demux_stats = pd.read_csv(file_path, nrows=128)  # Adjusted to read only relevant rows for the first table
    top_unknown_barcodes = pd.read_csv(file_path, skiprows=131)  # Starts reading from the actual data of the second table

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

# Example usage (you would replace '/path/to/your/file.csv' with your actual file path)
if __name__ == "__main__":
    file_path = '/path/to/your/file.csv'
    demux_stats, top_unknown_barcodes = read_dataframes(file_path)
    pool_string = get_pool_string(file_path)
    metrics = calculate_metrics(demux_stats, top_unknown_barcodes)
    formatted_metrics = format_metrics(metrics)
    for key, value in formatted_metrics.items():
        print(f"{key}: {value}")
    plot_reads_vs_sampleID_reversed(demux_stats, pool_string)
