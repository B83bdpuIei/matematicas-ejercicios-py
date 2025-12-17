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
# 🔐 CONFIGURACIÓN GENERAL
# ==========================================
TOKEN = os.environ.get("DISCORD_TOKEN")

# --- IDs DE CANALES ---
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
# 🖼️ DATOS DE MINIJUEGOS (IMÁGENES Y RESPUESTAS)
# ==========================================

# 1. DROP ROJO (Siempre la misma imagen representativa)
IMG_ARK_DROP = "https://ark.wiki.gg/images/e/e3/Supply_Crate_Level_60.png"

# 2. DATA TAMEO (20 Dinos: 10 Carne, 10 Bayas)
DATA_TAMING = [
    # Carnívoros (Carne)
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
    # Herbívoros (Bayas)
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

# 3. DATA CRAFTING (20 Objetos y su material principal)
# He simplificado esto para que funcione con botones fijos. El juego preguntará por el material principal.
DATA_CRAFTING = [
    # Metal
    {"url": "https://ark.wiki.gg/images/9/9a/Metal_Ingot.png", "mat": "Metal", "name": "Lingote de Metal"},
    {"url": "https://ark.wiki.gg/images/3/30/Flak_Chestpiece.png", "mat": "Metal", "name": "Pechera de Metal"},
    {"url": "https://ark.wiki.gg/images/7/72/Longneck_Rifle.png", "mat": "Metal", "name": "Rifle de Largo Alcance"},
    {"url": "https://ark.wiki.gg/images/3/32/Metal_Pick.png", "mat": "Metal", "name": "Pico de Metal"},
    {"url": "https://ark.wiki.gg/images/5/54/Industrial_Forge.png", "mat": "Metal", "name": "Forja Industrial"},
    # Piedra/Madera
    {"url": "https://ark.wiki.gg/images/b/b9/Stone_Wall.png", "mat": "Piedra/Madera", "name": "Pared de Piedra"},
    {"url": "https://ark.wiki.gg/images/e/e3/Mortar_and_Pestle.png", "mat": "Piedra/Madera", "name": "Mortero"},
    {"url": "https://ark.wiki.gg/images/1/1c/Campfire.png", "mat": "Piedra/Madera", "name": "Hoguera"},
    {"url": "https://ark.wiki.gg/images/7/7c/Wooden_Foundation.png", "mat": "Piedra/Madera", "name": "Cimiento de Madera"},
    {"url": "https://ark.wiki.gg/images/1/1a/Stone_Arrow.png", "mat": "Piedra/Madera", "name": "Flecha de Piedra"},
    # Piel/Fibra
    {"url": "https://ark.wiki.gg/images/b/b4/Hide_Shirt.png", "mat": "Piel/Fibra", "name": "Camisa de Piel"},
    {"url": "https://ark.wiki.gg/images/a/a5/Cloth_Hat.png", "mat": "Piel/Fibra", "name": "Sombrero de Tela"},
    {"url": "https://ark.wiki.gg/images/6/6d/Simple_Bed.png", "mat": "Piel/Fibra", "name": "Cama Simple"},
    {"url": "https://ark.wiki.gg/images/8/88/Saddle.png", "mat": "Piel/Fibra", "name": "Montura Genérica"},
    {"url": "https://ark.wiki.gg/images/c/c2/Bola.png", "mat": "Piel/Fibra", "name": "Boleadora"},
    # Componentes Avanzados (Electrónica, Polímero, Pólvora)
    {"url": "https://ark.wiki.gg/images/9/92/C4_Charge.png", "mat": "Avanzado", "name": "C4"},
    {"url": "https://ark.wiki.gg/images/f/f4/Assault_Rifle.png", "mat": "Avanzado", "name": "Rifle de Asalto"},
    {"url": "https://ark.wiki.gg/images/e/e8/Heavy_Auto_Turret.png", "mat": "Avanzado", "name": "Torreta Pesada"},
    {"url": "https://ark.wiki.gg/images/2/26/Cryopod.png", "mat": "Avanzado", "name": "Cryopod"},
    {"url": "https://ark.wiki.gg/images/3/37/Advanced_Rifle_Bullet.png", "mat": "Avanzado", "name": "Bala de Rifle Avanzado"},
]

# 4. DATA CRIANZA (20 Imágenes de bebés/huevos para flavor)
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

# 5. DATA ALPHA HUNT (Imágenes de Alphas únicas disponibles)
DATA_ALPHA_IMGS = [
    "https://ark.wiki.gg/images/0/03/Alpha_T-Rex.png",
    "https://ark.wiki.gg/images/5/53/Alpha_Raptor.png",
    "https://ark.wiki.gg/images/e/eb/Alpha_Carno.png",
    "https://ark.wiki.gg/images/4/4d/Alpha_Megalodon.png",
    "https://ark.wiki.gg/images/f/f6/Alpha_Mosasaur.png",
    "https://ark.wiki.gg/images/8/85/Alpha_Tusoteuthis.png",
    "https://ark.wiki.gg/images/4/40/Alpha_Leedsichthys.png",
    "https://ark.wiki.gg/images/a/a2/Alpha_Fire_Wyvern.png",
    "https://ark.wiki.gg/images/9/91/Alpha_Deathworm.png",
    "https://ark.wiki.gg/images/d/db/Alpha_Surface_Reaper_King.png",
    "https://ark.wiki.gg/images/c/c6/Alpha_Karkinos.png",
    "https://ark.wiki.gg/images/e/e3/Alpha_Basilisk.png",
    "https://ark.wiki.gg/images/0/03/Alpha_T-Rex.png", # Repetimos algunos icónicos para rellenar
    "https://ark.wiki.gg/images/5/53/Alpha_Raptor.png",
    "https://ark.wiki.gg/images/e/eb/Alpha_Carno.png",
    "https://ark.wiki.gg/images/a/a2/Alpha_Fire_Wyvern.png"
]

# 6. DATA POKÉMON (20 Pokémon variados y sus tipos principales)
DATA_POKEMON = [
    # Fuego
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png", "type": "Fuego", "name": "Charizard"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/59.png", "type": "Fuego", "name": "Arcanine"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/257.png", "type": "Fuego", "name": "Blaziken"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/4.png", "type": "Fuego", "name": "Charmander"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/38.png", "type": "Fuego", "name": "Ninetales"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/136.png", "type": "Fuego", "name": "Flareon"},
    # Agua
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/9.png", "type": "Agua", "name": "Blastoise"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/130.png", "type": "Agua", "name": "Gyarados"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/134.png", "type": "Agua", "name": "Vaporeon"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png", "type": "Agua", "name": "Squirtle"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/55.png", "type": "Agua", "name": "Golduck"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/245.png", "type": "Agua", "name": "Suicune"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/260.png", "type": "Agua", "name": "Swampert"},
    # Planta
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/3.png", "type": "Planta", "name": "Venusaur"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png", "type": "Planta", "name": "Bulbasaur"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/154.png", "type": "Planta", "name": "Meganium"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/254.png", "type": "Planta", "name": "Sceptile"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/45.png", "type": "Planta", "name": "Vileplume"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/152.png", "type": "Planta", "name": "Chikorita"},
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/251.png", "type": "Planta", "name": "Celebi"},
]

