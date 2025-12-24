import discord
from discord import app_commands
from discord.ext import commands, tasks
import datetime
import re
import random
import config 

class EmbedBuilderModal(discord.ui.Modal):
    def __init__(self, mode="create", existing_data=None, embed_name=None):
        super().__init__(title=f"{mode.capitalize()} Embed")
        self.mode = mode
        self.existing_data = existing_data
        self.embed_name_ref = embed_name

        self.e_name = discord.ui.TextInput(label="ID Name (No spaces)", placeholder="e.g., rules_v1", required=True, default=embed_name if embed_name else "")
        self.e_title = discord.ui.TextInput(label="Title", required=False, default=existing_data.get("title", "") if existing_data else "")
        self.e_desc = discord.ui.TextInput(label="Description", style=discord.TextStyle.paragraph, required=True, default=existing_data.get("description", "") if existing_data else "")
        self.e_color = discord.ui.TextInput(label="Color", placeholder="Red, Blue, Purple, Gold...", required=False, default=existing_data.get("color_str", "") if existing_data else "")
        self.e_image = discord.ui.TextInput(label="Image URL", required=False, default=existing_data.get("image", "") if existing_data else "")

        self.add_item(self.e_name)
        self.add_item(self.e_title)
        self.add_item(self.e_desc)
        self.add_item(self.e_color)
        self.add_item(self.e_image)

    async def on_submit(self, interaction: discord.Interaction):
        c_val = 0x2b2d31 
        c_str = self.e_color.value.strip().lower()
        
        colors = {
            "red": 0x990000, "blue": 0x0000FF, "green": 0x00FF00, "gold": 0xFFD700,
            "orange": 0xFFA500, "purple": 0x800080, "yellow": 0xFFFF00, "white": 0xFFFFFF,
            "black": 0x000000, "pink": 0xFFC0CB, "cyan": 0x00FFFF, "dark": 0x2b2d31
        }
        
        if c_str.startswith("#"): 
            try: c_val = int(c_str[1:], 16)
            except: pass
        elif c_str in colors:
            c_val = colors[c_str]

        temp_data = {
            "title": self.e_title.value,
            "description": self.e_desc.value,
            "color": c_val,
            "color_str": self.e_color.value,
            "image": self.e_image.value,
            "footer": "Hell System • Embeds"
        }
        
        embed = discord.Embed(title=temp_data["title"], description=temp_data["description"], color=c_val)
        if temp_data["image"]: embed.set_image(url=temp_data["image"])
        embed.set_footer(text=temp_data["footer"])

        view = EmbedPreviewView(self.e_name.value, temp_data)
        await interaction.response.send_message(f"👁️ **PREVIEW** (ID: `{self.e_name.value}`)", embed=embed, view=view, ephemeral=True)

class EmbedPreviewView(discord.ui.View):
    def __init__(self, name, data):
        super().__init__(timeout=None)
        self.name = name
        self.data = data

    @discord.ui.button(label="SAVE", style=discord.ButtonStyle.success, emoji="💾")
    async def save(self, interaction: discord.Interaction, button: discord.ui.Button):
        config.embeds_data[self.name] = self.data
        await interaction.response.edit_message(content=f"✅ Saved `{self.name}`.", view=None, embed=None)

    @discord.ui.button(label="EDIT", style=discord.ButtonStyle.secondary, emoji="✏️")
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmbedBuilderModal(mode="edit", existing_data=self.data, embed_name=self.name))

class AutoSendModal(discord.ui.Modal, title="⏰ Configure AutoSend"):
    def __init__(self, embed_name):
        super().__init__()
        self.embed_name = embed_name
        self.time_input = discord.ui.TextInput(label="Time (HH:MM) 24h", placeholder="14:30", required=True)
        self.channel_id = discord.ui.TextInput(label="Channel ID", required=True)
        self.add_item(self.time_input)
        self.add_item(self.channel_id)

    async def on_submit(self, interaction: discord.Interaction):
        t = self.time_input.value.strip()
        cid = self.channel_id.value.strip()
        if not re.match(r"^\d{2}:\d{2}$", t):
            return await interaction.response.send_message("❌ Invalid time format (HH:MM)", ephemeral=True)
        
        uid = f"{self.embed_name}_{t}" 
        config.autosend_data[uid] = {"embed": self.embed_name, "time": t, "channel": cid}
        await interaction.response.send_message(f"✅ AutoSend: `{self.embed_name}` at `{t}` in `{cid}`.", ephemeral=True)

