


# from bs4 import BeautifulSoup
import pandas as pd
import lxml
import requests
import re
from selenium import webdriver
import json
import espn_scrape_functions as espn


# # *** GET GAME SCHEDULES and GAME LINKS ****
# df_games = pd.DataFrame()   # Initialize DataFrame
# for year in range(2020, 2021):
#     for week in range(1, 18):
#         print(f'Year: {year}, Week: {week}')
#
#         df_game = (espn.get_game_ids_from_schedule(str(year),
#                                                    str(week),
#                                                    postseason=False))
#         print(df_game.columns)
#         df_game.to_csv('games.csv', mode='a')
#         df_games = df_games.dropna(how='all')
#         df_games = df_games.append(df_game)
#
#
# df_games.to_excel('all_games.xlsx')


df_games = pd.read_csv('games.csv')
df_games = df_games.dropna()

# Loop over all games
for game_id in df_games['gameId']:
    game_url = espn.game_url_prefix + game_id

    game_soup = espn.bs4_from_selenium(game_url)



moo = 'boo'