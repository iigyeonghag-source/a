import json
import os
import random
from datetime import datetime, timezone, timedelta
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
from discord import app_commands


load_dotenv()

GUILD_ID = 1510681614919794868
GUILD = discord.Object(id=GUILD_ID)

TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    raise RuntimeError("TOKEN이 없음. Railway Variables에 TOKEN 넣어야 함.")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

favor = {}
user_memory = {}
last_response_key = {}
last_topic = {}


MONEY_FILE = "poker_money.json"

DATA_DIR = "/data"
DATA_FILE = "/data/data.json"

data = {
    "poker_money": {},
    "poker_last_claim": {},
    "favor": {},
    "memory": {},
    "characters": {}
}

characters = {}

def load_data():
    global data, poker_money, poker_last_claim, favor, user_memory, characters


    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        data["poker_money"] = loaded.get("poker_money", {})
        data["poker_last_claim"] = loaded.get("poker_last_claim", {})
        data["favor"] = loaded.get("favor", {})
        data["memory"] = loaded.get("memory", {})
        data["characters"] = loaded.get("characters", {})

    poker_money = data["poker_money"]
    favor = data["favor"]
    user_memory = data["memory"]
    characters = data["characters"]

    poker_last_claim = {}
    for uid, value in data["poker_last_claim"].items():
        poker_last_claim[uid] = datetime.fromisoformat(value)

def save_data():
    os.makedirs(DATA_DIR, exist_ok=True)

    data["poker_money"] = poker_money
    data["favor"] = favor
    data["memory"] = user_memory
    data["characters"] = characters
    data["poker_last_claim"] = {
        uid: value.isoformat()
        for uid, value in poker_last_claim.items()
    }

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

load_data()

poker_rooms = {}
poker_money = {}
poker_last_claim = {}
user_memory = {}

load_data()

KST = timezone(timedelta(hours=9))

def get_favor(user_id):
    return favor.get(str(user_id), 0)

def add_favor(user_id, amount):
    uid = str(user_id)
    favor[uid] = favor.get(uid, 0) + amount
    favor[uid] = max(-100, min(100, favor[uid]))
    
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
    stage = get_favor_stage(user_id)

    if stage and random.random() < 0.3:
        return random.choice(FAVOR_STAGE_RESPONSES[stage]) + "\n" + response

    return response

def remember_user_value(user_id, key, value):
    uid = str(user_id)
    user_memory.setdefault(uid, {})
    user_memory[uid][key] = value
    save_data()

