from functools import wraps
import discord
import sys
from discord.ext import commands
from discord import app_commands
from ulearn import Ulearn, Relord
import json_edit
import datetime
import random
import aiohttp
from wcin import get_current_and_next_class
import pytz
import score 

bound_channel_id = 1240297889809305733
Admin_discord_id = 729170921788801074
intents=discord.Intents.all()
intents.members = True
days_of_week = ["一", "二", "三", "四", "五", "六", "日"]

bot = commands.Bot(command_prefix='/', intents=intents)

def check_bound_channel():
    def decorator(func):
        @wraps(func)
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            if bound_channel_id is None:
                await interaction.response.send_message('蘿菠特未綁定到任何頻道。請先使用 /set_channel 命令綁定頻道。', ephemeral=False)
            elif interaction.channel.id == bound_channel_id:
                return await func(interaction, *args, **kwargs)
            else:
                await interaction.response.send_message('此蘿菠特只能在指定頻道中使用。', ephemeral=False)
        return wrapper
    return decorator

class Form(discord.ui.Modal, title='NFU Ulearn 登入'):
    def __init__(self, username=None, password=None, called_by_test=False):
        super().__init__()
        self.Student_ID = discord.ui.TextInput(label='學號', placeholder='NFU 學號', default=username)
        self.Password = discord.ui.TextInput(label='密碼', placeholder='密碼', style=discord.TextStyle.short, required=True, default=password)
        self.called_by_test = called_by_test
        self.add_item(self.Student_ID)
        self.add_item(self.Password)

    async def on_submit(self, interaction: discord.Interaction):
        # 調用 Ulearn 函數
        username = self.Student_ID.value
        password = self.Password.value
        DC_user_id = interaction.user.id
        await interaction.response.send_message('正在嘗試登入...', ephemeral=False)
        retry_count = 0
        ch_name, put_back, error_message = await Ulearn(interaction, username, password, DC_user_id, retry_count, put=False)
        while error_message == "驗證碼錯誤":
            retry_count += 1
            ch_name, put_back, error_message = await Ulearn(interaction, username, password, DC_user_id, retry_count, put=False)
        if ch_name == None: 
            embed = discord.Embed(title="[❎] NFU Ulearn 登入", description=f"登入: {interaction.user.mention}", color=0x1abc9c)
            embed.add_field(name="狀態", value=error_message, inline=True)
            embed.set_footer(text=f"Ulearn 點名 • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
            if not self.called_by_test:
                await interaction.delete_original_response()
            await interaction.followup.send(embed=embed)
        elif put_back == None:
            embed = discord.Embed(title="[✅] NFU Ulearn 登入", description=f"登入: {interaction.user.mention}", color=0x1abc9c)
            embed.add_field(name="姓名", value=ch_name, inline=True)
            embed.add_field(name="學號", value=username, inline=True)
            embed.add_field(name="Discord ID", value=DC_user_id, inline=True)
            embed.set_footer(text=f"Ulearn 點名 • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
            if not self.called_by_test:
                await interaction.delete_original_response()
            await interaction.followup.send(embed=embed)
        elif ch_name:
            embed = discord.Embed(title="[✅] NFU Ulearn 登入", description=f"登入: {interaction.user.mention}", color=0x1abc9c)
            embed.add_field(name="姓名", value=ch_name, inline=True)
            embed.add_field(name="學號", value=username, inline=True)
            embed.add_field(name="Discord ID", value=DC_user_id, inline=True)
            img_path = f"./userimg/{username}.png"
            img_name = f"{username}.png"
            embed.set_image(url=f"attachment://{img_name}")
            embed.set_footer(text=f"Ulearn 點名 • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
            file = discord.File(img_path, filename=img_name)
            if not self.called_by_test:
                await interaction.delete_original_response()
            await interaction.followup.send(embed=embed, files=[file])

class FeedbackModal(discord.ui.Modal, title="問題反饋和新增命令"):
    feedback = discord.ui.TextInput(
        label="請描述你的問題或建議",
        style=discord.TextStyle.paragraph,
        placeholder="輸入你的反饋或建議...",
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        user = await bot.fetch_user(Admin_discord_id)
        embed = discord.Embed(title="NFU Ulearn 反饋", description=f"來自 {interaction.user.name} ({interaction.user.nick}):", color=0x1abc9c)
        embed.add_field(name="反饋:", value=[self.feedback.value], inline=True)
        embed.set_footer(text=f"Ulearn 點名 • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
        await user.send(embed=embed)
        embed = discord.Embed(title="NFU Ulearn 反饋", description="已送達反饋", color=0x1abc9c)
        embed.set_footer(text=f"Ulearn 點名 • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
        await interaction.response.send_message(embed=embed)

class FormButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="點擊此處", custom_id="form_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Form())

class ChannelSelect(discord.ui.Select):
    def __init__(self, channels):
        # 碮保選項列表的長度在 1 到 25 之間
        options = [discord.SelectOption(label=channel.name, value=str(channel.id)) for channel in channels[:25]]
        super().__init__(placeholder='選擇一個頻道來綁定蘿菠特', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        global bound_channel_id
        bound_channel_id = int(self.values[0])
        embed = discord.Embed(title="NFU Ulearn 頻道", description=f'蘿菠特已綁定到頻道: <#{bound_channel_id}>', color=0x1abc9c)
        embed.set_footer(text=f"Ulearn 點名 • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
        await interaction.response.send_message(embed=embed)

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
@check_bound_channel()
async def ulearn_login(interaction: discord.Interaction):
    await interaction.response.send_message('NFU Ulearn 登入:', view=FormButton(), ephemeral=False)

@bot.tree.command(name="test_my_account", description="測試Ulearn帳號是否能正常登入")
@check_bound_channel()
async def test_my_account(interaction: discord.Interaction):
    username, password = json_edit.search(interaction.user.id)
    if username is None:
        embed = discord.Embed(title="NFU Ulearn 測試", description=f'尚無在此蘿菠特綁定帳號', color=0x1abc9c)
        embed.set_footer(text=f"Ulearn 點名 • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
        await interaction.response.send_message(embed=embed)
    else:
        form = Form(username=username, password=password, called_by_test=True)
        await form.on_submit(interaction)

@bot.tree.command(name="分數查詢", description="叫機器人把分數交出來")
@check_bound_channel()
async def scores(interaction: discord.Interaction):
    username, password = json_edit.search(interaction.user.id)
    print(username, password)
    if username is None:
        embed = discord.Embed(title="NFU Ulearn 分數", description=f'尚無在此蘿菠特綁定帳號', color=0x1abc9c)
        embed.set_footer(text=f"Ulearn 點名 • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.defer()
        await score.ecare_login(username, password)
        embed = discord.Embed(title="NFU 成績查詢", description=f"使用者:<@{interaction.user.id}>", color=0x1abc9c)
        img_path = f"./final_output.png"
        img_name = f"final_output.png"
        embed.set_image(url=f"attachment://{img_name}")
        embed.set_footer(text=f"Ulearn 點名 • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
        file = discord.File(img_path, filename=img_name)
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, files=[file])
        else:
            await interaction.response.send_message(embed=embed, file=file)
        
@bot.tree.command(name="十八尖山", description="機器人所在位置")
async def link(interaction: discord.Interaction):
    embed = discord.Embed(title="NFU Ulearn 群連結", description="https://discord.gg/kwmSjxJMc7", color=0x1abc9c)
    embed.set_footer(text=f"Ulearn 點名 • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="修復", description="執行此指令有機會修復機器人")
@check_bound_channel()
async def fix(interaction: discord.Interaction):
    async with aiohttp.ClientSession() as session:
        await Relord(session)
    embed = discord.Embed(title="NFU Ulearn 修復", description="已重新載入 `ulearn.py`", color=0x1abc9c)
    embed.set_footer(text=f"Ulearn 點名 • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="del_my_account", description="刪除在羅波特紀錄的帳號")
@check_bound_channel()
async def del_my_account(interaction: discord.Interaction):
    data = json_edit.del_user(interaction.user.id)
    if data is None:
        embed = discord.Embed(title="NFU Ulearn 註銷", description=f'尚無在此蘿菠特綁定帳號', color=0x1abc9c)
        embed.set_footer(text=f"Ulearn 點名 • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="NFU Ulearn 註銷", description=f'已刪除在此蘿菠特綁定的帳號', color=0x1abc9c)
        embed.add_field(name="使用者", value=interaction.user.mention, inline=True)
        embed.add_field(name="學號", value=data, inline=True)
        embed.set_footer(text=f"Ulearn 點名 • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="code_sign_in", description="數字點名")
@check_bound_channel()
async def ulearn_sign_in(interaction: discord.Interaction, code: str):
    await interaction.response.send_message('正在嘗試簽到...', ephemeral=False)
    for student_id, password, user_id in json_edit.put():
        retry_count = 0
        ch_name, put_back, error_message = await Ulearn(interaction, student_id, password, user_id, retry_count, put=code)
        while error_message == "驗證碼錯誤":
            retry_count += 1
            ch_name, put_back, error_message = await Ulearn(interaction, student_id, password, user_id, retry_count, put=code)
        print(ch_name, put_back, error_message)
        if error_message == "暫無點名":
            user = await bot.fetch_user(user_id)
            embed = discord.Embed(title="NFU Ulearn 簽到", description=f"簽到: <@{user.id}>", color=0x1abc9c)
            embed.add_field(name="簽到狀態", value="❎", inline=True)
            embed.add_field(name="", value="該帳號無法未找到點名中的課堂\n需要自行點名", inline=True)
            embed.set_footer(text=f"Ulearn 點名 • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
            await interaction.followup.send(embed=embed)
        elif put_back:
            user = await bot.fetch_user(user_id)
            embed = discord.Embed(title="NFU Ulearn 簽到", description=f"簽到: <@{user.id}>", color=0x1abc9c)
            embed.add_field(name="簽到狀態", value="✅", inline=True)
            embed.add_field(name="姓名", value=ch_name, inline=True)
            embed.add_field(name="學號", value=student_id, inline=True)
            embed.add_field(name="Discord ID", value=user_id, inline=True)
            embed.set_footer(text=f"Ulearn 點名 • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
            await interaction.followup.send(embed=embed)
        else:
            user = await bot.fetch_user(user_id)
            embed = discord.Embed(title="NFU Ulearn 簽到", description=f"簽到: <@{user.id}>", color=0x1abc9c)
            embed.add_field(name="簽到狀態", value="❎", inline=True)
            embed.add_field(name="姓名", value=ch_name, inline=True)
            embed.add_field(name="學號", value=student_id, inline=True)
            embed.add_field(name="Discord ID", value=user_id, inline=True)
            embed.set_footer(text=f"Ulearn 點名 • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
            await interaction.followup.send(embed=embed)

@bot.tree.command(name="shut_up", description="隨機 使用者/被使用者 將被禁言10秒")
@check_bound_channel()
@app_commands.describe(user="選擇一個伺服器用戶")
async def shut_up(interaction: discord.Interaction, user: discord.Member):
    target_user = interaction.user if random.randint(0, 1) == 1 else user
    try:
        await target_user.timeout(datetime.timedelta(seconds=10), reason="被禁言10秒")
        await interaction.response.send_message(f'閉嘴 <@{target_user.id}> 禁言10秒', ephemeral=False)
    except discord.Forbidden:
        await interaction.response.send_message(f'具有管理員權限 <@{target_user.id}> (無法禁言)。禁止使用機器人15秒', ephemeral=False)

@bot.tree.command(name="課表", description="課表")
@check_bound_channel()
async def school_timetable(interaction: discord.Interaction):
    embed = discord.Embed(title="NFU 五資一甲 課表", color=0x1abc9c)
    img_path = f"./school_timetable.png"
    img_name = f"school_timetable.png"
    embed.set_image(url=f"attachment://{img_name}")
    embed.set_footer(text=f"Ulearn 點名 • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
    file = discord.File(img_path, filename=img_name)
    if interaction.response.is_done():
        await interaction.followup.send(embed=embed, files=[file])
    else:
        await interaction.response.send_message(embed=embed, file=file)

@bot.tree.command(name="下節甚麼課", description="下節甚麼課")
@check_bound_channel()
async def wcin(interaction: discord.Interaction):
    target_timezone = pytz.timezone('Asia/Taipei')
    now = datetime.datetime.now(target_timezone)
    current_time = now.strftime("%H:%M")
    current_day = days_of_week[now.weekday()]
    current_status, current_subject, current_location, remaining_minutes, next_status, next_subject, next_location = get_current_and_next_class(current_day, current_time)
    embed = discord.Embed(title="NFU Ulearn 課堂", color=0x1abc9c)
    embed.add_field(name="目前時間", value=f"星期{current_day} [{current_time}]", inline=True)
    print(remaining_minutes)
    print(type(remaining_minutes))
    if remaining_minutes is None: remaining_minutes = "現在為下課/放學時間"
    embed.add_field(name="還有多久下課", value=f"{remaining_minutes}", inline=True)
    embed.add_field(name="這節課", value=f"{current_status} - {current_subject} ({current_location})", inline=True)
    embed.add_field(name="下節課", value=f"{next_status} - {next_subject} ({next_location})", inline=True)
    embed.set_footer(text=f"Ulearn 點名 • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="教學問卷", description="教學問卷")
async def survey(interaction: discord.Interaction):
    embed = discord.Embed(title="NFU Ulearn 教學問卷", description="https://qsurvey.nfu.edu.tw/survey/mySurvey", color=0x1abc9c)
    embed.set_footer(text=f"Ulearn 點名 • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="反饋", description="希望新增/問題反饋")
async def feedback(interaction: discord.Interaction):
    await interaction.response.send_modal(FeedbackModal())

@bot.tree.command(name="test", description="測試(可能會是各種奇怪的功能)")
async def test(interaction: discord.Interaction):
    if interaction.user.voice and interaction.user.voice.channel:
        channel = interaction.user.voice.channel
        try:
            await channel.connect()
        except Exception as e:
            pass
bot.run('MTI0MDI5NTcxNjAzMTgyNzk5OA.GLzzuT.VHHNgIbgM6zQPuAO0jBtV8EC6WDJSkf6bgH6w4')
