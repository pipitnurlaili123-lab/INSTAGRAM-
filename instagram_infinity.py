# =====================================================
# INFINITY INSTAGRAM MULTI - By Infinity V4
# Same Speed | Same Features | Instagram Version
# Control: Telegram Bot → Controls Instagram Accounts
# =====================================================

import asyncio
import json
import os
import random
import time
import logging
import io
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, PleaseWaitFewMinutes

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from gtts import gTTS

# ==========================================
# CONFIG — EDIT THIS SECTION
# ==========================================

TELEGRAM_BOT_TOKEN = "8603454108:AAFNVfaegrPap77ngHWL1HCjUBN_NGSrVow"  # Telegram bot token for control

# All your Instagram accounts (add as many as you want)
INSTAGRAM_ACCOUNTS = [
    {"xinfinite._": "insta_account_1", "Tobixsana": "password_1"},
    {"username": "insta_account_2", "password": "password_2"},
    {"username": "insta_account_3", "password": "password_3"},
    {"username": "insta_account_4", "password": "password_4"},
    {"username": "insta_account_5", "password": "password_5"},
    {"username": "insta_account_6", "password": "password_6"},
    {"username": "insta_account_7", "password": "password_7"},
    {"username": "insta_account_8", "password": "password_8"},
    {"username": "insta_account_9", "password": "password_9"},
    {"username": "insta_account_10", "password": "password_10"},
    {"username": "insta_account_11", "password": "password_11"},
    {"username": "insta_account_12", "password": "password_12"},
]

OWNER_ID         = 8494250384          # Your Telegram user ID
SUDO_FILE        = "sudo_ig.json"
SESSION_DIR      = "ig_sessions"       # Folder to save login sessions
VOICE_CLONES_FILE = "voice_clones.json"

tempest_API_KEY  = "sk_e326b337242b09b451e8f18041fd0a7149cc895648e36538"

DOMAIN_EXPANSION_IMAGE = "https://i.imgur.com/6Gq9V1P.jpeg"

# ==========================================
# TEXTS (Same as Telegram version)
# ==========================================
RAID_TEXTS = [
    "Infinity PAPA KA LUN CHUS ⃟♥️", "Infinity PAPA KA LUN CHUS ⃟💔", "Infinity PAPA KA LUN CHUS ⃟❣️",
    "Infinity PAPA KA LUN CHUS ⃟💕", "Infinity PAPA KA LUN CHUS ⃟💞", "Infinity PAPA KA LUN CHUS ⃟💓",
    "Infinity PAPA KA LUN CHUS ⃟💗", "Infinity PAPA KA LUN CHUS ⃟💖", "Infinity PAPA KA LUN CHUS ⃟💘",
    "Infinity PAPA KA LUN CHUS ⃟💌", "Infinity PAPA KA LUN CHUS ⃟🩶", "Infinity PAPA KA LUN CHUS ⃟🩷",
    "Infinity PAPA KA LUN CHUS ⃟🩵", "Infinity PAPA KA LUN CHUS ⃟❤️‍🔥", "Infinity PAPA KA LUN CHUS ⃟❤️‍🩹",
    "Infinity BAAP H TERA RNDYKE❤️‍🔥"
]

INFINITY_TEXTS = [
    "🎀", "💝", "🔱", "💘", "💞", "💢", "❤️‍🔥", "🌈", "🪐", "☄️",
    "⚡", "🦚", "🦈", "🕸️", "🍬", "🧃", "🗽", "🪅", "🎏", "🎸",
    "📿", "🏳️‍🌈", "🌸", "🎶", "🎵", "☃️", "❄️", "🕊️", "🍷", "🥂"
]

NCEMO_EMOJIS = [
    "💘", "🪷", "🎐", "🫧", "💥", "💢", "❤️‍🔥", "☘️", "🪐", "☄️",
    "🪽", "🦚", "🦈", "🕸️", "🍬", "🧃", "🗽", "🪅", "🎏", "🎸",
    "📿", "🏳️‍🌈", "🌸", "🎶", "🎵", "☃️", "❄️", "🕊️", "🍷", "🥂"
]

DOMAIN_MODE_TEXTS = {
    "gcnc":     RAID_TEXTS,
    "ncemo":    NCEMO_EMOJIS,
    "ncbaap":   RAID_TEXTS,
    "infinity": INFINITY_TEXTS,
}

VOICE_CHARACTERS = {
    1:  {"name": "Urokodaki",  "voice_id": "VR6AewLTigWG4xSOukaG", "description": "Deep Indian voice"},
    2:  {"name": "Kanae",      "voice_id": "EXAVITQu4vr4xnSDxMaL", "description": "Cute sweet voice"},
    3:  {"name": "Uppermoon",  "voice_id": "AZnzlk1XvdvUeBnXmlld", "description": "Creepy dark voice"},
    4:  {"name": "Tanjiro",    "voice_id": "VR6AewLTigWG4xSOukaG", "description": "Heroic determined voice"},
    5:  {"name": "Nezuko",     "voice_id": "EXAVITQu4vr4xnSDxMaL", "description": "Cute mute sounds"},
    6:  {"name": "Zenitsu",    "voice_id": "AZnzlk1XvdvUeBnXmlld", "description": "Scared whiny voice"},
    7:  {"name": "Inosuke",    "voice_id": "VR6AewLTigWG4xSOukaG", "description": "Wild aggressive voice"},
    8:  {"name": "Muzan",      "voice_id": "AZnzlk1XvdvUeBnXmlld", "description": "Evil mastermind voice"},
    9:  {"name": "Shinobu",    "voice_id": "EXAVITQu4vr4xnSDxMaL", "description": "Gentle but deadly voice"},
    10: {"name": "Giyu",       "voice_id": "VR6AewLTigWG4xSOukaG", "description": "Silent serious voice"},
}

