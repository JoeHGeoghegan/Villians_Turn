# Library Imports
from nicegui import ui, app

from classes.Action import Action
from classes.Turn import Turn
from functions.basics import dict_to_df, list_oxford
from functions.game import roll_dice, validate_die_roll
from functions.groups import player_characters_groups, groups_list

action:Action = None
actors: ui.select = None
containing_page: ui.refreshable = None
current_turn = Turn()

def combat_interface(page: ui.refreshable):
    # Init
    global containing_page, actors
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
        actors = ui.select(active_selectable_characters,
                           multiple=True,
                           label='Action Actor(s)')\
            .classes('w-64').props('use-chips')\
            .bind_value(mem['turn_data'], "actor")
        ui.button("Make Action", on_click=lambda : action_dialog()).bind_enabled_from(actors, "value")
        ui.button("Finalize Turn", on_click=lambda : turn_dialog()).bind_visibility_from(current_turn, "actions")

def select_handler(select_values, mem_turn_data_list):
    app.storage.general["turn_data"][mem_turn_data_list] = select_values

def action_dialog():
    global current_turn, containing_page, action
    mem = app.storage.general
    user = app.storage.user
    turn_track = dict_to_df(mem["character_details"])
    all_characters = turn_track["name"].to_list()
    all_characters.append("Non-Tracked Entity")
    is_host = user['type'] == "Host" # TODO DO NOT IMPLEMENT THIS FURTHER DUDE!

    action = Action(mem["current_turn"] if is_host else player_characters_groups()[0]["group"])

    # Action Selector, Delete Action, Save Action # TODO DO NOT IMPLEMENT THIS FURTHER DUDE!

    with ui.dialog().style('width: 1200px; max-width: none') as dialog, ui.card():
        ui.label(f"Make Action for {list_oxford(actors.value)}")
        with ui.row().classes('w-full no-wrap'):
            with ui.column():
                ui.label("Action Type")
                action_type_select = ui.toggle(options=list(mem['audit_actions'].keys()),
                                               on_change=lambda e: (action_subtype_select.set_options(mem["audit_actions"][e.value]),
                                                                    targets_visibility_handle(e.value)))\
                    .bind_value(action, "action_type")\
                    .classes('w-full no-wrap')
        with ui.row().classes('w-full no-wrap'):
            action_subtype_select = ui.select(label="Action Subtype", options=["Select Action Type"]) \
                .bind_enabled_from(action, "action_type") \
                .bind_value(action, "action_subtype")\
                .bind_visibility_from(action_type_select,"value")\
                .classes('w-64').props('use-chips')
            targets = ui.select(all_characters, multiple=True, label='Action Target(s)')\
                .classes('w-64').props('use-chips')\
                .bind_value(mem['turn_data'],"target")
        if is_host:
            ui.separator()
            with ui.row().classes('w-full no-wrap'):
                with ui.input("Dice Roller",value="1d20") as dice_equation:
                    ui.tooltip("Enter Dice Equation. Example: 2d20-2d3+4")
                with ui.column():
                    roll_button = ui.button("Roll")
                    die_roll_info = ui.label().style('white-space: pre-wrap;')
                def roll_the_dice():
                    if validate_die_roll(dice_equation.value):
                        roll = roll_dice(dice_equation.value,show_details=True,show_range=True)
                        return f"{roll['result']} rolled{"!" if roll['result']==roll['max'] else "."}\nRange: {roll["min"]} to {roll['max']}"
                    else:
                        return "Failed to roll dice. Check input."
                roll_button.on_click(lambda: die_roll_info.set_text(roll_the_dice()))
                ui.select(mem['audit_outcome']['Outcome'], label='Action Outcome') \
                    .classes('w-48')
            ui.separator()
            with ui.row().classes('w-full no-wrap'):
                ui.select(mem['audit_outcome']['Results'], multiple=True, label='Action Result(s)',
                          on_change=lambda e: ( update_results_data(e.value), build_result_list()))\
                    .classes('w-64').props('use-chips')\
                    .bind_value(action, "action_results")
                # if results_select.value:
                flavors = mem['flavors']
            with ui.row():
                result_data_list = ui.list().props('dense separator')
        ui.separator()
        with ui.row():
            if is_host:
                ui.button("Add Action")
            else:
                ui.button("Suggest Action Plan")
            ui.button('Back', on_click=dialog.close)
    def targets_visibility_handle(action_mode):
        if action_mode == "Main Action":
            targets.set_visibility(True)
        else:
            targets.set_visibility(False)
            mem["targets"] = []
    def build_result_list():
        result_data_list.clear()
        with result_data_list:
            for result in action.action_results:
                flavor = flavors[result]
                with ui.item():
                    with ui.item_section().props('no-wrap'):
                        ui.label(result)
                    with ui.item_section().props('no-wrap, side'):
                        if flavor["target"] == 'self':
                            target_pool = actors
                        elif flavor["target"] == 'target_group':
                            target_pool = groups_list(dict_to_df(mem["character_details"]))
                        else:
                            target_pool = all_characters  # general target
                        ui.select(target_pool, multiple=True, label="Specific Target(s)")\
                            .classes('w-64').props('use-chips')\
                            .bind_value(action.action_results_data[result], "target")
                    with ui.item_section().props('no-wrap, side'):
                        ui.label(flavor["modification"])
                        if flavor["modification"] in ['+', '-']:
                            ui.number(label=flavor["wording"], precision=0)\
                                .classes('w-64') \
                                .bind_value(action.action_results_data[result], "result_data")
                        elif flavor["modification"] == "attribute":
                            ui.select(mem["lists"]["attribute"], label=flavor["wording"])\
                                .classes('w-64') \
                                .bind_value(action.action_results_data[result], "result_data")
                        elif flavor["modification"] == "condition":
                            # TODO
                            ui.label("Unimplemented")
                        elif flavor["modification"] == "disrupt":
                            ui.button("Specify Disruption", on_click=lambda: disrupt_dialog())
                        else:
                            ui.label(f"'{flavor["modification"]}' didn't catch logic")
    targets_visibility_handle("Init")
    dialog.open()

