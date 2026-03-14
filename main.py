import asyncio
import os
import re
import shutil
import subprocess
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DEEZER_ARL = os.getenv("DEEZER_ARL")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Basic validation
if not BOT_TOKEN:
    logger.error("BOT_TOKEN is missing in .env")
    exit(1)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Regex to find Deezer URLs
DEEZER_REGEX = re.compile(r"https?://(?:www\.)?deezer\.(?:com|page\.link)[^\s]+")

DOWNLOADS_DIR = os.path.join(os.getcwd(), "downloads")
CONFIG_DIR = os.path.join(os.getcwd(), "config")

def setup_deemix():
    """Ensure deemix config directory exists and write ARL."""
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    if DEEZER_ARL:
        arl_path = os.path.join(CONFIG_DIR, ".arl")
        with open(arl_path, "w") as f:
            f.write(DEEZER_ARL)
            
setup_deemix()

async def start_deemix_process(url: str, output_path: str):
    """Start deemix to download a track/playlist."""
    cmd = [
        "python", "-m", "deemix",
        "--portable",
        "-b", "flac",
        "-p", output_path,
        url
    ]
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    return process

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Assalomu alaykum! Men Deezer'dan Hi-Fi (FLAC) musiqalarni tortib beruvchi botman.\n"
        "Menga Deezer track, album yoki playlist havolasini (linkini) yuboring."
    )

@dp.message(F.text)
async def process_message(message: types.Message):
    text = message.text
    matches = DEEZER_REGEX.findall(text)
    
    if not matches:
        if "deezer" in text.lower():
             await message.answer("Iltimos, to'g'ri Deezer havolasini yuboring.")
        return
        
    for url in matches:
        status_msg = await message.answer("🎵 Havola qabul qilindi. Yuklab olinmoqda (FLAC)...")
        
        # User specific unique folder
        user_folder = os.path.join(DOWNLOADS_DIR, str(message.from_user.id))
        os.makedirs(user_folder, exist_ok=True)
        
        try:
            # Clear previous downloads in user folder to avoid conflicts
            for f in os.listdir(user_folder):
                file_path = os.path.join(user_folder, f)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)

            process = await start_deemix_process(url, user_folder)
            
            sent_files = set()
            total_sent = 0
            
            while True:
                for root, _, files in os.walk(user_folder):
                    for file in files:
                        if file.endswith((".flac", ".mp3", ".m4a")):
                            file_path = os.path.join(root, file)
                            if file_path not in sent_files:
                                try:
                                    # Check if deemix finished writing by attempting rename
                                    os.rename(file_path, file_path)
                                except OSError:
                                    continue # Still writing
                                
                                # File is complete
                                try:
                                    audio = FSInputFile(file_path)
                                    await message.answer_audio(audio)
                                    sent_files.add(file_path)
                                    total_sent += 1
                                    try:
                                        os.remove(file_path)
                                    except OSError:
                                        pass
                                except Exception as e:
                                    logger.error(f"Failed to send {file}: {e}")
                                    sent_files.add(file_path)
                
                try:
                    await asyncio.wait_for(process.wait(), timeout=2.0)
                    break # Process finished
                except asyncio.TimeoutError:
                    continue # Keep polling
            
            # One final sweep to catch anything missed at the exact moment it finished
            for root, _, files in os.walk(user_folder):
                for file in files:
                    if file.endswith((".flac", ".mp3", ".m4a")):
                        file_path = os.path.join(root, file)
                        if file_path not in sent_files:
                            try:
                                audio = FSInputFile(file_path)
                                await message.answer_audio(audio)
                                total_sent += 1
                            except Exception as e:
                                logger.error(f"Failed to send {file}: {e}")
            
            if total_sent > 0:
                await status_msg.edit_text(f"✅ Yuklab olindi va yuborildi! Jami: {total_sent} ta.")
            else:
                logger.error(f"Deemix failed to download anything. total_sent=0")
                await status_msg.edit_text("❌ Musiqa yuklanmadi. Balki premium/hifi (ARL) kiritilmagan yoki havola xato bo'lishi mumkin.")
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            await status_msg.edit_text("❌ Kutilmagan xatolik yuz berdi.")
        finally:
            # Clean up user folder
            if os.path.exists(user_folder):
                shutil.rmtree(user_folder, ignore_errors=True)

from aiohttp import web

async def handle_health_check(request):
    return web.Response(text="Bot is running!")

async def main():
    logger.info("Bot is starting...")
    
    # Start health check server for Render
    app = web.Application()
    app.router.add_get("/", handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 8080)))
    asyncio.create_task(site.start())
    logger.info(f"Health check server started on port {os.getenv('PORT', 8080)}")

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