# ==========================================
# GLOBAL STATE
# ==========================================
if os.path.exists(SUDO_FILE):
    try:
        with open(SUDO_FILE, "r") as f:
            SUDO_USERS = set(int(x) for x in json.load(f))
    except Exception:
        SUDO_USERS = {OWNER_ID}
else:
    SUDO_USERS = {OWNER_ID}

os.makedirs(SESSION_DIR, exist_ok=True)

ig_clients      = []         # List of logged-in instagrapi Client objects
executor        = ThreadPoolExecutor(max_workers=50)

bio_tasks       = {}         # {target_username: [asyncio.Task, ...]}
comment_tasks   = {}         # {media_id: [asyncio.Task, ...]}
dm_tasks        = {}         # {target_uid: [asyncio.Task, ...]}
react_tasks     = {}         # {target_uid: [asyncio.Task, ...]}
slide_targets   = set()      # usernames whose comments we auto-reply to
slidespam_targets = set()
infinity_tasks  = {}         # {target_username: [asyncio.Task, ...]}
domain_expansion_active = {} # {target_username: [asyncio.Task, ...]}

current_running_command = None
delay           = 0.1
infinity_delay  = 0.05
primary_app     = None

logging.basicConfig(level=logging.INFO)

# ==========================================
# SAVE HELPERS
# ==========================================
def save_sudo():
    with open(SUDO_FILE, "w") as f:
        json.dump(list(SUDO_USERS), f)

# ==========================================
# DECORATORS
# ==========================================
def only_sudo(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in SUDO_USERS:
            await update.message.reply_text("❌ You are not SUDO.")
            return
        return await func(update, context)
    return wrapper

def only_owner(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != OWNER_ID:
            await update.message.reply_text("❌ Only Owner can do this.")
            return
        return await func(update, context)
    return wrapper

# ==========================================
# INSTAGRAM LOGIN
# ==========================================
def login_account(acc: dict) -> Client | None:
    """Login to Instagram account, use saved session if possible."""
    cl = Client()
    cl.delay_range = [1, 3]
    session_file = os.path.join(SESSION_DIR, f"{acc['username']}.json")
    try:
        if os.path.exists(session_file):
            cl.load_settings(session_file)
            cl.login(acc["username"], acc["password"])
            cl.dump_settings(session_file)
        else:
            cl.login(acc["username"], acc["password"])
            cl.dump_settings(session_file)
        print(f"✅ Logged in: @{acc['username']}")
        return cl
    except ChallengeRequired:
        print(f"⚠️ Challenge required for @{acc['username']} — check your email/phone")
        return None
    except Exception as e:
        print(f"❌ Login failed for @{acc['username']}: {e}")
        return None

async def login_all_accounts():
    """Login all Instagram accounts concurrently."""
    global ig_clients
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(executor, login_account, acc) for acc in INSTAGRAM_ACCOUNTS]
    results = await asyncio.gather(*tasks)
    ig_clients = [cl for cl in results if cl is not None]
    print(f"🎉 {len(ig_clients)} Instagram accounts logged in!")

# ==========================================
# INSTAGRAM ASYNC WRAPPERS
# ==========================================
async def ig_set_bio(cl: Client, name: str, bio: str):
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(executor, lambda: cl.account_edit(full_name=name, biography=bio))
    except PleaseWaitFewMinutes:
        await asyncio.sleep(30)
    except Exception:
        pass

async def ig_comment(cl: Client, media_id: str, text: str):
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(executor, lambda: cl.media_comment(media_id, text))
    except PleaseWaitFewMinutes:
        await asyncio.sleep(60)
    except Exception:
        pass

async def ig_dm(cl: Client, user_id: int, text: str):
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(executor, lambda: cl.direct_send(text, [user_id]))
    except PleaseWaitFewMinutes:
        await asyncio.sleep(60)
    except Exception:
        pass

async def ig_get_user_id(username: str) -> int | None:
    loop = asyncio.get_event_loop()
    try:
        if not ig_clients:
            return None
        cl = ig_clients[0]
        uid = await loop.run_in_executor(executor, lambda: cl.user_id_from_username(username))
        return uid
    except Exception as e:
        logging.error(f"Could not get user_id for {username}: {e}")
        return None

async def ig_get_latest_post(username: str) -> str | None:
    loop = asyncio.get_event_loop()
    try:
        if not ig_clients:
            return None
        cl = ig_clients[0]
        uid = await loop.run_in_executor(executor, lambda: cl.user_id_from_username(username))
        medias = await loop.run_in_executor(executor, lambda: cl.user_medias(uid, 1))
        if medias:
            return str(medias[0].pk)
        return None
    except Exception as e:
        logging.error(f"Could not get post for {username}: {e}")
        return None

# ==========================================
# LOOP FUNCTIONS (SAME SPEED AS TELEGRAM VERSION)
# ==========================================

async def bio_loop(cl: Client, base: str, mode: str):
    """GCNC style — rapid bio/name change. 30 requests batched."""
    texts = DOMAIN_MODE_TEXTS.get(mode, RAID_TEXTS)
    i = 0
    while True:
        try:
            tasks = []
            for _ in range(30):
                text = f"{base} {texts[i % len(texts)]}"
                tasks.append(ig_set_bio(cl, text, text))
                i += 1
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.0001)
        except asyncio.CancelledError:
            return
        except Exception:
            await asyncio.sleep(0.01)

