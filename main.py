from os import name
import discord
from discord import player
from discord import member
from discord import embeds
from discord.embeds import Embed
from discord.ext import tasks, commands
import json
import math
from time import sleep

"""Help messages"""
help_dict = {
    'level': discord.Embed(title="Command : level",
                           description="Give your level and experience if no user is specified. \n \
                To know someone else type : `$level @User#0001`",
                           color=0xff0000),

    'coins': discord.Embed(title="Command : coins",
                           description="Gives your amount of coins if no user is specified. \n \
               To know someone else type : `$coins @User#0001`",
                           color=0xff0000),

    'give-coins': discord.Embed(title="Command : give-coins",
                                description="This command is used to give (or remove) coins from the mentionned player. \n \
               Usage is `$give-coins @User#0001 amount` the amount can be negative to remove coins",
                                color=0xff0000),

    'richest': discord.Embed(title="Command : richest",
                             description="Sends the top 10 richest players on the server and the total amount of coins. \n \
               Usage : `$richest`, no parameter is required (or expected)",
                             color=0xff0000),

    'buy': discord.Embed(title="Command : buy",
                         description="You can buy items from the shop with this function. \n \
               It accepts the item ID or its name : `$buy 001` or `$buy Beautiful Role`",
                         color=0xff0000),

    'shop': discord.Embed(title="Command : shop",
                          description="To see the entire shop simple type `$shop`. \n \
               If you want to see only a specific item you can use `$shop item_id` or `$shop item_name`",
                          color=0xff0000),

    'inventory': discord.Embed(title="Command : inventory",
                               description="Lists all the items you own : `$inventory`. \n",
                               color=0xff0000),

    'use': discord.Embed(title="Command : shop",
                         description="Uses the item specified : `$use item_id` or `$use item_name`. \n \
               It will notify staff, they will quickly get in touch with you",
                         color=0xff0000),

    'add-item': discord.Embed(title="Command : shop",
                              description="Restricted to staff. \
               The expected arguments (in order and separated by '$') are : item_id, item_name, price, item_description, item_image. \n \
               Example : `$add-item 0001 $Role#1 $1000 $This role is important $https://imgur.com/y3ls2gX`",
                              color=0xff0000),

    'modify-item': discord.Embed(title="Command : shop",
                                 description="Restricted to staff. \
               Works similar to add-item except that the item with the id item_id will be changed with the new info provided. \n \
               Example : `$modify-item 0001 $RoleChange#1 $2000 $This role is even more important $https://imgur.com/y3ls2gX`",
                                 color=0xff0000),

    'remove-item': discord.Embed(title="Command : shop",
                                 description="Restricted to staff. \
               The item corresponding to the given item id will be deleted. \n \
               Example : `$remove-item 0001`",
                                 color=0xff0000),

    'help': discord.Embed(title='**All available commands**',
                          description='Some displayed are restricted to staff (and will not allow you to execute them)',
                          color=0xff0000),

}
fields_values = ['coins', '`$help coins`', True], ['give-coins', '`$help give-coins`', True], ['richest', '`$help richest`', True],\
                ['buy', '`$help buy`', True], ['shop', '`$help shop`', True], ['inventory', '`$help inventory`', True],\
                ['use', '`$help use`', True], ['level', '`$help level`', True], ['help', '`$help help`', True], \
                ['add-item (staff-only)', '`$help add-item`', True], ['modify-item (staff-only)', '`$help modify-item`', True], \
                ['remove-item (staff-only)', '`$help remove-item`', True]
for val in fields_values:
    help_dict['help'].add_field(name=val[0], value=val[1], inline=val[2])

allow_userIDs = [425337707825201152, 892805391870726164, 508950406076825621, 367344593911545856,
                 198373115892465664, 257501547246780416, 511165011637436416, 533584123600830466]


client = commands.Bot(command_prefix='$', help_command=None)


"""Functions"""


