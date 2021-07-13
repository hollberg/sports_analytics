"""
espn_scrape_functions.py

Functions to facilitate data scraping from ESPN
"""

# **** IMPORTS ****
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import lxml
import requests
import re
from selenium import webdriver
import json


# **** CONSTANTS ****
schedule_url_prefix = r'https://www.espn.com/nfl/team/schedule/_/name/no/season/'
game_url_prefix = r'https://www.espn.com/nfl/game/_/gameId/'
game_pbp_url_prefix = r'https://www.espn.com/nfl/playbyplay?gameId='


# All NFL Schedule URLS
url_nfl_schedule = f'https://www.espn.com/nfl/schedule/_/week/<Week#>/year/<YYYY>'
url_wildcard_schedule = f'https://www.espn.com/nfl/schedule/_/year/<YYYY>/seasontype/3'
url_div_round_schedule = f'https://www.espn.com/nfl/schedule/_/week/2/year/<YYYY>/seasontype/3'
url_conf_champ_sched = f'https://www.espn.com/nfl/schedule/_/week/3/year/<YYYY>/seasontype/3'
url_superbowl_sched = f'https://www.espn.com/nfl/schedule/_/week/5/year/<YYYY>/seasontype/3'


# Build list with the data elements contained in the ESPN javascript
# script containing the game and play-by-play data
gamepackage = ['gameId',
               'type',
               'timestamp',
               'status',
               'league',
               'leagueId',
               'sport',
               'network',
               'awayTeamName',
               'homeTeamName',
               'awayTeamId',
               'homeTeamId',
               'awayTeamColor',
               'homeTeamColor',
               'showGamebreak',
               'supportsHeadshots',
               'playByPlaySource',
               'probability.data',
               ]

team_codes_espn = {'Bills': {'code': 'buf'},
                   'Dolphins': {'code': 'mia'},
                   'Patriots': {'code': 'ne'},
                   'Jets ': {'code': 'nyj'},
                   'Cowboys': {'code': 'dal'},
                   'Giants': {'code': 'nyg'},
                   'Eagles': {'code': 'phi'},
                   'Football': {'code': 'wsh'},
                   'Ravens': {'code': 'bal'},
                   'Bengals': {'code': 'cin'},
                   'Browns': {'code': 'cle'},
                   'Steelers': {'code': 'pit'},
                   'Bears': {'code': 'chi'},
                   'Lions': {'code': 'det'},
                   'Packers': {'code': 'gb'},
                   'Vikings': {'code': 'min'},
                   'Texans': {'code': 'hou'},
                   }


# **** FUNCTIONS ***


def bs4_from_selenium(url: str):
    """
    Pass a URL string: return a Beautiful Soup object of the page as
    rendered via Selenium (thus with fully executed javascript, etc.
    :param url: String of the URL to target
    :return: Beautiful Soup Object
    """
    # Use selenium render full page
    DRIVER_PATH = r'selenium/chromedriver.exe'
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)

    page = driver.get(url)
    soup_page = BeautifulSoup(driver.page_source, features='lxml')
    driver.close()  # Close the selenium window
    return soup_page


def clean_gamepackage_text(gp_text: str, value: str):
    """
    Each ESPN "game summary" page includes a js script that includes
    JSON data of key game and play by play details as variables.
    Each variable declaration follows the format:
    espn.gamepackage.<specific variable> = "<the variable>";, ie,
        espn.gamepackage.gameId = "401220369";
    This script will clean all these lines to extract just the value
    of the variable
    :param gp_text: String: Line of text from the "game summary" javascript
        ex: espn.gamepackage.gameId = "401220369";
    :param value: The current element we're search for (ie, 'gameId')
    :return: The specific value assigned to the js variable
        ex: "401220369"
    """
    string_to_remove = f'espn.gamepackage.{value} = "'
    gp_text = gp_text.replace(string_to_remove, '')
    return gp_text[:-2]     # drop trailing "; characters


