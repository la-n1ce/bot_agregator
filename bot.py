import asyncio
import discord
import json
from discord.ext import commands
import random
import time


def open_json():
    with open('bot.json', 'r', encoding='utf-8') as f:
        file = json.load(f)
        return file


def write_json(file):
    with open('bot.json', 'w') as jf:
        json.dump(file, jf, indent=4)


def get_dict_index(mas, key, value):
    for mas_dict in mas:
        if mas_dict[key] == value:
            index = mas.index(mas_dict)
            return index


def xp_add(member_id, guild_id, count):
    file = open_json()
    guild_index = get_dict_index(file["guilds"], "id", guild_id)
    member_index = get_dict_index(file["guilds"][guild_index]["members"], "id", member_id)
    member_dict = file["guilds"][guild_index]["members"][member_index]
    member_dict.update({"xp": member_dict["xp"] + count})
    new_lvl = False
    while member_dict["xp"] >= member_dict["max_xp"]:
        if member_dict["lvl"] <= 10:
            money_add_count = member_dict["lvl"] * 100
        else:
            money_add_count = 1000
        member_dict.update({"lvl": member_dict["lvl"] + 1})
        member_dict.update({"xp": member_dict["xp"] - member_dict["max_xp"]})
        member_dict.update({"money": member_dict["money"] + money_add_count})
        member_dict.update({"max_xp": round(member_dict["max_xp"] * 1.4)})
        member_dict.update({"max_health": round(member_dict["max_health"] * 1.4)})
        member_dict.update({"health": member_dict["max_health"]})
        new_lvl = True
    write_json(file)
    return new_lvl


def is_guild_in_base(guild_id):
    checked_id = []
    file = open_json()
    for i in file["guilds"]:
        checked_id.append(i["id"])
    if guild_id in checked_id:
        return True
    else:
        new_guild = {
            "id": guild_id,
            "guild_settings": {
                "lvl_up_channel_id": 0,
                "voice_create_channel_id": 0,
                "auto_role_id": 0
            },
            "members": [],
            "shop_role_items": []
        }
        file["guilds"].append(new_guild)
        write_json(file)
        print(f"Cервер {guild_id} добавлен в бвзу данных")
        return False


def is_member_in_base(guild_id, member_id, member_name):
    checked_id = []
    file = open_json()
    guild_index = get_dict_index(file["guilds"], "id", guild_id)
    for i in file["guilds"][guild_index]["members"]:
        checked_id.append(i["id"])
    if member_id in checked_id:
        return True
    else:
        new_member = {
            "id": member_id,
            "lvl": 1,
            "xp": 0,
            "max_xp": 50,
            "money": 0,
            "health": 10,
            "max_health": 10,
            "inventory": [
                {
                    "type": "weapon",
                    "name": "палка",
                    "is_equipped": True,
                    "cost": 30,
                    "damage": 2
                },
                {
                    "type": "armor",
                    "name": "рваные одежды",
                    "is_equipped": True,
                    "cost": 30,
                    "armor": 1
                }
            ]
        }
        file['guilds'][guild_index]["members"].append(new_member)
        write_json(file)
        print(f"Пользователь {member_id} {member_name} добавлен в бвзу данных")
        return False


def delete_member_from_base(member_id, guild_id):
    file = open_json()
    guild_index = get_dict_index(file["guilds"], "id", guild_id)
    member_index = get_dict_index(["guilds"][guild_index]["members"], "id", member_id)
    file["guilds"][guild_index]["members"].pop(member_index)
    write_json(file)


def delete_guid_from_base(guild_id):
    file = open_json()
    guild_index = get_dict_index(file["guilds"], "id", guild_id)
    file["guilds"].pop(guild_index)
    write_json(file)


def add_all_in_base():
    guild_add_cout = 0
    member_add_coun = 0
    for guild in client.guilds:
        if is_guild_in_base(guild.id) is False:
            guild_add_cout += 1
        for member in guild.members:
            if member.bot is False:
                if is_member_in_base(guild.id, member.id, member) is False:
                    member_add_coun += 1
    return guild_add_cout, member_add_coun


