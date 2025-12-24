import discord
from discord import app_commands
from discord.ext import commands, tasks
import random
import asyncio
import config  # Importamos la configuración global

# ==========================================
# 🦕 CLASES DINO GAME
# ==========================================

class DinoModal(discord.ui.Modal, title="🦖 WHO IS THAT DINO?"):
    answer_input = discord.ui.TextInput(label="Dino Name", placeholder="Enter name...", required=True)

    def __init__(self, correct_answer):
        super().__init__()
        self.correct_answer = correct_answer
        self.view_ref = None

    async def on_submit(self, interaction: discord.Interaction):
        guess = self.answer_input.value.strip().lower()
        
        # Verificar si alguien ya ganó (si el botón fue deshabilitado visualmente o por lógica)
        if self.view_ref and self.view_ref.grabbed:
             await interaction.response.send_message("❌ Someone was faster.", ephemeral=True)
             return

        if guess == self.correct_answer.lower():
            if self.view_ref: self.view_ref.grabbed = True 
            
            # Dar puntos
            points_won = 200 
            uid = str(interaction.user.id)
            config.points_data[uid] = config.points_data.get(uid, 0) + points_won
            
            try: await interaction.response.send_message(f"{config.EMOJI_CORRECT} **CORRECT!** You guessed it.", ephemeral=True)
            except: pass

            embed = discord.Embed(color=0x00FF00)
            embed.description = (
                f"{config.EMOJI_WINNER} **WINNER:** {interaction.user.mention}\n"
                f"{config.EMOJI_ANSWER} **ANSWER:** `{self.correct_answer}`\n"
                f"{config.EMOJI_POINTS} **POINTS:** +{points_won}"
            )
            embed.set_footer(text="Hell System • Dino Games")
            
            if interaction.channel: 
                await interaction.channel.send(embed=embed)
            
            # Deshabilitar botón original
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

# ==========================================
# 🎮 CLASES MINIJUEGOS RANDOM
# ==========================================

class ArkDropView(discord.ui.View):
    def __init__(self): 
        super().__init__(timeout=None)
        self.grabbed = False
    @discord.ui.button(label="CLAIM DROP", style=discord.ButtonStyle.danger, emoji="🎁", custom_id="drop_claim_btn")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.grabbed: return 
        self.grabbed = True
        try:
            # Dar puntos
            uid = str(interaction.user.id)
            config.points_data[uid] = config.points_data.get(uid, 0) + 200
            
            button.label = f"Loot of {interaction.user.name}"
            button.style = discord.ButtonStyle.secondary
            button.disabled = True
            
            embed = interaction.message.embeds[0]
            embed.color = discord.Color.dark_grey()
            embed.set_footer(text=f"Claimed by: {interaction.user.display_name} (+200 Points)")
            
            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.followup.send(f"🔴 **{interaction.user.mention}** opened the Red Drop and won 200 points!", ephemeral=False)
            self.stop()
        except Exception: pass

class ArkTameView(discord.ui.View):
    def __init__(self, correct_food, dino_name):
        super().__init__(timeout=None)
        self.correct_food = correct_food
        self.dino_name = dino_name
        self.grabbed = False
    
    async def feed(self, interaction: discord.Interaction, food: str):
        if self.grabbed: return
        self.grabbed = True
        try:
            if food == self.correct_food:
                uid = str(interaction.user.id)
                config.points_data[uid] = config.points_data.get(uid, 0) + 200
                await interaction.response.send_message(f"🦕 **TAMED!** {interaction.user.mention} gave {food} to the {self.dino_name} (+200 pts).", ephemeral=False)
            else:
                await interaction.response.send_message(f"❌ The {self.dino_name} rejects {food}. It fled!", ephemeral=False)
            
            for child in self.children: child.disabled = True
            await interaction.message.edit(view=self)
            self.stop()
        except Exception: pass

    @discord.ui.button(label="Raw Meat 🥩", style=discord.ButtonStyle.danger, custom_id="tm_meat")
    async def meat(self, interaction: discord.Interaction, button: discord.ui.Button): await self.feed(interaction, "Raw Meat")
    @discord.ui.button(label="Mejoberries 🫐", style=discord.ButtonStyle.primary, custom_id="tm_berry")
    async def berries(self, interaction: discord.Interaction, button: discord.ui.Button): await self.feed(interaction, "Mejoberries")

