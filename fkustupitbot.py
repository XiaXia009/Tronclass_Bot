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
        user_id = interaction.user.id
        await Ulearn(interaction, username, password, user_id)

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
        await interaction.response.send_message(f'蘿菠特已綁定到頻道: <#{bound_channel_id}>', ephemeral=False)

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
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message('只有管理員可以設定蘿菠特綁定的頻道。', ephemeral=True)
        return

    guild = interaction.guild
    channels = [channel for channel in guild.text_channels if channel.permissions_for(guild.me).send_messages]
    if channels:
        await interaction.response.send_message('選擇一個頻道來綁定蘿菠特:', view=ChannelSelectView(channels), ephemeral=True)

@bot.tree.command(name="ulearn_login", description="向蘿菠特登入帳號")
async def ulearn_login(interaction: discord.Interaction):
    if bound_channel_id is None:
        await interaction.response.send_message('蘿菠特未綁定到任何頻道。請先使用 /set_channel 命令綁定頻道。', ephemeral=False)
    elif interaction.channel.id == bound_channel_id:
        await interaction.response.send_message('NFU Ulearn 登入:', view=FormButton(), ephemeral=False)
    else:
        await interaction.response.send_message('此蘿菠特只能在指定頻道中使用。', ephemeral=False)

@bot.tree.command(name="13", description="測試(可能會是各種奇怪的功能)")
async def test(interaction: discord.Interaction):
    if bound_channel_id is None:
        await interaction.response.send_message('蘿菠特未綁定到任何頻道。請先使用 /set_channel 命令綁定頻道。', ephemeral=False)
    elif interaction.channel.id == bound_channel_id:
        await interaction.response.send_message(f'你的使用者ID:{interaction.user.id}', ephemeral=False)
    else:
        await interaction.response.send_message('此蘿菠特只能在指定頻道中使用。', ephemeral=False)

@bot.tree.command(name="test", description="地震報告")
async def earthquake_report(interaction: discord.Interaction):
    embed = discord.Embed(title="Taiwan EEW System", description="臺灣東部海域發生規模3.5有感地震，最大震度花蓮縣和平、宜蘭縣南澳2級。", color=0x1abc9c)
    
    embed.add_field(name="經度", value="無\n(小區域有感地震)", inline=True)
    embed.add_field(name="發生時間", value="2024年5月11日\n03:57:30", inline=True)
    embed.add_field(name="震央位置", value="花蓮縣政府東北方35.2公里\n(位於臺灣東部海域)", inline=True)
    embed.add_field(name="規模", value="芮氏 3.5\n(微小)", inline=True)
    embed.add_field(name="深度", value="79.9公里\n(極淺層)", inline=True)
    embed.add_field(name="最大震度", value="2級\n(花蓮縣, 和平)", inline=True)
    embed.add_field(name="最大震度 2級 地區", value="花蓮縣\n宜蘭縣", inline=True)

    embed.set_image(url="https://ulearn.nfu.edu.tw/static/assets/images/favicon-b420ac72.ico")
    embed.set_footer(text="臺灣交通部中央氣象署 • 2024/05/11 04:00")

    file = discord.File("/mnt/data/image.png", filename="image.png")
    await interaction.response.send_message(file=file, embed=embed)

bot.run('MTI0MDI5NTcxNjAzMTgyNzk5OA.GtIbBH.fq3rriVOFdGvyIBU0rafQc3LhlyxVHxWRkmlEE')