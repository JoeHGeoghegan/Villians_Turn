from functions.game import roll_dice
# from classes.Action import Action

class Turn:
    def __init__(self):
        self.d20_roll = roll_dice("d20") #TODO Revamp - this is all temporary
        self.turn_track, self.current_turn, self.results_data, self.additional_log = None, None, None, None
        self.actions = []
    def to_dict(self):
        # Convert object attributes to a dictionary
        return {}
    def load_dict(self, data: dict):
        #TODO
        self.d20_roll = data["d20"]
    def update_d20(self):
        self.d20_roll = roll_dice("d20")
    def action_rows(self):
        return [x.action_row() for x in self.actions]