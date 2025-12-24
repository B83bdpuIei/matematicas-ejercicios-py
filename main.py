# main.py
# EL CEREBRO DE ARRANQUE

import discord
from discord.ext import commands
import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from config import TOKEN # Importamos el token de config

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
    try:
        port = int(os.environ.get("PORT", 8080))
        server = HTTPServer(('0.0.0.0', port), SimpleHandler)
        server.serve_forever()
    except: pass

threading.Thread(target=run_fake_server, daemon=True).start()

# ==========================================
# ⚙️ ARRANQUE DEL BOT
# ==========================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True
intents.presences = True

class HellBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def setup_hook(self):
        # Lista de archivos a cargar desde la carpeta cogs
        extensions = [
            'cogs.systems',   # Vault, Database, Giveaways, Puntos
            'cogs.minigames', # Dino, Drop, Crafting, etc.
            'cogs.events',    # On_message, Support Roles, Shop
            'cogs.embeds'     # <--- AQUI IRÁ EL NUEVO SISTEMA (LO CREAREMOS VACIO O LLENO LUEGO)
        ]

        for ext in extensions:
            try:
                await self.load_extension(ext)
                print(f"✅ Cargado: {ext}")
            except Exception as e:
                print(f"❌ Error cargando {ext}: {e}")

        # Sincronizar comandos de barra (/)
        try:
            synced = await self.tree.sync()
            print(f"🔄 Comandos Slash sincronizados: {len(synced)}")
        except Exception as e:
            print(f"⚠️ Error sync slash: {e}")

    async def on_ready(self):
        print(f"🔥 HELL SYSTEM ONLINE: {self.user} (ID: {self.user.id})")

bot = HellBot()

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ ERROR: No hay TOKEN en config.py o variables de entorno.")
