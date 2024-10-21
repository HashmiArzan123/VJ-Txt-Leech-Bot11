import os
import re
import sys
import json
import time
import asyncio
import requests
import subprocess

import core as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN
from aiohttp import ClientSession
from pyromod import listen
from subprocess import getstatusoutput

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@bot.on_message(filters.command(["start"]))
async def start(bot: Client, m: Message):
    await m.reply_text(
        f"<b>Hello {m.from_user.mention} 👋\n\n"
        "I Am A Bot For Download Links From Your **.TXT** File And Then Upload That File On Telegram. "
        "So Basically If You Want To Use Me, First Send Me /upload Command And Then Follow A Few Steps.\n\n"
        "Use /stop to stop any ongoing task.</b>"
    )

@bot.on_message(filters.command("stop"))
async def stop_handler(_, m):
    await m.reply_text("**Stopped**🚦", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command(["upload"]))
async def upload(bot: Client, m: Message):
    editable = await m.reply_text('𝕤ᴇɴᴅ ᴛxᴛ ғɪʟᴇ ⚡️')
    input_msg: Message = await bot.listen(editable.chat.id)
    x = await input_msg.download()
    await input_msg.delete(True)

    path = f"./downloads/{m.chat.id}"

    try:
        with open(x, "r") as f:
            content = f.read()
        links = [line.split("://", 1) for line in content.split("\n") if line]
        os.remove(x)
    except Exception:
        await m.reply_text("**Invalid file input.**")
        os.remove(x)
        return

    await editable.edit(f"**𝕋ᴏᴛᴀʟ ʟɪɴᴋ𝕤 ғᴏᴜɴᴅ ᴀʀᴇ🔗🔗** **{len(links)}**\n\n**𝕊ᴇɴᴅ 𝔽ʀᴏᴍ ᴡʜᴇʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ɪɴɪᴛɪᴀʟ ɪ𝕤** **1**")
    
    input0: Message = await bot.listen(editable.chat.id)
    initial_count = int(input0.text)
    await input0.delete(True)

    await editable.edit("**Now Please Send Me Your Batch Name**")
    input1: Message = await bot.listen(editable.chat.id)
    batch_name = input1.text
    await input1.delete(True)

    await editable.edit("**𝔼ɴᴛᴇʀ ʀᴇ𝕤ᴏʟᴜᴛɪᴏɴ📸**\n144,240,360,480,720,1080 please choose quality")
    input2: Message = await bot.listen(editable.chat.id)
    resolution = input2.text
    await input2.delete(True)

    resolution_map = {
        "144": "256x144",
        "240": "426x240",
        "360": "640x360",
        "480": "854x480",
        "720": "1280x720",
        "1080": "1920x1080"
    }
    res = resolution_map.get(resolution, "UN")

    await editable.edit("Now Enter A Caption to add caption on your uploaded file")
    input3: Message = await bot.listen(editable.chat.id)
    caption = input3.text
    await input3.delete(True)

    highlighter = f"️ ⁪⁬⁮⁮⁮"
    caption_suffix = highlighter if caption == 'Robin' else caption

    await editable.edit("Now send the Thumbnail URL\nOr if you don't want a thumbnail, send 'no'")
    input6: Message = await bot.listen(editable.chat.id)
    thumb_url = input6.text
    await input6.delete(True)

    if thumb_url.startswith("http://") or thumb_url.startswith("https://"):
        getstatusoutput(f"wget '{thumb_url}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = "no"

    count = initial_count if len(links) > 1 else 1

    try:
        for i in range(count - 1, len(links)):
            V = links[i][1].replace("file/d/", "uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing", "")
            url = "https://" + V

            # Custom URL handling for specific sources
            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as resp:
                        text = await resp.text()
                        url_match = re.search(r"(https://.*?playlist.m3u8.*?)\"", text)
                        if url_match:
                            url = url_match.group(1)

            elif 'videos.classplusapp' in url:
                url = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers={'x-access-token': 'YOUR_TOKEN'}).json()['url']

            elif ("tencdn.classplusapp" in url or "classplusapp.com" in url or "media-cdn" in url) and ".m3u8" in url:
                headers = {
                    'Host': 'api.classplusapp.com',
                    'x-access-token': 'YOUR_ACCESS_TOKEN',  # Replace with your actual access token
                    'user-agent': 'Mobile-Android',
                    'app-version': '1.4.37.1',
                    'api-version': '18',
                    'device-id': '5d0d17ac8b3c9f51',
                    'device-details': '2848b866799971ca_2848b8667a33216c_SDK-30',
                    'accept-encoding': 'gzip'
                }
                params = {'url': url}
                url = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=params).json()['url']

            elif '/master.mpd' in url:
                id = url.split("/")[-2]
                url = "https://d26g5bnklkwsh4.cloudfront.net/" + id + "/master.m3u8"

            name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'{str(count).zfill(3)}) {name1[:60]}'

            if "youtu" in url:
                ytf = f"b[height<={resolution}][ext=mp4]/bv[height<={resolution}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                ytf = f"b[height<={resolution}]/bv[height<={resolution}]+ba/b/bv+ba"

            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            try:
                # Download logic
                cc = f"**[📽️] Vid_ID:** {str(count).zfill(3)}.** {name1}{caption_suffix}.mkv\n**𝔹ᴀᴛᴄʜ** » **{batch_name}**"
                cc1 = f"**[📁] Pdf_ID:** {str(count).zfill(3)}. {name1}{caption_suffix}.pdf \n**𝔹ᴀᴛᴄʜ** » **{batch_name}**"

                if "drive" in url:
                    ka = await helper.download(url, name)
                    copy = await bot.send_document(chat_id=m.chat.id, document=ka, caption=cc1)
                    count += 1
                    os.remove(ka)
                    time.sleep(1)
                elif ".pdf" in url:
                    download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                    os.system(download_cmd)
                    copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                    count += 1
                    os.remove(f'{name}.pdf')
                    time.sleep(1)
                else:
                    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    while True:
                        output = process.stdout.readline()
                        if process.poll() is not None and output == b"":
                            break
                        if output:
                            await editable.edit(f"{output.decode().strip()}")
                    copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.mp4', caption=cc)

                await editable.edit(f"**Uploaded {str(count).zfill(3)} - {name}**")
                count += 1

            except Exception as e:
                await editable.edit(f"Error occurred while processing {name}: {e}")
                continue

    except Exception as e:
        await editable.edit(f"**An error occurred:** {e}")

    await editable.edit("All files have been processed and uploaded.")

if __name__ == "__main__":
    bot.run()
