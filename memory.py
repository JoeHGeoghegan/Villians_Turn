# Library Imports
import pandas as pd
### Local Imports
from functions.data import read_audit, read_flavor

########## Headers/Setup/"Constants" (may change) ##########
track_headers = ["name","health","armor_class","initiative","initiative_bonus","team","group","attributes"]
audit_headers = ["turn","action_number","action","result","target","target_additional_info","source","source_additional_info","environment","damage","healing","additional_effects"]

########## Global Variables ##########
turn_track = pd.DataFrame()
turn_track = pd.DataFrame(columns=track_headers)
current_turn = None
audit = pd.DataFrame(columns=audit_headers)
audit_actions,audit_outcome, audit_tags = read_audit("assets\data\default_form_data.txt")
flavor_lookup = read_flavor("assets\data\default_flavor_data.csv")
turn_number = 0
action_number = 0
results_data = []
audit_combat = True
audit_changes = True