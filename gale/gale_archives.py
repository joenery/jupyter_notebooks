import os
import sqlite3
from sqlite3 import Error
import pandas as pd
from datetime import datetime
import re

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Successfully connected to SQLite. SQLite version: {sqlite3.version}")
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_database(db_path="archives.db"):
    # Updated SQL for the Paths table to include creation and modification dates
    sql_create_paths_table = """ CREATE TABLE IF NOT EXISTS Paths (
                                        path_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        path TEXT NOT NULL UNIQUE,
                                        path_type TEXT NOT NULL CHECK (path_type IN ('file', 'directory')),
                                        created_at DATETIME NOT NULL,
                                        modified_at DATETIME NOT NULL,
                                        is_removed BOOLEAN NOT NULL DEFAULT FALSE
                                    ); """

    # Archives table creation SQL remains unchanged, but ensure it aligns with your current database schema
    sql_create_archives_table = """CREATE TABLE IF NOT EXISTS Archives (
                                    archive_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    path_id INTEGER,
                                    archive_type TEXT NOT NULL CHECK (archive_type IN ('dsmc', 'aws')),
                                    archive_status TEXT NOT NULL,
                                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                                    additional_info TEXT,
                                    FOREIGN KEY (path_id) REFERENCES Paths(path_id) ON DELETE CASCADE
                                    UNIQUE(path_id, archive_type) -- Composite unique constraint
                                );"""

    # Create a database connection
    conn = create_connection(db_path)

    # Create tables
    if conn is not None:
        create_table(conn, sql_create_paths_table)
        create_table(conn, sql_create_archives_table)
        print("Tables were created successfully.")
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

def list_table_names(db_path):
    """
    List all table names in the SQLite database specified by db_path.
    
    :param db_path: Path to the SQLite database file.
    :return: A list of table names in the database.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query to select all table names from sqlite_master
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        
        # Fetch all results and extract table names
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        return table_names
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_db_table(db_path, table_name):
    """
    Return a DataFrame containing the contents of a database table.

    :param db_path: The path to the SQLite database file.
    :param table_name: The name of the table to return.
    :return: A pandas DataFrame of the requested table.
    """
    # Create a connection to the database
    conn = sqlite3.connect(db_path)

    # Query the table and read into a pandas DataFrame
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, conn)

    # Close the database connection
    conn.close()

    # Return the DataFrame
    return df

def get_file_path_for_archive_type(archive_type):
    """
    Determine the file path based on the archive type.
    
    :param archive_type (str): The type of archive ('dsmc' or 'aws').
    :return: The file path associated with the given archive type.
    """
    # Example logic using hardcoded paths for demonstration
    # Replace with os.environ.get(...) for actual environment variables
    file_paths = {
        'dsmc': os.environ.get('ARCHIVED'),
        'aws': os.environ.get('DEEPARCHIVED')
    }
    return file_paths.get(archive_type.lower())

def generate_paths_list(directory_path):
    """
    Generates a list of paths within a given directory where the entry names start with a digit.
    
    :param directory_path: The directory to scan for paths.
    :return: A list of paths meeting the criteria.
    """
    return [os.path.join(directory_path, entry) for entry in os.listdir(directory_path) if entry[0].isdigit()]

def get_paths_from_files_with_regex(directory_path, pattern):
    """
    Retrieves a list of paths from all files in the specified directory whose names match a given regex pattern.
    
    :param directory_path: The directory to search for files matching the regex pattern.
    :param pattern: The regex pattern to match file names against.
    :return: A list of paths found within the files that match the given regex pattern.
    """
    paths = []  # List to store paths
    regex = re.compile(pattern)  # Compile the regex pattern

    # List all files in the directory and filter for those matching the regex
    filtered_files = [file for file in os.listdir(directory_path) if regex.search(file)]

    for filename in filtered_files:
        # Construct the full path to the file
        file_path = os.path.join(directory_path, filename)

        # Open and read the file
        try:
            with open(file_path, 'r') as file:
                # Add each line from the file to the paths list
                paths.extend(line.strip() for line in file if line.strip())
        except IOError as e:
            print(f"Error reading file {filename}: {e}")

    return paths

def get_filesystem_dates(entry_path):
    """
    Tries to retrieve the creation and modification dates for a file or directory.
    If the file or directory has been removed and dates can't be retrieved, returns None.
    
    :param entry_path: The path to the file or directory.
    :return: A tuple of (creation_date, modification_date) or None if the path doesn't exist.
    """
    try:
        creation_time = os.path.getctime(entry_path)
        modification_time = os.path.getmtime(entry_path)
        creation_date = datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d %H:%M:%S")
        modification_date = datetime.fromtimestamp(modification_time).strftime("%Y-%m-%d %H:%M:%S")
        return creation_date, modification_date
    except OSError:
        return None

def update_archive_details_from_list(db_path, paths, archive_type):
    """
    Updates the database with archival details for a list of paths based on a provided archive log file.
    
    Handles cases where files or directories have been removed by setting 'is_removed' accordingly.
    """
    archived_names_log_path = get_file_path_for_archive_type(archive_type)

    try:
        with open(archived_names_log_path, 'r') as file:
            archived_names = {line.strip() for line in file.readlines()}
    except IOError as e:
        print(f"Could not read archived names log file: {e}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for entry_path in paths:
        dates = get_filesystem_dates(entry_path)
        if dates:
            creation_date, modification_date = dates
            is_removed = False
            path_type = 'file' if os.path.isfile(entry_path) else 'directory'
            archive_status = 'complete' if entry_path in archived_names else 'pending'
        else:
            # If dates could not be retrieved, assume the file/directory has been removed
            creation_date = modification_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Placeholder dates
            is_removed = True
            path_type = 'unknown'
            archive_status = 'pending'  # Default to pending if the path is missing

        print(f"Processing: {entry_path}, Type: {path_type}, Archive Status: {archive_status}")
        
        db_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            cursor.execute("""
                INSERT INTO Paths (path, path_type, created_at, modified_at, is_removed)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    path_type=excluded.path_type,
                    created_at=excluded.created_at,
                    modified_at=excluded.modified_at,
                    is_removed=excluded.is_removed;
                """, (entry_path, path_type, creation_date, modification_date, is_removed))

            if not is_removed:
                cursor.execute("SELECT path_id FROM Paths WHERE path = ?", (entry_path,))
                path_id = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO Archives (path_id, archive_type, archive_status, last_updated)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(path_id, archive_type) DO UPDATE SET
                        archive_status=excluded.archive_status,
                        last_updated=excluded.last_updated;
                    """, (path_id, archive_type, archive_status, db_update_time))
        except sqlite3.Error as e:
            print(f"Database error while processing {entry_path}: {e}")

    conn.commit()
    conn.close()
    print(f"Completed updating archive details for provided paths with archive type '{archive_type}'.")

