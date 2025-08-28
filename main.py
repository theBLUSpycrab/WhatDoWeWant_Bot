# -- important for logging --
#import logging
#logging.basicConfig(level=logging.INFO)

# -- configuration (C style macros) --
DEVELOPEMENT = True

if DEVELOPEMENT:
    dev_guildfile = open("dev_guildfile.txt", mode="r")
    dev_guild = dev_guildfile.read()
    DEVELOPEMENT_GUILD = dev_guild
else:
    DEVELOPEMENT_GUILD = 0

DESIRED_CHANNEL_NAME = "What Do We Want"
FUZZY_CHANNEL_NAME = False
FUZZY_ACTIVITY_NAME = True

# -- program start--
import discord
from discord import app_commands
from discord.ext import tasks
import classes as cl
import custom_logic as clc
import pandas as pd
from sortedcontainers import SortedDict

# -- class definitions --
class User:
    def __init__(self, userID: int=-1, guildID_list: list=[], activity_list: dict={}):
        self.userID = userID
        self.guildID_list = guildID_list
        self.activity_list = SortedDict(activity_list)

class BotClient(discord.Client):
    def __init__(self):
        intents=discord.Intents.default()
        intents.guilds = True
        intents.messages = True
        intents.members = True

        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        if DEVELOPEMENT:
            guild = discord.Object(id=DEVELOPEMENT_GUILD)
            self.tree.copy_global_to(guild=guild)
            for cmd in await self.tree.fetch_commands():
                await cmd.delete()
            await self.tree.sync(guild=guild)
        else:
            for cmd in await self.tree.fetch_commands():
                await cmd.delete()
            await self.tree.sync()
        
        list_of_interests.start(self)
        matchmaker.start(self)

    async def on_guild_join(self, guild):
        if guild.system_channel:
            await guild.system_channel.send("Please set my working channel with '/setchannel' (Admins only)")

# -- funcion definitions --
def PrintUserList(list: list[User]):
    for user in list:
        print(user.userID, user.activity_list, user.guildID_list)

def PublishDesires(users: list[User], guilds: dict[int, int]):
    for guild in guilds:
        pass #TODO



# -- globals --
user_list: list[User] = []
server_channel_list = {}

Bot = BotClient()

@Bot.tree.command(name="hello_world", description="Say hello")
async def hello_world(interaction: discord.Interaction):
    """
    A Discord slash command that responds with a temporary acknowledgement message.
    """
    if interaction.channel_id == server_channel_list[interaction.guild_id]:
        print("recieved hello")
        await interaction.response.send_message(f"Acknowledged.\nDeleting in 10 seconds.")
        response = await interaction.original_response()
        await response.delete(delay=10)


@Bot.tree.command(name="add", description="add an activity to the list")
@app_commands.describe(activity="name of activity", minimum_people="minimum number of people")
async def add(interaction: discord.Interaction, activity: str, minimum_people: int):
    """
    A Discord slash command that allows users to add or update activities in their personal activity list.

    Behavior:
      - Only works if invoked in the designated server channel for the guild.
      - Fetches the invoking user's ID and display name.
      - Converts the provided activity name to uppercase for consistency.
      - Checks if the user already exists in the global `user_list`:
          • If the user exists and the activity is new:
              - Adds the activity with its minimum required people.
              - Ensures the user's guild list is updated with the current guild.
              - Sends a confirmation message.
          • If the user exists and the activity already exists:
              - Updates the minimum required people for that activity.
              - Sends a confirmation message.
          • If the user does not exist:
              - Creates a new `User` object with the activity and guild association.
              - Appends it to `user_list`.
              - Sends a confirmation message.
      - If development mode (`DEVELOPEMENT`) is enabled, prints the current state of `user_list` for debugging.

    Args:
        interaction (discord.Interaction): The interaction object representing the slash command invocation.
        activity (str): The name of the activity to add or update.
        minimum_people (int): The minimum number of people required for the activity.

    Returns:
        None: The command completes asynchronously after updating the data and sending a response message.
    """
    if interaction.channel_id == server_channel_list[interaction.guild_id]:
        userID = interaction.user.id
        userName = await Bot.fetch_user(userID)
        guildID = interaction.guild_id

        activity_value = activity.upper()
        user_new = True
        
        for user in user_list:
            if user.userID == userID:
                user_new = False

                user.activity_list[activity_value] = minimum_people

                if guildID not in user.guildID_list:
                    for guild in Bot.guilds:  # update all guild IDs
                        if guild.get_member(userID):
                            user.guildID_list.append(guildID)

                await interaction.response.send_message(f"Added/Updated {activity} for {userName.global_name}")
                break
        
        if user_new:
            new_user = User(userID,[guildID],{activity_value: minimum_people})
            user_list.append(new_user)
            print(user_list[-1].userID)
            await interaction.response.send_message(f"added {activity} to new user {userName.global_name}")
                

        if DEVELOPEMENT:
            print("user_list:")
            PrintUserList(user_list)


