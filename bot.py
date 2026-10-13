import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

BOT_TOKEN = "8570870167:AAERz1_Rf9wKCi7Dt5-9ytbGf7v1I6rDjMI"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Класс состояний FSM
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


def make_keyboard(buttons: list[str]) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=btn)] for btn in buttons]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Здравствуйте! Давайте заполним техническое задание на съемку.\n\n"
        "Укажите <b>дату съемки</b> (например: 15.11.2026):",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML",
    )
    await state.set_state(Survey.shoot_date)


@dp.message(Survey.shoot_date)
async def step_shoot_date(message: Message, state: FSMContext):
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
async def step_product_desc(message
