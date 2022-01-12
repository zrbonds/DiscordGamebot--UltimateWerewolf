# @author Zack Bonds
#
# A class representing a Player in the game
# has the associated information
class Player:
    # The user associated with this Player object
    user = 0

    # The role this user will be playing
    role = 0

    # Whether or not the user is currently living
    living = True

    def __init__(self, user, role):
        self.user = user
        self.role = role
        self.living = True

    def is_alive(self):
        return self.living
