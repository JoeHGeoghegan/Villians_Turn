# Imports
import pandas as pd

def read_flavor(path):
    output = {}
    with open(path, 'r', encoding='utf-8-sig') as file:
        for flavor in file:
            flavor_list = flavor.strip().split(',')
            if flavor_list[0] not in output.keys():
                output[flavor_list[0]] = [{
                    "target" : flavor_list[1],
                    "modification" : flavor_list[2],
                    "wording" : flavor_list[3]
                }]
            else:
                output[flavor_list[0]].append( [{
                    "target" : flavor_list[1],
                    "modification" : flavor_list[2],
                    "wording" : flavor_list[3]
                }] )
    return output

def parse_meta_str(meta):
    meta_list = meta.strip('][').split(',')
    output = {}
    output["target"] = meta_list[1]
    output["modification"] = meta_list[2]
    output["wording"] = meta_list[3]
    return meta_list[0],output

def meta_to_dict(audit_meta,key='Results'):
    output = {}
    for meta in audit_meta[key]:
        parse_name, parse_dict = parse_meta_str(meta)
        output[parse_name] = parse_dict
    return output

def read_audit(path):
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
    
    return process_audit(audit_actions), process_audit(audit_out), process_audit(audit_tags), process_audit(audit_meta)

def process_audit(df:pd.DataFrame):
    df = df.set_index("Audit Header").transpose().reset_index(drop=True)
    audit_out = {}
    for col in df.columns : audit_out[col] = df[col].dropna().to_list()
    return audit_out

print(read_flavor("assets\\data\\default_flavor_data.csv"))
audit_actions, audit_out ,audit_tags, audit_meta = read_audit("Streamlit Implementation\\data\\default_audit_actions.csv")
print(meta_to_dict(audit_meta))