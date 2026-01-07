import discord
from discord.ext import commands, tasks
import os
import asyncio
import threading
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import config 

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
# ⚙️ CONFIGURACIÓN DEL BOT
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
                print(f"❌ ERROR CRÍTICO cargando {ext}: {e}")

        try:
            synced = await self.tree.sync()
            print(f"🔄 Slash Commands sincronizados: {len(synced)}")
        except Exception as e:
            print(f"⚠️ Error sync slash: {e}")

        self.channel_sweeper.start()

    async def on_ready(self):
        print(f"🔥 HELL SYSTEM ONLINE: {self.user} (ID: {self.user.id})")

    # 🔥 CAPA 1: GESTIÓN DE MENSAJES
    async def on_message(self, message):
        if message.author.bot: return

        # Canal Sugerencias
        if message.channel.id == config.SUGGEST_CHANNEL_ID:
            # EXCEPCIÓN OWNER: Si eres tú, no hace nada (te deja escribir)
            if message.author.id == config.OWNER_ID:
                return 

            if message.content.startswith(".suggest"):
                txt = message.content[8:].strip()
                if txt:
                    try: await message.delete() 
                    except: pass
                    embed = discord.Embed(description=f"**{txt}**", color=0xffaa00)
                    embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
                    msg = await message.channel.send(embed=embed)
                    await msg.add_reaction(config.CHECK_ICON)
                    await msg.add_reaction(config.CROSS_ICON)
            else:
                try: await message.delete() 
                except: pass
            return

        # Canal Comandos
        if message.channel.id == config.CMD_CHANNEL_ID:
            await self.process_commands(message)
            if message.type != discord.MessageType.chat_input_command:
                try: await message.delete(delay=3) 
                except: pass
            return

        await self.process_commands(message)

    # 🔥 CAPA 2: BARRENDERO
    @tasks.loop(minutes=1)
    async def channel_sweeper(self):
        await self.wait_until_ready()
        channel = self.get_channel(config.CMD_CHANNEL_ID)
        if not channel: return

        now = datetime.datetime.now(datetime.timezone.utc)

        def check_msg(m):
            if m.author == self.user and m.embeds and "SERVER COMMANDS" in (m.embeds[0].title or ""):
                return False
            age = (now - m.created_at).total_seconds()
            if m.author == self.user:
                return age > 120
            return age > 10

        try:
            deleted = await channel.purge(limit=50, check=check_msg)
            if len(deleted) > 0: print(f"[SWEEPER] Limpieza: {len(deleted)}")
        except: pass

bot = HellBot()

if __name__ == "__main__":
    if config.TOKEN: 
        bot.run(config.TOKEN)
    else: 
        print("❌ ERROR: TOKEN NO ENCONTRADO")
