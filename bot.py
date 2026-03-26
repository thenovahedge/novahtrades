import discord
from discord.ext import commands
import asyncio
import os
import json
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()


# ─────────────────────────────────────────────
#  CONFIGURATION — edit these if needed
# ─────────────────────────────────────────────
# Load configuration from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ CRITICAL ERROR: 'BOT_TOKEN' environment variable is missing!")
    print("Please add it in your Railway 'Variables' tab.")



VERIFY_EMOJI        = "📈"

VERIFY_CHANNEL_NAME = "start-here"
MEMBER_ROLE_NAME    = "member"


# ─────────────────────────────────────────────

def create_verify_embed():
    embed = discord.Embed(
        title="👋 Welcome to The Novah Edge!",
        description=(
            "Before you can access the community, please verify that you've read and agree to our rules.\n\n"
            "React with 📈 below to verify and unlock access to the server!"

        ),
        color=0x00AEFF  # Novah Blue
    )
    
    rules_text = (
        "**Maintain a respectful behaviour**\n"
        "Refrain from harassment, arguments, or disruptive behaviour.\n\n"
        "**Stay On-Topic**\n"
        "Keep discussions relevant to the channel topic.\n\n"
        "**No Self-Promo**\n"
        "Do not promote other Discord servers, websites, or services in this server or via DMs.\n\n"
        "**No NSFW Content**\n"
        "Posting NSFW content will result in an immediate ban."
    )

    
    
    embed.add_field(name="📜 Rules", value=rules_text + "\n\u200b", inline=False)


    
    # Removed old spacer field, using \n in the Rules value instead

    
    tos_text = (
        "**Terms of Service**\n"
        "By reacting, you acknowledge that all content is for educational purposes only. "
        "We are not financial advisors, and you assume all risk for your own trading decisions."
    )
    embed.add_field(name="⚖️ Terms of Service", value=tos_text + "\n\u200b", inline=False)

    
    embed.add_field(name="📈 Verification", value="React below to gain access!", inline=False)

    embed.set_footer(text="The Novah Edge")
    # Using the jetski image as a thumbnail if possible, or just a stylish color bar

    return embed

# ─────────────────────────────────────────────


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

# CONFIG FILE to persist state across restarts
CONFIG_FILE = "bot_config.json"

# Stores the verification message ID
verify_message_id = None

def save_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump({"verify_message_id": verify_message_id}, f)

def load_config():
    global verify_message_id
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                bot.verify_message_id = data.get("verify_message_id")
        except:
            pass


# ══════════════════════════════════════════════
#  STARTUP
# ══════════════════════════════════════════════
@bot.event
async def on_ready():
    print(f"✅ Bot logged in as {bot.user}")
    # Load message ID from environment variable or JSON file
    env_id = os.getenv("VERIFY_MESSAGE_ID")
    if env_id:
        try:
            bot.verify_message_id = int(env_id)
            print(f"📊 Monitoring verification message ID (from ENV): {bot.verify_message_id}")
        except ValueError:
            print("⚠️ INVALID VERIFY_MESSAGE_ID in environment variables.")
    
    if not bot.verify_message_id:
        try:
            with open("bot_config.json", "r") as f:
                config = json.load(f)
                bot.verify_message_id = config.get("verify_message_id")
                if bot.verify_message_id:
                    print(f"📊 Monitoring verification message ID (from JSON): {bot.verify_message_id}")
                else:
                    print("📊 No verification message ID found in JSON. Run !setup to initialize.")
        except FileNotFoundError:
            print("📊 No verification message ID found. Run !setup to initialize.")

    # --- Update bot username to "Novah" ---
    try:
        await bot.user.edit(username="Novah")
        print("✅ Username set to 'Novah'")
    except discord.HTTPException as e:
        print(f"⚠️  Could not update username: {e}")

    # --- Update bot avatar to jetski image ---
    try:
        avatar_path = os.path.join(os.path.dirname(__file__), "pfp_jetski.png")
        with open(avatar_path, "rb") as f:
            avatar_bytes = f.read()
        await bot.user.edit(avatar=avatar_bytes)
        print("✅ Avatar updated to jetski image")
    except (discord.HTTPException, FileNotFoundError) as e:
        print(f"⚠️  Could not update avatar: {e}")

    print("Commands available:")

    print("  !setup        — Build the full server structure (admin only)")
    print("  !post_verify  — Post the verification message in #start-here (admin only)")
    print("  !post_socials — Post the TikTok & Instagram links in #socials (admin only)")








