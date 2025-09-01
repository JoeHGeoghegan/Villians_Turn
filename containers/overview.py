# Library Imports
from nicegui import ui, app
import pandas as pd

### Local Imports
import memory as mem
from functions.characters import attributes_list
from functions.data import has_flavor
from functions.game import next_turn, previous_turn, add_audit, submit_action
from functions.groups import groups_list, groups_gathered_check, multi_person_groups_list
from functions.basics import df_match_slice

def create_content():
    # Checks to ensure data is able to be displayed
    if len(mem.turn_track) == 0:
        ui.write("Welcome! Add Characters in the Modifications tab or Import an exisiting Villain's Turn csv to get started!")
    elif not groups_gathered_check(mem.turn_track) :
        ui.write("Groups are not gathered, move groups to desired order or reset initiative")
    else :
        # Turn tracking start up
        if mem.current_turn==None or not (mem.current_turn in groups_list(mem.turn_track)):
            mem.current_turn = mem.turn_track.iloc[0]['group']
        current_group = mem.turn_track.loc[mem.turn_track['group']==mem.current_turn]

        # Turn Track displays
        col_current_turn, col_on_deck, col_turn_controls = ui.columns(3)
        with col_current_turn:
            ui.write(f"{mem.current_turn}'s turn")
            ui.write(current_group['name'])
        with col_on_deck:
            next_turn = next_turn(mem.turn_track,mem.current_turn)
            ui.write(f"{next_turn} is on deck")
            ui.write(mem.turn_track.loc[mem.turn_track['group']==next_turn,'name'])
        with col_turn_controls:
            if ui.button("Next Turn"):
                mem.current_turn = next_turn
                mem.turn_number += 1
            if ui.button("Previous Turn"):
                mem.current_turn = previous_turn(mem.turn_track,mem.current_turn)
                mem.turn_number -= 1
            turn_jump = ui.selectbox("Jump to Turn",options=groups_list(mem.turn_track))
            if ui.button("Jump to Turn"):
                mem.current_turn = turn_jump
                mem.turn_number = 0
        
        # Combat Interface
        # Would be nice to do this with a form but forms stop the internal widgets from being modified
        if ui.checkbox("Show Combat Entry - Toggle to clear values"):
            ui.markdown("---")
            col_actors, col_action, col_target,col_execute = ui.columns(4)
            # Active Character
            with col_actors:
                attribute_select_active_characters = []
                if ui.checkbox("Are there active characters?",value=True):
                    # Single/Multi Character Handling
                    if len(mem.turn_track.loc[mem.turn_track['group']==mem.current_turn,'name']) > 1 :
                        active_characters = ui.multiselect("Active Character(s)", options=mem.turn_track.loc[mem.turn_track['group']==mem.current_turn,'name'])
                    elif len(mem.turn_track.loc[mem.turn_track['group']==mem.current_turn,'name']) == 1  :
                        active_characters = [mem.turn_track.loc[mem.turn_track['group']==mem.current_turn,'name'].values[0]]
                    else : # Error catch, "should" never happen
                        ui.write("It is no one's turn!")
                    # Attribute specifications
                    if ui.checkbox("Specify Attributes?",key="active_characters_specify"):
                        attribute_select_active_characters = ui.multiselect("Select Attributes",
                            options = attributes_list(current_group[current_group['name'].isin(active_characters)])
                        )
                else :
                    active_characters = ui.text_area(f'What is causing the action?')
            # Action
            with col_action:
                if ui.checkbox("Standard Action",value=True):
                    action_subject = ui.selectbox("Action Type", options=mem.audit_actions.keys())
                    action = ui.multiselect(f"{action_subject} Submenu", options=mem.audit_actions[action_subject])
                else :
                    action = ui.text_area('What occured?')
            # Target Character
            with col_target:
                attribute_select_target_characters = []
                if ui.checkbox("Are there target characters?",value=True):
                    # Multi Character Handling Only
                    target_characters = ui.multiselect("Target Character(s)", options=mem.turn_track['name'])
                    # Attribute specifications
                    if ui.checkbox("Specify Attributes?",key="target_characters_specify"):
                        attribute_select_target_characters = ui.multiselect("Select Attributes",
                            options = attributes_list(mem.turn_track[mem.turn_track['name'].isin(target_characters)])
                        )
                else :
                    target_characters = ui.text_area(f'What occured with the {action}')
            with col_execute:
                attribute_environment = ui.selectbox("Environment Information", options=mem.audit_tags['Environment'])
                outcome = ui.selectbox("Outcome",options=mem.audit_outcome['Outcome'])
                results = ui.multiselect("Result",options=mem.audit_outcome['Results'])
                # Writes list of confirmed actions
                ui.write(f'Confirmed Actions: {mem.results_data}')
                if ui.button("Submit Action"):
                    # creates an additional log, submits action and adds to audit
                    additional_log = ""
                    mem.turn_track, mem.current_turn, additional_log, damage, healing = submit_action(mem.turn_track,mem.current_turn,mem.results_data,additional_log)
                    if mem.audit_combat : add_audit(mem.audit,
                        mem.turn_number,mem.action_number, # turn, action_number
                        action, # action
                        results, # result
                        target_characters, # target
                        attribute_select_target_characters, # target_additional_info
                        active_characters, # source
                        attribute_select_active_characters, # source_additional_info
                        attribute_environment, # environment
                        damage, # damage
                        healing, # healing
                        additional_log # additional_effects
                        )
                    mem.results_data = []
                    mem.action_number += 1
            ui.markdown("---")
            # Dynamic Flavor Data handling
            if results != None :
                for result in results :
                    ui.markdown(f"### {result}")
                    col_result_data, col_result_target = ui.columns(2)
                    if has_flavor(result,mem.flavor_lookup):
                        flavor = mem.flavor_lookup[result]
                        with col_result_data:
                            # Fills mod_data with correct input depending on need
                            mod_data = ui.empty()
                            if flavor["modification"] in ['-','+']:
                                mod_data = []
                                mod_characters = ui.multiselect(f"Characters {result}",options=active_characters,key=f'data_characters_{result}')
                                for character in mod_characters:
                                    mod_data.append([character,ui.number_input(f'{character} {result}',value=0,key=f'data_number_{character}_{result}')])
                            elif flavor["modification"] == 'attribute':
                                mod_data = ui.multiselect(f'Attribute {flavor["wording"]}',options=attribute_select_active_characters,key=f'data_attribute_{result}')
                            elif flavor["modification"] == 'condition':
                                mod_data = ui.multiselect(f'Condition {flavor["wording"]}',options=mem.audit_tags['Condition'],key=f'data_condition_{result}')
                            elif flavor["modification"] == 'info':
                                mod_data = ui.text_area(flavor["wording"],key=f'data_info_{result}')
                            elif flavor["modification"] == 'disrupt':
                                mod_data = ui.selectbox("Who is Disrupting (can only be one)",options=active_characters,key=f'data_disrupt_{result}')
                        with col_result_target:
                            # Fills target_data with correct input depending on need
                            target_data = ui.empty()
                            if flavor["target"] == 'self' : target_data = active_characters
                            elif flavor["target"] == 'target':
                                if type(active_characters)==str : targets = target_characters
                                elif type(target_characters)==str : targets = active_characters
                                else : targets = active_characters + target_characters
                                target_data = ui.multiselect("Specific Target(s)",options=targets,key=f'target_specifics_{result}')
                            elif (flavor["target"] == 'target_group') and (flavor["modification"] == 'disrupt'):
                                # Disrupt handling
                                action_group_to_split = ui.selectbox("Select Group to Disrupt",
                                                            options=multi_person_groups_list(mem.turn_track),
                                                            key=f'target_group_{result}')
                                if(action_group_to_split!=None):
                                    action_group_to_split_1st = ui.text_input("First Half Name",value=f"{action_group_to_split} 1",key=f'target_name1_{result}')
                                    action_group_to_split_2nd = ui.text_input("Second Half Name",value=f"{action_group_to_split} 2",key=f'target_name2_{result}')
                                    action_group_to_split_df = df_match_slice(mem.turn_track,"group",action_group_to_split)
                                    action_split_decicions = []
                                    ui.write("Where is:")
                                    for member in action_group_to_split_df['name']:
                                        action_split_decicions.append(ui.select_slider(member,
                                            options=[action_group_to_split_1st,action_group_to_split_2nd],key=f'target_{member}_{result}'
                                        ))
                                target_data = [action_group_to_split,action_group_to_split_1st,action_split_decicions,action_group_to_split_2nd]
                            elif (flavor["target"] == 'target_group'):
                                # Target group handling
                                target_data = ui.selectbox("Select Group",options=groups_list(mem.turn_track),key=f'target_group_{result}')
                            if ui.button(f"Confirm Result - {result}"):
                                mem.results_data.append([
                                    flavor["modification"],
                                    mod_data,
                                    target_data
                                ])
                        ui.markdown("---")