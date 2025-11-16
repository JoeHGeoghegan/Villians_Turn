## Local Imports
from functions.basics import df_set_slice
from functions.game import set_turn
from functions.groups import move_character_to_new_group, move_group, person_is_alone


def submit_action(turn_track, current_turn, results_data, additional_log):
    damage = []
    healing = []
    for result in results_data:
        if result[0] in ['+', '-']:
            adjust_health(turn_track, result[0], result[1], result[2])
        elif result[0] in ['attribute', 'condition', 'info']:
            if additional_log != "": additional_log += '\n'
            additional_log += add_additional_info(result)
        elif result[0] == 'disrupt':
            if len(turn_track[turn_track['group'] == current_turn]) == 1:
                current_turn = set_turn(turn_track, current_turn, 1, "go to")
            turn_track = disrupt(turn_track, result[1], result[2])

        if result[0] == '-':
            damage.append([result[1], result[2]])
        elif result[0] == '+':
            healing.append([result[1], result[2]])
    return turn_track, current_turn, additional_log, damage, healing


def adjust_health(turn_track, is_damage, numbers, target):
    health_mod = 1
    if is_damage == "-": health_mod = -1
    for number in numbers:
        value = number[1]
        turn_track.loc[turn_track['name'].isin(target), 'health'] += (health_mod * value)


def add_additional_info(result):
    return f'{result[0]} -> {result[2]} : {result[1]}'


def disrupt(turn_track, disruptor, disrupted_info):
    print(disrupted_info)
    group_to_split = disrupted_info[0]
    group_name_1 = disrupted_info[1]
    split_decisions = disrupted_info[2]
    group_name_2 = disrupted_info[3]
    turn_track = df_set_slice(turn_track, "group", group_to_split, split_decisions)
    if not person_is_alone(turn_track, disruptor):
        turn_track = move_character_to_new_group(turn_track, disruptor, disruptor)
    else:
        turn_track.loc[turn_track['name'] == disruptor, 'group'] = disruptor
    turn_track = move_group(turn_track, disruptor, "After", group_name_1)
    turn_track = move_group(turn_track, group_name_2, "After", disruptor)
    return turn_track