class ArkCraftView(discord.ui.View):
    def __init__(self, correct_mat):
        super().__init__(timeout=None)
        self.correct_mat = correct_mat
        self.grabbed = False
    
    async def check_mat(self, interaction: discord.Interaction, mat_clicked: str):
        if self.grabbed: return
        self.grabbed = True
        try:
            if mat_clicked == self.correct_mat:
                uid = str(interaction.user.id)
                config.points_data[uid] = config.points_data.get(uid, 0) + 200
                await interaction.response.send_message(f"🔨 **Correct!** {interaction.user.mention} crafted the item (+200 pts).", ephemeral=False)
            else:
                await interaction.response.send_message("❌ Wrong material. It broke.", ephemeral=False)
            
            for child in self.children: child.disabled = True
            await interaction.message.edit(view=self)
            self.stop()
        except Exception: pass

    @discord.ui.button(label="Metal / Ingots", style=discord.ButtonStyle.secondary, custom_id="cr_metal")
    async def b1(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check_mat(interaction, "Metal")
    @discord.ui.button(label="Stone / Wood / Flint", style=discord.ButtonStyle.secondary, custom_id="cr_stone")
    async def b2(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check_mat(interaction, "Stone/Wood")
    @discord.ui.button(label="Hide / Fiber / Thatch", style=discord.ButtonStyle.secondary, custom_id="cr_hide")
    async def b3(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check_mat(interaction, "Hide/Fiber")
    @discord.ui.button(label="Electronics / Polymer / Gunpowder", style=discord.ButtonStyle.success, custom_id="cr_adv")
    async def b4(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check_mat(interaction, "Advanced")

class ArkImprintView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.needs = random.choice(["Cuddle", "Walk", "Feed"])
        self.grabbed = False
    
    async def check(self, interaction: discord.Interaction, action: str):
        if self.grabbed: return
        self.grabbed = True
        try:
            if action == self.needs:
                uid = str(interaction.user.id)
                config.points_data[uid] = config.points_data.get(uid, 0) + 200
                await interaction.response.send_message(f"❤️ **Imprinting increased!** {interaction.user.mention} got it right (+200 pts).", ephemeral=False)
                for child in self.children: child.disabled = True
                await interaction.message.edit(view=self)
            else:
                await interaction.response.send_message(f"😭 The baby wanted **{self.needs}**. It got angry and left!", ephemeral=False)
                embed = interaction.message.embeds[0]
                embed.color = discord.Color.red()
                embed.title = "Rearing FAILED"
                for child in self.children: child.disabled = True
                await interaction.message.edit(embed=embed, view=self)
            self.stop()
        except Exception: pass

    @discord.ui.button(label="Cuddle 🧸", style=discord.ButtonStyle.primary, custom_id="imp_cud")
    async def b1(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check(interaction, "Cuddle")
    @discord.ui.button(label="Walk 🚶", style=discord.ButtonStyle.success, custom_id="imp_wlk")
    async def b2(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check(interaction, "Walk")
    @discord.ui.button(label="Feed 🍖", style=discord.ButtonStyle.danger, custom_id="imp_fed")
    async def b3(self, interaction: discord.Interaction, button: discord.ui.Button): await self.check(interaction, "Feed")

class ArkAlphaView(discord.ui.View):
    def __init__(self, win, loss, chance): 
        super().__init__(timeout=None)
        self.win = win
        self.loss = loss
        self.chance = chance
        self.grabbed = False
    @discord.ui.button(label="🗡️ ATTACK ALPHA", style=discord.ButtonStyle.danger, custom_id="alpha_atk")
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.grabbed: return
        self.grabbed = True
        try:
            uid = str(interaction.user.id)
            if random.random() < self.chance: 
                config.points_data[uid] = config.points_data.get(uid, 0) + self.win
                await interaction.response.send_message(f"🏆 **VICTORY!** {interaction.user.mention} killed the Alpha (+{self.win} pts).", ephemeral=False)
            else: 
                current = config.points_data.get(uid, 0)
                config.points_data[uid] = max(0, current - self.loss)
                await interaction.response.send_message(f"💀 **DEATH...** {interaction.user.mention} died and lost **{self.loss} points**.", ephemeral=False)
            
            button.disabled = True
            await interaction.message.edit(view=self)
            self.stop()
        except Exception: pass

class PokemonVisualView(discord.ui.View):
    def __init__(self, correct_type, poke_name):
        super().__init__(timeout=None)
        self.correct_type = correct_type
        self.poke_name = poke_name
        self.grabbed = False
    
    async def guess(self, interaction: discord.Interaction, type_guess: str):
        if self.grabbed: return
        self.grabbed = True
        try:
            if type_guess == self.correct_type:
                uid = str(interaction.user.id)
                config.points_data[uid] = config.points_data.get(uid, 0) + 200
                await interaction.response.send_message(f"✅ **Correct!** {interaction.user.mention} got it right (+200 pts).", ephemeral=False)
            else:
                await interaction.response.send_message(f"❌ Incorrect. It was {self.correct_type}.", ephemeral=False)
            
            for child in self.children: child.disabled = True
            await interaction.message.edit(view=self)
            self.stop()
        except Exception: pass

    @discord.ui.button(label="Fire 🔥", style=discord.ButtonStyle.danger, custom_id="pk_fir")
    async def b1(self, interaction: discord.Interaction, button: discord.ui.Button): await self.guess(interaction, "Fire")
    @discord.ui.button(label="Water 💧", style=discord.ButtonStyle.primary, custom_id="pk_wat")
    async def b2(self, interaction: discord.Interaction, button: discord.ui.Button): await self.guess(interaction, "Water")
    @discord.ui.button(label="Grass 🌿", style=discord.ButtonStyle.success, custom_id="pk_gra")
    async def b3(self, interaction: discord.Interaction, button: discord.ui.Button): await self.guess(interaction, "Grass")

# ==========================================
# ⚙️ CLASE PRINCIPAL (COG)
# ==========================================

class Minigames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Iniciamos loops
        self.dino_game_loop.start()
        self.minigames_auto_loop.start()

    def cog_unload(self):
        self.dino_game_loop.cancel()
        self.minigames_auto_loop.cancel()

    # --- COMANDOS ---
    @commands.command(name="recipes")
    async def show_recipes(self, ctx):
        embed = discord.Embed(title=f"{config.EMOJI_BLOOD} **HELL RECIPES** {config.EMOJI_BLOOD}", color=0x990000)
        embed.description = "Custom crafting recipes for this season."
        embed.set_image(url="https://media.discordapp.net/attachments/1329487785857650748/1335660249704693760/recipes.png") 
        
        recipes = [
            ("🍰 Sweet Veg. Cake", "50 Cementing Paste"),
            ("🥚 Kibble", "1 Fiber"),
            ("🎨 Colors", "1 Thatch"),
            ("🥩 Shadow Steak", "1 Raw Meat"),
            ("🧠 Mindwipe Tonic", "200 Mejoberries"),
            ("💉 Medical Brew", "1 Tintoberry"),
            ("⚔️ Battle Tartare", "10 Crystal"),
            ("🍺 Beer Jar", "5 Thatch"),
            ("🌵 Cactus Broth", "50 Stone"),
            ("🍄 Mushroom Brew", "5 Aquatic Mushroom"),
            ("🌶️ Focal Chili", "100 Raw Metal"),
            ("🦗 Bug Repellent", "1 Chitin/Keratin")
        ]

        for name, ingredients in recipes:
            embed.add_field(name=f"**{name}**", value=f"{config.HELL_ARROW} {ingredients}", inline=True)

        embed.set_footer(text="Hell System • Crafting")
        await ctx.send(embed=embed)

    # --- LOOPS ---
    
    @tasks.loop(minutes=20)
    async def dino_game_loop(self):
        try:
            channel = self.bot.get_channel(config.DINO_CHANNEL_ID)
            if not channel: return
            
            if config.last_dino_message:
                try: await config.last_dino_message.edit(view=None)
                except: pass

            dino_real_name = random.choice(config.ARK_DINOS)
            char_list = list(dino_real_name.upper())
            random.shuffle(char_list)
            scrambled_name = "".join(char_list)
            while scrambled_name == dino_real_name.upper():
                random.shuffle(char_list)
                scrambled_name = "".join(char_list)

            embed = discord.Embed(title=f"{config.EMOJI_DINO_TITLE} WHO IS THE DINO?", color=0xFFA500)
            embed.description = (
                f"Unscramble the name of this creature!\n\n"
                f"🧩 **SCRAMBLED:** `{scrambled_name}`\n\n"
                f"Click the button to answer."
            )
            embed.set_footer(text="Hell System • Dino Games")
            view = DinoView(correct_dino=dino_real_name)
            config.last_dino_message = await channel.send(embed=embed, view=view)
        except Exception as e:
            print(f"[MINIGAMES] Error in Dino Loop: {e}")

    @dino_game_loop.before_loop
    async def before_dino(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=5)
    async def minigames_auto_loop(self):
        try:
            channel = self.bot.get_channel(config.MINIGAMES_CHANNEL_ID)
            if not channel: return
            
            if config.last_minigame_message:
                try: await config.last_minigame_message.edit(view=None)
                except: pass 
            
            config.last_minigame_message = await self.spawn_game(channel)
        except Exception as e:
            print(f"[MINIGAMES] Error Minigame Loop: {e}")

    @minigames_auto_loop.before_loop
    async def before_minigames(self):
        await self.bot.wait_until_ready()

    async def spawn_game(self, channel):
        game_type = random.randint(1, 6)
        view = None
        msg = None
        
        if game_type == 1:
            embed = discord.Embed(title="RED SUPPLY DROP INCOMING!", description="Contains high-level loot. Claim it fast!", color=discord.Color.red())
            embed.set_image(url=config.IMG_ARK_DROP)
            view = ArkDropView()
            msg = await channel.send(embed=embed, view=view)
        
        elif game_type == 2:
            data = random.choice(config.DATA_TAMING)
            embed = discord.Embed(title="Unconscious Dino!", description=f"What does this **{data['name']}** eat to be tamed?", color=discord.Color.green())
            embed.set_image(url=data["url"])
            view = ArkTameView(data["food"], data["name"])
            msg = await channel.send(embed=embed, view=view)
        
        elif game_type == 3:
            data = random.choice(config.DATA_CRAFTING)
            embed = discord.Embed(title="Crafting Table", description=f"What is the main material for: **{data['name']}**?", color=discord.Color.orange())
            embed.set_image(url=data["url"])
            view = ArkCraftView(data["mat"])
            msg = await channel.send(embed=embed, view=view)
        
        elif game_type == 4:
            img = random.choice(config.DATA_BREEDING_IMGS)
            embed = discord.Embed(title="Baby Rearing", description="The baby is crying. **Guess what care it needs.**", color=discord.Color.purple())
            embed.set_image(url=img)
            view = ArkImprintView()
            msg = await channel.send(embed=embed, view=view)
        
        elif game_type == 5:
            data = random.choice(config.DATA_ALPHAS)
            embed = discord.Embed(title=f"⚠️ {data['name'].upper()} DETECTED", description=f"Do you risk attacking it?\n\n🟢 **Reward:** +{data['win']} Points\n🔴 **Risk:** -{data['loss']} Points\n🎲 **Win Chance:** {int(data['chance']*100)}%", color=data['color'])
            embed.set_image(url=data["url"])
            view = ArkAlphaView(data["win"], data["loss"], data["chance"])
            msg = await channel.send(embed=embed, view=view)
        
        elif game_type == 6:
            data = random.choice(config.DATA_POKEMON)
            embed = discord.Embed(title="What type is this Pokémon?", description=f"Guess the type of **{data['name']}**.", color=discord.Color.gold())
            embed.set_image(url=data["url"])
            view = PokemonVisualView(data["type"], data["name"])
            msg = await channel.send(embed=embed, view=view)
            
        return msg

async def setup(bot):
    await bot.add_cog(Minigames(bot))
