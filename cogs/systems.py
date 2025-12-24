import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import json
import io
import time
import random
import re
import config

def convert_time(time_str):
    time_regex = re.compile(r"(\d+)([smhd])")
    matches = time_regex.findall(time_str.lower().replace(" ", ""))
    total_seconds = 0
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    if not matches: return -1
    for amount, unit in matches:
        total_seconds += int(amount) * time_dict[unit]
    return total_seconds

def parse_poll_result(content, winner_emoji):
    lines = content.split('\n')
    question = "Unknown Question"
    answer = "Unknown Answer"
    for line in lines:
         if "hell_arrow" in line or line.strip().startswith(">"):
             clean_q = re.sub(r'<a?:[^:]+:[0-9]+>', '', line)
             clean_q = clean_q.replace(">", "").replace("*", "").replace("_", "").strip()
             if clean_q: question = clean_q
             break
    s_emoji = str(winner_emoji)
    found = False
    for line in lines:
        if s_emoji in line:
            answer = line.replace(s_emoji, "").strip()
            if answer.startswith("-") or answer.startswith(":"): answer = answer[1:].strip()
            found = True
            break
    if not found: answer = s_emoji 
    return question, answer

class VaultModal(discord.ui.Modal, title="🔐 SECURITY OVERRIDE"):
    code_input = discord.ui.TextInput(label="INSERT PIN CODE", placeholder="####", min_length=4, max_length=4, required=True)
    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        current_time = time.time()
        
        if user_id in config.user_cooldowns:
            remaining = 15 - (current_time - config.user_cooldowns[user_id])
            if remaining > 0:
                await interaction.response.send_message(f"{config.EMOJI_VAULT_WAIT} Wait **{int(remaining)}s**...", ephemeral=True)
                return
        config.user_cooldowns[user_id] = current_time

        if not config.vault_state["active"]:
            await interaction.response.send_message("❌ Event ended.", ephemeral=True)
            return

        if self.code_input.value == config.vault_state["code"]:
            config.vault_state["active"] = False 
            if config.vault_state["hints_task"]: config.vault_state["hints_task"].cancel()
            
            uid = str(user_id)
            config.points_data[uid] = config.points_data.get(uid, 0) + 2000
            
            try:
                ch = interaction.guild.get_channel(config.VAULT_CHANNEL_ID)
                original_msg = await ch.fetch_message(config.vault_state["message_id"])
                view = VaultView()
                for child in view.children:
                    child.disabled = True
                    child.label = "VAULT CRACKED"
                    child.style = discord.ButtonStyle.secondary
                await original_msg.edit(view=view)
            except: pass

            embed = discord.Embed(title=f"{config.EMOJI_PARTY_NEW} VAULT CRACKED! {config.EMOJI_PARTY_NEW}", color=0xFFD700)
            embed.description = (
                f"{config.EMOJI_VAULT_WINNER_CROWN} **WINNER:** {interaction.user.mention}\n"
                f"{config.EMOJI_VAULT_CODE_ICON} **CODE:** `{config.vault_state['code']}`\n"
                f"{config.EMOJI_GIFT_NEW} **LOOT:** {config.vault_state['prize']}\n"
                f"{config.EMOJI_POINTS} **BONUS:** +2000"
            )
            embed.set_footer(text="HELL SYSTEM • Vault Event")
            embed.set_image(url="https://media1.tenor.com/m/X9kF3Qv1mJAAAAAC/open-safe.gif")
            if interaction.channel: await interaction.channel.send(embed=embed)
            await interaction.response.defer()
        else:
            await interaction.response.send_message(f"{config.EMOJI_VAULT_DENIED} **ACCESS DENIED.**", ephemeral=True)

class VaultView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="ATTEMPT HACK", style=discord.ButtonStyle.danger, emoji="☠️", custom_id="vault_btn")
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not config.vault_state["active"]:
             await interaction.response.send_message("❌ Event ended.", ephemeral=True)
             return
        await interaction.response.send_modal(VaultModal())

