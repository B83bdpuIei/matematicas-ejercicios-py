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
import io
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==========================================
# 🚑 FAKE WEB SERVER (24/7 UPTIME)
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
GIVEAWAY_CHANNEL_ID = 1449849645495746803 # Canal ROJO (Support)
CMD_CHANNEL_ID = 1449346777659609288
ROLES_CHANNEL_ID = 1449083960578670614
SUGGEST_CHANNEL_ID = 1449346646465839134
VAULT_CHANNEL_ID = 1450244608817762465
DINO_CHANNEL_ID = 1450244689285353544 
MINIGAMES_CHANNEL_ID = 1450244729848598618
DB_CHANNEL_ID = 1451330350436323348 # Cloud Database

SHOP_CHANNEL_NAME = "「🔥」hell-store"

# SUPPORT CONFIG
SUPPORT_TEXT = "! HELL WIPES FRIDAY 100€"
SUPPORT_ROLE_ID = 1336477737594130482

# ==========================================
# 🖼️ DATASETS
# ==========================================
IMG_ARK_DROP = "https://ark.wiki.gg/images/e/e3/Supply_Crate_Level_60.png"
EMOJI_C4 = "<:C4_HELL:1451357075321131049>"

DATA_RAID = [
    {"name": "Metal Wall", "c4": "4", "img": "https://ark.wiki.gg/images/3/3b/Metal_Wall.png"},
    {"name": "Stone Wall", "c4": "2", "img": "https://ark.wiki.gg/images/b/b9/Stone_Wall.png"},
    {"name": "Metal Vault", "c4": "19", "img": "https://ark.wiki.gg/images/thumb/8/88/Vault.png/300px-Vault.png"},
    {"name": "Tek Turret", "c4": "1", "img": "https://ark.wiki.gg/images/6/6c/Tek_Turret.png"},
    {"name": "Heavy Turret", "c4": "1", "img": "https://ark.wiki.gg/images/e/e8/Heavy_Auto_Turret.png"},
    {"name": "Auto Turret", "c4": "1", "img": "https://ark.wiki.gg/images/0/02/Auto_Turret.png"},
    {"name": "Stone Found.", "c4": "2", "img": "https://ark.wiki.gg/images/c/c3/Stone_Foundation.png"},
    {"name": "Metal Found.", "c4": "4", "img": "https://ark.wiki.gg/images/3/34/Metal_Foundation.png"},
    {"name": "Tek Replicator", "c4": "6", "img": "https://ark.wiki.gg/images/a/a2/Tek_Replicator.png"},
    {"name": "Indy Forge", "c4": "7", "img": "https://ark.wiki.gg/images/5/54/Industrial_Forge.png"},
    {"name": "Chem Bench", "c4": "2", "img": "https://ark.wiki.gg/images/a/a8/Chemistry_Bench.png"},
    {"name": "Fabricator", "c4": "1", "img": "https://ark.wiki.gg/images/7/75/Fabricator.png"},
    {"name": "Generator", "c4": "1", "img": "https://ark.wiki.gg/images/0/07/Electrical_Generator.png"},
    {"name": "Tek Generator", "c4": "6", "img": "https://ark.wiki.gg/images/7/77/Tek_Generator.png"},
    {"name": "Transmitter", "c4": "4", "img": "https://ark.wiki.gg/images/3/33/Tek_Transmitter.png"},
    {"name": "Cloning Chamber", "c4": "12", "img": "https://ark.wiki.gg/images/5/5e/Cloning_Chamber.png"},
    {"name": "Teleporter", "c4": "10", "img": "https://ark.wiki.gg/images/1/1b/Tek_Teleporter.png"},
    {"name": "Cryofridge", "c4": "4", "img": "https://ark.wiki.gg/images/2/22/Cryofridge.png"},
    {"name": "Tek Forcefield", "c4": "1", "img": "https://ark.wiki.gg/images/d/d5/Tek_Forcefield.png"},
    {"name": "Large Crop Plot", "c4": "1", "img": "https://ark.wiki.gg/images/9/9e/Large_Crop_Plot.png"}
]

