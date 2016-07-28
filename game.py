class Game(object):
    @staticmethod
    def diff(old_schedule, new_schedule):
        """ Compares 2 schedules and returns which schedules were added and
            deleted in the new schedule.

            Args:
                old_schedule - A list of Games in the old schedule.
                new_schedule - A list of Games in the new updated schedule.

            Returns a tuple containing 2 lists.
                - The first list contains the games that were in the new
                schedule, but not in the old schedule. These should be added.
                - The second list contains the game that were in the old
                schedule, but removed in the new schedule. These should be
                deleted.
        """
        added_games = []
        removed_games = []
        for game in new_schedule:
            if game not in old_schedule:
                added_games.append(game)
        for game in old_schedule:
            if game not in new_schedule:
                removed_games.append(game)
        return (added_games, removed_games)

    def __init__(self, time, opponent, is_home, location, game_id=None, playoffs=False):
        self._time = time
        self._opponent = opponent
        self._is_home = is_home
        self._location = location
        self._game_id = game_id
        self._playoffs = playoffs

    @property
    def time(self):
        return self._time

    @property
    def opponent(self):
        return self._opponent

    @property
    def is_home(self):
        return self._is_home

    @property
    def location(self):
        return self._location

    @property
    def game_id(self):
        return self._game_id

    @property
    def playoffs(self):
        return self._playoffs

    def __repr__(self):
        return '%s %s %s %s %s' % (str(self._time),
                                   self._opponent,
                                   str(self._is_home),
                                   self._location,
                                   self._game_id)

    def __eq__(self, other):
        # Don't worry about location.
        return (self.time == other.time and self.opponent == other.opponent and
                self.is_home == other.is_home and self.playoffs == other.playoffs)
