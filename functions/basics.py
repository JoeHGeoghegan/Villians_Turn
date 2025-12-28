# Imports
import pandas as pd
from nicegui import app, ui


def dict_to_df(data:dict):
    """Convert dict or list of dicts to DataFrame"""
    if isinstance(data, dict):
        return pd.DataFrame([data])
    return pd.DataFrame(data).dropna(how='all')


def df_to_dict(df: pd.DataFrame):
    return df.to_dict(orient='records')


def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')


def mem_df_modify(df_name: str, func, *args):
    mem = app.storage.general
    df = dict_to_df(mem[df_name])
    df = func(df, *args)
    mem[df_name] = df_to_dict(df)


def mem_df_use(df_name: str, func, *args):
    mem = app.storage.general
    df = dict_to_df(mem[df_name])
    return func(df, *args)


def df_match_slice(df: pd.DataFrame, column, match):
    return df[df[column] == match]


def df_set_slice(df: pd.DataFrame, column, match, new_data):
    df_slice = df[df[column] == match].copy()
    df_slice[column] = new_data
    df_copy = df.copy()
    df_copy.update(df_slice)
    return df_copy


def split_column_list(df, column_name, new_axis_names):
    df_split = df.copy()
    df_split.drop(df[df[column_name].isin(["", []])].index, inplace=True)
    df_split[new_axis_names] = pd.DataFrame(df_split[column_name].to_list(), columns=new_axis_names,
                                            index=df_split.index)
    df_split.drop(columns=column_name, inplace=True)
    return df_split

def list_oxford(things_to_string):
    output = ""
    length = len(things_to_string)
    if length == 1:
        return things_to_string[0]
    elif length == 2:
        return f"{things_to_string[0]} and {things_to_string[1]}"
    else:
        for index, thing in enumerate(things_to_string):
            if index == 0:
                # First value
                output = f"{thing}"
            elif index != length - 1:
                # Action for all other values
                output += f", {thing}"
            else:
                # last value
                output += f", and {thing}"

    return output