import discord
from discord import app_commands
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
GIVEAWAY_CHANNEL_ID = 1449849645495746803  # CANAL HELL

# ==========================================
# ⚙️ SETUP DEL BOT
# ==========================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True
intents.presences = True

bot = commands.Bot(command_prefix='!', intents=intents)

def convert_time(time_str):
    unit = time_str[-1].lower()
    if unit not in ['s', 'm', 'h', 'd']: return -1
    try: val = int(time_str[:-1])
    except: return -2
    if unit == 's': return val
    if unit == 'm': return val * 60
    if unit == 'h': return val * 3600
    if unit == 'd': return val * 86400
    return 0

# ==========================================
# 🎁 COMANDO SLASH: /start_giveaway
# ==========================================
@bot.tree.command(name="start_giveaway", description="Inicia un sorteo (Modo Hell automático según el canal)")
@app_commands.describe(tiempo="Duración (ej: 10m, 24h)", premio="Qué se sortea")
async def start_giveaway(interaction: discord.Interaction, tiempo: str, premio: str):
    
    # 1. Permisos de Admin
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ No tienes permisos.", ephemeral=True)
        return

    seconds = convert_time(tiempo)
    if seconds <= 0:
        await interaction.response.send_message("❌ Tiempo inválido. Usa formato: 10s, 30m, 24h", ephemeral=True)
        return

    # 2. Detectar si es el Canal HELL
    es_canal_hell = (interaction.channel_id == GIVEAWAY_CHANNEL_ID)

    if es_canal_hell:
        # --- MODO HELL (ROJO + ANTI-CHEAT) ---
        color = 0xff0000
        titulo = "🔥 **HELL SPONSOR GIVEAWAY** 🔥"
        footer = "⚠️ ANTI-CHEAT ACTIVE: Remove name tag = Auto-Kick"
    else:
        # --- MODO NORMAL (VERDE + CHILL) ---
        color = 0x00ff00
        titulo = "🎉 **GIVEAWAY** 🎉"
        footer = "Good luck to everyone!"

    embed = discord.Embed(
        title=titulo,
        description=f"Prize: **{premio}**\nTime: **{tiempo}**\n\nReact with 🎉 to enter!",
        color=color
    )
    embed.set_footer(text=footer)

    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    await msg.add_reaction("🎉")

    await asyncio.sleep(seconds)

    # --- FINAL DEL SORTEO ---
    try:
        msg = await interaction.channel.fetch_message(msg.id)
    except: return

    users = []
    for reaction in msg.reactions:
        if str(reaction.emoji) == "🎉":
            async for user in reaction.users():
                if not user.bot: users.append(user)
    
    if users:
        winner = random.choice(users)
        await interaction.channel.send(f"👑 **WINNER:** {winner.mention} won **{premio}**!")
        
        embed.description += f"\n\n🏆 **Winner:** {winner.mention}"
        embed.color = 0xffd700
        await msg.edit(embed=embed)
    else:
        await interaction.channel.send("❌ No participants.")

# ==========================================
# 🚀 EVENTOS + ANTI-CHEAT
# ==========================================

@bot.event
async def on_ready():
    print(f"🔥 SISTEMA HELL ONLINE - {bot.user}")
    print("🔄 Sincronizando comandos Slash...")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Se han sincronizado {len(synced)} comandos Slash.")
    except Exception as e:
        print(f"❌ Error sincronizando: {e}")
    
    # Escáner inicial
    for guild in bot.guilds:
        role = guild.get_role(SUPPORT_ROLE_ID)
        if role:
            for member in guild.members:
                name_check = member.global_name if member.global_name else member.name
                if name_check and SUPPORT_TEXT.lower() in name_check.lower():
                    if role not in member.roles:
                        try: await member.add_roles(role)
                        except: pass

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
        try: await after.add_roles(role)
        except: pass

    # --- QUITAR ROL Y REVISAR SORTEOS (ANTI-CHEAT) ---
    elif not name_has_tag and has_role:
        try:
            await after.remove_roles(role)
            print(f"[-] ROL QUITADO: {name_check}")
            
            # Anti-Cheat selectivo (Solo Canal Hell)
            giveaway_channel = guild.get_channel(GIVEAWAY_CHANNEL_ID)
            if giveaway_channel:
                async for message in giveaway_channel.history(limit=20):
                    if message.author == bot.user and message.embeds:
                        embed = message.embeds[0]
                        if "ANTI-CHEAT" in (embed.footer.text or ""):
                            for reaction in message.reactions:
                                if str(reaction.emoji) == "🎉":
                                    try:
                                        await message.remove_reaction("🎉", after)
                                        print(f"   [x] KICKED FROM GIVEAWAY: {name_check}")
                                    except: pass
        except: pass

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
