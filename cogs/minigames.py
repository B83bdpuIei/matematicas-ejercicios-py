import discord
from discord.ext import commands, tasks
import random
import asyncio
import config

class DinoModal(discord.ui.Modal, title="🦖 WHO IS THAT DINO?"):
    answer_input = discord.ui.TextInput(label="Dino Name", placeholder="Enter name...", required=True)
    def __init__(self, correct_answer):
        super().__init__()
        self.correct_answer = correct_answer
        self.view_ref = None
    async def on_submit(self, interaction: discord.Interaction):
        guess = self.answer_input.value.strip().lower()
        if self.view_ref and self.view_ref.grabbed:
             await interaction.response.send_message("❌ Someone was faster.", ephemeral=True)
             return
        if guess == self.correct_answer.lower():
            if self.view_ref: self.view_ref.grabbed = True 
            points_won = 200 
            uid = str(interaction.user.id)
            config.points_data[uid] = config.points_data.get(uid, 0) + points_won
            try: await interaction.response.send_message(f"{config.EMOJI_CORRECT} **CORRECT!**", ephemeral=True)
            except: pass
            embed = discord.Embed(color=0x00FF00)
            embed.description = (f"{config.EMOJI_WINNER} **WINNER:** {interaction.user.mention}\n{config.EMOJI_ANSWER} **ANSWER:** `{self.correct_answer}`\n{config.EMOJI_POINTS} **POINTS:** +{points_won}")
            embed.set_footer(text="Hell System • Dino Games")
            if interaction.channel: await interaction.channel.send(embed=embed)
            try:
                view = self.view_ref 
                for child in view.children: child.disabled = True
                await interaction.message.edit(view=view)
            except: pass
        else:
            try: await interaction.response.send_message(f"❌ **WRONG!** Try again.", ephemeral=True)
            except: pass

class DinoView(discord.ui.View):
    def __init__(self, correct_dino):
        super().__init__(timeout=None)
        self.correct_dino = correct_dino
        self.grabbed = False 
    @discord.ui.button(label="GUESS THE DINO", style=discord.ButtonStyle.primary, emoji="❓", custom_id="dino_guess_btn_v2")
    async def guess_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.grabbed:
            await interaction.response.send_message("❌ Round ended.", ephemeral=True)
            return
        modal = DinoModal(self.correct_dino)
        modal.view_ref = self 
        await interaction.response.send_modal(modal)

# --- GAMES ---
class ArkDropView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None); self.grabbed = False
    @discord.ui.button(label="CLAIM DROP", style=discord.ButtonStyle.danger, emoji="🎁", custom_id="drop_claim_btn")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.grabbed: return 
        self.grabbed = True
        try:
            uid = str(interaction.user.id)
            config.points_data[uid] = config.points_data.get(uid, 0) + 200
            button.label = f"Loot of {interaction.user.name}"
            button.style = discord.ButtonStyle.secondary
            button.disabled = True
            embed = interaction.message.embeds[0]
            embed.color = discord.Color.dark_grey()
            embed.set_footer(text=f"Claimed by: {interaction.user.display_name} (+200 Points)")
            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.followup.send(f"🔴 **{interaction.user.mention}** opened the Red Drop!", ephemeral=False)
            self.stop()
        except: pass

