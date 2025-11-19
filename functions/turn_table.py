from nicegui import app

# local imports
from functions.basics import dict_to_df, df_to_dict
from functions.data import cols_and_labels_to_ui_cols
from functions.saveable_methods import lookup_method


# Compiles database to gather all turn track display info
def turn_track_df():
    mem = app.storage.general
    # We need the following -
    # Start with the basics from character_details: "name","armor_class","initiative","initiative_bonus","team","group"
    turn_track_dataframe = dict_to_df(mem['character_details'])[
        ["name", "armor_class", "initiative", "initiative_bonus", "team", "group"]]
    # Then for each character we grab resources and resource overrides
    #   and will have to merge them into the main dataframe indexed on character name

    # From resources, we just need "health" resource types,
    #   which has "current" and "max" which translate to "health" and "max_health"
    resources_df = dict_to_df(mem['resources'])
    health_df = resources_df[resources_df['name'] == "Current HP"][["character_name", "current", "max"]]
    health_df.rename(columns={"character_name": "name", "current": "health", "max": "max_health"}, inplace=True)
    turn_track_dataframe = turn_track_dataframe.merge(health_df, on="name", how="left")

    # From resource_override, we need "health" and "armor_class" to check "override_type","override_current",
    #   and "override_max" to figure out overrides
    override_df = dict_to_df(mem['resource_override'])
    # Health Overrides
    health_overrides = override_df[override_df['resource_name'] == "Current HP"]
    health_overrides = health_overrides[["character_name", "override_type", "override_current", "override_max"]]
    health_overrides.rename(columns={
        "character_name": "name",
        "override_type": "temporary_health_function",
        "override_current": "temporary_health",
        "override_max": "temporary_health_max"
    }, inplace=True)
    turn_track_dataframe = turn_track_dataframe.merge(health_overrides, on="name", how="left")
    # Armor Class Overrides
    armor_overrides = override_df[override_df['resource_name'] == "armor_class"]
    armor_overrides = armor_overrides[["character_name", "override_type", "override_current"]]
    armor_overrides.rename(columns={
        "character_name": "name",
        "override_type": "ac_mod_function",
        "override_current": "ac_mod"
    }, inplace=True)
    turn_track_dataframe = turn_track_dataframe.merge(armor_overrides, on="name", how="left")

    # Health and Armor Fill ins if no override
    turn_track_dataframe[["temporary_health_function", "ac_mod_function"]] = turn_track_dataframe[
        ["temporary_health_function","ac_mod_function"]].astype(str).fillna("Sum")
    turn_track_dataframe[["temporary_health", "temporary_health_max", "ac_mod"]] = turn_track_dataframe[
        ["temporary_health", "temporary_health_max","ac_mod"]].astype(float).fillna(0).astype(int)

    return turn_track_dataframe

# Setting application
def turn_table_display_filter_df(user_type):
    # get and organize data
    mem = app.storage.general
    full_df = turn_track_df()
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