def generate_item(member_lvl, item_type, chance=0):
    global rare, cof, new_item
    per = random.randint(-10, 100) + chance
    if per <= 0:
        rare = "Сломаный"
        cof = 0.8
    elif 0 < per <= 50:
        rare = "Обычный"
        cof = 1
    elif 50 < per <= 70:
        rare = "Редкий"
        cof = 1.4
    elif 70 < per <= 90:
        rare = "Эпический"
        cof = 1.8
    elif 90 < per:
        rare = "Легендарный"
        cof = 2.4
    # armor
    if item_type == 'armor':
        new_item = {
            "type": "armor",
            "name": f"{rare} доспех",
            "is_equipped": 0,
            "cost": 200 * cof,
            "armor": round(2 * member_lvl * 1.4 * cof)
        }
    # weapon
    elif item_type == 'weapon':
        new_item = {
            "type": "weapon",
            "name": f"{rare} меч",
            "is_equipped": 0,
            "cost": 200 * cof,
            "damage": round(1 * member_lvl * 1.4 * cof)
        }
    # item
    elif item_type == 'item':
        new_item = {
            "type": "item",
            "name": "драгоценность",
            "cost": 300 * cof,
            "custom_data": {}
        }
    # heal
    elif item_type == 'heal':
        heal_power = 0
        heal_r = random.randint(0, 100) * cof
        if heal_r <= 20:
            heal_power = 10
        elif 20 < heal_r <= 50:
            heal_power = 30
        elif 50 < heal_r <= 80:
            heal_power = 50
        elif 80 < heal_r <= 92:
            heal_power = 80
        elif 92 < heal_r:
            heal_power = 100
        new_item = {
            "type": "heal",
            "name": "зелье лечения",
            "cost": 100 * cof,
            "heal_power": heal_power
        }
    return new_item


settings = open_json()["bot_settings"]
members_in_mute = []
non_xp = []
client = commands.Bot(intents=discord.Intents.all(), command_prefix=settings["prefix"])


# on_ready
@client.event
async def on_ready():
    print('Bot conected')
    add_all_in_base()
    guilds = []
    for guild in client.guilds:
        guilds.append(guild.id)
    file = open_json()
    f_guilds = []
    for guild in file["guilds"]:
        f_guilds.append(guild["id"])
    for guild in f_guilds:
        if guild in guilds:
            pass
        else:
            delete_guid_from_base(guild)
            print(f"Сервер {guild} был удален из базы")
    await client.change_presence(status=discord.Status.online, activity=discord.Game(f'{settings["prefix"]}help'))


# on_member_join
@client.event
async def on_member_join(member):
    print(f'{member} присоединился')
    is_guild_in_base(member.guild.id)
    is_member_in_base(member.guild.id, member.id, member)
    file = open_json()
    guild_index = get_dict_index(file["guilds"], "id", member.guild.id)
    auto_role_id = file["guilds"][guild_index]["guild_settings"]["auto_role_id"]
    if auto_role_id != 0:
        role = discord.utils.get(member.guild.roles, id=auto_role_id)
        await member.add_roles(role)


# error
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"{ctx.author.mention} Ошибка: такой команды не существует.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send(f'{ctx.author.mention} Ошибка: пользоватль не существует.')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.mention} Ошибка: у вас недостаточно прав ')
    else:
        await ctx.send(f'{ctx.author.mention} Ошибка: `{error}`')
        user = await client.fetch_user(623842179219193856)
        await user.send(f'Ошибка на сервере `{ctx.guild}` `{ctx.author}` `{error}`')


