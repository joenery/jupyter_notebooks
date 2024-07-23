import matplotlib.pyplot as plt
import re
import numpy as np
import pandas as pd
import sqlite3
from io import StringIO

def get_pool_strings(file_name):
    """
    Extracts the substring between double underscores and all occurrences of the pattern 
    'SALK' followed by digits from that substring in the given file name.

    Args:
    file_name (str): The input file name containing the substrings to extract.

    Returns:
    tuple: A tuple containing:
        - The extracted substring between double underscores (str) or None if no match is found.
        - A list of all occurrences of 'SALK' followed by digits within the extracted substring (list) or an empty list if no matches are found.
    """
    # Extract the substring between double underscores
    match = re.search(r'__(.*?)__', file_name)
    if match:
        pool_string = match.group(1)
        # Find all occurrences of 'SALK' followed by digits within the extracted substring
        pool_strings = re.findall(r'SALK\d+', pool_string)
        return pool_string, pool_strings
    else:
        return None, []

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

def read_dataframes_old(file_path):
    """
    Reads two tables from a CSV file into pandas dataframes,
    dynamically determining the transition based on a specific string.
    """
    transition_row = find_transition_row(file_path)
    #if transition_row is None:
    #    raise ValueError("Transition string '[Top Unknown Barcodes]' not found in the file.")

    if transition_row is None:
        # If no transition row is found, read only the first table
        demux_stats = pd.read_csv(file_path)
        return demux_stats, None
    
    # Adjust for 0-based indexing in pandas and to skip the header of the second table
    second_table_start = transition_row + 1  # To start reading from the data right after the header

    # Read the first table, ignoring empty lines just above the transition string
    demux_stats = pd.read_csv(file_path, nrows=transition_row - 1)  # Read up to the row before the transition row

    # Read the second table, skipping rows up to and including the transition row
    top_unknown_barcodes = pd.read_csv(file_path, skiprows=second_table_start)

    return demux_stats, top_unknown_barcodes

def calculate_metrics_old(demux_stats, top_unknown_barcodes):
    # Check for the column for Q30 bases and sum accordingly
    if "# of >= Q30 Bases (PF)" in demux_stats.columns:
        run_yield = int(demux_stats["# of >= Q30 Bases (PF)"].sum())
        run_yield_excluding_undetermined = int(demux_stats[~demux_stats["SampleID"].fillna('').str.contains("Undetermined")]["# of >= Q30 Bases (PF)"].sum())
    else:
        run_yield = int(demux_stats["# Reads"].sum())
        run_yield_excluding_undetermined = int(demux_stats[~demux_stats["SampleID"].fillna('').str.contains("Undetermined")]["# Reads"].sum())

    total_reads = int(demux_stats["# Reads"].sum())
    total_reads_excluding_undetermined = int(demux_stats[~demux_stats["SampleID"].fillna('').str.contains("Undetermined")]["# Reads"].sum())

    if top_unknown_barcodes is not None:
        phiX_condition1 = (top_unknown_barcodes["index"] == "TGCCGTGGAT") & (top_unknown_barcodes["index2"] == "GATATAGAGT")
        phiX_condition2 = (top_unknown_barcodes["index"] == "GATATAGAGT") & (top_unknown_barcodes["index2"] == "GATATAGAGT")
        assumed_phiX_reads = int(top_unknown_barcodes[phiX_condition1 | phiX_condition2]["# Reads"].sum())
        percent_phix_assumed = assumed_phiX_reads / total_reads if total_reads != 0 else 0
    else:
        assumed_phiX_reads = 0
        percent_phix_assumed = 0

    # Find the sample with the fewest reads
    if not demux_stats.empty:
        min_reads = demux_stats['# Reads'].min()
        min_reads_row = demux_stats[demux_stats['# Reads'] == min_reads]
        if not min_reads_row.empty:
            sample_id_with_fewest_reads = min_reads_row['SampleID'].values[0]
            fewest_reads = min_reads_row['# Reads'].values[0]
            plate_with_fewest_reads_in_a_lane = f"{sample_id_with_fewest_reads}: {fewest_reads:,.0f}"
        else:
            plate_with_fewest_reads_in_a_lane = "No data available"
    else:
        plate_with_fewest_reads_in_a_lane = "No data available"

    return {
        "run_yield": run_yield,
        "run_yield_excluding_undetermined": run_yield_excluding_undetermined,
        "total_reads": total_reads,
        "total_reads_excluding_undetermined":total_reads_excluding_undetermined,
        "assumed_phiX_reads": assumed_phiX_reads,
        "percent_phix_assumed": percent_phix_assumed,
        "plate_with_fewest_reads_in_a_lane": plate_with_fewest_reads_in_a_lane
    }

