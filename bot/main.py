import datetime
import interactions
import requests
from interactions import slash_command, SlashContext, OptionType, slash_option, SlashCommandChoice, Button, ButtonStyle
import discord
import random
from datetime import datetime
from io import BytesIO

bot = interactions.Client(token="MTE2NzEwNDM0ODUwNjAzNDI1OQ.GCAmhu.f9QC7cgesi4kjw6s-Zw8PAs35Kk0xm9Aq4L_FA")

'''
All events are defined below.
'''



'''
All slah commands are defined below.
'''

@slash_command(name="help", description="Get a list of all available commands")
async def help_command(ctx: SlashContext):
    await ctx.defer()
    commands = [
        {
            "name": "help",
            "description": "Get a list of all available commands"
        },
        {
            "name": "info",
            "description": "Get information about the bot"
        },
        {
            "name": "server_info",
            "description": "Get information about a Steam game server"
        },
        {
            "name": "steam_user_info",
            "description": "Get information about a Steam user"
        }
    ]
    message = "Here are the available commands:\n"
    for command in commands:
        message += f"**/{command['name']}**: {command['description']}\n"
    embed = discord.Embed(title="Help", description=message)
    await ctx.send(embed=embed.to_dict())

@slash_command(name="info", description="Get information about the bot")
async def bot_info_function(ctx: SlashContext):
    await ctx.defer()
    bot_name = bot.user.display_name
    bot_id = bot.user.id
    bot_avatar = bot.user.avatar_url
    message = f"**Bot Name:** {bot_name}\n**Bot ID:** {bot_id}"
    embed = discord.Embed(title="Bot Info", description=message)
    embed.set_thumbnail(url=bot_avatar)
    embed.set_footer(text="Made by algorythm")
    await ctx.send(embed=embed.to_dict())

@slash_command(name="server_info", description="Get information about a Steam game server")
@slash_option(
    name="ip_address",
    description="Enter the IP and the port of the server in the format IP:Port",
    required=True,
    opt_type=OptionType.STRING
)
async def server_info_function(ctx: SlashContext, ip_address: str):
    await ctx.defer()
    url = f"http://api.steampowered.com/ISteamApps/GetServersAtAddress/v0001?addr={ip_address}&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "response" in data and "servers" in data["response"]:
            servers = data["response"]["servers"]
            if len(servers) > 0:
                server_info = servers[0]
                appid = server_info['appid']
                game_url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
                game_response = requests.get(game_url)
                if game_response.status_code == 200:
                    game_data = game_response.json()
                    if str(appid) in game_data and "data" in game_data[str(appid)]:
                        game_name = game_data[str(appid)]["data"]["name"]
                        game_image = game_data[str(appid)]["data"]["header_image"]
                        game_link = f"https://store.steampowered.com/app/{appid}"
                        message = f"**Server address:** {server_info['addr']}\n**Game:** {game_name}\n**VAC secure:** {server_info['secure']}"
                        embed = discord.Embed(title=game_name, url=game_link, description=message)
                        embed.set_thumbnail(url=game_image)
                        await ctx.send(embed=embed.to_dict())
                        return
    await ctx.send("Failed to get server information")

