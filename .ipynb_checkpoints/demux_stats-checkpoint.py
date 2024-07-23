import pandas as pd

def read_dataframes(file_path):
    """
    Reads two tables from a CSV file into pandas dataframes.

    Parameters:
    file_path (str): The path to the CSV file.

    Returns:
    tuple: A tuple containing two pandas dataframes.
    """
    # Read the first table into a dataframe named demux_stats
    demux_stats = pd.read_csv(file_path, nrows=136, skiprows=0)

    # Read the second table into a dataframe named top_unknown_barcodes
    top_unknown_barcodes = pd.read_csv(file_path, skiprows=139)

    return demux_stats, top_unknown_barcodes

def calculate_metrics(demux_stats, top_unknown_barcodes):
    """
    Calculates various metrics from the provided dataframes.

    Parameters:
    demux_stats (pd.DataFrame): The dataframe containing demultiplexing statistics.
    top_unknown_barcodes (pd.DataFrame): The dataframe containing information about top unknown barcodes.

    Returns:
    dict: A dictionary containing calculated metrics.
    """
    # Sum of "# of >= Q30 Bases (PF)"
    run_yield = demux_stats["# of >= Q30 Bases (PF)"].sum()

    # Sum of "# of >= Q30 Bases (PF)" excluding rows with "Undetermined" in "SampleID"
    run_yield_excluding_undetermined = demux_stats[~demux_stats["SampleID"].str.contains("Undetermined")]["# of >= Q30 Bases (PF)"].sum()

    # Sum of "# Reads"
    total_reads = demux_stats["# Reads"].sum()

    # Calculating assumed PhiX reads
    phiX_condition1 = (top_unknown_barcodes["index"] == "TGCCGTGGAT") & (top_unknown_barcodes["index2"] == "GATATAGAGT")
    phiX_condition2 = (top_unknown_barcodes["index"] == "GATATAGAGT") & (top_unknown_barcodes["index2"] == "GATATAGAGT")
    assumed_phiX_reads = top_unknown_barcodes[phiX_condition1 | phiX_condition2]["# Reads"].sum()

    # Calculating percent PhiX assumed
    percent_phix_assumed = assumed_phiX_reads / total_reads if total_reads != 0 else 0

    return {
        "run_yield": run_yield,
        "run_yield_excluding_undetermined": run_yield_excluding_undetermined,
        "total_reads": total_reads,
        "assumed_phiX_reads": assumed_phiX_reads,
        "percent_phix_assumed": percent_phix_assumed
    }

def format_metrics(metrics):
    """
    Formats the numeric metrics for better readability and adds units.

    Parameters:
    metrics (dict): A dictionary containing the metrics to be formatted.

    Returns:
    dict: A dictionary with formatted metric values and units.
    """
    formatted_metrics = {}

    # Formatting numbers with commas and adding units for run_yield and run_yield_excluding_undetermined
    for key in ['run_yield', 'run_yield_excluding_undetermined']:
        formatted_metrics[key] = "{:,} >= Q30 Bases".format(metrics[key])

    # Formatting numbers with commas and adding units for total_reads and assumed_phiX_reads
    for key in ['total_reads', 'assumed_phiX_reads']:
        formatted_metrics[key] = "{:,} Reads PF".format(metrics[key])

    # Formatting percentage
    formatted_metrics['percent_phix_assumed'] = "{:.2%}".format(metrics['percent_phix_assumed'])

    return formatted_metrics

# This block will only run if the script is executed directly, not when imported
if __name__ == "__main__":
    file_path = '/path/to/your/file.csv'
    demux_stats, top_unknown_barcodes = read_dataframes(file_path)
    metrics = calculate_metrics(demux_stats, top_unknown_barcodes)

    # Print the calculated metrics
    for key, value in metrics.items():
        print(f"{key}: {value}")
