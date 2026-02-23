#### 如何将文字/文件推送到 Telegram

## 了解需求

为什么我们需要此功能？

我们可能在开发一个项目，并且创建了一个 Telegram 频道，用于存放 CI 版本

但是，我们不可能每构建出一个 CI 版本，就手动往 Telegram 频道发，这是个耗时又枯燥的过程

现在，大部分项目都向 github 托管代码，并创建 Github Actions 来自动构建项目，这让我们的目的有了实现的可能

## 原理

现在主流的方式就是使用一个 python 脚本（需要 telethon 库），它可以与 Telegram 频道中的 bot 通信，让脚本以 bot 的身份发布信息

每当我们推送代码到 github，github 就会运行一个 workflow（前提是你配置了 workflow）中。在这个 workflow 中，我们可以设置一个步骤，让它执行推送脚本，等执行完成，频道中就会出现信息啦

## 实现

这个脚本至少需要五个环境变量，它们是: 

- `BOT_TOKEN` 这是 bot 的访问令牌。

- `BOT_SESSION` 这是 bot 的会话字符串，用于登录

- `API_ID` Telegram API的认证凭证

- `API_HASH` Telegram API的认证凭证

- `CHAT_ID` 频道的 ID

- `MESSAGE_THREAD_ID`（可选）如果你的群组启用了话题功能，那还需要指定话题 ID

1.创建 Telegram 频道/群组。打开 Telegram 客户端，点击右上角的三条横杠，再点击 Contacts，继续点击 New Group / New Channel（群组/频道），填信息，然后点右上角的对钩

2.创建 Telegram Bot 。与 @BotFather 聊天（这是专门用来创建 Telegram Bot 的机器人），发送 /newbot，然后发送 bot 的名称、用户名。然后 BotFather 就会发给你 BOT_TOKEN 啦。将你的机器人拉进你的频道，然后设置为管理员

> 不要向它人发送你的 BOT_TOKEN！

3.获取 BOT_SESSION。复制一下 python 代码，然后保存为 getsession.py，将 “token”替换为你获取的 BOT_TOKEN

```python
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# 替换为你的信息
BOT_TOKEN = "token"  # 从 @BotFather 获取
API_ID = 611335
API_HASH = "d524b414d21f4d37f08684c1df41ac9c"

def get_bot_session():
    with TelegramClient(
        session=StringSession(),
        api_id=API_ID,
        api_hash=API_HASH
    ) as client:
        client.start(bot_token=BOT_TOKEN)
        
        session_str = client.session.save()
        print(session_str)
        return session_str

if __name__ == "__main__":
    get_bot_session()
```

首先安装一下 telethon

```shell
pip3 install telethon
```

然后执行 getsession.py

```shell
python3 getsession.py
```

它会让你输入 BOT_TOKEN，复制粘贴就行

然后你就获得 BOT_SESSION 了

4.关于 API_ID 和 API_HASH。直接使用 KernelSU 使用的就行了

API_ID : `611335`

API_HASH : `d524b414d21f4d37f08684c1df41ac9c`

5.获取 CHAT_ID。访问此链接，里面有（替换你的 BOT_TOKEN 和频道用户名）

```
https://api.telegram.org/bot<你的BOT_TOKEN>/getChat?chat_id=@频道用户名
```

"id": 后面的就是（频道的 id 一般是负数）

6.（可选）打开话题，点击任意消息，选择"复制链接"，链接格式：https://t.me/c/2496139642/5593/397983 。其中，5593 就是话题ID

7.写 python 脚本

（太多了放[这里](bot.py)）

其中，BOT_TOKE 和 NCHAT_ID通过环境变量来获取，因为它们是敏感/变化信息，不推荐硬编码

BOT_SESSION 在这由程序读取，同样需要通过环境变量来获取

```python
session_dir = os.path.join(script_dir, "bot")
```

8.配置 github secrets。此功能用于保存一些敏感信息，避免泄露。

打开你的 github 仓库，点击 Settings，再点 Secrets and variables，然后点 Actions，继续点 Repository secrets 右边的 New repository secret，填名字和内容。

需要的 Secrets 是 BOT_TOKEN，BOT_SESSION，CHAT_ID。如果启用话题功能，还需添加 MESSAGE_THREAD_ID

9.配置 github actions

```yaml
      - name: Upload to telegram
        if: github.event_name != 'pull_request' # 如果是 pr 的话不运行
        env:
          BOT_TOKEN: ${{ secrets.BOT_TOKEN }}
          BOT_SESSION: ${{ secrets.BOT_SESSION }}
          CHAT_ID: ${{ secrets.CHAT_ID }}
          # 如果启用话题功能，这里添加 MESSAGE_THREAD_ID:  ${{ secrets.MESSAGE_THREAD_ID }}
          COMMIT_MESSAGE: ${{ github.event.head_commit.message }} # 此次 commit 的信息
          COMMIT_URL: ${{ github.event.head_commit.url }} # commit 的链接
          RUN_URL: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }} # workflow 的链接
          COMMIT_AUTHOR: ${{ github.event.head_commit.author.name }} # commit 的作者
          BRANCH: ${{ github.ref_name }} # commit 所属的分支
        run: |
            if [ ! -z "${{ secrets.BOT_TOKEN }}" ]; then # 只有当 BOT_TOKEN 在 Secrets 中配置了才运行（对分支不需要此功能的友好）
              pip3 install telethon
              python3 $GITHUB_WORKSPACE/scripts/bot.py file.txt # 参数填需要上传的文件
            fi
```

最后运行工作流，即可正常使用