# ══════════════════════════════════════════════
#  !setup  — Build the full server structure
# ══════════════════════════════════════════════
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    guild = ctx.guild
    
    setup_embed = discord.Embed(
        title="🚀 Server Setup",
        description="Starting minimal server setup. Please wait...",
        color=discord.Color.blue()
    )
    status_msg = await ctx.send(embed=setup_embed)

    try:
        # --- 1. Roles ---
        print("Creating/checking roles...")
        member_role = discord.utils.get(guild.roles, name=MEMBER_ROLE_NAME)
        if not member_role:
            member_role = await guild.create_role(name=MEMBER_ROLE_NAME, color=discord.Color.green(), hoist=True, mentionable=False)
            print(f"Created role: {MEMBER_ROLE_NAME}")
        
        # Check hierarchy
        bot_highest_role = guild.me.top_role
        if bot_highest_role.position <= member_role.position:
            print(f"⚠️  WARNING: Bot role ({bot_highest_role.name}) is below or equal to {MEMBER_ROLE_NAME}!")
            await ctx.send(f"⚠️ **Warning**: My role is too low in the list. Move my role **above** **{MEMBER_ROLE_NAME}** in Server Settings or I won't be able to give people the role!")

        # --- Permissions ---

        # start-here/socials are public so unverified users can see
        public_read_perms = discord.PermissionOverwrite(read_messages=True, send_messages=False, add_reactions=False)

        # --- 2. Channels ---
        print("Creating channels...")

        # Create channels at the top level (no category)
        if not discord.utils.get(guild.text_channels, name=VERIFY_CHANNEL_NAME):
            await guild.create_text_channel(
                VERIFY_CHANNEL_NAME,
                overwrites={guild.default_role: public_read_perms}
            )
            print(f"Created channel: {VERIFY_CHANNEL_NAME}")

        if not discord.utils.get(guild.text_channels, name="socials"):
            await guild.create_text_channel(
                "socials",
                overwrites={guild.default_role: public_read_perms}
            )
            print("Created channel: socials")

        # --- 3. Automated Posting ---
        print("Posting initial embeds...")
        
        # Post Socials
        socials_channel = discord.utils.get(guild.text_channels, name="socials")
        if socials_channel:
            try:
                await socials_channel.purge(limit=10)
            except:
                pass
            
            socials_embed = discord.Embed(
                title="Follow us!",
                description="🔗 https://www.tiktok.com/@novahtrades\n🔗 https://www.instagram.com/novahtrades",
                color=0x00AEFF
            )
            socials_embed.set_footer(text="The Novah Edge")
            await socials_channel.send(embed=socials_embed)

        # Post Verification
        verify_channel = discord.utils.get(guild.text_channels, name=VERIFY_CHANNEL_NAME)
        if verify_channel:
            try:
                await verify_channel.purge(limit=10)
            except:
                pass
            
            v_embed = create_verify_embed()
            v_msg = await verify_channel.send(embed=v_embed)
            await v_msg.add_reaction(VERIFY_EMOJI)
            
            global verify_message_id
            verify_message_id = v_msg.id
            save_config()

        # --- 4. Sync Permissions for Existing Channels ---
        print("Syncing permissions for all channels...")
        for channel in guild.channels:
            try:
                # Add read access for Member role
                await channel.set_permissions(member_role, read_messages=True, reason="Auto-setup role access")
                print(f"   [OK] Updated {channel.name}")
            except Exception as e:
                print(f"   [X] Failed {channel.name}: {e}")

        setup_embed.title = "✅ Setup & Sync Complete"
        setup_embed.description = (
            "Server setup finished! Roles verified, channels created, and **Member** permissions synced to all existing channels.\n\n"
            "**Channels Active:**\n"
            "📍 #start-here (React to get access)\n"
            "📱 #socials (Links posted)\n\n"
            "Everyone with the **Member** role can now see your entire server!"
        )



        setup_embed.color = discord.Color.green()
        await status_msg.edit(embed=setup_embed)

        print("Minimal setup completed successfully.")

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Setup Error",
            description=f"An error occurred during setup: `{e}`",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        print(f"Error during setup: {e}")




