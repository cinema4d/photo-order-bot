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

    # Шаг 11: Подпункты образа
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


# --- Старт и шаги 1–10 ---
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    now = datetime.now()
    kb = generate_calendar_keyboard(now.year, now.month)
    await message.answer(
        "👋