# ==========================================
# OTHER CONFIGS (Roles, Emojis, Shop, etc.)
# ==========================================
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

# --- ESTADOS ---
vault_state = {
    "active": False,
    "code": None,
    "prize": None,
    "message_id": None,
    "hints_task": None
}
user_cooldowns = {} 
dino_game_state = {
    "active": False,
    "current_dino": None,
    "message_id": None
}

# --- SISTEMA DE PUNTOS (JSON) ---
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
    if data[uid] < amount: return False
    data[uid] -= amount
    save_points(data)
    return True

def get_user_points(user_id):
    data = load_points()
    return data.get(str(user_id), 0)

# ==========================================
# ⚙️ SETUP
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
    answer_input = discord.ui.TextInput(
        label="Dino Name",
        placeholder="Enter the correct name...",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not dino_game_state["active"]:
            await interaction.response.send_message("❌ Too late! The round is over.", ephemeral=True)
            return

        guess = self.answer_input.value.strip().lower()
        correct = dino_game_state["current_dino"].lower()

        if guess == correct:
            dino_game_state["active"] = False 
            points_won = 150 
            add_points_to_user(interaction.user.id, points_won)

            await interaction.response.send_message(f"{EMOJI_CORRECT} **CORRECT!** You guessed it.", ephemeral=True)

            embed = discord.Embed(color=0x00FF00)
            embed.description = (
                f"{EMOJI_WINNER} **WINNER:** {interaction.user.mention}\n"
                f"{EMOJI_ANSWER} **ANSWER:** `{dino_game_state['current_dino']}`\n"
                f"{EMOJI_POINTS} **POINTS:** +{points_won}"
            )
            embed.set_footer(text="Hell System • Dino Games")
            
            channel = bot.get_channel(DINO_CHANNEL_ID)
            if channel:
                await channel.send(embed=embed)
            
            try:
                msg = await channel.fetch_message(dino_game_state["message_id"])
                await msg.edit(view=None)
            except: pass

        else:
            await interaction.response.send_message(f"❌ **WRONG!** Try again.", ephemeral=True)

class DinoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="GUESS THE DINO", style=discord.ButtonStyle.primary, emoji="❓", custom_id="dino_guess_btn")
    async def guess_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not dino_game_state["active"]:
            await interaction.response.send_message("❌ Round ended.", ephemeral=True)
            return
        await interaction.response.send_modal(DinoModal())

