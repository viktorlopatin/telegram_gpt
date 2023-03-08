import asyncio
import logging

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from functions import get_gpt3_response
from Languages import f
from models import User, Statistic
from settings import TOKEN


router = Router()
bot = Bot(TOKEN, parse_mode="HTML")


@router.message(Command(commands=["start"]))
async def command_start_handler(message: Message) -> None:
    lang = message.from_user.language_code
    user = User.get_or_create(message)

    text = f(lang, "hello", name=message.from_user.full_name)

    msg = await message.answer(text)


@router.message(Command(commands=["stat"]))
async def command_stat_handler(message: Message) -> None:
    lang = message.from_user.language_code
    user = User.get_or_create(message)

    text = f"<code>{Statistic.get_stat_by_week()}</code>"

    msg = await message.answer(text)


@router.message(F.text)
async def echo_handler(message: types.Message) -> None:
    lang = message.from_user.language_code
    msg = await message.answer(f(lang, "wait"))
    try:
        user = User.get_or_create(message)
        Statistic.add_request()
        gpt_text = await get_gpt3_response(message.text, user.get_messages())
        await msg.edit_text(gpt_text)
        user.add_message(message.text, role="user")
        user.add_message(gpt_text, role="assistant")
        Statistic.add_request_true()
    except Exception as e:
        print(e)
        await msg.edit_text(f(lang, "answer_error"))


@router.chosen_inline_result()
async def chosen_inline_handler(query: types.ChosenInlineResult) -> None:

    text = query.query
    message_id = query.inline_message_id
    lang = query.from_user.language_code
    user = User.get_by_chat_id(chat_id=query.from_user.id)

    try:
        is_user_active = await bot.send_chat_action(query.from_user.id, "typing")
    except Exception as e:
        is_user_active = False
    if user is None or is_user_active is False:
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text=f(lang, 'create_account_button'),
            url="https://t.me/GptMagicianBot")
        )

        await bot.edit_message_text(
            f(lang, 'create_account_text'),
            inline_message_id=message_id,
            reply_markup=builder.as_markup()
        )
        return

    try:
        await bot.edit_message_text(f"{text}\n\n{f(lang, 'wait')}", inline_message_id=message_id)
        Statistic.add_request()
        text_gpt = await get_gpt3_response(text)
        await bot.edit_message_text(f"{text}\n\n{text_gpt}", inline_message_id=message_id)
        user.add_message(text, role="user")
        user.add_message(text_gpt, role="assistant")
        Statistic.add_request_true()
    except Exception as e:
        await bot.edit_message_text(f(lang, "answer_error"), inline_message_id=message_id)


@router.inline_query(F.query.func(len) > 1)
async def inline_echo_handler(query: types.InlineQuery) -> None:
    text = query.query


    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="wait...",
        callback_data="__")
    )
    article = types.InlineQueryResultArticle(
        id="12",
        title=text,
        input_message_content=types.InputTextMessageContent(message_text=text),
        reply_markup=builder.as_markup()
    )
    await query.answer([article], cache_time=30, is_personal=True)


async def main() -> None:
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