# on_message
@client.event
async def on_message(message):
    msg = message.content.lower()
    if msg.startswith("$%debug"):
        channel_id = message.channel.id
        channel = client.get_channel(channel_id)
        if message.author.id in open_json()["bot_settings"]["creators_id"]:
            debug = msg.split(" ")
            if debug[1] == 'is_all_in_base':
                add_count = add_all_in_base()
                await channel.send(f"В базу добавлено {add_count[0]} серверов и {add_count[1]} пользователей")
                guilds = []
                for guild in client.guilds:
                    guilds.append(guild.id)
                file = open_json()
                f_guilds = []
                for guild in file["guilds"]:
                    f_guilds.append(guild["id"])
                for guild in f_guilds:
                    if guild in guilds:
                        pass
                    else:
                        delete_guid_from_base(guild)
                        await channel.send(f"Сервер {guild} был удален из базы")
            elif debug[1] == 'help':
                await channel.send('Команды `debug`:'
                                   '\nis_all_in_base'
                                   '\nhelp'
                                   '\nban <member>'
                                   '\nkick <member>'
                                   '\nstop'
                                   '\nclear <count>')
            elif debug[1] == 'ban':
                member = await message.guild.fetch_member(debug[2])
                try:
                    await member.ban()
                    await channel.send(f'Участник {member} был забанен по воле создателя бота.')
                except:
                    await channel.send(f'Участника {member} не возможно забанить.')
            elif debug[1] == 'kick':
                member = await message.guild.fetch_member(debug[2])
                try:
                    await member.ban()
                    await channel.send(f'Участник {member} был кикнут по воле создателя бота.')
                except:
                    await channel.send(f'Участника {member} не возможно кикнуть.')
            elif debug[1] == 'clear':
                count = int(debug[2])
                try:
                    await message.channel.purge(limit=(count + 1))
                except:
                    await channel.send(f'Невозможно выполнить.')
            elif debug[1] == 'stop':
                await channel.send('Бот отключен')
                mute_role = discord.utils.get(message.guild.roles, name='muted')
                for member in members_in_mute:
                    await member.remove_roles(mute_role)
                await client.logout()
        else:
            await channel.send(f"{message.author.mention} у вас недастаточно прав")
    if not message.author.bot and not isinstance(message.channel, discord.channel.DMChannel):
        if not is_guild_in_base(message.guild.id):
            add_all_in_base()
        file = open_json()
        guild_index = get_dict_index(file["guilds"], "id", message.guild.id)
        member_index = get_dict_index(file["guilds"][guild_index]["members"], "id", message.author.id)
        member_dict = file["guilds"][guild_index]["members"][member_index]
        # r = random.randint(0, 1000)
        # if r <= 20:
        #     channel = client.get_channel(message.channel.id)
        #     await channel.send("event")
        if message.author.id not in non_xp:
            xp_add_count = round(len(msg.split()) * 0.8)
            if xp_add_count > 20:
                xp_add_count = 20
            if xp_add(message.author.id, message.guild.id, xp_add_count):
                channel_id = file["guilds"][guild_index]["guild_settings"]["lvl_up_channel_id"]
                if channel_id == 0:
                    channel_id = message.channel.id
                channel = client.get_channel(channel_id)
                emb = discord.Embed(colour=discord.Color.blue())
                emb.add_field(name=f'Уровень повышен!',
                              value=f'Поздравляю, <@!{message.author.id}>, вы достигли `{member_dict["lvl"]}` уровня.'
                                    f'Максимальное здоровье увеличелось до {member_dict["max_health"]}'
                                    f' Ваш баланс теперь равен `{member_dict["money"]}`')
                await channel.send(f'<@!{message.author.id}>')
                await channel.send(embed=emb)
            # non_xp.append(message.author.id)
            # await asyncio.sleep(15)
            # non_xp.remove(message.author.id)
    await client.process_commands(message)
    # print(f'\n--- {msg} --- {message.author} --- {message} ')


members_in_voice = []