def update_archive_details_in_db(db_path, directory_path, archive_type):
    archived_names_log_path = get_file_path_for_archive_type(archive_type)

    if not archived_names_log_path or not os.path.isfile(archived_names_log_path):
        print(f"Log file path for archive type '{archive_type}' could not be determined or does not exist.")
        return

    with open(archived_names_log_path, 'r') as file:
        archived_names = {line.strip() for line in file.readlines()}

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    numbered_entries = [entry for entry in os.listdir(directory_path) if entry[0].isdigit()]

    for entry in numbered_entries:
        entry_path = os.path.join(directory_path, entry)
        creation_date, modification_date = get_filesystem_dates(entry_path)
        path_type = 'file' if os.path.isfile(entry_path) else 'directory'
        archive_status = 'complete' if entry in archived_names else 'pending'

        print(f"Processing: {entry_path}, Type: {path_type}, Archive Status: {archive_status}")

        # Get the current time for the database update operation
        db_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            cursor.execute("""
                INSERT INTO Paths (path, path_type, created_at, modified_at, is_removed)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    path_type=excluded.path_type,
                    created_at=excluded.created_at,
                    modified_at=excluded.modified_at,
                    is_removed=excluded.is_removed;
                """, (entry_path, path_type, creation_date, modification_date, False))
            print("Inserted/Updated in Paths table successfully.")

        except sqlite3.Error as e:
            print(f"Error updating Paths table for {entry_path}: {e}")

        try:
            cursor.execute("SELECT path_id FROM Paths WHERE path = ?", (entry_path,))
            path_id_result = cursor.fetchone()

            if path_id_result:
                path_id = path_id_result[0]
                cursor.execute("""
                    INSERT INTO Archives (path_id, archive_type, archive_status, last_updated)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(path_id, archive_type) DO UPDATE SET
                        archive_status=excluded.archive_status,
                        last_updated=excluded.last_updated;
                    """, (path_id, archive_type, archive_status, db_update_time))
                print("Inserted/Updated in Archives table successfully.")
            else:
                print(f"No path_id found for {entry_path}")

        except sqlite3.Error as e:
            print(f"Error updating Archives table for {entry_path} with path_id {path_id}: {e}")

    conn.commit()
    conn.close()
    print(f"Completed updating archive details for '{directory_path}' with archive type '{archive_type}'.")

