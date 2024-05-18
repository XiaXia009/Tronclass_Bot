import discord
from discord.ext import commands
from discord import app_commands
from ulearn import Ulearn  # Import Ulearn function from ulearn.py

# 初始化綁定頻道 ID 為 None
bound_channel_id = None

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

class Form(discord.ui.Modal, title='NFU Ulearn 登入'):
    Student_ID = discord.ui.TextInput(label='學號', placeholder='NFU 學號')
    Password = discord.ui.TextInput(label='密碼', placeholder='密碼', style=discord.TextStyle.short, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        # 調用 Ulearn 函數
        username = self.Student_ID.value
        password = self.Password.value
        await Ulearn(interaction, username, password)

class FormButton(discord.ui.View):
    @discord.ui.button(label="點擊此處", custom_id="form_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Form())

class ChannelSelect(discord.ui.Select):
    def __init__(self, channels):
        # 確保選項列表的長度在 1 到 25 之間
        options = [discord.SelectOption(label=channel.name, value=str(channel.id)) for channel in channels[:25]]
        super().__init__(placeholder='選擇一個頻道來綁定蘿菠特', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        global bound_channel_id
        bound_channel_id = int(self.values[0])
        # 只在選定頻道中發送公開消息
        channel = interaction.guild.get_channel(bound_channel_id)
        if channel:
            await channel.send(f'蘿菠特已成功綁定到此頻道: <#{bound_channel_id}>')
        await interaction.response.send_message(f'蘿菠特已綁定到頻道: <#{bound_channel_id}>', ephemeral=True)

class ChannelSelectView(discord.ui.View):
    def __init__(self, channels):
        super().__init__()
        self.add_item(ChannelSelect(channels))

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.tree.command(name="set_channel", description="設定蘿菠特綁定的頻道")
async def set_channel(interaction: discord.Interaction):
    # 檢查是否為管理員
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message('只有管理員可以設定蘿菠特綁定的頻道。', ephemeral=True)
        return

    guild = interaction.guild
    channels = [channel for channel in guild.text_channels if channel.permissions_for(guild.me).send_messages]
    if channels:
        await interaction.response.send_message('選擇一個頻道來綁定蘿菠特:', view=ChannelSelectView(channels), ephemeral=True)
    else:
        await interaction.response.send_message('沒有可用的頻道來綁定蘿菠特。', ephemeral=True)

@bot.tree.command(name="ulearn_login", description="向蘿菠特登入帳號")
async def ulearn_login(interaction: discord.Interaction):
    if bound_channel_id is None:
        await interaction.response.send_message('蘿菠特未綁定到任何頻道。請先使用 /set_channel 命令綁定頻道。', ephemeral=False)
    elif interaction.channel.id == bound_channel_id:
        await interaction.response.send_message('NFU Ulearn 登入:', view=FormButton(), ephemeral=False)
    else:
        await interaction.response.send_message('此蘿菠特只能在指定頻道中使用。', ephemeral=False)

bot.run('MTI0MDI5NTcxNjAzMTgyNzk5OA.GtIbBH.fq3rriVOFdGvyIBU0rafQc3LhlyxVHxWRkmlEE')