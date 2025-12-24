import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
import asyncio
import random
import threading
import re
import time
import json
import traceback
import io 
import datetime 
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==========================================
# 🚑 FAKE WEB SERVER (Mantiene el bot 24/7)
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
# 🔐 CONFIGURATION
# ==========================================
TOKEN = os.environ.get("DISCORD_TOKEN")

# IDs CHANNELS
GIVEAWAY_CHANNEL_ID = 1449849645495746803 
POLLS_CHANNEL_ID = 1449083865862770819       
CMD_CHANNEL_ID = 1449346777659609288
ROLES_CHANNEL_ID = 1449083960578670614
SUGGEST_CHANNEL_ID = 1449346646465839134
VAULT_CHANNEL_ID = 1450244608817762465
DINO_CHANNEL_ID = 1450244689285353544 
MINIGAMES_CHANNEL_ID = 1450244729848598618

# 🔴 CLOUD DATABASE CHANNEL
DB_CHANNEL_ID = 1451330350436323348

SHOP_CHANNEL_NAME = "「🔥」hell-store"

# ==========================================
# 🖼️ EMOJIS & DATA (BASE DE DATOS COMPLETA)
# ==========================================
SERVER_EMOJIS = {
    # EMOJIS ANIMADOS (IMPORTANTE: LA 'a' AL PRINCIPIO)
    "emoji_9": "<a:emoji_9:868224374333919333>",
    "emoji_48": "<a:emoji_48:926958427404648488>",
    "Good_2": "<a:Good_2:930098652804952074>",
    "Red": "<a:Red:931298336458301520>",
    "Good": "<a:Good:931298968250482768>",
    "Green": "<a:Green:931299102694715393>",
    "Red_Point": "<a:Red_Point:1096357727334318210>",
    "Withe_Point": "<a:Withe_Point:1096357771462582332>",
    "Black_Arrow": "<a:Black_Arrow:1137005574744191047>",
    "Withe_Arrow": "<a:Withe_Arrow:1137005592100212746>",
    "party": "<a:party:1137005680520331304>",
    "hell_arrow": "<a:hell_arrow:1211049707128750080>",
    "cyan_crown": "<a:cyan_crown:1219625507243429968>",
    "pink_crown": "<a:pink_crown:1219625526550073385>",
    "green_crown": "<a:green_crown:1219625543314575483>",
    "yelow_crown": "<a:yelow_crown:1219625559747858523>",
    "blue_crown": "<a:blue_crown:1219625577082785854>",
    "notification": "<a:notification:1275469575638614097>",
    "fire": "<a:fire:1275469598183002183>",
    "warn": "<a:warn:1275471955138711572>",
    "emoji_74": "<a:emoji_74:1317875400419836016>",
    "emoji_75": "<a:emoji_75:1317875418782498858>", 
    "emoji_68": "<a:emoji_68:1328804237546881126>", 
    "emoji_69": "<a:emoji_69:1328804255741771899>", 
    "emoji_70": "<a:emoji_70:1328804269683376150>",
    "Blue_Arrow": "<a:Blue_Arrow:1328804298951360605>",
    "emoji_72": "<a:emoji_72:1328804312859672586>",
    "Check": "<a:Check:1336817519364669511>",
    "Purple_Clock": "<a:Purple_Clock:1336818117094936587>",
    "Red_Clock": "<a:Red_Clock:1336818629743738963>",
    "event_ping": "<a:event_ping:1336821944036622467>",
    "hype": "<a:hype:1336822678501326949>",
    "Check_hell": "<a:Check_hell:1450255850508779621>",
    "cruz_hell": "<a:cruz_hell:1450255934273355918>",
    "pikachu_culon": "<:pikachu_culon:1450624552827752479>", 
    "Gift_hell": "<a:Gift_hell:1450624953723654164>",
    "party_new": "<a:party:1450625235383488649>", 
    "greenarrow": "<a:greenarrow:1450625398051311667>",
    "Pokecoin": "<:Pokecoin:1450625492309901495>", 
    "C4_HELL": "<:C4_HELL:1451357075321131049>",   

    # RESTO
    "Money": "<:Money:932019879287087164>",
    "Paypal": "<:Paypal:1096357712289345566>",
    "Emoji": "<:Emoji:1137005608697086092>",
    "Anouncement": "<:Anouncement:1137005622160785418>",
    "Owner": "<:Owner:1139164478324346911>",
    "head": "<:head:1139301621378076812>",
    "mod": "<:mod:1139305860703719566>",
    "staff": "<:staff:1139305872682647737>",
    "bot": "<:bot:1139305890915307541>",
    "boost": "<:boost:1139305913530986596>",
    "dono": "<:dono:1139305927103758336>",
    "content_creator": "<:content_creator:1139305949295820820>",
    "trial": "<:trial:1139353110406508584>",
    "Admn": "<:Admn:1139353149505810563>",
    "trusted": "<:trusted:1139353676620779520>",
    "mele": "<:mele:1210301380389240902>",
    "speed": "<:speed:1210301413276647514>",
    "fabrication": "<:fabrication:1210301469203496970>",
    "Oxigen": "<:Oxigen:1210317445840244736>",
    "stamine": "<:stamine:1210317471475699782>",
    "weight": "<:weight:1210317493072302190>",
    "water": "<:water:1210317549946929192>",
    "resistence": "<:resistence:1210317577134415912>",
}

# CONFIGURACIÓN VARIABLES EMOJIS
HELL_ARROW = SERVER_EMOJIS["hell_arrow"]
NOTIFICATION_ICON = SERVER_EMOJIS["notification"]
CHECK_ICON = SERVER_EMOJIS["Check_hell"]
CROSS_ICON = SERVER_EMOJIS["cruz_hell"]
EMOJI_BLOOD = SERVER_EMOJIS["emoji_75"]
EMOJI_CODE  = SERVER_EMOJIS["emoji_68"]

