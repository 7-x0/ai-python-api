import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# تحميل .env
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# تفعيل الصلاحيات
intents = discord.Intents.default()
intents.message_content = True

# إنشاء البوت
bot = commands.Bot(command_prefix="!", intents=intents)

# لما يشتغل
@bot.event
async def on_ready():
    print(f"💙 Phos شغالة: {bot.user}")

# لما أحد يكتب
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await message.reply("هلا 😏")

    await bot.process_commands(message)

# تشغيل البوت
bot.run(TOKEN)