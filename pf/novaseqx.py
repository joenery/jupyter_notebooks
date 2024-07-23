import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(filepath):
    """
    Load data from a CSV file.

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the loaded data.
    """
    return pd.read_csv(filepath)

def add_reads_in_billions(dataframe, column_name='# Reads'):
    """
    Adds a new column to the DataFrame with reads converted to billions.

    Args:
        dataframe (pd.DataFrame): DataFrame with read data.
        column_name (str): Name of the column containing read counts.

    Returns:
        pd.DataFrame: DataFrame with the new column added.
    """
    dataframe['# Reads in Billions'] = dataframe[column_name] / 1e9
    return dataframe

def plot_boxplot(dataframe, x_label, y_label, title, rotation=90):
    """
    Generates and displays a box plot for the given DataFrame.

    Args:
        dataframe (pd.DataFrame): DataFrame containing the data to plot.
        x_label (str): Label for the x-axis.
        y_label (str): Label for the y-axis.
        title (str): Title of the plot.
        rotation (int): Degree of rotation for x-axis labels.
    """
    plt.figure(figsize=(14, 8))
    sns.boxplot(data=dataframe, x=x_label, y=y_label)
    plt.xticks(rotation=rotation)  # Rotate x labels for better readability
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True)
    plt.show()

def main():
    """
    Main function to load data, process it, and generate a box plot.
    """
    # Specify the path to the CSV file
    filepath = 'path_to_your_data.csv'
    
    # Load the data
    data = load_data(filepath)
    
    # Add reads in billions
    data = add_reads_in_billions(data)
    
    # Generate the box plot
    plot_boxplot(data, 'SampleID', '# Reads in Billions', 'Box Plot of # Reads Including Undetermined Indices')

if __name__ == "__main__":
    main()
