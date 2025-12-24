import discord
from discord import app_commands
from discord.ext import commands, tasks
import datetime
import re
import random
import config # Importamos configuración y bases de datos

# ==========================================
# 🛠️ CLASES DE UTILIDAD (MODALES Y VISTAS)
# ==========================================

# --- 1. MODAL DE CREACIÓN/EDICIÓN ---
class EmbedBuilderModal(discord.ui.Modal):
    def __init__(self, mode="create", existing_data=None, embed_name=None):
        super().__init__(title=f"{mode.capitalize()} Embed")
        self.mode = mode
        self.existing_data = existing_data
        self.embed_name_ref = embed_name

        # Campos del formulario
        self.e_name = discord.ui.TextInput(
            label="ID Name (Único, sin espacios)", 
            placeholder="ej: bienvenida_reglas", 
            required=True, 
            default=embed_name if embed_name else ""
        )
        self.e_title = discord.ui.TextInput(
            label="Título", 
            required=False, 
            default=existing_data.get("title", "") if existing_data else ""
        )
        self.e_desc = discord.ui.TextInput(
            label="Descripción", 
            style=discord.TextStyle.paragraph, 
            required=True, 
            default=existing_data.get("description", "") if existing_data else ""
        )
        self.e_color = discord.ui.TextInput(
            label="Color (Hex o Nombre)", 
            placeholder="#FF0000 o Red", 
            required=False, 
            default=existing_data.get("color_str", "") if existing_data else ""
        )
        self.e_image = discord.ui.TextInput(
            label="URL de Imagen (Opcional)", 
            required=False, 
            default=existing_data.get("image", "") if existing_data else ""
        )

        self.add_item(self.e_name)
        self.add_item(self.e_title)
        self.add_item(self.e_desc)
        self.add_item(self.e_color)
        self.add_item(self.e_image)

    async def on_submit(self, interaction: discord.Interaction):
        # Procesar color
        c_val = 0x2b2d31 # Default gris oscuro
        c_str = self.e_color.value.strip()
        
        if c_str.startswith("#"): 
            try: c_val = int(c_str[1:], 16)
            except: pass
        elif c_str.lower() == "red": c_val = 0x990000
        elif c_str.lower() == "green": c_val = 0x00FF00
        elif c_str.lower() == "blue": c_val = 0x0000FF
        elif c_str.lower() == "gold": c_val = 0xFFD700
        elif c_str.lower() == "orange": c_val = 0xFFA500

        # Crear objeto de datos temporal
        temp_data = {
            "title": self.e_title.value,
            "description": self.e_desc.value,
            "color": c_val,
            "color_str": c_str,
            "image": self.e_image.value,
            "footer": "Hell System • Embeds"
        }
        
        # Generar Embed de prueba
        embed = discord.Embed(title=temp_data["title"], description=temp_data["description"], color=c_val)
        if temp_data["image"]: embed.set_image(url=temp_data["image"])
        embed.set_footer(text=temp_data["footer"])

        # Enviar vista de confirmación
        view = EmbedPreviewView(self.e_name.value, temp_data)
        await interaction.response.send_message(
            f"👁️ **VISTA PREVIA** (ID: `{self.e_name.value}`)\n¿Te gusta? Dale a **SAVE** para guardar.", 
            embed=embed, 
            view=view, 
            ephemeral=True
        )

