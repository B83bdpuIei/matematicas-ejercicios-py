import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
import random
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==========================================
# 🚑 FAKE WEB SERVER (Keep-Alive)
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

# --- MENU TEXT ---
COMMAND_LIST_TEXT = """
🔸 **!recipes** - Ver crafteos del server
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
# 🧹 LIMPIEZA DE ENCUESTAS (LÓGICA MEJORADA)
# ==========================================
def extract_poll_data(content):
    """
    Analiza el mensaje como en tus fotos:
    1. Busca la línea del título (ignora separadores ---).
    2. Limpia símbolos como '>' o '**'.
    """
    if not content: return None
    
    lines = content.split('\n')
    question = "Encuesta"
    
    for line in lines:
        clean = line.strip()
        # Ignorar líneas vacías o separadores (----)
        if not clean or set(clean) <= {'-', '_', ' ', '*'}: 
            continue
        
        # Esta es la línea del título
        question = clean
        break
    
    # Limpieza estética para que quede pro
    # Quitamos el '>' que usan en otros servers, y las negritas
    question = question.replace(">", "").replace("**", "").replace("__", "").replace(":", "").strip()
    
    if len(question) > 60:
        question = question[:57] + "..."
        
    return question

# ==========================================
# 📊 COMANDO: /finish_polls
# ==========================================
@bot.tree.command(name="finish_polls", description="Publica resultados de las votaciones.")
async def finish_polls(interaction: discord.Interaction):
    # --- SILENCIADOR DE ERRORES 404 ---
    try:
        await interaction.response.defer()
    except Exception:
        # Si el bot estaba dormido y falla la conexión, no hacemos NADA (silencio).
        # El usuario tendrá que darle otra vez, pero no spameamos la terminal.
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
    
    # Leemos historial
    async for message in polls_channel.history(limit=50):
        if not message.content or not message.reactions:
            continue 

        # Ignorar mensajes que sean puras líneas
        if set(message.content.strip()) <= {'-', '_'}:
            continue

        msg_date = message.created_at.date()
        if reference_date is None:
            reference_date = msg_date
        elif msg_date != reference_date:
            break 

        # Ganador
        winner_reaction = max(message.reactions, key=lambda r: r.count)
        
        if winner_reaction.count > 1:
            question = extract_poll_data(message.content)
            if not question: continue

            # --- NUEVO DISEÑO ---
            # Usamos '🔸' para temática Hell, diferente al '>' de los otros.
            # Formato: 🔸 Pregunta ➔ Emoji (Votos)
            results_text += f"🔸 **{question}** ➔ {winner_reaction.emoji} **({winner_reaction.count})**\n"
            count += 1

    if count == 0:
        await interaction.followup.send("⚠️ No encontré resultados recientes.", ephemeral=True)
        return

    # --- ENVIAR (Paginado) ---
    MAX_LENGTH = 3500 # Un poco menos para asegurar
    
    header_text = f"📢 **POLL RESULTS**\n📅 Date: {reference_date}\n" + "➖"*15 + "\n\n"

    # Si cabe en uno solo
    if len(header_text + results_text) <= MAX_LENGTH:
        embed = discord.Embed(
            description=header_text + results_text,
            color=0xff4400 # Naranja rojizo (Hell theme)
        )
        embed.set_footer(text="Community Voice • Hell Legion")
        if bot.user.avatar: embed.set_thumbnail(url=bot.user.avatar.url)
        await interaction.followup.send(embed=embed)
    else:
        # Si es muy largo, dividimos
        full_text = header_text + results_text
        partes = [full_text[i:i+MAX_LENGTH] for i in range(0, len(full_text), MAX_LENGTH)]
        
        for i, parte in enumerate(partes):
            embed = discord.Embed(
                description=parte,
                color=0xff4400
            )
            embed.set_footer(text=f"Page {i+1}/{len(partes)} • Hell Legion")
            await interaction.followup.send(embed=embed)

# Manejador de error específico para este comando
@finish_polls.error
async def finish_polls_error(interaction: discord.Interaction, error):
    # Esto captura el error si falla ANTES de ejecutar el código
    pass

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
# 🚀 STARTUP & MENÚ
# ==========================================
@bot.event
async def on_ready():
    print(f"🔥 HELL SYSTEM ONLINE - {bot.user}")
    try:
        await bot.tree.sync()
        print("✅ Comandos listos")
    except Exception as e:
        print(f"❌ Error sync: {e}")
    
    # --- MENÚ PERMANENTE ---
    cmd_channel = bot.get_channel(CMD_CHANNEL_ID)
    if cmd_channel:
        try:
            # Comprobar si ya existe el menú correcto al final del chat
            last_msg = None
            async for msg in cmd_channel.history(limit=1):
                last_msg = msg
            
            menu_ok = False
            if last_msg and last_msg.author == bot.user and last_msg.embeds:
                if "AVAILABLE COMMANDS" in (last_msg.embeds[0].title or ""):
                    menu_ok = True
            
            if not menu_ok:
                print("🔄 Actualizando menú...")
                async for msg in cmd_channel.history(limit=10):
                    if msg.author == bot.user and msg.embeds:
                        if "AVAILABLE COMMANDS" in (msg.embeds[0].title or ""):
                            await msg.delete()
                
                embed = discord.Embed(
                    title="📜 **AVAILABLE COMMANDS / COMANDOS**",
                    description=f"Use the commands below. Messages autodestruct in **2 minutes**.\n\n{COMMAND_LIST_TEXT}",
                    color=0xffaa00 
                )
                embed.set_footer(text="⚠️ Auto-Cleaner Active")
                if bot.user.avatar: embed.set_thumbnail(url=bot.user.avatar.url)
                await cmd_channel.send(embed=embed)
            else:
                print("✅ Menú correcto, no se toca.")

        except Exception as e:
            print(f"⚠️ Error menú: {e}")

    # Escáner de roles
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
            # Anti-cheat giveaway check
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
