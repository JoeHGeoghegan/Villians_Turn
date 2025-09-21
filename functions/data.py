# Imports
import io
import pandas as pd
from nicegui import ui, app

#####################################
########## Cross functions ##########
#####################################
from functions.groups import individual_groups
from functions.basics import split_column_list

####################################
########## Data Functions ##########
####################################
def cols_and_labels_to_ui_cols(cols, labels):
    #return [{col: label} for col, label in zip(cols,labels)]
    return [{'name': col, 'label': label, 'field': col, 'sortable': False} for col, label in zip(cols,labels)]

def df_to_ui_rows(df:pd.DataFrame):
    return df.to_dict(orient='records')

def set_mem(target, value):
    app.storage.general[target] = value

def set_user_mem(target, value):
    app.storage.user[target] = value

def import_file(refresh_target:ui.refreshable,file,import_groups=True):
    data = io.BytesIO(file.content.read())
    process_party(refresh_target,pd.read_csv(data),import_groups)

def process_party(refresh_target:ui.refreshable,party,import_groups):
    if not ( import_groups and ('group' in list(party))):
        party = individual_groups(party)
    party[['temporary_health','ac_mod','initiative','initiative_bonus']
          ] = party[['temporary_health','ac_mod','initiative','initiative_bonus']].fillna(0)
    party['health'] = party['health'].fillna(party['max_health'])
    party['team'] = party['team'].fillna(party['name'])
    party['group'] = party['group'].fillna(party['team'])
    add_to_turn_track(party)
    refresh_target.refresh()

def add_to_turn_track(party:pd.DataFrame):
    # memory setup
    mem = app.storage.general
    df = pd.DataFrame(mem['turn_track'])
    mem['turn_track'] = pd.concat([df,party]).to_dict()

def read_audit(path):
    audit_tags = {}
    audit_out = {}
    audit_actions = {}

    with open(path, 'r') as file:
        for data_line in file:
            audit_list = data_line.strip().split(',')
            key = audit_list[0]
            if key == 'Tags':
                audit_tags[audit_list[1]] = audit_list[2:]
            elif key == 'Out':
                audit_out[audit_list[1]] = audit_list[2:]
            else:
                audit_actions[audit_list[1]] = audit_list[2:]

    return audit_actions, audit_out, audit_tags

def read_flavor(path):
    output = {}
    with open(path, 'r', encoding='utf-8-sig') as file:
        for flavor in file:
            flavor_list = flavor.strip().split(',')
            output[flavor_list[0]] = {
                "target" : flavor_list[1],
                "modification" : flavor_list[2],
                "wording" : flavor_list[3]
            }
    return output

def col_str_every_action(df,column_name,drop_cols):
    df_split = df.copy()
    df_split.drop(df_split[df_split[column_name]==''].index,inplace=True)
    df_split.drop(columns=drop_cols,inplace=True)
    df_split['additional_effects'] = df_split['additional_effects'].str.split('\n')
    df_split = df_split.explode('additional_effects').reset_index(drop=True)
    df_split.drop(df_split[df_split[column_name]==''].index,inplace=True)
    return df_split

def col_list_every_action(df,column_name,drop_cols):
    df_split = df.explode(column_name)
    df_split.dropna(inplace=True)
    df_split.drop(columns=drop_cols,inplace=True)
    df_split = split_column_list(df_split,column_name,['sources','target'])
    df_split = df_split.explode('sources')
    df_split = split_column_list(df_split,'sources',['source',column_name])
    return df_split

def has_flavor(result,flavor_lookup:dict):
    return result in flavor_lookup.keys()