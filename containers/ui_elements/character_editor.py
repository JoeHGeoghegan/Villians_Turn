# Library Imports
import pandas as pd
from nicegui import ui, app
from pandas import Series

### Local Imports
from functions.basics import dict_to_df, df_to_dict
from functions.characters import character_list, new_character, character_search
from functions.database import resources_file_init
from containers.ui_elements.turn_table_interface import turn_track_ui_list_create_content

# Page Temp Memory
selected_character: dict = {}
containing_page: ui.refreshable = None
weapons_panel: ui.tab_panel = None
resources_panel: ui.tab_panel = None
feats_panel: ui.tab_panel = None
features_panel: ui.tab_panel = None
conditions_panel: ui.tab_panel = None
inventory_panel: ui.tab_panel = None
resource_override_panel: ui.tab_panel = None

def create_content(page: ui.refreshable,sidebar: ui.refreshable):
    # memory setup
    global selected_character
    global containing_page
    global weapons_panel,resources_panel,feats_panel,features_panel,conditions_panel,inventory_panel,resource_override_panel

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
        if len(all_characters) == 0 or all_characters == ["New Character"]: character_selector.disable()
        else: character_selector.enable()# Normal selector

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
                    weapons_tab = ui.tab('Weapons')
                    resources_tab = ui.tab('Resources')
                    feats_tab = ui.tab('Feats')
                    features_tab = ui.tab('Features')
                    conditions_tab = ui.tab('Conditions')
                    inventory_tab = ui.tab('Inventory')
                    resource_override_tab = ui.tab('Resource Overrides')
                with ui.tab_panels(tabs, value=weapons_tab).classes('w-full'):
                    weapons_panel = ui.tab_panel(weapons_tab)
                    if len(selected_character["weapons"]) > 0:
                        make_entry_cards(weapons_panel, "weapons",
                                         [["Add Weapon", lambda: new_weapon()]])
                    resources_panel = ui.tab_panel(resources_tab)
                    if len(selected_character["resources"]) > 0:
                        make_entry_cards(resources_panel, "resources",
                                         [["Add Resource",lambda: new_resource()],
                                          ["Add Spell Resources",lambda:
                                              add_to_section("resources", resources_file_init(
                                              selected_character["character_details"]["name"],
                                              "assets/database_structures/resources/addable_spell_resources_defaults.csv"))]
                                          ])
                    feats_panel = ui.tab_panel(feats_tab)
                    if len(selected_character["feats"]) > 0:
                        make_search_cards(feats_panel, "feats", "feats",
                                          "Feat", None,
                                          [["Add Feat", lambda: new_feat()]])
                    features_panel = ui.tab_panel(features_tab)
                    if len(selected_character["features"]) > 0:
                        make_search_cards(features_panel, "features", "features",
                                          "Features", "Description",
                                          [["Add Feature", lambda: new_feature()]])
                    conditions_panel = ui.tab_panel(conditions_tab)
                    if len(selected_character["conditions"]) > 0:
                        make_search_cards(conditions_panel, "conditions", "conditions",
                                          "Condition", "Description",
                                          [["Add Condition", lambda: new_condition()]])
                    inventory_panel = ui.tab_panel(inventory_tab)
                    if len(selected_character["inventory"]) > 0:
                        make_search_cards(inventory_panel, "inventory","items",
                                         "Item",None,
                                         [["Add Inventory", lambda: new_inventory()]])
                    resource_override_panel = ui.tab_panel(resource_override_tab)
                    if len(selected_character["resource_override"]) > 0:
                        make_entry_cards(resource_override_panel, "resource_override",
                                         [["Add Resource Override", lambda: new_resource_override()]])
        ui.button("Save", on_click=lambda: (character_save(selected_character), page.refresh()))
    with ui.column():
        if all(cell is None for cell in mem['character_details'][0].values()):
            ui.label("No other characters exist")
        else:
            turn_track_ui_list_create_content("Host", highlight_rows=False, page=page, sidebar_page=sidebar)

def make_entry_cards(tab_panel,mem_section,end_buttons):
    mem = app.storage.general

    with tab_panel:
        for index,values in enumerate(selected_character[mem_section]):
            with ui.card():
                with ui.card_section():
                    with ui.row():
                        entry_fields(mem_section,
                                     mem["schemas"][mem_section]["headers"],
                                     index=index)
                        delete_icon = ui.icon("delete", color='primary').classes('text-5xl')
                        delete_icon.tooltip(f'Delete')
                        delete_icon.on('click', lambda: remove_character_data(mem_section, index))
        with ui.row():
            for button_items in end_buttons:
                ui.button(button_items[0],on_click=button_items[1])


