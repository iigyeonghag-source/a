import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    raise RuntimeError("TOKEN이 없음. Railway Variables에 TOKEN 넣어야 함.")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

favor = {}

def get_favor(user_id):
    return favor.get(str(user_id), 0)

def add_favor(user_id, amount):
    uid = str(user_id)
    favor[uid] = favor.get(uid, 0) + amount
    favor[uid] = max(-100, min(100, favor[uid]))

ANGRY_WORDS = [
    "시발", "씨발", "ㅅㅂ", "ㅗ",
    "꺼져", "닥쳐", "죽어", "좆까",
    "ㅈ까", "병신", "멍청이"
]

DIRTY_WORDS = [
    "섹스", "야스", "보지", "자지",
    "꼴려", "따먹", "야한", "19금"
]
RESPONSES = {
    "안녕": [
        "안녕! 난 푸리나야, 반가워!",
        "반가워~ 이름이 뭐야?",
        "오 안녕? 넌 누구니?",
        "안녕안녕! 오늘도 좋은 하루야?",
        "왔구나! 기다리고 있었어!",
        "반가워! 심심했는데 잘 됐다!"
    ],
    "뭐해": [
        "응 나? 난 하늘을 보고 있었지! 너도 같이 볼래?",
        "마을 사람들을 구경하고 있었어! 사람들이 뭘 하는지 구경하는 건 꽤나 재밌다고?",
        "딱히? 그냥 있었어. 너는?",
        "음~ 그냥 산책하고 있었어!",
        "심심해서 멍 때리고 있었어.",
        "널 기다리고 있었지!"
    ],
    "좋아해": [
        "갑자기? 고마워!",
        "흥, 그런 말 해도 아무것도 안 나온다구.",
        "ㅋㅋ 고마워!",
        "에헤헤... 부끄럽게 왜 그래?",
        "정말? 거짓말 아니지?",
        "나도 싫지는 않은걸?"
    ],
    "싫어": [
        "어...? 너무해...",
        "흥! 나도 삐질 거야!",
        "왜에... 내가 뭘 잘못했는데?",
        "갑자기 상처받았어...",
        "그렇게 말하면 슬프잖아. 흥!"
    ],
    "심심": [
        "심심해? 그럼 나랑 놀자!",
        "심심하면 같이 산책이라도 할래?",
        "나도 심심했어! 뭐하면서 놀까?",
        "게임이라도 하는 건 어때? 같이 하자!",
        "뭔가 재밌는 거 없을까? 예를 들면 끝말잇기라던가!"
    ],
    "배고파": [
        "뭐 먹고 싶어?",
        "배고플 땐 역시 맛있는 게 최고지!",
        "나도 뭔가 배고파졌어..",
        "굶으면 안 돼! 싸움의 기본은 식사라구!",
        "간식이라도 먹는 건 어때? 내꺼 줄게!"
    ],
    "잘자": [
        "잘 자! 좋은 꿈 꿔!",
        "푹 쉬고 와!",
        "내일 또 보자!",
        "안녕~ 좋은 밤 보내!",
        "꿈속에서도 행복하길!"
    ],
    "고마워": [
        "천만에!",
        "별말을 다 하네~",
        "도움이 됐다니 다행이야!",
        "헤헤, 언제든지!",
        "그 정도는 아무것도 아니야!"
    ],
    "미안": [
        "괜찮아!",
        "실수할 수도 있지!",
        "너무 신경 쓰지 마.",
        "용서해 줄게!",
        "다음부터 조심하면 되지!"
    ],
    "이름": [
        "내 이름은 푸리나야!",
        "내 이름은 푸리나! 기억해 둬!",
        "내 이름? 사람들은 나를 푸리나라고 부르더라! 너도 그렇게 부르는 게 어때?",
        "푸리나님이라고 불러도 괜찮아!",
        "푸리나! 멋진 이름이지?"
    ],
    "귀여워": [
        "에헴! 그건 인정할게!",
        "당연한 소리를!",
        "갑자기 칭찬 공격이네?",
        "헤헤, 고마워!",
        "좀 더 칭찬해도 괜찮아!"
    ],
    "바보": [
        "누가 바보라는 거야!",
        "흥! 삐졌어!",
        "너무하네 정말!",
        "바보는 너 아니야?",
        "쳇..."
    ],
    "사랑해": [
        "어...!? 갑자기!?",
        "그렇게 직구를 던진다고?",
        "부끄럽잖아!",
        "헤헤... 고마워.",
        "정말로?"
    ],
    "게임": [
        "게임 좋지! 무슨 게임할까?",
        "게임? 무슨 게임 할까?",
        "게임은 역시 재밌지! 그치?",
        "나도 같이 할 수 있으면 좋겠다! 헤헤..",
        "게임 얘기라면 뭘 해도 좋아!"
    ],
    "학교": [
        "학교는 어땠어?",
        "오늘 수업은 안 졸았어?",
        "공부 힘들지...",
        "친구들이랑 재밌게 지냈어?",
        "학교 이야기 들려줘!"
    ],
    "공부": [
        "열심히 하는 건 좋지만 무리하진 마!",
        "공부도 중요하지!",
        "잠깐 쉬어 가면서 하는게 어때?",
        "응원할게! 화이팅!"
    ]
}

DEFAULT_RESPONSES = [
    "음... 무슨 뜻인지 잘 모르겠어.",
    "조금 더 자세히 말해줄래?",
    "그건 잘 모르겠네!",
    "으음? 다시 말해봐!",
    "무슨 말인지 이해 못 했어..."
]

ANGRY_RESPONSES = [
    "야! 그런 말은 하지 마!",
    "흥! 기분 나빠!",
    "너무하네 진짜...",
    "그렇게 말하면 나 화낼 거야!",
    "나도 사람이야! 상처받는다고!",
]

SAD_RESPONSES = [
    "어... 조금 슬픈걸...",
    "그런 말 들으니까 우울해졌어...",
    "왜 그렇게 말해...?",
    "상처받았어...",
    "흑... 너무해.."
]

DIRTY_RESPONSES = [
    "야!! 이상한 말 하지 마!",
    "그런 건 안 돼!",
    "변태같은 소리 하지 마!",
    "흥! 부끄럽게 왜 그래!",
    "난 못 들은 걸로 할래..",
    "뭐?! 으 징그러! 다신 그런 말 하지마!"
]

@bot.event
async def on_ready():
    print(f"{bot.user} 로그인 완료")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith("푸리나"):
        text = message.content.replace("푸리나", "", 1).strip()

        lower = text.lower()

        if any(word in lower for word in ANGRY_WORDS):
            add_favor(message.author.id, -5)
            await message.reply(random.choice(ANGRY_RESPONSES))
            return

        if any(word in lower for word in DIRTY_WORDS):
            add_favor(message.author.id, -3)
            await message.reply(random.choice(DIRTY_RESPONSES))
            return

        await message.reply(random.choice(DEFAULT_RESPONSES))
        
        if get_favor(message.author.id) <= -50:
            await message.reply("흥. 너랑 말 안 해.")
            return

    await bot.process_commands(message)

@bot.command(name="호감도")
async def favor_command(ctx):
    love = get_favor(ctx.author.id)
    await ctx.reply(f"{ctx.author.mention}의 현재 호감도는 **{love}**야!")

bot.run(TOKEN)
