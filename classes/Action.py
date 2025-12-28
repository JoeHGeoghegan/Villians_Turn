from nicegui import app


class Action:
    def __init__(self,group):
        mem = app.storage.general
        self.turn = group # Current Turn's Group if Host or Player's Group
        self.actors = mem['turn_data']["actor"]
        self.actors_notes = []
        self.actors_impact = []
        self.targets = mem['turn_data']["target"]
        self.targets_notes = []
        self.targets_impact = []
        self.action_type = None
        self.action_subtype = None
        self.action_notes = []
    def action_row(self):
        return [self.actors,self.actors_notes,self.actors_impact,
                self.targets,self.targets_notes,self.targets_impact,
                self.action_type,self.action_subtype,self.action_notes]