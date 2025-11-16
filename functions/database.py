import csv

import pandas as pd
from nicegui import app

from functions.basics import df_to_dict


def schema_to_dict(path):
    with open(path, 'r', newline='') as schema_file:
        schema = csv.DictReader(schema_file)
        data = []
        for row in schema:
            data.append(row)
    return {
        "headers": list(data[0].keys()),
        "labels": data[0],
        "types": data[1],
        "defaults": data[2]
    }


def load_lists_from_csvs():
    mem = app.storage.general

    schemas = mem["schemas"]
    lists = []
    mem["lists"] = {}
    for section in schemas:
        types = schemas[section]["types"]
        for key in types:
            if (types[key] not in ["int", "string", "bool", "character_name", "character_resources", "dice_equation",
                                   None]) and types[key] not in lists:
                lists.append(types[key])
    for item in lists:
        path = f"assets/database_structures/lists/{item}.csv"
        with open(path, 'r', newline='') as file:
            csv_reader = csv.reader(file)
            data = next(csv_reader)
            mem["lists"][item] = data


def resources_file_init(character_name, path):
    resource = pd.read_csv(path)
    resource["character_name"] = character_name
    return df_to_dict(resource)