def load_paths_details(db_path):
    """
    Load paths and their details into a DataFrame.

    :param db_path: Path to the SQLite database file.
    :return: A pandas DataFrame with the paths and their details.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)

    # SQL query to join Paths and Archives tables and calculate age
    # Note: SQLite does not have a built-in DATEDIFF function, so we use
    # the Julian day function to calculate the difference in days
    query = """
    SELECT 
        p.path, 
        p.path_type, 
        CASE 
            WHEN p.path_type = 'file' THEN 
                ROUND(julianday('now') - julianday(p.modified_at))
            ELSE 
                ROUND(julianday('now') - julianday(p.created_at))
        END AS age,
        a.archive_type, 
        a.archive_status, 
        p.is_removed
    FROM 
        Paths p
    JOIN 
        Archives a ON p.path_id = a.path_id;
    """

    # Execute the query and load the results into a DataFrame
    df = pd.read_sql_query(query, conn)

    # Close the database connection
    conn.close()

    return df

def get_complete_non_removed_paths(db_path):
    """
    Generate a list of paths that are not removed and have both AWS and DSMC 
    archive status marked as 'complete'.

    :param db_path: Path to the SQLite database file.
    :return: A list of paths meeting the criteria.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL query to find paths that are not removed and have both AWS and DSMC status as 'complete'
    query = """
    SELECT p.path
    FROM Paths p
    WHERE p.is_removed = 0
    AND EXISTS (
        SELECT 1 FROM Archives a WHERE a.path_id = p.path_id AND a.archive_type = 'aws' AND a.archive_status = 'complete'
    )
    AND EXISTS (
        SELECT 1 FROM Archives a WHERE a.path_id = p.path_id AND a.archive_type = 'dsmc' AND a.archive_status = 'complete'
    );
    """

    try:
        cursor.execute(query)
        paths = [row[0] for row in cursor.fetchall()]
        return paths
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

def get_paths_by_archive_status(db_path, archive_criteria):
    """
    Generate a list of paths based on specified archive types and statuses.

    :param db_path: Path to the SQLite database file.
    :param archive_criteria: A dictionary mapping archive types to their desired statuses.
                             Example: {'aws': 'complete', 'dsmc': 'complete'}
    :return: A list of paths meeting the criteria.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Base query to select paths that meet the specified archive criteria
    base_query = """
    SELECT DISTINCT p.path
    FROM Paths p
    WHERE p.is_removed = 0
    """
    
    # Dynamically build the EXISTS subquery for each archive type/status pair
    subqueries = []
    for archive_type, status in archive_criteria.items():
        subquery = f"""
        AND EXISTS (
            SELECT 1 FROM Archives a 
            WHERE a.path_id = p.path_id 
            AND a.archive_type = '{archive_type}' 
            AND a.archive_status = '{status}'
        )
        """
        subqueries.append(subquery)

    # Combine the base query with all subqueries
    final_query = base_query + " ".join(subqueries) + ";"

    try:
        cursor.execute(final_query)
        paths = [row[0] for row in cursor.fetchall()]
        return paths
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

def get_paths_by_archive_status_and_subpath(db_path, archive_criteria, subpath=None):
    """
    Generate a list of paths based on specified archive types, statuses, and an optional substring of the path.

    :param db_path: Path to the SQLite database file.
    :param archive_criteria: A dictionary mapping archive types to their desired statuses.
                             Example: {'aws': 'complete', 'dsmc': 'complete'}
    :param subpath: Optional string for filtering paths that contain this substring.
    :return: A list of paths meeting the criteria.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Base query to select paths that meet the specified archive criteria
    base_query = """
    SELECT DISTINCT p.path
    FROM Paths p
    WHERE p.is_removed = 0
    """
    
    # Filter by subpath if provided
    if subpath:
        base_query += f" AND p.path LIKE '%{subpath}%'"
    
    # Dynamically build the EXISTS subquery for each archive type/status pair
    subqueries = []
    for archive_type, status in archive_criteria.items():
        subquery = f"""
        AND EXISTS (
            SELECT 1 FROM Archives a 
            WHERE a.path_id = p.path_id 
            AND a.archive_type = '{archive_type}' 
            AND a.archive_status = '{status}'
        )
        """
        subqueries.append(subquery)

    # Combine the base query with all subqueries
    final_query = base_query + " ".join(subqueries) + ";"

    try:
        cursor.execute(final_query)
        paths = [row[0] for row in cursor.fetchall()]
        return paths
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

