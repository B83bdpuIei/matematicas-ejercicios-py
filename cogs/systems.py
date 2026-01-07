import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import json
import io
import time
import datetime
import random
import re
import config

# ==========================================
# 🛠️ UTILS
# ==========================================
def convert_time(time_str):
    time_regex = re.compile(r"(\d+)([smhd])")
    matches = time_regex.findall(time_str.lower().replace(" ", ""))
    total = 0
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    for amount, unit in matches: total += int(amount) * time_dict[unit]
    return total if matches else -1

def parse_poll_result(content, winner_emoji):
    lines = content.split('\n')
    question = "Unknown"; answer = "Unknown"
    for line in lines:
         if "hell_arrow" in line or line.strip().startswith(">"):
             clean_q = re.sub(r'<a?:[^:]+:[0-9]+>', '', line).replace(">", "").replace("*", "").replace("_", "").strip()
             if clean_q: question = clean_q; break
    s_emoji = str(winner_emoji); found = False
    for line in lines:
        if s_emoji in line:
            answer = line.replace(s_emoji, "").strip()
            if answer.startswith("-") or answer.startswith(":"): answer = answer[1:].strip()
            found = True; break
    if not found: answer = s_emoji 
    return question, answer

# ==========================================
# 📝 MODALS (FORMULARIOS)
# ==========================================