EMOJI_DINO_TITLE = SERVER_EMOJIS["pikachu_culon"]
EMOJI_REWARD     = SERVER_EMOJIS["Gift_hell"]
EMOJI_CORRECT    = SERVER_EMOJIS["Good_2"]
EMOJI_WINNER     = SERVER_EMOJIS["party_new"]
EMOJI_ANSWER     = SERVER_EMOJIS["greenarrow"]
EMOJI_POINTS     = SERVER_EMOJIS["Pokecoin"]

# EMOJIS GIVEAWAY & VAULT
EMOJI_PARTY_NEW = SERVER_EMOJIS["party_new"]
EMOJI_GIFT_NEW = SERVER_EMOJIS["Gift_hell"]
EMOJI_FIRE_ANIM = SERVER_EMOJIS["emoji_9"]
EMOJI_CLOCK_NEW = SERVER_EMOJIS["Purple_Clock"]
EMOJI_VAULT_WINNER_CROWN = SERVER_EMOJIS["yelow_crown"]
EMOJI_VAULT_CODE_ICON = SERVER_EMOJIS["emoji_69"]

EMOJI_GIVEAWAY_ENDED_RED = SERVER_EMOJIS["Red"]
EMOJI_GIVEAWAY_WINNER_CROWN = SERVER_EMOJIS["yelow_crown"]

# 🔥 EMOJIS MODAL VAULT NUEVOS 🔥
EMOJI_VAULT_WAIT = SERVER_EMOJIS["Red_Clock"]
EMOJI_VAULT_DENIED = SERVER_EMOJIS["warn"]

IMG_ARK_DROP = "https://ark.wiki.gg/images/e/e3/Supply_Crate_Level_60.png"
VAULT_IMAGE_URL = "https://ark.wiki.gg/images/thumb/8/88/Vault.png/300px-Vault.png"

SUPPORT_TEXT = "! HELL WIPES FRIDAY 100€"
SUPPORT_ROLE_ID = 1336477737594130482

# --- STATES (GLOBAL) ---
vault_state = {
    "active": False,
    "code": None,
    "prize": None,
    "message_id": None,
    "hints_task": None
}
user_cooldowns = {} 
last_minigame_message = None 
last_dino_message = None 

# --- RAM DATABASE & CLOUD SYNC ---
points_data = {} 
giveaways_data = {} 

def add_points_to_user(user_id, amount):
    uid = str(user_id)
    if uid not in points_data: points_data[uid] = 0
    points_data[uid] += amount
    return points_data[uid]

def remove_points_from_user(user_id, amount):
    uid = str(user_id)
    if uid not in points_data: points_data[uid] = 0
    if points_data[uid] < amount: 
        points_data[uid] = 0 
    else:
        points_data[uid] -= amount
    return True

def get_user_points(user_id):
    return points_data.get(str(user_id), 0)

# 🔥 FUNCIONES DE GUARDADO 🔥
async def save_giveaways_db():
    try:
        channel = bot.get_channel(DB_CHANNEL_ID)
        if channel:
            json_str = json.dumps(giveaways_data, indent=None)
            file_obj = discord.File(io.StringIO(json_str), filename="db_giveaways.json")
            await channel.send(f"Giveaways Backup: {int(time.time())}", file=file_obj)
    except: pass

async def backup_points_task():
    await bot.wait_until_ready()
    # 1. LOAD POINTS
    try:
        channel = bot.get_channel(DB_CHANNEL_ID)
        if channel:
            async for msg in channel.history(limit=50):
                if msg.author == bot.user and msg.attachments:
                    if msg.attachments[0].filename == "db_points.json":
                        data_bytes = await msg.attachments[0].read()
                        global points_data
                        points_data = json.loads(data_bytes)
                        print(f"[DB] Points loaded.")
                        break
    except: pass

    # 2. LOAD GIVEAWAYS
    try:
        channel = bot.get_channel(DB_CHANNEL_ID)
        if channel:
            found_gw = False
            async for msg in channel.history(limit=50):
                if msg.author == bot.user and msg.attachments:
                    if msg.attachments[0].filename == "db_giveaways.json":
                        data_bytes = await msg.attachments[0].read()
                        global giveaways_data
                        giveaways_data = json.loads(data_bytes)
                        print(f"[DB] Giveaways loaded: {len(giveaways_data)}")
                        found_gw = True
                        break
            
            if found_gw:
                for msg_id, data in list(giveaways_data.items()):
                    bot.loop.create_task(run_giveaway_timer(
                        int(data["channel_id"]), 
                        int(msg_id), 
                        data["end_time"], 
                        data["prize"], 
                        data["winners"]
                    ))
    except Exception as e: 
        print(f"[DB ERROR] Giveaways load failed: {e}")

    # Loop de guardado de puntos
    while not bot.is_closed():
        await asyncio.sleep(120) 
        try:
            channel = bot.get_channel(DB_CHANNEL_ID)
            if channel and points_data:
                json_str = json.dumps(points_data, indent=None)
                file_obj = discord.File(io.StringIO(json_str), filename="db_points.json")
                await channel.send(f"Points Backup: {int(time.time())}", file=file_obj)
                try:
                    async for msg in channel.history(limit=20):
                        if msg.author == bot.user:
                            if (time.time() - msg.created_at.timestamp()) > 600:
                                await msg.delete()
                except: pass
        except: pass

# ==========================================
# ⚙️ SETUP BOT
# ==========================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True
intents.presences = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ==========================================
# 🧩 HELPER FUNCTIONS (CORREGIDO PARSE POLL)
# ==========================================
def parse_poll_result(content, winner_emoji):
    lines = content.split('\n')
    question = "Pregunta desconocida"
    answer = "Respuesta desconocida"
    
    for line in lines:
         # Buscamos la línea que tiene la flecha o empieza por >
         if "hell_arrow" in line or line.strip().startswith(">"):
             # Limpiamos todos los adornos sucios
             clean_q = line.replace("<a:hell_arrow:1334124040960610336>", "") 
             clean_q = clean_q.replace("<a:hell_arrow:1211049707128750080>", "") 
             clean_q = clean_q.replace(">", "")
             clean_q = clean_q.replace("*", "") # Quitamos negritas viejas
             clean_q = clean_q.replace("_", "") # Quitamos subrayados viejos
             clean_q = clean_q.strip()
             question = clean_q
             break
             
    s_emoji = str(winner_emoji)
    found = False
    for line in lines:
        if s_emoji in line:
            answer = line.replace(s_emoji, "").strip()
            # Quitamos guiones o decoraciones extra
            if answer.startswith("-") or answer.startswith(":"):
                answer = answer[1:].strip()
            found = True
            break
            
    if not found: answer = s_emoji 
    return question, answer

