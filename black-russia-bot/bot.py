import logging
import random
import sqlite3
import time
import datetime
import asyncio
import flask
import threading
import hashlib
import secrets
import re
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters, 
    ContextTypes
)

# === КОНФИГУРАЦИЯ ===
BOT_TOKEN = "ВАШ_ТОКЕН_ЗДЕСЬ"
DATABASE_NAME = "black_russia_bot.db"

# === WEB SERVER FOR UPTIMEROBOT ===
app = flask.Flask(__name__)
start_time = datetime.datetime.now()

@app.route('/')
def home():
    return "🤖 Black Russia Bot is RUNNING!"

@app.route('/health')
def health():
    return {"status": "ok", "bot": "Black Russia"}, 200

def run_web_server():
    app.run(host='0.0.0.0', port=8080, debug=False)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Списки серверов (ВСЕ сервера)
SERVERS = [
    "№1 | Red", "№2 | Green", "№3 | Blue", "№4 | Yellow", "№5 | Orange", 
    "№6 | Purple", "№7 | Lime", "№8 | Pink", "№9 | Cherry", "№10 | Black",
    "№11 | Indigo", "№12 | White", "№13 | Magenta", "№14 | Crimson", "№15 | Gold",
    "№16 | Azure", "№17 | Platinum", "№18 | Aqua", "№19 | Gray", "№20 | Ice",
    "№21 | Chilli", "№22 | Choco", "№23 | Moscow", "№24 | SPB", "№25 | UFA",
    "№26 | SOCHI", "№27 | KAZAN", "№28 | SAMARA", "№29 | ROSTOV", "№30 | ANAPA",
    "№31 | EKB", "№32 | Krasnodar", "№33 | ARZAMAZ", "№34 | NOVOSIB", "№35 | GROZNY",
    "№36 | SARATOV", "№37 | OMSK", "№38 | IRKUTSK", "№39 | VOLGOGRAD", "№40 | VORONEZH",
    "№41 | BELGOROD", "№42 | MAKHACHKALA", "№43 | VLADIKAVKAZ", "№44 | VLADIVOSTOK", "№45 | KALININGRAD",
    "№46 | CHELYABINSK", "№47 | KRASNOYARSK", "№48 | KHEBOKSARY", "№49 | KHABAROVSK", "№50 | PERM",
    "№51 | TULA", "№52 | RYAZAN", "№53 | MURMANSK", "№54 | PENZA", "№55 | KURSK",
    "№56 | ARCHANGELSK", "№57 | ORENBURG", "№58 | KIROV", "№59 | KEMEROVO", "№60 | TYUMEN",
    "№61 | TOLYATI", "№62 | IVANOVO", "№63 | STAVROPOL", "№64 | SMOLENSK", "№65 | PSKOV",
    "№66 | BRYANSK", "№67 | OREL", "№68 | YAROSLAVL", "№69 | BARNAUL", "№70 | LIPETSK",
    "№71 | ULYANOVSK", "№72 | YAKUTSK", "№73 | TAMBOV", "№74 | BRATSK", "№75 | ASTRACHAN",
    "№76 | CHITA", "№77 | KOSTROMA", "№78 | VLADIMIR", "№79 | KALUGA", "№80 | NOVGOROD",
    "№81 | TAGANROG", "№88 | VOLOGA", "№89 | TVER", "№90 | TOMSK", "№91 | IZHEVSK",
    "№92 | SURGUT", "№93 | PODOLSK", "№94 | MAGADAN", "№95 | CHEREPOVETS"
]

# === СИСТЕМА КРАФТА И РЕСУРСОВ ===

# Ресурсы для крафта
RESOURCES = {
    "metal": {"name": "⚙️ Металл", "emoji": "⚙️", "rarity": "common"},
    "electronics": {"name": "🔌 Электроника", "emoji": "🔌", "rarity": "uncommon"},
    "engine": {"name": "🔧 Двигатель", "emoji": "🔧", "rarity": "rare"},
    "turbo": {"name": "💨 Турбина", "emoji": "💨", "rarity": "epic"},
    "carbon": {"name": "🖤 Карбон", "emoji": "🖤", "rarity": "legendary"},
    "diamond": {"name": "💎 Алмазы", "emoji": "💎", "rarity": "mythical"},
    "gold": {"name": "🥇 Золото", "emoji": "🥇", "rarity": "legendary"},
    "uranium": {"name": "☢️ Уран", "emoji": "☢️", "rarity": "mythical"},
    "ai_chip": {"name": "🤖 ИИ-чип", "emoji": "🤖", "rarity": "mythical"},
    "quantum_core": {"name": "⚛️ Квантовое ядро", "emoji": "⚛️", "rarity": "mythical"}
}

# Уникальные машины для крафта
CRAFTABLE_CARS = [
    {
        "name": "🚀 CyberRoadster", 
        "price": 0, 
        "craft_price": 50000000,
        "resources": {"metal": 50, "electronics": 30, "engine": 5, "carbon": 10},
        "rarity": "legendary",
        "sell_price": 25000000,
        "description": "Электрический гиперкар будущего"
    },
    {
        "name": "🐉 Dragon Wagon", 
        "price": 0, 
        "craft_price": 75000000,
        "resources": {"metal": 80, "electronics": 40, "turbo": 8, "gold": 5},
        "rarity": "legendary", 
        "sell_price": 37500000,
        "description": "Бронированный внедорожник с огнеметом"
    },
    {
        "name": "🌙 Lunar Rover", 
        "price": 0, 
        "craft_price": 100000000,
        "resources": {"metal": 100, "electronics": 60, "engine": 10, "diamond": 3},
        "rarity": "mythical",
        "sell_price": 50000000,
        "description": "Внедорожник для лунной поверхности"
    },
    {
        "name": "⚡ Thunder Bolt", 
        "price": 0, 
        "craft_price": 150000000,
        "resources": {"metal": 120, "electronics": 80, "turbo": 12, "uranium": 2},
        "rarity": "mythical",
        "sell_price": 75000000,
        "description": "Электромобиль с ядерным реактором"
    },
    {
        "name": "👑 Tsar Tank", 
        "price": 0, 
        "craft_price": 200000000,
        "resources": {"metal": 200, "electronics": 100, "engine": 15, "gold": 10, "diamond": 5},
        "rarity": "mythical",
        "sell_price": 100000000,
        "description": "Царь-танк современности"
    },
    {
        "name": "🤖 Autobot X", 
        "price": 0, 
        "craft_price": 300000000,
        "resources": {"metal": 150, "electronics": 120, "ai_chip": 1, "quantum_core": 1},
        "rarity": "mythical",
        "sell_price": 150000000,
        "description": "Трансформер с искусственным интеллектом"
    },
    {
        "name": "🌌 Nebula Cruiser", 
        "price": 0, 
        "craft_price": 500000000,
        "resources": {"metal": 300, "electronics": 200, "quantum_core": 2, "uranium": 5},
        "rarity": "mythical",
        "sell_price": 250000000,
        "description": "Межзвездный крейсер для городских улиц"
    },
    {
        "name": "💀 Phantom Rider", 
        "price": 0, 
        "craft_price": 80000000,
        "resources": {"metal": 60, "electronics": 45, "carbon": 15, "engine": 8},
        "rarity": "legendary",
        "sell_price": 40000000,
        "description": "Призрачный байк с невидимостью"
    },
    {
        "name": "🔥 Inferno GT", 
        "price": 0, 
        "craft_price": 120000000,
        "resources": {"metal": 90, "electronics": 70, "turbo": 10, "engine": 12},
        "rarity": "legendary",
        "sell_price": 60000000,
        "description": "Спорткар с плазменными двигателями"
    },
    {
        "name": "❄️ Frost Wolf", 
        "price": 0, 
        "craft_price": 90000000,
        "resources": {"metal": 70, "electronics": 50, "carbon": 12, "diamond": 2},
        "rarity": "legendary",
        "sell_price": 45000000,
        "description": "Внедорожник с криогенной системой"
    }
]

# Крафт оружия
CRAFTABLE_WEAPONS = [
    {
        "name": "🔫 Plasma Rifle", 
        "price": 0, 
        "craft_price": 20000000,
        "resources": {"metal": 20, "electronics": 15, "uranium": 1},
        "rarity": "legendary",
        "damage": 200,
        "sell_price": 10000000,
        "description": "Плазменная винтовка будущего"
    },
    {
        "name": "💣 Quantum Grenade", 
        "price": 0, 
        "craft_price": 15000000,
        "resources": {"metal": 15, "electronics": 10, "quantum_core": 1},
        "rarity": "mythical",
        "damage": 500,
        "sell_price": 7500000,
        "description": "Граната с квантовым взрывом"
    }
]

# Расширенные списки ников
RUSSIAN_NAMES = ["ivan", "alex", "maxim", "dmitry", "sergey", "andrey", "mikhail", "vladimir", "nikita", "artyom"]
RUSSIAN_SURNAMES = ["ivanov", "petrov", "sidorov", "smirnov", "popov", "volkov", "kozlov", "novikov", "morozov", "pavlov"]
RANDOM_NICKNAMES = [f"{name}_{surname}" for name in RUSSIAN_NAMES for surname in RUSSIAN_SURNAMES]

# Автономера (российский формат: буква-3 цифры-2 буквы-2-3 цифры)
CAR_NUMBER_LETTERS = "АВЕКМНОРСТУХ"
CAR_NUMBER_REGIONS = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99", "102", "113", "116", "121", "123", "124", "125", "134", "136", "138", "142", "147", "150", "152", "154", "159", "161", "163", "164", "173", "174", "177", "178", "186", "190", "196", "197", "199", "277", "299", "777", "799", "977"]

def generate_car_number():
    letter1 = random.choice(CAR_NUMBER_LETTERS)
    numbers1 = str(random.randint(0, 999)).zfill(3)
    letter2 = random.choice(CAR_NUMBER_LETTERS)
    letter3 = random.choice(CAR_NUMBER_LETTERS)
    region = random.choice(CAR_NUMBER_REGIONS)
    return f"{letter1}{numbers1}{letter2}{letter3}{region}"

