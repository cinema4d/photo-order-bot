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
        "Укажите **дату съемки** (например: 15.11.2026):",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown",
    )
    await state.set_state(Survey.shoot_date)


@dp.message(Survey.shoot_date)
async def step_shoot_date(message: Message, state: FSMContext):
    await state.update_data(shoot_date=message.text)
    await message.answer("1. Введите **код вашего заказа** (например: АН091076):", parse_mode="Markdown")
    await state.set_state(Survey.order_code)


@dp.message(Survey.order_code)
async def step_order_code(message: Message, state: FSMContext):
    await state.update_data(order_code=message.text)
    kb = make_keyboard(["WB", "OZON", "Lamoda", "WB + OZON", "Все маркетплейсы", "Другое"])
    await message.answer(
        "2. **Для какого МП** съемка?\n"
        "*(Один МП входит в тариф, за последующий +350р/арт за кадрирование)*\n"
        "Выберите вариант или напишите свои площадки вручную:",
        reply_markup=kb,
        parse_mode="Markdown",
    )
    await state.set_state(Survey.marketplaces)


@dp.message(Survey.marketplaces)
async def step_marketplaces(message: Message, state: FSMContext):
    await state.update_data(marketplaces=message.text)
    await message.answer(
        "3. **Наименование товара и детали подготовки**:\n"
        "- Напишите название, цвет и особенности посадки.\n"
        "- ❗️ Укажите, есть ли нюансы подготовки (отпаривание, глажка).\n"
        "- Если необходимо показать крепления/ремни — отправьте описание или ссылку на диск с деталями:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown",
    )
    await state.set_state(Survey.product_desc)


@dp.message(Survey.product_desc)
async def step_product_desc(message: Message, state: FSMContext):
    await state.update_data(product_desc=message.text)
    kb = make_keyboard(["1 арт", "2 арт", "3 арт", "4 арт", "5+ арт"])
    await message.answer("4. Укажите **количество артикулов**:", reply_markup=kb, parse_mode="Markdown")
    await state.set_state(Survey.sku_count)


@dp.message(Survey.sku_count)
async def step_sku_count(message: Message, state: FSMContext):
    await state.update_data(sku_count=message.text)
    kb = make_keyboard(["1/1", "3/4", "9/16", "3/4 и 9/16"])
    await message.answer("5. Выберите **формат кадрирования фото**:", reply_markup=kb, parse_mode="Markdown")
    await state.set_state(Survey.crop_format)


@dp.message(Survey.crop_format)
async def step_crop_format(message: Message, state: FSMContext):
    await state.update_data(crop_format=message.text)
    await message.answer(
        "6. Укажите **имя модели** (например: Юля Л):",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown",
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
        "7. Выберите **локацию и цвет фона**:\n"
        "*(Белое на белом не рекомендуем. Цветные фоны: +1700р за фон. Съемки в интерьере проводятся на фоне из анонса)*",
        reply_markup=kb,
        parse_mode="Markdown",
    )
    await state.set_state(Survey.location)


@dp.message(Survey.location)
async def step_location(message: Message, state: FSMContext):
    await state.update_data(location=message.text)
    kb = make_keyboard(["Фаре 1 арт", "Фаре 2 арт", "Фаре 3 арт", "Индивидуальный"])
    await message.answer("8. Выберите **тариф** съемки:", reply_markup=kb, parse_mode="Markdown")
    await state.set_state(Survey.tariff)


@dp.message(Survey.tariff)
async def step_tariff(message: Message, state: FSMContext):
    await state.update_data(tariff=message.text)
    await message.answer(
        "9. Опишите **видео** (на какой артикул/вещь требуется проходка, динамика):\n"
        "*(Например: видеопроходка на черную футболку, 1 арт)*",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown",
    )
    await state.set_state(Survey.video_details)


@dp.message(Survey.video_details)
async def step_video_details(message: Message, state: FSMContext):
    await state.update_data(video_details=message.text)
    kb = make_keyboard(["9х16", "3х4", "Не требуется"])
    await message.answer("10. Выберите **формат видео**:", reply_markup=kb, parse_mode="Markdown")
    await state.set_state(Survey.video_aspect)


@dp.message(Survey.video_aspect)
async def step_video_aspect(message: Message, state: FSMContext):
    await state.update_data(video_aspect=message.text)
    await message.answer(
        "11. **Основной образ модели**\n\n"
        "Примеры стилей:\n"
        "• Стилизация образа: https://disk.yandex.ru/d/IZNg3NqqdHLDgA\n"
        "• База гардероба: https://disk.yandex.ru/d/rHWIfHqchR_fpA\n\n"
        "📌 *Если вы кладете свои вещи к образу — обязательно укажите это здесь.*\n"
        "🚫 *Точь-в-точь позы и образы в рамках сборных съемок не повторяются.*\n\n"
        "Опишите желаемый образ (или пришлите ссылку на референсы):",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown",
    )
    await state.set_state(Survey.look_details)


