# Library Imports
import pandas as pd
from nicegui import app
import json
### Local Imports
from functions.data import read_audit, read_flavor

########## Load Default Table Display Settings ##########
with open('assets\\data\\table_view_dm_default.json', 'r') as f:
    dm_table_settings = json.load(f)
with open('assets\\data\\table_view_player_default.json', 'r') as f:
    player_setting_tables = json.load(f)

audit_headers = ['turn','action_number','action','result','target','target_additional_info','source','source_additional_info','environment','damage','healing','additional_effects']

def init_mem():
    mem = app.storage.general
    user = app.storage.user
    ########## Global Variables ##########
    mem['turn_track'] = pd.DataFrame().to_dict()
    mem['dm_table_settings'] = dm_table_settings
    mem['player_setting_tables'] = player_setting_tables
    mem['current_turn'] = None
    mem['audit'] = pd.DataFrame(columns=audit_headers).to_dict()
    mem['audit_actions'],mem['audit_outcome'],mem['audit_tags'] = read_audit('assets\\data\\default_form_data.txt')
    mem['flavors'] = read_flavor('assets\\data\\default_flavor_data.csv')
    mem['turn_mode'] = "Active"
    mem['turn_number'] = 0
    mem['action_number'] = 0
    mem['results_data'] = []
    mem['audit_combat'] = True
    mem['audit_changes'] = True
    ########## Server Owner Assignment #############
    user['markdown_view_path'] = ''
    user['type'] = "Host"
    user['id'] = 0