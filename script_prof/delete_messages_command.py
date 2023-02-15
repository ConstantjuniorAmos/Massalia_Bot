import os
from dotenv import load_dotenv
load_dotenv(dotenv_path="config")
from discord.ext import commands

import nest_asyncio
nest_asyncio.apply()

bot = commands.Bot(command_prefix="!") 

@bot.event
async def on_ready():
    print("Le bot est prêt.")

@bot.command(name="del")
async def delete(ctx, number_of_messages: int):
    messages = await ctx.channel.history(limit=number_of_messages+1).flatten()
    for each_message in messages:
        await each_message.delete()


bot.run(os.getenv("TOKEN"))