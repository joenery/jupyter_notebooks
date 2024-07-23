import sqlite3

def create_database_schema(db_file):
    # Establish a connection to the SQLite database
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Create the TissueBlocks table
    c.execute('''
        CREATE TABLE IF NOT EXISTS TissueBlocks (
            TissueBlockID INTEGER PRIMARY KEY,
            TissueName TEXT NOT NULL
        )
    ''')

    # Create the MerScopeRuns table
    c.execute('''
        CREATE TABLE IF NOT EXISTS MerScopeRuns (
            RunID TEXT PRIMARY KEY,
            TissueBlockID INTEGER NOT NULL,
            FOREIGN KEY (TissueBlockID) REFERENCES TissueBlocks (TissueBlockID)
        )
    ''')

    # Create the TrelloCards table
    c.execute('''
        CREATE TABLE IF NOT EXISTS TrelloCards (
            CardID TEXT PRIMARY KEY,
            RunID TEXT NOT NULL,
            CardName TEXT NOT NULL,
            FOREIGN KEY (RunID) REFERENCES MerScopeRuns (RunID)
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def create_database_with_text_ids(db_name):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # Create the TissueBlocks table with TissueBlockID as TEXT
    c.execute('''
        CREATE TABLE IF NOT EXISTS TissueBlocks (
            TissueBlockID TEXT PRIMARY KEY,
            TissueName TEXT NOT NULL
        )
    ''')

    # Create the MerScopeRuns table with RunID as TEXT and TissueBlockID as TEXT
    c.execute('''
        CREATE TABLE IF NOT EXISTS MerScopeRuns (
            RunID TEXT PRIMARY KEY,
            TissueBlockID TEXT NOT NULL,
            FOREIGN KEY (TissueBlockID) REFERENCES TissueBlocks (TissueBlockID)
        )
    ''')

    # Create the TrelloCards table with CardID and RunID as TEXT
    c.execute('''
        CREATE TABLE IF NOT EXISTS TrelloCards (
            CardID TEXT PRIMARY KEY,
            RunID TEXT NOT NULL,
            CardName TEXT NOT NULL,
            FOREIGN KEY (RunID) REFERENCES MerScopeRuns (RunID)
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def insert_data_into_db(tissue_block_id, run_id, card_id, card_name):
    """
    Inserts data into TissueBlocks, MerScopeRuns, and TrelloCards tables.

    Parameters:
    - tissue_block_id (str): TissueBlock ID to be used as TissueName and TissueBlockID.
    - run_id (str): Run ID to be inserted into MerScopeRuns.
    - card_id (str): Card ID to be inserted into TrelloCards.
    - card_name (str): Card Name to be inserted into TrelloCards.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect('merscope.db')
    c = conn.cursor()
    
    # Insert into TissueBlocks
    c.execute('''
        INSERT INTO TissueBlocks (TissueBlockID, TissueName) VALUES (?, ?)
        ON CONFLICT(TissueBlockID) DO UPDATE SET TissueName = excluded.TissueName;
    ''', (tissue_block_id, tissue_block_id))

    # Insert into MerScopeRuns
    c.execute('''
        INSERT INTO MerScopeRuns (RunID, TissueBlockID) VALUES (?, ?)
        ON CONFLICT(RunID) DO NOTHING;
    ''', (run_id, tissue_block_id))

    # Insert into TrelloCards
    c.execute('''
        INSERT INTO TrelloCards (CardID, RunID, CardName) VALUES (?, ?, ?)
        ON CONFLICT(CardID) DO UPDATE SET RunID = excluded.RunID, CardName = excluded.CardName;
    ''', (card_id, run_id, card_name))

    # Commit changes and close connection
    conn.commit()
    conn.close()