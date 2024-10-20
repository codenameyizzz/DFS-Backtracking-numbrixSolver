# board.py

import random

def is_one_away(val1, val2):
    """Return whether or not the two values are numerically adjacent."""
    return abs(val1 - val2) == 1

def get_directional_neighbors(row, col):
    """Given a row and column value, return the row and column values of the corresponding up, down, left and right
    neighboring squares."""
    return [[a + b for a, b in zip((row, col), directional)]
            for directional in ((-1, 0), (1, 0), (0, -1), (0, 1))]

def get_all_coordinates_at_distance(row, col, distance):
    """Return all feasible coordinates in a board which have a Manhattan Distance of `distance` from the location given
    by (row, col)."""
    coordinates = set()

    if distance <= 0:
        return coordinates

    pairs = [(x, distance - x) for x in range(distance + 1)]
    for quadrant_multiplier in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        row_multiplier, col_multiplier = quadrant_multiplier
        for row_pair_part, col_pair_part in pairs:
            r = row + (row_pair_part * row_multiplier)
            c = col + (col_pair_part * col_multiplier)
            if 0 <= r < 9 and 0 <= c < 9:
                coordinates.add((r, c))

    return coordinates

class Val:
    """
    A class to represent a value location in a Numbrix board.

    Within a Numbrix board, every square can have one of the values of the set [1 .. 81].

    When a value is set, the `val` instance variable will be defined, however when a value is not set, the
    `possible_values` will contain all values that could reasonably be held by the square this Val occupies.
    """
    def __init__(self, val_to_copy=None):
        """Create a Numbrix board value. The default value has no `val` and all possible values are present in
        `possible_values`. If this new Val should copy an existing Val, then copy its internal state.

        :param val_to_copy: other Val to copy internal state from.
        """
        self.val = None

        if val_to_copy is not None:
            self.val = val_to_copy.val
            self.possible_values = val_to_copy.possible_values[:]
        else:
            self.possible_values = [x for x in range(1, 82)]

    def remove_possible_value(self, possible_value):
        """Remove a value from this Val's `possible_values`."""
        if not self.is_set() and possible_value in self.possible_values:
            self.possible_values.remove(possible_value)

    def is_set(self):
        """Check if this Val has a defined value."""
        return self.val is not None

    def possible_values_size(self):
        """Return the size of this Val's `possible_values`."""
        return len(self.possible_values)

    def get(self):
        return self.val

    def set(self, value, is_fixed=False):
        self.val = value
        if is_fixed:
            self.possible_values = []  # Clear possible values if fixed

    def __str__(self):
        if self.is_set():
            return str(self.get())
        else:
            return "-"