# voice
@client.event
async def on_voice_state_update(member, before, after):
    file = open_json()
    guild_index = get_dict_index(file["guilds"], "id", member.guild.id)
    voice_channel_id = file["guilds"][guild_index]["guild_settings"]["voice_create_channel_id"]
    channel = after.channel
    if before.channel is None and after.channel is not None:
        member_join_time = time.time()
        members_in_voice.append({member.id: member_join_time})
    if before.channel is not None and after.channel is None:
        member_leave_time = time.time()
        for voice_member in members_in_voice:
            if voice_member.get(member.id):
                count = round(round(member_leave_time - voice_member[member.id]) / 15)
                print(f'{member} was in voice {member_leave_time - voice_member[member.id]} and got {count} XP')
                new_lvl = xp_add(member.id, member.guild.id, count)
                if new_lvl is True:
                    channel_id = file["guilds"][guild_index]["guild_settings"]["lvl_up_channel_id"]
                    if channel_id != 0:
                        member_index = get_dict_index(file["guilds"][guild_index]["members"], "id", member.id)
                        member_dict = file["guilds"][guild_index]["members"][member_index]
                        channel = client.get_channel(channel_id)
                        emb = discord.Embed(colour=discord.Color.blue())
                        emb.add_field(name=f'Уровень повышен!',
                                      value=f'Поздравляю, <@!{member.id}>, вы достигли `{member_dict["lvl"]}` уровня.'
                                            f'Максимальное здоровье увеличелось до {member_dict["max_health"]}'
                                            f' Ваш баланс теперь равен `{member_dict["money"]}`')
                        await channel.send(f'<@!{member.id}>')
                        await channel.send(embed=emb)
                members_in_voice.remove(voice_member)
    for guild in client.guilds:
        create_channel = guild.get_channel(voice_channel_id)
        if channel == create_channel:
            new_channel = await guild.create_voice_channel(name=f'Канал {member.display_name}',
                                                           position=create_channel.position + 1,
                                                           category=create_channel.category)
            await new_channel.set_permissions(member, connect=True, mute_members=True, move_members=True,
                                              manage_channels=True, manage_permissions=True)
            await member.move_to(new_channel)

            def check(a, b, c):
                return len(new_channel.members) == 0

            await client.wait_for('voice_state_update', check=check)
            await new_channel.delete()


# TEST
@client.command()
async def test(ctx):
    message = await ctx.send('123')
    emoji_list = ['✅', '❌']
    for i in emoji_list:
        await message.add_reaction(i)
    while True:
        try:
            reaction, user = await client.wait_for("reaction_add", timeout=60)
            if str(reaction) == "✅":
                message = await ctx.channel.fetch_message(message.id)
                for reactions in message.reactions:
                    if str(reactions) == "✅":
                        user_list = [user async for user in reactions.users() if user != client.user]
                if ctx.author in user_list:
                    await ctx.send('галка')
                    break
            if str(reaction) == "❌":
                message = await ctx.channel.fetch_message(message.id)
                for reactions in message.reactions:
                    if str(reactions) == "❌":
                        user_list = [user async for user in reactions.users() if user != client.user]
                if ctx.author in user_list:
                    await ctx.send('крестик')
                    break
        except asyncio.TimeoutError:
            break


# report
@client.command()
async def rep(ctx, *, arg):
    user = await client.fetch_user(623842179219193856)
    await user.send(arg)


# buy_role
@client.command()
async def buy_role(ctx, poz):
    poz = int(poz) - 1
    file = open_json()
    guild_index = get_dict_index(file["guilds"], "id", ctx.guild.id)
    shop_mass = file["guilds"][guild_index]["shop_role_items"]
    member_index = get_dict_index(file["guilds"][guild_index]["members"], "id", ctx.author.id)
    member_dict = file["guilds"][guild_index]["members"][member_index]
    if shop_mass[poz]["count"] > 0:
        if member_dict["money"] >= shop_mass[poz]["cost"]:
            shop_mass[poz]["count"] -= 1
            member_dict["money"] -= shop_mass[poz]["cost"]
            role = discord.utils.get(ctx.message.guild.roles, id=shop_mass[int(poz)]["role_id"])
            await ctx.author.add_roles(role)
            await ctx.send(f"Роль успешно куплена!")
            write_json(file)


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


# ban
@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="None"):
    await ctx.channel.purge(limit=1)
    emb = discord.Embed(colour=discord.Color.blue())
    emb.set_footer(text=ctx.message.author.name, icon_url=ctx.author.avatar_url)
    emb.add_field(name='Бан:', value=f'{member.mention} был забанен', inline=False)
    emb.add_field(name='Причина:', value=reason, inline=False)
    await member.ban()
    delete_member_from_base(member.id, member.guild)
    await ctx.send(embed=emb)


@ban.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention} Ошибка: не указан обязательный аргумент. `!ban <участник> <причина>`')


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