def update_money(change_dict: dict):
    """
    change_dict = {userID : amount,}
    with amount being positive or negative
    """
    pass

    with open('data.json', 'r') as f:
        current_info = json.load(f)

    for userID, amount in change_dict.items():
        userID = str(userID)
        if userID not in current_info:
            current_info[userID] = amount
        else:
            if current_info[userID] + amount < 30000:
                current_info[userID] += amount
            else:
                current_info[userID] = 30000

    with open('data.json', 'w') as f:
        json.dump(current_info, f, indent=4)


def get_amounts():
    """
    :return: dict with {userID : amount,}
    """
    with open('data.json', 'r') as f:
        current_info = json.load(f)

    return current_info


"""Auto-Giving Coins (activity)"""
info = {"messages": {},
        "vocal": {},
        "user_vocal": []}


#   Message Counter #
@client.event
async def on_message(msg):
    await client.process_commands(msg)
    authorID = msg.author.id

    member = await FNTK_guild.fetch_member(int(authorID))

    multiplier = 1
    for role in member.roles:
        if role.id == 923161171744411668:
            multiplier = 1.5
            break
    if authorID not in info['messages']:
        info['messages'][authorID] = 1*multiplier
    else:
        info['messages'][authorID] += 1*multiplier

#   Vocal Counter   #


@client.event
async def on_voice_state_update(user, before, after):
    userID = user.id

    if after.channel == None or after.channel.id == 893189817322602537:
        info['user_vocal'].remove(userID)
    else:
        # in vc and not afk vc
        if userID not in info['user_vocal'] and after.channel.id != 893189817322602537:
            info['user_vocal'].append(userID)
        else:  # he muted/unmuted deafened/undeafened himself/herself
            pass