class BaseTourStartModal(discord.ui.Modal, title="🏰 START BASE TOUR"):
    time_input = discord.ui.TextInput(label="End Time (e.g. 24h)", placeholder="24h", required=True)
    reqs_input = discord.ui.TextInput(label="Requirements", style=discord.TextStyle.paragraph, default="Crafting Station, 6 Breeders (Lined), Turret Wall/Tower, Youtube Video #HELL", required=True)
    rewards_input = discord.ui.TextInput(label="Rewards", style=discord.TextStyle.paragraph, default="15€ Dono Credit, 20 Hell Points", required=True)
    mentions_input = discord.ui.TextInput(label="Mentions", placeholder="@everyone @here", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        sec = convert_time(self.time_input.value)
        if sec <= 0: sec = 86400
        end_ts = int(time.time() + sec)
        
        embed = discord.Embed(title=f"{config.EMOJI_FIRE_ANIM} __**72H BASE TOUR EVENT**__ {config.EMOJI_FIRE_ANIM}", color=0x990000)
        embed.description = "> *Show off your fortress. Prove you rule the server.*"
        embed.add_field(name=f"{config.EMOJI_CLOCK_NEW} **TIME REMAINING:**", value=f"<t:{end_ts}:R>", inline=False)
        
        req_text = ""
        for r in self.reqs_input.value.split(','): req_text += f"{config.CHECK_ICON} **{r.strip()}**\n"
        embed.add_field(name=f"{config.HELL_ARROW} **__REQUIREMENTS__**", value=req_text, inline=False)
        
        rew_text = ""
        for r in self.rewards_input.value.split(','): rew_text += f"> {r.strip()}\n"
        embed.add_field(name=f"{config.EMOJI_REWARD} **__REWARDS__**", value=rew_text, inline=False)
        embed.add_field(name=f"{config.EMOJI_WARN} **SUBMIT VIA TICKET**", value="Open a ticket to send your video.", inline=False)
        
        content = f"||{self.mentions_input.value}||" if self.mentions_input.value else ""
        await interaction.channel.send(content=content, embed=embed)
        await interaction.response.send_message("✅ Base Tour Started!", ephemeral=True)

class BaseTourVoteModal(discord.ui.Modal, title="🗳️ START VOTING"):
    time_input = discord.ui.TextInput(label="Voting Ends In (e.g. 24h)", placeholder="24h", required=True)
    opt1_link = discord.ui.TextInput(label="Link Option 1", placeholder="https://youtu.be/...", required=True)
    opt2_link = discord.ui.TextInput(label="Link Option 2", placeholder="https://youtu.be/...", required=True)
    mentions = discord.ui.TextInput(label="Mentions", placeholder="@everyone", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        sec = convert_time(self.time_input.value)
        if sec <= 0: sec = 86400
        end_ts = int(time.time() + sec)

        embed = discord.Embed(title=f"{config.EMOJI_FIRE_ANIM} __**VOTE: BEST BASE DESIGN**__ {config.EMOJI_FIRE_ANIM}", color=0xFFD700)
        embed.description = "> *The submissions are in. Now the community decides.*\n> *Who built the ultimate fortress?*"
        embed.add_field(name=f"{config.EMOJI_CLOCK_NEW} **VOTING ENDS:**", value=f"<t:{end_ts}:R>", inline=False)
        embed.add_field(name="1️⃣ **OPTION 1**", value=f"> {self.opt1_link.value}", inline=False)
        embed.add_field(name="2️⃣ **OPTION 2**", value=f"> {self.opt2_link.value}", inline=False)
        embed.add_field(name=f"{config.EMOJI_WARN} **REACT BELOW TO VOTE**", value="Only one vote counts!", inline=False)
        
        content = f"||{self.mentions.value}||" if self.mentions.value else ""
        msg = await interaction.channel.send(content=content, embed=embed)
        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")
        await interaction.response.send_message("✅ Voting Started!", ephemeral=True)

class BaseTourFinishModal(discord.ui.Modal, title="🏆 FINISH BASE TOUR"):
    winner_name = discord.ui.TextInput(label="Winner Name", placeholder="Tribe/Player Name", required=True)
    winner_link = discord.ui.TextInput(label="Winning Video Link", placeholder="https://...", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"👑 __**BASE TOUR WINNER**__ 👑", color=0xFF0000)
        embed.description = f"The community has spoken!\n\n🏆 **CONGRATULATIONS:** **{self.winner_name.value}**\n\n📺 **WINNING TOUR:**\n{self.winner_link.value}"
        embed.set_footer(text="Open a ticket to claim your reward.")
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("✅ Event Finished!", ephemeral=True)

class WipeConfigModal(discord.ui.Modal, title="⚙️ CONFIGURE NEXT WIPE"):
    date_input = discord.ui.TextInput(label="Date (DD/MM/YYYY)", placeholder="e.g. 02/01/2026", required=True, min_length=10, max_length=10)
    time_input = discord.ui.TextInput(label="Time (HH:MM)", placeholder="e.g. 17:00", required=True, min_length=5, max_length=5)
    async def on_submit(self, interaction: discord.Interaction):
        try:
            full_str = f"{self.date_input.value.strip()} {self.time_input.value.strip()}"
            dt = datetime.datetime.strptime(full_str, "%d/%m/%Y %H:%M")
            config.wipes_data["next"] = self.date_input.value.strip()
            config.wipes_data["next_timestamp"] = int(dt.timestamp())
            if c:=interaction.guild.get_channel(config.NEXT_WIPE_CHANNEL_ID): 
                await c.edit(name=f"💀 NEXT WIPE: {config.wipes_data['next']}")
            await interaction.response.send_message(f"✅ Wipe Set: {full_str}", ephemeral=True)
        except: await interaction.response.send_message("❌ Invalid Date Format", ephemeral=True)

class GiveawayModal(discord.ui.Modal, title="🎉 START GIVEAWAY"):
    time_str = discord.ui.TextInput(label="Time (e.g. 10m, 1h)", placeholder="10m", required=True)
    prize = discord.ui.TextInput(label="Prize", placeholder="Nitrado Code", required=True)
    winners = discord.ui.TextInput(label="Winners Count", placeholder="1", required=False, default="1")
    is_bulk = discord.ui.TextInput(label="Bulk? (yes/no)", placeholder="no", required=False, default="no")
    async def on_submit(self, interaction: discord.Interaction):
        sec = convert_time(self.time_str.value)
        if sec <= 0: return await interaction.response.send_message("❌ Bad Time", ephemeral=True)
        cog = interaction.client.get_cog("Systems")
        if self.is_bulk.value.lower() == "yes": await cog.start_bulk_giveaway_logic(interaction, sec, self.prize.value, int(self.winners.value))
        else: await cog.start_giveaway_logic(interaction, sec, self.prize.value, int(self.winners.value))

class VaultModalStart(discord.ui.Modal, title="☠️ START VAULT EVENT"):
    code = discord.ui.TextInput(label="Pin Code (4 digits)", min_length=4, max_length=4, required=True)
    prize = discord.ui.TextInput(label="Loot Reward", required=True)
    async def on_submit(self, interaction: discord.Interaction):
        cog = interaction.client.get_cog("Systems")
        await cog.event_vault_logic(interaction, self.code.value, self.prize.value)

class PointsModal(discord.ui.Modal, title="💰 MANAGE POINTS"):
    user_id = discord.ui.TextInput(label="User ID", required=True)
    amount = discord.ui.TextInput(label="Amount", required=True)
    action = discord.ui.TextInput(label="Action (add/remove)", placeholder="add", required=True)
    async def on_submit(self, interaction: discord.Interaction):
        uid = self.user_id.value.strip(); amt = int(self.amount.value)
        current = config.points_data.get(uid, 0)
        if self.action.value.lower() == "add": config.points_data[uid] = current + amt
        else: config.points_data[uid] = max(0, current - amt)
        await interaction.response.send_message(f"✅ Points updated for {uid}", ephemeral=True)

class VaultModal(discord.ui.Modal, title="🔐 SECURITY"):
    code_input = discord.ui.TextInput(label="PIN", min_length=4, max_length=4)
    async def on_submit(self, interaction: discord.Interaction):
        if not config.vault_state["active"]: return await interaction.response.send_message("❌ Ended", ephemeral=True)
        if self.code_input.value == config.vault_state["code"]:
            config.vault_state["active"] = False
            uid = str(interaction.user.id)
            config.points_data[uid] = config.points_data.get(uid, 0) + 2000
            await interaction.channel.send(f"🎉 {interaction.user.mention} CRACKED THE VAULT! Prize: {config.vault_state['prize']}")
            await interaction.response.send_message("✅ GG", ephemeral=True)
        else: await interaction.response.send_message("❌ Access Denied", ephemeral=True)

class VaultView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="CRACK", style=discord.ButtonStyle.danger, custom_id="v_crack")
    async def crack(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(VaultModal())

# ==========================================
# 🧭 DASHBOARD NAVIGATION SYSTEM (THE HELENA STYLE)
# ==========================================

# --- 1. HOME SCREEN ---
class HomeSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Base Tour", emoji="🏰", description="Start, Vote, Finish Base Tours"),
            discord.SelectOption(label="Events & Giveaways", emoji="🎉", description="Giveaways, Vaults"),
            discord.SelectOption(label="Wipe & Polls", emoji="📅", description="Wipe dates, Polls"),
            discord.SelectOption(label="Economy", emoji="💰", description="Manage points")
        ]
        super().__init__(placeholder="Select A Category - Click Here", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        val = self.values[0]
        if val == "Base Tour":
            embed = discord.Embed(title="🏰 **BASE TOUR CONFIGURATION**", description="Manage the 72H Base Tour Event.\n\nSelect an action below.", color=0x2b2d31)
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1329487785857650748/1335660249704693760/recipes.png") 
            await interaction.response.edit_message(embed=embed, view=BaseTourView())
        elif val == "Events & Giveaways":
            embed = discord.Embed(title="🎉 **EVENTS & GIVEAWAYS**", description="Launch special events and prizes.", color=0x2b2d31)
            await interaction.response.edit_message(embed=embed, view=EventsSubView())
        elif val == "Wipe & Polls":
            embed = discord.Embed(title="📅 **WIPE MANAGER**", description="Configure server wipes and polls.", color=0x2b2d31)
            await interaction.response.edit_message(embed=embed, view=WipeSubView())
        elif val == "Economy":
            embed = discord.Embed(title="💰 **ECONOMY MANAGER**", description="Add or remove player points.", color=0x2b2d31)
            await interaction.response.edit_message(embed=embed, view=EconomySubView())

class HomeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HomeSelect())
        # Botón Exit para cerrar el menú
        exit_btn = discord.ui.Button(label="Exit", style=discord.ButtonStyle.danger, emoji="⛔")
        async def exit_callback(interaction): await interaction.message.delete()
        exit_btn.callback = exit_callback
        self.add_item(exit_btn)

# --- 2. BASE TOUR SUB-MENU ---
class BaseTourSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="1. Start Base Tour", emoji="▶️"),
            discord.SelectOption(label="2. Vote Base Tour", emoji="🗳️"),
            discord.SelectOption(label="3. Finish Base Tour", emoji="🏆")
        ]
        super().__init__(placeholder="Select Base Tour Action...", min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "1. Start Base Tour": await interaction.response.send_modal(BaseTourStartModal())
        elif self.values[0] == "2. Vote Base Tour": await interaction.response.send_modal(BaseTourVoteModal())
        elif self.values[0] == "3. Finish Base Tour": await interaction.response.send_modal(BaseTourFinishModal())

class BaseTourView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(BaseTourSelect())
        self.add_item(BackButton())

# --- 3. EVENTS SUB-MENU ---
class EventsSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Start Giveaway", emoji="🎉"),
            discord.SelectOption(label="Start Bulk Giveaway", emoji="🎁"),
            discord.SelectOption(label="Start Vault Event", emoji="🔐")
        ]
        super().__init__(placeholder="Select Event Action...", min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Start Giveaway": await interaction.response.send_modal(GiveawayModal())
        elif self.values[0] == "Start Bulk Giveaway": 
            m = GiveawayModal(); m.is_bulk.default = "yes"; m.title="🎁 BULK GIVEAWAY"
            await interaction.response.send_modal(m)
        elif self.values[0] == "Start Vault Event": await interaction.response.send_modal(VaultModalStart())

class EventsSubView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None); self.add_item(EventsSelect()); self.add_item(BackButton())

