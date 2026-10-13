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
    look_details = State()
    look_change = State()
    model_mood = State()
    product_features = State()
    photo_examples = State()
    allow_tags_trimming = State()
    client_contacts = State()
    delivery_date = State()


# --- Вспомогательные функции для клавиатур ---
def make_keyboard(buttons: list[str]) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=btn)] for btn in buttons]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)


MONTHS_RU = [
    "",
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь",
]


def generate_calendar_keyboard(year: int, month: int) -> InlineKeyboardMarkup:
    """Генератор инлайн-календаря для Telegram"""
    kb = []

    # Заголовок (Месяц Год)
    month_name = MONTHS_RU[month]
    kb.append([InlineKeyboardButton(text=f"{month_name} {year}", callback_data="cal_ignore")])

    # Дни недели
    days_header = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    kb.append([InlineKeyboardButton(text=day, callback_data="cal_ignore") for day in days_header])

    # Сетка дней
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

    # Стрелки переключения месяцев
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


# --- Старт и Шаг 1 (Календарь даты съемки) ---
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
    await state.set_