@slash_command(name="steam_user_info", description="Get information about a Steam user")
@slash_option(
    name="steam_id",
    description="Enter the Steam ID of the user",
    required=True,
    opt_type=OptionType.STRING
)
async def steam_user_info_function(ctx: SlashContext, steam_id: str):
    await ctx.defer()
    steam_api_url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=CD1A6B0F05C833598D51231A8AA9A87D&steamids={steam_id}"
    response = requests.get(steam_api_url)
    if response.status_code == 200:
        data = response.json()
        if "response" in data and "players" in data["response"]:
            player_data = data["response"]["players"][0]
            player_name = player_data["personaname"]
            player_link = f"https://steamcommunity.com/profiles/{steam_id}"
            player_avatar = player_data["avatarmedium"]
            last_logoff = datetime.datetime.fromtimestamp(player_data["lastlogoff"]).strftime('%Y-%m-%d %H:%M:%S')
            loc_country_code = player_data["loccountrycode"]
            primary_group_id = player_data["primaryclanid"]
            primary_group_link = f"https://steamcommunity.com/gid/{primary_group_id}"
            message = f"**Steam ID:** {steam_id}\n**Steam Account Name:** {player_name}\n**Steam Account Link:** {player_link}\n**Last Logoff:** {last_logoff}\n**Primary Group ID:** [{primary_group_id}]({primary_group_link})\n**Location Country Code:** {loc_country_code}"
            embed = discord.Embed(title="Steam User Info", description=message)
            embed.set_thumbnail(url=player_avatar)
            
            # Get recently played games
            steam_api_url = f"https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key=CD1A6B0F05C833598D51231A8AA9A87D&steamid={steam_id}&format=json"
            response = requests.get(steam_api_url)
            if response.status_code == 200:
                data = response.json()
                if "response" in data and "games" in data["response"]:
                    games_data = data["response"]["games"]
                    games_message = ""
                    for game_data in games_data[:3]:
                        game_name = game_data["name"]
                        game_app_id = game_data["appid"]
                        game_playtime = round(game_data["playtime_windows_forever"] / 60, 2) + round(game_data["playtime_mac_forever"] / 60, 2) + round(game_data["playtime_linux_forever"] / 60, 2)
                        game_link = f"https://store.steampowered.com/app/{game_app_id}"
                        games_message += f"\n[{game_name}]({game_link}) - {game_playtime} hours"
                    embed.add_field(name="Recently Played Games", value=games_message, inline=False)
            
            await ctx.send(embed=embed.to_dict())
            return

@slash_command(name="steam_game_info", description="Get information about a specific Steam game")
@slash_option(
    name="game_name",
    description="Enter the name of the game",
    required=True,
    opt_type=OptionType.STRING
)
async def steam_game_info_function(ctx: SlashContext, game_name: str):
    await ctx.defer()
    steam_api_url = f"https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    response = requests.get(steam_api_url)
    if response.status_code == 200:
        data = response.json()
        if "applist" in data and "apps" in data["applist"]:
            app_list = data["applist"]["apps"]
            app_id = None
            for app in app_list:
                if app["name"].lower() == game_name.lower():
                    app_id = app["appid"]
                    break
            if app_id is not None:
                steam_api_url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
                response = requests.get(steam_api_url)
                if response.status_code == 200:
                    data = response.json()
                    if str(app_id) in data and "data" in data[str(app_id)]:
                        game_data = data[str(app_id)]["data"]
                        game_name = game_data["name"]
                        game_release_date = game_data["release_date"]["date"]
                        game_developer = game_data["developers"][0]
                        game_publisher = game_data["publishers"][0]
                        game_description = game_data["short_description"]
                        game_link = f"https://store.steampowered.com/app/{app_id}"
                        game_image = game_data["header_image"]
                        message = f"**Game Name:** {game_name}\n**Release Date:** {game_release_date}\n**Developer:** {game_developer}\n**Publisher:** {game_publisher}\n**Description:** {game_description}\n**Game Link:** {game_link}"
                        embed = discord.Embed(title="Steam Game Info", description=message)
                        embed.set_thumbnail(url=game_image)
                        await ctx.send(embed=embed.to_dict())
                        return
    await ctx.send("Failed to get Steam game information")

@slash_command(name="random_skin", description="Get a random CSGO skin")
async def random_skin_function(ctx: SlashContext):
    await ctx.defer()
    skins_api_url = "https://bymykel.github.io/CSGO-API/api/en/skins.json"
    response = requests.get(skins_api_url)
    if response.status_code == 200:
        skins_data = response.json()
        random_skin = random.choice(skins_data)
        skin_name = random_skin["name"]
        skin_description = random_skin["description"]
        skin_image_url = random_skin["image"]
        embed = discord.Embed(title=skin_name, description=skin_description)
        embed.set_image(url=skin_image_url)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Failed to get CSGO skins information")

@slash_command(name="anime_quote", description="Get a random anime quote")
async def anime_quote_function(ctx: SlashContext):
    await ctx.defer()
    anime_api_url = "https://animechan.xyz/api/random"
    response = requests.get(anime_api_url)
    if response.status_code == 200:
        data = response.json()
        quote = data["quote"]
        character = data["character"]
        anime = data["anime"]
        message = f"**Quote:** {quote}\n**Character:** {character}\n**Anime:** {anime}"
        embed = discord.Embed(title="Anime Quote", description=message)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Failed to get anime quote")