def make_search_cards(tab_panel, mem_section, search_datablock, search_datablock_column, search_datablock_description_column, end_buttons):
    with tab_panel:
        for index,values in enumerate(selected_character[mem_section]):
            with ui.card():
                with ui.card_section():
                    with ui.row():
                        search_field(mem_section,search_datablock,
                                     search_datablock_column,search_datablock_description_column,
                                     index=index)
                        delete_icon = ui.icon("delete", color='primary').classes('text-5xl')
                        delete_icon.tooltip(f'Delete')
                        delete_icon.on('click', lambda: remove_character_data(mem_section, index))
            with ui.row():
                for button_items in end_buttons:
                    ui.button(button_items[0], on_click=button_items[1])

def refresh_tab(tab):
    if tab == "weapons":
        weapons_panel.clear()
        if len(selected_character["weapons"]) > 0:
            make_entry_cards(weapons_panel, "weapons",
                             [["Add Weapon", lambda: new_weapon()]])
    elif tab == "resources":
        resources_panel.clear()
        if len(selected_character["resources"]) > 0:
            make_entry_cards(resources_panel, "resources",
                             [["Add Resource", lambda: new_resource()],
                              ["Add Spell Resources",
                               lambda: (add_to_section("resources", resources_file_init(
                                   selected_character["character_details"]["name"],
                                   "../../assets/database_structures/resources/addable_spell_resources_defaults.csv")),
                                        refresh_tab("resources"))]
                              ])
    elif tab == "feats":
        feats_panel.clear()
        if len(selected_character["feats"]) > 0:
            make_search_cards(feats_panel, "feats", "feats",
                              "Feat", None,
                              [["Add Feat", lambda: new_feat()]])
    elif tab == "features":
        features_panel.clear()
        if len(selected_character["features"]) > 0:
            make_search_cards(features_panel, "features", "features",
                              "Features", "Description",
                              [["Add Feature", lambda: new_feature()]])
    elif tab == "conditions":
        conditions_panel.clear()
        if len(selected_character["conditions"]) > 0:
            make_search_cards(conditions_panel, "conditions", "conditions",
                              "Condition", "Description",
                              [["Add Condition", lambda: new_condition()]])
    elif tab == "inventory":
        inventory_panel.clear()
        if len(selected_character["inventory"]) > 0:
            make_search_cards(inventory_panel, "inventory", "items",
                              "Item", None,
                              [["Add Inventory", lambda: new_inventory()]])
    elif tab == "resource_override":
        resource_override_panel.clear()
        if len(selected_character["resource_override"]) > 0:
            make_entry_cards(resource_override_panel, "resource_override",
                             [["Add Resource Override", lambda: new_resource_override()]])

def character_save(character):
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

def add_to_section(section, new_item):
    global selected_character
    if type(new_item) == dict:
        selected_character[section].append(new_item)
    elif type(new_item) == list:
        selected_character[section].extend(new_item)
    refresh_tab(section)

def set_character_data(section, index, key, new_value):
    if type(new_value) == float:
        new_value = int(new_value)
    global selected_character
    selected_character[section][index][key] = new_value

def remove_character_data(section, index):
    global selected_character
    selected_character[section].pop(index)
    refresh_tab(section)

def set_character_detail(key, new_value):
    if type(new_value) == float:
        new_value = int(new_value)
    global selected_character
    selected_character["character_details"][key] = new_value

def entry_fields(mem_section, header_list, index=0):
    global selected_character
    mem = app.storage.general
    head_table = True if mem_section == "character_details" else False
    for header in header_list:
        label = mem["schemas"][mem_section]["labels"][header]  # only need the specific label and type
        entry_type = mem["schemas"][mem_section]["types"][header]
        if head_table:
            data_value = selected_character[mem_section][header]
        else:
            data_value = selected_character[mem_section][index][header]
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
                set_character_data(mem_section, index, h, e.value))
        elif entry_type == "string":
            if head_table:
                ui.input(label=label, value=data_value, on_change=lambda e, h=header:
                set_character_detail(h, e.value))
            else:
                ui.input(label=label, value=data_value, on_change=lambda e, h=header:
                set_character_data(mem_section, index, h, e.value))
        elif entry_type == "dice_equation":  # Same as String but with validation. #TODO add validation (Try/Except on dice roll?)
            if head_table:
                ui.input(label=label, value=data_value, on_change=lambda e, h=header:
                set_character_detail(h, e.value))
            else:
                ui.input(label=label, value=data_value, on_change=lambda e, h=header:
                set_character_data(mem_section, index, h, e.value))
        elif entry_type == "bool":
            if head_table:
                ui.checkbox(text=label, value=data_value, on_change=lambda e, h=header:
                set_character_detail(h, e.value))
            else:
                ui.checkbox(text=label, value=data_value, on_change=lambda e, h=header:
                set_character_data(mem_section, index, h, e.value))
        elif entry_type == "character_resources":
            if head_table:
                ui.select(options=[resource["name"] for resource in selected_character["resources"]],
                          label=label, value=data_value,
                          on_change=lambda e: set_character_detail(header, e.value))
            else:
                ui.select(options=[resource["name"] for resource in selected_character["resources"]],
                          label=label, value=data_value,
                          on_change=lambda e, h=header: set_character_data(mem_section, index, h, e.value))
        else:
            if head_table:
                ui.select(options=mem["lists"][entry_type], label=label, value=data_value,
                          on_change=lambda e: set_character_detail(header, e.value))
            else:
                ui.select(options=mem["lists"][entry_type], label=label,
                          value=data_value,
                          on_change=lambda e, h=header: set_character_data(mem_section, index, h, e.value))