# --- 4. WIPE SUB-MENU ---
class WipeSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Set Next Wipe", emoji="📅"),
            discord.SelectOption(label="Finish Polls", emoji="📊"),
            discord.SelectOption(label="Force Update Channels", emoji="🔄")
        ]
        super().__init__(placeholder="Select Wipe Action...", min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Set Next Wipe": await interaction.response.send_modal(WipeConfigModal())
        elif self.values[0] == "Finish Polls":
            await interaction.response.defer(ephemeral=True)
            polls_ch = interaction.guild.get_channel(config.POLLS_CHANNEL_ID)
            if not polls_ch: return
            results = []
            async for m in polls_ch.history(limit=50):
                if "----" in m.content or not m.reactions: continue
                try: 
                    win = max(m.reactions, key=lambda r: r.count)
                    if win.count > 1:
                        q, a = parse_poll_result(m.content, win.emoji)
                        results.append(f"{config.HELL_ARROW} **{q}** : {a}")
                except: continue
            if results:
                embed = discord.Embed(title="📢 POLL RESULTS", description="\n".join(reversed(results)), color=0x990000)
                await interaction.followup.send(embed=embed)
            else: await interaction.followup.send("❌ No polls found.", ephemeral=True)
        elif self.values[0] == "Force Update Channels":
            await interaction.response.defer(ephemeral=True)
            try:
                g = interaction.guild
                l = config.wipes_data.get('last') or "?"; n = config.wipes_data.get('next') or "?"
                if c:=g.get_channel(config.LAST_WIPE_CHANNEL_ID): await c.edit(name=f"🩸 LAST WIPE: {l}")
                if c:=g.get_channel(config.NEXT_WIPE_CHANNEL_ID): await c.edit(name=f"💀 NEXT WIPE: {n}")
                await interaction.followup.send("✅ Done", ephemeral=True)
            except: await interaction.followup.send("❌ Error", ephemeral=True)

class WipeSubView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None); self.add_item(WipeSelect()); self.add_item(BackButton())

