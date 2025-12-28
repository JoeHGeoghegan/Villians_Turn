# Library Imports
from nicegui import ui, app

from classes.Action import Action
from classes.Turn import Turn
from functions.basics import dict_to_df, list_oxford
from functions.groups import player_characters_groups

actors: ui.select = None
targets: ui.select = None
containing_page: ui.refreshable = None
current_turn = Turn()

def combat_interface(page: ui.refreshable):
    # Init
    global containing_page, actors, targets
    if containing_page is None:
        containing_page = page
    # memory setup
    mem = app.storage.general

    turn_track = dict_to_df(mem["character_details"])
    all_characters = turn_track["name"].to_list()
    all_characters.append("Non-Tracked Entity")
    active_characters = turn_track[turn_track["group"] == mem["current_turn"]]["name"]
    active_characters = active_characters.to_list()
    active_selectable_characters = active_characters.copy()
    active_selectable_characters.extend(mem["turn_data"]["actor_override"])
    active_selectable_characters.append("Non-Tracked Entity")

    with (ui.column()):
        ui.label(f"Actions needed for {list_oxford(active_characters)}")
        # Current Turn's Action Status Table (No Actions Yet, Suggested Action, Action Given)
        actors = ui.select(active_selectable_characters, multiple=True, label='Action Actor(s)',
                           value=mem['turn_data']["actor"],
                           on_change=lambda e: (select_handler(e.value, "actor"), page.refresh())
                           ).classes('w-64').props('use-chips')
        targets = ui.select(all_characters, multiple=True, label='Action Target(s)',
                            value=mem['turn_data']["target"],
                            on_change=lambda e: (select_handler(e.value, "target"), page.refresh())
                            ).classes('w-64').props('use-chips')
        ui.button("Make Action", on_click=lambda : action_dialog()).bind_enabled_from(actors, "value")
        ui.button("Finalize Turn", on_click=lambda : turn_dialog()).bind_visibility_from(current_turn, "actions")

def select_handler(select_values, mem_turn_data_list):
    app.storage.general["turn_data"][mem_turn_data_list] = select_values

def action_dialog():
    global current_turn
    mem = app.storage.general
    user = app.storage.user
    is_host = user['type'] == "Host" # TODO DO NOT IMPLEMENT THIS FURTHER DUDE!

    action = Action(mem["current_turn"] if is_host else player_characters_groups()[0]["group"])

    # Action Selector, Delete Action, Save Action # TODO DO NOT IMPLEMENT THIS FURTHER DUDE!

    with ui.dialog() as dialog, ui.card():
        ui.label(f"Make Action for {list_oxford(actors.value)}")
        with ui.row().classes('w-full no-wrap'):
            with ui.column():
                ui.label("Action Type")
                action_type_select = ui.toggle(options=list(mem['audit_actions'].keys()),
                                               on_change=lambda e: action_subtype_select.set_options(mem["audit_actions"][e.value]))\
                    .bind_value(action, "action_type")\
                    .classes('w-full no-wrap')
        with ui.row().classes('w-full no-wrap'):
            action_subtype_select = ui.select(label="Action Subtype", options=["Select Action Type"]) \
                .bind_enabled_from(action, "action_type") \
                .bind_value(action, "action_subtype")\
                .bind_visibility_from(action_type_select,"value")\
                .classes('w-full no-wrap')
        ui.separator()
        with ui.row():
            if is_host:
                ui.button("Add Action")
            else:
                ui.button("Suggest Action Plan")
            ui.button('Back', on_click=dialog.close)
    dialog.open()

def turn_dialog():

    with ui.dialog() as dialog, ui.card():
        with ui.row():
            pass
        ui.separator()
        with ui.row():
            ui.button('Back', on_click=dialog.close)
    dialog.open()