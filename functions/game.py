# Imports
import random
import re

import numpy as np
import pandas as pd
from nicegui import app

from functions.basics import dict_to_df, df_to_dict
### Local Imports
from functions.data import audit_col_list_every_action, audit_col_str_every_action, cols_and_labels_to_ui_cols
from functions.saveable_methods import lookup_method
from memory import init_turn


####################################
########## Game Functions ##########
####################################
# Compiles database to gather all turn track display info
def turn_track():
    mem = app.storage.general
    # We need the following -
    # Start with the basics from character_details: "name","armor_class","initiative","initiative_bonus","team","group"
    turn_track_df = dict_to_df(mem['character_details'])[
        ["name", "armor_class", "initiative", "initiative_bonus", "team", "group"]]
    # Then for each character we grab resources and resource overrides
    #   and will have to merge them into the main dataframe indexed on character name

    # From resources, we just need "health" resource types,
    #   which has "current" and "max" which translate to "health" and "max_health"
    health_df = dict_to_df(mem['resources'])
    health_df = health_df[health_df['resource_type'] == "health"][["character_name", "current", "max"]]
    health_df.rename(columns={"character_name": "name", "current": "health", "max": "max_health"}, inplace=True)
    turn_track_df = turn_track_df.merge(health_df, on="name", how="left")

    # From resource_override, we need "health" and "armor_class" to check "override_type","override_current",
    #   and "override_max" to figure out overrides
    override_df = dict_to_df(mem['resource_override'])
    # Health Overrides
    health_overrides = override_df[override_df['resource_name'] == "health"]
    health_overrides = health_overrides[["character_name", "override_type", "override_current", "override_max"]]
    health_overrides.rename(columns={
        "character_name": "name",
        "override_type": "temporary_health_function",
        "override_current": "temporary_health",
        "override_max": "temporary_health_max"
    }, inplace=True)
    turn_track_df = turn_track_df.merge(health_overrides, on="name", how="left")
    # Armor Class Overrides
    armor_overrides = override_df[override_df['resource_name'] == "armor_class"]
    armor_overrides = armor_overrides[["character_name", "override_type", "override_current"]]
    armor_overrides.rename(columns={
        "character_name": "name",
        "override_type": "ac_mod_function",
        "override_current": "ac_mod"
    }, inplace=True)
    turn_track_df = turn_track_df.merge(armor_overrides, on="name", how="left")

    return turn_track_df


# Setting application
def turn_table_display(user_type):
    # get and organize data
    mem = app.storage.general
    full_df = turn_track()
    settings = mem['dm_table_settings'].copy() if user_type == "Host" else mem['player_setting_tables'].copy()
    specials = settings['special'].copy()
    del settings['special']

    # Get columns to display and the correct labels
    display_cols = [col for col in settings.keys() if settings[col]['enabled']]  # columns to display
    labels = [settings[col]["label"] for col in display_cols]  # get labels for display columns

    # establish output
    display_df = full_df.copy().astype(object)

    # Handle Default Display Overrides
    for col in settings.keys():
        if 'override' in settings[col].keys() and settings[col]['enabled']:
            method, arg_columns = lookup_method(settings[col]['override'])
            override_col = method(full_df[arg_columns])
            display_df[col] = override_col
    # Handle hiding values and special views for non Host view
    if user_type == "Host":
        for special_handle in specials:
            if 'team' in special_handle.keys():
                if 'hidden_cols' in special_handle.keys():
                    for hidden_col in special_handle['hidden_cols']:
                        if hidden_col in display_cols:  # Corner case check...
                            display_df.loc[display_df['team'] == special_handle[
                                'team'], hidden_col] = 'Hidden'  # Hide values for specific teams
                if 'override' in special_handle.keys():
                    for override_col_name in special_handle['override'].keys():
                        if override_col_name in display_cols:
                            method, arg_columns = lookup_method(special_handle['override'][override_col_name])
                            override_col_values = method(full_df[arg_columns])
                            impact_zone = display_df['team'] == special_handle['team']
                            display_df.loc[impact_zone, override_col_name] = override_col_values[impact_zone]

    # Filter down and adjust columns
    display_df = display_df[display_cols]  # Filter Columns to just enabled ones

    # Format Return
    rows = df_to_dict(display_df)
    cols = cols_and_labels_to_ui_cols(display_cols, labels)
    return cols, rows, display_df


