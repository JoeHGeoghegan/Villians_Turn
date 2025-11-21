# Imports
import copy

from nicegui import app

from functions.basics import df_match_slice
from functions.basics import dict_to_df, df_to_dict
from functions.database import resources_file_init


#########################################
########## Character Functions ##########
#########################################
def character_list():
    characters = dict_to_df(app.storage.general['character_details'])
    if characters is None:
        print("No characters found.")
        return []
    else:
        print(f"Character List: {characters['name'].unique().tolist()}")
        return characters["name"].unique().tolist()


def team_list():
    characters = dict_to_df(app.storage.general['character_details']).dropna(inplace=True)
    if characters is None:
        return []
    else:
        return characters["team"].unique().tolist()


def new_character():
    mem = app.storage.general
    details = copy.deepcopy(mem["schemas"]["character_details"]["defaults"])
    character_name = "New Character"
    skills = resources_file_init(character_name, "assets/database_structures/resources/new_character_skills.csv")
    resources = resources_file_init(character_name,
                                    "assets/database_structures/resources/new_character_default_resources.csv")
    weapons = copy.deepcopy(mem["schemas"]["weapons"]["defaults"])
    feats = copy.deepcopy(mem["schemas"]["feats"]["defaults"])
    features = copy.deepcopy(mem["schemas"]["features"]["defaults"])
    conditions = copy.deepcopy(mem["schemas"]["conditions"]["defaults"])
    inventory = copy.deepcopy(mem["schemas"]["inventory"]["defaults"])
    resource_override = copy.deepcopy(mem["schemas"]["resource_override"]["defaults"])

    # Clear sections
    for section in [feats, features, conditions, inventory, resource_override]:
        for key in section:
            section[key] = None

    # Link resources to character
    weapons["character_name"] = character_name

    character = {
        "character_details": details,
        "weapons": [weapons],
        "resources": resources,
        "skills": skills,
        "feats": [feats],
        "features": [features],
        "conditions": [conditions],
        "inventory": [inventory],
        "resource_override": [resource_override]
    }

    # character_save(character)

    return character


def character_search(character_name):
    mem = app.storage.general
    if character_name == "New Character":
        return new_character()
    return {
        "character_details": df_to_dict(df_match_slice(dict_to_df(mem["character_details"]), "name", character_name))[
            0],
        "weapons": df_to_dict(df_match_slice(dict_to_df(mem["weapons"]), "character_name", character_name)),
        "resources": df_to_dict(df_match_slice(dict_to_df(mem["resources"]), "character_name", character_name)),
        "skills": df_to_dict(df_match_slice(dict_to_df(mem["skills"]), "character_name", character_name)),
        "feats": df_to_dict(df_match_slice(dict_to_df(mem["feats"]), "character_name", character_name)),
        "features": df_to_dict(df_match_slice(dict_to_df(mem["features"]), "character_name", character_name)),
        "conditions": df_to_dict(df_match_slice(dict_to_df(mem["conditions"]), "character_name", character_name)),
        "inventory": df_to_dict(df_match_slice(dict_to_df(mem["inventory"]), "character_name", character_name)),
        "resource_override": df_to_dict(
            df_match_slice(dict_to_df(mem["resource_override"]), "character_name", character_name))
    }
