# Library Imports
import pandas as pd
from nicegui import ui, app
from pandas import Series

from functions.basics import dict_to_df, df_to_dict
### Local Imports
from functions.characters import character_list, new_character, character_search, new_weapon, new_resource, new_feat, \
    new_feature, new_condition, new_inventory, new_resource_override
from functions.database import resources_file_init
from functions.table_control import game_list

# Page Temp Memory
selected_character: dict = {}
containing_page: ui.refreshable = None


def create_content(page: ui.refreshable):
    # memory setup
    global selected_character
    global containing_page
    mem = app.storage.general

    if containing_page is None:
        containing_page = page

    with ui.column():
        # Character Select Init
        all_characters = character_list()
        if len(all_characters) == 0 or all_characters == ["New Character"]:
            selected_character = new_character()
        elif not selected_character:  # No character selected yet
            selected_character = character_search(mem["character_details"][0]["name"])
        # Character Select UI
        character_selector = ui.select(all_characters + ["New Character"],
                                       value=selected_character["character_details"]["name"],
                                       on_change=lambda character_name: select_character(character_name.value))
        # Disable if no other character
        if len(all_characters) == 0 or all_characters == ["New Character"]:
            print('Selector Disabled')
            character_selector.disable()
        else:  # Normal selector
            print('Selector Enabled')
            character_selector.enable()

        # Character Details
        ui.markdown('###Character Editor')
        with ui.row():
            ui.button("Print Character Details Mem",
                      on_click=lambda: print(mem['character_details']))  # TODO Temporary Debug Button
        with ui.card():
            with ui.card_section():
                with ui.row():
                    entry_fields("character_details",
                                 mem["schemas"]["character_details"]["headers"])
                with ui.tabs().classes('w-full') as tabs:
                    attacking = ui.tab('Weapons')
                    resources = ui.tab('Resources')
                    feats = ui.tab('Feats')
                    features = ui.tab('Features')
                    conditions = ui.tab('Conditions')
                    inventory = ui.tab('Inventory')
                    resource_override = ui.tab('Resource Overrides')
                with ui.tab_panels(tabs, value=attacking).classes('w-full'):
                    with ui.tab_panel(attacking):
                        if len(selected_character["weapons"]) > 0:
                            for index, weapon in enumerate(selected_character["weapons"]):
                                with ui.card():
                                    with ui.card_section():
                                        with ui.row():
                                            entry_fields("weapons",
                                                         mem["schemas"]["weapons"]["headers"],
                                                         index=index)
                        ui.button("Add Weapon", on_click=lambda: new_weapon())
                    with ui.tab_panel(resources):
                        if len(selected_character["resources"]) > 0:
                            for index, weapon in enumerate(selected_character["resources"]):
                                with ui.card():
                                    with ui.card_section():
                                        with ui.row():
                                            entry_fields("resources",
                                                         mem["schemas"]["resources"]["headers"],
                                                         index=index)
                        with ui.row():
                            ui.button("Add Resource", on_click=lambda: new_resource())
                            ui.button("Add Spell Resources",
                                      on_click=lambda: (add_to_section("resources", resources_file_init(
                                          selected_character["character_details"]["name"],
                                          "assets/database_structures/resources/addable_spell_resources_defaults.csv")),
                                                        page.refresh()
                                                        ))
                    with ui.tab_panel(feats):
                        if len(selected_character["feats"]) > 0:
                            for index, weapon in enumerate(selected_character["feats"]):
                                with ui.card():
                                    with ui.card_section():
                                        with ui.row():
                                            entry_fields("feats",
                                                         mem["schemas"]["feats"]["headers"],
                                                         index=index)
                        ui.button("Add Feat", on_click=lambda: new_feat())
                    with ui.tab_panel(features):
                        if len(selected_character["features"]) > 0:
                            for index, weapon in enumerate(selected_character["features"]):
                                with ui.card():
                                    with ui.card_section():
                                        with ui.row():
                                            entry_fields("features",
                                                         mem["schemas"]["features"]["headers"],
                                                         index=index)
                        ui.button("Add Feature", on_click=lambda: new_feature())
                    with ui.tab_panel(conditions):
                        if len(selected_character["conditions"]) > 0:
                            for index, weapon in enumerate(selected_character["conditions"]):
                                with ui.card():
                                    with ui.card_section():
                                        with ui.row():
                                            entry_fields("conditions",
                                                         mem["schemas"]["conditions"]["headers"],
                                                         index=index)
                        ui.button("Add Condition", on_click=lambda: new_condition())
                    with ui.tab_panel(inventory):
                        if len(selected_character["inventory"]) > 0:
                            for index, weapon in enumerate(selected_character["inventory"]):
                                with ui.card():
                                    with ui.card_section():
                                        with ui.row():
                                            entry_fields("inventory",
                                                         mem["schemas"]["inventory"]["headers"],
                                                         index=index)
                        ui.button("Add Inventory", on_click=lambda: new_inventory())
                    with ui.tab_panel(resource_override):
                        if len(selected_character["resource_override"]) > 0:
                            for index, weapon in enumerate(selected_character["resource_override"]):
                                with ui.card():
                                    with ui.card_section():
                                        with ui.row():
                                            entry_fields("resource_override",
                                                         mem["schemas"]["resource_override"]["headers"],
                                                         index=index)
                        ui.button("Add Resource Override", on_click=lambda: new_resource_override())
        ui.button("Save", on_click=lambda: (character_save(selected_character), page.refresh()))
    with ui.column():
        if all(cell is None for cell in mem['character_details'][0].values()):
            ui.label("No other characters exist")
        else:
            game_list("Host", highlight_rows=False, page=page)