def read_dataframes(run_path, skip_undetermined=False):
    # Define the stop condition
    stop_condition = lambda line: "[Top Unknown Barcodes]" in line

    # Initialize lists to collect lines
    lines_before_top_unknown_barcodes_string = []
    lines_after_top_unknown_barcodes_string = []

    # Use a flag to track which part of the file is being read
    reading_before = True

    with open(run_path, 'r') as file:
        for line in file:
            if skip_undetermined and "Undetermined" in line:
                continue  # Skip lines containing "Undetermined"
            if stop_condition(line):
                reading_before = False
                continue  # Skip the line containing the stop condition itself
            if reading_before:
                if line.strip():  # Avoid adding blank lines
                    lines_before_top_unknown_barcodes_string.append(line)
            else:
                if line.strip():  # Avoid adding blank lines
                    lines_after_top_unknown_barcodes_string.append(line)

    # Create a pandas DataFrame from the collected lines before the stop condition
    if lines_before_top_unknown_barcodes_string:
        demux_stats = pd.read_csv(StringIO(''.join(lines_before_top_unknown_barcodes_string)))
    else:
        demux_stats = pd.DataFrame()  # Create an empty DataFrame if no lines are collected

    # Create a pandas DataFrame from the collected lines after the stop condition
    if lines_after_top_unknown_barcodes_string:
        top_unknown_barcodes = pd.read_csv(StringIO(''.join(lines_after_top_unknown_barcodes_string)))
    else:
        top_unknown_barcodes = pd.DataFrame()  # Create an empty DataFrame if no lines are collected

    # Return both DataFrames
    return demux_stats, top_unknown_barcodes

def calculate_metrics(demux_stats, top_unknown_barcodes=None):
    # Check for the column for Q30 bases and sum accordingly
    if "# of >= Q30 Bases (PF)" in demux_stats.columns:
        run_yield = int(demux_stats["# of >= Q30 Bases (PF)"].sum())
        run_yield_excluding_undetermined = int(demux_stats[~demux_stats["SampleID"].fillna('').str.contains("Undetermined")]["# of >= Q30 Bases (PF)"].sum())
    else:
        run_yield = 0  # Set to 0 if the column is not present
        run_yield_excluding_undetermined = 0  # Set to 0 if the column is not present

    total_reads = int(demux_stats["# Reads"].sum())
    total_reads_excluding_undetermined = int(demux_stats[~demux_stats["SampleID"].fillna('').str.contains("Undetermined")]["# Reads"].sum())

    if top_unknown_barcodes is not None and not top_unknown_barcodes.empty:
        phiX_condition1 = (top_unknown_barcodes["index"] == "TGCCGTGGAT") & (top_unknown_barcodes["index2"] == "GATATAGAGT")
        phiX_condition2 = (top_unknown_barcodes["index"] == "GATATAGAGT") & (top_unknown_barcodes["index2"] == "GATATAGAGT")
        assumed_phiX_reads = int(top_unknown_barcodes[phiX_condition1 | phiX_condition2]["# Reads"].sum())
        percent_phix_assumed = assumed_phiX_reads / total_reads if total_reads != 0 else 0
    else:
        assumed_phiX_reads = 0
        percent_phix_assumed = 0

    # Find the sample with the fewest reads
    if not demux_stats.empty:
        min_reads = demux_stats['# Reads'].min()
        min_reads_row = demux_stats[demux_stats['# Reads'] == min_reads]
        if not min_reads_row.empty:
            sample_id_with_fewest_reads = min_reads_row['SampleID'].values[0]
            fewest_reads = min_reads_row['# Reads'].values[0]
            plate_with_fewest_reads_in_a_lane = f"{sample_id_with_fewest_reads}: {fewest_reads:,.0f}"
        else:
            plate_with_fewest_reads_in_a_lane = "No data available"
    else:
        plate_with_fewest_reads_in_a_lane = "No data available"

    return {
        "run_yield": run_yield,
        "run_yield_excluding_undetermined": run_yield_excluding_undetermined,
        "total_reads": total_reads,
        "total_reads_excluding_undetermined": total_reads_excluding_undetermined,
        "assumed_phiX_reads": assumed_phiX_reads,
        "percent_phix_assumed": percent_phix_assumed,
        "plate_with_fewest_reads_in_a_lane": plate_with_fewest_reads_in_a_lane
    }
    
