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
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==========================================
# 🚑 FAKE WEB SERVER
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
# 🔐 CONFIGURACIÓN
# ==========================================
TOKEN = os.environ.get("DISCORD_TOKEN")

# IDs CANALES
GIVEAWAY_CHANNEL_ID = 1449849645495746803 
POLLS_CHANNEL_ID = 1449083865862770819      
CMD_CHANNEL_ID = 1449346777659609288
ROLES_CHANNEL_ID = 1449083960578670614
SUGGEST_CHANNEL_ID = 1449346646465839134
VAULT_CHANNEL_ID = 1450244608817762465
DINO_CHANNEL_ID = 1450244689285353544 
MINIGAMES_CHANNEL_ID = 1450244729848598618

SHOP_CHANNEL_NAME = "「🔥」hell-store"

# ==========================================
# 🖼️ DATOS (IMÁGENES Y CONFIGURACIÓN)
# ==========================================
IMG_ARK_DROP = "https://ark.wiki.gg/images/e/e3/Supply_Crate_Level_60.png"

DATA_TAMING = [
    {"url": "https://ark.wiki.gg/images/e/e6/Raptor.png", "food": "Carne", "name": "Raptor"},
    {"url": "https://ark.wiki.gg/images/0/03/Rex.png", "food": "Carne", "name": "T-Rex"},
    {"url": "https://ark.wiki.gg/images/7/78/Carno.png", "food": "Carne", "name": "Carnotaurus"},
    {"url": "https://ark.wiki.gg/images/a/a8/Argentavis.png", "food": "Carne", "name": "Argentavis"},
    {"url": "https://ark.wiki.gg/images/2/2e/Pteranodon.png", "food": "Carne", "name": "Pteranodon"},
    {"url": "https://ark.wiki.gg/images/c/c1/Allosaurus.png", "food": "Carne", "name": "Allosaurus"},
    {"url": "https://ark.wiki.gg/images/4/47/Spino.png", "food": "Carne", "name": "Spinosaurus"},
    {"url": "https://ark.wiki.gg/images/9/9e/Giganotosaurus.png", "food": "Carne", "name": "Giganotosaurus"},
    {"url": "https://ark.wiki.gg/images/d/d8/Thylacoleo.png", "food": "Carne", "name": "Thylacoleo"},
    {"url": "https://ark.wiki.gg/images/4/4c/Yutyrannus.png", "food": "Carne", "name": "Yutyrannus"},
    {"url": "https://ark.wiki.gg/images/2/2f/Triceratops.png", "food": "Bayas", "name": "Triceratops"},
    {"url": "https://ark.wiki.gg/images/1/12/Stegosaurus.png", "food": "Bayas", "name": "Stegosaurus"},
    {"url": "https://ark.wiki.gg/images/0/07/Brontosaurus.png", "food": "Bayas", "name": "Brontosaurus"},
    {"url": "https://ark.wiki.gg/images/5/5a/Parasaur.png", "food": "Bayas", "name": "Parasaur"},
    {"url": "https://ark.wiki.gg/images/f/f3/Ankylosaurus.png", "food": "Bayas", "name": "Ankylosaurus"},
    {"url": "https://ark.wiki.gg/images/c/c7/Doedicurus.png", "food": "Bayas", "name": "Doedicurus"},
    {"url": "https://ark.wiki.gg/images/a/a9/Iguanodon.png", "food": "Bayas", "name": "Iguanodon"},
    {"url": "https://ark.wiki.gg/images/3/38/Therizinosaurus.png", "food": "Bayas", "name": "Therizinosaurus"},
    {"url": "https://ark.wiki.gg/images/4/45/Mammoth.png", "food": "Bayas", "name": "Mammoth"},
    {"url": "https://ark.wiki.gg/images/3/36/Phiomia.png", "food": "Bayas", "name": "Phiomia"},
]

