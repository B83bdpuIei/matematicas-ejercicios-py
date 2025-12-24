# config.py
# AQUÍ GUARDAMOS DATOS GLOBALES PARA QUE NO MOLESTEN EN EL CÓDIGO

import os

# ====================
# 🔐 VARIABLES
# ====================
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
DB_CHANNEL_ID = 1451330350436323348

SHOP_CHANNEL_NAME = "「🔥」hell-store"
SUPPORT_TEXT = "! HELL WIPES FRIDAY 100€"
SUPPORT_ROLE_ID = 1336477737594130482

# ====================
# 🖼️ EMOJIS & IMAGENES
# ====================
SERVER_EMOJIS = {
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

# ALIASES DE EMOJIS (Para facilitar uso)
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

# IMAGENES Y DATOS FIJOS
IMG_ARK_DROP = "https://ark.wiki.gg/images/e/e3/Supply_Crate_Level_60.png"
VAULT_IMAGE_URL = "https://ark.wiki.gg/images/thumb/8/88/Vault.png/300px-Vault.png"

ARK_DINOS = ["Raptor", "Rex", "Argentavis", "Pteranodon", "Giganotosaurus", "Triceratops", "Stegosaurus", "Brontosaurus", "Parasaur", "Dodo"]

# ROLES (Si tienes los IDs, los pones aquí, si no, lo dejo vacío para que no falle)
ROLES_CONFIG = {
    # "Nombre del rol": ID_DEL_ROL,
}

SHOP_ITEMS = [
    {"name": "1 BP", "price": 15000, "desc": "Random High Quality Blueprint"},
    # Puedes añadir más aquí
]

# DATOS MINIJUEGOS (Para no llenar el otro archivo)
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

# VARIABLES GLOBALES DE DATOS (SE USAN EN TODOS LADOS)
points_data = {} 
giveaways_data = {} 
vault_state = {"active": False, "code": None, "prize": None, "message_id": None, "hints_task": None}
user_cooldowns = {}
embeds_data = {} # Para el nuevo sistema
autosend_data = {} # Para el nuevo sistema
menus_data = {} # Para el nuevo sistema
