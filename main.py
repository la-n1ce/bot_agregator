import discord
from config import TOKEN
import music
from discord.ext import commands
import random

from youtube_dl import YoutubeDL

import requests
from bs4 import BeautifulSoup

import threading
import logging
import time

import json


songs_list = []

YDL_OPTIONS = {'format': 'worstaudio/best', 'noplaylist': 'False', 'simulate': 'True',
               'preferredquality': '192', 'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

client = commands.Bot(command_prefix=".!.")
print(client.get_user(id))

def thread_function():
    while True:
        print(songs_list)
        if len(songs_list) > 0 and songs_list[0][2]:
            if songs_list[0][0].message.guild.voice_client != None and len(songs_list) > 1 and not songs_list[0][0].message.guild.voice_client.is_playing():
                url = play_mus(songs_list[0][0], songs_list[1])
                songs_list.remove(songs_list[1])
                songs_list[0][1].play(discord.FFmpegPCMAudio(executable="bin\\ffmpeg.exe", source=url, **FFMPEG_OPTIONS))

            if songs_list[0][1] == None:
                for i in range(len(songs_list) - 1):
                    songs_list.remove(songs_list[1])
        time.sleep(1)


x = threading.Thread(target=thread_function)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.command(pass_context=True)
async def test(ctx, arg):
    await ctx.send(arg)


@client.command()
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


@client.command(pass_context=True)
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
@client.command()
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
@client.command()
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
@client.command()
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


def play_mus(ctx, arg):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        if 'https://' in arg:
            info = ydl.extract_info(arg, download=False)
        else:
            info = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]

    url = info['formats'][0]['url']
    return url


@client.command(pass_context=True)
async def play(ctx, *, arg):
    vc, url = None, None
    server = ctx.message.guild
    voice_channel = server.voice_client
    print(voice_channel)

    if voice_channel is not None and voice_channel.is_playing():
        songs_list.append(arg)
        print(songs_list)
    else:
        if voice_channel is not None and not voice_channel.is_playing():
            vc = songs_list[0][1]
            url = play_mus(ctx, arg)
        else:
            vc = await ctx.message.author.voice.channel.connect()
            songs_list.append([ctx, vc, True])
            url = play_mus(ctx, arg)

        print(1)
        vc.play(discord.FFmpegPCMAudio(executable="bin\\ffmpeg.exe", source=url, **FFMPEG_OPTIONS))


@client.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    songs_list[0][2] = False
    if ctx.message.guild.voice_client != None:
        server = ctx.message.guild
        voice_channel = server.voice_client

        voice_channel.pause()
    else:
        await ctx.send("Ты че бота кикнул не играй с ошибками!")


@client.command(name='resume', help='This command resumes the song!')
async def resume(ctx):
    songs_list[0][2] = True
    if ctx.message.guild.voice_client != None:
        server = ctx.message.guild
        voice_channel = server.voice_client

        voice_channel.resume()
    else:
        await ctx.send("Ты че бота кикнул не играй с ошибками!")


@client.command(name='stop', help='This command stops the song!')
async def stop(ctx):
    for i in range(len(songs_list) - 1):
        songs_list.remove(songs_list[1])

    if ctx.message.guild.voice_client != None:
        server = ctx.message.guild
        voice_channel = server.voice_client

        voice_channel.stop()
    else:
        await ctx.send("Ты че бота кикнул не играй с ошибками!")



@client.command(name='next', help='This command skip music!')
async def next(ctx):
    if ctx.message.guild.voice_client != None:
        server = ctx.message.guild
        voice_channel = server.voice_client

        voice_channel.stop()
    else:
        await ctx.send("Ты че бота кикнул не играй с ошибками!")


@client.command(name='leave', help='This command leave from channel!')
async def leave(ctx):
    if ctx.message.guild.voice_client != None:
        await ctx.message.guild.voice_client.disconnect()
    else:
        await ctx.send("Ты че бота кикнул не играй с ошибками!")


x.start()
client.run(TOKEN)
