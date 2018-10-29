import os
import yaml


def get_match_data(match_dir, match_file):
    match_id = match_file.split('.')[0]
    with open(os.path.join(match_dir, match_file)) as match_f:
        match_data = yaml.load(match_f)
        inn1_deliveries = map(get_delivery_data, match_data['innings'][0].values()[0]['deliveries'])
        inn1_insert_values = map(lambda x: get_insert_value_str([match_id, 1] + x), inn1_deliveries)
        inn2_deliveries = map(get_delivery_data, match_data['innings'][1].values()[0]['deliveries'])
        inn2_insert_values = map(lambda x: get_insert_value_str([match_id, 2] + x), inn2_deliveries)
        insert_value_str = ','.join(inn1_insert_values + inn2_insert_values)
        return "INSERT INTO deliveries(match_id, inning, delivery, batsman, bowler, non_striker, bat_runs, total_runs, out, out_type) VALUES " + insert_value_str


def get_delivery_data(delivery_json):
    ball = delivery_json.keys()[0]
    d_values = delivery_json.values()[0]
    bat_runs = d_values['runs']['batsman']
    total_runs = d_values['runs']['total']
    batsman = d_values['batsman']
    bowler = d_values['bowler']
    non_striker = d_values['non_striker']
    out = d_values['wicket']['player_out'] if 'wicket' in d_values else 'NULL'
    out_type = d_values['wicket']['kind'] if 'wicket' in d_values else 'NULL'
    return [ball, batsman, bowler, non_striker, bat_runs, total_runs, out, out_type]


def get_insert_value_str(delivery_vals):
    return "('%s',%d,%.1f,'%s','%s','%s',%d,%d,%s,%s)" % tuple(delivery_vals)


insert_sql = get_match_data("data/prediction/test/", "225247.yaml")
print insert_sql
