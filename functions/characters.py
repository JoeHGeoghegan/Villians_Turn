# Imports
import pandas as pd
import random
import ast

#########################################
########## Character Functions ##########
#########################################
def character_list(turn_track:pd.DataFrame):
    return(turn_track['name'].unique())

def team_list(turn_track:pd.DataFrame):
    return(turn_track['team'].unique())

def roll(sided=20):
    return random.randint(1,sided)

def attributes_list(groups:pd.DataFrame):
    df = groups[['name','attributes']].copy()
    df.dropna(inplace=True)
    all_attributes = []
    for index,character in df.iterrows():
        character_attributes = ast.literal_eval(character['attributes'])
        for key, values in character_attributes.items() :
            if type(values) == list :
                for item in values:
                    all_attributes.append(f"{character['name']} - {key} - {item}")
            else :
                all_attributes.append(f"{character['name']} - {key} - {values}")
    return all_attributes

def adjust_health(turn_track,is_damage,numbers,target):
    health_mod = 1
    if is_damage == "-" : health_mod = -1
    for number in numbers :
        value = number[1]
        turn_track.loc[turn_track['name'].isin(target),'health'] += (health_mod * value)

def add_additional_info(result):
    return f'{result[0]} -> {result[2]} : {result[1]}'