# --- 2. VISTA DE PREVIEW (SAVE / EDIT) ---
class EmbedPreviewView(discord.ui.View):
    def __init__(self, name, data):
        super().__init__(timeout=None)
        self.name = name
        self.data = data

    @discord.ui.button(label="SAVE", style=discord.ButtonStyle.success, emoji="💾")
    async def save(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Guardamos en la memoria global (config)
        config.embeds_data[self.name] = self.data
        # Feedback
        await interaction.response.edit_message(content=f"✅ Embed **{self.name}** guardado correctamente en la base de datos.", view=None, embed=None)

    @discord.ui.button(label="EDIT", style=discord.ButtonStyle.secondary, emoji="✏️")
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Reabrir el modal con los datos
        await interaction.response.send_modal(EmbedBuilderModal(mode="edit", existing_data=self.data, embed_name=self.name))

# --- 3. MODAL PARA AUTOSEND (Configurar hora) ---
class AutoSendModal(discord.ui.Modal, title="⏰ Configurar Auto-Envío"):
    def __init__(self, embed_name):
        super().__init__()
        self.embed_name = embed_name
        self.time_input = discord.ui.TextInput(label="Hora (HH:MM) Formato 24h", placeholder="14:30", required=True)
        self.channel_id = discord.ui.TextInput(label="ID del Canal", placeholder="123456789...", required=True)
        self.add_item(self.time_input)
        self.add_item(self.channel_id)

    async def on_submit(self, interaction: discord.Interaction):
        t = self.time_input.value.strip()
        cid = self.channel_id.value.strip()
        
        # Validar formato hora simple con Regex
        if not re.match(r"^\d{2}:\d{2}$", t):
            return await interaction.response.send_message("❌ Formato de hora incorrecto. Usa HH:MM (ej: 18:00)", ephemeral=True)
        
        # Guardar en base de datos
        uid = f"{self.embed_name}_{t}" # ID único
        config.autosend_data[uid] = {"embed": self.embed_name, "time": t, "channel": cid}
        
        await interaction.response.send_message(f"✅ **AutoSend Configurado:**\nEl embed `{self.embed_name}` se enviará todos los días a las `{t}` en el canal `{cid}`.", ephemeral=True)

# --- 4. VISTA DE SELECTOR DE EMBEDS (El corazón del sistema) ---
class EmbedSelectorView(discord.ui.View):
    def __init__(self, action, bot_ref=None):
        super().__init__(timeout=None)
        self.action = action
        self.bot_ref = bot_ref # Necesitamos el bot para esperar mensajes en el chat
        
        options = []
        # Listamos los embeds guardados (máximo 25 por límite de Discord)
        keys = list(config.embeds_data.keys())
        if not keys:
            options.append(discord.SelectOption(label="No hay embeds", value="none"))
        else:
            for name in keys[:25]: 
                options.append(discord.SelectOption(label=name, value=name))
        
        self.select = discord.ui.Select(placeholder="Selecciona un embed...", options=options, disabled=(not keys))
        self.select.callback = self.callback
        self.add_item(self.select)

    async def callback(self, interaction: discord.Interaction):
        embed_name = self.select.values[0]
        if embed_name == "none": return

        # === ACCIÓN: EDITAR ===
        if self.action == "edit":
            data = config.embeds_data[embed_name]
            await interaction.response.send_modal(EmbedBuilderModal(mode="edit", existing_data=data, embed_name=embed_name))
        
        # === ACCIÓN: BORRAR ===
        elif self.action == "delete":
            del config.embeds_data[embed_name]
            await interaction.response.edit_message(content=f"🗑️ Embed `{embed_name}` eliminado permanentemente.", view=None)

        # === ACCIÓN: ENVIAR ===
        elif self.action == "send":
            await interaction.response.edit_message(content=f"Has elegido: `{embed_name}`.\n⬇️ **Ahora escribe en el chat la ID del canal o menciónalo (#general).**", view=None)
            
            def check(m): return m.author == interaction.user and m.channel == interaction.channel
            try:
                msg = await self.bot_ref.wait_for('message', check=check, timeout=30)
                try:
                    # Intentar sacar ID de mención o texto
                    cid = int(msg.content.strip("<#>"))
                    channel = self.bot_ref.get_channel(cid)
                    if channel:
                        d = config.embeds_data[embed_name]
                        embed = discord.Embed(title=d["title"], description=d["description"], color=d["color"])
                        if d["image"]: embed.set_image(url=d["image"])
                        embed.set_footer(text=d["footer"])
                        
                        await channel.send(embed=embed)
                        await interaction.followup.send(f"✅ Enviado a {channel.mention}")
                    else:
                        await interaction.followup.send("❌ No encuentro ese canal.")
                except: 
                    await interaction.followup.send("❌ ID inválida.")
                try: await msg.delete() 
                except: pass
            except asyncio.TimeoutError:
                await interaction.followup.send("⏰ Tiempo agotado.")

        # === ACCIÓN: AUTOSEND ===
        elif self.action == "auto":
            await interaction.response.send_modal(AutoSendModal(embed_name))

        # === ACCIÓN: CREAR MENÚ VINCULADO ===
        elif self.action == "menu_step1":
            await interaction.response.edit_message(content=f"✅ **Embed Principal:** `{embed_name}`.\n\nAhora vamos a añadir las opciones del menú.\nEscribe en el chat con este formato:\n`Nombre Opción : ID_Del_Embed_Destino`\n\nEjemplo: `Ver Normas : normas_embed`\n\nEscribe **FIN** para terminar y crear el menú.", view=None)
            
            options_list = []
            def check(m): return m.author == interaction.user and m.channel == interaction.channel
            
            while True:
                try:
                    msg = await self.bot_ref.wait_for('message', check=check, timeout=120)
                    content = msg.content.strip()
                    
                    if content.upper() == "FIN":
                        try: await msg.delete()
                        except: pass
                        break
                    
                    if ":" in content:
                        label, target = content.split(":", 1)
                        label = label.strip()
                        target = target.strip()
                        
                        if target in config.embeds_data:
                            options_list.append({"label": label, "embed": target})
                            await interaction.followup.send(f"➕ Opción añadida: **{label}** -> Abre `{target}`", ephemeral=True)
                        else:
                            await interaction.followup.send(f"⚠️ El embed `{target}` no existe. Crea uno primero.", ephemeral=True)
                    else:
                        await interaction.followup.send("❌ Formato incorrecto. Usa `Nombre : ID_Embed`", ephemeral=True)
                    
                    try: await msg.delete()
                    except: pass
                except asyncio.TimeoutError:
                    break
            
            if options_list:
                # Generar el mensaje final
                d = config.embeds_data[embed_name]
                embed = discord.Embed(title=d["title"], description=d["description"], color=d["color"])
                if d["image"]: embed.set_image(url=d["image"])
                
                menu_data = {"main_embed": embed_name, "options": options_list}
                
                # Crear vista persistente
                view = PersistentMenuView(menu_data)
                sent_msg = await interaction.channel.send(embed=embed, view=view)
                
                # Guardar en base de datos de menús
                config.menus_data[str(sent_msg.id)] = menu_data
                # Registrar vista en el bot para que funcione si reinicias
                self.bot_ref.add_view(view, message_id=sent_msg.id)
                
                await interaction.followup.send("✅ **Menú Interactivo Creado.**", ephemeral=True)
            else:
                await interaction.followup.send("❌ No añadiste opciones. Cancelado.", ephemeral=True)

# --- 5. MENÚ PRINCIPAL (El que sale con /embed_setup) ---
class EmbedManagerView(discord.ui.View):
    def __init__(self, bot_ref):
        super().__init__(timeout=None)
        self.bot_ref = bot_ref

    @discord.ui.select(placeholder="¿Qué quieres hacer?", options=[
        discord.SelectOption(label="Create Embed", value="create", emoji="✨", description="Crear un nuevo mensaje desde cero."),
        discord.SelectOption(label="Edit Embed", value="edit", emoji="✏️", description="Editar uno existente."),
        discord.SelectOption(label="Send Embed", value="send", emoji="📤", description="Enviar un embed a un canal."),
        discord.SelectOption(label="Created Menu", value="menu", emoji="🔗", description="Vincular embeds en un menú."),
        discord.SelectOption(label="Delete Embed", value="delete", emoji="🗑️", description="Borrar un diseño."),
        discord.SelectOption(label="Embed Autosend", value="auto", emoji="⏰", description="Programar envío diario."),
        discord.SelectOption(label="Disable Autosend", value="no_auto", emoji="🔕", description="Cancelar envíos automáticos."),
        discord.SelectOption(label="See All Embeds", value="list", emoji="📜", description="Ver lista de IDs.")
    ])
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        action = select.values[0]

        if action == "create":
            await interaction.response.send_modal(EmbedBuilderModal())
        
        elif action == "list":
            if not config.embeds_data: return await interaction.response.send_message("❌ Lista vacía.", ephemeral=True)
            txt = "\n".join([f"• `{k}`" for k in config.embeds_data.keys()])
            await interaction.response.send_message(f"**📚 Embeds Guardados:**\n{txt}", ephemeral=True)

        elif action == "no_auto":
            if not config.autosend_data: return await interaction.response.send_message("❌ No hay alarmas activas.", ephemeral=True)
            config.autosend_data.clear()
            await interaction.response.send_message("✅ Todas las tareas automáticas han sido desactivadas.", ephemeral=True)

        # Acciones que requieren selector (Edit, Send, Delete, Auto, Menu)
        else:
            if not config.embeds_data: 
                return await interaction.response.send_message("❌ No hay embeds guardados. Crea uno primero.", ephemeral=True)
            
            # Mapeamos la acción interna correcta para el selector
            act_map = {
                "edit": "edit", "send": "send", "delete": "delete", 
                "auto": "auto", "menu": "menu_step1"
            }
            
            await interaction.response.send_message(
                "Selecciona el embed objetivo:", 
                view=EmbedSelectorView(act_map[action], self.bot_ref), 
                ephemeral=True
            )

# --- 6. VISTA DEL MENÚ VINCULADO (Lo que ve el usuario final) ---
class PersistentMenuView(discord.ui.View):
    def __init__(self, menu_config):
        super().__init__(timeout=None)
        self.menu_config = menu_config
        
        options = []
        for opt in menu_config["options"]:
            options.append(discord.SelectOption(label=opt["label"], value=opt["embed"]))
        
        # Añadimos opción de volver al inicio si quieres, o solo las opciones
        # options.append(discord.SelectOption(label="Volver al Inicio", value="MAIN_MENU_RESET", emoji="🏠"))

        select = discord.ui.Select(
            placeholder="Selecciona una opción...", 
            options=options, 
            custom_id=f"menu_v3_{random.randint(1,999999)}" # ID único para evitar conflictos
        )
        select.callback = self.callback
        self.add_item(select)

    async def callback(self, interaction: discord.Interaction):
        selected = interaction.data["values"][0]
        
        target_embed_name = selected
        # Si implementáramos volver al inicio:
        # if selected == "MAIN_MENU_RESET": target_embed_name = self.menu_config["main_embed"]

        if target_embed_name in config.embeds_data:
            d = config.embeds_data[target_embed_name]
            embed = discord.Embed(title=d["title"], description=d["description"], color=d["color"])
            if d["image"]: embed.set_image(url=d["image"])
            embed.set_footer(text=d["footer"])
            
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Error: El embed vinculado ha sido borrado.", ephemeral=True)

# ==========================================
# ⚙️ CLASE PRINCIPAL (COG)
# ==========================================

class Embeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.autosend_loop.start()

    def cog_unload(self):
        self.autosend_loop.cancel()

    # --- COMANDO PRINCIPAL ---
    @app_commands.command(name="embed_setup", description="Abre el panel de gestión de Embeds.")
    async def embed_setup(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Solo admins.", ephemeral=True)
        
        embed = discord.Embed(title="🛠️ **EMBED MANAGER**", description="Sistema avanzado de gestión de mensajes.\nUsa el menú de abajo para comenzar.", color=0x2b2d31)
        embed.set_footer(text="Hell System • V3.0")
        
        # Pasamos self.bot para que el selector pueda esperar mensajes
        await interaction.channel.send(embed=embed, view=EmbedManagerView(self.bot))
        await interaction.response.send_message("✅ Panel enviado.", ephemeral=True)

    # --- TAREA AUTOMÁTICA (AUTOSEND) ---
    @tasks.loop(minutes=1)
    async def autosend_loop(self):
        # Obtener hora actual HH:MM
        now = datetime.datetime.now().strftime("%H:%M")
        
        for uid, data in config.autosend_data.items():
            if data["time"] == now:
                try:
                    channel = self.bot.get_channel(int(data["channel"]))
                    if channel and data["embed"] in config.embeds_data:
                        d = config.embeds_data[data["embed"]]
                        embed = discord.Embed(title=d["title"], description=d["description"], color=d["color"])
                        if d["image"]: embed.set_image(url=d["image"])
                        embed.set_footer(text=d["footer"])
                        
                        await channel.send(embed=embed)
                        print(f"[AUTOSEND] Enviado {data['embed']} a las {now}")
                except Exception as e:
                    print(f"[AUTOSEND ERROR] {e}")

    @autosend_loop.before_loop
    async def before_autosend(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Embeds(bot))