def format_metrics(metrics):
    formatted_metrics = {}
    for key in ['run_yield', 'run_yield_excluding_undetermined', 'total_reads','total_reads_excluding_undetermined', 'assumed_phiX_reads']:
        if metrics[key] is not None:
            if key in ['run_yield', 'run_yield_excluding_undetermined']:
                formatted_metrics[key] = "{:,} bases".format(metrics[key])
            else:
                formatted_metrics[key] = "{:,} Reads PF".format(metrics[key])
        else:
            if key in ['run_yield', 'run_yield_excluding_undetermined']:
                formatted_metrics[key] = "N/A bases"
            else:
                formatted_metrics[key] = "N/A Reads PF"
    
    if metrics['percent_phix_assumed'] is not None:
        formatted_metrics['percent_phix_assumed'] = "{:.2%}".format(metrics['percent_phix_assumed'])
    else:
        formatted_metrics['percent_phix_assumed'] = "N/A"
    
    formatted_metrics['plate_with_fewest_reads_in_a_lane'] = metrics['plate_with_fewest_reads_in_a_lane']
    return formatted_metrics

def plot_reads_vs_sampleID_reversed(demux_stats, save_dir, pool_string):
    # Convert '# Reads' values to millions for the pivot table
    demux_stats['# Reads in Millions'] = demux_stats['# Reads'] / 1e6

    # Handle non-finite values in 'Lane' column before converting to integers
    demux_stats['Lane'] = demux_stats['Lane'].replace([np.inf, -np.inf], np.nan)
    demux_stats['Lane'] = demux_stats['Lane'].dropna().astype(int)
    
    # Create the pivot table using the converted values
    pivot_table = demux_stats.pivot_table(index='SampleID', columns='Lane', values='# Reads in Millions', fill_value=0)
    
    # Ensure columns are integers
    pivot_table.columns = pivot_table.columns.astype(int)
    
    pivot_table.plot(kind='barh', figsize=(10, 6))
    plt.title(f'{pool_string} Reads PF for Each Plate in Each Lane')
    plt.ylabel('SampleID')
    plt.xlabel('# Reads in Millions')
    plt.legend(title='Lane')
    plt.tight_layout()
    plt.savefig(f"{save_dir}/{pool_string}_reads_pf_broad.png")
    plt.show()
    
    plot_reads_boxplot(demux_stats, save_dir, pool_string)

def plot_reads_boxplot(dataframe, save_dir, pool_string):
    """
    Generates a box plot of the '# Reads' in millions for each 'SampleID' from the provided DataFrame.
    The plot size is set to match the bar plot dimensions (18x8 inches).
    
    Parameters:
        dataframe (pd.DataFrame): The DataFrame containing demultiplexing statistics with columns
                                  'SampleID' and '# Reads'.
        save_dir (str): The directory where the plot image will be saved.
        pool_string (str): A string used in the filename of the saved plot image.
                                  
    Returns:
        None: This function directly displays the box plot.
    """
    # Remove rows where 'SampleID' is 'Undetermined'
    filtered_df = dataframe[dataframe['SampleID'] != 'Undetermined'].copy()

    # Convert '# Reads' values to millions for plotting
    filtered_df.loc[:, '# Reads in Millions'] = filtered_df['# Reads'] / 1e6

    # Creating the box plot with the converted data
    plt.figure(figsize=(10, 6))  # Setting figure size to 18x8 inches
    boxplot = filtered_df.boxplot(column='# Reads in Millions', by='SampleID', vert=False)
    plt.title(f'{pool_string} Reads PF Distribution')
    plt.suptitle('')  # Suppress the default title to clean up the plot display
    plt.xlabel('# Reads in Millions')
    plt.ylabel('SampleID')

    # Adjust vertical distance between y-axis labels
    plt.yticks(fontsize=10)  # Increase the vertical space between labels by adjusting the fontsize

    plt.tight_layout()
    plt.savefig(f"{save_dir}/{pool_string}_reads_pf_broad_box.png")
    plt.show()

def extract_samples(dataframe, sample_ids):
    """
    Extracts rows from the given DataFrame where the 'SampleID' column matches any of the sample IDs in the provided list.

    Parameters:
        dataframe (pd.DataFrame): The DataFrame containing demultiplexing statistics with columns
                                  'SampleID' and '# Reads'.
        sample_ids (list): A list of sample IDs to be extracted.

    Returns:
        pd.DataFrame: A new DataFrame containing only the rows with 'SampleID's matching those in the sample_ids list.
    """
    # Extract rows where 'SampleID' is in the sample_ids list
    extracted_df = dataframe[dataframe['SampleID'].isin(sample_ids)].copy()
    
    return extracted_df