@slash_command(name="anime_image", description="Get a random anime image")
async def anime_image_function(ctx: SlashContext):
    await ctx.defer()
    api_url = "https://nekos.best/api/v2/neko"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        image_url = data["results"][0]["url"]
        artist_name = data["results"][0]["artist_name"]
        source_url = data["results"][0]["source_url"]
        embed = discord.Embed(title="Random Anime Image", description=f"Artist: {artist_name}\nSource: {source_url}")
        embed.set_image(url=image_url)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Failed to get anime image")

@slash_command(name="anime_waifu", description="Get a random anime waifu")
@slash_option(
    name="tag",
    description="Choose a tag for the waifu image",
    required=True,
    opt_type=3,
    choices=[
        SlashCommandChoice(name="waifu", value="waifu"),
        SlashCommandChoice(name="maid", value="maid"),
        SlashCommandChoice(name="marin-kitagawa", value="marin-kitagawa"),
        SlashCommandChoice(name="mori-calliope", value="mori-calliope"),
        SlashCommandChoice(name="raiden-shogun", value="raiden-shogun"),
        SlashCommandChoice(name="oppai", value="oppai"),
        SlashCommandChoice(name="selfies", value="selfies"),
        SlashCommandChoice(name="uniform", value="uniform")
    ]
)
async def anime_waifu_function(ctx: SlashContext, tag: str):
    await ctx.defer()
    url = 'https://api.waifu.im/search'
    params = {
        'included_tags': [tag],
        'height': '>=2000'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        image_url = data["images"][0]["url"]
        source_url = data["images"][0]["source"]
        embed = discord.Embed(title="Random Anime Waifu", description=f"Tag: {tag}\nSource: {source_url}")
        embed.set_image(url=image_url)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Failed to get anime waifu image")

@slash_command(name="bacon_image", description="Get a bacon image of the size of your choice")
@slash_option(
    name="width",
    description="Enter the width of the image",
    required=True,
    opt_type=OptionType.INTEGER
)
@slash_option(
    name="height",
    description="Enter the height of the image",
    required=True,
    opt_type=OptionType.INTEGER
)
async def bacon_image_function(ctx: SlashContext, width: int, height: int):
    await ctx.defer()
    image_url = f"https://baconmockup.com/{width}/{height}"
    embed = discord.Embed(title="Bacon Image")
    embed.set_image(url=image_url)
    await ctx.send(embed=embed.to_dict())

@slash_command(name="coffee_image", description="Get a random coffee image")
async def coffee_image_function(ctx: SlashContext):
    await ctx.defer()
    response = requests.get("https://coffee.alexflipnote.dev/random.json")
    image_url = response.json()["file"]
    embed = discord.Embed(title="Coffee Image")
    embed.set_image(url=image_url)
    await ctx.send(embed=embed.to_dict())

@slash_command(name="game_cheapest_deal", description="Get the cheapest deal for a specific game")
@slash_option(
    name="game_name",
    description="Enter the name of the game",
    required=True,
    opt_type=OptionType.STRING
)
async def game_cheapest_deal_function(ctx: SlashContext, game_name: str):
    await ctx.defer()
    url = f"https://www.cheapshark.com/api/1.0/games?title={game_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            games_list = ""
            for i, game in enumerate(data):
                game_title = game["external"]
                game_price = game["cheapest"]
                game_deal_id = game["cheapestDealID"]
                games_list += f"**Title:** {game_title}\n**Price:** {game_price}\n**Deal:** https://www.cheapshark.com/redirect?dealID={game_deal_id}\n\n"
                if (i+1) % 10 == 0:
                    embed = discord.Embed(title=f"All deals for {game_name}", description=games_list)
                    await ctx.send(embed=embed.to_dict())
                    games_list = ""
            if games_list:
                embed = discord.Embed(title=f"All deals for {game_name}", description=games_list)
                await ctx.send(embed=embed.to_dict())
        else:
            await ctx.send(f"No results found for {game_name}")
    else:
        await ctx.send("Failed to get cheapest deal for game")

@slash_command(name="minecraft_player_info", description="Get information about a Minecraft player")
@slash_option(
    name="username",
    description="Enter the username of the Minecraft player",
    required=True,
    opt_type=OptionType.STRING
)
async def minecraft_player_info_function(ctx: SlashContext, username: str):
    await ctx.defer()
    timestamp = int(datetime.now().timestamp() * 1000)
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}?at={timestamp}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        uuid = data["id"]
        skin_preview_url = f"https://crafatar.com/renders/body/{uuid}"
        embed = discord.Embed(title=f"{username}", description=f"**UUID:** {uuid}")
        embed.set_image(url=skin_preview_url)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send(f"Failed to get information for {username}")

