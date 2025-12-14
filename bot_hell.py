import discord
from discord.ext import commands
import os

# ==========================================
# 🔐 SEGURIDAD: VARIABLES DE ENTORNO
# ==========================================
# AHORA BUSCA LA VARIABLE CORRECTA: "DISCORD_TOKEN"
TOKEN = os.environ.get("DISCORD_TOKEN")

if not TOKEN:
    print("❌ ERROR: No encuentro la variable 'DISCORD_TOKEN' en el entorno.")
    exit()

# ==========================================
# 🔥 CONFIGURACIÓN DE HELL
# ==========================================
SUPPORT_TEXT = "! HELL WIPES FRIDAY 100€"
SUPPORT_ROLE_ID = 1336477737594130482
GIVEAWAY_CHANNEL_ID = 1449849645495746803

# ==========================================
# ⚙️ PREPARACIÓN DEL BOT
# ==========================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ==========================================
# 🚀 EVENTOS
# ==========================================

@bot.event
async def on_ready():
    print(f"🔥 SISTEMA HELL ONLINE")
    print(f"Conectado como: {bot.user}")
    print(f"Rastreando: {SUPPORT_TEXT}")
    print("------------------------------------------------")

@bot.event
async def on_member_update(before, after):
    if before.display_name == after.display_name:
        return

    guild = after.guild
    role = guild.get_role(SUPPORT_ROLE_ID)
    
    if not role:
        print(f"[ERROR] Rol {SUPPORT_ROLE_ID} no encontrado.")
        return

    name_has_tag = SUPPORT_TEXT.lower() in after.display_name.lower()
    has_role = role in after.roles

    # --- CASO A: PONE EL NOMBRE ---
    if name_has_tag and not has_role:
        try:
            await after.add_roles(role)
            print(f"[+] ROL DADO a: {after.display_name}")
        except discord.Forbidden:
            print(f"[!] ERROR PERMISOS: Sube el rol del Bot.")

    # --- CASO B: QUITA EL NOMBRE (Anti-Cheat) ---
    elif not name_has_tag and has_role:
        try:
            await after.remove_roles(role)
            print(f"[-] ROL QUITADO a: {after.display_name}")
            
            giveaway_channel = guild.get_channel(GIVEAWAY_CHANNEL_ID)
            if giveaway_channel:
                async for message in giveaway_channel.history(limit=20):
                    for reaction in message.reactions:
                        try:
                            await message.remove_reaction(reaction.emoji, after)
                            print(f"   [x] REACCIÓN BORRADA de {after.display_name}")
                        except:
                            pass
            else:
                print(f"[!] ERROR: Canal sorteos no encontrado.")

        except discord.Forbidden:
            print(f"[!] PERMISOS: No puedo gestionar a {after.display_name}.")

if __name__ == "__main__":
    bot.run(TOKEN)
