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

# --- IDs DE CANALES ---
GIVEAWAY_CHANNEL_ID = 1449849645495746803 
POLLS_CHANNEL_ID = 1449083865862770819      
CMD_CHANNEL_ID = 1449346777659609288
ROLES_CHANNEL_ID = 1449083960578670614
SUGGEST_CHANNEL_ID = 1449346646465839134 

# --- IDs DE ROLES (AUTO-ROLES) ---
ROLES_CONFIG = {
    "Ping": 1199101577127014541,
    "Wipes": 1210709945339875328,
    "News": 1210710127871787050,
    "Rollbacks": 1210710910499299349,
    "Events": 1326887310331220028,
    "Giveaways": 1326887498856661053,
    "Announcements": 1326887647406329918,
    "Polls": 1326887768923701300,
    "Ban / Warns": 1326887925547274250,
    "Patchs": 1326888505216864361
}

# --- ESTÉTICA & EMOJIS ---
HELL_ARROW = "<a:hell_arrow:1211049707128750080>" 
NOTIFICATION_ICON = "<a:notification:1275469575638614097>"

# TUS NUEVOS EMOJIS DE SUGERENCIAS
CHECK_ICON = "<a:Check_hell:1450255850508779621>" 
CROSS_ICON = "<a:cruz_hell:1450255934273355918>" 

SUPPORT_TEXT = "! HELL WIPES FRIDAY 100€"
SUPPORT_ROLE_ID = 1336477737594130482

COMMAND_LIST_TEXT = f"""
{HELL_ARROW} **!recipes** - Ver crafteos del server
"""

# VARIABLE GLOBAL PARA CONTAR SUGERENCIAS
suggestion_count = 0

