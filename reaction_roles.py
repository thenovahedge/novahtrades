import discord
from discord.ext import commands
import asyncio
import os


# ─────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN")



# The emoji users must react with to get verified
VERIFY_EMOJI = "✅"

# The name of the channel where the verification message will be posted
VERIFY_CHANNEL_NAME = "start-here"

# The name of the role that will be granted upon reaction
MEMBER_ROLE_NAME = "Member"

# The verification message text
VERIFY_MESSAGE = (
    "👋 **Welcome to The Novah Edge!**\n\n"
    "Before you can access the community, please verify that you've read and agree to our rules.\n\n"
    "React with ✅ below to verify and unlock access to the server!\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "📜 **Rules:**\n"
    "1. Respect everyone in the community.\n"
    "2. No spam or self-promotion.\n"
    "3. Keep discussions relevant to trading & mentorship.\n"
    "4. Follow Discord's Terms of Service.\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "✅ React below to gain access!"
)
# ─────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Stores the ID of the verification message so we know which message to watch
verify_message_id = None


@bot.event
async def on_ready():
    print(f"✅ Reaction Roles Bot logged in as {bot.user}")
    print(f"Use !post_verify in #{VERIFY_CHANNEL_NAME} to post the verification message.")


@bot.command()
@commands.has_permissions(administrator=True)
async def post_verify(ctx):
    """
    Admin command: Posts (or re-posts) the verification message in the
    verification channel and adds the reaction for users to click.
    Usage: !post_verify
    """
    global verify_message_id

    # Find the verification channel
    channel = discord.utils.get(ctx.guild.text_channels, name=VERIFY_CHANNEL_NAME)
    if channel is None:
        await ctx.send(
            f"❌ Could not find a channel named **#{VERIFY_CHANNEL_NAME}**. "
            f"Make sure it exists or update VERIFY_CHANNEL_NAME in the script."
        )
        return

    # Post the verification message
    msg = await channel.send(VERIFY_MESSAGE)
    await msg.add_reaction(VERIFY_EMOJI)

    verify_message_id = msg.id
    await ctx.send(
        f"✅ Verification message posted in {channel.mention}! "
        f"Message ID: `{msg.id}` (saved in memory)."
    )
    print(f"Verification message posted. ID: {msg.id}")


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """Fires whenever anyone reacts to any message."""
    global verify_message_id

    # Ignore bot reactions
    if payload.user_id == bot.user.id:
        return

    # Only act on the verification message
    if verify_message_id is None or payload.message_id != verify_message_id:
        return

    # Only act on the correct emoji
    if str(payload.emoji) != VERIFY_EMOJI:
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return

    member = guild.get_member(payload.user_id)
    if member is None:
        return

    # Find the Member role
    role = discord.utils.get(guild.roles, name=MEMBER_ROLE_NAME)
    if role is None:
        print(
            f"⚠️  Role '{MEMBER_ROLE_NAME}' not found! "
            f"Make sure it exists in the server (run !setup first)."
        )
        return

    # Grant the role
    if role not in member.roles:
        await member.add_roles(role, reason="Verified via reaction role.")
        print(f"✅ Granted '{MEMBER_ROLE_NAME}' to {member.display_name} ({member.id})")
    else:
        print(f"ℹ️  {member.display_name} already has the '{MEMBER_ROLE_NAME}' role.")


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    """Optional: Remove the Member role if the user un-reacts."""
    global verify_message_id

    if verify_message_id is None or payload.message_id != verify_message_id:
        return

    if str(payload.emoji) != VERIFY_EMOJI:
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return

    member = guild.get_member(payload.user_id)
    if member is None:
        return

    role = discord.utils.get(guild.roles, name=MEMBER_ROLE_NAME)
    if role and role in member.roles:
        await member.remove_roles(role, reason="Un-verified (reaction removed).")
        print(f"🔴 Removed '{MEMBER_ROLE_NAME}' from {member.display_name} ({member.id})")


if __name__ == "__main__":
    bot.run(BOT_TOKEN)
