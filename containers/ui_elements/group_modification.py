# Imports
from nicegui import ui

# Local Functions
from functions.basics import mem_df_modify
from functions.groups import breakup_group, groups_list, merge_groups, rename_group
from functions.turn_table import turn_track_df


def create_group_content(page: ui.refreshable):
    groups = groups_list(turn_track_df())

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
                ui.button("Change", on_click=lambda: (mem_df_modify("turn_track",
                                                                    rename_group,
                                                                    *(group, name.value)),
                                                      dialog.close, page.refresh()))
        ui.button('Breakup Group', on_click=lambda: (mem_df_modify("turn_track",
                                                                   breakup_group,
                                                                   group),
                                                     dialog.close, page.refresh()))
        with ui.list().style('width: fit-content;').props('bordered separator'):
            with ui.item().props('dense'):
                ui.item_label("Merge with another Group")
            ui.separator()

            def local_merge_group_row(head_page, head_group, head_other_group):
                item = ui.item(on_click=lambda: (merge_group_dialog(head_page, head_group, head_other_group)))
                with item.props('dense'):
                    with ui.item_section().props('no-wrap, side'):
                        ui.item_label(head_other_group)
                return item

            for other_group in groups:
                if other_group != group:
                    local_merge_group_row(page, group, other_group)
        ui.button('Close', on_click=dialog.close)
    dialog.open()


def merge_group_dialog(page: ui.refreshable, group1, group2):
    with ui.dialog() as dialog, ui.card():
        ui.button(f'Set name to {group1}', on_click=lambda: (mem_df_modify("turn_track",
                                                                           merge_groups,
                                                                           *(group1, group2, group1)),
                                                             dialog.close, page.refresh()))
        ui.button(f'Set name to {group2}', on_click=lambda: (mem_df_modify("turn_track",
                                                                           merge_groups,
                                                                           *(group1, group2, group2)),
                                                             dialog.close, page.refresh()))
        with ui.row():
            new_name = ui.input("Name", placeholder="Or enter new name")
            if new_name.value is not None:
                ui.button("Confirm", on_click=lambda: (mem_df_modify("turn_track",
                                                                     merge_groups,
                                                                     *(group1, group2, new_name.value)),
                                                       dialog.close, page.refresh()))

        ui.button('Back', on_click=dialog.close)
    dialog.open()
