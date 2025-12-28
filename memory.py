import json
import pandas as pd
from nicegui import app

from functions.basics import df_to_dict
from functions.data import read_audit, read_flavor
from functions.database import schema_to_dict, load_lists_from_csvs

########## Load Default Table Display Settings ##########
with open('assets/data/table_view_dm_default.json', 'r') as f:
    dm_table_settings = json.load(f)
with open('assets/data/table_view_player_default.json', 'r') as f:
    player_setting_tables = json.load(f)

audit_headers = ['turn', 'action_number', 'action', 'result', 'target', 'target_additional_info', 'source',
                 'source_additional_info', 'environment', 'damage', 'healing', 'additional_effects']


def init_mem():
    mem = app.storage.general
    mem.clear()
    ########## Global Variables ##########
    # Settings
    mem['dm_table_settings'] = dm_table_settings
    mem['player_setting_tables'] = player_setting_tables
    mem['audit'] = df_to_dict(pd.DataFrame(columns=audit_headers))
    mem['audit_actions'], mem['audit_outcome'], mem['audit_tags'] = read_audit('assets/data/default_form_data.txt')
    mem['flavors'] = read_flavor('assets/data/default_flavor_data.csv')
    # Control Flags
    mem['audit_combat'] = True
    mem['audit_changes'] = True

    # Database Loading
    mem['schemas'] = {
        "character_details": schema_to_dict("assets/database_structures/table_schemas/character_details_fields.csv"),
        "conditions": schema_to_dict("assets/database_structures/table_schemas/conditions_fields.csv"),
        "feats": schema_to_dict("assets/database_structures/table_schemas/feats_fields.csv"),
        "features": schema_to_dict("assets/database_structures/table_schemas/features_fields.csv"),
        "inventory": schema_to_dict("assets/database_structures/table_schemas/inventory_fields.csv"),
        "resource_override": schema_to_dict("assets/database_structures/table_schemas/resource_override_fields.csv"),
        "resources": schema_to_dict("assets/database_structures/table_schemas/resources_fields.csv"),
        "skills": schema_to_dict("assets/database_structures/table_schemas/skills_fields.csv"),
        "weapons": schema_to_dict("assets/database_structures/table_schemas/weapons_fields.csv")
    }
    load_lists_from_csvs()

    ########## Other Memory Assignment #############
    init_database()
    init_table()
    init_turn()
    user = app.storage.user
    user['selectable_view'] = []
    user['character_focus'] = ''
    user['type'] = "Host"
    user['id'] = 0
    mem['clients'] = [f"{user['type']} {user['id']}"]


def init_database():
    mem = app.storage.general

    for section in mem['schemas']:
        headers = mem['schemas'][section]['headers']
        mem[section] = mem[section] = [{header: None for header in headers}]


def init_table():
    mem = app.storage.general

    mem['current_turn'] = None
    mem['turn_mode'] = "setup"
    mem['table_mode'] = "info"
    mem['turn_number'] = 0
    mem['action_number'] = 0


def init_user():
    mem = app.storage.general
    user = app.storage.user
    user['selectable_view'] = []
    user['type'] = "Player"
    user['character_focus'] = ''

    temp_list = list(mem['clients'])
    user['id'] = len(temp_list)

    temp_list.append(f"{user['type']} {user['id']}")
    mem['clients'] = temp_list


def init_turn():
    app.storage.general['turn_data'] = {
        "actor": [],
        "actor_override": [],
        "target": [],
        'results_data': [],
    }


def set_mem(target, value):
    app.storage.general[target] = value


def set_user_mem(target, value):
    app.storage.user[target] = value


def set_user_type(role):
    set_user_mem("type", role)
