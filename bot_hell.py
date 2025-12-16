import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
import random
import threading
import re
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==========================================
# 🚑 FAKE WEB SERVER (ANTI-CRASH & UPTIMEROBOT)
# ==========================================
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"HELL SYSTEM ACTIVE")
    
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_fake_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

# ==========================================
# 🔐 CONFIGURACIÓN GENERAL
# ==========================================
TOKEN = os.environ.get("DISCORD_TOKEN")

# --- IDs DE CANALES ---
GIVEAWAY_CHANNEL_ID = 1449849645495746803 
POLLS_CHANNEL_ID = 1449083865862770819      
CMD_CHANNEL_ID = 1449346777659609288
ROLES_CHANNEL_ID = 1449083960578670614
SUGGEST_CHANNEL_ID = 1449346646465839134
VAULT_CHANNEL_ID = 1450244608817762465  # <--- ✅ ID ACTUALIZADA

# --- IDs DE ROLES ---
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

# --- EMOJIS & ESTÉTICA ---
HELL_ARROW = "<a:hell_arrow:1211049707128750080>" 
NOTIFICATION_ICON = "<a:notification:1275469575638614097>"
CHECK_ICON = "<a:Check_hell:1450255850508779621>" 
CROSS_ICON = "<a:cruz_hell:1450255934273355918>" 
# URL directa a imagen de Vault de ARK (Wiki oficial)
VAULT_IMAGE_URL = "https://ark.wiki.gg/images/thumb/8/88/Vault.png/300px-Vault.png"

SUPPORT_TEXT = "! HELL WIPES FRIDAY 100€"
SUPPORT_ROLE_ID = 1336477737594130482

COMMAND_LIST_TEXT = f"""
{HELL_ARROW} **!recipes** - Ver crafteos del server
"""

# VARIABLES GLOBALES
suggestion_count = 0

# --- ESTADO DEL EVENTO VAULT ---
vault_state = {
    "active": False,
    "code": None,
    "prize": None,
    "message_id": None,
    "hints_task": None
}
user_cooldowns = {} # Para guardar tiempos de espera

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
# 🏦 SISTEMA VAULT (CAJA FUERTE)
# ==========================================

class VaultModal(discord.ui.Modal, title="🔐 ENTER VAULT CODE"):
    code_input = discord.ui.TextInput(
        label="4-Digit Code",
        placeholder="####",
        min_length=4,
        max_length=4,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        current_time = time.time()

        # 1. Chequeo de Cooldown (15 segundos)
        if user_id in user_cooldowns:
            elapsed = current_time - user_cooldowns[user_id]
            remaining = 15 - elapsed
            if remaining > 0:
                await interaction.response.send_message(f"⏳ Please wait **{int(remaining)}s** before trying again.", ephemeral=True)
                return
        
        # Guardar tiempo del intento
        user_cooldowns[user_id] = current_time

        # 2. Verificar si evento sigue activo
        if not vault_state["active"]:
            await interaction.response.send_message("❌ Event ended.", ephemeral=True)
            return

        guess = self.code_input.value

        # 3. Verificar Código
        if guess == vault_state["code"]:
            # --- ¡GANADOR! ---
            vault_state["active"] = False # Cerrar evento
            
            # Cancelar pistas
            if vault_state["hints_task"]:
                vault_state["hints_task"].cancel()

            # Mensaje al usuario
            await interaction.response.send_message(f"🔓 **ACCESS GRANTED!** Code accepted.", ephemeral=True)
            
            # Mensaje Público de Ganador
            winner_embed = discord.Embed(
                title="🎉 VAULT CRACKED! 🎉",
                description=f"👑 **WINNER:** {interaction.user.mention}\n🔓 **CODE:** `{guess}`\n🎁 **PRIZE:** {vault_state['prize']}",
                color=0xFFD700
            )
            winner_embed.set_image(url="https://media1.tenor.com/m/X9kF3Qv1mJAAAAAC/open-safe.gif") # Gif abriendo
            winner_embed.set_footer(text="Hell Legion System • Vault Event")
            
            channel = bot.get_channel(VAULT_CHANNEL_ID)
            if channel:
                await channel.send(content=f"{interaction.user.mention} opened the Vault!", embed=winner_embed)

            # Desactivar botón original (opcional)
            try:
                msg = await interaction.channel.fetch_message(vault_state["message_id"])
                await msg.edit(view=None)
            except: pass

        else:
            # --- CÓDIGO INCORRECTO ---
            await interaction.response.send_message(f"❌ **Wrong code!** Try again in 15 seconds.", ephemeral=True)

class VaultView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) 

    @discord.ui.button(label="Submit Code", style=discord.ButtonStyle.success, emoji="🔓", custom_id="vault_open_btn")
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not vault_state["active"]:
            await interaction.response.send_message("❌ This event is over.", ephemeral=True)
            return
        await interaction.response.send_modal(VaultModal())

# --- TAREA DE PISTAS (HINTS) ---
async def manage_vault_hints(channel, message, code):
    try:
        # PISTA 2: A las 5 Horas
        await asyncio.sleep(18000) # 5 horas en segundos
        
        if not vault_state["active"]: return

        hint_2 = f"{code[:2]}##"
        new_embed = message.embeds[0]
        # Actualizamos el campo de la pista (index 0 porque es el primer field)
        new_embed.set_field_at(0, name="🧟 First Hint", value=f"`{hint_2}`", inline=True)
        await message.edit(embed=new_embed)
        
        # PISTA 3: A las 24 Horas (19h mas tarde)
        await asyncio.sleep(68400) # 19 horas mas
        
        if not vault_state["active"]: return

        hint_3 = f"{code[:3]}#"
        new_embed = message.embeds[0]
        new_embed.set_field_at(0, name="🧟 First Hint", value=f"`{hint_3}`", inline=True)
        await message.edit(embed=new_embed)

    except asyncio.CancelledError:
        pass

