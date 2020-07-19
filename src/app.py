#!/usr/bin/env python3

import json
import random
import re
import math
import tweepy
import requests
import constant


def get_eia_tok():
    """ Getter for the EIA API token. You won't find these actual values anywhere in the repo -
    I removed them so nobody can do anything evil. """
    creds_data = json.load(open('../tokens.json', "r"))
    return creds_data['EIA_API_KEY']


def get_twitter_toks():
    """ Getter for the Twitter API token. You won't find these actual values anywhere in the repo -
    I removed them so nobody can do anything evil. """
    creds_data = json.load(open('../tokens.json', "r"))
    del creds_data['EIA_API_KEY']
    return creds_data


def get_sub_series(sub_cats):
    """ Gets the series IDs of all the subseries that are in UTC time
    associated with a given load balancing station """
    series = []
    for category in sub_cats['category']['childseries']:
        if "UTC time" in category['name']:
            series.append(category['series_id'])
    return series


def get_last_hour_data(sub_series_ids):
    """ Returns a dictionary with the energy source pointing to the amount of megawhatt hours
    generated by that energy source, given an iterable of subseries IDs to loop through """
    last_hour_data = {}
    for sub_series in sub_series_ids:
        params = {'api_key': get_eia_tok(), 'series_id': sub_series}
        data = requests.get(constant.EIA_SERIES_ENDPOINT, params=params)
        if data.status_code != 200: # ERROR TODO: Figure out error handling here
            print("failed to get data from a specific series")
        else:
            data = json.loads(data.text)
            source_re = re.compile("Net generation from (.*) for ")
            energy_source = source_re.match(data['series'][0]['name']).group(1)
            last_hour_data[energy_source] = data['series'][0]['data'][0][1]
    return last_hour_data


def get_emoji_bars(energy_dict):
    """ Returns a string containing the emoji bars that represent the
    distribution of energy generated by each energy source accoring to the
    energy dictionary passed in, mapping energy sources to MWh generated """
    emojis_string = ""
    # Sometimes - energy_dict's values contains both strings and ints
    total_energy = sum(map(int, energy_dict.values()))
    if total_energy <= 0:
        return "0 MWh\nNo energy generated in this balancing station location"

    emojis_string += str(total_energy) + " MWh\n\n"
    for element in energy_dict.keys():
        energy = energy_dict[element]
        if energy > 0: # Removes negative energy counts
            emoji_bar = ""
            num_emojis = math.ceil(energy / total_energy * constant.MAX_EMOJIS_PER_TWEET)
            for _ in range(num_emojis):
                emoji_bar += constant.EMOJIS[element]
            number_and_bar = str(energy_dict[element]) + " MWh\n" + emoji_bar + "\n"
            emojis_string += (element.capitalize() + ": " + number_and_bar)

    return emojis_string


def get_balancing_station():
    """ Randomly chooses a balancing station from the list in the
    file balancing_stations.json and then returns that balancing stations
    name and the text of it's subcategories' json as a tuple. """
    stations = json.load(open('../balancing_stations.json', "r"))
    station = random.choice(stations)
    params = {'api_key': get_eia_tok(), 'category_id': str(station['category_id'])}
    resp = requests.get(constant.EIA_CATEGORY_ENDPOINT, params=params)
    if resp.status_code == 200:
        return (station['name'] + ": ", resp.text)
    # ERROR TODO: Figure out error handling here as well
    return ("", "")
        #raise Exception("Failed to get data about the selected station: " + station['category_id']


def update_status():
    """ Continues attempting to update status until there is a
    tweet that is not a duplicate or a different error occurs """
    # Choose a random balancing station, and get it's name and sub series information
    (final_tweet, sub_series_text) = get_balancing_station()
    # Get a list of subseries IDs, giving endpoints for each energy source in the balancing station
    series_ids = get_sub_series(json.loads(sub_series_text))
    # Get the last hour's data from each subseries, returning a dictionary of energy -> MWh
    last_hour_data = get_last_hour_data(series_ids)
    # Add the emoji bars to the final tweet
    final_tweet += get_emoji_bars(last_hour_data)
    # Send final tweet
    try:
        api.update_status(final_tweet)
        # print(final_tweet)
    except tweepy.error.RateLimitError:
        # Catches errors where something has gone wrong and we're tweeting too frequently
        print("rate limit")
    except tweepy.TweepError as err:
        # Catches duplicated tweet error, simply making a new tweet
        if err.args[0][0]['code'] == 187:
            update_status()
        else:
            print(err)


# Authenticate twitter account
tw_toks = get_twitter_toks()
auth = tweepy.OAuthHandler(tw_toks['TWIT_CONSUMER_KEY'], tw_toks['TWIT_CONSUMER_SECRET'])
auth.set_access_token(tw_toks['TWIT_ACC_TOK'], tw_toks['TWIT_ACC_SEC'])
api = tweepy.API(auth)

update_status()
