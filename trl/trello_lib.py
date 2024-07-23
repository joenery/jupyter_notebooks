#!/usr/bin/env python3

import os
import argparse
import requests
import logging

logger = logging.getLogger(__name__)

# Custom field "Archive path" field id
ar_path_custom_field_id = "63ee7a99ec62faeb23cc164c"
api_key = os.environ.get('TKEY')
token = os.environ.get('TTOKEN')
base_url = "https://api.trello.com/1"


def get_request_url(endpoint, **params):
    """
    Constructs a URL for the Trello API request.
    """
    params.update({'key': api_key, 'token': token})
    query = '&'.join(f'{key}={value}' for key, value in params.items())
    return f"{base_url}/{endpoint}?{query}"


def get_list_by_name(board_id, list_name):
    """
    Retrieves a Trello list with the specified name.
    """
    try:
        url = get_request_url(f'boards/{board_id}/lists')
        response = requests.get(url)
        response.raise_for_status()
        lists = response.json()

        for trello_list in lists:
            if trello_list['name'] == list_name:
                return trello_list
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return None


def get_top_card_in_list(list_id):
    """
    Retrieves the top card in a Trello list.
    """
    try:
        url = get_request_url(f'lists/{list_id}/cards')
        response = requests.get(url)
        response.raise_for_status()
        cards = response.json()

        if cards:
            return cards[0]
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return None


def get_card_member_usernames(card_id):
    """
    Retrieve a list of usernames for the members of a Trello card.
    """
    try:
        url = get_request_url(f'cards/{card_id}/members')
        response = requests.get(url)
        response.raise_for_status()
        members = response.json()

        member_usernames = [member['username'] for member in members]
        return member_usernames
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return []


def get_mentions(card_id):
    """
    Retrieve a string of mentions for the members of a Trello card by card ID.
    """
    usernames = get_card_member_usernames(card_id)
    mentions = ' '.join('@' + username for username in usernames)
    return mentions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve information from Trello.")
    parser.add_argument("-b", "--board-id", required=True, help="The ID of the Trello board")
    parser.add_argument("-l", "--list-name", required=True, help="The name of the Trello list")
    args = parser.parse_args()

    board_id = args.board_id
    list_name = args.list_name

    list_obj = get_list_by_name(board_id, list_name)
    if list_obj:
        print(f"List found: {list_obj['name']} (ID: {list_obj['id']})")
        top_card_obj = get_top_card_in_list(list_obj['id'])
        if top_card_obj:
            print(f"Top card: {top_card_obj['name']} (ID: {top_card_obj['id']})")
            mentions = get_mentions(top_card_obj['id'])
            print(f"Mentions: {mentions}")
        else:
            print("No cards found in the list.")
    else:
        print("List not found.")