DATA_CRAFTING = [
    {"url": "https://ark.wiki.gg/images/9/9a/Metal_Ingot.png", "mat": "Metal", "name": "Lingote de Metal"},
    {"url": "https://ark.wiki.gg/images/3/30/Flak_Chestpiece.png", "mat": "Metal", "name": "Pechera de Metal"},
    {"url": "https://ark.wiki.gg/images/7/72/Longneck_Rifle.png", "mat": "Metal", "name": "Rifle de Largo Alcance"},
    {"url": "https://ark.wiki.gg/images/3/32/Metal_Pick.png", "mat": "Metal", "name": "Pico de Metal"},
    {"url": "https://ark.wiki.gg/images/5/54/Industrial_Forge.png", "mat": "Metal", "name": "Forja Industrial"},
    {"url": "https://ark.wiki.gg/images/b/b9/Stone_Wall.png", "mat": "Piedra/Madera", "name": "Pared de Piedra"},
    {"url": "https://ark.wiki.gg/images/e/e3/Mortar_and_Pestle.png", "mat": "Piedra/Madera", "name": "Mortero"},
    {"url": "https://ark.wiki.gg/images/1/1c/Campfire.png", "mat": "Piedra/Madera", "name": "Hoguera"},
    {"url": "https://ark.wiki.gg/images/7/7c/Wooden_Foundation.png", "mat": "Piedra/Madera", "name": "Cimiento de Madera"},
    {"url": "https://ark.wiki.gg/images/1/1a/Stone_Arrow.png", "mat": "Piedra/Madera", "name": "Flecha de Piedra"},
    {"url": "https://ark.wiki.gg/images/b/b4/Hide_Shirt.png", "mat": "Piel/Fibra", "name": "Camisa de Piel"},
    {"url": "https://ark.wiki.gg/images/a/a5/Cloth_Hat.png", "mat": "Piel/Fibra", "name": "Sombrero de Tela"},
    {"url": "https://ark.wiki.gg/images/6/6d/Simple_Bed.png", "mat": "Piel/Fibra", "name": "Cama Simple"},
    {"url": "https://ark.wiki.gg/images/8/88/Saddle.png", "mat": "Piel/Fibra", "name": "Montura Genérica"},
    {"url": "https://ark.wiki.gg/images/c/c2/Bola.png", "mat": "Piel/Fibra", "name": "Boleadora"},
    {"url": "https://ark.wiki.gg/images/9/92/C4_Charge.png", "mat": "Avanzado", "name": "C4"},
    {"url": "https://ark.wiki.gg/images/f/f4/Assault_Rifle.png", "mat": "Avanzado", "name": "Rifle de Asalto"},
    {"url": "https://ark.wiki.gg/images/e/e8/Heavy_Auto_Turret.png", "mat": "Avanzado", "name": "Torreta Pesada"},
    {"url": "https://ark.wiki.gg/images/2/26/Cryopod.png", "mat": "Avanzado", "name": "Cryopod"},
    {"url": "https://ark.wiki.gg/images/3/37/Advanced_Rifle_Bullet.png", "mat": "Avanzado", "name": "Bala de Rifle Avanzado"},
]

DATA_BREEDING_IMGS = [
    "https://ark.wiki.gg/images/e/e3/Fertilized_Rex_Egg.png",
    "https://ark.wiki.gg/images/5/5d/Fertilized_Giganotosaurus_Egg.png",
    "https://ark.wiki.gg/images/a/a8/Fertilized_Wyvern_Egg_%28Fire%29.png",
    "https://ark.wiki.gg/images/f/f2/Fertilized_Rock_Drake_Egg.png",
    "https://ark.wiki.gg/images/c/c8/Fertilized_Spino_Egg.png",
    "https://ark.wiki.gg/images/9/9d/Fertilized_Bronto_Egg.png",
    "https://ark.wiki.gg/images/0/0e/Fertilized_Trike_Egg.png",
    "https://ark.wiki.gg/images/b/b0/Fertilized_Stego_Egg.png",
    "https://ark.wiki.gg/images/2/22/Fertilized_Ankylo_Egg.png",
    "https://ark.wiki.gg/images/d/d4/Fertilized_Raptor_Egg.png",
    "https://ark.wiki.gg/images/2/2b/Fertilized_Argentavis_Egg.png",
    "https://ark.wiki.gg/images/9/90/Fertilized_Pteranodon_Egg.png",
    "https://ark.wiki.gg/images/e/e9/Fertilized_Quetzal_Egg.png",
    "https://ark.wiki.gg/images/3/31/Fertilized_Therizino_Egg.png",
    "https://ark.wiki.gg/images/a/a5/Fertilized_Yutyrannus_Egg.png",
    "https://ark.wiki.gg/images/c/c2/Fertilized_Allosaurus_Egg.png",
    "https://ark.wiki.gg/images/8/8e/Fertilized_Baryonyx_Egg.png",
    "https://ark.wiki.gg/images/6/61/Fertilized_Carnotaurus_Egg.png",
    "https://ark.wiki.gg/images/0/04/Fertilized_Deinonychus_Egg.png",
    "https://ark.wiki.gg/images/3/39/Fertilized_Magmasaur_Egg.png"
]