# Расширенный список автономеров с ценами
CAR_NUMBERS = [
    {"number": "А001АА777", "price": 5000000, "rarity": "legendary"},
    {"number": "В777ВВ777", "price": 10000000, "rarity": "mythical"},
    {"number": "С123СС197", "price": 3000000, "rarity": "epic"},
    {"number": "Е666ЕК99", "price": 8000000, "rarity": "legendary"},
    {"number": "К999КХ77", "price": 12000000, "rarity": "mythical"},
    {"number": "М111МР116", "price": 2000000, "rarity": "rare"},
    {"number": "О555ОО750", "price": 4000000, "rarity": "epic"},
    {"number": "Р333РУ178", "price": 1500000, "rarity": "uncommon"},
    {"number": "Т777ТС190", "price": 6000000, "rarity": "legendary"},
    {"name": "🚗 Lada Vesta", "price": 2500000, "rarity": "common", "sell_price": 1250000},
    {"name": "🚗 Lada Granta", "price": 2000000, "rarity": "common", "sell_price": 1000000},
    {"name": "🚗 ВАЗ 2109", "price": 1500000, "rarity": "common", "sell_price": 750000},
    {"name": "🚗 Ford Focus", "price": 4500000, "rarity": "uncommon", "sell_price": 2250000},
    {"name": "🚗 Kia Rio", "price": 4250000, "rarity": "uncommon", "sell_price": 2125000},
    {"name": "🏎 Ford Mustang", "price": 7500000, "rarity": "rare", "sell_price": 3750000},
    {"name": "🏎 Chevrolet Camaro", "price": 7000000, "rarity": "rare", "sell_price": 3500000},
    {"name": "🏎 BMW M5", "price": 12500000, "rarity": "epic", "sell_price": 6250000},
    {"name": "🏎 Mercedes S63", "price": 11000000, "rarity": "epic", "sell_price": 5500000},
    {"name": "🚀 Lamborghini Huracan", "price": 25000000, "rarity": "legendary", "sell_price": 12500000},
    {"name": "🚀 Bugatti Chiron", "price": 40000000, "rarity": "mythical", "sell_price": 20000000},
    {"name": "🚗 Lada Niva", "price": 1750000, "rarity": "common", "sell_price": 875000},
    {"name": "🚗 Volkswagen Polo", "price": 4750000, "rarity": "uncommon", "sell_price": 2375000},
    {"name": "🚗 Hyundai Solaris", "price": 4400000, "rarity": "uncommon", "sell_price": 2200000},
    {"name": "🏎 Nissan GT-R", "price": 22500000, "rarity": "epic", "sell_price": 11250000},
    {"name": "🏎 Porsche 911", "price": 19000000, "rarity": "epic", "sell_price": 9500000},
    {"name": "🚀 Ferrari F8", "price": 32500000, "rarity": "legendary", "sell_price": 16250000},
    {"name": "🚀 McLaren P1", "price": 37500000, "rarity": "legendary", "sell_price": 18750000},
    {"name": "🚁 Helicopter", "price": 75000000, "rarity": "mythical", "sell_price": 37500000},
    {"name": "✈️ Private Jet", "price": 250000000, "rarity": "mythical", "sell_price": 125000000},
    {"name": "🚓 Police Car", "price": 6000000, "rarity": "rare", "sell_price": 3000000},
    {"name": "🚐 Minivan", "price": 3500000, "rarity": "common", "sell_price": 1750000},
    {"name": "🚚 Truck", "price": 10000000, "rarity": "uncommon", "sell_price": 5000000},
    {"name": "🏍 Motorcycle", "price": 3000000, "rarity": "common", "sell_price": 1500000},
    {"name": "🚜 Tractor", "price": 4000000, "rarity": "common", "sell_price": 2000000},
    {"name": "🚛 Big Truck", "price": 17500000, "rarity": "rare", "sell_price": 8750000},
    {"name": "🚎 Bus", "price": 14000000, "rarity": "uncommon", "sell_price": 7000000},
    {"name": "🚑 Ambulance", "price": 9000000, "rarity": "rare", "sell_price": 4500000},
    {"name": "🚒 Fire Truck", "price": 11000000, "rarity": "rare", "sell_price": 5500000},
    {"name": "🏎 Formula 1", "price": 60000000, "rarity": "legendary", "sell_price": 30000000},
    {"name": "🚙 Range Rover", "price": 15000000, "rarity": "epic", "sell_price": 7500000},
    {"name": "🚙 Lexus LX", "price": 18000000, "rarity": "epic", "sell_price": 9000000},
    {"name": "🏎 Audi R8", "price": 22000000, "rarity": "legendary", "sell_price": 11000000},
    {"name": "🚙 Toyota Camry", "price": 5000000, "rarity": "uncommon", "sell_price": 2500000},
    {"name": "🚙 Honda Civic", "price": 4500000, "rarity": "uncommon", "sell_price": 2250000},
    {"name": "🏎 Tesla Model S", "price": 12000000, "rarity": "epic", "sell_price": 6000000},
    {"name": "🏎 Tesla Cybertruck", "price": 20000000, "rarity": "legendary", "sell_price": 10000000},
    {"name": "🚙 Bentley Continental", "price": 35000000, "rarity": "legendary", "sell_price": 17500000},
    {"name": "🚙 Rolls Royce Phantom", "price": 45000000, "rarity": "mythical", "sell_price": 22500000},
    {"name": "🏎 Aston Martin DB11", "price": 28000000, "rarity": "legendary", "sell_price": 14000000},
    {"name": "🚙 Jaguar F-Pace", "price": 16000000, "rarity": "epic", "sell_price": 8000000},
    {"name": "🏎 Maserati GranTurismo", "price": 24000000, "rarity": "legendary", "sell_price": 12000000}
]

# Расширенная система фарма - типы работ
FARM_JOBS = [
    {"name": "🚗 Таксист", "min_reward": 10000, "max_reward": 50000, "cooldown": 300, "risk": 0.1, "exp": 50},
    {"name": "🏢 Курьер", "min_reward": 15000, "max_reward": 75000, "cooldown": 400, "risk": 0.15, "exp": 75},
    {"name": "🛒 Продавец", "min_reward": 20000, "max_reward": 100000, "cooldown": 500, "risk": 0.2, "exp": 100},
    {"name": "💼 Офисный работник", "min_reward": 30000, "max_reward": 150000, "cooldown": 600, "risk": 0.05, "exp": 150},
    {"name": "🚚 Дальнобойщик", "min_reward": 50000, "max_reward": 250000, "cooldown": 800, "risk": 0.25, "exp": 250},
    {"name": "👮‍♂️ Охранник", "min_reward": 40000, "max_reward": 200000, "cooldown": 700, "risk": 0.3, "exp": 200},
    {"name": "🍕 Доставка еды", "min_reward": 25000, "max_reward": 125000, "cooldown": 450, "risk": 0.12, "exp": 125},
    {"name": "🔧 Автомеханик", "min_reward": 35000, "max_reward": 175000, "cooldown": 550, "risk": 0.18, "exp": 175},
    {"name": "🏗 Строитель", "min_reward": 45000, "max_reward": 225000, "cooldown": 650, "risk": 0.22, "exp": 225},
    {"name": "💻 IT специалист", "min_reward": 60000, "max_reward": 300000, "cooldown": 900, "risk": 0.08, "exp": 300},
    {"name": "👨‍⚕️ Врач", "min_reward": 70000, "max_reward": 350000, "cooldown": 950, "risk": 0.05, "exp": 350},
    {"name": "👨‍🏫 Учитель", "min_reward": 40000, "max_reward": 200000, "cooldown": 600, "risk": 0.03, "exp": 200},
    {"name": "👨‍💼 Банкир", "min_reward": 80000, "max_reward": 400000, "cooldown": 1000, "risk": 0.1, "exp": 400},
    {"name": "👨‍✈️ Пилот", "min_reward": 100000, "max_reward": 500000, "cooldown": 1200, "risk": 0.15, "exp": 500},
    {"name": "🕵️‍♂️ Детектив", "min_reward": 90000, "max_reward": 450000, "cooldown": 1100, "risk": 0.2, "exp": 450},
    {"name": "👨‍🔬 Ученый", "min_reward": 85000, "max_reward": 425000, "cooldown": 1050, "risk": 0.07, "exp": 425},
    {"name": "🎬 Актер", "min_reward": 75000, "max_reward": 375000, "cooldown": 950, "risk": 0.25, "exp": 375},
    {"name": "👨‍🍳 Шеф-повар", "min_reward": 65000, "max_reward": 325000, "cooldown": 850, "risk": 0.12, "exp": 325},
    {"name": "🎨 Художник", "min_reward": 55000, "max_reward": 275000, "cooldown": 750, "risk": 0.3, "exp": 275},
    {"name": "📹 Блогер", "min_reward": 95000, "max_reward": 475000, "cooldown": 1150, "risk": 0.35, "exp": 475}
]

# Специальные события фарма
FARM_EVENTS = [
    {"name": "🎯 Бонус за эффективность", "multiplier": 2.0, "chance": 0.1},
    {"name": "💸 Нашел деньги на улице", "bonus": 50000, "chance": 0.15},
    {"name": "🎁 Дополнительный заказ", "multiplier": 1.5, "chance": 0.2},
    {"name": "👑 VIP клиент", "multiplier": 3.0, "chance": 0.05},
    {"name": "⚡ Сверхскорость", "multiplier": 1.8, "chance": 0.12},
    {"name": "🔧 Поломка оборудования", "multiplier": 0.5, "chance": 0.08},
    {"name": "🚓 Пробки на дорогах", "multiplier": 0.7, "chance": 0.1},
    {"name": "🌧️ Плохая погода", "multiplier": 0.8, "chance": 0.09},
    {"name": "💰 Премия от начальства", "bonus": 100000, "chance": 0.07},
    {"name": "🎊 Перевыполнение плана", "multiplier": 2.5, "chance": 0.06}
]

# Номера телефонов (от 1 до 100000)
def generate_phone_number():
    return str(random.randint(1, 100000)).zfill(6)

# Система семей как в Black Russia
FAMILY_RANKS = {
    1: {"name": "🔰 Новичок", "max_members": 5, "bonus": 0.05, "upgrade_cost": 0},
    2: {"name": "🥉 Бронза", "max_members": 10, "bonus": 0.10, "upgrade_cost": 10000000},
    3: {"name": "🥈 Серебро", "max_members": 20, "bonus": 0.15, "upgrade_cost": 25000000},
    4: {"name": "🥇 Золото", "max_members": 30, "bonus": 0.20, "upgrade_cost": 50000000},
    5: {"name": "💎 Платина", "max_members": 50, "bonus": 0.25, "upgrade_cost": 100000000},
    6: {"name": "👑 Легенда", "max_members": 100, "bonus": 0.30, "upgrade_cost": 250000000}
}

FAMILY_ROLES = {
    "owner": {"name": "👑 Владелец", "permissions": ["all"]},
    "co_owner": {"name": "⭐ Заместитель", "permissions": ["invite", "kick", "manage_members"]},
    "officer": {"name": "🔰 Офицер", "permissions": ["invite", "kick"]},
    "member": {"name": "👤 Участник", "permissions": []}
}