class MenuOptionModal(discord.ui.Modal, title="Add Option to Menu"):
    def __init__(self, view_ref, target_embed):
        super().__init__()
        self.view_ref = view_ref
        self.target_embed = target_embed
        self.label = discord.ui.TextInput(label="Button Label", placeholder="e.g. Rules", required=True)
        self.add_item(self.label)

    async def on_submit(self, interaction: discord.Interaction):
        self.view_ref.options_list.append({"label": self.label.value, "embed": self.target_embed})
        await interaction.response.edit_message(content=f"📝 **Building Menu:** `{self.view_ref.main_embed}`\nAdded: **{self.label.value}** -> `{self.target_embed}`", view=self.view_ref)

class MenuBuilderView(discord.ui.View):
    def __init__(self, main_embed):
        super().__init__(timeout=None)
        self.main_embed = main_embed
        self.options_list = []
        
        options = []
        for name in list(config.embeds_data.keys())[:25]:
            options.append(discord.SelectOption(label=name, value=name))
        
        self.select = discord.ui.Select(placeholder="Select Embed to Link...", options=options)
        self.select.callback = self.add_option_callback
        self.add_item(self.select)

    async def add_option_callback(self, interaction: discord.Interaction):
        target = self.select.values[0]
        await interaction.response.send_modal(MenuOptionModal(self, target))

    @discord.ui.button(label="FINISH & SEND", style=discord.ButtonStyle.success, row=1)
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.options_list: return await interaction.response.send_message("❌ No options added.", ephemeral=True)
        
        await interaction.response.send_message("⬇️ Type Channel ID to send (Ephemeral):", ephemeral=True)
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        try:
            msg = await interaction.client.wait_for('message', check=check, timeout=30)
            cid = int(msg.content.strip("<#>"))
            channel = interaction.client.get_channel(cid)
            if channel:
                d = config.embeds_data[self.main_embed]
                embed = discord.Embed(title=d["title"], description=d["description"], color=d["color"])
                if d["image"]: embed.set_image(url=d["image"])
                
                menu_data = {"main_embed": self.main_embed, "options": self.options_list}
                view = PersistentMenuView(menu_data)
                sent = await channel.send(embed=embed, view=view)
                
                config.menus_data[str(sent.id)] = menu_data
                interaction.client.add_view(view, message_id=sent.id)
                await interaction.followup.send("✅ Menu Sent!", ephemeral=True)
            try: await msg.delete()
            except: pass
        except: await interaction.followup.send("❌ Cancelled/Invalid ID", ephemeral=True)

class EmbedSelectorView(discord.ui.View):
    def __init__(self, action, bot_ref=None):
        super().__init__(timeout=None)
        self.action = action
        self.bot_ref = bot_ref
        
        options = []
        
        if action == "disable_auto":
            for uid in list(config.autosend_data.keys())[:25]:
                options.append(discord.SelectOption(label=uid, value=uid))
            if not options: options.append(discord.SelectOption(label="No tasks", value="none"))
        else:
            for name in list(config.embeds_data.keys())[:25]: 
                options.append(discord.SelectOption(label=name, value=name))

        self.select = discord.ui.Select(placeholder="Select...", options=options, disabled=(not options or options[0].value=="none"))
        self.select.callback = self.callback
        self.add_item(self.select)

    async def callback(self, interaction: discord.Interaction):
        val = self.select.values[0]
        if val == "none": return

        if self.action == "edit":
            await interaction.response.send_modal(EmbedBuilderModal(mode="edit", existing_data=config.embeds_data[val], embed_name=val))
        
        elif self.action == "delete":
            del config.embeds_data[val]
            await interaction.response.edit_message(content=f"🗑️ Deleted `{val}`.", view=None)

        elif self.action == "send":
            await interaction.response.edit_message(content=f"Target: `{val}`. ⬇️ **Type Channel ID:**", view=None)
            def check(m): return m.author == interaction.user and m.channel == interaction.channel
            try:
                msg = await self.bot_ref.wait_for('message', check=check, timeout=30)
                cid = int(msg.content.strip("<#>"))
                ch = self.bot_ref.get_channel(cid)
                if ch:
                    d = config.embeds_data[val]
                    embed = discord.Embed(title=d["title"], description=d["description"], color=d["color"])
                    if d["image"]: embed.set_image(url=d["image"])
                    embed.set_footer(text=d["footer"])
                    await ch.send(embed=embed)
                    await interaction.followup.send("✅ Sent.", ephemeral=True)
                try: await msg.delete() 
                except: pass
            except: pass

        elif self.action == "auto":
            await interaction.response.send_modal(AutoSendModal(val))

        elif self.action == "disable_auto":
            del config.autosend_data[val]
            await interaction.response.edit_message(content=f"✅ Task `{val}` removed.", view=None)

        elif self.action == "menu_wizard":
            await interaction.response.edit_message(content=f"✅ Main Embed: `{val}`\nAdd options below:", view=MenuBuilderView(val))

