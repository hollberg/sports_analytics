"""
get_nfl_play_by_play
"""

import espn_scrape_functions as espn
import re
import pandas as pd
import json


# list_of_games = [
#     '401220395',
#     '401220399'
# ]

df_games = pd.read_csv('games.csv')
list_of_games =\
    [game_id for game_id in df_games['gameId'] if game_id != 'gameId']


# Loop over all games. Extract game data and populate 2 separate spreadsheets:
# 1) games.xlsx: contains top-leve game data (teams, date, etc.)
# 2) pbp.xlsx: contains play-by-play data for each game
for game_num, game_id in enumerate(list_of_games):
    game = espn.bs4_from_selenium(f'{espn.game_url_prefix}{game_id}')

    # Get "Gamepackage" script from webpage
    my_script = game.find_all(string=re.compile('espn.gamepackage'))
    script_text = my_script[0].replace('\t', '')

    game_data = {}
    for line in script_text.split('\n'):
        for element in espn.gamepackage:
            if line != '' and line.startswith(f'espn.gamepackage.{element}'):
                game_data[element] = espn.clean_gamepackage_text(line, element)

    pbp_text = game_data.pop('probability.data')

    if game_num == 0:
        df_games = pd.DataFrame.from_dict([game_data])
        print(f'Processed game id: {game_id}')
        df_games.to_csv('game_results.csv', mode='a')
    else:
        df_current = pd.DataFrame.from_dict([game_data])
        df_games = df_games.append(df_current)
        print(f'Processed game id: {game_id}')
        df_current.to_csv('game_results.csv', mode='a')

    pbp_clean = pbp_text.replace('espn.gamepackage.probability.data = ', '')
    pbp_clean = pbp_clean + ']'
    # print(clean_prob_data)

    pbp_json = json.loads(pbp_clean);

    if game_num == 0:
        df_pbp = pd.json_normalize(pbp_json)
        df_pbp['gameId'] = game_data['gameId']    # Add column with gameId
        # Append current dataframe to csv
        df_pbp.to_csv('pbp.csv', mode='a')
    else:
        df_current = pd.json_normalize(pbp_json)
        df_current['gameId'] = game_data['gameId']
        # Append current dataframe to csv
        df_current.to_csv('pbp.csv', mode='a')
        df_pbp = df_pbp.append(df_current)

df_pbp.to_excel('pbp.xlsx')
df_games.to_excel('games.xlsx')

moo = 'boo'