@slash_command(name="minecraft_server_info", description="Get information about a Minecraft server")
@slash_option(
    name="server_address",
    description="Enter the address of the Minecraft server",
    required=True,
    opt_type=OptionType.STRING
)
@slash_option(
    name="bedrock",
    description="Is the server a Bedrock server?",
    required=False,
    opt_type=OptionType.BOOLEAN
)
async def minecraft_server_info_function(ctx: SlashContext, server_address: str, bedrock: bool = False):
    await ctx.defer()
    if bedrock:
        url = f"https://api.mcsrvstat.us/bedrock/3/{server_address}"
    else:
        url = f"https://api.mcsrvstat.us/3/{server_address}"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            server_name = data.get("motd", {}).get("clean", "Unknown")
            server_ip_port = f"{data.get('ip', 'Unknown')}:{data.get('port', 'Unknown')}"
            server_status = "Online" if data.get("online", False) else "Offline"
            server_version = data.get("version", "Unknown")
            gamemode = data.get("gamemode", None)
            players_online = data.get("players", {}).get("online", "Unknown")
            players_max = data.get("players", {}).get("max", "Unknown")
            players = f"{players_online}/{players_max}"
            plugins = [f"{plugin.get('name')} ({plugin.get('version')})" for plugin in data.get("plugins", [])]
            mods = [f"{mod.get('name')} ({mod.get('version')})" for mod in data.get("mods", [])]

            embed = discord.Embed(title=f"{server_name}", description=f"**IP:Port:** {server_ip_port}\n**Status:** {server_status}\n**Version:** {server_version}\n**Players:** {players}")
            if gamemode:
                embed.add_field(name="Gamemode", value=gamemode, inline=False)
            if plugins:
                embed.add_field(name="Plugins", value=", ".join(plugins), inline=False)
            if mods:
                embed.add_field(name="Mods", value=", ".join(mods), inline=False)

            await ctx.send(embed=embed.to_dict())
        except ValueError:
            await ctx.send(f"Failed to parse response from {url}")
    else:
        await ctx.send(f"Failed to get information for {server_address}")

@slash_command(name="draw_a_card", description="Draw a random card a specified number of times")
@slash_option(
    name="number_of_cards",
    description="Enter the number of cards to draw",
    required=True,
    opt_type=OptionType.INTEGER
)
async def draw_a_card_function(ctx: SlashContext, number_of_cards: int):
    response = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1")
    if response.status_code == 200:
        data = response.json()
        deck_id = data.get("deck_id")
        response = requests.get(f"https://deckofcardsapi.com/api/deck/{deck_id}/draw/?count={number_of_cards}")
        if response.status_code == 200:
            data = response.json()
            cards = data.get("cards")
            embed = discord.Embed(title=f"Drawn {number_of_cards} cards from deck {deck_id}")
            for card in cards:
                embed.set_image(url=card.get("image"))
                await ctx.send(embed=embed.to_dict())
        else:
            await ctx.send(f"Failed to draw cards from deck {deck_id}")
    else:
        await ctx.send("Failed to shuffle a new deck")

import random

