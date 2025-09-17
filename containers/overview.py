# Library Imports
from nicegui import ui, app
import pandas as pd

### Local Imports
from functions.game import next_turn, previous_turn, set_current_turn, turn_table_viewer, turn_track
from functions.groups import groups_list

def create_content(page:ui.refreshable):
    def update_content():
        ui_current_turn.update()
        ui_on_deck.update()
        page.refresh()
    # memory setup
    mem = app.storage.general
    user = app.storage.user
    # Turn Initialize
    if mem["current_turn"]==None or not (mem["current_turn"] in groups_list(turn_track())):
            set_current_turn(turn_track().iloc[0]['group'])
    ######## UI ########
    with ui.row():
        with ui.column():
            with ui.row():
                ui.label(f"Turn #: {mem['turn_number']}").classes('text-xl')
                ui.label(f"Action #: {mem['action_number']}").classes('text-xl')
            with ui.row():
                ui.table.from_pandas(turn_table_viewer(dm_view=False)).on_select=lambda e: ui.notify(f'selected: {e.selection}')
        with ui.column():
            if user["type"]=="Host":
                with ui.button_group():
                    ui.button("Previous Turn", on_click=lambda: (set_current_turn(previous_turn(turn_track(), mem["current_turn"])),update_content()))
                    ui.button("Next Turn", on_click=lambda: (set_current_turn(next_turn(turn_track(), mem["current_turn"])),update_content()))
            ui_current_turn = ui.label(f"Current Turn: {mem["current_turn"]}")
            ui_on_deck = ui.label(f"On Deck: {next_turn(turn_track(), mem["current_turn"])}")