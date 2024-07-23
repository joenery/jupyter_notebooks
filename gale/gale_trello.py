#!/usr/bin/env python3
"""
Script for creating a new Trello card and updating a custom field with the specified card name.

Usage:
    python trello-add-card-to-aws-archive-upload-merfish-v1.py "/path/to/file"

Required Environment Variables:
    - TKEY: Trello API key
    - TTOKEN: Trello API token
    - TBOARDID_SEQ_PIPELINE: Trello board ID

Example:
    python trello-add-card-to-aws-archive-upload-merfish-v1.py "/ceph/cephatlas/merscope_data/processed/000000000000_test_vmsctest/000000000000_test_vmsctest.raw.tar.gz"
"""

import os
import requests
import sys

# Retrieve API key, token, and board ID from environment variables
API_KEY = os.environ.get("TKEY")
TOKEN = os.environ.get("TTOKEN")
BOARD_ID = os.environ.get("TBOARDID_SEQ_PIPELINE")
LIST_ID = "64012c1810c953983e3dac09"
FIELD_ID = "63ee7a99ec62faeb23cc164c"

# Set the list name
LIST_NAME = "Trello aws archive upload"

# Trello API endpoint URLs
BASE_URL = "https://api.trello.com/1"
CARDS_URL = f"{BASE_URL}/cards"

def get_board_id_from_card(card_name):
    """
    Get the board ID based on the card name.

    Args:
        card_name (str): The name of the Trello card.

    Returns:
        str: The board ID associated with the card.
    """
    if "SALK" in card_name:
        #print("This is a BICAN card")
        return os.environ.get('TBOARDID_BICAN')
    else:
        #print("This is not a BICAN card")
        return os.environ.get('TBOARDID_SEQ_PIPELINE')

def get_trello_card_comments(card_id, api_key, api_token):
    """
    Retrieves comments from a specified Trello card.

    Parameters:
    - card_id (str): The ID of the Trello card.
    - api_key (str): Your Trello API key.
    - api_token (str): Your Trello API token.

    Returns:
    - List[Dict]: A list of comments, where each comment is represented as a dictionary.
    """
    # The URL for the Trello API endpoint to get actions for a card
    url = f"https://api.trello.com/1/cards/{card_id}/actions"

    # Specify the query parameters, including your API key and token, and a filter for comments
    query = {
        'key': api_key,
        'token': api_token,
        'filter': 'commentCard'  # This filters for comments on the card
    }

    # Make the request to the Trello API
    response = requests.get(url, params=query)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response and return it
        return response.json()
    else:
        print(f"Failed to get comments. Status code: {response.status_code}")
        return []

def extract_upload_comments(data):
    upload_comments = []
    for item in data:
        # Accessing the text of each comment
        text = item.get('data', {}).get('text', '')
        
        # Finding and extracting the part with "upload:"
        if "upload:" in text:
            # This assumes you want the entire comment if "upload:" is found
            # Modify this as needed, for example, to extract just the specific part with "upload:"
            upload_comments.append(text)
    
    return upload_comments

def is_aws_upload_complete(upload_comments):
    # Check if any comments containing "upload:" were found
    if upload_comments:
        # Print or process the extracted comments
        for comment in upload_comments:
            print(comment)
        # Update aws status to complete
        # need to get path in here
    else:
        # No comments with "upload:" were found, perform alternative action
        print("No comments containing 'upload:' were found.")

def post_comment_to_card(card_id, comment_text, api_key, api_token):
    """
    Posts a comment to a Trello card with the given ID.

    Args:
        card_id (str): The ID of the Trello card to comment on.
        comment_text (str): The text of the comment to post.
        api_key (str): Your Trello API key.
        api_token (str): Your Trello API token.

    Returns:
        bool: True if the comment was posted successfully, False otherwise.
    """

    url = f"https://api.trello.com/1/cards/{card_id}/actions/comments"
    # Set up parameters for Trello API request
    params = {
        "key": api_key,
        "token": api_token,
        "text": comment_text
    }

    try:
        response = requests.post(url, params=params)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        print("Comment posted successfully!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error posting comment: {str(e)}")
        return False

