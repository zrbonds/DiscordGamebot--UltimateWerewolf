# @author Zack bonds
# @date 5/15/2021
#
# The main method. Initializes the game state, runs the necessary methods.
import asyncio
from random import randint

# Token Security Process
from dotenv import load_dotenv
import os

import operator
import discord
from discord.ext import commands
from discord.ext.commands import CommandInvokeError

from Player import Player
import RolesInfo
from RolesInfo import Roles
from WerewolfGame import WerewolfGame
from RolesInfo import Werewolf
from RolesInfo import Villager

description = 'A bot with which to play ultimate werewolf over discord'
bot = commands.Bot(command_prefix='!', description=description)

# The game object! The one and only.
game = WerewolfGame()

# Some useful booleans for our game
global has_started
has_started = False


#######################
### USEFUL COMMANDS ###
#######################
@bot.command()
async def see_players(ctx, *args):
    if len(game.users) == 0:
        await ctx.send("There are currently no players. Join the game by typing \'!add_me\'")
        return
    active_players = 'The players are: ' + ', '.join(e.display_name for e in game.users)
    await ctx.send(active_players)


@bot.command()
async def see_roles(ctx, *args):
    if len(game.active_roles) == 0:
        await ctx.send("There are currently no loaded roles. Load roles by typing \'!load_roles\' followed " +
                       "by the role names.")
        return
    roles = 'The roles are: ' + ', '.join(e for e in game.active_roles)
    await ctx.send(roles)


@bot.command()
async def role_choices(ctx, *args):
    await ctx.send("Currently implemented roles are: \nWerewolf, Villager, Seer, Bodyguard")


@bot.command()
async def role_help(ctx, *args):
    role_name_list = list(args)
    role_name = role_name_list[0]
    if role_name.upper() ==  "WEREWOLF":
        await ctx.send("The Werewolf chooses a target to kill each night. If there is more than one Werewolf, "
                       "they vote on the target. The Werewolf wins when every other member of the village is dead.")
    if role_name.upper() == "VILLAGER":
        await ctx.send("The Villager is a generic townsperson, they have no actions at night. The Villager wins when "
                       "all the Werewolves are dead.")
    if role_name.upper() == "SEER":
        await ctx.send("The Seer is a townsperson, who learns the role of another player each night. The Seer wins "
                       "with the townspeople when the Werewolves are dead.")
    if role_name.upper() == "BODYGUARD":
        await ctx.send("The Bodyguard is a townsperson, who chooses a player to protect each night. That player "
                       "cannot be killed by the Werewolves. Each player may only be chosen once. The Bodyguard wins "
                       "with the townspeople when the Werewolves are dead.")

#######################
## STARTING THE GAME ##
#######################


@bot.event
async def on_ready():
    print('I\'m... alive')


@bot.command()
async def startup(ctx, *args):
    global has_started
    has_started = False
    await ctx.send('I\'m... alive. Who will be playing?')


@bot.command()
async def add_me(ctx, *args):
    global has_started
    if has_started:
        return
    if ctx.author in game.users:
        await ctx.send('{0} is already in the game.'.format(ctx.author.display_name))
    else:
        game.users.append(ctx.author)
        await ctx.send('{0} has been added!'.format(ctx.author.display_name))


@bot.command()
async def load_roles(ctx, *args):
    if has_started:
        return
    roles = list(args)
    game.active_roles = roles
    await ctx.send("The roles have been loaded!")