class ArkTameView(discord.ui.View):
    def __init__(self, correct_food, dino_name): super().__init__(timeout=None); self.correct_food = correct_food; self.dino_name = dino_name; self.grabbed = False
    async def feed(self, interaction: discord.Interaction, food: str):
        if self.grabbed: return
        self.grabbed = True
        try:
            if food == self.correct_food:
                uid = str(interaction.user.id)
                config.points_data[uid] = config.points_data.get(uid, 0) + 200
                await interaction.response.send_message(f"🦕 **TAMED!** {interaction.user.mention} gave {food} to the {self.dino_name} (+200 pts).", ephemeral=False)
            else: await interaction.response.send_message(f"❌ The {self.dino_name} rejects {food}. It fled!", ephemeral=False)
            for child in self.children: child.disabled = True
            await interaction.message.edit(view=self)
            self.stop()
        except: pass
    @discord.ui.button(label="Raw Meat 🥩", style=discord.ButtonStyle.danger)
    async def meat(self, interaction: discord.Interaction, button: discord.ui.Button): await self.feed(interaction, "Raw Meat")
    @discord.ui.button(label="Mejoberries 🫐", style=discord.ButtonStyle.primary)
    async def berries(self, interaction: discord.Interaction, button: discord.ui.Button): await self.feed(interaction, "Mejoberries")

