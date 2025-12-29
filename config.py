import os

# ====================
# 🔐 VARIABLES
# ====================
TOKEN = os.environ.get("DISCORD_TOKEN")

# CANALES
GIVEAWAY_CHANNEL_ID = 1449849645495746803 
POLLS_CHANNEL_ID = 1449083865862770819       
CMD_CHANNEL_ID = 1449346777659609288
ROLES_CHANNEL_ID = 1449083960578670614
SUGGEST_CHANNEL_ID = 1449346646465839134
VAULT_CHANNEL_ID = 1450244608817762465
DINO_CHANNEL_ID = 1450244689285353544 
MINIGAMES_CHANNEL_ID = 1450244729848598618
DB_CHANNEL_ID = 1451330350436323348

SHOP_CHANNEL_NAME = "「🔥」hell-store"

# CANALES DE WIPE (VOZ)
LAST_WIPE_CHANNEL_ID = 1454812627887853668
NEXT_WIPE_CHANNEL_ID = 1454813012182569020

# DATOS DE SOPORTE
SUPPORT_TEXT = "! HELL WIPES SATURDAY"
SUPPORT_ROLE_ID = 1336477737594130482

# ====================
# 🔘 CONFIGURACIÓN DE AUTO-ROLES
# ====================
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

# ====================
# 🖼️ EMOJIS
# ====================
SERVER_EMOJIS = {
    "emoji_9": "<a:emoji_9:868224374333919333>",
    "party": "<a:party:1137005680520331304>",
    "hell_arrow": "<a:hell_arrow:1211049707128750080>",
    "yelow_crown": "<a:yelow_crown:1219625559747858523>",
    "notification": "<a:notification:1275469575638614097>",
    "fire": "<a:fire:1275469598183002183>",
    "warn": "<a:warn:1275471955138711572>",
    "emoji_68": "<a:emoji_68:1328804237546881126>", 
    "emoji_69": "<a:emoji_69:1328804255741771899>", 
    "Check": "<a:Check:1336817519364669511>",
    "Purple_Clock": "<a:Purple_Clock:1336818117094936587>",
    "Red_Clock": "<a:Red_Clock:1336818629743738963>",
    "Check_hell": "<a:Check_hell:1450255850508779621>",
    "cruz_hell": "<a:cruz_hell:1450255934273355918>",
    "pikachu_culon": "<:pikachu_culon:1450624552827752479>", 
    "Gift_hell": "<a:Gift_hell:1450624953723654164>",
    "party_new": "<a:party:1450625235383488649>", 
    "greenarrow": "<a:greenarrow:1450625398051311667>",
    "Pokecoin": "<:Pokecoin:1450625492309901495>", 
    "Red": "<a:Red:931298336458301520>",
    "Good_2": "<a:Good_2:930098652804952074>",
    "C4_HELL": "<:C4_HELL:1451357075321131049>",
    "emoji_75": "<a:emoji_75:1317875418782498858>"
}

# ALIASES
HELL_ARROW = SERVER_EMOJIS["hell_arrow"]
CHECK_ICON = SERVER_EMOJIS["Check_hell"]
CROSS_ICON = SERVER_EMOJIS["cruz_hell"]
EMOJI_BLOOD = SERVER_EMOJIS["emoji_75"]
EMOJI_DINO_TITLE = SERVER_EMOJIS["pikachu_culon"]
EMOJI_REWARD = SERVER_EMOJIS["Gift_hell"]
EMOJI_CORRECT = SERVER_EMOJIS["Good_2"]
EMOJI_WINNER = SERVER_EMOJIS["party_new"]
EMOJI_ANSWER = SERVER_EMOJIS["greenarrow"]
EMOJI_POINTS = SERVER_EMOJIS["Pokecoin"]
EMOJI_PARTY_NEW = SERVER_EMOJIS["party_new"]
EMOJI_GIFT_NEW = SERVER_EMOJIS["Gift_hell"]
EMOJI_FIRE_ANIM = SERVER_EMOJIS["emoji_9"]
EMOJI_CLOCK_NEW = SERVER_EMOJIS["Purple_Clock"]
EMOJI_VAULT_WINNER_CROWN = SERVER_EMOJIS["yelow_crown"]
EMOJI_VAULT_CODE_ICON = SERVER_EMOJIS["emoji_69"]
EMOJI_GIVEAWAY_ENDED_RED = SERVER_EMOJIS["Red"]
EMOJI_GIVEAWAY_WINNER_CROWN = SERVER_EMOJIS["yelow_crown"]
EMOJI_VAULT_WAIT = SERVER_EMOJIS["Red_Clock"]
EMOJI_VAULT_DENIED = SERVER_EMOJIS["warn"]
EMOJI_WARN = SERVER_EMOJIS["warn"]

# DATOS FIJOS
IMG_ARK_DROP = "https://ark.wiki.gg/images/e/e3/Supply_Crate_Level_60.png"
VAULT_IMAGE_URL = "https://ark.wiki.gg/images/thumb/8/88/Vault.png/300px-Vault.png"

ARK_DINOS = ["Raptor", "Rex", "Argentavis", "Pteranodon", "Giganotosaurus", "Triceratops", "Stegosaurus", "Brontosaurus", "Parasaur", "Dodo"]

SHOP_ITEMS = [
    {"name": "1 BP", "price": 15000, "desc": "Random High Quality Blueprint"},
]

DATA_TAMING = [
    {"url": "https://ark.wiki.gg/images/e/e6/Raptor.png", "food": "Raw Meat", "name": "Raptor"},
    {"url": "https://ark.wiki.gg/images/1/1f/Rex.png", "food": "Raw Meat", "name": "Rex"}
]
DATA_CRAFTING = [
    {"url": "https://ark.wiki.gg/images/9/9a/Metal_Ingot.png", "mat": "Metal", "name": "Metal Ingot"},
    {"url": "https://ark.wiki.gg/images/4/43/Polymer.png", "mat": "Advanced", "name": "Polymer"}
]
DATA_BREEDING_IMGS = ["https://ark.wiki.gg/images/e/e3/Fertilized_Rex_Egg.png"]
DATA_ALPHAS = [
    {"url": "https://ark.wiki.gg/images/5/53/Alpha_Raptor.png", "name": "Alpha Raptor", "win": 200, "loss": 200, "chance": 0.70, "color": 0x00FF00}
]
DATA_POKEMON = [
    {"url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png", "type": "Fire", "name": "Charizard"}
]

# VARIABLES GLOBALES
points_data = {} 
giveaways_data = {} 
vault_state = {"active": False, "code": None, "prize": None, "message_id": None, "hints_task": None}
user_cooldowns = {}
embeds_data = {} 
autosend_data = {} 
menus_data = {} 
wipes_data = {
    "last": "27/12/2025", 
    "next": None, 
    "next_timestamp": 0
}