# 🔥 NUEVO CONVERTIDOR DE TIEMPO FLEXIBLE
def convert_time(time_str):
    time_regex = re.compile(r"(\d+)([smhd])")
    matches = time_regex.findall(time_str.lower().replace(" ", ""))
    total_seconds = 0
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    if not matches: return -1
    for amount, unit in matches:
        total_seconds += int(amount) * time_dict[unit]
    return total_seconds

async def run_giveaway_timer(channel_id, message_id, end_time, prize, winners_count):
    remaining = end_time - time.time()
    if remaining > 0:
        await asyncio.sleep(remaining)
    
    try:
        channel = bot.get_channel(channel_id)
        if not channel: return
        msg = await channel.fetch_message(message_id)
    except:
        if str(message_id) in giveaways_data:
            del giveaways_data[str(message_id)]
            await save_giveaways_db()
        return

    users = []
    for reaction in msg.reactions:
        if str(reaction.emoji) == EMOJI_PARTY_NEW:
            async for user in reaction.users():
                if not user.bot: 
                    users.append(user)
    
    if len(users) > 0:
        winner_list = random.sample(users, k=min(len(users), winners_count))
        winners_text = ", ".join([w.mention for w in winner_list])
        
        embed = msg.embeds[0]
        embed.color = discord.Color.greyple()
        embed.description = (
            f"{EMOJI_GIFT_NEW} **Prize:** {prize}\n"
            f"{EMOJI_GIVEAWAY_ENDED_RED} **ENDED**\n"
            f"{EMOJI_GIVEAWAY_WINNER_CROWN} **Winners:** {winners_text}"
        )
        await msg.edit(embed=embed)
        await channel.send(f"🎉 **CONGRATULATIONS** {winners_text}! You won **{prize}**!")
    else:
        await channel.send(f"❌ Giveaway for **{prize}** ended without participants.")

    if str(message_id) in giveaways_data:
        del giveaways_data[str(message_id)]
        await save_giveaways_db()

# ==========================================
# 🦖 MINIGAME: WHO IS THE DINO
# ==========================================

class DinoModal(discord.ui.Modal, title="🦖 WHO IS THAT DINO?"):
    answer_input = discord.ui.TextInput(label="Dino Name", placeholder="Enter name...", required=True)

    def __init__(self, correct_answer):
        super().__init__()
        self.correct_answer = correct_answer
        self.view_ref = None

    async def on_submit(self, interaction: discord.Interaction):
        guess = self.answer_input.value.strip().lower()
        if self.view_ref and self.view_ref.grabbed:
             await interaction.response.send_message("❌ Someone was faster.", ephemeral=True)
             return

        if guess == self.correct_answer.lower():
            if self.view_ref: self.view_ref.grabbed = True 
            points_won = 200 
            add_points_to_user(interaction.user.id, points_won)
            try: await interaction.response.send_message(f"{EMOJI_CORRECT} **CORRECT!** You guessed it.", ephemeral=True)
            except: pass

            embed = discord.Embed(color=0x00FF00)
            embed.description = (
                f"{EMOJI_WINNER} **WINNER:** {interaction.user.mention}\n"
                f"{EMOJI_ANSWER} **ANSWER:** `{self.correct_answer}`\n"
                f"{EMOJI_POINTS} **POINTS:** +{points_won}"
            )
            embed.set_footer(text="Hell System • Dino Games")
            if interaction.channel: await interaction.channel.send(embed=embed)
            
            try:
                view = self.view_ref 
                for child in view.children: child.disabled = True
                await interaction.message.edit(view=view)
            except: pass
        else:
            try: await interaction.response.send_message(f"❌ **WRONG!** Try again.", ephemeral=True)
            except: pass

class DinoView(discord.ui.View):
    def __init__(self, correct_dino):
        super().__init__(timeout=None)
        self.correct_dino = correct_dino
        self.grabbed = False 

    @discord.ui.button(label="GUESS THE DINO", style=discord.ButtonStyle.primary, emoji="❓", custom_id="dino_guess_btn_v2")
    async def guess_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.grabbed:
            await interaction.response.send_message("❌ Round ended.", ephemeral=True)
            return
        modal = DinoModal(self.correct_dino)
        modal.view_ref = self 
        await interaction.response.send_modal(modal)

@tasks.loop(minutes=20)
async def dino_game_loop():
    global last_dino_message
    try:
        channel = bot.get_channel(DINO_CHANNEL_ID)
        if not channel: return
        
        if last_dino_message:
            try: await last_dino_message.edit(view=None)
            except: pass

        dino_real_name = random.choice(ARK_DINOS)
        char_list = list(dino_real_name.upper())
        random.shuffle(char_list)
        scrambled_name = "".join(char_list)
        while scrambled_name == dino_real_name.upper():
            random.shuffle(char_list)
            scrambled_name = "".join(char_list)

        embed = discord.Embed(title=f"{EMOJI_DINO_TITLE} WHO IS THE DINO?", color=0xFFA500)
        embed.description = (
            f"Unscramble the name of this creature!\n\n"
            f"🧩 **SCRAMBLED:** `{scrambled_name}`\n\n"
            f"Click the button to answer."
        )
        embed.set_footer(text="Hell System • Dino Games")
        view = DinoView(correct_dino=dino_real_name)
        last_dino_message = await channel.send(embed=embed, view=view)
    except Exception as e:
        print(f"Error in Dino Loop: {e}")

