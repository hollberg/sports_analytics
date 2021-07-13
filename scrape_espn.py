"""
scrape_espn.py

Scrape NFL data from ESPN website
"""

from bs4 import BeautifulSoup
import pandas as pd
import lxml
import requests
import re
from selenium import webdriver
import json





schedule_url_prefix = r'https://www.espn.com/nfl/team/schedule/_/name/no/season/'
game_url_prefix = r'https://www.espn.com/nfl/game/_/gameId/'
game_playbyplay_url_prefix = r'https://www.espn.com/nfl/playbyplay?gameId='
GAME_ID = '401220369'



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

loopers = ['homeWinPercentage',
           'playId',
           'tiePercentage'
           ,'secondsLeft']

play_loopers = ['period']

terminator = '}];'  # String that terminates/ends the espn.gamepackage.probability.data variable


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
    return soup_page


def parse_espn_nfl_play_by_play(bs_obj):
    """
    Pass a BeautifulSoup object of a parsed url of espn's NFL game play by play
    (ie, https://www.espn.com/nfl/playbyplay?gameId={game_id} )
    return tuple of (df_drives, df_plays)
    :param beautifulsoup_object:
    :return:
    """
    pbp = bs_obj.find(id='gamepackage-drives-wrap')

    # Get number of drives. One 'ul' element of class 'drive-list' per drive
    num_drives = len(pbp.find_all('ul', class_='drive-list'))

    for drive_num, drive in enumerate(pbp.find_all('ul', class_='drive-list')):
        drive_summary = ''
        print(f'Drive # {drive_num}:')
        team_logo = \
            pbp.find_all('span', class_='home-logo')[drive_num].find(class_='team-logo').attrs['src']

        drive_result = pbp.find_all('span', class_='drives')[drive_num].text
        home_team = pbp.find_all('span', class_='home')[drive_num].find(class_='team-name').text
        home_score = pbp.find_all('span', class_='home')[drive_num].find(class_='team-score').text
        away_team = pbp.find_all('span', class_='away')[drive_num].find(class_='team-name').text
        away_score = pbp.find_all('span', class_='away')[drive_num].find(class_='team-score').text
        drive_details = drive_result = pbp.find_all('span', class_='drive-details')[drive_num].text
        print(f'{drive_result} / {home_team}: {home_score} / {away_team}: {away_score} / {drive_details}')

        # Loop over all PLAYS in the current DRIVE
        for play_num, play in enumerate(pbp.find_all('ul', class_='drive-list')[drive_num].find_all('li')):
            moo = 'b00'
            down_and_distance = play.find_all('h3')[0].text
            play_summary = play.find_all('p')[0].text
            print(f'Play # {play_num}: D&D: {down_and_distance}, summary: {play_summary}')



        # drive_summary.append(pbp.find_all('span', class_='home-logo')[drive_num])



def get_playbyplay_page(url: str) -> str:
    """

    :param url: URL of the play by play page for the game
    :return: HTML of page
    """
    # Use selenium render full page
    DRIVER_PATH = r'selenium/chromedriver.exe'
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)

    page = driver.get(url)
    soup_page = BeautifulSoup(driver.page_source, features='lxml')

    pbp = soup_page.find(id='gamepackage-drives-wrap')

    # Find all "li" elements of the <ul> for each drive
    # soup_page.find(id='gamepackage-drives-wrap').find_all('ul', class_='drive-list')
    # Play level details
    # soup_page.find(id='gamepackage-drives-wrap').find_all('ul', class_='drive-list')[3].find_all('li')

    moo = 'boo'
    return soup_page


# get_playbyplay_page(f'{game_playbyplay_url_prefix}401220369')

# Parse ESPN's NFL play by play page for specified game id
#pbp_soup = bs4_from_selenium(f'{game_playbyplay_url_prefix}401220369')

#parse_espn_nfl_play_by_play(pbp_soup)

gamecast_soup = bs4_from_selenium('https://www.espn.com/nfl/game/_/gameId/401220369')

foo = gamecast_soup.find_all('script', type='text/javascript')

my_script = gamecast_soup.find_all(string = re.compile('espn.gamepackage'))
script_text = my_script[0].replace('\t', '')


foo = {}
for line in script_text.split('\n'):
    for start in gamepackage:
        if line.startswith(f'espn.gamepackage.{start}'):
            foo[start] = line

for item, val in foo.items():
    print(f'{item}, {val} \n')

# [line for line in my_script[0].split('\n')]

clean_prob_data = foo['probability.data'].replace('espn.gamepackage.probability.data = ', '')
clean_prob_data = clean_prob_data[:-1]
print(clean_prob_data)

mygood = json.loads(clean_prob_data)
df = pd.json_normalize(mygood)

df.to_clipboard()


moo = 'boo'