class Board:
    """A Numbrix board.

    A board is represented as a 9x9 grid of values, stored internally as a 1-dimensional array.
    """
    def __init__(self, other_board=None):
        if other_board is not None:
            self.board = []
            for val in other_board.board:
                self.board.append(Val(val_to_copy=val))
        else:
            self.board = [Val() for _ in range(81)]  # Inisialisasi papan kosong

    def is_complete(self):
        """Check if the board has valid values for all squares."""
        return False not in [v.is_set() for v in self.board]

    def is_not_feasible(self):
        """Check if the current board is no longer feasible.

        This may happen if:
         * Any squares no longer have any feasible values which they can hold
         * Any squares have become somewhat surrounded but they do not have their required "correct neighbors"
        """
        for row in range(9):
            for col in range(9):
                val = self.get(row, col)
                if val.is_set() and not self.would_be_feasible(row, col, val.get()):
                    return True

        return len([1 for v in self.board if not v.is_set() and v.possible_values_size() == 0]) > 0

    def get(self, row, col):
        """Using row-major ordering, get the value at location (row, col) or return None if the index is bad."""
        if not (0 <= row < 9 and 0 <= col < 9):
            return None
        return self.board[row * 9 + col]

    def set(self, row, col, val, is_fixed=False):
        """Using row-major ordering, set the value at location (row, col).

        This operation will also ripple throughout the rest of the board, progressively removing possible values from
        the surrounding squares on the board.

        For example, if the middle of the board is set to value 50, everything else in the board should lose the
        possibility of having the value 50, every square a Manhattan Distance of 2 or greater away should also lose the
        values 49 and 51, etc.
        """
        if not (0 <= row < 9 and 0 <= col < 9):
            raise ValueError(f"Row and column values must be in the range [0 .. 8] but got row: {row}, column: {col}")
        self.board[row * 9 + col].set(val, is_fixed=is_fixed)

        for distance in range(1, 17):  # 16 is the maximum board distance
            for r, c in get_all_coordinates_at_distance(row, col, distance):
                if self.get(r, c) is not None:
                    for v in range(val - distance + 1, val + distance):
                        if 1 <= v <= 81:
                            self.get(r, c).remove_possible_value(v)

    def would_be_feasible(self, row, col, val):
        """Check if the provided value would be feasible at the specified location.

        For a value to be feasible at a location, it must have (provided it is not 1 or 81):
         * At least two open neighbors (if none of the directional neighbors are correct)
         * Or one correct directional neighbor and at least one open neighbor
         * Or two correct directional neighbors

        If the value is 1 or 81:
         * It can either have at least one open neighbor
         * Or one correct directional neighbor
        """
        open_neighbors = 0
        correct_directional_neighbors = 0

        for directional_row, directional_col in get_directional_neighbors(row, col):
            if not (0 <= directional_row < 9 and 0 <= directional_col < 9):
                continue

            directional_val = self.get(directional_row, directional_col)
            if not directional_val.is_set():
                open_neighbors += 1
            elif is_one_away(val, directional_val.get()):
                correct_directional_neighbors += 1

        if val == 1 or val == 81:
            return open_neighbors >= 1 or correct_directional_neighbors == 1
        else:
            return (correct_directional_neighbors == 0 and open_neighbors >= 2) or \
                   (correct_directional_neighbors == 1 and open_neighbors >= 1) or \
                   correct_directional_neighbors == 2

    def get_next_boards(self):
        """Evaluate the board and take the next logical assignments on some specific square. Return all boards that
        represent feasible moves on the minimal options location.
        """
        next_boards = []

        minimal_options_val_tuple = None

        for row in range(9):
            for col in range(9):
                val = self.get(row, col)
                if not val.is_set() and (
                        minimal_options_val_tuple is None
                        or val.possible_values_size() < minimal_options_val_tuple[0].possible_values_size()):
                    minimal_options_val_tuple = (val, row, col)

        if minimal_options_val_tuple is None:
            return next_boards  # No possible moves

        # Minimal options location has been identified, now return all feasible values as possible next boards
        val, row, col = minimal_options_val_tuple
        for value in val.possible_values:
            if self.would_be_feasible(row, col, value):
                new_board = Board(other_board=self)
                new_board.set(row, col, value)
                next_boards.append(new_board)

        return next_boards

    def __repr__(self):
        """What should the board look like when it is printed? How about:

            +----------------------------+
            |  1  2  3  4  5  6  7  8  9 |
            | 18 17 16 15 14 13 12 11 10 |
            | 19 20 21 22 23 24 25 26 27 |
            | 36 35 34 33 32 31 30 29 28 |
            | 37 38 39 40 41 42 43 44 45 |
            | 54 53 52 51 50 49 48 47 46 |
            | 55 56 57 58 59 60 61 62 63 |
            | 72 71 70 69 68 67 66 65 64 |
            | 73 74 75 76 77 78 79 80 81 |
            +----------------------------+

        :return: The string representation of the board.
        """
        output = "    +----------------------------+\n"
        for row in range(9):
            output += "    |"
            for col in range(9):
                val = self.get(row, col)
                output += str(val).rjust(3)
            output += " |\n"
        output += "    +----------------------------+"
        return output
