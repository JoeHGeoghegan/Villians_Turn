from nicegui import app


def set_user_type(role):
    print(f"Currently {app.storage.user["type"]} and setting to {role}")
    app.storage.user["type"] = role
    print(app.storage.user["type"])