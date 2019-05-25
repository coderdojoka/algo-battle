from algo_battle.domain.algorithmus import Algorithmus
from algo_battle.domain import FeldZustand, Richtung
from enum import unique, Enum
from copy import deepcopy

@unique
class States(Enum):
    Init = 1
    Secure = 2
    Fill = 3
    Recover = 4


class Map(object):
    def __init__(self, width: int, height:int):
        self._storage = [FeldZustand.Frei] * width * height
        self._width = width
        self._height = height

    def get(self, x:int, y:int):
        """Coordinate system starts top left."""
        return self._storage[y*self._width + x]

    def update(self, x: int, y: int, new: FeldZustand):
        self._storage[y*self._width+x] = new

class StateMachiner(Algorithmus):

    def __init__(self):
        super().__init__()
        self._current_update_fn = self.update_init
        self._map = None
        self._target_points = []
        self._current_square = None
        self._finished_squares = []

    def _next_dir(self):
        if self._next_dirs:
            return self._next_dirs.pop()
        return None

    def x(self):
        return self.abstand(Richtung.Links)
    def y(self):
        return self.abstand(Richtung.Oben)

    def most_room(self):
        return max([(r, self.abstand(r)) for r in [Richtung.Oben,
                                                   Richtung.Unten,
                                                   Richtung.Links,
                                                   Richtung.Rechts]],
                   key=lambda x: x[1])[0]

    def build_grid(self, grid_x:int, grid_y:int):
        grid = []
        for i in range(grid_x):
            for j in range(grid_y):
                # Top Left
                # Top Right
                # Bot Right
                # Bot Left
                grid.append([(int((self._map._width-1)/grid_x * i),
                              int((self._map._height-1)/grid_y * j)),
                             (int((self._map._width-1)/grid_x * (i+1)),
                              int((self._map._height-1)/grid_y * j)),
                             (int((self._map._width-1)/grid_x * (i+1)),
                              int((self._map._height-1)/grid_y * (j+1))),
                             (int((self._map._width-1)/grid_x * i),
                              int((self._map._height-1)/grid_y* (j+1)))])
        # Find the rectangle whose starting point is closest to us
        starting_rect = grid.index(min(grid, key=lambda rect:
                                       abs(self.x() - rect[0][0]) +
                                       abs(self.y() - rect[0][1])))
        # shift the list so we start with that one
        if starting_rect > len(grid) / 2:
            return (list(reversed(grid[0:starting_rect])) +
                    list(reversed(grid[starting_rect:])))
        return grid[starting_rect:] + grid[0:starting_rect]

    def update_init(self, letzter_zustand: FeldZustand, zug_nummer:
                    int, aktuelle_punkte: int) -> Richtung:
        width = self.abstand(Richtung.Links) + self.abstand(Richtung.Rechts)
        height = self.abstand(Richtung.Oben) + self.abstand(Richtung.Unten)
        # print("Width: ", width)
        # print("Height: ", height)
        self._map = Map(width, height)
        self._grid = self.build_grid(grid_x=8, grid_y=8)
        return self.most_room(), self.update_explore

    def navigate_to_point(self, x:int, y:int):
        xdist = x - self.x()
        ydist = y - self.y()
        if xdist == 0 and ydist == 0:
            return None
        xdir = Richtung.Links if xdist < 0 else Richtung.Rechts
        ydir = Richtung.Oben if ydist < 0 else Richtung.Unten

        if xdist == 0:
            direction = ydir
        elif ydist == 0:
            direction = xdir
        elif abs(xdist) < abs(ydist):
            direction = xdir
        else:
            direction = ydir
        return direction

    def next_square(self):
        if not self._grid:
            return None
        sq = self._grid[0]
        self._grid = self._grid[1:]
        self._current_square = deepcopy(sq)
        return sq

    def update_explore(self, letzter_zustand: FeldZustand, zug_nummer:
                    int, aktuelle_punkte: int) -> Richtung:
        if self.collided():
            self._target_points = self.next_square()
        direction = None
        while direction is None:
            if not self._target_points:
                # print("Getting next square")
                if self._current_square is not None:
                    self._finished_squares.append(self.fill_points(reversed(self._current_square)))
                self._target_points = self.next_square()
                if self._target_points is None:
                    return self.richtung, self.update_fill
            direction = self.navigate_to_point(*self._target_points[0])
            if direction is None:
                # print("Getting next point")
                self._target_points = self._target_points[1:]

        return direction, self.update_explore

    def fill_points(self, square_points):
        # Order of points in finished_squares:
        # Bot Left
        # Bot Right
        # Top Right
        # Top Left
        start_left = True
        points = []
        # we don't need to fill the outer lines of the square,
        # since we've already done that
        ybegin = square_points[0][1] - 1
        yend = square_points[3][1] + 1
        # supply negative step here because top y coord is smaller than bot
        # and subtract 1 from yend so we actually hit the topmost line
        for y in range(ybegin, yend-1, -1):
            left_point = [square_points[0][0]+1, y]
            right_point = [square_points[1][0]-1, y]
            if (start_left):
                points.append(left_point)
                points.append(right_point)
            else:
                points.append(right_point)
                points.append(left_point)
            start_left = not start_left
        return points
    
    def next_fill(self):
        if not self._finished_squares:
            return None
        sq = self._finished_squares.pop()
        return sq
                
    def update_fill(self, letzter_zustand: FeldZustand, zug_nummer:
                    int, aktuelle_punkte: int) -> Richtung:
        if self.collided():
            self._target_points = self.next_fill()
        direction = None
        while direction is None:
            if not self._target_points:
                # print("Getting next fill")
                self._target_points = self.next_fill()
                if self._target_points is None:
                    return self.richtung, self.update_random
            direction = self.navigate_to_point(*self._target_points[0])
            if direction is None:
                # print("Getting next point")
                self._target_points = self._target_points[1:]

        return direction, self.update_fill
        
    def update_random(self, letzter_zustand: FeldZustand, zug_nummer:
                      int, aktuelle_punkte: int) -> Richtung:
        if self.collided():
            return Richtung.zufall(ausser=self.richtung), self.update_random
        return self.richtung, self.update_random

    
    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer:
                      int, aktuelle_punkte: int) -> Richtung:
        if self._map is not None:
            self._map.update(self.x(), self.y(), FeldZustand.Besucht)
            expected_x, expected_y = self.update_coords(self.old_x,
                                                        self.old_y, self.old_dir)
            if expected_x != self.x() or expected_y != self.y():
                self._map.update(expected_x, expected_y, FeldZustand.Belegt)

        direction, new_update_fn = self._current_update_fn(letzter_zustand,
                                                           zug_nummer, aktuelle_punkte)
        self._current_update_fn = new_update_fn
        self.old_x = self.x()
        self.old_y = self.y()
        self.old_dir = direction

        return direction

    def collided(self):
        expected_x, expected_y = self.update_coords(self.old_x,
                                                    self.old_y, self.old_dir)
        # print("Expected: ", expected_x, expected_y)
        # print("Current: ", self.x(), self.y())
        # if expected_x != self.x() or expected_y != self.y():
        #     print("COLLISION")
        return expected_x != self.x() or expected_y != self.y()

    def update_coords(self, x:int, y:int, direction:Richtung):
        if direction == Richtung.Links:
            return max(x-1, 0), y
        elif direction == Richtung.Rechts:
            return min(x+1, self._map._width-1), y
        elif direction == Richtung.Oben:
            return x, max(y-1, 0)
        elif direction == Richtung.Unten:
            return x, min(y+1, self._map._height-1)

if __name__ == "__main__":
    from algo_battle.app.pyside2_gui import start_gui

    start_gui([__name__])
