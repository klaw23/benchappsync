class Game(object):
    def __init__(self, time, opponent, is_home, location):
        self._time = time
        self._opponent = opponent
        self._is_home = is_home
        self._location = location

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

    def __repr__(self):
        return '%s %s %s %s' % (str(self._time),
                                self._opponent,
                                str(self._is_home),
                                self._location)