# --- 5. ECONOMY SUB-MENU ---
class EconomySelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label="Manage Points", emoji="💳")]
        super().__init__(placeholder="Select Action...", min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Manage Points": await interaction.response.send_modal(PointsModal())

class EconomySubView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None); self.add_item(EconomySelect()); self.add_item(BackButton())

# --- COMMON BACK BUTTON ---
class BackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary, emoji="◀️")
    async def callback(self, interaction: discord.Interaction):
        # VOLVER AL HOME
        embed = discord.Embed(title="⚡ **HELL KEEPER ADMINISTRATION**", color=0x2b2d31)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1329487785857650748/1335660249704693760/recipes.png")
        
        desc = "**Page: Home**\n\n"
        desc += f"🏰 **Base Tour**\n↳ Manage Start, Vote & Finish events.\n\n"
        desc += f"🎉 **Events & Giveaways**\n↳ Manage Giveaways and Vault events.\n\n"
        desc += f"📅 **Wipe & Polls**\n↳ Configure Season dates and Polls.\n\n"
        desc += f"💰 **Economy**\n↳ Manage player points."
        
        embed.description = desc
        embed.set_footer(text="Select A Category - Click Here")
        
        await interaction.response.edit_message(embed=embed, view=HomeView())

# ==========================================
# ⚙️ SYSTEMS COG (MAIN)
# ==========================================