# === NUEVA CONFIGURACIÓN ALPHA POR NIVELES ===
DATA_ALPHAS = [
    # Nivel FÁCIL (70% win, 300 pts)
    {"url": "https://ark.wiki.gg/images/5/53/Alpha_Raptor.png", "name": "Alpha Raptor", "win": 300, "loss": 300, "chance": 0.70, "color": discord.Color.green()},
    {"url": "https://ark.wiki.gg/images/e/eb/Alpha_Carno.png", "name": "Alpha Carno", "win": 300, "loss": 300, "chance": 0.70, "color": discord.Color.green()},
    
    # Nivel NORMAL (50% win, 600 pts)
    {"url": "https://ark.wiki.gg/images/0/03/Alpha_T-Rex.png", "name": "Alpha T-Rex", "win": 600, "loss": 600, "chance": 0.50, "color": discord.Color.gold()},
    {"url": "https://ark.wiki.gg/images/4/4d/Alpha_Megalodon.png", "name": "Alpha Megalodon", "win": 600, "loss": 600, "chance": 0.50, "color": discord.Color.gold()},
    
    # Nivel DIFÍCIL (40% win, 1200 pts)
    {"url": "https://ark.wiki.gg/images/a/a2/Alpha_Fire_Wyvern.png", "name": "Alpha Wyvern", "win": 1200, "loss": 1200, "chance": 0.40, "color": discord.Color.red()},
    {"url": "https://ark.wiki.gg/images/e/e3/Alpha_Basilisk.png", "name": "Alpha Basilisk", "win": 1200, "loss": 1200, "chance": 0.40, "color": discord.Color.red()},
    {"url": "https://ark.wiki.gg/images/d/db/Alpha_Surface_Reaper_King.png", "name": "Alpha Reaper", "win": 1200, "loss": 1200, "chance": 0.40, "color": discord.Color.red()},

    # Nivel EXTREMO (30% win, 2500 pts)
    {"url": "https://ark.wiki.gg/images/f/f6/Alpha_Mosasaur.png", "name": "Alpha Mosasaur", "win": 2500, "loss": 2500, "chance": 0.30, "color": discord.Color.purple()},
    {"url": "https://ark.wiki.gg/images/8/85/Alpha_Tusoteuthis.png", "name": "Alpha Tusoteuthis", "win": 2500, "loss": 2500, "chance": 0.30, "color": discord.Color.purple()},
]

DATA_POKEMON = [
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png", "type": "Fuego", "name": "Charizard"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/59.png", "type": "Fuego", "name": "Arcanine"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/257.png", "type": "Fuego", "name": "Blaziken"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/4.png", "type": "Fuego", "name": "Charmander"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/38.png", "type": "Fuego", "name": "Ninetales"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/136.png", "type": "Fuego", "name": "Flareon"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/9.png", "type": "Agua", "name": "Blastoise"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/130.png", "type": "Agua", "name": "Gyarados"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/134.png", "type": "Agua", "name": "Vaporeon"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", "type": "Agua", "name": "Squirtle"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/55.png", "type": "Agua", "name": "Golduck"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/245.png", "type": "Agua", "name": "Suicune"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/260.png", "type": "Agua", "name": "Swampert"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/3.png", "type": "Planta", "name": "Venusaur"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png", "type": "Planta", "name": "Bulbasaur"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/154.png", "type": "Planta", "name": "Meganium"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/254.png", "type": "Planta", "name": "Sceptile"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/45.png", "type": "Planta", "name": "Vileplume"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/152.png", "type": "Planta", "name": "Chikorita"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/251.png", "type": "Planta", "name": "Celebi"},
]

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