async def ncbaap_bio_loop(cl: Client, base: str):
    """GOD LEVEL — 40 bio changes batched, 0.0001s sleep."""
    i = 0
    while True:
        try:
            tasks = []
            for j in range(40):
                text = f"{base} {RAID_TEXTS[(i+j) % len(RAID_TEXTS)]}"
                tasks.append(ig_set_bio(cl, text, text))
            await asyncio.gather(*tasks, return_exceptions=True)
            i += 40
            await asyncio.sleep(0.0001)
        except asyncio.CancelledError:
            return
        except Exception:
            await asyncio.sleep(0.01)

async def infinity_bio_loop(cl: Client, base: str):
    """Infinity mode — 25 batched bio changes."""
    i = 0
    while True:
        try:
            tasks = []
            for _ in range(25):
                text = f"{base} {INFINITY_TEXTS[i % len(INFINITY_TEXTS)]}"
                tasks.append(ig_set_bio(cl, text, text))
                i += 1
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.0001)
        except asyncio.CancelledError:
            return
        except Exception:
            await asyncio.sleep(0.01)

async def infinity_godspeed_bio_loop(cl: Client, base: str):
    """GOD SPEED — 50 batched bio changes."""
    i = 0
    while True:
        try:
            tasks = []
            for j in range(50):
                text = f"{base} {INFINITY_TEXTS[(i+j) % len(INFINITY_TEXTS)]}"
                tasks.append(ig_set_bio(cl, text, text))
            await asyncio.gather(*tasks, return_exceptions=True)
            i += 50
            await asyncio.sleep(0.0001)
        except asyncio.CancelledError:
            return
        except Exception:
            await asyncio.sleep(0.01)

async def comment_spam_loop(cl: Client, media_id: str, text: str):
    """Spam comments on a post. 50 comments batched."""
    while True:
        try:
            tasks = [ig_comment(cl, media_id, text) for _ in range(50)]
            await asyncio.gather(*tasks, return_exceptions=True)
        except asyncio.CancelledError:
            return
        except Exception:
            await asyncio.sleep(0.001)

async def dm_spam_loop(cl: Client, user_id: int, text: str):
    """Spam DMs to a user. 20 DMs batched."""
    while True:
        try:
            tasks = [ig_dm(cl, user_id, text) for _ in range(20)]
            await asyncio.gather(*tasks, return_exceptions=True)
        except asyncio.CancelledError:
            return
        except Exception:
            await asyncio.sleep(0.001)

async def domain_expansion_bio_loop(target_username: str, base: str, mode: str):
    """Domain Expansion: ALL accounts rotate bio changes at 0.08s intervals."""
    texts = DOMAIN_MODE_TEXTS.get(mode, RAID_TEXTS)
    i = 0
    while True:
        try:
            for cl in ig_clients:
                title = f"{base} {texts[i % len(texts)]}"
                try:
                    await ig_set_bio(cl, title, title)
                except Exception:
                    pass
                i += 1
                await asyncio.sleep(0.08)
        except asyncio.CancelledError:
            return
        except Exception:
            await asyncio.sleep(0.3)

async def domain_expansion_watcher(target_username: str, base: str):
    """Every 3s — check if bio still has base text. If not, ALL accounts revert."""
    while True:
        try:
            await asyncio.sleep(3)
            if not ig_clients:
                continue
            loop = asyncio.get_event_loop()
            cl = ig_clients[0]
            try:
                user_id = await loop.run_in_executor(executor, lambda: cl.user_id_from_username(target_username))
                user_info = await loop.run_in_executor(executor, lambda: cl.user_info(user_id))
                live_bio = user_info.biography or ""
                if base.lower() not in live_bio.lower():
                    revert_tasks = [ig_set_bio(c, f"{base} 😈♾️", f"{base} 😈♾️") for c in ig_clients]
                    await asyncio.gather(*revert_tasks, return_exceptions=True)
            except Exception:
                pass
        except asyncio.CancelledError:
            return
        except Exception:
            await asyncio.sleep(3)

# ==========================================
# VOICE FUNCTIONS
# ==========================================
async def generate_tempest_voice(text: str, voice_id: str):
    url = f"https://api.tempest.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": tempest_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
    }
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            executor, lambda: requests.post(url, json=data, headers=headers)
        )
        if response.status_code == 200:
            return io.BytesIO(response.content)
    except Exception as e:
        logging.error(f"tempest error: {e}")
    return None

