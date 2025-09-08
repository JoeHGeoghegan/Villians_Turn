# Library Imports
import pandas as pd
from nicegui import ui, app
import json
### Local Imports
from functions.data import read_audit, read_flavor

########## Load Default Table Display Settings ##########
with open('assets\\data\\default_header_settings.json', 'r') as f:
    initial_header_settings = json.load(f)

audit_headers = ["turn","action_number","action","result","target","target_additional_info","source","source_additional_info","environment","damage","healing","additional_effects"]

def init_mem():
    mem = app.storage.tab
    ########## Global Variables ##########
    mem["turn_track"] = pd.DataFrame()
    mem["turn_track_settings"] = initial_header_settings
    mem["current_turn"] = None
    mem["audit"] = pd.DataFrame(columns=audit_headers)
    mem["audit_actions"],mem["audit_outcome"],mem["audit_tags"] = read_audit("assets\\data\\default_form_data.txt")
    mem["flavors"] = read_flavor("assets\\data\\default_flavor_data.csv")
    mem["turn_number"] = 0
    mem["action_number"] = 0
    mem["results_data"] = []
    mem["audit_combat"] = True
    mem["audit_changes"] = True
    mem['markdown_view_path'] = ''