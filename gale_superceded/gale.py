import os
import re
import sqlite3
import pandas as pd

def list_table_names(db_path):
    """
    List all table names in the specified SQLite database.

    Parameters:
    - db_path (str): Path to the SQLite database file.

    Returns:
    - list of str: A list of table names.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Execute the query to retrieve all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    
    # Fetch all results and extract table names
    tables = [row[0] for row in cursor.fetchall()]

    # Clean up and close the database connection
    conn.close()

    return tables


def erase_all_data_from_db(db_path):
    """
    Erases all data from all tables in the specified SQLite database.
    
    Parameters:
    - db_path (str): Path to the SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Retrieve all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Delete all records from each table
    for table_name in tables:
        print(f"Erasing data from table: {table_name[0]}")
        cursor.execute(f"DELETE FROM {table_name[0]};")

    # Commit changes
    conn.commit()

    # Vacuum the database to optimize and shrink the file size
    cursor.execute("VACUUM;")

    # Close the connection
    conn.close()

    print("All data erased from the database.")

def get_or_insert_base_path_id(conn, gale_base, sculpin_base):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM BasePaths WHERE gale_base = ? AND sculpin_base = ?", (gale_base, sculpin_base))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute("INSERT INTO BasePaths (gale_base, sculpin_base) VALUES (?, ?)", (gale_base, sculpin_base))
        conn.commit()
        return cursor.lastrowid

import os

def get_file_path_for_archive_type(archive_type):
    """
    Determine the file path for directories to be archived based on the archive type.
    
    This function uses environment variables to decide the file path for different archive types.
    It can be extended or modified to incorporate more complex logic depending on the application's needs.
    
    Parameters:
    - archive_type (str): The type of archive ('DSMCArchives' or 'AWSArchives').
    
    Returns:
    - str: The file path associated with the given archive type, or None if not defined.
    """
    # Mapping of archive types to environment variables
    env_vars = {
        'DSMCArchives': 'ARCHIVED',
        'AWSArchives': 'DEEPARCHIVED'
    }
    
    # Get the environment variable name for the given archive type
    env_var = env_vars.get(archive_type)
    
    # Return the file path from the environment variable, if it exists
    if env_var:
        return os.environ.get(env_var)
    else:
        print(f"Warning: No environment variable defined for archive type '{archive_type}'.")
        return None

def get_file_path_for_archive_type(archive_type):
    """
    Determine the file path based on the archive type.
    
    Parameters:
    - archive_type (str): The type of archive ('DSMCArchives' or 'AWSArchives').
    
    Returns:
    - str: The file path associated with the given archive type.
    """
    # Example logic using environment variables
    file_paths = {
        'dsmc': os.environ.get('ARCHIVED'),
        'aws': os.environ.get('DEEPARCHIVED')
    }
    return file_paths.get(archive_type)

def update_archive_details_in_db(db_path, directory_path, archive_type):
    """
    Update the database with detailed archive information for files or directories in the specified
    directory that start with a number, based on their presence in a log file of archived names determined
    by the archive type.

    :param db_path: Path to the SQLite database file.
    :param directory_path: Path to the directory to check.
    :param archive_type: The type of archive ('dsmc' or 'aws').
    """
    # Retrieve the path to the log file for the specified archive type
    archived_names_log_path = get_file_path_for_archive_type(archive_type)

    # Ensure the log file path was successfully retrieved
    if not archived_names_log_path or not os.path.isfile(archived_names_log_path):
        print(f"Log file path for archive type '{archive_type}' could not be determined or does not exist.")
        return

    # Read archived names from the log file
    with open(archived_names_log_path, 'r') as file:
        archived_names = [line.strip() for line in file.readlines()]

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Current time for created_at, modified_at, and last_updated columns
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # List all files/directories in the given directory that start with a number
    numbered_entries = [entry for entry in os.listdir(directory_path) if entry[0].isdigit()]

    for entry in numbered_entries:
        archive_status = 'complete' if entry in archived_names else 'pending'
        entry_path = os.path.join(directory_path, entry)
        path_type = 'file' if os.path.isfile(entry_path) else 'directory'

        # Insert or update Paths and Archives details
        # Implementation would follow similarly to the previous examples,
        # adjusting SQL commands and logic to suit your schema and requirements

    # Commit changes and close the database connection
    conn.commit()
    conn.close()

    print(f"Updated archive details for entries in '{directory_path}' with archive type '{archive_type}'.")


def print_paths_and_status(db_path, archive_table, server_base_path='gale_base'):
    """
    Prints a DataFrame of paths and their statuses from the specified archive table,
    choosing between 'gale_base' or 'sculpin_base' based on the server_base_path parameter.
    
    Parameters:
    - db_path (str): Path to the SQLite database file.
    - archive_table (str): The name of the archive table ('AWSArchives' or 'DSMCArchives').
    - server_base_path (str): Determines which base path column to use ('gale_base' or 'sculpin_base'). Defaults to 'gale_base'.
    """
    # Validate server_base_path parameter
    if server_base_path not in ['gale_base', 'sculpin_base']:
        raise ValueError("server_base_path must be 'gale_base' or 'sculpin_base'")
    
    # Construct the SQL query with corrected path concatenation
    query = f"""
    SELECT 
        rtrim(BasePaths.{server_base_path}, '/') || '/' || ltrim(Paths.relative_path, '/') AS full_path, 
        {archive_table}.archive_status
    FROM {archive_table}
    JOIN Paths ON Paths.id = {archive_table}.path_id
    JOIN BasePaths ON BasePaths.id = Paths.base_path_id
    ORDER BY full_path;
    """
    
    # Connect to the database and execute the query using pandas
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn)

    # Close the connection
    conn.close()

    # Print the DataFrame
    print(df)