# ==========================================
# TELEGRAM COMMANDS — CORE
# ==========================================
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⌬ ɪɴꜰɪɴɪᴛʏ ɪɴsᴛᴀɢʀᴀᴍ ᴍᴜʟᴛɪ\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "𝗦𝘆𝘀𝘁𝗲𝗺 𝗢𝗻𝗹𝗶𝗻𝗲 ✅\n"
        f"𝗔𝗰𝘁𝗶𝘃𝗲 𝗔𝗰𝗰𝗼𝘂𝗻𝘁𝘀 : {len(ig_clients)}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Type /help to see all commands"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "╔═══════════════════════════════╗\n"
        "║  ⌬  I N F I N I T Y  I G  V 4  ║\n"
        "║    ◈  M U L T I  A C C  ◈      ║\n"
        "╚═══════════════════════════════╝\n"
        "\n"
        "◤━━━━━━━━━━━━━━━━━━━━━━━━◥\n"
        "  💀  B I O  C H A N G E R\n"
        "◣━━━━━━━━━━━━━━━━━━━━━━━━◢\n"
        "  ⌁ /gcnc <text>       » RAID style bio\n"
        "  ⌁ /ncemo <text>      » Emoji style bio\n"
        "  ⌁ /ncbaap <text>     » GOD LEVEL 👑\n"
        "  ⌁ /stopgcnc  /stopncemo  /stopncbaap\n"
        "  ⌁ /stopall           » Kill everything\n"
        "  ⌁ /delay <sec>       » Set speed\n"
        "\n"
        "◤━━━━━━━━━━━━━━━━━━━━━━━━◥\n"
        "  ♾️  I N F I N I T Y  B I O\n"
        "◣━━━━━━━━━━━━━━━━━━━━━━━━◢\n"
        "  ⌁ /infinity <text>\n"
        "  ⌁ /infinityfast <text>\n"
        "  ⌁ /infinitygodspeed <text>\n"
        "  ⌁ /stopinfinity\n"
        "\n"
        "◤━━━━━━━━━━━━━━━━━━━━━━━━◥\n"
        "  😈  D O M A I N  E X P A N S I O N\n"
        "◣━━━━━━━━━━━━━━━━━━━━━━━━◢\n"
        "  ⌁ /domainexpansiongcnc @user <text>\n"
        "  ⌁ /domainexpansionncemo @user <text>\n"
        "  ⌁ /domainexpansionncbaap @user <text>\n"
        "  ⌁ /domainexpansioninfinity @user <text>\n"
        "  ⌁ /stopdomainexpansion @user\n"
        "\n"
        "◤━━━━━━━━━━━━━━━━━━━━━━━━◥\n"
        "  💥  S P A M\n"
        "◣━━━━━━━━━━━━━━━━━━━━━━━━◢\n"
        "  ⌁ /commentspam <post_url> <text>\n"
        "  ⌁ /stopcommentspam\n"
        "  ⌁ /dmspam @username <text>\n"
        "  ⌁ /stopdmspam\n"
        "  ⌁ /emojispam @username <emoji>\n"
        "  ⌁ /stopemojispam\n"
        "\n"
        "◤━━━━━━━━━━━━━━━━━━━━━━━━◥\n"
        "  🥷  S L I D E  A T T A C K\n"
        "◣━━━━━━━━━━━━━━━━━━━━━━━━◢\n"
        "  ⌁ /targetslide @username\n"
        "  ⌁ /stopslide @username\n"
        "  ⌁ /slidespam @username\n"
        "  ⌁ /stopslidespam @username\n"
        "\n"
        "◤━━━━━━━━━━━━━━━━━━━━━━━━◥\n"
        "  🎵  V O I C E\n"
        "◣━━━━━━━━━━━━━━━━━━━━━━━━◢\n"
        "  ⌁ /animevn <1-10> <text>\n"
        "  ⌁ /voices\n"
        "  ⌁ /tempest <text>\n"
        "\n"
        "◤━━━━━━━━━━━━━━━━━━━━━━━━◥\n"
        "  🤖  A C C  M A N A G E M E N T\n"
        "◣━━━━━━━━━━━━━━━━━━━━━━━━◢\n"
        "  ⌁ /accounts        » List all accounts\n"
        "  ⌁ /addsudo  /delsudo  /listsudo\n"
        "  ⌁ /myid  /ping  /status\n"
        "\n"
        f"╔═══════════════════════════════╗\n"
        f"║  ⚡ {len(ig_clients)} Accounts  •  SUDO: Active  ║\n"
        "║  ♾️  Infinity IG V4 — Unstoppable ║\n"
        "╚═══════════════════════════════╝"
    )
    await update.message.reply_text(help_text)

async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    msg = await update.message.reply_text("🏓 Pinging...")
    end = time.time()
    await msg.edit_text(f"🏓 Pong! {int((end-start)*1000)}ms")

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 Your ID: {update.effective_user.id}")

# ==========================================
# BIO CHANGER COMMANDS
# ==========================================
@only_sudo
async def gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_running_command
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /gcnc <text>")
    base = " ".join(context.args)
    current_running_command = f"gcnc:{base}"

    # Stop existing
    for key in list(bio_tasks.keys()):
        for t in bio_tasks[key]: t.cancel()
    bio_tasks.clear()

    tasks = []
    for cl in ig_clients:
        task = asyncio.create_task(bio_loop(cl, base, "gcnc"))
        tasks.append(task)
    bio_tasks["gcnc"] = tasks
    await update.message.reply_text(f"🔄 GCNC Bio Changer Started on {len(ig_clients)} accounts!")

@only_sudo
async def ncemo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_running_command
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /ncemo <text>")
    base = " ".join(context.args)
    current_running_command = f"ncemo:{base}"

    for key in list(bio_tasks.keys()):
        for t in bio_tasks[key]: t.cancel()
    bio_tasks.clear()

    tasks = []
    for cl in ig_clients:
        task = asyncio.create_task(bio_loop(cl, base, "ncemo"))
        tasks.append(task)
    bio_tasks["ncemo"] = tasks
    await update.message.reply_text(f"🎭 Emoji Bio Changer Started on {len(ig_clients)} accounts!")

