"""Library-provided serialization hooks for some common classes."""
from collections import namedtuple
import sys


class Hooks(namedtuple("Hooks", ["serialize", "deserialize"], defaults=[{}, {}])):
    """A convenience class for a pair of two dicts of hooks: one dict for serialization and one for deserialization.  
    Can be passed to any class or function that requires hooks. Classes that only need serialization or only
    deserialization are smart enough to get their needed half.
    """
    def update(self, *others):
        """Update the hooks by merging other hooks into them."""
        for other in others:
            self |= other

    def __ior__(self, other):
        """Merge hooks from other into self."""
        self.serialize.update(other.serialize)
        self.deserialize.update(other.deserialize)

        return self
    
    def __or__(self, other):
        """Create and return a new Hooks object with hooks from both arguments."""
        result = Hooks(self.serialize.copy(), self.deserialize.copy())
        result |= other

        return result


# Must be at the bottom to prevent circular import errors
from .qt import qt
