import discord
from discord.ext import commands
import asyncio
import os

# --- INSTRUCTIONS ---
# 1. Go to https://discord.com/developers/applications
# 2. Click "New Application", give it a name like "Mentorship Setup Bot"
# 3. Go to "Bot" on the left menu, click "Add Bot" or "Reset Token" to get your token.
# 4. Scroll down on the Bot page and enable ALL THREE "Privileged Gateway Intents" (Presence, Server Members, Message Content).
# 5. Go to "OAuth2" -> "URL Generator" on the left.
# 6. Check the "bot" scope, and under Bot Permissions, check "Administrator".
# 7. Copy the generated URL at the bottom, paste it into your browser, and invite the bot to your empty Trading Server.
# 8. Paste your bot token below, save, and run this script (python setup_server.py).

BOT_TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print("Type '!setup' in any channel in your server to build the Daytrading Community structure!")

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    guild = ctx.guild
    await ctx.send("🚀 Starting server setup! Please wait...")

    try:
        # --- 1. Roles ---
        print("Creating roles...")
        founder_role = await guild.create_role(name="Founder / Mentor", color=discord.Color.red(), hoist=True, mentionable=True)
        mod_role = await guild.create_role(name="Moderator", color=discord.Color.blue(), hoist=True, mentionable=True)
        premium_role = await guild.create_role(name="Premium Member", color=discord.Color.gold(), hoist=True, mentionable=True)
        # Member role: granted automatically by the reaction-role bot after verification
        member_role = await guild.create_role(name="Member", color=discord.Color.green(), hoist=True, mentionable=False)
        
        # --- 2. Clear existing channels (optional but recommended for a fresh server) ---
        # NOTE: Uncomment the next block if you want to wipe the server first.
        # for channel in guild.channels:
        #     await channel.delete()

        # --- Permissions Setup ---
        everyone_perms       = discord.PermissionOverwrite(read_messages=False)
        read_only_perms      = discord.PermissionOverwrite(read_messages=True, send_messages=False)
        member_read_perms    = discord.PermissionOverwrite(read_messages=True, send_messages=False)
        member_chat_perms    = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        premium_perms        = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        start_here_perms     = discord.PermissionOverwrite(read_messages=True, send_messages=False)  # visible to everyone (for verification)

        # --- 3. Categories & Channels ---
        print("Creating categories & channels...")
        
        # CATEGORY: Welcome & Info
        # start-here is visible to EVERYONE (unverified) so they can react & get the Member role.
        # Other info channels are locked to Members+.
        info_cat = await guild.create_category("👋 Welcome & Information")
        await guild.create_text_channel(
            "start-here", category=info_cat,
            overwrites={guild.default_role: start_here_perms}  # public – react here to verify
        )
        await guild.create_text_channel(
            "welcome", category=info_cat,
            overwrites={guild.default_role: everyone_perms, member_role: member_read_perms}
        )
        await guild.create_text_channel(
            "rules", category=info_cat,
            overwrites={guild.default_role: everyone_perms, member_role: member_read_perms}
        )
        await guild.create_text_channel(
            "announcements", category=info_cat,
            overwrites={guild.default_role: everyone_perms, member_role: member_read_perms}
        )

        # CATEGORY: Trading Floor (Premium only)
        trading_cat = await guild.create_category("📈 Trading Floor", overwrites={
            guild.default_role: everyone_perms,
            premium_role: premium_perms
        })
        await guild.create_text_channel("pre-market-prep", category=trading_cat)
        await guild.create_text_channel("chart-markups", category=trading_cat)
        await guild.create_voice_channel("Live Trading Floor", category=trading_cat)

        # CATEGORY: Mentorship
        mentor_cat = await guild.create_category("📚 Mentorship & Education", overwrites={
            guild.default_role: everyone_perms,
            premium_role: premium_perms
        })
        await guild.create_text_channel("educational-resources", category=mentor_cat)
        await guild.create_text_channel("q-and-a", category=mentor_cat)
        await guild.create_voice_channel("1-on-1 Coaching", category=mentor_cat)

        # CATEGORY: Community Lounge (Members+ only)
        lounge_cat = await guild.create_category(
            "☕ Community Lounge",
            overwrites={guild.default_role: everyone_perms, member_role: member_chat_perms}
        )
        await guild.create_text_channel("general-chat", category=lounge_cat)
        await guild.create_text_channel("wins-and-losses", category=lounge_cat)
        await guild.create_text_channel("mindset-psychology", category=lounge_cat)
        await guild.create_voice_channel("Hangout", category=lounge_cat)

        await ctx.send("✅ Server setup complete! Welcome to your new Daytrading Mentorship community.")
        print("Setup completed successfully.")

    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")
        print(f"Error during setup: {e}")

if __name__ == "__main__":
    if False:
        print("⚠️ Please update BOT_TOKEN in the script before running!")
    else:
        bot.run(BOT_TOKEN)
