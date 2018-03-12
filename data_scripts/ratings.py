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
NEITHER_PREF = "neither"

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
    Helper method for the CTA classification given above. Given a
    CTA route number (one of the keys in the CTA_CLASSIFICATION
    dict) and a destination code (one of UC, HP, DT, and SS),
    returns a boolean indicating whether that CTA route includes
    that destination code.
    
    Inputs:
        cta_route: (int) CTA route number
        destination_code: (int) UC, HP, DT, or SS
    
    Returns: (boolean) Does the given CTA route go to that destination?
    '''
    classifier = CTA_CLASSIFICATION[cta_route]
    bit_place = int(math.log(destination_code, 2))
    return ((classifier & (1 << bit_place)) != 0)

# ------- Main Functions for Interfacing with UI -------- #

def compute_rankings(user_input):
    '''
    Compute a rating for each address given in the user input, based on the
    preferences given in the user input. This is the main function used
    to interface between the ratings system and the UI.
    
    The user input is the following 5-tuple:
    (
        address list,
        point of interest list,
        transit type preferences,
        cta preference,
        south side preference
    )
    
    Address list is a list of one or more addresses we care about rating 
    (each expressed as a string).
    Point of interest list is a (possibly empty) list of points of interest,
    each expressed as a string containing either that POI's address or 'identifier'
    (e.g. grocery store, medical center, bank, etc.)
    Transit type preferences is a dictionary mapping transit types (WALKING,
    DRIVING, CTA, etc.) to the user preference for each transit type (HIGH,
    MED, LOW, or NONE).
    CTA preference indicates where the user cares most about being able to
    use the CTA to travel to, and is either HP_PREF, DT_PREF, or NEITHER_PREF.
    South side preference indicates whether the user cares about being able
    to use the CTA to go to the south side, and is either "yes" or "no".
    
    Inputs:
        user_input: (tuple) A 5-tuple of user inputs
    
    Returns: (dict) A dictionary mapping addresses (strings) to their ratings
        (floats). Each address given in the user input contains an entry in the
        dictionary.
    '''
    # Extract information
    cleaned_user_input = parse_user_input(user_input)
    apartment_list = cleaned_user_input[0] # List of apartment addresses
    poi_list = cleaned_user_input[1] # List of points of interest
    transit_prefs = cleaned_user_input[2] # Dictionary mapping transit types to preference
    cta_pref = cleaned_user_input[3] # HP_PREF, DT_PREF, or neither
    south_side = cleaned_user_input[4] # Boolean
    
    # Perform Calculations
    address_ratings = [
        rating_for_address(
            address, poi_list, transit_prefs, cta_pref, south_side
        ) for address in apartment_list
    ]
    return {
        address: rating for address, rating in zip(apartment_list, address_ratings)
    }

# --------- Generic Helper Functions --------- #

def parse_user_input(user_input):
    '''
    Helper method for compute_rankings. Given user input in the same form as
    described in compute_rankings, verifies that the user input is valid and
    converts it to the form needed for use in this part of the program. Raises
    a ValueError if some aspect of the user input is invalid.
    
    Inputs:
        user_input: (tuple) A 5-tuple of user inputs (see compute_rankings)
    
    Returns:
        (tuple) A 5-tuple containing 
    '''
    valid_ranking = False # Will we be able to calculate a valid ranking?
    
    # Argument 0 - Address List
    apartment_list = user_input[0]
    
    # Argument 1 - POI List
    poi_list = user_input[1]
    if poi_list:
        # If the list of POI's is non-empty, then we should be able to produce
        # a valid POI ranking, regardless of whether there's a valid proximity
        # rating (exception is if all transit prefs are NONE)
        valid_ranking = True
    
    # Argument 2 - Transit Type Preferences
    transit_prefs = user_input[2]
    if transit_prefs[SHUTTLE] == NONE and \
        transit_prefs[DIVVY] == NONE and \
        transit_prefs[CTA] == NONE:
        if transit_prefs[WALKING] == NONE and \
            transit_prefs[DRIVING] == NONE and \
            transit_prefs[BIKING] == NONE:
            # If all tranist preferences are NONE, we won't be able to
            # calculate any valid ranking
            valid_ranking = False
    else:
        # If at least one of these first three preferences is non-NONE,
        # we'll be able to calculate a valid proximity rating
        valid_ranking = True
    
    # Argument 3 - CTA Preference
    cta_pref = user_input[3]
    if cta_pref != NEITHER_PREF and cta_pref != HP_PREF and cta_pref != DT_PREF:
        raise ValueError(
            "Value given for CTA preference is invalid. Expected " +
            HP_PREF + " or " +
            DT_PREF + " or " +
            NEITHER_PREF + ". Received " +
            str(cta_pref)
        )
    
    # Argument 4 - South Side Preference
    south_side_str = user_input[4].lower()
    if south_side_str == "yes":
        south_side = True
    elif south_side_str == "no":
        south_side = False
    else:
        raise ValueError(
            "South Side argument (user_input[4]) must be either yes or no"
        )
    
    # Raise an error if the preferences prevent us from calculating a valid
    # ranking
    if not valid_ranking:
        raise ValueError(
            "Can't calculate a rating for the apartment given the user's preferences."
        )
    
    # Return
    return (
        apartment_list,
        poi_list,
        transit_prefs,
        cta_pref,
        south_side
    )

def weighted_average(nums, weights):
    '''
    Returns the weighted average of the numbers in nums, weighted based on the
    weights given in weights. This function is used to ensure that all the
    ratings are effectively normalized.
    
    Inputs: 
        nums: (list of floats) A list of numbers for which we want the weighted
            average.
        weights: (list of floats) A list of weights to use when calculating the
            weighted average.
    
    Returns: (float) The weighted average
    '''
    return sum([n * weight for n, weight in zip(nums, weights)]) / sum(weights)


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

# ---------- Ratings Helper Functions -------- $

def rating_for_address(address, poi_list, transit_prefs, cta_pref, south_side):
    '''
    Calculate a rating for a single address, based on all of the given user
    preferences.
    
    Inputs:
        address: (string) The apartment address to rate. Must be in Hyde Park.
        poi_list: (list of strings) A list of points of interests, expressed
            either as addresses or as place names (e.g. grocery store, bank, etc.)
        transit_prefs: (dict) A dictionary mapping transit types to the user's
            preference for each transit type.
        cta_pref: (string) Either HP_PREF, DT_PREF, or neither
        south_side: (boolean) Does the user care about being able to use the 
            CTA to travel south of Hyde Park?
    
    Returns: (float) A rating for the given address. Lower is better.
    '''
    loc_rating = location_rating_for_address(address, transit_prefs, cta_pref, south_side)
    if poi_list:
        # Make sure poi_list is non-empty
        poi_rating = poi_rating_for_address(address, poi_list, transit_prefs)
        weights = [1, 1] # Location Rating, POI Rating
        return weighted_average([loc_rating, poi_rating], weights)
    else:
        return loc_rating
        
            
def location_rating_for_address(address, transit_prefs, cta_pref, south_side):
    '''
    Calculate a rating for this address based on its proximity to CTA bus stops,
    uChicago shuttles, and Divvy bike stations. Assumes that this rating can
    be meaningfully calculated given the user preferences (cases where this
    isn't the case should be handled outside this function by not calling it).
    
    Inputs:
        address: (string) The address to calculate a rating for
        transit_prefs: (dict) A dictionary mapping transit types to the user's
            preference for each type.
        cta_pref: (string) HP_PREF, DT_PREF, or NEITHER_PREF
        south_side: (boolean) Does the user care about being able to use the
            CTA buses to go south of Hyde Park.
    
    Returns: (float) A rating for the given address.
    '''
    # calculate all the needed travel times and store them in a dictionary
    walking_times_dict = travel_times.go(address, transit_prefs)
    
    # Extract user-given importance for each travel_type
    importances = {}
    for travel_type, travel_type_dict in walking_times_dict.items():
        example_entry = next(iter(travel_type_dict.values()))
        importances[travel_type] = example_entry["ranking"]
    
    # Calculate a rating for each travel_type
    ratings_dict = {
        CTA: cta_proximity_rating(walking_times_dict[CTA], cta_pref, south_side) if CTA in walking_times_dict else 0,
        DIVVY: divvy_proximity_rating(walking_times_dict[DIVVY]) if DIVVY in walking_times_dict else 0,
        SHUTTLE: shuttle_proximity_rating(walking_times_dict[SHUTTLE]) if SHUTTLE in walking_times_dict else 0
    }
    
    # Calculate an overall proximity rating for this address
    ratings = []
    weights = []
    weights_dict = {
        HIGH: 4,
        MED: 2,
        LOW: 1
    }
    for transit_type in walking_times_dict:
        # walking_times_dict excludes transit types for which the preference is None
        ratings.append(ratings_dict[transit_type])
        weights.append(weights_dict[transit_type])
    
    return weighted_average(ratings, weights)
  
def cta_proximity_rating(cta_travel_times_dict, cta_pref, south_side):
    '''
    Calculate a proximity rating based on the travel times to local CTA stops
    and the user's preferences.
    
    Inputs:
        cta_travel_times_dict: (dict) Mapping of CTA route names to
            dictionaries containing information about them.
        cta_pref: (string) HP_PREF, DT_PREF, or NEITHER_PREF
        south_side: (boolean) Same as everywhere else
    
    Returns: (float) A rating measuring the proxmity to CTA bus routes
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
        routes, times = find_closest_routes(sorted_cta_routes[dest])
        closest_routes[dest] = routes
        closest_route_times[dest] = times
    
    # Figure out weightings
    # UC and HP both reflect routes inside hype park, but UC is weighted much
    # more heavily because those routes are subjectively much more useful
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
    
    Inputs: 
        divvy_travel_times_dict: (dict) Mapping of divvy stop names to
            dictionaries containing information about them.
    
    Returns: (float) A rating measuring the proximity to Divvy stations
    '''
    stops, times = find_closest_routes(divvy_travel_times_dict)
    weights = [4, 1] # Should be a list of 2 numbers
    raw_rating = sum(
        [time * weight for time, weight in zip(times, weights)]
    )
    normalized_rating = raw_rating / sum(weights)
    return normalized_rating
    

DAY_SHUTTLES = [
    "53rd Street Express",
    "Apostolic/Drexel", # Exclude Apostolic and Drexel as independent routes
    "Campus Shuttle",
    "Friend Center/Metra",
    "Hyde Park Route",
    "Midway Route", # Exclude Midway Metra AM/PM as independent routes
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
    Generate a rating for this address' proximity to uChicago shuttle routes
    
    Inputs: 
        shuttle_travel_times_dict: (dict) Mapping of uChicago shuttle names to
            dictionaries containing information about them
    
    Returns: (float) A rating measuring the proximity to uChciago shuttle routes
    '''
    # Split shuttles into day and night shuttles
    day_shuttle_info = {}
    night_shuttle_info = {}
    for route in DAY_SHUTTLES:
        day_shuttle_info[route] = shuttle_travel_times_dict[route]
    for route in NIGHT_SHUTTLES:
        night_shuttle_info[route] = shuttle_travel_times_dict[route]
        
    # Calculate ratings for the day and night
    day_routes, day_times = find_closest_routes(day_shuttle_info)
    night_routes, night_times = find_closest_routes(night_shuttle_info)
    first_second_weights = [3, 1] # How heavily to weight closest route vs second closest
    day_rating = weighted_average(day_times, first_second_weights)
    night_rating = weighted_average(night_times, first_second_weights)
    
    # Calculate an overall rating
    day_night_weights = [1, 2] # Day weight, night weight
    return weighted_average([day_rating, night_rating], day_night_weights)

   
def poi_rating_for_address(address, poi_list, transit_prefs):
    '''
    Calcualate a POI rating for the given address.
    
    Inputs:
        address: (string) The address we care about
        poi_list: (string) A list of POI's. Can be either addresses or place
            names.
        transit_prefs: (dict) The user's preference for each type of transit.
    
    Returns: (float) A rating for the given address
    '''
    weights = [1 / (idx + 1) for idx in range(len(poi_list))]
    poi_ratings = []
    for poi in poi_list:
        poi_dict = points_of_interest.go(address, poi, transit_prefs)
        poi_ratings.append(rating_for_poi(poi_dict))
    return weighted_average(poi_ratings, weights) 


def rating_for_poi(poi_dict):
    '''
    Takes a dict for a specific POI and returns a rating for that POI
    
    Inputs:
        poi_dict: (dict) The output of points_of_interest.go. Maps each
            non-NONE travel type to a dict containing information about
            the relationship between the passed address and POI.
    
    Returns: (float) A rating for the given 
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
    based on the user's preferences. Given a travel time and a ranking for the
    associated travel type (HIGH, MED, or LOW), calculates an adjusted time
    which takes into account the user's preference for this form of travel.
    
    Inputs:
        time: (float) A travel time in seconds
        ranking: (string) HIGH, MED, or LOW
    
    Returns: (float) An 'adjusted' travel time in seconds
    '''
    # The current implementation of this adjusted ratings system works similarly
    # to marginal tax rates. There are four "time brackets", defined by
    # (0, cutoff1), (cutoff1, cutoff2), (cutoff2, cutoff3), and
    # (cutoff3, infinity). There is a marginal 'modification rate' which 
    # applies to each time bracket. These are given by mod_rate1, modrate2,
    # and mod_rate3, with the rate for the final bracket being 0. If the
    # preference is MED, the adjusted time is no different from the given
    # time. If the preference is HIGH or LOW, then the adjusted time is given
    # by modifying the given time by the cumulative modification achieved
    # by applying the given marginal modification rates to the given time.
    if ranking == MED:
        return time
        
    # Bracket cutoff definitions
    cutoff1 = 300 # 5 minutes
    cutoff2 = 720 # 12 minutes
    cutoff3 = 1500 # 25 minutes
    
    # Modification rates for each bracket
    mod_rate1 = 0.7
    mod_rate2 = 0.5
    mod_rate3 = 0.25
    
    # Perform the calculation
    cum_modification = mod_rate1 * min(time, cutoff1)
    cum_modification += mod_rate2 * min(max(time - cutoff1, 0), cutoff2 - cutoff1)
    cum_modification += mod_rate3 * min(max(time - cutoff2, 0), cutoff3 - cutoff2)
    if ranking == HIGH:
        return time - cum_modification
    elif ranking == LOW:
        return time + cum_modification
    else:
        raise ValueError("The given value for ranking is invalid")
    
    
         
         
    
