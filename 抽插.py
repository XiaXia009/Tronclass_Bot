import discord
from discord.ext import commands
import time
# 設置必要的意圖
intents = discord.Intents.default()
intents.members = True
intents.voice_states = True


bot = commands.Bot(command_prefix='/', description='', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
    channel_id = 1218840782623084655
    channel = bot.get_channel(channel_id)
    #if channel and isinstance(channel, discord.VoiceChannel):
        #voice_client = await channel.connect()
    while True:
        time.sleep(0.08)
        if channel and isinstance(channel, discord.VoiceChannel):
            voice_client = await channel.connect()
            time.sleep(0.08)
        await voice_client.disconnect()

bot.run('MTI0MDI5NTcxNjAzMTgyNzk5OA.GLzzuT.VHHNgIbgM6zQPuAO0jBtV8EC6WDJSkf6bgH6w4')