import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_library_pools_by_date(data):
    """
    Plots a bar chart showing the total number of library pools by shipping date.

    Parameters:
    - data (pd.DataFrame): A pandas DataFrame containing at least two columns:
        'Shipping Date' with dates in datetime format, and
        'Library Pool Count' representing the count of library pools for each record.

    The function aggregates the library pool counts by shipping date, formats the dates,
    and plots a bar chart with seaborn. Shipping dates are displayed on the x-axis,
    and the total number of library pools is displayed on the y-axis.

    Note: Ensure 'Shipping Date' is in datetime format and 'Library Pool Count' is correctly calculated
    before calling this function.

    Example usage:
    >>> plot_library_pools_by_date(data)
    """
    # Aggregate library pool counts by shipping date
    library_pools_per_date = data.groupby('Shipping Date')['Library Pool Count'].sum()

    # Convert the index (which is in datetime format) to string format for plotting
    library_pools_per_date.index = library_pools_per_date.index.strftime('%Y-%m-%d')

    # Create a bar chart
    plt.figure(figsize=(12, 8))
    sns.barplot(x=library_pools_per_date.index, y=library_pools_per_date.values, palette="coolwarm")

    plt.title('Total Number of Library Pools by Shipping Date')
    plt.xlabel('Date')
    plt.ylabel('Total Number of Library Pools')
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()