DATA_GEO = [
    {"map": "Aberration", "hint": "Radioactive / Pink", "img": "https://ark.wiki.gg/images/thumb/3/30/The_Surface_%28Aberration%29.jpg/400px-The_Surface_%28Aberration%29.jpg"},
    {"map": "The Island", "hint": "The Volcano", "img": "https://ark.wiki.gg/images/thumb/3/3f/Volcano.jpg/400px-Volcano.jpg"},
    {"map": "Extinction", "hint": "Sanctuary City", "img": "https://ark.wiki.gg/images/thumb/9/9f/Sanctuary.jpg/400px-Sanctuary.jpg"},
    {"map": "Scorched Earth", "hint": "Red Obelisk Desert", "img": "https://ark.wiki.gg/images/thumb/e/e4/Red_Obelisk_%28Scorched_Earth%29.jpg/400px-Red_Obelisk_%28Scorched_Earth%29.jpg"},
    {"map": "Genesis 1", "hint": "Ocean Biome", "img": "https://ark.wiki.gg/images/thumb/9/98/Ocean_Biome_%28Genesis_Part_1%29.jpg/400px-Ocean_Biome_%28Genesis_Part_1%29.jpg"},
    {"map": "Ragnarok", "hint": "Highlands", "img": "https://ark.wiki.gg/images/thumb/5/52/Highlands.jpg/400px-Highlands.jpg"},
    {"map": "The Center", "hint": "Floating Island", "img": "https://ark.wiki.gg/images/thumb/5/53/The_Center_%28The_Center%29.jpg/400px-The_Center_%28The_Center%29.jpg"},
    {"map": "Valguero", "hint": "White Cliffs", "img": "https://ark.wiki.gg/images/thumb/4/47/The_White_Cliffs_%28Valguero%29.jpg/400px-The_White_Cliffs_%28Valguero%29.jpg"},
    {"map": "Crystal Isles", "hint": "Floating Crystals", "img": "https://ark.wiki.gg/images/thumb/6/63/Eldritch_Isle_%28Crystal_Isles%29.jpg/400px-Eldritch_Isle_%28Crystal_Isles%29.jpg"},
    {"map": "Genesis 2", "hint": "Eden Side", "img": "https://ark.wiki.gg/images/thumb/c/c5/Eden_%28Genesis_Part_2%29.jpg/400px-Eden_%28Genesis_Part_2%29.jpg"},
    {"map": "Genesis 2", "hint": "Rockwell Side", "img": "https://ark.wiki.gg/images/thumb/f/f6/Rockwell%27s_Garden_%28Genesis_Part_2%29.jpg/400px-Rockwell%27s_Garden_%28Genesis_Part_2%29.jpg"},
    {"map": "Lost Island", "hint": "Monkey Temple", "img": "https://ark.wiki.gg/images/thumb/8/87/Tumash_Jungle_%28Lost_Island%29.jpg/400px-Tumash_Jungle_%28Lost_Island%29.jpg"},
    {"map": "Fjordur", "hint": "Asgard (Gold)", "img": "https://ark.wiki.gg/images/thumb/d/d4/Asgard_%28Fjordur%29.jpg/400px-Asgard_%28Fjordur%29.jpg"},
    {"map": "Fjordur", "hint": "Jotunheim (Ice)", "img": "https://ark.wiki.gg/images/thumb/6/63/Jotunheim_%28Fjordur%29.jpg/400px-Jotunheim_%28Fjordur%29.jpg"},
    {"map": "Aberration", "hint": "Blue Zone", "img": "https://ark.wiki.gg/images/thumb/7/75/The_Luminous_Marshlands_%28Aberration%29.jpg/400px-The_Luminous_Marshlands_%28Aberration%29.jpg"},
    {"map": "Extinction", "hint": "Snow Dome", "img": "https://ark.wiki.gg/images/thumb/5/56/Snow_Dome_%28Extinction%29.jpg/400px-Snow_Dome_%28Extinction%29.jpg"},
    {"map": "The Island", "hint": "Redwoods", "img": "https://ark.wiki.gg/images/thumb/2/23/Redwood_Forests.jpg/400px-Redwood_Forests.jpg"},
    {"map": "Scorched Earth", "hint": "Wyvern Trench", "img": "https://ark.wiki.gg/images/thumb/6/67/World_Scar_%28Scorched_Earth%29.jpg/400px-World_Scar_%28Scorched_Earth%29.jpg"},
    {"map": "Ragnarok", "hint": "Lava Golem Cave", "img": "https://ark.wiki.gg/images/thumb/4/48/Jungle_Dungeon_%28Ragnarok%29.jpg/400px-Jungle_Dungeon_%28Ragnarok%29.jpg"},
    {"map": "Fjordur", "hint": "Mines of Moria", "img": "https://ark.wiki.gg/images/thumb/e/e3/Mines_of_Moria_%28Fjordur%29.jpg/400px-Mines_of_Moria_%28Fjordur%29.jpg"}
]

DATA_TAME_TRICKY = [
    {"name": "Rex", "method": "Knockout", "img": "https://ark.wiki.gg/images/0/03/Rex.png"},
    {"name": "Giganotosaurus", "method": "Knockout", "img": "https://ark.wiki.gg/images/9/9e/Giganotosaurus.png"},
    {"name": "Wyvern", "method": "Steal Egg", "img": "https://ark.wiki.gg/images/a/a8/Fire_Wyvern.png"},
    {"name": "Deinonychus", "method": "Steal Egg", "img": "https://ark.wiki.gg/images/2/23/Deinonychus.png"},
    {"name": "Magmasaur", "method": "Steal Egg", "img": "https://ark.wiki.gg/images/6/6a/Magmasaur.png"},
    {"name": "Chalicotherium", "method": "Passive", "img": "https://ark.wiki.gg/images/f/f2/Chalicotherium.png"}, 
    {"name": "Equus", "method": "Passive", "img": "https://ark.wiki.gg/images/8/86/Equus.png"},
    {"name": "Moschops", "method": "Passive", "img": "https://ark.wiki.gg/images/0/06/Moschops.png"},
    {"name": "Rock Golem", "method": "Knockout", "img": "https://ark.wiki.gg/images/d/d3/Rock_Elemental.png"}, 
    {"name": "Basilosaurus", "method": "Passive", "img": "https://ark.wiki.gg/images/0/03/Basilosaurus.png"},
    {"name": "Rock Drake", "method": "Steal Egg", "img": "https://ark.wiki.gg/images/d/d3/Rock_Drake.png"},
    {"name": "Reaper King", "method": "Steal Egg", "img": "https://ark.wiki.gg/images/b/bd/Reaper_King.png"},
    {"name": "Shadowmane", "method": "Passive", "img": "https://ark.wiki.gg/images/f/f2/Shadowmane.png"},
    {"name": "Voidwyrm", "method": "Passive", "img": "https://ark.wiki.gg/images/e/e0/Voidwyrm.png"},
    {"name": "Noglin", "method": "Passive", "img": "https://ark.wiki.gg/images/c/c2/Noglin.png"},
]

