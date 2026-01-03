from nicegui import app


def results_data_init():
    results_data = {}
    mem = app.storage.general
    for flavor in mem['flavors']:
        results_data[flavor] = {
            "target": [],
            "modification": None,
            "result_data": None
        }
    return results_data

class Action:
    def __init__(self,group):
        mem = app.storage.general
        self.turn = group # Current Turn's Group if Host or Player's Group
        self.actors = mem['turn_data']["actor"]
        self.actors_notes = []
        self.targets = mem['turn_data']["target"]
        self.targets_notes = []
        self.action_type = None
        self.action_subtype = None
        self.action_notes = []
        self.action_results = []
        self.action_results_data = results_data_init()
    def action_row(self):
        return [self.actors,self.actors_notes,
                self.targets,self.targets_notes,
                self.action_type,self.action_subtype,self.action_notes,
                self.action_results, self.action_results_data]
