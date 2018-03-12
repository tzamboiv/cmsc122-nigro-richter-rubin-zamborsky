from points_of_interest import time_to_dest
import math

WEIGHTS = {
    "low": 2,
    "medium": 1,
    "high": 0.5
}

def best_travel_options(address_1, address_2, transit_inputs):
    '''
    Computes best and second best travel option between two addresses
    '''
    travel_times = time_to_dest(adress_1, address_2, transit_inputs)
    adjusted_times = [WEIGHTS[type] * travel_times["type"] for type in travel_times]
    best_time = math.inf
    second_time = math.inf
    best = None
    second = None
    for transit_type, time in adjusted_times.items():
        if time < best_time:
            second_time = best
            second = best
            best_time = time
            best = transit_type
        elif time < second_time:
            second_time = time
            second = transit_type
    return [("best", "best_time"), ("second", "second_time")]


def compute_initial_score(address_1, address_2, transit_inputs):
    '''
    Computes initial rating score for two addresses
    '''
    best_options = best_travel_options(address_1, address_2, transit_inputs)
    
    total_score = math.log(best_options[0][1]) + 0.5 * math.exp(best_options[1][1])
    return total_score