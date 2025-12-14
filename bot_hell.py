import discord
from discord.ext import commands
import os
import asyncio
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==========================================
# 🚑 FAKE WEB SERVER (Para Render)
# ==========================================
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"HELL SYSTEM ACTIVE")

def run_fake_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

# ==========================================
# 🔐 CONFIGURACIÓN
# ==========================================
TOKEN = os.environ.get("DISCORD_TOKEN")
SUPPORT_TEXT = "! HELL WIPES FRIDAY 100€"
SUPPORT_ROLE_ID = 1336477737594130482
GIVEAWAY_CHANNEL_ID = 1449849645495746803

# ==========================================
# ⚙️ SETUP
# ==========================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True
intents.presences = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Función para convertir tiempo (ej: 10s, 1m, 1h)
def convert_time(time_str):
    unit = time_str[-1]
    if unit not in ['s', 'm', 'h', 'd']:
        return -1
    try:
        val = int(time_str[:-1])
    except:
        return -2
        
    if unit == 's': return val
    if unit == 'm': return val * 60
    if unit == 'h': return val * 3600
    if unit == 'd': return val * 86400
    return 0

# ==========================================
# 🎁 COMANDO DE SORTEOS (NUEVO)
# ==========================================
@bot.command(name="gstart")
@commands.has_permissions(administrator=True)
async def gstart(ctx, duration: str, *, prize: str):
    """
    Uso: !gstart 10m 100€ PayPal
    Crea un sorteo que usa Reacciones, compatible con el Anti-Cheat.
    """
    # 1. Borramos el comando del admin para limpiar
    await ctx.message.delete()

    seconds = convert_time(duration)
    if seconds < 0:
        await ctx.send("❌ Error en el tiempo. Usa s/m/h/d (ej: 10m).", delete_after=5)
        return

    # 2. Crear el Embed del Sorteo
    embed = discord.Embed(
        title="🎉 **GIVEAWAY TIME** 🎉",
        description=f"Prize: **{prize}**\nTime: **{duration}**\n\nReact with 🎉 to enter!",
        color=0xff0000 # Color Rojo Hell
    )
    embed.set_footer(text="Anti-Cheat System Active: If you remove the tag, you are removed.")
    
    # 3. Enviar mensaje y poner reacción
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎉")

    # 4. Esperar el tiempo
    await asyncio.sleep(seconds)

    # 5. Elegir ganador
    new_msg = await ctx.channel.fetch_message(msg.id) # Refrescar mensaje
    users = []
    
    # Recoger usuarios válidos
    for reaction in new_msg.reactions:
        if str(reaction.emoji) == "🎉":
            async for user in reaction.users():
                if not user.bot:
                    users.append(user)
    
    if len(users) > 0:
        winner = random.choice(users)
        
        # Embed de victoria
        win_embed = discord.Embed(
            title="👑 **WE HAVE A WINNER** 👑",
            description=f"Congratulations {winner.mention}!\nYou won: **{prize}**",
            color=0x00ff00
        )
        await ctx.send(content=f"{winner.mention}", embed=win_embed)
        
        # Editar el sorteo original para decir que acabó
        embed.description += f"\n\n🏆 **Winner:** {winner.mention}"
        await msg.edit(embed=embed)
    else:
        await ctx.send("❌ No one entered the giveaway.")

# ==========================================
# 🚀 EVENTOS (ANTI-CHEAT)
# ==========================================
@bot.event
async def on_ready():
    print(f"🔥 SISTEMA HELL ONLINE - {bot.user}")
    print("------------------------------------------------")

@bot.event
async def on_member_update(before, after):
    name_check = after.global_name if after.global_name else after.name
    if not name_check: return

    guild = after.guild
    role = guild.get_role(SUPPORT_ROLE_ID)
    if not role: return

    name_has_tag = SUPPORT_TEXT.lower() in name_check.lower()
    has_role = role in after.roles

    if name_has_tag == has_role: return

    # --- DAR ROL ---
    if name_has_tag and not has_role:
        try:
            await after.add_roles(role)
            print(f"[+] ROL DADO: {name_check}")
        except: pass

    # --- QUITAR ROL Y BORRAR DEL SORTEO ---
    elif not name_has_tag and has_role:
        try:
            await after.remove_roles(role)
            print(f"[-] ROL QUITADO: {name_check}")
            
            # Buscamos en el canal de sorteos
            giveaway_channel = guild.get_channel(GIVEAWAY_CHANNEL_ID)
            if giveaway_channel:
                async for message in giveaway_channel.history(limit=20):
                    # Solo miramos mensajes del propio bot (los sorteos)
                    if message.author == bot.user:
                        for reaction in message.reactions:
                            if str(reaction.emoji) == "🎉":
                                try:
                                    await message.remove_reaction("🎉", after)
                                    print(f"   [x] SACADO DEL SORTEO: {name_check}")
                                except: pass
        except: pass

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