# 🔥 ARREGLO DE LOOP (Espera a que el bot este listo)
@dino_game_loop.before_loop
async def before_dino_game_loop():
    await bot.wait_until_ready()

# ==========================================
# 🎮 MINIGAMES CLASSES
# ==========================================

class ArkDropView(discord.ui.View):
    def __init__(self): 
        super().__init__(timeout=None)
        self.grabbed = False
    @discord.ui.button(label="CLAIM DROP", style=discord.ButtonStyle.danger, emoji="🎁", custom_id="drop_claim_btn")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.grabbed: return 
        self.grabbed = True
        try:
            button.label = f"Loot of {interaction.user.name}"
            button.style = discord.ButtonStyle.secondary
            button.disabled = True
            add_points_to_user(interaction.user.id, 200)
            embed = interaction.message.embeds[0]
            embed.color = discord.Color.dark_grey()
            embed.set_footer(text=f"Claimed by: {interaction.user.display_name} (+200 Points)")
            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.followup.send(f"🔴 **{interaction.user.mention}** opened the Red Drop and won 200 points!", ephemeral=False)
            self.stop()
        except Exception: pass

class ArkTameView(discord.ui.View):
    def __init__(self, correct_food, dino_name):
        super().__init__(timeout=None)
        self.correct_food = correct_food
        self.dino_name = dino_name
        self.grabbed = False
    async def feed(self, interaction: discord.Interaction, food: str):
        if self.grabbed: return
        self.grabbed = True
        try:
            if food == self.correct_food:
                add_points_to_user(interaction.user.id, 200)
                await interaction.response.send_message(f"🦕 **TAMED!** {interaction.user.mention} gave {food} to the {self.dino_name} (+200 pts).", ephemeral=False)
                for child in self.children: child.disabled = True
                await interaction.message.edit(view=self)
                self.stop()
            else:
                await interaction.response.send_message(f"❌ The {self.dino_name} rejects {food}. It fled!", ephemeral=False)
                for child in self.children: child.disabled = True
                await interaction.message.edit(view=self)
                self.stop()
        except Exception: pass
    @discord.ui.button(label="Raw Meat 🥩", style=discord.ButtonStyle.danger, custom_id="tm_meat")
    async def meat(self, interaction: discord.Interaction, button: discord.ui.Button): await self.feed(interaction, "Raw Meat")
    @discord.ui.button(label="Mejoberries 🫐", style=discord.ButtonStyle.primary, custom_id="tm_berry")
    async def berries(self, interaction: discord.Interaction, button: discord.ui.Button): await self.feed(interaction, "Mejoberries")