def search_field(mem_section, datablock, search_column, description_column, index):
    global selected_character,containing_page
    mem = app.storage.general

    # Dialogs
    def detail_dialog():
        with ui.dialog() as dialog, ui.card():
            ui.label("Details")

            if description_column is not None:
                ui.markdown(datablock_df.loc[datablock_df[search_column] == data_value, description_column].iloc[0])
            with ui.row():
                ui.button('Close', on_click=dialog.close)

        dialog.open()
    def search_dialog():
        with ui.dialog() as dialog, ui.card():
            ui.label(f'Find {datablock}')

            selected = ui.select(select_list, label=f'Choose {datablock}',on_change=lambda : refresh_tab(mem_section))

            if selected.value is not None and description_column is not None:
                ui.markdown(datablock_df.loc[datablock_df[search_column] == data_value, description_column])

            with ui.row():
                ui.button('Close', on_click=dialog.close)
                ui.button('Submit', on_click=lambda: (
                    dialog.close(),
                    set_character_data(mem_section, index, 'name', selected.value),
                    refresh_tab(mem_section)
                ))

        dialog.open()

    #init datablock if nothing loaded
    if 'datablocks' not in mem:
        mem["datablocks"] = {}
        datablock_df = pd.read_csv(f"assets/database_structures/datablocks/{datablock}.csv")
        mem["datablocks"][datablock] = df_to_dict(datablock_df)
        select_list = datablock_df[search_column].tolist()
    #init specific datablock if not loaded
    elif datablock not in mem["datablocks"]:
        datablock_df = pd.read_csv(f"assets/database_structures/datablocks/{datablock}.csv")
        select_list = datablock_df[search_column].tolist()
    else:
        datablock_df = dict_to_df(mem["datablocks"][datablock])
        select_list = datablock_df[search_column].tolist()

    label = mem["schemas"][mem_section]["labels"]['name']  # only need the specific label and type
    data_value = selected_character[mem_section][index]['name']
    # clean data_value
    if type(data_value) == Series:
        data_value = data_value.iloc[0]
    ui.input(label=label, value=data_value, on_change=lambda e:
        set_character_data(mem_section, index, "name", e.value))
    if "weight" in mem["schemas"][mem_section]["headers"]:
        ui.number(label=mem["schemas"][mem_section]["labels"]["weight"], value=selected_character[mem_section][index]["weight"],
                  on_change=lambda e :set_character_data(mem_section, index, "weight", e.value))
    if data_value is not None and description_column is not None:
        detail_icon = ui.icon("help_outline", color='primary').classes('text-5xl')
        detail_icon.tooltip(f'{label} Details')
        detail_icon.on('click', detail_dialog)
    search_icon = ui.icon("manage_search", color='primary').classes('text-5xl')
    search_icon.tooltip(f'{label} Search')
    search_icon.on('click', search_dialog)

def new_weapon():
    global selected_character, containing_page
    add_to_section("weapons", {
        "character_name":selected_character["character_details"]["name"],
        "name":'',
        "action_cost":0,
        "range":5,
        "damage_dice":'',
        "attribute":'none',
        "proficiency":False,
        "weight":0,
        "traits":''
    })

def new_resource():
    global selected_character, containing_page
    add_to_section("resources", {
        "character_name":selected_character["character_details"]["name"],
        "name": '',
        "resource_type": None,
        "resource_type_trigger_time": None,
        "resource_use_type": None,
        "current": None,
        "max": None,
        "min": None,
        "proficiency": False,
        "attribute": 'none'
    })

def new_feat():
    global selected_character, containing_page
    add_to_section("feats", {
        "character_name":selected_character["character_details"]["name"],
        "name": ''
    })

def new_feature():
    global selected_character, containing_page
    add_to_section("features", {
        "character_name":selected_character["character_details"]["name"],
        "name": ''
    })

def new_condition():
    global selected_character, containing_page
    add_to_section("conditions", {
        "character_name":selected_character["character_details"]["name"],
        "name": ''
    })

def new_inventory():
    global selected_character, containing_page
    add_to_section("inventory", {
        "character_name":selected_character["character_details"]["name"],
        "name": '',
        "weight": None
    })

def new_resource_override():
    global selected_character, containing_page
    add_to_section("resource_override", {
        "character_name":selected_character["character_details"]["name"],
        "resource_name" : None,
        "override_type" : None,
        "override_resource_type" : None,
        "override_resource_type_trigger_time" : None,
        "override_resource_use_type" : None,
        "override_current" : None,
        "override_max" : None,
        "override_min" : None,
        "override_proficiency" : True,
        "override_attribute" : 'none'
    })