@only_sudo
async def ncbaap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_running_command
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /ncbaap <text>")
    base = " ".join(context.args)
    current_running_command = f"ncbaap:{base}"

    for key in list(bio_tasks.keys()):
        for t in bio_tasks[key]: t.cancel()
    bio_tasks.clear()

    tasks = []
    for cl in ig_clients:
        task = asyncio.create_task(ncbaap_bio_loop(cl, base))
        tasks.append(task)
    bio_tasks["ncbaap"] = tasks
    await update.message.reply_text(f"👑 GOD LEVEL NCBAAP Activated on {len(ig_clients)} accounts!")

@only_sudo
async def stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "gcnc" in bio_tasks:
        for t in bio_tasks["gcnc"]: t.cancel()
        del bio_tasks["gcnc"]
        await update.message.reply_text("⏹ GCNC Bio Changer Stopped!")
    else:
        await update.message.reply_text("❌ No active GCNC")

@only_sudo
async def stopncemo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "ncemo" in bio_tasks:
        for t in bio_tasks["ncemo"]: t.cancel()
        del bio_tasks["ncemo"]
        await update.message.reply_text("⏹ NCEMO Stopped!")
    else:
        await update.message.reply_text("❌ No active NCEMO")

@only_sudo
async def stopncbaap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "ncbaap" in bio_tasks:
        for t in bio_tasks["ncbaap"]: t.cancel()
        del bio_tasks["ncbaap"]
        await update.message.reply_text("⏹ GOD LEVEL NCBAAP Stopped!")
    else:
        await update.message.reply_text("❌ No active NCBAAP")

# ==========================================
# INFINITY COMMANDS
# ==========================================
@only_sudo
async def infinity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_running_command
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /infinity <text>")
    base = " ".join(context.args)
    current_running_command = f"infinity:{base}"

    for key in list(infinity_tasks.keys()):
        for t in infinity_tasks[key]: t.cancel()
    infinity_tasks.clear()

    tasks = [asyncio.create_task(infinity_bio_loop(cl, base)) for cl in ig_clients]
    infinity_tasks["infinity"] = tasks
    await update.message.reply_text(f"💀 Infinity Mode Activated on {len(ig_clients)} accounts!")

@only_sudo
async def infinityfast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_running_command, infinity_delay
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /infinityfast <text>")
    base = " ".join(context.args)
    infinity_delay = 0.03
    current_running_command = f"infinityfast:{base}"

    for key in list(infinity_tasks.keys()):
        for t in infinity_tasks[key]: t.cancel()
    infinity_tasks.clear()

    tasks = [asyncio.create_task(infinity_bio_loop(cl, base)) for cl in ig_clients]
    infinity_tasks["infinityfast"] = tasks
    await update.message.reply_text(f"⚡ FAST Infinity Activated on {len(ig_clients)} accounts!")

@only_sudo
async def infinitygodspeed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_running_command
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /infinitygodspeed <text>")
    base = " ".join(context.args)
    current_running_command = f"infinitygodspeed:{base}"

    for key in list(infinity_tasks.keys()):
        for t in infinity_tasks[key]: t.cancel()
    infinity_tasks.clear()

    tasks = [asyncio.create_task(infinity_godspeed_bio_loop(cl, base)) for cl in ig_clients]
    infinity_tasks["godspeed"] = tasks
    await update.message.reply_text(f"👑🔥 GOD SPEED Infinity ACTIVATED on {len(ig_clients)} accounts!")

@only_sudo
async def stopinfinity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if infinity_tasks:
        for key in list(infinity_tasks.keys()):
            for t in infinity_tasks[key]: t.cancel()
        infinity_tasks.clear()
        await update.message.reply_text("🛑 Infinity Stopped!")
    else:
        await update.message.reply_text("❌ No active Infinity")

# ==========================================
# COMMENT SPAM COMMANDS
# ==========================================
@only_sudo
async def commentspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_running_command
    if len(context.args) < 2:
        return await update.message.reply_text("⚠️ Usage: /commentspam <post_url_or_media_id> <text>")

    post_input = context.args[0]
    text = " ".join(context.args[1:])
    current_running_command = f"spam:{text}"

    # Extract media ID from URL if needed
    media_id = post_input
    if "instagram.com" in post_input:
        try:
            loop = asyncio.get_event_loop()
            media_id = await loop.run_in_executor(
                executor, lambda: ig_clients[0].media_pk_from_url(post_input)
            )
            media_id = str(media_id)
        except Exception as e:
            return await update.message.reply_text(f"❌ Could not extract post ID: {e}")

    # Stop existing
    for key in list(comment_tasks.keys()):
        for t in comment_tasks[key]: t.cancel()
    comment_tasks.clear()

    tasks = [asyncio.create_task(comment_spam_loop(cl, media_id, text)) for cl in ig_clients]
    comment_tasks[media_id] = tasks
    await update.message.reply_text(f"💥 COMMENT SPAM STARTED!\n📌 Post: {media_id}\n🔢 Accounts: {len(ig_clients)}")

@only_sudo
async def stopcommentspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if comment_tasks:
        for key in list(comment_tasks.keys()):
            for t in comment_tasks[key]: t.cancel()
        comment_tasks.clear()
        await update.message.reply_text("🛑 Comment Spam Stopped!")
    else:
        await update.message.reply_text("❌ No active comment spam")

