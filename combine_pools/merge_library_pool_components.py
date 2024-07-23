import pandas as pd
import os

def read_csv_file(file_path):
    """
    Read a CSV file from the specified file path.
    """
    data = pd.read_csv(file_path)
    return data

def merge_library_pool_components_dfs(df1, df2):
    """
    Merge two DataFrames from library pool components and return the merged result with updated 'library_pool_local_name'.
    """
    merged_df = pd.concat([df1, df2], ignore_index=True)
    unique_names_1 = df1['library_pool_local_name'].unique()
    unique_names_2 = df2['library_pool_local_name'].unique()
    concatenated_name = '_'.join(sorted([unique_names_1[0], unique_names_2[0]]))
    merged_df['library_pool_local_name'] = concatenated_name
    return merged_df, concatenated_name

def write_csv_file(data, output_file_path):
    """
    Write DataFrame to a specified CSV file path.
    """
    output_directory = os.path.dirname(output_file_path)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    data.to_csv(output_file_path, index=False)

def check_and_convert_date_format(data, column_name, original_format, target_format):
    """
    Attempt to parse the date using an original format and convert it to a target format.
    """
    parsed_date = pd.to_datetime(data[column_name], format=original_format, errors='coerce')
    if not parsed_date.isnull().all():
        data[column_name] = parsed_date.dt.strftime(target_format)

def process_library_pool(input_directory, output_directory, concatenated_name, new_barcode=None):
    """
    Process the library pool CSV by reading, updating specific fields, and writing to a new location.
    """
    library_pool_path = os.path.join(input_directory, 'library_pool.csv')
    data = read_csv_file(library_pool_path)
    
    if 'library_pool_preparation_date' in data.columns:
        check_and_convert_date_format(data, 'library_pool_preparation_date', '%y/%m/%d', '%m/%d/%Y')

    if 'library_pool_local_name' in data.columns and 'library_pool_local_tube_id' in data.columns:
        data['library_pool_local_name'] = concatenated_name
        data['library_pool_local_tube_id'] = concatenated_name

    if new_barcode is not None:
        data['library_pool_tube_barcode'] = new_barcode

    output_file_path = os.path.join(output_directory, 'library_pool.csv')
    write_csv_file(data, output_file_path)

def combine_pools(input_directory1, input_directory2, new_barcode=None):
    """
    Combines library pool data from two directories, updating and saving the results to a new directory 
    based on the combined names.
    """
    library_pool_component_path1 = os.path.join(input_directory1, 'library_pool_component.csv')
    library_pool_component_path2 = os.path.join(input_directory2, 'library_pool_component.csv')
    
    df1 = read_csv_file(library_pool_component_path1)
    df2 = read_csv_file(library_pool_component_path2)
    merged_df, concatenated_name = merge_library_pool_components_dfs(df1, df2)
    
    output_directory = os.path.join(os.path.dirname(input_directory1), concatenated_name)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        
    output_file_path = os.path.join(output_directory, 'library_pool_component.csv')
    write_csv_file(merged_df, output_file_path)
    
    if new_barcode is not None:
        process_library_pool(input_directory1, output_directory, concatenated_name, new_barcode)
    else:
        process_library_pool(input_directory1, output_directory, concatenated_name)
    
    concatenate_csvs_in(input_directory1, input_directory2)

def concatenate_csvs(file1, file2, output_file, axis=0):
    """
    Concatenates two CSV files and saves the result to a new CSV file.

    Parameters:
    - file1: str, path to the first CSV file
    - file2: str, path to the second CSV file
    - output_file: str, path to the output CSV file
    - axis: int, axis to concatenate along (0 for rows, 1 for columns)

    Returns:
    - None
    """
    # Read the CSV files
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Concatenate the DataFrames along the specified axis
    result = pd.concat([df1, df2], axis=axis)

    # Save the concatenated DataFrame to a new CSV file
    result.to_csv(output_file, index=False)
    print(f"Files concatenated successfully and saved to {output_file}")

def concatenate_csvs_in(dir1, dir2):
    """
    Concatenates CSV files with the same name from two directories and saves the result to a new directory.

    Parameters:
    - dir1: str, path to the first directory
    - dir2: str, path to the second directory

    Returns:
    - None
    """
    # Extract the common path and the basenames
    common_path = os.path.commonpath([dir1, dir2])
    base1 = os.path.basename(dir1)
    base2 = os.path.basename(dir2)
    
    # Create the output directory
    output_dir = os.path.join(common_path, f"{base1}_{base2}")
    os.makedirs(output_dir, exist_ok=True)

    # List of filenames to concatenate
    filenames = ["barcoded_cell_sample_component.csv", "barcoded_cell_sample.csv", "library.csv"]

    # Concatenate each file
    for filename in filenames:
        file1 = os.path.join(dir1, filename)
        file2 = os.path.join(dir2, filename)
        output_file = os.path.join(output_dir, filename)
        concatenate_csvs(file1, file2, output_file)

