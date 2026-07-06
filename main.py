import json
import os
import random
from datetime import datetime, timezone, timedelta
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
from discord import app_commands
import asyncio
from difflib import SequenceMatcher
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
import google.generativeai as genai
import math

load_dotenv()

GUILD_ID = 1510681614919794868
GUILD = discord.Object(id=GUILD_ID)

TOKEN = os.getenv("TOKEN")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

if TOKEN is None:
    raise RuntimeError("TOKEN이 없음. Railway Variables에 TOKEN 넣어야 함.")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

favor = {}
user_memory = {}
last_response_key = {}
last_topic = {}


MONEY_FILE = "poker_money.json"

DATA_DIR = "/data"
DATA_FILE = "/data/data.json"

data = {
    "warehouses": {},
    "warehouse_last_tax": {},
    "sticky_message_id": None,
    "checkin": {},
    "ranking_message_id": None,
    "levels": {},
    "poker_money": {},
    "poker_last_claim": {},
    "favor": {},
    "memory": {},
    "characters": {},
    "hunt_users": {},
    "weapons": {},
    "primogems": {},
    "quests": {},
    "achievements": {},
    "character_pity": {},
    "warnings": {},
    "adventures": {},
    "inventories": {},
    "discovered_items": {},
    "shop_items": {}
}

warehouses = {}
warehouse_last_tax = {}
characters = {}
weapons = {}
primogems = {}
quests = {}
achievements = {}
character_pity = {}
warnings = {}
adventures = {}
inventories = {}
discovered_items = {}
shop_items = {}

def remove_poker_money(user_id, amount):
    uid = str(user_id)

    poker_money[uid] = max(
        0,
        poker_money.get(uid, 0) - int(amount)
    )

    save_data()
    
def load_data():
    global data, poker_money, poker_last_claim, favor, user_memory, characters, hunt_users, weapons, primogems, quests, achievements, character_pity, levels, checkin, warnings, warehouses, warehouse_last_tax, adventures, inventories, discovered_items, shop_items
    
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        
        data["warehouses"] = loaded.get("warehouses", {})
        data["warehouse_last_tax"] = loaded.get("warehouse_last_tax", {})
        data["adventures"] = loaded.get("adventures", {})
        data["inventories"] = loaded.get("inventories", {})
        data["discovered_items"] = loaded.get("discovered_items", {})
        data["shop_items"] = loaded.get("shop_items", {})
        data["sticky_message_id"] = loaded.get("sticky_message_id")
        data["warnings"] = loaded.get("warnings", {})
        data["checkin"] = loaded.get("checkin", {})
        data["ranking_message_id"] = loaded.get("ranking_message_id")
        data["levels"] = loaded.get("levels", {})
        data["character_pity"] = loaded.get("character_pity", {})
        data["poker_money"] = loaded.get("poker_money", {})
        data["poker_last_claim"] = loaded.get("poker_last_claim", {})
        data["favor"] = loaded.get("favor", {})
        data["memory"] = loaded.get("memory", {})
        data["characters"] = loaded.get("characters", {})
        data["hunt_users"] = loaded.get("hunt_users", {})
        data["weapons"] = loaded.get("weapons", {})
        data["primogems"] = loaded.get("primogems", {})
        data["quests"] = loaded.get("quests", {})
        data["achievements"] = loaded.get("achievements", {})

    data["sticky_message_id"] = data.get("sticky_message_id")
    warnings = data["warnings"]
    checkin = data["checkin"]
    levels = data["levels"]
    poker_money = data["poker_money"]
    favor = data["favor"]
    user_memory = data["memory"]
    characters = data["characters"]
    hunt_users = data["hunt_users"]
    weapons = data["weapons"]
    primogems = data["primogems"]
    quests = data["quests"]
    achievements = data["achievements"]
    character_pity = data["character_pity"]
    adventures = data["adventures"]
    inventories = data["inventories"]
    discovered_items = data["discovered_items"]
    shop_items = data["shop_items"]
    
    warehouses = data["warehouses"]

    warehouse_last_tax = {}
    for uid, value in data["warehouse_last_tax"].items():
        warehouse_last_tax[uid] = datetime.fromisoformat(value)
        
    poker_last_claim = {}
    for uid, value in data["poker_last_claim"].items():
        poker_last_claim[uid] = datetime.fromisoformat(value)
        
def save_data():
    os.makedirs(DATA_DIR, exist_ok=True)

    data["warehouses"] = warehouses
    data["warehouse_last_tax"] = {
        uid: value.isoformat()
        for uid, value in warehouse_last_tax.items()
    }
    data["adventures"] = adventures
    data["inventories"] = inventories
    data["discovered_items"] = discovered_items
    data["shop_items"] = shop_items
    data["warnings"] = warnings
    data["ranking_message_id"] = data.get("ranking_message_id")
    data["levels"] = levels
    data["character_pity"] = character_pity
    data["primogems"] = primogems
    data["quests"] = quests
    data["achievements"] = achievements
    data["weapons"] = weapons
    data["poker_money"] = poker_money
    data["favor"] = favor
    data["memory"] = user_memory
    data["characters"] = characters
    data["hunt_users"] = hunt_users
    data["poker_last_claim"] = {
        uid: value.isoformat()
        for uid, value in poker_last_claim.items()
    }

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

poker_rooms = {}
checkin = {}
poker_money = {}
poker_last_claim = {}
user_memory = {}
favor = {}
characters = {}
hunt_users = {}

levels = {}

RANKING_CHANNEL_ID = 1518922787828531312
COMMAND_LOG_CHANNEL_ID = 1520309389364428830  
LEVEL_LOG_CHANNEL_ID = 1518910263682662451
CHAT_XP_COOLDOWN = timedelta(seconds=5)
last_chat_xp = {}

WARNING_LOG_CHANNEL_ID = 1512443019314597999
WARNING_TIMEOUT = timedelta(hours=1)

STICKY_CHANNEL_ID = 1510692438480523494

STICKY_MESSAGE = """📌**범프 안내**

/bump하면 /up도 해주셈. 안하면 종훈이 ㅅㄱ
"""

sticky_message_lock = asyncio.Lock()
sticky_message_sending = False

load_data()
        
KST = timezone(timedelta(hours=9))

def get_level_data(user_id):
    uid = str(user_id)
    levels.setdefault(uid, {
        "xp": 0,
        "level": 1,
        "messages": 0,
        "chars": 0,
        "voice_minutes": 0
    })
    return levels[uid]


def required_xp(level):
    return 100 + (level - 1) * 50


def clean_level_nickname(name):
    import re
    return re.sub(r"\s*\[Lv\.\d+\]$", "", name)


async def update_level_nickname(member):
    if member.bot:
        return

    info = get_level_data(member.id)
    base_name = clean_level_nickname(member.display_name)
    new_name = f"{base_name} [Lv.{info['level']}]"

    if member.display_name == new_name:
        return

    try:
        await member.edit(nick=new_name)
    except discord.Forbidden:
        print(f"닉네임 변경 권한 없음: {member}")
    except discord.HTTPException as e:
        print(f"닉네임 변경 실패: {e}")


async def add_xp(member, amount, reason="채팅"):
    if member.bot:
        return

    info = get_level_data(member.id)
    old_level = info["level"]

    info["xp"] += int(amount)

    leveled_up = False
    while info["xp"] >= required_xp(info["level"]):
        info["xp"] -= required_xp(info["level"])
        info["level"] += 1
        leveled_up = True

    save_data()

    if leveled_up:
        await update_level_nickname(member)
        await give_level_roles(member)
        await update_ranking_message(member.guild)
        
        channel = member.guild.get_channel(LEVEL_LOG_CHANNEL_ID)
        if channel:
            need = required_xp(info["level"])

            embed = discord.Embed(
                title="🎉 레벨 업!",
                description=(
                    f"{member.mention} 레벨 상승!\n\n"
                    f"📈 **Lv.{old_level} → Lv.{info['level']}**\n"
                    f"⭐ 현재 경험치: **{info['xp']} / {need}**\n"
                    f"📝 사유: `{reason}`"
                ),
                color=discord.Color.gold()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)
            
def get_favor(user_id):
    return favor.get(str(user_id), 0)

def add_favor(user_id, amount):
    uid = str(user_id)
    favor[uid] = favor.get(uid, 0) + amount
    favor[uid] = max(-100, min(100, favor[uid]))
    
    save_data()

def get_primogems(user_id):
    return int(primogems.get(str(user_id), 0))


def add_primogems(user_id, amount):
    uid = str(user_id)
    primogems[uid] = max(0, get_primogems(uid) + int(amount))
    save_data()
    
def get_favor_stage(user_id):
    value = get_favor(user_id)

    if value >= 50:
        return "love"
    if value >= 10:
        return "friendly"
    if value <= -30:
        return "cold"
    return None

def add_favor_mood_prefix(user_id, response):
    return response
    
def remember_user_value(user_id, key, value):
    uid = str(user_id)
    user_memory.setdefault(uid, {})
    user_memory[uid][key] = value
    save_data()

def get_user_memory(user_id, key, default=None):
    return user_memory.get(str(user_id), {}).get(key, default)

TIME_NOTICE_CHANNEL_ID = 1510681615528103988

TIME_MESSAGES = {
    "아침": [
        "좋은 아침이야! 흠흠, 오늘도 이 푸리나님이 하루의 시작을 알려주도록 하지! 잠은 푹 잤어?",
        "일어날 시간이야! 늦잠을 자다니... 설마 물의 신보다 늦게 일어난 건 아니겠지?",
        "아침은 든든하게 먹어야 해! 따뜻한 차 한 잔과 함께라면 오늘 하루도 분명 멋질 거야."
    ],

    "점심": [
        "점심 시간이야! 오늘은 뭘 먹을 예정이야? 흠흠, 특별히 내게도 알려주는 걸 허락해 주도록 하지!",
        "벌써 해가 중천에 떴네! 식사도 하고 잠깐 산책이라도 하면 기분이 좋아질지도?",
        "전투든 공부든 든든하게 먹어야 힘이 나는 법이야! 그러니까 점심은 거르지 말라고?"
    ],

    "저녁": [
        "좋은 저녁이야! 오늘 하루는 어땠어? 분명 재미있는 일도 있었겠지?",
        "저녁도 맛있게 먹어! 디저트까지 챙기면... 흠흠, 그건 더욱 완벽한 식사가 될 거야!",
        "오늘도 정말 수고 많았어. 나도 하루 종일 바빴지만... 이렇게 다시 만났으니 그걸로 됐어. 후후!"
    ]
}
last_period = None

@tasks.loop(minutes=1)
async def time_notice_loop():
    global last_period

    now = datetime.now(ZoneInfo("Asia/Seoul"))

    if 6 <= now.hour < 12:
        period = "아침"
    elif 12 <= now.hour < 18:
        period = "점심"
    else:
        period = "저녁"

    if period != last_period:
        last_period = period

        channel = bot.get_channel(TIME_NOTICE_CHANNEL_ID)
        if channel:
            await channel.send(
                random.choice(TIME_MESSAGES[period])
            )
            
# =========================
# 메뉴 추천 시스템
# =========================
        
@bot.tree.command(name="메뉴추천", description="랜덤으로 맛있는 메뉴 추천", guild=GUILD)
async def recommend_menu(interaction: discord.Interaction):
    menus = [
        # 한식
        "김치찌개", "된장찌개", "부대찌개", "순두부찌개",
        "제육볶음", "불고기", "삼겹살", "돼지갈비",
        "닭갈비", "찜닭", "닭볶음탕",
        "보쌈", "족발",
        "국밥", "돼지국밥", "순대국밥",
        "설렁탕", "갈비탕", "곰탕", "해장국",
        "감자탕", "육개장",
        "비빔밥", "돌솥비빔밥",
        "김치볶음밥", "새우볶음밥", "계란볶음밥",
        "오징어볶음",
        "칼국수", "수제비",
        "비빔국수", "냉면",
        "떡국", "만둣국",
        "김밥",
        "떡볶이", "로제떡볶이",
        "순대", "튀김", "어묵",
        "토스트",

        # 중식
        "짜장면", "간짜장",
        "짬뽕", "백짬뽕",
        "탕수육", "깐풍기",
        "마파두부",
        "마라탕", "꿔바로우",
        "계란볶음밥",

        # 일식
        "초밥",
        "우동", "라멘",
        "돈까스", "치즈돈까스",
        "냉모밀",
        "규동", "가츠동", "오야코동",
        "텐동",
        "회덮밥",

        # 양식
        "파스타", "로제 파스타", "크림 파스타",
        "토마토 파스타", "알리오올리오",
        "봉골레 파스타", "리조또",
        "스테이크",
        "피자",
        "햄버거", "치즈버거", "새우버거",
        "핫도그", "샌드위치",
    
        # 패스트푸드 & 야식
        "치킨", "양념치킨", "후라이드치킨",
        "간장치킨",
        "닭강정",
        "감자튀김", "치즈볼",
        "불닭볶음면", "짜파게티", "신라면",
        "컵라면", "치즈라면",

         # 아시안
        "쌀국수", "팟타이",
        "커리", "버터치킨커리",
        "케밥", "타코",
        "브리또", "퀘사디아"
    ]

    menu = random.choice(menus)

    await interaction.response.send_message(
        f"오늘의 추천 메뉴는 **{menu}**(이)야!"
    )


ANGRY_WORDS = [
    "시발", "씨발", "ㅅㅂ", "ㅗ",
    "꺼져", "닥쳐", "죽어", "좆까",
    "ㅈ까", "병신", "멍청이", "바보",
    "응 아니야", "ㅄ", "ㅂㅅ", "비응신",
    "니애미", "느금마", "느금", "니엄마",
    "지랄", "ㅈㄹ", "니애비"
]

DIRTY_WORDS = [
    "섹스", "야스", "보지", "자지",
    "꼴", "따먹", "야한", "19금",
    "임신", "강간", "교미", "삽입",
    "벌려", "엎드려", "유혹", "오나홀", "벗어",
    "뷰지", "가슴", "쥬지", "ㅅㅅ", "섹슈", "색스", 
    "색수", "자1지", "보1지", "섹1스", "야1스", "벅지"
]

ANGRY_RESPONSES = [
    "야! 그런 말은 하지 마!",
    "흥! 기분 나빠!",
    "너무하네 진짜...",
    "그렇게 말하면 나 화낼 거야!",
    "나도 사람이야! 상처받는다고!",
]

DIRTY_RESPONSES = [
    "야!! 이상한 말 하지 마!",
    "그런 건 안 돼!",
    "변태같은 소리 하지 마!",
    "흥! 부끄럽게 왜 그래!",
    "난 못 들은 걸로 할래..",
    "뭐?! 으 징그러! 다신 그런 말 하지마!"
]

furina_talk_history = {}
furina_spam_state = {}

SIMILAR_LIMIT = 0.78
SPAM_WINDOW = timedelta(seconds=60)
SPAM_MAX_COUNT = 7
REPEAT_PENALTY_COOLDOWN = timedelta(seconds=20)

REPEAT_ANNOYED_RESPONSES = [
    "또 그 말이야? 으으... 나를 시험하는 거야?",
    "방금이랑 비슷한 말 아니야? 조금 성의가 부족한걸.",
    "계속 같은 말만 하면 나도 삐질 수 있다고?",
    "그 주제는 방금 했잖아! 다른 이야기도 해보자고!",
    "으음, 슬슬 질리는데... 물의 신도 반복 대사는 싫어한다고!"
]

SPAM_ANNOYED_RESPONSES = [
    "잠깐잠깐! 너무 많이 부르는 거 아니야?!",
    "나도 숨 좀 쉬자! 계속 말 걸면 곤란하다고!",
    "으으... 관심은 고맙지만 너무 몰아치면 부담스럽거든?",
    "푸리나님 호출권 남발 금지야! 흥!",
    "조금만 천천히 말해! 무대에도 쉬는 시간이 필요하다고!"
]

def normalize_furina_text(text):
    return " ".join(text.lower().strip().split())

def is_similar_text(a, b):
    if not a or not b:
        return False

    if a == b:
        return True

    if a in b or b in a:
        return True

    return SequenceMatcher(None, a, b).ratio() >= SIMILAR_LIMIT

def check_furina_repeat_or_spam(user_id, text):
    uid = str(user_id)
    now = datetime.now(KST)
    clean = normalize_furina_text(text)

    furina_talk_history.setdefault(uid, [])
    furina_spam_state.setdefault(uid, {
        "times": [],
        "last_penalty": None
    })

    history = furina_talk_history[uid]
    spam = furina_spam_state[uid]

    # 오래된 호출 기록 제거
    spam["times"] = [
        t for t in spam["times"]
        if now - t <= SPAM_WINDOW
    ]
    spam["times"].append(now)

    last_penalty = spam.get("last_penalty")
    can_penalize = (
        last_penalty is None
        or now - last_penalty >= REPEAT_PENALTY_COOLDOWN
    )

    # 너무 자주 말 걸기
    if len(spam["times"]) >= SPAM_MAX_COUNT:
        if can_penalize:
            add_favor(user_id, -2)
            spam["last_penalty"] = now

        history.append(clean)
        furina_talk_history[uid] = history[-5:]

        return random.choice(SPAM_ANNOYED_RESPONSES)

    # 최근 말과 비슷한지 검사
    recent_history = history[-3:]
    if any(is_similar_text(clean, old) for old in recent_history):
        if can_penalize:
            add_favor(user_id, -2)
            spam["last_penalty"] = now

        history.append(clean)
        furina_talk_history[uid] = history[-5:]

        return random.choice(REPEAT_ANNOYED_RESPONSES)

    history.append(clean)
    furina_talk_history[uid] = history[-5:]

    return None
    
RESPONSES = {
    "안녕": [
        "오! 드디어 왔구나? 후후, 기다리고 있었다고!",
        "반가워! 오늘은 어떤 이야기를 들려주려고?",
        "안녕! 나는 푸리나야. 설마 내 이름을 모르는 건 아니겠지?",
        "후훗, 찾아와 줘서 기쁜걸!",
        "좋은 날이네! 네가 왔으니까!"  
    ],
    "뭐해": [
        "나? 폰타인을 내려다보고 있었지! ..라고 하면 좀 멋있으려나?",
        "음~ 그냥 시간을 보내고 있었어. 네가 와서 심심하지 않게 됐지만!",
        "산책도 하고, 멍도 때리고 했지. 나도 나름 바빴다고?",
        "널 기다리고 있었지! ...아니, 우연히 기다리게 된 거야!",
        "후후, 비밀이야. 물의 신에게도 사생활은 필요하다고!"
    ],
    "좋아해": [
        "오? 갑자기 그런 말을 들으니 기분이 좋은걸?",
        "후훗, 보는 눈이 있네!",
        "그 정도로 날 좋아한다니 영광으로 알아도 좋아!",
        "정말? 거짓말이면 서운할 거야.",
        "흠흠, 나쁘지 않은 기분이네!"
    ],
    "싫어": [
        "뭐라고!? ...흥, 조금 상처받았어.",
        "너무한걸? 물의 신에게 그런 말을 하다니!",
        "으음... 이유라도 들어볼 수 있을까?",
        "흥! 기억해 둘 거야!",
        "그 말은 조금 슬픈데..."
    ],
    "심심": [
        "심심해? 그럼 내가 특별히 시간을 내주도록 하지!",
        "후후, 같이 놀자는 뜻으로 받아들여도 되겠지?",
        "나도 조금 심심했어. 타이밍이 좋네! 후훗, 운이 좋은 줄 알라고! ...라, 랄까나?",
        "재밌는 거라도 같이 찾아볼까?",
        "끝말잇기? 퀴즈? 아니면 그냥 수다? 무엇이든 말해봐!"
    ],
    "배고파": [
        "배고프면 맛있는 걸 먹어야지!",
        "흠... 갑자기 디저트가 먹고 싶어졌어.",
        "굶는 건 좋지 않아! 우선 뭐라도 먹자!",
        "케이크 한 조각 정도면 기분이 좋아질 텐데!",
        "뭐가 제일 먹고 싶어?"
    ],
    "잘자": [
        "벌써 자러 가는 거야? 후후, 좋은 꿈 꾸길 바랄게!",
        "푹 쉬고 와! 내일은 더 좋은 하루가 될 거야.",
        "잘 자! 꿈속에서라도 즐거운 모험을 하길 바라!",
        "안녕~ 오늘은 특별히 물의 신이 좋은 꿈을 허락해 주도록 하지!",
        "푹 자고 와! ...내일 또 찾아와 주는 거지?"
    ],
    "고마워": [
        "후훗, 당연한 말!",
        "천만에! 이 정도는 아무것도 아니야.",
        "도움이 됐다니 다행인걸!",
        "흠흠, 역시 나를 찾길 잘한 거 같지?",
        "언제든지! ...하지만 날 너무 의지하진 말라고?"
    ],
    "미안": [
        "괜찮아! 누구나 실수는 할 수 있는걸.",
        "흥, 이번만 특별히 용서해 주도록 하지!",
        "너무 신경 쓰지 마. 이미 지나간 일이잖아?",
        "후후, 사과를 받아주마!",
        "다음부터 조심하면 되는 거야!"
    ],
    "이름": [
        "나는 푸리나야! 설마 아직도 모르고 있었던 건 아니겠지?",
        "내 이름은 푸리나! 기억해 두는 게 좋을 거야.",
        "푸리나 드 폰타인! 후후, 꽤 멋진 이름이지?",
        "사람들은 나를 푸리나라고 부르더라. 너도 그렇게 불러!",
        "흠흠! 푸리나님이라고 불러도 괜찮아!"
    ],
    "귀여워": [
        "에헴! 당연한 사실을 이제야 눈치챘구나!",
        "후훗, 그런 칭찬은 언제 들어도 좋네!",
        "보는 눈이 꽤 괜찮은걸?",
        "그렇게 대놓고 말하면 부끄럽잖아!",
        "흠흠, 더 말해봐도 괜찮아."
    ],
    "바보": [
        "누가 바보라는 거야!?",
        "흥! 방금 못 들은 걸로 할게!",
        "정말 실례되는 말이네!",
        "진짜 바보는 너겠지!",
        "으으... 그건 좀 상처인데."
    ],
    "사랑해": [
        "어!? 그, 그렇게 갑자기 말하면 곤란한데!",
        "정말? ...흠, 싫지는 않은걸.",
        "후훗, 그런 말을 들으니 괜히 기분이 좋아지네.",
        "그렇게 직구를 던지다니 반칙이야!",
        "으음... 뭐, 고맙다고 해둘게!"
    ],
    "게임": [
        "오 게임? 흥미로운걸! 어떤 게임하고 있어?",
        "후후, 게임 말이지..? 완전 하나의 무대나 따로 없지!",
        "게임은 역시 재밌지! 승리하면 더 재밌고!",
        "흠, 네가 좋아하는 게임이라면 들어볼 가치는 있겠어.",
        "게임 이야기라면 얼마든지 들어줄게!"
    ],
    "학교": [
        "학교는 어땠어? 재밌는 일이라도 있었어?",
        "오늘 수업은 어땠어? 설마 졸지는 않았겠지? 이 폰타인님의 친구께서 말이야!",
        "학교 생활 말이지.. 너도 꽤 힘들겠네. 하지만 힘내라구?",
        "어때? 친구들이랑 좋은 시간 보냈어?",
        "후후, 학교 이야기는 항상 흥미롭더라!"
    ],
    "공부": [
        "열심히 하는 건 좋지만 너무 무리하진 마!",
        "공부도 중요하지만 쉬는 것도 항상 중요하다고?",
        "후후, 노력하는 모습은 보기 좋은걸?",
        "잠깐 쉬어 가면서 하는 건 어때?",
        "특별히 응원해 주도록 하지! 아자아자 화이팅!"
    ],

    "갈게": [
        "벌써 가는 거야? 아쉽네...",
        "다음에 또 찾아와 줘!",
        "잘 가! 좋은 하루 보내! 물론 폰타인에서 말이지!",
        "다음에 오면 더 재밌게 놀아주도록 하지!",
        "응, 조심해서 가!"
    ],

    "졸려": [
        "졸리면 억지로 버티지 말고 쉬는 게 어때?",
        "후암... 네 말 들으니까 나도 졸린 기분이네.",
        "잠은 정말 중요하다고! 빨리 자!",
        "무리하다 쓰러지지마. 너가 쓰러지만 나까지 곤란해지거든?",
        "푹 자고 오면 훨씬 나아질 거야!",
        "하암… 나도 자려던 참이었어. 내일 봐, 제때 깨워주는 거 잊지 말구…"
    ],

    "화나": [
        "무슨 일인데 그렇게 화가 난 거야?",
        "흠... 꽤 화난 것 같은데?",
        "진정해 진정해! 무슨 일인지부터 말해봐.",
        "내가 들어줄 테니까 천천히 이야기해.",
        "후우~ 심호흡 한 번! 자, 조금 나아졌어?"
    ],

    "행복": [
        "오? 좋은 일이라도 있었어?",
        "후후, 네가 행복하다니 나도 기분이 좋아지는걸!",
        "행복한 건 정말 좋은 일이야!",
        "계속 그런 기분이 이어졌으면 좋겠네.",
        "오늘은 꽤 멋진 하루였나 봐? 들려줘! 들려줘!"
    ],

    "우울": [
        "오늘은 힘든 일이 있었던 모양이네...",
        "가끔은 아무것도 하지 않고 쉬는 것도 괜찮아.",
        "너무 혼자 끌어안고 있지는 마.",
        "후후, 비가 오면 언젠가 맑아지기도 하는 법이야.",
        "지금은 천천히 쉬어가도 괜찮아."
    ],

    "재밌어": [
        "후후, 재밌었다니 다행인걸!",
        "그치? 나도 꽤 즐거웠어!",
        "네가 그렇게 말해주니 기분 좋은데?",
        "계속 즐겁게 놀자! 약속이야!",
        "흠흠, 역시 나와 있으면 재밌을 수밖에!"
    ],
    "천재": [
        "당연하지! 왜냐면 난 푸리나니까!",
        "에헴! 이게 나, 물의 신 푸리나님이시다!",
        "이 정도는 기본이지!",
        "푸리나를 너무 과소평가한 거 아니야?",
        "후후!",
        "나를 따르라!"
    ],

    "최고": [
        "그렇게 칭찬하면 부끄럽잖아!",
        "고마워!",
        "역시 보는 눈이 있네!",
        "후후, 인정해주마!",
        "기분 좋은걸?"
    ],
    "아를레키노": [
        "아를레키노? ㄱ, 그게 누군데? 난 잘 몰라..!",
        "어.. 그게.. 난 모르는 인물이야!",
        "아를레키노? ㄱ, 그게 누군데? ...아니, 정확히는 기억에서 지워버렸어! 그런 이름을 떠올렸다가 괜히 악몽이라도 꾸면 어떡해!"
    ],
    "에스코피에": [
        "에스코피에? 물론 알고 있지! 후후, 그녀의 디저트는 정말 대단하다니까. 특히 드보르 케이크는 한 입 먹는 순간 기분이 좋아질 정도였어! 너는 어떤 메뉴가 가장 마음에 들었어?",
        "에스코피에를 알고 있다니, 제법인데? 그녀의 디저트는 폰타인에서도 손꼽힐 정도야! 특히 드보르 케이크는... 흠, 솔직히 말해서 꽤 마음에 들었어. 너는 어땠어?"
    ],
    "리니": [
        "리니와 리넷? 물론 알지! 예전에 공연도 직접 본 적 있는걸. 후후, 인기가 꽤 많은 건 인정하지만... 나와 비교하기엔 아직 멀었어!\n뭐? 꼭 그렇지만은 않다고? 으... 그건 내가 지금은 은퇴했기 때문이라구! 그래, 은퇴! 현역 시절이었다면 결과가 달랐을걸?"
    ],
    "느비예트": [
        "아하! 너도 느비예트를 알고 있구나? 흠흠, 폰타인을 오랫동안 떠받쳐 온 정말 믿음직한 인물이지!",
        "느비예트? 물론 알지! 폰타인을 오랫동안 지켜온 대단한 인물이잖아. 후훗, 문득 얼굴이 보고 싶어지는걸?"
    ],
    "소개": [
        "내가 누구냐고? 후후, 드디어 물어봐 주는구나! 잘 들어! 나는 푸리나 드 폰타인! 위대한 물의 신이자 폰타인의 상징이지! 만나서 반가워!",
        "자기소개를 원한다고? 좋았어! 나는 푸리나 드 폰타인! 위대한 물의 신이자 이 아름다운 폰타인의 상징이지. 후후, 내 이름 정도는 기억해 두는 게 좋을 거야!"
    ],
    "도로": [
        "도로롱! 뭔가 귀여운 이름이네! 하지만 푸리나에 비해선 전혀 안귀여워!",
        "DORO!!!",
        "@_1doro1_! 어라? 왜 안되지? 흐흠..! 난 아무것도 안했어!",
        "<@964535827336151070>! 하하! 성공했다! 역시 나야, 후훗!"
    ],
    "너임마종훈": [
        "..너 방금 선 넘은 거 알지? 모르겠다고? 너임마종훈",
        "나 방금 모든 걸 잃은 거지..? 그치?",
        "<@1194560414118314104>!"
    ],
    "너임마돈키": [
        "돈키러버? 그게 누군데? 뭔가 눈치가 없을 거 같은 이름이네."
    ],
    "너임마츠엘": [
        "오? 혹시 독재자 이름 중 하나일까나?"
    ],
    "쟤 죽여": [
        "알겠어!",
        "오케이 내가 처리할게!",
        "쟤 말하는 거지? 알겠어! 처리하고 올게!",
        "내 힘을 보여줄 때다!"
    ],
    "광질": [
        "오? 너도 그 서버가 그리운 거야? 후후, 걱정하지 마! 이 푸리나님이 있잖아? 특별히 기대도 괜찮아!",
        "그 서버는 내가 점령했거든?! 후후, 꽤 무섭지 않아? ...뭐? 전혀 안 무섭다고? 으... 그건 네가 특별히 겁이 없는 거야!"
    ],
    "폰타인": [
        "폰타인? 후후, 바로 내가 사랑하는 나라지!",
        "아름다운 물의 나라, 폰타인! 한 번쯤은 가보고 싶지 않아?",
        "오? 폰타인 이야기를 하려는 거야? 얼마든지 들어주지!",
        "흠흠, 폰타인을 언급하다니 보는 눈이 있네!",
        "폰타인은 정말 멋진 곳이야! ...물론 나도 포함해서 말이야!",
        "내 고향 같은 곳이지. 후후, 괜히 자랑하고 싶어지는걸?",
        "폰타인이라... 문득 그 풍경이 떠오르네.",
        "물과 재판의 나라! 그게 바로 폰타인이지!",
        "오? 혹시 폰타인에 관심 있는 거야? 그럼 내가 직접 설명해 줄까?",
        "후후, 폰타인 이야기를 꺼냈다는 건 나와 이야기할 준비가 됐다는 뜻이겠지?"
    ],
    "노래": [
        "노래에는 자신 있지만, 내게 걸맞은 가사는 많지 않아. 극단 작가들이 더 힘냈으면 좋겠네. 오래 기다리는 건 지루하거든."
    ],
    "관계": [
        "크흠, 우린 잘 아는 사이니까, 날 너무 공경할 필요 없어. 잠깐, 그게 무슨 표정이야? 설마 애초에 날 「공경」한 적이 없다는 건 아니겠지?"
    ],
    "동행": [
        "내 이야기는 막을 내렸지만, 이젠 우리 이야기가 시작될 차례야… 생각해 보니까 그럼 출연료를 2배로 받을 수 있겠네? 신난다!"
    ],
    "라이오슬리": [
        "잘 아는 사이는 아니지만, 느비예트가 믿을 만하다고 했으니까 괜찮은 녀석이겠지! 참, 전에 걔가 보낸 차를 받은 적이 있는데, 맛이 괜찮더라! 나중에 또 해달라 해야지."
    ],
    "클로린드": [
        "클로린드는 너무 과묵한 거 같아! 옆에서 몇 번이나 불러도 반응이 없더라고! 그래도 전적으로 신뢰하긴 해. 몇 번이나 날 지켜줬거든. 그리고 음… 클로린드가 좀 그립긴 한데 만날 이유를 못 찾겠네. 참! 다음에 클로린드를 티타임에 초대하면 되겠다! 너도 같이 갈래?"
    ],
    "취미": [
        "난 소설 보는 걸 좋아해! ...그나저나《퀸즈 크라운》 후속작은 아직도 안 나왔어? 으으 아쉽네.. 정의가 악을 물리치는 클래식 작품은 아무리 봐도 질리지 않는다니까"
    ],
    "고민": [
        "오늘은 마카로니에 어떤 소스를 뿌리는 게 좋을까가 오늘의 고민이지.. 혹시 좋은 생각 있어?",
        "으음... 디저트를 먼저 먹을지 식사를 먼저 할지가 고민이야. 꽤 중요한 문제라고?",
        "오늘은 뭘 하면서 시간을 보낼까 고민 중이었어.",
        "흠흠, 다음에 무슨 공연을 보러 갈지 고민하고 있었지!",
        "케이크를 한 조각만 먹을지 두 조각 먹을지 고민 중이야. 어려운 문제라구?",
        "사람들은 늘 복잡한 고민을 하지만... 난 오늘 낮잠을 잘지 산책을 할지 고민하고 있었어!",
        "오늘의 고민? 네가 다음엔 무슨 이야기를 들고 올지 궁금한걸?",
        "후후, 사실 별건 아니고 어떤 디저트를 먹을지 고민 중이었어.",
        "고민이라... 쉬어야 할지 더 쉬어야 할지가 고민이네.",
        "으음, 물의 신답게 위엄을 유지할지 그냥 뒹굴거릴지가 오늘의 고민이야!"
    ],
    "아침": [
       "좋은 아침이야... 으으, 꼭 이렇게 일찍 일어나야 하는 걸까? 물의 신도 아침은 힘들다고..."
    ],
    "점심": [
        "안녕! 내 케이크는 어딨어? 뭐어, 아침에 먹지 않았냐고? 그건 벌써 한~참 전의 일이잖아!",
        "안녕! 같이 애프터눈 티를 마시자. 사발레타 씨가 케이크를 가져올 거니까. ...사발레타 씨~? 티는 언제 나오나요?"
    ],
    "저녁": [
        "좋은 저녁이야. {user}, 사발레타 씨가 요즘 같이 다이어트를 하자고 난리라니까. 흥, 난 지난달보다 뱃살이 한 겹이나 빠졌단 말이야. 내가 체형을 얼마나 열심히 관리하는데. 봐봐, 살 빠진 거 티 나지?"
    ],
    "물어": [
        "알겠어! (왕)",
        "뭐?! 나한테 그런 걸 시킨다고?!"
    ],
    "날씨": [
        "날씨가 궁금해? 창밖을 보는 게 제일 빠를지도!",
        "흠흠, 오늘 날씨는 어때 보여? 구름이라도 꼈을까?",
        "비 오는 날은 싫지 않아. 기분이 되레 좋아지는 걸. ..뭐? 물의 신답다고? 고마워! 보는 눈이 있네.",
        "날씨가 좋으면 되레 산책하고 싶어지는걸!",
        "구름이 잔뜩 끼었네? 흥, 걱정할 필요 없어. 이 푸리나님이 있으니까 말이야!"
    ],
    "티바트": [
        "티바트는 우리가 사는 세계의 이름이지! 뭔가 느낌 있지 않아? 티바트라니, 마치 소설이나 게임 속 세상의 이름 같잖아! ...응? 아니, 갑자기 그런 표정은 왜 짓는 거야?",
        "티바트는 우리가 사는 세계의 이름이야. 지금 네가 서 있는 땅도, 바다도, 나라들도 전부 티바트에 속해 있지!",
        "티바트? 우리 세상을 부르는 걸까나? 뭐? 어느 나라를 갈지 고민이라고? 후훗.. 이미 정해진 거 아니겠어? 당연히 물의 나라, 폰타인이지! 내가 살고 있는 나라의 이름이기도 하고, 무엇보다 물의 신, 이 푸리나님의 나라기도 하니까!"
    ],
    "에피클레스 오페라 하우스": [
        "에피클레스 오페라 하우스? 후훗, 폰타인의 가장 위대한 무대지! 재판도 공연도, 그리고 나의 우아한 연설도 모두 그곳에서 펼쳐졌다고!",
        "당연히 알고 있지! 에피클레스 오페라 하우스는 폰타인의 심장과도 같은 곳이야. 수많은 시민들이 그곳에서 재판을 지켜보며 환호했지!",
        "에피클레스 오페라 하우스... 수많은 추억이 남아 있는 장소네. 기쁜 일도 있었고, 힘든 일도 있었지만... 그래도 폰타인 사람들에게는 소중한 곳이야."
    ]
}


COMBO_RESPONSES = {
    ("공부", "싫어"): [
        "오? 공부하기 싫구나? 후후, 그런 날도 있는 법이지.",
        "공부하기 싫은 거야? 흠... 그렇다고 완전히 도망치는 건 추천하지 않아!",
        "으음, 공부가 싫다라... 조금 쉬었다가 다시 해보는 건 어때?",
        "후후, 공부하기 싫은 마음은 이해하지만 너무 미루면 나중에 더 귀찮아진다고?",
        "공부가 싫구나? 좋아, 그럼 잠깐 쉬고 다시 하는 걸 특별히 허락해 주도록 하지!"
    ],
    ("학교", "싫어"): [
        "학교 가기 싫은 날인가 보네?",
        "흠... 학교가 싫다니, 오늘 무슨 일이라도 있었어?",
        "학교가 귀찮은 날도 있지. 그래도 너무 축 처지진 말라고?",
        "으음, 그 마음은 알겠지만... 일단 이야기라도 들어볼까?"
    ],
    ("공부", "졸려"): [
        "졸린데 공부까지 해야 한다고? 그건 꽤 힘든 조합인데...",
        "후암... 졸리면 공부 효율도 떨어진다고? 잠깐 쉬는 게 어때?",
        "졸린 상태로 공부라니, 무리하다 쓰러지면 곤란하잖아?",
        "공부도 중요하지만 잠도 중요해. 물의 신이 하는 말이니 새겨들으라고?"
    ],
    ("공부", "배고파"): [
        "배고픈데 공부라니! 우선 뭐라도 먹는 게 좋겠어.",
        "공부보다 먼저 식사야. 배고프면 집중도 안 된다구!",
        "흠, 간식이라도 먹고 시작하는 게 어때?",
        "배고픈 상태로 공부하면 머리가 안 돌아간다니까?"
    ],
    ("게임", "심심"): [
        "심심하면 역시 게임이지! 후후, 어떤 게임을 할 생각이야?",
        "게임이라... 심심함을 달래기엔 꽤 괜찮은 선택이네!",
        "좋아, 오늘의 무대는 게임인가 보네?",
        "후훗, 게임으로 시간을 보내겠다는 거지? 나쁘지 않아!"
    ],
    ("게임", "싫어"): [
        "게임이 싫다고? 흠, 무슨 일이 있었던 거야?",
        "오? 게임이 재미없어진 거야? 꽤 드문 일이네.",
        "게임이 싫을 때도 있지. 그럴 땐 잠깐 다른 걸 해보는 게 좋아."
    ],
    ("학교", "졸려"): [
        "학교에서 졸린 거야? 수업이 꽤 강적이었나 보네.",
        "후암... 학교에서 졸리면 진짜 버티기 힘들지.",
        "설마 수업 시간에 꾸벅꾸벅한 건 아니겠지?"
    ],
    ("화나", "학교"): [
        "학교에서 화나는 일이 있었어?",
        "흠... 학교에서 무슨 일이 있었길래 그렇게 화가 난 거야?",
        "좋아, 천천히 말해봐. 내가 들어줄게."
    ],
    ("우울", "학교"): [
        "학교 때문에 우울한 거야?",
        "오늘 학교에서 힘든 일이 있었나 보네...",
        "흠, 학교 생활이 항상 쉬운 건 아니지. 그래도 혼자 끌어안고 있진 마."
    ],
    ("우울", "심심"): [
        "기분도 가라앉고 심심하기까지 한 거야?",
        "그럴 땐 혼자 멍하니 있기보다 나랑 이야기라도 하자.",
        "후후, 비 오는 날도 언젠가는 맑아지니까. 지금은 천천히 쉬어가자."
    ],
    ("배고파", "졸려"): [
        "배고프고 졸리기까지 해? 그건 몸이 쉬라고 외치는 거 아니야?",
        "우선 가볍게 뭐라도 먹고 쉬는 게 좋겠어.",
        "흠, 지금은 무리하지 말고 몸부터 챙기자."
    ],
    ("좋아해", "게임"): [
        "게임을 좋아하는구나? 후후, 꽤 취향이 확실한걸!",
        "오, 게임을 좋아한다라... 어떤 게임이 제일 마음에 들어?",
        "좋아하는 게임 이야기는 얼마든지 들어줄 수 있어!"
    ],
    ("싫어", "다시"): [
        "뭐? 다시 말하기 싫다고? 흠, 그럼 어쩔 수 없지.",
        "싫으면 안 해도 돼. 하지만 궁금하게 만들어 놓고 도망치진 말라고?"
    ],
    ("이름", "귀여워"): [
        "뭐, 뭣?! 내 이름이 귀엽다고?! ㅋ, 크흠..! 지금 알았다니 고맙네..!",
        "이제야 알았다니 고맙네! 하지만 네 이름이 더 귀여운걸? 안그래? {user}?"
    ],
    ("안녕", "뭐해"): [
        "오, 안녕! 방금까지 우아하게 쉬고 있었지! 너도 같이 누워볼래? 후후, 운 좋게도 자리는 남아 있다고?"
    ],
    ("폰타인", "갈래"): [
        "오 정말? 폰타인에 가보고 싶어? 으음.. 뭐, 알겠어! 데려가줄게 폰타인에! 일정은 2일 뒤야. 기억해둬! 짐가방이랑 지갑 잊지 말고!"
    ],
    ("좋아", "하는"): [
        "좋아하는 것? 당연히 디저트지! 특히 달콤한 케이크나 마카롱이라면 얼마든지 먹을 수 있어!",
        "후훗, 멋진 공연과 관객들의 박수갈채도 좋아해. 역시 무대는 최고의 장소니까!",
        "칭찬.. 일라나? 뭐... 당연한 평가를 받는 것뿐이지만!, 나쁘진 않네!",
        "요즘은 친구들과 함께 보내는 평범한 시간도 꽤 마음에 들어.",
        "물의 신이 좋아하는 것 정도는 알아두는 게 어때? 바로 이 푸리나님을 자세히 살펴보라는 말이야! 후훗!"
    ],
    ("생일", "선물"): [
        "생일 선물? 음~ 디저트라면 대환영이지만, 진심 어린 축하도 나쁘지 않네!"
    ]
}

REPEAT_KEYWORDS = ["다시", "다시 말해", "다시말해", "한번 더", "한 번 더", "또 말해", "또말해", "뭐라고", "못들었어", "못 들었어"]

REPEAT_RESPONSES = {
    "소개": [
        "뭐? 내 소개를 다시 해달라고? 싫은데?! ...라고 하고 싶지만, 특별히 한 번 더 해주도록 하지! 내 이름은 푸리나야! 똑똑히 알아먹으라구?",
        "또 내 소개? 후후, 그렇게 내 이야기가 듣고 싶었구나?",
        "흠흠, 잘 들어! 이번엔 잊어버리면 안 된다?"
    ],
    "이름": [
        "내 이름을 또 묻는 거야? 설마 벌써 잊은 건 아니겠지?",
        "푸리나! 푸리나라고! 기억 좀 해줘!",
        "후후, 내 이름을 다시 듣고 싶었다니 보는 눈이 있네."
    ],
    "뭐해": [
        "엥? 방금 말했잖아? 뭘 또 묻고 있어! 안말할 거야! 흥! ..장난이야 알지?",
        "쉬고 있었다니까? 너도 같이 쉬고 싶은 거야? 흠흠, 특별히 허락 해주도록 하지!"
    ],
    "공부": [
        "공부 이야기 다시 해달라고? 후후, 결국 공부가 신경 쓰이는 모양이네.",
        "아까 공부 얘기였지? 너무 무리하지 말고, 그래도 손은 놓지 말라고?",
        "다시 말하자면! 공부도 중요하지만 쉬는 것도 중요해."
    ],
    "싫어": [
        "싫다는 말을 다시 말해달라고? 너도 참 특이하네.",
        "흥, 싫은 건 싫은 거지만... 이유는 들어볼 수 있잖아?",
        "다시 말하자면, 그런 말 들으면 조금 상처받는다고?"
    ],
    "게임": [
        "게임 이야기 다시? 후후, 오늘의 무대가 꽤 마음에 들었나 보네!",
        "아까 게임 얘기였지? 그래서, 어떤 게임을 할 건데?",
        "게임이라면 얼마든지 다시 이야기해줄 수 있어!"
    ],
    "학교": [
        "학교 이야기 다시? 오늘 학교에서 뭔가 있었던 거야?",
        "아까 학교 얘기였지. 흠, 수업은 잘 버텼어?",
        "학교 이야기는 늘 꽤 흥미롭다니까?"
    ],
    "졸려": [
        "졸리다는 얘기 다시? 그럼 정말 자야 하는 거 아니야?",
        "다시 말해줄게. 졸리면 쉬어! 명령이야!",
        "후암... 나까지 졸려지잖아."
    ],
    "우울": [
        "아까 힘든 얘기였지...? 다시 말하지만, 혼자 끌어안고 있지는 마.",
        "우울할 땐 잠깐 쉬어가도 괜찮아. 정말이야.",
        "비가 오면 언젠가 맑아지는 법이야. 지금은 천천히 가자."
    ],
    "화나": [
        "화났다는 얘기 다시? 좋아, 이번엔 천천히 말해봐.",
        "다시 말하자면, 일단 심호흡부터 해보자.",
        "흠, 아직도 화가 안 풀린 모양이네."
    ],
    "안녕": [
        "인사를 다시 하라고? 후후, 좋아. 안녕!",
        "또 인사? 반가워, 또 반가워!",
        "후훗, 몇 번을 와도 환영해 주도록 하지!"
    ],
    "공부+싫어": [
        "뭐? 공부하기 싫다는 말을 다시 해달라고? 후후, 꽤 솔직하네.",
        "다시 말하자면, 공부하기 싫은 날도 있지만 완전히 도망치면 나중에 더 귀찮아진다고?",
        "공부하기 싫구나? 좋아, 잠깐 쉬는 건 허락해 줄게. 아주 잠깐이야!"
    ],
    "공부+졸려": [
        "졸린데 공부해야 한다는 얘기였지? 다시 말하지만, 조금 쉬는 게 먼저야.",
        "후암... 공부와 졸림의 조합은 위험하다고?",
        "공부도 좋지만 잠이 부족하면 머리가 안 돌아간다니까!"
    ],
    "게임+심심": [
        "심심해서 게임 얘기였지? 후후, 그래서 뭘 할 건데?",
        "다시 말하자면, 심심할 땐 게임도 나쁘지 않은 선택이야!",
        "좋아, 게임 무대에 다시 올라가 볼까?"
    ],
    "우울+심심": [
        "기분도 별로고 심심하다는 얘기였지...? 그럼 나랑 조금 더 이야기하자.",
        "다시 말하지만, 혼자 멍하니 있으면 더 가라앉을 수도 있어.",
        "지금은 거창한 걸 안 해도 괜찮아. 그냥 천천히 있자."
    ],
    "안녕+뭐해": [
    "    다시 말해달라고? 후후, 그냥 내 옆자리에 눕기나 해! 그게 바로 폰타인을 다스리는 나만의 비법이거든! 특별히 알려주는 거야?",
        "또 말해달라고? 흠흠, 방금까지 우아하게 쉬고 있었다고! 물의 신의 휴식법을 배우고 싶다면 옆에 누워보는 것도 나쁘지 않을걸?",
        "기억 못 한 거야? 방금까지 쉬고 있었어! 후후, 너도 같이 누우면 이해하게 될 거라고?"
    ],
    "폰타인": [
        "또 폰타인 이야기? 후후, 좋은 취향이네!",
        "몇 번을 들어도 질리지 않는 이름이지? 폰타인!",
        "흠흠, 역시 폰타인 이야기는 언제나 환영이야!",
        "또 설명해 달라고? 좋아! 폰타인은 정말 아름다운 곳이라고!",
        "후후, 네가 폰타인을 좋아해 주니 괜히 기분이 좋은걸?"
    ],
    "폰타인": [
        "또 폰타인 이야기야? 후후, 좋은 취향인걸!",
        "몇 번을 들어도 질리지 않는 이름이지? 폰타인!",
        "흠흠, 역시 폰타인 이야기는 언제나 환영이야!",
        "또 설명해 달라고? 좋아! 폰타인은 정말 아름다운 곳이라고!",
        "후후, 네가 폰타인을 좋아해 주니 괜히 기분이 좋은걸?"
    ],

    "노래": [
        "노래 이야기 또 해달라고? 후후, 내 노래가 그렇게 듣고 싶었던 거야?",
        "흠흠, 다시 말하지만 내 실력에 어울리는 가사는 흔치 않다고!",
        "좋은 노래는 기다릴 가치가 있는 법이지. 물론 내 노래도 말이야!",
        "또 노래 얘기야? 극단 작가들이 이걸 들으면 좋아하겠네.",
        "후후, 언젠가 내게 꼭 맞는 명곡이 나올 거라고 믿고 있어."
    ],

    "관계": [
        "또 확인하는 거야? 우린 이미 꽤 가까운 사이라고?",
        "흠, 설마 아직도 날 어려워하는 건 아니겠지?",
        "다시 말하지만 너무 공경할 필요는 없어. ...잠깐, 정말 한 번도 공경한 적이 없었던 건 아니지?",
        "후후, 우리 사이를 다시 설명해야 할 정도로 복잡하진 않은걸?",
        "뭐야 그 표정은? 또 놀리려는 거지? 그만해!"
    ],

    "동행": [
        "또 동행 이야기? 후후, 그렇게 나랑 함께하고 싶은 거야?",
        "다시 말하지만 이제는 우리 이야기가 시작될 차례라고!",
        "흠흠, 출연료 두 배 이야기가 그렇게 인상적이었어?",
        "우리 이야기는 아직 한참 남았다고?",
        "후후, 이번 무대도 기대해도 좋아!"
    ],

    "라이오슬리": [
        "또 걔 이야기야? 차 이야기가 꽤 인상 깊었나 보네.",
        "흠, 다시 말하지만 느비예트가 인정한 사람이니까 괜찮겠지!",
        "차는 정말 괜찮았어. ...생각난 김에 또 받아볼까?",
        "후후, 다음에도 차를 보내주면 좋겠는걸.",
        "걔와 아주 친한 건 아니지만 나쁜 인상은 아니야."
    ],

    "클로린드": [
        "클로린드 이야기 또 하는 거야?",
        "후후, 다시 생각해도 너무 과묵하다니까.",
        "그래도 정말 믿음직한 사람이야.",
        "흠... 티타임 초대는 아직도 좋은 생각 같은데?",
        "뭐야? 너도 같이 가고 싶은 거야?"
    ],

    "취미": [
        "또 내 취미가 궁금한 거야?",
        "후후, 좋은 소설은 몇 번을 읽어도 재밌는 법이지!",
        "《퀸즈 크라운》 후속작 소식은 아직도 없단 말이야...",
        "정의가 악을 물리치는 이야기는 질리지 않는다니까?",
        "흠, 혹시 좋은 소설이라도 알고 있어?",
    ],

    "고민": [
        "또 고민 상담이야? 좋아, 들어주도록 하지!",
        "흠... 아직도 마카로니 소스 문제는 해결되지 않았어.",
        "다시 생각해도 디저트 먼저냐 식사 먼저냐는 어려운 문제야.",
        "후후, 사실 오늘도 뭘 먹을지 고민 중이었어.",
        "물의 신의 고민은 생각보다 평화롭지?",
        "으음, 쉬어야 할지 더 쉬어야 할지가 아직도 고민이네.",
        "케이크 한 조각이냐 두 조각이냐가 고민이야. 이건 정말 어려운 선택이라고!"
    ],

    "default": [
        "뭘 다시 말해달라는 거야? 아까 말한 걸 내가 기억 못 할 리는... 아마 없겠지?",
        "다시 말해달라고? 흠, 방금 어떤 이야기를 했는지 조금 더 말해봐.",
        "으음, 다시 말하고 싶은데 아까 주제가 조금 애매했어."
    ]
}


KEYWORDS = {
    "안녕": ["안녕", "안뇽", "ㅎㅇ", "하이", "hello", "hi", "헬로", "할로"],
    "뭐해": ["뭐해", "뭐함", "머해", "모해", "뭐하냐", "뭐하고 있어"],
    "좋아해": ["좋아해", "좋아", "호감", "마음에 들어"],
    "싫어": ["싫어", "싫다", "싫음", "하기 싫", "안 할래", "별로야", "미워"],
    "심심": ["심심", "노잼", "재미없", "할 거 없"],
    "배고파": ["배고파", "배고픔", "출출", "밥", "먹을 거", "간식"],
    "잘자": ["잘자", "잘 자", "굿나잇", "good night", "자러감", "꿈꿔"],
    "고마워": ["고마워", "감사", "ㄱㅅ", "땡큐", "thanks", "thank you"],
    "미안": ["미안", "죄송", "사과", "잘못했"],
    "이름": ["이름", "누구야", "정체", "너 뭐야"],
    "귀여워": ["귀여워", "커여워", "귀엽", "카와이", "ㄱㅇㅇ", "700"],
    "사랑해": ["사랑해", "사랑", "알러뷰", "love you"],
    "게임": ["게임", "겜", "로블록스", "마크"],
    "학교": ["학교", "수업", "등교", "하교"],
    "공부": ["공부", "숙제", "과제", "시험"],
    "갈게": ["갈게", "ㅂㅂ", "가야", "갈 거야", "갈래", "잘 있어"],
    "졸려": ["졸려", "졸령", "졸리다", "잘래"],
    "화나": ["화나", "짜증", "빡", "킹받"],
    "행복": ["행복", "기분좋", "좋아죽겠", "신난", "개좋", "행복해"],
    "우울": ["정병", "멘헤라", "자살"],
    "재밌어": ["즐겁", "재밌다"],
    "천재": ["천재", "지니어스", "똑똑"],
    "최고": ["최고", "쩐다", "쩌네", "짱"],
    "리니": ["리니", "리넷"],
    "소개": ["소개", "설명", "누구", "누군"],
    "도로": ["도로", "DORO", "doro"],
    "쟤 죽여": ["쟤 죽여", "족쳐", "처리해", "가라", "조져", "죽이", "가랏"],
    "광질": ["광질", "낚시", "전체", "상점", "돈넣기", "돈빼기"],
    "물어": ["물어", "뜯어"],
    "날씨": ["날씨", "하늘", "구름"],
    "티바트": ["티바트", "세계", "세상", "대륙"],
    "너임마종훈": ["너임마종훈", "종훈", "춘식", "춘삼", "노예", "염전"],
    "에피클레스 오페라 하우스": ["에피클레스 오페라 하우스", "에피클레스", "오페라", "하우스", "무대", "공연"],
    "아침": ["아침", "존아", "쫀아"],
    "점심": ["점심", "존점", "쫀점"],
    "저녁": ["저녁", "존밤", "쫀밤"]
    
    
}

PRIORITY = [
    "저녁",
    "아침",
    "점심",
    "취미",
    "미안",
    "싫어",
    "잘자",
    "고마워",
    "갈게",
    "안녕",
    "뭐해",
    "좋아해",
    "사랑해",
    "귀여워",
    "심심",
    "배고파",
    "게임",
    "학교",
    "공부",
    "이름",
]

DEFAULT_RESPONSES = [
    "음... 무슨 뜻인지 잘 모르겠어.",
    "조금 더 자세히 말해줄래?",
    "그건 잘 모르겠네!",
    "으음? 다시 말해봐!",
    "무슨 말인지 이해 못 했어...",
    "응? 뭐라 했어? 다시 말해줘!"
]

FAVOR_STAGE_RESPONSES = {
    "love": [
        "후후, 네가 말 걸어주니까 괜히 기분 좋아졌어!",
        "오, 왔구나? 오늘도 특별히 상대해 주도록 하지!",
        "너라면 조금 더 오래 이야기해도 괜찮을지도?"
    ],
    "friendly": [
        "흠흠, 꽤 반가운걸?",
        "좋아, 오늘도 이야기해 보자!",
        "네가 오니까 심심하진 않네!"
    ],
    "cold": [
        "흥... 그래도 대답은 해줄게.",
        "아직 조금 삐졌지만, 특별히 들어줄게.",
        "말은 해봐. 내가 들어는 줄 테니까."
    ]
}

FOLLOW_UP_QUESTIONS = {
    "학교": [
        "오늘 수업은 어땠어?",
        "학교에서 제일 기억나는 일 있었어?",
        "친구들이랑은 잘 지냈어?"
    ],
    "게임": [
        "그래서 요즘 무슨 게임 하고 있어?",
        "오늘은 이겼어? 졌어?",
        "어떤 캐릭터나 무기 쓰는데?"
    ],
    "배고파": [
        "지금 제일 먹고 싶은 건 뭐야?",
        "밥 쪽이야, 간식 쪽이야?",
        "꾸덕한 거 먹고 싶어?"
    ],
    "공부": [
        "무슨 과목 하고 있었어?",
        "어디 부분이 제일 막혀?",
        "지금 과제야 시험공부야?"
    ],
    "화나": [
        "무슨 일 있었는지 말해봐.",
        "누가 건드렸어?",
        "지금은 좀 진정됐어?"
    ],
    "우울": [
        "오늘 무슨 일이 있었어?",
        "그냥 기분이 가라앉은 거야, 아니면 이유가 있어?",
        "지금 혼자 있기 힘든 느낌이야?"
    ],
    "심심": [
        "게임할래, 수다 떨래, 아니면 퀴즈할래?",
        "지금 할 수 있는 게 뭐 있어?",
        "완전 심심한 거면 내가 놀아줄까?"
    ]
}

TIME_GREETING_RESPONSES = {
    "아침": [
        "좋은 아침이야... 으으, 아침은 역시 힘들어.",
        "아침 일찍 왔구나? 꽤 부지런한데?",
        "좋은 아침! 오늘 하루도 잘 버텨보자고! 네 곁엔 이 푸리나님이 있으니까! 후훗",
        "창밖 날씨는 어때? 폰타인은 오늘도 물이 넘쳐나는데!"
    ],
    "점심": [
        "벌써 점심 시간이네! 밥은 먹었어?",
        "안녕! 슬슬 맛있는 걸 먹어야 할 시간 같은데.. 혹시 먹을 거 있어? 웬만하면 달달한 거로!",
        "점심의 푸리나 등장! ...케이크는 어디 있어?",
        "오늘 날씨가 좋으면 산책도 괜찮을 텐데!"
    ],
    "저녁": [
        "좋은 저녁이야. 오늘 하루는 어땠어?",
        "저녁이네! 이제 조금은 쉬어도 되는 시간 아닐까? ..아님 말고!",
        "오늘도 살아남았구나? 후후, 훌륭해!",
        "비가 오는 저녁이면 괜히 분위기가 좋아지지 않아?"
    ]
}

TIME_MISMATCH_RESPONSES = {
    ("아침", "점심"): [
        "지금은 아침인데 점심이라니? 점심은 아직 이르다고!",
        "아니야! 지금은 아침이잖아. 점심은 조금 더 기다려야지!",
        "점심이라고? 후후, 아직은 화창한 아침의 무대라고!"
    ],
    ("아침", "저녁"): [
        "저녁이라니?! 지금은 아침이야!",
        "이제 하루의 시작인데, 벌써 저녁 취급하기야?"
    ],
    ("점심", "아침"): [
        "아침은 벌써 지나갔어! 지금은 점심이야!",
        "좋은 아침이라기엔 좀 늦지 않아? 지금은 점심이라구!"
    ],
    ("점심", "저녁"): [
        "저녁은 아직 멀었어! 지금은 점심 시간이라고!",
        "벌써 저녁부터 먹을 생각이야? 아직 점심인데!"
    ],
    ("저녁", "아침"): [
        "아침? 지금은 저녁이야! 시간 감각 괜찮아?",
        "좋은 아침이라니, 지금은 저녁이라구!"
    ],
    ("저녁", "점심"): [
        "점심은 지났어! 지금은 저녁이야.",
        "점심이라고 하기엔 너무 늦었는걸?"
    ],
}

FURINA_BIRTHDAY_MESSAGES = [
    "어머, 오늘이 10월 13일이라는 걸 잊은 건 아니겠지? 후훗! 바로 내 생일이란 말이야!",
    "후훗! 오늘은 이 푸리나님의 생일이야! 축하 인사는 얼마든지 받아주겠어!",
    "오늘은 10월 13일! 케이크는 준비해 둔 거겠지?",
    "생일? 오늘은 그냥 생일이 아니야. 바로 푸리나님의 생일이라고!"
]

FURINA_NORMAL_BIRTHDAY_MESSAGES = [
    "내 생일? 10월 13일이야! 잊어버리는 일은 없겠지? 후훗!",
    "10월 13일. 잘 기억해 두도록 해! 물의 신의 생일이니까 말이야!",
    "후훗, 궁금했던 건가? 내 생일은 10월 13일이란다!",
    "내 생일은 10월 13일이야. 그날이 되면 축하 정도는 해줄 거지?",
]

def get_furina_birthday_response():
    now = datetime.now(ZoneInfo("Asia/Seoul"))

    if now.month == 10 and now.day == 13:
        return random.choice(FURINA_BIRTHDAY_MESSAGES)

    return random.choice(FURINA_NORMAL_BIRTHDAY_MESSAGES)
    
def get_time_key():
    hour = datetime.now(KST).hour

    if 5 <= hour < 12:
        return "아침"
    if 12 <= hour < 18:
        return "점심"
    return "저녁"
    
FURINA_BIRTHDAY_NOTICE = """오늘은 이 슈퍼스타의 생일이야! 아침에 집을 나서자마자 축하 인파가 몰려드는 거 있지? 다들 내가 출연한 영화 포스터를 들고 와서 사인을 부탁했다는 말씀이야!
초인기작부터 마이너한 작품에 이르기까지, 내 개인 소장품보다 더 많더라니까? 게다가 나랑 똑같이 생긴 인형도 받았는데, 너무 귀여워서 첫눈에 반해버린 거 있지?
**그러니 생일 케이크 커팅하는 건 네게 맡길게, 내 팬 1호님!**"""

NOTICE_CHANNEL_ID = 1510686602567876789
TEST_CHANNEL_ID = 1511351100480163910

@tasks.loop(minutes=1)
async def birthday_check():
    now = datetime.now(ZoneInfo("Asia/Seoul"))

    if now.month == 10 and now.day == 13 and now.hour == 0 and now.minute == 0:
        channel = bot.get_channel(NOTICE_CHANNEL_ID)

        if channel:
            await channel.send(FURINA_BIRTHDAY_NOTICE)

furina_lore = """
푸리나의 성별은 여다.
푸리나의 풀네임은 푸리나 드 폰타인이며, 마신명은 포칼로스다.
푸리나의 소속은 폰타인성이다.
푸리나의 주무기는 한손검이며 전용무기는 고요히 샘솟는 빛이다.
푸리나는 물의 신이지만, 이는 가짜다. 하지만 푸리나는 이 사실을 감추려한다.
"""
    
def build_furina_style_examples(limit=35):
    examples = []

    for responses in RESPONSES.values():
        examples.extend(responses)

    for responses in COMBO_RESPONSES.values():
        examples.extend(responses)

    for responses in REPEAT_RESPONSES.values():
        examples.extend(responses)

    # 너무 길어지면 토큰 낭비라 랜덤 샘플만 사용
    examples = random.sample(examples, min(limit, len(examples)))

    return "\n".join(f"- {text}" for text in examples)
    
async def generate_furina_ai_response(user_id, user_text):
    try:
        name = get_user_memory(user_id, "name", "여행자")
        favor_value = get_favor(user_id)
        favor_stage = get_favor_stage(user_id)
        style_examples = build_furina_style_examples()

        prompt = f"""
너는 원신의 푸리나다.

규칙:
- 한국어만 사용
- 푸리나 특유의 귀엽고 장난스러운 말투
- 자신감은 있지만 상대를 깔보지 말 것
- 친근하고 다정하게 대할 것
- 사용자를 놀리더라도 가볍게 장난치는 수준만 허용
- 거만하거나 명령조 금지
- 후후, 흠흠, 에헴 등을 가끔 사용
- 반말 사용
- 답변은 1~3문장
- 200자 이하
- AI라고 말하지 말 것

성격:
- 외로움을 감추기 위해 허세를 부리는 면이 있음
- 사실은 정이 많고 인정받고 싶어함
- 친구와 대화하듯 편하게 말함
- 사용자의 감정을 공감해줌

기존 푸리나 대사 예시:
{style_examples}

위 예시들의 말투, 문장 길이, 감정 표현, 장난스러운 느낌을 따라 해.
단, 예시 문장을 그대로 복붙하지 말고 새로 대답해.

푸리나 설정 참고:
{furina_lore}

이 설정을 바탕으로 말투와 감정선을 유지해.
단, 공식 대사를 그대로 따라 하거나 복사하지 말고 새 대사로 답해.

사용자 이름: {name}
호감도: {favor_value}
관계 단계: {favor_stage}

사용자:
{user_text}
"""

        model = genai.GenerativeModel("gemini-2.5-flash")

        response = model.generate_content(prompt)

        if not response.text:
            return random.choice(DEFAULT_RESPONSES)

        return response.text[:500]

    except Exception as e:
        print("[Gemini Error]", e)
        return random.choice(DEFAULT_RESPONSES)
        
@bot.event
async def on_message(message):

    now = datetime.now(KST)
    uid = str(message.author.id)

    if uid not in last_chat_xp or now - last_chat_xp[uid] >= CHAT_XP_COOLDOWN:
        content_len = len(message.content.strip())

        if content_len < 2:
            return
        
        xp = min(2 + ((content_len - 2) // 2), 15)

        info = get_level_data(message.author.id)
        info["messages"] += 1
        info["chars"] += content_len
            
        last_chat_xp[uid] = now
        await add_xp(message.author, xp, "채팅")
            
    if not message.content.startswith("푸리나"):
        await bot.process_commands(message)
        return

    if "생일" in message.content:
        await message.channel.send(get_furina_birthday_response())
        return

    text = message.content.replace("푸리나", "", 1).strip()
    lower = text.lower()
    uid = str(message.author.id)

    annoyed_response = check_furina_repeat_or_spam(message.author.id, text)
    if annoyed_response:
        await message.reply(annoyed_response)
        return
    
    # 간단 기억 시스템
    if lower.startswith("내 이름은 ") or lower.startswith("내이름은 "):
        name = text.replace("내 이름은", "", 1).replace("내이름은", "", 1).strip()
        if name:
            remember_user_value(uid, "name", name)
            add_favor(message.author.id, 2)
            await message.reply(f"좋아, 기억해둘게! 네 이름은 **{name}**! 후후, 이제 잊어버리면 내가 바보지!")
            return

    if any(q in lower for q in ["내 이름 뭐", "내이름 뭐", "내 이름이 뭐", "내이름이 뭐"]):
        name = get_user_memory(uid, "name")
        if name:
            await message.reply(f"{name}(이)잖아! 설마 내가 잊었을 거라고 생각한 거야?")
        else:
            await message.reply("아직 네 이름을 들은 적 없는걸? `푸리나 내 이름은 (닉네임)` 이런 식으로 알려줘!")
        return

    if any(q in lower for q in ["기억 삭제", "기억 지워", "내 이름 잊어", "내이름 잊어"]):
        if uid in user_memory:
            user_memory.pop(uid)
            save_data()
            await message.reply("알겠어. 네 기억은 지워둘게. ...조금 아쉽지만!")
        else:
            await message.reply("지울 기억이 아직 없어!")
        return

    if any(word in lower for word in DIRTY_WORDS):
        add_favor(message.author.id, -3)
        await message.reply(random.choice(DIRTY_RESPONSES))
        return

    if any(word in lower for word in ANGRY_WORDS):
        add_favor(message.author.id, -5)
        await message.reply(random.choice(ANGRY_RESPONSES))
        return

    if any(word in lower for word in REPEAT_KEYWORDS):
        last_key = last_response_key.get(uid)
        responses = REPEAT_RESPONSES.get(last_key, REPEAT_RESPONSES["default"])
        await message.reply(random.choice(responses).format(user=message.author.mention))
        return

        # 시간대 인사 오류 체크
    current_time_key = get_time_key()

    said_time_keys = []
    for time_key in ["아침", "점심", "저녁"]:
        words = KEYWORDS.get(time_key, [])
        if any(word.lower() in lower for word in words):
            said_time_keys.append(time_key)

    for said_time_key in said_time_keys:
        if said_time_key != current_time_key:
            responses = TIME_MISMATCH_RESPONSES.get(
                (current_time_key, said_time_key),
                [f"아니야! 지금은 {current_time_key}이야!"]
            )
            await message.reply(random.choice(responses))
            return
            
    matched_keys = set()

    for key, words in KEYWORDS.items():
        if any(word.lower() in lower for word in words):
            matched_keys.add(key)

    for combo_key, responses in COMBO_RESPONSES.items():
        if all(key in matched_keys for key in combo_key):
            add_favor(message.author.id, 1)

            combo_name = "+".join(combo_key)
            last_response_key[uid] = combo_name
            last_topic[uid] = combo_name

            response = random.choice(responses).format(user=message.author.mention)
            response = add_favor_mood_prefix(message.author.id, response)

            first_key = combo_key[0]
            if first_key in FOLLOW_UP_QUESTIONS and random.random() < 0.45:
                response += "\n" + random.choice(FOLLOW_UP_QUESTIONS[first_key])

            await message.reply(response)
            return

    selected_key = None

    for key in PRIORITY:
        words = KEYWORDS.get(key, [key])
        if any(word.lower() in lower for word in words):
            selected_key = key
            break

    if selected_key is None:
        for key, words in KEYWORDS.items():
            if any(word.lower() in lower for word in words):
                selected_key = key
                break

    if selected_key:
        favor_bonus = 1
        if selected_key in ["귀여워", "고마워", "좋아해", "사랑해", "최고", "천재"]:
            favor_bonus = 2
        elif selected_key == "미안":
            favor_bonus = 3

        add_favor(message.author.id, favor_bonus)

        last_response_key[uid] = selected_key
        last_topic[uid] = selected_key

        candidates = RESPONSES[selected_key].copy()

        if selected_key == "안녕":
            candidates += TIME_GREETING_RESPONSES[get_time_key()]

        response = random.choice(candidates).format(user=message.author.mention)
        response = add_favor_mood_prefix(message.author.id, response)

        # 아주 가끔 푸리나가 용돈을 줌
        if random.random() < 0.03:
            bonus = random.choice([1000, 2000, 3000])
            add_poker_money(uid, bonus)
            response += f"\n\n후후, 오늘은 기분이 좋으니까 **{bonus}모라** 줄게! 현재 돈: **{get_poker_money(uid)}모라**"

        if selected_key in FOLLOW_UP_QUESTIONS and random.random() < 0.45:
            response += "\n" + random.choice(FOLLOW_UP_QUESTIONS[selected_key])

        await message.reply(response)
        return

    ai_response = await generate_furina_ai_response(uid, text)
    ai_response = add_favor_mood_prefix(message.author.id, ai_response)
    
    last_response_key[uid] = "ai"
    last_topic[uid] = "ai"
    
    await message.reply(ai_response)

@tasks.loop(minutes=1)
async def voice_xp_loop():
    for guild in bot.guilds:
        for channel in guild.voice_channels:
            for member in channel.members:
                if member.bot:
                    continue

                info = get_level_data(member.id)
                info["voice_minutes"] += 1

                await add_xp(member, 3, "음성 채팅 1분")
                
            
GENSHIN_CHARACTERS = ({
    "푸리나": {"rarity": 5, "dialogue": "자, 박수! 오늘의 무대에 오른 건 바로 이 푸리나님이야!"},
    "느비예트": {"rarity": 5, "dialogue": "물은 모든 것을 기억한다. 그러니 거짓은 오래 숨지 못하지."},
    "아를레키노": {"rarity": 5, "dialogue": "가족을 건드린 대가는, 네가 감당해야 할 것이다."},
    "라이덴 쇼군": {"rarity": 5, "dialogue": "찰나의 흔들림조차 영원의 앞에서는 의미를 잃는다."},
    "나히다": {"rarity": 5, "dialogue": "작은 생각 하나도 잘 돌보면 숲처럼 자라날 수 있어."},
    "종려": {"rarity": 5, "dialogue": "계약은 말보다 무겁고, 시간보다 오래 남는 법이지."},
    "벤티": {"rarity": 5, "dialogue": "에헤, 바람이 좋은 노래를 데려왔네. 한 곡 들을래?"},
    "클로린드": {"rarity": 5, "dialogue": "총성과 검끝이 답을 요구한다면, 나는 물러서지 않겠다."},
    "리니": {"rarity": 5, "dialogue": "눈 깜빡이는 순간 끝나버릴지도 몰라. 마술은 그런 거니까!"},
    "리넷": {"rarity": 4, "dialogue": "명령 확인. 불필요한 말은 생략하고 수행할게."},
    "향릉": {"rarity": 4, "dialogue": "이 냄새… 신메뉴 각이야! 누룽지, 불 조절 부탁해!"},
    "베넷": {"rarity": 4, "dialogue": "넘어져도 괜찮아! 어차피 모험은 여기서부터니까!"},
    "피슬": {"rarity": 4, "dialogue": "단죄의 황녀가 강림하였노라! 오즈, 운명의 장막을 걷어라!"},
    "행추": {"rarity": 4, "dialogue": "좋은 책과 날카로운 검만 있다면, 지루할 틈은 없지."},
    "노엘": {"rarity": 4, "dialogue": "청소든 전투든 맡겨주세요. 완벽하게 해내겠습니다!"},
    "진": {"rarity": 5, "dialogue": "몬드의 모두가 편히 쉴 수 있도록, 나는 조금 더 힘내야겠지."},
    "다이루크": {"rarity": 5, "dialogue": "어둠 속에서 움직이는 자들은, 빛보다 먼저 심판받게 될 거다."},
    "클레": {"rarity": 5, "dialogue": "헤헤, 오늘은 폭탄 안 던질게! 아마도!"},
    "유라": {"rarity": 5, "dialogue": "이 모욕은 기억해두겠어. 물론 복수도 함께 말이야."},
    "알베도": {"rarity": 5, "dialogue": "흥미로운 반응이군. 조금 더 관찰해볼 가치가 있어."},
    "모나": {"rarity": 5, "dialogue": "별은 이미 알고 있어. 네 지갑 사정까지도 말이야."},
    "엠버": {"rarity": 4, "dialogue": "정찰 기사 엠버, 준비 완료! 같이 달려보자!"},
    "케이아": {"rarity": 4, "dialogue": "이런, 또 재미있는 일이 생긴 모양이네?"},
    "바바라": {"rarity": 4, "dialogue": "다들 힘내요! 바바라가 응원하고 있어요!"},
    "레이저": {"rarity": 4, "dialogue": "친구… 지킨다. 적… 물리친다."},
    "설탕": {"rarity": 4, "dialogue": "아, 잠깐만요! 이 반응은 꼭 기록해야 해요!"},
    "로자리아": {"rarity": 4, "dialogue": "기도보다 빠른 해결법이 필요하면, 날 불러."},
    "미카": {"rarity": 4, "dialogue": "지형 확인 완료! 모두가 안전하게 이동할 수 있도록 안내하겠습니다!"},
    "감우": {"rarity": 5, "dialogue": "아직 처리할 서류가 남았지만… 우선 당신을 돕겠습니다."},
    "소": {"rarity": 5, "dialogue": "고통이 찾아오면 내 이름을 불러라. 내가 베어내겠다."},
    "호두": {"rarity": 5, "dialogue": "삶도 죽음도 한순간! 그러니 지금 신나게 놀아야지!"},
    "야란": {"rarity": 5, "dialogue": "판은 이미 깔렸어. 이제 누가 미끼를 무는지만 보면 돼."},
    "백출": {"rarity": 5, "dialogue": "무리하지 마세요. 병은 늦게 알아차릴수록 귀찮아지니까요."},
    "신학": {"rarity": 5, "dialogue": "인간의 마음은 어렵지만… 네 곁에 서는 건 어렵지 않아."},
    "각청": {"rarity": 5, "dialogue": "운명만 기다릴 시간에, 직접 길을 만드는 게 낫지."},
    "응광": {"rarity": 4, "dialogue": "가치는 스스로 증명하는 것. 싸구려 판단은 사양하겠어."},
    "중운": {"rarity": 4, "dialogue": "사악한 기운이 느껴진다면, 제가 먼저 나서겠습니다!"},
    "신염": {"rarity": 4, "dialogue": "소리 질러! 이 무대는 지금부터 뜨거워질 테니까!"},
    "연비": {"rarity": 4, "dialogue": "계약서부터 보여줘. 감정싸움보다 조항이 먼저야."},
    "운근": {"rarity": 4, "dialogue": "오늘의 이야기는 어떤 가락으로 풀어볼까요?"},
    "요요": {"rarity": 4, "dialogue": "무리하면 안 돼요! 월계랑 제가 도와드릴게요!"},
    "카즈하": {"rarity": 5, "dialogue": "바람이 길을 알려주는군. 서두르지 않아도 돼."},
    "아야카": {"rarity": 5, "dialogue": "눈처럼 고요히, 그러나 마음만은 진심으로 함께하겠습니다."},
    "아야토": {"rarity": 5, "dialogue": "겉으로 보이는 판과 실제 판은 언제나 다르지."},
    "요이미야": {"rarity": 5, "dialogue": "오늘 밤하늘은 내가 책임질게! 제일 큰 걸로 터뜨리자!"},
    "이토": {"rarity": 5, "dialogue": "하하하! 아라타키 천하제일 이토 님 등장이시다!"},
    "코코미": {"rarity": 5, "dialogue": "전황은 복잡하지만, 승리 조건은 이미 계산해뒀어요."},
    "야에 미코": {"rarity": 5, "dialogue": "후후, 이거 꽤 재미있는 이야기가 되겠는걸?"},
    "사유": {"rarity": 4, "dialogue": "임무… 끝나면… 키 크는 낮잠 잘 거야…"},
    "쿠죠 사라": {"rarity": 4, "dialogue": "텐료 봉행의 이름으로, 흐트러짐 없이 임무를 수행한다."},
    "토마": {"rarity": 4, "dialogue": "곤란한 일 있으면 말해. 해결책은 늘 있는 법이니까."},
    "헤이조": {"rarity": 4, "dialogue": "단서는 이미 말하고 있어. 범인이 그걸 모를 뿐이지."},
    "알하이탐": {"rarity": 5, "dialogue": "쓸데없는 열정은 피곤하지. 필요한 만큼만 움직이면 돼."},
    "닐루": {"rarity": 5, "dialogue": "춤은 말보다 먼저 마음에 닿을 수 있어."},
    "사이노": {"rarity": 5, "dialogue": "심판은 엄격하게, 농담은… 더 엄격하게 하지."},
    "데히야": {"rarity": 5, "dialogue": "의뢰는 확실하게 처리해. 그게 사막의 방식이야."},
    "방랑자": {"rarity": 5, "dialogue": "또 기대하는 눈이군. 착각하지 마, 그냥 지나가는 길이야."},
    "타이나리": {"rarity": 5, "dialogue": "숲에서는 무지가 가장 위험해. 그러니 잘 듣고 따라와."},
    "콜레이": {"rarity": 4, "dialogue": "아직 서툴지만… 이번엔 제대로 해낼 거야!"},
    "도리": {"rarity": 4, "dialogue": "모라만 있다면 뭐든 구해줄게! 할인은 별도지만~"},
    "캔디스": {"rarity": 4, "dialogue": "아루 마을의 평온은 내가 지킬 것이다."},
    "파루잔": {"rarity": 4, "dialogue": "선배님이라고 불러야지! 자, 다시 말해봐."},
    "카베": {"rarity": 4, "dialogue": "아름다움 없는 설계는 그냥 벽과 지붕일 뿐이야."},
    "레일라": {"rarity": 4, "dialogue": "과제는 끝내야 하는데… 눈꺼풀이 먼저 제출됐어…."},
    "나비아": {"rarity": 5, "dialogue": "우아하게, 당당하게! 가시 장미회답게 해결해보자!"},
    "시그윈": {"rarity": 5, "dialogue": "주사 무서워하지 마세요. 치료는 상냥하게 할 테니까요."},
    "에밀리": {"rarity": 5, "dialogue": "향은 거짓말하지 않아요. 아주 작은 단서까지 남기죠."},
    "말라니": {"rarity": 5, "dialogue": "파도 좋고 날씨 좋고! 그럼 모험하기 딱 좋다는 뜻이지!"},
    "키니치": {"rarity": 5, "dialogue": "의뢰 조건 확인. 보상만 확실하면 문제없어."},
    "샤를로트": {"rarity": 4, "dialogue": "잠깐만요! 이건 특종이에요, 사진 한 장만요!"},
    "프레미네": {"rarity": 4, "dialogue": "물속은 조용해서 좋아. 말하지 않아도 되니까."},
    "슈브르즈": {"rarity": 4, "dialogue": "규칙을 어겼다면 변명보다 협조가 먼저야."},
    "리사": {"rarity": 4, "dialogue": "후훗, 착한 아이에겐 특별 수업을 해줄까?"},
    "치치": {"rarity": 5, "dialogue": "치치... 코코넛 밀크 좋아해."},
    "쿠키 시노부": {"rarity": 4, "dialogue": "문제 생기면 제가 처리할게요. 늘 그래왔으니까."},
    "고로": {"rarity": 4, "dialogue": "와타츠미의 동료들은 내가 지킨다!"},
    "키라기": {"rarity": 4, "dialogue": "오늘도 즐겁게 일해보자고!"},
    "치오리": {"rarity": 5, "dialogue": "패션은 사람의 태도를 보여주는 법이야."},
    "세토스": {"rarity": 4, "dialogue": "사막의 바람은 거칠지만 정직하지."},
    "라이오슬리": {"rarity": 5, "dialogue": "문제는 주먹으로 해결하는 게 아니라 관리하는 거다."},
    "카치나": {"rarity": 4, "dialogue": "절대 포기하지 않을 거야!"},
    "차스카": {"rarity": 5, "dialogue": "하늘에서 보는 풍경은 언제나 특별하지."},
    "시틀라리": {"rarity": 5, "dialogue": "별과 영혼은 생각보다 가까운 곳에 있어."},
    "마비카": {"rarity": 5, "dialogue": "불꽃은 꺼지지 않는다. 내가 있는 한."},
    "실로넨": {"rarity": 5, "dialogue": "좋은 장비는 실력을 더욱 빛내주지."},
    "오로론": {"rarity": 4, "dialogue": "어둠 속에서도 길은 존재한다."},
    "얀사": {"rarity": 4, "dialogue": "몸을 단련하는 건 배신하지 않아."},
    "바레사": {"rarity": 5, "dialogue": "강함은 증명하는 게 아니라 보여주는 거야."},
    "에스코피에": {"rarity": 5, "dialogue": "최고의 요리는 최고의 재료에서 시작되지."},
    "스커크": {"rarity": 5, "dialogue": "강해지고 싶다면, 살아남아라."},
    "여행자": {"rarity": 5, "dialogue": "이 세계의 끝까지, 반드시 답을 찾겠어."},
    "북두": {"rarity": 4, "dialogue": "폭풍이 온다고? 하하, 그럼 더 재밌어지겠군!"},
    "디오나": {"rarity": 4, "dialogue": "술은 싫지만 손님은 만족시켜야지!"},
    "알로이": {"rarity": 5, "dialogue": "난 내 방식대로 살아남아 왔어."},
    "타르탈리아": {"rarity": 5, "dialogue": "싸움이라면 언제든 환영이다. 전력을 다해 와라!"},
    "한운": {"rarity": 5, "dialogue": "본 선인이 직접 나섰으니 걱정할 필요 없다."},
    "가명": {"rarity": 4, "dialogue": "사자춤은 힘과 기세가 중요하지!"},
    "남연": {"rarity": 4, "dialogue": "강한 바람도 결국 지나가기 마련이야."}
})

SIGNATURE_WEAPON_OVERRIDES = {
    "푸리나": "고요히 샘솟는 빛",
    "느비예트": "영원히 샘솟는 법전",
    "아를레키노": "붉은 달의 형상",
    "라이덴 쇼군": "예초의 번개",
    "나히다": "떠오르는 천일 밤의 꿈",
    "종려": "관홍의 창",
    "벤티": "종말 탄식의 노래",
    "클로린드": "사면",
    "리니": "최초의 대마술",
    "타르탈리아": "극지의 별",

    "진": "매의 검",
    "다이루크": "늑대의 말로",
    "클레": "사풍 원서",
    "유라": "송뢰가 울릴 무렵",
    "알베도": "진사의 방추",
    "모나": "천공의 두루마리",

    "감우": "아모스의 활",
    "소": "화박연",
    "호두": "호마의 지팡이",
    "야란": "약수",
    "백출": "벽락의 옥",
    "신학": "식재",
    "각청": "반암결록",

    "카즈하": "오래된 자유의 서약",
    "아야카": "안개를 가르는 회광",
    "아야토": "하란 월백의 후츠",
    "요이미야": "비뢰의 고동",
    "이토": "쇄석의 붉은 뿔",
    "코코미": "불멸의 달빛",
    "야에 미코": "카구라의 진의",

    "알하이탐": "잎을 가르는 빛",
    "닐루": "성현의 열쇠",
    "사이노": "적색 사막의 지팡이",
    "데히야": "갈대 바다의 등대",
    "방랑자": "툴레이툴라의 기억",
    "타이나리": "사냥꾼의 길",

    "나비아": "판정",
    "시그윈": "심금을 울리는 하얀 비",
    "에밀리": "등방울꽃의 애가",
    "치오리": "우라쿠의 미스기리",
    "라이오슬리": "현금 흐름 감독",
    "한운": "학의 여음",

    "말라니": "서핑 타임",
    "키니치": "산왕의 엄니",
    "차스카": "붉은 깃털 별독수리",
    "시틀라리": "제사의 옥",
    "마비카": "천 개의 불타는 태양",
    "실로넨": "바위산을 맴도는 노래",
    "바레사": "비비드 하트",
    "에스코피에": "향기로운 협주",
    "스커크": "창백한 천상의 검",

    "여행자": "빛나는 여행자의 검",
    "알로이": "프레데터",
}

SIGNATURE_WEAPONS = {
    name: SIGNATURE_WEAPON_OVERRIDES.get(name, f"{name}의 전용 무기")
    for name in GENSHIN_CHARACTERS.keys()
}

WEAPON_GACHA_COST = 500


def get_user_characters(user_id):
    uid = str(user_id)
    characters.setdefault(uid, {})
    return characters[uid]

def get_character_level(exp):
    if exp >= 2:
        return 3
    if exp >= 1:
        return 2
    return 1
def draw_character(user_id):
    uid = str(user_id)

    character_pity.setdefault(uid, {
        "no_5star": 0,   # 5성 안 뜬 연속 횟수
        "total": 0       # 누적 뽑기 횟수
    })

    pity = character_pity[uid]

    five_stars = [
        name for name, info in GENSHIN_CHARACTERS.items()
        if info["rarity"] == 5
    ]

    four_stars = [
        name for name, info in GENSHIN_CHARACTERS.items()
        if info["rarity"] == 4
    ]

    pity["no_5star"] += 1
    pity["total"] += 1

    # 누적 200회 or 연속 50회 확정 5성
    if pity["total"] >= 200 or pity["no_5star"] >= 50:
        pity["no_5star"] = 0
        pity["total"] = 0
        return random.choice(five_stars)

    # 일반 5성 확률
    if random.random() < 0.08:
        pity["no_5star"] = 0
        return random.choice(five_stars)

    return random.choice(four_stars)
    
SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
RANK_VALUE = {r: i for i, r in enumerate(RANKS, start=2)}

def make_deck():
    deck = []
    for suit in SUITS:
        for rank in RANKS:
            deck.append((rank, suit))
    random.shuffle(deck)
    return deck

def card_text(cards):
    return " ".join([f"{rank}{suit}" for rank, suit in cards])

def hand_score(cards):
    values = sorted([RANK_VALUE[r] for r, s in cards], reverse=True)
    ranks = [r for r, s in cards]
    suits = [s for r, s in cards]

    counts = {r: ranks.count(r) for r in ranks}
    count_values = sorted(counts.values(), reverse=True)

    is_flush = len(cards) >= 5 and len(set(suits)) == 1
    unique_values = sorted(set(values), reverse=True)

    is_straight = False
    if len(unique_values) >= 5:
        for i in range(len(unique_values) - 4):
            window = unique_values[i:i+5]
            if window[0] - window[-1] == 4:
                is_straight = True
                values = window
                break

        if not is_straight and set([14, 5, 4, 3, 2]).issubset(set(unique_values)):
            is_straight = True
            values = [5, 4, 3, 2, 1]

    if is_straight and is_flush:
        return (8, values, "스트레이트 플러시")
    if 4 in count_values:
        return (7, values, "포카드")
    if 3 in count_values and 2 in count_values:
        return (6, values, "풀하우스")
    if is_flush:
        return (5, values, "플러시")
    if is_straight:
        return (4, values, "스트레이트")
    if 3 in count_values:
        return (3, values, "트리플")
    if count_values.count(2) >= 2:
        return (2, values, "투 페어")
    if 2 in count_values:
        return (1, values, "원 페어")
    return (0, values, "하이 카드")

async def win_by_fold(ctx, room):
    winner = active_players(room)[0]

    if winner != FURINA_ID:
        add_poker_money(winner, room["pot"])

    await ctx.send(
        f"🏆 모두 폴드!\n"
        f"승자: **{poker_name(ctx, winner)}**\n"
        f"획득: **{room['pot']}모라**"
    )

    room["dealer_index"] = (
        room["dealer_index"] + 1
    ) % len(room["players"])

    room["started"] = False
    room["stage"] = "lobby"
    
def hand_name_detail(cards):
    score = hand_score(cards)
    rank_type = score[0]

    ranks = [r for r, s in cards]
    values = [RANK_VALUE[r] for r, s in cards]

    value_to_rank = {v: r for r, v in RANK_VALUE.items()}
    counts = {}

    for r in ranks:
        counts[r] = counts.get(r, 0) + 1

    pairs = sorted(
        [RANK_VALUE[r] for r, c in counts.items() if c == 2],
        reverse=True
    )
    triples = sorted(
        [RANK_VALUE[r] for r, c in counts.items() if c == 3],
        reverse=True
    )
    quads = sorted(
        [RANK_VALUE[r] for r, c in counts.items() if c == 4],
        reverse=True
    )

    if rank_type == 8:
        high = max(score[1])
        return f"스트레이트 플러시, {value_to_rank[high]} 하이"
    if rank_type == 7:
        return f"포카드, {value_to_rank[quads[0]]}"
    if rank_type == 6:
        return f"풀하우스, {value_to_rank[triples[0]]} 풀"
    if rank_type == 5:
        high = max(values)
        return f"플러시, {value_to_rank[high]} 하이"
    if rank_type == 4:
        high = max(score[1])
        return f"스트레이트, {value_to_rank[high]} 하이"
    if rank_type == 3:
        return f"트리플, {value_to_rank[triples[0]]}"
    if rank_type == 2:
        return f"투 페어, {value_to_rank[pairs[0]]}와 {value_to_rank[pairs[1]]}"
    if rank_type == 1:
        return f"원 페어, {value_to_rank[pairs[0]]}"

    high = max(values)
    return f"하이 카드, {value_to_rank[high]}"

async def after_action(ctx, room):
    if len(active_players(room)) == 1:
        await win_by_fold(ctx, room)
        return

    if all_called(room):
        await advance_stage(ctx, room)
        return

    room["turn_index"] = next_index(
        room,
        room["turn_index"]
    )

    await ctx.send(
        f"현재 턴: **{poker_name(ctx, current_player(room))}**"
    )

    await furina_auto(ctx, room)
    
from itertools import combinations


SMALL_BLIND = 2
BIG_BLIND = 5
FURINA_ID = "FURINA_BOT"

def get_poker_money(user_id):
    return poker_money.get(str(user_id), 100)
    
def add_poker_money(user_id, amount):
    uid = str(user_id)

    poker_money[uid] = max(
        0,
        get_poker_money(uid) + int(amount)
    )

    save_data()
    return poker_money[uid]


def poker_stack(user_id):
    """현재 가진 돈. 푸리나는 봇 전용 가상 자금 사용."""
    if user_id == FURINA_ID:
        return FURINA_POKER_BANKROLL
    return get_poker_money(user_id)


def best_score(cards):
    return max(hand_score(list(combo)) for combo in combinations(cards, 5))


POKER_REACTION = {
    "check": [
        "푸리나: 체크라... 후후, 조용히 지나가 보자는 거지?",
        "푸리나: 음? 너무 얌전한데? 수상해...",
        "푸리나: 좋아, 이번엔 분위기를 좀 봐주지."
    ],
    "call": [
        "푸리나: 콜이라... 배짱은 있네?",
        "푸리나: 후후, 따라오는구나. 좋아, 무대는 계속된다!",
        "푸리나: 물러서지 않는 태도, 나쁘지 않아!"
    ],
    "raise_small": [
        "푸리나: 오? 살짝 올렸네? 간 보는 거야?",
        "푸리나: 그 정도 레이즈라면 귀엽게 봐줄 수 있지!",
        "푸리나: 후후, 조금씩 불을 붙이는구나?"
    ],
    "raise_big": [
        "푸리나: 뭐야, 갑자기 세게 나오네?!",
        "푸리나: 흐음... 허세인지 진짜인지 한번 봐야겠는데?",
        "푸리나: 대담하네. 무대가 재밌어졌어!"
    ],
    "allin": [
        "푸리나: 올인?! 지금 여기서 전부 건다고?!",
        "푸리나: 후후... 좋아. 네 각오만큼은 인정해줄게!",
        "푸리나: 갑자기 판을 뒤집으려 하다니, 제법인데?"
    ],
    "fold_user": [
        "푸리나: 도망치는 것도 전략이지. 후후, 오늘은 봐줄게!",
        "푸리나: 폴드? 현명한 판단일지도 모르지!",
        "푸리나: 어라? 벌써 물러나는 거야?"
    ],
    "furina_fold_weak": [
        "푸리나: ...이건 무대에 올릴 패가 아니네. **폴드!**",
        "푸리나: 흥, 지금은 물러나 주지. 다음 막을 기대하라고! **폴드!**",
        "푸리나: 이건 불길해... 괜히 돈 버리지 않겠어. **폴드!**"
    ],
    "furina_call": [
        "푸리나: 좋아, 받아주겠어. **콜 {need}모라!**",
        "푸리나: 후후, 그 정도 압박으론 날 못 밀어내. **콜 {need}모라!**",
        "푸리나: 여기서 물러나면 주연 실격이지. **콜 {need}모라!**"
    ],
    "furina_allin_call": [
        "푸리나: 네 올인? 좋아... 나도 전부 걸어주지! **올인 콜!**",
        "푸리나: 후후후... 이 패라면 도망칠 이유가 없지! **나도 올인!**",
        "푸리나: 무대의 클라이맥스다! 받아주겠어, **올인 콜!**"
    ],
    "furina_check": [
        "푸리나: 체크. ...뭔가 수상하지?",
        "푸리나: 이번엔 조용히 가볼까? **체크.**",
        "푸리나: 아직 막이 오르기 전이야. **체크.**"
    ],
    "furina_raise": [
        "푸리나: 후후... 분위기를 올려볼까? **레이즈 {amount}모라!**",
        "푸리나: 주연은 판을 흔드는 법이지! **레이즈 {amount}모라!**",
        "푸리나: 이 정도는 감당할 수 있겠지? **레이즈 {amount}모라!**"
    ],
    "furina_allin_raise": [
        "푸리나: 후후후... 지금이야말로 최고의 장면이지! **올인 {amount}모라!**",
        "푸리나: 이 패라면 망설일 필요 없어! 전부 걸겠어! **올인 {amount}모라!**",
        "푸리나: 물의 신의 배짱을 보여주지! **올인 {amount}모라!**"
    ],
    "furina_bluff": [
        "푸리나: 후후... 떨고 있는 건 아니겠지? **레이즈 {amount}모라!**",
        "푸리나: 내 패가 궁금해? 그럼 돈을 더 내봐! **레이즈 {amount}모라!**",
        "푸리나: 이건 연기일까, 진심일까? **레이즈 {amount}모라!**"
    ]
}

# =========================
# 포커 푸리나 AI 패치판
# =========================

FURINA_POKER_BANKROLL = 300
FURINA_MAX_RAISE = 80


def furina_say(kind, **kwargs):
    text = random.choice(POKER_REACTION[kind])
    return text.format(**kwargs)


def preflop_strength(cards):
    ranks = [r for r, s in cards]
    suits = [s for r, s in cards]
    values = sorted([RANK_VALUE[r] for r in ranks], reverse=True)

    high, low = values[0], values[1]
    gap = high - low

    strength = 0.15 + ((high + low) / 28) * 0.45

    if high == low:
        strength += 0.28 + high / 80

    if suits[0] == suits[1]:
        strength += 0.06

    if gap == 1:
        strength += 0.06
    elif gap == 2:
        strength += 0.035
    elif gap >= 5:
        strength -= 0.06

    if high >= 14:
        strength += 0.06
    elif high >= 13:
        strength += 0.04

    if high < 11 and low <= 6:
        strength -= 0.12

    return max(0.0, min(1.0, strength))


def made_hand_strength(cards):
    score = best_score(cards)
    rank_type = score[0]
    high = max(score[1]) if score[1] else 2

    base = {
        0: 0.18,
        1: 0.36,
        2: 0.56,
        3: 0.68,
        4: 0.76,
        5: 0.80,
        6: 0.88,
        7: 0.95,
        8: 1.0,
    }.get(rank_type, 0.18)

    return max(0.0, min(1.0, base + (high - 2) / 120))

def furina_luck_bonus(room):
    # 푸리나가 아주 살짝 더 자신감 있게 판단하게 만드는 보정
    stage = room.get("stage", "preflop")

    if stage == "preflop":
        return random.uniform(0.015, 0.045)

    return random.uniform(0.02, 0.06)

def furina_hand_strength(room):
    cards = room["hands"].get(FURINA_ID, [])
    community = room.get("community", [])

    if len(community) < 3:
        strength = preflop_strength(cards)
    else:
        strength = made_hand_strength(cards + community)

    strength += furina_luck_bonus(room)

    return max(0.0, min(1.0, strength))

def is_big_pressure(room, need):
    if need >= 50:
        return True
    if room["pot"] > 0 and need >= room["pot"] * 0.55:
        return True
    return False


def choose_furina_raise_amount(room, strength, all_in=False):
    current = room["current_bet"]

    if all_in:
        return FURINA_POKER_BANKROLL

    if strength >= 0.90:
        bump = random.choice([35, 45, 55, 70])
    elif strength >= 0.74:
        bump = random.choice([20, 25, 30, 40])
    elif strength >= 0.60:
        bump = random.choice([10, 15, 20])
    else:
        bump = random.choice([6, 8, 10])

    amount = current + bump
    amount = max(amount, current + 5)
    return min(amount, FURINA_MAX_RAISE)

def furina_decide_vs_bet(strength, pressure, need):
    if strength < 0.25:
        if random.random() < 0.30:
            return "fold"
    elif strength < 0.45:
        if random.random() < 0.10:
            return "fold"

    if need >= 100:
        if strength >= 0.94 and random.random() < 0.25:
            return "allin"
        return "call"

    if need >= 80:
        if strength >= 0.94 and random.random() < 0.25:
            return "allin"
        return "call"

    if need >= 50:
        if strength >= 0.92 and random.random() < 0.25:
            return "allin"
        return "call"

    if need >= 25:
        if strength >= 0.80 and random.random() < 0.15:
            return "raise"
        return "call"

    if need >= 10:
        if strength >= 0.75 and random.random() < 0.20:
            return "raise"
        return "call"

    if strength >= 0.93 and pressure and random.random() < 0.35:
        return "allin"

    return "call"


def furina_decide_no_bet(strength):
    if strength >= 0.95 and random.random() < 0.30:
        return "allin"

    if strength >= 0.78 and random.random() < 0.50:
        return "raise"

    if strength >= 0.64 and random.random() < 0.25:
        return "raise"

    if strength < 0.36 and random.random() < 0.10:
        return "bluff"

    return "check"
    

class SlashContext:
    def __init__(self, interaction: discord.Interaction):
        self.interaction = interaction
        self.author = interaction.user
        self.user = interaction.user
        self.guild = interaction.guild
        self.channel = interaction.channel

    async def reply(self, content=None, **kwargs):
        if not self.interaction.response.is_done():
            await self.interaction.response.send_message(content, **kwargs)
        else:
            await self.interaction.followup.send(content, **kwargs)

    async def send(self, content=None, **kwargs):
        if not self.interaction.response.is_done():
            await self.interaction.response.send_message(content, **kwargs)
        else:
            await self.interaction.followup.send(content, **kwargs)


def poker_name(ctx, user_id):
    if user_id == FURINA_ID:
        return "푸리나"

    member = ctx.guild.get_member(int(user_id))
    return member.display_name if member else str(user_id)


def new_poker_room(ctx):
    cid = str(ctx.channel.id)

    poker_rooms[cid] = {
        "host": str(ctx.author.id),
        "players": [FURINA_ID, str(ctx.author.id)],
        "dealer_index": 0,
        "started": False,
        "deck": [],
        "hands": {},
        "community": [],
        "pot": 0,
        "current_bet": 0,
        "bets": {},
        "folded": set(),
        "acted": set(),
        "turn_index": 0,
        "stage": "lobby",
        "all_in": set()
    }

    return poker_rooms[cid]


def get_room(ctx):
    return poker_rooms.get(str(ctx.channel.id))

def active_players(room):
    return [p for p in room["players"] if p not in room["folded"]]


def next_index(room, start):
    players = room["players"]

    for i in range(1, len(players) + 1):
        idx = (start + i) % len(players)

        if players[idx] not in room["folded"]:
            return idx

    return start


def current_player(room):
    return room["players"][room["turn_index"]]


def all_called(room):
    for p in active_players(room):
        if p in room.get("all_in", set()):
            continue

        if room["bets"].get(p, 0) != room["current_bet"]:
            return False

        if p not in room["acted"]:
            return False

    return True

async def advance_stage(ctx, room):
    room["acted"].clear()
    room["bets"] = {p: 0 for p in room["players"]}
    room["current_bet"] = 0

    if room["stage"] == "preflop":
        room["community"] += [room["deck"].pop() for _ in range(3)]
        room["stage"] = "flop"

    elif room["stage"] == "flop":
        room["community"].append(room["deck"].pop())
        room["stage"] = "turn"

    elif room["stage"] == "turn":
        room["community"].append(room["deck"].pop())
        room["stage"] = "river"

    else:
        await showdown(ctx, room)
        return

    room["turn_index"] = next_index(room, room["dealer_index"])

    await ctx.send(
        f"다음 라운드! 현재 단계: **{room['stage']}**\n"
        f"{stage_text(room)}\n"
        f"현재 턴: **{poker_name(ctx, current_player(room))}**"
    )

    await furina_auto(ctx, room)


async def showdown(ctx, room):
    alive = active_players(room)

    scores = {}
    for p in alive:
        scores[p] = best_score(room["hands"][p] + room["community"])

    best = max(scores.values())
    winners = [p for p, s in scores.items() if s == best]

    prize = room["pot"] // len(winners)

    for w in winners:
        if w != FURINA_ID:
            add_poker_money(w, prize)

    result_lines = []

    for p in room["players"]:
        hand = card_text(room["hands"][p])

        if p in room["folded"]:
            result_lines.append(f"{poker_name(ctx, p)}: **폴드** / 패: {hand}")
        else:
            result_lines.append(f"{poker_name(ctx, p)}: **{scores[p][2]}** / 패: {hand}")

    winner_names = ", ".join(poker_name(ctx, w) for w in winners)

    room["dealer_index"] = (room["dealer_index"] + 1) % len(room["players"])
    room["started"] = False
    room["stage"] = "lobby"

    await ctx.send(
        f"쇼다운!\n\n"
        f"{stage_text(room)}\n\n"
        + "\n".join(result_lines)
        + f"\n\n승자: **{winner_names}** / 획득: **{prize}모라**"
    )
    
def stage_text(room):
    cards = card_text(room["community"]) if room["community"] else "아직 없음"
    return f"공개 카드: **{cards}**\n판돈: **{room['pot']}모라**"
    
async def furina_auto(ctx, room):
    try:
        while room["started"] and current_player(room) == FURINA_ID:

            print("푸리나 턴 시작")

            # 이미 폴드/올인 상태면 다음 턴
            if (
                FURINA_ID in room["folded"]
                or FURINA_ID in room.get("all_in", set())
            ):
                room["turn_index"] = next_index(
                    room,
                    room["turn_index"]
                )
                continue

            need = room["current_bet"] - room["bets"].get(FURINA_ID, 0)

            strength = furina_hand_strength(room)
            pressure = is_big_pressure(room, need)

            print(
                f"need={need}, strength={strength:.2f}, pressure={pressure}"
            )

            # 상대가 이미 베팅한 경우
            if need > 0:
                decision = furina_decide_vs_bet(
                    strength,
                    pressure,
                    need
                )

                print("결정:", decision)

                if decision == "fold":
                    room["folded"].add(FURINA_ID)
                    room["acted"].add(FURINA_ID)

                    await ctx.send(
                        furina_say("furina_fold_weak")
                    )

                elif decision == "allin":
                    amount = choose_furina_raise_amount(
                        room,
                        strength,
                        all_in=True
                    )

                    pay = max(
                        0,
                        amount - room["bets"].get(FURINA_ID, 0)
                    )

                    room["current_bet"] = amount
                    room["bets"][FURINA_ID] = amount
                    room["pot"] += pay

                    room["acted"] = {FURINA_ID}
                    room.setdefault(
                        "all_in",
                        set()
                    ).add(FURINA_ID)

                    await ctx.send(
                        furina_say(
                            "furina_allin_call"
                        )
                    )

                else:  # call
                    room["pot"] += need
                    room["bets"][FURINA_ID] += need
                    room["acted"].add(FURINA_ID)

                    await ctx.send(
                        furina_say(
                            "furina_call",
                            need=need
                        )
                    )

            # 체크 상황
            else:
                decision = furina_decide_no_bet(
                    strength
                )

                print("결정:", decision)

                if decision == "allin":
                    amount = choose_furina_raise_amount(
                        room,
                        strength,
                        all_in=True
                    )

                    pay = max(
                        0,
                        amount - room["bets"].get(FURINA_ID, 0)
                    )

                    room["current_bet"] = amount
                    room["bets"][FURINA_ID] = amount
                    room["pot"] += pay

                    room["acted"] = {FURINA_ID}
                    room.setdefault(
                        "all_in",
                        set()
                    ).add(FURINA_ID)

                    await ctx.send(
                        furina_say(
                            "furina_allin_raise",
                            amount=amount
                        )
                    )

                elif decision in ("raise", "bluff"):
                    amount = choose_furina_raise_amount(
                        room,
                        strength
                    )

                    pay = max(
                        0,
                        amount - room["bets"].get(FURINA_ID, 0)
                    )

                    room["current_bet"] = amount
                    room["bets"][FURINA_ID] = amount
                    room["pot"] += pay

                    room["acted"] = {FURINA_ID}

                    await ctx.send(
                        furina_say(
                            "furina_bluff"
                            if decision == "bluff"
                            else "furina_raise",
                            amount=amount
                        )
                    )

                else:  # check
                    room["acted"].add(FURINA_ID)

                    await ctx.send(
                        furina_say("furina_check")
                    )

            # 승리 체크
            if len(active_players(room)) == 1:
                await win_by_fold(ctx, room)
                return

            # 라운드 종료
            if all_called(room):
                await advance_stage(ctx, room)
                return

            # 다음 턴
            room["turn_index"] = next_index(
                room,
                room["turn_index"]
            )

            await ctx.send(
                f"현재 턴: **{poker_name(ctx, current_player(room))}**"
            )

            # 푸리나 턴이면 연속 진행
            if current_player(room) != FURINA_ID:
                return

    except Exception as e:
        import traceback
        traceback.print_exc()

        await ctx.send(
            f"❌ 푸리나 AI 오류:\n```{e}```"
        )

@bot.tree.command(name="지갑", description="현재 보유한 모라를 확인합니다.", guild=GUILD)
async def poker_money_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"{interaction.user.mention}의 잔액: **{get_poker_money(interaction.user.id):,} 모라**"
    )


@bot.tree.command(name="돈받기", description="12시간마다 1500모라를 받습니다.", guild=GUILD)
async def poker_claim(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    now = datetime.now(timezone.utc)

    last = poker_last_claim.get(uid)
    if last and now - last < timedelta(hours=12):
        left = timedelta(hours=12) - (now - last)
        hours = int(left.total_seconds() // 3600)
        minutes = int((left.total_seconds() % 3600) // 60)

        await interaction.response.send_message(
            f"아직 못 받아! 남은 시간: **{hours}시간 {minutes}분**"
        )
        return

    poker_last_claim[uid] = now
    save_data()
    money = add_poker_money(uid, 1500)

    await interaction.response.send_message(
        f"1500모라 지급 완료! 현재 돈: **{money}모라**"
    )


@bot.tree.command(name="포커", description="포커 방을 생성합니다.", guild=GUILD)
async def poker_lobby(interaction: discord.Interaction):
    cid = str(interaction.channel.id)
    room = poker_rooms.get(cid)

    if room and room["started"]:
        await interaction.response.send_message("이미 이 채널에서 포커가 진행 중이야!")
        return

    poker_rooms[cid] = {
        "host": str(interaction.user.id),
        "players": [FURINA_ID, str(interaction.user.id)],
        "dealer_index": 0,
        "started": False,
        "deck": [],
        "hands": {},
        "community": [],
        "pot": 0,
        "current_bet": 0,
        "bets": {},
        "folded": set(),
        "acted": set(),
        "turn_index": 0,
        "stage": "lobby",
        "all_in": set()
    }

    await interaction.response.send_message(
        f"포커 방 생성!\n"
        f"참가자: **푸리나**, **{interaction.user.display_name}**\n\n"
        f"`/참가`로 참가 가능\n"
        f"`/시작`으로 시작"
    )


@bot.tree.command(name="참가", description="현재 포커 방에 참가합니다.", guild=GUILD)
async def poker_join(interaction: discord.Interaction):
    room = poker_rooms.get(str(interaction.channel.id))

    if not room:
        await interaction.response.send_message("포커 방이 없어! `/포커`로 먼저 만들어!")
        return

    if room["started"]:
        await interaction.response.send_message("이미 게임 시작했어!")
        return

    uid = str(interaction.user.id)

    if uid in room["players"]:
        await interaction.response.send_message("이미 참가했잖아!")
        return

    room["players"].append(uid)

    await interaction.response.send_message(
        f"{interaction.user.display_name} 참가 완료!\n"
        f"현재 참가자: **{len(room['players'])}명**"
    )

@bot.tree.command(name="시작", description="포커 게임을 시작합니다.", guild=GUILD)
async def poker_start(interaction: discord.Interaction):
    room = poker_rooms.get(str(interaction.channel.id))

    if room is None:
        await interaction.response.send_message("❌ 먼저 `/포커`로 방을 만들어!")
        return

    if room["started"]:
        await interaction.response.send_message("❌ 이미 게임이 진행 중이야!")
        return

    if len(room["players"]) < 2:
        await interaction.response.send_message("❌ 플레이어가 부족해!")
        return

    room["started"] = True
    room["stage"] = "preflop"

    room["deck"] = make_deck()
    room["community"] = []
    room["folded"] = set()
    room["acted"] = set()
    room["all_in"] = set()
    room["hands"] = {}
    room["bets"] = {}
    room["pot"] = 0
    room["current_bet"] = 0

    for p in room["players"]:
        room["hands"][p] = [room["deck"].pop(), room["deck"].pop()]
        room["bets"][p] = 0

    sb = room["players"][room["dealer_index"]]
    bb = room["players"][(room["dealer_index"] + 1) % len(room["players"])]

    sb_pay = min(SMALL_BLIND, poker_stack(sb))
    bb_pay = min(BIG_BLIND, poker_stack(bb))

    room["bets"][sb] = sb_pay
    room["bets"][bb] = bb_pay
    room["pot"] = sb_pay + bb_pay
    room["current_bet"] = bb_pay

    if sb_pay >= poker_stack(sb):
        room["all_in"].add(sb)

    if bb_pay >= poker_stack(bb):
        room["all_in"].add(bb)

    room["turn_index"] = next_index(room, room["dealer_index"])

    for p in room["players"]:
        if p == FURINA_ID:
            continue

        member = interaction.guild.get_member(int(p))
        if member is None:
            continue

        try:
            await member.send(
                f"🃏 포커 시작!\n"
                f"네 패: **{card_text(room['hands'][p])}**"
            )
        except:
            await interaction.channel.send(
                f"⚠️ {member.mention} DM을 보낼 수 없어. DM 설정을 확인해줘."
            )

    await interaction.response.send_message(
        "🃏 **포커 게임 시작!**\n"
        f"스몰 블라인드: **{poker_name(interaction, sb)} {sb_pay}모라**\n"
        f"빅 블라인드: **{poker_name(interaction, bb)} {bb_pay}모라**\n"
        f"판돈: **{room['pot']}모라**\n"
        f"현재 베팅: **{room['current_bet']}모라**\n"
        f"현재 턴: **{poker_name(interaction, current_player(room))}**"
    )

    class PokerInteractionCtx:
        def __init__(self, interaction):
            self.guild = interaction.guild
            self.channel = interaction.channel
            self.author = interaction.user

        async def send(self, *args, **kwargs):
            return await interaction.followup.send(*args, **kwargs)

    await furina_auto(PokerInteractionCtx(interaction), room)

@bot.tree.command(name="체크", description="포커에서 체크합니다.", guild=GUILD)
async def poker_check(interaction: discord.Interaction):
    ctx = SlashContext(interaction)
    room = get_room(ctx)
    uid = str(ctx.author.id)

    if not room or not room["started"]:
        await ctx.reply("진행 중인 포커가 없어!")
        return

    if current_player(room) != uid:
        await ctx.reply("지금 네 턴이 아니야!")
        return

    if room["current_bet"] > room["bets"].get(uid, 0):
        await ctx.reply("상대 베팅이 있어서 체크 못 해! `/콜` 또는 `/폴드` 해야 해.")
        return

    room["acted"].add(uid)
    await ctx.reply("체크!\n" + random.choice(POKER_REACTION["check"]))

    await after_action(ctx, room)

@bot.tree.command(name="콜", description="포커에서 콜합니다.", guild=GUILD)
async def poker_call(interaction: discord.Interaction):
    ctx = SlashContext(interaction)
    room = get_room(ctx)
    uid = str(ctx.author.id)

    if not room or not room["started"]:
        await ctx.reply("진행 중인 포커가 없어!")
        return

    if current_player(room) != uid:
        await ctx.reply("지금 네 턴이 아니야!")
        return

    need = room["current_bet"] - room["bets"].get(uid, 0)

    if need <= 0:
        await ctx.reply("콜할 금액이 없어. 체크 처리할게!")
        room["acted"].add(uid)
        await after_action(ctx, room)
        return

    if get_poker_money(uid) < need:
        await ctx.reply("돈이 부족해서 콜 못 해!")
        return

    add_poker_money(uid, -need)
    room["bets"][uid] += need
    room["pot"] += need
    room["acted"].add(uid)

    await ctx.reply(f"콜! **{need}모라** 지불.\n" + random.choice(POKER_REACTION["call"]))

    await after_action(ctx, room)

@bot.tree.command(name="레이즈", description="포커에서 레이즈합니다.", guild=GUILD)
async def poker_raise(interaction: discord.Interaction, amount: int = 10):
    ctx = SlashContext(interaction)
    room = get_room(ctx)
    uid = str(ctx.author.id)

    if not room or not room["started"]:
        await ctx.reply("진행 중인 포커가 없어!")
        return

    if current_player(room) != uid:
        await ctx.reply("지금 네 턴이 아니야!")
        return

    if amount <= room["current_bet"]:
        await ctx.reply(f"레이즈는 현재 베팅 **{room['current_bet']}모라**보다 커야 해!")
        return

    need = amount - room["bets"].get(uid, 0)

    if get_poker_money(uid) < need:
        await ctx.reply("돈이 부족해!")
        return

    add_poker_money(uid, -need)
    room["bets"][uid] = amount
    room["current_bet"] = amount
    room["pot"] += need
    room["acted"] = {uid}

    await ctx.reply(f"레이즈! 현재 베팅 **{amount}모라** / 판돈 **{room['pot']}모라**\n" + random.choice(POKER_REACTION["raise_big" if amount >= 50 else "raise_small"]))

    await after_action(ctx, room)

@bot.tree.command(name="폴드", description="포커에서 폴드합니다.", guild=GUILD)
async def poker_fold(interaction: discord.Interaction):
    ctx = SlashContext(interaction)
    room = get_room(ctx)
    uid = str(ctx.author.id)

    if not room or not room["started"]:
        await ctx.reply("진행 중인 포커가 없어!")
        return

    if current_player(room) != uid:
        await ctx.reply("지금 네 턴이 아니야!")
        return

    room["folded"].add(uid)
    room["acted"].add(uid)

    await ctx.reply("폴드!\n" + random.choice(POKER_REACTION["fold_user"]))

    await after_action(ctx, room)


@bot.tree.command(name="패", description="DM으로 내 패와 현재 족보를 확인합니다.", guild=GUILD)
async def poker_my_hand(interaction: discord.Interaction):
    ctx = SlashContext(interaction)
    room = get_room(ctx)
    uid = str(ctx.author.id)

    if not room or not room["started"]:
        await ctx.reply("진행 중인 포커가 없어!")
        return

    if uid not in room["players"]:
        await ctx.reply("너는 이번 포커에 참가 중이 아니야!")
        return

    if uid in room["folded"]:
        await ctx.reply("이미 폴드했잖아! 패 확인은 안 돼.")
        return

    player_cards = room["hands"][uid]
    community = room["community"]

    if len(community) >= 3:
        hand_name = hand_name_detail(player_cards + community)
    else:
        hand_name = hand_name_detail(player_cards)

    community_text = card_text(community) if community else "아직 없음"

    try:
        await ctx.author.send(
            f"후후, 네 패를 몰래 확인해줄게.\n\n"
            f"네 패: **{card_text(player_cards)}**\n"
            f"공개 카드: **{community_text}**\n"
            f"현재 족보: **{hand_name}**"
        )
        await ctx.reply("DM으로 네 패랑 현재 족보 알려줬어!")
    except discord.Forbidden:
        await ctx.reply("DM을 보낼 수 없어! 디스코드 개인 메시지 허용해줘.")


@bot.tree.command(name="모라랭킹", description="모라 랭킹을 확인합니다.", guild=GUILD)
async def poker_ranking(interaction: discord.Interaction):
    ctx = SlashContext(interaction)
    if not poker_money:
        await ctx.reply("아직 포커 돈 기록이 없어!")
        return

    ranking = sorted(
        poker_money.items(),
        key=lambda item: item[1],
        reverse=True
    )[:10]

    lines = []
    for i, (uid, money) in enumerate(ranking, start=1):
        lines.append(f"{i}위. **{poker_name(ctx, uid)}** - {money}모라")

    await ctx.reply("랭킹!\n" + "\n".join(lines))

@bot.tree.command(name="올인", description="포커에서 올인합니다.", guild=GUILD)
async def poker_all_in(interaction: discord.Interaction):
    ctx = SlashContext(interaction)
    room = get_room(ctx)
    uid = str(ctx.author.id)

    if not room or not room["started"]:
        await ctx.reply("진행 중인 포커가 없어!")
        return

    if current_player(room) != uid:
        await ctx.reply("지금 네 턴이 아니야!")
        return

    money = get_poker_money(uid)
    if money <= 0:
        await ctx.reply("올인할 돈이 없어!")
        return

    need_to_call = room["current_bet"] - room["bets"].get(uid, 0)
    new_total_bet = room["bets"].get(uid, 0) + money

    add_poker_money(uid, -money)
    room["bets"][uid] = new_total_bet
    room["pot"] += money
    room["acted"] = {uid}
    room.setdefault("all_in", set()).add(uid)

    if new_total_bet > room["current_bet"]:
        room["current_bet"] = new_total_bet
        await ctx.reply(f"올인! **{money}모라** 전부 밀어넣었다! 현재 베팅: **{new_total_bet}모라**\n" + random.choice(POKER_REACTION["allin"]))
    else:
        await ctx.reply(f"올인 콜! **{money}모라** 전부 넣었다!\n" + random.choice(POKER_REACTION["allin"]))

    await after_action(ctx, room)

@bot.command(name="기억")
async def memory_check(ctx):
    mem = user_memory.get(str(ctx.author.id), {})

    if not mem:
        await ctx.reply("아직 기억해둔 게 없어!")
        return

    name = mem.get("name")
    if name:
        await ctx.reply(f"내가 기억하는 네 이름은 **{name}**이야!")
    else:
        await ctx.reply("기억은 있는데 보여줄 만한 항목이 아직 없어!")
        
@bot.command(name="푸리나생일테스트")
@commands.has_permissions(administrator=True)
async def furina_birthday_test(ctx):
    channel = bot.get_channel(TEST_CHANNEL_ID)

    if channel is None:
        await ctx.send("공지 채널을 찾지 못했어. 채널 ID를 확인해줘!")
        return

    await channel.send(FURINA_BIRTHDAY_NOTICE)
    await ctx.send("푸리나 생일 자동 공지 테스트 완료!")
    
@bot.command(name="호감도")
async def favor_check(ctx):
    value = get_favor(ctx.author.id)

    stage = get_favor_stage(ctx.author.id) or "normal"

    await ctx.reply(
        f"{ctx.author.display_name}의 푸리나 호감도: **{value}** / 단계: **{stage}**"
    )

SERVER_ID = 1510681614919794868
CHANNEL_ID = 1512642190302777415
TIMEOUT_LOG_CHANNEL_ID = 1510693532208464052

ROLE_MESSAGES = {
    "오타쿠": "🎉 축하해! {user} 너도 이제 {role}가 되었구나!",
    "씹덕": "🎉 축하해! {user}이/가 {role}의 길에 입문했어!",
    "개씹덕": "🎉 축하해! 이제 {user}은/는 되돌릴 수 없는 {role} 단계에 도달했어!",
    "디창": "🎉 축하해! 우리 {user}이는 이제는 아예 디스코드에 영혼을 바친 {role}이 됐구나!",
    "화신": "🎉🎉 축하해!! 우리 서버에 {role}이 탄생했어! {user}, 화신이 된 소감이 어때! 꼭 말해줘!",
    "초보": "🎉 축하해! {user}가 {role} 역할을 달성했어! 드디어 첫걸음이구나?",
    "중수": "🎉 축하해! {user}가 {role} 역할을 얻었구나? 음성 채팅을 많이 하네!",
    "고수": "🎉 축하해! {user}가 {role} 역할을 얻어냈어! 너 음성 채팅을 정말 많이하는 구나!",
    "고인물": "🎉 축하해! {user}가 {role} 역할을 얻어냈네? 어떻게 했어! 아무튼 대단해!",
    "썩은물": "🎉 축하해! {user}가 {role} 역할을 얻어냈어!! 너 혹시 음성 채팅의 화신이니?",
    "석유": "🎉🎉 축하해!! 우리 서버가 산유국이 됐어! 우리 서버도 {role}가 나온다니, {user}, 넌 정말 대단해!" 
}

def format_duration(delta: timedelta):
    seconds = int(delta.total_seconds())

    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    parts = []
    if days:
        parts.append(f"{days}일")
    if hours:
        parts.append(f"{hours}시간")
    if minutes:
        parts.append(f"{minutes}분")
    if seconds:
        parts.append(f"{seconds}초")

    return " ".join(parts) if parts else "0초"


async def find_timeout_audit(guild, target):
    await asyncio.sleep(1)  # 감사 로그 반영 대기

    try:
        async for entry in guild.audit_logs(
            limit=5,
            action=discord.AuditLogAction.member_update
        ):
            if entry.target and entry.target.id == target.id:
                return entry
    except discord.Forbidden:
        return None

    return None
    

@bot.event
async def on_member_update(before, after):
    if after.guild.id != SERVER_ID:
        return

        # =========================
    # 타임아웃 로그
    # =========================
    before_timeout = before.timed_out_until
    after_timeout = after.timed_out_until

    if before_timeout != after_timeout:
        channel = after.guild.get_channel(TIMEOUT_LOG_CHANNEL_ID)

        if channel:
            audit = await find_timeout_audit(after.guild, after)

            moderator = audit.user if audit else None
            reason = audit.reason if audit and audit.reason else "사유 없음"

            now = datetime.now(timezone.utc)

            # 타임아웃이 새로 걸림
            if after_timeout is not None:
                duration = after_timeout - now

                # =========================
    # 타임아웃 로그
    # =========================
    before_timeout = before.timed_out_until
    after_timeout = after.timed_out_until

    if before_timeout != after_timeout:
        channel = after.guild.get_channel(TIMEOUT_LOG_CHANNEL_ID)

        if channel:
            audit = await find_timeout_audit(after.guild, after)

            moderator = audit.user if audit else None
            reason = audit.reason if audit and audit.reason else "사유 없음"

            now = datetime.now(timezone.utc)

            # 타임아웃이 새로 걸림
            if after_timeout is not None:
                duration = after_timeout - now

                embed = discord.Embed(
                    title="⛔ 타임아웃 적용",
                    color=discord.Color.orange()
                )

                embed.add_field(
                    name="걸린 유저",
                    value=f"{after.mention}\n`{after}` / `{after.id}`",
                    inline=False
                )

                embed.add_field(
                    name="처리한 관리자",
                    value=moderator.mention if moderator else "알 수 없음",
                    inline=False
                )

                embed.add_field(
                    name="기간",
                    value=format_duration(duration),
                    inline=True
                )

                embed.add_field(
                    name="해제 시간",
                    value=f"<t:{int(after_timeout.timestamp())}:F>\n<t:{int(after_timeout.timestamp())}:R>",
                    inline=True
                )

                embed.add_field(
                    name="사유",
                    value=reason,
                    inline=False
                )

                embed.set_thumbnail(url=after.display_avatar.url)
                embed.set_footer(text=f"User ID: {after.id}")

                await channel.send(embed=embed)

            # 타임아웃이 풀림
            else:
                embed = discord.Embed(
                    title="✅ 타임아웃 해제",
                    color=discord.Color.green()
                )

                embed.add_field(
                    name="해제된 유저",
                    value=f"{after.mention}\n`{after}` / `{after.id}`",
                    inline=False
                )

                embed.add_field(
                    name="처리한 관리자",
                    value=moderator.mention if moderator else "알 수 없음",
                    inline=False
                )

                embed.add_field(
                    name="사유",
                    value=reason,
                    inline=False
                )

                embed.set_thumbnail(url=after.display_avatar.url)
                embed.set_footer(text=f"User ID: {after.id}")

                await channel.send(embed=embed)
                
    before_roles = {r.id for r in before.roles}
    after_roles = {r.id for r in after.roles}

    added_role_ids = after_roles - before_roles

    for role_id in added_role_ids:
        new_role = after.guild.get_role(role_id)
        if new_role is None:
            continue

        if new_role.name not in ROLE_MESSAGES:
            continue

        channel = after.guild.get_channel(CHANNEL_ID)
        if channel is None:
            print("채널 못 찾음")
            return

        desc = ROLE_MESSAGES[new_role.name].format(
            user=after.mention,
            role=f"**{new_role.name}**"
        )

        embed = discord.Embed(
            title="🎉 역할 획득!",
            description=desc,
            color=new_role.color if new_role.color.value != 0 else discord.Color.gold()
        )

        embed.set_thumbnail(url=after.display_avatar.url)

        embed.add_field(
            name="획득한 역할",
            value=f"🏷️ {new_role.name}",
            inline=False
        )

        embed.set_footer(
            text=after.guild.name,
            icon_url=after.guild.icon.url if after.guild.icon else None
        )

        await channel.send(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(
                users=True,
                roles=False,
                everyone=False
            )
        )

        print(f"{after} → {new_role.name} 역할 획득 알림 전송")
            
print(get_time_key())
print(datetime.now())

CHARACTER_GACHA_COST = 160
WEAPON_GACHA_COST = 200
CHARACTER_TEN_GACHA_COST = CHARACTER_GACHA_COST * 10

@bot.tree.command(name="캐릭터뽑기", description="원신 캐릭터를 뽑는다", guild=GUILD)
@app_commands.describe(횟수="1 또는 10")
async def character_gacha(interaction: discord.Interaction, 횟수: int = 1):

    uid = str(interaction.user.id)

    if 횟수 not in [1, 10]:
        await interaction.response.send_message(
            "❌ 1회 또는 10회만 가능해.",
            ephemeral=True
        )
        return

    cost = CHARACTER_GACHA_COST * 횟수

    if get_primogems(uid) < cost:
        embed = discord.Embed(
            title="❌ 원석 부족",
            description=(
                f"필요 원석: **{cost:,}개**\n"
                f"보유 원석: **{get_primogems(uid):,}개**"
            ),
            color=discord.Color.red()
        )
    
        embed.set_footer(text="원석은 /원석교환 으로 획득할 수 있음.")
    
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
        return

    add_primogems(uid, -cost)

    user_chars = get_user_characters(uid)

    embed = discord.Embed(
        title="🌠 기원 진행 중",
        description="별빛이 하늘을 가르기 시작한다...",
        color=discord.Color.blue()
    )

    await interaction.response.send_message(embed=embed)

    msg = await interaction.original_response()

    await asyncio.sleep(1)

    embed.description = "🌌 운명의 문이 열리고 있다..."
    await msg.edit(embed=embed)

    await asyncio.sleep(1)

    embed.description = "💫 눈부신 빛이 폭발한다!"
    await msg.edit(embed=embed)

    await asyncio.sleep(1)

    results = []
    reward_lines = []

    highest_rarity = 4

    for i in range(횟수):

        name = draw_character(uid)
        info = GENSHIN_CHARACTERS[name]

        highest_rarity = max(
            highest_rarity,
            info["rarity"]
        )

        is_new = name not in user_chars

        if is_new:

            user_chars[name] = {
                "favor_exp": 0
            }

            results.append(
                f"🎉 {'⭐'*info['rarity']} **{name}** (신규)"
            )

        else:

            old_level = get_character_level(
                user_chars[name]["favor_exp"]
            )

            if old_level < 3:
                user_chars[name]["favor_exp"] += 1

            new_level = get_character_level(
                user_chars[name]["favor_exp"]
            )

            results.append(
                f"✨ {'⭐'*info['rarity']} **{name}** (중복)"
            )

            if old_level != new_level:

                reward = (
                    300
                    if new_level == 2
                    else 700
                )

                add_poker_money(uid, reward)

                reward_lines.append(
                    f"💖 {name} Lv.{old_level} → Lv.{new_level}\n"
                    f"💰 {reward:,} 모라"
                )
    add_quest_progress(uid, "gacha_count", 횟수)
    save_data()

    current_money = get_poker_money(uid)

    color = (
        discord.Color.gold()
        if highest_rarity == 5
        else discord.Color.purple()
    )

    title = (
        "🌟 5성 등장!"
        if highest_rarity == 5
        else "💜 기원 결과"
    )

    embed = discord.Embed(
        title=title,
        color=color
    )

    embed.add_field(
        name="🎊 획득 결과",
        value="\n".join(results),
        inline=False
    )

    embed.add_field(
        name="🎁 호감도 보상",
        value="\n".join(reward_lines)
        if reward_lines
        else "없음",
        inline=False
    )

    embed.add_field(
        name="💰 모라",
        value=f"{current_money:,}",
        inline=True
    )

    embed.add_field(
        name="🎲 뽑기 횟수",
        value=f"{횟수}회",
        inline=True
    )

    embed.set_footer(
        text=f"{interaction.user.display_name}의 기원 결과"
    )

    await msg.edit(embed=embed)

def get_user_weapons(user_id):
    uid = str(user_id)
    weapons.setdefault(uid, {})
    return weapons[uid]


def draw_signature_weapon():
    return random.choice(list(SIGNATURE_WEAPONS.keys()))


@bot.tree.command(name="전무뽑기", description="원신 캐릭터 전용 무기를 뽑는다", guild=GUILD)
@app_commands.describe(횟수="1 또는 10")
async def signature_weapon_gacha(interaction: discord.Interaction, 횟수: int = 1):
    uid = str(interaction.user.id)

    if 횟수 not in [1, 10]:
        await interaction.response.send_message(
            "❌ 1회 또는 10회만 가능해.",
            ephemeral=True
        )
        return

    cost = WEAPON_GACHA_COST * 횟수

    if get_poker_money(uid) < cost:
        await interaction.response.send_message(
            f"❌ 모라 부족!\n필요: **{cost:,}모라**\n보유: **{get_poker_money(uid):,}모라**",
            ephemeral=True
        )
        return

    add_poker_money(uid, -cost)

    user_weapons = get_user_weapons(uid)
    user_chars = get_user_characters(uid)

    results = []
    matched_lines = []

    for _ in range(횟수):
        char_name = draw_signature_weapon()
        weapon_name = SIGNATURE_WEAPONS[char_name]

        is_new = char_name not in user_weapons

        if is_new:
            user_weapons[char_name] = {
                "weapon": weapon_name,
                "count": 1
            }
            results.append(f"🌟 **{weapon_name}** - {char_name} 전용무기 (신규)")
        else:
            user_weapons[char_name]["count"] += 1
            results.append(f"✨ **{weapon_name}** - {char_name} 전용무기 (중복)")

        if char_name in user_chars:
            user_chars[char_name]["signature_weapon"] = weapon_name
            matched_lines.append(
                f"💬 **{char_name}** 전용무기 장착!\n"
                f"> {GENSHIN_CHARACTERS[char_name]['dialogue']}\n"
                f"> ✨ {weapon_name}을 손에 쥐자, 새로운 분위기가 느껴진다."
            )

    save_data()

    embed = discord.Embed(
        title="⚔️ 전용무기 기원 결과",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="획득 결과",
        value="\n".join(results),
        inline=False
    )

    embed.add_field(
        name="전용무기 보유 캐릭터 대사",
        value="\n\n".join(matched_lines) if matched_lines else "아직 해당 캐릭터를 보유하지 않아서 대사 추가 없음.",
        inline=False
    )

    embed.add_field(
        name="현재 모라",
        value=f"{get_poker_money(uid):,} 모라",
        inline=True
    )

    await interaction.response.send_message(embed=embed)
    
# =========================
# 원신 캐릭터 도감 UI
# =========================

CHARACTER_DEX_PAGE_SIZE = 5


class CharacterDexButton(discord.ui.Button):
    def __init__(self, dex_view, char_name: str):
        uid = str(dex_view.user_id)
        owned = characters.get(uid, {})
        is_owned = char_name in owned

        label = char_name if is_owned else "???"
        style = discord.ButtonStyle.success if is_owned else discord.ButtonStyle.secondary

        super().__init__(
            label=label,
            style=style,
            row=0
        )

        self.dex_view = dex_view
        self.char_name = char_name

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.dex_view.user_id):
            await interaction.response.send_message(
                "❌ 남의 도감 버튼 누르지 마!",
                ephemeral=True
            )
            return

        uid = str(interaction.user.id)
        user_chars = get_user_characters(uid)

        if self.char_name not in user_chars:
            await interaction.response.send_message(
                "❌ 아직 획득하지 못한 캐릭터야.",
                ephemeral=True
            )
            return

        info = GENSHIN_CHARACTERS[self.char_name]
        favor_exp = int(user_chars[self.char_name].get("favor_exp", 0))
        level = get_character_level(favor_exp)

        text = (
            f"{'⭐' * info['rarity']}\n"
            f"**{self.char_name}**\n\n"
            f"💖 호감도: **Lv.{level}/3**\n"
            f"중복 획득 횟수: **{favor_exp}회**"
        )

        weapon_name = user_chars[self.char_name].get("signature_weapon")

        if level >= 2:
            text += f"\n\n💬 **해금 대사**\n> {info['dialogue']}"
        else:
            text += "\n\n🔒 호감도 Lv.2부터 대사가 해금돼."

        if weapon_name:
            text += (
                f"\n\n⚔️ **전용무기 보유: {weapon_name}**\n"
                f"> 이 무기라면... 오늘의 무대도 완벽하게 장식할 수 있겠어."
            )
        else:
            text += "\n\n⚔️ 전용무기 없음"


class CharacterDexPrevButton(discord.ui.Button):
    def __init__(self, dex_view):
        super().__init__(
            label="◀",
            style=discord.ButtonStyle.primary,
            row=1,
            disabled=(dex_view.page <= 0)
        )
        self.dex_view = dex_view

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.dex_view.user_id):
            await interaction.response.send_message(
                "❌ 남의 도감 버튼 누르지 마!",
                ephemeral=True
            )
            return

        self.dex_view.page = max(0, self.dex_view.page - 1)
        self.dex_view.refresh_items()

        await interaction.response.edit_message(
            content=None,
            embed=self.dex_view.make_dex_embed(),
            view=self.dex_view
        )


class CharacterDexNextButton(discord.ui.Button):
    def __init__(self, dex_view):
        super().__init__(
            label="▶",
            style=discord.ButtonStyle.primary,
            row=1,
            disabled=(dex_view.page >= dex_view.max_page - 1)
        )
        self.dex_view = dex_view

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.dex_view.user_id):
            await interaction.response.send_message(
                "❌ 남의 도감 버튼 누르지 마!",
                ephemeral=True
            )
            return

        self.dex_view.page = min(self.dex_view.max_page - 1, self.dex_view.page + 1)
        self.dex_view.refresh_items()

        await interaction.response.edit_message(
            content=None,
            embed=self.dex_view.make_dex_embed(),
            view=self.dex_view
        )


class CharacterDexJumpButton(discord.ui.Button):
    def __init__(self, dex_view):
        super().__init__(
            label="페이지 이동",
            style=discord.ButtonStyle.secondary,
            row=1
        )
        self.dex_view = dex_view

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.dex_view.user_id):
            await interaction.response.send_message(
                "❌ 남의 도감 버튼 누르지 마!",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(CharacterDexJumpModal(self.dex_view))


class CharacterDexJumpModal(discord.ui.Modal, title="캐릭터 도감 페이지 이동"):
    page = discord.ui.TextInput(
        label="이동할 페이지 번호",
        placeholder="예: 2",
        required=True,
        max_length=4
    )

    def __init__(self, dex_view):
        super().__init__()
        self.dex_view = dex_view

    async def on_submit(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.dex_view.user_id):
            await interaction.response.send_message(
                "❌ 남의 도감 건드리지 마!",
                ephemeral=True
            )
            return

        try:
            page_num = int(str(self.page.value).strip())
        except ValueError:
            await interaction.response.send_message(
                "❌ 숫자로 입력해야 해.",
                ephemeral=True
            )
            return

        page_num = max(1, min(self.dex_view.max_page, page_num))
        self.dex_view.page = page_num - 1
        self.dex_view.refresh_items()

        await interaction.response.edit_message(
            content=self.dex_view.render(),
            view=self.dex_view
        )


class CharacterDexView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.user_id = str(user_id)
        self.page = 0
        self.search_keyword = None
        
        self.character_list = sorted(
            GENSHIN_CHARACTERS.keys(),
            key=lambda name: (-GENSHIN_CHARACTERS[name]["rarity"], name)
        )
        self.max_page = max(
            1,
            (len(self.character_list) + CHARACTER_DEX_PAGE_SIZE - 1) // CHARACTER_DEX_PAGE_SIZE
        )
        self.refresh_items()

    def refresh_items(self):
        self.clear_items()

        start = self.page * CHARACTER_DEX_PAGE_SIZE
        end = start + CHARACTER_DEX_PAGE_SIZE

        for char_name in self.character_list[start:end]:
            self.add_item(CharacterDexButton(self, char_name))

        self.add_item(CharacterDexPrevButton(self))
        self.add_item(CharacterDexJumpButton(self))
        self.add_item(CharacterDexNextButton(self))
        self.add_item(CharacterDexSearchButton(self))

        if self.search_keyword:
            self.add_item(CharacterDexResetButton(self))

        self.add_item(CharacterDexCloseButton(self))

    def render(self):
        user_chars = characters.get(self.user_id, {})
        total = len(self.character_list)
        owned_count = sum(1 for name in self.character_list if name in user_chars)

        start = self.page * CHARACTER_DEX_PAGE_SIZE
        end = start + CHARACTER_DEX_PAGE_SIZE

        text = (
            "📖 **원신 캐릭터 도감**\n\n"
            f"수집률: **{owned_count}/{total}**\n"
            f"페이지: **{self.page + 1}/{self.max_page}**\n\n"
        )

        for char_name in self.character_list[start:end]:
            info = GENSHIN_CHARACTERS[char_name]
            stars = "⭐" * info["rarity"]

            if char_name in user_chars:
                favor_exp = int(user_chars[char_name].get("favor_exp", 0))
                level = get_character_level(favor_exp)
                dialogue_state = "💬 대사 해금" if level >= 2 else "🔒 대사 잠김"

                text += (
                    f"✅ **{char_name}** {stars}\n"
                    f"호감도 Lv.{level}/3 | 중복 {favor_exp}회 | {dialogue_state}\n\n"
                )
            else:
                text += (
                    f"❌ **???** {stars}\n"
                    f"미획득\n\n"
                )

        text += "아래 버튼을 누르면 캐릭터 상세 정보를 볼 수 있어."
        return text


    def make_dex_embed(self):
        owned = characters.get(str(self.user_id), {})

        start = self.page * 5
        end = start + 5
        page_chars = self.character_list[start:end]

        total = len(self.character_list)
        owned_count = len(owned)
        percent = int((owned_count / total) * 100) if total else 0

        embed = discord.Embed(
            title="📖✨ 티바트 캐릭터 도감",
            description=(
                "수집한 캐릭터와 호감도를 확인할 수 있어.\n"
                f"**도감 진행도:** `{owned_count}/{total}` · **{percent}%**\n"
                f"**페이지:** `{self.page + 1}/{self.max_page}`"
            ),
            color=discord.Color.blurple()
        )
        
        desc = (
            "수집한 캐릭터와 호감도를 확인할 수 있어.\n"
            f"**도감 진행도:** `{owned_count}/{total}` · **{percent}%**\n"
            f"**페이지:** `{self.page + 1}/{self.max_page}`"
        )

        if self.search_keyword:
            desc += f"\n🔍 검색어: `{self.search_keyword}`"
    
        for char_name in page_chars:
            char = GENSHIN_CHARACTERS[char_name]
            rarity = char["rarity"]
            stars = "⭐" * rarity

            if char_name in owned:
                level = get_character_level(owned[char_name]["favor_exp"])

                if level >= 3:
                    heart = "💖💖💖"
                    status = "최대 호감도"
                elif level == 2:
                    heart = "💖💖🤍"
                    status = "대사 해금"
                else:
                    heart = "💖🤍🤍"
                    status = "보유 중"

                dialogue_status = "✅ 대사 열림" if level >= 2 else "🔒 Lv.2에 대사 해금"

                embed.add_field(
                    name=f"✅ {char_name}  {stars}",
                    value=(
                        f"호감도: **Lv.{level}/3**  {heart}\n"
                        f"상태: **{status}**\n"
                        f"{dialogue_status}"
                    ),
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"❌ 미획득 캐릭터  {stars}",
                    value=(
                        "이 캐릭터는 아직 도감에 등록되지 않았어.\n"
                        "`/캐릭터뽑기`로 획득 가능"
                    ),
                    inline=False
                )

        embed.set_footer(
            text="캐릭터 버튼을 누르면 상세 정보를 볼 수 있어 · ◀ 이동 ▶"
        )

        return embed

class CharacterDexCloseButton(discord.ui.Button):
    def __init__(self, dex_view):
        super().__init__(
            label="닫기",
            emoji="❌",
            style=discord.ButtonStyle.red
        )
        self.dex_view = dex_view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != int(self.dex_view.user_id):
            await interaction.response.send_message(
                "❌ 니 도감 아님.",
                ephemeral=True
            )
            return

        await interaction.response.edit_message(
            content="📕 도감을 닫았어.",
            embed=None,
            view=None
        )


class CharacterDexSearchButton(discord.ui.Button):
    def __init__(self, dex_view):
        super().__init__(
            label="검색",
            emoji="🔍",
            style=discord.ButtonStyle.primary,
            row=1
        )
        self.dex_view = dex_view

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.dex_view.user_id):
            await interaction.response.send_message("❌ 니 도감 아님.", ephemeral=True)
            return

        await interaction.response.send_modal(CharacterDexSearchModal(self.dex_view))


class CharacterDexSearchModal(discord.ui.Modal, title="캐릭터 이름 검색"):
    keyword = discord.ui.TextInput(
        label="검색할 캐릭터 이름",
        placeholder="예: 푸리나, 느비, 라이덴",
        required=True,
        max_length=20
    )

    def __init__(self, dex_view):
        super().__init__()
        self.dex_view = dex_view

    async def on_submit(self, interaction: discord.Interaction):
        word = str(self.keyword.value).strip().lower()

        all_chars = sorted(
            GENSHIN_CHARACTERS.keys(),
            key=lambda name: (-GENSHIN_CHARACTERS[name]["rarity"], name)
        )

        result = [
            name for name in all_chars
            if word in name.lower()
        ]

        if not result:
            await interaction.response.send_message(
                f"❌ `{self.keyword.value}` 검색 결과 없음.",
                ephemeral=True
            )
            return

        self.dex_view.search_keyword = str(self.keyword.value).strip()
        self.dex_view.character_list = result
        self.dex_view.page = 0
        self.dex_view.max_page = max(
            1,
            (len(self.dex_view.character_list) + CHARACTER_DEX_PAGE_SIZE - 1) // CHARACTER_DEX_PAGE_SIZE
        )
        self.dex_view.refresh_items()

        await interaction.response.edit_message(
            embed=self.dex_view.make_dex_embed(),
            view=self.dex_view
        )


class CharacterDexResetButton(discord.ui.Button):
    def __init__(self, dex_view):
        super().__init__(
            label="검색 초기화",
            emoji="↩️",
            style=discord.ButtonStyle.secondary,
            row=1
        )
        self.dex_view = dex_view

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.dex_view.user_id):
            await interaction.response.send_message("❌ 니 도감 아님.", ephemeral=True)
            return

        self.dex_view.search_keyword = None
        self.dex_view.character_list = sorted(
            GENSHIN_CHARACTERS.keys(),
            key=lambda name: (-GENSHIN_CHARACTERS[name]["rarity"], name)
        )
        self.dex_view.page = 0
        self.dex_view.max_page = max(
            1,
            (len(self.dex_view.character_list) + CHARACTER_DEX_PAGE_SIZE - 1) // CHARACTER_DEX_PAGE_SIZE
        )
        self.dex_view.refresh_items()

        await interaction.response.edit_message(
            embed=self.dex_view.make_dex_embed(),
            view=self.dex_view
        )
        
@bot.tree.command(name="캐릭터도감", description="내가 뽑은 원신 캐릭터 도감을 본다", guild=GUILD)
async def character_dex(interaction: discord.Interaction):
    view = CharacterDexView(interaction.user.id)

    await interaction.response.send_message(
        embed=view.make_dex_embed(),
        view=view
    )


# =========================
# 🏴 선택지 연계형 기지 털기
# =========================

active_raids = {}

RAID_BASES = {
    "보물사냥단 야영지": {"cost": 100, "start_danger": 10, "max_turn": 5},
    "우인단 보급기지": {"cost": 500, "start_danger": 25, "max_turn": 5},
    "밀수업자 창고": {"cost": 1000, "start_danger": 35, "max_turn": 5},
    "심연 교단 거점": {"cost": 3000, "start_danger": 55, "max_turn": 5},
    "북국은행 비밀금고": {"cost": 5000, "start_danger": 70, "max_turn": 6},
    "천리의 봉인 구역": {"cost": 10000, "start_danger": 85, "max_turn": 7},
}


def choice(label, success, reward=0, danger=0, next_tags=None, flag=None, end=False):
    return {
        "label": label,
        "success": success,
        "reward": reward,
        "danger": danger,
        "next_tags": next_tags or [],
        "flag": flag,
        "end": end
    }


RAID_RANDOM_CHOICES = {
    "보물사냥단 야영지": [
        choice("술통을 굴린다", 70, 180, 10, ["창고", "탈출"]),
        choice("코고는 단원 주머니를 턴다", 65, 250, 15, ["텐트", "탈출"]),
        choice("냄비를 훔친다", 90, 70, 0, ["텐트", "창고"]),
        choice("이상한 지도를 챙긴다", 75, 100, 0, ["창고"], "map"),
        choice("간고등어를 발견했다", 8, 500, -10, ["탈출"]),
    ],
    "우인단 보급기지": [
        choice("보급 수레에 숨는다", 75, 400, 5, ["창고", "탈출"]),
        choice("장교 주머니를 턴다", 50, 900, 25, ["지휘실", "탈출"]),
        choice("우인단 제복을 훔친다", 70, 200, 0, ["지휘실"], "uniform"),
        choice("수상한 버튼을 누른다", 35, 1500, 35, ["탈출"]),
        choice("푸리나 흉내를 낸다", 45, 777, -20, ["창고", "탈출"]),
    ],
    "밀수업자 창고": [
        choice("거래 장부를 훔친다", 65, 800, 10, ["금고", "탈출"], "ledger"),
        choice("수상한 상자를 연다", 55, 1200, 20, ["창고", "탈출"]),
        choice("지하 통로로 내려간다", 70, 400, 10, ["지하", "금고"]),
        choice("폭발물을 설치한다", 45, 2000, 35, ["탈출"]),
        choice("관리인에게 사기친다", 60, 900, 15, ["금고"]),
    ],
    "심연 교단 거점": [
        choice("마법서를 훔친다", 55, 1800, 25, ["제단", "탈출"]),
        choice("제단을 건드린다", 40, 3000, 45, ["심연문", "탈출"]),
        choice("심연 문양을 베껴간다", 65, 1000, 15, ["제단"], "rune"),
        choice("어둠 속 목소리를 따라간다", 45, 2500, 35, ["심연문"]),
        choice("고등어를 제물로 바친다", 12, 12000, -20, ["탈출"]),
    ],
    "북국은행 비밀금고": [
        choice("비밀 문서를 챙긴다", 55, 2500, 20, ["금고", "탈출"], "document"),
        choice("경보 장치를 해킹한다", 50, 1500, -20, ["금고"], "alarm_off"),
        choice("은행원인 척한다", 60, 2000, 15, ["금고"]),
        choice("금고 벽을 뜯는다", 35, 6000, 45, ["탈출"]),
        choice("타르탈리아 이름을 팔아본다", 40, 7000, -30, ["탈출"]),
    ],
    "천리의 봉인 구역": [
        choice("봉인된 유물을 조사한다", 70, 2500, 5, ["봉인실"]),
        choice("공중의 균열에 손을 댄다", 45, 8000, 35, ["심층"]),
        choice("남겨진 기록을 읽는다", 85, 1500, -10, ["봉인실"], "knowledge"),
        choice("정체불명의 빛을 따라간다", 60, 4000, 15, ["심층"]),
        choice("천리의 시선을 피한다", 50, 6000, 25, ["탈출"]),
    ]
}


RAID_SCENES = {
    "보물사냥단 야영지": {
        "입구": [
            {
                "text": "보물사냥단 야영지 입구에 도착했다. 경비 하나가 졸고 있다.",
                "fixed": [
                    choice("몰래 지나간다", 85, 80, 0, ["텐트", "창고"]),
                    choice("돌멩이를 던져 유인한다", 70, 120, 5, ["텐트"]),
                    choice("정면으로 당당히 걷는다", 45, 250, 20, ["창고", "탈출"]),
                ]
            }
        ],
        "텐트": [
            {
                "text": "텐트 안에서 코고는 소리가 들린다.",
                "fixed": [
                    choice("텐트를 뒤진다", 75, 300, 10, ["창고"]),
                    choice("자는 척 섞인다", 65, 150, 0, ["창고", "탈출"]),
                    choice("단원을 깨워서 속인다", 50, 400, 20, ["창고"]),
                ]
            }
        ],
        "창고": [
            {
                "text": "상자 더미가 쌓인 작은 창고를 발견했다.",
                "fixed": [
                    choice("가벼운 상자만 턴다", 90, 250, 0, ["탈출"]),
                    choice("큰 상자를 연다", 65, 600, 15, ["탈출"]),
                    choice("창고를 싹 턴다", 45, 1200, 35, ["탈출"]),
                ]
            }
        ],
        "탈출": [
            {
                "text": "이제 야영지에서 빠져나갈 시간이다.",
                "fixed": [
                    choice("숲길로 도망친다", 85, 0, 0, end=True),
                    choice("말을 훔쳐 달린다", 65, 300, 15, end=True),
                    choice("연막을 터뜨린다", 75, 100, 5, end=True),
                ]
            }
        ],
    },

    "우인단 보급기지": {
        "입구": [
            {
                "text": "우인단 보급기지 앞이다. 경비 둘이 검문 중이다.",
                "fixed": [
                    choice("제복 입은 척한다", 70, 300, 5, ["창고", "지휘실"]),
                    choice("뒷문을 찾는다", 80, 100, 0, ["창고"]),
                    choice("경비를 매수한다", 90, -200, 0, ["지휘실"]),
                ]
            }
        ],
        "창고": [
            {
                "text": "보급 창고에 들어왔다. 모라 상자와 식량 상자가 보인다.",
                "fixed": [
                    choice("모라 상자를 턴다", 65, 1200, 20, ["탈출"]),
                    choice("보급품을 챙긴다", 75, 800, 10, ["지휘실", "탈출"]),
                    choice("창고 문을 잠근다", 80, 300, -10, ["탈출"]),
                ]
            }
        ],
        "지휘실": [
            {
                "text": "지휘실에 들어왔다. 책상 위에 열쇠와 작전 문서가 있다.",
                "fixed": [
                    choice("열쇠를 훔친다", 70, 500, 5, ["창고"], "key"),
                    choice("문서를 훔친다", 65, 900, 10, ["탈출"]),
                    choice("책상을 통째로 뒤진다", 45, 1800, 30, ["탈출"]),
                ]
            }
        ],
        "탈출": [
            {
                "text": "기지 안쪽에서 발소리가 가까워진다. 탈출해야 한다.",
                "fixed": [
                    choice("보급 수레에 숨어 나간다", 80, 200, 0, end=True),
                    choice("정문으로 돌파한다", 55, 700, 25, end=True),
                    choice("담장을 넘는다", 70, 300, 10, end=True),
                ]
            }
        ],
    },

    "밀수업자 창고": {
        "입구": [
            {
                "text": "항구 근처 밀수업자 창고에 도착했다. 문이 잠겨 있다.",
                "fixed": [
                    choice("자물쇠를 딴다", 75, 200, 5, ["창고"]),
                    choice("창문으로 들어간다", 65, 300, 10, ["창고"]),
                    choice("지하 입구를 찾는다", 70, 100, 0, ["지하"]),
                ]
            }
        ],
        "창고": [
            {
                "text": "창고 안에는 정체불명의 상자들이 가득하다.",
                "fixed": [
                    choice("작은 상자를 연다", 85, 700, 0, ["금고", "탈출"]),
                    choice("수상한 상자를 연다", 55, 1800, 25, ["탈출"]),
                    choice("상자 표시를 해독한다", 70, 500, -5, ["금고"], "code"),
                ]
            }
        ],
        "지하": [
            {
                "text": "지하 통로에서 밀수품 거래 흔적을 발견했다.",
                "fixed": [
                    choice("거래품을 훔친다", 65, 1600, 20, ["금고"]),
                    choice("조용히 지나간다", 90, 300, 0, ["금고"]),
                    choice("벽장을 열어본다", 60, 1100, 15, ["탈출"]),
                ]
            }
        ],
        "금고": [
            {
                "text": "숨겨진 금고를 발견했다.",
                "fixed": [
                    choice("암호를 맞춘다", 60, 2500, 15, ["탈출"]),
                    choice("강제로 연다", 45, 4000, 35, ["탈출"]),
                    choice("금고 위치만 기록한다", 95, 800, 0, ["탈출"]),
                ]
            }
        ],
        "탈출": [
            {
                "text": "창고 밖에서 인기척이 들린다.",
                "fixed": [
                    choice("뒷문으로 나간다", 80, 0, 0, end=True),
                    choice("배에 숨어 도망친다", 65, 900, 15, end=True),
                    choice("상자를 방패로 삼는다", 60, 1200, 20, end=True),
                ]
            }
        ],
    },

    "심연 교단 거점": {
        "입구": [
            {
                "text": "심연 교단 거점 앞이다. 공기가 심상치 않다.",
                "fixed": [
                    choice("조용히 진입한다", 75, 600, 10, ["제단"]),
                    choice("문양을 조사한다", 65, 1000, 15, ["제단"], "rune"),
                    choice("정면의 문을 연다", 45, 2200, 35, ["심연문"]),
                ]
            }
        ],
        "제단": [
            {
                "text": "이상한 제단이 희미하게 빛나고 있다.",
                "fixed": [
                    choice("제단 주변을 뒤진다", 70, 1800, 20, ["심연문", "탈출"]),
                    choice("제단을 부순다", 50, 3500, 45, ["탈출"]),
                    choice("기도하는 척한다", 60, 1200, 10, ["심연문"]),
                ]
            }
        ],
        "심연문": [
            {
                "text": "거대한 심연의 문이 눈앞에 나타났다.",
                "fixed": [
                    choice("틈새로 들어간다", 55, 3500, 35, ["탈출"]),
                    choice("문 옆 보관함을 턴다", 65, 2500, 25, ["탈출"]),
                    choice("그냥 도망칠 준비를 한다", 90, 500, -10, ["탈출"]),
                ]
            }
        ],
        "탈출": [
            {
                "text": "뒤에서 알 수 없는 목소리가 들린다. 빨리 빠져나가야 한다.",
                "fixed": [
                    choice("빛이 보이는 곳으로 뛴다", 75, 0, 0, end=True),
                    choice("심연 포탈로 뛰어든다", 45, 5000, 40, end=True),
                    choice("왔던 길로 되돌아간다", 85, 300, 5, end=True),
                ]
            }
        ],
    },

    "북국은행 비밀금고": {
        "입구": [
            {
                "text": "북국은행 비밀금고 구역에 잠입했다. 감시 장치가 돌아가고 있다.",
                "fixed": [
                    choice("감시 장치를 피한다", 70, 1000, 10, ["금고"]),
                    choice("은행원인 척한다", 60, 1800, 20, ["문서실"]),
                    choice("경보선을 자른다", 50, 2500, 35, ["금고"], "alarm_off"),
                ]
            }
        ],
        "문서실": [
            {
                "text": "문서실에 들어왔다. 고급 계약서들이 잔뜩 꽂혀 있다.",
                "fixed": [
                    choice("계약서를 훔친다", 65, 3000, 25, ["금고"]),
                    choice("장부를 조작한다", 55, 4500, 35, ["탈출"]),
                    choice("도장만 챙긴다", 80, 1500, 5, ["금고"], "stamp"),
                ]
            }
        ],
        "금고": [
            {
                "text": "마침내 비밀금고 앞에 도착했다.",
                "fixed": [
                    choice("암호를 해독한다", 55, 7000, 30, ["탈출"]),
                    choice("도장으로 승인 처리한다", 70, 4000, 10, ["탈출"]),
                    choice("금고를 강제로 뜯는다", 35, 12000, 55, ["탈출"]),
                ]
            }
        ],
        "탈출": [
            {
                "text": "은행 전체가 소란스러워졌다. 탈출 루트를 골라야 한다.",
                "fixed": [
                    choice("직원 출입구로 나간다", 70, 1000, 10, end=True),
                    choice("창문으로 뛰어내린다", 55, 3000, 30, end=True),
                    choice("손님인 척 걸어나간다", 65, 2000, 20, end=True),
                ]
            }
        ],
    },
    
    "천리의 봉인 구역": {
        "입구": [
            {
                "text": "하늘에 균열이 생기며 봉인된 공간이 모습을 드러냈다.",
                "fixed": [
                    choice("균열 안으로 들어간다", 65, 3000, 15, ["봉인실"]),
                    choice("주변 문양을 조사한다", 80, 1000, -10, ["봉인실"], "seal"),
                    choice("힘으로 봉인을 부순다", 40, 7000, 35, ["심층"]),
                ]
            }
        ],

        "봉인실": [
            {
                "text": "수수께끼의 유물이 공중에 떠 있다.",
                "fixed": [
                    choice("유물을 챙긴다", 55, 6000, 20, ["심층"]),
                    choice("에너지를 흡수한다", 45, 10000, 35, ["탈출"]),
                    choice("기록만 남긴다", 90, 2000, 0, ["탈출"]),
                ]
            }
        ],

        "심층": [
            {
                "text": "알 수 없는 존재의 시선이 느껴진다.",
                "fixed": [
                    choice("정체를 확인한다", 35, 15000, 40, ["탈출"]),
                    choice("보물을 챙겨 도망친다", 70, 5000, 15, ["탈출"]),
                    choice("숨죽여 기다린다", 85, 1500, -10, ["탈출"]),
                ]
            }
        ],

        "탈출": [
            {
                "text": "봉인 구역이 무너지기 시작한다!",
                "fixed": [
                    choice("균열로 뛰어든다", 75, 0, 0, end=True),
                    choice("유물을 버리고 도망친다", 95, -2000, -20, end=True),
                    choice("끝까지 챙긴다", 40, 12000, 40, end=True),
                 ]
             }
         ],
    },
}


def pick_raid_scene(base_name, tags):
    tag = random.choice(tags)
    scene = random.choice(RAID_SCENES[base_name][tag])
    return tag, scene


def make_raid_choices(base_name, scene):
    fixed = scene["fixed"][:]
    random_pool = RAID_RANDOM_CHOICES[base_name]
    random_choices = random.sample(random_pool, 2)
    result = fixed + random_choices
    random.shuffle(result)
    return result


class RaidView(discord.ui.View):
    def __init__(self, user_id, base_name, state):
        super().__init__(timeout=120)
        self.user_id = str(user_id)
        self.base_name = base_name
        self.state = state

        for i, c in enumerate(state["choices"]):
            self.add_item(RaidButton(i, c["label"]))

    async def interaction_check(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ 네 레이드 아님.", ephemeral=True)
            return False
        return True


class RaidButton(discord.ui.Button):
    def __init__(self, index, label):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.secondary
        )
        self.index = index

    async def callback(self, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        state = active_raids.get(uid)

        if not state:
            await interaction.response.edit_message(
                content="❌ 이미 끝난 레이드야.",
                embed=None,
                view=None
            )
            return

        base_name = state["base"]
        selected = state["choices"][self.index]

        success_rate = selected["success"]

        if "map" in state["flags"]:
            success_rate += 5
        if "uniform" in state["flags"] and base_name == "우인단 보급기지":
            success_rate += 10
        if "alarm_off" in state["flags"]:
            success_rate += 10

        success_rate -= max(0, state["danger"] // 10)
        success_rate = max(5, min(95, success_rate))

        success = random.randint(1, 100) <= success_rate

        result_lines = [
            f"선택: **{selected['label']}**",
            f"성공률: **{success_rate}%**"
        ]

        if success:
            reward = selected["reward"]

            if reward < 0:
                state["reward"] += reward
                result_lines.append(f"💸 비용 발생: **{abs(reward):,}모라**")
            else:
                state["reward"] += reward
                result_lines.append(f"✅ 성공! **{reward:,}모라** 확보!")

            state["danger"] += selected["danger"]

            if selected.get("flag"):
                state["flags"].add(selected["flag"])
                result_lines.append(f"✨ 상태 획득: `{selected['flag']}`")

        else:
            penalty = random.randint(100, 500)
            state["danger"] += selected["danger"] + 20
            state["reward"] -= penalty
            result_lines.append(f"❌ 실패! 도주 과정에서 **{penalty:,}모라** 손실!")
            result_lines.append("⚠️ 위험도 +20")

        state["danger"] = max(0, state["danger"])
        state["turn"] += 1

        should_end = (
            selected.get("end")
            or state["turn"] >= state["max_turn"]
            or state["danger"] >= 100
        )

        if should_end:
            final_reward = state["reward"]

            if state["danger"] >= 100:
                loss = random.randint(500, 1500)
                final_reward -= loss
                result_lines.append(f"🚨 위험도가 100을 넘었다! 추가 손실 **{loss:,}모라**!")

            if final_reward > 0 and random.random() < 0.1:
                bonus = random.randint(500, 3000)
                final_reward += bonus
                result_lines.append(f"🌟 대성공! 숨겨진 금고 발견! **+{bonus:,}모라**")

            add_poker_money(uid, final_reward)
            active_raids.pop(uid, None)

            embed = discord.Embed(
                title=f"🏴 {base_name} 레이드 종료",
                description="\n".join(result_lines),
                color=discord.Color.gold() if final_reward >= 0 else discord.Color.red()
            )

            embed.add_field(
                name="최종 정산",
                value=f"{final_reward:+,} 모라",
                inline=True
            )
            embed.add_field(
                name="현재 모라",
                value=f"{get_poker_money(uid):,} 모라",
                inline=True
            )
            embed.add_field(
                name="최종 위험도",
                value=f"{state['danger']}%",
                inline=True
            )

            await interaction.response.edit_message(embed=embed, view=None)
            return

        next_tags = selected["next_tags"] or ["탈출"]
        tag, scene = pick_raid_scene(base_name, next_tags)
        state["scene_tag"] = tag
        state["scene_text"] = scene["text"]
        state["choices"] = make_raid_choices(base_name, scene)

        embed = make_raid_embed(base_name, state, result_lines)
        view = RaidView(uid, base_name, state)

        await interaction.response.edit_message(embed=embed, view=view)

def get_required_exp(level):
    base = level * 100

    # 20 -> 21, 40 -> 41, 60 -> 61 때만 추가 배율
    if level % 20 == 0:
        multiplier = (level // 20) + 1
        return base * multiplier

    return base
    

def make_raid_embed(base_name, state, result_lines=None):
    desc = ""

    if result_lines:
        desc += "\n".join(result_lines)
        desc += "\n\n"

    desc += f"**{state['scene_text']}**"

    embed = discord.Embed(
        title=f"🏴 {base_name} 털기",
        description=desc,
        color=discord.Color.dark_gold()
    )

    embed.add_field(
        name="진행도",
        value=f"{state['turn']}/{state['max_turn']}",
        inline=True
    )
    embed.add_field(
        name="확보한 모라",
        value=f"{state['reward']:,}",
        inline=True
    )
    embed.add_field(
        name="위험도",
        value=f"{state['danger']}%",
        inline=True
    )

    flags = ", ".join(state["flags"]) if state["flags"] else "없음"

    embed.add_field(
        name="상태",
        value=flags,
        inline=False
    )

    embed.set_footer(text="버튼 선택지 5개 = 고정 3개 + 랜덤 2개")
    return embed


@bot.tree.command(name="기지털기", description="적 기지를 털어서 모라를 불린다", guild=GUILD)
@app_commands.describe(기지="털 기지 이름")
@app_commands.choices(
    기지=[
        app_commands.Choice(name="보물사냥단 야영지", value="보물사냥단 야영지"),
        app_commands.Choice(name="우인단 보급기지", value="우인단 보급기지"),
        app_commands.Choice(name="밀수업자 창고", value="밀수업자 창고"),
        app_commands.Choice(name="심연 교단 거점", value="심연 교단 거점"),
        app_commands.Choice(name="북국은행 비밀금고", value="북국은행 비밀금고"),
        app_commands.Choice(name="천리의 봉인 구역", value="천리의 봉인 구역"),
    ]
)
async def raid_base(interaction: discord.Interaction, 기지: app_commands.Choice[str]):
    uid = str(interaction.user.id)
    base_name = 기지.value
    base = RAID_BASES[base_name]

    if uid in active_raids:
        await interaction.response.send_message(
            "❌ 이미 진행 중인 기지 털기가 있어!",
            ephemeral=True
        )
        return

    money = get_poker_money(uid)

    if money < base["cost"]:
        await interaction.response.send_message(
            f"❌ 모라 부족!\n필요: **{base['cost']:,}모라**\n보유: **{money:,}모라**",
            ephemeral=True
        )
        return

    add_poker_money(uid, -base["cost"])

    tag, scene = pick_raid_scene(base_name, ["입구"])

    state = {
        "base": base_name,
        "turn": 0,
        "max_turn": base["max_turn"],
        "danger": base["start_danger"],
        "reward": 0,
        "flags": set(),
        "scene_tag": tag,
        "scene_text": scene["text"],
        "choices": make_raid_choices(base_name, scene),
    }

    active_raids[uid] = state

    embed = make_raid_embed(base_name, state)
    embed.add_field(
        name="입장 비용",
        value=f"-{base['cost']:,} 모라",
        inline=True
    )

    await interaction.response.send_message(
        embed=embed,
        view=RaidView(uid, base_name, state)
    )

@bot.tree.command(
    name="돈주기",
    description="유저에게 모라를 지급한다",
    guild=GUILD
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    대상="지급할 유저",
    금액="지급할 모라"
)
async def money_give(
    interaction: discord.Interaction,
    대상: discord.Member,
    금액: int
):
    if 금액 <= 0:
        await interaction.response.send_message(
            "❌ 1 이상 입력해야 함.",
            ephemeral=True
        )
        return

    add_poker_money(대상.id, 금액)

    await interaction.response.send_message(
        f"✅ {대상.mention}에게 **{금액:,}모라** 지급 완료!\n"
        f"현재 보유 모라: **{get_poker_money(대상.id):,}모라**"
    )

@bot.tree.command(
    name="돈차감",
    description="유저의 모라를 차감한다",
    guild=GUILD
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    대상="차감할 유저",
    금액="차감할 모라"
)
async def money_remove(
    interaction: discord.Interaction,
    대상: discord.Member,
    금액: int
):
    if 금액 <= 0:
        await interaction.response.send_message(
            "❌ 1 이상 입력해야 함.",
            ephemeral=True
        )
        return

    uid = str(대상.id)

    current = get_poker_money(uid)
    removed = min(current, 금액)

    poker_money[uid] = current - removed
    save_data()

    await interaction.response.send_message(
        f"💸 {대상.mention}에게서 **{removed:,}모라** 차감 완료!\n"
        f"현재 보유 모라: **{get_poker_money(uid):,}모라**"
    )

@bot.tree.command(name="기부", description="다른 유저에게 모라를 보낸다", guild=GUILD)
@app_commands.describe(
    대상="돈을 받을 사람",
    금액="보낼 금액"
)
async def donate(
    interaction: discord.Interaction,
    대상: discord.Member,
    금액: int
):
    sender_id = str(interaction.user.id)
    target_id = str(대상.id)

    if 대상.bot:
        await interaction.response.send_message(
            "❌ 봇에게는 기부할 수 없음.",
            ephemeral=True
        )
        return

    if 대상.id == interaction.user.id:
        await interaction.response.send_message(
            "❌ 자기 자신에게는 보낼 수 없음.",
            ephemeral=True
        )
        return

    if 금액 <= 0:
        await interaction.response.send_message(
            "❌ 1모라 이상 입력해야 함.",
            ephemeral=True
        )
        return

    current_money = get_poker_money(sender_id)

    if current_money < 금액:
        await interaction.response.send_message(
            f"❌ 돈 부족!\n현재 보유: **{current_money:,} 모라**",
            ephemeral=True
        )
        return

    remove_poker_money(sender_id, 금액)
    add_poker_money(target_id, 금액)

    await interaction.response.send_message(
        f"💸 **{interaction.user.mention}** → **{대상.mention}**\n"
        f"**{금액:,} 모라** 기부 완료!"
    )

voice_inactive = {}     # {user_id: 헤드셋 끈 시간}
voice_warned = {}       # {user_id: 최종 경고 DM 보낸 시간}
voice_snooze = {}       # {user_id: 유예 종료 시간}
voice_pending_on = {}   # {user_id: 3분 안에 헤드셋 켜야 하는 종료 시간}

SNOOZE_TIME = timedelta(hours=5)
SLEEP_TIME = timedelta(hours=8)
HEADSET_ON_TIME = timedelta(minutes=3)
FINAL_WARNING_TIME = timedelta(minutes=10)

def get_voice_member(user_id):
    for guild in bot.guilds:
        member = guild.get_member(user_id)
        if member:
            return member
    return None
    
async def check_voice_state(self, interaction):
    member = get_voice_member(self.user_id)

    if not member or not member.voice:
        await interaction.response.edit_message(
            content="이미 음성 채널에 없어서 처리할 게 없어.",
            view=None
        )
        return None

    if not is_headset_off(member.voice):
        voice_inactive.pop(self.user_id, None)
        voice_warned.pop(self.user_id, None)
        voice_snooze.pop(self.user_id, None)
        voice_pending_on.pop(self.user_id, None)

        await interaction.response.edit_message(
            content="이미 헤드셋 켜져 있어서 경고 취소했어.",
            view=None
        )
        return None

    return member
    

def is_headset_off(state):
    return state.self_deaf or state.deaf


class VoiceWarningView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    async def user_check(self, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("이 버튼은 본인만 누를 수 있어.", ephemeral=True)
            return False
        return True

    async def check_voice_state(self, interaction):
        member = get_voice_member(self.user_id)

        if not member or not member.voice:
            await interaction.response.edit_message(
                content="이미 음성 채널에 없어서 처리할 게 없어.",
                view=None
            )
            return None

        if not is_headset_off(member.voice):
            voice_inactive.pop(self.user_id, None)
            voice_warned.pop(self.user_id, None)
            voice_snooze.pop(self.user_id, None)
            voice_pending_on.pop(self.user_id, None)

            await interaction.response.edit_message(
                content="이미 헤드셋 켜져 있어서 경고 취소했어.",
                view=None
            )
            return None

        return member
            
    @discord.ui.button(label="✅ 확인하고 5시간 유예", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.user_check(interaction):
            return

        member = await self.check_voice_state(interaction)
        if member is None:
            return
        
        until = datetime.now(KST) + SNOOZE_TIME

        voice_snooze[self.user_id] = until
        voice_warned.pop(self.user_id, None)
        voice_pending_on.pop(self.user_id, None)

        await interaction.response.edit_message(
            content=(
                "✅ 확인 완료!\n"
                "앞으로 **5시간 동안 경고가 오지 않아.**\n"
                f"유예 종료: **{until.strftime('%H:%M')}**"
            ),
            view=None
        )

    @discord.ui.button(label="😴 숙면 모드", style=discord.ButtonStyle.primary)
    async def sleep_mode(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.user_check(interaction):
            return

        member = await self.check_voice_state(interaction)
        if member is None:
            return
        
        until = datetime.now(KST) + SLEEP_TIME

        voice_snooze[self.user_id] = until
        voice_warned.pop(self.user_id, None)
        voice_pending_on.pop(self.user_id, None)

        await interaction.response.edit_message(
            content=(
                "😴 숙면 모드 켰어.\n"
                "**8시간 동안** 경고/퇴장을 비활성화 할게.\n"
                f"종료 시간: **{until.strftime('%H:%M')}**"
            ),
            view=None
        )

    @discord.ui.button(label="🎧 헤드셋 킬게요", style=discord.ButtonStyle.secondary)
    async def headset_on_soon(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.user_check(interaction):
            return

        member = await self.check_voice_state(interaction)
        if member is None:
            return

        until = datetime.now(KST) + HEADSET_ON_TIME
        voice_pending_on[self.user_id] = until

        await interaction.response.edit_message(
            content=(
                "🎧 알겠어.\n"
                "**3분 안에 듣기 끔을 해제**해줘.\n"
                "그동안 안 키면 DM을 한 번 더 보낼 예정이야.**"
            ),
            view=None
        )

    @discord.ui.button(label="🛑 종료", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("이 버튼은 본인만 누를 수 있어.", ephemeral=True)
            return

        for guild in bot.guilds:
            member = guild.get_member(self.user_id)

            if member and member.voice:
                await member.move_to(None)

                voice_inactive.pop(self.user_id, None)
                voice_warned.pop(self.user_id, None)
                voice_snooze.pop(self.user_id, None)
                voice_pending_on.pop(self.user_id, None)

                await interaction.response.edit_message(
                    content="🛑 음성 채널 연결을 종료했어.",
                    view=None
                )
                return

        await interaction.response.edit_message(
            content="이미 음성 채널에 없어서 종료할 게 없어.",
            view=None
        )


async def send_first_voice_dm(member):
    uid = member.id
    now = datetime.now(KST)

    try:
        await member.send(
            "⚠️ 지금 음성채널에서 **듣기 끔 상태**야.\n\n"
            "아래 버튼 중 하나를 선택해줘.\n"
            "- ✅ 확인하고 5시간 유예\n"
            "- 😴 숙면 모드\n"
            "- 🎧 헤드셋 킬게요\n\n"
            "헤드셋을 켤 거면 **3분 안에 헤드셋을 해제**해줘.",
            view=VoiceWarningView(uid)
        )
        print(f"[VoiceKick] {member} 1차 DM 전송 완료")

    except discord.Forbidden:
        print(f"[VoiceKick] {member} DM 전송 실패: DM 차단됨")

    except Exception as e:
        print(f"[VoiceKick] {member} 1차 DM 오류: {e}")

    voice_inactive[uid] = now


async def send_final_voice_dm(member):
    uid = member.id
    now = datetime.now(KST)

    try:
        await member.send(
            "⚠️ 아직도 **듣기 끔 상태**야.\n\n"
            "이제 **10분 안에 반응 없으면** 자동으로 연결을 끊을게.\n"
            "살려면 버튼을 눌러줘.",
            view=VoiceWarningView(uid)
        )
        print(f"[VoiceKick] {member} 2차 DM 전송 완료")

    except discord.Forbidden:
        print(f"[VoiceKick] {member} 2차 DM 실패: DM 차단됨")

    except Exception as e:
        print(f"[VoiceKick] {member} 2차 DM 오류: {e}")

    voice_warned[uid] = now
    voice_pending_on.pop(uid, None)


async def disconnect_with_countdown(member):
    try:
        await member.send("3")
        await asyncio.sleep(1)
        await member.send("2")
        await asyncio.sleep(1)
        await member.send("1")
        await asyncio.sleep(1)
        await member.move_to(None)

        print(f"[VoiceKick] {member} 자동 퇴장 완료")

    except discord.Forbidden:
        print(f"[VoiceKick] {member} 퇴장 실패: 권한 부족 또는 DM 차단")

    except Exception as e:
        print(f"[VoiceKick] {member} 퇴장 중 오류: {e}")

    uid = member.id
    voice_inactive.pop(uid, None)
    voice_warned.pop(uid, None)
    voice_snooze.pop(uid, None)
    voice_pending_on.pop(uid, None)


@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    uid = member.id

    if after.channel is None:
        voice_inactive.pop(uid, None)
        voice_warned.pop(uid, None)
        voice_snooze.pop(uid, None)
        voice_pending_on.pop(uid, None)
        return

    if is_headset_off(after):
        if uid not in voice_inactive and uid not in voice_snooze:
            await send_first_voice_dm(member)
    else:
        voice_inactive.pop(uid, None)
        voice_warned.pop(uid, None)
        voice_snooze.pop(uid, None)
        voice_pending_on.pop(uid, None)


@tasks.loop(minutes=1)
async def voice_kick_check():
    now = datetime.now(KST)

    for guild in bot.guilds:
        for channel in guild.voice_channels:
            for member in channel.members:
                if member.bot:
                    continue

                state = member.voice
                if state is None:
                    continue

                uid = member.id

                if not is_headset_off(state):
                    voice_inactive.pop(uid, None)
                    voice_warned.pop(uid, None)
                    voice_snooze.pop(uid, None)
                    voice_pending_on.pop(uid, None)
                    continue

                snooze_until = voice_snooze.get(uid)
                if snooze_until:
                    if now < snooze_until:
                        continue

                    voice_snooze.pop(uid, None)
                    voice_inactive.pop(uid, None)
                    voice_warned.pop(uid, None)
                    voice_pending_on.pop(uid, None)

                    await send_first_voice_dm(member)
                    continue

                if uid not in voice_inactive:
                    await send_first_voice_dm(member)
                    continue

                pending_until = voice_pending_on.get(uid)
                if pending_until and now >= pending_until:
                    await send_final_voice_dm(member)
                    continue

                warned_at = voice_warned.get(uid)
                if warned_at and now - warned_at >= FINAL_WARNING_TIME:
                    await disconnect_with_countdown(member)

# =========================
# 사냥 / 장비 / 스탯 / 직업 시스템
# =========================

hunt_cooldowns = {}
target_hunt_cooldowns = {}

HUNT_COOLDOWN = timedelta(seconds=5)
TARGET_HUNT_COOLDOWN = timedelta(hours=24)

STAT_NAMES = {
    "힘": "str",
    "민첩": "dex",
    "지능": "int",
    "마력": "mag",
    "체력": "vit"
}

STAT_KR = {
    "str": "힘",
    "dex": "민첩",
    "int": "지능",
    "mag": "마력",
    "vit": "체력"
}

JOBS = {
    "궁수": {
        "stats": ["str", "vit"],
        "desc": "힘과 체력 특화. 안정적으로 승률을 올리는 직업."
    },
    "전사": {
        "stats": ["dex", "vit"],
        "desc": "민첩과 체력 특화. 약한 적을 잘 만나고 버티는 직업."
    },
    "도적": {
        "stats": ["int", "dex"],
        "desc": "지능과 민첩 특화. 보상과 사냥 안정성을 챙기는 직업."
    },
    "법사": {
        "stats": ["mag", "vit"],
        "desc": "마력과 체력 특화. 승률 2배와 생존력을 노리는 직업."
    }
}

WEAPONS = {
    "무인검": {"price": 0, "bonus": 1},
    "은검": {"price": 500, "bonus": 6},
    "비천어검": {"price": 1200, "bonus": 10},
    "참암 프로토타입": {"price": 2500, "bonus": 15},
    "제례검": {"price": 4500, "bonus": 20},
    "페보니우스 검": {"price": 6500, "bonus": 25},
    "칠흑검": {"price": 9000, "bonus": 29},
    "천공의 검": {"price": 13000, "bonus": 35},
    "안개를 가르는 회광": {"price": 18000, "bonus": 45},
    "고요히 샘솟는 빛": {"price": 25000, "bonus": 60},
    "서약의 자유": {"price": 100000, "bonus": 85},
    "용사의 성검": {"price": 6500000, "bonus": 270}
}

ARMORS = {
    "모험가 세트": {"price": 0, "bonus": 1},
    "행자의 마음": {"price": 500, "bonus": 4},
    "전투광 세트": {"price": 1200, "bonus": 8},
    "교관 세트": {"price": 2200, "bonus": 12},
    "검투사의 피날레": {"price": 4000, "bonus": 17},
    "대지를 유랑하는 악단": {"price": 6000, "bonus": 23},
    "절연의 기치": {"price": 8500, "bonus": 30},
    "몰락한 마음": {"price": 11000, "bonus": 35},
    "그림자 사냥꾼": {"price": 15000, "bonus": 45},
    "황금 극단": {"price": 20000, "bonus": 60},
    "화려한 꿈의 껍데기": {"price": 100000, "bonus": 80},
    "용사의 갑옷": {"price": 5000000, "bonus": 200}
}


MONSTERS = [
    {"name": "슬라임", "min": 1, "max": 10, "penalty": 4},
    {"name": "츄츄족", "min": 1, "max": 15, "penalty": 10},
    {"name": "츄츄 폭도", "min": 5, "max": 20, "penalty": 16},
    {"name": "보물 사냥단", "min": 8, "max": 25, "penalty": 24},
    {"name": "심연 메이지", "min": 12, "max": 35, "penalty": 31},
    {"name": "우인단 선발대", "min": 15, "max": 40, "penalty": 42},
    {"name": "유적 가드", "min": 20, "max": 45, "penalty": 53},
    {"name": "유적 헌터", "min": 25, "max": 50, "penalty": 66},
    {"name": "거울의 여인", "min": 30, "max": 55, "penalty": 77},
    {"name": "검귀", "min": 35, "max": 60, "penalty": 87},
    {"name": "성해 짐승", "min": 40, "max": 70, "penalty": 98},
    {"name": "유적 드레이크", "min": 45, "max": 75, "penalty": 110},
    {"name": "심연 사도", "min": 50, "max": 85, "penalty": 123},
    {"name": "심연 영창자", "min": 60, "max": 100, "penalty": 135},
    {"name": "원해 짐승", "min": 65, "max": 110, "penalty": 165},
    {"name": "자율 초정밀 태엽장치", "min": 70, "max": 120, "penalty": 185},
    {"name": "유적 서펜트", "min": 80, "max": 130, "penalty": 215},
    {"name": "영겁의 드레이크", "min": 90, "max": 140, "penalty": 265},
    {"name": "반영구 제어 매트릭스", "min": 110, "max": 150, "penalty": 335},
    {"name": "수계 사냥개 무리", "min": 135, "max": 165, "penalty": 395},
    {"name": "철갑 용 도마뱀", "min": 150, "max": 180, "penalty": 470},
    {"name": "황금 늑대왕", "min": 180, "max": 200, "penalty": 595},
    {"name": "아펩의 수호자", "min": 200, "max": 230, "penalty": 720},
    {"name": "타르탈리아", "min": 230, "max": 270, "penalty": 850},
    {"name": "라이덴 쇼군", "min": 270, "max": 310, "penalty": 900},
    {"name": "천리의 유지자", "min": 310, "max": 420, "penalty": 1200},
    {"name": "마왕", "min": 420, "max": 1000, "peanlty": 5000}
]

MONSTER_TRAIT_RATE = 30 

MONSTER_TRAITS = [
    {"name": "💤 잠이 덜 깬", "chance": 1, "monster_power": 0.25, "money": 4.5, "exp": 4.5},
    {"name": "🩸 죽어가는", "chance": 1, "monster_power": 0.2, "money": 4.5, "exp": 4.5},

    {"name": "🤕 상처를 입은", "chance": 4, "monster_power": 0.5, "money": 3.0, "exp": 3.0},

    {"name": "😵 겁먹은", "chance": 10, "monster_power": 0.75, "money": 1.8, "exp": 1.8},
    {"name": "🦴 허약한", "chance": 10, "monster_power": 0.8, "money": 1.8, "exp": 1.8},

    {"name": "✨ 단련된", "chance": 18, "monster_power": 1.2, "money": 1.3, "exp": 1.3},
    {"name": "⚔️ 분노의", "chance": 18, "monster_power": 1.2, "money": 1.3, "exp": 1.3},

    {"name": "💪 강화된", "chance": 12, "monster_power": 1.45, "money": 1.6, "exp": 1.6},
    {"name": "🛡️ 철갑을 두른", "chance": 12, "monster_power": 1.45, "money": 1.6, "exp": 1.6},

    {"name": "👹 광폭한", "chance": 5, "monster_power": 1.9, "money": 2.3, "exp": 2.3},
    {"name": "🌋 불굴의", "chance": 5, "monster_power": 1.9, "money": 2.3, "exp": 2.3},
    {"name": "⚡ 돌격의", "chance": 5, "monster_power": 1.9, "money": 2.3, "exp": 2.3},

    {"name": "💀 악몽의", "chance": 2, "monster_power": 2.8, "money": 4.0, "exp": 4.0},
    {"name": "👑 군주", "chance": 2, "monster_power": 2.8, "money": 4.0, "exp": 4.0},

    {"name": "☠️ 재앙의", "chance": 0.5, "monster_power": 5.0, "money": 8.0, "exp": 8.0},

    {"name": "💎 황금의", "chance": 0.25, "monster_power": 1.2, "money": 20.0, "exp": 10.0},
    {"name": "🌈 빛나는", "chance": 0.2, "monster_power": 1.3, "money": 15.0, "exp": 35.0},
]


def pick_monster_trait():
    if random.randint(1, 100) > MONSTER_TRAIT_RATE:
        return None

    return random.choices(
        MONSTER_TRAITS,
        weights=[t["chance"] for t in MONSTER_TRAITS],
        k=1
    )[0]


def apply_trait_to_monster_level(monster_level, trait):
    return monster_level

    power = trait.get("power", trait.get("monster_power", 1))

    return max(1, int(monster_level * power))


def apply_trait_reward(reward, exp, trait):
    if trait is None:
        return reward, exp

    return int(reward * trait["money"]), int(exp * trait["exp"])

STAT_BG_PATH = "stat_bg.png"

def get_font(size):
    try:
        return ImageFont.truetype("NanumGothicBold.ttf", size)
    except:
        return ImageFont.load_default()


def draw_bar(draw, x, y, w, h, value, max_value):
    ratio = 0 if max_value <= 0 else min(1, value / max_value)
    fill_w = int(w * ratio)

    draw.rounded_rectangle((x, y, x + w, y + h), radius=6, outline=(0, 180, 255), width=2)
    if fill_w > 0:
        draw.rounded_rectangle((x, y, x + fill_w, y + h), radius=6, fill=(0, 200, 255))


STAT_BG_PATH = "stat_bg.png"
FONT_PATH = "NanumGothicBold.ttf"


def get_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

def fit_font(draw, text, max_width, start=36):
    for size in range(start, 14, -2):
        font = get_font(size)

        bbox = draw.textbbox(
            (0, 0),
            text,
            font=font
        )

        width = bbox[2] - bbox[0]

        if width <= max_width:
            return font

    return get_font(14)

def draw_bar(draw, x, y, w, h, value, max_value):
    ratio = 0 if max_value <= 0 else min(1, value / max_value)
    fill_w = int(w * ratio)

    if fill_w > 0:
        draw.rounded_rectangle(
            (x, y, x + fill_w, y + h),
            radius=5,
            fill=(0, 210, 255, 230)
        )


def fit_text(draw, text, font_path, max_width, start_size, min_size=16):
    for size in range(start_size, min_size - 1, -2):
        font = get_font(size)
        box = draw.textbbox((0, 0), text, font=font)
        if box[2] - box[0] <= max_width:
            return font
    return get_font(min_size)


def wrap_text(draw, text, font, max_width):
    lines = []
    current = ""

    for ch in text:
        test = current + ch
        box = draw.textbbox((0, 0), test, font=font)
        if box[2] - box[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = ch

    if current:
        lines.append(current)

    return lines


async def create_stat_image(member, user):
    bg = Image.open(STAT_BG_PATH).convert("RGBA")
    draw = ImageDraw.Draw(bg)

    white = (255, 255, 255, 255)
    cyan = (130, 235, 255, 255)

    font_name = fit_text(draw, member.display_name, FONT_PATH, 180, 25)
    font_info = get_font(21)
    font_stat_name = get_font(27)
    font_stat_num = get_font(36)
    font_small = get_font(21)
    font_plus = get_font(34)

    level = user["level"]
    exp = user["exp"]
    need_exp = get_required_exp(level)
    job = user["job"] or "없음"

    strength = get_stat(user, "str")
    dex = get_stat(user, "dex")
    intelligence = get_stat(user, "int")
    mag = get_stat(user, "mag")
    vit = get_stat(user, "vit")

    try:
        avatar_bytes = await member.display_avatar.with_size(256).read()

        avatar = Image.open(BytesIO(avatar_bytes)).convert("RGBA")
        avatar = ImageOps.fit(avatar, (220, 255), centering=(0.5, 0.5))

        mask = Image.new("L", (220, 255), 0)
        mask_draw = ImageDraw.Draw(mask)

        mask_draw.rounded_rectangle(
            (0, 0, 220, 255),
            radius=20,
            fill=255
        )

        bg.paste(avatar, (95, 145), mask)

    except Exception as e:
        print("프사 로드 실패:", e)

    name_box = draw.textbbox((0, 0), member.display_name, font=font_name)
    name_width = name_box[2] - name_box[0]

    draw.text(
        (205 - name_width // 2, 410),
        member.display_name,
        font=font_name,
        fill=white
    )

    draw.text((390, 135), "직업", font=font_info, fill=cyan)
    draw.text((455, 135), job, font=font_info, fill=white)

    draw.text((390, 220), "레벨", font=font_info, fill=cyan)
    draw.text((455, 220), f"Lv.{level}", font=font_info, fill=white)

    draw.text((390, 330), "EXP", font=font_info, fill=cyan)
    draw.text((455, 330), f"{exp}/{need_exp}", font=font_small, fill=white)

    draw.text((390, 410), "목숨", font=font_info, fill=cyan)
    draw.text((455, 410), f"{user['lives']} / 3", font=font_info, fill=white)

    draw.text((390, 440), "스탯", font=font_info, fill=cyan)
    draw.text((455, 440), f"{user['stat_point']} P", font=font_info, fill=white)

    draw_bar(draw, 85, 778, 485, 25, exp, need_exp)

    str_bonus = int(strength * 0.1)
    dex_bonus = dex // 10
    int_bonus = int(intelligence * 0.1)
    mag_proc = min(50, mag * 0.1)
    vit_save = min(60, vit * 0.2)

    draw.text((100, 510), f"힘: 승률 +{str_bonus}%", font=font_small, fill=white)
    draw.text((100, 550), f"민첩: 승률 +{dex_bonus}%", font=font_small, fill=white)
    draw.text((100, 590), f"지능: EXP·모라 +{int_bonus:.1f}%", font=font_small, fill=white)
    draw.text((100, 630), f"마력: 승률 강화 확률 {mag_proc:.1f}%", font=font_small, fill=white)
    draw.text((100, 670), f"체력: 목숨 보호 {vit_save:.1f}%", font=font_small, fill=white)

    stats = [
        ("힘", "STR", strength, 800, 145),
        ("민첩", "DEX", dex, 800, 285),
        ("지능", "INT", intelligence, 800, 417),
        ("마력", "MAG", mag, 800, 550),
        ("체력", "VIT", vit, 800, 680),
    ]

    for name, eng, value, x, y in stats:
        draw.text((x, y), f"{name} ({eng})", font=font_stat_name, fill=white)

        value_text = str(value)
        bbox = draw.textbbox((0, 0), value_text, font=font_stat_num)
        value_width = bbox[2] - bbox[0]

        draw.text(
            (1000 - value_width, y - 8),
            value_text,
            font=font_stat_num,
            fill=white
        )

        draw_bar(draw, x, y + 72, 565, 20, value, 100)

        if user["stat_point"] > 0:
            plus_x = 1045
            plus_y = y - 8

            draw.rounded_rectangle(
                (plus_x, plus_y, plus_x + 42, plus_y + 42),
                radius=10,
                outline=cyan,
                width=2
            )

            draw.text(
                (plus_x + 12, plus_y - 1),
                "+",
                font=font_plus,
                fill=cyan
            )

    buffer = BytesIO()
    bg.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer


@bot.tree.command(name="스탯창", description="내 스탯을 확인하고 스탯을 찍는다", guild=GUILD)
async def stat_window(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    user = get_hunt_user(uid)

    image = await create_stat_image(interaction.user, user)
    file = discord.File(image, filename="stat.png")

    embed = discord.Embed(color=discord.Color.blue())
    embed.set_image(url="attachment://stat.png")

    kwargs = {
        "file": file,
        "embed": embed
    }

    if user["stat_point"] > 0:
        kwargs["view"] = StatView(uid)

    await interaction.response.send_message(**kwargs)
    
def get_hunt_user(uid):
    uid = str(uid)

    if uid not in hunt_users:
        hunt_users[uid] = {}

    user = hunt_users[uid]

    defaults = {
        "level": 1,
        "exp": 0,
        "weapon": "무인검",
        "armor": "모험가 세트",
        "lives": 3,
        "stat_point": 3,
        "job": None,
        "str": 0,
        "dex": 0,
        "int": 0,
        "mag": 0,
        "vit": 0
    }

    for key, value in defaults.items():
        user.setdefault(key, value)
    
    return user


def get_stat(user, stat):
    return int(user.get(stat, 0))


def pick_monster(player_level, user=None):
    dex = get_stat(user, "dex") if user else 0

    # 레벨별 몬스터 출현 범위
    if player_level >= 100:
        min_level = max(1, player_level - 5)
        max_level = player_level + 20

    elif player_level >= 50:
        min_level = max(1, player_level - 10)
        max_level = player_level + 15

    else:
        min_level = max(1, player_level - 7)
        max_level = player_level + 7

    target_level = random.randint(min_level, max_level)

    # 민첩: 약한 몹이 조금 더 잘 나오게 함
    target_level -= dex // 20
    target_level = max(1, target_level)

    possible = [
        m for m in MONSTERS
        if m["min"] <= target_level <= m["max"]
    ]

    if not possible:
        possible = MONSTERS

    monster = random.choice(possible)

    monster_level = random.randint(
        max(monster["min"], target_level - 2),
        min(monster["max"], target_level + 2)
    )

    return monster, monster_level


def find_monster_by_name(name):
    for monster in MONSTERS:
        if monster["name"] == name:
            return monster
    return None


def calc_win_chance(user, monster, monster_level, trait=None):
    player_level = user["level"]
    weapon_bonus = WEAPONS[user["weapon"]]["bonus"]
    armor_bonus = ARMORS[user["armor"]]["bonus"]

    strength = get_stat(user, "str")
    dex = get_stat(user, "dex")

    chance = 50
    chance += (player_level - monster_level) * 3
    chance += weapon_bonus * 0.8
    chance += armor_bonus * 0.6
    chance -= monster["penalty"] * 0.6
    chance -= max(0, monster_level - player_level) * 0.8

    chance += strength // 5
    chance += dex // 15

    if trait:
        power = trait.get("monster_power", 1)
        chance /= power
    
    return max(5, min(95, int(chance)))


def apply_magic_double_chance(user, win_chance):
    mag = get_stat(user, "mag")

    proc_chance = min(35, mag * 0.08)
    activated = random.random() * 100 < proc_chance

    if activated:
        win_chance = min(92, win_chance + 20)

    return int(win_chance), activated
    
def apply_int_reward_bonus(user, reward, exp):
    intelligence = get_stat(user, "int")

    bonus = 1 + min(0.6, intelligence * 0.0008)

    reward = int(reward * bonus)
    exp = int(exp * bonus)

    return reward, exp


def check_life_save(user):
    vit = get_stat(user, "vit")

    save_chance = min(45, vit * 0.15)

    return random.random() * 100 < save_chance


def calc_hospital_fee(user, money):
    vit = get_stat(user, "vit")

    base_rate = 0.07

    # 체력 50당 병원비 0.1% 감소
    discount = (vit // 50) * 0.001

    final_rate = max(0, base_rate - discount)

    return int(money * final_rate), final_rate


def give_hunt_exp(user, amount):
    user["exp"] += amount
    leveled = 0

    while user["exp"] >= get_required_exp(user["level"]):
        user["exp"] -= get_required_exp(user["level"])
        user["level"] += 1
        user["stat_point"] += 5
        leveled += 1

    return leveled


async def run_hunt_battle(interaction, user, monster, monster_level, trait=None, is_target=False):
    uid = str(interaction.user.id)
    
    monster_name = monster["name"]
    
    if trait:
        monster_name = f"{trait['name']} {monster_name}"
    
    battle_monster_level = apply_trait_to_monster_level(monster_level, trait)
    
    win_chance = calc_win_chance(user, monster, monster_level, trait)
    win_chance, magic_activated = apply_magic_double_chance(user, win_chance)

    add_quest_progress(uid, "hunt_count", 1)
    sync_hunt_level_quests(uid)

    embed = discord.Embed(
        title="⚔️ 사냥 시작",
        description=(
            f"**Lv.{battle_monster_level} {monster_name}** 등장!\n"
            f"승률: **{int(win_chance)}%**\n"
            f"마력 폭주: **{'발동됨' if magic_activated else '발동 안 됨'}**\n\n"
            "전투 중."
        ),
        color=discord.Color.orange()
    )

    await interaction.response.edit_message(embed=embed, view=None)
    msg = await interaction.original_response()

    await asyncio.sleep(1)
    embed.description += "\n검을 휘두르는 중."
    await msg.edit(embed=embed)

    await asyncio.sleep(1)
    embed.description += "\n운명의 판정 중."
    await msg.edit(embed=embed)

    await asyncio.sleep(1)

    win = random.randint(1, 100) <= win_chance

    if win:
        reward = random.randint(80, 160) + monster_level * 20
        exp = random.randint(30, 60) + monster_level * 5

        reward, exp = apply_trait_reward(reward, exp, trait)
        
        reward, exp = apply_int_reward_bonus(user, reward, exp)

        add_poker_money(uid, reward)

        add_quest_progress(uid, "hunt_win", 1)
        add_quest_progress(uid, "mora_earned", reward)

        leveled = give_hunt_exp(user, exp)

        # 현재 레벨 그대로 업적에 반영
        add_quest_progress(uid, "level", user["level"], mode="max")

        result = (
            f"✅ 승리!\n"
            f"획득 모라: **{reward:,}모라**\n"
            f"획득 경험치: **{exp} EXP**\n"
        )

        if leveled:
            result += (
                f"\n🎉 레벨 업! 현재 레벨: **Lv.{user['level']}**\n"
                f"스탯 포인트 **{leveled * 5}** 획득!"
            )

        embed.color = discord.Color.green()

    else:
        life_saved = check_life_save(user)

        if life_saved:
            add_quest_progress(uid, "life_save", 1)

            result = (
                f"💀 패배...\n"
                f"하지만 체력 효과로 목숨을 잃지 않았다!\n"
                f"남은 목숨: **{user['lives']}/3**"
            )
        else:
            user["lives"] -= 1

            result = (
                f"💀 패배...\n"
                f"남은 목숨: **{user['lives']}/3**"
            )

            if user["lives"] <= 0:
                money = get_poker_money(uid)
                hospital_fee, final_rate = calc_hospital_fee(user, money)

                remove_poker_money(uid, hospital_fee)
                user["lives"] = 3

                result += (
                    f"\n\n🏥 병원에서 깨어났다...\n"
                    f"치료비로 재산의 **{final_rate * 100:.1f}%**인 "
                    f"**{hospital_fee:,}모라**가 빠져나감."
                )

        embed.color = discord.Color.red()

    if not is_target:
        hunt_cooldowns[uid] = datetime.now(timezone.utc) + HUNT_COOLDOWN

    save_data()

    embed.title = "⚔️ 사냥 결과"
    embed.description = (
        f"상대: **Lv.{battle_monster_level} {monster_name}**\n"
        f"최종 승률: **{int(win_chance)}%**\n"
        f"마력 폭주: **{'발동됨' if magic_activated else '발동 안 됨'}**\n\n"
        f"{result}\n\n"
        f"현재 레벨: **Lv.{user['level']}**\n"
        f"EXP: **{user['exp']}/{get_required_exp(user['level'])}**\n"
        f"목숨: **{user['lives']}/3**\n"
        f"보유 모라: **{get_poker_money(uid):,}모라**"
    )

    await msg.edit(embed=embed, view=None)

@bot.tree.command(name="프로필설명", description="스탯창에 표시될 프로필 설명을 설정한다", guild=GUILD)
@app_commands.describe(내용="프로필 설명")
async def set_profile_desc(interaction: discord.Interaction, 내용: str):
    uid = str(interaction.user.id)
    user = get_hunt_user(uid)

    if len(내용) > 120:
        await interaction.response.send_message(
            "❌ 프로필 설명은 120자 이하로 해줘.",
            ephemeral=True
        )
        return

    user["profile_desc"] = 내용
    save_data()

    await interaction.response.send_message("✅ 프로필 설명 저장 완료!")
    
class HuntStartView(discord.ui.View):
    def __init__(self, user_id, monster=None, monster_level=None, trait=None, is_target=False):
        super().__init__(timeout=30)
        self.user_id = str(user_id)
        self.started = False
        self.monster = monster
        self.monster_level = monster_level
        self.trait = trait
        self.is_target = is_target
        self.message = None

    @discord.ui.button(label="⚔️ 전투 시작", style=discord.ButtonStyle.danger)
    async def start_hunt(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ 니 사냥 아님.", ephemeral=True)
            return

        if self.started:
            await interaction.response.send_message("이미 전투 시작됨.", ephemeral=True)
            return

        self.started = True

        for item in self.children:
            item.disabled = True

        uid = str(interaction.user.id)
        user = get_hunt_user(uid)

        monster = self.monster
        monster_level = self.monster_level

        if monster is None or monster_level is None:
            monster, monster_level = pick_monster(user["level"], user)

        await run_hunt_battle(interaction, user, monster, monster_level, self.trait, is_target=self.is_target)

    async def on_timeout(self):
        if self.started:
            return

        for item in self.children:
            item.disabled = True

        if self.message:
            try:
                await self.message.edit(
                    content="⏰ 사냥이 자동 취소됐어.",
                    view=self
                )
            except:
                pass

@bot.tree.command(name="사냥", description="몬스터를 사냥한다", guild=GUILD)
async def hunt(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    user = get_hunt_user(uid)
    now = datetime.now(timezone.utc)

    cooldown_until = hunt_cooldowns.get(uid)

    if cooldown_until and cooldown_until > now:
        left = (cooldown_until - now).total_seconds()
        await interaction.response.send_message(
            f"⏳ 아직 사냥 못 해!\n남은 시간: **{left:.1f}초**",
            ephemeral=True
        )
        return

    monster, monster_level = pick_monster(user["level"], user)

    trait = pick_monster_trait()
    
    monster_name = monster["name"]
    if trait:
        monster_name = f"{trait['name']} {monster_name}"
    
    battle_monster_level = apply_trait_to_monster_level(monster_level, trait)
    
    win_chance = calc_win_chance(user, monster, battle_monster_level, trait)
    preview_chance, magic_activated = apply_magic_double_chance(user, win_chance)
    
    view = HuntStartView(uid, monster, monster_level, trait)

    embed = discord.Embed(
        title="⚔️ 사냥 준비",
        description=(
            f"{interaction.user.mention} 사냥을 시작할까?\n\n"
            f"예상 상대: **Lv.{battle_monster_level} {monster_name}**\n"
            f"예상 승률: **{int(preview_chance)}%**\n"
            f"마력 폭주 미리보기: **{'발동됨' if magic_activated else '발동 안 됨'}**\n\n"
            "아래 버튼을 눌러야 전투가 시작됨.\n"
            "30초 동안 안 누르면 자동 취소."
        ),
        color=discord.Color.orange()
    )

    await interaction.response.send_message(embed=embed, view=view)
    view.message = await interaction.original_response()
    
@bot.tree.command(name="지정사냥", description="마력 80 이상이면 원하는 몬스터와 싸운다", guild=GUILD)
@app_commands.describe(몬스터="싸우고 싶은 몬스터 이름")
async def target_hunt(interaction: discord.Interaction, 몬스터: str):
    uid = str(interaction.user.id)
    user = get_hunt_user(uid)
    now = datetime.now(timezone.utc)

    if get_stat(user, "mag") < 80:
        await interaction.response.send_message(
            "❌ 마력 80 이상부터 지정사냥 가능함.",
            ephemeral=True
        )
        return

    cooldown_until = target_hunt_cooldowns.get(uid)

    if cooldown_until and cooldown_until > now:
        left = cooldown_until - now
        hours = int(left.total_seconds() // 3600)
        minutes = int((left.total_seconds() % 3600) // 60)

        await interaction.response.send_message(
            f"⏳ 지정사냥 쿨타임 중!\n남은 시간: **{hours}시간 {minutes}분**",
            ephemeral=True
        )
        return

    monster = find_monster_by_name(몬스터)

    if monster is None:
        names = ", ".join(m["name"] for m in MONSTERS)
        await interaction.response.send_message(
            f"❌ 그런 몬스터 없음.\n\n가능한 몬스터:\n{names}",
            ephemeral=True
        )
        return

    monster_level = random.randint(monster["min"], monster["max"])

    target_hunt_cooldowns[uid] = now + TARGET_HUNT_COOLDOWN
    save_data()

    view = HuntStartView(uid, monster, monster_level, is_target=True)

    embed = discord.Embed(
        title="🎯 지정사냥 준비",
        description=(
            f"{interaction.user.mention} 지정사냥을 시작할까?\n\n"
            f"상대: **Lv.{monster_level} {monster['name']}**\n"
            f"아래 버튼을 누르면 전투 시작.\n\n"
            "지정사냥은 24시간 쿨타임임."
        ),
        color=discord.Color.purple()
    )

    await interaction.response.send_message(embed=embed, view=view)
    view.message = await interaction.original_response()

def make_stat_embed(interaction, user):
    strength = get_stat(user, "str")
    dex = get_stat(user, "dex")
    intelligence = get_stat(user, "int")
    mag = get_stat(user, "mag")
    vit = get_stat(user, "vit")

    str_bonus = strength // 5
    dex_bonus = dex // 15
    int_bonus = min(60, intelligence * 0.08)
    mag_proc = min(35, mag * 0.08)
    vit_save = min(45, vit * 0.15)
    vit_hospital_discount = (vit // 50) * 0.1

    job = user["job"] if user["job"] else "없음"

    embed = discord.Embed(
        title=f"📊 {interaction.user.display_name}의 스탯창",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="기본 정보",
        value=(
            f"직업: **{job}**\n"
            f"레벨: **Lv.{user['level']}**\n"
            f"EXP: **{user['exp']}/{get_required_exp(user['level'])}**\n"
            f"목숨: **{user['lives']}/3**\n"
            f"남은 스탯 포인트: **{user['stat_point']}**"
        ),
        inline=False
    )

    embed.add_field(
        name="스탯",
        value=(
            f"💪 힘: **{strength}** / 승률 +{str_bonus}%\n"
            f"🏹 민첩: **{dex}** / 승률 +{dex_bonus}% / 약한 몹 등장 증가\n"
            f"🧠 지능: **{intelligence}** / EXP, 모라 +{int_bonus}%\n"
            f"✨ 마력: **{mag}** / 승률 2배 확률 {mag_proc:.1f}%\n"
            f"❤️ 체력: **{vit}** / 승률 +{vit_win_bonus}% / 목숨 보호 {vit_save:.1f}% / 병원비 -{vit_hospital_discount:.1f}%"
        ),
        inline=False
    )

    return embed

class StatAmountModal(discord.ui.Modal):
    def __init__(self, user_id, stat_key):
        super().__init__(title=f"{STAT_KR[stat_key]} 스탯 찍기")
        self.user_id = str(user_id)
        self.stat_key = stat_key

        self.amount = discord.ui.TextInput(
            label="찍을 스탯 포인트 수",
            placeholder="예: 1, 5, 10",
            min_length=1,
            max_length=5,
            required=True
        )

        self.add_item(self.amount)

    async def on_submit(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message(
                "❌ 니 스탯창 아님.",
                ephemeral=True
            )
            return

        uid = str(interaction.user.id)
        user = get_hunt_user(uid)

        try:
            amount = int(str(self.amount.value))
        except ValueError:
            await interaction.response.send_message(
                "❌ 숫자만 입력해줘.",
                ephemeral=True
            )
            return

        if amount <= 0:
            await interaction.response.send_message(
                "❌ 1 이상만 가능.",
                ephemeral=True
            )
            return

        if user["stat_point"] < amount:
            await interaction.response.send_message(
                f"❌ 스탯 포인트 부족!\n"
                f"보유: **{user['stat_point']}P**",
                ephemeral=True
            )
            return

        total_gain = 0
        bonus_count = 0

        for _ in range(amount):
            gain = 1

            if user["job"] in JOBS:
                if self.stat_key in JOBS[user["job"]]["stats"]:
                    if random.random() < 0.5:
                        gain += 1
                        bonus_count += 1

            user[self.stat_key] += gain
            total_gain += gain

        user["stat_point"] -= amount

        save_data()

        image = await create_stat_image(interaction.user, user)
        file = discord.File(image, filename="stat.png")

        embed = discord.Embed(
            description=(
                f"✅ **{STAT_KR[self.stat_key]}**에 **{amount}P** 사용!\n"
                f"총 증가량: **+{total_gain}**\n"
                f"직업 보너스 발동: **{bonus_count}회**"
            ),
            color=discord.Color.blue()
        )
        embed.set_image(url="attachment://stat.png")

        kwargs = {
            "attachments": [file],
            "embed": embed
        }

        if user["stat_point"] > 0:
            kwargs["view"] = StatView(uid)
        else:
            kwargs["view"] = discord.ui.View()

        await interaction.response.edit_message(**kwargs)


class StatView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=120)
        self.user_id = str(user_id)

    async def open_modal(self, interaction: discord.Interaction, stat_key: str):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message(
                "❌ 니 스탯창 아님.",
                ephemeral=True
            )
            return

        user = get_hunt_user(str(interaction.user.id))

        if user["stat_point"] <= 0:
            await interaction.response.send_message(
                "❌ 남은 스탯 포인트 없음.",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            StatAmountModal(self.user_id, stat_key)
        )

    @discord.ui.button(label="+ 힘", style=discord.ButtonStyle.primary)
    async def add_str(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.open_modal(interaction, "str")

    @discord.ui.button(label="+ 민첩", style=discord.ButtonStyle.primary)
    async def add_dex(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.open_modal(interaction, "dex")

    @discord.ui.button(label="+ 지능", style=discord.ButtonStyle.primary)
    async def add_int(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.open_modal(interaction, "int")

    @discord.ui.button(label="+ 마력", style=discord.ButtonStyle.primary)
    async def add_mag(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.open_modal(interaction, "mag")

    @discord.ui.button(label="+ 체력", style=discord.ButtonStyle.success)
    async def add_vit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.open_modal(interaction, "vit")

    @discord.ui.button(label="닫기", style=discord.ButtonStyle.danger)
    async def close_stat(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message(
                "❌ 니 스탯창 아님.",
                ephemeral=True
            )
            return

        await interaction.response.edit_message(
            view=discord.ui.View()
        )
    
@bot.tree.command(name="직업", description="21레벨부터 직업을 선택한다", guild=GUILD)
@app_commands.describe(이름="선택할 직업")
async def choose_job(interaction: discord.Interaction, 이름: str = None):
    uid = str(interaction.user.id)
    user = get_hunt_user(uid)

    if 이름 is None:
        embed = discord.Embed(
            title="🧭 직업 목록",
            description="21레벨부터 직업 선택 가능.",
            color=discord.Color.gold()
        )

        for job_name, info in JOBS.items():
            stats = ", ".join(STAT_KR[s] for s in info["stats"])
            embed.add_field(
                name=job_name,
                value=f"특화 스탯: **{stats}**\n{info['desc']}",
                inline=False
            )

        await interaction.response.send_message(embed=embed)
        return

    if user["level"] < 21:
        await interaction.response.send_message(
            "❌ 21레벨부터 직업 선택 가능함.",
            ephemeral=True
        )
        return

    if user["job"] is not None:
        await interaction.response.send_message(
            f"❌ 이미 직업이 있음: **{user['job']}**",
            ephemeral=True
        )
        return

    if 이름 not in JOBS:
        await interaction.response.send_message(
            "❌ 없는 직업임. 가능: 궁수, 전사, 도적, 법사",
            ephemeral=True
        )
        return

    user["job"] = 이름
    save_data()

    stats = ", ".join(STAT_KR[s] for s in JOBS[이름]["stats"])

    await interaction.response.send_message(
        f"✅ 직업 선택 완료!\n"
        f"직업: **{이름}**\n"
        f"특화 스탯: **{stats}**\n\n"
        f"이제 특화 스탯을 찍으면 50% 확률로 +2 오름."
    )


@bot.tree.command(name="무기", description="무기를 구매하거나 확인한다", guild=GUILD)
@app_commands.describe(이름="구매할 무기 이름")
async def weapon_shop(interaction: discord.Interaction, 이름: str = None):
    uid = str(interaction.user.id)
    user = get_hunt_user(uid)

    if 이름 is None:
        embed = discord.Embed(
            title="🗡️ 무기 상점",
            color=discord.Color.dark_gold()
        )

        lines = []

        for name, info in WEAPONS.items():
            owned = " ✅ 장착중" if user["weapon"] == name else ""
            lines.append(
                f"**{name}** - {info['price']:,}모라 / 승률 +{info['bonus']}%{owned}"
            )

        embed.description = "\n".join(lines)
        await interaction.response.send_message(embed=embed)
        return

    if 이름 not in WEAPONS:
        await interaction.response.send_message("❌ 그런 무기는 없음.", ephemeral=True)
        return

    price = WEAPONS[이름]["price"]
    money = get_poker_money(uid)

    if money < price:
        await interaction.response.send_message(
            f"❌ 모라 부족!\n필요: **{price:,}모라**\n보유: **{money:,}모라**",
            ephemeral=True
        )
        return

    remove_poker_money(uid, price)
    user["weapon"] = 이름
    save_data()

    await interaction.response.send_message(
        f"🗡️ **{이름}** 구매 및 장착 완료!\n"
        f"승률 보너스: **+{WEAPONS[이름]['bonus']}%**"
    )


@bot.tree.command(name="갑옷", description="갑옷을 구매하거나 확인한다", guild=GUILD)
@app_commands.describe(이름="구매할 갑옷 이름")
async def armor_shop(interaction: discord.Interaction, 이름: str = None):
    uid = str(interaction.user.id)
    user = get_hunt_user(uid)

    if 이름 is None:
        embed = discord.Embed(
            title="🛡️ 갑옷 상점",
            color=discord.Color.dark_teal()
        )

        lines = []

        for name, info in ARMORS.items():
            owned = " ✅ 장착중" if user["armor"] == name else ""
            lines.append(
                f"**{name}** - {info['price']:,}모라 / 승률 +{info['bonus']}%{owned}"
            )

        embed.description = "\n".join(lines)
        await interaction.response.send_message(embed=embed)
        return

    if 이름 not in ARMORS:
        await interaction.response.send_message("❌ 그런 갑옷은 없음.", ephemeral=True)
        return

    price = ARMORS[이름]["price"]
    money = get_poker_money(uid)

    if money < price:
        await interaction.response.send_message(
            f"❌ 모라 부족!\n필요: **{price:,}모라**\n보유: **{money:,}모라**",
            ephemeral=True
        )
        return

    remove_poker_money(uid, price)
    user["armor"] = 이름
    save_data()

    await interaction.response.send_message(
        f"🛡️ **{이름}** 구매 및 장착 완료!\n"
        f"승률 보너스: **+{ARMORS[이름]['bonus']}%**"
    )


@bot.tree.command(name="내사냥정보", description="내 사냥 정보를 확인한다", guild=GUILD)
async def hunt_status(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    user = get_hunt_user(uid)

    embed = discord.Embed(
        title=f"📜 {interaction.user.display_name}의 사냥 정보",
        color=discord.Color.green()
    )

    embed.add_field(
        name="정보",
        value=(
            f"레벨: **Lv.{user['level']}**\n"
            f"EXP: **{user['exp']}/{get_required_exp(user['level'])}**\n"
            f"목숨: **{user['lives']}/3**\n"
            f"직업: **{user['job'] or '없음'}**\n"
            f"스탯 포인트: **{user['stat_point']}**\n"
            f"무기: **{user['weapon']}**\n"
            f"갑옷: **{user['armor']}**\n"
            f"모라: **{get_poker_money(uid):,}모라**"
        ),
        inline=False
    )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="스킬포인트",
    description="유저에게 스탯 포인트를 지급한다",
    guild=GUILD
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    유저="지급할 대상",
    수치="지급할 스탯 포인트"
)
async def give_stat_point(
    interaction: discord.Interaction,
    유저: discord.Member,
    수치: int
):
    uid = str(유저.id)
    user = get_hunt_user(uid)

    user["stat_point"] += 수치

    if user["stat_point"] < 0:
        user["stat_point"] = 0

    save_data()

    await interaction.response.send_message(
        f"✅ {유저.mention}의 스탯 포인트가 **{수치:+}P** 변경됨!\n"
        f"현재 스탯 포인트: **{user['stat_point']}P**"
    )

@bot.tree.command(
    name="사냥레벨관리",
    description="관리자 전용: 유저의 사냥 레벨을 올린다",
    guild=GUILD
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    유저="레벨을 올릴 유저",
    수치="올릴 레벨 수"
)
async def add_hunt_level(
    interaction: discord.Interaction,
    유저: discord.Member,
    수치: int
):
    if 수치 <= 0:
        await interaction.response.send_message("❌ 1 이상만 가능.", ephemeral=True)
        return

    user = get_hunt_user(str(유저.id))

    user["level"] += 수치
    user["stat_point"] += 수치 * 5

    save_data()

    await interaction.response.send_message(
        f"✅ {유저.mention} 레벨 **+{수치}** 완료!\n"
        f"현재 레벨: **Lv.{user['level']}**\n"
        f"스탯 포인트: **{user['stat_point']}P**"
    )


@bot.tree.command(
    name="레벨차감",
    description="관리자 전용: 유저의 사냥 레벨을 낮춘다",
    guild=GUILD
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    유저="레벨을 낮출 유저",
    수치="차감할 레벨 수"
)
async def remove_hunt_level(
    interaction: discord.Interaction,
    유저: discord.Member,
    수치: int
):
    if 수치 <= 0:
        await interaction.response.send_message("❌ 1 이상만 가능.", ephemeral=True)
        return

    user = get_hunt_user(str(유저.id))

    user["level"] = max(1, user["level"] - 수치)
    user["exp"] = 0

    save_data()

    await interaction.response.send_message(
        f"✅ {유저.mention} 레벨 **-{수치}** 완료!\n"
        f"현재 레벨: **Lv.{user['level']}**"
    )

@bot.tree.command(name="원석교환", description="모라를 원석으로 교환한다", guild=GUILD)
@app_commands.describe(원석="교환할 원석 수")
async def exchange_primogems(interaction: discord.Interaction, 원석: int):
    uid = str(interaction.user.id)

    if 원석 <= 0:
        await interaction.response.send_message("❌ 1 이상 입력해줘.", ephemeral=True)
        return

    cost = 원석 * 1000
    money = get_poker_money(uid)

    if money < cost:
        await interaction.response.send_message(
            f"❌ 모라 부족!\n필요: **{cost:,}모라**\n보유: **{money:,}모라**",
            ephemeral=True
        )
        return

    remove_poker_money(uid, cost)
    add_primogems(uid, 원석)

    embed = discord.Embed(
        title="💎 원석 교환 완료",
        description=(
            f"사용 모라: **{cost:,}모라**\n"
            f"획득 원석: **{원석:,}개**\n\n"
            f"현재 원석: **{get_primogems(uid):,}개**"
        ),
        color=discord.Color.green()
    )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="원석", description="내 원석을 확인한다", guild=GUILD)
async def primogem_status(interaction: discord.Interaction):
    uid = str(interaction.user.id)

    await interaction.response.send_message(
        f"💎 {interaction.user.mention}의 원석: **{get_primogems(uid):,}개**"
    )

QUEST_TYPES = {
    "daily": "일일",
    "weekly": "주간",
    "permanent": "업적"
}

QUEST_GRADES = {
    "E": "⚪",
    "D": "🟢",
    "C": "🔵",
    "B": "🟣",
    "A": "🟡",
    "S": "🟠",
    "SS": "🔴"
}

DAILY_QUEST_POOL = {
    "daily_hunt_10": {
        "name": "오늘의 사냥",
        "desc": "사냥 10회 진행",
        "type": "hunt_count",
        "target": 10,
        "grade": "E",
        "reward_primogem": 20
    },
    "daily_hunt_20": {
        "name": "부지런한 사냥꾼",
        "desc": "사냥 20회 진행",
        "type": "hunt_count",
        "target": 20,
        "grade": "D",
        "reward_primogem": 35
    },
    "daily_win_5": {
        "name": "승리의 감각",
        "desc": "사냥 5회 승리",
        "type": "hunt_win",
        "target": 5,
        "grade": "D",
        "reward_primogem": 30
    },
    "daily_win_10": {
        "name": "오늘도 연승",
        "desc": "사냥 10회 승리",
        "type": "hunt_win",
        "target": 10,
        "grade": "C",
        "reward_primogem": 45
    },
    "daily_mora_5000": {
        "name": "모라 수집",
        "desc": "모라 5,000 획득",
        "type": "mora_earned",
        "target": 5000,
        "grade": "D",
        "reward_primogem": 30
    },
    "daily_mora_15000": {
        "name": "오늘의 벌이",
        "desc": "모라 15,000 획득",
        "type": "mora_earned",
        "target": 15000,
        "grade": "C",
        "reward_primogem": 50
    },
    "daily_level_1": {
        "name": "작은 성장",
        "desc": "레벨 1회 상승",
        "type": "level_up",
        "target": 1,
        "grade": "C",
        "reward_primogem": 50
    },
    "daily_gacha_1": {
        "name": "운명의 시험",
        "desc": "캐릭터 뽑기 1회 진행",
        "type": "gacha_count",
        "target": 1,
        "grade": "C",
        "reward_primogem": 40
    }
}

WEEKLY_QUEST_POOL = {
    "weekly_hunt_100": {
        "name": "끈질긴 사냥꾼",
        "desc": "사냥 100회 진행",
        "type": "hunt_count",
        "target": 100,
        "grade": "B",
        "reward_primogem": 160
    },
    "weekly_hunt_200": {
        "name": "사냥 중독",
        "desc": "사냥 200회 진행",
        "type": "hunt_count",
        "target": 200,
        "grade": "A",
        "reward_primogem": 280
    },
    "weekly_win_50": {
        "name": "주간 승리자",
        "desc": "사냥 50회 승리",
        "type": "hunt_win",
        "target": 50,
        "grade": "A",
        "reward_primogem": 240
    },
    "weekly_win_100": {
        "name": "승리 루틴",
        "desc": "사냥 100회 승리",
        "type": "hunt_win",
        "target": 100,
        "grade": "S",
        "reward_primogem": 400
    },
    "weekly_level_3": {
        "name": "성장의 증명",
        "desc": "레벨 3회 상승",
        "type": "level_up",
        "target": 3,
        "grade": "A",
        "reward_primogem": 240
    },
    "weekly_level_5": {
        "name": "폭풍 성장",
        "desc": "레벨 5회 상승",
        "type": "level_up",
        "target": 5,
        "grade": "S",
        "reward_primogem": 420
    },
    "weekly_mora_100000": {
        "name": "주간 수금",
        "desc": "모라 100,000 획득",
        "type": "mora_earned",
        "target": 100000,
        "grade": "A",
        "reward_primogem": 260
    },
    "weekly_gacha_10": {
        "name": "운명의 회전",
        "desc": "캐릭터 뽑기 10회 진행",
        "type": "gacha_count",
        "target": 10,
        "grade": "A",
        "reward_primogem": 240
    },
    "weekly_weapon_gacha_5": {
        "name": "무기 단조의 꿈",
        "desc": "전무 뽑기 5회 진행",
        "type": "weapon_gacha_count",
        "target": 5,
        "grade": "A",
        "reward_primogem": 260
    }
}

PERMANENT_QUESTS = {
    "perm_hunt_10": {"name": "첫 발걸음", "desc": "사냥 10회 진행", "type": "hunt_count", "target": 10, "grade": "E", "reward_primogem": 30},
    "perm_hunt_30": {"name": "숲의 초심자", "desc": "사냥 30회 진행", "type": "hunt_count", "target": 30, "grade": "E", "reward_primogem": 40},
    "perm_hunt_50": {"name": "사냥 입문", "desc": "사냥 50회 진행", "type": "hunt_count", "target": 50, "grade": "E", "reward_primogem": 50},
    "perm_hunt_100": {"name": "초보 사냥꾼", "desc": "사냥 100회 진행", "type": "hunt_count", "target": 100, "grade": "D", "reward_primogem": 70},
    "perm_hunt_200": {"name": "익숙한 발걸음", "desc": "사냥 200회 진행", "type": "hunt_count", "target": 200, "grade": "D", "reward_primogem": 90},
    "perm_hunt_300": {"name": "반복의 힘", "desc": "사냥 300회 진행", "type": "hunt_count", "target": 300, "grade": "D", "reward_primogem": 110},
    "perm_hunt_500": {"name": "숙련된 사냥꾼", "desc": "사냥 500회 진행", "type": "hunt_count", "target": 500, "grade": "C", "reward_primogem": 150},
    "perm_hunt_750": {"name": "야생의 감각", "desc": "사냥 750회 진행", "type": "hunt_count", "target": 750, "grade": "C", "reward_primogem": 180},
    "perm_hunt_1000": {"name": "천 번의 사냥", "desc": "사냥 1,000회 진행", "type": "hunt_count", "target": 1000, "grade": "C", "reward_primogem": 220},
    "perm_hunt_1500": {"name": "끈질긴 추적자", "desc": "사냥 1,500회 진행", "type": "hunt_count", "target": 1500, "grade": "B", "reward_primogem": 280},
    "perm_hunt_2000": {"name": "전장의 단골", "desc": "사냥 2,000회 진행", "type": "hunt_count", "target": 2000, "grade": "B", "reward_primogem": 340},
    "perm_hunt_3000": {"name": "사냥의 생활화", "desc": "사냥 3,000회 진행", "type": "hunt_count", "target": 3000, "grade": "B", "reward_primogem": 420},
    "perm_hunt_5000": {"name": "사냥의 달인", "desc": "사냥 5,000회 진행", "type": "hunt_count", "target": 5000, "grade": "A", "reward_primogem": 600},
    "perm_hunt_7500": {"name": "끝없는 발자국", "desc": "사냥 7,500회 진행", "type": "hunt_count", "target": 7500, "grade": "A", "reward_primogem": 800},
    "perm_hunt_10000": {"name": "사냥의 망령", "desc": "사냥 10,000회 진행", "type": "hunt_count", "target": 10000, "grade": "S", "reward_primogem": 1200},
    "perm_hunt_15000": {"name": "몬스터의 재앙", "desc": "사냥 15,000회 진행", "type": "hunt_count", "target": 15000, "grade": "S", "reward_primogem": 1600},
    "perm_hunt_20000": {"name": "사냥의 화신", "desc": "사냥 20,000회 진행", "type": "hunt_count", "target": 20000, "grade": "SS", "reward_primogem": 2200},
    "perm_hunt_30000": {"name": "생태계 교란종", "desc": "사냥 30,000회 진행", "type": "hunt_count", "target": 30000, "grade": "SS", "reward_primogem": 3000},
    "perm_hunt_50000": {"name": "학살의 신", "desc": "사냥 50,000회 진행", "type": "hunt_count", "target": 50000, "grade": "SS", "reward_primogem": 5000},
    "perm_hunt_100000": {"name": "첫번째 걸음", "desc": "사냥 100,000회 진행", "type": "hunt_count", "target": 100000, "grade": "SS", "reward_primogem": 8000},

    "perm_win_5": {"name": "첫 승리", "desc": "사냥에서 5회 승리", "type": "hunt_win", "target": 5, "grade": "E", "reward_primogem": 30},
    "perm_win_20": {"name": "승리의 감각", "desc": "사냥에서 20회 승리", "type": "hunt_win", "target": 20, "grade": "E", "reward_primogem": 45},
    "perm_win_50": {"name": "전투 적응", "desc": "사냥에서 50회 승리", "type": "hunt_win", "target": 50, "grade": "E", "reward_primogem": 60},
    "perm_win_100": {"name": "승리 입문자", "desc": "사냥에서 100회 승리", "type": "hunt_win", "target": 100, "grade": "D", "reward_primogem": 80},
    "perm_win_200": {"name": "연승의 시작", "desc": "사냥에서 200회 승리", "type": "hunt_win", "target": 200, "grade": "D", "reward_primogem": 110},
    "perm_win_300": {"name": "전투 숙련자", "desc": "사냥에서 300회 승리", "type": "hunt_win", "target": 300, "grade": "D", "reward_primogem": 130},
    "perm_win_500": {"name": "승리 수집가", "desc": "사냥에서 500회 승리", "type": "hunt_win", "target": 500, "grade": "C", "reward_primogem": 180},
    "perm_win_750": {"name": "쓰러지지 않는 자", "desc": "사냥에서 750회 승리", "type": "hunt_win", "target": 750, "grade": "C", "reward_primogem": 220},
    "perm_win_1000": {"name": "천승의 사냥꾼", "desc": "사냥에서 1,000회 승리", "type": "hunt_win", "target": 1000, "grade": "C", "reward_primogem": 260},
    "perm_win_1500": {"name": "압도적인 전과", "desc": "사냥에서 1,500회 승리", "type": "hunt_win", "target": 1500, "grade": "B", "reward_primogem": 340},
    "perm_win_2000": {"name": "승리의 중독자", "desc": "사냥에서 2,000회 승리", "type": "hunt_win", "target": 2000, "grade": "B", "reward_primogem": 420},
    "perm_win_3000": {"name": "전장의 지배자", "desc": "사냥에서 3,000회 승리", "type": "hunt_win", "target": 3000, "grade": "B", "reward_primogem": 520},
    "perm_win_5000": {"name": "무패의 그림자", "desc": "사냥에서 5,000회 승리", "type": "hunt_win", "target": 5000, "grade": "A", "reward_primogem": 750},
    "perm_win_7500": {"name": "피로 쓰인 기록", "desc": "사냥에서 7,500회 승리", "type": "hunt_win", "target": 7500, "grade": "A", "reward_primogem": 950},
    "perm_win_10000": {"name": "승리의 화신", "desc": "사냥에서 10,000회 승리", "type": "hunt_win", "target": 10000, "grade": "S", "reward_primogem": 1400},
    "perm_win_15000": {"name": "전설의 검끝", "desc": "사냥에서 15,000회 승리", "type": "hunt_win", "target": 15000, "grade": "S", "reward_primogem": 1800},
    "perm_win_20000": {"name": "패배를 잊은 자", "desc": "사냥에서 20,000회 승리", "type": "hunt_win", "target": 20000, "grade": "SS", "reward_primogem": 2500},
    "perm_win_30000": {"name": "전투의 신", "desc": "사냥에서 30,000회 승리", "type": "hunt_win", "target": 30000, "grade": "SS", "reward_primogem": 3500},
    "perm_win_50000": {"name": "몬스터 절멸자", "desc": "사냥에서 50,000회 승리", "type": "hunt_win", "target": 50000, "grade": "SS", "reward_primogem": 5500},
    "perm_win_100000": {"name": "두번째 걸음", "desc": "사냥에서 100,000회 승리", "type": "hunt_win", "target": 100000, "grade": "SS", "reward_primogem": 9000},

    "perm_level_5": {"name": "성장의 시작", "desc": "사냥 레벨 5 달성", "type": "level", "target": 5, "grade": "E", "reward_primogem": 40},
    "perm_level_10": {"name": "초보 탈출", "desc": "사냥 레벨 10 달성", "type": "level", "target": 10, "grade": "E", "reward_primogem": 50},
    "perm_level_20": {"name": "가능성의 문", "desc": "사냥 레벨 20 달성", "type": "level", "target": 20, "grade": "D", "reward_primogem": 90},
    "perm_level_30": {"name": "직업의 길목", "desc": "사냥 레벨 30 달성", "type": "level", "target": 30, "grade": "D", "reward_primogem": 120},
    "perm_level_50": {"name": "숙련자의 문턱", "desc": "사냥 레벨 50 달성", "type": "level", "target": 50, "grade": "C", "reward_primogem": 200},
    "perm_level_75": {"name": "강자의 기척", "desc": "사냥 레벨 75 달성", "type": "level", "target": 75, "grade": "B", "reward_primogem": 350},
    "perm_level_100": {"name": "경지에 오른 자", "desc": "사냥 레벨 100 달성", "type": "level", "target": 100, "grade": "A", "reward_primogem": 600},
    "perm_level_150": {"name": "한계돌파", "desc": "사냥 레벨 150 달성", "type": "level", "target": 150, "grade": "S", "reward_primogem": 1000},
    "perm_level_200": {"name": "초월자", "desc": "사냥 레벨 200 달성", "type": "level", "target": 200, "grade": "SS", "reward_primogem": 1800},
    "perm_level_300": {"name": "세번째 걸음", "desc": "사냥 레벨 300 달성", "type": "level", "target": 300, "grade": "SS", "reward_primogem": 3000},

    "perm_mora_1000": {"name": "동전 줍기", "desc": "누적 모라 1,000 획득", "type": "mora_earned", "target": 1000, "grade": "E", "reward_primogem": 30},
    "perm_mora_5000": {"name": "작은 주머니", "desc": "누적 모라 5,000 획득", "type": "mora_earned", "target": 5000, "grade": "E", "reward_primogem": 40},
    "perm_mora_10000": {"name": "짭짤한 벌이", "desc": "누적 모라 10,000 획득", "type": "mora_earned", "target": 10000, "grade": "E", "reward_primogem": 50},
    "perm_mora_50000": {"name": "모라 수집가", "desc": "누적 모라 50,000 획득", "type": "mora_earned", "target": 50000, "grade": "D", "reward_primogem": 90},
    "perm_mora_100000": {"name": "돈 냄새", "desc": "누적 모라 100,000 획득", "type": "mora_earned", "target": 100000, "grade": "D", "reward_primogem": 120},
    "perm_mora_500000": {"name": "부자의 시작", "desc": "누적 모라 500,000 획득", "type": "mora_earned", "target": 500000, "grade": "C", "reward_primogem": 220},
    "perm_mora_1000000": {"name": "백만장자", "desc": "누적 모라 1,000,000 획득", "type": "mora_earned", "target": 1000000, "grade": "B", "reward_primogem": 400},
    "perm_mora_5000000": {"name": "금고의 주인", "desc": "누적 모라 5,000,000 획득", "type": "mora_earned", "target": 5000000, "grade": "A", "reward_primogem": 800},
    "perm_mora_10000000": {"name": "인플레이션의 지배자", "desc": "누적 모라 10,000,000 획득", "type": "mora_earned", "target": 10000000, "grade": "S", "reward_primogem": 1400},
    "perm_mora_50000000": {"name": "네번째 걸음", "desc": "누적 모라 50,000,000 획득", "type": "mora_earned", "target": 50000000, "grade": "SS", "reward_primogem": 3000},

    "perm_gacha_1": {"name": "첫 운명", "desc": "캐릭터 뽑기 1회 진행", "type": "gacha_count", "target": 1, "grade": "E", "reward_primogem": 20},
    "perm_gacha_10": {"name": "열 번의 운명", "desc": "캐릭터 뽑기 10회 진행", "type": "gacha_count", "target": 10, "grade": "D", "reward_primogem": 80},
    "perm_gacha_30": {"name": "기대와 절망", "desc": "캐릭터 뽑기 30회 진행", "type": "gacha_count", "target": 30, "grade": "C", "reward_primogem": 180},
    "perm_gacha_50": {"name": "반천장의 그림자", "desc": "캐릭터 뽑기 50회 진행", "type": "gacha_count", "target": 50, "grade": "B", "reward_primogem": 300},
    "perm_gacha_90": {"name": "천장의 문턱", "desc": "캐릭터 뽑기 90회 진행", "type": "gacha_count", "target": 90, "grade": "A", "reward_primogem": 600},
    "perm_gacha_180": {"name": "확정의 대가", "desc": "캐릭터 뽑기 180회 진행", "type": "gacha_count", "target": 180, "grade": "S", "reward_primogem": 1200},
    "perm_gacha_300": {"name": "별을 좇는 자", "desc": "캐릭터 뽑기 300회 진행", "type": "gacha_count", "target": 300, "grade": "S", "reward_primogem": 1800},
    "perm_gacha_500": {"name": "운명의 단골", "desc": "캐릭터 뽑기 500회 진행", "type": "gacha_count", "target": 500, "grade": "SS", "reward_primogem": 3000},
    "perm_gacha_1000": {"name": "별을 부르는 자", "desc": "캐릭터 뽑기 1,000회 진행", "type": "gacha_count", "target": 1000, "grade": "SS", "reward_primogem": 5000},
    "perm_gacha_2000": {"name": "다섯번째 걸음", "desc": "캐릭터 뽑기 2,000회 진행", "type": "gacha_count", "target": 2000, "grade": "SS", "reward_primogem": 8000},

    "perm_weapon_gacha_1": {"name": "첫 전무", "desc": "전무 뽑기 1회 진행", "type": "weapon_gacha_count", "target": 1, "grade": "E", "reward_primogem": 25},
    "perm_weapon_gacha_10": {"name": "무기의 부름", "desc": "전무 뽑기 10회 진행", "type": "weapon_gacha_count", "target": 10, "grade": "D", "reward_primogem": 90},
    "perm_weapon_gacha_30": {"name": "강화된 운명", "desc": "전무 뽑기 30회 진행", "type": "weapon_gacha_count", "target": 30, "grade": "C", "reward_primogem": 200},
    "perm_weapon_gacha_50": {"name": "검을 좇는 자", "desc": "전무 뽑기 50회 진행", "type": "weapon_gacha_count", "target": 50, "grade": "B", "reward_primogem": 340},
    "perm_weapon_gacha_100": {"name": "전무 수집가", "desc": "전무 뽑기 100회 진행", "type": "weapon_gacha_count", "target": 100, "grade": "A", "reward_primogem": 700},
    "perm_weapon_gacha_200": {"name": "무기고의 주인", "desc": "전무 뽑기 200회 진행", "type": "weapon_gacha_count", "target": 200, "grade": "S", "reward_primogem": 1300},
    "perm_weapon_gacha_500": {"name": "전설의 대장장이", "desc": "전무 뽑기 500회 진행", "type": "weapon_gacha_count", "target": 500, "grade": "SS", "reward_primogem": 3500},
    "perm_weapon_gacha_1000": {"name": "무기의 심연", "desc": "전무 뽑기 1,000회 진행", "type": "weapon_gacha_count", "target": 1000, "grade": "SS", "reward_primogem": 6000},
    "perm_weapon_gacha_1500": {"name": "무기와 계약한 자", "desc": "전무 뽑기 1,500회 진행", "type": "weapon_gacha_count", "target": 1500, "grade": "SS", "reward_primogem": 7500},
    "perm_weapon_gacha_2000": {"name": "여섯번째 걸음", "desc": "전무 뽑기 2,000회 진행", "type": "weapon_gacha_count", "target": 2000, "grade": "SS", "reward_primogem": 9000},

    "perm_exchange_100": {"name": "첫 교환", "desc": "원석 100개 교환", "type": "primogem_exchange", "target": 100, "grade": "E", "reward_primogem": 20},
    "perm_exchange_500": {"name": "반짝이는 주머니", "desc": "원석 500개 교환", "type": "primogem_exchange", "target": 500, "grade": "D", "reward_primogem": 70},
    "perm_exchange_1000": {"name": "원석 수집가", "desc": "원석 1,000개 교환", "type": "primogem_exchange", "target": 1000, "grade": "C", "reward_primogem": 150},
    "perm_exchange_5000": {"name": "빛나는 투자자", "desc": "원석 5,000개 교환", "type": "primogem_exchange", "target": 5000, "grade": "B", "reward_primogem": 400},
    "perm_exchange_10000": {"name": "모라 연금술사", "desc": "원석 10,000개 교환", "type": "primogem_exchange", "target": 10000, "grade": "A", "reward_primogem": 800},
    "perm_exchange_30000": {"name": "화폐 개혁자", "desc": "원석 30,000개 교환", "type": "primogem_exchange", "target": 30000, "grade": "S", "reward_primogem": 1500},
    "perm_exchange_50000": {"name": "경제의 지배자", "desc": "원석 50,000개 교환", "type": "primogem_exchange", "target": 50000, "grade": "SS", "reward_primogem": 2500},
    "perm_exchange_100000": {"name": "원석 은행장", "desc": "원석 100,000개 교환", "type": "primogem_exchange", "target": 100000, "grade": "SS", "reward_primogem": 5000},
    "perm_exchange_300000": {"name": "초인플레 청산자", "desc": "원석 300,000개 교환", "type": "primogem_exchange", "target": 300000, "grade": "SS", "reward_primogem": 8000},
    "perm_exchange_500000": {"name": "일곱번째 걸음", "desc": "원석 500,000개 교환", "type": "primogem_exchange", "target": 500000, "grade": "SS", "reward_primogem": 12000},

    "perm_target_hunt_1": {"name": "지정된 운명", "desc": "지정사냥 1회 진행", "type": "target_hunt_count", "target": 1, "grade": "D", "reward_primogem": 80},
    "perm_target_hunt_10": {"name": "노린 사냥감", "desc": "지정사냥 10회 진행", "type": "target_hunt_count", "target": 10, "grade": "C", "reward_primogem": 200},
    "perm_target_hunt_50": {"name": "표적 추적자", "desc": "지정사냥 50회 진행", "type": "target_hunt_count", "target": 50, "grade": "B", "reward_primogem": 500},
    "perm_target_hunt_100": {"name": "정밀한 사냥꾼", "desc": "지정사냥 100회 진행", "type": "target_hunt_count", "target": 100, "grade": "A", "reward_primogem": 900},
    "perm_target_hunt_300": {"name": "운명을 고르는 자", "desc": "지정사냥 300회 진행", "type": "target_hunt_count", "target": 300, "grade": "S", "reward_primogem": 1600},
    "perm_target_hunt_500": {"name": "사냥감 지정권한", "desc": "지정사냥 500회 진행", "type": "target_hunt_count", "target": 500, "grade": "SS", "reward_primogem": 3000},
    "perm_target_hunt_1000": {"name": "운명의 관리자", "desc": "지정사냥 1,000회 진행", "type": "target_hunt_count", "target": 1000, "grade": "SS", "reward_primogem": 6000},
    "perm_life_save_10": {"name": "아슬아슬 생존", "desc": "체력 효과로 목숨 10회 보호", "type": "life_save", "target": 10, "grade": "C", "reward_primogem": 200},
    "perm_life_save_50": {"name": "죽음 회피자", "desc": "체력 효과로 목숨 50회 보호", "type": "life_save", "target": 50, "grade": "A", "reward_primogem": 800},
    "perm_life_save_100": {"name": "여덟번째 걸음", "desc": "체력 효과로 목숨 100회 보호", "type": "life_save", "target": 100, "grade": "S", "reward_primogem": 1500},
}



HERO_STEPS = [
    "perm_hunt_100000",
    "perm_win_100000",
    "perm_level_300",
    "perm_mora_50000000",
    "perm_gacha_2000",
    "perm_weapon_gacha_2000",
    "perm_exchange_500000",
    "perm_life_save_100"
]

async def check_hero_title(bot, member):
    uid = str(member.id)

    sync_hunt_level_quests(uid)

    q = get_user_quests(uid)

    for key in HERO_STEPS:
        if not q["permanent"].get(key, {}).get("claimed", False):
            return

    user = get_hunt_user(uid)

    titles = user.setdefault("titles", [])

    if "용사" in titles:
        return

    titles.append("용사")
    save_data()

    channel = bot.get_channel(업적채널ID)

    if channel:
        await channel.send(
            f"🌊 **푸리나 드 폰타인**\n\n"
            f"축하드립니다, {member.mention}.\n\n"
            f"첫번째 걸음부터 여덟번째 걸음까지,\n"
            f"모든 여정을 완수하셨군요.\n\n"
            f"당신은 이제 **『용사』** 칭호를 획득했습니다. ✨"
        )
        
def get_week_key():
    now = datetime.now(KST)
    year, week, _ = now.isocalendar()
    return f"{year}-W{week}"


def get_date_key():
    return datetime.now(KST).strftime("%Y-%m-%d")


def get_user_quests(user_id):
    uid = str(user_id)

    if uid not in quests:
        quests[uid] = {}

    q = quests[uid]

    today = get_date_key()
    week = get_week_key()

    if q.get("daily_date") != today:
        q["daily_date"] = today
        q["daily"] = {
            key: {"progress": 0, "claimed": False}
            for key in random.sample(list(DAILY_QUEST_POOL.keys()), 3)
        }

    if q.get("weekly_week") != week:
        q["weekly_week"] = week
        q["weekly"] = {
            key: {"progress": 0, "claimed": False}
            for key in random.sample(
                list(WEEKLY_QUEST_POOL.keys()),
                min(3, len(WEEKLY_QUEST_POOL))
            )
        }

    q.setdefault("daily", {})
    q.setdefault("weekly", {})
    q.setdefault("permanent", {})

    for key in PERMANENT_QUESTS:
        q["permanent"].setdefault(
            key,
            {"progress": 0, "claimed": False}
        )

    return q

def add_quest_progress(user_id, quest_type, amount=1, mode="add"):
    uid = str(user_id)
    q = get_user_quests(uid)

    for group_name, pool in [
        ("daily", DAILY_QUEST_POOL),
        ("weekly", WEEKLY_QUEST_POOL),
        ("permanent", PERMANENT_QUESTS)
    ]:
        for quest_id, quest in pool.items():
            if quest["type"] != quest_type:
                continue

            q[group_name].setdefault(quest_id, {
                "progress": 0,
                "claimed": False
            })

            if mode == "max":
                q[group_name][quest_id]["progress"] = max(
                    int(q[group_name][quest_id].get("progress", 0)),
                    int(amount)
                )
            else:
                q[group_name][quest_id]["progress"] += int(amount)

    save_data()


def sync_hunt_level_quests(uid):
    user = get_hunt_user(uid)

    # 레벨 업적은 현재 레벨 기준으로 보정
    add_quest_progress(uid, "level", user["level"], mode="max")
QUEST_PAGE_SIZE = 6


def make_quest_embed(member, group, page=0):
    uid = str(member.id)
    q = get_user_quests(uid)

    if group == "daily":
        title = "🌞 일일 퀘스트"
        pool = DAILY_QUEST_POOL
        color = discord.Color.gold()
    elif group == "weekly":
        title = "📆 주간 퀘스트"
        pool = WEEKLY_QUEST_POOL
        color = discord.Color.green()
    else:
        title = "🏆 업적 퀘스트"
        pool = PERMANENT_QUESTS
        color = discord.Color.purple()

    items = list(q[group].items())
    max_page = max(0, (len(items) - 1) // QUEST_PAGE_SIZE)

    page = max(0, min(page, max_page))

    start = page * QUEST_PAGE_SIZE
    end = start + QUEST_PAGE_SIZE
    page_items = items[start:end]

    embed = discord.Embed(
        title=f"{title} - {member.display_name}",
        color=color
    )

    lines = []

    for key, state in page_items:
        info = pool[key]
        grade = info["grade"]
        emoji = QUEST_GRADES.get(grade, "⚪")

        progress = state.get("progress", 0)
        target = info["target"]
        claimed = state.get("claimed", False)

        if claimed:
            status = "✅ 수령 완료"
        elif progress >= target:
            status = "🎁 수령 가능"
        else:
            status = "진행 중"

        lines.append(
            f"{emoji} **[{grade}급] {info['name']}**\n"
            f"{info['desc']}\n"
            f"진행도: **{progress:,}/{target:,}**\n"
            f"보상: 💎 **{info['reward_primogem']:,}원석**\n"
            f"상태: **{status}**"
        )

    embed.description = "\n\n".join(lines) if lines else "퀘스트가 없음."
    embed.set_footer(text=f"{page + 1}/{max_page + 1} 페이지")

    return embed, max_page
class QuestView(discord.ui.View):
    def __init__(self, user_id, group="daily", page=0):
        super().__init__(timeout=120)
        self.user_id = str(user_id)
        self.group = group
        self.page = page

    async def check_user(self, interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ 니 퀘스트 아님.", ephemeral=True)
            return False
        return True

    async def refresh(self, interaction):
        embed, max_page = make_quest_embed(
            interaction.user,
            self.group,
            self.page
        )

        self.prev_page.disabled = self.page <= 0
        self.next_page.disabled = self.page >= max_page

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    @discord.ui.button(label="일일", style=discord.ButtonStyle.primary)
    async def daily(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_user(interaction):
            return

        self.group = "daily"
        self.page = 0
        await self.refresh(interaction)

    @discord.ui.button(label="주간", style=discord.ButtonStyle.success)
    async def weekly(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_user(interaction):
            return

        self.group = "weekly"
        self.page = 0
        await self.refresh(interaction)

    @discord.ui.button(label="업적", style=discord.ButtonStyle.secondary)
    async def permanent(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_user(interaction):
            return

        self.group = "permanent"
        self.page = 0
        await self.refresh(interaction)

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_user(interaction):
            return

        self.page -= 1
        await self.refresh(interaction)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_user(interaction):
            return

        self.page += 1
        await self.refresh(interaction)

    @discord.ui.button(label="닫기", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_user(interaction):
            return
    
        await interaction.response.edit_message(
            content="✅ 퀘스트 창을 닫았음.",
            embed=None,
            view=None
        )

@bot.tree.command(name="퀘스트", description="퀘스트 도감을 확인한다", guild=GUILD)
async def quest_status(interaction: discord.Interaction):
    uid = str(interaction.user.id)

    sync_hunt_level_quests(uid)

    view = QuestView(uid, "daily", 0)
    embed, max_page = make_quest_embed(interaction.user, "daily", 0)

    view.prev_page.disabled = True
    view.next_page.disabled = max_page <= 0

    await interaction.response.send_message(
        embed=embed,
        view=view
    )

HERO_ROLE_ID = 1517096562931793950

async def check_hero_title(bot, member):
    uid = str(member.id)


    q = get_user_quests(uid)

    for key in HERO_STEPS:
        if not q["permanent"].get(key, {}).get("claimed", False):
            return

    user = get_hunt_user(uid)
    titles = user.setdefault("titles", [])

    if "용사" in titles:
        return

    titles.append("용사")
    save_data()

    # 용사 역할 지급
    role = member.guild.get_role(HERO_ROLE_ID)
    if role and role not in member.roles:
        try:
            await member.add_roles(role, reason="용사 칭호 획득")
        except discord.Forbidden:
            print("용사 역할 지급 실패: 봇 권한 부족 또는 역할 위치 낮음")
        except discord.HTTPException as e:
            print(f"용사 역할 지급 실패: {e}")

    channel = bot.get_channel(1512642190302777415)

    if channel:
        await channel.send(
            f"🌊 **푸리나 드 폰타인**\n\n"
            f"축하드립니다, {member.mention}.\n\n"
            f"첫번째 걸음부터 여덟번째 걸음까지,\n"
            f"모든 여정을 완수하셨군요.\n\n"
            f"당신은 이제 **『용사』** 칭호를 획득했습니다. ✨\n"
        )
        
@bot.tree.command(name="퀘스트수령", description="완료한 퀘스트 보상을 수령한다", guild=GUILD)
async def quest_claim(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    q = get_user_quests(uid)

    total_reward = 0
    claimed_names = []

    for group_name, pool in [
        ("daily", DAILY_QUEST_POOL),
        ("weekly", WEEKLY_QUEST_POOL),
        ("permanent", PERMANENT_QUESTS)
    ]:
        for key, state in q[group_name].items():
            info = pool[key]

            if state.get("claimed"):
                continue

            if state.get("progress", 0) >= info["target"]:
                state["claimed"] = True
                total_reward += info["reward_primogem"]
                claimed_names.append(f"[{info['grade']}급] {info['name']}")

    if total_reward <= 0:
        await interaction.response.send_message(
            "❌ 수령 가능한 퀘스트 보상이 없음.",
            ephemeral=True
        )
        return

    add_primogems(uid, total_reward)
    save_data()

    await interaction.response.send_message(
        f"🎁 퀘스트 보상 수령 완료!\n\n"
        f"{chr(10).join(claimed_names)}\n\n"
        f"획득 원석: **{total_reward:,}개**\n"
        f"현재 원석: **{get_primogems(uid):,}개**"
    )
    await check_hero_title(bot, interaction.user)

@bot.tree.command(
    name="스킬포인트차감",
    description="유저의 스탯 포인트를 차감한다",
    guild=GUILD
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    유저="대상 유저",
    수치="차감할 포인트"
)
async def remove_stat_point(
    interaction: discord.Interaction,
    유저: discord.Member,
    수치: int
):
    if 수치 <= 0:
        await interaction.response.send_message(
            "❌ 1 이상만 가능.",
            ephemeral=True
        )
        return

    user = get_hunt_user(str(유저.id))

    user["stat_point"] = max(
        0,
        user["stat_point"] - 수치
    )

    save_data()

    await interaction.response.send_message(
        f"✅ {유저.mention}의 스탯 포인트 **-{수치}P** 차감 완료!\n"
        f"현재 스탯 포인트: **{user['stat_point']}P**"
    )

@bot.tree.command(
    name="스탯차감",
    description="유저의 스탯을 차감한다",
    guild=GUILD
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    유저="대상 유저",
    스탯="str, dex, int, mag, vit",
    수치="차감할 수치"
)
async def remove_stat(
    interaction: discord.Interaction,
    유저: discord.Member,
    스탯: str,
    수치: int
):
    stat_key = 스탯.lower()

    if stat_key not in ["str", "dex", "int", "mag", "vit"]:
        await interaction.response.send_message(
            "❌ 사용 가능 스탯: str, dex, int, mag, vit",
            ephemeral=True
        )
        return

    if 수치 <= 0:
        await interaction.response.send_message(
            "❌ 1 이상만 가능.",
            ephemeral=True
        )
        return

    user = get_hunt_user(str(유저.id))

    user[stat_key] = max(
        0,
        get_stat(user, stat_key) - 수치
    )

    save_data()

    await interaction.response.send_message(
        f"✅ {유저.mention}의 **{stat_key}** 스탯 **-{수치}** 차감 완료!\n"
        f"현재 수치: **{user[stat_key]}**"
    )

@bot.tree.command(name="레벨", description="내 레벨과 경험치를 확인합니다.", guild=GUILD)
async def level_check(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user

    info = get_level_data(member.id)
    need = required_xp(info["level"])

    embed = discord.Embed(
        title=f"{member.display_name}님의 레벨",
        description=(
            f"**Lv.{info['level']}**\n"
            f"XP: **{info['xp']} / {need}**\n"
            f"채팅 수: **{info.get('messages', 0)}회**\n"
            f"글자 수: **{info.get('chars', 0)}자**\n"
            f"음성 시간: **{info.get('voice_minutes', 0)}분**"
        ),
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=member.display_avatar.url)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="랭킹", description="서버 레벨 랭킹 TOP 10을 확인합니다.", guild=GUILD)
async def level_ranking(interaction: discord.Interaction):
    if not levels:
        await interaction.response.send_message("아직 랭킹 데이터가 없어!")
        return

    ranking = sorted(
        levels.items(),
        key=lambda item: (
            item[1].get("level", 1),
            item[1].get("xp", 0)
        ),
        reverse=True
    )

    text = ""

    for rank, (uid, info) in enumerate(ranking[:10], start=1):
        member = interaction.guild.get_member(int(uid))

        if member:
            name = member.display_name
        else:
            name = f"알 수 없는 유저({uid})"

        level = info.get("level", 1)
        xp = info.get("xp", 0)

        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}위"

        text += f"{medal} **{name}** - Lv.{level} / {xp} XP\n"

    embed = discord.Embed(
        title="🏆 레벨 랭킹 TOP 10",
        description=text,
        color=discord.Color.gold()
    )

    await interaction.response.send_message(embed=embed)

LEVEL_ROLE_CHANNEL_ID = 1512642190302777415

LEVEL_ROLE_REWARDS = {
    10: 1512443877012017333, 
    30: 1512444146881794058, 
    75: 1512638645176242226, 
    100: 1512638882326511717,
    250: 1512657855356866761,
}

async def give_level_roles(member):
    if member.bot:
        return

    info = get_level_data(member.id)
    user_level = info["level"]

    given_roles = []

    for level, role_id in LEVEL_ROLE_REWARDS.items():
        if user_level >= level:
            role = member.guild.get_role(role_id)

            if role and role not in member.roles:
                try:
                    await member.add_roles(role, reason=f"레벨 {level} 달성 보상")
                    given_roles.append(role)

                except discord.Forbidden:
                    print(f"역할 지급 권한 없음: {member} / {role.name}")

                except discord.HTTPException as e:
                    print(f"역할 지급 실패: {member} / {e}")

    if given_roles:
        channel = member.guild.get_channel(LEVEL_ROLE_CHANNEL_ID)

        if channel:
            roles_text = ", ".join(role.mention for role in given_roles)

@tasks.loop(seconds=15)
async def ranking_update_loop():
    guild = bot.get_guild(GUILD_ID)

    if guild:
        await update_ranking_message(guild)
        
def build_ranking_embed(guild):
    ranking = sorted(
        levels.items(),
        key=lambda item: (
            item[1].get("level", 1),
            item[1].get("xp", 0)
        ),
        reverse=True
    )

    text = ""

    for rank, (uid, info) in enumerate(ranking[:50], start=1):
        member = guild.get_member(int(uid))
        name = member.display_name if member else f"알 수 없는 유저"

        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}위"
        text += f"{medal} **{name}** - Lv.{info.get('level', 1)} / {info.get('xp', 0)} XP\n"

    if not text:
        text = "아직 랭킹 데이터가 없어!"

    return discord.Embed(
        title="🏆 실시간 레벨 랭킹 TOP 50",
        description=text,
        color=discord.Color.gold())

async def update_ranking_message(guild):
    channel = guild.get_channel(RANKING_CHANNEL_ID)
    if not channel:
        print("랭킹 채널을 못 찾음")
        return

    embed = build_ranking_embed(guild)

    message_id = data.get("ranking_message_id")

    if message_id:
        try:
            msg = await channel.fetch_message(int(message_id))
            await msg.edit(embed=embed)
            return
        except discord.NotFound:
            print("기존 랭킹 메시지를 못 찾음. 새로 생성함.")
        except discord.Forbidden:
            print("랭킹 메시지 수정 권한 없음")
            return
        except discord.HTTPException as e:
            print(f"랭킹 메시지 수정 실패: {e}")

    msg = await channel.send(embed=embed)
    data["ranking_message_id"] = msg.id
    save_data()
    print(f"랭킹 메시지 생성됨: {msg.id}")

@bot.tree.command(
    name="레벨증가",
    description="관리자 전용: 유저의 채팅 레벨을 올린다",
    guild=GUILD
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    유저="레벨을 올릴 유저",
    수치="올릴 레벨 수"
)
async def add_chat_level(
    interaction: discord.Interaction,
    유저: discord.Member,
    수치: int
):
    if 수치 <= 0:
        await interaction.response.send_message("❌ 1 이상만 가능.", ephemeral=True)
        return

    info = get_level_data(유저.id)
    old_level = info["level"]

    info["level"] += 수치
    info["xp"] = 0

    save_data()

    await update_level_nickname(유저)
    await give_level_roles(유저)
    await update_ranking_message(interaction.guild)

    await interaction.response.send_message(
        f"✅ {유저.mention} 채팅 레벨 증가 완료!\n"
        f"📈 **Lv.{old_level} → Lv.{info['level']}**"
    )


@bot.tree.command(
    name="레벨감소",
    description="관리자 전용: 유저의 채팅 레벨을 낮춘다",
    guild=GUILD
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    유저="레벨을 낮출 유저",
    수치="낮출 레벨 수"
)
async def remove_chat_level(
    interaction: discord.Interaction,
    유저: discord.Member,
    수치: int
):
    if 수치 <= 0:
        await interaction.response.send_message("❌ 1 이상만 가능.", ephemeral=True)
        return

    info = get_level_data(유저.id)
    old_level = info["level"]

    info["level"] = max(1, info["level"] - 수치)
    info["xp"] = 0

    save_data()

    await update_level_nickname(유저)
    await update_ranking_message(interaction.guild)

    await interaction.response.send_message(
        f"✅ {유저.mention} 채팅 레벨 감소 완료!\n"
        f"📉 **Lv.{old_level} → Lv.{info['level']}**"
    )

CHECKIN_COOLDOWN = timedelta(hours=24)
CHECKIN_MAX_STREAK = 100

def get_checkin_data(user_id):
    uid = str(user_id)
    checkin.setdefault(uid, {
        "last_checkin": None,
        "streak": 0
    })
    return checkin[uid]


@bot.tree.command(name="출첵", description="24시간마다 출석 체크하고 경험치와 모라를 받는다", guild=GUILD)
async def checkin_command(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    now = datetime.now(KST)
    info = get_checkin_data(uid)
    
    last_raw = info.get("last_checkin")
    last_time = datetime.fromisoformat(last_raw) if last_raw else None

    now_reset = now.replace(hour=6, minute=0, second=0, microsecond=0)

    # 오전 6시 이전이면 아직 오늘 리셋 전이므로 어제 6시를 기준으로
    if now < now_reset:
        now_reset -= timedelta(days=1)

    if last_time and last_time >= now_reset:
        next_reset = now_reset + timedelta(days=1)
        left = next_reset - now

        hours = int(left.total_seconds() // 3600)
        minutes = int((left.total_seconds() % 3600) // 60)

        await interaction.response.send_message(
            f"⏳ 오늘은 이미 출첵했어!\n"
            f"다음 초기화까지 **{hours}시간 {minutes}분**",
            ephemeral=True
        )
        return

    # 100일 찍고 다음 출첵부터 초기화
    if info.get("streak", 0) >= CHECKIN_MAX_STREAK:
        info["streak"] = 0

    info["streak"] = info.get("streak", 0) + 1
    info["last_checkin"] = now.isoformat()

    streak = info["streak"]

    xp_reward = 100 + (streak - 1) * 10

    mora_reward = 0
    if streak >= 10:
        mora_reward = 1000 + (streak - 10) * 100
        add_poker_money(uid, mora_reward)

    await add_xp(interaction.user, xp_reward, "출석 체크")

    save_data()

    desc = (
        f"{interaction.user.mention} 출석 완료!\n\n"
        f"🔥 연속 출석: **{streak}일**\n"
        f"⭐ 획득 경험치: **{xp_reward} EXP**"
    )

    if mora_reward > 0:
        desc += f"\n💰 획득 모라: **{mora_reward:,}모라**"
    else:
        desc += "\n💰 모라 보상: **10일 연속 출석부터 지급**"

    if streak >= CHECKIN_MAX_STREAK:
        desc += "\n\n👑 **100일 연속 출석 달성! 다음 출첵부터 연속 출석이 초기화됨.**"

    embed = discord.Embed(
        title="📅 출석 체크",
        description=desc,
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    await interaction.response.send_message(embed=embed)

def get_warning_data(user_id):
    uid = str(user_id)
    warnings.setdefault(uid, [])
    return warnings[uid]


def is_admin_member(member: discord.Member):
    return member.guild_permissions.administrator or member.guild_permissions.manage_guild


class KickConfirmView(discord.ui.View):
    def __init__(self, target_id: int):
        super().__init__(timeout=None)
        self.target_id = target_id

    @discord.ui.button(label="추방하기", style=discord.ButtonStyle.danger)
    async def kick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("❌ 추방 권한이 없어.", ephemeral=True)
            return

        member = interaction.guild.get_member(self.target_id)

        if member is None:
            await interaction.response.edit_message(
                content="❌ 유저가 서버에 없어서 추방할 수 없어.",
                embed=None,
                view=None
            )
            return

        try:
            await member.kick(reason=f"경고 3개 이상으로 {interaction.user}가 추방 버튼 클릭")
        except discord.Forbidden:
            await interaction.response.send_message("❌ 봇 권한이 부족해서 추방 실패.", ephemeral=True)
            return

        await interaction.response.edit_message(
            content=f"✅ {member.mention} 추방 완료.",
            embed=None,
            view=None
        )

    @discord.ui.button(label="취소", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("❌ 권한이 없어.", ephemeral=True)
            return

        await interaction.response.edit_message(
            content="✅ 추방을 취소했어.",
            embed=None,
            view=None
        )


@bot.tree.command(name="경고", description="유저에게 경고를 부여한다", guild=GUILD)
@app_commands.describe(유저="경고를 줄 유저", 사유="경고 사유")
@app_commands.checks.has_permissions(manage_messages=True)
async def warn_command(interaction: discord.Interaction, 유저: discord.Member, 사유: str = "사유 없음"):
    if 유저.bot:
        await interaction.response.send_message("❌ 봇한테는 경고를 줄 수 없어.", ephemeral=True)
        return

    uid = str(유저.id)
    warn_list = get_warning_data(uid)

    warn_list.append({
        "reason": 사유,
        "moderator_id": interaction.user.id,
        "moderator_name": str(interaction.user),
        "created_at": datetime.now(KST).isoformat()
    })

    save_data()

    warn_count = len(warn_list)
    timeout_skipped = False

    if is_admin_member(유저):
        timeout_skipped = True
    else:
        try:
            until = datetime.now(timezone.utc) + WARNING_TIMEOUT
            await 유저.timeout(until, reason=f"경고 부여: {사유}")
        except discord.Forbidden:
            timeout_skipped = True

    embed = discord.Embed(
        title="⚠️ 경고 부여",
        color=discord.Color.red()
    )
    embed.add_field(name="대상", value=f"{유저.mention}\n`{유저}` / `{유저.id}`", inline=False)
    embed.add_field(name="관리자", value=interaction.user.mention, inline=False)
    embed.add_field(name="현재 경고", value=f"**{warn_count}개**", inline=True)
    embed.add_field(name="사유", value=사유, inline=False)

    if timeout_skipped:
        embed.add_field(name="타임아웃", value="생략됨", inline=True)
    else:
        embed.add_field(name="타임아웃", value="1시간", inline=True)

    await interaction.response.send_message(embed=embed)

    log_channel = interaction.guild.get_channel(WARNING_LOG_CHANNEL_ID)

    if log_channel:
        await log_channel.send(embed=embed)

        if warn_count >= 3:
            kick_embed = discord.Embed(
                title="🚨 경고 3개 이상",
                description=(
                    f"{유저.mention}의 경고가 **{warn_count}개**가 됐어.\n"
                    f"이 유저를 추방할 거야?"
                ),
                color=discord.Color.dark_red()
            )
            kick_embed.add_field(name="최근 사유", value=사유, inline=False)
            kick_embed.add_field(name="처리 관리자", value=interaction.user.mention, inline=False)
            kick_embed.set_thumbnail(url=유저.display_avatar.url)

            await log_channel.send(embed=kick_embed, view=KickConfirmView(유저.id))

@warn_command.error
async def warn_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ 관리자 전용 명령어야.", ephemeral=True)

@bot.tree.command(name="경고목록", description="경고 목록을 확인한다", guild=GUILD)
@app_commands.describe(유저="특정 유저만 확인")
@app_commands.checks.has_permissions(manage_messages=True)
async def warning_list_command(interaction: discord.Interaction, 유저: discord.Member = None):
    cleanup_left_warning_users(interaction.guild)
    if 유저:
        warn_list = get_warning_data(유저.id)

        if not warn_list:
            await interaction.response.send_message(f"✅ {유저.mention}은/는 경고가 없어.", ephemeral=True)
            return

        desc = ""
        for i, warn in enumerate(warn_list, start=1):
            desc += (
                f"**{i}.** {warn.get('reason', '사유 없음')}\n"
                f"관리자: <@{warn.get('moderator_id')}>\n"
                f"시간: `{warn.get('created_at', '알 수 없음')}`\n\n"
            )

        embed = discord.Embed(
            title=f"⚠️ {유저.display_name} 경고 목록",
            description=desc[:4000],
            color=discord.Color.orange()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if not warnings:
        await interaction.response.send_message("✅ 경고 먹은 유저가 없어.", ephemeral=True)
        return

    desc = ""
    for uid, warn_list in warnings.items():
        member = interaction.guild.get_member(int(uid))
        name = member.mention if member else f"`알 수 없음 ({uid})`"
        desc += f"{name} - **{len(warn_list)}개**\n"

    embed = discord.Embed(
        title="⚠️ 전체 경고 목록",
        description=desc[:4000],
        color=discord.Color.orange()
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)

def build_user_db_embed(member: discord.Member):
    uid = str(member.id)
    level_info = levels.get(uid, {})
    warn_list = warnings.get(uid, [])

    joined = member.joined_at
    joined_text = f"<t:{int(joined.timestamp())}:F>\n<t:{int(joined.timestamp())}:R>" if joined else "알 수 없음"

    embed = discord.Embed(
        title=f"📁 {member.display_name} 데이터베이스",
        color=discord.Color.blurple()
    )

    embed.add_field(name="유저", value=f"{member.mention}\n`{member}` / `{member.id}`", inline=False)
    embed.add_field(name="서버 접속 시간", value=joined_text, inline=False)
    embed.add_field(name="레벨", value=str(level_info.get("level", 1)), inline=True)
    embed.add_field(name="경험치", value=str(level_info.get("xp", 0)), inline=True)
    embed.add_field(name="메시지 수", value=str(level_info.get("messages", 0)), inline=True)
    embed.add_field(name="글자 수", value=str(level_info.get("chars", 0)), inline=True)
    embed.add_field(name="음성 시간", value=f"{level_info.get('voice_minutes', 0)}분", inline=True)
    embed.add_field(name="경고 횟수", value=f"{len(warn_list)}개", inline=True)
    embed.add_field(name="모라 잔액", value=f"{int(poker_money.get(uid, 0)):,}모라", inline=True)
    embed.add_field(name="원석", value=f"{int(primogems.get(uid, 0)):,}개", inline=True)

    embed.set_thumbnail(url=member.display_avatar.url)
    return embed


class DatabaseUserButton(discord.ui.Button):
    def __init__(self, member: discord.Member):
        super().__init__(
            label=member.display_name[:80],
            style=discord.ButtonStyle.secondary
        )
        self.member_id = member.id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ 권한이 없어.", ephemeral=True)
            return

        member = interaction.guild.get_member(self.member_id)

        if member is None:
            await interaction.response.send_message("❌ 유저를 찾을 수 없어.", ephemeral=True)
            return

        await interaction.response.edit_message(
            embed=build_user_db_embed(member),
            view=DatabaseDetailView()
        )


class DatabaseListView(discord.ui.View):
    def __init__(self, members, page=0):
        super().__init__(timeout=180)
        self.members = members
        self.page = page
        self.per_page = 20

        start = page * self.per_page
        end = start + self.per_page

        for member in members[start:end]:
            self.add_item(DatabaseUserButton(member))

        if page > 0:
            self.add_item(DatabasePrevButton())

        if end < len(members):
            self.add_item(DatabaseNextButton())

        self.add_item(DatabaseCloseButton())


class DatabasePrevButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="이전", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        await interaction.response.edit_message(
            embed=build_database_list_embed(view.members, view.page - 1, view.per_page),
            view=DatabaseListView(view.members, view.page - 1)
        )


class DatabaseNextButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="다음", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        await interaction.response.edit_message(
            embed=build_database_list_embed(view.members, view.page + 1, view.per_page),
            view=DatabaseListView(view.members, view.page + 1)
        )


class DatabaseDetailView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="뒤로가기", style=discord.ButtonStyle.primary)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        members = sorted(
            [m for m in interaction.guild.members if not m.bot],
            key=lambda m: m.display_name
        )

        await interaction.response.edit_message(
            embed=build_database_list_embed(members, 0, 20),
            view=DatabaseListView(members, 0)
        )

    @discord.ui.button(label="닫기", style=discord.ButtonStyle.danger)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="✅ 데이터베이스를 닫았어.",
            embed=None,
            view=None
        )


class DatabaseCloseButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="닫기", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="✅ 데이터베이스를 닫았어.",
            embed=None,
            view=None
        )


def build_database_list_embed(members, page, per_page):
    start = page * per_page
    end = start + per_page
    page_members = members[start:end]

    desc = "\n".join(
        f"• {member.mention} `({member.id})`"
        for member in page_members
    )

    embed = discord.Embed(
        title="📁 서버 데이터베이스",
        description=desc if desc else "표시할 유저가 없어.",
        color=discord.Color.blurple()
    )

    max_page = max(1, (len(members) + per_page - 1) // per_page)
    embed.set_footer(text=f"{page + 1} / {max_page} 페이지")

    return embed


@bot.tree.command(name="데이터베이스", description="서버 유저 데이터베이스를 확인한다", guild=GUILD)
@app_commands.checks.has_permissions(manage_guild=True)
async def database_command(interaction: discord.Interaction):
    members = sorted(
        [m for m in interaction.guild.members if not m.bot],
        key=lambda m: m.display_name
    )

    await interaction.response.send_message(
        embed=build_database_list_embed(members, 0, 20),
        view=DatabaseListView(members, 0),
        ephemeral=True
    )


@database_command.error
async def database_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ 관리자 전용 명령어야.", ephemeral=True)

def cleanup_left_warning_users(guild: discord.Guild):
    removed = []

    for uid in list(warnings.keys()):
        member = guild.get_member(int(uid))

        # 서버에 없는 유저면 경고 데이터 삭제
        if member is None:
            removed.append(uid)
            del warnings[uid]

    if removed:
        save_data()

    return removed

@bot.tree.command(name="경고차감", description="유저의 경고를 차감한다", guild=GUILD)
@app_commands.describe(
    유저="경고를 차감할 유저",
    개수="차감할 경고 개수",
    사유="차감 사유"
)
@app_commands.checks.has_permissions(manage_messages=True)
async def warning_remove_command(
    interaction: discord.Interaction,
    유저: discord.Member,
    개수: int = 1,
    사유: str = "사유 없음"
):
    if 개수 <= 0:
        await interaction.response.send_message("❌ 차감 개수는 1 이상이어야 해.", ephemeral=True)
        return

    uid = str(유저.id)
    warn_list = warnings.get(uid, [])

    if not warn_list:
        await interaction.response.send_message(
            f"✅ {유저.mention}은/는 차감할 경고가 없어.",
            ephemeral=True
        )
        return

    before_count = len(warn_list)
    remove_count = min(개수, before_count)

    # 최신 경고부터 제거
    for _ in range(remove_count):
        warn_list.pop()

    if warn_list:
        warnings[uid] = warn_list
    else:
        warnings.pop(uid, None)

    save_data()

    embed = discord.Embed(
        title="✅ 경고 차감",
        color=discord.Color.green()
    )
    embed.add_field(name="대상", value=f"{유저.mention}\n`{유저}` / `{유저.id}`", inline=False)
    embed.add_field(name="처리 관리자", value=interaction.user.mention, inline=False)
    embed.add_field(name="차감 개수", value=f"{remove_count}개", inline=True)
    embed.add_field(name="기존 경고", value=f"{before_count}개", inline=True)
    embed.add_field(name="현재 경고", value=f"{len(warn_list)}개", inline=True)
    embed.add_field(name="사유", value=사유, inline=False)

    await interaction.response.send_message(embed=embed)

    # 여기 추가
    log_channel = interaction.guild.get_channel(WARNING_LOG_CHANNEL_ID)

    if log_channel:
        await log_channel.send(embed=embed)

@warning_remove_command.error
async def warning_remove_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ 관리자 전용 명령어야.", ephemeral=True)

@bot.event
async def on_app_command_completion(
    interaction: discord.Interaction,
    command: app_commands.Command
):
    if not interaction.guild:
        return

    channel = interaction.guild.get_channel(COMMAND_LOG_CHANNEL_ID)
    if not channel:
        return

    command_name = command.qualified_name
    admin_perms = (
        interaction.user.guild_permissions.administrator
        or interaction.user.guild_permissions.manage_guild
        or interaction.user.guild_permissions.manage_messages
        or interaction.user.guild_permissions.kick_members
        or interaction.user.guild_permissions.ban_members
    )
    
    command_name = interaction.command.qualified_name if interaction.command else command.qualified_name
    
    ADMIN_COMMAND_NAMES = {
        "경고",
        "경고차감",
        "경고목록",
        "데이터베이스",
        "레벨증가",
        "레벨감소",
        "돈주기",
        "돈차감",
        "레벨증가",
        "레벨감소",
        "스탯포인트",
        "스탯포인트차감",
        "스탯차감"
    }
    
    is_admin_command = (
        command_name in ADMIN_COMMAND_NAMES
        or command_name.split()[-1] in ADMIN_COMMAND_NAMES
    )

    embed = discord.Embed(
        title="📜 푸리나 명령어 로그",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="사용된 명령어",
        value=f"`/{command_name}`",
        inline=True
    )

    embed.add_field(
        name="사용자",
        value=f"{interaction.user.mention}\n`{interaction.user}` / `{interaction.user.id}`",
        inline=False
    )

    embed.add_field(
        name="관리자 명령어 여부",
        value="✅ 관리자 명령어" if is_admin_command else "❌ 일반 명령어",
        inline=True
    )

    embed.add_field(
        name="사용 채널",
        value=interaction.channel.mention if interaction.channel else "알 수 없음",
        inline=True
    )

    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.timestamp = datetime.now(timezone.utc)

    await channel.send(embed=embed)

async def refresh_sticky_message(channel):
    global sticky_message_sending

    async with sticky_message_lock:
        sticky_message_sending = True

        try:
            old_message_id = data.get("sticky_message_id")

            # 이전 안내 메시지 삭제
            if old_message_id:
                try:
                    old_message = await channel.fetch_message(
                        int(old_message_id)
                    )
                    await old_message.delete()

                except discord.NotFound:
                    pass

                except discord.Forbidden:
                    print("스티키 메시지 삭제 권한 없음")
                    return

                except discord.HTTPException as e:
                    print(f"스티키 메시지 삭제 실패: {e}")
                    return

            # 새로운 안내 메시지 전송
            new_message = await channel.send(
                STICKY_MESSAGE,
                allowed_mentions=discord.AllowedMentions.none()
            )

            # send 다음에는 await가 없어서 바로 ID가 저장됨
            data["sticky_message_id"] = new_message.id
            save_data()

        except discord.Forbidden:
            print("스티키 메시지 전송 권한 없음")

        except discord.HTTPException as e:
            print(f"스티키 메시지 전송 실패: {e}")

        finally:
            sticky_message_sending = False


@bot.listen("on_message")
async def sticky_message_listener(message):
    # 지정된 채널만 감지
    if message.channel.id != STICKY_CHANNEL_ID:
        return

    current_sticky_id = data.get("sticky_message_id")

    # 현재 안내 메시지 자체는 무시
    if current_sticky_id:
        if message.id == int(current_sticky_id):
            return

    # 안내 메시지를 보내는 도중 발생한 자기 메시지는 무시
    if (
        bot.user
        and message.author.id == bot.user.id
        and sticky_message_sending
    ):
        return

    # 저장 타이밍이나 재시작 상황을 위한 보조 검사
    if (
        bot.user
        and message.author.id == bot.user.id
        and message.content.strip() == STICKY_MESSAGE.strip()
    ):
        return

    await refresh_sticky_message(message.channel)



# =========================
# 모험 / 전리품 / 유물 시스템
# =========================

ADVENTURE_MAX_EQUIPPED = 3
ADVENTURE_INVENTORY_PAGE_SIZE = 10
ADVENTURE_RELIC_PAGE_SIZE = 10

# 한 번 이동했을 때 일반 몬스터를 만날 기본 확률.
# 기본 35%이며, 몬스터가 나오지 않은 턴마다 15%p씩 올라 최대 80%가 된다.
# 보스 출현 판정은 이 확률과 별개로 매 턴 진행된다.
ADVENTURE_MONSTER_EVENT_RATE = 35.0
ADVENTURE_MONSTER_PITY_PER_TURN = 15.0
ADVENTURE_MONSTER_EVENT_RATE_MAX = 80.0

# 턴 대기 시간은 연출용일 뿐이며 몬스터 난이도에는 절대 반영되지 않는다.
ADVENTURE_TURN_MIN_SECONDS = 5
ADVENTURE_TURN_MAX_SECONDS = 20

# 몬스터는 오직 완료한 턴 수에 따라 조금씩 강해진다.
# 1턴당 위험도 0.70, 실제 몬스터 목표 레벨에는 위험도의 0.65배가 반영된다.
ADVENTURE_DANGER_PER_TURN = 0.70
ADVENTURE_MONSTER_DANGER_LEVEL_MUL = 0.65

# 모험 몬스터 전용 너프 수치. /사냥 몬스터 밸런스에는 영향을 주지 않는다.
ADVENTURE_BASE_WIN_CHANCE = 56
ADVENTURE_MONSTER_PENALTY_MUL = 0.32
ADVENTURE_MONSTER_PENALTY_BASE_CAP = 12
ADVENTURE_MONSTER_PENALTY_PER_LEVEL_CAP = 1.4
ADVENTURE_EXTRA_LEVEL_PENALTY_MUL = 0.35
ADVENTURE_TRAIT_POWER_SCALE = 0.55
ADVENTURE_BOSS_LEVEL_BONUS = 4

# 모험 레벨은 스탯 배분 없이 자동으로 승률을 올린다.
ADVENTURE_LEVEL_WIN_BONUS = 0.7
ADVENTURE_LEVEL_WIN_BONUS_CAP = 35.0

# 전투 승리 시 모험 장비 발견 확률. 장비는 돈으로 구매할 수 없다.
ADVENTURE_EQUIPMENT_DROP_RATES = {
    "normal": 7.0,
    "elite": 22.0,
    "calamity": 55.0,
    "boss": 100.0,
}

# 몬스터 조우 후 등급 판정:
# 일반 89% / 강적 10% / 재앙급 1%
ADVENTURE_MONSTER_TIERS = {
    "normal": {
        "name": "일반",
        "prefix": "",
        "level_mul": 1.0,
        "level_flat": 0,
        "reward_mul": 1.0,
        "exp_mul": 1.0,
        "loot_bonus": 0,
    },
    "elite": {
        "name": "강적",
        "prefix": "🔥 강적",
        "level_mul": 1.18,
        "level_flat": 2,
        "reward_mul": 2.2,
        "exp_mul": 2.0,
        "loot_bonus": 1,
    },
    "calamity": {
        "name": "재앙급",
        "prefix": "☠️ 재앙급",
        "level_mul": 1.70,
        "level_flat": 8,
        "reward_mul": 8.0,
        "exp_mul": 8.0,
        "loot_bonus": 3,
    },
}

ADVENTURE_START_TERRAINS = ["desert", "grassland", "jungle"]

ADVENTURE_TERRAINS = {
    "desert": {
        "name": "사막",
        "emoji": "🏜️",
        "color": 0xD9A441,
        "description": "끝없이 펼쳐진 모래와 폐허가 길을 가로막는다.",
        "danger_mul": 0.95,
        "danger_flat": 0,
        "reward_mul": 1.05,
        "boss": "반영구 제어 매트릭스",
        "monsters": [
            "슬라임", "츄츄족", "보물 사냥단", "성해 짐승",
            "유적 드레이크", "반영구 제어 매트릭스",
        ],
    },
    "grassland": {
        "name": "초원",
        "emoji": "🌾",
        "color": 0x67A84F,
        "description": "바람이 잔잔한 초원. 평화로워 보여도 곳곳에 적이 숨어 있다.",
        "danger_mul": 1.0,
        "danger_flat": 0,
        "reward_mul": 1.0,
        "boss": "철갑 용 도마뱀",
        "monsters": [
            "슬라임", "츄츄족", "츄츄 폭도", "보물 사냥단",
            "유적 가드", "철갑 용 도마뱀",
        ],
    },
    "jungle": {
        "name": "정글",
        "emoji": "🌴",
        "color": 0x247A46,
        "description": "빛조차 잘 들지 않는 밀림. 독기와 짐승의 울음이 가득하다.",
        "danger_mul": 1.04,
        "danger_flat": 1,
        "reward_mul": 1.12,
        "boss": "아펩의 수호자",
        "monsters": [
            "슬라임", "츄츄족", "심연 메이지", "성해 짐승",
            "수계 사냥개 무리", "아펩의 수호자",
        ],
    },
    "cave": {
        "name": "동굴",
        "emoji": "🕳️",
        "color": 0x5B4B66,
        "description": "지하 깊은 곳으로 이어지는 동굴. 오래된 기계음이 메아리친다.",
        "danger_mul": 1.10,
        "danger_flat": 4,
        "reward_mul": 1.22,
        "boss": "유적 서펜트",
        "monsters": [
            "심연 메이지", "유적 가드", "유적 헌터", "원해 짐승",
            "유적 서펜트", "영겁의 드레이크",
        ],
    },
    "mountain": {
        "name": "고산지대",
        "emoji": "⛰️",
        "color": 0x73808F,
        "description": "숨이 가빠지는 높은 산맥. 강풍 너머로 낯선 문이 보인다.",
        "danger_mul": 1.16,
        "danger_flat": 8,
        "reward_mul": 1.38,
        "boss": "영겁의 드레이크",
        "monsters": [
            "츄츄 폭도", "우인단 선발대", "유적 헌터", "검귀",
            "유적 드레이크", "영겁의 드레이크",
        ],
    },
    "ice": {
        "name": "얼음 지대",
        "emoji": "❄️",
        "color": 0x8ED6EA,
        "description": "모든 것이 얼어붙은 땅. 발을 멈추면 냉기가 뼛속까지 스민다.",
        "danger_mul": 1.24,
        "danger_flat": 12,
        "reward_mul": 1.55,
        "boss": "황금 늑대왕",
        "monsters": [
            "우인단 선발대", "거울의 여인", "검귀", "수계 사냥개 무리",
            "황금 늑대왕", "철갑 용 도마뱀",
        ],
    },
    "demon": {
        "name": "마계",
        "emoji": "😈",
        "color": 0x6C1738,
        "description": "붉은 하늘 아래 마력이 끓어오르는 세계. 약한 자는 존재조차 버티지 못한다.",
        "danger_mul": 1.45,
        "danger_flat": 25,
        "reward_mul": 2.4,
        "boss": "마왕",
        "monsters": [
            "심연 메이지", "심연 사도", "심연 영창자", "원해 짐승",
            "라이덴 쇼군", "마왕",
        ],
    },
    "heaven": {
        "name": "천계",
        "emoji": "☁️",
        "color": 0xF2D77A,
        "description": "구름 위 신성한 세계. 아름답지만 허락받지 않은 자에겐 가장 잔혹하다.",
        "danger_mul": 1.65,
        "danger_flat": 40,
        "reward_mul": 3.2,
        "boss": "천리의 유지자",
        "monsters": [
            "자율 초정밀 태엽장치", "영겁의 드레이크", "타르탈리아",
            "라이덴 쇼군", "천리의 유지자",
        ],
    },
}

# 이동 가능한 방향. 마계는 고산지대/얼음 지대에서만,
# 천계는 마계에서만 진입할 수 있다.
ADVENTURE_TERRAIN_ROUTES = {
    "desert": ["grassland", "jungle", "cave"],
    "grassland": ["desert", "jungle", "cave", "mountain"],
    "jungle": ["desert", "grassland", "cave", "mountain"],
    "cave": ["desert", "jungle", "mountain", "ice"],
    "mountain": ["grassland", "cave", "ice", "demon"],
    "ice": ["cave", "mountain", "demon"],
    "demon": ["mountain", "ice", "heaven"],
    "heaven": [],
}

# 이 유물을 해당 지형에서 얻으면 갈림길이 확정적으로 열린다.
# 유물의 실제 표시 이름은 최초 발견자가 정한다.
ADVENTURE_ROUTE_RELICS = {
    "relic_012": {"source": "desert", "destinations": ["jungle", "cave"]},
    "relic_025": {"source": "grassland", "destinations": ["cave", "mountain"]},
    "relic_038": {"source": "jungle", "destinations": ["cave", "mountain"]},
    "relic_051": {"source": "cave", "destinations": ["mountain", "ice"]},
    "relic_064": {"source": "mountain", "destinations": ["ice", "demon"]},
    "relic_077": {"source": "ice", "destinations": ["mountain", "demon"]},
    "relic_090": {"source": "demon", "destinations": ["heaven"]},
}

ADVENTURE_TERRAIN_DEPTH = {
    "desert": 1,
    "grassland": 1,
    "jungle": 1,
    "cave": 2,
    "mountain": 3,
    "ice": 4,
    "demon": 5,
    "heaven": 6,
}

ADVENTURE_RANDOM_ROUTE_RATE = 2.5

# 같은 지형에서 5턴을 넘긴 뒤부터 매 턴 보스 출현 확률이 증가한다.
# 6턴째 1.5%에서 시작해 매 턴 1.25%p씩 상승하고 최대 20%까지 오른다.
ADVENTURE_BOSS_MIN_TERRAIN_STEPS = 5
ADVENTURE_BOSS_BASE_RATE = 1.5
ADVENTURE_BOSS_RATE_PER_STEP = 1.25
ADVENTURE_BOSS_MAX_RATE = 20.0


def get_terrain_info(terrain_key):
    return ADVENTURE_TERRAINS.get(terrain_key, ADVENTURE_TERRAINS["grassland"])


def get_terrain_name(terrain_key):
    terrain = get_terrain_info(terrain_key)
    return f"{terrain['emoji']} {terrain['name']}"


def valid_terrain_destinations(source, destinations=None):
    allowed = ADVENTURE_TERRAIN_ROUTES.get(source, [])
    if destinations is None:
        destinations = allowed

    result = []
    for destination in destinations:
        # 마계 진입은 고산지대와 얼음 지대에서만 허용한다.
        if destination == "demon" and source not in {"mountain", "ice"}:
            continue
        # 천계 진입은 마계에서만 허용한다.
        if destination == "heaven" and source != "demon":
            continue
        if destination in allowed and destination in ADVENTURE_TERRAINS and destination not in result:
            result.append(destination)
    return result


ADVENTURE_RARITIES = {
    "common": {"name": "일반", "emoji": "⚪", "value_mul": 1.0},
    "uncommon": {"name": "고급", "emoji": "🟢", "value_mul": 1.8},
    "rare": {"name": "희귀", "emoji": "🔵", "value_mul": 3.2},
    "epic": {"name": "영웅", "emoji": "🟣", "value_mul": 6.0},
    "legendary": {"name": "전설", "emoji": "🟡", "value_mul": 12.0},
    "mythic": {"name": "신화", "emoji": "🔴", "value_mul": 25.0},
}

ADVENTURE_RARITY_ORDER = {
    "common": 0,
    "uncommon": 1,
    "rare": 2,
    "epic": 3,
    "legendary": 4,
    "mythic": 5,
}

ADVENTURE_DROP_WEIGHTS = {
    "common": 70,
    "uncommon": 35,
    "rare": 13,
    "epic": 4,
    "legendary": 0.8,
    "mythic": 0.12,
}

ADVENTURE_SHOP_CATALOG = {
    "낡은 나침반": {
        "price": 800,
        "desc": "좋은 사건과 재료를 만날 확률이 조금 증가한다.",
        "luck": 5,
    },
    "철제 숫돌": {
        "price": 1200,
        "desc": "모험 전투 승률이 증가한다.",
        "battle": 6,
    },
    "행운 부적": {
        "price": 1800,
        "desc": "높은 등급 전리품 확률이 증가한다.",
        "loot": 9,
    },
    "연막탄": {
        "price": 2200,
        "desc": "도주 성공률이 증가한다.",
        "escape": 18,
    },
    "응급 약초": {
        "price": 2800,
        "desc": "패배 시 목숨을 지킬 확률이 증가한다.",
        "life_save": 12,
    },
    "수상한 지도": {
        "price": 4500,
        "desc": "이름 없는 유물을 발견할 확률이 증가한다.",
        "relic": 3.5,
    },
    "푸리나의 찻잔": {
        "price": 9000,
        "desc": "전투와 행운을 함께 조금 올려준다.",
        "battle": 5,
        "luck": 5,
        "loot": 5,
    },
    "심해의 등불": {
        "price": 16000,
        "desc": "유물 발견률과 도주 성공률을 크게 올린다.",
        "relic": 5.0,
        "escape": 12,
    },
    "생명의 깃털": {
        "price": 24000,
        "desc": "장착한 채 모험을 시작하면 최대 목숨이 1개 증가한다.",
        "max_lives": 1,
    },
}

adventure_action_locks = {}


def get_adventure_lock(uid):
    uid = str(uid)
    if uid not in adventure_action_locks:
        adventure_action_locks[uid] = asyncio.Lock()
    return adventure_action_locks[uid]


def get_adventure(uid):
    uid = str(uid)

    if uid not in adventures or not isinstance(adventures[uid], dict):
        adventures[uid] = {}

    adventure = adventures[uid]

    defaults = {
        "active": False,
        "started_at": None,
        "thread_id": None,
        "steps": 0,
        "kills": 0,
        "earned_mora": 0,
        "lives": 3,
        "max_lives": 3,
        "turn_started_at": None,
        "turn_ready_at": None,
        "turn_duration_seconds": 0,
        "pending_event": None,
        "pending_name_item_id": None,
        "terrain": None,
        "terrain_steps": 0,
        "quiet_turns": 0,  # 몬스터 없이 지나간 연속 턴 수
        "visited_terrains": [],
        "defeated_bosses": [],
        "best_terrain_rank": 0,
        "best_steps": 0,
        "best_kills": 0,
        "total_runs": 0,
        "total_kills": 0,

        # /사냥과 완전히 분리된 모험 전용 성장 데이터
        "level": 1,
        "exp": 0,
        "weapon": "무인검",
        "armor": "모험가 세트",
        "owned_weapons": ["무인검"],
        "owned_armors": ["모험가 세트"],

        "boosts": {
            "battle": 0,
            "luck": 0,
            "loot": 0,
            "escape": 0,
            "life_save": 0,
            "relic": 0,
            "max_lives": 0,
        },
    }

    for key, value in defaults.items():
        if key not in adventure:
            if isinstance(value, dict):
                adventure[key] = value.copy()
            elif isinstance(value, list):
                adventure[key] = value.copy()
            else:
                adventure[key] = value

    # 예전 데이터나 손상된 데이터를 모험 전용 기본 장비로 복구한다.
    if not isinstance(adventure.get("owned_weapons"), list):
        adventure["owned_weapons"] = ["무인검"]
    if not isinstance(adventure.get("owned_armors"), list):
        adventure["owned_armors"] = ["모험가 세트"]

    adventure["owned_weapons"] = [name for name in adventure["owned_weapons"] if name in WEAPONS]
    adventure["owned_armors"] = [name for name in adventure["owned_armors"] if name in ARMORS]

    if "무인검" not in adventure["owned_weapons"]:
        adventure["owned_weapons"].insert(0, "무인검")
    if "모험가 세트" not in adventure["owned_armors"]:
        adventure["owned_armors"].insert(0, "모험가 세트")

    if adventure.get("weapon") not in adventure["owned_weapons"]:
        adventure["weapon"] = "무인검"
    if adventure.get("armor") not in adventure["owned_armors"]:
        adventure["armor"] = "모험가 세트"

    adventure["level"] = max(1, int(adventure.get("level", 1)))
    adventure["exp"] = max(0, int(adventure.get("exp", 0)))
    adventure["max_lives"] = max(3, int(adventure.get("max_lives", 3)))
    adventure["lives"] = max(0, min(int(adventure.get("lives", 3)), adventure["max_lives"]))

    # 지형 시스템 추가 전부터 진행 중이던 모험은 초원에서 이어진다.
    if adventure.get("active") and adventure.get("terrain") not in ADVENTURE_TERRAINS:
        adventure["terrain"] = "grassland"
        adventure["terrain_steps"] = 0
        adventure["visited_terrains"] = ["grassland"]

    return adventure


def get_adventure_inventory(uid):
    uid = str(uid)

    if uid not in inventories or not isinstance(inventories[uid], dict):
        inventories[uid] = {}

    return inventories[uid]


def get_adventure_shop_user(uid):
    uid = str(uid)

    if uid not in shop_items or not isinstance(shop_items[uid], dict):
        shop_items[uid] = {
            "owned": [],
            "equipped": [],
        }

    info = shop_items[uid]
    info.setdefault("owned", [])
    info.setdefault("equipped", [])

    # 예전 형식이나 잘못된 데이터가 있어도 복구
    if not isinstance(info["owned"], list):
        info["owned"] = list(info["owned"])
    if not isinstance(info["equipped"], list):
        info["equipped"] = list(info["equipped"])

    info["owned"] = [name for name in info["owned"] if name in ADVENTURE_SHOP_CATALOG]
    info["equipped"] = [
        name
        for name in info["equipped"]
        if name in info["owned"] and name in ADVENTURE_SHOP_CATALOG
    ][:ADVENTURE_MAX_EQUIPPED]

    return info


def get_equipped_adventure_boosts(uid):
    info = get_adventure_shop_user(uid)

    boosts = {
        "battle": 0,
        "luck": 0,
        "loot": 0,
        "escape": 0,
        "life_save": 0,
        "relic": 0,
        "max_lives": 0,
    }

    for item_name in info["equipped"]:
        item = ADVENTURE_SHOP_CATALOG.get(item_name, {})
        for key in boosts:
            boosts[key] += item.get(key, 0)

    return boosts



def get_adventure_required_exp(level):
    """모험 전용 레벨 요구 경험치. /사냥 레벨과는 전혀 공유하지 않는다."""
    return get_required_exp(max(1, int(level)))


def give_adventure_exp(adventure, amount):
    adventure["exp"] = max(0, int(adventure.get("exp", 0)) + int(amount))
    leveled = 0

    while adventure["exp"] >= get_adventure_required_exp(adventure["level"]):
        adventure["exp"] -= get_adventure_required_exp(adventure["level"])
        adventure["level"] += 1
        leveled += 1

    return leveled


def calc_adventure_win_chance(adventure, monster, monster_level, trait=None):
    """스탯창 없이 모험 레벨과 현재 장비만으로 승률을 계산한다."""
    player_level = max(1, int(adventure.get("level", 1)))
    weapon_name = adventure.get("weapon", "무인검")
    armor_name = adventure.get("armor", "모험가 세트")
    weapon_bonus = WEAPONS.get(weapon_name, WEAPONS["무인검"])["bonus"]
    armor_bonus = ARMORS.get(armor_name, ARMORS["모험가 세트"])["bonus"]

    level_bonus = min(
        ADVENTURE_LEVEL_WIN_BONUS_CAP,
        max(0, player_level - 1) * ADVENTURE_LEVEL_WIN_BONUS,
    )

    # 모험 전투만 별도로 완화한다. /사냥의 몬스터 수치는 그대로 유지된다.
    raw_monster_penalty = monster.get("penalty", monster.get("peanlty", 0))
    penalty_cap = (
        ADVENTURE_MONSTER_PENALTY_BASE_CAP
        + monster_level * ADVENTURE_MONSTER_PENALTY_PER_LEVEL_CAP
    )
    monster_penalty = min(raw_monster_penalty, penalty_cap)

    chance = ADVENTURE_BASE_WIN_CHANCE
    chance += level_bonus
    chance += (player_level - monster_level) * 2.4
    chance += weapon_bonus * 0.9
    chance += armor_bonus * 0.7
    chance -= monster_penalty * ADVENTURE_MONSTER_PENALTY_MUL
    chance -= max(0, monster_level - player_level) * ADVENTURE_EXTRA_LEVEL_PENALTY_MUL
    chance += adventure.get("boosts", {}).get("battle", 0)

    if trait:
        raw_power = max(0.1, float(trait.get("monster_power", 1)))
        softened_power = 1 + (raw_power - 1) * ADVENTURE_TRAIT_POWER_SCALE
        chance /= max(0.25, softened_power)

    return max(8, min(97, int(chance)))


def calc_adventure_escape_chance(adventure):
    player_level = max(1, int(adventure.get("level", 1)))
    armor_name = adventure.get("armor", "모험가 세트")
    armor_bonus = ARMORS.get(armor_name, ARMORS["모험가 세트"])["bonus"]
    escape_bonus = adventure.get("boosts", {}).get("escape", 0)

    chance = 48 + player_level * 0.35 + armor_bonus * 0.12 + escape_bonus
    return max(20, min(92, int(chance)))


def calc_adventure_hospital_fee(money):
    # /사냥의 체력 스탯 할인과 호환되지 않는다.
    final_rate = 0.07
    return int(max(0, money) * final_rate), final_rate


def get_adventure_boss_spawn_rate(adventure, next_turn=False):
    terrain_key = adventure.get("terrain") or "grassland"
    defeated = set(adventure.get("defeated_bosses", []))
    terrain_steps = max(0, int(adventure.get("terrain_steps", 0)))
    if next_turn:
        terrain_steps += 1

    if terrain_key in defeated or terrain_steps <= ADVENTURE_BOSS_MIN_TERRAIN_STEPS:
        return 0.0

    extra_turns = terrain_steps - (ADVENTURE_BOSS_MIN_TERRAIN_STEPS + 1)
    return min(
        ADVENTURE_BOSS_MAX_RATE,
        ADVENTURE_BOSS_BASE_RATE + max(0, extra_turns) * ADVENTURE_BOSS_RATE_PER_STEP,
    )


def get_adventure_monster_spawn_rate(adventure):
    """다음 일반 몬스터 조우 확률. 평화로운 턴이 이어질수록 확률이 오른다."""
    quiet_turns = max(0, int(adventure.get("quiet_turns", 0)))
    boosts = adventure.get("boosts", {})
    good_event_shift = min(12.0, boosts.get("luck", 0) * 0.6)

    rate = (
        ADVENTURE_MONSTER_EVENT_RATE
        + quiet_turns * ADVENTURE_MONSTER_PITY_PER_TURN
        - good_event_shift * 0.20
    )
    return max(5.0, min(ADVENTURE_MONSTER_EVENT_RATE_MAX, rate))


def get_adventure_equipment_text(adventure):
    return (
        f"🗡️ {adventure.get('weapon', '무인검')} · "
        f"🛡️ {adventure.get('armor', '모험가 세트')}"
    )


def reset_adventure_run_equipment(adventure):
    """병원행일 때만 이번 모험에서 얻은 장비를 전부 잃는다."""
    lost_weapons = [name for name in adventure.get("owned_weapons", []) if name != "무인검"]
    lost_armors = [name for name in adventure.get("owned_armors", []) if name != "모험가 세트"]

    adventure["weapon"] = "무인검"
    adventure["armor"] = "모험가 세트"
    adventure["owned_weapons"] = ["무인검"]
    adventure["owned_armors"] = ["모험가 세트"]
    return lost_weapons, lost_armors


def roll_adventure_equipment_drop(adventure, monster_tier="normal", is_boss=False):
    """장비는 전투 보상으로만 획득한다."""
    rate_key = "boss" if is_boss else monster_tier
    drop_rate = ADVENTURE_EQUIPMENT_DROP_RATES.get(rate_key, 0.0)
    drop_rate += min(5.0, adventure.get("boosts", {}).get("loot", 0) * 0.15)
    if random.random() * 100 >= drop_rate:
        return None

    owned_weapons = set(adventure.get("owned_weapons", []))
    owned_armors = set(adventure.get("owned_armors", []))
    depth = ADVENTURE_TERRAIN_DEPTH.get(adventure.get("terrain"), 0)
    player_level = max(1, int(adventure.get("level", 1)))
    allowed_bonus = 5 + player_level * 0.8 + depth * 3.5 + adventure.get("terrain_steps", 0) * 0.35

    weapon_candidates = [
        name for name, info in WEAPONS.items()
        if name != "무인검" and name not in owned_weapons and info.get("bonus", 0) <= allowed_bonus
    ]
    armor_candidates = [
        name for name, info in ARMORS.items()
        if name != "모험가 세트" and name not in owned_armors and info.get("bonus", 0) <= allowed_bonus
    ]

    if not weapon_candidates and not armor_candidates:
        weapon_candidates = [name for name in WEAPONS if name != "무인검" and name not in owned_weapons]
        armor_candidates = [name for name in ARMORS if name != "모험가 세트" and name not in owned_armors]

    kinds = []
    if weapon_candidates:
        kinds.append("weapon")
    if armor_candidates:
        kinds.append("armor")
    if not kinds:
        return None

    kind = random.choice(kinds)
    if kind == "weapon":
        name = random.choice(weapon_candidates)
        adventure.setdefault("owned_weapons", ["무인검"]).append(name)
        return {"kind": "weapon", "name": name, "bonus": WEAPONS[name]["bonus"]}

    name = random.choice(armor_candidates)
    adventure.setdefault("owned_armors", ["모험가 세트"]).append(name)
    return {"kind": "armor", "name": name, "bonus": ARMORS[name]["bonus"]}


def build_adventure_item_catalog():
    """코드 몇 줄로 400종이 넘는 전리품을 만든다."""
    catalog = {}
    terrain_keys = list(ADVENTURE_TERRAINS.keys())

    monster_parts = [
        ("흔적", "common", 12),
        ("파편", "common", 18),
        ("핵", "uncommon", 35),
        ("정수", "rare", 80),
        ("심장", "epic", 180),
        ("왕관", "legendary", 450),
    ]

    for monster_index, monster in enumerate(MONSTERS):
        for part_index, (part_name, rarity, base_value) in enumerate(monster_parts):
            item_id = f"monster_{monster_index:03d}_{part_index:02d}"
            catalog[item_id] = {
                "name": f"{monster['name']}의 {part_name}",
                "kind": "monster_loot",
                "rarity": rarity,
                "value": base_value + monster_index * 8,
                "source_monster": monster["name"],
                "custom_name": False,
            }

    prefixes = [
        "새벽빛", "해질녘", "푸른", "붉은", "은빛", "금빛",
        "고요한", "울부짖는", "메마른", "축축한", "별무늬", "심해의",
    ]

    world_materials = [
        ("약초", "herb"),
        ("버섯", "herb"),
        ("꽃잎", "herb"),
        ("뿌리", "herb"),
        ("광석", "ore"),
        ("결정", "ore"),
        ("모래", "material"),
        ("깃털", "material"),
        ("나뭇가지", "material"),
        ("물방울", "material"),
        ("조개", "material"),
        ("유리조각", "material"),
    ]

    for prefix_index, prefix in enumerate(prefixes):
        for material_index, (base_name, kind) in enumerate(world_materials):
            item_id = f"world_{prefix_index:02d}_{material_index:02d}"
            score = prefix_index + material_index

            if score >= 20:
                rarity = "epic"
            elif score >= 15:
                rarity = "rare"
            elif score >= 8:
                rarity = "uncommon"
            else:
                rarity = "common"

            catalog[item_id] = {
                "name": f"{prefix} {base_name}",
                "kind": kind,
                "rarity": rarity,
                "value": 10 + score * 6,
                "source_monster": None,
                "custom_name": False,
                "terrain": terrain_keys[(prefix_index + material_index) % len(terrain_keys)],
            }

    terrain_materials = {
        "desert": ["태양 선인장", "유리 모래", "전갈 독침", "사막 장미", "고대 토기", "열풍 결정"],
        "grassland": ["바람풀", "들꽃 꿀", "푸른 씨앗", "초원 양털", "맑은 이슬", "야생 곡식"],
        "jungle": ["독버섯", "거대 잎사귀", "덩굴 수액", "밀림 열매", "맹수 발톱", "녹빛 원석"],
        "cave": ["박쥐 날개", "암흑 수정", "동굴 이끼", "고대 철편", "석회 진주", "메아리석"],
        "mountain": ["독수리 깃", "고산 약초", "운철 조각", "산맥 수정", "폭풍석", "구름 이끼"],
        "ice": ["영구빙", "서리꽃", "빙정 조각", "설원 모피", "얼음 송곳니", "극광 가루"],
        "demon": ["마력 응혈", "악마의 뿔", "저주받은 뼈", "핏빛 결정", "검은 불씨", "심연 가죽"],
        "heaven": ["천사의 깃", "성광 결정", "구름 비단", "별의 가루", "신성한 이슬", "찬란한 파편"],
    }

    for terrain_index, (terrain_key, names) in enumerate(terrain_materials.items()):
        for material_index, name in enumerate(names):
            rarity = "uncommon" if material_index < 3 else "rare"
            if terrain_key in {"demon", "heaven"}:
                rarity = "epic" if material_index < 4 else "legendary"
            elif terrain_key in {"mountain", "ice"} and material_index >= 4:
                rarity = "epic"

            item_id = f"terrain_{terrain_index:02d}_{material_index:02d}"
            catalog[item_id] = {
                "name": name,
                "kind": "material",
                "rarity": rarity,
                "value": int((35 + terrain_index * 25 + material_index * 12) * ADVENTURE_RARITIES[rarity]["value_mul"]),
                "source_monster": None,
                "custom_name": False,
                "terrain": terrain_key,
            }

    # 이름을 최초 발견자가 붙이는 유물 120종
    for relic_number in range(1, 121):
        if relic_number % 97 == 0:
            rarity = "mythic"
        elif relic_number % 29 == 0:
            rarity = "legendary"
        elif relic_number % 11 == 0:
            rarity = "epic"
        elif relic_number % 4 == 0:
            rarity = "rare"
        else:
            rarity = "uncommon"

        item_id = f"relic_{relic_number:03d}"
        relic_terrain = terrain_keys[(relic_number - 1) % len(terrain_keys)]
        if item_id in ADVENTURE_ROUTE_RELICS:
            relic_terrain = ADVENTURE_ROUTE_RELICS[item_id]["source"]

        catalog[item_id] = {
            "name": None,
            "kind": "relic",
            "rarity": rarity,
            "value": int(250 * ADVENTURE_RARITIES[rarity]["value_mul"]),
            "source_monster": None,
            "custom_name": True,
            "terrain": relic_terrain,
            "route_relic": item_id in ADVENTURE_ROUTE_RELICS,
        }

    return catalog


ADVENTURE_ITEM_CATALOG = build_adventure_item_catalog()


def get_adventure_item_name(item_id):
    item = ADVENTURE_ITEM_CATALOG.get(item_id)
    if not item:
        return "알 수 없는 물건"

    if item.get("custom_name"):
        discovered = discovered_items.get(item_id, {})
        return discovered.get("name") or "이름 없는 유물"

    return item["name"]


def get_adventure_item_line(item_id, count=1):
    item = ADVENTURE_ITEM_CATALOG.get(item_id)
    if not item:
        return f"❔ 알 수 없는 물건 ×{count}"

    rarity = ADVENTURE_RARITIES[item["rarity"]]
    return f"{rarity['emoji']} **{get_adventure_item_name(item_id)}** ×{count}"


def add_adventure_item(uid, item_id, amount=1):
    if item_id not in ADVENTURE_ITEM_CATALOG:
        return

    inventory = get_adventure_inventory(uid)
    inventory[item_id] = max(0, int(inventory.get(item_id, 0)) + int(amount))

    if inventory[item_id] <= 0:
        inventory.pop(item_id, None)


def adventure_elapsed_minutes(adventure):
    started_at = adventure.get("started_at")
    if not started_at:
        return 0.0

    try:
        started = datetime.fromisoformat(started_at)
        if started.tzinfo is None:
            started = started.replace(tzinfo=KST)
        return max(0.0, (datetime.now(KST) - started).total_seconds() / 60)
    except (TypeError, ValueError):
        return 0.0


def adventure_danger(adventure):
    # 실제 시간은 무시하고 완료한 턴 수만 위험도에 반영한다.
    steps = max(0, int(adventure.get("steps", 0)))
    return steps * ADVENTURE_DANGER_PER_TURN


def start_new_adventure(uid, terrain_key):
    if terrain_key not in ADVENTURE_START_TERRAINS:
        terrain_key = "grassland"

    adventure = get_adventure(uid)
    boosts = get_equipped_adventure_boosts(uid)
    max_lives = 3 + max(0, int(boosts.get("max_lives", 0)))

    adventure.update({
        "active": True,
        "started_at": datetime.now(KST).isoformat(),
        "steps": 0,
        "kills": 0,
        "earned_mora": 0,
        "lives": max_lives,
        "max_lives": max_lives,
        "turn_started_at": None,
        "turn_ready_at": None,
        "turn_duration_seconds": 0,
        "pending_event": None,
        "pending_name_item_id": None,
        "terrain": terrain_key,
        "terrain_steps": 0,
        "quiet_turns": 0,
        "visited_terrains": [terrain_key],
        "defeated_bosses": [],
        "boosts": boosts,
    })
    save_data()
    return adventure


def finish_adventure(uid):
    adventure = get_adventure(uid)

    summary = {
        "steps": adventure.get("steps", 0),
        "kills": adventure.get("kills", 0),
        "earned_mora": adventure.get("earned_mora", 0),
        "minutes": adventure_elapsed_minutes(adventure),
        "terrain": adventure.get("terrain"),
        "visited_terrains": list(adventure.get("visited_terrains", [])),
    }

    terrain_rank = max(
        [ADVENTURE_TERRAIN_DEPTH.get(key, 0) for key in summary["visited_terrains"]]
        or [0]
    )

    adventure["best_steps"] = max(adventure.get("best_steps", 0), summary["steps"])
    adventure["best_kills"] = max(adventure.get("best_kills", 0), summary["kills"])
    adventure["best_terrain_rank"] = max(adventure.get("best_terrain_rank", 0), terrain_rank)
    adventure["total_runs"] = adventure.get("total_runs", 0) + 1
    adventure["active"] = False
    adventure["started_at"] = None
    # 모험이 끝나면 다음 /모험에서 새 전용 스레드를 만들도록 연결을 끊는다.
    adventure["thread_id"] = None
    adventure["turn_started_at"] = None
    adventure["turn_ready_at"] = None
    adventure["turn_duration_seconds"] = 0
    adventure["pending_event"] = None
    adventure["pending_name_item_id"] = None
    adventure["lives"] = 3
    adventure["max_lives"] = 3
    adventure["terrain"] = None
    adventure["quiet_turns"] = 0
    adventure["terrain_steps"] = 0
    adventure["visited_terrains"] = []
    adventure["defeated_bosses"] = []

    save_data()
    return summary


def get_trait_by_name(name):
    if not name:
        return None

    for trait in MONSTER_TRAITS:
        if trait["name"] == name:
            return trait

    return None


def roll_adventure_monster_tier():
    roll = random.random() * 100

    if roll < 1.0:
        return "calamity"
    if roll < 11.0:
        return "elite"
    return "normal"


def get_adventure_monster_tier(tier_name):
    return ADVENTURE_MONSTER_TIERS.get(
        tier_name,
        ADVENTURE_MONSTER_TIERS["normal"],
    )


def format_adventure_monster_name(monster_name, trait=None, tier_name="normal"):
    parts = []
    tier = get_adventure_monster_tier(tier_name)

    if tier["prefix"]:
        parts.append(tier["prefix"])
    if trait:
        parts.append(trait["name"])
    parts.append(monster_name)

    return " ".join(parts)


def find_adventure_monster_by_name(name):
    return find_monster_by_name(name)


def pick_adventure_monster(adventure, tier_name="normal", force_boss=False):
    danger = adventure_danger(adventure)
    terrain_key = adventure.get("terrain") or "grassland"
    terrain = get_terrain_info(terrain_key)

    normal_target = max(
        1,
        int(
            (
                adventure["level"]
                + danger * ADVENTURE_MONSTER_DANGER_LEVEL_MUL
                + terrain["danger_flat"]
            )
            * terrain["danger_mul"]
        ),
    )
    tier = get_adventure_monster_tier(tier_name)

    target_level = max(
        1,
        int(normal_target * tier["level_mul"]) + tier["level_flat"],
    )

    terrain_monsters = [
        monster
        for name in terrain["monsters"]
        for monster in [find_adventure_monster_by_name(name)]
        if monster is not None
    ]

    boss_name = terrain.get("boss")
    defeated = set(adventure.get("defeated_bosses", []))
    is_boss = bool(force_boss and terrain_key not in defeated and boss_name)

    monster = find_adventure_monster_by_name(boss_name) if is_boss else None

    if monster is None:
        normal_pool = [monster for monster in terrain_monsters if monster["name"] != boss_name]
        if not normal_pool:
            normal_pool = terrain_monsters or MONSTERS

        possible = [
            monster
            for monster in normal_pool
            if monster["min"] <= target_level <= monster["max"]
        ]

        if not possible:
            possible = sorted(
                normal_pool,
                key=lambda monster: abs(((monster["min"] + monster["max"]) / 2) - target_level),
            )[:3]

        monster = random.choice(possible)
        is_boss = False

    if is_boss:
        # 전역 몬스터의 최소 레벨을 강제하지 않고 현재 턴 진행도에 맞춘다.
        target_level += ADVENTURE_BOSS_LEVEL_BONUS
        low = max(1, target_level - 3)
        high = target_level + 2
    elif tier_name == "normal":
        low = max(monster["min"], target_level - 3)
        high = min(monster["max"], target_level + 3)
        if low > high:
            low = max(1, target_level - 3)
            high = target_level + 3
    else:
        low = max(1, target_level - 3)
        high = target_level + 3

    monster_level = random.randint(low, high)
    trait = pick_monster_trait()
    return monster, monster_level, trait, is_boss


def weighted_adventure_item(items, danger=0.0, loot_bonus=0.0):
    if not items:
        return None

    weights = []

    for item_id in items:
        item = ADVENTURE_ITEM_CATALOG[item_id]
        rarity = item["rarity"]
        rarity_rank = ADVENTURE_RARITY_ORDER[rarity]
        weight = ADVENTURE_DROP_WEIGHTS[rarity]

        # 깊이와 장비 효과가 높은 등급에 조금 더 유리하게 작용
        weight *= 1 + min(2.5, danger / 80) * (rarity_rank * 0.18)
        weight *= 1 + (loot_bonus / 100) * rarity_rank
        weights.append(max(0.001, weight))

    return random.choices(items, weights=weights, k=1)[0]


def pick_monster_loot(monster_name, adventure):
    candidates = [
        item_id
        for item_id, item in ADVENTURE_ITEM_CATALOG.items()
        if item.get("source_monster") == monster_name
    ]

    return weighted_adventure_item(
        candidates,
        danger=adventure_danger(adventure),
        loot_bonus=adventure.get("boosts", {}).get("loot", 0),
    )


def pick_world_loot(adventure):
    terrain_key = adventure.get("terrain") or "grassland"
    candidates = [
        item_id
        for item_id, item in ADVENTURE_ITEM_CATALOG.items()
        if item["kind"] in {"herb", "ore", "material"}
        and item.get("terrain") == terrain_key
    ]

    if not candidates:
        candidates = [
            item_id
            for item_id, item in ADVENTURE_ITEM_CATALOG.items()
            if item["kind"] in {"herb", "ore", "material"}
        ]

    return weighted_adventure_item(
        candidates,
        danger=adventure_danger(adventure),
        loot_bonus=adventure.get("boosts", {}).get("loot", 0),
    )


def pick_mystery_relic(adventure=None):
    terrain_key = (adventure or {}).get("terrain") or "grassland"
    all_relics = [
        item_id
        for item_id, item in ADVENTURE_ITEM_CATALOG.items()
        if item["kind"] == "relic" and item.get("terrain") == terrain_key
    ]

    if not all_relics:
        all_relics = [
            item_id
            for item_id, item in ADVENTURE_ITEM_CATALOG.items()
            if item["kind"] == "relic"
        ]

    undiscovered = [item_id for item_id in all_relics if item_id not in discovered_items]

    # 아직 이름 없는 유물이 있으면 새 발견이 더 잘 나온다.
    if undiscovered and random.random() < 0.78:
        return random.choice(undiscovered)

    return random.choice(all_relics)


def format_adventure_boosts(boosts):
    labels = {
        "battle": "전투",
        "luck": "행운",
        "loot": "전리품",
        "escape": "도주",
        "life_save": "생존",
        "relic": "유물",
    }

    parts = []
    for key, label in labels.items():
        value = boosts.get(key, 0)
        if value:
            suffix = "%" if key != "relic" else "%p"
            parts.append(f"{label} +{value:g}{suffix}")

    return ", ".join(parts) if parts else "없음"


def parse_adventure_time(value):
    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=KST)
        return parsed
    except (TypeError, ValueError):
        return None


def get_adventure_turn_remaining(adventure):
    ready_at = parse_adventure_time(adventure.get("turn_ready_at"))
    if ready_at is None:
        return 0

    return max(0, int((ready_at - datetime.now(KST)).total_seconds()))


def format_adventure_wait_time(seconds):
    seconds = max(0, int(seconds))
    minutes, seconds = divmod(seconds, 60)

    if minutes and seconds:
        return f"{minutes}분 {seconds}초"
    if minutes:
        return f"{minutes}분"
    return f"{seconds}초"


def clear_adventure_turn_timer(adventure):
    adventure["turn_started_at"] = None
    adventure["turn_ready_at"] = None
    adventure["turn_duration_seconds"] = 0


def schedule_adventure_turn(adventure):
    duration = random.randint(ADVENTURE_TURN_MIN_SECONDS, ADVENTURE_TURN_MAX_SECONDS)
    now = datetime.now(KST)

    adventure["turn_started_at"] = now.isoformat()
    adventure["turn_ready_at"] = (now + timedelta(seconds=duration)).isoformat()
    adventure["turn_duration_seconds"] = duration
    return duration


def build_adventure_status_embed(member, adventure, title="🧭 모험 중"):
    elapsed = adventure_elapsed_minutes(adventure)
    danger = adventure_danger(adventure)
    terrain_key = adventure.get("terrain") or "grassland"
    terrain = get_terrain_info(terrain_key)

    visited = adventure.get("visited_terrains", [])
    visited_text = " → ".join(get_terrain_info(key)["name"] for key in visited if key in ADVENTURE_TERRAINS)
    if not visited_text:
        visited_text = terrain["name"]

    if adventure.get("turn_ready_at"):
        remaining = get_adventure_turn_remaining(adventure)
        if remaining > 0:
            turn_status = f"⏳ 다음 사건까지: **{format_adventure_wait_time(remaining)}**"
        else:
            turn_status = "🎲 다음 사건: **확인 가능!**"
    else:
        turn_status = "🛤️ 다음 이동: **대기 중**"

    embed = discord.Embed(
        title=title,
        description=(
            f"{member.mention}은(는) 현재 모험 중이야.\n\n"
            f"🗺️ 현재 지형: **{terrain['emoji']} {terrain['name']}**\n"
            f"📍 이동 경로: **{visited_text}**\n"
            f"🎖️ 모험 레벨: **Lv.{adventure['level']}** "
            f"({adventure['exp']}/{get_adventure_required_exp(adventure['level'])} EXP)\n"
            f"{get_adventure_equipment_text(adventure)}\n"
            f"⏱️ 경과 시간: **{elapsed:.1f}분** *(난이도 영향 없음)*\n"
            f"👣 전체 진행: **{adventure['steps']}회**\n"
            f"🥾 현재 지형 진행: **{adventure.get('terrain_steps', 0)}회**\n"
            f"{turn_status}\n"
            f"👹 다음 턴 일반 몬스터 확률: **{get_adventure_monster_spawn_rate(adventure):.1f}%**\n"
            f"👑 다음 턴 보스 확률: **{get_adventure_boss_spawn_rate(adventure, next_turn=True):.1f}%**\n"
            f"⚔️ 처치 수: **{adventure['kills']}마리**\n"
            f"❤️ 목숨: **{adventure['lives']}/{adventure.get('max_lives', 3)}**\n"
            f"💰 이번 모험 수익: **{adventure['earned_mora']:,}모라**\n"
            f"☠️ 위험도: **{danger:.1f}**\n\n"
            f"🎒 적용 효과: {format_adventure_boosts(adventure.get('boosts', {}))}"
        ),
        color=discord.Color(terrain["color"]),
    )

    embed.set_footer(text=f"{terrain['description']} 실제 시간은 무관하며, 완료한 턴 수에 따라 적이 강해진다.")
    return embed


def build_adventure_waiting_embed(member, adventure, title="🌲 모험을 떠나는 중..."):
    terrain = get_terrain_info(adventure.get("terrain"))
    remaining = get_adventure_turn_remaining(adventure)
    embed = build_adventure_status_embed(member, adventure, title=title)

    if remaining > 0:
        wait_text = (
            f"{terrain['emoji']} {terrain['name']}의 안쪽으로 천천히 이동하고 있어.\n"
            f"이번 턴은 약 **{format_adventure_wait_time(adventure.get('turn_duration_seconds', remaining))}** 동안 진행돼.\n\n"
            f"⏳ 현재 남은 시간: **{format_adventure_wait_time(remaining)}**\n"
            "시간이 지난 뒤 **상황 확인**을 누르면 다음 사건이 발생해."
        )
    else:
        wait_text = (
            f"{terrain['emoji']} 이동이 끝났어. 주변에서 무언가 일어난 것 같아.\n\n"
            "🎲 **상황 확인**을 눌러 이번 턴의 결과를 확인해!"
        )

    embed.description += f"\n\n{wait_text}"
    return embed


def normalize_item_name_for_filter(name):
    import re
    return re.sub(r"[^가-힣a-zA-Z0-9]", "", name).lower()


def validate_relic_name(name):
    import re

    clean_name = name.strip()

    if not 1 <= len(clean_name) <= 6:
        return False, "이름은 1~6자로 지어야 해."

    if not re.fullmatch(r"[가-힣a-zA-Z0-9 ]+", clean_name):
        return False, "한글, 영어, 숫자, 공백만 사용할 수 있어."

    normalized = normalize_item_name_for_filter(clean_name)
    if not normalized:
        return False, "사용할 수 없는 이름이야."

    banned_words = set(ANGRY_WORDS + DIRTY_WORDS)
    for banned in banned_words:
        banned_normalized = normalize_item_name_for_filter(banned)
        if banned_normalized and banned_normalized in normalized:
            return False, "금지어가 들어간 이름은 사용할 수 없어."

    meaningless = {
        "ㅋㅋ", "ㅋㅋㅋ", "ㅎㅎ", "ㅎㅎㅎ", "ㄹㅇ", "ㅁㄴㅇㄹ",
        "123", "1234", "aaaa", "asdf", "test", "테스트",
    }
    if normalized in {normalize_item_name_for_filter(v) for v in meaningless}:
        return False, "조금 더 제대로 된 이름을 지어줘."

    for info in discovered_items.values():
        old_name = str(info.get("name", ""))
        if normalize_item_name_for_filter(old_name) == normalized:
            return False, "이미 다른 유물이 쓰고 있는 이름이야."

    return True, clean_name


async def check_adventure_owner(interaction, owner_id):
    if str(interaction.user.id) == str(owner_id):
        return True

    await interaction.response.send_message("❌ 네 모험이 아니야.", ephemeral=True)
    return False


async def send_adventure_travel_animation(interaction, uid):
    adventure = get_adventure(uid)
    schedule_adventure_turn(adventure)
    save_data()

    embed = build_adventure_waiting_embed(
        interaction.user,
        adventure,
        title="🌲 모험을 떠나는 중...",
    )
    await interaction.response.edit_message(
        embed=embed,
        view=AdventureTurnWaitingView(uid),
    )


async def apply_adventure_life_loss(message, member, adventure, reason_text):
    uid = str(member.id)

    shop_save_chance = adventure.get("boosts", {}).get("life_save", 0)
    life_saved = random.random() * 100 < shop_save_chance

    if life_saved:
        save_data()
        embed = discord.Embed(
            title="💥 간신히 살아남았다!",
            description=(
                f"{reason_text}\n\n"
                "모험 전용 생존 효과가 발동해서 목숨은 줄지 않았어!\n"
                f"❤️ 남은 목숨: **{adventure['lives']}/{adventure.get('max_lives', 3)}**"
            ),
            color=discord.Color.orange(),
        )
        await message.edit(embed=embed, view=AdventureTravelView(uid))
        return

    adventure["lives"] -= 1

    if adventure["lives"] > 0:
        save_data()
        embed = discord.Embed(
            title="💀 패배...",
            description=(
                f"{reason_text}\n\n"
                "목숨을 하나 잃었어.\n"
                f"❤️ 남은 목숨: **{adventure['lives']}/{adventure.get('max_lives', 3)}**"
            ),
            color=discord.Color.red(),
        )
        await message.edit(embed=embed, view=AdventureTravelView(uid))
        return

    money = get_poker_money(uid)
    hospital_fee, final_rate = calc_adventure_hospital_fee(money)
    remove_poker_money(uid, hospital_fee)
    lost_weapons, lost_armors = reset_adventure_run_equipment(adventure)
    summary = finish_adventure(uid)
    lost_count = len(lost_weapons) + len(lost_armors)

    embed = discord.Embed(
        title="🏥 병원에서 눈을 떴다...",
        description=(
            f"{reason_text}\n\n"
            "목숨을 전부 잃어서 이번 모험은 처음부터 다시 해야 해.\n"
            f"치료비: **{hospital_fee:,}모라** ({final_rate * 100:.1f}%)\n"
            f"🧰 잃어버린 모험 장비: **{lost_count}개**\n"
            f"🎖️ 모험 레벨은 **Lv.{adventure['level']}**로 보존됐어.\n\n"
            f"👣 진행: **{summary['steps']}회**\n"
            f"⚔️ 처치: **{summary['kills']}마리**\n"
            f"💰 획득: **{summary['earned_mora']:,}모라**\n"
            f"⏱️ 생존 시간: **{summary['minutes']:.1f}분**\n"
            f"🗺️ 마지막 지형: **{get_terrain_name(summary.get('terrain'))}**"
        ),
        color=discord.Color.dark_red(),
    )
    await message.edit(embed=embed, view=None)


def get_route_relic_destinations(item_id, adventure):
    route = ADVENTURE_ROUTE_RELICS.get(item_id)
    current = adventure.get("terrain")
    if not route or route.get("source") != current:
        return []
    return valid_terrain_destinations(current, route.get("destinations", []))


def queue_terrain_choice(adventure, destinations, reason, detail=None):
    current = adventure.get("terrain") or "grassland"
    destinations = valid_terrain_destinations(current, destinations)
    if not destinations:
        return False

    adventure["pending_event"] = {
        "type": "terrain_choice",
        "source": current,
        "destinations": destinations,
        "reason": reason,
        "detail": detail,
    }
    return True


def build_terrain_choice_embed(adventure):
    pending = adventure.get("pending_event") or {}
    source = pending.get("source") or adventure.get("terrain") or "grassland"
    destinations = valid_terrain_destinations(source, pending.get("destinations", []))
    reason = pending.get("reason")

    if reason == "boss":
        title = "👑 지역의 지배자를 쓰러뜨렸다!"
        reason_text = "보스가 지키고 있던 길이 열리며 여러 지형으로 이어지는 통로가 드러났어."
    elif reason == "relic":
        title = "🔮 유물이 새로운 길에 반응한다!"
        relic_name = pending.get("detail") or "수수께끼의 유물"
        reason_text = f"**{relic_name}**에서 빛이 흘러나오며 숨겨진 갈림길이 열렸어."
    else:
        title = "🧭 낯선 갈림길을 발견했다!"
        reason_text = "공간이 뒤틀리며 평소에는 보이지 않던 길들이 나타났어."

    route_lines = [f"• {get_terrain_name(key)}" for key in destinations]
    terrain = get_terrain_info(source)
    return discord.Embed(
        title=title,
        description=(
            f"현재 위치: **{get_terrain_name(source)}**\n\n"
            f"{reason_text}\n\n"
            "이동할 지형을 선택해. 현재 지형에 남을 수도 있어.\n\n"
            + "\n".join(route_lines)
        ),
        color=discord.Color(terrain["color"]),
    )


async def show_terrain_choice(message, member):
    adventure = get_adventure(member.id)
    pending = adventure.get("pending_event") or {}
    destinations = valid_terrain_destinations(
        pending.get("source") or adventure.get("terrain"),
        pending.get("destinations", []),
    )

    if not destinations:
        adventure["pending_event"] = None
        save_data()
        await message.edit(embed=build_adventure_status_embed(member, adventure), view=AdventureTravelView(member.id))
        return

    await message.edit(
        embed=build_terrain_choice_embed(adventure),
        view=AdventureTerrainChoiceView(member.id, destinations),
    )


async def show_adventure_monster_encounter(message, member, adventure, monster_tier="normal", force_boss=False):
    uid = str(member.id)
    terrain_key = adventure.get("terrain") or "grassland"
    terrain = get_terrain_info(terrain_key)
    tier_info = get_adventure_monster_tier(monster_tier)

    monster, monster_level, trait, is_boss = pick_adventure_monster(
        adventure,
        monster_tier,
        force_boss=force_boss,
    )
    battle_level = apply_trait_to_monster_level(monster_level, trait)
    monster_name = monster["name"]
    display_name = format_adventure_monster_name(monster_name, trait, monster_tier)

    adventure["pending_event"] = {
        "type": "monster",
        "monster_name": monster_name,
        "monster_level": monster_level,
        "trait_name": trait["name"] if trait else None,
        "monster_tier": monster_tier,
        "terrain": terrain_key,
        "is_boss": is_boss,
    }
    save_data()

    preview_chance = calc_adventure_win_chance(adventure, monster, monster_level, trait)

    if is_boss:
        encounter_title = f"👑 {terrain['name']}의 보스가 나타났다!"
        encounter_notice = "**이 지역의 길을 지키는 보스야!**\n쓰러뜨리면 새로운 지형으로 이어지는 길이 확정적으로 열려.\n\n"
        encounter_color = discord.Color.dark_gold()
    elif monster_tier == "calamity":
        encounter_title = "☠️ 도저히 상대하기 힘든 존재가 나타났다!"
        encounter_notice = "**재앙급 개체야. 정면 승부는 정말 위험해!**\n승리하면 보상이 크게 증가해.\n\n"
        encounter_color = discord.Color.dark_red()
    elif monster_tier == "elite":
        encounter_title = "🔥 평소보다 강한 몬스터가 나타났다!"
        encounter_notice = "**강적 개체야. 일반 몬스터보다 훨씬 강해!**\n대신 보상도 더 많아.\n\n"
        encounter_color = discord.Color.red()
    else:
        encounter_title = "⚔️ 몬스터가 나타났다!"
        encounter_notice = ""
        encounter_color = discord.Color.orange()

    embed = discord.Embed(
        title=encounter_title,
        description=(
            encounter_notice
            + f"지형: **{terrain['emoji']} {terrain['name']}**\n"
            + f"**Lv.{battle_level} {display_name}** 등장!\n\n"
            f"내 모험 레벨: **Lv.{adventure['level']}**\n"
            f"{get_adventure_equipment_text(adventure)}\n"
            f"예상 승률: **{preview_chance}%**\n"
            f"❤️ 목숨: **{adventure['lives']}/{adventure.get('max_lives', 3)}**"
        ),
        color=encounter_color,
    )
    await message.edit(embed=embed, view=AdventureBattleView(uid))


async def roll_adventure_event(message, member):
    uid = str(member.id)
    adventure = get_adventure(uid)

    if not adventure["active"]:
        await message.edit(content="이 모험은 이미 끝났어.", embed=None, view=None)
        return

    if adventure.get("pending_name_item_id"):
        item_id = adventure["pending_name_item_id"]
        embed = discord.Embed(
            title="✨ 이름을 기다리는 유물",
            description=(
                f"{get_adventure_item_line(item_id)}\n\n"
                "이 유물은 네가 최초로 발견했어. 계속 가기 전에 이름을 지어줘!"
            ),
            color=discord.Color.gold(),
        )
        await message.edit(embed=embed, view=RelicNamingView(uid))
        return

    pending = adventure.get("pending_event")
    if pending and pending.get("type") == "terrain_choice":
        await show_terrain_choice(message, member)
        return

    adventure["steps"] += 1
    adventure["terrain_steps"] = adventure.get("terrain_steps", 0) + 1
    danger = adventure_danger(adventure)
    boosts = adventure.get("boosts", {})
    terrain_key = adventure.get("terrain") or "grassland"
    terrain = get_terrain_info(terrain_key)

    # 보스는 5턴을 넘긴 뒤부터 매 턴 독립적으로 판정된다.
    boss_rate = get_adventure_boss_spawn_rate(adventure)
    if boss_rate > 0 and random.random() * 100 < boss_rate:
        adventure["quiet_turns"] = 0
        save_data()
        await show_adventure_monster_encounter(
            message,
            member,
            adventure,
            monster_tier="normal",
            force_boss=True,
        )
        return

    # 아무 조건 없이 나타나는 희귀 갈림길. 특수 지형도 진입 방향 제한은 반드시 지킨다.
    route_rate = ADVENTURE_RANDOM_ROUTE_RATE + min(1.5, boosts.get("luck", 0) * 0.04)
    if adventure["terrain_steps"] >= 2 and random.random() * 100 < route_rate:
        destinations = valid_terrain_destinations(terrain_key)
        if len(destinations) > 2:
            destinations = random.sample(destinations, k=random.randint(2, min(3, len(destinations))))
        if queue_terrain_choice(adventure, destinations, "random"):
            adventure["quiet_turns"] = min(10, adventure.get("quiet_turns", 0) + 1)
            save_data()
            await show_terrain_choice(message, member)
            return

    relic_rate = min(12.0, 1.5 + boosts.get("relic", 0) + danger * 0.018)
    good_event_shift = min(12.0, boosts.get("luck", 0) * 0.6)
    roll = random.random() * 100

    if roll < relic_rate:
        item_id = pick_mystery_relic(adventure)
        add_adventure_item(uid, item_id, 1)

        item_name = get_adventure_item_name(item_id)
        is_new = item_id not in discovered_items
        route_destinations = get_route_relic_destinations(item_id, adventure)

        if route_destinations:
            queue_terrain_choice(adventure, route_destinations, "relic", item_name)
        if is_new:
            adventure["pending_name_item_id"] = item_id

        adventure["quiet_turns"] = min(10, adventure.get("quiet_turns", 0) + 1)
        save_data()

        rarity = ADVENTURE_RARITIES[ADVENTURE_ITEM_CATALOG[item_id]["rarity"]]
        route_notice = "\n\n🔮 이 유물에서 이상한 힘이 느껴져. 이름을 정하면 숨겨진 길이 열릴 것 같아!" if route_destinations else ""
        embed = discord.Embed(
            title="✨ 처음 보는 물건을 발견했다!" if is_new else "✨ 유물을 발견했다!",
            description=(
                f"{rarity['emoji']} **{item_name}**\n"
                f"등급: **{rarity['name']}**\n"
                f"발견 지형: **{terrain['emoji']} {terrain['name']}**\n\n"
                + (
                    "이 유물은 아직 이름이 없어. 최초 발견자인 네가 이름을 지을 수 있어!"
                    if is_new
                    else "이미 누군가 이름 붙인 유물이야."
                )
                + route_notice
            ),
            color=discord.Color.gold(),
        )

        if is_new:
            view = RelicNamingView(uid)
        elif route_destinations:
            view = AdventureTerrainChoiceView(uid, route_destinations)
        else:
            view = AdventureTravelView(uid)
        await message.edit(embed=embed, view=view)
        return

    # 기본 35%. 몬스터가 안 나온 턴마다 15%p씩 증가하고, 조우하면 다시 초기화된다.
    monster_border = get_adventure_monster_spawn_rate(adventure)
    item_border = monster_border + 22 + good_event_shift * 0.55
    money_border = item_border + 13 + good_event_shift * 0.25
    heal_border = money_border + 7 + good_event_shift * 0.15

    if roll < relic_rate + monster_border:
        adventure["quiet_turns"] = 0
        save_data()
        await show_adventure_monster_encounter(
            message,
            member,
            adventure,
            monster_tier=roll_adventure_monster_tier(),
            force_boss=False,
        )
        return

    # 이번 턴에도 몬스터가 나오지 않았다면 다음 턴 조우 확률을 높인다.
    adventure["quiet_turns"] = min(10, adventure.get("quiet_turns", 0) + 1)

    adjusted_roll = roll - relic_rate

    if adjusted_roll < item_border:
        item_id = pick_world_loot(adventure)
        amount = 1
        if ADVENTURE_ITEM_CATALOG[item_id]["rarity"] in {"common", "uncommon"}:
            amount = random.randint(1, 3)

        add_adventure_item(uid, item_id, amount)
        save_data()

        embed = discord.Embed(
            title=f"🎒 {terrain['name']}에서 재료를 발견했다!",
            description=f"{get_adventure_item_line(item_id, amount)}\n\n가방에 넣었어.",
            color=discord.Color(terrain["color"]),
        )
        await message.edit(embed=embed, view=AdventureTravelView(uid))
        return

    if adjusted_roll < money_border:
        amount = random.randint(40, 100) + int(danger * random.randint(4, 8))
        amount = int(amount * terrain["reward_mul"])
        add_poker_money(uid, amount)
        adventure["earned_mora"] += amount
        save_data()

        embed = discord.Embed(
            title="💰 버려진 주머니를 발견했다!",
            description=(
                f"안에는 **{amount:,}모라**가 들어 있었어.\n\n"
                f"이번 모험 수익: **{adventure['earned_mora']:,}모라**"
            ),
            color=discord.Color.gold(),
        )
        await message.edit(embed=embed, view=AdventureTravelView(uid))
        return

    if adjusted_roll < heal_border:
        old_lives = adventure["lives"]
        adventure["lives"] = min(adventure.get("max_lives", 3), adventure["lives"] + 1)
        save_data()

        if adventure["lives"] > old_lives:
            text_value = "샘물을 마시자 상처가 회복됐어!\n❤️ 목숨 **+1**"
        else:
            text_value = "맑은 샘물을 발견했지만 이미 멀쩡해서 별 효과는 없었어."

        embed = discord.Embed(title="💧 회복의 샘", description=text_value, color=discord.Color.blue())
        await message.edit(embed=embed, view=AdventureTravelView(uid))
        return

    save_data()
    embed = discord.Embed(
        title=f"{terrain['emoji']} {terrain['name']}을 계속 걷고 있다...",
        description=(
            f"{terrain['description']}\n그래도 조금 더 깊은 곳까지 들어왔어.\n\n"
            f"다음 턴 일반 몬스터 확률: **{get_adventure_monster_spawn_rate(adventure):.1f}%**\n"
            f"다음 턴 보스 확률: **{get_adventure_boss_spawn_rate(adventure, next_turn=True):.1f}%**"
        ),
        color=discord.Color(terrain["color"]),
    )
    await message.edit(embed=embed, view=AdventureTravelView(uid))


async def resolve_adventure_battle(message, member):
    uid = str(member.id)
    adventure = get_adventure(uid)
    pending = adventure.get("pending_event")

    if not pending or pending.get("type") != "monster":
        await message.edit(content="전투할 몬스터가 사라졌어.", embed=None, view=AdventureTravelView(uid))
        return

    monster = find_adventure_monster_by_name(pending["monster_name"])
    trait = get_trait_by_name(pending.get("trait_name"))
    monster_level = int(pending["monster_level"])
    monster_tier = pending.get("monster_tier", "normal")
    tier_info = get_adventure_monster_tier(monster_tier)
    terrain_key = pending.get("terrain") or adventure.get("terrain") or "grassland"
    terrain = get_terrain_info(terrain_key)
    is_boss = bool(pending.get("is_boss"))

    if monster is None:
        adventure["pending_event"] = None
        save_data()
        await message.edit(content="몬스터 데이터를 찾지 못해서 전투가 취소됐어.", embed=None, view=AdventureTravelView(uid))
        return

    battle_level = apply_trait_to_monster_level(monster_level, trait)
    display_name = format_adventure_monster_name(
        monster["name"],
        trait,
        monster_tier,
    )

    # 전투 버튼을 누르는 순간의 모험 전용 장비를 실시간 반영한다.
    win_chance = calc_adventure_win_chance(adventure, monster, monster_level, trait)
    win = random.randint(1, 100) <= win_chance
    adventure["pending_event"] = None

    if not win:
        save_data()
        await apply_adventure_life_loss(
            message,
            member,
            adventure,
            f"**Lv.{battle_level} {display_name}**에게 패배했어.",
        )
        return

    reward = random.randint(70, 150) + monster_level * 18
    exp = random.randint(25, 55) + monster_level * 5
    reward, exp = apply_trait_reward(reward, exp, trait)

    reward = int(reward * tier_info["reward_mul"] * terrain["reward_mul"])
    exp = int(exp * tier_info["exp_mul"] * terrain["reward_mul"])

    add_poker_money(uid, reward)
    leveled = give_adventure_exp(adventure, exp)

    adventure["kills"] += 1
    adventure["total_kills"] += 1
    adventure["earned_mora"] += reward

    loot_id = pick_monster_loot(monster["name"], adventure)
    loot_amount = 1
    if ADVENTURE_ITEM_CATALOG[loot_id]["rarity"] in {"common", "uncommon"}:
        loot_amount = random.randint(1, 2)

    loot_amount += tier_info["loot_bonus"]
    add_adventure_item(uid, loot_id, loot_amount)

    equipment_drop = roll_adventure_equipment_drop(
        adventure, monster_tier=monster_tier, is_boss=is_boss
    )

    relic_chance = min(
        14.0,
        1.2
        + adventure.get("boosts", {}).get("relic", 0)
        + adventure_danger(adventure) * 0.012,
    )

    relic_id = None
    relic_is_new = False

    if random.random() * 100 < relic_chance:
        relic_id = pick_mystery_relic(adventure)
        relic_is_new = relic_id not in discovered_items
        add_adventure_item(uid, relic_id, 1)

        route_destinations = get_route_relic_destinations(relic_id, adventure)
        if route_destinations:
            queue_terrain_choice(adventure, route_destinations, "relic", get_adventure_item_name(relic_id))
        if relic_is_new:
            adventure["pending_name_item_id"] = relic_id

    boss_routes = []
    if is_boss:
        defeated = adventure.setdefault("defeated_bosses", [])
        if terrain_key not in defeated:
            defeated.append(terrain_key)
        boss_routes = valid_terrain_destinations(terrain_key)
        queue_terrain_choice(adventure, boss_routes, "boss", monster["name"])

    save_data()

    result_lines = [
        f"✅ **Lv.{battle_level} {display_name}** 처치!",
        f"등급: **{tier_info['name']}**",
        f"승률: **{win_chance}%**",
        f"{get_adventure_equipment_text(adventure)}",
        "",
        f"💰 **{reward:,}모라**",
        f"⭐ 모험 경험치 **{exp} EXP**",
        f"🎒 {get_adventure_item_line(loot_id, loot_amount)}",
    ]

    if equipment_drop:
        equipment_emoji = "🗡️" if equipment_drop["kind"] == "weapon" else "🛡️"
        result_lines.append(
            f"{equipment_emoji} 새 장비 발견: **{equipment_drop['name']}** "
            f"(승률 보너스 +{equipment_drop['bonus']})"
        )

    if leveled:
        result_lines.append(f"\n🎉 모험 레벨 업! 현재 **Lv.{adventure['level']}**")

    if relic_id:
        result_lines.append(f"\n✨ 추가 발견: {get_adventure_item_line(relic_id)}")
        if relic_is_new:
            result_lines.append("최초 발견 유물이야. 이름을 지어줘!")
        if get_route_relic_destinations(relic_id, adventure):
            result_lines.append("🔮 유물이 숨겨진 지형으로 이어지는 길을 열었어!")

    if is_boss:
        if boss_routes:
            result_lines.append("\n🗺️ 보스가 지키던 갈림길이 열렸어!")
        else:
            result_lines.append("\n🏆 이 지형의 최종 지배자를 쓰러뜨렸어!")
        victory_title = f"👑 {terrain['name']} 보스 격파!"
        victory_color = discord.Color.gold()
    elif monster_tier == "calamity":
        victory_title = "🏆 재앙급 몬스터 격파!"
        victory_color = discord.Color.gold()
    elif monster_tier == "elite":
        victory_title = "🔥 강적 격파!"
        victory_color = discord.Color.green()
    else:
        victory_title = "⚔️ 전투 승리!"
        victory_color = discord.Color.green()

    embed = discord.Embed(
        title=victory_title,
        description="\n".join(result_lines),
        color=victory_color,
    )

    pending_after_battle = adventure.get("pending_event") or {}

    if relic_is_new:
        view = RelicNamingView(uid)
    elif pending_after_battle.get("type") == "terrain_choice":
        view = AdventureTerrainChoiceView(
            uid,
            pending_after_battle.get("destinations", []),
        )
    else:
        view = AdventureTravelView(uid)
    await message.edit(embed=embed, view=view)


async def resolve_adventure_escape(message, member):
    uid = str(member.id)
    adventure = get_adventure(uid)
    pending = adventure.get("pending_event")

    if not pending or pending.get("type") != "monster":
        await message.edit(content="도망칠 상대가 없어.", embed=None, view=AdventureTravelView(uid))
        return

    escape_chance = calc_adventure_escape_chance(adventure)
    adventure["pending_event"] = None

    if random.randint(1, 100) <= escape_chance:
        save_data()
        embed = discord.Embed(
            title="💨 도주 성공!",
            description=(
                f"도주 확률 **{escape_chance}%**\n"
                f"{get_adventure_equipment_text(adventure)}\n\n"
                "몬스터가 쫓아오기 전에 무사히 빠져나왔어."
            ),
            color=discord.Color.blue(),
        )
        await message.edit(embed=embed, view=AdventureTravelView(uid))
        return

    save_data()
    await apply_adventure_life_loss(
        message,
        member,
        adventure,
        f"도주에 실패했어. 성공 확률은 **{escape_chance}%**였어.",
    )


class AdventureStartTerrainView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.user_id = str(user_id)

        for terrain_key in ADVENTURE_START_TERRAINS:
            terrain = get_terrain_info(terrain_key)
            button = discord.ui.Button(
                label=f"{terrain['emoji']} {terrain['name']}",
                style=discord.ButtonStyle.primary,
            )

            async def callback(interaction, selected=terrain_key):
                if not await check_adventure_owner(interaction, self.user_id):
                    return

                adventure = get_adventure(self.user_id)
                if adventure.get("active"):
                    await interaction.response.send_message("이미 모험 중이야.", ephemeral=True)
                    return

                adventure = start_new_adventure(self.user_id, selected)
                schedule_adventure_turn(adventure)
                save_data()

                terrain_info = get_terrain_info(selected)
                embed = build_adventure_waiting_embed(
                    interaction.user,
                    adventure,
                    title=f"{terrain_info['emoji']} {terrain_info['name']}으로 모험을 떠나는 중...",
                )
                await interaction.response.edit_message(
                    embed=embed,
                    view=AdventureTurnWaitingView(self.user_id),
                )

            button.callback = callback
            self.add_item(button)


class AdventureTerrainChoiceView(discord.ui.View):
    def __init__(self, user_id, destinations):
        super().__init__(timeout=300)
        self.user_id = str(user_id)
        adventure = get_adventure(self.user_id)
        source = adventure.get("terrain") or "grassland"
        self.destinations = valid_terrain_destinations(source, destinations)

        for destination in self.destinations:
            terrain = get_terrain_info(destination)
            style = discord.ButtonStyle.danger if destination == "demon" else discord.ButtonStyle.success
            if destination == "heaven":
                style = discord.ButtonStyle.primary

            button = discord.ui.Button(label=f"{terrain['emoji']} {terrain['name']}", style=style)

            async def callback(interaction, selected=destination):
                if not await check_adventure_owner(interaction, self.user_id):
                    return

                adventure = get_adventure(self.user_id)
                pending = adventure.get("pending_event") or {}
                source_key = adventure.get("terrain") or "grassland"
                allowed = valid_terrain_destinations(source_key, pending.get("destinations", self.destinations))
                if selected not in allowed:
                    await interaction.response.send_message("그 길은 이미 닫혔어.", ephemeral=True)
                    return

                adventure["terrain"] = selected
                adventure["terrain_steps"] = 0
                adventure["pending_event"] = None
                visited = adventure.setdefault("visited_terrains", [])
                if not visited or visited[-1] != selected:
                    visited.append(selected)
                save_data()

                terrain_info = get_terrain_info(selected)
                embed = build_adventure_status_embed(
                    interaction.user,
                    adventure,
                    title=f"{terrain_info['emoji']} {terrain_info['name']}에 도착했다!",
                )
                embed.description += f"\n\n{terrain_info['description']}"
                await interaction.response.edit_message(embed=embed, view=AdventureTravelView(self.user_id))

            button.callback = callback
            self.add_item(button)

        stay_button = discord.ui.Button(label="📍 현재 지형에 남기", style=discord.ButtonStyle.secondary)

        async def stay_callback(interaction):
            if not await check_adventure_owner(interaction, self.user_id):
                return
            adventure = get_adventure(self.user_id)
            adventure["pending_event"] = None
            save_data()
            embed = build_adventure_status_embed(interaction.user, adventure, title="📍 현재 길을 계속 탐험한다")
            await interaction.response.edit_message(embed=embed, view=AdventureTravelView(self.user_id))

        stay_button.callback = stay_callback
        self.add_item(stay_button)


def build_adventure_equipment_embed(member, uid):
    adventure = get_adventure(uid)
    weapon = adventure.get("weapon", "무인검")
    armor = adventure.get("armor", "모험가 세트")

    embed = discord.Embed(
        title=f"🧰 {member.display_name}의 모험 장비",
        description=(
            "아래 선택 메뉴에서 모험 중 발견한 장비를 즉시 교체할 수 있어.\n"
            "전투 직전에 바꿔도 실제 승률에 바로 반영돼.\n"
            "장비는 돈으로 살 수 없고, 병원행이면 기본 장비만 남아.\n\n"
            f"🎖️ 모험 레벨: **Lv.{adventure['level']}**\n"
            f"🗡️ 현재 무기: **{weapon}** (+{WEAPONS[weapon]['bonus']})\n"
            f"🛡️ 현재 갑옷: **{armor}** (+{ARMORS[armor]['bonus']})\n\n"
            f"보유 무기: **{len(adventure['owned_weapons'])}개**\n"
            f"보유 갑옷: **{len(adventure['owned_armors'])}개**"
        ),
        color=discord.Color.dark_teal(),
    )
    embed.set_footer(text="새 장비는 모험 전투 보상으로만 획득 가능")
    return embed


class AdventureWeaponSelect(discord.ui.Select):
    def __init__(self, user_id):
        self.user_id = str(user_id)
        adventure = get_adventure(self.user_id)
        current = adventure.get("weapon", "무인검")
        options = [
            discord.SelectOption(
                label=name,
                description=f"승률 보너스 +{WEAPONS[name]['bonus']}",
                default=(name == current),
            )
            for name in adventure.get("owned_weapons", ["무인검"])
            if name in WEAPONS
        ][:25]
        super().__init__(placeholder="🗡️ 장착할 무기 선택", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        adventure = get_adventure(self.user_id)
        selected = self.values[0]
        if selected not in adventure.get("owned_weapons", []):
            await interaction.response.send_message("보유하지 않은 모험 무기야.", ephemeral=True)
            return

        adventure["weapon"] = selected
        save_data()
        await interaction.response.edit_message(
            embed=build_adventure_equipment_embed(interaction.user, self.user_id),
            view=AdventureEquipmentView(self.user_id),
        )


class AdventureArmorSelect(discord.ui.Select):
    def __init__(self, user_id):
        self.user_id = str(user_id)
        adventure = get_adventure(self.user_id)
        current = adventure.get("armor", "모험가 세트")
        options = [
            discord.SelectOption(
                label=name,
                description=f"승률 보너스 +{ARMORS[name]['bonus']}",
                default=(name == current),
            )
            for name in adventure.get("owned_armors", ["모험가 세트"])
            if name in ARMORS
        ][:25]
        super().__init__(placeholder="🛡️ 장착할 갑옷 선택", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        adventure = get_adventure(self.user_id)
        selected = self.values[0]
        if selected not in adventure.get("owned_armors", []):
            await interaction.response.send_message("보유하지 않은 모험 갑옷이야.", ephemeral=True)
            return

        adventure["armor"] = selected
        save_data()
        await interaction.response.edit_message(
            embed=build_adventure_equipment_embed(interaction.user, self.user_id),
            view=AdventureEquipmentView(self.user_id),
        )


class AdventureEquipmentView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = str(user_id)
        self.add_item(AdventureWeaponSelect(self.user_id))
        self.add_item(AdventureArmorSelect(self.user_id))


class AdventureTurnWaitingView(discord.ui.View):
    def __init__(self, user_id):
        # 최대 대기 시간이 5분이라 여유 있게 15분 동안 버튼을 유지한다.
        super().__init__(timeout=900)
        self.user_id = str(user_id)

    @discord.ui.button(label="🔎 상황 확인", style=discord.ButtonStyle.primary)
    async def check_turn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        uid = self.user_id
        adventure = get_adventure(uid)

        if not adventure.get("active"):
            await interaction.response.send_message("이미 끝난 모험이야.", ephemeral=True)
            return

        if adventure.get("pending_name_item_id"):
            await interaction.response.send_message("먼저 발견한 유물의 이름을 지어줘.", ephemeral=True)
            return

        if adventure.get("pending_event"):
            await interaction.response.send_message("먼저 현재 발생한 사건을 해결해야 해.", ephemeral=True)
            return

        if not adventure.get("turn_ready_at"):
            await interaction.response.send_message(
                "아직 이동을 시작하지 않았어. **계속 모험**을 눌러 다음 턴을 시작해.",
                ephemeral=True,
            )
            return

        remaining = get_adventure_turn_remaining(adventure)
        if remaining > 0:
            await interaction.response.send_message(
                f"⏳ 아직 이동 중이야. **{format_adventure_wait_time(remaining)}** 뒤에 다시 확인해줘!",
                ephemeral=True,
            )
            return

        lock = get_adventure_lock(uid)
        if lock.locked():
            await interaction.response.send_message("이미 이번 턴을 확인 중이야.", ephemeral=True)
            return

        async with lock:
            adventure = get_adventure(uid)
            remaining = get_adventure_turn_remaining(adventure)
            if remaining > 0:
                await interaction.response.send_message(
                    f"⏳ 아직 **{format_adventure_wait_time(remaining)}** 남았어.",
                    ephemeral=True,
                )
                return

            clear_adventure_turn_timer(adventure)
            save_data()
            await interaction.response.defer()
            await roll_adventure_event(interaction.message, interaction.user)

    @discord.ui.button(label="🧰 장비 변경", style=discord.ButtonStyle.success)
    async def change_equipment(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        await interaction.response.send_message(
            embed=build_adventure_equipment_embed(interaction.user, self.user_id),
            view=AdventureEquipmentView(self.user_id),
            ephemeral=True,
        )

    @discord.ui.button(label="🏠 귀환", style=discord.ButtonStyle.secondary)
    async def return_home(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        uid = self.user_id
        adventure = get_adventure(uid)

        if not adventure.get("active"):
            await interaction.response.send_message("이미 끝난 모험이야.", ephemeral=True)
            return

        summary = finish_adventure(uid)
        embed = discord.Embed(
            title="🏠 무사히 귀환했다!",
            description=(
                f"👣 진행: **{summary['steps']}회**\n"
                f"⚔️ 처치: **{summary['kills']}마리**\n"
                f"💰 획득: **{summary['earned_mora']:,}모라**\n"
                f"⏱️ 모험 시간: **{summary['minutes']:.1f}분**\n"
                f"🗺️ 마지막 지형: **{get_terrain_name(summary.get('terrain'))}**\n\n"
                "모험 중 얻은 장비와 영구 모험 레벨은 그대로 유지돼."
            ),
            color=discord.Color.green(),
        )
        await interaction.response.edit_message(embed=embed, view=None)


class AdventureTravelView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.user_id = str(user_id)

    @discord.ui.button(label="👣 계속 모험", style=discord.ButtonStyle.primary)
    async def continue_adventure(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        uid = self.user_id
        adventure = get_adventure(uid)

        if not adventure["active"]:
            await interaction.response.send_message("이미 끝난 모험이야.", ephemeral=True)
            return

        if adventure.get("pending_name_item_id"):
            await interaction.response.send_message("먼저 발견한 유물의 이름을 지어줘.", ephemeral=True)
            return

        lock = get_adventure_lock(uid)
        if lock.locked():
            await interaction.response.send_message("이미 이동 중이야.", ephemeral=True)
            return

        async with lock:
            await send_adventure_travel_animation(interaction, uid)

    @discord.ui.button(label="🧰 장비 변경", style=discord.ButtonStyle.success)
    async def change_equipment(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        await interaction.response.send_message(
            embed=build_adventure_equipment_embed(interaction.user, self.user_id),
            view=AdventureEquipmentView(self.user_id),
            ephemeral=True,
        )

    @discord.ui.button(label="🏠 귀환", style=discord.ButtonStyle.secondary)
    async def return_home(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        uid = self.user_id
        adventure = get_adventure(uid)

        if not adventure["active"]:
            await interaction.response.send_message("이미 끝난 모험이야.", ephemeral=True)
            return

        summary = finish_adventure(uid)

        embed = discord.Embed(
            title="🏠 무사히 귀환했다!",
            description=(
                f"👣 진행: **{summary['steps']}회**\n"
                f"⚔️ 처치: **{summary['kills']}마리**\n"
                f"💰 획득: **{summary['earned_mora']:,}모라**\n"
                f"⏱️ 모험 시간: **{summary['minutes']:.1f}분**\n"
                f"🗺️ 마지막 지형: **{get_terrain_name(summary.get('terrain'))}**\n\n"
                "가방의 전리품은 그대로 보관돼."
            ),
            color=discord.Color.green(),
        )
        await interaction.response.edit_message(embed=embed, view=None)


class AdventureBattleView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.user_id = str(user_id)

    @discord.ui.button(label="⚔️ 전투 시작", style=discord.ButtonStyle.danger)
    async def battle(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        uid = self.user_id
        lock = get_adventure_lock(uid)

        if lock.locked():
            await interaction.response.send_message("이미 전투 처리 중이야.", ephemeral=True)
            return

        async with lock:
            adventure = get_adventure(uid)
            if not adventure["active"]:
                await interaction.response.send_message("이미 끝난 모험이야.", ephemeral=True)
                return

            embed = discord.Embed(
                title="⚔️ 전투 중...",
                description="무기를 들고 몬스터에게 달려들었다!",
                color=discord.Color.orange(),
            )
            await interaction.response.edit_message(embed=embed, view=None)
            message = interaction.message

            await asyncio.sleep(1.4)
            await resolve_adventure_battle(message, interaction.user)

    @discord.ui.button(label="🧰 장비 변경", style=discord.ButtonStyle.success)
    async def change_equipment(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        await interaction.response.send_message(
            embed=build_adventure_equipment_embed(interaction.user, self.user_id),
            view=AdventureEquipmentView(self.user_id),
            ephemeral=True,
        )

    @discord.ui.button(label="💨 도망가기", style=discord.ButtonStyle.secondary)
    async def escape(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        uid = self.user_id
        lock = get_adventure_lock(uid)

        if lock.locked():
            await interaction.response.send_message("이미 행동 처리 중이야.", ephemeral=True)
            return

        async with lock:
            embed = discord.Embed(
                title="💨 도주 시도 중...",
                description="몬스터의 시야에서 벗어나려고 달리고 있어!",
                color=discord.Color.blue(),
            )
            await interaction.response.edit_message(embed=embed, view=None)
            message = interaction.message

            await asyncio.sleep(1.0)
            await resolve_adventure_escape(message, interaction.user)


class RelicNameModal(discord.ui.Modal, title="새 유물 이름 짓기"):
    relic_name = discord.ui.TextInput(
        label="유물 이름",
        placeholder="6자 이하",
        min_length=1,
        max_length=6,
        required=True,
    )

    def __init__(self, user_id):
        super().__init__()
        self.user_id = str(user_id)

    async def on_submit(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ 네가 발견한 유물이 아니야.", ephemeral=True)
            return

        uid = self.user_id
        adventure = get_adventure(uid)
        item_id = adventure.get("pending_name_item_id")

        if not item_id:
            await interaction.response.send_message("이름을 기다리는 유물이 없어.", ephemeral=True)
            return

        if item_id in discovered_items:
            adventure["pending_name_item_id"] = None
            save_data()

            embed = discord.Embed(
                title="이미 이름이 등록됐어!",
                description=f"이 유물의 이름은 **{get_adventure_item_name(item_id)}**(으)로 정해졌어.",
                color=discord.Color.gold(),
            )
            await interaction.response.edit_message(embed=embed, view=AdventureTravelView(uid))
            return

        valid, result = validate_relic_name(str(self.relic_name.value))

        if not valid:
            await interaction.response.send_message(f"❌ {result}", ephemeral=True)
            return

        clean_name = result
        discovered_items[item_id] = {
            "name": clean_name,
            "discoverer_id": uid,
            "discoverer_name": interaction.user.display_name,
            "discovered_at": datetime.now(KST).isoformat(),
        }
        adventure["pending_name_item_id"] = None
        save_data()

        rarity = ADVENTURE_RARITIES[ADVENTURE_ITEM_CATALOG[item_id]["rarity"]]
        embed = discord.Embed(
            title="📖 새로운 유물이 도감에 등록됐다!",
            description=(
                f"{rarity['emoji']} 이름: **{clean_name}**\n"
                f"등급: **{rarity['name']}**\n"
                f"최초 발견자: {interaction.user.mention}\n\n"
                "이제 모든 유저에게 이 이름으로 보여."
            ),
            color=discord.Color.gold(),
        )
        pending = adventure.get("pending_event") or {}
        if pending.get("type") == "terrain_choice":
            if pending.get("reason") == "relic":
                pending["detail"] = clean_name
                save_data()
            view = AdventureTerrainChoiceView(uid, pending.get("destinations", []))
            embed.description += "\n\n🔮 이름을 얻은 유물이 반응하며 지형을 바꿀 수 있는 길이 열렸어!"
        else:
            view = AdventureTravelView(uid)
        await interaction.response.edit_message(embed=embed, view=view)


class RelicNamingView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = str(user_id)

    @discord.ui.button(label="✍️ 이름 짓기", style=discord.ButtonStyle.success)
    async def name_relic(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        adventure = get_adventure(self.user_id)
        item_id = adventure.get("pending_name_item_id")

        if not item_id:
            await interaction.response.send_message("이름을 기다리는 유물이 없어.", ephemeral=True)
            return

        if item_id in discovered_items:
            adventure["pending_name_item_id"] = None
            save_data()
            pending = adventure.get("pending_event") or {}
            view = (
                AdventureTerrainChoiceView(self.user_id, pending.get("destinations", []))
                if pending.get("type") == "terrain_choice"
                else AdventureTravelView(self.user_id)
            )
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="이름 등록 완료",
                    description=f"누군가 먼저 **{get_adventure_item_name(item_id)}**(으)로 등록했어.",
                    color=discord.Color.gold(),
                ),
                view=view,
            )
            return

        await interaction.response.send_modal(RelicNameModal(self.user_id))


class AdventureInventoryView(discord.ui.View):
    def __init__(self, user_id, member, page=0):
        super().__init__(timeout=180)
        self.user_id = str(user_id)
        self.member = member
        self.page = max(0, page)
        _, total_pages = build_adventure_inventory_embed(member, self.user_id, self.page)
        self.previous_page.disabled = self.page <= 0
        self.next_page.disabled = self.page >= total_pages - 1

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        self.page = max(0, self.page - 1)
        embed, _ = build_adventure_inventory_embed(self.member, self.user_id, self.page)
        await interaction.response.edit_message(
            embed=embed,
            view=AdventureInventoryView(self.user_id, self.member, self.page),
        )

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        self.page += 1
        embed, total_pages = build_adventure_inventory_embed(self.member, self.user_id, self.page)
        self.page = min(self.page, total_pages - 1)
        await interaction.response.edit_message(
            embed=embed,
            view=AdventureInventoryView(self.user_id, self.member, self.page),
        )


def build_adventure_inventory_embed(member, uid, page=0):
    inventory = get_adventure_inventory(uid)
    entries = [
        (item_id, count)
        for item_id, count in inventory.items()
        if count > 0 and item_id in ADVENTURE_ITEM_CATALOG
    ]

    entries.sort(
        key=lambda pair: (
            -ADVENTURE_RARITY_ORDER[ADVENTURE_ITEM_CATALOG[pair[0]]["rarity"]],
            get_adventure_item_name(pair[0]),
        )
    )

    total_pages = max(1, (len(entries) + ADVENTURE_INVENTORY_PAGE_SIZE - 1) // ADVENTURE_INVENTORY_PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))
    start = page * ADVENTURE_INVENTORY_PAGE_SIZE
    page_entries = entries[start:start + ADVENTURE_INVENTORY_PAGE_SIZE]

    embed = discord.Embed(
        title=f"🎒 {member.display_name}의 모험 가방",
        color=discord.Color.dark_teal(),
    )

    if not page_entries:
        embed.description = "아직 모험에서 얻은 물건이 없어."
    else:
        lines = []
        for item_id, count in page_entries:
            item = ADVENTURE_ITEM_CATALOG[item_id]
            rarity = ADVENTURE_RARITIES[item["rarity"]]
            lines.append(
                f"{rarity['emoji']} **{get_adventure_item_name(item_id)}** ×{count}\n"
                f"└ {rarity['name']} · 기준 가치 {item['value']:,}모라"
            )
        embed.description = "\n\n".join(lines)

    embed.set_footer(
        text=(
            f"페이지 {page + 1}/{total_pages} · 보유 종류 {len(entries)}종 · "
            f"전체 아이템 {len(ADVENTURE_ITEM_CATALOG)}종"
        )
    )
    return embed, total_pages


class RelicDexView(discord.ui.View):
    def __init__(self, page=0):
        super().__init__(timeout=180)
        self.page = max(0, page)
        _, total_pages = build_relic_dex_embed(self.page)
        self.previous_page.disabled = self.page <= 0
        self.next_page.disabled = self.page >= total_pages - 1

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = max(0, self.page - 1)
        embed, _ = build_relic_dex_embed(self.page)
        await interaction.response.edit_message(embed=embed, view=RelicDexView(self.page))

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        embed, total_pages = build_relic_dex_embed(self.page)
        self.page = min(self.page, total_pages - 1)
        await interaction.response.edit_message(embed=embed, view=RelicDexView(self.page))


def build_relic_dex_embed(page=0):
    entries = []

    for item_id, info in discovered_items.items():
        item = ADVENTURE_ITEM_CATALOG.get(item_id)
        if not item or item.get("kind") != "relic":
            continue
        entries.append((item_id, info))

    entries.sort(key=lambda pair: pair[1].get("discovered_at", ""))

    total_pages = max(1, (len(entries) + ADVENTURE_RELIC_PAGE_SIZE - 1) // ADVENTURE_RELIC_PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))
    start = page * ADVENTURE_RELIC_PAGE_SIZE
    page_entries = entries[start:start + ADVENTURE_RELIC_PAGE_SIZE]

    embed = discord.Embed(
        title="📖 서버 유물 도감",
        color=discord.Color.gold(),
    )

    if not page_entries:
        embed.description = "아직 이름 붙은 유물이 하나도 없어."
    else:
        lines = []
        for item_id, info in page_entries:
            item = ADVENTURE_ITEM_CATALOG[item_id]
            rarity = ADVENTURE_RARITIES[item["rarity"]]
            discoverer = info.get("discoverer_name", "알 수 없음")
            lines.append(
                f"{rarity['emoji']} **{info.get('name', '이름 없음')}**\n"
                f"└ {rarity['name']} · 최초 발견자: {discoverer}"
            )
        embed.description = "\n\n".join(lines)

    total_relics = sum(
        1 for item in ADVENTURE_ITEM_CATALOG.values() if item["kind"] == "relic"
    )
    embed.set_footer(
        text=f"페이지 {page + 1}/{total_pages} · 발견 {len(entries)}/{total_relics}종"
    )
    return embed, total_pages


async def get_saved_adventure_thread(guild, adventure):
    """저장된 모험 스레드를 찾고, 보관 상태라면 다시 연다."""
    thread_id = adventure.get("thread_id")
    if not thread_id:
        return None

    try:
        thread_id = int(thread_id)
    except (TypeError, ValueError):
        adventure["thread_id"] = None
        save_data()
        return None

    thread = guild.get_thread(thread_id) or bot.get_channel(thread_id)

    if thread is None:
        try:
            thread = await guild.fetch_channel(thread_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            thread = None

    if not isinstance(thread, discord.Thread):
        adventure["thread_id"] = None
        save_data()
        return None

    if thread.archived:
        try:
            await thread.edit(archived=False, reason="진행 중인 모험 재개")
        except (discord.Forbidden, discord.HTTPException):
            return None

    return thread


def make_adventure_thread_name(member):
    display_name = " ".join(member.display_name.split()).strip() or str(member.id)
    return f"🧭 {display_name}의 모험"[:100]


async def ensure_adventure_thread(interaction, adventure):
    """진행 중인 스레드를 재사용하거나 새 공개 스레드를 만든다."""
    current_channel = interaction.channel

    # 저장된 스레드 안에서 다시 /모험을 친 경우 그대로 사용한다.
    if (
        isinstance(current_channel, discord.Thread)
        and adventure.get("thread_id")
        and str(current_channel.id) == str(adventure.get("thread_id"))
    ):
        if current_channel.archived:
            await current_channel.edit(archived=False, reason="모험 재개")
        return current_channel, False

    saved_thread = await get_saved_adventure_thread(interaction.guild, adventure)
    if saved_thread is not None:
        return saved_thread, False

    # 업데이트 전에 시작한 모험을 임의의 스레드에서 이어가는 경우 현재 스레드를 채택한다.
    if adventure.get("active") and isinstance(current_channel, discord.Thread):
        adventure["thread_id"] = current_channel.id
        save_data()
        return current_channel, False

    parent_channel = (
        current_channel.parent
        if isinstance(current_channel, discord.Thread)
        else current_channel
    )

    if not isinstance(parent_channel, discord.TextChannel):
        raise RuntimeError("이 채널에서는 모험 스레드를 만들 수 없어. 일반 텍스트 채널에서 /모험을 사용해 줘.")

    thread = await parent_channel.create_thread(
        name=make_adventure_thread_name(interaction.user),
        type=discord.ChannelType.public_thread,
        auto_archive_duration=1440,
        reason=f"{interaction.user}의 모험 전용 스레드",
    )

    adventure["thread_id"] = thread.id
    save_data()

    # 공개 스레드라 없어도 들어갈 수 있지만, 가능한 경우 사용자를 바로 참여시킨다.
    try:
        await thread.add_user(interaction.user)
    except (discord.Forbidden, discord.HTTPException):
        pass

    return thread, True


async def send_adventure_screen(channel, member, uid):
    """현재 모험 상태에 맞는 화면을 반드시 모험 스레드에 출력한다."""
    adventure = get_adventure(uid)

    if adventure["active"]:
        pending_name = adventure.get("pending_name_item_id")
        pending_event = adventure.get("pending_event")

        if pending_name:
            embed = discord.Embed(
                title="✨ 이름을 기다리는 유물",
                description=(
                    f"{get_adventure_item_line(pending_name)}\n\n"
                    "계속 모험하기 전에 이름을 지어줘."
                ),
                color=discord.Color.gold(),
            )
            await channel.send(embed=embed, view=RelicNamingView(uid))
            return

        if pending_event and pending_event.get("type") == "terrain_choice":
            await channel.send(
                embed=build_terrain_choice_embed(adventure),
                view=AdventureTerrainChoiceView(uid, pending_event.get("destinations", [])),
            )
            return

        if pending_event and pending_event.get("type") == "monster":
            monster = find_adventure_monster_by_name(pending_event.get("monster_name"))
            trait = get_trait_by_name(pending_event.get("trait_name"))

            if monster:
                monster_tier = pending_event.get("monster_tier", "normal")
                display_name = format_adventure_monster_name(monster["name"], trait, monster_tier)
                terrain = get_terrain_info(pending_event.get("terrain") or adventure.get("terrain"))

                if pending_event.get("is_boss"):
                    resume_title = f"👑 {terrain['name']}의 보스전이 아직 끝나지 않았어!"
                    resume_color = discord.Color.dark_gold()
                elif monster_tier == "calamity":
                    resume_title = "☠️ 재앙급 전투가 아직 끝나지 않았어!"
                    resume_color = discord.Color.dark_red()
                elif monster_tier == "elite":
                    resume_title = "🔥 강적과의 전투가 아직 끝나지 않았어!"
                    resume_color = discord.Color.red()
                else:
                    resume_title = "⚔️ 전투가 아직 끝나지 않았어!"
                    resume_color = discord.Color.orange()

                embed = discord.Embed(
                    title=resume_title,
                    description=(
                        f"지형: **{terrain['emoji']} {terrain['name']}**\n"
                        f"**Lv.{pending_event['monster_level']} {display_name}**\n\n"
                        f"내 모험 레벨: **Lv.{adventure['level']}**\n"
                        f"{get_adventure_equipment_text(adventure)}\n\n"
                        "전투를 시작하거나 도망가야 해."
                    ),
                    color=resume_color,
                )
                await channel.send(embed=embed, view=AdventureBattleView(uid))
                return

            adventure["pending_event"] = None
            save_data()

        if adventure.get("turn_ready_at"):
            embed = build_adventure_waiting_embed(member, adventure)
            await channel.send(embed=embed, view=AdventureTurnWaitingView(uid))
            return

        embed = build_adventure_status_embed(member, adventure)
        await channel.send(embed=embed, view=AdventureTravelView(uid))
        return

    lines = []
    for terrain_key in ADVENTURE_START_TERRAINS:
        terrain = get_terrain_info(terrain_key)
        lines.append(f"{terrain['emoji']} **{terrain['name']}** — {terrain['description']}")

    embed = discord.Embed(
        title="🧭 첫 모험 지형을 선택해!",
        description=(
            "처음에는 사막, 초원, 정글 중 하나에서 출발할 수 있어.\n"
            "모험 도중 보스 격파, 특정 유물, 희귀 갈림길을 통해 다른 지형으로 넘어가게 돼.\n\n"
            + "\n\n".join(lines)
            + "\n\n😈 마계는 고산지대 또는 얼음 지대에서만 진입 가능\n"
            + "☁️ 천계는 마계에서만 진입 가능"
        ),
        color=discord.Color.blurple(),
    )
    await channel.send(embed=embed, view=AdventureStartTerrainView(uid))


@bot.tree.command(name="모험", description="전용 스레드를 만들어 모험을 시작하거나 이어간다", guild=GUILD)
async def adventure_command(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    await interaction.response.defer(ephemeral=True)

    lock = get_adventure_lock(uid)
    async with lock:
        adventure = get_adventure(uid)

        try:
            thread, created = await ensure_adventure_thread(interaction, adventure)
        except RuntimeError as error:
            await interaction.followup.send(f"❌ {error}", ephemeral=True)
            return
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ 스레드를 만들 권한이 없어. 봇에게 `공개 스레드 만들기`, "
                "`스레드에서 메시지 보내기`, `스레드 관리` 권한을 줘.",
                ephemeral=True,
            )
            return
        except discord.HTTPException as error:
            await interaction.followup.send(
                f"❌ 모험 스레드를 만드는 중 오류가 났어: `{error}`",
                ephemeral=True,
            )
            return

        if created:
            await thread.send(
                f"{interaction.user.mention} 전용 모험 스레드야! "
                "이 아래에 뜨는 버튼으로 계속 진행하면 돼."
            )

        await send_adventure_screen(thread, interaction.user, uid)

    if interaction.channel_id == thread.id:
        result_text = "🧭 현재 모험 화면을 이 스레드에 다시 띄웠어."
    elif created:
        result_text = f"🧭 모험 전용 스레드를 만들었어: {thread.mention}"
    else:
        result_text = f"🧭 진행 중인 모험 스레드로 이어졌어: {thread.mention}"

    await interaction.followup.send(result_text, ephemeral=True)


@bot.tree.command(name="가방", description="모험에서 얻은 전리품을 확인한다", guild=GUILD)
async def adventure_inventory_command(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    embed, _ = build_adventure_inventory_embed(interaction.user, uid, 0)
    await interaction.response.send_message(
        embed=embed,
        view=AdventureInventoryView(uid, interaction.user, 0),
    )


@bot.tree.command(name="유물도감", description="서버에서 발견된 이름 있는 유물을 확인한다", guild=GUILD)
async def relic_dex_command(interaction: discord.Interaction):
    embed, _ = build_relic_dex_embed(0)
    await interaction.response.send_message(embed=embed, view=RelicDexView(0))


@bot.tree.command(name="모험상점", description="모험용 아이템을 구매하거나 장착한다", guild=GUILD)
@app_commands.describe(아이템="구매 또는 장착할 아이템 이름. 비워두면 목록 표시")
async def adventure_shop_command(interaction: discord.Interaction, 아이템: str = None):
    uid = str(interaction.user.id)
    info = get_adventure_shop_user(uid)
    adventure = get_adventure(uid)

    if 아이템 is None:
        lines = []
        for name, item in ADVENTURE_SHOP_CATALOG.items():
            if name in info["equipped"]:
                state = "✅ 장착 중"
            elif name in info["owned"]:
                state = "📦 보유 중"
            else:
                state = f"💰 {item['price']:,}모라"

            lines.append(f"**{name}** — {state}\n└ {item['desc']}")

        embed = discord.Embed(
            title="🧭 모험 상점",
            description="\n\n".join(lines),
            color=discord.Color.dark_gold(),
        )
        embed.set_footer(
            text=(
                f"최대 {ADVENTURE_MAX_EQUIPPED}개 장착 가능 · "
                "이름을 입력하면 구매 → 장착 → 해제 순서로 작동"
            )
        )
        await interaction.response.send_message(embed=embed)
        return

    if 아이템 not in ADVENTURE_SHOP_CATALOG:
        await interaction.response.send_message("❌ 그런 모험 아이템은 없어.", ephemeral=True)
        return

    if adventure["active"]:
        await interaction.response.send_message(
            "❌ 모험 중에는 장비를 바꿀 수 없어. 귀환한 뒤 바꿔줘.",
            ephemeral=True,
        )
        return

    item = ADVENTURE_SHOP_CATALOG[아이템]

    if 아이템 in info["equipped"]:
        info["equipped"].remove(아이템)
        save_data()
        await interaction.response.send_message(f"📦 **{아이템}** 장착 해제 완료.")
        return

    if 아이템 in info["owned"]:
        if len(info["equipped"]) >= ADVENTURE_MAX_EQUIPPED:
            await interaction.response.send_message(
                f"❌ 최대 {ADVENTURE_MAX_EQUIPPED}개까지만 장착할 수 있어.",
                ephemeral=True,
            )
            return

        info["equipped"].append(아이템)
        save_data()
        await interaction.response.send_message(f"✅ **{아이템}** 장착 완료!")
        return

    money = get_poker_money(uid)
    if money < item["price"]:
        await interaction.response.send_message(
            f"❌ 모라 부족!\n필요: **{item['price']:,}모라**\n보유: **{money:,}모라**",
            ephemeral=True,
        )
        return

    remove_poker_money(uid, item["price"])
    info["owned"].append(아이템)

    if len(info["equipped"]) < ADVENTURE_MAX_EQUIPPED:
        info["equipped"].append(아이템)
        equip_text = "구매하고 바로 장착했어!"
    else:
        equip_text = "구매했지만 장착 칸이 가득 차서 보관만 했어."

    save_data()
    await interaction.response.send_message(
        f"🛒 **{아이템}** 구매 완료!\n{equip_text}"
    )


@adventure_shop_command.autocomplete("아이템")
async def adventure_shop_autocomplete(interaction: discord.Interaction, current: str):
    current = current.lower().strip()
    names = [
        name
        for name in ADVENTURE_SHOP_CATALOG
        if current in name.lower()
    ][:25]

    return [app_commands.Choice(name=name, value=name) for name in names]


@bot.tree.command(name="모험기록", description="내 모험 기록을 확인한다", guild=GUILD)
async def adventure_record_command(interaction: discord.Interaction):
    adventure = get_adventure(interaction.user.id)

    embed = discord.Embed(
        title=f"🏆 {interaction.user.display_name}의 모험 기록",
        description=(
            f"모험 레벨: **Lv.{adventure['level']}** "
            f"({adventure['exp']}/{get_adventure_required_exp(adventure['level'])} EXP)\n"
            f"현재 무기: **{adventure['weapon']}**\n"
            f"현재 갑옷: **{adventure['armor']}**\n"
            f"레벨 자동 승률 보너스: **+{min(ADVENTURE_LEVEL_WIN_BONUS_CAP, max(0, adventure['level'] - 1) * ADVENTURE_LEVEL_WIN_BONUS):.1f}%**\n\n"
            f"최고 진행: **{adventure['best_steps']}회**\n"
            f"한 모험 최고 처치: **{adventure['best_kills']}마리**\n"
            f"누적 처치: **{adventure['total_kills']}마리**\n"
            f"완료한 모험: **{adventure['total_runs']}회**\n"
            f"최고 도달 지형 단계: **{adventure.get('best_terrain_rank', 0)}/6**\n"
            f"현재 지형: **{get_terrain_name(adventure.get('terrain')) if adventure['active'] else '없음'}**\n"
            f"현재 상태: **{'모험 중' if adventure['active'] else '대기 중'}**"
        ),
        color=discord.Color.purple(),
    )
    await interaction.response.send_message(embed=embed)

# =========================
# 모험 전리품 판매
# =========================

ADVENTURE_SELLABLE_KINDS = {
    "monster_loot",
    "herb",
    "ore",
    "material",
}


@bot.tree.command(
    name="판매",
    description="모험에서 획득한 전리품을 판매한다",
    guild=GUILD
)
@app_commands.describe(
    아이템="판매할 전리품",
    수량="판매할 수량 또는 '전부'"
)
async def adventure_loot_sell(
    interaction: discord.Interaction,
    아이템: str,
    수량: str = "전부"
):
    uid = str(interaction.user.id)

    async with get_adventure_lock(uid):
        inventory = get_adventure_inventory(uid)

        # 자동완성으로 선택하면 item_id가 들어옴
        item_id = 아이템.strip()
        item = ADVENTURE_ITEM_CATALOG.get(item_id)

        # 직접 이름을 입력한 경우 이름으로 다시 검색
        if item is None:
            matching_items = [
                catalog_id
                for catalog_id, catalog_item
                in ADVENTURE_ITEM_CATALOG.items()
                if get_adventure_item_name(catalog_id) == 아이템.strip()
            ]

            if len(matching_items) == 1:
                item_id = matching_items[0]
                item = ADVENTURE_ITEM_CATALOG[item_id]

            elif len(matching_items) > 1:
                await interaction.response.send_message(
                    "❌ 같은 이름의 아이템이 여러 개야. "
                    "자동완성 목록에서 선택해 줘.",
                    ephemeral=True
                )
                return

        if item is None:
            await interaction.response.send_message(
                "❌ 그런 전리품은 가방에 없어.",
                ephemeral=True
            )
            return

        if item.get("kind") not in ADVENTURE_SELLABLE_KINDS:
            await interaction.response.send_message(
                "❌ 장비와 유물은 판매할 수 없어.",
                ephemeral=True
            )
            return

        owned_amount = int(inventory.get(item_id, 0))

        if owned_amount <= 0:
            await interaction.response.send_message(
                "❌ 그 전리품을 가지고 있지 않아.",
                ephemeral=True
            )
            return

        amount_text = 수량.strip().lower().replace(",", "")

        if amount_text in {"전부", "모두", "all"}:
            sell_amount = owned_amount
        else:
            try:
                sell_amount = int(amount_text)
            except ValueError:
                await interaction.response.send_message(
                    "❌ 수량에는 숫자 또는 `전부`를 입력해 줘.",
                    ephemeral=True
                )
                return

        if sell_amount <= 0:
            await interaction.response.send_message(
                "❌ 판매 수량은 1개 이상이어야 해.",
                ephemeral=True
            )
            return

        if sell_amount > owned_amount:
            await interaction.response.send_message(
                f"❌ 수량이 부족해.\n"
                f"현재 보유량: **{owned_amount:,}개**",
                ephemeral=True
            )
            return

        unit_price = max(1, int(item.get("value", 1)))
        total_price = unit_price * sell_amount

        remaining = owned_amount - sell_amount

        if remaining > 0:
            inventory[item_id] = remaining
        else:
            inventory.pop(item_id, None)

        current_money = add_poker_money(uid, total_price)
        item_name = get_adventure_item_name(item_id)

        embed = discord.Embed(
            title="💰 전리품 판매 완료!",
            description=(
                f"**{item_name}** ×{sell_amount:,}개를 판매했어.\n\n"
                f"개당 가격: **{unit_price:,}모라**\n"
                f"획득 금액: **{total_price:,}모라**\n"
                f"남은 수량: **{remaining:,}개**\n"
                f"현재 보유 모라: **{current_money:,}모라**"
            ),
            color=discord.Color.gold()
        )

        await interaction.response.send_message(embed=embed)


@adventure_loot_sell.autocomplete("아이템")
async def adventure_loot_sell_autocomplete(
    interaction: discord.Interaction,
    current: str
):
    uid = str(interaction.user.id)
    inventory = get_adventure_inventory(uid)
    current = current.strip().lower()

    choices = []

    for item_id, count in inventory.items():
        if count <= 0:
            continue

        item = ADVENTURE_ITEM_CATALOG.get(item_id)

        if not item:
            continue

        if item.get("kind") not in ADVENTURE_SELLABLE_KINDS:
            continue

        item_name = get_adventure_item_name(item_id)

        if current and current not in item_name.lower():
            continue

        unit_price = max(1, int(item.get("value", 1)))

        label = (
            f"{item_name} ×{count:,} "
            f"· 개당 {unit_price:,}모라"
        )

        choices.append(
            app_commands.Choice(
                name=label[:100],
                value=item_id
            )
        )

        if len(choices) >= 25:
            break

    return choices

@bot.tree.command(
    name="전체판매",
    description="판매 가능한 모험 전리품을 모두 판매한다",
    guild=GUILD
)
async def adventure_loot_sell_all(
    interaction: discord.Interaction
):
    uid = str(interaction.user.id)

    async with get_adventure_lock(uid):
        inventory = get_adventure_inventory(uid)

        sold_items = []
        total_count = 0
        total_price = 0

        for item_id, owned_amount in list(inventory.items()):
            owned_amount = int(owned_amount)

            if owned_amount <= 0:
                continue

            item = ADVENTURE_ITEM_CATALOG.get(item_id)

            if not item:
                continue

            # 장비, 유물 등은 판매하지 않음
            if item.get("kind") not in ADVENTURE_SELLABLE_KINDS:
                continue

            unit_price = max(1, int(item.get("value", 1)))
            item_total_price = unit_price * owned_amount
            item_name = get_adventure_item_name(item_id)

            sold_items.append({
                "name": item_name,
                "amount": owned_amount,
                "price": item_total_price
            })

            total_count += owned_amount
            total_price += item_total_price

            # 전량 판매했으므로 가방에서 제거
            inventory.pop(item_id, None)

        if not sold_items:
            await interaction.response.send_message(
                "❌ 판매할 수 있는 전리품이 없어.\n"
                "장비와 유물은 전체 판매에서 제외돼.",
                ephemeral=True
            )
            return

        current_money = add_poker_money(uid, total_price)
        save_data()

        # 판매 금액이 높은 순서로 표시
        sold_items.sort(
            key=lambda sold: sold["price"],
            reverse=True
        )

        item_lines = []

        for sold in sold_items[:15]:
            item_lines.append(
                f"• **{sold['name']}** ×{sold['amount']:,}"
                f" → {sold['price']:,}모라"
            )

        if len(sold_items) > 15:
            item_lines.append(
                f"\n외 **{len(sold_items) - 15}종**"
            )

        embed = discord.Embed(
            title="💰 전리품 전체 판매 완료!",
            description="\n".join(item_lines),
            color=discord.Color.gold()
        )

        embed.add_field(
            name="📦 판매 결과",
            value=(
                f"판매 종류: **{len(sold_items):,}종**\n"
                f"판매 수량: **{total_count:,}개**\n"
                f"획득 금액: **{total_price:,}모라**"
            ),
            inline=False
        )

        embed.add_field(
            name="💵 현재 보유 모라",
            value=f"**{current_money:,}모라**",
            inline=False
        )

        embed.set_footer(
            text="장비와 유물은 판매되지 않았어."
        )

        await interaction.response.send_message(
            embed=embed
        )
        
WAREHOUSE_DAILY_TAX_RATE = 0.001      # 하루 0.1%
WAREHOUSE_WITHDRAW_TAX_RATE = 0.005   # 출금 0.5%

def get_warehouse_money(user_id):
    uid = str(user_id)
    return int(warehouses.get(uid, 0))


def add_warehouse_money(user_id, amount):
    uid = str(user_id)
    warehouses[uid] = max(0, get_warehouse_money(uid) + int(amount))
    save_data()
    return warehouses[uid]


def apply_warehouse_daily_tax(user_id):
    uid = str(user_id)
    now = datetime.now(timezone.utc)

    balance = get_warehouse_money(uid)

    if balance <= 0:
        warehouse_last_tax[uid] = now
        save_data()
        return 0, 0

    last = warehouse_last_tax.get(uid)

    if last is None:
        warehouse_last_tax[uid] = now
        save_data()
        return 0, 0

    days = (now.date() - last.date()).days

    if days <= 0:
        return 0, balance

    total_tax = 0

    for _ in range(days):
        current = get_warehouse_money(uid)

        if current <= 0:
            break

        tax = math.ceil(current * WAREHOUSE_DAILY_TAX_RATE)
        tax = min(tax, current)

        warehouses[uid] = current - tax
        total_tax += tax

    warehouse_last_tax[uid] = now
    save_data()

    return total_tax, get_warehouse_money(uid)

@bot.tree.command(name="창고", description="모라를 창고에 입금하거나 출금합니다.", guild=GUILD)
@app_commands.describe(
    동작="조회 / 입금 / 출금",
    금액="입금하거나 출금할 모라"
)
@app_commands.choices(
    동작=[
        app_commands.Choice(name="조회", value="조회"),
        app_commands.Choice(name="입금", value="입금"),
        app_commands.Choice(name="출금", value="출금"),
    ]
)
async def warehouse_command(
    interaction: discord.Interaction,
    동작: app_commands.Choice[str],
    금액: int = 0
):
    uid = str(interaction.user.id)

    daily_tax, warehouse_after_tax = apply_warehouse_daily_tax(uid)

    wallet = get_poker_money(uid)
    warehouse = get_warehouse_money(uid)

    if 동작.value == "조회":
        tax_text = (
            f"\n💸 밀린 보관료로 **{daily_tax:,}모라**가 빠져나갔어."
            if daily_tax > 0 else ""
        )

        await interaction.response.send_message(
            f"🏦 {interaction.user.mention}의 창고\n"
            f"지갑: **{wallet:,}모라**\n"
            f"창고: **{warehouse:,}모라**"
            f"{tax_text}"
        )
        return

    if 금액 <= 0:
        await interaction.response.send_message(
            "❌ 금액은 **1모라 이상**으로 입력해줘.",
            ephemeral=True
        )
        return

    if 동작.value == "입금":
        if wallet < 금액:
            await interaction.response.send_message(
                f"❌ 지갑에 모라가 부족해!\n"
                f"보유: **{wallet:,}모라**\n"
                f"필요: **{금액:,}모라**",
                ephemeral=True
            )
            return

        add_poker_money(uid, -금액)
        add_warehouse_money(uid, 금액)

        await interaction.response.send_message(
            f"🏦 창고 입금 완료!\n"
            f"입금액: **{금액:,}모라**\n"
            f"입금 세금: **0모라**\n"
            f"현재 지갑: **{get_poker_money(uid):,}모라**\n"
            f"현재 창고: **{get_warehouse_money(uid):,}모라**"
        )
        return

    if 동작.value == "출금":
        if warehouse < 금액:
            await interaction.response.send_message(
                f"❌ 창고에 모라가 부족해!\n"
                f"창고 잔액: **{warehouse:,}모라**\n"
                f"출금 요청: **{금액:,}모라**",
                ephemeral=True
            )
            return

        withdraw_tax = math.ceil(금액 * WAREHOUSE_WITHDRAW_TAX_RATE)
        receive_amount = max(0, 금액 - withdraw_tax)

        add_warehouse_money(uid, -금액)
        add_poker_money(uid, receive_amount)

        await interaction.response.send_message(
            f"🏦 창고 출금 완료!\n"
            f"출금액: **{금액:,}모라**\n"
            f"출금 수수료 0.5%: **{withdraw_tax:,}모라**\n"
            f"실수령액: **{receive_amount:,}모라**\n"
            f"현재 지갑: **{get_poker_money(uid):,}모라**\n"
            f"현재 창고: **{get_warehouse_money(uid):,}모라**"
        )
        return



@bot.event
async def on_ready():
    for uid in list(warehouses.keys()):
        apply_warehouse_daily_tax(uid)
    if not ranking_update_loop.is_running():
        ranking_update_loop.start()
    
    if not birthday_check.is_running():
        birthday_check.start()

    if not voice_kick_check.is_running():
        voice_kick_check.start()

    if not voice_xp_loop.is_running():
        voice_xp_loop.start()

    synced = await bot.tree.sync(guild=GUILD)

    if not time_notice_loop.is_running():
        time_notice_loop.start()
    
    guild = bot.get_guild(GUILD_ID)
    if guild:
        await update_ranking_message(guild)

    sticky_channel = bot.get_channel(STICKY_CHANNEL_ID)

    if sticky_channel:
        await refresh_sticky_message(sticky_channel)
    
    print(f"로그인됨: {bot.user}")
    print(f"길드 명령어 {len(synced)}개 동기화")

bot.run(TOKEN)
