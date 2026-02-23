import asyncio
import os
import sys
from telethon import TelegramClient

API_ID = 611335
API_HASH = "d524b414d21f4d37f08684c1df41ac9c"

CHAT_ID = os.environ.get("CHAT_ID")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
# 如果启用话题功能，添加 MESSAGE_THREAD_ID = os.environ.get("MESSAGE_THREAD_ID")
COMMIT_URL = os.environ.get("COMMIT_URL")
COMMIT_MESSAGE = os.environ.get("COMMIT_MESSAGE")
RUN_URL = os.environ.get("RUN_URL")
COMMIT_AUTHOR = os.environ.get("COMMIT_AUTHOR")
BRANCH = os.environ.get("BRANCH")
MSG_TEMPLATE = """
New push to github! # 这里填需要发送的文字
Branch: **{branch}**
Changelog: 
```
{commit_message}

```
[Commit({short_sha})]({commit_url})
[Workflow run]({run_url})

by **{commit_author}**
""".strip()


def get_caption():
    msg = MSG_TEMPLATE.format( # 如果要发送的信息中用到变量需要在这里传递
        commit_message=COMMIT_MESSAGE,
        commit_url=COMMIT_URL,
        run_url=RUN_URL,
        commit_author=COMMIT_AUTHOR,
        branch=BRANCH,
    )
    if len(msg) > 1024:
        return COMMIT_URL
    return msg


def check_environ():
    global CHAT_ID # 如果启用话题功能，这里改为 global CHAT_ID, MESSAGE_THREAD_ID
    if BOT_TOKEN is None:
        print("[-] Invalid BOT_TOKEN")
        exit(1)
    if CHAT_ID is None:
        print("[-] Invalid CHAT_ID")
        exit(1)
    else:
        try:
            CHAT_ID = int(CHAT_ID)
        except:
            pass


async def main():
    print("[+] Uploading to telegram")
    check_environ()
    files = sys.argv[1:]
    print("[+] Files:", files)
    if len(files) <= 0:
        print("[-] No files to upload")
        exit(1)
    print("[+] Logging in Telegram with bot")
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    session_dir = os.path.join(script_dir, "bot")
    
    async with await TelegramClient(session=session_dir, api_id=API_ID, api_hash=API_HASH).start(bot_token=BOT_TOKEN) as bot:
        caption_text = get_caption()
        print("[+] Caption: ")
        print("---")
        print(caption_text)
        print("---")
        print("[+] Sending")
        
        await bot.send_file(entity=CHAT_ID, file=files[0], caption=caption_text, parse_mode="markdown")
        
        print("[+] Done!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"[-] An error occurred: {e}")
