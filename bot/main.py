import datetime
import interactions
import requests
from interactions import slash_command, SlashContext, OptionType, slash_option, SlashCommandChoice, Button, ButtonStyle
import discord
import random
from datetime import datetime


'''
Voir la documentation pour plus d'informations sur la façon de configurer le robot.
'''

bot = interactions.Client(token="Votre token")

'''
Tous les événements sont définis ci-dessous.
'''



'''
Toutes les commandes slash sont définies ci-dessous.
'''

@slash_command(name="aide", description="Obtenir une liste de toutes les commandes disponibles")
async def aide_commande(ctx: SlashContext):
    await ctx.defer()
    commandes = [
        {
            "name": "aide",
            "description": "Obtenir une liste de toutes les commandes disponibles"
        },
        {
            "name": "info",
            "description": "Obtenir des informations sur le bot"
        },
        {
            "name": "info_serveur",
            "description": "Obtenir des informations sur un serveur de jeu Steam"
        },
        {
            "name": "info_utilisateur_steam",
            "description": "Obtenir des informations sur un utilisateur Steam"
        }
    ]
    message = "Voici les commandes disponibles :\n"
    for commande in commandes:
        message += f"**/{commande['name']}**: {commande['description']}\n"
    embed = discord.Embed(title="Aide", description=message)
    await ctx.send(embed=embed.to_dict())

@slash_command(name="info", description="Obtenir des informations sur le bot")
async def info_bot_fonction(ctx: SlashContext):
    await ctx.defer()
    nom_bot = bot.user.display_name
    id_bot = bot.user.id
    avatar_bot = bot.user.avatar_url
    message = f"**Nom du bot:** {nom_bot}\n**ID du bot:** {id_bot}"
    embed = discord.Embed(title="Informations sur le bot", description=message)
    embed.set_thumbnail(url=avatar_bot)
    embed.set_footer(text="Créé par algorythm")
    await ctx.send(embed=embed.to_dict())

