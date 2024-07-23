#!/usr/bin/env python3

import os
import argparse
from trello import TrelloClient
import logging

logger = logging.getLogger(__name__)

#Custom field "Archive path" field id
ar_path_custom_field_id="63ee7a99ec62faeb23cc164c"

def get_client():
    """
    Retrieves API key and token from environment variables
    and returns a Trello client instance.

    Returns:
        TrelloClient: An instance of TrelloClient if successful, None otherwise.
    """
    api_key = os.environ.get('TKEY')
    token = os.environ.get('TTOKEN')

    try:
        client = TrelloClient(api_key=api_key, token=token)
    except KeyError as e:
        logger.error(f"Missing environment variable: {str(e)}")
        return None
    except trello.exceptions.ResourceUnavailable as e:
        logger.error(f"Trello API is unavailable: {str(e)}")
        return None

    return client

def get_list_by_name(list_name):
    """
    Retrieves a Trello list with the specified name.

    Args:
        list_name (str): The name of the Trello list.

    Returns:
        List: The Trello list if found, None otherwise.
    """
    try:
        client = get_client()
        board_id = os.environ.get('TBOARDID')

        if client is None:
            return None

        board = client.get_board(board_id)
        lists = board.list_lists()

        for trello_list in lists:
            if trello_list.name == list_name:
                return trello_list

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

    return None

def get_top_card_in_list(trello_list):
    """
    Retrieves the top card in a Trello list.

    Args:
        trello_list (List): The Trello list.

    Returns:
        Card: The top card if available, None otherwise.
    """
    try:
        cards = trello_list.list_cards()

        if cards:
            return cards[0]
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

    return None


def get_custom_field_value(card, custom_field_name):
    """
    Retrieve the value of a custom field for a given card.

    Args:
        card (trello.Card): The Trello card object.
        custom_field_name (str): The name of the custom field.

    Returns:
        str: The value of the custom field.
    """
    try:
        custom_field = card.get_custom_field_by_name(custom_field_name)
        if custom_field:
            return custom_field.value

        logger.info(f"Custom field '{custom_field_name}' not found for the card.")
        return None

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return None


def get_card_member_usernames(card):
    """
    Retrieve a list of usernames for the members of a Trello card.

    Args:
        card (Card): Trello card object.

    Returns:
        list: A list of member usernames associated with the card.
    """
    try:
        client = get_client()
        if client is None:
            return []

        member_usernames = []
        for member_id in card.member_id:
            member = client.get_member(member_id)
            member_usernames.append(member.username)

        return member_usernames

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return []


def get_card_member_usernames_by_card_id(card_id):
    """
    Retrieve a list of usernames for the members of a Trello card given the card ID.

    Args:
        card_id (str): The ID of the Trello card.

    Returns:
        list: A list of member usernames associated with the card.
    """
    try:
        client = get_client()
        if client is None:
            return []

        card = client.get_card(card_id)
        if card is None:
            logger.error(f"Card with ID '{card_id}' not found.")
            return []

        member_usernames = []
        for member_id in card.member_id:
            member = client.get_member(member_id)
            member_usernames.append(member.username)

        return member_usernames

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return []


def get_mention_usernames(member_usernames):
    """
    Append "@" to the begining of each username in a list

    Args:
        member_usernames: a list of card member username strings

    Returns:
        A string with "@" appended to the beginning of each member username
    """

    mentions = ' '.join('@' + username for username in member_usernames)
    return mentions


def get_mentions(card_id):
    """
    Retrieve a string of mentions for the members of a Trello card by card ID.

    Args:
        card_id (str): The ID of the Trello card.

    Returns:
        str: A string with "@" appended to the beginning of each member username.
    """
    usernames = get_card_member_usernames_by_card_id(card_id)
    mentions = get_mention_usernames(usernames)
    return mentions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve information from Trello.")
    parser.add_argument("-l", "--list-name", help="The name of the Trello list")
    parser.add_argument("-f", "--custom-field-name", help="The name of the Trello card")
    args = parser.parse_args()

    list_name = args.list_name
    custom_field_name = args.custom_field_name

    list_obj = get_list_by_name(list_name)
    list_obj_name = list_obj.name
    list_obj_id = list_obj.id
    top_card_obj = get_top_card_in_list(list_obj)
    top_card_name = top_card_obj.name
    top_card_id = top_card_obj.id
    print(top_card_name)
    print(top_card_id)

    #print(get_custom_field_value(top_card_obj, "Archive Path"))

    usernames = get_card_member_usernames(top_card_obj)
    #print(usernames)

    #print(get_username_mentions(usernames))

    mentions = get_mentions(top_card_id)

    print(mentions)