@bot.command()
async def start(ctx, *args):
    # Mark the game as started
    global has_started
    has_started = True

    # Convert the players into Player objects
    for user in game.users:
        player_role_name = game.active_roles[randint(0, len(game.active_roles) - 1)]
        if player_role_name.upper() == 'WEREWOLF':
            player_role = 'Werewolf'
        elif player_role_name.upper() == 'VILLAGER':
            player_role = 'Villager'
        elif player_role_name.upper() == 'SEER':
            player_role = 'Seer'
        elif player_role_name.upper() == 'BODYGUARD':
            player_role = 'Bodyguard'
        new_player = Player(user, player_role)
        game.players.add(new_player)
        game.active_roles.remove(player_role_name)
        await user.send("Your role is " + player_role_name)

    # Begin the gameplay loop

    game_continues = True
    while game_continues:
        ####### Night
        await ctx.send("Night has fallen! Go to sleep... and check your DM's")

        # Execute Each Players Role
        killed_player = 0
        killed_player_name = 0
        protected_player_name = 0
        protected_name_list = list()
        target_list = list()
        for player in game.players:

            # Check if the response is valid
            def check(m):
                target = m.content
                for possible_target in game.players:
                    name = possible_target.user.display_name
                    if name == target:
                        return True
                return False

            def bodyguard_check(m):
                target = m.content
                if target in protected_name_list:
                    return False
                for possible_target in game.players:
                    name = possible_target.user.display_name
                    if name == target:
                        return True
                return False

            # Werewolf
            if player.role == 'Werewolf':
                await player.user.send('Who would you like to kill?')

                # Wait for a valid target message
                msg = await bot.wait_for('message', check=check)

                # Remove the killed player from the game
                proposed = msg.content
                for seen in game.players:
                    name1 = seen.user.display_name
                    if name1 == proposed:
                        target_list.append(seen)
                        break

            # Bodyguard
            if player.role == 'Bodyguard':
                await player.user.send('Who would you like to protect? Remember you can\'t protect someone more than '
                                       'once per game')

                # Wait for a valid target message
                msg = await bot.wait_for('message', check=bodyguard_check)

                proposed = msg.content
                for seen in game.players:
                    name1 = seen.user.display_name
                    if name1 == proposed:
                        protected_player_name = name1
                        protected_name_list.append(name1)
                        break

            # Seer
            if player.role == 'Seer':
                await player.user.send('Who would you like to learn more about?')

                # Wait for a valid target message
                msg = await bot.wait_for('message', check=check)

                proposed = msg.content
                for seen in game.players:
                    name1 = seen.user.display_name
                    if name1 == proposed:
                        await player.user.send(seen.user.display_name + " is a " + seen.role)
                        break

        # Who did the Werewolves vote for?
        count_dict = dict()
        for target1 in target_list:
            count_dict[target1] = 0
        for target1 in target_list:
            count_dict[target1] = count_dict[target1] + 1
        voting_list = sorted(count_dict.items(), key=operator.itemgetter(1), reverse=True)
        killed_player = voting_list[0][0]
        killed_player_name = killed_player.user.display_name

        if protected_player_name == killed_player_name:
            print("Bodyguard protected target.")
        else:
            try:
                game.players.remove(killed_player)
                game.users.remove(killed_player.user)
                await ctx.send(
                    '{0} has been killed!'.format(killed_player_name))
            except (CommandInvokeError, KeyError):
                print("Illogical game state-- no target acquired.")

        # Check to see if there's any werewolves left
        if len(game.players) == 0:
            print("Illogical game state-- no living players remaining")
            await ctx.send('Game over! Everyone\'s friggin dead!')
            game_continues = False
            break
        if game.wolves_win():
            await ctx.send('Game over! Werewolves win!')
            game_continues = False
            break
        if game.villagers_win():
            await ctx.send('Game over! Villagers win!')
            game_continues = False
            break

        await ctx.send('Who can we trust? You have 3 minutes to discuss.')
        await asyncio.sleep(10)
        await ctx.send('Time is up! Who is the first to be nominated?')

        # Find the nominee
        nominees = list()

        def person_check(m):
            target = m.content
            for possible_target in game.players:
                name = possible_target.user.display_name
                if name == target:
                    return True
            return False

        msg = await bot.wait_for('message', check=person_check)

        # Add the first person to the list
        proposed = msg.content
        for seen in game.players:
            name1 = seen.user.display_name
            if name1 == proposed:
                nominees.append(seen)
                break
        await ctx.send(proposed + " has been nominated! Who's next?")

        def person_check2(m):
            target = m.content
            if target == nominees[0].user.display_name:
                return False
            for possible_target in game.players:
                name = possible_target.user.display_name
                if name == target:
                    return True
            return False

        msg = await bot.wait_for('message', check=person_check2)

        proposed = msg.content
        for seen in game.players:
            name1 = seen.user.display_name
            if name1 == proposed:
                nominees.append(seen)
                break

        await ctx.send('The nominees have been chosen! Voting begins now. You have 60 seconds.')

        # Handle the voting
        msg2 = await ctx.send(
            'Respond 1 or 2 for either ' + ' or '.join(e.user.display_name for e in nominees) + ' respectively.')
        await asyncio.sleep(60)
        msg = await ctx.fetch_message(msg2.id)

        # Count the votes
        reactions = msg.reactions
        ones = reactions.count(reactions[0])
        twos = reactions.count(reactions[1])
        voted_out_player = 0
        if ones > twos:
            voting_target = nominees[0]
        else:
            voting_target = nominees[1]
        for seen in game.players:
            name1 = seen.user.display_name
            if name1 == voting_target.user.display_name:
                game.players.remove(seen)
                game.users.remove(seen.user)
                voted_out_player = seen
                break
        await ctx.send('{0} has been voted out!'.format(voted_out_player.user.display_name))

        # Check to see if there's any werewolves left
        if len(game.players) == 0:
            print("Illogical game state-- no living players remaining")
            await ctx.send('Game over! Everyone\'s friggin dead!')
            game_continues = False
            break
        if game.wolves_win():
            await ctx.send('Game over! Werewolves win!')
            game_continues = False
            break
        if game.villagers_win():
            await ctx.send('Game over! Villagers win!')
            game_continues = False
            break


load_dotenv('.env')
bot.run(os.getenv('BOT_TOKEN'))
