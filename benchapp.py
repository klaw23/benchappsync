import datetime
import re
import requests

from bs4 import BeautifulSoup
from dateutil.parser import parse as parsedate
from game import Game

class BenchApp(object):
    def __init__(self, email, password, team_name):
        self._login_url = 'https://www.benchapp.com/player-area/ajax/login.php'
        self._schedule_url = 'https://www.benchapp.com/schedule/list'
        self._add_game_url = 'https://www.benchapp.com/schedule-area/ajax/addEditGame.php'
        self._remove_game_url = 'https://www.benchapp.com/modules/ajax/removeItem.php'

        self._team_name = team_name
        self._games = []

        # Login
        self._session = requests.Session()
        self._session.post(self._login_url,
                           data={'email': email, 'password': password})

    def _parse_game(self, date_string, time_string, home_team, away_team,
                    location_string, game_id_string, playoffs):
        # Parse date and time into a datetime.
        date = parsedate(date_string).date()
        time = parsedate(time_string).time()
        game_time = datetime.datetime.combine(date, time)

        # Parse matchup.
        if home_team == self._team_name:
            opponent = away_team
            is_home = True
        else:
            opponent = home_team
            is_home = False

        return Game(game_time,
                    opponent,
                    is_home,
                    location_string,
                    game_id_string,
                    playoffs)

    def crawl_schedule(self):
        response = self._session.get(self._schedule_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Parse the schedule table.
        # Get all rows with a month-year class (example: Mar-2016).
        row_class_re = re.compile('^\w\w\w-\w\w\w\w')
        rows_soup = soup.findAll('tr', {'class': row_class_re})
        for row_soup in rows_soup:
            # Parse the columns from each row.
            # Filter for links to the game.
            game_link_re = re.compile('schedule')
            columns_soup = row_soup.findAll('a', {'href': game_link_re})

            text_filter_re = re.compile('[A-Za-z ]+')
            home_team = text_filter_re.search(columns_soup[1].getText()).group()
            away_team = text_filter_re.search(columns_soup[2].getText()).group()
            date_string = row_soup.find('div', {'class': 'dayOfMonth'}).getText()
            location_string = text_filter_re.search(\
                columns_soup[3].find('div', {'class': 'location'}).getText()).group()
            time_string = row_soup.find('div', {'class': 'time'}).getText()
            game_id_string = columns_soup[0]['href'].split('-')[1]
            playoffs = bool(row_soup.find('span', {'class': 'fa-trophy'}))

            # Parse the game.
            game = self._parse_game(date_string,
                                    time_string,
                                    home_team,
                                    away_team,
                                    location_string,
                                    game_id_string,
                                    playoffs)
            if game.time.date() > datetime.date.today():
                # Only look at future games.
                self._games.append(game)

    def add_games(self, games):
        """ Add games to the benchapp schedule.
        """
        for game in games:
            # TODO(kevin): Use Benchapp opponent ID rather than creating a new
            # opponent for every game.
            response = self._session.get(self._add_game_url,
                                         params={
                                             'type': 'GAME',
                                             'subType': 'PLAYOFF' if game.playoffs else 'REGULAR',
                                             'opponentID': 0,
                                             'newTeamName': game.opponent,
                                             'homeAway': 'Home' if game.is_home else 'Away',
                                             'dateValue': str(game.time.date()),
                                             'hr': game.time.strftime('%I'),
                                             'min': game.time.strftime('%M'),
                                             'am-pm': game.time.strftime('%p'),
                                             'duration_hrs': "1",
                                             'location': game.location
                                          })
            response.raise_for_status()

    def remove_games(self, games):
        """ Remove games from the benchapp schedule.

            TODO(kevin): We should probably "cancel" rather than "remove" the
            game so the team gets notified.
        """
        for game in games:
            response = self._session.get(self._remove_game_url,
                                         params={
                                             'type': 'game',
                                             'id': game.game_id
                                          })
            response.raise_for_status()

    @property
    def games(self):
        return self._games

