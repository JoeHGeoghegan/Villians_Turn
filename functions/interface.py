from nicegui import app, ui

#local imports
from functions.game import turn_table_display

def game_list(user_type,highlight_rows,page:ui.refreshable):
    def list_creator(row):
        op_mode = "table_click"
        if (row['group'] == mem['current_turn'] and highlight_rows):
            item = ui.item(on_click=lambda: (table_click_handler(row["name"],True,op_mode), page.refresh()))
            item.classes('w-full items-center highlighted-row')
        else:
            item = ui.item(on_click=lambda: (table_click_handler(row["name"],False,op_mode), page.refresh()))
        with item.props('dense'):
            for col in cols:
                if col['name'] == "name":
                    with ui.item_section().props('no-wrap, side').classes(f'col-{col["name"]}'):
                        ui.item_label(row["name"])
                        ui.item_label(row["team"]).props('caption')
                elif col['name'] != "team":
                    with ui.item_section().props('no-wrap, side').classes(f'col-{col["name"]}'):
                        ui.item_label(row[col["name"]])
        return item
    
    mem = app.storage.general
    cols, rows = turn_table_display(user_type)
    with ui.list().style('width: fit-content;').props('bordered separator'):
        with ui.item().props('dense'):
            for col in cols:
                if col['name'] != "team" :
                    with ui.item_section().props('no-wrap, side').classes(f'col-{col["name"]}'):
                        ui.item_label(col['label']).classes('text-bold')
        ui.separator()
        for row in rows:
            list_creator(row)
    return

def table_click_handler(name,if_turn,op_mode):
    mem = app.storage.general
    if op_mode == "table_click":
        operation = mem["table_mode"]
    else:
        operation = op_mode
    print(f"Handling {operation} type operation for {name}. Turn: {if_turn}")
    if operation == 'actor':
        list_actor = list(mem["turn_data"]["actor"])
        list_actor_override = list(mem["turn_data"]["actor_override"])
        if not (name in list_actor) and (if_turn or (name in list_actor_override)):
            list_actor.append(name)
            mem["turn_data"]["actor"] = list_actor
        elif not (name in list_actor_override):
            ui.notify(f"It is not {name}'s turn. Press again to add anyway.")
            list_actor_override.append(name)
            mem["turn_data"]["actor_override"] = list_actor_override
        else:
            ui.notify(f"{name} is already selected as actor")
    elif operation == "remove_actor":
        list_actor = list(mem["turn_data"]["actor"])
        if name in list_actor:
            list_actor.remove(name)
            mem["turn_data"]["actor"] = list_actor
        else:
            ui.notify(f"{name} wasn't in the actor select...huh")
    elif operation == 'target':
        list_target = list(mem["turn_data"]["target"])
        if not (name in list_target):
            list_target.append(name)
            mem["turn_data"]["target"] = list_target
        else:
            ui.notify(f"{name} is already selected as target")
    elif operation == "remove_target":
        list_target = list(mem["turn_data"]["target"])
        if name in list_target:
            list_target.remove(name)
            mem["turn_data"]["target"] = list_target
        else:
            ui.notify(f"{name} wasn't in the target select...huh")
    elif operation == 'group':
        return
    elif operation == 'info':
        return
    print(mem["turn_data"])

def select_handler(select_values,mem_turn_data_list):
    app.storage.general["turn_data"][mem_turn_data_list] = select_values

def set_user_type(role):
    app.storage.user["type"] = role

def overview_table_row_style(row, group):
    if row["Group"] == group :
        return f'background-color: {ui.colors.accent};'