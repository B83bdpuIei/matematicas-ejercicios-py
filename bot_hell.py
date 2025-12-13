import discord
from discord.ext import commands
import os

# --- CONFIGURACIÓN DE SEGURIDAD ---
# El bot buscará la contraseña en los archivos secretos de Render
TOKEN = os.getenv('DISCORD_TOKEN')

# --- TUS IDs (¡CAMBIA ESTO POR TUS NÚMEROS REALES!) ---
TAG_SERVIDOR = "! HELL"      # El texto que deben tener en el nombre
ID_ROL_VIP = 123456789       # <--- PEGA AQUÍ LA ID DEL ROL (ej: Demon)
ID_CANAL_LOGS = 123456789    # <--- PEGA AQUÍ LA ID DEL CANAL LOGS

# Configuración de colores
COLOR_HELL = 0x8B0000        # Rojo Oscuro Sangre

# Permisos del Bot (Necesarios para que funcione)
intents = discord.Intents.default()
intents.members = True       
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'🔥 {bot.user} está vigilando el Infierno.')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="almas pecadoras"))

# --- SISTEMA DE NOMBRES (AUTO-ROLE) ---
@bot.event
async def on_member_update(before, after):
    # Si el nombre no ha cambiado, no hacemos nada
    if before.display_name == after.display_name:
        return

    guild = after.guild
    rol_vip = guild.get_role(ID_ROL_VIP)
    canal_logs = guild.get_channel(ID_CANAL_LOGS)

    if not rol_vip:
        return

    # 1. CASO: Se ha puesto el TAG
    if TAG_SERVIDOR in after.display_name and TAG_SERVIDOR not in before.display_name:
        if rol_vip not in after.roles:
            await after.add_roles(rol_vip)
            print(f"✅ {after.name} se unió a la secta.")
            if canal_logs:
                await canal_logs.send(f"👹 **{after.mention}** ha aceptado el pacto. Rol {rol_vip.mention} añadido.")

    # 2. CASO: Se ha quitado el TAG
    elif TAG_SERVIDOR not in after.display_name and TAG_SERVIDOR in before.display_name:
        if rol_vip in after.roles:
            await after.remove_roles(rol_vip)
            print(f"❌ {after.name} rompió el pacto.")
            if canal_logs:
                await canal_logs.send(f"🚮 **{after.mention}** ha traicionado al servidor. Rol eliminado.")

# --- COMANDO PARA PUBLICAR LAS REGLAS (EMBED) ---
@bot.command()
@commands.has_permissions(administrator=True)
async def reglas(ctx):
    await ctx.message.delete() # Borra tu comando

    embed = discord.Embed(
        title="📜 CONTRACT OF THE DAMNED (Contrato de los Malditos)",
        description="Has descendido a **HELL**. Al entrar a este dominio, aceptas sellar este contrato con sangre.\nRomperlo significa el exilio eterno al vacío.",
        color=COLOR_HELL
    )
    
    # Imagen (Puedes cambiar el link si quieres otra)
    embed.set_thumbnail(url="https://i.imgur.com/8Q9QX6D.png") 
    
    embed.add_field(
        name="I. 👹 RESPETO ENTRE DEMONIOS", 
        value="La toxicidad está permitida dentro del rol (PVP), pero el racismo, homofobia o ataques personales graves están prohibidos.", 
        inline=False
    )
    embed.add_field(
        name="II. 🏰 ESTRUCTURAS DEL INFIERNO", 
        value="No construyas en zonas de artefactos o recursos críticos.\n🚫 **Spam de cimientos** = Wipe de base.", 
        inline=False
    )
    embed.add_field(
        name="III. ⚔️ GUERRA LIMPIA", 
        value="Usar **Mesh**, **Exploits** o **Hacks** = **PERMABAN**.\nSer **Insider** = Deshonra pública y Ban.", 
        inline=False
    )
    embed.add_field(
        name="IV. 🩸 IDENTIFICACIÓN", 
        value="Nombres como 'Human', '123' o invisibles están prohibidos.", 
        inline=False
    )
    
    embed.set_footer(text="🔥 HELL ADMINISTRATION • Ignorantia juris non excusat")

    await ctx.send(embed=embed)

bot.run(TOKEN)
