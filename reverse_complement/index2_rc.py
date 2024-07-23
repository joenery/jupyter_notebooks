import pandas as pd
import os

def reverse_complement(seq):
    """
    Calculate the reverse complement of a DNA sequence.

    Args:
    seq (str): A string representing a DNA sequence (consisting of A, T, C, G).

    Returns:
    str: The reverse complement of the DNA sequence.
    """
    complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
    return ''.join([complement[base] for base in reversed(seq)])

def index2_rc(file_path):
    """
    Process a BCLConvert CSV file, apply reverse complement to 'index2' column, 
    and concatenate with lines before the header. Writes the result to a new CSV file.

    This function reads a CSV file specified by 'file_path', identifies the header line 
    containing "Sample_ID", and applies a reverse complement transformation to the 'index2' column. 
    It then concatenates any lines found before the header line with the transformed CSV data, 
    and writes the combined content to a new CSV file with the same name but appended with '.new'.

    Args:
    file_path (str): The path to the BCLConvert CSV file.

    Returns:
    str: The path to the newly created CSV file, or an error message if the header is not found or the data is not present.
    """
    header_line = None

    with open(file_path, 'r') as file:
        for i, line in enumerate(file):
            if "Sample_ID" in line:
                header_line = i
                break

    if header_line is not None:
        bclconvert_data = pd.read_csv(file_path, skiprows=header_line)
    else:
        return "Header containing 'Sample_ID' not found or data loading issue"

    if bclconvert_data is not None:
        bclconvert_data['index2'] = bclconvert_data['index2'].apply(reverse_complement)

        # Generate new file name
        new_file_name = os.path.splitext(file_path)[0] + ".index2_rc.csv"

        # Write concatenated DataFrame to new CSV file
        bclconvert_data.to_csv(new_file_name, index=False)
        
        return new_file_name

    return "BCLConvert data not found"
    
# This block will only run if the script is executed directly, not when imported
if __name__ == "__main__":
    # Load the CSV file and perform the operation
    file_path = '/mnt/data/js_1_5.novaseq.bclconvert.sample_sheet.csv'
    result = index2_rc(file_path)
    print("Result:", result)