class Systems(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backup_task.start()
        self.wipe_monitor.start()

    def cog_unload(self):
        self.backup_task.cancel()
        self.wipe_monitor.cancel()

    # --- COMMANDS ---
    @app_commands.command(name="events", description="ADMIN: Open Master Dashboard")
    async def events_menu(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator and interaction.user.id != config.OWNER_ID: return
        
        embed = discord.Embed(title="⚡ **HELL KEEPER ADMINISTRATION**", color=0x2b2d31)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1329487785857650748/1335660249704693760/recipes.png")
        
        desc = "**Page: Home**\n\n"
        desc += f"🏰 **Base Tour**\n↳ Manage Start, Vote & Finish events.\n\n"
        desc += f"🎉 **Events & Giveaways**\n↳ Manage Giveaways and Vault events.\n\n"
        desc += f"📅 **Wipe & Polls**\n↳ Configure Season dates and Polls.\n\n"
        desc += f"💰 **Economy**\n↳ Manage player points."
        
        embed.description = desc
        embed.set_footer(text="Select A Category - Click Here")
        
        await interaction.response.send_message(embed=embed, view=HomeView(), ephemeral=True)

    @app_commands.command(name="config_wipe", description="ADMIN: Quick Wipe Config")
    async def config_wipe_menu(self, interaction: discord.Interaction):
         if not interaction.user.guild_permissions.administrator: return
         # Redirige directamente al sub-menú Wipe para comodidad
         embed = discord.Embed(title="📅 **WIPE MANAGER**", description="Configure server wipes and polls.", color=0x2b2d31)
         await interaction.response.send_message(embed=embed, view=WipeSubView(), ephemeral=True)

    @commands.command(name="wipe")
    async def wipe_cmd(self, ctx):
        last = config.wipes_data.get("last", "Unknown")
        nxt = config.wipes_data.get("next", None)
        ts = config.wipes_data.get("next_timestamp", 0)
        embed = discord.Embed(title="🔥 **HELL CHRONICLES: WIPE SCHEDULE**", color=0x990000)
        embed.add_field(name=f"{config.HELL_ARROW} **LAST WIPE**", value=f"📅 `{last}`", inline=False)
        if nxt and ts > 0:
            embed.add_field(name=f"{config.HELL_ARROW} **NEXT WIPE**", value=f"📅 `{nxt}`\n{config.EMOJI_CLOCK_NEW} <t:{ts}:R>", inline=False)
        else:
             embed.add_field(name=f"{config.HELL_ARROW} **NEXT WIPE**", value="❓ **TBA**", inline=False)
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        await ctx.send(embed=embed)

    # --- LOGIC HELPERS ---
    async def start_giveaway_logic(self, interaction, seconds, prize, winners):
        end_ts = int(time.time() + seconds)
        embed = discord.Embed(title=f"{config.EMOJI_PARTY_NEW} GIVEAWAY", color=0x00FF00)
        embed.description = f"{config.EMOJI_GIFT_NEW} **Prize:** {prize}\n{config.EMOJI_CLOCK_NEW} **Ends:** <t:{end_ts}:R>\nWinners: {winners}\nReact with {config.EMOJI_PARTY_NEW}"
        await interaction.response.send_message("✅ Created", ephemeral=True)
        msg = await interaction.channel.send(embed=embed)
        await msg.add_reaction(config.EMOJI_PARTY_NEW)
        config.giveaways_data[str(msg.id)] = {"channel_id": interaction.channel_id, "end_time": end_ts, "prize": prize, "winners": winners}
        self.bot.loop.create_task(self.run_giveaway_timer(interaction.channel_id, msg.id, end_ts, prize, winners))

    async def start_bulk_giveaway_logic(self, interaction, seconds, prize_str, winners):
        prizes = [p.strip() for p in prize_str.split(',')]
        await interaction.response.send_message(f"✅ Creating {len(prizes)} giveaways...", ephemeral=True)
        end_ts = int(time.time() + seconds)
        for p in prizes:
            embed = discord.Embed(title=f"{config.EMOJI_PARTY_NEW} GIVEAWAY", color=0x00FF00)
            embed.description = f"{config.EMOJI_GIFT_NEW} **Prize:** {p}\n{config.EMOJI_CLOCK_NEW} <t:{end_ts}:R>\nReact with {config.EMOJI_PARTY_NEW}"
            msg = await interaction.channel.send(embed=embed)
            await msg.add_reaction(config.EMOJI_PARTY_NEW)
            config.giveaways_data[str(msg.id)] = {"channel_id": interaction.channel_id, "end_time": end_ts, "prize": p, "winners": winners}
            self.bot.loop.create_task(self.run_giveaway_timer(interaction.channel_id, msg.id, end_ts, p, winners))
            await asyncio.sleep(1)

    async def event_vault_logic(self, interaction, code, prize):
        ch = self.bot.get_channel(config.VAULT_CHANNEL_ID)
        if not ch: return await interaction.response.send_message("❌ No Vault Channel", ephemeral=True)
        embed = discord.Embed(title="🩸 **VAULT DETECTED**", description=f"Crack the PIN.\nReward: {prize}", color=0x8a0404)
        embed.add_field(name="📡 LEAKED DATA", value=f"`{code[0]}###`", inline=True)
        embed.set_image(url=config.VAULT_IMAGE_URL)
        msg = await ch.send(embed=embed, view=VaultView())
        config.vault_state.update({"active": True, "code": code, "prize": prize, "message_id": msg.id})
        await interaction.response.send_message("✅ Vault Started", ephemeral=True)

    # --- TASKS ---
    @tasks.loop(minutes=1)
    async def wipe_monitor(self):
        if not config.wipes_data.get("next") or not config.wipes_data.get("next_timestamp"): return
        if int(time.time()) >= config.wipes_data["next_timestamp"]:
            config.wipes_data["last"] = config.wipes_data["next"]
            config.wipes_data["next"] = None
            config.wipes_data["next_timestamp"] = 0
            try:
                g = self.bot.guilds[0]
                if c:=g.get_channel(config.LAST_WIPE_CHANNEL_ID): 
                    await c.edit(name=f"🩸 LAST WIPE: {config.wipes_data['last']}")
                if c:=g.get_channel(config.NEXT_WIPE_CHANNEL_ID): 
                    await c.edit(name="💀 NEXT WIPE: TBA")
            except: pass

    @tasks.loop(minutes=2)
    async def backup_task(self):
        await self.save_json("db_points.json", config.points_data)
        await self.save_json("db_giveaways.json", config.giveaways_data)
        await self.save_json("db_wipes.json", config.wipes_data)

    async def save_json(self, filename, data):
        try:
            channel = self.bot.get_channel(config.DB_CHANNEL_ID)
            if channel and data:
                json_str = json.dumps(data, indent=None)
                file_obj = discord.File(io.StringIO(json_str), filename=filename)
                await channel.send(f"Backup {filename}: {int(time.time())}", file=file_obj)
        except: pass

    async def run_giveaway_timer(self, cid, mid, end_time, prize, winners):
        await asyncio.sleep(end_time - time.time())
        try:
            ch = self.bot.get_channel(cid)
            msg = await ch.fetch_message(mid)
            users = [u async for u in msg.reactions[0].users() if not u.bot]
            if users:
                ws = random.sample(users, k=min(len(users), winners))
                txt = ", ".join([u.mention for u in ws])
                await ch.send(f"🎉 Winners: {txt}")
                embed = msg.embeds[0]; embed.color=discord.Color.greyple(); embed.description=f"ENDED. Winners: {txt}"; await msg.edit(embed=embed)
            else: await ch.send("No participants.")
            del config.giveaways_data[str(mid)]
        except: pass

    @wipe_monitor.before_loop
    async def before_wipe(self): await self.bot.wait_until_ready()
    @backup_task.before_loop
    async def before_backup(self): 
        await self.bot.wait_until_ready()
        try:
            channel = self.bot.get_channel(config.DB_CHANNEL_ID)
            if channel:
                print("[SYSTEMS] Loading Database...")
                async for msg in channel.history(limit=50):
                    if msg.author == self.bot.user and msg.attachments:
                        fname = msg.attachments[0].filename
                        try:
                            data = json.loads(await msg.attachments[0].read())
                            if fname == "db_points.json": config.points_data = data
                            elif fname == "db_giveaways.json": config.giveaways_data = data
                            elif fname == "db_wipes.json": config.wipes_data = data
                        except: pass
                if "last" not in config.wipes_data: config.wipes_data["last"] = "27/12/2025"
                if "next" not in config.wipes_data: config.wipes_data["next"] = None
        except: pass

async def setup(bot): await bot.add_cog(Systems(bot))
