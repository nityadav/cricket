import yaml
import json
import os
from collections import defaultdict


def generate_match_data(data_dir, only_matches_with_results=True):
    """
    Generates match data.
    :param data_dir: 
    :param only_matches_with_results: 
    :return:
    """
    with open("config.json") as conf_f:
        config = json.load(conf_f)
    task_config = config["tasks"]["odi_prediction"]

    filenames = filter(lambda x: x.split('.')[-1] == task_config["file_type"], os.listdir(data_dir))
    for match_file in filenames:
        inn1, inn2, result, summary = get_match_data(os.path.join(data_dir, match_file), only_matches_with_results)
        url = task_config["cricinfo_url"] % match_file.split('.')[0]
        yield inn1, inn2, result, summary, url


def get_match_data(match_file_path, only_matches_with_results):
    with open(match_file_path) as match_f:
        match_data = yaml.load(match_f)
        match_winner = get_winner(match_data)
        if (only_matches_with_results and match_winner is not None) or not only_matches_with_results:
            rw_list1, summary1 = get_score_by_over(get_deliveries(match_data, 1))
            rw_list2, summary2 = get_score_by_over(get_deliveries(match_data, 2))
            return rw_list1, rw_list2, match_winner, [summary1, summary2]


def get_winner(match_data):
    """
    :param match_data: 
    :return: 0 if the team batting first wins, and 1 if the second batting team wins.
    """
    try:
        winner = match_data['info']['outcome']['winner']
        bat_first = match_data['innings'][0].values()[0]['team']
        bat_second = match_data['innings'][1].values()[0]['team']
        if bat_first == winner:
            return 0
        elif bat_second == winner:
            return 1
    except KeyError:
        return None


def get_deliveries(match_data, inning_num):
    """
    :param match_data: 
    :param inning_num: 1 or 2 for ODI
    :return: list of (delivery, run, wickets)
    """
    deliveries = []
    for delivery in match_data['innings'][inning_num - 1].values()[0]['deliveries']:
        deliveries.append(
            (delivery.keys()[0], delivery.values()[0]['runs']['total'], 1 if 'wicket' in delivery.values()[0] else 0))
    return deliveries


def get_score_by_over(deliveries_list):
    """
    With the list of deliveries in an innings, it compacts it by over.
    :param deliveries_list: 
    :return: list of runs and wickets in each over, (total_runs, total_wickets, total_deliveries)
    """
    total_deliveries = 0
    dd = defaultdict(list)
    for d in deliveries_list:
        over, ball = str(d[0]).split('.')
        dd[over].append((d[1], d[2]))
        if int(ball) <= 6:
            total_deliveries += 1
    rw_o = [(k, [sum(rw) for rw in zip(*dd[k])]) for k in dd.keys()]
    rw_sorted = map(lambda y: y[1], sorted(rw_o, key=lambda x: int(x[0])))
    total_runs, total_wickets = [sum(rw) for rw in zip(*rw_sorted)]
    return rw_sorted, [total_runs, total_wickets, total_deliveries]
