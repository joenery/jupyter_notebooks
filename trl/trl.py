#!/usr/bin/env python3

import os
import requests
import pandas as pd

def get_card_id_by_name(card_name, board_id, api_key, token):
    """
    Get the card ID based on the card name and board ID.

    Args:
        card_name (str): The name of the Trello card.
        board_id (str): The ID of the Trello board.

    Returns:
        str: The ID of the Trello card, if found; otherwise, None.
    """
    api_key = os.environ.get('TKEY')
    api_token = os.environ.get('TTOKEN')

    url = f"https://api.trello.com/1/boards/{board_id}/cards"
    params = {
        'key': api_key,
        'token': token
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        cards = response.json()

        for card in cards:
            if card['name'] == card_name:
                return card['id']

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {str(e)}")

    return None

def get_custom_fields_for_card(card_id, api_key, token):
    """
    Retrieves custom field items associated with a Trello card using the Trello API.

    Args:
    - card_id (str): The ID of the Trello card for which to retrieve custom field items.
    - api_key (str): The Trello API key for authentication.
    - token (str): The Trello API token for authentication.

    Returns:
    - custom_fields_df (DataFrame): A Pandas DataFrame containing custom field items associated with the specified card.
                                    Returns None if no custom field items are found or if an error occurs.
    """
    # URL for the Trello API
    url = f"https://api.trello.com/1/cards/{card_id}/customFieldItems?key={api_key}&token={token}"

    # Send a GET request to the Trello API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        card_data = response.json()

        # Check if custom field items exist
        if card_data:  # Check if the response is not empty
            custom_fields = card_data
            return custom_fields
        else:
            print("No custom fields found for this card.")
            return None
    else:
        print("Error:", response.status_code)
        return None

def create_custom_fields_dataframe(custom_fields_list):
    """
    Create a Pandas DataFrame from a list of custom field items.

    Parameters:
    - custom_fields_list (list): A list of dictionaries, where each dictionary represents a custom field item.

    Returns:
    - custom_fields_df (DataFrame): A Pandas DataFrame containing custom field items.
    """
    if custom_fields_list:
        custom_fields_df = pd.DataFrame(custom_fields_list)
        return custom_fields_df
    else:
        print("Custom fields list is empty.")
        return None

def get_custom_field_names(board_id, api_key, token):
    """
    Retrieve custom field names associated with a Trello board using the Trello API.

    Parameters:
    - board_id (str): The ID of the Trello board for which to retrieve custom field names.
    - api_key (str): The Trello API key for authentication.
    - token (str): The Trello API token for authentication.

    Returns:
    - custom_field_names (dict): A dictionary mapping idCustomField values to field names.
                                 Returns None if no custom field names are found or if an error occurs.
    """
    # URL for the Trello API to get board custom fields
    url = f"https://api.trello.com/1/boards/{board_id}/customFields?key={api_key}&token={token}"

    # Send a GET request to the Trello API
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        custom_fields_data = response.json()

        # Create a dictionary to store custom field names
        custom_field_names = {}
        
        # Extract idCustomField and field name mapping
        for field in custom_fields_data:
            custom_field_names[field['id']] = field['name']
        
        return custom_field_names
    else:
        print("Error:", response.status_code)
        return None

def query_df_by_field_name(field_name, custom_field_names, custom_fields_df):
    """
    Query a DataFrame using the field name obtained from the idCustomField.

    Parameters:
    - field_name (str): The name of the custom field to query.
    - custom_field_names (dict): A dictionary mapping idCustomField values to field names.
    - custom_fields_df (DataFrame): The DataFrame containing custom field items.

    Returns:
    - filtered_df (DataFrame): A DataFrame containing rows filtered based on the field name.
                               Returns None if no custom field is found with the given name.
    """
    # Retrieve idCustomField corresponding to the field name
    id_custom_field = None
    for id_custom, name in custom_field_names.items():
        if name == field_name:
            id_custom_field = id_custom
            break

    if id_custom_field is None:
        print(f"No custom field found with name '{field_name}'")
        return None

    # Filter DataFrame based on idCustomField
    filtered_df = custom_fields_df[custom_fields_df['idCustomField'] == id_custom_field]
    return filtered_df

def create_custom_fields_values_dataframe(custom_fields_df, custom_field_names):
    """
    Create a new DataFrame with field names and their corresponding values.

    Parameters:
    - custom_fields_df (DataFrame): The DataFrame containing custom field items.
    - custom_field_names (dict): A dictionary mapping idCustomField values to field names.

    Returns:
    - custom_fields_values_df (DataFrame): A new DataFrame containing field names and their values.
    """
    custom_fields_values = []

    for _, row in custom_fields_df.iterrows():
        field_name = custom_field_names.get(row['idCustomField'], 'Unknown Field')
        field_value = row['value']
        custom_fields_values.append({'Field Name': field_name, 'Field Value': field_value})

    custom_fields_values_df = pd.DataFrame(custom_fields_values)
    return custom_fields_values_df

def extract_value_from_dict(field_value):
    """
    Extracts value from a dictionary or returns the original value.

    Parameters:
    - field_value: The value to process.

    Returns:
    - The extracted value if field_value is a dictionary, otherwise returns field_value.
    """
    if isinstance(field_value, dict):  
        return list(field_value.values())[0]  # Extract the value from the dictionary
    else:
        return field_value

def create_custom_fields_values_dataframe(custom_fields_df, custom_field_names, use_dict_values=True):
    """
    Create a new DataFrame with field names and their corresponding values.

    Parameters:
    - custom_fields_df (DataFrame): The DataFrame containing custom field items.
    - custom_field_names (dict): A dictionary mapping idCustomField values to field names.
    - use_dict_values (bool, optional): Whether to extract values from dictionaries or use the dictionaries directly.
                                        Defaults to True.

    Returns:
    - custom_fields_values_df (DataFrame): A new DataFrame containing field names and their values.
    """
    custom_fields_values = []

    for _, row in custom_fields_df.iterrows():
        field_name = custom_field_names.get(row['idCustomField'], 'Unknown Field')
        field_value = extract_value_from_dict(row['value']) if use_dict_values else row['value']
        
        custom_fields_values.append({'Field Name': field_name, 'Field Value': field_value})

    custom_fields_values_df = pd.DataFrame(custom_fields_values)
    return custom_fields_values_df

def fetch_xlsx_attachment_url(card_id, api_key, token):
    """
    Fetches the attachment URL of an xlsx file from a Trello card using
    the Trello API.

    Parameters:
    - card_id: The ID of the Trello card to fetch the attachment URL from.
    - api_key: The API key for Trello API access.
    - token: The token for Trello API access.

    Returns:
    - attachment_url: The URL of the first attachment on the card that contains
                      the string "xlsx". Returns None if not found.
    """
    # Base URL for Trello API requests
    base_url = "https://api.trello.com/1"

    # Construct the URL to get the card's attachments
    url = f"{base_url}/cards/{card_id}/attachments"

    # Parameters for authentication
    query = {
        'key': api_key,
        'token': token,
    }

    # Make the request to Trello API
    response = requests.get(url, params=query)

    # Check for successful response
    if response.status_code == 200:
        attachments = response.json()

        # Find the first attachment that contains "xlsx" in its name.
        for attachment in attachments:
            if 'xlsx' in attachment['name']:
                return attachment['url']

        print('No xlsx attachment found on card')
        return None
    else:
        raise Exception(f"Failed to get attachments: {response.text}")

def get_xlsx_attachment_id(card_id, api_key, token):
    """
    Finds the ID of an attachment with 'xlsx' in its name on a specified Trello card.

    Parameters:
    - card_id: The ID of the Trello card.
    - api_key: Your Trello API key.
    - token: Your Trello token.

    Returns:
    - The ID of the first 'xlsx' file attachment found on the card, or None if no such attachment exists.
    """
    # Construct URL to get all attachments on the card
    attachments_url = f"https://api.trello.com/1/cards/{card_id}/attachments"

    # Parameters for the API request
    params = {
        'key': api_key,
        'token': token,
    }

    # Make the API request
    response = requests.get(attachments_url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        attachments = response.json()

        # Search through attachments for one with 'xlsx' in its name
        for attachment in attachments:
            if 'xlsx' in attachment['name']:
                return attachment['id']

    # Return None if no 'xlsx' attachment is found or request fails
    return None

def download_attachment_with_oauth(card_id, attachment_id, file_name, api_key, token):
    """
    Downloads an attachment from a Trello card using OAuth for authentication.

    Parameters:
    - card_id: The ID of the Trello card.
    - attachment_id: The ID of the attachment to download.
    - file_name: The name of the file to save the attachment as.
    - api_key: Your Trello API key.
    - token: Your Trello token.
    """
    url = f"https://api.trello.com/1/cards/{card_id}/attachments/{attachment_id}/download/{file_name}"

    # Construct the Authorization header
    auth_header = {
        "Authorization": f'OAuth oauth_consumer_key="{api_key}", oauth_token="{token}"'
    }

    # Make the request
    response = requests.get(url, headers=auth_header, stream=True)

    # Check for successful response
    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"File downloaded successfully: {file_name}")
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")

def get_list_id(list_name, board_id, api_key, token):
    url = f"https://api.trello.com/1/boards/{board_id}/lists"
    querystring = {
        'key': api_key,
        'token': token
    }
    response = requests.get(url, params=querystring)
    response.raise_for_status()
    lists = response.json()
    
    for trello_list in lists:
        if trello_list['name'] == list_name:
            return trello_list['id']

    # If the list is not found, return None
    return None

def get_custom_field_id(board_id, field_name, api_key, token):
    """
    Fetch the custom field ID for a given custom field name on a Trello board.

    Parameters:
    - board_id (str): The ID of the Trello board.
    - field_name (str): The name of the custom field.
    - api_key (str): Your Trello API key.
    - token (str): Your Trello token for API access.

    Returns:
    - str: The ID of the custom field, or None if not found.
    """
    # Endpoint to get all custom fields on a board
    url = f"https://api.trello.com/1/boards/{board_id}/customFields"
    params = {
        'key': api_key,
        'token': token
    }

    # Make the API request
    response = requests.get(url, params=params)
    if response.status_code == 200:
        custom_fields = response.json()

        # Search for the custom field by name
        for field in custom_fields:
            if field['name'] == field_name:
                return field['id']

    # Return None if not found or if there's an error
    return None

