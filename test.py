# Imports
import pandas as pd

def process_audit(df:pd.DataFrame):
    df = df.set_index("Audit Header").transpose().reset_index(drop=True)
    audit_out = {}
    for col in df.columns : audit_out[col] = df[col].dropna().to_list()
    return audit_out

def csv_read_audit(path):
    audit_read = pd.read_csv(path)

    audit_tags = audit_read[audit_read['Audit Header'].str.contains('tags_')].reset_index(drop=True)
    audit_out = audit_read[audit_read['Audit Header'].str.contains('out_')].reset_index(drop=True)
    audit_meta = audit_read[audit_read['Audit Header'].str.contains('meta_')].reset_index(drop=True)
    
    audit_actions = audit_read.drop(index=audit_read[audit_read['Audit Header'].str.contains('tags_')].index)
    audit_actions = audit_actions.drop(index=audit_read[audit_read['Audit Header'].str.contains('out_')].index)
    audit_actions = audit_actions.drop(index=audit_read[audit_read['Audit Header'].str.contains('meta_')].index)

    audit_actions.reset_index(drop=True,inplace=True)

    audit_tags['Audit Header'] = audit_tags['Audit Header'].str[5:]
    audit_out['Audit Header'] = audit_out['Audit Header'].str[4:]
    audit_meta['Audit Header'] = audit_meta['Audit Header'].str[5:]
        
    print(process_audit(audit_actions))
    return process_audit(audit_actions), process_audit(audit_out), process_audit(audit_tags), process_audit(audit_meta)

def txt_read_audit(path):
    audit_tags = {}
    audit_out = {}
    audit_flavor = {}
    audit_actions = {}

    with open(path, 'r') as file:
        for data_line in file:
            audit_list = data_line.strip().split(',')
            key = audit_list[0]
            if key == 'Tags':
                audit_tags[audit_list[1]] = audit_list[2:]
            elif key == 'Out':
                audit_out[audit_list[1]] = audit_list[2:]
            elif key == 'Flavor':
                audit_flavor[audit_list[1]] = audit_list[2:]
            else:
                audit_actions[audit_list[1]] = audit_list[2:]

    print(audit_actions)
    return audit_actions, audit_out, audit_tags, audit_flavor


csv_read_audit("assets\data\default_audit_actions.csv")
txt_read_audit("assets\data\default_form_data.txt")