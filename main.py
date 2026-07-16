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
import hashlib

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
    "discovered_foods": {},
    "relic_upgrades": {},
    "shop_items": {},
    "party_profiles": {},
    "relic_discovery_stats": {},
    "fever_multiplier": 1.0
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
discovered_foods = {}
relic_upgrades = {}
shop_items = {}
party_profiles = {}
relic_discovery_stats = {}

def remove_poker_money(user_id, amount):
    uid = str(user_id)

    poker_money[uid] = max(
        0,
        poker_money.get(uid, 0) - int(amount)
    )

    save_data()
    
def load_data():
    global data, poker_money, poker_last_claim, favor, user_memory, characters, hunt_users, weapons, primogems, quests, achievements, character_pity, levels, checkin, warnings, warehouses, warehouse_last_tax, adventures, inventories, discovered_items, discovered_foods, relic_upgrades, shop_items, party_profiles, relic_discovery_stats
    
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        
        data["warehouses"] = loaded.get("warehouses", {})
        data["warehouse_last_tax"] = loaded.get("warehouse_last_tax", {})
        data["adventures"] = loaded.get("adventures", {})
        data["inventories"] = loaded.get("inventories", {})
        data["discovered_items"] = loaded.get("discovered_items", {})
        data["discovered_foods"] = loaded.get("discovered_foods", {})
        data["relic_upgrades"] = loaded.get("relic_upgrades", {})
        data["shop_items"] = loaded.get("shop_items", {})
        data["party_profiles"] = loaded.get("party_profiles", {})
        data["relic_discovery_stats"] = loaded.get("relic_discovery_stats", {})
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
        data["fever_multiplier"] = loaded.get("fever_multiplier", 1.0)

    try:
        data["fever_multiplier"] = max(0.0, float(data.get("fever_multiplier", 1.0)))
    except (TypeError, ValueError):
        data["fever_multiplier"] = 1.0

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
    discovered_items = data.get("discovered_items", {})
    discovered_foods = data.get("discovered_foods", {})
    relic_upgrades = data["relic_upgrades"]
    shop_items = data["shop_items"]
    party_profiles = data.get("party_profiles", {})
    relic_discovery_stats = data.get("relic_discovery_stats", {})
    if not isinstance(party_profiles, dict):
        party_profiles = {}
    if not isinstance(relic_discovery_stats, dict):
        relic_discovery_stats = {}
    data["party_profiles"] = party_profiles
    data["relic_discovery_stats"] = relic_discovery_stats
    
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
    data["discovered_foods"] = discovered_foods
    data["relic_upgrades"] = relic_upgrades
    data["shop_items"] = shop_items
    data["party_profiles"] = party_profiles
    data["relic_discovery_stats"] = relic_discovery_stats
    data["fever_multiplier"] = get_fever_multiplier()
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


def get_fever_multiplier():
    try:
        multiplier = float(data.get("fever_multiplier", 1.0))
    except (TypeError, ValueError):
        multiplier = 1.0

    if not math.isfinite(multiplier):
        multiplier = 1.0

    return max(0.0, multiplier)


def apply_fever_multiplier(amount):
    try:
        base_amount = max(0.0, float(amount))
    except (TypeError, ValueError):
        return 0

    multiplied = base_amount * get_fever_multiplier()
    if multiplied <= 0:
        return 0

    # 소수 배수에서도 실제 획득 경험치가 0으로 사라지지 않도록 반올림한다.
    return max(1, int(math.floor(multiplied + 0.5)))


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
        return 0

    amount = apply_fever_multiplier(amount)
    info = get_level_data(member.id)
    old_level = info["level"]

    info["xp"] += amount

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

    return amount
            
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

WEAPON_GACHA_COST = 120


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
    "신": "🎉🎉🎉 믿습니다!! 우리 서버에 {role}이신 {user}님께서 강림하셨다!!",
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
WEAPON_GACHA_COST = 120
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

    if get_primogems(uid) < cost:
        await interaction.response.send_message(
            f"❌ 원석 부족!\n필요: **{cost:,}원석**\n보유: **{get_primogems(uid):,}원석**",
            ephemeral=True
        )
        return

    add_primogems(uid, -cost)

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
        name="현재 원석",
        value=f"{get_primogems(uid):,} 원석",
        inline=True
    )

    embed.set_footer(text=f"전무 기원 1회 {WEAPON_GACHA_COST}원석")

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
    "전사": {
        "stats": ["str", "vit"],
        "desc": "힘과 체력 특화. 정면 전투의 승률과 생존력을 함께 올리는 직업."
    },
    "궁수": {
        "stats": ["dex", "str"],
        "desc": "민첩과 힘 특화. 약한 적을 잘 포착하고 안정적으로 피해를 누적하는 직업."
    },
    "도적": {
        "stats": ["dex", "int"],
        "desc": "민첩과 지능 특화. 사냥 안정성과 모라·경험치 수익을 함께 챙기는 직업."
    },
    "법사": {
        "stats": ["mag", "int"],
        "desc": "마력과 지능 특화. 마력 폭주와 높은 보상 효율을 노리는 직업."
    }
}

JOB_CHANGE_BASE_COST = 50_000
JOB_CHANGE_MAX_COST = 500_000

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
    "용사의 성검": {"price": 6500000, "bonus": 270},

    # 17번 연구소 전용 무기. 상점 구매 및 일반 장비 드롭으로는 절대 획득할 수 없다.
    "P90": {"price": 0, "bonus": 95, "obtain_only": True},
    "AK12": {"price": 0, "bonus": 145, "obtain_only": True},
    "MINIGUN": {"price": 0, "bonus": 235, "obtain_only": True},

    # 외곽 / !@$*!& 전용 장비. 지정된 적 외에는 절대 드롭하지 않는다.
    "홍련의 신검": {"price": 0, "bonus": 310, "obtain_only": True},
    "폭풍의 신검": {"price": 0, "bonus": 320, "obtain_only": True},
    "종말의 마검": {"price": 0, "bonus": 420, "obtain_only": True},
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
    "용사의 갑옷": {"price": 5000000, "bonus": 200},

    # 외곽 신 전용 방어구. 일반 장비 추첨에서는 제외된다.
    "심해신의 예복": {"price": 0, "bonus": 260, "obtain_only": True},
    "대지신의 갑주": {"price": 0, "bonus": 280, "obtain_only": True},
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
    {"name": "수계 사냥개 무리", "min": 135, "max": 165, "penalty": 385},
    {"name": "철갑 용 도마뱀", "min": 160, "max": 185, "penalty": 450},
    {"name": "황금 늑대왕", "min": 180, "max": 200, "penalty": 495},
    {"name": "아펩의 수호자", "min": 200, "max": 235, "penalty": 520},
    {"name": "타르탈리아", "min": 230, "max": 275, "penalty": 750},
    {"name": "라이덴 쇼군", "min": 270, "max": 315, "penalty": 820},
    {"name": "천리의 유지자", "min": 310, "max": 425, "penalty": 1000},
    {"name": "마왕", "min": 420, "max": 1000, "penalty": 3000},

    # 모험 최종장 전용 몬스터
    {"name": "불의 신", "min": 330, "max": 470, "penalty": 1450},
    {"name": "물의 신", "min": 340, "max": 480, "penalty": 1500},
    {"name": "바람의 신", "min": 350, "max": 490, "penalty": 1550},
    {"name": "땅의 신", "min": 360, "max": 510, "penalty": 1650},
    {"name": "대마왕", "min": 380, "max": 560, "penalty": 1900},
    {"name": "시설 가드", "min": 390, "max": 570, "penalty": 2150},
    {"name": "기동특수부대원", "min": 410, "max": 610, "penalty": 2750},
    {"name": "알파 부대원", "min": 530, "max": 700, "penalty": 3350},
    {"name": "알파 부대장", "min": 650, "max": 930, "penalty": 4750},
    {"name": "저거너트", "min": 1000, "max": 1700, "penalty": 6850},
    {"name": "39번 실험체", "min": 1500, "max": 2720, "penalty": 12100},
    {"name": "1번 실험체", "min": 2530, "max": 3760, "penalty": 25400},
    {"name": "각성한 매드 사이언티스트", "min": 5570, "max": 7820, "penalty": 52900},
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

    if uid not in hunt_users or not isinstance(hunt_users[uid], dict):
        hunt_users[uid] = {}

    user = hunt_users[uid]

    defaults = {
        "level": 1,
        "exp": 0,
        "weapon": "무인검",
        "armor": "모험가 세트",
        "owned_weapons": ["무인검"],
        "owned_armors": ["모험가 세트"],
        "lives": 3,
        "stat_point": 3,
        "job": None,
        "job_change_count": 0,
        "allocated_stat_points": 0,
        "str": 0,
        "dex": 0,
        "int": 0,
        "mag": 0,
        "vit": 0
    }

    for key, value in defaults.items():
        if key not in user:
            if isinstance(value, list):
                user[key] = value.copy()
            elif isinstance(value, dict):
                user[key] = value.copy()
            else:
                user[key] = value

    # 예전 사냥 데이터에는 보유 장비 목록이 없었으므로 안전하게 마이그레이션한다.
    if not isinstance(user.get("owned_weapons"), list):
        user["owned_weapons"] = ["무인검"]
    if not isinstance(user.get("owned_armors"), list):
        user["owned_armors"] = ["모험가 세트"]

    # 존재하지 않는 장비와 중복값을 제거한다.
    user["owned_weapons"] = list(dict.fromkeys(
        name for name in user["owned_weapons"]
        if isinstance(name, str) and name in WEAPONS
    ))
    user["owned_armors"] = list(dict.fromkeys(
        name for name in user["owned_armors"]
        if isinstance(name, str) and name in ARMORS
    ))

    if "무인검" not in user["owned_weapons"]:
        user["owned_weapons"].insert(0, "무인검")
    if "모험가 세트" not in user["owned_armors"]:
        user["owned_armors"].insert(0, "모험가 세트")

    # 기존에 장착 중이던 장비는 보유 장비로 자동 등록한다.
    if user.get("weapon") not in WEAPONS:
        user["weapon"] = "무인검"
    if user.get("armor") not in ARMORS:
        user["armor"] = "모험가 세트"

    if user["weapon"] not in user["owned_weapons"]:
        user["owned_weapons"].append(user["weapon"])
    if user["armor"] not in user["owned_armors"]:
        user["owned_armors"].append(user["armor"])

    user["job_change_count"] = max(0, int(user.get("job_change_count", 0)))
    if "allocated_stat_points" not in user or not isinstance(user.get("allocated_stat_points"), int):
        total_stats = sum(max(0, int(user.get(key, 0))) for key in STAT_KR)
        earned_points = 3 + max(0, int(user.get("level", 1)) - 1) * 5
        estimated_spent = max(0, earned_points - max(0, int(user.get("stat_point", 0))))
        user["allocated_stat_points"] = min(total_stats, estimated_spent)
    user["allocated_stat_points"] = max(0, int(user.get("allocated_stat_points", 0)))

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
    amount = apply_fever_multiplier(amount)
    user["exp"] += amount
    leveled = 0

    while user["exp"] >= get_required_exp(user["level"]):
        user["exp"] -= get_required_exp(user["level"])
        user["level"] += 1
        user["stat_point"] += 5
        leveled += 1

    return leveled, amount


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

        leveled, exp = give_hunt_exp(user, exp)

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
        user["allocated_stat_points"] = max(0, int(user.get("allocated_stat_points", 0))) + amount

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


@bot.tree.command(name="직업변경", description="직업과 사냥 스탯을 초기화하고 다른 직업으로 변경한다", guild=GUILD)
@app_commands.describe(이름="변경할 직업")
async def change_job(interaction: discord.Interaction, 이름: str):
    uid = str(interaction.user.id)
    user = get_hunt_user(uid)

    if user["level"] < 21:
        await interaction.response.send_message("❌ 21레벨부터 직업을 변경할 수 있어.", ephemeral=True)
        return
    if 이름 not in JOBS:
        await interaction.response.send_message("❌ 없는 직업이야. 가능: 전사, 궁수, 도적, 법사", ephemeral=True)
        return
    if user.get("job") is None:
        await interaction.response.send_message("❌ 아직 직업이 없어. 먼저 `/직업`으로 선택해줘.", ephemeral=True)
        return
    if user.get("job") == 이름:
        await interaction.response.send_message("❌ 이미 그 직업이야.", ephemeral=True)
        return

    change_count = max(0, int(user.get("job_change_count", 0)))
    cost = 0 if change_count == 0 else min(JOB_CHANGE_MAX_COST, JOB_CHANGE_BASE_COST * (2 ** (change_count - 1)))
    if get_poker_money(uid) < cost:
        await interaction.response.send_message(
            f"❌ 직업 변경 비용이 부족해.\n필요: **{cost:,}모라**\n보유: **{get_poker_money(uid):,}모라**",
            ephemeral=True,
        )
        return

    old_job = user["job"]
    refunded = max(0, int(user.get("allocated_stat_points", 0)))
    if cost > 0:
        add_poker_money(uid, -cost)

    for stat_key in STAT_KR:
        user[stat_key] = 0
    user["stat_point"] = max(0, int(user.get("stat_point", 0))) + refunded
    user["allocated_stat_points"] = 0
    user["job"] = 이름
    user["job_change_count"] = change_count + 1
    save_data()

    stats = ", ".join(STAT_KR[s] for s in JOBS[이름]["stats"])
    next_count = user["job_change_count"]
    next_cost = min(JOB_CHANGE_MAX_COST, JOB_CHANGE_BASE_COST * (2 ** max(0, next_count - 1)))
    await interaction.response.send_message(
        f"✅ **{old_job} → {이름}** 직업 변경 완료!\n"
        f"환급된 스탯 포인트: **{refunded}P**\n"
        f"지불 비용: **{cost:,}모라**\n"
        f"새 특화 스탯: **{stats}**\n"
        f"다음 변경 비용: **{next_cost:,}모라**"
    )


@bot.tree.command(name="무기", description="무기를 구매하거나 확인한다", guild=GUILD)
@app_commands.describe(이름="구매하거나 장착할 무기 이름")
async def weapon_shop(interaction: discord.Interaction, 이름: str = None):
    uid = str(interaction.user.id)
    user = get_hunt_user(uid)
    owned_weapons = user["owned_weapons"]

    if 이름 is None:
        embed = discord.Embed(
            title="🗡️ 무기 상점",
            color=discord.Color.dark_gold()
        )

        lines = []
        for name, info in WEAPONS.items():
            if info.get("obtain_only"):
                continue

            if user["weapon"] == name:
                state = " ✅ 장착중"
            elif name in owned_weapons:
                state = " ✅ 보유중"
            else:
                state = ""

            lines.append(
                f"**{name}** - {info['price']:,}모라 / "
                f"승률 +{info['bonus']}%{state}"
            )

        embed.description = "\n".join(lines)
        await interaction.response.send_message(embed=embed)
        return

    이름 = 이름.strip()

    if 이름 not in WEAPONS:
        await interaction.response.send_message("❌ 그런 무기는 없음.", ephemeral=True)
        return

    if WEAPONS[이름].get("obtain_only"):
        await interaction.response.send_message(
            "❌ 이 무기는 상점에서 살 수 없어. 지정된 적을 처치해야만 획득할 수 있어.",
            ephemeral=True,
        )
        return

    # 이미 구매한 장비는 다시 돈을 받지 않고 바로 장착한다.
    if 이름 in owned_weapons:
        user["weapon"] = 이름
        save_data()
        await interaction.response.send_message(
            f"🗡️ **{이름}** 장착 완료!\n"
            f"승률 보너스: **+{WEAPONS[이름]['bonus']}%**"
        )
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
    owned_weapons.append(이름)
    user["weapon"] = 이름
    save_data()

    await interaction.response.send_message(
        f"🗡️ **{이름}** 구매 및 장착 완료!\n"
        f"승률 보너스: **+{WEAPONS[이름]['bonus']}%**"
    )


@bot.tree.command(name="갑옷", description="갑옷을 구매하거나 확인한다", guild=GUILD)
@app_commands.describe(이름="구매하거나 장착할 갑옷 이름")
async def armor_shop(interaction: discord.Interaction, 이름: str = None):
    uid = str(interaction.user.id)
    user = get_hunt_user(uid)
    owned_armors = user["owned_armors"]

    if 이름 is None:
        embed = discord.Embed(
            title="🛡️ 갑옷 상점",
            color=discord.Color.dark_teal()
        )

        lines = []
        for name, info in ARMORS.items():
            if info.get("obtain_only"):
                continue

            if user["armor"] == name:
                state = " ✅ 장착중"
            elif name in owned_armors:
                state = " ✅ 보유중"
            else:
                state = ""

            lines.append(
                f"**{name}** - {info['price']:,}모라 / "
                f"승률 +{info['bonus']}%{state}"
            )

        embed.description = "\n".join(lines)
        await interaction.response.send_message(embed=embed)
        return

    이름 = 이름.strip()

    if 이름 not in ARMORS:
        await interaction.response.send_message("❌ 그런 갑옷은 없음.", ephemeral=True)
        return

    if ARMORS[이름].get("obtain_only"):
        await interaction.response.send_message(
            "❌ 이 갑옷은 상점에서 살 수 없어. 지정된 적을 처치해야만 획득할 수 있어.",
            ephemeral=True,
        )
        return

    # 이미 구매한 장비는 다시 돈을 받지 않고 바로 장착한다.
    if 이름 in owned_armors:
        user["armor"] = 이름
        save_data()
        await interaction.response.send_message(
            f"🛡️ **{이름}** 장착 완료!\n"
            f"승률 보너스: **+{ARMORS[이름]['bonus']}%**"
        )
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
    owned_armors.append(이름)
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

@bot.tree.command(
    name="사냥장비변경",
    description="보유 중인 사냥 장비를 변경한다",
    guild=GUILD
)
@app_commands.describe(
    종류="변경할 장비 종류",
    이름="장착할 장비 이름"
)
@app_commands.choices(
    종류=[
        app_commands.Choice(name="무기", value="weapon"),
        app_commands.Choice(name="갑옷", value="armor"),
    ]
)
async def hunt_equipment_change(
    interaction: discord.Interaction,
    종류: app_commands.Choice[str],
    이름: str
):
    uid = str(interaction.user.id)
    user = get_hunt_user(uid)
    equipment_type = 종류.value
    equipment_name = 이름.strip()

    if equipment_type == "weapon":
        equipment_data = WEAPONS
        owned_key = "owned_weapons"
        equipped_key = "weapon"
        type_name = "무기"
        emoji = "🗡️"
    else:
        equipment_data = ARMORS
        owned_key = "owned_armors"
        equipped_key = "armor"
        type_name = "갑옷"
        emoji = "🛡️"

    if equipment_name not in equipment_data:
        await interaction.response.send_message(
            f"❌ 존재하지 않는 {type_name}야.",
            ephemeral=True
        )
        return

    if equipment_name not in user[owned_key]:
        await interaction.response.send_message(
            f"❌ **{equipment_name}**은(는) 보유하지 않은 {type_name}야.",
            ephemeral=True
        )
        return

    if user[equipped_key] == equipment_name:
        await interaction.response.send_message(
            f"❌ 이미 **{equipment_name}**을(를) 장착 중이야.",
            ephemeral=True
        )
        return

    user[equipped_key] = equipment_name
    save_data()

    await interaction.response.send_message(
        f"{emoji} 사냥 {type_name} 변경 완료!\n"
        f"장착 장비: **{equipment_name}**\n"
        f"승률 보너스: **+{equipment_data[equipment_name]['bonus']}%**"
    )


@hunt_equipment_change.autocomplete("이름")
async def hunt_equipment_change_autocomplete(
    interaction: discord.Interaction,
    current: str
):
    user = get_hunt_user(interaction.user.id)
    equipment_type = getattr(interaction.namespace, "종류", None)

    if isinstance(equipment_type, app_commands.Choice):
        equipment_type = equipment_type.value

    if equipment_type == "weapon":
        owned = user["owned_weapons"]
    elif equipment_type == "armor":
        owned = user["owned_armors"]
    else:
        owned = []

    current = current.strip().lower()
    return [
        app_commands.Choice(name=name[:100], value=name)
        for name in owned
        if current in name.lower()
    ][:25]


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

@bot.tree.command(
    name="피버타임",
    description="서버 전체 경험치 배수를 설정한다 (서버장 전용)",
    guild=GUILD
)
@app_commands.describe(
    배수="적용할 경험치 배수 (예: 2, 1.2, 0.5 / 1은 정상 배율)"
)
async def fever_time_command(
    interaction: discord.Interaction,
    배수: float
):
    if interaction.guild is None or interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message(
            "❌ 이 명령어는 서버장만 사용할 수 있어.",
            ephemeral=True
        )
        return

    if not math.isfinite(배수) or 배수 < 0 or 배수 > 100:
        await interaction.response.send_message(
            "❌ 배수는 **0 이상 100 이하의 숫자**로 입력해줘.",
            ephemeral=True
        )
        return

    old_multiplier = get_fever_multiplier()
    data["fever_multiplier"] = float(배수)
    save_data()

    if 배수 == 1:
        title = "✅ 피버타임 종료"
        description = "서버 전체 경험치 배수가 **1배(기본값)**로 돌아왔어."
        color = discord.Color.green()
    elif 배수 == 0:
        title = "⛔ 경험치 획득 중지"
        description = "서버 전체 경험치 배수가 **0배**로 설정됐어."
        color = discord.Color.red()
    else:
        title = "🔥 피버타임 설정"
        description = f"이 서버에서 얻는 모든 경험치가 이제 **{배수:g}배**로 적용돼!"
        color = discord.Color.gold()

    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    embed.add_field(
        name="배수 변경",
        value=f"`{old_multiplier:g}배` → `{배수:g}배`",
        inline=False
    )
    embed.set_footer(text="채팅 · 음성 · 출석 · 사냥 · 모험 · 파티 모험 경험치에 적용")

    await interaction.response.send_message(embed=embed)


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
    700: 1524344010863411352,
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

    xp_reward = await add_xp(interaction.user, xp_reward, "출석 체크")

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

RELIC_MAX_ENHANCEMENT = 7
RELIC_MAX_EQUIPPED = 3
RELIC_FAILURE_MATERIAL_CONSUME_RATE = 0.50
RELIC_PITY_BONUS_PER_FAIL = 8.0
RELIC_PITY_MAX_SUCCESS_RATE = 95.0

# 디스코드는 일반 글자에 임의 색상을 넣을 수 없어서,
# 상세 화면에서는 ANSI 색상 + 색상 이모지 + 임베드 색상을 함께 사용한다.
RELIC_ENHANCEMENT_STYLES = {
    0: {"emoji": "⚪", "name": "무강화", "color": 0x7F8C8D, "ansi": 37},
    1: {"emoji": "🔴", "name": "빨강", "color": 0xE74C3C, "ansi": 31},
    2: {"emoji": "🟠", "name": "주황", "color": 0xFF8C00, "ansi": 33},
    3: {"emoji": "🟡", "name": "노랑", "color": 0xF1C40F, "ansi": 93},
    4: {"emoji": "🟢", "name": "초록", "color": 0x2ECC71, "ansi": 32},
    5: {"emoji": "🔵", "name": "파랑", "color": 0x3498DB, "ansi": 34},
    6: {"emoji": "🔷", "name": "남색", "color": 0x4B0082, "ansi": 36},
    7: {"emoji": "🟣", "name": "보라", "color": 0x9B59B6, "ansi": 35},
}

# 유물 등급별로 한 번의 강화에서 요구되는 재료 종류/기본 수량/성공률이 달라진다.
# 실제 수량은 목표 강화 단계와 재료 자체의 희귀도까지 반영하여 고정 랜덤으로 계산된다.
RELIC_UPGRADE_RULES = {
    "uncommon": {
        "type_range": (2, 3),
        "amount_range": (2, 5),
        "success": [100, 95, 90, 82, 74, 66, 58],
    },
    "rare": {
        "type_range": (2, 4),
        "amount_range": (3, 7),
        "success": [100, 92, 84, 76, 68, 60, 52],
    },
    "epic": {
        "type_range": (3, 4),
        "amount_range": (4, 9),
        "success": [96, 88, 80, 72, 64, 54, 44],
    },
    "legendary": {
        "type_range": (3, 5),
        "amount_range": (6, 12),
        "success": [92, 84, 76, 68, 58, 48, 38],
    },
    "mythic": {
        "type_range": (4, 6),
        "amount_range": (8, 16),
        "success": [88, 80, 72, 64, 54, 44, 34],
    },
    "transcendent": {
        "type_range": (5, 6),
        "amount_range": (14, 28),
        "success": [84, 76, 68, 60, 50, 40, 30],
    },
}


# 유물 속성은 이름과 무관하게 유물 ID와 출현 지형으로 고정된다.
# 최초 발견자는 성능 부담 없이 자유롭게 이름을 지을 수 있다.
RELIC_MATERIAL_THEMES = {
    "fire": {
        "display": "화염",
        "relic_keywords": ["불", "화", "화염", "염", "태양", "해", "열", "붉", "적", "용암"],
        "material_keywords": ["불", "태양", "열풍", "핏빛", "붉은", "금빛", "새벽빛", "해질녘", "사막", "전갈"],
        "terrains": ["desert", "demon"],
    },
    "ice": {
        "display": "빙결",
        "relic_keywords": ["얼음", "빙", "서리", "눈", "설", "한기", "극광"],
        "material_keywords": ["얼음", "빙", "서리", "설원", "극광", "영구빙", "냉기"],
        "terrains": ["ice"],
    },
    "wind": {
        "display": "바람",
        "relic_keywords": ["바람", "풍", "폭풍", "하늘", "구름", "날개", "깃"],
        "material_keywords": ["바람", "폭풍", "구름", "날개", "깃", "독수리"],
        "terrains": ["grassland", "mountain", "heaven"],
    },
    "water": {
        "display": "물",
        "relic_keywords": ["물", "바다", "해양", "심해", "파도", "비", "눈물", "청해"],
        "material_keywords": ["물", "심해", "물방울", "조개", "이슬", "축축한", "푸른"],
        "terrains": ["grassland", "cave", "ice"],
    },
    "earth": {
        "display": "대지",
        "relic_keywords": ["땅", "대지", "산", "암석", "돌", "바위", "광석", "철", "금"],
        "material_keywords": ["광석", "결정", "모래", "철", "돌", "수정", "원석", "운철", "산맥"],
        "terrains": ["desert", "cave", "mountain"],
    },
    "nature": {
        "display": "자연",
        "relic_keywords": ["숲", "초원", "풀", "꽃", "나무", "잎", "생명", "녹", "독"],
        "material_keywords": ["약초", "버섯", "꽃", "뿌리", "잎", "나무", "열매", "씨앗", "이끼", "녹빛", "독"],
        "terrains": ["grassland", "jungle"],
    },
    "dark": {
        "display": "암흑",
        "relic_keywords": ["어둠", "암흑", "심연", "악마", "마왕", "저주", "죽음", "검은", "밤"],
        "material_keywords": ["암흑", "심연", "악마", "저주", "검은", "핏빛", "뼈", "응혈"],
        "terrains": ["cave", "demon"],
    },
    "light": {
        "display": "성광",
        "relic_keywords": ["빛", "광명", "성광", "신성", "천사", "신", "별", "찬란", "새벽"],
        "material_keywords": ["빛", "성광", "신성", "천사", "별", "찬란", "새벽빛", "금빛"],
        "terrains": ["heaven"],
    },
    "beast": {
        "display": "야수",
        "relic_keywords": ["용", "늑대", "짐승", "야수", "사냥", "발톱", "송곳니", "뿔", "피"],
        "material_keywords": ["용", "늑대", "짐승", "발톱", "송곳니", "뿔", "가죽", "뼈", "심장", "모피"],
        "terrains": ["jungle", "mountain", "ice", "demon"],
    },
    "machine": {
        "display": "기계",
        "relic_keywords": ["기계", "유적", "철", "장치", "톱니", "매트릭스", "인형"],
        "material_keywords": ["유적", "철편", "기계", "장치", "매트릭스", "드레이크", "파편", "핵"],
        "terrains": ["desert", "cave", "mountain"],
    },
    "magic": {
        "display": "마력",
        "relic_keywords": ["마력", "마법", "정령", "정수", "핵", "결정", "수정", "신비"],
        "material_keywords": ["마력", "정수", "핵", "결정", "수정", "원석", "가루", "진주"],
        "terrains": ["cave", "demon", "heaven"],
    },
}

RELIC_THEME_EFFECTS = {
    "fire": {"main": ("battle", 3.5), "sub": ("loot", 2.0), "desc": "전투와 전리품 획득 강화"},
    "ice": {"main": ("life_save", 3.5), "sub": ("escape", 2.0), "desc": "생존과 도주 강화"},
    "wind": {"main": ("escape", 4.0), "sub": ("luck", 2.0), "desc": "도주와 행운 강화"},
    "water": {"main": ("life_save", 3.0), "sub": ("loot", 2.5), "desc": "생존과 전리품 강화"},
    "earth": {"main": ("battle", 2.8), "sub": ("life_save", 2.5), "desc": "전투와 생존 강화"},
    "nature": {"main": ("loot", 4.0), "sub": ("relic", 0.7), "desc": "전리품과 유물 발견 강화"},
    "dark": {"main": ("battle", 4.0), "sub": ("luck", 2.2), "desc": "전투와 행운 강화"},
    "light": {"main": ("relic", 1.0), "sub": ("life_save", 3.0), "desc": "유물 발견과 생존 강화"},
    "beast": {"main": ("battle", 3.6), "sub": ("escape", 2.0), "desc": "전투와 추적 강화"},
    "machine": {"main": ("loot", 3.2), "sub": ("battle", 2.2), "desc": "전리품 분석과 전투 강화"},
    "magic": {"main": ("relic", 1.2), "sub": ("luck", 2.5), "desc": "유물 발견과 행운 강화"},
}

RELIC_RARITY_EFFECT_MULTIPLIER = {
    "uncommon": 1.00,
    "rare": 1.25,
    "epic": 1.60,
    "legendary": 2.15,
    "mythic": 2.85,
    "transcendent": 4.50,
}

RELIC_EFFECT_LABELS = {
    "battle": "전투 승률",
    "luck": "행운",
    "loot": "전리품",
    "escape": "도주",
    "life_save": "생존",
    "relic": "유물 발견률",
    "max_lives": "최대 목숨",
}

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

# 마계에 한 번이라도 도달한 유저가 선택할 수 있는 하드모드 보정.
# 위험도 상승, 몬스터 레벨, 강적 비율은 높아지고 장비/유물 획득률도 함께 증가한다.
ADVENTURE_HARD_DANGER_MUL = 1.75
ADVENTURE_HARD_MONSTER_LEVEL_MUL = 1.15
ADVENTURE_HARD_MONSTER_LEVEL_FLAT = 2
ADVENTURE_HARD_EQUIPMENT_DROP_MUL = 1.65
ADVENTURE_HARD_RELIC_BONUS = 4.0
ADVENTURE_HARD_ELITE_RATE = 24.0
ADVENTURE_HARD_CALAMITY_RATE = 4.0

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
    "outskirts": {
        "name": "외곽",
        "emoji": "🌌",
        "color": 0x6257A8,
        "description": "천계 바깥의 경계. 네 원소의 신들이 침입자를 시험한다.",
        "danger_mul": 1.82,
        "danger_flat": 55,
        "reward_mul": 3.8,
        # 네 신 중 하나가 해당 모험의 외곽 보스로 선택된다.
        "boss": "땅의 신",
        "bosses": ["불의 신", "물의 신", "바람의 신", "땅의 신"],
        "monsters": ["불의 신", "물의 신", "바람의 신", "땅의 신"],
    },
    "glitch": {
        "name": "!@$*!&",
        "emoji": " ",
        "color": 0x16051F,
        "description": "공간과 글자가 무너진 장소. 이곳에는 대마왕 외에는 아무것도 존재하지 않는다.",
        "danger_mul": 2.0,
        "danger_flat": 70,
        "reward_mul": 4.2,
        "boss": "대마왕",
        "monsters": ["대마왕"],
    },
    "lab17": {
        "name": "17번 연구소",
        "emoji": "🧪",
        "color": 0x263238,
        "description": "세계의 끝에 숨겨진 실험 시설. 모든 모험의 진실이 이곳에 잠들어 있다.",
        "danger_mul": 2.15,
        "danger_flat": 85,
        "reward_mul": 4.8,
        "boss": "각성한 매드 사이언티스트",
        "monsters": [
            "시설 가드", "기동특수부대원", "알파 부대원", "알파 부대장",
            "저거너트", "대마왕", "39번 실험체", "1번 실험체",
            "각성한 매드 사이언티스트",
        ],
    },
}

# 이동 가능한 방향. 천계 이후의 최종장 지형은 랜덤/유물 갈림길로 진입할 수 없고,
# 오직 현재 지형의 보스를 쓰러뜨렸을 때만 아래 순서대로 이동한다.
ADVENTURE_TERRAIN_ROUTES = {
    "desert": ["grassland", "jungle", "cave"],
    "grassland": ["desert", "jungle", "cave", "mountain"],
    "jungle": ["desert", "grassland", "cave", "mountain"],
    "cave": ["desert", "jungle", "mountain", "ice"],
    "mountain": ["grassland", "cave", "ice", "demon"],
    "ice": ["cave", "mountain", "demon"],
    "demon": ["mountain", "ice", "heaven"],
    "heaven": ["outskirts"],
    "outskirts": ["glitch"],
    "glitch": ["lab17"],
    "lab17": [],
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
    "outskirts": 7,
    "glitch": 8,
    "lab17": 9,
}

# 기존 120종 유물/월드 재료의 지형 배치를 유지하기 위한 목록이다.
# 새 최종장 지형을 여기에 넣으면 기존 유물 ID의 출현 지형이 전부 바뀌므로 추가하지 않는다.
ADVENTURE_LOOT_TERRAINS = [
    "desert", "grassland", "jungle", "cave", "mountain", "ice", "demon", "heaven"
]

ADVENTURE_STORY_LOCKED_TERRAINS = {"heaven", "outskirts", "glitch", "lab17"}
ADVENTURE_FORCED_TERRAINS = {"glitch", "lab17"}

# 엔딩 보상 설정. ID가 0이면 같은 이름의 역할을 찾고, 없으면 새로 생성한다.
ADVENTURE_ENDING_CHANNEL_ID = 1523946840310157323
ADVENTURE_ENDING_ROLE_ID = 0
ADVENTURE_ENDING_ROLE_NAME = "THE END"

# 지정 몬스터 전용 장비. 일반 장비 드롭에서는 제외되며
# 아래 몬스터를 직접 쓰러뜨렸을 때만 각 확률로 획득할 수 있다.
ADVENTURE_RESTRICTED_WEAPONS = {
    "P90", "AK12", "MINIGUN",
    "홍련의 신검", "폭풍의 신검", "종말의 마검",
}
ADVENTURE_EXCLUSIVE_EQUIPMENT_DROPS = {
    # 17번 연구소
    "기동특수부대원": [("weapon", "P90", 18.0)],
    "알파 부대원": [("weapon", "AK12", 14.0)],
    "알파 부대장": [("weapon", "AK12", 30.0)],
    "저거너트": [("weapon", "MINIGUN", 20.0)],

    # 외곽의 네 신
    "불의 신": [("weapon", "홍련의 신검", 10.0)],
    "물의 신": [("armor", "심해신의 예복", 10.0)],
    "바람의 신": [("weapon", "폭풍의 신검", 10.0)],
    "땅의 신": [("armor", "대지신의 갑주", 10.0)],

    # !@$*!&
    "대마왕": [("weapon", "종말의 마검", 6.0)],
}

ADVENTURE_STORY_PHASES = {
    "glitch_demon_king": {
        "monster": "대마왕",
        "level_mul": 3.0,
        "level_flat": 150,
        "escape": True,
    },
    "lab_guard": {
        "monster": "시설 가드",
        "level_mul": 3.5,
        "level_flat": 175,
        "escape": False,
    },
    "lab_mtf": {
        "monster": "기동특수부대원",
        "level_mul": 4.2,
        "level_flat": 230,
        "escape": False,
    },
    "lab_alpha": {
        "monster": "알파 부대원",
        "level_mul": 5.2,
        "level_flat": 280,
        "escape": False,
    },
    "lab_alpha_leader": {
        "monster": "알파 부대장",
        "level_mul": 6.5,
        "level_flat": 330,
        "escape": False,
    },
    "lab_juggernaut": {
        "monster": "저거너트",
        "level_mul": 8.3,
        "level_flat": 400,
        "escape": False,
    },
    "experiment_19": {
        "monster": "대마왕",
        "level_mul": 10.8,
        "level_flat": 450,
        "escape": False,
    },
    "experiment_39": {
        "monster": "39번 실험체",
        "level_mul": 14.0,
        "level_flat": 500,
        "escape": False,
    },
    "experiment_1": {
        "monster": "1번 실험체",
        "level_mul": 18.0,
        "level_flat": 700,
        "escape": False,
    },
    "mad_scientist_final": {
        "monster": "각성한 매드 사이언티스트",
        "level_mul": 23.0,
        "level_flat": 950,
        "escape": False,
    },
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
        # 최종장 지형은 반드시 바로 이전 스테이지의 보스 진행으로만 연결된다.
        if destination == "outskirts" and source != "heaven":
            continue
        if destination == "glitch" and source != "outskirts":
            continue
        if destination == "lab17" and source != "glitch":
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
    "transcendent": {"name": "초월", "emoji": "🌌", "value_mul": 100.0},
}

ADVENTURE_RARITY_ORDER = {
    "common": 0,
    "uncommon": 1,
    "rare": 2,
    "epic": 3,
    "legendary": 4,
    "mythic": 5,
    "transcendent": 6,
}

ADVENTURE_DROP_WEIGHTS = {
    "common": 70,
    "uncommon": 35,
    "rare": 13,
    "epic": 4,
    "legendary": 0.8,
    "mythic": 0.12,
    # 초월 유물은 이 가중치로 뽑지 않는다.
    # pick_mystery_relic()에서 정확히 0.00015%로 별도 판정한다.
    "transcendent": 0.00015,
}

ADVENTURE_RELIC_TOTAL_COUNT = 1000
ADVENTURE_RELIC_RARITY_COUNTS = {
    "uncommon": 665,
    "rare": 230,
    "epic": 86,
    "legendary": 15,
    "mythic": 3,
    "transcendent": 1,
}

# 퍼센트 단위다. 0.00015% = 약 666,667번에 1번.
ADVENTURE_TRANSCENDENT_RELIC_CHANCE_PERCENT = 0.00015
ADVENTURE_TRANSCENDENT_SOFT_PITY_START = 2_000
ADVENTURE_TRANSCENDENT_HARD_PITY = 10_000
ADVENTURE_TRANSCENDENT_SOFT_PITY_PER_100 = 0.002
TRANSCENDENT_SYNTHESIS_COST = 1_000_000


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

# 포션은 영구 장착 아이템과 달리 여러 개 구매해 두었다가 모험 중에 소비한다.
ADVENTURE_POTION_CATALOG = {
    "체력의 포션": {
        "price": 2200,
        "desc": "모험 중 사용하면 목숨을 1 회복한다. 모험당 최대 2회 사용 가능.",
    },
    "힘의 포션": {
        "price": 3500,
        "desc": "이번 모험 동안 전투 승률이 10% 증가한다. 모험당 1회 사용 가능.",
    },
    "운의 포션": {
        "price": 4000,
        "desc": "이번 모험 동안 행운/전리품 효과가 12%, 유물 발견률이 3%p 증가한다. 모험당 1회 사용 가능.",
    },
}

# 요리는 정확히 3개의 전리품을 조합한다.
# 아래 150종은 자동 생성하지 않고, 레시피와 버프를 전부 코드에 직접 고정해 둔다.
# 음식 이름은 서버 최초 발견자가 정하며, 재료를 넣는 순서는 판정에 영향을 주지 않는다.
ADVENTURE_COOKING_PAGE_SIZE = 25
ADVENTURE_COOKING_RECIPE_TOTAL = 500

def adventure_monster_item(monster_index, part_index):
    return f"monster_{monster_index:03d}_{part_index:02d}"

def adventure_world_item(prefix_index, material_index):
    return f"world_{prefix_index:02d}_{material_index:02d}"

def adventure_terrain_item(terrain_index, material_index):
    return f"terrain_{terrain_index:02d}_{material_index:02d}"

ADVENTURE_COOKING_RECIPES = {}
_ADVENTURE_COOKING_USED_KEYS = set()

def normalize(ingredient_ids):
    return tuple(sorted(str(item_id) for item_id in ingredient_ids))

def _register_adventure_cooking_recipe(ingredients, effects, concept):
    key = normalize(ingredients)
    if len(key) != 3 or len(set(key)) != 3:
        return False
    if key in _ADVENTURE_COOKING_USED_KEYS:
        return False
    recipe_id = f"dish_{len(ADVENTURE_COOKING_RECIPES) + 1:03d}"
    ADVENTURE_COOKING_RECIPES[recipe_id] = {
        "ingredients": list(ingredients),
        "effects": dict(effects),
        "concept": str(concept),
    }
    _ADVENTURE_COOKING_USED_KEYS.add(key)
    return True

# first recipes
_register_adventure_cooking_recipe(
    [adventure_terrain_item(1,5), adventure_terrain_item(1,1), adventure_monster_item(0,0)],
    {"heal":1, "life_save":6},
    "초원 젤리죽",
)
_register_adventure_cooking_recipe(
    [adventure_world_item(0,0), adventure_terrain_item(1,5), adventure_monster_item(1,0)],
    {"battle":6, "loot":4},
    "새벽 야전죽",
)
_register_adventure_cooking_recipe(
    [adventure_terrain_item(0,0), adventure_terrain_item(0,3), adventure_world_item(0,9)],
    {"luck":8, "loot":6},
    "선인장 장미차",
)

ADVENTURE_COOKING_CURATED_BLUEPRINTS = [
    ([adventure_terrain_item(0,0), adventure_world_item(1,9), adventure_monster_item(3,1)], {"escape":8,"loot":5}, "사막 도적 스튜"),
    ([adventure_terrain_item(2,0), adventure_world_item(2,1), adventure_monster_item(10,4)], {"battle":10,"life_save":5}, "밀림 맹수버섯구이"),
    ([adventure_terrain_item(3,2), adventure_world_item(6,5), adventure_monster_item(6,2)], {"relic":1.8,"loot":6}, "동굴 이끼 코어탕"),
    ([adventure_terrain_item(4,1), adventure_world_item(0,3), adventure_monster_item(9,3)], {"battle":9,"luck":5}, "고산 검귀 약초탕"),
    ([adventure_terrain_item(5,1), adventure_world_item(4,9), adventure_monster_item(21,0)], {"escape":10,"life_save":6}, "서리꽃 늑대차"),
    ([adventure_terrain_item(6,4), adventure_world_item(3,5), adventure_monster_item(12,3)], {"battle":11,"relic":2.2}, "검은 불씨 심연찜"),
    ([adventure_terrain_item(7,4), adventure_world_item(5,2), adventure_monster_item(25,3)], {"max_lives":1,"heal":1,"life_save":9}, "신성한 이슬 성광정식"),
    ([adventure_world_item(2,0), adventure_world_item(2,1), adventure_terrain_item(1,5)], {"heal":1,"luck":4}, "푸른 약초버섯죽"),
    ([adventure_world_item(3,4), adventure_world_item(3,5), adventure_monster_item(15,2)], {"battle":8,"loot":8}, "붉은 태엽 코어구이"),
    ([adventure_world_item(4,10), adventure_terrain_item(5,0), adventure_monster_item(14,0)], {"escape":12,"loot":4}, "은빛 조개 냉탕"),
    ([adventure_world_item(5,0), adventure_terrain_item(4,5), adventure_monster_item(17,1)], {"battle":10,"relic":2.0}, "금빛 드레이크 구름탕"),
    ([adventure_world_item(6,2), adventure_terrain_item(7,3), adventure_monster_item(23,3)], {"luck":12,"loot":5}, "고요한 별가루 차"),
    ([adventure_world_item(7,7), adventure_terrain_item(4,0), adventure_monster_item(24,3)], {"battle":13,"escape":5}, "울부짖는 깃 번개구이"),
    ([adventure_world_item(8,6), adventure_terrain_item(0,5), adventure_monster_item(18,2)], {"relic":2.4,"luck":6}, "메마른 열풍 코어과자"),
    ([adventure_world_item(9,9), adventure_terrain_item(2,3), adventure_monster_item(19,0)], {"life_save":10,"escape":7}, "축축한 밀림 생존식"),
    ([adventure_world_item(10,2), adventure_terrain_item(7,2), adventure_monster_item(29,3)], {"loot":11,"luck":7}, "별무늬 구름비단 무침"),
    ([adventure_world_item(11,10), adventure_terrain_item(6,5), adventure_monster_item(26,4)], {"battle":18,"life_save":8}, "심해 조개 마왕구이"),
]
for ingredients, effects, concept in ADVENTURE_COOKING_CURATED_BLUEPRINTS:
    _register_adventure_cooking_recipe(ingredients, effects, concept)

ADVENTURE_COOKING_MONSTER_IDS = [
    adventure_monster_item(monster_index, part_index)
    for monster_index in range(40)
    for part_index in range(6)
]
ADVENTURE_COOKING_WORLD_IDS = [
    adventure_world_item(prefix_index, material_index)
    for prefix_index in range(12)
    for material_index in range(12)
]
ADVENTURE_COOKING_TERRAIN_IDS = [
    adventure_terrain_item(terrain_index, material_index)
    for terrain_index in range(8)
    for material_index in range(6)
]
ADVENTURE_COOKING_ALL_INGREDIENT_IDS = (
    ADVENTURE_COOKING_MONSTER_IDS
    + ADVENTURE_COOKING_WORLD_IDS
    + ADVENTURE_COOKING_TERRAIN_IDS
)

ADVENTURE_COOKING_EDIBLE_BASES = [
    adventure_terrain_item(1,5), adventure_terrain_item(1,1), adventure_terrain_item(2,3),
    adventure_world_item(0,0), adventure_world_item(1,1), adventure_world_item(2,2),
    adventure_world_item(3,3), adventure_world_item(4,9), adventure_world_item(5,10),
]
ADVENTURE_COOKING_SPICES = [
    adventure_terrain_item(0,3), adventure_terrain_item(2,2), adventure_terrain_item(4,1),
    adventure_terrain_item(5,1), adventure_terrain_item(6,4), adventure_terrain_item(7,4),
    adventure_world_item(6,2), adventure_world_item(7,0), adventure_world_item(8,5),
    adventure_world_item(9,9), adventure_world_item(10,2), adventure_world_item(11,5),
]
ADVENTURE_COOKING_BINDERS = [
    adventure_world_item(0,9), adventure_world_item(1,6), adventure_world_item(2,10),
    adventure_world_item(3,11), adventure_terrain_item(0,1), adventure_terrain_item(3,4),
    adventure_terrain_item(5,0), adventure_terrain_item(7,2),
]
ADVENTURE_COOKING_ARCANE_ITEMS = [
    adventure_terrain_item(3,1), adventure_terrain_item(3,5), adventure_terrain_item(4,2),
    adventure_terrain_item(4,3), adventure_terrain_item(5,2), adventure_terrain_item(5,5),
    adventure_terrain_item(6,0), adventure_terrain_item(6,3), adventure_terrain_item(7,1),
    adventure_terrain_item(7,5), adventure_world_item(4,4), adventure_world_item(5,5),
]

ADVENTURE_COOKING_EFFECT_PATTERNS = [
    {"battle": 6, "loot": 4},
    {"heal": 1, "life_save": 6},
    {"luck": 8, "loot": 6},
    {"escape": 10, "luck": 4},
    {"life_save": 8, "battle": 4},
    {"relic": 1.6, "loot": 5},
    {"battle": 8, "escape": 5},
    {"loot": 9, "luck": 4},
    {"battle": 5, "life_save": 7},
    {"relic": 2.0, "luck": 5},
]
ADVENTURE_COOKING_ADVANCED_EFFECT_PATTERNS = [
    {"battle": 12, "loot": 8},
    {"battle": 10, "luck": 8},
    {"loot": 12, "escape": 8},
    {"life_save": 13, "battle": 6},
    {"relic": 3.0, "luck": 7},
    {"heal": 1, "loot": 7, "luck": 4},
    {"battle": 9, "loot": 9, "luck": 4},
    {"escape": 13, "relic": 2.7},
    {"max_lives": 1, "heal": 1, "life_save": 10},
]
ADVENTURE_COOKING_CONCEPT_WORDS = [
    "야전죽", "향신 스튜", "젤리탕", "버섯구이", "결정찜",
    "약초차", "전투 도시락", "탐험 수프", "마력 조림", "생존 정식",
    "보물 사냥 볶음", "유물 탐색식", "심연 전골", "천계 디저트", "폭풍 꼬치",
]

def _adventure_cooking_effect_for_index(index, item_id):
    advanced = False
    if item_id.startswith("monster_"):
        try:
            monster_index = int(item_id.split("_")[1])
            part_index = int(item_id.split("_")[2])
            advanced = monster_index >= 20 or part_index >= 3
        except Exception:
            advanced = False
    elif item_id.startswith("terrain_"):
        try:
            terrain_index = int(item_id.split("_")[1])
            material_index = int(item_id.split("_")[2])
            advanced = terrain_index >= 5 or material_index >= 4
        except Exception:
            advanced = False
    elif item_id.startswith("world_"):
        try:
            prefix_index = int(item_id.split("_")[1])
            material_index = int(item_id.split("_")[2])
            advanced = prefix_index >= 8 or material_index >= 8
        except Exception:
            advanced = False

    patterns = ADVENTURE_COOKING_ADVANCED_EFFECT_PATTERNS if advanced else ADVENTURE_COOKING_EFFECT_PATTERNS
    return patterns[index % len(patterns)]

def _adventure_cooking_concept_for_index(index, item_id):
    if item_id.startswith("monster_"):
        family = "몬스터"
    elif item_id.startswith("terrain_"):
        family = "지역"
    else:
        family = "월드"
    return f"{family} {ADVENTURE_COOKING_CONCEPT_WORDS[index % len(ADVENTURE_COOKING_CONCEPT_WORDS)]}"

def _register_adventure_cooking_recipe_for_item(index, item_id):
    if item_id.startswith("monster_"):
        ingredients = [
            item_id,
            ADVENTURE_COOKING_EDIBLE_BASES[index % len(ADVENTURE_COOKING_EDIBLE_BASES)],
            ADVENTURE_COOKING_SPICES[(index * 3 + 1) % len(ADVENTURE_COOKING_SPICES)],
        ]
    elif item_id.startswith("world_"):
        ingredients = [
            item_id,
            ADVENTURE_COOKING_MONSTER_IDS[(index * 5 + 7) % len(ADVENTURE_COOKING_MONSTER_IDS)],
            ADVENTURE_COOKING_BINDERS[(index * 2 + 3) % len(ADVENTURE_COOKING_BINDERS)],
        ]
    else:
        ingredients = [
            item_id,
            ADVENTURE_COOKING_MONSTER_IDS[(index * 7 + 11) % len(ADVENTURE_COOKING_MONSTER_IDS)],
            ADVENTURE_COOKING_WORLD_IDS[(index * 11 + 13) % len(ADVENTURE_COOKING_WORLD_IDS)],
        ]

    return _register_adventure_cooking_recipe(
        ingredients,
        _adventure_cooking_effect_for_index(index, item_id),
        _adventure_cooking_concept_for_index(index, item_id),
    )

for index, item_id in enumerate(ADVENTURE_COOKING_ALL_INGREDIENT_IDS):
    _register_adventure_cooking_recipe_for_item(index, item_id)

fill_index = 0
while len(ADVENTURE_COOKING_RECIPES) < ADVENTURE_COOKING_RECIPE_TOTAL:
    monster = ADVENTURE_COOKING_MONSTER_IDS[(fill_index * 13 + 5) % len(ADVENTURE_COOKING_MONSTER_IDS)]
    world = ADVENTURE_COOKING_WORLD_IDS[(fill_index * 17 + 9) % len(ADVENTURE_COOKING_WORLD_IDS)]
    terrain = ADVENTURE_COOKING_TERRAIN_IDS[(fill_index * 19 + 2) % len(ADVENTURE_COOKING_TERRAIN_IDS)]
    effects = ADVENTURE_COOKING_ADVANCED_EFFECT_PATTERNS[fill_index % len(ADVENTURE_COOKING_ADVANCED_EFFECT_PATTERNS)]
    concept = f"혼합 {ADVENTURE_COOKING_CONCEPT_WORDS[fill_index % len(ADVENTURE_COOKING_CONCEPT_WORDS)]}"
    _register_adventure_cooking_recipe([monster, world, terrain], effects, concept)
    fill_index += 1
    if fill_index > 10000:
        raise RuntimeError("요리 레시피 500개를 채우지 못했어.")

if len(ADVENTURE_COOKING_RECIPES) != ADVENTURE_COOKING_RECIPE_TOTAL:
    raise RuntimeError(f"요리 레시피 수 오류: {len(ADVENTURE_COOKING_RECIPES)}/{ADVENTURE_COOKING_RECIPE_TOTAL}종")


ADVENTURE_COOKING_RECIPE_KEYS = [
    normalize(recipe["ingredients"])
    for recipe in ADVENTURE_COOKING_RECIPES.values()
]
if len(set(ADVENTURE_COOKING_RECIPE_KEYS)) != len(ADVENTURE_COOKING_RECIPE_KEYS):
    raise RuntimeError("서로 같은 재료 구성의 요리 레시피가 중복되어 있어.")

# 임시 생성용 변수는 전역에 남겨도 작동에는 문제 없지만, 지저분하면 지워도 된다.
try:
    del _ADVENTURE_COOKING_USED_KEYS
except NameError:
    pass

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
        "pending_food_recipe_id": None,
        "cooked_recipe_ids": [],
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
        "hard_mode_unlocked": False,
        "hard_mode": False,
        "health_potion_uses": 0,
        "strength_potion_used": False,
        "luck_potion_used": False,

        # 천계 이후 최종장 진행 및 엔딩 기록
        "story_phase": None,
        "lab_defeated": [],
        "ending_cleared": False,
        "ending_clear_count": 0,

        # /사냥과 완전히 분리된 모험 전용 성장 데이터
        "level": 1,
        "exp": 0,
        "weapon": "무인검",
        "armor": "모험가 세트",
        "owned_weapons": ["무인검"],
        "owned_armors": ["모험가 세트"],
        "equipped_relics": [],

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
    adventure["health_potion_uses"] = max(0, min(2, int(adventure.get("health_potion_uses", 0))))
    adventure["strength_potion_used"] = bool(adventure.get("strength_potion_used", False))
    adventure["luck_potion_used"] = bool(adventure.get("luck_potion_used", False))
    if not isinstance(adventure.get("cooked_recipe_ids"), list):
        adventure["cooked_recipe_ids"] = []
    adventure["cooked_recipe_ids"] = [
        recipe_id for recipe_id in adventure["cooked_recipe_ids"]
        if recipe_id in ADVENTURE_COOKING_RECIPES
    ]
    if adventure.get("pending_food_recipe_id") not in ADVENTURE_COOKING_RECIPES:
        adventure["pending_food_recipe_id"] = None
    if not isinstance(adventure.get("lab_defeated"), list):
        adventure["lab_defeated"] = []
    adventure["ending_cleared"] = bool(adventure.get("ending_cleared", False))
    adventure["ending_clear_count"] = max(0, int(adventure.get("ending_clear_count", 0)))
    if not isinstance(adventure.get("equipped_relics"), list):
        adventure["equipped_relics"] = []
    owned_inventory = inventories.get(str(uid), {}) if isinstance(inventories.get(str(uid), {}), dict) else {}
    adventure["equipped_relics"] = list(dict.fromkeys(
        item_id for item_id in adventure.get("equipped_relics", [])
        if item_id in ADVENTURE_ITEM_CATALOG
        and ADVENTURE_ITEM_CATALOG[item_id].get("kind") == "relic"
        and int(owned_inventory.get(item_id, 0)) > 0
    ))[:RELIC_MAX_EQUIPPED]

    # 기존 유저도 과거 최고 도달 지형 기록이나 현재 이동 기록에 마계가 있으면 자동 해금한다.
    if (
        int(adventure.get("best_terrain_rank", 0)) >= ADVENTURE_TERRAIN_DEPTH["demon"]
        or "demon" in adventure.get("visited_terrains", [])
    ):
        adventure["hard_mode_unlocked"] = True

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
            "potions": {},
        }

    info = shop_items[uid]
    info.setdefault("owned", [])
    info.setdefault("equipped", [])
    info.setdefault("potions", {})

    # 예전 형식이나 잘못된 데이터가 있어도 복구
    if not isinstance(info["owned"], list):
        info["owned"] = list(info["owned"])
    if not isinstance(info["equipped"], list):
        info["equipped"] = list(info["equipped"])
    if not isinstance(info["potions"], dict):
        info["potions"] = {}

    info["owned"] = [name for name in info["owned"] if name in ADVENTURE_SHOP_CATALOG]
    info["equipped"] = [
        name
        for name in info["equipped"]
        if name in info["owned"] and name in ADVENTURE_SHOP_CATALOG
    ][:ADVENTURE_MAX_EQUIPPED]
    info["potions"] = {
        name: max(0, int(amount))
        for name, amount in info["potions"].items()
        if name in ADVENTURE_POTION_CATALOG and int(amount) > 0
    }

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

    relic_boosts = get_equipped_relic_boosts(uid)
    for key in boosts:
        boosts[key] += relic_boosts.get(key, 0)

    boosts["max_lives"] = int(boosts.get("max_lives", 0))
    return boosts


def get_adventure_shop_item_effect_text(item_name):
    item = ADVENTURE_SHOP_CATALOG.get(item_name, {})
    labels = {
        "battle": "전투",
        "luck": "행운",
        "loot": "전리품",
        "escape": "도주",
        "life_save": "생존",
        "relic": "유물",
        "max_lives": "최대 목숨",
    }

    parts = []
    for key in ["battle", "luck", "loot", "escape", "life_save", "relic", "max_lives"]:
        value = item.get(key, 0)
        if not value:
            continue
        if key == "max_lives":
            parts.append(f"{labels[key]} +{int(value)}")
        elif key == "relic":
            parts.append(f"{labels[key]} +{value:g}%p")
        else:
            parts.append(f"{labels[key]} +{value:g}%")

    return " · ".join(parts) if parts else "효과 없음"


def get_adventure_shop_equipment_text(uid):
    info = get_adventure_shop_user(uid)
    equipped = [name for name in info.get("equipped", []) if name in ADVENTURE_SHOP_CATALOG]

    if not equipped:
        return "장착 중인 모험상점 장비 없음"

    return "\n".join(
        f"✅ **{name}** — {get_adventure_shop_item_effect_text(name)}"
        for name in equipped
    )


def get_adventure_shop_boost_summary_text(uid):
    boosts = get_equipped_adventure_boosts(uid)
    parts = []

    if boosts.get("battle"):
        parts.append(f"전투 +{boosts['battle']:g}%")
    if boosts.get("luck"):
        parts.append(f"행운 +{boosts['luck']:g}%")
    if boosts.get("loot"):
        parts.append(f"전리품 +{boosts['loot']:g}%")
    if boosts.get("escape"):
        parts.append(f"도주 +{boosts['escape']:g}%")
    if boosts.get("life_save"):
        parts.append(f"생존 +{boosts['life_save']:g}%")
    if boosts.get("relic"):
        parts.append(f"유물 +{boosts['relic']:g}%p")
    if boosts.get("max_lives"):
        parts.append(f"최대 목숨 +{int(boosts['max_lives'])}")

    return " · ".join(parts) if parts else "효과 없음"



def get_adventure_required_exp(level):
    """모험 전용 레벨 요구 경험치. /사냥 레벨과는 전혀 공유하지 않는다."""
    return get_required_exp(max(1, int(level)))


def give_adventure_exp(adventure, amount):
    amount = apply_fever_multiplier(amount)
    adventure["exp"] = max(0, int(adventure.get("exp", 0)) + amount)
    leveled = 0

    while adventure["exp"] >= get_adventure_required_exp(adventure["level"]):
        adventure["exp"] -= get_adventure_required_exp(adventure["level"])
        adventure["level"] += 1
        leveled += 1

    return leveled, amount


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
    if terrain_key in ADVENTURE_FORCED_TERRAINS:
        return 0.0
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
    if adventure.get("hard_mode"):
        drop_rate *= ADVENTURE_HARD_EQUIPMENT_DROP_MUL
    if random.random() * 100 >= min(100.0, drop_rate):
        return None

    owned_weapons = set(adventure.get("owned_weapons", []))
    owned_armors = set(adventure.get("owned_armors", []))
    depth = ADVENTURE_TERRAIN_DEPTH.get(adventure.get("terrain"), 0)
    player_level = max(1, int(adventure.get("level", 1)))
    allowed_bonus = 5 + player_level * 0.8 + depth * 3.5 + adventure.get("terrain_steps", 0) * 0.35

    weapon_candidates = [
        name for name, info in WEAPONS.items()
        if (
            name != "무인검"
            and name not in ADVENTURE_RESTRICTED_WEAPONS
            and not info.get("obtain_only")
            and name not in owned_weapons
            and info.get("bonus", 0) <= allowed_bonus
        )
    ]
    armor_candidates = [
        name for name, info in ARMORS.items()
        if (
            name != "모험가 세트"
            and not info.get("obtain_only")
            and name not in owned_armors
            and info.get("bonus", 0) <= allowed_bonus
        )
    ]

    if not weapon_candidates and not armor_candidates:
        weapon_candidates = [
            name for name, info in WEAPONS.items()
            if (
                name != "무인검"
                and name not in ADVENTURE_RESTRICTED_WEAPONS
                and not info.get("obtain_only")
                and name not in owned_weapons
            )
        ]
        armor_candidates = [
            name for name, info in ARMORS.items()
            if name != "모험가 세트" and not info.get("obtain_only") and name not in owned_armors
        ]

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


def build_adventure_relic_rarity_map():
    """
    유물 1~120번은 기존 등급을 그대로 유지하고,
    121~1000번만 추가 배치하여 기존 보유 유물의 등급이 바뀌지 않게 한다.
    """
    rarity_map = {}

    # 기존 120종의 등급 배치를 그대로 보존한다.
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
        rarity_map[relic_number] = rarity

    # 기존 신화 1개/전설 4개를 유지한 채 목표 개수까지 추가한다.
    for relic_number in {499, 997}:
        rarity_map[relic_number] = "mythic"

    for relic_number in {
        174, 232, 290, 348, 406, 464,
        522, 580, 638, 696, 754,
    }:
        rarity_map[relic_number] = "legendary"

    # 1000번은 단 하나뿐인 초월 유물이다.
    rarity_map[1000] = "transcendent"

    available_numbers = [
        relic_number
        for relic_number in range(121, 1000)
        if relic_number not in rarity_map
    ]

    # 새 일반/희귀/영웅 유물은 고정 시드로 섞어 서버 재시작 후에도 등급이 유지된다.
    rng = random.Random(20260707)
    rng.shuffle(available_numbers)

    current_counts = {
        rarity: list(rarity_map.values()).count(rarity)
        for rarity in ADVENTURE_RELIC_RARITY_COUNTS
    }
    epic_needed = ADVENTURE_RELIC_RARITY_COUNTS["epic"] - current_counts["epic"]
    rare_needed = ADVENTURE_RELIC_RARITY_COUNTS["rare"] - current_counts["rare"]
    uncommon_needed = ADVENTURE_RELIC_RARITY_COUNTS["uncommon"] - current_counts["uncommon"]

    expected_remaining = epic_needed + rare_needed + uncommon_needed
    if expected_remaining != len(available_numbers):
        raise RuntimeError(
            f"유물 등급 배치 수가 맞지 않음: 필요 {expected_remaining}, 남은 ID {len(available_numbers)}"
        )

    cursor = 0
    for relic_number in available_numbers[cursor:cursor + epic_needed]:
        rarity_map[relic_number] = "epic"
    cursor += epic_needed

    for relic_number in available_numbers[cursor:cursor + rare_needed]:
        rarity_map[relic_number] = "rare"
    cursor += rare_needed

    for relic_number in available_numbers[cursor:cursor + uncommon_needed]:
        rarity_map[relic_number] = "uncommon"

    actual_counts = {
        rarity: list(rarity_map.values()).count(rarity)
        for rarity in ADVENTURE_RELIC_RARITY_COUNTS
    }
    if len(rarity_map) != ADVENTURE_RELIC_TOTAL_COUNT:
        raise RuntimeError(
            f"유물 총 개수 오류: {len(rarity_map)} / {ADVENTURE_RELIC_TOTAL_COUNT}"
        )
    if actual_counts != ADVENTURE_RELIC_RARITY_COUNTS:
        raise RuntimeError(
            f"유물 등급 개수 오류: {actual_counts}"
        )

    return rarity_map


ADVENTURE_RELIC_RARITY_MAP = build_adventure_relic_rarity_map()


def build_adventure_item_catalog():
    """몬스터 전리품, 월드 재료, 이름을 붙이는 유물 1000종을 만든다."""
    catalog = {}
    terrain_keys = list(ADVENTURE_LOOT_TERRAINS)

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

    # 이름을 최초 발견자가 붙이는 유물 1000종
    for relic_number in range(1, ADVENTURE_RELIC_TOTAL_COUNT + 1):
        rarity = ADVENTURE_RELIC_RARITY_MAP[relic_number]

        # :03d는 1~999번의 기존 ID 형식을 보존하고, 1000번은 relic_1000이 된다.
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


# 정렬된 튜플은 순서만 없애고 같은 재료의 개수는 그대로 보존한다.
# 예: A+B+C, C+A+B, B+C+A는 모두 같은 구성으로 판정된다.
def normalize_adventure_cooking_ingredients(ingredient_ids):
    return tuple(sorted(str(item_id) for item_id in ingredient_ids))


ADVENTURE_COOKING_RECIPE_LOOKUP = {
    normalize_adventure_cooking_ingredients(recipe["ingredients"]): recipe_id
    for recipe_id, recipe in ADVENTURE_COOKING_RECIPES.items()
}


def get_discovered_food_name(recipe_id):
    info = discovered_foods.get(recipe_id, {})
    if info.get("name"):
        return str(info["name"])

    recipe = ADVENTURE_COOKING_RECIPES.get(recipe_id, {})
    return str(recipe.get("concept") or "이름 없는 요리")


def get_adventure_food_effect_text(recipe_id):
    recipe = ADVENTURE_COOKING_RECIPES.get(recipe_id, {})
    effects = recipe.get("effects", {})
    labels = {
        "battle": "전투",
        "luck": "행운",
        "loot": "전리품",
        "escape": "도주",
        "life_save": "생존",
        "relic": "유물 발견률",
    }
    parts = []
    for key, label in labels.items():
        value = effects.get(key, 0)
        if value:
            suffix = "%p" if key == "relic" else "%"
            parts.append(f"{label} +{value:g}{suffix}")
    if effects.get("max_lives"):
        parts.append(f"최대 목숨 +{int(effects['max_lives'])}")
    if effects.get("heal"):
        parts.append(f"목숨 회복 +{int(effects['heal'])}")
    return ", ".join(parts) if parts else "효과 없음"


def get_adventure_cooking_entries(uid):
    inventory = get_adventure_inventory(uid)
    entries = []
    for item_id, amount in inventory.items():
        item = ADVENTURE_ITEM_CATALOG.get(item_id)
        amount = int(amount)
        if not item or amount <= 0 or item.get("kind") == "relic":
            continue
        entries.append((item_id, amount))

    entries.sort(
        key=lambda pair: (
            -ADVENTURE_RARITY_ORDER.get(ADVENTURE_ITEM_CATALOG[pair[0]]["rarity"], 0),
            get_adventure_item_name(pair[0]),
        )
    )
    return entries


def apply_adventure_food_effect(adventure, recipe_id):
    recipe = ADVENTURE_COOKING_RECIPES[recipe_id]
    effects = recipe.get("effects", {})
    boosts = adventure.setdefault("boosts", {})

    max_lives_gain = max(0, int(effects.get("max_lives", 0)))
    if max_lives_gain:
        adventure["max_lives"] = max(3, int(adventure.get("max_lives", 3))) + max_lives_gain

    healed = 0
    heal_amount = max(0, int(effects.get("heal", 0)))
    if heal_amount:
        before = int(adventure.get("lives", 0))
        adventure["lives"] = min(int(adventure.get("max_lives", 3)), before + heal_amount)
        healed = adventure["lives"] - before

    for key in ("battle", "luck", "loot", "escape", "life_save", "relic"):
        value = effects.get(key, 0)
        if value:
            boosts[key] = boosts.get(key, 0) + value

    return healed


def cook_adventure_food(uid, selected_item_ids, member):
    uid = str(uid)
    adventure = get_adventure(uid)
    inventory = get_adventure_inventory(uid)

    if not adventure.get("active"):
        return False, "❌ 현재 진행 중인 모험이 없어.", None, False

    if len(selected_item_ids) != 3 or any(not item_id for item_id in selected_item_ids):
        return False, "❌ 세 칸에 재료를 전부 넣어야 해.", None, False

    required = {}
    for item_id in selected_item_ids:
        item = ADVENTURE_ITEM_CATALOG.get(item_id)
        if not item or item.get("kind") == "relic":
            return False, "❌ 유물이나 존재하지 않는 물건은 요리 재료로 쓸 수 없어.", None, False
        required[item_id] = required.get(item_id, 0) + 1

    for item_id, amount in required.items():
        if int(inventory.get(item_id, 0)) < amount:
            return False, f"❌ **{get_adventure_item_name(item_id)}** 수량이 부족해.", None, False

    recipe_key = normalize_adventure_cooking_ingredients(selected_item_ids)
    recipe_id = ADVENTURE_COOKING_RECIPE_LOOKUP.get(recipe_key)

    # 이미 이번 모험에서 먹은 완성 요리는 조리 자체를 막고 재료도 건드리지 않는다.
    # 틀린 조합은 실제 조리 실패로 처리하여 아래에서 재료를 전부 소모한다.
    used = adventure.setdefault("cooked_recipe_ids", [])
    if recipe_id and recipe_id in used:
        return False, "❌ 같은 레시피의 버프는 한 모험에서 한 번만 받을 수 있어.", recipe_id, False

    for item_id, amount in required.items():
        inventory[item_id] = int(inventory.get(item_id, 0)) - amount
        if inventory[item_id] <= 0:
            inventory.pop(item_id, None)

    if not recipe_id:
        save_data()
        return False, (
            "🔥 요리에 실패했어! 정체불명의 검은 덩어리만 남았고 "
            "넣었던 재료 3개는 전부 사라졌어."
        ), None, False

    used.append(recipe_id)
    healed = apply_adventure_food_effect(adventure, recipe_id)

    first_discovery = recipe_id not in discovered_foods
    if first_discovery:
        discovered_foods[recipe_id] = {
            "name": None,
            "discoverer_id": uid,
            "discoverer_name": member.display_name,
            "discovered_at": datetime.now(KST).isoformat(),
        }
        adventure["pending_food_recipe_id"] = recipe_id

    food_name = get_discovered_food_name(recipe_id)
    effect_text = get_adventure_food_effect_text(recipe_id)
    heal_note = ""
    if ADVENTURE_COOKING_RECIPES[recipe_id].get("effects", {}).get("heal"):
        heal_note = f"\n실제 회복: **{healed}** · 현재 목숨 **{adventure['lives']}/{adventure['max_lives']}**"

    save_data()
    return True, (
        f"🍽️ **{food_name}** 완성! 바로 먹어서 버프를 받았어.\n"
        f"효과: **{effect_text}**{heal_note}"
    ), recipe_id, first_discovery


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



def get_relic_upgrade_state(uid, item_id):
    uid = str(uid)

    if uid not in relic_upgrades or not isinstance(relic_upgrades[uid], dict):
        relic_upgrades[uid] = {}

    if item_id not in relic_upgrades[uid] or not isinstance(relic_upgrades[uid][item_id], dict):
        relic_upgrades[uid][item_id] = {
            "level": 0,
            "attempts": 0,
            "failures": 0,
            "fail_streak": 0,
        }

    state = relic_upgrades[uid][item_id]
    state["level"] = max(0, min(RELIC_MAX_ENHANCEMENT, int(state.get("level", 0))))
    state["attempts"] = max(0, int(state.get("attempts", 0)))
    state["failures"] = max(0, int(state.get("failures", 0)))
    state["fail_streak"] = max(0, int(state.get("fail_streak", 0)))
    return state


def get_relic_enhancement_style(level):
    level = max(0, min(RELIC_MAX_ENHANCEMENT, int(level)))
    return RELIC_ENHANCEMENT_STYLES[level]


def format_relic_name(uid, item_id, markdown=True):
    state = get_relic_upgrade_state(uid, item_id)
    level = state["level"]
    style = get_relic_enhancement_style(level)
    name = get_adventure_item_name(item_id)
    suffix = f" +{level}" if level > 0 else ""
    label = f"{style['emoji']} {name}{suffix}"
    return f"**{label}**" if markdown else label


def format_relic_ansi_name(uid, item_id):
    """상세 화면에서 강화 단계에 맞는 ANSI 색상으로 유물 이름을 표시한다."""
    state = get_relic_upgrade_state(uid, item_id)
    level = state["level"]
    style = get_relic_enhancement_style(level)
    name = get_adventure_item_name(item_id)
    suffix = f" +{level}" if level > 0 else ""
    return f"```ansi\n\u001b[1;{style['ansi']}m{name}{suffix}\u001b[0m\n```"


def get_owned_relic_entries(uid):
    inventory = get_adventure_inventory(uid)
    entries = []

    for item_id, count in inventory.items():
        item = ADVENTURE_ITEM_CATALOG.get(item_id)
        if not item or item.get("kind") != "relic" or int(count) <= 0:
            continue
        entries.append((item_id, int(count)))

    entries.sort(
        key=lambda pair: (
            -get_relic_upgrade_state(uid, pair[0])["level"],
            -ADVENTURE_RARITY_ORDER[ADVENTURE_ITEM_CATALOG[pair[0]]["rarity"]],
            get_adventure_item_name(pair[0]),
        )
    )
    return entries


def resolve_owned_relic_id(uid, query):
    if not query:
        return None

    query = str(query).strip()
    owned_ids = {item_id for item_id, _ in get_owned_relic_entries(uid)}
    if query in owned_ids:
        return query

    normalized_query = normalize_item_name_for_filter(query)
    for item_id in owned_ids:
        if normalize_item_name_for_filter(get_adventure_item_name(item_id)) == normalized_query:
            return item_id
    return None


def get_relic_name_themes(item_id):
    """호환용 이름. 실제 속성은 작명과 무관하게 유물 ID와 출현 지형으로 결정된다."""
    item = ADVENTURE_ITEM_CATALOG.get(item_id, {})
    terrain_key = item.get("terrain")
    terrain_themes = {
        "desert": ["fire", "earth", "machine"],
        "grassland": ["wind", "nature", "water"],
        "jungle": ["nature", "beast", "dark"],
        "cave": ["earth", "dark", "magic", "machine"],
        "mountain": ["wind", "earth", "beast"],
        "ice": ["ice", "wind", "beast"],
        "demon": ["dark", "fire", "magic", "beast"],
        "heaven": ["light", "wind", "magic"],
    }
    candidates = terrain_themes.get(terrain_key, list(RELIC_MATERIAL_THEMES.keys()))
    seed = int(hashlib.sha256(f"{item_id}|relic-affinity-v2".encode("utf-8")).hexdigest()[:16], 16)
    return [random.Random(seed).choice(candidates)]


def get_relic_effects(uid, item_id, override_level=None):
    item = ADVENTURE_ITEM_CATALOG.get(item_id, {})
    if item.get("kind") != "relic":
        return {}
    level = get_relic_upgrade_state(uid, item_id)["level"] if override_level is None else int(override_level)
    level = max(0, min(RELIC_MAX_ENHANCEMENT, level))
    theme_key = get_relic_name_themes(item_id)[0]
    effect_info = RELIC_THEME_EFFECTS[theme_key]
    rarity_mul = RELIC_RARITY_EFFECT_MULTIPLIER.get(item.get("rarity"), 1.0)
    level_mul = 1.0 + level * 0.28
    if level >= 5:
        level_mul += 0.12
    if level >= 7:
        level_mul += 0.25

    effects = {}
    main_key, main_base = effect_info["main"]
    effects[main_key] = effects.get(main_key, 0.0) + main_base * rarity_mul * level_mul

    # +4부터 보조 특성이 열리고 +7에서 완성 보정을 받는다.
    if level >= 4:
        sub_key, sub_base = effect_info["sub"]
        sub_mul = 1.0 + (level - 4) * 0.20
        if level >= 7:
            sub_mul += 0.25
        effects[sub_key] = effects.get(sub_key, 0.0) + sub_base * rarity_mul * sub_mul

    # 초월 +7은 원정 시작 목숨을 하나 더 준다.
    if item.get("rarity") == "transcendent" and level >= 7:
        effects["max_lives"] = effects.get("max_lives", 0) + 1

    return effects


def format_relic_effects(uid, item_id, override_level=None):
    effects = get_relic_effects(uid, item_id, override_level=override_level)
    parts = []
    for key, value in effects.items():
        label = RELIC_EFFECT_LABELS.get(key, key)
        if key == "max_lives":
            parts.append(f"{label} +{int(value)}")
        elif key == "relic":
            parts.append(f"{label} +{value:.2f}%p")
        else:
            parts.append(f"{label} +{value:.1f}%")
    return " · ".join(parts) if parts else "효과 없음"


def get_equipped_relic_ids(uid):
    adventure = get_adventure(uid)
    inventory = get_adventure_inventory(uid)
    equipped = [
        item_id for item_id in adventure.get("equipped_relics", [])
        if ADVENTURE_ITEM_CATALOG.get(item_id, {}).get("kind") == "relic"
        and int(inventory.get(item_id, 0)) > 0
    ]
    adventure["equipped_relics"] = list(dict.fromkeys(equipped))[:RELIC_MAX_EQUIPPED]
    return adventure["equipped_relics"]


def get_equipped_relic_boosts(uid):
    boosts = {"battle": 0.0, "luck": 0.0, "loot": 0.0, "escape": 0.0, "life_save": 0.0, "relic": 0.0, "max_lives": 0}
    for item_id in get_equipped_relic_ids(uid):
        for key, value in get_relic_effects(uid, item_id).items():
            boosts[key] = boosts.get(key, 0) + value
    boosts["max_lives"] = int(boosts.get("max_lives", 0))
    return boosts


def get_equipped_relic_summary(uid):
    equipped = get_equipped_relic_ids(uid)
    if not equipped:
        return "장착 중인 유물 없음"
    return "\n".join(
        f"💠 {format_relic_name(uid, item_id)} — {format_relic_effects(uid, item_id)}"
        for item_id in equipped
    )


def get_upgrade_material_search_text(item_id):
    item = ADVENTURE_ITEM_CATALOG[item_id]
    terrain = get_terrain_info(item.get("terrain")) if item.get("terrain") else {}
    parts = [
        get_adventure_item_name(item_id),
        str(item.get("kind", "")),
        str(item.get("source_monster") or ""),
        str(terrain.get("name", "")),
    ]
    return normalize_item_name_for_filter(" ".join(parts))


def material_matches_relic_themes(item_id, theme_keys):
    item = ADVENTURE_ITEM_CATALOG[item_id]
    search_text = get_upgrade_material_search_text(item_id)
    terrain_key = item.get("terrain")

    for theme_key in theme_keys:
        theme = RELIC_MATERIAL_THEMES[theme_key]
        if terrain_key in theme.get("terrains", []):
            return True
        if any(normalize_item_name_for_filter(keyword) in search_text for keyword in theme["material_keywords"]):
            return True
    return False


def get_relic_upgrade_success_rate(item_id, target_level, uid=None):
    item = ADVENTURE_ITEM_CATALOG[item_id]
    rules = RELIC_UPGRADE_RULES[item["rarity"]]
    target_level = max(1, min(RELIC_MAX_ENHANCEMENT, int(target_level)))
    base = float(rules["success"][target_level - 1])
    if uid is None:
        return base
    fail_streak = get_relic_upgrade_state(uid, item_id).get("fail_streak", 0)
    return min(RELIC_PITY_MAX_SUCCESS_RATE, base + fail_streak * RELIC_PITY_BONUS_PER_FAIL)


def get_relic_upgrade_requirements(item_id, target_level):
    """
    유물 ID, 고유 속성, 등급, 목표 강화 단계를 씨앗으로 재료를 고정 랜덤 생성한다.
    서버가 재시작되어도 같은 유물의 같은 단계는 항상 같은 재료를 요구한다.
    """
    item = ADVENTURE_ITEM_CATALOG[item_id]
    rarity_key = item["rarity"]
    rules = RELIC_UPGRADE_RULES[rarity_key]
    target_level = max(1, min(RELIC_MAX_ENHANCEMENT, int(target_level)))
    seed_text = f"{item_id}|{rarity_key}|{target_level}|upgrade-recipe-v2"
    seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16)
    rng = random.Random(seed)

    all_materials = [
        material_id
        for material_id, material in ADVENTURE_ITEM_CATALOG.items()
        if material.get("kind") != "relic"
    ]
    theme_keys = get_relic_name_themes(item_id)
    themed_materials = [
        material_id
        for material_id in all_materials
        if material_matches_relic_themes(material_id, theme_keys)
    ]

    minimum_types, maximum_types = rules["type_range"]
    type_count = rng.randint(minimum_types, maximum_types)
    if target_level >= 5 and maximum_types < 6 and rng.random() < 0.45:
        type_count += 1
    type_count = min(type_count, len(all_materials), 6)

    selected = []
    attempts = 0
    while len(selected) < type_count and attempts < 500:
        attempts += 1
        # 고유 속성과 맞는 재료가 75%, 전체 전리품에서 무작위 재료가 25%.
        pool = themed_materials if themed_materials and rng.random() < 0.75 else all_materials
        candidate = rng.choice(pool)
        if candidate not in selected:
            selected.append(candidate)

    # 테마 후보가 지나치게 적은 경우에도 무한 반복 없이 전체 재료에서 채운다.
    if len(selected) < type_count:
        remaining = [material_id for material_id in all_materials if material_id not in selected]
        rng.shuffle(remaining)
        selected.extend(remaining[:type_count - len(selected)])

    minimum_amount, maximum_amount = rules["amount_range"]
    level_scale = 1.0 + (target_level - 1) * 0.45
    requirements = []

    for material_id in selected:
        material = ADVENTURE_ITEM_CATALOG[material_id]
        material_rank = ADVENTURE_RARITY_ORDER.get(material["rarity"], 0)
        base_amount = rng.randint(minimum_amount, maximum_amount)

        # 희귀 재료는 너무 많은 수량을 요구하지 않도록 수량을 낮춘다.
        rarity_divisor = 1.0 + material_rank * 0.38
        amount = max(1, int(round(base_amount * level_scale / rarity_divisor)))
        requirements.append((material_id, amount))

    requirements.sort(
        key=lambda pair: (
            -ADVENTURE_RARITY_ORDER[ADVENTURE_ITEM_CATALOG[pair[0]]["rarity"]],
            get_adventure_item_name(pair[0]),
        )
    )
    return requirements


def get_missing_relic_materials(uid, requirements):
    inventory = get_adventure_inventory(uid)
    missing = []
    for material_id, required in requirements:
        owned = max(0, int(inventory.get(material_id, 0)))
        if owned < required:
            missing.append((material_id, required, owned))
    return missing


def consume_relic_upgrade_materials(uid, requirements, consume_rate=1.0):
    inventory = get_adventure_inventory(uid)
    consumed = []
    consume_rate = max(0.0, min(1.0, float(consume_rate)))
    for material_id, required in requirements:
        amount = max(1, int(math.ceil(int(required) * consume_rate))) if consume_rate > 0 else 0
        remaining = max(0, int(inventory.get(material_id, 0)) - amount)
        if remaining > 0:
            inventory[material_id] = remaining
        else:
            inventory.pop(material_id, None)
        consumed.append((material_id, amount))
    return consumed


def build_owned_relic_embed(member, uid, page=0):
    entries = get_owned_relic_entries(uid)
    total_pages = max(1, (len(entries) + ADVENTURE_RELIC_PAGE_SIZE - 1) // ADVENTURE_RELIC_PAGE_SIZE)
    page = max(0, min(int(page), total_pages - 1))
    start = page * ADVENTURE_RELIC_PAGE_SIZE
    page_entries = entries[start:start + ADVENTURE_RELIC_PAGE_SIZE]

    embed = discord.Embed(
        title=f"🔮 {member.display_name}의 유물",
        color=discord.Color.purple(),
    )

    if not page_entries:
        embed.description = "아직 보유한 유물이 없어. 모험에서 유물을 발견해 봐!"
    else:
        lines = []
        for item_id, count in page_entries:
            item = ADVENTURE_ITEM_CATALOG[item_id]
            rarity = ADVENTURE_RARITIES[item["rarity"]]
            state = get_relic_upgrade_state(uid, item_id)
            level = state["level"]
            if item_id not in discovered_items:
                next_text = "이름 등록 대기 중"
            elif level >= RELIC_MAX_ENHANCEMENT:
                next_text = "최대 강화 완료"
            else:
                chance = get_relic_upgrade_success_rate(item_id, level + 1, uid)
                next_text = f"다음 강화 성공률 {chance:.0f}%"

            equipped_mark = " · ✅ 장착" if item_id in get_equipped_relic_ids(uid) else ""
            lines.append(
                f"{format_relic_name(uid, item_id)} ×{count}{equipped_mark}\n"
                f"└ {rarity['emoji']} {rarity['name']} · {next_text}"
            )
        embed.description = "\n\n".join(lines)
        embed.add_field(
            name="사용법",
            value="`/유물 이름:<유물>`로 재료와 강화 버튼을 확인할 수 있어.",
            inline=False,
        )

    embed.set_footer(text=f"페이지 {page + 1}/{total_pages} · 보유 유물 {len(entries)}종 · 유물은 /가방에 표시되지 않음")
    return embed, total_pages


def build_relic_detail_embed(member, uid, item_id):
    item = ADVENTURE_ITEM_CATALOG[item_id]
    rarity = ADVENTURE_RARITIES[item["rarity"]]
    state = get_relic_upgrade_state(uid, item_id)
    level = state["level"]
    style = get_relic_enhancement_style(level)
    inventory = get_adventure_inventory(uid)
    owned_count = max(0, int(inventory.get(item_id, 0)))
    theme_keys = get_relic_name_themes(item_id)
    theme_text = ", ".join(RELIC_MATERIAL_THEMES[key]["display"] for key in theme_keys)
    equipped = item_id in get_equipped_relic_ids(uid)

    embed = discord.Embed(
        title=f"{style['emoji']} 유물 상세",
        description=format_relic_ansi_name(uid, item_id),
        color=discord.Color(style["color"]),
    )
    embed.add_field(
        name="기본 정보",
        value=(
            f"등급: {rarity['emoji']} **{rarity['name']}**\n"
            f"강화: **+{level}/{RELIC_MAX_ENHANCEMENT}** · 색상: **{style['name']}**\n"
            f"보유 수량: **{owned_count}개**\n"
            f"고유 속성: **{theme_text}** · {'✅ 장착 중' if equipped else '미장착'}"
        ),
        inline=False,
    )
    embed.add_field(
        name="현재 유물 효과",
        value=format_relic_effects(uid, item_id),
        inline=False,
    )

    if item_id not in discovered_items:
        embed.add_field(
            name="강화 불가",
            value="아직 이름이 등록되지 않은 유물이야. 최초 발견자가 이름을 정한 뒤 강화할 수 있어.",
            inline=False,
        )
    elif level >= RELIC_MAX_ENHANCEMENT:
        embed.add_field(
            name="🌈 최대 강화 완료",
            value=f"이 유물은 이미 **+{RELIC_MAX_ENHANCEMENT}**까지 강화됐어.",
            inline=False,
        )
    else:
        target_level = level + 1
        chance = get_relic_upgrade_success_rate(item_id, target_level, uid)
        requirements = get_relic_upgrade_requirements(item_id, target_level)
        lines = []
        for material_id, required in requirements:
            material = ADVENTURE_ITEM_CATALOG[material_id]
            material_rarity = ADVENTURE_RARITIES[material["rarity"]]
            owned = max(0, int(inventory.get(material_id, 0)))
            mark = "✅" if owned >= required else "❌"
            lines.append(
                f"{mark} {material_rarity['emoji']} **{get_adventure_item_name(material_id)}** "
                f"{owned}/{required}"
            )

        embed.add_field(
            name=f"🔨 +{target_level} 강화 재료",
            value="\n".join(lines),
            inline=False,
        )
        embed.add_field(
            name="성공 확률",
            value=(
                f"**{chance:.0f}%** · 연속 실패 보정 **+{state['fail_streak'] * RELIC_PITY_BONUS_PER_FAIL:.0f}%p**\n"
                f"성공하면 재료 전부, 실패하면 재료의 **{RELIC_FAILURE_MATERIAL_CONSUME_RATE * 100:.0f}%**만 소모돼.\n"
                f"다음 단계 효과: {format_relic_effects(uid, item_id, override_level=target_level)}"
            ),
            inline=False,
        )

    embed.set_footer(text=f"강화 시도 {state['attempts']}회 · 누적 실패 {state['failures']}회 · 연속 실패 {state['fail_streak']}회")
    return embed


class OwnedRelicView(discord.ui.View):
    def __init__(self, user_id, member, page=0):
        super().__init__(timeout=180)
        self.user_id = str(user_id)
        self.member = member
        self.page = max(0, int(page))
        _, total_pages = build_owned_relic_embed(member, self.user_id, self.page)
        self.previous_page.disabled = self.page <= 0
        self.next_page.disabled = self.page >= total_pages - 1

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return
        self.page = max(0, self.page - 1)
        embed, _ = build_owned_relic_embed(self.member, self.user_id, self.page)
        await interaction.response.edit_message(embed=embed, view=OwnedRelicView(self.user_id, self.member, self.page))

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return
        self.page += 1
        embed, total_pages = build_owned_relic_embed(self.member, self.user_id, self.page)
        self.page = min(self.page, total_pages - 1)
        await interaction.response.edit_message(embed=embed, view=OwnedRelicView(self.user_id, self.member, self.page))


class RelicUpgradeView(discord.ui.View):
    def __init__(self, user_id, member, item_id):
        super().__init__(timeout=300)
        self.user_id = str(user_id)
        self.member = member
        self.item_id = item_id
        state = get_relic_upgrade_state(self.user_id, self.item_id)
        target_level = min(RELIC_MAX_ENHANCEMENT, state["level"] + 1)
        self.upgrade_button.label = f"🔨 +{target_level} 강화 도전"
        self.upgrade_button.disabled = (
            state["level"] >= RELIC_MAX_ENHANCEMENT
            or self.item_id not in discovered_items
        )
        equipped = self.item_id in get_equipped_relic_ids(self.user_id)
        self.equip_button.label = "💠 유물 해제" if equipped else "💠 유물 장착"
        self.equip_button.style = discord.ButtonStyle.secondary if equipped else discord.ButtonStyle.success

    @discord.ui.button(label="🔨 강화 도전", style=discord.ButtonStyle.danger)
    async def upgrade_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        async with get_adventure_lock(self.user_id):
            owned_ids = {item_id for item_id, _ in get_owned_relic_entries(self.user_id)}
            if self.item_id not in owned_ids:
                await interaction.response.send_message("❌ 더 이상 이 유물을 가지고 있지 않아.", ephemeral=True)
                return

            if self.item_id not in discovered_items:
                await interaction.response.send_message("❌ 이름이 등록된 뒤에 강화할 수 있어.", ephemeral=True)
                return

            state = get_relic_upgrade_state(self.user_id, self.item_id)
            if state["level"] >= RELIC_MAX_ENHANCEMENT:
                await interaction.response.send_message("이미 최대 강화야!", ephemeral=True)
                return

            target_level = state["level"] + 1
            requirements = get_relic_upgrade_requirements(self.item_id, target_level)
            missing = get_missing_relic_materials(self.user_id, requirements)
            if missing:
                lines = [
                    f"• {get_adventure_item_name(material_id)}: {owned}/{required}"
                    for material_id, required, owned in missing
                ]
                await interaction.response.send_message(
                    "❌ 강화 재료가 부족해.\n" + "\n".join(lines),
                    ephemeral=True,
                )
                return

            chance = get_relic_upgrade_success_rate(self.item_id, target_level, self.user_id)
            success = random.random() * 100 < chance
            state["attempts"] += 1

            if success:
                consume_relic_upgrade_materials(self.user_id, requirements, 1.0)
                state["level"] = target_level
                state["fail_streak"] = 0
                result_text = (
                    f"🎉 **강화 성공!** {get_adventure_item_name(self.item_id)}이(가) "
                    f"**+{target_level}**이 됐어.\n"
                    f"새 효과: **{format_relic_effects(self.user_id, self.item_id)}**"
                )
            else:
                consumed = consume_relic_upgrade_materials(
                    self.user_id,
                    requirements,
                    RELIC_FAILURE_MATERIAL_CONSUME_RATE,
                )
                state["failures"] += 1
                state["fail_streak"] += 1
                consumed_text = ", ".join(
                    f"{get_adventure_item_name(material_id)} ×{amount}"
                    for material_id, amount in consumed
                )
                next_chance = get_relic_upgrade_success_rate(self.item_id, target_level, self.user_id)
                result_text = (
                    f"💥 **강화 실패...** 이번 성공 확률은 **{chance:.0f}%**였어.\n"
                    f"절반 소모: {consumed_text}\n"
                    f"연속 실패 보정으로 다음 성공 확률은 **{next_chance:.0f}%**야."
                )

            save_data()
            embed = build_relic_detail_embed(self.member, self.user_id, self.item_id)
            embed.add_field(name="이번 강화 결과", value=result_text, inline=False)
            await interaction.response.edit_message(
                embed=embed,
                view=RelicUpgradeView(self.user_id, self.member, self.item_id),
            )

    @discord.ui.button(label="💠 유물 장착", style=discord.ButtonStyle.success)
    async def equip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return
        owned_ids = {item_id for item_id, _ in get_owned_relic_entries(self.user_id)}
        if self.item_id not in owned_ids:
            await interaction.response.send_message("❌ 그 유물을 가지고 있지 않아.", ephemeral=True)
            return

        adventure = get_adventure(self.user_id)
        equipped = get_equipped_relic_ids(self.user_id)
        if self.item_id in equipped:
            adventure["equipped_relics"] = [item_id for item_id in equipped if item_id != self.item_id]
            result = "✅ 유물을 해제했어."
        else:
            if len(equipped) >= RELIC_MAX_EQUIPPED:
                await interaction.response.send_message(
                    f"❌ 유물은 최대 **{RELIC_MAX_EQUIPPED}개**까지 장착할 수 있어.",
                    ephemeral=True,
                )
                return
            adventure["equipped_relics"] = equipped + [self.item_id]
            result = "✅ 유물을 장착했어. 효과는 다음 개인 모험 시작부터 적용돼."
        save_data()
        embed = build_relic_detail_embed(self.member, self.user_id, self.item_id)
        embed.add_field(name="장착 변경", value=result, inline=False)
        await interaction.response.edit_message(
            embed=embed,
            view=RelicUpgradeView(self.user_id, self.member, self.item_id),
        )


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
    danger = steps * ADVENTURE_DANGER_PER_TURN
    if adventure.get("hard_mode"):
        danger *= ADVENTURE_HARD_DANGER_MUL
    return danger


def is_adventure_hard_mode_unlocked(adventure):
    return bool(
        adventure.get("hard_mode_unlocked")
        or int(adventure.get("best_terrain_rank", 0)) >= ADVENTURE_TERRAIN_DEPTH["demon"]
        or "demon" in adventure.get("visited_terrains", [])
    )


def start_new_adventure(uid, terrain_key, hard_mode=False):
    if terrain_key not in ADVENTURE_START_TERRAINS:
        terrain_key = "grassland"

    adventure = get_adventure(uid)
    boosts = get_equipped_adventure_boosts(uid)
    max_lives = 3 + max(0, int(boosts.get("max_lives", 0)))
    hard_mode = bool(hard_mode and is_adventure_hard_mode_unlocked(adventure))

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
        "pending_food_recipe_id": None,
        "cooked_recipe_ids": [],
        "terrain": terrain_key,
        "terrain_steps": 0,
        "quiet_turns": 0,
        "visited_terrains": [terrain_key],
        "defeated_bosses": [],
        "hard_mode": hard_mode,
        "health_potion_uses": 0,
        "strength_potion_used": False,
        "luck_potion_used": False,
        "story_phase": None,
        "lab_defeated": [],
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
    adventure["pending_food_recipe_id"] = None
    adventure["cooked_recipe_ids"] = []
    adventure["lives"] = 3
    adventure["max_lives"] = 3
    adventure["terrain"] = None
    adventure["quiet_turns"] = 0
    adventure["terrain_steps"] = 0
    adventure["visited_terrains"] = []
    adventure["defeated_bosses"] = []
    adventure["hard_mode"] = False
    adventure["health_potion_uses"] = 0
    adventure["strength_potion_used"] = False
    adventure["luck_potion_used"] = False
    adventure["story_phase"] = None
    adventure["lab_defeated"] = []

    save_data()
    return summary


def get_trait_by_name(name):
    if not name:
        return None

    for trait in MONSTER_TRAITS:
        if trait["name"] == name:
            return trait

    return None


def roll_adventure_monster_tier(adventure=None):
    roll = random.random() * 100

    if adventure and adventure.get("hard_mode"):
        if roll < ADVENTURE_HARD_CALAMITY_RATE:
            return "calamity"
        if roll < ADVENTURE_HARD_CALAMITY_RATE + ADVENTURE_HARD_ELITE_RATE:
            return "elite"
        return "normal"

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
    if adventure.get("hard_mode"):
        normal_target = max(
            1,
            int(normal_target * ADVENTURE_HARD_MONSTER_LEVEL_MUL)
            + ADVENTURE_HARD_MONSTER_LEVEL_FLAT,
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

    boss_names = list(terrain.get("bosses") or ([terrain.get("boss")] if terrain.get("boss") else []))
    boss_name = random.choice(boss_names) if boss_names else None
    defeated = set(adventure.get("defeated_bosses", []))
    is_boss = bool(force_boss and terrain_key not in defeated and boss_name)

    monster = find_adventure_monster_by_name(boss_name) if is_boss else None

    if monster is None:
        normal_pool = [monster for monster in terrain_monsters if monster["name"] not in boss_names]
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


def get_relic_discovery_stats():
    global relic_discovery_stats
    if not isinstance(relic_discovery_stats, dict):
        relic_discovery_stats = {}
    relic_discovery_stats.setdefault("total_relic_rolls", 0)
    relic_discovery_stats.setdefault("attempts_since_transcendent", 0)
    relic_discovery_stats["total_relic_rolls"] = max(0, int(relic_discovery_stats.get("total_relic_rolls", 0)))
    relic_discovery_stats["attempts_since_transcendent"] = max(0, int(relic_discovery_stats.get("attempts_since_transcendent", 0)))
    data["relic_discovery_stats"] = relic_discovery_stats
    return relic_discovery_stats


def get_transcendent_relic_chance_percent(attempts):
    attempts = max(0, int(attempts))
    if attempts >= ADVENTURE_TRANSCENDENT_HARD_PITY:
        return 100.0
    chance = ADVENTURE_TRANSCENDENT_RELIC_CHANCE_PERCENT
    if attempts >= ADVENTURE_TRANSCENDENT_SOFT_PITY_START:
        pity_blocks = (attempts - ADVENTURE_TRANSCENDENT_SOFT_PITY_START) // 100 + 1
        chance += pity_blocks * ADVENTURE_TRANSCENDENT_SOFT_PITY_PER_100
    return min(5.0, chance)


def pick_mystery_relic(adventure=None):
    """초월은 서버 공유 천장으로 판정하고, 나머지는 지형별 일반 유물 풀에서 뽑는다."""
    terrain_key = (adventure or {}).get("terrain") or "grassland"
    stats = get_relic_discovery_stats()
    stats["total_relic_rolls"] += 1
    stats["attempts_since_transcendent"] += 1

    transcendent_relics = [
        item_id
        for item_id, item in ADVENTURE_ITEM_CATALOG.items()
        if item.get("kind") == "relic" and item.get("rarity") == "transcendent"
    ]
    chance = get_transcendent_relic_chance_percent(stats["attempts_since_transcendent"])
    if transcendent_relics and random.random() * 100 < chance:
        stats["attempts_since_transcendent"] = 0
        undiscovered = [item_id for item_id in transcendent_relics if item_id not in discovered_items]
        return random.choice(undiscovered or transcendent_relics)

    all_relics = [
        item_id
        for item_id, item in ADVENTURE_ITEM_CATALOG.items()
        if item.get("kind") == "relic"
        and item.get("rarity") != "transcendent"
        and item.get("terrain") == terrain_key
    ]
    if not all_relics:
        all_relics = [
            item_id
            for item_id, item in ADVENTURE_ITEM_CATALOG.items()
            if item.get("kind") == "relic" and item.get("rarity") != "transcendent"
        ]

    undiscovered = [item_id for item_id in all_relics if item_id not in discovered_items]
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
            f"🎚️ 난이도: **{'🔥 하드모드' if adventure.get('hard_mode') else '일반모드'}**\n"
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
            f"🎒 적용 효과: {format_adventure_boosts(adventure.get('boosts', {}))}\n"
            f"🍳 이번 모험 요리: **{len(adventure.get('cooked_recipe_ids', []))}종**"
        ),
        color=discord.Color(terrain["color"]),
    )

    hard_notice = " 하드모드에서는 회복의 샘이 등장하지 않는다." if adventure.get("hard_mode") else ""
    embed.set_footer(text=f"{terrain['description']} 실제 시간은 무관하며, 완료한 턴 수에 따라 적이 강해진다.{hard_notice}")
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


def validate_food_name(name):
    import re

    clean_name = name.strip()
    if not 1 <= len(clean_name) <= 12:
        return False, "요리 이름은 1~12자로 지어야 해."
    if not re.fullmatch(r"[가-힣a-zA-Z0-9 ]+", clean_name):
        return False, "한글, 영어, 숫자, 공백만 사용할 수 있어."

    normalized = normalize_item_name_for_filter(clean_name)
    if not normalized:
        return False, "사용할 수 없는 이름이야."

    for banned in set(ANGRY_WORDS + DIRTY_WORDS):
        banned_normalized = normalize_item_name_for_filter(banned)
        if banned_normalized and banned_normalized in normalized:
            return False, "금지어가 들어간 이름은 사용할 수 없어."

    meaningless = {"ㅋㅋ", "ㅋㅋㅋ", "ㅎㅎ", "ㅎㅎㅎ", "123", "1234", "asdf", "test", "테스트"}
    if normalized in {normalize_item_name_for_filter(v) for v in meaningless}:
        return False, "조금 더 제대로 된 이름을 지어줘."

    for info in discovered_foods.values():
        old_name = str(info.get("name") or "")
        if old_name and normalize_item_name_for_filter(old_name) == normalized:
            return False, "이미 다른 요리가 쓰고 있는 이름이야."

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
    # 천계 이후에는 어떤 유물도 다음 스테이지로 가는 길을 열 수 없다.
    if current in ADVENTURE_STORY_LOCKED_TERRAINS:
        return []
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


def move_adventure_to_terrain(adventure, destination):
    """갈림길 UI 없이 스토리상 다음 지형으로 강제 이동한다."""
    if destination not in ADVENTURE_TERRAINS:
        return False

    adventure["terrain"] = destination
    adventure["terrain_steps"] = 0
    adventure["quiet_turns"] = 0
    adventure["pending_event"] = None
    clear_adventure_turn_timer(adventure)

    visited = adventure.setdefault("visited_terrains", [])
    if not visited or visited[-1] != destination:
        visited.append(destination)

    if destination == "demon":
        adventure["hard_mode_unlocked"] = True
    return True


def get_story_monster_display_name(member, phase, monster_name):
    if phase == "experiment_19":
        return "19번 실험체 — 대마왕"
    if phase == "experiment_1":
        return f"1번 실험체 — {member.mention}"
    return monster_name


def get_story_monster_level(adventure, phase):
    phase_info = ADVENTURE_STORY_PHASES[phase]

    player_level = max(1, int(adventure.get("level", 1)))
    level_mul = float(phase_info.get("level_mul", 1.0))
    level_flat = int(phase_info.get("level_flat", 0))

    danger_bonus = int(adventure_danger(adventure) * 0.5)

    monster_level = int(
        player_level * level_mul
        + level_flat
        + danger_bonus
    )

    if adventure.get("hard_mode"):
        monster_level = int(monster_level * 1.35)

    return max(1, monster_level)


def roll_adventure_exclusive_equipment_drop(adventure, monster_name):
    """전용 장비는 지정된 몬스터에게서만 각 고정 확률로 획득한다."""
    drops = ADVENTURE_EXCLUSIVE_EQUIPMENT_DROPS.get(monster_name, [])
    owned_weapons = set(adventure.get("owned_weapons", []))
    owned_armors = set(adventure.get("owned_armors", []))

    for kind, equipment_name, chance in drops:
        if kind == "weapon":
            if equipment_name in owned_weapons or equipment_name not in WEAPONS:
                continue
            if random.random() * 100 < chance:
                adventure.setdefault("owned_weapons", ["무인검"]).append(equipment_name)
                return {
                    "kind": "weapon",
                    "name": equipment_name,
                    "bonus": WEAPONS[equipment_name]["bonus"],
                    "special": True,
                    "chance": chance,
                    "source_monster": monster_name,
                }

        elif kind == "armor":
            if equipment_name in owned_armors or equipment_name not in ARMORS:
                continue
            if random.random() * 100 < chance:
                adventure.setdefault("owned_armors", ["모험가 세트"]).append(equipment_name)
                return {
                    "kind": "armor",
                    "name": equipment_name,
                    "bonus": ARMORS[equipment_name]["bonus"],
                    "special": True,
                    "chance": chance,
                    "source_monster": monster_name,
                }

    return None


async def show_adventure_story_scene(
    message,
    member,
    *,
    title,
    story_text,
    next_phase,
    button_label="계속",
    result_lines=None,
    color=None,
):
    uid = str(member.id)
    adventure = get_adventure(uid)
    adventure["story_phase"] = next_phase
    adventure["pending_event"] = {
        "type": "story_continue",
        "next_phase": next_phase,
        "button_label": button_label,
    }
    save_data()

    description_parts = []
    if result_lines:
        description_parts.append("\n".join(result_lines))
    description_parts.append(story_text)

    embed = discord.Embed(
        title=title,
        description="\n\n━━━━━━━━━━━━━━━━━━\n\n".join(description_parts),
        color=color or discord.Color.dark_purple(),
    )
    await message.edit(
        embed=embed,
        view=AdventureStoryContinueView(uid, button_label=button_label),
    )


async def show_adventure_forced_encounter(message, member, phase):
    uid = str(member.id)
    adventure = get_adventure(uid)
    phase_info = ADVENTURE_STORY_PHASES.get(phase)

    if not phase_info:
        await message.edit(
            content="스토리 전투 정보를 찾지 못했어.",
            embed=None,
            view=AdventureTravelView(uid),
        )
        return

    monster_name = phase_info["monster"]
    monster = find_adventure_monster_by_name(monster_name)
    if monster is None:
        await message.edit(
            content=f"몬스터 데이터가 없어: {monster_name}",
            embed=None,
            view=AdventureTravelView(uid),
        )
        return

    terrain_key = adventure.get("terrain") or "grassland"
    terrain = get_terrain_info(terrain_key)
    monster_level = get_story_monster_level(adventure, phase)
    display_name = get_story_monster_display_name(member, phase, monster_name)

    adventure["story_phase"] = phase
    adventure["pending_event"] = {
        "type": "monster",
        "monster_name": monster_name,
        "monster_level": monster_level,
        "trait_name": None,
        "monster_tier": "normal",
        "terrain": terrain_key,
        "is_boss": True,
        "story_phase": phase,
        "display_name": display_name,
    }
    save_data()

    preview_chance = calc_adventure_win_chance(adventure, monster, monster_level, None)

    if phase == "glitch_demon_king":
        title = "!@#%... 대마왕이 나타났다"
        notice = (
            "주변에는 길도, 유물도, 재료도 없어. 오직 대마왕만이 존재해.\n"
            "**쓰러뜨리거나 도주에 성공하면 17번 연구소로 넘어갈 수 있어.**"
        )
    elif phase == "mad_scientist_final":
        title = "🧬 최종보스 — 각성한 매드 사이언티스트"
        notice = "약물을 주입한 과학자의 육체가 붕괴하며 거대한 실험체로 변했다. 이번이 진짜 마지막 전투야."
    elif phase.startswith("experiment_"):
        title = "🚨 실험체 격리 해제"
        notice = "매드 사이언티스트가 다음 격리 장치를 열었다. 이 전투에서는 도망칠 수 없어."
    else:
        title = "🚨 17번 연구소 교전"
        notice = "시설 봉쇄가 시작됐다. 이 적을 쓰러뜨려야 다음 구역으로 갈 수 있어."

    embed = discord.Embed(
        title=title,
        description=(
            f"{notice}\n\n"
            f"위치: **{terrain['emoji']} {terrain['name']}**\n"
            f"**Lv.{monster_level} {display_name}** 등장!\n\n"
            f"내 모험 레벨: **Lv.{adventure['level']}**\n"
            f"{get_adventure_equipment_text(adventure)}\n"
            f"예상 승률: **{preview_chance}%**\n"
            f"❤️ 목숨: **{adventure['lives']}/{adventure.get('max_lives', 3)}**"
        ),
        color=discord.Color.dark_red(),
    )
    await message.edit(
        embed=embed,
        view=AdventureBattleView(uid, allow_escape=bool(phase_info.get("escape"))),
    )


async def continue_adventure_story(message, member):
    adventure = get_adventure(member.id)
    pending = adventure.get("pending_event") or {}
    phase = pending.get("next_phase") or adventure.get("story_phase")

    if phase not in ADVENTURE_STORY_PHASES:
        await message.edit(
            embed=build_adventure_status_embed(member, adventure),
            view=AdventureTravelView(member.id),
        )
        return

    adventure["pending_event"] = None
    save_data()
    await show_adventure_forced_encounter(message, member, phase)


async def give_adventure_ending_role(member):
    guild = member.guild
    role = guild.get_role(ADVENTURE_ENDING_ROLE_ID) if ADVENTURE_ENDING_ROLE_ID else None

    if role is None:
        role = discord.utils.get(guild.roles, name=ADVENTURE_ENDING_ROLE_NAME)

    if role is None:
        try:
            role = await guild.create_role(
                name=ADVENTURE_ENDING_ROLE_NAME,
                reason="모험 시스템 엔딩 보상 역할 자동 생성",
            )
        except (discord.Forbidden, discord.HTTPException) as error:
            print(f"모험 엔딩 역할 생성 실패: {error}")
            return None

    if role not in member.roles:
        try:
            await member.add_roles(role, reason="17번 연구소 모험 엔딩 클리어")
        except (discord.Forbidden, discord.HTTPException) as error:
            print(f"모험 엔딩 역할 지급 실패: {error}")
            return None
    return role


async def complete_adventure_ending(message, member, result_lines):
    uid = str(member.id)
    adventure = get_adventure(uid)
    first_clear = not adventure.get("ending_cleared", False)
    adventure["ending_cleared"] = True
    adventure["ending_clear_count"] = int(adventure.get("ending_clear_count", 0)) + 1
    clear_count = adventure["ending_clear_count"]

    role = await give_adventure_ending_role(member)
    summary = finish_adventure(uid)

    role_text = role.mention if role else f"`{ADVENTURE_ENDING_ROLE_NAME}` (봇 역할 권한을 확인해 줘)"
    ending_embed = discord.Embed(
        title="🎬 ENDING — 17번 연구소",
        description=(
            "\n".join(result_lines)
            + "\n\n━━━━━━━━━━━━━━━━━━\n\n"
            + "매드 사이언티스트의 몸이 무너지자 연구소 전체의 경보가 멎었다.\n"
            + "닫혀 있던 지상 출구가 열리고, 지금까지의 모든 모험이 하나의 실험이었다는 기록만이 남았다.\n\n"
            + f"{member.mention}은(는) 마침내 **모험의 끝**에 도달했다.\n"
            + f"🏅 엔딩 역할: {role_text}\n"
            + f"🔁 엔딩 클리어: **{clear_count}회**\n\n"
            + f"👣 최종 진행: **{summary['steps']}회**\n"
            + f"⚔️ 최종 처치: **{summary['kills']}마리**\n"
            + f"💰 모험 수익: **{summary['earned_mora']:,}모라**"
        ),
        color=discord.Color.gold(),
    )
    ending_embed.set_footer(text="축하해. 모험 시스템의 엔딩을 최초로 완주했어!" if first_clear else "다시 한 번 엔딩을 완주했어!")
    await message.edit(embed=ending_embed, view=None)

    channel = member.guild.get_channel(ADVENTURE_ENDING_CHANNEL_ID) or bot.get_channel(ADVENTURE_ENDING_CHANNEL_ID)
    if channel:
        celebration = discord.Embed(
            title="🎉 모험 엔딩 클리어!",
            description=(
                f"축하합니다, {member.mention}!\n\n"
                "**천계 → 외곽 → !@$*!& → 17번 연구소**를 돌파하고\n"
                "각성한 매드 사이언티스트를 쓰러뜨려 모험 시스템의 엔딩에 도달했습니다.\n\n"
                f"🏅 획득 역할: {role_text}\n"
                f"🔁 누적 엔딩 클리어: **{clear_count}회**"
            ),
            color=discord.Color.gold(),
        )
        celebration.set_thumbnail(url=member.display_avatar.url)
        try:
            await channel.send(content=member.mention, embed=celebration)
        except discord.HTTPException as error:
            print(f"모험 엔딩 축하 메시지 전송 실패: {error}")


async def handle_adventure_story_victory(message, member, phase, result_lines):
    uid = str(member.id)
    adventure = get_adventure(uid)
    defeated = adventure.setdefault("lab_defeated", [])
    monster_name = ADVENTURE_STORY_PHASES.get(phase, {}).get("monster")
    if monster_name and monster_name not in defeated:
        defeated.append(monster_name)

    if phase == "glitch_demon_king":
        move_adventure_to_terrain(adventure, "lab17")
        await show_adventure_story_scene(
            message,
            member,
            title="🧪 17번 연구소",
            story_text=(
                "대마왕의 뒤에서 금속제 방폭문이 모습을 드러냈다.\n"
                "문에는 희미하게 **제17연구소**라는 글자가 적혀 있다.\n\n"
                "시설 방송: `미인가 실험체 접근 확인. 전 구역 봉쇄.`"
            ),
            next_phase="lab_guard",
            button_label="연구소에 진입한다",
            result_lines=result_lines,
            color=discord.Color.dark_teal(),
        )
        return

    phase_flow = {
        "lab_guard": (
            "lab_mtf",
            "🚨 2차 방어선",
            "시설 가드가 쓰러지자 중무장한 **기동특수부대원**이 통로를 봉쇄했다.",
            "다음 구역 돌파",
        ),
        "lab_mtf": (
            "lab_alpha",
            "⚠️ 알파 부대 투입",
            "일반 기동부대로는 막을 수 없다고 판단한 연구소가 **알파 부대원**을 투입했다.",
            "알파 부대와 교전",
        ),
        "lab_alpha": (
            "lab_alpha_leader",
            "🔺 지휘관 접근",
            "알파 부대원의 통신기에서 명령이 흘러나온다.\n`부대장이 직접 처리한다.`",
            "알파 부대장과 맞선다",
        ),
        "lab_alpha_leader": (
            "lab_juggernaut",
            "🛡️ 최종 방어 병기",
            "알파 부대장이 쓰러지자 잠겨 있던 격납고가 열렸다.\n"
            "**알파 부대장을 처치했기 때문에 저거너트가 출현했다.**",
            "저거너트와 교전",
        ),
        "lab_juggernaut": (
            "experiment_19",
            "🧬 매드 사이언티스트",
            "`훌륭해. 여기까지 도달한 개체는 네가 처음이야.`\n\n"
            "흰 가운을 입은 남자가 박수를 치며 관제실에서 내려온다.\n"
            "`하지만 경비를 이긴 정도로 실험이 끝났다고 생각하진 않았겠지?`\n"
            "`19번 실험체, 격리를 해제한다.`",
            "19번 실험체와 맞선다",
        ),
        "experiment_19": (
            "experiment_39",
            "🧫 다음 실험체",
            "매드 사이언티스트: `대마왕조차 실패인가. 좋아, 39번의 데이터를 확인하지.`\n"
            "정체를 알 수 없는 거대한 격리 용기가 열리기 시작한다.",
            "39번 실험체와 맞선다",
        ),
        "experiment_39": (
            "experiment_1",
            "1️⃣ 마지막 실험체",
            f"매드 사이언티스트: `이제 마지막이다. 최초이자 최종 실험체, 1번.`\n\n"
            f"모니터에 표시된 1번 실험체의 이름은 다름 아닌 **{member.mention}**이었다.",
            "1번 실험체와 맞선다",
        ),
        "experiment_1": (
            "mad_scientist_final",
            "💉 최종 실험",
            "매드 사이언티스트: `1번마저 넘어섰다고...? 그렇다면 내가 직접 완성체가 되겠다.`\n\n"
            "그가 검붉은 약물을 자신의 목에 꽂았다. 뼈가 뒤틀리고 연구소 전체가 진동하기 시작한다.",
            "각성한 과학자와 최종전",
        ),
    }

    if phase == "mad_scientist_final":
        await complete_adventure_ending(message, member, result_lines)
        return

    next_data = phase_flow.get(phase)
    if not next_data:
        save_data()
        await message.edit(
            embed=discord.Embed(
                title="⚔️ 전투 승리!",
                description="\n".join(result_lines),
                color=discord.Color.green(),
            ),
            view=AdventureTravelView(uid),
        )
        return

    next_phase, title, story_text, button_label = next_data
    await show_adventure_story_scene(
        message,
        member,
        title=title,
        story_text=story_text,
        next_phase=next_phase,
        button_label=button_label,
        result_lines=result_lines,
        color=discord.Color.dark_red(),
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
    if pending and pending.get("type") == "story_continue":
        await continue_adventure_story(message, member)
        return

    terrain_key = adventure.get("terrain") or "grassland"
    if terrain_key in ADVENTURE_FORCED_TERRAINS:
        phase = adventure.get("story_phase")
        if not phase:
            phase = "glitch_demon_king" if terrain_key == "glitch" else "lab_guard"
            adventure["story_phase"] = phase
            save_data()
        await show_adventure_forced_encounter(message, member, phase)
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
    if (
        terrain_key not in ADVENTURE_STORY_LOCKED_TERRAINS
        and adventure["terrain_steps"] >= 2
        and random.random() * 100 < route_rate
    ):
        destinations = valid_terrain_destinations(terrain_key)
        if len(destinations) > 2:
            destinations = random.sample(destinations, k=random.randint(2, min(3, len(destinations))))
        if queue_terrain_choice(adventure, destinations, "random"):
            adventure["quiet_turns"] = min(10, adventure.get("quiet_turns", 0) + 1)
            save_data()
            await show_terrain_choice(message, member)
            return

    hard_relic_bonus = ADVENTURE_HARD_RELIC_BONUS if adventure.get("hard_mode") else 0.0
    relic_rate = min(
        18.0 if adventure.get("hard_mode") else 12.0,
        1.5 + boosts.get("relic", 0) + danger * 0.018 + hard_relic_bonus,
    )
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
    # 하드모드에서는 회복의 샘이 아예 등장하지 않는다.
    heal_border = money_border if adventure.get("hard_mode") else money_border + 7 + good_event_shift * 0.15

    if roll < relic_rate + monster_border:
        adventure["quiet_turns"] = 0
        save_data()
        await show_adventure_monster_encounter(
            message,
            member,
            adventure,
            monster_tier=roll_adventure_monster_tier(adventure),
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

    if not adventure.get("hard_mode") and adjusted_roll < heal_border:
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
    story_phase = pending.get("story_phase")

    if monster is None:
        adventure["pending_event"] = None
        save_data()
        await message.edit(content="몬스터 데이터를 찾지 못해서 전투가 취소됐어.", embed=None, view=AdventureTravelView(uid))
        return

    battle_level = apply_trait_to_monster_level(monster_level, trait)
    display_name = pending.get("display_name") or format_adventure_monster_name(
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
    leveled, exp = give_adventure_exp(adventure, exp)

    adventure["kills"] += 1
    adventure["total_kills"] += 1
    adventure["earned_mora"] += reward

    # !@$*!&에서는 대마왕 외에 어떤 물건도 존재하지 않는다.
    loot_id = None
    loot_amount = 0
    if story_phase != "glitch_demon_king":
        loot_id = pick_monster_loot(monster["name"], adventure)
        if loot_id:
            loot_amount = 1
            if ADVENTURE_ITEM_CATALOG[loot_id]["rarity"] in {"common", "uncommon"}:
                loot_amount = random.randint(1, 2)
            loot_amount += tier_info["loot_bonus"]
            add_adventure_item(uid, loot_id, loot_amount)

    # 전용 장비가 지정된 적은 오직 자신의 전용 장비 추첨만 사용한다.
    # 따라서 외곽의 신/대마왕/연구소 적 장비가 일반 장비 풀에 섞이지 않는다.
    equipment_drop = None
    exclusive_equipment_drop = roll_adventure_exclusive_equipment_drop(
        adventure, monster["name"]
    )
    if not story_phase and monster["name"] not in ADVENTURE_EXCLUSIVE_EQUIPMENT_DROPS:
        equipment_drop = roll_adventure_equipment_drop(
            adventure, monster_tier=monster_tier, is_boss=is_boss
        )

    relic_id = None
    relic_is_new = False
    allow_relic_drop = not story_phase and terrain_key not in ADVENTURE_STORY_LOCKED_TERRAINS
    if allow_relic_drop:
        relic_chance = min(
            20.0 if adventure.get("hard_mode") else 14.0,
            1.2
            + adventure.get("boosts", {}).get("relic", 0)
            + adventure_danger(adventure) * 0.012
            + (ADVENTURE_HARD_RELIC_BONUS if adventure.get("hard_mode") else 0.0),
        )

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
    story_transition = None
    if is_boss and not story_phase:
        defeated = adventure.setdefault("defeated_bosses", [])
        if terrain_key not in defeated:
            defeated.append(terrain_key)

        if terrain_key == "heaven":
            story_transition = "outskirts"
        elif terrain_key == "outskirts":
            story_transition = "glitch"
        else:
            boss_routes = valid_terrain_destinations(terrain_key)
            queue_terrain_choice(adventure, boss_routes, "boss", monster["name"])

    result_lines = [
        f"✅ **Lv.{battle_level} {display_name}** 처치!",
        f"등급: **{tier_info['name']}**",
        f"승률: **{win_chance}%**",
        f"{get_adventure_equipment_text(adventure)}",
        "",
        f"💰 **{reward:,}모라**",
        f"⭐ 모험 경험치 **{exp} EXP**",
    ]

    if loot_id:
        result_lines.append(f"🎒 {get_adventure_item_line(loot_id, loot_amount)}")
    elif story_phase == "glitch_demon_king":
        result_lines.append("🕳️ 이 공간에는 가져갈 수 있는 전리품이 없었다.")

    if equipment_drop:
        equipment_emoji = "🗡️" if equipment_drop["kind"] == "weapon" else "🛡️"
        result_lines.append(
            f"{equipment_emoji} 새 장비 발견: **{equipment_drop['name']}** "
            f"(승률 보너스 +{equipment_drop['bonus']})"
        )

    if exclusive_equipment_drop:
        equipment_emoji = "🔫" if exclusive_equipment_drop["kind"] == "weapon" else "🛡️"
        equipment_label = "전용 무기" if exclusive_equipment_drop["kind"] == "weapon" else "전용 방어구"
        result_lines.append(
            f"{equipment_emoji} {equipment_label} 획득: **{exclusive_equipment_drop['name']}** "
            f"(승률 보너스 +{exclusive_equipment_drop['bonus']}, "
            f"{exclusive_equipment_drop['source_monster']} 전용 · 드롭률 {exclusive_equipment_drop['chance']:g}%)"
        )

    if leveled:
        result_lines.append(f"\n🎉 모험 레벨 업! 현재 **Lv.{adventure['level']}**")

    if relic_id:
        result_lines.append(f"\n✨ 추가 발견: {get_adventure_item_line(relic_id)}")
        if relic_is_new:
            result_lines.append("최초 발견 유물이야. 이름을 지어줘!")
        if get_route_relic_destinations(relic_id, adventure):
            result_lines.append("🔮 유물이 숨겨진 지형으로 이어지는 길을 열었어!")

    # 강제 스토리 전투는 승리 후 다음 순서로 곧바로 연결한다.
    if story_phase:
        save_data()
        await handle_adventure_story_victory(message, member, story_phase, result_lines)
        return

    # 천계 이후에는 갈림길 선택 없이 보스를 잡아야만 고정된 다음 스테이지로 간다.
    if story_transition == "outskirts":
        move_adventure_to_terrain(adventure, "outskirts")
        save_data()
        result_lines.append(
            "\n🌌 천리의 유지자가 지키던 벽이 무너지고 **외곽**으로 향하는 단 하나의 길이 열렸다."
        )
        embed = discord.Embed(
            title="👑 천계 보스 격파 — 외곽 진입",
            description="\n".join(result_lines),
            color=discord.Color.gold(),
        )
        await message.edit(embed=embed, view=AdventureTravelView(uid))
        return

    if story_transition == "glitch":
        move_adventure_to_terrain(adventure, "glitch")
        adventure["story_phase"] = "glitch_demon_king"
        save_data()
        await show_adventure_story_scene(
            message,
            member,
            title="  !@$*!&",
            story_text=(
                "외곽의 신이 쓰러진 순간 공간이 찢어졌다.\n"
                "빛도 길도 사라지고, 깨진 문자 사이에서 하나의 형체만 다가온다.\n\n"
                "이곳에서는 탐색도, 유물 발견도, 다른 행동도 할 수 없다."
            ),
            next_phase="glitch_demon_king",
            button_label="대마왕을 마주한다",
            result_lines=result_lines,
            color=discord.Color.dark_purple(),
        )
        return

    save_data()

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

    story_phase = pending.get("story_phase")
    if story_phase and story_phase != "glitch_demon_king":
        await message.edit(
            embed=discord.Embed(
                title="🚫 퇴로가 차단됐다",
                description="17번 연구소의 격리문이 닫혀 있어 이 전투에서는 도망칠 수 없어.",
                color=discord.Color.dark_red(),
            ),
            view=AdventureBattleView(uid, allow_escape=False),
        )
        return

    escape_chance = calc_adventure_escape_chance(adventure)
    adventure["pending_event"] = None

    if random.randint(1, 100) <= escape_chance:
        if story_phase == "glitch_demon_king":
            move_adventure_to_terrain(adventure, "lab17")
            adventure["story_phase"] = "lab_guard"
            save_data()
            await show_adventure_story_scene(
                message,
                member,
                title="💨 도주 성공 — 17번 연구소 발견",
                story_text=(
                    f"도주 확률 **{escape_chance}%**\n"
                    f"{get_adventure_equipment_text(adventure)}\n\n"
                    "대마왕의 공격을 피해 깨진 공간의 틈으로 뛰어들었다.\n"
                    "눈을 뜨자 거대한 철문과 함께 **제17연구소**라는 표식이 보였다.\n\n"
                    "시설 방송: `미인가 실험체 접근 확인. 전 구역 봉쇄.`"
                ),
                next_phase="lab_guard",
                button_label="연구소에 진입한다",
                color=discord.Color.blue(),
            )
            return

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


def build_adventure_start_embed(uid, hard_mode=False):
    adventure = get_adventure(uid)
    unlocked = is_adventure_hard_mode_unlocked(adventure)
    weapon = adventure.get("weapon", "무인검")
    armor = adventure.get("armor", "모험가 세트")

    lines = []
    for terrain_key in ADVENTURE_START_TERRAINS:
        terrain = get_terrain_info(terrain_key)
        lines.append(f"{terrain['emoji']} **{terrain['name']}** — {terrain['description']}")

    start_equipment_text = (
        "\n\n🧰 **시작 모험상점 장비**\n"
        f"{get_adventure_shop_equipment_text(uid)}\n"
        f"📊 합산 효과: **{get_adventure_shop_boost_summary_text(uid)}**\n"
        "바꾸려면 `/모험장비변경`을 사용해. "
        "이 장비 효과는 모험 시작 순간에 이번 모험 버프로 적용돼.\n"
        f"⚔️ 전투 드랍 장비: 🗡️ {weapon} (+{WEAPONS[weapon]['bonus']}) · "
        f"🛡️ {armor} (+{ARMORS[armor]['bonus']})"
    )

    mode_text = "🔥 **하드모드 ON**" if hard_mode else "🟢 **일반모드**"
    hard_description = ""
    if unlocked:
        hard_description = (
            "\n\n🔥 **하드모드 해금 완료**\n"
            "강적/재앙급 출현률과 턴당 위험도, 몬스터 레벨이 증가해. "
            "대신 장비와 유물이 더 잘 나오며 회복의 샘은 등장하지 않아.\n"
            f"현재 선택: {mode_text}"
        )

    return discord.Embed(
        title="🧭 첫 모험 지형을 선택해!",
        description=(
            "처음에는 사막, 초원, 정글 중 하나에서 출발할 수 있어.\n"
            "모험 도중 보스 격파, 특정 유물, 희귀 갈림길을 통해 다른 지형으로 넘어가게 돼.\n\n"
            + "\n\n".join(lines)
            + "\n\n😈 마계는 고산지대 또는 얼음 지대에서만 진입 가능\n"
            + "☁️ 천계는 마계에서만 진입 가능"
            + start_equipment_text
            + hard_description
        ),
        color=discord.Color.red() if hard_mode else discord.Color.blurple(),
    )


class AdventureStoryContinueView(discord.ui.View):
    def __init__(self, user_id, button_label="계속"):
        super().__init__(timeout=900)
        self.user_id = str(user_id)
        self.continue_story.label = button_label

    @discord.ui.button(label="계속", style=discord.ButtonStyle.danger)
    async def continue_story(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        lock = get_adventure_lock(self.user_id)
        if lock.locked():
            await interaction.response.send_message("이미 다음 장면을 처리 중이야.", ephemeral=True)
            return

        async with lock:
            adventure = get_adventure(self.user_id)
            if not adventure.get("active"):
                await interaction.response.send_message("이미 끝난 모험이야.", ephemeral=True)
                return

            await interaction.response.defer()
            await continue_adventure_story(interaction.message, interaction.user)

    @discord.ui.button(label="🍳 요리하기", style=discord.ButtonStyle.success)
    async def cook_food(self, interaction: discord.Interaction, button: discord.ui.Button):
        await open_adventure_cooking_menu(interaction, self.user_id)


class AdventureStartTerrainView(discord.ui.View):
    def __init__(self, user_id, hard_mode=False):
        super().__init__(timeout=180)
        self.user_id = str(user_id)
        adventure = get_adventure(self.user_id)
        self.hard_mode = bool(hard_mode and is_adventure_hard_mode_unlocked(adventure))

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

                adventure = start_new_adventure(
                    self.user_id,
                    selected,
                    hard_mode=self.hard_mode,
                )
                schedule_adventure_turn(adventure)
                save_data()

                terrain_info = get_terrain_info(selected)
                mode_prefix = "🔥 하드모드 · " if adventure.get("hard_mode") else ""
                embed = build_adventure_waiting_embed(
                    interaction.user,
                    adventure,
                    title=f"{mode_prefix}{terrain_info['emoji']} {terrain_info['name']}으로 모험을 떠나는 중...",
                )
                await interaction.response.edit_message(
                    embed=embed,
                    view=AdventureTurnWaitingView(self.user_id),
                )

            button.callback = callback
            self.add_item(button)

        if is_adventure_hard_mode_unlocked(adventure):
            toggle_button = discord.ui.Button(
                label="🔥 하드모드: ON" if self.hard_mode else "🔥 하드모드: OFF",
                style=discord.ButtonStyle.danger if self.hard_mode else discord.ButtonStyle.secondary,
            )

            async def toggle_callback(interaction):
                if not await check_adventure_owner(interaction, self.user_id):
                    return

                current = get_adventure(self.user_id)
                if current.get("active"):
                    await interaction.response.send_message("이미 모험 중이야.", ephemeral=True)
                    return

                self.hard_mode = not self.hard_mode
                toggle_button.label = "🔥 하드모드: ON" if self.hard_mode else "🔥 하드모드: OFF"
                toggle_button.style = discord.ButtonStyle.danger if self.hard_mode else discord.ButtonStyle.secondary
                await interaction.response.edit_message(
                    embed=build_adventure_start_embed(self.user_id, self.hard_mode),
                    view=self,
                )

            toggle_button.callback = toggle_callback
            self.add_item(toggle_button)


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
                if selected == "demon":
                    adventure["hard_mode_unlocked"] = True
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

        potion_button = discord.ui.Button(label="🧪 포션 사용", style=discord.ButtonStyle.primary)

        async def potion_callback(interaction):
            await open_adventure_potion_menu(interaction, self.user_id)

        potion_button.callback = potion_callback
        self.add_item(potion_button)

        cooking_button = discord.ui.Button(label="🍳 요리하기", style=discord.ButtonStyle.success)

        async def cooking_callback(interaction):
            await open_adventure_cooking_menu(interaction, self.user_id)

        cooking_button.callback = cooking_callback
        self.add_item(cooking_button)


def build_adventure_equipment_embed(member, uid):
    adventure = get_adventure(uid)
    weapon = adventure.get("weapon", "무인검")
    armor = adventure.get("armor", "모험가 세트")
    mode_label = "현재 모험 장비" if adventure.get("active") else "다음 모험 시작 장비"

    embed = discord.Embed(
        title=f"🧰 {member.display_name}의 모험 장비",
        description=(
            "아래 선택 메뉴에서 모험 장비를 바꿀 수 있어.\n"
            "모험 시작 전에 바꾸면 다음 모험을 그 장비로 시작하고, "
            "모험 중에 바꾸면 전투 승률에 바로 반영돼.\n"
            "장비는 돈으로 살 수 없고, 병원행이면 기본 장비만 남아.\n\n"
            f"🎖️ 모험 레벨: **Lv.{adventure['level']}**\n"
            f"📌 상태: **{mode_label}**\n"
            f"🗡️ 무기: **{weapon}** (+{WEAPONS[weapon]['bonus']})\n"
            f"🛡️ 갑옷: **{armor}** (+{ARMORS[armor]['bonus']})\n\n"
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


class AdventureShopEquipmentSelect(discord.ui.Select):
    def __init__(self, user_id):
        self.user_id = str(user_id)
        adventure = get_adventure(self.user_id)
        info = get_adventure_shop_user(self.user_id)
        owned = [name for name in info.get("owned", []) if name in ADVENTURE_SHOP_CATALOG]

        if owned:
            options = [
                discord.SelectOption(
                    label=name,
                    description=(
                        ("장착 중 · " if name in info.get("equipped", []) else "보유 중 · ")
                        + get_adventure_shop_item_effect_text(name)
                    )[:100],
                    default=False,
                )
                for name in owned
            ][:25]
            placeholder = "🧰 장착/해제할 모험상점 장비 선택"
            disabled = bool(adventure.get("active"))
        else:
            options = [
                discord.SelectOption(
                    label="구매한 모험상점 장비 없음",
                    value="__none__",
                    description="/모험상점에서 영구 모험 아이템을 먼저 구매해줘.",
                )
            ]
            placeholder = "구매한 모험상점 장비가 없어"
            disabled = True

        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=1,
            options=options,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        adventure = get_adventure(self.user_id)
        if adventure.get("active"):
            await interaction.response.send_message(
                "❌ 모험상점 장비는 모험 시작 전에만 바꿀 수 있어. "
                "이번 모험에는 시작할 때 장착한 장비 효과가 적용 중이야.",
                ephemeral=True,
            )
            return

        selected = self.values[0]
        if selected == "__none__":
            await interaction.response.send_message("구매한 모험상점 장비가 없어.", ephemeral=True)
            return

        info = get_adventure_shop_user(self.user_id)
        if selected not in info.get("owned", []):
            await interaction.response.send_message("보유하지 않은 모험상점 장비야.", ephemeral=True)
            return

        if selected in info["equipped"]:
            info["equipped"].remove(selected)
            result_text = f"📦 **{selected}** 장착 해제 완료."
        else:
            if len(info["equipped"]) >= ADVENTURE_MAX_EQUIPPED:
                await interaction.response.send_message(
                    f"❌ 최대 {ADVENTURE_MAX_EQUIPPED}개까지만 장착할 수 있어. 먼저 하나 해제해줘.",
                    ephemeral=True,
                )
                return

            info["equipped"].append(selected)
            result_text = f"✅ **{selected}** 장착 완료. 다음 모험 시작부터 적용돼!"

        save_data()
        await interaction.response.edit_message(
            embed=build_adventure_shop_equipment_embed(interaction.user, self.user_id, result_text),
            view=AdventureShopEquipmentView(self.user_id),
        )


def build_adventure_shop_equipment_embed(member, uid, result_text=None):
    uid = str(uid)
    adventure = get_adventure(uid)
    info = get_adventure_shop_user(uid)

    lines = []
    for name, item in ADVENTURE_SHOP_CATALOG.items():
        if name in info["equipped"]:
            state = "✅ 장착 중"
        elif name in info["owned"]:
            state = "📦 보유 중"
        else:
            state = f"🔒 미보유 · {item['price']:,}모라"

        lines.append(
            f"**{name}** — {state}\n"
            f"└ {item['desc']}\n"
            f"└ 효과: {get_adventure_shop_item_effect_text(name)}"
        )

    active_notice = ""
    if adventure.get("active"):
        active_notice = (
            "\n\n⚠️ 지금은 모험 중이라 모험상점 장비를 바꿀 수 없어. "
            "이번 모험에는 시작할 때 장착한 장비 효과가 이미 적용돼 있어."
        )

    result_part = f"\n\n{result_text}" if result_text else ""

    embed = discord.Embed(
        title=f"🧰 {member.display_name}의 모험상점 장비",
        description=(
            f"모험 시작 전에 장착할 영구 모험 아이템을 고르는 메뉴야.\n"
            f"최대 **{ADVENTURE_MAX_EQUIPPED}개**까지 장착 가능하고, "
            "장착 효과는 `/모험`으로 새 모험을 시작하는 순간 이번 모험 버프로 들어가.\n\n"
            f"현재 장착: **{len(info['equipped'])}/{ADVENTURE_MAX_EQUIPPED}개**\n"
            f"합산 효과: **{get_adventure_shop_boost_summary_text(uid)}**"
            f"{result_part}"
            f"{active_notice}\n\n"
            + "\n\n".join(lines)
        ),
        color=discord.Color.dark_gold(),
    )
    embed.set_footer(text="구매는 /모험상점 · 장착 변경은 모험 시작 전에만 가능")
    return embed


class AdventureShopEquipmentView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = str(user_id)
        self.add_item(AdventureShopEquipmentSelect(self.user_id))

    @discord.ui.button(label="장착 전부 해제", style=discord.ButtonStyle.secondary)
    async def clear_equipment(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        adventure = get_adventure(self.user_id)
        if adventure.get("active"):
            await interaction.response.send_message(
                "❌ 모험상점 장비는 모험 시작 전에만 바꿀 수 있어.",
                ephemeral=True,
            )
            return

        info = get_adventure_shop_user(self.user_id)
        if not info.get("equipped"):
            await interaction.response.send_message("이미 장착한 모험상점 장비가 없어.", ephemeral=True)
            return

        info["equipped"] = []
        save_data()
        await interaction.response.edit_message(
            embed=build_adventure_shop_equipment_embed(interaction.user, self.user_id, "📦 모든 모험상점 장비를 해제했어."),
            view=AdventureShopEquipmentView(self.user_id),
        )


def get_adventure_potion_usage_text(adventure, potion_name):
    if potion_name == "체력의 포션":
        return f"{int(adventure.get('health_potion_uses', 0))}/2회 사용"
    if potion_name == "힘의 포션":
        return "1/1회 사용" if adventure.get("strength_potion_used") else "0/1회 사용"
    return "1/1회 사용" if adventure.get("luck_potion_used") else "0/1회 사용"


def build_adventure_potion_embed(member, uid):
    adventure = get_adventure(uid)
    info = get_adventure_shop_user(uid)

    lines = []
    for name, potion in ADVENTURE_POTION_CATALOG.items():
        owned = int(info["potions"].get(name, 0))
        usage = get_adventure_potion_usage_text(adventure, name)
        lines.append(
            f"🧪 **{name}** — 보유 **{owned}개** · {usage}\n"
            f"└ {potion['desc']}"
        )

    embed = discord.Embed(
        title=f"🧪 {member.display_name}의 포션 가방",
        description=(
            "아래 선택 메뉴에서 사용할 포션을 골라.\n"
            "사용할 수 없는 상태라면 포션과 사용 횟수는 소모되지 않아.\n\n"
            + "\n\n".join(lines)
        ),
        color=discord.Color.purple(),
    )
    embed.set_footer(text="체력 포션 2회 · 힘/운 포션 각 1회까지 사용 가능")
    return embed


async def use_adventure_potion(uid, potion_name):
    uid = str(uid)
    adventure = get_adventure(uid)
    info = get_adventure_shop_user(uid)

    if not adventure.get("active"):
        return False, "❌ 현재 진행 중인 모험이 없어."

    if potion_name not in ADVENTURE_POTION_CATALOG:
        return False, "❌ 존재하지 않는 포션이야."

    owned = int(info["potions"].get(potion_name, 0))
    if owned <= 0:
        return False, f"❌ **{potion_name}**을 가지고 있지 않아. 모험 전에 상점에서 구매해 둬."

    if potion_name == "체력의 포션":
        used = int(adventure.get("health_potion_uses", 0))
        if used >= 2:
            return False, "❌ 체력의 포션은 한 모험에서 최대 2번만 사용할 수 있어."
        if adventure["lives"] >= adventure.get("max_lives", 3):
            return False, "❌ 이미 목숨이 가득 차 있어. 포션은 소모되지 않았어."

        adventure["lives"] += 1
        adventure["health_potion_uses"] = used + 1
        result = (
            "❤️ 목숨을 1 회복했어!\n"
            f"현재 목숨: **{adventure['lives']}/{adventure.get('max_lives', 3)}**\n"
            f"이번 모험 사용 횟수: **{adventure['health_potion_uses']}/2회**"
        )

    elif potion_name == "힘의 포션":
        if adventure.get("strength_potion_used"):
            return False, "❌ 힘의 포션은 한 모험에서 한 번만 사용할 수 있어."

        adventure["strength_potion_used"] = True
        boosts = adventure.setdefault("boosts", {})
        boosts["battle"] = boosts.get("battle", 0) + 10
        result = "💪 이번 모험이 끝날 때까지 전투 승률이 **10% 증가**해!"

    else:
        if adventure.get("luck_potion_used"):
            return False, "❌ 운의 포션은 한 모험에서 한 번만 사용할 수 있어."

        adventure["luck_potion_used"] = True
        boosts = adventure.setdefault("boosts", {})
        boosts["luck"] = boosts.get("luck", 0) + 12
        boosts["loot"] = boosts.get("loot", 0) + 12
        boosts["relic"] = boosts.get("relic", 0) + 3
        result = "🍀 이번 모험이 끝날 때까지 행운/전리품 **+12%**, 유물 발견률 **+3%p**!"

    remaining = owned - 1
    if remaining > 0:
        info["potions"][potion_name] = remaining
    else:
        info["potions"].pop(potion_name, None)

    save_data()
    return True, (
        f"🧪 **{potion_name}** 사용 완료!\n"
        f"{result}\n"
        f"남은 수량: **{remaining}개**"
    )


class AdventurePotionSelect(discord.ui.Select):
    def __init__(self, user_id):
        self.user_id = str(user_id)
        adventure = get_adventure(self.user_id)
        info = get_adventure_shop_user(self.user_id)

        options = []
        potion_emojis = {
            "체력의 포션": "❤️",
            "힘의 포션": "💪",
            "운의 포션": "🍀",
        }
        for name in ADVENTURE_POTION_CATALOG:
            owned = int(info["potions"].get(name, 0))
            usage = get_adventure_potion_usage_text(adventure, name)
            options.append(
                discord.SelectOption(
                    label=name,
                    description=f"보유 {owned}개 · {usage}",
                    emoji=potion_emojis.get(name, "🧪"),
                )
            )

        super().__init__(
            placeholder="🧪 사용할 포션 선택",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        lock = get_adventure_lock(self.user_id)
        if lock.locked():
            await interaction.response.send_message("이미 다른 행동을 처리 중이야.", ephemeral=True)
            return

        async with lock:
            success, result = await use_adventure_potion(self.user_id, self.values[0])

        embed = build_adventure_potion_embed(interaction.user, self.user_id)
        embed.add_field(
            name="사용 결과" if success else "사용 불가",
            value=result,
            inline=False,
        )
        await interaction.response.edit_message(
            embed=embed,
            view=AdventurePotionView(self.user_id),
        )


class AdventurePotionView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = str(user_id)
        self.add_item(AdventurePotionSelect(self.user_id))


async def open_adventure_potion_menu(interaction, user_id):
    if not await check_adventure_owner(interaction, user_id):
        return

    adventure = get_adventure(user_id)
    if not adventure.get("active"):
        await interaction.response.send_message("이미 끝난 모험이야.", ephemeral=True)
        return

    await interaction.response.send_message(
        embed=build_adventure_potion_embed(interaction.user, user_id),
        view=AdventurePotionView(user_id),
        ephemeral=True,
    )


def build_adventure_cooking_embed(member, uid, selected=None, page=0, result_text=None, active_slot=0):
    selected = (list(selected or []) + [None, None, None])[:3]
    active_slot = max(0, min(int(active_slot), 2))

    entries = get_adventure_cooking_entries(uid)
    total_pages = max(1, (len(entries) + ADVENTURE_COOKING_PAGE_SIZE - 1) // ADVENTURE_COOKING_PAGE_SIZE)
    page = max(0, min(int(page), total_pages - 1))
    start = page * ADVENTURE_COOKING_PAGE_SIZE
    page_entries = entries[start:start + ADVENTURE_COOKING_PAGE_SIZE]

    slot_lines = []
    inventory = get_adventure_inventory(uid)
    for index, item_id in enumerate(selected, start=1):
        marker = "👉 " if index - 1 == active_slot else ""
        if item_id and item_id in ADVENTURE_ITEM_CATALOG:
            owned = int(inventory.get(item_id, 0))
            slot_lines.append(f"{marker}**{index}번 칸:** {get_adventure_item_name(item_id)} · 보유 {owned}개")
        else:
            slot_lines.append(f"{marker}**{index}번 칸:** 비어 있음")

    page_lines = []
    for item_id, amount in page_entries:
        item = ADVENTURE_ITEM_CATALOG[item_id]
        rarity = ADVENTURE_RARITIES[item["rarity"]]
        page_lines.append(f"{rarity['emoji']} {get_adventure_item_name(item_id)} ×{amount}")

    pending_recipe = get_adventure(uid).get("pending_food_recipe_id")
    pending_text = ""
    if pending_recipe:
        pending_text = "\n\n✨ **최초 발견한 요리의 이름을 아직 정하지 않았어.** 아래 이름 짓기 버튼을 눌러줘."

    result_block = f"\n\n## 조리 결과\n{result_text}" if result_text else ""
    embed = discord.Embed(
        title=f"🍳 {member.display_name}의 야전 요리",
        description=(
            "가방의 전리품을 세 칸에 하나씩 넣어 조합해. 재료 순서는 상관없어.\n"
            "먼저 아래 버튼으로 넣을 칸을 고른 뒤, 재료 목록 페이지에서 재료를 선택하면 돼.\n"
            "페이지를 넘겨도 조리대에 넣은 재료는 유지돼.\n"
            "정확한 레시피면 재료가 소모되고, 완성한 요리를 바로 먹어 이번 모험 버프를 받아.\n"
            "틀린 조합도 조리에 실패하면서 넣은 재료 3개를 전부 잃어. 같은 레시피 버프는 모험당 1회만 적용돼.\n\n"
            f"## 조리대 · 현재 선택 칸: {active_slot + 1}번\n" + "\n".join(slot_lines)
            + f"\n\n## 재료 목록 ({page + 1}/{total_pages}쪽)\n"
            + ("\n".join(page_lines) if page_lines else "요리에 쓸 수 있는 전리품이 없어.")
            + pending_text
            + result_block
        ),
        color=discord.Color.orange(),
    )
    embed.set_footer(text=f"발견된 요리 {sum(1 for info in discovered_foods.values() if info.get('name'))}/{len(ADVENTURE_COOKING_RECIPES)}종")
    return embed, page, total_pages, page_entries


class AdventureCookingIngredientSelect(discord.ui.Select):
    def __init__(self, user_id, selected, page, page_entries, active_slot=0):
        self.user_id = str(user_id)
        self.selected_state = (list(selected or []) + [None, None, None])[:3]
        self.page = int(page)
        self.active_slot = max(0, min(int(active_slot), 2))

        options = []
        current = self.selected_state[self.active_slot]
        for item_id, amount in page_entries:
            item = ADVENTURE_ITEM_CATALOG[item_id]
            rarity = ADVENTURE_RARITIES[item["rarity"]]
            options.append(
                discord.SelectOption(
                    label=get_adventure_item_name(item_id)[:100],
                    value=item_id,
                    description=f"{rarity['name']} · 보유 {amount}개"[:100],
                    emoji=rarity["emoji"],
                    default=(item_id == current),
                )
            )

        super().__init__(
            placeholder=f"{self.active_slot + 1}번 칸에 넣을 재료 선택",
            min_values=1,
            max_values=1,
            options=options,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        selected = list(self.selected_state)
        selected[self.active_slot] = self.values[0]
        embed, page, _, _ = build_adventure_cooking_embed(
            interaction.user,
            self.user_id,
            selected,
            self.page,
            active_slot=self.active_slot,
        )
        await interaction.response.edit_message(
            embed=embed,
            view=AdventureCookingView(self.user_id, selected, page, self.active_slot),
        )


class AdventureCookingView(discord.ui.View):
    def __init__(self, user_id, selected=None, page=0, active_slot=0):
        super().__init__(timeout=600)
        self.user_id = str(user_id)
        self.selected = (list(selected or []) + [None, None, None])[:3]
        self.active_slot = max(0, min(int(active_slot), 2))

        entries = get_adventure_cooking_entries(self.user_id)
        self.total_pages = max(1, (len(entries) + ADVENTURE_COOKING_PAGE_SIZE - 1) // ADVENTURE_COOKING_PAGE_SIZE)
        self.page = max(0, min(int(page), self.total_pages - 1))
        start = self.page * ADVENTURE_COOKING_PAGE_SIZE
        page_entries = entries[start:start + ADVENTURE_COOKING_PAGE_SIZE]

        if page_entries:
            self.add_item(
                AdventureCookingIngredientSelect(
                    self.user_id,
                    self.selected,
                    self.page,
                    page_entries,
                    self.active_slot,
                )
            )

        slot_buttons = [self.slot_1, self.slot_2, self.slot_3]
        for index, slot_button in enumerate(slot_buttons):
            slot_button.label = f"{'✅ ' if index == self.active_slot else ''}{index + 1}번 칸"
            slot_button.style = discord.ButtonStyle.primary if index == self.active_slot else discord.ButtonStyle.secondary

        self.previous_page.disabled = self.total_pages <= 1
        self.next_page.disabled = self.total_pages <= 1

    async def change_active_slot(self, interaction: discord.Interaction, slot_index: int):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        embed, page, _, _ = build_adventure_cooking_embed(
            interaction.user,
            self.user_id,
            self.selected,
            self.page,
            active_slot=slot_index,
        )
        await interaction.response.edit_message(
            embed=embed,
            view=AdventureCookingView(self.user_id, self.selected, page, slot_index),
        )

    @discord.ui.button(label="1번 칸", style=discord.ButtonStyle.secondary, row=1)
    async def slot_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.change_active_slot(interaction, 0)

    @discord.ui.button(label="2번 칸", style=discord.ButtonStyle.secondary, row=1)
    async def slot_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.change_active_slot(interaction, 1)

    @discord.ui.button(label="3번 칸", style=discord.ButtonStyle.secondary, row=1)
    async def slot_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.change_active_slot(interaction, 2)

    @discord.ui.button(label="◀ 이전", style=discord.ButtonStyle.secondary, row=2)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return
        new_page = (self.page - 1) % self.total_pages
        embed, page, _, _ = build_adventure_cooking_embed(
            interaction.user,
            self.user_id,
            self.selected,
            new_page,
            active_slot=self.active_slot,
        )
        await interaction.response.edit_message(
            embed=embed,
            view=AdventureCookingView(self.user_id, self.selected, page, self.active_slot),
        )

    @discord.ui.button(label="다음 ▶", style=discord.ButtonStyle.secondary, row=2)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return
        new_page = (self.page + 1) % self.total_pages
        embed, page, _, _ = build_adventure_cooking_embed(
            interaction.user,
            self.user_id,
            self.selected,
            new_page,
            active_slot=self.active_slot,
        )
        await interaction.response.edit_message(
            embed=embed,
            view=AdventureCookingView(self.user_id, self.selected, page, self.active_slot),
        )

    @discord.ui.button(label="🧹 칸 비우기", style=discord.ButtonStyle.secondary, row=3)
    async def clear_slots(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return
        selected = [None, None, None]
        embed, page, _, _ = build_adventure_cooking_embed(
            interaction.user,
            self.user_id,
            selected,
            self.page,
            active_slot=self.active_slot,
        )
        await interaction.response.edit_message(
            embed=embed,
            view=AdventureCookingView(self.user_id, selected, page, self.active_slot),
        )

    @discord.ui.button(label="🔥 요리하기", style=discord.ButtonStyle.danger, row=3)
    async def cook(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        lock = get_adventure_lock(self.user_id)
        if lock.locked():
            await interaction.response.send_message("이미 다른 행동을 처리 중이야.", ephemeral=True)
            return

        async with lock:
            success, result, recipe_id, first_discovery = cook_adventure_food(
                self.user_id, self.selected, interaction.user
            )

        embed, page, _, _ = build_adventure_cooking_embed(
            interaction.user,
            self.user_id,
            [None, None, None],
            self.page,
            result,
            active_slot=self.active_slot,
        )
        if success and first_discovery:
            embed.add_field(
                name="🌟 서버 최초 발견!",
                value="이 레시피를 처음 완성했어. 이 요리의 이름을 직접 지을 수 있어!",
                inline=False,
            )
            view = FoodNamingView(self.user_id, recipe_id)
        else:
            view = AdventureCookingView(self.user_id, [None, None, None], page, self.active_slot)

        await interaction.response.edit_message(embed=embed, view=view)


class FoodNameModal(discord.ui.Modal, title="새 요리 이름 짓기"):
    food_name = discord.ui.TextInput(
        label="요리 이름",
        placeholder="12자 이하",
        min_length=1,
        max_length=12,
        required=True,
    )

    def __init__(self, user_id, recipe_id):
        super().__init__()
        self.user_id = str(user_id)
        self.recipe_id = recipe_id

    async def on_submit(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ 네가 최초 발견한 요리가 아니야.", ephemeral=True)
            return

        adventure = get_adventure(self.user_id)
        info = discovered_foods.get(self.recipe_id)
        if not info or str(info.get("discoverer_id")) != self.user_id:
            adventure["pending_food_recipe_id"] = None
            save_data()
            await interaction.response.send_message("이 요리의 작명 권한을 찾지 못했어.", ephemeral=True)
            return

        if info.get("name"):
            adventure["pending_food_recipe_id"] = None
            save_data()
            embed, page, _, _ = build_adventure_cooking_embed(
                interaction.user,
                self.user_id,
                result_text=f"이미 **{info['name']}**(으)로 등록된 요리야.",
            )
            await interaction.response.edit_message(
                embed=embed,
                view=AdventureCookingView(self.user_id, page=page),
            )
            return

        valid, result = validate_food_name(str(self.food_name.value))
        if not valid:
            await interaction.response.send_message(f"❌ {result}", ephemeral=True)
            return

        info["name"] = result
        info["named_at"] = datetime.now(KST).isoformat()
        adventure["pending_food_recipe_id"] = None
        save_data()

        embed, page, _, _ = build_adventure_cooking_embed(
            interaction.user,
            self.user_id,
            result_text=(
                f"📖 새로운 요리 **{result}**이(가) 서버 레시피 도감에 등록됐어!\n"
                f"최초 발견자: {interaction.user.mention}\n"
                f"효과: **{get_adventure_food_effect_text(self.recipe_id)}**"
            ),
        )
        await interaction.response.edit_message(
            embed=embed,
            view=AdventureCookingView(self.user_id, page=page),
        )


class FoodNamingView(discord.ui.View):
    def __init__(self, user_id, recipe_id):
        super().__init__(timeout=900)
        self.user_id = str(user_id)
        self.recipe_id = recipe_id

    @discord.ui.button(label="✍️ 요리 이름 짓기", style=discord.ButtonStyle.success)
    async def name_food(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return

        adventure = get_adventure(self.user_id)
        info = discovered_foods.get(self.recipe_id, {})
        if info.get("name"):
            adventure["pending_food_recipe_id"] = None
            save_data()
            embed, page, _, _ = build_adventure_cooking_embed(
                interaction.user,
                self.user_id,
                result_text=f"이미 **{info['name']}**(으)로 등록됐어.",
            )
            await interaction.response.edit_message(
                embed=embed,
                view=AdventureCookingView(self.user_id, page=page),
            )
            return

        if str(info.get("discoverer_id")) != self.user_id:
            await interaction.response.send_message("작명 권한이 없어.", ephemeral=True)
            return

        await interaction.response.send_modal(FoodNameModal(self.user_id, self.recipe_id))


async def open_adventure_cooking_menu(interaction, user_id):
    if not await check_adventure_owner(interaction, user_id):
        return

    adventure = get_adventure(user_id)
    if not adventure.get("active"):
        await interaction.response.send_message("이미 끝난 모험이야.", ephemeral=True)
        return

    pending_recipe = adventure.get("pending_food_recipe_id")
    if pending_recipe:
        info = discovered_foods.get(pending_recipe, {})
        if info.get("name"):
            adventure["pending_food_recipe_id"] = None
            save_data()
        elif str(info.get("discoverer_id")) == str(user_id):
            embed, _, _, _ = build_adventure_cooking_embed(interaction.user, user_id)
            await interaction.response.send_message(
                embed=embed,
                view=FoodNamingView(user_id, pending_recipe),
                ephemeral=True,
            )
            return

    embed, page, _, _ = build_adventure_cooking_embed(interaction.user, user_id)
    await interaction.response.send_message(
        embed=embed,
        view=AdventureCookingView(user_id, page=page),
        ephemeral=True,
    )

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

    @discord.ui.button(label="🧪 포션 사용", style=discord.ButtonStyle.primary)
    async def use_potion(self, interaction: discord.Interaction, button: discord.ui.Button):
        await open_adventure_potion_menu(interaction, self.user_id)

    @discord.ui.button(label="🍳 요리하기", style=discord.ButtonStyle.success)
    async def cook_food(self, interaction: discord.Interaction, button: discord.ui.Button):
        await open_adventure_cooking_menu(interaction, self.user_id)

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

        pending = adventure.get("pending_event") or {}
        lock = get_adventure_lock(uid)

        if pending.get("type") == "story_continue" or adventure.get("terrain") in ADVENTURE_FORCED_TERRAINS:
            if lock.locked():
                await interaction.response.send_message("이미 스토리를 진행 중이야.", ephemeral=True)
                return
            async with lock:
                await interaction.response.defer()
                if pending.get("type") == "story_continue":
                    await continue_adventure_story(interaction.message, interaction.user)
                else:
                    phase = adventure.get("story_phase")
                    if not phase:
                        phase = "glitch_demon_king" if adventure.get("terrain") == "glitch" else "lab_guard"
                        adventure["story_phase"] = phase
                        save_data()
                    await show_adventure_forced_encounter(interaction.message, interaction.user, phase)
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

    @discord.ui.button(label="🧪 포션 사용", style=discord.ButtonStyle.primary)
    async def use_potion(self, interaction: discord.Interaction, button: discord.ui.Button):
        await open_adventure_potion_menu(interaction, self.user_id)

    @discord.ui.button(label="🍳 요리하기", style=discord.ButtonStyle.success)
    async def cook_food(self, interaction: discord.Interaction, button: discord.ui.Button):
        await open_adventure_cooking_menu(interaction, self.user_id)

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
    def __init__(self, user_id, allow_escape=True):
        super().__init__(timeout=180)
        self.user_id = str(user_id)
        self.allow_escape = bool(allow_escape)
        self.escape.disabled = not self.allow_escape
        if not self.allow_escape:
            self.escape.label = "🚫 도주 불가"

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

    @discord.ui.button(label="🧪 포션 사용", style=discord.ButtonStyle.primary)
    async def use_potion(self, interaction: discord.Interaction, button: discord.ui.Button):
        await open_adventure_potion_menu(interaction, self.user_id)

    @discord.ui.button(label="🍳 요리하기", style=discord.ButtonStyle.success)
    async def cook_food(self, interaction: discord.Interaction, button: discord.ui.Button):
        await open_adventure_cooking_menu(interaction, self.user_id)

    @discord.ui.button(label="💨 도망가기", style=discord.ButtonStyle.secondary)
    async def escape(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_adventure_owner(interaction, self.user_id):
            return
        if not self.allow_escape:
            await interaction.response.send_message("이 전투에서는 도망칠 수 없어.", ephemeral=True)
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
            "upgrade_recipe_version": 1,
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
        if (
            count > 0
            and item_id in ADVENTURE_ITEM_CATALOG
            and ADVENTURE_ITEM_CATALOG[item_id].get("kind") != "relic"
        )
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
        embed.description = "아직 보유한 전리품이 없어. 유물은 `/유물`에서 확인할 수 있어."
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
            f"강화 재료 종류 {sum(1 for item in ADVENTURE_ITEM_CATALOG.values() if item.get('kind') != 'relic')}종 · 유물은 /유물"
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

        if pending_event and pending_event.get("type") == "story_continue":
            next_phase = pending_event.get("next_phase") or adventure.get("story_phase")
            terrain = get_terrain_info(adventure.get("terrain"))
            await channel.send(
                embed=discord.Embed(
                    title="📖 최종장 진행 중",
                    description=(
                        f"현재 위치: **{terrain['emoji']} {terrain['name']}**\n"
                        "중단된 장면부터 계속 진행할 수 있어."
                    ),
                    color=discord.Color.dark_purple(),
                ),
                view=AdventureStoryContinueView(
                    uid,
                    button_label=pending_event.get("button_label", "계속"),
                ),
            )
            return

        if pending_event and pending_event.get("type") == "monster":
            monster = find_adventure_monster_by_name(pending_event.get("monster_name"))
            trait = get_trait_by_name(pending_event.get("trait_name"))

            if monster:
                monster_tier = pending_event.get("monster_tier", "normal")
                display_name = pending_event.get("display_name") or format_adventure_monster_name(monster["name"], trait, monster_tier)
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
                story_phase = pending_event.get("story_phase")
                allow_escape = bool(
                    not story_phase
                    or ADVENTURE_STORY_PHASES.get(story_phase, {}).get("escape", False)
                )
                await channel.send(
                    embed=embed,
                    view=AdventureBattleView(uid, allow_escape=allow_escape),
                )
                return

            adventure["pending_event"] = None
            save_data()

        if adventure.get("turn_ready_at"):
            embed = build_adventure_waiting_embed(member, adventure)
            await channel.send(embed=embed, view=AdventureTurnWaitingView(uid))
            return

        if adventure.get("terrain") in ADVENTURE_FORCED_TERRAINS:
            terrain = get_terrain_info(adventure.get("terrain"))
            await channel.send(
                embed=discord.Embed(
                    title="📖 최종장 진행 중",
                    description=f"현재 위치: **{terrain['emoji']} {terrain['name']}**\n계속 버튼을 눌러 전투를 이어가.",
                    color=discord.Color.dark_purple(),
                ),
                view=AdventureStoryContinueView(uid, button_label="전투 계속"),
            )
            return

        embed = build_adventure_status_embed(member, adventure)
        await channel.send(embed=embed, view=AdventureTravelView(uid))
        return

    embed = build_adventure_start_embed(uid, hard_mode=False)
    await channel.send(embed=embed, view=AdventureStartTerrainView(uid, hard_mode=False))


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


@bot.tree.command(name="모험장비변경", description="다음 모험 시작 때 적용할 모험상점 장비를 변경한다", guild=GUILD)
async def adventure_equipment_change_command(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    get_adventure(uid)
    get_adventure_shop_user(uid)

    await interaction.response.send_message(
        embed=build_adventure_shop_equipment_embed(interaction.user, uid),
        view=AdventureShopEquipmentView(uid),
        ephemeral=True,
    )


@bot.tree.command(name="가방", description="모험에서 얻은 전리품을 확인한다", guild=GUILD)
async def adventure_inventory_command(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    embed, _ = build_adventure_inventory_embed(interaction.user, uid, 0)
    await interaction.response.send_message(
        embed=embed,
        view=AdventureInventoryView(uid, interaction.user, 0),
    )



@bot.tree.command(name="유물", description="보유 유물의 효과·장착·강화를 관리한다", guild=GUILD)
@app_commands.describe(이름="상세 확인하거나 강화할 유물. 비워두면 전체 목록 표시")
async def owned_relic_command(interaction: discord.Interaction, 이름: str = None):
    uid = str(interaction.user.id)

    if not 이름:
        embed, _ = build_owned_relic_embed(interaction.user, uid, 0)
        await interaction.response.send_message(
            embed=embed,
            view=OwnedRelicView(uid, interaction.user, 0),
        )
        return

    item_id = resolve_owned_relic_id(uid, 이름)
    if not item_id:
        await interaction.response.send_message("❌ 그 유물은 가지고 있지 않아.", ephemeral=True)
        return

    embed = build_relic_detail_embed(interaction.user, uid, item_id)
    await interaction.response.send_message(
        embed=embed,
        view=RelicUpgradeView(uid, interaction.user, item_id),
    )


@owned_relic_command.autocomplete("이름")
async def owned_relic_autocomplete(interaction: discord.Interaction, current: str):
    uid = str(interaction.user.id)
    normalized = normalize_item_name_for_filter(current)
    choices = []

    for item_id, count in get_owned_relic_entries(uid):
        name = get_adventure_item_name(item_id)
        if normalized and normalized not in normalize_item_name_for_filter(name):
            continue
        item = ADVENTURE_ITEM_CATALOG[item_id]
        rarity = ADVENTURE_RARITIES[item["rarity"]]["name"]
        level = get_relic_upgrade_state(uid, item_id)["level"]
        choices.append(
            app_commands.Choice(
                name=f"{name} +{level} · {rarity} · {count}개"[:100],
                value=item_id,
            )
        )
        if len(choices) >= 25:
            break

    return choices


@bot.tree.command(name="초월합성", description="서로 다른 +7 신화 유물 3개와 모라로 초월 유물을 합성한다", guild=GUILD)
@app_commands.describe(이름="초월 유물이 아직 발견되지 않았다면 등록할 이름(1~6자)")
async def transcend_relic_synthesis(interaction: discord.Interaction, 이름: str = None):
    uid = str(interaction.user.id)
    inventory = get_adventure_inventory(uid)
    transcendent_ids = [
        item_id for item_id, item in ADVENTURE_ITEM_CATALOG.items()
        if item.get("kind") == "relic" and item.get("rarity") == "transcendent"
    ]
    if not transcendent_ids:
        await interaction.response.send_message("❌ 초월 유물 데이터가 없어.", ephemeral=True)
        return
    transcendent_id = transcendent_ids[0]
    if int(inventory.get(transcendent_id, 0)) > 0:
        await interaction.response.send_message("❌ 이미 초월 유물을 보유하고 있어.", ephemeral=True)
        return

    eligible = [
        item_id for item_id, count in inventory.items()
        if int(count) > 0
        and ADVENTURE_ITEM_CATALOG.get(item_id, {}).get("rarity") == "mythic"
        and get_relic_upgrade_state(uid, item_id)["level"] >= RELIC_MAX_ENHANCEMENT
    ]
    eligible = list(dict.fromkeys(eligible))
    if len(eligible) < 3:
        await interaction.response.send_message(
            f"❌ 서로 다른 **+7 신화 유물 3개**가 필요해. 현재 조건 충족: **{len(eligible)}개**",
            ephemeral=True,
        )
        return
    if get_poker_money(uid) < TRANSCENDENT_SYNTHESIS_COST:
        await interaction.response.send_message(
            f"❌ 합성 비용이 부족해. 필요: **{TRANSCENDENT_SYNTHESIS_COST:,}모라**",
            ephemeral=True,
        )
        return

    if transcendent_id not in discovered_items:
        if not 이름:
            await interaction.response.send_message(
                "❌ 서버 최초 초월 합성이야. `이름`에 1~6자의 유물 이름을 입력해줘.",
                ephemeral=True,
            )
            return
        valid, result = validate_relic_name(이름)
        if not valid:
            await interaction.response.send_message(f"❌ {result}", ephemeral=True)
            return
        clean_name = result
    else:
        clean_name = discovered_items[transcendent_id]["name"]

    consumed = eligible[:3]
    for item_id in consumed:
        inventory[item_id] = int(inventory.get(item_id, 0)) - 1
        if inventory[item_id] <= 0:
            inventory.pop(item_id, None)
            relic_upgrades.get(uid, {}).pop(item_id, None)
        adventure = get_adventure(uid)
        adventure["equipped_relics"] = [rid for rid in adventure.get("equipped_relics", []) if rid != item_id]

    add_poker_money(uid, -TRANSCENDENT_SYNTHESIS_COST)
    add_adventure_item(uid, transcendent_id, 1)
    if transcendent_id not in discovered_items:
        discovered_items[transcendent_id] = {
            "name": clean_name,
            "discoverer_id": uid,
            "discoverer_name": interaction.user.display_name,
            "discovered_at": datetime.now(KST).isoformat(),
            "upgrade_recipe_version": 2,
            "discovery_method": "mythic_synthesis",
        }
    get_relic_discovery_stats()["attempts_since_transcendent"] = 0
    save_data()

    consumed_names = ", ".join(get_adventure_item_name(item_id) for item_id in consumed)
    await interaction.response.send_message(
        f"🌌 **초월 합성 성공!**\n"
        f"획득: **{clean_name}**\n"
        f"소모 신화 유물: {consumed_names}\n"
        f"소모 모라: **{TRANSCENDENT_SYNTHESIS_COST:,}모라**"
    )


@bot.tree.command(name="유물도감", description="서버에서 발견된 이름 있는 유물을 확인한다", guild=GUILD)
async def relic_dex_command(interaction: discord.Interaction):
    embed, _ = build_relic_dex_embed(0)
    await interaction.response.send_message(embed=embed, view=RelicDexView(0))


@bot.tree.command(name="모험상점", description="모험용 아이템과 포션을 구매한다", guild=GUILD)
@app_commands.describe(
    아이템="구매하거나 장착할 아이템 이름. 비워두면 목록 표시",
    수량="포션을 한꺼번에 구매할 수량 (1~999)",
)
async def adventure_shop_command(
    interaction: discord.Interaction,
    아이템: str = None,
    수량: app_commands.Range[int, 1, 999] = 1,
):
    uid = str(interaction.user.id)
    info = get_adventure_shop_user(uid)
    adventure = get_adventure(uid)

    if 아이템 is None:
        equipment_lines = []
        for name, item in ADVENTURE_SHOP_CATALOG.items():
            if name in info["equipped"]:
                state = "✅ 장착 중"
            elif name in info["owned"]:
                state = "📦 보유 중"
            else:
                state = f"💰 {item['price']:,}모라"

            equipment_lines.append(f"**{name}** — {state}\n└ {item['desc']}")

        potion_lines = []
        for name, item in ADVENTURE_POTION_CATALOG.items():
            count = int(info["potions"].get(name, 0))
            potion_lines.append(
                f"**{name}** — 🧪 보유 {count}개 · 💰 {item['price']:,}모라\n"
                f"└ {item['desc']}"
            )

        embed = discord.Embed(
            title="🧭 모험 상점",
            description=(
                "## 영구 모험 아이템\n"
                + "\n\n".join(equipment_lines)
                + "\n\n## 포션\n"
                + "\n\n".join(potion_lines)
            ),
            color=discord.Color.dark_gold(),
        )
        embed.set_footer(
            text=(
                f"영구 아이템은 최대 {ADVENTURE_MAX_EQUIPPED}개 장착 · "
                "포션은 수량을 입력해 한꺼번에 구매 가능 · 모험 중에는 '포션 사용' 버튼으로 사용"
            )
        )
        await interaction.response.send_message(embed=embed)
        return

    # 포션은 모험 전에 구매하고, 모험 중에는 화면의 포션 버튼으로 사용한다.
    if 아이템 in ADVENTURE_POTION_CATALOG:
        potion = ADVENTURE_POTION_CATALOG[아이템]

        if adventure["active"]:
            await interaction.response.send_message(
                "❌ 모험 중에는 `/모험상점`으로 포션을 사용할 수 없어. "
                "모험 화면의 **🧪 포션 사용** 버튼을 눌러줘.",
                ephemeral=True,
            )
            return

        quantity = max(1, int(수량))
        total_price = potion["price"] * quantity
        money = get_poker_money(uid)
        if money < total_price:
            affordable = money // potion["price"]
            await interaction.response.send_message(
                f"❌ 모라 부족!\n필요: **{total_price:,}모라** "
                f"({potion['price']:,} × {quantity})\n"
                f"보유: **{money:,}모라** · 최대 구매 가능: **{affordable}개**",
                ephemeral=True,
            )
            return

        remove_poker_money(uid, total_price)
        info["potions"][아이템] = int(info["potions"].get(아이템, 0)) + quantity
        save_data()
        await interaction.response.send_message(
            f"🛒 **{아이템}** {quantity}개 구매 완료!\n"
            f"사용 모라: **{total_price:,}모라**\n"
            f"현재 보유: **{info['potions'][아이템]}개**"
        )
        return

    if 아이템 not in ADVENTURE_SHOP_CATALOG:
        await interaction.response.send_message("❌ 그런 모험 아이템은 없어.", ephemeral=True)
        return

    if int(수량) != 1:
        await interaction.response.send_message(
            "❌ 영구 모험 아이템은 한 번에 하나만 구매하거나 장착할 수 있어. 수량은 포션 구매에만 적용돼.",
            ephemeral=True,
        )
        return

    if adventure["active"]:
        await interaction.response.send_message(
            "❌ 모험 중에는 영구 아이템을 바꿀 수 없어. 포션은 모험 화면의 버튼으로 사용해.",
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
    all_names = list(ADVENTURE_SHOP_CATALOG) + list(ADVENTURE_POTION_CATALOG)
    names = [name for name in all_names if current in name.lower()][:25]
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
            f"하드모드: **{'해금됨' if is_adventure_hard_mode_unlocked(adventure) else '잠김 (마계 도달 필요)'}**\n"
            f"현재 난이도: **{'하드모드' if adventure.get('hard_mode') else '일반모드'}**\n"
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

# 기존 판매가가 너무 낮아 모든 판매 가능 전리품의 가격을 2배로 계산한다.
ADVENTURE_SELL_PRICE_MULTIPLIER = 2.0


def get_adventure_sell_unit_price(item):
    return max(1, int(item.get("value", 1) * ADVENTURE_SELL_PRICE_MULTIPLIER))


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

        # 유물은 판매 가능 종류가 바뀌더라도 절대로 판매되지 않도록 먼저 차단한다.
        if item.get("kind") == "relic":
            await interaction.response.send_message(
                "❌ 유물은 판매할 수 없어.",
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

        unit_price = get_adventure_sell_unit_price(item)
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

        unit_price = get_adventure_sell_unit_price(item)

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

            # 유물은 판매 종류 설정과 무관하게 전체판매에서 무조건 제외한다.
            if item.get("kind") == "relic":
                continue

            # 장비 및 기타 비판매 품목도 제외한다.
            if item.get("kind") not in ADVENTURE_SELLABLE_KINDS:
                continue

            unit_price = get_adventure_sell_unit_price(item)
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

@bot.tree.command(
    name="장비압수",
    description="유저의 사냥 또는 모험 장비를 압수한다",
    guild=GUILD
)
@app_commands.describe(
    대상="장비를 압수할 유저",
    구분="사냥 장비인지 모험 장비인지 선택",
    장비="압수할 장비 이름"
)
@app_commands.choices(
    구분=[
        app_commands.Choice(name="사냥", value="hunt"),
        app_commands.Choice(name="모험", value="adventure"),
    ]
)
@app_commands.default_permissions(administrator=True)
async def confiscate_equipment(
    interaction: discord.Interaction,
    대상: discord.Member,
    구분: app_commands.Choice[str],
    장비: str
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ 관리자만 사용할 수 있어.",
            ephemeral=True
        )
        return

    uid = str(대상.id)
    equipment_name = 장비.strip()
    mode = 구분.value

    if equipment_name in {"무인검", "모험가 세트"}:
        await interaction.response.send_message(
            "❌ 기본 장비는 압수할 수 없어.",
            ephemeral=True
        )
        return

    if equipment_name in WEAPONS:
        equipment_type = "무기"
        equipped_key = "weapon"
        owned_key = "owned_weapons"
        default_equipment = "무인검"
    elif equipment_name in ARMORS:
        equipment_type = "갑옷"
        equipped_key = "armor"
        owned_key = "owned_armors"
        default_equipment = "모험가 세트"
    else:
        await interaction.response.send_message(
            "❌ 존재하지 않는 장비 이름이야.",
            ephemeral=True
        )
        return

    if mode == "hunt":
        user_data = get_hunt_user(uid)
        mode_name = "사냥"
    else:
        user_data = get_adventure(uid)
        mode_name = "모험"

    owned_list = user_data.get(owned_key, [])
    if not isinstance(owned_list, list):
        owned_list = []

    is_equipped = user_data.get(equipped_key) == equipment_name
    is_owned = equipment_name in owned_list

    if not is_owned and not is_equipped:
        await interaction.response.send_message(
            f"❌ {대상.mention}은(는) {mode_name}에서 "
            f"**{equipment_name}**을(를) 보유하고 있지 않아.",
            ephemeral=True
        )
        return

    user_data[owned_key] = [
        name for name in owned_list
        if name != equipment_name
    ]

    # 장착 중인 장비를 압수하면 즉시 기본 장비로 교체한다.
    if is_equipped:
        user_data[equipped_key] = default_equipment

    # 기본 장비는 어떤 경우에도 보유 목록에서 사라지지 않게 한다.
    if default_equipment not in user_data[owned_key]:
        user_data[owned_key].insert(0, default_equipment)

    save_data()

    message = (
        f"🔨 {대상.mention}의 {mode_name} {equipment_type} "
        f"**{equipment_name}**을(를) 압수했어."
    )
    if is_equipped:
        message += f"\n장착 장비는 **{default_equipment}**으로 변경됐어."

    await interaction.response.send_message(message)


@confiscate_equipment.autocomplete("장비")
async def confiscate_equipment_autocomplete(
    interaction: discord.Interaction,
    current: str
):
    target = getattr(interaction.namespace, "대상", None)
    mode = getattr(interaction.namespace, "구분", None)

    if isinstance(mode, app_commands.Choice):
        mode = mode.value

    target_id = getattr(target, "id", None)
    if target_id is None or mode not in {"hunt", "adventure"}:
        return []

    if mode == "hunt":
        user_data = get_hunt_user(target_id)
    else:
        user_data = get_adventure(target_id)

    equipment_names = []
    equipment_names.extend(user_data.get("owned_weapons", []))
    equipment_names.extend(user_data.get("owned_armors", []))

    # 손상된 구버전 데이터에서도 현재 장착 장비를 찾을 수 있게 포함한다.
    equipment_names.extend([
        user_data.get("weapon"),
        user_data.get("armor"),
    ])

    equipment_names = list(dict.fromkeys(
        name for name in equipment_names
        if isinstance(name, str)
    ))
    equipment_names = [
        name for name in equipment_names
        if name not in {"무인검", "모험가 세트"}
        and (name in WEAPONS or name in ARMORS)
    ]

    current = current.strip().lower()
    return [
        app_commands.Choice(name=name[:100], value=name)
        for name in equipment_names
        if current in name.lower()
    ][:25]

# =========================================================
# 파티 모험 시스템 (기존 개인 /모험과 완전히 분리된 로그라이크 모드)
# =========================================================

# 파티 모집 글을 올릴 채널 ID.
# 0으로 두면 /파티생성을 사용한 채널에 모집 글이 올라간다.
PARTY_RECRUIT_CHANNEL_ID = 0
PARTY_DATA_FILE = "/data/party_adventures.json"
PARTY_MAX_HUMANS = 4
PARTY_TOTAL_SLOTS = 4
PARTY_CAMP_INTERVAL = 5
PARTY_REST_COOLDOWN_TURNS = 10
PARTY_BOSS_INTERVAL = 10
PARTY_BALANCE_VERSION = 4
PARTY_EXPLORE_WAIT_MIN = 2
PARTY_EXPLORE_WAIT_MAX = 5
PARTY_BATTLE_SAFE_TURNS = 1
PARTY_LEVEL_SYSTEM_VERSION = 1
PARTY_BOT_STORAGE_CHANCE = 0.30
PARTY_TOKEN_NAME = "원정 인장"

# 파티 모험에서만 사용되는 판별 유물. 획득 즉시 파티 전체에 적용되고 한 판이 끝나면 사라진다.
PARTY_RELICS = {
    "전쟁의 깃발": {
        "emoji": "🚩",
        "desc": "파티 전체 공격력 +6%",
        "bonus": {"attack_pct": 0.06},
    },
    "수호자의 심장": {
        "emoji": "💚",
        "desc": "파티 전체 최대 체력 +8%",
        "bonus": {"hp_pct": 0.08},
    },
    "강철 파편": {
        "emoji": "🔩",
        "desc": "파티 전체 방어력 +5%p",
        "bonus": {"defense_flat": 5.0},
    },
    "붉은 송곳니": {
        "emoji": "🦷",
        "desc": "파티 전체 치명타 확률 +5%p",
        "bonus": {"crit_flat": 0.05},
    },
    "바람의 깃털": {
        "emoji": "🪶",
        "desc": "파티 전체 회피 확률 +4%p",
        "bonus": {"dodge_flat": 0.04},
    },
    "은빛 나침반": {
        "emoji": "🧭",
        "desc": "전투에서 얻는 공용 모라 +12%",
        "bonus": {"reward_pct": 0.12},
    },
    "행운의 토끼발": {
        "emoji": "🐇",
        "desc": "장비 발견 확률 +7%p",
        "bonus": {"equipment_rate": 0.07},
    },
    "낡은 상인 장부": {
        "emoji": "📒",
        "desc": "상인 장비 가격 12% 할인",
        "bonus": {"merchant_discount": 0.12},
    },
    "잔불 부적": {
        "emoji": "🔥",
        "desc": "전투 승리 후 생존자 체력 5% 회복",
        "bonus": {"after_battle_heal": 0.05},
    },
    "풍요의 주머니": {
        "emoji": "🎒",
        "desc": "탐험 중 재료를 발견하면 획득량 +1묶음",
        "bonus": {"material_bonus": 1},
    },
}

PARTY_JOB_INFO = {
    "전사": {
        "emoji": "⚔️",
        "desc": "높은 공격력. 직업 스킬로 강력한 일격을 가한다.",
        "attack_mul": 1.18,
        "hp_mul": 1.05,
    },
    "수호자": {
        "emoji": "🛡️",
        "desc": "높은 체력과 방어력. 직업 스킬로 파티 전체를 보호한다.",
        "attack_mul": 0.88,
        "hp_mul": 1.35,
    },
    "궁수": {
        "emoji": "🏹",
        "desc": "치명타 특화. 직업 스킬은 높은 확률로 치명타가 발생한다.",
        "attack_mul": 1.08,
        "hp_mul": 0.95,
    },
    "도적": {
        "emoji": "🗡️",
        "desc": "회피와 연속 공격 특화. 직업 스킬로 모라를 훔칠 수 있다.",
        "attack_mul": 1.02,
        "hp_mul": 0.92,
    },
    "마법사": {
        "emoji": "🔮",
        "desc": "강한 마법 공격. 직업 스킬로 적의 공격력도 약화한다.",
        "attack_mul": 1.14,
        "hp_mul": 0.88,
    },
    "사제": {
        "emoji": "✨",
        "desc": "회복 특화. 직업 스킬로 가장 위급한 파티원을 치료한다.",
        "attack_mul": 0.78,
        "hp_mul": 1.02,
    },
}

PARTY_BASIC_WEAPON = "무인검"
PARTY_BASIC_ARMOR = "모험가 세트"
PARTY_NORMAL_WEAPON_CAP = WEAPONS.get("용사의 성검", {}).get("bonus", 270)
PARTY_NORMAL_ARMOR_CAP = ARMORS.get("용사의 갑옷", {}).get("bonus", 200)

# 외곽 이후에만 상인/보상 풀에 들어가는 장비의 최소 지형 깊이.
PARTY_SPECIAL_EQUIPMENT_DEPTH = {
    "홍련의 신검": 7,
    "폭풍의 신검": 7,
    "심해신의 예복": 7,
    "대지신의 갑주": 7,
    "종말의 마검": 8,
    "P90": 9,
    "AK12": 9,
    "MINIGUN": 9,
}

PARTY_MATERIALS = [
    "짐승 고기", "버섯", "달콤달콤꽃", "새알", "생선", "밀",
    "당근", "감자", "소금", "향신료", "사과", "양배추",
]

PARTY_RECIPES = {
    "야채 수프": {
        "ingredients": {"버섯": 1, "당근": 1, "감자": 1},
        "desc": "모든 생존자의 체력을 최대 체력의 25% 회복한다.",
        "effect": "heal",
        "value": 0.25,
    },
    "고기 스튜": {
        "ingredients": {"짐승 고기": 2, "감자": 1},
        "desc": "모든 생존자의 체력을 최대 체력의 40% 회복한다.",
        "effect": "heal",
        "value": 0.40,
    },
    "생선 꼬치": {
        "ingredients": {"생선": 2, "소금": 1},
        "desc": "다음 2번의 전투 동안 파티 공격력이 15% 증가한다.",
        "effect": "attack_battles",
        "value": 2,
    },
    "매운 고기볶음": {
        "ingredients": {"짐승 고기": 1, "향신료": 1, "양배추": 1},
        "desc": "다음 전투 동안 파티 공격력이 30% 증가한다.",
        "effect": "attack_strong",
        "value": 1,
    },
    "수호자의 스튜": {
        "ingredients": {"짐승 고기": 1, "버섯": 1, "감자": 1},
        "desc": "다음 전투 동안 받는 피해가 20% 감소한다.",
        "effect": "defense_battles",
        "value": 1,
    },
    "새알 볶음밥": {
        "ingredients": {"새알": 2, "밀": 1},
        "desc": "요리한 사람의 체력을 전부 회복한다.",
        "effect": "self_full_heal",
        "value": 1,
    },
}

# 지형마다 별도의 이벤트를 둔다. choice의 kind를 공통 처리 함수가 해석한다.
PARTY_TERRAIN_EVENTS = {
    "desert": [
        {
            "id": "desert_oasis",
            "name": "신기루 속 오아시스",
            "description": "뜨거운 모래바람 너머에서 맑은 물소리가 들린다.",
            "choices": [
                {"label": "물을 마신다", "emoji": "💧", "kind": "heal"},
                {"label": "샘물을 담는다", "emoji": "🫙", "kind": "materials"},
            ],
        },
        {
            "id": "desert_ruins",
            "name": "모래에 묻힌 고대 유적",
            "description": "반쯤 무너진 문 아래에서 오래된 금속빛이 번뜩인다.",
            "choices": [
                {"label": "안쪽을 뒤진다", "emoji": "🏺", "kind": "risky_equipment"},
                {"label": "안전한 잔해만 챙긴다", "emoji": "🪙", "kind": "coins"},
            ],
        },
    ],
    "grassland": [
        {
            "id": "grass_hilichurl",
            "name": "츄츄족의 캠프",
            "description": "작은 츄츄족 캠프에서 연기와 고기 냄새가 피어오른다.",
            "choices": [
                {"label": "캠프를 약탈한다", "emoji": "🔥", "kind": "raid"},
                {"label": "조심스럽게 말을 건다", "emoji": "👋", "kind": "talk"},
            ],
        },
        {
            "id": "grass_fountain",
            "name": "생명의 샘",
            "description": "초원 한가운데 작은 샘이 푸른빛을 내며 솟아오른다.",
            "choices": [
                {"label": "샘에서 휴식한다", "emoji": "💚", "kind": "heal_big"},
                {"label": "샘 주변을 조사한다", "emoji": "🔎", "kind": "equipment_low"},
            ],
        },
    ],
    "jungle": [
        {
            "id": "jungle_fruit",
            "name": "빛나는 열매",
            "description": "정글 깊은 곳에서 정체불명의 열매가 은은하게 빛난다.",
            "choices": [
                {"label": "먹어 본다", "emoji": "🍈", "kind": "risky_heal"},
                {"label": "재료로 챙긴다", "emoji": "🎒", "kind": "materials"},
            ],
        },
        {
            "id": "jungle_shrine",
            "name": "덩굴에 잠긴 사당",
            "description": "오래된 사당의 제단 위에 봉인된 상자가 놓여 있다.",
            "choices": [
                {"label": "봉인을 푼다", "emoji": "🔓", "kind": "risky_equipment"},
                {"label": "제단에 공물을 둔다", "emoji": "🙏", "kind": "blessing"},
            ],
        },
    ],
    "cave": [
        {
            "id": "cave_ore",
            "name": "거대한 광맥",
            "description": "벽면을 가득 채운 광석이 횃불 빛을 반사한다.",
            "choices": [
                {"label": "깊게 채굴한다", "emoji": "⛏️", "kind": "risky_coins"},
                {"label": "표면만 채굴한다", "emoji": "🪨", "kind": "coins"},
            ],
        },
        {
            "id": "cave_adventurer",
            "name": "길을 잃은 모험가",
            "description": "부상당한 모험가가 바위에 기대어 도움을 요청한다.",
            "choices": [
                {"label": "치료해 준다", "emoji": "🩹", "kind": "help"},
                {"label": "가진 정보를 산다", "emoji": "🗺️", "kind": "merchant_hint"},
            ],
        },
    ],
    "mountain": [
        {
            "id": "mountain_shrine",
            "name": "바람의 제단",
            "description": "절벽 끝 제단에서 강한 바람과 함께 오래된 목소리가 들린다.",
            "choices": [
                {"label": "시련을 받는다", "emoji": "🌪️", "kind": "risky_equipment"},
                {"label": "기도한다", "emoji": "🕯️", "kind": "blessing"},
            ],
        },
        {
            "id": "mountain_nest",
            "name": "거대 독수리의 둥지",
            "description": "둥지 안쪽에 반짝이는 장비와 식재료가 쌓여 있다.",
            "choices": [
                {"label": "빠르게 훔친다", "emoji": "🪶", "kind": "raid"},
                {"label": "주변의 재료만 줍는다", "emoji": "🥚", "kind": "materials"},
            ],
        },
    ],
    "ice": [
        {
            "id": "ice_lake",
            "name": "얼어붙은 호수",
            "description": "투명한 얼음 아래에서 보물상자 같은 형체가 보인다.",
            "choices": [
                {"label": "얼음을 깨고 꺼낸다", "emoji": "🧊", "kind": "risky_equipment"},
                {"label": "낚시만 한다", "emoji": "🎣", "kind": "materials"},
            ],
        },
        {
            "id": "ice_camp",
            "name": "버려진 우인단 보급소",
            "description": "급히 철수한 흔적과 함께 보급 상자가 남아 있다.",
            "choices": [
                {"label": "보급품을 챙긴다", "emoji": "📦", "kind": "equipment_low"},
                {"label": "문서를 조사한다", "emoji": "📜", "kind": "blessing"},
            ],
        },
    ],
    "demon": [
        {
            "id": "demon_altar",
            "name": "피로 물든 제단",
            "description": "제단은 힘을 약속하며 생명력을 요구한다.",
            "choices": [
                {"label": "대가를 치른다", "emoji": "🩸", "kind": "sacrifice"},
                {"label": "제단을 부순다", "emoji": "💥", "kind": "battle"},
            ],
        },
        {
            "id": "demon_market",
            "name": "마계의 암시장",
            "description": "정체를 숨긴 상인들이 금지된 장비를 거래하고 있다.",
            "choices": [
                {"label": "거래한다", "emoji": "🕶️", "kind": "merchant"},
                {"label": "상인을 협박한다", "emoji": "😈", "kind": "raid"},
            ],
        },
    ],
    "heaven": [
        {
            "id": "heaven_garden",
            "name": "천상의 정원",
            "description": "빛으로 이루어진 꽃이 파티의 상처를 어루만진다.",
            "choices": [
                {"label": "꽃밭에서 쉰다", "emoji": "🌼", "kind": "heal_big"},
                {"label": "빛의 씨앗을 챙긴다", "emoji": "✨", "kind": "blessing"},
            ],
        },
        {
            "id": "heaven_trial",
            "name": "천상의 무기고",
            "description": "수호 조각상이 길을 막고 뒤편에는 강력한 장비가 보인다.",
            "choices": [
                {"label": "수호자에게 도전한다", "emoji": "⚔️", "kind": "battle_elite"},
                {"label": "조용히 물러난다", "emoji": "🪽", "kind": "coins"},
            ],
        },
    ],
    "outskirts": [
        {
            "id": "outskirts_rift",
            "name": "원소 균열",
            "description": "세계 바깥의 힘이 균열 사이로 흘러나온다.",
            "choices": [
                {"label": "균열에 손을 뻗는다", "emoji": "🌌", "kind": "special_equipment"},
                {"label": "균열을 봉인한다", "emoji": "🔒", "kind": "blessing"},
            ],
        },
    ],
    "glitch": [
        {
            "id": "glitch_cache",
            "name": "깨진 데이터 저장소",
            "description": "읽을 수 없는 글자 사이로 비정상적인 장비 데이터가 떠다닌다.",
            "choices": [
                {"label": "데이터를 복구한다", "emoji": "💾", "kind": "special_equipment"},
                {"label": "삭제한다", "emoji": "🗑️", "kind": "coins_big"},
            ],
        },
    ],
    "lab17": [
        {
            "id": "lab_armory",
            "name": "17번 연구소 무기고",
            "description": "전자 잠금장치 뒤에 현대식 화기가 정렬되어 있다.",
            "choices": [
                {"label": "잠금장치를 해킹한다", "emoji": "⌨️", "kind": "special_equipment"},
                {"label": "폭파하고 진입한다", "emoji": "💣", "kind": "battle_elite"},
            ],
        },
    ],
}

party_data = {"parties": {}, "next_id": 1}
party_locks = {}
party_registered_view_keys = set()


def load_party_data():
    global party_data
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(PARTY_DATA_FILE):
        party_data = {"parties": {}, "next_id": 1}
        return
    try:
        with open(PARTY_DATA_FILE, "r", encoding="utf-8") as file:
            loaded = json.load(file)
        if not isinstance(loaded, dict):
            loaded = {}
        loaded.setdefault("parties", {})
        loaded.setdefault("next_id", 1)
        party_data = loaded
    except (OSError, json.JSONDecodeError) as error:
        print(f"파티 데이터 로드 실패: {error}")
        party_data = {"parties": {}, "next_id": 1}


def save_party_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    temp_path = PARTY_DATA_FILE + ".tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(party_data, file, ensure_ascii=False, indent=2)
        os.replace(temp_path, PARTY_DATA_FILE)
    except OSError as error:
        print(f"파티 데이터 저장 실패: {error}")


load_party_data()


def get_party_profile(uid):
    uid = str(uid)
    if uid not in party_profiles or not isinstance(party_profiles[uid], dict):
        party_profiles[uid] = {}
    profile = party_profiles[uid]
    defaults = {
        "tokens": 0,
        "runs": 0,
        "clears": 0,
        "hard_clears": 0,
        "boss_kills": 0,
        "total_turns": 0,
        "best_depth": 0,
        "first_clear_rewarded": False,
        "titles": [],
    }
    for key, value in defaults.items():
        if key not in profile:
            profile[key] = value.copy() if isinstance(value, list) else value
    for key in ("tokens", "runs", "clears", "hard_clears", "boss_kills", "total_turns", "best_depth"):
        profile[key] = max(0, int(profile.get(key, 0)))
    profile["first_clear_rewarded"] = bool(profile.get("first_clear_rewarded", False))
    if not isinstance(profile.get("titles"), list):
        profile["titles"] = []
    profile["titles"] = list(dict.fromkeys(str(title) for title in profile["titles"]))
    return profile


def grant_party_permanent_rewards(party, victory=False, voluntary=False):
    run = party.get("run") or {}
    if run.get("permanent_rewards_granted"):
        return str(run.get("permanent_reward_summary", ""))

    humans = party_human_members(party)
    if not humans:
        run["permanent_rewards_granted"] = True
        run["permanent_reward_summary"] = "영구 보상을 받을 실제 유저가 없었어."
        save_party_data()
        return run["permanent_reward_summary"]

    turns = max(0, int(run.get("turn", 0)))
    bosses = max(0, int(run.get("boss_kills", 0)))
    depth = ADVENTURE_TERRAIN_DEPTH.get(run.get("terrain"), 1)
    token_base = max(5, turns * 2 + bosses * 15 + depth * 10)
    if victory:
        token_base += 100
    elif voluntary:
        token_base = max(5, int(token_base * 0.45))
    else:
        token_base = max(5, int(token_base * 0.65))
    if party.get("hard_mode"):
        token_base = int(token_base * 1.4)

    mora_rate = 0.50 if victory else (0.15 if voluntary else 0.25)
    mora_each = int(int(run.get("coins", 0)) * mora_rate / max(1, len(humans)))
    reward_lines = []

    for uid in humans:
        profile = get_party_profile(uid)
        profile["tokens"] += token_base
        profile["runs"] += 1
        profile["boss_kills"] += bosses
        profile["total_turns"] += turns
        profile["best_depth"] = max(profile["best_depth"], depth)
        first_clear_gems = 0
        if victory:
            profile["clears"] += 1
            if party.get("hard_mode"):
                profile["hard_clears"] += 1
            if not profile["first_clear_rewarded"]:
                profile["first_clear_rewarded"] = True
                first_clear_gems = 160
                add_primogems(uid, first_clear_gems)
        if mora_each > 0:
            add_poker_money(uid, mora_each)
        reward_lines.append(
            f"<@{uid}> · {PARTY_TOKEN_NAME} **+{token_base}** · 모라 **+{mora_each:,}**"
            + (f" · 첫 완주 원석 **+{first_clear_gems}**" if first_clear_gems else "")
        )

    run["permanent_rewards_granted"] = True
    run["permanent_reward_summary"] = "\n".join(reward_lines)
    save_data()
    save_party_data()
    return run["permanent_reward_summary"]


def get_party_lock(party_id):
    party_id = str(party_id)
    if party_id not in party_locks:
        party_locks[party_id] = asyncio.Lock()
    return party_locks[party_id]


def next_party_id():
    number = max(1, int(party_data.get("next_id", 1)))
    party_data["next_id"] = number + 1
    return f"P{number:04d}"


def get_party(party_id):
    return party_data.get("parties", {}).get(str(party_id))


def find_user_party(user_id):
    uid = str(user_id)
    for party in party_data.get("parties", {}).values():
        if party.get("status") not in {"lobby", "playing"}:
            continue
        if uid in party.get("members", []):
            return party
    return None


def party_human_members(party):
    return [str(uid) for uid in party.get("members", [])]


def party_alive_human_ids(party):
    run = party.get("run") or {}
    result = []
    for uid in party_human_members(party):
        player = run.get("players", {}).get(uid)
        if player and player.get("alive"):
            result.append(uid)
    return result


def get_party_member_name(guild, uid):
    uid = str(uid)
    try:
        member = guild.get_member(int(uid)) if guild else None
    except ValueError:
        member = None
    if member:
        return member.display_name
    return f"유저 {uid[-4:]}"


def get_party_member_level(uid):
    try:
        return max(1, int(get_level_data(int(uid)).get("level", 1)))
    except (ValueError, TypeError):
        return 1


def get_party_thread(party):
    guild = bot.get_guild(int(party.get("guild_id", 0)))
    if not guild:
        return None
    return guild.get_thread(int(party.get("thread_id", 0)))


def get_party_recruit_channel(party):
    guild = bot.get_guild(int(party.get("guild_id", 0)))
    if not guild:
        return None
    return guild.get_channel(int(party.get("recruit_channel_id", 0)))


def get_terrain_display(terrain_key):
    info = ADVENTURE_TERRAINS.get(terrain_key, {})
    return f"{info.get('emoji', '🗺️')} {info.get('name', terrain_key)}"


def party_job_text(job):
    info = PARTY_JOB_INFO.get(job, {})
    return f"{info.get('emoji', '🎭')} {job}"


def build_party_recruit_embed(party):
    guild = bot.get_guild(int(party.get("guild_id", 0)))
    members = party_human_members(party)
    member_lines = []
    for index, uid in enumerate(members, start=1):
        job = party.get("jobs", {}).get(uid, "미선택")
        crown = "👑 " if uid == str(party.get("leader_id")) else ""
        member_lines.append(
            f"{index}. {crown}<@{uid}> · "
            + (party_job_text(job) if job in PARTY_JOB_INFO else "🎭 직업 미선택")
        )
    while len(member_lines) < PARTY_MAX_HUMANS:
        member_lines.append(f"{len(member_lines) + 1}. `빈자리`")

    status = party.get("status", "lobby")
    if status == "lobby":
        status_text = "🟢 모집 중"
    elif status == "playing":
        status_text = "⚔️ 모험 진행 중"
    elif status == "completed":
        status_text = "🏆 모험 완료"
    elif status == "failed":
        status_text = "☠️ 전멸"
    elif status == "abandoned":
        status_text = "🏳️ 중도 종료"
    else:
        status_text = "🔒 모집 종료"

    thread_text = f"<#{party.get('thread_id')}>" if party.get("thread_id") else "생성 중"

    embed = discord.Embed(
        title=f"🧭 파티 모험 모집 · {party.get('name', party.get('id'))}",
        description=(
            f"상태: **{status_text}**\n"
            f"모드: **{'🔥 하드' if party.get('hard_mode') else '일반'}**\n"
            f"시작 지형: **{get_terrain_display(party.get('start_terrain', 'grassland'))}**\n"
            f"파티 스레드: {thread_text}\n\n"
            + "\n".join(member_lines)
            + "\n\n빈자리가 남은 채 시작하면 NPC 용병이 자동으로 채워져.\n원정 레벨·장비·유물은 판이 끝나면 사라지고, 원정 인장과 정산 모라는 영구 지급돼."
        ),
        color=discord.Color.red() if party.get("hard_mode") else discord.Color.blurple(),
    )
    embed.set_footer(text=f"파티 ID {party.get('id')} · 최대 유저 4명")
    return embed


def build_party_lobby_embed(party):
    guild = bot.get_guild(int(party.get("guild_id", 0)))
    lines = []
    for uid in party_human_members(party):
        name = get_party_member_name(guild, uid)
        job = party.get("jobs", {}).get(uid)
        leader = "👑 " if uid == str(party.get("leader_id")) else ""
        job_text = party_job_text(job) if job in PARTY_JOB_INFO else "🎭 미선택"
        lines.append(f"{leader}**{name}** · 원정 Lv.1 시작 · {job_text}")

    missing = PARTY_TOTAL_SLOTS - len(lines)
    if missing > 0:
        lines.append(f"\n🤖 시작 시 NPC 용병 **{missing}명** 자동 합류")

    jobs_text = "\n".join(
        f"{info['emoji']} **{name}** — {info['desc']}"
        for name, info in PARTY_JOB_INFO.items()
    )

    embed = discord.Embed(
        title=f"🏕️ {party.get('name')} 파티 대기실",
        description=(
            f"파티장: <@{party.get('leader_id')}>\n"
            f"난이도: **{'🔥 하드 모드' if party.get('hard_mode') else '일반 모드'}**\n"
            f"시작 지형: **{get_terrain_display(party.get('start_terrain', 'grassland'))}**\n\n"
            "## 현재 파티원\n"
            + "\n".join(lines)
            + "\n\n## 직업 6종\n"
            + jobs_text
        ),
        color=discord.Color.dark_teal(),
    )
    embed.set_footer(text="원정 레벨·장비·유물은 이번 판 전용이며 종료 시 초기화돼. 대신 원정 인장과 일부 모라는 영구 지급돼.")
    return embed


def party_get_player(party, uid):
    run = party.get("run") or {}
    return run.get("players", {}).get(str(uid))


def party_player_equipment_bonus(player):
    weapon = player.get("weapon", PARTY_BASIC_WEAPON)
    armor = player.get("armor", PARTY_BASIC_ARMOR)
    weapon_bonus = int(WEAPONS.get(weapon, WEAPONS[PARTY_BASIC_WEAPON]).get("bonus", 0))
    armor_bonus = int(ARMORS.get(armor, ARMORS[PARTY_BASIC_ARMOR]).get("bonus", 0))
    return weapon_bonus, armor_bonus


def party_player_stats(player, run=None):
    level = max(1, int(player.get("level", 1)))
    job = player.get("job", "전사")
    job_info = PARTY_JOB_INFO.get(job, PARTY_JOB_INFO["전사"])
    weapon_bonus, armor_bonus = party_player_equipment_bonus(player)

    rookie_mul = 1.15 if level <= 20 else 1.0
    attack = (16 + level * 2.4 + weapon_bonus * 0.38) * job_info["attack_mul"] * rookie_mul
    max_hp = (95 + level * 5.2 + armor_bonus * 0.85) * job_info["hp_mul"] * rookie_mul
    defense = min(72.0, 4.0 + armor_bonus * 0.18)
    crit = 0.08
    dodge = 0.03

    if job == "수호자":
        defense += 12
    elif job == "궁수":
        crit += 0.20
    elif job == "도적":
        dodge += 0.16
    elif job == "마법사":
        attack *= 1.06
    elif job == "사제":
        defense += 4

    if run:
        buffs = run.get("buffs", {})
        if int(buffs.get("attack_battles", 0)) > 0:
            attack *= 1.15
        if int(buffs.get("attack_strong", 0)) > 0:
            attack *= 1.30

        relic_bonuses = get_party_relic_bonuses(run)
        attack *= 1.0 + float(relic_bonuses.get("attack_pct", 0.0))
        max_hp *= 1.0 + float(relic_bonuses.get("hp_pct", 0.0))
        defense += float(relic_bonuses.get("defense_flat", 0.0))
        crit += float(relic_bonuses.get("crit_flat", 0.0))
        dodge += float(relic_bonuses.get("dodge_flat", 0.0))

    return {
        "attack": max(1, int(round(attack))),
        "max_hp": max(1, int(round(max_hp))),
        "defense": max(0.0, min(80.0, defense)),
        "crit": max(0.0, min(0.75, crit)),
        "dodge": max(0.0, min(0.70, dodge)),
    }


def refresh_party_player_max_hp(player, run=None, keep_ratio=True):
    old_max = max(1, int(player.get("max_hp", 1)))
    old_hp = max(0, int(player.get("hp", old_max)))
    ratio = old_hp / old_max if keep_ratio else 1.0
    stats = party_player_stats(player, run)
    player["max_hp"] = stats["max_hp"]
    player["hp"] = min(player["max_hp"], max(0, int(round(player["max_hp"] * ratio))))


def build_party_status_lines(party):
    run = party.get("run") or {}
    lines = []
    for key, player in run.get("players", {}).items():
        alive = bool(player.get("alive"))
        hp = max(0, int(player.get("hp", 0)))
        max_hp = max(1, int(player.get("max_hp", 1)))
        marker = "🤖" if player.get("is_bot") else "👤"
        state = f"❤️ {hp}/{max_hp}" if alive else "💀 관전 중"
        level = max(1, int(player.get("level", 1)))
        exp = max(0, int(player.get("party_exp", 0)))
        need_exp = party_level_exp_required(level)
        rookie = " · 🌱 초보자 강화 +15%" if level <= 20 else ""
        lines.append(
            f"{marker} **{player.get('name')}** · 원정 Lv.{level} ({exp}/{need_exp} EXP) · "
            f"{party_job_text(player.get('job', '전사'))} · {state}{rookie}\n"
            f"└ 🗡️ [원정] {player.get('weapon')} / 🛡️ [원정] {player.get('armor')}"
        )
    return lines


def build_party_explore_embed(party, result_text=None):
    run = party.get("run") or {}
    terrain = run.get("terrain", party.get("start_terrain", "grassland"))
    info = ADVENTURE_TERRAINS.get(terrain, {})
    description = (
        f"현재 지형: **{get_terrain_display(terrain)}**\n"
        f"완료 턴: **{run.get('turn', 0)}턴**\n"
        f"공용 모라: **{int(run.get('coins', 0)):,}모라**\n"
        f"난이도: **{'🔥 하드' if party.get('hard_mode') else '일반'}**\n\n"
    )
    if result_text:
        description += f"{result_text}\n\n"

    relics = run.get("relics", [])
    relic_text = ", ".join(
        f"{PARTY_RELICS.get(name, {}).get('emoji', '✨')} {name}" for name in relics
    ) or "아직 발견한 유물 없음"
    battle_rate = get_party_battle_spawn_rate(party) * 100
    safe_text = " · 전투 직후 안전 구간" if int(run.get("battle_safe_turns", 0)) > 0 else ""
    end_votes = [uid for uid in run.get("end_votes", []) if uid in party_human_members(party)]
    end_needed = party_end_vote_needed(party)
    description += (
        f"## 이번 판 유물\n{relic_text}\n\n"
        f"다음 탐험 몬스터 조우 확률: **{battle_rate:.0f}%**{safe_text}\n"
        f"종료 투표: **{len(end_votes)}/{end_needed}표** · `/파티종료`\n\n"
        "## 파티 상태\n" + "\n".join(build_party_status_lines(party))
    )
    embed = discord.Embed(
        title=f"🧭 파티 모험 · {party.get('name')}",
        description=description,
        color=int(info.get("color", 0x5865F2)),
    )
    embed.set_footer(text="탐험에는 2~5초가 걸리며 전투·유물·장비·재료·상인·지형 이벤트가 무작위로 발생해.")
    return embed


def build_party_battle_embed(party):
    run = party.get("run") or {}
    battle = run.get("battle") or {}
    monster = battle.get("monster") or {}
    monster_hp = max(0, int(monster.get("hp", 0)))
    monster_max_hp = max(1, int(monster.get("max_hp", 1)))

    action_lines = []
    actions = battle.get("actions", {})
    for uid in party_alive_human_ids(party):
        player = party_get_player(party, uid)
        action = actions.get(uid)
        action_lines.append(
            f"{'✅' if action else '⏳'} **{player.get('name')}** — {action or '행동 대기'}"
        )

    logs = battle.get("log", [])[-10:]
    log_text = "\n".join(logs) if logs else "전투가 시작됐다. 행동을 선택해!"
    scale = float(monster.get("member_scale", 1.0))
    embed = discord.Embed(
        title=f"⚔️ {monster.get('name', '몬스터')} 전투 · 라운드 {battle.get('round', 1)}",
        description=(
            f"👹 **Lv.{monster.get('level', 1)} {monster.get('name', '몬스터')}**\n"
            f"❤️ 체력: **{monster_hp:,}/{monster_max_hp:,}**\n"
            f"💥 공격력: **{int(monster.get('attack', 1)):,}**\n"
            f"📈 파티 인원 난이도 배율: **×{scale:.2f}**\n\n"
            "## 행동 선택\n"
            + ("\n".join(action_lines) if action_lines else "생존한 유저 파티원이 없어.")
            + "\n\n## 전투 기록\n"
            + log_text
            + "\n\n## 파티 상태\n"
            + "\n".join(build_party_status_lines(party))
        ),
        color=discord.Color.red(),
    )
    embed.set_footer(text="공격·방어·직업 스킬 중 하나를 선택해. 전원이 선택하면 라운드가 진행돼.")
    return embed


def build_party_event_embed(party):
    run = party.get("run") or {}
    event = get_party_event_by_id(run.get("event_id"))
    votes = run.get("event_votes", {})
    humans = party_human_members(party)
    vote_lines = []
    for uid in humans:
        choice_index = votes.get(uid)
        if choice_index is None:
            vote_lines.append(f"⏳ <@{uid}> — 선택 대기")
        else:
            try:
                label = event["choices"][int(choice_index)]["label"]
            except (IndexError, KeyError, TypeError, ValueError):
                label = "알 수 없음"
            vote_lines.append(f"✅ <@{uid}> — **{label}**")

    embed = discord.Embed(
        title=f"🎭 지형 이벤트 · {event.get('name', '알 수 없는 사건')}",
        description=(
            f"현재 지형: **{get_terrain_display(run.get('terrain'))}**\n\n"
            f"{event.get('description', '')}\n\n"
            "## 파티 투표\n"
            + "\n".join(vote_lines)
            + "\n\n모든 유저 파티원이 투표하면 가장 많은 표를 받은 선택지가 실행돼. "
            "동률이면 파티장의 선택이 우선돼."
        ),
        color=discord.Color.purple(),
    )
    return embed


def build_party_merchant_embed(party):
    run = party.get("run") or {}
    offers = run.get("merchant_offers", [])
    lines = []
    for offer in offers:
        kind_emoji = "🗡️" if offer.get("kind") == "weapon" else "🛡️"
        catalog = WEAPONS if offer.get("kind") == "weapon" else ARMORS
        bonus = int(catalog.get(offer.get("name"), {}).get("bonus", 0))
        lines.append(
            f"{kind_emoji} **{offer.get('name')}** · 보너스 +{bonus} · "
            f"**{int(offer.get('price', 0)):,}모라**"
        )

    embed = discord.Embed(
        title="🛒 떠돌이 상인",
        description=(
            f"상인은 모험의 **{run.get('turn', 0)}턴**과 "
            f"**{get_terrain_display(run.get('terrain'))}**에 맞는 장비를 꺼냈다.\n"
            f"공용 모라: **{int(run.get('coins', 0)):,}모라**\n\n"
            + ("\n".join(lines) if lines else "팔 수 있는 장비가 없어 보인다.")
            + "\n\n구매한 장비는 구매자의 가방에 들어가며, 캠프에서 착용할 수 있어."
        ),
        color=discord.Color.gold(),
    )
    return embed


def build_party_camp_embed(party, notice=None):
    run = party.get("run") or {}
    humans = party_human_members(party)
    votes = [uid for uid in run.get("rest_votes", []) if uid in humans]
    needed = max(1, math.ceil(len(humans) / 2))
    remaining = max(
        0,
        PARTY_REST_COOLDOWN_TURNS - (int(run.get("turn", 0)) - int(run.get("last_rest_turn", -999))),
    )
    storage = run.get("shared_storage", [])
    storage_text = "\n".join(
        f"• {'🗡️' if item.get('kind') == 'weapon' else '🛡️'} {item.get('name')}"
        for item in storage[:12]
    )
    if not storage_text:
        storage_text = "비어 있음"
    if len(storage) > 12:
        storage_text += f"\n외 {len(storage) - 12}개"

    locked_lines = []
    for uid in humans:
        locked = bool(run.get("camp_locked", {}).get(uid))
        locked_lines.append(f"{'🔒' if locked else '✅'} <@{uid}> — {'이번 캠프 휴식 불가' if locked else '휴식 가능'}")

    description = (
        f"**{run.get('turn', 0)}턴**을 마치고 캠프에 도착했다.\n"
        "전투에서 쓰러진 파티원은 생명 1로 부활하고, 최대 체력의 50%를 회복했어.\n\n"
    )
    if notice:
        description += f"{notice}\n\n"
    description += (
        f"## 휴식 투표\n"
        f"현재 **{len(votes)}/{needed}표** · "
        + ("지금 휴식 가능" if remaining == 0 else f"다음 휴식까지 {remaining}턴")
        + "\n"
        + "\n".join(locked_lines)
        + "\n\n휴식이 성립하면 전원의 생명 1과 체력이 전부 회복돼. "
        "요리하거나 장비를 공용 보관함에 올린 사람은 이번 캠프에서 휴식 투표를 할 수 없어.\n\n"
        "## 공용 보관함\n"
        + storage_text
        + "\n\n## 파티 상태\n"
        + "\n".join(build_party_status_lines(party))
    )

    embed = discord.Embed(title="🏕️ 파티 캠프", description=description, color=discord.Color.dark_green())
    embed.set_footer(text="캠프에서는 요리·장비 변경·공용 보관함 이용이 가능해.")
    return embed


def build_party_route_embed(party):
    run = party.get("run") or {}
    current = run.get("terrain")
    routes = ADVENTURE_TERRAIN_ROUTES.get(current, [])
    lines = [f"• {get_terrain_display(key)}" for key in routes]
    embed = discord.Embed(
        title="🗺️ 다음 지형 선택",
        description=(
            f"**{get_terrain_display(current)}**의 보스를 쓰러뜨렸다.\n\n"
            + ("\n".join(lines) if lines else "더 이어지는 길이 없다.")
            + "\n\n파티장이 다음 지형을 선택해."
        ),
        color=discord.Color.blue(),
    )
    return embed


def get_party_event_by_id(event_id):
    for events in PARTY_TERRAIN_EVENTS.values():
        for event in events:
            if event.get("id") == event_id:
                return event
    return {
        "id": "unknown",
        "name": "알 수 없는 사건",
        "description": "사건의 흔적이 사라졌다.",
        "choices": [
            {"label": "계속 간다", "emoji": "➡️", "kind": "coins"},
        ],
    }


def get_party_relic_bonuses(run):
    bonuses = {
        "attack_pct": 0.0,
        "hp_pct": 0.0,
        "defense_flat": 0.0,
        "crit_flat": 0.0,
        "dodge_flat": 0.0,
        "reward_pct": 0.0,
        "equipment_rate": 0.0,
        "merchant_discount": 0.0,
        "after_battle_heal": 0.0,
        "material_bonus": 0,
    }
    for relic_name in run.get("relics", []):
        relic = PARTY_RELICS.get(relic_name, {})
        for key, value in relic.get("bonus", {}).items():
            bonuses[key] = bonuses.get(key, 0) + value
    return bonuses


def roll_party_relic(run):
    owned = set(run.get("relics", []))
    candidates = [name for name in PARTY_RELICS if name not in owned]
    if not candidates:
        return None
    relic_name = random.choice(candidates)
    run.setdefault("relics", []).append(relic_name)

    # 최대 체력 유물은 현재 체력 비율을 유지한 채 즉시 반영한다.
    if relic_name == "수호자의 심장":
        for player in run.get("players", {}).values():
            refresh_party_player_max_hp(player, run, keep_ratio=True)
    return relic_name


def format_party_relic(relic_name):
    relic = PARTY_RELICS.get(relic_name, {})
    return f"{relic.get('emoji', '✨')} **{relic_name}** — {relic.get('desc', '알 수 없는 힘')}"


def get_party_battle_spawn_rate(party):
    run = party.get("run") or {}
    if int(run.get("battle_safe_turns", 0)) > 0:
        return 0.0
    base = 0.27 if not party.get("hard_mode") else 0.32
    pity = min(0.24, int(run.get("turns_without_battle", 0)) * 0.07)
    return min(0.60, base + pity)


def build_party_travel_embed(party, wait_seconds):
    run = party.get("run") or {}
    terrain = run.get("terrain", party.get("start_terrain", "grassland"))
    return discord.Embed(
        title="🚶 파티가 탐험 중이야...",
        description=(
            f"현재 지형: **{get_terrain_display(terrain)}**\n"
            f"예상 탐험 시간: **{wait_seconds}초**\n\n"
            "주변을 살피며 천천히 이동하고 있어.\n"
            "몬스터뿐 아니라 유물·장비·재료·상인·지형 사건을 만날 수 있어."
        ),
        color=discord.Color.blurple(),
    )


def get_party_equipment_depth_allowed(name, depth):
    required = PARTY_SPECIAL_EQUIPMENT_DEPTH.get(name)
    if required is None:
        return True
    return depth >= required


def party_equipment_candidates(run, kind, low_tier=False, special_only=False):
    terrain = run.get("terrain", "grassland")
    depth = ADVENTURE_TERRAIN_DEPTH.get(terrain, 1)
    turn = max(1, int(run.get("turn", 1)))
    catalog = WEAPONS if kind == "weapon" else ARMORS
    basic = PARTY_BASIC_WEAPON if kind == "weapon" else PARTY_BASIC_ARMOR
    normal_cap = PARTY_NORMAL_WEAPON_CAP if kind == "weapon" else PARTY_NORMAL_ARMOR_CAP

    # 턴과 지형이 깊어질수록 허용 보너스가 상승한다.
    progress_cap = 8 + turn * 4.5 + depth * 13
    if low_tier:
        progress_cap = max(12, progress_cap * 0.58)
    if depth < ADVENTURE_TERRAIN_DEPTH.get("outskirts", 7):
        progress_cap = min(progress_cap, normal_cap)

    result = []
    for name, info in catalog.items():
        if name == basic:
            continue
        bonus = int(info.get("bonus", 0))
        is_special = bool(info.get("obtain_only")) or name in PARTY_SPECIAL_EQUIPMENT_DEPTH
        if special_only and not is_special:
            continue
        if not special_only and is_special and depth < ADVENTURE_TERRAIN_DEPTH.get("outskirts", 7):
            continue
        if not get_party_equipment_depth_allowed(name, depth):
            continue
        if depth < ADVENTURE_TERRAIN_DEPTH.get("outskirts", 7) and bonus > normal_cap:
            continue
        if bonus <= progress_cap or special_only:
            result.append(name)

    if not result and not special_only:
        fallback = []
        for name, info in catalog.items():
            if name == basic or info.get("obtain_only"):
                continue
            if depth < ADVENTURE_TERRAIN_DEPTH.get("outskirts", 7) and int(info.get("bonus", 0)) > normal_cap:
                continue
            fallback.append(name)
        fallback.sort(key=lambda item_name: int(catalog[item_name].get("bonus", 0)))
        result = fallback[:4]

    result.sort(key=lambda item_name: int(catalog[item_name].get("bonus", 0)))
    return result


def roll_party_equipment(run, low_tier=False, special_only=False):
    kinds = ["weapon", "armor"]
    random.shuffle(kinds)
    for kind in kinds:
        candidates = party_equipment_candidates(run, kind, low_tier=low_tier, special_only=special_only)
        if candidates:
            # 가능한 장비 중 현재 진행도에 가까운 상위 절반에서 뽑는다.
            start = max(0, len(candidates) // 2 - 1)
            name = random.choice(candidates[start:])
            return {"kind": kind, "name": name}
    return None


def party_level_exp_required(level):
    level = max(1, int(level))
    return 50 + (level - 1) * 35


def party_equipment_bonus_value(kind, name):
    catalog = WEAPONS if kind == "weapon" else ARMORS
    return int(catalog.get(name, {}).get("bonus", 0))


def party_bot_equip_best(player, run=None):
    """용병이 가방과 착용 장비를 비교해 가장 강한 장비를 자동 착용한다."""
    if not player or not player.get("is_bot"):
        return []

    changes = []
    for kind, equipped_key, bag_key, basic in [
        ("weapon", "weapon", "bag_weapons", PARTY_BASIC_WEAPON),
        ("armor", "armor", "bag_armors", PARTY_BASIC_ARMOR),
    ]:
        bag = player.setdefault(bag_key, [])
        equipped = player.get(equipped_key, basic)
        candidates = [equipped] + list(bag)
        best = max(candidates, key=lambda name: party_equipment_bonus_value(kind, name))
        if best == equipped:
            continue

        bag.remove(best)
        if equipped != basic:
            bag.append(equipped)
        player[equipped_key] = best
        changes.append({"kind": kind, "name": best, "old": equipped})

    if any(change["kind"] == "armor" for change in changes):
        refresh_party_player_max_hp(player, run, keep_ratio=True)
    return changes


def give_party_equipment_to_player(player, equipment, run=None):
    if not equipment or not player:
        return {"equipped": False, "changes": []}
    if equipment.get("kind") == "weapon":
        player.setdefault("bag_weapons", []).append(equipment.get("name"))
    else:
        player.setdefault("bag_armors", []).append(equipment.get("name"))

    changes = party_bot_equip_best(player, run)
    equipped = any(change.get("name") == equipment.get("name") for change in changes)
    return {"equipped": equipped, "changes": changes}


def party_equipment_receive_suffix(player, equipment, receive_result):
    if player.get("is_bot") and receive_result.get("equipped"):
        return f" **{player.get('name')}**이 성능을 비교한 뒤 바로 착용했다."
    return f" **{player.get('name')}**의 가방에 들어갔다."


def handle_party_bot_camp_actions(run):
    """캠프 도착 시 용병이 장비를 정리하고 30% 확률로 남는 장비 하나를 공유한다."""
    notices = []
    storage = run.setdefault("shared_storage", [])
    for player in run.get("players", {}).values():
        if not player.get("is_bot"):
            continue

        changes = party_bot_equip_best(player, run)
        for change in changes:
            notices.append(f"🤖 **{player.get('name')}**이 **{change.get('name')}**을 자동 착용했다.")

        candidates = []
        for name in player.setdefault("bag_weapons", []):
            candidates.append({"kind": "weapon", "name": name})
        for name in player.setdefault("bag_armors", []):
            candidates.append({"kind": "armor", "name": name})

        if candidates and random.random() < PARTY_BOT_STORAGE_CHANCE:
            item = random.choice(candidates)
            bag_key = "bag_weapons" if item["kind"] == "weapon" else "bag_armors"
            try:
                player[bag_key].remove(item["name"])
            except ValueError:
                continue
            storage.append(item)
            notices.append(
                f"📦 **{player.get('name')}**이 남는 **{item.get('name')}**을 공용 보관함에 올렸다."
            )
    return notices


def grant_party_battle_experience(party):
    run = party.get("run") or {}
    monster = (run.get("battle") or {}).get("monster") or {}
    monster_level = max(1, int(monster.get("level", 1)))
    gained = 28 + monster_level * 7
    if monster.get("is_elite"):
        gained = int(round(gained * 1.45))
    if monster.get("is_boss"):
        gained = int(round(gained * 2.0))
    if party.get("hard_mode"):
        gained = int(round(gained * 1.15))

    gained = apply_fever_multiplier(gained)

    leveled = []
    for player in run.get("players", {}).values():
        player["party_exp"] = max(0, int(player.get("party_exp", 0))) + gained
        old_level = max(1, int(player.get("level", 1)))
        while player["party_exp"] >= party_level_exp_required(player.get("level", 1)):
            need = party_level_exp_required(player.get("level", 1))
            player["party_exp"] -= need
            player["level"] = int(player.get("level", 1)) + 1
        if int(player.get("level", 1)) > old_level:
            refresh_party_player_max_hp(player, run, keep_ratio=True)
            leveled.append(f"{player.get('name')} Lv.{old_level}→Lv.{player.get('level')}")

    text = f"\n⭐ 파티 모험 경험치 **+{gained} EXP**"
    if leveled:
        text += "\n🎉 레벨 업: " + ", ".join(leveled)
    return text


def party_end_vote_needed(party):
    human_count = max(1, len(party_human_members(party)))
    return human_count // 2 + 1


def generate_party_merchant_offers(run):
    offers = []
    used = set()
    depth = ADVENTURE_TERRAIN_DEPTH.get(run.get("terrain"), 1)
    for _ in range(8):
        if len(offers) >= 4:
            break
        equipment = roll_party_equipment(
            run,
            low_tier=False,
            special_only=(depth >= 7 and random.random() < 0.25),
        )
        if not equipment:
            continue
        key = (equipment["kind"], equipment["name"])
        if key in used:
            continue
        used.add(key)
        catalog = WEAPONS if equipment["kind"] == "weapon" else ARMORS
        bonus = int(catalog[equipment["name"]].get("bonus", 0))
        base_price = max(120, int(120 + bonus * 16 + int(run.get("turn", 1)) * 28))
        discount = min(0.50, float(get_party_relic_bonuses(run).get("merchant_discount", 0.0)))
        price = max(80, int(round(base_price * (1.0 - discount))))
        offers.append({
            "id": f"offer_{len(offers)}",
            "kind": equipment["kind"],
            "name": equipment["name"],
            "price": price,
        })
    return offers


def add_party_materials(player, count=2):
    gained = {}
    materials = player.setdefault("materials", {})
    for _ in range(max(1, int(count))):
        name = random.choice(PARTY_MATERIALS)
        amount = random.randint(1, 2)
        materials[name] = int(materials.get(name, 0)) + amount
        gained[name] = gained.get(name, 0) + amount
    return gained


def format_gained_materials(gained):
    return ", ".join(f"{name} ×{amount}" for name, amount in gained.items())


def create_party_player(uid, name, job, level, is_bot=False):
    player = {
        "id": str(uid),
        "user_id": None if is_bot else str(uid),
        "name": name,
        "job": job,
        "level": max(1, int(level)),
        "party_exp": 0,
        "is_bot": bool(is_bot),
        "alive": True,
        "lives": 1,
        "hp": 1,
        "max_hp": 1,
        "weapon": PARTY_BASIC_WEAPON,
        "armor": PARTY_BASIC_ARMOR,
        "bag_weapons": [],
        "bag_armors": [],
        "materials": {},
        "skill_cooldown": 0,
        "defending": False,
        "dodge_bonus": 0.0,
    }
    refresh_party_player_max_hp(player, None, keep_ratio=False)
    player["hp"] = player["max_hp"]
    return player


def initialize_party_run(party):
    guild = bot.get_guild(int(party.get("guild_id", 0)))
    humans = party_human_members(party)
    players = {}

    for uid in humans:
        job = party.get("jobs", {}).get(uid, "전사")
        name = get_party_member_name(guild, uid)
        players[uid] = create_party_player(uid, name, job, 1, is_bot=False)

    bot_jobs = list(PARTY_JOB_INFO.keys())
    random.shuffle(bot_jobs)
    for index in range(PARTY_TOTAL_SLOTS - len(humans)):
        bot_id = f"npc:{party.get('id')}:{index + 1}"
        job = bot_jobs[index % len(bot_jobs)]
        players[bot_id] = create_party_player(
            bot_id,
            f"용병 {index + 1}",
            job,
            1,
            is_bot=True,
        )

    party["run"] = {
        "turn": 0,
        "terrain": party.get("start_terrain", "grassland"),
        "phase": "explore",
        "coins": 300,
        "players": players,
        "battle": None,
        "event_id": None,
        "event_votes": {},
        "merchant_offers": [],
        "shared_storage": [],
        "rest_votes": [],
        "last_rest_turn": -999,
        "camp_locked": {},
        "pending_route": False,
        "buffs": {
            "attack_battles": 0,
            "attack_strong": 0,
            "defense_battles": 0,
        },
        "kills": 0,
        "boss_kills": 0,
        "equipment_found": 0,
        "relics": [],
        "turns_without_battle": 0,
        "battle_safe_turns": 0,
        "last_result": None,
        "end_votes": [],
        "permanent_rewards_granted": False,
        "permanent_reward_summary": "",
        "level_system_version": PARTY_LEVEL_SYSTEM_VERSION,
        "started_at": datetime.now(KST).isoformat(),
    }


def party_average_level(run):
    levels = [max(1, int(player.get("level", 1))) for player in run.get("players", {}).values()]
    return max(1, int(round(sum(levels) / max(1, len(levels)))))


def create_party_monster(party, elite=False, boss=False, forced_name=None):
    run = party.get("run") or {}
    terrain_key = run.get("terrain", "grassland")
    terrain = ADVENTURE_TERRAINS.get(terrain_key, ADVENTURE_TERRAINS["grassland"])
    depth = ADVENTURE_TERRAIN_DEPTH.get(terrain_key, 1)
    turn = max(1, int(run.get("turn", 1)))

    # 첫 유저는 기준 배율 ×1.00이고, 추가로 참가한 유저 1명마다 +25%.
    # 빈자리를 채운 NPC는 전력 보조용이므로 1명당 +10%만 반영한다.
    human_count = max(1, len(party_human_members(party)))
    npc_count = max(0, len(run.get("players", {})) - human_count)
    member_scale = 1.0 + 0.25 * max(0, human_count - 1) + 0.10 * npc_count

    # 체력은 파티 규모의 영향을 그대로 받지만 공격력은 완만하게 증가한다.
    # 초반 1~5턴에는 공격력 보호 보정을 적용해 시작부터 즉사하지 않도록 한다.
    attack_member_scale = 1.0 + (member_scale - 1.0) * 0.55
    early_attack_scale = min(1.0, 0.72 + max(0, turn - 1) * 0.07)

    hard_hp_scale = 1.40 if party.get("hard_mode") else 1.0
    hard_attack_scale = 1.22 if party.get("hard_mode") else 1.0
    elite_hp_scale = 1.30 if elite else 1.0
    elite_attack_scale = 1.18 if elite else 1.0
    boss_hp_scale = 1.70 if boss else 1.0
    boss_attack_scale = 1.35 if boss else 1.0
    terrain_scale = max(0.8, float(terrain.get("danger_mul", 1.0)))

    average_level = party_average_level(run)
    target_level = max(
        1,
        int(round(average_level + max(0, turn - 1) * 0.55 + max(0, depth - 1) * 2.2)),
    )
    if elite:
        target_level += 3
    if boss:
        target_level += 6

    if forced_name:
        name = forced_name
    elif boss:
        if terrain_key == "outskirts":
            name = random.choice(terrain.get("bosses", [terrain.get("boss", "보스")]))
        else:
            name = terrain.get("boss", "지형의 지배자")
    else:
        candidates = list(terrain.get("monsters", ["슬라임"]))
        if terrain.get("boss") in candidates and len(candidates) > 1:
            candidates = [name for name in candidates if name != terrain.get("boss")]
        name = random.choice(candidates or [terrain.get("boss", "슬라임")])

    base_hp = 65 + target_level * 13 + max(0, turn - 1) * 9
    base_attack = 4 + target_level * 1.0 + max(0, turn - 1) * 0.55

    hp_scale = member_scale * hard_hp_scale * elite_hp_scale * boss_hp_scale * terrain_scale
    attack_scale = (
        attack_member_scale
        * hard_attack_scale
        * elite_attack_scale
        * boss_attack_scale
        * terrain_scale
        * early_attack_scale
    )
    max_hp = max(55, int(round(base_hp * hp_scale)))
    attack = max(4, int(round(base_attack * attack_scale)))

    return {
        "name": name,
        "level": target_level,
        "hp": max_hp,
        "max_hp": max_hp,
        "attack": attack,
        "member_scale": member_scale,
        "human_count": human_count,
        "npc_count": npc_count,
        "balance_version": PARTY_BALANCE_VERSION,
        "is_elite": bool(elite),
        "is_boss": bool(boss),
        "attack_debuff": 0.0,
    }


def start_party_battle(party, elite=False, boss=False, forced_name=None, opening_log=None):
    run = party.get("run") or {}
    monster = create_party_monster(party, elite=elite, boss=boss, forced_name=forced_name)
    run["phase"] = "battle"
    run["battle"] = {
        "monster": monster,
        "round": 1,
        "actions": {},
        "log": [opening_log] if opening_log else [],
    }
    for player in run.get("players", {}).values():
        player["defending"] = False
        player["dodge_bonus"] = 0.0


def party_random_living_player(run):
    living = [player for player in run.get("players", {}).values() if player.get("alive")]
    return random.choice(living) if living else None


def party_lose_equipped_item(player):
    candidates = []
    if player.get("weapon") != PARTY_BASIC_WEAPON:
        candidates.append("weapon")
    if player.get("armor") != PARTY_BASIC_ARMOR:
        candidates.append("armor")
    if not candidates:
        return None
    lost_kind = random.choice(candidates)
    if lost_kind == "weapon":
        lost_name = player.get("weapon")
        player["weapon"] = PARTY_BASIC_WEAPON
    else:
        lost_name = player.get("armor")
        player["armor"] = PARTY_BASIC_ARMOR
    refresh_party_player_max_hp(player, None, keep_ratio=True)
    return {"kind": lost_kind, "name": lost_name}


def party_apply_damage(player, raw_damage, run, extra_reduction=0.0):
    stats = party_player_stats(player, run)
    if random.random() < min(0.80, stats["dodge"] + float(player.get("dodge_bonus", 0.0))):
        return 0, True, None

    reduction = stats["defense"] + extra_reduction
    if player.get("defending"):
        reduction += 60.0
    if int(run.get("buffs", {}).get("defense_battles", 0)) > 0:
        reduction += 20.0
    reduction = max(0.0, min(85.0, reduction))
    damage = max(1, int(round(float(raw_damage) * (1.0 - reduction / 100.0))))
    player["hp"] = max(0, int(player.get("hp", 0)) - damage)

    lost = None
    if player["hp"] <= 0 and player.get("alive"):
        player["alive"] = False
        player["lives"] = 0
        player["hp"] = 0
        lost = party_lose_equipped_item(player)
    return damage, False, lost


def party_attack_damage(player, run, skill_multiplier=1.0, forced_crit_chance=None):
    stats = party_player_stats(player, run)
    crit_chance = stats["crit"] if forced_crit_chance is None else forced_crit_chance
    critical = random.random() < crit_chance
    variance = random.uniform(0.90, 1.10)
    damage = stats["attack"] * skill_multiplier * variance
    if critical:
        damage *= 1.75
    return max(1, int(round(damage))), critical


def resolve_party_battle_round(party):
    run = party.get("run") or {}
    battle = run.get("battle") or {}
    monster = battle.get("monster") or {}
    actions = dict(battle.get("actions", {}))
    logs = []

    # NPC는 자동으로 행동한다.
    for key, player in run.get("players", {}).items():
        if not player.get("alive") or not player.get("is_bot"):
            continue
        if int(player.get("skill_cooldown", 0)) <= 0 and random.random() < 0.42:
            actions[key] = "직업 스킬"
        elif player.get("job") == "수호자" and random.random() < 0.28:
            actions[key] = "방어"
        else:
            actions[key] = "공격"

    for player in run.get("players", {}).values():
        player["defending"] = False
        player["dodge_bonus"] = 0.0
        if int(player.get("skill_cooldown", 0)) > 0:
            player["skill_cooldown"] = int(player.get("skill_cooldown", 0)) - 1

    party_guard = 0.0
    monster_attack_reduction = 0.0

    # 민첩한 직업부터 행동하도록 대략적인 우선순위를 둔다.
    job_order = {"도적": 0, "궁수": 1, "마법사": 2, "전사": 3, "사제": 4, "수호자": 5}
    acting_players = [
        (key, player) for key, player in run.get("players", {}).items()
        if player.get("alive")
    ]
    acting_players.sort(key=lambda item: job_order.get(item[1].get("job"), 9))

    for key, player in acting_players:
        if int(monster.get("hp", 0)) <= 0:
            break
        action = actions.get(key, "공격")
        job = player.get("job", "전사")

        if action == "방어":
            player["defending"] = True
            logs.append(f"🛡️ **{player.get('name')}**이 방어 태세를 취했다.")
            continue

        if action != "직업 스킬" or int(player.get("skill_cooldown", 0)) > 0:
            damage, critical = party_attack_damage(player, run)
            monster["hp"] = max(0, int(monster.get("hp", 0)) - damage)
            logs.append(
                f"{'💥' if critical else '⚔️'} **{player.get('name')}**의 공격! "
                f"**{damage:,}** 피해{' (치명타)' if critical else ''}."
            )
            continue

        player["skill_cooldown"] = 3
        if job == "전사":
            damage, critical = party_attack_damage(player, run, skill_multiplier=1.90, forced_crit_chance=0.18)
            monster["hp"] = max(0, int(monster.get("hp", 0)) - damage)
            logs.append(f"⚔️ **{player.get('name')}**의 `분쇄의 일격`! **{damage:,}** 피해.")

        elif job == "수호자":
            damage, _ = party_attack_damage(player, run, skill_multiplier=0.72)
            monster["hp"] = max(0, int(monster.get("hp", 0)) - damage)
            party_guard = max(party_guard, 38.0)
            player["defending"] = True
            logs.append(
                f"🛡️ **{player.get('name')}**의 `철벽 수호`! **{damage:,}** 피해를 주고 이번 라운드 파티 피해를 감소시킨다."
            )

        elif job == "궁수":
            damage, critical = party_attack_damage(player, run, skill_multiplier=1.48, forced_crit_chance=0.58)
            monster["hp"] = max(0, int(monster.get("hp", 0)) - damage)
            logs.append(
                f"🏹 **{player.get('name')}**의 `약점 관통`! **{damage:,}** 피해"
                f"{' (치명타)' if critical else ''}."
            )

        elif job == "도적":
            total = 0
            crits = 0
            for _ in range(2):
                damage, critical = party_attack_damage(player, run, skill_multiplier=0.78)
                total += damage
                crits += 1 if critical else 0
            monster["hp"] = max(0, int(monster.get("hp", 0)) - total)
            stolen = random.randint(25, 70) + int(run.get("turn", 1)) * 4
            run["coins"] = int(run.get("coins", 0)) + stolen
            player["dodge_bonus"] = 0.25
            logs.append(
                f"🗡️ **{player.get('name')}**의 `그림자 연격`! **{total:,}** 피해, "
                f"모라 **{stolen:,}** 탈취{f', 치명타 {crits}회' if crits else ''}."
            )

        elif job == "마법사":
            damage, critical = party_attack_damage(player, run, skill_multiplier=1.72, forced_crit_chance=0.14)
            monster["hp"] = max(0, int(monster.get("hp", 0)) - damage)
            monster_attack_reduction = max(monster_attack_reduction, 0.27)
            logs.append(
                f"🔮 **{player.get('name')}**의 `원소 붕괴`! **{damage:,}** 피해를 주고 적 공격력을 27% 약화한다."
            )

        elif job == "사제":
            living = [p for p in run.get("players", {}).values() if p.get("alive")]
            target = min(living, key=lambda p: p.get("hp", 0) / max(1, p.get("max_hp", 1))) if living else player
            heal = max(1, int(round(target.get("max_hp", 1) * 0.38)))
            old_hp = int(target.get("hp", 0))
            target["hp"] = min(int(target.get("max_hp", 1)), old_hp + heal)
            actual = target["hp"] - old_hp
            damage, _ = party_attack_damage(player, run, skill_multiplier=0.55)
            monster["hp"] = max(0, int(monster.get("hp", 0)) - damage)
            logs.append(
                f"✨ **{player.get('name')}**의 `치유의 빛`! **{target.get('name')}** 체력 **{actual:,}** 회복, "
                f"적에게 **{damage:,}** 피해."
            )

    if int(monster.get("hp", 0)) <= 0:
        battle["actions"] = {}
        battle["log"] = (battle.get("log", []) + logs)[-12:]
        return "victory", logs

    living = [player for player in run.get("players", {}).values() if player.get("alive")]
    if not living:
        return "defeat", logs

    # 일반 몬스터는 파티 인원이 많아도 기본 1회만 공격한다.
    # 정예는 최대 2회, 보스는 2회(하드 보스는 최대 3회) 공격한다.
    attack_count = 1
    if monster.get("is_elite") and len(living) >= 3:
        attack_count = 2
    if monster.get("is_boss"):
        attack_count = 2
        if party.get("hard_mode") and len(living) >= 3:
            attack_count = 3

    for _ in range(attack_count):
        target = party_random_living_player(run)
        if not target:
            break
        raw_attack = int(monster.get("attack", 1))
        debuff = max(float(monster.get("attack_debuff", 0.0)), monster_attack_reduction)
        raw_attack = max(1, int(round(raw_attack * (1.0 - debuff))))
        damage, dodged, lost = party_apply_damage(target, raw_attack, run, extra_reduction=party_guard)
        if dodged:
            logs.append(f"💨 **{target.get('name')}**이 {monster.get('name')}의 공격을 회피했다!")
        else:
            logs.append(f"👹 **{monster.get('name')}**의 공격! **{target.get('name')}**에게 **{damage:,}** 피해.")
        if not target.get("alive"):
            if lost:
                logs.append(
                    f"💀 **{target.get('name')}** 전투 불능! 착용 중이던 **{lost.get('name')}**을 잃었다. "
                    "다음 캠프까지 관전한다."
                )
            else:
                logs.append(
                    f"💀 **{target.get('name')}** 전투 불능! 다음 캠프까지 관전한다."
                )

    for player in run.get("players", {}).values():
        player["defending"] = False
        player["dodge_bonus"] = 0.0

    battle["round"] = int(battle.get("round", 1)) + 1
    battle["actions"] = {}
    battle["log"] = (battle.get("log", []) + logs)[-12:]

    if not any(player.get("alive") for player in run.get("players", {}).values()):
        return "defeat", logs
    return "continue", logs


def reward_party_battle(party):
    run = party.get("run") or {}
    battle = run.get("battle") or {}
    monster = battle.get("monster") or {}
    turn = max(1, int(run.get("turn", 1)))
    depth = ADVENTURE_TERRAIN_DEPTH.get(run.get("terrain"), 1)
    reward = int((80 + turn * 22 + depth * 65) * (1.7 if monster.get("is_boss") else 1.0))
    if monster.get("is_elite"):
        reward = int(reward * 1.45)
    if party.get("hard_mode"):
        reward = int(reward * 1.4)
    relic_bonuses = get_party_relic_bonuses(run)
    reward = int(round(reward * (1.0 + float(relic_bonuses.get("reward_pct", 0.0)))))
    run["coins"] = int(run.get("coins", 0)) + reward
    run["kills"] = int(run.get("kills", 0)) + 1
    if monster.get("is_boss"):
        run["boss_kills"] = int(run.get("boss_kills", 0)) + 1

    living = [player for player in run.get("players", {}).values() if player.get("alive")]
    material_text = ""
    if living:
        receiver = random.choice(living)
        gained = add_party_materials(receiver, count=2 if monster.get("is_elite") else 1)
        material_text = f"\n🎒 **{receiver.get('name')}** 재료 획득: {format_gained_materials(gained)}"

    equipment_text = ""
    rate = 0.18
    if monster.get("is_elite"):
        rate = 0.45
    if monster.get("is_boss"):
        rate = 1.0
    if party.get("hard_mode"):
        rate *= 1.25
    rate += float(relic_bonuses.get("equipment_rate", 0.0))
    if living and random.random() < min(1.0, rate):
        equipment = roll_party_equipment(
            run,
            low_tier=False,
            special_only=(depth >= 7 and monster.get("is_boss") and random.random() < 0.55),
        )
        if equipment:
            receiver = random.choice(living)
            receive_result = give_party_equipment_to_player(receiver, equipment, run)
            run["equipment_found"] = int(run.get("equipment_found", 0)) + 1
            equipment_text = (
                f"\n{'🗡️' if equipment.get('kind') == 'weapon' else '🛡️'} "
                f"장비 획득: **{equipment.get('name')}**"
                + party_equipment_receive_suffix(receiver, equipment, receive_result)
            )

    # 사제와 유물의 전투 후 회복.
    priests = [player for player in living if player.get("job") == "사제"]
    priest_text = ""
    if priests:
        for player in living:
            heal = max(1, int(player.get("max_hp", 1) * 0.06))
            player["hp"] = min(int(player.get("max_hp", 1)), int(player.get("hp", 0)) + heal)
        priest_text = "\n✨ 사제의 전투 후 기도로 생존자들이 최대 체력의 6%를 회복했다."

    relic_heal_text = ""
    relic_heal_rate = float(relic_bonuses.get("after_battle_heal", 0.0))
    if living and relic_heal_rate > 0:
        for player in living:
            heal = max(1, int(player.get("max_hp", 1) * relic_heal_rate))
            player["hp"] = min(int(player.get("max_hp", 1)), int(player.get("hp", 0)) + heal)
        relic_heal_text = f"\n🔥 잔불 부적이 생존자들의 체력을 {relic_heal_rate * 100:.0f}% 회복했다."

    experience_text = grant_party_battle_experience(party)

    return (
        f"🏆 **{monster.get('name')}** 격파! 공용 모라 **+{reward:,}**"
        + experience_text
        + material_text
        + equipment_text
        + priest_text
        + relic_heal_text
    )


def decrement_party_battle_buffs(run):
    buffs = run.get("buffs", {})
    for key in ("attack_battles", "attack_strong", "defense_battles"):
        if int(buffs.get(key, 0)) > 0:
            buffs[key] = int(buffs.get(key, 0)) - 1


def revive_party_at_camp(run):
    revived = []
    for player in run.get("players", {}).values():
        if player.get("alive"):
            continue
        player["alive"] = True
        player["lives"] = 1
        refresh_party_player_max_hp(player, run, keep_ratio=False)
        player["hp"] = max(1, int(player.get("max_hp", 1) * 0.50))
        revived.append(player.get("name"))
    return revived


def party_run_summary_embed(party, victory=False, reason=None, voluntary=False):
    run = party.get("run") or {}
    permanent_reward_text = grant_party_permanent_rewards(party, victory=victory, voluntary=voluntary)
    if voluntary:
        title = "🏳️ 파티 모험 중도 종료"
        color = discord.Color.orange()
    else:
        title = "🏆 파티 모험 종료" if victory else "☠️ 파티 모험 실패"
        color = discord.Color.gold() if victory else discord.Color.dark_red()
    player_levels = [max(1, int(player.get("level", 1))) for player in run.get("players", {}).values()]
    average_party_level = sum(player_levels) / max(1, len(player_levels))
    description = (
        f"파티: **{party.get('name')}**\n"
        f"도달 지형: **{get_terrain_display(run.get('terrain'))}**\n"
        f"완료 턴: **{int(run.get('turn', 0))}턴**\n"
        f"처치 수: **{int(run.get('kills', 0))}마리**\n"
        f"보스 처치: **{int(run.get('boss_kills', 0))}마리**\n"
        f"발견 장비: **{int(run.get('equipment_found', 0))}개**\n"
        f"발견 유물: **{len(run.get('relics', []))}개**\n"
        f"평균 원정 레벨: **Lv.{average_party_level:.1f}**\n"
        f"남은 공용 모라: **{int(run.get('coins', 0)):,}모라**"
    )
    if reason:
        description += f"\n\n{reason}"
    description += f"\n\n## 영구 원정 보상\n{permanent_reward_text}"
    return discord.Embed(title=title, description=description, color=color)


async def update_party_recruit_message(party):
    channel = get_party_recruit_channel(party)
    if not channel or not party.get("recruit_message_id"):
        return
    try:
        message = await channel.fetch_message(int(party.get("recruit_message_id")))
        await message.edit(
            embed=build_party_recruit_embed(party),
            view=PartyRecruitView(party.get("id")),
        )
    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
        pass


async def update_party_lobby_message(party):
    thread = get_party_thread(party)
    if not thread or not party.get("lobby_message_id"):
        return
    try:
        message = await thread.fetch_message(int(party.get("lobby_message_id")))
        await message.edit(
            embed=build_party_lobby_embed(party),
            view=PartyLobbyView(party.get("id")),
        )
    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
        pass


async def close_party(party, status="closed", reason=None):
    party["status"] = status
    party["closed_at"] = datetime.now(KST).isoformat()
    save_party_data()
    await update_party_recruit_message(party)
    thread = get_party_thread(party)
    if thread:
        try:
            text = reason or "파티 모집이 종료됐어."
            await thread.send(f"🔒 {text}")
        except discord.HTTPException:
            pass


async def party_edit_interaction(interaction, embed, view=None, content=None):
    if interaction.response.is_done():
        try:
            await interaction.edit_original_response(content=content, embed=embed, view=view)
        except (discord.NotFound, discord.HTTPException):
            await interaction.followup.send(content=content, embed=embed, view=view)
    else:
        await interaction.response.edit_message(content=content, embed=embed, view=view)


async def party_complete_turn(interaction, party, result_text=None):
    run = party.get("run") or {}
    completed_battle = bool(run.get("battle"))
    if completed_battle:
        run["turns_without_battle"] = 0
        run["battle_safe_turns"] = PARTY_BATTLE_SAFE_TURNS
        run["last_result"] = "battle"
    else:
        run["turns_without_battle"] = int(run.get("turns_without_battle", 0)) + 1
        run["battle_safe_turns"] = max(0, int(run.get("battle_safe_turns", 0)) - 1)
        run["last_result"] = "non_battle"

    run["battle"] = None
    run["event_id"] = None
    run["event_votes"] = {}
    run["merchant_offers"] = []

    if not any(player.get("alive") for player in run.get("players", {}).values()):
        party["status"] = "failed"
        run["phase"] = "ended"
        save_party_data()
        await update_party_recruit_message(party)
        await party_edit_interaction(
            interaction,
            party_run_summary_embed(party, victory=False, reason="파티 전원이 쓰러져 다음 캠프에 도달하지 못했다."),
            view=None,
        )
        return

    if int(run.get("turn", 0)) % PARTY_CAMP_INTERVAL == 0:
        revived = revive_party_at_camp(run)
        bot_camp_notices = handle_party_bot_camp_actions(run)
        run["phase"] = "camp"
        run["rest_votes"] = []
        run["camp_locked"] = {uid: False for uid in party_human_members(party)}
        notice_parts = []
        if result_text:
            notice_parts.append(result_text)
        if revived:
            notice_parts.append("💫 캠프 도착으로 부활: " + ", ".join(revived))
        notice_parts.extend(bot_camp_notices)
        save_party_data()
        await party_edit_interaction(
            interaction,
            build_party_camp_embed(party, "\n".join(notice_parts) if notice_parts else None),
            view=PartyCampView(party.get("id")),
        )
        return

    if run.get("pending_route"):
        routes = ADVENTURE_TERRAIN_ROUTES.get(run.get("terrain"), [])
        if not routes:
            party["status"] = "completed"
            run["phase"] = "ended"
            save_party_data()
            await update_party_recruit_message(party)
            await party_edit_interaction(
                interaction,
                party_run_summary_embed(party, victory=True, reason="마지막 지형의 보스를 쓰러뜨리고 파티 모험을 완주했다!"),
                view=None,
            )
            return
        run["phase"] = "route"
        save_party_data()
        await party_edit_interaction(interaction, build_party_route_embed(party), view=PartyRouteView(party.get("id")))
        return

    run["phase"] = "explore"
    save_party_data()
    await party_edit_interaction(
        interaction,
        build_party_explore_embed(party, result_text=result_text),
        view=PartyExploreView(party.get("id")),
    )


async def start_party_encounter(interaction, party):
    run = party.get("run") or {}

    # 이전 저장본도 새 탐험 흐름으로 안전하게 마이그레이션한다.
    run.setdefault("relics", [])
    run.setdefault("turns_without_battle", 0)
    run.setdefault("battle_safe_turns", 0)
    run.setdefault("last_result", None)

    run["turn"] = int(run.get("turn", 0)) + 1
    turn = int(run.get("turn", 1))

    # 10턴마다 현재 지형 보스가 등장한다. 일반 조우 확률과는 별개다.
    if turn % PARTY_BOSS_INTERVAL == 0:
        run["pending_route"] = True
        start_party_battle(party, boss=True, opening_log="👑 긴 탐험 끝에 지형의 보스가 길을 막아섰다!")
        save_party_data()
        await party_edit_interaction(interaction, build_party_battle_embed(party), view=PartyBattleView(party.get("id")))
        return

    battle_rate = get_party_battle_spawn_rate(party)
    event_rate = 0.20
    relic_rate = 0.16
    equipment_rate = 0.12 + min(0.10, float(get_party_relic_bonuses(run).get("equipment_rate", 0.0)))
    merchant_rate = 0.08
    material_rate = 0.10
    coin_rate = 0.06
    recovery_rate = 0.05
    quiet_rate = 0.03

    outcomes = [
        ("battle", battle_rate),
        ("event", event_rate),
        ("relic", relic_rate),
        ("equipment", equipment_rate),
        ("merchant", merchant_rate),
        ("materials", material_rate),
        ("coins", coin_rate),
        ("recovery", recovery_rate),
        ("quiet", quiet_rate),
    ]
    total = sum(weight for _, weight in outcomes if weight > 0)
    roll = random.random() * total
    selected = "quiet"
    cursor = 0.0
    for name, weight in outcomes:
        if weight <= 0:
            continue
        cursor += weight
        if roll <= cursor:
            selected = name
            break

    if selected == "battle":
        elite = random.random() < (0.22 if party.get("hard_mode") else 0.12)
        start_party_battle(party, elite=elite)
        save_party_data()
        await party_edit_interaction(interaction, build_party_battle_embed(party), view=PartyBattleView(party.get("id")))
        return

    if selected == "event":
        events = PARTY_TERRAIN_EVENTS.get(run.get("terrain"), PARTY_TERRAIN_EVENTS["grassland"])
        event = random.choice(events)
        run["phase"] = "event"
        run["event_id"] = event.get("id")
        run["event_votes"] = {}
        save_party_data()
        await party_edit_interaction(interaction, build_party_event_embed(party), view=PartyEventView(party.get("id")))
        return

    if selected == "merchant":
        run["phase"] = "merchant"
        run["merchant_offers"] = generate_party_merchant_offers(run)
        save_party_data()
        await party_edit_interaction(interaction, build_party_merchant_embed(party), view=PartyMerchantView(party.get("id")))
        return

    if selected == "relic":
        relic_name = roll_party_relic(run)
        if relic_name:
            await party_complete_turn(
                interaction,
                party,
                "✨ 오래된 빛을 따라가 **파티 유물**을 발견했다!\n" + format_party_relic(relic_name),
            )
            return
        selected = "equipment"

    if selected == "equipment":
        receiver = party_random_living_player(run)
        equipment = roll_party_equipment(run, low_tier=(turn <= 5))
        if receiver and equipment:
            receive_result = give_party_equipment_to_player(receiver, equipment, run)
            run["equipment_found"] = int(run.get("equipment_found", 0)) + 1
            icon = "🗡️" if equipment.get("kind") == "weapon" else "🛡️"
            await party_complete_turn(
                interaction,
                party,
                f"{icon} 길가의 상자에서 **{equipment.get('name')}**을 발견했다!"
                + party_equipment_receive_suffix(receiver, equipment, receive_result),
            )
            return
        selected = "materials"

    if selected == "materials":
        receiver = party_random_living_player(run)
        if receiver:
            bonus_count = int(get_party_relic_bonuses(run).get("material_bonus", 0))
            gained = add_party_materials(receiver, count=1 + bonus_count)
            await party_complete_turn(
                interaction,
                party,
                f"🌿 탐험 중 쓸 만한 재료를 발견했다.\n"
                f"🎒 **{receiver.get('name')}** 획득: {format_gained_materials(gained)}",
            )
            return
        selected = "quiet"

    if selected == "coins":
        depth = ADVENTURE_TERRAIN_DEPTH.get(run.get("terrain"), 1)
        amount = random.randint(80, 160) + turn * 14 + depth * 35
        run["coins"] = int(run.get("coins", 0)) + amount
        await party_complete_turn(
            interaction,
            party,
            f"🪙 버려진 짐에서 공용 모라 **{amount:,}**를 발견했다.",
        )
        return

    if selected == "recovery":
        living = [player for player in run.get("players", {}).values() if player.get("alive")]
        for player in living:
            heal = max(1, int(player.get("max_hp", 1) * 0.18))
            player["hp"] = min(int(player.get("max_hp", 1)), int(player.get("hp", 0)) + heal)
        await party_complete_turn(
            interaction,
            party,
            "💧 잠시 쉴 만한 작은 샘을 발견해 생존자 전원이 최대 체력의 18%를 회복했다.",
        )
        return

    await party_complete_turn(
        interaction,
        party,
        random.choice([
            "🌤️ 별다른 위협 없이 조용히 길을 통과했다.",
            "👣 오래된 발자국을 따라갔지만 이미 흔적은 끊겨 있었다.",
            "🌬️ 바람 소리만 들리는 평온한 구간을 지나갔다.",
            "🔎 주변을 샅샅이 살폈지만 특별한 것은 발견하지 못했다.",
        ]),
    )


def resolve_party_event_outcome(party, choice):
    run = party.get("run") or {}
    kind = choice.get("kind")
    living = [player for player in run.get("players", {}).values() if player.get("alive")]
    receiver = random.choice(living) if living else None

    if kind == "heal":
        for player in living:
            heal = max(1, int(player.get("max_hp", 1) * 0.22))
            player["hp"] = min(int(player.get("max_hp", 1)), int(player.get("hp", 0)) + heal)
        return "done", "💧 맑은 물을 마셔 생존자 전원이 최대 체력의 22%를 회복했다."

    if kind == "heal_big":
        for player in living:
            heal = max(1, int(player.get("max_hp", 1) * 0.40))
            player["hp"] = min(int(player.get("max_hp", 1)), int(player.get("hp", 0)) + heal)
        return "done", "💚 생명의 기운이 퍼져 생존자 전원이 최대 체력의 40%를 회복했다."

    if kind == "risky_heal":
        if random.random() < 0.65:
            for player in living:
                heal = max(1, int(player.get("max_hp", 1) * 0.32))
                player["hp"] = min(int(player.get("max_hp", 1)), int(player.get("hp", 0)) + heal)
            return "done", "🍈 달콤한 열매였다! 생존자 전원이 최대 체력의 32%를 회복했다."
        for player in living:
            damage = max(1, int(player.get("max_hp", 1) * 0.12))
            player["hp"] = max(1, int(player.get("hp", 1)) - damage)
        return "done", "☠️ 열매에 약한 독이 있었다. 생존자 전원이 최대 체력의 12% 피해를 입었다."

    if kind == "materials":
        if not receiver:
            return "done", "주울 수 있는 파티원이 없었다."
        gained = add_party_materials(receiver, count=3)
        return "done", f"🎒 **{receiver.get('name')}**이 {format_gained_materials(gained)}을 챙겼다."

    if kind in {"coins", "coins_big"}:
        amount = random.randint(120, 260) + int(run.get("turn", 1)) * (18 if kind == "coins" else 35)
        if kind == "coins_big":
            amount *= 2
        run["coins"] = int(run.get("coins", 0)) + amount
        return "done", f"🪙 공용 모라 **{amount:,}**을 획득했다."

    if kind == "risky_coins":
        if random.random() < 0.72:
            amount = random.randint(320, 600) + int(run.get("turn", 1)) * 30
            run["coins"] = int(run.get("coins", 0)) + amount
            return "done", f"⛏️ 광맥 채굴에 성공해 공용 모라 **{amount:,}**을 얻었다."
        start_party_battle(party, elite=True, opening_log="💢 채굴 소리에 잠들어 있던 강적이 깨어났다!")
        return "battle", "광맥의 수호자가 나타났다."

    if kind in {"equipment_low", "risky_equipment", "special_equipment"}:
        if not receiver:
            return "done", "장비를 받을 파티원이 없었다."
        if kind == "risky_equipment" and random.random() < 0.32:
            start_party_battle(party, elite=True, opening_log="⚠️ 장비에 손을 대자 수호자가 나타났다!")
            return "battle", "수호자와의 전투가 시작됐다."
        equipment = roll_party_equipment(
            run,
            low_tier=(kind == "equipment_low"),
            special_only=(kind == "special_equipment"),
        )
        if not equipment:
            amount = 180 + int(run.get("turn", 1)) * 20
            run["coins"] = int(run.get("coins", 0)) + amount
            return "done", f"쓸 만한 장비는 없었지만 모라 **{amount:,}**을 발견했다."
        give_party_equipment_to_player(receiver, equipment, run)
        run["equipment_found"] = int(run.get("equipment_found", 0)) + 1
        return "done", (
            f"{'🗡️' if equipment.get('kind') == 'weapon' else '🛡️'} **{receiver.get('name')}**이 "
            f"**{equipment.get('name')}**을 획득했다."
        )

    if kind == "raid":
        if random.random() < 0.45:
            start_party_battle(party, elite=random.random() < 0.35, opening_log="🔥 약탈을 시작하자 캠프의 주인들이 몰려왔다!")
            return "battle", "약탈 전투가 시작됐다."
        amount = random.randint(180, 420) + int(run.get("turn", 1)) * 20
        run["coins"] = int(run.get("coins", 0)) + amount
        equipment = roll_party_equipment(run, low_tier=True)
        text = f"🔥 빈틈을 노려 공용 모라 **{amount:,}**을 약탈했다."
        if receiver and equipment:
            give_party_equipment_to_player(receiver, equipment, run)
            run["equipment_found"] = int(run.get("equipment_found", 0)) + 1
            text += f" **{receiver.get('name')}**은 **{equipment.get('name')}**도 챙겼다."
        return "done", text

    if kind == "talk":
        if random.random() < 0.72:
            amount = random.randint(80, 180)
            run["coins"] = int(run.get("coins", 0)) + amount
            if receiver:
                gained = add_party_materials(receiver, count=2)
                return "done", f"👋 대화가 통했다! 모라 **{amount:,}**과 {format_gained_materials(gained)}을 받았다."
            return "done", f"👋 대화가 통했다! 모라 **{amount:,}**을 받았다."
        start_party_battle(party, opening_log="💢 말이 통하지 않았다. 상대가 무기를 들었다!")
        return "battle", "협상이 결렬됐다."

    if kind == "blessing":
        run.setdefault("buffs", {})["attack_battles"] = max(
            int(run.get("buffs", {}).get("attack_battles", 0)), 2
        )
        return "done", "✨ 축복을 받아 다음 2번의 전투 동안 파티 공격력이 15% 증가한다."

    if kind == "help":
        amount = random.randint(150, 350)
        run["coins"] = int(run.get("coins", 0)) + amount
        run.setdefault("buffs", {})["defense_battles"] = max(
            int(run.get("buffs", {}).get("defense_battles", 0)), 1
        )
        return "done", f"🩹 모험가가 감사의 뜻으로 모라 **{amount:,}**과 방어 축복을 건넸다."

    if kind == "merchant_hint":
        run["phase"] = "merchant"
        run["merchant_offers"] = generate_party_merchant_offers(run)
        return "merchant", "모험가가 숨겨진 상인의 위치를 알려줬다."

    if kind == "merchant":
        run["phase"] = "merchant"
        run["merchant_offers"] = generate_party_merchant_offers(run)
        return "merchant", "암시장 상인이 장비를 펼쳐 보였다."

    if kind == "sacrifice":
        for player in living:
            damage = max(1, int(player.get("max_hp", 1) * 0.18))
            player["hp"] = max(1, int(player.get("hp", 1)) - damage)
        equipment = roll_party_equipment(run, special_only=True) or roll_party_equipment(run)
        if receiver and equipment:
            give_party_equipment_to_player(receiver, equipment, run)
            run["equipment_found"] = int(run.get("equipment_found", 0)) + 1
            return "done", (
                f"🩸 생존자 전원이 최대 체력의 18%를 대가로 치렀고, "
                f"**{receiver.get('name')}**이 **{equipment.get('name')}**을 받았다."
            )
        return "done", "🩸 생명력을 바쳤지만 제단은 아무것도 내놓지 않았다."

    if kind == "battle":
        start_party_battle(party, elite=True, opening_log="⚔️ 선택의 결과로 강적과 전투가 시작됐다!")
        return "battle", "전투가 시작됐다."

    if kind == "battle_elite":
        start_party_battle(party, elite=True, opening_log="🔥 강력한 수호자가 파티를 시험한다!")
        return "battle", "강적과의 전투가 시작됐다."

    return "done", "사건은 별다른 일 없이 끝났다."


class PartyRecruitView(discord.ui.View):
    def __init__(self, party_id):
        super().__init__(timeout=None)
        self.party_id = str(party_id)
        party = get_party(self.party_id) or {}
        disabled = party.get("status") != "lobby" or len(party_human_members(party)) >= PARTY_MAX_HUMANS
        join_button = discord.ui.Button(
            label="파티 참가하기",
            emoji="➕",
            style=discord.ButtonStyle.success,
            custom_id=f"party_join:{self.party_id}",
            disabled=disabled,
        )
        join_button.callback = self.join_callback
        self.add_item(join_button)

    async def join_callback(self, interaction):
        async with get_party_lock(self.party_id):
            party = get_party(self.party_id)
            if not party or party.get("status") != "lobby":
                await interaction.response.send_message("❌ 이미 모집이 끝난 파티야.", ephemeral=True)
                return
            uid = str(interaction.user.id)
            existing = find_user_party(uid)
            if existing:
                await interaction.response.send_message(
                    f"❌ 이미 **{existing.get('name')}** 파티에 들어가 있어. 먼저 `/나가기`를 사용해줘.",
                    ephemeral=True,
                )
                return
            if len(party_human_members(party)) >= PARTY_MAX_HUMANS:
                await interaction.response.send_message("❌ 파티가 이미 가득 찼어.", ephemeral=True)
                return

            party.setdefault("members", []).append(uid)
            party.setdefault("jobs", {})[uid] = None
            save_party_data()

            thread = get_party_thread(party)
            if thread:
                try:
                    await thread.add_user(interaction.user)
                except (discord.Forbidden, discord.HTTPException):
                    pass

            await interaction.response.send_message(
                f"✅ **{party.get('name')}** 파티에 참가했어! {thread.mention if thread else ''}\n"
                "스레드에서 직업을 골라줘.",
                ephemeral=True,
            )
            await update_party_recruit_message(party)
            await update_party_lobby_message(party)


class PartyJobSelect(discord.ui.Select):
    def __init__(self, party_id):
        self.party_id = str(party_id)
        options = [
            discord.SelectOption(
                label=name,
                value=name,
                emoji=info["emoji"],
                description=info["desc"][:100],
            )
            for name, info in PARTY_JOB_INFO.items()
        ]
        super().__init__(
            placeholder="직업 1개 선택",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"party_job:{self.party_id}",
        )

    async def callback(self, interaction):
        async with get_party_lock(self.party_id):
            party = get_party(self.party_id)
            uid = str(interaction.user.id)
            if not party or party.get("status") != "lobby":
                await interaction.response.send_message("❌ 대기 중인 파티가 아니야.", ephemeral=True)
                return
            if uid not in party_human_members(party):
                await interaction.response.send_message("❌ 이 파티의 파티원이 아니야.", ephemeral=True)
                return
            job = self.values[0]
            party.setdefault("jobs", {})[uid] = job
            save_party_data()
            await interaction.response.send_message(f"✅ 직업을 **{party_job_text(job)}**(으)로 선택했어.", ephemeral=True)
            await update_party_lobby_message(party)
            await update_party_recruit_message(party)


class PartyStartTerrainSelect(discord.ui.Select):
    def __init__(self, party_id):
        self.party_id = str(party_id)
        party = get_party(self.party_id) or {}
        options = []
        for key in ADVENTURE_START_TERRAINS:
            info = ADVENTURE_TERRAINS[key]
            options.append(
                discord.SelectOption(
                    label=info["name"],
                    value=key,
                    emoji=info["emoji"],
                    description=info["description"][:100],
                    default=(party.get("start_terrain") == key),
                )
            )
        super().__init__(
            placeholder="파티 시작 지형 선택",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"party_start_terrain:{self.party_id}",
        )

    async def callback(self, interaction):
        async with get_party_lock(self.party_id):
            party = get_party(self.party_id)
            if not party or party.get("status") != "lobby":
                await interaction.response.send_message("❌ 대기 중인 파티가 아니야.", ephemeral=True)
                return
            if str(interaction.user.id) != str(party.get("leader_id")):
                await interaction.response.send_message("❌ 시작 지형은 파티장만 정할 수 있어.", ephemeral=True)
                return
            party["start_terrain"] = self.values[0]
            save_party_data()
            await interaction.response.send_message(
                f"✅ 시작 지형을 **{get_terrain_display(self.values[0])}**(으)로 변경했어.",
                ephemeral=True,
            )
            await update_party_lobby_message(party)
            await update_party_recruit_message(party)


class PartyLobbyView(discord.ui.View):
    def __init__(self, party_id):
        super().__init__(timeout=None)
        self.party_id = str(party_id)
        party = get_party(self.party_id) or {}
        disabled = party.get("status") != "lobby"
        self.add_item(PartyJobSelect(self.party_id))
        self.add_item(PartyStartTerrainSelect(self.party_id))

        hard_button = discord.ui.Button(
            label="하드 모드 전환",
            emoji="🔥",
            style=discord.ButtonStyle.danger,
            custom_id=f"party_toggle_hard:{self.party_id}",
            disabled=disabled,
        )
        hard_button.callback = self.hard_callback
        self.add_item(hard_button)

        start_button = discord.ui.Button(
            label="파티 모험 시작",
            emoji="⚔️",
            style=discord.ButtonStyle.success,
            custom_id=f"party_start:{self.party_id}",
            disabled=disabled,
        )
        start_button.callback = self.start_callback
        self.add_item(start_button)

        close_button = discord.ui.Button(
            label="파티 해산",
            emoji="🔒",
            style=discord.ButtonStyle.secondary,
            custom_id=f"party_close:{self.party_id}",
            disabled=disabled,
        )
        close_button.callback = self.close_callback
        self.add_item(close_button)

    async def hard_callback(self, interaction):
        async with get_party_lock(self.party_id):
            party = get_party(self.party_id)
            if not party or party.get("status") != "lobby":
                await interaction.response.send_message("❌ 대기 중인 파티가 아니야.", ephemeral=True)
                return
            uid = str(interaction.user.id)
            if uid != str(party.get("leader_id")):
                await interaction.response.send_message("❌ 파티장만 난이도를 바꿀 수 있어.", ephemeral=True)
                return
            if not is_adventure_hard_mode_unlocked(get_adventure(uid)):
                await interaction.response.send_message("❌ 파티장이 개인 모험에서 하드 모드를 먼저 해금해야 해.", ephemeral=True)
                return
            party["hard_mode"] = not bool(party.get("hard_mode"))
            save_party_data()
            await interaction.response.send_message(
                f"✅ 난이도를 **{'🔥 하드 모드' if party.get('hard_mode') else '일반 모드'}**로 바꿨어.",
                ephemeral=True,
            )
            await update_party_lobby_message(party)
            await update_party_recruit_message(party)

    async def start_callback(self, interaction):
        async with get_party_lock(self.party_id):
            party = get_party(self.party_id)
            if not party or party.get("status") != "lobby":
                await interaction.response.send_message("❌ 이미 시작했거나 종료된 파티야.", ephemeral=True)
                return
            uid = str(interaction.user.id)
            if uid != str(party.get("leader_id")):
                await interaction.response.send_message("❌ 파티장만 시작할 수 있어.", ephemeral=True)
                return
            missing_jobs = [member_uid for member_uid in party_human_members(party) if party.get("jobs", {}).get(member_uid) not in PARTY_JOB_INFO]
            if missing_jobs:
                mentions = " ".join(f"<@{member_uid}>" for member_uid in missing_jobs)
                await interaction.response.send_message(
                    f"❌ 아직 직업을 고르지 않은 파티원이 있어: {mentions}",
                    ephemeral=True,
                )
                return
            if party.get("hard_mode") and not is_adventure_hard_mode_unlocked(get_adventure(uid)):
                party["hard_mode"] = False

            initialize_party_run(party)
            party["status"] = "playing"
            party["started_at"] = datetime.now(KST).isoformat()
            save_party_data()
            await update_party_recruit_message(party)
            await interaction.response.edit_message(
                embed=build_party_explore_embed(
                    party,
                    result_text=(
                        "⚔️ 파티 모험이 시작됐다! "
                        f"빈자리 **{PARTY_TOTAL_SLOTS - len(party_human_members(party))}개**는 NPC 용병이 채웠어."
                    ),
                ),
                view=PartyExploreView(self.party_id),
            )

    async def close_callback(self, interaction):
        async with get_party_lock(self.party_id):
            party = get_party(self.party_id)
            if not party or party.get("status") != "lobby":
                await interaction.response.send_message("❌ 해산할 수 있는 대기 파티가 아니야.", ephemeral=True)
                return
            if str(interaction.user.id) != str(party.get("leader_id")):
                await interaction.response.send_message("❌ 파티장만 해산할 수 있어.", ephemeral=True)
                return
            party["status"] = "closed"
            save_party_data()
            await update_party_recruit_message(party)
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="🔒 파티 해산",
                    description="파티장이 모집을 종료했어.",
                    color=discord.Color.dark_grey(),
                ),
                view=None,
            )


class PartyExploreView(discord.ui.View):
    def __init__(self, party_id):
        super().__init__(timeout=None)
        self.party_id = str(party_id)
        button = discord.ui.Button(
            label="탐험 시작",
            emoji="🥾",
            style=discord.ButtonStyle.primary,
            custom_id=f"party_next_turn:{self.party_id}",
        )
        button.callback = self.next_callback
        self.add_item(button)

    async def next_callback(self, interaction):
        async with get_party_lock(self.party_id):
            party = get_party(self.party_id)
            if not party or party.get("status") != "playing":
                await interaction.response.send_message("❌ 진행 중인 파티가 아니야.", ephemeral=True)
                return
            if str(interaction.user.id) != str(party.get("leader_id")):
                await interaction.response.send_message("❌ 탐험 시작은 파티장만 할 수 있어.", ephemeral=True)
                return
            run = party.get("run") or {}
            if run.get("phase") != "explore":
                await interaction.response.send_message("❌ 지금은 탐험을 시작할 수 없는 상태야.", ephemeral=True)
                return

            wait_seconds = random.randint(PARTY_EXPLORE_WAIT_MIN, PARTY_EXPLORE_WAIT_MAX)
            await interaction.response.edit_message(
                embed=build_party_travel_embed(party, wait_seconds),
                view=None,
            )
            await asyncio.sleep(wait_seconds)
            await start_party_encounter(interaction, party)


class PartyBattleView(discord.ui.View):
    def __init__(self, party_id):
        super().__init__(timeout=None)
        self.party_id = str(party_id)
        for label, emoji, style, action in [
            ("공격", "⚔️", discord.ButtonStyle.danger, "공격"),
            ("방어", "🛡️", discord.ButtonStyle.secondary, "방어"),
            ("직업 스킬", "✨", discord.ButtonStyle.primary, "직업 스킬"),
        ]:
            button = discord.ui.Button(
                label=label,
                emoji=emoji,
                style=style,
                custom_id=f"party_battle_{action}:{self.party_id}",
            )
            button.callback = self.make_action_callback(action)
            self.add_item(button)

        force_button = discord.ui.Button(
            label="미선택 인원 공격 처리",
            emoji="⏩",
            style=discord.ButtonStyle.secondary,
            custom_id=f"party_battle_force:{self.party_id}",
        )
        force_button.callback = self.force_callback
        self.add_item(force_button)

    def make_action_callback(self, action):
        async def callback(interaction):
            await self.record_action(interaction, action)
        return callback

    async def record_action(self, interaction, action):
        async with get_party_lock(self.party_id):
            party = get_party(self.party_id)
            uid = str(interaction.user.id)
            if not party or party.get("status") != "playing":
                await interaction.response.send_message("❌ 진행 중인 파티가 아니야.", ephemeral=True)
                return
            run = party.get("run") or {}
            battle = run.get("battle") or {}
            if run.get("phase") != "battle" or not battle:
                await interaction.response.send_message("❌ 지금은 전투 중이 아니야.", ephemeral=True)
                return
            player = party_get_player(party, uid)
            if not player or uid not in party_human_members(party):
                await interaction.response.send_message("❌ 이 파티의 유저 파티원이 아니야.", ephemeral=True)
                return
            if not player.get("alive"):
                await interaction.response.send_message("💀 전투 불능 상태라 다음 캠프까지 관전해야 해.", ephemeral=True)
                return
            if uid in battle.get("actions", {}):
                await interaction.response.send_message("❌ 이번 라운드 행동은 이미 골랐어.", ephemeral=True)
                return
            if action == "직업 스킬" and int(player.get("skill_cooldown", 0)) > 0:
                await interaction.response.send_message(
                    f"❌ 직업 스킬 재사용까지 **{int(player.get('skill_cooldown', 0))}라운드** 남았어.",
                    ephemeral=True,
                )
                return

            battle.setdefault("actions", {})[uid] = action
            alive_humans = party_alive_human_ids(party)
            ready = all(member_uid in battle.get("actions", {}) for member_uid in alive_humans)
            if not ready:
                save_party_data()
                await interaction.response.edit_message(embed=build_party_battle_embed(party), view=PartyBattleView(self.party_id))
                return

            result, _ = resolve_party_battle_round(party)
            if result == "victory":
                reward_text = reward_party_battle(party)
                decrement_party_battle_buffs(run)
                save_party_data()
                await party_complete_turn(interaction, party, reward_text)
                return
            if result == "defeat":
                party["status"] = "failed"
                run["phase"] = "ended"
                save_party_data()
                await update_party_recruit_message(party)
                await interaction.response.edit_message(
                    embed=party_run_summary_embed(
                        party,
                        victory=False,
                        reason="파티 전원이 전투에서 쓰러져 다음 캠프에 도달하지 못했다.",
                    ),
                    view=None,
                )
                return
            save_party_data()
            await interaction.response.edit_message(embed=build_party_battle_embed(party), view=PartyBattleView(self.party_id))

    async def force_callback(self, interaction):
        async with get_party_lock(self.party_id):
            party = get_party(self.party_id)
            if not party or party.get("status") != "playing":
                await interaction.response.send_message("❌ 진행 중인 파티가 아니야.", ephemeral=True)
                return
            if str(interaction.user.id) != str(party.get("leader_id")):
                await interaction.response.send_message("❌ 파티장만 강제 진행할 수 있어.", ephemeral=True)
                return
            run = party.get("run") or {}
            battle = run.get("battle") or {}
            if run.get("phase") != "battle" or not battle:
                await interaction.response.send_message("❌ 전투 중이 아니야.", ephemeral=True)
                return
            for uid in party_alive_human_ids(party):
                battle.setdefault("actions", {}).setdefault(uid, "공격")
            result, _ = resolve_party_battle_round(party)
            if result == "victory":
                reward_text = reward_party_battle(party)
                decrement_party_battle_buffs(run)
                save_party_data()
                await party_complete_turn(interaction, party, reward_text)
                return
            if result == "defeat":
                party["status"] = "failed"
                run["phase"] = "ended"
                save_party_data()
                await update_party_recruit_message(party)
                await interaction.response.edit_message(
                    embed=party_run_summary_embed(party, victory=False, reason="파티 전원이 쓰러졌다."),
                    view=None,
                )
                return
            save_party_data()
            await interaction.response.edit_message(embed=build_party_battle_embed(party), view=PartyBattleView(self.party_id))


class PartyEventView(discord.ui.View):
    def __init__(self, party_id):
        super().__init__(timeout=None)
        self.party_id = str(party_id)
        party = get_party(self.party_id) or {}
        run = party.get("run") or {}
        event = get_party_event_by_id(run.get("event_id"))
        for index, choice in enumerate(event.get("choices", [])[:4]):
            button = discord.ui.Button(
                label=choice.get("label", f"선택 {index + 1}"),
                emoji=choice.get("emoji"),
                style=discord.ButtonStyle.primary if index == 0 else discord.ButtonStyle.secondary,
                custom_id=f"party_event_{index}:{self.party_id}",
            )
            button.callback = self.make_vote_callback(index)
            self.add_item(button)

        force = discord.ui.Button(
            label="현재 투표로 결정",
            emoji="🗳️",
            style=discord.ButtonStyle.success,
            custom_id=f"party_event_force:{self.party_id}",
        )
        force.callback = self.force_callback
        self.add_item(force)

    def make_vote_callback(self, index):
        async def callback(interaction):
            await self.vote(interaction, index)
        return callback

    async def vote(self, interaction, index):
        async with get_party_lock(self.party_id):
            party = get_party(self.party_id)
            uid = str(interaction.user.id)
            if not party or party.get("status") != "playing":
                await interaction.response.send_message("❌ 진행 중인 파티가 아니야.", ephemeral=True)
                return
            run = party.get("run") or {}
            if run.get("phase") != "event" or uid not in party_human_members(party):
                await interaction.response.send_message("❌ 이 이벤트에 투표할 수 없어.", ephemeral=True)
                return
            event = get_party_event_by_id(run.get("event_id"))
            if index < 0 or index >= len(event.get("choices", [])):
                await interaction.response.send_message("❌ 존재하지 않는 선택지야.", ephemeral=True)
                return
            run.setdefault("event_votes", {})[uid] = index
            if len(run.get("event_votes", {})) < len(party_human_members(party)):
                save_party_data()
                await interaction.response.edit_message(embed=build_party_event_embed(party), view=PartyEventView(self.party_id))
                return
            await self.resolve_votes(interaction, party)

    async def force_callback(self, interaction):
        async with get_party_lock(self.party_id):
            party = get_party(self.party_id)
            if not party or party.get("status") != "playing":
                await interaction.response.send_message("❌ 진행 중인 파티가 아니야.", ephemeral=True)
                return
            if str(interaction.user.id) != str(party.get("leader_id")):
                await interaction.response.send_message("❌ 파티장만 현재 투표로 결정할 수 있어.", ephemeral=True)
                return
            run = party.get("run") or {}
            if run.get("phase") != "event":
                await interaction.response.send_message("❌ 이벤트 진행 중이 아니야.", ephemeral=True)
                return
            if not run.get("event_votes"):
                await interaction.response.send_message("❌ 아직 아무도 투표하지 않았어.", ephemeral=True)
                return
            await self.resolve_votes(interaction, party)

    async def resolve_votes(self, interaction, party):
        run = party.get("run") or {}
        event = get_party_event_by_id(run.get("event_id"))
        votes = run.get("event_votes", {})
        counts = {}
        for index in votes.values():
            counts[int(index)] = counts.get(int(index), 0) + 1
        best_count = max(counts.values())
        candidates = [index for index, count in counts.items() if count == best_count]
        leader_vote = votes.get(str(party.get("leader_id")))
        if leader_vote in candidates:
            selected_index = int(leader_vote)
        else:
            selected_index = min(candidates)
        choice = event.get("choices", [])[selected_index]
        outcome, text = resolve_party_event_outcome(party, choice)
        save_party_data()
        if outcome == "battle":
            await interaction.response.edit_message(embed=build_party_battle_embed(party), view=PartyBattleView(self.party_id))
        elif outcome == "merchant":
            await interaction.response.edit_message(embed=build_party_merchant_embed(party), view=PartyMerchantView(self.party_id))
        else:
            await party_complete_turn(interaction, party, f"🎭 **{choice.get('label')}** 선택 결과\n{text}")


class PartyMerchantSelect(discord.ui.Select):
    def __init__(self, party_id):
        self.party_id = str(party_id)
        party = get_party(self.party_id) or {}
        offers = (party.get("run") or {}).get("merchant_offers", [])
        options = []
        for offer in offers[:25]:
            catalog = WEAPONS if offer.get("kind") == "weapon" else ARMORS
            bonus = int(catalog.get(offer.get("name"), {}).get("bonus", 0))
            options.append(
                discord.SelectOption(
                    label=offer.get("name")[:100],
                    value=offer.get("id"),
                    emoji="🗡️" if offer.get("kind") == "weapon" else "🛡️",
                    description=f"보너스 +{bonus} · {int(offer.get('price', 0)):,}모라"[:100],
                )
            )
        if not options:
            options = [discord.SelectOption(label="판매 장비 없음", value="none")]
        super().__init__(
            placeholder="구매할 장비 선택",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"party_merchant_select:{self.party_id}",
            disabled=(offers == []),
        )

    async def callback(self, interaction):
        async with get_party_lock(self.party_id):
            party = get_party(self.party_id)
            uid = str(interaction.user.id)
            if not party or party.get("status") != "playing":
                await interaction.response.send_message("❌ 진행 중인 파티가 아니야.", ephemeral=True)
                return
            run = party.get("run") or {}
            if run.get("phase") != "merchant" or uid not in party_human_members(party):
                await interaction.response.send_message("❌ 지금 상점을 이용할 수 없어.", ephemeral=True)
                return
            player = party_get_player(party, uid)
            if not player or not player.get("alive"):
                await interaction.response.send_message("💀 관전 중에는 장비를 살 수 없어.", ephemeral=True)
                return
            offer_id = self.values[0]
            offer = next((item for item in run.get("merchant_offers", []) if item.get("id") == offer_id), None)
            if not offer:
                await interaction.response.send_message("❌ 이미 팔렸거나 존재하지 않는 장비야.", ephemeral=True)
                return
            price = int(offer.get("price", 0))
            if int(run.get("coins", 0)) < price:
                await interaction.response.send_message(
                    f"❌ 공용 모라가 부족해. 필요 **{price:,}**, 보유 **{int(run.get('coins', 0)):,}**",
                    ephemeral=True,
                )
                return
            run["coins"] = int(run.get("coins", 0)) - price
            give_party_equipment_to_player(player, offer, run)
            run["merchant_offers"] = [item for item in run.get("merchant_offers", []) if item.get("id") != offer_id]
            save_party_data()
            await interaction.response.edit_message(embed=build_party_merchant_embed(party), view=PartyMerchantView(self.party_id))


class PartyMerchantView(discord.ui.View):
    def __init__(self, party_id):
        super().__init__(timeout=None)
        self.party_id = str(party_id)
        self.add_item(PartyMerchantSelect(self.party_id))
        continue_button = discord.ui.Button(
            label="상인을 떠난다",
            emoji="➡️",
            style=discord.ButtonStyle.success,
            custom_id=f"party_merchant_continue:{self.party_id}",
        )
        continue_button.callback = self.continue_callback
        self.add_item(continue_button)

    async def continue_callback(self, interaction):
        async with get_party_lock(self.party_id):
            party = get_party(self.party_id)
            if not party or party.get("status") != "playing":
                await interaction.response.send_message("❌ 진행 중인 파티가 아니야.", ephemeral=True)
                return
            if str(interaction.user.id) != str(party.get("leader_id")):
                await interaction.response.send_message("❌ 파티장만 상인을 떠날 수 있어.", ephemeral=True)
                return
            run = party.get("run") or {}
            if run.get("phase") != "merchant":
                await interaction.response.send_message("❌ 지금은 상인과 거래 중이 아니야.", ephemeral=True)
                return
            await party_complete_turn(interaction, party, "🛒 상인과의 거래를 마쳤다.")


class PartyCampView(discord.ui.View):
    def __init__(self, party_id):
        super().__init__(timeout=None)
        self.party_id = str(party_id)
        buttons = [
            ("휴식 투표", "😴", discord.ButtonStyle.success, self.rest_callback, "rest"),
            ("요리하기", "🍳", discord.ButtonStyle.primary, self.cook_callback, "cook"),
            ("장비 변경", "🎒", discord.ButtonStyle.secondary, self.equipment_callback, "equipment"),
            ("공용 보관함", "📦", discord.ButtonStyle.secondary, self.storage_callback, "storage"),
            ("캠프 떠나기", "➡️", discord.ButtonStyle.danger, self.continue_callback, "continue"),
        ]
        for label, emoji, style, callback, key in buttons:
            button = discord.ui.Button(
                label=label,
                emoji=emoji,
                style=style,
                custom_id=f"party_camp_{key}:{self.party_id}",
            )
            button.callback = callback
            self.add_item(button)

    async def rest_callback(self, interaction):
        async with get_party_lock(self.party_id):
            party = get_party(self.party_id)
            uid = str(interaction.user.id)
            if not party or party.get("status") != "playing":
                await interaction.response.send_message("❌ 진행 중인 파티가 아니야.", ephemeral=True)
                return
            run = party.get("run") or {}
            if run.get("phase") != "camp" or uid not in party_human_members(party):
                await interaction.response.send_message("❌ 지금 휴식 투표를 할 수 없어.", ephemeral=True)
                return
            if run.get("camp_locked", {}).get(uid):
                await interaction.response.send_message(
                    "❌ 이번 캠프에서 요리하거나 장비를 보관함에 올려서 바로 휴식할 수 없어.",
                    ephemeral=True,
                )
                return
            remaining = PARTY_REST_COOLDOWN_TURNS - (int(run.get("turn", 0)) - int(run.get("last_rest_turn", -999)))
            if remaining > 0:
                await interaction.response.send_message(f"❌ 휴식 쿨타임이 **{remaining}턴** 남았어.", ephemeral=True)
                return
            votes = run.setdefault("rest_votes", [])
            if uid in votes:
                await interaction.response.send_message("❌ 이미 휴식에 투표했어.", ephemeral=True)
                return
            votes.append(uid)
            needed = max(1, math.ceil(len(party_human_members(party)) / 2))
            notice = f"😴 <@{uid}> 휴식 투표 · {len(votes)}/{needed}"
            if len(votes) >= needed:
                for player in run.get("players", {}).values():
                    player["alive"] = True
                    player["lives"] = 1
                    refresh_party_player_max_hp(player, run, keep_ratio=False)
                    player["hp"] = player["max_hp"]
                run["last_rest_turn"] = int(run.get("turn", 0))
                run["rest_votes"] = []
                notice = "💤 파티 절반 이상이 휴식에 동의했다! 전원의 생명 1과 체력이 모두 회복됐다."
            save_party_data()
            await interaction.response.edit_message(
                embed=build_party_camp_embed(party, notice),
                view=PartyCampView(self.party_id),
            )

    async def cook_callback(self, interaction):
        party = get_party(self.party_id)
        uid = str(interaction.user.id)
        if not party or party.get("status") != "playing" or uid not in party_human_members(party):
            await interaction.response.send_message("❌ 이 캠프에서 요리할 수 없어.", ephemeral=True)
            return
        run = party.get("run") or {}
        if run.get("phase") != "camp":
            await interaction.response.send_message("❌ 요리는 캠프에서만 할 수 있어.", ephemeral=True)
            return
        player = party_get_player(party, uid)
        await interaction.response.send_message(
            embed=build_party_cooking_embed(player),
            view=PartyCookingView(self.party_id, uid),
            ephemeral=True,
        )

    async def equipment_callback(self, interaction):
        party = get_party(self.party_id)
        uid = str(interaction.user.id)
        if not party or party.get("status") != "playing" or uid not in party_human_members(party):
            await interaction.response.send_message("❌ 이 캠프의 파티원이 아니야.", ephemeral=True)
            return
        if (party.get("run") or {}).get("phase") != "camp":
            await interaction.response.send_message("❌ 장비 변경은 캠프에서만 가능해.", ephemeral=True)
            return
        await interaction.response.send_message(
            embed=build_party_equipment_manage_embed(party_get_player(party, uid)),
            view=PartyEquipmentView(self.party_id, uid),
            ephemeral=True,
        )

    async def storage_callback(self, interaction):
        party = get_party(self.party_id)
        uid = str(interaction.user.id)
        if not party or party.get("status") != "playing" or uid not in party_human_members(party):
            await interaction.response.send_message("❌ 이 캠프의 파티원이 아니야.", ephemeral=True)
            return
        if (party.get("run") or {}).get("phase") != "camp":
            await interaction.response.send_message("❌ 공용 보관함은 캠프에서만 이용할 수 있어.", ephemeral=True)
            return
        await interaction.response.send_message(
            embed=build_party_storage_embed(party, uid),
            view=PartyStorageView(self.party_id, uid),
            ephemeral=True,
        )

    async def continue_callback(self, interaction):
        async with get_party_lock(self.party_id):
            party = get_party(self.party_id)
            if not party or party.get("status") != "playing":
                await interaction.response.send_message("❌ 진행 중인 파티가 아니야.", ephemeral=True)
                return
            if str(interaction.user.id) != str(party.get("leader_id")):
                await interaction.response.send_message("❌ 파티장만 캠프를 떠날 수 있어.", ephemeral=True)
                return
            run = party.get("run") or {}
            if run.get("phase") != "camp":
                await interaction.response.send_message("❌ 지금은 캠프가 아니야.", ephemeral=True)
                return
            if run.get("pending_route"):
                routes = ADVENTURE_TERRAIN_ROUTES.get(run.get("terrain"), [])
                if not routes:
                    party["status"] = "completed"
                    run["phase"] = "ended"
                    save_party_data()
                    await update_party_recruit_message(party)
                    await interaction.response.edit_message(
                        embed=party_run_summary_embed(party, victory=True, reason="마지막 보스를 격파하고 모험을 완주했다!"),
                        view=None,
                    )
                    return
                run["phase"] = "route"
                save_party_data()
                await interaction.response.edit_message(embed=build_party_route_embed(party), view=PartyRouteView(self.party_id))
                return
            run["phase"] = "explore"
            save_party_data()
            await interaction.response.edit_message(
                embed=build_party_explore_embed(party, result_text="🏕️ 캠프 정비를 마치고 다시 길을 나섰다."),
                view=PartyExploreView(self.party_id),
            )


def build_party_cooking_embed(player):
    materials = player.get("materials", {}) if player else {}
    material_text = ", ".join(
        f"{name} ×{amount}" for name, amount in materials.items() if int(amount) > 0
    ) or "보유 재료 없음"
    recipe_lines = []
    for name, recipe in PARTY_RECIPES.items():
        ingredient_text = ", ".join(f"{item} ×{amount}" for item, amount in recipe["ingredients"].items())
        recipe_lines.append(f"**{name}** — {ingredient_text}\n└ {recipe['desc']}")
    return discord.Embed(
        title="🍳 캠프 요리",
        description=(
            f"보유 재료: {material_text}\n\n"
            + "\n\n".join(recipe_lines)
            + "\n\n요리에 성공하면 이번 캠프에서는 휴식 투표를 할 수 없어."
        ),
        color=discord.Color.orange(),
    )


class PartyCookingSelect(discord.ui.Select):
    def __init__(self, party_id, uid):
        self.party_id = str(party_id)
        self.uid = str(uid)
        options = [
            discord.SelectOption(
                label=name,
                value=name,
                emoji="🍲",
                description=recipe["desc"][:100],
            )
            for name, recipe in PARTY_RECIPES.items()
        ]
        super().__init__(placeholder="만들 요리 선택", options=options, min_values=1, max_values=1)

    async def callback(self, interaction):
        if str(interaction.user.id) != self.uid:
            await interaction.response.send_message("❌ 이 요리 창의 주인이 아니야.", ephemeral=True)
            return
        async with get_party_lock(self.party_id):
            party = get_party(self.party_id)
            run = (party or {}).get("run") or {}
            if not party or party.get("status") != "playing" or run.get("phase") != "camp":
                await interaction.response.send_message("❌ 지금은 요리할 수 없어.", ephemeral=True)
                return
            player = party_get_player(party, self.uid)
            recipe_name = self.values[0]
            recipe = PARTY_RECIPES.get(recipe_name)
            materials = player.setdefault("materials", {})
            missing = [
                f"{name} {amount - int(materials.get(name, 0))}개"
                for name, amount in recipe["ingredients"].items()
                if int(materials.get(name, 0)) < amount
            ]
            if missing:
                await interaction.response.send_message("❌ 재료 부족: " + ", ".join(missing), ephemeral=True)
                return
            for name, amount in recipe["ingredients"].items():
                materials[name] = int(materials.get(name, 0)) - amount
                if materials[name] <= 0:
                    materials.pop(name, None)

            effect = recipe["effect"]
            if effect == "heal":
                for target in run.get("players", {}).values():
                    if target.get("alive"):
                        heal = max(1, int(target.get("max_hp", 1) * float(recipe["value"])))
                        target["hp"] = min(int(target.get("max_hp", 1)), int(target.get("hp", 0)) + heal)
            elif effect == "attack_battles":
                run.setdefault("buffs", {})["attack_battles"] = max(
                    int(run.get("buffs", {}).get("attack_battles", 0)), int(recipe["value"])
                )
            elif effect == "attack_strong":
                run.setdefault("buffs", {})["attack_strong"] = max(
                    int(run.get("buffs", {}).get("attack_strong", 0)), int(recipe["value"])
                )
            elif effect == "defense_battles":
                run.setdefault("buffs", {})["defense_battles"] = max(
                    int(run.get("buffs", {}).get("defense_battles", 0)), int(recipe["value"])
                )
            elif effect == "self_full_heal":
                player["hp"] = int(player.get("max_hp", 1))

            run.setdefault("camp_locked", {})[self.uid] = True
            run["rest_votes"] = [uid for uid in run.get("rest_votes", []) if uid != self.uid]
            save_party_data()
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="🍳 요리 완료",
                    description=f"**{recipe_name}**을 만들었어.\n{recipe['desc']}\n\n이번 캠프에서는 휴식 투표를 할 수 없어.",
                    color=discord.Color.orange(),
                ),
                view=None,
            )


class PartyCookingView(discord.ui.View):
    def __init__(self, party_id, uid):
        super().__init__(timeout=180)
        self.add_item(PartyCookingSelect(party_id, uid))


def build_party_equipment_manage_embed(player):
    if not player:
        return discord.Embed(title="장비 정보 없음")
    weapons = ", ".join(player.get("bag_weapons", [])) or "없음"
    armors = ", ".join(player.get("bag_armors", [])) or "없음"
    return discord.Embed(
        title=f"🎒 {player.get('name')} 장비 관리",
        description=(
            f"현재 무기: **{player.get('weapon')}**\n"
            f"현재 방어구: **{player.get('armor')}**\n\n"
            f"가방 무기: {weapons}\n"
            f"가방 방어구: {armors}\n\n"
            "장비를 바꾸면 기존 착용 장비는 가방으로 들어가."
        ),
        color=discord.Color.blue(),
    )


class PartyEquipSelect(discord.ui.Select):
    def __init__(self, party_id, uid, kind):
        self.party_id = str(party_id)
        self.uid = str(uid)
        self.kind = kind
        party = get_party(self.party_id) or {}
        player = party_get_player(party, self.uid) or {}
        names = player.get("bag_weapons" if kind == "weapon" else "bag_armors", [])
        catalog = WEAPONS if kind == "weapon" else ARMORS
        options = []
        for index, name in enumerate(names[:25]):
            options.append(
                discord.SelectOption(
                    label=name[:100],
                    value=str(index),
                    emoji="🗡️" if kind == "weapon" else "🛡️",
                    description=f"보너스 +{int(catalog.get(name, {}).get('bonus', 0))}"[:100],
                )
            )
        if not options:
            options = [discord.SelectOption(label="교체할 장비 없음", value="none")]
        super().__init__(
            placeholder="무기 변경" if kind == "weapon" else "방어구 변경",
            options=options,
            min_values=1,
            max_values=1,
            disabled=(names == []),
        )

    async def callback(self, interaction):
        if str(interaction.user.id) != self.uid:
            await interaction.response.send_message("❌ 이 장비 창의 주인이 아니야.", ephemeral=True)
            return
        async with get_party_lock(self.party_id):
            party = get_party(self.party_id)
            run = (party or {}).get("run") or {}
            if not party or run.get("phase") != "camp":
                await interaction.response.send_message("❌ 캠프에서만 장비를 바꿀 수 있어.", ephemeral=True)
                return
            player = party_get_player(party, self.uid)
            bag_key = "bag_weapons" if self.kind == "weapon" else "bag_armors"
            equip_key = "weapon" if self.kind == "weapon" else "armor"
            bag = player.setdefault(bag_key, [])
            try:
                index = int(self.values[0])
                new_name = bag.pop(index)
            except (ValueError, IndexError):
                await interaction.response.send_message("❌ 장비가 없어.", ephemeral=True)
                return
            old_name = player.get(equip_key)
            basic = PARTY_BASIC_WEAPON if self.kind == "weapon" else PARTY_BASIC_ARMOR
            if old_name and old_name != basic:
                bag.append(old_name)
            player[equip_key] = new_name
            refresh_party_player_max_hp(player, run, keep_ratio=True)
            save_party_data()
            await interaction.response.edit_message(
                embed=build_party_equipment_manage_embed(player),
                view=PartyEquipmentView(self.party_id, self.uid),
            )


class PartyEquipmentView(discord.ui.View):
    def __init__(self, party_id, uid):
        super().__init__(timeout=180)
        self.add_item(PartyEquipSelect(party_id, uid, "weapon"))
        self.add_item(PartyEquipSelect(party_id, uid, "armor"))


def build_party_storage_embed(party, uid):
    run = party.get("run") or {}
    player = party_get_player(party, uid) or {}
    bag_items = [f"🗡️ {name}" for name in player.get("bag_weapons", [])] + [
        f"🛡️ {name}" for name in player.get("bag_armors", [])
    ]
    storage_items = [
        f"{'🗡️' if item.get('kind') == 'weapon' else '🛡️'} {item.get('name')}"
        for item in run.get("shared_storage", [])
    ]
    return discord.Embed(
        title="📦 캠프 공용 보관함",
        description=(
            "### 내 가방의 미착용 장비\n"
            + ("\n".join(bag_items) if bag_items else "없음")
            + "\n\n### 공용 보관함\n"
            + ("\n".join(storage_items) if storage_items else "비어 있음")
            + "\n\n착용 중인 장비는 올릴 수 없어. 장비를 올리면 이번 캠프에서 휴식할 수 없어."
        ),
        color=discord.Color.dark_gold(),
    )


class PartyStorageDepositSelect(discord.ui.Select):
    def __init__(self, party_id, uid):
        self.party_id = str(party_id)
        self.uid = str(uid)
        party = get_party(self.party_id) or {}
        player = party_get_player(party, self.uid) or {}
        items = []
        for index, name in enumerate(player.get("bag_weapons", [])):
            items.append((f"w:{index}", "weapon", name))
        for index, name in enumerate(player.get("bag_armors", [])):
            items.append((f"a:{index}", "armor", name))
        options = [
            discord.SelectOption(
                label=name[:100],
                value=value,
                emoji="🗡️" if kind == "weapon" else "🛡️",
            )
            for value, kind, name in items[:25]
        ]
        if not options:
            options = [discord.SelectOption(label="올릴 장비 없음", value="none")]
        super().__init__(
            placeholder="공용 보관함에 올릴 장비",
            options=options,
            min_values=1,
            max_values=1,
            disabled=(items == []),
        )

    async def callback(self, interaction):
        if str(interaction.user.id) != self.uid:
            await interaction.response.send_message("❌ 이 보관함 창의 주인이 아니야.", ephemeral=True)
            return
        async with get_party_lock(self.party_id):
            party = get_party(self.party_id)
            run = (party or {}).get("run") or {}
            if not party or run.get("phase") != "camp":
                await interaction.response.send_message("❌ 캠프에서만 보관함을 이용할 수 있어.", ephemeral=True)
                return
            player = party_get_player(party, self.uid)
            try:
                prefix, index_text = self.values[0].split(":", 1)
                index = int(index_text)
            except (ValueError, AttributeError):
                await interaction.response.send_message("❌ 올릴 장비가 없어.", ephemeral=True)
                return
            if prefix == "w":
                bag = player.setdefault("bag_weapons", [])
                kind = "weapon"
            else:
                bag = player.setdefault("bag_armors", [])
                kind = "armor"
            if index < 0 or index >= len(bag):
                await interaction.response.send_message("❌ 장비가 이미 이동됐어.", ephemeral=True)
                return
            name = bag.pop(index)
            run.setdefault("shared_storage", []).append({"kind": kind, "name": name, "from": self.uid})
            run.setdefault("camp_locked", {})[self.uid] = True
            run["rest_votes"] = [uid for uid in run.get("rest_votes", []) if uid != self.uid]
            save_party_data()
            await interaction.response.edit_message(
                embed=build_party_storage_embed(party, self.uid),
                view=PartyStorageView(self.party_id, self.uid),
            )


class PartyStorageWithdrawSelect(discord.ui.Select):
    def __init__(self, party_id, uid):
        self.party_id = str(party_id)
        self.uid = str(uid)
        party = get_party(self.party_id) or {}
        storage = (party.get("run") or {}).get("shared_storage", [])
        options = [
            discord.SelectOption(
                label=item.get("name", "장비")[:100],
                value=str(index),
                emoji="🗡️" if item.get("kind") == "weapon" else "🛡️",
            )
            for index, item in enumerate(storage[:25])
        ]
        if not options:
            options = [discord.SelectOption(label="가져올 장비 없음", value="none")]
        super().__init__(
            placeholder="공용 보관함에서 가져올 장비",
            options=options,
            min_values=1,
            max_values=1,
            disabled=(storage == []),
        )

    async def callback(self, interaction):
        if str(interaction.user.id) != self.uid:
            await interaction.response.send_message("❌ 이 보관함 창의 주인이 아니야.", ephemeral=True)
            return
        async with get_party_lock(self.party_id):
            party = get_party(self.party_id)
            run = (party or {}).get("run") or {}
            if not party or run.get("phase") != "camp":
                await interaction.response.send_message("❌ 캠프에서만 보관함을 이용할 수 있어.", ephemeral=True)
                return
            try:
                index = int(self.values[0])
                item = run.setdefault("shared_storage", []).pop(index)
            except (ValueError, IndexError):
                await interaction.response.send_message("❌ 장비가 이미 이동됐어.", ephemeral=True)
                return
            player = party_get_player(party, self.uid)
            give_party_equipment_to_player(player, item, run)
            save_party_data()
            await interaction.response.edit_message(
                embed=build_party_storage_embed(party, self.uid),
                view=PartyStorageView(self.party_id, self.uid),
            )


class PartyStorageView(discord.ui.View):
    def __init__(self, party_id, uid):
        super().__init__(timeout=180)
        self.add_item(PartyStorageDepositSelect(party_id, uid))
        self.add_item(PartyStorageWithdrawSelect(party_id, uid))


class PartyRouteSelect(discord.ui.Select):
    def __init__(self, party_id):
        self.party_id = str(party_id)
        party = get_party(self.party_id) or {}
        run = party.get("run") or {}
        routes = ADVENTURE_TERRAIN_ROUTES.get(run.get("terrain"), [])
        options = [
            discord.SelectOption(
                label=ADVENTURE_TERRAINS[key]["name"],
                value=key,
                emoji=ADVENTURE_TERRAINS[key]["emoji"],
                description=ADVENTURE_TERRAINS[key]["description"][:100],
            )
            for key in routes[:25]
            if key in ADVENTURE_TERRAINS
        ]
        if not options:
            options = [discord.SelectOption(label="이어지는 지형 없음", value="none")]
        super().__init__(
            placeholder="다음 지형 선택",
            options=options,
            min_values=1,
            max_values=1,
            custom_id=f"party_route_select:{self.party_id}",
            disabled=(routes == []),
        )

    async def callback(self, interaction):
        async with get_party_lock(self.party_id):
            party = get_party(self.party_id)
            if not party or party.get("status") != "playing":
                await interaction.response.send_message("❌ 진행 중인 파티가 아니야.", ephemeral=True)
                return
            if str(interaction.user.id) != str(party.get("leader_id")):
                await interaction.response.send_message("❌ 파티장만 다음 지형을 선택할 수 있어.", ephemeral=True)
                return
            run = party.get("run") or {}
            destination = self.values[0]
            if destination not in ADVENTURE_TERRAIN_ROUTES.get(run.get("terrain"), []):
                await interaction.response.send_message("❌ 이동할 수 없는 지형이야.", ephemeral=True)
                return
            run["terrain"] = destination
            run["pending_route"] = False
            run["phase"] = "explore"
            save_party_data()
            await interaction.response.edit_message(
                embed=build_party_explore_embed(
                    party,
                    result_text=f"🗺️ 파티가 **{get_terrain_display(destination)}**에 진입했다.",
                ),
                view=PartyExploreView(self.party_id),
            )


class PartyRouteView(discord.ui.View):
    def __init__(self, party_id):
        super().__init__(timeout=None)
        self.add_item(PartyRouteSelect(party_id))


def migrate_party_battle_balance():
    """이전 파티 저장본을 새 전용 레벨·종료 투표·전투 밸런스로 마이그레이션한다."""
    changed = False
    for party in party_data.get("parties", {}).values():
        if party.get("status") != "playing":
            continue
        run = party.get("run") or {}
        if "end_votes" not in run:
            run["end_votes"] = []
            changed = True

        if int(run.get("level_system_version", 0)) < PARTY_LEVEL_SYSTEM_VERSION:
            for player in run.get("players", {}).values():
                player["level"] = 1
                player["party_exp"] = 0
                refresh_party_player_max_hp(player, run, keep_ratio=True)
            run["level_system_version"] = PARTY_LEVEL_SYSTEM_VERSION
            changed = True

        battle = run.get("battle") or {}
        old_monster = battle.get("monster") or {}
        if old_monster and int(old_monster.get("balance_version", 0)) < PARTY_BALANCE_VERSION:
            old_max_hp = max(1, int(old_monster.get("max_hp", 1)))
            hp_ratio = max(0.0, min(1.0, int(old_monster.get("hp", old_max_hp)) / old_max_hp))
            refreshed = create_party_monster(
                party,
                elite=bool(old_monster.get("is_elite")),
                boss=bool(old_monster.get("is_boss")),
                forced_name=old_monster.get("name"),
            )
            refreshed["hp"] = max(1, int(round(refreshed["max_hp"] * hp_ratio)))
            battle["monster"] = refreshed
            changed = True

    if changed:
        save_party_data()
        print("파티 모험: 전용 레벨 및 최신 밸런스로 진행 중 파티를 조정함")


def restore_party_persistent_views():
    for party_id, party in party_data.get("parties", {}).items():
        if party.get("status") not in {"lobby", "playing"}:
            continue
        view_factories = [PartyRecruitView]
        if party.get("status") == "lobby":
            view_factories.append(PartyLobbyView)
        else:
            view_factories.extend([
                PartyExploreView,
                PartyBattleView,
                PartyEventView,
                PartyMerchantView,
                PartyCampView,
                PartyRouteView,
            ])
        for factory in view_factories:
            key = (party_id, factory.__name__)
            if key in party_registered_view_keys:
                continue
            try:
                bot.add_view(factory(party_id))
                party_registered_view_keys.add(key)
            except Exception as error:
                print(f"파티 persistent view 등록 실패 {party_id}/{factory.__name__}: {error}")


@bot.tree.command(name="파티생성", description="최대 4명의 파티 모험을 만들고 모집 스레드를 생성한다", guild=GUILD)
@app_commands.describe(
    파티이름="모집 글에 표시할 파티 이름",
    하드모드="파티장이 하드 모드를 해금했다면 모든 파티원에게 적용",
)
async def party_create_command(
    interaction: discord.Interaction,
    파티이름: str = None,
    하드모드: bool = False,
):
    uid = str(interaction.user.id)
    existing = find_user_party(uid)
    if existing:
        await interaction.response.send_message(
            f"❌ 이미 **{existing.get('name')}** 파티에 들어가 있어. 먼저 `/나가기`를 사용해줘.",
            ephemeral=True,
        )
        return
    if 하드모드 and not is_adventure_hard_mode_unlocked(get_adventure(uid)):
        await interaction.response.send_message(
            "❌ 개인 모험에서 하드 모드를 해금한 파티장만 하드 파티를 만들 수 있어.",
            ephemeral=True,
        )
        return

    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    if not guild:
        await interaction.followup.send("❌ 서버에서만 사용할 수 있어.", ephemeral=True)
        return

    recruit_channel = None
    if PARTY_RECRUIT_CHANNEL_ID:
        recruit_channel = guild.get_channel(PARTY_RECRUIT_CHANNEL_ID)
    if recruit_channel is None:
        if isinstance(interaction.channel, discord.Thread):
            recruit_channel = interaction.channel.parent
        else:
            recruit_channel = interaction.channel
    if not isinstance(recruit_channel, discord.TextChannel):
        await interaction.followup.send(
            "❌ 파티 모집 채널을 찾지 못했어. `PARTY_RECRUIT_CHANNEL_ID`에 일반 텍스트 채널 ID를 넣어줘.",
            ephemeral=True,
        )
        return

    party_id = next_party_id()
    clean_name = (파티이름 or f"{interaction.user.display_name}의 원정대").strip()[:40]
    if not clean_name:
        clean_name = f"파티 {party_id}"
    party = {
        "id": party_id,
        "name": clean_name,
        "guild_id": guild.id,
        "leader_id": uid,
        "members": [uid],
        "jobs": {uid: None},
        "hard_mode": bool(하드모드),
        "start_terrain": "grassland",
        "status": "lobby",
        "recruit_channel_id": recruit_channel.id,
        "recruit_message_id": None,
        "thread_id": None,
        "lobby_message_id": None,
        "created_at": datetime.now(KST).isoformat(),
        "run": None,
    }
    party_data.setdefault("parties", {})[party_id] = party
    save_party_data()

    try:
        recruit_message = await recruit_channel.send(
            embed=build_party_recruit_embed(party),
            view=PartyRecruitView(party_id),
        )
        thread_name = f"🧭-{clean_name}-{party_id}"[:100]
        thread = await recruit_message.create_thread(name=thread_name, auto_archive_duration=1440)
        party["recruit_message_id"] = recruit_message.id
        party["thread_id"] = thread.id
        try:
            await thread.add_user(interaction.user)
        except (discord.Forbidden, discord.HTTPException):
            pass
        lobby_message = await thread.send(
            content=f"{interaction.user.mention} 파티장이 생성한 파티 모험 스레드야!",
            embed=build_party_lobby_embed(party),
            view=PartyLobbyView(party_id),
        )
        party["lobby_message_id"] = lobby_message.id
        save_party_data()
        await recruit_message.edit(embed=build_party_recruit_embed(party), view=PartyRecruitView(party_id))
        restore_party_persistent_views()
        await interaction.followup.send(
            f"✅ 파티를 만들었어! 모집 글: {recruit_message.jump_url}\n파티 스레드: {thread.mention}",
            ephemeral=True,
        )
    except discord.Forbidden:
        party_data.get("parties", {}).pop(party_id, None)
        save_party_data()
        await interaction.followup.send(
            "❌ 봇에게 `메시지 보내기`, `공개 스레드 만들기`, `스레드에서 메시지 보내기`, `스레드 관리` 권한이 필요해.",
            ephemeral=True,
        )
    except discord.HTTPException as error:
        party_data.get("parties", {}).pop(party_id, None)
        save_party_data()
        await interaction.followup.send(f"❌ 파티를 만드는 중 오류가 났어: `{error}`", ephemeral=True)


@bot.tree.command(name="나가기", description="현재 참가 중인 파티에서 나간다", guild=GUILD)
async def party_leave_command(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    party = find_user_party(uid)
    if not party:
        await interaction.response.send_message("❌ 참가 중인 파티가 없어.", ephemeral=True)
        return

    party_id = party.get("id")
    async with get_party_lock(party_id):
        party = get_party(party_id)
        if not party or uid not in party_human_members(party):
            await interaction.response.send_message("❌ 참가 중인 파티가 없어.", ephemeral=True)
            return

        status = party.get("status")
        party["members"] = [member_uid for member_uid in party_human_members(party) if member_uid != uid]
        party.setdefault("jobs", {}).pop(uid, None)

        if status == "playing":
            run = party.get("run") or {}
            run["end_votes"] = [vote_uid for vote_uid in run.get("end_votes", []) if vote_uid != uid]
            player = run.get("players", {}).get(uid)
            if player:
                player["is_bot"] = True
                player["user_id"] = None
                player["name"] = f"대체 용병 ({player.get('job', '전사')})"

        if not party_human_members(party):
            party["status"] = "abandoned"
            if party.get("run"):
                party["run"]["phase"] = "ended"
        elif uid == str(party.get("leader_id")):
            party["leader_id"] = party_human_members(party)[0]

        save_party_data()
        thread = get_party_thread(party)
        if thread:
            try:
                await thread.remove_user(interaction.user)
            except (discord.Forbidden, discord.HTTPException):
                pass
        await interaction.response.send_message(f"✅ **{party.get('name')}** 파티에서 나갔어.", ephemeral=True)
        await update_party_recruit_message(party)
        if party.get("status") == "lobby":
            await update_party_lobby_message(party)
        elif party.get("status") == "abandoned" and thread:
            try:
                await thread.send("🔒 유저 파티원이 모두 나가 파티 모험이 종료됐어.")
            except discord.HTTPException:
                pass


@bot.tree.command(name="파티종료", description="진행 중인 파티 모험의 중도 종료에 투표한다", guild=GUILD)
async def party_end_vote_command(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    party = find_user_party(uid)
    if not party or party.get("status") != "playing":
        await interaction.response.send_message("❌ 진행 중인 파티 모험에 참가하고 있지 않아.", ephemeral=True)
        return

    party_id = party.get("id")
    async with get_party_lock(party_id):
        party = get_party(party_id)
        if not party or party.get("status") != "playing" or uid not in party_human_members(party):
            await interaction.response.send_message("❌ 진행 중인 파티 모험에 참가하고 있지 않아.", ephemeral=True)
            return

        run = party.get("run") or {}
        humans = party_human_members(party)
        votes = [member_uid for member_uid in run.setdefault("end_votes", []) if member_uid in humans]
        run["end_votes"] = votes
        needed = party_end_vote_needed(party)

        if uid in votes:
            await interaction.response.send_message(
                f"❌ 이미 종료에 투표했어. 현재 **{len(votes)}/{needed}표**야.",
                ephemeral=True,
            )
            return

        votes.append(uid)
        save_party_data()
        if len(votes) < needed:
            await interaction.response.send_message(
                f"🏳️ {interaction.user.mention}이 파티 모험 종료에 투표했어. "
                f"현재 **{len(votes)}/{needed}표** · 실제 유저 과반수가 필요해.",
            )
            return

        party["status"] = "abandoned"
        party["closed_at"] = datetime.now(KST).isoformat()
        run["phase"] = "ended"
        run["ended_by_vote"] = True
        save_party_data()
        await update_party_recruit_message(party)

        reason = (
            f"실제 파티원 **{len(votes)}/{len(humans)}명**이 종료에 동의해 "
            "파티 모험을 중도 종료했다. NPC 용병은 투표 수에 포함되지 않아."
        )
        summary = party_run_summary_embed(party, victory=False, reason=reason, voluntary=True)
        thread = get_party_thread(party)
        if thread and interaction.channel_id != thread.id:
            try:
                await thread.send(embed=summary)
            except discord.HTTPException:
                pass
        await interaction.response.send_message(embed=summary)


@bot.tree.command(name="파티상태", description="현재 참가 중인 파티 상태를 확인한다", guild=GUILD)
async def party_status_command(interaction: discord.Interaction):
    party = find_user_party(interaction.user.id)
    if not party:
        await interaction.response.send_message("❌ 참가 중인 파티가 없어.", ephemeral=True)
        return
    if party.get("status") == "lobby":
        embed = build_party_lobby_embed(party)
    else:
        phase = (party.get("run") or {}).get("phase")
        if phase == "battle":
            embed = build_party_battle_embed(party)
        elif phase == "camp":
            embed = build_party_camp_embed(party)
        elif phase == "merchant":
            embed = build_party_merchant_embed(party)
        elif phase == "event":
            embed = build_party_event_embed(party)
        elif phase == "route":
            embed = build_party_route_embed(party)
        else:
            embed = build_party_explore_embed(party)
    thread = get_party_thread(party)
    content = thread.mention if thread else None
    await interaction.response.send_message(content=content, embed=embed, ephemeral=True)


@bot.tree.command(name="원정프로필", description="파티 원정의 영구 기록과 원정 인장을 확인한다", guild=GUILD)
async def expedition_profile_command(interaction: discord.Interaction):
    profile = get_party_profile(interaction.user.id)
    best_depth = int(profile.get("best_depth", 0))
    best_terrain = next(
        (info.get("name", key) for key, info in ADVENTURE_TERRAINS.items() if ADVENTURE_TERRAIN_DEPTH.get(key) == best_depth),
        "기록 없음",
    )
    titles = ", ".join(profile.get("titles", [])) or "없음"
    embed = discord.Embed(title=f"🧭 {interaction.user.display_name}의 원정 프로필", color=discord.Color.teal())
    embed.add_field(
        name="영구 기록",
        value=(
            f"{PARTY_TOKEN_NAME}: **{profile['tokens']:,}개**\n"
            f"참가: **{profile['runs']}회** · 완주: **{profile['clears']}회** · 하드 완주: **{profile['hard_clears']}회**\n"
            f"누적 보스: **{profile['boss_kills']}마리** · 누적 턴: **{profile['total_turns']}턴**\n"
            f"최고 도달: **{best_terrain}**\n칭호: **{titles}**"
        ),
        inline=False,
    )
    embed.set_footer(text="원정 내부 레벨·장비·유물은 매 판 초기화되지만 이 기록과 인장은 유지돼.")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="원정교환", description="원정 인장을 영구 보상으로 교환한다", guild=GUILD)
@app_commands.describe(보상="교환할 보상")
@app_commands.choices(보상=[
    app_commands.Choice(name="100 인장 → 20,000 모라", value="mora"),
    app_commands.Choice(name="250 인장 → 160 원석", value="primogem"),
    app_commands.Choice(name="1,000 인장 → 숙련 원정대원 칭호", value="title"),
])
async def expedition_exchange_command(interaction: discord.Interaction, 보상: app_commands.Choice[str]):
    uid = str(interaction.user.id)
    profile = get_party_profile(uid)
    rewards = {
        "mora": (100, "20,000 모라"),
        "primogem": (250, "160 원석"),
        "title": (1000, "숙련 원정대원 칭호"),
    }
    cost, label = rewards[보상.value]
    if profile["tokens"] < cost:
        await interaction.response.send_message(
            f"❌ {PARTY_TOKEN_NAME}이 부족해. 필요 **{cost}개**, 보유 **{profile['tokens']}개**",
            ephemeral=True,
        )
        return
    if 보상.value == "title" and "숙련 원정대원" in profile["titles"]:
        await interaction.response.send_message("❌ 이미 그 칭호를 보유하고 있어.", ephemeral=True)
        return
    profile["tokens"] -= cost
    if 보상.value == "mora":
        add_poker_money(uid, 20_000)
    elif 보상.value == "primogem":
        add_primogems(uid, 160)
    else:
        profile["titles"].append("숙련 원정대원")
    save_data()
    await interaction.response.send_message(
        f"✅ {PARTY_TOKEN_NAME} **{cost}개**를 사용해 **{label}**을(를) 받았어.\n"
        f"남은 인장: **{profile['tokens']}개**"
    )


@bot.tree.command(name="게임프로필", description="서버 활동·사냥·개인 모험·파티 원정 진행도를 한 번에 확인한다", guild=GUILD)
async def game_profile_command(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    activity = get_level_data(interaction.user.id)
    hunt_user = get_hunt_user(uid)
    adventure = get_adventure(uid)
    expedition = get_party_profile(uid)
    user_chars = characters.get(uid, {})
    equipped_relics = get_equipped_relic_ids(uid)

    embed = discord.Embed(title=f"🎮 {interaction.user.display_name}의 게임 프로필", color=discord.Color.blurple())
    embed.add_field(
        name="💬 서버 활동 레벨",
        value=f"Lv.**{activity['level']}** · XP **{activity['xp']}/{required_xp(activity['level'])}**",
        inline=False,
    )
    embed.add_field(
        name="⚔️ 사냥 성장(영구)",
        value=(
            f"사냥 Lv.**{hunt_user['level']}** · 직업 **{hunt_user.get('job') or '미선택'}**\n"
            f"장비: 🗡️ **{hunt_user['weapon']}** / 🛡️ **{hunt_user['armor']}**"
        ),
        inline=False,
    )
    embed.add_field(
        name="🧭 개인 모험 성장(영구)",
        value=(
            f"모험 Lv.**{adventure['level']}** · 최고 지형 깊이 **{adventure.get('best_terrain_rank', 0)}**\n"
            f"장비: 🗡️ **{adventure['weapon']}** / 🛡️ **{adventure['armor']}**\n"
            f"장착 유물: **{len(equipped_relics)}/{RELIC_MAX_EQUIPPED}개**"
        ),
        inline=False,
    )
    embed.add_field(
        name="🏕️ 파티 원정 기록(판 내부 성장은 초기화)",
        value=(
            f"{PARTY_TOKEN_NAME} **{expedition['tokens']}개** · 완주 **{expedition['clears']}회**\n"
            f"누적 보스 **{expedition['boss_kills']}마리** · 최고 깊이 **{expedition['best_depth']}**"
        ),
        inline=False,
    )
    embed.add_field(
        name="🌠 캐릭터 수집",
        value=f"보유 캐릭터 **{len(user_chars)}명** · 원석 **{get_primogems(uid):,}개** · 모라 **{get_poker_money(uid):,}**",
        inline=False,
    )
    embed.set_footer(text="서버 활동 / 사냥 / 개인 모험 / 파티 원정은 서로 다른 성장축이야.")
    await interaction.response.send_message(embed=embed)


@bot.event
async def on_ready():
    migrate_party_battle_balance()
    restore_party_persistent_views()

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