EMOJI_DINO_TITLE = "<:pikachu_culon:1450624552827752479>" 
EMOJI_REWARD     = "<a:Gift_hell:1450624953723654164>"     
EMOJI_CORRECT    = "<a:Good_2:930098652804952074>"         
EMOJI_WINNER     = "<a:party:1450625235383488649>"         
EMOJI_ANSWER     = "<a:greenarrow:1450625398051311667>"    
EMOJI_POINTS     = "<:Pokecoin:1450625492309901495>"       

HELL_ARROW = "<a:hell_arrow:1211049707128750080>" 
NOTIFICATION_ICON = "<a:notification:1275469575638614097>"
CHECK_ICON = "<a:Check_hell:1450255850508779621>" 
CROSS_ICON = "<a:cruz_hell:1450255934273355918>" 
VAULT_IMAGE_URL = "https://ark.wiki.gg/images/thumb/8/88/Vault.png/300px-Vault.png"
EMOJI_BLOOD = "<a:emoji_75:1317875418782498858>" 
EMOJI_CODE  = "<a:emoji_68:1328804237546881126>" 

SUPPORT_TEXT = "! HELL WIPES FRIDAY 100€"
SUPPORT_ROLE_ID = 1336477737594130482

SHOP_ITEMS = [
    {"name": "Starter Kit", "price": 3000, "desc": "Full Metal Kit + Cryos"},
    {"name": "Dino Color Change", "price": 7500, "desc": "Change color of 1 Dino"},
    {"name": "Turret Filler (1x)", "price": 12000, "desc": "Fill 1 Turret Box"},
    {"name": "Base Rename", "price": 20000, "desc": "Rename Tribe/Base"},
    {"name": "VIP Bronze (3 Days)", "price": 50000, "desc": "Trial VIP Role"}
]

ARK_DINOS = [
    "Tyrannosaurus", "Giganotosaurus", "Raptor", "Argentavis", "Pteranodon", 
    "Triceratops", "Stegosaurus", "Spinosaurus", "Allosaurus", "Ankylosaurus", 
    "Brontosaurus", "Carnotaurus", "Dilophosaurus", "Dimorphodon", "Direwolf", 
    "Doedicurus", "Dunkleosteus", "Gallimimus", "Griffin", "Ichthyosaurus", 
    "Iguanodon", "Kairuku", "Kaprosuchus", "Lystrosaurus", "Mammoth", 
    "Megalodon", "Megatherium", "Moschops", "Oviraptor", "Parasaur", 
    "Pegomastax", "Phiomia", "Procoptodon", "Quetzal", "Sarcosuchus", 
    "Tapejara", "Terror Bird", "Therizinosaurus", "Thylacoleo", "Titanoboa", 
    "Troodon", "Wyvern", "Yutyrannus", "Velonasaur", "Snow Owl", "Managarmr"
]

# --- ESTADOS (GLOBALES) ---
vault_state = {
    "active": False,
    "code": None,
    "prize": None,
    "message_id": None,
    "hints_task": None
}
user_cooldowns = {} 

# VARIABLES PARA CONTROLAR ÚLTIMO JUEGO ACTIVO
last_minigame_message = None 

# --- SISTEMA DE PUNTOS ---
POINTS_FILE = "points.json"

def load_points():
    if not os.path.exists(POINTS_FILE):
        return {}
    try:
        with open(POINTS_FILE, "r") as f:
            return json.load(f)
    except: return {}

def save_points(data):
    with open(POINTS_FILE, "w") as f:
        json.dump(data, f)

def add_points_to_user(user_id, amount):
    data = load_points()
    uid = str(user_id)
    if uid not in data: data[uid] = 0
    data[uid] += amount
    save_points(data)
    return data[uid]

def remove_points_from_user(user_id, amount):
    data = load_points()
    uid = str(user_id)
    if uid not in data: data[uid] = 0
    if data[uid] < amount: 
        data[uid] = 0 
    else:
        data[uid] -= amount
    save_points(data)
    return True