# ==========================================
# DM SPAM COMMANDS
# ==========================================
@only_sudo
async def dmspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_running_command
    if len(context.args) < 2:
        return await update.message.reply_text("⚠️ Usage: /dmspam @username <text>")

    target_username = context.args[0].lstrip("@")
    text = " ".join(context.args[1:])
    current_running_command = f"dmspam:{text}"

    await update.message.reply_text(f"🔍 Looking up @{target_username}...")
    target_uid = await ig_get_user_id(target_username)
    if not target_uid:
        return await update.message.reply_text("❌ Could not find user!")

    # Stop existing
    for key in list(dm_tasks.keys()):
        for t in dm_tasks[key]: t.cancel()
    dm_tasks.clear()

    tasks = [asyncio.create_task(dm_spam_loop(cl, target_uid, text)) for cl in ig_clients]
    dm_tasks[target_username] = tasks
    await update.message.reply_text(f"💥 DM SPAM STARTED → @{target_username}\n🔢 Accounts: {len(ig_clients)}")

@only_sudo
async def stopdmspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if dm_tasks:
        for key in list(dm_tasks.keys()):
            for t in dm_tasks[key]: t.cancel()
        dm_tasks.clear()
        await update.message.reply_text("🛑 DM Spam Stopped!")
    else:
        await update.message.reply_text("❌ No active DM spam")

# ==========================================
# EMOJI SPAM (COMMENT BOMB WITH EMOJI)
# ==========================================
@only_sudo
async def emojispam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_running_command
    if len(context.args) < 2:
        return await update.message.reply_text("⚠️ Usage: /emojispam @username <emoji>")

    target_username = context.args[0].lstrip("@")
    emoji = context.args[1]
    current_running_command = "emojispam"

    await update.message.reply_text(f"🔍 Getting latest post from @{target_username}...")
    media_id = await ig_get_latest_post(target_username)
    if not media_id:
        return await update.message.reply_text("❌ Could not get post from this user!")

    for key in list(react_tasks.keys()):
        for t in react_tasks[key]: t.cancel()
    react_tasks.clear()

    tasks = [asyncio.create_task(comment_spam_loop(cl, media_id, emoji)) for cl in ig_clients]
    react_tasks[target_username] = tasks
    await update.message.reply_text(f"🎭 EMOJI SPAM {emoji} → @{target_username} latest post!\n🔢 Accounts: {len(ig_clients)}")

@only_sudo
async def stopemojispam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if react_tasks:
        for key in list(react_tasks.keys()):
            for t in react_tasks[key]: t.cancel()
        react_tasks.clear()
        await update.message.reply_text("🛑 Emoji Spam Stopped!")
    else:
        await update.message.reply_text("❌ No active emoji spam")

# ==========================================
# SLIDE COMMANDS
# ==========================================
@only_sudo
async def targetslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /targetslide @username")
    username = context.args[0].lstrip("@")
    slide_targets.add(username)
    await update.message.reply_text(f"🎯 Target slide added: @{username}")

@only_sudo
async def stopslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /stopslide @username")
    username = context.args[0].lstrip("@")
    slide_targets.discard(username)
    await update.message.reply_text(f"🛑 Slide stopped: @{username}")

@only_sudo
async def slidespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /slidespam @username")
    username = context.args[0].lstrip("@")
    slidespam_targets.add(username)
    await update.message.reply_text(f"💥 Slide spam started: @{username}")

@only_sudo
async def stopslidespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /stopslidespam @username")
    username = context.args[0].lstrip("@")
    slidespam_targets.discard(username)
    await update.message.reply_text(f"🛑 Slide spam stopped: @{username}")

# ==========================================
# DOMAIN EXPANSION
# ==========================================
async def _start_domain(update, target_username: str, base: str, mode: str):
    # Cancel existing domain for this target
    if target_username in domain_expansion_active:
        for t in domain_expansion_active[target_username]:
            t.cancel()
        await asyncio.sleep(0.2)

    mode_labels = {
        "gcnc":     "💀 GCNC",
        "ncemo":    "🎭 NCEMO",
        "ncbaap":   "👑 NCBAAP",
        "infinity": "♾️ INFINITY",
    }

    caption = (
        "╔══════════════════════════════╗\n"
        "║   😈  D O M A I N           ║\n"
        "║      E X P A N S I O N  ♾️  ║\n"
        "╚══════════════════════════════╝\n"
        "\n"
        f"  📛  Base    : {base}\n"
        f"  🎯  Target  : @{target_username}\n"
        f"  ⚙️  Mode    : {mode_labels.get(mode, mode)}\n"
        f"  ⚡  Accounts: {len(ig_clients)} active\n"
        "\n"
        "  ◈ Bio cycling — ENGAGED\n"
        "  ◈ Rate limit consumed — ENEMY SLOWED\n"
        "  ◈ Watcher — ONLINE\n"
        "\n"
        f"  ➡ /stopdomainexpansion @{target_username}"
    )

    try:
        await update.message.reply_photo(photo=DOMAIN_EXPANSION_IMAGE, caption=caption)
    except Exception:
        await update.message.reply_text(caption)

    tasks = [
        asyncio.create_task(domain_expansion_bio_loop(target_username, base, mode)),
        asyncio.create_task(domain_expansion_watcher(target_username, base)),
    ]
    domain_expansion_active[target_username] = tasks

@only_sudo
async def domainexpansiongcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("⚠️ Usage: /domainexpansiongcnc @username <text>")
    target = context.args[0].lstrip("@")
    base = " ".join(context.args[1:])
    await _start_domain(update, target, base, "gcnc")

