from nicegui import ui, app

from containers.ui_elements.group_modification import turn_table_character_group_click_dialog
from functions.data import df_max_lengths_in_cols
from functions.turn_table import turn_table_display_filter_df

main_container:ui.refreshable = None
sidebar:ui.refreshable = None

def turn_track_ui_list_create_content(user_type, highlight_rows, page: ui.refreshable, sidebar_page: ui.refreshable):
    global main_container, sidebar

    if main_container is None:
        main_container = page
        sidebar = sidebar_page

    px_char_width = 9
    px_side_buffer = 7
    min_px_width = 60

    def list_creator(list_row):
        op_mode = "table_click"
        if list_row['group'] == mem['current_turn'] and highlight_rows:
            item = ui.item(on_click=lambda: turn_track_ui_list_row_click_handler(list_row["name"], True, op_mode))
            item.classes('w-full items-center highlighted-row')
        else:
            item = ui.item(on_click=lambda: turn_track_ui_list_row_click_handler(list_row["name"], False, op_mode))
        with item.props('dense'):
            for list_col in cols:
                if list_col['name'] == "name":
                    row_col_width = col_widths["name"] if col_widths["name"] > col_widths["team"] else col_widths["team"]
                    with ui.item_section().props('no-wrap, side').style(f'width: {row_col_width}px'):
                        ui.item_label(list_row["name"])  # .classes('font-ui-monospace')
                        ui.item_label(list_row["team"]).props('caption')
                elif list_col['name'] != "team":
                    with ui.item_section().props('no-wrap, side').style(f'width: {col_widths[list_col['name']]}px'):
                        ui.item_label(list_row[list_col["name"]])  # .classes('font-ui-monospace')
        return item

    mem = app.storage.general
    cols, rows, display_table = turn_table_display_filter_df(user_type)
    base_col_widths = df_max_lengths_in_cols(display_table)

    # Calculate necessary pixel widths for columns
    col_widths = {}
    for col in base_col_widths.keys():
        col_width = (base_col_widths[col] * px_char_width) + px_side_buffer
        if col_width < min_px_width: col_width = min_px_width
        col_widths[col] = col_width

    with ui.list().style('width: fit-content;').props('bordered separator'):
        with ui.item().props('dense'):
            for col in cols:
                if col['name'] != "team":
                    if col['name'] == "name":
                        width = col_widths["name"] if col_widths["name"] > col_widths["team"] else col_widths["team"]
                    else:
                        width = col_widths[col['name']]
                    with ui.item_section().props('no-wrap, side').style(f'width: {width}px'):
                        ui.item_label(col['label']).classes('text-bold')
        ui.separator()
        for row in rows:
            list_creator(row)
    return

def refresh():
    global main_container, sidebar
    main_container.refresh()
    sidebar.refresh()

def turn_track_ui_list_row_click_handler(name, if_turn, op_mode):
    mem = app.storage.general
    user = app.storage.user
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
        refresh()
    elif operation == "remove_actor":
        list_actor = list(mem["turn_data"]["actor"])
        if name in list_actor:
            list_actor.remove(name)
            mem["turn_data"]["actor"] = list_actor
        else:
            ui.notify(f"{name} wasn't in the actor select...huh, someone found a bug..")
        refresh()
    elif operation == 'target':
        list_target = list(mem["turn_data"]["target"])
        if not (name in list_target):
            list_target.append(name)
            mem["turn_data"]["target"] = list_target
        else:
            ui.notify(f"{name} is already selected as target")
        refresh()
    elif operation == "remove_target":
        list_target = list(mem["turn_data"]["target"])
        if name in list_target:
            list_target.remove(name)
            mem["turn_data"]["target"] = list_target
        else:
            ui.notify(f"{name} wasn't in the target select...huh")
        refresh()
    elif operation == 'group':
        turn_table_character_group_click_dialog(main_container,name)
    elif operation == 'info':
        user['character_focus'] = name
        print(user['character_focus'])
        refresh()