class Systems(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backup_task.start()

    def cog_unload(self):
        self.backup_task.cancel()

    @tasks.loop(minutes=2)
    async def backup_task(self):
        await self.save_json("db_points.json", config.points_data)
        await self.save_json("db_giveaways.json", config.giveaways_data)
        await self.save_json("db_embeds.json", config.embeds_data)
        await self.save_json("db_autosend.json", config.autosend_data)
        await self.save_json("db_menus.json", config.menus_data)

    async def save_json(self, filename, data):
        try:
            channel = self.bot.get_channel(config.DB_CHANNEL_ID)
            if channel and data:
                json_str = json.dumps(data, indent=None)
                file_obj = discord.File(io.StringIO(json_str), filename=filename)
                await channel.send(f"Backup {filename}: {int(time.time())}", file=file_obj)
        except: pass

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
                            elif fname == "db_embeds.json": config.embeds_data = data
                            elif fname == "db_autosend.json": config.autosend_data = data
                            elif fname == "db_menus.json": config.menus_data = data
                        except: pass
                
                for msg_id, gdata in list(config.giveaways_data.items()):
                    self.bot.loop.create_task(self.run_giveaway_timer(
                        int(gdata["channel_id"]), int(msg_id), gdata["end_time"], gdata["prize"], gdata["winners"]
                    ))
                print("[SYSTEMS] Database Loaded.")
        except Exception as e:
            print(f"[SYSTEMS ERROR] DB Load Failed: {e}")

    @app_commands.command(name="add_points", description="ADMIN: Add points to a user")
    async def add_points(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        if not interaction.user.guild_permissions.administrator: return
        uid = str(user.id)
        config.points_data[uid] = config.points_data.get(uid, 0) + amount
        await interaction.response.send_message(f"✅ {user.mention} +{amount} (Total: {config.points_data[uid]})")

    @app_commands.command(name="remove_points", description="ADMIN: Remove points from a user")
    async def remove_points(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        if not interaction.user.guild_permissions.administrator: return
        uid = str(user.id)
        current = config.points_data.get(uid, 0)
        config.points_data[uid] = max(0, current - amount)
        await interaction.response.send_message(f"✅ {user.mention} -{amount}")

    @commands.command(name="points")
    async def check_points(self, ctx):
        bal = config.points_data.get(str(ctx.author.id), 0)
        msg = await ctx.send(f"💰 {ctx.author.mention}: **{bal}** Points.")
        try:
            await ctx.message.delete()
            await asyncio.sleep(10)
            await msg.delete()
        except: pass

    @app_commands.command(name="event_vault", description="Start a Vault event")
    async def event_vault(self, interaction: discord.Interaction, code: str, prize: str):
        if not interaction.user.guild_permissions.administrator: return
        ch = self.bot.get_channel(config.VAULT_CHANNEL_ID)
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(title=f"{config.EMOJI_BLOOD} **VAULT DETECTED**", description=f"Crack the PIN.\nReward: {prize}", color=0x8a0404)
        embed.add_field(name="📡 LEAKED DATA", value=f"`{code[0]}###`", inline=True)
        embed.set_image(url=config.VAULT_IMAGE_URL)
        
        msg = await ch.send(embed=embed, view=VaultView())
        
        config.vault_state.update({"active": True, "code": code, "prize": prize, "message_id": msg.id})
        if config.vault_state["hints_task"]: config.vault_state["hints_task"].cancel()
        config.vault_state["hints_task"] = asyncio.create_task(self.manage_vault_hints(ch, msg, code))
        
        await interaction.followup.send("✅ Vault Started.")

    async def manage_vault_hints(self, channel, message, code):
        try:
            await asyncio.sleep(18000) 
            if not config.vault_state["active"]: return
            embed = message.embeds[0]
            embed.set_field_at(0, name="📡 LEAKED DATA", value=f"`{code[:2]}##`", inline=True)
            await message.edit(embed=embed)
            
            await asyncio.sleep(68400) 
            if not config.vault_state["active"]: return
            embed.set_field_at(0, name="📡 LEAKED DATA", value=f"`{code[:3]}#`", inline=True)
            await message.edit(embed=embed)
        except: pass

    async def run_giveaway_timer(self, cid, mid, end_time, prize, winners):
        await asyncio.sleep(end_time - time.time())
        try:
            ch = self.bot.get_channel(cid)
            if not ch: return
            msg = await ch.fetch_message(mid)
            
            users = []
            for reaction in msg.reactions:
                if str(reaction.emoji) == config.EMOJI_PARTY_NEW:
                    async for user in reaction.users():
                        if not user.bot: users.append(user)
            
            if users:
                ws = random.sample(users, k=min(len(users), winners))
                w_txt = ", ".join([u.mention for u in ws])
                
                embed = msg.embeds[0]
                embed.color = discord.Color.greyple()
                embed.description = (
                    f"{config.EMOJI_GIFT_NEW} **Prize:** {prize}\n"
                    f"{config.EMOJI_GIVEAWAY_ENDED_RED} **ENDED**\n"
                    f"{config.EMOJI_GIVEAWAY_WINNER_CROWN} **Winners:** {w_txt}"
                )
                await msg.edit(embed=embed)
                await ch.send(f"🎉 **CONGRATULATIONS** {w_txt}! You won **{prize}**!")
            else:
                await ch.send(f"❌ Giveaway for **{prize}** ended without participants.")

            if str(mid) in config.giveaways_data:
                del config.giveaways_data[str(mid)]
        except: pass

    @app_commands.command(name="start_giveaway", description="Start a single giveaway")
    async def start_giveaway(self, interaction: discord.Interaction, time_str: str, prize: str, winners: int = 1):
        if not interaction.user.guild_permissions.administrator:
             await interaction.response.send_message("❌ No permissions.", ephemeral=True)
             return
        
        seconds = convert_time(time_str)
        if seconds <= 0: return await interaction.response.send_message("❌ Invalid time format.", ephemeral=True)

        is_sponsor = (interaction.channel_id == config.GIVEAWAY_CHANNEL_ID)
        
        embed = discord.Embed(
            title=f"{config.EMOJI_FIRE_ANIM} HELL SPONSOR GIVEAWAY {config.EMOJI_FIRE_ANIM}" if is_sponsor else f"{config.EMOJI_PARTY_NEW} GIVEAWAY",
            color=0x990000 if is_sponsor else 0x00FF00
        )
        end_ts = int(time.time() + seconds)
        
        warning_text = f"\n{config.EMOJI_WARN} **ANTI-CHEAT ACTIVE: Remove name tag = Auto-Kick**" if is_sponsor else ""
        
        embed.description = (
            f"{config.EMOJI_GIFT_NEW} **Prize:** {prize}\n"
            f"{config.EMOJI_CLOCK_NEW} **Ends:** <t:{end_ts}:R>\n"
            f"{config.EMOJI_VAULT_WINNER_CROWN} **Winners:** {winners}\n"
            f"{warning_text}\n"
            f"React with {config.EMOJI_PARTY_NEW} to enter!"
        )
        embed.set_footer(text="Hell System • Giveaway")
        
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        await msg.add_reaction(config.EMOJI_PARTY_NEW)
        
        config.giveaways_data[str(msg.id)] = {
            "channel_id": interaction.channel_id,
            "end_time": end_ts,
            "prize": prize,
            "winners": winners
        }
        self.bot.loop.create_task(self.run_giveaway_timer(interaction.channel_id, msg.id, end_ts, prize, winners))

    @app_commands.command(name="start_bulk_giveaway", description="Create multiple giveaways")
    async def start_bulk_giveaway(self, interaction: discord.Interaction, time_str: str, prizes_list: str, winners_per_giveaway: int = 1):
        if not interaction.user.guild_permissions.administrator: return
        seconds = convert_time(time_str)
        if seconds <= 0: return await interaction.response.send_message("❌ Invalid time.", ephemeral=True)

        prizes = [p.strip() for p in prizes_list.split(',')]
        await interaction.response.send_message(f"✅ Creating **{len(prizes)}** giveaways...", ephemeral=True)

        is_sponsor = (interaction.channel_id == config.GIVEAWAY_CHANNEL_ID)
        end_ts = int(time.time() + seconds)
        warning_text = f"\n{config.EMOJI_WARN} **ANTI-CHEAT ACTIVE: Remove name tag = Auto-Kick**" if is_sponsor else ""

        for prize in prizes:
            embed = discord.Embed(
                title=f"{config.EMOJI_FIRE_ANIM} HELL SPONSOR GIVEAWAY" if is_sponsor else f"{config.EMOJI_PARTY_NEW} GIVEAWAY",
                color=0x990000 if is_sponsor else 0x00FF00
            )
            embed.description = (
                f"{config.EMOJI_GIFT_NEW} **Prize:** {prize}\n"
                f"{config.EMOJI_CLOCK_NEW} **Ends:** <t:{end_ts}:R>\n"
                f"{config.EMOJI_VAULT_WINNER_CROWN} **Winners:** {winners_per_giveaway}\n"
                f"{warning_text}\n"
                f"React with {config.EMOJI_PARTY_NEW} to enter!"
            )
            embed.set_footer(text="Hell System • Giveaway")
            
            msg = await interaction.channel.send(embed=embed)
            await msg.add_reaction(config.EMOJI_PARTY_NEW)

            config.giveaways_data[str(msg.id)] = {
                "channel_id": interaction.channel_id,
                "end_time": end_ts,
                "prize": prize,
                "winners": winners_per_giveaway
            }
            self.bot.loop.create_task(self.run_giveaway_timer(interaction.channel_id, msg.id, end_ts, prize, winners_per_giveaway))
            await asyncio.sleep(1)

    @app_commands.command(name="finish_polls", description="Clean and publish poll results")
    async def finish_polls(self, interaction: discord.Interaction):
        try: await interaction.response.defer()
        except: return 
        if not interaction.user.guild_permissions.administrator: return
        
        polls_channel = self.bot.get_channel(config.POLLS_CHANNEL_ID)
        if not polls_channel: return

        target_date = None
        async for last_msg in polls_channel.history(limit=1):
            target_date = last_msg.created_at.date()
        
        if not target_date: return

        results_list = []
        async for message in polls_channel.history(limit=50):
            if message.created_at.date() != target_date: break 
            if not message.content or not message.reactions: continue 
            if "----" in message.content: continue

            try: winner_reaction = max(message.reactions, key=lambda r: r.count)
            except: continue

            if winner_reaction.count >= 1: 
                question, answer_text = parse_poll_result(message.content, winner_reaction.emoji)
                line = f"{config.HELL_ARROW} **{question}** : {answer_text}"
                results_list.append(line)

        if not results_list:
            await interaction.followup.send(f"⚠️ No polls found for {target_date}.", ephemeral=True)
            return

        results_list.reverse()
        full_content = "\n".join(results_list)
        header = f"📢 **POLL RESULTS**\n📅 {target_date}\n\n"
        final_text = header + full_content

        if len(final_text) <= 4000:
            embed = discord.Embed(description=final_text, color=0x990000)
            embed.set_footer(text="Hell System polls")
            await interaction.followup.send(embed=embed)
        else:
            chunks = [final_text[i:i+4000] for i in range(0, len(final_text), 4000)]
            for i, chunk in enumerate(chunks):
                embed = discord.Embed(description=chunk, color=0x990000)
                await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Systems(bot))