def roll_dice(equation, show_details=False, show_range=False):
    """
    Roll dice based on a die equation string.

    Args:
        equation: String like "3d6+d8+5" (supports +, -, *, /, parentheses)
        show_details: If True, returns dict with individual roll details
        show_range: If True, includes min/max possible values in dict

    Returns:
        Integer result, or dict with details if show_details=True
    """
    equation = equation.replace(" ", "").lower()

    # Convert implicit multiplication: 2(d6) -> 2*(d6)
    equation = re.sub(r'(\d+|\))(\()', r'\1*\2', equation)
    original = equation

    rolls_log = []

    def roll_dice_term(match):
        """Roll a die term and return the sum."""
        term = match.group()
        parts = term.split('d')
        num = int(parts[0]) if parts[0] else 1
        sides = int(parts[1])

        results = [random.randint(1, sides) for _ in range(num)]
        if show_details:
            rolls_log.append((term, results))
        return str(sum(results))

    # Replace all dice terms with their rolled values
    equation = re.sub(r'\d*d\d+', roll_dice_term, equation)

    # Evaluate the resulting mathematical expression
    result = int(eval(equation))

    if not show_details:
        return result

    # Build details dictionary
    details = {
        'result': result,
        'rolls': rolls_log,
        'equation': original
    }

    if show_range:
        # Calculate min/max by replacing dice with their bounds
        def get_bounds(match):
            term = match.group()
            parts = term.split('d')
            num = int(parts[0]) if parts[0] else 1
            sides = int(parts[1])
            return f'({num},{num * sides})'  # (min, max)

        # Create expression with bounds tuples
        min_expr = re.sub(r'\d*d\d+', lambda m: get_bounds(m).split(',')[0][1:], original.lower())
        max_expr = re.sub(r'\d*d\d+', lambda m: get_bounds(m).split(',')[1][:-1], original.lower())

        min_eval = eval(min_expr)
        max_eval = eval(max_expr)

        details['min'] = int(min_eval)
        details['max'] = int(max_eval)

    return details


def peak_turn(df: pd.DataFrame, current_turn, direction):
    # df.reset_index(drop=True,inplace=True)
    groups = df["group"].unique()
    current_group_index_search = np.where(groups == current_turn)
    current_group_index = current_group_index_search[0][0]
    if current_group_index + direction >= len(groups):
        return groups[direction - 1]
    return groups[current_group_index + direction]


def set_turn(df: pd.DataFrame, current_turn, direction, mode):
    init_turn()
    if mode == "active":
        app.storage.general['turn_number'] += direction
    app.storage.general['current_turn'] = peak_turn(df, current_turn, direction)


def add_audit(audit_trail: pd.DataFrame, turn, action_number, action, result, target, target_additional_info, source,
              source_additional_info, environment, damage, healing, additional_effects):
    audit_trail.loc[len(audit_trail.index)] = [
        turn, action_number,
        action,
        result,
        target,
        target_additional_info,
        source,
        source_additional_info,
        environment,
        damage,
        healing,
        additional_effects
    ]


def add_audit_note(audit_trail: pd.DataFrame, turn, action_number, note):
    add_audit(audit_trail, turn, action_number, "", "", "", "", "", "", "", "", "", note)


def add_audit_character_note(audit_trail: pd.DataFrame, turn, action_number, character, note):
    add_audit(audit_trail, turn, action_number, character, "", "", "", "", "", "", "", "", note)


def audit_every_action_df(audit: pd.DataFrame):
    action_df = audit.copy()[["turn", "action_number", "damage", "healing", "additional_effects"]]
    concat_list = []
    if not all(action_df['damage'].isin(["", []])): concat_list.append(
        audit_col_list_every_action(action_df, 'damage', ['healing', 'additional_effects']))
    if not all(action_df['healing'].isin(["", []])): concat_list.append(
        audit_col_list_every_action(action_df, 'healing', ['damage', 'additional_effects']))
    if not all(action_df['additional_effects'].isin(["", []])): concat_list.append(
        audit_col_str_every_action(action_df, 'additional_effects', ['damage', 'healing']))

    if len(concat_list): return pd.concat(concat_list, ignore_index=True).sort_values(by=["turn", "action_number"])
    return pd.DataFrame(columns=['turn', 'action_number', 'source', 'damage', 'healing', 'additional_effects'])