class EmbedManagerView(discord.ui.View):
    def __init__(self, bot_ref):
        super().__init__(timeout=None)
        self.bot_ref = bot_ref

    @discord.ui.select(placeholder="Select Action...", options=[
        discord.SelectOption(label="Create Embed", value="create", emoji="✨"),
        discord.SelectOption(label="Edit Embed", value="edit", emoji="✏️"),
        discord.SelectOption(label="Send Embed", value="send", emoji="📤"),
        discord.SelectOption(label="Create Menu", value="menu", emoji="🔗"),
        discord.SelectOption(label="Delete Embed", value="delete", emoji="🗑️"),
        discord.SelectOption(label="Embed Autosend", value="auto", emoji="⏰"),
        discord.SelectOption(label="Disable Autosend", value="no_auto", emoji="🔕"),
        discord.SelectOption(label="List Embeds", value="list", emoji="📜")
    ])
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        action = select.values[0]

        if action == "create": await interaction.response.send_modal(EmbedBuilderModal())
        elif action == "list":
            txt = "\n".join([f"`{k}`" for k in config.embeds_data.keys()]) or "None"
            await interaction.response.send_message(f"**📚 Embeds:**\n{txt}", ephemeral=True)
        else:
            act_map = {
                "edit": "edit", "send": "send", "delete": "delete", 
                "auto": "auto", "menu": "menu_wizard", "no_auto": "disable_auto"
            }
            if not config.embeds_data and action != "no_auto":
                return await interaction.response.send_message("❌ No embeds found.", ephemeral=True)
            
            await interaction.response.send_message("Select Target:", view=EmbedSelectorView(act_map[action], self.bot_ref), ephemeral=True)

class PersistentMenuView(discord.ui.View):
    def __init__(self, menu_config):
        super().__init__(timeout=None)
        self.menu_config = menu_config
        options = [discord.SelectOption(label=o["label"], value=o["embed"]) for o in menu_config["options"]]
        select = discord.ui.Select(placeholder="Select Option...", options=options, custom_id=f"menu_{random.randint(1,99999)}")
        select.callback = self.callback
        self.add_item(select)

    async def callback(self, interaction: discord.Interaction):
        target = interaction.data["values"][0]
        if target in config.embeds_data:
            d = config.embeds_data[target]
            embed = discord.Embed(title=d["title"], description=d["description"], color=d["color"])
            if d["image"]: embed.set_image(url=d["image"])
            embed.set_footer(text=d["footer"])
            await interaction.response.edit_message(embed=embed)
        else: await interaction.response.send_message("❌ Embed not found.", ephemeral=True)

class Embeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.autosend_loop.start()

    def cog_unload(self): self.autosend_loop.cancel()

    @app_commands.command(name="embed_setup", description="Manage Embeds & Menus")
    async def embed_setup(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator: return
        embed = discord.Embed(title="🛠️ **EMBED MANAGER**", description="Select an option below.", color=0x2b2d31)
        await interaction.channel.send(embed=embed, view=EmbedManagerView(self.bot))
        await interaction.response.send_message("✅ Panel Sent.", ephemeral=True)

    @tasks.loop(minutes=1)
    async def autosend_loop(self):
        now = datetime.datetime.now().strftime("%H:%M")
        # Copia de seguridad de la lista para iterar sin errores
        for uid, data in list(config.autosend_data.items()):
            if data["time"] == now:
                try:
                    channel = self.bot.get_channel(int(data["channel"]))
                    if channel and data["embed"] in config.embeds_data:
                        d = config.embeds_data[data["embed"]]
                        embed = discord.Embed(title=d["title"], description=d["description"], color=d["color"])
                        if d["image"]: embed.set_image(url=d["image"])
                        embed.set_footer(text=d["footer"])
                        await channel.send(embed=embed)
                        print(f"[AUTOSEND] Sent {data['embed']} to {data['channel']}")
                except Exception as e:
                    print(f"[AUTOSEND ERROR] {e}")

    @autosend_loop.before_loop
    async def before_autosend(self): await self.bot.wait_until_ready()

async def setup(bot): await bot.add_cog(Embeds(bot))