@slash_command(name="random_number", description="Get a random number between two specified numbers")
@slash_option(
    name="min",
    description="Enter the minimum value",
    required=True,
    opt_type=OptionType.INTEGER
)
@slash_option(
    name="max",
    description="Enter the maximum value",
    required=True,
    opt_type=OptionType.INTEGER
)
async def random_number_function(ctx: SlashContext, min: int, max: int):
    if min >= max:
        await ctx.send("The minimum value must be less than the maximum value.")
        return
    number = random.randint(min, max)
    await ctx.send(f"Your random number between {min} and {max} is {number}.")

@slash_command(name="random_giveaway", description="Get a random giveaway from the list of giveaways")
async def random_giveaway_function(ctx: SlashContext):
    response = requests.get("https://www.gamerpower.com/api/giveaways")
    if response.status_code == 200:
        data = response.json()
        giveaway = random.choice(data)
        embed = discord.Embed(title=giveaway.get("title"), description=giveaway.get("description"))
        embed.set_thumbnail(url=giveaway.get("thumbnail"))
        embed.add_field(name="Worth", value=giveaway.get("worth"), inline=True)
        embed.add_field(name="Platforms", value=giveaway.get("platforms"), inline=True)
        embed.add_field(name="End Date", value=giveaway.get("end_date"), inline=True)
        embed.add_field(name="Instructions", value=giveaway.get("instructions"), inline=False)
        embed.add_field(name="Open Giveaway URL", value=giveaway.get("open_giveaway_url"), inline=False)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Failed to get giveaways from GamerPower API.")


@slash_command(name="random_joke", description="Get a random joke")
async def random_joke_function(ctx: SlashContext):
    response = requests.get("https://official-joke-api.appspot.com/random_joke")
    if response.status_code == 200:
        data = response.json()
        setup = data.get("setup")
        punchline = data.get("punchline")
        embed = discord.Embed(title="Random Joke")
        embed.add_field(name="", value=setup, inline=False)
        embed.add_field(name="", value=punchline, inline=False)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Failed to get a random joke.")

@slash_command(name="random_dog", description="Get a random dog image")
async def random_dog_function(ctx: SlashContext):
    response = requests.get("https://dog.ceo/api/breeds/image/random")
    if response.status_code == 200:
        data = response.json()
        image_url = data.get("message")
        embed = discord.Embed(title="Random Dog Image")
        embed.set_image(url=image_url)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Failed to get a random dog image.")

import requests
import discord

