# Imports
import pandas as pd

#####################################
########## Cross functions ##########
#####################################
from functions.characters import roll, adjust_health, add_additional_info
from functions.data import col_list_every_action, col_str_every_action
from functions.groups import  disrupt

####################################
########## Game Functions ##########
####################################
def sort_by_initiatives(groups:pd.DataFrame):
    df = groups.copy()
    df['total_initiative'] = df['initiative']+df['initiative_bonus']
    df.sort_values(by='total_initiative',ascending=False,inplace=True)
    return df.drop(columns="total_initiative")

def initiative_based_group_assignment(groups:pd.DataFrame):
    df = sort_by_initiatives(groups)
    df_count = {}
    team_order = df['team']
    group_placement = []
    lastTeam = None
    for team in team_order:
        if team != lastTeam :
            if team in df_count.keys() :
                df_count[team]+=1
            else :
                df_count[team]=1
            lastTeam = team
        group_placement.append(f"{team} {df_count[team]}")
    df['group']=group_placement
    return df

def auto_initiative(groups:pd.DataFrame):
    df = groups.copy()
    df['initiative'] = df['initiative'].apply(lambda x: roll(20))
    return df

def next_turn(groups:pd.DataFrame,current_turn):
    groups.reset_index(drop=True,inplace=True)
    current_turns_last_index=groups[groups['group']==current_turn].index[-1]
    if current_turns_last_index == len(groups)-1 : #loop around detection
        return groups.iloc[0]['group']
    else:
        return groups.iloc[current_turns_last_index+1]['group']

def previous_turn(groups:pd.DataFrame,current_turn):
    groups.reset_index(drop=True,inplace=True)
    current_turns_last_index=groups[groups['group']==current_turn].index[0]
    if current_turns_last_index == 0 : #loop around detection
        return groups.iloc[-1]['group']
    else:
        return groups.iloc[current_turns_last_index-1]['group']

def add_audit(audit_trail:pd.DataFrame,turn,action_number,action,result,target,target_additional_info,source,source_additional_info,environment,damage,healing,additional_effects):
    audit_trail.loc[len(audit_trail.index)] = [
        turn, action_number,
        action,
        result,
        target,
        target_additional_info,
        source,
        source_additional_info,
        environment,
        damage,
        healing,
        additional_effects
    ]

def add_audit_note(audit_trail:pd.DataFrame,turn,action_number,note):
    add_audit(audit_trail,turn,action_number,"","","","","","","","","",note)
def add_audit_character_note(audit_trail:pd.DataFrame,turn,action_number,character,note):
    add_audit(audit_trail,turn,action_number,character,"","","","","","","","",note)

def audit_every_action_df(audit:pd.DataFrame):
    action_df = audit.copy()[["turn","action_number","damage","healing","additional_effects"]]
    concat_list = []
    if not all(action_df['damage'].isin(["",[]])) : concat_list.append(col_list_every_action(action_df,'damage',['healing','additional_effects']))
    if not all(action_df['healing'].isin(["",[]])) : concat_list.append(col_list_every_action(action_df,'healing',['damage','additional_effects']))
    if not all(action_df['additional_effects'].isin(["",[]])) : concat_list.append(col_str_every_action(action_df,'additional_effects',['damage','healing']))
    
    if len(concat_list) : return pd.concat(concat_list,ignore_index=True).sort_values(by=["turn","action_number"])
    return pd.DataFrame(columns=['turn','action_number','source','damage','healing','additional_effects'])


def submit_action(turn_track,current_turn,results_data,additional_log):
    damage = []
    healing = []
    for result in results_data:
        if result[0] in ['+','-'] : adjust_health(turn_track,result[0],result[1],result[2])
        elif result[0] in ['attribute','condition','info'] :
            if additional_log != "" : additional_log += '\n'
            additional_log += add_additional_info(result)
        elif result[0] == 'disrupt' :
            if len(turn_track[turn_track['group']==current_turn]) == 1 : 
                current_turn = next_turn(turn_track,current_turn)
            turn_track = disrupt(turn_track,result[1],result[2])

        if result[0] == '-' : damage.append([result[1],result[2]])
        elif result[0] == '+' : healing.append([result[1],result[2]])
    return turn_track, current_turn, additional_log, damage, healing