def get_nfl_games_by_team(team_code: str, seasons: list):
    """

    :param team_code: 2-letter code for the team (ex: New Orleans Saints: NO)
    :param seasons: list of season(s) to pull
    :return:
    """
    schedule_url = f'https://www.espn.com/nfl/team/schedule/_/name/{team_code}/season/'
    game_url_prefix = r'https://www.espn.com/nfl/game/_/gameId/'

    for season in seasons:
        schedule = bs4_from_selenium(f'{schedule_url}{season}')

        # Get URLS of all games

        page_links = schedule.find_all('a', class_='AnchorLink')
        game_links = [link.attrs['href'] for link in page_links if game_url_prefix in link.attrs['href']]

        for game in game_links:
            print(f"'{game.replace(game_url_prefix, '')}'")


def get_game_ids_from_schedule(season: str, week: str, postseason=False):
    """
    Pass the season and week, return list of all gameId values for NFL games
    played that season/week

    :param season:
    :param week:
    :param postseason: Boolean, if TRUE adjust
    :return:
    """
    game_ids = []

    url_schedule = \
        f'https://www.espn.com/nfl/schedule/_/week/{week}/year/{season}'

    # Postseason games indicated by appending additional 'seasontype' url
    if postseason:
        url_schedule = url_schedule + '/seasontype/3'

    game_url_prefix = r'/nfl/game/_/gameId/'    # remove text to isolate gameId
    frame_columns = ['away', 'home', 'result', 'passing_leader',
                     'rushing_leader', 'rec_leader', 'drop_me']

    schedule = bs4_from_selenium(url_schedule)

    # Find all 'a' links (scores) with hyperlinks to game page
    game_links = schedule.find_all('a', {'name': '&lpos=nfl:schedule:score'})
    game_ids = \
        [link.attrs['href'].replace(game_url_prefix, '') for link in game_links]

    # Get dataframe of game schedule, update column names, clean empty column
    games_tables = pd.read_html(url_schedule)

    df_games = pd.concat(games_tables)

    print(str(df_games.shape[1]))
    if df_games.shape[1] != 7:
        # Drop the "BYE" column if it exists
        df_games.drop(['BYE'], axis='columns', inplace=True)
        moo = 'boo' # What's up? Some kind of issue
    df_games.columns = frame_columns
    df_games.drop('drop_me', axis='columns', inplace=True)

    # Certain configurations import dataframe rows of repeated
    # values (ie, "NFC Championship") when there is a row in the
    # table used as a header/spacer. Delete these from df
    rows_to_delete = df_games[df_games['away'] == df_games['home']].index
    df_games.drop(rows_to_delete, inplace=True)

    # Weeks with "Bye" games cause a row of 'nan' values to
    # appear in the table/dataframe. Clean these out
    df_games.dropna(how='all', inplace=True)

    # Add new column with gameIDs, season, week
    game_ids = \
        [game.attrs['href'].replace(game_url_prefix, '') for game in game_links]

    if df_games.shape[0] != len(game_ids):
        moo = 'boo'

    df_games['gameId'] = game_ids
    df_games['season'] = season
    df_games['week'] = week
    df_games['IsPostseason'] = postseason

    return df_games


def get_mulitple_gameids(seasons: list, weeks: list, postseason=False):
    """

    :param seasons:
    :param weeks:
    :param postseason:
    :return:
    """
    df_games = pd.DataFrame()   # Initialize DataFrame
    for year in range(2020, 2021):
        for week in range(1, 18):
            print(f'Year: {year}, Week: {week}')

            df_game = (get_game_ids_from_schedule(str(year),
                                                  str(week),
                                                  postseason=False))
            print(df_game.columns)
            df_game.to_csv('games.csv', mode='a')
            df_games = df_games.dropna(how='all')
            df_games = df_games.append(df_game)

    df_games.to_excel('all_games.xlsx')



