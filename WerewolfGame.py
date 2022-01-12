# @author Zack Bonds
# @date 5/15/2021
#
# This represents an instance of the player game including all the objects that the
# game must include.
import RolesInfo
from RolesInfo import Roles


class WerewolfGame:
    # The name of the roles in the game
    active_roles = list()

    # The name of the players in the game
    users = set()

    # The Player objects in the game
    players = set()

    # The current state of the game
    game_state = 0

    def __init__(self, active_roles=[], player_names=[]):
        self.active_roles = active_roles
        self.users = player_names
        self.game_state = 0

    def wolves_win(self):
        for player in self.players:
            if player.role == 'Villager' or player.role == 'Seer' or player.role == 'Bodyguard':
                return False
        return True

    def villagers_win(self):
        for player in self.players:
            if player.role == 'Werewolf':
                return False
        return True