def get_user_points(user_id):
    data = load_points()
    return data.get(str(user_id), 0)

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
# 🦖 MINIGAME: WHO IS THE DINO (SCRAMBLE)
# ==========================================

class DinoModal(discord.ui.Modal, title="🦖 WHO IS THAT DINO?"):
    answer_input = discord.ui.TextInput(label="Dino Name", placeholder="Enter name...", required=True)

    def __init__(self, correct_answer):
        super().__init__()
        self.correct_answer = correct_answer
        self.view_ref = None

    async def on_submit(self, interaction: discord.Interaction):
        guess = self.answer_input.value.strip().lower()
        
        # Anti-Doble Click Logic (Si alguien ya ganó, el juego se cierra antes)
        if self.view_ref and self.view_ref.grabbed:
             await interaction.response.send_message("❌ Alguien fue más rápido.", ephemeral=True)
             return

        if guess == self.correct_answer.lower():
            if self.view_ref: self.view_ref.grabbed = True # Bloqueo global
            
            points_won = 150 
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
        self.grabbed = False # Candado

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
    if not bot.is_ready(): return

    try:
        channel = bot.get_channel(DINO_CHANNEL_ID)
        if not channel: return

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
        await channel.send(embed=embed, view=view)

    except Exception as e:
        print(f"Error en Dino Loop: {e}")

# ==========================================
# 🎮 CLASES MINIGAMES (Lógica BLINDADA)
# ==========================================

# 1. ARK: DROP ROJO
class ArkDropView(discord.ui.View):
    def __init__(self): 
        super().__init__(timeout=None)
        self.grabbed = False
        
    @discord.ui.button(label="CLAIM DROP", style=discord.ButtonStyle.danger, emoji="🎁", custom_id="drop_claim_btn")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.grabbed: return # Si ya se pulsó, ignorar
        self.grabbed = True
        
        try:
            button.label = f"Loot de {interaction.user.name}"
            button.style = discord.ButtonStyle.secondary
            button.disabled = True
            add_points_to_user(interaction.user.id, 500)
            embed = interaction.message.embeds[0]
            embed.color = discord.Color.dark_grey()
            embed.set_footer(text=f"Reclamado por: {interaction.user.display_name} (+500 Puntos)")
            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.followup.send(f"🔴 **{interaction.user.mention}** abrió el Drop Rojo y ganó 500 puntos!", ephemeral=False)
            self.stop()
        except Exception: pass

# 2. ARK: TAMEO
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
                await interaction.response.send_message(f"🦕 **¡TAMEADO!** {interaction.user.mention} le dio {food} al {self.dino_name} (+200 pts).", ephemeral=False)
                for child in self.children: child.disabled = True
                await interaction.message.edit(view=self)
                self.stop()
            else:
                await interaction.response.send_message(f"❌ El {self.dino_name} rechaza {food}. ¡Huyó!", ephemeral=False)
                for child in self.children: child.disabled = True
                await interaction.message.edit(view=self)
                self.stop()
        except Exception: pass

    @discord.ui.button(label="Carne Cruda 🥩", style=discord.ButtonStyle.danger, custom_id="tm_meat")
    async def meat(self, interaction: discord.Interaction, button: discord.ui.Button): await self.feed(interaction, "Carne")
    @discord.ui.button(label="Mejoberries 🫐", style=discord.ButtonStyle.primary, custom_id="tm_berry")
    async def berries(self, interaction: discord.Interaction, button: discord.ui.Button): await self.feed(interaction, "Bayas")

