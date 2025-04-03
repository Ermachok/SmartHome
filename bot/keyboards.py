from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

COLORS = {
    "🔴 Кровавая Мэри": (255, 0, 0),
    "🟠 Апельсиновый щербет": (255, 165, 0),
    "🟡 Лимонный щербет": (255, 255, 0),
    "🟢 Лесная зелень": (0, 255, 0),
    "🟦 Морской бриз": (0, 191, 255),
    "🔵 Глубокий океан": (0, 0, 255),
    "🟣 Магический фиолет": (128, 0, 128),
    "🌿 Изумрудная долина": (80, 200, 120),
    "💖 Розовый закат": (255, 105, 180),
    "⚪ Снежная вуаль": (255, 255, 255),
    "🧈 Сливочное масло": (255, 239, 100),
}

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💡 Включить/выключить свет")],
        [KeyboardButton(text="🔆 Установить яркость")],
        [
            KeyboardButton(text="🎨 Изменить цвет лампы"),
            KeyboardButton(text="Настройки расписания"),
            KeyboardButton(text="📸 Сделать фото"),
        ],
    ],
    resize_keyboard=True,
)

color_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=color)] for color in COLORS.keys()]
    + [[KeyboardButton(text="⬅ Назад")]],
    resize_keyboard=True,
)

schedule_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Показать все расписания")],
        [KeyboardButton(text="Установить новое расписание")],
        [KeyboardButton(text="⬅ Назад")],
    ],
    resize_keyboard=True,
)