@slash_command(name="steam_users", description="Get the number of steam users online and in game")
async def steam_users_function(ctx: SlashContext):
    response = requests.get("https://www.valvesoftware.com/about/stats")
    if response.status_code == 200:
        data = response.json()
        users_online = data.get("users_online")
        users_ingame = data.get("users_ingame")
        embed = discord.Embed(title="Steam Users")
        embed.add_field(name="Users Online", value=users_online, inline=False)
        embed.add_field(name="Users In Game", value=users_ingame, inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Failed to get the number of steam users online and in game.")

@slash_command(name="vacances_scolaires", description="Get the dates of the school holidays in Versailles")
@slash_option(
    name="year",
    description="Choose a year for the school holidays",
    required=True,
    opt_type=3,
    choices=[
        SlashCommandChoice(name="2023-2024", value="2023-2024"),
        SlashCommandChoice(name="2024-2025", value="2024-2025")
    ]
)
async def vacances_scolaires_function(ctx: SlashContext, year: str):
    response = requests.get(f"https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records?where=annee_scolaire%3D%22{year}%22%20AND%20location%3D%22Versailles%22&order_by=start_date&limit=100")
    if response.status_code == 200:
        data = response.json()
        embed = discord.Embed(title=f"School Holidays in Versailles ({year})", color=0x00ff00)
        for holiday in data["results"]:
            start_date = holiday["start_date"]
            end_date = holiday["end_date"]
            embed.add_field(name=holiday["description"], value=f"{start_date} - {end_date}", inline=False)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Failed to get the school holidays in Versailles.")

@slash_command(name="ville_infos", description="Get information about a city")
@slash_option(
    name="postal_code",
    description="Enter the postal code of the city",
    required=True,
    opt_type=OptionType.INTEGER
)
async def ville_infos_function(ctx: SlashContext, postal_code: int):
    response = requests.get(f"https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/correspondance-code-insee-code-postal/records?where=postal_code%3D%22{postal_code}%22&limit=1")
    if response.status_code == 200:
        data = response.json()
        city_name = data["results"][0]["nom_comm"]
        insee_code = data["results"][0]["insee_com"]
        department = data["results"][0]["nom_dept"][0] # remove the [''] from department
        region = data["results"][0]["nom_region"][0] # remove the [''] from region
        population = data["results"][0]["population"]
        embed = discord.Embed(title=f"Information about {city_name}", color=0x00ff00)
        embed.add_field(name="INSEE Code", value=insee_code, inline=False)
        embed.add_field(name="Department", value=department, inline=False)
        embed.add_field(name="Region", value=region, inline=False)
        embed.add_field(name="Population (in thousands)", value=population, inline=False)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Failed to get information about the city.")

@slash_command(name="risques_naturels", description="Get information about natural risks in a city / territory")
@slash_option(
    name="insee_code",
    description="Enter the INSEE code of the city / territory",
    required=True,
    opt_type=OptionType.INTEGER
)
async def risques_naturels_function(ctx: SlashContext, insee_code: int):
    response = requests.get(f"https://www.georisques.gouv.fr/api/v1/gaspar/risques?code_insee={insee_code}&page=1&page_size=10&rayon=1000")
    if response.status_code == 200:
        data = response.json()
        if len(data["data"]) == 0:
            await ctx.send("No natural risks found in the city / territory.")
        else:
            embed = discord.Embed(title=f"Natural Risks in {data['data'][0]['libelle_commune']}", color=0x00ff00)
            for risque in data["data"][0]["risques_detail"]:
                embed.add_field(name=risque["libelle_risque_long"], value=f"Numéro de risque: {risque['num_risque']}\nZone de sismicité: {risque['zone_sismicite']}", inline=False)
            await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Failed to get information about natural risks in the city / territory.")

@slash_command(name="jours_feries", description="Get the public holidays in France")
@slash_option(
    name="year",
    description="Choose a year for the school holidays",
    required=True,
    opt_type=3,
    choices=[
        SlashCommandChoice(name="2023", value="2023"),
        SlashCommandChoice(name="2024", value="2024"),
        SlashCommandChoice(name="2025", value="2025"),
        SlashCommandChoice(name="2026", value="2026")
    ]
)
async def jours_feries_function(ctx: SlashContext, year: int):
    response = requests.get(f"https://calendrier.api.gouv.fr/jours-feries/metropole/{year}.json")
    if response.status_code == 200:
        data = response.json()
        holidays = "\n".join([f"**{date}**: {name}" for date, name in data.items()])
        embed = discord.Embed(title=f"Public Holidays in {year}", description=holidays, color=0x00ff00)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Failed to get public holidays for the year.")

@slash_command(name="ville_stations_essences", description="Get the fuel stations in a city")
@slash_option(
    name="postal_code",
    description="Enter the postal code of the city",
    required=True,
    opt_type=OptionType.INTEGER
)
async def ville_stations_essences_function(ctx: SlashContext, postal_code: int):
    response = requests.get(f"https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/records?where=cp%3D%22{postal_code}%22&limit=100")
    if response.status_code == 200:
        data = response.json()
        if data['total_count'] == 0:
            await ctx.send("The city has no fuel station...")
        else:
            embed = discord.Embed(title=f"Fuel Prices in {data['results'][0]['ville']}", color=0x00ff00)
            for record in data["results"]:
                carburants = ', '.join(record['carburants_disponibles']) if isinstance(record['carburants_disponibles'], list) else record['carburants_disponibles']
                services = ', '.join(record['services_service']) if isinstance(record['services_service'], list) else record['services_service']
                embed.add_field(name=record["adresse"], value=f"**Carburants disponibles:** {carburants}\n**24/24 Automate:** {record['horaires_automate_24_24']}\n**Services:** {services}", inline=False)
            await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Failed to get fuel prices for the city.")

@slash_command(name="ville_meteo", description="Get the weather in a city")
@slash_option(
    name="postal_code",
    description="Enter the postal code of the city",
    required=True,
    opt_type=OptionType.INTEGER
)
async def ville_meteo_function(ctx: SlashContext, postal_code: int):
    response = requests.get(f"https://geo.api.gouv.fr/communes?codePostal={postal_code}&fields=nom,code,codesPostaux,centre&format=json&geometry=centre")
    if response.status_code == 200:
        data = response.json()
        if len(data) == 0:
            await ctx.send("No city found for the given postal code.")
        else:
            city_name = data[0]["nom"]
            city_code = data[0]["code"]
            response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?appid=<YOUR_API_KEY>&q={city_name},{city_code},FR&units=metric")
            if response.status_code == 200:
                data = response.json()
                weather_description = data["weather"][0]["description"]
                temperature = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                humidity = data["main"]["humidity"]
                wind_speed = data["wind"]["speed"]
                embed = discord.Embed(title=f"Weather in {city_name}", description=weather_description, color=0x00ff00)
                embed.add_field(name="Temperature", value=f"{temperature}°C", inline=True)
                embed.add_field(name="Feels Like", value=f"{feels_like}°C", inline=True)
                embed.add_field(name="Humidity", value=f"{humidity}%", inline=True)
                embed.add_field(name="Wind Speed", value=f"{wind_speed} m/s", inline=True)
                await ctx.send(embed=embed.to_dict())
            else:
                await ctx.send("Failed to get weather information for the city.")
    else:
        await ctx.send("Failed to get city information for the postal code.")

@slash_command(name="ville_musées_de_france", description="Get the museums with the Musée de France appelation in a city")
@slash_option(
    name="postal_code",
    description="Enter the postal code of the city",
    required=True,
    opt_type=OptionType.INTEGER
)
async def ville_musees_de_france_function(ctx: SlashContext, postal_code: int):
    response = requests.get(f"https://data.culture.gouv.fr/api/explore/v2.1/catalog/datasets/musees-de-france-base-museofile/records?where=cp_m%3D%22{postal_code}%22&limit=100")
    if response.status_code == 200:
        data = response.json()
        if data['total_count'] == 0:
            await ctx.send(f"No museum with Musée de France appelation found in {postal_code}...")
        else:
            embed = discord.Embed(title=f"Museums with Musée de France appelation in {postal_code}", color=0x00ff00)
            for record in data["results"]:
                embed.add_field(name="Museum name", value=record.get("autnom", "unknown"), inline=False)
                embed.add_field(name="Museum address", value=record.get("adrl1_m", "unknown"), inline=False)
                embed.add_field(name="Categories", value=', '.join(record.get("categ", ["unknown"])), inline=False)
                embed.add_field(name="DomPal", value=', '.join(record.get("dompal", ["unknown"])), inline=False)
            await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Failed to get museums information for the city.")

@slash_command(name="gare_au_hasard", description="Get a random train station in Ile-de-France")
async def gare_au_hasard_function(ctx: SlashContext):
    response = requests.get("https://data.iledefrance.fr/api/explore/v2.1/catalog/datasets/gares_ferroviaires_de_tous_types_exploitees_ou_non/records?limit=100")
    if response.status_code == 200:
        data = response.json()
        if data['total_count'] == 0:
            await ctx.send("No train station found in Ile-de-France...")
        else:
            record = random.choice(data["results"])
            embed = discord.Embed(title=record.get("nom", "unknown"), color=0x00ff00)
            embed.add_field(name="City", value=record.get("ville", ["unknown"])[0], inline=False)
            embed.add_field(name="Usage", value=', '.join(record.get("nature", ["unknown"])), inline=False)
            await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Failed to get train station information.")

@slash_command(name="gare_ligne", description="Get the train stations on a specific line")
@slash_option(
    name="line",
    description="Choose the line",
    required=True,
    opt_type=3,
    choices=[
        SlashCommandChoice(name="RER A", value="A"),
        SlashCommandChoice(name="RER B", value="B"),
        SlashCommandChoice(name="RER C", value="C"),
        SlashCommandChoice(name="RER D", value="D"),
        SlashCommandChoice(name="RER E", value="E"),
        SlashCommandChoice(name="Train H", value="H"),
        SlashCommandChoice(name="Train J", value="J"),
        SlashCommandChoice(name="Train K", value="K"),
        SlashCommandChoice(name="Train L", value="L"),
        SlashCommandChoice(name="Train N", value="N"),
        SlashCommandChoice(name="Train P", value="P"),
        SlashCommandChoice(name="Train R", value="R"),
        SlashCommandChoice(name="Train U", value="U")
    ]
)
async def gare_ligne_function(ctx: SlashContext, line: str):
    response = requests.get(f"https://data.iledefrance.fr/api/explore/v2.1/catalog/datasets/gares-et-stations-du-reseau-ferre-dile-de-france-par-ligne/records?where=indice_lig=\"{line}\"&limit=100")
    if response.status_code == 200:
        data = response.json()
        if data['total_count'] == 0:
            await ctx.send(f"No train station found on line {line}...")
        else:
            embed = discord.Embed(title=f"Train stations on line {line}", color=0x00ff00)
            station_count = len(data["results"])
            embed.add_field(name="Number of stations", value=station_count, inline=False)
            
            for i, record in enumerate(data["results"]):
                if i >= 5:
                    break
                embed.add_field(name=record.get("nom_gares", ["unknown"]), value=record.get("exploitant", "unknown"), inline=False)
            
            if station_count > 5:
                if line in ["A", "B", "C", "D", "E"]:
                    url = f"https://www.bonjour-ratp.fr/lignes-rer/ligne-{line.lower()}/"
                else:
                    url = f"https://www.bonjour-ratp.fr/lignes-transilien/ligne-{line.lower()}/"
                button = Button(
                    style=ButtonStyle.URL,
                    label="Voir plus",
                    url=url,
                )
                await ctx.send(embed=embed.to_dict(), components=[[button]])
            else:
                await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Failed to get train station information.")

@slash_command(name="tarifs_transports_idf", description="Get the transport prices in Ile-de-France")
async def tarifs_transports_IDF_function(ctx: SlashContext):
    response = requests.get("https://data.iledefrance.fr/api/explore/v2.1/catalog/datasets/description-et-tarif-des-titres-de-transport-en-ile-de-france/records?limit=100")
    if response.status_code == 200:
        data = response.json()
        if data['total_count'] == 0:
            await ctx.send("No transport prices found in Ile-de-France...")
        else:
            embed1 = discord.Embed(title="Transport prices in Ile-de-France (1/2)", color=0x00ff00)
            embed2 = discord.Embed(title="Transport prices in Ile-de-France (2/2)", color=0x00ff00)
            count = 0
            for record in data["results"]:
                url = record.get("url", "unknown")
                field_value = f"{record.get('short_description', 'unknown')}\n[Buy it]({url})"
                if count < 25:
                    embed1.add_field(name=f"{record.get('product_name', 'unknown')} - Price: {record.get('price', 'unknown')}", value=field_value, inline=False)
                else:
                    embed2.add_field(name=f"{record.get('product_name', 'unknown')} - Price: {record.get('price', 'unknown')}", value=field_value, inline=False)
                count += 1
            await ctx.send(embed=embed1.to_dict())
            if count > 25:
                await ctx.send(embed=embed2.to_dict())
    else:
        await ctx.send("Failed to get transport prices information.")

@slash_command(name="ville_amie_des_animaux",description="Check if a city is friend of animals")
@slash_option(
    name="city_name",
    description="Enter the name of the city",
    required=True,
    opt_type=OptionType.STRING
)
async def ville_amie_des_animaux(ctx: SlashContext, city_name: str):
    response = requests.get(f"https://data.iledefrance.fr/api/explore/v2.1/catalog/datasets/label-ville-amie-des-animaux/records?where=commune%3D%22{city_name}%22&order_by=annee&limit=20")
    if response.status_code == 200:
        data = response.json()
        if data['total_count'] == 0:
            await ctx.send(f"{city_name} is not friend of animals...")
        else:
            embed = discord.Embed(title=f"{city_name} - Friend of animals", color=0x00ff00)
            for record in data["results"]:
                embed.add_field(name="Distinction", value=record.get("distinction", "unknown"), inline=False)
                embed.add_field(name="Year", value=record.get("annee", "unknown"), inline=False)
            await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Failed to get information about the city.")

bot.start()