from collections import UserString
from typing import Self

class Commit(UserString):
    """Represents a git commit"""

    def __eq__(self, other: Self | str):
        return self.startswith(other) or other.startswith(self)