# Расширенный список домов из Black Russia
HOUSES = [
    {"name": "🏠 Квартира в хрущевке", "price": 5000000, "rarity": "common", "sell_price": 2500000},
    {"name": "🏠 Квартира в панельке", "price": 12500000, "rarity": "common", "sell_price": 6250000},
    {"name": "🏠 Таунхаус", "price": 25000000, "rarity": "uncommon", "sell_price": 12500000},
    {"name": "🏡 Загородный дом", "price": 50000000, "rarity": "rare", "sell_price": 25000000},
    {"name": "🏰 Вилла", "price": 125000000, "rarity": "epic", "sell_price": 62500000},
    {"name": "🏯 Особняк", "price": 250000000, "rarity": "legendary", "sell_price": 125000000},
    {"name": "🏤 Резиденция", "price": 500000000, "rarity": "mythical", "sell_price": 250000000},
    {"name": "🏢 Пентхаус", "price": 75000000, "rarity": "epic", "sell_price": 37500000},
    {"name": "🏛 Дворец", "price": 1000000000, "rarity": "mythical", "sell_price": 500000000},
    {"name": "🏬 Бизнес-центр", "price": 1500000000, "rarity": "mythical", "sell_price": 750000000},
    {"name": "🏘 Коттедж", "price": 40000000, "rarity": "uncommon", "sell_price": 20000000},
    {"name": "🏚 Дача", "price": 15000000, "rarity": "common", "sell_price": 7500000},
    {"name": "🏣 Офисное здание", "price": 200000000, "rarity": "legendary", "sell_price": 100000000},
    {"name": "🏪 Магазин", "price": 30000000, "rarity": "uncommon", "sell_price": 15000000},
    {"name": "🏨 Гостиница", "price": 175000000, "rarity": "legendary", "sell_price": 87500000},
    {"name": "🏢 Небоскреб", "price": 2000000000, "rarity": "mythical", "sell_price": 1000000000},
    {"name": "🏰 Замок", "price": 750000000, "rarity": "mythical", "sell_price": 375000000},
    {"name": "🏡 Фазенда", "price": 60000000, "rarity": "rare", "sell_price": 30000000},
    {"name": "🏠 Студия", "price": 8000000, "rarity": "common", "sell_price": 4000000},
    {"name": "🏡 Усадьба", "price": 300000000, "rarity": "legendary", "sell_price": 150000000}
]

# Расширенный список оружия из Black Russia
WEAPONS = [
    {"name": "🔪 Нож", "price": 250000, "rarity": "common", "damage": 10, "sell_price": 125000},
    {"name": "🏏 Бейсбольная бита", "price": 400000, "rarity": "common", "damage": 15, "sell_price": 200000},
    {"name": "🔫 Пистолет ПМ", "price": 750000, "rarity": "common", "damage": 25, "sell_price": 375000},
    {"name": "🔫 Glock-17", "price": 1000000, "rarity": "uncommon", "damage": 30, "sell_price": 500000},
    {"name": "🔫 AK-47", "price": 2500000, "rarity": "rare", "damage": 50, "sell_price": 1250000},
    {"name": "🔫 M4A1", "price": 3000000, "rarity": "rare", "damage": 55, "sell_price": 1500000},
    {"name": "🔫 AWP", "price": 4000000, "rarity": "epic", "damage": 80, "sell_price": 2000000},
    {"name": "💣 РПГ-7", "price": 7500000, "rarity": "legendary", "damage": 150, "sell_price": 3750000},
    {"name": "🔫 Золотой AK-47", "price": 10000000, "rarity": "legendary", "damage": 100, "sell_price": 5000000},
    {"name": "🔫 Desert Eagle", "price": 1750000, "rarity": "uncommon", "damage": 40, "sell_price": 875000},
    {"name": "🔫 MP5", "price": 2250000, "rarity": "rare", "damage": 45, "sell_price": 1125000},
    {"name": "🔫 Sniper Rifle", "price": 6000000, "rarity": "epic", "damage": 90, "sell_price": 3000000},
    {"name": "💣 Гранатомет", "price": 12500000, "rarity": "legendary", "damage": 200, "sell_price": 6250000},
    {"name": "🔫 Плазменная пушка", "price": 25000000, "rarity": "mythical", "damage": 300, "sell_price": 12500000},
    {"name": "🔫 UZI", "price": 2000000, "rarity": "rare", "damage": 35, "sell_price": 1000000},
    {"name": "🔫 Thompson", "price": 2800000, "rarity": "rare", "damage": 48, "sell_price": 1400000},
    {"name": "💣 Мины", "price": 3500000, "rarity": "epic", "damage": 120, "sell_price": 1750000},
    {"name": "🔫 Дробовик", "price": 3200000, "rarity": "epic", "damage": 70, "sell_price": 1600000},
    {"name": "🔫 Лазерная винтовка", "price": 30000000, "rarity": "mythical", "damage": 350, "sell_price": 15000000},
    {"name": "🛡 Щит", "price": 1500000, "rarity": "uncommon", "damage": 5, "sell_price": 750000}
]

# Расширенный список бизнесов из Black Russia
BUSINESSES = [
    {"name": "🏪 Магазин продуктов", "price": 10000000, "income": 250000, "supply_cost": 500000, "rarity": "common", "sell_price": 5000000},
    {"name": "⛽ Автозаправка", "price": 25000000, "income": 600000, "supply_cost": 1250000, "rarity": "uncommon", "sell_price": 12500000},
    {"name": "🎮 Игровой клуб", "price": 40000000, "income": 1000000, "supply_cost": 2000000, "rarity": "rare", "sell_price": 20000000},
    {"name": "💎 Ювелирный магазин", "price": 75000000, "income": 1750000, "supply_cost": 3500000, "rarity": "epic", "sell_price": 37500000},
    {"name": "🏢 Отель", "price": 125000000, "income": 3000000, "supply_cost": 6000000, "rarity": "legendary", "sell_price": 62500000},
    {"name": "🛳 Судоходная компания", "price": 250000000, "income": 6000000, "supply_cost": 12000000, "rarity": "mythical", "sell_price": 125000000},
    {"name": "🍕 Пиццерия", "price": 15000000, "income": 400000, "supply_cost": 750000, "rarity": "common", "sell_price": 7500000},
    {"name": "🏭 Завод", "price": 200000000, "income": 5000000, "supply_cost": 10000000, "rarity": "legendary", "sell_price": 100000000},
    {"name": "🎲 Казино", "price": 300000000, "income": 7500000, "supply_cost": 15000000, "rarity": "mythical", "sell_price": 150000000},
    {"name": "💻 IT компания", "price": 175000000, "income": 4500000, "supply_cost": 9000000, "rarity": "legendary", "sell_price": 87500000},
    {"name": "🏥 Больница", "price": 150000000, "income": 3500000, "supply_cost": 7000000, "rarity": "legendary", "sell_price": 75000000},
    {"name": "🏦 Банк", "price": 500000000, "income": 10000000, "supply_cost": 20000000, "rarity": "mythical", "sell_price": 250000000},
    {"name": "🎭 Кинотеатр", "price": 80000000, "income": 1800000, "supply_cost": 3600000, "rarity": "epic", "sell_price": 40000000},
    {"name": "🏟 Стадион", "price": 350000000, "income": 8000000, "supply_cost": 16000000, "rarity": "mythical", "sell_price": 175000000},
    {"name": "🚗 Автосалон", "price": 120000000, "income": 2800000, "supply_cost": 5600000, "rarity": "legendary", "sell_price": 60000000}
]

# Сим-карты с номерами от 1 до 100000
def generate_sim_cards(count=50):
    sim_cards = []
    for _ in range(count):
        number = generate_phone_number()
        price = random.randint(500000, 5000000)
        rarity = random.choice(["common", "uncommon", "rare", "epic", "legendary", "mythical"])
        sim_cards.append({"number": number, "price": price, "rarity": rarity})
    return sim_cards

SIM_CARDS = generate_sim_cards(50)

# Расширенные скины и аксессуары из Black Russia
SKINS_AND_ACCESSORIES = [
    # Маски
    {"name": "🎭 Маска Anonymous", "price": 500000, "type": "mask", "rarity": "common"},
    {"name": "🎭 Маска Guy Fawkes", "price": 750000, "type": "mask", "rarity": "uncommon"},
    {"name": "🎭 Золотая маска", "price": 2000000, "type": "mask", "rarity": "rare"},
    {"name": "🎭 Маска Джокера", "price": 1500000, "type": "mask", "rarity": "rare"},
    {"name": "🎭 Маска Джейсона", "price": 1200000, "type": "mask", "rarity": "uncommon"},
    {"name": "🎭 Маска Скайрима", "price": 3000000, "type": "mask", "rarity": "epic"},
    {"name": "🎭 Маска Бэтмена", "price": 5000000, "type": "mask", "rarity": "legendary"},
    {"name": "🎭 Маска Железного человека", "price": 8000000, "type": "mask", "rarity": "mythical"},
    
    # Одежда
    {"name": "👕 Футболка Basic", "price": 250000, "type": "clothes", "rarity": "common"},
    {"name": "👕 Футболка Premium", "price": 500000, "type": "clothes", "rarity": "uncommon"},
    {"name": "👔 Костюм бизнесмена", "price": 1500000, "type": "clothes", "rarity": "rare"},
    {"name": "🥋 Костюм ниндзя", "price": 2000000, "type": "clothes", "rarity": "epic"},
    {"name": "👗 Вечернее платье", "price": 1800000, "type": "clothes", "rarity": "rare"},
    {"name": "🧥 Кожаная куртка", "price": 1200000, "type": "clothes", "rarity": "uncommon"},
    {"name": "🥼 Лабораторный халат", "price": 800000, "type": "clothes", "rarity": "common"},
    {"name": "👘 Кимоно", "price": 2200000, "type": "clothes", "rarity": "epic"},
    {"name": "🦺 Тактический жилет", "price": 2500000, "type": "clothes", "rarity": "rare"},
    {"name": "👑 Королевская мантия", "price": 10000000, "type": "clothes", "rarity": "mythical"},
    
    # Аксессуары
    {"name": "🕶 Солнечные очки", "price": 300000, "type": "accessory", "rarity": "common"},
    {"name": "⌚ Часы Rolex", "price": 1000000, "type": "accessory", "rarity": "uncommon"},
    {"name": "💍 Золотое кольцо", "price": 750000, "type": "accessory", "rarity": "rare"},
    {"name": "⛓ Цепь золотая", "price": 1250000, "type": "accessory", "rarity": "epic"},
    {"name": "🎒 Рюкзак тактический", "price": 800000, "type": "accessory", "rarity": "uncommon"},
    {"name": "💼 Кожаный портфель", "price": 600000, "type": "accessory", "rarity": "common"},
    {"name": "🧳 Чемодан VIP", "price": 1500000, "type": "accessory", "rarity": "rare"},
    {"name": "📿 Четки", "price": 400000, "type": "accessory", "rarity": "common"},
    {"name": "🔑 Ключи от города", "price": 5000000, "type": "accessory", "rarity": "legendary"},
    {"name": "💎 Бриллиантовый кулон", "price": 3000000, "type": "accessory", "rarity": "epic"},
    
    # Головные уборы
    {"name": "🎩 Цилиндр", "price": 600000, "type": "hat", "rarity": "rare"},
    {"name": "🧢 Бейсболка", "price": 200000, "type": "hat", "rarity": "common"},
    {"name": "👒 Шляпа ковбоя", "price": 450000, "type": "hat", "rarity": "uncommon"},
    {"name": "⛑ Каска строителя", "price": 350000, "type": "hat", "rarity": "common"},
    {"name": "🎓 Выпускная шапочка", "price": 700000, "type": "hat", "rarity": "uncommon"},
    {"name": "👑 Корона", "price": 8000000, "type": "hat", "rarity": "mythical"},
    {"name": "🪖 Армейский шлем", "price": 1200000, "type": "hat", "rarity": "rare"},
    
    # Обувь
    {"name": "👟 Кроссовки Nike", "price": 400000, "type": "shoes", "rarity": "uncommon"},
    {"name": "👞 Туфли кожаные", "price": 350000, "type": "shoes", "rarity": "common"},
    {"name": "🥾 Ботинки тактические", "price": 800000, "type": "shoes", "rarity": "uncommon"},
    {"name": "👢 Сапоги ковбойские", "price": 600000, "type": "shoes", "rarity": "rare"},
    {"name": "🩴 Сланцы пляжные", "price": 150000, "type": "shoes", "rarity": "common"},
    {"name": "👠 Туфли на каблуках", "price": 550000, "type": "shoes", "rarity": "uncommon"},
    
    # Специальные скины
    {"name": "🎨 Скин 'Неон'", "price": 2500000, "type": "special", "rarity": "epic"},
    {"name": "🌈 Скин 'Радуга'", "price": 3000000, "type": "special", "rarity": "epic"},
    {"name": "💀 Скин 'Хэллоуин'", "price": 1800000, "type": "special", "rarity": "rare"},
    {"name": "🎄 Скин 'Новый Год'", "price": 2000000, "type": "special", "rarity": "rare"},
    {"name": "⭐ Скин 'Звездная ночь'", "price": 5000000, "type": "special", "rarity": "legendary"},
    {"name": "🔥 Скин 'Огненный'", "price": 4500000, "type": "special", "rarity": "legendary"},
    {"name": "💧 Скин 'Ледяной'", "price": 4500000, "type": "special", "rarity": "legendary"},
    {"name": "⚡ Скин 'Электрический'", "price": 4800000, "type": "special", "rarity": "legendary"},
    {"name": "🌌 Скин 'Космический'", "price": 7500000, "type": "special", "rarity": "mythical"},
    {"name": "👑 Скин 'Королевский'", "price": 10000000, "type": "special", "rarity": "mythical"}
]

