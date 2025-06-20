from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.chat_action import ChatActionSender

from src.utils.ai import MusicQuizAI
from src.utils.settings import settings
from src.utils.r import get_redis
from src.bot.routers.system import QuizStates

router = Router()
ai = MusicQuizAI(api_key=settings.GEMINI_API_KEY)


@router.message(QuizStates.answering)
async def handle_answer(message: Message, state: FSMContext, bot: Bot):
    async with ChatActionSender.typing(message.chat.id, bot):
        data = await state.get_data()
        correct_answer = data.get("correct_answer")

        if not correct_answer:
            await state.clear()
            await message.answer("Please start the quiz with /start command")
            return

        is_correct = message.text == correct_answer
        response = "✅ Correct! Let's try another one!" if is_correct else f"❌ Wrong! The correct answer was: {correct_answer}"

        redis = await get_redis()
        genre = await redis.get(f"user:{message.from_user.id}:genre")

        quiz_response = await ai.generate_question(genre=genre)
        new_correct_answer = next(
            option.text for option in quiz_response.options if option.is_correct)
        await state.update_data(correct_answer=new_correct_answer)

        question_text = f"{response}\n\n🎵 {quiz_response.question}\n\n"
        if quiz_response.hint:
            question_text += f"\n💡 Hint: <tg-spoiler>{quiz_response.hint}</tg-spoiler>"

        if not genre:
            question_text += "\n\n📌 Tip: Use /genre to set your preferred music genre!"

        builder = ReplyKeyboardBuilder()
        for option in quiz_response.options:
            builder.add(KeyboardButton(text=option.text))
        builder.adjust(1)
        keyboard = builder.as_markup(
            resize_keyboard=True,
            input_field_placeholder="Select answer"
        )

        await state.set_state(QuizStates.answering)
        await message.answer(
            text=question_text,
            reply_markup=keyboard
        )
