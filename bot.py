import discord
import requests
import re
from discord.ext import commands

TOKEN = 'YOURTOKEN'
speaker = 3

# 接続に必要なオブジェクトを生成
client = discord.Client(intents=discord.Intents.all())
intents = discord.Intents.all()
voice_client = None
intents.voice_states = True
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

# 起動時に動作する処理
@client.event
async def on_ready():
    print('起動完了')

# menuボタンUIの生成
class vcView(discord.ui.View): 
    def __init__(self, author, timeout=180): 
        super().__init__(timeout=timeout)
        self.author = author
    
    # 接続ボタン
    @discord.ui.button(label="接続", style=discord.ButtonStyle.success)
    async def ok(self, interaction: discord.Interaction, button: discord.ui.Button):
        global voice_client
        vcuser = self.author
        if not vcuser.voice:
            await interaction.response.send_message("ボイスチャンネルに接続していません。",ephemeral=True)
            return
        await interaction.response.send_message("接続しました。\n話者はずんだもんに初期化されます。",ephemeral=True)
        global speaker  
        speaker = 3
        voice_channel = vcuser.voice.channel
        voice_client = await voice_channel.connect()
        
    # 切断ボタン
    @discord.ui.button(label="切断", style=discord.ButtonStyle.danger)
    async def ng(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("切断処理を行います。",ephemeral=True)
        await voice_client.disconnect()  

    @discord.ui.button(label="VC設定", style=discord.ButtonStyle.blurple)
    async def option(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = speakerView(timeout=None)
        await interaction.response.send_message(view=view)

    @discord.ui.button(label="仕様", style=discord.ButtonStyle.blurple)
    async def ref(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("接続は/joinを実行した人がVCに接続している必要があります。\nVC設定で話者を変更できます。話者は個別設定できず、起動時にずんだもんに初期化されます。/voiceでも呼び出せます。\n「/」や「!」で始まる各種コマンド・メンション・URLは読み上げません。\n各ボタンを連続して実行するとエラーになる場合があります。時間を置いて再度実行してください。\nVOICEVOX低速版を使用しているため音声合成まで時間がかかることがあります。",ephemeral=True)    




# 話者変更ボタンUIの生成    
class speakerView(discord.ui.View): 
    def __init__(self, timeout=180): 
            super().__init__(timeout=timeout)

    @discord.ui.button(label="ずんだ", style=discord.ButtonStyle.blurple)
    async def zunda(self, interaction: discord.Interaction, button: discord.ui.Button):
        global speaker  
        speaker = 3
        await interaction.response.send_message("ずんだもんに変更しました") 

    @discord.ui.button(label="めたん", style=discord.ButtonStyle.blurple)
    async def metan(self, interaction: discord.Interaction, button: discord.ui.Button):
        global speaker  
        speaker = 2
        await interaction.response.send_message("四国めたんに変更しました") 

    @discord.ui.button(label="つむぎ", style=discord.ButtonStyle.blurple)
    async def tumugi(self, interaction: discord.Interaction, button: discord.ui.Button):
        global speaker  
        speaker = 8
        await interaction.response.send_message("春日部つむぎに変更しました")

    @discord.ui.button(label="はう", style=discord.ButtonStyle.blurple)
    async def hau(self, interaction: discord.Interaction, button: discord.ui.Button):
        global speaker  
        speaker = 10
        await interaction.response.send_message("雨晴はうに変更しました")   

    @discord.ui.button(label="ひまり", style=discord.ButtonStyle.blurple)
    async def himari(self, interaction: discord.Interaction, button: discord.ui.Button):
        global speaker  
        speaker = 14
        await interaction.response.send_message("冥鳴ひまりに変更しました") 

    @discord.ui.button(label="うさぎ", style=discord.ButtonStyle.blurple)
    async def usagi(self, interaction: discord.Interaction, button: discord.ui.Button):
        global speaker  
        speaker = 61
        await interaction.response.send_message("中国うさぎに変更しました")     

    @discord.ui.button(label="その他", style=discord.ButtonStyle.gray)
    async def ex(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("/id=(話者ID)で自由に音声を変えられます。VOICEVOX公式を参照してください。",ephemeral=True)              

# 誰も居なくなると自動切断
@client.event
async def on_voice_state_update(member, before, after):
    if before.channel and not after.channel and len(before.channel.members) == 1:
        await member.guild.voice_client.disconnect()    

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):

    # グローバル変数
    global speaker  

    # 絵文字パターン判定
    emoji = r"\<:[^:]+:[0-9]+\>"

    # wavファイルurl判定パターン
    wavpat = r'"wavDownloadUrl":"(.*?)","mp3Do'

    # jsonファイルurl判定パターン
    jsonpat = r'audioStatusUrl":"(.*?)","wav'

    # 音声合成ステータス判定パターン
    statepat = r'Ready":(.*?),"isAudioError'

    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return

    elif message.content == "/join":
        view = vcView(message.author)
        await message.channel.send(view=view)
        return
    
    elif message.content == "/voice":
        view = speakerView(timeout=None)
        await message.channel.send(view=view)
        return
    
    elif message.content.startswith("/id="):
        vcid = message.content.replace('/id=','')
        speaker = (str(vcid))
        await message.channel.send(f'話者IDを{vcid}に設定します。数値以外を入力した場合は反映されません。')
        return
    
    # botがボイスチャンネルに接続していないときは返す
    elif message.author.voice is None:
        return
    
    # URLとコマンドは返す
    elif message.content.startswith("http"):
        return
    elif message.content.startswith("/"):
        return
    elif message.content.startswith("@"):
        return
    elif message.content.startswith("!"):
        return
    elif message.content.startswith("?"):
        return
    elif message.content.startswith("$"):
        return
    elif message.content.startswith("%"):
        return
    
    # テキストを変数として設定
    vctx = str(re.sub(emoji,"",message.content))

    # リクエスト送信
    response1 = requests.get(f'https://api.tts.quest/v3/voicevox/synthesis?text={vctx}&speaker={str(speaker)}')

    # レスポンスからwavファイル取得urlを抽出
    match = re.search(wavpat,response1.text)
    dlurl = match.group(1)

    # レスポンスから音声合成ステータスurlを抽出
    jsonmatch = re.search(jsonpat,response1.text)
    jsonurl = jsonmatch.group(1)

    # 取得したJsonファイルから音声合成ステータスの判定を繰り返す
    total = 1
    while total < 100:

        response2 = requests.get(jsonurl.replace("\\", ""))
        statematch = re.search(statepat,response2.text)
        state = statematch.group(1)

        if state == ('false'):
            print('再試行回数=' + str(total))
            total += 1   

        if state == ('true'):
            print('合成成功')
            break

    # wavファイルを取得
    response3 = requests.get(dlurl.replace("\\", ""))
    with open("yomiage.wav","wb") as file:
        file.write(response3.content)
        
    # 取得したwavファイルを再生する
    message.guild.voice_client.play(discord.FFmpegPCMAudio("yomiage.wav"))
    return

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)