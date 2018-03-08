import math

# Transit Types
WALKING = "walking"
DRIVING = "driving"
CTA = "cta"
BIKING = "bicycling"
DIVVY = "divvy"
SHUTTLE = "suhttles"

# Ratings
HIGH = "high"
MED = "med"
LOW = "low"
NONE = "none"

# CTA Destination Coding
UC = 8 # uChicago
HP = 4 # Hyde park
DT = 2 # Downtown
SS = 1 # South side
CTA_CLASSIFICATION = {
    2: DT + HP,
    3: DT + SS,
    4: DT + SS,
    6: DT + HP + SS,
    15: HP + SS,
    28: HP + SS,
    29: DT + SS,
    30: SS,
    47: HP,
    55: HP + SS,
    59: SS,
    63: SS,
    67: SS,
    71: SS,
    95: 0,
    169: 0,
    171: UC,
    172: UC,
    192: DT
}

def cta_goes_to_destination(cta_route, destination_code):
    classifier = CTA_CLASSIFICATION[cta_route]
    bit_place = int(math.log(destination_code, 2))
    return ((classifier & (1 << bit_place)) != 0)

def normalized_location_rating(walking_times_dict, cta_pref, south_side):
    '''
    Produce a rating for a specific address based on its proximity to cta stops, divvy stops, and shuttle stops
    '''
    # Extract user-given importance for each travel_type
    importances = {}
    for travel_type, travel_type_dict in walking_times_dict.items():
        example_entry = next(iter(travel_type_dict.values()))
        importances[travel_type] = example_entry["ranking"]
    
    # Calculate a rating for each travel_type
    ratings = {
        CTA: cta_proximity_rating(walking_times_dict[CTA], cta_pref),
        DIVVY: divvy_proximity_rating(walking_times_dict[DIVVY]),
        SHUTTLE: shuttle_proximity_rating(walking_times_dict[SHUTTLE])
    }
    
    # Calculate an overall proximity rating for this address
    raw_rating = 0
    weights = []
    weightings = {
        HIGH: 4,
        MED: 2,
        LOW: 1,
        NONE: 0
    }
    for travel_type in [CTA, DIVVY, SHUTTLE]:
        weight = weightings[importances[travel_type]]
        weights.append(weight)
        raw_rating += ratings[travel_type] * weight 
    
    # Normalize this rating
    normalization_const = sum(weights) / len(weights)
    return raw_rating / (normalization_const if normalization_const > 0 else 1)
  
def cta_proximity_rating(cta_travel_times_dict, cta_pref, south_side):
    '''
    TODO: Change the route sorting to be in a separate function that is only run once
    '''
    # Sort all routes based on their destination
    destinations = [HP, DT, SS, UC]
    sorted_routes = { dest:{} for dest in destinations }
    for route, route_info in cta_travel_times_dict.items():
        for dest in destinations:
            if cta_goes_to_destintation(route, dest):
                sorted_routes[dest][route] = route_info
    
    # Find closest routes for each destination
    for dest in destinations:
        
    
def divvy_proximity_rating(divvy_travel_times_dict):
    '''
    Generate a rating for this address' proximity to divvy stations
    '''
    stops, times = find_closest_routes(divvy_travel_times_dict)
    weights = [4, 1] # Should be a list of 2 numbers
    raw_rating = sum(
        [time * weight for time, weight in zip(closest_stop_times, weights)]
    )
    normalized_rating = raw_rating / sum(weights)
    return normalized_rating

def find_closest_routes(travel_times_dict):
    '''
    Given a dict mapping route names (or site names, for divvy bikes) to dicts
    containing travel times, finds the two closest stops and the time to each. 
    Returns a tuple of lists: (stops, times).
    
    TODO: Make this work for arbitrary number of stops (not just 2)
    '''
    # Determine the relevant stops and their related times
    num_stops_to_include = 2
    # The first element in the list is the closest stop, etc.
    closest_stops = [None] * num_stops_to_include
    closest_stop_times = [math.inf] * num_stops_to_include
    for divvy_stop, stop_dict in divvy_travel_times_dict.items():
        time = stop_dict["time"]
        if time < closest_stop_times[0]:
            # New closest stop
            closest_stop_times[1] = closest_stop_times[0]
            closest_stops[1] = closest_stops[0]
            closest_stop_times[0] = time
            closest_stops[0] = divvy_stop
        elif time < closest_stop_times[1]:
            # New second-closest stop
            closest_stop_times[1] = time
            closest_stops[1] = divvy_stop
    return (closest_stops, closest_stop_times)
    

def shuttle_proximity_rating(shuttle_travel_times_dict):
    pass

def cta_hours(cta_line_name):
    pass

def shuttle_hours(shuttle_name):
    pass

def normalized_rating_for_poi(poi_dict):
    '''
    Takes a dict for a specific POI and returns a rating for that POI
    '''
    ratings = {}
    for travel_type in poi_dict:
         ratings[travel_type] = poi_dict[travel_type]["time"]
    