@slash_command(name="server_info", description="Obtenir des informations sur un serveur de jeu Steam")
@slash_option(
    name="ip_address",
    description="Entrez l'adresse IP et le port du serveur au format IP:Port",
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
                        message = f"**Adresse du serveur:** {server_info['addr']}\n**Jeu:** {game_name}\n**VAC sécurisé:** {server_info['secure']}"
                        embed = discord.Embed(title=game_name, url=game_link, description=message)
                        embed.set_thumbnail(url=game_image)
                        await ctx.send(embed=embed.to_dict())
                        return
    await ctx.send("Impossible d'obtenir les informations du serveur")

@slash_command(name="steam_user_info", description="Obtenir des informations sur un utilisateur Steam")
@slash_option(
    name="steam_id",
    description="Entrez l'ID Steam de l'utilisateur",
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
            message = f"**ID Steam:** {steam_id}\n**Nom du compte Steam:** {player_name}\n**Lien du compte Steam:** {player_link}\n**Dernière déconnexion:** {last_logoff}\n**ID du groupe principal:** [{primary_group_id}]({primary_group_link})\n**Code de pays de localisation:** {loc_country_code}"
            embed = discord.Embed(title="Informations sur l'utilisateur Steam", description=message)
            embed.set_thumbnail(url=player_avatar)
            
            # Obtenir les jeux récemment joués
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

@slash_command(name="steam_game_info", description="Obtenir des informations sur un jeu Steam spécifique")
@slash_option(
    name="nom_jeu",
    description="Entrez le nom du jeu",
    required=True,
    opt_type=OptionType.STRING
)
async def steam_game_info_function(ctx: SlashContext, nom_jeu: str):
    await ctx.defer()
    steam_api_url = f"https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    response = requests.get(steam_api_url)
    if response.status_code == 200:
        data = response.json()
        if "applist" in data and "apps" in data["applist"]:
            app_list = data["applist"]["apps"]
            app_id = None
            for app in app_list:
                if app["name"].lower() == nom_jeu.lower():
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
                        message = f"**Nom du jeu:** {game_name}\n**Date de sortie:** {game_release_date}\n**Développeur:** {game_developer}\n**Éditeur:** {game_publisher}\n**Description:** {game_description}\n**Lien du jeu:** {game_link}"
                        embed = discord.Embed(title="Informations sur le jeu Steam", description=message)
                        embed.set_thumbnail(url=game_image)
                        await ctx.send(embed=embed.to_dict())
                        return
    await ctx.send("Impossible d'obtenir les informations sur le jeu Steam")

@slash_command(name="random_skin", description="Obtenir un skin CSGO aléatoire")
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
        await ctx.send("Impossible d'obtenir les informations sur les skins CSGO")

@slash_command(name="anime_quote", description="Obtenir une citation aléatoire d'anime")
async def anime_quote_function(ctx: SlashContext):
    await ctx.defer()
    anime_api_url = "https://animechan.xyz/api/random"
    response = requests.get(anime_api_url)
    if response.status_code == 200:
        data = response.json()
        quote = data["quote"]
        character = data["character"]
        anime = data["anime"]
        message = f"**Citation :** {quote}\n**Personnage :** {character}\n**Anime :** {anime}"
        embed = discord.Embed(title="Citation d'anime", description=message)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Impossible d'obtenir une citation d'anime")

@slash_command(name="anime_image", description="Obtenir une image aléatoire d'anime")
async def anime_image_function(ctx: SlashContext):
    await ctx.defer()
    api_url = "https://nekos.best/api/v2/neko"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        image_url = data["results"][0]["url"]
        artist_name = data["results"][0]["artist_name"]
        source_url = data["results"][0]["source_url"]
        embed = discord.Embed(title="Image aléatoire d'anime", description=f"Artiste : {artist_name}\nSource : {source_url}")
        embed.set_image(url=image_url)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Impossible d'obtenir une image d'anime")

@slash_command(name="anime_waifu", description="Obtenir une waifu aléatoire d'anime")
@slash_option(
    name="tag",
    description="Choisir un tag pour l'image de waifu",
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
        embed = discord.Embed(title="Waifu aléatoire d'anime", description=f"Tag : {tag}\nSource : {source_url}")
        embed.set_image(url=image_url)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Impossible d'obtenir une image de waifu d'anime")

@slash_command(name="bacon_image", description="Obtenir une image de bacon de la taille de votre choix")
@slash_option(
    name="largeur",
    description="Entrer la largeur de l'image",
    required=True,
    opt_type=OptionType.INTEGER
)
@slash_option(
    name="hauteur",
    description="Entrer la hauteur de l'image",
    required=True,
    opt_type=OptionType.INTEGER
)
async def bacon_image_function(ctx: SlashContext, largeur: int, hauteur: int):
    await ctx.defer()
    image_url = f"https://baconmockup.com/{largeur}/{hauteur}"
    embed = discord.Embed(title="Image de bacon")
    embed.set_image(url=image_url)
    await ctx.send(embed=embed.to_dict())

@slash_command(name="coffee_image", description="Obtenir une image de café aléatoire")
async def coffee_image_function(ctx: SlashContext):
    await ctx.defer()
    response = requests.get("https://coffee.alexflipnote.dev/random.json")
    image_url = response.json()["file"]
    embed = discord.Embed(title="Image de café")
    embed.set_image(url=image_url)
    await ctx.send(embed=embed.to_dict())

@slash_command(name="game_cheapest_deal", description="Obtenir la meilleure offre pour un jeu spécifique")
@slash_option(
    name="nom_jeu",
    description="Entrer le nom du jeu",
    required=True,
    opt_type=OptionType.STRING
)
async def game_cheapest_deal_function(ctx: SlashContext, nom_jeu: str):
    await ctx.defer()
    url = f"https://www.cheapshark.com/api/1.0/games?title={nom_jeu}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            liste_jeux = ""
            for i, jeu in enumerate(data):
                titre_jeu = jeu["external"]
                prix_jeu = jeu["cheapest"]
                deal_id_jeu = jeu["cheapestDealID"]
                liste_jeux += f"**Titre:** {titre_jeu}\n**Prix:** {prix_jeu}\n**Offre:** https://www.cheapshark.com/redirect?dealID={deal_id_jeu}\n\n"
                if (i+1) % 10 == 0:
                    embed = discord.Embed(title=f"Toutes les offres pour {nom_jeu}", description=liste_jeux)
                    await ctx.send(embed=embed.to_dict())
                    liste_jeux = ""
            if liste_jeux:
                embed = discord.Embed(title=f"Toutes les offres pour {nom_jeu}", description=liste_jeux)
                await ctx.send(embed=embed.to_dict())
        else:
            await ctx.send(f"Aucun résultat trouvé pour {nom_jeu}")
    else:
        await ctx.send("Impossible d'obtenir la meilleure offre pour le jeu")

@slash_command(name="minecraft_player_info", description="Obtenir des informations sur un joueur Minecraft")
@slash_option(
    name="username",
    description="Entrez le nom d'utilisateur du joueur Minecraft",
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
        await ctx.send(f"Impossible d'obtenir des informations pour {username}")

@slash_command(name="minecraft_server_info", description="Obtenir des informations sur un serveur Minecraft")
@slash_option(
    name="server_address",
    description="Entrez l'adresse du serveur Minecraft",
    required=True,
    opt_type=OptionType.STRING
)
@slash_option(
    name="bedrock",
    description="Le serveur est-il un serveur Bedrock ?",
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
            server_name = data.get("motd", {}).get("clean", "Inconnu")
            server_ip_port = f"{data.get('ip', 'Inconnu')}:{data.get('port', 'Inconnu')}"
            server_status = "En ligne" if data.get("online", False) else "Hors ligne"
            server_version = data.get("version", "Inconnu")
            gamemode = data.get("gamemode", None)
            players_online = data.get("players", {}).get("online", "Inconnu")
            players_max = data.get("players", {}).get("max", "Inconnu")
            players = f"{players_online}/{players_max}"
            plugins = [f"{plugin.get('name')} ({plugin.get('version')})" for plugin in data.get("plugins", [])]
            mods = [f"{mod.get('name')} ({mod.get('version')})" for mod in data.get("mods", [])]

            embed = discord.Embed(title=f"{server_name}", description=f"**IP:Port:** {server_ip_port}\n**Statut:** {server_status}\n**Version:** {server_version}\n**Joueurs:** {players}")
            if gamemode:
                embed.add_field(name="Mode de jeu", value=gamemode, inline=False)
            if plugins:
                embed.add_field(name="Plugins", value=", ".join(plugins), inline=False)
            if mods:
                embed.add_field(name="Mods", value=", ".join(mods), inline=False)

            await ctx.send(embed=embed.to_dict())
        except ValueError:
            await ctx.send(f"Impossible d'analyser la réponse de {url}")
    else:
        await ctx.send(f"Impossible d'obtenir des informations pour {server_address}")

@slash_command(name="draw_a_card", description="Tirer une carte aléatoire un nombre spécifié de fois")
@slash_option(
    name="number_of_cards",
    description="Entrez le nombre de cartes à tirer",
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
            embed = discord.Embed(title=f"Tiré {number_of_cards} cartes du paquet {deck_id}")
            for card in cards:
                embed.set_image(url=card.get("image"))
                await ctx.send(embed=embed.to_dict())
        else:
            await ctx.send(f"Impossible de tirer des cartes du paquet {deck_id}")
    else:
        await ctx.send("Impossible de mélanger un nouveau paquet")


@slash_command(name="random_number", description="Obtenir un nombre aléatoire entre deux nombres spécifiés")
@slash_option(
    name="min",
    description="Entrez la valeur minimale",
    required=True,
    opt_type=OptionType.INTEGER
)
@slash_option(
    name="max",
    description="Entrez la valeur maximale",
    required=True,
    opt_type=OptionType.INTEGER
)
async def random_number_function(ctx: SlashContext, min: int, max: int):
    if min >= max:
        await ctx.send("La valeur minimale doit être inférieure à la valeur maximale.")
        return
    number = random.randint(min, max)
    await ctx.send(f"Votre nombre aléatoire entre {min} et {max} est {number}.")

@slash_command(name="giveaway_au_hasard", description="Obtenir un giveaway aléatoire de la liste des giveaways")
async def cadeau_au_hasard_fonction(ctx: SlashContext):
    response = requests.get("https://www.gamerpower.com/api/giveaways")
    if response.status_code == 200:
        data = response.json()
        giveaway = random.choice(data)
        embed = discord.Embed(title=giveaway.get("title"), description=giveaway.get("description"))
        embed.set_thumbnail(url=giveaway.get("thumbnail"))
        embed.add_field(name="Valeur", value=giveaway.get("worth"), inline=True)
        embed.add_field(name="Plateformes", value=giveaway.get("platforms"), inline=True)
        embed.add_field(name="Date de fin", value=giveaway.get("end_date"), inline=True)
        embed.add_field(name="Instructions", value=giveaway.get("instructions"), inline=False)
        embed.add_field(name="URL du giveaway", value=giveaway.get("open_giveaway_url"), inline=False)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Impossible d'obtenir des cadeaux depuis l'API GamerPower.")

@slash_command(name="chien_au_hasard", description="Obtenir une image de chien aléatoire")
async def chien_au_hasard_fonction(ctx: SlashContext):
    response = requests.get("https://dog.ceo/api/breeds/image/random")
    if response.status_code == 200:
        data = response.json()
        url_image = data.get("message")
        embed = discord.Embed(title="Image de chien aléatoire")
        embed.set_image(url=url_image)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Impossible d'obtenir une image de chien aléatoire.")

@slash_command(name="utilisateurs_steam", description="Obtenir le nombre d'utilisateurs Steam en ligne et en jeu")
async def utilisateurs_steam_fonction(ctx: SlashContext):
    response = requests.get("https://www.valvesoftware.com/about/stats")
    if response.status_code == 200:
        data = response.json()
        utilisateurs_en_ligne = data.get("users_online")
        utilisateurs_en_jeu = data.get("users_ingame")
        embed = discord.Embed(title="Utilisateurs Steam")
        embed.add_field(name="Utilisateurs en ligne", value=utilisateurs_en_ligne, inline=False)
        embed.add_field(name="Utilisateurs en jeu", value=utilisateurs_en_jeu, inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Impossible d'obtenir le nombre d'utilisateurs Steam en ligne et en jeu.")

@slash_command(name="vacances_scolaires", description="Obtenir les dates des vacances scolaires dans l'académie de Versailles")
@slash_option(
    name="year",
    description="Choisissez une année pour les vacances scolaires",
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
        embed = discord.Embed(title=f"Vacances scolaires dans l'académie de Versailles ({year})", color=0x00ff00)
        for holiday in data["results"]:
            start_date = holiday["start_date"]
            end_date = holiday["end_date"]
            embed.add_field(name=holiday["description"], value=f"{start_date} - {end_date}", inline=False)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Impossible d'obtenir les vacances scolaires dans l'académie de Versailles.")

@slash_command(name="ville_infos", description="Obtenir des informations sur une ville")
@slash_option(
    name="postal_code",
    description="Entrez le code postal de la ville",
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
        embed = discord.Embed(title=f"Informations sur {city_name}", color=0x00ff00)
        embed.add_field(name="Code INSEE", value=insee_code, inline=False)
        embed.add_field(name="Département", value=department, inline=False)
        embed.add_field(name="Région", value=region, inline=False)
        embed.add_field(name="Population (en milliers)", value=population, inline=False)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Impossible d'obtenir des informations sur la ville.")

@slash_command(name="risques_naturels", description="Obtenir des informations sur les risques naturels dans une ville / territoire")
@slash_option(
    name="insee_code",
    description="Entrez le code INSEE de la ville / territoire",
    required=True,
    opt_type=OptionType.INTEGER
)
async def risques_naturels_function(ctx: SlashContext, insee_code: int):
    response = requests.get(f"https://www.georisques.gouv.fr/api/v1/gaspar/risques?code_insee={insee_code}&page=1&page_size=10&rayon=1000")
    if response.status_code == 200:
        data = response.json()
        if len(data["data"]) == 0:
            await ctx.send("Aucun risque naturel trouvé dans la ville / territoire.")
        else:
            embed = discord.Embed(title=f"Risques Naturels à {data['data'][0]['libelle_commune']}", color=0x00ff00)
            for risque in data["data"][0]["risques_detail"]:
                embed.add_field(name=risque["libelle_risque_long"], value=f"Numéro de risque: {risque['num_risque']}\nZone de sismicité: {risque['zone_sismicite']}", inline=False)
            await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Impossible d'obtenir des informations sur les risques naturels dans la ville / territoire.")

@slash_command(name="jours_feries", description="Obtenir les jours fériés en France")
@slash_option(
    name="year",
    description="Choisissez une année pour les jours fériés",
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
        embed = discord.Embed(title=f"Jours Fériés en {year}", description=holidays, color=0x00ff00)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Impossible d'obtenir les jours fériés pour l'année.")

@slash_command(name="ville_stations_essences", description="Obtenir les stations-service dans une ville")
@slash_option(
    name="code_postal",
    description="Entrez le code postal de la ville",
    required=True,
    opt_type=OptionType.INTEGER
)
async def ville_stations_essences_function(ctx: SlashContext, code_postal: int):
    response = requests.get(f"https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/records?where=cp%3D%22{code_postal}%22&limit=100")
    if response.status_code == 200:
        data = response.json()
        if data['total_count'] == 0:
            await ctx.send("La ville n'a pas de station-service...")
        else:
            embed = discord.Embed(title=f"Prix des carburants à {data['results'][0]['ville']}", color=0x00ff00)
            for record in data["results"]:
                carburants = ', '.join(record['carburants_disponibles']) if isinstance(record['carburants_disponibles'], list) else record['carburants_disponibles']
                services = ', '.join(record['services_service']) if isinstance(record['services_service'], list) else record['services_service']
                embed.add_field(name=record["adresse"], value=f"**Carburants disponibles:** {carburants}\n**24/24 Automate:** {record['horaires_automate_24_24']}\n**Services:** {services}", inline=False)
            await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Impossible d'obtenir les prix des carburants pour la ville.")

@slash_command(name="ville_musées_de_france", description="Obtenir les musées avec l'appellation Musée de France dans une ville")
@slash_option(
    name="code_postal",
    description="Entrez le code postal de la ville",
    required=True,
    opt_type=OptionType.INTEGER
)
async def ville_musees_de_france_function(ctx: SlashContext, code_postal: int):
    response = requests.get(f"https://data.culture.gouv.fr/api/explore/v2.1/catalog/datasets/musees-de-france-base-museofile/records?where=cp_m%3D%22{code_postal}%22&limit=100")
    if response.status_code == 200:
        data = response.json()
        if data['total_count'] == 0:
            await ctx.send(f"Aucun musée avec l'appellation Musée de France trouvé à {code_postal}...")
        else:
            embed = discord.Embed(title=f"Musées avec l'appellation Musée de France à {code_postal}", color=0x00ff00)
            for record in data["results"]:
                embed.add_field(name="Nom du musée", value=record.get("autnom", "inconnu"), inline=False)
                embed.add_field(name="Adresse du musée", value=record.get("adrl1_m", "inconnue"), inline=False)
                embed.add_field(name="Catégories", value=', '.join(record.get("categ", ["inconnue"])), inline=False)
                embed.add_field(name="DomPal", value=', '.join(record.get("dompal", ["inconnu"])), inline=False)
            await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Impossible d'obtenir les informations sur les musées pour la ville.")

@slash_command(name="gare_au_hasard", description="Obtenir une gare de train aléatoire en Île-de-France")
async def gare_au_hasard_function(ctx: SlashContext):
    if random.randint(0, 1) == 0:
        response = requests.get("https://data.iledefrance.fr/api/explore/v2.1/catalog/datasets/gares-et-stations-du-reseau-ferre-dile-de-france-donnee-generalisee/records?order_by=codeunique%20ASC&limit=100")
    else:
        response = requests.get("https://data.iledefrance.fr/api/explore/v2.1/catalog/datasets/gares-et-stations-du-reseau-ferre-dile-de-france-donnee-generalisee/records?order_by=codeunique%20DESC&limit=100")
    if response.status_code == 200:
        data = response.json()
        if data['total_count'] == 0:
            await ctx.send("Aucune gare de train trouvée en Île-de-France...")
        else:
            record = random.choice(data["results"])
            embed = discord.Embed(title=record.get("nom_long", "inconnu"), color=0x00ff00)
            embed.add_field(name="Ligne(s)", value=record.get("res_com"), inline=False)
            embed.add_field(name="Exploitant", value=record.get("exploitant"), inline=False)
            await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Impossible d'obtenir les informations sur les gares de train.")

@slash_command(name="gare_ligne", description="Obtenir les gares de train sur une ligne spécifique")
@slash_option(
    name="ligne",
    description="Choisir la ligne",
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
async def gare_ligne_function(ctx: SlashContext, ligne: str):
    response = requests.get(f"https://data.iledefrance.fr/api/explore/v2.1/catalog/datasets/gares-et-stations-du-reseau-ferre-dile-de-france-par-ligne/records?where=indice_lig=\"{ligne}\"&limit=100")
    if response.status_code == 200:
        data = response.json()
        if data['total_count'] == 0:
            await ctx.send(f"Aucune gare de train trouvée sur la ligne {ligne}...")
        else:
            embed = discord.Embed(title=f"Gares de train sur la ligne {ligne}", color=0x00ff00)
            station_count = len(data["results"])
            embed.add_field(name="Nombre de gares", value=station_count, inline=False)
            
            for i, record in enumerate(data["results"]):
                if i >= 5:
                    break
                embed.add_field(name=record.get("nom_gares", ["inconnu"]), value=record.get("exploitant", "inconnu"), inline=False)
            
            if station_count > 5:
                if ligne in ["A", "B", "C", "D", "E"]:
                    url = f"https://www.bonjour-ratp.fr/lignes-rer/ligne-{ligne.lower()}/"
                else:
                    url = f"https://www.bonjour-ratp.fr/lignes-transilien/ligne-{ligne.lower()}/"
                button = Button(
                    style=ButtonStyle.URL,
                    label="Voir plus",
                    url=url,
                )
                await ctx.send(embed=embed.to_dict(), components=[[button]])
            else:
                await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Impossible d'obtenir les informations sur les gares de train.")

@slash_command(name="tarifs_transports_idf", description="Obtenir les prix des transports en Ile-de-France")
async def tarifs_transports_IDF_function(ctx: SlashContext):
    response = requests.get("https://data.iledefrance.fr/api/explore/v2.1/catalog/datasets/description-et-tarif-des-titres-de-transport-en-ile-de-france/records?limit=100")
    if response.status_code == 200:
        data = response.json()
        if data['total_count'] == 0:
            await ctx.send("Aucun prix de transport trouvé en Ile-de-France...")
        else:
            embed1 = discord.Embed(title="Prix des transports en Ile-de-France (1/2)", color=0x00ff00)
            embed2 = discord.Embed(title="Prix des transports en Ile-de-France (2/2)", color=0x00ff00)
            count = 0
            for record in data["results"]:
                url = record.get("url", "inconnu")
                field_value = f"{record.get('short_description', 'inconnu')}\n[Acheter]({url})"
                if count < 25:
                    embed1.add_field(name=f"{record.get('product_name', 'inconnu')} - Prix : {record.get('price', 'inconnu')}", value=field_value, inline=False)
                else:
                    embed2.add_field(name=f"{record.get('product_name', 'inconnu')} - Prix : {record.get('price', 'inconnu')}", value=field_value, inline=False)
                count += 1
            await ctx.send(embed=embed1.to_dict())
            if count > 25:
                await ctx.send(embed=embed2.to_dict())
    else:
        await ctx.send("Impossible d'obtenir les informations sur les prix des transports.")

@slash_command(name="ville_amie_des_animaux",description="Vérifier si une ville est amie des animaux")
@slash_option(
    name="nom_ville",
    description="Entrez le nom de la ville",
    required=True,
    opt_type=OptionType.STRING
)
async def ville_amie_des_animaux(ctx: SlashContext, nom_ville: str):
    response = requests.get(f"https://data.iledefrance.fr/api/explore/v2.1/catalog/datasets/label-ville-amie-des-animaux/records?where=commune%3D%22{nom_ville}%22&order_by=annee&limit=20")
    if response.status_code == 200:
        data = response.json()
        if data['total_count'] == 0:
            await ctx.send(f"{nom_ville} n'est pas amie des animaux...")
        else:
            embed = discord.Embed(title=f"{nom_ville} - Amie des animaux", color=0x00ff00)
            for record in data["results"]:
                embed.add_field(name="Distinction", value=record.get("distinction", "inconnu"), inline=False)
                embed.add_field(name="Année", value=record.get("annee", "inconnu"), inline=False)
            await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Impossible d'obtenir des informations sur la ville.")

@slash_command(name="nombre_premier", description="Vérifier si un nombre est premier")
@slash_option(
    name="nombre",
    description="Entrez le nombre",
    required=True,
    opt_type=OptionType.INTEGER
)
async def nombre_premier_function(ctx: SlashContext, nombre: int):
    if nombre > 1:
        for i in range(2, nombre):
            if (nombre % i) == 0:
                await ctx.send(f"{nombre} n'est pas un nombre premier.")
                break
        else:
            await ctx.send(f"{nombre} est un nombre premier.")
    else:
        await ctx.send(f"{nombre} n'est pas un nombre premier.")

@slash_command(name="iss_location", description="Obtenir la position actuelle de l'ISS")
async def iss_location_function(ctx: SlashContext):
    response = requests.get("http://api.open-notify.org/iss-now.json")
    if response.status_code == 200:
        data = response.json()
        latitude = data.get("iss_position", {}).get("latitude")
        longitude = data.get("iss_position", {}).get("longitude")
        embed = discord.Embed(title="Position actuelle de l'ISS", description=f"**Latitude:** {latitude}\n**Longitude:** {longitude}")
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Impossible d'obtenir la position actuelle de l'ISS.")

@slash_command(name="personnes_dans_lespace", description="Obtenir le nombre de personnes dans l'espace")
async def personnes_dans_lespace_function(ctx: SlashContext):
    response = requests.get("http://api.open-notify.org/astros.json")
    if response.status_code == 200:
        data = response.json()
        number_of_people = data.get("number")
        people = data.get("people")
        people_in_space = "\n".join([f"**{person.get('name')}** - {person.get('craft')}" for person in people])
        embed = discord.Embed(title=f"Personnes dans l'espace ({number_of_people})", description=people_in_space)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Impossible d'obtenir le nombre de personnes dans l'espace.")

@slash_command(name="nombre_info", description="Obtenir des informations sur un nombre")
@slash_option(
    name="nombre",
    description="Entrez le nombre",
    required=True,
    opt_type=OptionType.INTEGER
)
async def nombre_info_function(ctx: SlashContext, nombre: int):
    response = requests.get(f"http://numbersapi.com/{nombre}")
    if response.status_code == 200:
        data = response.text
        embed = discord.Embed(title=f"Informations sur le nombre {nombre}", description=data)
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Impossible d'obtenir des informations sur le nombre.")

@slash_command(name="photo_astronomie_du_jour", description="Obtenir la photo d'astronomie du jour")
async def photo_astronomie_du_jour_function(ctx: SlashContext):
    response = requests.get("https://api.nasa.gov/planetary/apod?api_key=C2FgyOCHtCmeFVZR6D1J1idPsgjVPR9rhcayo1o5")
    if response.status_code == 200:
        data = response.json()
        explanation = data.get("explanation")
        # Translate explanation to French
        translation_response = requests.get(f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=fr&dt=t&q={explanation}")
        if translation_response.status_code == 200:
            translation_data = translation_response.json()
            french_explanation = translation_data[0][0][0]
        else:
            french_explanation = explanation
        embed = discord.Embed(title=data.get("title"), description=french_explanation)
        embed.set_image(url=data.get("url"))
        await ctx.send(embed=embed.to_dict())
    else:
        await ctx.send("Impossible d'obtenir la photo d'astronomie du jour.")

@slash_command(name="photo_mars", description="Obtenir une photo de Mars")
@slash_option(
    name="camera",
    description="Choisissez une caméra",
    required=True,
    opt_type=3,
    choices=[
        SlashCommandChoice(name="FHAZ", value="FHAZ"),
        SlashCommandChoice(name="RHAZ", value="RHAZ"),
        SlashCommandChoice(name="CHEMCAM", value="CHEMCAM"),
        SlashCommandChoice(name="MAHLI", value="MAHLI"),
        SlashCommandChoice(name="MARDI", value="MARDI"),
        SlashCommandChoice(name="NAVCAM", value="NAVCAM")
    ]
)
async def photo_mars_function(ctx: SlashContext, camera: str):
    response = requests.get(f"https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol=1000&camera={camera}&api_key=C2FgyOCHtCmeFVZR6D1J1idPsgjVPR9rhcayo1o5")
    if response.status_code == 200:
        data = response.json()
        if data['photos']:
            photo = random.choice(data["photos"])
            embed = discord.Embed(title=f"Photo de Mars avec la caméra {camera}", color=0x00ff00)
            embed.set_image(url=photo.get("img_src"))
            await ctx.send(embed=embed.to_dict())
        else:
            await ctx.send(f"Aucune photo de Mars trouvée avec la caméra {camera}...")
    else:
        await ctx.send("Impossible d'obtenir des photos de Mars.")



bot.start()
