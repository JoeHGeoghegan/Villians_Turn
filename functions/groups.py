# Imports
import numpy as np
import pandas as pd
from nicegui import app

from functions.basics import dict_to_df
from functions.game import roll_dice


### Local Imports

#####################################
########## Group Functions ##########
#####################################
## Info
def groups_list(characters: pd.DataFrame):
    return characters['group'].unique().tolist()


def person_is_alone(characters: pd.DataFrame, person):
    group_name = characters[characters['name'] == person]['group'].values[0]
    return len(characters[characters['group'] == group_name]) == 1


def groups_gathered_check(characters: pd.DataFrame):
    order_list = groups_list(characters)
    team_changes = characters["group"].shift() != characters["group"]
    return len(team_changes[team_changes == True]) == len(order_list)


def multi_person_groups_list(characters):
    multi_person_groups_mask = [len(characters[characters['group'] == x]) != 1 for x in characters['group'].unique()]
    multi_person_groups = characters['group'].unique()[multi_person_groups_mask]
    return multi_person_groups


def player_characters_groups():
    #TODO Create Character->Player table, use user["id"] to filter down to Player Characters and
    # their groups (list of dicts {character,group})
    # THIS IS NOT A PRIORITY DON'T WORK ON THIS DUDE!!!
    return groups_list(dict_to_df(app.storage.general["character_details"]))


# Full table modifications
def remove_group_assignments(characters: pd.DataFrame):
    df = characters.copy()
    df['group'] = np.nan
    return df


def individual_groups(characters: pd.DataFrame):
    df = characters.copy()
    df['group'] = df['name']
    return df


def initiative_based_group_assignment(characters: pd.DataFrame):
    df = sort_by_initiatives(characters)
    df_count = {}
    team_order = df['team']
    group_placement = []
    last_team = None
    for team in team_order:
        if team != last_team:
            if team in df_count.keys():
                df_count[team] += 1
            else:
                df_count[team] = 1
            last_team = team
        group_placement.append(f"{team} {df_count[team]}")
    df['group'] = group_placement
    return df


def auto_initiative_groups(characters: pd.DataFrame):
    df = auto_initiative(characters)
    df = initiative_based_group_assignment(df)
    df = sort_by_initiatives(df)
    return df


def group_in_place(characters: pd.DataFrame):
    df = characters.copy()
    for group_name in df['group'].unique():
        group_mask = df['group'] == group_name

        # If there is only one subgroup of this grouping, we can skip the below logic
        if ((df['group'].shift(1) != df['group']) & group_mask).sum() == 1:
            continue

        # Renames all subgroups to unique values by appending a number to the end
        index = 0
        subgroup_number = 1
        matching_group = False
        for mask in group_mask:
            if mask:
                df.loc[index, 'group'] = f"{group_name} {subgroup_number}"
                matching_group = True
            else:
                if matching_group:
                    subgroup_number += 1
                    matching_group = False
            index += 1
    return df


# Sub table modifications
def breakup_group(characters: pd.DataFrame, group):
    df = characters.copy()
    df.loc[(df["group"] == group, "group")] = df['name']
    return df


def rename_group(characters: pd.DataFrame, group, new_name):
    df = characters.copy()
    df.loc[(df["group"] == group, "group")] = new_name
    return df


def move_group(characters: pd.DataFrame, group_to_move, before_or_after, group_to_place):
    df = characters.copy()
    df.reset_index(drop=True, inplace=True)
    slice_group_to_move = df[df['group'] == group_to_move].copy()
    df.drop(slice_group_to_move.index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    slice_group_to_move.reset_index(drop=True, inplace=True)
    if before_or_after == "Before":
        index_split_point = (df[df['group'] == group_to_place].index[0])  # first index
    else:
        index_split_point = df[df['group'] == group_to_place].index[-1] + 1  # last index
    return pd.concat([df.iloc[:index_split_point], slice_group_to_move, df.iloc[index_split_point:]]).reset_index(
        drop=True)


def move_character(characters: pd.DataFrame, person_to_move, destination_group):
    df = characters.copy()
    df.reset_index(drop=True, inplace=True)
    slice_character_to_move = df[df['name'] == person_to_move].copy()
    slice_character_to_move['group'] = destination_group
    df.drop(slice_character_to_move.index, inplace=True)
    index_split_point = df[df['group'] == destination_group].index[-1]  # last index
    return pd.concat([df.iloc[:index_split_point], slice_character_to_move, df.iloc[index_split_point:]]).reset_index(
        drop=True)


def move_character_to_new_group(characters: pd.DataFrame, person_to_move, new_group_name):
    df = characters.copy()
    old_group = df.loc[(df["name"] == person_to_move, "group")].values[0]#TODO Flagged by IDE, should retest
    df.loc[(df["name"] == person_to_move, "group")] = new_group_name
    if df[df['group'] == old_group].empty:
        return df  # If character was the only member of a group, no need to rearrange
    return move_group(df, new_group_name, "After", old_group)


def merge_groups(characters: pd.DataFrame, merge_group_1, merge_group_2, merged_name):
    df = characters.copy()
    df = move_group(df, merge_group_1, "After", merge_group_2)
    df['group'].replace([merge_group_1, merge_group_2], [merged_name, merged_name], inplace=True)
    return df


def sort_by_initiatives(characters: pd.DataFrame):
    df = characters.copy()
    df['total_initiative'] = df['initiative'] + df['initiative_bonus']
    df.sort_values(by='total_initiative', ascending=False, inplace=True)
    return df.drop(columns="total_initiative")


def auto_initiative(characters: pd.DataFrame):
    df = characters.copy()
    df['initiative'] = df['initiative'].apply(lambda x: roll_dice("d20"))
    return df