def has_comment_with_text(card_id, target_text, api_key, api_token, base_url="https://api.trello.com/1"):
  """
  Checks if a Trello card has a comment containing a specific string.

  Args:
      card_id (str): ID of the Trello card to check.
      target_text (str): The text string to search for in comments.
      api_key (str): Your Trello API key.
      api_token (str): Your Trello API token.
      base_url (str, optional): Base URL for the Trello API (defaults to "https://api.trello.com/1").

  Returns:
      bool: True if a comment containing the target text is found, False otherwise.
  """

  # Construct URL to get card comments
  comments_url = f"{base_url}/cards/{card_id}/comments"

  # Headers with API credentials
  headers = {"Authorization": f"Bearer {api_token}"}

  # Send request to get card comments
  response = requests.get(comments_url, headers=headers)

  if response.status_code == 200:
    comments_data = response.json()
    
    # Search for the comment text
    for comment in comments_data:
      if comment["data"].lower().find(target_text.lower()) != -1:
        return True
    return False
  else:
    print(f"Error retrieving card comments: {response.status_code}")
    return False

def get_card_id(card_name, board_id):
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
        'token': api_token
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

# Find the ID of the list
def get_list_id(board_id, list_name):
    lists_url = f"{BASE_URL}/boards/{board_id}/lists"
    response = requests.get(lists_url, params={"key": API_KEY, "token": TOKEN})
    lists = response.json()
    for l in lists:
        if l["name"] == list_name:
            return l["id"]
    return None

# Find the ID of the custom field based on its name
def get_custom_field_id(board_id, field_name):
    custom_fields_url = f"{BASE_URL}/boards/{board_id}/customFields"
    response = requests.get(custom_fields_url, params={"key": API_KEY, "token": TOKEN})
    custom_fields = response.json()
    for field in custom_fields:
        if field["name"] == field_name:
            return field["id"]
    return None

# Update custom field with the specified value
def update_custom_field(card_id, field_id, value):
    custom_field_url = f"{BASE_URL}/cards/{card_id}/customField/{field_id}/item"
    payload = {
        "key": API_KEY,
        "token": TOKEN,
        "value": {"text": value}
    }
    response = requests.put(custom_field_url, json=payload)
    if response.status_code == 200:
        print("Custom field updated successfully!")
    else:
        print("Custom field update failed.")

# Create a new card
def create_card(list_id, title, description):
  """
  Creates a card in Trello and optionally posts a comment to it.

  Args:
      list_id (str): ID of the Trello list where the card will be created.
      title (str): Title of the new card.
      description (str): Description for the new card (optional).
      comment_text (str): Text for the comment to be posted on the card (optional).
      api_key (str): Your Trello API key.
      api_token (str): Your Trello API token.

  Returns:
      str: The ID of the created card, or None if creation failed.
  """

  payload = {
      "key": API_KEY,
      "token": TOKEN,
      "idList": list_id,
      "name": title,
      "desc": description
  }
  response = requests.post(CARDS_URL, data=payload)

  if response.status_code == 200:
      card_id = response.json()["id"]
      print(card_id)
      comment_text = card_id

      # Post a comment to the card (if comment text provided)
      if comment_text:
          post_comment_to_card(card_id, comment_text, API_KEY, TOKEN)

      # Return the card ID
      return card_id
  else:
      print("Card creation failed.")
      return None  

def trello_aws(path):
    # Retrieve API key, token, and board ID from environment variables
    API_KEY = os.environ.get("TKEY")
    TOKEN = os.environ.get("TTOKEN")
    BOARD_ID = os.environ.get("TBOARDID_SEQ_PIPELINE")
    LIST_ID = "64012c1810c953983e3dac09"
    FIELD_ID = "63ee7a99ec62faeb23cc164c"

    # Set the list name
    LIST_NAME = "Trello aws archive upload"

    # Trello API endpoint URLs
    BASE_URL = "https://api.trello.com/1"
    CARDS_URL = f"{BASE_URL}/cards"

    card_name = path
    list_id = LIST_ID
    create_card(list_id, card_name, "")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python trello-add-card-to-aws-archive-upload-merfish-v1.py \"/path/to/file\"")
        sys.exit(1)

    file_path = sys.argv[1]
    #list_id = get_list_id(BOARD_ID, LIST_NAME)
    list_id = LIST_ID
    if list_id:
        # Use the full file path as the card name
        card_name = file_path
        create_card(list_id, card_name, "")
    else:
        print("List not found.")