# ══════════════════════════════════════════════
#  !post_verify  — Post the reaction-role message
# ══════════════════════════════════════════════
@bot.command()
@commands.has_permissions(administrator=True)
async def post_verify(ctx):
    global verify_message_id

    channel = discord.utils.get(ctx.guild.text_channels, name=VERIFY_CHANNEL_NAME)
    if channel is None:
        await ctx.send(f"❌ Could not find **#{VERIFY_CHANNEL_NAME}**. Run `!setup` first.")
        return

    embed = create_verify_embed()
    msg = await channel.send(embed=embed)

    await msg.add_reaction(VERIFY_EMOJI)
    global verify_message_id
    verify_message_id = msg.id
    save_config()

    success_embed = discord.Embed(

        title="✅ Success",
        description=f"Verification message posted in {channel.mention}!",
        color=discord.Color.green()
    )
    await ctx.send(embed=success_embed)

    print(f"Verification message posted. ID: {msg.id}")


# ══════════════════════════════════════════════
#  !post_socials  — Post the TikTok & Instagram links
# ══════════════════════════════════════════════
@bot.command()
@commands.has_permissions(administrator=True)
async def post_socials(ctx):
    channel = discord.utils.get(ctx.guild.text_channels, name="socials")
    if channel is None:
        # If the channel doesn't exist, try to create it in the Welcome & Info category if possible
        await ctx.send("❌ Could not find **#socials**. Run `!setup` or create the channel manually.")
        return

    embed = discord.Embed(
        title="Follow us!",
        description="🔗 https://www.tiktok.com/@novahtrades\n🔗 https://www.instagram.com/novahtrades",
        color=0x00AEFF  # Novah Blue
    )



    embed.set_footer(text="The Novah Edge")





    
    await channel.send(embed=embed)
    
    success_embed = discord.Embed(
        title="✅ Success",
        description=f"Social links posted in {channel.mention}!",
        color=discord.Color.green()
    )
    await ctx.send(embed=success_embed)



# ══════════════════════════════════════════════
#  REACTION ADD — grant Member role
# ══════════════════════════════════════════════
@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    global verify_message_id

    if payload.user_id == bot.user.id:
        return
    if verify_message_id is None or payload.message_id != verify_message_id:
        return
    if str(payload.emoji) != VERIFY_EMOJI:
        return

    guild  = bot.get_guild(payload.guild_id)
    if not guild:
        print(f"🔍 Reaction debug: Guild {payload.guild_id} not found in cache.")
        return
        
    print(f"🔍 Reaction debug: Received {payload.emoji} on message {payload.message_id} (Watching: {verify_message_id})")

    member = guild.get_member(payload.user_id)
    if not member:
        try:
            member = await guild.fetch_member(payload.user_id)
        except Exception as e:
            print(f"🔍 Reaction debug: Could not fetch member {payload.user_id}: {e}")
            return
            
    role = discord.utils.get(guild.roles, name=MEMBER_ROLE_NAME)



    if role not in member.roles:
        try:
            await member.add_roles(role, reason="Verified via reaction.")
            print(f"✅ Granted '{MEMBER_ROLE_NAME}' to {member.display_name}")
        except discord.Forbidden:
            print(f"❌ FAILED: Missing Permissions. Bot role must be ABOVE '{MEMBER_ROLE_NAME}' in role settings.")
        except Exception as e:
            print(f"❌ ERROR: {e}")





# ══════════════════════════════════════════════
#  REACTION REMOVE — revoke Member role
# ══════════════════════════════════════════════
@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    global verify_message_id

    if verify_message_id is None or payload.message_id != verify_message_id:
        return
    if str(payload.emoji) != VERIFY_EMOJI:
        return

    guild  = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id) if guild else None
    role   = discord.utils.get(guild.roles, name=MEMBER_ROLE_NAME) if guild else None

    if member and role and role in member.roles:
        await member.remove_roles(role, reason="Un-verified (reaction removed).")
        print(f"🔴 Removed '{MEMBER_ROLE_NAME}' from {member.display_name}")


if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ Cannot start bot: No token found.")
    else:
        try:
            bot.run(BOT_TOKEN)
        except Exception as e:
            print(f"❌ CRITICAL CRASH: {e}")

