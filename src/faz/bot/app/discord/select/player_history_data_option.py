from __future__ import annotations

from enum import Enum


class PlayerHistoryDataOptionType(Enum):
    CATEGORICAL = "Categorical"
    NUMERICAL = "Numerical"
    ALL = "ALL"


class _IdOptionsMember:
    def __init__(self, value: str, type: PlayerHistoryDataOptionType) -> None:
        self._type = type
        self._value = value

    @property
    def type(self):
        """The type property."""
        return self._type

    @property
    def value(self):
        """The value property."""
        return self._value


class PlayerHistoryDataOption(Enum):
    """Mapping of enum member to display value for IdSelect."""

    ALL = _IdOptionsMember("All", PlayerHistoryDataOptionType.ALL)

    GUILD = _IdOptionsMember("Guild", PlayerHistoryDataOptionType.CATEGORICAL)
    USERNAME = _IdOptionsMember("Username", PlayerHistoryDataOptionType.CATEGORICAL)

    LEVEL = _IdOptionsMember("Level", PlayerHistoryDataOptionType.NUMERICAL)
    """level + (xp/100)"""
    WARS = _IdOptionsMember("Wars", PlayerHistoryDataOptionType.NUMERICAL)
    """wars"""
    PLAYTIME = _IdOptionsMember("Playtime", PlayerHistoryDataOptionType.NUMERICAL)
    """playtime"""
    MOBS_KILLED = _IdOptionsMember("Mobs Killed", PlayerHistoryDataOptionType.NUMERICAL)
    """mobs_killed"""
    CHESTS_FOUND = _IdOptionsMember("Chests Found", PlayerHistoryDataOptionType.NUMERICAL)
    """chests_found"""
    LOGINS = _IdOptionsMember("Logins", PlayerHistoryDataOptionType.NUMERICAL)
    """logins"""
    DEATHS = _IdOptionsMember("Deaths", PlayerHistoryDataOptionType.NUMERICAL)
    """deaths"""
    CHALLENGES = _IdOptionsMember("Challenges", PlayerHistoryDataOptionType.NUMERICAL)
    """hardcord, ultimate_ironman, ironman, craftsman, hunted"""
    PROFESSIONS = _IdOptionsMember("Professions", PlayerHistoryDataOptionType.NUMERICAL)
    """alchemism, armouring, cooking, jeweling, scribing, tailoring, weaponsmithing, woodworking, mining, woodcutting, farming, fishing"""
    COMPLETIONS = _IdOptionsMember("Completions", PlayerHistoryDataOptionType.NUMERICAL)
    """dungeon_completions, quest_completions, raid_completions"""

    @property
    def type(self) -> PlayerHistoryDataOptionType:
        return self.value.type
