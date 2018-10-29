import random


def get_random_part(inning_data, summary, samples_count=2, min_overs=10):
    sub_innings = []
    total_runs = []
    sub_innings_total = []
    inn_total_runs = summary[0]
    inn_total_overs = len(inning_data)
    if inn_total_overs <= min_overs:
        return None
    for _ in range(samples_count):
        cut = random.randint(min_overs, inn_total_overs)
        sub_inning = inning_data[:cut]
        sub_innings.append(sub_inning + [[0, 0]] * (50 - len(sub_inning)))
        total_runs.append(inn_total_runs)
        sub_innings_total.append(sum(map(lambda x: x[0], sub_inning)))
    return sub_innings, total_runs, sub_innings_total