class ArkCraftView(discord.ui.View):
    def __init__(self, correct_mat): super().__init__(timeout=None); self.correct_mat = correct_mat; self.grabbed = False
    async def check_mat(self, interaction: discord.Interaction, mat_clicked: str):
        if self.grabbed: return
        self.grabbed = True
        try:
            if mat_clicked == self.correct_mat:
                uid = str(interaction.user.id)
                config.points_data[uid] = config.points_data.get(uid, 0) + 200
                await interaction.response.send_message(f"🔨 **Correct!** {interaction.user.mention} crafted the item (+200 pts).", ephemeral=False)
            else: await interaction.response.send_message("❌ Wrong material. It broke.", ephemeral=False)
            for child in self.children: child.disabled = True
            await interaction.message.edit(view=self)
            self.stop()
        except: pass
    @discord.ui.button(label="Metal", style=discord.ButtonStyle.secondary)
    async def b1(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check_mat(interaction, "Metal")
    @discord.ui.button(label="Stone/Wood", style=discord.ButtonStyle.secondary)
    async def b2(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check_mat(interaction, "Stone/Wood")
    @discord.ui.button(label="Fiber/Hide", style=discord.ButtonStyle.secondary)
    async def b3(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check_mat(interaction, "Hide/Fiber")
    @discord.ui.button(label="Advanced", style=discord.ButtonStyle.success)
    async def b4(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check_mat(interaction, "Advanced")

class ArkImprintView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None); self.needs = random.choice(["Cuddle", "Walk", "Feed"]); self.grabbed = False
    async def check(self, interaction: discord.Interaction, action: str):
        if self.grabbed: return
        self.grabbed = True
        try:
            if action == self.needs:
                uid = str(interaction.user.id)
                config.points_data[uid] = config.points_data.get(uid, 0) + 200
                await interaction.response.send_message(f"❤️ **Imprinting increased!** (+200 pts).", ephemeral=False)
                for child in self.children: child.disabled = True
                await interaction.message.edit(view=self)
            else:
                await interaction.response.send_message(f"😭 Baby wanted **{self.needs}**.", ephemeral=False)
                embed = interaction.message.embeds[0]; embed.color = discord.Color.red(); embed.title = "Rearing FAILED"
                for child in self.children: child.disabled = True
                await interaction.message.edit(embed=embed, view=self)
            self.stop()
        except: pass
    @discord.ui.button(label="Cuddle 🧸", style=discord.ButtonStyle.primary)
    async def b1(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check(interaction, "Cuddle")
    @discord.ui.button(label="Walk 🚶", style=discord.ButtonStyle.success)
    async def b2(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check(interaction, "Walk")
    @discord.ui.button(label="Feed 🍖", style=discord.ButtonStyle.danger)
    async def b3(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check(interaction, "Feed")

class ArkAlphaView(discord.ui.View):
    def __init__(self, win, loss, chance): super().__init__(timeout=None); self.win = win; self.loss = loss; self.chance = chance; self.grabbed = False
    @discord.ui.button(label="🗡️ ATTACK ALPHA", style=discord.ButtonStyle.danger)
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.grabbed: return
        self.grabbed = True
        try:
            uid = str(interaction.user.id)
            if random.random() < self.chance: 
                config.points_data[uid] = config.points_data.get(uid, 0) + self.win
                await interaction.response.send_message(f"🏆 **VICTORY!** Killed Alpha (+{self.win} pts).", ephemeral=False)
            else: 
                cur = config.points_data.get(uid, 0); config.points_data[uid] = max(0, cur - self.loss)
                await interaction.response.send_message(f"💀 **DEATH...** You died and lost {self.loss} pts.", ephemeral=False)
            button.disabled = True
            await interaction.message.edit(view=self)
            self.stop()
        except: pass

class PokemonVisualView(discord.ui.View):
    def __init__(self, correct_type, poke_name): super().__init__(timeout=None); self.correct_type = correct_type; self.poke_name = poke_name; self.grabbed = False
    async def guess(self, interaction: discord.Interaction, type_guess: str):
        if self.grabbed: return
        self.grabbed = True
        try:
            if type_guess == self.correct_type:
                uid = str(interaction.user.id)
                config.points_data[uid] = config.points_data.get(uid, 0) + 200
                await interaction.response.send_message(f"✅ **Correct!** (+200 pts).", ephemeral=False)
            else: await interaction.response.send_message(f"❌ Incorrect. It was {self.correct_type}.", ephemeral=False)
            for child in self.children: child.disabled = True
            await interaction.message.edit(view=self)
            self.stop()
        except: pass
    @discord.ui.button(label="Fire 🔥", style=discord.ButtonStyle.danger)
    async def b1(self, interaction: discord.Interaction, button: discord.ui.Button): await self.guess(interaction, "Fire")
    @discord.ui.button(label="Water 💧", style=discord.ButtonStyle.primary)
    async def b2(self, interaction: discord.Interaction, button: discord.ui.Button): await self.guess(interaction, "Water")
    @discord.ui.button(label="Grass 🌿", style=discord.ButtonStyle.success)
    async def b3(self, interaction: discord.Interaction, button: discord.ui.Button): await self.guess(interaction, "Grass")

class Minigames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # VARIABLES LOCALES - ESTO SOLUCIONA EL ERROR DE RENDER
        self.last_dino_msg = None
        self.last_minigame_msg = None
        
        self.dino_game_loop.start()
        self.minigames_auto_loop.start()

    def cog_unload(self):
        self.dino_game_loop.cancel()
        self.minigames_auto_loop.cancel()

    @commands.command(name="recipes")
    async def show_recipes(self, ctx):
        embed = discord.Embed(title=f"{config.EMOJI_BLOOD} **HELL RECIPES** {config.EMOJI_BLOOD}", color=0x990000)
        embed.set_image(url="https://media.discordapp.net/attachments/1329487785857650748/1335660249704693760/recipes.png") 
        recipes = [("Sweet Veg. Cake", "50 Cementing Paste"), ("Kibble", "1 Fiber"), ("Colors", "1 Thatch"), ("Shadow Steak", "1 Raw Meat"), ("Mindwipe Tonic", "200 Mejoberries"), ("Medical Brew", "1 Tintoberry")]
        for name, ing in recipes: embed.add_field(name=f"**{name}**", value=f"{config.HELL_ARROW} {ing}", inline=True)
        embed.set_footer(text="Hell System • Crafting")
        await ctx.send(embed=embed)

    @tasks.loop(minutes=20)
    async def dino_game_loop(self):
        channel = self.bot.get_channel(config.DINO_CHANNEL_ID)
        if not channel: return
        
        # LÓGICA PARA DESHABILITAR EL ANTERIOR Y PONERLO GRIS
        if self.last_dino_msg:
            try:
                # Recuperar la vista vieja si es posible, o crear una dummy deshabilitada
                view = discord.ui.View()
                btn = discord.ui.Button(label="GAME ENDED", style=discord.ButtonStyle.secondary, disabled=True, emoji="🔒")
                view.add_item(btn)
                await self.last_dino_msg.edit(view=view)
            except: pass

        dino_real_name = random.choice(config.ARK_DINOS)
        scrambled_name = "".join(random.sample(list(dino_real_name.upper()), len(dino_real_name)))
        
        embed = discord.Embed(title=f"{config.EMOJI_DINO_TITLE} WHO IS THE DINO?", color=0xFFA500)
        embed.description = f"Unscramble the name!\n🧩 **SCRAMBLED:** `{scrambled_name}`\n\nClick the button to answer."
        embed.set_footer(text="Hell System • Dino Games")
        view = DinoView(correct_dino=dino_real_name)
        
        self.last_dino_msg = await channel.send(embed=embed, view=view)

    @tasks.loop(minutes=5)
    async def minigames_auto_loop(self):
        channel = self.bot.get_channel(config.MINIGAMES_CHANNEL_ID)
        if not channel: return
        
        if self.last_minigame_msg:
            try:
                # Poner el anterior en gris
                view = discord.ui.View()
                btn = discord.ui.Button(label="EXPIRED", style=discord.ButtonStyle.secondary, disabled=True)
                view.add_item(btn)
                await self.last_minigame_msg.edit(view=view)
            except: pass 
        
        self.last_minigame_msg = await self.spawn_game(channel)

    async def spawn_game(self, channel):
        game_type = random.randint(1, 6)
        # (Resto de la lógica de spawn igual, ya está corregida arriba)
        if game_type == 1:
            embed = discord.Embed(title="RED SUPPLY DROP INCOMING!", description="Contains high-level loot. Claim it fast!", color=discord.Color.red())
            embed.set_image(url=config.IMG_ARK_DROP)
            return await channel.send(embed=embed, view=ArkDropView())
        elif game_type == 2:
            data = random.choice(config.DATA_TAMING)
            embed = discord.Embed(title="Unconscious Dino!", description=f"What does this **{data['name']}** eat to be tamed?", color=discord.Color.green())
            embed.set_image(url=data["url"])
            return await channel.send(embed=embed, view=ArkTameView(data["food"], data["name"]))
        elif game_type == 3:
            data = random.choice(config.DATA_CRAFTING)
            embed = discord.Embed(title="Crafting Table", description=f"What is the main material for: **{data['name']}**?", color=discord.Color.orange())
            embed.set_image(url=data["url"])
            return await channel.send(embed=embed, view=ArkCraftView(data["mat"]))
        elif game_type == 4:
            embed = discord.Embed(title="Baby Rearing", description="The baby is crying. **Guess what care it needs.**", color=discord.Color.purple())
            embed.set_image(url=random.choice(config.DATA_BREEDING_IMGS))
            return await channel.send(embed=embed, view=ArkImprintView())
        elif game_type == 5:
            data = random.choice(config.DATA_ALPHAS)
            embed = discord.Embed(title=f"⚠️ {data['name'].upper()} DETECTED", description=f"Do you risk attacking it?\n\n🟢 **Reward:** +{data['win']} Points\n🔴 **Risk:** -{data['loss']} Points\n🎲 **Win Chance:** {int(data['chance']*100)}%", color=data['color'])
            embed.set_image(url=data["url"])
            return await channel.send(embed=embed, view=ArkAlphaView(data["win"], data["loss"], data["chance"]))
        elif game_type == 6:
            data = random.choice(config.DATA_POKEMON)
            embed = discord.Embed(title="What type is this Pokémon?", description=f"Guess the type of **{data['name']}**.", color=discord.Color.gold())
            embed.set_image(url=data["url"])
            return await channel.send(embed=embed, view=PokemonVisualView(data["type"], data["name"]))

    @dino_game_loop.before_loop
    async def before_dino(self): await self.bot.wait_until_ready()
    @minigames_auto_loop.before_loop
    async def before_minigames(self): await self.bot.wait_until_ready()

async def setup(bot): await bot.add_cog(Minigames(bot))
