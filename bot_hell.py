import discord
from discord.ext import commands
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==========================================
# 🚑 ARREGLO PARA RENDER (FAKE WEB SERVER)
# ==========================================
# Esto crea una página web falsa para que Render detecte un puerto abierto
# y no te apague el bot con el error "Port scan timeout".
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"HELL BOT IS ALIVE")

def run_fake_server():
    # Render nos da un puerto en la variable 'PORT', si no, usamos 8080
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"🌍 FAKE SERVER LISTENING ON PORT {port}")
    server.serve_forever()

# Iniciamos el servidor falso en un hilo separado
threading.Thread(target=run_fake_server, daemon=True).start()

# ==========================================
# 🔐 SEGURIDAD
# ==========================================
TOKEN = os.environ.get("DISCORD_TOKEN")

if not TOKEN:
    print("❌ ERROR: Falta la variable 'DISCORD_TOKEN'.")
    # No hacemos exit() aquí para que al menos el servidor web arranque y veas el error
else:
    print("✅ TOKEN ENCONTRADO")

# ==========================================
# 🔥 CONFIGURACIÓN DE HELL
# ==========================================
SUPPORT_TEXT = "! HELL WIPES FRIDAY 100€"
SUPPORT_ROLE_ID = 1336477737594130482
GIVEAWAY_CHANNEL_ID = 1449849645495746803

# ==========================================
# ⚙️ BOT SETUP
# ==========================================
intents = discord.Intents.default()
intents.members = True          
intents.message_content = True  
intents.reactions = True
intents.presences = True 

bot = commands.Bot(command_prefix='!', intents=intents)

# ==========================================
# 🚀 EVENTOS
# ==========================================

@bot.event
async def on_ready():
    print("------------------------------------------------")
    print(f"🔥 SISTEMA HELL ONLINE - {bot.user}")
    print(f"👀 Rastreando: {SUPPORT_TEXT}")
    print("------------------------------------------------")

    # --- ESCÁNER DE INICIO (LO QUE PEDISTE) ---
    print("🔄 INICIANDO ESCANEO DE MIEMBROS EXISTENTES...")
    
    # Recorremos todos los servidores donde esté el bot
    for guild in bot.guilds:
        role = guild.get_role(SUPPORT_ROLE_ID)
        if not role:
            print(f"   [!] Rol no encontrado en {guild.name}")
            continue
            
        # Revisamos miembro a miembro
        count = 0
        for member in guild.members:
            # Lógica de detección de nombre
            name_check = member.global_name if member.global_name else member.name
            if not name_check: continue

            name_has_tag = SUPPORT_TEXT.lower() in name_check.lower()
            has_role = role in member.roles

            # Solo actuamos si TIENE el nombre pero NO el rol
            if name_has_tag and not has_role:
                try:
                    await member.add_roles(role)
                    print(f"   [+] ROL DADO (Scan): {name_check}")
                    count += 1
                except:
                    pass # Error de permisos o bot
        
        print(f"✅ ESCANEO COMPLETADO en {guild.name}: {count} roles entregados.")
    print("------------------------------------------------")

@bot.event
async def on_member_update(before, after):
    """Detecta cambios en vivo."""
    # 1. Obtenemos el nombre REAL (Global)
    name_check = after.global_name if after.global_name else after.name
    if not name_check: return

    guild = after.guild
    role = guild.get_role(SUPPORT_ROLE_ID)
    if not role: return

    # 2. Comprobamos lógica
    name_has_tag = SUPPORT_TEXT.lower() in name_check.lower()
    has_role = role in after.roles

    # Optimizacion: Si no hay cambio de estado, salir
    if name_has_tag == has_role: return

    # --- CASO A: PONE EL NOMBRE ---
    if name_has_tag and not has_role:
        try:
            await after.add_roles(role)
            print(f"[+] ROL DADO a: {name_check}")
        except discord.Forbidden:
            print(f"[!] ERROR PERMISOS: Sube el rol del Bot.")

    # --- CASO B: QUITA EL NOMBRE (Anti-Cheat) ---
    elif not name_has_tag and has_role:
        try:
            await after.remove_roles(role)
            print(f"[-] ROL QUITADO a: {name_check}")
            
            # Anti-Cheat: Borrar reacciones
            giveaway_channel = guild.get_channel(GIVEAWAY_CHANNEL_ID)
            if giveaway_channel:
                async for message in giveaway_channel.history(limit=20):
                    for reaction in message.reactions:
                        try:
                            await message.remove_reaction(reaction.emoji, after)
                            print(f"   [x] REACCIÓN BORRADA de sorteos")
                        except:
                            pass
        except discord.Forbidden:
            print(f"[!] PERMISOS: No puedo gestionar a este usuario.")

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