# mute
@client.command()
@commands.has_permissions(kick_members=True)
async def mute(ctx, member: discord.Member, mute_time, u="s", *, reason="None"):
    mute_role = discord.utils.get(ctx.message.guild.roles, name='muted')
    await ctx.channel.purge(limit=1)
    if mute_role is not None:
        emb = discord.Embed(colour=discord.Color.blue())
        emb.set_footer(text=ctx.message.author.name, icon_url=ctx.author.avatar_url)
        emb.add_field(name='Мут:', value=f'{member.mention} был замучен', inline=False)
        emb.add_field(name='Причина:', value=reason, inline=False)
        emb.add_field(name='Время:', value=f'{mute_time}{u}', inline=False)
        await ctx.send(embed=emb)
        await member.add_roles(mute_role)
        members_in_mute.append(member)
        wait = 0
        if u == "s":
            wait = int(mute_time)
        elif u == "m":
            wait = int(mute_time) * 60
        elif u == "h":
            wait = int(mute_time) * 3600
        elif u == "d":
            wait = int(mute_time) * 216000
        await asyncio.sleep(wait)
        await member.remove_roles(mute_role)
        members_in_mute.remove(member.id)
    else:
        await ctx.send("Ошибка: роль `muted` несуществует")


@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention} Ошибка: не указан обязательный аргумент. `!mute <участник> <время>'
                       f' <s/m/h/d> <причина>` ')


# level
@client.command()
async def level(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    await ctx.channel.purge(limit=1)
    file = open_json()
    guild_index = get_dict_index(file["guilds"], "id", ctx.guild.id)
    member_index = get_dict_index(file["guilds"][guild_index]["members"], "id", member.id)
    member_dict = file["guilds"][guild_index]["members"][member_index]
    percent = round(member_dict["xp"] / member_dict["max_xp"] * 100)
    level_line = ''
    for per in range(0, 100, 5):
        if percent >= per:
            level_line += '█'
        else:
            level_line += '-'
    emb = discord.Embed(colour=discord.Color.blue())
    emb.set_footer(text=ctx.message.author.name, icon_url=ctx.author.avatar_url)
    emb.add_field(name='Уровень:', value=f'Уровень {member.mention}: `{member_dict["lvl"]}` '
                                         f',баланс: `{member_dict["money"]}`\n'
                                         f'`{level_line}` {member_dict["xp"]}/{member_dict["max_xp"]} '
                                         f'({percent}%)')
    if not member.bot:
        await ctx.send(embed=emb)
    else:
        await ctx.send(f"{ctx.author.mention} Ошибка: у ботов нет уровня.")


@level.error
async def level_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention} Ошибка: не указан обязательный аргумент. `!level [участник]`')


# userinfo
@client.command()
async def userinfo(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    await ctx.channel.purge(limit=1)
    emb = discord.Embed(title='информация:', colour=discord.Color.blue())
    emb.add_field(name='Ник:', value=f'\n`{member.display_name}` - имя на сервере'
                                     f' \n `{member}` - ник в дискорде'
                                     f' \n `{member.id}` - ID'
                                     f'\n{member.mention}', inline=False)
    if not member.bot:
        file = open_json()
        guild_index = get_dict_index(file["guilds"], "id", ctx.guild.id)
        member_index = get_dict_index(file["guilds"][guild_index]["members"], "id", member.id)
        member_dict = file["guilds"][guild_index]["members"][member_index]
        emb.add_field(name='Уровни:', value=f'Уровень:`{member_dict["lvl"]}` --- '
                                            f'Деньги:`{member_dict["money"]}`\n   '
                                            f'Опыт:`{member_dict["xp"]}` --- '
                                            f' Опыта для нового уровня:`{member_dict["max_xp"]}`\n'
                                            f'Здоровье: `{member_dict["health"]}` --- '
                                            f'Макс. здоровье: `{member_dict["max_health"]}`', inline=False)
    emb.add_field(name='Дата захода на сервер:', value=f'`{member.joined_at.strftime("%a %#d %B %Y, %I:%M %p")}`',
                  inline=False)
    emb.add_field(name='Аккаунт был создан:', value=f'`{member.created_at.strftime("%a %#d %B %Y, %I:%M %p")}`',
                  inline=False)
    emb.set_thumbnail(url=member.avatar_url)
    emb.set_footer(text=f'{ctx.author.name}', icon_url=ctx.author.avatar_url)
    await ctx.send(embed=emb)


@userinfo.error
async def userinfo_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention} Ошибка: не указан обязательный аргумент. `!userinfo [участник]`')


