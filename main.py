# main.py
import discord
from discord.ext import commands
import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from config import TOKEN, CMD_CHANNEL_ID # Importamos config

# ==========================================
# 🚑 KEEP ALIVE
# ==========================================
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"HELL SYSTEM ONLINE")
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
# ⚙️ BOT SETUP
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
        extensions = [
            'cogs.systems',   
            'cogs.minigames', 
            'cogs.events',    
            'cogs.embeds'     
        ]
        for ext in extensions:
            try:
                await self.load_extension(ext)
                print(f"✅ Loaded: {ext}")
            except Exception as e:
                print(f"❌ Error loading {ext}: {e}")

        try:
            synced = await self.tree.sync()
            print(f"🔄 Slash Commands Synced: {len(synced)}")
        except Exception as e:
            print(f"⚠️ Slash Sync Error: {e}")

    async def on_ready(self):
        print(f"🔥 HELL SYSTEM ONLINE: {self.user} (ID: {self.user.id})")

    # 🔥 LIMPIEZA DE CANAL COMANDOS (AQUÍ ES INMORTAL) 🔥
    async def on_message(self, message):
        if message.author.bot: return

        # Si es el canal de comandos, borrar TODO lo que no sea slash command
        if message.channel.id == CMD_CHANNEL_ID:
            if message.type == discord.MessageType.chat_input_command: return 
            try: await message.delete(delay=2) 
            except: pass
            return
        
        # Procesar otros comandos si los hubiera
        await self.process_commands(message)

bot = HellBot()

if __name__ == "__main__":
    if TOKEN: bot.run(TOKEN)
    else: print("❌ TOKEN NOT FOUND")