@only_sudo
async def domainexpansionncemo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("⚠️ Usage: /domainexpansionncemo @username <text>")
    target = context.args[0].lstrip("@")
    base = " ".join(context.args[1:])
    await _start_domain(update, target, base, "ncemo")

@only_sudo
async def domainexpansionncbaap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("⚠️ Usage: /domainexpansionncbaap @username <text>")
    target = context.args[0].lstrip("@")
    base = " ".join(context.args[1:])
    await _start_domain(update, target, base, "ncbaap")

@only_sudo
async def domainexpansioninfinity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("⚠️ Usage: /domainexpansioninfinity @username <text>")
    target = context.args[0].lstrip("@")
    base = " ".join(context.args[1:])
    await _start_domain(update, target, base, "infinity")

@only_sudo
async def stopdomainexpansion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /stopdomainexpansion @username")
    target = context.args[0].lstrip("@")
    if target in domain_expansion_active:
        for t in domain_expansion_active[target]:
            t.cancel()
        del domain_expansion_active[target]
        await update.message.reply_text(f"✅ Domain Expansion LIFTED for @{target}\n♾️ The barrier is gone.")
    else:
        await update.message.reply_text(f"❌ No active Domain Expansion for @{target}")

# ==========================================
# STOP ALL
# ==========================================
@only_sudo
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_running_command
    current_running_command = None

    for d in [bio_tasks, comment_tasks, dm_tasks, react_tasks, infinity_tasks]:
        for key in list(d.keys()):
            for t in d[key]: t.cancel()
        d.clear()

    for key in list(domain_expansion_active.keys()):
        for t in domain_expansion_active[key]: t.cancel()
    domain_expansion_active.clear()

    slide_targets.clear()
    slidespam_targets.clear()

    await update.message.reply_text("⏹ ALL ACTIVITIES STOPPED!")

@only_sudo
async def delay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global delay
    if not context.args:
        return await update.message.reply_text(f"⏱ Current delay: {delay}s")
    try:
        delay = max(0.1, float(context.args[0]))
        await update.message.reply_text(f"✅ Delay set to {delay}s")
    except Exception:
        await update.message.reply_text("❌ Invalid number")

# ==========================================
# STATUS COMMANDS
# ==========================================
@only_sudo
async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_text = f"""
📊 Infinity IG V4 Status:

🎀 Bio Changers: {sum(len(t) for t in bio_tasks.values())}
♾️ Infinity Sessions: {sum(len(t) for t in infinity_tasks.values())}
💬 Comment Spam: {sum(len(t) for t in comment_tasks.values())}
📩 DM Spam: {sum(len(t) for t in dm_tasks.values())}
🎭 Emoji Spam: {sum(len(t) for t in react_tasks.values())}
🥷 Slide Targets: {len(slide_targets)}
💥 Slide Spam: {len(slidespam_targets)}
😈 Domain Expansions: {len(domain_expansion_active)}

⏱ Delay: {delay}s
♾️ Infinity Delay: {infinity_delay}s
📱 Active Accounts: {len(ig_clients)}
👑 SUDO Users: {len(SUDO_USERS)}
    """
    await update.message.reply_text(status_text)

@only_sudo
async def accounts_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ig_clients:
        return await update.message.reply_text("❌ No accounts logged in!")
    lines = ["╔══════════════════════╗",
             "║  📱 IG ACCOUNTS LIST  ║",
             "╚══════════════════════╝", ""]
    for i, cl in enumerate(ig_clients):
        try:
            lines.append(f"  {i+1}. @{cl.username} ✅")
        except Exception:
            lines.append(f"  {i+1}. Account {i+1} ⚠️")
    lines.append(f"\n✅ Total: {len(ig_clients)} accounts")
    await update.message.reply_text("\n".join(lines))

# ==========================================
# VOICE COMMANDS
# ==========================================
@only_sudo
async def animevn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("⚠️ Usage: /animevn <char_numbers> <text>\nExample: /animevn 1 2 Hello world")
    try:
        char_numbers, text_parts = [], []
        for arg in context.args:
            if arg.isdigit() and int(arg) in VOICE_CHARACTERS:
                char_numbers.append(int(arg))
            else:
                text_parts.append(arg)
        if not char_numbers:
            return await update.message.reply_text("❌ Valid character numbers: 1-10")
        text = " ".join(text_parts)
        if not text:
            return await update.message.reply_text("❌ Please provide text to speak")
        await update.message.reply_text(f"🎭 Generating voices: {', '.join([VOICE_CHARACTERS[n]['name'] for n in char_numbers])}...")
        for num in char_numbers:
            vc = VOICE_CHARACTERS[num]
            audio = await generate_tempest_voice(text, vc["voice_id"])
            if audio:
                await update.message.reply_voice(voice=audio, caption=f"🎀 {vc['name']}: {text}")
            else:
                tts = gTTS(text=text, lang='ja', slow=False)
                f = io.BytesIO()
                tts.write_to_fp(f); f.seek(0)
                await update.message.reply_voice(voice=f, caption=f"🎀 {vc['name']} (fallback): {text}")
            await asyncio.sleep(1)
    except Exception as e:
        await update.message.reply_text(f"❌ Voice error: {e}")