def update_results_data(results):
    global action
    mem = app.storage.general
    for data in action.action_results_data:
        flavor = mem['flavors'][data]
        if data in results:
            action.action_results_data[data]["modification"] = flavor["modification"]
            if action.action_results_data[data]["result_data"] is None:
                if flavor["modification"] in ['-','+']:
                    action.action_results_data[data]["result_data"] = 0
                else:
                    action.action_results_data[data]["result_data"] = ""
        else:
            action.action_results_data[data]["target"] = []
            action.action_results_data[data]["modification"] = None
            action.action_results_data[data]["result_data"] = None
    return

def disrupt_dialog():
    action.action_results_data["Main Action"]["result_data"] = "disrupt"
    #TODO
    # if(action_group_to_split!=None):
    #     action_group_to_split_1st = st.text_input("First Half Name",value=f"{action_group_to_split} 1",key=f'target_name1_{result}')
    #     action_group_to_split_2nd = st.text_input("Second Half Name",value=f"{action_group_to_split} 2",key=f'target_name2_{result}')
    #     action_group_to_split_df = fx.df_match_slice(ss.turn_track,"group",action_group_to_split)
    #     action_split_decicions = []
    #     st.write("Where is:")
    #     for member in action_group_to_split_df['name']:
    #         action_split_decicions.append(st.select_slider(member,
    #             options=[action_group_to_split_1st,action_group_to_split_2nd],key=f'target_{member}_{result}'
    #         ))
    #     target_data = [action_group_to_split,action_group_to_split_1st,action_split_decicions,action_group_to_split_2nd]

def turn_dialog():

    with ui.dialog() as dialog, ui.card():
        with ui.row():
            pass
        ui.separator()
        with ui.row():
            ui.button('Back', on_click=dialog.close)
    dialog.open()