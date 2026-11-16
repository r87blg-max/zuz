"""
╔══════════════════════════════════════════════════════════╗
║       بوت شراء الأرقام — النسخة الاحترافية v3.0         ║
║   ✦ نظام صلاحيات الأدمن  ✦ تفعيل تلقائي Telethon       ║
║   ✦ شحن آسياسيل تلقائي ODP ✦ لوحة تحكم متكاملة           ║
╚══════════════════════════════════════════════════════════╝
"""

import asyncio
import os
import requests, sqlite3, time, json, random, io, math, hashlib, string, hmac, threading, re
from datetime import datetime, timedelta
from collections import defaultdict
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_OK = True
except ImportError:
    PLAYWRIGHT_OK = False

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    PILLOW = True
except ImportError:
    PILLOW = False

try:
    from telethon import TelegramClient
    from telethon.sessions import StringSession
    from telethon import functions, errors as tel_errors
    TELETHON = True
except ImportError:
    TELETHON = False

# ╔══════════════════════════════════════════════════════════╗
# ║            ◄◄ إعدادات البوت — عدّل هنا فقط ►►          ║
# ╚══════════════════════════════════════════════════════════╝
TOKEN              = os.environ.get("BOT_TOKEN",              "8779869096:AAEJqEGT-mSJ3-dBj1iCUFolrIjtn6cssYI")
OWNER_ID           = int(os.environ.get("OWNER_ID",           "5264176309"))
BOT_USERNAME       = os.environ.get("BOT_USERNAME",           "FAKEROZBOT")
ACTIVATION_CHANNEL = os.environ.get("ACTIVATION_CHANNEL",    "D_WWORK")
PROOF_CHANNEL      = os.environ.get("PROOF_CHANNEL",         "Q_O_Q_N")
SUPPORT            = os.environ.get("SUPPORT",                "https://t.me/ROZMOC")

TELEGRAM_API_ID    = int(os.environ.get("TELEGRAM_API_ID",   "30918784"))
TELEGRAM_API_HASH  = os.environ.get("TELEGRAM_API_HASH",     "674cc8f64d5eefe01c80f9e2caefae3c")

# رقم هاتف المطور الذي سيُحوّل إليه الرصيد (عدّله هنا)
RECEIVER_ASIACELL_PHONE = os.environ.get("RECEIVER_ASIACELL_PHONE", "07737169799")

REFERRAL_REWARD_CENTS = 1       # $0.01 لكل إحالة
# ╚══════════════════════════════════════════════════════════╝

_BALANCE_SECRET = hashlib.sha256(f"{TOKEN}_BAL_SECURE_v3".encode()).hexdigest()
URL    = f"https://api.telegram.org/bot{TOKEN}"
offset = None
_rate_limits = defaultdict(list)
_rate_lock   = threading.Lock()
browser_sessions = {}
_browser_lock = threading.Lock()

# ═══ صلاحيات الأدمن الافتراضية ═══
DEFAULT_ADMIN_PERMS = {
    "add_numbers":    1,
    "delete_numbers": 1,
    "edit_prices":    1,
    "view_stats":     1,
    "broadcast":      0,
    "grant_balance":  0,
    "manage_users":   1,
    "manage_subs":    1,
    "clean_data":     0,
    "sales_log":      1,
    "manage_prices":  1,
    "manage_recharge":1,
}

PERM_LABELS = {
    "add_numbers":    "➕ إضافة أرقام",
    "delete_numbers": "🗑 حذف أرقام",
    "edit_prices":    "💲 تعديل الأسعار",
    "view_stats":     "📊 إحصائيات",
    "broadcast":      "📣 البث للمستخدمين",
    "grant_balance":  "💰 منح/خصم رصيد",
    "manage_users":   "👥 إدارة المستخدمين",
    "manage_subs":    "🔔 الاشتراكات الإجبارية",
    "clean_data":     "🧹 تنظيف البيانات",
    "sales_log":      "📜 سجل المبيعات",
    "manage_prices":  "💲 أسعار الدول",
    "manage_recharge":"🔄 طلبات الشحن",
}

# ═══ إيموجي سريعة للأزرار ═══
QUICK_EMOJI = [
    "🎯","⭐","🔥","💎","👑","🚀","🌟","✨",
    "💰","💵","📊","🛒","💳","🎁","🔔","💬",
    "🤖","⚙️","🔐","🔑","✅","📱","🌍","🔗",
    "📣","👤","👥","💼","🏆","🎉","🛡","⚡",
    "🎨","📌","🌈","🦋","🎪","🔮","💫","🌙",
    "❤️","🧡","💛","💚","💙","💜","🖤","🤍",
]

EMOJI_CATS = {
    "💼 أعمال":  ["💼","📊","💹","🏦","💰","💵","📈","💎","🏧","💳"],
    "⭐ نجوم":   ["⭐","🌟","✨","🔥","💫","🎯","🚀","🌙","☀️","🌠"],
    "🔧 تقنية":  ["🤖","⚙️","🔧","📱","💻","🌐","🔌","📡","🛰","🔬"],
    "🎁 هدايا":  ["🎁","🎊","🎉","🎈","🎀","🏆","🥇","👑","🎖","🎗"],
    "💬 تواصل":  ["📣","📢","💬","📩","📨","🔔","💡","📌","🗣","📞"],
    "🔐 أمان":   ["🔐","🔒","🛡","🔑","🗝","⚠️","🚨","✅","🔓","🛑"],
    "👥 أشخاص":  ["👤","👥","🙋","👔","🤝","💪","🫡","🧑","👨‍💼","🤴"],
    "🌍 متنوع":  ["🌍","🌏","🌎","🗺","📍","🏴","🚩","🌐","🏠","🏪"],
}

# ═══ الدول ═══
COUNTRIES = {
    "العراق":("🇮🇶","+964"),"السعودية":("🇸🇦","+966"),"الإمارات":("🇦🇪","+971"),
    "مصر":("🇪🇬","+20"),"الكويت":("🇰🇼","+965"),"قطر":("🇶🇦","+974"),
    "البحرين":("🇧🇭","+973"),"عُمان":("🇴🇲","+968"),"اليمن":("🇾🇪","+967"),
    "الأردن":("🇯🇴","+962"),"لبنان":("🇱🇧","+961"),"سوريا":("🇸🇾","+963"),
    "فلسطين":("🇵🇸","+970"),"المغرب":("🇲🇦","+212"),"الجزائر":("🇩🇿","+213"),
    "تونس":("🇹🇳","+216"),"ليبيا":("🇱🇾","+218"),"السودان":("🇸🇩","+249"),
    "موريتانيا":("🇲🇷","+222"),"الصومال":("🇸🇴","+252"),"تركيا":("🇹🇷","+90"),
    "إيران":("🇮🇷","+98"),"باكستان":("🇵🇰","+92"),"الهند":("🇮🇳","+91"),
    "بنغلاديش":("🇧🇩","+880"),"نيبال":("🇳🇵","+977"),"أفغانستان":("🇦🇫","+93"),
    "روسيا":("🇷🇺","+7"),"أوكرانيا":("🇺🇦","+380"),"كازاخستان":("🇰🇿","+7"),
    "أوزبكستان":("🇺🇿","+998"),"أذربيجان":("🇦🇿","+994"),"جورجيا":("🇬🇪","+995"),
    "أرمينيا":("🇦🇲","+374"),"إندونيسيا":("🇮🇩","+62"),"ماليزيا":("🇲🇾","+60"),
    "الفلبين":("🇵🇭","+63"),"فيتنام":("🇻🇳","+84"),"تايلاند":("🇹🇭","+66"),
    "الصين":("🇨🇳","+86"),"اليابان":("🇯🇵","+81"),"كوريا الجنوبية":("🇰🇷","+82"),
    "الولايات المتحدة":("🇺🇸","+1"),"كندا":("🇨🇦","+1"),"المملكة المتحدة":("🇬🇧","+44"),
    "ألمانيا":("🇩🇪","+49"),"فرنسا":("🇫🇷","+33"),"إسبانيا":("🇪🇸","+34"),
    "إيطاليا":("🇮🇹","+39"),"هولندا":("🇳🇱","+31"),"بلجيكا":("🇧🇪","+32"),
    "السويد":("🇸🇪","+46"),"النرويج":("🇳🇴","+47"),"الدنمارك":("🇩🇰","+45"),
    "فنلندا":("🇫🇮","+358"),"بولندا":("🇵🇱","+48"),"رومانيا":("🇷🇴","+40"),
    "أستراليا":("🇦🇺","+61"),"نيوزيلندا":("🇳🇿","+64"),
    "البرازيل":("🇧🇷","+55"),"الأرجنتين":("🇦🇷","+54"),"المكسيك":("🇲🇽","+52"),
    "نيجيريا":("🇳🇬","+234"),"إثيوبيا":("🇪🇹","+251"),"كينيا":("🇰🇪","+254"),
    "غانا":("🇬🇭","+233"),"جنوب أفريقيا":("🇿🇦","+27"),
}

LANGUAGES = [
    ("ar", "🌐", "العربية"),
    ("en", "🇬🇧", "English"),
]

LANG_WELCOME = {
    "ar": """👋 أهلاً بك <b>{name}</b>!

🆔 معرّفك: <code>{uid}</code>
💰 رصيدك: <b>{balance}</b>""",
    "en": """👋 Welcome <b>{name}</b>!

🆔 Your ID: <code>{uid}</code>
💰 Balance: <b>{balance}</b>""",
}

ENGLISH_BTNS = {
    "btn_buy":        "🛒 Buy Phone Number",
    "btn_cat_fraud":  "📵 Fraud Numbers",
    "btn_cat_fake":   "🎭 Fake Numbers",
    "btn_whatsapp":   "💬 SMS WhatsApp",
    "btn_transfer":   "💸 Transfer Balance",
    "btn_balance":    "💵 My Balance",
    "btn_recharge":   "💳 Recharge",
    "btn_mystats":    "📊 My Stats",
    "btn_daily":      "🎁 Daily Bonus",
    "btn_invite":     "🔗 Invite Link",
    "btn_support":    "🆘 Support",
    "btn_activation": "📢 Activation Channel",
    "btn_proof":      "🔐 Proof Channel",
    "btn_language":   "🌐 Change Language",
    "btn_agent":      "👔 Agent Panel",
    "btn_admin":      "⚙️ Admin Panel",
    "btn_owner":      "👑 Owner Panel",
    "btn_back":       "◀️ Back",
    "btn_cancel":     "❌ Cancel",
}