# 3. ARK: CRAFTING
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
                add_points_to_user(interaction.user.id, 150)
                await interaction.response.send_message(f"🔨 **¡Correcto!** {interaction.user.mention} fabricó el objeto (+150 pts).", ephemeral=False)
                for child in self.children: child.disabled = True
                await interaction.message.edit(view=self)
                self.stop()
            else:
                await interaction.response.send_message("❌ Material incorrecto. Se rompió.", ephemeral=False)
                for child in self.children: child.disabled = True
                await interaction.message.edit(view=self)
                self.stop()
        except Exception: pass

    @discord.ui.button(label="Metal / Lingotes", style=discord.ButtonStyle.secondary, custom_id="cr_metal")
    async def b1(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check_mat(interaction, "Metal")
    @discord.ui.button(label="Piedra / Madera / Sílex", style=discord.ButtonStyle.secondary, custom_id="cr_stone")
    async def b2(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check_mat(interaction, "Piedra/Madera")
    @discord.ui.button(label="Piel / Fibra / Paja", style=discord.ButtonStyle.secondary, custom_id="cr_hide")
    async def b3(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check_mat(interaction, "Piel/Fibra")
    @discord.ui.button(label="Electrónica / Polímero / Pólvora", style=discord.ButtonStyle.success, custom_id="cr_adv")
    async def b4(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check_mat(interaction, "Avanzado")

# 4. ARK: IMPRONTA
class ArkImprintView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.needs = random.choice(["Mimos", "Paseo", "Comida"])
        self.grabbed = False
    
    async def check(self, interaction: discord.Interaction, action: str):
        if self.grabbed: return
        self.grabbed = True
        
        try:
            if action == self.needs:
                add_points_to_user(interaction.user.id, 300)
                await interaction.response.send_message(f"❤️ **¡Impronta subida!** {interaction.user.mention} acertó (+300 pts).", ephemeral=False)
                for child in self.children: child.disabled = True
                await interaction.message.edit(view=self)
                self.stop()
            else:
                await interaction.response.send_message(f"😭 El bebé quería **{self.needs}**. ¡Se enfadó y se fue!", ephemeral=False)
                embed = interaction.message.embeds[0]
                embed.color = discord.Color.red()
                embed.title = "Crianza FALLIDA"
                for child in self.children: child.disabled = True
                await interaction.message.edit(embed=embed, view=self)
                self.stop()
        except Exception: pass

    @discord.ui.button(label="Dar Mimos 🧸", style=discord.ButtonStyle.primary, custom_id="imp_cud")
    async def b1(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check(interaction, "Mimos")
    @discord.ui.button(label="Pasear 🚶", style=discord.ButtonStyle.success, custom_id="imp_wlk")
    async def b2(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check(interaction, "Paseo")
    @discord.ui.button(label="Alimentar 🍖", style=discord.ButtonStyle.danger, custom_id="imp_fed")
    async def b3(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check(interaction, "Comida")

# 5. ARK: ALPHA HUNT (NIVELES Y PENALIZACIÓN)
class ArkAlphaView(discord.ui.View):
    def __init__(self, win, loss, chance): 
        super().__init__(timeout=None)
        self.win = win
        self.loss = loss
        self.chance = chance
        self.grabbed = False

    @discord.ui.button(label="🗡️ ATACAR ALPHA", style=discord.ButtonStyle.danger, custom_id="alpha_atk")
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.grabbed: return
        self.grabbed = True
        
        try:
            if random.random() < self.chance: 
                add_points_to_user(interaction.user.id, self.win)
                await interaction.response.send_message(f"🏆 **¡VICTORIA!** {interaction.user.mention} mató al Alpha (+{self.win} pts).", ephemeral=False)
            else: 
                remove_points_from_user(interaction.user.id, self.loss)
                await interaction.response.send_message(f"💀 **MUERTE...** {interaction.user.mention} murió y perdió **{self.loss} puntos**.", ephemeral=False)
            
            button.disabled = True
            await interaction.message.edit(view=self)
            self.stop()
        except Exception: pass

# 6. POKÉMON
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
                add_points_to_user(interaction.user.id, 150)
                await interaction.response.send_message(f"✅ **¡Correcto!** {interaction.user.mention} acertó (+150 pts).", ephemeral=False)
                for child in self.children: child.disabled = True
                await interaction.message.edit(view=self)
                self.stop()
            else:
                await interaction.response.send_message(f"❌ Incorrecto. Era {self.correct_type}.", ephemeral=False)
                for child in self.children: child.disabled = True
                await interaction.message.edit(view=self)
                self.stop()
        except Exception: pass

    @discord.ui.button(label="Fuego 🔥", style=discord.ButtonStyle.danger, custom_id="pk_fir")
    async def b1(self, interaction: discord.Interaction, button: discord.ui.Button): await self.guess(interaction, "Fuego")
    @discord.ui.button(label="Agua 💧", style=discord.ButtonStyle.primary, custom_id="pk_wat")
    async def b2(self, interaction: discord.Interaction, button: discord.ui.Button): await self.guess(interaction, "Agua")
    @discord.ui.button(label="Planta 🌿", style=discord.ButtonStyle.success, custom_id="pk_gra")
    async def b3(self, interaction: discord.Interaction, button: discord.ui.Button): await self.guess(interaction, "Planta")

# ==========================================
# 🔄 SISTEMA AUTOMÁTICO (LOOP CON LIMPIEZA)
# ==========================================

async def spawn_game(channel):
    game_type = random.randint(1, 6)
    
    if game_type == 1: # Drop
        embed = discord.Embed(title="¡SUMINISTRO ROJO CAYENDO!", description="Contiene loot de alto nivel. ¡Reclámalo rápido!", color=discord.Color.red())
        embed.set_image(url=IMG_ARK_DROP)
        view = ArkDropView()
        msg = await channel.send(embed=embed, view=view)
        return msg

    elif game_type == 2: # Tame
        data = random.choice(DATA_TAMING)
        embed = discord.Embed(title="¡Dino Inconsciente!", description=f"¿Qué come este **{data['name']}** para ser tameado?", color=discord.Color.green())
        embed.set_image(url=data["url"])
        view = ArkTameView(data["food"], data["name"])
        msg = await channel.send(embed=embed, view=view)
        return msg

    elif game_type == 3: # Craft
        data = random.choice(DATA_CRAFTING)
        embed = discord.Embed(title="Mesa de Crafteo", description=f"¿Cuál es el material principal para: **{data['name']}**?", color=discord.Color.orange())
        embed.set_image(url=data["url"])
        view = ArkCraftView(data["mat"])
        msg = await channel.send(embed=embed, view=view)
        return msg

    elif game_type == 4: # Imprint
        img = random.choice(DATA_BREEDING_IMGS)
        embed = discord.Embed(title="Crianza de Bebé", description="El bebé llora. **Adivina qué cuidado necesita.**", color=discord.Color.purple())
        embed.set_image(url=img)
        view = ArkImprintView()
        msg = await channel.send(embed=embed, view=view)
        return msg

    elif game_type == 5: # Alpha (POR NIVELES)
        data = random.choice(DATA_ALPHAS)
        embed = discord.Embed(title=f"⚠️ {data['name']} DETECTADO", description=f"¿Te arriesgas a atacarlo?\n\n🟢 **Recompensa:** +{data['win']} Puntos\n🔴 **Riesgo:** -{data['loss']} Puntos\n🎲 **Probabilidad:** {int(data['chance']*100)}%", color=data['color'])
        embed.set_image(url=data["url"])
        view = ArkAlphaView(data["win"], data["loss"], data["chance"])
        msg = await channel.send(embed=embed, view=view)
        return msg

    elif game_type == 6: # Pokemon
        data = random.choice(DATA_POKEMON)
        embed = discord.Embed(title="¿Qué tipo es este Pokémon?", description=f"Adivina el tipo de **{data['name']}**.", color=discord.Color.gold())
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
        
        # 1. ELIMINAR JUEGO ANTERIOR (Si existe y nadie jugó)
        if last_minigame_message:
            try:
                # Al poner view=None, los botones desaparecen y ya no se puede jugar
                await last_minigame_message.edit(view=None)
            except:
                pass 

        # 2. ENVIAR NUEVO JUEGO
        last_minigame_message = await spawn_game(channel)
        
    except Exception as e:
        print(f"Error Minigame Loop: {e}")

# ==========================================
# 🏦 SISTEMA VAULT
# ==========================================
class VaultModal(discord.ui.Modal, title="🔐 SECURITY OVERRIDE"):
    code_input = discord.ui.TextInput(label="INSERT PIN CODE", placeholder="####", min_length=4, max_length=4, required=True)
    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        current_time = time.time()
        if user_id in user_cooldowns:
            if (time.time() - user_cooldowns[user_id]) < 15:
                await interaction.response.send_message(f"🚫 Wait...", ephemeral=True)
                return
        user_cooldowns[user_id] = current_time
        
        if not vault_state["active"]:
            await interaction.response.send_message("❌ Event ended.", ephemeral=True)
            return
            
        if self.code_input.value == vault_state["code"]:
            vault_state["active"] = False 
            if vault_state["hints_task"]: vault_state["hints_task"].cancel()
            add_points_to_user(interaction.user.id, 2000)
            await interaction.response.send_message(f"{EMOJI_CORRECT} **ACCESS GRANTED.**", ephemeral=True)
            
            embed = discord.Embed(title="🎉 VAULT CRACKED! 🎉", description=f"{EMOJI_WINNER} Winner: {interaction.user.mention}\nCode: `{vault_state['code']}`\nReward: {vault_state['prize']}", color=0xFFD700)
            embed.set_image(url="https://media1.tenor.com/m/X9kF3Qv1mJAAAAAC/open-safe.gif")
            if interaction.channel: await interaction.channel.send(embed=embed)
        else:
            await interaction.response.send_message(f"⚠️ **ACCESS DENIED.**", ephemeral=True)

class VaultView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="ATTEMPT HACK", style=discord.ButtonStyle.danger, emoji="☠️", custom_id="vault_btn")
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not vault_state["active"]: return
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
# ⚡ COMANDOS
# ==========================================
@bot.tree.command(name="add_points", description="ADMIN")
async def add_points(interaction: discord.Interaction, usuario: discord.Member, cantidad: int):
    if not interaction.user.guild_permissions.administrator: return
    nb = add_points_to_user(usuario.id, cantidad)
    await interaction.response.send_message(f"✅ {usuario.mention} +{cantidad} (Total: {nb})")

@bot.tree.command(name="remove_points", description="ADMIN")
async def remove_points(interaction: discord.Interaction, usuario: discord.Member, cantidad: int):
    if not interaction.user.guild_permissions.administrator: return
    remove_points_from_user(usuario.id, cantidad)
    await interaction.response.send_message(f"✅ {usuario.mention} -{cantidad}")

@bot.command(name="points")
async def check_points(ctx):
    bal = get_user_points(ctx.author.id)
    msg = await ctx.send(f"💰 {ctx.author.mention}: **{bal}** Puntos.")
    try: 
        await ctx.message.delete()
        await asyncio.sleep(10)
        await msg.delete()
    except: pass

@bot.command(name="recipes")
async def show_recipes(ctx):
    await ctx.send(f"{HELL_ARROW} **RECIPES:**\n*(Imagen de crafteos aquí)*")

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
async def start_giveaway(interaction: discord.Interaction, tiempo: str, premio: str):
    if not interaction.user.guild_permissions.administrator: return
    await interaction.response.send_message(f"🎉 **GIVEAWAY**\nPrize: {premio}")
    msg = await interaction.original_response()
    await msg.add_reaction("🎉")

# ==========================================
# 🛡️ EVENTOS
# ==========================================
@bot.event
async def on_ready():
    print(f"🔥 HELL SYSTEM ONLINE: {bot.user}")
    try: await bot.tree.sync()
    except: pass
    
    # Iniciar Loops
    if not dino_game_loop.is_running(): dino_game_loop.start()
    if not minigames_auto_loop.is_running(): minigames_auto_loop.start()
    
    # Recuperar Vistas
    bot.add_view(RolesView())
    bot.add_view(VaultView())

    # Setup Comandos (Limpio)
    c_ch = bot.get_channel(CMD_CHANNEL_ID)
    if c_ch:
        async for m in c_ch.history(limit=5):
            if m.author == bot.user: await m.delete()
        
        embed = discord.Embed(title="🛠️ **SERVER COMMANDS**", color=0x990000)
        embed.add_field(name="👤 **PLAYER COMMANDS**", value=f"{HELL_ARROW} **!recipes**\n{HELL_ARROW} **!points**\n{HELL_ARROW} **.suggest <text>**", inline=False)
        embed.set_footer(text="HELL SYSTEM • Commands")
        await c_ch.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot: return
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
    if message.channel.id == CMD_CHANNEL_ID:
        try: await message.delete(delay=120)
        except: pass
    await bot.process_commands(message)

if __name__ == "__main__":
    if TOKEN: bot.run(TOKEN)
