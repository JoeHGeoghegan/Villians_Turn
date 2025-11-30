# Imports
import json

import pandas as pd
from nicegui import ui, app
from datetime import datetime

## Local Imports
from functions.basics import split_column_list, df_to_dict

####################################
########## Data Functions ##########
####################################
def cols_and_labels_to_ui_cols(cols, labels):
    return [{'name': col, 'label': label, 'field': col, 'sortable': False} for col, label in zip(cols, labels)]


def df_max_lengths_in_cols(df):
    return {col: df[col].astype(str).str.len().max() for col in df.columns}


def import_file(refresh_target: ui.refreshable, file_path, database_target, import_groups=True):
    mem = app.storage.general
    data = pd.read_csv(file_path)
    if not import_groups and 'group' in data.columns:
        data['group'] = ''
    mem[database_target] = df_to_dict(data)
    refresh_target.refresh()

def export_character_data():
    mem = app.storage.general
    data_list = [
        mem['character_details'],
        mem['conditions'],
        mem['feats'],
        mem['features'],
        mem['inventory'],
        mem['resource_override'],
        mem['resources'],
        mem['skills'],
        mem['weapons']
    ]

    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d_%H:%M:%S")

    json_content = json.dumps(data_list, indent=2)
    ui.download.content(json_content, f'VilliansTurnExport_{formatted_time}.json')

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
                "target": flavor_list[1],
                "modification": flavor_list[2],
                "wording": flavor_list[3]
            }
    return output


def audit_col_str_every_action(df, column_name, drop_cols):
    df_split = df.copy()
    df_split.drop(df_split[df_split[column_name] == ''].index, inplace=True)
    df_split.drop(columns=drop_cols, inplace=True)
    df_split['additional_effects'] = df_split['additional_effects'].str.split('\n')
    df_split = df_split.explode('additional_effects').reset_index(drop=True)
    df_split.drop(df_split[df_split[column_name] == ''].index, inplace=True)
    return df_split


def audit_col_list_every_action(df, column_name, drop_cols):
    df_split = df.explode(column_name)
    df_split.dropna(inplace=True)
    df_split.drop(columns=drop_cols, inplace=True)
    df_split = split_column_list(df_split, column_name, ['sources', 'target'])
    df_split = df_split.explode('sources')
    df_split = split_column_list(df_split, 'sources', ['source', column_name])
    return df_split


def has_flavor(result, flavor_lookup: dict):
    return result in flavor_lookup.keys()
