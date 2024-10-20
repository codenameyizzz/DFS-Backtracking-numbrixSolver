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

    def set(self, value):
        self.val = value

    def __str__(self):
        if self.is_set():
            return str(self.get())
        else:
            return ""
