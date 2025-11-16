from nicegui import ui

columns = [
    {'name': 'name', 'label': 'Name', 'field': 'name', 'required': True, 'align': 'left'},
    {'name': 'age', 'label': 'Age', 'field': 'age', 'sortable': True},
]

rows = [
    {'name': 'Alice', 'age': 30},
    {'name': 'Bob', 'age': 24},
    {'name': 'Charlie', 'age': 35},
]


@ui.page('/')
def main_page():
    ui.label('Click on a row in the table below:')
    table = ui.table(columns=columns, rows=rows, row_key='name')

    def handle_row_click(e):
        print(e)
        clicked_name = e.args[1]["name"]
        ui.notify(f'You clicked on: {clicked_name}')

    table.on('row-click', handle_row_click)


ui.run()