@tasks.loop(minutes=20)
async def dino_game_loop():
    channel = bot.get_channel(DINO_CHANNEL_ID)
    if not channel: return

    if dino_game_state["active"]:
        fail_embed = discord.Embed(description=f"⏰ **TIME'S UP!** Nobody guessed correctly.\n{EMOJI_ANSWER} The answer was: **{dino_game_state['current_dino']}**", color=0xFF0000)
        fail_embed.set_footer(text="Hell System • Dino Games")
        await channel.send(embed=fail_embed)
        try:
            old_msg = await channel.fetch_message(dino_game_state["message_id"])
            await old_msg.edit(view=None)
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
        f"Click the button to answer. You have **20 minutes**!"
    )
    embed.set_footer(text="Hell System • Dino Games")

    view = DinoView()
    msg = await channel.send(embed=embed, view=view)

    dino_game_state["active"] = True
    dino_game_state["current_dino"] = dino_real_name
    dino_game_state["message_id"] = msg.id

# ==========================================
# 🎮 CLASES MINIGAMES (Lógica de Botones)
# ==========================================

# 1. ARK: DROP ROJO
class ArkDropView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="CLAIM DROP", style=discord.ButtonStyle.danger, emoji="🎁")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
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

# 2. ARK: TAMEO (Dinámico)
class ArkTameView(discord.ui.View):
    def __init__(self, correct_food, dino_name):
        super().__init__(timeout=None)
        self.correct_food = correct_food
        self.dino_name = dino_name

    async def feed(self, interaction: discord.Interaction, food: str):
        if food == self.correct_food:
            add_points_to_user(interaction.user.id, 200)
            await interaction.response.send_message(f"🦕 **¡TAMEADO!** {interaction.user.mention} le dio {food} al {self.dino_name} y ganó 200 puntos.", ephemeral=False)
            for child in self.children: child.disabled = True
            await interaction.message.edit(view=self)
            self.stop()
        else:
            await interaction.response.send_message(f"❌ El {self.dino_name} rechaza {food}. ¡Cuidado!", ephemeral=True)

    @discord.ui.button(label="Carne Cruda 🥩", style=discord.ButtonStyle.danger)
    async def meat(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.feed(interaction, "Carne")
    @discord.ui.button(label="Mejoberries 🫐", style=discord.ButtonStyle.primary)
    async def berries(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.feed(interaction, "Bayas")

# 3. ARK: CRAFTING (Dinámico)
class ArkCraftView(discord.ui.View):
    def __init__(self, correct_mat):
        super().__init__(timeout=None)
        self.correct_mat = correct_mat

    async def check_mat(self, interaction: discord.Interaction, mat_clicked: str):
        if mat_clicked == self.correct_mat:
            add_points_to_user(interaction.user.id, 150)
            await interaction.response.send_message(f"🔨 **¡Correcto!** {interaction.user.mention} usó los materiales correctos (+150 Puntos).", ephemeral=False)
            for child in self.children: child.disabled = True
            await interaction.message.edit(view=self)
            self.stop()
        else:
            await interaction.response.send_message("❌ Material incorrecto para este objeto.", ephemeral=True)

    @discord.ui.button(label="Metal / Lingotes", style=discord.ButtonStyle.secondary)
    async def btn_metal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_mat(interaction, "Metal")
    @discord.ui.button(label="Piedra / Madera / Sílex", style=discord.ButtonStyle.secondary)
    async def btn_stone(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_mat(interaction, "Piedra/Madera")
    @discord.ui.button(label="Piel / Fibra / Paja", style=discord.ButtonStyle.secondary)
    async def btn_hide(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_mat(interaction, "Piel/Fibra")
    @discord.ui.button(label="Electrónica / Polímero / Pólvora", style=discord.ButtonStyle.success)
    async def btn_adv(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_mat(interaction, "Avanzado")

# 4. ARK: IMPRONTA
class ArkImprintView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.needs = random.choice(["Mimos", "Paseo", "Comida"])

    async def check(self, interaction: discord.Interaction, action: str):
        if action == self.needs:
            add_points_to_user(interaction.user.id, 300)
            await interaction.response.send_message(f"❤️ **¡Impronta subida!** {interaction.user.mention} acertó y ganó 300 puntos.", ephemeral=False)
            for child in self.children: child.disabled = True
            await interaction.message.edit(view=self)
            self.stop()
        else:
            await interaction.response.send_message(f"El bebé no quiere eso... Quería **{self.needs}**.", ephemeral=True)

    @discord.ui.button(label="Dar Mimos 🧸", style=discord.ButtonStyle.primary)
    async def cuddle(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check(interaction, "Mimos")
    @discord.ui.button(label="Pasear 🚶", style=discord.ButtonStyle.success)
    async def walk(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check(interaction, "Paseo")
    @discord.ui.button(label="Alimentar 🍖", style=discord.ButtonStyle.danger)
    async def feed(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check(interaction, "Comida")

# 5. ARK: ALPHA HUNT
class ArkAlphaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label="🗡️ ATACAR ALPHA", style=discord.ButtonStyle.danger)
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        if random.random() < 0.5: # 50%
            add_points_to_user(interaction.user.id, 1000)
            await interaction.response.send_message(f"🏆 **¡VICTORIA ÉPICA!** {interaction.user.mention} mató al Alpha y ganó **1000 puntos**.", ephemeral=False)
        else:
            await interaction.response.send_message(f"💀 **MUERTE...** {interaction.user.mention} fue devorado.", ephemeral=False)
        button.disabled = True
        await interaction.message.edit(view=self)
        self.stop()

# 6. POKÉMON (Dinámico)
class PokemonVisualView(discord.ui.View):
    def __init__(self, correct_type, poke_name):
        super().__init__(timeout=None)
        self.correct_type = correct_type
        self.poke_name = poke_name

    async def guess(self, interaction: discord.Interaction, type_guess: str):
        if type_guess == self.correct_type:
            add_points_to_user(interaction.user.id, 150)
            await interaction.response.send_message(f"✅ **¡Correcto!** {interaction.user.mention} acertó. {self.poke_name} es tipo {self.correct_type} (+150 Puntos).", ephemeral=False)
            for child in self.children: child.disabled = True
            await interaction.message.edit(view=self)
            self.stop()
        else:
            await interaction.response.send_message(f"❌ Tipo incorrecto para {self.poke_name}.", ephemeral=True)

    @discord.ui.button(label="Fuego 🔥", style=discord.ButtonStyle.danger)
    async def fire(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.guess(interaction, "Fuego")
    @discord.ui.button(label="Agua 💧", style=discord.ButtonStyle.primary)
    async def water(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.guess(interaction, "Agua")
    @discord.ui.button(label="Planta 🌿", style=discord.ButtonStyle.success)
    async def grass(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.guess(interaction, "Planta")


# ==========================================
# 🔄 SISTEMA AUTOMÁTICO (SPAWNERS CON DATOS ALEATORIOS)
# ==========================================

async def spawn_drop(channel):
    embed = discord.Embed(title="¡SUMINISTRO ROJO CAYENDO!", description="Contiene loot de alto nivel. ¡Reclámalo rápido!", color=discord.Color.red())
    embed.set_image(url=IMG_ARK_DROP)
    await channel.send(embed=embed, view=ArkDropView())

async def spawn_tame(channel):
    # Elegir datos aleatorios de la lista
    data = random.choice(DATA_TAMING)
    embed = discord.Embed(title="¡Dino Inconsciente!", description=f"¿Qué come este **{data['name']}** para ser tameado?", color=discord.Color.green())
    embed.set_image(url=data["url"])
    # Pasar los datos correctos a la View
    await channel.send(embed=embed, view=ArkTameView(correct_food=data["food"], dino_name=data["name"]))

async def spawn_craft(channel):
    data = random.choice(DATA_CRAFTING)
    embed = discord.Embed(title="Mesa de Crafteo", description=f"¿Cuál es el material principal para fabricar: **{data['name']}**?", color=discord.Color.orange())
    embed.set_image(url=data["url"])
    await channel.send(embed=embed, view=ArkCraftView(correct_mat=data["mat"]))

async def spawn_imprint(channel):
    img_url = random.choice(DATA_BREEDING_IMGS)
    embed = discord.Embed(title="Crianza de Bebé", description="El bebé está llorando. **Intenta adivinar qué cuidado necesita.**", color=discord.Color.purple())
    embed.set_image(url=img_url)
    await channel.send(embed=embed, view=ArkImprintView())

async def spawn_alpha(channel):
    img_url = random.choice(DATA_ALPHA_IMGS)
    embed = discord.Embed(title="⚠️ ¡ALPHA DETECTADO!", description="¿Te arriesgas a atacarlo? (50% Ganar 1000 Pts / 50% Morir)", color=discord.Color.dark_red())
    embed.set_image(url=img_url)
    await channel.send(embed=embed, view=ArkAlphaView())

async def spawn_poke(channel):
    data = random.choice(DATA_POKEMON)
    embed = discord.Embed(title="¿Qué tipo es este Pokémon?", description=f"Adivina el tipo de **{data['name']}**.", color=discord.Color.gold())
    embed.set_image(url=data["url"])
    await channel.send(embed=embed, view=PokemonVisualView(correct_type=data["type"], poke_name=data["name"]))

@tasks.loop(minutes=5)
async def minigames_auto_loop():
    channel = bot.get_channel(MINIGAMES_CHANNEL_ID)
    if not channel:
        return

    # Lista de funciones para llamar
    games = [spawn_drop, spawn_tame, spawn_craft, spawn_imprint, spawn_alpha, spawn_poke]
    
    # Elegir uno al azar y ejecutarlo
    selected_game = random.choice(games)
    await selected_game(channel)

# ==========================================
# 🏦 SISTEMA VAULT
# ==========================================

class VaultModal(discord.ui.Modal, title="🔐 SECURITY OVERRIDE"):
    code_input = discord.ui.TextInput(label="INSERT PIN CODE", placeholder="####", min_length=4, max_length=4, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        current_time = time.time()
        if user_id in user_cooldowns:
            elapsed = current_time - user_cooldowns[user_id]
            remaining = 15 - elapsed
            if remaining > 0:
                await interaction.response.send_message(f"🚫 **SYSTEM LOCKED.** Wait **{int(remaining)}s** for reboot.", ephemeral=True)
                return
        user_cooldowns[user_id] = current_time
        if not vault_state["active"]:
            await interaction.response.send_message("❌ Connection lost. Event ended.", ephemeral=True)
            return
        guess = self.code_input.value
        if guess == vault_state["code"]:
            vault_state["active"] = False 
            if vault_state["hints_task"]: vault_state["hints_task"].cancel()
            
            bonus_points = 2000
            add_points_to_user(interaction.user.id, bonus_points)

            await interaction.response.send_message(f"{EMOJI_CORRECT} **ACCESS GRANTED.** Downloading loot...", ephemeral=True)
            
            winner_embed = discord.Embed(
                title="🎉 VAULT CRACKED! 🎉",
                description=f"{EMOJI_WINNER} **WINNER:** {interaction.user.mention}\n{EMOJI_CODE} **CODE:** `{guess}`\n{EMOJI_REWARD} **LOOT:** {vault_state['prize']}\n{EMOJI_POINTS} **BONUS:** +{bonus_points}",
                color=0xFFD700
            )
            winner_embed.set_image(url="https://media1.tenor.com/m/X9kF3Qv1mJAAAAAC/open-safe.gif") 
            winner_embed.set_footer(text="HELL SYSTEM • Vault Event") 
            channel = bot.get_channel(VAULT_CHANNEL_ID)
            if channel: await channel.send(content=f"{interaction.user.mention} cracked the code!", embed=winner_embed)
            try:
                msg = await interaction.channel.fetch_message(vault_state["message_id"])
                await msg.edit(view=None)
            except: pass
        else:
            await interaction.response.send_message(f"⚠️ **ACCESS DENIED.** Invalid PIN.\n*Security protocol active: 15s timeout.*", ephemeral=True)

class VaultView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None) 
    @discord.ui.button(label="ATTEMPT HACK", style=discord.ButtonStyle.danger, emoji="☠️", custom_id="vault_open_btn")
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not vault_state["active"]:
            await interaction.response.send_message("❌ Target offline.", ephemeral=True)
            return
        await interaction.response.send_modal(VaultModal())

async def manage_vault_hints(channel, message, code):
    try:
        await asyncio.sleep(18000) 
        if not vault_state["active"]: return
        hint_2 = f"{code[:2]}##"
        new_embed = message.embeds[0]
        new_embed.set_field_at(0, name="📡 LEAKED DATA", value=f"`{hint_2}`", inline=True)
        await message.edit(embed=new_embed)
        await asyncio.sleep(68400) 
        if not vault_state["active"]: return
        hint_3 = f"{code[:3]}#"
        new_embed = message.embeds[0]
        new_embed.set_field_at(0, name="📡 LEAKED DATA", value=f"`{hint_3}`", inline=True)
        await message.edit(embed=new_embed)
    except asyncio.CancelledError: pass

# ==========================================
# 🔘 ROLES
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
# ⚡ COMANDOS ADMIN (SLASH /)
# ==========================================

@bot.tree.command(name="add_points", description="ADMIN: Añadir puntos a un usuario")
async def add_points(interaction: discord.Interaction, usuario: discord.Member, cantidad: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ No tienes permisos.", ephemeral=True)
        return
    
    new_bal = add_points_to_user(usuario.id, cantidad)
    await interaction.response.send_message(f"✅ Se añadieron **{cantidad}** {EMOJI_POINTS} a {usuario.mention}. Nuevo saldo: **{new_bal}**")

@bot.tree.command(name="remove_points", description="ADMIN: Quitar puntos a un usuario")
async def remove_points(interaction: discord.Interaction, usuario: discord.Member, cantidad: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ No tienes permisos.", ephemeral=True)
        return
    
    success = remove_points_from_user(usuario.id, cantidad)
    if success:
        new_bal = get_user_points(usuario.id)
        await interaction.response.send_message(f"✅ Se retiraron **{cantidad}** {EMOJI_POINTS} a {usuario.mention}. Nuevo saldo: **{new_bal}**")
    else:
        await interaction.response.send_message(f"❌ El usuario no tiene suficientes puntos.", ephemeral=True)

# ==========================================
# ⚡ COMANDOS USUARIO (PREFIX !)
# ==========================================

@bot.command(name="points")
async def check_points(ctx):
    bal = get_user_points(ctx.author.id)
    msg = await ctx.send(f"💰 {ctx.author.mention}, tienes **{bal}** {EMOJI_POINTS} Puntos.")
    try:
        await ctx.message.delete()
        await asyncio.sleep(10)
        await msg.delete()
    except: pass

@bot.command(name="recipes")
async def show_recipes(ctx):
    await ctx.send(f"{HELL_ARROW} **RECIPES:**\n*(Aquí deberías poner la imagen o lista de crafteos)*")

# ==========================================
# ⚡ EVENTOS SLASH (ADMIN)
# ==========================================

@bot.tree.command(name="event_vault", description="Inicia el evento de la Caja Fuerte")
async def event_vault(interaction: discord.Interaction, code: str, prize: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ No tienes permisos.", ephemeral=True)
        return
    if len(code) != 4 or not code.isdigit():
        await interaction.response.send_message("❌ Código inválido.", ephemeral=True)
        return
    channel = bot.get_channel(VAULT_CHANNEL_ID)
    if not channel:
        await interaction.response.send_message("❌ Error ID Canal.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    hint_1 = f"{code[0]}###"
    embed = discord.Embed(title=f"{EMOJI_BLOOD} **HIGH VALUE VAULT DETECTED** {EMOJI_BLOOD}", color=0x8a0404)
    desc = (f"The Admins locked the best loot inside. Are you smart enough to take it, or are you just muscle?\n\n🎯 **TASK:** Crack the 4-digit PIN before anyone else.\n⚠️ **WARNING:** Area is Hot. Expect PvP.\n🛡️ **SECURITY:** 15s Lockout protocol active on fail.\n\n{EMOJI_REWARD} **MYSTERY REWARD:** {prize}")
    embed.description = desc
    embed.add_field(name="📡 LEAKED DATA", value=f"`{hint_1}`", inline=True)
    embed.set_image(url=VAULT_IMAGE_URL)      
    embed.set_footer(text="HELL SYSTEM • Vault Event") 
    view = VaultView()
    msg = await channel.send(embed=embed, view=view)
    vault_state["active"] = True
    vault_state["code"] = code
    vault_state["prize"] = prize
    vault_state["message_id"] = msg.id
    if vault_state["hints_task"]: vault_state["hints_task"].cancel()
    vault_state["hints_task"] = asyncio.create_task(manage_vault_hints(channel, msg, code))
    await interaction.followup.send(f"✅ Evento iniciado.")

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

@bot.tree.command(name="finish_polls", description="Publica resultados.")
async def finish_polls(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator: return
    await interaction.response.send_message("Procesando...", ephemeral=True)

# ==========================================
# 🛡️ GESTOR MENSAJES (.suggest y limpieza)
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
        embed.set_footer(text="HELL SYSTEM • Suggestions") 
        sent_msg = await message.channel.send(embed=embed)
        try:
            await sent_msg.add_reaction(CHECK_ICON)
            await sent_msg.add_reaction(CROSS_ICON)
        except: pass
        return

    # --- LIMPIEZA CANAL COMANDOS ---
    if message.channel.id == CMD_CHANNEL_ID:
        # El delay=120 significa 2 minutos (120 segundos)
        try: await message.delete(delay=120) 
        except: pass 

    await bot.process_commands(message)

# ==========================================
# 🚀 STARTUP
# ==========================================
@bot.event
async def on_ready():
    print(f"🔥 HELL SYSTEM ONLINE - {bot.user}")
    
    bot.add_view(RolesView())
    bot.add_view(VaultView()) 
    bot.add_view(DinoView()) 
    
    try: await bot.tree.sync()
    except: pass

    # Iniciar loops
    if not dino_game_loop.is_running():
        dino_game_loop.start()
    
    if not minigames_auto_loop.is_running():
        minigames_auto_loop.start()

    # --- 1. ROLES ---
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
                    description=(f"{HELL_ARROW} Click the buttons below to toggle your roles.\n{HELL_ARROW} Select the channels you want to see.\n━━━━━━━━━━━━━━━━━━━━━━━━"),
                    color=0x990000
                )
                embed.set_footer(text="HELL SYSTEM • Auto-Roles") 
                await roles_channel.send(embed=embed, view=RolesView())
        except: pass

    # --- 2. SETUP DE TIENDA (AUTO-SEARCH/CREATE) ---
    for guild in bot.guilds:
        shop_channel = discord.utils.get(guild.text_channels, name=SHOP_CHANNEL_NAME)
        
        # Si no existe, crear
        if not shop_channel:
            try:
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(send_messages=False),
                    guild.me: discord.PermissionOverwrite(send_messages=True)
                }
                shop_channel = await guild.create_text_channel(SHOP_CHANNEL_NAME, overwrites=overwrites)
                print(f"✅ Canal de tienda creado: {SHOP_CHANNEL_NAME}")
            except Exception as e:
                print(f"❌ Error creando tienda: {e}")
        
        # Si existe, postear menú
        if shop_channel:
            last_msg = None
            async for msg in shop_channel.history(limit=1): last_msg = msg
            
            shop_ok = False
            if last_msg and last_msg.author == bot.user and last_msg.embeds:
                if "BLACK MARKET SHOP" in (last_msg.embeds[0].title or ""): shop_ok = True
            
            if not shop_ok:
                await shop_channel.purge(limit=10)
                embed = discord.Embed(title=f"{EMOJI_REWARD} **BLACK MARKET SHOP** {EMOJI_REWARD}", color=0x9900FF)
                embed.description = f"Earn {EMOJI_POINTS} by winning minigames.\n{HELL_ARROW} **Dino Win:** 150 Pts\n{HELL_ARROW} **Vault Win:** 2000 Pts\n\n**⚠️ OPEN A TICKET TO BUY ⚠️**\n━━━━━━━━━━━━━━━━━━━━━━━━"
                for item in SHOP_ITEMS:
                    embed.add_field(
                        name=f"📦 {item['name']}",
                        value=f"{EMOJI_POINTS} **{item['price']}**\n*{item['desc']}*",
                        inline=False
                    )
                embed.set_footer(text="Hell System • Economy")
                await shop_channel.send(embed=embed)

    # --- 3. ACTUALIZAR LISTA DE COMANDOS (LIMPIO - SIN ADMIN) ---
    cmd_channel = bot.get_channel(CMD_CHANNEL_ID)
    if cmd_channel:
        try:
            last_cmd_msg = None
            async for msg in cmd_channel.history(limit=1):
                 if msg.author == bot.user: last_cmd_msg = msg; break
            
            # Construir Embed
            embed_cmds = discord.Embed(title=f"🛠️ **SERVER COMMANDS**", color=0x990000)
            
            # Campo Jugador SOLAMENTE
            embed_cmds.add_field(
                name="👤 **PLAYER COMMANDS**", 
                value=f"{HELL_ARROW} **!recipes** - Ver crafteos\n{HELL_ARROW} **!points** - Ver puntos\n{HELL_ARROW} **.suggest <text>** - Sugerencia",
                inline=False
            )
            # He borrado el campo ADMIN COMMANDS como pediste
            
            embed_cmds.set_footer(text="HELL SYSTEM • Commands")

            # Verificar si hay que reenviar
            list_ok = False
            if last_cmd_msg and last_cmd_msg.embeds:
                # Comprobamos si es el mensaje correcto Y si NO tiene el campo Admin
                if "SERVER COMMANDS" in (last_cmd_msg.embeds[0].title or ""):
                    # Si tiene más de 1 campo (el de Player), es el viejo, así que list_ok = False
                    if len(last_cmd_msg.embeds[0].fields) == 1:
                        list_ok = True
            
            if not list_ok:
                async for msg in cmd_channel.history(limit=10):
                    if msg.author == bot.user: await msg.delete()
                await cmd_channel.send(embed=embed_cmds)
        except: pass

    # --- 4. SUGERENCIAS ---
    suggest_channel = bot.get_channel(SUGGEST_CHANNEL_ID)
    if suggest_channel:
        try:
            last_sug_msg = None
            async for msg in suggest_channel.history(limit=1): last_sug_msg = msg
            
            guide_ok = False
            if last_sug_msg and last_sug_msg.author == bot.user and last_sug_msg.embeds:
                if "SUGGESTION SYSTEM" in (last_sug_msg.embeds[0].title or ""): guide_ok = True
            
            if not guide_ok:
                async for msg in suggest_channel.history(limit=20):
                    if msg.author == bot.user and msg.embeds:
                        if "SUGGESTION SYSTEM" in (msg.embeds[0].title or ""):
                            await msg.delete()

                embed = discord.Embed(
                    title="💡 **SUGGESTION SYSTEM**",
                    description=(f"To suggest something, use the command below:\n\n` .suggest <your text> `\n\n{HELL_ARROW} **Example:** `.suggest Add more kits`\n━━━━━━━━━━━━━━━━━━━━━━━━"),
                    color=0x990000
                )
                embed.set_footer(text="HELL SYSTEM • Suggestions") 
                await suggest_channel.send(embed=embed)
        except: pass

    # --- 5. NOMBRES ---
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

def convert_time(time_str):
    unit = time_str[-1].lower()
    try: val = int(time_str[:-1])
    except: return -1
    if unit == 's': return val
    if unit == 'm': return val * 60
    if unit == 'h': return val * 3600
    if unit == 'd': return val * 86400
    return 0

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