class ArkCraftView(discord.ui.View):
    def __init__(self, correct_mat):
        super().__init__(timeout=None)
        self.correct_mat = correct_mat
        self.grabbed = False
    async def check_mat(self, interaction: discord.Interaction, mat_clicked: str):
        if self.grabbed: return
        self.grabbed = True
        try:
            if mat_clicked == self.correct_mat:
                add_points_to_user(interaction.user.id, 200)
                await interaction.response.send_message(f"🔨 **Correct!** {interaction.user.mention} crafted the item (+200 pts).", ephemeral=False)
                for child in self.children: child.disabled = True
                await interaction.message.edit(view=self)
                self.stop()
            else:
                await interaction.response.send_message("❌ Wrong material. It broke.", ephemeral=False)
                for child in self.children: child.disabled = True
                await interaction.message.edit(view=self)
                self.stop()
        except Exception: pass
    @discord.ui.button(label="Metal / Ingots", style=discord.ButtonStyle.secondary, custom_id="cr_metal")
    async def b1(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check_mat(interaction, "Metal")
    @discord.ui.button(label="Stone / Wood / Flint", style=discord.ButtonStyle.secondary, custom_id="cr_stone")
    async def b2(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check_mat(interaction, "Stone/Wood")
    @discord.ui.button(label="Hide / Fiber / Thatch", style=discord.ButtonStyle.secondary, custom_id="cr_hide")
    async def b3(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check_mat(interaction, "Hide/Fiber")
    @discord.ui.button(label="Electronics / Polymer / Gunpowder", style=discord.ButtonStyle.success, custom_id="cr_adv")
    async def b4(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check_mat(interaction, "Advanced")

class ArkImprintView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.needs = random.choice(["Cuddle", "Walk", "Feed"])
        self.grabbed = False
    async def check(self, interaction: discord.Interaction, action: str):
        if self.grabbed: return
        self.grabbed = True
        try:
            if action == self.needs:
                add_points_to_user(interaction.user.id, 200)
                await interaction.response.send_message(f"❤️ **Imprinting increased!** {interaction.user.mention} got it right (+200 pts).", ephemeral=False)
                for child in self.children: child.disabled = True
                await interaction.message.edit(view=self)
                self.stop()
            else:
                await interaction.response.send_message(f"😭 The baby wanted **{self.needs}**. It got angry and left!", ephemeral=False)
                embed = interaction.message.embeds[0]
                embed.color = discord.Color.red()
                embed.title = "Rearing FAILED"
                for child in self.children: child.disabled = True
                await interaction.message.edit(embed=embed, view=self)
                self.stop()
        except Exception: pass
    @discord.ui.button(label="Cuddle 🧸", style=discord.ButtonStyle.primary, custom_id="imp_cud")
    async def b1(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check(interaction, "Cuddle")
    @discord.ui.button(label="Walk 🚶", style=discord.ButtonStyle.success, custom_id="imp_wlk")
    async def b2(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check(interaction, "Walk")
    @discord.ui.button(label="Feed 🍖", style=discord.ButtonStyle.danger, custom_id="imp_fed")
    async def b3(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check(interaction, "Feed")

class ArkAlphaView(discord.ui.View):
    def __init__(self, win, loss, chance): 
        super().__init__(timeout=None)
        self.win = win
        self.loss = loss
        self.chance = chance
        self.grabbed = False
    @discord.ui.button(label="🗡️ ATTACK ALPHA", style=discord.ButtonStyle.danger, custom_id="alpha_atk")
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.grabbed: return
        self.grabbed = True
        try:
            if random.random() < self.chance: 
                add_points_to_user(interaction.user.id, self.win)
                await interaction.response.send_message(f"🏆 **VICTORY!** {interaction.user.mention} killed the Alpha (+{self.win} pts).", ephemeral=False)
            else: 
                remove_points_from_user(interaction.user.id, self.loss)
                await interaction.response.send_message(f"💀 **DEATH...** {interaction.user.mention} died and lost **{self.loss} points**.", ephemeral=False)
            button.disabled = True
            await interaction.message.edit(view=self)
            self.stop()
        except Exception: pass

class PokemonVisualView(discord.ui.View):
    def __init__(self, correct_type, poke_name):
        super().__init__(timeout=None)
        self.correct_type = correct_type
        self.poke_name = poke_name
        self.grabbed = False
    async def guess(self, interaction: discord.Interaction, type_guess: str):
        if self.grabbed: return
        self.grabbed = True
        try:
            if type_guess == self.correct_type:
                add_points_to_user(interaction.user.id, 200)
                await interaction.response.send_message(f"✅ **Correct!** {interaction.user.mention} got it right (+200 pts).", ephemeral=False)
                for child in self.children: child.disabled = True
                await interaction.message.edit(view=self)
                self.stop()
            else:
                await interaction.response.send_message(f"❌ Incorrect. It was {self.correct_type}.", ephemeral=False)
                for child in self.children: child.disabled = True
                await interaction.message.edit(view=self)
                self.stop()
        except Exception: pass
    @discord.ui.button(label="Fire 🔥", style=discord.ButtonStyle.danger, custom_id="pk_fir")
    async def b1(self, interaction: discord.Interaction, button: discord.ui.Button): await self.guess(interaction, "Fire")
    @discord.ui.button(label="Water 💧", style=discord.ButtonStyle.primary, custom_id="pk_wat")
    async def b2(self, interaction: discord.Interaction, button: discord.ui.Button): await self.guess(interaction, "Water")
    @discord.ui.button(label="Grass 🌿", style=discord.ButtonStyle.success, custom_id="pk_gra")
    async def b3(self, interaction: discord.Interaction, button: discord.ui.Button): await self.guess(interaction, "Grass")

# ==========================================
# 🔄 AUTOMATIC SYSTEM
# ==========================================

async def spawn_game(channel):
    game_type = random.randint(1, 6)
    view = None
    if game_type == 1:
        embed = discord.Embed(title="RED SUPPLY DROP INCOMING!", description="Contains high-level loot. Claim it fast!", color=discord.Color.red())
        embed.set_image(url=IMG_ARK_DROP)
        view = ArkDropView()
        msg = await channel.send(embed=embed, view=view)
        return msg
    elif game_type == 2:
        data = random.choice(DATA_TAMING)
        embed = discord.Embed(title="Unconscious Dino!", description=f"What does this **{data['name']}** eat to be tamed?", color=discord.Color.green())
        embed.set_image(url=data["url"])
        view = ArkTameView(data["food"], data["name"])
        msg = await channel.send(embed=embed, view=view)
        return msg
    elif game_type == 3:
        data = random.choice(DATA_CRAFTING)
        embed = discord.Embed(title="Crafting Table", description=f"What is the main material for: **{data['name']}**?", color=discord.Color.orange())
        embed.set_image(url=data["url"])
        view = ArkCraftView(data["mat"])
        msg = await channel.send(embed=embed, view=view)
        return msg
    elif game_type == 4:
        img = random.choice(DATA_BREEDING_IMGS)
        embed = discord.Embed(title="Baby Rearing", description="The baby is crying. **Guess what care it needs.**", color=discord.Color.purple())
        embed.set_image(url=img)
        view = ArkImprintView()
        msg = await channel.send(embed=embed, view=view)
        return msg
    elif game_type == 5:
        data = random.choice(DATA_ALPHAS)
        embed = discord.Embed(title=f"⚠️ {data['name'].upper()} DETECTED", description=f"Do you risk attacking it?\n\n🟢 **Reward:** +{data['win']} Points\n🔴 **Risk:** -{data['loss']} Points\n🎲 **Win Chance:** {int(data['chance']*100)}%", color=data['color'])
        embed.set_image(url=data["url"])
        view = ArkAlphaView(data["win"], data["loss"], data["chance"])
        msg = await channel.send(embed=embed, view=view)
        return msg
    elif game_type == 6:
        data = random.choice(DATA_POKEMON)
        embed = discord.Embed(title="What type is this Pokémon?", description=f"Guess the type of **{data['name']}**.", color=discord.Color.gold())
        embed.set_image(url=data["url"])
        view = PokemonVisualView(data["type"], data["name"])
        msg = await channel.send(embed=embed, view=view)
        return msg

@tasks.loop(minutes=5)
async def minigames_auto_loop():
    if not bot.is_ready(): return
    global last_minigame_message
    try:
        channel = bot.get_channel(MINIGAMES_CHANNEL_ID)
        if not channel: return
        
        if last_minigame_message:
            try: await last_minigame_message.edit(view=None)
            except: pass 
        
        last_minigame_message = await spawn_game(channel)
    except Exception as e:
        print(f"Error Minigame Loop: {e}")

# 🔥 ARREGLO DE LOOP (Espera a que el bot este listo)
@minigames_auto_loop.before_loop
async def before_minigames_loop():
    await bot.wait_until_ready()

# ==========================================
# 🏦 VAULT SYSTEM
# ==========================================
class VaultModal(discord.ui.Modal, title="🔐 SECURITY OVERRIDE"):
    code_input = discord.ui.TextInput(label="INSERT PIN CODE", placeholder="####", min_length=4, max_length=4, required=True)
    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        current_time = time.time()
        if user_id in user_cooldowns:
            if (time.time() - user_cooldowns[user_id]) < 15:
                # 🔥 EMOJI RED CLOCK
                await interaction.response.send_message(f"{EMOJI_VAULT_WAIT} Wait...", ephemeral=True)
                return
        user_cooldowns[user_id] = current_time
        if not vault_state["active"]:
            await interaction.response.send_message("❌ Event ended.", ephemeral=True)
            return
        if self.code_input.value == vault_state["code"]:
            vault_state["active"] = False 
            if vault_state["hints_task"]: vault_state["hints_task"].cancel()
            add_points_to_user(interaction.user.id, 2000)
            
            # 🔥 BLOQUEAR BOTÓN ORIGINAL 🔥
            try:
                ch = interaction.guild.get_channel(VAULT_CHANNEL_ID)
                original_msg = await ch.fetch_message(vault_state["message_id"])
                
                # Crear vista con botón deshabilitado
                view = VaultView()
                for child in view.children:
                    child.disabled = True
                    child.label = "VAULT OPENED"
                    child.style = discord.ButtonStyle.secondary
                
                await original_msg.edit(view=view)
            except: pass

            embed = discord.Embed(title=f"{EMOJI_PARTY_NEW} VAULT CRACKED! {EMOJI_PARTY_NEW}", color=0xFFD700)
            embed.description = (
                f"{EMOJI_VAULT_WINNER_CROWN} **WINNER:** {interaction.user.mention}\n"
                f"{EMOJI_VAULT_CODE_ICON} **CODE:** `{vault_state['code']}`\n"
                f"{EMOJI_GIFT_NEW} **LOOT:** {vault_state['prize']}\n"
                f"{EMOJI_POINTS} **BONUS:** +2000"
            )
            embed.set_footer(text="HELL SYSTEM • Vault Event")
            embed.set_image(url="https://media1.tenor.com/m/X9kF3Qv1mJAAAAAC/open-safe.gif")
            if interaction.channel: await interaction.channel.send(embed=embed)
            
            # AQUI YA NO MANDAMOS NADA EFIMERO, SOLO EL WINNER PUBLICO
        else:
            # 🔥 EMOJI WARN
            await interaction.response.send_message(f"{EMOJI_VAULT_DENIED} **ACCESS DENIED.**", ephemeral=True)

class VaultView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="ATTEMPT HACK", style=discord.ButtonStyle.danger, emoji="☠️", custom_id="vault_btn")
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not vault_state["active"]:
             await interaction.response.send_message("❌ Event ended. (Start new one with /event_vault)", ephemeral=True)
             return
        await interaction.response.send_modal(VaultModal())

async def manage_vault_hints(channel, message, code):
    try:
        await asyncio.sleep(18000)
        if not vault_state["active"]: return
        embed = message.embeds[0]
        embed.set_field_at(0, name="📡 LEAKED DATA", value=f"`{code[:2]}##`", inline=True)
        await message.edit(embed=embed)
        await asyncio.sleep(68400)
        if not vault_state["active"]: return
        embed.set_field_at(0, name="📡 LEAKED DATA", value=f"`{code[:3]}#`", inline=True)
        await message.edit(embed=embed)
    except: pass

# ==========================================
# 🔘 ROLES
# ==========================================
class RoleButton(discord.ui.Button):
    def __init__(self, label, role_id):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, custom_id=f"role_{role_id}")
        self.role_id = role_id
    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if role:
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(f"➖ Removed {role.name}", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"➕ Added {role.name}", ephemeral=True)

class RolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for l, r in ROLES_CONFIG.items(): self.add_item(RoleButton(l, r))

# ==========================================
# ⚡ COMMANDS
# ==========================================
@bot.tree.command(name="add_points", description="ADMIN: Add points")
async def add_points(interaction: discord.Interaction, usuario: discord.Member, cantidad: int):
    if not interaction.user.guild_permissions.administrator: return
    nb = add_points_to_user(usuario.id, cantidad)
    await interaction.response.send_message(f"✅ {usuario.mention} +{cantidad} (Total: {nb})")

@bot.tree.command(name="remove_points", description="ADMIN: Remove points")
async def remove_points(interaction: discord.Interaction, usuario: discord.Member, cantidad: int):
    if not interaction.user.guild_permissions.administrator: return
    remove_points_from_user(usuario.id, cantidad)
    await interaction.response.send_message(f"✅ {usuario.mention} -{cantidad}")

@bot.command(name="points")
async def check_points(ctx):
    bal = get_user_points(ctx.author.id)
    msg = await ctx.send(f"💰 {ctx.author.mention}: **{bal}** Points.")
    try: 
        await ctx.message.delete()
        await asyncio.sleep(10)
        await msg.delete()
    except: pass

@bot.command(name="recipes")
async def show_recipes(ctx):
    embed = discord.Embed(title=f"{EMOJI_BLOOD} **HELL RECIPES** {EMOJI_BLOOD}", color=0x990000)
    embed.description = "Custom crafting recipes for this season."
    embed.set_image(url="https://media.discordapp.net/attachments/1329487785857650748/1335660249704693760/recipes.png") 
    
    recipes = [
        ("🍰 Sweet Veg. Cake", "50 Cementing Paste"),
        ("🥚 Kibble", "1 Fiber"),
        ("🎨 Colors", "1 Thatch"),
        ("🥩 Shadow Steak", "1 Raw Meat"),
        ("🧠 Mindwipe Tonic", "200 Mejoberries"),
        ("💉 Medical Brew", "1 Tintoberry"),
        ("⚔️ Battle Tartare", "10 Crystal"),
        ("🍺 Beer Jar", "5 Thatch"),
        ("🌵 Cactus Broth", "50 Stone"),
        ("🍄 Mushroom Brew", "5 Aquatic Mushroom"),
        ("🌶️ Focal Chili", "100 Raw Metal"),
        ("🦗 Bug Repellent", "1 Chitin/Keratin")
    ]

    for name, ingredients in recipes:
        embed.add_field(name=f"**{name}**", value=f"{HELL_ARROW} {ingredients}", inline=True)

    embed.set_footer(text="Hell System • Crafting")
    await ctx.send(embed=embed)

@bot.tree.command(name="event_vault")
async def event_vault(interaction: discord.Interaction, code: str, prize: str):
    if not interaction.user.guild_permissions.administrator: return
    ch = bot.get_channel(VAULT_CHANNEL_ID)
    if not ch: return
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(title=f"{EMOJI_BLOOD} **VAULT DETECTED**", description=f"Crack the PIN.\nReward: {prize}", color=0x8a0404)
    embed.add_field(name="📡 LEAKED DATA", value=f"`{code[0]}###`", inline=True)
    embed.set_image(url=VAULT_IMAGE_URL)
    msg = await ch.send(embed=embed, view=VaultView())
    vault_state.update({"active": True, "code": code, "prize": prize, "message_id": msg.id})
    if vault_state["hints_task"]: vault_state["hints_task"].cancel()
    vault_state["hints_task"] = asyncio.create_task(manage_vault_hints(ch, msg, code))
    await interaction.followup.send("✅ Started")

@bot.tree.command(name="start_giveaway")
async def start_giveaway(interaction: discord.Interaction, time_str: str, prize: str, winners: int = 1):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ No tienes permisos.", ephemeral=True)
        return

    seconds = convert_time(time_str)
    if seconds < 0:
        await interaction.response.send_message("❌ Tiempo inválido. Usa formato `3d`, `10m`, `3d 10h`.", ephemeral=True)
        return

    is_sponsor_channel = (interaction.channel_id == GIVEAWAY_CHANNEL_ID)
    if is_sponsor_channel:
        embed_color = 0x990000
        embed_title = f"{EMOJI_FIRE_ANIM} HELL SPONSOR GIVEAWAY {EMOJI_FIRE_ANIM}"
        footer_text = "⚠️ ANTI-CHEAT ACTIVE: Remove name tag = Auto-Kick"
    else:
        embed_color = 0x00FF00
        embed_title = f"{EMOJI_PARTY_NEW} GIVEAWAY"
        footer_text = "Hell System • Giveaway"

    end_timestamp = int(time.time() + seconds)
    
    embed = discord.Embed(title=embed_title, color=embed_color)
    embed.description = (
        f"{EMOJI_GIFT_NEW} **Prize:** {prize}\n"
        f"{EMOJI_CLOCK_NEW} **Ends:** <t:{end_timestamp}:R>\n" 
        f"👑 **Winners:** {winners}\n\n"
        f"React with {EMOJI_PARTY_NEW} to enter!"
    )
    embed.set_footer(text=footer_text)

    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    await msg.add_reaction(EMOJI_PARTY_NEW)

    giveaways_data[str(msg.id)] = {
        "channel_id": interaction.channel_id,
        "end_time": end_timestamp,
        "prize": prize,
        "winners": winners
    }
    await save_giveaways_db()
    
    bot.loop.create_task(run_giveaway_timer(
        interaction.channel_id, 
        msg.id, 
        end_timestamp, 
        prize, 
        winners
    ))

@bot.tree.command(name="finish_polls", description="Publica resultados SOLO del día de la última encuesta.")
async def finish_polls(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
    except:
        return 

    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("❌ No tienes permisos.", ephemeral=True)
        return

    polls_channel = bot.get_channel(POLLS_CHANNEL_ID)
    if not polls_channel:
        await interaction.followup.send(f"❌ Canal {POLLS_CHANNEL_ID} no encontrado.", ephemeral=True)
        return

    # 1. Obtener la fecha de referencia del ÚLTIMO mensaje del canal
    target_date = None
    async for last_msg in polls_channel.history(limit=1):
        target_date = last_msg.created_at.date()
    
    if not target_date:
        await interaction.followup.send("⚠️ El canal está vacío.", ephemeral=True)
        return

    results_list = []
    
    # 2. Buscar solo mensajes que coincidan con esa fecha
    # Limitamos a 50 para no saturar, pero pararemos antes si cambia la fecha
    async for message in polls_channel.history(limit=50):
        # Si el mensaje es de un día diferente al último, PARAMOS de buscar
        if message.created_at.date() != target_date:
            break 

        if not message.content or not message.reactions: continue 
        # Filtro para ignorar mensajes de separacion "----"
        if "----" in message.content and len(message.content) < 30: continue

        # Buscar ganador
        try:
            winner_reaction = max(message.reactions, key=lambda r: r.count)
        except:
            continue # Si no hay reacciones, saltamos

        # Solo si tiene votos (count > 1 porque el bot cuenta como 1 a veces)
        if winner_reaction.count >= 1: 
            question, answer_text = parse_poll_result(message.content, winner_reaction.emoji)
            # Formato FINAL: Flecha + Negrita (sin subrayar) + Respuesta
            line = f"{HELL_ARROW} **{question}** : {answer_text}"
            results_list.append(line)

    if not results_list:
        await interaction.followup.send(f"⚠️ No encontré encuestas válidas para la fecha {target_date}.", ephemeral=True)
        return

    # 3. Invertir la lista para que salga de la primera a la última
    results_list.reverse()
    
    full_content = "\n".join(results_list)
    
    # Cabecera
    header = f"📢 **POLL RESULTS**\n📅 {target_date}\n\n"
    final_text = header + full_content

    # 4. Enviar (Gestión de límite de 4096 caracteres)
    if len(final_text) <= 4000:
        embed = discord.Embed(description=final_text, color=0x990000)
        embed.set_footer(text="Hell System polls")
        await interaction.followup.send(embed=embed)
    else:
        # Si es MUY largo, cortamos (aunque al filtrar por día es raro que pase)
        chunks = [final_text[i:i+4000] for i in range(0, len(final_text), 4000)]
        for i, chunk in enumerate(chunks):
            embed = discord.Embed(description=chunk, color=0x990000)
            if i == 0:
                embed.set_footer(text="Hell System polls (Parte 1)")
            else:
                embed.set_footer(text=f"Hell System polls (Parte {i+1})")
            await interaction.followup.send(embed=embed)

# ==========================================
# 🛡️ EVENTS
# ==========================================
@bot.event
async def on_ready():
    print(f"🔥 HELL SYSTEM ONLINE: {bot.user}")
    try: await bot.tree.sync()
    except: pass
    
    # 🔴 HERRAMIENTA DE EMOJIS (SOLO IMPRIME EN CONSOLA)
    print("\n--- LISTA DE EMOJIS DEL SERVIDOR ---")
    for guild in bot.guilds:
        print(f"Servidor: {guild.name}")
        for emoji in guild.emojis:
            print(f"Nombre: {emoji.name} | ID: {emoji.id} | Código: <:{emoji.name}:{emoji.id}>")
    print("------------------------------------\n")

    bot.loop.create_task(backup_points_task())
    if not dino_game_loop.is_running(): dino_game_loop.start()
    if not minigames_auto_loop.is_running(): minigames_auto_loop.start()
    bot.add_view(RolesView())
    bot.add_view(VaultView())

    async def check_support_roles():
        while True:
            guild = bot.guilds[0] if bot.guilds else None
            if guild:
                role = guild.get_role(SUPPORT_ROLE_ID)
                if role:
                    for member in guild.members:
                        name_check = member.global_name if member.global_name else member.name
                        if name_check and SUPPORT_TEXT.lower() in name_check.lower():
                            if role not in member.roles:
                                try: await member.add_roles(role)
                                except: pass
                        else:
                            if role in member.roles:
                                try: await member.remove_roles(role)
                                except: pass
            await asyncio.sleep(60)
    bot.loop.create_task(check_support_roles())

    for guild in bot.guilds:
        shop_channel = discord.utils.get(guild.text_channels, name=SHOP_CHANNEL_NAME)
        if not shop_channel:
            try:
                overwrites = {guild.default_role: discord.PermissionOverwrite(send_messages=False), guild.me: discord.PermissionOverwrite(send_messages=True)}
                shop_channel = await guild.create_text_channel(SHOP_CHANNEL_NAME, overwrites=overwrites)
            except: pass
        if shop_channel:
            last_msg = None
            async for m in shop_channel.history(limit=1): last_msg = m
            is_shop_ok = False
            if last_msg and last_msg.author == bot.user and last_msg.embeds:
                if "BLACK MARKET SHOP" in (last_msg.embeds[0].title or ""): is_shop_ok = True
            if not is_shop_ok:
                await shop_channel.purge(limit=5)
                embed = discord.Embed(title=f"{EMOJI_REWARD} **BLACK MARKET SHOP** {EMOJI_REWARD}", color=0x9900FF)
                embed.description = f"Earn {EMOJI_POINTS} by winning minigames.\n**⚠️ OPEN A TICKET TO BUY ⚠️**\n━━━━━━━━━━━━━━━━━━━━━━━━"
                for item in SHOP_ITEMS:
                    embed.add_field(name=f"📦 {item['name']}", value=f"{EMOJI_POINTS} **{item['price']}**\n*{item['desc']}*", inline=False)
                embed.set_footer(text="Hell System • Economy")
                await shop_channel.send(embed=embed)

    c_ch = bot.get_channel(CMD_CHANNEL_ID)
    if c_ch:
        async for m in c_ch.history(limit=10):
            if m.author == bot.user:
                if m.embeds and "SERVER COMMANDS" in (m.embeds[0].title or ""):
                    pass 
                else:
                    await m.delete() 
        menu_exists = False
        async for m in c_ch.history(limit=10):
             if m.author == bot.user and m.embeds and "SERVER COMMANDS" in (m.embeds[0].title or ""):
                 menu_exists = True
                 break
        if not menu_exists:
            embed = discord.Embed(title="🛠️ **SERVER COMMANDS**", color=0x990000)
            embed.add_field(name="👤 **PLAYER COMMANDS**", value=f"{HELL_ARROW} **!recipes**\n{HELL_ARROW} **!points**\n{HELL_ARROW} **.suggest <text>**\n{HELL_ARROW} **/whitelistme**", inline=False)
            embed.set_footer(text="HELL SYSTEM • Commands")
            await c_ch.send(embed=embed)

@bot.event
async def on_member_update(before, after):
    name_check = after.global_name if after.global_name else after.name
    if not name_check: return
    role = after.guild.get_role(SUPPORT_ROLE_ID)
    if not role: return

    if SUPPORT_TEXT.lower() in name_check.lower():
        if role not in after.roles:
            try: await after.add_roles(role)
            except: pass
    else:
        if role in after.roles:
            try: await after.remove_roles(role)
            except: pass
            try:
                ga_channel = after.guild.get_channel(GIVEAWAY_CHANNEL_ID)
                if ga_channel:
                    async for msg in ga_channel.history(limit=10):
                        await msg.remove_reaction(EMOJI_PARTY_NEW, after)
            except: pass

@bot.event
async def on_message(message):
    if message.channel.id == CMD_CHANNEL_ID:
        if message.author.bot:
            if message.author == bot.user and message.embeds:
                if "SERVER COMMANDS" in (message.embeds[0].title or ""):
                    return 
            await message.delete(delay=120)
            return

        if message.type == discord.MessageType.chat_input_command:
            return 

        if message.content.startswith('/'):
            return

        if message.content.startswith(('!', '.')):
             await bot.process_commands(message)
             try: await message.delete(delay=5)
             except: pass
             return
        
        try: await message.delete() 
        except: pass
        return

    if message.channel.id == SUGGEST_CHANNEL_ID:
        if message.content.startswith(".suggest"):
            txt = message.content[8:].strip()
            if txt:
                try: await message.delete() 
                except: pass
                embed = discord.Embed(description=f"**{txt}**", color=0xffaa00)
                embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
                msg = await message.channel.send(embed=embed)
                await msg.add_reaction(CHECK_ICON)
                await msg.add_reaction(CROSS_ICON)
        else:
            try: await message.delete() 
            except: pass
        return

    await bot.process_commands(message)

if __name__ == "__main__":
    if TOKEN: bot.run(TOKEN)
