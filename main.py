import discord
import asyncio
from config import TOKEN
from music import musics
from discord.ext import commands
import random

bot = commands.Bot(command_prefix='.!.')

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.command(pass_context=True)
async def test(ctx, arg):
    await ctx.send(arg)


@bot.command(pass_context=True)
async def give_mus(ctx, *args):
    author_mus, mus = " ".join(args).split(", ")

    if author_mus not in musics:
        await ctx.send("Такого автора пока нет.")
        return True

    if all([mus != i for i in musics[author_mus]]):
        await ctx.send("Этой песни автора пока нет.")
        return True

    for i in musics:
        if i == author_mus:
            for j in musics[i]:
                if j == mus:
                    await ctx.send(musics[i][j])
                    return True


# clear
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=1):
    if amount != 0:
        await ctx.channel.purge(limit=(amount + 1))
    else:
        await ctx.channel.purge()


@clear.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention} Ошибка: не указан обязательный аргумент. `!clear <кол-во сообщений>`')


#lot
@bot.command()
async def lot(ctx):
    lot = ''
    for i in range(0, 5):
        if random.randint(1, 2) == 1:
            lot += '--||в||'
        else:
            lot += '--||п||'
    lot += '--'
    print(lot)
    await ctx.send(lot)


bot.run(TOKEN)
