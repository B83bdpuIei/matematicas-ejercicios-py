import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
import random
import threading
from datetime import datetime, timedelta
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

# --- IDs ---
SUPPORT_TEXT = "! HELL WIPES FRIDAY 100€"
SUPPORT_ROLE_ID = 1336477737594130482

GIVEAWAY_CHANNEL_ID = 1449849645495746803 
POLLS_CHANNEL_ID = 1449083865862770819      
CMD_CHANNEL_ID = 1449346777659609288

# --- LISTA DE COMANDOS (Menú Fijo) ---
COMMAND_LIST_TEXT = """
⚫ **!recipes** - Ver crafteos del server
"""

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
# 📊 COMANDO: /finish_polls (FORMATO COMPACTO)
# ==========================================
@bot.tree.command(name="finish_polls", description="Publica resultados del último lote de votaciones.")
async def finish_polls(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ No tienes permisos.", ephemeral=True)
        return

    await interaction.response.defer()

    polls_channel = bot.get_channel(POLLS_CHANNEL_ID)
    if not polls_channel:
        await interaction.followup.send("❌ Error: No encuentro el canal de votaciones.")
        return

    results_text = ""
    count = 0
    reference_date = None 
    
    async for message in polls_channel.history(limit=None):
        if not message.content or not message.reactions:
            continue 

        msg_date = message.created_at.date()

        if reference_date is None:
            reference_date = msg_date
        elif msg_date != reference_date:
            break 

        winner_reaction = max(message.reactions, key=lambda r: r.count)
        
        if winner_reaction.count > 1:
            # Limpieza básica del texto para que no quede raro
            question = message.content.strip()
            # Quitamos asteriscos extra si el usuario los puso manual, para ponerlos nosotros bien
            question_clean = question.replace("**", "")
            
            # Cortamos si es muy largo
            if len(question_clean) > 80:
                question_clean = question_clean[:80] + "..."

            # --- FORMATO "Buff Carcha : No y ya" ---
            # ⚫ **Pregunta**: Emoji (Votos)
            results_text += f"⚫ **{question_clean}**: {winner_reaction.emoji} ({winner_reaction.count})\n"
            count += 1

    if count == 0:
        await interaction.followup.send("⚠️ No encontré votaciones recientes.")
        return

    # --- Lógica de Paginación (Anti-Crash 4096) ---
    MAX_LENGTH = 4000 

    if len(results_text) <= MAX_LENGTH:
        embed = discord.Embed(
            title="👑 **POLL RESULTS / RESULTADOS**",
            description=f"**(Fecha: {reference_date})**\n\n{results_text}",
            color=0xff0000
        )
        embed.set_footer(text="Community Voice • Hell Legion")
        if bot.user.avatar:
            embed.set_thumbnail(url=bot.user.avatar.url)
        await interaction.followup.send(embed=embed)

    else:
        partes = [results_text[i:i+MAX_LENGTH] for i in range(0, len(results_text), MAX_LENGTH)]
        
        for i, parte in enumerate(partes):
            embed = discord.Embed(
                title=f"👑 **POLL RESULTS** (Parte {i+1}/{len(partes)})",
                description=f"**(Fecha: {reference_date})**\n\n{parte}",
                color=0xff0000
            )
            embed.set_footer(text="Community Voice • Hell Legion")
            if bot.user.avatar:
                embed.set_thumbnail(url=bot.user.avatar.url)
            
            await interaction.followup.send(embed=embed)

# ==========================================
# 🛡️ GESTOR DE MENSAJES (AUTO-DELETE + MENÚ)
# ==========================================
@bot.event
async def on_message(message):
    if message.channel.id == CMD_CHANNEL_ID:
        dont_delete = False
        if message.author == bot.user and message.embeds:
            embed = message.embeds[0]
            title = str(embed.title).upper()
            if "AVAILABLE COMMANDS" in title or "GIVEAWAY" in title:
                dont_delete = True
        
        if not dont_delete:
            try: await message.delete(delay=120) 
            except: pass 

    if message.author.bot: return
    await bot.process_commands(message)

# ==========================================
# 🎁 COMANDO: /start_giveaway
# ==========================================
@bot.tree.command(name="start_giveaway", description="Inicia un sorteo")
@app_commands.describe(tiempo="Duración (ej: 10m, 24h)", premio="Qué se sortea")
async def start_giveaway(interaction: discord.Interaction, tiempo: str, premio: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ No tienes permisos.", ephemeral=True)
        return

    seconds = convert_time(tiempo)
    if seconds <= 0:
        await interaction.response.send_message("❌ Tiempo inválido.", ephemeral=True)
        return

    es_canal_hell = (interaction.channel_id == GIVEAWAY_CHANNEL_ID)
    if es_canal_hell:
        color = 0xff0000
        titulo = "🔥 **HELL SPONSOR GIVEAWAY** 🔥"
        footer = "⚠️ ANTI-CHEAT ACTIVE: Remove name tag = Auto-Kick"
    else:
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

    try: msg = await interaction.channel.fetch_message(msg.id)
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
# 🚀 EVENTOS DE INICIO
# ==========================================
@bot.event
async def on_ready():
    print(f"🔥 SISTEMA HELL ONLINE - {bot.user}")
    print("🔄 Sincronizando comandos Slash...")
    await bot.tree.sync()
    
    cmd_channel = bot.get_channel(CMD_CHANNEL_ID)
    if cmd_channel:
        try:
            async for msg in cmd_channel.history(limit=20):
                if msg.author == bot.user and msg.embeds:
                    if "AVAILABLE COMMANDS" in (msg.embeds[0].title or ""):
                        await msg.delete()
            
            embed = discord.Embed(
                title="📜 **AVAILABLE COMMANDS / COMANDOS**",
                description=f"Use the commands below. Messages autodestruct in **2 minutes**.\n\n{COMMAND_LIST_TEXT}",
                color=0xffaa00 
            )
            embed.set_footer(text="⚠️ Auto-Cleaner Active: Chat stays clean.")
            if bot.user.avatar: embed.set_thumbnail(url=bot.user.avatar.url)
            
            await cmd_channel.send(embed=embed)
            print(f"✅ Menú actualizado en el canal {CMD_CHANNEL_ID}")
        except Exception as e:
            print(f"⚠️ Error actualizando menú: {e}")

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

    if name_has_tag and not has_role:
        try: await after.add_roles(role)
        except: pass
    elif not name_has_tag and has_role:
        try:
            await after.remove_roles(role)
            giveaway_channel = guild.get_channel(GIVEAWAY_CHANNEL_ID)
            if giveaway_channel:
                async for message in giveaway_channel.history(limit=20):
                    if message.author == bot.user and message.embeds:
                        embed = message.embeds[0]
                        if "ANTI-CHEAT" in (embed.footer.text or ""):
                            for reaction in message.reactions:
                                if str(reaction.emoji) == "🎉":
                                    try: await message.remove_reaction("🎉", after)
                                    except: pass
        except: pass

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
