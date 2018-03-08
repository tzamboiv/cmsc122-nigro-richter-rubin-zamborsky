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
    classifier = CTA_CLASSIFICATION[cta_route]
    bit_place = int(math.log(destination_code, 2))
    return ((classifier & (1 << bit_place)) != 0)

def compute_rankings(user_input):
    # Extract information
    apartment_list = user_input[0] # List of apartment addresses
    poi_list = user_input[1] # List of points of interest
    transit_prefs = user_input[2] # Dictionary mapping transit types to preference
    cta_pref = user_input[3] # HP_PREF, DT_PREF, or NEITHER_PREF
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
    
    
def rating_for_address(address, poi_list, transit_prefs, cta_pref, south_side):
    loc_rating = location_rating_for_address(address, transit_prefs, cta_pref, south_side)
    if poi_list:
        # Make sure poi_list is non-empty
        poi_rating = poi_rating_for_address(address, poi_list, transit_prefs)
        return 0.5 * loc_rating + 0.5 * poi_rating
    else:
        return loc_rating
    
            
def poi_rating_for_address(address, poi_list, transit_prefs):
    weights = [1 / (idx + 1) for idx in range(len(poi_list))]
    poi_ratings = []
    for poi in poi_list:
        poi_dict = points_of_interest.go(address, poi, transit_prefs)
        poi_ratings.append(normalized_rating_for_poi(poi_dict))
    return weighted_average(poi_ratings, weights)
        

def location_rating_for_address(address, transit_prefs, cta_pref, south_side):
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
        CTA: cta_proximity_rating(walking_times_dict[CTA], cta_pref, south_side),
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
    normalization_const = sum(weights)
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

def weighted_average(nums, weights):
    return sum([n * weight for n, weight in zip(nums, weights)]) / sum(weights)
    
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
    
    TODO: Make this work for arbitrary number of stops (not just 2)
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
    

def shuttle_proximity_rating(shuttle_travel_times_dict):
    return 0

def cta_hours(cta_line_name):
    pass

def shuttle_hours(shuttle_name):
    pass

def normalized_rating_for_poi(poi_dict):
    '''
    Takes a dict for a specific POI and returns a rating for that POI
    '''
    ratings = {}
    weightings = {
        HIGH: 4,
        MED: 2,
        LOW: 1,
        NONE: 0
    }
    raw_rating = 0
    weights = []
    for travel_type in poi_dict:
        weight = weightings[poi_dict[travel_type]["ranking"]]
        weights.append(weight)
        raw_rating += poi_dict[travel_type]["time"]
    
    # Normalize the rating
    normalization_const = sum(weights)
    return raw_rating / normalization_const
         
         
    
