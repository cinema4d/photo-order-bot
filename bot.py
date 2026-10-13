import asyncio
import calendar
from datetime import datetime
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

BOT_TOKEN = "8570870167:AAERz1_Rf9wKCi7Dt5-9ytbGf7v1I6rDjMI"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- КАТАЛОГ БАЗЫ ГАРДЕРОБА (ФОТО И НАЗВАНИЯ) ---
# Замените ссылки на прямые ссылки ваших фото с диска/хостинга при необходимости
BASE_ITEMS = {
    "shoes": [
        {"id": "sh_1", "name": "Белые кеды / кроссовки", "photo": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800"},
        {"id": "sh_2", "name": "Черные лоферы / туфли", "photo": "https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=800"},
        {"id": "sh_3", "name": "Босоножки / открытая обувь", "photo": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=800"},
        {"id": "sh_own", "name": "Своя обувь из ТЗ", "photo": None},
    ],
    "bottom": [
        {"id": "bt_1", "name": "Прямые голубые джинсы", "photo": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800"},
        {"id": "bt_2", "name": "Черные классические брюки", "photo": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=800"},
        {"id": "bt_3", "name": "Широкие светлые палаццо", "photo": "https://images.unsplash.com/photo-1509551388413-e18d0ac5d495?w=800"},
        {"id": "bt_own", "name": "Свой низ / брюки из ТЗ", "photo": None},
    ],
    "top": [
        {"id": "tp_1", "name": "Белая базовая футболка", "photo": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800"},
        {"id": "tp_2", "name": "Черный топ / лонгслив", "photo": "https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=800"},
        {"id": "tp_3", "name": "Объемный жакет / пиджак", "photo": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800"},
        {"id": "tp_own", "name": "Свой артикул из ТЗ", "photo": None},
    ]
}


# --- FSM Состояния ---
class Survey(StatesGroup):
    shoot_date = State()
    order_code = State()
    marketplaces = State()
    product_desc = State()
    sku_count = State()
    crop_format = State()
    model_name = State()
    location = State()
    tariff = State()
    video_details = State()
    video_aspect = State()
    
    # Подшаги образа модели (База)
    look_shoes = State()
    look_bottom = State()
    look_top = State()
    look_comment = State()
    
    look_change = State()
    model_mood = State()
    product_features = State()
    photo_examples = State()
    allow_tags_trimming = State()
    client_contacts = State()
    delivery_date = State()


def make_keyboard(buttons: list[str]) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=btn)] for btn in buttons]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)


MONTHS_RU = [
    "", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
]


def generate_calendar_keyboard(year: int, month: int) -> InlineKeyboardMarkup:
    kb = []
    month_name = MONTHS_RU[month]
    kb.append([InlineKeyboardButton(text=f"{month_name} {year}", callback_data="cal_ignore")])

    days_header = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    kb.append([InlineKeyboardButton(text=day, callback_data="cal_ignore") for day in days_header])

    cal = calendar.monthcalendar(year, month)
    for week in cal:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="cal_ignore"))
            else:
                row.append(
                    InlineKeyboardButton(
                        text=str(day),
                        callback_data=f"cal_day:{year}:{month:02d}:{day:02d}",
                    )
                )
        kb.append(row)

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    nav_row = [
        InlineKeyboardButton(text="◀️", callback_data=f"cal_nav:{prev_year}:{prev_month}"),
        InlineKeyboardButton(text="▶️", callback_data=f"cal_nav:{next_year}:{next_month}"),
    ]
    kb.append(nav_row)
    return InlineKeyboardMarkup(inline_keyboard=kb)


