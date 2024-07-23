#!/usr/bin/env python3

import requests
import pandas as pd

def get_card_fields(api_key, api_token, card_id):
    """
    Get all fields of a specific card.

    Parameters:
    - api_key (str): The API key for Trello.
    - api_token (str): The API token for authentication.
    - card_id (str): The ID of the card to retrieve fields for.

    Returns:
    - dict: A dictionary containing all fields of the card as JSON.
    """
    url = f"https://api.trello.com/1/cards/{card_id}?key={api_key}&token={api_token}"
    response = requests.get(url)
    return response.json()

def get_custom_fields(api_key, api_token, card_id):
    """
    Get custom fields for a specific card.

    Parameters:
    - api_key (str): The API key for Trello.
    - api_token (str): The API token for authentication.
    - card_id (str): The ID of the card to retrieve custom fields for.

    Returns:
    - dict: The raw JSON response from the API.
    """
    url = f"https://api.trello.com/1/cards/{card_id}/customFieldItems?key={api_key}&token={api_token}"
    response = requests.get(url)
    return response.json()

def get_checklist_items(api_key, api_token, card_id):
    """
    Get checklist items for a specific card.

    Parameters:
    - api_key (str): The API key for Trello.
    - api_token (str): The API token for authentication.
    - card_id (str): The ID of the card to retrieve checklist items for.

    Returns:
    - dict: The raw JSON response from the API.
    """
    url = f"https://api.trello.com/1/cards/{card_id}?key={api_key}&token={api_token}&checklists=all"
    response = requests.get(url)
    return response.json()

def get_custom_fields_and_checklists(api_key, api_token, board_id, filter_string=None):
    """
    Get custom fields and checklist items for all cards on a Trello board.

    Parameters:
    - api_key (str): The API key for Trello.
    - api_token (str): The API token for authentication.
    - board_id (str): The ID of the Trello board to retrieve cards from.
    - filter_string (str, optional): A string to filter cards by name. If provided, only cards containing this string in their name will be included.
    """
    url = f"https://api.trello.com/1/boards/{board_id}/cards?key={api_key}&token={api_token}"
    response = requests.get(url)
    cards = response.json()

    for card in cards:
        card_name = card["name"]
        if filter_string and filter_string.lower() not in card_name.lower():
            continue  # Skip card if it doesn't contain the filter string
        card_id = card["id"]
        custom_fields_json = get_custom_fields(api_key, api_token, card_id)
        checklist_items_json = get_checklist_items(api_key, api_token, card_id)
        fields_json = get_card_fields(api_key, api_token, card_id)
        
        print(f"Card Name: {card_name}")
        #print(f"Card ID: {card_id}")
        #print("Custom Fields JSON:", custom_fields_json)
        #print("Checklist Items JSON:", checklist_items_json)
        print("Fields JSON:", fields_json)
        print()

def json_to_dataframe(json_data):
    """
    Convert JSON data to a DataFrame.

    Parameters:
    - json_data (dict): The JSON data to convert.

    Returns:
    - pd.DataFrame: A DataFrame containing the JSON data.
    """
    return pd.DataFrame(json_data)

def get_last_update_timestamp(api_key, api_token, card_id):
    """
    Retrieve the timestamp of the last update for a Trello card.

    Parameters:
        api_key (str): Your Trello API key.
        api_token (str): Your Trello API token.
        card_id (str): The ID of the Trello card to retrieve information for.

    Returns:
        str: Timestamp of the last update in ISO 8601 format (YYYY-MM-DDTHH:MM:SS.ZZZZ).
    """
    # URL to fetch card details
    url = f"https://api.trello.com/1/cards/{card_id}?key={api_key}&token={api_token}"

    # Send GET request to Trello API
    response = requests.get(url)

    # Check if request was successful
    if response.status_code == 200:
        # Parse JSON response
        card_data = response.json()

        # Extract last activity timestamp
        last_activity = card_data['dateLastActivity']

        return last_activity
    else:
        print("Failed to fetch card details. Status code:", response.status_code)
        return None