@dp.message(Survey.look_details)
async def step_look_details(message: Message, state: FSMContext):
    await state.update_data(look_details=message.text)
    kb = make_keyboard([
        "Да (однотонный фон - 2200р)",
        "Да (интерьер - 3150р)",
        "Нет",
    ])
    await message.answer(
        "12. Требуется ли **смена образа**?",
        reply_markup=kb,
        parse_mode="Markdown",
    )
    await state.set_state(Survey.look_change)


@dp.message(Survey.look_change)
async def step_look_change(message: Message, state: FSMContext):
    await state.update_data(look_change=message.text)
    kb = make_keyboard(["Радостное", "Спокойное", "Сексуальное", "Сдержанное / Каталожное"])
    await message.answer("13. Выберите **настроение модели**:", reply_markup=kb, parse_mode="Markdown")
    await state.set_state(Survey.model_mood)


@dp.message(Survey.model_mood)
async def step_model_mood(message: Message, state: FSMContext):
    await state.update_data(model_mood=message.text)
    await message.answer(
        "14. **Детали товара**, которые необходимо показать крупно/отдельно (строчки, пуговицы, карманы, подкладка и т.д.):",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown",
    )
    await state.set_state(Survey.product_features)


@dp.message(Survey.product_features)
async def step_product_features(message: Message, state: FSMContext):
    await state.update_data(product_features=message.text)
    await message.answer(
        "15. **Примеры фото/ракурсов** (не более 10 примеров).\n"
        "Отправьте ссылку на диск/папку или короткое описание желаемых ракурсов:",
        parse_mode="Markdown",
    )
    await state.set_state(Survey.photo_examples)


@dp.message(Survey.photo_examples)
async def step_photo_examples(message: Message, state: FSMContext):
    await state.update_data(photo_examples=message.text)
    kb = make_keyboard([
        "Да, можно всё (бирки, нитки, бахрому)",
        "Только отрезать нитки",
        "Категорически ничего не срезать",
    ])
    await message.answer(
        "16. **Коррекция товара перед съемкой**:\n"
        "Можно ли срезать бирки, ровнять бахрому, отрезать нитки?",
        reply_markup=kb,
        parse_mode="Markdown",
    )
    await state.set_state(Survey.allow_tags_trimming)


@dp.message(Survey.allow_tags_trimming)
async def step_allow_tags(message: Message, state: FSMContext):
    await state.update_data(allow_tags_trimming=message.text)
    await message.answer(
        "17. Укажите **ваше имя, ник в Telegram (@username) и контактный телефон**:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown",
    )
    await state.set_state(Survey.client_contacts)


@dp.message(Survey.client_contacts)
async def step_client_contacts(message: Message, state: FSMContext):
    await state.update_data(client_contacts=message.text)
    await message.answer("18. Укажите **дату и способ доставки товара** в студию:", parse_mode="Markdown")
    await state.set_state(Survey.delivery_date)


@dp.message(Survey.delivery_date)
async def step_finish(message: Message, state: FSMContext):
    await state.update_data(delivery_date=message.text)
    data = await state.get_data()

    summary_text = (
        "📋 **ИТОГОВОЕ ТЕХНИЧЕСКОЕ ЗАДАНИЕ НА СЪЕМКУ**\n\n"
        f"**Дата съемки:** {data.get('shoot_date')}\n"
        f"1. **Код заказа:** {data.get('order_code')}\n"
        f"2. **Маркетплейсы:** {data.get('marketplaces')}\n"
        f"3. **Наименование и подготовка:** {data.get('product_desc')}\n"
        f"4. **Количество артикулов:** {data.get('sku_count')}\n"
        f"5. **Формат кадрирования:** {data.get('crop_format')}\n"
        f"6. **Имя модели:** {data.get('model_name')}\n"
        f"7. **Локация и фон:** {data.get('location')}\n"
        f"8. **Тариф:** {data.get('tariff')}\n"
        f"9. **Формат видеопроходки:** {data.get('video_details')}\n"
        f"10. **Формат видео:** {data.get('video_aspect')}\n"
        f"11. **Основной образ модели:** {data.get('look_details')}\n"
        f"12. **Смена образа:** {data.get('look_change')}\n"
        f"13. **Настроение модели:** {data.get('model_mood')}\n"
        f"14. **Детали товара:** {data.get('product_features')}\n"
        f"15. **Примеры фото (референсы):** {data.get('photo_examples')}\n"
        f"16. **Срез бирок / ниток:** {data.get('allow_tags_trimming')}\n"
        f"17. **Контакты заказчика:** {data.get('client_contacts')}\n"
        f"18. **Дата доставки товара:** {data.get('delivery_date')}\n"
    )

    await message.answer(summary_text, parse_mode="Markdown")
    await message.answer("✅ Анкета сформирована! Скопируйте текст выше или сохраните его для менеджера.")
    await state.clear()


# Фейковый веб-сервер для прохождения проверки портов Render
async def handle_ping(request):
    return web.Response(text="Bot is running!")


async def run_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/ping", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


async def main():
    await run_web_server()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
