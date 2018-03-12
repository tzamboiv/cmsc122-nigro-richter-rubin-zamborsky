
def compute_score(address_dic, weight_dic):
    '''
    Compute the score of one address

    Input:
        address_dic: dictioanry containing address information
        weight_dic: dictionary containing the weight of each component
    Return:
        score float
    '''
    score = 0
    for i in address_dic:
        score += address_dic[i] * weight_dic[i]
    return score
def rank_addresses(lis, weight_dic):
    '''
    Ranks addresses based on weight dictionaries

    Input:
        lis: list of tuples of (address, address_dic)
        weight: weight_dic
    Return:
        list of tuples of (address, score) in descending order based
        on score
    '''
    res_list = []
    for address_tup  in lis:
        res_list.append((address_tup[0], compute_score(address_tup[1], weight_dic) ))
    return sorted(res_list, key=lambda tup: tup[1], reverse = True)