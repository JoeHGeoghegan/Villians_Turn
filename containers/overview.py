# Library Imports
from nicegui import ui, app
import pandas as pd

### Local Imports
from functions.data import set_mem
from functions.game import peak_turn, set_turn, turn_track
from functions.groups import groups_list
from functions.interface import game_list

def create_content(page:ui.refreshable):
    def update_content():
        ui_turn_number.update()
        ui_action_number.update()
        ui_current_turn.update()
        ui_on_deck.update()
        page.refresh()
    # memory setup
    mem = app.storage.general
    user = app.storage.user
    # Turn Initialize
    if mem["current_turn"]==None or not (mem["current_turn"] in groups_list(turn_track())):
            mem["current_turn"] = turn_track().iloc[0]['group']
    ######## UI ########
    with ui.row():
        with ui.column():
            with ui.row():
                ui_turn_number = ui.label(f"Turn #: {mem['turn_number']}").classes('text-xl')
                ui_action_number = ui.label(f"Action #: {mem['action_number']}").classes('text-xl')
            with ui.row():
                game_list(user["type"], highlight_rows=True)
        with ui.column():
            if user["type"]=="Host":
                with ui.button_group().classes('flex justify-end'):
                    sel_options = {
                        'Setup': 'Setup',
                        'Active': 'Active'
                        }
                    ui.select(sel_options,value=mem["turn_mode"],on_change=lambda selector : set_mem("turn_mode",selector.value))
                    ui.button("Previous Turn", on_click=lambda e: (set_turn(turn_track(), mem["current_turn"],-1,mem["turn_mode"]),update_content()))
                    ui.button("Next Turn", on_click=lambda e: (set_turn(turn_track(), mem["current_turn"],1,mem["turn_mode"]),update_content()))
                with ui.column():
                    ui_current_turn = ui.label(f"Current Turn: {mem["current_turn"]}")
                    ui_on_deck = ui.label(f"On Deck: {peak_turn(turn_track(), mem["current_turn"],1)}")