def regexp(expr, item):
    """
    Define a function to be used with SQLite's REGEXP operator.
    
    :param expr: Regular expression pattern.
    :param item: String to test against the regular expression.
    :return: True if there is a match, else False.
    """
    reg = re.compile(expr)
    return reg.search(item) is not None

def get_paths_by_archive_status_and_regex(db_path, archive_criteria, regex=None):
    """
    Generate a list of paths based on specified archive types, statuses, and an optional regex for the path.

    :param db_path: Path to the SQLite database file.
    :param archive_criteria: A dictionary mapping archive types to their desired statuses.
    :param regex: Optional regular expression string for filtering paths.
    :return: A list of paths meeting the criteria.
    """
    conn = sqlite3.connect(db_path)
    conn.create_function("REGEXP", 2, regexp)  # Register the custom REGEXP function
    cursor = conn.cursor()

    base_query = """
    SELECT DISTINCT p.path
    FROM Paths p
    WHERE p.is_removed = 0
    """

    if regex:
        base_query += f" AND p.path REGEXP '{regex}'"
    
    subqueries = []
    for archive_type, status in archive_criteria.items():
        subquery = f"""
        AND EXISTS (
            SELECT 1 FROM Archives a
            WHERE a.path_id = p.path_id
            AND a.archive_type = '{archive_type}'
            AND a.archive_status = '{status}'
        )
        """
        subqueries.append(subquery)

    final_query = base_query + " ".join(subqueries) + ";"

    try:
        cursor.execute(final_query)
        paths = [row[0] for row in cursor.fetchall()]
        return paths
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

def set_path_status(db_path, path, archive_type, status):
    """
    Sets the archive status of a given path for a specified archive_type to the provided status.

    :param db_path: Path to the SQLite database file.
    :param path: The path whose status needs to be updated.
    :param archive_type: The type of archive ('aws', 'dsmc', etc.) whose status is to be updated.
    :param status: The new status to set for the path ('complete', 'pending', etc.).
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Find the path_id from the Paths table
        cursor.execute("SELECT path_id FROM Paths WHERE path = ?", (path,))
        result = cursor.fetchone()

        if result:
            path_id = result[0]

            # Update the Archives table to set the status to the provided value
            cursor.execute("""
                UPDATE Archives
                SET archive_status = ?, last_updated = datetime('now')
                WHERE path_id = ? AND archive_type = ?
            """, (status, path_id, archive_type))

            # Check if the update was successful
            if cursor.rowcount == 0:
                print(f"No existing record found for {path} with archive_type '{archive_type}'.")
            else:
                print(f"Archive status set to '{status}' for {path} with archive_type '{archive_type}'.")

        else:
            print(f"Path not found: {path}")

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def fetch_filtered_paths_and_archives(db_path, path_pattern=None, archive_type=None, archive_status=None):
    sql_query = """
    SELECT
        p.path,
        p.path_type,
        p.created_at,
        p.modified_at,
        p.is_removed,
        a.archive_type,
        a.archive_status,
        a.last_updated
    FROM
        Paths p
    JOIN
        Archives a ON p.path_id = a.path_id
    """
    params = []
    conditions = []

    if archive_type:
        conditions.append("a.archive_type = ?")
        params.append(archive_type)
    
    if archive_status:
        conditions.append("a.archive_status = ?")
        params.append(archive_status)
    
    if path_pattern:
        conditions.append("p.path LIKE ?")
        params.append(path_pattern)  # For simple patterns, use SQLite's LIKE syntax
    
    if conditions:
        sql_query += " WHERE " + " AND ".join(conditions)

    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(sql_query, conn, params=params)
        return df
    finally:
        conn.close()