def generate_base_picker(category: str) -> InlineKeyboardMarkup:
    items = BASE_ITEMS[category]
    kb = []
    for item in items:
        kb.append([InlineKeyboardButton(text=item["name"], callback_data=f"base_sel:{category}:{item['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


# --- Обработчики шагов ---
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    now = datetime.now()
    kb = generate_calendar_keyboard(now.year, now.month)
    await message.answer(
        "👋 Здравствуйте! Давайте заполним техническое задание на съемку.\n\n"
        "📅 Выберите <b>дату съемки</b> в календаре (или напишите дату вручную):",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await state.set_state(Survey.shoot_date)


@dp.callback_query(F.data.startswith("cal_nav:"), Survey.shoot_date)
async def calendar_nav(callback: CallbackQuery):
    _, year_str, month_str = callback.data.split(":")
    year, month = int(year_str), int(month_str)
    new_kb = generate_calendar_keyboard(year, month)
    await callback.message.edit_reply_markup(reply_markup=new_kb)
    await callback.answer()


@dp.callback_query(F.data == "cal_ignore")
async def calendar_ignore(callback: CallbackQuery):
    await callback.answer()


@dp.callback_query(F.data.startswith("cal_day:"), Survey.shoot_date)
async def calendar_day_chosen(callback: CallbackQuery, state: FSMContext):
    _, year, month, day = callback.data.split(":")
    selected_date = f"{day}.{month}.{year}"
    await state.update_data(shoot_date=selected_date)

    await callback.message.edit_text(f"✅ Дата съемки выбрана: <b>{selected_date}</b>", parse_mode="HTML")
    await callback.message.answer("1. Введите <b>код вашего заказа</b> (например: АН091076):", parse_mode="HTML")
    await state.set_state(Survey.order_code)
    await callback.answer()


@dp.message(Survey.shoot_date)
async def step_shoot_date_manual(message: Message, state: FSMContext):
    await state.update_data(shoot_date=message.text)
    await message.answer("1. Введите <b>код вашего заказа</b> (например: АН091076):", parse_mode="HTML")
    await state.set_state(Survey.order_code)


@dp.message(Survey.order_code)
async def step_order_code(message: Message, state: FSMContext):
    await state.update_data(order_code=message.text)
    kb = make_keyboard(["WB", "OZON", "Lamoda", "WB + OZON", "Все маркетплейсы", "Другое"])
    await message.answer(
        "2. <b>Для какого МП</b> съемка?\n"
        "<i>(Один МП входит в тариф, за последующий +350р/арт за кадрирование)</i>\n"
        "Выберите вариант или напишите свои площадки вручную:",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await state.set_state(Survey.marketplaces)


@dp.message(Survey.marketplaces)
async def step_marketplaces(message: Message, state: FSMContext):
    await state.update_data(marketplaces=message.text)
    await message.answer(
        "3. <b>Наименование товара и детали подготовки</b>:\n"
        "• Напишите название, цвет и особенности посадки.\n"
        "• ❗️ Укажите, есть ли нюансы подготовки (отпаривание, глажка).\n"
        "• Если необходимо показать крепления/ремни — отправьте описание или ссылку на диск с деталями:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML",
    )
    await state.set_state(Survey.product_desc)


@dp.message(Survey.product_desc)
async def step_product_desc(message: Message, state: FSMContext):
    await state.update_data(product_desc=message.text)
    kb = make_keyboard(["1 арт", "2 арт", "3 арт", "4 арт", "5+ арт"])
    await message.answer("4. Укажите <b>количество артикулов</b>:", reply_markup=kb, parse_mode="HTML")
    await state.set_state(Survey.sku_count)


@dp.message(Survey.sku_count)
async def step_sku_count(message: Message, state: FSMContext):
    await state.update_data(sku_count=message.text)
    kb = make_keyboard(["для WB", "на усмотрение команды", "1/1", "3/4", "9/16", "3/4 и 9/16"])
    await message.answer("5. Выберите <b>формат кадрирования фото</b>:", reply_markup=kb, parse_mode="HTML")
    await state.set_state(Survey.crop_format)


@dp.message(Survey.crop_format)
async def step_crop_format(message: Message, state: FSMContext):
    await state.update_data(crop_format=message.text)
    await message.answer(
        "6. Укажите <b>имя модели</b> (например: Юля Л):",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML",
    )
    await state.set_state(Survey.model_name)


@dp.message(Survey.model_name)
async def step_model_name(message: Message, state: FSMContext):
    await state.update_data(model_name=message.text)
    kb = make_keyboard([
        "Белая циклорама",
        "Засеренная циклорама",
        "Серая циклорама",
        "Цветной фон (+1700р)",
        "Интерьер",
    ])
    await message.answer(
        "7. Выберите <b>локацию и цвет фона</b>:\n"
        "<i>(Белое на белом не рекомендуем. Цветные фоны: +1700р за фон. Съемки в интерьере проводятся на фоне из анонса)</i>",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await state.set_state(Survey.location)


@dp.message(Survey.location)
async def step_location(message: Message, state: FSMContext):
    await state.update_data(location=message.text)
    kb = make_keyboard(["Фаре 1 арт", "Фаре 2 арт", "Фаре 3 арт", "Индивидуальный"])
    await message.answer("8. Выберите <b>тариф</b> съемки:", reply_markup=kb, parse_mode="HTML")
    await state.set_state(Survey.tariff)


@dp.message(Survey.tariff)
async def step_tariff(message: Message, state: FSMContext):
    await state.update_data(tariff=message.text)
    await message.answer(
        "9. Опишите <b>видео</b> (на какой артикул/вещь требуется проходка, динамика):\n"
        "<i>(Например: видеопроходка на черную футболку, 1 арт)</i>",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML",
    )
    await state.set_state(Survey.video_details)


@dp.message(Survey.video_details)
async def step_video_details(message: Message, state: FSMContext):
    await state.update_data(video_details=message.text)
    kb = make_keyboard(["для WB", "9х16", "3х4", "Не требуется"])
    await message.answer("10. Выберите <b>формат видео</b>:", reply_markup=kb, parse_mode="HTML")
    await state.set_state(Survey.video_aspect)


# --- ШАГ 11 (ОСНОВНОЙ ОБРАЗ МОДЕЛИ: ВЫБОР ИЗ БАЗЫ) ---
@dp.message(Survey.video_aspect)
async def step_video_aspect(message: Message, state: FSMContext):
    await state.update_data(video_aspect=message.text)
    await message.answer(
        "11. <b>Основной образ модели: выбор элементов базы гардероба</b>\n\n"
        "Стилизация образа: https://disk.yandex.ru/d/IZNg3NqqdHLDgA\n"
        "База женская: https://disk.yandex.ru/d/XQJl5aJKjBx6dA/\n\n"
        "👟 <b>Шаг 11.1: Выберите ОБУВЬ из базы</b>:",
        reply_markup=generate_base_picker("shoes"),
        parse_mode="HTML",
    )
    await state.set_state(Survey.look_shoes)


@dp.callback_query(F.data.startswith("base_sel:shoes:"), Survey.look_shoes)
async def step_shoes_chosen(callback: CallbackQuery, state: FSMContext):
    item_id = callback.data.split(":")[2]
    item = next(x for x in BASE_ITEMS["shoes"] if x["id"] == item_id)
    await state.update_data(look_shoes=item["name"], look_shoes_photo=item["photo"])

    await callback.message.edit_text(f"✅ Выбрана обувь: <b>{item['name']}</b>", parse_mode="HTML")
    await callback.message.answer(
        "👖 <b>Шаг 11.2: Выберите НИЗ (Джинсы / брюки) из базы</b>:",
        reply_markup=generate_base_picker("bottom"),
        parse_mode="HTML",
    )
    await state.set_state(Survey.look_bottom)
    await callback.answer()


@dp.callback_query(F.data.startswith("base_sel:bottom:"), Survey.look_bottom)
async def step_bottom_chosen(callback: CallbackQuery, state: FSMContext):
    item_id = callback.data.split(":")[2]
    item = next(x for x in BASE_ITEMS["bottom"] if x["id"] == item_id)
    await state.update_data(look_bottom=item["name"], look_bottom_photo=item["photo"])

    await callback.message.edit_text(f"✅ Выбран низ: <b>{item['name']}</b>", parse_mode="HTML")
    await callback.message.answer(
        "👕 <b>Шаг 11.3: Выберите ВЕРХ (или свой артикул из ТЗ)</b>:",
        reply_markup=generate_base_picker("top"),
        parse_mode="HTML",
    )
    await state.set_state(Survey.look_top)
    await callback.answer()


@dp.callback_query(F.data.startswith("base_sel:top:"), Survey.look_top)
async def step_top_chosen(callback: CallbackQuery, state: FSMContext):
    item_id = callback.data.split(":")[2]
    item = next(x for x in BASE_ITEMS["top"] if x["id"] == item_id)
    await state.update_data(look_top=item["name"], look_top_photo=item["photo"])

    await callback.message.edit_text(f"✅ Выбран верх: <b>{item['name']}</b>", parse_mode="HTML")
    await callback.message.answer(
        "📝 Дополнительные комментарии к образу (или напишите «нет», если всё выбрано):",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML",
    )
    await state.set_state(Survey.look_comment)
    await callback.answer()


@dp.message(Survey.look_comment)
async def step_look_comment(message: Message, state: FSMContext):
    await state.update_data(look_comment=message.text)
    kb = make_keyboard([
        "Да (однотонный фон - 2200р)",
        "Да (интерьер - 3150р)",
        "Нет",
    ])
    await message.answer("12. Требуется ли <b>смена образа</b>
