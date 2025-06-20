from aiogram import Bot, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.utils.ai import MusicQuizAI
from src.utils.settings import settings

router = Router()
ai = MusicQuizAI(api_key=settings.GEMINI_API_KEY)


@router.message(CommandStart())
async def start_command_handler(message: Message, state: FSMContext, bot: Bot):
    await bot.send_chat_action(message.chat.id, "typing", request_timeout=10)
    
    quiz_response = await ai.generate_question()
    correct_answer = next(option.text for option in quiz_response.options if option.is_correct)
    await state.update_data(correct_answer=correct_answer)
    
    response_text = f"🎵 {quiz_response.question}\n\n"
    
    if quiz_response.hint:
        response_text += f"\n💡 Hint: <tg-spoiler>{quiz_response.hint}</tg-spoiler>"
    
    builder = ReplyKeyboardBuilder()
    for option in quiz_response.options:
        builder.add(KeyboardButton(text=option.text))
    builder.adjust(1)
    keyboard = builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Select answer"
    )

    await message.answer(
        text=response_text,
        reply_markup=keyboard
    )


@router.message(Command("support"))
async def support_command_handler(message: Message):
    await message.answer("Developer: @Artemka1806")
