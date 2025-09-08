# Imports
import pandas as pd
from nicegui import ui, app

def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

def df_match_slice(df:pd.DataFrame,column,match):
    return df[df[column]==match]

def df_set_slice(df:pd.DataFrame,column,match,new_data):
    df_slice = df[df[column] == match].copy()
    df_slice[column] = new_data
    df_copy = df.copy()
    df_copy.update(df_slice)
    return df_copy

def split_column_list(df,column_name,new_axis_names):
    df[new_axis_names] = pd.DataFrame(df[column_name].to_list(),index=df.index)
    df.drop(columns=column_name,inplace=True)

    
def split_column_list(df,column_name,new_axis_names):
    df_split = df.copy()
    df_split.drop(df[df[column_name].isin(["",[]])].index,inplace=True)
    df_split[new_axis_names] = pd.DataFrame(df_split[column_name].to_list(),columns=new_axis_names,index=df_split.index)
    df_split.drop(columns=column_name,inplace=True)
    return df_split

def mem_df_inplace(df_name:str, func=df_match_slice, *args, **kwargs):
    mem = app.storage.tab
    mem[df_name] = func(mem[df_name], *args, **kwargs)