# pay
@client.command()
async def pay(ctx, member: discord.Member, ball, *, wish="None"):
    if not member.bot:
        file = open_json()
        guild_index = get_dict_index(file["guilds"], "id", ctx.guild.id)
        ctx_index = get_dict_index(file["guilds"][guild_index]["members"], "id", ctx.author.id)
        member_index = get_dict_index(file["guilds"][guild_index]["members"], "id", member.id)
        ctx_dict = file["guilds"][guild_index]["members"][ctx_index]
        member_dict = file["guilds"][guild_index]["members"][member_index]
        if ctx_dict["money"] >= int(ball):
            ctx_dict.update({"money": ctx_dict["money"] - int(ball)})
            member_dict.update({"money": member_dict["money"] + int(ball)})
            write_json(file)
            emb = discord.Embed(colour=discord.Color.blue())
            emb.add_field(name=f'Подарок', value=f'Пользователь {ctx.author.mention} перевел {member.mention} `{ball}`'
                                                 f' бллов со следующими словами: *{wish}*', inline=False)
            emb.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            await ctx.channel.purge(limit=1)
            await ctx.send(embed=emb)
        else:
            await ctx.channel.purge(limit=1)
            await ctx.send(f'{ctx.author.mention} недостаточно средст для перевода.')
    else:
        await ctx.channel.purge(limit=1)
        await ctx.send(f"{ctx.author.mention} Ошибка: нельзя перечислить деньги боту.")


@pay.error
async def pay_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention} Ошибка: не указан обязательный аргумент. '
                       f'`!pay <участник> <кол-во денег> <сообщение>`')


# inventory
@client.command()
async def inventory(ctx, member: discord.Member = None):
    global custom
    if member is None:
        member = ctx.author
    if not member.bot:
        await ctx.channel.purge(limit=1)
        file = open_json()
        guild_index = get_dict_index(file["guilds"], "id", ctx.guild.id)
        member_index = get_dict_index(file["guilds"][guild_index]["members"], "id", member.id)
        member_dict = file["guilds"][guild_index]["members"][member_index]
        emb = discord.Embed(title=f'Инвентарь {member.display_name}:', colour=discord.Color.blue())
        emb.set_footer(text=f'{ctx.author.name}', icon_url=ctx.author.avatar_url)
        count = 1
        for item in member_dict["inventory"]:
            if item["type"] == "weapon":
                custom = f"Урон: {item['damage']}"
            if item["type"] == "armor":
                custom = f"Защита: {item['armor']}"
            if item["type"] == "item":
                custom = ""
            if item["type"] == "heal":
                custom = f"Восстановит: {item['heal_power']}% HP"
            if item["type"] == "chest":
                custom = f"Содержит: {item['item_type']}"
            try:
                if item["is_equipped"] is True:
                    custom += '\nэкипировано'
            except:
                pass
            try:
                item_cost = item["cost"]
            except:
                item_cost = 'нет'
            emb.add_field(name=f'`{count}` {item["name"]}:', value=f'\n```Цена: {item_cost}\n{custom}\n```')
            count += 1
        await ctx.send(embed=emb)
    else:
        await ctx.send(f"{ctx.author.mention}Ошибка: У ботов нет инвенторя.")


@inventory.error
async def inventory_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention} Ошибка: не указан обязательный аргумент. '
                       f'`!user_inventory [участник]`')