TRANSFER_MIN_CENTS  = 10   # $0.10 الحد الأدنى للمبلغ المُحوَّل
TRANSFER_FEE_CENTS  = 3    # $0.03 عمولة البوت

_build_lang = "ar"

STYLES = ["primary","success","danger"]
def rnd(): return random.choice(STYLES)

# ═══════════════ DB ═══════════════
_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_pro.db")
conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA foreign_keys=ON")

_db_lock = threading.Lock()

class _SafeCursor:
    def __init__(self): self._local = threading.local()
    def _last(self): return getattr(self._local, 'c', None)
    def execute(self, sql, params=()):
        with _db_lock:
            c = conn.cursor(); c.execute(sql, params); self._local.c = c
        return self
    def executescript(self, sql):
        with _db_lock:
            c = conn.cursor(); c.executescript(sql); self._local.c = c
        return self
    def fetchone(self):
        c = self._last(); return c.fetchone() if c else None
    def fetchall(self):
        c = self._last(); return c.fetchall() if c else []
    @property
    def rowcount(self):
        c = self._last(); return c.rowcount if c else 0

cur = _SafeCursor()

def setup_db():
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0,
        phone TEXT DEFAULT '', join_date TEXT, last_active TEXT,
        last_daily TEXT, referrer_id INTEGER DEFAULT 0,
        verified INTEGER DEFAULT 0, phone_ok INTEGER DEFAULT 0,
        user_lang TEXT DEFAULT 'ar'
    );
    CREATE TABLE IF NOT EXISTS admins(
        user_id INTEGER PRIMARY KEY, added_by INTEGER, added_date TEXT,
        permissions TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS agents(
        user_id INTEGER PRIMARY KEY, added_by INTEGER, added_date TEXT,
        commission_rate INTEGER DEFAULT 5, level TEXT DEFAULT 'regular',
        total_earned INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS numbers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT UNIQUE, code TEXT DEFAULT '', verify_code TEXT DEFAULT '',
        price INTEGER DEFAULT 100, country TEXT DEFAULT 'غير محدد',
        added_by INTEGER, added_date TEXT, status TEXT DEFAULT 'متاح',
        session_str TEXT DEFAULT '', auto_mode INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, number TEXT, code TEXT, verify_code TEXT,
        price INTEGER, country TEXT, purchase_date TEXT, txn_id TEXT,
        auto_sent INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS purchase_sessions(
        txn TEXT PRIMARY KEY, user_id INTEGER, number TEXT,
        session_str TEXT, two_fa TEXT
    );
    CREATE TABLE IF NOT EXISTS recharge_requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, amount INTEGER, method TEXT DEFAULT 'يدوي',
        proof TEXT, status TEXT DEFAULT 'معلق', request_date TEXT
    );
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
    CREATE TABLE IF NOT EXISTS referrals(
        user_id INTEGER, referred_id INTEGER, date TEXT,
        PRIMARY KEY(user_id, referred_id)
    );
    CREATE TABLE IF NOT EXISTS sub_channels(
        id INTEGER PRIMARY KEY AUTOINCREMENT, channel TEXT UNIQUE, title TEXT
    );
    CREATE TABLE IF NOT EXISTS btn_labels(
        key TEXT PRIMARY KEY, label TEXT, emoji TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS country_prices(
        country TEXT PRIMARY KEY, price_cents INTEGER DEFAULT 100
    );
    CREATE TABLE IF NOT EXISTS custom_countries(
        name TEXT PRIMARY KEY, flag TEXT DEFAULT '🏳️', prefix TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS hidden_countries(
        country TEXT PRIMARY KEY
    );
    CREATE TABLE IF NOT EXISTS wa_numbers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT UNIQUE,
        status TEXT DEFAULT 'متاح',
        claimed_by INTEGER DEFAULT 0,
        claimed_date TEXT DEFAULT '',
        added_by INTEGER,
        added_date TEXT
    );
    CREATE TABLE IF NOT EXISTS balance_audit(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, op TEXT, amount INTEGER,
        balance_before INTEGER, balance_after INTEGER,
        ref_txn TEXT, sig TEXT, ts TEXT
    );
    CREATE TABLE IF NOT EXISTS accounts(
        id INTEGER PRIMARY KEY AUTOINCREMENT, number TEXT UNIQUE,
        session_str TEXT DEFAULT '', status TEXT DEFAULT 'نشط',
        added_by INTEGER, added_date TEXT, note TEXT DEFAULT ''
    );
    """)
    conn.commit()

setup_db()

def migrate():
    for sql in [
        "ALTER TABLE users ADD COLUMN phone TEXT DEFAULT ''",
        "ALTER TABLE users ADD COLUMN phone_ok INTEGER DEFAULT 0",
        "ALTER TABLE numbers ADD COLUMN verify_code TEXT DEFAULT ''",
        "ALTER TABLE numbers ADD COLUMN session_str TEXT DEFAULT ''",
        "ALTER TABLE numbers ADD COLUMN auto_mode INTEGER DEFAULT 0",
        "ALTER TABLE numbers ADD COLUMN two_fa TEXT DEFAULT ''",
        "ALTER TABLE history ADD COLUMN auto_sent INTEGER DEFAULT 0",
        "ALTER TABLE admins ADD COLUMN permissions TEXT DEFAULT ''",
        "ALTER TABLE users ADD COLUMN user_lang TEXT DEFAULT 'ar'",
        "ALTER TABLE numbers ADD COLUMN category TEXT DEFAULT ''",
        "CREATE TABLE IF NOT EXISTS btn_premium(key TEXT PRIMARY KEY, emoji_id TEXT)",
    ]:
        try: cur.execute(sql); conn.commit()
        except: pass

migrate()

DEFAULT_BTNS = {
    "btn_buy":        "🛒 شراء رقم هاتفي",
    "btn_cat_fraud":  "📵 أرقام احتيالية",
    "btn_cat_fake":   "🎭 أرقام مزيفة",
    "btn_whatsapp":   "💬 SMS WhatsApp",
    "btn_transfer":   "💸 تحويل الرصيد",
    "btn_balance":    "💵 رصيدي الحالي",
    "btn_recharge":   "💳 شحن الرصيد",
    "btn_recharge_stars": "⭐ شحن تلقائي بنجوم تيليجرام",
    "btn_recharge_dev":   "💎 شحن عبر المطور مباشرة",
    "btn_mystats":    "📊 إحصائياتي",
    "btn_daily":      "🎁 الهدية اليومية",
    "btn_invite":     "🔗 رابط الدعوة",
    "btn_support":    "🆘 الدعم الفني",
    "btn_activation": "📢 قناة التفعيلات",
    "btn_proof":      "🔐 قناة الاثباتات",
    "btn_language":   "🌐 تغيير اللغة",
    "btn_agent":      "👔 لوحة الوكيل",
    "btn_admin":      "⚙️ لوحة الإدارة",
    "btn_owner":      "👑 لوحة المطور",
    "btn_back":       "◀️ رجوع",
    "btn_cancel":     "❌ إلغاء الأمر",
}

def get_admin_perms(uid):
    if uid == OWNER_ID:
        return {k: 1 for k in DEFAULT_ADMIN_PERMS}
    cur.execute("SELECT permissions FROM admins WHERE user_id=?", (uid,))
    row = cur.fetchone()
    if not row or not row[0]:
        return dict(DEFAULT_ADMIN_PERMS)
    try:
        stored = json.loads(row[0])
        result = dict(DEFAULT_ADMIN_PERMS)
        result.update(stored)
        return result
    except:
        return dict(DEFAULT_ADMIN_PERMS)

def has_perm(uid, perm):
    if uid == OWNER_ID: return True
    if not is_admin(uid): return False
    return bool(get_admin_perms(uid).get(perm, DEFAULT_ADMIN_PERMS.get(perm, 0)))

def set_admin_perm(uid, perm, val):
    perms = get_admin_perms(uid)
    perms[perm] = int(val)
    cur.execute("UPDATE admins SET permissions=? WHERE user_id=?", (json.dumps(perms), uid))
    conn.commit()

def toggle_admin_perm(uid, perm):
    perms = get_admin_perms(uid)
    cur_val = perms.get(perm, DEFAULT_ADMIN_PERMS.get(perm, 0))
    set_admin_perm(uid, perm, 0 if cur_val else 1)

def gs(key, default=""):
    cur.execute("SELECT value FROM settings WHERE key=?", (key,))
    r = cur.fetchone()
    return r[0] if r else default

def ss(key, value):
    cur.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (key, value))
    conn.commit()

def get_label(key):
    if _build_lang == "en" and key in ENGLISH_BTNS:
        return ENGLISH_BTNS[key]
    cur.execute("SELECT label,emoji FROM btn_labels WHERE key=?", (key,))
    r = cur.fetchone()
    if r:
        lbl, em = r
        return f"{em} {lbl}".strip() if em else lbl
    return DEFAULT_BTNS.get(key, key)

def get_premium_id(key):
    try:
        r = cur.execute("SELECT emoji_id FROM btn_premium WHERE key=?", (key,)).fetchone()
        return r[0] if r and r[0] else ""
    except Exception: return ""

def set_premium_id(key, eid):
    if eid: cur.execute("INSERT OR REPLACE INTO btn_premium(key,emoji_id) VALUES(?,?)", (key, eid))
    else:   cur.execute("DELETE FROM btn_premium WHERE key=?", (key,))
    conn.commit()

def with_premium(btn, key):
    eid = get_premium_id(key)
    if eid: btn["icon_custom_emoji_id"] = eid
    return btn

def text_with_premium(text, entities):
    ents = [e for e in (entities or []) if e.get("type") == "custom_emoji" and e.get("custom_emoji_id")]
    if not ents: return text
    u = text.encode("utf-16-le")
    out = b""; pos = 0
    for e in sorted(ents, key=lambda x: x["offset"]):
        o = e["offset"]*2; l = e["length"]*2
        out += u[pos:o]
        fb = u[o:o+l].decode("utf-16-le")
        out += f'<tg-emoji emoji-id="{e["custom_emoji_id"]}">{fb}</tg-emoji>'.encode("utf-16-le")
        pos = o + l
    out += u[pos:]
    return out.decode("utf-16-le")

def set_ctx(uid):
    global _build_lang
    _build_lang = get_user_lang(uid)

def now():   return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def today(): return datetime.now().strftime("%Y-%m-%d")
def fmt(cents): return f"${cents/100:.2f}"

def mask(num):
    s = str(num)
    return (s[:4]+"****"+s[-3:]) if len(s)>6 else "****"

def mask_activation(num):
    s = str(num).strip().replace(" ","")
    digits = s.lstrip("+")
    try: codes = [str(v[1]).lstrip("+") for v in get_all_countries().values() if v and len(v)>1 and v[1]]
    except Exception: codes = []
    best = ""
    for c in codes:
        if digits.startswith(c) and len(c) > len(best): best = c
    if not best: best = digits[:3]
    return f"+{best} 🔒🔒🔒"

def gen_txn():
    return "TXN-"+"".join(random.choices(string.ascii_uppercase+string.digits, k=8))

def gen_hash(txn, uid, amt):
    return hashlib.sha256(f"{txn}|{uid}|{amt}|{TOKEN[:8]}".encode()).hexdigest()[:12].upper()

def _bal_sig(uid, op, amount, bb, ba, txn):
    msg = f"{uid}|{op}|{amount}|{bb}|{ba}|{txn}|{_BALANCE_SECRET}"
    return hmac.new(_BALANCE_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()[:16].upper()

def get_proof_channel():    return gs("proof_channel", PROOF_CHANNEL)
def get_activation_channel():return gs("activation_channel", ACTIVATION_CHANNEL)
def get_country_price(c):
    cur.execute("SELECT price_cents FROM country_prices WHERE country=?", (c,))
    r = cur.fetchone(); return r[0] if r else 100
def set_country_price(c, p):
    cur.execute("INSERT OR REPLACE INTO country_prices(country,price_cents) VALUES(?,?)", (c, p))
    conn.commit()
def is_maintenance(): return gs("maintenance_mode","0")=="1"
def get_stars_per_dollar(): return int(gs("stars_per_dollar","100"))
def get_daily_bonus_max():  return int(gs("daily_bonus_max","1"))

def get_all_countries():
    result = dict(COUNTRIES)
    cur.execute("SELECT name,flag,prefix FROM custom_countries")
    for row in cur.fetchall():
        result[row[0]] = (row[1], row[2])
    return result

def is_country_hidden(name):
    cur.execute("SELECT 1 FROM hidden_countries WHERE country=?", (name,))
    return cur.fetchone() is not None

def add_custom_country(name, flag, prefix):
    cur.execute("INSERT OR REPLACE INTO custom_countries(name,flag,prefix) VALUES(?,?,?)", (name,flag,prefix))
    if not get_country_price(name):
        set_country_price(name, 100)
    conn.commit()

def del_hidden_country(name):
    cur.execute("DELETE FROM hidden_countries WHERE country=?", (name,))
    conn.commit()

def hide_country(name):
    cur.execute("INSERT OR IGNORE INTO hidden_countries(country) VALUES(?)", (name,))
    conn.commit()

def get_user_lang(uid):
    return "ar"

def set_user_lang(uid, lang):
    ensure(uid)
    cur.execute("UPDATE users SET user_lang=? WHERE user_id=?", (lang, uid))
    conn.commit()

def get_welcome_text(uid, uname, bal):
    lang = get_user_lang(uid)
    tmpl = gs("welcome_text", "")
    if tmpl:
        return tmpl.replace("{name}", uname).replace("{uid}", str(uid)).replace("{balance}", fmt(bal))
    tmpl = LANG_WELCOME.get(lang, LANG_WELCOME["ar"])
    return tmpl.replace("{name}", uname).replace("{uid}", str(uid)).replace("{balance}", fmt(bal))

def show_language_menu(chat_id, mid):
    kb = {"inline_keyboard": [
        [
            {"text": "العربية", "callback_data": "setlang_ar", "style": "primary"},
            {"text": "🇬🇧 English", "callback_data": "setlang_en", "style": "success"},
        ],
        [_b("btn_back", "main_menu", "danger")],
    ]}
    edit(chat_id, mid, "🌐 <b>اختر لغتك | Choose your language</b>", kb)

def check_rate_limit(uid, action="buy", max_per_hour=10):
    key = f"{uid}:{action}"
    now_ts = time.time()
    with _rate_lock:
        times = [t for t in _rate_limits[key] if now_ts-t < 3600]
        _rate_limits[key] = times
        if len(times) >= max_per_hour: return False
        _rate_limits[key].append(now_ts)
        return True

_session = requests.Session()
_session.headers.update({"Connection": "keep-alive"})

def api(method, data=None, files=None):
    try:
        if files:
            r = _session.post(f"{URL}/{method}", data=data or {}, files=files, timeout=8)
        else:
            r = _session.post(f"{URL}/{method}", json=data or {}, timeout=8)
        return r.json()
    except Exception as e:
        print(f"[API:{method}] {e}"); return {}

def send(chat_id, text, kb=None, parse_mode="HTML"):
    d = {"chat_id":chat_id,"text":text,"parse_mode":parse_mode}
    if kb: d["reply_markup"] = json.dumps(kb)
    return api("sendMessage", d)

def send_photo(chat_id, photo_bytes, caption="", kb=None):
    d = {"chat_id":chat_id,"caption":caption,"parse_mode":"HTML"}
    if kb: d["reply_markup"] = json.dumps(kb)
    return api("sendPhoto", d, files={"photo":("c.png",photo_bytes,"image/png")})

def edit(chat_id, mid, text, kb=None, parse_mode="HTML"):
    d = {"chat_id":chat_id,"message_id":mid,"text":text,"parse_mode":parse_mode}
    if kb: d["reply_markup"] = json.dumps(kb)
    api("editMessageText", d)

def answer(cb_id, text="", alert=False):
    api("answerCallbackQuery",{"callback_query_id":cb_id,"text":text,"show_alert":alert})

def delete_msg(chat_id, mid):
    api("deleteMessage",{"chat_id":chat_id,"message_id":mid})

def send_invoice(chat_id, title, desc, payload, stars):
    api("sendInvoice",{
        "chat_id":chat_id,"title":title,"description":desc,
        "payload":payload,"currency":"XTR",
        "prices":json.dumps([{"label":title,"amount":stars}])
    })

def answer_pq(pq_id, ok=True, err=None):
    d = {"pre_checkout_query_id":pq_id,"ok":ok}
    if err: d["error_message"] = err
    api("answerPreCheckoutQuery", d)

def get_tl_api_id():
    v = gs("tl_api_id", "")
    try: return int(v) if v else TELEGRAM_API_ID
    except: return TELEGRAM_API_ID

def get_tl_api_hash():
    v = gs("tl_api_hash", "")
    return v if v else TELEGRAM_API_HASH

def telethon_ready():
    return TELETHON and bool(get_tl_api_id()) and bool(get_tl_api_hash())

def telethon_verify_session(session_str):
    api_id, api_hash = get_tl_api_id(), get_tl_api_hash()
    if not TELETHON or not api_id or not api_hash:
        return False, "Telethon غير مفعّل"

    async def _verify():
        client = TelegramClient(StringSession(session_str), api_id, api_hash)
        await client.connect()
        try:
            if await client.is_user_authorized():
                me = await client.get_me()
                info = f"+{me.phone}" if me and me.phone else "—"
                if me: info += f" | {me.first_name or ''}"
                return True, info.strip()
            return False, "الجلسة منتهية"
        finally:
            await client.disconnect()

    try:
        loop = asyncio.new_event_loop()
        try: return loop.run_until_complete(_verify())
        finally: loop.close()
    except Exception as e:
        return False, str(e)

def _tl_run(coro_fn):
    loop = asyncio.new_event_loop()
    try: return loop.run_until_complete(coro_fn())
    finally: loop.close()

def tl_login_send_code(phone):
    if not telethon_ready(): return False, "", "Telethon غير مفعّل"
    async def _go():
        c = TelegramClient(StringSession(), get_tl_api_id(), get_tl_api_hash(),
                           system_version="4.16.30-vxCUSTOM", device_model="Desktop", app_version="4.0")
        await c.connect()
        try:
            r = await c.send_code_request(phone)
            return True, c.session.save(), r.phone_code_hash
        finally:
            await c.disconnect()
    try: return _tl_run(_go)
    except Exception as e: return False, "", f"{type(e).__name__}: {e}"

def tl_login_sign_in(session_str, phone, code, code_hash, password=None):
    async def _go():
        c = TelegramClient(StringSession(session_str), get_tl_api_id(), get_tl_api_hash(),
                           system_version="4.16.30-vxCUSTOM", device_model="Desktop", app_version="4.0")
        await c.connect()
        try:
            try:
                if password is not None and code is None:
                    await c.sign_in(password=password)
                else:
                    await c.sign_in(phone=phone, code=code, phone_code_hash=code_hash)
            except tel_errors.SessionPasswordNeededError:
                return "2fa", c.session.save()
            return "ok", c.session.save()
        finally:
            await c.disconnect()
    try: return _tl_run(_go)
    except Exception as e: return "error", f"{type(e).__name__}: {e}"

def ask_num_country(chat_id, uid, st, extra=""):
    st["step"]="add_num_country"
    kb={"inline_keyboard":[]}; row=[]
    for cname,(cflag,_) in get_all_countries().items():
        row.append({"text":f"{cflag} {cname}","callback_data":f"selcountry_{cname}","style":rnd()})
        if len(row)==3: kb["inline_keyboard"].append(row); row=[]
    if row: kb["inline_keyboard"].append(row)
    kb["inline_keyboard"].append([_b("btn_cancel","main_menu","danger")])
    states[uid]=st
    send(chat_id,f"{extra}🌍 <b>اختر دولة الرقم:</b>",kb)

def purchase_kb(txn):
    return {"inline_keyboard":[
        [_b("🔑 جلب الكود",f"getcode_{txn}","success"),_b("🚪 تسجيل خروج",f"logout_{txn}","danger")],
        [_b("btn_back","main_menu","danger")],
    ]}

def telethon_fetch_last_code(session_str):
    api_id, api_hash = get_tl_api_id(), get_tl_api_hash()
    if not TELETHON or not api_id or not api_hash:
        return None, None, "Telethon غير مضبوط"
    async def _go():
        c = TelegramClient(StringSession(session_str), api_id, api_hash,
                           system_version="4.16.30-vxCUSTOM", device_model="Desktop", app_version="4.0")
        await c.connect()
        try:
            if not await c.is_user_authorized():
                return None, None, "الجلسة منتهية"
            msgs = await c.get_messages(777000, limit=8)
            for m in msgs:
                mm = re.search(r'(\d{5,6})', m.text or "")
                if mm: return mm.group(1), m.date, None
            return None, None, None
        finally:
            await c.disconnect()
    try: return _tl_run(_go)
    except Exception as e: return None, None, f"{type(e).__name__}: {e}"

def telethon_logout_session(session_str):
    api_id, api_hash = get_tl_api_id(), get_tl_api_hash()
    if not TELETHON or not api_id or not api_hash:
        return False, "Telethon غير مضبوط"
    async def _go():
        c = TelegramClient(StringSession(session_str), api_id, api_hash,
                           system_version="4.16.30-vxCUSTOM", device_model="Desktop", app_version="4.0")
        await c.connect()
        try:
            if not await c.is_user_authorized():
                return True, None
            await c.log_out()
            return True, None
        finally:
            try: await c.disconnect()
            except Exception: pass
    try: return _tl_run(_go)
    except Exception as e: return False, f"{type(e).__name__}: {e}"

def _bg_getcode(chat_id, uid, txn):
    cur2 = conn.cursor()
    cur2.execute("SELECT session_str FROM purchase_sessions WHERE txn=? AND user_id=?", (txn,uid))
    r = cur2.fetchone()
    if not r:
        send(chat_id, "❌ الجلسة غير متوفرة"); return
    code, dt, err = telethon_fetch_last_code(r[0])
    if err:
        send(chat_id, f"⚠️ <b>تعذر جلب الكود</b>\n\n<code>{err}</code>", purchase_kb(txn))
        return
    if not code:
        send(chat_id, "⏳ <b>ما وصل كود بعد</b>", purchase_kb(txn)); return
    try:
        mins = max(0, int((datetime.now(dt.tzinfo) - dt).total_seconds() // 60))
        age = f"\n🕒 وصل قبل {mins} دقيقة" if mins else "\n🕒 وصل الآن"
    except Exception:
        age = ""
    send(chat_id, f"🔑 <b>آخر كود:</b> <code>{code}</code>{age}", purchase_kb(txn))

def _bg_logout(chat_id, uid, txn):
    cur2 = conn.cursor()
    cur2.execute("SELECT session_str FROM purchase_sessions WHERE txn=? AND user_id=?", (txn,uid))
    r = cur2.fetchone()
    if not r:
        send(chat_id, "❌ الجلسة غير متوفرة"); return
    ok, err = telethon_logout_session(r[0])
    if ok:
        cur2.execute("DELETE FROM purchase_sessions WHERE txn=?", (txn,)); conn.commit()
        send(chat_id, "✅ <b>تم تسجيل الخروج من الجلسة</b>", back())
    else:
        send(chat_id, f"⚠️ <b>تعذر تسجيل الخروج</b>\n\n<code>{err}</code>", purchase_kb(txn))

def telethon_wait_otp_bg(session_str, phone, buyer_uid, two_fa="", price=0, country="", txn=""):
    api_id   = get_tl_api_id()
    api_hash = get_tl_api_hash()
    if not TELETHON or not api_id or not api_hash:
        send(buyer_uid, "⚠️ Telethon غير مضبوط"); return

    async def _wait_otp():
        from telethon import events as tl_events
        client = TelegramClient(
            StringSession(session_str), api_id, api_hash,
            system_version="4.16.30-vxCUSTOM", device_model="Desktop", app_version="4.0",
        )
        await client.connect()
        try:
            if not await client.is_user_authorized():
                send(buyer_uid, "⚠️ الجلسة منتهية")
                return

            otp_ready  = asyncio.Event()
            found_code = [None]

            def _extract_code(text):
                m = re.search(r'(\d{5,6})', text or "")
                return m.group(1) if m else None

            @client.on(tl_events.NewMessage(from_users=777000))
            async def _on_service_msg(event):
                if otp_ready.is_set(): return
                code = _extract_code(event.raw_text)
                if code:
                    found_code[0] = code
                    otp_ready.set()

            try:
                recent = await client.get_messages(777000, limit=5)
                if recent:
                    cutoff = datetime.now(datetime.timezone.utc) - timedelta(seconds=30)
                    for msg in recent:
                        if msg.date and msg.date > cutoff:
                            code = _extract_code(msg.text or "")
                            if code:
                                found_code[0] = code
                                otp_ready.set()
                                break
            except Exception: pass

            if not otp_ready.is_set():
                send(
                    buyer_uid,
                    f"📱 <b>الرقم جاهز للتفعيل!</b>\n\n📞 الرقم: <code>{phone}</code>\n\n⏳ <b>المهلة: 10 دقائق</b>",
                    purchase_kb(txn) if txn else None,
                )

            try:
                await asyncio.wait_for(otp_ready.wait(), timeout=600)
            except asyncio.TimeoutError:
                send(buyer_uid, "⏰ <b>انتهت المهلة (10 دقائق)</b>")
                return

            code = found_code[0]
            if not code: return

            two_fa_line = (f"🔐 كلمة المرور الثنائية: <b><code>{two_fa}</code></b>\n" if two_fa else "")
            send(
                buyer_uid,
                f"✅ <b>وصل كودك!</b>\n\n📞 الرقم: <code>{phone}</code>\n🔑 الكود: <b><code>{code}</code></b>\n{two_fa_line}",
                purchase_kb(txn) if txn else None,
            )
        finally:
            try: await client.disconnect()
            except Exception: pass

    try:
        loop = asyncio.new_event_loop()
        try: loop.run_until_complete(_wait_otp())
        finally: loop.close()
    except Exception as e:
        pass

def telethon_verify_session_bg(session_str, phone, admin_uid):
    ok, info = telethon_verify_session(session_str)
    if ok:
        send(admin_uid, f"✅ <b>الجلسة صالحة وجاهزة!</b>\n\n📞 {info}")
    else:
        send(admin_uid, f"⚠️ <b>تحذير: الجلسة غير صالحة</b>\n\n❌ {info}")

def _send_ch(channel, text, kb=None):
    for t in [f"@{channel}", channel]:
        try:
            d = {"chat_id":t,"text":text,"parse_mode":"HTML"}
            if kb: d["reply_markup"] = json.dumps(kb)
            r = _session.post(f"{URL}/sendMessage", json=d, timeout=8).json()
            if r.get("ok"): return
        except: pass

def proof_success(number, price, country, uid, txn):
    flag = COUNTRIES.get(country,("🏳️",""))[0]
    vh = gen_hash(txn, uid, price)
    _send_ch(get_proof_channel(),
        f"🔐 <b>إثبات معاملة #{txn}</b>\n{'━'*20}\n"
        f"✅ <b>شراء ناجح</b>\n{'━'*20}\n"
        f"📞 الرقم: <code>{mask_activation(number)}</code>\n"
        f"💵 المبلغ: <b>{fmt(price)}</b>\n"
        f"🌍 الدولة: {country} {flag}\n"
        f"👤 العميل: <code>#{uid}</code>\n{'━'*20}\n"
        f"🔑 Hash: <code>{vh}</code>\n{'━'*20}\n"
        f"🤖 @{BOT_USERNAME}")

def proof_failed(number, price, uid, reason="إلغاء"):
    txn = gen_txn()
    _send_ch(get_proof_channel(),
        f"🔐 <b>إثبات معاملة #{txn}</b>\n{'━'*20}\n"
        f"❌ <b>الحالة: {reason}</b>\n{'━'*20}\n"
        f"📞 الرقم: <code>{mask_activation(number)}</code>\n"
        f"💵 السعر: <b>{fmt(price)}</b>\n"
        f"👤 العميل: <code>#{uid}</code>")

def activation_notif(number, code, vcode, price, country, uid, auto_mode=False):
    flag = COUNTRIES.get(country,("🏳️",""))[0]
    mn   = mask_activation(number)
    mode_tag = "⚡ تلقائي" if auto_mode else "🔧 يدوي"
    _send_ch(get_activation_channel(),
        f"✅ <b>تفعيل جديد! {mode_tag}</b>\n\n"
        f"🌍 {country} {flag}\n"
        f"📞 <code>{mn}</code>\n"
        f"💵 <b>{fmt(price)}</b>  |  👤 <code>{uid}</code>",
        {"inline_keyboard":[[{"text":f"🤖 @{BOT_USERNAME}","url":f"https://t.me/{BOT_USERNAME}"}]]})

captcha_sessions = {}

def start_captcha(chat_id, uid):
    code = str(random.randint(100000,999999))
    opts = {code}
    while len(opts) < 6:
        opts.add(str(random.randint(100000,999999)))
    opts = list(opts); random.shuffle(opts)
    captcha_sessions[uid] = {"code": code, "attempts": 0}
    kb = {"inline_keyboard": []}
    row = []
    for opt in opts:
        row.append({"text": opt, "callback_data": f"cap_{opt}", "style": rnd()})
        if len(row) == 2:
            kb["inline_keyboard"].append(row)
            row = []
    if row:
        kb["inline_keyboard"].append(row)
    cap = ("🔐 <b>التحقق الأمني — خطوة أخيرة</b>\n\n"
           "🔢 اختر الرقم الصحيح من الصورة:")
    if PILLOW:
        img = _gen_captcha_img(code)
        send_photo(chat_id, img, caption=cap, kb=kb)
    else:
        send(chat_id, f"{cap}\n\n<b>الرمز:</b> <code>{code}</code>", kb)

def _gen_captcha_img(code):
    w,h = 300,100
    bg = (random.randint(230,250),random.randint(230,250),random.randint(230,250))
    img = Image.new("RGB",(w,h),color=bg)
    draw = ImageDraw.Draw(img)
    for _ in range(12):
        x1,y1,x2,y2 = random.randint(0,w),random.randint(0,h),random.randint(0,w),random.randint(0,h)
        draw.line([(x1,y1),(x2,y2)],fill=(random.randint(150,220),)*3,width=2)
    for _ in range(800):
        draw.point((random.randint(0,w-1),random.randint(0,h-1)),fill=(random.randint(0,200),)*3)
    fonts=[]
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"]:
        try: fonts.append(ImageFont.truetype(p,random.randint(42,55)))
        except: pass
    if not fonts: fonts=[ImageFont.load_default()]
    x_pos=20
    for ch in code:
        font=random.choice(fonts)
        try: font=ImageFont.truetype(font.path,random.randint(40,56))
        except: pass
        tmp=Image.new("RGBA",(70,80),(0,0,0,0))
        td=ImageDraw.Draw(tmp)
        td.text((5,5),ch,font=font,fill=(random.randint(0,80),random.randint(0,80),random.randint(0,120)))
        tmp=tmp.rotate(random.randint(-25,25),expand=True)
        img.paste(tmp,(x_pos,random.randint(8,30)),tmp)
        x_pos+=random.randint(42,54)
    img=img.filter(ImageFilter.GaussianBlur(radius=0.9))
    buf=io.BytesIO(); img.save(buf,format="PNG"); buf.seek(0); return buf.read()

def is_owner(uid): return uid==OWNER_ID
def is_admin(uid):
    if uid==OWNER_ID: return True
    cur.execute("SELECT 1 FROM admins WHERE user_id=?",(uid,))
    return bool(cur.fetchone())
def is_agent(uid):
    cur.execute("SELECT level,commission_rate,total_earned FROM agents WHERE user_id=?",(uid,))
    return cur.fetchone()

def ensure(uid):
    cur.execute("INSERT OR IGNORE INTO users(user_id,balance,join_date,last_active,verified,phone_ok) VALUES(?,0,?,?,0,0)",
                (uid,now(),now()))
    conn.commit()

def touch(uid):
    ensure(uid)
    cur.execute("UPDATE users SET last_active=? WHERE user_id=?",(now(),uid))
    conn.commit()

def is_verified(uid):
    cur.execute("SELECT verified FROM users WHERE user_id=?",(uid,))
    r=cur.fetchone(); return bool(r and r[0])

def is_phone_ok(uid):
    cur.execute("SELECT phone_ok FROM users WHERE user_id=?",(uid,))
    r=cur.fetchone(); return bool(r and r[0])

def set_phone(uid, phone):
    ensure(uid)
    cur.execute("UPDATE users SET phone=?,phone_ok=1 WHERE user_id=?",(phone,uid))
    conn.commit()

def set_verified(uid):
    ensure(uid)
    cur.execute("UPDATE users SET verified=1 WHERE user_id=?",(uid,))
    conn.commit()

def get_bal(uid):
    cur.execute("SELECT balance FROM users WHERE user_id=?",(uid,))
    r=cur.fetchone(); return r[0] if r else 0

def _audit(uid, op, amount, bb, ba, txn=""):
    sig = _bal_sig(uid,op,amount,bb,ba,txn)
    cur.execute("INSERT INTO balance_audit(user_id,op,amount,balance_before,balance_after,ref_txn,sig,ts) VALUES(?,?,?,?,?,?,?,?)",
                (uid,op,amount,bb,ba,txn,sig,now()))
    conn.commit()

def add_bal(uid, cents, txn="", op="credit"):
    if cents<=0: return
    ensure(uid)
    bb=get_bal(uid)
    cur.execute("UPDATE users SET balance=balance+? WHERE user_id=?",(cents,uid))
    conn.commit()
    _audit(uid,op,cents,bb,get_bal(uid),txn)

def sub_bal(uid, cents, txn="", op="debit"):
    if cents<=0: return False
    ensure(uid)
    bb=get_bal(uid)
    if bb<cents: return False
    cur.execute("UPDATE users SET balance=balance-? WHERE user_id=? AND balance>=?",(cents,uid,cents))
    if cur.rowcount==0: conn.commit(); return False
    conn.commit()
    _audit(uid,op,cents,bb,get_bal(uid),txn)
    return True

def referral(referrer, new_user):
    return

def daily_bonus(uid):
    cur.execute("SELECT last_daily FROM users WHERE user_id=?",(uid,))
    row=cur.fetchone(); last=row[0] if row else None
    if last:
        try:
            if datetime.strptime(last,"%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")==today(): return None
        except: pass
    mx = get_daily_bonus_max()
    bonus = random.randint(1, max(1,mx))
    add_bal(uid, bonus, op="daily_bonus")
    cur.execute("UPDATE users SET last_daily=? WHERE user_id=?",(now(),uid))
    conn.commit()
    return bonus

def check_sub(uid):
    cur.execute("SELECT channel FROM sub_channels")
    ns=[]
    for (ch,) in cur.fetchall():
        try:
            r=_session.get(f"{URL}/getChatMember",params={"chat_id":f"@{ch}","user_id":uid},timeout=5).json()
            if r.get("result",{}).get("status","") in ("left","kicked",""): ns.append(ch)
        except: pass
    return ns

def use_emoji(): return gs("use_custom_emoji","0")=="1"

def _b(text_or_key, cb=None, style=None, url=None):
    text = get_label(text_or_key) if text_or_key.startswith("btn_") else text_or_key
    btn  = {"text":text}
    if url: btn["url"]=url
    else:   btn["callback_data"]=cb or text_or_key; btn["style"]=style or rnd()
    if text_or_key.startswith("btn_"): with_premium(btn, text_or_key)
    return btn

def back(to="main_menu"): return {"inline_keyboard":[[_b("btn_back",to,"danger")]]}
def cancel():             return {"inline_keyboard":[[_b("btn_cancel","main_menu","danger")]]}
def sub_kb(channels):
    kb={"inline_keyboard":[]}
    for ch in channels:
        kb["inline_keyboard"].append([{"text":f"📢 اشترك في @{ch}","url":f"https://t.me/{ch}"}])
    kb["inline_keyboard"].append([_b("✅ تحققت من اشتراكي","check_sub","success")])
    return kb

def main_kb(uid):
    rows=[
        [_b("btn_buy","buy","success")],
        [_b("btn_cat_fraud","cat_fraud","danger"),_b("btn_cat_fake","cat_fake","primary")],
        [_b("btn_transfer","transfer_bal","success"),_b("btn_balance","balance_show","primary")],
        [_b("btn_recharge","recharge",rnd()),_b("btn_mystats","mystats",rnd())],
        [with_premium({"text":get_label("btn_activation"),"url":f"https://t.me/{get_activation_channel()}"},"btn_activation")],
        [with_premium({"text":get_label("btn_support"),"url":SUPPORT},"btn_support")],
    ]
    if is_agent(uid):  rows.append([_b("btn_agent","agent_panel","primary")])
    if is_admin(uid):  rows.append([_b("btn_admin","admin_panel",rnd())])
    if is_owner(uid):  rows.append([_b("btn_owner","owner_panel","danger")])
    return {"inline_keyboard":rows}

def admin_kb(uid):
    def apb(label, cb, perm=None, style=None):
        if perm and not has_perm(uid, perm): return None
        return _b(label, cb, style or rnd())

    rows = []
    r1=[apb("📊 إحصائيات","admin_stats","view_stats"), apb("📱 إدارة الأرقام","admin_numbers","add_numbers")]
    if any(r1): rows.append([b for b in r1 if b])
    r2=[apb("👥 المستخدمون","admin_users","manage_users"), apb("🔄 طلبات الشحن","admin_recharge","manage_recharge")]
    if any(r2): rows.append([b for b in r2 if b])
    r3=[apb("💰 إدارة الرصيد","admin_balance","grant_balance"), apb("📣 بث رسالة","admin_broadcast","broadcast")]
    if any(r3): rows.append([b for b in r3 if b])
    r4=[apb("🔔 اشتراك إجباري","admin_subscribe","manage_subs"), apb("💲 أسعار الدول","admin_prices","manage_prices")]
    if any(r4): rows.append([b for b in r4 if b])
    r5=[apb("📜 سجل المبيعات","sales_log","sales_log"), apb("⚙️ متقدم","admin_advanced")]
    if any(r5): rows.append([b for b in r5 if b])
    rows.append([_b("btn_back","main_menu","danger")])
    return {"inline_keyboard":rows}

def owner_kb():
    return {"inline_keyboard":[
        [_b("👔 الوكلاء","owner_agents"),      _b("👤 الإداريون","owner_admins")],
        [_b("💸 شحن جماعي","owner_mass_recharge"),_b("📜 سجل المبيعات","owner_sales_log")],
        [_b("💰 منح رصيد","owner_grant"),      _b("🛠 إعدادات البوت","owner_bot_settings")],
        [_b("💎 إعدادات TON","owner_ton"),     _b("⭐ إعدادات النجوم","owner_stars")],
        [_b("📣 القنوات","owner_channels"),    _b("🔇 وضع الصيانة","owner_maintenance")],
        [_b("🎨 تخصيص الأزرار","owner_emoji_mgr"),_b("🧹 تنظيف","owner_clean","danger")],
        [_b("📱 إدارة الحسابات","owner_accounts"),_b("💳 تعديل صفحة الشحن","owner_recharge_edit","success")],
        [_b("🔐 سجل الرصيد","owner_balance_audit"),_b("🔑 صلاحيات الأدمن","owner_admin_perms")],
        [_b("🔌 إعدادات Telethon","owner_telethon","success")],
        [_b("📂 استيراد أرقام من ملف TXT","owner_import_txt","success")],
        [_b("💬 استيراد أرقام WhatsApp","owner_import_wa","primary")],
        [_b("btn_back","main_menu","danger")],
    ]}

def agent_kb():
    return {"inline_keyboard":[
        [_b("📊 إحصائياتي","agent_stats",rnd()),_b("🔗 رابط الوكيل","agent_invite",rnd())],
        [_b("btn_back","main_menu","danger")],
    ]}

states = {}
def clr(uid): states.pop(uid, None)

CAT_KEYS = {"fraud":"btn_cat_fraud","fake":"btn_cat_fake"}

def show_countries(chat_id, mid, cat=""):
    cur.execute("SELECT country,COUNT(*) FROM numbers WHERE status='متاح' AND COALESCE(category,'')=? GROUP BY country",(cat,))
    avail = dict(cur.fetchall())
    all_ctry = get_all_countries()
    avail_btns = []
    unavail_btns = []
    for name,(flag,_) in all_ctry.items():
        if is_country_hidden(name): continue
        cnt=avail.get(name,0)
        price=get_country_price(name)
        if cnt>0:
            avail_btns.append({"text":f"{flag} {name} ({cnt}) {fmt(price)}","callback_data":(f"ctryc_{cat}_{name}" if cat else f"ctry_{name}"),"style":"success"})
    all_btns = avail_btns + unavail_btns
    kb = {"inline_keyboard":[]}
    row=[]
    for btn in all_btns:
        row.append(btn)
        if len(row)==2: kb["inline_keyboard"].append(row); row=[]
    if row: kb["inline_keyboard"].append(row)
    kb["inline_keyboard"].append([_b("btn_back","main_menu","danger")])
    head = f"<b>{get_label(CAT_KEYS[cat])}</b>" if cat in CAT_KEYS else "🛒 <b>اختر دولة الرقم المطلوب</b>"
    if not all_btns:
        edit(chat_id,mid,head+"\n\n❌ <b>لا توجد أرقام متاحة بهذا القسم حالياً</b>",kb); return
    edit(chat_id,mid,head+"\n\n<i>السعر يظهر بجانب كل دولة</i>",kb)

def show_numbers(chat_id, mid, country, cat=""):
    cur.execute("SELECT id,number,price FROM numbers WHERE country=? AND status='متاح' AND COALESCE(category,'')=? ORDER BY price",(country,cat))
    nums=cur.fetchall()
    back_to = f"cat_{cat}" if cat else "buy"
    if not nums:
        edit(chat_id,mid,"❌ <b>نفدت أرقام هذه الدولة</b>",back(back_to)); return
    flag=COUNTRIES.get(country,("🏳️",""))[0]
    kb={"inline_keyboard":[]}
    for n in nums:
        kb["inline_keyboard"].append([{"text":f"📞 {mask_activation(n[1])}  —  {fmt(n[2])}","callback_data":f"preconfirm_{n[0]}","style":rnd()}])
    kb["inline_keyboard"].append([_b("btn_back",back_to,"danger")])
    edit(chat_id,mid,f"{flag} <b>أرقام {country} المتاحة:</b>",kb)

def confirm_purchase(chat_id, uid, nid, mid, cb_id):
    cur.execute("SELECT number,price,country,auto_mode FROM numbers WHERE id=? AND status='متاح'",(nid,))
    row=cur.fetchone()
    if not row: answer(cb_id,"❌ الرقم لم يعد متاحاً",True); return
    number,price,country,auto_mode=row
    flag=COUNTRIES.get(country,("🏳️",""))[0]
    bal=get_bal(uid)
    ok=bal>=price
    mode_tag="⚡ إرسال كود تلقائي" if auto_mode else "🔧 كود مسجّل مسبقاً"
    edit(chat_id,mid,
        f"🛒 <b>تأكيد الشراء</b>\n\n"
        f"📞 الرقم: <code>{mask_activation(number)}</code>\n"
        f"🌍 الدولة: {country} {flag}\n"
        f"💵 السعر: <b>{fmt(price)}</b>\n"
        f"💰 رصيدك: <b>{fmt(bal)}</b>\n"
        f"🔌 النوع: {mode_tag}\n\n"
        f"{'✅ رصيدك كافٍ' if ok else '❌ رصيدك غير كافٍ — اشحن أولاً'}",
        {"inline_keyboard":[[
            _b("✅ تأكيد الشراء",f"confirm_{nid}","success"),
            _b("❌ إلغاء",f"cancel_buy_{nid}","danger"),
        ]]})
    answer(cb_id)

def do_purchase(chat_id, uid, nid, mid, cb_id):
    if not check_rate_limit(uid,"buy",10):
        answer(cb_id,"⚠️ تجاوزت حد العمليات المسموح.",True); return
    cur.execute("SELECT number,code,verify_code,price,country,session_str,auto_mode,two_fa FROM numbers WHERE id=? AND status='متاح'",(nid,))
    row=cur.fetchone()
    if not row: answer(cb_id,"❌ الرقم لم يعد متاحاً",True); return
    number,code,vcode,price,country,session_str,auto_mode,two_fa=row
    two_fa=two_fa or ""
    txn=gen_txn()
    if not sub_bal(uid,price,txn=txn,op="purchase"):
        answer(cb_id,"❌ رصيدك غير كافٍ. اشحن أولاً",True); return
    cur.execute("DELETE FROM numbers WHERE id=?",(nid,))
    cur.execute("INSERT INTO history(user_id,number,code,verify_code,price,country,purchase_date,txn_id,auto_sent) VALUES(?,?,?,?,?,?,?,?,?)",
                (uid,number,code,vcode,price,country,now(),txn,1 if auto_mode else 0))
    conn.commit()
    if auto_mode:
        edit(chat_id,mid,
            f"✅ <b>تم الشراء بنجاح!</b>\n\n"
            f"📞 الرقم: <code>{number}</code>\n"
            f"💵 دفعت: <b>{fmt(price)}</b>\n"
            f"💰 رصيدك المتبقي: <b>{fmt(get_bal(uid))}</b>\n"
            f"🆔 العملية: <code>{txn}</code>\n\n"
            f"⏳ <i>جاري إعداد الكود التلقائي...</i>",purchase_kb(txn) if session_str else back())
        if session_str:
            cur.execute("INSERT OR REPLACE INTO purchase_sessions(txn,user_id,number,session_str,two_fa) VALUES(?,?,?,?,?)",(txn,uid,number,session_str,two_fa))
            conn.commit()
        threading.Thread(target=telethon_wait_otp_bg, args=(session_str,number,uid,two_fa,price,country,txn), daemon=True).start()
    else:
        edit(chat_id,mid,
            f"✅ <b>تم الشراء بنجاح!</b>\n\n"
            f"📞 الرقم: <code>{number}</code>\n"
            f"🔑 الكود: <code>{code}</code>\n"
            +(f"🔐 رمز التحقق: <code>{vcode}</code>\n" if vcode else "")+
            f"💵 دفعت: <b>{fmt(price)}</b>\n"
            f"💰 رصيدك المتبقي: <b>{fmt(get_bal(uid))}</b>\n"
            f"🆔 العملية: <code>{txn}</code>",back())
    answer(cb_id)
    activation_notif(number,code,vcode,price,country,uid,auto_mode=bool(auto_mode))
    proof_success(number,price,country,uid,txn)
    cur.execute("SELECT referrer_id FROM users WHERE user_id=?",(uid,))
    rr=cur.fetchone()
    if rr and rr[0]:
        ag=is_agent(rr[0])
        if ag:
            comm=math.floor(price*ag[1]/100)
            if comm>0:
                add_bal(rr[0],comm,txn=txn,op="commission")
                cur.execute("UPDATE agents SET total_earned=total_earned+? WHERE user_id=?",(comm,rr[0]))
                conn.commit()

def cancel_purchase(chat_id, uid, nid, mid, cb_id):
    cur.execute("SELECT number,price FROM numbers WHERE id=? AND status='متاح'",(nid,))
    row=cur.fetchone()
    if row: proof_failed(row[0],row[1],uid,"إلغاء بواسطة المستخدم")
    edit(chat_id,mid,"❌ <b>تم إلغاء الشراء</b>\n\n💰 لم يُخصم أي رصيد",back())
    answer(cb_id,"تم الإلغاء")

DEFAULT_RECHARGE_TEXT = "💳 <b>شحن الرصيد</b>\n\n💎 <b>عبر آسيا سيل أو المطور:</b>\n\nاختر:"

def show_recharge(chat_id, mid):
    kb={"inline_keyboard":[
        [_b("💳 شحن تلقائي (آسيا سيل ODP)", "recharge_asiacell_start", "success")],
        [_b("btn_recharge_dev", url=gs("recharge_dev_url", SUPPORT))],
        [_b("btn_back", "main_menu", "danger")],
    ]}
    edit(chat_id, mid, gs("recharge_text", DEFAULT_RECHARGE_TEXT), kb)

def ac_cleanup(uid):
    """إغلاق متصفح المستخدم وتنظيف الجلسة بأمان"""
    with _browser_lock:
        session = browser_sessions.pop(uid, None)
    if session:
        try:
            if session.get("browser"):
                session["browser"].close()
        except Exception:
            pass
        try:
            if session.get("playwright"):
                session["playwright"].stop()
        except Exception:
            pass

def ac_step1_login_and_captcha(chat_id, uid, phone_number):
    """الخطوة 1: فتح صفحة تسجيل الدخول، إدخال الرقم، والتقاط الكابتشا."""
    if not PLAYWRIGHT_OK:
        return False, "مكتبة Playwright غير مثبتة على السيرفر."
    ac_cleanup(uid)
    try:
        p = sync_playwright().start()
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        with _browser_lock:
            browser_sessions[uid] = {
                "playwright": p,
                "browser": browser,
                "page": page,
                "created_at": time.time()
            }

        page.goto("https://www.asiacell.com/personal/my-account/login", timeout=60000)

        phone_input_selector = "input#msisdn, input[name='msisdn'], input[type='tel']"
        page.wait_for_selector(phone_input_selector, timeout=15000)
        page.fill(phone_input_selector, phone_number)

        captcha_img_selector = "canvas#captchaCanvas, img.captcha-img, .captcha-container"
        page.wait_for_selector(captcha_img_selector, timeout=15000)

        captcha_element = page.locator(captcha_img_selector).first
        screenshot_bytes = captcha_element.screenshot()
        return True, screenshot_bytes
    except Exception as e:
        print(f"[AC Step 1 Error] {e}")
        ac_cleanup(uid)
        return False, str(e)

def ac_step2_verify_captcha(chat_id, uid, captcha_text):
    """الخطوة 2: إدخال نص الكابتشا والضغط على إرسال طلب كود SMS."""
    with _browser_lock:
        session = browser_sessions.get(uid)
    if not session or "page" not in session:
        return False, "انتهت جلسة المتصفح، يرجى بدء العملية من جديد."
    page = session["page"]
    try:
        captcha_input_selector = "input#captcha, input[name='captcha'], input.captcha-input"
        page.wait_for_selector(captcha_input_selector, timeout=10000)
        page.fill(captcha_input_selector, captcha_text)

        submit_btn_selector = "button#sendOtpBtn, button[type='submit'], .btn-submit-otp"
        page.click(submit_btn_selector)

        time.sleep(2.5)
        error_texts = page.locator(".error-message, .alert-danger").all_text_contents()
        if any("خطأ" in err or "incorrect" in err.lower() or "invalid" in err.lower() for err in error_texts):
            captcha_img_selector = "canvas#captchaCanvas, img.captcha-img, .captcha-container"
            new_img = None
            try:
                new_img = page.locator(captcha_img_selector).first.screenshot()
            except Exception:
                pass
            return "retry_captcha", new_img

        return True, "تم التحقق من الكابتشا وإرسال رمز SMS."
    except Exception as e:
        print(f"[AC Step 2 Error] {e}")
        ac_cleanup(uid)
        return False, str(e)

def ac_step3_submit_otp_and_transfer(chat_id, uid, otp_code, selected_amount):
    """الخطوة 3: إدخال رمز SMS، الانتقال لصفحة التحويل (tab=3)، وإتمام التحويل للمطور."""
    with _browser_lock:
        session = browser_sessions.get(uid)
    if not session or "page" not in session:
        return False, "انتهت جلسة المتصفح، يرجى إعادة المحاولة."
    page = session["page"]
    try:
        otp_input_selector = "input#otpCode, input[name='otp'], input.otp-input"
        page.wait_for_selector(otp_input_selector, timeout=10000)
        page.fill(otp_input_selector, otp_code)

        verify_login_btn = "button#verifyOtpBtn, button.btn-verify"
        page.click(verify_login_btn)
        time.sleep(3)

        page.goto("https://www.asiacell.com/personal/my-account?tab=3", timeout=60000)

        # إدخال رقم المطور المستلم (RECEIVER_ASIACELL_PHONE)
        receiver_input_selector = "input#receiverPhone, input[name='receiver_msisdn']"
        page.wait_for_selector(receiver_input_selector, timeout=15000)
        page.fill(receiver_input_selector, RECEIVER_ASIACELL_PHONE)

        # إدخال المبلغ المختار (selected_amount)
        amount_input_selector = "input#transferAmount, input[name='amount'], select#amountSelect"
        page.fill(amount_input_selector, str(selected_amount))

        transfer_submit_btn = "button#confirmTransferBtn, button.btn-transfer-submit"
        page.click(transfer_submit_btn)
        time.sleep(2)

        modal_confirm_btn = "button.confirm-modal-btn, div.modal button.btn-primary"
        if page.locator(modal_confirm_btn).is_visible():
            page.click(modal_confirm_btn)

        time.sleep(3)
        success_msg_selector = ".success-message, .alert-success, div.alert-success"
        if page.locator(success_msg_selector).is_visible():
            ac_cleanup(uid)
            return True, "تم تحويل الرصيد بنجاح إلى رقم المطور!"
        else:
            error_text = " | ".join([t.strip() for t in page.locator(".error-message, .alert-danger").all_text_contents() if t.strip()])
            ac_cleanup(uid)
            return False, error_text or "تعذر إتمام التحويل (تأكد من توفر الرصيد أو صحة الرمز)."
    except Exception as e:
        print(f"[AC Step 3 Error] {e}")
        ac_cleanup(uid)
        return False, str(e)

def show_asiacell_amounts(chat_id, mid):
    amounts = [
        (1000, "1,000 د.ع"), (5000, "5,000 د.ع"),
        (10000, "10,000 د.ع"), (15000, "15,000 د.ع"),
        (20000, "20,000 د.ع"), (25000, "25,000 د.ع"),
        (30000, "30,000 د.ع"), (50000, "50,000 د.ع"),
        (60000, "60,000 د.ع")
    ]
    kb = {"inline_keyboard": []}
    row = []
    for val, lbl in amounts:
        row.append({"text": f"💵 {lbl}", "callback_data": f"ac_amt_{val}", "style": rnd()})
        if len(row) == 2:
            kb["inline_keyboard"].append(row)
            row = []
    if row:
        kb["inline_keyboard"].append(row)
    kb["inline_keyboard"].append([_b("btn_back", "recharge", "danger")])
    edit(chat_id, mid, "💳 <b>اختر فئة الشحن المطلوبة (آسيا سيل):</b>", kb)

def show_stars_menu(chat_id, mid):
    spd=get_stars_per_dollar()
    opts=[(50,int(50*100/spd)),(100,int(100*100/spd)),(200,int(200*100/spd)),
          (500,int(500*100/spd)),(1000,int(1000*100/spd)),(2000,int(2000*100/spd))]
    kb={"inline_keyboard":[]}
    for stars,cents in opts:
        kb["inline_keyboard"].append([{"text":f"⭐ {stars} نجمة  ←  {fmt(cents)}","callback_data":f"stars_{stars}","style":rnd()}])
    kb["inline_keyboard"].append([_b("btn_back","recharge","danger")])
    edit(chat_id,mid,f"⭐ <b>شحن بنجوم تيليجرام</b>\n\n• {spd} نجمة = $1.00\nاختر المبلغ:",kb)

def show_emoji_manager(chat_id, mid):
    kb={"inline_keyboard":[]}
    row=[]
    for key, default in DEFAULT_BTNS.items():
        cur_lbl = get_label(key)
        short   = cur_lbl[:16]+("…" if len(cur_lbl)>16 else "")
        row.append({"text":f"✏️ {short}"+(" 💎" if get_premium_id(key) else ""),"callback_data":f"editbtn_{key}","style":rnd()})
        if len(row)==2: kb["inline_keyboard"].append(row); row=[]
    if row: kb["inline_keyboard"].append(row)
    emoji_on = gs("use_custom_emoji","0")=="1"
    kb["inline_keyboard"].append([{"text":f"{'✅' if emoji_on else '❌'} إيموجي مميز تيليجرام",
                                    "callback_data":"toggle_emoji","style":"success" if emoji_on else "danger"}])
    kb["inline_keyboard"].append([_b("🔄 إعادة تعيين كل الإيموجي","reset_all_emoji","danger")])
    kb["inline_keyboard"].append([_b("btn_back","owner_panel","danger")])
    edit(chat_id,mid, "🎨 <b>تخصيص الأزرار</b>", kb)

def show_emoji_picker(chat_id, mid, btn_key):
    kb={"inline_keyboard":[]}
    row=[]
    for i,em in enumerate(QUICK_EMOJI):
        row.append({"text":em,"callback_data":f"eset_{btn_key}_{i}","style":rnd()})
        if len(row)==8: kb["inline_keyboard"].append(row); row=[]
    if row: kb["inline_keyboard"].append(row)
    kb["inline_keyboard"].append([
        _b("✏️ إيموجي مخصص",f"ecustom_{btn_key}",rnd()),
        _b("🗑 إزالة الإيموجي",f"eremove_{btn_key}","danger"),
    ])
    kb["inline_keyboard"].append([_b("btn_back","owner_emoji_mgr","danger")])
    cur_lbl = get_label(btn_key)
    edit(chat_id,mid, f"🎨 <b>اختر إيموجي للزر:</b>\n<b>{cur_lbl}</b>", kb)

def show_admin_perms_list(chat_id, mid):
    cur.execute("SELECT user_id,added_date FROM admins")
    adms=cur.fetchall()
    if not adms:
        edit(chat_id,mid,"❌ لا يوجد إداريون بعد",back("owner_panel")); return
    kb={"inline_keyboard":[]}
    for ad in adms:
        perms=get_admin_perms(ad[0])
        granted=sum(1 for v in perms.values() if v)
        kb["inline_keyboard"].append([_b(f"👤 {ad[0]} — {granted}/{len(perms)} صلاحية",f"admperm_{ad[0]}",rnd())])
    kb["inline_keyboard"].append([_b("btn_back","owner_panel","danger")])
    edit(chat_id,mid,"🔑 <b>صلاحيات الإداريين</b>",kb)

def show_admin_perms_panel(chat_id, mid, target_uid):
    perms=get_admin_perms(target_uid)
    kb={"inline_keyboard":[]}
    for perm,label in PERM_LABELS.items():
        val=perms.get(perm,DEFAULT_ADMIN_PERMS.get(perm,0))
        icon="✅" if val else "❌"
        kb["inline_keyboard"].append([{"text":f"{icon} {label}", "callback_data":f"aptog_{target_uid}_{perm}", "style":"success" if val else "danger"}])
    kb["inline_keyboard"].append([
        _b("✅ منح الكل",f"apall_{target_uid}_1","success"),
        _b("❌ سحب الكل",f"apall_{target_uid}_0","danger"),
    ])
    kb["inline_keyboard"].append([_b("btn_back","owner_admin_perms","danger")])
    edit(chat_id,mid, f"🔑 <b>صلاحيات الأدمن</b>\n👤 المعرّف: <code>{target_uid}</code>",kb)

def show_accounts_panel(chat_id, mid):
    cur.execute("SELECT id,number,status,added_date,note FROM accounts ORDER BY added_date DESC LIMIT 20")
    rows=cur.fetchall()
    txt="📱 <b>إدارة الحسابات</b>\n\n"
    if rows:
        for r in rows:
            icon="✅" if r[2]=="نشط" else ("🔒" if r[2]=="مُستخدم" else "❌")
            txt+=f"{icon} <code>{r[1]}</code> — {r[2]}\n\n"
    else: txt+="❌ لا توجد حسابات مضافة"
    kb={"inline_keyboard":[
        [_b("➕ إضافة","acc_add_start","success"),_b("🗑 حذف","acc_del_start","danger")],
        [_b("btn_back","owner_panel","danger")],
    ]}
    edit(chat_id,mid,txt[:4000],kb)

print("╔══════════════════════════════════════════╗")
print("║  بوت شراء الأرقام — النسخة الاحترافية  ║")
print(f"║  المالك: {OWNER_ID:<33}║")
print(f"║  البوت:  @{BOT_USERNAME:<31}║")
print("╚══════════════════════════════════════════╝")

while True:
    try:
        _session.post(f"{URL}/deleteWebhook", json={"drop_pending_updates": False}, timeout=10)
        _me = _session.get(f"{URL}/getMe", timeout=10).json()
        if _me.get("ok"):
            print(f"✅ يعمل الآن | @{_me['result'].get('username','?')}")
            break
    except Exception: pass
    time.sleep(3)

while True:
  try:
    resp=_session.get(f"{URL}/getUpdates",params={"timeout":25,"offset":offset},timeout=35).json()
    updates=resp.get("result",[])
    for u in updates:
        offset=u["update_id"]+1
        if "pre_checkout_query" in u:
            answer_pq(u["pre_checkout_query"]["id"],True); continue

        if "message" in u:
            msg=u["message"]; chat_id=msg["chat"]["id"]
            uid=msg["from"]["id"]; text=msg.get("text","")
            uname=msg["from"].get("first_name","") or msg["from"].get("username","") or "مستخدم"
            mid=msg["message_id"]; touch(uid); set_ctx(uid)

            if "successful_payment" in msg:
                stars=msg["successful_payment"]["total_amount"]
                spd=get_stars_per_dollar(); cents=int(stars*100/spd)
                txn=gen_txn(); add_bal(uid,cents,txn=txn,op="stars_recharge")
                send(uid, f"✅ <b>تم الشحن بنجاح!</b>\n⭐ النجوم: <b>{stars}</b>\n💵 المضاف: <b>{fmt(cents)}</b>\n💰 رصيدك: <b>{fmt(get_bal(uid))}</b>", back())
                continue

            if is_maintenance() and not is_owner(uid):
                send(chat_id,"🔧 <b>البوت في وضع الصيانة</b>"); continue

            if text.startswith("/start"):
                parts=text.split(); ref_id=None
                if len(parts)>1 and parts[1].startswith("ref_"):
                    try: ref_id=int(parts[1][4:])
                    except: pass
                ensure(uid)
                if not is_owner(uid) and not is_verified(uid):
                    start_captcha(chat_id,uid); continue
                not_sub=check_sub(uid)
                if not_sub: send(chat_id,"🔔 <b>يجب الاشتراك أولاً:</b>",sub_kb(not_sub)); continue
                bal=get_bal(uid)
                wtxt=get_welcome_text(uid,uname,bal)
                send(chat_id,wtxt,main_kb(uid)); continue

            st=states.get(uid,{}); step=st.get("step","")

            # ─── شحن آسيا سيل تلقائي ODP (Playwright Sync API) ───
            if step == "asiacell_wait_phone":
                phone_input = text.strip()
                if not re.search(r'^(?:\+?964|0)?7[78]\d{8}$', phone_input):
                    send(chat_id, "❌ <b>رقم غير صالح!</b>\nيرجى إدخال رقم آسيا سيل صحيح (مثال: <code>07712345678</code>):", cancel())
                    continue

                if phone_input.startswith("+964"):
                    clean_phone = "0" + phone_input[4:]
                elif phone_input.startswith("964"):
                    clean_phone = "0" + phone_input[3:]
                elif not phone_input.startswith("0"):
                    clean_phone = "0" + phone_input
                else:
                    clean_phone = phone_input

                st["ac_phone"] = clean_phone
                st["step"] = "asiacell_processing"
                states[uid] = st

                send(chat_id, "⏳ <i>جاري فتح موقع آسياسيل وجلب صورة التحقق (الكابتشا)...</i>", cancel())

                def _run_ac_step1(cid=chat_id, u_id=uid, ph=clean_phone):
                    ok, res = ac_step1_login_and_captcha(cid, u_id, ph)
                    if ok:
                        st_now = states.get(u_id, {})
                        st_now["step"] = "asiacell_wait_captcha"
                        states[u_id] = st_now
                        send_photo(cid, res, caption="🔢 <b>أرسل الرمز الظاهر في صورة الكابتشا أعلاه:</b>", kb=cancel())
                    else:
                        clr(u_id)
                        send(cid, f"❌ <b>تعذر الاتصال بموقع آسياسيل:</b>\n<code>{res}</code>", back())

                threading.Thread(target=_run_ac_step1, daemon=True).start()
                continue

            if step == "asiacell_wait_captcha":
                captcha_text = text.strip()
                st["step"] = "asiacell_processing"
                states[uid] = st

                send(chat_id, "⏳ <i>جاري التحقق من الكابتشا وإرسال كود الـ SMS...</i>", cancel())

                def _run_ac_step2(cid=chat_id, u_id=uid, cap=captcha_text):
                    ok, res = ac_step2_verify_captcha(cid, u_id, cap)
                    if ok == "retry_captcha":
                        st_now = states.get(u_id, {})
                        st_now["step"] = "asiacell_wait_captcha"
                        states[u_id] = st_now
                        if res:
                            send_photo(cid, res, caption="❌ <b>رمز الكابتشا خاطئ!</b>\nأرسل الرمز الظاهر في الصورة الجديدة:", kb=cancel())
                        else:
                            send(cid, "❌ <b>رمز الكابتشا خاطئ!</b> يرجى المحاولة مرة أخرى:", cancel())
                    elif ok:
                        st_now = states.get(u_id, {})
                        st_now["step"] = "asiacell_wait_code"
                        states[u_id] = st_now
                        send(cid,
                             f"✅ <b>تم إرسال كود التحقق (SMS) إلى هاتفك!</b>\n\n"
                             f"📩 <b>أرسل رمز الـ SMS لإتمام عملية الشحن:</b>", cancel())
                    else:
                        clr(u_id)
                        send(cid, f"❌ <b>خطأ أثناء التحقق:</b>\n<code>{res}</code>", back())

                threading.Thread(target=_run_ac_step2, daemon=True).start()
                continue

            if step == "asiacell_wait_code":
                otp_code = text.strip()
                if len(otp_code) < 4:
                    send(chat_id, "❌ الرمز قصير جداً، يرجى إرسال الرمز الصحيح:", cancel())
                    continue

                phone_num = st.get("ac_phone", "")
                selected_amount = st.get("ac_amount", 1000)
                st["step"] = "asiacell_processing"
                states[uid] = st

                send(chat_id, "⏳ <i>جاري تسجيل الدخول وتنفيذ تحويل الرصيد تلقائياً...</i>", cancel())

                def _run_ac_step3(cid=chat_id, u_id=uid, otp=otp_code, amt=selected_amount, ph=phone_num):
                    ok, res = ac_step3_submit_otp_and_transfer(cid, u_id, otp, amt)
                    if ok:
                        cents_to_add = int((amt / 1500) * 100)
                        add_bal(u_id, cents_to_add, op="asiacell_auto_recharge")
                        clr(u_id)
                        send(cid,
                             f"✅ <b>تم شحن رصيدك بنجاح عبر آسيا سيل!</b>\n"
                             f"📞 الرقم: <code>{ph}</code>\n"
                             f"💵 الفئة: <b>{amt:,} دينار عراقي</b>\n"
                             f"💰 رصيدك الحالي: <b>{fmt(get_bal(u_id))}</b>",
                             back())
                    else:
                        clr(u_id)
                        send(cid, f"❌ <b>فشلت عملية التحويل:</b>\n<code>{res}</code>", back())

                threading.Thread(target=_run_ac_step3, daemon=True).start()
                continue

            # الخطوات الأخرى للبوت الأصلي...
            if step=="add_num_number":
                st["number"]=text.strip(); st["step"]="add_num_country"
                states[uid]=st
                ask_num_country(chat_id,uid,st)
                continue

        elif "callback_query" in u:
            cq=u["callback_query"]; chat_id=cq["message"]["chat"]["id"]
            mid=cq["message"]["message_id"]; uid=cq["from"]["id"]; set_ctx(uid)
            uname=cq["from"].get("first_name","") or cq["from"].get("username","") or "مستخدم"
            data=cq["data"]; cb_id=cq["id"]; touch(uid)

            if data.startswith("cap_"):
                chosen=data[4:]; session=captcha_sessions.get(uid)
                if not session: answer(cb_id,"❌ انتهت الصلاحية",True); continue
                if chosen==session["code"]:
                    set_verified(uid); del captcha_sessions[uid]
                    answer(cb_id,"✅ تم التحقق بنجاح! 🎉"); delete_msg(chat_id,mid)
                    bal=get_bal(uid)
                    send(chat_id,get_welcome_text(uid,uname,bal),main_kb(uid))
                else:
                    session["attempts"]=session.get("attempts",0)+1
                    if session["attempts"]>=3:
                        del captcha_sessions[uid]
                        answer(cb_id,"❌ تجاوزت المحاولات",True)
                    else:
                        answer(cb_id,f"❌ خاطئ! المحاولات المتبقية: {3-session['attempts']}",True)
                continue

            answer(cb_id)

            if data=="main_menu":
                clr(uid)
                ac_cleanup(uid)
                bal=get_bal(uid)
                edit(chat_id,mid,get_welcome_text(uid,uname,bal),main_kb(uid))

            elif data=="balance_show":
                edit(chat_id,mid,f"💵 <b>رصيدك الحالي</b>\n\n<b>{fmt(get_bal(uid))}</b>",back())

            elif data=="buy":
                show_countries(chat_id,mid)

            elif data=="recharge":
                show_recharge(chat_id,mid)

            elif data=="recharge_asiacell_start":
                show_asiacell_amounts(chat_id, mid)

            elif data.startswith("ac_amt_"):
                amount_iqd = int(data[7:])
                st2 = states.get(uid, {})
                st2["ac_amount"] = amount_iqd
                st2["step"] = "asiacell_wait_phone"
                states[uid] = st2
                
                edit(chat_id, mid,
                    f"💳 <b>شحن رصيد تلقائي (آسيا سيل)</b>\n"
                    f"💵 الفئة المختارة: <b>{amount_iqd:,} دينار عراقي</b>\n\n"
                    f"📱 <b>يرجى إرسال رقم هاتف آسيا سيل الخاص بك:</b>\n"
                    f"<i>مثال: <code>07712345678</code></i>", cancel())

            elif data=="recharge_stars":
                show_stars_menu(chat_id,mid)

            elif data=="admin_panel":
                if is_admin(uid): edit(chat_id,mid,"⚙️ <b>لوحة الإدارة</b>",admin_kb(uid))

            elif data=="owner_panel":
                if is_owner(uid): edit(chat_id,mid,"👑 <b>لوحة المطور</b>",owner_kb())

            elif data=="owner_emoji_mgr":
                if is_owner(uid): show_emoji_manager(chat_id,mid)

            elif data=="owner_accounts":
                if is_owner(uid): show_accounts_panel(chat_id,mid)

  except requests.exceptions.Timeout:
      pass
  except Exception as e:
      print(f"[ERROR] {e}")
      time.sleep(1)
