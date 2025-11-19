# Imports
import random
import re

import numpy as np
import pandas as pd
from nicegui import app

### Local Imports
from functions.data import audit_col_list_every_action, audit_col_str_every_action
from memory import init_turn


####################################
########## Game Functions ##########
####################################
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