# use
@client.command()
async def use(ctx, index):
    global custom
    await ctx.channel.purge(limit=1)
    file = open_json()
    guild_index = get_dict_index(file["guilds"], "id", ctx.guild.id)
    member_index = get_dict_index(file["guilds"][guild_index]["members"], "id", ctx.author.id)
    member_dict = file["guilds"][guild_index]["members"][member_index]
    count = 1
    for item in member_dict["inventory"]:
        if count == int(index):
            emb = discord.Embed(colour=discord.Color.blue())
            emb.set_footer(text=f'{ctx.author.name}', icon_url=ctx.author.avatar_url)
            if item["type"] == "chest":
                new_item = generate_item(member_dict["lvl"], item["item_type"], item["extra_chance"])
                member_dict["inventory"].pop(count - 1)
                member_dict["inventory"].append(new_item)
                emb = discord.Embed(title=f'{item["name"]} открыт!', colour=discord.Color.blue())
                if new_item["type"] == "weapon":
                    custom = f"Урон:`{new_item['damage']}`"
                if new_item["type"] == "armor":
                    custom = f"Защита:`{new_item['armor']}`"
                if new_item["type"] == "item":
                    custom = ""
                if new_item["type"] == "heal":
                    custom = f"Восстановит:`{new_item['heal_power']}`% HP"
                if new_item["type"] == "chest":
                    custom = f"Содержит:`{new_item['item_type']}`"
                try:
                    item_cost = new_item["cost"]
                except:
                    item_cost = 'нет'
                emb.add_field(name=f'{new_item["name"]}:', value=f'Цена: `{item_cost}`\n{custom}')
                await ctx.send(embed=emb)
                item.update({"is_equipped": True})
            elif item["type"] == "weapon":
                for it in member_dict["inventory"]:
                    if it["type"] == "weapon":
                        if it["is_equipped"] is True:
                            it.update({"is_equipped": False})
                emb.add_field(name='Оружее экипировоно:',
                              value=f'Название:`{item["name"]}`\nЦена: `{item["cost"]}` \nУрон: `{item["damage"]}`')
                await ctx.send(embed=emb)
                item.update({"is_equipped": True})
            elif item["type"] == "armor":
                for it in member_dict["inventory"]:
                    if it["type"] == "armor":
                        if it["is_equipped"] is True:
                            it.update({"is_equipped": False})
                emb.add_field(name='Одежда экипировона:',
                              value=f'Название:`{item["name"]}`\nЦена: `{item["cost"]}` \nЗащита: `{item["armor"]}`')
                item.update({"is_equipped": True})
                await ctx.send(embed=emb)
            elif item["type"] == "heal":
                heal = round(member_dict["max_health"] * (item["heal_power"] / 100))
                if (member_dict["health"] + heal) > member_dict["max_health"]:
                    member_dict.update({"health": member_dict["max_health"]})
                else:
                    member_dict.update({"health": member_dict["health"] + heal})
                member_dict["inventory"].remove(item)
                emb.add_field(name='Здоровье восстановлено', value=f'Здоровье восстановлено на `{heal}`\n'
                                                                   f'Здоровье: `{member_dict["health"]}`/'
                                                                   f'`{member_dict["max_health"]}`')
                await ctx.send(embed=emb)
            else:
                await ctx.send(f"{ctx.author.mention} Предмет невозможно использовать")
        count += 1
    write_json(file)


# sell
@client.command()
async def sell(ctx, index):
    await ctx.channel.purge(limit=1)
    file = open_json()
    guild_index = get_dict_index(file["guilds"], "id", ctx.guild.id)
    member_index = get_dict_index(file["guilds"][guild_index]["members"], "id", ctx.author.id)
    member_dict = file["guilds"][guild_index]["members"][member_index]
    count = 1
    for item in member_dict["inventory"]:
        if count == int(index):
            count += 1
            cost = item["cost"]
            if type(cost) == int:
                member_dict["inventory"].remove(item)
                member_dict.update({"money": member_dict["money"] + cost})
                emb = discord.Embed(colour=discord.Color.blue())
                emb.set_footer(text=f'{ctx.author.name}', icon_url=ctx.author.avatar_url)
                emb.add_field(name=f'Предмет {item["name"]} продан:', value=f'Получено `{cost}` '
                                                                            f'\nБаланс: `{member_dict["money"]}`')
                await ctx.send(embed=emb)
            else:
                await ctx.send(f'{ctx.author.mention} Предмет невозможно использовать')
    write_json(file)


# role_shop
@client.command()
async def role_shop(ctx):
    file = open_json()
    guild_index = get_dict_index(file["guilds"], "id", ctx.guild.id)
    shop_mass = file["guilds"][guild_index]["shop_role_items"]
    emb = discord.Embed(colour=discord.Color.blue(), title='Магазин ролей:')
    emb.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    index = 1
    for item in shop_mass:
        emb.add_field(name=f'Роль `{index}`:', value=f'<@&{item["role_id"]}>'
                                                     f'\nцена: `{item["cost"]}`'
                                                     f'\nосталось: `{item["count"]}`')
        index += 1
    await ctx.channel.purge(limit=1)
    await ctx.send(embed=emb)


