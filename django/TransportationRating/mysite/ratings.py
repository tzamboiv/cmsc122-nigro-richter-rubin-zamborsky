import math
import points_of_interest
import travel_times

# Transit Types
WALKING = "walking"
DRIVING = "driving"
CTA = "cta"
BIKING = "bicycling"
DIVVY = "divvy"
SHUTTLE = "shuttles"

# Ratings
HIGH = "high"
MED = "medium"
LOW = "low"
NONE = "none"

# CTA Prefs
HP_PREF = "hyde_park"
DT_PREF = "downtown"

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
    '''
    Checks if CTA does to destinate
    '''
    classifier = CTA_CLASSIFICATION[cta_route]
    bit_place = int(math.log(destination_code, 2))
    return ((classifier & (1 << bit_place)) != 0)

# ------- Main Function for Interfacing with UI -------- #

def compute_rankings(user_input):
    '''
    Computes the ranking of input dictionary
    '''
    # Extract information
    apartment_list = user_input[0] # List of apartment addresses
    poi_list = user_input[1] # List of points of interest
    transit_prefs = user_input[2] # Dictionary mapping transit types to preference
    cta_pref = user_input[3] # HP_PREF, DT_PREF, or neither
    south_side_str = user_input[4]
    south_side = (south_side_str.lower() == "yes") # Boolean
    
    # Perform Calculations
    address_ratings = [
        rating_for_address(
            address, poi_list, transit_prefs, cta_pref, south_side
        ) for address in apartment_list
    ]
    return {
        address: rating for address, rating in zip(apartment_list, address_ratings)
    }

# ------- Helper Functions ------- #

def weighted_average(nums, weights):
    '''
    Returns the weighted average of the numbers in nums, weighted based on the
    weights given in weights. This function is used to ensure that all the
    ratings are just heavily weighted averages of a lot of different travel times.
    '''
    return sum([n * weight for n, weight in zip(nums, weights)]) / sum(weights)


def rating_for_address(address, poi_list, transit_prefs, cta_pref, south_side):
    '''
    Calculate a rating for a given address.
    '''
    loc_rating = location_rating_for_address(address, transit_prefs, cta_pref, south_side)
    if poi_list:
        # Make sure poi_list is non-empty
        poi_rating = poi_rating_for_address(address, poi_list, transit_prefs)
        return 0.5 * loc_rating + 0.5 * poi_rating
    else:
        return loc_rating
    
            
def poi_rating_for_address(address, poi_list, transit_prefs):
    '''
    Computs poi rating for address
    '''
    weights = [1 / (idx + 1) for idx in range(len(poi_list))]
    poi_ratings = []
    for poi in poi_list:
        poi_dict = points_of_interest.go(address, poi, transit_prefs)
        poi_ratings.append(normalized_rating_for_poi(poi_dict))
    return weighted_average(poi_ratings, weights)
        
        
def location_rating_for_address(address, transit_prefs, cta_pref, south_side):
    '''
    Computes location rating for address
    '''
    walking_times_dict = travel_times.go(address, transit_prefs)
    return normalized_location_rating(walking_times_dict, cta_pref, south_side)


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
        CTA: cta_proximity_rating(walking_times_dict[CTA], cta_pref, south_side) if CTA in walking_times_dict else 0,
        DIVVY: divvy_proximity_rating(walking_times_dict[DIVVY]) if DIVVY in walking_times_dict else 0,
        SHUTTLE: shuttle_proximity_rating(walking_times_dict[SHUTTLE]) if SHUTTLE in walking_times_dict else 0
    }
    
    # Calculate an overall proximity rating for this address
    raw_rating = 0
    weights = []
    weightings = {
        HIGH: 4,
        MED: 2,
        LOW: 1
    }
    for travel_type in [ttype for ttype in [CTA, DIVVY, SHUTTLE] if ttype in walking_times_dict]:
        weight = weightings[importances[travel_type]]
        weights.append(weight)
        raw_rating += ratings[travel_type] * weight 
    
    # Normalize this rating
    normalization_const = sum(weights)
    return raw_rating / (normalization_const if normalization_const > 0 else 1)
  
def cta_proximity_rating(cta_travel_times_dict, cta_pref, south_side):
    '''
    Computes CTA proximity rating
    '''
    # Sort all routes based on their destination
    destinations = [HP, DT, SS, UC]
    sorted_routes = { dest:{} for dest in destinations }
    for route, route_info in cta_travel_times_dict.items():
        for dest in destinations:
            if cta_goes_to_destination(route, dest):
                sorted_routes[dest][route] = route_info
    
    # Find closest routes for each destination
    closest_routes = {}
    closest_route_times = {}
    for dest in destinations:
        routes, times = find_closest_routes(sorted_routes[dest])
        closest_routes[dest] = routes
        closest_route_times[dest] = times
    
    # Figure out weightings
    dest_weightings = {
        HP: 1,
        DT: 4,
        UC: 3,
        SS: 0
    } # Defaults
    if cta_pref == HP_PREF:
        dest_weightings[HP] = 2
        dest_weightings[UC] = 6
    elif cta_pref == DT_PREF:
        dest_weightings[DT] = 8
    if south_side:
        dest_weightings[SS] = 4
    route_weightings = [4, 1] # Should be list of 2 numbers
        
    # Calculate overall rating
    raw_rating = 0
    for dest in destinations:
        dest_rating = weighted_average(closest_route_times[dest], route_weightings)
        raw_rating += dest_rating * dest_weightings[dest]
    
    # Normalize this rating
    normalization_const = sum(dest_weightings.values())
    return raw_rating / (normalization_const if normalization_const > 0 else 1)
    
