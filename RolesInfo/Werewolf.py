# @author Zack Bonds
#
# A class representing a werewolf in the game
# has the associated information
from RolesInfo import Roles
from RolesInfo.Roles import Roles
from discord import User


class Werewolf:
    # The balance value, for game balance calculation
    BALANCE_VAL = -6

    # The name of the class, for information parsing purposes
    CLASS_NAME = 'werewolf'

    # The role enumeration value of the class
    ROLE = Roles.WEREWOLF