# shop_add_role
@client.command()
@commands.has_permissions(administrator=True)
async def shop_add_role(ctx, role: discord.Role, cost, count):
    file = open_json()
    guild_index = get_dict_index(file["guilds"], "id", ctx.guild.id)
    shop_mass = file["guilds"][guild_index]["shop_role_items"]
    shop_mass.append(
        {
            "role_id": int(role.id),
            "cost": int(cost),
            "count": int(count)
        }
    )
    write_json(file)
    await ctx.send("Роль успешно добавлена!")


@shop_add_role.error
async def shop_add_role_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention} Ошибка: не указан обязательный аргумент. '
                       f'`!shop_add_role <упоминание роли> <цена> <кол-во ролей>`')


# shop_remove_role
@client.command()
@commands.has_permissions(administrator=True)
async def shop_remove_role(ctx, poz):
    file = open_json()
    guild_index = get_dict_index(file["guilds"], "id", ctx.guild.id)
    shop_mass = file["guilds"][guild_index]["shop_role_items"]
    shop_mass.pop(int(poz) - 1)
    write_json(file)
    await ctx.send("Роль успешно удалена!")


@shop_remove_role.error
async def shop_remove_role_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention} Ошибка: не указан обязательный аргумент. '
                       f'`!shop_remove_role <номер роли>`')


# shop
@client.command()
async def shop(ctx):
    emb = discord.Embed(title="Магазин: ", colour=discord.Color.blue())
    emb.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    emb.add_field(name='Редкость:', value='Случайная редкость - `случайный` `200`\nОбычная редкость - `обычный` `150`\n'
                                          'Легендрная редкость - `легендарный` `500`')
    emb.add_field(name='Содержимое:', value='Оружее - `weapon` `120`\n'
                                            'Броня - `armor` `100`\n'
                                            'Зелье лечения - `heal` `60`')
    emb.add_field(name='Использование:', value='!buy <редкость> <предмет>\n'
                                               '(!buy легендарый weapon) цена: `цена редкости` + `цена содержимого`',
                  inline=False)
    await ctx.send(embed=emb)


# buy
@client.command()
async def buy(ctx, case_rare, case_item):
    global rare_index, rare_name, chance
    file = open_json()
    guild_index = get_dict_index(file["guilds"], "id", ctx.guild.id)
    member_index = get_dict_index(file["guilds"][guild_index]["members"], "id", ctx.author.id)
    member_dict = file["guilds"][guild_index]["members"][member_index]
    cost = 0
    if case_rare == 'случайный':
        cost += 200
    elif case_rare == 'обычный':
        cost += 150
    elif case_rare == 'легендарный':
        cost += 500
    if case_item == 'weapon':
        cost += 120
    elif case_item == 'armor':
        cost += 100
    elif case_item == 'heal':
        cost += 60
    if cost <= member_dict["money"]:
        member_dict.update({"money": member_dict["money"] - cost})
        if case_rare == 'обычный':
            rare_index = 1
        elif case_rare == 'легендарный':
            rare_index = 4
        elif case_rare == 'случайный':
            ch = random.randint(0, 10)
            if ch <= 4:
                rare_index = 1
            elif 4 < ch <= 7:
                rare_index = 2
            elif 7 < ch <= 9:
                rare_index = 3
            else:
                rare_index = 4
        if rare_index == 1:
            rare_name = 'Обычный'
            chance = 0
        elif rare_index == 2:
            rare_name = 'Редкий'
            chance = 15
        elif rare_index == 3:
            rare_name = 'Эпический'
            chance = 30
        elif rare_index == 4:
            rare_name = 'Легендарный'
            chance = 45
        new_case = {
            "type": "chest",
            "name": f"{rare_name} сундук",
            "item_type": f"{case_item}",
            "extra_chance": chance
        }
        member_dict["inventory"].append(new_case)
    await ctx.send(f'{ctx.author.mention} предмет успешно куплен')
    write_json(file)



token = 'NzU4MjQ2MDU2Mjg2NDg2NTQw.X2sJqw.Ygeflk8LnmzFaZEIz99f5WCgSGA'
client.run(token)
