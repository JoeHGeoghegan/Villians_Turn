# Imports
from nicegui import ui,app

# Local Functions
from functions.basics import mem_df_modify, dict_to_df
from functions.groups import breakup_group, groups_list, merge_groups, rename_group, move_character, \
    move_character_to_new_group, move_group


def create_group_content(page: ui.refreshable):
    mem = app.storage.general
    groups = groups_list(dict_to_df(mem["character_details"]))

    def clickable_group(head_page, head_group):
        item = ui.item(on_click=lambda: (group_click_handler(head_page, head_group, groups)))
        with item.props('dense'):
            with ui.item_section().props('no-wrap, side'):
                ui.item_label(head_group)
        return item

    with ui.list().style('width: fit-content;').props('bordered separator'):
        with ui.item().props('dense'):
            ui.item_label("Modify Whole Groups?")
        ui.separator()
        for group in groups:
            clickable_group(page, group)


def group_click_handler(page: ui.refreshable, group, groups):
    with ui.dialog() as dialog, ui.card():
        with ui.row():
            name = ui.input("Name", value=group)
            if name != group:
                ui.button("Change", on_click=(lambda: (mem_df_modify("character_details",
                                                                    rename_group,
                                                                    *(group, name.value)),
                                                      page.refresh(),dialog.close)))
        ui.button('Breakup Group', on_click=(lambda: (mem_df_modify("character_details",
                                                                   breakup_group,
                                                                   group),
                                                     page.refresh(),dialog.close)))
        with ui.list().style('width: fit-content;').props('bordered separator'):
            with ui.item().props('dense'):
                function_selector = ui.toggle(["Move Before", "Move After", "Merge With"],value="Move Before")
            ui.separator()

            def local_group_row(head_page, head_group, head_other_group):
                def function_select_case(function, refresh_page, current_group, second_group):
                    if function == "Move Before":
                        mem_df_modify("character_details",
                                      move_group,
                                      *(current_group, "Before", second_group))
                        head_page.refresh()
                    elif function == "Move After":
                        mem_df_modify("character_details",
                                      move_group,
                                      *(current_group, "After", second_group))
                        head_page.refresh()
                    elif function == "Merge With":
                        merge_group_dialog(refresh_page, current_group, second_group)
                item = ui.item(on_click=lambda: (function_select_case(function_selector.value, head_page, head_group, head_other_group)))
                with item.props('dense'):
                    with ui.item_section().props('no-wrap, side'):
                        ui.item_label(head_other_group)
                return item

            for other_group in groups:
                if other_group != group:
                    local_group_row(page, group, other_group)
        ui.button('Close', on_click=dialog.close)
    dialog.open()


def merge_group_dialog(page: ui.refreshable, group1, group2):
    with ui.dialog() as dialog, ui.card():
        ui.button(f'Set name to {group1}', on_click=(lambda: (mem_df_modify("character_details",
                                                                           merge_groups,
                                                                           *(group1, group2, group1)),
                                                             page.refresh(),dialog.close)))
        ui.button(f'Set name to {group2}', on_click=(lambda: (mem_df_modify("character_details",
                                                                           merge_groups,
                                                                           *(group1, group2, group2)),
                                                             page.refresh(),dialog.close)))
        with ui.row():
            new_name = ui.input("Name", placeholder="Or enter new name")
            if new_name.value is not None:
                ui.button("Confirm", on_click=(lambda: (mem_df_modify("character_details",
                                                                     merge_groups,
                                                                     *(group1, group2, new_name.value)),
                                                       page.refresh(),dialog.close)))

        ui.button('Back', on_click=dialog.close)
    dialog.open()

def turn_table_character_group_click_dialog(page: ui.refreshable, character):
    with ui.dialog() as dialog, ui.card():
        mem = app.storage.general
        characters = dict_to_df(mem["character_details"])
        groups = groups_list(characters)
        character_group = characters[characters["name"] == character]["group"].iloc[0]
        with ui.row():
            ui.markdown(f'"**{character}**" is currently in group "**{character_group}**"')
        groups.remove(character_group)
        group_target = ui.select(options=groups,label="Groups",value=groups[0]).classes('w-32')
        new_group_input = ui.input(label="New Group Name", value=character_group)
        with ui.row():
            ui.button("Move to Group", on_click=(lambda: (mem_df_modify("character_details",
                                                                        move_character,
                                                                        *(character, group_target.value)),
                                                                    page.refresh(),dialog.close))).classes('w-32')
            ui.button("Move to New Group", on_click=(lambda: (mem_df_modify("character_details",
                                                                        move_character_to_new_group,
                                                                        *(character, new_group_input.value)),
                                                                    page.refresh(),dialog.close))).classes('w-32')
            ui.button('Back', on_click=dialog.close).classes('w-32')
    dialog.open()