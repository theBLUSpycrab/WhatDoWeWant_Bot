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
    DEVELOPEMENT_GUILD = None

DESIRED_CHANNEL_NAME = "What Do We Want"
FUZZY_CHANNEL_NAME = False
FUZZY_ACTIVITY_NAME = True

# -- program start--
import discord
from discord import app_commands
from discord.ext import tasks
import classes as cl
import logic as lc
import pandas as pd

user_list = {}
server_channel_list = {}


class BotClient(discord.Client):
    def __init__(self):
        intents=discord.Intents.default()
        intents.guilds = True
        intents.messages = True

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

    async def on_guild_join(self, guild):
        if guild.system_channel:
            await guild.system_channel.send("Please set my working channel with '/setchannel' (Admins only)")

Bot = BotClient()

@Bot.tree.command(name="hello_world", description="Say hello")
async def hello_world(interaction: discord.Interaction):
    if interaction.channel_id == server_channel_list[interaction.guild_id]:
        print("recieved hello")
        await interaction.response.send_message(f"Acknowledged.\nDeleting in 10 seconds.")
        response = await interaction.original_response()
        await response.delete(delay=10)

@Bot.tree.command(name="add", description="add an activity to the list")
@app_commands.describe(activity="name of activity")
async def add(interaction: discord.Interaction, activity: str):
    if interaction.channel_id == server_channel_list[interaction.guild_id]:
        userID = interaction.user.id
        userName = await Bot.fetch_user(userID)
        guildID = interaction.guild_id

        activity_value = activity.upper()
        user_list.setdefault(userID, {}).setdefault("activity", [])
        user_list.setdefault(userID, {}).setdefault("guilidID", [])
        
        if activity_value not in user_list[userID]["activity"]:
            user_list[userID]["activity"].append(activity_value)

            if guildID not in user_list[userID]["guilidID"]:
                user_list[userID]["guilidID"].append(guildID)

            await interaction.response.send_message(f"added {activity} to {userName.global_name} in {}")
        else:
            await interaction.response.send_message(f"{activity} already added to {userName.global_name}")

        if DEVELOPEMENT:
            print(user_list)

@Bot.tree.command(name="remove", description="remove an activity from the list")
@app_commands.describe(activity="name of activity")
async def remove(interaction: discord.Interaction, activity: str):
    if interaction.channel_id == server_channel_list[interaction.guild_id]:
        userID = interaction.user.id
        userName = await Bot.fetch_user(userID)
        
        activity_value = activity.upper()

        if activity_value in user_list.get(userID, {}).get("activity", []):
            user_list[userID]["activity"].remove(activity_value)
            await interaction.response.send_message(f"removed {activity} from {userName.global_name}")
        else:
            await interaction.response.send_message(f"did not find {activity} from {userName.global_name}")

        if DEVELOPEMENT:
            print(user_list)

@Bot.tree.command(name="setchannel", description="Set the channel to be used in (Admins only)")
@app_commands.describe(activity="Set the channel to be used in (Admins only)")
@app_commands.checks.has_permissions(administrator=True)
async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
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

@tasks.loop(minutes=1)
async def list_of_interests(client: BotClient):
    if DEVELOPEMENT: print("running loop")
    for guildID, channelID in server_channel_list.items():
        try:
            channel = client.get_channel(channelID)
            if channel: 
                msg = await channel.send("heartbeat")
                await msg.delete(delay=10)
        except:
            print(f"no channel set for {client.get_guild(guildID)}")


# -- run bot
tokenfile = open("token.txt", mode="r")
token = tokenfile.read()

print("\nStarting Bot")
Bot.run(token)
