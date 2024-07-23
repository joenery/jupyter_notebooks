#!/usr/bin/env python3


import requests

# Function to fetch custom fields
def fetch_custom_fields(api_key, api_token, board_id):
    custom_fields_url = f"https://api.trello.com/1/boards/{board_id}/customFields?key={api_key}&token={api_token}"
    response = requests.get(custom_fields_url)
    custom_fields_data = response.json()
    custom_fields = {}
    for field in custom_fields_data:
        custom_fields[field['id']] = field['name']
    return custom_fields

# Function to fetch checklists
def fetch_checklists(api_key, api_token, board_id):
    checklists_url = f"https://api.trello.com/1/boards/{board_id}/checklists?key={api_key}&token={api_token}"
    response = requests.get(checklists_url)
    checklists_data = response.json()
    checklists = {}
    for checklist in checklists_data:
        checklists[checklist['id']] = checklist['name']
    return checklists

# Print custom fields
def print_custom_fields(api_key, api_token, board_id):
    print("Custom Fields:")
    custom_fields = fetch_custom_fields(api_key, api_token, board_id)
    for field_id, field_name in custom_fields.items():
        print(f"{field_id}: {field_name}")

# Print checklists
def print_checklists(api_key, api_token, board_id):
    print("\nChecklists:")
    checklists = fetch_checklists(api_key, api_token, board_id)
    for checklist_id, checklist_name in checklists.items():
        print(f"{checklist_id}: {checklist_name}")