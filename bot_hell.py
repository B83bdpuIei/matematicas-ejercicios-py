import discord
from discord.ext import commands
import os

# ==========================================
# 🔐 SEGURIDAD
# ==========================================
TOKEN = os.environ.get("DISCORD_TOKEN")

if not TOKEN:
    print("❌ ERROR: Falta la variable 'DISCORD_TOKEN'.")
    exit()

# ==========================================
# 🔥 CONFIGURACIÓN
# ==========================================
SUPPORT_TEXT = "! HELL WIPES FRIDAY 100€"
SUPPORT_ROLE_ID = 1336477737594130482
GIVEAWAY_CHANNEL_ID = 1449849645495746803

# ==========================================
# ⚙️ BOT SETUP
# ==========================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True
# IMPORTANTE: Necesario para ver cambios de perfil global a veces
intents.presences = True 

bot = commands.Bot(command_prefix='!', intents=intents)

# ==========================================
# 🚀 EVENTOS
# ==========================================

@bot.event
async def on_ready():
    print(f"🔥 SISTEMA HELL ONLINE")
    print(f"Rastreando Nombre Global: {SUPPORT_TEXT}")
    print("------------------------------------------------")

@bot.event
async def on_member_update(before, after):
    """
    Se activa cuando un miembro se actualiza.
    Ahora miramos after.global_name (Nombre General) en vez de display_name.
    """
    
    # 1. Obtenemos el nombre REAL (Global)
    # Si no tiene global_name (raro), usamos el name de usuario.
    name_check = after.global_name if after.global_name else after.name
    
    # Si por lo que sea falla, saltamos
    if not name_check:
        return

    guild = after.guild
    role = guild.get_role(SUPPORT_ROLE_ID)
    
    if not role:
        print(f"[ERROR] Rol {SUPPORT_ROLE_ID} no encontrado.")
        return

    # 2. Comprobamos si el texto está en su NOMBRE GLOBAL
    name_has_tag = SUPPORT_TEXT.lower() in name_check.lower()
    has_role = role in after.roles

    # Evitar spam en consola si no hay cambios relevantes
    # (Solo actuamos si el estado del rol no coincide con el estado del nombre)
    if name_has_tag == has_role:
        return

    # --- CASO A: TIENE EL NOMBRE GLOBAL -> DAR ROL ---
    if name_has_tag and not has_role:
        try:
            await after.add_roles(role)
            print(f"[+] ROL DADO a: {name_check} (Usuario: {after.name})")
        except discord.Forbidden:
            print(f"[!] ERROR PERMISOS: Sube el rol del Bot.")

    # --- CASO B: SE QUITÓ EL NOMBRE GLOBAL -> QUITAR ROL Y REACCIONES ---
    elif not name_has_tag and has_role:
        try:
            await after.remove_roles(role)
            print(f"[-] ROL QUITADO a: {name_check}")
            
            # Anti-Cheat: Borrar reacciones
            giveaway_channel = guild.get_channel(GIVEAWAY_CHANNEL_ID)
            if giveaway_channel:
                async for message in giveaway_channel.history(limit=20):
                    for reaction in message.reactions:
                        try:
                            await message.remove_reaction(reaction.emoji, after)
                            print(f"   [x] REACCIÓN BORRADA de sorteos")
                        except:
                            pass
        except discord.Forbidden:
            print(f"[!] PERMISOS: No puedo gestionar a este usuario.")

if __name__ == "__main__":
    bot.run(TOKEN)
