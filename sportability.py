import datetime
import re
import requests

from bs4 import BeautifulSoup
from dateutil.parser import parse as parsedate
from game import Game

class Sportability(object):
    def __init__(self, league_id, team_id, team_name):
        self._url = ('http://www.sportability.com/spx/Leagues/schedule.asp'
                     '?LgID=%s&Filter=%s' % (league_id, team_id))
        self._team_name = team_name
        self._games = []

    def _parse_game(self, date_string, time_string, matchup_string, location_string):
        # Parse date and time into a datetime.
        date = parsedate(date_string).date()
        time = parsedate(time_string).time()
        game_time = datetime.datetime.combine(date, time)

        # Parse matchup.
        # Playoffs start with "(Pla)", so have to pull that off the front.
        if matchup_string.startswith('(Pla) '):
            matchup_string = matchup_string[6:]
            playoffs = True
        else:
            playoffs = False
        teams = matchup_string.split(' at ')
        if teams[0] == self._team_name:
            opponent = teams[1]
            is_home = False
        else:
            opponent = teams[0]
            is_home = True

        return Game(game_time, opponent, is_home, location_string, playoffs=playoffs)

    def crawl_schedule(self):
        response = requests.get(self._url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Parse the schedule table.
        # Get all the rows.
        rows_soup = soup.findAll('tr', {'class': 'tablecontent'})
        for row_soup in rows_soup:
            # Parse the columns from each row.
            columns_soup = row_soup.findAll('td')
            
            try:
                date_string = columns_soup[0].getText()
                time_string = columns_soup[1].getText()
                matchup_string = columns_soup[2].getText()
                location_string = columns_soup[4].getText()
            except IndexError:
                continue

            # Parse the game.
            game = self._parse_game(date_string,
                                    time_string,
                                    matchup_string,
                                    location_string)
            if game.time.date() > datetime.date.today():
                # Only look at future games.
                self._games.append(game)

    @property
    def games(self):
        return self._games

