# Imports
import pandas as pd
import numpy as np

#####################################
########## Cross functions ##########
#####################################
from functions.basics import df_set_slice

#####################################
########## Group Functions ##########
#####################################
def groups_list(turn_track:pd.DataFrame):
    return(turn_track['group'].unique())

def person_is_alone(groups:pd.DataFrame,person):
    group_name = groups[groups['name'] == person]['group'].values[0]
    return len(groups[groups['group']==group_name]) == 1

def multi_person_groups_list(groups):
    multi_person_groups_mask = [len(groups[groups['group']==x]) != 1 for x in groups['group'].unique()]
    multi_person_groups = groups['group'].unique()[multi_person_groups_mask]
    return multi_person_groups

def groups_gathered_check(groups:pd.DataFrame):
    order_list = groups_list(groups)
    team_changes = groups["group"].shift() != groups["group"]
    return len(team_changes[team_changes==True])==len(order_list)

def remove_group_assignments(groups:pd.DataFrame):
    df = groups.copy()
    df['group']=np.nan
    return df

def individual_groups(groups:pd.DataFrame):
    df = groups.copy()
    df['group']=df['name']
    return df

def group_in_place(groups:pd.DataFrame):
    df = groups.copy()
    for group_name in df['group'].unique():
        group_mask = df['group'] == group_name

        #If there is only one subgroup of this grouping, we can skip the below logic
        if ((df['group'].shift(1) != df['group']) & group_mask).sum() == 1:
            continue

        # Renames all subgroups to unique values by appending a number to the end
        index = 0
        subgroup_number = 1
        matching_group=False
        for mask in group_mask:
            if mask:
                df.loc[index,'group'] = f"{group_name} {subgroup_number}"
                matching_group=True
            else:
                if matching_group:
                    subgroup_number+=1
                    matching_group=False
            index+=1
    return df

def move_group(groups:pd.DataFrame,group_to_move,before_or_after,group_to_place):
    df = groups.copy()
    df.reset_index(drop=True,inplace=True)
    slice_group_to_move = df[df['group']==group_to_move].copy()
    df.drop(slice_group_to_move.index,inplace=True)
    df.reset_index(drop=True,inplace=True)
    slice_group_to_move.reset_index(drop=True,inplace=True)
    if before_or_after == "Before" :
        index_split_point = (df[df['group']==group_to_place].index[0]) #first index
    else :
        index_split_point = df[df['group']==group_to_place].index[-1]+1 #last index
    return pd.concat([df.iloc[:index_split_point],slice_group_to_move,df.iloc[index_split_point:]]).reset_index(drop=True)

def move_character(groups:pd.DataFrame,person_to_move,destination_group):
    df = groups.copy()
    df.reset_index(drop=True,inplace=True)
    slice_character_to_move = df[df['name']==person_to_move].copy()
    slice_character_to_move['group']=destination_group
    df.drop(slice_character_to_move.index,inplace=True)
    index_split_point = df[df['group']==destination_group].index[-1] #last index
    return pd.concat([df.iloc[:index_split_point],slice_character_to_move,df.iloc[index_split_point:]]).reset_index(drop=True)

def move_character_to_new_group(groups:pd.DataFrame,person_to_move,new_group_name):
    df = groups.copy()
    old_group=df.loc[(df["name"]==person_to_move,"group")].values[0]
    df.loc[(df["name"]==person_to_move,"group")]=new_group_name
    if df[df['group']==old_group].empty :
        return df # If character was the only member of a group, no need to rearrange
    return move_group(df,new_group_name,"After",old_group)

def merge_groups(groups:pd.DataFrame,merge_group_1,merge_group_2,merged_name):
    df = groups.copy()
    df = move_group(df,merge_group_1,"After",merge_group_2)
    df['group'].replace([merge_group_1,merge_group_2],[merged_name,merged_name],inplace=True)
    return df

def disrupt(turn_track,disruptor,disrupted_info):
    print(disrupted_info)
    group_to_split = disrupted_info[0]
    group_name_1 = disrupted_info[1]
    split_decicions = disrupted_info[2]
    group_name_2 = disrupted_info[3]
    turn_track = df_set_slice(turn_track,"group",group_to_split,split_decicions)
    if not person_is_alone(turn_track,disruptor) :
        turn_track = move_character_to_new_group(turn_track, disruptor, disruptor)
    else :
        turn_track.loc[turn_track['name']==disruptor,'group']=disruptor
    turn_track = move_group(turn_track,disruptor,"After",group_name_1)
    turn_track = move_group(turn_track,group_name_2,"After",disruptor)
    return turn_track
