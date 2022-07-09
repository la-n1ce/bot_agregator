import discord
from config import TOKEN
import music
from discord.ext import commands
import random

import requests
from bs4 import BeautifulSoup

import json


bot = commands.Bot(command_prefix='.!.')

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.command(pass_context=True)
async def test(ctx, arg):
    await ctx.send(arg)


@bot.command()
async def link_to_mus(ctx, *args):
    #url = 'https://genius.com/Mentaldora-dorafool-lyrics'
    #url = 'https://genius.com/Serega-pirat-dahak-hymn-lyrics'

    url_to_site = f"https://genius.com/api/search/multi?per_page=5&q={'%20'.join(args)}"
    page_site = requests.get(url_to_site)
    content = page_site.text

    url_to_mus = json.loads(content)["response"]["sections"][1]["hits"][0]["result"]["url"]

    page = requests.get(url_to_mus)
    soup = BeautifulSoup(page.text, 'html.parser')
    result_mus = soup.select("#lyrics-root > div:nth-child(2)")
    text = result_mus[0].get_text("\n")
    name_mus = (((text.split('\n'))[0].split("«"))[1].split("»"))[0]
    print(name_mus)

    if name_mus.lower() not in music.musics:
        music.musics[name_mus.lower()] = f'```{text}```'
    print(text)

    await ctx.send(f'```{text}```')


@bot.command()
async def name_to_mus(ctx, *msg):
    url_to_site = f"https://genius.com/search?q={'%20'.join(['гимн', 'дахака'])}"
    page_site = requests.get(url_to_site)
    soup_site = BeautifulSoup(page_site.text, "html.parser")
    result_site = soup_site.select("body > routable-page > ng-outlet > search-results-page > div > div.column_layout > div.column_layout-column_span.column_layout-column_span--primary > div:nth-child(1) > search-result-section > div > div:nth-child(2) > search-result-items > div > search-result-item > div > mini-song-card > a")


    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    result_mus = soup.select("#lyrics-root > div:nth-child(2)")
    text = result_mus[0].get_text("\n")
    name_mus = (((text.split('\n'))[0].split("«"))[1].split("»"))[0]
    print(name_mus)

    if name_mus.lower() not in music.musics:
        music.musics[name_mus.lower()] = f'```{text}```'

    await ctx.send(f'```{text}```')



@bot.command(pass_context=True)
async def give_mus(ctx, *args):
    author_mus, mus = " ".join(args).split(", ")

    if author_mus not in music.musics:
        await ctx.send("Такого автора пока нет.")
        return True

    if all([mus != i for i in music.musics[author_mus]]):
        await ctx.send("Этой песни автора пока нет.")
        return True

    for i in music.musics:
        if i == author_mus:
            for j in music.musics[i]:
                if j == mus:
                    await ctx.send(music.musics[i][j])
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


# kick
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="None"):
    await ctx.channel.purge(limit=1)
    emb = discord.Embed(colour=discord.Color.blue())
    emb.set_footer(text=ctx.message.author.name, icon_url=ctx.author.avatar_url)
    emb.add_field(name='Кик:', value=f'{member.mention} был кикнут', inline=False)
    emb.add_field(name='Причина:', value=reason, inline=False)
    await member.kick()
    await ctx.send(embed=emb)


@kick.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention} Ошибка: не указан обязательный аргумент. `!kick <участник> <причина>`')


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