# === СИСТЕМА BLACK PASS ===
BLACK_PASS_QUESTS = [
    {
        "id": 1,
        "name": "🚀 Начало пути",
        "description": "Заработайте 1,000,000 ₽",
        "requirement": {"type": "money", "amount": 1000000},
        "reward": {"money": 500000, "exp": 1000, "items": ["⚙️ Металл"]}
    },
    {
        "id": 2,
        "name": "🏠 Первый дом",
        "description": "Купите первую недвижимость",
        "requirement": {"type": "house", "amount": 1},
        "reward": {"money": 1000000, "exp": 2000, "items": ["🔌 Электроника"]}
    },
    {
        "id": 3,
        "name": "🚗 Автолюбитель",
        "description": "Купите 3 автомобиля",
        "requirement": {"type": "cars", "amount": 3},
        "reward": {"money": 2000000, "exp": 3000, "items": ["🔧 Двигатель"]}
    },
    {
        "id": 4,
        "name": "💼 Бизнесмен",
        "description": "Приобретите бизнес",
        "requirement": {"type": "business", "amount": 1},
        "reward": {"money": 3000000, "exp": 4000, "items": ["💨 Турбина"]}
    },
    {
        "id": 5,
        "name": "👥 Командный игрок",
        "description": "Вступите в семью",
        "requirement": {"type": "family", "amount": 1},
        "reward": {"money": 1500000, "exp": 2500, "items": ["🖤 Карбон"]}
    },
    {
        "id": 6,
        "name": "🎯 Снайпер",
        "description": "Купите снайперскую винтовку",
        "requirement": {"type": "weapon", "name": "🔫 AWP"},
        "reward": {"money": 2500000, "exp": 3500, "items": ["🥇 Золото"]}
    },
    {
        "id": 7,
        "name": "⭐ Ветеран",
        "description": "Достигните 10 уровня",
        "requirement": {"type": "level", "amount": 10},
        "reward": {"money": 5000000, "exp": 5000, "items": ["💎 Алмазы"]}
    },
    {
        "id": 8,
        "name": "🔨 Мастер на все руки",
        "description": "Создайте предмет через крафт",
        "requirement": {"type": "craft", "amount": 1},
        "reward": {"money": 4000000, "exp": 4500, "items": ["☢️ Уран"]}
    },
    {
        "id": 9,
        "name": "🏆 Коллекционер",
        "description": "Соберите 10 уникальных предметов",
        "requirement": {"type": "collection", "amount": 10},
        "reward": {"money": 6000000, "exp": 6000, "items": ["🤖 ИИ-чип"]}
    },
    {
        "id": 10,
        "name": "👑 Император",
        "description": "Заработайте 100,000,000 ₽",
        "requirement": {"type": "money", "amount": 100000000},
        "reward": {"money": 20000000, "exp": 10000, "items": ["⚛️ Квантовое ядро"]}
    }
]

# Система аутентификации
class AuthenticationSystem:
    def __init__(self):
        self.pending_auth = {}
    
    def generate_auth_code(self, user_id):
        code = str(random.randint(100000, 999999))
        self.pending_auth[user_id] = {
            'code': code,
            'timestamp': time.time(),
            'attempts': 0
        }
        return code
    
    def verify_auth_code(self, user_id, code):
        if user_id not in self.pending_auth:
            return False, "Код не найден или устарел"
        
        auth_data = self.pending_auth[user_id]
        
        # Проверка времени (код действителен 5 минут)
        if time.time() - auth_data['timestamp'] > 300:
            del self.pending_auth[user_id]
            return False, "Код устарел"
        
        # Проверка попыток
        if auth_data['attempts'] >= 3:
            del self.pending_auth[user_id]
            return False, "Слишком много неверных попыток"
        
        auth_data['attempts'] += 1
        
        if auth_data['code'] == code:
            del self.pending_auth[user_id]
            return True, "Аутентификация успешна"
        else:
            remaining_attempts = 3 - auth_data['attempts']
            return False, f"Неверный код. Осталось попыток: {remaining_attempts}"

auth_system = AuthenticationSystem()