# ==========================================
# ⚙️ SETUP DEL BOT
# ==========================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True
intents.presences = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ==========================================
# 🔘 CLASE DE BOTONES (AUTO-ROLES)
# ==========================================
class RoleButton(discord.ui.Button):
    def __init__(self, label, role_id):
        super().__init__(
            label=label, 
            style=discord.ButtonStyle.secondary, 
            custom_id=f"role_{role_id}"
        )
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            await interaction.response.send_message("❌ Error: Role not found.", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"➖ Removed **{role.name}** role.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"➕ Added **{role.name}** role.", ephemeral=True)

class RolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for label, role_id in ROLES_CONFIG.items():
            self.add_item(RoleButton(label, role_id))

# ==========================================
# 📊 FUNCIONES AUXILIARES
# ==========================================
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

def parse_poll_result(content, winner_emoji):
    if not content: return None, None
    lines = content.split('\n')
    question = None
    winning_text = "Opción Seleccionada"
    found_option = False

    for line in lines:
        if "1211049707128750080" in line or "hell_arrow" in line:
            temp_q = re.sub(r'<a?:hell_arrow:[0-9]+>', '', line)
            temp_q = temp_q.replace(":hell_arrow:", "")
            question = temp_q.replace("**", "").replace("__", "").strip()
            break
    
    if not question:
        for line in lines:
            clean = line.strip()
            if "---" in clean or "___" in clean: continue
            if len(clean) < 3: continue
            question = clean.replace("**", "").replace("__", "").replace(">", "").strip()
            break
            
    if not question: question = "Encuesta"

    emoji_str = str(winner_emoji)
    for line in lines:
        if emoji_str in line:
            clean_option = line.replace(emoji_str, "").strip()
            clean_option = clean_option.lstrip(" :->").strip()
            clean_option = re.sub(r'\([0-9]+\)$', '', clean_option).strip()
            if clean_option:
                winning_text = clean_option
                found_option = True
                break
    
    if not found_option: winning_text = str(winner_emoji)
    if len(question) > 60: question = question[:57] + "..."
    if len(winning_text) > 50: winning_text = winning_text[:47] + "..."

    return question, winning_text

# ==========================================
# ⚡ COMANDOS SLASH
# ==========================================
@bot.tree.command(name="finish_polls", description="Publica resultados limpios.")
async def finish_polls(interaction: discord.Interaction):
    try: await interaction.response.defer()
    except: return 

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
        if "----" in message.content and len(message.content) < 30: continue

        msg_date = message.created_at.date()
        if reference_date is None: reference_date = msg_date
        elif msg_date != reference_date: break 

        winner_reaction = max(message.reactions, key=lambda r: r.count)
        
        if winner_reaction.count > 1:
            question, answer_text = parse_poll_result(message.content, winner_reaction.emoji)
            results_text += f"{HELL_ARROW} **{question}** : {answer_text}\n"
            count += 1

    if count == 0:
        await interaction.followup.send("⚠️ No encontré resultados.", ephemeral=True)
        return

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
    embed = discord.Embed(title=titulo, description=f"Prize: **{premio}**\nTime: **{tiempo}**\n\nReact with 🎉 to enter!", color=color)
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
            async for user in reaction.users() :
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
# 🛡️ GESTOR DE MENSAJES (SUGERENCIAS MEJORADO)
# ==========================================
@bot.event
async def on_message(message):
    if message.author.bot: return

    # --- LÓGICA DE SUGERENCIAS ---
    if message.channel.id == SUGGEST_CHANNEL_ID:
        
        # BORRAR SI NO ES COMANDO
        if not message.content.startswith(".suggest"):
            try: await message.delete()
            except: pass
            return
        
        # PROCESAR SUGERENCIA
        try: await message.delete()
        except: pass
        
        suggestion_content = message.content[8:].strip()
        if not suggestion_content: return 

        # Crear Embed Bonito
        embed = discord.Embed(description=f"**{suggestion_content}**", color=0xffaa00)
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.set_footer(text="Hell Legion System • Suggestions")
        
        sent_msg = await message.channel.send(embed=embed)
        try:
            await sent_msg.add_reaction(CHECK_ICON)
            await sent_msg.add_reaction(CROSS_ICON)
        except Exception as e:
            print(f"Error reacciones: {e}")

        # RECORDATORIO BONITO (Cada 10)
        global suggestion_count
        suggestion_count += 1
        
        if suggestion_count % 10 == 0:
            # Creamos un embed para el tip también
            tip_embed = discord.Embed(
                description=(
                    f"💡 **HOW TO SUGGEST**\n"
                    f"{HELL_ARROW} Use: `.suggest <your text>`\n"
                    f"{HELL_ARROW} Example: `.suggest Add more turrets`\n\n"
                    "*Everything else is auto-deleted.*"
                ),
                color=0x2b2d31 # Color oscuro "discreto"
            )
            if bot.user.avatar: tip_embed.set_thumbnail(url=bot.user.avatar.url)
            
            await message.channel.send(embed=tip_embed)

        return 

    # --- LIMPIEZA COMANDOS ---
    if message.channel.id == CMD_CHANNEL_ID:
        dont_delete = False
        if message.author == bot.user and message.embeds:
            title = str(message.embeds[0].title).upper()
            if "AVAILABLE COMMANDS" in title or "GIVEAWAY" in title:
                dont_delete = True
        if not dont_delete:
            try: await message.delete(delay=120) 
            except: pass 

    await bot.process_commands(message)

# ==========================================
# 🚀 STARTUP & LÓGICA AUTOMÁTICA
# ==========================================
@bot.event
async def on_ready():
    print(f"🔥 HELL SYSTEM ONLINE - {bot.user}")
    
    bot.add_view(RolesView())
    try: await bot.tree.sync()
    except: pass
    
    # 1. MENÚ DE COMANDOS
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

    # 2. MENÚ DE ROLES
    roles_channel = bot.get_channel(ROLES_CHANNEL_ID)
    if roles_channel:
        try:
            last_role_msg = None
            async for msg in roles_channel.history(limit=1): last_role_msg = msg
            roles_ok = False
            if last_role_msg and last_role_msg.author == bot.user and last_role_msg.embeds:
                if "NOTIFICATIONS & ACCESS" in (last_role_msg.embeds[0].title or ""): roles_ok = True
            
            if not roles_ok:
                async for msg in roles_channel.history(limit=10):
                    if msg.author == bot.user: await msg.delete()

                embed = discord.Embed(
                    title=f"{NOTIFICATION_ICON} **NOTIFICATIONS & ACCESS**",
                    description=(
                        f"{HELL_ARROW} Click the buttons below to toggle your roles.\n"
                        f"{HELL_ARROW} Select the channels you want to see.\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━"
                    ),
                    color=0x990000 
                )
                embed.set_footer(text="Hell Legion System • Auto-Roles")
                if bot.user.avatar: embed.set_thumbnail(url=bot.user.avatar.url)
                await roles_channel.send(embed=embed, view=RolesView())
        except Exception as e:
            print(f"⚠️ Error en roles: {e}")

    # 3. MENÚ DE SUGERENCIAS (NUEVO HEADER FIJO)
    suggest_channel = bot.get_channel(SUGGEST_CHANNEL_ID)
    if suggest_channel:
        try:
            # Verificamos si ya está el mensaje de guía
            last_sug_msg = None
            async for msg in suggest_channel.history(limit=1): last_sug_msg = msg
            
            guide_ok = False
            # Si el ultimo mensaje es del bot y tiene el titulo correcto, asumimos que está bien
            if last_sug_msg and last_sug_msg.author == bot.user and last_sug_msg.embeds:
                if "SUGGESTION SYSTEM" in (last_sug_msg.embeds[0].title or ""): guide_ok = True
            
            # Si no es el último mensaje (porque alguien sugirió algo) o no existe, lo enviamos
            # NOTA: En este canal NO borramos mensajes viejos para no borrar sugerencias de usuarios
            
            if not guide_ok:
                # Solo borramos mensajes PROPIOS del bot que sean viejos (limpieza de spam del bot)
                async for msg in suggest_channel.history(limit=10):
                    if msg.author == bot.user:
                         # Borramos si es un recordatorio viejo o un menú viejo
                         await msg.delete()

                # Enviamos el Header Nuevo
                embed = discord.Embed(
                    title="💡 **SUGGESTION SYSTEM**",
                    description=(
                        f"To suggest something, use the command below:\n\n"
                        f"` .suggest <your text> `\n\n"
                        f"{HELL_ARROW} **Example:** `.suggest Add more kits`\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━"
                    ),
                    color=0x990000
                )
                embed.set_footer(text="Hell Legion System • Suggestions")
                if bot.user.avatar: embed.set_thumbnail(url=bot.user.avatar.url)
                
                await suggest_channel.send(embed=embed)
                print("✅ Menú de sugerencias creado.")
                
        except Exception as e:
            print(f"⚠️ Error en sugerencias: {e}")

    # 4. ESCÁNER DE NOMBRES
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
