import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
import random
import threading
import re
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==========================================
# 🚑 FAKE WEB SERVER
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

# --- TU FLECHA ---
HELL_ARROW = "<a:hell_arrow:1211049707128750080>" 

COMMAND_LIST_TEXT = f"""
{HELL_ARROW} **!recipes** - Ver crafteos del server
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
# 🧠 LÓGICA INTELIGENTE (FIXED)
# ==========================================
def parse_poll_result(content, winner_emoji):
    if not content: return None, None

    lines = content.split('\n')
    question = "Encuesta"
    winning_text = "Opción Seleccionada"
    found_option = False

    # 1. BUSCAR PREGUNTA (Filtro mejorado)
    for line in lines:
        # Quitamos basura markdown PRIMERO
        clean_check = line.replace(">", "").replace("*", "").replace("_", "").replace("-", "").strip()
        
        # Si después de limpiar no queda casi nada (menos de 2 letras), es una línea separadora
        if len(clean_check) < 2: 
            continue
        
        # Si llegamos aquí, es texto real -> Es la pregunta
        question = line.replace(">", "").replace("*", "").replace("__", "").strip()
        break
    
    # 2. BUSCAR RESPUESTA
    emoji_str = str(winner_emoji)
    
    for line in lines:
        if emoji_str in line:
            # Quitamos el emoji, los > y las negritas para dejar solo el texto
            clean_option = line.replace(emoji_str, "").replace(">", "").replace("*", "").replace("_", "").strip()
            # Limpieza final de guiones o dos puntos al inicio
            clean_option = clean_option.lstrip(" :-").strip()
            
            if clean_option:
                winning_text = clean_option
                found_option = True
                break
    
    # Si no encontramos texto al lado del emoji, usamos el emoji mismo
    if not found_option:
        winning_text = str(winner_emoji)

    # Cortar si es muy largo
    if len(question) > 60: question = question[:57] + "..."
    if len(winning_text) > 50: winning_text = winning_text[:47] + "..."

    return question, winning_text

# ==========================================
# 📊 COMANDO: /finish_polls
# ==========================================
@bot.tree.command(name="finish_polls", description="Publica resultados limpios.")
async def finish_polls(interaction: discord.Interaction):
    # Anti-Crash 404
    try:
        await interaction.response.defer()
    except:
        return 

    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("❌ No tienes permisos.", ephemeral=True)
        return

    polls_channel = bot.get_channel(POLLS_CHANNEL_ID)
    if not polls_channel:
        await interaction.followup.send("❌ Error: No encuentro el canal.", ephemeral=True)
        return

    results_text = ""
    count = 0
    reference_date = None 
    
    async for message in polls_channel.history(limit=50):
        if not message.content or not message.reactions: continue 
        
        # Comprobación extra: Si al quitar guiones no queda nada, ignoramos el mensaje entero
        check_msg = message.content.replace("-", "").replace("_", "").strip()
        if not check_msg: continue

        msg_date = message.created_at.date()
        if reference_date is None: reference_date = msg_date
        elif msg_date != reference_date: break 

        winner_reaction = max(message.reactions, key=lambda r: r.count)
        
        if winner_reaction.count > 1:
            question, answer_text = parse_poll_result(message.content, winner_reaction.emoji)
            if not question: continue

            # --- FORMATO FINAL ---
            # Flecha Pregunta : Respuesta
            # SIN NÚMEROS DE VOTOS
            results_text += f"{HELL_ARROW} **{question}** : {answer_text}\n"
            count += 1

    if count == 0:
        await interaction.followup.send("⚠️ No encontré resultados recientes.", ephemeral=True)
        return

    # --- ENVIAR ---
    MAX_LENGTH = 3500 
    header = f"📢 **POLL RESULTS**\n📅 {reference_date}\n\n"
    full_content = header + results_text

    if len(full_content) <= MAX_LENGTH:
        embed = discord.Embed(description=full_content, color=0x990000)
        embed.set_footer(text="Hell Legion System")
        if bot.user.avatar: embed.set_thumbnail(url=bot.user.avatar.url)
        await interaction.followup.send(embed=embed)
    else:
        partes = [full_content[i:i+MAX_LENGTH] for i in range(0, len(full_content), MAX_LENGTH)]
        for i, parte in enumerate(partes):
            embed = discord.Embed(description=parte, color=0x990000)
            embed.set_footer(text=f"Page {i+1} • Hell Legion System")
            await interaction.followup.send(embed=embed)

# ==========================================
# 🛡️ GESTOR DE MENSAJES 
# ==========================================
@bot.event
async def on_message(message):
    if message.channel.id == CMD_CHANNEL_ID:
        dont_delete = False
        if message.author == bot.user and message.embeds:
            title = str(message.embeds[0].title).upper()
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
# 🚀 STARTUP
# ==========================================
@bot.event
async def on_ready():
    print(f"🔥 HELL SYSTEM ONLINE - {bot.user}")
    try: await bot.tree.sync()
    except: pass
    
    cmd_channel = bot.get_channel(CMD_CHANNEL_ID)
    if cmd_channel:
        try:
            last_msg = None
            async for msg in cmd_channel.history(limit=1): last_msg = msg
            
            menu_ok = False
            if last_msg and last_msg.author == bot.user and last_msg.embeds:
                if "AVAILABLE COMMANDS" in (last_msg.embeds[0].title or ""): menu_ok = True
            
            if not menu_ok:
                async for msg in cmd_channel.history(limit=10):
                    if msg.author == bot.user and msg.embeds:
                        if "AVAILABLE COMMANDS" in (msg.embeds[0].title or ""): await msg.delete()
                
                embed = discord.Embed(
                    title="📜 **AVAILABLE COMMANDS / COMANDOS**",
                    description=f"Use the commands below. Messages autodestruct in **2 minutes**.\n\n{COMMAND_LIST_TEXT}",
                    color=0xffaa00 
                )
                embed.set_footer(text="⚠️ Auto-Cleaner Active")
                if bot.user.avatar: embed.set_thumbnail(url=bot.user.avatar.url)
                await cmd_channel.send(embed=embed)
        except: pass

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
            # Check anti-cheat
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
