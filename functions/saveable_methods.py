import re
import pandas as pd
def lookup_method(method_str):
    if method_str == "health_full_detail":
        return health_full_detail, ['health','temporary_health','max_health']
    elif method_str == "health_curr_total":
        return health_curr_total, ['health','temporary_health','max_health']
    elif method_str == "health_hp_and_max":
        return health_hp_and_max, ['health','temporary_health','max_health']
    elif method_str == "health_pct":
        return health_pct, ['health','temporary_health','max_health']
    elif method_str == "health_vague":
        return health_vague, ['health','temporary_health','max_health']
    elif method_str == "armor_full_detail":
        return armor_full_detail, ['armor_class','ac_mod']
    elif method_str == "armor_total":
        return armor_total, ['armor_class','ac_mod']
    else:
        raise ValueError(f"Unknown method string: {method_str}")
    
def health_full_detail(df_slice:pd.DataFrame,showSet=True): #['health','temporary_health','max_health']
    def handle_row(row):
        if type(row['temporary_health']) == str:
            if row['temporary_health'].startswith('SET'):
                if showSet:
                    return f"{row['health']}/{re.findall(r'\d+', row['temporary_health'])}"
                else:
                    return f"{row['health']}/{"".join(filter(str.isdigit, row['temporary_health']))}"
        return f"({row['health']}+{row['temporary_health']})/{row['max_health']}"
    return df_slice.apply(
        lambda row : handle_row(row),
        axis=1
    )

def health_curr_total(df_slice): #['health','temporary_health','max_health']
    def handle_row(row):
        if type(row['temporary_health']) == str:
            if row['temporary_health'].startswith('SET'):
                return df_slice['health']
        return df_slice['health'] + df_slice['temporary_health']
    return df_slice.apply(
        lambda row : handle_row(row),
        axis=1
    )

def health_hp_and_max(df_slice,showSet=True): #['health','temporary_health','max_health']
    def handle_row(row):
        if type(row['temporary_health']) == str:
            if row['temporary_health'].startswith('SET'):
                if showSet:
                    return f"{row['health']}/*{re.findall(r'\d+', row['temporary_health'])}*"
                else:
                    return f"{row['health']}/{"".join(filter(str.isdigit, row['temporary_health']))}"
        return f"{df_slice['hp_curr']+df_slice['hp_temp']}/{df_slice['hp_max']}"
    return df_slice.apply(
        lambda row : handle_row(row),
        axis=1
    )

def health_pct(df_slice): #['health','temporary_health','max_health']
    def handle_row(row):
        if type(row['temporary_health']) == str:
            if row['temporary_health'].startswith('SET'):
                return "???" if (re.findall(r'\d+', row['temporary_health']) == 0) else f"{(df_slice['hp_curr'])/re.findall(r'\d+', row['temporary_health'])*100:.0f}%"
        return "???" if (df_slice['hp_max'] == 0) else f"{(df_slice['hp_curr']+df_slice['hp_temp'])/df_slice['hp_max']*100:.0f}%"
    return df_slice.apply(
        lambda row : handle_row(row),
        axis=1
    )

def health_vague(df_slice): #['health','temporary_health','max_health']
    def vague(row):
        hp_curr = int(row['health'])
        hp_temp = row['temporary_health']
        hp_max = int(row['max_health'])
        if type(row['temporary_health']) == str:
            if hp_temp.startswith('SET'):
                hp_max = int("".join(filter(str.isdigit, row['temporary_health'])))
                hp_temp = 0
        if hp_max == 0 : return "???"
        hp_temp = int(hp_temp)
        pct = (hp_curr+hp_temp)/hp_max*100
        if pct >= 100 : return "Healthy"
        elif pct >= 90 : return "Fine"
        elif pct >= 75 : return "Lightly Injured"
        elif pct >= 50 : return "Injured"
        elif pct >= 25 : return "Heavily Injured"
        elif pct > 0 : return "Near Death"
        else : return "Unconscious/Dead"
    return df_slice.apply(vague, axis=1)

def armor_full_detail(df_slice,showSet=False): #['armor_class','ac_mod']
    def handle_row(row):
        if type(row['ac_mod']) == str:
            if row['ac_mod'].startswith('SET'):
                if showSet:
                    return f"{re.findall(r'\d+', row['ac_mod'])}"
                else:
                    return f"{"".join(filter(str.isdigit, row['ac_mod']))}"
            else:
                return f"{row['armor_class']}+{row['ac_mod']}"
        else:
            return f"{row['armor_class']}+{row['ac_mod']}"
    return df_slice.apply(
        lambda row : handle_row(row),
        axis=1
    )
def armor_total(df_slice,showSet=True): #['armor_class','ac_mod']
    def handle_row(row):
        if type(row['ac_mod']) == str:
            if row['ac_mod'].startswith('SET'):
                if showSet:
                    return f"{re.findall(r'\d+', row['ac_mod'])}"
        return row['armor_class'] + row['ac_mod']
    return df_slice.apply(
        lambda row : handle_row(row),
        axis=1
    )