@only_sudo
async def tempest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /tempest <text>")
    text = " ".join(context.args)
    audio = await generate_tempest_voice(text, VOICE_CHARACTERS[1]["voice_id"])
    if audio:
        await update.message.reply_voice(voice=audio, caption=f"🎙️ {VOICE_CHARACTERS[1]['name']}: {text}")
    else:
        tts = gTTS(text=text, lang='en', slow=False)
        f = io.BytesIO(); tts.write_to_fp(f); f.seek(0)
        await update.message.reply_voice(voice=f, caption=f"🗣️ Fallback TTS: {text}")

@only_sudo
async def voices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice_list = "🎭 Available Anime Voices:\n\n"
    for num, v in VOICE_CHARACTERS.items():
        voice_list += f"{num}. {v['name']} — {v['description']}\n"
    voice_list += "\n🎀 Usage: /animevn 1 2 3 Hello world"
    await update.message.reply_text(voice_list)

# ==========================================
# SUDO MANAGEMENT
# ==========================================
@only_owner
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user")
    uid = update.message.reply_to_message.from_user.id
    SUDO_USERS.add(uid)
    save_sudo()
    await update.message.reply_text(f"✅ SUDO added: {uid}")

@only_owner
async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user")
    uid = update.message.reply_to_message.from_user.id
    if uid in SUDO_USERS:
        SUDO_USERS.remove(uid)
        save_sudo()
        await update.message.reply_text(f"🗑 SUDO removed: {uid}")
    else:
        await update.message.reply_text("❌ User not in SUDO")

@only_sudo
async def listsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sudo_list = "\n".join([f"👑 {uid}" for uid in SUDO_USERS])
    await update.message.reply_text(f"👑 SUDO Users:\n{sudo_list}")

# ==========================================
# BOT SETUP & MAIN
# ==========================================
def build_app(token: str) -> Application:
    app = Application.builder().token(token).build()

    # Core
    app.add_handler(CommandHandler("start",   start_cmd))
    app.add_handler(CommandHandler("help",    help_cmd))
    app.add_handler(CommandHandler("ping",    ping_cmd))
    app.add_handler(CommandHandler("myid",    myid))
    app.add_handler(CommandHandler("status",  status_cmd))
    app.add_handler(CommandHandler("accounts",accounts_cmd))

    # Bio Changer
    app.add_handler(CommandHandler("gcnc",    gcnc))
    app.add_handler(CommandHandler("ncemo",   ncemo))
    app.add_handler(CommandHandler("ncbaap",  ncbaap))
    app.add_handler(CommandHandler("stopgcnc",   stopgcnc))
    app.add_handler(CommandHandler("stopncemo",  stopncemo))
    app.add_handler(CommandHandler("stopncbaap", stopncbaap))
    app.add_handler(CommandHandler("stopall",    stopall))
    app.add_handler(CommandHandler("delay",      delay_cmd))

    # Infinity
    app.add_handler(CommandHandler("infinity",         infinity))
    app.add_handler(CommandHandler("infinityfast",     infinityfast))
    app.add_handler(CommandHandler("infinitygodspeed", infinitygodspeed))
    app.add_handler(CommandHandler("stopinfinity",     stopinfinity))

    # Spam
    app.add_handler(CommandHandler("commentspam",     commentspam))
    app.add_handler(CommandHandler("stopcommentspam", stopcommentspam))
    app.add_handler(CommandHandler("dmspam",          dmspam))
    app.add_handler(CommandHandler("stopdmspam",      stopdmspam))
    app.add_handler(CommandHandler("emojispam",       emojispam))
    app.add_handler(CommandHandler("stopemojispam",   stopemojispam))

    # Slide
    app.add_handler(CommandHandler("targetslide",    targetslide))
    app.add_handler(CommandHandler("stopslide",      stopslide))
    app.add_handler(CommandHandler("slidespam",      slidespam))
    app.add_handler(CommandHandler("stopslidespam",  stopslidespam))

    # Voice
    app.add_handler(CommandHandler("animevn",  animevn))
    app.add_handler(CommandHandler("tempest",  tempest_cmd))
    app.add_handler(CommandHandler("voices",   voices))

    # Domain Expansion
    app.add_handler(CommandHandler("domainexpansiongcnc",      domainexpansiongcnc))
    app.add_handler(CommandHandler("domainexpansionncemo",     domainexpansionncemo))
    app.add_handler(CommandHandler("domainexpansionncbaap",    domainexpansionncbaap))
    app.add_handler(CommandHandler("domainexpansioninfinity",  domainexpansioninfinity))
    app.add_handler(CommandHandler("stopdomainexpansion",      stopdomainexpansion))

    # SUDO
    app.add_handler(CommandHandler("addsudo",  addsudo))
    app.add_handler(CommandHandler("delsudo",  delsudo))
    app.add_handler(CommandHandler("listsudo", listsudo))

    return app

async def main():
    print("🔐 Logging into all Instagram accounts...")
    await login_all_accounts()

    if not ig_clients:
        print("❌ No Instagram accounts logged in. Check credentials!")
        return

    print(f"✅ {len(ig_clients)} accounts ready!")
    print("🤖 Starting Telegram control bot...")

    app = build_app(TELEGRAM_BOT_TOKEN)

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    print("🎉 Infinity Instagram V4 is LIVE!")
    print(f"📱 Instagram Accounts: {len(ig_clients)}")
    print("🔫 All features activated — waiting for commands...")

    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Infinity IG V4 Shutting Down...")
    except Exception as e:
        print(f"❌ Error: {e}")
