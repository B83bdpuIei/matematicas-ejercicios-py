import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
import random
import threading
import re # Necesario para buscar los emojis en el texto
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

# --- LISTA DE COMANDOS ---
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

# --- FUNCIÓN MÁGICA PARA ARREGLAR EMOJIS ---
def fix_content_visuals(text, bot_instance):
    """
    1. Busca patrones :nombre: y los reemplaza por el emoji real si el bot lo tiene.
    2. Limpia asteriscos y guiones bajos extra.
    """
    # Paso 1: Reemplazar nombres de emojis por sus IDs reales
    # Busca palabras entre dos puntos, ej: :hell_arrow:
    emoji_pattern = re.compile(r':([a-zA-Z0-9_]+):')
    
    def replace_emoji(match):
        emoji_name = match.group(1)
        # Busca el emoji en la caché del bot
        emoji = discord.utils.get(bot_instance.emojis, name=emoji_name)
        if emoji:
            return str(emoji) # Devuelve <a:nombre:ID>
        return match.group(0) # Si no existe, deja el texto original
    
    text = emoji_pattern.sub(replace_emoji, text)
    
    # Paso 2: Limpieza estética
    # Quitar negritas excesivas o guiones bajos de Markdown
    text = text.replace("**", "").replace("__", "").replace("⚫", "").strip()
    
    return text

# ==========================================
# 📊 COMANDO: /finish_polls
# ==========================================
@bot.tree.command(name="finish_polls", description="Publica resultados del último lote de votaciones.")
async def finish_polls(interaction: discord.Interaction):
    # 1. DEFER INMEDIATO: Lo primero que hace el bot para evitar el Error 404
    await interaction.response.defer()

    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("❌ No tienes permisos.", ephemeral=True)
        return

    polls_channel = bot.get_channel(POLLS_CHANNEL_ID)
    if not polls_channel:
        await interaction.followup.send("❌ Error: No encuentro el canal de votaciones.")
        return

    results_text = ""
    count = 0
    reference_date = None 
    
    # Recorremos el historial
    async for message in polls_channel.history(limit=50): # Limitado a 50 para que sea rápido
        if not message.content or not message.reactions:
            continue 

        # FILTRO DE BASURA: Si el mensaje es solo líneas separadoras, lo ignoramos
        if "____" in message.content or "----" in message.content:
            continue

        msg_date = message.created_at.date()

        if reference_date is None:
            reference_date = msg_date
        elif msg_date != reference_date:
            break # Paramos si cambiamos de día (lote anterior)

        # Calculamos ganador
        winner_reaction = max(message.reactions, key=lambda r: r.count)
        
        # Filtro: Solo mostrar si tiene más de 1 voto (evitar spam vacío)
        if winner_reaction.count > 1:
            # LIMPIEZA AUTOMÁTICA
            question_clean = fix_content_visuals(message.content, bot)
            
            # Si después de limpiar queda vacío o muy corto, lo saltamos
            if len(question_clean) < 3:
                continue

            # Cortamos si es gigante
            if len(question_clean) > 60:
                question_clean = question_clean[:60] + "..."

            # Formato final solicitado: ⚫ Pregunta : Ganador (Votos)
            # winner_reaction.emoji ya es el objeto emoji correcto si es una reacción
            results_text += f"⚫ **{question_clean}** : {winner_reaction.emoji} ({winner_reaction.count})\n\n"
            count += 1

    if count == 0:
        await interaction.followup.send("⚠️ No encontré votaciones válidas recientes.")
        return

    # --- ENVIAR RESULTADOS (Con protección anti-crash) ---
    MAX_LENGTH = 4000 

    # Si es corto, un solo mensaje
    if len(results_text) <= MAX_LENGTH:
        embed = discord.Embed(
            title="👑 **POLL RESULTS**", # Título limpio
            description=results_text,
            color=0xff0000
        )
        embed.set_footer(text=f"Community Voice • {reference_date}")
        if bot.user.avatar:
            embed.set_thumbnail(url=bot.user.avatar.url)
        await interaction.followup.send(embed=embed)

    # Si es largo, paginamos
    else:
        partes = [results_text[i:i+MAX_LENGTH] for i in range(0, len(results_text), MAX_LENGTH)]
        
        for i, parte in enumerate(partes):
            embed = discord.Embed(
                title=f"👑 **POLL RESULTS** ({i+1}/{len(partes)})",
                description=parte,
                color=0xff0000
            )
            embed.set_footer(text=f"Community Voice • {reference_date}")
            if bot.user.avatar:
                embed.set_thumbnail(url=bot.user.avatar.url)
            
            await interaction.followup.send(embed=embed)

# ==========================================
# 🛡️ GESTOR DE MENSAJES 
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
    try:
        await bot.tree.sync()
        print("✅ Comandos Sincronizados")
    except Exception as e:
        print(f"❌ Error sync: {e}")
    
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
        except Exception as e:
            print(f"⚠️ Error actualizando menú: {e}")

    # Escáner de roles inicial
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