def get_all_cards(board_id, api_key, token):
    """
    Fetch all cards from a specified Trello board.

    Parameters:
    - api_key (str): The API key for Trello.
    - token (str): The token for authenticating API requests.
    - board_id (str): The ID of the Trello board.

    Returns:
    - list: A list of cards from the Trello board.
    """
    url = f"https://api.trello.com/1/boards/{board_id}/cards"
    headers = {
        "Accept": "application/json"
    }
    query = {
        'key': api_key,
        'token': token
    }

    response = requests.get(url, headers=headers, params=query)
    if response.status_code == 200:
        return response.json()  # Return a list of card details
    else:
        return f"Failed to retrieve cards with status code: {response.status_code}"

def get_card_id_and_name(card_data):
    """
    Extracts the ID and name from Trello card JSON data.

    Parameters:
    - card_data (dict): A dictionary containing the JSON data of a Trello card.

    Returns:
    - tuple: A tuple containing the ID and name of the card.
    """
    card_id = card_data['id']
    card_name = card_data['name']
    return (card_id, card_name)

def get_custom_field_data(card_id, api_key, token):
    """
    Fetches custom field data for a specific Trello card.

    Parameters:
    - api_key (str): Your Trello API key.
    - token (str): Your Trello token for authentication.
    - card_id (str): The ID of the Trello card.

    Returns:
    - dict: JSON response containing custom field data, or an error message if the request fails.
    """
    url = f"https://api.trello.com/1/cards/{card_id}/customFieldItems"
    params = {
        'key': api_key,
        'token': token
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()  # This returns the list of custom field items as JSON
    else:
        return f"Failed to retrieve custom fields with status code: {response.status_code}"

def get_custom_fields_in_board(board_id, api_key, token):
    """
    Fetches all custom fields defined in a specific Trello board.

    Parameters:
    - board_id (str): The ID of the Trello board.
    - api_key (str): Your Trello API key.
    - token (str): Your Trello token for authentication.

    Returns:
    - list: A list containing the custom fields on the board, or an error message if the request fails.
    """
    url = f"https://api.trello.com/1/boards/{board_id}/customFields"
    params = {
        'key': api_key,
        'token': token
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()  # Returns the list of custom fields as JSON
    else:
        return f"Failed to retrieve custom fields with status code: {response.status_code}"

def extract_custom_field_text(custom_fields_list, target_custom_field_id):
    """
    Extracts the 'text' value from a specific custom field in a list of custom fields.

    Parameters:
    - custom_fields_list (list): A list of dictionaries, each representing a custom field item.
    - target_custom_field_id (str): The ID of the custom field from which to extract the 'text' value.

    Returns:
    - str: The 'text' value of the custom field if available, otherwise None.
    """
    for item in custom_fields_list:
        if item['idCustomField'] == target_custom_field_id:
            # Check if 'value' is not None and 'text' key exists in 'value'
            if item['value'] and 'text' in item['value']:
                return item['value']['text']
    return None  # Return None if the custom field is not found or 'text' key does not exist

def extract_custom_field_text_from_json(json_string, target_custom_field_id):
    """
    Parses a JSON string and extracts the 'text' value from a specific custom field in the JSON data.

    Parameters:
    - json_string (str): The JSON string representing a list of custom field items.
    - target_custom_field_id (str): The ID of the custom field from which to extract the 'text' value.

    Returns:
    - str: The 'text' value of the custom field if available, otherwise None.
    """
    try:
        custom_fields_json = json.loads(json_string)  # Parse JSON string
        for item in custom_fields_json:
            if item['idCustomField'] == target_custom_field_id and 'value' in item and 'text' in item['value']:
                return item['value']['text']
    except json.JSONDecodeError:
        return "Invalid JSON format"
    except KeyError:
        return "Key error in JSON data"
    return None  # Return None if the custom field is not found or 'text' key does not exist
