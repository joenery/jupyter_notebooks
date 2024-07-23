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

import sqlite3

def update_archive_status(base_path, db_path, archive_type='DSMCArchives'):
    """
    Update the archive status based on directories listed in a specific file,
    determined by the archive type, and handle special path cases.
    
    Parameters:
    - base_path (str): The base directory to search through.
    - db_path (str): Path to the SQLite database.
    - archive_type (str): The archive type, which determines the file to use.
    """
    # Use the helper function to determine the correct file path
    file_path = get_file_path_for_archive_type(archive_type)
    if not file_path:
        raise ValueError(f"File path for archive type '{archive_type}' could not be determined.")
    
    # Load archived directories from file
    with open(file_path, 'r') as f:
        archived_dirs = {line.strip() for line in f}
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for dir_name in os.listdir(base_path):
        if re.match(r'^\d', dir_name) and dir_name in archived_dirs:
            gale_path = os.path.join(base_path, dir_name)
            if base_path == "/gale/netapp/seq2/illumina_runs":
                sculpin_path = f"/archive/gale-netapp/seq2/{dir_name}"
            else:
                sculpin_path = gale_path
            
            # Attempt to insert into Paths, handling potential duplicates gracefully
            cursor.execute("""
                INSERT OR IGNORE INTO Paths (gale_path, sculpin_path) 
                VALUES (?, ?)
                """, (gale_path, sculpin_path))
            
            # Retrieve the path_id for the current path
            cursor.execute("SELECT id FROM Paths WHERE gale_path = ?", (gale_path,))
            path_id = cursor.fetchone()[0]
            
            # Check if a record already exists for this path_id in the archive table
            cursor.execute(f"SELECT id FROM {archive_type} WHERE path_id = ?", (path_id,))
            existing_record = cursor.fetchone()
            
            if existing_record:
                # Update the existing record
                cursor.execute(f"""
                    UPDATE {archive_type} 
                    SET archive_status = 'Complete', last_updated = CURRENT_TIMESTAMP 
                    WHERE path_id = ?
                    """, (path_id,))
            else:
                # Insert a new record if it does not exist
                cursor.execute(f"""
                    INSERT INTO {archive_type} (path_id, archive_status) 
                    VALUES (?, 'Complete')
                    """, (path_id,))
    
    conn.commit()
    conn.close()

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
        'DSMCArchives': os.environ.get('ARCHIVED'),
        'AWSArchives': os.environ.get('DEEPARCHIVED')
    }
    return file_paths.get(archive_type)

def update_archive_status(base_path, db_path, archive_type='DSMCArchives'):
    """
    Update the archive status based on directories listed in a specific file,
    determined by the archive type, and handle special path cases.
    
    Parameters:
    - base_path (str): The base directory to search through.
    - db_path (str): Path to the SQLite database.
    - archive_type (str): The archive type ('AWSArchives' or 'DSMCArchives'), which determines the file to use.
    """
    # Use the helper function to determine the correct file path
    file_path = get_file_path_for_archive_type(archive_type)
    if not file_path:
        raise ValueError(f"File path for archive type '{archive_type}' could not be determined.")

    # Load archived directories from file
    with open(file_path, 'r') as f:
        archived_dirs = {line.strip() for line in f}
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Iterate through directories in the base path
    for dir_name in os.listdir(base_path):
        # Check if the directory starts with a number
        if re.match(r'^\d', dir_name) and dir_name in archived_dirs:
            # Construct new gale_path and determine sculpin_path
            gale_path = os.path.join(base_path, dir_name)
            sculpin_path = f"/archive/gale-netapp/seq2/{dir_name}" if base_path == "/gale/netapp/seq2/illumina_runs" else gale_path
            
            # Insert into Paths table
            cursor.execute("""
                INSERT INTO Paths (gale_path, sculpin_path) 
                VALUES (?, ?)
                ON CONFLICT(gale_path) DO UPDATE SET sculpin_path=excluded.sculpin_path
                """, (gale_path, sculpin_path))
            path_id = cursor.lastrowid  # Get the id of the newly inserted path
            
            # Dynamically set archive status in the specified archive table
            cursor.execute(f"""
                INSERT INTO {archive_type} (path_id, archive_status) 
                VALUES (?, 'Complete')
                ON CONFLICT(path_id) DO UPDATE SET archive_status=excluded.archive_status
                """, (path_id,))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

def update_or_insert_archive_status(base_path, db_path, archive_type, status='Not Started'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the gale_path or sculpin_path exists in the Paths table
    cursor.execute("SELECT id FROM Paths WHERE gale_path = ? OR sculpin_path = ?", (base_path, base_path))
    row = cursor.fetchone()

    if row:
        path_id = row[0]
        # Check if there is an existing entry in the AWSArchives table
        cursor.execute(f"SELECT id FROM {archive_type} WHERE path_id = ?", (path_id,))
        archive_row = cursor.fetchone()
        
        if archive_row:
            # Update the existing entry with the new status
            cursor.execute(f"UPDATE {archive_type} SET archive_status = ? WHERE id = ?", (status, archive_row[0]))
        else:
            # Insert a new entry if it doesn't exist
            cursor.execute(f"INSERT INTO {archive_type} (path_id, archive_status) VALUES (?, ?)", (path_id, status))
    else:
        print("Path does not exist in the Paths table. Please add it before updating the archive status.")
    
    conn.commit()
    conn.close()


def check_dsmc_status(db_path, gale_path=None, sculpin_path=None):
    """
    Check the DSMC archive status of a given path.
    
    Parameters:
    - db_path (str): Path to the SQLite database.
    - gale_path (str): The gale_path to check. Optional if sculpin_path is provided.
    - sculpin_path (str): The sculpin_path to check. Optional if gale_path is provided.
    
    Returns:
    - str or None: The archive status if found, None otherwise.
    """
    # Validate input
    if not gale_path and not sculpin_path:
        raise ValueError("Either gale_path or sculpin_path must be provided.")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Construct the query
    query = """
    SELECT DSMCArchives.archive_status
    FROM Paths
    JOIN DSMCArchives ON Paths.id = DSMCArchives.path_id
    WHERE 
    """
    if gale_path:
        query += "Paths.gale_path = ?"
        path_to_check = gale_path
    else:
        query += "Paths.sculpin_path = ?"
        path_to_check = sculpin_path
    
    # Execute the query
    cursor.execute(query, (path_to_check,))
    result = cursor.fetchone()
    
    # Close the connection
    conn.close()
    
    # Return the result
    if result:
        return result[0]  # Return the archive status
    else:
        return None  # Indicate that no status was found


def print_paths_and_status(db_path, archive_table, server_path='gale_path'):
    """
    Prints a DataFrame of paths and their statuses from the specified archive table,
    choosing between 'gale_path' or 'sculpin_path' based on the server_path parameter.

    Parameters:
    - db_path (str): Path to the SQLite database file.
    - archive_table (str): The name of the archive table ('AWSArchives' or 'DSMCArchives').
    - server_path (str): Determines which path column to use ('gale_path' or 'sculpin_path').
    """
    # Ensure the server_path is valid
    if server_path not in ['gale_path', 'sculpin_path']:
        raise ValueError("server_path must be 'gale_path' or 'sculpin_path'")
    
    # Construct the SQL query
    query = f"""
    SELECT Paths.{server_path} AS server_path, {archive_table}.archive_status
    FROM {archive_table}
    JOIN Paths ON Paths.id = {archive_table}.path_id
    ORDER BY Paths.{server_path};
    """

    # Connect to the database and execute the query using pandas
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn)

    # Close the connection
    conn.close()

    # Print the DataFrame
    print(df)