# Инициализация базы данных
def init_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            balance INTEGER DEFAULT 1000000,
            level INTEGER DEFAULT 1,
            experience INTEGER DEFAULT 0,
            server TEXT DEFAULT NULL,
            phone_number TEXT DEFAULT NULL,
            car_number TEXT DEFAULT NULL,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_authenticated BOOLEAN DEFAULT FALSE,
            black_pass_tier INTEGER DEFAULT 0
        )
    ''')
    
    # Таблица инвентаря пользователя
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_type TEXT,
            item_name TEXT,
            item_data TEXT,
            acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Таблица ресурсов пользователя
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_resources (
            user_id INTEGER,
            resource_type TEXT,
            quantity INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, resource_type),
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Таблица квестов Black Pass
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_quests (
            user_id INTEGER,
            quest_id INTEGER,
            progress INTEGER DEFAULT 0,
            completed BOOLEAN DEFAULT FALSE,
            completed_at TIMESTAMP,
            PRIMARY KEY (user_id, quest_id),
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Таблица семей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS families (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            tag TEXT UNIQUE,
            owner_id INTEGER,
            level INTEGER DEFAULT 1,
            balance INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users (user_id)
        )
    ''')
    
    # Таблица участников семей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS family_members (
            family_id INTEGER,
            user_id INTEGER,
            role TEXT DEFAULT 'member',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (family_id, user_id),
            FOREIGN KEY (family_id) REFERENCES families (id),
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Таблица фарма
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_farm (
            user_id INTEGER PRIMARY KEY,
            job_type TEXT,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Таблица краж
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_robberies (
            user_id INTEGER PRIMARY KEY,
            last_robbery TIMESTAMP,
            success_count INTEGER DEFAULT 0,
            fail_count INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Функции для работы с базой данных
def get_user_data(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            'user_id': user[0],
            'username': user[1],
            'first_name': user[2],
            'last_name': user[3],
            'balance': user[4],
            'level': user[5],
            'experience': user[6],
            'server': user[7],
            'phone_number': user[8],
            'car_number': user[9],
            'registered_at': user[10],
            'last_active': user[11],
            'is_authenticated': user[12],
            'black_pass_tier': user[13]
        }
    return None

def update_user_data(user_id, **kwargs):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    if kwargs:
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(user_id)
        cursor.execute(f'UPDATE users SET {set_clause} WHERE user_id = ?', values)
    
    conn.commit()
    conn.close()

def create_user(user_id, username, first_name, last_name):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Генерация случайного номера телефона и автономера
    phone_number = generate_phone_number()
    car_number = generate_car_number()
    
    cursor.execute('''
        INSERT OR IGNORE INTO users 
        (user_id, username, first_name, last_name, phone_number, car_number) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, last_name, phone_number, car_number))
    
    # Инициализация квестов Black Pass
    for quest in BLACK_PASS_QUESTS:
        cursor.execute('''
            INSERT OR IGNORE INTO user_quests (user_id, quest_id)
            VALUES (?, ?)
        ''', (user_id, quest["id"]))
    
    conn.commit()
    conn.close()

def get_user_inventory(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_inventory WHERE user_id = ?', (user_id,))
    inventory = cursor.fetchall()
    conn.close()
    return inventory

def add_to_inventory(user_id, item_type, item_name, item_data):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_inventory (user_id, item_type, item_name, item_data)
        VALUES (?, ?, ?, ?)
    ''', (user_id, item_type, item_name, item_data))
    conn.commit()
    conn.close()

def get_user_resources(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_resources WHERE user_id = ?', (user_id,))
    resources = cursor.fetchall()
    conn.close()
    
    resource_dict = {}
    for resource in resources:
        resource_dict[resource[1]] = resource[2]
    
    return resource_dict

def update_user_resource(user_id, resource_type, quantity):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO user_resources (user_id, resource_type, quantity)
        VALUES (?, ?, ?)
    ''', (user_id, resource_type, quantity))
    
    conn.commit()
    conn.close()

def get_user_quests(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_quests WHERE user_id = ?', (user_id,))
    quests = cursor.fetchall()
    conn.close()
    
    quest_dict = {}
    for quest in quests:
        quest_dict[quest[1]] = {
            "progress": quest[2],
            "completed": bool(quest[3]),
            "completed_at": quest[4]
        }
    
    return quest_dict

def update_user_quest(user_id, quest_id, progress, completed=False):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    if completed:
        cursor.execute('''
            UPDATE user_quests 
            SET progress = ?, completed = TRUE, completed_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND quest_id = ?
        ''', (progress, user_id, quest_id))
    else:
        cursor.execute('''
            UPDATE user_quests 
            SET progress = ?
            WHERE user_id = ? AND quest_id = ?
        ''', (progress, user_id, quest_id))
    
    conn.commit()
    conn.close()

# Функции для работы с семьями
def create_family(name, tag, owner_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO families (name, tag, owner_id)
            VALUES (?, ?, ?)
        ''', (name, tag, owner_id))
        
        family_id = cursor.lastrowid
        
        cursor.execute('''
            INSERT INTO family_members (family_id, user_id, role)
            VALUES (?, ?, 'owner')
        ''', (family_id, owner_id))
        
        conn.commit()
        return True, "Семья успешно создана!"
    except sqlite3.IntegrityError:
        return False, "Семья с таким названием или тегом уже существует!"
    finally:
        conn.close()

def get_family_by_name(name):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM families WHERE name = ?', (name,))
    family = cursor.fetchone()
    conn.close()
    return family

def get_user_family(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT f.*, fm.role 
        FROM families f 
        JOIN family_members fm ON f.id = fm.family_id 
        WHERE fm.user_id = ?
    ''', (user_id,))
    family = cursor.fetchone()
    conn.close()
    return family

# Функции для фарма
def start_farming(user_id, job_type):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    start_time = datetime.datetime.now()
    job_data = next((job for job in FARM_JOBS if job["name"] == job_type), None)
    
    if job_data:
        end_time = start_time + datetime.timedelta(seconds=job_data["cooldown"])
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_farm (user_id, job_type, start_time, end_time)
            VALUES (?, ?, ?, ?)
        ''', (user_id, job_type, start_time, end_time))
    
    conn.commit()
    conn.close()
    return job_data

def get_farm_status(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_farm WHERE user_id = ?', (user_id,))
    farm_data = cursor.fetchone()
    conn.close()
    return farm_data

def complete_farming(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM user_farm WHERE user_id = ?', (user_id,))
    farm_data = cursor.fetchone()
    
    if farm_data:
        job_type = farm_data[1]
        end_time = datetime.datetime.fromisoformat(farm_data[3])
        
        if datetime.datetime.now() >= end_time:
            job_data = next((job for job in FARM_JOBS if job["name"] == job_type), None)
            if job_data:
                reward = random.randint(job_data["min_reward"], job_data["max_reward"])
                
                # Применение случайного события
                event = random.choices(
                    FARM_EVENTS, 
                    weights=[e["chance"] for e in FARM_EVENTS]
                )[0]
                
                if "multiplier" in event:
                    reward = int(reward * event["multiplier"])
                elif "bonus" in event:
                    reward += event["bonus"]
                
                # Проверка риска
                if random.random() < job_data["risk"]:
                    reward = int(reward * 0.5)  # Потеря 50% при неудаче
                    event_message = f"❌ Неудача! {event['name']}. Вы потеряли часть дохода."
                else:
                    event_message = f"✅ Успех! {event['name']}"
                
                # Обновление баланса и добавление опыта
                cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (reward, user_id))
                cursor.execute('DELETE FROM user_farm WHERE user_id = ?', (user_id,))
                
                # Добавление опыта
                new_level = add_experience(user_id, job_data["exp"])
                
                conn.commit()
                conn.close()
                
                level_up_message = f"\n🎉 Поздравляем! Вы достигли {new_level} уровня!" if new_level else ""
                
                return True, reward, event_message + level_up_message
    
    conn.close()
    return False, 0, "Фарм еще не завершен!"

# Функции для краж
def can_rob(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM user_robberies WHERE user_id = ?', (user_id,))
    robbery_data = cursor.fetchone()
    
    if not robbery_data:
        return True
    
    last_robbery = datetime.datetime.fromisoformat(robbery_data[1])
    cooldown = datetime.timedelta(hours=1)
    
    conn.close()
    return datetime.datetime.now() - last_robbery >= cooldown

def update_robbery_stats(user_id, success):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM user_robberies WHERE user_id = ?', (user_id,))
    robbery_data = cursor.fetchone()
    
    if robbery_data:
        if success:
            cursor.execute('''
                UPDATE user_robberies 
                SET last_robbery = ?, success_count = success_count + 1 
                WHERE user_id = ?
            ''', (datetime.datetime.now(), user_id))
        else:
            cursor.execute('''
                UPDATE user_robberies 
                SET last_robbery = ?, fail_count = fail_count + 1 
                WHERE user_id = ?
            ''', (datetime.datetime.now(), user_id))
    else:
        if success:
            cursor.execute('''
                INSERT INTO user_robberies (user_id, last_robbery, success_count)
                VALUES (?, ?, 1)
            ''', (user_id, datetime.datetime.now()))
        else:
            cursor.execute('''
                INSERT INTO user_robberies (user_id, last_robbery, fail_count)
                VALUES (?, ?, 1)
            ''', (user_id, datetime.datetime.now()))
    
    conn.commit()
    conn.close()

# Система уровней
def add_experience(user_id, exp):
    user_data = get_user_data(user_id)
    if not user_data:
        return None
    
    new_exp = user_data['experience'] + exp
    current_level = user_data['level']
    
    # Формула для следующего уровня: level^2 * 1000
    exp_needed = current_level * current_level * 1000
    
    if new_exp >= exp_needed:
        new_level = current_level + 1
        new_exp = new_exp - exp_needed
        
        update_user_data(user_id, level=new_level, experience=new_exp)
        return new_level
    else:
        update_user_data(user_id, experience=new_exp)
        return None

# Функции для крафта
def can_craft_item(user_id, item):
    user_resources = get_user_resources(user_id)
    user_data = get_user_data(user_id)
    
    if user_data['balance'] < item['craft_price']:
        return False, "Недостаточно денег для крафта"
    
    for resource, amount in item['resources'].items():
        if user_resources.get(resource, 0) < amount:
            return False, f"Недостаточно {RESOURCES[resource]['name']}"
    
    return True, "Можно создать"

def craft_item(user_id, item):
    success, message = can_craft_item(user_id, item)
    
    if not success:
        return False, message
    
    # Списываем ресурсы и деньги
    user_resources = get_user_resources(user_id)
    for resource, amount in item['resources'].items():
        new_quantity = user_resources.get(resource, 0) - amount
        update_user_resource(user_id, resource, new_quantity)
    
    user_data = get_user_data(user_id)
    new_balance = user_data['balance'] - item['craft_price']
    update_user_data(user_id, balance=new_balance)
    
    # Добавляем предмет в инвентарь
    add_to_inventory(user_id, "vehicle" if "car" in item['name'].lower() else "weapon", item['name'], str(item))
    
    return True, f"✅ {item['name']} успешно создан!"

# Функции для Black Pass
def check_quest_progress(user_id, quest):
    user_data = get_user_data(user_id)
    user_inventory = get_user_inventory(user_id)
    user_quests = get_user_quests(user_id)
    
    quest_data = user_quests.get(quest["id"], {"progress": 0, "completed": False})
    
    if quest_data["completed"]:
        return quest_data["progress"], True
    
    requirement = quest["requirement"]
    progress = 0
    
    if requirement["type"] == "money":
        progress = min(user_data['balance'], requirement["amount"])
    elif requirement["type"] == "level":
        progress = min(user_data['level'], requirement["amount"])
    elif requirement["type"] == "house":
        houses = [item for item in user_inventory if item[2] == "house"]
        progress = min(len(houses), requirement["amount"])
    elif requirement["type"] == "cars":
        cars = [item for item in user_inventory if "car" in item[2].lower() or "🚗" in item[2] or "🏎" in item[2]]
        progress = min(len(cars), requirement["amount"])
    elif requirement["type"] == "business":
        businesses = [item for item in user_inventory if item[2] == "business"]
        progress = min(len(businesses), requirement["amount"])
    elif requirement["type"] == "family":
        family = get_user_family(user_id)
        progress = 1 if family else 0
    elif requirement["type"] == "weapon":
        weapons = [item for item in user_inventory if requirement["name"] in item[3]]
        progress = 1 if weapons else 0
    elif requirement["type"] == "craft":
        crafted_items = [item for item in user_inventory if "crafted" in item[3]]
        progress = min(len(crafted_items), requirement["amount"])
    elif requirement["type"] == "collection":
        progress = min(len(user_inventory), requirement["amount"])
    
    completed = progress >= requirement["amount"]
    update_user_quest(user_id, quest["id"], progress, completed)
    
    return progress, completed

def claim_quest_reward(user_id, quest):
    user_quests = get_user_quests(user_id)
    quest_data = user_quests.get(quest["id"])
    
    if not quest_data or not quest_data["completed"]:
        return False, "Квест не завершен"
    
    # Выдача наград
    reward = quest["reward"]
    user_data = get_user_data(user_id)
    
    if "money" in reward:
        new_balance = user_data['balance'] + reward["money"]
        update_user_data(user_id, balance=new_balance)
    
    if "exp" in reward:
        add_experience(user_id, reward["exp"])
    
    if "items" in reward:
        for item in reward["items"]:
            # Находим тип ресурса по эмодзи
            resource_type = None
            for res_key, res_data in RESOURCES.items():
                if res_data["emoji"] == item:
                    resource_type = res_key
                    break
            
            if resource_type:
                user_resources = get_user_resources(user_id)
                current_quantity = user_resources.get(resource_type, 0)
                update_user_resource(user_id, resource_type, current_quantity + 1)
    
    return True, "Награда получена!"

# === КНОПКИ И ИНТЕРФЕЙСЫ ===

def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("👤 Профиль", callback_data="profile"),
         InlineKeyboardButton("💼 Работа", callback_data="work")],
        [InlineKeyboardButton("🏪 Магазин", callback_data="shop"),
         InlineKeyboardButton("🎒 Инвентарь", callback_data="inventory")],
        [InlineKeyboardButton("🔨 Крафт", callback_data="craft"),
         InlineKeyboardButton("👥 Семьи", callback_data="families")],
        [InlineKeyboardButton("🎮 Игры", callback_data="games"),
         InlineKeyboardButton("⚡ Black Pass", callback_data="black_pass")],
        [InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
         InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_shop_keyboard():
    keyboard = [
        [InlineKeyboardButton("🚗 Автомобили", callback_data="shop_cars"),
         InlineKeyboardButton("🏠 Дома", callback_data="shop_houses")],
        [InlineKeyboardButton("🔫 Оружие", callback_data="shop_weapons"),
         InlineKeyboardButton("💼 Бизнесы", callback_data="shop_businesses")],
        [InlineKeyboardButton("📱 Сим-карты", callback_data="shop_simcards"),
         InlineKeyboardButton("🎭 Скины", callback_data="shop_skins")],
        [InlineKeyboardButton("⚙️ Ресурсы", callback_data="shop_resources"),
         InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_work_keyboard():
    keyboard = []
    for i in range(0, len(FARM_JOBS), 2):
        if i + 1 < len(FARM_JOBS):
            keyboard.append([
                InlineKeyboardButton(FARM_JOBS[i]["name"], callback_data=f"work_{i}"),
                InlineKeyboardButton(FARM_JOBS[i+1]["name"], callback_data=f"work_{i+1}")
            ])
        else:
            keyboard.append([InlineKeyboardButton(FARM_JOBS[i]["name"], callback_data=f"work_{i}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

def get_craft_keyboard():
    keyboard = [
        [InlineKeyboardButton("🚗 Крафт машин", callback_data="craft_cars"),
         InlineKeyboardButton("🔫 Крафт оружия", callback_data="craft_weapons")],
        [InlineKeyboardButton("📦 Мои ресурсы", callback_data="craft_resources"),
         InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_craft_cars_keyboard():
    keyboard = []
    for i in range(0, len(CRAFTABLE_CARS), 2):
        if i + 1 < len(CRAFTABLE_CARS):
            keyboard.append([
                InlineKeyboardButton(CRAFTABLE_CARS[i]["name"], callback_data=f"craft_car_{i}"),
                InlineKeyboardButton(CRAFTABLE_CARS[i+1]["name"], callback_data=f"craft_car_{i+1}")
            ])
        else:
            keyboard.append([InlineKeyboardButton(CRAFTABLE_CARS[i]["name"], callback_data=f"craft_car_{i}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="craft")])
    return InlineKeyboardMarkup(keyboard)

def get_families_keyboard():
    keyboard = [
        [InlineKeyboardButton("👥 Моя семья", callback_data="family_my"),
         InlineKeyboardButton("🏠 Создать семью", callback_data="family_create")],
        [InlineKeyboardButton("📊 Топ семей", callback_data="family_top"),
         InlineKeyboardButton("🔍 Найти семью", callback_data="family_search")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_games_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎰 Казино", callback_data="game_casino"),
         InlineKeyboardButton("🎯 Рулетка", callback_data="game_roulette")],
        [InlineKeyboardButton("🎮 Мини-игры", callback_data="game_minigames"),
         InlineKeyboardButton("🏆 Турниры", callback_data="game_tournaments")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_black_pass_keyboard():
    keyboard = [
        [InlineKeyboardButton("📋 Список квестов", callback_data="black_pass_quests"),
         InlineKeyboardButton("🎁 Получить награды", callback_data="black_pass_rewards")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# === ОСНОВНЫЕ КОМАНДЫ БОТА ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Проверяем, зарегистрирован ли пользователь
    user_data = get_user_data(user_id)
    
    if not user_data:
        # Пользователь не зарегистрирован - показываем кнопку регистрации
        keyboard = [[InlineKeyboardButton("🚀 Начать регистрацию", callback_data="start_registration")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""
🎮 *Добро пожаловать в Black Russia Bot!*

Привет, {user.first_name}! 👋

Это официальный бот игры *Black Russia* - самой популярной русской ролевой игры!

⚡ *Новые возможности:*
• 🔨 *Система крафта* - Создавайте уникальные машины и оружие
• ⚡ *Black Pass* - Выполняйте квесты и получайте эксклюзивные награды
• 💼 *20+ видов работ* - Зарабатывайте деньги и опыт
• 🚗 *50+ автомобилей* - От ВАЗа до космических кораблей
• 🏠 *Элитная недвижимость* - От квартир до небоскребов
• 👥 *Расширенные семьи* - Объединяйтесь и доминируйте
• 🎮 *Мини-игры и казино* - Испытайте удачу

🎯 *Для начала нажмите кнопку ниже:*
        """
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        # Пользователь зарегистрирован - показываем главное меню
        if not user_data['is_authenticated']:
            # Требуется аутентификация
            auth_code = auth_system.generate_auth_code(user_id)
            
            auth_text = f"""
🔐 *Требуется аутентификация*

Для доступа к функциям бота введите код подтверждения:

🛡 *Код безопасности:* `{auth_code}`

✍️ *Введите этот код в чат для подтверждения*
            """
            
            await update.message.reply_text(
                auth_text,
                parse_mode='Markdown'
            )
        else:
            # Пользователь аутентифицирован - показываем главное меню
            main_menu_text = f"""
🎮 *Главное меню Black Russia*

Привет, *{user.first_name}*! 👋

💰 Баланс: *{user_data['balance']:,} ₽*
🎯 Уровень: *{user_data['level']}*
⭐ Опыт: *{user_data['experience']:,} XP*
⚡ Black Pass: *Уровень {user_data['black_pass_tier']}*

Выберите действие:
            """
            
            await update.message.reply_text(
                main_menu_text,
                reply_markup=get_main_menu_keyboard(),
                parse_mode='Markdown'
            )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    callback_data = query.data
    
    user_data = get_user_data(user_id)
    
    if not user_data:
        await query.edit_message_text("❌ Сначала зарегистрируйтесь через /start")
        return
    
    if not user_data['is_authenticated']:
        await query.edit_message_text("❌ Сначала пройдите аутентификацию через /start")
        return
    
    # Обработка callback данных
    if callback_data == "main_menu":
        main_menu_text = f"""
🎮 *Главное меню Black Russia*

Привет, *{query.from_user.first_name}*! 👋

💰 Баланс: *{user_data['balance']:,} ₽*
🎯 Уровень: *{user_data['level']}*
⭐ Опыт: *{user_data['experience']:,} XP*
⚡ Black Pass: *Уровень {user_data['black_pass_tier']}*

Выберите действие:
        """
        await query.edit_message_text(
            main_menu_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode='Markdown'
        )
    
    elif callback_data == "profile":
        await show_profile(query, user_data)
    
    elif callback_data == "shop":
        await show_shop_menu(query)
    
    elif callback_data == "work":
        await show_work_menu(query)
    
    elif callback_data == "inventory":
        await show_inventory(query, user_id)
    
    elif callback_data == "craft":
        await show_craft_menu(query)
    
    elif callback_data == "families":
        await show_families_menu(query)
    
    elif callback_data == "games":
        await show_games_menu(query)
    
    elif callback_data == "black_pass":
        await show_black_pass_menu(query, user_id)
    
    elif callback_data == "settings":
        await show_settings(query)
    
    elif callback_data == "help":
        await show_help(query)
    
    elif callback_data.startswith("shop_"):
        await handle_shop_callback(query, callback_data, user_data)
    
    elif callback_data.startswith("work_"):
        await handle_work_callback(query, callback_data, user_id)
    
    elif callback_data.startswith("craft_"):
        await handle_craft_callback(query, callback_data, user_id)
    
    elif callback_data.startswith("family_"):
        await handle_family_callback(query, callback_data, user_id)
    
    elif callback_data.startswith("game_"):
        await handle_game_callback(query, callback_data, user_id)
    
    elif callback_data.startswith("black_pass_"):
        await handle_black_pass_callback(query, callback_data, user_id)

async def show_profile(query, user_data):
    user_resources = get_user_resources(user_data['user_id'])
    
    resources_text = ""
    for resource, quantity in user_resources.items():
        if quantity > 0:
            resources_text += f"{RESOURCES[resource]['emoji']} {RESOURCES[resource]['name']}: {quantity}\n"
    
    if not resources_text:
        resources_text = "Ресурсы отсутствуют"
    
    profile_text = f"""
👤 *Профиль игрока*

📛 *Имя:* {query.from_user.first_name}
🆔 *ID:* `{user_data['user_id']}`
💰 *Баланс:* {user_data['balance']:,} ₽
🎯 *Уровень:* {user_data['level']}
⭐ *Опыт:* {user_data['experience']:,} XP

📱 *Телефон:* +7 {user_data['phone_number']}
🚗 *Автономер:* {user_data['car_number']}
🌐 *Сервер:* {user_data['server'] or 'Не выбран'}

📦 *Ресурсы:*
{resources_text}

📅 *Зарегистрирован:* {user_data['registered_at'][:10]}
    """
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
    await query.edit_message_text(
        profile_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_shop_menu(query):
    shop_text = """
🏪 *Магазин Black Russia*

Здесь вы можете приобрести различные товары:

🚗 *Автомобили* - От ВАЗа до Бугатти
🏠 *Недвижимость* - От квартиры до дворца
🔫 *Оружие* - Для защиты и нападения
💼 *Бизнесы* - Пассивный доход
📱 *Сим-карты* - Уникальные номера
🎭 *Скины и аксессуары* - Для стиля
⚙️ *Ресурсы* - Для крафта уникальных предметов

Выберите категорию:
    """
    await query.edit_message_text(
        shop_text,
        reply_markup=get_shop_keyboard(),
        parse_mode='Markdown'
    )

async def show_work_menu(query):
    work_text = """
💼 *Работа в Black Russia*

Выберите работу для заработка денег и опыта:

💡 *Чем выше риск - тем выше награда!*
⚡ *Специальные события* могут увеличить ваш доход!

Выберите работу:
    """
    await query.edit_message_text(
        work_text,
        reply_markup=get_work_keyboard(),
        parse_mode='Markdown'
    )

async def show_inventory(query, user_id):
    inventory = get_user_inventory(user_id)
    
    if not inventory:
        inventory_text = "🎒 *Ваш инвентарь пуст*\n\nПосетите магазин чтобы приобрести товары!"
    else:
        inventory_text = "🎒 *Ваш инвентарь:*\n\n"
        cars = [item for item in inventory if "car" in item[2].lower() or "🚗" in item[2] or "🏎" in item[2]]
        houses = [item for item in inventory if item[2] == "house"]
        weapons = [item for item in inventory if item[2] == "weapon"]
        businesses = [item for item in inventory if item[2] == "business"]
        
        if cars:
            inventory_text += "🚗 *Автомобили:*\n"
            for car in cars[:5]:  # Показываем первые 5
                inventory_text += f"• {car[3]}\n"
        
        if houses:
            inventory_text += "\n🏠 *Недвижимость:*\n"
            for house in houses[:3]:
                inventory_text += f"• {house[3]}\n"
        
        if weapons:
            inventory_text += "\n🔫 *Оружие:*\n"
            for weapon in weapons[:3]:
                inventory_text += f"• {weapon[3]}\n"
        
        if businesses:
            inventory_text += "\n💼 *Бизнесы:*\n"
            for business in businesses[:2]:
                inventory_text += f"• {business[3]}\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
    await query.edit_message_text(
        inventory_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_craft_menu(query):
    craft_text = """
🔨 *Система крафта Black Russia*

Создавайте уникальные предметы, которых нет в магазине!

🚗 *Крафт машин* - Уникальные автомобили с особыми свойствами
🔫 *Крафт оружия* - Мощное оружие будущего
📦 *Ресурсы* - Просмотр ваших ресурсов

💡 *Для крафта вам понадобятся:*
• Деньги для оплаты работы
• Ресурсы, которые можно купить в магазине или получить за квесты

Выберите категорию:
    """
    await query.edit_message_text(
        craft_text,
        reply_markup=get_craft_keyboard(),
        parse_mode='Markdown'
    )

async def show_families_menu(query):
    families_text = """
👥 *Семьи Black Russia*

Семьи - это объединения игроков для совместной игры:

👑 *Возможности семей:*
• Совместные заработки
• Защита территории
• Войны с другими семьями
• Общий банк семьи
• Уникальные бонусы

Выберите действие:
    """
    await query.edit_message_text(
        families_text,
        reply_markup=get_families_keyboard(),
        parse_mode='Markdown'
    )

async def show_games_menu(query):
    games_text = """
🎮 *Игры и развлечения*

Испытайте удачу в наших играх:

🎰 *Казино* - Классические азартные игры
🎯 *Рулетка* - Ставки на числа
🎮 *Мини-игры* - Различные развлечения
🏆 *Турниры* - Соревнования с призами

Выберите игру:
    """
    await query.edit_message_text(
        games_text,
        reply_markup=get_games_keyboard(),
        parse_mode='Markdown'
    )

async def show_black_pass_menu(query, user_id):
    user_quests = get_user_quests(user_id)
    completed_quests = sum(1 for q in user_quests.values() if q["completed"])
    total_quests = len(BLACK_PASS_QUESTS)
    
    black_pass_text = f"""
⚡ *Black Pass - Сезон 1*

Система достижений и наград!

📊 *Прогресс:* {completed_quests}/{total_quests} квестов завершено
🎁 *Награды:* Деньги, опыт и уникальные ресурсы

💎 *Эксклюзивные награды за выполнение всех квестов:*
• Легендарный автомобиль
• Мифическое оружие
• Уникальные ресурсы для крафта

Выберите действие:
    """
    await query.edit_message_text(
        black_pass_text,
        reply_markup=get_black_pass_keyboard(),
        parse_mode='Markdown'
    )

async def show_settings(query):
    settings_text = """
⚙️ *Настройки бота*

Здесь вы можете настроить бота под себя:

🔔 Уведомления
🌐 Язык интерфейса
🎨 Тема оформления
🔒 Настройки приватности

*Функции в разработке...*
    """
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
    await query.edit_message_text(
        settings_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_help(query):
    help_text = """
ℹ️ *Помощь по боту Black Russia*

📖 *Основные команды:*
/start - Запустить бота
/profile - Показать профиль
/shop - Открыть магазин
/work - Начать работать
/inventory - Показать инвентарь
/craft - Открыть систему крафта

🎮 *Игровой процесс:*
• Зарабатывайте деньги работой
• Покупайте автомобили и недвижимость
• Создавайте уникальные предметы через крафт
• Выполняйте квесты Black Pass
• Создавайте семьи с друзьями
• Участвуйте в играх и турнирах

💡 *Советы:*
• Регулярно работайте для стабильного дохода
• Инвестируйте в бизнесы для пассивного заработка
• Собирайте ресурсы для крафта уникальных предметов
• Выполняйте квесты Black Pass для эксклюзивных наград
    """
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
    await query.edit_message_text(
        help_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_shop_callback(query, callback_data, user_data):
    if callback_data == "shop_cars":
        await show_car_shop(query, user_data)
    elif callback_data == "shop_houses":
        await show_house_shop(query, user_data)
    elif callback_data == "shop_weapons":
        await show_weapon_shop(query, user_data)
    elif callback_data == "shop_businesses":
        await show_business_shop(query, user_data)
    elif callback_data == "shop_simcards":
        await show_simcard_shop(query, user_data)
    elif callback_data == "shop_skins":
        await show_skin_shop(query, user_data)
    elif callback_data == "shop_resources":
        await show_resource_shop(query, user_data)

async def handle_work_callback(query, callback_data, user_id):
    try:
        job_index = int(callback_data.replace("work_", ""))
        job_data = FARM_JOBS[job_index]
    except (ValueError, IndexError):
        await query.edit_message_text("❌ Работа не найдена")
        return
    
    # Проверяем, не работает ли пользователь уже
    farm_status = get_farm_status(user_id)
    if farm_status:
        await query.edit_message_text("❌ Вы уже работаете! Завершите текущую работу.")
        return
    
    # Начинаем работу
    job_data = start_farming(user_id, job_data["name"])
    
    if job_data:
        minutes = job_data['cooldown'] // 60
        seconds = job_data['cooldown'] % 60
        
        work_text = f"""
💼 *Вы начали работать!*

🏢 *Работа:* {job_data['name']}
💰 *Заработок:* {job_data['min_reward']:,} - {job_data['max_reward']:,} ₽
⭐ *Опыт:* {job_data['exp']} XP
⏰ *Длительность:* {minutes} мин {seconds} сек
⚡ *Риск:* {job_data['risk']*100}%

🕐 Вернитесь через {minutes} минут чтобы получить оплату!
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Назад к работам", callback_data="work")]]
        await query.edit_message_text(
            work_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text("❌ Ошибка при начале работы")

async def handle_craft_callback(query, callback_data, user_id):
    if callback_data == "craft_cars":
        await show_craft_cars_menu(query, user_id)
    elif callback_data == "craft_weapons":
        await show_craft_weapons_menu(query, user_id)
    elif callback_data == "craft_resources":
        await show_craft_resources(query, user_id)
    elif callback_data.startswith("craft_car_"):
        await handle_craft_car(query, callback_data, user_id)
    elif callback_data.startswith("craft_weapon_"):
        await handle_craft_weapon(query, callback_data, user_id)

async def handle_family_callback(query, callback_data, user_id):
    if callback_data == "family_my":
        family_data = get_user_family(user_id)
        if family_data:
            family_text = f"""
👥 *Ваша семья*

🏠 *Название:* {family_data[1]}
🔰 *Тег:* {family_data[2]}
👑 *Владелец:* {family_data[3]}
🎯 *Уровень:* {family_data[4]}
💰 *Банк:* {family_data[5]:,} ₽
👤 *Ваша роль:* {family_data[7]}
            """
        else:
            family_text = "❌ Вы не состоите в семье"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="families")]]
        await query.edit_message_text(
            family_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif callback_data == "family_create":
        family_text = """
🏠 *Создание семьи*

Для создания семьи введите:

/nf [название] [тег]

Пример:
/nf RussianMafia RM

💡 *Требования:*
• Уровень 5+
• 1,000,000 ₽ для создания
• Уникальное название и тег
        """
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="families")]]
        await query.edit_message_text(
            family_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

async def handle_game_callback(query, callback_data, user_id):
    if callback_data == "game_casino":
        casino_text = """
🎰 *Казино Black Russia*

Испытайте удачу в нашем казино!

🎯 *Доступные игры:*
• Слот-машины
• Блэкджек
• Покер
• Кости

💎 *Минимальная ставка:* 10,000 ₽
💎 *Максимальная ставка:* 1,000,000 ₽

⚡ *Для игры используйте команды:*
/casino_slots [ставка] - Играть в слоты
/casino_blackjack [ставка] - Блэкджек
/casino_dice [ставка] - Игра в кости
        """
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="games")]]
        await query.edit_message_text(
            casino_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

async def handle_black_pass_callback(query, callback_data, user_id):
    if callback_data == "black_pass_quests":
        await show_black_pass_quests(query, user_id)
    elif callback_data == "black_pass_rewards":
        await claim_black_pass_rewards(query, user_id)

# Функции для крафта
async def show_craft_cars_menu(query, user_id):
    craft_text = """
🚗 *Крафт автомобилей*

Создавайте уникальные автомобили, которых нет в магазине!

💎 *Особенности крафта:*
• Эксклюзивные модели
• Улучшенные характеристики
• Уникальный дизайн
• Высокая стоимость перепродажи

Выберите автомобиль для крафта:
    """
    await query.edit_message_text(
        craft_text,
        reply_markup=get_craft_cars_keyboard(),
        parse_mode='Markdown'
    )

async def show_craft_weapons_menu(query, user_id):
    craft_text = """
🔫 *Крафт оружия*

Создавайте мощное оружие будущего!

💎 *Особенности крафта:*
• Высокий урон
• Уникальные ability
• Редкие ресурсы
• Эксклюзивный дизайн

Доступное оружие для крафта:

"""
    
    for i, weapon in enumerate(CRAFTABLE_WEAPONS):
        craft_text += f"• {weapon['name']} - {weapon['craft_price']:,} ₽\n"
        craft_text += f"  📖 {weapon['description']}\n"
        craft_text += f"  💥 Урон: {weapon['damage']}\n"
        
        # Показываем требуемые ресурсы
        resources_text = ""
        for resource, amount in weapon['resources'].items():
            resources_text += f"{RESOURCES[resource]['emoji']} {amount} "
        craft_text += f"  📦 Ресурсы: {resources_text}\n\n"
    
    keyboard = [
        [InlineKeyboardButton("Крафт Plasma Rifle", callback_data="craft_weapon_0")],
        [InlineKeyboardButton("Крафт Quantum Grenade", callback_data="craft_weapon_1")],
        [InlineKeyboardButton("🔙 Назад", callback_data="craft")]
    ]
    
    await query.edit_message_text(
        craft_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_craft_resources(query, user_id):
    user_resources = get_user_resources(user_id)
    
    resources_text = "📦 *Ваши ресурсы:*\n\n"
    for resource, quantity in user_resources.items():
        resources_text += f"{RESOURCES[resource]['emoji']} *{RESOURCES[resource]['name']}*: {quantity}\n"
    
    if not user_resources:
        resources_text += "У вас пока нет ресурсов\n\n"
    
    resources_text += "\n💡 *Как получить ресурсы:*\n"
    resources_text += "• Покупайте в магазине\n"
    resources_text += "• Выполняйте квесты Black Pass\n"
    resources_text += "• Находите в случайных событиях"
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="craft")]]
    await query.edit_message_text(
        resources_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_craft_car(query, callback_data, user_id):
    try:
        car_index = int(callback_data.replace("craft_car_", ""))
        car = CRAFTABLE_CARS[car_index]
    except (ValueError, IndexError):
        await query.edit_message_text("❌ Автомобиль не найден")
        return
    
    user_data = get_user_data(user_id)
    can_craft, message = can_craft_item(user_id, car)
    
    craft_text = f"""
🚗 *Крафт {car['name']}*

📖 *Описание:* {car['description']}
💎 *Редкость:* {car['rarity']}
💰 *Стоимость крафта:* {car['craft_price']:,} ₽
💵 *Ваш баланс:* {user_data['balance']:,} ₽

📦 *Требуемые ресурсы:*
"""
    
    user_resources = get_user_resources(user_id)
    for resource, amount in car['resources'].items():
        has_amount = user_resources.get(resource, 0)
        status = "✅" if has_amount >= amount else "❌"
        craft_text += f"{status} {RESOURCES[resource]['emoji']} {RESOURCES[resource]['name']}: {has_amount}/{amount}\n"
    
    if can_craft:
        craft_text += f"\n✅ *Вы можете создать этот автомобиль!*"
        keyboard = [
            [InlineKeyboardButton("🔨 Создать", callback_data=f"confirm_craft_car_{car_index}")],
            [InlineKeyboardButton("🔙 Назад", callback_data="craft_cars")]
        ]
    else:
        craft_text += f"\n❌ *Недостаточно ресурсов:* {message}"
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="craft_cars")]]
    
    await query.edit_message_text(
        craft_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_craft_weapon(query, callback_data, user_id):
    try:
        weapon_index = int(callback_data.replace("craft_weapon_", ""))
        weapon = CRAFTABLE_WEAPONS[weapon_index]
    except (ValueError, IndexError):
        await query.edit_message_text("❌ Оружие не найдено")
        return
    
    user_data = get_user_data(user_id)
    can_craft, message = can_craft_item(user_id, weapon)
    
    craft_text = f"""
🔫 *Крафт {weapon['name']}*

📖 *Описание:* {weapon['description']}
💎 *Редкость:* {weapon['rarity']}
💥 *Урон:* {weapon['damage']}
💰 *Стоимость крафта:* {weapon['craft_price']:,} ₽
💵 *Ваш баланс:* {user_data['balance']:,} ₽

📦 *Требуемые ресурсы:*
"""
    
    user_resources = get_user_resources(user_id)
    for resource, amount in weapon['resources'].items():
        has_amount = user_resources.get(resource, 0)
        status = "✅" if has_amount >= amount else "❌"
        craft_text += f"{status} {RESOURCES[resource]['emoji']} {RESOURCES[resource]['name']}: {has_amount}/{amount}\n"
    
    if can_craft:
        craft_text += f"\n✅ *Вы можете создать это оружие!*"
        keyboard = [
            [InlineKeyboardButton("🔨 Создать", callback_data=f"confirm_craft_weapon_{weapon_index}")],
            [InlineKeyboardButton("🔙 Назад", callback_data="craft_weapons")]
        ]
    else:
        craft_text += f"\n❌ *Недостаточно ресурсов:* {message}"
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="craft_weapons")]]
    
    await query.edit_message_text(
        craft_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# Функции для Black Pass
async def show_black_pass_quests(query, user_id):
    quests_text = "⚡ *Black Pass - Активные квесты:*\n\n"
    
    for quest in BLACK_PASS_QUESTS:
        progress, completed = check_quest_progress(user_id, quest)
        requirement = quest["requirement"]
        
        status = "✅" if completed else "🔄"
        progress_bar = "█" * int(progress / requirement["amount"] * 10) + "░" * (10 - int(progress / requirement["amount"] * 10))
        
        quests_text += f"{status} *{quest['name']}*\n"
        quests_text += f"📖 {quest['description']}\n"
        quests_text += f"📊 {progress_bar} {progress}/{requirement['amount']}\n"
        
        if completed:
            quests_text += "🎁 *Награда готова к получению!*\n"
        else:
            # Показываем награду
            reward_text = "🎁 Награда: "
            if "money" in quest["reward"]:
                reward_text += f"💰 {quest['reward']['money']:,} ₽ "
            if "exp" in quest["reward"]:
                reward_text += f"⭐ {quest['reward']['exp']} XP "
            if "items" in quest["reward"]:
                for item in quest["reward"]["items"]:
                    reward_text += f"{item} "
            quests_text += f"{reward_text}\n"
        
        quests_text += "\n"
    
    keyboard = [
        [InlineKeyboardButton("🎁 Получить все награды", callback_data="black_pass_claim_all")],
        [InlineKeyboardButton("🔙 Назад", callback_data="black_pass")]
    ]
    
    await query.edit_message_text(
        quests_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def claim_black_pass_rewards(query, user_id):
    total_rewards = 0
    claimed_quests = []
    
    for quest in BLACK_PASS_QUESTS:
        progress, completed = check_quest_progress(user_id, quest)
        if completed:
            success, message = claim_quest_reward(user_id, quest)
            if success:
                total_rewards += 1
                claimed_quests.append(quest["name"])
    
    if total_rewards > 0:
        reward_text = f"🎉 *Получено наград: {total_rewards}*\n\n"
        for quest_name in claimed_quests:
            reward_text += f"✅ {quest_name}\n"
        
        # Обновляем уровень Black Pass
        user_data = get_user_data(user_id)
        new_tier = min(user_data['black_pass_tier'] + total_rewards, len(BLACK_PASS_QUESTS))
        update_user_data(user_id, black_pass_tier=new_tier)
        
        reward_text += f"\n⚡ *Уровень Black Pass повышен до {new_tier}!*"
    else:
        reward_text = "❌ *Нет завершенных квестов для получения наград*"
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="black_pass")]]
    await query.edit_message_text(
        reward_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# Функции магазина (остаются без изменений, но добавлен магазин ресурсов)
async def show_resource_shop(query, user_data):
    resource_text = """
⚙️ *Магазин ресурсов*

Ресурсы необходимы для крафта уникальных предметов:

"""
    
    for resource_key, resource_data in RESOURCES.items():
        price = random.randint(100000, 5000000)  # Случайная цена
        resource_text += f"{resource_data['emoji']} *{resource_data['name']}* - {price:,} ₽ ({resource_data['rarity']})\n"
    
    resource_text += f"\n💰 Ваш баланс: {user_data['balance']:,} ₽"
    
    keyboard = [
        [InlineKeyboardButton(f"Купить {RESOURCES['metal']['name']}", callback_data="buy_resource_metal")],
        [InlineKeyboardButton("🔙 Назад в магазин", callback_data="shop")]
    ]
    
    await query.edit_message_text(
        resource_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# Обработка регистрации
async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Проверяем, не зарегистрирован ли пользователь уже
    user_data = get_user_data(user_id)
    if user_data:
        await query.edit_message_text("❌ Вы уже зарегистрированы!")
        return
    
    # Начинаем процесс регистрации
    registration_text = """
🚀 *Регистрация в Black Russia*

Добро пожаловать в официальный бот игры Black Russia!

📝 *Процесс регистрации:*
1. Выбор сервера
2. Создание персонажа  
3. Получение стартового набора
4. Аутентификация

🎁 *Стартовый набор:*
• 1,000,000 ₽
• Телефон с номером
• Автомобиль с номером
• Доступ ко всем функциям

Нажмите кнопку ниже чтобы выбрать сервер:
    """
    
    # Создаем клавиатуру для выбора сервера
    keyboard = []
    for i in range(0, len(SERVERS), 2):
        if i + 1 < len(SERVERS):
            keyboard.append([
                InlineKeyboardButton(SERVERS[i], callback_data=f"server_{i}"),
                InlineKeyboardButton(SERVERS[i+1], callback_data=f"server_{i+1}")
            ])
        else:
            keyboard.append([InlineKeyboardButton(SERVERS[i], callback_data=f"server_{i}")])
    
    await query.edit_message_text(
        registration_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# Обработка выбора сервера
async def handle_server_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    server_index = int(query.data.replace("server_", ""))
    selected_server = SERVERS[server_index]
    
    # Создаем пользователя в базе данных
    create_user(user_id, query.from_user.username, query.from_user.first_name, query.from_user.last_name)
    
    # Обновляем данные пользователя с выбранным сервером
    update_user_data(user_id, server=selected_server)
    
    # Генерируем код аутентификации
    auth_code = auth_system.generate_auth_code(user_id)
    
    registration_complete_text = f"""
✅ *Регистрация завершена!*

🎉 Поздравляем, {query.from_user.first_name}! 
Вы успешно зарегистрировались в Black Russia Bot!

📊 *Ваши данные:*
🌐 *Сервер:* {selected_server}
📱 *Телефон:* +7 {get_user_data(user_id)['phone_number']}
🚗 *Автомобиль:* {get_user_data(user_id)['car_number']}
💰 *Баланс:* 1,000,000 ₽

🔐 *Аутентификация*
Для завершения регистрации введите код безопасности:

🛡 *Код подтверждения:* `{auth_code}`

✍️ *Введите этот код в чат для активации аккаунта*
    """
    
    await query.edit_message_text(
        registration_complete_text,
        parse_mode='Markdown'
    )

# Обработка текстовых сообщений (для аутентификации)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    message_text = update.message.text.strip()
    
    user_data = get_user_data(user_id)
    
    if not user_data:
        await update.message.reply_text("❌ Сначала зарегистрируйтесь через /start")
        return
    
    if user_data['is_authenticated']:
        # Пользователь уже аутентифицирован
        await update.message.reply_text(
            "🎮 Используйте кнопки меню для навигации!",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Проверяем код аутентификации
    success, message = auth_system.verify_auth_code(user_id, message_text)
    
    if success:
        # Аутентификация успешна
        update_user_data(user_id, is_authenticated=True)
        
        welcome_text = f"""
🎊 *Аутентификация успешна!*

Добро пожаловать в игру, *{update.message.from_user.first_name}*! 🎉

Теперь вам доступны все функции бота:

💰 *Заработок денег* - 20+ видов работ
🚗 *Транспорт* - 50+ автомобилей + уникальный крафт
🏠 *Недвижимость* - От квартир до небоскребов
🔨 *Крафт* - Создавайте эксклюзивные предметы
⚡ *Black Pass* - Квесты с уникальными наградами
👥 *Семьи* - Объединяйтесь с друзьями
🎮 *Игры* - Испытайте удачу

🎯 *Начните свое восхождение к вершинам Black Russia!*

Выберите действие из меню:
        """
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode='Markdown'
        )
    else:
        # Неверный код
        await update.message.reply_text(f"❌ {message}")

# Основная функция
def main():
    # Запуск веб-сервера в отдельном потоке
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    # Инициализация базы данных
    init_database()
    
    # Создание приложения
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    
    # Обработчики callback-ов
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(CallbackQueryHandler(handle_server_selection, pattern="^server_"))
    application.add_handler(CallbackQueryHandler(start_registration, pattern="^start_registration$"))
    
    # Обработчик текстовых сообщений (для аутентификации)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()