def character_save(character):
    print(f"Saving data for {character["character_details"]["name"]}")
    print(f"Current Characters: {character_list()}")
    mem = app.storage.general

    # renamed character catch
    if "original_name" in character["character_details"]:
        rename_character(character["character_details"]["name"])
        character_name = character["character_details"]["original_name"]
        del character["character_details"]["original_name"]
    else:
        character_name = character["character_details"]["name"]

    for section in character:
        current_section_memory_df = dict_to_df(mem[section])
        # remove old character data and any empty placeholder rows
        if section == "character_details":
            unmodified_section_memory_df = current_section_memory_df[
                (current_section_memory_df["name"] != character_name) & (current_section_memory_df["name"].notna())]
        else:
            unmodified_section_memory_df = current_section_memory_df[
                (current_section_memory_df["character_name"] != character_name) & (
                    current_section_memory_df["character_name"].notna())]

        # Isolate new section data and convert to df
        new_data_character_section = character[section]
        new_data_character_section_df = dict_to_df(new_data_character_section)

        # Merge and save back to memory
        if unmodified_section_memory_df.empty:
            mem[section] = df_to_dict(new_data_character_section_df)
        else:
            updated_data = pd.concat([unmodified_section_memory_df, new_data_character_section_df], ignore_index=True)
            mem[section] = df_to_dict(updated_data)
    print(f"Existing Characters: {character_list()}")


def rename_character(new_name):
    global selected_character
    # first rename catch
    if "original_name" not in selected_character["character_details"]:
        selected_character["character_details"]["original_name"] = selected_character["character_details"]["name"]
    # rename in all sections
    selected_character["character_details"]["name"] = new_name
    for section in selected_character.keys():
        if section != "character_details":
            index = 0
            for _ in selected_character[section]:
                selected_character[section][index]["character_name"] = new_name
                index += 1


def select_character(character_name):
    global selected_character, containing_page
    selected_character = character_search(character_name)
    containing_page.refresh()


def set_character_data(section, index, key, new_value):
    global selected_character
    selected_character[section][index][key] = new_value


def add_to_section(section, new_item):
    global selected_character
    if type(new_item) == dict:
        selected_character[section].append(new_item)
    elif type(new_item) == list:
        selected_character[section].extend(new_item)


def set_character_detail(key, new_value):
    global selected_character
    selected_character["character_details"][key] = new_value


def entry_fields(database_section, header_list, index=0):
    global selected_character
    mem = app.storage.general
    head_table = True if database_section == "character_details" else False
    for header in header_list:
        label = mem["schemas"][database_section]["labels"][header]  # only need the specific label and type
        entry_type = mem["schemas"][database_section]["types"][header]
        if head_table:
            data_value = selected_character[database_section][header]
        else:
            data_value = selected_character[database_section][index][header]
        # clean data_value
        if type(data_value) == Series:
            data_value = data_value.iloc[0]
        if entry_type == "character_name" and head_table:
            ui.input(label=label, value=data_value, on_change=lambda e: rename_character(e.value))
        elif entry_type == "character_name" and not head_table:
            pass
        elif entry_type == "int":
            if head_table:
                ui.number(label=label, value=data_value, on_change=lambda e, h=header:
                set_character_detail(h, e.value))
            else:
                ui.number(label=label, value=data_value, on_change=lambda e, h=header:
                set_character_data(database_section, index, h, e.value))
        elif entry_type == "string":
            if head_table:
                ui.input(label=label, value=data_value, on_change=lambda e, h=header:
                set_character_detail(h, e.value))
            else:
                ui.input(label=label, value=data_value, on_change=lambda e, h=header:
                set_character_data(database_section, index, h, e.value))
        elif entry_type == "dice_equation":  # Same as String but with validation. #TODO add validation (Try/Except on dice roll?)
            if head_table:
                ui.input(label=label, value=data_value, on_change=lambda e, h=header:
                set_character_detail(h, e.value))
            else:
                ui.input(label=label, value=data_value, on_change=lambda e, h=header:
                set_character_data(database_section, index, h, e.value))
        elif entry_type == "bool":
            if head_table:
                ui.checkbox(text=label, value=data_value, on_change=lambda e, h=header:
                set_character_detail(h, e.value))
            else:
                ui.checkbox(text=label, value=data_value, on_change=lambda e, h=header:
                set_character_data(database_section, index, h, e.value))
        elif entry_type == "character_resources":
            if head_table:
                ui.select(options=[resource["name"] for resource in selected_character["resources"]],
                          label="Resource to override", value=data_value,
                          on_change=lambda e: set_character_detail(header, e.value))
            else:
                ui.select(options=[resource["name"] for resource in selected_character["resources"]],
                          label=label, value=data_value,
                          on_change=lambda e, h=header: set_character_data(database_section, index, h, e.value))
        else:
            if head_table:
                ui.select(options=mem["lists"][entry_type], label=label, value=data_value,
                          on_change=lambda e: set_character_detail(header, e.value))
            else:
                ui.select(options=mem["lists"][entry_type], label=label,
                          value=data_value,
                          on_change=lambda e, h=header: set_character_data(database_section, index, h, e.value))