@Bot.tree.command(name="remove", description="remove an activity from the list")
@app_commands.describe(activity="name of activity")
async def remove(interaction: discord.Interaction, activity: str):
    """
    A Discord slash command that removes an activity from a user's personal activity list.

    Behavior:
    - Only executes if the command is run in the designated server channel for the guild.
    - Fetches the invoking user's ID and display name.
    - Converts the provided activity name to uppercase to ensure consistency.
    - Searches for the user in the global `user_list`:
        • If the user exists and the activity is found:
            - Removes the activity from the user's list.
            - Sends a confirmation message.
        • If the user exists but the activity is not found:
            - Sends a message indicating the activity was not found.
        • If the user does not exist in `user_list`:
            - (No message is currently sent — function simply ends).
    - If development mode (`DEVELOPEMENT`) is enabled, prints the current state of `user_list` for debugging.

    Args:
        interaction (discord.Interaction): The interaction object representing the slash command invocation.
        activity (str): The name of the activity to remove.

    Returns:
        None: The command completes asynchronously after updating data and 
            sending a response message.
    """
    if interaction.channel_id == server_channel_list[interaction.guild_id]:
        userID = interaction.user.id
        userName = await Bot.fetch_user(userID)
        
        activity_value = activity.upper()

        for user in user_list:
            if user.userID == userID:
                if activity_value in user.activity_list:
                    del user.activity_list[activity_value]
                    await interaction.response.send_message(f"removed {activity} from {userName.global_name}")
                else:
                    await interaction.response.send_message(f"did not find {activity} from {userName.global_name}")
                break

        if DEVELOPEMENT:
            print("\nuser_list:")
            PrintUserList(user_list)


@Bot.tree.command(name="setchannel", description="Set the channel to be used in (Admins only)")
@app_commands.describe(channel="Set the channel to be used in (Admins only)")
@app_commands.checks.has_permissions(administrator=True)
async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    """
    A Discord slash command (admin-only) that sets the designated channel for bot operations in the current guild.

    Behavior:
      - Restricted to administrators via `@app_commands.checks.has_permissions`.
      - Stores the provided channel ID in the global `server_channel_list` under the guild's ID.
      - Sends a confirmation message tagging the new channel, which will auto-delete after 10 seconds.
      - If an error occurs while sending the confirmation message, sends a fallback error message and logs the issue to console.
      - If development mode (`DEVELOPEMENT`) is enabled:
          • Deletes the response after 10 seconds.
          • Prints the current state of `server_channel_list` for debugging.

    Args:
        interaction (discord.Interaction): The interaction object representing the slash command invocation.
        channel (discord.TextChannel): The Discord text channel to set as the designated bot channel for the guild.

    Returns:
        None: The command completes asynchronously after updating the stored channel ID and sending a response.
    """
    guildID = interaction.guild_id
    channelID = channel.id

    server_channel_list[guildID] = channelID
    try:
        await interaction.response.send_message(f"Operating in {channel.mention} now\nDeleting in 10 seconds...")
    except:
        await interaction.response.send_message(f"Set channel error\nDeleting in 10 seconds...")
        print("set_channel error")

    if DEVELOPEMENT:
        response = await interaction.original_response()
        await response.delete(delay=10)
        print("\nserver_channel_list",server_channel_list)


@tasks.loop(minutes=3)
async def matchmaker(client: BotClient):
    for guildID, channelID in server_channel_list.items():
            try:
                channel = client.get_channel(channelID)
                if channel: 
                    msg = await channel.send("matching now ...")
                    
            except:
                print(f"no channel set for {client.get_guild(guildID)}")
    
    activities = []
    users = []

    for user in user_list:
        activities.append(list(user.activity_list.keys()))
        users.append(user.userID)

    all_matches, full_matches, partial_matches, max_count = clc.multiway_match_strings(activities,users)
    print()
    for activity, count, who in all_matches:
        print(f"{activity} x {count} in {who}")
    


if DEVELOPEMENT: # hearbeat task
    @tasks.loop(minutes=1)
    async def list_of_interests(client: BotClient):
        for guildID, channelID in server_channel_list.items():
            try:
                channel = client.get_channel(channelID)
                if channel: 
                    msg = await channel.send("heartbeat")
                    await msg.delete(delay=30)
            except:
                print(f"no channel set for {client.get_guild(guildID)}")



# -- run bot
tokenfile = open("token.txt", mode="r")
token = tokenfile.read()

print("\nStarting Bot")
Bot.run(token)
