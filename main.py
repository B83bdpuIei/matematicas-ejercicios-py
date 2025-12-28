import discord
from discord.ext import commands
import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import config # Importamos TODA la configuración para usar iconos y canales

# ==========================================
# 🚑 KEEP ALIVE (Para que no se duerma en Render)
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
        # Cargar todos los módulos
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

        # Sincronizar comandos de barra
        try:
            synced = await self.tree.sync()
            print(f"🔄 Slash Commands Synced: {len(synced)}")
        except Exception as e:
            print(f"⚠️ Slash Sync Error: {e}")

    async def on_ready(self):
        print(f"🔥 HELL SYSTEM ONLINE: {self.user} (ID: {self.user.id})")

    # 🔥 GESTOR DE MENSAJES CENTRAL (Sugerencias + Limpieza) 🔥
    async def on_message(self, message):
        if message.author.bot: return

        # 1. SISTEMA DE SUGERENCIAS (.suggest)
        # Si estamos en el canal de sugerencias y empieza por .suggest
        if message.channel.id == config.SUGGEST_CHANNEL_ID:
            if message.content.startswith(".suggest"):
                txt = message.content[8:].strip()
                if txt:
                    # Borramos el mensaje del usuario
                    try: await message.delete() 
                    except: pass
                    
                    # Creamos el embed bonito
                    embed = discord.Embed(description=f"**{txt}**", color=0xffaa00)
                    embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
                    msg = await message.channel.send(embed=embed)
                    
                    # Añadimos reacciones
                    await msg.add_reaction(config.CHECK_ICON)
                    await msg.add_reaction(config.CROSS_ICON)
            else:
                # Si escribe algo que no es una sugerencia, se borra
                try: await message.delete() 
                except: pass
            return # Paramos aquí para este canal

        # 2. CANAL DE COMANDOS (Limpieza + Ejecución)
        if message.channel.id == config.CMD_CHANNEL_ID:
            # PRIMERO: Intentamos procesar si es un comando (como !recipes)
            await self.process_commands(message)
            
            # SEGUNDO: Si no es un comando de barra (/), programamos su borrado
            if message.type != discord.MessageType.chat_input_command:
                try: await message.delete(delay=2) 
                except: pass
            return

        # 3. RESTO DE CANALES (Procesar comandos normales)
        await self.process_commands(message)

bot = HellBot()

if __name__ == "__main__":
    if config.TOKEN: 
        bot.run(config.TOKEN)
    else: 
        print("❌ TOKEN NOT FOUND")
