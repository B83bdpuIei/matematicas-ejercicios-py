import discord
from discord.ext import commands
import os
from flask import Flask  # <--- NUEVO
import threading         # <--- NUEVO

# --- CONFIGURACIÓN DE SEGURIDAD ---
TOKEN = os.getenv('DISCORD_TOKEN')

# --- TUS IDs ---
TAG_SERVIDOR = "! HELL"
ID_ROL_VIP = 123456789       # <--- ¡Asegúrate de que aquí siguen tus IDs reales!
ID_CANAL_LOGS = 123456789    # <--- ¡Asegúrate de que aquí siguen tus IDs reales!

# Configuración colores
COLOR_HELL = 0x8B0000

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- (AQUÍ VA TODO EL CÓDIGO DE TUS EVENTOS Y COMANDOS IGUAL QUE ANTES) ---
# ... (on_ready, on_member_update, reglas, etc...)
# NO CAMBIES NADA DE TUS COMANDOS, DÉJALOS IGUAL


# --- 🛑 BLOQUE NUEVO: EL SERVIDOR FALSO PARA RENDER 🛑 ---
# Pega esto justo ANTES de la última línea (bot.run)

app = Flask(__name__)

@app.route('/')
def home():
    return "🔥 HELL KEEPER ESTÁ VIVO Y VIGILANDO."

def run_web_server():
    # Render nos da un puerto específico, lo usamos aquí
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run_web_server)
    t.start()

# Encendemos la web falsa
keep_alive()

# Encendemos el bot (ESTA DEBE SER SIEMPRE LA ÚLTIMA LÍNEA)
bot.run(TOKEN)