DATA_POKEMON_TRICKY = [
    {"name": "Sudowoodo", "type": "Rock", "ban": ["Grass"], "img": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/185.png"}, 
    {"name": "Lugia", "type": "Psychic", "ban": ["Water", "Flying"], "img": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/249.png"}, 
    {"name": "Charizard", "type": "Fire", "ban": ["Flying", "Dragon"], "img": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png"},
    {"name": "Gyarados", "type": "Water", "ban": ["Flying", "Dragon"], "img": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/130.png"}, 
    {"name": "Flygon", "type": "Ground", "ban": ["Dragon", "Bug", "Flying"], "img": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/330.png"}, 
    {"name": "Groudon", "type": "Ground", "ban": ["Fire"], "img": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/383.png"}, 
    {"name": "Tangela", "type": "Grass", "ban": ["Water"], "img": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/114.png"}, 
    {"name": "Lurantis", "type": "Grass", "ban": ["Bug", "Fairy"], "img": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/754.png"}, 
    {"name": "Dhelmise", "type": "Ghost", "ban": ["Grass", "Water"], "img": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/781.png"},
    {"name": "Pikachu", "type": "Electric", "ban": [], "img": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png"},
    {"name": "Psyduck", "type": "Water", "ban": ["Psychic"], "img": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/54.png"},
    {"name": "Grapploct", "type": "Fighting", "ban": ["Water"], "img": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/853.png"},
    {"name": "Falinks", "type": "Fighting", "ban": ["Bug"], "img": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/870.png"},
    {"name": "Stunfisk", "type": "Ground", "ban": ["Electric", "Water"], "img": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/618.png"},
    {"name": "Flabébé", "type": "Fairy", "ban": ["Grass"], "img": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/669.png"},
    {"name": "Dragalge", "type": "Poison", "ban": ["Water", "Dragon"], "img": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/691.png"},
    {"name": "Nihilego", "type": "Rock", "ban": ["Poison", "Ghost", "Water"], "img": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/793.png"},
    {"name": "Solgaleo", "type": "Steel", "ban": ["Psychic", "Fire"], "img": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/791.png"},
    {"name": "Palkia", "type": "Water", "ban": ["Dragon"], "img": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/484.png"},
    {"name": "Luxray", "type": "Electric", "ban": ["Dark"], "img": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/405.png"},
]

DATA_CRAFTING = [
    {"url": "https://ark.wiki.gg/images/9/9a/Metal_Ingot.png", "mat": "Metal", "name": "Metal Ingot"},
    {"url": "https://ark.wiki.gg/images/3/30/Flak_Chestpiece.png", "mat": "Metal", "name": "Flak Chestpiece"},
    {"url": "https://ark.wiki.gg/images/7/72/Longneck_Rifle.png", "mat": "Metal", "name": "Longneck Rifle"},
    {"url": "https://ark.wiki.gg/images/3/32/Metal_Pick.png", "mat": "Metal", "name": "Metal Pick"},
    {"url": "https://ark.wiki.gg/images/5/54/Industrial_Forge.png", "mat": "Metal", "name": "Industrial Forge"},
    {"url": "https://ark.wiki.gg/images/b/b9/Stone_Wall.png", "mat": "Stone/Wood", "name": "Stone Wall"},
    {"url": "https://ark.wiki.gg/images/e/e3/Mortar_and_Pestle.png", "mat": "Stone/Wood", "name": "Mortar and Pestle"},
    {"url": "https://ark.wiki.gg/images/1/1c/Campfire.png", "mat": "Stone/Wood", "name": "Campfire"},
    {"url": "https://ark.wiki.gg/images/7/7c/Wooden_Foundation.png", "mat": "Stone/Wood", "name": "Wooden Foundation"},
    {"url": "https://ark.wiki.gg/images/1/1a/Stone_Arrow.png", "mat": "Stone/Wood", "name": "Stone Arrow"},
    {"url": "https://ark.wiki.gg/images/b/b4/Hide_Shirt.png", "mat": "Hide/Fiber", "name": "Hide Shirt"},
    {"url": "https://ark.wiki.gg/images/a/a5/Cloth_Hat.png", "mat": "Hide/Fiber", "name": "Cloth Hat"},
    {"url": "https://ark.wiki.gg/images/6/6d/Simple_Bed.png", "mat": "Hide/Fiber", "name": "Simple Bed"},
    {"url": "https://ark.wiki.gg/images/8/88/Saddle.png", "mat": "Hide/Fiber", "name": "Saddle"},
    {"url": "https://ark.wiki.gg/images/c/c2/Bola.png", "mat": "Hide/Fiber", "name": "Bola"},
    {"url": "https://ark.wiki.gg/images/9/92/C4_Charge.png", "mat": "Advanced", "name": "C4 Charge"},
    {"url": "https://ark.wiki.gg/images/f/f4/Assault_Rifle.png", "mat": "Advanced", "name": "Assault Rifle"},
    {"url": "https://ark.wiki.gg/images/e/e8/Heavy_Auto_Turret.png", "mat": "Advanced", "name": "Heavy Auto Turret"},
    {"url": "https://ark.wiki.gg/images/2/26/Cryopod.png", "mat": "Advanced", "name": "Cryopod"},
    {"url": "https://ark.wiki.gg/images/3/37/Advanced_Rifle_Bullet.png", "mat": "Advanced", "name": "Adv. Rifle Bullet"},
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

DATA_ALPHAS = [
    {"url": "https://ark.wiki.gg/images/5/53/Alpha_Raptor.png", "name": "Alpha Raptor", "win": 200, "loss": 200, "chance": 0.70, "color": discord.Color.green()},
    {"url": "https://ark.wiki.gg/images/e/eb/Alpha_Carno.png", "name": "Alpha Carno", "win": 200, "loss": 200, "chance": 0.70, "color": discord.Color.green()},
    {"url": "https://ark.wiki.gg/images/0/03/Alpha_T-Rex.png", "name": "Alpha T-Rex", "win": 300, "loss": 300, "chance": 0.50, "color": discord.Color.gold()},
    {"url": "https://ark.wiki.gg/images/a/a2/Alpha_Fire_Wyvern.png", "name": "Alpha Wyvern", "win": 400, "loss": 400, "chance": 0.40, "color": discord.Color.red()},
    {"url": "https://ark.wiki.gg/images/f/f6/Alpha_Mosasaur.png", "name": "Alpha Mosasaur", "win": 500, "loss": 500, "chance": 0.30, "color": discord.Color.purple()},
]

SHOP_ITEMS = [
    {"name": "1 BP", "price": 15000, "desc": "Random High Quality Blueprint"},
    {"name": "1 Paint for Dino", "price": 15000, "desc": "Custom Dino Coloring"},
    {"name": "1 Breed", "price": 30000, "desc": "Dino Breeding Service"},
    {"name": "1 Ascension", "price": 30000, "desc": "Boss Ascension Unlock"},
    {"name": "1 Dedi", "price": 45000, "desc": "Tek Dedicated Storage"},
    {"name": "1 Ammo Dedi", "price": 45000, "desc": "Dedicated Storage full of Ammo"},
    {"name": "5€ Credit", "price": 45000, "desc": "Store Credit"},
    {"name": "1 Modded Cave", "price": 80000, "desc": "Exclusive Cave Location"},
    {"name": "25€ Credit", "price": 300000, "desc": "Store Credit"},
    {"name": "Private Map", "price": 500000, "desc": "Private Map Access"},
    {"name": "Reaper Queen", "price": 1000000, "desc": "R-Reaper Queen Tame"}
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
    "Patches": 1326888505216864361
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

# --- STATES ---
vault_state = {"active": False, "code": None, "prize": None, "message_id": None, "hints_task": None}
user_cooldowns = {} 
last_minigame_message = None 
points_data = {} 
active_giveaways = {} 

# --- FUNCTIONS ---
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

# CLOUD BACKUP
async def backup_points_task():
    await bot.wait_until_ready()
    try:
        channel = bot.get_channel(DB_CHANNEL_ID)
        if channel:
            found = False
            async for msg in channel.history(limit=10):
                if msg.author == bot.user and msg.attachments:
                    try:
                        data_bytes = await msg.attachments[0].read()
                        global points_data
                        points_data = json.loads(data_bytes)
                        print(f"[DB] Loaded points for {len(points_data)} users.")
                        found = True
                        break
                    except: pass
    except Exception as e: print(f"[DB ERROR] Load: {e}")

    while not bot.is_closed():
        await asyncio.sleep(120) 
        try:
            channel = bot.get_channel(DB_CHANNEL_ID)
            if channel and points_data:
                json_str = json.dumps(points_data, indent=None) 
                file_obj = discord.File(io.StringIO(json_str), filename="db_points.json")
                await channel.send(f"Backup: {int(time.time())}", file=file_obj)
                try:
                    async for msg in channel.history(limit=10):
                        if msg.author == bot.user and (time.time() - msg.created_at.timestamp()) > 10:
                            await msg.delete()
                except: pass
        except: pass

# ==========================================
# ⚙️ SETUP
# ==========================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ==========================================
# 🎮 MINIGAME VIEWS (ALL 8 GAMES)
# ==========================================

# 1. ARK DROP
class ArkDropView(discord.ui.View):
    def __init__(self): 
        super().__init__(timeout=None)
        self.grabbed = False
    @discord.ui.button(label="CLAIM DROP", style=discord.ButtonStyle.danger, emoji="🎁", custom_id="drop_claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.grabbed: return 
        self.grabbed = True
        try:
            add_points_to_user(interaction.user.id, 200)
            button.label = f"Loot: {interaction.user.name}"
            button.style = discord.ButtonStyle.secondary
            button.disabled = True
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(f"🔴 **{interaction.user.mention}** claimed the Drop (+200 pts)!", ephemeral=False)
            self.stop()
        except: pass

# 2. DINO TRAINER
class ArkTameView(discord.ui.View):
    def __init__(self, correct_method, dino_name):
        super().__init__(timeout=None)
        self.correct = correct_method
        self.dino = dino_name
        self.grabbed = False
    
    async def process(self, interaction: discord.Interaction, method: str):
        if self.grabbed: return
        self.grabbed = True
        if method == self.correct:
            add_points_to_user(interaction.user.id, 200)
            await interaction.response.send_message(f"🦕 **SUCCESS!** {interaction.user.mention} used {method} on {self.dino} (+200 pts).", ephemeral=False)
        else:
            await interaction.response.send_message(f"❌ Wrong method! {self.dino} needs **{self.correct}**.", ephemeral=False)
        
        for c in self.children: c.disabled = True
        await interaction.message.edit(view=self)
        self.stop()

    @discord.ui.button(label="Knockout 🏹", style=discord.ButtonStyle.danger)
    async def b_ko(self, interaction, button): await self.process(interaction, "Knockout")
    @discord.ui.button(label="Passive 🤲", style=discord.ButtonStyle.success)
    async def b_pas(self, interaction, button): await self.process(interaction, "Passive")
    @discord.ui.button(label="Steal Egg 🥚", style=discord.ButtonStyle.primary)
    async def b_egg(self, interaction, button): await self.process(interaction, "Steal Egg")

# 3. POKEMON TRICKY (Logic Smart + BAN LIST)
class PokemonView(discord.ui.View):
    def __init__(self, correct, name, banned_types):
        super().__init__(timeout=None)
        self.correct = correct
        self.name = name
        self.grabbed = False
        
        all_types = ["Fire", "Water", "Grass", "Rock", "Ground", "Psychic", "Ghost", "Electric", "Dragon", "Ice", "Steel", "Fairy", "Fighting", "Poison", "Flying", "Bug", "Normal", "Dark"]
        
        options = [correct]
        while len(options) < 4:
            t = random.choice(all_types)
            # LOGIC FIX: Check against ban list!
            if t not in options and t not in banned_types: 
                options.append(t)
        random.shuffle(options)
        
        for opt in options:
            self.add_item(PokemonButton(opt, opt == correct))

class PokemonButton(discord.ui.Button):
    def __init__(self, label, is_correct):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.is_correct = is_correct

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if view.grabbed: return
        view.grabbed = True
        if self.is_correct:
            add_points_to_user(interaction.user.id, 200)
            await interaction.response.send_message(f"✅ **Correct!** {interaction.user.mention} got it right (+200 pts).", ephemeral=False)
        else:
            await interaction.response.send_message(f"❌ Wrong! It was **{view.correct}**.", ephemeral=False)
        for c in view.children: c.disabled = True
        await interaction.message.edit(view=view)
        view.stop()

# 4. RAID MASTER
class RaidView(discord.ui.View):
    def __init__(self, correct_c4):
        super().__init__(timeout=None)
        self.correct = str(correct_c4)
        self.grabbed = False
        opts = [self.correct]
        while len(opts) < 3:
            r = str(random.randint(1, 20))
            if r not in opts: opts.append(r)
        random.shuffle(opts)
        for opt in opts: self.add_item(RaidButton(opt, opt == self.correct))

class RaidButton(discord.ui.Button):
    def __init__(self, label, is_correct):
        super().__init__(label=f"{label} {EMOJI_C4}", style=discord.ButtonStyle.secondary)
        self.is_correct = is_correct
    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if view.grabbed: return
        view.grabbed = True
        if self.is_correct:
            add_points_to_user(interaction.user.id, 200)
            await interaction.response.send_message(f"💥 **BOOM!** {interaction.user.mention} destroyed it! (+200 pts)", ephemeral=False)
        else:
            await interaction.response.send_message(f"❌ Not enough C4! You failed the raid.", ephemeral=False)
        for c in view.children: c.disabled = True
        await interaction.message.edit(view=view)
        view.stop()

# 5. GEOGUESSER
class GeoView(discord.ui.View):
    def __init__(self, correct_map):
        super().__init__(timeout=None)
        self.correct = correct_map
        self.grabbed = False
        all_maps = ["The Island", "Aberration", "Extinction", "Genesis 1", "Genesis 2", "Ragnarok", "Valguero", "Crystal Isles", "Lost Island", "Fjordur", "The Center", "Scorched Earth"]
        opts = [correct_map]
        while len(opts) < 4:
            m = random.choice(all_maps)
            if m not in opts: opts.append(m)
        random.shuffle(opts)
        for m in opts: self.add_item(GeoButton(m, m == correct_map))

class GeoButton(discord.ui.Button):
    def __init__(self, label, is_correct):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.is_correct = is_correct
    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if view.grabbed: return
        view.grabbed = True
        if self.is_correct:
            add_points_to_user(interaction.user.id, 200)
            await interaction.response.send_message(f"🌍 **Correct!** {interaction.user.mention} identified {self.label} (+200 pts).", ephemeral=False)
        else:
            await interaction.response.send_message(f"❌ Nope! That was {view.correct}.", ephemeral=False)
        for c in view.children: c.disabled = True
        await interaction.message.edit(view=view)
        view.stop()

# 6. ALPHA HUNT
class ArkAlphaView(discord.ui.View):
    def __init__(self, win, loss, chance): 
        super().__init__(timeout=None)
        self.win, self.loss, self.chance = win, loss, chance
        self.grabbed = False
    @discord.ui.button(label="🗡️ ATTACK ALPHA", style=discord.ButtonStyle.danger, custom_id="alpha_atk")
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.grabbed: return
        self.grabbed = True
        if random.random() < self.chance: 
            add_points_to_user(interaction.user.id, self.win)
            await interaction.response.send_message(f"🏆 **VICTORY!** {interaction.user.mention} killed the Alpha (+{self.win} pts).", ephemeral=False)
        else: 
            remove_points_from_user(interaction.user.id, self.loss)
            await interaction.response.send_message(f"💀 **DEATH...** {interaction.user.mention} died and lost **{self.loss} pts**.", ephemeral=False)
        button.disabled = True
        await interaction.message.edit(view=self)
        self.stop()

# 7. CRAFTING
class ArkCraftView(discord.ui.View):
    def __init__(self, correct_mat):
        super().__init__(timeout=None)
        self.correct_mat = correct_mat
        self.grabbed = False
    async def check_mat(self, interaction: discord.Interaction, mat_clicked: str):
        if self.grabbed: return
        self.grabbed = True
        if mat_clicked == self.correct_mat:
            add_points_to_user(interaction.user.id, 200)
            await interaction.response.send_message(f"🔨 **Correct!** {interaction.user.mention} crafted the item (+200 pts).", ephemeral=False)
        else:
            await interaction.response.send_message("❌ Wrong material. It broke.", ephemeral=False)
        for child in self.children: child.disabled = True
        await interaction.message.edit(view=self)
        self.stop()
    @discord.ui.button(label="Metal / Ingots", style=discord.ButtonStyle.secondary, custom_id="cr_metal")
    async def b1(self, i, b): await self.check_mat(i, "Metal")
    @discord.ui.button(label="Stone / Wood", style=discord.ButtonStyle.secondary, custom_id="cr_stone")
    async def b2(self, i, b): await self.check_mat(i, "Stone/Wood")
    @discord.ui.button(label="Hide / Fiber", style=discord.ButtonStyle.secondary, custom_id="cr_hide")
    async def b3(self, i, b): await self.check_mat(i, "Hide/Fiber")
    @discord.ui.button(label="Advanced", style=discord.ButtonStyle.success, custom_id="cr_adv")
    async def b4(self, i, b): await self.check_mat(i, "Advanced")

# 8. IMPRINTING
class ArkImprintView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.needs = random.choice(["Cuddle", "Walk", "Feed"])
        self.grabbed = False
    async def check(self, interaction: discord.Interaction, action: str):
        if self.grabbed: return
        self.grabbed = True
        if action == self.needs:
            add_points_to_user(interaction.user.id, 200)
            await interaction.response.send_message(f"❤️ **Imprinting increased!** {interaction.user.mention} got it right (+200 pts).", ephemeral=False)
        else:
            await interaction.response.send_message(f"😭 The baby wanted **{self.needs}**. It got angry.", ephemeral=False)
        for child in self.children: child.disabled = True
        await interaction.message.edit(view=self)
        self.stop()
    @discord.ui.button(label="Cuddle 🧸", style=discord.ButtonStyle.primary)
    async def b1(self, i, b): await self.check(i, "Cuddle")
    @discord.ui.button(label="Walk 🚶", style=discord.ButtonStyle.success)
    async def b2(self, i, b): await self.check(i, "Walk")
    @discord.ui.button(label="Feed 🍖", style=discord.ButtonStyle.danger)
    async def b3(self, i, b): await self.check(i, "Feed")

# ==========================================
# 🔄 GAME LOOP
# ==========================================
async def spawn_game(channel):
    gt = random.randint(1, 8) 
    
    if gt == 1: # Drop
        embed = discord.Embed(title="RED DROP INCOMING", color=discord.Color.red())
        embed.set_image(url=IMG_ARK_DROP)
        return await channel.send(embed=embed, view=ArkDropView())
        
    elif gt == 2: # Dino Trainer
        data = random.choice(DATA_TAME_TRICKY)
        embed = discord.Embed(title="WILD DINO SPOTTED", description=f"How do you tame a **{data['name']}**?", color=discord.Color.green())
        embed.set_image(url=data["img"])
        return await channel.send(embed=embed, view=ArkTameView(data["method"], data["name"]))
        
    elif gt == 3: # Pokemon Tricky
        data = random.choice(DATA_POKEMON_TRICKY)
        embed = discord.Embed(title="WHO IS THAT POKEMON?", description=f"What is the MAIN type of **{data['name']}**?", color=discord.Color.gold())
        embed.set_image(url=data["img"])
        return await channel.send(embed=embed, view=PokemonView(data["type"], data["name"], data["ban"]))
        
    elif gt == 4: # Raid Master
        data = random.choice(DATA_RAID)
        embed = discord.Embed(title="RAID ACADEMY", description=f"How many **C4** {EMOJI_C4} to destroy a **{data['name']}**?", color=discord.Color.orange())
        embed.set_image(url=data["img"])
        return await channel.send(embed=embed, view=RaidView(data["c4"]))
        
    elif gt == 5: # Geoguesser
        data = random.choice(DATA_GEO)
        embed = discord.Embed(title="ARK GEOGUESSER", description="Where is this location?", color=discord.Color.blue())
        embed.set_image(url=data["img"])
        return await channel.send(embed=embed, view=GeoView(data["map"]))
        
    elif gt == 6: # Alpha
        data = random.choice(DATA_ALPHAS)
        embed = discord.Embed(title=f"⚠️ {data['name'].upper()} DETECTED", description=f"Risk: -{data['loss']} | Reward: +{data['win']}", color=data['color'])
        embed.set_image(url=data["url"])
        return await channel.send(embed=embed, view=ArkAlphaView(data["win"], data["loss"], data["chance"]))

    elif gt == 7: # Crafting
        data = random.choice(DATA_CRAFTING)
        embed = discord.Embed(title="CRAFTING BENCH", description=f"Main material for: **{data['name']}**?", color=discord.Color.teal())
        embed.set_image(url=data["img"])
        return await channel.send(embed=embed, view=ArkCraftView(data["mat"]))

    elif gt == 8: # Imprinting
        img = random.choice(DATA_BREEDING_IMGS)
        embed = discord.Embed(title="BABY CRYING", description="What does the baby want?", color=discord.Color.purple())
        embed.set_image(url=img)
        return await channel.send(embed=embed, view=ArkImprintView())

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
    except Exception as e: print(f"Game Loop Error: {e}")

# ==========================================
# 🦖 DINO SCRAMBLE (Independent Loop)
# ==========================================
class DinoScrambleView(discord.ui.View):
    def __init__(self, answer):
        super().__init__(timeout=None)
        self.answer = answer
        self.grabbed = False
    
    @discord.ui.button(label="ANSWER", style=discord.ButtonStyle.success)
    async def ans(self, interaction, button):
        if self.grabbed: return await interaction.response.send_message("Too late!", ephemeral=True)
        await interaction.response.send_modal(DinoModal(self.answer)) 

class DinoModal(discord.ui.Modal, title="🦖 WHO IS THAT DINO?"):
    answer_input = discord.ui.TextInput(label="Dino Name", placeholder="Enter name...", required=True)
    def __init__(self, correct_answer):
        super().__init__()
        self.correct_answer = correct_answer
    async def on_submit(self, interaction: discord.Interaction):
        if self.answer_input.value.strip().lower() == self.correct_answer.lower():
            add_points_to_user(interaction.user.id, 200)
            await interaction.response.send_message(f"✅ Correct! (+200 pts)", ephemeral=False)
            try: await interaction.message.edit(view=None) # Stop game
            except: pass
        else: await interaction.response.send_message("❌ Wrong!", ephemeral=True)

@tasks.loop(minutes=20)
async def dino_scramble_loop():
    if not bot.is_ready(): return
    channel = bot.get_channel(DINO_CHANNEL_ID)
    if not channel: return
    try:
        history = [msg async for msg in channel.history(limit=20)]
        if len(history) > 10:
            await channel.delete_messages(history[10:])
    except: pass

    dino = random.choice(ARK_DINOS)
    scrambled = "".join(random.sample(list(dino.upper()), len(dino)))
    async for m in channel.history(limit=5):
        if m.author == bot.user and m.view:
            try: await m.edit(view=None)
            except: pass

    view = DinoScrambleView(dino)
    embed = discord.Embed(title="WHO IS THIS DINO?", description=f"🧩 `{scrambled}`", color=0xFFA500)
    view.message = await channel.send(embed=embed, view=view)

# ==========================================
# 🔘 ROLES PANEL LOGIC
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
# 🎁 ADVANCED GIVEAWAY SYSTEM
# ==========================================
@tasks.loop(seconds=10)
async def check_giveaways():
    for msg_id, data in list(active_giveaways.items()):
        if datetime.datetime.now().timestamp() >= data["end_time"]:
            channel = bot.get_channel(data["channel_id"])
            if not channel: 
                del active_giveaways[msg_id]
                continue
            
            try:
                msg = await channel.fetch_message(msg_id)
            except:
                del active_giveaways[msg_id]
                continue

            # Pick winner
            users = []
            for reaction in msg.reactions:
                if str(reaction.emoji) == "🎉":
                    async for user in reaction.users():
                        if user.bot: continue
                        # REQUIREMENT CHECK IF CHANNEL IS THE SUPPORT CHANNEL
                        if channel.id == GIVEAWAY_CHANNEL_ID:
                            member = msg.guild.get_member(user.id)
                            if member:
                                role_check = member.guild.get_role(SUPPORT_ROLE_ID)
                                if role_check in member.roles:
                                    users.append(user)
                        else:
                            # NORMAL GIVEAWAY (No restriction)
                            users.append(user)
            
            if users:
                winner_count = min(len(users), data["winners"])
                winners = random.sample(users, winner_count)
                winner_mentions = ", ".join([w.mention for w in winners])
                await channel.send(f"🎉 **GIVEAWAY ENDED** 🎉\nPrize: **{data['prize']}**\nWinners: {winner_mentions}")
            else:
                await channel.send(f"🎉 **GIVEAWAY ENDED**\nPrize: {data['prize']}\nNo valid winners.")
            
            del active_giveaways[msg_id]

@bot.tree.command(name="start_giveaway")
async def start_giveaway(interaction: discord.Interaction, time_str: str, winners: int, prize: str, channel: discord.TextChannel = None):
    if not interaction.user.guild_permissions.administrator: return
    
    # Parse time
    seconds = 0
    if time_str.endswith("s"): seconds = int(time_str[:-1])
    elif time_str.endswith("m"): seconds = int(time_str[:-1]) * 60
    elif time_str.endswith("h"): seconds = int(time_str[:-1]) * 3600
    elif time_str.endswith("d"): seconds = int(time_str[:-1]) * 86400
    else: return await interaction.response.send_message("Invalid time format (use 10s, 10m, 1h).", ephemeral=True)

    target_channel = channel if channel else interaction.channel
    end_time = datetime.datetime.now().timestamp() + seconds
    
    # RED VS GREEN LOGIC
    if target_channel.id == GIVEAWAY_CHANNEL_ID:
        color = 0xFF0000 # Red
        req_text = "\n\n⚠️ **REQUIREMENT:** Must have `! HELL WIPES...` in name to win!"
    else:
        color = 0x00FF00 # Green
        req_text = ""

    embed = discord.Embed(title="🎉 **GIVEAWAY** 🎉", description=f"**Prize:** {prize}\n**Winners:** {winners}\n**Ends:** <t:{int(end_time)}:R>{req_text}", color=color)
    
    await interaction.response.send_message(f"Giveaway started in {target_channel.mention}", ephemeral=True)
    msg = await target_channel.send(embed=embed)
    await msg.add_reaction("🎉")
    
    active_giveaways[msg.id] = {
        "end_time": end_time,
        "winners": winners,
        "prize": prize,
        "channel_id": target_channel.id
    }

# ==========================================
# ⚡ CORE EVENTS & COMMANDS
# ==========================================
@bot.event
async def on_ready():
    print(f"🔥 HELL SYSTEM ONLINE: {bot.user}")
    bot.loop.create_task(backup_points_task())
    dino_scramble_loop.start()
    minigames_auto_loop.start()
    check_giveaways.start() 
    
    # SHOP POSTING
    for guild in bot.guilds:
        ch = discord.utils.get(guild.text_channels, name=SHOP_CHANNEL_NAME)
        if not ch: continue
        last = None
        async for m in ch.history(limit=1): last = m
        if not last or last.author != bot.user:
            await ch.purge(limit=10)
            embed = discord.Embed(title=f"🔥 **BLACK MARKET** 🔥", color=0x9900FF)
            for i in SHOP_ITEMS:
                embed.add_field(name=f"{i['name']} - {i['price']} Pts", value=i['desc'], inline=False)
            await ch.send(embed=embed)

    # ROLES POSTING
    r_ch = bot.get_channel(ROLES_CHANNEL_ID)
    if r_ch:
        last_r = None
        async for m in r_ch.history(limit=1): last_r = m
        if not last_r or last_r.author != bot.user:
            await r_ch.purge(limit=5)
            embed = discord.Embed(title="🎭 **SELF ROLES**", description="Click to get notified!", color=0x00AAFF)
            await r_ch.send(embed=embed, view=RolesView())
            
    # COMMANDS POSTING
    c_ch = bot.get_channel(CMD_CHANNEL_ID)
    if c_ch:
        async for m in c_ch.history(limit=5):
            if m.author == bot.user:
                await m.delete()
                await asyncio.sleep(1.5)
        
        embed = discord.Embed(title="🛠️ **SERVER COMMANDS**", color=0x990000)
        embed.add_field(name="👤 **PLAYER COMMANDS**", value=f"{HELL_ARROW} **!recipes**\n{HELL_ARROW} **!points**\n{HELL_ARROW} **.suggest <text>**\n{HELL_ARROW} **/whitelistme**", inline=False)
        embed.set_footer(text="HELL SYSTEM • Commands")
        await c_ch.send(embed=embed)

    # AUTO HYPESQUAD LOOP
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
            await asyncio.sleep(60)
    bot.loop.create_task(check_support_roles())

@bot.event
async def on_member_update(before, after):
    name_check = after.global_name if after.global_name else after.name
    if not name_check: return
    role = after.guild.get_role(SUPPORT_ROLE_ID)
    if not role: return
    
    has_name = SUPPORT_TEXT.lower() in name_check.lower()
    
    if has_name and role not in after.roles:
        try: await after.add_roles(role)
        except: pass
        
    elif not has_name and role in after.roles:
        # REMOVE ROLE & GIVEAWAY REACTION
        try: 
            await after.remove_roles(role)
            # Scan active giveaways in the support channel
            for msg_id, data in active_giveaways.items():
                if data["channel_id"] == GIVEAWAY_CHANNEL_ID:
                    ch = bot.get_channel(GIVEAWAY_CHANNEL_ID)
                    msg = await ch.fetch_message(msg_id)
                    await msg.remove_reaction("🎉", after)
        except: pass

@bot.event
async def on_message(message):
    # 1. BOT MESSAGES IN COMMAND CHANNEL
    if message.author.bot:
        if message.channel.id == CMD_CHANNEL_ID:
            # Protect the Menu
            if message.embeds and "SERVER COMMANDS" in (message.embeds[0].title or ""):
                return
            # Delete everything else after 2m
            await message.delete(delay=120)
        return

    # 2. SUGGESTIONS
    if message.channel.id == SUGGEST_CHANNEL_ID:
        if message.content.startswith(".suggest"):
            await message.delete()
            embed = discord.Embed(description=message.content.replace(".suggest", ""), color=0xFFA500)
            embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
            m = await message.channel.send(embed=embed)
            await m.add_reaction("✅")
            await m.add_reaction("❌")
        else: await message.delete()
        return

    # 3. USER MESSAGES IN COMMAND CHANNEL
    if message.channel.id == CMD_CHANNEL_ID:
        if message.content.startswith(("!", ".", "/")):
            await message.delete(delay=120)
            await bot.process_commands(message)
        else:
            try: await message.delete() # Instant delete
            except: pass
        return

    await bot.process_commands(message)

# ADMIN CMDS
@bot.tree.command(name="add_points")
async def ap(i: discord.Interaction, user: discord.Member, amount: int):
    if not i.user.guild_permissions.administrator: return
    new_bal = add_points_to_user(user.id, amount)
    await i.response.send_message(f"✅ Added {amount} to {user.mention}. Total: {new_bal}")

@bot.tree.command(name="remove_points")
async def rp(i: discord.Interaction, user: discord.Member, amount: int):
    if not i.user.guild_permissions.administrator: return
    remove_points_from_user(user.id, amount)
    await i.response.send_message(f"✅ Removed {amount} from {user.mention}.")

@bot.command(name="points")
async def p(ctx):
    pts = get_user_points(ctx.author.id)
    m = await ctx.send(f"💰 {ctx.author.mention} you have **{pts}** points.")
    await ctx.message.delete()
    await asyncio.sleep(10)
    await m.delete()

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

# START
if __name__ == "__main__":
    if TOKEN: bot.run(TOKEN)