def get_user_memory(user_id, key, default=None):
    return user_memory.get(str(user_id), {}).get(key, default)

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
    "뷰지", "가슴", "쥬지"
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
    "다": [
        "그래 푸리나야! 갑자기 날 왜 불렀을까?",
        "안녕!"
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
    "다": ["다", "드 폰타인", "야"],
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
        
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if not message.content.startswith("푸리나"):
        await bot.process_commands(message)
        return

    if "생일" in message.content:
        await message.channel.send(get_furina_birthday_response())
        return

    text = message.content.replace("푸리나", "", 1).strip()
    lower = text.lower()
    uid = str(message.author.id)

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
            bonus = random.choice([10, 20, 30])
            add_poker_money(uid, bonus)
            response += f"\n\n후후, 오늘은 기분이 좋으니까 **{bonus}모라** 줄게! 현재 돈: **{get_poker_money(uid)}모라**"

        if selected_key in FOLLOW_UP_QUESTIONS and random.random() < 0.45:
            response += "\n" + random.choice(FOLLOW_UP_QUESTIONS[selected_key])

        await message.reply(response)
        return

    await message.reply(random.choice(DEFAULT_RESPONSES))

GENSHIN_CHARACTERS = {
    "푸리나": {
        "rarity": 5,
        "dialogue": "후후, 드디어 날 제대로 알아보는구나? 이 푸리나님과 함께라면 지루할 틈은 없을 거야!"
    },
    "느비예트": {
        "rarity": 5,
        "dialogue": "질서는 물처럼 흘러야 한다. 그러나 때로는 그 흐름을 바로잡아야 하지."
    },
    "아를레키노": {
        "rarity": 5,
        "dialogue": "흥미롭군. 네 선택이 어디까지 이어질지 지켜보겠다."
    },
    "라이덴 쇼군": {
        "rarity": 5,
        "dialogue": "영원은 쉽게 흔들리지 않는다."
    },
    "나히다": {
        "rarity": 5,
        "dialogue": "작은 씨앗도 언젠가 커다란 나무가 될 수 있어."
    },
    "종려": {
        "rarity": 5,
        "dialogue": "계약은 맺어진 순간부터 의미를 가진다."
    },
    "벤티": {
        "rarity": 5,
        "dialogue": "바람이 부는 곳이라면 어디든 노래가 있지!"
    },
    "클로린드": {
        "rarity": 5,
        "dialogue": "결투라면 피하지 않겠다."
    },
    "리니": {
        "rarity": 5,
        "dialogue": "자, 눈 깜빡하지 마. 진짜 마술은 지금부터니까!"
    },
    "리넷": {
        "rarity": 4,
        "dialogue": "명령 확인. 수행할게."
    },
    "향릉": {
        "rarity": 4,
        "dialogue": "새로운 식재료 발견! 이건 꼭 요리해봐야 해!"
    },
    "베넷": {
        "rarity": 4,
        "dialogue": "불운해도 괜찮아! 모험은 계속되는 거니까!"
    },
    "피슬": {
        "rarity": 4,
        "dialogue": "단죄의 황녀가 그대의 부름에 응답하였노라!"
    },
    "행추": {
        "rarity": 4,
        "dialogue": "책 속의 지혜와 검술은 의외로 닮은 점이 많지."
    },
    "노엘": {
        "rarity": 4,
        "dialogue": "무엇이든 맡겨주세요. 제가 도와드릴게요!"
    }
}

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

def draw_character():
    five_stars = [name for name, info in GENSHIN_CHARACTERS.items() if info["rarity"] == 5]
    four_stars = [name for name, info in GENSHIN_CHARACTERS.items() if info["rarity"] == 4]

    if random.random() < 0.08:
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
    
from itertools import combinations

SMALL_BLIND = 2
BIG_BLIND = 5
FURINA_ID = "FURINA_BOT"

def get_poker_money(user_id):
    return poker_money.get(str(user_id), 100)

def add_poker_money(user_id, amount):
    uid = str(user_id)
    poker_money[uid] = get_poker_money(uid) + amount
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

FURINA_POKER_BANKROLL = 300
FURINA_MAX_RAISE = 80

def furina_say(kind, **kwargs):
    text = random.choice(POKER_REACTION[kind])
    return text.format(**kwargs)

def preflop_strength(cards):
    """공개 카드가 없을 때 푸리나가 자기 패를 대충 평가하는 값. 0.0~1.0"""
    ranks = [r for r, s in cards]
    suits = [s for r, s in cards]
    values = sorted([RANK_VALUE[r] for r in ranks], reverse=True)

    high, low = values[0], values[1]
    strength = (high + low) / 28

    if ranks[0] == ranks[1]:
        strength += 0.32 + (high / 100)
    if suits[0] == suits[1]:
        strength += 0.08
    if abs(high - low) == 1:
        strength += 0.07
    elif abs(high - low) == 2:
        strength += 0.04
    if high >= 13:
        strength += 0.08
    if low <= 5 and high < 11:
        strength -= 0.12

    return max(0.0, min(1.0, strength))

def made_hand_strength(cards):
    """공개 카드가 있을 때 현재 족보 기반으로 0.0~1.0 평가."""
    score = best_score(cards)
    rank_type = score[0]
    high = max(score[1]) if score[1] else 2

    base = {
        0: 0.18,
        1: 0.34,
        2: 0.52,
        3: 0.66,
        4: 0.74,
        5: 0.78,
        6: 0.86,
        7: 0.94,
        8: 1.0,
    }.get(rank_type, 0.2)

    return max(0.0, min(1.0, base + (high - 2) / 100))

def furina_hand_strength(room):
    cards = room["hands"].get(FURINA_ID, [])
    community = room.get("community", [])

    if len(community) < 3:
        return preflop_strength(cards)

    return made_hand_strength(cards + community)

def choose_furina_raise_amount(room, strength, all_in=False):
    current = room["current_bet"]

    if all_in:
        return max(current + 1, FURINA_POKER_BANKROLL)

    if strength >= 0.86:
        bump = random.choice([30, 40, 50, 70])
    elif strength >= 0.66:
        bump = random.choice([15, 20, 25, 30])
    else:
        bump = random.choice([8, 10, 15, 20])

    amount = max(current + 5, current + bump)
    return min(amount, FURINA_MAX_RAISE)

def is_big_pressure(room, need):
    if need >= 50:
        return True
    if room["pot"] > 0 and need >= room["pot"] * 0.7:
        return True
    return False


def furina_decide_vs_bet(strength, pressure, need):
    """상대 레이즈/올인에 대한 푸리나의 선택. fold/call/allin 중 하나."""
    if strength < 0.28:
        return "fold" if random.random() < (0.82 if pressure else 0.55) else "call"
    if strength < 0.45:
        return "fold" if random.random() < (0.45 if pressure else 0.20) else "call"
    if strength < 0.62:
        return "fold" if random.random() < (0.18 if pressure else 0.06) else "call"
    if strength >= 0.84 and pressure and random.random() < 0.65:
        return "allin"
    if strength >= 0.92 and random.random() < 0.35:
        return "allin"
    return "call"

def furina_decide_no_bet(strength):
    """상대 베팅이 없을 때 푸리나의 선공 행동. check/raise/allin 중 하나."""
    if strength >= 0.93 and random.random() < 0.45:
        return "allin"
    if strength >= 0.68 and random.random() < 0.65:
        return "raise"
    if strength >= 0.52 and random.random() < 0.35:
        return "raise"
    if strength < 0.34 and random.random() < 0.13:
        return "bluff"
    return "check"

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

def stage_text(room):
    cards = card_text(room["community"]) if room["community"] else "아직 없음"
    return f"공개 카드: **{cards}**\n판돈: **{room['pot']}모라**"

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

async def furina_auto(ctx, room):
    while room["started"] and current_player(room) == FURINA_ID:
        if FURINA_ID in room["folded"] or FURINA_ID in room.get("all_in", set()):
            room["turn_index"] = next_index(room, room["turn_index"])
            continue

        need = room["current_bet"] - room["bets"].get(FURINA_ID, 0)
        strength = furina_hand_strength(room)
        pressure = is_big_pressure(room, need)

        if need > 0:
            decision = furina_decide_vs_bet(strength, pressure, need)

            if decision == "fold":
                room["folded"].add(FURINA_ID)
                room["acted"].add(FURINA_ID)
                await ctx.send(furina_say("furina_fold_weak"))
            elif decision == "allin":
                # 푸리나 전용 가상 자금 기준 올인. 현재 베팅보다 최소 1원은 높게 잡아 역압박 가능.
                amount = max(room["current_bet"] + 1, choose_furina_raise_amount(room, strength, all_in=True))
                pay = max(0, amount - room["bets"].get(FURINA_ID, 0))
                room["current_bet"] = amount
                room["bets"][FURINA_ID] = amount
                room["pot"] += pay
                room["acted"] = {FURINA_ID}
                room.setdefault("all_in", set()).add(FURINA_ID)
                await ctx.send(furina_say("furina_allin_call"))
            else:
                room["pot"] += need
                room["bets"][FURINA_ID] += need
                room["acted"].add(FURINA_ID)
                await ctx.send(furina_say("furina_call", need=need))
        else:
            decision = furina_decide_no_bet(strength)

            if decision == "allin":
                amount = choose_furina_raise_amount(room, strength, all_in=True)
                pay = max(0, amount - room["bets"].get(FURINA_ID, 0))
                room["current_bet"] = amount
                room["bets"][FURINA_ID] = amount
                room["pot"] += pay
                room["acted"] = {FURINA_ID}
                room.setdefault("all_in", set()).add(FURINA_ID)
                await ctx.send(furina_say("furina_allin_raise", amount=amount))
            elif decision in ("raise", "bluff"):
                amount = choose_furina_raise_amount(room, strength)
                pay = max(0, amount - room["bets"].get(FURINA_ID, 0))
                room["current_bet"] = amount
                room["bets"][FURINA_ID] = amount
                room["pot"] += pay
                room["acted"] = {FURINA_ID}
                await ctx.send(furina_say("furina_bluff" if decision == "bluff" else "furina_raise", amount=amount))
            else:
                room["acted"].add(FURINA_ID)
                await ctx.send(furina_say("furina_check"))

        if len(active_players(room)) == 1:
            await win_by_fold(ctx, room)
            return

        if all_called(room):
            await advance_stage(ctx, room)
            return

        room["turn_index"] = next_index(room, room["turn_index"])
        await ctx.send(f"현재 턴: **{poker_name(ctx, current_player(room))}**")
        return

async def win_by_fold(ctx, room):
    winner = active_players(room)[0]

    if winner != FURINA_ID:
        add_poker_money(winner, room["pot"])

    await ctx.send(
        f"모두 폴드!\n"
        f"승자: **{poker_name(ctx, winner)}**\n"
        f"획득: **{room['pot']}모라**"
    )

    room["dealer_index"] = (room["dealer_index"] + 1) % len(room["players"])
    room["started"] = False
    room["stage"] = "lobby"

async def after_action(ctx, room):
    if len(active_players(room)) == 1:
        await win_by_fold(ctx, room)
        return

    if all_called(room):
        await advance_stage(ctx, room)
        return

    room["turn_index"] = next_index(room, room["turn_index"])

    await ctx.send(f"현재 턴: **{poker_name(ctx, current_player(room))}**")
    await furina_auto(ctx, room)

@bot.command(name="돈")
async def poker_money_command(ctx):
    await ctx.reply(f"{ctx.author.mention}의 포커 돈: **{get_poker_money(ctx.author.id)}모라**")

@bot.command(name="돈받기")
async def poker_claim(ctx):
    uid = str(ctx.author.id)
    now = datetime.now(timezone.utc)

    last = poker_last_claim.get(uid)
    if last and now - last < timedelta(hours=24):
        left = timedelta(hours=24) - (now - last)
        hours = int(left.total_seconds() // 3600)
        minutes = int((left.total_seconds() % 3600) // 60)
        await ctx.reply(f"아직 못 받아! 남은 시간: **{hours}시간 {minutes}분**")
        return

    poker_last_claim[uid] = now
    save_data()
    money = add_poker_money(uid, 100)
    await ctx.reply(f"100모라 지급 완료! 현재 돈: **{money}모라**")

@bot.command(name="포커")
async def poker_lobby(ctx):
    room = get_room(ctx)

    if room and room["started"]:
        await ctx.reply("이미 이 채널에서 포커가 진행 중이야!")
        return

    room = new_poker_room(ctx)

    await ctx.reply(
        f"포커 방 생성!\n"
        f"참가자: **푸리나**, **{ctx.author.display_name}**\n\n"
        f"`!참가`로 참가 가능\n"
        f"`!시작`으로 시작"
    )

@bot.command(name="참가")
async def poker_join(ctx):
    room = get_room(ctx)

    if not room:
        await ctx.reply("포커 방이 없어! `!포커`로 먼저 만들어!")
        return

    if room["started"]:
        await ctx.reply("이미 게임 시작했어!")
        return

    uid = str(ctx.author.id)

    if uid in room["players"]:
        await ctx.reply("이미 참가했잖아!")
        return

    room["players"].append(uid)

    await ctx.reply(
        f"{ctx.author.display_name} 참가 완료!\n"
        f"현재 참가자: **{len(room['players'])}명**"
    )

@bot.command(name="시작")
async def poker_start(ctx):
    room = get_room(ctx)

    if not room:
        await ctx.reply("포커 방이 없어! `!포커`부터 해!")
        return

    if room["started"]:
        await ctx.reply("이미 시작했어!")
        return

    if str(ctx.author.id) != room["host"]:
        await ctx.reply("방장만 시작할 수 있어!")
        return

    if len(room["players"]) < 2:
        await ctx.reply("참가자가 부족해!")
        return

    deck = make_deck()
    room["deck"] = deck
    room["hands"] = {p: [deck.pop(), deck.pop()] for p in room["players"]}
    room["community"] = []
    room["pot"] = 0
    room["current_bet"] = BIG_BLIND
    room["bets"] = {p: 0 for p in room["players"]}
    room["folded"] = set()
    room["acted"] = set()
    room["all_in"] = set()
    room["stage"] = "preflop"
    room["started"] = True

    players = room["players"]
    dealer = room["dealer_index"]

    small_idx = (dealer + 1) % len(players)
    big_idx = (dealer + 2) % len(players)

    if len(players) == 2:
        small_idx = dealer
        big_idx = (dealer + 1) % len(players)

    small = players[small_idx]
    big = players[big_idx]

    for p, blind in [(small, SMALL_BLIND), (big, BIG_BLIND)]:
        room["bets"][p] += blind
        room["pot"] += blind
        if p != FURINA_ID:
            add_poker_money(p, -blind)

    room["turn_index"] = next_index(room, big_idx)

    msg = (
        f"포커 시작!\n"
        f"딜러: **{poker_name(ctx, players[dealer])}**\n"
        f"스몰 블라인드: **{poker_name(ctx, small)} {SMALL_BLIND}모라**\n"
        f"빅 블라인드: **{poker_name(ctx, big)} {BIG_BLIND}모라**\n\n"
        f"현재 판돈: **{room['pot']}모라**\n"
        f"현재 턴: **{poker_name(ctx, current_player(room))}**"
    )

    await ctx.send(msg)

    for p in players:
        if p != FURINA_ID:
            user = await bot.fetch_user(int(p))
            await user.send(f"네 포커 패: **{card_text(room['hands'][p])}**")

    await furina_auto(ctx, room)

@bot.command(name="체크")
async def poker_check(ctx):
    room = get_room(ctx)
    uid = str(ctx.author.id)

    if not room or not room["started"]:
        await ctx.reply("진행 중인 포커가 없어!")
        return

    if current_player(room) != uid:
        await ctx.reply("지금 네 턴이 아니야!")
        return

    if room["current_bet"] > room["bets"].get(uid, 0):
        await ctx.reply("상대 베팅이 있어서 체크 못 해! `!콜` 또는 `!폴드` 해야 해.")
        return

    room["acted"].add(uid)
    await ctx.reply("체크!\n" + random.choice(POKER_REACTION["check"]))

    await after_action(ctx, room)

@bot.command(name="콜")
async def poker_call(ctx):
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

@bot.command(name="레이즈")
async def poker_raise(ctx, amount: int = 10):
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

@bot.command(name="폴드")
async def poker_fold(ctx):
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


@bot.command(name="패")
async def poker_my_hand(ctx):
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


@bot.command(name="포커랭킹")
async def poker_ranking(ctx):
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

    await ctx.reply("포커 랭킹!\n" + "\n".join(lines))

@bot.command(name="올인")
async def poker_all_in(ctx):
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

async def send_role_message(member, role_name, channel):
    role = discord.utils.get(member.guild.roles, name=role_name)
    if role is None:
        return

    msg = ROLE_MESSAGES[role_name].format(
        user=member.mention,
        role=role.mention
    )

    await channel.send(msg)

SERVER_ID = 1510681614919794868
CHANNEL_ID = 1512642190302777415

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

@bot.event
async def on_member_update(before, after):
    print("업데이트 감지")
    print("서버 ID:", after.guild.id)
    print("설정 SERVER_ID:", SERVER_ID)

    if after.guild.id != SERVER_ID:
        return

    before_roles = {role.id for role in before.roles}

    for role in after.roles:
        if role.id not in before_roles:
            print("새 역할:", repr(role.name))

            if role.name in ROLE_MESSAGES:
                channel = after.guild.get_channel(CHANNEL_ID)

                if channel is None:
                    print("채널 못 찾음")
                    return

                msg = ROLE_MESSAGES[role.name].format(
                    user=after.mention,
                    role=role.mention
                )
                await channel.send(msg)
print(get_time_key())
print(datetime.now())

CHARACTER_GACHA_COST = 160
CHARACTER_TEN_GACHA_COST = CHARACTER_GACHA_COST * 10

@bot.tree.command(name="캐릭터뽑기", description="원신 캐릭터를 뽑는다")
@app_commands.describe(횟수="1 또는 10")
async def character_gacha(interaction: discord.Interaction, 횟수: int = 1):
    uid = str(interaction.user.id)    
    current_money = get_poker_money(uid)
    
    if 횟수 not in [1, 10]:
        await interaction.response.send_message(
            "❌ 1회 또는 10회만 가능해.",
            ephemeral=True
        )
        return

    cost = CHARACTER_GACHA_COST * 횟수

    if get_poker_money(uid) < cost:
        await interaction.response.send_message(
            f"❌ 모라가 부족해!\n필요 모라: **{cost}**\n보유 모라: **{get_poker_money(uid)}**",
            ephemeral=True
        )
        return

    add_poker_money(uid, -cost)
    user_chars = get_user_characters(uid)

    await interaction.response.send_message(
        "✨ 하늘에 별빛이 모이기 시작한다..."
    )

    msg = await interaction.original_response()

    await asyncio.sleep(1)
    await msg.edit(content="🌌 운명의 문이 열리는 중...")
    await asyncio.sleep(1)
    await msg.edit(content="💫 빛이 강하게 폭발한다!")
    await asyncio.sleep(1)

    results = []
    reward_lines = []

    for i in range(횟수):
        name = draw_character()
        info = GENSHIN_CHARACTERS[name]
        is_new = name not in user_chars

        if is_new:
            user_chars[name] = {"favor_exp": 0}
            results.append(f"{i+1}. 🎉 신규 {'⭐' * info['rarity']} **{name}**")
        else:
            old_level = get_character_level(user_chars[name]["favor_exp"])

            if old_level < 3:
                user_chars[name]["favor_exp"] += 1

            new_level = get_character_level(user_chars[name]["favor_exp"])

            results.append(f"{i+1}. ✨ 중복 {'⭐' * info['rarity']} **{name}** | 호감도 Lv.{new_level}/3")

            if old_level != new_level:
                reward = 300 if new_level == 2 else 700
                add_poker_money(uid, reward)

                reward_lines.append(
                    f"💖 **{name}** 호감도 Lv.{old_level} → Lv.{new_level} / 보상 **{reward}모라**"
                )

                if new_level >= 2:
                    reward_lines.append(f"💬 **{name}의 대사**: {info['dialogue']}")

    save_data()

    result_text = "\n".join(results)
    reward_text = "\n".join(reward_lines) if reward_lines else "없음"

    current_money = get_poker_money(uid)

    await msg.edit(
        content=(
            f"🎊 **캐릭터 뽑기 결과!**\n"
            f"소모 모라: **{cost}**\n\n"
            f"{result_text}\n\n"
            f"🎁 **호감도 보상**\n"
            f"{reward_text}\n\n"
            f"💰 현재 모라: **{current_money}**"
        )
    )

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

        if level >= 2:
            text += f"\n\n💬 **해금 대사**\n> {info['dialogue']}"
        else:
            text += "\n\n🔒 호감도 Lv.2부터 대사가 해금돼."

        await interaction.response.send_message(
            text,
            ephemeral=True
        )


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
            content=self.dex_view.render(),
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
            content=self.dex_view.render(),
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


@bot.tree.command(name="캐릭터도감", description="내가 뽑은 원신 캐릭터 도감을 본다", guild=GUILD)
async def character_dex(interaction: discord.Interaction):
    view = CharacterDexView(interaction.user.id)

    await interaction.response.send_message(
        content=view.render(),
        view=view
    )
    
@bot.event
async def on_ready():
    if not birthday_check.is_running():
        birthday_check.start()
        
    synced = await bot.tree.sync(guild=GUILD)
    print(f"로그인됨: {bot.user}")
    print(f"길드 명령어 {len(synced)}개 동기화")
    
bot.run(TOKEN)
