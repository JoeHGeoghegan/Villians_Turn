# Library Imports
from nicegui import ui, app

# Local Imports
from functions.game import turn_track

actors: ui.select = None
targets: ui.select = None
containing_page: ui.refreshable = None


def update_content():
    actors.update()
    targets.update()
    containing_page.refresh()


def combat_interface(page: ui.refreshable):
    # Init
    global containing_page, actors, targets
    if containing_page is None:
        containing_page = page

    # memory setup
    mem = app.storage.general

    all_characters = turn_track()["name"].to_list()
    all_characters.append("Non-Tracked Entity")
    active_characters = turn_track()[turn_track()["group"] == mem["current_turn"]]["name"]
    active_characters = active_characters.to_list()
    active_characters.append("Non-Tracked Entity")
    with ui.column():
        with ui.row():  # Actor(s)
            actors = ui.select(active_characters, multiple=True, label='Actor(s)',
                               value=mem['turn_data']["actor"],
                               on_change=lambda e: (select_handler(e.value, "actor"), update_content())
                               ).classes('w-64').props('use-chips')
        with ui.row():  # Target(s)
            targets = ui.select(all_characters, multiple=True, label='Target(s)',
                                value=mem['turn_data']["target"],
                                on_change=lambda e: (select_handler(e.value, "target"), update_content())
                                ).classes('w-64').props('use-chips')


def select_handler(select_values, mem_turn_data_list):
    app.storage.general["turn_data"][mem_turn_data_list] = select_values