def read_file_to_list(file_path):
    """
    Reads a file and stores each line as an element in a list.

    Parameters:
        file_path (str): The path to the file to be read.

    Returns:
        list: A list where each element is a line from the file.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Remove any trailing newline characters from each line
    lines = [line.strip() for line in lines]
    
    return lines

def extract_samples_from_files(dataframe, files):
    """
    Extracts rows from the given DataFrame where the 'SampleID' column matches any of the sample IDs
    in each provided file, and returns a dictionary of DataFrames.

    Parameters:
        dataframe (pd.DataFrame): The DataFrame containing demultiplexing statistics with columns
                                  'SampleID' and '# Reads'.
        files (list): A list of file paths. Each file contains sample IDs to be extracted, one per line.

    Returns:
        dict: A dictionary where each key is a file path and the value is a DataFrame containing
              the extracted rows for that file.
    """
    extracted_dfs = {}

    # Read each file and collect the corresponding sample IDs
    for file_path in files:
        sample_ids = read_file_to_list(file_path)
        
        # Extract rows where 'SampleID' is in the sample_ids list
        extracted_df = extract_samples(dataframe, sample_ids)
        
        # Add the resulting DataFrame to the dictionary with the file name as the key
        extracted_dfs[file_path] = extracted_df
    
    return extracted_dfs

def setup_database(db_name):
    """
    Sets up the SQLite database with the necessary table.
    
    Parameters:
    db_name (str): The name or path of the SQLite database file.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pool_metrics (
            pool TEXT PRIMARY KEY,
            total_reads INTEGER,
            plate_with_fewest_reads TEXT,
            fewest_read_count INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def add_column_if_not_exists(db_name):
    """
    Checks if the 'percent_phix_assumed' column exists in the 'pool_metrics' table of the specified SQLite database.
    Adds the column if it does not exist.

    Parameters:
    db_name (str): The name or path of the SQLite database file.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Execute PRAGMA to check for existing columns in the table
    cursor.execute('''
        PRAGMA table_info(pool_metrics)
    ''')
    columns = [info[1] for info in cursor.fetchall()]

    # Check if 'percent_phix_assumed' column is missing and add it
    if 'percent_phix_assumed' not in columns:
        cursor.execute('''
            ALTER TABLE pool_metrics ADD COLUMN percent_phix_assumed REAL
        ''')
        print("Column 'percent_phix_assumed' added.")
    else:
        print("Column 'percent_phix_assumed' already exists.")

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print("Database update complete.")


def extract_numeric_value(reads_pf_string):
    """
    Extracts the numeric value from a reads PF string.
    
    Parameters:
    reads_pf_string (str): A string containing the reads PF information.
    
    Returns:
    int: The numeric value extracted from the string.
    """
    return int(re.sub(r'[^\d]', '', reads_pf_string))

def write_to_broad_metrics_db(pool_strings, all_formatted_metrics, db_name):
    """
    Writes the pool names and their corresponding total reads to a SQLite database.
    If a pool already exists, it updates the total reads instead of adding a new entry.
    Extracts and stores additional information about the plate with the fewest reads.
    Prints the pool name with the fewest reads in a lane and total reads.

    Parameters:
    pool_strings (list of str): List of pool names.
    all_formatted_metrics (list of dict): List of dictionaries containing metrics for each pool.
    db_name (str): The name or path of the SQLite database file.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Iterate over the pool_strings and all_formatted_metrics
    for pool, metrics in zip(pool_strings, all_formatted_metrics):
        #total_reads_string = metrics.get('total_reads')
        #total_reads = extract_numeric_value(total_reads_string)
        total_reads = metrics.get('total_reads')
        pool_with_fewest_reads = metrics.get('plate_with_fewest_reads_in_a_lane')

        # Extract plate_with_fewest_reads and fewest_read_count using regex
        match = re.match(r'(.+): ([\d,]+)', pool_with_fewest_reads)
        if match:
            plate_with_fewest_reads = match.group(1)
            fewest_read_count = int(match.group(2).replace(',', ''))
        else:
            plate_with_fewest_reads = None
            fewest_read_count = None

        cursor.execute('''
            INSERT INTO pool_metrics (pool, total_reads, plate_with_fewest_reads, fewest_read_count)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(pool) DO UPDATE SET
            total_reads=excluded.total_reads,
            plate_with_fewest_reads=excluded.plate_with_fewest_reads,
            fewest_read_count=excluded.fewest_read_count
        ''', (pool, total_reads, plate_with_fewest_reads, fewest_read_count))

    conn.commit()
    conn.close()

    print(f"The database, {db_name}, has been updated.")

def query_database(db_name):
    """
    Queries the SQLite database to print all records in the pool_metrics table.
    
    Parameters:
    db_name (str): The name of the SQLite database file.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pool_metrics')
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()

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
