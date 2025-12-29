import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import config 

# ==========================================
# 🔘 ROLES VIEW 
# ==========================================
class RoleButton(discord.ui.Button):
    def __init__(self, label, role_id):
        # ID Personalizada para persistencia
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
        else:
            await interaction.response.send_message("❌ Role config error. Check IDs in config.py", ephemeral=True)

class RolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Persistente
        for label, role_id in config.ROLES_CONFIG.items():
            self.add_item(RoleButton(label, role_id))

# ==========================================
# ⚙️ MAIN COG
# ==========================================

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.support_role_task.start()

    def cog_unload(self):
        self.support_role_task.cancel()

    # --- SUPPORT ROLE TASK ---
    @tasks.loop(minutes=1)
    async def support_role_task(self):
        guild = self.bot.guilds[0] if self.bot.guilds else None
        if not guild: return

        role = guild.get_role(config.SUPPORT_ROLE_ID)
        if not role: return

        for member in guild.members:
            name_check = member.global_name if member.global_name else member.name
            if not name_check: continue
            
            if config.SUPPORT_TEXT.lower() in name_check.lower():
                if role not in member.roles:
                    try: await member.add_roles(role)
                    except: pass
            else:
                if role in member.roles:
                    try: await member.remove_roles(role)
                    except: pass

    @support_role_task.before_loop
    async def before_support(self):
        await self.bot.wait_until_ready()

    # --- ON READY (AUTO-SEND & PERSISTENCE) ---
    @commands.Cog.listener()
    async def on_ready(self):
        # 1. Registrar la vista para que los botones funcionen siempre
        self.bot.add_view(RolesView())
        print("[EVENTS] Roles View Registered.")

        # 2. AUTO-ENVÍO DEL PANEL DE ROLES
        roles_channel = self.bot.get_channel(config.ROLES_CHANNEL_ID)
        if roles_channel:
            msg_exists = False
            # Buscar si ya enviamos el panel antes
            async for m in roles_channel.history(limit=20):
                if m.author == self.bot.user and m.embeds:
                    if "NOTIFICATIONS & ACCESS" in (m.embeds[0].title or ""):
                        msg_exists = True
                        break
            
            # Si no existe, lo enviamos
            if not msg_exists:
                await roles_channel.purge(limit=5) # Limpieza opcional antes de enviar
                embed = discord.Embed(title="🔔 **NOTIFICATIONS & ACCESS**", description="> Click buttons below to toggle roles.\n> Select channels you want to see.\n-----------------------------", color=0x990000)
                embed.set_footer(text="Hell Legion System • Auto-Roles")
                await roles_channel.send(embed=embed, view=RolesView())
                print("[EVENTS] Roles Panel Sent.")

        # 3. Check Shop Channel (Misma lógica, auto-envío)
        for guild in self.bot.guilds:
            shop_channel = discord.utils.get(guild.text_channels, name=config.SHOP_CHANNEL_NAME)
            if shop_channel:
                last_msg = None
                async for m in shop_channel.history(limit=1): last_msg = m
                is_shop_ok = False
                if last_msg and last_msg.author == self.bot.user and last_msg.embeds:
                    if "BLACK MARKET SHOP" in (last_msg.embeds[0].title or ""): is_shop_ok = True
                
                if not is_shop_ok:
                    await shop_channel.purge(limit=5)
                    embed = discord.Embed(title=f"{config.EMOJI_REWARD} **BLACK MARKET SHOP** {config.EMOJI_REWARD}", color=0x9900FF)
                    embed.description = f"Earn {config.EMOJI_POINTS} by winning minigames.\n**⚠️ OPEN A TICKET TO BUY ⚠️**\n━━━━━━━━━━━━━━━━━━━━━━━━"
                    for item in config.SHOP_ITEMS:
                        embed.add_field(name=f"📦 {item['name']}", value=f"{config.EMOJI_POINTS} **{item['price']}**\n*{item['desc']}*", inline=False)
                    embed.set_footer(text="Hell System • Economy")
                    await shop_channel.send(embed=embed)

        # 4. Check Commands Channel
        c_ch = self.bot.get_channel(config.CMD_CHANNEL_ID)
        if c_ch:
            async for m in c_ch.history(limit=10):
                if m.author == self.bot.user:
                    if m.embeds and "SERVER COMMANDS" in (m.embeds[0].title or ""): pass 
                    else: await m.delete()
            
            menu_exists = False
            async for m in c_ch.history(limit=10):
                 if m.author == self.bot.user and m.embeds and "SERVER COMMANDS" in (m.embeds[0].title or ""):
                     menu_exists = True
                     break
            
            if not menu_exists:
                embed = discord.Embed(title="🛠️ **SERVER COMMANDS**", color=0x990000)
                # 🔥 CAMBIO AQUÍ: QUITADO .SUGGEST, AÑADIDO !WIPE
                embed.add_field(name="👤 **PLAYER COMMANDS**", value=f"{config.HELL_ARROW} **!recipes**\n{config.HELL_ARROW} **!points**\n{config.HELL_ARROW} **!wipe**\n{config.HELL_ARROW} **/whitelistme**", inline=False)
                embed.set_footer(text="HELL SYSTEM • Commands")
                await c_ch.send(embed=embed)

    # --- MEMBER UPDATE ---
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        name_check = after.global_name if after.global_name else after.name
        if not name_check: return
        role = after.guild.get_role(config.SUPPORT_ROLE_ID)
        if not role: return

        if config.SUPPORT_TEXT.lower() in name_check.lower():
            if role not in after.roles:
                try: await after.add_roles(role)
                except: pass
        else:
            if role in after.roles:
                try: await after.remove_roles(role)
                except: pass
                try:
                    ga_channel = after.guild.get_channel(config.GIVEAWAY_CHANNEL_ID)
                    if ga_channel:
                        async for msg in ga_channel.history(limit=10):
                            await msg.remove_reaction(config.EMOJI_PARTY_NEW, after)
                except: pass

async def setup(bot):
    await bot.add_cog(Events(bot))