# ==========================================
# 🔘 CLASE DE BOTONES (AUTO-ROLES)
# ==========================================
class RoleButton(discord.ui.Button):
    def __init__(self, label, role_id):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, custom_id=f"role_{role_id}")
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if not role: return
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"➖ Removed **{role.name}**", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"➕ Added **{role.name}**", ephemeral=True)

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
    try: val = int(time_str[:-1])
    except: return -1
    if unit == 's': return val
    if unit == 'm': return val * 60
    if unit == 'h': return val * 3600
    if unit == 'd': return val * 86400
    return 0

# ==========================================
# ⚡ COMANDOS SLASH
# ==========================================

# --- COMANDO VAULT ---
@bot.tree.command(name="event_vault", description="Inicia el evento de la Caja Fuerte")
@app_commands.describe(code="Código de 4 dígitos (ej: 5821)", prize="Premio a ganar")
async def event_vault(interaction: discord.Interaction, code: str, prize: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ No tienes permisos.", ephemeral=True)
        return

    if len(code) != 4 or not code.isdigit():
        await interaction.response.send_message("❌ El código debe ser de **4 NÚMEROS**.", ephemeral=True)
        return

    channel = bot.get_channel(VAULT_CHANNEL_ID)
    if not channel:
        await interaction.response.send_message("❌ Error: No encuentro el canal VAULT_CHANNEL_ID.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    # Preparar Pista Inicial
    hint_1 = f"{code[0]}###"

    # Embed estilo "Lazy Wipe" adaptado a HELL
    embed = discord.Embed(title=f"✊ **OPEN THE VAULT EVENT** ✊", color=0x2b2d31)
    
    desc = (
        f"🧨 **No need a C4**\n\n"
        f"🔸 **Guess the code and win the prize**\n"
        f"🔸 **You can guess every 15 seconds**\n\n"
        f"🎁 **PRIZE:** {prize}"
    )
    embed.description = desc
    embed.add_field(name="🧟 First Hint", value=f"`{hint_1}`", inline=True)
    embed.set_thumbnail(url=VAULT_IMAGE_URL) # Imagen pequeña a la derecha (opcional, o usa set_image para grande)
    embed.set_image(url=VAULT_IMAGE_URL)     # Imagen grande abajo
    embed.set_footer(text="Hell Legion System • Vault Event")

    view = VaultView()
    msg = await channel.send(embed=embed, view=view)

    # Guardar estado
    vault_state["active"] = True
    vault_state["code"] = code
    vault_state["prize"] = prize
    vault_state["message_id"] = msg.id
    
    # Iniciar cronómetro de pistas
    if vault_state["hints_task"]:
        vault_state["hints_task"].cancel()
    
    vault_state["hints_task"] = asyncio.create_task(manage_vault_hints(channel, msg, code))

    await interaction.followup.send(f"✅ Evento iniciado con código `{code}` en {channel.mention}.")


@bot.tree.command(name="start_giveaway", description="Inicia un sorteo")
async def start_giveaway(interaction: discord.Interaction, tiempo: str, premio: str):
    if not interaction.user.guild_permissions.administrator: return
    seconds = convert_time(tiempo)
    if seconds <= 0: return
    embed = discord.Embed(title="🎉 GIVEAWAY", description=f"Prize: **{premio}**\nTime: **{tiempo}**", color=0xff0000)
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    await msg.add_reaction("🎉")
    await asyncio.sleep(seconds)
    # Logica simplificada...

@bot.tree.command(name="finish_polls", description="Publica resultados de encuestas.")
async def finish_polls(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator: return
    await interaction.response.send_message("Procesando encuestas...", ephemeral=True)
    # Tu logica de polls iría aquí...

# ==========================================
# 🛡️ GESTOR DE MENSAJES
# ==========================================
@bot.event
async def on_message(message):
    if message.author.bot: return

    # --- SUGERENCIAS ---
    if message.channel.id == SUGGEST_CHANNEL_ID:
        if not message.content.startswith(".suggest"):
            try: await message.delete()
            except: pass
            return
        
        try: await message.delete()
        except: pass
        suggestion_content = message.content[8:].strip()
        if not suggestion_content: return 
        
        embed = discord.Embed(description=f"**{suggestion_content}**", color=0xffaa00)
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.set_footer(text="Hell Legion System • Suggestions")
        sent_msg = await message.channel.send(embed=embed)
        try:
            await sent_msg.add_reaction(CHECK_ICON)
            await sent_msg.add_reaction(CROSS_ICON)
        except: pass
        return

    # --- LIMPIEZA COMANDOS ---
    if message.channel.id == CMD_CHANNEL_ID:
        try: await message.delete(delay=120) 
        except: pass 

    await bot.process_commands(message)

# ==========================================
# 🚀 STARTUP
# ==========================================
@bot.event
async def on_ready():
    print(f"🔥 HELL SYSTEM ONLINE - {bot.user}")
    
    # ⚠️ IMPORTANTE: Añadimos las Views para que los botones funcionen al reiniciar
    bot.add_view(RolesView())
    bot.add_view(VaultView()) 
    
    try: await bot.tree.sync()
    except: pass

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
    role = after.guild.get_role(SUPPORT_ROLE_ID)
    if not role: return
    name_has_tag = SUPPORT_TEXT.lower() in name_check.lower()
    has_role = role in after.roles
    if name_has_tag and not has_role:
        try: await after.add_roles(role)
        except: pass
    elif not name_has_tag and has_role:
        try: await after.remove_roles(role)
        except: pass

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
