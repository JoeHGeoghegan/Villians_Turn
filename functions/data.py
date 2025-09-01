# Imports
import pandas as pd

#####################################
########## Cross functions ##########
#####################################
from functions.groups import individual_groups
from functions.basics import split_column_list

####################################
########## Data Functions ##########
####################################
def read_import(path,import_groups=True):
    party = pd.read_csv(path)
    if import_groups and ('group' in list(party)):
        return party
    else:
        party = individual_groups(party)
        return party

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
    with open(path, 'r') as file:
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