@tasks.loop(seconds=10)
async def update():

    #   Update vocal amount #
    for userID in info['user_vocal']:
        member = await FNTK_guild.fetch_member(int(userID))

        multiplier = 1
        for role in member.roles:
            if role.id == 923161171744411668:
                multiplier = 1.5
                break
        if userID not in info['vocal']:
            info['vocal'][userID] = 10*multiplier
        else:
            info['vocal'][userID] += 10*multiplier

    give_dict = {}

    #   10 messages = 1 coin    #
    for userID, amount in info['messages'].items():
        #   Calculating coins   #
        if amount >= 10:  # user getting at least 1 coin
            fntk_coins = amount // 10
            info['messages'][userID] = amount % 10
        else:
            fntk_coins = 0

        if userID not in give_dict:
            give_dict[userID] = fntk_coins
        else:
            give_dict[userID] += fntk_coins

    #   1 hour of vc = 20 coins #
    for userID, time in info['vocal'].items():
        #   Calculating coins   #
        if time >= 3600:  # user getting at least 20 coins
            fntk_coins = (time // 3600)*20
            info['vocal'][userID] = time % 3600
        else:
            fntk_coins = 0

        if userID not in give_dict:
            give_dict[userID] = fntk_coins
        else:
            give_dict[userID] += fntk_coins
    # updating the levels
    with open('level.json', 'r') as f:
        lvl = json.load(f)

    for user, xp in give_dict.items():
        user = str(user)
        if user not in lvl:
            lvl[user] = {'xp': xp, 'lvl': 0}

        else:
            lvl[user]['xp'] += xp
            if lvl[user]['lvl'] < 10:
                if lvl[user]['xp'] >= (lvl[user]['lvl']+1)*1000:
                    lvl[user]['xp'] -= (lvl[user]['lvl']+1)*1000
                    lvl[user]['lvl'] += 1
            elif lvl[user]['lvl'] < 16:
                if lvl[user]['xp'] >= 10000:
                    lvl[user]['xp'] -= 10000
                    lvl[user]['lvl'] += 1
            elif lvl[user]['lvl'] < 21:
                if lvl[user]['xp'] >= 20000:
                    lvl[user]['xp'] -= 20000
                    lvl[user]['lvl'] += 1
            name = f"Level {lvl[user]['lvl']}"
            if lvl[user]['lvl'] != 0:
                roles = FNTK_guild.roles
                role = discord.utils.get(roles, name=name)
                member = await FNTK_guild.fetch_member(int(user))
                await member.add_roles(role)

    with open('level.json', 'w') as f:
        json.dump(lvl, f, indent=4)

    update_money(give_dict)


"""User Commands"""


@client.event
async def on_ready():
    global FNTK_guild
    print('Ready !')
    FNTK_guild = await client.fetch_guild(692749537219051531)
    update.start()


@client.command(name='coins')
async def coins(ctx, *user):

    current_info = get_amounts()
    return_embed = discord.Embed(description='Empty', color=6345206)

    if not user:  # wants his/her amount of coins
        authorID = ctx.message.author.id
        for userID, amount in current_info.items():
            if int(userID) == authorID:
                return_embed.description = f"**You** have {amount} coins !"

        if return_embed.description == 'Empty':
            return_embed.description = f"**You** don't have **any** coins"
        await ctx.channel.send(embed=return_embed)
    else:  # wants someone else's amount of coins
        memberID = user[0]
        for char in '<@!>':
            memberID = memberID.replace(char, '')
        member = await client.fetch_user(memberID)

        for userID, amount in current_info.items():
            if int(memberID) == int(userID):

                return_embed.description = f"**{member.name}** has {amount} coins !"

        if return_embed.description == 'Empty':
            return_embed.description = f"**{member.name}** doesn't  have **any** coins !"
        await ctx.channel.send(embed=return_embed)


@client.command(name='give-coins')
async def give_coins(ctx, user_id, amount):
    userID = ctx.message.author.id
    if userID not in allow_userIDs:
        await ctx.channel.send(embed=discord.Embed(description='You are not part of the whitelist :x:', color=6345206))
    else:

        for char in '<@!>':
            user_id = user_id.replace(char, '')

        update_money({user_id: int(amount)})
        pseudo = await client.fetch_user(user_id)
        amount = int(amount)
        if 1 < amount:
            description = f":white_check_mark: {amount} <:fanatikCoins:894584412166058014> have been given to {pseudo.mention}"
        if 1 == amount:
            description = f":white_check_mark: {amount} <:fanatikCoins:894584412166058014> has been given to {pseudo.mention}"
        elif 0 == amount:
            description = "I cannot give 0 coins."
        elif 1 == amount:
            description = f":white_check_mark: {amount-(2*amount)} <:fanatikCoins:894584412166058014> has been removed from {pseudo.mention}"
        elif 1 > amount:
            description = f":white_check_mark: {amount-(2*amount)} <:fanatikCoins:894584412166058014> have been removed from {pseudo.mention}"
        color = 6345206
        embed = discord.Embed(description=description, color=color)
        await ctx.channel.send(embed=embed)


@client.command(name='richest')
async def richest(ctx):
    dico = get_amounts()
    valeur = []
    user_list = []
    am_total = 0
    for userID, amount in dico.items():
        valeur.append(amount)
        user_list.append(userID)
        am_total += amount

    embed = discord.Embed(
        title="Richest", description="List of the richest people on the server", color=6345206)
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/icons/692749537219051531/0c98647b4dd76cdecc2c670556c75f7e.png?size=4096")
    embed.add_field(name=f':bank: - Server Total',
                    value=f"{am_total} coins", inline=False)
    am_total = 0
    for i in range(10):
        rech_am = max(valeur)
        j = valeur.index(rech_am)
        if rech_am == 0:
            rech_us = None
        else:
            rech_us = await client.fetch_user(user_list[j])
            rech_us = rech_us.name
        valeur[j] = 0
        if i == 0:
            embed.add_field(
                name=f':first_place: - {rech_us}', value=f"<:fanatikCoins:894584412166058014> {rech_am} coins", inline=False)
        elif i == 1:
            embed.add_field(
                name=f':second_place: - {rech_us}', value=f"<:fanatikCoins:894584412166058014> {rech_am} coins", inline=False)
        elif i == 2:
            embed.add_field(
                name=f':third_place: - {rech_us}', value=f"<:fanatikCoins:894584412166058014> {rech_am} coins", inline=False)
        else:
            embed.add_field(
                name=f'{i+1} - {rech_us}', value=f"<:fanatikCoins:894584412166058014> {rech_am} coins", inline=False)
    await ctx.channel.send(embed=embed)


@client.command(name='buy')
async def buy(ctx, *item_id):
    with open('inventory.json', 'r') as f:
        inv = json.load(f)

    with open('shop.json', 'r') as f:
        shop = json.load(f)

    item_id = ' '.join(item_id).lower()

    authorID = ctx.message.author.id
    current_info = get_amounts()
    for userID, amount in current_info.items():
        if int(userID) == authorID:
            try:
                shop[item_id]
            except:
                for i in shop.keys():
                    if item_id == shop[i][0]:
                        item_id = i
            if amount >= shop[item_id][2]:
                if userID not in inv:
                    inv[userID] = {item_id: 1}
                else:
                    if str(item_id) in inv[userID]:
                        inv[userID][str(item_id)] += 1
                    else:
                        inv[userID][str(item_id)] = 1
                update_money({userID: -shop[item_id][2]})
                pseudo = await client.fetch_user(authorID)
                description = f'**{pseudo.name}** bought **{shop[item_id][0]}**'
            else:
                description = f"You don't have enough coins"
    embed = discord.Embed(description=description, color=6345206)
    await ctx.channel.send(embed=embed)

    with open('inventory.json', 'w') as f:
        json.dump(inv, f, indent=4)


@client.command(name='shop')
async def shop(ctx, *id):
    with open('shop.json', 'r') as f:
        shop = json.load(f)

    title = '**Boutique de TEAM FANATIK**'
    description = "Use `$shop <item name>` or `$shop <item id>` to get more details about an item.\nUse `$buy <item name>` or `$buy <item id>`to buy an item\n\n:money_with_wings: **Here are our items:**"
    color = 6345206

    new_embed = discord.Embed(
        title=title, description=description, color=color)

    msg = ""
    if id == ():
        for i in shop.items():
            new_embed.add_field(name=f"{str(i[1][0])} - <:fanatikCoins:894584412166058014> {str(i[1][2])}:",
                                value=f"{str(i[1][1])} \n`id : {str(i[0])}`", inline=False)
            msg += "ok"
    else:
        id = ' '.join(id).lower()
        id = str(id)
        description2 = "Use `$shop <item name>` or `$shop <item id>` to get more details about an item.\nUse `$buy <item name>` or `$buy <item id>`to buy an item\n\n:money_with_wings: **Here is the item you requested:**"
        new_embed = discord.Embed(
            title=title, description=description2, color=color)
        for i in shop.items():
            if i[1][0] == id or i[0] == id:
                new_embed.add_field(name=f"{str(i[1][0])} - <:fanatikCoins:894584412166058014> {str(i[1][2])}:",
                                    value=f"{str(i[1][1])} \nid : `{str(i[0])}`", inline=False)
                new_embed.set_image(url=str(i[1][3]))
                msg += "ok"
        if msg == "":
            msg = "bug"
            new_embed = discord.Embed(
                title="Error !", description="The item you asked for does not exist.", color=color)
    await ctx.channel.send(embed=new_embed)


@client.command(name='inventory')
async def inventory(ctx):
    with open('inventory.json', 'r') as f:
        inv = json.load(f)

    with open('shop.json', 'r') as f:
        shop = json.load(f)

    authorID = str(ctx.message.author.id)
    try:
        playerInv = inv[authorID]
    except KeyError:  # user has no inventory
        playerInv = {}

    member = await client.fetch_user(authorID)

    title = f"{member.name}'s inventory"
    description = "Use `$shop <item name>` or `$shop <item id>` to get more details about an item.\nUse `$buy <item name>` or `$buy <item id>`to buy an item\nUse `$use <item name>` or `$use <item id>` to use an item\n\n**You have :**"
    color = 6345206

    new_embed = discord.Embed(
        title=title, description=description, color=color)

    for i in playerInv.items():
        for y in shop.keys():
            if str(shop[i[0]][0]) == shop[y][0]:
                item_id = y
        new_embed.add_field(name=f"{str(i[1])} {str(shop[i[0]][0])}:",
                            value=f"{str(shop[item_id][1])}\nid : `{item_id}`", inline=False)
    await ctx.channel.send(embed=new_embed)


@client.command(name='help')
async def help(ctx, *cmd):
    if not cmd:
        await ctx.channel.send(embed=help_dict['help'])
    else:
        if cmd[0] in help_dict:

            await ctx.channel.send(embed=help_dict[cmd[0]])
        else:
            await ctx.channel.send(embed=discord.Embed(title='**Comand not found**', description=f'{cmd[0]} is not a valid command, type `$help` for a complete list'))


@client.command(name='use')
async def use(ctx, *item_id):
    with open('inventory.json', 'r') as f:
        inv = json.load(f)

    with open('shop.json', 'r') as f:
        shop = json.load(f)

    item_id = ' '.join(item_id).lower()
    item_id = str(item_id)
    authorID = str(ctx.message.author.id)
    color = 6345206
    if authorID in inv:
        try:
            shop[item_id]
        except:
            for i in shop.keys():
                if item_id == shop[i][0]:
                    item_id = i
        if item_id in inv[authorID]:
            inv[authorID][item_id] -= 1
            if shop[item_id][0] == "banana":
                title = "Stop everything"
                embed = discord.Embed(title=title, color=color)
                await ctx.channel.send(embed=embed)
                sleep(0.5)
                title = "Kris get the banana!"
                embed = discord.Embed(title=title, color=color)
                await ctx.channel.send(embed=embed)
                sleep(0.5)
                title = "The banana !"
                embed = discord.Embed(title=title, color=color)
                await ctx.channel.send(embed=embed)
                sleep(0.5)
                title = "**POTASSIUM**"
                description = "Kris got the banana"
                await ctx.channel.send("https://images-ext-1.discordapp.net/external/7XU8lcCaOUnWQYywFUHc4mLDqDAIYTC5Bu6MVQNVIF4/https/i.kym-cdn.com/photos/images/newsfeed/002/206/266/b53.gif")
            else:
                if inv[authorID][item_id] == 0:
                    del inv[authorID][item_id]
                member = await client.fetch_user(authorID)
                title = "Use"
                description = f"**{member.name}** used **{shop[item_id][0]}**"
                await ctx.channel.send(f"<@892805391870726164>")
        else:
            title = "Error !"
            description = "You don't own this item"
    else:
        title = "Error !"
        description = "You don't own this item"

    new_embed = discord.Embed(
        title=title, description=description, color=color)
    await ctx.channel.send(embed=new_embed)

    with open('inventory.json', 'w') as f:
        json.dump(inv, f, indent=4)


@client.command(name='add-item')
async def add_item(ctx, *msg):
    userID = ctx.message.author.id
    if userID not in allow_userIDs:
        await ctx.channel.send(embed=discord.Embed(description='You are not part of the whitelist :x:', color=6345206))
    else:
        msg = ' '.join(msg)
        msg = msg.split(" $")
        item_id, item_name, price, item_description, item_image = msg[0], msg[1].lower(
        ), msg[2], msg[3], str(msg[4])
        try:
            int(price)
        except ValueError:
            await ctx.channel.send(f"{price} isn't a valid price")
            return(None)  # To prevent the function from creating an invalid item

        try:
            int(item_id)
        except ValueError:
            await ctx.channel.send(f"{item_id}isn't a valid id")
            return(None)  # To prevent the function from creating an invalid item

        with open('shop.json', 'r') as f:
            shop = json.load(f)

        if type(item_description) == list or type(item_description) == tuple:
            item_description = ' '.join(item_description)

        shop[item_id] = [item_name, item_description, int(price), item_image]

        with open('shop.json', 'w') as f:
            json.dump(shop, f, indent=4)

        title = "Added to shop :"
        color = 6345206
        name = f"{item_name} - <:fanatikCoins:894584412166058014> {price}:"
        value = f"{item_description} \n`id:{item_id}`"
        embed = discord.Embed(title=title, color=color)
        embed.add_field(name=name, value=value)
        embed.set_image(url=item_image)
        await ctx.channel.send(embed=embed)


@client.command(name='modify-item')
async def modify_item(ctx, *msg):
    userID = ctx.message.author.id
    if userID not in allow_userIDs:
        await ctx.channel.send(embed=discord.Embed(description='You are not part of the whitelist :x:', color=6345206))
    else:
        msg = ' '.join(msg)
        msg = msg.split(" $")
        item_id, item_name, price, item_description, item_image = msg[0], msg[1].lower(
        ), msg[2], msg[3], str(msg[4])
        try:
            int(price)
        except ValueError:
            await ctx.channel.send(f"{price} isn't a valid price")
            return(None)  # To prevent the function from creating an invalid item

        try:
            int(item_id)
        except ValueError:
            await ctx.channel.send(f"{item_id}isn't a valid id")
            return(None)  # To prevent the function from creating an invalid item

        with open('shop.json', 'r') as f:
            shop = json.load(f)

        if type(item_description) == list or type(item_description) == tuple:
            item_description = ' '.join(item_description)

        shop[item_id] = [item_name, item_description, int(price), item_image]

        with open('shop.json', 'w') as f:
            json.dump(shop, f, indent=4)

        title = "Modified from shop :"
        color = 6345206
        name = f"{item_name} - <:fanatikCoins:894584412166058014> {price}:"
        value = f"{item_description} \n`id:{item_id}`"
        embed = discord.Embed(title=title, color=color)
        embed.add_field(name=name, value=value)
        embed.set_image(url=item_image)
        await ctx.channel.send(embed=embed)


@client.command(name='remove-item')
async def remove_item(ctx, item_id):
    userID = ctx.message.author.id
    if userID not in allow_userIDs:
        await ctx.channel.send(embed=discord.Embed(description='You are not part of the whitelist :x:', color=6345206))
    else:
        with open('shop.json', 'r') as f:
            shop = json.load(f)

        name = shop[item_id][0]

        del shop[item_id]

        with open('shop.json', 'w') as f:
            json.dump(shop, f, indent=4)

        title = "Removed from shop :"
        color = 6345206
        description = f"{name} was successfully removed from shop"
        embed = discord.Embed(
            title=title, description=description, color=color)
        await ctx.channel.send(embed=embed)


@client.command(name='level')
async def level(ctx, *user):
    with open('level.json', 'r') as f:
        current_info = json.load(f)

    if not user:  # wants his/her level
        authorID = ctx.message.author.id

    else:  # wants someone else's level
        authorID = user[0]
        for char in '<@!>':
            authorID = authorID.replace(char, '')
    member = await client.fetch_user(authorID)

    title = f"{member.name}'s level"
    description = "You can earn levels by sending messages or spending time in a voice channel. \nBe careful, You won't earn any xp in afk channel."
    color = 6345206
    return_embed = discord.Embed(
        title=title, description=description, color=color)

    for userID, infos in current_info.items():

        if int(userID) == int(authorID):
            name = f"Level {infos['lvl']}"
            if infos['lvl'] < 10:
                needed = (infos['lvl']+1)*1000
            elif infos['lvl'] < 16:
                needed = 10000
            elif infos['lvl'] < 21:
                needed = 20000
            value = f"xp : {infos['xp']}/{needed}\n {infos['xp']*100/needed}% to the next level"
            return_embed.add_field(name=name, value=value)

    await ctx.channel.send(embed=return_embed)

client.run('ODYxNTI5MjM5Njc3NTY2OTg2.YOLHoQ.s-UFtmIyvXQfpyd5l93o8YprY_w')