def divvy_proximity_rating(divvy_travel_times_dict):
    '''
    Generate a rating for this address' proximity to divvy stations
    '''
    stops, times = find_closest_routes(divvy_travel_times_dict)
    weights = [4, 1] # Should be a list of 2 numbers
    raw_rating = sum(
        [time * weight for time, weight in zip(times, weights)]
    )
    normalized_rating = raw_rating / sum(weights)
    return normalized_rating

def find_closest_routes(travel_times_dict):
    '''
    Given a dict mapping route names (or site names, for divvy bikes) to dicts
    containing travel times, finds the two closest stops and the time to each. 
    Returns a tuple of lists: (stops, times).
    
    '''
    # Determine the relevant stops and their related times
    num_routes_to_include = 2
    # The first element in the list is the closest stop, etc.
    closest_routes = [None] * num_routes_to_include
    closest_route_times = [math.inf] * num_routes_to_include
    for route, route_dict in travel_times_dict.items():
        time = route_dict["time"]
        if time < closest_route_times[0]:
            # New closest stop
            closest_route_times[1] = closest_route_times[0]
            closest_routes[1] = closest_routes[0]
            closest_route_times[0] = time
            closest_routes[0] = route
        elif time < closest_route_times[1]:
            # New second-closest stop
            closest_route_times[1] = time
            closest_routes[1] = route
    return (closest_routes, closest_route_times)
    

DAY_SHUTTLES = [
    "53rd Street Express",
    "Apostolic/Drexel", # Exclude Apostolic and Drexel independently
    "Campus Shuttle",
    "Friend Center/Metra",
    "Hyde Park Route",
    "Midway Route", # Exclude Midway Metra AM/PM independently
    "Polsky Express"
]
NIGHT_SHUTTLES = [
    "Central",
    "East",
    "North",
    "South",
    "Regents Express",
    "South Loop Shuttle"
]

def shuttle_proximity_rating(shuttle_travel_times_dict):
    '''
    Computes shuttle proximity rating
    '''
    day_shuttle_info = {}
    night_shuttle_info = {}
    for route in DAY_SHUTTLES:
        day_shuttle_info[route] = shuttle_travel_times_dict[route]
    for route in NIGHT_SHUTTLES:
        night_shuttle_info[route] = shuttle_travel_times_dict[route]
    day_routes, day_times = find_closest_routes(day_shuttle_info)
    night_routes, night_times = find_closest_routes(night_shuttle_info)
    first_second_weights = [3, 1] # Should be list of 2 numbers
    day_rating = weighted_average(day_times, first_second_weights)
    night_rating = weighted_average(night_times, first_second_weights)
    day_night_weights = [1, 2] # Day weight, Night weight
    return weighted_average([day_rating, night_rating], day_night_weights)
    

def normalized_rating_for_poi(poi_dict):
    '''
    Takes a dict for a specific POI and returns a rating for that POI
    
    TODO- Ignore travel types that won't be used when calculating the rating
    (because of some combination of weak preference and inconvenience)
    '''
    adjusted_ratings = {}
    for travel_type, tt_info in poi_dict.items():
        ranking = tt_info['ranking']
        time = tt_info['time']
        adjusted_ratings[travel_type] = {}
        adjusted_ratings[travel_type]['time'] = adjusted_rating_for_poi_travel_type(time, ranking)
    
    # Normalize the rating
    weights = [4, 1]
    travel_types, adjusted_times = find_closest_routes(adjusted_ratings)
    return weighted_average(adjusted_times, weights)
    
      
def adjusted_rating_for_poi_travel_type(time, ranking):
    '''
    Helper function for choosing the best form of transportation to a given POI
    based on the user's preferences.
    '''
    offset1 = 300
    offset2 = 900
    offset3 = 1500
    time_offset = 0.7 * min(time, offset1)
    time_offset += 0.5 * min(max(time - offset1, 0), offset2 - offset1)
    time_offset += 0.3 * min(max(time - offset2, 0), offset3 - offset2)
    adjusted_time = time
    if ranking == HIGH:
        adjusted_time = time - time_offset
    elif ranking == LOW:
        adjusted_time = time + time_offset
    return adjusted_time
    
    
         
         
    
