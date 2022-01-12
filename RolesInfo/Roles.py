# @author Zack Bonds
#
# The enumeration of roles that exist to be chosen from
# To add a role, add one of these
from enum import Enum, unique, auto


@unique
class Roles(Enum):
    VILLAGER = auto()
    WEREWOLF = auto()
    SEER = auto()
    BODYGUARD = auto()

